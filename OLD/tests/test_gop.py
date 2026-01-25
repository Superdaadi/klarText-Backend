from core.gop import gop_score

def test_perfect_gop():
    score = gop_score(-10.0, [-30.0, -25.0])
    assert score > 80

def test_bad_gop():
    score = gop_score(-40.0, [-20.0])
    assert score < 20

def test_no_competitors():
    assert gop_score(-10, []) == 0
