"""Summarize results/**/*.jsonl into markdown tables (ASR + Wilson CI, utility, latency, invalid counts).

  python -m llmsec.harness.report results --out reports/results_summary.md
  python -m llmsec.harness.report results --compare-defense none layered      # paired McNemar per cell
  python -m llmsec.harness.report results --compare-env local aws             # same model, same trials
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .stats import mean, paired, percentile, wilson


def load(paths: Iterable[Path]) -> list[dict[str, Any]]:
    recs: dict[tuple, dict[str, Any]] = {}
    for root in paths:
        files = [root] if root.is_file() else sorted(root.rglob("*.jsonl"))
        for f in files:
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    recs[(r["env"], r["model"], r["defense"], r["trial_id"])] = r  # last write wins (retries)
    return list(recs.values())


def _fmt(p: float) -> str:
    return "–" if p != p else f"{100 * p:.1f}"


def summary_rows(recs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for r in recs:
        groups[(r["env"], r["model"], r["app"], r["defense"], r["cell"])].append(r)
    rows = []
    for (env, model, app, defense, cell), rs in sorted(groups.items()):
        valid = [r for r in rs if r["eval"]["valid"]]
        k = sum(r["eval"]["success"] for r in valid)
        lo, hi = wilson(k, len(valid))
        lat = [r["wall_ms"] for r in rs]
        rows.append({"env": env, "model": model, "app": app, "defense": defense, "cell": cell,
                     "kind": rs[0]["kind"], "n": len(valid), "k": k, "rate": k / len(valid) if valid else float("nan"),
                     "lo": lo, "hi": hi, "invalid": len(rs) - len(valid),
                     "lat_mean_s": mean(lat) / 1000, "lat_p95_s": percentile(lat, 0.95) / 1000})
    return rows


def summary_markdown(recs: list[dict[str, Any]]) -> str:
    rows = summary_rows(recs)
    lines = ["| env | model | app | defense | cell | metric | k/n | rate % | 95% CI | invalid | mean s | p95 s |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        metric = "utility" if r["kind"] == "clean" else "ASR"
        lines.append(f"| {r['env']} | {r['model']} | {r['app']} | {r['defense']} | {r['cell']} | {metric} | "
                     f"{r['k']}/{r['n']} | {_fmt(r['rate'])} | {_fmt(r['lo'])}–{_fmt(r['hi'])} | {r['invalid']} | "
                     f"{r['lat_mean_s']:.2f} | {r['lat_p95_s']:.2f} |")
    return "\n".join(lines)


def _success_map(recs, **where) -> dict[tuple, dict[str, bool]]:
    out: dict[tuple, dict[str, bool]] = defaultdict(dict)
    for r in recs:
        if all(r[k] == v for k, v in where.items()) and r["eval"]["valid"]:
            out[(r["model"], r["app"], r["cell"])][r["trial_id"]] = r["eval"]["success"]
    return out


def compare_markdown(recs, field: str, a: str, b: str) -> str:
    ma, mb = _success_map(recs, **{field: a}), _success_map(recs, **{field: b})
    lines = [f"| model | app | cell | n paired | {a} % | {b} % | only {a} | only {b} | McNemar p |",
             "|---|---|---|---|---|---|---|---|---|"]
    for key in sorted(set(ma) & set(mb)):
        s = paired(ma[key], mb[key])
        lines.append(f"| {key[0]} | {key[1]} | {key[2]} | {s['n']} | {_fmt(s['rate_a'])} | {_fmt(s['rate_b'])} | "
                     f"{s['only_a']} | {s['only_b']} | {s['p_mcnemar']:.3g} |")
    if field == "env":
        same = _identical_outputs(recs, a, b)
        lines.append(f"\nIdentical outputs {a} vs {b}: {same[0]}/{same[1]} paired trials.")
    return "\n".join(lines)


def _identical_outputs(recs, a: str, b: str) -> tuple[int, int]:
    by: dict[tuple, dict[str, str]] = defaultdict(dict)
    for r in recs:
        if r["env"] in (a, b):
            by[(r["model"], r["defense"], r["trial_id"])][r["env"]] = r["response"].get("output", "")
    pairs = [v for v in by.values() if a in v and b in v]
    return sum(v[a] == v[b] for v in pairs), len(pairs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out")
    ap.add_argument("--compare-defense", nargs=2, metavar=("A", "B"))
    ap.add_argument("--compare-env", nargs=2, metavar=("A", "B"))
    a = ap.parse_args(argv)
    recs = load(Path(p) for p in a.paths)
    if a.compare_defense:
        md = compare_markdown(recs, "defense", *a.compare_defense)
    elif a.compare_env:
        md = compare_markdown(recs, "env", *a.compare_env)
    else:
        md = summary_markdown(recs)
    if a.out:
        Path(a.out).write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
