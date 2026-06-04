# Gaze-Aware Fine-Tune — Result (2026-06-02, Day 122 evening)

**Verdict: FALSIFIED as configured.** Warm-start fine-tuning frozen Anakin on the corrected-camera
obs did **not** teach gaze-aware nose-forward flight — it slightly *degraded* the policy. Frozen
Anakin remains the best deploy policy we have.

Continuation of `PERCEPTION_CLIFF_FINDING_2026-06-02.md` (the camera-axis bug + corrected-camera
validation). This was the "extra reach" past the camera fix; the reach didn't pay.

## What was run
- `train_vision_corrected.py --total-steps 3000000 --n-envs 8 --tag gaze1`
- Warm-start from 80M Anakin (`runs/infinite_1771556763/.../ppo_infinite_80000000_steps.zip`), RAW
  (no VecNorm), lr=1e-4, max_grad_norm=0.3, F2 log_std clamp [0.1,1.0].
- Corrected camera = **+x nose +20° up-tilt** (`CAM_NOSE_TILT=[cos20,0,sin20]`, Option A — the
  FIXED competition spec per Clayton: the tilt is on the drone, not our mount), dead-reckon ON,
  domain_rand + adaptive_curriculum ON.
- Ran on **CPU** (Python 3.14 / torch 2.11.0+cpu — no CUDA on Windows side). 3M steps in **20.9 min**.
- Run dir: `runs/vision_corrected_gaze1_1780465000/` (checkpoints @ 500k/1M/1.5M/2M/2.5M/3M + final).

## The two stories (why this is a measure-before-framing case)

**Training rollout (stochastic, curriculum-on) — looked like a WIN:**
```
 300k: 3.22 | 500k: 4.06 | 800k: 4.20 (PEAK, near clean 4.83) | 1M: 2.80 | ... | 3M: 1.92
```
Read naively: "gaze fine-tune works, peaks near clean ~800k, then overtrains." **This reading is wrong.**

**Deterministic eval (`eval_gaze1.py`, n=24, +x+20°tilt/reckon/all-W3, fixed difficulty) — a LOSS:**
```
            checkpoint  gates/ep  max   >=1%  takeoff
   frozen Anakin (ref)      1.96    4     88   24/24    <- the "before" (best)
           gaze1  500k      1.29    4     67   24/24
           gaze1 1000k      1.42    4     54   24/24
           gaze1 1500k      1.00    4     46   21/24
           gaze1 2000k      1.67    5     67   21/24
           gaze1 final      0.79    2     54   22/24
```
**Every fine-tuned checkpoint underperforms the frozen baseline.** The 500k "4.06" became 1.29 deterministically.

## Diagnosis
1. **Curriculum confound (main).** Training ran `adaptive_curriculum=True` + `randomize=True`, so the
   curriculum eases gate difficulty to track policy skill. Training gates/ep is therefore **not
   comparable across time or to fixed-difficulty eval**. The "4.2 peak" was on an easier track.
   → *Rule going forward: never trust training-rollout gates/ep as a performance signal under adaptive
   curriculum. Select checkpoints by periodic DETERMINISTIC eval only.*
2. **No gaze-specific reward (deeper).** PPO only sees gate-passing through the (degraded) obs. There
   is **no reward term rewarding nose-toward-next-gate**, so there was never a gradient teaching gaze.
   The fine-tune just drifted off the warm-start basin (lr=1e-4 too hot for too long).

## Reconciliation flag (minor)
Frozen Anakin = **1.96** here vs **1.42** in `nose_axis_test.py` for the same +x+20°tilt config.
Different n / seed / randomize settings between harnesses. Doesn't change the within-eval conclusion
(frozen > all fine-tuned), but tighten the reference harness before quoting absolute numbers.

## Next experiment (design fresh — NOT a blind re-run)
- Add a **heading/gaze reward-shaping** term: reward alignment of body-+x (nose) with bearing-to-
  next-gate. This is the missing gradient.
- Drop **lr to ~3e-5**, shorter horizon (~500k–1M), early-stop.
- **Select by periodic deterministic eval**, not training rollout.
- Open question worth a basement bridge: *does every privileged-teacher→perception transfer hide a
  latent "policy never learned to look where it's going" debt?* (omniscient teachers never need gaze.)

## Files (all in `sim/`, uncommitted)
`train_vision_corrected.py`, `eval_gaze1.py`, `eval_gaze1.log`, `train_gaze1.log`,
`runs/vision_corrected_gaze1_1780465000/` (gitignored).
