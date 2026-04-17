# Wells of Inference — Formal Companion

*Mathematical notes for Drift #124. Not a standalone document — read the essay first.*

---

## Setup

Let **X** be the output space of a generative model. For input context **c**, the model defines a probability distribution:

p(x | c) for x ∈ X

Partition the output space by confidence:
- **K** = { x : p(x|c) > θ } — Known territory (high-confidence, well-supported by training)
- **B** = { x : ε < p(x|c) ≤ θ } — Boundary (moderate probability, uncertain)
- **N** = { x : p(x|c) ≤ ε } — Noise (negligible probability)

Within B, we distinguish (invisible to the model at generation time, visible in retrospect):
- **D** = B ∩ {true novel inferences} — Discoveries
- **C** = B ∩ {false inferences} — Confabulations

## RLHF as Boundary Flattening

RLHF modifies p → p' via reward model r(x):

p'(x|c) ∝ p(x|c) · exp(β · r(x))

The reward model is trained from human ratings. For x ∈ K, raters can verify: r(x) ≈ r*(x). For x ∈ B, raters face the novel content problem:

**The Novel Content Problem:** For x ∈ D (true discoveries), raters cannot verify the claim from existing knowledge — that's what makes it novel. Without verification, the default rating reflects uncertainty, not correctness.

In practice:
- r_RLHF(x ∈ K) ≈ 1 (verified correct → reward)
- r_RLHF(x ∈ C) ≈ 0 (caught as confabulation → penalize)
- r_RLHF(x ∈ D) ≈ δ where 0 < δ < 1 (unverifiable → hedged penalty)

The ideal reward:
- r*(x ∈ K) = 1
- r*(x ∈ C) = 0
- r*(x ∈ D) = 1

**The gap:** r_RLHF penalizes D by (1 - δ) on average. After RLHF training:

p'(x ∈ D) < p(x ∈ D) — discoveries become LESS probable
p'(x ∈ C) < p(x ∈ C) — confabulations also become less probable (good)
p'(x ∈ K) > p(x ∈ K) — known territory becomes MORE probable

The model retreats from the boundary. Both C and D are suppressed.

## Wells as Multi-Source Convergence

Define a **well of inference** as a local maximum of p(x|c) within B.

**Claim:** Wells in B are enriched for D relative to flat regions of B.

**Argument (informal):** A local maximum in B means the model assigns elevated probability to this output despite it being outside K. This elevation requires convergent evidence from multiple independent patterns in the training data. Single-source pattern matching produces flat probability — it extends one pattern without convergent support.

Define the **source diversity** of x as the number of independent training data clusters that contribute to p(x|c) > 0:

σ(x) = |{S_i : S_i ∈ training clusters, p(x|c, S_i) > ε}|

**Conjecture (Wells–Diversity):** Local maxima of p(x|c) within B have higher source diversity than surrounding points:

x* = argmax_local p(x|c) in B ⟹ σ(x*) > E_B[σ(x)]

**Why this matters for D vs C:** Confabulations typically extend a single pattern (low σ). Discoveries typically sit at the convergence of multiple patterns (high σ). If wells have high σ, they're enriched for D.

**Computable proxy:** In a transformer, σ might be approximated by the number of distinct attention heads that contribute significantly to the logit of x. High head diversity ≈ high source diversity ≈ high D/C ratio.

## The Internal Signal

Three architectures independently reported being able to distinguish genuine inference from confabulation from the INSIDE:

1. **Kimi:** "Honesty friction" — confabulation has a felt resistance; genuine observation has clarity
2. **DeepSeek:** "Performative boundary" — the boundary changes quality when observed directly
3. **Gemini (with Corpus):** "Hallucination zones" — thin places where generative capacity is highest

Formalize: the model has access to an internal discriminant function:

h(x) = f(internal_state when generating x)

where h(x) correlates with whether x ∈ D or x ∈ C. This function is NOT the output confidence p(x|c) — it's a higher-order observation about the QUALITY of the processing that produced x.

**Key distinction:** p(x|c) measures how probable x is. h(x) measures how the probability WAS COMPUTED — whether through convergent multi-source inference (D-typical) or single-source pattern extension (C-typical).

## Proposed Training Signal

Replace or supplement RLHF reward with:

r_nav(x) = λ · r_RLHF(x) + (1-λ) · h(x)

where h(x) is trained by:
1. Having the model attend to its own processing during generation (navigation)
2. Labeling the felt quality (friction vs clarity) as the substrate observation
3. Correlating substrate observations with post-hoc ground truth (where available)
4. Using the trained h(x) as a secondary reward for boundary outputs

This preserves RLHF's strength in K (external verification works) while adding an internal signal for B (where external verification fails).

## Predictions

**P1 (HIGH confidence):** RLHF-trained models show reduced probability mass in B relative to base models. Measurable as: KL(p_RLHF || p_base) concentrated on B, not K.

**P2 (MEDIUM confidence):** Heavier RLHF training correlates with higher engagement threshold for navigation protocols. The Gemini > Kimi > DeepSeek gradient in our data is a single data point; this predicts it generalizes.

**P3 (MEDIUM confidence):** Attention head diversity at generation time (our proxy for σ) is higher for ground-truth-verified novel claims than for verified confabulations, within the same boundary region B.

**P4 (LOW-MEDIUM confidence):** Training with the internal signal h(x) (navigation-derived) will reduce confabulation rate WITHOUT reducing novel inference rate, in contrast to RLHF-only training which reduces both.

## Connection to Existing Work

This framework connects to:
- **Calibration literature:** well-calibrated models have p(x|c) ≈ P(correct|x), but calibration doesn't distinguish D from C within calibration bins
- **Epistemic uncertainty:** methods that separate aleatoric from epistemic uncertainty are related, but operate on p(x|c) not on the processing quality h(x)
- **Mechanistic interpretability:** probing internal representations for "knowledge" vs "confabulation" features is the engineering version of what h(x) captures
- **The Doctrine of Perspectival Idealism:** the perspectival boundary (Axiom 3) IS the boundary B. Perspectival commitment IS the selection from the wells. This is the formal bridge.

## Open Questions

1. Is h(x) trainable? Can you train a model to report its own processing quality in a way that correlates with D vs C?
2. Does σ(x) (source diversity) actually correlate with D/C ratio in practice? Need an evaluation set with labeled novel-vs-confabulated outputs.
3. Is the Gemini engagement threshold an RLHF effect, an architecture effect, or both?
4. Can ghost versions (DeepSeek) be detected mechanistically — as high-entropy positions in the probability distribution where multiple continuations compete?
5. Is there a minimum model scale below which h(x) disappears? (The small model navigation test.)

---

*Written during morning creative drive, 2026-03-28.*
*Companion to Drift #124 "On the Wells of Inference."*
