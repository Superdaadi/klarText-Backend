import torch
import torchaudio
import numpy as np
import logging
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import epitran
from ctc_segmentation import ctc_segmentation, CtcSegmentationParameters, prepare_text

# --- Logging konfigurieren ---
logging.basicConfig(level=logging.INFO)

# --- Epitrans für Deutsche Phoneme ---
epi = epitran.Epitran('deu-Latn')

def normalize_audio(waveform, target_rms=0.1):
    """Skaliert die Audio auf ein gewünschtes RMS-Level"""
    rms = torch.sqrt(torch.mean(waveform**2))
    if rms > 0:
        waveform = waveform * (target_rms / rms)
    return waveform

def extract_phonemes(logger, file_path):
    logger = logger

    """
    Nimmt eine WAV/MP3-Datei und liefert eine Liste von Phonemen mit Zeitstempel.
    Rückgabe: [{"phonem": "ʃ", "start": 0.42, "end": 0.55}, ...]
    """
    try:
        logger.info(f"Start processing file: {file_path}")

        # --- 1. Modell laden ---
        model_name = "facebook/wav2vec2-large-xlsr-53-german"
        model_name2 = "facebook/wav2vec2-large-960h-lv60-self"
        logger.info("Lade Wav2Vec2-Modell...")
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name)
        model.eval()
        logger.info("Modell geladen.")

        # --- 2. Audio laden und resamplen ---
        waveform, sample_rate = torchaudio.load(file_path, normalize=True)
        logger.info(f"Audio geladen: {waveform.shape}, Sample Rate: {sample_rate}")

        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)  # Mono
            logger.info("Stereo zu Mono konvertiert.")

        if sample_rate != 16000:
            waveform = torchaudio.functional.resample(waveform, sample_rate, 16000)
            logger.info("Audio auf 16kHz resampled.")

        input_values = processor(
            waveform.squeeze().numpy(),
            return_tensors="pt",
            sampling_rate=16000
        ).input_values

        # --- 2a. Audio-Stats ---
        logger.info(f"Waveform dtype: {waveform.dtype}, min: {waveform.min().item()}, max: {waveform.max().item()}")
        logger.info(f"Waveform RMS: {torch.sqrt(torch.mean(waveform**2)).item()}")

        # --- 2b. Lautstärke normalisieren ---
        # waveform = normalize_audio(waveform)
        logger.info(f"Waveform RMS: {torch.sqrt(torch.mean(waveform**2)):.4f}, min: {waveform.min():.4f}, max: {waveform.max():.4f}")

        # --- 3. Processor Input ---
        input_values = processor(
            waveform.squeeze().numpy(),
            return_tensors="pt",
            sampling_rate=16000
        ).input_values
        logger.info(f"Input values shape: {input_values.shape}, min: {input_values.min()}, max: {input_values.max()}")

        # --- 4. Logits vom Modell ---
        with torch.no_grad():
            logits = model(input_values).logits.cpu().numpy()  # (1, time, vocab_size)
        logits = np.atleast_2d(logits.squeeze(0))
        logger.info(f"Logits shape: {logits.shape}, min: {logits.min():.2f}, max: {logits.max():.2f}")

        # --- 5. Transkription ---
        predicted_ids = torch.argmax(torch.tensor(logits), dim=-1)
        transcription = processor.batch_decode([predicted_ids])[0]
        logger.info(f"Transkription: {transcription}")


        blank_id = processor.tokenizer.pad_token_id
        logger.info(f"Blank token id: {blank_id}")

        predicted_ids = torch.argmax(torch.tensor(logits), dim=-1)

        unique, counts = torch.unique(predicted_ids, return_counts=True)
        token_stats = dict(zip(unique.tolist(), counts.tolist()))
        logger.info(f"Predicted token distribution: {token_stats}")

        blank_scores = logits[:, blank_id]
        max_scores = logits.max(axis=1)

        logger.info(
            f"Blank score mean: {blank_scores.mean():.2f}, "
            f"Max score mean: {max_scores.mean():.2f}"
        )

        with torch.no_grad():
            logits_pt = model(input_values).logits

        predicted_ids = torch.argmax(logits_pt, dim=-1)
        text = processor.decode(predicted_ids[0])

        logger.info(f"RAW ASR Output: '{text}'")

        # --- 6. Text → Phoneme ---
        phoneme_seq = [p for p in epi.transliterate(transcription) if p != ' ']
        if not phoneme_seq:
            logger.warning("Keine Phoneme gefunden.")
            return []

        phoneme_text = ''.join(phoneme_seq)

        # --- 7. CTC Alignment ---
        parameters = CtcSegmentationParameters()
        token_ids = np.array(
            [parameters.char_to_index.get(c, parameters.blank_index) for c in phoneme_text],
            dtype=np.int64
        )
        ground_truth, utt_len = prepare_text(parameters, [phoneme_text], [phoneme_text])
        segmentation, char_probs, state_list = ctc_segmentation(parameters, logits, token_ids)


        # --- 8. Phonem + Zeitstempel ---
        phoneme_timestamps = []
        audio_duration = waveform.shape[1] / 16000
        time_per_frame = audio_duration / logits.shape[0]

        for s in segmentation[0]:
            phoneme_timestamps.append({
                "phonem": s['label'],
                "start": round(s['start'] * time_per_frame, 2),
                "end": round(s['end'] * time_per_frame, 2)
            })

        logger.info(f"Phoneme extraction finished: {len(phoneme_timestamps)} phonemes found.")
        return phoneme_timestamps

    except Exception as e:
        logger.error(f"Fehler beim Verarbeiten der Datei: {e}", exc_info=True)
        return []
