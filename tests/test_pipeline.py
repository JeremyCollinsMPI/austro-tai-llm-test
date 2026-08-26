#!/usr/bin/env python3
from __future__ import annotations

import random

import pytest

from src.gloss_concepts import GLOSS_TO_LEXIBANK_CONCEPT
from src.json_utils import extract_json_array
from src.judge import _build_user_prompt, summarize_judgments, Judgment, PairRequest
from src.lexibank_check import (
    _load_concept_records,
    _load_lexibank_attestation,
    match_concept,
    has_coverage_gap,
    audit_attestation,
)
from src.parse_smith import build_aligned_pairs, read_aligned_pairs
from src.permute import permute_pan_values


def test_all_glosses_have_explicit_mapping():
    pairs = build_aligned_pairs()
    for pair in pairs:
        assert pair.gloss in GLOSS_TO_LEXIBANK_CONCEPT, f"Missing gloss mapping: {pair.gloss}"


def test_blow_maps_to_wind_not_low():
    records = _load_concept_records()
    concept = match_concept("blow", records)
    assert concept is not None
    assert concept.concept_id == "blowofwind"
    assert concept.concepticon_gloss == "BLOW (OF WIND)"


def test_boat_maps_and_has_attestation():
    records = _load_concept_records()
    concept = match_concept("boat", records)
    assert concept is not None
    assert concept.concept_id == "boat"


def test_hungry_maps_to_behungry():
    records = _load_concept_records()
    concept = match_concept("hungry", records)
    assert concept is not None
    assert concept.concept_id == "behungry"


def test_judge_prompt_is_meaning_blind():
    pairs = build_aligned_pairs()[:3]
    prompt, _ = _build_user_prompt(pairs)
    assert "gloss" not in prompt.lower()
    for pair in pairs:
        assert pair.gloss not in prompt
        assert pair.pair_id not in prompt
    assert "proto_austronesian" in prompt
    assert "proto_kra_dai" in prompt
    assert "do not use meaning" in prompt.lower()


def test_permute_changes_pan_assignment():
    pairs = build_aligned_pairs()[:10]
    rng = random.Random(1)
    shuffled = permute_pan_values(pairs, rng)
    assert shuffled != [p.pan for p in pairs]


def test_extract_json_array_strips_fences():
    text = """```json
[{"pair_id": "001", "generosity": 4, "plausible_sound_correspondences": "none", "reasoning": "ok"}]
```"""
    parsed = extract_json_array(text)
    assert parsed[0]["pair_id"] == "001"


def test_extract_json_array_allows_raw_newlines_in_strings():
    text = '[{"pair_id": "001", "reasoning": "line1\nline2", "generosity": 4}]'
    parsed = extract_json_array(text)
    assert parsed[0]["reasoning"] == "line1\nline2"


def test_extract_json_array_strips_trailing_commas():
    text = '[{"comparison_id": "001", "generosity": 4,},]'
    parsed = extract_json_array(text)
    assert parsed[0]["comparison_id"] == "001"
    assert parsed[0]["generosity"] == 4



def test_summarize_judgments():
    judgments = [
        Judgment("a", "water", "*daNum", "*nam", 5, "n~m", "good", True, 0, "b0"),
        Judgment("b", "fire", "*za", "*apuy", 2, "none", "weak", False, 0, "b0"),
    ]
    summary = summarize_judgments(judgments)
    assert summary["n_hits"] == 1
    assert summary["mean_generosity"] == 3.5


def test_bird_cache_includes_sanchong_kelao_when_uncapped():
    attestation, _ = _load_lexibank_attestation(force=False)
    forms = attestation.get("bird", {}).get("forms") or []
    assert any(
        f.get("language") == "Sanchong Kelao" and "ma" in str(f.get("form", "")).lower()
        for f in forms
    ), "Expected Sanchong Kelao ma…lo form among all bird forms"
    assert len(forms) >= 70


def test_coverage_gap_excludes_sparse_concepts():
    pairs = read_aligned_pairs()
    audits = audit_attestation(pairs, validation_scores={})
    shadow = next(a for a in audits if a.gloss == "shadow")
    if shadow.lexibank_tai_kadai_language_count < 3:
        assert shadow.coverage_gap
        assert not shadow.included_in_permutation_test


def test_score_one_pkd_excluded_from_tier_a_but_flagged_unjustified():
    pairs = read_aligned_pairs()
    scores = {
        "112_turtle": {"attestation_score": "1", "reasoning": "unsupported"},
        "004_ant": {"attestation_score": "5", "reasoning": "strong"},
    }
    audits = audit_attestation(pairs, validation_scores=scores)
    turtle = next(a for a in audits if a.pair_id == "112_turtle")
    ant = next(a for a in audits if a.pair_id == "004_ant")
    assert turtle.unjustified_pkd
    assert not turtle.included_in_permutation_test
    assert not ant.unjustified_pkd
    assert ant.included_in_permutation_test


def test_an_sample_is_stratified_and_capped():
    from collections import Counter

    from src.an_sampling import sample_austronesian_forms
    from src.lexibank_check import _load_austronesian_attestation

    an = _load_austronesian_attestation()
    forms = an.get("bird", {}).get("forms") or []
    assert len(forms) > 80
    sampled = sample_austronesian_forms(forms, target=80)
    assert len(sampled) <= 80
    counts = Counter(f["clade"] for f in sampled)
    assert counts.get("formosan", 0) >= 1
    assert counts.get("western_mp", 0) >= 1
    assert counts.get("oceanic", 0) >= 1
    # one form per language
    assert len({f["language_id"] for f in sampled}) == len(sampled)


def test_score_one_pan_excluded_from_tier_a():
    pairs = read_aligned_pairs()
    pan_scores = {
        "001_1sg": {"attestation_score": "1", "reasoning": "unsupported pan"},
        "004_ant": {"attestation_score": "5", "reasoning": "ok"},
    }
    pkd_scores = {
        "001_1sg": {"attestation_score": "5", "reasoning": "ok"},
        "004_ant": {"attestation_score": "5", "reasoning": "ok"},
    }
    audits = audit_attestation(pairs, validation_scores=pkd_scores, pan_validation_scores=pan_scores)
    one = next(a for a in audits if a.pair_id == "001_1sg")
    ant = next(a for a in audits if a.pair_id == "004_ant")
    assert one.unjustified_pan
    assert not one.included_in_permutation_test
    assert not ant.unjustified_pan
    assert ant.included_in_permutation_test


def test_onomatopoeia_and_dedupe_helpers():
    from src.attested_pilot import dedupe_forms, looks_like_onomatopoeia

    assert looks_like_onomatopoeia("ti")
    assert looks_like_onomatopoeia("baba")
    assert not looks_like_onomatopoeia("mata")
    forms = [
        {"language_id": "a", "clade": "tai", "form": "mata"},
        {"language_id": "b", "clade": "tai", "form": "mata"},
        {"language_id": "c", "clade": "tai", "form": "ti"},
    ]
    deduped = dedupe_forms(forms)
    assert len(deduped) == 1
    assert deduped[0]["form"] == "mata"


def test_summarize_attested_from_null_csv(tmp_path):
    from src.attested_pilot import summarize_attested_from_null_csv

    observed = tmp_path / "obs.csv"
    null = tmp_path / "null.csv"
    observed.write_text(
        "comparison_id,concept_id,generosity,shared_shape_notes,reasoning,"
        "n_tk_forms,n_an_forms,permutation_id\n"
        "001,eye,4,n,r,1,1,0\n"
        "002,ear,1,n,r,1,1,0\n",
        encoding="utf-8",
    )
    null.write_text(
        "comparison_id,concept_id,generosity,shared_shape_notes,reasoning,"
        "n_tk_forms,n_an_forms,permutation_id,an_source_concept_id\n"
        "001,eye,1,n,r,1,1,1,ear\n"
        "002,ear,2,n,r,1,1,1,eye\n"
        "001,eye,4,n,r,1,1,2,ear\n"
        "002,ear,1,n,r,1,1,2,eye\n",
        encoding="utf-8",
    )
    summary = summarize_attested_from_null_csv(observed, null, thresholds=(2, 4))
    assert summary["observed_hits"][2] == 1
    assert summary["observed_hits"][4] == 1
    assert summary["null_hits"][4] == [0, 1]
    assert summary["p_value_one_sided"]["4"] == pytest.approx(2 / 3)  # (1+1)/(2+1)
