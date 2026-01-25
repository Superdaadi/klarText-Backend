VOWELS = set("aeiouyɛøœɐəɪʊɔɑɛ")

def syllabify(phonemes):
    syllables = []
    current = []

    for ph in phonemes:
        current.append(ph)
        if ph in VOWELS:
            syllables.append(current)
            current = []

    if current and syllables:
        syllables[-1].extend(current)

    return syllables
