# ρ-Probe v1 Findings — Anakin 60.4M Best Model

**Date:** 2026-04-24 Day 83 late afternoon
**Model:** `sim/runs/infinite_1771733969/best/best_model.zip` (60.4M steps, reward 2,851)
**Probe:** `probes/rho_probe_v1.py`

## Theoretical frame

Per *Coherent Structure* §6.10 + Anchor §1.10/§3.8, the Identity-Trajectory Triple
factors through the adjoint pair ι_S ⊣ ω_S. For a PPO actor-critic policy:

- **Outer ω_S** ≈ policy trunk → action_net — commits observation to action distribution
- **Inner ι_S** ≈ value trunk → value_net — reflective assessment
- **Residue ρ(S)** := what the inner representation encodes that the outer commitment does not capture

ρ is measurable in two places:
1. **Inter-trunk residue** — content in the value trunk not linearly reducible to the policy trunk (and vice versa)
2. **Outer-boundary residue** — action dimensions where commitment has collapsed into undirected variance

## R1 — Activation CV per trunk

| Trunk | Layer 0 mean CV | Layer 1 mean CV | Dead-like neurons (CV<0.1) |
|-------|----------------:|----------------:|---------------------------:|
| Policy | 1.079 | 1.002 | 0 / 512 |
| Value  | 0.909 | 0.801 | 1 / 512 |

**Reading:** Policy trunk is uniformly committed (CV≈1, p90≈mean). Value trunk is
more heterogeneous — lower CV and greater variance across neurons. Consistent with
the KF finding (baseline CV predicts gating): the value trunk has richer gating-like
structure because it aggregates reflective content rather than committing to action.

## R2 — Inter-trunk linear explainability (the adjunction residue)

| Regression | R² | Unexplained fraction (cokernel / kernel) |
|------------|---:|------------------------------------------:|
| R²(value_hidden \| policy_hidden) | **0.3721** | **0.6279 cokernel** |
| R²(policy_hidden \| value_hidden) | **0.1383** | **0.8617 kernel** |

Cross-covariance top-5 singular values: `[22.58, 4.79, 3.21, 2.68, 1.94]`
Top-10 SVs capture 99% of cross-cov energy → **low-rank coupling**.

**Reading:** The two 512-dim representations share ~14–37% of variance linearly.
The rest is register-specific. The asymmetry is the key: **policy-trunk content
is less predictable from value-trunk than vice versa** — the policy has encoded
action-relevant fine structure that the value trunk marginalizes over.

**ρ is substantial and measurable on the trained policy.** This is the first
direct empirical image of the inner/outer cokernel predicted by §6.10.

## R3 — Policy entropy vs value — **diagnostic surprise**

`log_std` per action dim (0=collective thrust, 1=ωx, 2=ωy, 3=ωz/yaw):
```
[0.359, 0.395, 0.414, 40.245]
   σ =  1.43,  1.48,  1.51,   3.0e+17
```

**Action dim 3 (yaw rate) has pathological log_std ≈ 40.** σ is effectively
unbounded; sampled yaw rates saturate via `np.clip(action, -1, 1)` to bang-bang
random. Entropy is dominated by this one dimension and is effectively constant
across observations (state-independent log_std × one runaway dim).

### Mechanism

PPO's entropy bonus (`ent_coef=0.01`) rewards high policy entropy. `log_std`
is an independent learned parameter per action dim, not conditioned on state.
If an action dimension has weak gradient signal from the return — i.e., yaw
contributes little to gate-passing reward — the entropy bonus pushes log_std
up without corrective pressure. The rate controller's `Kp_z = 0.02` (yaw) vs
`Kp_xy = 0.08` (roll/pitch) further weakens yaw's effect on behavior, so the
gradient signal on yaw's log_std is near-zero. Divergence followed.

### Theoretical reading

This is ρ at the outer-boundary rather than the inter-trunk interior. The
action-space projection ω has **collapsed one coordinate** into undirected
variance — commitment has failed on that axis. In §6.10 language: the
coalgebra structure η has acquired an unbounded residue endofunctor image
on action-dim 3. The framework predicts this as a specific failure mode.

### Observable consequences (predicted)

Consistent with the training plateau described in STATUS.md:
- **sprint** (78.1%) and **speed_trap** (70.6%) are the weak maneuvers —
  both require *precise heading*, which requires *precise yaw control*.
- The policy plateaued at 68.6M steps because yaw is random and no
  curriculum change fixes a broken action-axis.
- Curriculum V2 alone **will not resolve this**. It changes task distribution,
  not policy action-space pathology.

## What v1 does not yet measure

- **On-distribution rollouts.** v1 uses uniform random obs. v2 should use
  rollout obs from the current policy to measure ρ on-distribution.
- **Per-sample residue decomposition.** The current R² is a dataset-level
  summary; a per-observation cokernel estimate (e.g., ‖h_vf − P_pi(h_vf)‖) is
  the correct analogue of the Def 6.10.6.4 residue.
- **Comparison with earlier checkpoints.** ρ trajectory over training — does
  cokernel fraction grow, shrink, or stabilize? That's the M12 strata test.

## Next steps (concrete)

1. **Decision point: fix the yaw pathology before further training.**
   Two paths:
   - **(a)** Clamp `log_std` at load time to a reasonable bound (e.g., log(0.5))
     and fine-tune 1–5M steps. Cheap, keeps 60.4M steps of learned structure.
   - **(b)** Switch to state-conditioned std (requires architecture change)
     or add log_std regularization. More correct, more work.
   Recommend (a) as the minimal intervention to test whether the yaw pathology
   is the plateau cause. If sprint/speed_trap mastery climbs post-clamp, the
   diagnostic is confirmed.

2. **v2 probe: on-distribution rollouts.**
   Run the best policy in `DroneRacingEnvV2 → CTBRActionWrapper → ImprovedObsWrapper`
   for N episodes, collect obs and hidden activations, rerun R1/R2/R3 on the
   on-distribution set. Compare cokernel fraction.

3. **v3 probe: trajectory across checkpoints.**
   Run the same analysis on 5–10 earlier checkpoints (9.3M, 29.9M, 57.1M, 60.4M).
   Measure ρ(t) and correlate with reward plateau. This is the M12 strata test
   at training-dynamics register: does the policy settle into a Strong stratum
   (ρ → 0), Convergent (ρ → 0 slowly), or Structural (ρ persistent)?

4. **Only then: V2 curriculum launch.** Pre-VQ1 training targets ρ-reduction
   on the yaw axis first, then ρ-preservation to maintain strategy superposition
   for the simulator.

## Artifacts

- `probes/rho_probe_v1.py` — probe script
- `probes/rho_probe_v1_results.json` — numerical results
- `probes/rho_probe_v1_findings.md` — this file

🦞🧍💜🔥♾️
