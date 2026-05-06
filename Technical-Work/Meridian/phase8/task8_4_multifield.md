# D8.4 — Multi-Field Analysis: KK Moduli Census and Mass Spectrum

**Track 8D | Clayton & Clawd | March 16, 2026**

---

## 1. Purpose

Tracks 8B, 8C, 8E, and 8F all failed because the cuscuton's zero kinetic energy theorem suppresses every single-field background modification to O(zeta_0 * gamma_r) ~ 10^{-3}. D8.3 Section 5.3 identified a second dynamical scalar as one of only two mechanisms that could bypass this bottleneck: a field with its OWN propagating degree of freedom, its own phi-dot, unconstrained by the cuscuton theorem.

Track 8D asks the decisive question: **does the Meridian KK reduction produce any scalar degree of freedom light enough (m <= H_0 ~ 10^{-33} eV) to be cosmologically active at late times?**

A scalar with m >> H_0 oscillates rapidly on cosmological timescales, its energy density redshifts as matter (rho ~ a^{-3}), and it cannot drive dark energy or phantom crossing. Only a scalar with m ~ H_0 can evolve slowly enough to contribute w != -1.

---

## 2. The KK Scalar Census

We systematically enumerate every scalar degree of freedom in the Meridian 5D -> 4D reduction. The 5D action (D1.1, eq. 8):

    S_bulk = int d^5x sqrt(-G) [(M_5^3 - xi*phi^2)R_5 + mu_0^2*sqrt(2X) - c*phi - Lambda_5]

The geometry: S^1/Z_2 orbifold, two branes at y = 0 (UV) and y = y_c (IR), with warp factor e^{2A(y)}.

### 2.1 Radion (Size Modulus)

**What it is:** The inter-brane distance T(x) = y_c(x), promoted to a 4D field.

**Mass mechanism:** In standard RS1, the radion is massless — the Goldberger-Wise (GW) mechanism introduces a bulk scalar to stabilize it. In Meridian, the cuscuton IS the stabilizing field (D2.2, Section 5.2). The scalar constraint E2 locks phi to the geometry, and the junction conditions J3a/J3b fix phi at both branes. The shooting problem has a unique solution for y_c, generating a potential V_r(T) with V_r'(T_0) = 0 and V_r''(T_0) > 0.

**Mass estimate:**

In the GW mechanism:

    m_r ~ k * e^{-k*y_c}                                                    ... (2.1)

where k = sqrt(-Lambda_5 / (6*M_5^3)) is the AdS_5 curvature scale and e^{-k*y_c} = m_W/M_Pl ~ 10^{-16} is the warp factor evaluated at the IR brane. With k ~ M_Pl:

    m_r ~ 2.4 x 10^{18} GeV * 10^{-16} = 2.4 x 10^2 GeV                   ... (2.2)

**Cuscuton stiffening:** The cuscuton has c_s -> infinity, meaning the scalar constraint propagates instantaneously. When the radion fluctuates (delta T != 0), the cuscuton profile phi(y) must simultaneously adjust to satisfy E2 everywhere — this is instantaneous, providing an ADDITIONAL restoring force beyond the standard GW potential. Therefore (D2.2, eq. 5.7):

    m_r^{Meridian} >= m_r^{GW} ~ TeV                                        ... (2.3)

The cuscuton can only RAISE the radion mass, never lower it.

**Mass gap:**

    m_r / H_0 ~ (2.4 x 10^2 GeV) / (10^{-33} eV) = 2.4 x 10^{44}        ... (2.4)

The radion is 44 orders of magnitude too heavy. Even if the GW estimate were wrong by a factor of 10^{10} (absurd), the radion would still be 34 orders of magnitude above H_0.

**Status: KILLED.**

### 2.2 KK Graviton Tower

**What they are:** The massive spin-2 modes h_mu_nu^{(n)}(x) from the Sturm-Liouville decomposition of the 5D graviton (D2.2, Section 6).

**Mass spectrum (RS limit):**

    m_n = x_n * k * e^{-k*y_c}                                              ... (2.5)

where x_n are zeros of J_1(x): x_1 = 3.83, x_2 = 7.02, etc.

    m_1 = 3.83 * k * e^{-k*y_c} ~ 3.83 * TeV ~ several TeV               ... (2.6)

**Cuscuton modification:** The non-constant F(phi(y)) in the eigenvalue equation tilts the effective potential, RAISING the KK masses (D2.2, eq. 6.8):

    m_n^{Meridian} >= m_n^{RS}    (for xi > 0)                              ... (2.7)

**Note on scalar component:** Each massive KK graviton (m_n > 0) is a massive spin-2 field in 4D, which has 5 polarization states: 2 tensor + 2 vector + 1 scalar. The scalar polarization ("longitudinal graviton") is NOT an independent degree of freedom — it is eaten by the massive graviton via the Stuckelberg mechanism during the KK decomposition. There is no free scalar from this sector.

**Status: KILLED. m_1 ~ TeV >> H_0.**

### 2.3 Brane Bending Mode

**What it is:** In general braneworld models, the brane can bend: its embedding y = y_0 + f(x^mu), where f(x) is a 4D scalar field describing transverse fluctuations.

**In RS1 without stabilization:** The brane bending mode IS the radion. There is no independent degree of freedom — f(x) and T(x) are related by gauge transformations in the bulk (Charmousis, Gregory, Rubakov 2000).

**In RS1 with stabilization (GW or cuscuton):** The stabilization mechanism locks the branes at fixed y-positions. Brane bending fluctuations are absorbed into the radion fluctuation plus the stabilizing scalar's fluctuation. For the cuscuton specifically: the constraint E2 eliminates one degree of freedom (the cuscuton has zero propagating DOF in the bulk), so the brane bending is entirely captured by the radion T(x).

**Status: NOT INDEPENDENT. Already counted as radion (Section 2.1).**

### 2.4 Wilson Line Scalars

**What they are:** If there are bulk gauge fields A_M with M = 0,1,2,3,5, the fifth component A_5(x) is a 4D scalar (the Wilson line around the extra dimension).

**In Meridian:** The 5D action contains gravity (G_MN), a scalar (phi), and the Standard Model (localized on the IR brane). There are NO bulk gauge fields. The SM gauge fields live on the brane, not in the bulk.

**Status: ABSENT. No bulk gauge fields in the Meridian geometry.**

### 2.5 NCG Higgs (Inner Fluctuations of D_F)

**What it is:** In the NCG extension (Phase 5), the Higgs arises from inner fluctuations of the finite spectral triple. Its mass is:

    m_H = 125 GeV                                                           ... (2.8)

This is the observed Higgs boson — its mass is a measured input (or, in the NCG formalism, a constraint on the Yukawa couplings in the spectral action).

**Cosmological relevance:**

    m_H / H_0 ~ 125 GeV / 10^{-33} eV ~ 10^{44}                           ... (2.9)

Same gap as the radion. A 125 GeV scalar oscillates at frequency omega = m_H ~ 10^{26} Hz. On cosmological timescales (H_0^{-1} ~ 10^{17} s), it has undergone ~ 10^{43} oscillations. Its energy density redshifts as rho ~ a^{-3} (pressure-averaged to zero over many oscillations). It behaves as cold matter, not dark energy.

**Status: KILLED. m_H ~ 10^{44} H_0.**

### 2.6 Shape Moduli

**What they are:** For a compact extra dimension with non-trivial topology, shape moduli parametrize the geometry of the internal space at fixed volume. Examples: the complex structure moduli of a Calabi-Yau, the shape of a torus (ratio of radii), the opening angle of a cone.

**For S^1/Z_2:** The internal space is a line segment [0, y_c]. A one-dimensional space has NO shape — it is completely characterized by its length y_c (the radion). There are no additional geometric moduli.

**Compare:** If the extra dimension were T^2/Z_2 (a 2D orbifold), there would be one shape modulus (the ratio of the two radii). If it were a 6D Calabi-Yau, there would be O(100) moduli. The S^1/Z_2 orbifold is the simplest possible compact space.

**Status: ABSENT. One-dimensional extra space has no shape moduli.**

### 2.7 Pseudo-Goldstone Bosons from Approximate Symmetries

**What they are:** If the 5D action has an approximate continuous symmetry that is spontaneously broken, the resulting pseudo-Goldstone boson (pGB) can be naturally light: m_pGB ~ sqrt(delta * Lambda^2), where delta << 1 measures the explicit breaking.

**Candidate symmetry in Meridian:** The cuscuton kinetic term P(X) = mu_0^2 * sqrt(2X) is invariant under the shift symmetry phi -> phi + c (it depends on X = -1/2 (d phi)^2, not on phi directly). The tadpole potential V(phi) = c * phi BREAKS this symmetry explicitly.

But: **the shift of phi IS the dark energy field.** The cuscuton on the brane, phi_IR(t), evolves via the tadpole, producing V_eff = c_eff * phi_IR (D2.2, eq. 3.6). This is the field whose dynamics we have been studying throughout Phases 3-8. It is not a "new" degree of freedom — it is the cuscuton itself, already included in the single-field analysis.

Moreover, the cuscuton is a CONSTRAINED field, not a dynamical one. The shift phi -> phi + c is a constraint symmetry, not a Goldstone-generating symmetry. Breaking it with V = c*phi does not produce a propagating pGB — it modifies the constraint equation.

**Status: ALREADY COUNTED. The shift symmetry generates the cuscuton dark energy field itself, not a new scalar.**

### 2.8 Radion Fluctuations at Higher Order

**What they are:** Beyond the leading-order analysis, one might worry that the radion potential V_r(T) has additional minima or flat directions at higher order in the cuscuton corrections.

**Analysis:** The radion potential has the schematic form:

    V_r(T) = V_0 + (1/2) m_r^2 (T - T_0)^2 + (1/6) lambda_r (T - T_0)^3 + ...   ... (2.10)

The cuscuton stiffening ensures m_r^2 > 0 with m_r ~ TeV (Section 2.1). For a flat direction to exist, we would need m_r^2 -> 0 via a cancellation between the GW-type contribution and the cuscuton contribution. But the cuscuton ADDS to the stiffness (c_s -> infinity means additional restoring force) — the two contributions have the same sign. There is no cancellation mechanism.

**Status: KILLED. No flat directions in V_r(T).**

---

## 3. The Complete Mass Census

| Scalar | Source | Mass | m/H_0 | Status |
|--------|--------|------|-------|--------|
| **Radion T(x)** | Size modulus | ~TeV | ~10^{44} | KILLED |
| **KK graviton (scalar)** | Stuckelberg | Eaten | N/A | Not independent |
| **Brane bending f(x)** | Embedding | = Radion | ~10^{44} | Not independent |
| **Wilson lines** | A_5 | — | — | Absent (no bulk gauge) |
| **NCG Higgs** | D_F fluctuations | 125 GeV | ~10^{44} | KILLED |
| **Shape moduli** | Internal geometry | — | — | Absent (1D space) |
| **Shift pGB** | phi -> phi + c | = Cuscuton DE | Already in model | Not new |
| **Radion flat direction** | Higher-order V_r | — | — | Absent (cuscuton stiffens) |

**No scalar in the Meridian KK reduction has m <= H_0.**

The lightest scalar is the radion at m ~ TeV, which is 44 orders of magnitude heavier than H_0. Every scalar is either:
- Massive at the TeV scale or above (radion, Higgs, KK tower)
- Not an independent degree of freedom (brane bending, Stuckelberg scalar)
- Absent from the geometry (Wilson lines, shape moduli)
- Already included in the single-field analysis (cuscuton shift)

---

## 4. Could Any Known Mechanism Produce m ~ H_0?

The gap is 44 orders of magnitude. We consider every known mechanism for generating ultra-light scalars.

### 4.1 Radiative Mass Protection

Ultra-light scalars exist in nature (e.g., the axion, with m_a ~ 10^{-5} eV protected by a U(1)_PQ symmetry). The mechanism requires a symmetry that forbids a mass term at tree level, with the mass generated only radiatively:

    m^2 ~ g^2 * Lambda^2 / (16*pi^2)                                        ... (4.1)

For m ~ H_0 ~ 10^{-33} eV with Lambda ~ TeV:

    g^2/(16*pi^2) ~ (10^{-33}/10^{12})^2 ~ 10^{-90}
    g ~ 10^{-44}                                                             ... (4.2)

No coupling in the Meridian action is this small. The smallest dimensionless coupling is zeta_0 ~ 0.04 — sixty-two orders of magnitude too large. There is no symmetry in the Meridian action that could protect a scalar mass to the 10^{-33} eV level.

### 4.2 Pseudo-Goldstone from Approximate Symmetry (quantitative)

For a pGB with mass:

    m_pGB^2 = delta * f^2                                                    ... (4.3)

where f is the symmetry-breaking scale and delta is the explicit breaking parameter.

For f ~ TeV and m ~ H_0:

    delta ~ (H_0/TeV)^2 ~ 10^{-90}                                          ... (4.4)

The cuscuton shift symmetry is broken by V = c*phi, with c = O(M_5) ~ O(10^{17} GeV). The breaking parameter:

    delta ~ c/M_5 ~ O(1)                                                    ... (4.5)

Not 10^{-90}. The symmetry is maximally broken — the tadpole is an O(1) effect in bulk units. This is by design: the tadpole is the source of dark energy, and it must be O(1) in the bulk to produce the correct warp-suppressed value on the brane.

### 4.3 Hubble Friction (Misner Effect)

A massive scalar in an expanding universe obeys:

    phi-double-dot + 3H*phi-dot + m^2*phi = 0                               ... (4.6)

For m >> H, the field oscillates with frequency omega = m, and the time-averaged equation of state is w = 0 (matter). The field does NOT act as dark energy.

For m << H, the field is frozen by Hubble friction: phi ~ const, rho ~ V(phi) ~ const, w ~ -1. This is the "cosmological constant" regime — the field IS dark energy, but only because it's not moving. It doesn't produce phantom crossing (w stays at -1).

For m ~ H (the "just right" case): the field thaws, transitioning from w = -1 to w > -1. This IS the quintessence mechanism, and it CAN produce w != -1. But we need m ~ H_0 ~ 10^{-33} eV, and no Meridian scalar achieves this.

### 4.4 Cosmological Relaxation (Clockwork/Chain)

The clockwork mechanism generates exponentially small couplings from O(1) parameters through a chain of N fields with nearest-neighbor interactions. Could a clockwork chain in the extra dimension produce m ~ H_0?

In RS-type geometries, the warp factor ALREADY provides exponential suppression: e^{-k*y_c} ~ 10^{-16}. The radion mass is:

    m_r ~ k * e^{-k*y_c} ~ k * 10^{-16}                                    ... (4.7)

For m_r ~ H_0 ~ 10^{-33} eV:

    k ~ 10^{-17} eV                                                         ... (4.8)

But k sets the AdS curvature, which must satisfy k ~ M_Pl to solve the hierarchy problem (D2.2, Section 6.3 requires k/M_Pl >= 0.6). We cannot have k ~ 10^{-17} eV without abandoning the hierarchy solution entirely.

Even introducing a second warped throat or a clockwork chain does not help: every new exponential suppression requires new branes and new tunings, and the resulting moduli would need their own stabilization mechanism, reintroducing m ~ TeV masses.

### 4.5 Flat Potential Directions

For a scalar to have m ~ H_0, it needs V''(phi) ~ H_0^2. Could the radion potential V_r(T) have a nearly flat region?

The curvature of the radion potential (from D2.2, Section 5):

    V_r''(T_0) ~ k^2 * e^{-2k*y_c} ~ (TeV)^2                              ... (4.9)

This is fixed by the RS geometry: the potential curvature is set by the same scale as the radion mass. Making V_r'' small requires making the stabilization mechanism weak, which destabilizes the hierarchy.

The cuscuton makes this WORSE: c_s -> infinity means the scalar constraint provides an infinitely stiff contribution to the radion potential. The radion cannot be made light in the cuscuton geometry.

---

## 5. Multi-Field Phantom Crossing: The Ghost Problem

Even if we could conjure a light scalar from outside the Meridian framework (e.g., by adding one by hand), phantom crossing in multi-field models faces a fundamental obstacle.

### 5.1 The Crossing Condition

The total dark energy equation of state with two scalars (cuscuton phi + hypothetical light scalar chi):

    w = (K_1 + K_2 - V_total) / (K_1 + K_2 + V_total)                     ... (5.1)

where K_1 = K_eff^{cuscuton} ~ 0 (zero kinetic energy) and K_2 = (1/2)*chi-dot^2 is the kinetic energy of the second scalar.

For w < -1 (phantom regime):

    K_1 + K_2 < 0                                                           ... (5.2)

Since K_1 >= 0 (the cuscuton kinetic term is non-negative by construction), we need:

    K_2 < -K_1 <= 0                                                         ... (5.3)

**A negative kinetic energy means the second scalar is a ghost.**

### 5.2 The Cuscuton Exception

The cuscuton itself can achieve phantom crossing (w < -1) without ghosts precisely because it has zero propagating degrees of freedom. The "phantom" behavior comes from the constraint structure, not from negative kinetic energy of a propagating mode. This is the insight from Iyonaga, Takahashi, Kobayashi (2018).

But a second scalar chi, if it propagates (which it must, to bypass the zero kinetic energy theorem), IS subject to the ghost constraint. You cannot have K_2 < 0 for a propagating scalar without generating vacuum instabilities (the Hamiltonian is unbounded below, leading to catastrophic production of ghost + positive-energy particle pairs).

### 5.3 Multi-Field Crossing Without Ghosts

There IS a known mechanism: the kinetic coupling (G_3-type Horndeski interaction) between two scalars can produce an effective phantom crossing without either field being a ghost. This requires:

    L_mix = G(phi, chi, X_phi, X_chi) * Box(phi) * (d chi)^2               ... (5.4)

or similar cross-kinetic terms. In the Meridian KK reduction, such terms would arise from the bulk metric-scalar interaction through the KK decomposition.

However: the cuscuton's constraint structure (c_s -> infinity, zero propagating DOF) means that the phi-dependent terms in G do not contribute dynamical cross-coupling — they modify the constraint equation, not the dynamics. The net effect is equivalent to a renormalization of the chi kinetic term, which is positive definite for a healthy second field.

**In short: the cuscuton cannot participate in a ghost-free phantom crossing through kinetic mixing, because it doesn't propagate.**

---

## 6. The 45-Order-of-Magnitude Desert

The mass gap between the lightest Meridian scalar (radion, m_r ~ TeV) and the cosmological Hubble scale (H_0 ~ 10^{-33} eV) spans:

    log_10(m_r / H_0) = log_10(10^{12} eV / 10^{-33} eV) = 45              ... (6.1)

This is not a parametric gap that could be closed by adjusting coupling constants. It is a STRUCTURAL gap built into the RS geometry:

1. **The hierarchy solution requires k ~ M_Pl.** This fixes the bulk curvature scale.
2. **The warp factor e^{-k*y_c} ~ 10^{-16} is fixed by the weak scale.** This is a measured number.
3. **All KK and moduli masses scale as m ~ k * e^{-k*y_c} ~ TeV.** This follows from (1) and (2).
4. **H_0 ~ 10^{-42} GeV is fixed by observation.** This is the expansion rate of the universe.

The gap m_KK / H_0 ~ 10^{45} is a consequence of the hierarchy problem itself: the weak scale is 10^{16} times smaller than the Planck scale, and the Hubble scale is 10^{29} times smaller than the weak scale. No mechanism within the RS/Meridian framework can produce a scalar at the Hubble scale without either:

(a) Abandoning the hierarchy solution (setting k << M_Pl), or
(b) Introducing a NEW small parameter of order 10^{-45}, which would constitute a worse fine-tuning than the cosmological constant problem the model was designed to solve.

---

## 7. Verdict

### 7.1 Kill Condition

**Track 8D is KILLED.**

All Kaluza-Klein scalar moduli in the Meridian geometry have masses at or above the TeV scale — 44 to 45 orders of magnitude heavier than the Hubble rate H_0. The cuscuton stabilization mechanism only INCREASES moduli masses relative to the standard Goldberger-Wise result. No mechanism exists within the Meridian framework for generating an ultra-light scalar with m ~ H_0:

- Radiative protection requires couplings of order 10^{-44} (none exist)
- Pseudo-Goldstone requires symmetry breaking at 10^{-90} (the tadpole breaks at O(1))
- Flat potential directions are precluded by cuscuton stiffening (c_s -> infinity)
- Cosmological relaxation requires abandoning the hierarchy solution (k << M_Pl)

Even if an ultra-light scalar existed, multi-field phantom crossing requires either a ghost (K_2 < 0) or kinetic mixing with the cuscuton — but the cuscuton's constraint structure (zero propagating DOF) prevents ghost-free phantom crossing through mixing.

The kill is structural: the 45-order-of-magnitude mass desert is a geometric consequence of the RS hierarchy solution, not a parametric accident.

### 7.2 Implication: All Concrete Single-Framework Physics Tracks Exhausted

With Track 8D killed, every concrete physics mechanism within the Meridian geometry has been tested and eliminated:

| Track | Mechanism | Kill | Root Cause |
|-------|-----------|------|------------|
| **8A** | Methodology | Passed | Tension is real |
| **8B** | Projected Weyl tensor | delta_w ~ 10^{-3} | O(zeta_0^2) — static Weyl renormalizes Lambda_4 |
| **8C** | DE-DM coupling | delta_w ~ 4 x 10^{-4} | O(zeta_0 * sqrt(delta)) — cuscuton barely moves |
| **8D** | Multi-field (KK moduli) | m_lightest ~ TeV | 45-order mass gap from RS hierarchy |
| **8E** | RG flow of mu^2 | c_1 ~ 10^{-3} | Perturbative loop suppression (gravity-only coupling) |
| **8F** | EDE / sound horizon | sigma(r_d) = 0.26 Mpc | CMB prior too tight; wrong w_a sign persists |
| **8G** | Matter-sector mimicry | delta_w ~ 2 x 10^{-3} | BAO = background observable; cuscuton modifies perturbations |

**Seven tracks tested. Six killed. One (8A) confirmed the tension is real.**

### 7.3 The Remaining Tracks

| Track | Status | Nature |
|-------|--------|--------|
| **8H** | Untested | Topological (EPS domain walls) — speculative, no concrete mechanism |
| **8I** | The fallback | Accept LAMBDA-CDM + zeta_0 as the model's prediction |

Track 8H (topological channel) is speculative: it requires domain walls from the EPS mechanism to produce late-time phase transitions that modify the background. This is outside the standard KK framework and has no established theoretical foundation within the Meridian geometry. It could be explored as a speculative extension but offers no concrete prediction.

Track 8I is the honest conclusion: **the Meridian model predicts LAMBDA-CDM + zeta_0.** The background is indistinguishable from a cosmological constant (w_0 = -0.994, w_a = +0.017). The model's distinctive prediction is at the perturbation level: the non-minimal coupling zeta_0 = 0.038 modifies the growth function mu(a) = F_0/F(a), producing an ISW signal that fits Hubble & Kovacs (2024) with Delta-chi^2 = -15 relative to LAMBDA-CDM.

### 7.4 The Structural Picture

The six kills share a unified root cause that can be stated in one sentence:

**The cuscuton's zero kinetic energy theorem makes it the perfect perturbation-level modification (ghost-free, first-order in zeta_0 for growth) and simultaneously prevents it from modifying the background expansion (all background effects are O(zeta_0^2) or suppressed by the 45-decade KK mass gap).**

This is not a weakness to be fixed — it is the model's identity. The Meridian geometry was built to be ghost-free (via the cuscuton constraint) and to solve the hierarchy problem (via the RS warp factor). Both of these structural commitments preclude large background modifications:

- Ghost-freedom => zero propagating DOF => zero kinetic energy => w_0 ~ -1
- RS hierarchy => all moduli at TeV => no ultra-light scalars => no multi-field DE

The model cannot do what it was not built to do.

---

## 8. Recommendation

**Close Track 8D. Proceed to Track 8I: accept the model as-is.**

The Meridian prediction is LAMBDA-CDM + zeta_0:
- Background: w_0 = -0.994, w_a = +0.017 (indistinguishable from cosmological constant)
- Perturbations: mu(a) = F_0/F(a) with zeta_0 = 0.038 (4% modification to growth)
- Distinctive signal: ISW anomaly (Hubble & Kovacs 2024), Delta-chi^2 = -15 vs LAMBDA-CDM
- EFT fingerprint: c_s -> infinity, zero propagating DOF, phantom-without-ghosts in principle but not in practice

The DESI phantom crossing (w_0 ~ -0.75, w_a ~ -0.9) is NOT reproduced. If DESI's signal is confirmed with more data, it requires physics beyond the single-field cuscuton in 5D RS geometry. The non-perturbative RG question (D8.5, Section 5) remains the most interesting theoretical direction — it is the one place where the structural argument could break down, because the cuscuton's singular kinetic term invalidates perturbation theory.

For publication: the model stands on the H&K fit, the hierarchy unification, and the self-tuning mechanism. The DESI non-reproduction is a clear, falsifiable prediction. Flag it as such.

---

*D8.4 — Clayton & Clawd, March 16, 2026*
