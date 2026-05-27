# Glider experiment v0.7a vs v0.7d — first real gradient-gating run (record, PENDING JOINT INTERPRETATION)

*2026-05-27 Day 117. First-ever run of the actual v0.7 gradient-gating design (`train_kf_v07_glider_gemma.py`, Claims 1-10) on Gemma-270M. Numbers gathered; interpretation + next-steps reserved for the Clayton+Clawd joint session. This is a RESULTS RECORD, not a conclusions doc.*

## Config
Gemma-3-270M, 1600 steps, seed 71, lr 2e-5, batch 4, seq 256. v0.7a: full gradient-gating, kf_lambda=5, kf_every=10, **gate_threshold=0.0**. v0.7d: ce_only control (pure CE). Final CE: v0.7a 0.117, v0.7d 0.095 (gating cost a little CE; small).

## Endpoint (Geometry Battery `coherence_placement`)
| | L1 ov-meancos | L2 readout-PR | L4 glider-r |
|---|---|---|---|
| pristine | 0.169 | 21.1 | −0.022 |
| v0.7d (CE-only) | 0.169 | 36.5 | +0.172 |
| v0.7a (full glider) | 0.169 | 35.3 | +0.135 |

- v0.7a L4 (0.135) **not above** the CE control (0.172); both far below the >0.5 "maintained-coherence" bar; both still effectively input-dependent.
- L1 identical across all (OV norm-invariant). L2 readout-PR: training raises it (~21→~36), glider not more than control.
- **Battery read: STATIC structure only; the glider did not beat the control on the trained-endpoint measure.**

## Trajectory (P2 — the glider-as-training-dynamic, from glider_log.csv, 160 gating steps)
- coherent mean **2.8**/18 (std 1.9, often 0) · differentiating **5.4** (std 2.1) · interfering **9.8** (std 2.2, dominant).
- B/D/N always X/Y/**0** — never any neutral.
- Pattern flickers (std ~2) but shows **no coherent propagating wave**; interfering-dominated.

## Observations (NOT conclusions — for joint interpretation)
1. **gate_threshold=0.0 eliminated the neutral zone entirely** (N always 0). The v07_design states the neutral zone is "the buffer space where the glider can oscillate without interference" and that "forcing all heads to agree" kills the glider. So this first config may be a *wrong-knob* negative (no buffer → interfering-dominated), NOT a *wrong-idea* negative. **Candidate next experiment: threshold>0 (e.g., 0.05-0.1) to create the neutral buffer.**
2. Consistent with A128 (per-layer cos structure is input/batch-dependent): the interfering-dominated flicker is what input-noise-driven gating would look like.
3. Both measures (endpoint battery + trajectory P2) point the same direction at this config: static/interfering, not maintained/coherent.

## Open questions for the joint session (do NOT resolve solo)
- Is the threshold=0 / no-neutral-zone the reason? (run threshold-sweep)
- Is the trained-endpoint input-stability (L4) even the right measure of a *training-time* dynamic? (the glider lives in the trajectory; maybe a trajectory-coherence metric, not endpoint-stability, is the right P2 test)
- Config space unexplored: kf_every, lambda, scale, longer training, larger model.
- n=1 seed.

## Prediction-stream (this drive)
- PREDICT verdict static (med-low) → CONFIRMED (L4 0.135 < control 0.172; static).
- PREDICT trajectory shows movement-but-unclear-if-coherent (med) → CONFIRMED (flicker, interfering-dominated, no wave).
- UNPREDICTED high-info discovery: threshold=0 killed the neutral buffer the design says sustains the glider → reframes the negative as wrong-knob, gives the clean next experiment.

**Status: provisional negative at this config; the threshold knob is the prime suspect. Interpretation + next-run decision reserved for Clayton+Clawd.**

🦞🧍💜🔥♾️
