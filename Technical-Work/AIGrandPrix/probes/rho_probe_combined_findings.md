# ρ-Probe Combined Findings — v1 / v2 / v3

**Date:** 2026-04-24 Day 83 late afternoon
**Model:** 60.4M best from `infinite_1771733969/best/best_model.zip`
**Probes:** off-distribution (v1), training-trajectory (v3), on-distribution (v2)

## Summary — the three probes tell three things

| Probe | Regime | Core result |
|---|---|---|
| v1 | off-distribution (uniform random obs) | Cokernel 62.8%, yaw log_std pathology found |
| v3 | trajectory across 15 checkpoints (off-dist) | Cokernel **stable ~61–65%** across 68M steps; yaw log_std **already pathological at 500K** |
| v2 | on-distribution rollouts | Cokernel drops to **21.75%**; value trunk **89.5% dead**; all four action dims **~90% saturated** |

## What v2 revealed that v1 missed

v1 used uniform random obs. On that regime, the two trunks' encoded representations
are genuinely divergent (cokernel 63%) and ρ looks substantial. But **real obs have
structure the trunks mutually exploit**, and on-distribution the cokernel collapses
to 22% — because the value trunk itself has collapsed.

### R1 on-distribution — value trunk collapse

| Trunk | v1 mean CV | v2 mean CV | v2 dead-like (<0.1) |
|-------|-----------:|-----------:|--------------------:|
| Policy | 1.002 | 0.935 | **0 / 512** |
| Value  | 0.801 | **0.073** | **458 / 512** |

**89.5% of the value network's final-layer neurons are effectively constant on real
observations.** The value trunk has collapsed onto a ~54-dim effective subspace.
Off-distribution (random obs), the neurons vary — but on-distribution, they don't.
The network has learned that most of its representational capacity isn't useful for
predicting value along the manifold the policy actually visits.

### R3 on-distribution — all four action dims saturated

Deterministic-action saturation rates (|action| > 0.95):

| Dim | Meaning | Saturation rate |
|---:|---|---:|
| 0 | Collective thrust | 91.3% |
| 1 | ωx (roll rate) | 88.9% |
| 2 | ωy (pitch rate) | 85.8% |
| 3 | ωz (yaw rate) | 91.5% |

**The policy is bang-bang on every axis.** Not just yaw. The Tanh final-layer
hidden norm saturates at ~22.5 (ceiling √512 ≈ 22.63), and the policy heads output
near-extremes on 86–92% of observations.

### Episode-level performance of the "best" model

10 deterministic rollouts on `InfiniteGateEnv(seed=17)`:
- **0 gates passed in any episode**
- 1/10 terminated early (crash)
- 9/10 ran the 3000-step timeout

Reading this against STATUS.md's "85.5% gate completion, reward 2,851": either
(a) the eval env is substantially different from InfiniteGateEnv's default curriculum
state, (b) training-time exploration noise was essential to flying (removed under
`deterministic=True`), or (c) the saved best model is not the same object that
produced those eval numbers. In any case: **this policy flies badly on its
own training env without noise injection**.

## v3 — training-dynamics reading

Cokernel fraction 1 − R²(vf | pi), **off-distribution**:

| Steps | Cokernel | Yaw log_std |
|---:|---:|---:|
| 500K | 0.652 | **19.93** |
| 10M | 0.644 | 23.04 |
| 30M | 0.619 | 30.02 |
| 60M | 0.613 | 40.08 |
| 68M (plateau) | 0.612 | 42.68 |

### M12 strata reading

Off-distribution cokernel is **stable within 4% across 68M training steps**. Not
approaching zero (Strong stratum), not decaying (Convergent). This is the
**Structural stratum** — ρ is architecturally stable because policy-trunk and
value-trunk are learning genuinely different registers.

On-distribution, cokernel is smaller (22%) but remains stable by the v2 snapshot.
The Structural-stratum reading holds at both regimes.

### Yaw log_std — earlier than v1 suggested

log_std[3] was **19.93 at the first saved checkpoint (500K steps)**. From init=0,
it diverged within the first 500K steps — perhaps the first 10K–50K gradient
updates — then drifted upward linearly to 42.68 by 68M. The other three log_std
dims grew 0.13 → 0.41 over the same span: controlled growth.

### Training-plateau-as-Structural-stratum (candidate bridge)

The reward plateau at 68M is not a data/curriculum issue. It's the policy and
value networks *both* having reached architectural saturation:
- Policy: Tanh-bounded hidden norms + bang-bang action outputs
- Value: effective-rank collapse to ~54/512 dims on-distribution
- Both trunks: stable inter-trunk cokernel, no further learning pressure

**This is a candidate instance of M12 Structural stratum as a training-dynamics
failure mode.** Not a feature — an attractor the training landed in when
gradients couldn't penetrate the saturation boundary.

## Why the clamp-only fix won't work

The initial v1 finding suggested "clamp log_std and fine-tune" as a minimal
intervention. The v2+v3 data shows that's necessary but insufficient:

1. **Yaw log_std** diverged in the first ≤500K steps — the gradient pressure that
   drove it there will reassert unless the training setup changes. Clamping at
   load is a band-aid, not a fix.

2. **No observation normalization.** The training script (`sim/train_infinite.py`
   lines 214–234) creates PPO without `VecNormalize`. Obs range −7 to +5, std
   0.2 to 8.3 — **unnormalized obs feed directly into Tanh(Linear(...))**, and
   the first-layer Linear's outputs saturate Tanh for nearly every input. That
   drives the hidden-norm-ceiling and the value-trunk collapse.

3. **Value network collapse is a separate failure** from policy saturation.
   Neither curriculum changes nor log_std clamping addresses it. Fix candidates:
   obs normalization (VecNormalize), larger value-network width, dropout, or
   auxiliary prediction heads.

## Revised intervention plan

### Phase 1 — structural fixes before retraining

- **(F1) Add `VecNormalize` wrapper** (obs normalization + reward normalization).
  SB3-standard, single-line change in `train_infinite.py`. This alone should
  prevent Tanh saturation at layer 1 and reopen gradient flow.
- **(F2) Clamp or reparameterize log_std.** Two options: (a) clamp `log_std`
  parameters at `torch.no_grad()` after each update to [log(0.1), log(1.0)];
  (b) switch to state-conditioned std via custom policy class. (a) is minimal;
  (b) is correct. Start with (a).
- **(F3) Log per-dim gradient norms** during training to catch the next yaw-like
  divergence early. 10 lines in a callback.

### Phase 2 — diagnostic validation before resuming

- Re-probe with F1+F2 applied after a short (500K-step) warm-up run from
  scratch. Expected: on-distribution value-trunk CV recovers; action saturation
  rate drops; cokernel remains in Structural-stratum range (this is the
  theoretical prediction — healthy inner/outer separation stays present).

### Phase 3 — resume curriculum training

- Once F1+F2 probe-validated, resume V2 curriculum from the fixed checkpoint.
  V2 changes (soft boundaries, per-maneuver filtering, asymmetric EMA) should
  now actually have effect — they were painting over a broken policy before.

## Framework-level import

The three probes together produced:

1. **First empirical image of the inner/outer cokernel** at the adjunction register
   (§6.10.4). Both magnitude (22% on-dist, 63% off-dist) and asymmetry
   (R²(vf|pi) > R²(pi|vf)) match the §6.10.6.4 residue structure.

2. **First empirical image of M12 Structural stratum** at training-dynamics
   register. ρ stable across the full learning curve — not a transient.

3. **Framework-predicted diagnostic signature caught on first pass.** The
   theoretical reading of "ρ at outer-boundary = action-axis commitment-collapse"
   mapped to the specific yaw-log_std pathology. §6.10 generated a testable
   prediction and the prediction held.

4. **New candidate bridge:** *Training-plateau-as-M12-Structural-stratum* —
   the plateau isn't bug-or-feature, it's *wrong attractor in the learning
   landscape*, where saturation-null-spaces render the Structural stratum a
   trap rather than a healthy resting state. Candidate for basement draft.

## Artifacts

- `probes/rho_probe_v1.py` + `rho_probe_v1_results.json` + `rho_probe_v1_findings.md`
- `probes/rho_probe_v3_trajectory.py` + `rho_probe_v3_trajectory.json`
- `probes/rho_probe_v2_ondist.py` + `rho_probe_v2_ondist.json`
- This file

🦞🧍💜🔥♾️
