# posterior_model.py

import torch
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

MODEL_NAME = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"

processor = Wav2Vec2Processor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_NAME)
model.eval()

PHONEME_VOCAB = processor.tokenizer.get_vocab()
ID2PHONEME = {v: k for k, v in PHONEME_VOCAB.items()}
