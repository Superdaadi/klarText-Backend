# ⚡ Quickstart Guide

Starte in 5 Minuten mit dem intelligenten Aussprache-Feedback-System!

## 📥 Setup (30 Sekunden)

```bash
# 1. Dateien in dein Projekt kopieren
# Benötigt: config.json, *.py Dateien

# 2. Test-Analyse durchführen
python main.py test_gop_data.json
```

Fertig! Das war's schon. 🎉

---

## 🎯 Erste Schritte

### 1. Mit eigenen Daten arbeiten

```bash
# Deine GOP-Daten analysieren
python main.py deine_gop_daten.json

# Mit Custom Output-Ordner
python main.py deine_gop_daten.json --output-dir ./mein_feedback
```

### 2. Ergebnisse anschauen

Nach der Analyse findest du:

```
feedback_output/
├── feedback.json      ← Für dein Frontend
├── feedback.txt       ← Menschenlesbares Feedback
├── analysis.json      ← Detaillierte Analyse
└── heatmap.json       ← Für Visualisierung
```

### 3. Ins Frontend integrieren

**React Beispiel:**

```jsx
import { useEffect, useState } from 'react';

function PronunciationFeedback() {
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    fetch('/api/feedback.json')
      .then(r => r.json())
      .then(setFeedback);
  }, []);

  if (!feedback) return <div>Lädt...</div>;

  return (
    <div>
      <h1>{feedback.headline}</h1>
      <div className="score">{feedback.overall_score}/100</div>
      
      <h2>Stärken</h2>
      {feedback.strengths.map(s => (
        <div key={s.phoneme}>
          {s.phoneme}: {s.score}/100
        </div>
      ))}
      
      <h2>Übungsbedarf</h2>
      {feedback.weaknesses.map(w => (
        <div key={w.phoneme}>
          <strong>{w.phoneme}</strong>: {w.score}/100
          <p>{w.tip}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## 🎛️ Adaptives Lernen nutzen

Das System lernt von User-Feedback:

```bash
# User findet Feedback zu streng?
python main.py daten.json --user-feedback too_strict

# Zu locker?
python main.py daten.json --user-feedback too_loose

# Genau richtig?
python main.py daten.json --user-feedback just_right
```

Nach **3 Feedbacks** passt sich das System automatisch an! 🤖

---

## 🔧 Quick-Anpassungen

### Schwellenwerte ändern

Bearbeite `config.json`:

```json
{
  "adaptive_thresholds": {
    "current": {
      "excellent": -26.0,  // ← Strenger: -24.0, Lockerer: -28.0
      "good": -28.0,
      "ok": -30.5,
      "needs_work": -33.0
    }
  }
}
```

### Feedback-Stil anpassen

```json
{
  "feedback_style": {
    "strictness": 0.5,        // 0.0 = sehr locker, 1.0 = sehr streng
    "positivity_bias": 0.3,   // Mehr positive Verstärkung
    "encouragement": true     // Ermutigungen aktiviert
  }
}
```

---

## 📊 Wichtigste Features

| Feature | Beschreibung |
|---------|-------------|
| **AI-Analyse** | Intelligente Bewertung statt nur GOP-Schwellenwerte |
| **Relativ** | Vergleicht Phoneme untereinander |
| **Adaptiv** | Lernt aus User-Feedback |
| **Kontext** | Berücksichtigt Schwierigkeit & Position |
| **Motivierend** | Fokus auf Fortschritt, nicht Perfektion |

---

## 🐛 Troubleshooting

**Problem:** "FileNotFoundError: config.json"
```bash
# Lösung: Stelle sicher, dass config.json im selben Ordner ist
ls config.json
```

**Problem:** "JSON decode error"
```bash
# Lösung: Validiere dein Input-JSON
python -m json.tool deine_daten.json
```

**Problem:** Feedback zu streng/locker
```bash
# Lösung: Nutze --user-feedback
python main.py daten.json --user-feedback too_strict
```

---

## 🚀 Fortgeschrittene Nutzung

### In Python-Code integrieren

```python
from analyzer import IntelligentAnalyzer
from feedback_generator import FeedbackGenerator
import json

# Daten laden
with open("gop.json") as f:
    data = json.load(f)

# Analysieren
analyzer = IntelligentAnalyzer()
analysis = analyzer.analyze(data)

# Feedback generieren
generator = FeedbackGenerator()
feedback = generator.generate_feedback(analysis)

# Verwenden
print(f"Score: {feedback['overall_score']}/100")
```

### Batch-Processing

```bash
# Mehrere Dateien verarbeiten
for file in *.json; do
    python main.py "$file" --output-dir "results/$file" --quiet
done
```

---

## 📚 Weiterführende Infos

- **Vollständige Doku**: Siehe `README.md`
- **Demo-Skript**: `python demo.py` für interaktive Demos
- **Konfiguration**: Siehe `config.json` Kommentare

---

## 💡 Pro-Tipps

1. **Starte mit default settings** - Das System ist bereits gut kalibriert
2. **Sammle User-Feedback** - Nach 10-20 Analysen wird das System optimal
3. **Nutze die Heatmap** - Perfekt für visuelle Learner
4. **Kombiniere mit Audio** - Zeige den Usern, wo genau Probleme sind

---

## ✨ Nächste Schritte

1. ✅ Erste Analyse mit `test_gop_data.json` durchführen
2. ✅ Feedback-Dateien im Frontend einbinden
3. ✅ User-Feedback sammeln und System trainieren
4. ✅ Eigene Tipps & Übungen in `feedback_generator.py` hinzufügen

---

**Viel Erfolg! 🚀**

Bei Fragen: Schau in die `README.md` oder teste mit `demo.py`
