from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .config import (
    CACHE_DIR,
    DEFAULT_BATCH_SIZE,
    GENEROSITY_THRESHOLD,
    OUTPUT_DIR,
    PROMPT_VERSION,
)
from .json_utils import extract_json_array
from .nlp_client import chat
from .lexibank_check import read_eligible_pairs
from .parse_smith import AlignedPair, read_aligned_pairs

SYSTEM_PROMPT = """You are a comparative linguist scoring how similar proposed proto-language **forms** look, for exploratory Austro-Tai research.

Rules:
- Compare **phonetic and segmental shape only**. Do NOT use, infer, or mention meaning, semantics, glosses, or cognate labels.
- Each item gives a Proto-Kra-Dai (PKD) form and a candidate Proto-Austronesian (PAN) form. Score how similar the PAN form would be to the PKD form **if** it were the Austronesian reconstruction paired with that PKD slot—without knowing what concept either form represents.
- Do NOT require established regular sound correspondences; be generous on shape but not absurd.
- Ignore tone marks/superscripts when comparing shapes, but mention them if relevant.
- If the PAN side lists multiple alternate reconstructions, treat any plausible segmental match as supporting a higher score.

Return ONLY valid JSON (no markdown fences) as an array of objects with keys:
- comparison_id (string; echo the id from the input)
- generosity (integer 1-5; 5 = very similar shapes under a generous comparison)
- plausible_sound_correspondences (string; brief note or "none noted")
- reasoning (string; 1-3 sentences; do not refer to meaning)
"""


@dataclass
class Judgment:
    pair_id: str
    gloss: str
    pan: str
    pkd: str
    generosity: int
    plausible_sound_correspondences: str
    reasoning: str
    is_hit: bool
    permutation_id: int
    batch_id: str

    def to_row(self) -> dict[str, object]:
        return {
            "pair_id": self.pair_id,
            "gloss": self.gloss,
            "pan": self.pan,
            "pkd": self.pkd,
            "generosity": self.generosity,
            "plausible_sound_correspondences": self.plausible_sound_correspondences,
            "reasoning": self.reasoning,
            "is_hit": int(self.is_hit),
            "permutation_id": self.permutation_id,
            "batch_id": self.batch_id,
        }


@dataclass
class PairRequest:
    pair_id: str
    gloss: str
    pkd: str
    pan: str
    pt: str = ""
    chinese_flag: str = ""
    notes: str = ""


def _cache_key(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _connect_cache(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS batch_judgments (
            cache_key TEXT PRIMARY KEY,
            prompt_version TEXT,
            response_json TEXT,
            created_at REAL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pair_judgments (
            pkd TEXT NOT NULL,
            pan TEXT NOT NULL,
            prompt_version TEXT NOT NULL,
            generosity INTEGER NOT NULL,
            plausible_sound_correspondences TEXT,
            reasoning TEXT,
            created_at REAL,
            PRIMARY KEY (pkd, pan, prompt_version)
        )
        """
    )
    cols = {row[1] for row in conn.execute("PRAGMA table_info(pair_judgments)").fetchall()}
    if "gloss" in cols:
        conn.execute("DROP TABLE pair_judgments")
        conn.execute(
            """
            CREATE TABLE pair_judgments (
                pkd TEXT NOT NULL,
                pan TEXT NOT NULL,
                prompt_version TEXT NOT NULL,
                generosity INTEGER NOT NULL,
                plausible_sound_correspondences TEXT,
                reasoning TEXT,
                created_at REAL,
                PRIMARY KEY (pkd, pan, prompt_version)
            )
            """
        )
    return conn


def _build_user_prompt(items: Iterable[PairRequest | AlignedPair]) -> tuple[str, dict[str, PairRequest | AlignedPair]]:
    payload = []
    id_map: dict[str, PairRequest | AlignedPair] = {}
    for index, item in enumerate(items, start=1):
        comparison_id = f"{index:03d}"
        id_map[comparison_id] = item
        if isinstance(item, PairRequest):
            pkd = item.pkd
            pan = item.pan
            pt = item.pt
        else:
            pkd = item.pkd
            pan = item.pan
            pt = item.pt
        payload.append(
            {
                "comparison_id": comparison_id,
                "proto_austronesian": pan,
                "proto_kra_dai": pkd,
                "proto_tai_branch": pt or None,
            }
        )
    prompt = (
        "For each item, score how similar the proto-Austronesian form would be to the proto-Kra-Dai form "
        "if it were the Austronesian reconstruction for the same slot. Compare shapes only; do not use meaning.\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )
    return prompt, id_map


def _store_pair_judgment(
    conn: sqlite3.Connection,
    *,
    pkd: str,
    pan: str,
    generosity: int,
    sound_note: str,
    reasoning: str,
) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO pair_judgments
        (pkd, pan, prompt_version, generosity, plausible_sound_correspondences, reasoning, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (pkd, pan, PROMPT_VERSION, generosity, sound_note, reasoning, time.time()),
    )


def _lookup_pair(conn: sqlite3.Connection, pkd: str, pan: str) -> dict | None:
    row = conn.execute(
        """
        SELECT generosity, plausible_sound_correspondences, reasoning
        FROM pair_judgments
        WHERE pkd = ? AND pan = ? AND prompt_version = ?
        """,
        (pkd, pan, PROMPT_VERSION),
    ).fetchone()
    if not row:
        return None
    return {
        "generosity": int(row[0]),
        "plausible_sound_correspondences": row[1] or "",
        "reasoning": row[2] or "",
    }


def judge_requests(
    requests: list[PairRequest],
    *,
    permutation_id: int = 0,
    batch_size: int = DEFAULT_BATCH_SIZE,
    cache_path: Path | None = None,
    sleep_seconds: float = 0.5,
) -> list[Judgment]:
    cache_path = cache_path or (CACHE_DIR / "judgments.sqlite3")
    conn = _connect_cache(cache_path)

    missing: list[PairRequest] = []
    cached: dict[str, dict] = {}
    for request in requests:
        found = _lookup_pair(conn, request.pkd, request.pan)
        if found:
            cached[request.pair_id] = found
        else:
            missing.append(request)

    for start in range(0, len(missing), batch_size):
        chunk = missing[start : start + batch_size]
        batch_id = f"p{permutation_id}_b{start // batch_size:03d}"
        user_prompt, id_map = _build_user_prompt(chunk)
        cache_payload = {
            "prompt_version": PROMPT_VERSION,
            "system": SYSTEM_PROMPT,
            "user": user_prompt,
        }
        key = _cache_key(cache_payload)
        row = conn.execute(
            "SELECT response_json FROM batch_judgments WHERE cache_key = ?", (key,)
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
                        f"JSON parse failed for {batch_id} attempt {attempt + 1}/3: {exc}; retrying ..."
                    )
                    if sleep_seconds:
                        time.sleep(sleep_seconds * (attempt + 1))
            if parsed is None:
                raise RuntimeError(
                    f"Failed to parse LLM JSON for {batch_id} after 3 attempts"
                ) from last_error
            conn.execute(
                "INSERT OR REPLACE INTO batch_judgments(cache_key, prompt_version, response_json, created_at) VALUES (?, ?, ?, ?)",
                (key, PROMPT_VERSION, json.dumps(parsed, ensure_ascii=False), time.time()),
            )
            if sleep_seconds:
                time.sleep(sleep_seconds)
        by_id = {item.get("comparison_id") or item.get("pair_id"): item for item in parsed}
        for comparison_id, request in id_map.items():
            item = by_id.get(comparison_id)
            if not item:
                raise ValueError(
                    f"Missing judgment for comparison_id={comparison_id} (pair_id={request.pair_id}) "
                    f"in batch {batch_id}"
                )
            pair_request = request if isinstance(request, PairRequest) else PairRequest(
                pair_id=request.pair_id,
                gloss=request.gloss,
                pkd=request.pkd,
                pan=request.pan,
                pt=request.pt,
                chinese_flag=request.chinese_flag,
                notes=request.notes,
            )
            _store_pair_judgment(
                conn,
                pkd=pair_request.pkd,
                pan=pair_request.pan,
                generosity=int(item["generosity"]),
                sound_note=str(item.get("plausible_sound_correspondences") or ""),
                reasoning=str(item.get("reasoning") or ""),
            )
            cached[pair_request.pair_id] = {
                "generosity": int(item["generosity"]),
                "plausible_sound_correspondences": str(item.get("plausible_sound_correspondences") or ""),
                "reasoning": str(item.get("reasoning") or ""),
            }
    conn.commit()
    conn.close()

    results: list[Judgment] = []
    for request in requests:
        item = cached[request.pair_id]
        generosity = int(item["generosity"])
        results.append(
            Judgment(
                pair_id=request.pair_id,
                gloss=request.gloss,
                pan=request.pan,
                pkd=request.pkd,
                generosity=generosity,
                plausible_sound_correspondences=str(item.get("plausible_sound_correspondences") or ""),
                reasoning=str(item.get("reasoning") or ""),
                is_hit=generosity >= GENEROSITY_THRESHOLD,
                permutation_id=permutation_id,
                batch_id=f"p{permutation_id}",
            )
        )
    return results


def judge_pairs(
    pairs: list[AlignedPair],
    *,
    permutation_id: int = 0,
    batch_size: int = DEFAULT_BATCH_SIZE,
    cache_path: Path | None = None,
) -> list[Judgment]:
    requests = [
        PairRequest(
            pair_id=pair.pair_id,
            gloss=pair.gloss,
            pkd=pair.pkd,
            pan=pair.pan,
            pt=pair.pt,
            chinese_flag=pair.chinese_flag,
            notes=pair.notes,
        )
        for pair in pairs
    ]
    return judge_requests(
        requests,
        permutation_id=permutation_id,
        batch_size=batch_size,
        cache_path=cache_path,
    )


def build_judgment_matrix(
    pairs: list[AlignedPair] | None = None,
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> int:
    pairs = pairs or read_aligned_pairs()
    pans = sorted({pair.pan for pair in pairs})
    requests: list[PairRequest] = []
    for pair in pairs:
        for pan in pans:
            requests.append(
                PairRequest(
                    pair_id=f"{pair.pair_id}__x__{hash((pair.gloss, pair.pkd, pan)) & 0xfffffff:x}",
                    gloss=pair.gloss,
                    pkd=pair.pkd,
                    pan=pan,
                    pt=pair.pt,
                    chinese_flag=pair.chinese_flag,
                    notes=pair.notes,
                )
            )
    print(f"Matrix warm-up: {len(requests)} gloss/PKD/PAN combinations")
    judged = judge_requests(requests, permutation_id=-1, batch_size=batch_size)
    return len(judged)


def write_judgments(judgments: list[Judgment], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(Judgment.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for judgment in judgments:
            writer.writerow(judgment.to_row())


def summarize_judgments(judgments: list[Judgment]) -> dict[str, object]:
    hits = [j for j in judgments if j.is_hit]
    return {
        "n_pairs": len(judgments),
        "n_hits": len(hits),
        "hit_rate": len(hits) / len(judgments) if judgments else 0.0,
        "mean_generosity": sum(j.generosity for j in judgments) / len(judgments) if judgments else 0.0,
        "hits": [
            {
                "pair_id": j.pair_id,
                "gloss": j.gloss,
                "generosity": j.generosity,
                "reasoning": j.reasoning,
            }
            for j in hits
        ],
    }


def run_observed_judgment(
    pairs_path: Path | None = None,
    output_path: Path | None = None,
    *,
    use_eligible: bool = True,
) -> dict[str, object]:
    if pairs_path:
        from .parse_smith import read_aligned_pairs

        pairs = read_aligned_pairs(pairs_path)
    elif use_eligible:
        pairs = read_eligible_pairs()
    else:
        from .parse_smith import read_aligned_pairs

        pairs = read_aligned_pairs()
    print(f"Judging {len(pairs)} PKD/PAN form pairs (meaning-blind) ...")
    judgments = judge_pairs(pairs, permutation_id=0)
    output_path = output_path or (OUTPUT_DIR / "judgments_observed.csv")
    write_judgments(judgments, output_path)
    summary = summarize_judgments(judgments)
    summary["output_path"] = str(output_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return summary
