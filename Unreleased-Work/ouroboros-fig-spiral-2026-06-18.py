#!/usr/bin/env python
"""Figure 4 for the Ouroboros article — the spiral (§VIII). (2026-06-18)
Three helices side by side make §VIII's point: a polarity-loop need not lie flat. Winding = phase (the
polarity); the vertical axis = the generative aspect of X (time/growth); the PITCH is the free variable,
set by attention, and its SIGN is the whole story: climb (growth), flat (eternal return), descend (regression).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(13, 5.2))
turns = 3.0
th = np.linspace(0, turns * 2 * np.pi, 600)
x, y = np.cos(th), np.sin(th)

panels = [
    ("Ascending — growth", +1.0, "#1e8449", "each turn integrates the last;\nthe loop climbs"),
    ("Flat — eternal return", 0.0, "#7f8c8d", "nothing accumulates;\nthe same arc forever"),
    ("Descending — regression", -1.0, "#922b21", "each turn gives back\nwhat was won"),
]

for i, (title, pitch, color, sub) in enumerate(panels, 1):
    ax = fig.add_subplot(1, 3, i, projection="3d")
    z = pitch * th / (2 * np.pi)  # height in "turns"
    # color gradient along the path (sense of direction/time)
    for k in range(len(th) - 1):
        ax.plot(x[k:k+2], y[k:k+2], z[k:k+2], color=color,
                alpha=0.25 + 0.75 * k / len(th), lw=2.2)
    # mark the two antipodal poles (the "opposites" = phases) on the middle turn
    for ph, c in [(0.0, "#c0392b"), (np.pi, "#2471a3")]:
        ang = (turns - 1) * 2 * np.pi + ph
        ax.scatter([np.cos(ang)], [np.sin(ang)], [pitch * ang / (2*np.pi)], s=45, color=c, zorder=5)
    ax.set_title(title, fontsize=11, weight="bold", color=color, pad=2)
    ax.text2D(0.5, -0.02, sub, transform=ax.transAxes, ha="center", fontsize=8.5, color="#444")
    ax.set_zlim(-turns, turns)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_zlabel("generative axis\n(time / growth)", fontsize=8)
    ax.set_zticks([-turns, 0, turns]); ax.set_zticklabels(["−", "0", "+"], fontsize=8)
    ax.view_init(elev=18, azim=-60)
    ax.grid(False)

fig.suptitle("Figure 4.  The spiral — the loop that grows.  Winding = phase (the polarity); the vertical axis is the\n"
             "generative aspect of X; the PITCH is the free variable, set by attention — climb, flat, or descend.",
             fontsize=10.5, y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("ouroboros-fig-spiral-2026-06-18.png", dpi=140)
print("saved ouroboros-fig-spiral-2026-06-18.png")
