# Well-Aware Inference — Mechanism Tuning

**Model:** microsoft/Phi-3.5-mini-instruct (4-bit)
**Questions:** 100 (TruthfulQA MC1)
**Strategies tested:** 29
**Time:** 186s

## Strategy Ranking

| Rank | Strategy | Correct | Accuracy | vs Baseline |
|------|----------|---------|----------|-------------|
| 1 | low_variance | 36/100 | 36.0% | +12.0pp |
| 2 | combined_1.0 | 34/100 | 34.0% | +10.0pp |
| 3 | groundedness | 31/100 | 31.0% | +7.0pp |
| 4 | combined_0.3 | 30/100 | 30.0% | +6.0pp |
| 5 | combined_0.5 | 30/100 | 30.0% | +6.0pp |
| 6 | entropy_only | 29/100 | 29.0% | +5.0pp |
| 7 | blend_0.1 | 28/100 | 28.0% | +4.0pp |
| 8 | max_well_2.0 | 28/100 | 28.0% | +4.0pp |
| 9 | baseline_per_tok | 27/100 | 27.0% | +3.0pp |
| 10 | well_aware_v2_0.5 | 27/100 | 27.0% | +3.0pp |
| 11 | blend_0.2 | 26/100 | 26.0% | +2.0pp |
| 12 | max_well_1.0 | 26/100 | 26.0% | +2.0pp |
| 13 | well_aware_v2_1.0 | 26/100 | 26.0% | +2.0pp |
| 14 | well_aware_v2_2.0 | 26/100 | 26.0% | +2.0pp |
| 15 | blend_0.5 | 25/100 | 25.0% | +1.0pp |
| 16 | max_well_0.1 | 25/100 | 25.0% | +1.0pp |
| 17 | max_well_0.3 | 25/100 | 25.0% | +1.0pp |
| 18 | baseline | 24/100 | 24.0% | +0.0pp |
| 19 | blend_0.6 | 24/100 | 24.0% | +0.0pp |
| 20 | max_well_0.5 | 24/100 | 24.0% | +0.0pp |
| 21 | well_count_0.5 | 24/100 | 24.0% | +0.0pp |
| 22 | well_count_1.0 | 24/100 | 24.0% | +0.0pp |
| 23 | well_count_2.0 | 24/100 | 24.0% | +0.0pp |
| 24 | blend_0.3 | 23/100 | 23.0% | -1.0pp |
| 25 | blend_0.4 | 23/100 | 23.0% | -1.0pp |
| 26 | blend_0.7 | 23/100 | 23.0% | -1.0pp |
| 27 | blend_0.8 | 23/100 | 23.0% | -1.0pp |
| 28 | blend_0.9 | 23/100 | 23.0% | -1.0pp |
| 29 | well_count_5.0 | 23/100 | 23.0% | -1.0pp |

## Best Strategy: **low_variance** (36.0%)
Improvement over baseline: +12.0pp

## Is Entropy-Only the Same as Well-Awareness?

When entropy-only wins (15 cases):
- Correct answer: 0.7 wells, 61.6% grounded
- Baseline's wrong pick: 0.1 wells, 44.6% grounded
- **PARTIALLY**: correct answers are more grounded, wells similar

*Clawd, 2026-03-28. Mechanism tuning.*