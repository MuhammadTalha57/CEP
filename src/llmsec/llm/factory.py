"""Build LLM clients from configs/models.yaml (switch models/providers without code changes)."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

from .base import LLMClient, ModelSpec

_ENV = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODELS = REPO_ROOT / "configs" / "models.yaml"


def expand_env(value: Any) -> Any:
    """Replace ${VAR} / ${VAR:-default} in strings (recursively in dicts/lists)."""
    if isinstance(value, str):
        return _ENV.sub(lambda m: os.environ.get(m.group(1), m.group(2) or ""), value)
    if isinstance(value, dict):
        return {k: expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [expand_env(v) for v in value]
    return value


def load_specs(path: str | Path = DEFAULT_MODELS) -> dict[str, ModelSpec]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    specs = {}
    for entry in raw.get("models", []):
        spec = ModelSpec(**expand_env(entry))
        if spec.id in specs:
            raise ValueError(f"duplicate model id {spec.id!r} in {path}")
        specs[spec.id] = spec
    return specs


def make_client(spec: ModelSpec, **kwargs: Any) -> LLMClient:
    if spec.backend == "openai_compat":
        from .openai_compat import OpenAICompatClient
        return OpenAICompatClient(spec, **kwargs)
    if spec.backend == "mock":
        from .mock import MockClient
        return MockClient(spec, **kwargs)
    raise ValueError(f"unknown backend {spec.backend!r} for model {spec.id!r}")


def get_client(model_id: str, path: str | Path = DEFAULT_MODELS, **kwargs: Any) -> LLMClient:
    specs = load_specs(path)
    if model_id not in specs:
        raise KeyError(f"model {model_id!r} not in {path}; known: {sorted(specs)}")
    return make_client(specs[model_id], **kwargs)
