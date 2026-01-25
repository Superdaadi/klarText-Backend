import torch
import torch.nn.functional as F
from transformers import Wav2Vec2Processor, Wav2Vec2Model

class EmbeddingExtractor:
    def __init__(self, model_name="facebook/wav2vec2-base-xlsr-53"):
        self.processor = Wav2Vec2Processor.from_pretrained(model_name)
        self.model = Wav2Vec2Model.from_pretrained(model_name)
        self.model.eval()

    def extract(self, waveform, sr):
        inputs = self.processor(
            waveform,
            sampling_rate=sr,
            return_tensors="pt",
            padding=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        return outputs.last_hidden_state.mean(dim=1)


def cosine_score(emb_user, emb_ref):
    sim = F.cosine_similarity(emb_user, emb_ref).item()
    return int((sim + 1) / 2 * 100)
