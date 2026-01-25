from collections import defaultdict

def load_ctm(path):
    """
    Erwartetes CTM-Format:
    utt channel start duration phoneme loglikelihood
    """
    segments = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            utt, ch, start, dur, phoneme, ll = line.strip().split()
            start = float(start)
            dur = float(dur)
            ll = float(ll)

            segments.append({
                "phoneme": phoneme,
                "start": start,
                "end": start + dur,
                "ll": ll,
                # Platzhalter – echte GOP nutzt alle Alternativen
                "competitors": []
            })

    return segments


def attach_competitors(segments, competitor_map):
    """
    competitor_map = {
        index: [ll1, ll2, ...]
    }
    """
    for idx, seg in enumerate(segments):
        seg["competitors"] = competitor_map.get(idx, [])
    return segments
