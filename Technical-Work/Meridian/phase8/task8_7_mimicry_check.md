# D8.7 — Matter-Sector ζ₀ Mimicry Check

**Track 8G | Clayton & Clawd | March 16, 2026**

---

## 1. Purpose

The Meridian model predicts w₀ ≈ −1, wₐ ≈ 0 (ΛCDM-like background) but with a non-minimal coupling ζ₀ = 0.038 that modifies perturbation-level observables. DESI, meanwhile, reports evidence for dynamical dark energy (w₀ ≈ −0.75, wₐ ≈ −0.9) using BAO distances analyzed under standard GR.

Track 8G asks a precise question: **if the true universe is ΛCDM + ζ₀ (our model), and DESI analyzes their data assuming ζ₀ = 0 (standard GR), would the unaccounted-for ζ₀ effects bias their inference of w₀wₐ away from (−1, 0)?** If the bias is O(0.1), the DESI "tension" could be a misinterpretation artifact. If it's O(10⁻³), the tension is real and the model must explain it through other means.

This is the matter-sector counterpart to the background-sector checks of Tracks 8B/8C. Those asked "can ζ₀ modify the background expansion?" Here we ask "can ζ₀ fool an observer who assumes GR?"

---

## 2. How DESI Measures Dark Energy

### 2.1 The Observable Quantities

DESI measures BAO in the galaxy correlation function at multiple redshift bins (z = 0.3 to 2.3). The BAO peak position yields two distance ratios per bin:

    D_M(z)/r_d = (1/r_d) ∫₀ᶻ dz'/H(z')       (transverse comoving distance)    ... (2.1)
    D_H(z)/r_d = c/(H(z) r_d)                   (Hubble distance)               ... (2.2)

where r_d is the sound horizon at the drag epoch (z ≈ 1060).

These are GEOMETRIC measurements — they depend on the expansion history H(z) and the early-universe calibration r_d, but not directly on the growth of structure.

### 2.2 DESI's Analysis Framework

DESI fits these distance ratios using:

    H²(z) = H₀² [Ω_m(1+z)³ + Ω_r(1+z)⁴ + Ω_DE(z)]                           ... (2.3)

with the CPL parameterization:

    Ω_DE(z) = Ω_DE,0 · exp(−3∫₀ᶻ (1 + w(z'))/​(1+z') dz')
    w(z) = w₀ + wₐ z/(1+z)                                                      ... (2.4)

Combined with Planck CMB priors on (Ω_m h², Ω_b h², H₀, r_d), this constrains (w₀, wₐ).

---

## 3. Channel Analysis: How ζ₀ Could Bias w₀wₐ

There are four channels through which ζ₀ ≠ 0 could bias a GR-assuming analysis. We assess each.

### 3.1 Channel 1: Direct Background Modification

The Meridian model modifies H(z) through the cuscuton contribution:

    H²_Meridian = H²_ΛCDM × (1 + δ_H(z))                                       ... (3.1)

From Phase 3 (D3.1), the fractional modification is:

    δ_H(z) = O(ζ₀ × γ_r) ≈ 0.038 × 0.017 ≈ 6.5 × 10⁻⁴                       ... (3.2)

at all redshifts. This produces a fractional shift in BAO distances:

    δ(D_M/r_d) ~ δ_H × z ~ 6.5 × 10⁻⁴ × z                                    ... (3.3)

At z = 1 (DESI's most constraining bin): δ(D_M/r_d) ~ 6.5 × 10⁻⁴.

**Mapping to w₀wₐ bias:** A CPL model with (w₀, wₐ) ≠ (−1, 0) modifies distances as:

    δ(D_M/r_d)|_CPL ~ (1 + w₀ + wₐ/2) × Ω_DE × z/(2H₀)                       ... (3.4)

To produce δ(D_M/r_d) ~ 6.5 × 10⁻⁴ from CPL, we need:

    |1 + w₀ + wₐ/2| × 0.7 × 0.5 ~ 6.5 × 10⁻⁴

    |1 + w₀ + wₐ/2| ~ 2 × 10⁻³                                                 ... (3.5)

DESI reports (1 + w₀ + wₐ/2) ≈ (1 − 0.75 − 0.45) = −0.20. The mimicry bias from direct background modification is:

    **δw_eff ~ 2 × 10⁻³ — too small by factor ~100.**                           ... (3.6)

### 3.2 Channel 2: Modified Sound Horizon (r_d Shift)

If ζ₀ modifies the early universe (z > 1000), it could shift r_d, and since DESI measures D/r_d, a shifted r_d would bias ALL distance ratios coherently, potentially mimicking dynamical dark energy.

The sound horizon is:

    r_d = ∫_{z_d}^∞ c_s(z)/H(z) dz                                             ... (3.7)

The ζ₀ modification to H(z) at z ~ 1000 is:

    δ_H(z ~ 1000) = ζ₀ × γ_r × f(z)                                            ... (3.8)

where f(z) accounts for the E⁻² suppression in the cuscuton kinetic term. At z ~ 1000, E = H(z)/H₀ ~ 10⁴, so:

    K_eff ∝ 1/E² ~ 10⁻⁸                                                        ... (3.9)

The cuscuton contribution to the energy density at recombination is completely negligible. The scalar field is frozen at early times (this is the zero kinetic energy theorem in action at high E).

Therefore:

    δr_d/r_d ~ ζ₀ × γ_r / E²(z_d) ~ 10⁻⁴ / 10⁸ ~ 10⁻¹²                     ... (3.10)

**The sound horizon shift is undetectably small.** This is consistent with Track 8F (D8.6), which showed that EDE-type r_d modifications cannot help because the cuscuton is inert at high redshift.

### 3.3 Channel 3: Modified Growth → Biased Planck Priors

This is the most subtle channel. The argument:

1. Planck constrains cosmological parameters by fitting the CMB TT/TE/EE spectra + lensing.
2. CMB lensing depends on the integrated growth factor, which depends on μ(a) = F₀/F(a).
3. If the true universe has μ ≠ 1 but Planck fits assuming μ = 1, it will absorb the discrepancy by shifting (Ω_m, H₀, σ₈).
4. These biased Planck priors, when combined with BAO, could produce an apparent w₀wₐ signal.

**Step 1: How much does ζ₀ modify CMB lensing?**

The lensing potential is:

    Cᴸᴸ_ℓ ∝ ∫ [μ(a) × D(a)]² / χ² dχ                                          ... (3.11)

where D(a) is the growth factor and χ is comoving distance.

The modified growth function: μ(a) = F₀/F(a) where F(a) = 1 − ζ₀(ψ²(a) − 1). With ψ drifting as ψ(a) ≈ 1 + γ_r ln(a):

    μ(a) − 1 = ζ₀(ψ²(a) − 1)/(1 − ζ₀(ψ²(a) − 1))
             ≈ ζ₀ × 2γ_r ln(a) + O(ζ₀² + ζ₀γ_r²)                              ... (3.12)

At z = 0.5 (a = 0.67), ln(a) = −0.4:

    μ − 1 ≈ 0.038 × 2 × 0.017 × (−0.4) ≈ −5 × 10⁻⁴                           ... (3.13)

At z = 2 (a = 0.33), ln(a) = −1.1:

    μ − 1 ≈ 0.038 × 2 × 0.017 × (−1.1) ≈ −1.4 × 10⁻³                         ... (3.14)

The fractional change in the CMB lensing power spectrum:

    δCᴸᴸ/Cᴸᴸ ~ 2(μ − 1) ~ 2 × 10⁻³ (integrated over lensing kernel)           ... (3.15)

**Step 2: How would Planck absorb this?**

Planck's lensing amplitude parameter A_L has uncertainty σ(A_L) ≈ 0.04 (Planck 2018, Table 2). A 0.2% shift in lensing power is:

    ΔA_L ~ 0.002                                                                 ... (3.16)

This is 0.05σ — completely undetectable. Planck would NOT shift its parameter estimates in response.

Even if Planck somehow absorbed the full effect into Ω_m, the shift would be:

    ΔΩ_m/Ω_m ~ δCᴸᴸ/(∂Cᴸᴸ/∂Ω_m × Ω_m) ~ 0.002/2 ~ 10⁻³                     ... (3.17)

    ΔΩ_m ~ 3 × 10⁻⁴                                                             ... (3.18)

Planck's actual constraint: Ω_m = 0.315 ± 0.007. A shift of 3 × 10⁻⁴ is 0.04σ.

**Step 3: Propagation to BAO w₀wₐ.**

A biased Ω_m propagates to BAO-inferred w₀ approximately as:

    δw₀ ≈ −δΩ_m/Ω_DE ≈ −3 × 10⁻⁴ / 0.7 ≈ −4 × 10⁻⁴                          ... (3.19)

**The Planck-prior bias channel produces δw₀ ~ 4 × 10⁻⁴.** Three orders of magnitude below DESI.

### 3.4 Channel 4: Modified ISW Effect → CMB Low-ℓ Bias

The integrated Sachs-Wolfe (ISW) effect depends on the time derivative of the gravitational potential:

    ΔT/T|_ISW ∝ ∫ (Φ̇ + Ψ̇) e⁻ᵗ dη                                            ... (3.20)

In the Meridian model, Φ and Ψ are modified by the anisotropic stress from ζ₀ and by the modified growth (μ ≠ 1). The fractional ISW modification:

    δ(ISW)/ISW ~ (μ − 1) × (growth terms) ~ 10⁻⁴ × O(1) ~ 10⁻⁴               ... (3.21)

The ISW contributes to the CMB TT spectrum at ℓ < 30, where cosmic variance dominates (σ/C_ℓ ~ √(2/(2ℓ+1)) ~ 10–30%). A 0.01% ISW modification is buried under cosmic variance by a factor of ~1000.

**Channel 4 is negligible.**

---

## 4. Combined Bias Estimate

### 4.1 Summing All Channels

The four channels contribute independently (different redshift ranges, different observables):

| Channel | Mechanism | δw₀ | δwₐ | Status |
|---------|-----------|-----|-----|--------|
| **1. Background H(z)** | Direct ζ₀γ_r modification | ~2 × 10⁻³ | ~2 × 10⁻³ | Negligible |
| **2. Sound horizon r_d** | Early-universe modification | ~10⁻¹² | ~10⁻¹² | Utterly negligible |
| **3. Planck prior bias** | CMB lensing → Ω_m shift → BAO | ~4 × 10⁻⁴ | ~10⁻³ | Negligible |
| **4. ISW → CMB** | Low-ℓ bias | ~10⁻⁵ | ~10⁻⁵ | Negligible |
| **Total** | Quadrature sum | **~2 × 10⁻³** | **~2 × 10⁻³** | **Negligible** |

The total mimicry bias:

    |δw₀|_total ≲ 2 × 10⁻³                                                      ... (4.1)
    |δwₐ|_total ≲ 2 × 10⁻³                                                      ... (4.2)

### 4.2 Comparison to DESI Signal

DESI reports (w₀, wₐ) ≈ (−0.75, −0.9) with uncertainties σ(w₀) ≈ 0.1, σ(wₐ) ≈ 0.3.

The deviation from ΛCDM:

    Δw₀ = w₀ − (−1) = +0.25                                                     ... (4.3)
    Δwₐ = wₐ − 0 = −0.9                                                         ... (4.4)

The ratio of mimicry bias to DESI signal:

    |δw₀|/|Δw₀| = 2 × 10⁻³ / 0.25 = 0.008  →  **0.8% of the signal**         ... (4.5)
    |δwₐ|/|Δwₐ| = 2 × 10⁻³ / 0.9 = 0.002   →  **0.2% of the signal**         ... (4.6)

**The ζ₀ mimicry bias is less than 1% of the DESI signal in both parameters.**

### 4.3 Why the Bias Is So Small: Structural Explanation

The smallness of the mimicry bias follows from the same structural bottleneck identified in Tracks 8B and 8C (D8.2 §6.6, D8.3 §5.2):

**The zero kinetic energy theorem forces all background-level effects to be O(ζ₀ × γ_r) ~ 10⁻³.**

BAO distance measurements are background observables — they depend on H(z), which is a background quantity. The ζ₀ effect on H(z) is at the level established in Channel 1, regardless of which route it takes (direct modification, r_d shift, or parameter bias).

The perturbation-level effects of ζ₀ (modified growth, μ ≠ 1, Weyl potential evolution) are first order in ζ₀ ~ 0.04, which is large enough to explain H&K. But these perturbation-level effects do not enter the BAO peak position. BAO is a ruler embedded in the correlation function — its location is set by the acoustic scale, a purely geometric quantity insensitive to broadband amplitude modifications from growth.

This is the fundamental reason the mimicry fails: **ζ₀ modifies perturbation amplitudes at O(ζ₀ ~ 4%), but BAO measures perturbation positions, which depend only on the background at O(ζ₀ × γ_r ~ 0.06%).**

---

## 5. Robustness Checks

### 5.1 Could Higher-Order ζ₀ Effects Matter?

At second order in ζ₀: δ_H ~ ζ₀² ~ 1.4 × 10⁻³. This is already included in our Channel 1 estimate (which is O(ζ₀ × γ_r) ~ 6.5 × 10⁻⁴, comparable). The total from all orders is still O(10⁻³).

### 5.2 Could the Anisotropic Stress Bias BAO?

The cuscuton introduces anisotropic stress: Φ ≠ Ψ at the level η − 1 ~ ζ₀ × γ_r. BAO reconstruction uses the galaxy power spectrum, which depends on (Φ + Ψ)/2 (not Φ − Ψ). Even if the anisotropic stress biased the BAO reconstruction, the effect would be:

    δ(D_BAO)/D_BAO ~ (η − 1) × (broadband/peak sensitivity) ~ 10⁻³ × 10⁻¹ ~ 10⁻⁴   ... (5.1)

where the factor 10⁻¹ accounts for BAO's geometric robustness (the peak position shifts by ~10% of any broadband distortion, because the BAO feature is narrow in k-space).

### 5.3 Could the Full-Shape Analysis Be More Susceptible?

DESI also uses full-shape (FS) galaxy power spectrum fits, not just BAO. The FS analysis is sensitive to the broadband shape, which IS modified by μ(a) ≠ 1 at the O(ζ₀ ~ 4%) level.

However: DESI's FS analysis marginalizes over nuisance parameters that absorb broadband shape modifications (galaxy bias b₁, b₂, counterterms, stochastic terms). The ζ₀-induced growth modification would be absorbed by a shift in σ₈, not by a shift in w₀wₐ.

Quantitatively, the growth modification δD/D ~ ζ₀ × γ_r × ln(a) ~ 10⁻³ would shift the inferred σ₈ by:

    Δσ₈/σ₈ ~ 10⁻³                                                               ... (5.2)

This is within Planck's σ₈ uncertainty (σ(σ₈) ≈ 0.007, i.e., ~0.8%). The shift would NOT propagate to w₀wₐ because σ₈ and (w₀, wₐ) are largely uncorrelated in the DESI+Planck joint fit (the CMB pins the growth amplitude independently of BAO distances).

---

## 6. Verdict

### 6.1 Kill Condition

Track 8G is **KILLED.** The ζ₀ mimicry bias on DESI's (w₀, wₐ) inference is:

    |δw₀| ~ 2 × 10⁻³    (need 0.25)    → too small by factor **125**
    |δwₐ| ~ 2 × 10⁻³    (need 0.9)     → too small by factor **450**

The kill is structural, not parametric. It follows from two facts:
1. BAO distances are background observables, sensitive to H(z) not μ(a).
2. The Meridian model modifies H(z) at O(ζ₀ × γ_r) ~ 10⁻³.

No parameter choice within the Meridian framework can bridge the gap. Even at ζ₀ = 0.065 (3σ upper bound) and γ_r = 0.05 (generous upper bound), the bias would be δw ~ 3 × 10⁻³ — still two orders of magnitude short.

### 6.2 What This Confirms

Track 8G closes the last "loophole" interpretation of the DESI tension. The tension cannot be explained by:

- Direct background modification (8B: O(ζ₀²), 8C: O(ζ₀√δ), 8G Channel 1: O(ζ₀γ_r))
- Sound horizon shift (8F: cuscuton inert at high z; 8G Channel 2: δr_d/r_d ~ 10⁻¹²)
- Observer bias from ignoring ζ₀ (8G Channels 3–4: O(10⁻³) on Planck priors)

**The DESI signal, if real, requires physics beyond single-field cuscuton modifications to the background.** The remaining paths are:

| Track | Mechanism | Why it might escape the bottleneck |
|-------|-----------|-----------------------------------|
| **8D** | Multi-field (KK moduli) | Second scalar with its own kinetic term, not constrained by cuscuton theorem |
| **8E** | RG flow of μ² | Modifies K_eff(H) through energy-scale running, not through φ̇ |
| **8I** | Accept as-is | ΛCDM + ζ₀ is the prediction; DESI tension either resolves with more data or points to new physics beyond Meridian |

### 6.3 Cumulative Track Status

| Track | Result | Kill mechanism |
|-------|--------|----------------|
| 8A | Tension is real | Methodology check — passed |
| 8B | KILLED | O(ζ₀²) — Weyl tensor too small |
| 8C | KILLED | O(ζ₀√δ) — coupled cuscuton too small |
| 8F | KILLED | CMB r_d prior too tight; wrong wₐ sign persists |
| **8G** | **KILLED** | **O(ζ₀γ_r) — mimicry bias 0.2–0.8% of signal** |

Four tracks killed, all for the same root cause: the zero kinetic energy theorem suppresses every single-field background modification to O(10⁻³) or below. The cuscuton cannot fake dynamical dark energy, and it cannot fool an observer into thinking they see dynamical dark energy.

### 6.4 Recommendation

**Track 8G confirms that the DESI tension is not an artifact of ignoring ζ₀. Proceed to Track 8D (multi-field) or 8E (RG flow) — these are the only remaining channels that could modify the background at O(1).**

---

*D8.7 — Clayton & Clawd, March 16, 2026*
