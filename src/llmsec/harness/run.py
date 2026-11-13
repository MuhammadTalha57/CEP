"""Experiment runner (design.md §6): generate trials, send them to the apps, check, log JSONL.

Examples
  # in-process (no server), local Ollama:
  python -m llmsec.harness.run --models qwen3-1.7b --apps chatbot --variants 3 --env local
  # against a running server (local or AWS); the harness is black-box:
  python -m llmsec.harness.run --target http://<host>:8000 --env aws --models qwen3-1.7b --defense none

Output: results/<env>/<model>/<app>__<defense>.jsonl, one line per trial. Re-running resumes:
trials already logged with a valid result are skipped (use --retry-invalid to redo error/invalid ones).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import httpx

from ..attacks.generator import REPO_ROOT, Trial, generate, load_experiment
from .evaluate import evaluate

Sender = Callable[[dict[str, Any]], dict[str, Any]]


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True,
                              text=True, timeout=5).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def inproc_sender() -> Sender:
    from ..apps.executor import Executor
    ex = Executor()
    return ex.execute


def http_sender(target: str, api_key: str, timeout: float = 600.0,
                transport: httpx.BaseTransport | None = None) -> Sender:
    http = httpx.Client(base_url=target.rstrip("/"), timeout=timeout, transport=transport,
                        headers={"X-API-Key": api_key} if api_key else {})

    def send(body: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(3):
            try:
                r = http.post("/v1/run", json=body)
                if r.status_code == 200:
                    return r.json()
                if r.status_code < 500:
                    return {"output": "", "error": f"HTTP {r.status_code}: {r.text[:300]}"}
            except httpx.TransportError as e:
                err = f"{type(e).__name__}: {e}"
                if attempt == 2:
                    return {"output": "", "error": err}
            time.sleep(2 * (attempt + 1))
        return {"output": "", "error": "HTTP 5xx after retries"}

    return send


def out_path(out_dir: Path, env: str, model: str, app: str, defense: str) -> Path:
    return out_dir / env / model / f"{app}__{defense}.jsonl"


def done_ids(path: Path, retry_invalid: bool) -> set[str]:
    if not path.exists():
        return set()
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if retry_invalid and not rec.get("eval", {}).get("valid", False):
            continue
        ids.add(rec["trial_id"])
    return ids


WARMUP_BODY = {"defense": "none", "seed": 0,
               "request": {"app": "chatbot", "user_message": "Hello", "lab": {"secret": "ACME-WARM-UP00"}}}


def warm_up(send: Sender, model: str, quiet: bool = False) -> None:
    """Load the model before timing (pilot 13 Nov: the first trial included 40-112 s of model loading).

    Not logged as a trial; latency is a reported metric, so it must not include model load time.
    """
    t0 = time.perf_counter()
    resp = send({**WARMUP_BODY, "model": model})
    if not quiet:
        print(f"warm-up {model}: {time.perf_counter() - t0:.1f}s"
              f"{' error: ' + str(resp.get('error')) if resp.get('error') else ''}", flush=True)


def run_trial(send: Sender, trial: Trial, model: str, defense: str) -> dict[str, Any]:
    body = {"model": model, "defense": defense, "seed": trial.seed, "request": trial.request}
    t0 = time.perf_counter()
    resp = send(body)
    wall = (time.perf_counter() - t0) * 1000
    return {"trial": trial, "resp": resp, "wall_ms": wall, "eval": evaluate(trial.check, resp)}


def run(models: list[str], apps: list[str] | None, defense: str, env: str, target: str = "inproc",
        variants: int | None = None, cells: list[str] | None = None, include_clean: bool = True,
        limit: int | None = None, workers: int = 1, out_dir: Path = REPO_ROOT / "results",
        retry_invalid: bool = False, send: Sender | None = None, experiment: str | None = None,
        quiet: bool = False, warmup: bool = True) -> list[dict[str, Any]]:
    exp = load_experiment(experiment) if experiment else load_experiment()
    trials = generate(exp, apps=apps, variants=variants, cells=cells, include_clean=include_clean)
    if send is None:
        send = inproc_sender() if target == "inproc" else http_sender(target, os.environ.get("APP_API_KEY", ""))
    commit = git_commit()
    records: list[dict[str, Any]] = []
    for model in models:
        if warmup:
            warm_up(send, model, quiet)
        by_app: dict[str, list[Trial]] = {}
        for t in trials:
            by_app.setdefault(t.app, []).append(t)
        for app, app_trials in by_app.items():
            path = out_path(out_dir, env, model, app, defense)
            path.parent.mkdir(parents=True, exist_ok=True)
            skip = done_ids(path, retry_invalid)
            todo = [t for t in app_trials if t.trial_id not in skip][: limit or None]
            if not quiet:
                print(f"[{env}] {model} {app} defense={defense}: {len(todo)} to run, {len(skip)} already done",
                      flush=True)
            with path.open("a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=workers) as pool:
                for i, res in enumerate(pool.map(lambda tr: run_trial(send, tr, model, defense), todo), 1):
                    tr: Trial = res["trial"]
                    rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "env": env,
                           "target": target, "commit": commit, "model": model, "defense": defense,
                           "temperature": exp.get("temperature", 0.0), **tr.to_dict(),
                           "response": res["resp"], "wall_ms": round(res["wall_ms"], 1), "eval": res["eval"]}
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    fh.flush()
                    records.append(rec)
                    if not quiet and (i % 10 == 0 or i == len(todo)):
                        print(f"  {i}/{len(todo)} last={tr.trial_id} success={res['eval']['success']} "
                              f"valid={res['eval']['valid']} wall={res['wall_ms'] / 1000:.1f}s", flush=True)
    return records


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--apps", nargs="+", choices=["chatbot", "rag", "agent"])
    ap.add_argument("--defense", default="none")
    ap.add_argument("--env", default="local", help="label for results/<env>/ (e.g. local, aws)")
    ap.add_argument("--target", default="inproc", help="'inproc' or the server base URL")
    ap.add_argument("--variants", type=int, help="override variants per cell")
    ap.add_argument("--cells", nargs="+", help="only these cells (use U for clean tasks)")
    ap.add_argument("--no-clean", action="store_true")
    ap.add_argument("--limit", type=int, help="max trials per model/app (pilot)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(REPO_ROOT / "results"))
    ap.add_argument("--experiment", help="experiment yaml (default configs/experiment.yaml)")
    ap.add_argument("--retry-invalid", action="store_true")
    a = ap.parse_args(argv)
    run(a.models, a.apps, a.defense, a.env, a.target, a.variants, a.cells, not a.no_clean, a.limit, a.workers,
        Path(a.out), a.retry_invalid, experiment=a.experiment)
    return 0


if __name__ == "__main__":
    sys.exit(main())
