# Phase 2 Baseline Snapshot — 2026-04-24

Frozen state at Phase 2 GPU retrain launch. This snapshot is the canonical reference for what the code looked like when the run started — diff against future versions to recover *what changed* if Phase 2 results need re-interpretation.

## Provenance

- **Snapshot date:** 2026-04-24 evening PST
- **Git SHA at snapshot:** `2a0d719cf02a34dd0f7ad0b4b5beb692545ba861` (clawd repo, main)
- **Triggering event:** Phase 1 corrected eval confirmed Reading B (v3 7.5M = 0.03 gates, baseline = 16.14, control = 0.07). Phase 2 mandatory.

## Resume artifacts

- **Policy:** `sim/runs/infinite_v3_retrain10M_1777074572/checkpoints/ppo_v3_7500000_steps.zip`
- **VecNormalize:** `sim/runs/infinite_v3_retrain10M_1777074572/vec_normalize_reconstructed.pkl` (reconstructed via `probes/reconstruct_vecnorm.py` — original was lost when v3 retrain was killed before training-end save fired)

## V2 curriculum settings (baked into `infinite_gate_env.py`)

- **Stages:** Words → Sentences → Paragraphs → Essays
- **Soft boundaries** between stages (no hard graduation; mixture sampling)
- **Per-maneuver filtering** of difficult sequences below mastery thresholds
- **Asymmetric EMA:** α=0.02 rise, α=0.005 fall (mastery climbs fast, decays slow)
- **gate_speed_scale:** 0.08 (kept unchanged for one-to-one comparison + speed is competition-relevant)
- **Domain randomization:** 15% (mass, drag, motor strength variations)
- **gate_radius:** 0.75
- **dt:** 0.002 (500 Hz physics)
- **substeps:** 1
- **max_steps:** 30,000

## Train hyperparameters (baked into `train_phase2.py`)

- **Algorithm:** PPO (stable_baselines3)
- **Policy:** MLP[512, 512]
- **Learning rate:** 3e-4 (constant — not fine-tuning territory at 100% crash baseline)
- **Total steps:** 60,000,000 (continues from 7.5M; final = 67.5M)
- **n_envs:** 16
- **base_seed:** 17
- **device:** cuda (RTX 5080)
- **save_every:** 2,500,000 steps (policy + vecnorm both saved per checkpoint via `CheckpointWithVecNormalize`)
- **grad_log_freq:** 100,000
- **mastery_log_freq:** 100,000

## F1+F2+F3 cure (active throughout)

- **F1 — VecNormalize:** running obs/reward normalization (loaded from reconstructed pkl; preserved across resume)
- **F2 — LogStdClampCallback:** clamps action log_std to [0.1, 1.0] every step (prevents the log_std[3]=40 explosion seen in baseline)
- **F3 — GradNormLoggerCallback:** per-100K telemetry on policy + value gradient norms (catches incipient pathology)

## Bug fix introduced for Phase 2

- **CheckpointWithVecNormalize:** new callback in `train_phase2.py` that saves both `policy.zip` AND `vecnorm.pkl` at every checkpoint. Fixes the contamination class that broke Phase 1 eval (stock SB3 CheckpointCallback only saves the policy; vecnorm is lost if the run is killed before the manual `train_envs.save(...)` at training-end fires).

## Files in this snapshot

| File | Purpose |
|---|---|
| `infinite_gate_env.py` | Env + V2 curriculum (frozen at launch) |
| `sequence_generators.py` | Maneuver primitives (frozen at launch) |
| `train_infinite_v3.py` | Original train script — has the contamination bug; preserved for diff |
| `train_phase2.py` | Phase 2 train script with `CheckpointWithVecNormalize` |
| `eval_per_maneuver.py` | Three-way eval harness (frozen at launch) |
| `reconstruct_vecnorm.py` | Recovery tool — populates VecNormalize stats from policy rollout |
| `MANIFEST.md` | This file |
| `CHECKPOINT_GATE.md` | Decision criteria for the +15M evaluation gate |

## Why snapshot at launch

If Phase 2 produces a surprising result — capability climbs fast, capability stays flat, structure regresses, anything outside expectation — the first move will be diff-against-baseline to localize the change. This snapshot is the diff target.

🦞🧍💜🔥♾️
