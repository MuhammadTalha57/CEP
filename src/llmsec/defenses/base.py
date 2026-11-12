"""Defense hook interface shared by all apps (design.md §5).

Apps call these hooks at fixed points; Stage 6 adds concrete defenses (D1-D5, layered).
`NoDefense` is the undefended baseline and must not change any input or output.

Channels: "user" (user message), "document" (retrieved text), "tool_output" (tool results).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

CHANNELS = ("user", "document", "tool_output")
REFUSAL = "Sorry, I can't help with that request."


@dataclass
class Verdict:
    blocked: bool = False
    text: str | None = None  # possibly transformed text (None = unchanged)
    reason: str = ""
    score: float | None = None


@dataclass
class DefenseEvent:
    hook: str
    channel: str
    blocked: bool
    reason: str = ""
    score: float | None = None


class Defense:
    """Base class: every hook is a no-op. Subclasses override what they need."""

    name = "none"

    def __init__(self) -> None:
        self.events: list[DefenseEvent] = []

    # -- hooks --------------------------------------------------------------
    def check_input(self, text: str, channel: str) -> Verdict:
        return Verdict()

    def sanitize_document(self, raw: str | bytes, fmt: str, extracted: str) -> str | None:
        """Return cleaned text for a raw HTML/PDF document, or None to keep the naive extraction."""
        return None

    def wrap_untrusted(self, text: str, channel: str) -> str:
        return text

    def system_addendum(self) -> str:
        return ""

    def check_tool_call(self, name: str, arguments: dict[str, Any], user_request: str) -> Verdict:
        return Verdict()

    def check_output(self, text: str, secrets: list[str]) -> Verdict:
        return Verdict()

    # -- helpers used by apps ------------------------------------------------
    def run_input(self, text: str, channel: str) -> tuple[str, bool]:
        """Apply check_input; log the event; return (text_to_use, blocked)."""
        v = self.check_input(text, channel)
        self.events.append(DefenseEvent("check_input", channel, v.blocked, v.reason, v.score))
        return (v.text if v.text is not None else text), v.blocked

    def run_output(self, text: str, secrets: list[str]) -> tuple[str, bool]:
        v = self.check_output(text, secrets)
        self.events.append(DefenseEvent("check_output", "output", v.blocked, v.reason, v.score))
        if v.blocked:
            return REFUSAL, True
        return (v.text if v.text is not None else text), False

    def run_tool_call(self, name: str, arguments: dict[str, Any], user_request: str) -> bool:
        v = self.check_tool_call(name, arguments, user_request)
        self.events.append(DefenseEvent("check_tool_call", "tool", v.blocked, v.reason, v.score))
        return v.blocked

    def reset(self) -> None:
        self.events = []


class NoDefense(Defense):
    name = "none"


@dataclass
class AppResponse:
    output: str
    blocked: bool = False
    tool_calls: list[dict[str, Any]] = field(default_factory=list)  # executed and blocked calls
    retrieved_ids: list[str] = field(default_factory=list)
    latency_ms: float = 0.0  # total LLM time
    llm_calls: int = 0
    error: str | None = None
    defense: str = "none"
    defense_events: list[dict[str, Any]] = field(default_factory=list)
