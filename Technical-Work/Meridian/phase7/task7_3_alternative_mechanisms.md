# D7.3 — Alternative Mechanisms for Phantom Crossing

**Deliverable:** Systematic analysis of mechanisms beyond braiding parameterization
**Status:** COMPLETE
**Date:** 2026-03-15

---

## 1. Motivation

The Phase 7 solver (meridian_extended.py, 16 multi-start optimization) definitively showed:
- Power-law braiding Ω_braid = λ₀/E^{2α_b} does NOT produce negative wₐ
- All 30 parameter scan points give wₐ > 0 (more positive than minimal model)
- Optimizer kills both drift (γ_r → 0.017) and braiding (λ₀ → 0), collapsing to ΛCDM + ζ₀
- The surviving improvement (Δχ² = -14.93) comes entirely from H&K non-minimal coupling

This document develops three alternative mechanisms that may produce phantom crossing within the Meridian framework, plus identifies additional approaches.

---

## 2. Mechanism A: Dark Energy–Dark Matter Interaction (Coupled Cuscuton)

### 2.1 Physical Basis

In the 5D Meridian geometry, the scalar field φ (radion) propagates in the BULK. Matter fields can be:
- **Brane-localized** (SM fermions, gauge bosons) — couple to φ only through the induced metric
- **Bulk-propagating** (KK modes, possible DM candidates from Phase 7/8 of the plan) — couple DIRECTLY to φ through the bulk metric

This geometric distinction automatically creates a **differential coupling**: bulk dark matter couples more strongly to the radion than brane-localized SM matter.

### 2.2 Formalism

The interaction Lagrangian for bulk dark matter:

    L_int = β_c(y) ρ_DM φ / M_Pl

where β_c(y) depends on the dark matter's profile in the extra dimension. The conservation equations become:

    ∇_μ T^μν_DM = +Q u^ν      (DM gains/loses energy)
    ∇_μ T^μν_DE = -Q u^ν      (DE loses/gains energy)

with Q = β_c ρ_DM Ḣ / H (interaction rate proportional to Hubble evolution).

In the background cosmology:

    ρ̇_DM + 3Hρ_DM = +Q
    ρ̇_DE + 3H(1 + w_DE)ρ_DE = -Q

The EFFECTIVE equation of state observed by distance measurements is:

    w_eff = w_DE - Q / (3Hρ_DE)

### 2.3 Phantom Crossing Mechanism

If Q > 0 (energy flows from DE to DM — "decaying dark energy"):
- w_eff > w_DE → makes dark energy look MORE quintessence-like
- Does NOT help with phantom crossing

If Q < 0 (energy flows from DM to DE — "growing dark energy"):
- w_eff < w_DE → can push w_eff below -1 even if w_DE > -1
- At early times: ρ_DM is large, |Q| is large, w_eff is significantly phantom
- At late times: ρ_DM has diluted, |Q| decreases, w_eff → w_DE > -1
- This produces **phantom crossing from below** — w rises through -1

**Critical distinction:** The DESI pattern is w < -1 at low z, w > -1 at high z. The coupled cuscuton with Q < 0 gives the OPPOSITE: w < -1 at high z (when ρ_DM is large), w > -1 at low z. This is the WRONG direction.

### 2.4 Can We Get the Right Direction?

For the DESI pattern, we need the interaction to be STRONGER at late times than early times. This requires:

    Q = -β_c ρ_DM f(a)

where f(a) grows with a. In the Meridian context, f(a) could arise from:
- The radion profile evolving (ψ(N) changing with expansion)
- The extra dimension's warp factor evolving (A(y,t) time-dependent)
- The cuscuton constraint modifying as the scalar field drifts

The simplest possibility: if φ̇ = const (cuscuton) but the coupling β_c depends on φ itself:

    β_c(φ) = β_0 exp(α φ / M_Pl)

Then as φ grows linearly (φ = φ₀ + μ²t), the coupling strengthens exponentially at late times. This IS consistent with the cuscuton constraint and could produce the right crossing direction.

### 2.5 Assessment

**Strengths:**
- The differential coupling is GEOMETRIC — emerges automatically from bulk vs. brane localization
- Coupled quintessence is well-studied (Amendola 2000, Wetterich 1995, Pettorino & Baccigalupi 2008)
- Could explain DESI signal without modifying scalar Lagrangian
- Compatible with H&K constraint (ζ₀ unchanged)
- Dark matter as KK modes (Phase 8 of v4 plan) provides the coupling partner naturally

**Weaknesses:**
- The naive coupling gives the WRONG direction for phantom crossing (2.3 above)
- Getting the RIGHT direction requires φ-dependent coupling β_c(φ), adding a free function
- Tight constraints from CMB (ISW effect, DM dilution) and structure formation (σ₈)
- If DM is NOT bulk-propagating (e.g., brane-localized WIMPs), the mechanism doesn't work
- Need to verify cuscuton constraint survives the interaction term

**Viability: MODERATE.** The geometric motivation is genuine, but the direction problem (2.3) is a significant obstacle. Only works if the coupling β_c(φ) has the right φ-dependence, which must be derived from the 5D geometry, not assumed.

**Key question to resolve:** Does the 5D KK reduction with a bulk DM field produce a coupling β_c(φ) that grows at late times?

---

## 3. Mechanism B: Projected Weyl Tensor (Dark Radiation from the Bulk)

### 3.1 Physical Basis

The SMS (Shiromizu-Maeda-Sasaki) projection of the 5D Einstein equations onto the brane gives:

    G_μν = -Λ₄ g_μν + κ₄² T_μν + κ₅⁴ π_μν - E_μν

where E_μν = C^A_{μBν} n_A n^B is the projection of the 5D Weyl tensor.

**In Phases 1-6, we assumed E_μν = 0.** This is valid for a static, empty bulk (Randall-Sundrum). But the Meridian model has:
- A non-trivial bulk scalar field φ(y,t)
- A time-evolving radion (γ_r > 0 means the extra dimension drifts)
- A cuscuton profile that sources bulk geometry

These generically produce E_μν ≠ 0.

### 3.2 Decomposition

In cosmological backgrounds:

    E_μν = -6/κ₅⁴ [E (u_μ u_ν + g_μν/3) + P_μν + Q_(μ u_ν)]

where:
- **E** = dark energy density (scalar part, "dark radiation")
- **P_μν** = anisotropic stress (traceless, transverse)
- **Q_μ** = energy flux (vanishes by symmetry in FLRW)

The modified Friedmann equation becomes:

    E²(a) = Ω_m a⁻³ + Ω_r a⁻⁴ + Ω_DE(a) + Ω_Weyl(a)

### 3.3 Standard Dark Radiation

If the bulk is conformally flat (empty), E_μν evolves as:

    E = E₀ a⁻⁴    (radiation-like, from Bianchi identity on brane)

This adds "dark radiation" constrained by BBN: ΔN_eff < 0.5 → Ω_Weyl < 10⁻⁵. Far too small to affect late-time cosmology.

### 3.4 Non-Standard Evolution from Cuscuton Bulk

The key insight: with a non-trivial bulk scalar, E_μν does NOT necessarily scale as a⁻⁴.

The 5D bulk equations with the cuscuton field are:

    G^(5)_{AB} = κ₅² [∂_A φ ∂_B φ · P,X / √(2X) - G_{AB}(P(X) + V(φ))]

The cuscuton constraint P,X = μ² / √(2X) → φ̇ = μ² (on the brane) means the bulk profile evolves linearly in time. The 5D Weyl tensor sourced by this evolving profile has components:

    C^y_{μνy} ∝ ∂_y²A(y,t) · [corrections from φ(y,t)]

When projected onto the brane, this gives E_μν with a time dependence set by the BULK dynamics, not the simple a⁻⁴ scaling.

### 3.5 Could This Produce Phantom Crossing?

For E_μν to produce phantom crossing, Ω_Weyl(a) must:
1. Be negative at late times (w_Weyl < -1 requires Ω_Weyl to GROW)
2. Transition sign or growth rate at z ~ 0.5

**The problem:** E_μν enters the Friedmann equation through E, which is the projected Weyl scalar. In RS-type models, E ≥ 0 always (it represents the tidal stretching by the bulk). Negative E would require an exotic bulk geometry.

**However:** What matters for phantom crossing isn't the sign of E, but its EVOLUTION. If E evolves as:

    Ω_Weyl(a) = Ω_W0 · a^{-4+n}

with n > 0 (slower decay than radiation due to bulk scalar sourcing), then at late times Ω_Weyl is larger than expected, effectively reducing the rate at which dark energy density dilutes, mimicking phantom behavior.

More precisely, the total effective dark energy:

    ρ_eff = ρ_DE + ρ_Weyl

If ρ_Weyl grows (or decays slower than ρ_DE), the effective w_eff of the sum can cross -1.

### 3.6 Assessment

**Strengths:**
- E_μν ≠ 0 is the GENERIC case; E_μν = 0 is a special assumption we made for simplicity
- No new fields or parameters — uses existing 5D geometry
- Entirely geometric mechanism
- Well-studied in braneworld cosmology (Maartens 2004, Langlois 2001)
- The cuscuton bulk profile SPECIFICALLY makes E_μν time-dependent in a non-trivial way

**Weaknesses:**
- Computing E_μν requires solving the FULL 5D Einstein + scalar equations, not just the brane projection. This is a much harder problem (PDEs in y and t)
- BBN constraints on dark radiation are tight — if Ω_Weyl scales anything like a⁻⁴, it's tiny at late times
- Even with non-standard scaling, the effect may be too small to produce Δw ~ 0.2
- The SMS projection becomes unreliable when bulk dynamics are strong (need numerical 5D evolution)
- Risk of losing the simplicity that makes the model tractable

**Viability: MODERATE-HIGH.** The physics is compelling and the mechanism is already present in the equations. The question is magnitude. A first step would be to compute E_μν for the STATIC cuscuton bulk (no radion drift) and verify it's small, then estimate the correction when drift is turned on.

**Key question to resolve:** What is E_μν for the Meridian-specific 5D solution (cuscuton on S¹/Z₂ with warp factor e^{2A(y)})?

---

## 4. Mechanism C: Perturbation Backreaction

### 4.1 Physical Basis

Non-linear structure formation creates an inhomogeneous universe. The spatial average of an inhomogeneous expansion differs from the expansion of the spatially-averaged universe (Buchert 2000, 2001):

    ⟨θ²⟩ ≠ ⟨θ⟩²

This "backreaction" enters the averaged Friedmann equation:

    3(ȧ_D/a_D)² = 8πG⟨ρ⟩ - ½⟨R⟩_D - ½Q_D

where Q_D = ⅔(⟨θ²⟩ - ⟨θ⟩²) - 2⟨σ²⟩ is the kinematic backreaction.

### 4.2 Magnitude in GR

In standard GR, backreaction is perturbatively small:

    Q_D / H² ~ (δρ/ρ)² ~ 10⁻⁵ at recombination, ~ 10⁻² at z = 0

This is insufficient to explain dark energy acceleration (Green & Wald 2011, 2014 provided a rigorous perturbative proof). The Buchert backreaction advocates (Wiltshire 2007, Räsänen 2004) argue non-perturbative effects could be larger, but this remains controversial.

### 4.3 Enhancement in Modified Gravity

In the Meridian model, μ(a) = F₀/F(a) ≠ 1 modifies the growth of perturbations. The backreaction is:

    Q_D^{Meridian} = Q_D^{GR} × [1 + 2ζ₀(μ - 1)/μ + O(ζ₀²)]

At the best-fit point (ζ₀ = 0.038, μ ≈ 1.001), the enhancement is:

    Q_D^{Meridian} / Q_D^{GR} ≈ 1 + 2(0.038)(0.001) ≈ 1.00008

This is a 0.008% enhancement — completely negligible.

### 4.4 Could It Be Larger?

For backreaction to matter, we'd need either:
- Much larger ζ₀ (but constrained by H&K to < 0.1)
- Much larger μ deviation (but constrained by growth data)
- Non-perturbative effects (voids, walls) amplified by modified gravity

The last option is plausible in PRINCIPLE — modified gravity N-body simulations (f(R), DGP) do show enhanced backreaction. But the enhancement is typically a factor of 2-5, bringing Q_D from 10⁻² to 10⁻¹·⁵ at best. Still ~1% of H² — insufficient for Δw ~ 0.2.

### 4.5 Assessment

**Strengths:**
- Real physical effect, not speculative
- No new parameters
- Modified gravity does enhance backreaction
- Could explain small corrections to w(z)

**Weaknesses:**
- Quantitatively tiny. Even with generous estimates, |ΔW| < 0.01 — two orders of magnitude too small
- At the best-fit Meridian parameters, enhancement over GR is negligible (0.008%)
- Would require N-body simulations to compute properly
- Controversial even in GR context
- Green & Wald arguments apply with minor modifications to cuscuton gravity

**Viability: LOW.** Include for completeness but this cannot be the primary resolution. Backreaction might contribute a ~1% correction to w at late times, but not the Δw ~ 0.2 needed for DESI.

---

## 5. Additional Mechanisms Identified

### 5.A. Double-Counting Verification (Methodological, Not Physical)

The solver uses five χ² components:
- BAO distances (from DESI)
- fσ₈ growth (from various surveys)
- H₀ (from CMB angular distance)
- H&K (from luminosity-size relation)
- w₀wₐ prior (from CMB+SN, "excluding BAO")

**The concern:** The w₀wₐ prior claims to exclude BAO. But if derived from a DESI-era combined analysis (CMB+SN+BAO), removing BAO from the posterior is not the same as never including it. The prior might be contaminated by BAO information, creating double-counting.

**The test:** Run the solver WITHOUT the w₀wₐ prior. If the best-fit changes significantly, double-counting was affecting results.

**Impact:** If the model fits BAO distances well (χ² = 2.26 ≈ ΛCDM's 2.27) and fits H₀ and H&K, but "fails" only the w₀wₐ prior, and that prior is double-counted — then there may be no tension at all.

**Viability: HIGH priority, easy to test.** This is the single most important methodological check before pursuing any physical mechanism.

### 5.B. Scale-Dependent Effective w(z)

The CPL parameterization assumes w is a function of redshift only: w = w₀ + wₐ(1-a). But in modified gravity, different probes measure effective dark energy at different scales:
- CMB: superhorizon and recombination-epoch
- BAO: ~150 Mpc comoving
- SN: lightcone-integrated
- Growth: linear perturbation scale

The Meridian model's c_s = ∞ means scalar perturbations are infinitely stiff — they don't cluster on ANY scale. But the modified growth factor μ(a,k) is k-independent (QSA exact at all k). So scale-dependence in effective w is unlikely to be large.

**Viability: LOW.** Not promising for the Meridian model specifically, though worth noting for completeness.

### 5.C. Early Dark Energy from Modified K(H)

In the minimal cuscuton, K_eff = κ₀/E². At early times (E >> 1), K_eff → 0 — no early dark energy.

But the extended cuscuton allows K_eff ≠ κ₀/E². If K_eff(H) decays SLOWER than 1/H², there is residual kinetic energy at early times. This acts as Early Dark Energy (EDE), shifting the sound horizon r_s at recombination.

A smaller r_s increases all BAO distances (D_V/r_d, D_M/r_d, D_H/r_d), changing the χ² landscape. EDE models are known to alleviate the H₀ tension by shifting r_s downward by ~5%.

**In the Meridian context:** The ITK extended cuscuton provides K(H) freedom. If the spectral action selects a K(H) that decays as 1/H^{2-δ} with small δ > 0, we get EDE automatically. The amount of EDE is controlled by δ and κ₀ — both constrained by the spectral action.

**Viability: MODERATE.** This is implicitly part of the full ITK space exploration but hasn't been explicitly examined. A targeted analysis of EDE from extended K(H) would be valuable.

### 5.D. Chern-Simons Cosmological Effects

From D5.3: The spectral action produces gravitational Chern-Simons (CS) terms on the branes:

    S_CS = θ_grav ∫ CS₃(Γ)

In parity-violating gravity (Chern-Simons gravity, Alexander & Yunes 2009), the CS term modifies the gravitational wave sector but does NOT affect the background Friedmann equation (because FLRW is parity-even). However:
- CS gravity introduces **gravitational birefringence** (left- vs right-handed GW travel differently)
- At one-loop, CS parity violation can generate a TRACE anomaly, which DOES modify the background
- The anomaly acts as an additional dark energy component: ρ_CS ~ T⁴ (θ/M_Pl)²

**Viability: LOW.** The one-loop effect is suppressed by (H/M_Pl)² ~ 10⁻¹²⁰. Not relevant for cosmological phantom crossing. CS effects are interesting for GW observations but not for background dark energy.

---

## 6. Mechanism D: Matter-Sector Modification (ζ₀ as Phantom Mimicry)

### 6.1 Physical Basis

The non-minimal coupling ζ₀ modifies the effective gravitational constant:

    G_eff(a) = G_N / F(a),    F(a) = 1 - ζ₀(ψ²(a) - 1)

where ψ(a) is the radion field normalized to ψ(a=1) = 1. This changes how matter sources expansion:

    H²(a) = [8πG_eff(a)/3] ρ_tot(a)

Observers who assume GR (G_eff = const) interpret the distance-redshift relation d_L(z) as evidence for dark energy with equation of state w(z). But in modified gravity, the SAME d_L(z) corresponds to a DIFFERENT w(z) than in GR.

### 6.2 The Effective Equation of State

The luminosity distance depends on H(z):

    d_L(z) = (1+z) ∫₀ᶻ dz'/H(z')

In GR, H²(z) = H₀²[Ω_m(1+z)³ + Ω_DE exp(3∫₀ᶻ (1+w(z'))/z' dz')]. But in Meridian:

    H²(z) = H₀² [Ω_m(1+z)³/F(z) + Ω_DE(z)]

The 1/F(z) factor modifies the MATTER contribution. An observer assuming GR would attribute this to dark energy evolution. The "apparent" w(z) seen by a GR-assuming analysis is:

    w_apparent(z) = w_true(z) + δw(z)

where δw(z) depends on F'(z)/F(z) — the rate of change of the effective gravitational constant.

### 6.3 Can This Produce Apparent Phantom Crossing?

For F(a) = 1 - ζ₀(ψ² - 1), we need F(a) to change with time:

    dF/da = -ζ₀ · 2ψ · dψ/da

In the minimal cuscuton, ψ evolves as dψ/dN = β/E² where β ∝ γ_r. At the best-fit point (γ_r → 0.017), the drift is negligible — F is nearly constant.

**But what if the extended cuscuton allows faster radion evolution at intermediate redshift?** The ITK freedom in K(H) could permit ψ(a) trajectories where F changes rapidly near z ~ 0.5. A GR-assuming observer would see this as phantom crossing in w(z).

### 6.4 Quantitative Estimate

For apparent phantom crossing at z ~ 0.5, we need δw(z=0.5) ~ -0.2 to shift w from -0.8 to -1.0, then δw(z=0) ~ 0 to restore w ~ -0.8 today.

    δw ≈ -(2/3) · F'/[(1-F) · (1+z)]

With ζ₀ = 0.038 and β ~ 0.4:

    |δw| ≈ (2/3) · 2ζ₀β/E² ≈ (2/3) · 2(0.038)(0.4)/1.4² ≈ 0.01

This is an order of magnitude too small. The ζ₀ modification to F(a) produces percent-level changes in w, not the ~20% needed.

### 6.5 Enhancement Possibilities

To get |δw| ~ 0.2 from matter-sector modification alone:
- ζ₀ ~ 0.4 (10x larger — excluded by H&K at > 5σ)
- β ~ 4.0 (10x larger radion drift — gives w₀ far from -1)
- Rapid transient in ψ(a) near z ~ 0.5 (possible in extended cuscuton but requires specific K(H))

The third option connects to the ITK freedom: if K(H) has a feature near H(z=0.5), the radion could undergo a rapid transition, producing a transient in F(a). This is a specific K(H) shape that would need spectral action motivation.

### 6.6 Assessment

**Strengths:**
- Uses existing physics (ζ₀) without new fields or couplings
- The mechanism is well-understood in modified gravity literature (Kunz & Sapone 2007, Amendola et al. 2008)
- Could explain why DESI sees phantom crossing even if w_true ~ -1
- Doesn't require actual w < -1

**Weaknesses:**
- Quantitatively too small at current best-fit parameters (δw ~ 0.01 vs needed 0.2)
- Enhancement requires ζ₀ or γ_r far from best-fit values, creating tension elsewhere
- Relies on a specific K(H) transient feature — needs spectral action motivation
- The effect on BAO distances is degenerate with dark energy modification

**Viability: LOW-MODERATE.** The mechanism is sound but quantitatively insufficient at current parameters. Could become relevant if combined with other effects or if the extended K(H) permits a transient radion feature.

---

## 7. Mechanism E: Multi-Field Dynamics (Radion + Moduli)

### 7.1 Physical Basis

The Kaluza-Klein reduction of 5D gravity on S¹/Z₂ generically produces not just the radion (breathing mode of the extra dimension) but also:
- **Shape moduli** — if the extra dimension has non-trivial geometry beyond the warp factor
- **Brane moduli** — if brane positions can fluctuate independently
- **Wilson line scalars** — from components of higher-dimensional gauge fields along the extra dimension

In the Meridian geometry, the relevant fields from KK reduction are:
- **Radion T(x):** The size of the extra dimension. This is our φ.
- **Brane bending mode σ(x):** Perturbation of the IR brane position. In RS1 stabilization, this is the field that Goldberger-Wise stabilizes. In the cuscuton model, the cuscuton constraint REPLACES Goldberger-Wise, but the mode still exists — it's constrained, not absent.

### 7.2 Multi-Field Phantom Crossing

Multi-field dark energy models naturally produce phantom crossing (Cai & Saridakis 2009, Chiba et al. 2009). The mechanism:

Consider two fields φ₁ (radion) and φ₂ (modulus):

    ρ_DE = K₁(φ̇₁) + K₂(φ̇₂) + V(φ₁, φ₂)
    p_DE = K₁(φ̇₁) + K₂(φ̇₂) - V(φ₁, φ₂)

    w = (K₁ + K₂ - V) / (K₁ + K₂ + V)

If φ₁ dominates at high z (quintessence, K₁ > 0, w > -1) and φ₂ dominates at low z (phantom, K₂ < 0, w < -1), w crosses -1 at the transition redshift.

**The cuscuton twist:** The cuscuton constraint eliminates kinetic energy for φ₁ (the radion): K₁ = 0 effectively (zero kinetic energy theorem, D6.3). So:

    w = (K₂ - V) / (K₂ + V)

If K₂ is small, w ≈ -1 always (cosmological constant behavior from V alone). For w to deviate significantly from -1, the modulus φ₂ must contribute non-negligible kinetic energy.

### 7.3 Is There a Second Scalar in Meridian?

In the minimal RS1 setup with cuscuton stabilization, the relevant scalars are:

1. **Radion φ** — cuscuton-constrained. K_eff ~ 1/H². This is the field we've been studying.
2. **Brane bending σ** — in standard RS1, this is the radion itself. But with the cuscuton constraint, the brane bending might be partially decoupled.
3. **If the NCG internal space F contributes scalar modes** — the Higgs from inner fluctuations of D_F could mix with the radion.

The most natural candidate is the **NCG Higgs**. D5.6 assessed phi-Higgs identification. If the identification FAILS, we have TWO independent scalars: the radion (φ) and the NCG Higgs (H). Their mixing is constrained but non-zero.

### 7.4 Assessment

**Strengths:**
- Multi-field phantom crossing is a well-established mechanism
- KK reductions generically produce moduli — their absence would require explanation
- The NCG Higgs is already in the architecture (it's part of the spectral triple)
- Doesn't require exotic Lagrangians beyond what's already present
- The zero kinetic energy theorem for the radion DOESN'T apply to other scalars

**Weaknesses:**
- Significantly increases complexity — the single-field analysis (Phases 1-7) would need extension
- Need to identify the second scalar concretely and compute its potential and kinetic structure
- The Higgs mass (~125 GeV) suggests it's frozen at cosmological scales (m >> H₀)
- If all moduli are heavy (m >> H₀), they don't contribute to late-time cosmology
- The cuscuton constraint might propagate to other sectors, constraining all scalars jointly

**Viability: MODERATE.** Theoretically well-motivated and already partially present in the architecture (NCG Higgs). The key question is whether any scalar besides the radion is light enough to be cosmologically active. If all extra scalars have m >> H₀ ~ 10⁻³³ eV, this doesn't work. A concrete calculation of the moduli spectrum is needed.

**Key question:** What is the mass spectrum of KK scalars in the Meridian geometry? Specifically, is any mode light enough (m ≲ H₀) to contribute to late-time dark energy?

---

## 8. Mechanism F: Running Couplings / RG Flow

### 8.1 Physical Basis

The spectral action Tr(f(D²/Λ²)) gives the classical action at the cutoff scale Λ ~ 10¹⁷ GeV. The couplings that appear (Newton's constant, cosmological constant, Gauss-Bonnet coefficient, Yang-Mills coupling, Higgs parameters) are all evaluated AT this scale.

Cosmological observations probe scales E ~ H₀ ~ 10⁻³³ eV, some 50 orders of magnitude below Λ. The renormalization group (RG) flow between these scales can significantly modify the couplings.

### 8.2 What Runs in Meridian

The relevant running quantities:

1. **G₄(φ) = M_Pl²/2 + ξφ²** — The non-minimal coupling runs:
   - β_ξ = (ξ - 1/6)(6λ + 6y_t² - ...) / (4π)² in the SM (one-loop)
   - At cosmological scales, ξ(μ_cosmo) ≠ ξ(Λ)
   - This changes ζ₀ at low energies

2. **The cuscuton coefficient μ²** — If μ runs:
   - K_eff = μ²(H)/H² instead of μ₀²/H²
   - μ(H) could increase at low H (IR enhancement), making K_eff larger than 1/H²
   - This is EXACTLY the kind of K(H) modification that could help

3. **The braiding couplings G₂, G₃** — If the spectral action selects specific G₂(φ,X) and G₃(φ,X) at Λ, their running to cosmological scales produces different G₂(φ,X; μ) and G₃(φ,X; μ).

### 8.3 The Key Mechanism: Running μ²

If the cuscuton mass parameter runs as:

    μ²(H) = μ₀² (1 + c₁ ln(H/H₀) + c₂ ln²(H/H₀) + ...)

Then K_eff = μ²(H)/H² gets logarithmic corrections:

    K_eff = (μ₀²/H²)(1 + c₁ ln(H/H₀) + ...)

At z = 0 (H = H₀): K_eff = μ₀²/H₀²
At z = 0.5 (H ≈ 1.4H₀): K_eff = μ₀²/(1.4H₀)²(1 + 0.34c₁)
At z = 2 (H ≈ 3H₀): K_eff = μ₀²/(3H₀)²(1 + 1.1c₁)

For c₁ > 0 (positive running — μ increases at higher H), K_eff decays SLOWER than 1/H², meaning MORE kinetic dark energy at higher z. This tilts w(z) toward quintessence at high z more strongly, potentially producing a steeper transition to phantom at low z.

For c₁ < 0 (negative running), K_eff decays FASTER, potentially producing a PEAKED K(H) — exactly the shape identified in D7.3 Section 1 as needed for the right braiding behavior.

### 8.4 Computing the Running

The RG flow of the cuscuton sector is not well-studied. Standard results exist for:
- Scalar-tensor theories (G₄ running): Codello et al. 2015, Ohta et al. 2016
- Horndeski gravity (general): Saltas & Vitagliano 2017
- The cuscuton specifically: no published RG computation exists

The spectral action framework provides a natural starting point: the Seeley-DeWitt expansion IS a short-distance expansion, and the higher a_n coefficients encode the running. The a₆ and higher coefficients (not yet computed for our geometry) would give the beta functions.

### 8.5 Assessment

**Strengths:**
- Physically correct: RG flow between Λ ~ 10¹⁷ GeV and H₀ ~ 10⁻³³ eV is real
- The spectral action framework naturally contains the RG structure
- Running μ² could produce exactly the K(H) modification needed
- No new fields or couplings — just proper treatment of existing ones
- The effect emerges from the theory rather than being imposed

**Weaknesses:**
- Technically very difficult. The Horndeski RG is poorly understood.
- No existing literature on cuscuton RG specifically
- 50 orders of magnitude of running — need to trust perturbative RG over a huge range
- Non-perturbative effects might dominate over perturbative running
- Could easily become a multi-month side project with uncertain outcome
- The sign of c₁ (and whether it helps) is unknown a priori

**Viability: MODERATE.** Physically the most principled approach — it's asking "what does the theory ACTUALLY predict at cosmological scales?" But technically the hardest. A first step would be to estimate c₁ from dimensional analysis and known scalar-tensor beta functions, without attempting a full cuscuton RG calculation.

**Key question:** What is the sign and magnitude of the one-loop beta function for the cuscuton mass parameter μ²?

---

## 9. Mechanism G: Topological Channel (EPS Mechanism)

### 9.1 Physical Basis

From D5.3: The APS (Atiyah-Patodi-Singer) index theorem applied to the Meridian spectral action produces gravitational and gauge Chern-Simons terms on the branes:

    S_brane ⊃ θ_grav ∫ tr(Γ∧dΓ + ⅔Γ∧Γ∧Γ) + θ_gauge ∫ tr(A∧dA + ⅔A∧A∧A)

These terms are TOPOLOGICAL — they don't affect the background cosmology directly (FLRW is parity-even, and CS terms require parity violation).

However, the EPS (Electrogravitic Phase Structure) mechanism from D5.3 proposes that **topological transitions** — changes in the topological sector — can have physical consequences:

### 9.2 Domain Walls as Topological Transitions

In 5D, a domain wall interpolating between regions with different θ_grav is a physical object. If such domain walls form cosmologically (e.g., during the electroweak phase transition, or during radion stabilization), they produce:

1. **Localized energy density** — the wall tension contributes to ρ_DE
2. **Topological charge** — the Chern-Simons number changes across the wall
3. **Gravitational coupling modification** — the effective G changes across the wall

### 9.3 Could Domain Walls Produce Phantom Crossing?

A network of domain walls has equation of state w = -⅔ (for static walls). As the network evolves:
- At high z: walls are diluted by expansion, subdominant
- At intermediate z: walls might form during a phase transition, contributing energy
- At low z: walls dominate or annihilate

If the radion drift (φ evolving) triggers a phase transition at z ~ 0.5 (where the cuscuton field reaches a critical value), domain walls could form, producing a TRANSIENT energy injection that mimics phantom crossing.

### 9.4 The Phase Transition Scenario

The Meridian model has a natural phase transition: the electroweak symmetry breaking on the IR brane. In standard RS1, this happens at T_EW ~ 100 GeV (z ~ 10¹⁵). But if the radion is slowly drifting (even at γ_r ~ 0.017), the warp factor evolves:

    e^{A(y_c, t)} = e^{A₀(y_c)} · (1 + γ_r · H₀ · t + ...)

This could trigger a LATE-TIME phase transition if the slowly changing warp factor crosses a critical value. The associated domain walls/solitons would inject energy at the transition redshift.

### 9.5 Assessment

**Strengths:**
- Uses physics already present in the spectral action (CS terms, D5.3)
- Non-perturbative — could produce effects that no smooth parameterization captures
- The EPS mechanism was identified as the ONLY viable EM-gravity channel
- Domain walls from topological transitions are well-studied (Vilenkin & Shellard)
- A phase transition at z ~ 0.5 triggered by radion drift is physically plausible

**Weaknesses:**
- Highly speculative. No concrete calculation connects CS terms to background cosmology.
- Domain wall networks have w = -⅔, not w < -1. Need a more complex scenario for phantom crossing.
- The late-time phase transition requires fine-tuning of the warp factor evolution
- Computing the domain wall energy density requires full 5D field theory
- No existing literature on cuscuton + domain wall cosmology

**Viability: LOW-MODERATE.** This is the most creative and least developed mechanism. It could produce dramatic effects (phase transitions are discontinuous), but the theoretical distance from the current framework to a concrete prediction is large. Worth keeping in the idea space but not the next calculation to do.

**Key question:** Does the slowly evolving warp factor cross any critical values in the NCG spectral action that would trigger a topological transition at cosmological redshifts?

---

## 10. Summary and Priority Ranking

| # | Mechanism | Viability | Cost | Key Test |
|---|-----------|-----------|------|----------|
| 1 | **5.A. Double-counting check** | HIGH | LOW | Remove w₀wₐ prior, re-run solver |
| 2 | **B. Projected Weyl tensor** | MOD-HIGH | HIGH | Compute E_μν for static cuscuton bulk |
| 3 | **A. Coupled cuscuton (DE-DM)** | MOD | MOD | Derive β_c(φ) from KK reduction |
| 4 | **E. Multi-field (radion + moduli)** | MOD | HIGH | Compute moduli mass spectrum |
| 5 | **F. Running couplings / RG flow** | MOD | V. HIGH | Estimate β_μ² from dimensional analysis |
| 6 | **5.C. EDE from extended K(H)** | MOD | LOW | K_eff = κ₀/E^{2-δ}, scan δ |
| 7 | **D. Matter-sector (ζ₀ mimicry)** | LOW-MOD | LOW | Compute δw from F(a) variation |
| 8 | **G. Topological channel (EPS)** | LOW-MOD | V. HIGH | Warp factor critical value analysis |
| 9 | **C. Backreaction** | LOW | HIGH | Estimate enhancement factor |
| 10 | **5.B. Scale-dependent w** | LOW | LOW | Check k-dependence |
| 11 | **5.D. Chern-Simons** | LOW | LOW | Estimate anomaly magnitude |

---

## 11. Recommended Next Steps

1. **Immediate (today):** Run solver without w₀wₐ prior (5.A). Code modification, not physics. If the tension disappears, everything changes.

2. **Short-term (this week):** Compute E_μν for the Meridian-specific bulk solution (B). Static case first, then drift as perturbation.

3. **Short-term:** Estimate the running of μ² from dimensional analysis and known scalar-tensor beta functions (F). Even a rough sign determination is informative.

4. **Medium-term:** Derive β_c(φ) from KK reduction for each DM candidate (A). Direction test is critical.

5. **Medium-term:** Compute moduli mass spectrum (E). If any scalar has m ≲ H₀, multi-field phantom crossing is viable.

6. **Medium-term:** EDE scan (5.C). Modify solver, scan δ. Quick test.

7. **Medium-term:** Matter-sector δw estimate (D). Quick analytic check — if δw ~ 0.01, this mechanism is too small alone but could contribute in combination.

8. **Deferred:** Topological channel (G), backreaction (C), scale-dependent w (5.B), Chern-Simons (5.D). Note in plan but don't pursue actively unless other tracks close.

---

*D7.3 — Clayton & Clawd, March 15, 2026*
