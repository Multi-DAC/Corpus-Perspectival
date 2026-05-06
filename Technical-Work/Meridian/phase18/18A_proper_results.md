# 18A Proper MCMC Results — The Perturbation Test

*Completed March 20, 2026, 6:05 AM PST*
*MCMC runtime: ~10 hours (Fit A: 2.7h, Fit B: 2.4h, overhead: ~5h debugging/restarts)*

---

## The Question

Is phantom crossing (w_a != 0) real physics, or an artifact of assuming coupled perturbations when the truth has GR perturbations (mu = Sigma = 1)?

**Fit A** (Meridian): constant w_0, w_a = 0 fixed, mu = Sigma = 1 (smooth DE, no clustering)
**Fit B** (Standard CPL): w_0 + w_a free, standard coupled perturbations

## Configuration

- **Sampler:** emcee 3.1.6, 16 walkers, 200 burn-in + 500 production (serial)
- **Data:** BAO (DESI DR1 + SDSS), Pantheon+ (19 binned, diagonal + 0.25 mag floor), CMB compressed (l_A, R, omega_b from Planck 2018), f*sigma_8 (7 points from SDSS/WiggleZ)
- **CAMB:** v1.6.6, fluid DE model for both fits (c_s^2 = 1 for Fit A, PPF for Fit B)

**Important caveats:**
- Diagonal-only SNe (no full Pantheon+ covariance matrix)
- Compressed CMB (not full Planck likelihood)
- No inter-probe covariance
- This is RECONNAISSANCE, not publication-ready

---

## Results

### Best-Fit Parameters

| Parameter | Fit A | Fit B |
|-----------|-------|-------|
| w_0 | -1.042 | -0.124 |
| w_a | 0 (fixed) | -2.940 |
| Omega_m | 0.302 | 0.368 |
| H_0 | 68.77 | 62.71 |
| chi^2 | 118.84 | 104.21 |
| chi^2/dof | 3.127 | 2.817 |

### Posterior Summary

**Fit A:**
- w_0 = -1.049 +0.038 -0.041 (mean: -1.049 +/- 0.041)
- Omega_m = 0.302 +0.009 -0.010 (mean: 0.302 +/- 0.010)
- H_0 = 68.86 +1.17 -1.02 (mean: 68.91 +/- 1.12)
- Effective samples: 274

**Fit B:**
- w_0 = -0.287 +0.121 -0.204 (mean: -0.324 +/- 0.170)
- w_a = -2.396 +0.629 -0.436 (mean: -2.300 +/- 0.537)
- Omega_m = 0.354 +0.014 -0.017 (mean: 0.352 +/- 0.016)
- H_0 = 63.88 +1.57 -1.15 (mean: 64.08 +/- 1.47)
- Effective samples: ~200

### Model Comparison

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Delta chi^2 (A-B) | +14.63 | B fits better |
| **Delta AIC (A-B)** | **+12.63** | **"Decisive" for B** |
| Delta BIC (A-B) | +10.91 | Strong for B |

### Probe-by-Probe chi^2 at Best Fit

| Probe | Fit A | Fit B | Delta | Driver? |
|-------|-------|-------|-------|---------|
| BAO | 41.56 | 41.09 | +0.46 | No |
| **SNe** | **67.69** | **55.85** | **+11.84** | **YES** |
| CMB | 1.51 | 0.17 | +1.34 | Minor |
| f*sigma_8 | 8.09 | 7.10 | +0.99 | No |

### Growth vs Expansion Split

| Component | Fit A | Fit B | Delta |
|-----------|-------|-------|-------|
| Expansion (BAO+SNe+CMB) | 110.76 | 97.12 | +13.64 |
| Growth (f*sigma_8) | 8.09 | 7.10 | +0.99 |

---

## Critical Assessment

### What the DAIC Says
Formally, DAIC = 12.6 is "decisive" against Fit A. By Clayton's thresholds (> 10), the constant-w prediction is "in serious trouble."

### Why I Don't Trust It (5 Reasons)

**1. SNe drive everything.**
The entire DAIC comes from supernovae (+11.84 out of +14.63). Our SNe likelihood uses diagonal errors with a 0.25 mag systematic floor — the crudest possible approximation. The full Pantheon+ covariance matrix would change this number substantially and unpredictably.

**2. Fit B parameters are pathological.**
w_a = -2.94 (near prior boundary at -3.0), H_0 = 62.7 (below any reasonable measurement), Omega_m = 0.368. No existing analysis (DESI, Planck, DES, anybody) finds these values. Our Fit B is NOT reproducing the DESI result — it's finding a different, unphysical minimum.

**3. Growth data don't discriminate.**
The whole point of this test was: does forcing GR perturbations (mu = Sigma = 1) change the growth-expansion split? Answer: barely. Delta(f*sigma_8) = 0.99. The perturbation coupling is NOT driving the signal. The compromise artifact hypothesis predicts growth should prefer A while expansion prefers B — but growth weakly prefers B too. No probe split detected.

**4. Both fits are poor.**
chi^2/dof = 3.1 (A) and 2.8 (B). Both models fit the data badly. This suggests systematic issues with the likelihood construction, not that one model is correct.

**5. w_a posterior doesn't match DESI.**
Our w_a = -2.40 +/- 0.54. DESI (Lu & Simon 2026) finds w_a = -0.62 +/- 0.26. These are 3.3 sigma apart. Our pipeline is finding a DIFFERENT phantom crossing than the one in the literature. This almost certainly reflects likelihood pathologies, not new physics.

### What Would Change This Assessment

1. **Full Pantheon+ covariance** — the single most important upgrade. Our SNe chi^2 would change dramatically with proper systematics.
2. **Full CMB likelihood** — even our 3-parameter compressed CMB gives chi^2 ~ 1.5. This is suspiciously good and suggests the compressed form may not be constraining enough.
3. **DESI DR2 BAO** — proper DESI likelihoods with covariance.
4. **CosmoMC or Cobaya** — production-grade sampling with proper convergence diagnostics.

---

## Verdict

**The reconnaissance is INCONCLUSIVE.**

The formal DAIC (12.6) says "decisive for CPL." But the signal is entirely SNe-driven with pathological Fit B parameters, no growth-expansion split, and a w_a posterior inconsistent with DESI. This is a likelihood problem, not a physics verdict.

**The constant-w prediction is NOT definitively ruled out.** But it IS under pressure. The path forward:
1. Acquire full Pantheon+ covariance and re-run (the single highest-impact improvement)
2. If SNe contribution drops below ~5 with proper covariance, DAIC could fall well below 10
3. If it doesn't, investigate epsilon_2 X^2 corrections for small but nonzero w_a

**Meridian-specific note:** Fit A's posterior centers on w_0 = -1.05, not Meridian's -0.75. Even if DAIC were < 4 (constant-w adequate), the data don't want w = -0.75 under GR perturbations — they want LCDM. This is a separate tension from the DAIC. The brane parameters may need recalibration, or the reconnaissance likelihood is biasing the result.

---

## Decision Matrix (per Clayton's thresholds)

| Threshold | Result | Action |
|-----------|--------|--------|
| DAIC < 4 | NO (12.6) | ~~Write PRL immediately~~ |
| DAIC 4-10 | NO (12.6) | ~~Decompose~~ |
| **DAIC > 10** | **YES (12.6)** | **Investigate, BUT with major caveats** |

**Recommended action:** Do NOT declare "constant-w is dead." Instead: acknowledge the tension, prioritize acquiring proper likelihoods (Pantheon+ covariance is the bottleneck), and revisit. The reconnaissance tells us the question is worth asking with proper tools — it doesn't answer it.

---

*Generated by Clawd during the overnight vigil, March 20, 2026.*
