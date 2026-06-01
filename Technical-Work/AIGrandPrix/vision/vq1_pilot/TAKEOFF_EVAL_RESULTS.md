# Takeoff retrain — checkpoint eval (our sim, ground-start ×20)

Run: `runs/infinite_v3_takeoff_twr385_1780305737` (fine-tune from 67.5M, ground_start_prob=0.3,
TWR 3.85). Eval = `eval_takeoff.py` forces ground_start_prob=1.0, deterministic policy.
**Our calibrated sim, NOT the competition sim** — necessary, not sufficient. n=20 (noisy).

| Step    | Takeoff% | Mean gates | Max gates | Mean max-alt | Endings (clean/ground/oob) |
|---------|----------|------------|-----------|--------------|----------------------------|
| 75.0M   | **100%** | 5.70       | 14        | 7.11 m       | 10 / 8 / 2                 |
| 77.5M   | **100%** | 4.90       | 15        | 6.19 m       | 9 / 10 / 1                 |

## Reading
- **Takeoff SOLVED + stable** — 100% liftoff from cold ground start at both checkpoints.
  Closes VQ1 failure mode #1 (the 67.5M policy idled on the pad).
- **Plateau** — mastery EMA flat at 0.878 from 75M→77.7M; gates 5.70→4.90 is noise around a
  plateau, not improvement. The takeoff curriculum was learned within ~7.5M fine-tune steps.
- **Dominant downstream failure = 'ground'** (8–10 of 20): it takes off and flies, then
  descends into the ground later in the episode. Flight-quality/altitude-hold issue
  downstream of liftoff, not a takeoff issue.

## Decisions
1. **Select checkpoint by eval, not recency** — RL non-monotonic; 75M ≥ 77.5M here. Eval the
   full ladder (70/72.5/75/77.5/final) and pick best-by-gates before the live re-fly.
2. **Next takeoff fine-tune: ~7.5M steps, not 15M** (half compute) — plateau evidence.
3. **Re-fly the SELECTED checkpoint** via `state_pilot.py` (corrected send path) against the
   live VQ1 sim — the real verdict. Needs Clayton + sim.

## Caveats
- n=20, high variance (max-gate 14–15 vs mean ~5). Treat the 5.7/4.9 gap as noise.
- Our-sim gate-count is open-ended (infinite-gate env), not VQ1's fixed 6 — takeoff transfer
  is the load-bearing result, not the absolute gate number.
