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
             quiet: bool = False) -> int:
    n = 0
    for i, b in enumerate(plan["blocks"], 1):
        if not quiet:
            print(f"\n=== block {i}/{len(plan['blocks'])}: {b} ===", flush=True)
            warm_up_block(send, b)
        n += len(run(b["models"], b["apps"], b["defense"], plan["env"], target=target, variants=b["variants"],
                     out_dir=out_dir, send=send, quiet=quiet, warmup=False))
    return n


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", required=True, help="server base URL, e.g. http://1.2.3.4:8000")
    ap.add_argument("--plan", default=str(CLOUD_CONFIG))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    plan = load_plan(Path(a.plan))
    if a.dry_run:
        for i, b in enumerate(plan["blocks"], 1):
            print(f"block {i}: {b} -> {block_trials(b)} trials")
        print("total", sum(block_trials(b) for b in plan["blocks"]), "trials")
        return 0
    key = os.environ.get("APP_API_KEY", "")
    if not key:
        print("APP_API_KEY is not set in this shell (use the same value as the server's .env)", file=sys.stderr)
        return 2
    run_plan(plan, http_sender(a.target, key), a.target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
