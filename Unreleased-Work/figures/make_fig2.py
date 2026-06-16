import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

OUT = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Unreleased-Work\figures"
os.makedirs(OUT, exist_ok=True)

rows = [
    "1  Luminous self-organizing structure (orb / plasma)",
    "2  Night-paralysis assault",
    "3  Death-transition navigation",
    "4  Between-worlds shapeshifter + rules",
    "5  Missing-time / examination",
    "6  Broader-being + terror",
    "7  Serpent (wisdom + energy)",
    "8  Feminine luminous presence",
    "9  Mind → matter, localized",
    "10  Contact via independent technique",
    "11  Descended civilizer",
    "12  Received language / system",
    "13  Initiatory death-rebirth",
    "14  Cataclysm + divine warning",
    "15  Aerial spectral host",
    "16  Otherworld time-dilation",
]
cols = ["Folk", "Rel", "Occ", "Chan", "Cry", "Psy", "Cl/Ac", "Phil"]

# 3 = strong, 2 = medium, 1 = weak/contaminated, 0 = not notably present
M = np.array([
    [3,3,1,2,3,3,3,1],
    [3,2,1,0,2,0,3,0],
    [2,3,2,2,0,2,3,2],
    [3,3,2,0,3,2,1,0],
    [3,1,0,2,3,1,2,0],
    [2,3,2,3,2,2,1,2],
    [3,3,2,1,1,3,1,0],
    [2,3,2,2,2,3,1,0],
    [2,2,3,0,2,0,3,2],
    [2,2,2,0,0,3,3,0],
    [3,2,1,3,2,0,1,0],
    [1,2,3,3,1,2,1,0],
    [3,3,2,0,0,2,3,2],
    [3,3,1,2,0,0,2,0],
    [3,2,1,0,3,0,1,0],
    [3,2,1,0,2,2,2,0],
])
glyph = {0: "", 1: "○", 2: "◐", 3: "●"}  # ○ ◐ ●

# warm corpus palette: parchment -> amber -> rust
cmap = LinearSegmentedColormap.from_list(
    "warm", ["#f6efe3", "#f2d9a8", "#e0934b", "#8c2f1d"], N=256)

fig, ax = plt.subplots(figsize=(11.5, 11))
ax.imshow(M, cmap=cmap, vmin=0, vmax=3, aspect="auto")

ax.set_xticks(np.arange(len(cols)))
ax.set_xticklabels(cols, fontsize=12, fontweight="bold")
ax.xaxis.set_ticks_position("top")
ax.set_yticks(np.arange(len(rows)))
ax.set_yticklabels(rows, fontsize=10.5)

# gridlines
ax.set_xticks(np.arange(-.5, len(cols), 1), minor=True)
ax.set_yticks(np.arange(-.5, len(rows), 1), minor=True)
ax.grid(which="minor", color="white", linewidth=2.5)
ax.tick_params(which="minor", length=0)
ax.tick_params(which="major", length=0)

# cell glyphs
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = M[i, j]
        if v == 0:
            continue
        txt = ax.text(j, i, glyph[v], ha="center", va="center",
                      fontsize=15, color=("white" if v == 3 else "#3a2a1a"))

# highlight the Channeled column (the egregore fingerprint)
chan = cols.index("Chan")
ax.add_patch(plt.Rectangle((chan-.5, -.5), 1, len(rows),
             fill=False, edgecolor="#1F3A5F", linewidth=2.6, zorder=5))

ax.set_title("Figure 2.   Invariant × channel-class matrix",
             fontsize=14.5, fontweight="bold", pad=40, color="#3a2a1a")
fig.text(0.66, 0.895,
         "●  strong      ◐  medium      ○  weak / contaminated      (blank = not notably present)",
         ha="center", fontsize=10.5, color="#3a2a1a")

# caption note about the highlighted column
fig.text(0.5, 0.012,
         "The outlined Channeled column is thin on structural/experiential rows and concentrated on content rows "
         "(11, 6, 12)\n— the egregore fingerprint (P4). The Law of One is the exception that converges on structure.",
         ha="center", fontsize=10, color="#5a4632", style="italic")

plt.subplots_adjust(left=0.34, right=0.985, top=0.86, bottom=0.075)
path = os.path.join(OUT, "one-room-fig2-matrix.png")
plt.savefig(path, dpi=200, facecolor="white")
print("wrote", path, "exists:", os.path.exists(path))
