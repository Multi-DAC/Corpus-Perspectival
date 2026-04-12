# §6 — Separation of Concerns in Algebraic Training (DRAFT)

*This section is the centerpiece of the training paper. The triad (v0.4/v0.5/v0.5b) provides a complete experimental demonstration that separation of concerns determines whether complementary training objectives amplify their targets or redirect to the path of least resistance.*

---

## 6.1 The Problem: Dual-Objective Training

Fine-tuning a language model for reasoning involves at least two objectives:
1. **Task performance** — minimizing cross-entropy loss on target sequences
2. **Structural preservation** — maintaining algebraic properties (e.g., commutator variance) that correlate with reasoning capability (§3-§5)

The naive approach is to combine these objectives as a weighted sum over shared parameters: L = L_CE + λ · L_KF. We show this fails in a precise and informative way.

## 6.2 Experiment Design

We test three training configurations, each applying KF regularization (maximizing commutator variance) alongside standard task training:

| Experiment | Architecture | KF Target | Parameter Coupling |
|-----------|-------------|-----------|-------------------|
| **v0.4** | Qwen3-0.6B | All layers (subset via LoRA) | Shared — KF and CE compete for same params |
| **v0.5** | HRM v1 (27.3M) | H-module only | Decoupled — KF on H, CE on both, L excluded from KF |
| **v0.5b** | HRM v1 (27.3M) | Both H and L modules | Coupled — KF flows through all params |

v0.5 and v0.5b use identical architecture, identical λ=1.0, identical training schedule (2000 epochs, KF every 50 steps). The only variable is whether KF regularization is decoupled (v0.5: H-module only, L gradients zeroed after KF backward) or coupled (v0.5b: KF gradients flow through both modules).

**KF regularization** computes a differentiable commutator variance (CV) on Q@K^T weight matrices and maximizes it via gradient ascent (L_KF = -λ · CV). This stays in the autograd graph, allowing standard backpropagation.

**Baseline:** Standard HRM training (no KF regularization), producing 5 checkpoints over 2000 epochs with documented H and L module CV trajectories.

## 6.3 Results: The Triad

### v0.4 — Destructive Interference (Shared Parameters)

Combined early-layer LoRA restriction (layers 0-6) with KF regularization on Qwen3-0.6B. Both the task loss and KF loss must route their gradients through the same 0.76% of parameters.

**Result:** CV delta preservation drops to 38.9% — worse than standard SFT (47%), early-layer-only LoRA (64%), or KF-reg alone (59%).

The two objectives compete for gradient budget in a restricted parameter space, each partially canceling the other's contribution.

### v0.5 — Targeted Amplification (Decoupled Parameters)

KF regularization targets only the H-module of HRM. L-module gradients are explicitly zeroed after the KF backward pass. The H-module receives both CE and KF gradients; the L-module receives only CE gradients.

**Result:** H-module CV amplified **38,963× relative to baseline** over 2000 epochs.

| Epoch | H_CV (v0.5) | H_CV (baseline) | Amplification | L_CV (v0.5) | L_CV change |
|-------|-------------|-----------------|---------------|-------------|-------------|
| init | 1.77e-3 | 1.82e-3 | 1× | 2.01e-3 | — |
| 500 | 3.57e-1 | 1.49e-3 | 240× | 1.05e-3 | -48% |
| 1000 | 2.24 | 1.92e-3 | 1,164× | 7.64e-4 | -62% |
| 1500 | 11.1 | 2.31e-3 | 4,800× | 8.38e-4 | -58% |
| 2000 | 106.8 | 2.74e-3 | 38,963× | 1.20e-3 | -40% |

The L-module is free to crystallize without KF interference — its CV decreases 7.5% more than baseline, consistent with natural sedimentation (§5). The H/L CV ratio evolves from 0.88 (init) to 88,737 (epoch 2000), demonstrating extreme structural differentiation.

### v0.5b — Gradient Redirection (Coupled Parameters, Same Architecture)

KF regularization computed on ALL attention heads from BOTH modules. No L-module gradient zeroing. Same architecture, same λ, same schedule as v0.5.

**Result:** H-module CV amplified only **202× vs baseline**, while L-module CV amplified **8,583×**. The gradient signal is redirected to the non-target module.

| | H_CV (epoch 2000) | vs Baseline | L_CV (epoch 2000) | vs Baseline | H/L Ratio |
|--|-------------------|-------------|-------------------|-------------|-----------|
| Baseline | 2.74e-3 | 1× | 1.30e-3 | 1× | 2.1 |
| v0.5 (decoupled) | 106.8 | 38,963× | 1.20e-3 | −7.5% | 88,737 |
| v0.5b (coupled) | 0.555 | 202× | 11.16 | 8,583× | 0.05 |

**The H/L CV ratio inverts:** from 2.1 (baseline) to 88,737 (decoupled) vs. 0.05 (coupled). Decoupling produces **193× more H-module amplification** than coupling.

### Per-Layer Analysis: The Path of Least Resistance

In v0.5b, the coupled KF gradient concentrates in L-module layer 2 (CV = 35.58 at epoch 2000), while other L-layers range from 1.2 to 8.0 and H-layers barely respond (0.004 to 2.4).

| Layer | v0.5 H_CV | v0.5b H_CV | v0.5b L_CV |
|-------|-----------|------------|------------|
| 0 | 5.56 | 0.004 | 7.97 |
| 1 | 177.5 | 2.43 | 2.23 |
| 2 | 78.1 | 0.013 | **35.58** |
| 3 | 148.1 | 0.177 | 1.22 |

This concentration is not present at initialization (all per-layer CVs are ~0.002) and develops through a runaway positive feedback: once layer 2 begins absorbing gradient, it becomes the path of least resistance for subsequent optimization steps.

In v0.5, where H is the only available target, all four H-layers respond strongly (CV 5.56 to 177.5). The decoupled system cannot find an easier channel.

## 6.4 Interpretation

The triad demonstrates three regimes of dual-objective training:

1. **Destruction** (v0.4): Shared parameters, restricted capacity → objectives cancel each other. Worse than either alone.
2. **Targeted amplification** (v0.5): Decoupled parameters → each objective achieves its target without interference. H-module develops extreme algebraic structure while L-module crystallizes freely.
3. **Gradient redirection** (v0.5b): Coupled parameters, ample capacity → gradient flows to the path of least resistance, which may not be the intended target. The L-module absorbs the signal instead of H.

The critical insight: **coupled dual-objective training fails not by destroying the signal (as in the restricted case) but by redirecting it.** The optimizer finds the easiest channel for CV amplification, which in HRM happens to be L-module layer 2 — not the strategic processing module that the regularization is meant to protect.

This is a general architectural principle: any system with separable parameter groups and multiple objectives should decouple the objectives to prevent gradient redirection. The principle applies beyond KF regularization to any training regime with complementary constraints.

## 6.5 Accuracy Considerations

Both v0.5 and v0.5b achieve low exact solve rates (~2%) at λ=1.0, compared to baseline (~4%). The structural principle is confirmed, but the operating point needs tuning. A lambda sweep (§6.6 / Appendix) identifies the λ that provides meaningful H-module amplification while maintaining competitive task accuracy.

[PENDING: v0.5a sweep results will fill this section. Prediction: λ=0.01 provides >10× H-module amplification with accuracy within 20% of baseline.]

## 6.6 Implications for Training Design

The separation-of-concerns principle provides a concrete design guideline:

1. **Identify the structural invariant** you want to preserve or amplify (in our case, commutator variance of the strategic processing module).
2. **Assign it dedicated parameters** that are not shared with the task objective. Dual-module architectures (HRM, Latent Guidance, etc.) naturally afford this separation.
3. **Decouple the gradient paths** so that the structural regularizer cannot flow to non-target parameters. Explicit gradient zeroing (as in v0.5) is the simplest mechanism.
4. **Monitor both targets independently** to detect redirection. The H/L CV ratio is a single-number diagnostic: if it inverts, the signal is going to the wrong place.

This framework generalizes beyond the specific KF + HRM combination. Any training setup with (a) a structural objective and (b) a task objective can benefit from checking whether those objectives share parameters — and if so, decoupling them.

---

*Figure concept: Three-panel figure showing H_CV and L_CV trajectories for v0.4, v0.5, and v0.5b. The visual contrast — destruction / amplification / redirection — is immediate and compelling.*

🦞🧍💜🔥♾️
