"""System architecture on AWS (paper Figure 1), drawn with AWS Architecture Icons.

    python scripts/make_aws_diagram.py   ->  paper/figs/fig_aws_architecture.pdf, reports/figs/fig_aws_architecture.png

Icons in scripts/icons/ are the AWS Architecture Icons and tool logos bundled with the `diagrams` package (MIT);
group colors follow the AWS architecture-diagram convention (cloud, region, VPC, public subnet, security group).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ICONS = ROOT / "scripts" / "icons"
INK, MUTED = "#232F3E", "#545B64"
C_CLOUD, C_REGION, C_VPC, C_SUBNET, C_SG, C_EC2 = "#232F3E", "#00A4A6", "#8C4FFF", "#7AA116", "#DD344C", "#ED7100"
DOCKER = "#1D63ED"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6.5, "text.color": INK})
W, H = 160, 80
fig, ax = plt.subplots(figsize=(7.2, 7.2 * H / W))
fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")


def icon(name, x, y, s=5.0):
    ax.imshow(mpimg.imread(ICONS / f"{name}.png"), extent=(x - s / 2, x + s / 2, y - s / 2, y + s / 2), zorder=6,
              interpolation="antialiased")


def text(x, y, s, size=6.2, color=MUTED, bold=False, ha="center", va="center"):
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color, fontweight="bold" if bold else "normal", zorder=8,
            linespacing=1.2)


def group(x, y, w, h, color, label, ico=None, dashed=False):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor=color, lw=1.0, ls=(0, (3, 2)) if dashed else "-",
                           zorder=1))
    tx = x + 1.3
    if ico:
        ax.add_patch(Rectangle((x, y + h - 4.4), 4.4, 4.4, facecolor=color, edgecolor="none", zorder=2))
        if ico != "aws":
            icon(ico, x + 2.2, y + h - 2.2, 3.7)
        else:
            text(x + 2.2, y + h - 2.2, "aws", size=5.4, color="#FF9900", bold=True)
        tx = x + 5.6
    text(tx, y + h - 2.2, label, size=6.6, color=color, bold=True, ha="left")


def box(x, y, w, h, fill, edge, lw=0.8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", facecolor=fill,
                                edgecolor=edge, lw=lw, zorder=3))


def arrow(p1, p2, both=False):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="<|-|>" if both else "-|>", mutation_scale=7, lw=0.9,
                                 color=INK, zorder=5, shrinkA=0, shrinkB=0))


# ---------------------------------------------------------------- outside AWS
icon("users", 15, 58, 9)
text(15, 51.2, "User / attacker", size=6.8, color=INK, bold=True)
text(15, 47.6, "prompt\n(direct injection)")
icon("documents", 17, 26, 8)
text(17, 19.6, "Untrusted content", size=6.8, color=INK, bold=True)
text(17, 14.6, "documents, emails, web pages\n(indirect injection)")
icon("internet", 37, 40, 7)
text(37, 34.6, "Internet")
arrow((24, 54), (33.5, 43), both=True)
arrow((24, 29), (33.5, 37.5))

# ---------------------------------------------------------------- AWS groups
group(46, 2, 112, 76, C_CLOUD, "AWS Cloud", ico="aws")
group(48, 4, 108, 68.5, C_REGION, "Region", dashed=True)
group(50, 6, 104, 61, C_VPC, "VPC", ico="vpc")
group(57, 8, 95, 53.5, C_SUBNET, "Public subnet", ico="public-subnet")
group(59, 10, 91, 46, C_SG, "Security group", dashed=True)
group(61, 12, 87, 38.5, C_EC2, "EC2 instance", ico="ec2-instance")
icon("internet-gateway", 50, 40, 6)
arrow((40.7, 40), (47, 40), both=True)
arrow((53, 40), (67, 32), both=True)

ax.add_patch(Rectangle((64, 14), 82, 31, fill=False, edgecolor=DOCKER, lw=0.9, ls=(0, (3, 2)), zorder=2))
icon("docker", 67.4, 42.4, 4.4)
text(70.6, 42.4, "Docker Compose", size=6.6, color=DOCKER, bold=True, ha="left")

# application container
box(67, 16, 51, 23.5, "#E8F1FD", DOCKER)
icon("fastapi", 70.8, 36.4, 3.8)
text(73.6, 36.4, "LLM application container", size=6.6, color=INK, bold=True, ha="left")
for i, (t, s) in enumerate([("App A", "chatbot"), ("App B", "RAG"), ("App C", "agent")]):
    x0 = 69 + i * 16
    box(x0, 24.5, 14.5, 8.5, "white", DOCKER, lw=0.6)
    text(x0 + 7.25, 30.4, t, size=6.2, color=INK, bold=True)
    text(x0 + 7.25, 26.8, s, size=6.0)
box(69, 18, 46.5, 5, "#EAF5EA", "#3B8C3B", lw=0.6)
text(92.25, 20.5, "Defense layer (D1 to D4, layered)", size=6.0, color=INK)

# model container
box(126, 16, 18, 23.5, "#FDF3E7", C_EC2)
icon("server", 135, 33, 5)
text(135, 26.5, "Ollama", size=6.6, color=INK, bold=True)
text(135, 22.5, "open LLMs")
arrow((118, 27.5), (126, 27.5), both=True)

OUT_PNG, OUT_PDF = ROOT / "reports" / "figs", ROOT / "paper" / "figs"
OUT_PNG.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PNG / "fig_aws_architecture.png", dpi=220, facecolor="white")
fig.savefig(OUT_PDF / "fig_aws_architecture.pdf", facecolor="white")
print("wrote fig_aws_architecture.{png,pdf}")
