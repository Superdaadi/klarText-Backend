def fuse_scores(phoneme, duration, gop, weights=None):
    weights = weights or {
        "phoneme": 0.2,
        "duration": 0.3,
        "gop": 0.5
    }

    score = (
        phoneme * weights["phoneme"] +
        duration * weights["duration"] +
        gop * weights["gop"]
    )
    return int(score)
