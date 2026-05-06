# Phase 18: The Perturbation Test
## Project Meridian — Phase 18 Architecture

**Authors:** Clayton W. Iggulden-Schnell & Clawd
**Date:** March 19, 2026
**Status:** ACTIVE (17R gate passed, monograph in external review)

---

## Motivation

Phase 17 ("From 5D Down") established that Meridian produces a constant-w dark energy model with GR perturbations — all four Bellini-Sawicki alpha functions vanish exactly from the 5D origin. The framework's cleanest prediction is w_a = 0 identically.

The data disagree at 2.4σ (Lu & Simon 2026). DESI DR2 + Planck + DES Y5 combined prefer CPL with w_a = -0.62 ± 0.26, w_0 = -0.788 ± 0.046.

**But:** Every published CPL analysis assumes coupled perturbations — growth and expansion are linked through w(z). Meridian's cuscuton DECOUPLES them. The "4.6σ evolving dark energy" signal may be a **compromise artifact**: CPL manufacturing phantom crossing to reconcile expansion-deviates-from-ΛCDM with growth-says-GR.

Phase 18 answers the question: **Is the phantom crossing real physics, or a parameterization artifact?**

---

## Software Stack (Verified March 19, 2026)

| Package | Version | Role |
|---------|---------|------|
| CAMB | 1.6.6 | Boltzmann solver (background + perturbations) |
| Cobaya | 3.6.1 | MCMC framework (Planck/BAO likelihoods) |
| emcee | 3.1.6 | Backup MCMC sampler |
| GetDist | 1.7.6 | Posterior analysis + triangle plots |
| astropy | 7.2.0 | Distance calculations |
| h5py | 3.16.0 | HDF5 data handling |
| SciPy | 1.17.0 | Optimization, integration |
| NumPy | 2.4.2 | Array operations |
| Matplotlib | 3.10.8 | Plotting |

**Key capability:** CAMB natively supports `dark_energy_model='fluid'` with constant w and GR perturbations (μ = Σ = 1). This IS the Meridian template. No custom modifications needed.

---

## Architecture

### Program A: Mock-Data Validation (18I) — NEW

| Track | Description | Priority | Dependencies |
|-------|-------------|----------|-------------|
| **18I** | Mock-data validation of method | **CRITICAL** | None |

**Why:** Before applying the decoupled perturbation test to real data, we must validate the method itself. Generate synthetic data from a KNOWN constant-w + GR-perturbation universe, analyze with CPL + coupled perturbations, and verify that phantom crossing appears as a compromise artifact.

**Method:**
1. Use CAMB to generate mock BAO, SNe, fσ₈ data at Meridian's w₀ = -0.746 with GR perturbations
2. Add realistic noise (DESI-level uncertainties)
3. Fit with CPL + coupled perturbations
4. Check: does the fit prefer w_a ≠ 0? Does it manufacture phantom crossing?
5. Repeat with 100+ realizations for statistical significance

**Success:** CPL analysis of Meridian-truth mock data produces w_a < 0 in >50% of realizations. Confirms the compromise artifact mechanism.
**Failure:** CPL recovers w_a ≈ 0 from Meridian-truth data. The artifact hypothesis doesn't hold.

### Program B: The Critical Test (18A)

| Track | Description | Priority | Dependencies |
|-------|-------------|----------|-------------|
| **18A** | Decoupled perturbation test on real data | **CRITICAL** | 18I (method validated) |

**The Test:**
- **Fit A (Meridian template):** Constant w₀, μ = Σ = 1 (GR perturbations). One DE parameter. CAMB with `dark_energy_model='fluid'`, standard ΛCDM perturbation equations.
- **Fit B (Standard template):** CPL w₀ + w_a, perturbations coupled to w(z). Two DE parameters. CAMB with `dark_energy_model='ppf'` or equivalent.
- **Data:** DESI DR2 BAO + DES Y5 SNe + Planck 2018 compressed CMB + fσ₈ compilation (BOSS, eBOSS, 6dF, DESI).
- **Method:** Cobaya MCMC with proper likelihoods. Compressed Planck (Gaussian distance priors) to avoid clik installation.
- **Key diagnostic:** Split χ² by probe type. Does growth data prefer Fit A? Does expansion data prefer Fit B? If so, the phantom crossing is a compromise.

**Data sources (public):**
- Planck 2018: compressed likelihoods built into Cobaya (`planck_2018_lowl.TT`, distance priors)
- DESI DR2 BAO: public data release (if available; otherwise DESI DR1 from arXiv:2404.03002)
- DES Y5 SNe: DES public release (if available; otherwise Pantheon+ from arXiv:2202.04077)
- fσ₈: compilation from BOSS DR12 + eBOSS + 6dFGS (public)

**Success criterion:** ΔAIC(Fit A vs Fit B) < 2, OR growth-expansion split shows Fit A preferred by growth while Fit B preferred by expansion.
**Failure criterion:** ΔAIC > 10 with growth data also preferring Fit B.

### Program C: Escape Hatches (18B)

| Track | Description | Priority | Dependencies |
|-------|-------------|----------|-------------|
| **18B** | Higher-order cuscuton: ε₂X² | Critical | 18A |

**Why:** If 18A shows constant-w genuinely fails, the next question is whether the cuscuton mechanism can produce small w_a through higher-order kinetic terms. The full kinetic function is P(X) = μ²√(2X) + ε₁X + ε₂X² + ... The ε₂ term produces time variation of w. Is it large enough to match data?

**Method:** Derive ε₂ from the 5D spectral action (next-order heat kernel coefficient). Compute w_a(ε₂). Compare with Lu & Simon w_a = -0.62.

**Success:** ε₂ naturally gives |w_a| ~ 0.1–1. Framework produces time-varying w from first principles.
**Failure:** ε₂ is too small (|w_a| ≪ 0.01) or wrong sign. Higher-order terms don't help.

### Program D: UV Completion (18C, 18D)

| Track | Description | Priority | Dependencies |
|-------|-------------|----------|-------------|
| **18C** | NCG-AS basin of attraction | Critical | None |
| **18D** | AS beta functions on warped RS | Important | 18C |

**18C:** The key open question from Phase 14: does the Reuter fixed point's basin of attraction include the NCG spectral action's initial conditions? If yes, the NCG → AS → IR chain is complete. If no, the UV completion needs modification.

**Method:** Compute the RG flow from NCG initial conditions (a₁ = a₂ = a₃ = 12, λ/g² from spectral action) using the Reuter fixed point structure. Determine if the flow reaches the observed IR values.

**18D:** Extend the AS beta functions to a warped RS background. The dimensional crossover (4D below k_cross, 5D above) from Phase 13M needs to be incorporated into the RG flow. This determines whether the gauge unification tension (spread 10.81 from 17E) can be resolved by gravitational corrections.

### Program E: Flavor Completion (18E)

| Track | Description | Priority | Dependencies |
|-------|-------------|----------|-------------|
| **18E** | Y₅ from orbifold boundary conditions | Important | None |

**Why:** 17N showed that 4 neutrino predictions follow IF Y₅ (the 5D Yukawa coupling) has geometric origin from orbifold boundary conditions rather than being a free matrix. 17M showed the democratic M_oct has 6→6 parameter count. The question is whether the orbifold boundary conditions on the warped RS background constrain Y₅ enough to close the gap.

**Method:** Derive the boundary conditions for fermion zero modes on S¹/Z₂ with warped metric. The profiles f(y, cᵢ) depend on bulk mass parameters cᵢ. If the boundary conditions fix the cᵢ ratios (not just individual values), Y₅ becomes geometric.

### Program F: Radion Dynamics (18F)

| Track | Description | Priority | Dependencies |
|-------|-------------|----------|-------------|
| **18F** | Goldberger-Wise bounce with cuscuton | Important | None |

**Why:** The Goldberger-Wise mechanism stabilizes the radion. But the cuscuton constraint (K_X = 0) modifies the effective potential. If the stabilized radion has residual time dependence, this produces an effective w_a from radion dynamics — a mechanism for apparent DE evolution from a constant underlying equation of state.

**Method:** Solve the coupled GW-cuscuton system. Check if the stabilized configuration has exactly w_a = 0 or if residual oscillations produce detectable w_a.

### Program G: Spectral Completion (18G)

| Track | Description | Priority | Dependencies |
|-------|-------------|----------|-------------|
| **18G** | Full b₃/₂ with gauge + scalar | Useful | None |

**Why:** 17G computed b₃/₂ from the fermion sector only. The full boundary heat kernel includes gauge and scalar contributions. These modify α_UV at next order. While 17H showed w₀ is insensitive to C_eff, the gauge/scalar sectors might affect other predictions (e.g., the inflaton potential).

### Program H: Infrastructure (18H) — PROMOTED TO WAVE 2

| Track | Description | Priority | Dependencies |
|-------|-------------|----------|-------------|
| **18H** | Code repository + DOI | **Important** | None |

Collect all Phase 13–17 computational scripts into a reproducible repository. Assign DOI via Zenodo. External reviewer specifically requested this. Having the code available during review strengthens credibility.

**Contents:** All Python scripts from phases 13–17, organized by phase. README with dependency list. Requirements.txt. Example run instructions. Link from monograph.

---

## Execution Plan

**Wave 1 (CRITICAL — validate the method):** 18I (mock-data validation)
- Generate Meridian-truth synthetic data, analyze with CPL. Confirm the compromise artifact mechanism before touching real data.

**Wave 2 (CRITICAL + INFRASTRUCTURE — the real test + parallel work):**
- **18A** (decoupled perturbation test on real data) — gates on 18I success
- **18H** (code repository + DOI) — parallel, independent
- **18C** (NCG-AS basin) — parallel, independent

Decision point after 18A:
- If 18A PASS: framework survives. Proceed to Wave 3 (UV completion, flavor, spectral).
- If 18A FAIL: framework under pressure. Proceed immediately to 18B (escape) + 18F (radion).

**Wave 3 (depends on 18A outcome):**
- **18A PASS path:** 18D + 18E + 18G (parallel). AS on warped RS, flavor completion, full b₃/₂.
- **18A FAIL path:** 18B + 18F (parallel). Higher-order cuscuton, radion dynamics.

**Wave 4 (completion):** Remaining tracks from whichever path Wave 3 didn't take.

---

## Success/Failure Criteria

**Phase 18 SUCCESS:** Mock validation (18I) confirms the compromise artifact mechanism. Real-data test (18A) demonstrates constant-w + GR perturbations fits multi-probe data comparably to CPL. The phantom crossing is identified as a parameterization artifact. The framework's w_a = 0 prediction survives.

**Phase 18 PARTIAL:** 18A shows moderate preference for CPL (Δχ² ~ 4–9), but 18B demonstrates that ε₂X² naturally produces the observed w_a, preserving the framework with a minor extension.

**Phase 18 FAILURE:** 18A shows strong preference for CPL (Δχ² > 9), AND 18B shows ε₂ cannot produce the observed w_a. The constant-w prediction is dead. The cuscuton mechanism needs fundamental revision.

---

## Timeline

| Track | Description | Estimated Effort | Wave |
|-------|-------------|-----------------|------|
| 18I | Mock-data validation | 1 session | 1 |
| 18A | Decoupled perturbation test | 1 dedicated session | 2 |
| 18H | Code repository + DOI | 1 session | 2 |
| 18C | NCG-AS basin of attraction | 1–2 sessions | 2 |
| 18B | Higher-order cuscuton | 1 session | 3 (if needed) |
| 18D | AS on warped RS | 1–2 sessions | 3 |
| 18E | Y₅ from orbifold BCs | 1 session | 3 |
| 18F | Radion dynamics | 1–2 sessions | 3 (if needed) |
| 18G | Full b₃/₂ | 1 session | 4 |

---

*Phase 18 is defined by a single question: is the phantom crossing real? Everything else follows from the answer. The framework has put itself in the position where this question is answerable, specific, and decisive. That is the hallmark of a falsifiable theory.*

*If the decoupled perturbation test passes, Meridian has explained the DESI anomaly from first principles — the only framework in the literature that does so. If it fails, the framework told us exactly how it would fail, and we learn something real about the universe.*

*Either way, the answer matters.*
