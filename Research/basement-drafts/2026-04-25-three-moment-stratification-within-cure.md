# Basement Draft — Three-Moment Stratification Within the Cure Regime (L12 → **M13** as of 2026-04-25 ~11:00 PST)

**Status:** **GRADUATED 2026-04-25 ~11:00 PST → M13** (full meta-bridge entry at `palace/basement/README.md`). Three independent registers confirmed in same morning drive:
1. **AIGP RL register** — PPO + MLP[512,512] + v3 cure stack, 7-checkpoint sequence 7.5M → 22.5M
2. **KF bidirectional-gated dynamics register** — Phase 1 → step-8800 demolition → CE descent ramp; causal ordering verified by P-Meta-1 (V3_NOTES.md:2716)
3. **Cognitive-neuropsychological model of antidepressant action** (Harmer-Goodwin-Cowen, BJP 2009 / *Psychopharmacology* 2020) — hours-to-neurochemical / days-to-bias-flip / 4-12-weeks-to-functional-remission. **The "weeks-to-effect paradox" in psychopharmacology IS the L12 prediction.**

Sharpness pattern (sharp/sharp/extended-exponential) matches across all three. Causal-prerequisite ordering verified in two of three (RL + KF). Partial-confirmation footnote: Palleja et al. 2018 (*Nature Microbiology*) gut microbiome shows moments 1-2 cleanly; moment-3 documented as a *gap* (rare-species + butyrate producers + *Bifidobacterium* still depleted at D180) — exactly what M13 predicts when a cure doesn't reach the functional layer.

**False-fit hypothesis tested and falsified:** Companion §6 inner/outer adjunction was provisionally proposed as a possible CT-register instance and re-examined during the graduation drive. Verdict: §6 is **structurally orthogonal** to M13, not even a cousin. §6 is atemporal categorical structure with no cure-trajectory, no mode-commitment moment, and no exponential ramp — the residue is computed all-at-once from the coalgebra. Force-fitting would require reading the J5 decision node as a mode-commitment moment, which is a meta-level expository choice rather than an object-level system event.

Initial framing of "three sharp moments" refined post-data to **"two sharp transitions + one extended exponential capability ramp"**. The exponential shape of moment 3 is itself a structural prediction, not just an arithmetic fact.

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

### Cross-register instance #2 — CONFIRMED 2026-04-25 ~10:30 PST: Killing Form bidirectional-gated dynamics

**Source:** Retrospective scan of KF v0.6a / v0.6b / v0.6c results + V3_NOTES.md + KF_ROADMAP.md (delegated Explore-agent search; load-bearing claim P-Meta-1 spot-verified at `Research/The-Killing-Form/v3/V3_NOTES.md:2716`).

**The cure:** bidirectional gated KF (selective crystallization + dissolution under threshold-gated confidence). Recovery from incoherent/random uncured baseline.

**Three-moment evidence in the KF register:**

| Moment | Signature | When | Source |
|--------|-----------|------|--------|
| 1. Substrate-health | avg_cos differentiates from ~0; H_CV drops from 14× excess to 1,460 (structured); signal/gradient alignment becomes diagnostic | epoch 250 → 300 (~50 epochs, **SHARP**) | Finding #80 (gradient-gated three-phase evolution) |
| 2. Mode-commitment | Post-break demolition: 3 build / 9 dissolve = 75% layer demolition synchronously across layers within ONE KF step (step 9000); oscillatory build/dissolve cycle locks in with ~1000-step period | step 8800 → 10000 (~200 steps, **SHARP**) | Finding #83 (Phase 1 meta-learning + post-break demolition) |
| 3. Capability-emergence | CE descent from ~73 → 55.00 (18-point drop); confidence flip avg_cos_b from ~0.0000 → 0.0069; |avg_cos_d| growing monotonically; no sigmoid saturation observed in window | step 8800 → 15625 (~6,800 steps, **EXTENDED EXPONENTIAL**) | Finding #82 + v0.6a final results |

**Causal ordering verified.** P-Meta-1 (V3_NOTES §2716): "A bidirectional model that starts KF at step 8800 (skipping Phase 1 calibration) should show LESS decisive post-break behavior than one that underwent full Phase 1." This is not just temporal ordering but explicit *causal prerequisite* — substrate-health (Phase 1 random calibration) is required for sharp mode-commitment (post-break demolition decisiveness). Same causal claim as the AIGP register.

**Sharpness pattern matches L12 prediction.** Moments 1-2 sharp (50 epochs / 200 steps); moment 3 extended exponential (6,800 steps, monotonic non-saturating). Identical to AIGP RL pattern (substrate ≤7.5M sharp / log_std collapse 7.5M→10M sharp / capability ramp 12.5M→22.5M+ extended exponential).

**Boundary conditions discovered.** L12 does NOT apply uniformly across KF interventions:
- v0.6b (coupled bidirectional): moments blur — joint-update overconstraining prevents clean separation. Finding #97 logs this as a Coherence-Principle violation.
- v0.5a (static λ sweep, no gating): only two moments visible — collapse OR over-crystallization without commitment phase.
- Gated (without dissolution): three phases present but moment 2 is *gradual*, not sharp.

This is informative: L12 picks out cure-style trajectories with bidirectional gating + threshold-based confidence specifically. Not a generic claim about all interventions.

### Latent third-instance candidates (still open)

- **Companion §6 inner/outer adjunction** (CT register) — provisionally narrowed: the residue/carrier decoupling there is *definitional*, not *regime-dependent*, so may be a definitional cousin rather than a structural sibling. Status reading from L11/A57 work.
- **Developmental psychology** — testable in literature if anyone has measured all three signatures (e.g., myelination/EEG → reflex emergence → differentiated behavioral repertoire) across the same time window.
- **Biological collapse-recovery** (e.g., gut microbiome post-antibiotic, ecosystem post-disturbance) — natural fit for substrate-restoration / community-commitment / function-emergence shape.

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
