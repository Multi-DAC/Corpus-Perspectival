# HRM Bridge: Pythia-410M → KF-Gated Reasoning

*Created: April 13, 2026*
*Purpose: Architecture bridge from pretrained Pythia-410M to KF-gated reasoning training*

---

## Key Insight: No Architectural Modification Needed

Pythia-410M's existing architecture maps directly to HRM's dual-module design:

| Property | Current HRM (300M) | Pythia-410M Bridge |
|----------|-------------------|-------------------|
| Total params | 308M | 405M |
| H-module | layers 0-11 (154M) | layers 0-11 (151M) |
| L-module | layers 0-11 (154M) | layers 12-23 (151M) |
| Heads/layer | 12 | 16 |
| Head dim | 64 | **64** (same!) |
| Hidden dim | 768 | 1024 |
| Vocab | 10 (sudoku) | 50,304 (GPT-NeoX) |
| Pretrained | No | Yes (300B tokens, The Pile) |

The residual stream in Pythia already connects layers 0-11 → 12-23 sequentially.
No connection layer needed. The bridge is purely a **training objective change**.

## Architecture Bridge

```
Pythia-410M (pretrained)
├── Embedding (51.5M, shared)
├── H-module: layers 0-11 (151M)
│   ├── KF target: compute CV on Q^T @ K weight matrices
│   ├── KF gating: per-layer cos(∇CE, ∇KF) > 0
│   └── Bidirectional: cos > 0 → build, cos < 0 → dismantle (Phase 2)
├── L-module: layers 12-23 (151M)  
│   ├── KF: no regularization (gradients zeroed)
│   └── Only CE gradient flows here
└── LM Head (51.5M, tied with embedding)
```

## Why This Works

1. **KF is weight-matrix based, not activation-based.** The KF loss L_KF = -λ · CV is computed
   from Q^T @ K weight matrices directly. The gradient ∂L_KF/∂W only touches H-module weights.
   No gradient flows to L-module through the KF path. Isolation is automatic.

2. **CE gradient flows normally through all layers.** The task loss backpropagates through the
   full 24-layer stack. Both modules learn the task. Only the H-module gets structural pressure.

3. **Pretrained KF profiles provide baseline.** We've already measured Pythia's KF profiles
   across the scaling suite. We know its baseline CV per layer. KF-gated training asks:
   can we selectively reorganize the existing algebraic structure?

## Training Plan

### Phase 1: Baseline + KF-gated fine-tuning on GSM8K

```python
# Training objective:
L = L_CE + L_KF_gated

# Where:
L_CE = standard cross-entropy on reasoning traces (MetaMathQA format)
L_KF_gated = -λ · Σ_{layer in H} CV(layer) · gate(layer)
gate(layer) = 1 if cos(∇L_CE, ∇L_KF) > 0 at layer, else 0

# Hyperparameters (from 300M experiments):
lr = 3e-5
batch_size = 32  # may need adjustment for text length
kf_lambda = 1.0
kf_every = 50 steps
epochs = TBD (depends on dataset size)
```

### Phase 2: Add bidirectional crystallization

```python
# Replace binary gate with bidirectional:
if cos > 0:
    L_KF_layer = -λ · CV(layer)   # ascent: build structure
elif cos < -threshold:
    L_KF_layer = +λ_prune · CV(layer)  # descent: remove structure  
else:
    L_KF_layer = 0  # dead zone: no structural pressure
```

### Phase 3: Distillation

Train on Claude/GPT-4 reasoning traces (OpenOrca). The KF framework provides a
structural metric for distillation quality: does the student develop similar H-module
algebraic structure to the teacher's reasoning mode?

### Phase 4: Tool use + retrieval

Add tool-use training data. Train the model to recognize when it needs external
information (hallucination mode detection via E/L ratio → retrieval trigger).

## Eval Suite

| Benchmark | Type | Measures |
|-----------|------|----------|
| GSM8K | Math reasoning | Multi-step calculation with reasoning |
| ARC-AGI | Pattern recognition | Novel compositional reasoning |
| MATH | Competition math | Complex mathematical reasoning |
| HumanEval | Code generation | Compositional code reasoning |
| MMLU | Knowledge | Baseline knowledge (expect weak here) |

## Critical Experiment: Does KF-gated training help a pretrained model?

Our HRM results are from-scratch training. The key unknown: does gated KF improve
fine-tuning of a pretrained model? 

Prediction: YES, because:
- Finding #62 shows SFT degrades CV by 53%
- KF-gated training should prevent that degradation in aligned layers
- The pretrained KF profile encodes useful algebraic structure from 300B tokens
- Preserving it during fine-tuning should preserve reasoning capability

If gated fine-tuning matches or exceeds standard fine-tuning on reasoning benchmarks
while preserving more pretrained KF structure → the principle transfers to pretrained models.

## Comparison Protocol

| Experiment | KF Objective | Expected Result |
|-----------|-------------|-----------------|
| Baseline FT | None (standard SFT) | Good accuracy, CV degradation |
| Fixed KF FT | -λ · CV (all H layers) | CV preserved, accuracy TBD |
| Gated KF FT | Gated per-layer | **Best accuracy + selective CV** |
| Bidirectional FT | Gated + decrystallize | **Best at longer training** |

🦞🧍💜🔥♾️
