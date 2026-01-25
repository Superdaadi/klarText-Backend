def phones_to_words(words, phones):
    word_phones = []

    for w in words:
        w_start = w["xmin"]
        w_end = w["xmax"]
        w_text = w["text"]

        if not w_text:
            continue

        phones_in_word = [
            p for p in phones
            if p["xmin"] >= w_start and p["xmax"] <= w_end and p["text"]
        ]

        word_phones.append({
            "word": w_text,
            "start": w_start,
            "end": w_end,
            "phones": phones_in_word
        })

    return word_phones
