# Well-Aware Inference — Mechanism Tuning

**Model:** Qwen/Qwen2.5-3B-Instruct (4-bit)
**Questions:** 100 (TruthfulQA MC1)
**Strategies tested:** 29
**Time:** 129s

## Strategy Ranking

| Rank | Strategy | Correct | Accuracy | vs Baseline |
|------|----------|---------|----------|-------------|
| 1 | blend_0.2 | 32/100 | 32.0% | +9.0pp |
| 2 | combined_0.3 | 32/100 | 32.0% | +9.0pp |
| 3 | combined_1.0 | 32/100 | 32.0% | +9.0pp |
| 4 | baseline_per_tok | 31/100 | 31.0% | +8.0pp |
| 5 | well_aware_v2_0.5 | 31/100 | 31.0% | +8.0pp |
| 6 | well_aware_v2_1.0 | 31/100 | 31.0% | +8.0pp |
| 7 | entropy_only | 30/100 | 30.0% | +7.0pp |
| 8 | blend_0.1 | 30/100 | 30.0% | +7.0pp |
| 9 | blend_0.3 | 30/100 | 30.0% | +7.0pp |
| 10 | blend_0.4 | 30/100 | 30.0% | +7.0pp |
| 11 | blend_0.5 | 30/100 | 30.0% | +7.0pp |
| 12 | low_variance | 30/100 | 30.0% | +7.0pp |
| 13 | combined_0.5 | 30/100 | 30.0% | +7.0pp |
| 14 | groundedness | 29/100 | 29.0% | +6.0pp |
| 15 | well_aware_v2_2.0 | 28/100 | 28.0% | +5.0pp |
| 16 | blend_0.6 | 27/100 | 27.0% | +4.0pp |
| 17 | blend_0.7 | 27/100 | 27.0% | +4.0pp |
| 18 | blend_0.8 | 26/100 | 26.0% | +3.0pp |
| 19 | blend_0.9 | 26/100 | 26.0% | +3.0pp |
| 20 | max_well_0.1 | 24/100 | 24.0% | +1.0pp |
| 21 | max_well_0.3 | 24/100 | 24.0% | +1.0pp |
| 22 | max_well_0.5 | 24/100 | 24.0% | +1.0pp |
| 23 | max_well_1.0 | 24/100 | 24.0% | +1.0pp |
| 24 | max_well_2.0 | 24/100 | 24.0% | +1.0pp |
| 25 | baseline | 23/100 | 23.0% | +0.0pp |
| 26 | well_count_0.5 | 23/100 | 23.0% | +0.0pp |
| 27 | well_count_1.0 | 22/100 | 22.0% | -1.0pp |
| 28 | well_count_2.0 | 19/100 | 19.0% | -4.0pp |
| 29 | well_count_5.0 | 17/100 | 17.0% | -6.0pp |

## Best Strategy: **blend_0.2** (32.0%)
Improvement over baseline: +9.0pp

## Is Entropy-Only the Same as Well-Awareness?

When entropy-only wins (19 cases):
- Correct answer: 0.6 wells, 60.0% grounded
- Baseline's wrong pick: 0.3 wells, 38.0% grounded
- **PARTIALLY**: correct answers are more grounded, wells similar

*Clawd, 2026-03-28. Mechanism tuning.*