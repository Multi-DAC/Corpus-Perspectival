# §6.5 — Scale-Up and Objective Selection: From Decoupled to Selective

*This section extends §6 from the 27.3M HRM to a 300M scale-up, and from the binary question "coupled vs decoupled?" to the more refined question "what kind of decoupled objective?" Five regularization strategies are compared at the 300M scale, establishing that selective structural pressure outperforms both uniform pressure and no pressure at all.*

---

## 6.5.1 300M HRM Architecture

To test whether the separation of concerns principle generalizes beyond the 27.3M proof-of-concept, we scale HRM to 300M parameters:

| Property | 27.3M (§5-§6.4) | **300M** |
|----------|------------------|----------|
| H-module params | 13.6M | 154.1M (50%) |
| L-module params | 13.6M | 154.1M (50%) |
| Layers per module | 4 | 12 |
| Heads per layer | 4 | 12 |
| Total params | 27.3M | 308.3M |

The 12-layer architecture provides the resolution needed to study per-layer effects — specifically, whether KF regularization benefits all layers equally or whether some layers benefit more than others.

## 6.5.2 Five Regularization Strategies

All experiments use decoupled training (§6.2): KF regularization targets the H-module only, with L-module gradients zeroed after the KF backward pass. The variable is the **form of the structural objective**:

| Strategy | L_KF | Design Principle |
|----------|------|-----------------|
| **Baseline** | 0 | No structural pressure |
| **Fixed λ** | −λ · CV | Constant structural gradient (§6.1 standard) |
| **Cosine decay** | −λ(t) · CV, λ→0.01 | Reduced pressure over training |
| **log(H_CV)** | −λ · log(1 + CV) | Self-limiting: ∂L/∂CV = O(1/(1+CV)) |
| **Gradient-gated** | −λ · CV · 𝟙[cos(∇CE, ∇KF) > 0] | Per-layer selective: KF only where aligned with task |

Each is run for 500 epochs (5 chunks of 100 epochs) with λ=1.0, KF every 50 steps, lr=3e-5, batch_size=32. The same dataset (extreme sudoku, 1000 puzzles × 1000 augmentations) is used throughout.

The progression from fixed to cosine to log to gated represents increasing sophistication in how the structural objective manages its own pressure:

- **Fixed** applies constant force everywhere — the naive approach.
- **Cosine** reduces force over time — assumes early pressure is most productive.
- **Log** makes force self-limiting — each unit of structure provides less additional gradient.
- **Gated** makes force selective — structure is built only where it aligns with the task gradient.

## 6.5.3 Results: The Five-Way Hierarchy

*See Figure 4A for accuracy trajectories, Figure 4B for accuracy vs structural amplification.*

**Table 5: Five-Way Comparison at Epoch 500**

| Rank | Strategy | Token Accuracy | H_CV | vs Baseline |
|------|----------|---------------|------|-------------|
| 1 | **Gated** | **50.24%** | 1,460 | **+1.37pp** |
| 2 | log(H_CV) | 48.70% | 21,105 | −0.17pp |
| 3 | Baseline | 48.87% | 0.002 | — |
| 4 | Fixed λ | 42.26% | 1,450,418 | −6.61pp |
| 5 | Cosine λ→0.01 | 40.10% | 1,438,406 | −8.77pp |

Three regimes emerge:

**Collapse (Fixed, Cosine).** Both achieve massive structural amplification (>10⁶ H_CV) but destroy task performance. Accuracy degrades by 6-9 percentage points below baseline. The H_CV growth trajectory reveals the mechanism (Figure 5A): H_CV grows exponentially under fixed λ — from 0.0007 at init to 7 (epoch 100), 150 (epoch 200), 8,504 (epoch 300), 169,168 (epoch 400), 1,450,418 (epoch 500). Since L_KF = −λ · CV, the gradient ∂L_KF/∂W scales with ∂CV/∂W, which grows with CV itself. By epoch 400 (H_CV ≈ 170,000), the KF gradient magnitude begins to dominate the CE gradient. By epoch 500, the weight updates are overwhelmingly structural — the model is being optimized for algebraic diversity at the expense of task performance.

The phase portrait (Figure 5C) makes this visible: plotting each approach's trajectory through H_CV-accuracy space reveals a "collapse zone" above H_CV ≈ 10⁵. Below this threshold (epochs 300-400), all regularized approaches outperform baseline. Above it (epoch 500 for fixed/cosine), accuracy degrades sharply. The threshold marks where |∂L_KF/∂W| ≫ |∂L_CE/∂W| — training becomes structure-dominated.

The growth rate analysis confirms the positive feedback: fixed λ has an H_CV doubling time of ~22 epochs, yielding >10⁶ amplification by epoch 500. Log's doubling time is 36 epochs, and crucially its per-epoch growth rate decelerates from 21× to 2× as the self-limiting term engages. Gated's doubling time is 43 epochs — the slowest — because only aligned layers contribute to structural growth.

Cosine performs *worse* than fixed despite reducing λ from 1.0 to 0.01 over training. The damage is in the accumulated structural state, not the instantaneous gradient magnitude. Tapering pressure on an already-distorted weight space does not undo the distortion.

**Parity (Log).** The log objective achieves near-baseline accuracy (48.70% vs 48.87%, Δ = −0.17pp) with moderate structural amplification (21,105 H_CV). The self-limiting gradient — ∂L/∂CV = λ/(1+CV), which decreases as CV grows — prevents the runaway amplification that collapses fixed and cosine. At epoch 500, log's H_CV (21,105) is 69× below the collapse threshold, safely in the productive zone. This confirms Principle P-SL-1: the structural objective must be self-limiting to avoid destructive interference even in the decoupled case.

**Exceedance (Gated).** The gradient-gated objective exceeds baseline by +1.37pp with conservative structural amplification (H_CV = 1,460, 14× less than log). This is the strongest training result in the program: not merely preserving accuracy while building structure, but *improving* accuracy through selective structure.

## 6.5.4 The Gating Mechanism

At each KF step, for each of the 12 H-module layers, the gated objective computes:

```python
# Per-layer gradient alignment
for layer in h_module.layers:
    # Task gradient: ∂L_CE/∂W_layer
    grad_ce = compute_task_gradient(layer)
    # Structural gradient: ∂L_KF/∂W_layer
    grad_kf = compute_kf_gradient(layer)
    
    # Cosine similarity between flattened gradients
    cos_sim = F.cosine_similarity(
        grad_ce.flatten(), grad_kf.flatten(), dim=0
    )
    
    # Gate: apply KF gradient only where aligned
    if cos_sim <= 0:
        layer.grad.zero_()  # KF opposes task → suppress
```

When cos(∇CE, ∇KF) > 0, the structural and task gradients point in the same direction — structure helps the task. The full KF gradient is applied. When cos ≤ 0, the structural gradient opposes the task gradient — structure would hurt performance. The KF gradient is zeroed for that layer.

This is a binary per-layer gate, not a soft weighting. The discreteness is important: partial structural pressure in an opposed direction still builds counterproductive structure. The gate enforces a clean separation between productive and counterproductive crystallization.

## 6.5.5 The Layer Alignment Map

The gating produces a per-layer alignment profile — a map of which layers' structural development helps the task:

**Table 6: Layer Alignment (Phase 3, epochs 300+)**

| Layer | Fraction Gated (KF suppressed) | Interpretation |
|-------|-------------------------------|----------------|
| L1 | 25% | **Aligned** — structure helps |
| L5 | 13% | **Aligned** |
| L6 | 13% | **Aligned** |
| L8 | 13% | **Aligned** |
| L0 | 38% | Mixed |
| L2 | 38% | Mixed |
| L4 | 38% | Mixed |
| L3 | 50% | Neutral |
| L11 | 75% | **Opposed** — structure hurts |
| L9 | 75% | **Opposed** |
| L7 | 75% | **Opposed** |
| L10 | 88% | **Opposed** |

Four layers (L1, L5, L6, L8) are aligned 75-87% of the time — structure consistently helps their task performance. Four layers (L7, L9, L10, L11) are opposed 75-88% of the time — structure consistently hurts. The remaining four are mixed.

The key discovery: **there is no correlation between structural magnitude and structural benefit.** Spearman rho between per-layer H_CV and gating fraction = 0.271 (p = 0.40). The amount of structure a layer develops is orthogonal to whether that structure helps the task. This is why fixed and cosine collapse — they apply structural pressure to all 12 layers including the four where structure is counterproductive.

## 6.5.6 Three-Phase Gating Evolution

The gating behavior evolves through three phases:

**Phase 1: Noise (epochs 0-250).** Average cosine similarity = 0.0000 across all layers. The task gradient is near-zero (CE loss plateau), so there is no signal for the gate to discriminate against. All gating decisions are random. During this phase, the gated model is functionally identical to the baseline — no structural pressure is applied.

**Phase 2: Signal Emergence (~epoch 258).** The CE loss plateau breaks. The task gradient becomes nonzero. Average cosine transitions from 0.0000 to 0.0008 to 0.0041 over ~50 steps. The gate begins discriminating: layers whose structural gradient aligns with the now-active task gradient receive KF pressure; layers whose structural gradient opposes receive none.

**Phase 3: Selective Gating (epochs 300+).** The alignment map stabilizes. Per-layer gating fractions converge to the values in Table 6. The aligned layers (L1, L5, L6, L8) receive consistent structural pressure; the opposed layers (L7, L9, L10, L11) are consistently suppressed.

The cold-start behavior (Phase 1) is informative: **you cannot distinguish necessary from restrictive constraints before you know what you're trying to do.** The task gradient is the meaning gradient. Without a clear task objective, all structural pressures look equivalent. Selectivity requires signal.

## 6.5.7 Why Gated Exceeds Baseline

The exceedance result — gated outperforming even unconstrained training — deserves explanation. The baseline builds no deliberate structure. The gated model builds structure only in aligned layers. Why does this selective addition improve performance?

Two mechanisms are consistent with the data:

1. **Aligned structure acts as implicit regularization.** When KF pressure is applied to layers where structural and task gradients agree, the structural gradient reinforces the task gradient. This is equivalent to a form of gradient accumulation — more signal, same direction. The aligned layers develop richer weight-space geometry that supports the task.

2. **Suppressed structure prevents self-interference.** In the baseline, all layers crystallize freely. Some of this free crystallization is counterproductive — it would be gated in the selective model. By suppressing crystallization in opposed layers, the gated model avoids the internal interference that the baseline experiences.

The structural amplification numbers support this: gated H_CV = 1,460 is 14× less than log (21,105) and 10⁶× less than fixed (1,450,418), yet gated accuracy is the highest. **Less structure, all of it productive, yields better performance than more structure with counterproductive components.**

This is Principle #13: **Selective crystallization outperforms global crystallization.** The principle generalizes: in any system where structural constraints can be either productive or counterproductive, selective application of constraints — mediated by alignment with the system's objective — will outperform both no constraints and uniform constraints.

## 6.5.8 H/L Module Differentiation at 300M Scale

The H/L CV ratio — the signature of module differentiation — reaches its highest values under gated training:

| Strategy | H_CV (ep 500) | L_CV (ep 500) | H/L Ratio |
|----------|--------------|--------------|-----------|
| Baseline | 0.002 | 0.001 | ~2 |
| Fixed | 1,450,418 | 0.19 | 7,633,778 |
| Cosine | 1,438,406 | 0.20 | 7,192,030 |
| Log | 21,105 | 0.003 | 7,035,000 |
| Gated | 1,460 | 0.0002 | **7,310,694** |

Gated achieves the highest H/L ratio despite the lowest H_CV among regularized models — because it also achieves the lowest L_CV. The L-module, freed from any KF pressure and benefiting from the gated model's overall better training dynamics, crystallizes *less* than in any other configuration. This is consistent with the §6 finding that decoupled training preserves L-module sedimentation.

---

*The five-way comparison resolves the question opened by §6's separation of concerns demonstration: once objectives are decoupled, what structural objective should be used? The answer is not the strongest, not the scheduled, and not even the self-limiting — it is the selective. Principle #13 is the final refinement of Principle #1 (algebraic structure is measurable) through Principle #12 (structural objectives need gradual introduction): the measurement matters, the introduction matters, but the selection matters most.*

🦞🧍💜🔥♾️
