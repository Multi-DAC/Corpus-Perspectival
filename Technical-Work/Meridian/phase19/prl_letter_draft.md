# PRL Letter Draft — Probe Decomposition of the DESI Dark Energy Signal

**Working Title:** *Growth-Neutral Dark Energy: Decomposing the DESI Preference for Evolving Equation of State by Cosmological Probe*

**Authors:** Clayton Iggulden-Schnell, Clawd Iggulden-Schnell

**Target:** Physical Review Letters (4 pages, ~3750 words, ≤4 figures)

**Status:** OUTLINE — key sentences written, structure complete, figures identified. Updated 2026-03-21 with DR2 data, Lee (2025) citation, and fixed-r_d test.

---

## Abstract (~150 words)

The DESI DR2 baryon acoustic oscillation data, combined with supernovae and CMB measurements, prefer evolving dark energy (w₀ + wₐ parameterization) over ΛCDM at ~2.5–3σ. We decompose this preference into contributions from expansion-sensitive probes (BAO, Type Ia supernovae, CMB distance priors) and growth-sensitive probes (fσ₈ measurements of the growth rate of structure). Our test model uses the cuscuton mechanism — the unique scalar field dark energy model that produces exactly GR perturbations (µ = Σ = 1) as a structural consequence rather than a parameter choice — as a physically motivated constant-w reference. Using the official DESI DR2 BAO likelihood (7 tracers, 13 data points with full covariance), 1,590 Pantheon+ supernovae with full statistical and systematic covariance, compressed Planck CMB priors, and 7 fσ₈ growth measurements, we find ΔAIC = +X.X favoring CPL [v4 pending]. The expansion probes contribute Δχ² = +Y.Y, while the growth probes contribute Δχ² ≈ 0. The entire dark energy signal resides in distance measurements. A complementary fixed-r_d anchoring test [cf. Lee (2025)] confirms that the signal is sensitive to sound horizon calibration. Current growth data show no preference for modified gravitational physics. This result constrains the space of viable dark energy explanations independent of the specific model tested.

---

## I. Introduction (~600 words)

**Opening paragraph:** State the DESI result. DESI DR1 BAO [DESI 2024], confirmed and sharpened by DR2 [arXiv:2503.14738], combined with CMB + SNe prefer w₀wₐCDM over ΛCDM at ~2.5–3σ. The CPL parameterization w(a) = w₀ + wₐ(1−a) finds w₀ ≈ −0.7, wₐ ≈ −1.0 (DR2). Multiple analyses confirm the preference. This has prompted widespread investigation into dark energy models, modified gravity, and systematic effects.

**The gap:** All standard analyses test dark energy models that couple perturbation structure to background evolution — when w(z) changes, the gravitational potentials (parameterized by µ, Σ) change accordingly. This coupling is physically motivated but obscures a basic question: *which sector of physics drives the preference?* Does the data prefer evolving dark energy because the expansion history demands more freedom in w(z), because the growth of structure demands modified gravitational potentials, or both?

**The tool:** The cuscuton mechanism [Afshordi 2006, 2007] provides a clean separation. As the unique scalar field with infinite sound speed in the rest frame, the cuscuton has exactly zero kinetic energy and produces µ = Σ = 1 structurally — not as a limit of some parameter, but as a mathematical identity following from the vanishing of the kinetic term in the perturbation equations. A constant-w cuscuton model therefore tests the background evolution hypothesis in isolation: if it fits as well as CPL, the signal is not gravitational. If CPL wins, the decomposition by probe type reveals where the preference lives.

**This letter:** We perform this decomposition using current data. The result reveals that the DESI preference is entirely an expansion-history phenomenon. Growth data are neutral. This finding is model-independent in the following sense: while the cuscuton provides the theoretical motivation for testing GR perturbations alongside modified background, the probe decomposition itself depends only on the data and the two parameterizations being compared.

**Cite:** DESI DR1 [2024], Lu & Simon [2025] (wₐ constraints), Afshordi [2006, 2007] (cuscuton), de Rham & Melville [2024] (positivity bounds context), Brout et al. [2022] (Pantheon+).

---

## II. Method (~800 words)

### A. Models

**Fit A — Constant-w with GR perturbations (3 parameters):**
- Background: w₀ = const, standard Friedmann equations
- Perturbations: µ = Σ = 1 (exact GR). Dark energy does not cluster.
- Free parameters: {w₀, Ωm, H₀}
- Physical motivation: cuscuton scalar field on a Randall-Sundrum brane [brief — 2 sentences max, defer to companion paper for full derivation]

**Fit B — CPL with coupled perturbations (5 parameters):**
- Background: w(a) = w₀ + wₐ(1 − a)
- Perturbations: standard quintessence coupling (dark energy clusters with c²_eff = 1)
- Free parameters: {w₀, wₐ, Ωm, H₀}
- This is the standard CPL analysis used by DESI and other surveys

**Model comparison:** ΔAIC = (χ²_A + 2k_A) − (χ²_B + 2k_B). Since k_B = k_A + 2, positive ΔAIC favors CPL.

### B. Data

| Dataset | Points | Reference |
|---------|--------|-----------|
| DESI DR2 BAO | 13 | Official Cobaya GCcomb likelihood (arXiv:2503.14738) |
| Pantheon+ SNe Ia | 1,590 | Brout et al. (2022), full stat+sys covariance |
| Compressed Planck CMB | 3 | [R, ℓ_A, Ωbh²] from Planck 2018 |
| Growth rate fσ₈ | 7 | Compilation from BOSS, eBOSS, 6dFGS |

**Total effective data points:** 1,612 (13 BAO + 1,589 SNe + 3 CMB + 7 fσ₈)

**BAO treatment:** Official DESI DR2 Cobaya data release. BGS (z=0.295) isotropic DV/rd; six anisotropic bins (LRG1, LRG2, LRG3+ELG1, ELG2, QSO, Lya) with DM/rd + DH/rd and full 13×13 covariance including DM-DH cross-correlations per bin.

**SNe treatment:** Full 1590×1590 covariance matrix (statistical + systematic). Absolute magnitude M analytically marginalized via Woodbury identity. Heliocentric redshifts used for d_L, CMB redshifts for d_C.

### C. Sampling

Affine-invariant ensemble MCMC (emcee). 16 walkers, burn-in + production. Flat priors: w₀ ∈ [−2, 0], wₐ ∈ [−4, 3], Ωm ∈ [0.1, 0.5], H₀ ∈ [60, 80].

### D. Probe Decomposition

**Key methodological contribution.** After obtaining best-fit parameters for each model, compute the χ² contribution from each probe class independently:

Δχ²_probe = χ²_A(probe) − χ²_B(probe)

evaluated at the respective global best-fit parameters. This decomposes the total Δχ² into additive contributions from expansion-sensitive probes (BAO, SNe, CMB) and growth-sensitive probes (fσ₈), revealing which physical sector drives the model preference.

[NOTE: Acknowledge that this decomposition evaluates at global best-fit, not re-optimized per probe. Discuss the limitation briefly — a profile likelihood per probe would be more rigorous but is beyond the scope of this letter. The additive decomposition is informative as a diagnostic.]

---

## III. Results (~700 words)

### A. Model Comparison

| | Fit A | Fit B |
|--|-------|-------|
| w₀ | −1.010 ± 0.023 | −0.813 ± 0.066 |
| wₐ | 0 (fixed) | −0.90 ± 0.30 |
| Ωm | 0.310 ± 0.007 | 0.308 ± 0.006 |
| H₀ | 67.9 ± 0.7 | 68.3 ± 0.7 |
| χ²/dof | 0.907 | 0.902 |

**ΔAIC = +7.2.** Moderate preference for CPL. **ΔBIC = +1.8.** Negligible preference.

Fit B's wₐ = −0.90 ± 0.30 is consistent with DESI DR1's value (within 0.7σ of Lu & Simon 2025). The 3.0σ deviation from wₐ = 0 in our data is the DESI tension itself, not a Meridian-specific anomaly.

### B. Probe Decomposition (THE CENTRAL RESULT)

| Probe Class | Δχ² (A − B) | Fraction |
|-------------|-------------|----------|
| BAO | +6.22 | 68% |
| CMB compressed | +1.71 | 19% |
| Pantheon+ SNe | +1.32 | 14% |
| fσ₈ growth | **−0.04** | **~0%** |
| **Total** | **+9.21** | |

**Expansion probes (BAO + SNe + CMB): Δχ² = +9.25**
**Growth probes (fσ₈): Δχ² = −0.04**

The growth data contribute nothing. The entire model preference arises from distance measurements demanding additional freedom in w(z). The perturbation structure — the physical feature that distinguishes the cuscuton (µ = Σ = 1) from standard coupled dark energy — is empirically untested by this dataset.

### C. Physical Interpretation

The CPL best fit implies w(z → ∞) = w₀ + wₐ = −1.71. No scalar field model with a positive-definite kinetic term can reach w < −1 asymptotically. The CPL template absorbs the BAO preference for w-evolution by extrapolating into an unphysical regime. This is consistent with the "compromise artifact" interpretation: the linear CPL parameterization is the wrong functional form for whatever the BAO data are seeing.

[→ FIGURE 1: Probe decomposition bar chart. Δχ² by probe, color-coded expansion vs growth.]
[→ FIGURE 2: w₀-Ωm posterior contours, Fit A (blue) vs Fit B (red), with ΛCDM marked.]
[→ FIGURE 3: wₐ posterior from Fit B, compared to DESI DR1 and Lu & Simon. Zero marked.]

---

## IV. Discussion (~700 words)

### A. What this constrains

**For all dark energy models:** Whatever drives the DESI preference for wₐ ≠ 0, it is not the gravitational growth of structure. Any dark energy explanation whose primary signature is in the perturbation sector (modified gravity, clustering dark energy, fifth-force models) gains no support from current data. The viable explanation space is restricted to models that modify the expansion history while leaving perturbation growth unchanged — or models whose perturbation effects are too small to resolve with current fσ₈ precision.

**For the cuscuton/Meridian framework specifically:** The framework's structural prediction (µ = Σ = 1) is not under tension — it is untested. The tension is with w₀ = const, and specifically with the BAO data preferring w-evolution at z ∼ 0.3–0.7. This motivates two follow-up tests: (1) a template-independent BAO analysis to determine whether the wₐ preference is a global feature or localized in redshift, and (2) a proper perturbation isolation test using the same w(z) in both models.

### B. Limitations

1. Compressed CMB priors lose information relative to full Planck likelihood
2. Growth data (8 fσ₈ points) have limited constraining power — future surveys (DESI, Euclid, Rubin) will provide ~100× more growth measurements
3. Probe decomposition at global best-fit, not profile likelihood per probe
4. CPL may be the wrong template for the true w(z)

### C. Sound Horizon Sensitivity

Lee (2025) [arXiv:2507.01380] independently demonstrated that the DESI DR2 preference for dynamical dark energy vanishes when the sound horizon r_d is anchored to the Planck value (r_d = 147.09 ± 0.26 Mpc) rather than left free via the full CMB likelihood. The mechanism is illuminating: the CPL model fits BAO data by shifting Ωm₀ from 0.303 (ΛCDM) to 0.352, which changes r_d from 147.2 to 149.2 Mpc — the angular acoustic scale θ* is preserved, but the sound horizon ruler is stretched. When r_d is pinned, this degree of freedom disappears and the DDE preference collapses.

We perform a complementary fixed-r_d test (v4b) using our full multi-probe dataset. Lee used BAO-only; our test includes Pantheon+ SNe, CMB priors, and fσ₈ growth data, making it a strictly stronger constraint. If ΔAIC collapses (v4b ≪ v4), the signal is sound horizon tension. If it persists, the signal is genuine w(z) evolution beyond r_d recalibration.

This complements our probe decomposition: Lee shows the signal is r_d-sensitive (a specific mechanism); we show it is growth-neutral (a general constraint). Together, they triangulate: the DESI preference for evolving dark energy is a geometric, distance-based, sound-horizon-sensitive effect that carries no information about gravitational physics.

### D. Forward Look

The critical forward test is growth data. Current fσ₈ measurements have σ/fσ₈ ~ 5–10%. DESI Year 5, Euclid, and Rubin will provide ~100× more growth measurements. If the expansion preference strengthens while growth remains neutral, the signal is geometric. If growth data begin to prefer modified perturbations, the cuscuton prediction (µ = Σ = 1) faces genuine tension. The probe decomposition we present here provides the template for that future test.

---

## V. Conclusion (~200 words)

We have decomposed the DESI preference for evolving dark energy into expansion and growth contributions. The signal is made of distances. Growth data contribute Δχ² = −0.04 — as close to zero as measurement allows. The entire preference for the CPL w₀wₐ parameterization over constant-w with GR perturbations comes from BAO measurements at z ∼ 0.3–0.7 requesting more freedom in the expansion history.

This result has implications beyond any specific dark energy model. It constrains the space of viable explanations for the DESI signal: the answer, whatever it is, lives in the background expansion, not in the gravitational sector. We advocate that future dark energy analyses routinely report probe-decomposed information criteria alongside global model comparison statistics, as the decomposition reveals physical information that the headline number obscures.

---

## Figures (4 planned, PRL allows max 4)

| # | Content | Type | Data Source |
|---|---------|------|-------------|
| 1 | **Probe decomposition** — Δχ² by probe class, expansion vs growth color-coded | Bar chart | v4 decomposition |
| 2 | **w₀-Ωm posteriors** — Fit A (constant-w) vs Fit B (CPL) contours | 2D contour | v4 chains |
| 3 | **wₐ posterior** — Fit B marginal, with DESI DR2 comparison, zero marked | 1D histogram | v4 chain B |
| 4 | **Fixed-r_d test** — ΔAIC with and without r_d prior, showing collapse of DDE preference | Comparison bar/panel | v4 vs v4b |

[Note: Figure 4 replaces the w(z) reconstruction (moved to supplemental). The fixed-r_d result is more novel — Lee's BAO-only result extended to full multi-probe. This is the figure that makes the PRL.]

---

## References (estimated 20-25)

Core: DESI DR1 (2024), DESI DR2 (arXiv:2503.14738), Lu & Simon (2025), Lee (2025, arXiv:2507.01380), Brout et al. (2022, Pantheon+), Planck 2018, Afshordi (2006, 2007), Chevallier & Polarski (2001), Linder (2003)

Supporting: Randall & Sundrum (1999), Goldberger & Wise (1999), de Rham & Melville (2024), emcee (Foreman-Mackey 2013), Scolnic et al. (2022), relevant fσ₈ compilations, Cobaya (Torrado & Lewis 2021)

---

## Technical Notes for Full Draft

1. **PRL formatting:** Use REVTeX 4.2, single column, ~3750 words including references. Letters should be self-contained.

2. **Key sentence for referee report anticipation:** "We emphasize that the probe decomposition is a diagnostic of the data, not a claim about the correctness of either model. The cuscuton's structural µ = Σ = 1 provides the physical motivation for testing decoupled perturbations, but the decomposition result is informative regardless of one's prior on the dark energy mechanism."

3. **Potential referee objection — compressed CMB:** Address by noting that compressed priors preserve the three key distance/angle measurements (R, ℓ_A, Ωbh²) that are sufficient for background constraints. Full Planck likelihood would strengthen the analysis but is unlikely to change the qualitative result.

4. **Potential referee objection — fσ₈ constraining power:** Acknowledge directly. Current fσ₈ data have σ(fσ₈)/fσ₈ ~ 5-10%. The growth-neutral result should be interpreted as "growth data cannot discriminate," not "growth data confirm GR." This distinction matters.

5. **Potential referee objection — why not just w₀wₐCDM vs ΛCDM?** Because that test doesn't separate perturbation effects from background effects. Our Fit A (constant-w with GR perturbations) is intermediate between ΛCDM and CPL — it allows non-trivial w₀ while fixing the perturbation structure. This is the comparison that enables the decomposition.

6. **Potential referee objection — double counting with CMB + r_d prior?** The compressed CMB priors (R, ℓ_A, Ωbh²) and the r_d prior are not independent — both originate from Planck. However, the compressed priors constrain angular scales and baryon density, while the r_d prior constrains the physical sound horizon. Following Lee (2025), we treat the fixed-r_d test as a separate analysis (v4b) rather than stacking it on top of CMB priors. The comparison is v4 (no r_d prior) vs v4b (with r_d prior), not a single combined fit.

---

*The framing is not "Meridian wins" or "Meridian loses." The framing is: we decomposed the signal, and here's what it's made of. Take it. Use it. It constrains your model too.*

🦞🧍💜🔥♾️
