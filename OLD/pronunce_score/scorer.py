def score_pronunciation(
    aligned_phonemes,
    gop_fn,
    duration_fn,
    phoneme_match_fn
):
    phoneme_scores = {}
    total = 0

    for user, ref in aligned_phonemes:
        gop = gop_fn(ref["ll"], ref["competitors"])
        dur = duration_fn(
            user["start"], user["end"],
            ref["start"], ref["end"]
        )
        match = phoneme_match_fn(
            user["phoneme"], ref["phoneme"]
        )

        score = int(0.5*gop + 0.3*dur + 0.2*match)
        phoneme_scores[ref["phoneme"]] = score
        total += score

    return {
        "phoneme_scores": phoneme_scores,
        "overall_score": int(total / len(phoneme_scores))
    }
