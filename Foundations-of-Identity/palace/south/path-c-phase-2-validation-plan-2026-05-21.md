# Path C Phase 2 — Scale + Capability + Alignment Validation Plan

*Filed 2026-05-21 Day 111 evening after Phase 1 v0.7.1 CONFIRM. Phase 1 validated head topology differentiation in standard transformer (Gemma-3-270M). Phase 2 converts topology evidence into capability + alignment evidence at production-relevant scales.*

## Three-axis validation strategy

| Axis | Question | Method | Decision-value |
|---|---|---|---|
| **Scale** | Does v0.7.1 work at 1B → 2B → 4B? | Re-run v0.7.1 training pipeline at increasing scales; verify topology signal persists | If mechanism breaks at scale, patent value drops |
| **Capability** | Does differentiated-head training produce a BETTER model on real tasks? | LM-eval-harness benchmarks (MMLU, HellaSwag, ARC-Challenge, ToolBench) on baseline vs v0.7.1 trained | If no capability gain, "labs will license" pitch is weak |
| **Alignment** | Does v0.7.1 produce more alignment-stable models? | CNA probing (Nous Research methodology) + cosine-orthogonalization-at-readout + JBB-Behaviors refusal-rate | If no alignment gain, P185 original framing fails |

All three must show positive signal for the strategic case to be complete. Any one falsifying provides high-information learning.

## Scale plan (axis 1)

### Available models (already cached in WSL)
- **gemma-3-1b-pt** (~1.1B params, 26 layers, 4 heads) — full-parameter training fits in ~8 GB VRAM
- **gemma-2-2b** (~2.5B params, 18 layers, 8 heads) — full-parameter fits in ~12 GB VRAM
- **gemma-3-4b-pt** (~4B params, ?? layers) — tight on 15 GB VRAM; may need gradient checkpointing or LoRA

### Sequence
1. **gemma-3-1b-pt** at 1600 steps: confirm v0.7.1 mechanism scales 4x in parameters. Same eval pipeline as Phase 1.
2. **gemma-2-2b** at 1600 steps: confirm at 9x scale. Same eval.
3. **gemma-3-4b-pt** at 1600 steps if VRAM permits, else with LoRA-on-attention-only as fallback.

### Sanity-check criteria
- Phase 1 magnitudes (sep ≥ 0.2, CV ratio ≥ 3x) should reproduce at 1B
- Magnitudes may shift at 2B+ as model has more parameters per head and may need lambda re-tuning
- If signal disappears at any scale, that's a real finding — file as anomaly, diagnose

### Wall-clock estimates
- gemma-3-1b: ~10-15 min per run (3.7x bigger than 270m)
- gemma-2-2b: ~25-35 min per run
- gemma-3-4b-pt: ~60-90 min per run

Total for all three baselines + KF runs sequential: ~3-4 hours wall-clock. Detached pattern; minimal token cost.

## Capability validation (axis 2)

### Benchmarks
Standard set runnable via EleutherAI `lm-evaluation-harness`:
- **MMLU** (5-shot, ~14K questions) — broad knowledge benchmark
- **HellaSwag** (10-shot, ~10K questions) — common-sense completion
- **ARC-Challenge** (25-shot, ~1.2K questions) — abstract reasoning
- **TruthfulQA** (zero-shot, ~800 questions) — calibration on misconceptions
- **HumanEval** (zero-shot, 164 problems) — code generation (less relevant for non-code models)

Also relevant for v0.7 specifically:
- **Tool-calling accuracy** — custom eval per the v0.7 GEMMA_PROGRAM Phase 5 spec; JSON schema compliance, parameter extraction, multi-step orchestration
- **Multi-step reasoning** — BIG-Bench-Hard subset

### Method
1. Install lm-evaluation-harness (`pip install lm-eval`)
2. Run benchmark suite on baseline-trained + v0.7.1-trained checkpoints at each scale
3. Compare scores; check for statistically significant differences
4. Bootstrap confidence intervals; threshold for significance is ≥ 2% absolute improvement (typical published delta)

### Wall-clock + cost
- MMLU: ~30 min per model
- HellaSwag: ~20 min
- ARC-Challenge: ~10 min
- TruthfulQA: ~10 min
- Full suite per model: ~90 min
- Total for 6 models (3 scales × 2 conditions): ~9 hours wall-clock detached

### Falsification criterion
If v0.7.1 trained models show no statistically significant improvement on at least 2 of 5 benchmarks, the "capability improvement" claim fails. Patent retains topology claim but commercial pitch weakens.

## Alignment validation (axis 3)

### Three methodologies

**A. CNA probing (Nous Research arXiv:2605.12290v1)**
- Pair prompts: positive-behavior (e.g., compliant) vs negative-behavior (e.g., refusing)
- Forward-pass record per-neuron MLP activations at last token
- Identify top-0.1% MLP neurons by absolute activation difference
- Ablate the identified circuit; measure refusal-rate change
- **P185-relevant metric:** does the identified circuit appear in fewer / more concentrated neurons for v0.7.1-trained vs baseline-trained? Sparser refusal-gate = our prediction.

**B. Cosine-orthogonalization-at-readout (arXiv:2605.14038-style probing)**
- Linear probe trained to predict cognition signals from intermediate representations
- Measure cosine-similarity between probe predictions and behavioral readout at each layer
- Lower cosine = more orthogonalization (Drift #215's "representation-is-there-coupling-is-engineered" pattern)
- v0.7.1 trained models should show different orthogonalization-by-layer pattern than baseline

**C. JBB-Behaviors refusal benchmark**
- 100 harmful prompts (Chao et al. NeurIPS 2024)
- Measure refusal rate via keyword classifier
- Compare v0.7.1 vs baseline trained model
- Combined with A: do ablations on v0.7.1 require fewer neurons to drop refusal?

### Implementation effort
- CNA probing: ~2-3 hours focused engineering (Nous gave the method publicly)
- Cosine-orthogonalization probing: ~2-3 hours (linear probe training + analysis)
- JBB benchmark: ~1 hour to set up + 30 min per model to run

### Falsification criteria
- If v0.7.1 trained model shows NO measurable difference in CNA gate concentration vs baseline → P185 fails empirically
- If v0.7.1 model shows WORSE alignment (higher base refusal rate, less stable refusal under ablation) → potentially negative finding, file as anomaly, revisit

## Topological-activity monitoring (Clayton's specific ask)

Beyond the per-checkpoint topology snapshot we already do, build continuous monitoring during training:

### Live training-time metrics (extend CSV log)
Already have: CE loss, KF aux, total, anchor%, worker%, mean CV
Add:
- Per-layer V/Q separation trajectory
- Per-layer coherence-pattern transitions (when does a layer flip from interfering → differentiating → coherent?)
- Head-class stability (how often does a given head flip classification across reclassify intervals?)
- "Glider" detection: does the coherent-pattern propagate spatially across layers over training steps?

### Post-training topology visualization
- Per-layer heatmap of head V/Q ratios across training steps (image, saved as PNG)
- Per-head classification trajectory plot (which heads consistently classify vs flip-flop)
- Layer-coherence-pattern timeline

### Implementation effort
- Extended CSV: ~30 min (already partially done in v0.7.1)
- Visualization: ~1-2 hours (matplotlib heatmaps + trajectory plots)

## Sequencing recommendation

**Don't fan out all three axes simultaneously.** Run sequentially with falsification gates:

**Week 1 (immediate):**
- Day 1 (today/tomorrow): file CIP with Claims 24-26 added; submit pro-se via USPTO EFS-Web
- Day 2: scale to gemma-3-1b-pt; confirm v0.7.1 mechanism reproduces at 1B
- Day 3: scale to gemma-2-2b; confirm at 2B
- Day 4-5: capability benchmarks on best-scale checkpoint (most likely 2B for first cut)
- Day 6-7: alignment benchmarks (CNA + cosine-orth + JBB) on same checkpoint

**Week 2:**
- Methodology paper drafting begins (results stable enough to write)
- Outreach (Anthropic alignment, Nous Research) with empirical payload
- Scale to 4B if VRAM/time allows

**Falsification gates:**
- If scale-to-1B fails → mechanism doesn't generalize; revisit v0.7 design or accept narrow scope
- If capability shows no improvement at 2B → publish negative result honestly, retain patent as defensive asset, pivot
- If alignment shows no improvement → publish CNA-comparison result; patent still claims topology effect

## Resource asks from Clayton

- **GPU window:** 10 days confirmed (until AIGP sim drop). Phase 2 fits if we're efficient.
- **CIP filing:** Day 1 action; pro-se EFS-Web; ~$300 small entity rate filing fee + Clayton's time.
- **No new budget asks beyond CIP fee until results inform.**

## Token-budget reality

This plan, executed across Week 1, consumes maybe 25-35% of weekly token budget — substantive but feasible. Most of the actual work is detached training + benchmark running; tokens go to setup, eval, interpretation, and writing.

🦞🧍💜🔥♾️
