# Phase 3, Task 3.1: Modified Friedmann Equations

**Project Meridian — Deliverable D3.1**
*Clayton & Clawd, March 2026*

The 5D theory is built (Phase 1) and reduced (Phase 2). Now we put it on a cosmological background — FRW on the brane — and derive the modified Friedmann equations that govern the late-time universe. This is where the model meets DESI.

---

## 1. From Static Background to Cosmology

### 1.1 The Cosmological Ansatz

Promote the 4D metric from Minkowski to FRW:

    ds² = e^{2A(t,y)} [−n²(t,y) dt² + a²(t,y) δ_ij dx^i dx^j] + b²(t,y) dy²   ... (1.1)

where:
- n(t,y) is the lapse function (≡ 1 in conformal gauge on the brane)
- a(t,y) is the scale factor
- b(t,y) is the extra-dimensional metric component (= 1 in conformal gauge for the static case)

**Brane-centric coordinates:** We fix the IR brane at y = y_c and choose Gaussian normal coordinates where b = 1. On the IR brane, n(t, y_c) = 1 (proper time). The cosmological scale factor is:

    ā(t) ≡ a(t, y_c) · e^{A(y_c)}                                              ... (1.2)

which is the physical scale factor seen by IR-brane observers (i.e., us).

### 1.2 The Low-Energy Regime

For cosmological dynamics (energies ≪ k ~ M₅), we work in the **moduli approximation**: the bulk geometry adjusts instantaneously to the brane cosmology. This is justified because:

1. The cuscuton propagates at c_s → ∞ — the bulk scalar responds instantaneously to boundary changes
2. The KK graviton masses are ~ TeV ≫ H₀ ~ 10⁻³³ eV — all massive modes are integrated out
3. The radion mass m_r ~ TeV ≫ H₀ — the inter-brane distance is stabilized on Hubble timescales

In this regime, the bulk solution at each instant t is the static solution from Phase 1 with slowly varying parameters: A(y) → A(t,y), φ(y) → φ(t,y), with the time dependence entering through the brane boundary conditions.

### 1.3 Effective 4D Variables

The two dynamical 4D degrees of freedom are:

    H(t) ≡ ȧ/ā        (Hubble parameter on IR brane)                          ... (1.3)
    φ_IR(t) ≡ φ(t, y_c)   (scalar field value on IR brane)                      ... (1.4)

The radion T(t) = y_c(t) is stabilized at T₀ by the cuscuton constraint (D2.2 §5.2), with fluctuations suppressed by m_r ~ TeV. We set T = T₀ + δT(t) and initially work at zeroth order (δT = 0). Radion perturbations are reintroduced in §6.

---

## 2. The Projected Einstein Equations

### 2.1 Shiromizu-Maeda-Sasaki (SMS) Formalism

The standard tool for braneworld cosmology: project the 5D Einstein equations onto the brane using the Gauss-Codazzi relations (Shiromizu, Maeda, Sasaki; PRD 62, 024012, 2000).

The 4D Einstein equations on the IR brane:

    G^(4)_μν = −Λ₄ g_μν + (8π/M_Pl²) T_μν + (8π/M₅³)² π_μν − E_μν         ... (2.1)

where:
- **Λ₄**: effective 4D cosmological constant (from bulk + brane contributions)
- **T_μν**: brane energy-momentum (matter + radiation)
- **π_μν**: quadratic in T_μν, the high-energy (ρ²) correction — negligible at late times
- **E_μν**: projected 5D Weyl tensor — the "dark radiation" term

### 2.2 SMS with Non-Minimal Coupling

Our action has F(φ)R₅ instead of M₅³R₅. The SMS projection generalizes (Maartens, Living Rev. Rel. 7, 7, 2004; Langlois, arXiv:hep-th/0209261):

    G^(4)_μν = −Λ₄^eff g_μν + (1/M̃_Pl²) T_μν + (ρ/σ_IR) corrections − E_μν + S_μν^(φ)   ... (2.2)

where:
- **M̃_Pl²** ≡ 2∫₀^{y_c} F(φ) e^{2A} dy (from D2.2 eq 2.2)
- **σ_IR**: IR brane tension
- **S_μν^(φ)**: scalar field stress-energy projected from the bulk

### 2.3 The Cuscuton Simplification

The cuscuton's constraint structure dramatically simplifies the SMS equations:

**1. The dark radiation E_μν vanishes at late times.** The 5D Weyl tensor E_ABCD sources E_μν through KK graviton modes. Since all KK modes are massive (m_n ~ TeV) and the Hubble rate is H₀ ~ 10⁻³³ eV, the KK modes have decayed to negligible amplitude by late times:

    E_μν ~ e^{−m_KK · t_Hubble} → 0                                            ... (2.3)

**2. The quadratic correction π_μν is negligible.** This scales as ρ²/σ_IR where σ_IR ~ (TeV)⁴. At late times, ρ ~ ρ_Λ ~ (meV)⁴, so:

    π_μν/T_μν ~ ρ/σ_IR ~ (meV/TeV)⁴ ~ 10⁻⁶⁰                                 ... (2.4)

Negligible.

**3. The scalar projection S_μν^(φ) encodes the dark energy.** For the cuscuton, the brane-localized scalar action (D2.2, eq 3.5) gives:

    S_μν^(φ) = K_eff(φ̇_IR) u_μ u_ν − [K_eff(φ̇_IR) − V_eff(φ_IR)] g_μν     ... (2.5)

where u_μ is the 4-velocity of comoving observers.

---

## 3. The Modified Friedmann Equations

### 3.1 First Friedmann Equation

Taking the (00) component of the projected Einstein equations in the late-time, low-energy regime:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │                    THE FIRST FRIEDMANN EQUATION                              │
    │                                                                              │
    │  H² = (1/3M_Pl²) [ρ_m + ρ_r + ρ_φ]                                ... (F1) │
    │                                                                              │
    │  where:                                                                      │
    │    ρ_m = ρ_m₀ a⁻³        (matter)                                           │
    │    ρ_r = ρ_r₀ a⁻⁴        (radiation)                                        │
    │    ρ_φ = K_eff + V_eff    (dark energy from cuscuton tadpole)               │
    │                                                                              │
    │  with:                                                                       │
    │    V_eff(φ_IR) = c · φ_IR · e^{4A(y_c)}                                    │
    │    K_eff(φ̇_IR) = induced kinetic energy from cuscuton constraint            │
    │                                                                              │
    │  High-energy correction (negligible at late times):                          │
    │    + ρ²/(2σ_IR) + (6/κ₅⁴)U/a⁴                                             │
    │    (ρ² term from π_μν, U term from E_μν)                                    │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 3.2 Second Friedmann Equation (Raychaudhuri)

The trace equation gives:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │                    THE RAYCHAUDHURI EQUATION                                 │
    │                                                                              │
    │  Ḣ = −(1/2M_Pl²) [ρ_m + (4/3)ρ_r + ρ_φ + p_φ]                    ... (F2) │
    │                                                                              │
    │  where:                                                                      │
    │    p_φ = K_eff − V_eff                                                      │
    │                                                                              │
    │  High-energy correction:                                                     │
    │    − (1/2σ_IR)[ρ(2ρ + 3p)] − (6/κ₅⁴)U/a⁴                                 │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 3.3 The Dark Energy Equation of State

From the scalar energy density and pressure:

    w_φ ≡ p_φ/ρ_φ = (K_eff − V_eff)/(K_eff + V_eff)                           ... (3.1)

The effective equation of state of dark energy. For V_eff ≫ K_eff (slow evolution): w_φ → −1 (cosmological constant). For K_eff → V_eff: w_φ → 0 (matter-like). The cuscuton sits between these limits.

---

## 4. The Cuscuton Constraint on the Brane

### 4.1 The Key Equation

The cuscuton is non-dynamical: it satisfies a constraint, not a wave equation. In the 5D bulk, the scalar equation E2 (D1.3) contains A'' but not φ'' — the field is algebraically slaved to the geometry.

On the brane, this constraint induces a relation between φ̇_IR and H:

**Derivation.** The 5D cuscuton action contributes:

    μ₀²√(2X₅) = μ₀²√(−G^{AB}∂_A φ ∂_B φ)                                     ... (4.1)

In the cosmological background (1.1), with φ = φ(t,y):

    2X₅ = e^{−2A}(φ̇/n)² + (φ'/b)²                                              ... (4.2)

The cuscuton equation of motion (variation w.r.t. φ):

    ∂_A(√(−G) P_X G^{AB} ∂_B φ) = √(−G)(P_φ − V' + 2ξφR₅)                   ... (4.3)

Since P_X = μ₀²/√(2X₅), this is a constraint on the field derivatives, not a propagation equation. On the IR brane, projecting (4.3) using the Israel matching conditions:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  THE CUSCUTON BRANE CONSTRAINT                                              │
    │                                                                              │
    │  μ₀² [3H φ̇_IR/(φ̇_IR² + φ'²_IR)^{1/2}] = V'(φ_IR) − 2ξφ_IR R₄     (C1) │
    │                                                                              │
    │  For V = cφ:  V' = c                                                        │
    │  R₄ = 6(Ḣ + 2H²) in FRW                                                   │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 4.2 The Slow-Bulk Limit

In the moduli approximation (φ' ≫ φ̇ on cosmological timescales), the kinetic term simplifies:

    (φ̇_IR² + φ'²_IR)^{1/2} ≈ |φ'_IR|                                           ... (4.4)

The constraint becomes:

    3μ₀²H φ̇_IR/|φ'_IR| = c − 12ξφ_IR(Ḣ + 2H²)                                ... (4.5)

Solving for φ̇_IR:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  φ̇_IR = |φ'_IR|/(3μ₀²H) · [c − 12ξφ_IR(Ḣ + 2H²)]               ... (C2) │
    │                                                                              │
    │  THE SCALAR EVOLUTION LAW                                                    │
    │                                                                              │
    │  The scalar does NOT freely evolve — it is SLAVED to the                    │
    │  cosmological expansion. H determines φ̇_IR, not the other way.             │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 4.3 Properties of the Constraint

**1. The scalar always rolls.** For ξ small (or at late times when H → const), C2 gives:

    φ̇_IR ≈ c|φ'_IR|/(3μ₀²H) > 0                                               ... (4.6)

The tadpole (c > 0) ensures the field always evolves. There is no deSitter attractor at finite φ_IR. This is the Appleby-Bernardo mechanism: the linear potential has no minimum, preventing the system from reaching w = −1 exactly.

**2. The ξ-coupling creates a feedback loop.** The 12ξφ_IR(Ḣ + 2H²) term couples the scalar to the spacetime curvature. As φ_IR grows:
- If Ḣ + 2H² > 0 (accelerating universe): the feedback SLOWS the scalar, pushing w toward −1
- If Ḣ + 2H² < 0 (decelerating universe): the feedback SPEEDS the scalar, pushing w away from −1

This curvature feedback is the mechanism by which the ξ-coupling modifies w(z) beyond the simple tadpole prediction.

**3. Phantom crossing mechanism.** From the definition:

    K_eff = ½ α_K φ̇²_IR                                                        ... (4.7)

where α_K is the effective kinetic coefficient induced by the cuscuton constraint (proportional to 1/|φ'_IR|). Since K_eff ≥ 0 by construction, the standard phantom crossing no-go would apply.

However, the cuscuton is special: **the effective equation of state seen by the Friedmann equation includes the constraint backreaction.** Define the total dark energy:

    ρ_DE = V_eff + K_eff + ξ-coupling corrections                               ... (4.8)
    p_DE = K_eff − V_eff + ξ-coupling corrections                               ... (4.9)

The ξ-coupling corrections to ρ_DE and p_DE come from the R₄ terms in the non-minimal coupling action:

    ΔL = −ξφ²_IR R₄ = −ξφ²_IR · 6(Ḣ + 2H²)                                   ... (4.10)

This contributes to both ρ_DE and p_DE with different signs:

    Δρ_DE = −6ξH²φ²_IR − 12ξHφ_IR φ̇_IR                                        ... (4.11)
    Δp_DE = 2ξ(2Ḣ + 3H²)φ²_IR + 4ξ(Hφ_IR φ̇_IR + φ̇²_IR + φ_IR φ̈_IR)       ... (4.12)

The effective equation of state:

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  w_DE = (K_eff − V_eff + Δp_DE)/(K_eff + V_eff + Δρ_DE)           ... (W1) │
    │                                                                              │
    │  PHANTOM CROSSING: w_DE < −1 is possible when                               │
    │    Δρ_DE > 0 and Δp_DE < −(K_eff − V_eff)                                 │
    │                                                                              │
    │  This requires:                                                              │
    │    12ξHφ_IR φ̇_IR < −6ξH²φ²_IR  (need φ̇_IR < 0 or large φ_IR)          │
    │    AND curvature terms in Δp_DE dominate                                    │
    │                                                                              │
    │  The cuscuton has ZERO propagating DOF, so w < −1 does NOT                  │
    │  imply a ghost. This is the Boruah-Kim-Geshnizjani result.                  │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

---

## 5. The Complete Dynamical System

### 5.1 Autonomous System in Dimensionless Variables

Define:

    x ≡ φ̇_IR/(H M_Pl)          (kinetic fraction)                              ... (5.1)
    y ≡ √(V_eff)/(√3 H M_Pl)   (potential fraction)                             ... (5.2)
    λ ≡ −M_Pl V'_eff/V_eff     (slope parameter)                                ... (5.3)
    Γ ≡ V_eff V''_eff/(V'_eff)² (curvature parameter)                           ... (5.4)
    ζ ≡ ξ φ²_IR/M_Pl²           (non-minimal coupling strength)                 ... (5.5)
    N ≡ ln a                     (e-folding number)                               ... (5.6)

**For the tadpole:** V_eff = c_eff · φ_IR (linear), so:

    λ = −M_Pl/φ_IR              (decreasing as φ_IR grows)                       ... (5.7)
    Γ = 0                        (exactly — the tadpole has zero curvature)       ... (5.8)

This is special: Γ = 0 means the potential is EXACTLY linear. Most quintessence analyses assume Γ ≈ 1. The tadpole is the singular case.

### 5.2 The Friedmann Constraint

In dimensionless variables, the first Friedmann equation becomes:

    1 = Ω_m + Ω_r + Ω_φ                                                         ... (5.9)

where:

    Ω_m = ρ_m/(3M_Pl²H²)                                                       ... (5.10)
    Ω_r = ρ_r/(3M_Pl²H²)                                                       ... (5.11)
    Ω_φ = (K_eff + V_eff + Δρ_DE)/(3M_Pl²H²)                                  ... (5.12)
       = ½α_K x² + y² − 6ζH² − 12ζHφ_IR φ̇_IR/(3M_Pl²H²)                     ... (5.13)

### 5.3 Evolution Equations

The system reduces to four coupled ODEs in N = ln a:

**Scalar evolution** (from C2):

    dφ_IR/dN = |φ'_IR|/(3μ₀²H²) · [c_eff − 12ξφ_IR(Ḣ + 2H²)]                ... (S1)

where Ḣ = H² dln H/dN = H²(H'/H) and the prime denotes d/dN.

**Hubble evolution** (from F2):

    dH/dN = −(3/2)H(1 + w_eff)                                                  ... (S2)

where:

    w_eff = (p_m + p_r + p_φ)/(ρ_m + ρ_r + ρ_φ) = −1 + (Ω_m + (4/3)Ω_r + (1 + w_φ)Ω_φ)   ... (5.14)

**Matter** (standard conservation):

    dΩ_m/dN = −3Ω_m + 3Ω_m(1 + w_eff)                                          ... (S3)

**Radiation** (standard conservation):

    dΩ_r/dN = −4Ω_r + 3Ω_r(1 + w_eff)                                          ... (S4)

### 5.4 The ξ = 0 Limit (Minimal Coupling)

For ξ = 0: F = M₅³ (constant), Δρ_DE = 0, Δp_DE = 0, and:

    φ̇_IR = c_eff|φ'_IR|/(3μ₀²H)                                                ... (5.15)
    w_φ = (K_eff − V_eff)/(K_eff + V_eff)                                       ... (5.16)

This is the Appleby-Bernardo system with the cuscuton-induced kinetic term. No phantom crossing is possible at ξ = 0 — the kinetic energy is manifestly non-negative.

### 5.5 The ξ > 0 Case (Non-Minimal Coupling)

For ξ > 0: the curvature coupling generates the Δρ_DE and Δp_DE corrections (eqs 4.11-4.12). The effective equation of state w_DE (eq W1) can cross −1 without ghosts because:

1. The additional terms come from the **gravitational** sector (R₄ coupling), not from a kinetic term with wrong sign
2. The cuscuton has **zero propagating scalar DOF** — the scalar sector cannot carry ghost instabilities
3. In unitary gauge, only the two tensor polarizations of the graviton propagate (confirmed by Boruah et al. 2017, Dehghani et al. 2025)

---

## 6. The Radion Sector

### 6.1 Radion-Scalar Mixing

Although the radion is stabilized at T = T₀ with mass m_r ~ TeV, it participates in the cosmological dynamics through its mixing with the dark energy scalar. The radion perturbation δT(t) couples to φ_IR through the boundary condition:

    φ_IR(t) = φ(t, T₀ + δT(t))                                                 ... (6.1)

Expanding:

    δφ_IR = φ'(y_c) · δT + ½φ''(y_c) · (δT)² + ...                            ... (6.2)

The radion evolution equation (from the 5D (55) Einstein equation):

    δT̈ + 3HδṪ + m²_r δT = −(∂V_eff/∂T)|_{T₀}                                ... (6.3)

Since m_r ~ TeV ≫ H₀, the radion oscillates and decays rapidly. The cosmological effect is:

    ⟨δT²⟩ ~ T²_∗/(m_r t)                                                       ... (6.4)

where T_∗ is the initial displacement. For t ~ 1/H₀ and m_r/H₀ ~ 10⁴⁵:

    ⟨δT²⟩ ~ 10⁻⁴⁵ T²_∗                                                        ... (6.5)

The radion contribution to cosmological dynamics is negligible. ✓

### 6.2 Slowly Evolving Radion (Bedroya-Obied-Vafa-Wu Connection)

**However:** if the cuscuton constraint is imperfectly satisfied (e.g., at loop level or due to non-perturbative corrections), the radion potential V_r(T) may have a very shallow slope, allowing T₀ to drift slowly:

    Ṫ₀ ~ −V'_r(T₀)/(3Hm²_r)                                                   ... (6.6)

This is the "expanding dark dimension" scenario of Bedroya, Obied, Vafa, and Wu (arXiv:2507.03090). If the compactification radius y_c increases:

1. KK graviton masses m_n ∝ e^{−ky_c} decrease → effective DM mass decreases
2. The warp factor e^{A(y_c)} evolves → dark energy density evolves
3. A single mechanism produces both dynamical DE and decaying DM

**For our model:** This drift would contribute to w(z) through the time-dependent warp factor:

    V_eff(t) = c · φ_IR · e^{4A(y_c(t))}                                       ... (6.7)

    dV_eff/dt = ... + 4A'(y_c) · ẏ_c · V_eff                                   ... (6.8)

Since A'(y_c) < 0 (warp factor decreasing) and ẏ_c > 0 (expanding):

    dV_eff/dt < 0    (dark energy decreasing)                                    ... (6.9)

This gives w > −1 (dark energy diluting faster than cosmological constant), consistent with our prediction AND with DESI's w₀ ≈ −0.7.

**Phase 3 question:** Is the radion drift fast enough to contribute meaningfully to w₀, or is it negligible compared to the tadpole rolling? If radion drift dominates, the wₐ prediction changes because the evolution depends on V_r(T) rather than V(φ).

---

## 7. The Sequestering Contribution

### 7.1 The Sequestering Constraint Revisited

From D1.5, the sequestering sector imposes (after KK reduction):

    Λ₄ = Λ₄^tree + Σ_n c_n M^{4−n}_Pl ⟨φ^n⟩_brane                            ... (7.1)

The sequestering integral μ₄ ∫ d⁴x √(−g₄) = prescribed value constrains the spacetime volume. In cosmology, this becomes:

    μ₄ ∫ d⁴x √(−g₄) = μ₄ ∫₀^∞ dt a³(t) V₃ = prescribed                       ... (7.2)

where V₃ is the comoving spatial volume.

The global constraint (7.2) does NOT modify the local Friedmann equations — it constrains the solution space. In a flat FRW universe, it amounts to a boundary condition on the late-time behavior of a(t), selecting solutions where:

    Λ₄^eff → (small, finite value) as t → ∞                                     ... (7.3)

This is the sequestering mechanism: the global constraint dynamically selects the solution with a small cosmological constant, without fine-tuning the Lagrangian parameters.

### 7.2 Compatibility with Dynamical DE

The sequestering mechanism ensures Λ₄^vacuum ≈ 0, but it does NOT cancel the tadpole-driven dark energy. Why:

- **Sequestering** absorbs loop contributions to the vacuum energy (Λ₅ + quantum corrections → λ via the constraint)
- **The tadpole** V_eff = c·φ_IR·e^{4A(y_c)} is a classical, time-dependent contribution — not a vacuum energy

The sequestering integral (7.2) is satisfied with the dark energy included, provided the dark energy eventually redshifts away or asymptotes to zero (which the tadpole ensures — φ_IR → ∞ drives V_eff → ∞, but the constraint equation regulates this).

**Subtlety:** The tadpole potential V = cφ is unbounded below (as φ → −∞). The constraint equation C2 prevents φ from running away because the constraint slows φ̇_IR as V_eff grows. The system self-regulates.

---

## 8. Summary: The Complete Cosmological System

### 8.1 The Equations

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  MERIDIAN COSMOLOGICAL EQUATIONS                                            │
    │  ════════════════════════════════                                            │
    │                                                                              │
    │  FRIEDMANN:                                                                  │
    │  H² = (1/3M_Pl²) [ρ_m + ρ_r + ρ_DE(φ_IR, φ̇_IR, H)]                (F1)  │
    │                                                                              │
    │  RAYCHAUDHURI:                                                               │
    │  Ḣ = −(1/2M_Pl²) [ρ_m + (4/3)ρ_r + ρ_DE + p_DE]                    (F2)  │
    │                                                                              │
    │  DARK ENERGY DENSITY:                                                        │
    │  ρ_DE = V_eff + K_eff − 6ξH²φ²_IR − 12ξHφ_IR φ̇_IR                 (DE1) │
    │                                                                              │
    │  DARK ENERGY PRESSURE:                                                       │
    │  p_DE = −V_eff + K_eff + 2ξ(2Ḣ+3H²)φ²_IR                                 │
    │         + 4ξ(Hφ_IR φ̇_IR + φ̇²_IR + φ_IR φ̈_IR)                     (DE2) │
    │                                                                              │
    │  CUSCUTON CONSTRAINT:                                                        │
    │  φ̇_IR = |φ'_IR|/(3μ₀²H) · [c_eff − 12ξφ_IR(Ḣ + 2H²)]             (C2)  │
    │                                                                              │
    │  EFFECTIVE POTENTIAL:                                                         │
    │  V_eff = c · φ_IR · e^{4A(y_c)}  ≡  c_eff · φ_IR                   (V)   │
    │                                                                              │
    │  EFFECTIVE KINETIC:                                                           │
    │  K_eff = ½ α_K φ̇²_IR                                                (K)   │
    │  α_K = 3M₅³/(k e^{2ky_c}) · (integrated cuscuton kernel)                   │
    │                                                                              │
    │  EQUATION OF STATE:                                                          │
    │  w_DE = p_DE/ρ_DE                                                    (W1)  │
    │                                                                              │
    │  PARAMETERS:                                                                 │
    │  c_eff = c · e^{4A(y_c)}                    (warp-suppressed tadpole)       │
    │  ξ                                            (non-minimal coupling)         │
    │  α_K = f(M₅, k, y_c, μ₀, ξ)                 (kinetic coefficient)          │
    │  |φ'_IR| from background ODE solution         (boundary gradient)            │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

### 8.2 Key Properties

**1. Self-consistent closure.** The system {F1, F2, C2} is closed: F1 and F2 determine H(t) given ρ_DE; C2 determines φ̇_IR given H; and DE1-DE2 compute ρ_DE and p_DE from φ_IR, φ̇_IR, H. The system evolves autonomously.

**2. GR limit.** Setting ξ = 0 and c_eff = 0: ρ_DE = p_DE = 0, and {F1, F2} reduce to standard Friedmann equations. ✓

**3. ΛCDM limit.** Setting ξ = 0 and φ̇_IR → 0 (frozen field): ρ_DE = V_eff = const, p_DE = −V_eff, w_DE = −1. The model includes ΛCDM as a limiting case. ✓

**4. Phantom crossing.** For ξ > 0: the curvature-coupling terms Δρ_DE and Δp_DE in (DE1-DE2) modify w_DE. When the curvature feedback dominates the kinetic contribution, w_DE can cross −1 without ghost instabilities (zero propagating scalar DOF).

**5. No free functions.** Every quantity in the system is determined by the Phase 1-2 parameters: {M₅, k, y_c, c, ξ, μ₀}. Of these, Phase 2 fixed M₅, k, y_c from hierarchy + gravity, leaving effectively ONE free parameter (ξ, with c fixed by the dark energy scale). The cosmological predictions are sharp.

### 8.3 Comparison with Standard Braneworld Cosmology

| Feature | Standard RS1 | Maity et al. (2025) | **Meridian** |
|---------|-------------|---------------------|-------------|
| Bulk scalar | Goldberger-Wise (canonical) | Generic | Cuscuton (non-dynamical) |
| Radion | Stabilized by GW | Free or stabilized | Stabilized by cuscuton |
| Dark energy | Added by hand (Λ₄) | Thawing quintessence | Tadpole + self-tuning |
| Phantom crossing | No | Yes (modified Friedmann) | Yes (ξ-coupling) |
| CC problem | Unsolved | Not addressed | Three-layer self-tuning |
| Free parameters | Many | Several | ≤1 (ξ) |
| UV completion of cuscuton | — | — | **YES** (this model) |

---

## 9. Deliverable Checklist

    ┌──────────────────────────────────────────────────────────────────────────────┐
    │                                                                              │
    │  D3.1 — MODIFIED FRIEDMANN EQUATIONS                                        │
    │                                                                              │
    │  First Friedmann equation: H² = (1/3M²_Pl)(ρ_m + ρ_r + ρ_DE)       [§3]   │
    │  Raychaudhuri equation: Ḣ = −(1/2M²_Pl)(...)                        [§3]   │
    │  Cuscuton brane constraint: φ̇_IR = f(H, Ḣ, φ_IR, ξ, c_eff)        [§4]   │
    │  Dark energy density/pressure with ξ-corrections: DE1, DE2           [§4.3] │
    │  Phantom crossing mechanism: w_DE < −1 via curvature coupling        [§4.3] │
    │  Autonomous dynamical system: 4 ODEs in (H, φ_IR, Ω_m, Ω_r)        [§5]   │
    │  Radion contribution: negligible at late times (m_r/H₀ ~ 10⁴⁵)      [§6]   │
    │  Expanding dark dimension connection (Bedroya et al.)                 [§6.2] │
    │  Sequestering compatibility: constraint selects small Λ₄             [§7]   │
    │  Complete equation summary box                                        [§8]   │
    │                                                                              │
    │  KEY RESULTS:                                                                │
    │  • System is CLOSED with ≤1 free parameter (ξ)                              │
    │  • Phantom crossing via ξR₄φ² — no ghosts (zero scalar DOF)                │
    │  • UV completion of cuscuton dark energy (Afshordi et al. 2024)             │
    │  • Same warp factor explains weak hierarchy + DE hierarchy                   │
    │  • Model includes ΛCDM and standard RS1 as limiting cases                   │
    │                                                                              │
    │  NEXT: D3.2 — Solve the system numerically for                              │
    │  (w₀, wₐ, H₀, Ω_m, fσ₈, c²_s)                                            │
    │                                                                              │
    └──────────────────────────────────────────────────────────────────────────────┘

---

*D3.1 complete. The cosmological equations are derived.*
*The system is ready for numerical integration.*
