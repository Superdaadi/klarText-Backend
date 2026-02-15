"""
AI-gestützter Pronunciation Analyzer
Intelligente Analyse mit Kontext und relativer Bewertung
"""

import json
import statistics
from collections import defaultdict
from typing import List, Dict, Tuple
from feedback.adaptive_thresholds import AdaptiveThresholds


class IntelligentAnalyzer:
    def __init__(self, config_path: str = "config.json"):
        self.threshold_manager = AdaptiveThresholds(config_path)
        self.thresholds = self.threshold_manager.get_thresholds()
        
    def analyze(self, gop_data: List[Dict]) -> Dict:
        """
        Hauptanalyse-Funktion mit AI-gestützter Bewertung
        
        Returns:
            Detaillierte Analyse mit relativen und absoluten Scores
        """
        # 1. Grundlegende Statistiken pro Phonem
        phoneme_stats = self._calculate_phoneme_stats(gop_data)
        
        # 2. Globale Statistiken (für relative Bewertung)
        global_stats = self._calculate_global_stats(phoneme_stats)
        
        # 3. Kontextanalyse (Position, Nachbarn)
        context_analysis = self._analyze_context(gop_data)
        
        # 4. Intelligente Bewertung mit Schwierigkeitsgrad
        rated_phonemes = self._rate_phonemes_intelligently(
            phoneme_stats, 
            global_stats,
            context_analysis
        )
        
        # 5. Gesamtbewertung
        overall = self._calculate_overall_score(rated_phonemes, gop_data)
        
        return {
            "overall": overall,
            "phonemes": rated_phonemes,
            "global_stats": global_stats,
            "context_insights": context_analysis,
            "raw_data": gop_data
        }
    
    def _calculate_phoneme_stats(self, gop_data: List[Dict]) -> Dict:
        """Berechnet Statistiken für jedes Phonem"""
        phoneme_groups = defaultdict(list)
        
        for item in gop_data:
            phoneme_groups[item["phoneme"]].append({
                "gop": item["gop_score"],
                "start": item["start"],
                "end": item["end"],
                "duration": item["end"] - item["start"]
            })
        
        stats = {}
        for phoneme, instances in phoneme_groups.items():
            gop_scores = [i["gop"] for i in instances]
            durations = [i["duration"] for i in instances]
            
            stats[phoneme] = {
                "count": len(instances),
                "avg_gop": statistics.mean(gop_scores),
                "std_gop": statistics.stdev(gop_scores) if len(gop_scores) > 1 else 0,
                "min_gop": min(gop_scores),
                "max_gop": max(gop_scores),
                "avg_duration": statistics.mean(durations),
                "instances": instances
            }
        
        return stats
    
    def _calculate_global_stats(self, phoneme_stats: Dict) -> Dict:
        """Berechnet globale Statistiken für relative Bewertung"""
        all_avg_gops = [data["avg_gop"] for data in phoneme_stats.values()]
        
        return {
            "global_mean": statistics.mean(all_avg_gops),
            "global_median": statistics.median(all_avg_gops),
            "global_std": statistics.stdev(all_avg_gops) if len(all_avg_gops) > 1 else 0,
            "best_phoneme_score": max(all_avg_gops),
            "worst_phoneme_score": min(all_avg_gops)
        }
    
    def _analyze_context(self, gop_data: List[Dict]) -> Dict:
        """Analysiert Kontext: Position im Wort, Nachbar-Phoneme"""
        insights = {
            "word_position_analysis": {},
            "coarticulation_effects": [],
            "duration_outliers": []
        }
        
        # Einfache Positions-Analyse (Wortanfang, -mitte, -ende)
        # Hier vereinfacht - könnte erweitert werden mit echten Word-Boundaries
        
        for i, item in enumerate(gop_data):
            # Check für ungewöhnlich lange/kurze Phoneme
            duration = item["end"] - item["start"]
            if duration > 0.3:  # sehr lang
                insights["duration_outliers"].append({
                    "phoneme": item["phoneme"],
                    "duration": round(duration, 3),
                    "position": i,
                    "type": "too_long"
                })
            elif duration < 0.02:  # sehr kurz
                insights["duration_outliers"].append({
                    "phoneme": item["phoneme"],
                    "duration": round(duration, 3),
                    "position": i,
                    "type": "too_short"
                })
            
            # Koartikulations-Effekte (Nachbar-Phoneme beeinflussen sich)
            if i > 0 and i < len(gop_data) - 1:
                prev_phoneme = gop_data[i-1]["phoneme"]
                next_phoneme = gop_data[i+1]["phoneme"]
                
                # Beispiel: s vor t ist schwieriger
                if item["phoneme"] == "s" and next_phoneme in ["t", "tʰ"]:
                    insights["coarticulation_effects"].append({
                        "phoneme": "s",
                        "context": f"{prev_phoneme}-s-{next_phoneme}",
                        "note": "s vor t ist artikulatorisch anspruchsvoll"
                    })
        
        return insights
    
    def _rate_phonemes_intelligently(
        self, 
        phoneme_stats: Dict, 
        global_stats: Dict,
        context_analysis: Dict
    ) -> List[Dict]:
        """
        Intelligente Bewertung mit:
        - Absoluten Schwellenwerten
        - Relativer Performance
        - Schwierigkeitsgrad-Anpassung
        - Konsistenz-Bewertung
        """
        rated = []
        
        for phoneme, stats in phoneme_stats.items():
            # 1. Schwierigkeitsgrad berücksichtigen
            difficulty_multiplier = self.threshold_manager.get_difficulty_multiplier(phoneme)
            adjusted_gop = stats["avg_gop"] * difficulty_multiplier
            
            # 2. Absolute Bewertung
            absolute_rating = self._get_absolute_rating(adjusted_gop)
            
            # 3. Relative Bewertung (im Vergleich zu anderen Phonemen)
            relative_score = self._calculate_relative_score(
                stats["avg_gop"], 
                global_stats
            )
            
            # 4. Konsistenz-Score (niedrige Standardabweichung = gut)
            consistency_score = self._calculate_consistency_score(stats["std_gop"])
            
            # 5. Finaler Score (0-100)
            final_score = self._calculate_final_score(
                absolute_rating,
                relative_score,
                consistency_score,
                difficulty_multiplier
            )
            
            rated.append({
                "phoneme": phoneme,
                "count": stats["count"],
                "avg_gop": round(stats["avg_gop"], 2),
                "adjusted_gop": round(adjusted_gop, 2),
                "std_gop": round(stats["std_gop"], 2),
                "absolute_rating": absolute_rating,
                "relative_score": round(relative_score, 1),
                "consistency_score": round(consistency_score, 1),
                "final_score": round(final_score, 1),
                "difficulty": self._get_difficulty_label(phoneme),
                "needs_practice": final_score < 60
            })
        
        # Sortiere nach final_score (niedrigste zuerst = needs most work)
        rated.sort(key=lambda x: x["final_score"])
        
        return rated
    
    def _get_absolute_rating(self, gop: float) -> str:
        """Gibt absolute Bewertung basierend auf Schwellenwerten"""
        if gop >= self.thresholds["excellent"]:
            return "excellent"
        elif gop >= self.thresholds["good"]:
            return "good"
        elif gop >= self.thresholds["ok"]:
            return "ok"
        else:
            return "needs_work"
    
    def _calculate_relative_score(self, avg_gop: float, global_stats: Dict) -> float:
        """
        Berechnet relative Performance (0-100)
        
        Vergleicht mit dem globalen Durchschnitt und besten/schlechtesten Werten
        """
        global_mean = global_stats["global_mean"]
        best = global_stats["best_phoneme_score"]
        worst = global_stats["worst_phoneme_score"]
        
        # Normalisierung auf 0-100
        if best == worst:
            return 50.0
        
        relative = ((avg_gop - worst) / (best - worst)) * 100
        return max(0, min(100, relative))
    
    def _calculate_consistency_score(self, std_gop: float) -> float:
        """
        Berechnet Konsistenz-Score (0-100)
        
        Niedrige Standardabweichung = hohe Konsistenz = gut
        """
        # Standardabweichung von 0-5 auf Score 100-0 mappen
        max_std = 5.0
        consistency = max(0, (max_std - std_gop) / max_std * 100)
        return consistency
    
    def _calculate_final_score(
        self,
        absolute_rating: str,
        relative_score: float,
        consistency_score: float,
        difficulty_multiplier: float
    ) -> float:
        """
        Berechnet finalen Score (0-100) aus allen Komponenten
        
        Gewichtung:
        - Absolut: 40%
        - Relativ: 35%
        - Konsistenz: 25%
        + Bonus für schwierige Phoneme
        """
        # Absolute Rating zu Score
        absolute_map = {
            "excellent": 95,
            "good": 75,
            "ok": 55,
            "needs_work": 35
        }
        absolute_score = absolute_map[absolute_rating]
        
        # Gewichteter Durchschnitt
        final = (
            absolute_score * 0.40 +
            relative_score * 0.35 +
            consistency_score * 0.25
        )
        
        # Bonus für schwierige Phoneme
        if difficulty_multiplier > 1.0:
            bonus = (difficulty_multiplier - 1.0) * 10
            final = min(100, final + bonus)
        
        return final
    
    def _get_difficulty_label(self, phoneme: str) -> str:
        """Gibt Schwierigkeits-Label für Phonem zurück"""
        difficulty = self.threshold_manager.config["phoneme_difficulty"]
        
        for level, phonemes in difficulty.items():
            if phoneme in phonemes:
                return level
        return "medium"
    
    def _calculate_overall_score(self, rated_phonemes: List[Dict], raw_data: List[Dict]) -> Dict:
        """Berechnet Gesamt-Score und Zusammenfassung"""
        # Gewichteter Durchschnitt (häufigere Phoneme zählen mehr)
        total_count = sum(p["count"] for p in rated_phonemes)
        weighted_score = sum(
            p["final_score"] * p["count"] for p in rated_phonemes
        ) / total_count
        
        # Durchschnittlicher GOP
        avg_gop = statistics.mean([item["gop_score"] for item in raw_data])
        
        # Kategorien zählen
        excellent = sum(1 for p in rated_phonemes if p["absolute_rating"] == "excellent")
        good = sum(1 for p in rated_phonemes if p["absolute_rating"] == "good")
        ok = sum(1 for p in rated_phonemes if p["absolute_rating"] == "ok")
        needs_work = sum(1 for p in rated_phonemes if p["absolute_rating"] == "needs_work")
        
        return {
            "weighted_score": round(weighted_score, 1),
            "avg_gop": round(avg_gop, 2),
            "total_phonemes": len(rated_phonemes),
            "excellent_count": excellent,
            "good_count": good,
            "ok_count": ok,
            "needs_work_count": needs_work,
            "grade": self._calculate_grade(weighted_score)
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Konvertiert Score zu Schulnote basierend auf Config"""
        # Hol dir die Thresholds aus der Config via threshold_manager
        rt = self.threshold_manager.config["feedback_style"].get("rating_thresholds", {
            "excellent": 85,
            "good": 75,
            "solid": 65,
            "developing": 55
        })
        
        if score >= rt["excellent"]:
            return "A"
        elif score >= rt["good"]:
            return "B"
        elif score >= rt["solid"]:
            return "C"
        elif score >= rt["developing"]:
            return "D"
        else:
            return "F"
