import whisper
import os
import re

# Load model once during startup
print("Loading Whisper Model...")

# whisper_model = whisper.load_model("base")
whisper_model = whisper.load_model("medium")

def digits_to_words(text: str) -> str:
    digit_map = {
        "0": "null",
        "1": "eins",
        "2": "zwei",
        "3": "drei",
        "4": "vier",
        "5": "fünf",
        "6": "sechs",
        "7": "sieben",
        "8": "acht",
        "9": "neun"
    }

    def replace_digits(match):
        return " ".join(digit_map[d] for d in match.group())

    return re.sub(r"\d+", replace_digits, text)


def transcribe_and_create_lab(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio-Datei nicht gefunden: {audio_path}")

    # transcribe
    result = whisper_model.transcribe(audio_path, language="de", fp16=False)    # Important: fp16 => only on CPU
    text = result['text'].strip()

    text = digits_to_words(text)

    # clean text (remove punctuation and lowercase)
    clean_text = re.sub(r'[.#?!,]', '', text).lower()

    # .lab file in same folder as audio file
    lab_path = os.path.splitext(audio_path)[0] + ".lab"

    print("LabPath: ", lab_path)
    
    with open(lab_path, "w", encoding="utf-8") as f:
        f.write(clean_text)

    return clean_text