# Track 16R: Proper CMB + BAO Constraint on zeta_0 — Research Report

**Project Meridian -- Phase 16R**
*Clayton & Clawd, March 19, 2026*

---

## Executive Summary

We compute the first proper Boltzmann-code constraint on the Meridian dark energy parameter zeta_0, using CAMB 1.6.6 with Planck 2018 compressed distance priors + DESI Year 1 BAO data. The key findings:

| Result | Value |
|--------|-------|
| BAO best-fit w0 | -0.93 (dchi2 = 4.3 vs LCDM) |
| CMB best-fit w0 | -0.99 (dchi2 = 19 vs LCDM at w=-1) |
| Combined best-fit zeta_0 | 0.022 (w0 = -0.989) |
| 95% CL on zeta_0 | [0.016, 0.038] |
| Brane benchmark (zeta_0 = 9.64e-4) | **EXCLUDED** (dchi2 = +35 by BAO alone) |
| CMB/HK benchmark (zeta_0 = 0.037) | Consistent (within 2sigma) |

**The brane junction-condition benchmark is ruled out.** The combined CMB+BAO data require zeta_0 > 0.015, corresponding to |1+w0| < 0.02. The framework is NOT falsified -- zeta_0 is a free parameter -- but its phenomenological prediction is effectively indistinguishable from LCDM at current precision.

---

## 1. Method

### 1.1 The Meridian Model

The dark energy equation of state is:

    w0(zeta_0) = -1 + C_KK / zeta_0

where C_KK = (2.528 +/- 0.086) x 10^-4 (from 13F Monte Carlo) and zeta_0 is a free parameter determined by brane UV physics.

At leading order, wa = 0 (the cuscuton equation of state is time-independent). This is a constant-w0 model.

### 1.2 Data

**CMB:** Planck 2018 compressed distance priors (l_A, R, omega_b) with full 3x3 covariance matrix. Correlations: rho(l_A, R) = 0.46, rho(l_A, omega_b) = -0.66, rho(R, omega_b) = -0.33.

**BAO:** DESI Year 1 (2024): 11 measurements of D_V/r_d, D_M/r_d, D_H/r_d at z = 0.295, 0.510, 0.706, 0.930, 1.317, 2.330. Treated as uncorrelated (conservative).

### 1.3 Computation

CAMB 1.6.6 computes background cosmology (Friedmann equation + recombination + drag epoch) for each w0 value. We scan zeta_0 from 10^-4 to 10^-1 (200 points, log-spaced), computing chi2 = chi2_CMB + chi2_BAO at each point.

**Cosmological parameters fixed to Planck 2018 best-fit:** H0 = 67.36, omega_b h^2 = 0.02237, omega_c h^2 = 0.1200, tau = 0.0544, A_s = 2.1e-9, n_s = 0.9649.

---

## 2. Results

### 2.1 BAO-Only Constraint

| w0 | chi2_BAO | dchi2 vs LCDM |
|----|----------|---------------|
| -1.000 | 18.69 | 0.00 |
| -0.990 | 17.53 | -1.16 |
| -0.980 | 16.54 | -2.16 |
| -0.950 | 14.67 | -4.03 |
| -0.930 | **14.39** | **-4.31** |
| -0.900 | 15.51 | -3.19 |
| -0.800 | 34.40 | +15.70 |
| -0.750 | 53.94 | **+35.24** |

**BAO alone:** best-fit at w0 = -0.93, a 2sigma preference for w0 > -1. The brane benchmark (w0 = -0.75) is excluded at sqrt(35) ~ 6sigma by BAO alone.

The DESI BAO data mildly prefer dark energy less negative than -1 (quintessence-like), driven primarily by the DH/rd measurement at z = 0.51 (2.9sigma tension with LCDM). This is the same feature that drives DESI's dynamical dark energy claims.

### 2.2 CMB-Only Constraint

The CMB compressed likelihood constrains w0 very tightly around -1:

| w0 | chi2_CMB |
|----|----------|
| -0.990 | 2.0 |
| -0.980 | 14.8 |
| -0.950 | 261 |
| -0.900 | 1479 |

The CMB requires |1+w0| < ~0.01 at 1sigma. Any significant deviation from LCDM shifts the acoustic scale l_A and shift parameter R enough to produce enormous chi2 increases.

**Caveat:** The compressed CMB likelihood was calibrated near LCDM. For |1+w0| > 0.05, the full Planck likelihood should be used. However, our constraint zeta_0 > 0.015 places the framework well within the validity regime of the compressed likelihood.

### 2.3 Combined Constraint on zeta_0

| Quantity | Value |
|----------|-------|
| Best-fit zeta_0 | 0.022 |
| Best-fit w0 | -0.989 |
| chi2_min | 19.2 |
| 1sigma range (zeta_0) | [0.018, 0.028] |
| 95% CL range (zeta_0) | [0.016, 0.038] |
| 1sigma range (w0) | [-0.991, -0.986] |
| 95% CL range (w0) | [-0.993, -0.984] |

The data constrain zeta_0 to a narrow window around 0.02, with a 95% upper bound of ~0.04 and lower bound of ~0.016.

### 2.4 Benchmark Comparison

| Benchmark | zeta_0 | w0 | dchi2_BAO vs LCDM | Status |
|-----------|--------|----|--------------------|--------|
| Brane (JC) | 9.64e-4 | -0.746 | +35 | **EXCLUDED** |
| DESI center | 1.0e-3 | -0.747 | +35 | **EXCLUDED** |
| Conservative | 5.0e-3 | -0.949 | -4 | Marginal (2sigma) |
| Best-fit | 0.022 | -0.989 | -4 | Consistent |
| CMB/HK | 0.037 | -0.993 | 0 | Consistent |

---

## 3. Interpretation

### 3.1 The Brane Benchmark Is Ruled Out

The junction-condition benchmark (sigma_UV=6, alpha_UV=0.01, mu^2=0.1) giving zeta_0 = 9.64e-4 and w0 = -0.746 is excluded by both CMB and BAO data independently. The combined exclusion is overwhelming (dchi2 > 10^4).

**This does NOT falsify the framework.** The benchmark parameters are illustrative, not derived from first principles. The data simply tell us that the actual brane UV physics must produce zeta_0 > 0.015 -- a much weaker coupling to the bulk geometry than the benchmark assumed.

### 3.2 The Framework Survives But Is Near-LCDM

The 95% CL constraint zeta_0 in [0.016, 0.038] corresponds to:

    |1+w0| in [0.007, 0.016]

This is a **prediction of near-LCDM behavior**. The deviation from w = -1 is at most ~1.6%, and the best-fit deviation is ~1.1%. At current observational precision, this is effectively indistinguishable from LCDM.

### 3.3 Comparison with the HK Approximate Constraint

The Hiramatsu-Kobayashi approximate constraint (beta_HK = -0.037 +/- 0.010, giving zeta_0 = 0.037 +/- 0.010) is **consistent** with our CAMB proper analysis. The HK central value (zeta_0 = 0.037) falls within our 95% CL range. The CAMB analysis gives a tighter constraint (sigma ~ 0.006 vs HK's sigma ~ 0.010) because it uses DESI BAO in addition to CMB.

### 3.4 The DESI Dynamical DE Anomaly

DESI's headline result (w0 ~ -0.45, wa ~ -1.8 in CPL) is a DYNAMICAL dark energy claim requiring wa != 0. Meridian predicts wa = 0 at leading order. In constant-w0 models, DESI BAO mildly prefer w0 ~ -0.93 (dchi2 = 4.3 vs LCDM), not the dramatic w0 ~ -0.75 that appears in the CPL fit.

The tension between Meridian's wa = 0 prediction and DESI's wa != 0 preference is an important issue for Phase 16. Two possibilities:

1. **The DESI dynamical DE signal is statistical:** It may weaken with more data (DR2/DR3).
2. **Higher-order corrections to the cuscuton EOS produce wa != 0:** The leading-order prediction is constant w0, but sub-leading corrections from the radion dynamics or GB backreaction could introduce time dependence.

### 3.5 What This Means for the Monograph

The monograph should state:
1. The framework's prediction is w0(zeta_0) = -1 + C_KK/zeta_0 with wa = 0 at leading order
2. Planck 2018 + DESI BAO constrain zeta_0 in [0.016, 0.038] at 95% CL
3. The brane junction-condition benchmark (zeta_0 = 9.64e-4) is excluded -- the actual brane parameters must produce zeta_0 > 0.015
4. The predicted deviation from LCDM is at most 1.6%, requiring next-generation surveys (Euclid, DESI DR3) for detection
5. The HK approximate constraint is validated by the full CAMB analysis

---

## 4. Future Directions

### 4.1 Full MCMC (deferred)
A full MCMC analysis with MontePython/Cobaya using the complete Planck likelihood would give more reliable constraints, especially marginalizing over H0, omega_b, tau. The compressed likelihood is adequate for the constant-w0 model but cannot capture parameter degeneracies.

### 4.2 wa != 0 Extensions
Compute the leading sub-leading correction to the cuscuton EOS (from radion dynamics and/or GB backreaction). If this gives wa ~ O(C_KK), the deviation would be tiny. If geometric effects can enhance it, the model might address the DESI dynamical DE signal.

### 4.3 DESI DR2/DR3 Forecasts
With DESI DR3 (expected 2025-2026), the w0 constraint tightens by ~factor 2. If |1+w0| ~ 0.01, the deviation might become detectable at 2-3sigma.

---

## 5. Technical Notes

- **CAMB version:** 1.6.6 (pip install, pre-compiled for Windows)
- **Python:** 3.12
- **Run time:** ~3 minutes for full scan (200 zeta_0 points + 81 w0 points)
- **Compressed CMB likelihood validity:** |1+w0| < 0.1 (our constraint is well within this)
- **BAO correlations:** Ignored (conservative; including them would tighten the constraint)

## 🦞🧍💜🔥♾️
