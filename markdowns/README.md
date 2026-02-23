# 🎯 Intelligentes Aussprache-Feedback-System

Ein AI-gestütztes System zur Analyse von GOP (Goodness of Pronunciation) Daten mit adaptiven Schwellenwerten und nutzerfreundlichem Feedback.

## 🌟 Features

### 🧠 **AI-gestützte Analyse**
- **Relative Bewertung**: Vergleicht Phoneme untereinander, nicht nur mit absoluten Schwellenwerten
- **Kontextanalyse**: Berücksichtigt Position, Dauer und Nachbar-Phoneme
- **Schwierigkeitsgrad**: Schwere Phoneme (ʁ, ç, etc.) bekommen automatisch mehr Nachsicht
- **Konsistenz-Bewertung**: Bewertet nicht nur die durchschnittliche Qualität, sondern auch die Konsistenz

### 📊 **Intelligente Bewertung**
- **Multi-dimensionaler Score** (0-100):
  - 40% Absolute Bewertung (GOP-Schwellenwerte)
  - 35% Relative Performance (im Vergleich zu anderen Phonemen)
  - 25% Konsistenz (niedrige Standardabweichung = besser)
  - Bonus für schwierige Phoneme

### 🎛️ **Adaptive Schwellenwerte**
- **Selbstlernend**: Passt sich basierend auf User-Feedback an
- **3 Feedback-Typen**:
  - `too_strict` → Schwellenwerte werden lockerer
  - `too_loose` → Schwellenwerte werden strenger
  - `just_right` → Keine Anpassung, aber Bestätigung
- **Bounds**: Schwellenwerte können sich nur innerhalb definierter Grenzen bewegen

### 💬 **Nutzerfreundliches Feedback**
- **Motivierend**: Nicht zu streng, fokussiert auf Fortschritt
- **Konkrete Tipps**: Artikulationshinweise für jedes Phonem
- **Übungen**: Minimalpaare und praktische Übungen
- **Mehrsprachiges Output**: JSON (für Frontend), Text (für Menschen)

---

## 📦 Installation

```bash
# Keine externen Dependencies nötig - pure Python!
# Kopiere einfach alle Dateien in dein Projekt
```

**Benötigte Dateien:**
- `config.json` - Konfiguration und Schwellenwerte
- `adaptive_thresholds.py` - Lernmodul
- `analyzer.py` - AI-Analyse-Engine
- `feedback_generator.py` - Feedback-Generierung
- `main.py` - Hauptprogramm

---

## 🚀 Verwendung

### Basis-Analyse

```bash
python main.py gop_results.json
```

Erzeugt im Ordner `./feedback_output/`:
- `feedback.json` - Strukturiertes Feedback (für Frontend)
- `feedback.txt` - Lesbares Feedback (für Menschen)
- `analysis.json` - Detaillierte Analyse (für Debugging)
- `heatmap.json` - Zeitbasierte Visualisierungsdaten

### Mit Custom Output-Verzeichnis

```bash
python main.py gop_results.json --output-dir ./my_feedback
```

### User-Feedback geben (Adaptives Lernen)

Nach 3 Feedbacks passt das System die Schwellenwerte automatisch an:

```bash
# Feedback war zu streng
python main.py gop_results.json --user-feedback too_strict

# Feedback war zu locker
python main.py gop_results.json --user-feedback too_loose

# Feedback war genau richtig
python main.py gop_results.json --user-feedback just_right
```

### Stille Ausführung (für Batch-Processing)

```bash
python main.py gop_results.json --quiet
```

---

## 📋 Input-Format

Das System erwartet JSON-Daten im folgenden Format:

```json
[
  {
    "phoneme": "tʰ",
    "start": 0.0,
    "end": 0.04,
    "gop_score": -26.039
  },
  {
    "phoneme": "ɛ",
    "start": 0.04,
    "end": 0.15,
    "gop_score": -26.8306
  }
]
```

**Felder:**
- `phoneme` (string): IPA-Symbol des Phonems
- `start` (float): Startzeit in Sekunden
- `end` (float): Endzeit in Sekunden
- `gop_score` (float): GOP-Score (typisch zwischen -20 und -35)

---

## 📤 Output-Format

### 1. **feedback.json** (für Frontend)

```json
{
  "headline": "👍 Gute Leistung! (Note: C)",
  "summary": "Du hast eine solide Aussprache!...",
  "overall_score": 71.6,
  "grade": "C",
  "encouragement": "Super Fortschritt!...",
  "strengths": [
    {
      "phoneme": "tʰ",
      "score": 92.9,
      "count": 5,
      "label": "Sehr gut",
      "consistency": "Konsistent"
    }
  ],
  "weaknesses": [
    {
      "phoneme": "ç",
      "score": 40.6,
      "count": 3,
      "difficulty": "hard",
      "consistency": 81.3,
      "tip": "Sehr weich, Zunge flach Richtung Gaumen...",
      "note": "💡 'ç' ist ein anspruchsvoller Laut..."
    }
  ],
  "exercises": [
    {
      "phoneme": "ç",
      "exercise": "ich – nicht – mich – welche...",
      "priority": "hoch"
    }
  ],
  "insights": [
    "🔗 Einige Lautkombinationen sind besonders anspruchsvoll..."
  ],
  "metadata": {
    "total_phonemes": 17,
    "avg_gop": -27.9,
    "distribution": {
      "excellent": 5,
      "good": 6,
      "ok": 2,
      "needs_work": 4
    }
  }
}
```

### 2. **heatmap.json** (für Visualisierung)

```json
[
  {
    "phoneme": "tʰ",
    "start": 0.0,
    "end": 0.04,
    "gop_score": -26.04,
    "score_0_100": 60.3,
    "color": "yellow"
  }
]
```

Farben: `green` (≥75), `yellow` (≥60), `orange` (≥45), `red` (<45)

---

## ⚙️ Konfiguration

Die Datei `config.json` steuert das gesamte System:

### Adaptive Schwellenwerte

```json
{
  "adaptive_thresholds": {
    "enabled": true,
    "learning_rate": 0.1,
    "current": {
      "excellent": -26.0,
      "good": -28.0,
      "ok": -30.5,
      "needs_work": -33.0
    },
    "min_bounds": {
      "excellent": -24.0,
      "good": -26.0,
      "ok": -28.0,
      "needs_work": -31.0
    },
    "max_bounds": {
      "excellent": -28.0,
      "good": -30.0,
      "ok": -33.0,
      "needs_work": -36.0
    }
  }
}
```

**Anpassung:**
- `learning_rate`: Wie schnell sich Schwellenwerte ändern (0.0 - 1.0)
- `current`: Aktuelle Schwellenwerte
- `min_bounds` / `max_bounds`: Erlaubter Bereich für Schwellenwerte

### Phonem-Schwierigkeit

```json
{
  "phoneme_difficulty": {
    "easy": ["a", "m", "n", "l", "iː", "uː"],
    "medium": ["t", "d", "s", "z", "p", "b", ...],
    "hard": ["ʁ", "ç", "x", "ʃ", "ts", "pf", ...],
    "very_hard": ["tʃ", "ʒ", "ŋ", "øː", "yː", "ɐ"]
  }
}
```

Schwere Phoneme bekommen **Bonuspunkte** bei der Bewertung.

### Feedback-Stil

```json
{
  "feedback_style": {
    "strictness": 0.5,
    "positivity_bias": 0.3,
    "detail_level": "medium",
    "encouragement": true
  }
}
```

---

## 🎓 Wie funktioniert die AI-Analyse?

### 1. **Phonem-Statistiken**
Für jedes Phonem wird berechnet:
- Durchschnittlicher GOP
- Standardabweichung (für Konsistenz)
- Häufigkeit
- Dauer

### 2. **Globale Statistiken**
- Bester/schlechtester Phonem-Score
- Median und Mittelwert aller Phoneme
- → Ermöglicht **relative Bewertung**

### 3. **Kontextanalyse**
- Identifiziert zu lange/kurze Phoneme
- Erkennt schwierige Lautkombinationen (z.B. s→t)
- Analysiert Koartikulationseffekte

### 4. **Multi-dimensionale Bewertung**

Für jedes Phonem:

```python
final_score = (
    absolute_rating * 0.40 +    # GOP vs. Schwellenwerte
    relative_score * 0.35 +     # Im Vergleich zu anderen
    consistency_score * 0.25    # Wie konsistent?
) + difficulty_bonus
```

### 5. **Intelligente Feedback-Generierung**
- Identifiziert Top 5 Stärken & Schwächen
- Generiert kontextspezifische Tipps
- Wählt passende Übungen aus
- Erstellt motivierende Nachrichten

---

## 🔧 Erweiterung

### Neue Phoneme hinzufügen

In `feedback_generator.py`:

```python
PHONEME_TIPS = {
    "neues_phonem": "Artikulationshinweis hier...",
}

PHONEME_EXERCISES = {
    "neues_phonem": "Übung hier...",
}
```

Und in `config.json` zur passenden Schwierigkeitsstufe hinzufügen.

### Feedback-Stil anpassen

In `feedback_generator.py` in der `FeedbackGenerator`-Klasse:
- `_generate_headline()` - Überschrift
- `_generate_summary()` - Zusammenfassung
- `_generate_encouragement()` - Ermutigungen

### Eigene Bewertungslogik

In `analyzer.py` in der Methode `_calculate_final_score()`:
```python
def _calculate_final_score(self, ...):
    # Hier kannst du die Gewichtung anpassen
    final = (
        absolute_score * 0.40 +  # ← Ändern
        relative_score * 0.35 +  # ← Ändern
        consistency_score * 0.25 # ← Ändern
    )
```

---

## 🧪 Testing & Debugging

### Analyse-JSON anschauen

Die Datei `analysis.json` enthält alle internen Berechnungen:

```bash
cat feedback_output/analysis.json | python -m json.tool | less
```

### Schwellenwerte zurücksetzen

Bearbeite `config.json` und setze die Werte in `current` zurück.

### Verbose Output

```bash
python main.py test.json  # Zeigt alle Details
```

---

## 📊 Beispiel-Output

```
======================================================================
  👍 Gute Leistung! (Note: C)
======================================================================

📊 Gesamtscore: 71.6/100 (Note: C)

Du hast eine solide Aussprache! Von 17 analysierten Lauten hast du 
11 bereits sehr gut gemeistert.

💬 Super Fortschritt! Mit gezieltem Üben wirst du schnell besser.

✅ DEINE STÄRKEN
------------------------------------------------------------
  • tʰ: 93/100 (Sehr gut) – 5x erkannt, Konsistent
  • ɛ: 84/100 (Gut) – 5x erkannt, Sehr konsistent
  • s: 83/100 (Gut) – 9x erkannt, Sehr konsistent

📚 ÜBUNGSBEDARF
------------------------------------------------------------
  • ç: 41/100 (Schwierigkeit: hard)
    👉 Sehr weich, Zunge flach Richtung Gaumen. Wie 'ch' in 'ich'.
    💡 'ç' ist ein anspruchsvoller Laut im Deutschen – das braucht Zeit!

🎯 EMPFOHLENE ÜBUNGEN
------------------------------------------------------------
  • ç (Priorität: hoch)
    ich – nicht – mich – welche | Achte auf die weiche Position

💡 ZUSÄTZLICHE HINWEISE
------------------------------------------------------------
  🔗 Einige Lautkombinationen sind besonders anspruchsvoll – 
      übe diese Übergänge gezielt.

======================================================================
```

---

## 🤝 Integration mit Frontend

### React Beispiel

```javascript
// Lade Feedback
const response = await fetch('/api/feedback.json');
const feedback = await response.json();

// Zeige Score
<div className="score">
  <h2>{feedback.headline}</h2>
  <div className="score-value">{feedback.overall_score}/100</div>
  <p>{feedback.summary}</p>
</div>

// Zeige Schwächen mit Tipps
{feedback.weaknesses.map(w => (
  <div key={w.phoneme} className="weakness">
    <span className="phoneme">{w.phoneme}</span>
    <span className="score">{w.score}/100</span>
    <p className="tip">{w.tip}</p>
  </div>
))}
```

### Heatmap Visualisierung

```javascript
// Lade Heatmap-Daten
const heatmap = await fetch('/api/heatmap.json').then(r => r.json());

// Visualisiere mit Timeline
heatmap.forEach(item => {
  const width = (item.end - item.start) * scale;
  const left = item.start * scale;
  
  <div 
    style={{
      position: 'absolute',
      left: `${left}px`,
      width: `${width}px`,
      backgroundColor: item.color,
      height: '30px'
    }}
    title={`${item.phoneme}: ${item.score_0_100}/100`}
  />
});
```

---

## 🎯 Roadmap / Verbesserungen

- [ ] Verlaufs-Tracking (Fortschritt über Zeit)
- [ ] Export zu PDF/HTML
- [ ] Multi-Speaker Vergleich
- [ ] Audio-Snippets für Übungen
- [ ] Integration mit TTS für Aussprache-Demos
- [ ] Machine Learning für automatische Schwellenwert-Optimierung
- [ ] Mehrsprachige Tipps (EN, ES, FR, etc.)

---

## 📝 Lizenz

Frei verwendbar für dein Projekt!

---

## 🙋 Support

Bei Fragen oder Problemen:
1. Prüfe die `analysis.json` für Details
2. Schaue in die Config-Datei
3. Teste mit `--quiet` für saubere Logs

---

**Version:** 1.0.0  
**Erstellt mit:** ❤️ und AI
