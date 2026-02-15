import os
import uuid
import shutil
from audio_processor import process_audio
from transcription.transcription_service import transcribe_and_create_lab
from mfa.test_alignment import runMFAall
from feedback.feedback_service import runFeedback

if __name__ == "__main__":
    # 1. Setup: Test-Datei definieren
    original_audio = "audio_input/test.wav"
    
    # 2. Einzigartige Request-ID für diesen Testlauf generieren
    test_id = str(uuid.uuid4())
    # Wir erstellen einen Unterordner in 'processed', um MFA zu isolieren
    request_dir = os.path.join(os.getcwd(), "audio_input", test_id)
    os.makedirs(request_dir, exist_ok=True)
    
    # Kopiere die Testdatei in den UUID-Ordner (simuliert den Upload)
    test_path = os.path.join(request_dir, "test.wav")
    shutil.copy2(original_audio, test_path)

    try:
        print(f"🚀 Starte Testlauf ID: {test_id}")

        # --- Modul 1: Audio verarbeiten ---
        # WICHTIG: process_audio sollte die Datei im request_dir verarbeiten
        audio_info = process_audio(test_path)
        actual_path = audio_info["audio_path"]
        print(f"✅ Audio vorbereitet: {actual_path}")

        # --- Modul 2: Transkription erstellen ---
        # Erstellt die .lab Datei direkt neben der .wav im UUID-Ordner
        erkannter_text = transcribe_and_create_lab(actual_path)
        print(f"✅ Text extrahiert: {erkannter_text}")

        # --- Modul 3: MFA Alignment ---
        # Wir geben den spezifischen UUID-Ordner an
        # alignment_out bekommt ebenfalls einen UUID-Unterordner
        alignment_out = os.path.join(os.getcwd(), "audio_input", test_id)
        os.makedirs(alignment_out, exist_ok=True)
        
        # Wir übergeben das Verzeichnis (dirname), nicht die Datei
        runMFAall(os.path.dirname(actual_path), alignment_out)
        print(f"✅ MFA Alignment abgeschlossen in: {alignment_out}")

        # --- Modul 4: Feedback ---
        # Hier musst du ggf. die Pfade an runFeedback übergeben
        runFeedback(alignment_out) 

    except Exception as e:
        print(f"❌ Fehler im Testlauf: {e}")
    
    finally:
        # shutil.rmtree(request_dir)
        pass
