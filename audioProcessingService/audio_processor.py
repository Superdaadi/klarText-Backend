import librosa
import soundfile as sf
import numpy as np
import noisereduce as nr
import os

TARGET_SR = 16000

def process_audio(input_path: str):
    """Process audio and save results in the same folder."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Eingabedatei nicht gefunden: {input_path}")

    # 1. Load (16kHz mono)
    audio, sr = librosa.load(
        input_path,
        sr=TARGET_SR,
        mono=True
    )

    # 2. Noise reduction
    reduced_audio = nr.reduce_noise(
        y=audio,
        sr=sr,
        prop_decrease=0.9
    )

    # 3. Trim silence
    trimmed_audio, _ = librosa.effects.trim(
        reduced_audio,
        top_db=25
    )

    # 4. Normalize
    normalized_audio = librosa.util.normalize(trimmed_audio)

    # 5. Save

    base_dir = os.path.dirname(input_path)
    file_name = os.path.basename(input_path)
    name_without_ext = os.path.splitext(file_name)[0]
    
    output_filename = f"{name_without_ext}_processed.wav"
    output_path = os.path.join(base_dir, output_filename)

    # 5. Save
    sf.write(output_path, normalized_audio, TARGET_SR)

    # 6. Metadata
    duration = librosa.get_duration(y=normalized_audio, sr=TARGET_SR)

    # Delete original
    if os.path.abspath(input_path) != os.path.abspath(output_path):
        os.remove(input_path)

    return {
        "audio_path": os.path.abspath(output_path),
        "duration": round(duration, 2)
    }