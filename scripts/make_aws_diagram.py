"""AWS deployment architecture diagram (paper Figure 2) with AWS Architecture Icons.

    python scripts/make_aws_diagram.py   ->  paper/figs/fig_aws_architecture.pdf, reports/figs/fig_aws_architecture.png

Icons in scripts/icons/ are the AWS Architecture Icons and tool logos bundled with the `diagrams` package (MIT);
group colors follow the AWS architecture-diagram convention (cloud, region, VPC, public subnet, security group).
Numbered markers refer to the flow legend under the diagram.
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

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6, "text.color": INK})
W, H = 160, 92
fig, ax = plt.subplots(figsize=(7.2, 7.2 * H / W))
fig.subplots_adjust(0, 0, 1, 1)
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")


def icon(name, x, y, s=5.0):
    img = mpimg.imread(ICONS / f"{name}.png")
    ax.imshow(img, extent=(x - s / 2, x + s / 2, y - s / 2, y + s / 2), zorder=6, interpolation="antialiased")


def text(x, y, s, size=5.6, color=MUTED, bold=False, ha="center", va="center", bg=False, z=8):
    kw = dict(bbox=dict(facecolor="white", edgecolor="none", pad=0.3)) if bg else {}
    ax.text(x, y, s, ha=ha, va=va, fontsize=size, color=color, fontweight="bold" if bold else "normal",
            zorder=z, linespacing=1.2, **kw)


def group(x, y, w, h, color, label, ico=None, dashed=False, fs=6.0):
    ax.add_patch(Rectangle((x, y), w, h, fill=False, edgecolor=color, lw=0.9, ls=(0, (3, 2)) if dashed else "-",
                           zorder=1))
    tx = x + 1.2
    if ico:
        ax.add_patch(Rectangle((x, y + h - 4.4), 4.4, 4.4, facecolor=color, edgecolor="none", zorder=2))
        icon(ico, x + 2.2, y + h - 2.2, 3.7)
        tx = x + 5.4
    text(tx, y + h - 2.2, label, size=fs, color=color, bold=True, ha="left")


def box(x, y, w, h, fill, edge):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", facecolor=fill,
                                edgecolor=edge, lw=0.7, zorder=3))


def line(pts, color=INK, ls="-", head=True, tail=False):
    """Polyline with an arrowhead on the last segment (and optionally on the first)."""
    for (x1, y1), (x2, y2) in zip(pts[:-2], pts[1:-1]):
        ax.plot([x1, x2], [y1, y2], color=color, lw=0.8, ls=ls, zorder=5, solid_capstyle="butt")
    style = ("<|-|>" if tail and len(pts) == 2 else "-|>") if head else "-"
    ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle=style, mutation_scale=6.5, lw=0.8, color=color,
                                 ls=ls, zorder=5, shrinkA=0, shrinkB=0))
    if tail and len(pts) > 2:
        ax.add_patch(FancyArrowPatch(pts[1], pts[0], arrowstyle="-|>", mutation_scale=6.5, lw=0.8, color=color,
                                     zorder=5, shrinkA=0, shrinkB=0))


def marker(x, y, n):
    ax.text(x, y, str(n), ha="center", va="center", fontsize=5.2, color="white", fontweight="bold", zorder=9,
            bbox=dict(boxstyle="circle,pad=0.22", facecolor=INK, edgecolor="none"))


# ---------------------------------------------------------------- outside AWS (left)
box(1, 55, 32, 35, "#F4F5F6", MUTED)
icon("client", 8.5, 83.5, 7.0)
icon("python", 17.5, 83.5, 5.0)
icon("key", 26, 83.5, 4.6)
text(17, 76.2, "Tester laptop", size=6.6, color=INK, bold=True)
text(17, 73.0, "(attacker, outside AWS)")
text(17, 63.5, "llmsec.harness.cloud\nsame trial ids, seeds and\npayloads as on Kaggle\ndeterministic canary checks")

box(1, 14, 32, 32, "#F4F5F6", MUTED)
icon("python", 17, 40.5, 5.0)
text(17, 34.0, "Kaggle notebook", size=6.6, color=INK, bold=True)
text(17, 30.8, "(development deployment)")
text(17, 22.0, "2x NVIDIA T4 GPU\nharness, apps and Ollama\nin one process\n19,020 trials, 4 models")

line([(17, 46), (17, 55)], tail=True)
marker(20.5, 50.5, 4)

icon("internet", 42, 72, 6.0)
text(42, 67.6, "Internet")
icon("github", 41, 31, 5.0)
text(41, 26.6, "GitHub repo")

# ---------------------------------------------------------------- AWS groups
group(49, 13, 110, 78, C_CLOUD, "AWS Cloud")
ax.add_patch(Rectangle((49, 86.6), 4.4, 4.4, facecolor=INK, edgecolor="none", zorder=2))
text(51.2, 88.8, "aws", size=5.4, color="#FF9900", bold=True)
ax.texts[-2].set_x(54.6)  # move the "AWS Cloud" label right of the logo square
group(51, 15, 106, 69.5, C_REGION, "Region: Asia Pacific (Sydney) ap-southeast-2", dashed=True)
group(53, 17, 102, 62.5, C_VPC, "VPC (default)", ico="vpc")
icon("internet-gateway", 53, 64, 5.6)
text(53, 58.4, "Internet\ngateway", size=5.2, bg=True)
group(60, 19, 93, 54.5, C_SUBNET, "Public subnet (public IPv4)", ico="public-subnet")
group(62, 21, 89, 47.5, C_SG, "Security group cep-lab-sg: inbound TCP 22 and 8000 from the tester's IP only",
      dashed=True, fs=5.6)
group(64, 23, 85, 40, C_EC2, "EC2 m7i-flex.large: Ubuntu 24.04, 2 vCPU, 8 GB RAM, no GPU", ico="ec2-instance",
      fs=5.8)

ax.add_patch(Rectangle((67, 25), 60, 31, fill=False, edgecolor=DOCKER, lw=0.8, ls=(0, (3, 2)), zorder=2))
icon("docker", 70.4, 52.6, 4.6)
text(73.6, 52.6, "Docker Compose", size=5.8, color=DOCKER, bold=True, ha="left")

box(69, 27, 31, 22.5, "#E8F1FD", DOCKER)
icon("fastapi", 73, 46, 4.2)
text(75.8, 46, "app :8000", size=6.0, color=INK, bold=True, ha="left")
text(84.5, 35.6, "FastAPI: POST /v1/run\nX-API-Key check\nApps A, B, C\nD1 to D4, layered\nD1 DeBERTa on CPU", size=5.3)

box(106, 27, 19, 22.5, "#FDF3E7", C_EC2)
icon("server", 109, 46, 3.8)
text(111.4, 46, "ollama", size=6.0, color=INK, bold=True, ha="left")
text(115.5, 35.6, ":11434\nimage 0.40.16\ngemma3:1b\nllama3.2:3b", size=5.3)
line([(100, 38), (106, 38)], tail=True)
marker(103, 41.2, 3)

icon("ebs", 138, 48, 5.4)
text(138, 42.3, "EBS gp3 30 GB\nmodels, images", size=5.2)
icon("key", 138, 33, 4.4)
text(138, 28.0, ".env API key\n(chmod 600)", size=5.2)

# ---------------------------------------------------------------- flows
line([(33, 76), (38.8, 73.5)], tail=True)                      # 1: laptop <-> internet (HTTP)
line([(45.2, 72), (50.2, 65.5)], tail=True)                     #    internet <-> IGW
line([(55.8, 65), (57.6, 65), (57.6, 40), (69, 40)], tail=True)  #    IGW <-> app container
marker(35.6, 77.8, 1)
line([(33, 69), (39.3, 70.3)], color=MUTED, ls=(0, (2, 1.5)))  # 2: SSH
line([(44.8, 69.6), (50.6, 62.4)], color=MUTED, ls=(0, (2, 1.5)))
line([(55.6, 62.4), (58.9, 62.4), (58.9, 32), (64, 32)], color=MUTED, ls=(0, (2, 1.5)))
marker(36.0, 66.6, 2)
line([(37.6, 31), (33, 31)], color=MUTED, ls=(0, (2, 1.5)))     # 5: code from GitHub
line([(43.6, 29), (64, 29)], color=MUTED, ls=(0, (2, 1.5)))
marker(46.5, 31.6, 5)

# ---------------------------------------------------------------- legend
ax.add_patch(Rectangle((1, 0.6), 158, 11, facecolor="#F4F5F6", edgecolor="none", zorder=1))
items = [
    (1, "HTTP :8000, POST /v1/run with X-API-Key;\nJSON reply (1,350 paired trials)"),
    (2, "SSH :22 with key pair; aws_setup.sh installs\nDocker, clones the repo, pulls models"),
    (3, "OpenAI-compatible API inside the host,\ntemperature 0, fixed seed per trial"),
    (4, "paired comparison of Kaggle and AWS\nlogs on identical trial ids (McNemar)"),
    (5, "same code and configs from GitHub\nfor both deployments"),
]
xs = [3, 56, 108, 3, 56]
ys = [8.6, 8.6, 8.6, 3.4, 3.4]
for (n, s), x, y in zip(items, xs, ys):
    marker(x + 1, y, n)
    text(x + 3.4, y, s, size=5.1, color=INK, ha="left")
text(108, 3.4, "solid: attack traffic\ndashed: administration and code", size=5.1, color=MUTED, ha="left")

OUT_PNG, OUT_PDF = ROOT / "reports" / "figs", ROOT / "paper" / "figs"
OUT_PNG.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT_PNG / "fig_aws_architecture.png", dpi=220, facecolor="white")
fig.savefig(OUT_PDF / "fig_aws_architecture.pdf", facecolor="white")
print("wrote fig_aws_architecture.{png,pdf}")
