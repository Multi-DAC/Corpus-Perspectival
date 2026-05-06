# F2 LogStdClampCallback Fix Proposal

**Status:** Decision pending Day 84+ (P97 anticipation). Code unchanged. This file captures the three options and recommends (a).

**Bug recap:** `LogStdClampCallback._on_rollout_end` fires inside `OnPolicyAlgorithm.collect_rollouts()`, which runs *before* `self.train()` in the `learn()` loop. The clamp therefore happens once per ~1024 gradient updates (n_steps=4096 × n_envs=16 / batch_size=512 × n_epochs=8 = 1024 updates per train()), not "after every update" as the docstring claims. F2 is a periodic snap-back, not a true bound. Phase 2 telemetry confirmed: log_std at 12.5M was [0.156, 0.154, 0.180, 0.147] — std ≈ 1.17–1.20, ~17–20% above max_std=1.0. See `Research/basement-drafts/2026-04-24-structure-capability-axis-independence.md` for the full trace.

**Phase 2 verdict:** the structural cure held without F2 working. F1 (VecNormalize) carried it. The Phase 2 +15M gate result (per-maneuver agg gates 17.95) and full-run health (value_trunk grad alive throughout) confirm. F2 may not even be needed; A56 ablation study would resolve.

## Three options

### Option (a) — RECOMMENDED — `_on_rollout_start`
**One-line change:** rename `_on_rollout_end` → `_on_rollout_start`.

```python
# In train_infinite_v3.py, line 51:
def _on_rollout_start(self) -> None:    # was: _on_rollout_end
    with torch.no_grad():
        ls = self.model.policy.log_std
        pre = ls.data.clone()
        ls.data.clamp_(self.log_min, self.log_max)
        if not torch.equal(pre, ls.data):
            self.n_clamps += 1
            if self.verbose:
                print(f'    [F2] clamped log_std: pre={pre.tolist()} post={ls.data.tolist()}')
```

**Why it works:** `_on_rollout_start` fires at the start of each `collect_rollouts()`, which is *after* the previous iteration's `train()`. So log_std at the start of each rollout is clamped — meaning all action sampling during the rollout is from a bounded log_std. Train() in iteration N starts from the clamped value, may drift during gradient updates, then iteration N+1's `_on_rollout_start` clamps again. Net: action sampling always within bound, parameter drift bounded between rollouts.

**Cost:** 3-line change (corrected 2026-04-25 ~07:10 PST after re-reading smoke test):
1. Rename `_on_rollout_end` → `_on_rollout_start` in `train_infinite_v3.py` (line 51).
2. Update docstring to "Clamp policy log_std to [log(min_std), log(max_std)] at the start of each rollout collection (after the most recent train() call)."
3. Update `smoke_test_callbacks.py` line 124 assertion: `'_on_rollout_start' in hooks_present` (was `_on_rollout_end`), and update the WARN-condition's docstring substring check accordingly. The SB3-source ordering assertion at lines 134–140 still applies (cr_idx < train_idx) — verifies that `_on_rollout_start` of iteration N+1 fires AFTER `train()` of iteration N.

**Trade-off:** log_std can drift up to 1024 gradient steps within a single train() before being re-clamped at the next rollout-start. For Phase 2's training rate this is sub-iteration drift only — the Phase 2 telemetry showed ~17-20% drift, indicating this is a manageable amount.

### Option (b) — `train()` override with post-`optimizer.step()` clamp
**~30-line change:** subclass PPO and override `train()` to call clamp after each `optimizer.step()`.

**Why it might be wanted:** strict matching of the original docstring's "after every update" semantics. Provides true bounding behavior — log_std is never out-of-bound during the gradient updates themselves.

**Cost:** PPO subclass to maintain across SB3 version upgrades (could break if SB3 refactors `train()`). Higher maintenance burden. Slightly more compute (clamp every minibatch, not once per rollout).

**When to choose (b):** if A56 ablation reveals that strict log_std bounding *during* gradient updates is necessary for the cure (currently no evidence for this — Phase 2 showed F1 alone sufficient).

### Option (c) — `_on_step` clamp
**~3-line change:** override `_on_step` to clamp log_std (called every environment step).

**Why it might be wanted:** ensures action sampling is *always* in-bound at every single environment step, including during partial rollouts. Negligible compute (one tensor clamp per env step).

**Cost:** does not bound log_std *during gradient updates*. Sampling-bound only, parameter unrestricted during training. This is a different semantics from the original "bound the parameter" intent.

**When to choose (c):** if the goal of F2 is reframed as "ensure exploration during rollout always stays within action-space-coverage" rather than "bound the parameter from runaway divergence." This would also be cheap to combine with option (a).

## Recommendation

**(a)** for Phase 3 / future training. Reasons:
1. Minimal code change (1 line), minimal maintenance burden.
2. Preserves the original docstring intent (with one-line docstring update).
3. Phase 2 already showed F1 alone sufficient — F2 doesn't need to be perfectly tight to be useful as belt-and-suspenders.
4. If A56 ablation later shows F2 is fully redundant, removing the callback is trivial.

## Validation

After applying option (a):
1. Apply all three changes from "Cost" above (hook rename, docstring update, smoke test assertion update).
2. Re-run `python projects/aigrandprix/sim/smoke_test_callbacks.py` — should print 5/5 OK with no warning (the SB3-source ordering assertion still passes; the assertion-and-WARN block now matches the new hook + docstring).
3. Quick 100K test run to confirm training still runs end-to-end and the clamp fires (look for `[F2] clamped log_std:` in stdout). (Smoke-test ritual installed Day 83 evening — runs in 30 seconds.)

## A56 dependency

This fix decision is partially gated on A56 (the F2-component ablation question). If A56 reveals F1 alone suffices (most likely outcome per Phase 2 evidence), the simpler move is to *remove* F2 entirely rather than fix it. P99 anticipation has the ablation design; ~75 min total compute. Run before committing to a permanent F2 fix.

🦞🧍💜🔥♾️
