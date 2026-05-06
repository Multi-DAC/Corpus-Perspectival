# Track 13F: CKK Derivation Chain Verification — COMPLETE

**Date:** March 17, 2026
**Status:** VERIFIED with corrections identified
**Computation:** `13F_ckk_parametric.py` (Monte Carlo, N=100,000)

---

## 1. The CKK Formula

The framework's parametric prediction:

    1 + w₀ = C / ζ₀

where the CKK constant is:

    C = (1+q₀)² Ω_DE ε₁ / [4(1-q₀)²]

### Input Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| q₀ | -0.55 +/- 0.05 | Deceleration parameter (Planck 2018 + BAO) |
| Omega_DE | 0.685 +/- 0.007 | Dark energy fraction (Planck 2018) |
| epsilon_1 | 0.017 +/- 0.003 | GB coupling (C_GB = 2/3, radiatively stable) |

### CKK Constant

    C = 2.4538 x 10^-4 +/- 8.27 x 10^-5

- Relative uncertainty: 33.7%
- Monte Carlo (100k samples): C = 2.528 x 10^-4 +/- 8.61 x 10^-5
- Analytical/MC agreement: 0.09 sigma (excellent)

### Error Budget

| Source | sigma_C | Variance fraction |
|--------|---------|-------------------|
| q₀ | 7.04 x 10^-5 | **72.5%** |
| Omega_DE | 2.51 x 10^-6 | 0.1% |
| epsilon_1 | 4.33 x 10^-5 | **27.4%** |

**Dominated by q₀ uncertainty** (not epsilon_1 as one might expect). The deceleration parameter enters quadratically in both numerator and denominator, amplifying its effect. Omega_DE is negligible. To sharpen the prediction, better q₀ measurements matter most.

---

## 2. Parametric Curve w₀(zeta_0)

| zeta_0 | w₀ (central) | 1-sigma band | 2-sigma band |
|--------|-------------|--------------|--------------|
| 0.001 | -0.7546 | [-0.830, -0.664] | [-0.885, -0.544] |
| 0.005 | -0.9509 | [-0.966, -0.933] | [-0.977, -0.909] |
| 0.010 | -0.9755 | [-0.983, -0.966] | [-0.989, -0.954] |
| 0.020 | -0.9877 | [-0.992, -0.983] | [-0.994, -0.977] |
| 0.037 | -0.9934 | [-0.995, -0.991] | [-0.997, -0.988] |
| 0.050 | -0.9951 | [-0.997, -0.993] | [-0.998, -0.991] |
| 0.100 | -0.9975 | [-0.998, -0.997] | [-0.999, -0.995] |

The curve is a hyperbola: w₀ approaches -1 as zeta_0 grows, and deviates strongly for small zeta_0.

---

## 3. Observational Constraints

### (a) CMB constraint — Hiramatsu & Kobayashi (2022)

    zeta_0 = 0.037 +/- 0.010 (from beta_HK = -0.037 +/- 0.0095)
    w₀ = -0.9925 +/- 0.0047 (full MC, propagating all uncertainties)
    w₀ median = -0.9933

This is the tightest constraint. A 4-sigma detection of beta != 0 from Planck CMB data. Predicts w₀ indistinguishable from LCDM at current precision (|1+w₀| ~ 0.007).

### (b) H(z) expansion rate data

    zeta_0 = 0.009 +/- 0.013 (18-point compilation)
    w₀ = -0.973 (central, but uncertainty is enormous)

Consistent with LCDM at 0.7 sigma. Only 75% of MC samples have zeta_0 > 0 (the constraint is consistent with zero). This provides essentially no useful constraint on its own.

### (c) Brane benchmark (junction conditions)

    zeta_0 = 0.000964 (from sigma_UV=6, alpha_UV=0.01, mu^2=0.1)
    w₀ = -0.745

This is the ONLY value derived from the actual junction conditions (Track 13B). It predicts w₀ in the DESI range — a much more interesting prediction than w₀ ~ -1.

### (d) DESI intersection

    DESI: w₀ = -0.75 +/- 0.05
    Inverted: zeta_0 = 9.82 x 10^-4 +/- 4.47 x 10^-4
    DESI band maps to zeta_0 in [8.2 x 10^-4, 1.2 x 10^-3]

**The brane benchmark zeta_0 = 0.00096 falls squarely in the DESI band.** This is the framework's most testable prediction: if the junction conditions give zeta_0 ~ 10^-3, then DESI should measure w₀ ~ -0.75.

---

## 4. Cross-checks

| Check | Result | Status |
|-------|--------|--------|
| zeta_0 = 0.038 gives w₀ = -0.993? | w₀ = -0.9935 | PASS (delta = 0.0005) |
| zeta_0 = 0.00096 gives w₀ = -0.746? | w₀ = -0.7454 | PASS (delta = 0.001) |
| Large zeta_0 limit -> -1? | w₀(1.0) = -0.99975 | PASS |
| Small zeta_0 diverges? | w₀(10^-6) = +244 | PASS (correct pole) |
| Algebraic identity (0.45/1.55)^2? | 0.08428720 both ways | PASS |

All cross-checks pass.

---

## 5. Dimensional Consistency Check

**Finding: The monograph relation Phi_0^2 = 3 zeta_0 M_Pl^2 requires k = 1/2.**

The earlier phases use the convention M_Pl^2 = M_5^3/k (absorbing factors of 2 into k). The derivation chain is:

1. Definition: zeta_0 = xi Phi_0^2 / M_5^3 with xi = 1/6
2. Therefore: Phi_0^2 = 6 zeta_0 M_5^3
3. Convention used in phases 3-11: M_Pl^2 = M_5^3/k, i.e., M_5^3 = k M_Pl^2
4. Substituting: Phi_0^2 = 6 zeta_0 k M_Pl^2
5. Monograph states: Phi_0^2 = 3 zeta_0 M_Pl^2
6. Consistency requires: 6k = 3, i.e., **k = 1/2**

Note: the standard RS result is M_Pl^2 = M_5^3/(2k) in the large-warping limit. With THAT convention, Phi_0^2 = 12k zeta_0 M_Pl^2, requiring k = 1/4. The difference is whether the factor of 2 from the y-integral is absorbed into k or not. The phases use M_Pl^2 = M_5^3/k, so k = 1/2 is the correct consistency requirement.

**The numerical verification confirms k = 1/2.** At k = 0.5, all three expressions (definition, monograph, exact chain) agree. At k = 1.0 or k = 2.0, they disagree.

**The issue is the RS Planck mass convention.** The standard RS result is:

    M_Pl^2 = M_5^3 (1 - e^{-2k pi R}) / (2k)

In the large-warping limit: M_Pl^2 ~ M_5^3/(2k). Some references absorb the factor of 2 into k or use different normalizations.

**Resolution (recommended):** The monograph should use the fundamental relation Phi_0^2 = zeta_0 M_5^3 / xi = 6 zeta_0 M_5^3 throughout, and define M_Pl^2 accordingly. This avoids the k-convention ambiguity entirely. The CKK formula uses only zeta_0, not Phi_0 or k separately, so **no physics is affected** — this is purely a notational issue.

---

## 6. Perturbative Validity

The CKK formula 1 + w₀ = C/zeta_0 is a linearized result. It breaks down when |1+w₀| is not small.

| |1+w₀| threshold | zeta_0 | w₀ | Status |
|------------------|--------|----|----|
| 0.01 | 0.0245 | -0.99 | Perturbative |
| 0.05 | 0.0049 | -0.95 | Perturbative |
| 0.10 | 0.0025 | -0.90 | Marginal |
| 0.25 | 0.00098 | -0.75 | Marginal |
| 0.50 | 0.00049 | -0.50 | BREAKDOWN |
| 1.00 | 0.00025 | 0.00 | BREAKDOWN |

**Key boundaries:**
- **Strictly perturbative:** zeta_0 > 0.005 (|1+w₀| < 0.05)
- **Marginal:** 0.0005 < zeta_0 < 0.005 (0.05 < |1+w₀| < 0.5)
- **Breakdown:** zeta_0 < 0.0005 (|1+w₀| > 0.5)

**The brane benchmark zeta_0 = 0.00096 is in the marginal regime** (|1+w₀| ~ 0.25). The linearized formula may still be approximately valid here, but a full nonlinear computation would be needed for precision. This is an important caveat for the DESI prediction.

**The CMB constraint zeta_0 = 0.037 is solidly perturbative** (|1+w₀| ~ 0.007).

**Physical mechanism:** As zeta_0 -> 0, the effective potential V_eff flattens (V''_eff -> 0), the scalar becomes massless, and the slow-roll approximation underlying the CKK formula fails. The formula has a simple pole at zeta_0 = 0, which correctly signals this breakdown — it is not a pathology but a validity boundary.

---

## 7. Key Findings Summary

### Verified
1. The CKK formula correctly reproduces w₀ = -0.993 at zeta_0 = 0.038 and w₀ = -0.746 at zeta_0 = 0.00096
2. The parametric curve w₀(zeta_0) is well-behaved across the physical range
3. Uncertainty propagation is consistent between analytical and Monte Carlo methods
4. The brane benchmark zeta_0 falls squarely in the DESI band — this is the framework's most interesting prediction

### Corrections needed
1. **Dimensional convention:** The monograph must either state k = 1/2 explicitly or use Phi_0^2 = 6 zeta_0 M_5^3 throughout (recommended)
2. **Error budget text:** The dominant uncertainty comes from q₀ (72.5% of variance), not epsilon_1 (27.4%) — the monograph should state this correctly
3. **Perturbative validity caveat:** The brane benchmark prediction w₀ ~ -0.75 is in the marginal regime of the linearized formula. The monograph should acknowledge this and note that a full nonlinear analysis would be needed for precision at zeta_0 ~ 10^-3

### The honest story (for the monograph)
The framework predicts w₀(zeta_0) = -1 + C/zeta_0 with C = (2.45 +/- 0.83) x 10^-4. Two regimes:
- **CMB regime** (zeta_0 ~ 0.04): w₀ indistinguishable from -1 at current precision. Consistent with H&K Planck constraint.
- **Brane regime** (zeta_0 ~ 10^-3): w₀ ~ -0.75, in the DESI range. Perturbatively marginal but physically compelling.

Which regime nature chooses depends on the brane physics (UV completion). This is the open question.

---

## Files

| File | Contents |
|------|----------|
| `13F_ckk_parametric.py` | Full computation (11 sections, MC propagation) |
| `13F_ckk_results.json` | Machine-readable results for downstream tracks |
| `13F_ckk_results.md` | This document |
