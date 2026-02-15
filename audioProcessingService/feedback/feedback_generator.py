"""
Intelligenter Feedback Generator
Erzeugt motivierendes, nutzerfreundliches Feedback
"""

import json
from typing import Dict, List

# Erweiterte Artikulationstipps
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
    "ts": "Explosiv mit t starten, sofort in scharfes s übergehen. Wie in 'Zahn'.",
    "tʃ": "t-Verschluss, dann sch-artiger Reibelaut.",
    "pf": "p-Verschluss, direkt in f überleiten. Wie in 'Pfanne'.",

    # ─── Frikative ───
    "f": "Unterlippe sanft an obere Zähne, Luft gleichmäßig.",
    "v": "Wie f, aber stimmhaft.",
    "s": "Luftstrom bündeln, Zunge nah am Zahndamm, kein ‚sch'. Wie in 'lassen'.",
    "z": "Wie s, aber stimmhaft.",
    "ʃ": "Zunge weiter zurückziehen, Lippen leicht runden. Wie 'sch' in 'schön'.",
    "ʒ": "Wie ʃ, aber stimmhaft.",
    "ç": "Sehr weich, Zunge flach Richtung Gaumen. Wie 'ch' in 'ich'.",
    "x": "Rau, Zungenrücken nahe am weichen Gaumen. Wie 'ch' in 'Bach'.",
    "h": "Sehr leicht, nur Luft – kein harter Ansatz.",

    # ─── Nasale ───
    "m": "Lippen geschlossen, Luft durch die Nase.",
    "n": "Zungenspitze an den Zähnen, Luft nasal.",
    "ŋ": "Zungenrücken am Gaumen, kein n hörbar davor. Wie 'ng' in 'singen'.",

    # ─── Liquide & Approximanten ───
    "l": "Zungenspitze an den Zahndamm, Seiten offen.",
    "ʁ": "Im Rachen gebildet, nicht gerollt. Deutsches 'r'.",
    "j": "Zunge hoch vorne, wie kurzes ‚i'. Wie 'j' in 'ja'.",
    "ʋ": "Zwischen w und v, Lippen nur leicht gerundet.",

    # ─── Vokale kurz ───
    "ɪ": "Kurz und locker, nicht Richtung ‚iː' ziehen. Wie 'i' in 'bitte'.",
    "ʏ": "Kurz, Lippen gerundet, Zunge vorne. Wie 'ü' in 'Müller'.",
    "ʊ": "Kurz, Lippen leicht gerundet, nicht zu offen. Wie 'u' in 'Mutter'.",
    "ɛ": "Offener als ‚e', Kiefer leicht senken. Wie 'e' in 'Bett'.",
    "œ": "Kurz, offen, Lippen gerundet. Wie 'ö' in 'können'.",
    "ɔ": "Kurz, rund, nicht zu weit öffnen. Wie 'o' in 'Wort'.",
    "a": "Kurz, zentral, Mund offen. Wie 'a' in 'Mann'.",

    # ─── Vokale lang ───
    "iː": "Lang, gespannt, Zunge hoch vorne. Wie 'ie' in 'lieben'.",
    "yː": "Lang, gespannt, Lippen stark gerundet. Wie 'ü' in 'Tür'.",
    "uː": "Lang, gespannt, Lippen gerundet. Wie 'u' in 'Blume'.",
    "eː": "Lang, geschlossen, ruhig halten. Wie 'e' in 'Leben'.",
    "øː": "Lang, gespannt, Lippen gerundet. Wie 'ö' in 'schön'.",
    "oː": "Lang, rund, gleichmäßig. Wie 'o' in 'Boot'.",
    "ɛː": "Lang und offen, ruhig tragen. Wie 'ä' in 'Käse'.",
    "aː": "Lang halten, Mund weit öffnen. Wie 'a' in 'Vater'.",

    # ─── Reduzierte Vokale ───
    "ə": "Sehr kurz, neutral, kaum Mundbewegung. Schwa-Laut.",
    "ɐ": "Tiefer als schwa, leicht offen. Wie '-er' in 'Mutter'.",

    # ─── Diphthonge ───
    "aɪ": "Klarer Gleitlaut von a Richtung i. Wie 'ei' in 'Eis'.",
    "aj": "Klarer Gleitlaut von a Richtung i. Wie 'ei' in 'Eis'.",
    "aʊ": "Von offenem a zu rundem u. Wie 'au' in 'Haus'.",
    "ɔʏ": "Von rundem o Richtung ü. Wie 'eu' in 'Deutsch'."
}

PHONEME_EXERCISES = {
    "s": "Minimalpaare: sie – schie – see | Zungenübung: s-s-s (Luftstrom bündeln)",
    "ç": "ich – nicht – mich – welche | Achte auf die weiche Position",
    "ʃ": "schon – Schule – sprechen | Lippen leicht runden",
    "t": "Tag – Tee – bitte | Kurz und präzise, kein Nachhallen",
    "tʰ": "Tisch – Tat – Tier | Leichter Luftstoß, nicht übertreiben",
    "ʁ": "rot – Brot – richtig | Im Rachen, nicht rollen",
    "ts": "Zeit – Zahl – setzen | Fließender Übergang t→s",
    "ɛ": "Bett – wenn – essen | Mund etwas weiter öffnen als bei 'e'",
    "ɪ": "bitte – mit – Tisch | Kurz halten, nicht zu 'iː'",
    "aː": "Vater – Bahn – Staat | Lang und offen halten",
}






class FeedbackGenerator:
    def __init__(self, config_path: str = "feedback/config.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.style = self.config["feedback_style"]

        # Fallback-Werte, falls die Config unvollständig ist
        self.rating_thresholds = self.style.get("rating_thresholds", {
            "excellent": 85,
            "good": 75,
            "solid": 65,
            "developing": 55
        })
    
    def generate_feedback(self, analysis: Dict) -> Dict:
        """
        Generiert umfassendes Feedback aus der Analyse
        
        Returns:
            Dict mit verschiedenen Feedback-Formaten
        """
        overall = analysis["overall"]
        phonemes = analysis["phonemes"]

        print("Allgemein: ", overall)
        
        # Identifiziere Top Stärken und Schwächen
        strengths = [p for p in phonemes if p["final_score"] >= 75][-5:]  # Top 5
        weaknesses = [p for p in phonemes if p["needs_practice"]][:5]  # Worst 5
        
        # Generiere Texte
        headline = self._generate_headline(overall)
        summary = self._generate_summary(overall, len(strengths), len(weaknesses))
        encouragement = self._generate_encouragement(overall)
        
        # Detailliertes Feedback für Schwächen
        detailed_weaknesses = self._generate_weakness_feedback(weaknesses)
        
        # Übungen generieren
        exercises = self._generate_exercises(weaknesses)
        
        # Fortschritts-Insights
        insights = self._generate_insights(analysis)
        
        return {
            "headline": headline,
            "summary": summary,
            "overall_score": overall["weighted_score"],
            "grade": overall["grade"],
            "encouragement": encouragement,
            "strengths": self._format_strengths(strengths),
            "weaknesses": detailed_weaknesses,
            "exercises": exercises,
            "insights": insights,
            "metadata": {
                "total_phonemes": overall["total_phonemes"],
                "avg_gop": overall["avg_gop"],
                "distribution": {
                    "excellent": overall["excellent_count"],
                    "good": overall["good_count"],
                    "ok": overall["ok_count"],
                    "needs_work": overall["needs_work_count"]
                }
            }
        }
    
    def _generate_headline(self, overall: Dict) -> str:
        """Generiert motivierende Überschrift basierend auf Config-Thresholds"""
        score = overall["weighted_score"]
        grade = overall["grade"]
        rt = self.style["rating_thresholds"] # Zugriff auf neue Config
        
        if score >= rt["excellent"]:
            return f"🌟 Ausgezeichnet! (Note: {grade})"
        elif score >= rt["good"]:
            return f"💪 Sehr gut! (Note: {grade})"
        elif score >= rt["solid"]:
            return f"👍 Gute Leistung! (Note: {grade})"
        elif score >= rt["developing"]:
            return f"🚀 Solide Basis! (Note: {grade})"
        else:
            return f"📈 Viel Potenzial! (Note: {grade})"
    

    def _generate_summary(self, overall: Dict, strengths_count: int, weaknesses_count: int) -> str:
        """Generiert Zusammenfassung basierend auf Config-Thresholds"""
        score = overall["weighted_score"]
        rt = self.style["rating_thresholds"]
        
        # Grundaussage
        if score >= rt["good"]:
            base = "Deine Aussprache ist schon sehr gut!"
        elif score >= rt["solid"]:
            base = "Du hast eine solide Aussprache!"
        elif score >= rt["developing"]:
            base = "Du bist auf einem guten Weg!"
        else:
            base = "Du hast eine gute Grundlage, auf der du aufbauen kannst!"
        
        # Details
        details = f" Von {overall['total_phonemes']} analysierten Lauten "
        
        if overall["excellent_count"] + overall["good_count"] > overall["total_phonemes"] / 2:
            details += f"hast du {overall['excellent_count'] + overall['good_count']} bereits sehr gut gemeistert."
        else:
            details += f"gibt es bei {weaknesses_count} noch Verbesserungspotenzial."
        
        return base + details
    
    
    def _generate_encouragement(self, overall: Dict) -> str:
        """Generiert motivierende Ermutigung"""
        score = overall["weighted_score"]
        
        encouragements = {
            "high": [
                "Beeindruckend! Mit etwas Feinschliff könntest du muttersprachliches Niveau erreichen.",
                "Weiter so! Du hast die schwierigsten Teile bereits gemeistert.",
                "Fantastisch! Konzentriere dich jetzt auf die Details für den letzten Schliff."
            ],
            "medium": [
                "Super Fortschritt! Mit gezieltem Üben wirst du schnell besser.",
                "Du machst das gut! Die Basics sitzen, jetzt kommt die Feinarbeit.",
                "Toll! Bleib dran – Aussprache ist wie ein Muskel, der trainiert werden muss."
            ],
            "low": [
                "Keine Sorge – jeder fängt mal an! Mit etwas Übung wirst du schnelle Erfolge sehen.",
                "Gut, dass du übst! Die ersten Schritte sind die wichtigsten.",
                "Prima, dass du dabei bist! Aussprache verbessert sich mit jeder Übung."
            ]
        }
        
        if score >= 75:
            import random
            return random.choice(encouragements["high"])
        elif score >= 60:
            import random
            return random.choice(encouragements["medium"])
        else:
            import random
            return random.choice(encouragements["low"])
    
    def _format_strengths(self, strengths: List[Dict]) -> List[Dict]:
        """Formatiert Stärken für Output"""
        return [
            {
                "phoneme": s["phoneme"],
                "score": s["final_score"],
                "count": s["count"],
                "label": "Sehr gut" if s["final_score"] >= 85 else "Gut",
                "consistency": "Sehr konsistent" if s["consistency_score"] >= 80 else "Konsistent"
            }
            for s in strengths
        ]
    
    def _generate_weakness_feedback(self, weaknesses: List[Dict]) -> List[Dict]:
        """Generiert detailliertes Feedback für Schwächen"""
        feedback = []
        
        for w in weaknesses:
            phoneme = w["phoneme"]
            score = w["final_score"]
            
            # Basisinfo
            item = {
                "phoneme": phoneme,
                "score": score,
                "count": w["count"],
                "difficulty": w["difficulty"],
                "consistency": w["consistency_score"]
            }
            
            # Tipp
            if phoneme in PHONEME_TIPS:
                item["tip"] = PHONEME_TIPS[phoneme]
            else:
                item["tip"] = "Achte auf eine klare, kontrollierte Artikulation."
            
            # Spezifische Hinweise
            if w["consistency_score"] < 50:
                item["note"] = "⚠️ Die Aussprache variiert stark – übe für mehr Konstanz."
            elif w["difficulty"] in ["hard", "very_hard"]:
                item["note"] = f"💡 '{phoneme}' ist ein anspruchsvoller Laut im Deutschen – das braucht Zeit!"
            else:
                item["note"] = "📚 Mit gezielter Übung schnell verbesserbar."
            
            feedback.append(item)
        
        return feedback
    
    def _generate_exercises(self, weaknesses: List[Dict]) -> List[Dict]:
        """Generiert passende Übungen"""
        exercises = []
        
        for w in weaknesses[:3]:  # Top 3 Schwächen
            phoneme = w["phoneme"]
            
            if phoneme in PHONEME_EXERCISES:
                exercises.append({
                    "phoneme": phoneme,
                    "exercise": PHONEME_EXERCISES[phoneme],
                    "priority": "hoch" if w["final_score"] < 45 else "mittel"
                })
        
        return exercises
    
    def _generate_insights(self, analysis: Dict) -> List[str]:
        """Generiert zusätzliche Insights"""
        insights = []
        
        context = analysis.get("context_insights", {})
        
        # Duration Outliers
        if context.get("duration_outliers"):
            too_long = [o for o in context["duration_outliers"] if o["type"] == "too_long"]
            if too_long:
                insights.append(
                    f"⏱️ Einige Laute wurden zu lang gehalten ({len(too_long)}x). "
                    "Achte auf kompakte Artikulation."
                )
        
        # Coarticulation
        if context.get("coarticulation_effects"):
            insights.append(
                "🔗 Einige Lautkombinationen sind besonders anspruchsvoll – "
                "übe diese Übergänge gezielt."
            )
        
        # Schwierige Phoneme
        global_stats = analysis.get("global_stats", {})
        if global_stats:
            range_span = global_stats["best_phoneme_score"] - global_stats["worst_phoneme_score"]
            if range_span > 8:
                insights.append(
                    "📊 Es gibt größere Unterschiede zwischen deinen Lauten – "
                    "konzentriere dich auf die schwächsten."
                )
        
        return insights
    
    def generate_text_feedback(self, feedback_data: Dict) -> str:
        """Generiert lesbaren Text aus Feedback-Daten"""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append(feedback_data["headline"])
        lines.append("=" * 60)
        lines.append("")
        
        # Summary
        lines.append(f"📊 Gesamtscore: {feedback_data['overall_score']}/100")
        lines.append(feedback_data["summary"])
        lines.append("")
        lines.append(f"💬 {feedback_data['encouragement']}")
        lines.append("")
        
        # Strengths
        if feedback_data["strengths"]:
            lines.append("✅ DEINE STÄRKEN")
            lines.append("-" * 60)
            for s in feedback_data["strengths"]:
                lines.append(
                    f"  • {s['phoneme']}: {s['score']:.0f}/100 ({s['label']}) "
                    f"– {s['count']}x erkannt, {s['consistency']}"
                )
            lines.append("")
        
        # Weaknesses
        if feedback_data["weaknesses"]:
            lines.append("📚 ÜBUNGSBEDARF")
            lines.append("-" * 60)
            for w in feedback_data["weaknesses"]:
                lines.append(f"  • {w['phoneme']}: {w['score']:.0f}/100 (Schwierigkeit: {w['difficulty']})")
                lines.append(f"    👉 {w['tip']}")
                lines.append(f"    {w['note']}")
                lines.append("")
        
        # Exercises
        if feedback_data["exercises"]:
            lines.append("🎯 EMPFOHLENE ÜBUNGEN")
            lines.append("-" * 60)
            for ex in feedback_data["exercises"]:
                lines.append(f"  • {ex['phoneme']} (Priorität: {ex['priority']})")
                lines.append(f"    {ex['exercise']}")
                lines.append("")
        
        # Insights
        if feedback_data["insights"]:
            lines.append("💡 ZUSÄTZLICHE HINWEISE")
            lines.append("-" * 60)
            for insight in feedback_data["insights"]:
                lines.append(f"  {insight}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
