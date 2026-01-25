from pronunciation_score.metrics import duration_score, phoneme_base_score
from pronunciation_score.gop import gop_score
from pronunciation_score.syllables import syllabify


from pronunciation_score.phoneme_map import map_ipa


def score_word(word_block):
    phone_scores = {}
    total = 0

    for p in word_block["phones"]:
        score = int(
            0.5 * gop_score(p) +
            0.3 * duration_score(p) +
            0.2 * phoneme_base_score(p)
        )
        phone_scores[p["text"]] = score
        total += score

    avg = int(total / len(phone_scores)) if phone_scores else 0

    syllables = syllabify(word_block["phones"])
    syllable_score = avg if syllables else 0

    return {
        "word": word_block["word"],
        "phoneme_scores": phone_scores,
        "syllable_score": syllable_score,
        "word_score": avg
    }


def score_all(words_with_phones):
    results = []
    overall = 0

    for w in words_with_phones:
        r = score_word(w)
        results.append(r)
        overall += r["word_score"]

    overall_score = int(overall / len(results)) if results else 0

    return {
        "words": results,
        "overall_score": overall_score
    }



def score_alignment(alignment, frames):
    results = []

    for p in alignment:
        ipa = p["phoneme"]
        mapped = map_ipa(ipa)
        if not mapped:
            continue

        segment_frames = [
            f for f in frames
            if p["start"] <= f["time"] <= p["end"]
        ]

        score = gop_score(segment_frames, mapped)

        results.append({
            "phoneme": ipa,
            "start": p["start"],
            "end": p["end"],
            "gop_score": score
        })

    overall = int(
        sum(r["gop_score"] for r in results) / len(results)
    ) if results else 0

    return {
        "phonemes": results,
        "overall_score": overall
    }