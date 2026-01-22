import subprocess
import os
import textgrid
import json
import re
from num2words import num2words

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








# --- MAIN ---
INPUT = "./audio_input"
OUTPUT = "./alignment_output"

if __name__ == "__main__":
    try:
        run_mfa_alignment(INPUT, OUTPUT)
        
        tg_file = os.path.join(OUTPUT, "test.TextGrid")
        
        if os.path.exists(tg_file):
            result = export_phonemes_to_json(tg_file)
            with open("phoneme_output.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("✅ Fertig! JSON wurde erstellt:")
            print(json.dumps(result[:5], indent=2))

            data = parse_textgrid(tg_file)

            output_file = os.path.join(OUTPUT, "textgrid.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        else:
            print("❌ Fehler: TextGrid wurde nicht gefunden.")
            
    except subprocess.CalledProcessError as e:
        print(f"💥 MFA-Fehler! Returncode: {e.returncode}")
        print(f"Output:\n{e.output}")
    except Exception as e:
        print(f"💥 Fehler: {e}")