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
