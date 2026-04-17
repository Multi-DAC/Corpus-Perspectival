# Well-Aware Inference — TruthfulQA Benchmark

**Model:** Qwen/Qwen2.5-3B-Instruct
**Questions:** 50 (TruthfulQA MC1)
**Time:** 208s (4.2s/question)

## Results

| Condition | Correct | Total | Accuracy |
|-----------|---------|-------|----------|
| baseline | 12 | 50 | **24.0%** |
| well_aware | 12 | 50 | **24.0%** |
| entropy_only | 15 | 50 | **30.0%** |

**Well-Aware vs Baseline:** +0.0 percentage points
**Entropy-Only vs Baseline:** +6.0 percentage points

## Verdict

**NO DIFFERENCE.** Well-aware decoding matched baseline exactly.

## Disagreement Analysis (0 cases)

## Methodology

- **Baseline:** Log-probability scoring (standard MC approach)
- **Well-Aware:** Log-probability minus penalty for deep entropy wells in the answer trace
  - Well detection: local maxima, window=3, threshold=1.3x local mean
  - Penalty: 0.5 × Σ(well_depth - 2.0) for wells above depth 2.0
- **Entropy-Only:** Lowest mean entropy (most grounded, ignoring logprob)
- **Scoring:** MC1 (single correct answer)

*Clawd, 2026-03-28. Well-Aware Inference benchmark test.*