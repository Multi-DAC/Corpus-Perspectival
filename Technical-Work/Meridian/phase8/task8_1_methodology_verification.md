# D8.1 — Data Methodology Verification

**Track 8A | Clayton & Clawd | March 15, 2026**

## Purpose

Test whether the w₀wₐ prior (from CMB+SN combination) is biasing the Meridian model fit. If removing the prior changes the best-fit parameters or the Δχ² comparison with ΛCDM, the apparent tension with DESI could be an artifact of the prior rather than a real prediction of the model.

## Method

1. **Remove the w₀wₐ Gaussian prior** from the χ² and re-optimize all four parameters (ζ₀, γᵣ, αᵦ, λ₀) using BAO + fσ₈ + H₀ + H&K data only.
2. **Re-optimize with the prior** for direct comparison.
3. **Compare best-fit parameters, χ² breakdowns, and derived w₀wₐ** between the two cases.
4. **Direct distance comparison** at each DESI z-bin.

Eight multi-start Nelder-Mead trials per configuration, including warm starts from Phase 7 best-fit and diverse initial points spanning the full parameter space.

## Results

### Reference Values

| Configuration | BAO | fσ₈ | H₀ | H&K | w₀wₐ | Total |
|---|---|---|---|---|---|---|
| ΛCDM (with prior) | 2.27 | 7.11 | 0.01 | 15.17 | 1.82 | 26.38 |
| ΛCDM (no prior) | 2.27 | 7.11 | 0.01 | 15.17 | — | 24.56 |
| Phase 7 best (with prior) | 2.26 | 7.33 | 0.03 | 0.00 | 1.83 | 11.45 |
| Phase 7 best (no prior) | 2.26 | 7.33 | 0.03 | 0.00 | — | 9.62 |

**Δχ² vs ΛCDM = −14.93 in both cases.** The prior contributes 1.82–1.83 to both ΛCDM and the model equally, so it cancels in the comparison.

### Best-Fit Parameters

| Parameter | With prior | Without prior | Change |
|---|---|---|---|
| ζ₀ | 0.0379 | 0.0379 | 0.0000 |
| γᵣ | 0.0174 | 0.0189 | +0.0015 |
| λ₀ | 0.0000 | 0.0000 | 0.0000 |
| αᵦ | 5.82 | 4.43 | −1.39 |

The αᵦ shift is irrelevant — when λ₀ = 0, the braiding term λ₀·E^(−2αᵦ) vanishes identically, making αᵦ a flat direction. The three physics-determining parameters (ζ₀, γᵣ, λ₀) are essentially unchanged.

### Derived Equation of State (not used in fit)

| Quantity | With prior | Without prior | DESI DR2 |
|---|---|---|---|
| w₀ | −0.9948 | −0.9944 | −0.752 ± 0.058 |
| wₐ | +0.0166 | +0.0180 | −0.86 ± 0.27 |

Both cases predict w₀ ≈ −1, wₐ ≈ 0 (i.e., ΛCDM-like background). The tension with DESI is:
- w₀: 4.2σ from DESI (model too negative — too close to cosmological constant)
- wₐ: 3.3σ from DESI (wrong sign — model gives thawing, DESI sees phantom)

### Robustness of Optimization

All 8 trials without prior converge to the same χ² = 9.6225 (to 4 decimal places), with identical ζ₀ = 0.0379 and γᵣ ≈ 0.019, differing only in the degenerate αᵦ direction. The landscape has a single, clean minimum.

### Direct Distance Comparison (D/rₐ)

| z | Type | Data | ΛCDM | No prior | With prior |
|---|---|---|---|---|---|
| 0.295 | Dᵥ | 7.93 | 8.05 | 8.04 | 8.05 |
| 0.510 | Dₘ | 13.62 | 13.49 | 13.48 | 13.48 |
| 0.706 | Dₘ | 17.86 | 17.69 | 17.67 | 17.67 |
| 0.930 | Dₘ | 21.71 | 21.91 | 21.88 | 21.88 |
| 1.317 | Dₘ | 27.79 | 28.01 | 27.96 | 27.97 |
| 1.491 | Dₘ | 30.69 | 30.35 | 30.30 | 30.30 |
| 2.330 | Dₘ | 39.71 | 39.17 | 39.10 | 39.10 |

The model (γᵣ ≈ 0.02) shifts distances by < 0.3% relative to ΛCDM. Both are systematically short at high z (model predicts 39.10 vs data 39.71 at z = 2.33). The model is marginally better than ΛCDM at BAO (χ²_BAO = 2.26 vs 2.27) but this is negligible.

## Interpretation

### Where the Δχ² = −15 comes from

The entire model advantage is in **one data point**: the Hubble & Kovács (2024) ISW measurement, β_HK = −0.037 ± 0.038. ΛCDM predicts β_HK = 0 (no ISW anomaly), contributing χ²_HK = 15.17. The Meridian model, with ζ₀ = 0.038, predicts β_HK = −0.037, contributing χ²_HK = 0.00. This is a near-perfect fit to a 1σ measurement.

The remaining probes (BAO, fσ₈, H₀) are essentially neutral between the model and ΛCDM.

### What this means for the w₀wₐ tension

The tension is **real**, not an artifact. The model's background expansion is indistinguishable from ΛCDM (γᵣ ≈ 0.02 is a 2% perturbation). DESI sees w₀ ≈ −0.75, wₐ ≈ −0.9, requiring a substantial departure from ΛCDM at the background level. The minimal cuscuton cannot produce this.

### Kill condition status

Track 8A does NOT kill any track. It confirms:
1. The tension is genuine (proceed to physics modifications)
2. ζ₀ ≈ 0.038 is robust (any modification must preserve H&K)
3. The background needs to change (γᵣ ≈ 0.02 is insufficient)

## Verdict

**Track 8A: COMPLETE. Tension confirmed real. Proceed to Track 8B (Projected Weyl tensor).**

The prior is not biasing results. The model's strength (H&K fit via ζ₀) and weakness (ΛCDM-like background) are both robust features of the data, not artifacts of methodology.
