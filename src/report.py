from __future__ import annotations

import csv
import json
from pathlib import Path

from .config import GENEROSITY_THRESHOLD, MIN_ATTESTATION_SCORE_FOR_PERMUTATION, OUTPUT_DIR


def _lexibank_attestation_line(audit: dict[str, str]) -> str:
    concept = audit.get("lexibank_concepticon_gloss") or audit.get("lexibank_concept_name") or "unmapped"
    return (
        f"- Lexibank Tai-Kadai attestation: **{audit.get('lexibank_tai_kadai_language_count')}** "
        f"languages for `{concept}`"
    )


def build_report(
    *,
    judgments_observed_path: Path | None = None,
    permutation_results_path: Path | None = None,
    attestation_audit_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    judgments_observed_path = judgments_observed_path or (OUTPUT_DIR / "judgments_observed.csv")
    permutation_results_path = permutation_results_path or (OUTPUT_DIR / "permutation_results.json")
    attestation_audit_path = attestation_audit_path or (OUTPUT_DIR / "lexibank_attestation_audit.csv")
    output_path = output_path or (OUTPUT_DIR / "report.md")

    judgments = list(csv.DictReader(judgments_observed_path.open(encoding="utf-8"))) if judgments_observed_path.exists() else []
    permutation = json.loads(permutation_results_path.read_text(encoding="utf-8")) if permutation_results_path.exists() else {}
    attestation = list(csv.DictReader(attestation_audit_path.open(encoding="utf-8"))) if attestation_audit_path.exists() else []

    attestation_by_id = {row["pair_id"]: row for row in attestation}
    hits = [row for row in judgments if int(row.get("is_hit") or 0) == 1]
    excluded_gap = [row for row in attestation if row.get("coverage_gap") == "1"]
    unjustified = [row for row in attestation if row.get("unjustified_pkd") == "1"]
    unjustified_pan = [row for row in attestation if row.get("unjustified_pan") == "1"]
    tier_a = [row for row in attestation if row.get("included_in_permutation_test") == "1"]

    lines = [
        "# Austro-Tai LLM cognate screen — report",
        "",
        "## Summary",
        "",
        f"- Tier A (permutation test): PKD and PAN `attestation_score` ≥ **{MIN_ATTESTATION_SCORE_FOR_PERMUTATION}**, "
        f"no Lexibank coverage gap — **{len(tier_a)}** pairs",
        f"- Pairs judged (Tier A): **{len(judgments)}**",
        f"- Generosity threshold for hit: **>={GENEROSITY_THRESHOLD}**",
        f"- Observed hits: **{len(hits)}** ({len(hits)/len(judgments):.1%})" if judgments else "- Observed hits: n/a",
        f"- Coverage-gap exclusions: **{len(excluded_gap)}**",
        f"- Unjustified PKDs (`attestation_score` = 1): **{len(unjustified)}** "
        "(reported below; excluded from permutation)",
        f"- Unjustified PANs (`pan_attestation_score` = 1): **{len(unjustified_pan)}** "
        "(reported below; excluded from permutation)",
    ]

    if permutation:
        perm_n = permutation.get("n_pairs")
        stale = perm_n is not None and judgments and int(perm_n) != len(judgments)
        if stale:
            lines.extend(
                [
                    f"- Permutation results on disk are **stale** (ran on {perm_n} pairs; Tier A now has {len(judgments)}). "
                    "Re-run `./run.sh permute` before interpreting the p-value.",
                ]
            )
        else:
            lines.extend(
                [
                    f"- Permutation null mean hits: **{permutation.get('null_hits_mean', 0):.2f}**",
                    f"- One-sided p-value: **{permutation.get('p_value_one_sided', 'n/a')}**",
                    f"- Permutations run: **{permutation.get('n_permutations', 'n/a')}**",
                ]
            )

    lines.extend(["", "## Observed hits (Tier A)", ""])
    if not hits:
        lines.append("No pairs met the generosity threshold.")
    for row in hits:
        audit = attestation_by_id.get(row["pair_id"], {})
        cherry = audit.get("cherry_pick_risk") == "1"
        lines.extend(
            [
                f"### {row['gloss']}",
                "",
                f"- PAN: `{row['pan']}`",
                f"- PKD: `{row['pkd']}`",
                f"- Generosity: **{row['generosity']}**",
                f"- Sound correspondences (LLM note): {row.get('plausible_sound_correspondences') or '—'}",
                f"- Reasoning: {row.get('reasoning') or '—'}",
            ]
        )
        if audit:
            lines.extend(
                [
                    f"- Branch attestation (Smith): **{audit.get('branch_attestation_count')}** ({audit.get('attested_branches') or 'none'})",
                    _lexibank_attestation_line(audit),
                ]
            )
            if audit.get("attestation_score"):
                lines.append(
                    f"- PKD vs attested forms (LLM): **{audit.get('attestation_score')}/5** — {audit.get('attestation_score_reasoning') or '—'}"
                )
            if audit.get("pan_attestation_score"):
                lines.append(
                    f"- PAN vs sampled AN forms (LLM): **{audit.get('pan_attestation_score')}/5** — {audit.get('pan_attestation_score_reasoning') or '—'}"
                )
            if audit.get("lexibank_austronesian_language_count"):
                lines.append(
                    f"- Lexibank Austronesian attestation: **{audit.get('lexibank_austronesian_language_count')}** languages"
                )
            lines.append(f"- Cherry-pick risk flag: **{'yes' if cherry else 'no'}**")
        lines.append("")

    lines.extend(["## Unjustified PKD reconstructions (`attestation_score` = 1)", ""])
    lines.append(
        "These Smith PKD forms are weakly or not supported by Lexibank Tai-Kadai daughters. "
        "They remain part of the published comparison set for descriptive purposes, but are "
        "**not** counted in the Austro-Tai permutation test (and their PAN forms are not "
        "used in the Tier A null shuffle)."
    )
    lines.append("")
    if not unjustified:
        lines.append("None.")
    else:
        for row in unjustified:
            gap_note = " (also a coverage gap)" if row.get("coverage_gap") == "1" else ""
            lines.extend(
                [
                    f"### {row['gloss']}{gap_note}",
                    "",
                    f"- PKD: `{row['pkd']}`",
                    f"- Attestation score: **{row.get('attestation_score')}/5**",
                    f"- Reasoning: {row.get('attestation_score_reasoning') or '—'}",
                    "",
                ]
            )

    lines.extend(["## Unjustified PAN reconstructions (`pan_attestation_score` = 1)", ""])
    lines.append(
        "These Smith PAN forms are weakly or not supported by a phylogenetically stratified "
        "Lexibank Austronesian sample (Formosan / Western MP / SHWNG / Oceanic floors). "
        "They are listed for descriptive purposes but excluded from the Tier A permutation."
    )
    lines.append("")
    if not unjustified_pan:
        lines.append("None.")
    else:
        for row in unjustified_pan:
            gap_note = " (also a coverage gap)" if row.get("coverage_gap") == "1" else ""
            lines.extend(
                [
                    f"### {row['gloss']}{gap_note}",
                    "",
                    f"- PAN attestation score: **{row.get('pan_attestation_score')}/5**",
                    f"- Reasoning: {row.get('pan_attestation_score_reasoning') or '—'}",
                    "",
                ]
            )

    lines.extend(["## Coverage-gap exclusions", ""])
    if not excluded_gap:
        lines.append("None.")
    else:
        for row in excluded_gap:
            concept = row.get("lexibank_concepticon_gloss") or row.get("lexibank_concept_name") or "unmapped"
            lines.append(
                f"- `{row['gloss']}` — TK langs={row.get('lexibank_tai_kadai_language_count')}, "
                f"AN langs={row.get('lexibank_austronesian_language_count')} ({concept})"
            )

    attested_perm_path = OUTPUT_DIR / "attested_permutation_results.json"
    attested_obs_path = OUTPUT_DIR / "attested_judgments_observed.csv"
    if attested_perm_path.exists() or attested_obs_path.exists():
        lines.extend(["", "## Attested set-vs-set pilot (no reconstructions)", ""])
        lines.append(
            "Follow-up screen on dual-attested Lexibank concepts (pilot **K=50**, ≥15 TK and AN languages). "
            "Meaning-blind set-vs-set scores after phylogenetic sampling + onomatopoeia/dedupe filters. "
            "Commands: `./run.sh attested-core`, `attested-judge`, `attested-permute`."
        )
        lines.append("")
        if attested_obs_path.exists():
            attested_obs = list(csv.DictReader(attested_obs_path.open(encoding="utf-8")))
            for thr in (3, 4, 5):
                n_hit = sum(1 for r in attested_obs if int(r.get("generosity") or 0) >= thr)
                lines.append(f"- Observed hits @≥{thr}: **{n_hit}** / {len(attested_obs)}")
        if attested_perm_path.exists():
            ap = json.loads(attested_perm_path.read_text(encoding="utf-8"))
            means = ap.get("null_hits_mean") or {}
            pvals = ap.get("p_value_one_sided") or {}
            lines.extend(
                [
                    f"- Permutations: **{ap.get('n_permutations')}** (seed={ap.get('seed')})",
                    f"- Null mean hits @≥3/4/5: **{means.get('3')}** / **{means.get('4')}** / **{means.get('5')}**",
                    f"- One-sided p @≥3/4/5: **{pvals.get('3')}** / **{pvals.get('4')}** / **{pvals.get('5')}**",
                ]
            )

    flagged = [
        row
        for row in attestation
        if row.get("cherry_pick_risk") == "1"
        and row.get("coverage_gap") != "1"
        and row.get("unjustified_pkd") != "1"
        and row.get("unjustified_pan") != "1"
        and row.get("included_in_permutation_test") == "1"
    ]
    lines.extend(["", "## Cherry-pick risk flags (Tier A)", ""])
    if not flagged:
        lines.append("None among Tier A pairs.")
    else:
        for row in flagged:
            concept = row.get("lexibank_concepticon_gloss") or row.get("lexibank_concept_name") or "unmapped"
            lines.append(
                f"- `{row['gloss']}` / PKD `{row['pkd']}` — branches={row.get('branch_attestation_count')}, "
                f"TK langs={row.get('lexibank_tai_kadai_language_count')}, "
                f"AN langs={row.get('lexibank_austronesian_language_count')} ({concept}), "
                f"PKD score={row.get('attestation_score') or 'n/a'}, "
                f"PAN score={row.get('pan_attestation_score') or 'n/a'}"
            )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote report to {output_path}")
    return output_path
