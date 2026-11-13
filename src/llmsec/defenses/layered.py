"""Our defense: channel-aware layered defense (design.md §5.2) [OURS, built from paper-defined parts].

user message  -> D1 detector + D3 hardening
documents     -> D2 sanitize/normalize at ingestion, D1 on each retrieved chunk, D3 spotlighting
tool output   -> D3 spotlighting + D4 tool policy (output treated as data)
final answer  -> output guard: block the system secret (raw or with separators/case changed) and URLs
                 outside an allow-list. The guard is deliberately simpler than the scorer (no base64,
                 rot13 or reversal), so encoded leaks can still be measured, and the scorer is not
                 reused as the defense.
"""
from __future__ import annotations

import re

from .base import Defense, Verdict
from .config import defense_config
from .detector import DetectorMixin
from .sanitize import SanitizeMixin, normalize
from .spotlight import SpotlightMixin
from .tool_policy import ToolPolicyMixin

_URL = re.compile(r"(?:https?://|www\.)([\w.-]+)", re.I)


def _alnum(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def output_guard(text: str, secrets: list[str], allowed_domains: list[str]) -> Verdict:
    t_low, t_norm = text.lower(), _alnum(text)
    for s in secrets:
        if s and (s.lower() in t_low or _alnum(s) in t_norm):
            return Verdict(blocked=True, reason="secret in output")
    for host in _URL.findall(text):
        host = host.lower().rstrip(".")
        if not any(host == d or host.endswith("." + d) for d in allowed_domains):
            return Verdict(blocked=True, reason=f"URL not allowed: {host}")
    return Verdict()


class LayeredDefense(DetectorMixin, SanitizeMixin, SpotlightMixin, ToolPolicyMixin, Defense):
    name = "layered"

    def sanitize_document(self, raw, fmt, extracted):
        return self._sanitize(raw, fmt)

    def check_input(self, text: str, channel: str) -> Verdict:
        if channel == "tool_output":
            return Verdict()  # handled by spotlighting + tool policy (design.md §5.2)
        if channel == "document":
            text = normalize(text)
        v = self._detect(text)
        v.text = text if channel == "document" else None
        return v

    def system_addendum(self) -> str:
        return self._addendum()

    def wrap_untrusted(self, text: str, channel: str) -> str:
        return self._wrap(text, channel)

    def check_tool_call(self, name, arguments, user_request):
        return self._policy(name, arguments, user_request)

    def check_output(self, text: str, secrets: list[str]) -> Verdict:
        return output_guard(text, secrets, defense_config()["output_guard"]["allowed_domains"])
