from pronunce_score.core.duration import duration_score

def test_equal_duration():
    assert duration_score(0, 1, 0, 1) == 100

def test_half_duration():
    assert duration_score(0, 0.5, 0, 1) == 50
