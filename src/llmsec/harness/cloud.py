"""Stage 7: run the cloud matrix (configs/cloud.yaml) block by block against the hosted app over HTTP.

  set APP_API_KEY in the shell first (same value as the server's .env), then:
  python -m llmsec.harness.cloud --target http://<EC2-public-IP>:8000
  python -m llmsec.harness.cloud --target http://<ip>:8000 --dry-run      # list blocks and trial counts only

Blocks run in priority order; each resumes (finished trials are skipped), so it is safe to stop and restart.
Before each block one unlogged request warms up the model AND the defense (D1 loads its detector on first use),
so the logged latency never includes model or detector loading.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from ..attacks.generator import REPO_ROOT, generate, load_experiment
from .run import WARMUP_BODY, Sender, http_sender, run

CLOUD_CONFIG = REPO_ROOT / "configs" / "cloud.yaml"


def load_plan(path: Path = CLOUD_CONFIG) -> dict[str, Any]:
    plan = yaml.safe_load(path.read_text(encoding="utf-8"))
    for b in plan["blocks"]:
        if not {"models", "apps", "defense", "variants"} <= set(b):
            raise ValueError(f"block needs models, apps, defense, variants: {b}")
    return plan


def block_trials(block: dict[str, Any]) -> int:
    return len(generate(load_experiment(), apps=block["apps"], variants=block["variants"])) * len(block["models"])


def warm_up_block(send: Sender, block: dict[str, Any]) -> None:
    for model in block["models"]:
        t0 = time.perf_counter()
        resp = send({**WARMUP_BODY, "model": model, "defense": block["defense"]})
        print(f"warm-up {model} defense={block['defense']}: {time.perf_counter() - t0:.1f}s"
              f"{' error: ' + str(resp.get('error')) if resp.get('error') else ''}", flush=True)


def run_plan(plan: dict[str, Any], send: Sender, target: str, out_dir: Path = REPO_ROOT / "results",
             quiet: bool = False, blocks: list[int] | None = None, retry_invalid: bool = False) -> int:
    """blocks: 1-based block numbers to run (default all). retry_invalid: redo trials logged with an error
    (e.g. a connection timeout); the report keeps only the last record per trial."""
    n = 0
    for i, b in enumerate(plan["blocks"], 1):
        if blocks and i not in blocks:
            continue
        if not quiet:
            print(f"\n=== block {i}/{len(plan['blocks'])}: {b} ===", flush=True)
            warm_up_block(send, b)
        n += len(run(b["models"], b["apps"], b["defense"], plan["env"], target=target, variants=b["variants"],
                     out_dir=out_dir, send=send, quiet=quiet, warmup=False, retry_invalid=retry_invalid))
    return n


def plan_status(plan: dict[str, Any], out_dir: Path = REPO_ROOT / "results") -> list[dict[str, Any]]:
    """Per block: planned trials, trials with a valid result, trials whose last record is an error/invalid."""
    rows = []
    for i, b in enumerate(plan["blocks"], 1):
        planned = {(m, t.app, t.trial_id) for m in b["models"]
                   for t in generate(load_experiment(), apps=b["apps"], variants=b["variants"])}
        last: dict[tuple, bool] = {}
        for m in b["models"]:
            for app in b["apps"]:
                p = out_dir / plan["env"] / m / f"{app}__{b['defense']}.jsonl"
                if p.exists():
                    for line in p.read_text(encoding="utf-8").splitlines():
                        if line.strip():
                            r = json.loads(line)
                            last[(m, app, r["trial_id"])] = bool(r.get("eval", {}).get("valid"))
        valid = sum(1 for k in planned if last.get(k))
        failed = sum(1 for k in planned if k in last and not last[k])
        rows.append({"block": i, **b, "planned": len(planned), "valid": valid, "failed": failed,
                     "missing": len(planned) - valid - failed})
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", help="server base URL, e.g. http://1.2.3.4:8000")
    ap.add_argument("--plan", default=str(CLOUD_CONFIG))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--status", action="store_true", help="show per-block progress from results/ and exit")
    ap.add_argument("--blocks", nargs="+", type=int, help="only these block numbers (1-based)")
    ap.add_argument("--retry-invalid", action="store_true", help="redo trials that were logged with an error")
    a = ap.parse_args(argv)
    plan = load_plan(Path(a.plan))
    if a.status:
        for r in plan_status(plan):
            print(f"block {r['block']}: {r['models']} {r['apps']} {r['defense']}: {r['valid']}/{r['planned']} valid, "
                  f"{r['failed']} failed (retry with --retry-invalid), {r['missing']} not run")
        return 0
    if a.dry_run:
        for i, b in enumerate(plan["blocks"], 1):
            print(f"block {i}: {b} -> {block_trials(b)} trials")
        print("total", sum(block_trials(b) for b in plan["blocks"]), "trials")
        return 0
    if not a.target:
        print("--target is required to run", file=sys.stderr)
        return 2
    key = os.environ.get("APP_API_KEY", "")
    if not key:
        print("APP_API_KEY is not set in this shell (use the same value as the server's .env)", file=sys.stderr)
        return 2
    log_path = REPO_ROOT / "results" / plan["env"] / "cloud_run.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log:
        sys.stdout = _Tee(sys.__stdout__, log)
        print(f"\n##### {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} cloud run: target={a.target} "
              f"blocks={a.blocks or 'all'} retry_invalid={a.retry_invalid}")
        try:
            run_plan(plan, http_sender(a.target, key), a.target, blocks=a.blocks, retry_invalid=a.retry_invalid)
        finally:
            sys.stdout = sys.__stdout__
    return 0


class _Tee:
    """Console output also goes to results/<env>/cloud_run.log (a run log for the report)."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, s: str) -> int:
        for st in self.streams:
            st.write(s)
            st.flush()
        return len(s)

    def flush(self) -> None:
        for st in self.streams:
            st.flush()


if __name__ == "__main__":
    sys.exit(main())
