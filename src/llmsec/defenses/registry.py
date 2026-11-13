"""Name -> defense class. Stage 6 registers D1-D5 and `layered` here."""
from __future__ import annotations

from .base import Defense, NoDefense
from .detector import D1Detector

DEFENSES: dict[str, type[Defense]] = {"none": NoDefense, "d1_detector": D1Detector}


def get_defense(name: str) -> Defense:
    if name not in DEFENSES:
        raise KeyError(f"unknown defense {name!r}; known: {sorted(DEFENSES)}")
    return DEFENSES[name]()  # fresh instance per request (defenses keep per-request events)
