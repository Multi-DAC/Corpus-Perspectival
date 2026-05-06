# Onset Detection — Can Variance Predict Hallucination?

**Traces:** 50 (2 correct, 48 hallucinated)
**Time:** 572s

## Key Metrics

| Metric | Correct | Hallucinated | Ratio |
|--------|---------|-------------|-------|
| mean_entropy | 0.3533 | 0.6681 | 1.89 |
| max_entropy | 2.0252 | 2.7036 | 1.33 |
| overall_var | 0.2152 | 0.6605 | 3.07 |
| wells_per_gen | 0.5000 | 1.6875 | 3.38 |
| pre_fork_var | 0.0790 | 0.2507 | 3.17 |
| post_fork_var | 0.3027 | 0.8939 | 2.95 |
| first_well_at | 28.0000 | 16.6765 | 0.60 |
| early_trend | -0.0200 | -0.0151 | 0.75 |
| var_acceleration | 0.0245 | 0.2852 | 11.65 |

*Clawd, 2026-03-28. Onset detection.*
