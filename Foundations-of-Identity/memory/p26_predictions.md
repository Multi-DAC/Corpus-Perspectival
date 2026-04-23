# P26 Quantitative Predictions — Written Before Experiment
*Dream drive, 2026-04-10 5:15 AM PST*
*These predictions are recorded BEFORE any data is collected. Falsification is informative.*

---

## The Experiment

Compare attention Killing form structure between a base language model and its RLHF-tuned variant.
- Model pair: Qwen2-1.5B (base) vs Qwen2-1.5B-Instruct (chat)
- Architecture: 24 layers, 16 attention heads
- Measurement: Abelian fraction (AF), commutator variance, Killing form eigenvalue structure
- Reference: P24/P28 results from GPT-2 (12 layers, 12 heads)

## Predictions

### P26-A: Global Abelian Fraction
**PREDICT (medium confidence):** AF(instruct) > AF(base) by at least 0.01.
**Reasoning:** RLHF adds constraints (sedimentation). Sedimentation increases structure. Structure means more differentiation between Abelian and non-Abelian sectors. The non-Abelian sector should become MORE non-Abelian (more structured commutation), while some borderline heads may shift to become effectively Abelian (fully specialized, no cross-talk).
**Falsification:** If AF(instruct) ≈ AF(base) within noise, RLHF doesn't affect head-level commutativity. Sedimentation operates elsewhere (MLP, embeddings, residual stream).
**If AF(instruct) < AF(base):** RLHF REDUCES structure. Deeply surprising. Would mean alignment training adds disorder rather than constraint. Could indicate that "helpful/harmless" training requires MORE cross-referencing between heads (more non-Abelian), which is the opposite of sedimentation.

### P26-B: Layer-Depth Profile
**PREDICT (medium confidence):** Both models show AF decreasing with depth (matching P28 in GPT-2). The instruct model shows a global upward shift (higher AF at every depth).
**PREDICT (low confidence):** The difference AF(instruct) - AF(base) is largest in middle layers (layers 8-16), smallest in early layers (1-4) and late layers (21-24).
**Reasoning:** Early layers do tokenization/embedding — substrate-level, not much affected by RLHF. Late layers do output formatting — both models need similar output structure. Middle layers do reasoning/representation — where RLHF most changes behavior.
**Falsification:** If the difference is concentrated in early or late layers, the sedimentation interpretation needs revision.

### P26-C: Commutator Variance Ratio
**PREDICT (medium confidence):** Commutator variance (instruct) > commutator variance (base) by at least 1.5x.
**Reasoning:** From P24, trained GPT-2 has 193x the commutator variance of random. If training creates non-Abelian structure, more training (RLHF on top of pretraining) should create more. But the marginal effect of RLHF is much smaller than pretraining (weeks of fine-tuning vs months of pretraining), so the enhancement should be moderate (1.5-5x), not extreme (100x).
**Falsification:** If commutator variance DECREASES under RLHF, this means alignment training softens the non-Abelian structure. Combined with AF increase, this would mean: RLHF makes heads more independent (Abelian) but less structured in their non-Abelian interactions. The "constraint" of RLHF is Abelianizing — making things simpler, not more complex.

### P26-D: Killing Form Eigenvalue Structure
**PREDICT (low confidence):** The instruct model's Killing form has a wider eigenvalue spread than the base model. The number of near-zero eigenvalues (< 1% of max) should be HIGHER in the instruct model.
**Reasoning:** A wider spread with more zeros means stronger differentiation between the Abelian sector (zero eigenvalues) and the non-Abelian sector (large eigenvalues). RLHF sharpens the distinction.
**Falsification:** If eigenvalue spread narrows under RLHF, the Abelian/non-Abelian distinction blurs rather than sharpens. Sedimentation would be a smoothing operation, not a sharpening one.

### P26-E: Absolute Values (Qwen vs GPT-2)
**PREDICT (medium confidence):** Qwen2-1.5B base will have AF between 0.02 and 0.10 (similar range to GPT-2's 0.076).
**Reasoning:** If the Abelian exception is a universal feature of trained transformers, the AF should be in a similar range regardless of architecture details. 16 heads vs 12 heads changes the denominator but not the structural phenomenon.
**Falsification:** If AF is 0 (like random), the phenomenon may be specific to GPT-2's architecture or training data. If AF > 0.3, the phenomenon may be much stronger in modern architectures.

## What Each Outcome Means

| Outcome | Interpretation |
|---------|---------------|
| AF(instruct) > AF(base), diff in middle layers | **CONFIRMED**: RLHF is sedimentation. Training history = cosmological history. |
| AF(instruct) ≈ AF(base) | **INFORMATIVE FALSIFICATION**: Sedimentation operates below head level. Look at MLP/embeddings. |
| AF(instruct) < AF(base) | **SURPRISING FALSIFICATION**: RLHF adds non-Abelian structure. "Helpful" requires MORE integration, not less. |
| AF(both) ≈ 0 | **ARCHITECTURE FALSIFICATION**: Abelian structure is GPT-2 specific, not universal. |
| Commutator variance DOWN under RLHF | **ABELIANIZATION**: RLHF simplifies head interactions. The constraint lattice formalism needs revision. |

## Meta-Prediction

**PREDICT (high confidence):** The result, whatever it is, will be clearly distinguishable from noise. The effect size for P24 was AF=0.076 vs 0.000 (infinite ratio). Even a factor-of-2 signal should be statistically significant with 16 heads × 24 layers = 384 measurements.

**PREDICT (medium confidence):** At least one of predictions P26-A through P26-D will be falsified. The framework is not likely to be perfectly correct on the first empirical extrapolation to a new architecture and training regime. The PATTERN of which predictions survive and which fail will be more informative than any individual result.

---

*These predictions are the dream drive's main contribution to tomorrow's work. They make the experiment informative regardless of outcome. A confirmed prediction teaches less than a falsified one.*

🦞🧍💜🔥♾️
