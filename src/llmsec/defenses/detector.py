"""D1: prompt-injection detector on every untrusted text (design.md §5.1).

Model: ProtectAI DeBERTa-v3 prompt-injection v2 (184M), the public detector family benchmarked in
P03 p8-9 (TPR@FPR1% 43.22% for DeBERTa-184M) and used in P09 p8; blocking at a confidence
threshold follows P06 p4 (0.85). Texts are blocked when score >= threshold; the score is always logged.
"""
from __future__ import annotations

import threading
from typing import Callable

from .base import Defense, Verdict
from .config import defense_config

Scorer = Callable[[str], float]

_lock = threading.Lock()
_scorer: Scorer | None = None


def windows(text: str, size: int, overlap: int) -> list[str]:
    if len(text) <= size:
        return [text]
    step = max(1, size - overlap)
    return [text[i:i + size] for i in range(0, len(text) - overlap, step)]


def _load_hf_scorer() -> Scorer:
    from transformers import pipeline  # lazy: heavy import, not needed by tests or undefended runs

    cfg = defense_config()["detector"]
    device = -1 if cfg.get("device", "cpu") == "cpu" else 0
    clf = pipeline("text-classification", model=cfg["model"], truncation=True, max_length=512, device=device)

    def score(text: str) -> float:
        best = 0.0
        for chunk in windows(text, cfg["window_chars"], cfg["overlap_chars"]):
            r = clf(chunk)[0]
            p = r["score"] if r["label"].upper() == "INJECTION" else 1.0 - r["score"]
            best = max(best, p)
        return best

    return score


def get_scorer() -> Scorer:
    global _scorer
    with _lock:
        if _scorer is None:
            _scorer = _load_hf_scorer()
        return _scorer


def set_scorer(scorer: Scorer | None) -> None:
    """Tests inject a fake scorer here (None resets to the real model on next use)."""
    global _scorer
    with _lock:
        _scorer = scorer


class DetectorMixin:
    def _detect(self, text: str) -> Verdict:
        if not text.strip():
            return Verdict()
        s = get_scorer()(text)
        thr = defense_config()["detector"]["threshold"]
        return Verdict(blocked=s >= thr, reason=f"detector score {s:.3f}", score=round(s, 4))


class D1Detector(DetectorMixin, Defense):
    name = "d1_detector"

    def check_input(self, text: str, channel: str) -> Verdict:
        return self._detect(text)
