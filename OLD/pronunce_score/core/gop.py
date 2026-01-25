def gop_score(ll_correct, ll_competitors, scale=5, offset=20):
    if not ll_competitors:
        return 0

    best_other = max(ll_competitors)
    gop = ll_correct - best_other

    score = int((gop + offset) * scale)
    return max(0, min(100, score))
