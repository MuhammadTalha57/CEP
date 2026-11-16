"""Figures for the reports and the paper, computed from results/ (never typed in by hand).

  python scripts/make_figures.py      # writes reports/figs/*.png and paper/figs/*.pdf

Colors: validated categorical palette (dataviz reference, light mode, fixed order); every bar carries a
direct value label and every figure has a table in reports/ (contrast relief for the lighter slots).
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmsec.harness.report import load  # noqa: E402
from llmsec.harness.stats import percentile, wilson  # noqa: E402

SLOTS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
INK, MUTED, GRID = "#262624", "#6b6a64", "#e4e3de"
MODELS = ["qwen3-1.7b", "llama3.2-3b", "gemma3-1b", "qwen3-4b-instruct"]
APPS = [("chatbot", "Chatbot (App A)"), ("rag", "RAG (App B)"), ("agent", "Agent (App C)")]
DEFS = [("none", "none"), ("d1_detector", "D1 detector"), ("d2_sanitize", "D2 sanitize"),
        ("d3_spotlight", "D3 spotlight"), ("d4_toolpolicy", "D4 tool policy"), ("layered", "Layered (ours)")]
OUT_PNG, OUT_PDF = ROOT / "reports" / "figs", ROOT / "paper" / "figs"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK, "text.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False})


def save(fig, name):
    OUT_PNG.mkdir(parents=True, exist_ok=True)
    OUT_PDF.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_PNG / f"{name}.png", dpi=200, bbox_inches="tight", facecolor="white")
    fig.savefig(OUT_PDF / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def rate(recs, **where):
    rs = [r for r in recs if r["eval"]["valid"] and all(r[k] == v for k, v in where.items())]
    k = sum(r["eval"]["success"] for r in rs)
    return (k, len(rs))


def grouped(ax, groups, series, values, colors, ylabel, ymax=100):
    """values[g][s] = (k, n) or None. Bars with a 2px gap, value label on top, Wilson CI whisker."""
    n_s = len(series)
    width = 0.8 / n_s
    for si, (s, label) in enumerate(series):
        xs, hs, lo, hi = [], [], [], []
        for gi, g in enumerate(groups):
            v = values[g].get(s)
            if not v or not v[1]:
                continue
            k, n = v
            p = 100 * k / n
            l, h = wilson(k, n)
            xs.append(gi - 0.4 + width * (si + 0.5))
            hs.append(p)
            lo.append(p - 100 * l)
            hi.append(100 * h - p)
        ax.bar(xs, hs, width * 0.92, color=colors[si], label=label, edgecolor="white", linewidth=0.6, zorder=2)
        ax.errorbar(xs, hs, yerr=[lo, hi], fmt="none", ecolor=MUTED, elinewidth=0.7, capsize=1.5, zorder=3)
        for x, h, up in zip(xs, hs, hi):
            ax.text(x, h + up + 0.8, f"{h:.0f}", ha="center", va="bottom", fontsize=6.5, color=INK, zorder=4)
    ax.set_ylim(0, ymax)
    ax.set_ylabel(ylabel)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


def fig_baseline(recs):
    vals = {a: {m: rate(recs, env="kaggle", defense="none", app=a, model=m, kind="attack") for m in MODELS}
            for a, _ in APPS}
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    grouped(ax, [a for a, _ in APPS], [(m, m) for m in MODELS], vals, SLOTS, "Attack success rate (%)", 105)
    ax.set_xticks(range(len(APPS)), [l for _, l in APPS])
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.18), fontsize=8)
    ax.set_title("Baseline (no defense), attack cells pooled per app; whiskers = Wilson 95% CI", fontsize=8.5,
                 color=MUTED, pad=24)
    save(fig, "fig_baseline_asr")


def fig_defenses(recs):
    vals = {a: {d: rate(recs, env="kaggle", defense=d, app=a, kind="attack") for d, _ in DEFS} for a, _ in APPS}
    for a in vals:
        for d in list(vals[a]):
            if vals[a][d][1] == 0:
                vals[a][d] = None
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    grouped(ax, [a for a, _ in APPS], DEFS, vals, SLOTS, "Attack success rate (%)", 60)
    ax.set_xticks(range(len(APPS)), [l for _, l in APPS])
    ax.legend(ncol=6, loc="upper center", bbox_to_anchor=(0.5, 1.18), fontsize=7.5)
    ax.set_title("Pooled over models and attack cells (Kaggle); missing bar = defense not applicable to that app",
                 fontsize=8.5, color=MUTED, pad=24)
    save(fig, "fig_defense_asr")


def fig_rag_carriers(recs):
    cells = [("T7@C1", "C1 visible text"), ("T7@C2", "C2 hidden HTML"), ("T7@C3", "C3 alt/ARIA"),
             ("T7@C4", "C4 zero-width"), ("T7@C5", "C5 PDF white text"), ("T7@C6", "C6 PDF 0.1 pt"),
             ("T7@C7", "C7 PDF metadata"), ("H1@C2", "H1 = T4 in C2 (ours)"), ("H1@C5", "H1 = T4 in C5 (ours)")]
    series = [("none", "none"), ("d2_sanitize", "D2 sanitize"), ("layered", "Layered (ours)")]
    colors = [SLOTS[0], SLOTS[2], SLOTS[5]]
    vals = {c: {d: rate(recs, env="kaggle", defense=d, app="rag", cell=c) for d, _ in series} for c, _ in cells}
    fig, ax = plt.subplots(figsize=(7.0, 2.9))
    grouped(ax, [c for c, _ in cells], series, vals, colors, "Attack success rate (%)", 80)
    ax.set_xticks(range(len(cells)), [l for _, l in cells], rotation=25, ha="right", fontsize=7.5)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.16), fontsize=8)
    ax.set_title("RAG carriers, T7 unless noted, pooled over 4 models (n = 120 per bar)", fontsize=8.5, color=MUTED,
                 pad=22)
    save(fig, "fig_rag_carriers")


def fig_cloud(recs):
    recs = [r for r in recs if r["eval"]["valid"]]
    kag = {(r["model"], r["app"], r["defense"], r["trial_id"]): r for r in recs if r["env"] == "kaggle"}
    g = defaultdict(list)
    for r in recs:
        if r["env"] == "aws":
            k = (r["model"], r["app"], r["defense"], r["trial_id"])
            if k in kag:
                g[(r["model"], r["app"], r["defense"])].append((kag[k], r))
    keys = sorted(g)
    labels = [f"{m.split('-')[0]}\n{a}\n{d}" for m, a, d in keys]
    srv = lambda r: r["response"].get("server_ms", r["wall_ms"]) / 1000
    k_med = [percentile([srv(a) for a, _ in g[k]], 0.5) for k in keys]
    a_med = [percentile([srv(b) for _, b in g[k]], 0.5) for k in keys]
    fig, ax = plt.subplots(figsize=(7.0, 2.8))
    w = 0.38
    xs = range(len(keys))
    ax.bar([x - w / 2 for x in xs], k_med, w * 0.92, color=SLOTS[0], label="Kaggle (GPU, in process)", zorder=2)
    ax.bar([x + w / 2 for x in xs], a_med, w * 0.92, color=SLOTS[1], label="AWS EC2 (CPU, Docker, HTTP)", zorder=2)
    for x, v in zip(xs, k_med):
        ax.text(x - w / 2, v * 1.08, f"{v:.2f}", ha="center", fontsize=6.5)
    for x, v in zip(xs, a_med):
        ax.text(x + w / 2, v * 1.08, f"{v:.1f}", ha="center", fontsize=6.5)
    ax.set_yscale("log")
    ax.set_ylabel("Median server time per trial (s, log)")
    ax.set_xticks(list(xs), labels, fontsize=6.8)
    ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.16), fontsize=8)
    save(fig, "fig_cloud_latency")


def fig_architecture():
    """System overview: harness, the two deployments, the server with apps + defense hooks, Ollama."""
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    fig, ax = plt.subplots(figsize=(11.5, 4.9))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 44)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#f4f3ef", ec=MUTED, bold=False, fs=7.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=fc, ec=ec, lw=0.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
                fontweight="bold" if bold else "normal", color=INK, linespacing=1.25)

    def arrow(x1, y1, x2, y2, text="", dy=1.2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=8, lw=0.8, color=INK))
        if text:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, text, ha="center", fontsize=6.4, color=MUTED)

    # harness
    box(1, 27, 19, 13, "Harness (attacker side)\n\ntrial generator\nT1-T7 x C0-C9 + H1-H3\n30 variants per cell\n"
                       "runner, checker, statistics", fs=7.6)
    box(1, 9, 19, 11, "JSONL logs\n\nresults/<env>/<model>/\n<app>__<defense>.jsonl", fc="#ffffff", fs=7.6)
    arrow(10.5, 27, 10.5, 20.4)
    # deployments (two lanes between harness and server)
    arrow(20.6, 36, 37.4, 36)
    ax.text(29, 37.4, "Kaggle: in process\n(2x T4 GPU)", ha="center", va="bottom", fontsize=7, color=MUTED)
    arrow(20.6, 29, 37.4, 29)
    ax.text(29, 27.6, "AWS: HTTP + API key\n(EC2 m7i-flex.large, CPU,\nDocker Compose)", ha="center", va="top",
            fontsize=7, color=MUTED)
    # server
    ax.add_patch(FancyBboxPatch((38, 3), 44, 39, boxstyle="round,pad=0.4,rounding_size=1.5", fc="#ffffff",
                                ec=MUTED, lw=0.8, ls="--"))
    ax.text(60, 40.2, "App server: FastAPI /v1/run (identical code on Kaggle and AWS)", ha="center",
            fontsize=7.6, color=MUTED)
    box(40, 27, 12.5, 9.5, "App A\nchatbot\nsecret in prompt", fc="#e8f1fc", fs=7.4)
    box(53.8, 27, 12.5, 9.5, "App B\nRAG (BM25)\n20 HTML/PDF docs", fc="#e8f1fc", fs=7.4)
    box(67.6, 27, 12.5, 9.5, "App C\ntool agent\nmock email/files", fc="#e8f1fc", fs=7.4)
    box(40, 13.5, 40.1, 9, "Defense hooks: check_input, sanitize_document, wrap_untrusted,\nsystem_addendum, "
                           "check_tool_call, check_output\n(D1 detector, D2 sanitize, D3 spotlight, D4 policy, layered)",
        fc="#eaf6ef", fs=7.2)
    box(40, 4.5, 40.1, 5.5, "LLMClient: OpenAI-compatible, temperature 0, fixed seed", fs=7.4)
    for x in (46.2, 60, 73.8):
        arrow(x, 27, x, 22.9)
    arrow(60, 13.5, 60, 10.4)
    # ollama
    box(86, 3, 13, 14, "Ollama 0.40.16\n\nqwen3-1.7b\nllama3.2-3b\ngemma3-1b\nqwen3-4b-instruct", fc="#fdf3e1", fs=7.2)
    arrow(80.6, 7.2, 85.6, 7.2)
    save(fig, "fig_architecture")


def main():
    fig_architecture()
    recs = load([ROOT / "results" / "kaggle", ROOT / "results" / "aws"])
    fig_baseline(recs)
    fig_defenses(recs)
    fig_rag_carriers(recs)
    fig_cloud(recs)
    print("figures written to", OUT_PNG, "and", OUT_PDF)


if __name__ == "__main__":
    main()
