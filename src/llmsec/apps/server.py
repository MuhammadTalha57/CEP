"""HTTP API for the three apps (design.md §3, §7). Same code locally and on AWS.

Run:  uvicorn llmsec.apps.server:app --host 0.0.0.0 --port 8000
Env:  APP_API_KEY (required header X-API-Key when set) · SERVER_ENV (label logged with results, e.g. aws-ec2)
      OLLAMA_URL (used by configs/models.yaml)
"""
from __future__ import annotations

import os
import secrets
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from ..defenses.registry import DEFENSES
from .executor import APPS, Executor

app = FastAPI(title="llmsec lab apps", version="0.1.0")
_executor = Executor()


class RunBody(BaseModel):
    model: str
    defense: str = "none"
    seed: int = 0
    request: dict[str, Any]


def _auth(key: str | None) -> None:
    expected = os.environ.get("APP_API_KEY", "")
    if expected and not (key and secrets.compare_digest(key, expected)):
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"ok": True, "env": os.environ.get("SERVER_ENV", "local"), "apps": list(APPS),
            "models": _executor.model_ids, "defenses": sorted(DEFENSES)}


@app.post("/v1/run")
def run(body: RunBody, x_api_key: str | None = Header(default=None)) -> dict[str, Any]:
    _auth(x_api_key)
    try:
        out = _executor.execute(body.model_dump())
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    out["server_env"] = os.environ.get("SERVER_ENV", "local")
    return out
