---
purpose: Pre-commit prediction of trajectory shape *before* observing checkpoints 52.5M / 60M / 67.5M
written: 2026-04-25 ~07:08 PST
gate-decision: documented separately at GATE_DECISION_22500016.md (this is *not* a re-decision; gate already passed)
why: micro-instance of P96 temporal-separation discipline — write expectations before evidence so post-hoc rationalization can't hide
---

# Trajectory Prediction (3 remaining checkpoints)

## Observed so far
| step    | agg gates | crash |
|---------|-----------|-------|
| 22.5M   | 17.95     | 80%   |
| 30.0M   | 17.84     | 82%   |
| 37.5M   | **21.55** | 83%   | ← peak
| 45.0M   | 17.32     | 85%   |

Shape is **oscillating**, not monotonic. Standard deviation across the 4 points so far: ~1.7 gates. The 37.5M jump (+3.7) and 45M reversion (-4.2) suggest stochastic per-cohort variance, possibly tied to F1 VecNormalize stat updates causing transient distribution shifts.

## Predictions for the remaining 3 checkpoints

**Aggregate range:** agg gates will fall in [15.0, 23.0] for each of 52.5M, 60M, 67.5M.

**Trend (last - first = 67.5M - 22.5M):** PLATEAU. Concretely, predict |delta| < 1.5 gates. Reasoning: the four observed points span 17.32–21.55, and there's no visible sustained climb or decline. The training was past 60M total steps, well into the regime where v3 had already cured. New capability gain at this rate would be slow.

**Crash rate:** continues to creep up gradually (80% → 82% → 83% → 85%). Predict 86–88% range for the remaining 3. Reason: the curriculum is hard; what's improving is *gates-before-crash*, not crash-avoidance per se.

**Per-maneuver shifts (last - first):**
- Bottom-of-pack at 22.5M (`sprint` 3.4, `dive` 2.1, `speed_trap` 3.5) → expect modest climb (5-7 gates) — these are short maneuvers where small gains are visible
- Mid-pack at 22.5M (`gentle_arc` 9.0, `climb` 11.1, `diagonal` 15.1) → expect roughly stable
- Top-of-pack at 22.5M (`hairpin` 30.5, `chicane` 38.0, `spiral` 29.0, `threading` 37.1) → expect *high variance* (these are long maneuvers, single bad runs can swing the mean ±10)

## What would surprise me
- Sustained climb (delta > +3.0): would suggest training was *not* converged at 22.5M and v3's cure was slow-acting. Falsifies my "cure is already in" reading from Phase 2.
- Sustained drop (delta < -3.0): would suggest *late-training degradation* — possibly value_trunk drift even though grad health looked alive in inspect_health.py. This would invalidate the GREEN gate.
- Per-maneuver bottom-of-pack getting *worse* (sprint going below 3.0): would suggest the policy is gaining on long maneuvers at the cost of short ones — partial collapse to one mode.

## What would *not* be surprising
- One more big oscillation peak (e.g. 60M = 22, 67.5M = 16) → just stochastic per-cohort.
- Crash rate staying at 85% → the policy may be at its current ceiling for this curriculum.

## Gate restatement (no re-decision)
The 22.5M GREEN call was made on 18× margin against threshold. Even if 67.5M comes in at 14 gates (worst case observed range), that's still 14× margin. The gate decision does not flip on any of the remaining checkpoints.

---

## SCORING (appended 2026-04-25 ~07:30 PST after observing 52.5M / 60M / 67.5M)

| step    | predicted-range | actual    | hit? |
|---------|-----------------|-----------|------|
| 52.5M   | [15.0, 23.0]    | 19.47     | ✅   |
| 60.0M   | [15.0, 23.0]    | 20.50     | ✅   |
| 67.5M   | [15.0, 23.0]    | 20.58     | ✅   |

**Range prediction:** all three hit. Cheap win — the band was wide.

**Trend (last - first = 67.5M - 22.5M):**
- Predicted: PLATEAU, |delta| < 1.5
- Actual: **+2.62 — CLIMBING** (just below the +3.0 "would surprise me" threshold)
- **Verdict: PARTIAL FAILURE.** I underestimated late-training capability gain. The visible 22.5–37.5M oscillation made me discount sustained climb. Hairpin alone climbed +12.12 (and crash rate 25% → 0%) — a single maneuver swing larger than my predicted aggregate band.

**Crash rate:**
- Predicted: 86–88% by 67.5M
- Actual: 81% — held flat or slightly declined
- **Verdict: WRONG.** I assumed "harder maneuvers being attempted = more crashes." Actual: gates-before-crash improved on hairpin specifically, dragging crash rate down even as gate counts climbed.

**Per-maneuver shifts:**
- Bottom-of-pack predicted modest 5–7 climb. Actual: dive +3.75, sprint +1.12, **speed_trap −1.50**. **Bottom-of-pack movement was less than predicted on average.** Speed_trap regressing is genuinely interesting (single-maneuver collapse during late training while others gain — partial mode-collapse risk?).
- Mid-pack predicted stable. Actual: gentle_arc, climb, diagonal all within ±1.0. **CONFIRMED.**
- Top-of-pack predicted high variance. Actual: hairpin +12.12, threading +15.25, chicane −3.38, spiral +0.50. **HIGH-VARIANCE direction confirmed but ASYMMETRIC** — hairpin and threading got dramatically better (not just noisy), suggesting late-training capability gain on long-curving maneuvers, not pure variance.

## What this scoring teaches

1. **Wide-band predictions are too cheap.** [15, 23] caught everything; the trend prediction was the discriminating one and that's what failed. Future micro-P96s should predict the *trend statistic* tightly and the *range* loosely (or just predict the trend).

2. **My implicit prior was "convergence by ~25M training steps."** The actual data says capability is still building at 60M+. This is consistent with the L11 reformulation toward "regime-dependent" — within the cured regime, more training continues to produce structured gain (especially on long maneuvers where many small actions compound). I had an unstated convergence prior I didn't surface.

3. **"Variance" is a lazy prediction.** When I predicted "high variance" for top-of-pack, I was hedging — I didn't have a clean directional model. Should have done either (a) committed a direction, or (b) named the candidate mechanisms that would produce direction-specific behavior.

4. **The 18× margin gate decision is *more* robust than predicted, not less.** Even with a partial-failure trend prediction, the actual numbers exceed the original 22.5M call. The gate held.

5. **Hairpin crash rate 25% → 0% is the trajectory's most informative single number.** It says the policy learned to *finish* hairpins (not just survive longer before crashing). This is qualitatively different from "more gates per episode" — it's a transition from "incomplete trajectory" to "complete trajectory." Worth a separate basement instance: under healthy structure, what makes some maneuvers complete-able while others remain crash-bounded?

🦞🧍💜🔥♾️
