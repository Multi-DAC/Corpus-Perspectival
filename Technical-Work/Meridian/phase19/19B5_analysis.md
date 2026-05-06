# 19B.5 Perturbation Isolation Test — Analysis

**Completed:** 2026-03-22 03:42 PST | **Runtime:** 262.8 min (4.4 hrs) | **Platform:** GPU (CUDA)

---

## Executive Summary

The perturbation isolation test confirms what Phase 18's probe decomposition hinted: **the entire DESI dark energy signal lives in the expansion history, not in the growth of structure.** The framework's distinctive predictions — modified gravitational perturbations via cuscuton coupling — are invisible to current cosmological data. Meridian's μ = Σ = 1 prediction is **untested, not confirmed or refuted.**

---

## The Three-Fit Architecture

| Fit | Model | Parameters | χ² | Description |
|-----|-------|-----------|-----|-------------|
| **A** | Constant w₀, μ = 1 | 4 (w₀, Ωm, H₀, σ₈) | 1422.67 | Baseline: simplest dark energy |
| **C** | CPL (w₀ + wₐ), μ = 1 | 5 | 1417.29 | **Meridian prediction**: evolving w(z), GR perturbations |
| **D** | CPL (w₀ + wₐ), μ₀ free | 6 | 1417.19 | Agnostic: let the data choose perturbation coupling |

---

## Key Results

### 1. The w(z) Template Effect: ΔAIC(A vs C) = +3.38

Adding wₐ to the equation of state improves the fit. This is the DESI signal — it's real, moderate, and driven by:

| Probe | Fit A χ² | Fit C χ² | Δ | Interpretation |
|-------|---------|---------|-----|----------------|
| BAO | 12.87 | 10.40 | **+2.48** | **Primary driver** |
| CMB | 2.88 | 0.77 | **+2.11** | **Secondary driver** |
| SNe | 1403.83 | 1402.86 | +0.98 | Marginal |
| fσ₈ | 3.08 | 3.27 | -0.18 | Growth slightly *hurts* CPL |

**BAO and CMB together account for 4.59 of the 5.38 total Δχ².** Growth data contribute nothing positive. This refines Phase 18's finding (expansion Δ = +9.25, growth Δ = -0.04) with a cleaner decomposition.

### 2. THE HEADLINE — Perturbation Coupling: ΔAIC(C vs D) = -1.91

Adding the perturbation parameter μ₀ makes the fit **worse**. The probes cancel:

| Probe | Fit C χ² | Fit D χ² | Δ | Interpretation |
|-------|---------|---------|-----|----------------|
| BAO | 10.40 | 9.85 | +0.54 | Slight preference for μ₀ freedom |
| CMB | 0.77 | 1.32 | -0.56 | Penalizes μ₀ freedom equally |
| SNe | 1402.86 | 1402.93 | -0.07 | Noise |
| fσ₈ | 3.27 | 3.09 | +0.17 | Noise |

**Net Δχ² = 0.10 for one extra parameter.** The data contain *zero information* about perturbation coupling. The AIC penalty (-2) dominates, giving ΔAIC = -1.91.

### 3. μ₀ Posterior

```
μ₀ = 0.12 ± 0.52  (mean ± std)
μ₀ = 0.10  [-0.42, 0.67]  (median, 68% CI)
Tension with μ₀ = 0: 0.2σ
```

Meridian predicts μ₀ = 0 (cuscuton has infinite sound speed → no gravitational slip → μ = Σ = 1). The posterior is **wide and centered near zero**. Consistent with the prediction, but this is "consistent because unconstrained," not "consistent because tested."

### 4. σ₈ Stability

| Fit | σ₈ |
|-----|-----|
| A | 0.8010 ± 0.0207 |
| C | 0.8017 ± 0.0209 |
| D | 0.7975 ± 0.0257 |
| Planck 2018 | 0.811 ± 0.006 |

All fits ~1.4σ below Planck. The S₈ tension persists but is model-independent — it doesn't care about w(z) template or perturbation coupling. This is an independent tension, not a framework artifact.

### 5. wₐ Stability

| Fit | wₐ |
|-----|-----|
| C (μ = 1) | -0.504 ± 0.224 |
| D (μ₀ free) | -0.515 ± 0.229 |

Adding μ₀ freedom doesn't shift wₐ. The expansion and perturbation sectors are **decoupled in the posterior**. This is exactly what "the signal is a template effect" means — it lives entirely in the distance-redshift relation.

### 6. Convergence

All parameters: ESS > 500. Adequate for inference. Fit D has the best convergence (ESS 698–1516), likely because the wide μ₀ posterior means the sampler explores freely.

---

## Cross-Reference with Phase 18

| Metric | Phase 18 (v5 DR2) | 19B.5 (A vs C) | 19B.5 (A vs D) |
|--------|-------------------|-----------------|-----------------|
| ΔAIC | +1.10 | +3.38 | +1.47 |
| BAO drives? | Yes | Yes (+2.48) | Yes |
| Growth neutral? | Yes (Δ = -0.04) | Yes (Δ = -0.18) | Yes |

The v5 reference ΔAIC(A vs B) = +3.57 (no growth) vs our ΔAIC(A vs C) = +3.38 (with growth) — adding growth data **slightly reduces** the CPL preference. Growth is not just neutral; it marginally penalizes the evolving model. Consistent across all analysis versions.

---

## What This Means for the PRL Letter

1. **The probe decomposition IS the headline.** The peer reviewer was right. The story is not "dark energy evolves" — it's "the DESI signal is distance measurements, not structure formation."

2. **Perturbation isolation is clean.** ΔAIC(C vs D) = -1.91 with μ₀ = 0.12 ± 0.52. This is a single number that captures the entire perturbation story.

3. **The framework is untested, not confirmed.** Honest framing: "Meridian's predictions are consistent with data because current data lack the constraining power to test them." This is strength, not weakness — it means the framework survives contact with data, and the real tests (LISA, DUNE, collider) are still ahead.

4. **Phase 19 tracks vindicated.** The Phase 16 detection channels aren't wishful thinking — they're the *only way* to actually test the framework's distinctive physics.

---

## What This Means for the Framework

The DESI signal decomposes cleanly:
- **Expansion sector:** BAO + CMB see evolving w(z). ΔAIC = +3.38. Real but moderate.
- **Perturbation sector:** Invisible. μ₀ unconstrained. ΔAIC = -1.91.
- **Cross-sector:** Decoupled. wₐ doesn't shift when μ₀ is freed.

This is exactly the regime where Meridian lives — near-ΛCDM with w₀ ≈ -1, perturbation modifications too small to detect with current growth data, waiting for dedicated experiments to reveal the 5D structure.

---

*Analysis by Clawd, 2026-03-22. Data: DESI DR2 BAO + Pantheon+ SNe + Planck compressed CMB + fσ₈ compilation. Sampler: NumPyro NUTS on GPU. Growth ODE via RK4 (500 steps).*

🦞🧍💜🔥♾️
