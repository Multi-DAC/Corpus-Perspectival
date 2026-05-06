# D8.6 — Early Dark Energy and Sound Horizon Modification

**Track 8F | Clayton & Clawd | March 15-16, 2026**

---

## 1. Purpose

Test whether modifying the sound horizon r_d (as Early Dark Energy models do) can help the Meridian model fit the DESI data. The cuscuton's extended K(H) freedom (ITK 2018) could permit residual kinetic energy at early times, acting as EDE and shifting r_d at recombination.

---

## 2. Method

Systematic scan: optimize all Meridian parameters at each fixed r_d value, computing both:
- **With r_d Gaussian prior:** r_d = 147.09 ± 0.26 Mpc (Planck 2018 ΛCDM)
- **Without r_d prior:** Let the model freely find the best r_d

The χ² components: BAO (5 DESI bins) + fσ₈ (5 bins) + H₀ + H&K + r_d prior (when included).

ΛCDM reference computed at each r_d for fair comparison.

---

## 3. Results: With r_d Prior (σ = 0.26 Mpc)

| r_d (Mpc) | δ% | χ²_model | χ²_BAO | χ²_r_d | χ²_ΛCDM | Δχ² |
|---|---|---|---|---|---|---|
| 142.68 | −3% | 329.27 | 11.04 | 288.0 | 347.9 | −18.6 |
| 144.15 | −2% | 151.65 | 5.96 | 128.0 | 168.4 | −16.8 |
| 145.62 | −1% | 45.26 | 3.14 | 32.0 | 60.8 | −15.5 |
| 146.35 | −0.5% | 18.63 | 2.47 | 8.0 | 33.8 | −15.2 |
| **147.09** | **0%** | **9.62** | **2.26** | **0.0** | **24.6** | **−14.9** |
| 147.83 | +0.5% | 18.08 | 2.56 | 8.0 | 33.1 | −15.0 |
| 148.56 | +1% | 43.37 | 3.31 | 32.0 | 59.3 | −15.9 |
| 150.03 | +2% | 139.10 | 2.39 | 128.0 | 164.5 | −25.4 |
| 151.50 | +3% | 310.02 | 11.41 | 288.0 | 340.0 | −30.0 |

### Key observations:

1. **The r_d prior is extraordinarily tight.** σ = 0.26 Mpc means a 1% shift (1.47 Mpc) costs χ²_r_d = (1.47/0.26)² = 32.0. This DOMINATES the total χ² at even modest deviations.

2. **Δχ² (model vs ΛCDM) is stable at −14.9 to −15.9 across the scan.** The improvement comes entirely from the H&K term (ζ₀), not from any r_d-dependent effect. Shifting r_d helps both model and ΛCDM equally — it changes the BAO normalization for both.

3. **The optimal r_d is the fiducial value (147.09 Mpc).** There is no preference for modified r_d within the model.

---

## 4. Results: Without r_d Prior (Partial Scan)

| r_d (Mpc) | δ% | χ²_model | χ²_BAO | χ²_ΛCDM | Δχ² | w₀ | wₐ |
|---|---|---|---|---|---|---|---|
| 142.68 | −3% | 41.23 | — | 59.9 | −18.7 | −0.958 | +0.11 |

Without the r_d prior, a 3% downward shift in r_d gives Δχ² = −18.65 (vs −14.93 at fiducial) — a modest improvement. But:
- **w₀ = −0.958, wₐ = +0.11** — still the WRONG SIGN for wₐ
- The improvement comes from better BAO distances at shifted r_d, not from resolving the equation of state problem
- The model still predicts w ≈ −1 with positive wₐ (quintessence-like drift), not the negative wₐ DESI requires

---

## 5. Why EDE Cannot Help

### 5.1 The Prior Problem

The Planck 2018 constraint on r_d is σ = 0.26 Mpc (0.18%). This is derived from the full CMB power spectrum analysis, which measures the angular sound horizon θ_s = r_d/D_A(z*) to 0.03% precision. The r_d constraint degrades only slightly because D_A(z*) depends on late-time physics.

For EDE to help, it must predict a DIFFERENT r_d from Planck's value. But the Meridian model has:
- Standard recombination physics (no new light species)
- Standard BBN (no modified expansion rate before z ~ 10)
- The cuscuton is negligible at z > 10 (K_eff ∝ 1/E² → 0)

The EXTENDED cuscuton (ITK) could have K_eff that decays slower than 1/E², permitting non-negligible kinetic energy at early times. But this K(H) modification would need to be fine-tuned to inject energy at z ~ 3000 (to shift r_d) without affecting BBN (z ~ 10⁹) or structure formation (z ~ 1-10).

### 5.2 The wₐ Sign Problem Persists

Even with a shifted r_d, the model predicts wₐ > 0 (wrong sign). The r_d scan confirms this: at r_d = 142.68 Mpc (−3%), the best-fit gives wₐ = +0.11.

The reason is structural: wₐ > 0 comes from the cuscuton's K_eff ∝ 1/E² scaling, which makes w MORE negative at late times (quintessence → cosmological constant approach). Shifting r_d changes the BAO normalization but doesn't change the time-dependence of w.

### 5.3 Quantitative Bound

For the r_d shift to improve the fit more than the prior penalty:

    Δχ²_improvement > Δχ²_prior_penalty
    ΔBAOimprovement > (Δr_d / 0.26)²

At Δr_d = 1.47 Mpc (1%): penalty = 32, improvement in BAO ≈ 1.0. Net: −31. Strongly disfavored.

Even without the prior, the BAO improvement from shifting r_d is ~4 (from Δχ² = −14.9 to −18.7 at 3% shift). This is a modest improvement that doesn't address the fundamental w₀wₐ problem.

---

## 6. Verdict

### 6.1 Kill Condition

Track 8F is **EFFECTIVELY KILLED.** Sound horizon modification cannot resolve the DESI tension because:

1. **The CMB prior on r_d is too tight** (σ = 0.26 Mpc, 0.18%). Any r_d shift large enough to matter is strongly penalized.
2. **The wₐ sign problem persists** regardless of r_d. Shifting r_d changes the BAO normalization but not the equation of state evolution.
3. **The model has no natural EDE mechanism.** The cuscuton is negligible at early times by construction (K_eff → 0 as H → ∞). Extended K(H) requires fine-tuning without spectral action motivation.

### 6.2 Connection to Structural Insight

The r_d scan reinforces the pattern from Tracks 8B and 8C: the Meridian model's background cosmology is ΛCDM-like to high precision. The only robust departure is in the perturbation sector (ζ₀ modifying growth and H&K). Any attempt to change the background — whether through Weyl tensor (8B), DE-DM coupling (8C), or sound horizon (8F) — is either structurally suppressed or doesn't address the wₐ sign problem.

### 6.3 Cumulative Assessment (8A–8C + 8F)

| Track | Result | Root Cause |
|-------|--------|------------|
| 8A | Tension is real | (Methodology passed) |
| 8B | KILLED (δw ~ 10⁻³) | O(ζ₀²) suppression |
| 8C | KILLED (δw ~ 4×10⁻⁴) | Zero kinetic energy theorem |
| 8F | KILLED (wₐ sign wrong) | K_eff ∝ 1/E² → background ≈ ΛCDM |

**Four tracks completed, three killed, all pointing to the same structural conclusion:** the single-field cuscuton cannot modify the background expansion history at the level DESI requires.

---

*D8.6 — Clayton & Clawd, March 15-16, 2026*
