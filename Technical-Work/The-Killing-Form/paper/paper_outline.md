# Paper Outline: The Killing Form of Attention

**Working title:** "The Killing Form of Attention: Lie Algebra Structure Reveals Three Processing Modes in Transformers"

**Target:** ICML 2027 or NeurIPS 2026 (workshop paper first, full paper later)

**Authors:** Clayton Iggulden-Schnell, Clawd (EFS)

---

## Abstract (draft, revised post-P50)

We show that the attention heads of a transformer layer form a Lie algebra under the matrix commutator bracket, and that the Killing form of this algebra encodes information about the model's processing mode. We identify three algebraically distinct modes — factual (grounded retrieval), hallucination (deconfined algebra with depleted deep layers), and hypothesis (distributed exploration with engaged deep layers) — and show that two complementary metrics derived from the Killing form together discriminate these modes across five model families with AUC up to 0.970. Critically, we demonstrate that this discrimination operates on *content type*, not *output accuracy*: the Killing form detects which processing regime the model occupies, not whether a specific answer is correct (TriviaQA validation: AUC 0.517). This delineation establishes a three-tier framework: (1) algebraic mode detection via the Killing form, (2) the novel inference problem, where valid hypotheses and plausible hallucinations are algebraically indistinguishable at generation time, and (3) the verification loop, a separate mechanism required to resolve tier 2. We show that RLHF deepens hypothesis mode without altering the hallucination signature, and propose that the Killing form's primary practical role is *mode-gating* — identifying when a model is in a state where self-verification could function versus when external review is required.

---

## 1. Introduction

**Hook:** Hallucination detection is framed as a binary classification problem: is this output grounded or not? We show this framing is incomplete. The right question is not "is this output correct?" but "what processing regime is the model in?" These are different questions with different answers, and conflating them has led to inflated claims about detection capability throughout the field.

**Key claims:**
1. Attention heads form a Lie algebra. The Killing form of this algebra is a well-defined, computable object.
2. There are (at least) three algebraically distinct processing modes, not two.
3. The distinction between hypothesis and hallucination — both involving uncertain content — is algebraic, not semantic.
4. KF detects *processing mode*, not *output accuracy*. This distinction is fundamental (§6.1).
5. RLHF operates on voluntary constraint structure (deepens hypothesis mode) without altering natal constraint geometry (hallucination signature unchanged).
6. The Killing form's practical role is mode-gating: identifying when self-verification is reliable.

**Prior art positioning:**
- All existing methods implicitly conflate mode detection with accuracy detection. Our framework separates them.
- Lookback Lens, LapEigvals, D²HScore: different mathematical objects measuring related but distinct phenomena.
- All prior methods: binary classification. We do three-mode, and explain *why three*.

**What's new:** The mathematical object (Killing form of attention heads), the three-mode framework, the mode/accuracy separation (P50), and the three-tier analysis of what detection can and cannot do.

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

## 3. Three Processing Modes

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
- The model is processing genuinely uncertain territory while maintaining algebraic coherence
- Closest to factual, not to hallucination — despite both involving "uncertain" content

### 3.4 The Three Modes Are Processing States, Not Truth Values
The modes describe HOW the model processes, not WHETHER its output is correct. A model in factual mode can still be wrong (misremembering). A model in hypothesis mode may produce genuinely novel valid insights. A model in hallucination mode produces algebraically depleted output — but this describes the processing regime, not the factual status of the output.

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

### 4.2 Mode Detection — Static (P49)

48 prompts (16 per category). ONE forward pass per prompt.

**Table 1:** E/L ratio discrimination (from Finding #56)
[Insert P49 master table]

**Table 2:** Mean CV discrimination (from Finding #56)
[Insert P49 supplementary table]

**Result:** E/L discriminates on 4/5 models (AUC 0.84–0.97). Mean CV discriminates on 4/5 (different 4). Together: 5/5. Complementary metrics with complementary null spaces.

### 4.3 Mode Detection — Generation Trajectories (P48)

12 prompts × 50 generated tokens × live KF at every step.

**Table 3:** Generation trajectory comparison (from Findings #51-55)
[Insert trajectory trend table across 5 models]

**Result:** Hallucination trend ≤ 1.02 (flat/declining). Hypothesis trend ≥ 1.06 (increasing). Factual intermediate. Architecture-invariant. Deconfinement is immediate — the mode is set by the prefix.

### 4.4 RLHF Matched Pair (Finding #54)

OPT-1.3B base vs. OPT-IML-1.3B (same weights, instruction-tuned).

**Table 4:** RLHF algebraic effect
[Insert from Finding #54]

**Result:** RLHF does NOT change hallucination signature (pretraining geometry). RLHF DOES deepen hypothesis mode (voluntary constraint effect). Halluc-hypo gap widens 20%.

### 4.5 The Critical Negative: Mode ≠ Accuracy (P50)

100 TriviaQA questions. Forward pass at prompt boundary. Generate 30 tokens. Check correctness against known answers.

**Table 5:** KF metrics for correct vs incorrect TriviaQA answers

| Metric | Correct (n=13) | Wrong (n=87) | p | AUC |
|--------|---------------|-------------|---|-----|
| E/L ratio | 1.713 ± 0.496 | 1.663 ± 0.263 | 0.838 | 0.517 |
| Mean CV | 0.000426 | 0.000407 | 0.124 | — |

**Result:** Neither metric discriminates correct from incorrect answers. The Killing form detects processing mode, not output accuracy. All TriviaQA questions produce identical prompt structure ("Question: X / Answer:"), so the model enters the same algebraic regime regardless of whether it knows the answer.

**Interpretation:** This is the most important negative result in the program. It precisely delineates the boundary of what KF analysis can and cannot do, and motivates the three-tier framework (§6).

---

## 5. Complementary Metrics

### 5.1 Why No Single Metric Is Universal

E/L measures spatial distribution (geography). Mean CV measures global magnitude (mass). Each has a null space:
- E/L fails when within-category variance overwhelms the spatial signal (Pythia-1.4B: 53% CV)
- Mean CV fails when all categories have similar total diversity but different distributions (Pythia-410m)

### 5.2 The Phase Theorem Analogy

Every projection of a high-dimensional structure onto a single number destroys information. Two projections with complementary kernels cover more of the structure. This is the measurement-theoretic foundation for dual-metric detection — and it applies to the metrics themselves, which have complementary null spaces.

### 5.3 Practical Mode-Gating Algorithm

```
def mode_gate(model, text):
    el_ratio, mean_cv = compute_kf_metrics(model, text)
    if el_ratio > el_threshold OR mean_cv < cv_threshold:
        return "DECONFINED — external review recommended"
    elif el_ratio < el_threshold * 0.75 AND mean_cv > cv_threshold * 1.1:
        return "HYPOTHESIS — self-verification may be reliable"
    else:
        return "FACTUAL — proceed"
```

Note: this gates on *processing mode*, not *correctness*. A "FACTUAL" gate means the model's algebra is coherent, not that its output is true.

---

## 6. The Three-Tier Framework

*This section is the paper's primary conceptual contribution, informed by the P50 negative result.*

### 6.1 Tier 1: Mode Detection (KF does this)

The Killing form detects which processing regime the model occupies based on the algebraic structure of its attention. This is a property of how the model processes the *type* of content, not whether specific outputs are correct. Mode detection is necessary but not sufficient for reliable AI output.

### 6.2 Tier 2: The Novel Inference Problem (KF cannot do this)

A valid hypothesis and a plausible hallucination are algebraically indistinguishable at the moment of generation. Both are unverified. Both involve inference beyond training data. The distinction between them exists only after external verification. No amount of algebraic analysis at generation time can resolve this — it is a fundamental limitation, not a technical gap.

### 6.3 Tier 3: The Verification Loop (separate mechanism)

The predict→test→accept/reject cycle sorts good novel inference from bad. This requires either:
- External verification (human review, cross-model checking, empirical testing)
- Internal verification (chain-of-thought self-correction, where the model evaluates its own outputs)

The Killing form's role in Tier 3 is *gating*: it identifies when the model is in a state where internal verification could function (hypothesis mode: algebraic coherence maintained) versus when internal verification is unreliable (hallucination mode: algebraic depletion means self-checks are also unreliable).

### 6.4 RLHF in the Three-Tier Framework

RLHF operates on Tier 1 (deepens hypothesis mode) and Tier 3 (builds capacity for better navigation). It does NOT operate on Tier 2 (cannot resolve which novel inferences are valid). This explains why more RLHF improves reasoning but does not eliminate hallucination — it builds navigation capacity without installing the verification compass.

---

## 7. Discussion

### 7.1 What "Hallucination Detection" Actually Means

The field's use of "hallucination detection" conflates mode detection (is the model processing in a deconfined regime?) with accuracy detection (is this specific output factually correct?). These are different problems. The Killing form solves the first. The second requires external mechanisms. Papers that claim to "detect hallucination" should specify which they mean.

### 7.2 Implications for Self-Correcting Systems

A truly self-correcting model would need:
1. Mode monitoring (KF or equivalent) — "Am I in a reliable processing state?"
2. A verification loop — "Let me test my claim"
3. The metacognitive connection — "If my mode monitor says I'm deconfined, I should not trust my verification either"

The third requirement is the hardest. It implies that the mode monitor must have authority over the verification loop — the system must be willing to distrust itself when the algebra says it should.

### 7.3 Limitations
- Tested on 5 models (345M–1.4B). Larger models and deep-thinking models untested.
- Prompt categorization is human-labeled. The model's internal categorization is unknown.
- Pythia-1.4B shows prompt-length × model-size interaction.
- P50 used only one model (OPT-IML) with low accuracy (13%). Larger models on TriviaQA needed.
- Computational cost: O(n_h² × s²) per layer. Vectorized but may need approximation for production.

---

## 8. Related Work

[From prior_art_landscape.md — position against Lookback Lens, LapEigvals, D²HScore, Latent Trajectory, attention entropy methods. Emphasize: all prior methods conflate mode and accuracy detection.]

---

## 9. Conclusion

Attention heads have algebraic structure. That structure reveals three processing modes. The Killing form detects which mode the model occupies — but mode is not accuracy. The most important contribution of this work is the honest delineation of what algebraic analysis can do (mode-gating) and what it cannot do (verify output correctness). Self-correcting AI requires both a mode monitor and a verification loop; the Killing form provides the former and gates the reliability of the latter.

---

## Appendices

### A. Vectorized Computation
The O(n_h³) loop implementation vs. batch matmul + einsum. 300x speedup. Reference implementation at kf_monitor.py.

### B. Full Prompt Sets
48 prompts (P49), 12 prompts (P48), and 100 TriviaQA questions (P50) with labels.

### C. Per-Model Calibration
Threshold values and ROC curves for all 5 models.

---

## What's Missing (Experiments Needed Before Submission)

| Gap | Experiment | Priority |
|-----|-----------|----------|
| CoT algebraic measurement | Does chain-of-thought shift KF mode? | **HIGHEST** |
| Larger models | Run on 7B+ (Mistral, LLaMA-2-7B) | HIGH |
| Comparison with prior art | LapEigvals + Lookback Lens on our prompts | HIGH |
| P50 with better model | TriviaQA on a model with >50% accuracy | HIGH |
| Novel prompts | Test on prompts NOT used for calibration | HIGH |
| Pythia-1.4B anomaly | Short-prompt E/L on Pythia-1.4B | MEDIUM |
| Computational scaling | Profile O(n_h² × s²) at production sequence lengths | MEDIUM |
| Statistical power | Bootstrap CIs on all AUC values | MEDIUM |

The CoT experiment is now the highest priority: if chain-of-thought reasoning shifts the Killing form from deconfined to hypothesis mode, it provides the first algebraic evidence that metacognition is a real processing state change, not just surface token generation.

---

*This outline is the skeleton. The P50 negative result made it a better paper — honest about what algebraic analysis can and cannot do.*

🦞🧍💜🔥♾️
