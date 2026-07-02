# First-principles pass + targeted research sweep (Day 136, 2026-06-16 AM)

**Trigger:** both appearance-transfer routes (mask, edge) FALSIFIED → before spending multi-M GPU
on appearance-DR, Clayton asked the right question: *is the generalist-on-infinite-gate-curriculum
approach possible/sound, and what are we missing?* This note = the first-principles reasoning + a
targeted sweep aimed at the specific forks (NOT generic DR — we already have that lit).

## Verdict: the approach is POSSIBLE and SOUND. Ours is the *easy* version of a solved problem.
- We are sim-to-**sim**, not sim-to-real: no physics gap, no sensor noise, no real camera. **The
  entire domain gap is cosmetic** (color/texture/lighting/bloom) — the slice DR is most reliably good at.
- **Existence proof, almost exactly our setup:** **SkyDreamer** (arXiv 2510.14783, 2025) —
  "Interpretable End-to-End Vision-Based Drone Racing with Model-Based RL." DreamerV3-class, vision,
  racing, end-to-end. ★ MUST-READ IN FULL before the architectural fork below.
- DreamerV3 + domain randomization is validated for the pixel modality specifically: "Dreaming of
  Many Worlds" (2403.10967) + "Dynamics-Aligned Latent Imagination" (2508.20294) — contextual world
  models + DR give "striking" zero-shot pixel-modality generalization for the Dreamer family.

## The core diagnosis (what we were both half-missing)
**We built a geometry-generalist on a visual-specialist backbone.** The infinite-gate curriculum
randomized the axis we chose (gate layout/maneuvers) and left untouched the axis we never varied
(appearance — one look, 10M steps). Appearance-DR is NOT a retreat from the generalist philosophy;
it is that philosophy applied consistently to the dimension we forgot. "DR = the infinite-gate
curriculum, but for pixels."

## Generalist vs specialist — Clayton's read is exactly right, and the lit confirms it
- "Single-track RL policies demonstrate the best performance because they overfit the specific track."
  → our "difficult start" is the KNOWN cost of refusing to memorize. Expected, not a bug.
- Generalist IS achievable at high success: one policy hit **97.4% on 1000 random tracks**.
- BUT "DR alone fails on complicated unseen tracks" + "directly training one track, testing others,
  is not successful" → DR is necessary-not-sufficient; curriculum quality matters (see #3 below).

## What to ADD — ordered cheapest → heaviest
1. **★ Observation augmentation (RAD / random-convolution / color-jitter) — CHEAPER than our planned
   render.py work, and possibly higher-leverage.** Key distinction from the sweep: DR "assumes control
   of data generation" (edit render.py); data augmentation is applied to the observation AFTER
   rendering — **no render.py change at all.** Random-convolution + color-jitter are *purpose-built to
   make a policy ignore style/appearance while preserving geometry* — literally our problem.
   Refs: RAD (2004.14990), DrQ (2004.13649), **Style-Agnostic RL (2208.14863)**, **Progressive Random
   Convolutions for Single Domain Generalization (2304.00424)**. → **NEW cheapest-first-step:** add
   random-conv + color-jitter to the obs pipeline, short continue-train off `restyle_ft/best.pt`,
   re-gate. Beats the render.py bg-texture edit on cost AND targets the exact axis.
2. **Renderer-DR (illumination-first + bg-texture)** — our planned route, validated. Illumination = #1
   factor reconfirmed by "Continual Learning for Robust Gate Detection under Dynamic Lighting"
   (2405.01054). Do this if (1) moves the needle but not enough.
3. **Adaptive curriculum ("Environment as Policy: Learning to Race in Unseen Tracks", 2410.22308).**
   Our infinite-gate curriculum is FIXED/random. The frontier generates the tracks/gates the policy is
   currently WORST at (curriculum-as-policy). Strict upgrade, fully aligned with the generalist goal —
   "DR alone fails on hard unseen tracks because it ignores the policy's continuous improvement."

## The one architectural fork to decide DELIBERATELY (not by default)
**End-to-end model-based (us / SkyDreamer) vs modular decoupled-pose (the champions).**
- Champion-level systems (Nature 2023 Kaufmann/Loquercio; "Mastering Diverse, Unknown, and Cluttered
  Tracks") "remain MODULAR pipelines — gate-corner detection + Perspective-n-Point state estimation."
  A pose-based controller is appearance-invariant *by construction* — the ultimate generalist (sees
  geometry, never pixels).
- BUT SkyDreamer is the 2025 existence proof that END-TO-END model-based can reach racing competence
  AND stay interpretable. If it holds up on a full read, it justifies NOT abandoning DreamerV3 for a
  classical modular pipeline. **Decision gated on reading SkyDreamer in full.**

## Our own blind spot the literature did NOT address (still real)
**The measuring stick is bent.** The holdout gate's target = the official harvest, which is a biased
instrument (human flew around/above gates, not through). We may be optimizing toward a mismeasured
target. Even a few properly-flown official frames would re-calibrate. Independent of all the above.

## Recommended sequence (Clayton-gated; no render.py touched, nothing launched)
1. Read **SkyDreamer (2510.14783)** in full → settle the end-to-end-vs-modular fork.
2. Cheapest test FIRST: **obs augmentation (random-conv + color-jitter)**, short continue-train,
   re-gate — before any render.py edit (Mirror discipline: smallest version first, and this one is
   even smaller than our plan).
3. If needed: renderer-DR (illumination + bg-texture), then adaptive curriculum.

---

# ★ SkyDreamer FULL READ (2510.14783) — the fork RESOLVES, + a third route, + mask-route vindicated

*Read during the 09:03 creative drive. PREDICT (med-high): "interpretable" = latent grounded in
physical/pose quantities → hybrid is our target. **CONFIRMED**, mechanism sharper than predicted.*

**SkyDreamer = "informed Dreamer."** The world model decodes, alongside the usual observation
reconstruction, to **privileged information available ONLY during training**: position, velocity,
attitude, camera extrinsics, dynamic parameters. Standard DreamerV3 decodes raw obs; informed Dreamer
ALSO decodes physical state → "the world model effectively functions as an implicit state and
parameter estimator." Interpretability is a side-effect of grounding the latent toward physical state.
The policy still maps latent→motor end-to-end; **the privileged info is NOT needed at deployment.**
(Authors: Verraest, Bahnam, Ferede, de Croon, De Wagter — MAVLab/TU Delft. 17M steps, ~50h A100,
3-phase curriculum: warm-up → batch-length↑ @8M → entropy↓ @13M. JAX sim.)

## EXTRACT 1 — the end-to-end-vs-modular fork is a FALSE DICHOTOMY; informed-Dreamer is the synthesis
Neither classical-modular (no PnP pose pipeline, no decoupled controller) nor pure-monolith DreamerV3
(latent is grounded). **Stay on DreamerV3; add privileged decode heads supervised toward physical
state during training.** This is the architectural target. The fork I flagged Clayton-gated → resolved
by reading: don't rebuild as a modular pipeline; *inform* the world model we already have.

## EXTRACT 2 — a THIRD appearance-invariance route, and it attacks our diagnosed ROOT directly
Our root diagnosis: *the latent is keyed to appearance because nothing ever forced it toward geometry.*
Privileged latent supervision is the **direct cure**: if the world model MUST decode gate-pose /
drone-state / camera-params from its latent, the latent is *pressured to represent geometry, not the
specific pixels* — appearance-dependence gets squeezed out by the supervisory signal, not washed out of
the input. **We have ground-truth state in our sim already** (gate positions, drone state = free
privileged labels — no labeling needed). So the three routes to appearance-invariance, by mechanism:
  (1) Renderer-DR — vary the pixels (our plan; edits render.py).
  (2) Obs augmentation (random-conv/color-jitter) — vary the pixels post-render (cheapest; no render.py).
  (3) **★ Privileged latent supervision (informed Dreamer)** — give the latent a GEOMETRY job so it
      stops representing appearance (root-directed; free labels from sim; training-time only).
Routes (2) and (3) compose and neither touches the renderer. (3) is the most aligned with our diagnosis.

## EXTRACT 3 — our MASK route was wrong in IMPLEMENTATION, not in PRINCIPLE
SkyDreamer's visual input is **NOT raw RGB — it's a binary segmentation mask** (64×64) from a learned
U-Net ("GateNet", trained on 200–700 labeled real images/gate-type), + StochGAN synthetic→real mask
translation + 1px mask-erosion aug + rolling-shutter sim. **The champion-level end-to-end system feeds
its policy segmentation masks.** Our mask route (FALSIFIED Day 134) used a COLOR-THRESHOLD (brittle);
the right version is a LEARNED segmenter. A mask is appearance-invariant by construction (gate-color /
bg-texture irrelevant). Re-opens the mask route correctly — cost = labeling official-sim gate masks
(we have the 199-pair harvest to label). Even on masks they still appearance-DR (GAN translation +
erosion), confirming invariance is layered, never free.

## Honest caveat (the one place we are MORE ambitious than SOTA)
SkyDreamer reports **NO held-out-track generalization** — "all tracks used for training were tested;
no separate evaluation on novel gate layouts." Their transfer win is sim-to-real on APPEARANCE
(rendered→real masks) on KNOWN layouts. Our infinite-gate curriculum aims at *layout*-generalization
too. So we are not behind the SOTA on ambition — we are ahead on the layout axis and behind on the
appearance axis. The appearance axis is the one to close (routes 1–3); the layout axis is our edge.

## Updated recommended sequence (Clayton-gated; nothing launched, render.py untouched)
1. **Privileged decode heads (route 3)** — highest root-leverage, free sim labels, training-time only.
   Candidate cheapest test: add a state-decode auxiliary loss (gate-relative-pose + drone-vel) to the
   world-model training off `restyle_ft/best.pt`, short continue-train, re-gate. Measure if grounding
   the latent moves the official-domain term.
2. **Obs augmentation (route 2)** — random-conv + color-jitter, no render.py, composes with (1).
3. **Renderer-DR (route 1)** — illumination + bg-texture, if (1)+(2) insufficient.
4. **Learned segmentation front-end (EXTRACT 3)** — if pixel-space routes stall; needs official-mask labels.
Adaptive curriculum ("Environment as Policy") remains the layout-axis upgrade, orthogonal to all four.

---

*Sources (sweep 2026-06-16): SkyDreamer 2510.14783 (full read) · Dreaming of Many Worlds 2403.10967 ·
Dynamics-Aligned Latent Imagination 2508.20294 · RAD 2004.14990 · DrQ 2004.13649 · Style-Agnostic RL
2208.14863 · Progressive Random Convolutions 2304.00424 · Continual Gate Detection/Lighting 2405.01054 ·
Environment as Policy 2410.22308 · Champion-level drone racing (Nature 2023). arXiv MCP SSL-broken this
session (separate process, no truststore); sweep via WebSearch. Verify on full-paper reads before compute.*
