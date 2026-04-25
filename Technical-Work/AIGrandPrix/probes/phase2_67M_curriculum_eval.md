# Phase 2 67.5M — Gate-Completion Eval (training-matched config)

> **CORRECTION 2026-04-25 (this re-run).** An earlier run of this probe
> (commit `185a5da`) reported 0/50 gates and concluded "STRATEGY AT RISK."
> That verdict was wrong — caused by an eval bug: the probe read
> `venv.envs[0].episode_gates` *after* `done[0] == True`, but
> SB3's DummyVecEnv auto-resets the underlying env on done, zeroing the
> counter before the read. Corrected probe reads `info[0]['gates_passed']`
> during the step (matching `snapshots/.../eval_per_maneuver.py`). Original
> 0-gate "corroboration" across 4 checkpoints was the same bug repeating.
> The mastery.json being empty across 60M steps is a separate puzzle (likely
> a tracking-code bug, not a training failure) and should not have been
> treated as confirming the bad eval result. See
> `feedback_sb3_gates_after_reset.md` in auto-memory.

**Run:** 2026-04-25 13:46:38  
**Policy:** `sim\runs\infinite_v3_phase2_60M_1777095742\checkpoints\ppo_phase2_67500016_steps.zip`  
**VecNormalize:** `sim\runs\infinite_v3_phase2_60M_1777095742\checkpoints\ppo_phase2_67500016_steps_vecnorm.pkl`  
**Config:** curriculum=True, DR=True (scale=0.15), gate_radius=0.75, dt=0.002

## Why this eval

G5 thrust probe ran with curriculum=False, DR=False and saw zero gates across 10 episodes — but that wasn't the training configuration. This probe answers the question Phase 2's perpetual-generalist + fork-on-track-release strategy depends on: **does Phase 2 67.5M clear gates under its training distribution?**

## Headline

- Episodes run: **30**
- Gates per episode: mean **18.07**, p50 16.5, min 0, max 49
- Episodes with at least 1 gate: **29/30**
- Episodes with at least 5 gates: **27/30**
- Episodes with 0 gates: **1/30**
- Mean steps per episode: 15079

## Curriculum tier segmentation

The adaptive curriculum needs warmup (>=10 episodes for planner activation; >=50 for mastery to leave neutral default). Segmenting shows whether early failures are warmup-mode or true policy gaps.

| stage | episodes | gates_mean | gates_max |
|---|---|---|---|
| warmup_eps_0_to_10 | 10 | 17.10 | 31 |
| early_eps_10_to_25 | 15 | 18.33 | 39 |
| mature_eps_25_plus | 5 | 19.20 | 49 |

## Final planner state

- Final avg mastery: **0.8303609078408912**
- Total planner decisions: **201**
- Complexity distribution exercised:
  - word: 63.18%
  - sentence: 22.39%
  - paragraph: 14.43%
  - essay: 0.00%

## Verdict

**STRATEGY VALIDATED.** Phase 2 67.5M clears gates under training-matched config (mean 18.1 gates/ep). The perpetual-generalist + fork-on-track-release plan has the foundation it needs. Specialization fork on VQ1 release can begin from this checkpoint.

## Per-episode log

| ep | steps | gates | last maneuver |
|---|---|---|---|
| 0 | 30000 | 31 | sprint |
| 1 | 2670 | 5 | diagonal |
| 2 | 28748 | 31 | climb |
| 3 | 7532 | 10 | gentle_arc |
| 4 | 21404 | 20 | chicane |
| 5 | 30000 | 27 | threading |
| 6 | 21712 | 21 | chicane |
| 7 | 3222 | 5 | hairpin |
| 8 | 1860 | 2 | diagonal |
| 9 | 8355 | 19 | dive |
| 10 | 26072 | 28 | chicane |
| 11 | 18438 | 27 | speed_trap |
| 12 | 30000 | 39 | speed_trap |
| 13 | 8043 | 10 | climb |
| 14 | 19350 | 22 | gentle_arc |
| 15 | 30000 | 31 | threading |
| 16 | 6464 | 12 | spiral |
| 17 | 16221 | 23 | chicane |
| 18 | 10994 | 13 | hairpin |
| 19 | 9688 | 17 | chicane |
| 20 | 13475 | 14 | dive |
| 21 | 16255 | 24 | threading |
| 22 | 6753 | 13 | hard_turn |
| 23 | 2716 | 2 | chicane |
| 24 | 9508 | 0 | climb |
| 25 | 9837 | 11 | sprint |
| 26 | 10093 | 14 | dive |
| 27 | 17764 | 16 | hard_turn |
| 28 | 5210 | 6 | spiral |
| 29 | 30000 | 49 | speed_trap |
