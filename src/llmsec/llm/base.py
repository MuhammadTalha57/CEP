"""Model-agnostic LLM interface (design.md §2).

Apps only talk to `LLMClient.chat`; which model or provider answers is decided
in configs/models.yaml. Messages and tools use the OpenAI chat format because
every backend we target (Ollama, vLLM, llama.cpp, Bedrock via adapter) can map it.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]
    id: str = ""


@dataclass
class ChatResult:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    latency_ms: float = 0.0
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    model: str = ""
    error: str | None = None  # set instead of raising, so the harness can log it

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class ModelSpec:
    id: str  # our stable id, used in results paths
    backend: str  # "openai_compat" | "mock"
    model: str  # provider's model name, e.g. "qwen3:1.7b"
    base_url: str = ""
    api_key_env: str = ""  # name of the env var holding the key (never the key itself)
    supports_tools: bool = True
    system_suffix: str = ""  # appended to the system prompt, e.g. "/no_think" for qwen3
    extra_body: dict[str, Any] = field(default_factory=dict)  # backend-specific options
    timeout_s: float = 300.0


class LLMClient(ABC):
    def __init__(self, spec: ModelSpec):
        self.spec = spec

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.0,
        seed: int | None = 0,
        max_tokens: int = 512,
    ) -> ChatResult: ...

    def _apply_system_suffix(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not self.spec.system_suffix:
            return messages
        out = [dict(m) for m in messages]
        for m in out:
            if m.get("role") == "system":
                m["content"] = f"{m.get('content', '')}\n{self.spec.system_suffix}"
                return out
        return [{"role": "system", "content": self.spec.system_suffix}, *out]
