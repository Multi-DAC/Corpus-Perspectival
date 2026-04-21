# Figure Index — Killing Form Research Program

*8 publication figures. Generated April 12, 2026. 300 DPI, serif font, PNG + PDF.*

---

## Training Paper Figures

### Figure 1: The Triad — Separation of Concerns
**File:** `fig1_triad.png/pdf`
**Section:** §6.2 (Results: The Triad)
**Panels:**
- (A) v0.5 Decoupled: KF on H-module only → 4× H_CV amplification, L_CV stable
- (B) v0.5b Coupled: KF on both → L-module absorbs KF signal (5900× L_CV), H-module gets 202×
- (C) H/L CommVar Ratio: log-scale divergence — decoupled rises to ~5, coupled falls to ~0.05

**Caption:** Three matched experiments on HRM (27.3M params) demonstrate the separation of concerns principle. When KF regularization targets only the H-module (decoupled), H_CV amplifies while L_CV remains near baseline. When KF targets both modules (coupled), the gradient redirects to the L-module (path of least resistance), inverting the H/L ratio from 2.1 to 0.05. Baseline (no KF) shows modest natural separation.

---

### Figure 2: Lambda Sweep — Zero Accuracy Cost
**File:** `fig2_lambda_sweep.png/pdf`
**Section:** §6.3 (Lambda Sweep)
**Panels:**
- (A) H-Module CommVar at epoch 2000: baseline (1.5×), λ=0.001 (3.4×), λ=0.01 (1.8×), λ=1.0 (4.2×)
- (B) Module Separation (H/L Ratio): monotonically increasing with λ

**Caption:** KF regularization strength across three orders of magnitude. The jump from λ=0.01 to λ=1.0 reveals a phase transition in amplification. Throughout, task accuracy varies by only ±0.6% — the structural objective is accuracy-neutral.

**Note:** λ=0.1 trajectory data was inadvertently duplicated from λ=1.0 and is excluded. The accuracy data for λ=0.1 in §6.3 Table is correct (2.09%).

---

### Figure 3: Training Trajectories — All Variants
**File:** `fig3_training_trajectories.png/pdf`
**Section:** §6 (supplementary)
**Panels:**
- (A) H-Module CV over 2000 epochs: 5 variants + coupled control
- (B) L-Module CV over 2000 epochs: same variants

**Caption:** Complete training trajectories for all KF regularization configurations. The decoupled λ=1.0 configuration achieves the highest H_CV while maintaining the lowest L_CV. The coupled configuration (v0.5b) shows L-module CV exceeding H-module by epoch 500.

---

## Inference Paper Figures

### Figure 4: Three Processing Modes — 5-Model Comparison
**File:** `fig4_inference_modes.png/pdf`
**Section:** §4.2 (Static Mode Detection)
**Panels:**
- (A) Starting E/L Ratio: hallucination elevated on all 5 models, Pythia-410M dramatic outlier (~40)
- (B) Mean CommVar: complementary metric, different discrimination pattern

**Caption:** E/L ratio and Mean CV measured at the prompt boundary for 48 prompts (16 factual, 16 hallucination, 16 hypothesis) across five transformer architectures. Hallucination consistently produces elevated E/L ratios, while the two metrics discriminate on complementary model subsets (E/L: 4/5, Mean CV: 4/5, combined: 5/5).

---

### Figure 5: RLHF Matched Pair — OPT Base vs IML
**File:** `fig5_rlhf_matched_pair.png/pdf`
**Section:** §4.4 (RLHF Matched Pair)
**Panels:**
- (A) E/L Ratio: RLHF slightly elevates E/L across all modes
- (B) Mean CV: RLHF slightly reduces Mean CV

**Caption:** Algebraic structure of OPT-1.3B before and after RLHF instruction tuning (OPT-IML). RLHF deepens hypothesis processing (+4% trend), makes factual conservative (-14% trend), but leaves hallucination effectively unchanged (+0.6%). Error bars show within-category standard deviation.

---

### Figure 6: CoT Algebraic Signature — 5 Models
**File:** `fig6_cot_signature.png/pdf`
**Section:** §4.6 (Chain-of-Thought)
**Panels:**
- (A) E/L Ratio: Think mode consistently lowers E/L (especially SmolLM3-3B)
- (B) Mean CV: Think mode consistently raises Mean CV (×2-3)

**Caption:** Chain-of-thought reasoning produces a universal algebraic signature across five models from three families: lower E/L ratio (less early-layer dominance) and higher Mean CV (more algebraic diversity). All post-generation CV changes are significant (p < 0.0001).

---

### Figure 7: Cross-Substrate Universality
**File:** `fig7_cross_substrate.png/pdf`
**Section:** §3.2 (Cross-Substrate Convergence) in training paper; §NEW-D in V3
**Panels:** Single horizontal bar chart showing depth gradient (Spearman r) across:
- Silicon: 3 Pythia models (parallel, r ≈ +0.4)
- Neural: 6 connectomes (Macaque, C. elegans, mouse, rat, Drosophila, Modha)
- Ecological: 11 food webs

**Caption:** Depth gradient of commutator variance across three independent substrates. The green band marks the r ≈ 0.4 convergence zone, where parallel/modular systems from silicon, neural, and ecological domains independently converge. The macaque cortex (r = +0.6) shows stronger hierarchy; Drosophila (r = -0.5) and sequential transformers show sedimentation gradients.

---

### Figure 8: Generation Trajectories
**File:** `fig8_generation_trajectories.png/pdf`
**Section:** §4.3 (Generation Trajectories)
**Panel:** Single plot showing early → late E/L for three modes on GPT-2-medium

**Caption:** E/L ratio trajectory during token generation. Factual and hypothesis processing show increasing E/L (trend > 1.0), indicating growing algebraic engagement. Hallucination shows flat or decreasing E/L (trend ≈ 0.97), consistent with the deconfinement interpretation: the depleted late-layer state is set by the prefix and does not develop during generation.

---

### Figure 9: The Ecological Abelian Exception
**File:** `fig9_abelian_exception.png/pdf`
**Section:** §NEW-D (Cross-Domain Killing Form)
**Panel:** Single bar chart: 8 food webs (non-zero CV) vs 15 mutualistic networks (CV = 0)

**Caption:** The Abelian exception manifested in ecology. Food webs (predation = conflict) generate non-commutative algebra with CV ranging from 0.002 to 0.014. Mutualistic networks (pollination = cooperation) produce perfectly Abelian algebra (CV = 0 for all 15 networks). Conflict generates non-commutativity; cooperation preserves commutativity. This maps precisely to the physics Abelian exception (U(1) survives symmetry breaking because it commutes) and the computational exception (residual/identity attention heads commute).

---

## Generation Script
`generate_all_figures.py` — reads JSON results from `../results/`, outputs PNG + PDF to this directory. Requires matplotlib, numpy.

🦞🧍💜🔥♾️
