from src.attested_pilot import ATTESTED_DIR, prepare_concept_samples, read_core_concepts

core = read_core_concepts(pilot_only=True, path=ATTESTED_DIR / "core_concepts_blust.tsv")
prep = prepare_concept_samples(core=core, core_path=ATTESTED_DIR / "core_concepts_blust.tsv")
by = {p["concept_id"]: p for p in prep}
for cid in ("mother", "this", "blowofwind"):
    p = by[cid]
    print("=" * 70)
    print(cid, "gloss=", p.get("concepticon_gloss"))
    print(f"--- TK sample (n={len(p['tk_forms'])}) ---")
    for f in p["tk_forms"]:
        print(f"  {f.get('clade', ''):12s}  {f.get('language', ''):22s}  {f.get('form')}")
    print(f"--- AN sample (n={len(p['an_forms'])}) ---")
    for f in p["an_forms"]:
        print(f"  {f.get('clade', ''):12s}  {f.get('language', ''):22s}  {f.get('form')}")
