#!/usr/bin/env python3
"""Export sampled TK/AN forms for attested observed judgments (hits or all)."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from src.attested_pilot import prepare_concept_samples, read_core_concepts
from src.config import OUTPUT_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", type=Path, required=True)
    parser.add_argument("--observed", type=Path, required=True)
    parser.add_argument(
        "--min-generosity",
        type=int,
        default=3,
        help="Include concepts with generosity ≥ this (default 3). Use 1 for all.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for forms CSV + per-concept dumps (default beside observed)",
    )
    parser.add_argument("--label", default="all373")
    args = parser.parse_args()

    out_dir = args.output_dir or (OUTPUT_DIR / f"attested_forms_{args.label}")
    out_dir.mkdir(parents=True, exist_ok=True)

    with args.observed.open(newline="", encoding="utf-8") as handle:
        observed_rows = list(csv.DictReader(handle))
    by_gen = {r["concept_id"]: int(r["generosity"]) for r in observed_rows}
    notes = {r["concept_id"]: r.get("shared_shape_notes") or "" for r in observed_rows}
    reasoning = {r["concept_id"]: r.get("reasoning") or "" for r in observed_rows}

    core = read_core_concepts(pilot_only=True, path=args.core)
    prepared = prepare_concept_samples(core=core, core_path=args.core)

    flat_rows: list[dict[str, object]] = []
    hit_summaries: list[dict[str, object]] = []
    for item in prepared:
        cid = str(item["concept_id"])
        gen = by_gen.get(cid)
        if gen is None or gen < args.min_generosity:
            continue
        gloss = item.get("concepticon_gloss") or item.get("name") or cid
        hit_summaries.append(
            {
                "concept_id": cid,
                "gloss": gloss,
                "generosity": gen,
                "shared_shape_notes": notes.get(cid, ""),
                "reasoning": reasoning.get(cid, ""),
                "n_tk_forms": len(item["tk_forms"]),
                "n_an_forms": len(item["an_forms"]),
                "tk_forms": [f.get("form") for f in item["tk_forms"]],
                "an_forms": [f.get("form") for f in item["an_forms"]],
            }
        )
        for family, forms in (("tk", item["tk_forms"]), ("an", item["an_forms"])):
            for f in forms:
                flat_rows.append(
                    {
                        "concept_id": cid,
                        "gloss": gloss,
                        "generosity": gen,
                        "family": family,
                        "clade": f.get("clade") or "",
                        "language": f.get("language") or "",
                        "language_id": f.get("language_id") or "",
                        "form": f.get("form") or "",
                    }
                )

    flat_path = out_dir / f"sampled_forms_ge{args.min_generosity}.csv"
    with flat_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "concept_id",
            "gloss",
            "generosity",
            "family",
            "clade",
            "language",
            "language_id",
            "form",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(flat_rows)

    json_path = out_dir / f"hits_ge{args.min_generosity}.json"
    json_path.write_text(json.dumps(hit_summaries, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path = out_dir / f"hits_ge{args.min_generosity}.md"
    lines = [
        f"# Sampled forms for generosity ≥ {args.min_generosity} (`{args.label}`)",
        "",
        f"- Concepts: **{len(hit_summaries)}**",
        f"- Flat forms CSV: `{flat_path}`",
        "",
    ]
    for h in sorted(hit_summaries, key=lambda x: (-int(x["generosity"]), str(x["concept_id"]))):
        lines.extend(
            [
                f"## {h['gloss']} (`{h['concept_id']}`, gen={h['generosity']})",
                "",
                f"- Notes: {h['shared_shape_notes'] or '—'}",
                f"- Reasoning: {h['reasoning'] or '—'}",
                "",
                f"**TK** ({h['n_tk_forms']}): " + ", ".join(str(x) for x in h["tk_forms"]),
                "",
                f"**AN** ({h['n_an_forms']}): " + ", ".join(str(x) for x in h["an_forms"]),
                "",
            ]
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")

    # Score distribution over full observed file
    from collections import Counter

    dist = Counter(int(r["generosity"]) for r in observed_rows)
    print(f"Observed score distribution: {dict(sorted(dist.items()))}")
    for t in (2, 3, 4, 5):
        n = sum(1 for g in by_gen.values() if g >= t)
        print(f"  hits @{t}: {n}")
    print(f"Wrote {flat_path} ({len(flat_rows)} form rows)")
    print(f"Wrote {json_path} ({len(hit_summaries)} concepts)")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
