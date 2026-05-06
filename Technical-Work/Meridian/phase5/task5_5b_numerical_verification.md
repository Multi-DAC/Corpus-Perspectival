# Phase 5, Task 5.5b: Extended Cuscuton — Numerical Verification

**Project Meridian — Deliverable D5.5b**
*Clayton & Clawd, March 2026*

D5.5 derived the extended cuscuton analytically: G₃ braiding breaks K ~ 1/H² via a λ₃/E term in K_eff. This deliverable reports the numerical results.

---

## 1. Summary of Results

**The extended cuscuton (G₃ braiding) CANNOT fix the H₀ bottleneck.**

Every optimizer, from every starting point, drives λ₃ → 0. The mechanism that works analytically in isolation fails when embedded in the full normalization-constrained cosmology.

## 2. Numerical Tests Performed

### 2.1 Test A: Extended cuscuton at ζ₀ = 0 (no non-minimal coupling)

81-point grid scan over (ε₀, λ₃), plus 7 Nelder-Mead optimizations from different starting points.

**Result:** All optimizers converge to ε₀ → 0, λ₃ → 0 (ΛCDM). The extended cuscuton at ζ₀ = 0 has no H₀ problem to fix (H₀ = 67.4 at ε₀ → 0).

Increasing λ₃ at ζ₀ = 0 LOWERS H₀ slightly (67.4 → 66.5) and worsens χ²_DESI monotonically.

### 2.2 Test B: Extended cuscuton at ζ₀ = 0.058 (Phase 4 DESI-optimal)

This is the real test. At ζ₀ = 0.058, the minimal cuscuton gives:
- w₀ = -0.925, wₐ = -1.125 (good DESI fit)
- H₀ = 64.5 km/s/Mpc (5.7σ below Planck)
- χ²_total = 54.19

1D scan over λ₃ at fixed (ε₀ = 0.001, ζ₀ = 0.058):

| λ₃  | w₀     | wₐ     | H₀   | χ²_DESI | χ²_H₀  | χ²_total |
|------|--------|--------|------|---------|---------|----------|
| 0.00 | -0.925 | -1.125 | 64.5 | 9.93    | 32.82   | 54.19    |
| 0.10 | -0.936 | -1.233 | 64.4 | 11.99   | 36.15   | 59.98    |
| 0.20 | -0.943 | -1.357 | 64.3 | 14.39   | 39.61   | 66.27    |
| 0.30 | -0.949 | -1.497 | 64.1 | 17.27   | 43.21   | 73.21    |
| 0.50 | -0.953 | -1.818 | 63.8 | 25.14   | 50.82   | 89.69    |

λ₃ makes EVERYTHING worse: H₀ decreases, |wₐ| increases, χ² increases monotonically.

64-point 2D grid + 6 Nelder-Mead optimizations confirm: **optimum is at λ₃ = 0**.

Best extended: χ²_total = 54.12 (Δ = +0.07 from minimal — negligible).

## 3. Root Cause: Why the Analytical Estimate Failed

### 3.1 The Normalization Trap

The D5.5 analytical estimate assumed λ₃/E adds "new" dark energy at high redshift. But within the Friedmann normalization constraint (E(0) = 1), the λ₃ term does not add energy — it REDISTRIBUTES it:

    v₀ = (Ω_DE + 2ζ₀ + 4ζ₀β - λ₃) / (1 + ε₀)

Increasing λ₃ DECREASES v₀ (potential energy) AND κ₀ = ε₀v₀ (kinetic energy). The λ₃/E term at E > 1 (all past epochs) contributes LESS than λ₃, while the reduction in κ₀/E² from lower κ₀ dominates.

Net effect: dark energy is weaker at intermediate redshifts, not stronger. D_A increases, H₀ decreases. Opposite of the estimate.

### 3.2 The Deeper Issue

The K ~ 1/H² scaling is a consequence of the **cuscuton constraint** combined with the **warped geometry**. The G₃ braiding modifies the constraint (eq 3.3 of D5.5), but within the Friedmann normalization, this modification is absorbed. The constraint is too rigid to be broken from within its own sector.

**The cuscuton constraint determines φ algebraically from H. There is no dynamical freedom to exploit.** Adding G₃ changes which constraint holds, but it's still a constraint — zero propagating scalar DOF. The new constraint just maps differently onto the Friedmann equation without generating the needed decoupling.

## 4. Comparison Table

| Model | w₀ | wₐ | H₀ | χ²_DESI | χ²_fσ₈ | χ²_H₀ | χ²_HK | χ²_total |
|-------|------|-------|------|---------|---------|--------|--------|----------|
| ΛCDM | -1.000 | 0.000 | 67.4 | 28.82 | 7.02 | 0.00 | 15.17 | 51.01 |
| Minimal (ζ₀=0.058) | -0.925 | -1.125 | 64.5 | 9.93 | 7.92 | 32.82 | 3.52 | 54.19 |
| Extended (optimum) | -0.933 | -1.103 | 64.6 | 10.54 | 7.95 | 32.11 | 3.52 | 54.12 |

The minimal cuscuton BEATS ΛCDM on (χ²_DESI + χ²_HK) by 30.54 but LOSES on χ²_H₀ by 32.82. The net is +3.18 worse than ΛCDM. The extended cuscuton cannot close this gap.

## 5. What This Eliminates

- G₃ braiding as a fix for the H₀ bottleneck ❌
- Any modification WITHIN the cuscuton sector (same constraint structure) ❌
- The λ₃/E term in K_eff (analytically elegant but normalization-killed) ❌

## 6. What Remains Open

The H₀ bottleneck requires a modification OUTSIDE the cuscuton constraint. Three candidate paths:

### Path A: Accept the tension
Publish with H₀ ≈ 64.5. The model's strengths (first-principles, hierarchy unification, DESI w₀/wₐ, H&K preference) may outweigh the H₀ penalty. The tension is a PREDICTION — testable by future H₀ measurements.

### Path B: Modified potential V(φ)
Allow V(φ) to have specific redshift dependence beyond the slow-roll assumption. Changes K(E) indirectly. Adds freedom, loses minimality.

### Path C: Radion dynamics (most promising)
Let the brane position y_c evolve slowly. The radion is a DIFFERENT degree of freedom from the cuscuton — it lives in the geometry, not the scalar sector.

Key mechanism: GB correction (α̂ ~ 0.01 from spectral action, D5.2) perturbs the cuscuton's stabilization of the radion, allowing slow drift. The drifting brane changes the warp factor A(y_c(t)), modifying the effective 4D parameters independently of the scalar perturbation structure.

This connects: Phase 5 NCG (D5.2: α̂ predicted) → Phase 4 problem (H₀ bottleneck) → radion as the resolution.

---

## 7. Deliverable Checklist

- [x] D5.5b.1: Numerical scan at ζ₀ = 0 (Test A) — λ₃ collapses to ΛCDM
- [x] D5.5b.2: Numerical scan at ζ₀ = 0.058 (Test B) — λ₃ worsens everything
- [x] D5.5b.3: Root cause analysis (normalization trap, constraint rigidity)
- [x] D5.5b.4: Comparison table (ΛCDM vs minimal vs extended)
- [x] D5.5b.5: Elimination list and forward paths identified

---

*Negative results are informative. The extended cuscuton cannot break K ~ 1/H² from within the constraint sector. The resolution must come from a different degree of freedom — the radion. The spectral action provides the mechanism (GB-induced slow drift). This is Phase 6 territory.*

🦞🧍💜🔥♾️
