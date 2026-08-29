"""Recompute both studies with pronoun / deictic / nursery-kin slots removed.

Everything here runs off frozen caches and makes no API calls:

- Study 1 (LLM): replays the published permutations from the same seed and
  reads each assignment's generosity from the pair-judgment cache, so the null
  is the *same* 100 shuffles as the headline result, just scored over fewer
  slots.
- Study 2 (LLM): recomputes observed and per-permutation null hit counts from
  the frozen judgment CSVs, which store one row per concept per permutation.
- Both studies (algorithmic): reruns SCA/NED permutations over the retained
  slots only.

Usage: PYTHONPATH=. .venv/bin/python scripts/category_exclusion_rerun.py
"""

from __future__ import annotations

import csv
import json
import random
import sqlite3
import statistics
from collections import defaultdict
from pathlib import Path

from src.algo_score import run_algo_study1, run_algo_study2
from src.categories import study1_excluded, study2_excluded
from src.config import GENEROSITY_THRESHOLD, OUTPUT_DIR
from src.lexibank_check import read_eligible_pairs
from src.permute import permute_pan_values

CACHE_DB = Path("cache/judgments.sqlite3")
STUDY2_OBSERVED = OUTPUT_DIR / "attested_judgments_observed_blust194.csv"
STUDY2_NULL = OUTPUT_DIR / "attested_judgments_null_blust194_n30.csv"
N_PERM_STUDY1 = 100
SEED = 1


def _add_one_p(observed: float, null: list[float]) -> float:
    at_least = sum(1 for value in null if value >= observed)
    return (at_least + 1) / (len(null) + 1)


def _summary(observed: float, null: list[float]) -> dict[str, object]:
    mean = statistics.mean(null)
    sd = statistics.pstdev(null)
    return {
        "observed": observed,
        "null_mean": mean,
        "null_min": min(null),
        "null_max": max(null),
        "null_sd": sd,
        "z": (observed - mean) / sd if sd else float("nan"),
        "p_value": _add_one_p(observed, null),
    }


def study1_llm(level: str) -> dict[str, object]:
    pairs = read_eligible_pairs()
    excluded = study1_excluded(level)
    keep = [i for i, p in enumerate(pairs) if p.gloss not in excluded]

    conn = sqlite3.connect(CACHE_DB)
    scores: dict[tuple[str, str], int] = {
        (pkd, pan): int(gen)
        for pkd, pan, gen in conn.execute(
            "select pkd, pan, generosity from pair_judgments where generosity is not null"
        )
    }
    conn.close()

    def hits(assigned_pans: list[str], indices: list[int]) -> tuple[int, int]:
        found = missing = 0
        for i in indices:
            score = scores.get((pairs[i].pkd, assigned_pans[i]))
            if score is None:
                missing += 1
            elif score >= GENEROSITY_THRESHOLD:
                found += 1
        return found, missing

    observed_pans = [p.pan for p in pairs]
    obs_hits, obs_missing = hits(observed_pans, keep)

    rng = random.Random(SEED)
    null_hits: list[float] = []
    total_missing = 0
    for _ in range(N_PERM_STUDY1):
        shuffled = permute_pan_values(pairs, rng)
        found, missing = hits(shuffled, keep)
        total_missing += missing
        null_hits.append(float(found))

    result = _summary(float(obs_hits), null_hits)
    result.update(
        {
            "n_slots": len(keep),
            "n_excluded": len(pairs) - len(keep),
            "excluded_glosses": sorted(excluded),
            "n_permutations": N_PERM_STUDY1,
            "uncached_observed_cells": obs_missing,
            "uncached_null_cells": total_missing,
        }
    )
    return result


def study2_llm(level: str, threshold: int) -> dict[str, object]:
    excluded = study2_excluded(level)
    gloss_by_concept = {
        row["concept_id"]: row["concepticon_gloss"]
        for row in csv.DictReader(open("data/attested_pilot/core_concepts_blust.tsv"))
    }
    drop = {cid for cid, gloss in gloss_by_concept.items() if gloss in excluded}

    with STUDY2_OBSERVED.open(newline="", encoding="utf-8") as handle:
        obs_rows = [r for r in csv.DictReader(handle) if r["concept_id"] not in drop]
    obs_hits = sum(1 for r in obs_rows if int(r["generosity"]) >= threshold)

    per_perm: dict[str, int] = defaultdict(int)
    with STUDY2_NULL.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["concept_id"] in drop:
                continue
            per_perm.setdefault(row["permutation_id"], 0)
            if int(row["generosity"]) >= threshold:
                per_perm[row["permutation_id"]] += 1
    null_hits = [float(v) for v in per_perm.values()]

    result = _summary(float(obs_hits), null_hits)
    result.update(
        {
            "threshold": threshold,
            "n_concepts": len(obs_rows),
            "n_excluded": len(drop),
            "excluded_glosses": sorted(gloss_by_concept[c] for c in drop),
            "n_permutations": len(null_hits),
        }
    )
    return result


def main() -> None:
    report: dict[str, object] = {}

    for level in ("none", "core", "wide"):
        report[f"study1_llm_{level}"] = study1_llm(level)
        for threshold in (4, 3):
            report[f"study2_llm_ge{threshold}_{level}"] = study2_llm(level, threshold)

    for level in ("core", "wide"):
        report[f"study1_algo_{level}"] = run_algo_study1(
            n_permutations=1000,
            seed=SEED,
            exclusion_level=level,
        )
        report[f"study2_algo_{level}"] = run_algo_study2(
            n_permutations=1000,
            seed=SEED,
            workers=1,
            exclusion_level=level,
        )

    out = OUTPUT_DIR / "category_exclusion_rerun.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"\nWrote {out}")

    print("\n=== LLM ===")
    for level in ("none", "core", "wide"):
        r = report[f"study1_llm_{level}"]
        print(
            f"Study 1 ge4 [{level:4s}] n={r['n_slots']:3d} obs={r['observed']:.0f} "
            f"null={r['null_mean']:.2f} z={r['z']:.1f} p={r['p_value']:.4f} "
            f"(uncached cells: {r['uncached_null_cells']})"
        )
    for threshold in (4, 3):
        for level in ("none", "core", "wide"):
            r = report[f"study2_llm_ge{threshold}_{level}"]
            print(
                f"Study 2 ge{threshold} [{level:4s}] n={r['n_concepts']:3d} obs={r['observed']:.0f} "
                f"null={r['null_mean']:.2f} z={r['z']:.1f} p={r['p_value']:.4f}"
            )

    print("\n=== Algorithmic (N=1000) ===")
    for level in ("core", "wide"):
        for study in (1, 2):
            r = report[f"study{study}_algo_{level}"]
            for metric in ("mean_sca", "mean_ned"):
                b = r[metric]
                print(
                    f"Study {study} {metric} [{level:4s}] obs={b['observed']:.4f} "
                    f"null={b['null_mean']:.4f} z={b['z']:.2f} p={b['p_value']:.4f}"
                )


if __name__ == "__main__":
    main()
