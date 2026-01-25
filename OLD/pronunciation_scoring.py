"""
Modul 5.1 – Echtes Kaldi-GOP (Goodness of Pronunciation)
=======================================================

Dieses Modul ersetzt das Mock-Akustikmodell durch **echte Kaldi-Posterioren**.

Pipeline (klassisch & korrekt):
1. Kaldi erzeugt posterior.ark (DNN-Posterioren pro Frame)
2. Posterioren werden zu log P(x|phone) aggregiert
3. GOP(p) = log P(x|p) - max_{q≠p} log P(x|q)
4. Normalisierung → Score 0–100

Voraussetzungen:
- Kaldi installiert
- MFA oder eigenes Kaldi-Setup
- posterior.ark + phones.txt

Autor: KI Sprachanalyse
"""

from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple
from kaldiio import ReadHelper

# --------------------------------------------------
# Datamodelle
# --------------------------------------------------

@dataclass
class PhoneSegment:
    xmin: float
    xmax: float
    symbol: str
    phone_id: int

    @property
    def duration(self) -> float:
        return max(0.0, self.xmax - self.xmin)


# --------------------------------------------------
# Kaldi Posterior Loader
# --------------------------------------------------

class KaldiPosteriorLoader:
    """
    Liest posterior.ark im Kaldi-Format
    """

    def __init__(self, posterior_ark_path: str):
        from kaldiio import ReadHelper
        self.posterior_ark_path = posterior_ark_path
        self.ReadHelper = ReadHelper

    def load(self) -> Dict[str, List[Dict[int, float]]]:
        """
        Returns:
        utterance_id -> list of frame-level posterior dicts
        """
        data = {}

        with self.ReadHelper(f"ark:{self.posterior_ark_path}") as reader:
            for utt_id, post in reader:
                frames = []
                for frame in post:
                    frame_dict = {pid: prob for pid, prob in frame}
                    frames.append(frame_dict)
                data[utt_id] = frames

        return data


# --------------------------------------------------
# GOP Berechnung (ECHT)
# --------------------------------------------------

class KaldiGOPScorer:
    def __init__(self, posteriors: Dict[str, List[Dict[int, float]]]):
        self.posteriors = posteriors

    def log_likelihood(self, frames: List[Dict[int, float]], phone_id: int) -> float:
        """
        log P(x|p) = Summe über Frames log Posterior(p)
        """
        eps = 1e-10
        ll = 0.0
        for f in frames:
            ll += math.log(f.get(phone_id, eps))
        return ll

    def gop(self, frames: List[Dict[int, float]], correct_phone: int) -> float:
        ll_correct = self.log_likelihood(frames, correct_phone)

        competitors = set()
        for f in frames:
            competitors.update(f.keys())

        ll_best_competitor = -float("inf")
        for pid in competitors:
            if pid == correct_phone:
                continue
            ll = self.log_likelihood(frames, pid)
            ll_best_competitor = max(ll_best_competitor, ll)

        return ll_correct - ll_best_competitor

    @staticmethod
    def normalize(gop: float) -> int:
        score = 100 / (1 + math.exp(-0.5 * gop))
        return int(round(score))


# --------------------------------------------------
# Pronunciation Scoring Engine (Kaldi)
# --------------------------------------------------

class KaldiPronunciationScoringEngine:
    def __init__(self, posteriors):
        self.gop_scorer = KaldiGOPScorer(posteriors)

    def score_phone(self, utt_id: str, phone: PhoneSegment, frame_start: int, frame_end: int) -> Tuple[float, int]:
        frames = self.gop_scorer.posteriors[utt_id][frame_start:frame_end]
        gop = self.gop_scorer.gop(frames, phone.phone_id)
        score = self.gop_scorer.normalize(gop)
        return gop, score


# --------------------------------------------------
# Beispiel-Hauptprogramm
# --------------------------------------------------

if __name__ == "__main__":
    print("▶ Kaldi-GOP Scoring – Echtbetrieb")

    # Beispielpfade
    POSTERIOR_ARK = "posterior.ark"
    UTT_ID = "utt_001"

    loader = KaldiPosteriorLoader(POSTERIOR_ARK)
    posteriors = loader.load()

    engine = KaldiPronunciationScoringEngine(posteriors)

    # Beispiel-Phone (Frame-Grenzen kommen aus MFA-Alignment)
    phone = PhoneSegment(
        xmin=0.00,
        xmax=0.12,
        symbol="ɛ",
        phone_id=42
    )

    gop, score = engine.score_phone(
        utt_id=UTT_ID,
        phone=phone,
        frame_start=10,
        frame_end=18
    )

    print(f"GOP={gop:.2f} → Score={score}")
