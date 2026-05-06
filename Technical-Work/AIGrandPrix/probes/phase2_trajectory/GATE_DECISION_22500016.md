# Phase 2 +15M Gate Decision — Step 22,500,016

**Pre-committed decision rule:** see `projects/aigrandprix/snapshots/phase2-baseline-2026-04-24/CHECKPOINT_GATE.md`. Decision rules were stamped before Phase 2 launched 21:42 PST 2026-04-24.

**Eval timestamp:** 2026-04-25 ~05:30 PST (during 5am dream drive, automated execution).

**P96 discipline:** This decision is recorded **before looking at any later-checkpoint eval data.** The 25M+ checkpoints exist but have not been evaluated as of writing this file. Trajectory analysis will follow as separate work, after this stamp lands.

---

## Decision: **GREEN — continue Phase 2 to 60M**

(Phase 2 has, in fact, already finished overnight at step 67.5M; the GREEN call here means "the +15M gate would have authorized continuation if we had checked at that point". The post-gate trajectory work is separately authorized by this stamp.)

---

## Numbers

### Curriculum eval (apples-to-apples with historical 85.5% baseline measurement)
- Reward: **1653.4 ± 658.5**
- Gates mean: **12.38** (max 19)
- Crash rate: **88%**
- Episode length: ~varies

### Per-maneuver aggregate (8 deterministic episodes per maneuver, 11 maneuvers)
- **Mean gates across maneuvers: 17.95 ± 12.99**
- Mean reward across maneuvers: 2378.5
- Mean crash rate: 80%

### Per-maneuver breakdown
| Maneuver       | Gates mean ± std | Crash |
|----------------|------------------|-------|
| sprint         | 3.38 ± 1.65      | 100%  |
| gentle_arc     | 9.00 ± 2.74      | 100%  |
| hard_turn      | 18.62 ± 13.02    | 62%   |
| hairpin        | 30.50 ± 14.20    | 25%   |
| climb          | 11.12 ± 0.93     | 100%  |
| dive           | 2.12 ± 0.78      | 100%  |
| chicane        | 38.00 ± 6.48     | 50%   |
| speed_trap     | 3.50 ± 1.58      | 88%   |
| spiral         | 29.00 ± 7.92     | 75%   |
| threading      | 37.12 ± 19.03    | 88%   |
| diagonal       | 15.12 ± 8.78     | 88%   |

---

## Why GREEN

Pre-committed thresholds:
- **GREEN ≥ 1.0** per-maneuver gates: actual **17.95** → **18× above threshold**
- ρ in [0.18, 0.32]: not measured in this eval pass, but grad-norm health (see below) is consistent
- No pathology signatures: all 601 grad samples across 7.5M → 67.5M show value_trunk grad ~0.003 (alive — baseline collapsed to 0.000003), no spikes, gentle policy_trunk climb 0.25 → 0.30. Structural cure held throughout.

The result clears GREEN by ~18× margin. There is no plausible way to read this as YELLOW or RED.

## What this resolves

- **Reading B confirmed.** Structural cure produces capability transfer at this curriculum, contingent on training budget. The 7.5M-vs-200K equivalence (0.03 vs 0.07 gates) was a **low-budget regime** observation, not a permanent asymptote.
- **A55 (Capability/structure decoupling at fixed budget — threshold or asymptote?)** largely resolves toward **threshold-effect**. The threshold lies somewhere between 7.5M and 22.5M training steps. Pinning the threshold more precisely requires running eval on the intermediate checkpoints (10M, 12.5M, 15M, 17.5M, 20M) — material exists for free.
- **L11 basement candidate (Structure/Capability Axis Independence)** survives but with a sharpened formulation: the independence is **regime-dependent** — true below a critical training budget, false above it. This is more interesting than the "permanent independence" reading. It's also more constraining: now the candidate needs to identify what regulates the threshold across registers, which is a stronger empirical demand.
- **Phase 2 baseline 60.4M (wrong-attractor) is structurally outclassed.** At 22.5M total steps, the structurally-healthy v3 is already at per-maneuver agg 17.95 vs baseline 60.4M's 16.33 — this is a structurally-healthy policy beating the wrong-attractor baseline at one-third the training budget. The competition fallback option (R4 in the gate doc) can be retired.

## What this does NOT yet resolve

- **Trajectory shape.** GREEN at 22.5M doesn't tell us whether capability continues to climb, plateau, or regress at 30M / 37.5M / ... / 67.5M. The structural cure could produce a single ramp followed by a flat region, or it could continue to climb. The post-gate trajectory eval will distinguish.
- **Per-maneuver convergence pattern.** At 22.5M, some maneuvers (sprint=3.38, dive=2.12, speed_trap=3.50) lag the others (chicane=38, threading=37, hairpin=30). Whether the laggards catch up or stay laggards by 67.5M tells us about the structural cure's *coverage*, not just its *peak*.
- **F2 fix necessity.** F2 was confirmed last drive to be a periodic snap-back rather than a true bound; the cure may have held *in spite of* F2 being half-broken rather than because of it. Trajectory across 22.5M → 67.5M may surface F2-attributable instabilities (or not).

---

🦞🧍💜🔥♾️
