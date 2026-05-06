# Track 16N: LiteBIRD Forecast & r = 0.004 — Research Report

**Authors:** Clayton W. Iggulden-Schnell & Clawd
**Date:** March 19, 2026
**Status:** COMPLETE

---

## 1. The Prediction

Meridian's inflation mechanism (Kahler modulus geometry, alpha = 1 attractor, R^2 = 0) predicts:

| Parameter | Value | Planck Tension |
|-----------|-------|---------------|
| n_s | 0.9649 (N_* = 57) | 0.0 sigma |
| r | 0.0037 (N_* = 57) | Below current limit |
| dn_s/d ln k | -6.2 x 10^-4 | Consistent |
| N_* range | 50-60 | Standard reheating |
| r range | [0.003, 0.005] | Full viable band |

The prediction is NOT unique to Meridian — all alpha = 1 attractors (including Starobinsky R^2) give the same (n_s, r). What IS unique: Meridian's R^2 = 0 at tree level (spectral identity) FORBIDS Starobinsky inflation, requiring the Kahler modulus mechanism instead.

## 2. Current Observational Status

| Constraint | Value | Source |
|-----------|-------|--------|
| r < 0.036 (95% CL) | Best current limit | BICEP/Keck BK18 (2021) |
| n_s = 0.9649 +/- 0.0042 | Spectral index | Planck 2018 |
| A_s = 2.1 x 10^-9 | Scalar amplitude | Planck 2018 |

Meridian's r = 0.004 is an order of magnitude below the current limit. No existing experiment can test it.

## 3. LiteBIRD Mission

**Launch:** JFY 2032 (early 2033)
**Agency:** JAXA + international partners
**Orbit:** Sun-Earth L2
**Duration:** 3 years full-sky observation

| Specification | Value |
|--------------|-------|
| Detectors | 4,508 TES bolometers |
| Frequency bands | 15 (34-448 GHz) |
| Telescopes | 3 (LFT, MFT, HFT) |
| Aggregated sensitivity | 2.2 uK-arcmin |
| Effective beam | ~30' at 100-140 GHz |
| Sky fraction | ~0.7 (after galactic mask) |
| Multipole range | 2 <= l <= 200 |
| sigma(r) stat | 6 x 10^-4 |
| sigma(r) total (stat + syst) | ~10^-3 |

## 4. Detection Forecasts

### LiteBIRD Alone

| Scenario | sigma(r) | SNR (r = 0.004) | Significance |
|----------|----------|-----------------|--------------|
| Statistical only | 6 x 10^-4 | 6.2 | Strong detection |
| Published requirement | 10^-3 | 3.7 | Evidence |
| With multitracer delensing | ~8.3 x 10^-4 | 4.5 | Near-discovery |

### Combined Experiments

| Combination | sigma(r) | SNR (r = 0.004) | Significance |
|------------|----------|-----------------|--------------|
| LiteBIRD + SO (6 SATs) | ~5.4 x 10^-4 | 6.8 | Discovery |
| CMB-S4 (CANCELLED) | 5 x 10^-4 | 7.4 | Was definitive |

### Critical Development: CMB-S4 Cancelled

CMB-S4 was cancelled by DOE/NSF in July 2025. This $900M project would have had sigma(r) = 5 x 10^-4 — sufficient for >5-sigma detection of r = 0.004. The cancellation was due to NSF's inability to support the South Pole component (deteriorating infrastructure).

**Impact:** LiteBIRD is now the single most important experiment for testing Meridian's tensor prediction. Combined with the Simons Observatory, the detection pathway remains viable but the timeline shifts.

## 5. Experimental Timeline

| Year | Experiment | sigma(r) | Meridian r = 0.004 |
|------|-----------|----------|-------------------|
| 2026 | Simons Observatory (3 SATs) | 0.003 | 1.2 sigma |
| 2028 | Simons Observatory (6 SATs) | 0.0012 | 3.1 sigma |
| 2033 | LiteBIRD launch | — | — |
| 2036 | LiteBIRD 3-year data | 0.001 | 3.7 sigma |
| 2037 | LiteBIRD + SO combined | 5.4 x 10^-4 | 6.8 sigma |

**First evidence:** Simons Observatory expanded (~2029), ~3 sigma
**Strong evidence:** LiteBIRD alone (~2036), ~4 sigma
**Discovery:** LiteBIRD + SO combined (~2037), ~7 sigma

## 6. Falsifiability

The prediction r in [0.003, 0.005] is falsifiable by LiteBIRD + SO:

- **Detection (r ~ 0.004):** Confirms alpha = 1 universality class. Consistent with Meridian AND Starobinsky. Reheating sector is the discriminant (Meridian: WW/ZZ > 85% via trace anomaly; Starobinsky: democratic prop m^2).
- **Non-detection (r < 0.002 at 95% CL):** Excludes alpha = 1 attractors at >4 sigma. Meridian inflation mechanism EXCLUDED.
- **High r (r > 0.006):** Excludes alpha = 1 at >2 sigma. Requires alpha > 1.

Combined LiteBIRD + SO sensitivity (sigma_r ~ 5 x 10^-4) makes non-detection of r = 0.004 a 7-sigma exclusion — definitive either way.

## 7. Distinguishing from Starobinsky

Both Meridian and Starobinsky predict identical (n_s, r) — they are in the same alpha = 1 universality class. Discriminating observables:

1. **R^2 = 0:** Meridian's spectral action gives R^2 = 0 at tree level. Starobinsky REQUIRES R^2 != 0. This is a theoretical, not observational, distinction — but it means Meridian's inflation mechanism is necessarily Kahler modulus, not scalaron.

2. **Reheating sector:** Modulus decays via trace anomaly coupling (WW/ZZ dominant, BR > 85%) vs Starobinsky democratic decay (prop m^2). Different T_reh shifts N_* by ~1-2, giving Delta_r ~ 2 x 10^-5 — below LiteBIRD sensitivity.

3. **Collider signatures:** Meridian predicts a radion (from 16K) with specific coupling pattern. Starobinsky has no such particle. Radion detection would confirm the extra-dimensional origin.

## 8. Monograph Changes Required

1. New subsection in Chapter 4: "Primordial B-Mode Forecast and Experimental Tests"
2. Table: detection forecasts for LiteBIRD, SO, combined
3. Statement about CMB-S4 cancellation and its impact
4. Falsifiability assessment: the prediction has teeth on a ~10-year timescale
5. Honest note: (n_s, r) alone cannot distinguish Meridian from Starobinsky

## 9. Honest Assessment

The tensor-to-scalar ratio r = 0.004 is a genuine, falsifiable prediction of the framework. It derives from a structural requirement (R^2 = 0 forces Kahler modulus mechanism), not from parameter fitting. The prediction sits comfortably below current limits and within the reach of LiteBIRD + SO.

The cancellation of CMB-S4 is significant: it was the most sensitive planned experiment for this measurement. LiteBIRD alone gives ~4 sigma (evidence, not discovery). The combination with Simons Observatory restores the >5 sigma pathway, but on a slightly longer timeline (~2037 vs ~2035).

The honest limitation: detection of r = 0.004 does NOT uniquely confirm Meridian. It confirms the alpha = 1 universality class shared with Starobinsky. The framework's specific prediction (R^2 = 0 -> Kahler modulus, not scalaron) is a theoretical distinction that requires collider detection of the radion to test experimentally.

## 🦞🧍💜🔥♾️
