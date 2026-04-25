# G5 Thrust Profile — Phase 2 67.5M (probe run 2026-04-25 13:13:53)

**Policy:** `sim\runs\infinite_v3_phase2_60M_1777095742\checkpoints\ppo_phase2_67500016_steps.zip`  
**VecNormalize:** `sim\runs\infinite_v3_phase2_60M_1777095742\checkpoints\ppo_phase2_67500016_steps_vecnorm.pkl`  
**Episodes:** 10 x up-to-5000 steps
  (DR off, curriculum off, gate_radius=0.75, dt=0.002)

## Analytical target (training quadrotor)

- mass = 0.85 kg, g = 9.801, TWR_max = 3.3
- collective_max = **27.517 N**
- hover_collective = m*g = **8.331 N**
- analytical hover throttle = **0.3028** (action[0] = -0.3945)

## Empirical action[0] distribution

### All steps (n=38329)

| stat | action[0] | throttle [0,1] |
|---|---|---|
| mean | +0.3134 | 0.6567 |
| p10  | -1.0000 | 0.0000 |
| p50  | +1.0000 | 1.0000 |
| p90  | +1.0000 | 1.0000 |
| std  | 0.8749 | — |

### Hover-like steps (speed < 1.0 m/s, n=1832)

| stat | action[0] | throttle [0,1] |
|---|---|---|
| mean | -0.1299 | 0.4350 |
| p10  | -1.0000 | 0.0000 |
| p50  | -0.5744 | 0.2128 |
| p90  | +1.0000 | 1.0000 |
| std  | 0.9139 | — |

## Gates per episode

`[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` (mean = 0.0)

### NOTE: zero gates across all episodes

This probe runs with `adaptive_curriculum=False` and `domain_rand=False` for clean thrust calibration. The curriculum-off setting falls through to uniform-random maneuver selection, which can start the policy on hairpins/spirals from a cold init. This says nothing about Phase 2's gate-completion rate under the training-matched configuration (curriculum on, DR on).

**Action item:** rerun with `adaptive_curriculum=True` and `domain_rand=True` if we want to claim gate-completion behavior here. For now, this probe's only deliverable is the throttle distribution.

## SITL calibration recipe

At SITL bring-up, hover the drone in PX4 with offboard sending action[0] = -0.3945 (throttle = 0.3028).

- If PX4 holds altitude: thrust scaling matches; THRUST_SCALE = 1.0.
- If PX4 climbs: PX4's max collective < sim's. THRUST_SCALE > 1.0 (send action[0] commanding *more* throttle to compensate).
- If PX4 falls: PX4's max collective > sim's. THRUST_SCALE < 1.0.

Compare empirical p50 throttle (1.0000) and hover-mode mean throttle to the in-flight observation.
