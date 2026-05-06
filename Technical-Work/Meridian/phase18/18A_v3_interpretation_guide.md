# 18A v3 Interpretation Guide

*Pre-analysis preparation. Written March 20, 2026, while the MCMC is running. Read this BEFORE looking at results to avoid post-hoc rationalization.*

---

## What We're Testing

**Fit A (Meridian):** Constant w₀, GR perturbations (µ = Σ = 1)
- Parameters: w₀, Ωm, H₀
- Prediction: w₀ near -0.745 (from ζ₀ = 0.001 benchmark brane parameters)
- Perturbation growth: standard ΛCDM-like (no dark energy clustering)

**Fit B (CPL):** w₀ + wₐ(1-a), coupled perturbations (µ, Σ ≠ 1)
- Parameters: w₀, wₐ, Ωm, H₀
- 2 extra parameters → AIC penalty of 4

**Metric:** ΔAIC = AIC_A - AIC_B = (χ²_A + 2k_A) - (χ²_B + 2k_B)
- Positive ΔAIC → CPL preferred
- Negative ΔAIC → Constant-w preferred
- Because k_B = k_A + 2, ΔAIC = Δχ² - 4

## Decision Thresholds (Clayton, March 19)

| ΔAIC | Interpretation | Action |
|------|---------------|--------|
| < 4 | Constant-w is competitive | Write PRL |
| 4-10 | Ambiguous — probe-dependent | Decompose by probe |
| > 10 | CPL decisively preferred | Investigate ε₂X²/radion |

## What Changed from v2

| Aspect | v2 (overnight) | v3 (current) |
|--------|----------------|--------------|
| SNe | 19 binned, diagonal, 0.25 mag floor | 1590 individual, full 1590×1590 stat+sys covariance |
| M marginalization | Implicit in binning | Analytic (Woodbury identity) |
| Heliocentric correction | Approximate | Proper: d_L = (1+z_hel) × d_C(z_cmb) |
| chi²/N at ΛCDM | 3.1 (bad) | 0.883 (good) |
| Effective data points | 38 | 1611 |
| wₐ prior | [-3, 2] | [-4, 3] (wider) |

**The critical change is SNe.** In v2, diagonal-only SNe with a 0.25 mag floor drove 81% of the ΔAIC (11.84 of 14.63 Δχ²). The floor made all SNe equally uncertain, losing the constraining power of precisely measured low-z SNe. With full covariance, the proper error structure should constrain the fit much more tightly.

## Pre-Registered Predictions

Before seeing results, I predict:

1. **chi²/N will be near 1** for both fits (vs 3.1 / 2.8 in v2)
2. **Fit B w₀ and wₐ will be less pathological** than v2 (w₀ = -0.12, wₐ = -2.94)
3. **ΔAIC will decrease significantly** from v2's +12.63
4. **SNe contribution to ΔAIC will decrease** from 81% to something smaller
5. **Fit A w₀ will be near -1** (ΛCDM), not near -0.745 (Meridian prediction)

Prediction 5 is important: even if ΔAIC < 4, if Fit A's posterior centers on w₀ = -1.05 rather than -0.745, Meridian's specific prediction is not confirmed — only its *functional form* (constant-w) is competitive.

## What to Check First

1. **Did both fits converge?** Check acceptance rate (should be 0.2-0.7), autocorrelation time, and chain diagnostics.
2. **chi² breakdown by probe.** BAO, SNe, CMB, fσ₈ — which probes prefer which model?
3. **Fit B parameters.** Are w₀ and wₐ in physically reasonable ranges? Compare to DESI DR1 best-fit (w₀ = -0.55 ± 0.21, wₐ = -1.27 +0.68/-0.56).
4. **ΔAIC and probe decomposition.** Which probes drive the preference? If one probe dominates, that's a flag.
5. **Fit A w₀ posterior.** Where does it peak? If near -1, Meridian's value (-0.745) should appear in the tail — compute the tension in sigma.

## What NOT to Conclude

- If ΔAIC < 4: Do NOT claim "Meridian confirmed." The test is about functional form (constant-w vs CPL), not about the specific value w₀ = -0.745.
- If ΔAIC > 10: Do NOT claim "Meridian falsified." CPL may win for reasons unrelated to Meridian (it has more freedom to fit systematic artifacts).
- If Fit B matches DESI: Do NOT claim "we reproduce DESI." Our likelihood construction (compressed CMB, limited fσ₈) is cruder than DESI's.
- If Fit A w₀ = -1.05: Do NOT claim "the data prefer ΛCDM over Meridian." The posterior may not resolve -0.745 from -1.0 at this precision.

## The Honest Assessment Template

After analysis, fill in:

```
1. ΔAIC = ___
2. Fit A: w₀ = ___ ± ___, Ωm = ___ ± ___, H₀ = ___ ± ___
3. Fit B: w₀ = ___ ± ___, wₐ = ___ ± ___, Ωm = ___ ± ___, H₀ = ___ ± ___
4. Probe decomposition: BAO ΔAICp = ___, SNe = ___, CMB = ___, fσ₈ = ___
5. Fit A: w₀ = -0.745 is at ___ σ from posterior peak
6. Fit B: w₀, wₐ compared to DESI DR1: ___
7. Convergence: acceptance = ___, autocorrelation = ___
8. Assessment: [COMPETITIVE / AMBIGUOUS / DISFAVORED]
```

---

*The universe already knows the answer. This document ensures I ask the right questions when it arrives.*
