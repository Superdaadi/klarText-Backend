"""
Adaptive Threshold Manager
Passt Schwellenwerte basierend auf User-Feedback an
"""

import json
import os
from datetime import datetime
from typing import Dict, Literal

class AdaptiveThresholds:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Lädt die Konfiguration"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_config(self):
        """Speichert die Konfiguration"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_thresholds(self) -> Dict[str, float]:
        """Gibt die aktuellen Schwellenwerte zurück"""
        return self.config["adaptive_thresholds"]["current"]
    
    def record_user_feedback(self, feedback_type: Literal["too_strict", "too_loose", "just_right"]):
        """
        Zeichnet User-Feedback auf und passt Schwellenwerte an
        
        Args:
            feedback_type: "too_strict" | "too_loose" | "just_right"
        """
        prefs = self.config["user_preferences"]
        
        # Zähler erhöhen
        if feedback_type == "too_strict":
            prefs["feedback_too_strict_count"] += 1
        elif feedback_type == "too_loose":
            prefs["feedback_too_loose_count"] += 1
        else:
            prefs["feedback_just_right_count"] += 1
        
        # Anpassung nur wenn mindestens 3 Feedbacks vorhanden
        total_feedback = (
            prefs["feedback_too_strict_count"] +
            prefs["feedback_too_loose_count"] +
            prefs["feedback_just_right_count"]
        )
        
        if total_feedback >= 3:
            self._adjust_thresholds(feedback_type)
            prefs["last_adjustment"] = datetime.now().isoformat()
            
            # Reset nach Anpassung
            if total_feedback >= 5:
                prefs["feedback_too_strict_count"] = 0
                prefs["feedback_too_loose_count"] = 0
                prefs["feedback_just_right_count"] = 0
        
        self._save_config()
    
    def _adjust_thresholds(self, feedback_type: str):
        """
        Passt die Schwellenwerte an basierend auf Feedback
        """
        adaptive = self.config["adaptive_thresholds"]
        learning_rate = adaptive["learning_rate"]
        current = adaptive["current"]
        min_bounds = adaptive["min_bounds"]
        max_bounds = adaptive["max_bounds"]
        
        adjustment = 0
        
        if feedback_type == "too_strict":
            # Schwellenwerte senken (negativer = strenger bei GOP)
            adjustment = -0.5
        elif feedback_type == "too_loose":
            # Schwellenwerte erhöhen (weniger negativ = lockerer)
            adjustment = 0.5
        else:
            # Keine Anpassung bei "just_right"
            return
        
        # Anpassung mit Bounds-Check
        for key in current.keys():
            new_value = current[key] + adjustment * learning_rate
            # Innerhalb der Bounds halten
            new_value = max(max_bounds[key], min(min_bounds[key], new_value))
            current[key] = round(new_value, 2)
        
        print(f"✅ Schwellenwerte angepasst ({feedback_type}): {current}")
    
    def get_difficulty_multiplier(self, phoneme: str) -> float:
        """
        Gibt einen Schwierigkeits-Multiplikator für ein Phonem zurück
        
        Schwere Phoneme bekommen mehr Nachsicht bei der Bewertung
        """
        difficulty = self.config["phoneme_difficulty"]
        
        if phoneme in difficulty["very_hard"]:
            return 1.4
        elif phoneme in difficulty["hard"]:
            return 1.2
        elif phoneme in difficulty["medium"]:
            return 1.0
        else:  # easy
            return 0.9
    
    def get_strictness(self) -> float:
        """Gibt den aktuellen Strenge-Faktor zurück (0.0 = sehr locker, 1.0 = sehr streng)"""
        return self.config["feedback_style"]["strictness"]
    
    def adjust_strictness(self, delta: float):
        """
        Manuelle Anpassung der Strenge
        
        Args:
            delta: +0.1 für strenger, -0.1 für lockerer
        """
        style = self.config["feedback_style"]
        style["strictness"] = max(0.0, min(1.0, style["strictness"] + delta))
        self._save_config()
