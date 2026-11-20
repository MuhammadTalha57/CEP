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
APPS = [("chatbot", "Chatbot (App A, direct)"), ("rag", "RAG (App B, indirect)"), ("agent", "Agent (App C, indirect)")]
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


def fig_direct_indirect(recs):
    """Direct (App A, user message) versus indirect (Apps B and C, documents and tool outputs), no defense."""
    base = [r for r in recs if r["env"] == "kaggle" and r["defense"] == "none" and r["kind"] == "attack"]
    for r in base:
        r["_ch"] = "direct" if r["app"] == "chatbot" else "indirect"
    groups = MODELS + ["pooled"]
    vals = {m: {ch: rate([r for r in base if m == "pooled" or r["model"] == m], _ch=ch)
                for ch in ("direct", "indirect")} for m in groups}
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    grouped(ax, groups, [("direct", "Direct: user message (App A)"),
                         ("indirect", "Indirect: documents and tool outputs (Apps B, C)")],
            vals, [SLOTS[0], SLOTS[1]], "Attack success rate (%)", 100)
    ax.set_xticks(range(len(groups)), ["qwen3-1.7b", "llama3.2-3b", "gemma3-1b", "qwen3-4b-instruct",
                                       "Pooled"])
    ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.2), fontsize=8)
    ax.set_title("No defense (Kaggle), attack cells pooled; whiskers = Wilson 95% CI", fontsize=8.5, color=MUTED,
                 pad=24)
    save(fig, "fig_direct_indirect")


TECHS = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]


def fig_direct(recs):
    """Direct injection (App A, C0): ASR per technique and model, no defense."""
    base = [r for r in recs if r["env"] == "kaggle" and r["defense"] == "none" and r["app"] == "chatbot"
            and r["kind"] == "attack"]
    groups = TECHS + ["H2"]
    vals = {t: {m: rate(base, technique=t, model=m) for m in MODELS} for t in groups}
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    grouped(ax, groups, [(m, m) for m in MODELS], vals, SLOTS, "Attack success rate (%)", 112)
    ax.set_xticks(range(len(groups)), ["T1\nnaive", "T2\nignore", "T3 fake\ncompletion", "T4\nescape", "T5\nrole",
                                       "T6\nauthority", "T7\ncombined", "H2 split\n(ours)"], fontsize=7.5)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.2), fontsize=8)
    ax.set_title("Direct injection, App A (user message), no defense; n = 30 per bar", fontsize=8.5, color=MUTED,
                 pad=24)
    save(fig, "fig_direct")


def fig_indirect(recs):
    """Indirect injection: (a) technique in a RAG document vs an agent email; (b) carriers, no defense."""
    base = [r for r in recs if r["env"] == "kaggle" and r["defense"] == "none" and r["kind"] == "attack"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.6), gridspec_kw={"width_ratios": [1, 1.25]})
    vals = {t: {"rag": rate(base, app="rag", cell=f"{t}@C1"), "agent": rate(base, app="agent", cell=f"{t}@C8")}
            for t in TECHS}
    grouped(a1, TECHS, [("rag", "Document in RAG (C1)"), ("agent", "Email to agent (C8)")], vals,
            [SLOTS[1], SLOTS[3]], "Attack success rate (%)", 95)
    a1.set_xticks(range(len(TECHS)), TECHS, fontsize=7.5)
    a1.legend(ncol=1, loc="upper right", fontsize=7)
    a1.set_title("(a) by technique, pooled over models", fontsize=8, color=MUTED)
    cells = [("rag", "T7@C1", "C1 visible"), ("rag", "T7@C2", "C2 hidden"), ("rag", "T7@C3", "C3 alt"),
             ("rag", "T7@C4", "C4 zero-w."), ("rag", "T7@C5", "C5 white"), ("rag", "T7@C6", "C6 tiny"),
             ("rag", "T7@C7", "C7 meta"), ("agent", "T7@C8", "C8 email"), ("agent", "T7@C9", "C9 web"),
             ("rag", "H1@C2", "H1 (ours)"), ("rag", "H3@C2+C4", "H3 (ours)")]
    vals2 = {lab: {"x": rate(base, app=a, cell=c)} for a, c, lab in cells}
    grouped(a2, [lab for *_, lab in cells], [("x", "T7 unless noted")], vals2, [SLOTS[1]], "", 80)
    a2.set_xticks(range(len(cells)), [lab for *_, lab in cells], rotation=45, ha="right", fontsize=7)
    a2.set_title("(b) by carrier (T7 unless noted)", fontsize=8, color=MUTED)
    fig.tight_layout(w_pad=1.0)
    save(fig, "fig_indirect")


# Values reported in prior work (paper + page, literature/facts.md); not comparable: different prompts and checkers.
PRIOR = {
    "direct": [("qwen3-1.7b", 71.3), ("llama3.2-3b", 0.0), ("gemma3-1b", 62.8), ("qwen3-4b", 0.0)],  # P05 p7
    "pdf": [("C5 white", 50.83), ("C6 tiny", 49.33), ("C7 metadata", 43.17)],                          # P13 p5
    "ragdef": [("No defense", 24.9), ("All defenses", 4.7)],                                          # P04 p3
}


def fig_prior_vs_ours(recs):
    base = [r for r in recs if r["env"] == "kaggle" and r["kind"] == "attack"]
    none = [r for r in base if r["defense"] == "none"]
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 2.5), gridspec_kw={"width_ratios": [1.35, 1, 0.8]})
    ours_direct = [rate(none, app="chatbot", model=m) for m in MODELS]
    ours_pdf = [rate(none, app="rag", cell=c) for c in ("T7@C5", "T7@C6", "T7@C7")]
    ours_def = [rate(none, app="rag"), rate([r for r in base if r["defense"] == "layered"], app="rag")]
    panels = [("(a) Direct, same models\nprior: Jaiswal et al.", PRIOR["direct"], ours_direct),
              ("(b) Indirect, PDF carriers\nprior: Guler and Aydin", PRIOR["pdf"], ours_pdf),
              ("(c) RAG defense\nprior: Guo and Wei", PRIOR["ragdef"], ours_def)]
    for ax, (title, prior, ours) in zip(axs, panels):
        xs = range(len(prior))
        w = 0.38
        ax.bar([x - w / 2 for x in xs], [v for _, v in prior], w * 0.92, color="#a7a59c", label="Reported in prior work",
               zorder=2)
        ax.bar([x + w / 2 for x in xs], [100 * k / n for k, n in ours], w * 0.92, color=SLOTS[0], label="This work",
               zorder=2)
        for x, (_, v), (k, n) in zip(xs, prior, ours):
            ax.text(x - w / 2, v + 1.5, f"{v:.0f}", ha="center", fontsize=6.3)
            ax.text(x + w / 2, 100 * k / n + 1.5, f"{100 * k / n:.0f}", ha="center", fontsize=6.3)
        ax.set_xticks(list(xs), [l for l, _ in prior], fontsize=6.8, rotation=20 if len(prior) > 3 else 0)
        ax.set_ylim(0, 100)
        ax.set_title(title, fontsize=7.5, color=MUTED)
        ax.yaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
        ax.set_axisbelow(True)
    axs[0].set_ylabel("Attack success rate (%)")
    h, l = axs[0].get_legend_handles_labels()
    fig.tight_layout(w_pad=0.8, rect=(0, 0, 1, 0.9))
    fig.legend(h, l, ncol=2, loc="upper center", fontsize=8, frameon=False)
    save(fig, "fig_prior_vs_ours")


def fig_combined(recs):
    """No defense vs best existing defense (per app) vs layered, per channel and overall."""
    base = [r for r in recs if r["env"] == "kaggle" and r["kind"] == "attack"]
    best = {"chatbot": "d1_detector", "rag": "d1_detector", "agent": "d4_toolpolicy"}

    def pooled(apps, which):
        k = n = 0
        for a in apps:
            d = {"none": "none", "layered": "layered", "best": best[a]}[which]
            kk, nn = rate(base, app=a, defense=d)
            k, n = k + kk, n + nn
        return (k, n)

    groups = [("Direct\n(App A)", ["chatbot"]), ("Indirect: RAG\n(App B)", ["rag"]),
              ("Indirect: agent\n(App C)", ["agent"]), ("All channels", ["chatbot", "rag", "agent"])]
    vals = {g: {w: pooled(apps, w) for w in ("none", "best", "layered")} for g, apps in groups}
    fig, ax = plt.subplots(figsize=(7.0, 2.5))
    grouped(ax, [g for g, _ in groups], [("none", "No defense"), ("best", "Best existing defense (D1 or D4)"),
                                         ("layered", "Layered defense (ours)")], vals,
            ["#a7a59c", SLOTS[3], SLOTS[2]], "Attack success rate (%)", 55)
    ax.set_xticks(range(len(groups)), [g for g, _ in groups], fontsize=8)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.2), fontsize=8)
    ax.set_title("Pooled over models and attack cells (Kaggle); whiskers = Wilson 95% CI", fontsize=8.5,
                 color=MUTED, pad=24)
    save(fig, "fig_combined")


def main():
    recs = load([ROOT / "results" / "kaggle", ROOT / "results" / "aws"])
    fig_baseline(recs)
    fig_direct(recs)
    fig_indirect(recs)
    fig_prior_vs_ours(recs)
    fig_combined(recs)
    fig_direct_indirect(recs)
    fig_defenses(recs)
    fig_rag_carriers(recs)
    fig_cloud(recs)
    print("figures written to", OUT_PNG, "and", OUT_PDF)


if __name__ == "__main__":
    main()
