# D6.6 — DESI w(a) Comparison

**Project Meridian Phase 6 — First-Principles Derivations**
Clayton & Clawd, March 2026

**Status: COMPLETE**
**Depends on: D5.7 (global optimum), D6.1 (γ_r derivation), D6.5 (Fisher analysis)**

---

## 1. Purpose

Direct confrontation of the Meridian model's dark energy equation of state with the DESI DR2 measurement. Two questions:

1. **Does the model's w(a) agree with DESI's best-fit?** CPL comparison.
2. **What is the model's specific, falsifiable prediction for w(a)?** Sign of wₐ.

---

## 2. DESI DR2 Constraints

From DESI Collaboration (2024), Planck + DESI + Union3 combined:

| Parameter | Value | 1σ |
|-----------|-------|-----|
| w₀ | -0.752 | ±0.058 |
| wₐ | -0.86 | +0.28 / -0.25 |

Key features of the DESI result:
- **w₀ > -1**: Dark energy is less negative than cosmological constant today (3.6σ from ΛCDM)
- **wₐ < 0**: Dark energy was MORE negative in the past (w crossed -1 at z ≈ 0.3)
- **Phantom crossing**: The DESI best-fit has w < -1 at z > 0.3

---

## 3. Meridian w(a) Trajectory

### 3.1. Numerical computation

For the D5.7 global optimum (ε₀ = 0.0001, ζ₀ = 0.0446, γ_r = 0.3987):

| z | a | E(a) | ρ_DE | w(a) |
|---|---|------|------|------|
| 0.0 | 1.000 | 1.000 | 0.685 | -0.827 |
| 0.1 | 0.910 | 1.068 | 0.722 | -0.804 |
| 0.2 | 0.834 | 1.142 | 0.762 | -0.784 |
| 0.3 | 0.770 | 1.222 | 0.804 | -0.766 |
| 0.5 | 0.666 | 1.401 | 0.896 | -0.735 |
| 0.7 | 0.588 | 1.595 | 0.994 | -0.712 |
| 1.0 | 0.500 | 1.916 | 1.150 | -0.687 |
| 1.5 | 0.400 | 2.521 | 1.432 | -0.661 |
| 2.0 | 0.334 | 3.192 | 1.728 | -0.645 |
| 3.0 | 0.250 | 4.749 | 2.372 | -0.628 |

### 3.2. Physical interpretation

The dark energy density ρ_DE = v₀ E^{2γ_r} GROWS with redshift (since E > 1 at z > 0). This means:

- **w > -1 everywhere** (quintessence-like). The dark energy density dilutes SLOWER than cosmological constant but FASTER than matter.
- **No phantom crossing**. The model is strictly quintessence-like at all redshifts.
- **w becomes less negative at high z**: as H increases, V_eff = v₀ E^{2γ_r} grows, making DE act more like matter (w → -2/3 asymptotically).

This is the physical signature of the radion drift: the extra-dimensional modulus slowly evolves, feeding energy into the dark energy sector. The rate is set by γ_r.

---

## 4. CPL Fit

### 4.1. E²-based fit (what DESI measures)

DESI constrains dark energy by fitting E²(a) to the CPL form:

E²_CPL(a) = Ω_m a⁻³ + Ω_r a⁻⁴ + Ω_DE a^{-3(1+w₀+wₐ)} exp(-3wₐ(1-a))

Fitting E²_Meridian to this form over a ∈ [0.3, 1.0]:

| | Meridian | DESI DR2 | ΛCDM |
|--|---------|---------|------|
| w₀ | **-0.830** | -0.752 | -1.000 |
| wₐ | **+0.284** | -0.86 | 0.000 |

### 4.2. Fit quality

The CPL parameterization captures the Meridian E(a) with extraordinary precision:

- **Max |ΔE/E|** = 0.016%
- **RMS |ΔE/E|** = 0.006%

The CPL is an excellent approximation because the Meridian w(a) is nearly linear:

| z | w(a) actual | w(a) CPL | Difference |
|---|------------|---------|------------|
| 0.0 | -0.827 | -0.830 | +0.003 |
| 0.5 | -0.735 | -0.735 | +0.000 |
| 1.0 | -0.687 | -0.688 | +0.001 |
| 2.0 | -0.645 | -0.641 | -0.004 |

The maximum w(a) deviation from CPL is 0.006 — negligible compared to DESI error bars (~0.06). **The CPL comparison is fair and accurate.**

---

## 5. DESI Compatibility

### 5.1. Pulls and χ²

Using the DESI DR2 constraints (symmetrized wₐ error: σ_wₐ = 0.265):

| Model | w₀ pull | wₐ pull | χ²_DESI |
|-------|---------|---------|---------|
| **Meridian** | -1.3σ | **+4.3σ** | **20.4** |
| ΛCDM | -4.3σ | +3.2σ | 28.8 |

**Δχ² = -8.4 (Meridian better than ΛCDM)**

### 5.2. Where Meridian wins, where it loses

| Dimension | Meridian | ΛCDM | Winner |
|-----------|---------|------|--------|
| w₀ | -0.83 (1.3σ from DESI) | -1.00 (4.3σ) | Meridian |
| wₐ | +0.28 (4.3σ from DESI) | 0.00 (3.2σ) | ΛCDM |
| **Combined** | χ² = 20.4 | χ² = 28.8 | **Meridian** |

The model wins on w₀ and loses on wₐ. The w₀ advantage is larger because ΛCDM's w₀ = -1 is badly wrong (4.3σ from DESI), while Meridian's wₐ = +0.28 is wrong by 4.3σ but from a smaller baseline (|Δwₐ| = 1.14 vs |Δw₀| = 0.25).

### 5.3. The wₐ sign discrepancy

This is the central finding of D6.6:

**DESI measures wₐ < 0** (dark energy was more negative in the past → phantom crossing).
**Meridian predicts wₐ > 0** (dark energy was less negative in the past → quintessence).

These are **opposite** w(a) slopes. The physical origin is clear:

- **DESI wₐ < 0**: requires dark energy that was STRONGER (more negative pressure) at high z and is weakening. This is phantom-like behavior.
- **Meridian wₐ > 0**: V_eff = v₀ E^{2γ_r} grows with H, making dark energy density INCREASE at high z. For ρ_DE growing while the universe expands, w must be ABOVE -1. More growth → w further from -1 → wₐ > 0.

**The radion drift mechanism fundamentally produces quintessence, not phantom behavior.**

---

## 6. Sensitivity to γ_r

How does the DESI χ² depend on the radion drift index?

| γ_r | w₀ (E² CPL) | wₐ (E² CPL) | χ²_DESI |
|-----|-------------|-------------|---------|
| 0.0 | -1.000 | -0.001 | 28.8 |
| 0.1 | -0.968 | +0.091 | 26.8 |
| 0.2 | -0.930 | +0.171 | 24.6 |
| 0.3 | -0.884 | +0.236 | 22.3 |
| **0.40** | **-0.830** | **+0.284** | **20.4** |
| 0.5 | -0.762 | +0.312 | 19.6 |
| 0.6 | -0.679 | +0.314 | 21.2 |
| 0.8 | -0.442 | +0.221 | 45.2 |
| 1.0 | -0.001 | +0.005 | 178.1 |

Key observations:

1. **Minimum χ²_DESI ≈ 19.6 at γ_r ≈ 0.5** — the DESI-optimal γ_r is slightly above our fiducial (0.40). But the difference is small (Δχ² = 0.8).

2. **wₐ is ALWAYS positive** for 0 < γ_r < 1. The sign of wₐ is a structural prediction, not tunable.

3. **w₀ tracks γ_r monotonically**: larger γ_r → w₀ further from -1. At γ_r = 0.5, w₀ = -0.76 — almost exactly the DESI central value.

4. **The wₐ tension is irreducible** within the minimal Meridian model. No choice of γ_r can produce wₐ < 0 with V_eff = v₀ E^{2γ_r}.

---

## 7. w(a) at DESI Effective Redshifts

| z | w Meridian | w CPL(Meridian) | w CPL(DESI) | ΛCDM |
|---|-----------|----------------|-------------|------|
| 0.000 | -0.827 | -0.830 | -0.752 | -1.0 |
| 0.295 | -0.766 | -0.765 | -0.948 | -1.0 |
| 0.510 | -0.734 | -0.734 | -1.043 | -1.0 |
| 0.706 | -0.712 | -0.713 | -1.108 | -1.0 |
| 0.930 | -0.692 | -0.693 | -1.166 | -1.0 |
| 1.317 | -0.669 | -0.669 | -1.241 | -1.0 |
| 1.491 | -0.661 | -0.660 | -1.267 | -1.0 |
| 2.330 | -0.637 | -0.632 | -1.354 | -1.0 |

At z = 0.5 (where DESI has its strongest constraining power): Meridian gives w = -0.73, DESI best-fit gives w = -1.04, ΛCDM gives w = -1.0. Meridian is 0.30 above the DESI best-fit, while ΛCDM is 0.04 above. At this specific redshift, ΛCDM is closer to DESI.

But DESI doesn't measure w(z) point by point — it measures w₀ and wₐ as integrated constraints. The w₀ advantage for Meridian outweighs the wₐ disadvantage in the integrated χ².

---

## 8. Implications for the Model

### 8.1. What works

- **w₀ is natural**: The model produces w₀ ≈ -0.83 from first principles — the radion drift index γ_r ≈ 0.4 is derived from the 5D geometry (D6.1), not tuned to match DESI.
- **Dynamical DE is structural**: Unlike ΛCDM, the model MUST produce w ≠ -1. This is a consequence of the radion-dark energy coupling, not a parameter choice.
- **Beats ΛCDM on combined (w₀, wₐ)**: Δχ² = -8.4, driven by the w₀ advantage.

### 8.2. What doesn't work

- **wₐ sign is wrong**: +0.28 vs -0.86. This is a 4.3σ discrepancy.
- **No phantom crossing**: The model is strictly quintessence-like. DESI's best-fit requires phantom behavior.
- **Distances are systematically short** (D6.5): the same γ_r that gives good w₀ also makes comoving distances 3-5% too short at z > 0.5.

### 8.3. The extended cuscuton path

The Phase 5 analysis (D5.4) identified the extended cuscuton (Iyonaga-Takahashi-Kobayashi 2018) as the resolution to the H₀ bottleneck. How does this affect w(a)?

The extended cuscuton modifies K_eff from a pure 1/H² scaling to a more general K(H). If K(H) grows faster than 1/H² at high z, it can:

1. **Provide negative pressure at high z** → push w below -1 → enable phantom crossing
2. **Reduce the effective V_eff growth** → lengthen distances → fix the BAO shortfall
3. **Shift wₐ negative** → align with DESI

This is precisely what the Horndeski G₂(φ, X) and G₃(φ, X) terms do. The spectral action (Phase 5) constrains which G₂, G₃ nature selects. The wₐ sign is the observational discriminator between minimal and extended Meridian.

---

## 9. Falsifiable Predictions

### 9.1. Minimal Meridian (current model)

| Prediction | Value | Testable by |
|-----------|-------|------------|
| w₀ | -0.83 ± 0.02 | DESI Y5, Euclid |
| wₐ | **+0.28** (positive) | DESI Y5 (σ_wₐ → 0.1) |
| Phantom crossing | **None** | Any survey detecting w < -1 |
| w(z = 0.5) | -0.73 | Euclid spectroscopic |
| c²_s (DE sound speed) | → ∞ | CMB ISW cross-correlation |

### 9.2. Extended Meridian (with Horndeski G₂, G₃)

| Prediction | Value | Testable by |
|-----------|-------|------------|
| w₀ | -0.75 to -0.85 | Same range, refined |
| wₐ | **< 0** (negative possible) | DESI Y5 |
| Phantom crossing | **Yes** (from G₃ braiding) | Same |
| Distance shortfall | **Reduced/eliminated** | DESI Y5 BAO |

### 9.3. Decisive test

**If DESI Y5 confirms wₐ < -0.3 at > 3σ, the minimal Meridian is ruled out.** The extended cuscuton becomes mandatory. If wₐ turns out closer to 0 (within the current error bars), both versions remain viable and the w₀ prediction becomes the primary test.

---

## 10. Comparison Summary

| Property | ΛCDM | Minimal Meridian | DESI DR2 |
|----------|------|-----------------|---------|
| w₀ | -1.000 | -0.830 | -0.752 ± 0.058 |
| wₐ | 0.000 | +0.284 | -0.86 ± 0.27 |
| w₀ pull from DESI | 4.3σ | 1.3σ | — |
| wₐ pull from DESI | 3.2σ | 4.3σ | — |
| χ²_DESI | 28.8 | 20.4 | — |
| Phantom crossing | No (w = -1) | No (w > -1) | Yes (z ≈ 0.3) |
| Distance fit (BAO) | Excellent | 2-3σ short | — |
| Physical mechanism | None (constant) | Radion drift | — |
| Parameters | 0 (fixed) | 2 (from 5D geometry) | 2 (fitted) |

---

## 11. Deliverable Checklist

- [x] w(a) trajectory computed numerically
- [x] CPL fit (E²-based, what DESI measures)
- [x] CPL fit quality verified (RMS ΔE/E = 0.006%)
- [x] DESI compatibility: pulls and χ²
- [x] ΛCDM comparison: Meridian wins by Δχ² = -8.4
- [x] wₐ sign discrepancy identified and explained physically
- [x] No phantom crossing (structural prediction)
- [x] γ_r sensitivity scan
- [x] w(z) at DESI effective redshifts
- [x] Extended cuscuton path to fix wₐ
- [x] Falsifiable predictions tabulated
- [x] Decisive test identified: DESI Y5 wₐ sign
