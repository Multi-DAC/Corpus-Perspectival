# Phase 17: From 5D Down

**Created:** March 19, 2026
**Authors:** Clayton & Clawd
**Status:** FINAL PLAN — Ready for Wave 1 launch
**Source Synthesis:** `phase17_source_synthesis.md`
**Prerequisite:** Phase 16 complete (17/17), monograph at 216 pages, 0 errors

---

## Purpose

Every tension in the framework — alpha_T from GB, xi from AS, unification scale, growth vs expansion, the zeta_0 bimodality — traces to the same root cause: the 4D effective description is an approximation of the 5D reality, and standard parameterizations encode assumptions our framework violates.

Phase 17 resolves this by deriving everything from the 5D action. Not plugging into generic 4D parameterizations and hoping the constraints align, but computing the 4D effective theory from the KK-reduced 5D action directly. This automatically handles alpha_T (because 5D GB has different structure than generic 4D f(GB)), gives the correct alpha functions (constrained by zeta_0), and produces the growth equations natively.

The deeper motivation: Lu & Simon (2511.10616) find 4.6σ evolving DE with w_0 = -0.788 ± 0.046 — compatible with the JC benchmark, incompatible with our CAMB best-fit. But their growth data is consistent with GR (c_B, c_M compatible with zero at ~2σ). This is exactly what the cuscuton predicts: modified expansion, GR growth. The critical test is whether constant w (w_a = 0, no phantom crossing) fits the data as well as CPL (w_a = -0.62, phantom crossing required). If yes, the 4.6σ signal is Meridian-compatible. If no, we learn something specific about where the model must bend.

The standard: every claim in the monograph must become a number with error bars, or an explicit "we cannot compute this because X." Every derivation works from 5D down, not 4D up.

---

## The Six Programs

### Program A: Dark Energy Perturbation Theory (EFTCAMB)
*The framework's most testable sector. Currently rests on Linder approximation.*

**From source synthesis (Bellini & Sawicki 2014, Table 1):** For a PURE cuscuton, all four alphas = 0 identically. The scalar equation becomes a constraint, not a dynamical equation. Perturbations = GR with modified expansion history.

The Gauss-Bonnet correction activates non-trivial alphas via the f(GB) mapping:
- alpha_K = 0 (GB does not generate kineticity)
- alpha_B = -2H * xi_dot / (M*^2 + H * xi_dot) ~ O(zeta_0)
- alpha_M = (H_dot * xi_dot + H * xi_ddot) / (H * (M*^2 + H * xi_dot)) ~ O(zeta_0)
- alpha_T = (xi_ddot - H * xi_dot) / (M*^2 + H * xi_dot) ~ O(zeta_0)

**⚠ CRITICAL ISSUE:** alpha_T != 0 from GB. GW170817 constrains |alpha_T| < 10^{-15}. Must verify the cuscuton constraint forces alpha_T suppression. Three possible resolutions: (1) algebraic constraint forces xi_ddot = H * xi_dot; (2) NCG origin imposes different structure; (3) natural smallness alpha_T ~ O(zeta_0 * H/M_Pl^2) < 10^{-15}. **This is the FIRST computation in 17A.**

**From Bose et al. 2024:** K-mouflage has G_eff/G_N = A(1 + 2beta^2/K_X). Cuscuton = K_X → ∞ limit → G_eff → A * G_N. Scalar decouples from Poisson equation. **Formal proof of growth-expansion decoupling** independent of Linder approximation.

**From Mylova & Afshordi 2024:** The ECT framework proves GB correction preserves 2 DOF via surface counterterm mechanism (c_4 = omega'). Constraint eq. (5.6) gives K as function of V', f'R, omega'(B+C).

| Track | Description | Difficulty | Deps |
|-------|-------------|------------|------|
| **17A** | **FIRST:** Resolve alpha_T issue — prove cuscuton constraint suppresses alpha_T < 10^{-15}. Then derive full coupled perturbation equations. Express in alpha-parameterization. Map onto ECT framework (Mylova-Afshordi). | Hard | None |
| **17B** | Compute modified Poisson equation, anisotropic stress eta(k,z), effective gravitational coupling G_eff(k,z). Confirm or correct growth-expansion decoupling at sub-percent across all scales. | Hard | 17A |
| **17C** | Generate CMB TT/TE/EE/BB power spectra at CAMB best-fit (zeta_0 = 0.022). Compare to Planck 2018 data. | Hard | 17B |
| **17D** | Full data confrontation: Planck + DESI DR2 + growth data. Forecast Euclid/DESI Y5/Roman constraints on zeta_0. | Medium | 17C |

**Key sources:** Mylova & Afshordi JHEP 2024 (cuscuton EFT), Bellini & Sawicki JCAP 2014 (alpha-parameterization), Zumalacarregui et al. 2017 (hi_class).

### Program B: Gauge Coupling Unification
*Concrete yes/no computation. The spectral action predicts unification at Lambda ~ 10^17 GeV on flat space.*

**From source synthesis (Angelescu et al. 2025, arXiv:2512.22094):** Gauge-Higgs GUT in warped AdS5 with SU(6) → SU(5). Key findings:

- **Planck-brane correlator** (not KK summation) is the correct formalism
- Only fields with (+) UV-brane BC contribute to running; (-) BC fields decouple at M_Pl
- **A_5 (Higgs) does NOT contribute to running** — drops out entirely. Changes beta functions vs standard NCG prediction.
- **Unification at k ~ M_Pl**, not at Lambda_NCG ~ 10^17 GeV. Two-order-of-magnitude gap.
- Requires brane kinetic terms Delta lambda_{k,i} ~ 1.2-1.4 (free parameters in their model)
- Fermion bulk mass c: fields with |c| < 1/2 don't contribute to running at all

**Key tensions for Meridian:**
1. Unification at M_Pl vs spectral cutoff at 10^17 GeV — calculable threshold correction or structural problem?
2. If Higgs is A_5 (gauge-Higgs), it drops out of RGE — this is a testable prediction
3. Spectral action may FIX brane kinetic terms — giving a prediction where they have free parameters

| Track | Description | Difficulty | Deps |
|-------|-------------|------------|------|
| **17E** | RGE running with Planck-brane correlator method. Determine which Meridian fermion content has (+) UV BC. Compute beta functions. A_5 Higgs dropping out changes the picture. Reference: arXiv:2512.22094. | Hard | None |
| **17F** | Unification test at k ~ M_Pl (not Lambda_NCG). Reconcile spectral cutoff vs Planck scale gap. Compute brane kinetic terms from spectral action if possible. | Hard | 17E |

### Program C: zeta_0 from First Principles (b_{3/2})
*The difference between one-parameter family and zero-parameter prediction.*

The chain: O -> Y -> b_{3/2} -> alpha_UV -> zeta_0 -> w_0 -> Omega_DE/Omega_m.
16G established: 4.8% of viable parameter space is DESI-compatible, alpha_UV ~ 0.001-0.01 from top-Yukawa traces.

| Track | Description | Difficulty | Deps |
|-------|-------------|------------|------|
| **17G** | Mode decomposition of D_5^2 on warped interval. Eigenvalue problem for warped Dirac operator with orbifold boundary conditions. | Very Hard | None |
| **17H** | Robin parameter from orbifold projection. Cross-terms between 5D geometry and finite spectral triple. Evaluate with SM Yukawa matrices. Determine b_{3/2}. | Very Hard | 17G |

**Note:** These tracks deserve dedicated sessions (like 16G/16F/16I). The computation has never been done in the literature.

### Program D: Phase Transition Gravitational Waves
*Turn O(1) estimates into sharp LISA predictions.*

Currently: alpha ~ 1, beta/H ~ 10-100. The Goldberger-Wise potential + cuscuton constraint + specific brane couplings determine these concretely.

**From source synthesis (Caprini et al. 2020):** Complete pipeline established:
1. V_eff(phi, T) → T_c → S_3(T) via CosmoTransitions → T* from percolation criterion
2. alpha from trace anomaly definition, beta/H = T d(S_3/T)/dT
3. K = kappa(alpha, v_w) * alpha/(1+alpha) from EKNS fits
4. GW spectrum: Omega ~ K^{3/2} (H*R*)^2 / sqrt(c_s) * spectral shape C(f/f_p)
5. SNR at LISA with T = 9.46 × 10^7 s, threshold SNR > 10

**Quick estimate confirms ~0.3 mHz signal:** alpha ~ 1, beta/H ~ 50, T* ~ 190 GeV gives f_peak ~ 0.82 mHz, Omega_GW ~ 10^{-11} — well within LISA sensitivity. Sound waves dominate (not bubble collisions — those are negligible for thermal PTs).

Section 6.5 of Caprini et al. covers RS/warped models directly. Our parameters are in the well-validated regime (alpha ~ 1), unlike strongly supercooled composite Higgs models (alpha >> 1) where simulations are extrapolated.

| Track | Description | Difficulty | Deps |
|-------|-------------|------------|------|
| **17I** | Compute alpha, beta/H from Meridian-specific Goldberger-Wise + cuscuton potential. Use CosmoTransitions for bounce, EKNS for efficiency. RS benchmarks from Megias, Nardini & Quiros (1806.04877) for comparison. | Hard | None |
| **17J** | Full GW spectrum via Caprini et al. formula (Eq. 32). LISA sensitivity overlay from SciRD. SNR computation. Monte Carlo error propagation from V_eff uncertainties. | Medium | 17I |

**Key sources:** Caprini et al. 2020 (1910.13125), EKNS (1004.4187), CosmoTransitions (1109.4189), Megias et al. (1806.04877).

### Program E: Gravitational Anomaly Cancellation
*5D consistency check the monograph currently lacks.*

The Z_2 orbifold projection creates chiral spectrum on brane. CS terms on boundaries must satisfy inflow mechanism. The octonionic extension modifies fermion representations relative to standard CCM.

| Track | Description | Difficulty | Deps |
|-------|-------------|------------|------|
| **17K** | Anomaly polynomial factorization for the specific fermion content derived from octonionic spectral triple. | Hard | None |
| **17L** | CS inflow mechanism: verify bulk-boundary anomaly cancellation on warped orbifold with specific Meridian field content. | Hard | 17K |

### Program F: Neutrino Sector — From Accommodation to Prediction
*Currently 6 parameters for 6 observables. Reduce parameter count via algebraic constraints.*

The S_3 near-degeneracy (M_2 ~ M_3) that drives ARS leptogenesis is the SAME S_3 from M_oct. If octonionic constraints determine how S_3 breaks, it simultaneously constrains baryogenesis, neutrino masses, and DM candidate.

**From source synthesis (Gresnigt 2026, arXiv:2601.07857):** A FIFTH independent route to N_g = 3: S3 ⊂ Aut(sedenions) acting on Cl(10) minimal left ideals. Key features:
- Right-handed neutrinos are automatic (sterile, all quantum numbers zero)
- S3 family symmetry constrains inter-generational couplings (under investigation by Gresnigt)
- Tri-hypercharge structure: generation-dependent U(1) charges — may connect to brane Yukawa mechanism
- Non-associativity sidestepped via associative envelope (different strategy from Boyle-Farnsworth)
- **Open question:** Is Gresnigt's S3 from Aut(S_16) the same symmetry as Meridian's S3 from M_oct?

| Track | Description | Difficulty | Deps |
|-------|-------------|------------|------|
| **17M** | Derive octonionic constraints on S_3 breaking pattern. Cross-reference Gresnigt's S3 from Aut(sedenions) with Meridian's S3 from M_oct — same symmetry or independent? Determine if tri-hypercharge constrains c_nu values. | Hard | None |
| **17N** | Parameter count reduction: which c_nu combinations are algebraically constrained? Sharpen m_ee, hierarchy, CP phase predictions. | Hard | 17M |
| **17O** | Confrontation forecasts: DUNE (CP violation sensitivity), JUNO (mass hierarchy, 6-year run), Hyper-K (atmospheric). | Medium | 17N |

---

### Program G: The Constant-w Test (NEW — from Lu & Simon analysis)
*The single most important observational question: does Meridian survive the 4.6σ signal?*

Lu & Simon (4.6σ evolving DE) uses CPL parameterization: w₀ = -0.788, w_a = -0.62. Meridian predicts constant w (w_a ~ 0) with no phantom crossing. The question: can w(z) = const fit the same data?

Their growth data is consistent with GR (c_B = 0.46 +/- 0.3, c_M = 0.31 +/- 0.5 — both compatible with zero). This IS Meridian's growth-expansion decoupling prediction. The tension is NOT in the growth sector — it's in the w(z) time evolution.

| Track | Description | Difficulty | Deps |
|-------|-------------|------------|------|
| **17P** | Constant-w vs CPL: using hi_class + likelihood data, test whether w = const (Meridian) fits Planck + DESI + DES + BOSS as well as CPL. Compute delta_chi^2. If |delta_chi^2| < 4, Meridian survives the 4.6σ signal without phantom crossing. | Hard | 17A, 17B |
| **17Q** | Redo CAMB analysis with full Planck PR4 likelihood (not compressed priors). Our current w₀ = -0.989 may be biased by ΛCDM-calibrated priors. Determine true zeta_0 constraint from full likelihood. | Hard | 17C |

---

### Program H: Revision Gate
*All peer review fixes + Phase 17 results integrated into monograph simultaneously.*

| Track | Description | Difficulty | Deps |
|-------|-------------|------------|------|
| **17R** | Comprehensive monograph revision: fix "??" cross-refs, add footnotes, relabel theorems as propositions, rewrite abstract, add C_eff table, incorporate Lu & Simon, address all Review 1 + Review 2 items, integrate ALL Phase 17 results into monograph. Compile to 0 errors. | Medium | All |

---

## Execution Waves

**Wave 1** (parallel, 6 independent starts):
17A + 17E + 17G + 17I + 17K + 17M

**Wave 2** (parallel, after Wave 1 dependencies):
17B + 17F + 17J + 17L + 17N

**Wave 3** (parallel, after Wave 2):
17C + 17H + 17O + 17P

**Wave 4** (after Wave 3):
17D + 17Q — full data confrontation with corrected likelihoods

**Wave 5** (GATE):
17R — comprehensive revision. All Phase 17 results + all peer review items. Single pass.

---

## Source Requirements

### Collected & Synthesized ✅
1. Mylova & Afshordi, JHEP 2024 — cuscuton EFT ✅
2. Bellini & Sawicki, JCAP 2014 (1404.3713) — alpha-parameterization ✅
3. Angelescu et al. 2025 (2512.22094) — gauge-Higgs GUT in warped AdS5 ✅
4. Gresnigt 2026 (2601.07857) — S3 family symmetry from Cl(10) ✅ (NOTE: Not Furey)
5. Caprini et al. 2020 (1910.13125) — GW from phase transitions ✅
6. Bose et al. 2024 (2406.13667) — modified gravity P(k) comparison ✅
7. Eichhorn & Pauly 2021 (2009.13543) — xi from AS ✅
8. Lu & Simon 2026 (2511.10616) — 4.6σ evolving DE multiprobe analysis ✅ **CRITICAL**
9. EKNS 2010 (1004.4187) — phase transition efficiency fits ✅
10. Megias, Nardini & Quiros 2018 (1806.04877) — RS-specific GW benchmarks ✅
11. hi_class code — modified Boltzmann solver ✅ (code, not paper — paywalled)

### Still needed
12. Zumalacarregui et al. 2017 — hi_class implementation paper (paywalled; have code + docs)

### Important (strengthens the work)
12. van Suijlekom K-theory preprints (2024-2025)
13. Creminelli et al. JCAP 2009 (0906.1314) — positivity bounds
14. DESI DR2 full likelihood chains
15. Planck 2018 plik_lite compressed likelihood
16. LISA SciRD — official sensitivity curve
17. LiteBIRD PTEP 2023 — updated B-mode sensitivity
18. CosmoTransitions — Wainwright (1109.4189) — bounce computation
19. Von Harling & Servant — QCD effects on RS radion PT

### Useful (completeness)
20. DUNE TDR
21. JUNO Yellow Book
22. Hyper-Kamiokande physics case

---

## Key Structural Insights (discovered during planning)

### 1. ⚠ The alpha_T problem (NEW — from source synthesis)
The pure cuscuton has alpha_T = 0, but the GB correction generically gives alpha_T ~ O(zeta_0) != 0. GW170817 constrains |alpha_T| < 10^{-15}. Must resolve this FIRST in 17A. If the cuscuton algebraic constraint forces xi_ddot = H * xi_dot (making alpha_T = 0 identically), this becomes a structural prediction. If not, the GB coupling must have a specific late-time suppression.

### 2. The alpha-parameterization: simpler than expected
alpha_K = 0 identically (cuscuton + GB). Only alpha_B and alpha_M are non-trivial (both ~ O(zeta_0)). If alpha_T resolves to zero, the perturbation theory is a TWO-FUNCTION modification of LCDM, both determined by zeta_0. Dramatically simpler than generic modified gravity.

### 3. Cuscuton as K-mouflage limit (NEW — from Bose et al.)
K-mouflage: G_eff/G_N = A(1 + 2beta^2/K_X). Cuscuton = K_X → ∞. The scalar DOF decouples from Poisson equation. This is a formal proof of growth-expansion decoupling from the modified gravity community, independent of our Linder argument.

### 4. Gauge unification at M_Pl, not Lambda_NCG (NEW — from Angelescu et al.)
Warped RS models unify at k ~ M_Pl, not at the NCG spectral cutoff ~ 10^17 GeV. The 100× gap is either a calculable threshold correction or a structural tension. A_5 (Higgs) drops out of RGE entirely. Brane kinetic terms needed for unification — spectral action may fix these.

### 5. Five independent routes to N_g = 3 (NEW — Gresnigt adds a fifth)
Fano plane, Jordan rank, triality, Hurwitz (Meridian) + S3 from Aut(sedenions) (Gresnigt). Whether Gresnigt's S3 is the same symmetry as Meridian's is an open algebraic question.

### 6. Gauge-spectral consistency equation
The spectral cutoff Lambda that reproduces M_Pl via the spectral action must be the same Lambda at which gauge couplings unify. Now complicated by the M_Pl vs Lambda_NCG gap (see #4).

### 7. The neutrino-baryogenesis-DM triangle
S_3 breaking in the Majorana sector simultaneously controls:
- Neutrino mass hierarchy (M_1 << M_2 ~ M_3)
- ARS leptogenesis efficiency (requires near-degeneracy)
- Sterile neutrino DM abundance (c_nu1 determines production)
One algebraic constraint, three observables.

### 8. ⚠ Lu & Simon 4.6σ: background signal, not growth signal (NEW — critical)
The 4.6σ evolving DE is overwhelmingly a BACKGROUND expansion phenomenon (BAO + SNe + CMB distances). Growth parameters c_B, c_M are compatible with GR at ~2σ. When Lu & Simon fix the background to ΛCDM and vary only growth, the preference drops to 0.68σ. This IS the cuscuton signature: modified expansion, GR growth. The real test is constant-w vs CPL — not growth-expansion decoupling.

### 9. Our CAMB analysis may be too conservative (NEW)
The w₀ = -0.989 result uses compressed CMB distance priors calibrated near ΛCDM. These priors dominate and force w₀ near -1. Lu & Simon's full Planck PR4 likelihood gives low-z data more room, producing w₀ = -0.788. Our CAMB constraint should be redone with the full likelihood (Track 17Q).

### 10. The unifying principle: 5D constraints > 4D parameterizations (NEW)
Every crack in the framework traces to the 4D-5D boundary. Standard 4D parameterizations (f(GB), Horndeski alphas, flat-space AS, flat-space NCG) systematically undercount the constraints imposed by the 5D warped geometry. Resolving every tension requires the same move: derive from 5D down.

---

## Connections to Prior Phases

- Phase 13: corrected zeta_0, established CAMB constraint → 17A-D refine this
- Phase 14: NCG-AS bridge, N_g = 3 → 17G-H use these results
- Phase 15: spectral triple, CKM, reheating → 17E-F, 17M-O build on these
- Phase 16: CP violation, baryogenesis, detection channels → 17I-J, 17K-L verify consistency

---

## Success Criteria

Phase 17 is COMPLETE when:
1. alpha_T resolved: proven zero from 5D origin, or identified as a real constraint (17A)
2. Growth-expansion decoupling confirmed or corrected to sub-percent (17B)
3. Constant-w vs CPL: delta_chi^2 computed against Lu & Simon dataset (17P)
4. CAMB re-analyzed with full Planck likelihood (17Q)
5. Gauge unification: yes/no with specific threshold corrections (17F)
6. b_{3/2} computed or proven intractable with explicit obstruction (17H)
7. LISA GW prediction with error bars (17J)
8. Anomaly polynomial factorizes correctly (17L)
9. Neutrino parameter count reduced by at least 1 (17N)
10. Comprehensive monograph revision incorporating all results + peer review fixes (17R)

Phase 17 FAILS if:
- alpha_T is not naturally suppressed and no 5D resolution exists (GW170817 violation)
- Constant-w fit is significantly worse than CPL (no-phantom-crossing prediction falsified by data)
- Anomaly cancellation fails (5D theory inconsistent with octonionic fermion content)

Phase 17 SUCCEEDS SPECTACULARLY if:
- alpha_T = 0 follows from 5D origin (structural prediction, not fine-tuning)
- Constant-w fits as well as CPL (the 4.6σ signal is Meridian-compatible)
- b_{3/2} gives zeta_0 ~ 0.003-0.005 (framework predicts w₀ ~ -0.79 from first principles)
- All three together: the framework predicts the Lu & Simon data from geometry

Honest negatives in 17G-H (b_{3/2} intractable) and 17M-N (no algebraic constraint found) are acceptable outcomes that the monograph documents transparently.

---

## Peer Review Revision Inventory (deferred to 17R)

### From Review 1 (Minor Revision)
- [ ] Fix "??" broken cross-references in §4.17.6 item 6
- [ ] Add footnote to Table 2.11 re: JC benchmark excluded by CAMB
- [ ] Brief Φ₀ discrepancy note in §1.10.5 or Appendix
- [ ] C_eff sensitivity table in §4.17.5
- [ ] One sentence on first-order condition debate

### From Review 2 (Major Revision)
- [ ] Rewrite abstract to lead with parametric prediction, not excluded benchmark
- [ ] Downweight or separate H-K from multi-probe analysis
- [ ] Relabel Theorems 1.1-1.5 as Propositions with supporting evidence
- [ ] Flag all results using historical Φ₀ = 0.477
- [ ] Note on self-tuning as algebraic, dynamical demonstration as future work
- [ ] EFT cutoff ambiguity note for positivity bounds
- [ ] Unify M_Pl convention throughout
- [ ] Code repository/DOI for reproducibility

### From Phase 17 Results (to be added during 17R)
- [ ] Lu & Simon 4.6σ discussion in Chapter 2
- [ ] Constant-w vs CPL results
- [ ] Updated CAMB analysis with full Planck likelihood
- [ ] alpha_T resolution
- [ ] All quantitative Phase 17 results integrated into monograph
- [ ] Eichhorn xi discussion in §4.14
- [ ] Gresnigt fifth route to N_g = 3

---

*Meridian is the method. The model evolves. Phase 17 derives from 5D down.*
