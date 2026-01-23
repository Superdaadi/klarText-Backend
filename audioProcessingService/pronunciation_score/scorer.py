from pronunciation_score.metrics import duration_score, phoneme_base_score
from pronunciation_score.gop import gop_score
from pronunciation_score.syllables import syllabify


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
