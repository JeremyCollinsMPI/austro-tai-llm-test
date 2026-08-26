"""Attested Lexibank set-vs-set cognacy pilot (no reconstructions)."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import random
import re
import sqlite3
import time
import zipfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .an_sampling import load_language_clades as load_an_clades
from .an_sampling import sample_austronesian_forms
from .config import (
    AN_SAMPLE_SEED,
    CACHE_DIR,
    DATA_DIR,
    LEXIBANK_AN_ATTESTATION_CACHE,
    LEXIBANK_DIR,
    OUTPUT_DIR,
)
from .json_utils import extract_json_array
from .nlp_client import chat

ATTESTED_DIR = DATA_DIR / "attested_pilot"
CORE_CONCEPTS_TSV = ATTESTED_DIR / "core_concepts.tsv"
BLUST_210_TSV = ATTESTED_DIR / "Blust-2008-210.tsv"
TK_CLADES_CSV = LEXIBANK_DIR / "tai_kadai_language_clades.csv"
TK_RICH_CACHE = LEXIBANK_DIR / "tai_kadai_attestation_rich.json"

PILOT_K = 50
PILOT_MIN_LANGS = 15
PILOT_PERMUTATIONS = 20
ATTESTED_PROMPT_VERSION = "v1"


def load_blust210_concepticon_ids(path: Path | None = None) -> set[str]:
    path = path or BLUST_210_TSV
    with path.open(newline="", encoding="utf-8") as handle:
        return {
            str(row["CONCEPTICON_ID"])
            for row in csv.DictReader(handle, delimiter="\t")
            if row.get("CONCEPTICON_ID")
        }

TK_SAMPLE_TARGET = 40
TK_CLADE_FLOORS = {
    "tai": 12,
    "kam_sui": 8,
    "kra": 4,
    "hlai": 4,
    "lakkia_biao": 1,
    "be": 1,
}
TK_CLADE_ORDER = ("kra", "kam_sui", "lakkia_biao", "be", "tai", "hlai", "other_tk")

SYSTEM_PROMPT = """You are comparing two bags of word-forms from unknown languages as raw phonological strings only.

Critical rules:
- Do NOT use, infer, or mention word meanings, glosses, translations, or language identity.
- Even if you recognize a form from training data, IGNORE that knowledge. Treat every string as an opaque phoneme sequence from a hypothetical language.
- Judge only how promising the sets look for *hypothetical cognacy* based on segmental shape: shared consonant/vowel skeletons, plausible correspondences, and especially shapes that recur widely in BOTH bags.
- Score higher when similar shapes appear to be widespread across multiple items in both bags; score lower when only a single isolated lookalike exists, or bags look unrelated.
- Ignore tone digits/superscripts when comparing shapes.

Return ONLY valid JSON (no markdown fences) as an array of objects with keys:
- comparison_id (string; echo input)
- generosity (integer 1-5; 5 = highly promising hypothetical cognacy on shape alone)
- shared_shape_notes (string; brief note on recurring shapes, or "none noted")
- reasoning (string; 1-3 sentences; do not mention meaning)
"""


def load_tk_clades(path: Path | None = None) -> dict[str, str]:
    path = path or TK_CLADES_CSV
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["language_id"]: row["clade"] for row in csv.DictReader(handle) if row.get("language_id")}


def _normalize_form(form: str) -> str:
    text = form.lower()
    text = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉0-9]+", "", text)
    text = re.sub(r"[.\-_/\\|]+", "", text)
    text = re.sub(r"\s+", "", text)
    return text


def looks_like_onomatopoeia(form: str) -> bool:
    """Heuristic filter for expressive / onomatopoeic shapes."""
    norm = _normalize_form(form)
    if not norm:
        return True
    # Very short after normalization
    if len(norm) <= 2:
        return True
    # Clear reduplication (cv-cv or cvc-cvc with repeat)
    if re.fullmatch(r"(.{2,4})\1", norm):
        return True
    if re.fullmatch(r"([^aeiou]{0,2}[aeiou]+)\1", norm):
        return True
    return False


def dedupe_forms(forms: list[dict[str, str]]) -> list[dict[str, str]]:
    """Keep one form per language, then one per normalized shape within clade."""
    by_lang: dict[str, dict[str, str]] = {}
    for item in forms:
        if looks_like_onomatopoeia(item.get("form") or ""):
            continue
        lang_id = item.get("language_id") or item.get("language") or ""
        if not lang_id or lang_id in by_lang:
            continue
        by_lang[lang_id] = item

    by_clade_shape: dict[tuple[str, str], dict[str, str]] = {}
    for item in by_lang.values():
        clade = item.get("clade") or "other"
        shape = _normalize_form(item.get("form") or "")
        if not shape:
            continue
        key = (clade, shape)
        if key not in by_clade_shape:
            by_clade_shape[key] = item
    return list(by_clade_shape.values())


def sample_tk_forms(
    forms: list[dict[str, str]],
    *,
    target: int = TK_SAMPLE_TARGET,
    floors: dict[str, int] | None = None,
    seed: int = AN_SAMPLE_SEED,
) -> list[dict[str, str]]:
    floors = dict(floors or TK_CLADE_FLOORS)
    rng = random.Random(seed)
    pool = dedupe_forms(forms)
    by_clade: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in pool:
        by_clade[item.get("clade") or "other_tk"].append(item)
    for clade in by_clade:
        rng.shuffle(by_clade[clade])

    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()

    def take(clade: str, n: int) -> None:
        bucket = by_clade.get(clade) or []
        while n > 0 and bucket:
            item = bucket.pop()
            lang_id = item.get("language_id") or ""
            if lang_id in selected_ids:
                continue
            selected.append(item)
            selected_ids.add(lang_id)
            n -= 1

    for clade in TK_CLADE_ORDER:
        take(clade, floors.get(clade, 0))
    while len(selected) < target:
        progressed = False
        for clade in TK_CLADE_ORDER:
            if len(selected) >= target:
                break
            before = len(selected)
            take(clade, 1)
            if len(selected) > before:
                progressed = True
        if not progressed:
            break
    return selected


def sample_an_forms_for_pilot(forms: list[dict[str, str]], *, seed: int = AN_SAMPLE_SEED) -> list[dict[str, str]]:
    cleaned = dedupe_forms(forms)
    return sample_austronesian_forms(cleaned, seed=seed)


def build_rich_tk_attestation(force: bool = False) -> dict[str, dict[str, object]]:
    from .lexibank_check import download_lexibank

    download_lexibank(force=force)
    forms_zip = LEXIBANK_DIR / "forms.csv.zip"
    if (
        TK_RICH_CACHE.exists()
        and not force
        and TK_RICH_CACHE.stat().st_mtime >= forms_zip.stat().st_mtime
    ):
        return json.loads(TK_RICH_CACHE.read_text(encoding="utf-8"))

    languages = pd.read_csv(LEXIBANK_DIR / "languages.csv")
    tk_ids = set(languages.loc[languages["Family"] == "Tai-Kadai", "ID"].astype(str))
    language_names = dict(zip(languages["ID"].astype(str), languages["Name"].astype(str)))
    clades = load_tk_clades()

    counts: dict[str, set[str]] = defaultdict(set)
    forms_by_concept: dict[str, list[dict[str, str]]] = defaultdict(list)
    print("Scanning Lexibank forms for rich Tai-Kadai attestation ...")
    with zipfile.ZipFile(forms_zip) as archive:
        with archive.open("forms.csv") as raw:
            for row in csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8")):
                language_id = str(row["Language_ID"])
                if language_id not in tk_ids:
                    continue
                concept_id = str(row["Parameter_ID"])
                form = str(row.get("Form") or row.get("Value") or "").strip()
                if not form:
                    continue
                counts[concept_id].add(language_id)
                forms_by_concept[concept_id].append(
                    {
                        "language_id": language_id,
                        "language": language_names.get(language_id, language_id),
                        "form": form,
                        "clade": clades.get(language_id, "other_tk"),
                    }
                )
    cache = {
        cid: {"count": len(langs), "forms": forms_by_concept.get(cid, [])}
        for cid, langs in counts.items()
    }
    TK_RICH_CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    print(f"Cached rich TK attestation for {len(cache)} concepts -> {TK_RICH_CACHE}")
    return cache


def build_core_concepts(
    *,
    k: int = PILOT_K,
    min_langs: int = PILOT_MIN_LANGS,
    force: bool = False,
    list_filter: str | None = None,
    output_path: Path | None = None,
) -> list[dict[str, object]]:
    ATTESTED_DIR.mkdir(parents=True, exist_ok=True)
    tk_att = build_rich_tk_attestation(force=force)
    if not LEXIBANK_AN_ATTESTATION_CACHE.exists():
        from .lexibank_check import _load_austronesian_attestation

        _load_austronesian_attestation(force=force)
    an_att = json.loads(LEXIBANK_AN_ATTESTATION_CACHE.read_text(encoding="utf-8"))
    concepts = pd.read_csv(LEXIBANK_DIR / "concepts.csv")
    meta = {
        str(r["ID"]): {
            "name": str(r.get("Name") or ""),
            "concepticon_gloss": str(r.get("Concepticon_Gloss") or ""),
            "concepticon_id": str(r.get("Concepticon_ID") or ""),
        }
        for _, r in concepts.iterrows()
    }

    allowed_ids: set[str] | None = None
    if list_filter in {"blust", "blust210"}:
        allowed_ids = load_blust210_concepticon_ids()
    elif list_filter:
        raise ValueError(f"Unknown list_filter: {list_filter}")

    rows: list[dict[str, object]] = []
    for cid in set(tk_att) & set(an_att):
        n_tk = int(tk_att[cid].get("count") or 0)
        n_an = int(an_att[cid].get("count") or 0)
        if n_tk < min_langs or n_an < min_langs:
            continue
        info = meta.get(cid, {})
        conc_id = str(info.get("concepticon_id") or "")
        if allowed_ids is not None and conc_id not in allowed_ids:
            continue
        rows.append(
            {
                "concept_id": cid,
                "name": info.get("name") or cid,
                "concepticon_gloss": info.get("concepticon_gloss") or "",
                "concepticon_id": conc_id,
                "n_tk": n_tk,
                "n_an": n_an,
                "min_langs": min(n_tk, n_an),
            }
        )
    rows.sort(key=lambda r: (-int(r["min_langs"]), -int(r["n_tk"]), -int(r["n_an"]), str(r["concept_id"])))
    for index, row in enumerate(rows):
        row["rank"] = index + 1
        row["core_pilot"] = int(index < k)

    out = output_path or CORE_CONCEPTS_TSV
    if list_filter in {"blust", "blust210"} and output_path is None:
        out = ATTESTED_DIR / "core_concepts_blust.tsv"
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "concept_id",
                "name",
                "concepticon_gloss",
                "concepticon_id",
                "n_tk",
                "n_an",
                "min_langs",
                "core_pilot",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    core = [r for r in rows if r["core_pilot"] == 1]
    filt = f" filter={list_filter}" if list_filter else ""
    print(f"Wrote {len(rows)} dual-attested concepts{filt}; pilot core={len(core)} -> {out}")
    return core


def read_core_concepts(
    pilot_only: bool = True,
    path: Path | None = None,
) -> list[dict[str, str]]:
    path = path or CORE_CONCEPTS_TSV
    if not path.exists():
        build_core_concepts()
        path = CORE_CONCEPTS_TSV
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if pilot_only:
        rows = [r for r in rows if r.get("core_pilot") == "1"]
    return rows


@dataclass
class SetJudgment:
    comparison_id: str
    concept_id: str
    generosity: int
    shared_shape_notes: str
    reasoning: str
    n_tk_forms: int
    n_an_forms: int
    permutation_id: int

    def to_row(self) -> dict[str, object]:
        return {
            "comparison_id": self.comparison_id,
            "concept_id": self.concept_id,
            "generosity": self.generosity,
            "shared_shape_notes": self.shared_shape_notes,
            "reasoning": self.reasoning,
            "n_tk_forms": self.n_tk_forms,
            "n_an_forms": self.n_an_forms,
            "permutation_id": self.permutation_id,
        }


def _cache_key(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _forms_payload(forms: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {"clade": f.get("clade") or "", "form": f.get("form") or ""}
        for f in forms
    ]


def judge_set_pair(
    *,
    comparison_id: str,
    concept_id: str,
    tk_forms: list[dict[str, str]],
    an_forms: list[dict[str, str]],
    permutation_id: int = 0,
    cache_path: Path | None = None,
    sleep_seconds: float = 0.4,
) -> SetJudgment:
    cache_path = cache_path or (CACHE_DIR / "attested_set_judgments.sqlite3")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
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
    key = _cache_key(key_payload)

    conn = sqlite3.connect(cache_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS set_judgments (
            cache_key TEXT PRIMARY KEY,
            prompt_version TEXT,
            response_json TEXT,
            created_at REAL
        )
        """
    )
    row = conn.execute("SELECT response_json FROM set_judgments WHERE cache_key = ?", (key,)).fetchone()
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
                print(f"Attested set-judge JSON failed attempt {attempt+1}/3: {exc}")
                time.sleep(sleep_seconds * (attempt + 1))
        if parsed is None:
            raise RuntimeError("Failed to parse attested set judgment") from last_error
        conn.execute(
            "INSERT OR REPLACE INTO set_judgments(cache_key, prompt_version, response_json, created_at) VALUES (?,?,?,?)",
            (key, ATTESTED_PROMPT_VERSION, json.dumps(parsed, ensure_ascii=False), time.time()),
        )
        conn.commit()
        if sleep_seconds:
            time.sleep(sleep_seconds)
    conn.close()

    by_id = {item.get("comparison_id"): item for item in parsed}
    item = by_id.get("set001") or (parsed[0] if parsed else None)
    if not item:
        raise ValueError("Missing set judgment in model output")
    return SetJudgment(
        comparison_id=comparison_id,
        concept_id=concept_id,
        generosity=int(item["generosity"]),
        shared_shape_notes=str(item.get("shared_shape_notes") or ""),
        reasoning=str(item.get("reasoning") or ""),
        n_tk_forms=len(tk_forms),
        n_an_forms=len(an_forms),
        permutation_id=permutation_id,
    )


def prepare_concept_samples(
    core: list[dict[str, str]] | None = None,
    *,
    force: bool = False,
    core_path: Path | None = None,
) -> list[dict[str, object]]:
    core = core or read_core_concepts(pilot_only=True, path=core_path)
    tk_att = build_rich_tk_attestation(force=force)
    an_att = json.loads(LEXIBANK_AN_ATTESTATION_CACHE.read_text(encoding="utf-8"))
    prepared = []
    for row in core:
        cid = row["concept_id"]
        tk_forms = sample_tk_forms(list((tk_att.get(cid) or {}).get("forms") or []))
        an_forms = sample_an_forms_for_pilot(list((an_att.get(cid) or {}).get("forms") or []))
        prepared.append(
            {
                "concept_id": cid,
                "name": row.get("name") or cid,
                "concepticon_gloss": row.get("concepticon_gloss") or "",
                "n_tk": int(row.get("n_tk") or 0),
                "n_an": int(row.get("n_an") or 0),
                "tk_forms": tk_forms,
                "an_forms": an_forms,
            }
        )
    return prepared


def run_observed_attested(
    *,
    force: bool = False,
    output_path: Path | None = None,
    core_path: Path | None = None,
) -> list[SetJudgment]:
    prepared = prepare_concept_samples(force=force, core_path=core_path)
    judgments: list[SetJudgment] = []
    print(f"Attested pilot observed: {len(prepared)} concepts ...")
    for index, item in enumerate(prepared, start=1):
        comparison_id = f"{index:03d}"
        judgment = judge_set_pair(
            comparison_id=comparison_id,
            concept_id=str(item["concept_id"]),
            tk_forms=list(item["tk_forms"]),
            an_forms=list(item["an_forms"]),
            permutation_id=0,
        )
        judgments.append(judgment)
        print(
            f"  {item['concept_id']}: generosity={judgment.generosity} "
            f"(tk={judgment.n_tk_forms}, an={judgment.n_an_forms})"
        )

    output_path = output_path or (OUTPUT_DIR / "attested_judgments_observed.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SetJudgment.__dataclass_fields__))
        writer.writeheader()
        for judgment in judgments:
            writer.writerow(judgment.to_row())
    print(f"Wrote {output_path}")
    return judgments


def _default_null_judgments_path(results_path: Path | None) -> Path:
    if results_path is not None:
        return results_path.with_name(
            results_path.name.replace("permutation_results", "judgments_null").replace(".json", ".csv")
        )
    return OUTPUT_DIR / "attested_judgments_null.csv"


def _null_fieldnames() -> list[str]:
    return list(SetJudgment.__dataclass_fields__) + ["an_source_concept_id"]


def _load_completed_null_perms(
    null_judgments_path: Path,
    *,
    expected_n_concepts: int,
) -> tuple[set[int], dict[int, dict[int, int]], list[dict[str, object]]]:
    """Return completed perm ids, per-perm hit counts, and existing rows."""
    if not null_judgments_path.exists():
        return set(), {}, []
    with null_judgments_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    by_perm: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        perm = int(row["permutation_id"])
        by_perm.setdefault(perm, []).append(dict(row))
    completed: set[int] = set()
    hit_counts: dict[int, dict[int, int]] = {}
    kept: list[dict[str, object]] = []
    for perm, perm_rows in sorted(by_perm.items()):
        if len(perm_rows) != expected_n_concepts:
            print(
                f"Resume: dropping incomplete perm {perm} "
                f"({len(perm_rows)}/{expected_n_concepts} rows)"
            )
            continue
        completed.add(perm)
        kept.extend(perm_rows)
        hit_counts[perm] = {
            t: sum(1 for r in perm_rows if int(r["generosity"]) >= t) for t in (2, 3, 4, 5)
        }
    return completed, hit_counts, kept


def _write_null_judgments(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = _null_fieldnames()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def _write_attested_result(
    path: Path,
    *,
    label: str,
    prepared: list[dict[str, object]],
    n_permutations: int,
    seed: int,
    thresholds: tuple[int, ...],
    observed_hits: dict[int, int],
    null_hits: dict[int, list[int]],
    null_judgments_path: Path,
    partial: bool,
) -> dict[str, object]:
    completed = len(next(iter(null_hits.values()), []))
    result: dict[str, object] = {
        "label": label,
        "partial": partial,
        "n_concepts": len(prepared),
        "concept_ids": [str(item["concept_id"]) for item in prepared],
        "min_langs": PILOT_MIN_LANGS,
        "n_permutations": n_permutations,
        "n_permutations_completed": completed,
        "seed": seed,
        "thresholds": list(thresholds),
        "observed_hits": observed_hits,
        "null_hits": null_hits,
        "null_hits_mean": {
            str(t): (sum(null_hits[t]) / len(null_hits[t]) if null_hits[t] else 0.0) for t in thresholds
        },
        "p_value_one_sided": {
            str(t): (
                (sum(1 for h in null_hits[t] if h >= observed_hits[t]) + 1) / (len(null_hits[t]) + 1)
                if null_hits[t]
                else None
            )
            for t in thresholds
        },
        "null_judgments_path": str(null_judgments_path),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def run_attested_permutation(
    *,
    n_permutations: int = PILOT_PERMUTATIONS,
    seed: int = 1,
    force: bool = False,
    skip_observed: bool = False,
    resume: bool = True,
    core_path: Path | None = None,
    observed_path: Path | None = None,
    results_path: Path | None = None,
    null_judgments_path: Path | None = None,
    label: str | None = None,
) -> dict[str, object]:
    prepared = prepare_concept_samples(force=force, core_path=core_path)
    observed_path = observed_path or (OUTPUT_DIR / "attested_judgments_observed.csv")
    results_path = results_path or (OUTPUT_DIR / "attested_permutation_results.json")
    null_judgments_path = null_judgments_path or _default_null_judgments_path(results_path)

    if skip_observed and observed_path.exists():
        with observed_path.open(newline="", encoding="utf-8") as handle:
            observed_rows = list(csv.DictReader(handle))
        observed = [
            SetJudgment(
                comparison_id=row["comparison_id"],
                concept_id=row["concept_id"],
                generosity=int(row["generosity"]),
                shared_shape_notes=row.get("shared_shape_notes") or "",
                reasoning=row.get("reasoning") or "",
                n_tk_forms=int(row.get("n_tk_forms") or 0),
                n_an_forms=int(row.get("n_an_forms") or 0),
                permutation_id=int(row.get("permutation_id") or 0),
            )
            for row in observed_rows
        ]
        # Align prepared to observed concept order if both exist
        by_id = {item["concept_id"]: item for item in prepared}
        ordered = [by_id[row["concept_id"]] for row in observed_rows if row["concept_id"] in by_id]
        if len(ordered) == len(observed_rows):
            prepared = ordered
        elif len(observed) != len(prepared):
            raise ValueError(
                f"Observed CSV has {len(observed)} rows but core has {len(prepared)} concepts; "
                "refuse --skip-observed mismatch"
            )
    else:
        observed = run_observed_attested(force=False, output_path=observed_path, core_path=core_path)

    # Include ≥2 so thresholds can be inspected without re-running; full null rows
    # (with reasoning) are also written for any post-hoc cut.
    thresholds = (2, 3, 4, 5)
    observed_hits = {t: sum(1 for j in observed if j.generosity >= t) for t in thresholds}

    completed_perms: set[int] = set()
    prior_hit_counts: dict[int, dict[int, int]] = {}
    null_rows: list[dict[str, object]] = []
    if resume:
        completed_perms, prior_hit_counts, null_rows = _load_completed_null_perms(
            null_judgments_path, expected_n_concepts=len(prepared)
        )
        if completed_perms:
            print(
                f"Resume: {len(completed_perms)} complete permutation(s) already on disk "
                f"-> {null_judgments_path}"
            )
    else:
        null_rows = []
        if null_judgments_path.exists():
            print(f"Starting fresh (resume=False); replacing {null_judgments_path}")

    rng = random.Random(seed)
    an_sets = [list(item["an_forms"]) for item in prepared]
    an_source_by_id = {id(forms): str(item["concept_id"]) for item, forms in zip(prepared, an_sets, strict=True)}
    null_hits = {t: [] for t in thresholds}

    # Replay RNG for any already-completed perms so later shuffles match a clean run.
    for perm_index in range(1, n_permutations + 1):
        shuffled = an_sets[:]
        rng.shuffle(shuffled)
        if shuffled == an_sets and len(shuffled) > 1:
            shuffled = an_sets[1:] + an_sets[:1]

        if perm_index in completed_perms:
            for t in thresholds:
                null_hits[t].append(prior_hit_counts[perm_index][t])
            print(
                f"Attested perm {perm_index}/{n_permutations}: "
                f"hits@4={prior_hit_counts[perm_index][4]} "
                f"( @2={prior_hit_counts[perm_index][2]} @3={prior_hit_counts[perm_index][3]} "
                f"@5={prior_hit_counts[perm_index][5]} ) [cached]"
            )
            continue

        hits = {t: 0 for t in thresholds}
        perm_rows: list[dict[str, object]] = []
        for index, (item, an_forms) in enumerate(zip(prepared, shuffled, strict=True), start=1):
            judgment = judge_set_pair(
                comparison_id=f"{index:03d}",
                concept_id=str(item["concept_id"]),
                tk_forms=list(item["tk_forms"]),
                an_forms=an_forms,
                permutation_id=perm_index,
            )
            for t in thresholds:
                if judgment.generosity >= t:
                    hits[t] += 1
            row = judgment.to_row()
            row["an_source_concept_id"] = an_source_by_id.get(id(an_forms), "")
            perm_rows.append(row)
        null_rows.extend(perm_rows)
        for t in thresholds:
            null_hits[t].append(hits[t])
        _write_null_judgments(null_judgments_path, null_rows)
        _write_attested_result(
            results_path,
            label=label or "",
            prepared=prepared,
            n_permutations=n_permutations,
            seed=seed,
            thresholds=thresholds,
            observed_hits=observed_hits,
            null_hits=null_hits,
            null_judgments_path=null_judgments_path,
            partial=len(null_hits[thresholds[0]]) < n_permutations,
        )
        print(
            f"Attested perm {perm_index}/{n_permutations}: "
            f"hits@4={hits[4]} ( @2={hits[2]} @3={hits[3]} @5={hits[5]} )"
        )

    result = _write_attested_result(
        results_path,
        label=label or "",
        prepared=prepared,
        n_permutations=n_permutations,
        seed=seed,
        thresholds=thresholds,
        observed_hits=observed_hits,
        null_hits=null_hits,
        null_judgments_path=null_judgments_path,
        partial=False,
    )
    _write_null_judgments(null_judgments_path, null_rows)
    print(json.dumps({k: result[k] for k in result if k not in {"null_hits", "concept_ids"}}, indent=2))
    print(f"Wrote {results_path}")
    print(f"Wrote {null_judgments_path} ({len(null_rows)} null judgments)")
    return result


def summarize_attested_from_null_csv(
    observed_path: Path,
    null_judgments_path: Path,
    thresholds: tuple[int, ...] = (2, 3, 4, 5),
) -> dict[str, object]:
    """Recompute hit counts and one-sided p-values from stored judgment CSVs."""
    with observed_path.open(newline="", encoding="utf-8") as handle:
        observed = list(csv.DictReader(handle))
    with null_judgments_path.open(newline="", encoding="utf-8") as handle:
        null_rows = list(csv.DictReader(handle))

    observed_hits = {t: sum(1 for r in observed if int(r["generosity"]) >= t) for t in thresholds}
    by_perm: dict[int, list[int]] = {}
    for row in null_rows:
        perm = int(row["permutation_id"])
        by_perm.setdefault(perm, []).append(int(row["generosity"]))
    null_hits = {
        t: [sum(1 for g in scores if g >= t) for _, scores in sorted(by_perm.items())] for t in thresholds
    }
    return {
        "n_concepts": len(observed),
        "n_permutations": len(by_perm),
        "thresholds": list(thresholds),
        "observed_hits": observed_hits,
        "null_hits": null_hits,
        "null_hits_mean": {
            str(t): (sum(null_hits[t]) / len(null_hits[t]) if null_hits[t] else 0.0) for t in thresholds
        },
        "p_value_one_sided": {
            str(t): (sum(1 for h in null_hits[t] if h >= observed_hits[t]) + 1) / (len(null_hits[t]) + 1)
            for t in thresholds
        },
    }