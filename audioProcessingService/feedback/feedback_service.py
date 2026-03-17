# Feedback Service

import json
import argparse
import os
from datetime import datetime
from pathlib import Path

from feedback.analyzer import IntelligentAnalyzer
from feedback.feedback_generator import FeedbackGenerator
from feedback.adaptive_thresholds import AdaptiveThresholds



def load_gop_data(filepath: str) -> list:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_results(output_dir: str, analysis: dict, feedback: dict):
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. full analysis
    analysis_path = os.path.join(output_dir, f"analysis_{timestamp}.json")
    with open(analysis_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    # 2. user feedback
    feedback_path = os.path.join(output_dir, f"feedback_{timestamp}.json")
    with open(feedback_path, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)
    
    # 3. text version
    generator = FeedbackGenerator()
    text_feedback = generator.generate_text_feedback(feedback)
    text_path = os.path.join(output_dir, f"feedback_{timestamp}.txt")
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text_feedback)
    
    # 4. heatmap data
    heatmap = generate_heatmap(analysis["raw_data"])
    heatmap_path = os.path.join(output_dir, f"heatmap_{timestamp}.json")
    with open(heatmap_path, 'w', encoding='utf-8') as f:
        json.dump(heatmap, f, ensure_ascii=False, indent=2)
    
    # 5. update latest files
    latest_files = {
        "analysis.json": analysis_path,
        "feedback.json": feedback_path,
        "feedback.txt": text_path,
        "heatmap.json": heatmap_path
    }
    
    for latest_name, timestamped_path in latest_files.items():
        latest_path = os.path.join(output_dir, latest_name)
        # overwrite old
        if os.path.exists(latest_path):
            os.remove(latest_path)
        # copy new
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
    heatmap = []
    
    for item in raw_data:
        # GOP to 0-100 score
        gop = item["gop_score"]
        score = gop_to_score(gop)
        
        # score colors
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
    gop = max(min(gop, max_gop), min_gop)
    return ((gop - min_gop) / (max_gop - min_gop)) * 100


def print_summary(feedback: dict):
    # Gibt Zusammenfassung auf der Konsole aus
    print("\n" + "="*70)
    print(f"  {feedback['headline']}")
    print("="*70)
    print(f"\nDatum: {feedback['date']}")
    print(f"\nErkannter Text: {feedback['text']}")
    print(f"\n📊 Gesamtscore: {feedback['overall_score']}/100 (Note: {feedback['grade']})")
    print(f"\n{feedback['summary']}")
    print(f"\n💬 {feedback['encouragement']}")
    print()
    
    # stats
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



def main(input_path: str, output_path: str, config: str, text: str, userFeedback: str = "", quiet: bool = False):
    # helper log
    def log(msg):
        if not quiet: print(msg)

    # 1. Validation
    for path in [input_path, config]:
        if not os.path.exists(path):
            log(f"❌ Fehler: {path} nicht gefunden.")
            return 1
    
    os.makedirs(output_path, exist_ok=True)

    # 2. Adaptive thresholds
    if userFeedback:
        tm = AdaptiveThresholds(config)
        tm.record_user_feedback(userFeedback)
        log(f"✅ Feedback ({userFeedback}) verarbeitet. Neue Werte: {tm.get_thresholds()}\n")
    
    # 3. Pipeline: Load -> Analyze -> Generate
    log("🔄 Verarbeite Daten...")
    try:
        gop_data = load_gop_data(input_path)
        analysis = IntelligentAnalyzer(config).analyze(gop_data)
        # log(analysis)
        feedback = FeedbackGenerator(config).generate_feedback(analysis, text)
        
        # 4. Results
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


def runFeedback(dir: str, text: str):
    main(f"{dir}/gop_results.json", dir, CONFIG_FILE, text, "too_strict", False)


if __name__ == "__main__":
    exit(main(INPUT_FILE, OUTPUT_DIR, CONFIG_FILE, "too_strict", False))
