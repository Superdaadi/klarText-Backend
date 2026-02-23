import whisper
import os
import subprocess
import textgrid
import json

def generate_transcription(audio_path):
    # Modell "base" oder "small" reicht für Deutsch meist völlig aus
    model = whisper.load_model("small")
    result = model.transcribe(audio_path, language="de")
    
    # Text extrahieren
    text = result['text'].strip()
    
    # .lab Datei für MFA erstellen (gleicher Name wie Audio)
    base_name = os.path.splitext(audio_path)[0]
    lab_path = f"{base_name}.lab"
    
    with open(lab_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    return lab_path

def align_and_parse(audio_folder, output_folder):
    # MFA Alignment Befehl
    subprocess.run([
        "mfa", "align", 
        audio_folder, 
        "german_mfa", "german_mfa", 
        output_folder
    ])
    
    # Ergebnisse sammeln
    final_results = {}
    for file in os.listdir(output_folder):
        if file.endswith(".TextGrid"):
            tg_path = os.path.join(output_folder, file)
            final_results[file] = parse_textgrid(tg_path)
            
    return final_results

def parse_textgrid(tg_path):
    tg = textgrid.TextGrid.fromFile(tg_path)
    phones = tg.getFirst("phones")
    return [
        {"phoneme": p.mark, "start": p.minTime, "end": p.maxTime}
        for p in phones if p.mark not in ["", "sp", "sil", "spn"]
    ]

# --- Ablauf ---
audio_file = "mein_audio.wav"
# 1. Text automatisch generieren
generate_transcription(audio_file)

# 2. Alignment starten (für den gesamten Ordner)
results = align_and_parse("./audio_input", "./alignment_output")
print(json.dumps(results, indent=2))

