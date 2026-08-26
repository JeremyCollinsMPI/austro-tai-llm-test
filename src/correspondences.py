"""Exploratory sound-correspondence inventory over attested set-vs-set hits."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import time
from collections import defaultdict
from pathlib import Path

from .attested_pilot import ATTESTED_DIR, prepare_concept_samples, read_core_concepts
from .config import CACHE_DIR, OUTPUT_DIR
from .json_utils import extract_json_array
from .nlp_client import chat

CORR_PROMPT_VERSION = "v1"
CORR_DIR = OUTPUT_DIR / "correspondences"
NON_HIT_CONTROLS = ("bird", "ear", "blood", "dog", "star")

SYSTEM_PROMPT = """You are a comparative linguist building an *exploratory* inventory of possible
segmental sound correspondences between Tai-Kadai (TK) and Austronesian (AN) modern forms
for ONE Concepticon meaning.

Goal: propose recurring TK↔AN segment mappings supported by multiple forms in the samples,
not a full reconstruction or proof of cognacy.

Rules:
- Meanings ARE allowed here (this is a follow-up to a meaning-blind screen).
- Prefer mappings that recur across several languages/clades on both sides.
- Ignore tone digits/superscripts when comparing shape.
- Flag nursery/deixis/pronoun caveats when relevant.
- Do NOT invent proto-forms; stick to observed modern strings.
- Be concise. This is exploratory, not a correspondence proof.

Return ONLY valid JSON (no markdown fences) as an array with ONE object:
{
  "concept_id": string,
  "gloss": string,
  "tk_dominant_shapes": string (semicolon-separated short templates),
  "an_dominant_shapes": string,
  "proposed_mappings": [
    {
      "tk_segment": string,
      "an_segment": string,
      "context": string (e.g. "onset", "coda", "CVC skeleton"),
      "support": string (brief form examples from both sides),
      "confidence": integer 1-5
    }
  ],
  "caveats": string,
  "summary": string (2-4 sentences)
}
"""


def _cache_key(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _forms_brief(forms: list[dict[str, str]], *, limit: int = 35) -> list[dict[str, str]]:
    out = []
    for item in forms[:limit]:
        out.append({"clade": item.get("clade") or "", "form": item.get("form") or ""})
    return out


def analyze_concept_correspondences(
    *,
    concept_id: str,
    gloss: str,
    generosity: int,
    tk_forms: list[dict[str, str]],
    an_forms: list[dict[str, str]],
    cache_path: Path | None = None,
    sleep_seconds: float = 0.35,
) -> dict[str, object]:
    cache_path = cache_path or (CACHE_DIR / "correspondence_analyses.sqlite3")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    user_payload = {
        "concept_id": concept_id,
        "gloss": gloss,
        "generosity_from_blind_screen": generosity,
        "tk_forms": _forms_brief(tk_forms),
        "an_forms": _forms_brief(an_forms),
    }
    user_prompt = (
        "Propose exploratory TK↔AN segmental mappings for this concept from the form samples.\n\n"
        + json.dumps(user_payload, ensure_ascii=False, indent=2)
    )
    key_payload = {
        "prompt_version": CORR_PROMPT_VERSION,
        "system": SYSTEM_PROMPT,
        "user": user_prompt,
    }
    key = _cache_key(key_payload)

    conn = sqlite3.connect(cache_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS correspondence_analyses (
            cache_key TEXT PRIMARY KEY,
            prompt_version TEXT,
            response_json TEXT,
            created_at REAL
        )
        """
    )
    row = conn.execute(
        "SELECT response_json FROM correspondence_analyses WHERE cache_key = ?", (key,)
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
                print(f"Correspondence JSON failed {concept_id} attempt {attempt+1}/3: {exc}")
                time.sleep(sleep_seconds * (attempt + 1))
        if parsed is None:
            conn.close()
            raise RuntimeError(f"Failed to parse correspondence analysis for {concept_id}") from last_error
        conn.execute(
            "INSERT OR REPLACE INTO correspondence_analyses"
            "(cache_key, prompt_version, response_json, created_at) VALUES (?,?,?,?)",
            (key, CORR_PROMPT_VERSION, json.dumps(parsed, ensure_ascii=False), time.time()),
        )
        conn.commit()
        if sleep_seconds:
            time.sleep(sleep_seconds)
    conn.close()

    item = parsed[0] if isinstance(parsed, list) and parsed else parsed
    if not isinstance(item, dict):
        raise ValueError(f"Unexpected correspondence payload for {concept_id}")
    item["concept_id"] = concept_id
    item["gloss"] = gloss or str(item.get("gloss") or concept_id)
    item["generosity"] = generosity
    return item


def load_observed_by_concept(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["concept_id"]: row for row in csv.DictReader(handle)}


def run_correspondence_analysis(
    *,
    min_generosity: int = 2,
    observed_path: Path | None = None,
    core_path: Path | None = None,
    include_nonhit_controls: bool = True,
    label: str = "blust194",
) -> dict[str, object]:
    observed_path = observed_path or (OUTPUT_DIR / "attested_judgments_observed_blust194.csv")
    core_path = core_path or (ATTESTED_DIR / "core_concepts_blust.tsv")
    observed = load_observed_by_concept(observed_path)
    core_rows = read_core_concepts(pilot_only=True, path=core_path)
    prepared = prepare_concept_samples(core=core_rows, core_path=core_path)
    by_id = {str(item["concept_id"]): item for item in prepared}

    targets: list[tuple[str, int, bool]] = []
    for cid, row in observed.items():
        gen = int(row["generosity"])
        if gen >= min_generosity:
            targets.append((cid, gen, False))
    if include_nonhit_controls:
        for cid in NON_HIT_CONTROLS:
            if cid in observed and int(observed[cid]["generosity"]) < min_generosity:
                targets.append((cid, int(observed[cid]["generosity"]), True))

    # Stable order: higher generosity first, then concept id
    targets.sort(key=lambda t: (-t[1], t[0]))

    CORR_DIR.mkdir(parents=True, exist_ok=True)
    analyses: list[dict[str, object]] = []
    print(f"Correspondence analysis: {len(targets)} concepts (min_generosity>={min_generosity}) ...")
    for index, (cid, gen, is_control) in enumerate(targets, start=1):
        item = by_id.get(cid)
        if not item:
            print(f"  skip {cid}: not in prepared core")
            continue
        gloss = str(item.get("concepticon_gloss") or item.get("name") or cid)
        print(f"  [{index}/{len(targets)}] {cid} gen={gen}{' [control]' if is_control else ''}")
        result = analyze_concept_correspondences(
            concept_id=cid,
            gloss=gloss,
            generosity=gen,
            tk_forms=list(item["tk_forms"]),
            an_forms=list(item["an_forms"]),
        )
        result["is_nonhit_control"] = is_control
        analyses.append(result)

    raw_path = CORR_DIR / f"analyses_{label}_ge{min_generosity}.json"
    raw_path.write_text(json.dumps(analyses, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {raw_path}")

    mapping_rows = _flatten_mappings(analyses)
    map_path = CORR_DIR / f"mappings_{label}_ge{min_generosity}.csv"
    with map_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "concept_id",
            "gloss",
            "generosity",
            "is_nonhit_control",
            "tk_segment",
            "an_segment",
            "context",
            "support",
            "confidence",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in mapping_rows:
            writer.writerow(row)
    print(f"Wrote {map_path} ({len(mapping_rows)} mapping rows)")

    # Tiered exploratory reports (label in filename so runs don't overwrite each other)
    for thr in (4, 3, 2):
        if thr < min_generosity:
            continue
        report_path = CORR_DIR / f"correspondences_{label}_ge{thr}.md"
        report_path.write_text(
            _render_report(analyses, mapping_rows, threshold=thr, label=label),
            encoding="utf-8",
        )
        print(f"Wrote {report_path}")
    # Keep unlabelled aliases for the historical blust194 run only
    if label == "blust194":
        for thr in (4, 3, 2):
            if thr < min_generosity:
                continue
            src = CORR_DIR / f"correspondences_{label}_ge{thr}.md"
            dst = CORR_DIR / f"correspondences_ge{thr}.md"
            if src.exists():
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    summary = {
        "label": label,
        "min_generosity": min_generosity,
        "n_analyses": len(analyses),
        "n_mappings": len(mapping_rows),
        "raw_path": str(raw_path),
        "mappings_path": str(map_path),
    }
    (CORR_DIR / f"summary_{label}_ge{min_generosity}.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def _flatten_mappings(analyses: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for item in analyses:
        mappings = item.get("proposed_mappings") or []
        if not isinstance(mappings, list):
            continue
        for m in mappings:
            if not isinstance(m, dict):
                continue
            rows.append(
                {
                    "concept_id": item.get("concept_id"),
                    "gloss": item.get("gloss"),
                    "generosity": item.get("generosity"),
                    "is_nonhit_control": int(bool(item.get("is_nonhit_control"))),
                    "tk_segment": m.get("tk_segment") or "",
                    "an_segment": m.get("an_segment") or "",
                    "context": m.get("context") or "",
                    "support": m.get("support") or "",
                    "confidence": m.get("confidence") or "",
                }
            )
    return rows


def _normalize_seg(text: str) -> str:
    return " ".join(str(text or "").lower().split())


def _render_report(
    analyses: list[dict[str, object]],
    mapping_rows: list[dict[str, object]],
    *,
    threshold: int,
    label: str,
) -> str:
    hit_analyses = [
        a
        for a in analyses
        if not a.get("is_nonhit_control") and int(a.get("generosity") or 0) >= threshold
    ]
    controls = [a for a in analyses if a.get("is_nonhit_control")]
    hit_ids = {str(a["concept_id"]) for a in hit_analyses}

    # Recurrence among hit concepts only
    cell_concepts: dict[tuple[str, str], set[str]] = defaultdict(set)
    cell_rows: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in mapping_rows:
        if int(row.get("is_nonhit_control") or 0):
            continue
        if str(row["concept_id"]) not in hit_ids:
            continue
        key = (_normalize_seg(str(row["tk_segment"])), _normalize_seg(str(row["an_segment"])))
        if not key[0] or not key[1]:
            continue
        cell_concepts[key].add(str(row["concept_id"]))
        cell_rows[key].append(row)

    recurring = sorted(
        ((k, sorted(v)) for k, v in cell_concepts.items() if len(v) >= 2),
        key=lambda kv: (-len(kv[1]), kv[0][0], kv[0][1]),
    )

    lines = [
        f"# Exploratory TK↔AN correspondences (generosity ≥ {threshold})",
        "",
        f"Label: `{label}`. Follow-up to meaning-blind attested set-vs-set hits. "
        "**Not** a proof of regular sound laws—an inventory of LLM-proposed mappings "
        "for human inspection.",
        "",
        f"- Concepts in this tier: **{len(hit_analyses)}**",
        f"- Mapping rows from these concepts: "
        f"**{sum(1 for r in mapping_rows if str(r['concept_id']) in hit_ids and not int(r.get('is_nonhit_control') or 0))}**",
        f"- Mapping cells recurring in ≥2 concepts: **{len(recurring)}**",
        "",
        "## Recurring mapping cells (≥2 concepts)",
        "",
    ]
    if not recurring:
        lines.append("_None with ≥2 supporting concepts in this tier._")
        lines.append("")
    else:
        lines.append("| TK | AN | n concepts | concepts |")
        lines.append("|----|----|----------:|----------|")
        for (tk, an), concepts in recurring[:40]:
            lines.append(f"| `{tk}` | `{an}` | {len(concepts)} | {', '.join(concepts)} |")
        lines.append("")

    lines.extend(["## Per-concept summaries", ""])
    for item in sorted(hit_analyses, key=lambda a: (-int(a.get("generosity") or 0), str(a["concept_id"]))):
        lines.append(f"### {item.get('gloss') or item['concept_id']} (`{item['concept_id']}`, gen={item.get('generosity')})")
        lines.append("")
        lines.append(f"- TK shapes: {item.get('tk_dominant_shapes') or '—'}")
        lines.append(f"- AN shapes: {item.get('an_dominant_shapes') or '—'}")
        lines.append(f"- Caveats: {item.get('caveats') or '—'}")
        lines.append(f"- Summary: {item.get('summary') or '—'}")
        lines.append("")
        mappings = item.get("proposed_mappings") or []
        if isinstance(mappings, list) and mappings:
            lines.append("| TK | AN | context | conf | support |")
            lines.append("|----|----|---------|-----:|---------|")
            for m in mappings:
                if not isinstance(m, dict):
                    continue
                lines.append(
                    f"| `{m.get('tk_segment','')}` | `{m.get('an_segment','')}` | "
                    f"{m.get('context','')} | {m.get('confidence','')} | "
                    f"{(m.get('support') or '')[:120]} |"
                )
            lines.append("")

    if threshold >= 4 and controls:
        lines.extend(["## Non-hit controls (qualitative)", ""])
        lines.append(
            "Same prompt on concepts that scored below the blind-screen threshold "
            f"(controls: {', '.join(NON_HIT_CONTROLS)})."
        )
        lines.append("")
        for item in controls:
            lines.append(
                f"### {item.get('gloss') or item['concept_id']} "
                f"(`{item['concept_id']}`, gen={item.get('generosity')})"
            )
            lines.append("")
            lines.append(f"- Summary: {item.get('summary') or '—'}")
            lines.append(f"- Caveats: {item.get('caveats') or '—'}")
            nmap = len(item.get("proposed_mappings") or [])
            lines.append(f"- Proposed mappings: {nmap}")
            lines.append("")

    lines.extend(
        [
            "## Files",
            "",
            f"- Raw analyses: `output/correspondences/analyses_{label}_ge{{min}}.json`",
            f"- Flat mappings CSV: `output/correspondences/mappings_{label}_ge{{min}}.csv`",
            "",
        ]
    )
    return "\n".join(lines) + "\n"
