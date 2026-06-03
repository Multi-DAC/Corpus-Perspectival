# Anakin — the teacher is the OLD 80M pilot (2026-06-02, Day 122)

**Major finding, verified.** The distillation teacher we needed already exists in the graveyard.

## The three evals (current `InfiniteGateEnv`, ground_prob 0.5)
| pilot | obs | gates/ep | ≥1 gate | maneuver-avg | tool |
|---|---|---|---|---|---|
| **W5 vision student** (final 30M, `…w5loop_1780396881/…ppo_v3_2000128`) | perception | **0.23** | 20% | ~0% | `metrics_anakin.py` |
| **40M privileged teacher** (`…teacher_unitdir_1780340429/…ppo_v3_40000000`) | privileged | **1.32** | 66% | ~20% | `eval_teacher.py` |
| **OLD 80M pilot** (`runs/infinite_1771556763/checkpoints/ppo_infinite_80000000_steps.zip`) | privileged | **10.83** | 100% | **~83%** | raw eval (see below) |

**The OLD 80M pilot is ~8× the 40M teacher and transfers cleanly to the recalibrated env.** This is the
"perfect pilot" the distillation plan needs. Its STATUS.md record (85.5% overall, March/April V2
curriculum) HOLDS in the current env.

## Critical how-to (so this is reproducible)
- The old `infinite_1771556763` run **never used VecNormalize** → there is NO vecnorm pkl, and **it must
  be eval'd RAW** (no VecNormalize wrapper) or obs are wrong-scaled and it fails. `eval_teacher.py`
  assumes a vecnorm; for THIS pilot use the raw inline eval (no VecNormalize) — see the daily log / the
  one-liner that produced 10.83 gates/ep.
- **Dims match the current env: obs=(30,), act=(4,)** (confirmed by loading the policy). So it loads and
  consumes today's `InfiniteGateEnv(perception_obs=False)` obs directly. The feature layout is compatible
  enough that flight skill transfers (83% maneuvers).
- **Best checkpoint = 80M.** Eval'd 65M (3.0 gates/ep, 54%), 67.5M (4.6, 71%), 80M (10.83, 83%) — monotone
  in steps in the CURRENT env (the old-env "best at 60.4M / stalled at 68.6M" ranking does NOT hold post-
  recalibration; here more training = better transfer). `best/best_model.zip` (old EvalCallback best ≈60M)
  exists but 80M wins empirically.

## Honest caveats
1. n was small (12–15 eps). **Re-confirm the 80M with a larger eval (40–50 eps) before building on it.**
2. The Day-83 ρ-probe "wrong-attractor" flag on this pilot was about its INTERNAL representation, not its
   flight — and it flies at 83%, so for *distillation* (we only need good action targets) it likely doesn't
   matter. Note, don't block.
3. Transfers to `InfiniteGateEnv` (the distill env). Whether it transfers to the **real VQ1 sim** is the
   separate W6 question, unchanged.

## The plan, now unlocked
**Distill the OLD 80M privileged pilot → the vision student.** Ceiling jumps from ~1.3 (40M teacher) to
~11 gates/ep. Harness to build (next session, fresh context):
1. Run the 80M pilot (RAW, privileged obs) in `InfiniteGateEnv`, log `(perception_obs, teacher_action)`
   pairs at each step (student sees perception, teacher decides from privileged state — same sim step).
2. Train the vision policy by behavioral cloning to match; ideally DAgger-style on-policy correction so
   the student doesn't drift off the teacher's trajectory distribution.
3. Eval the distilled vision student with `metrics_anakin.py`; target ≫ 0.23 gates/ep.
4. **Read `train_infinite.py` (old) vs `train_infinite_v3.py` (new)** to understand how the old pilot was
   trained differently (curriculum/reward/protocol) — Clayton flagged this; informs why it's so good and
   whether to fold those settings forward.

Tools added today: `eval_teacher.py` (privileged-obs eval). The raw-eval one-liner is in the daily log.
