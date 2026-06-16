# Appearance-Randomization Route — design spec (Day 135, 2026-06-15)

**Status:** READY-TO-IMPLEMENT design, pending (a) flight #3 outcome and (b) Clayton's go. Successor to
the FALSIFIED mask/segmentation route (`SEG_ROUTE_DECISION_2026-06-14.md`). Pre-drafted as anticipatory
pre-work — answer ready before the question.

> **★ UPDATE 2026-06-16 (Day 136) — NOW THE ACTIVE ROUTE.** The edge-filter route (b) was FALSIFIED
> overnight (holdout gate 15.8, *worse* than mask's 1.15; roundtrip rehearsal collapsed). Edge-filtering
> amplified the background-texture mismatch instead of removing it → **bg-texture is confirmed as the
> dominant domain gap**, exactly as this spec hypothesized (line 32). So appearance-DR (route a) is the
> surviving route, and its two now-non-optional knobs are **background-texture randomization** and
> **illumination** (route order's (a) reached). Flight #4 = NO-GO on edge-ft. See
> `EDGE_FALSIFIED_DECISION_2026-06-16.md`. Pending Clayton's DR-design call + go on the multi-M run.

## Why (the case is now strong, from Day-135 diagnostics)
- **Mask route FALSIFIED** (gate mean-term ratio 1.153) — masking small official gates → near-blank obs.
- **Color-lineage backbone problem (measured):** the 10M-step scale-run backbone + band-ft trained on
  the OLD gate color (gray/blue-white, 0% orange-red); orange-red entered only in the SHORT restyle/mask
  fine-tunes. So the deep "gate" representation is keyed to an appearance the official sim doesn't use,
  with a thin patch on top. Chasing the *exact* official appearance is fragile because the backbone is
  the wrong shape for it.
- **The harvest is a biased instrument** (human pilot flew around/above gates, not through — official
  frames are off-line/tiny-gate). We cannot build a reliable exact-match reference from it.
- **Therefore: don't match the official appearance — be INVARIANT to appearance.** Standard sim-to-real
  domain randomization: train across a wide distribution of gate colors/sizes/bloom + backgrounds so the
  official sim is just one more sample inside the trained manifold. Removes the dependence on (a) a
  correct backbone color and (b) a good harvest, in one move.

## What to randomize (grounded in `sim/render.py` constants, lines 44-64)
The per-env randomization PATTERN already exists (`BG_JITTER`, `BG_NOISE`, `RIBBON_*` are sampled per
env) — extend the SAME mechanism to the gate. Sample once per env (per episode), not per frame.

| Knob | Current (fixed) | Randomize to | Rationale |
|------|-----------------|--------------|-----------|
| **Gate hue** | orange-red core (0.90,0.36,0.31) | hue ∈ [official −Δ … +Δ], Δ≈30–40° around red-orange, **plus** occasional far-off hues | THE key one — breaks the color-lineage dependence; forces gate detection on GEOMETRY not color |
| **Gate value/sat** | fixed | brightness ×[0.6,1.3], saturation ×[0.6,1.2] | lighting/exposure robustness |
| `GATE_DIM` | (0.45,0.18,0.15) | track the bright-gate jitter (same hue offset, dimmer) | consistency |
| `GATE_GLOW_A` | 0.35 | ∈ [0.15, 0.55] per env | bloom varies in the official feed |
| **Gate size** | `GATE_OUTER=2.7 / INNER=1.5` | ×[0.9, 1.15] per env | apparent-size robustness (mild; size is mostly distance-driven) |
| `BG_GRAY` / `BG_JITTER` | 27/255 ± 10/255 | widen to ±15/255; **add structured bg texture** (low-freq blotches / grid) approximating the official TRON background, jittered | the official bg is textured, not flat gray — the mask route's whole premise was that bg is the gap; randomize it instead of removing it |
| Ribbon | already randomized (P=0.5, W, A, JIT) | keep as-is (good) | distractor, already de-crutched |

## Train approach
- **Continue-train off `restyle_ft/best.pt`** with DR ON. ⚠ Likely needs MORE than a thin fine-tune —
  the backbone must un-learn color-specificity, so budget a substantial run (candidate: 3–5M steps,
  not 0.5M). Watch the encoder/world-model loss re-climb then settle as it generalizes.
- **DON'T mask.** Keep full RGB; let the policy learn appearance-invariance the honest way.
- **Pre-registered gate (the robustness test):** the DR policy must fly on HELD-OUT gate
  colors/sizes/bg it did NOT train on (split the randomization range; eval on the held-out slice) AND
  on the official sim. If it flies held-out → it's genuinely invariant, not memorizing a new palette.
  This is the moat-grade version of the in-domain eval (don't repeat the restyle mistake of testing
  in the trained regime only).

## Dependencies / risks / sequencing
- **Compute:** a multi-M-step DR continue-train on the 5080. Hours, not minutes. **This is the VQ1
  (~Jul 1) critical-path item if flight #3 DQs** — flag the time cost to Clayton early.
- **Flight #3 dependency:** if flight #3 FLIES → DR drops to "robustness margin," lower urgency (still
  worth a moderate run for the official's exact look). If flight #3 DQs → DR is THE route, start the
  render.py jitter + continue-train promptly.
- **Risk:** too-wide randomization can prevent convergence (policy can't learn a moving target). Mitigate
  with a curriculum (start narrow around orange-red, widen over training) — the proven pattern from the
  maneuver curriculum.
- **Cheapest first step (do before the big run):** add the gate-hue jitter only (one knob), short
  continue-train, re-run the holdout gate AND a held-out-color rehearsal — confirms DR moves the needle
  before committing the multi-M-step run. (Mirror discipline: measure the small version first.)

## One-line summary
Stop matching the official gate; train Anakin to not care what the gate looks like. The backbone is the
wrong color and the harvest is a biased ruler — invariance routes around both.

---
## Literature update (Day 135 PM exploration — sources: Loquercio/Kaufmann TRO-2019 "Deep Drone Racing: Sim-to-Real w/ Domain Randomization"; PencilNet arXiv 2207.14131; MonoRace 2026). From abstracts — verify on full-paper read before committing compute.
1. **ILLUMINATION is the #1 DR factor** (Loquercio), which this spec underweighted. Promote it above gate
   hue: per-env lighting/brightness/shadow/contrast randomization is the TOP knob. Add a global
   illumination multiplier + directional shading jitter to the render appearance block.
2. **A THIRD route — the "right" version of the FALSIFIED mask route: edge/abstraction-filter decoupling.**
   PencilNet gets ZERO-SHOT sim-to-real gate perception via a **pencil (edge) filter** — appearance- AND
   illumination-invariant because EDGES survive color/lighting — feeding a small CNN that outputs **gate
   POSE** (decoupled perception→pose→control). My mask route failed for two fixable reasons: it keyed
   invariance on COLOR (RGB threshold — the most brittle axis), and it fed masked pixels to the END-TO-END
   world model instead of decoupling. **Cheap test that resurrects it correctly:** replace `gate_mask.py`'s
   color-threshold with an EDGE/pencil obs-transform (Sobel/Canny-ish, kept in encoder RGB shape), fine-tune
   off restyle_ft, re-gate. Edges are the invariance axis the official↔backbone color-lineage gap demands.
3. **Route order for the DQ branch:** (b) edge-filter obs transform FIRST — cheapest, literature-backed,
   fixes the mask route's two errors; (a) appearance-DR (this spec, now illumination-first) if (b) insufficient;
   (c) full PencilNet-style decoupled pose front-end as the heavy, champion-level-proven fallback. All three
   are DCL-compatible (monocular FPV, no position telemetry).
