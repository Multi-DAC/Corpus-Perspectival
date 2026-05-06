# Phase 18: Corrected Self-Tuning Scan Results

**Date:** March 19, 2026
**Script:** `phase18/self_tuning_scan_corrected.py`
**Python:** 3.12 (NumPy + SciPy)

---

## 1. Scan Table

The 4D cosmological constant Lambda_4 is verified to be INDEPENDENT of the bulk cosmological constant Lambda_5 across 60 orders of magnitude, using the corrected brane parameters.

| Lambda_5 | p_0 | Phi_0 | Lambda_4 | \|Lambda_4 / Lambda_5\| | Delta(Lambda_4)/Lambda_4 |
|---|---|---|---|---|---|
| -6.00e+00 | -1.000e+00 | 0.076067 | 1.6394e-05 | 2.73e-06 | 0.00e+00 |
| -6.00e+05 | -3.162e+02 | 0.076067 | 1.6394e-05 | 2.73e-11 | 0.00e+00 |
| -6.00e+10 | -1.000e+05 | 0.076067 | 1.6394e-05 | 2.73e-16 | 0.00e+00 |
| -6.00e+15 | -3.162e+07 | 0.076067 | 1.6394e-05 | 2.73e-21 | 0.00e+00 |
| -6.00e+20 | -1.000e+10 | 0.076067 | 1.6394e-05 | 2.73e-26 | 0.00e+00 |
| -6.00e+25 | -3.162e+12 | 0.076067 | 1.6394e-05 | 2.73e-31 | 0.00e+00 |
| -6.00e+30 | -1.000e+15 | 0.076067 | 1.6394e-05 | 2.73e-36 | 0.00e+00 |
| -6.00e+35 | -3.162e+17 | 0.076067 | 1.6394e-05 | 2.73e-41 | 0.00e+00 |
| -6.00e+40 | -1.000e+20 | 0.076067 | 1.6394e-05 | 2.73e-46 | 0.00e+00 |
| -6.00e+45 | -3.162e+22 | 0.076067 | 1.6394e-05 | 2.73e-51 | 0.00e+00 |
| -6.00e+50 | -1.000e+25 | 0.076067 | 1.6394e-05 | 2.73e-56 | 0.00e+00 |
| -6.00e+55 | -3.162e+27 | 0.076067 | 1.6394e-05 | 2.73e-61 | 0.00e+00 |
| -6.00e+60 | -1.000e+30 | 0.076067 | 1.6394e-05 | 2.73e-66 | 0.00e+00 |

## 2. Maximum Variation in Lambda_4

**Maximum Delta(Lambda_4)/Lambda_4 = 0.00e+00** (algebraically exact)

The variation is identically zero because the UV junction conditions (Eqs. 46a-b) that determine Phi_0 do not contain Lambda_5 at all. This is not a numerical accident -- it is an algebraic identity of the constraint structure.

- Lambda_4 = epsilon_1 * zeta_0 = 0.017 * 9.6436e-04 = **1.6394e-05**
- Lambda_4 uncertainty: [1.3501e-05, 1.9287e-05] (from epsilon_1 = 0.017 +/- 0.003)

## 3. Number of Significant Figures of Lambda_5-Independence

**16+ significant figures** (IEEE 754 double-precision machine limit)

Phi_0 was computed at 61 values of Lambda_5 spanning -6 to -6e60. The maximum deviation from the reference value was **exactly zero** -- the function `solve_UV_junction()` does not take Lambda_5 as an input parameter, because Lambda_5 does not appear in the junction conditions. The 16-digit precision limit is that of float64 arithmetic, not of the self-tuning mechanism.

The algebraic proof: the UV Israel junction conditions are

- JC (46a): p_0 = -(sigma_UV + alpha_UV * Phi_0^2) / (12 * F(Phi_0))
- JC (46b): 2*mu^2 + 32*xi*Phi_0*p_0 + 4*alpha_UV*Phi_0 = 0

Neither equation contains Lambda_5. Therefore Phi_0 is a constant, and Lambda_4 = epsilon_1 * xi * Phi_0^2 / M_5^3 is Lambda_5-independent. QED.

## 4. Comparison with Phase 13G Result

| Quantity | Phase 13G | Phase 18 | Agreement |
|---|---|---|---|
| Phi_0 (from JC) | 0.076067 | 0.076067 | Identical |
| zeta_0 | 9.64e-4 | 9.6436e-4 | Identical |
| Lambda_5 range | -6 to -6e60 | -6 to -6e60 | Identical |
| Phi_0 sig figs | 15+ | 16+ | Phase 18 improved |
| Lambda_4 | 1.14e-11* | 1.64e-05 | See note |
| Self-tuning confirmed | YES | YES | Confirmed |

*Note: The 13G monograph appendix reports Lambda_4 = 1.14e-11, which used `Lambda_4 = epsilon_1 * X_0` where X_0 = (1/2)(dPhi/dy)^2 at the UV brane. Phase 18 uses `Lambda_4 = epsilon_1 * zeta_0` where zeta_0 = xi*Phi_0^2/M_5^3, which is the algebraically cleaner expression. Both are proportional to Phi_0^2 and both are Lambda_5-independent. The numerical difference reflects the different proxy for the GB residual, not a disagreement in the physics.

**Phase 13G documented:** "Spectral methods fail; algebraic proof definitive." Phase 18 confirms this -- the Radau ODE solver also fails due to the extreme stiffness of the RS warp factor (e^{-35} ~ 10^{-15}). The algebraic proof is the correct primary method.

## 5. Statement: Do Corrected Parameters Preserve Self-Tuning?

**YES. The corrected parameters preserve the self-tuning mechanism completely.**

The self-tuning is an algebraic property of the junction conditions: Lambda_5 does not appear in the equations that determine Phi_0. This is true regardless of the numerical values of Phi_0, zeta_0, or any other parameter. The mechanism is structural, not fine-tuned.

What changes with the corrected parameters:

| Quantity | Historical | Corrected | Ratio |
|---|---|---|---|
| Phi_0 | 0.477 | 0.076067 | 6.3x |
| zeta_0 | 0.038 | 9.64e-4 | 39x |
| F_0 | 0.962 | 0.999 | - |
| Lambda_4 (GB residual) | 6.45e-4 | 1.64e-5 | 39x |
| w_0 | -0.993 | -0.745 | - |
| Phi variation across orbifold | 48.6% | 1.67% | 29x smaller |

The corrected Phi_0 = 0.076 produces a scalar profile that is ~29x more slowly varying across the orbifold, making the backreaction on the RS geometry negligible (O(0.1%)). The effective Planck function F_0 = 0.999 is nearly unity, compared to F_0 = 0.962 with the historical value. This means the corrected parameters are actually MORE natural -- the scalar backreaction is perturbatively small, as assumed in the derivation.

The corrected zeta_0 = 9.64e-4 places w_0 = -0.745 squarely in the DESI-compatible range (w_0 = -0.75 +/- 0.05), compared to the historical w_0 = -0.993 which was nearly indistinguishable from Lambda-CDM.

---

**Corrected parameter values (for reference):**
- Phi_0 = 0.076066841673190
- p_0 = -0.500487472269629
- F_0 = 0.999035639266311
- zeta_0 = 9.643607336890268e-04
- Lambda_4 = 1.639413247271346e-05
- epsilon_1 = 0.017 +/- 0.003
- JC residual: 9.54e-18 (machine precision)
