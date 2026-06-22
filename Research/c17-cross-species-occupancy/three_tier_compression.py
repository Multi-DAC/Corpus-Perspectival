#!/usr/bin/env python
"""Three-tier meta-rate compression figure (Day 141).

The same shape at three scales: the BINDING / META quantity is far more invariant than the
SUBSTRATE / PERIPHERAL quantity it sits on top of. Sourced numbers:

TIER 1 — within-system (one human eye, rod<->cone) [our reciprocity work, Day 140]
  substrate: photoreceptor sampling rate lambda varies ~4x bright<->dim
  meta:      occupancy mu = lambda*tau pinned ~constant (tau compensates) -> spread ~1.1x

TIER 2 — within-human (cross-modal binding) [within_human_crossmodal.md, P246, srep17467 + gap-detection lit]
  substrate: peripheral temporal acuity ~20x (auditory ~3 ms <-> visual ~65 ms)
  meta:      cross-modal binding window ~1.5x (VT 279 ms <-> AV 418 ms)

TIER 3 — cross-species (mammals, brain rhythm) [Buzsaki, Logothetis & Singer, Neuron 2013, PMC4009705;
                                               CFFT span: Healy et al. 2013, PMC3791410]
  substrate: CFFT (visual sensor refresh) ~75x across vertebrates; brain VOLUME ~17,000x across mammals
  meta:      cortical oscillation frequency — conserved bands (alpha/gamma/ripple) ~1.6-3x;
             theta (most variable) ~ up to 10x; cross-brain conduction TIME held to "a few-fold"
             despite the 17,000x size (compensated by axon caliber).

Honest grade baked into the caption: a compressed BAND, not a single clock; tier-3 meta is the
NEURAL correlate (oscillation), mammal-centric — not the phenomenal 'now' nor insects/birds.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# (label, substrate_fold, meta_fold, substrate_name, meta_name)
tiers = [
    ("Within-system\n(one eye, rod↔cone)", 4.0, 1.1,
     "λ  photoreceptor rate", "μ=λτ  occupancy"),
    ("Within-human\n(cross-modal)", 20.0, 1.5,
     "peripheral acuity\n(aud ~3 ms ↔ vis ~65 ms)", "binding window\n(VT 279 ↔ AV 418 ms)"),
    ("Cross-species\n(mammals, brain rhythm)", 75.0, 3.0,
     "CFFT visual sensor (~75×)\n[brain volume ~17,000×]", "cortical oscillation\n(conserved bands)"),
]

fig, ax = plt.subplots(figsize=(10.5, 6.2))
ax.set_xscale("log")
y = np.arange(len(tiers))[::-1] * 1.0  # top = tier 1
barh = 0.30
sub_color, meta_color = "#c44e52", "#4c72b0"

for i, (label, sub, meta, sub_n, meta_n) in enumerate(tiers):
    yy = y[i]
    # substrate span (wide, light) and meta span (narrow, dark), both starting at 1x
    ax.barh(yy + 0.18, sub, left=1.0, height=barh, color=sub_color, alpha=0.85, zorder=3)
    ax.barh(yy - 0.18, meta, left=1.0, height=barh, color=meta_color, alpha=0.95, zorder=3)
    # span labels at the end of each bar
    ax.text(sub * 1.06, yy + 0.18, f"{sub:g}×  {sub_n}", va="center", ha="left", fontsize=8.5, color=sub_color)
    ax.text(meta * 1.10, yy - 0.18, f"{meta:g}×  {meta_n}", va="center", ha="left", fontsize=8.5, color=meta_color)
    # compression ratio
    comp = sub / meta
    ax.text(140, yy, f"→ {comp:.0f}×\ncompression", va="center", ha="left", fontsize=10,
            fontweight="bold", color="#333333")

ax.set_yticks(y)
ax.set_yticklabels([t[0] for t in tiers], fontsize=10)
ax.set_xlim(1, 700)
ax.set_xlabel("fold-variation across the tier  (log scale)  —  how much the quantity spans", fontsize=10)
ax.axvline(1, color="k", lw=0.8, alpha=0.5)
ax.set_title("The mind's clock is conserved where the substrate diverges — at three scales\n"
             "red = substrate/peripheral (free to vary)   •   blue = binding/meta rate (held nearly fixed)",
             fontsize=11.5)
# legend-ish caption
cap = ("Sources: tier 1 — occupancy reciprocity (this program, Day 140); tier 2 — srep17467 + gap-detection lit (P246); "
       "tier 3 — Buzsáki, Logothetis & Singer, Neuron 2013 (brain rhythms preserved across 17,000× brain volume) + "
       "Healy et al. 2013 (CFFT ~75×).\n"
       "Honest grade: a compressed BAND, not a single clock (theta still varies up to ~10×); tier-3 meta is the NEURAL "
       "correlate (oscillation), mammal-centric — not the phenomenal 'now', and insects/birds remain unbridged.")
fig.text(0.5, -0.02, cap, ha="center", va="top", fontsize=7.3, color="#555555", wrap=True)

ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
out = "three_tier_compression.png"
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"wrote {out}")
print("compression ratios:", [f"{s/m:.1f}x" for _, s, m, _, _ in tiers])
