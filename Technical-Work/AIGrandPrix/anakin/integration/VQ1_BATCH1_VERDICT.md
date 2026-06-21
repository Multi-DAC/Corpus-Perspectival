# VQ1 Reward Pivot — Batch-1 Verdict (rehearsal gate-count, vs seed baseline)

*Day 141 — 2026-06-21 ~13:35 PST. Measured during a creative drive while Clayton drove back. DIAGNOSTIC; the run (pid 9204) is still training — no action taken on it.*

## The test (right instrument, not the proxy)
After yesterday's pivot — train the **VQ1 objective** (gate-count / survival) instead of the VQ2 objective (speed) — the question is whether the chain-first reward (`ANAKIN_VQ1=1`: `CRASH_PENALTY=100=GATE_BONUS`, no speed bonus, `TIME_PENALTY=1.0`) actually produces *chaining*. The right instrument is the **rehearsal gate-count**, not `train_return` (which is −100 by design under this reward and means nothing about quality — Mirror #37).

Ran `translation_rehearsal.py --episodes 10 --env-device cpu` on **two** checkpoints on the **identical harness**:
- **SEED** = `maneuver_appearance_ft/best.pt` (the pre-VQ1 policy) — the baseline I had to generate to avoid attributing a change without a before.
- **VQ1 b1** = `maneuver_vq1_ft/best_vq1_b1_frozen.pt` (after 500k VQ1-reward steps; frozen so batch 2 couldn't overwrite it mid-test).

## Result

| condition | SEED gates | VQ1-b1 gates | SEED return | VQ1-b1 return |
|---|---|---|---|---|
| direct (training-domain anchor) | **1.3** | **1.1** | +67.97 | +21.63 |
| roundtrip (full transfer path) | **1.3** | **1.2** | +68.67 | +48.34 |
| band_resampled | 1.4 | 1.4 | +91.84 | +102.48 |
| band | 1.4 | 1.3 | +98.75 | +77.33 |
| blur | 1.3 | 1.1 | +68.06 | +21.86 |

## Verdict: NO improvement in chaining; slight degradation; return dropped — within n=10 noise

- The VQ1 reward, after batch 1, **did not increase gate-count** over the seed. Direct 1.3→1.1, roundtrip 1.3→1.2 — *down* by 0.1–0.2 gate.
- **Return fell notably** (direct +68→+22) in default-reward units (rehearsal scores with `ANAKIN_VQ1` unset, so both checkpoints are scored apples-to-apples). The policy got *more timid*, not better at chaining.
- **Noise caveat (discipline):** 10 episodes, mostly 1 gate with occasional 2–3; return std ±70–170. A 0.1–0.2 gate delta is **inside the noise band**. This is "no gain / slight degradation," **not** a clean falsification on one batch. Don't overclaim.

## Most likely cause — the reward I designed has a timidity trap
`CRASH_PENALTY = 100 = GATE_BONUS`. So **pass gate 1 (+100) then crash (−100) = net 0.** The risk-minimizing policy is therefore *"pass one gate, then fly cautiously / don't attempt the second"* — exactly the gates≈1, short-episode, near-zero-return pattern that dominates the rehearsal. The reward meant to *encourage* chaining instead made the marginal second gate **not worth the crash risk**.

## Recommendation (Clayton-gated) — two moves, do both
1. **Let the current run continue to ~batch 3, then re-rehearse** (free — it's training anyway). If chaining still hasn't risen above the seed's 1.3 by batch 3, the timidity trap is confirmed, not noise.
2. **Prep reward-v2 as the ready pivot** (spec below). If batch-3 confirms, switch to it immediately rather than burning the remaining 5 batches on a reward that degrades.

### Reward-v2 spec (the fix) — now with a quantified threshold
**Why it works (derived in the afternoon exploration, `palace/south/reward-timidity-ouroboros-bridge-2026-06-21.md` / basement LC56):** model the chain as a repeated gate-MDP. Chaining beats stopping iff gate-success **`p > p* = c/(g+c)`**. So:
- v1 `CRASH=GATE` → **p\* = 0.50** — the policy needs 50% per-gate success *just to make a second attempt worth trying*. In early training (p≈0.3–0.4) chaining is net-NEGATIVE, so the policy *correctly* stops. **That's the trap, quantified.**
- v2 `CRASH=40` → **p\* = 0.29** — chaining goes positive-EV at 29% success, covering the whole early-training band. **Prediction: v2 chains where v1 stalls, in the 29–50% success window.** The batch-3 re-rehearsal is the test.
- **`CRASH_PENALTY = 40`** (well below `GATE_BONUS=100`) → pass-then-crash still nets **+60**, so the second gate is *always* worth attempting; crashing is discouraged but not equal to a gate.
- **Consecutive-gate bonus**: `+25 * (gates_this_episode)` on each gate after the first, making chaining **superlinear** (gate 2 worth 100+25, gate 3 worth 100+50…) — directly rewards the chain, not just the count.
- Keep `SPEED_BONUS_SCALE=0`, `GATE_SPEED_SCALE=0` (VQ1 = no speed), `TIME_PENALTY=1.0` (anti-hover).
- Implement as a `ANAKIN_VQ1=2` branch in `sim/vec_env.py` + `sim/maneuver_env.py` (reversible, like the v1 override). Warm-start from the **seed** (`appearance_ft/best.pt`), not the timid VQ1-b1.

## Process note (the day's theme, again)
This verdict required three disciplined moves that the day's been drilling: (1) measure the gate-count **rehearsal**, not `train_return` (proxy vs target); (2) **generate the seed baseline** before attributing the change (no before = no causal claim); (3) **check the noise band** before calling it a falsification. The reward-design flaw is itself a proxy-for-target instance: `CRASH=GATE` was a proxy for "make chaining matter," but it actually encoded "one gate is enough." Filed against goal #12.
