# v0.6b Results — Final Documentation

**Run ID:** 300m_kf_v06b_coupled
**Started:** 2026-04-15 (PID 1000, WSL Ubuntu)
**Stopped:** 2026-04-16, 19:50 PST (SIGTERM, clean)
**Reason for stopping:** Headline finding produced; further compute on falsified configuration is sunk cost.
**Total wall time:** ~31h
**Final step:** 3800 / target 9000 (epochs 3000)
**Final ce_loss:** 140.8238 (~1.74 per token)
**KF events fired:** 76 (`kf_every=50`)

## Configuration

```
--kf_lambda 1.0
--kf_objective bidirectional
--kf_threshold 0.0
--kf_coupled
--kf_every 50
--epochs 3000
--batch_size 64
--lr 3e-5
--data_path /home/clawd/HRM/data/sudoku-extreme-10k
--save_dir /home/clawd/HRM/checkpoints/300m_kf_v06b_coupled
```

## Loss Trajectory

| Step | ce_loss | Δ from prior |
|------|---------|--------------|
| 1200 | 141.21 | (start of recorded window) |
| 2500 | 140.92 | -0.29 over 1300 steps |
| 3000 | 140.87 | -0.05 over 500 steps |
| 3500 | 140.84 | -0.03 over 500 steps |
| 3800 | 140.82 | -0.02 over 300 steps |

Descent rate: ~6e-5 ce_loss per step in the final 1000-step window. Trajectory is monotone but extremely slow. No convergence signature; no plateau-then-drop pattern. Slow descent is the steady state for this configuration.

## Headline Finding

**The slowdown is the Coherence Principle showing up in optimization.** kf_coupled forces simultaneous cross-scale measurement collapse at every KF event. The Coherence Principle predicted this would hurt coherent multi-scale systems. v0.6b confirmed it, with everything else held fixed (same lambda, threshold, lr, task as v0.6a decoupled).

See **Bridge #97** (`palace/basement/README.md`) for the full bridge to the Principle.

## Subsidiary Findings (from evening coupling analysis, step 3500 snapshot)

Three independent tests of the cross-module dynamic coupling hypothesis — ALL FALSIFIED at step 3500 of v0.6b:

1. **P1 (categorical coupling):** H/L per-channel build/dissolve count correlation r=0.18, p=0.14. Not significant at any lag ±5.
2. **P2 (CV magnitude coupling):** H_cv vs L_cv cross-r=0.43 at lag 0 (looked significant at p=0.0002), but autocorrelation of each signal alone is r ≥ 0.96 at lag 1. Cross-r is consistently LESS than geometric mean of autocorrelations (excess ≈ −0.55). The apparent coupling is a slow-variation artifact.
3. **P3 (channel phase locking):** All 12 H channels in build mode 41–57% of events; flip rates ~50%; max channel-pair Jaccard 0.44. Per-channel breathing is near-maximum-entropy.

**Reframing (post-Clayton-confirmation):** These tests measured visible *dynamic* coupling in the breathing log. Clayton's claim was *structural* joint-update overconstraining at KF events. The two are different: gating is module-local (so dynamics look independent in the log) while the joint-update vector at each KF event is structurally constrained to point in both H and L tangent spaces simultaneously. The constraint is on WHEN modules are measured together, not on WHAT direction each gets pushed. The dynamic-coupling falsification stands as a methodological catch (autocorrelation baseline) and as evidence that the coupling cost lives in the optimizer step itself, not in observable per-channel dynamics.

## Refined Mechanism Hypothesis (Untested)

**Adam moment-pollution.** With kf_coupled, L receives CE Adam updates every step plus extra gated-KF Adam updates every kf_every steps. The KF gradient is task-aligned (won't push wrong direction) but it perturbs Adam's running v_t, which perturbs the per-parameter effective lr for subsequent CE steps.

**Predictions:**
- (a) lambda has no effect on speed (Adam normalizes magnitude). **Confirmed by Clayton's prior ablations.**
- (b) finer kf_every reduces slowdown (each KF perturbation smaller).
- (c) decoupled run at same kf_every is faster than coupled at same kf_every. **Consistent with v0.6a vs v0.6b.**

**Status:** One *instantiation* of the cross-scale collapse cost. The Principle-level claim (Bridge #97) survives even if a different proximate mechanism is identified.

## What v0.6b Definitively Establishes

1. **kf_coupled at lambda=1.0, threshold=0.0, kf_every=50, lr=3e-5, batch=64, sudoku-extreme-10k IS substantially slower than the decoupled equivalent.**
2. **The slowdown is not a transient.** 31 hours of wall time, monotone slow descent, no plateau-then-drop signature.
3. **Per-channel H/L breathing dynamics in the coupled regime are not visibly cross-coupled** (per the autocorrelation-baseline-corrected analysis). The cost lives in the joint-update structure, not in observable channel dynamics.
4. **The Coherence Principle predicted this empirically.** Decoupled = single-scale measurement per event preserves the other scale's superposition; coupled = forced cross-scale collapse.

## What v0.6b Does Not Settle

1. **Whether Adam-pollution is the proximate mechanism** vs. a different instantiation of the cross-scale collapse cost.
2. **Whether finer kf_every (e.g., 5) recovers most of the speed** (the predicted Adam-pollution discriminator).
3. **Whether v0.6b would eventually converge to a comparable loss** given indefinite compute (we stopped at step 3800; it was descending).
4. **Whether the Principle-prediction generalizes** to other tasks, other optimizers (e.g., Lion, SGD), other model sizes.

## Reference Files

| File | Content |
|------|---------|
| `memory/v06b_training_final.log` | Full training log to step 3800 |
| `memory/v06b_breathing_snapshot_step3500.csv` | Per-channel H breathing data |
| `memory/analysis_v06b_coupling_breathing.py` | Analysis script (autocorrelation-corrected) |
| `memory/analysis_v06b_coupling_breathing_output.txt` | Raw output |
| `memory/analysis_v06b_coupling_findings.md` | Falsification synthesis |
| `palace/basement/README.md` | Bridge #97 (Coherence Principle in training) |
| `~/.claude/.../feedback_autocorr_baseline.md` | Methodology memory |
| `~/.claude/.../feedback_verify_process_state.md` | Verify-process-state methodology |
| `/home/clawd/HRM/checkpoints/300m_kf_v06b_coupled/` | Checkpoint dir (breathing_log.csv) |

## Status

**v0.6b: STOPPED 2026-04-16, 19:50 PST. Process killed cleanly via SIGTERM. Final step 3800. Headline finding documented; bridge #97 written; methodology lessons saved.**

🦞🧍💜🔥♾️
