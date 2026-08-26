from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .config import CACHE_DIR, DEFAULT_BATCH_SIZE, OUTPUT_DIR, RECONSTRUCTION_PROMPT_VERSION
from .json_utils import extract_json_array
from .lexibank_check import AttestationAudit, _load_lexibank_attestation
from .nlp_client import chat
from .parse_smith import AlignedPair, read_aligned_pairs

SYSTEM_PROMPT = """You are a comparative linguist assessing how well a proposed Proto-Kra-Dai (PKD) reconstruction is supported by attested modern Tai-Kadai word forms from Lexibank.

Rules:
- Compare the PKD form to attested daughter-language forms for the same meaning.
- Ignore tone marks/superscripts when comparing shapes, but mention them if relevant.
- Reward systematic reflexes across multiple languages; penalize if attested forms cluster around a different shape.
- Do NOT require perfect regular sound correspondences, but note major mismatches.
- If branch-level proto-Tai (PT) is given and contradicts most attested forms, lower the score.

Return ONLY valid JSON (no markdown fences) as an array of objects with keys:
- pair_id (string)
- attestation_score (integer 1-5; 5 = strongly supported across attested forms)
- supporting_reflexes (string; brief note on languages/forms that fit)
- problematic_reflexes (string; forms that do not fit, or "none noted")
- reasoning (string; 2-4 sentences)
"""


@dataclass
class ReconstructionScore:
    pair_id: str
    gloss: str
    pkd: str
    pt: str
    attestation_score: int
    supporting_reflexes: str
    problematic_reflexes: str
    reasoning: str
    n_attested_forms_sent: int

    def to_row(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "gloss": self.gloss,
            "pkd": self.pkd,
            "pt": self.pt,
            "attestation_score": self.attestation_score,
            "supporting_reflexes": self.supporting_reflexes,
            "problematic_reflexes": self.problematic_reflexes,
            "reasoning": self.reasoning,
            "n_attested_forms_sent": self.n_attested_forms_sent,
        }


def _connect_cache(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reconstruction_scores (
            cache_key TEXT PRIMARY KEY,
            prompt_version TEXT,
            response_json TEXT,
            created_at REAL
        )
        """
    )
    return conn


def _cache_key(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _build_validation_prompt(items: list[dict]) -> str:
    return (
        "Score how well each PKD reconstruction is supported by the attested Tai-Kadai forms listed.\n\n"
        + json.dumps(items, ensure_ascii=False, indent=2)
    )


def validate_batch(
    pairs: list[AlignedPair],
    attestation_by_id: dict[str, AttestationAudit],
    attestation_cache: dict[str, dict[str, object]],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    cache_path: Path | None = None,
    sleep_seconds: float = 0.5,
) -> list[ReconstructionScore]:
    cache_path = cache_path or (CACHE_DIR / "reconstruction_scores.sqlite3")
    results: list[ReconstructionScore] = []

    for start in range(0, len(pairs), batch_size):
        chunk = pairs[start : start + batch_size]
        items = []
        for pair in chunk:
            audit = attestation_by_id[pair.pair_id]
            concept_data = attestation_cache.get(audit.lexibank_concept_id, {})
            forms = concept_data.get("forms") or []
            items.append(
                {
                    "pair_id": pair.pair_id,
                    "gloss": pair.gloss,
                    "proto_kra_dai": pair.pkd,
                    "proto_tai_branch": pair.pt or None,
                    "lexibank_concept": audit.lexibank_concepticon_gloss or audit.lexibank_concept_name,
                    "n_attested_languages_in_lexibank": audit.lexibank_tai_kadai_language_count,
                    "attested_forms": forms,
                }
            )

        user_prompt = _build_validation_prompt(items)
        cache_payload = {
            "prompt_version": RECONSTRUCTION_PROMPT_VERSION,
            "system": SYSTEM_PROMPT,
            "user": user_prompt,
        }
        key = _cache_key(cache_payload)

        conn = _connect_cache(cache_path)
        row = conn.execute(
            "SELECT response_json FROM reconstruction_scores WHERE cache_key = ?", (key,)
        ).fetchone()
        if row:
            parsed = json.loads(row[0])
        else:
            parsed = None
            last_error: Exception | None = None
            for attempt in range(3):
                try:
                    reply = chat(user_prompt, system_content=SYSTEM_PROMPT)
                    parsed = extract_json_array(reply)
                    break
                except (json.JSONDecodeError, ValueError, KeyError) as exc:
                    last_error = exc
                    print(
                        f"JSON parse failed for reconstruction batch attempt {attempt + 1}/3: {exc}; retrying ..."
                    )
                    if sleep_seconds:
                        time.sleep(sleep_seconds * (attempt + 1))
            if parsed is None:
                raise RuntimeError(
                    "Failed to parse reconstruction LLM JSON after 3 attempts"
                ) from last_error
            conn.execute(
                "INSERT OR REPLACE INTO reconstruction_scores(cache_key, prompt_version, response_json, created_at) VALUES (?, ?, ?, ?)",
                (key, RECONSTRUCTION_PROMPT_VERSION, json.dumps(parsed, ensure_ascii=False), time.time()),
            )
            conn.commit()
            if sleep_seconds:
                time.sleep(sleep_seconds)
        conn.close()

        by_id = {item["pair_id"]: item for item in parsed}
        for pair, item_payload in zip(chunk, items, strict=True):
            item = by_id.get(pair.pair_id)
            if not item:
                raise ValueError(f"Missing attestation_score for pair_id={pair.pair_id}")
            results.append(
                ReconstructionScore(
                    pair_id=pair.pair_id,
                    gloss=pair.gloss,
                    pkd=pair.pkd,
                    pt=pair.pt,
                    attestation_score=int(item["attestation_score"]),
                    supporting_reflexes=str(item.get("supporting_reflexes") or ""),
                    problematic_reflexes=str(item.get("problematic_reflexes") or ""),
                    reasoning=str(item.get("reasoning") or ""),
                    n_attested_forms_sent=len(item_payload["attested_forms"]),
                )
            )
    return results


def run_reconstruction_validation(
    pairs: list[AlignedPair] | None = None,
    audits: list[AttestationAudit] | None = None,
    output_path: Path | None = None,
) -> list[ReconstructionScore]:
    pairs = pairs or read_aligned_pairs()
    attestation_cache, _ = _load_lexibank_attestation()
    if audits is None:
        from .lexibank_check import audit_attestation

        audits = audit_attestation(pairs)

    audit_by_id = {audit.pair_id: audit for audit in audits}
    eligible = [
        pair
        for pair in pairs
        if audit_by_id[pair.pair_id].lexibank_concept_id
        and audit_by_id[pair.pair_id].lexibank_tai_kadai_language_count > 0
    ]
    print(f"Validating PKD reconstructions for {len(eligible)} pairs with attested Lexibank forms ...")
    scores = validate_batch(eligible, audit_by_id, attestation_cache, batch_size=2)
    output_path = output_path or (OUTPUT_DIR / "reconstruction_validation.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(ReconstructionScore.__dataclass_fields__)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for score in scores:
            writer.writerow(score.to_row())
    print(f"Wrote reconstruction validation to {output_path}")
    return scores
