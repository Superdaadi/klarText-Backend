import subprocess
import os
import textgrid
import json
import re
from num2words import num2words
import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

def clean_text(text):
    # 1. Mehrfache Leerzeichen auf ein einzelnes reduzieren
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 2. Zahlen finden und umwandeln
    def replace_num(match):
        number = match.group()
        return num2words(int(number), lang='de')
    
    text = re.sub(r'\d+', replace_num, text)
    
    # 3. Satzzeichen entfernen (außer Leerzeichen, Umlaute bleiben)
    text = re.sub(r'[^\w\s]', '', text)
    
    # 4. Alles in Kleinbuchstaben und überschüssige Leerzeichen entfernen
    return text.lower().strip()



def run_mfa_alignment(input_dir, output_dir):
    # Bereinige die .lab Datei vor dem Start
    for file in os.listdir(input_dir):
        if file.endswith(".lab"):
            path = os.path.join(input_dir, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(clean_text(content))

    # MFA Befehl mit erhöhtem Beam und Logging
    cmd = [
        "mfa", "align",
        os.path.abspath(input_dir),
        "german_mfa",
        "german_mfa",
        os.path.abspath(output_dir),
        "--clean",
        "--overwrite",
        "--beam", "100",
        "--retry_beam", "400"
    ]
    
    print("⏳ MFA Aligner läuft...")

    # subprocess mit capture_output für Logging
    result = subprocess.run(cmd, text=True, capture_output=True)
    
    # Ausgabe stdout und stderr
    print("===== MFA STDOUT =====")
    print(result.stdout)
    print("===== MFA STDERR =====")
    print(result.stderr)

    # Überprüfen, ob MFA einen Fehler zurückgegeben hat
    result.check_returncode()



def export_phonemes_to_json(tg_path):
    tg = textgrid.TextGrid.fromFile(tg_path)
    # MFA erzeugt Tiers namens 'words' und 'phones'
    phones_tier = tg.getFirst("phones")
    
    phoneme_list = []
    for interval in phones_tier:
        # Ignoriere Stille (sil) und unbekannte Geräusche (spn)
        label = interval.mark
        if label not in ["", "sil", "spn", "sp"]:
            phoneme_list.append({
                "phoneme": label,
                "start": round(interval.minTime, 3),
                "end": round(interval.maxTime, 3)
            })
    return phoneme_list




def parse_textgrid(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tiers = {}
    # Trenne die einzelnen Items (Tiers)
    items = re.split(r'item \[\d+\]:', content)[1:]

    for item in items:
        # Name des Tiers extrahieren
        name_match = re.search(r'name = "(.+?)"', item)
        if not name_match:
            continue
        tier_name = name_match.group(1)

        # Alle Intervalle im Tier extrahieren
        intervals_matches = re.findall(
            r'intervals \[\d+\]:\s+xmin = ([\d\.]+)\s+xmax = ([\d\.]+)\s+text = "(.*?)"',
            item, re.DOTALL
        )

        # Liste von Intervallen erstellen
        intervals = []
        for xmin, xmax, text in intervals_matches:
            intervals.append({
                "xmin": float(xmin),
                "xmax": float(xmax),
                "text": text
            })

        tiers[tier_name] = intervals

    return tiers






def get_gop_scores(audio_path, phoneme_intervals):
    # Audio laden (Wav2Vec benötigt meist 16kHz)
    speech, sr = librosa.load(audio_path, sr=16000)
    input_values = processor(speech, return_tensors="pt", sampling_rate=16000).input_values

    # Logits (Wahrscheinlichkeiten vor dem Softmax) berechnen
    with torch.no_grad():
        logits = model(input_values).logits[0] # Shape: [Frames, Anzahl_Phoneme]
    
    # Log-Likelihoods berechnen
    log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
    
    results_with_gop = []
    
    # Für jedes Phonem aus deinem MFA-Output
    for p in phoneme_intervals:
        # Zeit in Frame-Indizes umrechnen (Wav2Vec2 hat ca. 50 Frames pro Sekunde)
        # Downsampling Faktor ist meist 320 bei 16kHz
        start_frame = int(p['start'] * 16000 / 320)
        end_frame = int(p['end'] * 16000 / 320)
        
        # Sicherstellen, dass wir innerhalb der Logits bleiben
        chunk = log_probs[start_frame:end_frame, :]
        if chunk.size(0) == 0: continue

        # Wir suchen das korrekte Label-ID für das Phonem
        # Hinweis: Das Mapping von MFA-Phonemen zu Wav2Vec2-Tokens muss oft normalisiert werden
        target_token = p['phoneme'].lower()
        
        try:
            # Token ID aus dem Processor holen
            token_id = processor.tokenizer.convert_tokens_to_ids(target_token)
            
            # 1. Log-Likelihood für den korrekten Laut (Durchschnitt über die Zeitdauer)
            ll_correct = chunk[:, token_id].mean().item()
            
            # 2. Max Log-Likelihood der Konkurrenz (alle außer dem Ziel-Token)
            # Wir maskieren den korrekten Token, um das Max der anderen zu finden
            mask = torch.ones(chunk.size(-1), dtype=torch.bool)
            mask[token_id] = False
            ll_competitors = chunk[:, mask].max(dim=-1)[0].mean().item()
            
            # GOP FORMEL: GOP = log P(target) - max log P(others)
            gop_score = ll_correct - ll_competitors
            
            p['gop_score'] = round(gop_score, 4)
            results_with_gop.append(p)
            
        except Exception as e:
            p['gop_score'] = None # Falls Phonem nicht im Modell-Vokabular
            results_with_gop.append(p)

    return results_with_gop








model_name = "facebook/wav2vec2-large-xlsr-53-german"
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)


# --- MAIN ---
INPUT = "./audio_input"
OUTPUT = "./alignment_output"

if __name__ == "__main__":
    try:
        # 1. Schritt: Alignment mit MFA
        run_mfa_alignment(INPUT, OUTPUT)
        
        # Pfad zur generierten TextGrid Datei
        # Hinweis: MFA benennt die Datei oft nach dem Namen des Audio-Files
        tg_file = os.path.join(OUTPUT, "test.TextGrid")
        
        if os.path.exists(tg_file):
            # 2. Schritt: Phoneme extrahieren (Intervalle)
            phoneme_intervals = export_phonemes_to_json(tg_file)
            
            # 3. Schritt: GOP-Scores berechnen
            # Wir übergeben das Original-Audio und die extrahierten Intervalle
            audio_file = os.path.join(INPUT, "test.wav")
            print(f"🔊 Berechne GOP-Scores für {audio_file}...")
            
            results_with_gop = get_gop_scores(audio_file, phoneme_intervals)
            
            # 4. Schritt: Speichern der Ergebnisse
            gop_output_path = os.path.join(OUTPUT, "gop_results.json")
            with open(gop_output_path, "w", encoding="utf-8") as f:
                json.dump(results_with_gop, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Erfolg! GOP-Scores wurden hier gespeichert: {gop_output_path}")
            
            # Optional: Kurze Vorschau in der Konsole
            for entry in results_with_gop[:3]:
                print(f"Phonem: {entry['phoneme']} | Score: {entry.get('gop_score', 'N/A')}")

        else:
            print(f"❌ Fehler: TextGrid wurde unter {tg_file} nicht gefunden. Prüfe die MFA-Logs.")
            
    except Exception as e:
        print(f"💥 Ein Fehler ist aufgetreten: {e}")