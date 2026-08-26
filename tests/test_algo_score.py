from src.algo_score import ned_distance, normalize_algo_form, sca_distance, set_distance


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
