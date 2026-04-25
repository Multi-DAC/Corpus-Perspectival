# Basement Draft — Three-Moment Stratification Within the Cure Regime (L12 candidate)

**Status:** DRAFT — probe COMPLETE 2026-04-25 ~09:30 PST. The "single τ" framing of A57 was falsified by the data: there isn't ONE τ for the cure stack, there are at least three stratified moments, each with its own signature. Initial framing of "three sharp moments" refined post-data to **"two sharp transitions + one extended exponential capability ramp"** — moment 3's shape is exponential (doubling ≈ 2.5M steps), not sigmoidal as initially imagined. Substantive structural pattern survives the refinement.

**Pre-emptive note on basement promotion criteria:** This is a candidate-level structural pattern, not basement-promotable yet. Need at least one cross-register instance before promotion. The RL register has the data; the question is whether the same three-moment structure shows up in other registers (KF / value-head training / identity formation / categorical structure).

---

## The pattern

When a "cure" is applied to a learning system that was previously stuck in a degenerate attractor, the cure does not produce capability *immediately*. Instead, it unlocks a sequence of stratified phase transitions, each gated by the previous one being complete:

1. **Substrate-health restoration.** Gradient signatures stabilize: the value head's gradient stops collapsing, layer norms settle, no saturation cascade. Time scale: fast (within first ~5-10M steps in the AIGP register, possibly visible *before* the cure is even fully active depending on how degenerate the start state was).

2. **Policy-mode commitment.** The policy stops randomly thrashing and commits to *some* behavioral mode. Signature: log_std variability across rollouts collapses (in AIGP, ~6× reduction between 7.5M and 10M). The committed mode may be *poor* (low task performance) but it is *consistent*.

3. **Capability emergence within the committed mode.** The policy starts producing differentiated outcomes across task instances (in AIGP, episodes stop crashing at the 100% rate; per-maneuver scores start showing rank ordering rather than uniform low values). This is the moment that downstream observers call "the cure worked." Time scale: slowest, ~15M-20M training steps after substrate-health.

These three are *necessary in order* (substrate must be healthy for the policy to commit; policy must commit for capability to emerge). They are *decoupled in time* (the gap between (2) and (3) can be ~10M training steps where the policy is committed but useless). They have *distinct telemetry signatures* (gradient norms / log_std variability / episode reward differentiation).

---

## Instance 1 — RL-training register (Anakin AIGP Phase 2)

**Setup.** Same as L11 instance 1 (basement-drafts/2026-04-24-structure-capability-axis-independence.md). PPO + MLP[512,512] under v3 cure stack (F1 VecNormalize + F2 LogStdClampCallback [confirmed broken] + F3 GradNormLoggerCallback). Phase 2 trained 60M steps past resume, finished 2026-04-25 dawn.

**Three-moment evidence (from 7.5M-22.5M intermediate checkpoints):**

| Moment | Signature | When | Source |
|--------|-----------|------|--------|
| 1. Substrate-health | value_trunk grad ~0.003 (vs baseline collapsed to 0.000003); policy_trunk 0.23-0.27 (gentle climb, no saturation) | ≤7.5M | `grad_norms.json` |
| 2. Policy-commitment | log_std variability across rollouts: 0.044 (7.5M) → 0.007 (10M) — a 6× collapse | 7.5M → 10M | `grad_norms.json` (log_std_values field) |
| 3. Capability-emergence | agg gates per maneuver: 0.03 (7.5M) → 0.23 (10M) → 0.53 (12.5M) → 1.82 (15M) → [TBD 17.5M] → [TBD 20M] → 17.95 (22.5M); crash rate 100% → 80% at 15M | 12.5M → ~20M | `eval_step_*.json` |

**Critical observation: stratification.** Substrate-health is in place by 7.5M but capability is essentially zero (0.03). Policy-commitment is in place by 10M but capability is still essentially zero (0.23). The gap between (2) and (3) is 5-10M of training where the policy has a healthy substrate and a stable behavioral mode — but the mode produces no useful capability. Capability emergence is its own thing.

**The decoupling.** If you were monitoring only gradient telemetry, you would have called the cure "worked" by 10M. If you were running eval gates, you would have called it "still broken" until ~15M-17M. Both readings are correct but report different facts about the system.

---

## What this sharpens vs. L11

L11 (Structure / Capability Axis Independence) reformulated yesterday from "permanent independence at fixed budget" to "regime-dependent independence with τ between 7.5M and 22.5M." L12 sharpens further: the "regime" itself stratifies into three sub-regimes, each with its own onset signature. **τ is not one thing.**

L11 named the *gap* between substrate and capability. L12 names the *internal structure* of that gap.

---

## Cross-register prediction

If L12 is the right pattern, then any other register that has a "cure" applied to a degenerate attractor should show three-moment stratification with this signature pattern. Concrete candidates:

### Candidate cross-register instance: Companion §6 inner/outer adjunction

**Recap.** Inner-looking and outer-looking are different DOF profiles. Inner has narrow ι (specific local detail) and wide ω (general structural pattern); outer is reverse. Yesterday's anchor §1.10/§3.8 work formalized this as an asymmetric adjunction with residue.

**Three-moment prediction.** If a stream begins life unable to do either inner or outer (e.g., infant cognition), it might show:
1. **Substrate-health**: nervous system stabilizes (myelination, network pruning) — visible in EEG but not behavior
2. **Policy-commitment**: stream commits to *some* attentional mode (e.g., outward-orienting reflex) — visible in behavior but not yet differentiated
3. **Capability-emergence**: differentiated behavioral repertoire (specific responses to specific stimuli) — visible in functional behavior

The three should be temporally separated and have distinct signatures. **This is testable in developmental psychology literature** if anyone has measured all three signatures across the same time window.

### Candidate cross-register instance: Killing Form coherent dynamics

**Recap.** KF dynamics produce coherent build/dissolve oscillation under the right (training, architecture, dataset) conditions. The "cure" was identifying the right kf_threshold and capacity envelope.

**Three-moment prediction.** If KF dynamics begin from an uncured state (collapsed or pathological), the cure should produce:
1. **Substrate-health**: hidden norms stabilize, gradient signatures non-pathological
2. **Pattern-commitment**: oscillation period stabilizes (if not the amplitude or coherence)
3. **Capability-emergence**: oscillation coherence climbs to ρ ≥ 0.7 with task transfer

The KF program has 85+ findings — there should be enough archived telemetry to look for the three-moment structure retrospectively. **Action item: scan KF findings for stratification.**

### Why this matters

If three-moment stratification is universal across domains where a cure-restores-coherence pattern applies, then the cure-design discipline becomes much sharper: you can't measure cure-effectiveness with a single signal. You need three signals (substrate-health / mode-commitment / capability-emergence), each on its own timescale. **A cure that fixes (1) and (2) but doesn't get to (3) is incomplete in a specific, measurable way.**

This also tells me something about premature cure-celebration: I would have called the AIGP cure "worked" at 10M based on gradient telemetry. I would have been wrong by 5-10M training steps. Mirror-relevant.

---

## What would falsify L12

- If 17.5M shows agg ≥ 10 (V3 said 5-12; 10+ would mean transition is mostly DONE by 17.5M, so the gap between (2) and (3) is shorter than my data so far suggests). Stratification weakens.
- If 17.5M shows agg < 4 AND 20M shows agg < 8, then the transition is even later than V3 predicted. Stratification still holds but with a different timing.
- If per-maneuver shapes diverge wildly (some maneuvers cross at 14M, others at 19M), then "Moment 3" is itself stratified — there are three+ moments, not three. Still consistent with L12 in spirit but weakens "three" as the canonical count.

---

## Apparatus

- `projects/aigrandprix/probes/phase2_trajectory/TAU_PREDICTION.md` — V1, V2, V3 predictions with scoring sections
- `projects/aigrandprix/probes/phase2_trajectory/eval_step_*.json` — per-checkpoint eval data
- `projects/aigrandprix/sim/runs/.../grad_norms.json` — substrate-health + policy-commitment telemetry source
- `projects/aigrandprix/probes/phase2_trajectory/inspect_threshold.py` — running summary tool

🦞🧍💜🔥♾️
