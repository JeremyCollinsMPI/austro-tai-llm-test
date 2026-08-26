"""Algorithmic (LingPy-style) form-similarity sanity check for Studies 1–2.

Primary continuous statistic: mean SCA / NED distance under the same
permutation nulls as the LLM screens. Lower distance = more similar.
"""

from __future__ import annotations

import csv
import json
import logging
import random
import re
import statistics
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from lingpy.align.pairwise import Pairwise, edit_dist

from .attested_pilot import prepare_concept_samples
from .config import OUTPUT_DIR
from .lexibank_check import read_eligible_pairs
from .permute import permute_pan_values

# Silence LingPy model-compile chatter on import/use.
logging.getLogger("lingpy").setLevel(logging.WARNING)

ALGO_SEED = 1
ALGO_N_PERM_DEFAULT = 1000
# Secondary hit thresholds (distance ≤ threshold); mean distance is primary.
SCA_HIT_THRESHOLD = 0.40
NED_HIT_THRESHOLD = 0.40


def normalize_algo_form(form: str) -> str:
    """Light strip aligned with Study 2 form cleanup (tones / separators / brackets)."""
    text = (form or "").lower().strip()
    text = text.lstrip("*")
    text = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉0-9]+", "", text)
    text = re.sub(r"[.\-_/\\|]+", "", text)
    text = re.sub(r"[()\[\]{}<>]+", "", text)
    text = re.sub(r"\s+", "", text)
    return text


def sca_distance(a: str, b: str) -> float:
    a_n = normalize_algo_form(a)
    b_n = normalize_algo_form(b)
    if not a_n or not b_n:
        return 1.0
    if a_n == b_n:
        return 0.0
    pair = Pairwise(a_n, b_n)
    pair.align(distance=True)
    return float(pair.alignments[0][2])


def ned_distance(a: str, b: str) -> float:
    a_n = normalize_algo_form(a)
    b_n = normalize_algo_form(b)
    if not a_n or not b_n:
        return 1.0
    if a_n == b_n:
        return 0.0
    return float(edit_dist(a_n, b_n, normalized=True))


def pair_distances(pan: str, pkd: str) -> dict[str, float]:
    return {"sca": sca_distance(pan, pkd), "ned": ned_distance(pan, pkd)}


def _extract_forms(forms: list[dict[str, str]] | list[str]) -> list[str]:
    out: list[str] = []
    for item in forms:
        raw = str(item.get("form") or "") if isinstance(item, dict) else str(item)
        norm = normalize_algo_form(raw)
        if norm:
            out.append(norm)
    return out


def _distance_normalized(a: str, b: str, *, metric: str) -> float:
    """Distance on already-normalized non-empty strings."""
    if a == b:
        return 0.0
    if metric == "sca":
        pair = Pairwise(a, b)
        pair.align(distance=True)
        return float(pair.alignments[0][2])
    return float(edit_dist(a, b, normalized=True))


def set_distance(
    tk_forms: list[dict[str, str]] | list[str],
    an_forms: list[dict[str, str]] | list[str],
    *,
    metric: str,
) -> float:
    """Mean over TK forms of best (min) distance to any AN form."""
    tk = _extract_forms(tk_forms)
    an = _extract_forms(an_forms)
    if not tk or not an:
        return 1.0
    bests: list[float] = []
    for t in tk:
        best = min(_distance_normalized(t, a, metric=metric) for a in an)
        bests.append(best)
    return float(statistics.mean(bests))


def _one_sided_p_lower(observed: float, null_values: list[float]) -> float:
    """Smaller-is-better: fraction of nulls ≤ observed, with add-one smoothing."""
    k = sum(1 for value in null_values if value <= observed)
    return (k + 1) / (len(null_values) + 1)


def _one_sided_p_higher(observed: float, null_values: list[float]) -> float:
    k = sum(1 for value in null_values if value >= observed)
    return (k + 1) / (len(null_values) + 1)


def _summarize_null(observed: float, null_values: list[float], *, lower_is_better: bool) -> dict[str, float]:
    p = (
        _one_sided_p_lower(observed, null_values)
        if lower_is_better
        else _one_sided_p_higher(observed, null_values)
    )
    return {
        "observed": observed,
        "null_mean": float(statistics.mean(null_values)) if null_values else float("nan"),
        "null_median": float(statistics.median(null_values)) if null_values else float("nan"),
        "null_min": float(min(null_values)) if null_values else float("nan"),
        "null_max": float(max(null_values)) if null_values else float("nan"),
        "p_value": p,
    }


def run_algo_study1(
    *,
    n_permutations: int = ALGO_N_PERM_DEFAULT,
    seed: int = ALGO_SEED,
    pairs_path: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, object]:
    pairs = read_eligible_pairs(pairs_path)
    print(f"Algo Study 1: {len(pairs)} Tier A pairs; N={n_permutations}")

    observed_rows: list[dict[str, object]] = []
    for pair in pairs:
        dists = pair_distances(pair.pan, pair.pkd)
        observed_rows.append(
            {
                "pair_id": pair.pair_id,
                "gloss": pair.gloss,
                "pan": pair.pan,
                "pkd": pair.pkd,
                "sca": dists["sca"],
                "ned": dists["ned"],
                "sca_hit": int(dists["sca"] <= SCA_HIT_THRESHOLD),
                "ned_hit": int(dists["ned"] <= NED_HIT_THRESHOLD),
            }
        )

    obs_mean_sca = statistics.mean(r["sca"] for r in observed_rows)  # type: ignore[arg-type]
    obs_mean_ned = statistics.mean(r["ned"] for r in observed_rows)  # type: ignore[arg-type]
    obs_sca_hits = sum(int(r["sca_hit"]) for r in observed_rows)
    obs_ned_hits = sum(int(r["ned_hit"]) for r in observed_rows)

    # Full PKD x PAN distance matrix for fast null rematching.
    pans = [pair.pan for pair in pairs]
    pkds = [pair.pkd for pair in pairs]
    sca_mat = [[sca_distance(pan, pkd) for pan in pans] for pkd in pkds]
    ned_mat = [[ned_distance(pan, pkd) for pan in pans] for pkd in pkds]
    # Index by original PAN order so shuffle of pans maps to column indices.
    pan_index = {pan: i for i, pan in enumerate(pans)}

    rng = random.Random(seed)
    null_mean_sca: list[float] = []
    null_mean_ned: list[float] = []
    null_sca_hits: list[int] = []
    null_ned_hits: list[int] = []

    for perm_index in range(1, n_permutations + 1):
        shuffled = permute_pan_values(pairs, rng)
        sca_vals = []
        ned_vals = []
        sca_hits = 0
        ned_hits = 0
        for row_i, pan in enumerate(shuffled):
            col = pan_index[pan]
            s = sca_mat[row_i][col]
            n = ned_mat[row_i][col]
            sca_vals.append(s)
            ned_vals.append(n)
            if s <= SCA_HIT_THRESHOLD:
                sca_hits += 1
            if n <= NED_HIT_THRESHOLD:
                ned_hits += 1
        null_mean_sca.append(float(statistics.mean(sca_vals)))
        null_mean_ned.append(float(statistics.mean(ned_vals)))
        null_sca_hits.append(sca_hits)
        null_ned_hits.append(ned_hits)
        if perm_index % 100 == 0 or perm_index == 1:
            print(
                f"  perm {perm_index}/{n_permutations}: "
                f"mean_sca={null_mean_sca[-1]:.3f} mean_ned={null_mean_ned[-1]:.3f}"
            )

    result: dict[str, object] = {
        "study": 1,
        "n_pairs": len(pairs),
        "n_permutations": n_permutations,
        "seed": seed,
        "sca_hit_threshold": SCA_HIT_THRESHOLD,
        "ned_hit_threshold": NED_HIT_THRESHOLD,
        "mean_sca": _summarize_null(obs_mean_sca, null_mean_sca, lower_is_better=True),
        "mean_ned": _summarize_null(obs_mean_ned, null_mean_ned, lower_is_better=True),
        "sca_hits": _summarize_null(float(obs_sca_hits), [float(x) for x in null_sca_hits], lower_is_better=False),
        "ned_hits": _summarize_null(float(obs_ned_hits), [float(x) for x in null_ned_hits], lower_is_better=False),
        "observed_pair_rows_path": str(OUTPUT_DIR / "algo_judgments_study1.csv"),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows_path = OUTPUT_DIR / "algo_judgments_study1.csv"
    with rows_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(observed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(observed_rows)

    output_path = output_path or (OUTPUT_DIR / "algo_permutation_study1.json")
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {rows_path}")
    print(f"Wrote {output_path}")
    print(
        f"Study 1 mean SCA: obs={obs_mean_sca:.3f} null≈{result['mean_sca']['null_mean']:.3f} "  # type: ignore[index]
        f"p={result['mean_sca']['p_value']:.4f}"  # type: ignore[index]
    )
    print(
        f"Study 1 mean NED: obs={obs_mean_ned:.3f} null≈{result['mean_ned']['null_mean']:.3f} "  # type: ignore[index]
        f"p={result['mean_ned']['p_value']:.4f}"  # type: ignore[index]
    )
    return result


def _matrix_row(args: tuple[int, list[str], list[list[str]]]) -> tuple[int, list[float], list[float]]:
    """Worker: distances from one TK group to every AN group (SCA + NED)."""
    i, tk, an_groups = args
    sca_row = [set_distance(tk, an, metric="sca") for an in an_groups]
    ned_row = [set_distance(tk, an, metric="ned") for an in an_groups]
    return i, sca_row, ned_row


def run_algo_study2(
    *,
    n_permutations: int = ALGO_N_PERM_DEFAULT,
    seed: int = ALGO_SEED,
    core_path: Path | None = None,
    output_path: Path | None = None,
    workers: int = 8,
) -> dict[str, object]:
    core_path = core_path or (Path("data/attested_pilot/core_concepts_blust.tsv"))
    prepared = prepare_concept_samples(force=False, core_path=core_path)
    n = len(prepared)
    print(f"Algo Study 2: {n} concepts; building {n}x{n} set-score matrices (SCA + NED) ...")

    # Pre-normalize forms once; set_distance still accepts dicts, but we pass strings.
    tk_groups = [_extract_forms(list(item["tk_forms"])) for item in prepared]
    an_groups = [_extract_forms(list(item["an_forms"])) for item in prepared]
    concept_ids = [str(item["concept_id"]) for item in prepared]

    sca_mat = [[0.0] * n for _ in range(n)]
    ned_mat = [[0.0] * n for _ in range(n)]
    tasks = [(i, tk_groups[i], an_groups) for i in range(n)]
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_matrix_row, task) for task in tasks]
        for fut in as_completed(futures):
            i, sca_row, ned_row = fut.result()
            sca_mat[i] = sca_row
            ned_mat[i] = ned_row
            done += 1
            if done % 10 == 0 or done == n:
                print(f"  matrix rows {done}/{n}", flush=True)

    obs_sca = [sca_mat[i][i] for i in range(n)]
    obs_ned = [ned_mat[i][i] for i in range(n)]
    obs_mean_sca = float(statistics.mean(obs_sca))
    obs_mean_ned = float(statistics.mean(obs_ned))
    obs_sca_hits = sum(1 for v in obs_sca if v <= SCA_HIT_THRESHOLD)
    obs_ned_hits = sum(1 for v in obs_ned if v <= NED_HIT_THRESHOLD)

    observed_rows = [
        {
            "concept_id": concept_ids[i],
            "name": prepared[i].get("name") or concept_ids[i],
            "n_tk_forms": len(tk_groups[i]),
            "n_an_forms": len(an_groups[i]),
            "sca": obs_sca[i],
            "ned": obs_ned[i],
            "sca_hit": int(obs_sca[i] <= SCA_HIT_THRESHOLD),
            "ned_hit": int(obs_ned[i] <= NED_HIT_THRESHOLD),
        }
        for i in range(n)
    ]

    rng = random.Random(seed)
    null_mean_sca: list[float] = []
    null_mean_ned: list[float] = []
    null_sca_hits: list[int] = []
    null_ned_hits: list[int] = []

    print(f"Running {n_permutations} group-shuffle nulls ...")
    for perm_index in range(1, n_permutations + 1):
        order = list(range(n))
        # Avoid identity if possible
        attempts = 0
        while attempts < 20:
            rng.shuffle(order)
            if order != list(range(n)):
                break
            attempts += 1
        if order == list(range(n)) and n > 1:
            order = list(range(1, n)) + [0]
        sca_vals = [sca_mat[i][order[i]] for i in range(n)]
        ned_vals = [ned_mat[i][order[i]] for i in range(n)]
        null_mean_sca.append(float(statistics.mean(sca_vals)))
        null_mean_ned.append(float(statistics.mean(ned_vals)))
        null_sca_hits.append(sum(1 for v in sca_vals if v <= SCA_HIT_THRESHOLD))
        null_ned_hits.append(sum(1 for v in ned_vals if v <= NED_HIT_THRESHOLD))
        if perm_index % 100 == 0 or perm_index == 1:
            print(
                f"  perm {perm_index}/{n_permutations}: "
                f"mean_sca={null_mean_sca[-1]:.3f} mean_ned={null_mean_ned[-1]:.3f}"
            )

    result: dict[str, object] = {
        "study": 2,
        "n_concepts": n,
        "n_permutations": n_permutations,
        "seed": seed,
        "core_path": str(core_path),
        "aggregation": "mean_of_per_tk_best_an_match",
        "sca_hit_threshold": SCA_HIT_THRESHOLD,
        "ned_hit_threshold": NED_HIT_THRESHOLD,
        "mean_sca": _summarize_null(obs_mean_sca, null_mean_sca, lower_is_better=True),
        "mean_ned": _summarize_null(obs_mean_ned, null_mean_ned, lower_is_better=True),
        "sca_hits": _summarize_null(float(obs_sca_hits), [float(x) for x in null_sca_hits], lower_is_better=False),
        "ned_hits": _summarize_null(float(obs_ned_hits), [float(x) for x in null_ned_hits], lower_is_better=False),
        "observed_rows_path": str(OUTPUT_DIR / "algo_judgments_study2_blust194.csv"),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows_path = OUTPUT_DIR / "algo_judgments_study2_blust194.csv"
    with rows_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(observed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(observed_rows)

    output_path = output_path or (OUTPUT_DIR / "algo_permutation_study2_blust194.json")
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {rows_path}")
    print(f"Wrote {output_path}")
    print(
        f"Study 2 mean SCA: obs={obs_mean_sca:.3f} null≈{result['mean_sca']['null_mean']:.3f} "  # type: ignore[index]
        f"p={result['mean_sca']['p_value']:.4f}"  # type: ignore[index]
    )
    print(
        f"Study 2 mean NED: obs={obs_mean_ned:.3f} null≈{result['mean_ned']['null_mean']:.3f} "  # type: ignore[index]
        f"p={result['mean_ned']['p_value']:.4f}"  # type: ignore[index]
    )
    return result
