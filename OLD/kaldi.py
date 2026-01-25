import math
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Kaldiio ist notwendig für den Zugriff auf .ark Dateien
try:
    from kaldiio import ReadHelper
except ImportError:
    print("Bitte installiere kaldiio: pip install kaldiio")

# --- Datenmodelle ---
@dataclass
class PhoneSegment:
    symbol: str
    phone_id: int
    f_start: int
    f_end: int

# --- Hilfsklassen für Kaldi ---
class KaldiDataHelper:
    @staticmethod
    def load_phones_mapping(phones_txt_path: str) -> Dict[str, int]:
        """Liest die phones.txt und erstellt ein Mapping Symbol -> ID"""
        mapping = {}
        if not os.path.exists(phones_txt_path):
            print(f"WARNUNG: {phones_txt_path} nicht gefunden. Nutze Dummy-IDs.")
            return {}
        with open(phones_txt_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    mapping[parts[0]] = int(parts[1])
        return mapping

    @staticmethod
    def load_posteriors(ark_path: str) -> Dict[str, List[Dict[int, float]]]:
        """Liest die ark-Datei und speichert Posterioren pro Frame"""
        data = {}
        if not os.path.exists(ark_path):
            print(f"ERROR: {ark_path} fehlt!")
            return {}
        with ReadHelper(f"ark:{ark_path}") as reader:
            for utt_id, post in reader:
                frames = []
                for frame in post:
                    # Konvertiert Kaldi-Posterioren in Python-Dict
                    frames.append({pid: prob for pid, prob in frame})
                data[utt_id] = frames
        return data

# --- GOP Logik ---
class KaldiGOPScorer:
    @staticmethod
    def calculate_gop(frames: List[Dict[int, float]], correct_id: int) -> float:
        """Kern-Formel: log P(p|x) - log max P(q|x)"""
        if not frames:
            return -10.0
        
        total_gop = 0.0
        eps = 1e-10
        
        for f in frames:
            p_correct = f.get(correct_id, eps)
            p_max = max(f.values()) if f else eps
            # Log-Likelihood Ratio
            total_gop += math.log(p_correct) - math.log(p_max)
            
        return total_gop / len(frames)

    @staticmethod
    def normalize(gop: float) -> int:
        """Mapping von GOP-Log-Ratio auf 0-100 Skala"""
        # Sigmoid-basierte Normalisierung
        score = 100 / (1 + math.exp(-0.5 * gop))
        return int(round(score))

# --- Engine ---
class GOPProcessingEngine:
    def __init__(self, ark_path: str, phones_path: str):
        print("Lade Kaldi-Daten...")
        self.posteriors = KaldiDataHelper.load_posteriors(ark_path)
        self.phone_map = KaldiDataHelper.load_phones_mapping(phones_path)

    def process_mfa_json(self, json_path: str, utt_id: str):
        """Verarbeitet das MFA-JSON und berechnet Scores"""
        if not os.path.exists(json_path):
            print(f"ERROR: {json_path} nicht gefunden!")
            return []
            
        with open(json_path, "r", encoding="utf-8") as f:
            mfa_data = json.load(f)
        
        if utt_id not in self.posteriors:
            print(f"ERROR: Utterance {utt_id} nicht in Ark-Datei!")
            return []

        results = []
        for p in mfa_data["phones"]:
            symbol = p["text"]
            if not symbol: continue # Pausen überspringen
            
            # 1. Zeit in Frames (Kaldi Standard: 10ms Schritte = 100 fps)
            f_start = int(float(p["xmin"]) * 100)
            f_end = int(float(p["xmax"]) * 100)
            
            # 2. Phone ID finden
            p_id = self.phone_map.get(symbol, 0)
            
            # 3. Frames aus Posterioren extrahieren
            relevant_frames = self.posteriors[utt_id][f_start:f_end]
            
            # 4. Score berechnen
            gop_val = KaldiGOPScorer.calculate_gop(relevant_frames, p_id)
            score = KaldiGOPScorer.normalize(gop_val)
            
            results.append({
                "phone": symbol,
                "gop": round(gop_val, 3),
                "score": score,
                "start": p["xmin"],
                "end": p["xmax"]
            })
        return results

# --- Ausführung ---
if __name__ == "__main__":
    print("--- Modul 5.1: Kaldi-GOP gestartet ---")
    
    # Pfadkonfiguration
    ARK_FILE = "posterior.ark"
    PHONES_FILE = "phones.txt"
    JSON_INPUT = "textgrid.json"
    UTTERANCE_ID = "utt_001" # Diese ID muss exakt so in deiner .ark stehen

    try:
        engine = GOPProcessingEngine(ARK_FILE, PHONES_FILE)
        scoring_results = engine.process_mfa_json(JSON_INPUT, UTTERANCE_ID)

        # Tabellarische Ausgabe
        print(f"\nErgebnisse für {UTTERANCE_ID}:")
        print(f"{'Phone':<10} | {'Zeit (s)':<12} | {'GOP':<8} | {'Score':<5}")
        print("-" * 45)
        for r in scoring_results:
            zeit = f"{r['start']}-{r['end']}"
            print(f"{r['phone']:<10} | {zeit:<12} | {r['gop']:<8} | {r['score']:<5}")
            
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")











