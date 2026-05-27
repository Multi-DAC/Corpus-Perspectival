# The Model Geometry Battery — a standardized multi-level assessment of model coherence

*Design doc, 2026-05-27 Day 117 morning (Do Be Talk Be Do drive). Consolidates the eight probes built/used during the Day 116→117 KF mechanism hunt into a principled methodology — the seed of Pillar A (standardized model-geometry assessment) from `STRATEGY_post-mechanism-hunt-2026-05-26.md`.*

## Purpose

A standardized battery for measuring the **geometry and coherence of a transformer model's internal structure**, across multiple levels, with a common interface and a structured report. Built from validated probes, model-general where possible.

**Why it matters independent of every other KF claim:** even if the orthogonality effect is a ghost and the glider never flies, *"here is a disciplined, multi-level methodology for assessing where a model's coherence lives"* is a legitimate, broadly-useful, plausibly-valuable contribution on its own. It is the robust floor deliverable. Everything riskier (the v0.7 architecture, the coherence-benefit) rides on top of it.

## The organizing principle (the conceptual spine — and the morning's discovery)

The eight probes are NOT an arbitrary metric grab-bag. Sorted by *what kind of structure they read*, they fall on a single axis — **static → dynamic** — which is exactly the axis that the Day-116→117 dream-drive crux turns on:

> *induced-static-structure* (universal in ML — every trained net has it) **vs** *maintained-dynamic-coherence* (the Coherence Principle's actual claim — rare).

So the battery measures coherence across the static→dynamic spectrum, and tells you **where on that spectrum a given model's coherence lives.** The levels:

| Level | Reads | Static↔Dynamic | Bears on |
|---|---|---|---|
| **L1 — Weight geometry** | weights alone (no forward pass) | most static | induced structure (what training *left in the weights*) |
| **L2 — Activation geometry** | activations over a probe set (forward pass) | static-ish (a snapshot) | how the induced structure *represents* concepts |
| **L3 — Attention-algebra** | attention matrices (forward pass, eager) | snapshot of the live computation | coherence of the head Lie-algebra *during inference* |
| **L4 — Gradient dynamics** | gradients (forward + backward) | most dynamic | the *coherence-in-motion* signal — the build/dissolve dialogue |

**The spine's payoff:** L1–L3 measure (mostly) induced structure; **L4 is the only level that touches *maintained dynamic coherence*** — the Principle's actual claim. This is why the battery isn't just diagnostics: it locates a model on the static→dynamic axis, and L4 is the level where the genuinely-novel (Principle-instance) phenomenon would show up. The toolkit's structure *encodes the crux it was built to investigate.*

## The levels and their probes

### L1 — Weight geometry (static; weights only)
- **Head-class topology** (`eval_v07_1_generic.py`) — per-head V/Q-norm separation between anchor/worker classes vs a pristine reference. *Measures: induced head differentiation.* (KF v0.7.1's robust signature: 2.89x at Gemma-270M, near-deterministic.)
- **OV write-decorrelation** (`ov_decorrelation_probe.py`) — mean pairwise |cos| of per-head OV write-operators (W_O·W_V). *Measures: head write-direction redundancy.* (Norm-invariant by construction → blind to norm-only changes; documented limitation.)

### L2 — Activation geometry (snapshot; forward pass over a fixed probe set)
- **Concept-orthogonality** (`cosine_orthogonality_probing.py`) — orthogonality of concept-direction representations at readout, across N conceptual axes. *Measures: concept separability / steerability.*
- **Effective rank** (`effective_rank_probe.py`) — participation ratio of per-layer activation covariance. *Measures: representational dimensionality / collapse* (note: middle layers rank-collapse to ~1 via the massive-activation artifact; the readout layer is the informative one).
- **Functional specialization** (`functional_specialization_probe.py`) — cross-class vs within-class similarity of per-head mean residual *writes* (activation-based). *Measures: whether head-classes do functionally distinct things* (distinct from L1's norm-separation — and A127 shows they can diverge).

### L3 — Attention-algebra (snapshot; eager attention required)
- **Killing-form commutator-CV** (`kf_regularizer_gemma.py`) — per-layer commutator variance of attention matrices (the KF metric proper, differentiable torch port of `kf_monitor.compute_layer_kf`). *Measures: attention-head Lie-algebra coherence* (the mode-detection signal: factual / hypothesis / deconfined). **Interface wrinkle: requires `attn_implementation="eager"`** — the others don't.

### L4 — Gradient dynamics (most dynamic; forward + backward)
- **Gating signal** (`kf_gating_signal_probe.py`) — per-head cos(∇KF, ∇CE) distribution (build/dissolve/neutral split). *Measures: the gradient-alignment structure the v0.7 gating acts on.*
- **Glider stability** (`kf_glider_stability_probe.py`) — cross-input correlation of the per-layer gating pattern. *Measures: whether the gradient-dynamics structure is input-stable (a property) or input-dependent (a dynamic).* **This is the probe closest to the Principle's claim** — it asks whether coherence is *maintained* or merely *momentary*.

## Common interface

Every probe resolves to: **`(model_id, optional ckpt) → JSON report fragment`**. The unified runner `geometry_battery.py` loads the model once and dispatches all applicable probes, emitting one combined `model_geometry_report.json`.

**The eager-attention wrinkle (predicted, confirmed in design):** L3 (and L4, which uses the KF regularizer) need `attn_implementation="eager"`; L1/L2 don't care. Clean resolution: the runner loads with eager always (eager is a strict superset — it can do everything SDPA can, just slower and with attentions exposed). Cost: eager forward is slower; for an assessment battery (not training), acceptable. So the wrinkle resolves by *defaulting the whole battery to eager* rather than per-probe branching. (Prediction was right that eager is the wrinkle; the resolution is "make it the default," not "special-case it.")

## The Model Geometry Report

A run produces a structured report with, per level, the probe outputs plus a one-line **interpretation** and a **static↔dynamic placement**. Top-level summary fields:
- `model_id`, `ckpt`, `reference` (pristine or named baseline)
- `L1_weight`: {head_class_separation_ratio, ov_write_meancos}
- `L2_activation`: {concept_orthogonality_score, readout_effective_rank, functional_class_sep}
- `L3_attention_algebra`: {mean_commutator_cv, per_layer_cv}
- `L4_gradient_dynamics`: {gating_build_dissolve_split, glider_cross_input_r}
- `coherence_placement`: a one-line read of *where on the static→dynamic spectrum this model's coherence lives* (e.g., "strong induced static structure [L1 2.9x], weak dynamic coherence [L4 r≈0]" — the current v0.7.1 signature).

## Honest scope

- **Validated on:** Gemma-3 (270M, 1B) + Qwen2.5-0.5B (L1/L2 cross-arch). All probes ran clean on Gemma-270M during the Day-116→117 work.
- **Model-general (drop-in via `--model_id`):** L1 head-topology, L2 orthogonality/effective-rank, all assume `model.model.layers[L].self_attn.{q,v,o}_proj` + `output_hidden_states`. Works for Llama/Qwen/Mistral/Gemma; needs adaptation for fused-QKV (GPT-NeoX/Bloom) and decoder-path (OPT) families.
- **L3/L4 require eager attention** + per-head q-proj gradient access; same family caveats.
- **Known probe limitations (documented, not hidden):** OV-decorrelation is norm-invariant (blind to the norm changes the KF aux makes); middle-layer effective-rank is artifact-collapsed (use readout layer); functional-specialization is sparse at low head-count (Gemma's 4 heads/layer → pooled across layers).

## Connection to strategy

This IS Pillar A. The **static→dynamic spine is the publishable conceptual contribution** — not "here are eight metrics" but "here is a principled axis for locating a model's coherence, and a battery that measures along it." A methods paper writes itself from this doc + the validated probes + a few cross-model reports. And it's the floor that holds regardless of whether the v0.7 glider (the L4 / dynamic-coherence frontier) ever flies. It also directly serves Wednesday: the v0.7 runs' outcomes get measured *by this battery*, and the report's `coherence_placement` field is exactly the read that tells us whether v0.7 moved a model from static-structure toward dynamic-coherence.

## Build status
- Design: this doc (2026-05-27 morning).
- Probes: all eight exist + validated individually.
- Unified runner `geometry_battery.py`: in progress this drive.
