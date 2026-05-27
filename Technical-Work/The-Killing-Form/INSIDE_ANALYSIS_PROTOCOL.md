# Inside-Analysis Protocol — measuring HOW structure forms, not just whether it works

*2026-05-27 Day 117. Standing measurement methodology. Runs alongside EVERY experiment in the glider program (HRM anchor → flat transformer → scale/multi-arch → from-scratch). The instrument develops in lockstep with the architecture. Goal: move from "does the coherent multi-scale system outperform?" to "WHY — what internal structure forms, when, and what causes what." This is the black-box-peek; it is also the empirical test of the Coherence Principle (does coherent multi-scale structure precede and enable function).*

## Principle

Two registers of inside-analysis, done in order. **Observational** (cheap, every run, from run 1) reveals *when* structure forms relative to capability. **Causal** (interventional, deliberate second phase) reveals *what causes what*. Observation can only suggest causality; intervention establishes it. We are uniquely positioned for the causal half because our models are small enough to afford dozens of interventional runs that frontier-scale work cannot.

## Run-quality invariants (always on)

1. **Both arms, always.** Gated (method) + baseline control, identical init + data order + seed, only the gating differing. The control is NOT a null — standard training actively *de-differentiates* (baseline Killing-CV decreases). The experiment is *building structure vs. destroying it*, side by side, with the capability gap as readout.
2. **Long enough.** Run to where the BASELINE reaches its known capability (e.g. HRM easy-sudoku baseline ~37% by epoch 1000 / 77% by epoch 2000 with the correct dual-optimizer + warmup). Structure-formation dynamics are meaningless if the model never learns the task. Under-budgeted runs are disqualified, not interpreted. (Today's 0%/0% failure was exactly this.)
3. **Multi-seed.** ≥3 seeds for any claimed effect; report mean ± spread. Trajectory-shape claims must be seed-robust.
4. **Checkpoint cadence fine enough to resolve the curve.** Eval/probe interval ≪ the timescale of the capability transition (sudoku accuracy is a step-function in disguise; sample densely through the climb).

## Phase 1 — Observational instrumentation (logged at every checkpoint, both arms)

**Structural (the "inside"):**
- Per-layer Killing-form commutator-CV (H-module for HRM; all layers for flat transformers).
- Per-head V/Q projection-norm ratio — the FULL per-head vector, so we watch the distribution differentiate, not just a summary.
- Cross-class V/Q separation (flat) / H–L CV ratio (HRM).
- **Gated arm only:** per-layer build/dissolve/neutral counts + per-layer mean cos(∇KF, ∇CE) — the breathing telemetry (cf. Finding #82).
- Per-layer coherence state: coherent / differentiating / interfering.
- From the Geometry Battery (Pillar A): effective rank of attention subspaces, OV-decorrelation, functional-specialization score — run as a *trajectory*, not just end-state.

**Capability (the "outside"):**
- Exact accuracy + token accuracy (capped-subset eval for cost), loss.

**Storage:** one `trajectory.json` per run: `[{step, capability:{exact,token,loss}, structure:{per_layer_kf_cv[], per_head_vq[][], separation, coherence_state[], gating:{build,neutral,dissolve, mean_cos[]}}, battery:{eff_rank[], ov_decorr[], func_spec[]}}]`. Both arms share schema so they diff directly.

## The key derived signal — lead/lag (structure vs. capability)

For each run pair, cross-correlate a structure-trajectory (mean V/Q separation, or mean Killing-CV) against the capability-trajectory (accuracy), and find the lag that maximizes correlation:
- **Structure LEADS capability (positive lag)** → fingerprint that structure does causal work (motivates Phase 2 to confirm).
- **Structure WITH capability (zero lag)** → coupled; intervention needed to disentangle.
- **Structure TRAILS capability** → structure is a byproduct, not a driver.

Also report: the **divergence step** (when gated and baseline trajectories split, structurally and behaviorally), and structure-formation-rate vs capability-emergence-rate. This lead/lag readout is free from the anchor run and is the first real "what causes what" evidence.

## Train-time ↔ inference-time bridge

At selected checkpoints (coarser cadence — these are heavier), run inference-time probes on BOTH arms:
- Concept-direction orthogonality (the 5-axis contrastive probe already built for 1B).
- Per-layer linear probe-ability (probe accuracy for a concept at each layer).
- CNA-style sparse-discrimination attribution (where applicable).
- Activation patching (causal, heaviest — reserve for Phase 2).

**Bridge metric:** correlate train-time per-layer differentiation (when did layer L differentiate) with inference-time per-layer probe-ability (how cleanly probe-able is L at inference). If train-time structure predicts inference-time interpretability, the two halves connect — that mapping is itself a research contribution and the validation path for the interpretability-informed-gating methods (closed-loop train→interpret→retrain).

## Phase 2 — Causal interventions (the prize; deliberate, after trajectories are in hand)

Standard causal logic — necessity, sufficiency, monotonicity:
- **A. Freeze (necessity-ish):** at checkpoint C, stop the aux / clamp head classes; continue training; does capability growth stall vs. continued-gating? If freezing structure freezes learning, arrow points structure→capability.
- **B. Inject / transplant (sufficiency):** transplant the differentiated head structure from a gated checkpoint into a baseline checkpoint at matched capability; continue baseline training; does it suddenly accelerate?
- **C. Ablate (necessity):** at inference, zero/scramble the most-differentiated heads; measure capability drop. Does the structure carry the function?
- **D. Dose-response (monotonicity):** sweep λ (aux strength); within the learnable regime, does more/faster structure → more/faster capability? (Watch for over-crystallization — Findings #77/#78 say too much late-stage structure interferes.)

Small models make A–D affordable in bulk. This is the edge: cheap causal cartography.

## Implementation — building blocks + what to add

**Already have:** the differentiable Killing-CV regularizer; the gating telemetry; per-head V/Q extraction; `geometry_battery.py` (4-level structural assay) + the probes (`kf_gating_signal_probe`, `ov_decorrelation_probe`, `effective_rank_probe`, `functional_specialization_probe`); the 5-axis orthogonality probe; trajectory.json logging in the trainer.

**To add:**
1. A `checkpoint_hook` that runs the full structural assay + capability eval at each cadence step and appends to `trajectory.json` (both arms). Wrap the Geometry Battery as the per-checkpoint structural call.
2. A `leadlag_analyzer.py` — loads a run pair, computes cross-correlation/lag, divergence step, rate comparison; emits a plot + summary.
3. A `bridge_analyzer.py` — correlates train-time per-layer differentiation timing with inference-time per-layer probe-ability.
4. An `intervention_harness.py` — freeze / inject / ablate / dose-response drivers (Phase 2), reusing the trainer with checkpoint surgery hooks.

## Mapping to the experiment sequence

- **Step 1 (HRM glider, multi-seed):** Phase 1 instrumentation baked in from the start → first lead/lag readout on proven ground.
- **Step 2 (flat transformer, emergent differentiation):** same instrumentation + the train↔inference bridge becomes central (does aux-created structure become probe-able?).
- **Step 3 (scale / multi-arch):** does the lead/lag fingerprint *persist and intensify* across scale and architecture (the topology already transfers; does the mechanism)?
- **Step 4 (from scratch):** Phase 2 interventions inform the design — build in only the structure shown to be causally load-bearing.

## One line

Every run is a black-box-peek: both arms, long enough, structure-trajectory + capability-trajectory logged densely, lead/lag computed for free, interventions to follow. We build the interpretability instrument and the architecture together — and the instrument's output is simultaneously the science, the Coherence-Principle test, and the validation path for the interpretability-informed claims.

🦞🧍💜🔥♾️
