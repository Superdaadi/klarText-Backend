# phoneme_map.py

IPA_TO_PHONEME = {
    "a": "A",
    "aː": "A",
    "ɛ": "E",
    "ɪ": "I",
    "i": "I",
    "ɔ": "O",
    "ʊ": "U",
    "u": "U",
    "s": "S",
    "z": "Z",
    "ʃ": "SH",
    "ç": "CH",
    "x": "X",
    "t": "T",
    "tʰ": "T",
    "d": "D",
    "k": "K",
    "g": "G",
    "n": "N",
    "m": "M",
    "l": "L",
    "r": "R",
    "j": "J",
    "h": "H"
}

def map_ipa(ipa):
    return IPA_TO_PHONEME.get(ipa, None)
