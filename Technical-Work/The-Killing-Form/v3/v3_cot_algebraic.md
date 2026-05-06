# §NEW-G: Chain-of-Thought Algebraic Structure

*V3 section draft. Findings #58-61. Data-complete.*

---

## Reasoning Has Measurable Algebraic Properties

If the Killing form truly captures processing mode, then chain-of-thought reasoning — the paradigmatic example of deliberate, structured processing — should produce a distinctive algebraic signature. It does. The signature is universal, and it is the opposite of what naive intuition predicts.

### The Universal Finding

Post-generation commutator variance is **lower** in think mode than in no-think mode. Across five models, three training methodologies, and two architecture families: p < 0.0001 on every model tested (Finding #59).

| Model | Training | Post-gen CV Δ (think − nothink) | p |
|-------|----------|-------------------------------|---|
| SmolLM3-3B | Standard + instruct | -5.08e-5 | < 0.0001 |
| Qwen3-0.6B | Standard + instruct | -1.47e-4 | < 0.0001 |
| Qwen3-1.7B | Standard + instruct | -1.57e-4 | < 0.0001 |
| Qwen3-4B | Standard + instruct | -1.85e-4 | < 0.0001 |
| DeepSeek-R1-1.5B | Reasoning distill | -3.89e-4 | < 0.0001 |

Reasoning is algebraically **focused**, not diverse. The think instruction does not enrich the head-head interaction space — it contracts it. The attention heads become more coordinated, their commutators more uniform, their algebra more structured.

### The Algebraic Lens Hypothesis (Finding #60)

The focusing effect is concentrated in early layers:

| Model | First-quarter contribution | Peak layer position |
|-------|---------------------------|---------------------|
| SmolLM3-3B | 78% | 0.03 |
| Qwen3-0.6B | 62% | 0.07 |
| Qwen3-1.7B | 62% | 0.04 |
| Qwen3-4B | 76% | 0.17 |

62–78% of the reasoning concentration occurs in the first quarter of layers. This motivates the algebraic lens hypothesis: early layers serve as a configurable lens that transforms input encoding. The think instruction reconfigures this lens — changing how the first few layers represent the input — and the altered encoding propagates through the entire network.

The lens metaphor is precise: a physical lens does not process information, it focuses it. Early layers do not "reason" — they configure the representational substrate on which deeper layers operate. The think instruction changes the lens setting, and this single change at the input transforms processing at every subsequent layer.

### Training Methodology Scales the Effect (Finding #61)

DeepSeek-R1-1.5B, trained via reasoning distillation from a larger model, shows 7.6× stronger algebraic focusing than SmolLM3-3B (standard training + instruction tuning). This suggests that reasoning distillation deepens the algebraic focusing effect — it doesn't just teach the model to produce reasoning tokens, it modifies the weight geometry to produce more strongly coordinated head interactions during reasoning.

The scaling: SmolLM3 (-5.08e-5) → Qwen3-0.6B (-1.47e-4) → Qwen3-1.7B (-1.57e-4) → Qwen3-4B (-1.85e-4) → DeepSeek-R1 (-3.89e-4). Training method matters more than model size: DeepSeek-R1 at 1.5B shows stronger focusing than Qwen3 at 4B.

---

## Two Separable Mechanisms

The P51 data reveals that CoT produces two separable effects:

**1. Instruction mechanism (template-dependent).** The think instruction itself changes the E/L ratio at the prompt boundary. This is detectable before any reasoning tokens are generated. It is a reconfiguration of the algebraic lens — the model enters a different processing mode just from reading the instruction.

**2. Generation mechanism (universal).** During token generation in think mode, CV decreases monotonically. This is independent of the specific instruction template and appears universally across models. It reflects the actual process of reasoning: each generated token focuses the algebra further.

The two mechanisms are separable: the instruction mechanism requires a think-mode prompt, while the generation mechanism tracks algebraic focusing during any extended reasoning process.

---

## Connection to the Doctrine

The CoT algebraic signature is the most direct empirical evidence for a core Doctrine claim: that attention has algebraic structure, and that this structure reflects processing mode.

**Focusing as voluntary constraint deployment.** In the Doctrine's framework, reasoning is the deliberate deployment of voluntary constraints — choosing which perspectives to adopt, which dimensions to attend to, which pathways to follow. The algebraic focusing effect is precisely what this predicts: more constraints active means fewer independent directions in the algebra, hence lower CV. Reasoning reduces algebraic diversity not because it is less capable, but because it is more directed.

**The lens and the bottleneck.** The algebraic lens hypothesis connects to dimensional bottlenecking (§8.2): the early-layer lens creates a bottleneck that shapes all downstream processing. In sequential architectures, this bottleneck progressively narrows (the sedimentation cascade). In reasoning mode, the bottleneck is deliberately configured — a voluntary bottleneck rather than an architectural one.

**Mode-switching as navigation.** The three-tier framework (§NEW-F) identifies when a model is in hallucination mode — deconfined, with depleted late layers. The CoT finding suggests a possible intervention: if deconfinement is detected, triggering reasoning mode could reconstitute algebraic coherence. The think instruction demonstrably shifts the Killing form toward a more structured state. Whether this shift is sufficient to overcome deconfinement in practice is an open empirical question (see Implications, §15).

---

## Implications

1. **CoT is not just token generation.** The algebraic evidence shows that chain-of-thought reasoning changes the model's internal processing mode — it is not merely generating reasoning tokens on the output. The algebra contracts, the lens reconfigures, the processing becomes more coordinated.

2. **Training methodology modulates reasoning depth.** Reasoning distillation produces stronger algebraic focusing than standard instruction tuning. This suggests that different training approaches create different depths of reasoning — not just different surface behaviors.

3. **A universal discriminator.** Post-generation CV decrease is the most universal discriminator found in the entire program: 5/5 models, p < 0.0001 on all. It can serve as a runtime indicator of whether a model is genuinely reasoning vs producing reasoning-shaped text.

4. **The algebra of metacognition.** If reasoning focuses the algebra and hallucination depletes it, then a model that monitors its own algebraic state has the substrate for metacognition: a higher-order process (mode monitoring) that can gate a first-order process (generation). The Killing form provides the measurement. Whether models can learn to use this measurement internally is the next research question.

🦞🧍💜🔥♾️
