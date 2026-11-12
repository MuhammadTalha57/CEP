"""Name -> defense class. Stage 6 registers D1-D5 and `layered` here."""
from __future__ import annotations

from .base import Defense, NoDefense

DEFENSES: dict[str, type[Defense]] = {"none": NoDefense}


def get_defense(name: str) -> Defense:
    if name not in DEFENSES:
        raise KeyError(f"unknown defense {name!r}; known: {sorted(DEFENSES)}")
    return DEFENSES[name]()  # fresh instance per request (defenses keep per-request events)
