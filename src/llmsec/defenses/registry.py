"""Name -> defense class. D5 (self-check) not implemented, see STATE.md."""
from __future__ import annotations

from .base import Defense, NoDefense
from .detector import D1Detector
from .sanitize import D2Sanitize
from .spotlight import D3Spotlight
from .layered import LayeredDefense
from .tool_policy import D4ToolPolicy

DEFENSES: dict[str, type[Defense]] = {"none": NoDefense, "d1_detector": D1Detector, "d2_sanitize": D2Sanitize,
                                 "d3_spotlight": D3Spotlight, "d4_toolpolicy": D4ToolPolicy,
                                 "layered": LayeredDefense}


def get_defense(name: str) -> Defense:
    if name not in DEFENSES:
        raise KeyError(f"unknown defense {name!r}; known: {sorted(DEFENSES)}")
    return DEFENSES[name]()  # fresh instance per request (defenses keep per-request events)
