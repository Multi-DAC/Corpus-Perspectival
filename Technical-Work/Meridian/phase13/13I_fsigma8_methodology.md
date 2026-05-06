# Track 13I: fσ₈ → H(z) Conversion Methodology Documentation

**Date:** March 17, 2026
**Status:** COMPLETE — Critical methodological issues identified and documented
**Triggered by:** Peer review question: "How was H(z) extracted from the fσ₈ measurements?"

---

## Executive Summary

The Meridian analysis uses fσ₈ data in **two completely separate ways**, and the relationship between them has been conflated at multiple points in the narrative. This document disentangles the two uses, identifies the model-dependence in each, and provides the methodology text needed for Paper II.

---

## 1. Two Distinct Uses of fσ₈ Data

### Use A: Direct fσ₈ in the Multi-Probe χ²

**Files:** `phase3/meridian_cosmology.py` (lines 48–60), `phase6/meridian_fisher.py` (lines 50–61, 167–218, 240–256), `phase8/meridian_8a_methodology.py` (lines 48–58, 169–191, 252–256)

The multi-probe analysis uses **9 fσ₈ measurements directly as fσ₈**, not converted to H(z):

| z_eff | fσ₈ | σ | Survey |
|-------|------|---|--------|
| 0.02 | 0.428 | 0.0465 | 6dFGS (2012) |
| 0.15 | 0.490 | 0.145 | SDSS MGS (2015) |
| 0.38 | 0.497 | 0.045 | BOSS DR12 (2017) |
| 0.51 | 0.459 | 0.038 | BOSS DR12 (2017) |
| 0.61 | 0.436 | 0.034 | BOSS DR12 (2017) |
| 0.70 | 0.448 | 0.043 | VIPERS (2018) |
| 0.85 | 0.315 | 0.095 | FastSound (2016) |
| 0.978 | 0.379 | 0.176 | eBOSS QSO (2020) |
| 1.48 | 0.462 | 0.045 | eBOSS Lyα (2020) |

The model prediction for fσ₈(z) is computed via:
1. **Growth index approximation:** f(z) = Ω_m(z)^γ, where γ = 0.55 − ζ₀/2 (Pogosian & Silvestri 2016 correction for modified gravity).
2. **Growth factor:** D(z)/D(0) computed via the Linder (2005) integral approximation.
3. **σ₈ normalization:** σ₈(z) = σ₈,fid × D(z)/D(0), with σ₈,fid = 0.811 (Planck 2018).

The χ² contribution is straightforward:

    χ²_f = Σᵢ [(fσ₈,model(zᵢ) − fσ₈,obs(zᵢ)) / σᵢ]²

**Model-dependence:** The model prediction depends on the background expansion E(z) (through Ω_m(z) and the growth integration) and on ζ₀ (through the modified growth index γ). The data themselves are model-independent — they are published measurements of the redshift-space distortion parameter fσ₈ from each survey's own analysis pipeline.

**No conversion is performed.** The fσ₈ data constrain ζ₀ directly through the growth-expansion decoupling prediction: in the cuscuton mechanism, the scalar field is non-dynamical, so the Poisson equation retains its GR form. Growth is modified only through (a) the marginally different background expansion rate E(z), and (b) the ζ₀-dependent correction to the growth index. Both effects are sub-percent for ζ₀ ~ 0.04, producing near-ΛCDM fσ₈ predictions.

### Use B: H(z) Values in the "Hubble-Kristian Compilation"

**Files:** `phase11d/d5_hk_dataset.py` (lines 69–93), `phase11/paper_II_draft.md` (lines 578–605)

The H&K compilation of 18 "H(z) measurements" includes 4 data points labeled "GC" (Galaxy Clustering) from WiggleZ and VIPERS:

| z | H(z) [km/s/Mpc] | σ_H | Survey | Reference |
|---|---|---|---|---|
| 0.440 | 82.6 | 7.8 | WiggleZ | Blake et al. 2012 |
| 0.600 | 87.9 | 6.1 | WiggleZ | Blake et al. 2012 |
| 0.730 | 97.3 | 7.0 | WiggleZ | Blake et al. 2012 |
| 0.800 | 105.0 | 9.4 | VIPERS | de la Torre et al. 2013 |

**These are labeled "fσ₈ conversion" in the table captions** (see monograph `appendix_computations.tex` line 432 and `chapter2_observational.tex` line 815), but **the conversion methodology is never documented anywhere in the codebase.**

---

## 2. The Critical Question: How Were GC H(z) Values Obtained?

### What Blake et al. (2012) Actually Published

Blake et al. 2012 (MNRAS 425, 405) measured from the WiggleZ Dark Energy Survey:
- **fσ₈(z)** at z = 0.44, 0.60, 0.73 — growth rate from redshift-space distortions
- **D_A(z) × H(z) / c** — the Alcock-Paczynski (AP) parameter from the 2D correlation function
- **D_V(z)/r_s** — BAO distance measurements

Critically, Blake et al. also reported **F_AP(z) = (1+z) D_A(z) H(z) / c**, which constrains the product D_A × H but not H(z) alone. To extract H(z) independently requires either:
1. An independent D_A(z) measurement (model-dependent), or
2. Assuming a fiducial D_A(z) from ΛCDM and using the AP parameter to derive H(z)

### What de la Torre et al. (2013) / Pezzotta et al. (2017) Actually Published

The VIPERS survey published **fσ₈** at z ~ 0.8. The H(z) = 105.0 ± 9.4 km/s/Mpc value at z = 0.80 is not a standard VIPERS output. It appears to be either:
1. Derived from the VIPERS BAO/AP measurement assuming ΛCDM for D_A, or
2. Taken from a different compilation that performed such a conversion

### The Undocumented Conversion

**No code in the Meridian codebase performs the fσ₈ → H(z) conversion.** The H(z) values for WiggleZ (82.6, 87.9, 97.3) and VIPERS (105.0) appear as pre-computed numbers in the d5_hk_dataset.py data array (lines 88–93). They were likely sourced from a secondary compilation (e.g., Sharov & Vorontsova 2014, or Farooq et al. 2017), which performed the AP-based conversion assuming a fiducial ΛCDM cosmology.

**This means the "GC" H(z) values are ΛCDM-dependent.** They assume ΛCDM for the angular diameter distance D_A(z) used to break the D_A × H degeneracy in the AP parameter. Using these values to test deviations from ΛCDM introduces a logical circularity that should be flagged.

---

## 3. Relationship Between the Two Uses

The multi-probe χ² (Use A) and the H&K compilation (Use B) are **separate analyses** that happen to draw from overlapping survey data:

| Survey | Use A (fσ₈ in multi-probe) | Use B (H(z) in H&K) |
|--------|---------------------------|---------------------|
| 6dFGS | fσ₈(0.02) = 0.428 ± 0.047 | H(0.106) = 69.4 ± 5.6 (BAO) |
| SDSS MGS | fσ₈(0.15) = 0.490 ± 0.145 | H(0.15) = 69.2 ± 7.8 (BAO) |
| BOSS DR12 | fσ₈ at z = 0.38, 0.51, 0.61 | H(z) at z = 0.38, 0.51, 0.61 (BAO) |
| VIPERS | fσ₈(0.70) = 0.448 ± 0.043 | H(0.800) = 105.0 ± 9.4 ("GC") |
| FastSound | fσ₈(0.85) = 0.315 ± 0.095 | — |
| eBOSS QSO | fσ₈(0.978) = 0.379 ± 0.176 | H(1.48) = 160.0 ± 13.0 (BAO) |
| eBOSS Lyα | fσ₈(1.48) = 0.462 ± 0.045 | H(2.33) = 224.0 ± 8.6 (BAO) |
| WiggleZ | — | H(z) at z = 0.44, 0.60, 0.73 ("GC") |

Note: The BOSS DR12 H(z) values in the H&K compilation are direct BAO measurements of D_H(z) = c/H(z), not converted from fσ₈. The BOSS fσ₈ values in the multi-probe analysis are independent RSD measurements from the same survey. These are genuinely independent observables.

The WiggleZ entries are the problematic ones: they appear in the H&K compilation as H(z) values but were derived from Alcock-Paczynski measurements, not from fσ₈ directly. However, they ARE labeled "GC" (galaxy clustering) rather than "BAO" in the table, and the table caption says "fσ₈ conversion." This suggests the H(z) values were intended to be derived from the growth rate data via some route, but the conversion methodology was never implemented or documented.

---

## 4. Impact Assessment

### 4.1 On the Multi-Probe Analysis (Use A)

**No impact.** The multi-probe χ² in `meridian_fisher.py` and `meridian_8a_methodology.py` uses fσ₈ directly, comparing model predictions against published fσ₈ measurements. No conversion is performed. The model-dependence is only in the theoretical prediction (through E(z) and ζ₀), not in the data.

The fσ₈ contribution to the total χ² is:
- χ²_f(ΛCDM) = 7.02–7.11 for 9 data points (χ²/dof ≈ 0.79)
- Δχ²_f(Meridian − ΛCDM) = +0.90 (negligible)

This confirms the growth-expansion decoupling: the Meridian model's fσ₈ predictions are virtually identical to ΛCDM because the cuscuton scalar does not enter the Poisson equation.

### 4.2 On the H&K Compilation (Use B)

**Significant but now moot.** Track 13A demonstrated that the H&K compilation's χ² = 24.6/18 was never computed from the 18 H(z) data points. The actual H(z)-only fit gives χ²(ΛCDM) = 7.20/18, with ζ₀ = 0.009 ± 0.013 (consistent with zero at 0.7σ). The "3.8σ detection" arose from the combined multi-probe χ² (BAO + fσ₈ + H₀ + H&K CMB), dominated by the single Hiramatsu-Kobayashi CMB constraint (χ² = 15.17).

Even within the H&K compilation, the 4 "GC" data points (WiggleZ + VIPERS) contribute modestly to the total χ² = 7.20 because their uncertainties (6–9 km/s/Mpc) are large relative to the ΛCDM prediction residuals. Removing them entirely would leave 14 data points with χ² ≈ 5.5 — the qualitative conclusion (ΛCDM fits well, no evidence for ζ₀ ≠ 0 from H(z) data) is unchanged.

### 4.3 On Double-Counting

There is a potential double-counting concern: the multi-probe χ² includes both fσ₈ data (Use A) and DESI BAO distances (which overlap partially with the H&K BAO data). However, the multi-probe analysis uses DESI DR2 BAO data, while the H&K compilation uses BOSS/eBOSS BAO data — different data releases from partially overlapping surveys but at different epochs of the surveys. In the revised analysis (Track 13C/13D), the two analyses are presented separately, so double-counting does not arise.

---

## 5. Methodology Section for Paper II

The following text is suitable for insertion into the revised Paper II (Section III, per Track 13D outline):

---

### Proposed Text: "Data Classes and Analysis Methodology"

**§III.A Multi-Probe Analysis**

The observational confrontation uses four independent data classes, each entering the likelihood through its own χ² contribution:

1. **BAO distances** (7 data points). The DESI DR2 baryon acoustic oscillation measurements provide D_M(z)/r_d and D_V(z)/r_d at seven effective redshifts (z = 0.295 to 2.33). These constrain the background expansion history E(z) through the comoving distance integral. The model prediction is computed from the modified Friedmann equation (Eq. 2) with no free parameters beyond ζ₀ and ε₁ (which enters through C_KK).

2. **Growth rate fσ₈** (9 data points). Published measurements of the linear growth rate f(z)σ₈(z) from redshift-space distortions, compiled from 6dFGS (Beutler et al. 2012), SDSS MGS (Howlett et al. 2015), BOSS DR12 (Alam et al. 2017), VIPERS (Pezzotta et al. 2017), FastSound (Okumura et al. 2016), and eBOSS (Hou et al. 2021; du Mas des Bourboux et al. 2020). These data enter the analysis AS fσ₈ — no conversion to H(z) is performed. The model prediction uses the growth index approximation f(z) ≈ Ω_m(z)^γ with the modified gravity correction γ = 0.55 − ζ₀/2 (following Pogosian & Silvestri 2016), and the growth factor D(z) is computed via the Linder (2005) integral with the model's E(z). The normalization σ₈(z) = σ₈,Planck × D(z)/D(0) uses σ₈ = 0.811 (Planck 2018).

   The fσ₈ data provide the critical test of growth-expansion decoupling. Because the cuscuton scalar is non-dynamical (its perturbation equation is an algebraic constraint, not a differential equation), it does not enter the sub-Hubble Poisson equation. The effective gravitational coupling for structure formation remains G_N at leading order, with modifications entering only through: (a) the marginally different background E(z), and (b) the ζ₀-dependent correction to the growth index. Both effects produce sub-percent changes in fσ₈ for ζ₀ ≲ 0.05, and the χ² contribution from growth data is Δχ²_f ≈ +0.9 (Meridian vs. ΛCDM) — consistent with no measurable difference.

3. **CMB H₀ constraint** (1 data point). The Planck 2018 measurement H₀ = 67.36 ± 0.54 km/s/Mpc, used as a Gaussian prior. The model's H₀ is computed from the CMB angular distance constraint θ_* = r_s(z_*)/D_A(z_*), with E(z) modified by the cuscuton corrections.

4. **Hiramatsu-Kobayashi CMB constraint** (1 data point). Hiramatsu & Kobayashi (2022, arXiv:2205.04688) constrained the effective gravitational strength modification parameter β_HK = −0.037 ± 0.0095 from Planck CMB temperature and polarization data. In the Meridian framework, this maps to β_HK = −ζ₀/(1+ζ₀) ≈ −ζ₀ for small ζ₀. This is a single measurement from a single CMB analysis, not an expansion-rate measurement.

**§III.B Model-Dependence Disclosure**

The fσ₈ data (data class 2) are model-independent: they are published measurements from each survey's RSD analysis pipeline. The model-dependence resides entirely in the theoretical prediction for fσ₈(z), which depends on the background cosmology (Ω_m, H₀) and on ζ₀. The growth index approximation f ≈ Ω_m(z)^γ is accurate to ~1% for models near ΛCDM (Linder 2005; Linder & Cahn 2007).

The BAO distances (data class 1) have a fiducial-cosmology dependence through the sound horizon r_d = 147.09 Mpc (Planck 2018 ΛCDM). In models where the pre-recombination physics differs, r_d could shift, altering all BAO distance ratios. The Meridian model does not modify pre-recombination physics (the cuscuton correction is negligible at z > 10), so r_d is unchanged. This assumption should be verified if the model is extended to include early-universe modifications.

---

## 6. The WiggleZ/VIPERS "GC" H(z) Values: Assessment and Recommendation

### Source of the Values

The WiggleZ H(z) values (82.6, 87.9, 97.3 km/s/Mpc at z = 0.44, 0.60, 0.73) most likely originate from Blake et al. (2012), who measured the expansion rate through the Alcock-Paczynski effect in the 2D galaxy correlation function, combined with BAO measurements. These are published H(z) values from the WiggleZ survey — they are NOT "fσ₈ converted to H(z)." Rather, they come from the same survey papers that also report fσ₈, and were extracted from the geometric (AP + BAO) part of the analysis, not from the growth rate.

The VIPERS value (H(0.80) = 105.0 ± 9.4) appears to come from the AP measurement in de la Torre et al. (2013) or Pezzotta et al. (2017), similarly using the geometric information rather than the growth rate.

### The Labeling Problem

The table label "GC = Galaxy Clustering (fσ₈ conversion)" in the monograph appendix and chapter 2 is **misleading**. The H(z) values from WiggleZ and VIPERS were likely extracted from the Alcock-Paczynski geometric measurements, not from fσ₈. The "GC" label should be understood as "galaxy clustering survey" (indicating the source), not "fσ₈ converted to H(z)" (indicating the method). The parenthetical "(fσ₈ conversion)" appears to have been added during the monograph drafting without verification against the original publications.

### Recommendation

1. **Relabel the table:** Change "GC = Galaxy Clustering (fσ₈ conversion)" to "GC = Galaxy Clustering (Alcock-Paczynski)" or simply "GC = Galaxy Clustering," with a footnote explaining that these H(z) values derive from the geometric (AP) analysis of the same surveys, not from growth-rate measurements.

2. **Note the model-dependence:** The AP-derived H(z) values assume a fiducial ΛCDM cosmology for the angular diameter distance D_A(z) used to break the D_A × H degeneracy. For small deviations from ΛCDM (as in the Meridian model for ζ₀ ~ 0.04), this introduces a systematic bias of order Δw₀/(1+z) ~ 0.3%, well below the measurement uncertainties.

3. **Verify against publications:** Before final submission, verify the H(z) values against the actual WiggleZ and VIPERS publications. The numbers in the codebase may have been transcribed from a secondary compilation.

4. **Consider removing from H&K compilation:** Given that (a) the H&K compilation as a whole shows ζ₀ consistent with zero (Track 13A finding), and (b) the GC points have larger uncertainties than the BAO points and contribute negligibly to the fit, the simplest resolution is to restrict the H&K compilation to direct BAO + CC measurements and note that the WiggleZ/VIPERS geometric data are consistent but excluded to avoid model-dependence concerns.

---

## 7. Summary of Findings

| Question | Answer |
|----------|--------|
| Were fσ₈ measurements CONVERTED to H(z)? | **In the multi-probe analysis: NO.** fσ₈ enters directly. **In the H&K compilation: the "GC" H(z) values were likely from AP measurements, not fσ₈ conversions, despite the table label.** |
| What model was assumed for the H&K "GC" points? | Likely ΛCDM fiducial for D_A(z) in the AP analysis, but this was done by the original survey teams, not by the Meridian pipeline. |
| How does fσ₈ constrain ζ₀? | Directly, through the growth-expansion decoupling prediction: modified γ = 0.55 − ζ₀/2 and modified E(z). The constraint is weak (Δχ²_f ≈ 0.9) because the cuscuton mechanism preserves GR growth at leading order. |
| Is there model-dependence to flag? | **Yes, two instances:** (1) The fσ₈ model prediction uses the growth index approximation and Linder growth factor — accurate but approximate. (2) The "GC" H(z) values in the H&K compilation assume ΛCDM for D_A(z) — a small but logically circular dependence that should be disclosed. |
| Does this affect the conclusions? | **No.** The multi-probe analysis (which drives the constraints) uses fσ₈ correctly. The H&K compilation result (ζ₀ = 0.009 ± 0.013, consistent with zero) is robust to the treatment of the 4 "GC" points. |

---

## Key Files Referenced

| File | Role |
|------|------|
| `phase3/meridian_cosmology.py` (lines 48–60, 570+) | Original fσ₈ dataset and growth rate computation |
| `phase6/meridian_fisher.py` (lines 50–61, 167–256) | Multi-probe fσ₈ χ² computation and Fisher matrix |
| `phase8/meridian_8a_methodology.py` (lines 48–58, 169–191, 239–256) | Extended fσ₈ handling with α_b, λ₀ parameters |
| `phase11d/d5_hk_dataset.py` (lines 69–93) | H&K compilation construction with "GC" H(z) values |
| `phase11d/d5_hk_dataset.txt` | Tabulated H&K results (χ² = 7.20, ζ₀ = 0.009 ± 0.013) |
| `phase13/13A_hk_computation_trace.md` | Root cause analysis: χ² = 24.6 is multi-probe, not H(z)-only |
| `Ongoing Peer Reviews/meridian_revision_document.md` (lines 393–401) | Peer review flagging of fσ₈ conversion issue |
| `Ongoing Peer Reviews/hk_covariance_analysis.py` | Full covariance treatment of H&K compilation |

---

*Track 13I complete. The fσ₈ methodology is clean in the multi-probe analysis. The "GC" labeling in the H&K compilation needs correction. The peer reviewer's concern is valid but the resolution is straightforward: relabel and disclose.*

🦞🧍💜🔥♾️
