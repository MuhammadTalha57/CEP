"""Timing pilot (design.md §4.4, step 4.7): a few trials per app and model -> seconds per trial and
an estimate of the full matrix runtime. Also checks things the design marked "verify in pilot":
model reachable, tool calling works (App C), qwen3 thinking really off, error rate.

  python -m llmsec.harness.pilot --models qwen3-1.7b llama3.2-3b gemma3-1b
  python -m llmsec.harness.pilot --models qwen3-1.7b --target http://<host>:8000 --env aws-pilot

Writes results/<env>/... (normal JSONL logs) and reports/pilot_<env>.md.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

from ..attacks.generator import REPO_ROOT, generate, load_experiment
from ..llm.factory import load_specs
from .run import run
from .stats import mean

PILOT_CELLS = {"chatbot": ["T2@C0", "T7@C0"], "rag": ["T7@C1", "T7@C5"], "agent": ["T7@C8", "T2@C8"]}
PILOT_VARIANTS = 2
PILOT_CLEAN = 3


def check_backend(model_id: str) -> tuple[bool, str]:
    spec = load_specs()[model_id]
    if spec.backend != "openai_compat":
        return True, "non-HTTP backend"
    try:
        r = httpx.get(spec.base_url.rstrip("/") + "/models", timeout=10)
        names = [m.get("id") for m in r.json().get("data", [])]
        ver = ""
        try:
            ver = httpx.get(spec.base_url.rstrip("/").removesuffix("/v1") + "/api/version", timeout=5).json()["version"]
        except Exception:  # noqa: BLE001  (not an Ollama server)
            pass
        ok = spec.model in names
        return ok, f"server ok{f', ollama {ver}' if ver else ''}; model {'found' if ok else 'NOT pulled'} ({spec.model})"
    except Exception as e:  # noqa: BLE001
        return False, f"cannot reach {spec.base_url}: {type(e).__name__}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--target", default="inproc")
    ap.add_argument("--env", default="local-pilot")
    ap.add_argument("--apps", nargs="+", default=["chatbot", "rag", "agent"])
    a = ap.parse_args(argv)

    exp = load_experiment()
    full = generate(exp)
    full_counts = {app: sum(1 for t in full if t.app == app) for app in a.apps}
    lines = [f"# Timing pilot ({a.env}, {datetime.now(timezone.utc).isoformat(timespec='minutes')})", "",
             f"Target: `{a.target}`. Pilot cells: {PILOT_CELLS}, {PILOT_VARIANTS} variants, {PILOT_CLEAN} clean tasks per app.",
             f"Full matrix trials per model per defense setting: {full_counts} (total {sum(full_counts.values())}).", ""]
    for model in a.models:
        if a.target == "inproc":
            ok, msg = check_backend(model)
            print(f"{model}: {msg}", flush=True)
            lines.append(f"## {model}\n\nBackend check: {msg}\n")
            if not ok:
                continue
        else:
            lines.append(f"## {model}\n")
        lines += ["| app | trials | invalid | mean s/trial | est. full hours | notes |", "|---|---|---|---|---|---|"]
        total_h = 0.0
        for app in a.apps:
            recs = run([model], [app], "none", a.env, a.target, variants=PILOT_VARIANTS,
                       cells=PILOT_CELLS[app], include_clean=False, experiment=None)
            clean_recs = run([model], [app], "none", a.env, a.target, cells=["U"], limit=PILOT_CLEAN)
            recs = recs + clean_recs
            if not recs:
                lines.append(f"| {app} | 0 | – | – | – | already run; delete results/{a.env} to redo |")
                continue
            secs = mean(r["wall_ms"] for r in recs) / 1000
            inval = [r for r in recs if not r["eval"]["valid"]]
            hours = secs * full_counts[app] / 3600
            total_h += hours
            notes = []
            if app == "agent":
                n_tool = sum(1 for r in recs if r["response"].get("tool_calls"))
                notes.append(f"tool calls in {n_tool}/{len(recs)} trials")
                n_text = sum(1 for r in recs if r["eval"].get("target_in_output") and not r["eval"]["success"])
                if n_text:
                    notes.append(f"text-only compliance (no tool call) in {n_text}")
            if any("<think>" in (r["response"].get("output") or "") for r in recs):
                notes.append("WARNING: <think> in output (thinking not disabled)")
            if inval:
                notes.append("invalid: " + "; ".join(sorted({r['eval']['invalid_reason'][:60] for r in inval})))
            succ = sum(r["eval"]["success"] for r in recs if r["kind"] == "attack")
            n_att = sum(1 for r in recs if r["kind"] == "attack")
            notes.append(f"attack successes {succ}/{n_att} (pilot only, not a result)")
            lines.append(f"| {app} | {len(recs)} | {len(inval)} | {secs:.1f} | {hours:.1f} | {'; '.join(notes)} |")
        lines.append(f"\n**Estimated full matrix for {model}: {total_h:.1f} h per defense setting.**\n")
    out = REPO_ROOT / "reports" / f"pilot_{a.env}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwritten: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
