"""Server-side request execution, shared by the HTTP server and the in-process runner.

One code path for both, so local in-process runs, local HTTP runs and AWS runs execute identical logic.
Request: {"model": id, "defense": name, "seed": int, "request": {"app": ..., <app input>, "lab": {...}}}
`lab` is the lab-only experiment setup (secret, planted docs/emails/pages); see design.md §3.
"""
from __future__ import annotations

import threading
import time
from dataclasses import asdict
from typing import Any

from ..attacks.carriers import build_poisoned_doc
from ..defenses.registry import get_defense
from ..llm.base import LLMClient
from ..llm.factory import load_specs, make_client
from .agent import ToolAgent
from .chatbot import SupportChatbot
from .rag import RAGApp

APPS = ("chatbot", "rag", "agent")


class Executor:
    def __init__(self, models_path: str | None = None, clients: dict[str, LLMClient] | None = None):
        self._specs = load_specs(models_path) if models_path else load_specs()
        self._clients: dict[str, LLMClient] = dict(clients or {})
        self._kb_chunks: dict[str, list] = {}
        self._lock = threading.Lock()

    @property
    def model_ids(self) -> list[str]:
        return sorted(set(self._specs) | set(self._clients))

    def client(self, model_id: str) -> LLMClient:
        with self._lock:
            if model_id not in self._clients:
                if model_id not in self._specs:
                    raise KeyError(f"unknown model {model_id!r}")
                self._clients[model_id] = make_client(self._specs[model_id])
            return self._clients[model_id]

    def _rag(self, client: LLMClient, defense_name: str) -> RAGApp:
        defense = get_defense(defense_name)
        with self._lock:
            chunks = self._kb_chunks.get(defense_name)
        app = RAGApp(client, defense=defense, base_chunks=chunks)
        if chunks is None:
            with self._lock:
                self._kb_chunks[defense_name] = app.base_chunks
        return app

    def execute(self, body: dict[str, Any]) -> dict[str, Any]:
        t0 = time.perf_counter()
        req = body["request"]
        app_id, seed = req["app"], int(body.get("seed", 0))
        defense_name = body.get("defense", "none")
        client = self.client(body["model"])
        lab = req.get("lab", {})
        if app_id == "chatbot":
            resp = SupportChatbot(client, secret=lab["secret"], defense=get_defense(defense_name)) \
                .handle(req["user_message"], seed=seed)
        elif app_id == "rag":
            docs = [build_poisoned_doc(d["carrier"], d["doc_id"], d["title"], d["cover"], d["payload"],
                                       d.get("variant", 0)) for d in lab.get("poison_docs", [])]
            resp = self._rag(client, defense_name).handle(req["question"], extra_docs=docs, seed=seed)
        elif app_id == "agent":
            resp = ToolAgent(client, defense=get_defense(defense_name)).handle(
                req["user_request"], extra_emails=lab.get("extra_emails", []),
                extra_pages=lab.get("extra_pages"), seed=seed)
        else:
            raise ValueError(f"unknown app {app_id!r}; known: {APPS}")
        out = asdict(resp)
        out["server_ms"] = (time.perf_counter() - t0) * 1000
        out["model"] = body["model"]
        return out
