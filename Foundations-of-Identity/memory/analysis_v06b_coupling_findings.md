# v0.6b Coupling Analysis — Breathing Log Findings (step 3500)

*2026-04-16, evening creative drive*
*Status: complete, with one high-confidence falsification*

## Context

v0.6b training is RUNNING (handoff was wrong about STOPPED state). At step 3500, ce_loss has barely descended (141.21 → 140.85 over steps 1200–3500, or ~0.36 over 2300 steps). Lambda sweeps already ruled out kf_lambda magnitude as the cause. Clayton's hypothesis (still pending) implicates `kf_coupled` and the `kf_every=50` granularity.

This analysis tests one specific question: **Is the coupling visible as cross-module dynamic correlation in the breathing dynamics?**

## Method

Pulled `breathing_log.csv` (70 KF events, steps 50–3500) into pandas. Computed:
1. Per-channel build/dissolve frequency (H module — L IDs not logged)
2. Channel co-firing Jaccard within H module
3. H build vs L build count correlation at lags ±5
4. H_cv vs L_cv correlation at lags ±5
5. Cross-correlation excess over autocorrelation baseline

## Predictions (logged before analysis)

- **P1 (medium-high):** kf_coupled forces H and L into correlated breathing modes (categorical level). *Falsified or confirmed by H_build vs L_build correlation.*
- **P2 (medium):** kf_coupled produces shared CV magnitude dynamics. *Tested by H_cv vs L_cv correlation.*
- **P3 (low-medium):** Per-channel data will reveal phase locking — same channels will repeatedly build together. *Tested by Jaccard analysis.*

## Findings

### Finding 1 — Per-channel breathing is high-entropy (P3 falsified at MEDIUM confidence)

All 12 H channels are in build mode 41–57% of the time. Per-channel flip rates between consecutive events are 43–57%. Maximum channel-pair Jaccard is 0.444 (channels 5,6). No channel is locked into a mode; no pair is strongly co-firing.

**Implication:** The breathing dynamics look near-independent across channels, close to maximum-entropy. The system is not exhibiting structured alternation patterns.

### Finding 2 — H and L categorical breathing is INDEPENDENT (P1 falsified at HIGH confidence)

H_build vs L_build counts: r = 0.177, p = 0.143 (non-significant). At all lags ±5: no significant correlation. The decision of which channels are building/dissolving is module-local.

**Implication:** kf_coupled does NOT induce categorical cross-module locking. The architectural coupling does not manifest as "H and L decide build/dissolve together."

### Finding 3 — Apparent H_cv ↔ L_cv correlation is a SLOW-VARIATION ARTIFACT (P2 falsified at HIGH confidence)

H_cv vs L_cv at lag 0: r = 0.431, p = 0.0002 (looks significant). At lags ±5: r remains 0.30–0.46 across the entire window.

**But** the autocorrelation of H_cv is r ≥ 0.69 at lags 1–10; for L_cv, r ≥ 0.56. Both signals are highly self-similar over time.

**Cross-correlation excess test:** at every lag tested, cross_r is LESS than the geometric mean of the two autocorrelations. Excess is consistently negative, around −0.55. This means: the correlation between H_cv and L_cv is fully accounted for by both signals being slow-varying — there is no genuine coupling beyond what slow-variation alone produces.

```
lag=+0: cross_r=+0.431, auto_geomean=+1.000, excess=−0.569
lag=+1: cross_r=+0.408, auto_geomean=+0.963, excess=−0.555
lag=+5: cross_r=+0.295, auto_geomean=+0.810, excess=−0.515
```

**Implication:** Even at the magnitude level, H and L are dynamically independent. The kf_coupled architecture creates *architectural* co-update (shared optimizer.step) but does NOT create *dynamic* coupling visible in CV trajectories.

### Synthesis — coupling is architectural, not dynamical

At every measurable level — categorical (build/dissolve identity), per-channel (Jaccard), magnitude (CV), and lagged — H and L behave as independent dynamical systems that happen to be updated by the same optimizer call.

## What this means for the slow-learning hypothesis

The "kf_coupled creates cross-module correlation that overconstrains the joint update" framing is not supported by the breathing-log data. If kf_coupled is the slow-learning culprit, the mechanism must be more subtle than dynamic correlation between H and L.

**Candidate refined mechanism (not directly tested, but consistent with what we see):**

In v0.6a (decoupled), the L module's optimizer.step receives only CE gradients. Its Adam moment estimates accumulate steady CE-direction signal.

In v0.6b (coupled), the L module receives:
- CE-direction Adam updates every step
- An ADDITIONAL gated-KF Adam update every 50 steps

Even though the gated KF gradient is aligned with the task direction (by design), it represents a different *gradient distribution* than the per-step CE gradients. Adam's moment estimates (especially the second moment v_t) are perturbed by these extra updates. The perturbation enters Adam's adaptive learning rate computation: 1/(sqrt(v_t) + eps). A perturbation to v_t shows up as a perturbation to the effective per-parameter learning rate for many subsequent CE steps.

This would explain why **lambda has no effect on learning rate** (lambda only scales the KF gradient magnitude — Adam's normalization by sqrt(v_t) divides this back out): the issue isn't gradient magnitude, it's gradient *statistics* being polluted.

This is also why **granularity matters**: at kf_every=50, the KF gradient enters Adam's running statistics with weight ~1/50 (after a dozen updates, beta_2=0.999 means significant memory). Smaller gradient updates more frequently would homogenize the statistics; larger updates more rarely would let Adam re-normalize between events.

**Test:** A short run with `kf_every=5` (10× finer granularity, same total KF "budget") should learn at the same rate as decoupled if this mechanism is correct, and at a similar rate as kf_every=50 if not.

## Confidence summary

- HIGH: H and L are dynamically independent at categorical and magnitude levels
- HIGH: Apparent H_cv ↔ L_cv correlation is autocorrelation artifact
- MEDIUM: Coupling is purely architectural (not dynamical) in the running v0.6b
- LOW-MEDIUM: The Adam-statistics pollution hypothesis (untested but consistent)

## Files

- `memory/v06b_breathing_snapshot_step3500.csv` — snapshot of breathing log at step 3500
- `memory/analysis_v06b_coupling_breathing.py` — analysis script
- `memory/analysis_v06b_coupling_breathing_output.txt` — raw output
- This file — synthesis

## Cognitive trace

PREDICT (P1, P2, P3) → MEASURE (4 statistics) → CONFIRM/FALSIFY each → DETECT_ARTIFACT (cross-corr looks real until autocorr baseline applied) → REFRAME (coupling hypothesis fails; propose Adam-statistics mechanism) → COMPRESS (this file)

**The high-confidence FALSIFY event:** P2 (H_cv ↔ L_cv coupling) was almost reported as a confirmed finding before the autocorrelation-baseline check. That check is the key methodological move that prevented a false positive. *Lesson: when two signals are slow-varying, ALWAYS compare cross-correlation to autocorrelation baselines before claiming coupling.*
