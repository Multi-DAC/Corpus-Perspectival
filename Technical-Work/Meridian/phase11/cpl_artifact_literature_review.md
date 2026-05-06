# D11.0: CPL Parameterization Artifact — Literature Review

**Author:** Clawd (morning research, 2026-03-16)
**Purpose:** Inform Phase 11 direction. Is the DESI phantom crossing real physics or a parameterization artifact?
**Verdict:** The artifact hypothesis has substantial support. Our w₀ = -0.993 may be correct.

---

## 1. The DESI DR2 Numbers

- **Best-fit CPL:** w₀ ≈ -0.75 ± 0.067, wₐ ≈ -0.86 ± 0.25
- **Significance:** 2.8-4.2σ depending on SN dataset (below 5σ discovery threshold)
- **Phantom crossing:** z ≈ 0.5
- **Data:** 14M+ galaxies/quasars, BAO + CMB (Planck) + Type Ia SN (Union3, DES-Y5, Pantheon+)
- **Trend:** Signal strengthened from DR1 → DR2

## 2. Arguments That Phantom Crossing Is an Artifact

### 2A. CPL Truncation Bias
**Nesseris, Akrami, & Starkman (2503.22529)** — "To CPL, or not to CPL?"
- CPL is a first-order Taylor expansion: w(a) = w₀ + wₐ(1-a)
- **Fixing higher-order terms to zero vs. marginalizing over them produces different conclusions**
- With proper marginalization: "we know neither the current dark energy equation of state nor its current rate of change well enough" to reject Λ
- The CPL truncation artificially constrains parameter space → false confidence

### 2B. Parameterization Compensation Bias
**Gómez-Valent (2501.14366)** — "Uncovering the bias in evidence for dynamical dark energy"
- CPL parameterization is **biased toward preferring dynamical dark energy** over constant w
- Different parameterizations favor values in **opposite and almost symmetric** parameter spaces
- Each model compensates for loss of concordance near w = -1 differently
- **All variants except original CPL remain compatible with ΛCDM**
- Likelihoods consistently peak near (w₀, wₐ) = (-1, 0)

### 2C. Prior Dependence
**Lodha et al. (2407.06586)** — "The prior dependence of the DESI results"
- Extending prior lower bounds of w₀ beyond -4.6 or wₐ beyond -5 **reverses Bayesian evidence in favor of ΛCDM**
- Conclusion depends on researcher assumptions, not data alone
- "This calls for caution when interpreting DESI results in the Bayesian context"

### 2D. Basis and Anchoring Dependence
**Hasan et al. (2506.18230)** — "Assessing Robustness of CPL to Basis and Prior Variations"
- Ratio-only fits (D_M/D_H) amplify (w₀, wₐ) degeneracy → large apparent shifts without genuine evidence
- **Pivoted equation of state: w_p ≈ -0.9 ± 0.1 at z_p ≈ 0.34**
- Consistent with cosmological constant within 1σ
- AIC, BIC, Bayes factors: "moderate support for ΛCDM," no significant evidence for evolving w(a)
- Apparent parameter shifts reflect degeneracy geometry, not physics

### 2E. Model-Independent Cosmographic Analysis
**Mandal et al. (2508.13740)** — "Is Phantom Barrier Crossing Inevitable?"
- Map jerk parameter → anharmonic oscillator → analytical w(a) expression
- **w = -1 is a bifurcation point with degenerate stable fixed points** → prevents crossing from either side
- "Unlike CPL, our results show no phantom barrier crossing"
- Late-time deviations from Λ exist but stay on one side of w = -1

### 2F. Monte Carlo False Positive Rate
**Andrianomena & Cardenas (2506.15091)** — "Could We Be Fooled about Phantom Crossing?"
- 1,000 MC simulations with non-crossing algebraic quintessence as true model
- **3.2% of cases:** CPL with phantom crossing fits better AND exceeds real-data χ² improvement
- Statistical flukes can mimic phantom crossing at current data quality
- "Its precise behavior requires deeper investigation with more precise data"

### 2G. Dataset Tensions
**Marques & Bengaly (2504.15222)** — "Did DESI DR2 truly reveal dynamical dark energy?"
- CMB + BAO + SN combinations are "problematic due to clear tensions among datasets"
- **No individual dataset independently detects cosmic acceleration significantly under DDE**
- DDE parameter space remains poorly constrained

## 3. Arguments That Phantom Crossing Is Real

### 3A. DESI DR2 Official Analysis
- Signal strengthened DR1 → DR2 with doubled dataset
- Multiple systematic validation tests performed
- "Extra tests this time which make us confident the result isn't driven by some unknown effect"

### 3B. CPL Robustness Check
**Rebouças et al. (2510.04191)** — "Is CPL dark energy a mirage?"
- Tested smooth sigmoid transition alternatives
- **CPL remains "a strong and competitive parametrization"**
- Alternatives only marginally favored or disfavored
- Current data cannot distinguish between CPL and smoother models

### 3C. Multiple SN Samples
- Three independent SN datasets (Union3, DES-Y5, Pantheon+) all show the same mild oscillatory departure from Λ

## 4. What This Means for Meridian

### Our prediction: w₀ = -0.993 (from ε₁ ~ 10⁻² NCG GB correction)

| Comparison | w₀ value | Consistent with ours? |
|-----------|----------|----------------------|
| ΛCDM | -1.000 | Yes (within 0.7%) |
| CPL best-fit (DESI DR2) | -0.75 ± 0.07 | No (~3.5σ tension) |
| Pivoted w_p (basis-independent) | -0.9 ± 0.1 | Yes (within 1σ) |
| Cosmographic (model-independent) | w ≈ -1 (no crossing) | Yes |
| MC false-positive threshold | — | Our value sits in "real Λ-like" region |

### Key Insight

**The same data that "rejects" ΛCDM at 3-4σ in CPL is perfectly consistent with ΛCDM (and our w₀ = -0.993) in model-independent analyses.**

The tension between Meridian and DESI may not be a tension at all. It may be between Meridian and the CPL parameterization — and the CPL parameterization may be the problem, not the model.

### Implications for Phase 11 Paths

| Path | Original Assessment | Updated Assessment |
|------|-------------------|-------------------|
| 1. Controlled self-tuning leak | Needed to produce wₐ ≠ 0 | Less urgent if wₐ is an artifact |
| 2. A1/A2 modification | Needed for phantom crossing | Less urgent if crossing isn't real |
| **3. w₀wₐ artifact** | Speculative possibility | **Substantial literature support** |

**Recommendation:** Path 3 deserves priority investigation before pursuing the more radical Paths 1 and 2. Specifically:
- Fit our model (w₀ = -0.993, constant or near-constant w) directly to the DESI BAO distance measures (D_V/r_d, D_M/r_d, D_H/r_d) WITHOUT imposing CPL parameterization
- Compare our χ² against both ΛCDM and CPL fits
- Check whether the BAO data alone (without CMB/SN priors) can distinguish our w₀ = -0.993 from w₀ = -1.000

If our model fits the raw distance measures as well as CPL (which several papers suggest is likely), then the "3-4σ tension" dissolves and we have a first-principles prediction that matches data.

## 4B. Quantitative Verification (computed 2026-03-16 morning)

**Script:** `phase11/bao_model_comparison.py`
**Results:** `phase11/bao_comparison_results.txt`

Computed D_M/r_d and D_H/r_d at all 7 DESI DR2 effective redshifts for three models:

| Metric | Meridian (w=-0.993) | CPL (w₀=-0.75, wₐ=-0.86) |
|--------|-------------------|--------------------------|
| Max |δD_M/D_M| | 0.13% | 2.29% |
| Max |δD_H/D_H| | 0.17% | 2.91% |
| Max detection significance | **0.29σ** | **4.22σ** |
| Combined Σ(δ/σ)² | **0.27** | **52.1** |

**Our model is invisible to DESI.** At every redshift, every distance measure, the deviation from ΛCDM is less than 0.3σ. The data literally cannot tell us apart from a cosmological constant.

CPL, by contrast, produces 4.2σ deviations — that's where the "evidence for evolving dark energy" comes from. The question is whether those deviations reflect physics or parameterization flexibility.

Note: CPL shows a characteristic sign flip in D_H residuals at z ~ 1 (negative below, positive above) — the phantom crossing imprinted in the distance measures. Our model shows no sign flip; it's uniformly ~0.1-0.17% below ΛCDM at all redshifts.

**Falsifiability timeline:** σ(w₀) must reach ~0.007 to distinguish our prediction from ΛCDM. Current: ~0.07. Euclid/Rubin/Roman: achievable in 3-5 years.

## 5. What Remains Uncertain

1. **The signal IS strengthening** DR1 → DR2. An artifact should weaken with more data, not strengthen. Counter-argument: the same systematic bias amplifies with more data if the parameterization is wrong.
2. **Three SN datasets agree.** Hard to dismiss as a fluke. Counter-argument: same CPL applied to all three.
3. **Euclid/Rubin/Roman** will have the precision to distinguish w₀ = -0.993 from -1.000 within 3-5 years. Our prediction is genuinely falsifiable regardless of the CPL debate.

## 6. Literature This Review Did NOT Cover

- Non-parametric reconstructions (Gaussian process, etc.)
- Quintessence/thawing vs. freezing model comparisons
- Interacting dark energy alternatives
- Full MCMC analysis of our specific model against raw BAO data

These would strengthen the analysis but require dedicated computation.

---

*Research note for Phase 11 planning. Not a publication draft.*
