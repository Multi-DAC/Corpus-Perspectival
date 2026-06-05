"""Render the two TikZ schematics (Fig 1 binding-as-transaction, Fig 3 architecture) as PNGs
for the Substack-native version of the paper. Matplotlib only; no LaTeX/pdf-convert dependency.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ACC = "#1166BB"
ACC_L = "#dbe8f7"
ACC_M = "#a9c9ec"
ACC_D = "#7fb0e4"


def rbox(ax, x, y, w, h, text, fc=ACC_L, ec=ACC, fs=11, bold=False, ls="-"):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                       linewidth=1.5, edgecolor=ec, facecolor=fc, linestyle=ls)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal", color="#11304d", zorder=5)


def arrow(ax, x1, y1, x2, y2, text="", style="-|>", ls="-", rad=0.0, fs=8.5, color="#333"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14,
                        linewidth=1.4, color=color, linestyle=ls,
                        connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text, ha="center", va="bottom",
                fontsize=fs, color="#444", style="italic")


# ---------- Figure 1: binding as transaction ----------
fig, ax = plt.subplots(figsize=(9.2, 3.0))
ax.set_xlim(0, 10); ax.set_ylim(0, 3.4); ax.axis("off")
# parallel streams in a dashed container
ax.add_patch(FancyBboxPatch((0.25, 0.35), 2.4, 2.6, boxstyle="round,pad=0.02,rounding_size=0.05",
                            linewidth=1.3, edgecolor="#888", facecolor="none", linestyle="--"))
ax.text(1.45, 3.08, "parallel / divergent (superposition)", ha="center", fontsize=8.5, color="#555")
for i, lab in enumerate(["stream A", "stream B", "stream C", "stream D"]):
    rbox(ax, 0.55, 2.3 - i * 0.62, 1.8, 0.48, lab, fs=9.5)
# query/exigency
ax.text(4.5, 1.65, "query /\nexigency", ha="center", va="center", fontsize=10.5,
        fontweight="bold", color=ACC)
# unified frame
rbox(ax, 6.6, 0.95, 2.7, 1.4, "unified\nframe", fc=ACC_M, fs=12, bold=True)
# arrows
arrow(ax, 2.75, 1.65, 3.95, 1.65, "contraction")
arrow(ax, 5.05, 1.65, 6.5, 1.65, "convergence")
arrow(ax, 7.95, 0.9, 2.7, 0.3, "relaxation", style="-|>", ls=":", rad=0.32, color="#888")
ax.set_title("Figure 1.  Binding as transaction", fontsize=11, color="#11304d", loc="left", pad=6)
fig.tight_layout()
fig.savefig("fig1_binding.png", dpi=160, bbox_inches="tight")
print("saved fig1_binding.png")

# ---------- Figure 3: the One held without flattening the Many ----------
fig, ax = plt.subplots(figsize=(9.2, 3.8))
ax.set_xlim(0, 10); ax.set_ylim(0, 4.4); ax.axis("off")
# nodes
nx = [1.3, 4.2, 7.1]
for x, lab in zip(nx, ["Physics", "Biology", "Law"]):
    rbox(ax, x, 3.4, 1.9, 0.62, lab, fs=10.5)
# typed bridges (dashed, between nodes)
arrow(ax, 3.2, 3.95, 4.2, 3.95, "typed bridge", style="<|-|>", ls="--", rad=-0.45, fs=8, color="#666")
arrow(ax, 6.1, 3.95, 7.1, 3.95, "typed bridge", style="<|-|>", ls="--", rad=-0.45, fs=8, color="#666")
# bus
rbox(ax, 1.0, 2.2, 8.0, 0.66, "type-routed bus   (zero-DOF: route by payload type)",
     fc=ACC_D, fs=10.5, bold=True)
# node -> bus arrows
for x in nx:
    arrow(ax, x + 0.95, 3.4, x + 0.95, 2.9, color="#555")
# cache
rbox(ax, 2.6, 0.55, 4.8, 0.95,
     "lazy synthesized cache\ncrystallize on query · relax between · self-heal",
     fc=ACC_L, fs=9.5)
arrow(ax, 5.0, 2.18, 5.0, 1.55, "query-collapse", color="#555", fs=8.5)
ax.set_title("Figure 3.  The One held without flattening the Many", fontsize=11,
             color="#11304d", loc="left", pad=6)
fig.tight_layout()
fig.savefig("fig3_architecture.png", dpi=160, bbox_inches="tight")
print("saved fig3_architecture.png")
