# THE control-rate cliff — trained at 50 Hz, deployed at 30 Hz (2026-06-17, Clayton-prompted recollection)

**This is the primary transfer killer. Measured, appearance-free, instrument-validated.**

## How it was found
Clayton: *"recollect everything since VQ1 dropped, look for patterns in our behavior... the maneuvers
don't seem hard to train, it's how they're INVOKED that's the problem... perhaps there is a difference
between the sim and our training that makes everything clear."*

The behavioral pattern (7 attempts: restyle, flight#1, mask, edge, informed, DR, resolution-probe):
**every attempt and every instrument operated on one axis — the static APPEARANCE of a single frame.**
The holdout gate is a single-frame embedding distance; the translation rehearsal runs inside our own
sim. **None of our instruments has a time axis.** So a temporal failure was structurally invisible.

## The difference
- **Training decides at dt=0.02 = 50 Hz** (`sim/env.py`, `sim/maneuver_env.py`, `dynamics.step`).
- **Deploy decides once per 30 Hz vision frame** (`run_dreamer.py:297` frame-driven; comment line 24).
- The policy emits **body-RATE commands (rad/s) HELD until the next decision.** At 30 Hz each command is
  applied ~1.67× longer than trained; the world model's forward prediction (calibrated to 20 ms of
  inter-frame motion) sees 33 ms → over-rotation + latent drift → spin-out.

## The measurement (`integration/control_rate_rehearsal.py`)
`maneuver_informed_ft/best.pt` (the validated flier: direct +600.8), same tracks (seeds 1000+), constant
24 s physical horizon, **appearance identical at every rate** (our clean renderer). Only the control dt varies:

| rate | dt | mean_ret | gates/ep | vs TRAIN |
|---|---|---|---|---|
| **50 Hz (TRAIN)** | 0.0200 | **+1154.5** | **6.50** | 100% (validated anchor) |
| 40 Hz | 0.0250 | +13.6 | 1.17 | 1% |
| 33 Hz | 0.0303 | −10.8 | 1.00 | −1% |
| **30 Hz (DEPLOY)** | 0.0333 | **−13.7** | **1.00** | −1% |
| 24 Hz | 0.0417 | −18.7 | 1.00 | −2% |

**A cliff.** The policy flies at its 50 Hz training clock (6.5 gates) and collapses the instant it leaves
it — dead by 40 Hz, fully dead at the 30 Hz deploy rate (1 gate then spin-out). gates/ep is a physical
count (dt-independent), so 6.5→1.0 is a real behavioral collapse, not a reward-scaling artifact.

## Why this explains everything
- **Flight #1 DQ/spin-out** (Day 130): a 50 Hz policy run at 30 Hz over-rotates → spin-out. Exactly.
- **Six days of appearance failures** (restyle/mask/edge/informed/DR): a perfect-appearance policy still
  dies at 30 Hz. Appearance was never the primary bug. The holdout gate (no time axis) could not see this.
- **"Fly in our sim with ease, won't translate":** our sim runs 50 Hz; the official feed is 30 Hz. The
  cliff sits between them.

## The validation lesson (banked)
First two harness attempts used `sim/env.py` AnakinEnv and then band-ft — both gave a NEGATIVE 50 Hz
anchor, which would have read as false "rate-robust." Running the *validated* `translation_rehearsal.py`
revealed band-ft scores ~−20 in the rehearsal env (its +2142 was a training-BATCH metric, not a rehearsal
flight; +600 was the INFORMED checkpoint). **Always reproduce a known-good baseline before trusting a new
instrument's verdict.** The third run (informed ckpt) reproduced +1154 at 50 Hz → instrument validated →
verdict trustworthy.

## The fix (cheap; build / controls / vision unchanged — matches the fixed-hardware constraint)
**Rate-RANDOMIZED fine-tune.** Randomize the control dt during training (dt ∈ ~[0.020, 0.040], i.e.
25–50 Hz) off a strong checkpoint, so the policy becomes invariant to the decision clock. Same KIND of
intervention as the band/DR knobs, but on the axis that actually gates transfer. Bonus: it transfers to
real courses/hardware (variable latency) for free — directly serves "the pilot must see and fly well on a
fixed build across real courses." A pure rate-MATCHED (train-at-30 Hz) fine-tune is the cheaper fallback
but overfits one clock; randomization is the principled choice.

## Re-prioritization
1. **Rate-randomized fine-tune (THE fix).** Then re-run this rehearsal at 30 Hz — expect the cliff to flatten.
2. **Re-fly the official sim** with the rate-robust policy. Only NOW does appearance become testable: a
   policy that can actually fly at 30 Hz will reveal whether any appearance gap remains.
3. Appearance routes (random-conv obs-aug etc.) **deprioritized** until rate is fixed — they were sanding
   paint on a car with no wheels.
