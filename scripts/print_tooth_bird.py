from pathlib import Path

from src.attested_pilot import prepare_concept_samples, read_core_concepts

core_path = Path("data/attested_pilot/core_concepts_all373.tsv")
core = read_core_concepts(pilot_only=True, path=core_path)
prep = {
    p["concept_id"]: p
    for p in prepare_concept_samples(core=core, core_path=core_path)
}
for cid in ("tooth", "bird"):
    p = prep[cid]
    print("=" * 70)
    print(cid, "gloss=", p.get("concepticon_gloss"))
    print(f"--- TK (n={len(p['tk_forms'])}) ---")
    for f in p["tk_forms"]:
        print(f"  {f.get('clade', ''):12s}  {f.get('language', ''):24s}  {f.get('form')}")
    print(f"--- AN (n={len(p['an_forms'])}) ---")
    for f in p["an_forms"]:
        print(f"  {f.get('clade', ''):12s}  {f.get('language', ''):24s}  {f.get('form')}")
