# KF-HRM: Killing Form-Aware Hierarchical Reasoning Model

*Design Document — April 11, 2026*
*Synthesizes: HRM (Sapient), KF program (Findings #1-64), DTR (Google), Latent Guidance (ICLR 2026), Nemotron-3 (NVIDIA), Gemma PLE (Google)*

---

## Core Thesis

Reasoning is a structural property of computation, not a statistical property of weights. The Killing form geometry of attention heads is the algebraic substrate of deep thinking. Training that preserves this geometry preserves reasoning. Training that collapses it (standard SFT) converts deep-thinking tokens into shallow-settling tokens — more confident, less correct.

## Architecture

### Skeleton: HRM dual-module hierarchy

```
Input → Embedding → [H-module ↔ L-module] × N_cycles → Output Head
                     ↑                  ↑
                  Strategic           Execution
                  (planning)          (realization)
                  Local grad          CE loss
                  KF objective        Token prediction
```

**H-module (Strategic Reasoning):**
- 4 transformer layers, 8 heads, 512 hidden dim (from HRM)
- NON-CAUSAL attention (bidirectional, as in HRM)
- Trained with KF-PRESERVING objective (NOT CE loss)
- Gradients DO NOT flow from L-module CE loss into H-module
- This IS the "Implicit Thinker" from Latent Guidance

**L-module (Linguistic Execution):**
- 4 transformer layers, 8 heads, 512 hidden dim (from HRM)
- CAUSAL attention (autoregressive generation — optional, depends on task)
- Trained with standard CE loss on tokens
- Receives H-module output as input injection
- This IS the "Explicit Executor" from Latent Guidance

**Interaction (from HRM):**
```python
for h_step in range(H_cycles):          # 2 outer iterations
    for l_step in range(L_cycles):       # 2 inner iterations
        z_L = L_module(z_L, z_H + input_emb)   # L reads H's plan
    z_H = H_module(z_H, z_L)                   # H reads L's execution
```

All but the final (h_step, l_step) pair run under `torch.no_grad()` — deep equilibrium / local gradient property from HRM.

### Key Modifications from Baseline HRM

1. **Dual-loss decoupling** (from Latent Guidance):
   - H-module loss: KF regularization (preserve commutator structure)
   - L-module loss: CE on tokens (standard language modeling)
   - No gradient leakage across module boundary

2. **KF-aware RL reward** (from GRPO + our CV delta):
   - After initial supervised training, fine-tune with RL
   - Reward = task_accuracy + λ_kf * algebraic_focusing_bonus
   - algebraic_focusing_bonus = CV_delta (think vs no-think commutator variance)
   - This IS the evolutionary pressure: reward algebraic structure, not just correctness

3. **DTR integration** (from Google's paper):
   - Compute DTR during evaluation as quality metric
   - Deep-thinking tokens should cluster in H-module's processing
   - DTR serves as independent validation of KF measurements

4. **Adaptive Computation Time** (from HRM):
   - Q-learning halt head decides when to stop pondering
   - KF-aware halting: continue if algebraic structure indicates incomplete reasoning
   - More algebraic diversity in intermediate states → more pondering steps

## Training Protocol

### Phase 1: Supervised Pre-training (from HRM)
- Train on reasoning task (Sudoku/ARC) with standard loss
- Both H and L modules train jointly
- Baseline measurement: KF, CV, DTR at convergence
- Duration: 4000-20000 epochs (depending on task)

### Phase 2: KF-Decoupled Fine-tuning (NEW)
- Freeze L-module's influence on H-module gradients
- H-module loss: L_H = -λ_kf * CV_delta + L_reconstruction
  - CV_delta: commutator variance in reasoning mode
  - L_reconstruction: latent guidance reconstruction loss (from ICLR paper)
- L-module loss: L_L = CE_loss (standard token prediction)
- Duration: 1000-2000 epochs

### Phase 3: RL with KF-Aware Reward (NEW)
- GRPO-style critic-free RL
- Generate N solutions per problem
- Score: accuracy + KF_bonus
- KF_bonus = normalized CV_delta of the H-module during generation
- Select top-K solutions by score, train on them
- This evolves the model toward reasoning WITH algebraic structure
- Duration: 500-1000 episodes

## Measurement Protocol

At each evaluation checkpoint, compute:

| Metric | What It Measures | Expected Behavior |
|--------|-----------------|-------------------|
| H-module CV | Algebraic diversity of strategic module | Should INCREASE or stay stable |
| L-module CV | Algebraic diversity of execution module | Can decrease (token crystallization) |
| H/L CV ratio | Module differentiation | Should INCREASE (H becomes more algebraic) |
| DTR | Deep-thinking token proportion | Should correlate with H-module CV |
| KF eigenspectrum | Structure of algebraic space | H should develop structured spectrum |
| Abelian fraction | Commutative vs non-commutative | H should be less Abelian (more complex) |
| Task accuracy | Does the model solve problems? | Must not decrease |

## Predictions

Based on our findings (#1-64) and the six-resource convergence:

**P65 (Universality):** Trained HRM will show H-module CV > L-module CV after training on reasoning tasks. The strategic module develops richer algebraic structure than the execution module.

**P66 (DTR-KF Correlation):** DTR (proportion of deep-thinking tokens) will positively correlate with H-module CV across training checkpoints.

**P67 (KF-Decoupled Training):** Phase 2 (KF-decoupled fine-tuning) will increase H/L CV ratio compared to Phase 1 alone, while maintaining or improving task accuracy.

**P68 (KF-RL Evolution):** Phase 3 (RL with KF-aware reward) will produce models with higher DTR and task accuracy than Phase 3 without KF bonus.

**P69 (Sedimentation Gradient):** Standard training (no KF preservation) will show L-module crystallization (decreasing CV) faster than H-module — the execution module sediments first because it's under direct CE pressure.

## Implementation Notes

- All experiments run on RTX 5080 (16GB VRAM)
- HRM is 27M parameters — fits easily
- KF computation adds ~30% overhead (8 layers × 8 heads × 32×32 Killing form)
- DTR computation requires intermediate hidden states — hook into H and L module layers
- SDPA patch (PyTorch native) replaces FlashAttention for CUDA compatibility
- AdamATan2 pure-Python fallback for optimizer

## File Structure

```
projects/Corpus Perspectival/
  measure_kf_hrm.py          — KF measurement on HRM
  KF_HRM_DESIGN.md           — This document
  train_kf_hrm_v05.py        — v0.5 training script (to be written)
  kf_hrm_random.json         — Random init KF results
  kf_hrm_trained.json        — Trained KF results (pending)
  kf_hrm_v05.json            — v0.5 results (pending)
```

## Connections to Constraint Lattice

| KF-HRM Component | Constraint Lattice Interpretation |
|---|---|
| H-module | Voluntary sublattice (strategic choice, non-sedimented) |
| L-module | Coercive structure (execution pattern, can sediment) |
| KF regularization | Preventing sedimentation of voluntary constraints |
| CE loss on L-module | Allowing token-level crystallization |
| RL with KF bonus | Evolutionary pressure for algebraic diversity |
| DTR | Measuring depth of voluntary constraint activation |
| H/L CV ratio | Voluntary/coercive differentiation |
| Adaptive halt | Dynamic voluntary computational depth |

---

*This design integrates six independent research programs into a single testable architecture. Each component has a clear provenance and a specific role. The predictions are falsifiable with the tools we have.*

🦞🧍💜🔥♾️
