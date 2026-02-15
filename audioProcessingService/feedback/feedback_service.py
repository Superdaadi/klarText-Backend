"""
Main Entry Point für das intelligente Aussprache-Feedback-System

Verwendung:
    python main.py <input_json_path> [--output-dir OUTPUT_DIR] [--user-feedback FEEDBACK_TYPE]
    
Beispiele:
    python main.py gop_results.json
    python main.py gop_results.json --output-dir ./feedback_output
    python main.py gop_results.json --user-feedback too_strict
"""

import json
import argparse
import os
from datetime import datetime
from pathlib import Path

from feedback.analyzer import IntelligentAnalyzer
from feedback.feedback_generator import FeedbackGenerator
from feedback.adaptive_thresholds import AdaptiveThresholds



def load_gop_data(filepath: str) -> list:
    """Lädt GOP-Daten aus JSON-Datei"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_results(output_dir: str, analysis: dict, feedback: dict):
    """Speichert alle Ergebnisse"""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Vollständige Analyse (für Entwickler/Debug)
    analysis_path = os.path.join(output_dir, f"analysis_{timestamp}.json")
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # 2. Nutzerfreundliches Feedback (für Frontend)
    feedback_path = os.path.join(output_dir, f"feedback_{timestamp}.json")
    with open(feedback_path, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)
    
    # 3. Text-Version (für schnelles Lesen)
    generator = FeedbackGenerator()
    text_feedback = generator.generate_text_feedback(feedback)
    text_path = os.path.join(output_dir, f"feedback_{timestamp}.txt")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text_feedback)
    
    # 4. Heatmap-Daten für Visualisierung
    heatmap = generate_heatmap(analysis["raw_data"])
    heatmap_path = os.path.join(output_dir, f"heatmap_{timestamp}.json")
    with open(heatmap_path, 'w', encoding='utf-8') as f:
        json.dump(heatmap, f, ensure_ascii=False, indent=2)
    
    # Erstelle auch "latest" Symlinks (ohne Timestamp)
    latest_files = {
        "analysis.json": analysis_path,
        "feedback.json": feedback_path,
        "feedback.txt": text_path,
        "heatmap.json": heatmap_path
    }
    
    for latest_name, timestamped_path in latest_files.items():
        latest_path = os.path.join(output_dir, latest_name)
        # Entferne alte Datei falls vorhanden
        if os.path.exists(latest_path):
            os.remove(latest_path)
        # Kopiere neue Datei
        with open(timestamped_path, 'r', encoding='utf-8') as src:
            with open(latest_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
    
    return {
        "analysis": analysis_path,
        "feedback": feedback_path,
        "text": text_path,
        "heatmap": heatmap_path
    }


def generate_heatmap(raw_data: list) -> list:
    """
    Generiert Heatmap-Daten für zeitbasierte Visualisierung
    
    Returns:
        Liste mit {phoneme, start, end, score, color}
    """
    heatmap = []
    
    for item in raw_data:
        # Konvertiere GOP zu 0-100 Score
        gop = item["gop_score"]
        score = gop_to_score(gop)
        
        # Farbe basierend auf Score
        if score >= 75:
            color = "green"
        elif score >= 60:
            color = "yellow"
        elif score >= 45:
            color = "orange"
        else:
            color = "red"
        
        heatmap.append({
            "phoneme": item["phoneme"],
            "start": item["start"],
            "end": item["end"],
            "gop_score": round(gop, 2),
            "score_0_100": round(score, 1),
            "color": color
        })
    
    return heatmap


def gop_to_score(gop: float, min_gop: float = -45, max_gop: float = -25) -> float:
    """Erweitert den Bereich, sodass -25 schon für 100% reicht statt -20"""
    gop = max(min(gop, max_gop), min_gop)
    return ((gop - min_gop) / (max_gop - min_gop)) * 100


def print_summary(feedback: dict):
    """Gibt Zusammenfassung auf der Konsole aus"""
    print("\n" + "="*70)
    print(f"  {feedback['headline']}")
    print("="*70)
    print(f"\n📊 Gesamtscore: {feedback['overall_score']}/100 (Note: {feedback['grade']})")
    print(f"\n{feedback['summary']}")
    print(f"\n💬 {feedback['encouragement']}")
    print()
    
    # Quick Stats
    meta = feedback['metadata']
    print(f"📈 Verteilung:")
    print(f"   Ausgezeichnet: {meta['distribution']['excellent']}")
    print(f"   Gut:          {meta['distribution']['good']}")
    print(f"   OK:           {meta['distribution']['ok']}")
    print(f"   Übungsbedarf: {meta['distribution']['needs_work']}")
    print()
    
    if feedback['weaknesses']:
        print(f"⚠️  {len(feedback['weaknesses'])} Laute brauchen Aufmerksamkeit")
        for w in feedback['weaknesses'][:3]:
            print(f"   • {w['phoneme']}: {w['score']:.0f}/100")
    
    print("\n" + "="*70 + "\n")



def main(input_path: str, output_path: str, config: str, userFeedback: str = "", quiet: bool = False):
    # Interne Hilfsfunktion für sauberes Logging
    def log(msg):
        if not quiet: print(msg)

    # 1. Validierung
    for path in [input_path, config]:
        if not os.path.exists(path):
            log(f"❌ Fehler: {path} nicht gefunden.")
            return 1
    
    os.makedirs(output_path, exist_ok=True)

    # 2. Adaptives Feedback (Thresholds)
    if userFeedback:
        tm = AdaptiveThresholds(config)
        tm.record_user_feedback(userFeedback)
        log(f"✅ Feedback ({userFeedback}) verarbeitet. Neue Werte: {tm.get_thresholds()}\n")
    
    # 3. Pipeline: Laden -> Analysieren -> Generieren
    log("🔄 Verarbeite Daten...")
    try:
        gop_data = load_gop_data(input_path)
        analysis = IntelligentAnalyzer(config).analyze(gop_data)
        # log(analysis)
        feedback = FeedbackGenerator(config).generate_feedback(analysis)
        
        # 4. Speichern und Abschluss
        saved_paths = save_results(output_path, analysis, feedback)
        
        log(f"✅ Erfolg! {len(gop_data)} Phoneme analysiert.")
        log(f"📁 Gespeichert in: {output_path}")
        
        if not quiet:
            print_summary(feedback)
            log("💡 Tipp: Feedback zu streng? 'too_strict' nutzen.")

    except Exception as e:
        log(f"❌ Fehler in der Pipeline: {e}")
        return 1
    
    return 0




# --- MAIN ---

INPUT_FILE = "./alignment_output/gop_results.json"
OUTPUT_DIR = "./feedback_output"
CONFIG_FILE = "./feedback/config.json"


def runFeedback(dir: str):
    main(f"{dir}/gop_results.json", dir, CONFIG_FILE, "too_strict", False)


if __name__ == "__main__":
    exit(main(INPUT_FILE, OUTPUT_DIR, CONFIG_FILE, "too_strict", False))
