# Far-start fine-tune — FALSIFIED (the real root cause is the obs representation)

**Date:** 2026-06-01 (Day 121, dream drive ~06:15 PST). Overnight `farstart_twr385` run
(resume from 80M, ground_start 15–28m, 15M steps → 95M). **The fix failed; this is the
high-value FALSIFY that redirects the work.**

## What I predicted vs what happened
- **PREDICT (med-high):** training on far-starts closes the obs gap (max|obs-norm| back <3),
  takeoff holds ~100%, gates improve.
- **ACTUAL:** `max|obs-norm| = 10.00` (the VecNormalize **clip ceiling**) at BOTH 80M and 95M.
  Far-start eval got *worse*, not better.

| eval (×15–20)            | takeoff | gates |
|--------------------------|---------|-------|
| 80M @ far (not far-trained) | 60%   | 3.93  |
| **95M @ far (far-trained)** | **47%** | **2.67** |
| 80M @ near (airborne)    | 80%     | 5.67  |
| 95M @ near (airborne)    | 67%     | 6.33  |

Disentangle: general/near skill is comparable (95M ≈ 80M, within n=15 noise). The
degradation is **far-start-specific** — exactly where the clip bites.

## Root cause (one level deeper than the Day-121 live diagnosis)
The observation encodes **raw, unbounded gate-relative distance** (dims ~[9],[12],[13],[18]).
Most training steps happen NEAR gates (0–10m), so VecNormalize's running std is dominated by
the near regime. A far gate (20–25m) is therefore a multi-σ outlier that **clips at 10
regardless of how much far-start data you add** — the policy trains on a saturated,
distance-blind signal. You cannot fix a **normalization-statistics** problem with more data.

This is structural-vs-behavioral (L23): "train on far-starts" is the *behavioral* fix (more
practice); it measurably **made things worse**. The *structural* fix is the representation.

## The real fix (next session — NOT another vanilla retrain)
1. **Bounded distance encoding** in the observation: replace raw gate-relative position with
   **unit direction (3) + bounded magnitude** (e.g. `tanh(dist/scale)` or `log1p(dist)` or a
   capped dist). Apply IDENTICALLY in `vision/adapter.build_observation` (deploy) AND
   `rl/train_ppo.ImprovedObsWrapper` (training) — they must match or the live obs diverges.
2. **Retrain from 80M**, NOT 95M (95M is far-start-degraded; near skill comparable but no
   reason to inherit the regression). Keep ground_start 15–28m so far-starts are in the data
   too — but now the *encoding* keeps them in-range so the data can actually teach.
3. Re-eval ladder + re-fly live.

## Status of the three Day-121 root causes
1. Tumble (sign) — FIXED, test-locked. Unchanged.
2. No-takeoff (ground_start + TWR) — FIXED (takeoff works at near start; far start needs #3).
3. Fly-away — **reclassified**: not merely a training-distribution gap but an **obs-encoding**
   problem. The distribution fix alone is insufficient (proven here). Bounded encoding required.

**Do NOT fly 95M live expecting success — it will still saturate at the 23m VQ1 start.**
The win tonight is the FALSIFY: we now know the fix is the representation, not the data.
