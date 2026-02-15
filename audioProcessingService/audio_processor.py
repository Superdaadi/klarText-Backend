import librosa
import soundfile as sf
import numpy as np
import noisereduce as nr
import os

TARGET_SR = 16000

def process_audio(input_path: str):
    """
    Verarbeitet das Audio und speichert das Ergebnis im selben Ordner 
    wie die Eingabedatei ab, um die UUID-Struktur beizubehalten.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Eingabedatei nicht gefunden: {input_path}")

    # 1. Audio laden (Mono & 16kHz)
    audio, sr = librosa.load(
        input_path,
        sr=TARGET_SR,
        mono=True
    )

    # 2. Rauschunterdrückung
    reduced_audio = nr.reduce_noise(
        y=audio,
        sr=sr,
        prop_decrease=0.9
    )

    # 3. Stille am Anfang/Ende entfernen
    trimmed_audio, _ = librosa.effects.trim(
        reduced_audio,
        top_db=25
    )

    # 4. Normalisierung
    normalized_audio = librosa.util.normalize(trimmed_audio)

    # 5. Speicherort festlegen
    # Wir speichern die verarbeitete Datei im gleichen Verzeichnis wie input_path
    # Wir hängen '_processed' an den Namen an, damit MFA die richtige Datei nimmt
    # oder überschreiben die Originaldatei, falls du nur eine Datei im Ordner willst.
    base_dir = os.path.dirname(input_path)
    file_name = os.path.basename(input_path)
    name_without_ext = os.path.splitext(file_name)[0]
    
    # Empfehlung: Benenne sie einheitlich, damit das .lab File dazu passt
    output_filename = f"{name_without_ext}_processed.wav"
    output_path = os.path.join(base_dir, output_filename)

    # 6. Speichern
    sf.write(output_path, normalized_audio, TARGET_SR)

    # 7. Metadaten berechnen
    duration = librosa.get_duration(y=normalized_audio, sr=TARGET_SR)

    # WICHTIG: Wir löschen das Original-Upload-File, damit MFA nicht 
    # zwei Audios im selben Ordner findet (das würde Fehler verursachen)
    if os.path.abspath(input_path) != os.path.abspath(output_path):
        os.remove(input_path)

    return {
        "audio_path": os.path.abspath(output_path),
        "duration": round(duration, 2)
    }