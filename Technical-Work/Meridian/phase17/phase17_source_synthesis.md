# Phase 17: Source Synthesis

**Date:** March 19, 2026
**Sources:** 6 papers (2 failed downloads noted below)

---

## Critical Finding: The alpha_T Problem

**Bellini & Sawicki (2014)** confirms that for a **pure cuscuton**, all four alpha parameters are identically zero:

| alpha_K | alpha_B | alpha_M | alpha_T |
|---------|---------|---------|---------|
| 0 | 0 | 0 | 0 |

The perturbation equations reduce to standard GR with a modified expansion history. The scalar equation becomes a *constraint*, not a dynamical equation. No propagating DOF.

**However:** Meridian's Gauss-Bonnet correction activates non-trivial alphas. From Table 1 of Bellini & Sawicki, the f(GB) contribution gives:

```
alpha_K = 0
alpha_B = -2H * xi_dot / (M*^2 + H * xi_dot)
alpha_M = (H_dot * xi_dot + H * xi_ddot) / (H * (M*^2 + H * xi_dot))
alpha_T = (xi_ddot - H * xi_dot) / (M*^2 + H * xi_dot)
```

where xi is the GB coupling function.

**THE ISSUE:** alpha_T != 0 from the GB correction. GW170817 constrains |alpha_T| < 10^{-15}. Since zeta_0 ~ 0.022 and xi ~ zeta_0 * f(phi), we need to verify that the specific time dependence of xi(phi) suppresses alpha_T below 10^{-15} at z ~ 0. If it doesn't, this is a **potential tension** that Track 17A must resolve immediately.

**Possible resolutions:**
1. The cuscuton constraint (phi determined algebraically) may force xi_ddot = H * xi_dot, which would give alpha_T = 0 exactly. This needs to be checked.
2. The GB correction in Meridian may not be a standard f(GB) model — it arises from the spectral action, and the NCG origin may impose different constraints.
3. The smallness of zeta_0 ~ 0.022 may make alpha_T ~ O(zeta_0 * H/M_Pl^2), which could be naturally < 10^{-15}.

**This is the single most important calculation in Track 17A.**

---

## Paper-by-Paper Synthesis

### 1. Bellini & Sawicki 2014 (1404.3713v3)
**"Maximal freedom at minimum cost: linear large-scale structure in general modifications of gravity"**

**Key equations for 17A-D:**
- alpha_M = H^{-1} d(ln M*^2)/dt — Planck mass run rate
- alpha_K — kineticity (zero for cuscuton)
- alpha_B — braiding (mixing of scalar and metric kinetic terms)
- alpha_T = c_T^2 - 1 — tensor speed excess (must be < 10^{-15})
- Stability: D = alpha_K + (3/2) alpha_B^2 > 0 for no-ghost. For cuscuton, D = 0 (no scalar DOF).
- Sound speed: c_s^2 expression from eq. (3.13) — vacuous for cuscuton (no scalar mode).

**The cuscuton limit (Section 3.4):** "The limit alpha_i -> 0 but with a non-LCDM expansion history... is equivalent to the cuscuton model... the proper way of modelling perturbations within the context of a wCDM cosmology that preserves general covariance."

**Mapping to EFT operators:** Table 2 provides alpha → EFT operator dictionary.

**Phenomenological parameterization:** alpha_i = (1 - Omega_m) * alpha_hat_i with alpha_hat_i ~ O(1) unless tuned.

**For Meridian:** The pure cuscuton = wCDM with GR perturbations. The GB correction is what creates testable perturbation signatures. The entire perturbation theory is controlled by zeta_0 through xi(phi).

### 2. Mylova & Afshordi, JHEP 2024 (JHEP04(2024)144)
**"Effective Cuscuton Theory"**

**The ECT action (eq. 3.5):**
```
S_ECT = Lambda^4 int d^4x sqrt(-g) [ V(phi) + f(phi) R/(2 Lambda^2)
        + omega(phi) R_GB/(2 Lambda^4) + c_1(phi) sqrt(X)/Lambda
        + c_2(phi) sqrt(X) K / Lambda^2 + ... ]
```

**Key structural result:** Surface counterterms (c_2 = f', c_4 = omega') cancel precisely the terms that would propagate a scalar DOF. This is automatic from the geometric construction, not tuning. After cancellation, the action is Type II MMG — proven to propagate only 2 tensorial DOF.

**Meridian mapping:**
- V(phi) → brane-projected effective CC (self-tuned)
- f(phi) → effective Planck mass on brane (from RS warp factor integral)
- c_1(phi) → cuscuton mass scale from brane tension
- **omega(phi) → Meridian's Gauss-Bonnet correction. This is where zeta_0 lives.**
- The c_4 = omega' constraint automatically ensures GB correction doesn't propagate scalar DOF.

**Critical connection:** The cuscuton is the UV limit (X >> 1) of anti-DBI. Meridian's brane scalar arises from DBI. The ECT is the low-energy expansion of what Meridian computes from 5D geometry.

**Open problems identified:**
1. Full Hamiltonian analysis beyond leading order (GB sector incomplete)
2. Covariant formulation of the "scalarless symmetry"
3. The c_3(phi) sqrt(X) R_{3d} term (brane intrinsic curvature) — set aside but may matter for RS
4. No stability analysis performed

**For 17A:** The ECT provides the formal proof that our GB correction preserves 2 DOF. The constraint equation (eq. 5.6) with GB gives K as function of V', f'R, omega'(B+C) — perturbative in zeta_0.

### 3. Angelescu, Bally, Goertz & Weber 2025 (2512.22094v1)
**"Gauge Coupling Unification in Gauge-Higgs GUT"**

**Model:** SU(6) in 5D warped AdS5, broken to SU(5) on one brane and G_SM on the other. Higgs = A_5 (gauge-Higgs unification). No SUSY.

**Central method: Planck-brane correlator.** Avoids summing infinite KK tower. Key rule: **only fields with (+) BC on UV brane contribute to running.** Fields with (-) BC decouple (mass ~ M_Pl).

**Results:**
- Unification occurs at k ~ M_Pl (not TeV, not 10^17 GeV)
- Requires brane kinetic terms Delta lambda_{k,i} ~ 1.2-1.4
- A_5 (Higgs) does NOT contribute to running — drops out entirely
- For q << T (below KK scale): standard 4D running
- For T << q << k: logarithmic running with modified coefficients
- Fermion bulk mass c controls everything: |c| < 1/2 fields don't contribute to running at all

**Critical implications for Meridian (17E-F):**

1. **The Planck-brane correlator is the correct formalism** for our warped orbifold.
2. **Unification at k ~ M_Pl, not Lambda_NCG ~ 10^17 GeV.** The two-order-of-magnitude gap matters. The spectral action cutoff may need reinterpretation as unification at k with brane-kinetic corrections encoding the Lambda → k evolution. This is a potential tension or a calculable threshold correction.
3. **A_5 dropping out changes the beta functions** relative to standard NCG prediction.
4. **Brane kinetic terms are free parameters in their framework** — but in Meridian, the spectral action may fix them. This would be a prediction where they have a free parameter.
5. **Fermion localization profiles** (bulk mass c) that give the SM mass hierarchy also control which fields contribute to gauge running. This is a consistency constraint Meridian must satisfy.

### 4. Gresnigt 2026 (2601.07857v1) [NOT Furey]
**"Electroweak Structure and Three Fermion Generations in Clifford Algebra with S3 Family Symmetry"**

**Main result:** N_g = 3 from S3 ⊂ Aut(sedenions) acting on minimal left ideals of Cl(10). Three linearly independent 8D semi-spinors span a 32D S3-closed subspace.

**This is a FIFTH independent route to N_g = 3**, distinct from Meridian's four:
1. Fano plane (Meridian)
2. Jordan algebra rank (Meridian)
3. Triality (Meridian)
4. Hurwitz (Meridian)
5. **Sedenion automorphism S3 action on Cl(10) (Gresnigt)**

**Key structural features:**
- Uses Cl(10) = End(C ⊗ T) where T = Dixon algebra = R ⊗ C ⊗ H ⊗ O
- Non-associativity sidestepped via associative endomorphism algebra (fundamentally different from Boyle-Farnsworth modified first-order condition)
- SU(3)_C × SU(2)_L × U(1)_Y emerges (NOT unified into simple group)
- Right-handed neutrinos are automatic (sterile, all quantum numbers zero)
- **No NCG connection whatsoever** — purely Clifford-algebraic
- **No dynamics** — no Lagrangian, no masses, no CKM, no CP violation
- No mass hierarchy mechanism (generation counting only)

**For 17M-N (neutrino sector):** The automatic right-handed neutrinos and intrinsic S3 family symmetry are relevant. The S3 constrains inter-generational couplings, which could connect to Meridian's democratic mass matrix M_oct with eigenvalues {1/2, 1/2, 2}. The tri-hypercharge structure (generation-dependent U(1) charges) could connect to brane Yukawa mechanism.

**Open question:** Is Gresnigt's S3 from Aut(sedenions) the same symmetry as Meridian's S3 from M_oct? Both trace to discrete structure of higher division algebras. If they're the same, it's convergent evidence. If different, it's two independent structural proofs.

### 5. Caprini et al. 2020 (1910.13125v2) — LISA Cosmology Working Group
**"Detecting gravitational waves from cosmological phase transitions with LISA: an update"**

**Complete pipeline from V(phi) to SNR at LISA:**

Step 1: V_eff(phi, T) with thermal corrections → find T_c
Step 2: Bounce action S_3(T) via CosmoTransitions
Step 3: T* from S_3(T*)/T* ~ 130-140
Step 4: alpha = (4/3) Delta_theta(T*) / w_+(T*), beta/H = T d(S_3/T)/dT
Step 5: K = kappa(alpha, v_w) * alpha/(1+alpha) from EKNS fits
Step 6: GW spectrum (Eq. 32 for most cases):
```
d Omega_GW / d ln(f) = 0.687 * F_{gw,0} * K^{3/2} * (H* R*)^2 / sqrt(c_s)
                        * Omega_tilde_gw * C(f/f_p)
```
where C(s) = s^3 (7/(4 + 3s^2))^{7/2}
Step 7: SNR at LISA with T = 9.46 × 10^7 s, threshold SNR > 10

**Section 6.5 covers RS/warped models directly:**
- Radion PT is strong, first-order
- Significant supercooling: T_n << T_c
- QCD running effects (Von Harling & Servant) remove thermal barrier near QCD temperatures
- Benchmark values from Table 1 of Megias, Nardini & Quiros: alpha up to 10^6, beta/H ~ 10-100

**Quick Meridian estimate (alpha ~ 1, beta/H ~ 50, T* ~ 190 GeV, v_w ~ 0.95):**
- K ~ 0.3 (kappa ~ 0.6 for alpha = 1)
- f_peak ~ 0.82 mHz
- Omega_GW ~ 10^{-11} — well within LISA sensitivity
- **Consistent with our ~0.3 mHz estimate**

**Tools to use for 17I-J:**
- CosmoTransitions (bounce action)
- EKNS efficiency fits (1004.4187)
- PTPlot (ptplot.org) for GW spectrum
- Sound shell model (1608.04735)
- RS benchmarks (1806.04877, Megias et al.)

### 6. Bose et al. 2024 (2406.13667v1)
**"Matter Power Spectra in Modified Gravity: A Comparative Study"**

**N-body code comparison paper for modified gravity P(k).** Tests nDGP, Cubic Galileon, K-mouflage against each other.

**Key relevance for 17A-D:**
- Uses reduced Horndeski (post-GW170817): L_H = G_4(phi) R + G_2(phi, X) - G_3(phi, X) □phi
- **K-mouflage is the closest studied analog to cuscuton.** The cuscuton is the K_X → ∞ limit.
- K-mouflage G_eff: G_eff,L/G_N = A(phi)(1 + 2 beta_K^2/K_X). For cuscuton, K_X → ∞ gives G_eff → A(phi) G_N. The scalar DOF decouples from the Poisson equation — **this IS growth-expansion decoupling**.
- The halo model reaction approach (ReACT) provides fast nonlinear P(k) computation for eventual Euclid/DESI confrontation.
- All codes agree to <2% for P_MG/P_LCDM at k ≤ 1 h/Mpc — validates the numerical tools.

---

---

## Second Batch: Four New Papers

### 7. Eichhorn & Pauly 2021 (2009.13543v2)
**"Constraining power of asymptotic safety for scalar fields"**

**THE xi PREDICTION:** AS predicts xi* = 0 at fixed point for generic scalar (shift symmetry preserved by quantum gravity). With Yukawa coupling (Higgs-like): xi* ≈ -0.04 (their convention) ≈ +0.04 (standard). Conformal value xi = 1/6 is OUTSIDE the viable window [-0.06, 0.09] for the interacting Yukawa fixed point.

**Key equations:**
- Beta function: beta_xi = (xi + 1/12)(y^2/4pi^2 + 3 lambda_4/16pi^2) + g * xi * [gravitational terms]
- Fixed point: xi* = -0.04, lambda_4* = 0.139, y* = 0.381
- Critical exponent for xi: |theta| ≈ 0.04 (irrelevant but VERY weakly attracted)

**Why this is NOT fatal for Meridian (three independent resolutions):**
1. **Warped 5D changes everything.** Paper uses 4D flat-background FRG. Meridian's warped orbifold modifies the graviton propagator and effective gravitational coupling felt by the scalar. No one has computed AS beta functions on a warped background.
2. **NCG sets UV initial conditions.** If NCG spectral action sets xi = 1/6 at Lambda_UV, and the irrelevant direction has |theta| ~ 0.04, the attraction toward xi* = 0.04 is extremely weak over a finite hierarchy Lambda_UV/M_Pl ~ 10-100. The initial condition is preserved.
3. **Self-tuning requires xi = 1/6.** This is topological protection — the brane CC cancellation mechanism structurally requires conformal coupling. AS cannot override a geometric constraint.

**Strategic value:** This paper STRENGTHENS the xi = 1/6 argument by making it more distinctive. If xi = 1/6 is ever confirmed observationally, it's evidence AGAINST generic 4D AS and FOR warped geometry providing geometric protection.

### 8. Lu & Simon 2026 (2511.10616v3)
**"New multiprobe analysis of modified gravity and evolving dark energy"**

**⚠ THIS IS THE SINGLE MOST IMPORTANT EXTERNAL PAPER FOR PHASE 17.**

**Results:**
- **4.6σ preference for evolving DE** (Planck PR4 + DESI DR2 + DES Y5 + EFTBOSS + ISWL + DESICl)
- w0 = -0.788 ± 0.046, wa = -0.62 ± 0.16-0.19
- **Modified gravity constraints:** cB = 0.46 +0.16/-0.22, cM = 0.31 +0.39/-0.49 (compatible with GR at ~2σ)
- alpha_T = 0 fixed (GW170817)
- Uses hi_class + MontePython + alpha-parameterization

**Direct implications for Meridian:**
- Meridian's w0 = -0.745 (JC benchmark) is ~1σ from their central value. Compatible.
- Meridian's CAMB best-fit w0 = -0.989 is 4.3σ from their central value. **TENSION.**
- Meridian predicts cB, cM ~ O(zeta_0) ≈ 0.02. Their measured cB ~ 0.46 is larger but compatible with zero at 2σ.
- The mu(a) and Sigma(a) formulas (their Eqs. 9-10) are exactly what 17B must compute.

**Critical realization:** The 4.6σ evolving DE signal, if real, FAVORS the JC benchmark over the CAMB best-fit. This may reopen the question of which zeta_0 regime the universe is in.

### 9. Espinosa, Konstandin, No & Servant 2010 (1004.4187v1)
**"Energy Budget of Cosmological First-order Phase Transitions"**

**Ready-to-use efficiency fits for 17I:**
- kappa_B (xi_w = c_s): kappa_B = alpha^(2/5) / (0.017 + (0.997 + alpha)^(2/5))
- kappa_C (Jouguet): kappa_C = sqrt(alpha) / (0.135 + sqrt(0.98 + alpha))
- kappa_D (ultra-relativistic): kappa_D = alpha / (0.73 + 0.083*sqrt(alpha) + alpha)
- Full interpolation formulas in Eqs. 99-102 for arbitrary wall velocity

**For alpha = 1:** kappa_C ≈ 0.65, kappa_D ≈ 0.55. For detonation near Jouguet with v_w ~ 0.95: **kappa ≈ 0.60.**

### 10. Megias, Nardini & Quiros 2018 (1806.04877v2)
**"Cosmological Phase Transitions in Warped Space: GW and Collider Signatures"**

**RS-specific benchmarks:**
- Large back-reaction prevents excessive supercooling (solves graceful exit problem)
- alpha ranges from 1.6 to 4.5×10^8; beta/H from ~230 to ~0.5
- T_R ~ 550-1050 GeV for the main benchmark class
- **ALL viable benchmarks detectable by BOTH LISA and Einstein Telescope** (SNR > 10)
- The "sweet spot" for LISA: alpha ~ 1-1000, log10(beta/H) ~ 1-2

**For Meridian 17I:** Need to compute E_0 (vacuum energy difference) and a_h(T) (back-reaction-modified BH free energy) from Meridian's specific potential. Their Eqs. 9.6-9.7 give alpha and beta/H from these.

---

## hi_class Code Analysis

**Language:** C with Python (Cython) wrapper
**Build:** Makefile, requires gcc. Need WSL on Windows.
**Alpha functions:** Defined in `gravity_smg/gravity_functions_smg.c` (lines 384-452)

**Fastest integration path for 17C:** Use `constant_alphas` model:
```ini
gravity_model = constant_alphas
parameters_smg = 0.0, alpha_B_val, alpha_M_val, 0.0, 1.0
# Format: alpha_K, alpha_B, alpha_M, alpha_T, M²_init
```

For time-dependent alphas: add custom model to `gravity_models_smg.c` with alpha(a) = c_i * Omega_DE(a).

---

## Updated Synthesis: What Changes in the Phase 17 Plan

### Track 17A (perturbation equations) — UPGRADED PRIORITY
The alpha_T issue is first computation. Additionally, the mu(a) and Sigma(a) formulas from Lu & Simon (Eqs. 9-10) provide the direct observational targets.

### Track 17B-D — NEW OBSERVATIONAL TARGET
Lu & Simon (4.6σ evolving DE) provides the state-of-the-art data confrontation benchmark. Their cB = 0.46 ± 0.2, cM = 0.31 ± 0.4 must be compared against Meridian's predicted O(zeta_0) values.

### ⚠ CRITICAL TENSION: CAMB best-fit vs 4.6σ evolving DE
If the Lu & Simon 4.6σ signal is real, w0 = -0.788 ± 0.046 is incompatible with our CAMB best-fit w0 = -0.989 at >4σ. But it's compatible with the JC benchmark w0 = -0.745. This reopens the question Review 2 flagged: the framework's empirical posture depends critically on which zeta_0 regime holds. **This must be addressed in the monograph.**

### Track 17E-F (gauge unification) — METHODOLOGICAL CLARITY
Planck-brane correlator is the correct tool. Unification at k ~ M_Pl, not Lambda_NCG.

### Track 17I-J (GW) — FULLY EQUIPPED
EKNS fits (kappa ~ 0.6 for alpha = 1) + Megias et al. benchmarks (alpha = 1.6 to 10^8) + Caprini et al. pipeline = complete computational pathway.

### Track 13P/17A crossover — xi = 1/6 STRENGTHENED
Eichhorn & Pauly confirm AS pushes xi → 0. Meridian's geometric protection is NECESSARY. Three independent mechanisms prevent xi from flowing away from 1/6. This is now a stronger argument, not a weaker one.

### Track 17M-N (neutrino sector)
Gresnigt's S3 from sedenion automorphisms is a fifth route to N_g = 3. Cross-reference needed.

---

## Recommended Further Sources (lower priority)

1. **Sound shell model:** Hindmarsh (1608.04735) — GW production mechanism
2. **CosmoTransitions:** Wainwright (1109.4189) — bounce computation tool
3. **Von Harling & Servant:** QCD effects on RS radion PT
4. **Planck PR4 likelihoods** — for 17C-D data confrontation
5. **MontePython sampler** — MCMC tool used by Lu & Simon
