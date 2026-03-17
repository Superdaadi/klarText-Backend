# 📁 Datei-Übersicht

## Core System Files

### `config.json`
**Zweck:** Zentrale Konfiguration für das gesamte System  
**Enthält:**
- Adaptive Schwellenwerte (current, min, max bounds)
- Phonem-Schwierigkeitsgrade (easy, medium, hard, very_hard)
- Feedback-Stil-Einstellungen
- User-Präferenzen und Lern-History

**Wird bearbeitet:** Automatisch durch adaptive Schwellenwerte, manuell für Anpassungen

---

### `adaptive_thresholds.py`
**Zweck:** Verwaltet selbstlernende Schwellenwerte  
**Klasse:** `AdaptiveThresholds`

**Hauptfunktionen:**
- `get_thresholds()` - Gibt aktuelle Schwellenwerte zurück
- `record_user_feedback()` - Zeichnet User-Feedback auf
- `_adjust_thresholds()` - Passt Schwellenwerte automatisch an
- `get_difficulty_multiplier()` - Gibt Schwierigkeits-Bonus für Phoneme

**Wird verwendet von:** `analyzer.py`, `main.py`

---

### `analyzer.py`
**Zweck:** Herzstück der AI-gestützten Analyse  
**Klasse:** `IntelligentAnalyzer`

**Hauptfunktionen:**
- `analyze()` - Haupt-Analyse-Funktion
- `_calculate_phoneme_stats()` - Statistiken pro Phonem
- `_calculate_global_stats()` - Globale Vergleichswerte
- `_analyze_context()` - Kontext (Duration, Koartikulation)
- `_rate_phonemes_intelligently()` - Multi-dimensionale Bewertung
- `_calculate_final_score()` - Finaler 0-100 Score

**Analyse-Pipeline:**
```
GOP-Daten
  ↓
Phonem-Statistiken (avg, std, count)
  ↓
Globale Statistiken (für Relativvergleich)
  ↓
Kontext-Analyse (Duration, Nachbarn)
  ↓
Intelligente Bewertung (absolut + relativ + Konsistenz)
  ↓
Finaler Score (0-100) mit Schwierigkeits-Bonus
```

**Wird verwendet von:** `main.py`, dein Code

---

### `feedback_generator.py`
**Zweck:** Generiert nutzerfreundliches, motivierendes Feedback  
**Klasse:** `FeedbackGenerator`

**Enthält:**
- `PHONEME_TIPS` - Artikulationstipps für alle deutschen Phoneme
- `PHONEME_EXERCISES` - Praktische Übungen (Minimalpaare)

**Hauptfunktionen:**
- `generate_feedback()` - Haupt-Generator
- `_generate_headline()` - Motivierende Überschrift
- `_generate_summary()` - Zusammenfassung
- `_generate_encouragement()` - Ermutigungen
- `_generate_weakness_feedback()` - Detailliertes Feedback für Schwächen
- `_generate_exercises()` - Passende Übungen
- `generate_text_feedback()` - Formatiert für Menschen lesbar

**Output-Format:** Strukturiertes JSON + lesbarer Text

**Wird verwendet von:** `main.py`, dein Code

---

### `main.py`
**Zweck:** Hauptprogramm & Command-Line Interface  
**Orchestriert:** Alle anderen Module

**Workflow:**
```bash
main.py input.json
  ↓
1. Lade GOP-Daten
2. Optional: Verarbeite User-Feedback
3. Analysiere mit IntelligentAnalyzer
4. Generiere Feedback mit FeedbackGenerator
5. Speichere Ergebnisse (JSON, TXT, Heatmap)
6. Zeige Zusammenfassung
```

**Funktionen:**
- `load_gop_data()` - Lädt JSON
- `save_results()` - Speichert alle Outputs
- `generate_heatmap()` - Erstellt Visualisierungsdaten
- `print_summary()` - Konsolen-Ausgabe
- `main()` - CLI-Argumente & Orchestrierung

**Command-Line Argumente:**
- `input_file` - GOP-JSON (required)
- `--output-dir` - Wohin speichern (default: ./feedback_output)
- `--config` - Config-Pfad (default: config.json)
- `--user-feedback` - too_strict | too_loose | just_right
- `--quiet` - Keine Konsolen-Ausgabe

---

## Support Files

### `test_gop_data.json`
**Zweck:** Beispiel-Daten für Tests  
**Enthält:** 91 Phoneme aus deinem Original-Input  
**Format:** Array von {phoneme, start, end, gop_score}

**Verwendung:**
```bash
python main.py test_gop_data.json
```

---

### `demo.py`
**Zweck:** Interaktives Demo-Skript  
**Features:**
- Demo 1: Basis-Analyse
- Demo 2: Adaptives Lernen
- Demo 3: Feedback-Vergleich
- Demo 4: Output-Formate
- Demo 5: Heatmap-Daten
- Demo 6: API-Verwendung

**Verwendung:**
```bash
python demo.py
# Dann Menü-Option wählen
```

---

### `README.md`
**Zweck:** Vollständige Dokumentation  
**Enthält:**
- Features & Capabilities
- Installation & Setup
- Verwendungs-Beispiele
- Input/Output-Formate
- Konfigurations-Details
- Erweiterungs-Anleitungen
- Troubleshooting

**Für:** Entwickler, die das System verstehen/erweitern wollen

---

### `QUICKSTART.md`
**Zweck:** Schneller Einstieg in 5 Minuten  
**Enthält:**
- Setup in 30 Sekunden
- Erste Schritte
- Frontend-Integration
- Quick-Anpassungen
- Troubleshooting

**Für:** Nutzer, die sofort loslegen wollen

---

## Output Files (generiert)

### `feedback_output/feedback.json`
**Format:** Strukturiertes JSON für Frontend  
**Enthält:**
- headline, summary, encouragement
- overall_score, grade
- strengths[] (Top-Performer)
- weaknesses[] (mit Tips & Übungen)
- exercises[]
- insights[]
- metadata

**Verwendung:** Direktes Laden im Frontend

---

### `feedback_output/feedback.txt`
**Format:** Menschenlesbarer Text  
**Enthält:** Gleiche Infos wie JSON, aber formatiert  
**Verwendung:** Schnelle Review, Export, Debugging

---

### `feedback_output/analysis.json`
**Format:** Detaillierte technische Analyse  
**Enthält:**
- Alle Phonem-Scores mit Details
- Globale Statistiken
- Kontext-Insights
- Raw GOP-Daten

**Verwendung:** Debugging, Entwicklung, tiefe Analyse

---

### `feedback_output/heatmap.json`
**Format:** Zeit-basierte Visualisierungsdaten  
**Enthält:** Array von {phoneme, start, end, score, color}  
**Verwendung:** Timeline-Visualisierung im Frontend

```javascript
// Beispiel: React Timeline
{heatmap.map(item => (
  <div 
    style={{
      left: item.start * scale,
      width: (item.end - item.start) * scale,
      backgroundColor: item.color
    }}
  />
))}
```

---

## Datenfluss-Diagramm

```
┌─────────────────┐
│  GOP-JSON       │  (Input)
│  Input-Datei    │
└────────┬────────┘
         │
         v
┌─────────────────┐
│  main.py        │  (Orchestrator)
└────────┬────────┘
         │
         ├──> adaptive_thresholds.py (Schwellenwerte laden)
         │
         v
┌─────────────────┐
│  analyzer.py    │  (AI-Analyse)
└────────┬────────┘
         │
         v
┌─────────────────┐
│  feedback_      │  (Feedback-Generierung)
│  generator.py   │
└────────┬────────┘
         │
         v
┌─────────────────────────────────────┐
│  Output Files                       │
│  • feedback.json                    │
│  • feedback.txt                     │
│  • analysis.json                    │
│  • heatmap.json                     │
└─────────────────────────────────────┘
```

---

## Wichtige Konzepte

### 1. **Multi-dimensionaler Score**
```
Final Score = 
  40% Absolute Rating (GOP vs Thresholds)
+ 35% Relative Score (vs andere Phoneme)
+ 25% Consistency Score (niedrige STD)
+ Difficulty Bonus (für harte Phoneme)
```

### 2. **Adaptive Schwellenwerte**
- Sammelt User-Feedback (too_strict, too_loose, just_right)
- Nach 3 Feedbacks: Automatische Anpassung
- Bleibt innerhalb definierter Bounds
- Learning Rate: 0.1 (konfigurierbar)

### 3. **Phonem-Schwierigkeit**
- easy: a, m, n, l, ... (Multiplikator: 0.9)
- medium: t, d, s, z, ... (Multiplikator: 1.0)
- hard: ʁ, ç, x, ... (Multiplikator: 1.2)
- very_hard: tʃ, ʒ, ŋ, ... (Multiplikator: 1.4)

### 4. **Kontext-Analyse**
- Duration Outliers (zu lang/kurz)
- Koartikulations-Effekte (s vor t schwieriger)
- Position im Wort (future feature)

---

## Erweiterungspunkte

**Neue Phoneme hinzufügen:**
→ `feedback_generator.py`: PHONEME_TIPS & PHONEME_EXERCISES

**Bewertungs-Logik ändern:**
→ `analyzer.py`: `_calculate_final_score()`

**Feedback-Stil anpassen:**
→ `feedback_generator.py`: `_generate_*()` Methoden

**Schwellenwerte ändern:**
→ `config.json`: adaptive_thresholds.current

**Neue Output-Formate:**
→ `main.py`: `save_results()`

---

## Wartung

**Config zurücksetzen:**
```bash
# Editiere config.json manuell oder
git checkout config.json
```

**Tests durchführen:**
```bash
python main.py test_gop_data.json
python demo.py  # Wähle Option 6 für API-Tests
```

**Logs/Debug:**
```bash
# Verbose Output
python main.py test.json  # (nicht --quiet)

# Nur Analysis anschauen
cat feedback_output/analysis.json | python -m json.tool
```

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 2026-02-14
