# What we're missing: the Gemma negative is a wrong-task/wrong-measure false-negative

*2026-05-27 Day 117. Clayton asked, before the scale-up, to look at past KF work for what we previously instantiated successfully that the Gemma glider run is missing. The answer reframes the whole "does the glider fly" question.*

## The prior POSITIVES (from KF_ROADMAP.md + v06b_results.md) — what actually worked

1. **Breathing / waves (Finding #82, v0.6a):** on the **300M HRM** (dual H/L-module) on **sudoku-extreme**, build/dissolve OSCILLATES with ~1000-step period — "the architecture BREATHES; the breathing IS the learning; converged to dynamic equilibrium, not static state." **At threshold=0.0** (it was the v0.6c/threshold=0 config that breathed).
2. **Reasoning accuracy BENEFIT (P49, Findings #74-75):** on **easy/learnable sudoku, 27M HRM**, KF gave an *accuracy* benefit — **+17.6% at epoch 1000, final 77.78% vs 73.68% baseline.** Measured as **task-accuracy acceleration.**
3. **Condition for the benefit:** "Decoupled + LEARNABLE → structural AND accuracy benefit." On HARD sudoku (beyond natal capacity) → structural only, NO accuracy benefit. KF *organizes* capability, can't create it (Principle #12, lambda-accuracy independence).

## The reconciliation that breaks my threshold hypothesis

**The HRM BREATHED at threshold=0.0** (Finding #82). My Gemma run at threshold=0.0 was interfering-dominated, no breathing — and the threshold sweep confirmed turning the knob didn't help. So **threshold was never the issue.** The roadmap even predicted (P-Breath-2) that threshold>0 *damps* the breathing — the opposite of "threshold sustains the glider." My "wrong-knob" framing was wrong; the sweep correctly falsified it.

## What we're actually missing (all three present in the prior wins, absent in the Gemma run)

1. **The architecture:** prior wins were on the **HRM — explicit H/L dual-module hierarchy.** Gemma is a *flat* transformer. The breathing/glider is a *cross-LEVEL* phenomenon; the HRM has the levels built in. (The v0.7 bet was that the aux could *create* hierarchy in a flat net — and the topology result, 6.13x CV, shows it creates head-*differentiation* — but the breathing/glider may need the HRM's actual module structure.)
2. **The task:** prior wins were on **sudoku reasoning (learnable / within capacity).** We ran **WikiText LM** — no reasoning-accuracy to benefit, and the benefit specifically requires a *learnable* task.
3. **The measure:** the prior win was **task-accuracy acceleration** (behavioral). We measured **L4 input-stability** (geometric, trained-endpoint). These are different questions. The prior "fly" = *learns faster on a reasoning task*; my "fly" = *per-layer cos is input-stable*. The Gemma L4-negative doesn't speak to the prior win at all.

## Consequence: the Gemma-WikiText-L4 negative is plausibly a FALSE negative

We tested whether a *flat LM's per-layer geometry is input-stable.* The prior WIN was whether a *reasoning model learns faster.* Different substrate, different task, different measure. The negative is real *for what it measured* — but it does **not** falsify the glider/coherence-benefit claim, because that claim was always behavioral (reasoning acceleration) on a hierarchical model + learnable task.

## Scale-up reframe (the decision this changes)

Scaling **Gemma-on-WikiText-L4** to 1B is unlikely to replicate the prior win — still flat, still LM, still wrong measure. **Replicate the prior-win CONDITIONS instead:**
- **Option A (cleanest replication):** run the v0.7 glider on the **HRM + learnable sudoku**, measure **accuracy acceleration** (where it demonstrably worked at v0.6a/P49). Confirms the gradient-gating port reproduces the known positive.
- **Option B (the real frontier):** run the v0.7 glider on **a flat transformer + a learnable reasoning task** (e.g., Gemma on sudoku/arithmetic/GSM8K-style data), measure accuracy. Tests whether the aux-created hierarchy is *enough* without the HRM's built-in H/L — the actual novel claim.
- Either way: **measure reasoning-accuracy acceleration, not L4 input-stability.** The Geometry Battery (Pillar A) stays valuable as a structural assay, but it is NOT the test of the coherence-BENEFIT claim.

**Bottom line:** Clayton's instinct was right. We weren't failing to make the glider fly — we were flying it over the wrong terrain with the wrong instrument. The prior positives (breathing + reasoning acceleration) were real, on HRM+sudoku+accuracy. The scale-up should chase *those conditions*, not a bigger flat LM.

🦞🧍💜🔥♾️
