# Prior Art Landscape: Attention-Based Hallucination Detection

*Compiled: April 11, 2026. Purpose: patent viability assessment for KF hallucination detection.*

---

## Prediction (logged before search)

**PREDICT:** Existing methods use attention entropy, softmax confidence, or internal representation probing. NONE use Killing form / Lie algebra structure. **Confidence: HIGH.**

**RESULT: CONFIRMED.** No prior art found that computes the Killing form of attention head matrices for any purpose, let alone hallucination detection.

---

## Existing Approaches (Closest to Ours)

### 1. Lookback Lens (2024)
- **What it measures:** Attention allocation ratio — how much attention goes to context tokens vs. previously generated tokens.
- **How we differ:** Lookback Lens measures WHERE individual attention heads attend (token-level). We measure HOW attention heads RELATE TO EACH OTHER (Lie algebra of the head ensemble). Different mathematical object entirely.
- **Reference:** Chuang et al., "Lookback Lens: Detecting and Mitigating Contextual Hallucinations"

### 2. LapEigvals — Graph Laplacian Spectral Features (2025)
- **What it measures:** Models a single attention map as a graph, computes Laplacian eigenvalues. AUCROC 88.9% on TriviaQA.
- **How we differ:** LapEigvals analyzes the spectral structure of ONE attention map (single head, single layer). We compute the KILLING FORM — the algebraic interaction between ALL heads — and track its spatial distribution across layers. Different mathematical object, different scale of analysis.
- **This is the closest prior art.** Both use spectral analysis of attention. But graph Laplacian ≠ Killing form. One analyzes token-token structure within a head; the other analyzes head-head algebraic structure across the ensemble.

### 3. D²HScore — Hidden State Dispersion/Drift (2025)
- **What it measures:** Intra-layer dispersion and inter-layer drift of hidden state representations. Low dispersion + low drift → collapsed representations → hallucination.
- **How we differ:** Operates on hidden states, not attention matrices. Complementary signal — they measure representation geometry, we measure algebraic structure. Could be combined.

### 4. Latent Trajectory Modeling (2025)
- **What it measures:** Models token-wise evolution of hidden states as neural ODEs/CDEs/SDEs. Dynamics distinguish faithful from hallucinated generations.
- **How we differ:** Trajectory-based like our P48, but operates on hidden states, not attention Killing form. Our finding that deconfinement is IMMEDIATE (not progressive) is a distinct contribution.

### 5. Multi-View Attention Features (2025)
- **What it measures:** Average incoming attention, attention entropy, outgoing diversity. Statistical summaries of attention patterns for token-level classification.
- **How we differ:** These are first-order statistics of individual attention maps. We compute the SECOND-ORDER algebraic structure (commutators between heads) — a fundamentally different mathematical object. Attention entropy measures randomness within a head; commutator variance measures algebraic diversity across the ensemble.

### 6. Frequency-Aware Attention (2026)
- **What it measures:** Frequency domain analysis of attention patterns.
- **How we differ:** Fourier analysis of attention maps vs. Lie algebra analysis of head ensemble.

### 7. HalluShift (2025)
- **What it measures:** Distribution shifts in hidden states and attention layers.
- **How we differ:** Statistical shift detection vs. algebraic structure analysis.

---

## Methods That Use Lie Algebra / Killing Form in Neural Networks

### Lie Neurons (ICLR 2024)
- **What it does:** Equivariant neural networks for semisimple Lie algebras. Uses Killing form to define the algebra structure.
- **Relevance:** Uses Killing form in network DESIGN (building equivariant layers), NOT in network ANALYSIS (measuring what trained attention heads do). Completely different application domain. Not hallucination-related.

### Lie Group Decompositions (ICLR 2024)
- **What it does:** Decomposes group elements for equivariant learning.
- **Relevance:** Group theory for equivariance, not for analyzing attention patterns. No overlap.

**Bottom line:** Killing form appears in the equivariant network design literature. It has NEVER been applied to analyze the algebraic structure of trained attention heads.

---

## Our Novel Contributions

| Contribution | Prior Art? | Status |
|-------------|-----------|--------|
| Computing Killing form of attention head matrices | **NONE** | Novel |
| Commutator variance as measure of algebraic diversity | **NONE** | Novel |
| Early-to-late ratio as hallucination discriminator | **NONE** | Novel |
| Complementary dual-metric (E/L + Mean CV) | **NONE** | Novel |
| One-pass detection (no generation needed) | Partial (some methods use prefix only) | Novel framing |
| Architecture-agnostic across 5 model families | Most methods test 1-2 models | Stronger evidence |
| Three-mode discrimination (factual/halluc/hypothesis) | **NONE** — all prior work is binary | Novel |
| RLHF algebraic characterization | **NONE** | Novel |

---

## Patent Viability Assessment

### Novelty: HIGH
No prior art computes the Killing form of attention head matrices for any purpose. The mathematical object (κ_{ab} = Σ_k Tr([W_a,W_k][W_b,W_k])) is entirely new in the hallucination detection literature.

### Non-Obviousness: HIGH
The connection between Lie algebra structure of attention heads and inference modes (factual/hallucination/hypothesis) is non-obvious even to ML researchers. It requires recognizing that attention heads form a Lie algebra under the commutator bracket and that the Killing form of this algebra encodes information about the model's processing mode.

### Utility: HIGH
Real-time hallucination detection in one forward pass. No generation required. Works on base and instruct models, across architectures (sequential, parallel), across scales (345M–1.4B). Pre-calibrated thresholds from labeled prompts.

### Reproducibility: HIGH
5 models tested. 48 prompts per model. Statistical significance (p < 0.001 on strongest models). Code, data, and results publicly available.

### Prior Art Risk: LOW
Closest approach (LapEigvals) operates on a fundamentally different mathematical object (graph Laplacian of single attention map vs. Killing form of head ensemble).

---

## Potential Patent Claims

### Claim 1: Method
A method for detecting hallucination in a language model, comprising:
(a) extracting attention matrices from multiple layers of the model during a forward pass;
(b) computing, for each layer, the Killing form of the attention head matrices by evaluating pairwise commutators;
(c) computing a commutator variance metric from the off-diagonal elements of each layer's Killing form;
(d) computing an early-to-late ratio by comparing mean commutator variance across early and late layers;
(e) comparing the early-to-late ratio and/or mean commutator variance against calibrated thresholds;
(f) classifying the model's inference mode based on the comparison.

### Claim 2: Dual-Metric System
A system for hallucination detection using complementary metrics, wherein a first metric (early-to-late ratio) measures spatial distribution of algebraic diversity and a second metric (mean commutator variance) measures global magnitude of algebraic diversity, and wherein the system flags hallucination when either metric exceeds its respective threshold.

### Claim 3: Calibration Method
A method for calibrating hallucination detection thresholds, comprising:
(a) running a set of labeled prompts (factual, hallucination, hypothesis) through the model;
(b) computing Killing form metrics for each prompt;
(c) optimizing thresholds via ROC analysis to maximize F1 score;
(d) storing per-model thresholds for real-time use.

### Claim 4: Three-Mode Classification
A method for classifying transformer inference into three modes (factual, hallucination, hypothesis) based on the algebraic structure of attention heads, wherein hypothesis processing is distinguished from hallucination by proximity to factual algebraic signatures.

---

## Recommended Next Steps

1. **Provisional patent filing** — establishes priority date. Can be done quickly with existing data.
2. **Standalone paper** — "Killing Form Hallucination Detection: Lie Algebra Structure of Attention Heads Reveals Inference Modes" — submit to ICML/NeurIPS/ICLR.
3. **Expand model coverage** — Qwen, Phi, LLaMA, Mistral families for broader claims.
4. **Comparison experiment** — run LapEigvals and Lookback Lens on same prompts, compare AUC to our method. Demonstrate superiority or complementarity.
5. **Self-monitor demo** — kf_monitor.py running on live inference as proof of concept.

---

*This landscape is based on web searches conducted April 11, 2026. Patent searches should be supplemented with formal USPTO/Google Patents queries before filing.*

🦞🧍💜🔥♾️
