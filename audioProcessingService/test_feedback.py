import json
from collections import defaultdict
import statistics
import os

# -----------------------------
# 1. Konfiguration
# -----------------------------

# GOP-Schwellen (anpassbar!)
GOOD_THRESHOLD = -25
OK_THRESHOLD = -29

# Artikulationstipps pro Phonem (Deutsch-fokussiert)
PHONEME_TIPS = {

    # ─── Plosive ───
    "p": "Lippen fest schließen, dann explosiv öffnen, stimmlos.",
    "pʰ": "Wie p, mit leichtem Luftstoß nach der Öffnung.",
    "b": "Lippen schließen, stimmhaft lösen.",
    "t": "Zungenspitze kurz an die oberen Schneidezähne, kein Nachhallen.",
    "tʰ": "Klarer, kurzer Hauch – nicht überaspirieren.",
    "d": "Stimmhaft, Zungenspitze locker an den Zähnen.",
    "k": "Zungenrücken gegen den weichen Gaumen, stimmlos lösen.",
    "kʰ": "Wie k, mit hörbarem, aber kurzem Luftstoß.",
    "g": "Stimmhaft, Zungenrücken am Gaumen.",

    # ─── Affrikaten ───
    "ts": "Explosiv mit t starten, sofort in scharfes s übergehen.",
    "tʃ": "t-Verschluss, dann sch-artiger Reibelaut.",
    "pf": "p-Verschluss, direkt in f überleiten.",

    # ─── Frikative ───
    "f": "Unterlippe sanft an obere Zähne, Luft gleichmäßig.",
    "v": "Wie f, aber stimmhaft.",
    "s": "Luftstrom bündeln, Zunge nah am Zahndamm, kein ‚sch‘.",
    "z": "Wie s, aber stimmhaft.",
    "ʃ": "Zunge weiter zurückziehen, Lippen leicht runden.",
    "ʒ": "Wie ʃ, aber stimmhaft.",
    "ç": "Sehr weich, Zunge flach Richtung Gaumen.",
    "x": "Rau, Zungenrücken nahe am weichen Gaumen.",
    "h": "Sehr leicht, nur Luft – kein harter Ansatz.",

    # ─── Nasale ───
    "m": "Lippen geschlossen, Luft durch die Nase.",
    "n": "Zungenspitze an den Zähnen, Luft nasal.",
    "ŋ": "Zungenrücken am Gaumen, kein n hörbar davor.",

    # ─── Liquide & Approximanten ───
    "l": "Zungenspitze an den Zahndamm, Seiten offen.",
    "ʁ": "Im Rachen gebildet, nicht gerollt.",
    "j": "Zunge hoch vorne, wie kurzes ‚i‘.",
    "ʋ": "Zwischen w und v, Lippen nur leicht gerundet.",

    # ─── Vokale kurz ───
    "ɪ": "Kurz und locker, nicht Richtung ‚iː‘ ziehen.",
    "ʏ": "Kurz, Lippen gerundet, Zunge vorne.",
    "ʊ": "Kurz, Lippen leicht gerundet, nicht zu offen.",
    "ɛ": "Offener als ‚e‘, Kiefer leicht senken.",
    "œ": "Kurz, offen, Lippen gerundet.",
    "ɔ": "Kurz, rund, nicht zu weit öffnen.",
    "a": "Kurz, zentral, Mund offen.",

    # ─── Vokale lang ───
    "iː": "Lang, gespannt, Zunge hoch vorne.",
    "yː": "Lang, gespannt, Lippen stark gerundet.",
    "uː": "Lang, gespannt, Lippen gerundet.",
    "eː": "Lang, geschlossen, ruhig halten.",
    "øː": "Lang, gespannt, Lippen gerundet.",
    "oː": "Lang, rund, gleichmäßig.",
    "ɛː": "Lang und offen, ruhig tragen.",
    "aː": "Lang halten, Mund weit öffnen.",

    # ─── Reduzierte Vokale ───
    "ə": "Sehr kurz, neutral, kaum Mundbewegung.",
    "ɐ": "Tiefer als schwa, leicht offen.",

    # ─── Diphthonge ───
    "aɪ": "Klarer Gleitlaut von a Richtung i.",
    "aʊ": "Von offenem a zu rundem u.",
    "ɔʏ": "Von rundem o Richtung ü."
}

PHONEME_EXERCISES = {
    "s": "Minimalpaare: sie – schie – see",
    "ç": "ich – nicht – mich – welche",
    "ʃ": "schon – Schule – sprechen",
    "t": "Tag – Tee – bitte",
    "ʁ": "rot – Brot – richtig",
}


# -----------------------------
# 2. Analyse-Funktionen
# -----------------------------

def classify_score(gop):
    if gop >= GOOD_THRESHOLD:
        return "gut"
    elif gop >= OK_THRESHOLD:
        return "mittel"
    else:
        return "schwach"

def analyze_pronunciation(data):
    phoneme_stats = defaultdict(list)

    for p in data:
        phoneme_stats[p["phoneme"]].append(p["gop_score"])

    summary = []
    for phoneme, scores in phoneme_stats.items():
        avg = statistics.mean(scores)
        summary.append({
            "phoneme": phoneme,
            "avg_gop": round(avg, 2),
            "rating": classify_score(avg)
        })

    return summary


def generate_exercises(weaknesses):
    exercises = []

    for w in weaknesses:
        if w["phoneme"] in PHONEME_EXERCISES:
            exercises.append({
                "phoneme": w["phoneme"],
                "exercise": PHONEME_EXERCISES[w["phoneme"]]
            })

    return exercises

# -----------------------------
# 3. Feedback-Generator
# -----------------------------

def generate_feedback(summary):
    feedback = []

    good = [s for s in summary if s["rating"] == "gut"]
    weak = [s for s in summary if s["rating"] == "schwach"]

    overall_score = round(statistics.mean([s["avg_gop"] for s in summary]), 2)

    # Gesamtfeedback
    feedback.append(f"🎯 Gesamtbewertung deiner Aussprache: {overall_score}")
    feedback.append("Je näher der Wert an 0 liegt, desto besser.\n")

    if overall_score > -27:
        feedback.append("💪 Sehr solide Aussprache! Du bist auf einem guten Weg.\n")
    else:
        feedback.append("🚀 Gute Basis! Mit gezieltem Training kannst du schnell Fortschritte machen.\n")

    # Stärken
    if good:
        feedback.append("✅ Besonders gut ausgesprochene Laute:")
        for g in good:
            feedback.append(f"  • {g['phoneme']} (Ø GOP: {g['avg_gop']})")
        feedback.append("")

    # Schwächen
    if weak:
        feedback.append("⚠️ Laute mit Verbesserungspotenzial:")
        for w in weak:
            tip = PHONEME_TIPS.get(w["phoneme"], "Achte auf eine saubere, kontrollierte Artikulation.")
            feedback.append(
                f"  • {w['phoneme']} (Ø GOP: {w['avg_gop']})\n"
                f"    👉 Tipp: {tip}"
            )

    return "\n".join(feedback)


def generate_heatmap(data):
    heatmap = []

    for p in data:
        heatmap.append({
            "phoneme": p["phoneme"],
            "start": p["start"],
            "end": p["end"],
            "score": gop_to_score(p["gop_score"])
        })

    return heatmap

def gop_to_score(gop, min_gop=-35, max_gop=-20):
    """
    Mappt GOP-Werte auf 0–100
    """
    gop = max(min(gop, max_gop), min_gop)
    return round((gop - min_gop) / (max_gop - min_gop) * 100, 1)



def analyze_pronunciation(data):
    phonemes = defaultdict(list)

    for p in data:
        phonemes[p["phoneme"]].append(p["gop_score"])

    results = []
    for phoneme, scores in phonemes.items():
        avg_gop = statistics.mean(scores)
        results.append({
            "phoneme": phoneme,
            "avg_gop": round(avg_gop, 2),
            "score_0_100": gop_to_score(avg_gop),
            "rating": (
                "gut" if avg_gop >= -25 else
                "mittel" if avg_gop >= -28 else
                "schwach"
            )
        })
    return results

def generate_feedback_json(summary):
    return {
        "overall_score": round(
            statistics.mean([s["score_0_100"] for s in summary]), 1
        ),
        "strengths": [s for s in summary if s["rating"] == "gut"],
        "weaknesses": [s for s in summary if s["rating"] == "schwach"],
        "details": summary
    }


def generate_feedback_text(feedback_json):
    lines = []

    lines.append(f"🎯 Gesamt-Aussprache-Score: {feedback_json['overall_score']}/100\n")

    if feedback_json["overall_score"] >= 70:
        lines.append("💪 Sehr gute Aussprache! Feinschliff lohnt sich.\n")
    else:
        lines.append("🚀 Gute Basis – gezieltes Training bringt schnelle Fortschritte.\n")

    if feedback_json["strengths"]:
        lines.append("✅ Stärken:")
        for s in feedback_json["strengths"]:
            lines.append(f"  • {s['phoneme']} ({s['score_0_100']}/100)")
        lines.append("")

    if feedback_json["weaknesses"]:
        lines.append("⚠️ Übungsbedarf:")
        for w in feedback_json["weaknesses"]:
            tip = PHONEME_TIPS.get(w["phoneme"], "Auf saubere Artikulation achten.")
            lines.append(
                f"  • {w['phoneme']} ({w['score_0_100']}/100)\n"
                f"    👉 Tipp: {tip}"
            )

    return "\n".join(lines)

def generate_feedback_text_json(feedback_json):
    return {
        "headline": "🗣️ Aussprache-Feedback",
        "overall": {
            "score": feedback_json["overall_score"],
            "message": (
                "Sehr gute Aussprache! Feinschliff lohnt sich."
                if feedback_json["overall_score"] >= 70
                else "Gute Basis – gezieltes Training bringt schnelle Fortschritte."
            )
        },
        "strengths": [
            {
                "phoneme": s["phoneme"],
                "score": s["score_0_100"],
                "label": "Stärke"
            }
            for s in feedback_json["strengths"]
        ],
        "weaknesses": [
            {
                "phoneme": w["phoneme"],
                "score": w["score_0_100"],
                "tip": PHONEME_TIPS.get(
                    w["phoneme"],
                    "Auf eine saubere und kontrollierte Artikulation achten."
                )
            }
            for w in feedback_json["weaknesses"]
        ],
        "exercises": feedback_json.get("exercises", [])
    }




# -----------------------------
# 4. Beispiel-Ausführung
# -----------------------------

INPUT = "./alignment_output"
OUTPUT = "./feedback_output"


if __name__ == "__main__":

    path = os.path.join(INPUT, "gop_results.json")
    
    # JSON hier laden (z.B. aus Datei)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = analyze_pronunciation(data)

    feedback_json = generate_feedback_json(summary)
    feedback_json["heatmap"] = generate_heatmap(data)
    feedback_json["exercises"] = generate_exercises(feedback_json["weaknesses"])

    # 1️⃣ Daten-JSON
    with open(os.path.join(OUTPUT, "feedback.json"), "w", encoding="utf-8") as f:
        json.dump(feedback_json, f, ensure_ascii=False, indent=2)

    # 2️⃣ Textdatei (für Debug / Export)
    text_feedback = generate_feedback_text(feedback_json)
    with open(os.path.join(OUTPUT, "feedback.txt"), "w", encoding="utf-8") as f:
        f.write(text_feedback)

    # 3️⃣ 🆕 Text-Feedback als JSON fürs Frontend
    feedback_text_json = generate_feedback_text_json(feedback_json)
    with open(os.path.join(OUTPUT, "feedback_text.json"), "w", encoding="utf-8") as f:
        json.dump(feedback_text_json, f, ensure_ascii=False, indent=2)

    print("✅ Feedback erfolgreich erzeugt (JSON + TXT)")
