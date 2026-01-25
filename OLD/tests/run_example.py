from pronunce_score.core.gop import gop_score
from pronunce_score.core.duration import duration_score
from pronunce_score.scorer import score_pronunciation

def phoneme_match(a, b):
    return 100 if a == b else 50

aligned = [
    (
        {"phoneme": "ʃ", "start": 0.0, "end": 0.20},
        {
            "phoneme": "ʃ",
            "start": 0.0,
            "end": 0.20,
            "ll": -10.0,
            "competitors": [-20.0, -25.0]
        }
    ),
    (
        {"phoneme": "p", "start": 0.21, "end": 0.31},
        {
            "phoneme": "p",
            "start": 0.21,
            "end": 0.31,
            "ll": -12.0,
            "competitors": [-30.0]
        }
    )
]

result = score_pronunciation(
    aligned,
    gop_fn=gop_score,
    duration_fn=duration_score,
    phoneme_match_fn=phoneme_match
)

print(result)
