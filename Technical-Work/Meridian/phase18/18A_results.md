# 18A Results: Real-Data Decoupled Perturbation Test

**Date:** 2026-03-19
**Runtime:** 458.9s

## The Question

Does real cosmological data prefer Meridian's constant-w template (GR perturbations)
over the standard CPL parameterization (w0 + wa, perturbations coupled to w(z))?

18I showed CPL can manufacture spurious w_a from mock constant-w data (w_a biased +0.13).
Real data (Lu & Simon 2026) show w_a = -0.62. This tests whether that signal is physical
or a compromise artifact.

## Data

| Probe | Source | Points |
|-------|--------|--------|
| BAO (D_M/r_d + D_H/r_d) | DESI DR1 (arXiv:2404.03002) | 12 |
| SNe Ia (binned mu) | Pantheon+ (arXiv:2202.04077) | 20 (19 effective) |
| CMB compressed | Planck 2018 (R, l_A, omega_b) | 3 |
| Growth (fsigma8) | 6dFGS + BOSS + DESI + eBOSS | 7 |
| **Total effective** | | **41** |

## Best-Fit Parameters

| Parameter | Fit A (Meridian) | Fit B (CPL) |
|-----------|-----------------|-------------|
| w_0 | -0.9305 | -0.4000 |
| w_a | 0 (fixed) | -2.2808 |
| Omega_m | 0.3231 | 0.3397 |
| H_0 (km/s/Mpc) | 67.51 | 66.00 |
| N_params | 3 | 4 |

## Chi-Squared Breakdown

| Probe | Fit A | Fit B | Delta (A-B) | Prefers |
|-------|-------|-------|-------------|---------|
| BAO (DM+DH) | 95.55 | 74.32 | +21.24 | B |
| SNe Ia | 7.19 | 5.15 | +2.04 | B |
| CMB | 4.90 | 1.65 | +3.25 | B |
| fsigma8 | 6.74 | 7.44 | -0.70 | A |
| **Total** | **114.38** | **88.55** | **+25.82** | **B** |

## Model Comparison

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Delta chi2 (A-B) | +25.82 | Fit B (CPL) fits better by -25.8 |
| Delta AIC (A-B) | +23.82 | Fit B preferred (|DAIC| > 2 = positive evidence, > 6 = strong) |
| chi2/dof (A) | 114.38/38 = 3.010 | |
| chi2/dof (B) | 88.55/37 = 2.393 | |

## Key Diagnostic: Expansion vs Growth

| Sector | Fit A | Fit B | Prefers |
|--------|-------|-------|---------|
| Expansion (BAO+SNe+CMB) | 107.64 | 81.12 | B |
| Growth (fsigma8) | 6.74 | 7.44 | A |

## CAMB Cross-Verification

Best-fit parameters were re-evaluated with full CAMB to verify fast-model accuracy.
- Fit A: CAMB chi2 = 1326.27 (fast: 114.38)
- Fit B: CAMB chi2 = 300.37 (fast: 88.55)

## Interpretation

**CPL is STRONGLY preferred over constant-w.** DAIC = 23.82.
The best-fit w_a = -2.281. This is inconsistent with Lu & Simon (2026) w_a = -0.62.

## Comparison with 18I Mock Results

| Quantity | 18I Mock (truth: w=-0.746) | 18A Real Data |
|----------|--------------------------|---------------|
| Best-fit w_a (CPL) | +0.13 (median, biased positive) | -2.281 |
| DAIC | ~-2 (favors constant w) | 23.82 |
| Best-fit w0 (const w) | -0.746 (recovered truth) | -0.931 |
| Expansion-growth split | Growth prefers A | See table above |
