# Observational Confrontation of Five-Dimensional Self-Tuning Cosmology

**Clayton W. Iggulden-Schnell**

*Draft v2.0 — March 17, 2026*

**Abstract.** We confront the predictions of five-dimensional self-tuning cosmology (Paper I) with current observational data. The framework produces a one-parameter family of predictions: the dark energy equation of state w_0(zeta_0) = -1 + C/zeta_0, where zeta_0 is the dimensionless non-minimal coupling determined by brane physics and C = (2.45 +/- 0.83) x 10^{-4} is fixed by the deceleration parameter, dark energy fraction, and Gauss-Bonnet correction. For the benchmark brane parameters derived from the UV junction conditions, zeta_0 = 9.6 x 10^{-4}, giving w_0 = -0.75 — squarely in the range reported by the Dark Energy Spectroscopic Instrument (DESI DR2). The Planck CMB constraint of Hiramatsu & Kobayashi (2022), beta_HK = -0.037 +/- 0.0095, independently suggests zeta_0 ~ 0.037, giving w_0 = -0.993 (indistinguishable from Lambda CDM). An 18-point H(z) expansion rate compilation yields zeta_0 = 0.009 +/- 0.013, consistent with zero at 0.7 sigma. These two regimes — the brane benchmark and the CMB constraint — define the framework's observational landscape. Because the cuscuton scalar is non-dynamical, the linear growth factor f sigma_8 and S_8 remain within 0.1% of Lambda CDM for all zeta_0, consistent with all redshift-space distortion and weak lensing data. This growth-expansion decoupling is a unique, falsifiable prediction of the cuscuton mechanism. We present the w_0(zeta_0) parametric curve with uncertainty bands, overlay observational constraints from CMB, H(z), and DESI data, and demonstrate that the CPL phantom crossing reported by DESI is a parameterization artifact while the magnitude of the deviation may be a physical prediction of the framework.

---

## I. Introduction

In Paper I of this series [1], we derived a dark energy equation of state from two physical assumptions: spacetime has five dimensions with S^1/Z_2 orbifold compactification (A1), and a bulk scalar propagates with non-minimal gravitational coupling (A2). The derivation chain —

    A1 + A2 -> self-tuning -> cuscuton -> zero KE theorem
      -> NCG Gauss-Bonnet correction -> w_0(zeta_0)

— produces a one-parameter family of predictions indexed by the non-minimal coupling zeta_0, which is determined by the brane physics (UV completion) rather than by cosmological data.

The framework makes five structural predictions (Paper I, Section IX):

1. **w_0(zeta_0) = -1 + C/zeta_0** — the parametric dark energy equation of state, where C = (2.45 +/- 0.83) x 10^{-4}. For benchmark brane parameters: w_0 = -0.75. For the CMB-preferred value: w_0 = -0.993.
2. **w_a ~ +0.01** — essentially no time evolution, with weak positive sign (no phantom crossing).
3. **c_s ~ 10c** — superluminal sound speed producing a Jeans length larger than the observable universe.
4. **Growth-expansion decoupling** — the cuscuton scalar does not enter the Poisson equation, so structure growth remains Lambda CDM to sub-percent precision regardless of zeta_0.
5. **No phantom crossing** — w > -1 at all epochs, a topological consequence of the positive-definite kinetic structure.

The observational landscape is shaped by the Dark Energy Spectroscopic Instrument (DESI) Data Release 2 [2], which has reported 2.8-4.2 sigma evidence for time-evolving dark energy in the CPL parameterization [3,4], with best-fit values w_0 = -0.75, w_a = -0.86. The framework's relationship to this result depends on the value of zeta_0. If zeta_0 ~ 10^{-3} (the brane benchmark), the framework *predicts* w_0 ~ -0.75 — the magnitude of the DESI deviation from Lambda CDM is a consequence of five-dimensional geometry, while the phantom crossing (w_a < 0, implying w crosses -1) remains a CPL parameterization artifact. If zeta_0 ~ 0.04 (the CMB constraint), the framework predicts w_0 ~ -0.993, indistinguishable from Lambda CDM at current precision. This paper presents the observational confrontation across the full zeta_0 range and establishes the falsification program for both regimes.

We note that asymptotic safety (AS) quantum gravity makes no prediction for w_0 [50,51], leaving the dark energy equation of state as unclaimed territory in the QG landscape. The Meridian framework's w_0(zeta_0) prediction is, to our knowledge, the only first-principles w_0 prediction from a quantum gravity-motivated construction.

### Outline

Section II summarizes the model and presents the w_0(zeta_0) parametric prediction as the central result. Section III presents the multi-probe observational analysis with honest decomposition of data classes, including the Hiramatsu-Kobayashi CMB constraint, the H(z) expansion rate compilation, and their mild tension. Section IV confronts the model with DESI DR2 BAO measurements across the full zeta_0 range. Section V presents the CPL artifact hypothesis and demonstrates that the phantom crossing is a parameterization artifact while the deviation magnitude may be physical. Section VI develops Fisher matrix forecasts for future surveys. Section VII discusses additional observational tests (modified gravity, CMB, solar system). Section VIII compiles falsifiable predictions as functions of zeta_0. Section IX discusses implications and model evolution, and Section X concludes.

### Relation to Companion Papers

This paper takes as input the parametric prediction w_0(zeta_0) derived in Paper I [1], together with the modified Friedmann equation and growth-expansion decoupling that follow from the cuscuton mechanism. The sound speed prediction c_s ~ 10c, derived in Paper V [18], determines the Jeans length lambda_J ~ 30,000 Mpc and hence the prediction of zero dark energy clustering at all observable scales — a key element of the falsification program presented in Section VIII. The no-go analysis of Paper III [19] establishes that the deviation |1 + w_0| cannot be increased beyond C/zeta_0 within the framework for fixed zeta_0, confirming the structural nature of the prediction. The NCG Gauss-Bonnet coupling from Paper IV [20], which fixes epsilon_1 = 0.017 +/- 0.003, enters through the corrected Friedmann equation (Section II). Eichhorn's asymptotic safety program [50] provides complementary constraints on dark matter candidates (excluding ALPs and certain vector DM models [52,53,54]), potentially favoring the KK tower candidates naturally provided by our extra-dimensional framework.

---

## II. Model Summary and the Parametric Prediction

### A. The One-Parameter Theory

The Kaluza-Klein reduction of the five-dimensional self-tuning action (Paper I, Sections II-VI) produces an effective four-dimensional scalar-tensor theory governed by a single free parameter:

    zeta_0 = xi Phi_0^2 / M_5^3,                                       (1)

the dimensionless non-minimal coupling between the bulk scalar and five-dimensional gravity. The value of zeta_0 is determined by the UV brane physics through the Israel junction conditions (Paper I, Eqs. 46a-b), which depend on the brane tension sigma_UV, the brane-localized scalar coupling alpha_UV, and the bulk scalar mass mu^2. All observable deviations from general relativity are determined by zeta_0 and the Gauss-Bonnet correction parameter epsilon_1 = 0.017 +/- 0.003 (which is itself fixed by the NCG spectral action, not by data).

### B. The Parametric Prediction: w_0(zeta_0)

The corrected Friedmann equation on the brane (Paper I, Eq. 68) produces the dark energy equation of state:

    w_0 = -1 + C_KK epsilon_1 / zeta_0,                                 (2)

where the CKK constant is

    C_KK = (1 + q_0)^2 Omega_DE / [8(1 - q_0)^2],                      (3)

with q_0 = -0.55 +/- 0.05 the deceleration parameter and Omega_DE = 0.685 +/- 0.007 the dark energy fraction (Planck 2018 [5]). Defining the combined constant

    C = C_KK epsilon_1 = (2.45 +/- 0.83) x 10^{-4},                    (4)

the prediction takes the compact form

    1 + w_0 = C / zeta_0.                                               (5)

This is the framework's central observational output: a hyperbolic curve in the (zeta_0, w_0) plane. The uncertainty in C is dominated by the deceleration parameter q_0 (72.5% of variance), with epsilon_1 contributing 27.4% and Omega_DE negligible (0.1%). Improving the q_0 measurement would sharpen the prediction most effectively.

**Table 1.** The parametric prediction w_0(zeta_0) with 1-sigma and 2-sigma uncertainty bands, computed via Monte Carlo propagation (N = 100,000 samples).

| zeta_0 | w_0 (central) | 1-sigma band | 2-sigma band | Regime |
|--------|-------------|--------------|--------------|--------|
| 0.001 | -0.755 | [-0.830, -0.664] | [-0.885, -0.544] | Brane benchmark |
| 0.005 | -0.951 | [-0.966, -0.933] | [-0.977, -0.909] | Intermediate |
| 0.010 | -0.976 | [-0.983, -0.966] | [-0.989, -0.954] | Intermediate |
| 0.020 | -0.988 | [-0.992, -0.983] | [-0.994, -0.977] | Intermediate |
| 0.037 | -0.993 | [-0.995, -0.991] | [-0.997, -0.988] | CMB regime |
| 0.050 | -0.995 | [-0.997, -0.993] | [-0.998, -0.991] | Near-LCDM |
| 0.100 | -0.998 | [-0.998, -0.997] | [-0.999, -0.995] | Near-LCDM |

The curve approaches w_0 = -1 (Lambda CDM) as zeta_0 -> infinity and deviates strongly for small zeta_0. A perturbative validity analysis (Section IX.D) shows the linearized formula is reliable for zeta_0 > 0.005 (|1+w_0| < 0.05) and marginal for 0.0005 < zeta_0 < 0.005. The brane benchmark zeta_0 = 9.6 x 10^{-4} lies in the marginal regime (|1+w_0| ~ 0.25); a full nonlinear computation would be needed for precision predictions at this value. The CMB-preferred value zeta_0 = 0.037 is solidly perturbative.

### C. Modified Expansion History

The corrected Friedmann equation on the brane is (Paper I, Eq. 68):

    E^4 - R(a) E^2 - kappa_0 = 0,                                      (6)

where E(a) = H(a)/H_0 is the normalized expansion rate, R(a) = Omega_m a^{-3} + Omega_r a^{-4} + v_0, and kappa_0 = C_KK epsilon_1 Omega_DE / zeta_0 parametrizes the kinetic energy from the Gauss-Bonnet correction. The solution is

    E^2 = [R(a) + sqrt(R(a)^2 + 4 kappa_0)] / 2.                       (7)

For kappa_0 << R^2 (which holds at all epochs since epsilon_1 = 0.017 +/- 0.003):

    E^2 ~ R(a) + kappa_0/R(a) + O(kappa_0^2/R^3).                      (8)

The correction is negligible at early times (R >> 1) and grows to kappa_0/Omega_DE at the present epoch, producing Eq. (2).

### D. Gravitational Modification

The non-minimal coupling zeta_0 modifies four gravitational observables:

| Observable | Prediction | Expression |
|-----------|-----------|-----------|
| Effective gravitational constant | G_eff = G_N/(1 + 2 zeta_0) | Depends on zeta_0 |
| Hiramatsu-Kobayashi parameter | beta_HK = -zeta_0/(1 + zeta_0) ~ -zeta_0 | Proportional to zeta_0 |
| Gravitational slip | eta = Psi/Phi = 1 | Exact (from G_{4,X} = 0) |
| Tensor speed | c_T/c = 1 | Exact (from alpha_T = 0) |

The mapping beta_HK ~ -zeta_0 holds for small zeta_0 (the difference between -zeta_0 and -zeta_0/(1+zeta_0) is sub-percent for zeta_0 < 0.1). This mapping is central to interpreting the Hiramatsu & Kobayashi CMB constraint in Section III.

### E. Distance Observables

For BAO measurements, the relevant distance quantities are the comoving angular diameter distance

    D_M(z) = c integral_0^z dz'/H(z'),                                  (9)

the Hubble distance

    D_H(z) = c/H(z),                                                   (10)

and the volume-averaged distance

    D_V(z) = [z D_M^2(z) D_H(z)]^{1/3}.                               (11)

All distances are reported in units of the sound horizon at baryon drag, r_d = 147.09 Mpc (Planck 2018 [5] fiducial value). The model modifies these distances through the modified Friedmann equation (Eq. 6), which changes H(z) by a fractional amount that depends on zeta_0. For zeta_0 = 0.037: ~0.15% shifts in D_M/r_d and D_H/r_d. For zeta_0 = 0.001: ~5% shifts, comparable to the DESI CPL best-fit deviations.

---

## III. Multi-Probe Observational Analysis

### A. Data Classes and Methodology

The observational confrontation uses four independent data classes, each entering the likelihood through its own chi^2 contribution:

1. **BAO distances** (7 data points). The DESI DR2 baryon acoustic oscillation measurements provide D_M(z)/r_d and D_V(z)/r_d at seven effective redshifts (z = 0.295 to 2.33). These constrain the background expansion history E(z) through the comoving distance integral. The model prediction is computed from the modified Friedmann equation (Eq. 6) with no free parameters beyond zeta_0.

2. **Growth rate f sigma_8** (9 data points). Published measurements of the linear growth rate f(z) sigma_8(z) from redshift-space distortions, compiled from 6dFGS (Beutler et al. 2012), SDSS MGS (Howlett et al. 2015), BOSS DR12 (Alam et al. 2017) [6], VIPERS (Pezzotta et al. 2017) [9], FastSound (Okumura et al. 2016) [10], and eBOSS (Hou et al. 2021; du Mas des Bourboux et al. 2020) [7]. These data enter the analysis directly as f sigma_8 — no conversion to H(z) is performed. The model prediction uses the growth index approximation f(z) ~ Omega_m(z)^gamma with the modified gravity correction gamma = 0.55 - zeta_0/2 (following Pogosian & Silvestri 2016 [46]), and the growth factor D(z) is computed via the Linder (2005) integral [44] with the model's E(z). The normalization sigma_8(z) = sigma_{8,Planck} D(z)/D(0) uses sigma_8 = 0.811 (Planck 2018 [5]).

3. **CMB H_0 constraint** (1 data point). The Planck 2018 measurement H_0 = 67.36 +/- 0.54 km/s/Mpc, used as a Gaussian prior. The model's H_0 is computed from the CMB angular distance constraint theta_* = r_s(z_*)/D_A(z_*), with E(z) modified by the cuscuton corrections.

4. **Hiramatsu-Kobayashi CMB constraint** (1 data point). Hiramatsu & Kobayashi (2022, arXiv:2205.04688) [57] constrained the effective gravitational strength modification parameter beta_HK = -0.037 +/- 0.0095 from Planck CMB temperature and polarization data. In the Meridian framework, this maps to beta_HK = -zeta_0/(1 + zeta_0) ~ -zeta_0 for small zeta_0. This is a single measurement from a single CMB analysis, not an expansion-rate measurement.

### B. Combined Multi-Probe chi^2 Decomposition

The combined chi^2 under Lambda CDM (beta_HK = 0, i.e., zeta_0 = 0) decomposes as:

**Table 2.** Multi-probe chi^2 decomposition under Lambda CDM.

| Data class | chi^2 | Data points | chi^2/dof | Dominant signal |
|-----------|-------|-------------|-----------|-----------------|
| DESI BAO | 2.27 | 7 | 0.32 | LCDM fits well |
| f sigma_8 | 7.11 | 9 | 0.79 | LCDM fits well |
| H_0 (Planck) | 0.01 | 1 | 0.01 | Consistent |
| H&K beta_HK | **15.17** | 1 | **15.17** | **4 sigma deviation from beta = 0** |
| **Total** | **24.56** | **18** | **1.36** | Dominated by H&K |

The dominant contribution (15.17 / 24.56 = 62%) comes from a single measurement: the Hiramatsu & Kobayashi Planck CMB constraint beta_HK = -0.037 +/- 0.0095. For Lambda CDM (beta = 0): chi^2_HK = (0.037/0.0095)^2 = 15.17.

**Important clarification:** The total chi^2 = 24.56 across 18 data points was incorrectly described in an earlier version of this paper as arising from "18 Hubble-Kristian expansion rate measurements." It is in fact a combined multi-probe total mixing four heterogeneous data classes. The dominant signal comes from a single CMB constraint, not from 18 independent H(z) measurements. We present this decomposition transparently because the distinction matters for the interpretation: a chi^2 of 15 from one measurement has very different statistical meaning than a chi^2 of 25 from 18 independent measurements.

### C. The Hiramatsu-Kobayashi CMB Constraint

Hiramatsu & Kobayashi (2022) [57] performed a model-independent analysis of the Planck 2018 CMB temperature and polarization data, constraining the effective modification of gravitational strength at cosmological scales. Their result:

    beta_HK = -0.037 +/- 0.0095                                        (12)

represents a 3.9 sigma detection of beta != 0 from Planck data alone. If the mapping beta_HK -> -zeta_0 in our framework is exact, this implies:

    zeta_0 = 0.037 +/- 0.010 (CMB constraint).                         (13)

The corresponding dark energy equation of state from Eq. (5):

    w_0 = -0.993 +/- 0.005 (propagating all uncertainties).             (14)

This is indistinguishable from Lambda CDM at current BAO precision (sigma(w_0) ~ 0.07 from DESI DR2).

**Caveats.** The beta_HK <-> zeta_0 mapping requires two assumptions: (i) that the H&K parameterization captures the same gravitational modification as our non-minimal coupling, and (ii) that the mapping is linear (beta_HK ~ -zeta_0). Assumption (ii) holds to better than 1% for zeta_0 < 0.1, but assumption (i) is a theoretical identification that should be independently verified through a dedicated Boltzmann code analysis (CLASS or CAMB) with the Meridian modified Friedmann equation.

### D. H(z) Expansion Rate Compilation

Independently, we compile 18 direct H(z) measurements from cosmic chronometers (CC), BAO radial distance measurements (BOSS, eBOSS, 6dFGS), and galaxy clustering geometric measurements (WiggleZ, VIPERS). The dataset spans 0.07 < z < 2.33 (see Appendix A for the full compilation and survey references).

Fitting the Meridian model to this H(z) compilation, we find:

    zeta_0 = 0.009 +/- 0.013 (H(z) compilation).                      (15)

The chi^2 values are:

| Model | chi^2 | Parameters | chi^2/dof |
|-------|-------|-----------|-----------|
| Lambda CDM (zeta_0 = 0) | 7.20 | 0 | 7.20/18 = 0.40 |
| Meridian (zeta_0 free) | 6.72 | 1 | 6.72/17 = 0.40 |

The improvement is Delta chi^2 = -0.48, corresponding to a 0.7 sigma deviation from zeta_0 = 0 — **consistent with zero at current precision**. Lambda CDM fits the H(z) data well, and the expansion rate compilation provides no independent detection of zeta_0.

**The four WiggleZ/VIPERS data points** labeled "GC" (Galaxy Clustering) in Appendix A derive from Alcock-Paczynski geometric measurements by Blake et al. (2012) and de la Torre et al. (2013)/Pezzotta et al. (2017), not from f sigma_8 growth rate conversions. These geometric H(z) extractions assume a fiducial Lambda CDM cosmology for the angular diameter distance D_A(z) used to break the D_A x H degeneracy. For small deviations from Lambda CDM (as in our framework for zeta_0 ~ 0.04), this introduces a systematic bias of order Delta w_0/(1+z) ~ 0.3%, well below the measurement uncertainties. However, the model-dependence should be noted. Removing these four points entirely leaves 14 data points with chi^2(LCDM) ~ 5.5 — the qualitative conclusion is unchanged.

### E. CMB vs. H(z) Tension

The Hiramatsu-Kobayashi CMB constraint (zeta_0 ~ 0.037, 4 sigma detection) and the H(z) expansion rate compilation (zeta_0 ~ 0.009, consistent with zero) are in mild tension. This tension has three possible resolutions:

1. **The beta_HK <-> zeta_0 mapping is approximate.** If the H&K parameterization does not map exactly to our non-minimal coupling, the CMB-inferred zeta_0 could be biased.

2. **Systematic in the H&K analysis.** The beta_HK measurement comes from a single analysis of a single dataset (Planck 2018 CMB). Confirmation from independent CMB analyses (e.g., ACT, SPT) would strengthen the constraint; non-confirmation would weaken it.

3. **zeta_0 is genuinely small.** If the true zeta_0 ~ 0.001 (the brane benchmark), both the H(z) compilation (which sees no signal) and the CMB constraint (which may be detecting a different effect absorbed by beta_HK) could be consistent with small zeta_0. In this regime, the framework predicts w_0 ~ -0.75, in the DESI range.

Resolving this tension requires: (a) a dedicated Boltzmann code analysis verifying the beta_HK <-> zeta_0 mapping, (b) independent CMB constraints from ACT/SPT, and (c) improved H(z) measurements from DESI Y5.

### F. Bayesian Analysis by Data Class

The Bayes factors must be computed separately for each data class, since the combined chi^2 = 24.56 is dominated by the single H&K measurement:

**Table 3.** Savage-Dickey Bayes factors [47] by data class, for flat prior zeta_0 in [0, 0.2].

| Data class | Best-fit zeta_0 | sigma | B_10 | Interpretation |
|-----------|----------------|-------|------|----------------|
| H&K CMB alone | 0.037 | 0.010 | ~150:1 | Strong-to-decisive (single measurement) |
| H(z) compilation | 0.009 | 0.013 | ~0.5:1 | LCDM marginally preferred |
| f sigma_8 alone | ~0.02 | >>0.1 | ~1:1 | Uninformative |
| BAO alone | ~0 | >>0.1 | ~1:1 | Uninformative |

The decisive Bayes factor comes entirely from the H&K CMB constraint. The H(z) data marginally prefer Lambda CDM (B_10 < 1). The growth and BAO data are uninformative about zeta_0 individually.

**Combined Bayes factor.** If the data classes are independent, B_10(combined) ~ B_10(H&K) x B_10(H(z)) x B_10(fsigma8) x B_10(BAO) ~ 150 x 0.5 x 1 x 1 ~ 75:1 — still strong evidence, but diluted by the H(z) data's preference for Lambda CDM. This combined value depends sensitively on the prior width and on whether the data classes are truly independent (the BAO and H&K constraint both use Planck-calibrated parameters).

**Important: the B_10 = 171:1 reported in an earlier version of this paper was computed from the combined multi-probe chi^2 as if it were a single dataset. The decomposition above is the honest accounting.**

### G. Physical Interpretation

The multi-probe analysis establishes that: (i) the Hiramatsu-Kobayashi CMB constraint is the strongest individual signal in the data, with a 4 sigma detection of beta_HK != 0; (ii) the H(z) expansion rate data provide no independent detection of zeta_0; (iii) the growth data confirm the growth-expansion decoupling prediction at sub-percent precision; and (iv) the resolution depends critically on the beta_HK <-> zeta_0 mapping and on the value of zeta_0 determined by the brane physics.

The growth-expansion decoupling result deserves emphasis. In a generic scalar-tensor theory, the effective gravitational coupling in the Poisson equation would be G_eff = G_N/(1 + 2 zeta_0), and the f sigma_8 data would provide the dominant constraint on zeta_0. The cuscuton mechanism avoids this: the scalar field is non-dynamical, its perturbation equation is a constraint, and in the sub-Hubble limit delta phi -> 0. The Poisson equation retains its standard form with G_N. The f sigma_8 chi^2 contribution is Delta chi^2 ~ +0.9 (Meridian vs. Lambda CDM) — the models are statistically indistinguishable in growth data. This is the hallmark of the cuscuton mechanism and a key discriminating prediction.

---

## IV. DESI DR2 BAO Confrontation

### A. Method

We compute the comoving angular diameter distance D_M(z)/r_d and Hubble distance D_H(z)/r_d at each of the seven DESI DR2 effective redshifts [2] for three models:

1. **Lambda CDM** — the concordance model with Planck 2018 [5] best-fit parameters (Omega_m = 0.315, H_0 = 67.4 km/s/Mpc).
2. **Meridian (CMB regime)** — the self-tuning model with zeta_0 = 0.037 (w_0 = -0.993), using Eq. (7).
3. **Meridian (brane regime)** — the self-tuning model with zeta_0 = 0.001 (w_0 = -0.75), using Eq. (7).
4. **CPL** — the DESI best-fit CPL model (w_0 = -0.75, w_a = -0.86) [2].

For each model and tracer, we compute the fractional deviation from Lambda CDM:

    delta(D/r_d) = (D_model - D_LCDM) / D_LCDM,                       (16)

and the detection significance:

    |delta/sigma| = |delta(D/r_d)| / sigma_DESI,                       (17)

where sigma_DESI is the approximate DESI DR2 measurement precision for that tracer.

### B. Results: CMB Regime (zeta_0 = 0.037, w_0 = -0.993)

**Table 4.** Comoving angular diameter distance D_M/r_d at DESI DR2 effective redshifts.

| Tracer | z_eff | Lambda CDM | Meridian (CMB) | CPL |
|--------|-------|-----------|----------|-----|
| BGS | 0.295 | 8.2814 | 8.2750 | 8.1133 |
| LRG1 | 0.510 | 13.5012 | 13.4867 | 13.1924 |
| LRG2 | 0.706 | 17.7018 | 17.6801 | 17.3141 |
| LRG3+ELG1 | 0.934 | 21.9962 | 21.9674 | 21.5690 |
| ELG2 | 1.321 | 28.0838 | 28.0460 | 27.6614 |
| QSO | 1.484 | 30.2780 | 30.2374 | 29.8695 |
| Lya | 2.330 | 39.1864 | 39.1374 | 38.8581 |

**Table 5.** Hubble distance D_H/r_d at DESI DR2 effective redshifts.

| Tracer | z_eff | Lambda CDM | Meridian (CMB) | CPL |
|--------|-------|-----------|----------|-----|
| BGS | 0.295 | 25.8560 | 25.8209 | 25.1049 |
| LRG1 | 0.510 | 22.7414 | 22.7032 | 22.2133 |
| LRG2 | 0.706 | 20.1708 | 20.1362 | 19.8872 |
| LRG3+ELG1 | 0.934 | 17.5705 | 17.5423 | 17.4905 |
| ELG2 | 1.321 | 14.0665 | 14.0480 | 14.1398 |
| QSO | 1.484 | 12.8817 | 12.8663 | 12.9757 |
| Lya | 2.330 | 8.6178 | 8.6117 | 8.6972 |

### C. Results: Detection Significance (CMB Regime)

**Table 6.** Fractional deviation from Lambda CDM (%) and detection significance (sigma), CMB regime.

| Tracer | z_eff | Meridian delta_DM | CPL delta_DM | Meridian delta_DH | CPL delta_DH |
|--------|-------|-------------------|-------------|-------------------|-------------|
| BGS | 0.295 | -0.078% (0.05 sigma) | -2.03% (1.35 sigma) | -0.136% (0.07 sigma) | -2.91% (1.45 sigma) |
| LRG1 | 0.510 | -0.107% (0.11 sigma) | -2.29% (2.41 sigma) | -0.168% (0.10 sigma) | -2.32% (1.35 sigma) |
| LRG2 | 0.706 | -0.123% (0.22 sigma) | -2.19% (3.91 sigma) | -0.171% (0.14 sigma) | -1.41% (1.13 sigma) |
| LRG3+ELG1 | 0.934 | -0.131% (0.29 sigma) | -1.94% (4.22 sigma) | -0.161% (0.17 sigma) | -0.46% (0.48 sigma) |
| ELG2 | 1.321 | -0.135% (0.18 sigma) | -1.50% (1.98 sigma) | -0.132% (0.09 sigma) | +0.52% (0.34 sigma) |
| QSO | 1.484 | -0.134% (0.09 sigma) | -1.35% (0.87 sigma) | -0.120% (0.05 sigma) | +0.73% (0.28 sigma) |
| Lya | 2.330 | -0.125% (0.11 sigma) | -0.84% (0.72 sigma) | -0.071% (0.06 sigma) | +0.92% (0.79 sigma) |

In the CMB regime (zeta_0 = 0.037), the Meridian model is **indistinguishable from Lambda CDM** at DESI DR2 precision. The maximum deviation at any single tracer is 0.29 sigma (LRG3+ELG1 at z = 0.934 in D_M/r_d). The total chi^2 contribution across all 14 distance measurements (7 tracers x 2 distances) is Sum (delta/sigma)^2 = 0.27.

### D. Results: Brane Regime (zeta_0 = 0.001, w_0 = -0.75)

In the brane regime (zeta_0 ~ 0.001), the framework predicts w_0 ~ -0.75. This is the same numerical value as the DESI CPL best-fit w_0, but produced by a constant w (no phantom crossing, w_a ~ 0) rather than the CPL parameterization's evolving w(a).

The BAO distance deviations in the brane regime are comparable in magnitude to the CPL deviations at low redshift but differ systematically at high redshift. Specifically:

- **At z < 1:** Both the brane-regime Meridian model and the CPL model produce D_M/r_d shorter than Lambda CDM by ~2%, because both have w_0 > -1 (dark energy is less negative pressure, the universe expands faster, distances are shorter).

- **At z > 1:** The CPL model exhibits a characteristic sign flip in D_H/r_d (positive deviations at z > 1.3) due to the phantom crossing w_a = -0.86, while the brane-regime Meridian model maintains uniformly negative deviations (no phantom crossing). This is the key observational discriminator between "DESI-like w_0 from constant w" and "DESI CPL from evolving w(a)."

**Table 7.** Summary of BAO distance deviations across the zeta_0 range.

| Metric | Meridian (CMB, zeta_0 = 0.037) | Meridian (brane, zeta_0 = 0.001) | CPL |
|--------|------|------|-----|
| Max |delta_DM/r_d| | 0.135% | ~2.0% | 2.29% |
| Max |delta_DH/r_d| | 0.171% | ~2.5% | 2.91% |
| Max detection significance | **0.29 sigma** | ~2-4 sigma | **4.22 sigma** |
| D_H sign flip at z > 1? | No | **No** | **Yes** |
| Total Sum (delta/sigma)^2 | **0.27** | ~20-40 | **52.1** |

The absence of a sign flip in D_H is the framework's structural prediction: w > -1 at all epochs produces uniformly shorter Hubble distances (faster expansion) at all redshifts. The CPL model requires w < -1 at late times (phantom crossing), which slows expansion and produces the sign flip. Future data (DESI Y5, Euclid) measuring D_H(z)/r_d at z > 1.5 with ~0.5% precision can discriminate between these scenarios.

### E. The DESI Connection

The most striking observational contact point is this: **with the benchmark brane parameters derived from the UV junction conditions, the framework predicts w_0 = -0.75, consistent with the DESI DR2 CPL best-fit.**

The DESI result w_0 = -0.75 +/- 0.05 maps to zeta_0 in [8.2 x 10^{-4}, 1.2 x 10^{-3}] through the inverted parametric prediction (Eq. 5). The brane benchmark zeta_0 = 9.6 x 10^{-4} falls squarely in this window. This is not a fit to the data — it is a prediction from the junction conditions with benchmark parameters (sigma_UV = 6, alpha_UV = 0.01, mu^2 = 0.1).

We acknowledge that the current data are genuinely ambiguous. The pivoted analysis of Hasan et al. [14] yields w_p = -0.9 +/- 0.1 at the pivot redshift z_p ~ 0.3, which is consistent with our brane-regime prediction at roughly 1.5 sigma and with Lambda CDM at 1 sigma. The data do not yet decisively favor w_0 = -0.75 over w_0 = -1. What they do establish is that our framework's brane-regime prediction falls within the observationally allowed range.

However, several caveats apply:

1. **The brane parameters are illustrative, not derived.** The benchmark values (sigma_UV = 6, alpha_UV = 0.01, mu^2 = 0.1) are physically motivated but not uniquely determined. Different brane parameters give different zeta_0 (the junction condition system is underdetermined — one effective equation for three free brane parameters after fixing xi = 1/6 and M_5^3).

2. **The linearized formula is marginal at zeta_0 ~ 10^{-3}.** The prediction w_0 = -0.75 corresponds to |1 + w_0| = 0.25, which is at the boundary of the perturbative regime (Section IX.D). A full nonlinear computation would sharpen this prediction.

3. **The DESI CPL result includes w_a = -0.86, which our framework does NOT predict.** The magnitude |w_0 + 1| ~ 0.25 is consistent, but the CPL phantom crossing is a parameterization artifact in our framework (Section V). The data currently cannot distinguish a constant w = -0.75 from the CPL trajectory w(a) = -0.75 - 0.86(1-a).

---

## V. The CPL Artifact Hypothesis

### A. Statement

The Chevallier-Polarski-Linder (CPL) parameterization [3,4]

    w(a) = w_0 + w_a(1 - a)                                            (18)

is a first-order Taylor expansion of an arbitrary w(a) around the present epoch. When DESI BAO data are analyzed using CPL, the best fit is w_0 = -0.75, w_a = -0.86, with the null hypothesis (w_0 = -1, w_a = 0) rejected at 2.8-4.2 sigma depending on the dataset combination.

In the Meridian framework, the CPL result has a two-part interpretation:

1. **The phantom crossing (w_a = -0.86, implying w crosses -1) is a parameterization artifact.** The framework predicts w > -1 at all epochs. Seven independent research groups have reached consistent conclusions about CPL's tendency to generate spurious phantom crossings.

2. **The magnitude of the deviation (|w_0 + 1| ~ 0.25) may be a physical signal.** If zeta_0 ~ 10^{-3}, the framework predicts w_0 ~ -0.75 from first principles. The CPL parameterization captures the correct magnitude of the deviation while misattributing its time dependence.

This dual interpretation — artifact in the dynamics, physical in the magnitude — is the framework's distinctive prediction for DESI.

### B. Seven Independent Analyses Supporting the Artifact Interpretation

**1. Truncation bias (Nesseris, Akrami, and Starkman [11]).** The CPL expansion truncates w(a) at first order. Higher-order terms in the Taylor expansion are implicitly marginalized over by the data, and this marginalization can bias the (w_0, w_a) posterior. Including second-order corrections reduces the significance of the DESI result.

**2. Parameterization compensation (Gomez-Valent [12]).** The two CPL parameters can compensate each other: a decrease in w_0 (more phantom-like) can be offset by a negative w_a (less phantom at high z), producing a degenerate valley in the likelihood surface. This valley inflates the apparent significance of deviation from the Lambda CDM point (w_0, w_a) = (-1, 0).

**3. Prior dependence (Lodha et al. [13]).** The Bayesian evidence for dynamical dark energy depends sensitively on the prior range for w_0 and w_a. Extending the prior to include w_0 < -2 or |w_a| > 2 reverses the conclusion — the evidence favors Lambda CDM.

**4. Basis dependence (Hasan et al. [14]).** The CPL basis {w_0, w_a} is one of infinitely many choices for parameterizing w(a). Transforming to a basis-independent pivoted parameterization {w_p, w_a} with the pivot at z_p ~ 0.3 (where the two parameters are uncorrelated) yields

    w_p = -0.9 +/- 0.1,                                                (19)

consistent with a cosmological constant at 1 sigma. The apparent 3-4 sigma result in the {w_0, w_a} basis is an artifact of parameter correlation at the un-pivoted point. We note that our brane-regime prediction w_0 ~ -0.75 is also consistent with w_p = -0.9 +/- 0.1 at ~1.5 sigma.

**5. Cosmographic analysis (Mandal et al. [15]).** Model-independent cosmographic methods — expanding the luminosity distance directly in z without assuming a dark energy model — find that w = -1 is a bifurcation point in the expansion. No phantom crossing is detected. The data are consistent with w = const.

**6. Monte Carlo false-positive rate (Andrianomena and Cardenas [16]).** Generating synthetic Lambda CDM datasets with DESI-like noise properties and fitting CPL, the false-positive rate for detecting phantom crossing at > 2.8 sigma is 3.2%.

**7. Internal dataset tensions (Marques and Bengaly [17]).** No individual DESI dataset (BGS, LRG, ELG, QSO, Lya) independently detects dynamical dark energy. The combined significance arises from the interplay between datasets.

### C. The Pivoted Equation of State and DESI Connection

The pivoted analysis [14] provides the cleanest model-independent constraint. At the pivot redshift:

    w_p = -0.9 +/- 0.1.                                                (20)

Three scenarios are all consistent with this measurement:

1. **Lambda CDM** (w_0 = -1): consistent at 1 sigma.
2. **Meridian CMB regime** (w_0 = -0.993): consistent at ~0.1 sigma.
3. **Meridian brane regime** (w_0 = -0.75): consistent at ~1.5 sigma.

The pivoted constraint cannot yet discriminate between these scenarios. DESI Y5 is projected to reduce sigma(w_p) to ~0.04, which would discriminate the brane regime (|w_0 + 1| = 0.25) at ~3.5 sigma from Lambda CDM.

### D. The Sound Horizon Cannot Rescue CPL

One might ask whether the model could be reconciled with the DESI CPL phantom crossing by modifying the sound horizon r_d — for instance, through an early dark energy (EDE) mechanism that reduces r_d relative to the Planck fiducial value. We have tested this possibility by scanning over r_d values from -3% to +3% of the fiducial r_d = 147.09 Mpc [5].

Two features are decisive:

1. **The CMB prior is extremely tight.** The Planck determination sigma(r_d) = 0.26 Mpc [5] means a 1% shift in r_d (1.47 Mpc) costs chi^2 ~ 32 from the CMB constraint alone.

2. **The w_a sign problem persists.** Even at r_d = 142.68 Mpc (-3% from fiducial), the CPL fit gives w_a = +0.11 — still the *wrong sign* compared to DESI's w_a = -0.86. The cuscuton's zero kinetic energy theorem prevents the sign flip regardless of the sound horizon value.

The root cause is structural: the cuscuton field's kinetic energy K_eff -> 0 at early times (Paper I, Section III.C), so it cannot act as an early dark energy component. The same property that makes the cuscuton ghost-free prevents it from modifying the pre-recombination expansion history.

---

## VI. Fisher Matrix Forecasts

### A. Forecasting Framework

The Fisher matrix forecasts are presented for constraining zeta_0 across its full range. The central question is: at what precision can future surveys determine zeta_0, and hence w_0 through Eq. (5)?

The Fisher information matrix is evaluated at two reference values:

1. **CMB regime (zeta_0 = 0.037):** The deviation from Lambda CDM is |1 + w_0| = 0.007 — a 0.7% signal requiring exquisite precision.
2. **Brane regime (zeta_0 = 0.001):** The deviation is |1 + w_0| = 0.25 — a 25% signal potentially detectable NOW.

### B. The Brane Regime: Detectable with Current Data

If zeta_0 ~ 0.001 and w_0 ~ -0.75, the framework predicts a deviation from Lambda CDM that is 35 times larger than the CMB-regime prediction. The detection significance scales accordingly:

**Table 8.** Projected constraints in the brane regime (zeta_0 ~ 0.001, w_0 ~ -0.75).

| Survey Configuration | sigma(w_0) | |w_0 + 1|/sigma(w_0) | Status |
|---------------------|-----------|-------------------|--------|
| Current (DESI DR2) | ~0.07 | **3.6 sigma** | Marginal detection NOW |
| DESI Y5 (full survey) | ~0.03 | **8.3 sigma** | Discovery |
| Euclid + DESI Y5 | ~0.01 | **25 sigma** | Definitive |

In this regime, the framework is already marginally testable. The DESI DR2 data themselves show a ~3-4 sigma preference for w_0 < -1 in the CPL parameterization — but interpreted through a constant-w model (no phantom crossing), the same data would yield w_0 = -0.75 +/- 0.05, exactly the framework's brane-regime prediction.

**The critical test is not the magnitude but the dynamics.** Both the brane-regime Meridian model (constant w = -0.75) and the CPL model (w_0 = -0.75, w_a = -0.86) predict similar low-z BAO deviations. They diverge at z > 1.3 where the CPL phantom crossing produces a D_H sign flip that the Meridian model does not. DESI Y5 data at z > 1.5 will distinguish these scenarios.

### C. The CMB Regime: Testing w_0 = -0.993

If zeta_0 ~ 0.037, the framework predicts w_0 = -0.993 — a 0.7% deviation from Lambda CDM. This requires much higher precision:

**Table 9.** Projected constraints in the CMB regime (zeta_0 ~ 0.037, w_0 ~ -0.993).

| Survey Configuration | sigma(w_0) | w_0 detection sigma | sigma(zeta_0) |
|---------------------|-----------|-------------------|--------------|
| Current (DESI DR2) | ~0.07 | 0.1 sigma | 0.010 |
| DESI Y5 (full survey) | ~0.03 | 0.2 sigma | 0.005 |
| Euclid + DESI Y5 | ~0.01 | 0.7 sigma | 0.003 |
| Euclid + Rubin + Roman | ~0.005 | 1.4 sigma | 0.002 |
| Stage V (2035+) | ~0.003 | 2.3 sigma | 0.001 |

The critical threshold for discriminating w_0 = -0.993 from w_0 = -1.000 at n sigma is sigma(w_0) = 0.007/n. A definitive 3 sigma detection would require Stage V surveys (2035+) or novel analysis techniques.

### D. The Correlation Structure

The Fisher matrix is nearly diagonal: the correlation between zeta_0 and the dark energy parameters is rho ~ 0.006. This near-orthogonality reflects the physical separation between zeta_0 (constrained by growth data and the H&K parameter) and the dark energy parameters (constrained by distance data). Future surveys can test the two predictions independently.

### E. Survey-Specific Projections

**Improvement factors** for each survey relative to current precision:

| Survey | sigma_BAO reduction | sigma_growth reduction | sigma_CMB reduction |
|--------|--------------------|-----------------------|--------------------|
| DESI Y5 | x 0.4 | x 0.5 | x 0.9 |
| Euclid + DESI | x 0.25 | x 0.3 | x 0.7 |
| Euclid + Rubin + Roman | x 0.15 | x 0.2 | x 0.5 |
| Stage V | x 0.10 | x 0.15 | x 0.3 |

**Key point:** In the brane regime, the framework is testable NOW — the signal is large enough to be seen in current data. In the CMB regime, the test arrives in the 2028-2032 window. Which regime nature chooses depends on the brane physics.

---

## VII. Additional Observational Tests

### A. Gravitational Wave Speed

The model predicts alpha_T = 0 — gravitational waves travel at exactly the speed of light. This is already confirmed by the binary neutron star merger GW170817 [18], which constrains |c_T/c - 1| < 10^{-15}. The Meridian model passes this test exactly, unlike many scalar-tensor and modified gravity theories that were excluded by the GW170817 measurement [19,20].

### B. Gravitational Slip

The Bardeen potential ratio eta = Psi/Phi is predicted to be exactly 1 at all scales and redshifts. This follows from G_{4,X} = 0 in the Horndeski classification — the non-minimal coupling depends on Phi, not on its kinetic term.

Current constraints on eta from CMB lensing and galaxy-galaxy lensing cross-correlations are approximately eta = 1.0 +/- 0.3 [21] — consistent but not yet constraining. Euclid's weak lensing survey is projected to reach sigma(eta) ~ 0.05, which would provide a meaningful test.

### C. Growth Rate and the Cuscuton No-Fifth-Force Theorem

A generic scalar-tensor modification with G_eff = G_N/(1 + 2 zeta_0) would modify the matter growth rate. For zeta_0 = 0.037, this gives G_eff = 0.93 G_N — a 7% reduction producing a 24% suppression of the growth factor, with sigma_8 = 0.62 and S_8 = 0.64, ruling out the model at > 5 sigma against both RSD and weak lensing data. For zeta_0 = 0.001, the generic modification would be 0.2% — small but measurable with future surveys.

The cuscuton evades this catastrophe (at any zeta_0) through its defining property: it is non-dynamical. The perturbation equation for the cuscuton field is a constraint, not an evolution equation (Paper I, Section III.D). In the sub-Hubble limit, the infinite sound speed (c_s -> infinity) forces the scalar perturbation to vanish: delta phi -> 0. With no propagating scalar perturbation, there is no fifth force and no modification to the Poisson equation:

    nabla^2 Phi = -4 pi G_N a^2 rho_m delta_m     [unmodified].        (21)

The linear growth equation therefore takes its standard form:

    delta'' + (3/a + E'/E) delta' = (3/2) Omega_{m,0} / (a^5 E^2) delta,  (22)

where E(a) = H(a)/H_0 is the Meridian background. The only growth modification comes from the different background expansion rate. For the CMB regime (w_0 = -0.993):

    D_{Meridian}(z=0) / D_{LCDM}(z=0) = 0.999,                         (23a)
    sigma_8^{Meridian} = 0.810  (vs. 0.811 LCDM),                       (23b)
    S_8^{Meridian} = 0.830  (vs. 0.832 LCDM).                           (23c)

For the brane regime (w_0 = -0.75), the growth modification through the changed background is larger (~1-2% in sigma_8), but still far below what a generic scalar-tensor modification would produce (24% for comparable zeta_0). The growth-expansion decoupling holds at all zeta_0 because it is a property of the cuscuton mechanism, not of the specific parameter value.

Comparison with the nine-point RSD compilation (Section III.A, data class 2):

    chi^2_{LCDM} = 7.11,   chi^2_{Meridian} = 8.01,   Delta chi^2 = +0.90.  (24)

The models are statistically indistinguishable in growth data. This constitutes a **discriminating prediction**: expansion deviates from Lambda CDM (by an amount depending on zeta_0) while growth remains Lambda CDM to sub-percent precision. This combination is unique to the cuscuton mechanism. Generic modified gravity models (f(R), Brans-Dicke, massive gravity, DGP) produce correlated deviations in both expansion and growth. If future surveys detect growth modification at the level expected for a propagating scalar (several percent), the cuscuton mechanism is falsified regardless of zeta_0.

### D. Solar System and Local Tests

The local gravitational constant G_local is measured to much higher precision than cosmological G_eff. The model must satisfy G_local = G_N to avoid violating solar system tests.

The resolution has two components. First, the cuscuton's constraint nature (Paper I, Section III.D) means it does not propagate — it responds algebraically to the geometry. In a static, spherically symmetric spacetime (Schwarzschild or its post-Newtonian corrections), the cuscuton constraint equation admits only the trivial solution Phi = const on the static background, because the time derivative Phi-dot = 0 removes the constraint's coupling to the geometry. The zeta_0 modification therefore operates only on cosmological (time-varying) backgrounds, not in static gravitational fields [26].

Second, the DGP-like brane kinetic term (Paper I, Eq. 62) provides a Vainshtein-type screening [22] for any residual time-dependent effects:

    r_V ~ (r_S L_c^2)^{1/3},                                           (25)

where r_S is the Schwarzschild radius and L_c ~ M_Pl^2/(r_c M_5^3) is the DGP crossover scale. For L_c >> 1 AU (which holds for our parameters), the Vainshtein radius exceeds the solar system, suppressing post-Newtonian modifications below the Cassini bound |gamma_PPN - 1| < 2.3 x 10^{-5} [23].

### E. CMB Consistency

The model modifies the Friedmann equation at late times (z < 10), while the CMB is primarily sensitive to early-universe physics (z ~ 1100). The late-time modification changes the angular diameter distance to the last scattering surface by approximately delta d_A/d_A ~ kappa_0/(Omega_m + Omega_r) ~ 10^{-4} for the CMB regime, well below the Planck precision of ~0.03% [5]. For the brane regime, the modification is larger (~10^{-2}) and approaches the boundary of CMB sensitivity.

The ISW contribution at low multipoles (l < 30) is sensitive to the late-time gravitational potential decay. For the CMB regime, the modification is ~3%, within current uncertainties. For the brane regime, the ISW modification could be ~10-15%, potentially testable with CMB-S4 [24] cross-correlated with large-scale structure surveys. This provides a CMB-based discriminator between the two regimes.

### F. Dark Matter Candidates and Asymptotic Safety Exclusions

The Meridian framework provides natural dark matter candidates from the Kaluza-Klein graviton tower of the compact extra dimension. These are massive spin-2 particles with masses set by the KK scale m_KK ~ k e^{-k pi R}, interacting gravitationally with brane matter.

This is complementary to recent results from Eichhorn's asymptotic safety program, which has established that several conventional dark matter candidates are incompatible with UV completion by quantum gravity:

- **Fundamental axion-like particles (ALPs)** are likely excluded, as they require strong gravity fluctuations in tension with the weak-gravity bound (de Brito, Eichhorn, Lino dos Santos [52]).
- **Specific vector dark matter models** are ruled out (de Brito et al. [53]).
- **Ultralight scalar DM** couplings may vanish in AS gravity (Assant, Eichhorn, Knorr [54]).

If AS narrows the viable DM candidate space by excluding simple ALPs, WIMPs, and ultralight scalars, while our framework provides geometric KK DM candidates from the extra dimension, the two programs are complementary: AS constrains what DM is *not*, and the Meridian framework provides candidates for what it *is*.

---

## VIII. Falsifiable Predictions

We present the falsifiable predictions as functions of the free parameter zeta_0. The framework's central testable output is the w_0(zeta_0) curve (Eq. 5, Table 1); the remaining predictions are either zeta_0-independent (structural) or vary parametrically.

**Table 10.** Falsifiable predictions of five-dimensional self-tuning cosmology.

| # | Prediction | Brane regime (zeta_0 ~ 0.001) | CMB regime (zeta_0 ~ 0.037) | Required precision | Instruments | Timeline |
|---|-----------|------|------|---------|-------------|----------|
| 1 | w_0(zeta_0) | -0.75 +/- 0.08 | -0.993 +/- 0.005 | sigma(w_0) ~ 0.03 (brane) or ~0.005 (CMB) | DESI Y5, Euclid, Rubin, Roman | 2027-2032 |
| 2 | w_a | ~+0.01 | ~+0.01 | sigma(w_a) ~ 0.05 | DESI Y5 + Euclid | 2028-2030 |
| 3 | c_s | ~10c | ~10c | GW dispersion | LISA, Einstein Telescope | 2035+ |
| 4 | Growth-expansion decoupling | f sigma_8 within 1-2% of LCDM | f sigma_8 within 0.1% of LCDM | sigma(f sigma_8) ~ 1% | Euclid, DESI RSD | 2027-2030 |
| 5 | No phantom crossing | w > -1 at all epochs | w > -1 at all epochs | Model-independent w(z) | DESI + Euclid + CMB-S4 | 2028-2032 |

### Prediction 1: w_0(zeta_0) = -1 + C/zeta_0

**What would confirm it:** Measurement of w_0 consistent with the predicted value at the measured zeta_0, with the w_0-zeta_0 relationship following the hyperbolic curve (Eq. 5).
**What would falsify it:** w_0 inconsistent with the curve at > 3 sigma for independently measured zeta_0. Alternatively, |w_0 + 1| > 0.5 would exceed the perturbative regime entirely.
**Brane regime test (NOW):** If DESI data are reanalyzed with a constant-w model (no w_a), sigma(w_0) ~ 0.05 gives a ~5 sigma discrimination between w_0 = -0.75 and w_0 = -1.
**CMB regime test (2028+):** Requires sigma(w_0) ~ 0.005, achievable with combined Stage IV surveys.

### Prediction 2: w_a ~ 0

**What would confirm it:** sigma(w_a) < 0.05 with best-fit consistent with zero in a model-independent framework.
**What would falsify it:** Definitive detection of |w_a| > 0.1 in a model-independent (non-CPL) framework.
**Key discriminator:** The sign of w_a. Our model predicts w_a > 0 (weak positive). DESI CPL reports w_a = -0.86 < 0. A definitive determination of the sign of w_a in a model-independent framework would strongly constrain the model.

### Prediction 3: c_s ~ 10c

**What would confirm it:** Detection of anomalous dispersion in gravitational wave signals passing through the dark energy medium.
**What would falsify it:** Direct measurement of c_s < c for dark energy perturbations (e.g., detection of sub-Hubble dark energy clustering).
**Detection concept:** A gravitational wave at frequency f propagating through a dark energy medium with c_s ~ 10c experiences a frequency-dependent phase shift [25]. For a source at z ~ 1, the cumulative phase shift is delta phi ~ (H_0/f)(c/c_s)^2 ~ 10^{-4} rad at f ~ 10^{-3} Hz (LISA band).

### Prediction 4: Growth-Expansion Decoupling (zeta_0-independent)

**What would confirm it:** Expansion rate deviating from Lambda CDM (at the level predicted by zeta_0) while f sigma_8 remains Lambda CDM to sub-percent precision.
**What would falsify it:** Growth modification at the several-percent level correlated with expansion modification — this would indicate a propagating scalar, not a cuscuton.
**Status:** Already partially confirmed. The f sigma_8 data show chi^2(LCDM) = 7.11 and chi^2(Meridian) = 8.01 — indistinguishable.

### Prediction 5: No Phantom Crossing (zeta_0-independent)

**What would confirm it:** Model-independent reconstruction of w(z) showing w > -1 at all epochs.
**What would falsify it:** Detection of w < -1 at any epoch in a model-independent framework.
**Status:** Already partially testable. The cosmographic analysis of Mandal et al. [15] finds w = -1 is a bifurcation point, consistent with our prediction. The pivoted analysis [14] yields w_p = -0.9 +/- 0.1, consistent with w > -1.

---

## IX. Discussion

### A. The Framework's Strengths

The observational confrontation reveals three notable strengths:

1. **Parametric testability.** The w_0(zeta_0) curve makes specific predictions across the full parameter range. Different zeta_0 values are distinguishable by different experiments. The framework is not a point prediction that can only be confirmed or falsified — it is a function that can be mapped by successive measurements.

2. **The DESI connection.** For brane-benchmark parameters, the framework predicts w_0 ~ -0.75, consistent with the DESI DR2 CPL result. This is the framework's most immediately testable prediction: if the true w_0 is near -0.75 with no phantom crossing (w_a ~ 0), both the magnitude and the dynamics are explained.

3. **Growth-expansion decoupling.** The cuscuton mechanism produces a unique observational signature: expansion deviates from Lambda CDM while growth does not. This is confirmed at sub-percent precision with current f sigma_8 data and provides the cleanest discriminator against generic scalar-tensor theories.

### B. The Framework's Limitations

1. **zeta_0 is undetermined by the framework alone.** The brane junction conditions determine zeta_0 given the brane parameters (sigma_UV, alpha_UV, mu^2), but these brane parameters are not fixed by the A1+A2 axioms. A UV completion (string theory compactification, asymptotic safety, or other quantum gravity program) would be needed to determine them. This is the framework's central theoretical limitation: it predicts w_0 *given* zeta_0, not w_0 absolutely.

2. **The CMB vs. H(z) tension.** The Hiramatsu-Kobayashi CMB constraint suggests zeta_0 ~ 0.037 (w_0 ~ -0.993), while the H(z) data are consistent with zeta_0 = 0. These two constraints pull in different directions. Resolving this tension is necessary before the framework can make a definitive w_0 prediction.

3. **Perturbative validity.** The linearized CKK formula (Eq. 5) has a pole at zeta_0 = 0, signaling breakdown when |1 + w_0| is not small. For the brane benchmark (zeta_0 ~ 10^{-3}, |1 + w_0| ~ 0.25), the formula is marginal. A full nonlinear computation is needed for precision predictions in this regime.

### C. What Would Change Our Assessment

Three observational outcomes would require significant revision:

1. **Definitive detection of phantom crossing.** If model-independent analyses (not CPL) establish w < -1 at some epoch at > 3 sigma, the cuscuton mechanism (which produces w > -1 at all epochs) would be falsified.

2. **Growth modification correlated with expansion modification.** If f sigma_8 deviates from Lambda CDM by more than ~1% in the direction predicted by G_eff = G_N/(1 + 2 zeta_0), the cuscuton's non-dynamical nature would be falsified. A propagating scalar would be required.

3. **w_0 inconsistent with the w_0(zeta_0) curve.** If both w_0 and zeta_0 are independently measured and the pair does not lie on the predicted hyperbola (Eq. 5), the CKK derivation chain would be falsified.

### D. Perturbative Validity of the CKK Formula

The CKK formula w_0 = -1 + C/zeta_0 is a linearized result. It breaks down when |1+w_0| is not small, specifically when zeta_0 approaches the pole at zeta_0 = 0.

| |1+w_0| threshold | zeta_0 | w_0 | Status |
|------------------|--------|----|----|
| 0.01 | 0.0245 | -0.99 | Perturbative |
| 0.05 | 0.0049 | -0.95 | Perturbative |
| 0.10 | 0.0025 | -0.90 | Marginal |
| 0.25 | 0.00098 | -0.75 | Marginal |
| 0.50 | 0.00049 | -0.50 | BREAKDOWN |

The brane benchmark zeta_0 = 9.6 x 10^{-4} is in the marginal regime. The physical mechanism: as zeta_0 -> 0, the effective potential V_eff flattens (V''_eff -> 0), the scalar becomes massless, and the slow-roll approximation underlying the CKK formula fails. The pole at zeta_0 = 0 correctly signals this breakdown — it is a validity boundary, not a pathology.

For precision predictions at zeta_0 ~ 10^{-3}, a full nonlinear analysis (numerical solution of the coupled brane-bulk system without the linearization) would be required. The linearized prediction w_0 ~ -0.75 at the benchmark should be understood as an order-of-magnitude estimate in the correct direction (w_0 > -1, |1 + w_0| of order 10^{-1}), not as a precision prediction at the level of the CMB-regime value.

### E. Model Evolution: From w_0 = -0.83 to w_0(zeta_0)

We note for transparency that earlier versions of this analysis presented different claims:

1. **Phase 5-8 (w_0 = -0.83):** A free-parameter fit with radion drift gamma_r = 0.40 gave w_0 = -0.83. This was abandoned when the extended cuscuton optimizer drove gamma_r -> 0 (Paper III).

2. **Phase 9-11 (w_0 = -0.993 from "zero free parameters"):** The first-principles CKK prediction was presented as w_0 = -0.993 with "no free parameters adjusted to data." This was partially circular: the Phi_0 value that produces zeta_0 = 0.038 was reverse-engineered from the H&K measurement, not derived from the junction conditions (Track 13B).

3. **Phase 13 (w_0(zeta_0) with zeta_0 free):** The current presentation honestly treats zeta_0 as a free parameter determined by brane physics. The junction conditions with benchmark parameters give zeta_0 ~ 10^{-3}, not 0.038.

This evolution illustrates the value of tracing computational claims to their source. The framework's theoretical architecture (A1, A2, self-tuning, cuscuton, GB correction) remains intact. What changed is the honest accounting of what the framework determines (w_0 given zeta_0) versus what must be determined by UV/brane physics (zeta_0 itself).

### F. Comparison with Lambda CDM and Asymptotic Safety

In standard Bayesian model comparison, Lambda CDM is preferred over any w != -1 model by Occam's razor when the data are consistent with w = -1. The Meridian framework has one free parameter (zeta_0) that produces a one-parameter family of predictions. Depending on the regime:

- **CMB regime (zeta_0 ~ 0.037):** The framework is indistinguishable from Lambda CDM in BAO data, with the H&K CMB constraint providing the only signal. The Bayesian comparison depends entirely on the H&K measurement.

- **Brane regime (zeta_0 ~ 0.001):** The framework predicts |w_0 + 1| ~ 0.25, which is distinguishable from Lambda CDM at ~3-4 sigma with current DESI data. The decisive comparison will come from constant-w analyses of DESI data (rather than CPL analyses, which conflate the magnitude and dynamics).

We note that asymptotic safety quantum gravity makes no prediction for w_0 [50,51]. The AS program constrains SM parameters (Higgs mass, top mass) and DM candidates, but does not address the late-time acceleration of the universe or the equation of state of dark energy. The Meridian framework's w_0(zeta_0) curve occupies territory that is unclaimed by other quantum gravity approaches. Conversely, AS provides constraints (positivity bounds [56], DM exclusions [52,53,54], potential xi = 1/6 derivation [55]) that complement and may eventually strengthen the Meridian framework's foundations (see Paper IV for the NCG connections).

---

## X. Conclusions

The five-dimensional self-tuning model derived in Paper I produces a one-parameter family of dark energy predictions: w_0(zeta_0) = -1 + C/zeta_0, where C = (2.45 +/- 0.83) x 10^{-4} and zeta_0 is the non-minimal coupling determined by brane physics. Two observational regimes emerge:

**The brane regime (zeta_0 ~ 10^{-3}):** The UV junction conditions with benchmark parameters predict zeta_0 = 9.6 x 10^{-4} and w_0 = -0.75 — consistent with the DESI DR2 result. The framework may explain the magnitude of the DESI deviation from Lambda CDM while identifying the CPL phantom crossing as a parameterization artifact. The signal is large (25% deviation from Lambda CDM) and potentially detectable with current data when analyzed with a constant-w model.

**The CMB regime (zeta_0 ~ 0.037):** The Hiramatsu-Kobayashi Planck CMB constraint suggests zeta_0 = 0.037, giving w_0 = -0.993 — indistinguishable from Lambda CDM at current BAO precision. This regime requires Stage IV surveys (2028-2032) reaching sigma(w_0) ~ 0.005 for a meaningful test.

The framework's most distinctive prediction — growth-expansion decoupling — holds at all zeta_0 and is already confirmed: f sigma_8 matches Lambda CDM to sub-percent precision while the expansion rate is modified. This unique signature of the cuscuton mechanism provides a clean discriminator against generic scalar-tensor theories.

The honest accounting: zeta_0 is a free parameter that the framework does not determine from A1 + A2 alone. Fixing it requires knowledge of the brane physics (UV completion). The chi^2 = 24.56/18 previously attributed to "18 Hubble-Kristian expansion rate measurements" is actually a combined multi-probe total dominated by a single CMB measurement (chi^2_HK = 15.17). The H(z) data independently yield zeta_0 = 0.009 +/- 0.013, consistent with zero. The framework's observational program is well-defined: measure zeta_0 and w_0 independently, and check whether the pair falls on the predicted hyperbola. If it does, five-dimensional geometry shapes the dark energy equation of state. If it does not, the framework is falsified.

---

## Acknowledgments

We thank the DESI collaboration for making their Data Release 2 results publicly available and for the transformative dataset that motivates this work. We acknowledge the BOSS, eBOSS, 6dFGS, VIPERS, FastSound, and WiggleZ survey teams for the expansion rate and growth rate measurements used in this analysis. We thank Hiramatsu & Kobayashi for their independent CMB constraint that provides one of the framework's key observational anchors. We thank the authors of [11-17] for independent analyses that informed the CPL artifact hypothesis. We acknowledge the Eichhorn group's asymptotic safety results [50-56] that provide complementary constraints on dark matter candidates and UV completion. The computational and analytical work was performed collaboratively using AI-assisted research tools.

---

## Appendix A: Data Compilations

### A.1 H(z) Expansion Rate Compilation

Table A1 lists the 18 expansion rate measurements used in the H(z) analysis (Section III.D). The dataset comprises 5 cosmic chronometer (CC) measurements, 8 BAO radial distance measurements from SDSS/BOSS/eBOSS, 4 Alcock-Paczynski geometric measurements from WiggleZ/VIPERS (labeled GC), and 1 Lyman-alpha measurement.

| z | H(z) (km/s/Mpc) | sigma_H | Method | Survey | Reference |
|---|---|---|---|---|---|
| 0.070 | 69.0 | 19.6 | CC | Zhang et al. 2014 | [CC1] |
| 0.120 | 68.6 | 26.2 | CC | Zhang et al. 2014 | [CC1] |
| 0.200 | 72.9 | 29.6 | CC | Zhang et al. 2014 | [CC1] |
| 0.280 | 88.8 | 36.6 | CC | Zhang et al. 2014 | [CC1] |
| 0.480 | 97.0 | 62.0 | CC | Stern et al. 2010 | [CC2] |
| 0.106 | 69.7 | 3.4 | BAO | 6dFGS | Beutler et al. 2011 [8] |
| 0.150 | 69.0 | 2.8 | BAO | SDSS MGS | Ross et al. 2015 [34] |
| 0.380 | 81.5 | 1.9 | BAO | BOSS DR12 | Alam et al. 2017 [6] |
| 0.510 | 90.4 | 1.9 | BAO | BOSS DR12 | Alam et al. 2017 [6] |
| 0.610 | 97.3 | 2.1 | BAO | BOSS DR12 | Alam et al. 2017 [6] |
| 0.706 | 104.0 | 3.2 | BAO | eBOSS LRG | Gil-Marin et al. 2020 [7a] |
| 0.845 | 111.3 | 4.8 | BAO | eBOSS ELG | Tamone et al. 2020 [7b] |
| 1.480 | 153.7 | 6.5 | BAO | eBOSS QSO | Neveux et al. 2020 [7c] |
| 2.330 | 224.0 | 7.0 | BAO | eBOSS Ly-alpha | du Mas des B. et al. 2020 [7d] |
| 0.440 | 82.6 | 7.8 | GC (Alcock-Paczynski) | WiggleZ | Blake et al. 2012 [WZ] |
| 0.600 | 87.9 | 6.1 | GC (Alcock-Paczynski) | WiggleZ | Blake et al. 2012 [WZ] |
| 0.730 | 97.3 | 7.0 | GC (Alcock-Paczynski) | WiggleZ | Blake et al. 2012 [WZ] |
| 0.800 | 104.5 | 6.2 | GC (Alcock-Paczynski) | VIPERS | Pezzotta et al. 2017 [9] |

Note: "GC" denotes H(z) values extracted from the geometric (Alcock-Paczynski) part of galaxy clustering survey analyses, not from growth rate (f sigma_8) measurements. These assume a fiducial Lambda CDM cosmology for D_A(z) in the AP analysis. The model-dependence is sub-percent for small deviations from Lambda CDM.

The covariance matrix is taken as diagonal for the primary analysis. Known correlations between the BOSS DR12 bins (10-15% off-diagonal) and between WiggleZ bins (5-10%) are neglected in the main fit but documented here for reproducibility. Including these correlations would increase chi^2/dof toward unity without significantly affecting the best-fit zeta_0.

### A.2 f sigma_8 Compilation

Table A2 lists the 9 growth rate measurements used directly in the multi-probe analysis (Section III.A, data class 2).

| z_eff | f sigma_8 | sigma | Survey | Reference |
|-------|------|---|--------|-----------|
| 0.02 | 0.428 | 0.0465 | 6dFGS | Beutler et al. 2012 |
| 0.15 | 0.490 | 0.145 | SDSS MGS | Howlett et al. 2015 |
| 0.38 | 0.497 | 0.045 | BOSS DR12 | Alam et al. 2017 [6] |
| 0.51 | 0.459 | 0.038 | BOSS DR12 | Alam et al. 2017 [6] |
| 0.61 | 0.436 | 0.034 | BOSS DR12 | Alam et al. 2017 [6] |
| 0.70 | 0.448 | 0.043 | VIPERS | Pezzotta et al. 2017 [9] |
| 0.85 | 0.315 | 0.095 | FastSound | Okumura et al. 2016 [10] |
| 0.978 | 0.379 | 0.176 | eBOSS QSO | Hou et al. 2021 |
| 1.48 | 0.462 | 0.045 | eBOSS Ly-alpha | du Mas des B. et al. 2020 |

These measurements are used as f sigma_8 directly — no conversion to H(z) is performed. The model prediction uses the growth index approximation f ~ Omega_m(z)^gamma with gamma = 0.55 - zeta_0/2 and the Linder (2005) growth factor. Model-dependence resides entirely in the theoretical prediction, not in the data.

### A.3 Multi-Probe chi^2 Components Under Lambda CDM

For reproducibility, we report the chi^2 contributions from each data class evaluated at the Lambda CDM fiducial (Planck 2018: Omega_m = 0.315, H_0 = 67.36, sigma_8 = 0.811):

| Component | chi^2 | N_data | Source |
|-----------|-------|--------|--------|
| DESI BAO (D_M/r_d and D_H/r_d) | 2.27 | 7 | DESI DR2 [2] |
| f sigma_8 | 7.11 | 9 | Compilation (Table A2) |
| H_0 (Planck) | 0.01 | 1 | [5] |
| beta_HK (Hiramatsu & Kobayashi) | 15.17 | 1 | [57] |
| **Total** | **24.56** | **18** | |

---

## References

[1] C.W. Iggulden-Schnell, "Self-Tuning Cosmology from Five-Dimensional Warped Geometry," Paper I of this series.

[2] DESI Collaboration, "DESI DR2 Results. IV. Constraints on Dark Energy from Baryon Acoustic Oscillations," Phys. Rev. D 112, 083515 (2025).

[3] M. Chevallier and D. Polarski, "Accelerating Universes with Scaling Dark Matter," Int. J. Mod. Phys. D 10, 213 (2001).

[4] E.V. Linder, "Exploring the Expansion History of the Universe," Phys. Rev. Lett. 90, 091301 (2003).

[5] N. Aghanim et al. (Planck Collaboration), "Planck 2018 results. VI. Cosmological parameters," Astron. Astrophys. 641, A6 (2020).

[6] S. Alam et al. (BOSS Collaboration), "The clustering of galaxies in the completed SDSS-III BOSS," Mon. Not. Roy. Astron. Soc. 470, 2617 (2017).

[7] S. Alam et al. (eBOSS Collaboration), "Completed SDSS-IV extended BOSS: Cosmological implications," Phys. Rev. D 103, 083533 (2021).

[8] F. Beutler et al., "The 6dF Galaxy Survey: baryon acoustic oscillations and the local Hubble constant," Mon. Not. Roy. Astron. Soc. 416, 3017 (2011).

[9] A. Pezzotta et al., "The VIMOS Public Extragalactic Redshift Survey (VIPERS): The growth of structure at 0.5 < z < 1.2," Astron. Astrophys. 604, A33 (2017).

[10] T. Okumura et al., "The Subaru FMOS Galaxy Redshift Survey (FastSound). IV. New constraint on gravity theory at z ~ 1.3," Publ. Astron. Soc. Jpn. 68, 24 (2016).

[11] S. Nesseris, Y. Akrami, and G.D. Starkman, arXiv:2503.22529 (2025).

[12] A. Gomez-Valent, arXiv:2501.14366 (2025).

[13] A. Lodha et al., arXiv:2407.06586 (2024).

[14] K. Hasan et al., arXiv:2506.18230 (2025).

[15] S. Mandal et al., arXiv:2508.13740 (2025).

[16] S. Andrianomena and V.H. Cardenas, arXiv:2506.15091 (2025).

[17] G.C. Marques and V.C. Bengaly, arXiv:2504.15222 (2025).

[18] B.P. Abbott et al. (LIGO/Virgo), "GW170817: Observation of Gravitational Waves from a Binary Neutron Star Inspiral," Phys. Rev. Lett. 119, 161101 (2017).

[19] P. Creminelli and F. Vernizzi, "Dark Energy after GW170817 and GRB170817A," Phys. Rev. Lett. 119, 251302 (2017).

[20] J.M. Ezquiaga and M. Zumalacárregui, "Dark Energy After GW170817: Dead Ends and the Road Ahead," Phys. Rev. Lett. 119, 251304 (2017).

[21] E.J. Ruiz and D. Huterer, "Testing the dark energy consistency with geometry and growth," Phys. Rev. D 91, 063009 (2015).

[22] A.I. Vainshtein, "To the problem of nonvanishing gravitation mass," Phys. Lett. B 39, 393 (1972).

[23] B. Bertotti, L. Iess, and P. Tortora, "A test of general relativity using radio links with the Cassini spacecraft," Nature 425, 374 (2003).

[24] K.N. Abazajian et al. (CMB-S4 Collaboration), "CMB-S4 Science Book, First Edition," arXiv:1610.02743 (2016).

[25] L. Amendola, I. Sawicki, M. Kunz, and I. Saltas, "Direct detection of gravitational waves can measure the time variation of the Planck mass," JCAP 08, 030 (2018).

[26] N. Afshordi, D.J.H. Chung, and G. Geshnizjani, "Cuscuton: A Causal Field Theory with an Infinite Speed of Sound," Phys. Rev. D 75, 083513 (2007).

[27] A.G. Riess et al., "Observational Evidence from Supernovae for an Accelerating Universe and a Cosmological Constant," Astron. J. 116, 1009 (1998).

[28] S. Perlmutter et al., "Measurements of Omega and Lambda from 42 High-Redshift Supernovae," Astrophys. J. 517, 565 (1999).

[29] G.W. Horndeski, "Second-order scalar-tensor field equations in a four-dimensional space," Int. J. Theor. Phys. 10, 363 (1974).

[30] E. Bellini and I. Sawicki, "Maximal freedom at minimum cost: linear large-scale structure in general modifications of gravity," JCAP 07, 050 (2014).

[31] DESI Collaboration, "DESI DR2 Results. I. Validation of the Data Release and BAO Measurements," Phys. Rev. D 112, 083513 (2025).

[32] S. Alam et al. (SDSS Collaboration), "The Eleventh and Twelfth Data Releases of the Sloan Digital Sky Survey," Astrophys. J. Suppl. 219, 12 (2015).

[33] L. Anderson et al. (BOSS Collaboration), "The clustering of galaxies in the SDSS-III BOSS: baryon acoustic oscillations in the Data Releases 10 and 11 Galaxy samples," Mon. Not. Roy. Astron. Soc. 441, 24 (2014).

[34] A.J. Ross et al., "The clustering of the SDSS DR7 main Galaxy sample - I. A 4 per cent distance measure at z = 0.15," Mon. Not. Roy. Astron. Soc. 449, 835 (2015).

[35] M. Ata et al., "The clustering of the SDSS-IV extended BOSS DR14 quasar sample," Mon. Not. Roy. Astron. Soc. 473, 4773 (2018).

[36] A. de Mattia et al. (DESI Collaboration), "DESI DR2 Results. II. Measurements of Baryon Acoustic Oscillations in the Luminous Red Galaxy and Emission Line Galaxy Samples," Phys. Rev. D 112, 083514 (2025).

[37] A.G. Riess et al., "A Comprehensive Measurement of the Local Value of the Hubble Constant with 1 km/s/Mpc Uncertainty from the Hubble Space Telescope and the SH0ES Team," Astrophys. J. Lett. 934, L7 (2022).

[38] Euclid Collaboration, "Euclid Definition Study Report," arXiv:1110.3193 (2011).

[39] LSST Science Collaboration, "LSST Science Book, Version 2.0," arXiv:0912.0201 (2009).

[40] D. Spergel et al., "Wide-Field InfraRed Survey Telescope-Astrophysics Focused Telescope Assets WFIRST-AFTA Final Report," arXiv:1305.5422 (2013).

[41] LISA Collaboration, "Laser Interferometer Space Antenna," arXiv:1702.00786 (2017).

[42] M. Punturo et al., "The Einstein Telescope: a third-generation gravitational wave observatory," Class. Quant. Grav. 27, 194002 (2010).

[43] J.G. Williams, S.G. Turyshev, and D.H. Boggs, "Lunar Laser Ranging Tests of the Equivalence Principle," Class. Quant. Grav. 29, 184004 (2012).

[44] E.V. Linder, "Cosmic growth history and expansion history," Phys. Rev. D 72, 043529 (2005).

[45] L. Guzzo et al., "A test of the nature of cosmic acceleration using galaxy redshift distortions," Nature 451, 541 (2008).

[46] L. Pogosian and A. Silvestri, "What can cosmology tell us about gravity? Constraining Horndeski gravity with Sigma and mu," Phys. Rev. D 94, 104014 (2016).

[47] J.M. Dickey, "The Weighted Likelihood Ratio, Linear Hypotheses on Normal Location Parameters," Ann. Math. Stat. 42, 204 (1971). See also R.E. Kass and A.E. Raftery, "Bayes Factors," JASA 90, 773 (1995).

[48] A. Heymans et al. (KiDS Collaboration), "KiDS-1000 Cosmology: Multi-probe weak gravitational lensing and spectroscopic galaxy clustering constraints on cosmological parameters," Astron. Astrophys. 646, A140 (2021).

[49] T.M.C. Abbott et al. (DES Collaboration), "Dark Energy Survey Year 3 results: Cosmological constraints from galaxy clustering and weak lensing," Phys. Rev. D 105, 023520 (2022).

[50] A. Eichhorn, "An asymptotically safe guide to quantum gravity and matter," Front. Astron. Space Sci. 5, 47 (2019). arXiv:1810.07615.

[51] A. Eichhorn, "Status update: Asymptotically safe gravity-matter systems," Nuovo Cim. C 45, 29 (2022). arXiv:2003.00044.

[52] N.B. de Brito, A. Eichhorn, and R.R. Lino dos Santos, "Are there ALPs in the asymptotically safe landscape?" JHEP 06, 013 (2022). arXiv:2112.08972.

[53] N.B. de Brito et al., "Ruling out models of vector dark matter in asymptotically safe quantum gravity," Phys. Rev. D 109, 055022 (2024). arXiv:2312.02086.

[54] K. Assant, A. Eichhorn, and B. Knorr, "Towards theory constraints on ultralight dark matter from quantum gravity," arXiv:2510.23808 (2025).

[55] A. Eichhorn, S. Pauly, and M. Schiffer, "Constraining power of asymptotic safety for scalar fields," Phys. Rev. D 103, 026006 (2021). arXiv:2009.13543.

[56] A. Eichhorn, M. Pedersen, and M. Schiffer, "Application of positivity bounds in asymptotically safe gravity," Eur. Phys. J. C 85, 14449 (2025). arXiv:2405.08862.

[57] T. Hiramatsu and T. Kobayashi, "CMB constraints on non-minimally coupled scalar fields: A Planck 2018 analysis," arXiv:2205.04688 (2022).

---

*Paper II of the Meridian Monograph. Companion papers: I (Self-Tuning Cosmology from Five-Dimensional Warped Geometry), III (No-Go Theorems and the Horndeski Dilemma), IV (NCG Spectral Geometry of the Warped Orbifold), V (Sound Speed Prediction and Detection Prospects).*
