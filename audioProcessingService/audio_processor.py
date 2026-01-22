import librosa
import soundfile as sf
import numpy as np
import noisereduce as nr
import os
import uuid

TARGET_SR = 16000
PROCESSED_DIR = "processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

def process_audio(input_path: str):
    audio, sr = librosa.load(
        input_path,
        sr=TARGET_SR,
        mono=True
    )

    reduced_audio = nr.reduce_noise(
        y=audio,
        sr=sr,
        prop_decrease=0.9
    )

    trimmed_audio, _ = librosa.effects.trim(
        reduced_audio,
        top_db=25
    )

    normalized_audio = librosa.util.normalize(trimmed_audio)

    filename = f"{uuid.uuid4()}.wav"
    output_path = os.path.join(PROCESSED_DIR, filename)

    sf.write(output_path, normalized_audio, TARGET_SR)

    duration = librosa.get_duration(y=normalized_audio, sr=TARGET_SR)

    return {
        "audio_path": os.path.abspath(output_path),
        "duration": round(duration, 2)
    }

