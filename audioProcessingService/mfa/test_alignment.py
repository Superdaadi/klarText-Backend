import subprocess
import osc
import textgrid
import json
import re
import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import soundfile as sf

def clean_text(text):
    # reduce mult whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # to lowercase
    return text.lower().strip()



def run_mfa_alignment(input_dir, output_dir):
    # clean .lab before start
    for file in os.listdir(input_dir):
        if file.endswith(".wav"):
            path = os.path.join(input_dir, file)
            data, samplerate = sf.read(path)
            # MFA needs 16kHz mono
            if samplerate != 16000:
                print(f"⚠️ Warnung: {file} hat {samplerate}Hz. MFA erwartet oft 16000Hz.")
        
        if file.endswith(".lab"):
            path = os.path.join(input_dir, file)
            with open(path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            cleaned = clean_text(raw_content)
            if not cleaned:
                print(f"❌ Fehler: {file} ist nach der Reinigung leer!")
                return
            with open(path, 'w', encoding='utf-8') as f:
                f.write(cleaned)

    # MFA command
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

    # run MFA
    result = subprocess.run(cmd, text=True, capture_output=True)
    
    # logs
    result.check_returncode()



def export_phonemes_to_json(tg_path):
    tg = textgrid.TextGrid.fromFile(tg_path)
    # get phone tier
    phones_tier = tg.getFirst("phones")
    
    phoneme_list = []
    for interval in phones_tier:
        # skip silence/noise
        label = interval.mark
        if label not in ["", "sil", "spn", "sp"]:
            phoneme_list.append({
                "phoneme": label,
                "start": round(interval.minTime, 3),
                "end": round(interval.maxTime, 3)
            })
    return phoneme_list




def parse_textgrid(file_path):
    with open(f"{file_path}_processed", 'r', encoding='utf-8') as f:
        content = f.read()

    tiers = {}
    # split tiers
    items = re.split(r'item \[\d+\]:', content)[1:]

    for item in items:
        # get name
        name_match = re.search(r'name = "(.+?)"', item)
        if not name_match:
            continue
        tier_name = name_match.group(1)

        # get intervals
        intervals_matches = re.findall(
            r'intervals \[\d+\]:\s+xmin = ([\d\.]+)\s+xmax = ([\d\.]+)\s+text = "(.*?)"',
            item, re.DOTALL
        )

        # map to list
        intervals = []
        for xmin, xmax, text in intervals_matches:
            intervals.append({
                "xmin": float(xmin),
                "xmax": float(xmax),
                "text": text
            })

        tiers[tier_name] = intervals

    return tiers



# Herzstück: GOP-Berechnung


def get_gop_scores(audio_path, phoneme_intervals):
    # load audio
    speech, sr = librosa.load(audio_path, sr=16000)
    input_values = processor(speech, return_tensors="pt", sampling_rate=16000).input_values

    # get logits
    with torch.no_grad():
        logits = model(input_values).logits[0] # Shape: [Frames, Anzahl_Phoneme]
    
    # log probs
    log_probs = torch.nn.functional.log_softmax(logits, dim=-1)
    
    results_with_gop = []
    
    # for each phoneme
    for p in phoneme_intervals:
        # time to frames
        start_frame = int(p['start'] * 16000 / 320)
        end_frame = int(p['end'] * 16000 / 320)
        
        # stay in bounds
        chunk = log_probs[start_frame:end_frame, :]
        if chunk.size(0) == 0: continue

        # get label id
        target_token = p['phoneme'].lower()
        
        try:
            # get token id
            token_id = processor.tokenizer.convert_tokens_to_ids(target_token)
            
            # 1. log-likelihood correct token
            ll_correct = chunk[:, token_id].mean().item()
            
            # 2. max log-likelihood others
            mask = torch.ones(chunk.size(-1), dtype=torch.bool)
            mask[token_id] = False
            ll_competitors = chunk[:, mask].max(dim=-1)[0].mean().item()
            
            # 3. GOP = log P(target) - max log P(others)
            gop_score = ll_correct - ll_competitors
            
            p['gop_score'] = round(gop_score, 4)
            results_with_gop.append(p)
            
        except Exception as e:
            p['gop_score'] = None # for tokens not in vocab
            results_with_gop.append(p)

    return results_with_gop


# Presentation hier


def runMFAall(INPUT, OUTPUT):
    try:
        # 1. Alignment
        run_mfa_alignment(INPUT, OUTPUT)
        
        # output file
        tg_file = os.path.join(OUTPUT, "test_processed.TextGrid")
        
        if os.path.exists(tg_file):
            # 2. Extract phonemes
            phoneme_intervals = export_phonemes_to_json(tg_file)
            
            # 3. GOP scores
            audio_file = os.path.join(INPUT, "test_processed.wav")
            print(f"🔊 Berechne GOP-Scores für {audio_file}...")
            
            results_with_gop = get_gop_scores(audio_file, phoneme_intervals)
            
            # 4. Save
            gop_output_path = os.path.join(OUTPUT, "gop_results.json")
            with open(gop_output_path, "w", encoding="utf-8") as f:
                json.dump(results_with_gop, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Erfolg! GOP-Scores wurden hier gespeichert: {gop_output_path}")
            
            # preview in console
            for entry in results_with_gop[:3]:
                print(f"Phoneme: {entry['phoneme']} | Score: {entry.get('gop_score', 'N/A')}")

        else:
            print(f"❌ Fehler: TextGrid wurde unter {tg_file} nicht gefunden. Prüfe die MFA-Logs.")
            
    except Exception as e:
        print(f"💥 Error: {e}")







model_name = "facebook/wav2vec2-large-xlsr-53-german"
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)









# --- MAIN ---
INPUT = "./../audio_input"
OUTPUT = "./../alignment_output"

if __name__ == "__main__":
    try:
        # 1. Alignment
        run_mfa_alignment(INPUT, OUTPUT)
        
        # output file
        tg_file = os.path.join(OUTPUT, "test_processed.TextGrid")
        
        if os.path.exists(tg_file):
            # 2. Extract phonemes
            phoneme_intervals = export_phonemes_to_json(tg_file)
            
            # 3. GOP scores
            audio_file = os.path.join(INPUT, "test_processed.wav")
            print(f"🔊 Berechne GOP-Scores für {audio_file}...")
            
            results_with_gop = get_gop_scores(audio_file, phoneme_intervals)
            
            # 4. Save results
            gop_output_path = os.path.join(OUTPUT, "gop_results.json")
            with open(gop_output_path, "w", encoding="utf-8") as f:
                json.dump(results_with_gop, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Erfolg! GOP-Scores wurden hier gespeichert: {gop_output_path}")
            
            # preview
            for entry in results_with_gop[:3]:
                print(f"Phoneme: {entry['phoneme']} | Score: {entry.get('gop_score', 'N/A')}")

        else:
            print(f"❌ Error: TextGrid not found at {tg_file}")
            
    except Exception as e:
        print(f"💥 Error: {e}")