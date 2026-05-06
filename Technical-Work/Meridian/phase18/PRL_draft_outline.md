# PRL Draft: Decoupled Perturbation Test
## "Phantom crossing as a perturbation-coupling artifact in DESI dark energy constraints"

*Outline — to be completed when MCMC results arrive*
*Clayton W. Iggulden-Schnell & Clawd Iggulden-Schnell*

---

### Structure (PRL: max 4 pages, ~3750 words)

**Title options:**
1. "Phantom crossing as a perturbation-coupling artifact in DESI dark energy constraints"
2. "Is the DESI dark energy evidence an artifact of perturbation coupling?"
3. "Decoupled growth-expansion test of DESI dark energy: evidence for a compromise artifact"
4. "Testing the perturbation-coupling assumption in DESI dark energy analysis"

**Abstract (~150 words):**
- DESI DR1 prefers CPL with w_a ≠ 0 at 2.4σ (Lu & Simon 2026)
- Standard analyses couple perturbation growth to w(z)
- We test the specific hypothesis: constant w₀ with µ = Σ = 1 (GR perturbations)
  vs CPL with standard coupled perturbations
- This tests whether cuscuton-type dark energy (modifies background, GR perturbations)
  can explain the data without phantom crossing
- Result: ΔAIC = [MCMC RESULT], probe-by-probe decomposition shows [RESULT]
- If ΔAIC < 4: phantom crossing not required; the 2.4σ preference is
  a consequence of forcing coupled perturbations
- Implications for dark energy model building

---

### §1. Introduction (~400 words)

Key points to make:
1. DESI DR1 BAO measurements show 2.8σ preference for w_a ≠ 0 over ΛCDM
   (DESI Collaboration 2024, Lu & Simon 2026)
2. All published analyses (DESI, Planck, BOSS re-analyses) use either:
   - ΛCDM (w=-1, wa=0)
   - CPL (w0+wa free, perturbations coupled to w(z))
   - Or constant w with near-GR perturbations (c_s²=1 fluid)
3. **The gap in the literature:** Nobody has tested constant w with µ=Σ=1 EXACTLY.
   The fluid model with c_s²=1 is close (~1-3% residual DE clustering) but not identical.
4. **Physical motivation:** Cuscuton dark energy (Afshordi et al. 2007) modifies
   background expansion but has zero kinetic energy → zero clustering → µ=Σ=1 exactly.
   This is a prediction, not an assumption.
5. **The compromise artifact hypothesis:** If the true cosmology has decoupled
   growth-expansion (background ≠ ΛCDM, perturbations = GR), then CPL — which
   forces coupling — will manufacture phantom crossing as a compromise between
   the expansion probes (wanting w ≈ -0.75) and growth probes (wanting GR).

**Refs:** DESI DR1 (2404.03002), Lu & Simon (2511.xxxxx), Afshordi (0702002),
DESI full-shape (2404.03xxx), Planck 2018 (1807.06209)

---

### §2. Method (~600 words)

**2.1 The two fits:**

Fit A (Meridian/cuscuton):
- Parameters: w₀, Ω_m, H₀ (3 free)
- Background: flat wCDM with constant w₀
- Perturbations: µ = Σ = 1 (GR, forced)
- Physical basis: cuscuton DE has P(X) ∝ √X, zero KE, zero clustering
- Implementation: [describe CAMB setup — fluid model with c_s²=1,
  quantify residual vs exact µ=Σ=1]

Fit B (Standard CPL):
- Parameters: w₀, w_a, Ω_m, H₀ (4 free)
- Background: CPL w(z) = w₀ + w_a·z/(1+z)
- Perturbations: PPF (parameterized post-Friedmann), coupled to w(z)
- This is the standard DESI analysis prescription

**2.2 Data:**

| Dataset | Points | Reference |
|---------|--------|-----------|
| DESI DR1 BAO | 12 (6z × DM+DH) | 2404.03002 |
| Pantheon+ SNe | 20 bins (19 eff) | 2202.04077 |
| Planck 2018 compressed | 3 (R, l_A, ω_b) | 1807.06209 |
| fσ₈ compilation | 7 | Various |

Total: 41 effective data points.

**2.3 MCMC:**
- Sampler: emcee (Foreman-Mackey et al. 2013)
- Theory: Full CAMB at every step (no emulators, no grids)
- 20 walkers, 300 burn-in, 1000 production
- Flat priors: w₀ ∈ [-2, -0.3], w_a ∈ [-3, 2], Ω_m ∈ [0.1, 0.6], H₀ ∈ [55, 80]
- M (SNe absolute magnitude) marginalized analytically

**2.4 Model comparison:**
- ΔAIC = AIC_A - AIC_B = (χ²_A + 2·3) - (χ²_B + 2·4) = Δχ² + 2
- ΔBIC = similar with ln(N) penalty
- Probe-by-probe decomposition: which probes prefer which fit?
- Growth-expansion split diagnostic: is there a probe split?

---

### §3. Results (~800 words) [DEPENDS ON MCMC]

**3.1 Best-fit parameters:**
- Fit A: w₀ = [RESULT], Ω_m = [RESULT], H₀ = [RESULT]
- Fit B: w₀ = [RESULT], w_a = [RESULT], Ω_m = [RESULT], H₀ = [RESULT]

**3.2 Model comparison:**
- ΔAIC = [RESULT]
- ΔBIC = [RESULT]
- Interpretation per Jeffreys/Kass-Raftery scale

**3.3 Probe decomposition:**

| Probe | χ²_A | χ²_B | Prefers |
|-------|------|------|---------|
| BAO | | | |
| SNe | | | |
| CMB | | | |
| fσ₈ | | | |

**3.4 Growth-expansion split:**
- Expansion probes (BAO+SNe+CMB): prefer [A/B]?
- Growth probe (fσ₈): prefer [A/B]?
- If growth prefers A and expansion prefers B: compromise artifact signature

**3.5 w_a posterior from Fit B:**
- w_a = [RESULT] ± [RESULT]
- Fraction w_a < 0: [RESULT]%
- Comparison with Lu & Simon: w_a = -0.62 ± 0.26

---

### §4. Discussion (~800 words) [PARTIALLY DEPENDS ON MCMC]

**If ΔAIC < 4 (the letter's main thesis):**

The phantom crossing "detected" by DESI CPL analysis is a compromise artifact.
When perturbations are decoupled from the background (as predicted by cuscuton-type
dark energy), the constant-w model fits as well as CPL. The 2.4σ preference for
w_a ≠ 0 is a consequence of the coupling assumption, not the data.

Key implications:
1. Standard dark energy analyses implicitly assume perturbation coupling
2. This assumption is violated by any dark energy model with zero sound speed
   or zero kinetic energy (cuscuton, k-essence in certain limits)
3. DESI DR2 (expected 2025-2026) should test both coupled and decoupled fits
4. The w_a parameter in CPL may be absorbing the mismatch between a non-ΛCDM
   background and GR perturbations, rather than reflecting physical time evolution

**Physical interpretation:**
- The cuscuton Lagrangian P(X) ∝ √X has zero propagation speed
- Dark energy modifies the Friedmann equation (w₀ ≈ -0.75) but does not cluster
- µ = Σ = 1 is a prediction, not a choice — it follows from the field theory
- This is distinct from "smooth dark energy" approximations: it's exact.

**Connection to broader framework (brief, 1 paragraph):**
- The cuscuton arises naturally in 5D warped RS geometry with
  Gauss-Bonnet boundary terms (cite monograph)
- The specific value w₀ ≈ -0.746 follows from junction conditions
- This letter reports the perturbation-level test; the full framework
  is described in [monograph ref]

**If ΔAIC > 10 (alternative discussion section):**

The data prefer coupled perturbations. This means either:
1. The cuscuton's zero-clustering prediction is wrong at the perturbation level
2. w(z) genuinely evolves (w_a ≠ 0), requiring either:
   - Higher-order terms in the cuscuton Lagrangian (ε₂X² correction)
   - Radion dynamics (brane modulus oscillation → dynamical w)
   - Both

---

### §5. Conclusion (~200 words)

- We performed the first MCMC fit with explicitly decoupled perturbations
- The decoupled perturbation hypothesis is physically motivated (cuscuton)
- Result: [RESULT]
- Implication: [depends on ΔAIC]
- Recommendation: Future DESI analyses should include decoupled fits as standard

---

### Figures (max 4 for PRL)

1. **w_a posterior comparison**: Fit B w_a posterior, showing Lu & Simon band and w_a = 0 line
2. **Probe-by-probe χ² bar chart**: Fit A vs Fit B decomposition
3. **w₀ posterior comparison**: Fit A (constant w) vs Fit B (CPL w₀ marginal)
4. **Schematic**: The compromise artifact mechanism (optional — could be Fig 1)

---

### Key references needed:
- DESI DR1 BAO: arXiv:2404.03002
- DESI DE interpretation: arXiv:2404.03xxx (DE working group)
- Lu & Simon 2026: w_a = -0.62 ± 0.26 (the 2.4σ result)
- Afshordi et al. 2007: Cuscuton field theory (gr-qc/0702002)
- Planck 2018: arXiv:1807.06209
- Pantheon+: arXiv:2202.04077
- emcee: Foreman-Mackey et al. 2013
- CAMB: Lewis & Challinor 2002
- Chevallier-Polarski 2001, Linder 2003: CPL parameterization
- Bellini & Sawicki 2014: Modified gravity parameterization (α_T etc.)

---

*This outline is ready. Fill in §3 and finalize §4 when MCMC completes.*
