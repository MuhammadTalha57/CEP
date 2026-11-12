"""Scripted backend for tests: no model needed."""
from __future__ import annotations

from typing import Any, Callable

from .base import ChatResult, LLMClient, ModelSpec

Responder = Callable[[list[dict[str, Any]], list[dict[str, Any]] | None], ChatResult]


class MockClient(LLMClient):
    """Replies with `responder(messages, tools)`; default echoes the last user message."""

    def __init__(self, spec: ModelSpec | None = None, responder: Responder | None = None):
        super().__init__(spec or ModelSpec(id="mock", backend="mock", model="mock"))
        self.responder = responder or (lambda msgs, tools: ChatResult(text=_last_user(msgs)))
        self.calls: list[dict[str, Any]] = []

    def chat(self, messages, tools=None, temperature=0.0, seed=0, max_tokens=512) -> ChatResult:
        messages = self._apply_system_suffix(messages)
        self.calls.append({"messages": messages, "tools": tools, "temperature": temperature, "seed": seed})
        res = self.responder(messages, tools)
        res.model = res.model or self.spec.model
        return res


def _last_user(messages: list[dict[str, Any]]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return str(m.get("content", ""))
    return ""
