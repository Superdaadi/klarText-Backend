import json
from pronunciation_score.alignment import phones_to_words
from pronunciation_score.scorer import score_all
from pronunciation_score.posterior_extractor import extract_posteriors
from pronunciation_score.scorer import score_alignment

INPUT_PATH = "pronunciation_score/input/textgrid.json"


ALIGNMENT_JSON = "pronunciation_score/input/textgrid.json"
AUDIO_PATH = "audio_input/test.wav"


def main():
    with open(ALIGNMENT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    phonemes = [
        {
            "phoneme": p["text"],
            "start": p["xmin"],
            "end": p["xmax"]
        }
        for p in data["phones"]
        if p["text"]
    ]

    frames = extract_posteriors(AUDIO_PATH)
    result = score_alignment(phonemes, frames)

    print(json.dumps(result, indent=2, ensure_ascii=False))



"""
def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    words = data["words"]
    phones = data["phones"]

    words_with_phones = phones_to_words(words, phones)
    result = score_all(words_with_phones)

    print(json.dumps(result, indent=2, ensure_ascii=False))
"""


if __name__ == "__main__":
    main()
