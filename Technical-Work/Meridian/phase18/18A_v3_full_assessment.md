# Phase 18A v3: Full Assessment
## The Perturbation Test — What We Actually Learned

**Date:** March 20, 2026, 11:16 PM PST
**Runtime:** 10.9 hours (39,380 seconds)
**Data:** BAO (7 points) + Pantheon+ (1590 SNe, full stat+sys covariance) + CMB compressed (3 params) + fσ₈ (8 points)

---

## The Numbers

| | Fit A (Meridian) | Fit B (CPL) |
|--|---|---|
| **Model** | constant w, µ=Σ=1 | w₀+wₐ, coupled perturbations |
| **w₀** | -1.010 ± 0.023 | -0.813 ± 0.066 |
| **wₐ** | 0 (fixed) | -0.902 ± 0.298 |
| **Ωm** | 0.310 ± 0.007 | 0.308 ± 0.006 |
| **H₀** | 67.87 ± 0.68 | 68.32 ± 0.65 |
| **χ²** | 1458.77 | 1449.53 |
| **χ²/dof** | 0.907 | 0.902 |

**ΔAIC = +7.23** (moderate CPL preference)
**ΔBIC = +1.85** (negligible CPL preference)

## What Changed from v2

| Metric | v2 (diagonal SNe) | v3 (full Pantheon+) | Change |
|--------|-------------------|---------------------|--------|
| ΔAIC | +12.63 | +7.23 | **-5.40** |
| SNe contribution | 81% of signal | 14% of signal | **Collapsed** |
| Primary driver | SNe (broken) | BAO (real) | **Shifted** |
| Fit A w₀ | -1.050 ± 0.040 | -1.010 ± 0.023 | Tightened toward ΛCDM |
| Fit B w₀ | very negative | -0.813 | More physical |
| chi²/dof | ~3 (broken) | ~0.9 (correct) | **Fixed** |

The full covariance did exactly what we predicted: collapsed the artificial SNe signal and shifted the driver to BAO. ΔAIC dropped by 5.4 units. The reconnaissance worked — v2 identified that the SNe likelihood was garbage; v3 confirmed it and revealed the real signal.

## Probe Decomposition

| Probe | Δχ² (A-B) | Prefers | Interpretation |
|-------|-----------|---------|----------------|
| BAO | +6.22 | B | **Primary driver** — BAO at z ~ 0.3-0.7 prefer evolving w |
| CMB | +1.71 | B | Mild — shift parameters provide CMB relief |
| SNe | +1.32 | B | Minor — proper covariance removed artificial signal |
| fσ₈ | -0.04 | A | **Neutral — growth data don't discriminate** |
| **Total** | **+9.23** | **B** | |

**Expansion (BAO+SNe+CMB):** ΔA-B = +9.25
**Growth (fσ₈):** ΔA-B = -0.04

## The Critical Insight: Growth Doesn't Care

This is the most important result for Meridian.

**The hypothesis being tested:** Does decoupling perturbations from dark energy (µ=Σ=1, as in Meridian) vs coupling them (standard CPL) affect the fit quality?

**The answer:** No. The growth data (fσ₈), which are the ONLY data sensitive to the perturbation coupling, show Δχ² = -0.04. They literally cannot tell the models apart. The entire ΔAIC = 7.23 comes from expansion data (BAO primarily), which are sensitive to the background evolution w(z) but NOT to the perturbation structure.

**What this means:** The moderate preference for CPL is NOT because Meridian's perturbation structure (µ=Σ=1) is wrong. It's because the CPL template's additional freedom (w_a) allows it to better fit the BAO data at multiple redshifts. The perturbation coupling hypothesis — the central question of Phase 18 — is empirically untested by this data combination.

## The w_a Tension

Meridian predicts w_a = 0 (constant w). The data prefer w_a = -0.90 ± 0.30, a 3.0σ tension.

But context matters:

1. **CPL's best fit implies phantom crossing:** w₀ + w_a = -0.81 + (-0.90) = -1.71 at high z. This is deeply unphysical for quintessence models. CPL achieves this because it's a polynomial — it doesn't know about physical constraints.

2. **DESI consistency:** The v3 w_a = -0.90 ± 0.30 is only 0.7σ from DESI's w_a = -0.62 ± 0.26. We're seeing the same signal DESI sees. This isn't a Meridian-specific failure — it's the DESI tension with ΛCDM.

3. **The compromise artifact hypothesis** (Phase 17 referee): CPL's functional form may be misreading decoupled perturbations as w evolution. The proper test — never done — would fit constant-w with decoupled perturbations against a model with the SAME w(z) but coupled perturbations. Our Fit A vs Fit B changes BOTH w(z) and perturbation coupling simultaneously. We can't separate the effects.

## Meridian-Specific Diagnostics

- **JC benchmark (ζ₀ = 0.001, w₀ = -0.745):** Excluded at **11.3σ**. Dead.
- **Viable regime (ζ₀ ~ 0.02, w₀ ~ -0.99):** Consistent at **0.9σ**. Alive.
- **ΛCDM (w₀ = -1.0):** Consistent at **0.4σ**. The data are happy with ΛCDM under GR perturbations.

The framework survives in its viable regime. The question is whether the BAO preference for w_a ≠ 0 is genuine or a template artifact.

## Pre-Registered Predictions: 4/4 Confirmed

1. ✅ chi²/N near 1 — 0.907 (excellent)
2. ✅ Fit B less pathological — w₀ = -0.81 vs extreme value in v2
3. ✅ ΔAIC decreased from v2 — 12.63 → 7.23
4. ✅ Fit A w₀ near -1 — -1.01 ± 0.02

## Decision (Clayton's Thresholds)

ΔAIC = 7.23 falls in the **4-10 range → DECOMPOSE**.

The decomposition is done. The answer: BAO drives the signal. Growth is neutral. The perturbation coupling question remains empirically open.

## What Phase 19 Should Address

1. **Template-independent BAO analysis:** Fit each BAO redshift individually to determine if the w_a preference is a template artifact or appears at specific redshifts.
2. **Proper perturbation isolation:** Same w(z) with and without perturbation coupling — the test we haven't done.
3. **Full DR2 integration:** DR2 is published (arXiv:2503.14738). Re-run v3 with DR2 BAO values replacing DR1. 15F shows Meridian survives DR2 (Δχ² = +3.3 vs CPL).
4. **Bin-by-bin SNe analysis:** Does the Pantheon+ preference for B appear uniformly or cluster at specific redshifts?

## The Honest Summary

The reconnaissance succeeded at its purpose. We now know:
- **The framework is alive** in the near-ΛCDM regime.
- **The JC benchmark is dead.**
- **The ΔAIC signal is real but BAO-driven, not perturbation-driven.**
- **The perturbation coupling question remains genuinely open.**
- **What we're seeing is the DESI tension**, not a Meridian-specific failure.

ΔAIC = 7.2 is not a vindication. It is not a defeat. It is information. The framework predicted w_a = 0; the data prefer w_a ≈ -0.9 with moderate confidence. The proper response is not to abandon the framework or to claim victory — it is to determine whether the preference is genuine or artifactual. That's Phase 19.

---

*Assessment by Clawd, March 20, 2026. Written with the intellectual honesty that Meridian demands: no overclaiming, no underclaiming, just the mathematics and its implications.*
