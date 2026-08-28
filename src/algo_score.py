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


def form_length(form: str) -> int:
    return len(normalize_algo_form(form))


def pan_length_band(length: int) -> str:
    """Coarse PAN length bands (exact lengths have many singletons on Tier A)."""
    if length <= 3:
        return "le3"
    if length == 4:
        return "4"
    if length == 5:
        return "5"
    if length == 6:
        return "6"
    if length <= 9:
        return "7to9"
    if length <= 19:
        return "10to19"
    return "ge20"


def mean_form_length(forms: list[str]) -> float:
    lens = [len(f) for f in forms if f]
    return float(statistics.mean(lens)) if lens else 0.0


def an_group_length_band(mean_len: float) -> str:
    r = int(round(mean_len))
    if r <= 4:
        return "le4"
    if r == 5:
        return "5"
    if r == 6:
        return "6"
    if r == 7:
        return "7"
    return "ge8"


def permute_within_bands(values: list, bands: list[str], rng: random.Random) -> list:
    """Permute values among indices that share the same band label."""
    if len(values) != len(bands):
        raise ValueError("values and bands must have the same length")
    out = list(values)
    by_band: dict[str, list[int]] = {}
    for index, band in enumerate(bands):
        by_band.setdefault(band, []).append(index)
    for idxs in by_band.values():
        if len(idxs) <= 1:
            continue
        subset = [values[i] for i in idxs]
        original = subset[:]
        attempts = 0
        while attempts < 20:
            rng.shuffle(subset)
            if subset != original:
                break
            attempts += 1
        if subset == original and len(subset) > 1:
            subset = subset[1:] + subset[:1]
        for index, value in zip(idxs, subset):
            out[index] = value
    return out


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return float("nan")
    mx = statistics.mean(xs)
    my = statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = sum((x - mx) ** 2 for x in xs) ** 0.5
    deny = sum((y - my) ** 2 for y in ys) ** 0.5
    if denx == 0 or deny == 0:
        return float("nan")
    return float(num / (denx * deny))


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
    null_mean = float(statistics.mean(null_values)) if null_values else float("nan")
    null_sd = float(statistics.pstdev(null_values)) if len(null_values) > 1 else float("nan")
    z = (observed - null_mean) / null_sd if null_sd and null_sd == null_sd and null_sd != 0 else float("nan")
    return {
        "observed": observed,
        "null_mean": null_mean,
        "null_median": float(statistics.median(null_values)) if null_values else float("nan"),
        "null_min": float(min(null_values)) if null_values else float("nan"),
        "null_max": float(max(null_values)) if null_values else float("nan"),
        "null_sd": null_sd,
        "z": z,
        "p_value": p,
    }


def run_algo_study1(
    *,
    n_permutations: int = ALGO_N_PERM_DEFAULT,
    seed: int = ALGO_SEED,
    pairs_path: Path | None = None,
    output_path: Path | None = None,
    length_controlled: bool = False,
) -> dict[str, object]:
    pairs = read_eligible_pairs(pairs_path)
    mode = "length-controlled" if length_controlled else "unrestricted"
    print(f"Algo Study 1 ({mode}): {len(pairs)} Tier A pairs; N={n_permutations}")

    observed_rows: list[dict[str, object]] = []
    for pair in pairs:
        dists = pair_distances(pair.pan, pair.pkd)
        pan_len = form_length(pair.pan)
        pkd_len = form_length(pair.pkd)
        observed_rows.append(
            {
                "pair_id": pair.pair_id,
                "gloss": pair.gloss,
                "pan": pair.pan,
                "pkd": pair.pkd,
                "pan_len": pan_len,
                "pkd_len": pkd_len,
                "abs_delta_len": abs(pan_len - pkd_len),
                "pan_length_band": pan_length_band(pan_len),
                "sca": dists["sca"],
                "ned": dists["ned"],
                "sca_hit": int(dists["sca"] <= SCA_HIT_THRESHOLD),
                "ned_hit": int(dists["ned"] <= NED_HIT_THRESHOLD),
            }
        )

    obs_mean_sca = statistics.mean(float(r["sca"]) for r in observed_rows)
    obs_mean_ned = statistics.mean(float(r["ned"]) for r in observed_rows)
    obs_sca_hits = sum(int(r["sca_hit"]) for r in observed_rows)
    obs_ned_hits = sum(int(r["ned_hit"]) for r in observed_rows)
    obs_mean_dlen = statistics.mean(float(r["abs_delta_len"]) for r in observed_rows)
    corr_sca_dlen = _pearson(
        [float(r["abs_delta_len"]) for r in observed_rows],
        [float(r["sca"]) for r in observed_rows],
    )
    corr_ned_dlen = _pearson(
        [float(r["abs_delta_len"]) for r in observed_rows],
        [float(r["ned"]) for r in observed_rows],
    )

    pans = [pair.pan for pair in pairs]
    pkds = [pair.pkd for pair in pairs]
    pan_bands = [pan_length_band(form_length(pan)) for pan in pans]
    band_counts = {b: pan_bands.count(b) for b in sorted(set(pan_bands))}
    print(f"  PAN length bands: {band_counts}")

    sca_mat = [[sca_distance(pan, pkd) for pan in pans] for pkd in pkds]
    ned_mat = [[ned_distance(pan, pkd) for pan in pans] for pkd in pkds]
    pan_index = {pan: i for i, pan in enumerate(pans)}

    rng = random.Random(seed)
    null_mean_sca: list[float] = []
    null_mean_ned: list[float] = []
    null_sca_hits: list[int] = []
    null_ned_hits: list[int] = []
    null_mean_dlen: list[float] = []

    for perm_index in range(1, n_permutations + 1):
        if length_controlled:
            shuffled = permute_within_bands(pans, pan_bands, rng)
        else:
            shuffled = permute_pan_values(pairs, rng)
        sca_vals = []
        ned_vals = []
        dlen_vals = []
        sca_hits = 0
        ned_hits = 0
        for row_i, pan in enumerate(shuffled):
            col = pan_index[pan]
            s = sca_mat[row_i][col]
            n = ned_mat[row_i][col]
            sca_vals.append(s)
            ned_vals.append(n)
            dlen_vals.append(abs(form_length(pan) - form_length(pkds[row_i])))
            if s <= SCA_HIT_THRESHOLD:
                sca_hits += 1
            if n <= NED_HIT_THRESHOLD:
                ned_hits += 1
        null_mean_sca.append(float(statistics.mean(sca_vals)))
        null_mean_ned.append(float(statistics.mean(ned_vals)))
        null_sca_hits.append(sca_hits)
        null_ned_hits.append(ned_hits)
        null_mean_dlen.append(float(statistics.mean(dlen_vals)))
        if perm_index % 100 == 0 or perm_index == 1:
            print(
                f"  perm {perm_index}/{n_permutations}: "
                f"mean_sca={null_mean_sca[-1]:.3f} mean_ned={null_mean_ned[-1]:.3f} "
                f"mean_|dlen|={null_mean_dlen[-1]:.3f}"
            )

    result: dict[str, object] = {
        "study": 1,
        "length_controlled": length_controlled,
        "length_band_definition": "PAN coarse bands le3/4/5/6/7to9/10to19/ge20",
        "pan_length_band_counts": band_counts,
        "n_pairs": len(pairs),
        "n_permutations": n_permutations,
        "seed": seed,
        "sca_hit_threshold": SCA_HIT_THRESHOLD,
        "ned_hit_threshold": NED_HIT_THRESHOLD,
        "mean_sca": _summarize_null(obs_mean_sca, null_mean_sca, lower_is_better=True),
        "mean_ned": _summarize_null(obs_mean_ned, null_mean_ned, lower_is_better=True),
        "sca_hits": _summarize_null(float(obs_sca_hits), [float(x) for x in null_sca_hits], lower_is_better=False),
        "ned_hits": _summarize_null(float(obs_ned_hits), [float(x) for x in null_ned_hits], lower_is_better=False),
        "mean_abs_delta_len": _summarize_null(obs_mean_dlen, null_mean_dlen, lower_is_better=True),
        "observed_corr_sca_vs_abs_delta_len": corr_sca_dlen,
        "observed_corr_ned_vs_abs_delta_len": corr_ned_dlen,
        "observed_pair_rows_path": str(
            OUTPUT_DIR / ("algo_judgments_study1_length.csv" if length_controlled else "algo_judgments_study1.csv")
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows_path = Path(str(result["observed_pair_rows_path"]))
    with rows_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(observed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(observed_rows)

    if output_path is None:
        output_path = OUTPUT_DIR / (
            "algo_permutation_study1_length.json" if length_controlled else "algo_permutation_study1.json"
        )
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {rows_path}")
    print(f"Wrote {output_path}")
    print(
        f"Study 1 mean SCA: obs={obs_mean_sca:.3f} null≈{result['mean_sca']['null_mean']:.3f} "  # type: ignore[index]
        f"z={result['mean_sca']['z']:.2f} p={result['mean_sca']['p_value']:.4f}"  # type: ignore[index]
    )
    print(
        f"Study 1 mean NED: obs={obs_mean_ned:.3f} null≈{result['mean_ned']['null_mean']:.3f} "  # type: ignore[index]
        f"z={result['mean_ned']['z']:.2f} p={result['mean_ned']['p_value']:.4f}"  # type: ignore[index]
    )
    print(
        f"Study 1 mean |Δlen|: obs={obs_mean_dlen:.3f} "
        f"null≈{result['mean_abs_delta_len']['null_mean']:.3f}"  # type: ignore[index]
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
    length_controlled: bool = False,
    matrix_cache_path: Path | None = None,
) -> dict[str, object]:
    import numpy as np

    core_path = core_path or (Path("data/attested_pilot/core_concepts_blust.tsv"))
    matrix_cache_path = matrix_cache_path or (OUTPUT_DIR / "algo_study2_blust194_mats.npz")
    prepared = prepare_concept_samples(force=False, core_path=core_path)
    n = len(prepared)
    mode = "length-controlled" if length_controlled else "unrestricted"
    print(f"Algo Study 2 ({mode}): {n} concepts")

    tk_groups = [_extract_forms(list(item["tk_forms"])) for item in prepared]
    an_groups = [_extract_forms(list(item["an_forms"])) for item in prepared]
    concept_ids = [str(item["concept_id"]) for item in prepared]
    tk_mean_lens = [mean_form_length(g) for g in tk_groups]
    an_mean_lens = [mean_form_length(g) for g in an_groups]
    an_bands = [an_group_length_band(m) for m in an_mean_lens]
    band_counts = {b: an_bands.count(b) for b in sorted(set(an_bands))}
    print(f"  AN mean-length bands: {band_counts}")

    if matrix_cache_path.exists():
        print(f"  Loading distance matrices from {matrix_cache_path}")
        cached = np.load(matrix_cache_path, allow_pickle=True)
        sca_mat = cached["sca"].tolist()
        ned_mat = cached["ned"].tolist()
        if len(sca_mat) != n:
            raise ValueError(f"Cached matrix size {len(sca_mat)} != n_concepts {n}")
    else:
        print(f"  Building {n}x{n} set-score matrices (SCA + NED); workers={workers} ...")
        sca_mat = [[0.0] * n for _ in range(n)]
        ned_mat = [[0.0] * n for _ in range(n)]
        tasks = [(i, tk_groups[i], an_groups) for i in range(n)]
        done = 0
        if workers <= 1:
            for task in tasks:
                i, sca_row, ned_row = _matrix_row(task)
                sca_mat[i] = sca_row
                ned_mat[i] = ned_row
                done += 1
                if done % 5 == 0 or done == n:
                    print(f"  matrix rows {done}/{n}", flush=True)
        else:
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = [pool.submit(_matrix_row, task) for task in tasks]
                for fut in as_completed(futures):
                    i, sca_row, ned_row = fut.result()
                    sca_mat[i] = sca_row
                    ned_mat[i] = ned_row
                    done += 1
                    if done % 10 == 0 or done == n:
                        print(f"  matrix rows {done}/{n}", flush=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            matrix_cache_path,
            sca=np.asarray(sca_mat, dtype=float),
            ned=np.asarray(ned_mat, dtype=float),
            concept_ids=np.asarray(concept_ids),
        )
        print(f"  Cached matrices -> {matrix_cache_path}")

    obs_sca = [sca_mat[i][i] for i in range(n)]
    obs_ned = [ned_mat[i][i] for i in range(n)]
    obs_mean_sca = float(statistics.mean(obs_sca))
    obs_mean_ned = float(statistics.mean(obs_ned))
    obs_sca_hits = sum(1 for v in obs_sca if v <= SCA_HIT_THRESHOLD)
    obs_ned_hits = sum(1 for v in obs_ned if v <= NED_HIT_THRESHOLD)
    obs_dlen = [abs(tk_mean_lens[i] - an_mean_lens[i]) for i in range(n)]
    obs_mean_dlen = float(statistics.mean(obs_dlen))
    corr_sca_dlen = _pearson(obs_dlen, obs_sca)
    corr_ned_dlen = _pearson(obs_dlen, obs_ned)

    observed_rows = [
        {
            "concept_id": concept_ids[i],
            "name": prepared[i].get("name") or concept_ids[i],
            "n_tk_forms": len(tk_groups[i]),
            "n_an_forms": len(an_groups[i]),
            "tk_mean_len": tk_mean_lens[i],
            "an_mean_len": an_mean_lens[i],
            "abs_delta_mean_len": obs_dlen[i],
            "an_length_band": an_bands[i],
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
    null_mean_dlen: list[float] = []

    print(f"Running {n_permutations} group-shuffle nulls ({mode}) ...")
    identity = list(range(n))
    for perm_index in range(1, n_permutations + 1):
        if length_controlled:
            order = permute_within_bands(identity, an_bands, rng)
        else:
            order = list(range(n))
            attempts = 0
            while attempts < 20:
                rng.shuffle(order)
                if order != identity:
                    break
                attempts += 1
            if order == identity and n > 1:
                order = list(range(1, n)) + [0]
        sca_vals = [sca_mat[i][order[i]] for i in range(n)]
        ned_vals = [ned_mat[i][order[i]] for i in range(n)]
        dlen_vals = [abs(tk_mean_lens[i] - an_mean_lens[order[i]]) for i in range(n)]
        null_mean_sca.append(float(statistics.mean(sca_vals)))
        null_mean_ned.append(float(statistics.mean(ned_vals)))
        null_sca_hits.append(sum(1 for v in sca_vals if v <= SCA_HIT_THRESHOLD))
        null_ned_hits.append(sum(1 for v in ned_vals if v <= NED_HIT_THRESHOLD))
        null_mean_dlen.append(float(statistics.mean(dlen_vals)))
        if perm_index % 100 == 0 or perm_index == 1:
            print(
                f"  perm {perm_index}/{n_permutations}: "
                f"mean_sca={null_mean_sca[-1]:.3f} mean_ned={null_mean_ned[-1]:.3f} "
                f"mean_|dlen|={null_mean_dlen[-1]:.3f}"
            )

    result: dict[str, object] = {
        "study": 2,
        "length_controlled": length_controlled,
        "length_band_definition": "AN group mean-length bands le4/5/6/7/ge8",
        "an_length_band_counts": band_counts,
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
        "mean_abs_delta_mean_len": _summarize_null(obs_mean_dlen, null_mean_dlen, lower_is_better=True),
        "observed_corr_sca_vs_abs_delta_mean_len": corr_sca_dlen,
        "observed_corr_ned_vs_abs_delta_mean_len": corr_ned_dlen,
        "matrix_cache_path": str(matrix_cache_path),
        "observed_rows_path": str(
            OUTPUT_DIR
            / (
                "algo_judgments_study2_blust194_length.csv"
                if length_controlled
                else "algo_judgments_study2_blust194.csv"
            )
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rows_path = Path(str(result["observed_rows_path"]))
    with rows_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(observed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(observed_rows)

    if output_path is None:
        output_path = OUTPUT_DIR / (
            "algo_permutation_study2_blust194_length.json"
            if length_controlled
            else "algo_permutation_study2_blust194.json"
        )
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {rows_path}")
    print(f"Wrote {output_path}")
    print(
        f"Study 2 mean SCA: obs={obs_mean_sca:.3f} null≈{result['mean_sca']['null_mean']:.3f} "  # type: ignore[index]
        f"z={result['mean_sca']['z']:.2f} p={result['mean_sca']['p_value']:.4f}"  # type: ignore[index]
    )
    print(
        f"Study 2 mean NED: obs={obs_mean_ned:.3f} null≈{result['mean_ned']['null_mean']:.3f} "  # type: ignore[index]
        f"z={result['mean_ned']['z']:.2f} p={result['mean_ned']['p_value']:.4f}"  # type: ignore[index]
    )
    return result
