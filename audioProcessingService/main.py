from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import logging

from audio_processor import process_audio
from transcription.transcription_service import transcribe_and_create_lab
from mfa.test_alignment import runMFAall
from feedback.feedback_service import runFeedback

# --- Logging konfigurieren ---
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


# --- Directories ---
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

AUDIO_INPUT_BASE = os.path.join(os.getcwd(), "audio_input")
os.makedirs(AUDIO_INPUT_BASE, exist_ok=True)


# --- FastAPI App ---
app = FastAPI(
    title="Audio Processing Service",
    description="Normalize & clean audio files",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Upload Endpoint
# -----------------------------
@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".wav", ".mp3", ".webm")):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    request_id = str(uuid.uuid4())
    request_dir = os.path.join(AUDIO_INPUT_BASE, request_id)
    os.makedirs(request_dir, exist_ok=True)

    target_file_path = os.path.join(request_dir, "test.wav")

    with open(target_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        print(f"🚀 Starte Abfrage-Durchlauf ID: {request_id}")

        print("Dir: " + request_dir)

        # --- Modul 1: Audio verarbeiten ---
        # WICHTIG: process_audio sollte die Datei im request_dir verarbeiten
        audio_info = process_audio(target_file_path)
        actual_path = audio_info["audio_path"]
        print(f"✅ Audio vorbereitet: {actual_path}")

        # --- Modul 2: Transkription erstellen ---
        # Erstellt die .lab Datei direkt neben der .wav im UUID-Ordner
        erkannter_text = transcribe_and_create_lab(actual_path)
        print(f"✅ Text extrahiert: {erkannter_text}")

        # --- Modul 3: MFA Alignment ---
        # Wir geben den spezifischen UUID-Ordner an
        # alignment_out bekommt ebenfalls einen UUID-Unterordner
        alignment_out = os.path.join(os.getcwd(), "audio_input", request_id)
        os.makedirs(alignment_out, exist_ok=True)
        
        # Wir übergeben das Verzeichnis (dirname), nicht die Datei
        runMFAall(os.path.dirname(actual_path), alignment_out)
        print(f"✅ MFA Alignment abgeschlossen in: {alignment_out}")

        # --- Modul 4: Feedback ---
        # Hier musst du ggf. die Pfade an runFeedback übergeben
        runFeedback(alignment_out, erkannter_text) 

    except Exception as e:
        print(f"❌ Fehler im Ablauf: {e}")
    
    finally:
        pass

    return request_id # JSONResponse(content=result)



# -----------------------------
# Fallback Endpoint
# -----------------------------
@app.get("/get-audio-results/{request_id}")
async def get_audio_results(request_id: str):
    
    request_dir = os.path.join(AUDIO_INPUT_BASE, request_id)
    
    if not os.path.exists(request_dir):
        raise HTTPException(status_code=404, detail="Result not found")

    feedback_path = os.path.join(request_dir, "feedback.json")

    if not os.path.isfile(feedback_path):
        raise HTTPException(status_code=404, detail="Feedback not ready")

    try:
        import json
        with open(feedback_path, "r", encoding="utf-8") as f:
            feedback_data = json.load(f)

        return JSONResponse(content=feedback_data)

    except Exception as e:
        logger.error(f"Error loading feedback for {request_id}: {e}")
        raise HTTPException(status_code=500, detail="Error loading feedback")

