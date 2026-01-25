def duration_score(phone):
    dur = phone["xmax"] - phone["xmin"]
    return min(100, int(dur * 300))  # grobe Normalisierung


def phoneme_base_score(phone):
    if phone["text"]:
        return 80
    return 0
