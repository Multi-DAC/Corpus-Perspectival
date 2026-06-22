#!/usr/bin/env python
"""Pre-render the Bee Substack piece's TABLES as PNGs (P249).

Substack drops rendered tables + math on paste (only PNG figures transfer —
reference_substack_base64_figures). The piece "Does a Bee Live in Slow Motion?" has two
load-bearing tables that would silently vanish on publish. Render both as clean PNGs so the
publish is paste-ready the moment Clayton says go.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def render_table(rows, col_labels, title, outfile, col_widths=None, figsize=(7.2, 1.9), highlight_col=None):
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=col_labels, cellLoc="center", loc="center",
                   colWidths=col_widths)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)
    tbl.scale(1, 2.4)
    # style header
    for j in range(len(col_labels)):
        c = tbl[0, j]
        c.set_facecolor("#3b3b4f")
        c.set_text_props(color="white", fontweight="bold")
    # style body
    for i in range(1, len(rows) + 1):
        for j in range(len(col_labels)):
            c = tbl[i, j]
            c.set_facecolor("#f7f7fb" if i % 2 else "#ffffff")
            if highlight_col is not None and j == highlight_col:
                c.set_text_props(fontweight="bold", color="#1a1a2e")
            c.set_edgecolor("#d0d0dd")
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold", pad=10, color="#2a2a3a")
    plt.tight_layout()
    plt.savefig(outfile, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"wrote {outfile}")


# --- Table 1: rod<->cone occupancy (the within-eye "caught red-handed" check) ---
render_table(
    rows=[
        ["Rod (night)", "~15 Hz", "~100 ms", "~1.5"],
        ["Cone (day)", "~60 Hz", "~25 ms", "~1.5"],
    ],
    col_labels=["", "refresh  λ", "window  τ", "μ = λτ  (occupancy)"],
    title="One eye, two clocks: refresh swings 4×, the texture (μ) holds still",
    outfile="bee_table_rodcone.png",
    col_widths=[0.22, 0.20, 0.20, 0.30],
    figsize=(7.4, 1.7),
    highlight_col=3,
)

# --- Table 2: the three-tier compression (the spine) ---
render_table(
    rows=[
        ["within one eye\n(rod↔cone)", "refresh  4×", "occupancy  ~1×", "~4×"],
        ["within one human\n(across the senses)", "peripheral acuity  ~20×", "binding window  ~1.5×", "~13×"],
        ["across mammals\n(by brain size)", "brain volume  17,000×\nrefresh  ~75×", "cortical rhythm  ~3×", "~25×"],
    ],
    col_labels=["scale", "the substrate varies…", "…the binding clock barely moves", "compression"],
    title="The same shape at three scales — the deeper you go, the more the clock refuses to move",
    outfile="bee_table_threetier.png",
    col_widths=[0.21, 0.27, 0.34, 0.15],
    figsize=(9.8, 3.0),
    highlight_col=3,
)

print("done — 2 table PNGs ready for the Bee publish")
