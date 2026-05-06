# Phase 1, Step 1: The Complete 5D Action

**Project Meridian — Deliverable D1.1**
*Clayton & Clawd, March 2026*

Every index. Every sign. Every term explicit.

---

## 1. Conventions and Notation

| Symbol | Meaning |
|--------|---------|
| M, N, P, Q | 5D indices: 0, 1, 2, 3, 5 |
| μ, ν, ρ, σ | 4D indices: 0, 1, 2, 3 |
| y (or x⁵) | Extra-dimension coordinate |
| G_MN | Full 5D metric |
| g_μν(x) | 4D metric (depends only on x^μ) |
| ' (prime) | d/dy |
| ∇_M | 5D covariant derivative compatible with G_MN |
| D_μ | 4D covariant derivative compatible with g_μν |
| □₅ | 5D d'Alembertian: G^MN ∇_M ∇_N |
| □₄ | 4D d'Alembertian: g^μν D_μ D_ν |
| R₅ | 5D Ricci scalar of G_MN |
| R₄ | 4D Ricci scalar of g_μν |

**Signature:** (−, +, +, +, +) — mostly plus.

**Sign conventions:**
- Einstein equation: G_MN = +8πG T_MN (MTW/Wald)
- Riemann: R^ρ_σμν = ∂_μ Γ^ρ_νσ − ∂_ν Γ^ρ_μσ + Γ^ρ_μλ Γ^λ_νσ − Γ^ρ_νλ Γ^λ_μσ
- Ricci: R_MN = R^P_MPN (contraction on first and third)

---

## 2. The General Warped Ansatz (Task 1.1)

The 5D line element with both warp factors dynamical:

    ds² = e^{2A(y)} g_μν(x) dx^μ dx^ν + e^{2B(y)} dy²         ... (2.1)

where:
- A(y): the warp factor (controls hierarchy between brane scales)
- B(y): the lapse of the extra dimension (gauge freedom; B = 0 is conformal gauge)
- g_μν(x): the 4D metric, independent of y at the background level

**Metric components:**

    G_μν = e^{2A(y)} g_μν(x)                                     ... (2.2a)
    G_55 = e^{2B(y)}                                              ... (2.2b)
    G_μ5 = 0                                                      ... (2.2c)

**Note on G_μ5 = 0:** This is a background-level simplification. The full KK ansatz includes off-diagonal components G_μ5 = κA_μ(x)e^{2A(y)}, where A_μ is the KK gauge field (identified with the electromagnetic potential in the KK reduction). Setting G_μ5 = 0 drops the EM sector from the background. The EM-gravity coupling through G_μ5 is restored in Task 2.4 and is potentially significant for gravitational modification via EM oscillation. See `external_data_eps.md` §3.1.

**Inverse metric:**

    G^μν = e^{-2A(y)} g^μν(x)                                    ... (2.3a)
    G^55 = e^{-2B(y)}                                             ... (2.3b)
    G^μ5 = 0                                                      ... (2.3c)

**Determinant:**

    det(G_MN) = e^{8A(y) + 2B(y)} det(g_μν)                      ... (2.4a)
    √(−G) = e^{4A + B} √(−g)                                     ... (2.4b)

**Note on topology:** The coordinate y ranges over:
- Compact interval: y ∈ [y₁, y₂] (two branes, RS-type)
- Semi-infinite ray: y ∈ [0, ∞) (one brane, RS2-type)
- Circle: y ∈ S¹ (periodic, no branes needed)

The topology determines boundary terms. Classification is Task 1.6.

---

## 3. Geometric Quantities

### 3.1 Christoffel Symbols

Non-vanishing 5D Christoffel symbols of G_MN:

    Γ^λ_μν = γ^λ_μν[g]       (4D Christoffel of g_μν)           ... (3.1a)

    Γ^λ_μ5 = A' δ^λ_μ                                            ... (3.1b)

    Γ^5_μν = −A' e^{2(A−B)} g_μν                                  ... (3.1c)

    Γ^5_55 = B'                                                    ... (3.1d)

All others vanish: Γ^μ_55 = 0, Γ^5_5μ = 0.

**Verification of (3.1b):**
Γ^λ_μ5 = ½ G^{λρ}(∂_μ G_{ρ5} + ∂_5 G_{μρ} − ∂_ρ G_{μ5})
        = ½ e^{-2A} g^{λρ}(0 + 2A' e^{2A} g_{μρ} − 0) = A' δ^λ_μ  ✓

**Verification of (3.1c):**
Γ^5_μν = ½ G^{55}(∂_μ G_{ν5} + ∂_ν G_{μ5} − ∂_5 G_{μν})
        = ½ e^{-2B}(0 + 0 − 2A' e^{2A} g_μν) = −A' e^{2(A−B)} g_μν  ✓

**Verification of (3.1d):**
Γ^5_55 = ½ G^{55} ∂_5 G_{55} = ½ e^{-2B} · 2B' e^{2B} = B'  ✓

### 3.2 5D Ricci Tensor

**R^(5D)_μν:**

    R^(5D)_μν = R^(4D)_μν − e^{2(A−B)} [A'' + 4(A')² − A'B'] g_μν    ... (3.2a)

Derivation: Expanding R_μν = ∂_P Γ^P_μν − ∂_ν Γ^P_μP + Γ^P_PQ Γ^Q_μν − Γ^P_νQ Γ^Q_μP with P, Q running over all 5D indices. The first bracket yields the 4D Ricci tensor R^(4D)_μν[g]. The remaining terms collect to:

    ∂_5 Γ^5_μν = −[A'' + 2A'(A' − B')] e^{2(A−B)} g_μν
    (Γ^ρ_ρ5 + Γ^5_55) Γ^5_μν = −(4A' + B') A' e^{2(A−B)} g_μν
    −Γ^ρ_ν5 Γ^5_μρ − Γ^5_νρ Γ^ρ_μ5 = +2(A')² e^{2(A−B)} g_μν

Sum: −[A'' + 2(A')² − 2A'B' + 4(A')² + A'B' − 2(A')²] e^{2(A−B)} g_μν
    = −[A'' + 4(A')² − A'B'] e^{2(A−B)} g_μν  ✓

**R^(5D)_55:**

    R^(5D)_55 = −4[A'' + (A')² − A'B']                            ... (3.2b)

Derivation: R_55 = ∂_P Γ^P_55 − ∂_5 Γ^P_5P + Γ^P_PQ Γ^Q_55 − Γ^P_5Q Γ^Q_5P

    ∂_P Γ^P_55 = B''                          (only P=5 contributes)
    −∂_5 Γ^P_5P = −(4A'' + B'')               (Γ^ρ_5ρ = 4A', Γ^5_55 = B')
    Γ^P_PQ Γ^Q_55 = (4A' + B') B'             (only Q=5 contributes)
    −Γ^P_5Q Γ^Q_5P = −4(A')² − (B')²

Sum: B'' − 4A'' − B'' + 4A'B' + (B')² − 4(A')² − (B')²
    = −4A'' − 4(A')² + 4A'B' = −4[A'' + (A')² − A'B']  ✓

**R^(5D)_μ5:**

    R^(5D)_μ5 = 0                                                  ... (3.2c)

(Vanishes by the block-diagonal structure of G_MN with A, B depending only on y.)

### 3.3 5D Ricci Scalar

    R₅ = G^MN R^(5D)_MN = G^μν R^(5D)_μν + G^55 R^(5D)_55

    G^μν R^(5D)_μν = e^{-2A} R₄ − 4e^{-2B} [A'' + 4(A')² − A'B']
    G^55 R^(5D)_55 = −4e^{-2B} [A'' + (A')² − A'B']

Therefore:

    ┌─────────────────────────────────────────────────────────────┐
    │  R₅ = e^{-2A} R₄ − e^{-2B} [8A'' + 20(A')² − 8A'B']     │  ... (3.3)
    └─────────────────────────────────────────────────────────────┘

**Check (RS gauge, B = 0):** R₅ = e^{-2A} R₄ − 8A'' − 20(A')²
For A = −k|y|, A' = −k, A'' = −2kδ(y) (distributional):
Away from branes: R₅ = e^{2k|y|} R₄ − 20k² → AdS₅ with R₅ = −20k² for flat branes.  ✓

---

## 4. The Bulk Action — S_bulk

    ┌──────────────────────────────────────────────────────────────────────┐
    │  S_bulk = ∫ d⁵x √(−G) [ (M₅³ − ξφ²) R₅ + P(X,φ) − V(φ) − Λ₅ ] │  ... (4.1)
    └──────────────────────────────────────────────────────────────────────┘

### 4.1 The Kinetic Sector: P(X, φ)

**Kinetic variable:**

    X = ½ G^MN ∂_M φ ∂_N φ                                        ... (4.2)

For the warped ansatz:

    X = ½ e^{-2A} g^μν ∂_μ φ ∂_ν φ + ½ e^{-2B} (φ')²            ... (4.3)

For background φ = φ(y) only:

    X₀ = ½ e^{-2B} (φ')²                                          ... (4.4)

**The function P(X, φ):**

| Choice | P(X, φ) | Notes |
|--------|---------|-------|
| Canonical | X | Standard kinetic term |
| DBI | −f(φ)^{-1} √(1 − 2f(φ)X) + f(φ)^{-1} | String-theory motivated |
| Cuscuton-like | μ²(φ)√(2X) | Self-tuning (Lacombe-Mukohyama, PRD 2022) |
| General shift-symmetric | P(X) | X-dependent only, no explicit φ |

The determination of which P(X,φ) is forced by singularity-free self-tuning in warped space is **Task 1.2** (Deliverable D1.2).

For now, we keep P(X,φ) general. All subsequent expressions are valid for arbitrary P.

**Key derivatives:**

    P_X ≡ ∂P/∂X|_φ                                                ... (4.5a)
    P_φ ≡ ∂P/∂φ|_X                                                ... (4.5b)
    P_XX ≡ ∂²P/∂X²|_φ                                             ... (4.5c)

For canonical P = X: P_X = 1, P_φ = 0, P_XX = 0.

### 4.2 The Non-Minimal Coupling: ξφ²R₅

The term −ξφ²R₅ in the action modifies the effective gravitational coupling:

    M²_eff(φ) = M₅³ − ξφ²                                         ... (4.6)

**Special values of ξ:**
- ξ = 0: minimal coupling
- ξ = 3/16: conformal coupling in 5D (from ξ_conf = (d−2)/4(d−1) with d=5)
- ξ > 0: required for hierarchy generation in RS-type models

**Constraint:** M²_eff > 0 everywhere (gravity remains attractive). This constrains |φ| < M₅^{3/2} / √ξ.

### 4.3 The Potential: V(φ)

General bulk potential. Not specified at this stage — constrained by self-tuning requirements (Task 1.4).

### 4.4 The Bare Cosmological Constant: Λ₅

Bare 5D cosmological constant. In the sequestering mechanism (Section 6), this is promoted to a global variable.

### 4.5 Explicit Bulk Action in Warped Coordinates

Substituting (2.4b) and (3.3) into (4.1):

    S_bulk = ∫ d⁴x dy · e^{4A+B} √(−g) ×
             [ (M₅³ − ξφ²) { e^{-2A} R₄ − e^{-2B} [8A'' + 20(A')² − 8A'B'] }
               + P(X,φ) − V(φ) − Λ₅ ]                            ... (4.7)

Distributing:

    S_bulk = ∫ d⁴x dy √(−g) [
        (M₅³ − ξφ²) e^{2A+B} R₄
      − (M₅³ − ξφ²) e^{4A−B} [8A'' + 20(A')² − 8A'B']
      + e^{4A+B} [P(X,φ) − V(φ) − Λ₅]
    ]                                                               ... (4.8)

**The A'' term** can be integrated by parts. Defining F(y) ≡ M₅³ − ξφ², the term involving A'' is:

    −8 ∫ dy F · e^{4A−B} A''

Integrating by parts (for the interval topology y ∈ [y₁, y₂]):

    = −8 [F e^{4A−B} A']_{y₁}^{y₂} + 8 ∫ dy A' ∂_y(F e^{4A−B})

    = −8 [F e^{4A−B} A']_{y₁}^{y₂}
      + 8 ∫ dy A' [F' e^{4A−B} + F(4A'−B') e^{4A−B}]

    = −8 [F e^{4A−B} A']_{y₁}^{y₂}
      + 8 ∫ dy e^{4A−B} [F' A' + 4F(A')² − FA'B']

where F' = −2ξφφ'. The boundary terms merge with the GHY contribution in Section 5.

---

## 5. The Boundary Action — S_bdy

### 5.1 Brane Action

For an interval topology with branes at y = y_i:

    ┌──────────────────────────────────────────────────────────────────┐
    │  S_brane = −∑_i ∫ d⁴x √(−h_i) [ σ_i + α_i φ²(y_i) + L_i ]  │  ... (5.1)
    └──────────────────────────────────────────────────────────────────┘

where:
- h_i^μν = e^{2A(y_i)} g_μν is the induced metric on brane i
- √(−h_i) = e^{4A(y_i)} √(−g)
- σ_i: brane tension (constant)
- α_i φ²: brane-localized scalar coupling
- L_i: brane-localized matter Lagrangian (SM fields live here)

**Topology-dependent boundary count:**
- Interval [y₁, y₂]: two branes, i = 1, 2 (RS1)
- Semi-infinite [0, ∞): one brane at y = 0 (RS2)
- Circle S¹: no branes (but orbifold S¹/Z₂ has two fixed points → two branes)

### 5.2 Gibbons-Hawking-York Term

Required for a well-posed variational principle with boundaries. For the non-minimally coupled action:

    ┌──────────────────────────────────────────────────────────────────────┐
    │  S_GHY = 2 ∑_i ε_i ∫ d⁴x √(−h_i) (M₅³ − ξφ²) K_i              │  ... (5.2)
    └──────────────────────────────────────────────────────────────────────┘

The factor (M₅³ − ξφ²) replaces M₅³ because the non-minimal coupling ξφ²R₅ generates its own boundary contribution.

**Extrinsic curvature:**

The unit outward normal to a y = const surface:

    n_M = ε e^B δ_M^5,    n^M = ε e^{-B} δ^M_5                   ... (5.3)

where ε = +1 at y = y₂ (outward = +y) and ε = −1 at y = y₁ (outward = −y).

The extrinsic curvature tensor:

    K_μν = ½ (£_n G)_μν = ε A' e^{2A−B} g_μν                     ... (5.4)

The trace:

    K = h^μν K_μν = 4ε A' e^{-B}                                  ... (5.5)

**Explicit GHY contribution:**

    S_GHY = 2 ∑_i ∫ d⁴x √(−g) · e^{4A_i} · (M₅³ − ξφ_i²) · 4A'_i e^{-B_i}

         = 8 ∑_i ∫ d⁴x √(−g) (M₅³ − ξφ_i²) A'_i e^{4A_i − B_i}  ... (5.6)

where A_i ≡ A(y_i), B_i ≡ B(y_i), φ_i ≡ φ(y_i), and the ε² = 1 factors have been absorbed (the relative signs between UV and IR branes are tracked by the sign of A'_i).

**Note:** The boundary terms from integrating A'' by parts in (4.8) combine with (5.6). Specifically, the −8[F e^{4A−B} A']_{y₁}^{y₂} term from the bulk exactly cancels the GHY contribution when the variational principle is imposed — this is precisely why the GHY term is required.

### 5.3 Total Boundary Action

    S_bdy = S_brane + S_GHY

    S_bdy = ∑_i ∫ d⁴x √(−g) e^{4A_i} [
        −σ_i − α_i φ_i² − L_i
        + 8(M₅³ − ξφ_i²) A'_i e^{-B_i - 4A_i} · e^{4A_i}
    ]

More cleanly:

    S_bdy = ∑_i ∫ d⁴x √(−h_i) [
        −σ_i − α_i φ_i² − L_i
    ] + S_GHY                                                      ... (5.7)

---

## 6. The Sequestering Sector — S_seq (Task 1.5)

Following Kaloper & Padilla (PRL 112, 091304, 2014), adapted to 5D warped geometry.

### 6.1 The Mechanism

The cosmological constant problem: quantum loop corrections generate vacuum energy ~ M⁴_Pl. In standard gravity, this gravitates. Sequestering promotes Λ₅ to a global (non-propagating) variable constrained to absorb all vacuum energy contributions.

### 6.2 The 5D Adapted Constraints

Promote Λ₅ to a global variable λ. Add constraint terms:

    ┌──────────────────────────────────────────────────────────────────────┐
    │  S_seq = λ [ σ(μ) − ∫ d⁵x √(−G) ]                               │  ... (6.1)
    │        + κ [ τ(μ) − ∫ d⁵x √(−G) (M₅³ − ξφ²) R₅ ]               │  ... (6.2)
    └──────────────────────────────────────────────────────────────────────┘

where:
- λ, κ are Lagrange multipliers (global, non-dynamical)
- σ(μ), τ(μ) are functions of a mass scale μ (specified by the UV theory)
- The constraints enforce that the spacetime volume and the gravitational integral are fixed by UV-determined quantities

**Effect on field equations:** Varying w.r.t. λ and κ yields global constraints. Varying the metric yields the standard Einstein equations with Λ₅ replaced by λ — but now λ is determined by a global condition that is insensitive to local vacuum energy shifts.

**Key result (Kaloper-Padilla):** All vacuum energy loop corrections are absorbed into λ. The effective 4D cosmological constant receives only a residual contribution suppressed by the ratio V₄/V₅ (spacetime volume ratios), which for infinite spacetime volume → 0.

### 6.3 Modified Bulk Action with Sequestering

When sequestering is active, the bulk action (4.1) is understood with Λ₅ → λ:

    S_bulk^seq = ∫ d⁵x √(−G) [ (M₅³ − ξφ²) R₅ + P(X,φ) − V(φ) − λ ]

and the full variation includes (6.1)–(6.2) as additional constraints.

**Full development** of the 5D sequestering equations, including the modified junction conditions and verification that vacuum energy decoupling survives the warped geometry, is **Task 1.5**.

**Note on local vacuum modification:** Sequestering absorbs vacuum energy globally. The reverse question — can one LOCALLY modify the effective vacuum energy (and hence the local gravitational coupling) through EM field manipulation — is raised by the EPS data. If the KK gauge field A_μ couples to the sequestering constraint through the gravitational integral, driving A_μ could locally shift the effective λ. See `external_data_eps.md` §3.2.

---

## 7. The NCG Action — S_NCG (Phase 5)

The noncommutative geometry sector handles the Standard Model gauge structure through a finite spectral triple (A_F, H_F, D_F, J_F, γ_F).

    ┌──────────────────────────────────────────────────────────────────────┐
    │  S_NCG = Tr(f(D_F / Λ_NCG)) + ⟨Jψ, D_A ψ⟩                       │  ... (7.1)
    └──────────────────────────────────────────────────────────────────────┘

**Bosonic sector:** Tr(f(D_F/Λ)) — the spectral action principle (Chamseddine-Connes). Heat kernel expansion produces: Yang-Mills action for SU(3)×SU(2)×U(1), Higgs kinetic and quartic terms, gravitational terms (Einstein-Hilbert + Weyl²), and cosmological constant contribution.

**Fermionic sector:** ⟨Jψ, D_A ψ⟩ — fermionic action with D_A the Dirac operator twisted by gauge connection A. Produces: fermion kinetic terms, gauge couplings, Yukawa couplings, and neutrino mixing.

**Coupling to 5D geometry:** The spectral triple lives on the total space M₄ × I × F. The NCG action couples to the continuous geometry through the Dirac operator on M₄ × I, which sees the warp factor. The integration over y produces the effective 4D NCG action with warp-factor-weighted couplings.

**Full expansion deferred to Phase 5** (Tasks 5A, 5B, 5C, 5D). At this stage, S_NCG enters as an opaque functional whose 4D reduction will be matched against SM parameters.

**Note on topological terms:** The spectral action contains topological contributions (Chern-Simons, Euler characteristic, Pontryagin) that are invisible to perturbation theory but can modify the gravitational coupling non-perturbatively. If the EM field on the brane has a topologically nontrivial configuration (nonzero Chern number), additional gravitational terms arise. This connects to the Berry phase / topological invariant structure identified in the EPS antigravity curriculum. See `external_data_eps.md` §3.4.

---

## 8. The Complete Action — Assembled

    ┌──────────────────────────────────────────────────────────────────────┐
    │                                                                      │
    │  S = S_bulk + S_bdy + S_seq + S_NCG                                 │
    │                                                                      │
    │  S_bulk = ∫ d⁵x √(−G) [(M₅³ − ξφ²)R₅ + P(X,φ) − V(φ) − Λ₅]     │
    │                                                                      │
    │  S_bdy = −∑_i ∫ d⁴x √(−h_i) [σ_i + α_i φ_i²]                    │
    │        + 2∑_i ε_i ∫ d⁴x √(−h_i) (M₅³ − ξφ_i²) K_i               │
    │        + S_matter[h_i, Ψ]                                           │
    │                                                                      │
    │  S_seq = λ[σ(μ) − ∫ d⁵x √(−G)]                                    │
    │        + κ[τ(μ) − ∫ d⁵x √(−G)(M₅³ − ξφ²)R₅]                     │
    │                                                                      │
    │  S_NCG = Tr(f(D_F/Λ_NCG)) + ⟨Jψ, D_A ψ⟩                          │
    │                                                                      │
    └──────────────────────────────────────────────────────────────────────┘

with:
    G_MN given by (2.2)
    √(−G) = e^{4A+B} √(−g)                                         [eq. 2.4b]
    R₅ = e^{-2A} R₄ − e^{-2B}[8A'' + 20(A')² − 8A'B']            [eq. 3.3]
    X = ½ e^{-2A} g^μν ∂_μφ ∂_νφ + ½ e^{-2B} (φ')²               [eq. 4.3]
    h_μν = e^{2A(y_i)} g_μν                                         [induced]
    K_i = 4ε_i A'(y_i) e^{-B(y_i)}                                 [eq. 5.5]

### 8.1 Free Parameters at This Stage

| Parameter | Type | Role | Constrained by |
|-----------|------|------|---------------|
| M₅ | Mass scale | 5D Planck mass | M_Pl via warp integral (Phase 2) |
| ξ | Dimensionless | Non-minimal coupling | Self-tuning + hierarchy (Tasks 1.2, 1.4) |
| P(X,φ) | Functional | Kinetic structure | Singularity-free self-tuning (Task 1.2) |
| V(φ) | Functional | Bulk potential | Stability + self-tuning (Task 1.4) |
| Λ₅ | Energy density | Bare 5D CC | Sequestering (Task 1.5) |
| A(y), B(y) | Profiles | Warp factors | Field equations (Task 1.3) |
| σ_i | Energy density | Brane tensions | Junction conditions (Task 1.3) |
| α_i | Dimensionless | Brane scalar coupling | Boundary conditions on φ |
| Topology of I | Discrete | Global structure | Classification (Task 1.6) |

### 8.2 Parameter Count

Continuous parameters: M₅, ξ, Λ₅, σ_i, α_i (2+2 for interval = 7 total)
Functional freedoms: P(X,φ), V(φ), A(y), B(y), φ(y) — constrained by field equations + self-tuning
Discrete choice: topology of I (3 candidates)

The field equations (Task 1.3) will reduce the functional freedoms. The self-tuning condition (Task 1.4) will further constrain P and V. The reverse-engineering from data (Track 2) will fix the continuous parameters.

---

## 9. Preview: Field Equations (Task 1.3)

For completeness, we state the abstract form of the equations that follow from varying the action. Full derivation in warped coordinates is Task 1.3.

### 9.1 5D Einstein Equations

Varying S w.r.t. G^MN (suppressing sequestering terms):

    (M₅³ − ξφ²) G^(5D)_MN + ξ(G_MN □₅ − ∇_M ∇_N)(φ²)
        = P_X ∂_M φ ∂_N φ − G_MN [P − V − Λ₅]
        − ∑_i δ(y − y_i)/√(G_55) · e^{2A} [σ_i + α_i φ² ] h_MN   ... (9.1)

where G^(5D)_MN = R^(5D)_MN − ½ G_MN R₅ is the 5D Einstein tensor, and h_MN = G_MN − n_M n_N is the projector onto the brane.

The ξ-coupling generates second-derivative terms □₅(φ²) and ∇_M ∇_N(φ²):

    □₅(φ²) = 2φ □₅φ + 2 ∂_M φ ∂^M φ = 2φ □₅φ + 4X               ... (9.2)
    ∇_M ∇_N(φ²) = 2φ ∇_M ∇_N φ + 2 ∂_M φ ∂_N φ                  ... (9.3)

### 9.2 Scalar Field Equation

Varying S w.r.t. φ:

    ∇_M(P_X ∇^M φ) − P_φ + V'(φ) + 2ξφR₅
        + ∑_i δ(y − y_i)/√(G_55) · 2(α_i − ξK_i)φ_i = 0          ... (9.4)

where V'(φ) = dV/dφ.

### 9.3 Junction Conditions (Israel)

At each brane y = y_i, the warp factors have discontinuities in their first derivatives. The Israel junction conditions relate the jump in extrinsic curvature to the brane energy-momentum:

    [K_μν − h_μν K]_i = −1/(2(M₅³ − ξφ_i²)) (σ_i + α_i φ_i²) h_μν   ... (9.5)

where [·]_i denotes the jump across the brane.

For our metric, this becomes conditions on [A']_i and [φ']_i at each brane location.

---

## 10. Status and Next Steps

### Completed
- [x] General warped ansatz with A(y), B(y) both dynamical (Task 1.1 partial)
- [x] Full 5D geometric decomposition: Christoffel, Ricci tensor, Ricci scalar
- [x] Bulk action in explicit warped coordinates
- [x] Boundary action with GHY terms for non-minimal coupling
- [x] Sequestering structure (Kaloper-Padilla adapted)
- [x] NCG action noted (Phase 5 placeholder)
- [x] Complete action assembled
- [x] Field equations in abstract form

### Next: Task 1.2
Determine which P(X,φ) is forced by singularity-free self-tuning in warped space, following Lacombe & Mukohyama (PRD 2022). This constrains the kinetic sector from "general" to "specific."

### Next: Task 1.3
Derive the explicit component equations by substituting the warped ansatz into (9.1)–(9.4). This gives coupled ODEs for A(y), B(y), φ(y) with specified boundary conditions.

---

*Working document. Updated as derivations proceed.*
*Phase 1, Step 1 — D1.1: Complete action, coordinate-explicit.*
