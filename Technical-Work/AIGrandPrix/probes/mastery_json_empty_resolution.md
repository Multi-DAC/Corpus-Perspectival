# mastery.json Empty Across 60M Steps — Resolved

**Filed:** 2026-04-25 mid-afternoon (Day 84)
**Run:** `sim/runs/infinite_v3_phase2_60M_1777095742/`
**Status:** RESOLVED — not a training failure, not an env tracker bug

## The puzzle

`mastery.json` for Phase 2 contains 601 entries from step 7,500,016 to
67,500,016 (100K-step increments, full duration). Every entry is
`{"step": N, "ema": {}, "raw": {}}`. Zero per-maneuver mastery data
landed across the entire 60M-step extension.

This was originally treated as corroborating evidence that Phase 2 was
broken (alongside the false 0-gate eval). Both have now been falsified.
The eval bug was Mirror #21 / `feedback_sb3_gates_after_reset.md`. This
note resolves the second piece.

## Diagnosis

Two-line schema diff is dispositive.

**On disk (601 entries):** keys are `"step"`, `"ema"`, `"raw"`.
**In `train_phase2.py` today:** `PerManeuverMasteryLogger._on_step` writes
keys `"step"`, `"ema_overall"`, `"raw"` (line 136-140).

`ema_overall` appears zero times in the on-disk file.

## Root cause

The Phase 2 training daemon (PID 667, launched 2026-04-24 21:42 PST) loaded
the *pre-fix* version of `PerManeuverMasteryLogger`. That version:

- Tried `inner.mastery_ema` — attribute does not exist on `InfiniteGateEnv`
- Tried `inner.mastery_raw` — attribute does not exist on `InfiniteGateEnv`
- Both reads fell through to empty-dict defaults
- Logged `{"step": N, "ema": {}, "raw": {}}` every 100K steps for 60M steps

The fix landed on disk during the 2026-04-25 ~00:30 PST late-night drive
(`feedback_wsl_process_mgmt`-style: launcher script + nohup, daemon does
not pick up source changes). Restarting the training process to pick up
the fix would have lost 7+ hours of compute, so we let it finish on the
old callback. The fix is in source for the next training run.

## What's NOT broken

The env's mastery tracker itself works correctly. Verified by
`sim/smoke_test_callbacks.py:env_contract` (check #2) — both
`InfiniteGateEnv._get_per_maneuver_masteries()` (returns dict) and
`InfiniteGateEnv._ema_mastery` (returns float) exist and return the
expected types post-`env.reset()`.

The trajectory eval (morning 2026-04-25, 22.5M → 67.5M) and the
training-matched eval (afternoon 2026-04-25, 18.07 gates/ep on 67.5M)
both confirm Phase 2 is a working generalist. The empty mastery.json
was a logging artifact, not a training signal.

## Cost / impact

- 60M-step worth of per-maneuver mastery telemetry permanently lost for
  this run. We cannot reconstruct which maneuvers strengthened/weakened
  during Phase 2 from the mastery.json file.
- Partial substitute available: re-derive an instantaneous per-maneuver
  mastery snapshot from any saved checkpoint by loading the env, running
  N evals per maneuver type, and computing pass rates. Coarser than the
  EMA telemetry but recoverable.
- Future training runs (Phase 3+) get correct telemetry from the fixed
  callback.

## Apparatus implication

The smoke test that catches this bug class (`smoke_test_callbacks.py`
check #2: env contract) was added the same late-night drive that caught
the attribute-name mismatch. Running the smoke test before launch would
have caught the bug in 30 seconds. The discipline now stands: any new
callback that reads env attributes must pass the env-contract check
before launch. See Mirror entry on smoke-testing-what-you-just-wrote.
