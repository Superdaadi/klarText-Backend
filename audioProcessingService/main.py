from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import logging

from audio_processor import process_audio
from phoeme_extraction import extract_phonemes

# --- Logging konfigurieren ---
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.INFO)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title="Audio Processing Service",
    description="Normalize & clean audio files",
    version="1.0.0"
)

@app.post("/process-audio")
async def process_audio_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith((".wav", ".mp3")):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    temp_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # --- Modul 3: Audio verarbeiten ---
        processed_audio = process_audio(temp_path)

        logger.info("M3 done")

        # --- Modul 4: Phonem-Extraktion automatisch ausführen ---
        # phonemes = extract_phonemes(logger, processed_audio["audio_path"])

        result = {
            "processed_audio": processed_audio,
            #"phonemes": phonemes
        }

    finally:
        os.remove(temp_path)

    return JSONResponse(content=result)
