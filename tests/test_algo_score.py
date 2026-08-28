from src.algo_score import (
    an_group_length_band,
    form_length,
    ned_distance,
    normalize_algo_form,
    pan_length_band,
    permute_within_bands,
    sca_distance,
    set_distance,
)


def test_normalize_strips_tones_stars_and_slashes():
    assert normalize_algo_form("*aku") == "aku"
    assert "1" not in normalize_algo_form("ba1n")
    assert "/" not in normalize_algo_form("(m/p-)aCay")
    assert "(" not in normalize_algo_form("(m/p-)aCay")


def test_identical_forms_zero_distance():
    assert sca_distance("*aku", "*aku") == 0.0
    assert ned_distance("*aku", "*aku") == 0.0


def test_set_distance_mean_of_best():
    tk = ["mata", "xxxxxx"]
    an = ["da", "mata"]
    d = set_distance(tk, an, metric="ned")
    assert 0.0 <= d < 1.0


def test_permute_within_bands_preserves_bands():
    import random

    values = ["a", "b", "c", "d", "e"]
    bands = ["x", "x", "y", "y", "z"]
    rng = random.Random(0)
    out = permute_within_bands(values, bands, rng)
    assert sorted(out[i] for i in range(2)) == sorted(values[:2])
    assert sorted(out[i] for i in range(2, 4)) == sorted(values[2:4])
    assert out[4] == "e"


def test_length_band_helpers():
    assert pan_length_band(3) == "le3"
    assert pan_length_band(5) == "5"
    assert pan_length_band(12) == "10to19"
    assert an_group_length_band(5.4) == "5"
    assert form_length("*aku") == 3
