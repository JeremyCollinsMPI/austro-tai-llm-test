from __future__ import annotations

import csv
import json
import random
from pathlib import Path

from .config import DEFAULT_PERMUTATIONS, ELIGIBLE_PAIRS_TSV, GENEROSITY_THRESHOLD, OUTPUT_DIR
from .judge import PairRequest, judge_pairs, judge_requests, summarize_judgments, write_judgments
from .lexibank_check import read_eligible_pairs
from .parse_smith import AlignedPair, read_aligned_pairs


def permute_pan_values(pairs: list[AlignedPair], rng: random.Random) -> list[str]:
    pans = [pair.pan for pair in pairs]
    shuffled = pans[:]
    attempts = 0
    while shuffled == pans and attempts < 20:
        rng.shuffle(shuffled)
        attempts += 1
    if shuffled == pans and len(pans) > 1:
        shuffled = pans[1:] + pans[:1]
    return shuffled


def observed_hit_count(judgments_path: Path) -> int:
    with judgments_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return sum(1 for row in reader if int(row.get("is_hit") or 0) == 1)


def _assignment_requests(pairs: list[AlignedPair], pans: list[str], permutation_id: int) -> list[PairRequest]:
    return [
        PairRequest(
            pair_id=pair.pair_id,
            gloss=pair.gloss,
            pkd=pair.pkd,
            pan=pans[index],
            pt=pair.pt,
            chinese_flag=pair.chinese_flag,
            notes=pair.notes,
        )
        for index, pair in enumerate(pairs)
    ]


def run_permutation_test(
    *,
    pairs_path: Path | None = None,
    n_permutations: int = DEFAULT_PERMUTATIONS,
    seed: int = 1,
    observed_judgments_path: Path | None = None,
    write_perm_csv: bool = False,
    use_eligible: bool = True,
) -> dict[str, object]:
    if pairs_path:
        pairs = read_aligned_pairs(pairs_path)
    elif use_eligible:
        pairs = read_eligible_pairs()
    else:
        pairs = read_aligned_pairs()
    print(f"Permutation test on {len(pairs)} eligible pairs ...")
    observed_judgments_path = observed_judgments_path or (OUTPUT_DIR / "judgments_observed.csv")

    if observed_judgments_path.exists():
        observed_hits = observed_hit_count(observed_judgments_path)
    else:
        observed = judge_pairs(pairs, permutation_id=0)
        write_judgments(observed, observed_judgments_path)
        observed_hits = sum(1 for j in observed if j.is_hit)

    rng = random.Random(seed)
    null_hits: list[int] = []
    null_summaries: list[dict[str, object]] = []

    for perm_index in range(1, n_permutations + 1):
        shuffled_pans = permute_pan_values(pairs, rng)
        requests = _assignment_requests(pairs, shuffled_pans, perm_index)
        judgments = judge_requests(requests, permutation_id=perm_index)
        hits = sum(1 for j in judgments if j.is_hit)
        null_hits.append(hits)
        summary = {
            "permutation_id": perm_index,
            "n_hits": hits,
            "hit_rate": hits / len(judgments) if judgments else 0.0,
        }
        if write_perm_csv:
            perm_path = OUTPUT_DIR / f"judgments_perm_{perm_index:04d}.csv"
            write_judgments(judgments, perm_path)
            summary["output_path"] = str(perm_path)
        null_summaries.append(summary)
        print(f"Permutation {perm_index}/{n_permutations}: hits={hits}")

    p_value = (sum(1 for value in null_hits if value >= observed_hits) + 1) / (len(null_hits) + 1)
    result = {
        "n_pairs": len(pairs),
        "generosity_threshold": GENEROSITY_THRESHOLD,
        "observed_hits": observed_hits,
        "observed_hit_rate": observed_hits / len(pairs) if pairs else 0.0,
        "n_permutations": n_permutations,
        "seed": seed,
        "null_hits_mean": sum(null_hits) / len(null_hits) if null_hits else 0.0,
        "null_hits_min": min(null_hits) if null_hits else 0,
        "null_hits_max": max(null_hits) if null_hits else 0,
        "p_value_one_sided": p_value,
        "null_hits": null_hits,
        "permutation_summaries": null_summaries,
    }

    out_path = OUTPUT_DIR / "permutation_results.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"null_hits", "permutation_summaries"}}, indent=2))
    return result
