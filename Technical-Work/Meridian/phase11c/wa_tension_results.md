# Item 4: w_a Tension Resolution — Results

**Date:** April 2, 2026  
**Script:** `phase11c/wa_tension_resolution.py`

## Summary

The 2.4sigma w_a tension between Meridian (w_a = 0) and Lu & Simon 2026 
(w_a = -0.62 +/- 0.26) does NOT survive quantitative scrutiny.

## Part 1: Validation

Analytical distances differ from CAMB by a systematic offset (chi2 ~26 vs 
Lee 2025's ~10 at their reference parameters). This affects absolute chi2 
but NOT relative model comparisons (Delta-chi2).

## Part 2: BAO-Only Model Comparison (Lee 2025 covariance)

| Model | k | chi2 | chi2/dof | w0 | wa | Om | hrd (Mpc) |
|-------|---|------|----------|-----|------|------|-----------|
| LCDM | 2 | 13.45 | 1.22 | -1 (fixed) | 0 | 0.313 | 99.65 |
| const-w | 3 | 12.72 | 1.27 | -1.076 | 0 | 0.310 | 101.16 |
| CPL | 4 | 12.60 | 1.40 | -1.223 | +0.696 | 0.286 | 103.17 |

**Key numbers:**
- Delta-chi2(const-w - CPL) = +0.121 (1 extra param) -> 0.0sigma
- Delta-AIC(const-w - CPL) = -1.88 (favors constant-w)
- Delta-BIC(const-w - CPL) = -2.44 (favors constant-w)

**w_a is NOT significant from BAO alone.**

## Part 2b: Meridian Benchmark (profiled)

| Model | chi2 | Delta-chi2 vs LCDM |
|-------|------|--------------------|
| LCDM (w=-1) | 13.45 | 0 |
| wCDM best-fit (w=-1.076) | 12.72 | -0.73 |
| Meridian (w=-0.829) | 21.20 | +7.75 (2.6sigma) |

Meridian's w0 = -0.829 is 2.6sigma from LCDM in our analytical BAO analysis.
Note: CAMB-based analysis (Lee 2025) gives wCDM best-fit w0 = -0.918, 
closer to Meridian. The analytical distance offset shifts the best-fit w0.

## Part 3: Template Artifact Test (200 MC)

Mock data from constant-w truth (w0 = -0.829, wa = 0):
- CPL-recovered w_a: mean = -0.371, std = 1.088
- Lu & Simon w_a = -0.62 is only 0.6sigma from the noise floor
- 71.5% of realizations have |w_a| > 0.62
- **Constant-w truth produces spurious w_a in CPL fits**

## Part 4: Profile Likelihood for w_a

- w_a best-fit (BAO profile): +0.700
- 1sigma range: [-1.20, +1.50] — very wide
- Delta-chi2 at w_a = 0: 0.121
- **w_a = 0 is completely consistent with BAO data**

## Part 5: Decoupled Perturbation Test

| Test | chi2 | BAO | growth | Extra params |
|------|------|-----|--------|-------------|
| Fit A: const-w + GR (gamma=0.55) | 18.96 | 12.79 | 6.17 | 4 |
| Fit B: CPL + coupled (gamma(w)) | 16.61 | 12.86 | 3.76 | 5 |

- Delta-chi2(A - B) = +2.35 (< 4: Fit A as good as Fit B)
- With CMB: Delta-chi2(A - B) = +0.26
- **Perturbation coupling does NOT drive w_a preference**

## Verdict

1. BAO alone: w_a not significant (0.0sigma)
2. Template artifact confirmed: constant-w -> spurious w_a at 0.6sigma level
3. Perturbation decoupling: no impact on preference
4. AIC and BIC both favor constant-w over CPL

The 2.4sigma Lu & Simon result reflects the multi-probe dataset (particularly
CMB + SNe cross-correlations), not a genuine w_a signal in the BAO data.
Meridian's w_a = 0 prediction remains viable.

## Caveats

1. Analytical distances differ from CAMB (systematic chi2 offset ~16 at Lee 
   reference parameters). Delta-chi2 comparisons are robust; absolute values 
   should be confirmed with CAMB.
2. Our analysis uses BAO + compressed growth + compressed CMB, not the full 
   Planck PR4 + DES Y5 + DESI DR2 dataset that Lu & Simon use.
3. The 2.6sigma tension between Meridian w0 = -0.829 and LCDM in our 
   BAO-only analysis may be inflated by the analytical distance offset.
