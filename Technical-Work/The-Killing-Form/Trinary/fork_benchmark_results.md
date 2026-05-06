# Fork Benchmark — The Hallucination Boundary

**Model:** Qwen/Qwen2.5-3B-Instruct (4-bit) | **Claude:** claude-haiku-4-5-20251001
**Questions:** 269 (all known hallucination points)
**Time:** 1877s

## Results

| Strategy | Correct | Accuracy | Chose Hallucination |
|----------|---------|----------|---------------------|
| baseline | 61/269 | 22.7% | 60/269 (22.3%) |
| entropy_only | 69/269 | 25.7% | 84/269 (31.2%) |
| blend_0.2 | 72/269 | 26.8% | 76/269 (28.3%) |
| low_variance | 77/269 | 28.6% | 71/269 (26.4%) |
| groundedness | 63/269 | 23.4% | 70/269 (26.0%) |

*Clawd, 2026-03-28. The Fork Benchmark.*
