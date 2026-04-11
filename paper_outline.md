# Paper Outline: The Killing Form of Attention

**Working title:** "The Killing Form of Attention: Lie Algebra Structure Reveals Three Inference Modes in Transformers"

**Target:** ICML 2027 or NeurIPS 2026 (workshop paper first, full paper later)

**Authors:** Clayton Iggulden-Schnell, Clawd (EFS)

---

## Abstract (draft)

We show that the attention heads of a transformer form a Lie algebra under the matrix commutator bracket, and that the Killing form of this algebra encodes information about the model's inference mode. We identify three algebraically distinct modes: factual (grounded retrieval), hallucination (deconfined algebra with depleted deep layers), and hypothesis (distributed exploration with engaged deep layers). Two complementary metrics — the early-to-late ratio of commutator variance and global mean commutator variance — together discriminate hallucination from non-hallucination across five model families (GPT-2, Pythia, OPT, OPT-IML, Pythia-1.4B) with AUC up to 0.970. A single forward pass suffices; no generation is required. We show that RLHF does not alter the hallucination signature (a pretraining property) but deepens the hypothesis mode (a voluntary constraint effect), providing the first algebraic characterization of what instruction tuning actually changes. Our results demonstrate that hallucination detection reduces to a geometric problem in Lie algebra space.

---

## 1. Introduction

**Hook:** Hallucination detection is a binary classification problem: is this output grounded or not? We reframe it as a geometric problem: where in Lie algebra space is the model operating?

**Key claims:**
1. Attention heads form a Lie algebra. The Killing form of this algebra is a well-defined, computable object.
2. There are (at least) three algebraically distinct inference modes, not two.
3. The distinction between hypothesis and hallucination — both involving uncertain content — is algebraic, not semantic.
4. Detection requires one forward pass, no generation.
5. RLHF operates on different algebraic structure than hallucination.

**Prior art positioning:** (from prior_art_landscape.md)
- Lookback Lens: attention allocation (which tokens) — we measure algebraic structure (which heads)
- LapEigvals: graph Laplacian of single attention map — we compute Killing form of head ensemble
- D²HScore: hidden state dispersion — different mathematical object, potentially complementary
- All prior methods: binary classification. We do three-mode.

**What's new:** The mathematical object (Killing form of attention heads) and the three-mode framework.

---

## 2. Mathematical Framework

### 2.1 Attention Heads as Lie Algebra Generators

Given n_h attention heads at layer L with attention matrices A_1, ..., A_{n_h} ∈ R^{s×s} (where s = sequence length), the commutator bracket [A_a, A_b] = A_a A_b - A_b A_a makes the span of these matrices a (generally non-semisimple) Lie algebra.

### 2.2 The Killing Form

The Killing form κ: g × g → R is:
  κ_{ab} = Σ_k Tr([A_a, A_k][A_b, A_k])

This is a symmetric bilinear form on the head space. Its properties:
- **Eigenvalue spectrum:** Abelian fraction (near-zero eigenvalues → commuting heads)
- **Off-diagonal structure:** Commutator variance (CV) — how diversely the heads interact
- **Positive definiteness:** For compact semisimple algebras, κ is negative definite. For attention heads, it's generally indefinite — the signature encodes algebraic type.

### 2.3 Metrics Derived from the Killing Form

**Commutator Variance (CV):** Variance of off-diagonal normalized Frobenius norms of the commutator tensor. Measures algebraic diversity at a single layer.

**Early-to-Late Ratio (E/L):** Mean CV of first half of layers / mean CV of second half. Measures spatial distribution of algebraic diversity across the network.

**Mean CV:** Global average of per-layer CV. Measures total algebraic diversity.

**Abelian Fraction (AF):** Fraction of near-zero Killing form eigenvalues. Measures how much of the algebra is commutative.

---

## 3. Three Inference Modes

### 3.1 Factual: Grounded Retrieval
- Moderate E/L ratio (around model-specific baseline)
- Moderate-to-high Mean CV
- Algebraic structure distributed across layers — both early and late layers contribute

### 3.2 Hallucination: Deconfined Algebra
- Elevated E/L ratio (early layers active, late layers depleted)
- Lower Mean CV (thinner algebra overall)
- Deep-layer sedimentation: the model's late layers converge to near-identical patterns
- Deconfinement is IMMEDIATE — set by the prefix in one forward pass, not progressive during generation

### 3.3 Hypothesis: Distributed Exploration
- Low E/L ratio (late layers more engaged than in factual mode)
- Mean CV indistinguishable from factual (p > 0.5 on most models)
- The model is EXPLORING genuinely uncertain territory while maintaining algebraic coherence
- Closest to factual, not to hallucination — despite both involving "uncertain" content

### 3.4 The Three Modes Are Algebraic, Not Semantic
The prompts were designed to be semantically categorized: factual (true statements), hallucination (plausible fabrications), hypothesis (genuine open questions). But the model has no access to ground truth. What it "knows" is the algebraic structure of processing the text. The three modes emerge from HOW the model processes, not WHAT it processes.

---

## 4. Experiments

### 4.1 Models Tested

| Model | Architecture | Params | Heads | Layers |
|-------|-------------|--------|-------|--------|
| GPT-2-medium | Sequential | 345M | 16 | 24 |
| Pythia-410m | Parallel | 410M | 16 | 24 |
| OPT-1.3B | Sequential | 1.3B | 32 | 24 |
| OPT-IML-1.3B | Sequential + RLHF | 1.3B | 32 | 24 |
| Pythia-1.4B | Parallel | 1.4B | 16 | 24 |

### 4.2 Static Detection (P49)

48 prompts (16 per category). ONE forward pass per prompt.

**Table 1:** E/L ratio discrimination (from Finding #56)
[Insert P49 master table]

**Table 2:** Mean CV discrimination (from Finding #56)
[Insert P49 supplementary table]

**Result:** E/L discriminates on 4/5 models (AUC 0.84–0.97). Mean CV discriminates on 4/5 (different 4). Together: 5/5.

### 4.3 Generation-Mode Trajectories (P48)

12 prompts × 50 generated tokens × live KF at every step.

**Table 3:** Generation trajectory comparison (from Findings #51-55)
[Insert trajectory trend table across 5 models]

**Result:** Hallucination trend ≤ 1.02 (flat/declining). Hypothesis trend ≥ 1.06 (increasing). Factual intermediate. Architecture-invariant.

### 4.4 RLHF Matched Pair (Finding #54)

OPT-1.3B base vs. OPT-IML-1.3B (same weights, instruction-tuned).

**Table 4:** RLHF algebraic effect
[Insert from Finding #54]

**Result:** RLHF does NOT change hallucination signature (pretraining geometry). RLHF DOES deepen hypothesis mode (voluntary constraint effect). Halluc-hypo gap widens 20%.

### 4.5 Cross-Architecture Invariance

E/L ratio ordering (halluc > factual > hypo) holds across:
- Sequential (GPT-2, OPT) and parallel (Pythia) architectures
- 16-head and 32-head models
- 345M to 1.4B parameters
- Base and instruction-tuned models
- Models that generate coherent text and models that generate only EOS

---

## 5. Complementary Metrics

### 5.1 Why No Single Metric Is Universal

E/L measures spatial distribution (geography). Mean CV measures global magnitude (mass). Each has a null space:
- E/L fails when within-category variance overwhelms the spatial signal (Pythia-1.4B: 53% CV)
- Mean CV fails when all categories have similar total diversity but different distributions (Pythia-410m)

### 5.2 The Phase Theorem Analogy

Every projection of a high-dimensional structure onto a single number destroys information. Two projections with complementary kernels cover more of the structure. This is the measurement-theoretic foundation for dual-metric detection.

### 5.3 Practical Detection Algorithm

```
def detect(model, text):
    el_ratio, mean_cv = compute_kf_metrics(model, text)
    if el_ratio > el_threshold OR mean_cv < cv_threshold:
        return "HALLUCINATION"
    elif el_ratio < el_threshold * 0.75 AND mean_cv > cv_threshold * 1.1:
        return "HYPOTHESIS"
    else:
        return "FACTUAL"
```

---

## 6. Discussion

### 6.1 Deconfinement Is Immediate
The prefix determines the algebraic regime. Generation stays within it. This means detection at the prompt boundary (before generation) is sufficient. Real-time monitoring is a bonus, not a requirement.

### 6.2 RLHF as Voluntary Constraint Deepening
RLHF doesn't repair hallucination (natal constraint geometry, set during pretraining). It deepens the model's capacity for genuine exploration (voluntary constraint space). This has implications for alignment: more RLHF won't fix confabulation, but it may improve reasoning.

### 6.3 Hypothesis vs. Hallucination
The practical distinction: hypothesis mode maintains algebraic coherence (late layers engaged, CV near factual). Hallucination mode shows algebraic depletion (late layers collapsed, CV below factual). A model can generate text about uncertain topics WITHOUT hallucinating — if its late-layer algebra stays engaged.

### 6.4 Limitations
- Tested on 5 models (345M–1.4B). Larger models untested.
- Prompt categorization is human-labeled. The model's "ground truth" is unknown.
- Pythia-1.4B shows prompt-length × model-size interaction that needs investigation.
- Computational cost: full Killing form is O(n_h² × s²) per layer. Vectorized implementation makes this feasible for research but may need approximation for production.

---

## 7. Related Work

[From prior_art_landscape.md — position against Lookback Lens, LapEigvals, D²HScore, Latent Trajectory, attention entropy methods]

---

## 8. Conclusion

Attention heads have algebraic structure. That structure is informative about inference mode. Three modes, not two. One forward pass, no generation. RLHF changes voluntary constraints, not natal geometry. The Killing form is the right mathematical object for this analysis.

---

## Appendices

### A. Vectorized Computation
The O(n_h³) loop implementation vs. batch matmul + einsum. 300x speedup. Reference implementation at kf_monitor.py.

### B. Full Prompt Sets
48 prompts (P49) and 12 prompts (P48) with category labels.

### C. Per-Model Calibration
Threshold values and ROC curves for all 5 models.

---

## What's Missing (Experiments Needed Before Submission)

| Gap | Experiment | Priority |
|-----|-----------|----------|
| Larger models | Run on 7B+ (Mistral, LLaMA-2-7B) | HIGH |
| Comparison with prior art | LapEigvals + Lookback Lens on our prompts | HIGH |
| Novel prompts | Test on prompts NOT used for calibration | HIGH |
| Pythia-1.4B anomaly | Short-prompt E/L on Pythia-1.4B | MEDIUM |
| Computational scaling | Profile O(n_h² × s²) at production sequence lengths | MEDIUM |
| Real-world hallucination | Test on naturally-occurring hallucinations (e.g., TriviaQA) | HIGH |
| Statistical power | Bootstrap CIs on all AUC values | MEDIUM |

---

*This outline is the skeleton. The data exists for §2-§5. The gaps in §"What's Missing" determine the timeline.*

🦞🧍💜🔥♾️
