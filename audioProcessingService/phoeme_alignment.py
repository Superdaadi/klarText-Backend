import os
import shutil
import json
from montreal_forced_aligner.command_line.align import run_align_corpus
from montreal_forced_aligner import config
import parselmouth  # Für TextGrid Parsing

def phoneme_alignment(audio_path, transcript_text, output_path="alignment.json"):
    """
    Wandelt Audio in IPA-Phoneme mit Zeitstempeln um.
    """
    # Temporäres Verzeichnis vorbereiten
    temp_dir = "mfa_temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Audio-Datei ins Temp-Verzeichnis kopieren
    audio_filename = os.path.basename(audio_path)
    temp_audio_path = os.path.join(temp_dir, audio_filename)
    shutil.copy(audio_path, temp_audio_path)
    
    # Transcript-Datei erstellen (mit gleichem Namen wie Audio, aber .txt)
    transcript_file = os.path.join(temp_dir, os.path.splitext(audio_filename)[0] + ".txt")
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript_text)
    
    # MFA-Konfiguration
    mfa_config = config.MfaConfig()
    mfa_config.output_directory = temp_dir
    mfa_config.clean = True
    mfa_config.verbose = True
    
    # Alignment ausführen
    run_align_corpus(
        corpus_directory=temp_dir,          # enthält Audio + Transcript
        dictionary_path="german.dict",     # MFA German dictionary
        acoustic_model_path="german.zip",  # Pfad zum deutschen Akustikmodell
        output_directory=temp_dir,
        config_path=None
    )
    
    # Phoneme aus TextGrid extrahieren
    textgrid_file = os.path.join(temp_dir, os.path.splitext(audio_filename)[0] + ".TextGrid")
    phoneme_list = []
    
    if os.path.exists(textgrid_file):
        tg = parselmouth.TextGrid(textgrid_file)
        for interval in tg[1]:  # 1. Tier = Phoneme
            if interval.text.strip():
                phoneme_list.append({
                    "phoneme": interval.text.strip(),
                    "start": round(interval.minTime, 2),
                    "end": round(interval.maxTime, 2)
                })
    
    # Output speichern
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(phoneme_list, f, ensure_ascii=False, indent=2)
    
    return phoneme_list

# Beispielaufruf
audio_file = "beispiel.wav"
transcript_text = "Schaf"
result = phoneme_alignment(audio_file, transcript_text)
print(json.dumps(result, ensure_ascii=False, indent=2))
