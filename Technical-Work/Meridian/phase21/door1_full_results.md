# Door 1 Complete: Spin-Dependent KK Thresholds with Anarchic Fermion Profiles

**Date:** 2026-03-23
**Phase:** 21, Track A
**Script:** `door1_full_anarchic.py`

---

## Executive Summary

The spin-dependent KK threshold calculation is now complete with:
1. **Fixed Bessel zero finder** — `brentq`-based root finding for arbitrary order J_nu(x), verified to machine precision
2. **Full Agashe-Perez-Soni anarchic fermion profiles** — 15 species with individual bulk mass parameters c
3. **Species-by-species beta function decomposition** — proper (b_1, b_2, b_3) per species from gauge quantum numbers
4. **Comprehensive scan** over profiles, scales, and extreme cases

**Result:** The spin-dependent KK threshold effect is **real but small**. For realistic APS profiles, it closes **< 1% of the gap**. Even with extreme IR/UV splits, it reaches only ~5%. The theoretical maximum from uniform c-scans is ~57% (at c = -0.5, where fermions match scalars), but this requires ALL fermions to be maximally IR-localized, which is excluded by the fermion mass hierarchy.

**Verdict: Door 1 is a perturbative correction, not a resolution mechanism.**

---

## Physical Setup

| Parameter | Value |
|-----------|-------|
| kL (warp factor) | 35 |
| k_IR | 783 GeV |
| k (5D cutoff) | 1.24 x 10^18 GeV |
| Lambda (NCG cutoff) | = k |
| m_KK1 (first gauge KK mass) | 3000 GeV |
| KK modes per species | 200 |
| Computation time | 3.3 seconds |

### KK Spectra by Spin

| Field | Bessel equation | First zero | m_KK1 (GeV) |
|-------|----------------|------------|--------------|
| Gauge bosons (spin-1) | J_1(x) = 0 | 3.832 | 3000 |
| Fermions, c = 0 | J_{1/2}(x) = 0 | pi = 3.142 | 2460 |
| Scalars (spin-0) | J_0(x) = 0 | 2.405 | 1883 |

**Ordering:** scalar < fermion(c=0) < gauge boson at each KK level.

For fermions with c > 0 (UV-localized): J_{c+1/2} zeros increase, making them heavier.
For fermions with c < 0 (IR-localized): |c+1/2| decreases toward J_0, making them lighter.

---

## Results by Case

### Case 1: Flat Profile (all c = 0)

All 15 fermion species at c = 0 (conformal limit). This isolates the pure gauge-vs-fermion spectral difference.

| Quantity | Value |
|----------|-------|
| S_gauge | 5906.44 |
| S_fermion | 5907.82 |
| S_scalar | 5909.32 |
| S_gauge - S_fermion | -1.378 |
| sin^2 shift | +0.008367 |
| Gap fraction | **+28.0%** |

The c = 0 case closes 28% of the remaining gap. This is the largest effect achievable with a UNIFORM profile, because at c = 0 the fermion-gauge spectral difference is maximized while keeping all fermions at the same mass.

### Case 2: APS Benchmark Anarchic Profile

Realistic fermion bulk masses from the Agashe-Perez-Soni model:

| Species | c | nu = |c+1/2| | m_KK1 (GeV) | S_f |
|---------|---|-------------|-------------|-----|
| Q3_L (top/bottom doublet) | 0.35 | 0.85 | 2841 | 5906.85 |
| t_R (top singlet) | -0.15 | 0.35 | 2291 | 5908.26 |
| b_R (bottom singlet) | 0.45 | 0.95 | 2947 | 5906.58 |
| L3_L (tau doublet) | 0.45 | 0.95 | 2947 | 5906.58 |
| tau_R | 0.40 | 0.90 | 2894 | 5906.71 |
| Q2_L (charm/strange) | 0.55 | 1.05 | 3053 | 5906.31 |
| c_R | 0.55 | 1.05 | 3053 | 5906.31 |
| s_R | 0.60 | 1.10 | 3105 | 5906.18 |
| L2_L (muon doublet) | 0.55 | 1.05 | 3053 | 5906.31 |
| mu_R | 0.60 | 1.10 | 3105 | 5906.18 |
| Q1_L (up/down) | 0.65 | 1.15 | 3157 | 5906.05 |
| u_R | 0.70 | 1.20 | 3209 | 5905.92 |
| d_R | 0.70 | 1.20 | 3209 | 5905.92 |
| L1_L (electron doublet) | 0.65 | 1.15 | 3157 | 5906.05 |
| e_R | 0.75 | 1.25 | 3261 | 5905.79 |

| Quantity | Value |
|----------|-------|
| sin^2 shift | -0.000161 |
| Gap fraction | **-0.54%** |
| Direction | WIDENING (bad) |

**Key finding:** The APS benchmark actually WIDENS the gap by 0.5%. This is because the anarchic c-values average to c ~ 0.5, where the fermion KK spectrum nearly matches the gauge boson spectrum (both near J_1 zeros), eliminating the spectral difference that drives the correction.

### Case 3: Uniform c-Value Scan

All fermions at the same c. Maps the full parameter space:

| c | sin^2 shift | Gap fraction |
|---|------------|--------------|
| -0.50 | +0.016967 | **+56.9%** |
| -0.30 | +0.013443 | +45.1% |
| -0.10 | +0.010035 | +33.6% |
| 0.00 | +0.008367 | +28.0% |
| 0.10 | +0.006719 | +22.5% |
| 0.20 | +0.005089 | +17.1% |
| 0.30 | +0.003476 | +11.7% |
| 0.40 | +0.001878 | +6.3% |
| **0.50** | **+0.000294** | **+1.0%** |
| 0.60 | -0.001277 | -4.3% |
| 0.70 | -0.002835 | -9.5% |
| 0.80 | -0.004383 | -14.7% |

**Zero crossing at c ~ 0.5:** When the fermion Bessel order nu = c + 1/2 = 1.0, the fermion spectrum matches the gauge boson spectrum (J_1 zeros). Above this, the effect reverses sign.

### Case 4: APS Profile with Shifts

Shift all 15 c-values by delta_c uniformly:

| delta_c | sin^2 shift | Gap fraction | Direction |
|---------|------------|--------------|-----------|
| -0.30 | +0.004622 | +15.5% | CLOSING |
| -0.20 | +0.003013 | +10.1% | CLOSING |
| -0.10 | +0.001419 | +4.8% | CLOSING |
| 0.00 | -0.000161 | -0.5% | WIDENING |
| +0.10 | -0.001728 | -5.8% | WIDENING |
| +0.20 | -0.003283 | -11.0% | WIDENING |
| +0.30 | -0.004828 | -16.2% | WIDENING |

**Sensitivity:** ~5% gap closure per 0.1 shift in mean c. The APS benchmark sits right at the zero-crossing, which is NOT a coincidence — the top mass determines the APS c-values, and the resulting average c ~ 0.5 happens to nearly cancel the spin-dependent effect.

### Case 5: KK Mass Scale Dependence

APS benchmark, varying m_KK1:

| m_KK1 (GeV) | Gap fraction |
|-------------|-------------|
| 1000 | -0.57% |
| 3000 | -0.54% |
| 10000 | -0.51% |
| 20000 | -0.49% |

**Insensitive to KK scale.** The spin-dependent correction is a ratio effect (gauge vs fermion spectral sums), and both scale the same way with k_IR. This is expected: the correction comes from the Bessel zero pattern, which is independent of the overall mass scale.

### Case 6: Extreme IR/UV Split

Maximally split profile (top at c = -0.5, electron at c = 1.0):

| Quantity | Value |
|----------|-------|
| sin^2 shift | +0.001470 |
| Gap fraction | **+4.9%** |
| Direction | CLOSING |

Even with an unrealistically extreme spread, the effect is only ~5%.

---

## The Fermion Anarchy Effect

The detailed mechanism is the **correlation between a species' localization (c-value) and its gauge quantum numbers**.

For the APS benchmark:

| Gauge group | Actual weighted sum | Universal sum | Anarchy effect |
|-------------|-------------------|---------------|----------------|
| U(1) | 23625.95 | 23625.59 | **+0.36** |
| SU(2) | 23625.52 | 23625.59 | **-0.08** |
| SU(3) | 23625.86 | 23625.59 | **+0.26** |

The top quark (c_tR = -0.15, most IR-localized) has the largest S_f and contributes heavily to b_1 (large hypercharge Y = 2/3) and b_3 (color triplet). This preferentially enhances U(1) and SU(3), but the effect is tiny because all KK sums S_f differ by only ~3 parts in 6000 across the full range of c values.

---

## Why the Effect Is Small

Three fundamental reasons:

1. **Bessel zero convergence:** For large n, j_{nu,n} ~ n*pi + (nu/2 - 1/4)*pi/n. The spectral difference between different orders shrinks as 1/n. The KK sum difference is therefore only logarithmic: Delta S ~ (1/2) * ln(N_modes), not linear.

2. **Enormous KK sums:** Each S_f ~ 5906, so differences of O(1) are O(10^{-4}) fractional corrections.

3. **APS cancellation:** The fermion mass hierarchy requires c-values that average near 0.5, precisely where the fermion spectrum matches the gauge boson spectrum. This is a structural feature of the RS model, not a coincidence.

---

## Implications for the 12% Gap

1. **Door 1 is not the answer.** The spin-dependent KK threshold effect is a real O(10^{-4}) correction to sin^2(theta_W), contributing at most a few percent of the 12% gap for realistic profiles.

2. **The APS cancellation is robust.** The SM fermion mass hierarchy constrains the c-values to a range where the effect nearly vanishes. You cannot simultaneously explain the fermion masses and get a large spin-dependent threshold correction.

3. **The logarithmic convergence is structural.** No amount of profile engineering can overcome the 1/n suppression of Bessel zero differences at high KK level.

4. **The T11 structural ceiling (29%) is not threatened or assisted.** Door 1 operates at a level too small to interact with the primary gap mechanisms (non-perturbative, F-theory embedding, twisted triples).

---

## Technical Notes

- **Bessel zero finder:** `brentq`-based, verified against `jn_zeros` for integer orders (machine precision agreement). For non-integer orders, verified by evaluating J_nu(z) at found zeros (|J| < 10^{-14}).
- **Beta function decomposition:** Verified sum per generation = (4/3, 4/3, 4/3) for all three gauge groups.
- **GUT normalization:** alpha_1 uses (5/3) factor. sin^2(theta_W) formula verified: gives 3/8 at unification.
- **200 KK modes per species:** Sufficient (all below Lambda for all tested profiles).
- **Script runtime:** 3.3 seconds (Python 3.12, Windows).

---

## Files

| File | Content |
|------|---------|
| `door1_full_anarchic.py` | Complete calculation script |
| `door1_full_results.md` | This analysis |
| `door1_spin_dependent_kk.py` | Previous (incomplete) version |
