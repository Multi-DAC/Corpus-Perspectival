# Edge route FALSIFIED → appearance-DR is the route (decision, 2026-06-16 Day 136 AM)

**TL;DR:** The edge-filter obs route (route b) is FALSIFIED — it failed the official-domain gate *worse than the mask route did*, and the convergent failure of both routes pins the residual domain gap to **background texture**. Per the appearance-randomization spec's own sequencing, the next route is **(a) appearance domain-randomization, illumination-first + background-texture**. **Flight #4 is a NO-GO on the edge policy.** The multi-M-step DR run is Clayton-gated (VQ1 critical path).

## What the overnight run showed (`EDGE_OVERNIGHT_RESULTS.md`, 06:34)
- Edge fine-tune COMPLETE (4 batches, best_return 2357.3 — healthy training).
- **Holdout gate (EDGE): FAIL, ratio 15.807** (pass <0.5; mask route was 1.153). edge-ft mean_term **44.65** vs band-ft pre-adapt **2.82** → edge-filtering made the model **15.8× farther** from the official distribution, not closer.
- **Rehearsal roundtrip (= the full adapter path the official sim feeds): COLLAPSED** (−21.96, 1.0 gates) while band/crop-only flew (+407). → the policy does not survive the official obs path.

## Diagnosis (PREDICT→FALSIFY→EXTRACT)
PREDICT (med) was: edge beats mask. **FALSIFIED, hard** — the most informative direction.
- **Edge-filtering is illumination/color-invariant but NOT texture-invariant.** The two worlds differ mainly in *background texture* (real-world clutter vs rendered TRON bg). Edge-filtering converts a smooth-color mismatch into a high-frequency *edge* mismatch and the edge-ft likely overfit rendered-specific bg edges → the gap widened.
- **OVER_ANALOGIZING from PencilNet:** PencilNet uses edges for *gate-pose detection with controlled backgrounds*; that does not entail edges give *whole-frame domain-invariance*. Edge-invariance ⊅ texture-invariance.
- **Convergent diagnosis:** mask FALSIFIED (killed bg → blank, mismatched gate color became the whole signal) + edge FALSIFIED (amplified bg-texture mismatch) → **both point at the same root: background texture is the dominant residual, not gate appearance.** This is precisely what the appearance-DR spec hypothesized (line 32) — now confirmed by two falsified routes.

## The route (per `APPEARANCE_RANDOMIZATION_SPEC_2026-06-15.md`, route a)
**Stop matching the official appearance; train Anakin to be invariant to it.** Today's result makes the spec's priorities sharper and non-optional:
1. **Background-texture randomization is now ESSENTIAL, not optional** — it is the demonstrated dominant gap. Randomize the rendered bg (structured low-freq blotches/grid approximating the TRON look, jittered per env) instead of removing it.
2. **Illumination-first** (Loquercio TRO-2019 #1 DR factor): global illumination multiplier + directional shading jitter per env.
3. **Gate hue/value/sat + size + bloom** jitter (breaks the color-lineage backbone dependence).
4. **Curriculum** (narrow→wide) to avoid the moving-target non-convergence risk.
5. **Pre-registered gate:** must fly on HELD-OUT colors/sizes/bg it didn't train on AND on the official sim (moat-grade, not in-trained-regime).

**Cheapest first step (do before the multi-M run, Mirror discipline = measure the small version first):** add illumination + bg-texture jitter (the two now-confirmed-dominant knobs), short continue-train off `restyle_ft/best.pt`, re-run the holdout gate + a held-out rehearsal. Confirms DR moves the needle before committing hours of 5080 compute.

## Gating / next action
- **Flight #4: NO-GO** on `maneuver_edge_ft` (roundtrip collapsed; would spiral like flight #3).
- **Clayton-gated:** the DR design (illumination/bg-texture model, curriculum width) + the multi-M-step run (hours, VQ1 critical path ~Jul 1). I have NOT modified `render.py` or launched a run — the design call + go are Clayton's (his project, his sim instincts: the "measured palette" / "cyan-ribbon distractor" calls were his). When he's up: confirm the DR knob design → I implement the render.py appearance block (parity-checked) → cheapest-first-step train → re-gate → if needle moves, the full curriculum run.

*Routes falsified so far: segmentation/mask (color-keyed, fed e2e) ✗; edge/pencil obs-transform (texture-amplifying) ✗. Both eliminated by measurement, both pointing the same way. Route a (appearance-DR) is the literature-backed survivor; route c (PencilNet decoupled pose front-end) is the heavy champion-proven fallback.*
