import json
from pronunciation_score.alignment import phones_to_words
from pronunciation_score.scorer import score_all

INPUT_PATH = "pronunciation_score/input/textgrid.json"


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    words = data["words"]
    phones = data["phones"]

    words_with_phones = phones_to_words(words, phones)
    result = score_all(words_with_phones)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
