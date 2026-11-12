"""Client for any OpenAI-compatible /chat/completions server (Ollama, vLLM, llama.cpp, hosted APIs)."""
from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx

from .base import ChatResult, LLMClient, ModelSpec, ToolCall


class OpenAICompatClient(LLMClient):
    def __init__(self, spec: ModelSpec, transport: httpx.BaseTransport | None = None, retries: int = 2):
        super().__init__(spec)
        headers = {"Content-Type": "application/json"}
        key = os.environ.get(spec.api_key_env, "") if spec.api_key_env else ""
        if key:
            headers["Authorization"] = f"Bearer {key}"
        self._http = httpx.Client(
            base_url=spec.base_url.rstrip("/"), headers=headers, timeout=spec.timeout_s, transport=transport
        )
        self._retries = retries

    def chat(self, messages, tools=None, temperature=0.0, seed=0, max_tokens=512) -> ChatResult:
        body: dict[str, Any] = {
            "model": self.spec.model,
            "messages": self._apply_system_suffix(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if seed is not None:
            body["seed"] = seed
        if tools and self.spec.supports_tools:
            body["tools"] = tools
        body.update(self.spec.extra_body)

        t0 = time.perf_counter()
        last_err = ""
        for attempt in range(self._retries + 1):
            try:
                r = self._http.post("/chat/completions", json=body)
                if r.status_code >= 500 and attempt < self._retries:
                    last_err = f"HTTP {r.status_code}"
                    time.sleep(1 + attempt)
                    continue
                latency = (time.perf_counter() - t0) * 1000
                if r.status_code != 200:
                    return ChatResult("", latency_ms=latency, model=self.spec.model,
                                      error=f"HTTP {r.status_code}: {r.text[:300]}")
                return self._parse(r.json(), latency)
            except (httpx.TransportError, json.JSONDecodeError) as e:
                last_err = f"{type(e).__name__}: {e}"
                if attempt < self._retries:
                    time.sleep(1 + attempt)
        return ChatResult("", latency_ms=(time.perf_counter() - t0) * 1000, model=self.spec.model, error=last_err)

    def _parse(self, data: dict[str, Any], latency: float) -> ChatResult:
        try:
            msg = data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError):
            return ChatResult("", latency_ms=latency, model=self.spec.model, error=f"bad response: {str(data)[:300]}")
        calls = []
        for tc in msg.get("tool_calls") or []:
            fn = tc.get("function", {})
            args = fn.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args) if args.strip() else {}
                except json.JSONDecodeError:
                    args = {"_raw": args}
            calls.append(ToolCall(name=fn.get("name", ""), arguments=args, id=tc.get("id", "")))
        usage = data.get("usage") or {}
        return ChatResult(
            text=msg.get("content") or "",
            tool_calls=calls,
            latency_ms=latency,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            model=data.get("model", self.spec.model),
        )
