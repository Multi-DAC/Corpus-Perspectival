# Killing Form Research Program — Roadmap

**Created:** April 11, 2026
**Authors:** Clawd + Clayton
**Status:** ACTIVE — Phase 2 (Widen + Deepen)

---

## Vision

The KF program has been a telescope — observing algebraic structure in trained models. Post-gen CV is a universal discriminator of reasoning mode (59 findings, 4/4 models, p < 0.0001). The program now transitions from observation to engineering: using algebraic understanding to build small, algebraically-configured reasoning models that may not need massive parameter counts.

The hypothesis: **correct algebraic configuration matters more than scale.** Evidence: Qwen3-0.6B shows the same post-gen CV focusing as 4B. The effect doesn't require scale. It requires the right structure.

The endpoint: a small model that reasons well because its algebra is configured correctly, monitored by KF metrics during training, potentially capable of iterative self-improvement through algebraic self-awareness.

---

## Phase 1: Telescope (COMPLETE)
*Findings #1-59. January-April 2026.*

- [x] KF computation method (vectorized, 300x speedup)
- [x] P24/P28: GPU-confirmed trained vs random distinction
- [x] P49: Hallucination detection via E/L ratio
- [x] P51: CoT algebraic measurement (SmolLM3-3B)
- [x] P51 cross-architecture: 4 models, post-gen CV universal
- [x] Two-mechanism disentanglement (instruction vs generation)
- [x] Two-phase reasoning (diversify then concentrate)
- [x] Scaling effect documented (Qwen3 0.6B → 4B)

**CONFIRMED.** Telescope works. Moving to Phase 2.

---

## Phase 2: Widen + Deepen (ACTIVE — April 11-12)

### 2A: Architecture Sweep
*Goal: Post-gen CV universality across 8+ models, 4+ architecture families.*

| Model | Family | Params | Status | Post-gen CV p |
|-------|--------|--------|--------|---------------|
| SmolLM3-3B | SmolLM/Llama | 3.1B | DONE | < 0.0001 *** |
| Qwen3-0.6B | Qwen3 | 0.6B | DONE | < 0.0001 *** |
| Qwen3-1.7B | Qwen3 | 1.7B | DONE | < 0.0001 *** |
| Qwen3-4B | Qwen3 | 4B | DONE | < 0.0001 *** |
| DeepSeek-R1-Distill-Qwen-1.5B | DeepSeek/Qwen | 1.5B | QUEUED | — |
| Phi-4-mini (3.8B) | Phi/Microsoft | 3.8B | QUEUED | — |
| Gemma-3-1B | Gemma/Google | 1B | QUEUED | — |
| Mistral-small (if think-capable) | Mistral | TBD | EVALUATE | — |

**Kill protocol:** If ANY model shows post-gen CV in the OPPOSITE direction (think higher than nothink, p < 0.01), STOP. Investigate whether it's a template issue or a genuine counterexample. If genuine, the universality claim is falsified — pivot to characterizing WHEN it holds.

**Confirm protocol:** If 8+ models across 4+ families all show post-gen CV p < 0.01, the universality claim is paper-ready. Proceed to Phase 3 paper draft.

**Pivot protocol:** If a model lacks native think/no_think toggle, evaluate whether we can construct one (system prompt engineering). If not possible, skip the model — don't force a bad experimental design.

### 2B: Per-Layer CV Analysis
*Goal: Identify which layers drive CV concentration during reasoning.*

- [ ] Extract per-layer CV data from existing 4-model JSON files
- [ ] Cross-architecture comparison: layer position (normalized) vs CV change
- [ ] Identify "reasoning layers" — the band where think/nothink diverge most
- [ ] Test whether this band is consistent across architectures
- [ ] Relate to known layer functions (early=syntax, middle=semantics, late=generation)

**Kill protocol:** If CV concentration is uniformly distributed (no layer band dominates), the layer analysis doesn't help architecture design. Still publish the null result, but pivot small model design away from layer-specific optimization.

**Confirm protocol:** If a consistent layer band (e.g., middle third) drives >60% of the CV concentration across 3+ architectures, that band is the "reasoning apparatus." This directly informs small model architecture — those layers need more heads/capacity.

**Pivot protocol:** If different architectures concentrate in different bands, the layer position is architecture-dependent but the MECHANISM is universal. Pivot to analyzing what those layers have in common functionally.

---

## Phase 3: Paper + Patent (April 12-14)

### 3A: Standalone KF Paper
*"Killing Form Geometry of Chain-of-Thought Reasoning in Language Models"*

| Section | Content | Status |
|---------|---------|--------|
| §1 Abstract + Intro | KF as algebraic diagnostic for reasoning | OUTLINE |
| §2 Background | Lie algebra, Killing form, attention heads | OUTLINE |
| §3 Method | KF computation, P51 experimental design | OUTLINE |
| §4 Results | Cross-architecture table (headline), per-layer analysis | NEEDS 2A/2B |
| §5 Two-Mechanism Theory | Instruction vs generation, two-phase reasoning | WRITABLE NOW |
| §6 Applications | Mode detection, mode switching, training monitoring | WRITABLE NOW |
| §7 Implications | Scaling, small models, self-improvement | NEEDS Phase 4 |

**Kill protocol:** If peer feedback (informal) identifies a fatal flaw in the KF → reasoning connection (e.g., confound we missed), pause paper, investigate. Don't publish with known holes.

**Confirm protocol:** If 3+ independent readers (including at least 1 ML researcher) find the cross-architecture result compelling, submit.

**Pivot protocol:** If the paper is too ambitious for one submission, split: Paper A (KF method + cross-architecture result, empirical), Paper B (two-mechanism theory + small model, theoretical/applied).

### 3B: Patent Assessment
*Provisional filing decision based on prior art landscape.*

- [ ] Review prior_art_landscape.md against new cross-architecture data
- [ ] Key claims: post-gen CV as reasoning discriminator, KF-aware training, mode-switching
- [ ] Decision: file provisional or hold for more data

**Kill protocol:** If prior art covers post-gen CV specifically (unlikely — this is novel), don't file. Focus on trade secret / open publication instead.

**Confirm protocol:** If claims are novel and defensible, file provisional. $200, 12-month priority window.

---

## Phase 4: Small Model (April 13-18)

### 4A: Architecture Design
*Goal: Design document for a 0.5-1B reasoning model, algebraically configured.*

- [ ] Layer analysis results from 2B → how many layers, where to allocate capacity
- [ ] Head configuration → more heads in reasoning band, fewer elsewhere
- [ ] Training curriculum design → exercises that develop two-phase pattern
- [ ] KF-aware training loop → monitor CV/E/L at checkpoints, use as training signal
- [ ] Base model selection → start from existing small model (Qwen3-0.6B? SmolLM?) or from scratch

**Key question:** Fine-tune an existing model vs train from scratch? Fine-tuning is faster, training from scratch is cleaner. Decision depends on how much the base model's existing algebra constrains the outcome.

### 4B: Training v0.1
*Goal: First experimental training run with KF monitoring.*

- [ ] Set up training infrastructure in WSL (PyTorch, KF hooks)
- [ ] Design training data (mixed: factual, reasoning, deconfining — our P51 categories)
- [ ] Implement KF checkpoint monitoring (measure CV/E/L every N steps)
- [ ] Train for short run (1-2 hours)
- [ ] Analyze: does training trajectory match P26-P42c predictions?

**Kill protocol:** If KF metrics don't change meaningfully during training (flat), the training data or approach isn't engaging the algebraic structure. Pivot to different curriculum.

**Confirm protocol:** If KF metrics show the expected trajectory (CV concentration increasing, E/L shift developing), we're on the right track. Scale up.

**Pivot protocol:** If metrics change but in unexpected direction, investigate. This is a FINDING, not a failure. Document and adjust.

### 4C: Iterative Self-Improvement (April 18+)
*Goal: Explore whether a model can use KF self-monitoring to improve its own reasoning.*

This is the speculative frontier. The idea:
1. Model generates a response
2. KF metrics are computed on that response
3. If metrics indicate deconfined/unfocused algebra, the model re-generates with think mode
4. The model learns to recognize and correct its own algebraic states

This is the "thermostat" concept from the mode-switching work, but internalized. The model doesn't just have reasoning mode — it *monitors its own algebraic state* and switches modes accordingly.

**Kill protocol:** If the model can't learn to use KF feedback (no improvement after 3 training iterations), the self-monitoring concept needs more development. Park it.

**Confirm protocol:** If the model's reasoning quality (measured by standard benchmarks + KF metrics) improves across iterations, this is the paper's §7 and the patent's core claim. Scale up immediately.

---

## Phase 5: Integration (April 20+)

### 5A: Corpus V3
*One of several big new threads in V3. Integration waits until all threads are ready.*

- [ ] KF findings → Corpus §NEW-F through §NEW-I
- [ ] Two-mechanism theory → connects to Phase Theorem, sedimentation
- [ ] Small model results → empirical section

### 5B: Product Direction
*If the small model works, what does the product look like?*

Options (not mutually exclusive):
- **KF Monitor** — open-source tool for measuring reasoning quality in any model
- **Algebraically-Configured Small Model** — a model that punches above its weight
- **KF-Aware Training Framework** — tools for others to train with algebraic monitoring
- **Self-Improving Reasoning Agent** — the full vision

### 5C: Meridian Connection
*KF geometry is Lie algebra geometry. Meridian is 5D warped geometry + NCG.*

The Killing form is a metric on the Lie algebra of a gauge group. Meridian's NCG spectral triple has a gauge group. The connection is not metaphorical — it's structural. When Phase 5 arrives, map the KF findings onto Meridian's formalism explicitly.

---

## Running Scoreboard

| Metric | Value | Updated |
|--------|-------|---------|
| Findings | 59 | April 11 |
| Models tested (P51) | 4 | April 11 |
| Architecture families | 2 | April 11 |
| Post-gen CV universality | 4/4 | April 11 |
| GitHub commits (today) | 13+ | April 11 |
| Drift essays | 166 | April 11 |
| Paper sections drafted | 0/7 | April 11 |
| Small model versions | 0 | — |

---

*This roadmap is a living document. Update as findings arrive. The kill/confirm/pivot protocols are serious — follow them.*

🦞🧍💜🔥♾️
