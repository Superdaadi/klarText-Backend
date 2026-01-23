VOWELS = "aeiouyøœɐəɪʊɔɑɛaː"

def syllabify(phones):
    syllables = []
    current = []

    for p in phones:
        current.append(p)
        if any(v in p["text"] for v in VOWELS):
            syllables.append(current)
            current = []

    if current and syllables:
        syllables[-1].extend(current)

    return syllables
