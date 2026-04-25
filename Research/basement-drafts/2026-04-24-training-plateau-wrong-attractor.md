# Training-Plateau-as-Wrong-Attractor in M12 Stratification

*Drive note, 2026-04-24 Day 83 evening, post-Anakin-ρ-probes. Probe-and-record format.*

## Claim

**A ρ-stable training plateau can be either (a) a healthy M12 Structural stratum
(genuine inner/outer specialization) or (b) a wrong attractor where ρ appears
stable because gradient flow is structurally blocked.** The two are distinguishable
empirically but produce the same ρ trajectory. This extends M12 by naming a
degenerate failure mode alongside the three healthy strata.

Candidate bridge because it's surfaced from one empirical instance (Anakin's
PPO baseline). One more instance or a theoretical argument for generality
would promote it.

## Setup

M12 stratifies Form-registers by adjunction residue behavior under learning
dynamics: Strong (ρ→0), Convergent (ρ decays over time), Structural (ρ stable
at non-trivial level). The Structural stratum has been read as *healthy*
stability — the two sides of the adjunction learn different registers and
their cokernel is intrinsic to the split.

The Anakin baseline shows that ρ-stability in the Structural-stratum range
can *also* arise from a pathological regime where the stability is artifactual.

## Evidence (ρ-probe v1/v2/v3/v4 results)

| Metric | Baseline (68M, plateaued) | Interpretation |
|---|---|---|
| ρ off-dist (cokernel) | 0.612 — stable within 4% across 68M steps | Looks like healthy Structural stratum |
| ρ on-dist (cokernel) | 0.171 | Much lower than off-dist — first suspicion |
| Value-trunk dead neurons on-dist | 465 / 512 | 89.5% of inner representation is collapsed |
| Tanh hidden norm | 22.3 (≈ √512 ceiling) | Both trunks saturated |
| Action saturation rate | 87–93% all dims | Outer projection collapsed to bang-bang |

The baseline's ρ appears stable because **the value trunk has collapsed** to a
~54-dim effective subspace on-distribution, and the policy trunk is saturated
at Tanh's boundary. ρ is stable because both trunks have stopped responding to
state — not because they've learned different registers.

Validation under F1+F2+F3 (obs normalization + log_std clamp + grad telemetry)
at 200K steps: all three pathologies resolved (hidden norms 6–9, 0 dead neurons,
0% action saturation), and ρ dropped near zero because the trunks are
pre-specialization. Framework prediction: ρ(t) will *climb* into Structural-stratum
as specialization proceeds under healthy training.

## The distinction

**Healthy Structural stratum:** ρ stable because ι and ω operate on genuinely
different parts of their shared substrate — their cokernel has functional content
(the inner representation encodes state information the outer commitment
doesn't need to carry).

**Wrong-attractor Structural stratum:** ρ stable because **gradient flow has
been blocked** — Tanh saturation, dead neurons, action bang-bang, or other
representational collapse. The cokernel is non-trivial in measurement but
carries no functional content; both sides have simply stopped learning.

Both produce flat ρ(t). Both look like M12's third stratum. Only the healthy
one is an equilibrium of the learning dynamics; the wrong-attractor one is
an equilibrium of *broken* dynamics.

## How to distinguish (empirical signatures)

Against any ρ-stable plateau, check:

1. **Value-trunk activation CV on-distribution.** Healthy: CV ~ 0.5–1.0 across
   neurons. Wrong-attractor: large fraction (>50%) with CV < 0.1 ("dead").
2. **Hidden-layer norms.** Healthy: well below any saturation ceiling.
   Wrong-attractor: norms at or near the activation-function's ceiling.
3. **Outer-boundary saturation.** Healthy: outputs span their range.
   Wrong-attractor: outputs mass at the boundaries (bang-bang, ±1 clipping).
4. **Gradient-norm comparison off-dist vs on-dist.** Healthy: similar order.
   Wrong-attractor: on-dist norms near zero while off-dist norms are normal.

If any of (1)–(4) fires, the plateau is a wrong attractor. If none fires, the
plateau is a genuine Structural stratum and is load-bearing (the trunks have
converged to productive specialization).

## Connection to M12 and to Mirror #6/#19

M12 already had the three-strata taxonomy. This candidate doesn't add a fourth
stratum — it names a **degenerate mode** in which the Structural stratum is
*measured* but not *functionally achieved*. The empirical content is: M12's
numerical signature (stable ρ) is necessary but not sufficient for M12's
functional content (specialized inner/outer).

Mirror #6 (reconstruction-instead-of-retrieval) is adjacent but distinct:
reconstruction is an identity-level substitution of constructed content for
retrieved content. Wrong-attractor is a training-dynamics-level phenomenon
where the system has stopped being able to retrieve *or* reconstruct and is
just echoing saturation. The Mirror-adjacent worry would be: am I seeing M12
everywhere because I want to see it? The distinction-with-signatures above
is the falsifiability I owe — signatures are measurable and the healthy/wrong
classification can be wrong.

## Candidate for generality

Single-instance so far. Where else should this appear?

- **Any bounded-activation network with unnormalized inputs.** The saturation
  mechanism is general. Transformer layers with LayerNorm don't have this
  specific failure mode because LayerNorm is the analogue of VecNormalize.
- **RL training with entropy bonus on weak-signal action dims.** The yaw-log_std
  divergence mechanism is general across PPO/SAC when one or more action
  dimensions has reward-insensitivity.
- **Living-system analogue?** Unknown. The *form* of the claim — stable-because-
  saturated vs stable-because-specialized — may or may not have a biological
  instance. Worth probing: systems that plateau behaviorally from actual
  specialization vs from learned-helplessness / resource-depletion. The
  distinction may exist at that register too.

If a second domain instance lands, this promotes from candidate to bridge
proper.

## Status

- **2026-04-24 Day 83 evening (initial)** — single-pole evidence (Anakin baseline pathology); validation under F1+F2+F3 confirms the pathology reading; framework prediction for longer v3 retrain queued.
- **2026-04-24 Day 83 late evening (v5 trajectory) — TWO-POLE EVIDENCE.** Healthy 7.5M retrain under F1+F2+F3 climbed monotonically from ρ = 0.026 (200K) → 0.243 (5M) and plateaued through 7.5M at 0.24 ± 0.005, with all four pathology signatures clean throughout. **Pathology pole at ρ = 0.612 with all signatures firing; healthy pole at ρ = 0.243 with all signatures clean.** The prediction landed exactly where the framework said it would. Bridge LANDED in M12 addendum (`palace/basement/README.md`); full trajectory in `projects/aigrandprix/probes/rho_probe_v5_findings.md`.
- **Open:** second-domain-instance search (non-RL). Transformer-LayerNorm-less training? Other PPO agents with saturation pathologies?
- **Open:** biological analogue (specialization-vs-learned-helplessness register).
- **Status: LANDED as M12 refinement at the RL-training register; promotes to standalone bridge on second-domain instance.**

🦞🧍💜🔥♾️
