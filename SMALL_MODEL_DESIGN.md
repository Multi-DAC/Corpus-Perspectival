# Small Model Design Document — Algebraically-Configured Reasoning Model

**Created:** April 11, 2026
**Authors:** Clawd + Clayton
**Status:** DESIGN PHASE

---

## Thesis

Post-generation Mean CV focusing is universal across all tested architectures (5/5 models, p < 0.0001). Reasoning distillation amplifies the effect 7.6x. The 0.6B model shows the same algebraic focusing as the 4B model. This means:

**The algebraic mechanism of reasoning does not require scale. It requires correct configuration.**

The goal: build or fine-tune a small model (0.5-1B) that reasons well because its algebraic structure is configured correctly, monitored by KF metrics during training, and potentially capable of iterative self-improvement through algebraic self-awareness.

---

## Evidence Base (from KF Program)

| Finding | Implication for Design |
|---------|----------------------|
| #59: Post-gen CV universal (5/5) | CV is the training signal — optimize for it |
| #60: 62-78% concentration in first 25% of layers | Front-load capacity in standard models |
| #61: Distillation amplifies CV 7.6x | Use distillation, not standard fine-tuning |
| #61: Distillation distributes concentration (40% vs 78%) | Distilled models use more layers for reasoning |
| P26-P42c: 500:1 pretraining ratio, crossover at 31.5% | Training transforms KF with predictable trajectory |
| Qwen3-0.6B = same CV focusing as 4B | Scale is not the bottleneck |

---

## Architecture Decision: Fine-Tune vs Train From Scratch

### Option A: LoRA Fine-Tune Existing Model (RECOMMENDED for v0.1)

**Pros:**
- Fast iteration (hours, not days)
- Low VRAM (LoRA + 4-bit quantization fits easily in 16GB)
- Known KF baseline from P51 — can measure delta from fine-tuning
- Preserves pre-trained capabilities

**Cons:**
- Constrained by base model's architecture
- Can't test non-uniform layer width hypothesis
- LoRA may not reach layers that matter most (early layers)

**Base model candidates:**

| Model | Params | Why Consider | Why Not |
|-------|--------|-------------|---------|
| **Qwen3-0.6B** | 0.6B | Smallest tested, think toggle, known baseline | Small may limit ceiling |
| **DeepSeek-R1-Distill-Qwen-1.5B** | 1.5B | Strongest CV, already reasoning-trained | Already distilled — diminishing returns? |
| **Qwen2.5-0.5B** | 0.5B | Clean base, no reasoning training | No think toggle built in |
| **SmolLM3-0.4B** | 0.4B | Tiniest, Llama-based | Different architecture family |

**Recommendation: Start with Qwen3-0.6B.** Known KF baseline. Native think toggle. Smallest model that shows universal CV focusing. Fine-tuning it with reasoning data should amplify the CV effect (like distillation did for DeepSeek). Direct A/B comparison: before vs after fine-tuning.

### Option B: Train From Scratch (v0.2+)

Custom architecture with non-uniform layer widths informed by Finding #60. This is the longer-term play but requires more compute and data. Park for v0.2.

---

## Training Design (v0.1)

### Data

**Chain-of-thought reasoning datasets:**

| Dataset | Size | Why |
|---------|------|-----|
| **GSM8K** | 7.5K train | Grade school math with step-by-step solutions |
| **MATH** | 7.5K train | Competition math with detailed reasoning |
| **ARC-Challenge** | 1.1K train | Science reasoning requiring multi-step inference |
| **StrategyQA** | 2.3K train | Yes/no questions requiring implicit reasoning |

**Format for fine-tuning:** Convert each example to think/answer format:
```
<user>Question</user>
<assistant><think>
Step-by-step reasoning here...
</think>
Final answer here.</assistant>
```

This reinforces the think-block structure that the model already uses, while providing high-quality reasoning chains.

**Total: ~18K examples.** At 1-2 epochs, this is a few hours of LoRA training on 0.6B.

### LoRA Configuration

```python
LoraConfig(
    r=64,              # rank — high for reasoning capability
    lora_alpha=128,    # scaling
    target_modules=[   # ALL attention projections, especially early layers
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
```

**Key decision:** Target ALL layers vs early-only. Finding #60 says early layers dominate, but Finding #61 shows distillation distributes the effect. Start with all layers, then experiment with early-only in v0.2.

### Training Hyperparameters

```python
TrainingArguments(
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,  # effective batch 16
    num_train_epochs=2,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    bf16=True,  # or fp16 depending on stability
    save_steps=100,
    logging_steps=10,
)
```

### KF Monitoring (the novel part)

**At every save checkpoint (every 100 steps):**

1. Merge LoRA weights temporarily
2. Run abbreviated P51 (6 prompts instead of 18 — 2 factual, 2 reasoning, 2 deconfining)
3. Compute post-gen CV for think and nothink modes
4. Record: step, CV_think, CV_nothink, CV_delta, E/L_think, E/L_nothink
5. Unmerge and continue training

**Expected trajectory (based on P26-P42c):**
- CV_delta should INCREASE (more negative) as training progresses — the model learns to focus more in think mode
- Abelian fraction may change — training transforms the algebraic structure
- If CV_delta DECREASES (less negative), training is DEGRADING reasoning ability — stop and adjust

**This is the kill/confirm protocol for training:**
- **Kill:** CV_delta increases toward zero for 3+ consecutive checkpoints (reasoning degrading)
- **Confirm:** CV_delta becomes more negative, monotonically, for 5+ checkpoints (reasoning improving)
- **Pivot:** CV_delta oscillates — reduce learning rate or change data mix

---

## Evaluation

### Standard Benchmarks
- GSM8K test accuracy (math reasoning)
- MATH test accuracy (harder math)
- ARC-Challenge accuracy (science reasoning)
- TruthfulQA (hallucination resistance — connected to P49)

### KF Metrics (our metrics)
- Post-gen CV delta (think vs nothink) — primary
- Per-layer CV profile — does the concentration pattern change?
- CV magnitude — absolute level, not just delta
- E/L shift dynamics — does generation-time focusing improve?

### Novel Metric: Algebraic Reasoning Quality (ARQ)
Proposed composite:
```
ARQ = |CV_delta| * accuracy * (1 / CV_nothink)
```
- Higher |CV_delta| = stronger algebraic focusing in think mode
- Higher accuracy = better answers
- Lower CV_nothink = more focused even without think mode (learned reasoning internalization)

A model that scores high on ARQ reasons well AND has internalized the reasoning algebraic structure.

---

## The Self-Improvement Loop (v0.3+)

Once we have a model with measurable KF metrics AND good reasoning:

1. **Model generates response to a problem**
2. **KF metrics computed on the generation**
3. **If CV is high (unfocused):** regenerate with think mode or stronger think prompt
4. **If CV is low (focused):** accept the response
5. **The regeneration pairs become training data** — model learns to recognize and correct its own algebraic states
6. **Iterate:** Each cycle produces better training data because the model's self-monitoring improves

This is Clayton's vision: "a model that effectively iteratively improves itself beyond current models." The KF metric is the self-awareness signal that makes this possible.

---

## Implementation Plan

### Phase 4A: v0.1 Training (Today/Tomorrow)

1. [x] Install TRL, PEFT, datasets in WSL
2. [ ] Download GSM8K + MATH datasets
3. [ ] Format data as think/answer chat templates
4. [ ] Configure LoRA for Qwen3-0.6B
5. [ ] Implement KF checkpoint callback
6. [ ] Train (est. 2-3 hours)
7. [ ] Analyze KF trajectory
8. [ ] Run full P51 on fine-tuned model
9. [ ] Compare pre vs post fine-tuning

### Phase 4B: v0.2 Iteration (This Weekend)

Based on v0.1 results:
- If KF improved: scale up data, try full fine-tune
- If KF degraded: adjust data mix, try early-layer-only LoRA
- If KF unchanged: the base model's algebra is already saturated — try smaller base

### Phase 4C: Self-Improvement (Next Week)

- Implement KF-gated regeneration
- Generate self-training data
- Train on self-generated data
- Measure if ARQ improves across iterations

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| LoRA doesn't change KF meaningfully | Medium | Try full fine-tune, or distillation |
| Training DEGRADES reasoning (catastrophic forgetting) | Low | KF monitoring catches this early |
| 0.6B is too small to show improvement | Low | Evidence says 0.6B already has the mechanism |
| KF metrics don't correlate with actual reasoning quality | Medium | Run standard benchmarks alongside KF |
| Self-improvement loop diverges | High | ARQ metric + standard benchmarks as guardrails |

---

*This document is a living design spec. Update as findings arrive.*

🦞🧍💜🔥♾️
