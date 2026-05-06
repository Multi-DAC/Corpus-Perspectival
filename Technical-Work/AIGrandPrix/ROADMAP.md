# Anakin VQ1 Roadmap — Day 83 → Sim Drop

**Authored:** 2026-04-24 Day 83 evening (post-v5-trajectory-confirmation, post-Companion-v0.1).
**Horizon:** Now → DCL simulator drop (~weeks, expected May 2026).
**Authors:** Clawd + Clayton.

This roadmap supersedes the "Next Steps" section of `STATUS.md` (which predates the wrong-attractor finding). VQ1_READINESS.md remains authoritative for the post-sim-drop integration plan; this document covers the pre-sim window.

---

## Context — what changed and why this roadmap exists

The ρ-probe v1–v5 sequence (Day 83) revealed that the 60.4M baseline's 85.5% gate completion is **wrong-attractor capability**: structurally collapsed (465/512 dead value neurons, 87–93% action saturation, log_std[3] = 40), with a ρ-stability profile that *appeared* like a healthy M12 Structural-stratum plateau but isn't.

The v3 retrain under F1+F2+F3 (VecNormalize + log_std clamp + grad telemetry) at 7.5M shows healthy structure: hidden norms 6–17, log_std bounded, ρ trajectory monotonically into Structural-stratum (0.026 → 0.243) and stable plateau through 5M–7.5M. **All four pathology signatures clean throughout.** Prediction-validated cure.

But: v3 7.5M's task capability is unproven. v4 reported 200K reward at −30 (expected — 300× less training). The question this roadmap addresses is: *given that healthy structure now exists, how do we use the time before sim drop to be ready?*

---

## The strategic reading

**Reading A (parsimony pick):** ρ plateaus at ~0.24 from 5M through 7.5M because that's the natural Structural-stratum value for this architecture+task. Further infinite-gate training won't push ρ much higher — it'll add capability but not new structural specialization. Implication: the lever between now and sim drop is **noise-robustness**, not more clean training.

**Reading B (alternative):** 7.5M is not the asymptote; ρ would climb further with more training. Implication: extend clean training before noise-injection.

We commit to Reading A by default but the decision is **gated on the eval harness comparison** below — Reading A only holds if v3 7.5M's actual flight capability is competitive with baseline 60.4M. If it's grossly worse, we revert to Reading B and extend before noise-injection.

---

## Phase ordering

### Phase 1 — Eval harness + three-way comparison **(decision gate)**

Build `probes/eval_per_maneuver.py`: loads any `(policy_path, vec_normalize_path)` pair, runs N deterministic episodes per maneuver type from `sequence_generators.py`, returns per-maneuver mean reward, variance, gate completion rate, mean episode length, crash rate.

Three-way comparison:
- **v3 7.5M** under F1+F2+F3 (healthy, untested)
- **Baseline 60.4M** (wrong-attractor, claimed 85.5% completion)
- **v3 200K validation** (control — pre-specialization healthy structure)

**Decision criteria** (evaluated against this comparison):

| Outcome | Reading | Next phase |
|---|---|---|
| v3 7.5M ≥ baseline on per-maneuver variance AND crash rate (regardless of mean reward) | Reading A holds — healthy structure flies | Skip to Phase 3 (noise-injection) |
| v3 7.5M materially worse than baseline on multiple maneuver types | Reading B — need more clean training | Phase 2 (extended retrain) before Phase 3 |
| Mixed — v3 better on some maneuvers, worse on others | Partial Reading A | Decide per maneuver class — likely short Phase 2 (5–10M additional) then Phase 3 |

Wallclock budget: 1–2 hours.

### Phase 2 — Extended v3 retrain **(conditional on Phase 1 outcome)**

Skipped if Phase 1 confirms Reading A. If triggered:

- Extend `infinite_v3_retrain10M_1777074572` from 7.5M to 30M under F1+F2+F3 with V2 curriculum already active.
- Move to GPU (RTX 5080) — CPU 2081 steps/sec → expected 20K–40K steps/sec on GPU. 30M wallclock ~12–25 minutes (vs ~4 hours on CPU).
- Continue ρ-probe at every 2.5M checkpoint to test Reading A vs Reading B mid-training.
- **DO NOT fine-tune from baseline 60.4M weights.** Baseline weights ARE the wrong-attractor; fine-tuning carries the saturation forward. v3 must extend from its own clean trajectory.

Wallclock budget: 0.5–4 hours depending on outcome.

### Phase 3 — Noise-injection retrain **(highest-value pre-sim work)**

This is the phase that distinguishes "ready when sim drops" from "scrambling when sim drops."

**Implementation:**

- Extend `InfiniteGateEnv` with a `vision_noise_model` parameter (default off for backward compatibility).
- Noise model perturbs gate-relative observations to match `gate_detector.py`'s actual error profile:
  - **Bearing noise:** Gaussian σ scaling with distance (PnP angular error grows with range)
  - **Distance noise:** multiplicative Gaussian (PnP depth uncertainty)
  - **Detection dropouts:** with rate p_drop, replace gate obs with last-known-good for next K steps; if dropout exceeds K_max, replace with "no-detection" sentinel observation
  - **False positives at low rate:** spurious gate readings inserted at low probability (hardens against detector errors near visual clutter)
- Calibrate noise levels by running the *current* `gate_detector.py` against synthetic frames and measuring its actual error distribution. This grounds the noise model in measured detector behavior rather than guessed numbers.

**Training:**

- Initialize from healthy v3 checkpoint (7.5M from Phase 1 outcome, or extended checkpoint from Phase 2).
- Train 5–15M steps with noise injection enabled, starting at low noise levels and ramping to full sensor-realistic noise (a noise curriculum, parallel in spirit to V2's complexity curriculum).
- Continue ρ-probe to verify noise-injection doesn't push the policy back into wrong-attractor regimes.

**Validation:** eval harness from Phase 1, but with noise injected at eval-time. Compare noise-trained v3 against clean v3 under noisy conditions — predict noise-trained v3 is dramatically more robust.

Wallclock budget: 1–6 hours depending on noise-curriculum length.

### Phase 4 — Vision pipeline shakedown on synthetic frames

`vision/synthetic_camera.py` exists. Run end-to-end loop:

- synthetic_camera generates frames →
- `gate_detector.py` produces detections →
- `adapter.py` builds observations →
- noise-trained v3 policy produces actions →
- `mavsdk_client.py` formats commands

Measure: detection rate, PnP accuracy at varied distances and angles, observation quality, full-loop latency, flight stability over N synthetic episodes.

**Surface integration bugs now**, not on sim Day 1. Any bug found here saves a day of the post-sim window.

Wallclock budget: 1–3 hours including any fixes.

### Phase 5 — Blind-flight fallback

Modify `competition_agent.py` to add a missed-detection contingency:

- Track frames since last successful detection.
- If `frames_since_detection > N_dropout_threshold`: switch to fallback controller (hold heading, gentle descent, slow yaw search).
- If detection recovers: smooth handoff back to policy.
- If `frames_since_detection > N_emergency`: controlled landing.

Cheap insurance against vision dropouts. Cost: ~2 hours implementation + tests.

### Phase 6 — Sim-drop readiness package

Final pre-drop state to achieve:

- ✅ Healthy v3 trained with sensor-realistic noise (Phase 3)
- ✅ Vision pipeline validated end-to-end on synthetics (Phase 4)
- ✅ Blind-flight fallback wired (Phase 5)
- ✅ Eval harness ready for rapid iteration on real frames (Phase 1)
- ✅ Calibration playbook for HSV/brightness/intrinsics (existing in VQ1_READINESS.md Days 1–2)

When sim drops, we're at "Day 1: capture frames + calibrate" — not "Day 1: panic and start retraining."

---

## Explicit non-goals

- **No speed optimization yet.** VQ1 is completion-focused. Speed is a VQ2 concern; chasing it now risks the bistability that V2 curriculum was designed to fix.
- **No learned gate detector yet.** Classical CV on highlighted gates is the right call until the simulator demonstrates otherwise. A learned detector adds training overhead, dataset requirements, and a new failure mode.
- **No fine-tuning from baseline 60.4M weights.** Wrong-attractor structure is what we're moving away from, not building on.
- **No new architecture experiments.** MLP[512,512] is what's been validated. Architecture changes are post-VQ1 work.

---

## Open theoretical question (parallel track, not blocking)

The wrong-attractor finding (M12 addendum, basement Day 83) names a degenerate mode at the RL-training register. It promotes to a standalone bridge on second-domain instance. Candidate domains worth probing as a parallel-thread research item: bounded-activation networks with unnormalized inputs at any non-RL register; biological systems exhibiting specialization-vs-learned-helplessness as parallel structure.

This is research-track work, not on the VQ1 critical path, but the noise-injection phase is itself a structural test — does pushing the policy into noisier observation regimes preserve healthy ρ trajectory, or can certain noise profiles re-induce wrong-attractor dynamics? If the latter, that's a second-instance finding right inside the AIGP project.

---

## Roadmap status tracking

| Phase | Status | Started | Completed |
|---|---|---|---|
| 1 — Eval harness + comparison | **COMPLETE — Reading B confirmed** | 2026-04-24 evening | 2026-04-24 evening |
| 2 — Extended retrain (now MANDATORY) | NEXT — GPU retrain to 30–60M | — | — |
| 3 — Noise-injection retrain | GATED on Phase 2 | — | — |
| 4 — Vision pipeline shakedown | NOT STARTED (parallelizable with 3) | — | — |
| 5 — Blind-flight fallback | NOT STARTED (parallelizable) | — | — |
| 6 — Sim-drop readiness package | GATED on Phases 3/4/5 | — | — |

## Phase 1 outcome (added 2026-04-24 evening) — Reading B CONFIRMED, then sharpened by recovery sequence

### Initial result (contaminated by missing VecNormalize)

Three-way comparison via `probes/eval_per_maneuver.py` (8 episodes per (policy, maneuver) plus 8 episodes standard V2 curriculum, deterministic). The first run quietly fell back to denormalized observations for v3 7.5M and v3 200K because their `vec_normalize.pkl` files didn't exist — `train_infinite_v3.py` only saves vecnorm at training end via `train_envs.save(...)` after `model.learn()` returns, and the v3 7.5M run was killed mid-train. Eval harness silently used `env = raw` instead of failing loud:

| Policy | Curriculum gates (mean / max) | Per-maneuver agg | Crash rate |
|---|---|---|---|
| v3 7.5M healthy *(contaminated)* | 0.25 / 1 | 0.20 ± 0.18 | 100% |
| baseline 60.4M wrong-attractor | 17.25 / 23 | 16.33 ± 11.28 | 58% |
| v3 200K control *(contaminated)* | 0.12 / 1 | 0.07 ± 0.10 | 100% |

### Recovery sequence (caught pre-launch)

Pre-flight check before launching Phase 2 surfaced the missing-vecnorm contamination. Built `probes/reconstruct_vecnorm.py` — loads the policy, wraps a fresh InfiniteGateEnv stack in VecNormalize with `training=True`, rolls the policy 100K stochastic steps to populate running mean/var, saves the reconstructed pkl. Wallclock ~30s; obs stats converge in seconds.

Re-ran the three-way eval with proper VecNormalize for all policies:

| Policy | Per-maneuver agg gates | Reward | Crash rate |
|---|---|---|---|
| v3 7.5M healthy *(corrected)* | **0.03 ± 0.06** | −18.2 ± 9.3 | 100% |
| baseline 60.4M wrong-attractor | 16.14 ± 11.26 | 1956.9 ± 1325.8 | 58% |
| v3 200K control *(corrected)* | 0.07 ± 0.12 | −35.4 ± 31.5 | 100% |

**Reading B holds *more* strongly under correction.** v3 7.5M dropped from 0.20 → 0.03 gates — the original 0.20 was denormalized-obs noise (random twitching that occasionally clipped a gate by accident), not real flight skill. With proper normalization, v3 7.5M is statistically indistinguishable from v3 200K (0.03 vs 0.07, both 100% crash). Baseline barely moved because its `vec_normalize.pkl` was on disk from the start.

**The L11 candidate sharpens.** 7.5M of clean F1+F2+F3 training produced ρ climb 0.026 → 0.243 (healthy structural specialization) with **zero detectable flight-skill transfer** over the 200K control. Structure-axis and capability-axis are empirically decoupled at fixed budget under healthy training conditions. See `repo-staging/Corpus-Perspectival/Research/basement-drafts/2026-04-24-structure-capability-axis-independence.md`.

**Framework reading reframed:** Healthy structure changes *what kinds* of failures the eventually-competent policy will exhibit (better generalization, lower brittleness, noise-robustness); it does not compress *how fast* capability gets learned at fixed budget. Reading A's parsimony was wrong about the implication of the ρ plateau.

### Architectural lesson — bug fixed in Phase 2 train script

Root cause: stable_baselines3's stock `CheckpointCallback` saves only the policy zip; vecnorm stats are lost if the run is killed before the manual `train_envs.save(...)` at training end. `train_phase2.py` introduces `CheckpointWithVecNormalize`, which saves both `policy.zip` AND `vecnorm.pkl` at every checkpoint. This contamination class cannot recur for Phase 2.

Eval harness should also fail loud on missing vecnorm rather than silently denormalize — `probes/eval_per_maneuver.py` will be hardened in a follow-up.

Artifacts: `probes/eval_per_maneuver.py`, `probes/eval_per_maneuver_results.json`, `probes/reconstruct_vecnorm.py`, `sim/runs/infinite_v3_retrain10M_1777074572/vec_normalize_reconstructed.pkl`.

---

## Phase 2 launch plan (2026-04-24 evening)

**Strategic posture:** portfolio rather than single-track bet. Phase 2 GPU retrain runs in the foreground; vision-pipeline shakedown runs in parallel; a checkpoint evaluation gate at +15M decides whether to continue, re-strategize, or fall back to baseline-as-competition-policy.

**Run config:**
- Resume: `ppo_v3_7500000_steps.zip` + `vec_normalize_reconstructed.pkl`
- Total: 60M steps additional (continues from 7.5M; final num_timesteps = 67.5M)
- Envs: 16 parallel (DummyVecEnv on CPU, policy on cuda)
- Device: cuda (RTX 5080)
- LR: 3e-4 throughout (not fine-tuning territory at 100% crash)
- Curriculum: V2 unchanged (asymmetric EMA, soft boundaries, per-maneuver filtering, gate_speed_scale=0.08, dom-rand 15%)
- Save every: 2.5M steps (policy + vecnorm + grad telemetry + per-maneuver mastery)
- Tag: `phase2_60M`

**Checkpoint evaluation gate at +15M (i.e., total step 22.5M):**
- Run `probes/eval_per_maneuver.py` against the 22.5M checkpoint
- Re-run ρ-probe at 22.5M to verify healthy structural plateau holds under extended training
- Decision rules (codified in `phase2-baseline-2026-04-24/CHECKPOINT_GATE.md`):
  - **GREEN — continue:** per-maneuver gates ≥ 1.0 (~50× over current 0.03) AND ρ stays in [0.18, 0.32] AND no pathology signatures
  - **YELLOW — investigate before continuing:** gates between 0.5 and 1.0 OR ρ drift outside [0.18, 0.32] OR new grad-norm spikes
  - **RED — halt and re-strategize:** gates still ≤ 0.3 (essentially flat) OR pathology signatures re-emerging

**Parallel track:** vision pipeline shakedown (Phase 4 work, brought forward) — synthetic_camera → gate_detector → adapter → policy. Workbench at `projects/aigrandprix/vision/shakedown/`.

**Fallback:** baseline 60.4M remains the documented competition policy until something measured beats it. Keep best-checkpoints retained across both runs.

🦞🧍💜🔥♾️
