# Phase 2 67.5M — Gate-Completion Eval (training-matched config)

**Run:** 2026-04-25 13:31:46  
**Policy:** `sim\runs\infinite_v3_phase2_60M_1777095742\checkpoints\ppo_phase2_67500016_steps.zip`  
**VecNormalize:** `sim\runs\infinite_v3_phase2_60M_1777095742\checkpoints\ppo_phase2_67500016_steps_vecnorm.pkl`  
**Config:** curriculum=True, DR=True (scale=0.15), gate_radius=0.75, dt=0.002

## Why this eval

G5 thrust probe ran with curriculum=False, DR=False and saw zero gates across 10 episodes — but that wasn't the training configuration. This probe answers the question Phase 2's perpetual-generalist + fork-on-track-release strategy depends on: **does Phase 2 67.5M clear gates under its training distribution?**

## Headline

- Episodes run: **50**
- Gates per episode: mean **0.00**, p50 0.0, min 0, max 0
- Episodes with at least 1 gate: **0/50**
- Episodes with at least 5 gates: **0/50**
- Episodes with 0 gates: **50/50**
- Mean steps per episode: 4210

## Curriculum tier segmentation

The adaptive curriculum needs warmup (>=10 episodes for planner activation; >=50 for mastery to leave neutral default). Segmenting shows whether early failures are warmup-mode or true policy gaps.

| stage | episodes | gates_mean | gates_max |
|---|---|---|---|
| warmup_eps_0_to_10 | 10 | 0.00 | 0 |
| early_eps_10_to_25 | 15 | 0.00 | 0 |
| mature_eps_25_plus | 25 | 0.00 | 0 |

## Final planner state

- Final avg mastery: **0.5446859624021461**
- Total planner decisions: **233**
- Complexity distribution exercised:
  - word: 100.00%
  - sentence: 0.00%
  - paragraph: 0.00%
  - essay: 0.00%

## Cross-checkpoint corroboration

The headline result is not a single-checkpoint artifact. Spot-eval at three earlier Phase 2 checkpoints (10 episodes each, training-matched config):

| checkpoint | gates per episode | mean |
|---|---|---|
| ppo_phase2_10000016 (2.5M into Phase 2) | `[0]*10` | 0.00 |
| ppo_phase2_30000016 (22.5M into Phase 2) | `[0]*10` | 0.00 |
| ppo_phase2_50000016 (42.5M into Phase 2) | `[0]*10` | 0.00 |
| ppo_phase2_67500016 (60M into Phase 2 — final) | `[0]*50` | 0.00 |

**Phase 2 produced zero gates throughout training.** The 60M of compute did not move the policy out of the 0-gate basin.

## Training telemetry corroboration

Two pieces of in-training data agree with the eval result:

1. **`mastery.json`: 601 entries spanning step 7,500,016 → 67,500,016. Zero non-empty `ema` or `raw` dicts.** The env's per-maneuver mastery tracker recorded no gate completions across the entire 60M-step run. This is consistent with the eval (the env can't track mastery for behaviors that don't happen) and rules out a "trained-but-eval-broken" explanation.

2. **`grad_norms.json`: F2 (LogStdClampCallback) appears not to be enforcing its lower bound effectively.** The `log_std_values` field shows action-distribution log-std drifting *below* F2's nominal `[0.1, 1.0]` clamp:
   - step  7.5M (resume start): `[0.011, 0.010, 0.012, 0.010]` — below floor (the F2 callback should have lifted these immediately)
   - step 37.5M (mid-train):   `[0.110, 0.114, 0.121, 0.114]` — at floor
   - step 67.5M (final):       `[0.086, 0.070, 0.075, 0.084]` — below floor again

   With log_std collapsed to ~0.07, exploration noise is `exp(0.07) ≈ 1.07x` — effectively deterministic. The policy cannot escape the 0-gate basin via stochastic exploration.

## Verdict

**STRATEGY AT RISK.** The "perpetual generalist + fork on track release" plan presumed Phase 2 67.5M was a working baseline that VQ1 fine-tuning could specialize from. Both the eval (0/50 + 0/10×3 across-checkpoint spot-checks) and the in-training telemetry (mastery=∅ for 60M steps; log_std collapsed below F2's floor) say the baseline is not working.

The G5 0-gate finding (with curriculum=False, DR=False) was not a curriculum artifact — it was the same dead policy showing up in a different configuration.

The Phase 1 manifest (`snapshots/phase2-baseline-2026-04-24/MANIFEST.md`) records that **Phase 2 was launched because Phase 1 v3 7.5M scored 0.03 gates/ep against a "baseline" that scored 16.14 gates/ep**. The cure (F1 vecnorm preservation + F2 log_std clamp + F3 grad telemetry) was supposed to fix the policy. The eval says the cure did not produce gate-completing behavior.

## Suggested next moves (priority-ordered)

1. **Identify the 16.14-gates baseline.** The manifest cites a baseline run that *did* score 16.14 gates/ep. Find that checkpoint. If it exists and reproduces, that — not Phase 2 67.5M — is the perpetual-generalist starting point.

2. **Diagnose the F2 clamp.** `log_std` is below the nominal floor at 4 of 4 timepoints sampled (start, mid, end, resume). Either the callback isn't firing, isn't being applied to the right tensor, or the logged values are read pre-clamp. Inspect `train_phase2.py:LogStdClampCallback` against the actual log_std drift.

3. **Resume training with explicit exploration restoration.** Even if F2 is fixed, log_std starting at 0.011 means the policy's natal exploration is ~10x lower than F2 nominally allows. A clean restart from a higher-noise checkpoint may be needed, not just a clamp.

4. **Reconsider the training recipe.** 60M PPO steps producing zero policy improvement is not a clamp issue — that's the action distribution being so narrow no policy gradient signal can move it. Curriculum + DR + clipped objective may have created a local minimum the policy can't leave at this exploration level. Consider: SAC/entropy bonus increase, or KL-bounded restart, or reward-shaping to densify the gate-approach signal.

The May VQ1 sim drop is the deadline. Diagnosing + retraining a working generalist is the gate that needs to clear before specialization-fork can begin.

## Per-episode log

| ep | steps | gates | last maneuver |
|---|---|---|---|
| 0 | 5000 | 0 | diagonal |
| 1 | 2836 | 0 | gentle_arc |
| 2 | 5000 | 0 | speed_trap |
| 3 | 5000 | 0 | hard_turn |
| 4 | 5000 | 0 | spiral |
| 5 | 5000 | 0 | speed_trap |
| 6 | 877 | 0 | climb |
| 7 | 5000 | 0 | speed_trap |
| 8 | 1211 | 0 | chicane |
| 9 | 5000 | 0 | sprint |
| 10 | 5000 | 0 | hard_turn |
| 11 | 5000 | 0 | hard_turn |
| 12 | 790 | 0 | dive |
| 13 | 5000 | 0 | climb |
| 14 | 5000 | 0 | sprint |
| 15 | 5000 | 0 | dive |
| 16 | 5000 | 0 | spiral |
| 17 | 5000 | 0 | hairpin |
| 18 | 2676 | 0 | diagonal |
| 19 | 5000 | 0 | hard_turn |
| 20 | 5000 | 0 | climb |
| 21 | 4792 | 0 | dive |
| 22 | 5000 | 0 | diagonal |
| 23 | 5000 | 0 | sprint |
| 24 | 5000 | 0 | hard_turn |
| 25 | 5000 | 0 | sprint |
| 26 | 1200 | 0 | chicane |
| 27 | 5000 | 0 | threading |
| 28 | 5000 | 0 | diagonal |
| 29 | 5000 | 0 | diagonal |
| 30 | 4231 | 0 | hard_turn |
| 31 | 5000 | 0 | climb |
| 32 | 5000 | 0 | diagonal |
| 33 | 1691 | 0 | chicane |
| 34 | 5000 | 0 | gentle_arc |
| 35 | 5000 | 0 | threading |
| 36 | 5000 | 0 | diagonal |
| 37 | 5000 | 0 | hard_turn |
| 38 | 2353 | 0 | diagonal |
| 39 | 5000 | 0 | hairpin |
| 40 | 3089 | 0 | hard_turn |
| 41 | 5000 | 0 | climb |
| 42 | 5000 | 0 | hard_turn |
| 43 | 5000 | 0 | climb |
| 44 | 3633 | 0 | diagonal |
| 45 | 5000 | 0 | spiral |
| 46 | 5000 | 0 | hard_turn |
| 47 | 698 | 0 | chicane |
| 48 | 5000 | 0 | hairpin |
| 49 | 400 | 0 | climb |
