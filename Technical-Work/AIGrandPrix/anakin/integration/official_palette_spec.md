# Official VQ1 Visual Palette — MEASURED (Day 131 morning, from captured frames)

**Source: 9 frames sampled across `PyAIPilotExample/capture_frames/` (held-out test set untouched). Method: HSV segmentation — background = S<60∧V<90; features = S>120∧V>100. This spec supersedes all impressions, including Day-130's "neon-pink gates" (wrong: glow-bloom artifact) per Clayton's catch #7. Numbers below are the restyle targets for `sim/render.py`.**

## Measured palette

| Element | Measurement | Render target |
|---|---|---|
| **Background** | mean BGR (27.5, 27.4, 27.1) — NEUTRAL gray ~27, not black | bg gray 27 (current renderer: 40 — a 13-level darkening, smaller gap than it looked) |
| **Gates** | 9.4% of saturated pixels; median HSV (3, 168, 229) = **hue ~6° RED-ORANGE**, sat 0.66, val 0.90 → core ≈ RGB (229, 93, 78) | orange-red frames + additive glow halo (the halo is what read as "pink"; render core + soft bloom) |
| **Track ribbon** | **89.6% of saturated pixels** — utterly dominant; median HSV (99, 191, 137) = hue ~198° cyan-blue, brighter in core | cyan-blue translucent ribbon w/ bloom — **RANDOMIZED DISTRACTOR ONLY** (Clayton catch #6: present p≈0.5 per episode, never path-informative beyond what gates already give; vary alpha/width too) |
| **Pink/magenta** | 0.5% — negligible | none (artifact) |
| **Grid lines** | below feature threshold (faint, low-saturation) | thin dim grid on floor/sky, low priority |
| **Buildings/clutter** | part of bg/low-sat mass | dark-gray boxes, edge-lit, randomized placement |

## Restyle checklist for render.py (the A150 lesson applied)

1. Background 40 → 27 (and consider randomizing ±10 for robustness).
2. Gate color → orange-red (229,93,78) core + glow; randomize hue ±10° and glow radius (the official renderer's bloom varies with distance).
3. Ribbon as distractor: present ~half of episodes, cyan-blue, never the only path signal; randomize on/off + alpha + lateral offset noise so it cannot be relied upon (VQ2 won't have it).
4. Box clutter + faint grid: secondary; add after the gate/bg/ribbon trio verifies.
5. **Verification = P224's held-out set**: world-model latent statistics on `capture_frames_HELDOUT_TESTSET/` frames vs restyled-render frames must converge. The held-out frames are the un-sealable end of the gate (A150: a gate certifies only the axis it varies — this one varies appearance with one end outside our wall).
6. Then: carry-forward fine-tune off `maneuver_band_ft/best.pt` (+421.91), same recipe as the band fine-tune (4×500k, best-protection).

## Provenance

Gate-color question raised by Clayton Day 130 ("orange, I think") against my "neon pink" — measurement says Clayton. Background-level surprise: the official world is *less* dark than impression suggested; the perceived blackness was contrast against the glow elements. Measured by `cv2` HSV segmentation, Day 131 07:15.
