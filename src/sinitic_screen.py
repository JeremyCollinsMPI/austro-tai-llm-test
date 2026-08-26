"""Screen meaning-blind hits for plausible Chinese loan connections."""

from __future__ import annotations

import csv
import json
import sqlite3
import time
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from .config import CACHE_DIR, OUTPUT_DIR
from .json_utils import extract_json_array
from .nlp_client import chat

SINITIC_PROMPT_VERSION = "v1"
CACHE_PATH = CACHE_DIR / "sinitic_screen.sqlite3"

SYSTEM_PROMPT = """You are a historical linguist assessing whether lexical lookalikes between Austronesian and Kra-Dai (Tai-Kadai) could plausibly reflect borrowing from Chinese (including Old Chinese / early Sinitic) into either Austronesian or Kra-Dai.

For each item, judge how plausible it is that the shared shape (or the alignment of forms) is due to a Chinese loan into Tai-Kadai and/or Austronesian, rather than inheritance within Austro-Tai, non-Sinitic contact, nursery forms, or chance.

Use a 1–5 scale:
1 = very implausible as a Chinese loan explanation for the shared resemblance
2 = unlikely
3 = uncertain / mixed
4 = plausible that Chinese is involved for at least one side
5 = strongly suggestive of a Chinese loan pathway

Return ONLY valid JSON (no markdown fences): an array of objects with keys:
- item_id (string; echo the id)
- chinese_loan_plausibility (integer 1-5)
- likely_direction (string; one of: "into_kra_dai", "into_austronesian", "into_both_or_unclear", "not_applicable")
- reasoning (string; 1-3 sentences; cite known Chinese comparanda only if you are reasonably confident)
"""


@dataclass
class ScreenItem:
    item_id: str
    study: str
    gloss: str
    form_summary: str
    generosity: int


def _connect_cache(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sinitic_judgments (
            cache_key TEXT PRIMARY KEY,
            prompt_version TEXT NOT NULL,
            response_json TEXT NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def _cache_key(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return sha256(blob.encode("utf-8")).hexdigest()


def _load_study1_hits(path: Path, min_generosity: int) -> list[ScreenItem]:
    items: list[ScreenItem] = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            g = int(float(row["generosity"]))
            if g < min_generosity:
                continue
            items.append(
                ScreenItem(
                    item_id=row["pair_id"],
                    study="study1",
                    gloss=row["gloss"],
                    form_summary=f"PAN {row['pan']} ~ PKD {row['pkd']}",
                    generosity=g,
                )
            )
    return items


def _load_study2_hits(path: Path, min_generosity: int) -> list[ScreenItem]:
    items: list[ScreenItem] = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            g = int(float(row["generosity"]))
            if g < min_generosity:
                continue
            concept = row.get("concept_id") or row.get("gloss") or row["comparison_id"]
            notes = (row.get("shared_shape_notes") or "").strip()
            form_summary = f"concept={concept}; shared_shape_notes={notes[:500]}"
            items.append(
                ScreenItem(
                    item_id=row["comparison_id"],
                    study="study2",
                    gloss=str(concept),
                    form_summary=form_summary,
                    generosity=g,
                )
            )
    return items


def _judge_batch(items: list[ScreenItem], conn: sqlite3.Connection) -> list[dict]:
    payload_items = [
        {
            "item_id": it.item_id,
            "gloss": it.gloss,
            "forms": it.form_summary,
            "study": it.study,
        }
        for it in items
    ]
    cache_payload = {
        "prompt_version": SINITIC_PROMPT_VERSION,
        "system": SYSTEM_PROMPT,
        "items": payload_items,
    }
    key = _cache_key(cache_payload)
    row = conn.execute(
        "SELECT response_json FROM sinitic_judgments WHERE cache_key = ?", (key,)
    ).fetchone()
    if row:
        return json.loads(row[0])

    user = (
        "For each item, score how plausible a Chinese-loan explanation is for the "
        "Austronesian–Kra-Dai resemblance.\n\n"
        + json.dumps(payload_items, ensure_ascii=False)
    )
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            reply = chat(user, system_content=SYSTEM_PROMPT, max_completion_tokens=4000)
            parsed = extract_json_array(reply)
            by_id = {str(x.get("item_id")): x for x in parsed if isinstance(x, dict)}
            ordered = []
            for it in items:
                hit = by_id.get(it.item_id)
                if not hit:
                    raise ValueError(f"Missing item_id {it.item_id} in model reply")
                ordered.append(hit)
            conn.execute(
                "INSERT OR REPLACE INTO sinitic_judgments(cache_key, prompt_version, response_json, created_at) VALUES (?, ?, ?, ?)",
                (key, SINITIC_PROMPT_VERSION, json.dumps(ordered, ensure_ascii=False), time.time()),
            )
            conn.commit()
            return ordered
        except Exception as exc:  # noqa: BLE001 — retry malformed LLM output
            last_err = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Sinitic screen batch failed after retries: {last_err}")


def run_sinitic_screen(
    *,
    min_generosity: int = 4,
    batch_size: int = 8,
    study1_path: Path | None = None,
    study2_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    study1_path = study1_path or (OUTPUT_DIR / "judgments_observed.csv")
    study2_path = study2_path or (OUTPUT_DIR / "attested_judgments_observed_blust194.csv")
    output_path = output_path or (OUTPUT_DIR / "sinitic_screen_hits.csv")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    items = _load_study1_hits(study1_path, min_generosity) + _load_study2_hits(
        study2_path, min_generosity
    )
    conn = _connect_cache(CACHE_PATH)
    results: list[dict] = []
    try:
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            judged = _judge_batch(batch, conn)
            for it, j in zip(batch, judged):
                results.append(
                    {
                        "study": it.study,
                        "item_id": it.item_id,
                        "gloss": it.gloss,
                        "form_summary": it.form_summary,
                        "generosity": it.generosity,
                        "chinese_loan_plausibility": int(j.get("chinese_loan_plausibility") or 0),
                        "likely_direction": j.get("likely_direction") or "",
                        "reasoning": j.get("reasoning") or "",
                        "prompt_version": SINITIC_PROMPT_VERSION,
                    }
                )
            print(f"Sinitic screen: {min(i + batch_size, len(items))}/{len(items)}")
    finally:
        conn.close()

    fieldnames = [
        "study",
        "item_id",
        "gloss",
        "form_summary",
        "generosity",
        "chinese_loan_plausibility",
        "likely_direction",
        "reasoning",
        "prompt_version",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Compact markdown table for the paper appendix
    md_path = OUTPUT_DIR / "sinitic_screen_hits.md"
    lines = [
        "# Sinitic loan plausibility screen (observed hits)",
        "",
        f"Prompt version `{SINITIC_PROMPT_VERSION}`; hits with generosity ≥ {min_generosity}.",
        "Score 1–5 = how plausible a Chinese loan into Tai-Kadai and/or Austronesian is as an explanation of the shared resemblance.",
        "",
        "| Study | Gloss / concept | Hit score | Chinese-loan plausibility | Direction |",
        "|-------|-----------------|----------:|--------------------------:|-----------|",
    ]
    for r in results:
        study = "1" if r["study"] == "study1" else "2"
        gloss = str(r["gloss"]).replace("|", "/")
        direction = str(r["likely_direction"]).replace("|", "/")
        lines.append(
            f"| {study} | {gloss} | {r['generosity']} | {r['chinese_loan_plausibility']} | {direction} |"
        )
    # Summary counts
    scores = [int(r["chinese_loan_plausibility"]) for r in results]
    from collections import Counter

    c = Counter(scores)
    lines.extend(
        [
            "",
            "## Score distribution",
            "",
            f"n = {len(scores)}; counts at 1–5: "
            + ", ".join(f"{k}:{c.get(k, 0)}" for k in range(1, 6)),
            f"Mean = {sum(scores)/len(scores):.2f}" if scores else "",
            f"Score ≥ 4: {sum(1 for s in scores if s >= 4)} / {len(scores)}",
            "",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path} and {md_path}")
    return output_path
