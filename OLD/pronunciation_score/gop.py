'''
def gop_score(phone):
    """
    Ersatz-GOP:
    längere, stabile Phones → besser
    """
    dur = phone["xmax"] - phone["xmin"]

    if dur < 0.03:
        return 40
    if dur < 0.06:
        return 65
    if dur < 0.12:
        return 85
    return 95
'''


def gop_score(frames, target_phoneme):
    values = []

    for f in frames:
        if target_phoneme not in f["log_probs"]:
            continue

        target = f["log_probs"][target_phoneme]
        competitors = [
            v for k, v in f["log_probs"].items()
            if k != target_phoneme
        ]

        if not competitors:
            continue

        values.append(target - max(competitors))

    if not values:
        return 0

    gop = sum(values) / len(values)

    # Normalisierung auf 0–100
    return max(0, min(100, int((gop + 5) * 10)))

