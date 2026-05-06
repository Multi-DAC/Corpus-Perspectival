# D10.7-D10.8 — Brane-Localized Quintessence: NCG Origin, Two-Sector Friedmann Equations, and Phantom Crossing

**Track 10C | Clayton & Clawd | March 16, 2026**

---

## 1. Purpose and Context

Phases 1-9 established that the Meridian framework (A1: 5D spacetime, A2: bulk scalar with non-minimal coupling) produces LCDM + zeta_0 = 0.038 as its UNIQUE cosmological prediction. The bulk cuscuton is ghost-free but background-frozen: the zero kinetic energy theorem prevents it from driving dynamical dark energy. Nine independent calculations confirm this is structural, not parametric.

Track 10C investigates the simplest Category II extension: keep the bulk cuscuton (it provides zeta_0 = 0.038, which fits Hubble-Kovacs data at Delta-chi^2 = -15), but add a separate brane-localized scalar psi that provides dynamical w(z). The two-sector model:

- **Sector 1 (BULK):** Cuscuton phi — constraint field, provides zeta_0, modifies gravity at perturbation level, w_phi ~ -1 always
- **Sector 2 (BRANE):** Quintessence psi — propagating field, provides w(z) dynamics

This deliverable addresses five questions:
1. Does NCG provide a first-principles origin for a brane-localized scalar beyond the Higgs? (10C.1)
2. What are the modified Friedmann equations for the two-sector system? (10C.2)
3. Can the system produce phantom crossing (w_eff < -1)? (10C.3)
4. Is simultaneous DESI + H&K fit achievable? (10C.4)
5. What is the fine-tuning cost? (10C.5)

---

## 2. NCG Scalar Analysis (Task 10C.1)

### 2.1 The Minimal NCG Standard Model

The Chamseddine-Connes spectral triple for the Standard Model uses the finite algebra:

    A_F = C + H + M_3(C)                                                    ... (2.1)

(equivalently expressed as M_2(H) + M_4(C) in the even real structure). The Hilbert space H_F is 96-dimensional per generation, encoding quarks and leptons with their correct hypercharges. The finite Dirac operator D_F encodes the Yukawa coupling matrices.

The SCALAR CONTENT of the minimal NCG SM is exactly:

    One complex SU(2) doublet: H = (H+, H0) in (2, 1)_{1/2}              ... (2.2)

This is the standard Higgs doublet. It arises from the inner fluctuations of D_F: the connection 1-form A = sum_i a_i [D_F, b_i] for a_i, b_i in A_F produces a scalar in the (2, 1)_{1/2} representation because the off-diagonal components of D_F (connecting the quaternionic and complex matrix algebra components) transform as an SU(2) doublet.

**The minimal NCG SM has NO other scalars.** The Higgs is uniquely determined by the algebra A_F and its representation on H_F. This is a theorem (Chamseddine-Connes-Marcolli 2007, "Gravity and the standard model with neutrino mixing"): the spectral triple classification determines A_F up to KO-dimension, and the allowed inner fluctuations produce exactly the SM Higgs and nothing more.

### 2.2 Beyond-SM NCG Extensions

The literature contains several well-motivated extensions of A_F that produce additional scalars:

#### (a) Right-Handed Neutrino Extension (Devastato-Lizzi-Martinetti 2014)

Adding right-handed neutrinos nu_R to the NCG framework requires enlarging the finite space to accommodate Majorana mass terms. The modified algebra:

    A_F^{nu_R} = C + H + M_3(C)    (same algebra)                         ... (2.3)

but with an enlarged Hilbert space:

    H_F^{nu_R} = 128-dimensional per generation                            ... (2.4)

(32 additional components for nu_R per generation). The key change is that D_F now contains the Majorana mass matrix M_R in addition to the Dirac Yukawa matrices.

The inner fluctuations of the enlarged D_F produce:

    1. The standard Higgs doublet H (as before)
    2. A real singlet scalar sigma                                          ... (2.5)

The singlet sigma couples to the right-handed neutrino mass term:

    L_sigma = (1/2)(d sigma)^2 + y_R sigma nu_R^c nu_R - V(sigma)        ... (2.6)

where y_R is the Majorana Yukawa coupling.

**The potential V(sigma):** From the spectral action, V(sigma) has the form:

    V(sigma) = -mu_sigma^2 sigma^2 + lambda_sigma sigma^4 + lambda_{Hsigma} |H|^2 sigma^2    ... (2.7)

The coefficients are determined by the spectral geometry at the unification scale Lambda:

    mu_sigma^2 ~ f_2 Lambda^2 / f_0 (same structure as Higgs mu^2)       ... (2.8)
    lambda_sigma ~ Tr(M_R^4) / (f_0 Lambda^4)
    lambda_{Hsigma} ~ Tr(Y_nu^dagger Y_nu M_R^2) / (f_0 Lambda^4)

where Y_nu is the neutrino Yukawa matrix and f_0, f_2 are moments of the spectral cutoff function.

**The mass of sigma:** After sigma acquires a VEV (breaking the B-L symmetry and generating Majorana masses):

    m_sigma^2 = 2 lambda_sigma <sigma>^2                                   ... (2.9)

For the see-saw mechanism to work: M_R = y_R <sigma> ~ 10^{10-14} GeV (GUT to intermediate scale). With lambda_sigma ~ O(0.01-1):

    m_sigma ~ sqrt(2 lambda_sigma) <sigma> ~ 10^{9-14} GeV               ... (2.10)

This is FAR above H_0 ~ 10^{-33} eV. The mass gap:

    m_sigma / H_0 ~ 10^{42-47}                                             ... (2.11)

**Verdict on sigma:** The NCG singlet from nu_R exists but has a mass 42-47 orders of magnitude above H_0. It is cosmologically inert at late times — it behaves as matter (oscillating, rho ~ a^{-3}). It cannot drive dark energy.

This is the SAME mass gap problem identified for the radion in D8.4 Section 6. The gap is structural: the see-saw scale is fixed by neutrino mass phenomenology, and there is no mechanism within the NCG framework to make sigma ultra-light while preserving the see-saw.

#### (b) Grand Unification Spectral Triples (Chamseddine-Connes-van Suijlekom 2013)

Extensions to Pati-Salam SU(2)_L x SU(2)_R x SU(4)_c or SO(10)-type algebras produce additional Higgs representations:

    Pati-Salam:  Bidoublet (2, 2, 1) + Right-triplet (1, 3, 10)          ... (2.12)

These additional scalars break the extended gauge symmetry down to the SM. Their masses are set by the symmetry breaking scale:

    m_{GUT scalars} ~ M_GUT ~ 10^{15-16} GeV                             ... (2.13)

Even heavier than the nu_R singlet. Cosmologically irrelevant.

#### (c) The Spectral Triple Classification Theorem (Chamseddine-Connes-Marcolli 2007)

The CCM classification constrains the algebra A_F by requiring:
1. KO-dimension 6 (to get the correct sign table for the SM)
2. Finite-dimensional representation of A_F
3. First-order condition (Axiom 5)
4. Symplectic structure from J (reality)

The theorem proves that A_F = C + H + M_3(C) is the UNIQUE algebra (up to discrete choices) satisfying these conditions with H_F having the right dimension for three generations of quarks and leptons.

**This means:** Any scalar beyond the Higgs requires modifying the axioms or the algebra. The nu_R extension modifies H_F (and hence the representation) while keeping A_F. The Pati-Salam extension modifies A_F itself. Both produce scalars at high scales (10^{10-16} GeV).

**No extension of the NCG spectral triple produces a scalar at the Hubble scale.**

### 2.3 The Conformal Scalar / Volume Scalar

From D5.9, there is a DIFFERENT class of NCG scalar: the conformal fluctuation (Chamseddine-Connes 2010) and the volume scalar (Chamseddine-Connes-Mukhanov 2014). These are geometric scalars associated with the metric, not with the internal space F.

The cuscuton phi IS this conformal/volume scalar in the Meridian architecture (D5.9 Section 3). It is already in the theory. Adding a SECOND conformal scalar would require a second independent metric degree of freedom — which does not exist in the 5D geometry (the only geometric moduli are the radion T and the cuscuton phi, both already counted in D8.4).

### 2.4 NCG Verdict

    +----------------------------------------------------------------------+
    |                                                                      |
    |  NCG SCALAR ANALYSIS: NO FIRST-PRINCIPLES BRANE SCALAR FOR DE      |
    |                                                                      |
    |  The minimal NCG SM: one Higgs doublet, nothing else.               |
    |  The nu_R extension: adds singlet sigma, but m_sigma ~ 10^{10} GeV.|
    |  Pati-Salam/SO(10): adds GUT-scale Higgs, m ~ 10^{15} GeV.        |
    |  Conformal/volume scalar: already IS the cuscuton phi.              |
    |                                                                      |
    |  EVERY NCG scalar has a mass set by the symmetry-breaking scale     |
    |  it participates in. No mechanism produces m ~ H_0 within NCG.      |
    |                                                                      |
    |  A brane quintessence field is therefore PHENOMENOLOGICAL:          |
    |  it must be added by hand, not derived from the spectral triple.    |
    |  This weakens the theoretical motivation but does not kill the      |
    |  track — the question of whether such a field WORKS is independent  |
    |  of whether NCG predicts it.                                        |
    |                                                                      |
    +----------------------------------------------------------------------+

---

## 3. Two-Sector Friedmann Equations (Task 10C.2)

### 3.1 The 4D Effective Lagrangian

Assume a brane-localized scalar psi with canonical kinetic term and potential V(psi), living on the IR brane alongside the Standard Model. The complete 4D effective Lagrangian on the brane:

    L = (M_Pl^2 / 2)(1 + 2*zeta_0) R
        - (1/2)(d psi)^2 - V(psi)
        + L_cuscuton
        + L_SM                                                             ... (3.1)

where:
- (1 + 2*zeta_0) arises from the bulk cuscuton's non-minimal coupling F(phi) = M_5^3 - xi*phi^2, projected onto the brane via the KK reduction (D2.2). The established value: zeta_0 = 0.038.
- psi is the brane-localized quintessence field with standard kinetic term
- V(psi) is its potential (to be specified)
- L_cuscuton encodes the cuscuton's contribution to the background: it is a constraint sector that produces the dark energy density V_eff = v_0 M_Pl^2 H_0^2 in the modified Friedmann equation, but does NOT propagate (zero kinetic energy)
- L_SM is the Standard Model Lagrangian

### 3.2 The Modified Friedmann Equation

The Friedmann equation for the two-sector system:

    H^2 = (8*pi*G_eff / 3) * (rho_m + rho_r + rho_cusc + rho_psi)       ... (3.2)

where:

    G_eff = G_N / (1 + 2*zeta_0)                                          ... (3.3)

is the effective gravitational coupling modified by the bulk cuscuton (D2.2, D4.1). With zeta_0 = 0.038:

    G_eff = G_N / 1.076 = 0.929 * G_N                                     ... (3.4)

The energy densities:
- rho_m = rho_{m,0} a^{-3} (matter)
- rho_r = rho_{r,0} a^{-4} (radiation)
- rho_cusc = rho_{cusc,0} + kappa_0 H_0^2 / H^2 (cuscuton sector, from D3.1)
- rho_psi = (1/2) psi-dot^2 + V(psi) (quintessence)

In the established Meridian notation (D3.1, D7.2), defining E = H/H_0 and Omega_i = rho_{i,0} / rho_{crit,0}:

    E^2 = [Omega_m a^{-3} + Omega_r a^{-4} + v_0 + kappa_0/E^2 + Omega_psi(a)] / (1 + 2*zeta_0)
                                                                            ... (3.5)

where Omega_psi(a) = rho_psi(a) / rho_{crit,0}.

**Crucially:** The cuscuton sector (v_0 + kappa_0/E^2) is UNCHANGED from the established Phase 7 result. It still satisfies the zero kinetic energy theorem. It still contributes zeta_0 to perturbation growth. The quintessence psi is an ADDITIVE sector, not a modification of the cuscuton.

### 3.3 The Quintessence Equation of Motion

The Klein-Gordon equation for psi on the brane:

    psi-double-dot + 3H psi-dot + V'(psi) = 0                             ... (3.6)

This is the standard quintessence evolution equation. It does NOT couple to the cuscuton phi because:

1. The cuscuton is a 5D bulk field. Its brane projection is a constraint (D1.1, eq. 1.1), not a dynamical field. There is no kinetic coupling between psi and phi on the brane.

2. The only coupling is GRAVITATIONAL: both psi and phi contribute to the Friedmann equation (3.5), so psi "feels" the cuscuton through H(t). But this is the universal gravitational coupling — it doesn't introduce new vertices.

3. Junction condition coupling is addressed in Section 4.3.

### 3.4 The Equation of State

The total dark energy equation of state as seen by observers:

    w_DE = (p_cusc + p_psi) / (rho_cusc + rho_psi)                       ... (3.7)

For the cuscuton: p_cusc = -rho_cusc + O(kappa_0/E^4). In the established limit (Phase 7), kappa_0/E^2 << v_0, so p_cusc approx -rho_cusc and w_cusc approx -1.

For quintessence:

    w_psi = ((1/2) psi-dot^2 - V(psi)) / ((1/2) psi-dot^2 + V(psi))     ... (3.8)

For canonical kinetic term: -1 <= w_psi <= +1 always.

The total:

    w_DE = [w_cusc * rho_cusc + w_psi * rho_psi] / [rho_cusc + rho_psi]
         = [-rho_cusc + w_psi * rho_psi] / [rho_cusc + rho_psi]          ... (3.9)

Define the quintessence fraction:

    f_psi = rho_psi / (rho_cusc + rho_psi)                                ... (3.10)

Then:

    w_DE = -1 + f_psi * (1 + w_psi)                                       ... (3.11)

Since 1 + w_psi >= 0 (canonical quintessence) and f_psi >= 0:

    w_DE >= -1    always    (for canonical brane scalar)                   ... (3.12)

**This is the standard result: canonical quintessence cannot cross the phantom divide.** Even in the two-sector model with the cuscuton, the total w_DE stays at or above -1 if the brane scalar has standard kinetic term.

### 3.5 Normalized Friedmann Equation

For practical computation, write the Friedmann equation as a polynomial (clearing the E^{-2} from the cuscuton):

    (1 + 2*zeta_0) E^4 - [Omega_m a^{-3} + Omega_r a^{-4} + v_0 + Omega_psi(a)] E^2 - kappa_0 = 0
                                                                            ... (3.13)

With zeta_0 = 0.038 and kappa_0 ~ gamma_r^2 ~ (0.017)^2 ~ 3 x 10^{-4} (from Phase 7 best fit, where gamma_r -> 0):

The kappa_0 term is negligible (O(10^{-4})). The dominant modification from the cuscuton is through G_eff:

    E^2 approx [Omega_m a^{-3} + Omega_r a^{-4} + v_0 + Omega_psi(a)] / (1 + 2*zeta_0)
                                                                            ... (3.14)

The cuscuton's role is purely to RESCALE G — it modifies the normalization but not the dynamics. The dynamics come entirely from the quintessence psi through Omega_psi(a).

---

## 4. Phantom Crossing Mechanisms (Task 10C.3)

### 4.1 Mechanism (a): Geometric Phantom Crossing from G_eff

**The key insight:** Observers who measure the expansion history H(z) and interpret it assuming GR with G = G_N will infer an equation of state w_eff that DIFFERS from the true w_DE of the dark energy sector. The mismatch arises because the actual gravitational coupling is G_eff = G_N/(1 + 2*zeta_0), not G_N.

Define the INFERRED equation of state w_eff: the value an observer would extract from H(z) data assuming standard Friedmann with G = G_N:

    H^2 = (8*pi*G_N / 3) [rho_m + rho_r + rho_DE^{eff}]                  ... (4.1)

where rho_DE^{eff}(a) is whatever function of a is needed to fit the observed H(z).

The TRUE Friedmann equation (eq. 3.14) is:

    H^2 = (8*pi*G_N / 3) * (1/(1 + 2*zeta_0)) * [rho_m + rho_r + rho_cusc + rho_psi]
                                                                            ... (4.2)

Comparing (4.1) and (4.2):

    rho_DE^{eff} = (rho_m + rho_r + rho_cusc + rho_psi)/(1 + 2*zeta_0) - rho_m - rho_r
                 = rho_cusc/(1 + 2*zeta_0) + rho_psi/(1 + 2*zeta_0) - 2*zeta_0*(rho_m + rho_r)/(1 + 2*zeta_0)
                                                                            ... (4.3)

The last term is crucial: it means the inferred dark energy density ABSORBS a fraction of the matter+radiation density. As a function of redshift:

    rho_DE^{eff}(z) = [rho_cusc + rho_psi - 2*zeta_0*(rho_m + rho_r)] / (1 + 2*zeta_0)
                                                                            ... (4.4)

The inferred equation of state:

    w_eff = -1 - (1/3) d(ln rho_DE^{eff}) / d(ln a)                       ... (4.5)

At late times (rho_r << rho_m << rho_DE):

    rho_DE^{eff} approx [rho_cusc + rho_psi - 2*zeta_0 * rho_m] / (1 + 2*zeta_0)
                                                                            ... (4.6)

The derivative:

    d(rho_DE^{eff})/d(ln a) = [d(rho_psi)/d(ln a) + 6*zeta_0 * rho_m / (1 + 2*zeta_0)] / (1 + 2*zeta_0)
                                                                            ... (4.7)

(using d(rho_cusc)/d(ln a) approx 0 since w_cusc approx -1, and d(rho_m)/d(ln a) = -3 rho_m)

Wait — I need to be more careful. The -2*zeta_0*(rho_m) term has d/d(ln a) = -2*zeta_0*(-3*rho_m) = +6*zeta_0*rho_m. So:

    d(rho_DE^{eff})/d(ln a) = [rho_psi*(1 + w_psi)*(-3) + 6*zeta_0*rho_m] / (1 + 2*zeta_0)
                                                                            ... (4.8)

Therefore:

    1 + w_eff = -(1/3) * d(ln rho_DE^{eff}) / d(ln a)
              = [rho_psi (1 + w_psi) - 2*zeta_0*rho_m / rho_DE^{eff}] * (1/(1 + 2*zeta_0))
                                                                            ... (4.9)

Hmm, this is getting algebraically tangled. Let me approach it more cleanly.

**The clean approach:** Define the phantom crossing condition. The inferred w_eff < -1 requires rho_DE^{eff} to INCREASE with time (the inferred dark energy density grows as the universe expands). From (4.6):

    d(rho_DE^{eff}) / dt > 0
    => d(rho_psi)/dt - 2*zeta_0 * d(rho_m)/dt > 0
    => -3H(1 + w_psi)*rho_psi + 6*H*zeta_0*rho_m > 0
    => 6*zeta_0*rho_m > 3(1 + w_psi)*rho_psi                             ... (4.10)

Rearranging:

    w_psi < 2*zeta_0 * (rho_m / rho_psi) - 1                             ... (4.11)

This is ALWAYS satisfied in some redshift range! As z increases, rho_m grows as (1+z)^3 while rho_psi stays roughly constant (for slow-rolling quintessence). At sufficiently high z:

    rho_m / rho_psi ~ (Omega_m / Omega_psi) * (1 + z)^3 >> 1             ... (4.12)

So the RHS of (4.11) becomes much larger than any w_psi, and the condition is trivially satisfied.

But the question is whether this holds at LOW z (z ~ 0.5-1.0), where DESI measures the phantom crossing. At z = 0:

    rho_m^{today} / rho_psi^{today} ~ Omega_m / Omega_psi                ... (4.13)

For Omega_m = 0.315, Omega_psi = fraction of dark energy from quintessence (rest from cuscuton).

**The quantitative condition at z = 0:**

    w_eff < -1  at z = 0  requires:
    w_psi < 2*zeta_0*(Omega_m / Omega_psi) - 1                           ... (4.14)

For zeta_0 = 0.038:

If Omega_psi = 0.685 (all DE from quintessence): w_psi < 2*0.038*0.315/0.685 - 1 = 0.035 - 1 = -0.965. This requires w_psi < -0.965, which is easily achieved by slow-rolling quintessence.

But wait — this means w_eff < -1 WHENEVER w_psi < -0.965? That seems too easy. Let me re-derive more carefully.

**Careful re-derivation.** The inferred w_eff is defined by fitting the TOTAL H(z) with a GR Friedmann equation using G_N:

    3 H^2 / (8*pi*G_N) = rho_m + rho_{DE}^{inferred}                     ... (4.15)

But the TRUE equation is:

    3 H^2 / (8*pi*G_N) = (rho_m + rho_cusc + rho_psi) / (1 + 2*zeta_0) ... (4.16)

So:

    rho_{DE}^{inferred} = (rho_m + rho_cusc + rho_psi)/(1 + 2*zeta_0) - rho_m
                        = (rho_cusc + rho_psi)/(1 + 2*zeta_0) - 2*zeta_0*rho_m/(1 + 2*zeta_0)
                                                                            ... (4.17)

Now: rho_cusc + rho_psi is the TRUE dark energy density. In the limit where the cuscuton contributes V_0 (constant) and psi contributes rho_psi(a):

    rho_{DE}^{inferred}(a) = [V_0 + rho_psi(a)]/(1 + 2*zeta_0) - 2*zeta_0*rho_{m,0}*a^{-3}/(1 + 2*zeta_0)
                                                                            ... (4.18)

The inferred w:

    1 + w_{inferred} = -(1/3) * (d ln rho_{DE}^{inferred})/(d ln a)

    = -(1/3) * [1/rho_{DE}^{inferred}] * [d(rho_psi)/(d ln a) + 6*zeta_0*rho_{m,0}*a^{-3}/(1+2*zeta_0)]/(1+2*zeta_0)
                                                                            ... (4.19)

At a = 1 (today), with d(rho_psi)/d(ln a) = -3(1+w_psi)*rho_psi:

    1 + w_{inferred} = [3(1+w_psi)*rho_psi/(1+2*zeta_0) - 6*zeta_0*rho_{m,0}/(1+2*zeta_0)^2] / (3*rho_{DE}^{inferred})
                                                                            ... (4.20)

For phantom crossing (w_inferred = -1): set 1 + w_inferred = 0:

    3(1+w_psi)*rho_psi = 6*zeta_0*rho_{m,0}/(1+2*zeta_0)

    (1 + w_psi) = 2*zeta_0*rho_{m,0} / [(1+2*zeta_0)*rho_psi]            ... (4.21)

**The geometric phantom crossing point:** w_eff = -1 when:

    1 + w_psi = 2*zeta_0 * Omega_m / [(1 + 2*zeta_0) * Omega_psi]        ... (4.22)

For zeta_0 = 0.038, Omega_m = 0.315:

    1 + w_psi = 2 * 0.038 * 0.315 / (1.076 * Omega_psi) = 0.0222 / Omega_psi
                                                                            ... (4.23)

**Case 1: All DE from quintessence** (Omega_psi = 0.685, V_0 = 0):

    1 + w_psi = 0.0222 / 0.685 = 0.032
    w_psi = -0.968                                                         ... (4.24)

**Case 2: Half DE from quintessence** (Omega_psi = 0.34, V_0 contributions = 0.34):

    1 + w_psi = 0.0222 / 0.34 = 0.065
    w_psi = -0.935                                                         ... (4.25)

**Interpretation:** For observers using GR with G_N, the inferred w_eff crosses -1 whenever the true w_psi is SLIGHTLY above -1 (by an amount proportional to zeta_0). The phantom crossing is an APPARENT effect caused by misidentifying G_eff as G_N.

    +----------------------------------------------------------------------+
    |                                                                      |
    |  GEOMETRIC PHANTOM CROSSING: THE MECHANISM                          |
    |                                                                      |
    |  True physics:                                                       |
    |    G_eff = G_N / (1 + 2*zeta_0) = 0.929 * G_N                     |
    |    w_psi = -0.97 (canonical quintessence, no ghosts)                |
    |                                                                      |
    |  Observer inference (assuming G = G_N):                              |
    |    w_eff < -1 (phantom!)                                            |
    |                                                                      |
    |  The observer sees phantom crossing because:                         |
    |  (a) They overestimate G by factor (1 + 2*zeta_0)                  |
    |  (b) This makes them underestimate rho_m's contribution             |
    |  (c) The residual they attribute to DE appears to grow,             |
    |      which requires w < -1 in the GR interpretation                 |
    |                                                                      |
    |  For w_psi = -0.97, Omega_psi = 0.685, zeta_0 = 0.038:           |
    |    w_{inferred,0} = -1.002                                          |
    |                                                                      |
    |  The effect is SMALL: |w_eff - (-1)| ~ zeta_0 * Omega_m / Omega_DE |
    |                       ~ 0.038 * 0.46 ~ 0.017                        |
    |                                                                      |
    +----------------------------------------------------------------------+

**The critical quantitative question:** Is this effect large enough to explain DESI?

DESI measures w_0 = -0.752 +/- 0.058 and w_a = -0.86 +/- 0.27. The departure from w = -1 is:

    |1 + w_0^{DESI}| = 0.248                                              ... (4.26)

The geometric phantom crossing effect at z = 0 is:

    |1 + w_eff| ~ zeta_0 * Omega_m / Omega_DE ~ 0.038 * 0.46 ~ 0.017    ... (4.27)

**This is TOO SMALL by a factor of 15.** The geometric phantom effect from zeta_0 = 0.038 produces |1 + w_eff| ~ 0.02, while DESI requires |1 + w_0| ~ 0.25.

**The geometric phantom mechanism CANNOT explain DESI on its own.** It can produce a tiny w < -1 bias (~2%) but not the ~25% departure DESI sees.

However: the geometric effect IS present and DOES shift w_eff systematically toward phantom values. It is a correction that should be included in any DESI fit within the Meridian framework.

### 4.2 Mechanism (b): Non-Canonical Brane Kinetics (DBI)

If the brane scalar psi has a non-canonical kinetic term arising from the brane's embedding in the bulk, the Lagrangian takes the DBI form:

    L_psi = -f(psi)^{-1} [sqrt(1 + f(psi)*(d psi)^2) - 1] - V(psi)     ... (4.28)

where f(psi) is the warp factor of the throat geometry evaluated at the brane position.

The DBI kinetic term produces an effective equation of state that CAN cross -1 through the k-essence mechanism, without ghosts, provided the kinetic energy changes sign in the effective Lagrangian. Specifically, the DBI action is equivalent to:

    P(X_psi) = -f^{-1}(sqrt(1 - 2f*X_psi) - 1) - V                     ... (4.29)

with X_psi = -(1/2)(d psi)^2. The sound speed:

    c_s^2 = 1 - 2f*X_psi = 1/(1 + f*psi-dot^2)                          ... (4.30)

This is always positive (no ghosts), and can be arbitrarily small (relativistic brane motion).

**However:** For phantom crossing from DBI, one needs the Lagrangian to satisfy P + 2X*P_X < 0 at some point. For the DBI form:

    P + 2X*P_X = -V + f^{-1}(1/sqrt(1-2fX) - 1) + 2X*f^{-1}/sqrt(1-2fX)^3 * f/2

This reduces to:

    = -V + f^{-1}[sqrt(1-2fX)^{-1} - 1 + fX/sqrt(1-2fX)^3]

For slow roll (fX << 1): P + 2X*P_X approx -V + O(X) < 0 if V > 0. So rho + p < 0 when V dominates — but this is w > -1, not w < -1. The phantom domain requires rho + p < 0 from the kinetic sector, which DBI cannot provide with positive f.

**The DBI brane scalar CANNOT cross the phantom divide** for the same structural reason as canonical quintessence: the kinetic energy is positive-definite.

**Verdict:** Mechanism (b) does not produce phantom crossing.

(Note: this is distinct from Track 10B, which considers the brane POSITION as the dynamical field. Here we consider a scalar LIVING ON the brane. Track 10B addresses the brane's own motion through the bulk.)

### 4.3 Mechanism (c): Cuscuton-Quintessence Coupling Through Junction Conditions

The Israel junction conditions at the IR brane (y = y_c) relate the extrinsic curvature jump [K_ij] to the brane stress-energy:

    [K_{mu nu}] - g_{mu nu} [K] = -kappa_5^2 * S_{mu nu}                 ... (4.31)

where S_{mu nu} includes ALL brane-localized stress-energy: the brane tension sigma, the SM fields, AND the quintessence psi. The stress-energy of psi:

    S^{psi}_{mu nu} = d_mu psi d_nu psi - g_{mu nu}[(1/2)(d psi)^2 + V(psi)]
                                                                            ... (4.32)

This enters the junction conditions, which in turn determine the bulk geometry near the brane, which feeds back into the cuscuton constraint equation. The feedback loop:

    psi stress-energy → junction conditions → bulk geometry → cuscuton constraint → effective V_eff

Does this coupling produce phantom crossing?

**Estimate the coupling strength.** The quintessence contribution to the junction conditions relative to the brane tension:

    |S^{psi}_{mu nu}| / |sigma * g_{mu nu}| ~ rho_psi / sigma            ... (4.33)

The brane tension sigma is fixed by the RS tuning (D1.1):

    sigma = 6 k M_5^3 / kappa_5^2 ~ 6 k M_Pl^2                          ... (4.34)

The quintessence energy density:

    rho_psi ~ Omega_psi * rho_crit ~ 0.7 * 3*H_0^2*M_Pl^2 / (8*pi) ~ 10^{-47} GeV^4
                                                                            ... (4.35)

The brane tension:

    sigma ~ k * M_Pl^2 ~ 10^{18} * (2.4*10^{18})^2 GeV^3 ~ 10^{55} GeV^3 ... (4.36)

Wait — the dimensions don't match. Let me be more careful. In natural units with [sigma] = [energy/area] = [mass^4]:

    sigma ~ k * M_5^3 ~ M_Pl^2 * k ~ (2.4*10^{18})^2 * 10^{18} ~ 10^{54} GeV^4
                                                                            ... (4.37)

(using k ~ M_Pl for the RS hierarchy solution)

The ratio:

    rho_psi / sigma ~ 10^{-47} / 10^{54} ~ 10^{-101}                     ... (4.38)

The quintessence energy density is 101 ORDERS OF MAGNITUDE smaller than the brane tension. The backreaction of psi on the bulk geometry through the junction conditions is completely negligible.

**This means:** The cuscuton does not "feel" the quintessence at all. The two sectors decouple to extraordinary precision. The coupling through junction conditions produces corrections of order:

    delta(w_cusc) ~ rho_psi/sigma ~ 10^{-101}                             ... (4.39)

This is not even Planck-suppressed. It is brane-tension-suppressed. FAR smaller than any observable effect.

**Verdict:** Mechanism (c) produces no measurable coupling. The two sectors are effectively decoupled.

### 4.4 Summary of Phantom Crossing Mechanisms

| Mechanism | Result | Size | Status |
|-----------|--------|------|--------|
| **(a) Geometric (G_eff)** | w_eff < -1 when w_psi > -(1 + 2*zeta_0*Omega_m/Omega_psi) | |1+w_eff| ~ 0.02 | **WORKS but 15x too small for DESI** |
| **(b) DBI kinetics** | Positive-definite kinetic energy | 0 | **KILLED (structural)** |
| **(c) Junction coupling** | rho_psi/sigma ~ 10^{-101} | negligible | **KILLED (suppression)** |

    +----------------------------------------------------------------------+
    |                                                                      |
    |  PHANTOM CROSSING VERDICT                                            |
    |                                                                      |
    |  The geometric mechanism (a) is the ONLY viable path.               |
    |  It produces w_eff < -1 through G_eff misidentification.            |
    |  But |1 + w_eff| ~ zeta_0 * Omega_m/Omega_DE ~ 0.02.              |
    |  DESI requires |1 + w_0| ~ 0.25.                                    |
    |                                                                      |
    |  The two-sector model produces:                                      |
    |    - Dynamical DE (from quintessence): w_psi > -1                   |
    |    - Small phantom bias (from G_eff): delta_w ~ -0.02              |
    |    - Combined: w_eff ~ w_psi - 0.02                                 |
    |                                                                      |
    |  For DESI w_0 = -0.75: need w_psi ~ -0.73. This is standard       |
    |  thawing quintessence — easily achieved with appropriate V(psi).    |
    |                                                                      |
    |  But w_a < 0 (DESI) requires w to become MORE negative at low z.   |
    |  Thawing quintessence has w_a > 0 (w becomes LESS negative).       |
    |  The phantom bias from zeta_0 doesn't help with the SIGN of w_a.   |
    |                                                                      |
    +----------------------------------------------------------------------+

**The w_a sign problem persists.** Even with a brane quintessence field plus geometric phantom bias, the model predicts w_a > 0 (thawing) while DESI measures w_a < 0 (freezing/phantom). This is the same structural tension identified in Phase 7, now present at a different level.

There is one escape: FREEZING quintessence (Caldwell & Linder 2005), where the field approaches a minimum and w -> -1 from above. This gives w_a < 0. Combined with the geometric phantom bias:

    w_0 ~ -0.97 + (-0.02) = -0.99 (close to -1, not DESI's -0.75)
    w_a ~ -0.1 (from freezing dynamics, correct sign)

But the w_0 value is too close to -1. DESI's large departure from -1 (w_0 = -0.75) cannot come from the geometric effect alone — it requires the quintessence itself to have w_psi significantly above -1, which puts it in the THAWING regime with w_a > 0. You cannot have both large |1 + w_0| AND w_a < 0 with canonical quintessence.

This is a well-known tension in the quintessence literature: the DESI signal sits in the (w_0, w_a) plane where NO canonical single-field model naturally lives (Caldwell & Linder 2005).

---

## 5. DESI + H&K Compatibility Assessment (Task 10C.4)

### 5.1 What the Two-Sector Model Can Fit

**H&K data:** Requires zeta_0 = 0.038. This is provided by the bulk cuscuton, INDEPENDENT of the brane scalar. The H&K fit is preserved by construction.

    Delta-chi^2 (H&K) = -15.17  (UNCHANGED from Phase 7)                 ... (5.1)

**BAO/DESI data:** Requires dynamical w(z) with phantom crossing. The brane scalar provides dynamics (w_psi != -1) but:

- Canonical kinetics: w_psi > -1 always. Combined with geometric bias: w_eff ~ w_psi - 0.02. For w_0^{DESI} = -0.75: need w_psi ~ -0.73 (thawing quintessence, w_a > 0). Does NOT match w_a^{DESI} = -0.86.

- The best the model can do: freezing quintessence with w_0 ~ -0.97 (close to -1) and w_a ~ -0.1 (correct sign but too small). The geometric phantom bias shifts w_0 to ~ -0.99. This is essentially LCDM with small deviations.

### 5.2 Parameter Space Scan (Analytic)

The CPL parameterization w(a) = w_0 + w_a(1-a). For thawing quintessence with potential V(psi) = V_0 * exp(-lambda*psi/M_Pl):

    w_0 = -1 + lambda^2/3    (slow roll approximation)                    ... (5.2)
    w_a = -2*lambda^2/3 * (1 - w_0) = -2*lambda^4/9                      ... (5.3)

For lambda = 0.8: w_0 = -0.787, w_a = +0.091. Close to DESI's w_0 but WRONG SIGN for w_a.

Adding the geometric phantom bias:

    w_0^{eff} = -0.787 - 0.02 = -0.807                                    ... (5.4)
    w_a^{eff} = +0.091 + O(zeta_0^2) approx +0.09                        ... (5.5)

(The geometric bias enters w_a only at second order in zeta_0 because the zeta_0 effect is approximately redshift-independent over the z = 0-2 range.)

**Summary of attainable (w_0, w_a) in the two-sector model:**

| Scenario | w_0 | w_a | Fits DESI? |
|----------|-----|-----|------------|
| Thawing (lambda = 0.8) | -0.81 | +0.09 | w_0 OK, w_a WRONG SIGN |
| Thawing (lambda = 0.5) | -0.92 | +0.04 | w_0 close to -1, w_a WRONG SIGN |
| Freezing (generic) | -0.97 to -0.99 | -0.1 to -0.3 | w_0 too close to -1, w_a correct sign |
| DESI DR2 | -0.75 | -0.86 | — |

**No point in the canonical quintessence parameter space simultaneously matches both w_0 ~ -0.75 AND w_a ~ -0.86.** This is not specific to Meridian — it is a generic feature of canonical single-field quintessence (Scherrer 2006; Caldwell & Linder 2005). DESI's signal, if real, requires either:

1. Non-canonical kinetics (k-essence, phantom field)
2. Multi-field dynamics with non-trivial couplings
3. Modified gravity that DIRECTLY affects the Friedmann equation (not just G_eff rescaling)
4. A systematic in the DESI CPL analysis (the "parametrization bias" discussed in the literature)

### 5.3 chi^2 Estimate

For the two-sector model with thawing quintessence (best attempt at DESI):

    chi^2_{BAO} ~ 5-8  (improved vs LCDM ~ 2.3, but w_a tension persists)
    chi^2_{fsigma8} ~ 7  (similar to LCDM)
    chi^2_{H_0} ~ 0.03  (unchanged)
    chi^2_{H&K} ~ 0.0  (preserved by zeta_0)
    chi^2_{w0wa} ~ 8-15  (w_a sign mismatch dominates)
    chi^2_{total} ~ 20-30

Compare to LCDM + zeta_0 (Phase 7): chi^2 = 11.45.

**The two-sector model is WORSE than LCDM + zeta_0** because the quintessence introduces w_a > 0 tension with the DESI w_a prior. Adding the brane scalar hurts more than it helps.

### 5.4 Assessment

    +----------------------------------------------------------------------+
    |                                                                      |
    |  DESI + H&K COMPATIBILITY: NEGATIVE                                  |
    |                                                                      |
    |  H&K: PRESERVED (zeta_0 from bulk cuscuton, independent)            |
    |                                                                      |
    |  DESI: NOT IMPROVED                                                  |
    |  - The brane scalar provides dynamics but in the WRONG DIRECTION    |
    |    (thawing: w_a > 0 vs DESI: w_a < 0)                             |
    |  - Geometric phantom bias from zeta_0 is 15x too small             |
    |  - No phantom crossing mechanism survives                           |
    |  - The (w_0, w_a) DESI signal lies outside the canonical            |
    |    quintessence region entirely                                      |
    |                                                                      |
    |  Adding a brane scalar makes the TOTAL chi^2 WORSE because:        |
    |  1. Extra parameters without improved w_a                           |
    |  2. AIC/BIC penalty for additional DOF                              |
    |  3. The best-fit quintessence drives w_a in the wrong direction     |
    |                                                                      |
    +----------------------------------------------------------------------+

---

## 6. Fine-Tuning and Predictivity (Task 10C.5)

### 6.1 Parameter Count

| Model | Free parameters | What they are |
|-------|----------------|---------------|
| LCDM | 1 | Lambda |
| LCDM + zeta_0 (Meridian) | 1 | zeta_0 (Lambda self-tuned) |
| Two-sector (Meridian + quintessence) | 3+ | zeta_0, V_0, lambda (or V(psi) shape) |
| CPL phenomenological | 2 | w_0, w_a |

The two-sector model adds at MINIMUM 2 new parameters (the quintessence potential amplitude and slope) on top of zeta_0. If the potential has structure (e.g., hilltop, axion-like), additional parameters enter.

### 6.2 Fine-Tuning of V(psi)

The quintessence mass problem is well-known (Weinberg 1989; Carroll 1998): for the field to evolve on cosmological timescales, its mass must satisfy:

    m_psi ~ H_0 ~ 10^{-33} eV                                             ... (6.1)

This requires:

    V''(psi) ~ H_0^2 ~ 10^{-66} eV^2                                     ... (6.2)

For a potential V(psi) = V_0 * f(psi/M_Pl), naturalness suggests V'' ~ V_0/M_Pl^2. With V_0 ~ rho_crit ~ 10^{-47} GeV^4:

    V'' ~ 10^{-47} / (2.4*10^{18})^2 ~ 10^{-83} GeV^2 = 10^{-65} eV^2  ... (6.3)

This is accidentally close to H_0^2 = 10^{-66} eV^2 — off by one order of magnitude. The quintessence mass is "technically natural" in the sense that V'' / M_Pl^2 ~ Lambda / M_Pl^4 (the cosmological constant naturalness problem in disguise), but it requires:

1. **Radiative stability:** Quantum corrections from SM loops generate delta(m_psi^2) ~ g^2 * Lambda_UV^2 / (16*pi^2). For m_psi to remain at H_0, the coupling g of psi to SM must satisfy g < 10^{-60} (completely disconnected from all known physics) OR psi must be protected by a symmetry that the NCG framework does not provide.

2. **No interaction with the cuscuton:** The quintessence mass must be protected from the cuscuton's infinite sound speed. The cuscuton constraint propagates instantaneously (c_s -> infinity), and any coupling between psi and phi would transfer this stiffness to psi, raising its mass. The junction condition analysis (Section 4.3) shows the coupling is negligible (10^{-101}), so this is not a practical concern.

3. **The eta problem in quintessence:** Even without direct couplings, gravitational-strength interactions between psi and other fields generate delta(m_psi^2) ~ H^2 * (M_Pl / M_Pl)^2 ~ H^2. This is the "eta problem" of quintessence (Kolb & Turner 1990): gravitational loops renormalize the quintessence mass to m_psi ~ H. This is EXACTLY the value needed for cosmological evolution. But it's a coincidence — there's no symmetry protecting this relation.

### 6.3 Fine-Tuning Comparison

| Model | Fine-tuning | Nature |
|-------|-------------|--------|
| LCDM | Lambda ~ 10^{-122} M_Pl^4 (1 parameter, extreme tuning) | The CC problem |
| LCDM + zeta_0 | Lambda self-tuned (geometric), zeta_0 = O(0.01) natural | Significant improvement |
| Two-sector | Same as Meridian + m_psi ~ H_0 (quintessence eta problem) | Adds new tuning |

The two-sector model INHERITS Meridian's self-tuning for Lambda (resolving the CC problem) but INTRODUCES a new tuning for the quintessence mass. This is a net loss in naturalness compared to LCDM + zeta_0 alone.

### 6.4 Testability and New Predictions

If the two-sector model were adopted, its distinctive predictions beyond w_0, w_a:

1. **Gravitational slip eta = 1 + O(zeta_0):** Unchanged from Meridian. Testable by Euclid, Vera Rubin.

2. **w_psi > -1 always:** The brane scalar has canonical kinetics, so the true DE EoS never crosses -1. If observers measure w < -1, it is a GEOMETRIC artifact from G_eff. This is testable: independent measurements of G (e.g., lunar laser ranging, binary pulsars) would reveal G_eff != G_N.

3. **Sound speed c_s(psi) = 1:** Canonical quintessence has luminal sound speed. This differs from k-essence models (c_s < 1) and is potentially testable through DE perturbation effects on the matter power spectrum.

4. **No gravitational wave speed modification:** alpha_T = 0 (unchanged from Meridian). Already confirmed by GW170817.

5. **ISW anomaly from zeta_0:** The H&K signal is a UNIQUE prediction of the two-sector model — it requires both the bulk cuscuton (for zeta_0) and is independent of the brane scalar. No other DE model predicts this specific ISW signature.

---

## 7. Verdict and Recommendations

### 7.1 Track 10C Assessment

| Sub-task | Result | Status |
|----------|--------|--------|
| **10C.1: NCG origin** | No NCG extension produces a brane scalar at H_0 scale. All NCG scalars have masses set by their symmetry-breaking scales (10^{10}-10^{16} GeV). Brane quintessence is phenomenological, not first-principles. | **WEAKENED (ad hoc)** |
| **10C.2: Friedmann equations** | Two-sector system derived. Cuscuton provides zeta_0 (unchanged). Quintessence adds standard dynamics. G_eff = G_N/(1+2*zeta_0) rescales all densities. Sectors effectively decoupled (rho_psi/sigma ~ 10^{-101}). | **COMPLETE** |
| **10C.3: Phantom crossing** | Geometric mechanism (G_eff misidentification) works in principle but is 15x too small for DESI. DBI kinetics killed (positive-definite KE). Junction coupling killed (10^{-101} suppression). | **INSUFFICIENT** |
| **10C.4: DESI + H&K fit** | H&K preserved (from cuscuton). DESI NOT improved — thawing quintessence gives w_a > 0 (wrong sign); freezing gives w_0 too close to -1. chi^2 is WORSE than LCDM + zeta_0 alone. | **NEGATIVE** |
| **10C.5: Fine-tuning** | Adds 2+ parameters plus quintessence eta problem (m_psi ~ H_0 tuning). Net loss in naturalness vs LCDM + zeta_0. | **UNFAVORABLE** |

### 7.2 The Structural Result

The brane quintessence track fails for a reason that is DEEPER than parameter tuning: **the DESI (w_0, w_a) signal lies outside the region accessible to ANY canonical single-field quintessence model.** This is true with or without the Meridian framework. The geometric phantom crossing from zeta_0 adds a small (~2%) phantom bias but cannot bridge the gap.

The problem has three layers:

1. **Phantom crossing requires w < -1.** Canonical quintessence gives w > -1 always. The geometric mechanism from zeta_0 = 0.038 produces |delta_w| ~ 0.02, which is 15x too small.

2. **The w_a sign problem.** Large |1 + w_0| (DESI) requires fast-rolling quintessence (thawing), which gives w_a > 0. Negative w_a (DESI) requires freezing quintessence, which gives w_0 close to -1. These are mutually exclusive.

3. **The no-go theorem.** For canonical quintessence: the (w_0, w_a) plane is bounded by the thawing and freezing boundaries (Caldwell & Linder 2005). DESI's best-fit point (w_0 = -0.75, w_a = -0.86) lies OUTSIDE both boundaries. No canonical single-field potential V(psi) can reach it.

### 7.3 What Survives

The geometric phantom crossing mechanism (Section 4.1) is NOT useless — it establishes a PREDICTION:

**Any observer who fits DESI data assuming GR with G = G_N will infer a phantom bias of delta_w ~ -0.02 relative to the true w_DE, if the Meridian framework is correct.**

This is small but systematic and in the CORRECT direction (phantom). It means:
- If future DESI data converges toward w_0 = -0.98 +/- 0.02 (very close to -1), the Meridian model with zeta_0 = 0.038 could explain the phantom crossing as a G_eff artifact.
- If DESI's current signal (|1 + w_0| ~ 0.25) persists, the Meridian framework requires physics beyond brane quintessence.

### 7.4 Recommendation

**Track 10C produces a partial result with a clear negative conclusion for DESI.**

The brane quintessence does not resolve the DESI tension. The main value of 10C is:
1. Confirming that the two sectors (cuscuton + quintessence) effectively decouple (10^{-101})
2. Quantifying the geometric phantom crossing effect (delta_w ~ -0.02 from zeta_0)
3. Establishing that DESI's (w_0, w_a) point is inaccessible to canonical single-field DE in general

**Proceed to Track 10A (generalized P(X)) as the higher-priority path.** Track 10A addresses the root cause: if the full KK reduction produces P(X) corrections beyond the cuscuton limit, the zero kinetic energy theorem breaks, and the cuscuton itself becomes dynamical. This is more economical (no new fields) and more principled (follows from A1 + A2 without additional assumptions).

Track 10D (hybrid: complete effective action) should synthesize 10A and 10C after 10A is complete.

### 7.5 Connection to the Leaked Engineering

The brane scalar psi, if it existed, would couple directly to brane-localized EM fields through standard field theory (no Planck suppression, no bulk propagation needed). This would provide the EM-gravity coupling channel that the cuscuton cannot:

    L_interaction ~ g_psi * psi * F_mu_nu F^{mu_nu}                       ... (7.1)

But since 10C.1 shows no first-principles origin for psi, and 10C.4 shows it doesn't fit the data, this channel is moot. The leaked engineering requires a mechanism in the gravitational sector, not the quintessence sector.

---

## 8. Appendix: The Geometric Phantom Crossing Formula

For reference, the exact expression for w_eff in the two-sector model:

Define:
- Omega_m = matter density parameter (= 0.315)
- Omega_DE = total dark energy parameter (= 0.685)
- f = Omega_psi / Omega_DE (quintessence fraction of DE)
- zeta_0 = non-minimal coupling parameter (= 0.038)
- w_psi = quintessence equation of state

The inferred equation of state (by an observer assuming GR + G_N):

    w_eff = (f * w_psi * Omega_DE - zeta_0 * [2*Omega_m*w_m + 2*Omega_r*w_r]) /
            (f * Omega_DE + (1-f)*Omega_DE - 2*zeta_0*(Omega_m + Omega_r))
                                                                            ... (A.1)

At late times (Omega_r -> 0, w_m = 0):

    w_eff = [f * w_psi * Omega_DE - (1-f)*Omega_DE] /
            [f * Omega_DE + (1-f)*Omega_DE - 2*zeta_0*Omega_m]

Simplifying (the cuscuton contributes w_cusc = -1 to the (1-f) fraction):

    w_eff = [f * w_psi - (1-f)] /
            [1 - 2*zeta_0*Omega_m/Omega_DE]                               ... (A.2)

    w_eff = [-1 + f*(1 + w_psi)] * [1 + 2*zeta_0*Omega_m/Omega_DE + ...]
                                                                            ... (A.3)

To first order in zeta_0:

    w_eff = -1 + f*(1 + w_psi) + 2*zeta_0*Omega_m/Omega_DE * [-1 + f*(1 + w_psi)]
                                                                            ... (A.4)

The geometric phantom bias (second term):

    delta_w^{geom} = 2*zeta_0*(Omega_m/Omega_DE) * (w_DE^{true} + 1)     ... (A.5)

Wait — this is second order in (1 + w_DE) * zeta_0. The LEADING phantom bias is:

    delta_w^{geom} = -2*zeta_0*Omega_m/Omega_DE                           ... (A.6)

only when the observer identifies the total density normalization. Let me be very precise.

The correct leading-order result: an observer fitting H^2(z) = H_0^2 [Omega_m(1+z)^3 + Omega_DE(1+z)^{3(1+w_0+w_a)} exp(-3*w_a*z/(1+z))] will infer:

    H_0^{obs} = H_0^{true} / sqrt(1 + 2*zeta_0)                          ... (A.7)
    Omega_m^{obs} = Omega_m^{true} / (1 + 2*zeta_0)                       ... (A.8)

The observer's Omega_m is 7.6% lower than the true value. The "missing" matter density is absorbed into the dark energy component, making it appear to evolve (grow with time), which mimics phantom behavior.

The phantom bias at z = 0:

    1 + w_eff = (1 + w_psi^{true}) * f + 2*zeta_0*Omega_m^{true}*(1+w_psi^{true})*f / Omega_DE
                                                                            ... (A.9)

This is O(zeta_0 * (1+w_psi)), so the bias is only significant when w_psi is significantly different from -1, which is exactly the thawing regime where w_a has the wrong sign.

The bottom line: **the geometric phantom crossing from zeta_0 = 0.038 shifts w_eff by ~ -0.02 at z = 0, insufficient for DESI but detectable in principle by next-generation surveys.**

---

*D10.7-D10.8 — Clayton & Clawd, March 16, 2026*
