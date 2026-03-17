#!/usr/bin/env python3
"""
Demo-Skript für das intelligente Aussprache-Feedback-System

Zeigt verschiedene Anwendungsfälle und Features
"""

import json
import os
import sys

def demo_basic_analysis():
    """Demo 1: Basis-Analyse"""
    print("\n" + "="*70)
    print("DEMO 1: Basis-Analyse")
    print("="*70)
    
    print("\n📋 Lade GOP-Daten und führe Analyse durch...")
    os.system("python main.py test_gop_data.json --output-dir demo_output")
    
    print("\n✅ Demo 1 abgeschlossen!")
    print("   Ergebnisse in: demo_output/")

def demo_adaptive_learning():
    """Demo 2: Adaptives Lernen"""
    print("\n" + "="*70)
    print("DEMO 2: Adaptives Lernen - Schwellenwerte anpassen")
    print("="*70)
    
    # Zeige aktuelle Schwellenwerte
    with open("config.json", "r") as f:
        config = json.load(f)
    
    print("\n📊 Aktuelle Schwellenwerte:")
    for key, value in config["adaptive_thresholds"]["current"].items():
        print(f"   {key}: {value}")
    
    print("\n🔄 Simuliere User-Feedback: 'zu streng'...")
    for i in range(3):
        print(f"   Feedback {i+1}/3: too_strict")
        os.system("python main.py test_gop_data.json --user-feedback too_strict --quiet")
    
    # Zeige neue Schwellenwerte
    with open("config.json", "r") as f:
        config = json.load(f)
    
    print("\n📊 Neue Schwellenwerte (nach Anpassung):")
    for key, value in config["adaptive_thresholds"]["current"].items():
        print(f"   {key}: {value}")
    
    print("\n✅ Demo 2 abgeschlossen!")
    print("   Das System hat die Schwellenwerte automatisch gelockert!")

def demo_comparison():
    """Demo 3: Vergleich verschiedener Feedback-Styles"""
    print("\n" + "="*70)
    print("DEMO 3: Feedback-Vergleich")
    print("="*70)
    
    # Normale Bewertung
    print("\n📊 1. Normale Bewertung:")
    os.system("python main.py test_gop_data.json --output-dir demo_comparison/normal --quiet")
    
    # Zeige nur Gesamtscore
    with open("demo_comparison/normal/feedback.json", "r") as f:
        feedback = json.load(f)
    print(f"   Gesamtscore: {feedback['overall_score']}/100")
    print(f"   Schwächen: {len(feedback['weaknesses'])}")
    
    print("\n✅ Demo 3 abgeschlossen!")
    print("   Ergebnisse in: demo_comparison/")

def demo_output_formats():
    """Demo 4: Verschiedene Output-Formate"""
    print("\n" + "="*70)
    print("DEMO 4: Output-Formate erkunden")
    print("="*70)
    
    os.system("python main.py test_gop_data.json --output-dir demo_formats --quiet")
    
    print("\n📁 Generierte Dateien:")
    for filename in os.listdir("demo_formats"):
        if not filename.startswith("._"):
            filepath = os.path.join("demo_formats", filename)
            size = os.path.getsize(filepath)
            print(f"   • {filename} ({size} bytes)")
    
    print("\n📄 Vorschau: feedback.txt")
    print("-" * 70)
    with open("demo_formats/feedback.txt", "r") as f:
        lines = f.readlines()[:20]
        print("".join(lines))
        if len(lines) == 20:
            print("   ...")
    
    print("\n✅ Demo 4 abgeschlossen!")

def demo_heatmap():
    """Demo 5: Heatmap-Daten"""
    print("\n" + "="*70)
    print("DEMO 5: Heatmap-Visualisierung (Daten)")
    print("="*70)
    
    os.system("python main.py test_gop_data.json --output-dir demo_heatmap --quiet")
    
    with open("demo_heatmap/heatmap.json", "r") as f:
        heatmap = json.load(f)
    
    print("\n🗺️ Heatmap-Daten (erste 10 Phoneme):")
    print(f"{'Zeit':<12} {'Phonem':<8} {'Score':<8} {'Farbe':<10}")
    print("-" * 50)
    
    for item in heatmap[:10]:
        time_range = f"{item['start']:.2f}-{item['end']:.2f}s"
        print(f"{time_range:<12} {item['phoneme']:<8} {item['score_0_100']:<8.1f} {item['color']:<10}")
    
    print(f"\n   ... und {len(heatmap) - 10} weitere Phoneme")
    
    print("\n✅ Demo 5 abgeschlossen!")

def demo_api_usage():
    """Demo 6: Programmatische Verwendung"""
    print("\n" + "="*70)
    print("DEMO 6: Programmatische API-Verwendung")
    print("="*70)
    
    print("\n📝 Beispiel-Code für Integration:\n")
    
    code = '''
from analyzer import IntelligentAnalyzer
from feedback_generator import FeedbackGenerator
import json

# 1. Lade GOP-Daten
with open("test_gop_data.json", "r") as f:
    gop_data = json.load(f)

# 2. Analysiere
analyzer = IntelligentAnalyzer("config.json")
analysis = analyzer.analyze(gop_data)

# 3. Generiere Feedback
generator = FeedbackGenerator("config.json")
feedback = generator.generate_feedback(analysis)

# 4. Verwende die Daten
print(f"Gesamtscore: {feedback['overall_score']}/100")
print(f"Note: {feedback['grade']}")

for weakness in feedback['weaknesses']:
    print(f"Übe: {weakness['phoneme']} (Score: {weakness['score']})")
'''
    
    print(code)
    
    print("\n🔄 Führe Beispiel aus...\n")
    
    from analyzer import IntelligentAnalyzer
    from feedback_generator import FeedbackGenerator
    
    with open("test_gop_data.json", "r") as f:
        gop_data = json.load(f)
    
    analyzer = IntelligentAnalyzer("config.json")
    analysis = analyzer.analyze(gop_data)
    
    generator = FeedbackGenerator("config.json")
    feedback = generator.generate_feedback(analysis)
    
    print(f"✅ Gesamtscore: {feedback['overall_score']}/100")
    print(f"✅ Note: {feedback['grade']}")
    print(f"✅ Schwächen erkannt: {len(feedback['weaknesses'])}")
    
    print("\n✅ Demo 6 abgeschlossen!")

def main():
    """Hauptmenü"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   🎯 INTELLIGENTES AUSSPRACHE-FEEDBACK-SYSTEM - DEMO              ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    demos = {
        "1": ("Basis-Analyse", demo_basic_analysis),
        "2": ("Adaptives Lernen", demo_adaptive_learning),
        "3": ("Feedback-Vergleich", demo_comparison),
        "4": ("Output-Formate", demo_output_formats),
        "5": ("Heatmap-Daten", demo_heatmap),
        "6": ("API-Verwendung", demo_api_usage),
        "all": ("Alle Demos", None)
    }
    
    print("Verfügbare Demos:\n")
    for key, (name, _) in demos.items():
        print(f"  {key}. {name}")
    
    print("\n  0. Beenden\n")
    
    choice = input("Demo auswählen [1-6, all, 0]: ").strip()
    
    if choice == "0":
        print("\n👋 Auf Wiedersehen!\n")
        return
    
    if choice == "all":
        for key in ["1", "2", "3", "4", "5", "6"]:
            demos[key][1]()
            input("\nDrücke Enter für die nächste Demo...")
    elif choice in demos and choice != "all":
        demos[choice][1]()
    else:
        print("❌ Ungültige Auswahl!")
        return
    
    print("\n" + "="*70)
    print("🎉 Demo abgeschlossen!")
    print("="*70)
    
    print("\n💡 Nächste Schritte:")
    print("   • Schaue dir die generierten Dateien an")
    print("   • Teste mit eigenen GOP-Daten")
    print("   • Passe config.json an deine Bedürfnisse an")
    print("   • Integriere ins Frontend mit den JSON-APIs\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo abgebrochen!\n")
        sys.exit(0)
