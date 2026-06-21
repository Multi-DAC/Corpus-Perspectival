# dt-conditioning — spec for the next refinement (NOT in the scale-up run) — 2026-06-20 Day 140

## Why this is the principled upgrade over rate-randomization

The control-rate cliff (`CONTROL_RATE_FINDING_2026-06-17.md`) is currently handled by **rate-
RANDOMIZATION**: `ANAKIN_RATE_RANDOM=1` samples a per-env control dt ∈ [0.020, 0.040] each episode
(`sim/vec_env.py` `dt_vec`), so the policy learns to be *invariant* to the decision clock. This
WORKS — the rate-ft run took 30 Hz from DEAD→FLYING, and appearance-ft (which keeps rate-random)
passes the gate and flies.

But invariance is blind: the policy cannot *see* its clock, so it must average over all rates
rather than compensate for the one it is actually running at. **dt-CONDITIONING** supplies the dt
to the policy as an observation, so it can adapt its body-rate commands to the real control rate.
Strictly more information → cleaner transfer, especially at the edges (24/30 Hz) and for variable
real-hardware latency. This is the documented next piece of the scale-to-10+-gates recipe.

## Current state (the gap)

- `sim/vec_env.py` ALREADY computes the per-env dt (`dt_vec[i] = rng.uniform(dt_min, dt_max)` when
  rate-random is on) and applies it in `dynamics.step`. The quantity exists; it is just not exposed.
- The policy observation is **image-only**. The Dreamer encoder's MLP/vector path is empty for the
  racer (priv_state is decoder-only, not an encoder input). So there is no channel to feed dt in.

## The build (bounded; partial warm-start is the key move)

1. **Expose dt as a scalar obs.** In `sim/vec_env.py`, add an obs key — e.g.
   `obs["ctrl_dt"] = normalize(dt_vec)` with a fixed normalization (suggest `(dt - 0.020)/(0.040 -
   0.020)` → [0,1], or `1/dt` scaled; pick one and freeze it). Emit it on every step + reset, for
   all envs (constant per-env across an episode). Mirror in the single-env `maneuver_env.py` for
   parity with `integration/control_rate_rehearsal.py`.
2. **Wire it into the encoder.** In `third_party/dreamerv3-torch/networks.py` `MultiEncoder`, add
   `ctrl_dt` to the MLP (vector) keys so it joins the latent. (Optionally also a decoder head for an
   auxiliary reconstruction signal, like priv_state — not required.) Confirm the config's
   `encoder.mlp_keys` regex matches `ctrl_dt`.
3. **Partial warm-start (strict=False).** The obs-space change means the appearance-ft checkpoint's
   encoder gains a new input branch. Load shared weights (image encoder, RSSM, actor-critic, decoder)
   and randomly-init ONLY the new dt-MLP. `carry_forward_train.py` ALREADY does non-strict loads —
   this is exactly how the priv_state head was added (`[ANAKIN_PRIV] non-strict load`). Gate behind
   a new env-var `ANAKIN_DT_COND=1` so it is opt-in and the proven rate-random path is untouched.

## Validation (the instrument already exists)

Run `integration/control_rate_rehearsal.py` across rates (24/30/33/40/50 Hz) on the dt-conditioned
checkpoint, appearance held constant. **Expected:** the cliff flattens *further* than rate-random
alone — gate-count holds nearer the 50 Hz anchor across 30–40 Hz, because the policy now compensates
rather than averages. Compare head-to-head vs the rate-random-only baseline at each rate. If
dt-conditioning does NOT beat rate-random-only, it is a null result — keep rate-random and move on.

## Risk / scope

- Obs-space change touches the replay-buffer schema; a fresh logdir (not a resume of an old buffer)
  avoids schema-mismatch. Seed from appearance-ft/best.pt via the non-strict load.
- This is an **architecture change** → a dedicated session with the smoke+rehearsal loop above, NOT
  a same-night launch. The scale-up run (`launch_scaleup_ft.py`) deliberately does NOT include it:
  rate-randomization already flies, so dt-conditioning is a refinement, not a blocker.

## One-line summary

The dt is already computed per-env; the work is (a) emit it as an obs, (b) add it to the encoder
MLP keys, (c) non-strict warm-start (priv-head precedent), (d) validate with control_rate_rehearsal.
Opt-in via `ANAKIN_DT_COND=1`.
