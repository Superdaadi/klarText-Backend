from core.fusion import fuse_scores

def test_fusion():
    score = fuse_scores(80, 70, 90)
    assert 80 < score < 90
