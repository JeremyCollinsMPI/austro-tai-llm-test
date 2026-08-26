"""Validate Proto-Austronesian reconstructions against sampled Lexibank AN forms."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path

from .an_sampling import sample_austronesian_forms
from .config import (
    AN_SAMPLE_TARGET,
    CACHE_DIR,
    OUTPUT_DIR,
    PAN_RECONSTRUCTION_PROMPT_VERSION,
)
from .json_utils import extract_json_array
from .nlp_client import chat
from .parse_smith import AlignedPair, read_aligned_pairs

SYSTEM_PROMPT = """You are a comparative linguist assessing how well a proposed Proto-Austronesian (PAN) reconstruction is supported by attested modern Austronesian word forms sampled from Lexibank.

Rules:
- Compare the PAN form to attested daughter-language forms for the same meaning.
- The sample is phylogenetically stratified (Formosan, Western Malayo-Polynesian, SHWNG, Oceanic, etc.). Weight evidence across clades; do not let Oceanic alone decide the score.
- Prefer support that includes Formosan and/or widespread Western MP reflexes for a high score.
- Ignore tone marks/superscripts when comparing shapes, but mention them if relevant.
- Reward systematic reflexes across multiple clades; penalize if attested forms cluster around a different shape.
- Do NOT require perfect regular sound correspondences, but note major mismatches.
- If alternate PAN reconstructions are listed, treat any well-supported alternate as supporting a higher score.

Return ONLY valid JSON (no markdown fences) as an array of objects with keys:
- pair_id (string)
- attestation_score (integer 1-5; 5 = strongly supported across sampled clades)
- supporting_reflexes (string; brief note on languages/forms/clades that fit)
- problematic_reflexes (string; forms that do not fit, or "none noted")
- reasoning (string; 2-4 sentences)
"""


@dataclass
class PanReconstructionScore:
    pair_id: str
    gloss: str
    pan: str
    attestation_score: int
    supporting_reflexes: str
    problematic_reflexes: str
    reasoning: str
    n_attested_forms_sent: int
    n_austronesian_languages_available: int
    sample_clade_counts: str

    def to_row(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "gloss": self.gloss,
            "pan": self.pan,
            "attestation_score": self.attestation_score,
            "supporting_reflexes": self.supporting_reflexes,
            "problematic_reflexes": self.problematic_reflexes,
            "reasoning": self.reasoning,
            "n_attested_forms_sent": self.n_attested_forms_sent,
            "n_austronesian_languages_available": self.n_austronesian_languages_available,
            "sample_clade_counts": self.sample_clade_counts,
        }


def _cache_key(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _connect_cache(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pan_reconstruction_scores (
            cache_key TEXT PRIMARY KEY,
            prompt_version TEXT,
            response_json TEXT,
            created_at REAL
        )
        """
    )
    return conn


def _clade_count_summary(forms: list[dict[str, str]]) -> str:
    counts: dict[str, int] = {}
    for item in forms:
        clade = item.get("clade") or "unknown"
        counts[clade] = counts.get(clade, 0) + 1
    return ",".join(f"{k}:{v}" for k, v in sorted(counts.items()))


def _build_validation_prompt(items: list[dict]) -> str:
    return (
        "Score how well each PAN reconstruction is supported by the sampled Austronesian forms listed.\n"
        "Each attested form includes its coarse phylogenetic clade.\n\n"
        + json.dumps(items, ensure_ascii=False, indent=2)
    )


def validate_pan_batch(
    pairs: list[AlignedPair],
    an_attestation: dict[str, dict[str, object]],
    concept_by_pair: dict[str, str],
    *,
    batch_size: int = 2,
    cache_path: Path | None = None,
    sleep_seconds: float = 0.5,
) -> list[PanReconstructionScore]:
    cache_path = cache_path or (CACHE_DIR / "pan_reconstruction_scores.sqlite3")
    results: list[PanReconstructionScore] = []

    for start in range(0, len(pairs), batch_size):
        chunk = pairs[start : start + batch_size]
        items = []
        sampled_by_pair: dict[str, list[dict[str, str]]] = {}
        available_by_pair: dict[str, int] = {}
        for pair in chunk:
            concept_id = concept_by_pair.get(pair.pair_id, "")
            concept_data = an_attestation.get(concept_id, {})
            all_forms = list(concept_data.get("forms") or [])
            sampled = sample_austronesian_forms(all_forms, target=AN_SAMPLE_TARGET)
            sampled_by_pair[pair.pair_id] = sampled
            available_by_pair[pair.pair_id] = int(concept_data.get("count") or 0)
            items.append(
                {
                    "pair_id": pair.pair_id,
                    "gloss": pair.gloss,
                    "proto_austronesian": pair.pan,
                    "lexibank_concept_id": concept_id,
                    "n_austronesian_languages_in_lexibank": available_by_pair[pair.pair_id],
                    "n_forms_in_sample": len(sampled),
                    "sample_clade_counts": _clade_count_summary(sampled),
                    "attested_forms": [
                        {
                            "language": f.get("language"),
                            "clade": f.get("clade"),
                            "form": f.get("form"),
                        }
                        for f in sampled
                    ],
                }
            )

        user_prompt = _build_validation_prompt(items)
        cache_payload = {
            "prompt_version": PAN_RECONSTRUCTION_PROMPT_VERSION,
            "system": SYSTEM_PROMPT,
            "user": user_prompt,
        }
        key = _cache_key(cache_payload)

        conn = _connect_cache(cache_path)
        row = conn.execute(
            "SELECT response_json FROM pan_reconstruction_scores WHERE cache_key = ?", (key,)
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
                        f"JSON parse failed for PAN validation attempt {attempt + 1}/3: {exc}; retrying ..."
                    )
                    if sleep_seconds:
                        time.sleep(sleep_seconds * (attempt + 1))
            if parsed is None:
                raise RuntimeError("Failed to parse PAN validation LLM JSON after 3 attempts") from last_error
            conn.execute(
                "INSERT OR REPLACE INTO pan_reconstruction_scores(cache_key, prompt_version, response_json, created_at) VALUES (?, ?, ?, ?)",
                (key, PAN_RECONSTRUCTION_PROMPT_VERSION, json.dumps(parsed, ensure_ascii=False), time.time()),
            )
            conn.commit()
            if sleep_seconds:
                time.sleep(sleep_seconds)
        conn.close()

        by_id = {item["pair_id"]: item for item in parsed}
        for pair in chunk:
            item = by_id.get(pair.pair_id)
            if not item:
                raise ValueError(f"Missing PAN attestation_score for pair_id={pair.pair_id}")
            sampled = sampled_by_pair[pair.pair_id]
            results.append(
                PanReconstructionScore(
                    pair_id=pair.pair_id,
                    gloss=pair.gloss,
                    pan=pair.pan,
                    attestation_score=int(item["attestation_score"]),
                    supporting_reflexes=str(item.get("supporting_reflexes") or ""),
                    problematic_reflexes=str(item.get("problematic_reflexes") or ""),
                    reasoning=str(item.get("reasoning") or ""),
                    n_attested_forms_sent=len(sampled),
                    n_austronesian_languages_available=available_by_pair[pair.pair_id],
                    sample_clade_counts=_clade_count_summary(sampled),
                )
            )
    return results


def run_pan_reconstruction_validation(
    pairs: list[AlignedPair] | None = None,
    output_path: Path | None = None,
) -> list[PanReconstructionScore]:
    from .lexibank_check import _load_austronesian_attestation, match_concept, _load_concept_records

    pairs = pairs or read_aligned_pairs()
    an_attestation = _load_austronesian_attestation()
    concept_records = _load_concept_records()
    concept_by_pair: dict[str, str] = {}
    eligible: list[AlignedPair] = []
    for pair in pairs:
        concept = match_concept(pair.gloss, concept_records)
        if not concept:
            continue
        count = int((an_attestation.get(concept.concept_id) or {}).get("count") or 0)
        if count <= 0:
            continue
        concept_by_pair[pair.pair_id] = concept.concept_id
        eligible.append(pair)

    print(f"Validating PAN reconstructions for {len(eligible)} pairs with sampled Austronesian forms ...")
    scores = validate_pan_batch(eligible, an_attestation, concept_by_pair, batch_size=2)
    output_path = output_path or (OUTPUT_DIR / "pan_reconstruction_validation.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(PanReconstructionScore.__dataclass_fields__)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for score in scores:
            writer.writerow(score.to_row())
    print(f"Wrote PAN reconstruction validation to {output_path}")
    return scores
