import whisper

print(f"Starting...")
model = whisper.load_model("base")
result = model.transcribe("audio_input/test.wav", language="de")
print(f"Erkannter Text: {result['text']}")

# Erstellt die .lab Datei für MFA
with open("audio_input/test.lab", "w", encoding="utf-8") as f:
    f.write(result['text'].strip())


