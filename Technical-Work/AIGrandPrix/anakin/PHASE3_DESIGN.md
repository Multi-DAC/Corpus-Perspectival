# Phase 3 — the grammar of flying on DreamerV3 (design lock)

**Day 124 (2026-06-04).** Phase 2 is green (Dreamer learns gated flight from pixels; lesion
confirmed the learning is genuinely vision-driven, not odometry — see `LESION_TEST_2026-06-04.md`).
Phase 3 turns the make-or-break loop into a **racer**: maneuver-based, infinite, varying, scored
for **speed not just gate-count**, trained in carry-forward batches.

This is a **unification**, not a new curriculum. The maneuver grammar already exists (built by
Clayton, Feb 11 2026, in `sim/infinite_gate_env.py` + `sim/sequence_generators.py` + Curriculum
V2) — but on the **PPO/SB3** stack (`drone_env_v2`, `train_infinite_v3.py`, VecNormalize). Phase 3
re-homes that grammar onto the **DreamerV3-from-pixels** pipeline validated in Phase 2.

## Three layers, by how much each must move

| Layer | What | Effort |
|---|---|---|
| **L1 — the grammar** | `ManeuverLibrary`, `SequencePlanner` (WORD→SENTENCE→PARAGRAPH→ESSAY), per-maneuver mastery EMA, Curriculum-V2 soft-boundary + hysteresis, metrics | **ports ~as-is** (architecture-agnostic) |
| **L2 — the env** | maneuver generator → anakin FPV env; **speed reward**; **takeoff**; batch-dim mastery | rewire onto `anakin/sim/env.py` |
| **L3 — the trainer** | batched-GPU vector-env (crux); carry-forward batch trainer | rebuild on DreamerV3 |

## Maneuver vocabulary (12)

`takeoff` (launch-only) + the 11 in-flight: `sprint, gentle_arc, hard_turn, hairpin, climb,
dive, chicane, speed_trap, spiral, threading, diagonal`. Ported verbatim into
`anakin/sim/maneuvers.py` (self-test passes).

- **takeoff is NEW as an explicit, tracked maneuver** (Clayton, Day 124). It was implicit in the
  old env (`ground_start_prob`); VQ1 starts from ground rest, so launch competence must be a
  first-class curriculum unit with its own metrics. `takeoff` is legal ONLY as the first segment
  from ground rest (`IN_FLIGHT` vs `LAUNCH` split; the random planner never samples it mid-course).
- **Extensible.** Other necessary maneuvers slot into the same `(pos, heading, alt, rng) ->
  (pos, heading, alt)` contract. Candidates if VQ1/VQ2 demand them: `brake_gate` (decel through a
  gate into a tight follow-up — partially covered by speed_trap→hairpin sequences), `descent_land`
  (only if a scored landing is required; not in a time-trial). Add when a track requirement names
  them, not speculatively.

## Speed — optimize for time, not just gates (Clayton, Day 124)

The old PPO env already did this; the new anakin env dropped it. Phase 3 **ports the speed terms
back** into `anakin/sim/env.py` reward (exact constants from `sim/infinite_gate_env.py::rc`):

```
gate_bonus      100.0
progress_scale    1.5
time_penalty      5.0   # * dt per step      — every step alive costs; punishes dawdling
speed_bonus_scale 0.15  # * dt per step      — rewards forward velocity along the racing line
gate_speed_scale  0.08  # gate_bonus * (1 + speed*this) — faster gate-crossing pays more
crash_penalty    15.0
```

Keep the current anakin shaping (progress toward gate, body-rate curriculum) and **add**
time_penalty + speed_bonus + velocity-scaled gate bonus. Net: the policy is pushed toward the
**minimum-time** racing line, the actual competition objective — not merely "pass the gate."
(Reward magnitudes will be re-tuned once it's in DreamerV3's symlog/return-normalized world; the
*shape* — reward speed, punish time — is the locked requirement.)

## Metrics — per-maneuver AND multi-maneuver, pass AND speed

Mastery/metrics track, per maneuver and per maneuver-sequence:
- **pass rate** (rolling window, asymmetric EMA: α_up 0.02 / α_down 0.005 — fast to credit, slow
  to forget, so brief dips don't collapse the curriculum)
- **speed** — mean crossing velocity and mean time-through, so "how *fast* is each maneuver now"
  is visible alongside "can it do it." This is what lets us watch the racer evolve, not just the
  pilot. (The old stack tracked pass-rate; adding the speed channel is part of the speed mandate.)

Curriculum escalation (Curriculum V2): soft tier-probability interpolation (no 80% cliff),
per-maneuver gating (a maneuver joins sequences only past ~0.82 mastery), and 8-pt hysteresis
between escalate/de-escalate thresholds.

## Crux — vector-env: approach **A** (batched-env shim)

Present the batched-GPU vector-env to DreamerV3's `simulate` as if it were N envs (the `sim/`
kernels already do 152k fps batched; the single-env wrapper just collapses to N=1). Stay on
upstream's tested training logic; **measure** where the bottleneck actually moves before
considering a custom loop (B). Chosen over B per Clayton's "go with whatever you think is best."

## Batching — carry the world model forward

DreamerV3 **is** the Messikommer decoupling: the world model learns the representation, the
actor-critic does policy search in latent imagination (zero env steps). So the carry-forward that
`sim/batched_train.py` did for PPO maps cleanly and *better*: run in fixed-size batches (fresh
process each, bounding memory accrual — the old run died ~7M steps), eval the batch's checkpoints,
and **carry the best world model forward** (the expensive, general physics+vision part) while the
policy keeps adapting as the curriculum escalates. Re-entrant via a JSON state file. VLM³
focal-normalization (canonical f) slots into the encoder for the sim→VQ1 camera-intrinsics gap.

## Compute

The 240 h figure (paper, RTX 8000) predates these levers: Messikommer representation/policy
decoupling (~28×, largely native to DreamerV3's imagination loop) + VLM³. Target a run that
finishes **overnight**, not a week. Don't fix model size / horizon / steps until the vector-env
is running and the throughput is read.

## Build order & status

1. **L1 port — maneuvers** ✅ `anakin/sim/maneuvers.py` (12 maneuvers incl. takeoff; self-test OK).
2. **L1 port — planner + mastery/metrics** ✅ `anakin/sim/sequences.py` (verbatim grammar) +
   `anakin/sim/curriculum.py` (`MasteryTracker` with pass AND **speed** channel, asymmetric EMA;
   `Curriculum` wrapper). takeoff tracked but excluded from the planner's sequence pool (launch-only).
   Self-tests OK. **Layer 1 complete.**
3. **L2 env — single-env racer** ✅ `anakin/sim/maneuver_env.py` (`AnakinManeuverEnv`): infinite
   curriculum gates + takeoff/ground-start + **speed reward** (progress + raw-speed bonus − time
   penalty + velocity-scaled gate bonus − crash) + per-maneuver pass/speed recording. Self-test OK
   on CUDA (ground-start targets takeoff; scripted climb lifts off 0.05→4.63 m; curriculum records).
   *Order refined: L2 before L3a — develop the racer on the single-env path, then batch a proven env.*
4. **L2 wire → Dreamer** — adapter + `anakin_maneuver` config branch pointing make_env at the
   maneuver env; short smoke to confirm it trains. *(next, small)*
5. **L3a — batched-GPU vector-env** ✅ `anakin/sim/vec_env.py` (`BatchedManeuverEnv`): N drones,
   one batched dynamics + one batched render per tick; shared `MasteryTracker` (batch-dim mastery)
   + per-env `SequencePlanner`s; fixed W=3 rolling gate window; internal auto-reset. **Benchmark:
   4.0k/15.5k/41.5k env-steps/s @ N=64/256/1024 — ~8000× the single-env run.** Worst-case
   (random-action reset churn dominates the Python path); real training keeps envs alive → climbs
   toward the 152k render ceiling. Bottleneck moved OFF the env onto GPU compute = goal met.
   *(next, when wiring training: if reset-bound, batch the reset/gate-gen path + keep crossing-math
   on GPU.)*
6. **L2 wire → Dreamer + L3b carry-forward trainer** — custom collection loop over the batched
   core (reusing Dreamer's cache/dataset/agent) + best-world-model-forward batches → scaling run.
