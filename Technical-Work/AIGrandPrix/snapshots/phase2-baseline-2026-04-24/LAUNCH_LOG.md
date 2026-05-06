# Phase 2 Launch Log

## 2026-04-24 21:42 PST — launched

**Run dir:** `projects/aigrandprix/sim/runs/infinite_v3_phase2_60M_1777095742/`
**WSL log:** `/home/clawd/aigp_logs/phase2_60M.log` (Python stdout buffered when redirected; check checkpoints + JSON instead)
**Process:** detached via `nohup setsid /home/clawd/run_phase2.sh` — TTY = `?` confirmed

**Configuration (final, post-benchmark):**
- Resume from: `ppo_v3_7500000_steps.zip` + `vec_normalize_reconstructed.pkl`
- Total: 60,000,000 additional steps (final num_timesteps will be 67.5M)
- n_envs: 16
- **Device: cpu** (changed from cuda after pre-launch benchmark)
- save_every: 2,500,000
- LR: 3e-4
- Tag: `phase2_60M`

## Pre-launch benchmark (cpu vs cuda decision)

Ran 50K-step benchmark in WSL Ubuntu (RTX 5080 / 24-core CPU):

| Device | Steps/sec | Wallclock for 50K |
|---|---|---|
| cpu | 2388 | 20.9s |
| cuda | 1882 | 26.6s |

CPU is **27% faster** than CUDA for this MLP[512,512] at 16 envs DummyVecEnv. SB3 explicitly warns about this case — for non-CNN policies the GPU dispatch overhead exceeds compute benefit. RTX 5080 is now reserved for vision-pipeline work where CNN forward pass actually pays for the GPU trip.

**Implication for ROADMAP estimate:** original "30M wallclock ~12-25 minutes on GPU" estimate was wrong. Actual at CPU 2388 sps for 60M = ~7 hours wallclock. Phase 2 will complete overnight.

## Verification at launch + 72s

- Process alive: PID 667, 99% CPU, fully detached
- Run dir created
- First checkpoint already saved: `ppo_phase2_7500016_steps.zip` + `ppo_phase2_7500016_steps_vecnorm.pkl` — both files present, confirms `CheckpointWithVecNormalize` bug fix is working
- `mastery.json` and `grad_norms.json` files created — callbacks firing

## Expected timeline

Assuming 2400 sps holds:
- Step +1M (8.5M total): ~7 min
- Step +2.5M checkpoint (10M total): ~17 min
- Step +5M checkpoint (12.5M total): ~35 min
- **Step +15M (22.5M total) — CHECKPOINT GATE:** ~1h 45min
- Step +30M (37.5M total): ~3h 30min
- Step +60M (67.5M total) — completion: ~7h

## Memory entry created

`feedback_vecnorm_per_checkpoint.md` — codifies the SB3 vecnorm-per-checkpoint discipline so this contamination class doesn't recur.

## Parallel track status

Vision shakedown workbench opened at `projects/aigrandprix/vision/shakedown/`. README + STATUS log in place. First stage (synthetic_camera × gate_detector smoke test) starts on next AIGP work session.

## Monitoring commands

From any session:
```bash
# Process alive?
wsl -d Ubuntu -- bash -lc 'ps -ef | grep train_phase2 | grep -v grep'

# Latest checkpoint?
ls projects/aigrandprix/sim/runs/infinite_v3_phase2_60M_1777095742/checkpoints/ | tail -3

# Mastery progress?
cat projects/aigrandprix/sim/runs/infinite_v3_phase2_60M_1777095742/mastery.json | python -c "import json,sys; h=json.load(sys.stdin); print(f'step {h[-1][\"step\"]:,} | maneuvers: {len(h[-1][\"ema\"])}')"

# Grad norms healthy?
cat projects/aigrandprix/sim/runs/infinite_v3_phase2_60M_1777095742/grad_norms.json | tail -50
```

🦞🧍💜🔥♾️
