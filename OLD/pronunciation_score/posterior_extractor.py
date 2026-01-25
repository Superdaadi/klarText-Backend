# posterior_extractor.py
import torch
import torchaudio
import numpy as np
from pronunciation_score.posterior_model import processor, model, ID2PHONEME

def extract_posteriors(wav_path):
    # In newer torchaudio, we use the dispatcher logic. 
    # This bypasses the search for 'torchcodec'.
    try:
        # Try loading specifically with the ffmpeg dispatcher
        waveform, sr = torchaudio.load(wav_path, format="wav")
    except Exception:
        # Generic fallback
        waveform, sr = torchaudio.load(wav_path)

    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)

    # Ensure mono
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0)
    else:
        waveform = waveform.squeeze()

    inputs = processor(
        waveform,
        sampling_rate=16000,
        return_tensors="pt"
    )

    with torch.no_grad():
        logits = model(**inputs).logits

    posteriors = torch.softmax(logits, dim=-1)[0]
    frame_time = waveform.shape[0] / 16000 / posteriors.shape[0]

    frames = []
    for i, vec in enumerate(posteriors):
        frames.append({
            "time": i * frame_time,
            "log_probs": {
                ID2PHONEME[j]: float(torch.log(vec[j] + 1e-9))
                for j in range(len(vec))
            }
        })

    return frames