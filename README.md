# klarTEXT – Backend (Speech AI & API)

> Das Herzstück von klarTEXT: KI-gestützte Aussprache-Analyse und Text-Vereinfachungs-API

Das Backend basiert auf einer hybriden Architektur aus **FastAPI** (Python) und spezialisierten Sprachmodellen wie dem **Montreal Forced Aligner (MFA)**.

---

## 🎯 Kernaufgaben

| Aufgabe | Beschreibung |
|---|---|
| **Phonem-Abgleich** | Präzise Analyse gesprochener Audio-Daten im Vergleich zum Referenztext |
| **Text-Transformation** | Verarbeitung komplexer Sprache in „Leichte Sprache" mittels NLP-Modellen |
| **Sicherheits-Layer** | Verschlüsselte HTTPS-Schnittstelle für den Mikrofon-Zugriff im Browser |

---

## 🚀 Setup & Installation

### 1. Conda Environment (MFA)

Für die phonetische Analyse wird eine spezifische Conda-Umgebung benötigt:

```bash
conda activate mfa
```

### 2. Python Virtual Environment

```bash
# Virtual Env erstellen (falls noch nicht vorhanden)
python -m venv venv

# Aktivieren unter Linux/macOS
source venv/bin/activate

# Aktivieren unter Windows
.\venv\Scripts\activate
```

### 3. Abhängigkeiten installieren

Stelle sicher, dass du dich im Root-Verzeichnis des Backends befindest:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Server starten

### Option A – Standard (HTTP)

Ideal für schnelle Tests der Textvereinfachung ohne Audio-Features:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option B – Mit SSL (HTTPS) ✅ Empfohlen

Moderne Browser erlauben Mikrofon-Zugriff nur über HTTPS. Daher wird dieser Modus für die Entwicklung empfohlen.

**Schritt 1:** Selbstsigniertes Zertifikat generieren

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

**Schritt 2:** Server mit SSL starten

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile ./key.pem --ssl-certfile ./cert.pem --reload
```

> [!TIP]
> Bei selbstsignierten Zertifikaten musst du `https://localhost:8000` einmal im Browser aufrufen und die Sicherheitswarnung manuell akzeptieren (`Erweitert` → `Weiter zu localhost`), damit das Frontend die API erreichen darf.

---

## 🏗️ Technische Details

- **Framework:** FastAPI (Python) – performante, asynchrone API-Endpunkte
- **Audio-Engine:** Montreal Forced Aligner (MFA) – Zeitstempel-Analyse einzelner Laute
- **Schnittstelle:** REST-API auf Standardport `8000`

---

## 🔒 Sicherheitshinweis – `.gitignore`

Die generierten Zertifikatsdateien sollten **niemals** in ein öffentliches Repository eingecheckt werden. Füge folgende Einträge zu deiner `.gitignore` hinzu:

```gitignore
# SSL-Zertifikate
*.pem
key.pem
cert.pem
```

---

## 📄 Lizenz

Dieses Projekt steht unter der **[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.de.html)**.
