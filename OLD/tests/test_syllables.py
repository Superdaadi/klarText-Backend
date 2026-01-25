from pronunce_score.core.syllables import syllabify

def test_simple_word():
    result = syllabify(["ʃ", "a", "p", "ə"])
    assert result == [["ʃ", "a"], ["p", "ə"]]
