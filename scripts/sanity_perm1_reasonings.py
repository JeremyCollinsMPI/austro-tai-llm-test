"""Compare observed vs perm-1 cached set-judgments (no new API calls)."""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sqlite3

from src.attested_pilot import (
    ATTESTED_PROMPT_VERSION,
    CACHE_DIR,
    SYSTEM_PROMPT,
    _forms_payload,
    prepare_concept_samples,
)


def lookup(conn: sqlite3.Connection, tk_forms, an_forms):
    user_payload = [
        {
            "comparison_id": "set001",
            "bag_a_forms": _forms_payload(tk_forms),
            "bag_b_forms": _forms_payload(an_forms),
        }
    ]
    user_prompt = (
        "For each item, score hypothetical cognacy between bag_a and bag_b on shape alone. "
        "Do not use meaning.\n\n"
        + json.dumps(user_payload, ensure_ascii=False, indent=2)
    )
    key_payload = {
        "prompt_version": ATTESTED_PROMPT_VERSION,
        "system": SYSTEM_PROMPT,
        "user": user_prompt,
    }
    key = hashlib.sha256(json.dumps(key_payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    row = conn.execute("SELECT response_json FROM set_judgments WHERE cache_key=?", (key,)).fetchone()
    if not row:
        return None
    arr = json.loads(row[0])
    item = arr[0] if arr else {}
    return {
        "generosity": int(item.get("generosity", -1)),
        "notes": item.get("shared_shape_notes") or "",
        "reasoning": item.get("reasoning") or "",
    }


def main() -> None:
    prepared = prepare_concept_samples(force=False)
    obs_rows = {
        r["concept_id"]: r
        for r in csv.DictReader(open("output/attested_judgments_observed.csv", encoding="utf-8"))
    }

    an_sets = [list(item["an_forms"]) for item in prepared]
    rng = random.Random(1)
    shuffled = an_sets[:]
    rng.shuffle(shuffled)
    if shuffled == an_sets and len(shuffled) > 1:
        shuffled = an_sets[1:] + an_sets[:1]

    conn = sqlite3.connect(CACHE_DIR / "attested_set_judgments.sqlite3")

    mismatches = []
    hits_obs = []
    for item, an_forms in zip(prepared, shuffled, strict=True):
        tk_cid = item["concept_id"]
        src_an = None
        for j, orig in enumerate(an_sets):
            if orig is an_forms:
                src_an = prepared[j]["concept_id"]
                break
        obs_g = int(obs_rows[tk_cid]["generosity"])
        null = lookup(conn, item["tk_forms"], an_forms)
        mismatches.append((tk_cid, src_an, obs_g, null))
        if obs_g >= 3:
            hits_obs.append((tk_cid, src_an, obs_g, null))

    ok = sum(1 for *_, n in mismatches if n)
    h4 = sum(1 for *_, n in mismatches if n and n["generosity"] >= 4)
    h3 = sum(1 for *_, n in mismatches if n and n["generosity"] >= 3)
    print(f"perm1 lookup success: {ok}/{len(mismatches)}; hits@4={h4} @3={h3}")

    print("\n=== OBSERVED HITS: same TK bag vs mismatched AN (perm1) ===\n")
    for tk, src_an, og, null in hits_obs:
        ng = null["generosity"] if null else "MISS"
        print(f"## TK={tk}  observed_gen={og}  |  paired with AN-from={src_an}  null_gen={ng}")
        if null:
            print(f"NULL notes: {null['notes'][:240]}")
            print(f"NULL reason: {null['reasoning'][:420]}")
        print()

    print("=== NULL HIGH SCORES in perm1 (gen>=3) ===\n")
    for tk, src_an, og, null in mismatches:
        if null and null["generosity"] >= 3:
            print(f"## TK={tk}(obs={og}) <- AN={src_an}  null_gen={null['generosity']}")
            print(f"notes: {null['notes'][:240]}")
            print(f"reason: {null['reasoning'][:420]}")
            print()

    print("=== Where true AN bags of observed-hit concepts landed ===\n")
    hit_cids = {tk for tk, *_ in hits_obs}
    for item, an_forms in zip(prepared, shuffled, strict=True):
        src_an = None
        for j, orig in enumerate(an_sets):
            if orig is an_forms:
                src_an = prepared[j]["concept_id"]
                break
        if src_an in hit_cids and item["concept_id"] != src_an:
            null = lookup(conn, item["tk_forms"], an_forms)
            og = int(obs_rows[item["concept_id"]]["generosity"])
            ng = null["generosity"] if null else "MISS"
            print(f"AN-from={src_an} -> TK={item['concept_id']}(obs={og}) null_gen={ng}")
            if null:
                print(f"  reason: {null['reasoning'][:300]}")
            print()

    print("=== Score drop summary (observed hits in perm1) ===")
    for tk, src_an, og, null in hits_obs:
        ng = null["generosity"] if null else None
        delta = (og - ng) if ng is not None else None
        print(f"{tk}: {og} -> {ng} (delta={delta}), mismatched AN={src_an}")

    # Also print observed reasonings for hits for side-by-side
    print("\n=== OBSERVED hit reasonings (for side-by-side) ===\n")
    for tk, *_ in hits_obs:
        r = obs_rows[tk]
        print(f"## {tk} gen={r['generosity']}")
        print(f"notes: {r.get('shared_shape_notes', '')[:240]}")
        print(f"reason: {r.get('reasoning', '')[:420]}")
        print()

    conn.close()


if __name__ == "__main__":
    main()
