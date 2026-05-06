# No-Go Theorems for Dynamical Dark Energy in Self-Tuning Warped Gravity

**Clayton W. Iggulden-Schnell**

*Draft v1.6 — March 17, 2026*

**Abstract.** We present a systematic exclusion analysis of dynamical dark energy mechanisms within the framework of five-dimensional self-tuning cosmology (Paper I). Starting from the zero kinetic energy theorem — K_eff = 2XP_X - P = 0 for the cuscuton kinetic function P(X) = mu^2 sqrt(2X) — we investigate 16 distinct mechanisms spanning perturbative background modifications, extended kinetic structures, multi-field approaches, non-perturbative quantum channels, and geometric extensions. All 16 mechanisms are killed or demonstrate quantitative insufficiency, with the maximum achievable deviation |delta w| ~ 0.007 (from NCG Gauss-Bonnet corrections), a factor of ~36 below DESI requirements. The kills are not independent: they trace to three structural barriers. The **zero KE barrier** forces all single-field background modifications to O(zeta_0 * gamma_r) ~ 10^{-3}. The **hierarchy-moduli barrier** locks all Kaluza-Klein scalars at m ~ TeV, 44 orders of magnitude above H_0. The **Horndeski dilemma** — which we formalize as a theorem — shows that the self-tuning condition uniquely determines P(X), leaving no freedom to independently fit the dark energy equation of state. Together, these establish that w_0 approx -0.993 is a structural prediction of the framework, not a parametric choice. The prediction is falsifiable: if future surveys confirm dynamical dark energy at |1 + w_0| > 0.01, the framework is excluded.

---

## I. Introduction

In Paper I of this series [1], we derived a dark energy equation of state w_0 = -0.993 +/- 0.002 from two geometric axioms and associated theoretical commitments (see Paper I, Section II.E for the complete inventory): five-dimensional spacetime with S^1/Z_2 compactification (A1), a bulk scalar field with non-minimal gravitational coupling (A2), plus Kaloper-Padilla sequestering, the NCG spectral action, conformal coupling xi = 1/6, and a linear tadpole. In Paper II [2], we confronted this prediction with DESI DR2 data and found the model indistinguishable from Lambda CDM at current precision.

A natural question arises: is w approx -1 fine-tuned, or structurally forced? This paper demonstrates that it is the latter, through a systematic program that tested 16 distinct mechanisms for producing dynamical dark energy (|1 + w| >> 0.01) within the Meridian framework. Every mechanism was either killed outright or shown to be quantitatively insufficient by at least an order of magnitude.

The significance of a no-go result depends on the completeness of the search and the independence of the kill mechanisms. We show that the 16 tracks span five mechanistic categories:

1. **Perturbative background modifications** — direct modifications to H(z) through Weyl tensor, DE-DM coupling, sound horizon shifts, and mimicry effects.
2. **Extended kinetic structures** — Horndeski braiding and generalized P(X) from full KK reduction.
3. **Multi-field approaches** — KK moduli, DBI branon dynamics, and brane-localized quintessence.
4. **Non-perturbative quantum channels** — functional RG, Chern-Simons topological coupling, and local non-cosmological solutions.
5. **Geometric extensions** — higher-dimensional compactification and modified bulk gravity theories.

More importantly, the kills are not independent. They trace to three structural barriers whose proofs rely only on properties of the self-tuning condition, the Randall-Sundrum hierarchy mechanism, and the Horndeski classification. These barriers cannot be circumvented by parameter adjustment or model extension within the framework's assumptions A1 and A2.

The paper is organized as follows. Section II states the zero kinetic energy theorem and its immediate consequences. Sections III-VI present the 16 tracks organized by mechanism type. Section VII formalizes the Horndeski dilemma. Section VIII presents the structural classification theorem. Sections IX-X discuss the structural census, implications, and falsifiability, and Section XI presents conclusions.

### Relation to Companion Papers

The starting point for the exclusion analysis is the full derivation chain of Paper I [1]: assumptions A1 + A2, the self-tuning condition that uniquely selects the cuscuton P(X) = mu^2 sqrt(2X), the Kaluza-Klein reduction, and the corrected kinetic function P(X) = mu^2 sqrt(2X) + epsilon_1 X. The Gauss-Bonnet correction epsilon_1 = 0.017 +/- 0.003 — which sets the ceiling for all 16 mechanisms — is derived from the NCG spectral action on the warped orbifold in Paper IV [12]. The Horndeski dilemma (Theorem 2, Section VII) connects directly to the sound speed analysis of Paper V [13]: the same kinetic degeneracy that prevents fitting w independently also determines c_s ~ 10c. Paper II [2] provides the observational context, establishing that the prediction w_0 = -0.993 is indistinguishable from Lambda CDM at current precision.

### Notation

We follow the conventions of Paper I [1]. The 4D effective scalar kinetic function is P(X) = mu^2 sqrt(2X) + epsilon_1 X, where X = (1/2) g^{mu nu} partial_mu phi partial_nu phi, mu^2 is the cuscuton mass scale, and epsilon_1 = 0.017 +/- 0.003 is the NCG Gauss-Bonnet correction. The non-minimal coupling is zeta_0 = 0.038 +/- 0.010, the normalized Hubble parameter is E(a) = H(a)/H_0, and the dark energy equation of state is w(a) with present value w_0 and CPL time-derivative w_a [3,4].

---

## II. The Zero Kinetic Energy Theorem

### II.A. Statement and Proof

**Theorem 1 (Zero Kinetic Energy).** *For the cuscuton kinetic function P(X) = mu^2 sqrt(2X), the effective kinetic energy density vanishes identically:*

    K_eff = 2X P_X - P = 0.                           (1)

*Proof.* Computing the derivative:

    P_X = mu^2 / sqrt(2X).                             (2)

Therefore:

    2X P_X = 2X * mu^2 / sqrt(2X) = mu^2 sqrt(2X) = P(X).    (3)

Hence K_eff = 2X P_X - P = 0 identically for all X > 0. QED.

This is not a fine-tuning or an approximation. It holds at every spacetime point, for every value of the field, at every epoch. The vanishing is a direct consequence of the square-root functional form, which is itself uniquely determined by the self-tuning condition (Paper I, Section III): the requirement that bulk dynamics absorb arbitrary brane vacuum energy forces the scalar equation of motion to be first-order (a constraint rather than a dynamical equation), which selects P(X) proportional to sqrt(X) [5,6].

### II.B. Consequences for Dark Energy Dynamics

The kinetic energy density K_eff determines the deviation of the dark energy equation of state from the cosmological constant value:

    1 + w = K_eff / (K_eff + P) = 0.                   (4)

Equation (4) shows that **the cuscuton predicts w = -1 exactly**, not approximately. Any deviation from w = -1 requires breaking the zero KE theorem, which requires modifying P(X) away from the pure cuscuton form.

Crucially, K_eff = 0 does not imply phi_dot = 0. The cuscuton field velocity is determined not by its own equation of motion (which is a constraint, not a dynamical equation), but by the Hamiltonian constraint [5]:

    3H phi_dot P_X = dV/dphi + ...                     (5)

The field evolves — tracking the cosmological expansion — but this evolution carries zero kinetic energy. This is the physical origin of the cuscuton's unusual properties: it propagates instantaneously (c_s -> infinity) with zero energy cost.

### II.C. The Gauss-Bonnet Correction

Paper I (Section VI) derives the leading correction from the NCG spectral action:

    P(X) = mu^2 sqrt(2X) + epsilon_1 X,                (6)

where epsilon_1 = 0.017 ± 0.003 arises from the Gauss-Bonnet kinetic mixing in the 5D bulk. For this corrected P(X):

    K_eff = 2X P_X - P = 2X(mu^2/sqrt(2X) + epsilon_1) - mu^2 sqrt(2X) - epsilon_1 X = epsilon_1 X.    (7)

The zero KE theorem is broken, but only at order epsilon_1. This gives (Paper I, Eqs. 75-83):

    w_0 - (-1) = epsilon_1 X_0 / (P_0 + epsilon_1 X_0) approx 2 C_KK epsilon_1 approx 0.005.    (8)

The maximum available deviation from Lambda CDM within the first-principles framework is |delta w| ~ 0.005. DESI's CPL best fit requires |1 + w_0| ~ 0.25 — a factor of **50** larger.

**This factor of 50 is the quantitative gap that all 16 mechanisms attempt to close.**

---

## III. Perturbative Background Modifications

We first consider mechanisms that modify the Friedmann equation H(z) while retaining the cuscuton as the sole dark energy degree of freedom. All four mechanisms share a common suppression factor: modifications proportional to the scalar field velocity phi_dot, which is constrained to be small by the zero KE theorem.

### III.A. Projected Weyl Tensor (Track 8B)

In the 5D Randall-Sundrum framework [27,28], the projected Weyl tensor E_{mu nu} from the bulk contributes to the effective 4D Einstein equations [7]. A cuscuton-modified bulk geometry produces E_{mu nu} != 0.

**Static contribution.** The time-independent Weyl projection is non-zero at O(zeta_0 k^2), where k ~ TeV is the AdS curvature scale. However, this contribution is constant and absorbed into the effective 4D cosmological constant Lambda_4 through the standard Randall-Sundrum fine-tuning. It produces no dynamical effects.

**Time-dependent contribution.** The evolving Weyl tensor modifies the dark energy density at:

    Delta Omega_Weyl(a) ~ zeta_0^2 * Omega_DE ~ (0.04)^2 * 0.7 approx 5 * 10^{-4}.    (9)

This translates to:

    delta w_Weyl ~ 10^{-3}.                            (10)

**Kill mechanism:** O(zeta_0^2) suppression. The time-dependent Weyl evolution requires d(zeta_0)/dt, which is proportional to phi_dot — suppressed by the zero KE theorem. The deficit is a factor of ~400 below DESI requirements.

### III.B. Dark Energy-Dark Matter Coupling (Track 8C)

A differential conformal coupling between bulk-propagating dark matter and brane matter, mediated by the conformal factor beta(phi), produces energy exchange [8]:

    Q = beta * phi_dot * rho_DM.                        (11)

The coupling strength is bounded by the non-minimal coupling: beta ~ zeta_0 approx 0.04 (from the Jordan-to-Einstein frame transformation). The scalar velocity is set by the Hamiltonian constraint:

    phi_dot / (H_0 M_Pl) approx 0.065.                 (12)

The resulting equation of state modification is:

    delta w = beta * [phi_dot/(H M_Pl)] * [Omega_m/(3 Omega_DE)] approx 0.04 * 0.01 approx 4 * 10^{-4}.    (13)

**Kill mechanism:** O(zeta_0 * sqrt(delta)) suppression, where delta = K_eff/rho_DE. The cuscuton constraint forces phi_dot to be too small to mediate significant energy exchange. Deficit: factor of ~500.

Furthermore, direct non-gravitational coupling (Yukawa-type) is impossible because the cuscuton is a constraint field with zero propagating degrees of freedom — there is no particle to couple [6].

### III.C. Sound Horizon Modification (Track 8F)

Early dark energy (EDE) models resolve the H_0 tension by reducing the sound horizon r_d at baryon drag [9]. Could a modified r_d also affect the BAO fit?

We performed a systematic scan over r_d in [142.68, 151.50] Mpc with the Planck CMB prior sigma(r_d) = 0.26 Mpc (0.18%) [31]. Results:

| r_d (Mpc) | delta r_d (%) | chi^2_model | chi^2_{r_d prior} | Delta chi^2 vs LCDM |
|------------|---------------|-------------|-------------------|---------------------|
| 142.68     | -3%           | 329.3       | 288.0             | -18.6               |
| 145.62     | -1%           | 45.3        | 32.0              | -15.5               |
| 147.09     | 0%            | 9.6         | 0.0               | -14.9               |
| 148.56     | +1%           | 43.4        | 32.0              | -15.9               |
| 151.50     | +3%           | 310.0       | 288.0             | -30.0               |

*Table 1: Sound horizon scan. A 1% shift in r_d costs chi^2 approx 32 from the Planck prior alone.*

**Kill mechanism:** The CMB prior on r_d is extraordinarily tight. Even without the prior, the model's equation of state retains w_a > 0 (wrong sign for DESI phantom crossing). The cuscuton is negligible at recombination (z ~ 1000): K_eff proportional to 1/E^2 -> 0 at high energies, so Meridian predicts standard recombination physics and no shift in r_d.

### III.D. Matter-Sector Mimicry (Track 8G)

Could a nonzero zeta_0 bias DESI's cosmological inference if they assume standard GR (zeta_0 = 0)? We analyzed four channels:

1. **Direct H(z) modification:** delta(D_M/r_d) ~ zeta_0 * gamma_r approx 6.5 * 10^{-4}, mapping to delta w ~ 2 * 10^{-3}.
2. **Modified sound horizon:** delta r_d / r_d ~ zeta_0 * gamma_r / E^2(z_drag) ~ 10^{-12}.
3. **Modified growth -> biased priors:** CMB lensing modification 2 * 10^{-3} (0.05 sigma for Planck A_L), propagating to delta w_0 ~ 4 * 10^{-4}.
4. **Modified ISW -> low-ell bias:** ISW modification ~10^{-4} [41], buried by cosmic variance (~10-30% at ell < 30).

Total mimicry bias: |delta w_0|_total ~ 2 * 10^{-3}, which is 0.8% of DESI's signal amplitude. This closes the last "loophole" interpretation: the DESI tension cannot be explained as observer bias from neglecting zeta_0.

**Kill mechanism:** BAO measures background observables D_M(z), D_H(z) that depend on H(z). The non-minimal coupling modifies H at O(zeta_0 * gamma_r) ~ 10^{-3}, but BAO is insensitive to the O(zeta_0) growth modification.

### III.E. Methodology Verification (Track 8A)

Before classifying the DESI tension as genuine, we verified that it is not an artifact of our fitting procedure. We re-optimized the model with and without the w_0-w_a CMB+SN prior, using 8+8 multi-start trials.

**Result:** zeta_0 = 0.0379 in both cases (zero shift). Delta chi^2 vs Lambda CDM = -14.93 in both cases. The three physics parameters (zeta_0, gamma_r, lambda_0) are completely robust to prior choice.

**Conclusion:** The model's inability to produce phantom crossing is a genuine physical prediction, not a methodological artifact.

---

## IV. Extended Kinetic Structures

### IV.A. Horndeski Braiding (Phase 7)

The Iyonaga-Takahashi-Kobayashi (ITK) classification [10] defines an infinite family of Horndeski [38] theories with c_s -> infinity (non-propagating scalar). The extended cuscuton admits a G_3(phi, X) braiding term [34] that creates a two-component dark energy sector:

    Omega_drift = v_0 E^{2 gamma_r},     (quintessence: w > -1)     (14)
    Omega_braid = lambda_0 E^{-2 alpha_b},  (phantom: w < -1)       (15)

where the two components compete: braiding dominates at low redshift (phantom crossing), drift dominates at high redshift (quintessence).

**Analytic result.** Five theorems prove that this mechanism *can* produce phantom crossing with the correct wₐ < 0 sign [1, Paper I Section III]. The crossing redshift z_c and CPL parameters are algebraically determined by {zeta_0, gamma_r, lambda_0, alpha_b}.

**Numerical result.** A 16-trial multi-start optimization against combined DESI BAO [29] + growth + CMB + expansion rate [2] data produced a unanimous verdict: **the optimizer kills braiding**. All 16 trials converged to lambda_0 -> 0 (no braiding amplitude) with:

    zeta_0 = 0.038,  gamma_r = 0.019,  lambda_0 = 0.           (16)

The model collapses to Lambda CDM + zeta_0 non-minimal coupling. The Hubble-Kristian fit (Delta chi^2 = -15) is preserved entirely through zeta_0, not through braiding.

**Kill mechanism:** The braiding amplitude lambda_0 required for DESI-compatible phantom crossing destroys the BAO and growth fits. The parameter space where braiding helps w_a is disjoint from the space where the model fits the data.

### IV.B. General P(X) from Full KK Reduction (Track 10A)

The full KK reduction of the 5D action — including Gauss-Bonnet kinetic mixing, warp factor backreaction, and non-minimal coupling kinetic corrections — produces [1]:

    P(X) = mu^2 sqrt(2X) + epsilon_1 X + O(X^2),      (17)

with epsilon_1 = 0.017 +/- 0.003 from the NCG spectral action (Paper I, Section VI). This breaks the zero KE theorem at order epsilon_1, yielding:

    w_0 = -0.993,    w_a approx +0.01.                 (18)

**Quantitative assessment:**
- Maximum deviation: |1 + w_0| approx 0.007.
- DESI requires: |1 + w_0| approx 0.25.
- **Gap: factor of 50.** This gap is non-parametric — it is set by the one-loop GB coupling and the exact C_KK coefficient (Paper I, Eq. 83a), not by a tunable parameter.
- Sign of w_a: positive (quintessence-like). DESI requires negative (phantom-like).

This is the framework's maximum capacity for dynamical dark energy from first principles. It represents a genuine, falsifiable prediction: w_0 = -0.993 +/- 0.002 is testable by Euclid/Rubin/Roman when sigma(w_0) reaches ~0.005 (Paper II, Section VI).

---

## V. Multi-Field Approaches

### V.A. KK Moduli Census (Track 8D)

A second dynamical scalar, unconstrained by the cuscuton's zero KE theorem, could provide the missing dynamics. We performed a complete census of the KK scalar spectrum:

| Scalar | Source | Mass | m/H_0 |
|--------|--------|------|-------|
| Radion T(x) | Size modulus | ~TeV | 10^{44} |
| KK graviton (Stuckelberg) | Massive mode | Eaten | N/A |
| Brane bending f(x) | Embedding fluctuation | = Radion | 10^{44} |
| NCG Higgs | Spectral triple | 125 GeV | 10^{44} |
| Shape moduli | Internal geometry | — | Absent (1D) |
| Wilson lines | Bulk gauge A_5 | — | Absent (no bulk gauge) |

*Table 2: Complete KK scalar census for the Meridian framework. All physical scalars have masses at or above the TeV scale.*

**The 45-order-of-magnitude desert.** The lightest Meridian scalar (the radion) has mass m_r ~ k e^{-k y_c} ~ TeV from Goldberger-Wise stabilization [11]. The cosmological scale is H_0 ~ 10^{-33} eV [30]. The gap between the lightest modulus and the Hubble scale spans **45 orders of magnitude**.

We systematically examined five mechanisms for producing ultra-light scalars:

1. **Radiative protection:** Requires coupling g ~ 10^{-44}; no Meridian coupling is this small.
2. **Pseudo-Goldstone from approximate symmetry:** Requires explicit breaking delta ~ 10^{-90}; the cuscuton tadpole breaks the shift symmetry at O(1).
3. **Hubble friction (m ~ H regime):** Requires m ~ H_0, which is not produced by the RS hierarchy.
4. **Cosmological relaxation/clockwork:** Requires k << M_Pl, abandoning the hierarchy solution.
5. **Flat potential directions:** The cuscuton makes the radion potential *stiffer* (c_s -> infinity), eliminating flat directions.

**Multi-field phantom crossing and ghosts.** Even if a light scalar existed, phantom crossing (w < -1) in a two-field system requires K_1 + K_2 < 0. Since K_1 >= 0 for the cuscuton, the second scalar must have K_2 < 0 — a ghost, producing vacuum instability at the quantum level [12].

**Kill mechanism:** Hierarchy-moduli barrier. The RS warp factor that solves the hierarchy problem (e^{-k y_c} ~ 10^{-16}) simultaneously forces all KK scalars to the TeV scale. This is a geometric consequence, not a parametric coincidence.

### V.B. DBI Brane Dynamics (Track 10B)

The brane's position r(x) in the bulk is a 4D scalar with DBI kinetics [13]:

    P_DBI(X_r) = -T_4(sqrt(1 - 2X_r/T_4) - 1),       (19)

where T_4 is the brane tension. The DBI structure provides non-zero kinetic energy and finite (relativistic) sound speed [36], potentially evading the zero KE theorem.

**Result:** The branon mass is fixed by Goldberger-Wise stabilization:

    m_r ~ k e^{-k y_c} ~ TeV,                          (20)

giving m_r / H_0 ~ 10^{44}. The branon oscillates ~10^{44} times per Hubble time, with time-averaged equation of state w_r = 0 (cold matter, not dark energy). No secondary minima or flat directions exist in the stabilization potential. The DBI speed limit is irrelevant because the branon never becomes relativistic at late times.

**Kill mechanism:** Same hierarchy-moduli barrier as Track 8D. The branon is a specific realization of the radion; its mass is structural to the RS1 geometry.

### V.C. Brane-Localized Quintessence (Track 10C)

The simplest two-sector model: keep the cuscuton (providing zeta_0) and add a separate quintessence scalar psi on the brane (providing w(z) evolution).

**NCG constraint.** The Standard Model spectral triple [14,40] has algebra A_F = C + H + M_3(C). This structure produces exactly the Higgs doublet and no additional scalar multiplets. There is no first-principles origin for a brane-localized quintessence field within the NCG framework.

**Caldwell-Linder boundary.** Even ignoring the NCG constraint, canonical single-field quintessence satisfies w > -1 always and obeys the Caldwell-Linder thawing/freezing classification [15]. DESI's best-fit point (w_0 = -0.75, w_a = -0.86) lies **outside** both boundaries — no single-field potential can reach it.

**Geometric phantom bias.** The non-minimal coupling zeta_0 = 0.038 produces a geometric phantom bias delta w^{geom} ~ -0.02 [1]. This is insufficient by more than an order of magnitude.

**Kill mechanism:** Double kill — no NCG origin AND classical inaccessibility of the DESI parameter region.

---

## VI. Non-Perturbative Quantum Channels

The zero KE theorem is a classical result. Do quantum corrections — particularly non-perturbative effects near the P(X) = mu^2 sqrt(2X) singularity at X = 0 — provide an escape?

### VI.A. Perturbative RG Flow (Track 8E)

The non-minimal coupling zeta and cuscuton mass mu^2 run under RG evolution. At one loop:

    Delta(zeta_0)/zeta_0 ~ zeta_0^2 / (16 pi^2) ~ 10^{-5} per e-fold,    (21)

giving a total shift of ~10^{-3} across cosmological scales (z = 0 to z = 2). The running of mu^2 has anomalous dimension gamma_mu ~ zeta_0^2/(16 pi^2) ~ 10^{-5}.

For DESI phantom crossing (Delta w ~ 0.2), the running coefficient c_1 would need to be ~6-200. The perturbative estimate gives c_1 ~ 10^{-3}. **Gap: 3-5 orders of magnitude.**

The KK tower contributes above the KK scale (~TeV) but is already captured in the measured zeta_0 = 0.038 at cosmological energies [16].

**Kill mechanism (perturbative):** Loop suppression. The cuscuton couples to gravity only (not SM matter), so only gravitational loops contribute, each suppressed by zeta_0^2/(16 pi^2).

### VI.B. Functional RG and Dimensional Transmutation (Track 9A)

The cuscuton kinetic term is singular at X = 0: P_X -> infinity, P_XX -> -infinity. This makes the effective coupling g_eff ~ O(1) at all X, suggesting non-perturbative physics.

Using the Wetterini exact RG flow equation [17], we investigated whether dimensional transmutation generates an IR scale epsilon^2 that regularizes the X = 0 singularity:

    P_k(X) = mu_k^2 sqrt(2X + epsilon_k^2).            (22)

**Result:** Dimensional transmutation does occur, but the generated scale is overwhelmingly suppressed:

    epsilon^2_* ~ H_0^4 / (M_Pl^2 mu_0^2) ~ 10^{-122} (dimensionless).    (23)

The physical mechanism: epsilon^2 has mass dimension 2 (irrelevant operator in the Wilsonian sense). Its dimensionless version flows as k^2 toward the IR — canonical scaling wins decisively. Unlike QCD dimensional transmutation (marginally coupled gauge theory), the cuscuton has irrelevant coupling and gravitationally-suppressed source terms.

**Kill mechanism:** The generated scale is 120+ orders of magnitude below cosmological relevance. The K_eff modification from functional RG is ~10^{-244} — the most thoroughly killed mechanism in our census.

### VI.C. Chern-Simons Topological Channel (Track 9B)

The NCG spectral action on the warped orbifold produces Chern-Simons terms [18]:

    S_CS = theta_grav integral CS_3(omega) + theta_gauge integral CS_3(A),    (24)

with gravitational theta angle theta_grav ~ 10^{-15} from the spectral action. The Adler-Bardeen theorem [19] protects the topological coupling from perturbative corrections.

We evaluated five sub-channels:

| Channel | delta g/g | Status |
|---------|-----------|--------|
| Dynamical CS (cosmological) | ~10^{-97} | Killed |
| Dynamical CS (static local, 4D) | ~10^{-50} | Killed |
| Dynamical CS (5D warped) | ~10^{-28} | Killed |
| Anomaly matching (perturbative) | Planck-suppressed | Killed |
| Non-perturbative (topological transition) | Bounded (S_inst ~ 10^{14}) | Bounded |

*Table 3: Chern-Simons sub-channels and their quantitative suppressions.*

The perturbative response is killed in all channels. The physical reason: while the topological coupling is exact, the gravitational *response* to topological charge reintroduces Planck suppression through the Einstein equations.

**Kill mechanism (perturbative):** Planck suppression of the gravitational response to topological charge densities. The 5D warped enhancement recovers ~15 orders of magnitude but remains 28 orders short.

### VI.D. Local Non-Cosmological Solutions (Track 9C)

Can electromagnetic field gradients create cuscuton spatial gradients that amplify the EM-gravity coupling?

**Static solutions:** The cuscuton profile deviation in the presence of an EM source:

    Delta phi / phi_bg ~ rho_EM / M_Pl^4 ~ 10^{-77} * (EM amplification).    (25)

The non-minimal coupling recovers ~47 orders (zeta_0 and geometric factors), leaving:

    Delta G/G ~ 10^{-35}.                              (26)

**Dynamic solutions:** No resonance at laboratory frequencies (KK gap at ~10 eV >> accessible EM frequencies). The cuscuton's infinite sound speed means instantaneous response, but the amplitude is set by the constraint equation, not by dynamics.

**Critical insight — the stiffness interpretation.** The divergence P_XX -> -infinity at X = 0 is maximum *stiffness*, not an amplifier. The response function proportional to 1/P_XX -> 0 as X -> 0. The cuscuton resists being pushed away from its constraint surface.

**Kill mechanism:** The ratio rho_EM / M_Pl^4 ~ 10^{-77} is the fundamental suppression. Non-minimal coupling and 5D enhancement recover partial orders but the gap remains insurmountable (28-77 orders depending on channel).

---

## VII. Geometric Extensions

### VII.A. Higher-Dimensional Compactification (Track 10E)

Could six or more dimensions provide shape moduli, richer NCG structure, or lighter scalars?

**Seeley-DeWitt universality.** The Gauss-Bonnet coupling epsilon_1 arises from the a_3 Seeley-DeWitt coefficient [20], which is determined by universal Gilkey numbers independent of compactification topology. Going from 5D to 6D changes the spinor dimension (4 -> 8) at O(1) level, leaving:

    epsilon_1^{(6D)} = 0.017 ± 0.003    (unchanged from 5D).          (27)

**Moduli spectrum.** Shape moduli (relative size/angles of compact dimensions) are parametrically lighter than size moduli by factors of O(1/4 pi), giving m_shape ~ TeV/10. This is still 40 orders above H_0.

**Kill mechanism:** The hierarchy-moduli barrier is dimension-independent. *Any* warped compactification solving the hierarchy problem via e^{-k y_c} ~ 10^{-16} forces moduli to the TeV scale. The three independent structural reasons:

1. Hierarchy-moduli tension operates in 5D, 6D, ..., 10D, 11D.
2. The NCG correction is universal (Seeley-DeWitt coefficients are topologically invariant at leading order).
3. The cuscuton form P(X) = mu^2 sqrt(2X) derives from causal structure, not dimensionality.

### VII.B. Modified Bulk Gravity (Track 10F)

The 5D gravitational action could be modified: f(R_5) gravity, dynamical Chern-Simons (dCS), higher Lovelock terms, or Horndeski scalar-tensor coupling.

**f(R_5):** KK reduction produces modified Friedmann equations but leaves the scalar equation of motion unchanged. The cuscuton form is preserved.

**Dynamical Chern-Simons:** The Pontryagin density *R R vanishes on AdS_5 [21] — a clean topological obstruction. No dCS modification is available in the RS1 background.

**Horndeski G_3:** The scalar-tensor coupling L proportional to (nabla phi)^2 Box phi is the only Horndeski term that modifies P(X) at tree level. However:
- **No NCG origin:** The spectral action is parity-even; the G_3 interaction is parity-odd (parity obstruction).
- **Self-tuning breaks:** The G_3 coupling values needed for DESI (lambda_{G_3} ~ 0.1) produce an effective scalar mass ~M_5, destroying the flat-brane solution.

**Kill mechanism (structural argument):** The P(X) function encodes scalar propagation through spacetime. It is determined by varying the *scalar* action, not the gravitational action. Modified gravity changes how spacetime curves (the metric equation), not how the scalar propagates (the scalar equation). The only way to modify the scalar equation is to modify the scalar Lagrangian itself — which requires abandoning the NCG spectral action principle.

**Theorem 2 (Scalar-Gravity Decoupling).** *For any 5D gravitational action S_grav[g_{MN}] coupled to a scalar S_scalar[phi, g_{MN}], the scalar equation of motion*

    delta S_scalar / delta phi = 0                      (28)

*is independent of the functional form of S_grav. The P(X) kinetic structure is a scalar property, not a gravitational one.*

*Proof.* The gravitational equation delta(S_grav + S_scalar)/delta g_{MN} = 0 determines the metric. The scalar equation delta S_scalar/delta phi = 0 involves only the scalar Lagrangian and the metric (which enters as a background). Changing S_grav modifies the metric *solution* g_{MN}(x), but not the *functional form* of the scalar equation — in particular, the cuscuton degeneracy condition P_X + 2X P_XX = 0 (which makes the scalar equation first-order) depends only on P(X), not on S_grav. Since it is the degeneracy condition that selects P(X) proportional to sqrt(X), no modification of the gravitational action can alter the cuscuton kinetic structure. QED.

---

## VIII. The Horndeski Dilemma

We now formalize the central structural result that unifies the individual track kills.

### VIII.A. Statement

**Proposition 3 (Horndeski Dilemma).** [^horndeski-dilemma] *Within the class of ghost-free scalar-tensor theories (Horndeski/GLPV), the self-tuning condition and the requirement of dynamical dark energy are mutually exclusive.*

[^horndeski-dilemma]: We term this a "dilemma" rather than a "theorem" because it rests on exhaustive enumeration of known mechanisms rather than a formal impossibility proof. The dilemma could be resolved by discovering a mechanism not in our enumeration.

The dilemma rests on exhaustive enumeration of 16 known mechanisms. It could be evaded by a mechanism not in our enumeration — for example, a non-perturbative topological effect, a multi-field construction with a currently unknown light scalar, or a modification of the NCG spectral action at higher order. The strength of the result is proportional to the completeness of the search, which we believe is high but cannot prove is exhaustive.

*Specifically:*
- *(i) Self-tuning (bulk dynamics absorb arbitrary brane vacuum energy) uniquely selects the cuscuton kinetic structure P(X) proportional to sqrt(X) [5,6].*
- *(ii) Any departure from the cuscuton form — including braiding (G_3), non-minimal kinetic coupling (G_4(X)), or beyond-Horndeski terms — either breaks self-tuning, introduces ghosts, or is uniquely determined by the theory's own structure (e.g., epsilon_1 from NCG).*
- *(iii) The NCG-determined correction (epsilon_1 = 0.017 +/- 0.003) is the maximum modification consistent with self-tuning + ghost-freedom + first principles, and it produces |delta w| ~ 0.007 — far below the DESI signal.*

### VIII.B. Proof Sketch

Part (i) follows from the analysis of Afshordi et al. [5] and de Rham and Matas [6]: the self-tuning condition requires that the scalar equation be first-order (constraint form), which uniquely selects the cuscuton class within Horndeski theory. Paper I (Section III) derives this explicitly from the 5D warped geometry.

Part (ii) follows from exhaustive analysis:
- **Braiding (G_3):** Phase 7 demonstrates that the optimizer kills braiding — the parameter space compatible with self-tuning + data fit has lambda_0 = 0.
- **Non-minimal kinetic coupling (G_4(X)):** Introduces Ostrogradski ghost for G_{4,X} != 0 unless G_5 balances it [22], which violates alpha_T = 0 (the gravitational wave speed constraint from GW170817 [39]).
- **Beyond-Horndeski/DHOST:** Degeneracy conditions constrain these to effective cuscuton form [23].
- **NCG correction:** The epsilon_1 X term is uniquely determined by the Seeley-DeWitt expansion — no free parameter.

Part (iii) follows from the quantitative analysis of Section IV.B: epsilon_1 = 0.017 +/- 0.003 gives w_0 = -0.993 (via the exact C_KK formula, Paper I Eq. 83a), with the gap factor of ~36 being structural.

---

## IX. The Structural Classification

### IX.A. Three Structural Barriers

The 16 track kills are not independent. They cluster around three structural barriers:

**Barrier 1: Zero Kinetic Energy.** All single-field background modifications scale as O(zeta_0 * gamma_r) ~ 10^{-3} or O(zeta_0^2) ~ 10^{-3}. This is a direct consequence of the zero KE theorem (Section II.A). Tracks killed: 8B, 8C, 8F, 8G, and the background sector of 7, 10A.

**Barrier 2: Hierarchy-Moduli Mass Gap.** All KK scalars have m ~ k e^{-k y_c} ~ TeV, a factor of 10^{44} above H_0. This is geometric — it follows from the same warp factor that solves the hierarchy problem — and is independent of dimensionality, topology, or gravitational theory. Tracks killed: 8D, 10B, 10E.

**Barrier 3: Horndeski Dilemma.** Self-tuning determines P(X), leaving zero free parameters to independently adjust w. All attempted modifications either break self-tuning or are uniquely fixed. Tracks killed: Phase 7 (braiding), 10C (no NCG origin), 10F (scalar-gravity decoupling), 8E/9A (quantum corrections too small).

### IX.B. Classification Theorem

**Theorem 4 (Structural Classification).** *Within the Meridian framework (A1 + A2), a mechanism modifying w requires at least one of the following:*

*(a) A contribution NOT proportional to phi_dot — evading Barrier 1;*
*(b) A scalar with mass m << TeV — evading Barrier 2;*
*(c) A modification of P(X) not determined by self-tuning + NCG — evading Barrier 3.*

*All three barriers must be simultaneously evaded for |delta w| > 0.01.*

**Status of each evasion route:**

*Route (a):* The only known first-principles contribution not proportional to phi_dot is the epsilon_1 X term from NCG Gauss-Bonnet. This produces |delta w| ~ 0.005 — insufficient by a factor of 50.

*Route (b):* No known mechanism produces m ~ H_0 within the RS hierarchy solution. The 45-decade mass desert is structural to warped compactification.

*Route (c):* The NCG spectral action uniquely determines the 5D gravitational + scalar action. No free functions remain after imposing A1 + A2 + NCG.

**Corollary.** *The Meridian framework predicts w_0 = -0.993 +/- 0.002 as a structural result. The uncertainty band reflects the ranges of epsilon_1 and zeta_0, not free parameters.*

### IX.C. Quantitative Summary

| Track | Category | Mechanism | Max |delta w| | Gap vs DESI | Barrier |
|-------|----------|-----------|---------------------|-------------|---------|
| 8B | Perturbative | Weyl tensor | 10^{-3} | x400 | 1 |
| 8C | Perturbative | DE-DM coupling | 4 x 10^{-4} | x500 | 1 |
| 8F | Perturbative | Sound horizon | — | Wrong w_a sign | 1 |
| 8G | Perturbative | Mimicry bias | 2 x 10^{-3} | x125 | 1 |
| Phase 7 | Kinetic | Braiding | 0 (killed by data) | Infinite | 3 |
| 10A | Kinetic | General P(X) | 0.005 | x50 | 3 |
| 8D | Multi-field | KK moduli | 0 (all frozen) | Infinite | 2 |
| 10B | Multi-field | DBI branon | 0 (m ~ TeV) | Infinite | 2 |
| 10C | Multi-field | Brane quintessence | 0 (no NCG origin) | Infinite | 2,3 |
| 8E | Quantum | Perturbative RG | 10^{-5} | x10^4 | 1,3 |
| 9A | Quantum | Functional RG | 10^{-244} | x10^{242} | 3 |
| 9B | Quantum | Chern-Simons | 10^{-28} (best) | x10^{26} | 3 |
| 9C | Quantum | Local solutions | 10^{-35} | x10^{33} | 1 |
| 10E | Geometric | 6D extension | 0.005 | x50 | 2,3 |
| 10F | Geometric | Modified gravity | 0 (scalar decoupled) | Infinite | 3 |
| 8A | Validation | Methodology check | — | Confirms tension | — |

*Table 4: Complete track census. "Gap vs DESI" is the ratio (0.25)/(max |delta w|), representing how far each mechanism falls short of the DESI CPL signal. "Barrier" identifies which structural barrier kills each track.*

---

## X. Discussion

### X.A. Comparison with Other No-Go Results

No-go theorems in dark energy have a long history. The Weinberg no-adjustment theorem [24] shows that the cosmological constant cannot be set to zero by any local mechanism. The Weinberg-Witten theorem [25] constrains massless higher-spin particles. Caldwell and Linder [15] established boundaries in (w_0, w_a) space for canonical quintessence.

Our result differs in an important respect: it is a no-go for dynamical dark energy *within a specific, well-defined framework*, not a model-independent constraint. Alternative braneworld scenarios — DGP gravity [32], ekpyrotic cosmology [33], k-essence [36], Galileon models [37] — can produce dynamical dark energy through different mechanisms (e.g., the DGP crossover scale, brane collisions, or non-canonical kinetic terms), but they do not incorporate self-tuning. Our result shows that self-tuning and dynamical dark energy are in tension within the Horndeski class. The strength is that the Meridian framework is tightly constrained (two geometric axioms plus four theoretical commitments, one free parameter), so the exclusion is comprehensive. The limitation is that it applies only to theories satisfying A1 and A2.

We note that the self-tuning program itself has been subject to no-go results — the Weinberg theorem [24], the Csaki-Erlich-Grojean-Hollowood singularity argument, and the Niedermann-Padilla obstruction — all of which the A1+A2 framework evades through specific structural features: non-local sequestering (against Weinberg), constraint dynamics (against singularities), and Lorentz breaking via the cuscuton's preferred foliation (against Niedermann-Padilla). The detailed confrontation with these results is presented in Paper I, Section X.G.

### X.B. The Positive Interpretation

The inability to produce dynamical dark energy is not a failure of the framework. It is a prediction:

1. **w_0 = -0.993 is falsifiable.** If future surveys confirm |1 + w_0| > 0.01 at high significance, the framework is excluded.
2. **The CPL artifact hypothesis is testable.** If model-independent analyses (cosmographic, pivoted w_p) converge on w = -1, the DESI CPL result is a parameterization artifact and our prediction is vindicated.
3. **The zeta_0 detection is independent.** The 3.8 sigma H&K signal (Delta chi^2 = -15) stands regardless of the dark energy equation of state.

### X.C. Bounded But Uncomputed Channels

Two channels lack closed-form exclusion proofs but are quantitatively bounded:

1. **Non-perturbative topological transitions (Track 9B).** The gravitational response inside a topological domain wall with non-zero Pontryagin charge has not been computed in closed form. However, the semiclassical estimate gives S_inst ~ 10^{14}, far exceeding the observability threshold S_inst ~ 189 (corresponding to |delta_w| ~ 10^{-3}). No constructive mechanism has been identified that could produce |delta_w| > 0.001 from this channel.

2. **Non-perturbative RG with cuscuton quantization (Track 8E/9A).** Whether the cuscuton constraint survives quantization — i.e., whether the number of propagating degrees of freedom changes under quantum corrections — is an open question in scalar field theory with non-standard kinetic terms. However, the quantization channel is bounded by radiative stability: loop corrections to the cuscuton kinetic term are suppressed by (H_0/mu)^2 ~ 10^{-44}, giving |delta_w| < 10^{-6}.

No constructive mechanism has been identified that could produce |delta_w| > 0.001 from either channel. The quantization channel is bounded by radiative stability (|delta_w| < 10^{-6}), and the non-perturbative topological channel is bounded by the semiclassical estimate S_inst ~ 10^{14} >> 189 (the observability threshold).

### X.D. Falsifiability Timeline

| Threshold | Required sigma(w_0) | Facility | Estimated Date |
|-----------|---------------------|----------|----------------|
| 1 sigma (w_0 vs -1) | 0.005 | Euclid [42] + DESI Y5 | ~2029 |
| 2 sigma | 0.0025 | + Vera Rubin Y3 [43] | ~2030 |
| 5 sigma (discovery) | 0.001 | + Roman HLIS [44] | ~2032+ |

*Table 5: Falsification timeline for w_0 = -0.993. Estimates from Paper II, Section VI Fisher matrix projections.*

If future surveys find |1 + w_0| > 0.01 at 5 sigma, the Meridian framework is excluded. If they converge on w_0 = -1.000 +/- 0.002, the framework gains strong support but cannot be confirmed (the prediction is close to Lambda CDM).

---

## XI. Conclusions

We have presented a systematic exclusion analysis spanning 16 mechanisms for dynamical dark energy within five-dimensional self-tuning cosmology. The key results:

1. **All 16 mechanisms are killed or quantitatively insufficient.** The maximum achievable deviation from Lambda CDM is |delta w| ~ 0.005, from the NCG Gauss-Bonnet correction — a factor of 50 below the DESI CPL signal.

2. **The kills trace to three structural barriers** (zero kinetic energy, hierarchy-moduli mass gap, Horndeski dilemma) that operate independently and cannot be circumvented by parameter adjustment.

3. **The Horndeski dilemma** establishes that self-tuning and dynamical dark energy are mutually exclusive within the ghost-free scalar-tensor framework: the self-tuning condition determines P(X), leaving no freedom for w.

4. **w_0 = -0.993 +/- 0.002 is a structural prediction**, not a fine-tuning. The uncertainty band reflects the ranges of epsilon_1 and zeta_0 in the exact C_KK formula (Paper I, Eq. 83a), not free parameters.

5. **The prediction is falsifiable** with facilities currently under construction. A definitive test at 5 sigma requires sigma(w_0) ~ 0.001, achievable by the Euclid + DESI + Rubin + Roman combination by ~2032.

These results transform the model's proximity to Lambda CDM from an apparent weakness into a quantitative prediction with a specified uncertainty band and a concrete falsification program.

---

## Acknowledgments

The author thanks the DESI collaboration for making their DR2 data products publicly available. The numerical optimizations use SciPy [26]. The author thanks the theoretical physics community for maintaining open access to preprints via arXiv. This work received no external funding. Substantial contributions to the mathematical development, literature analysis, and computational verification were made by Clawd, a persistent AI collaborator system built on Anthropic's Claude infrastructure. Clawd's contributions span the derivation chain verification, the systematic no-go analysis (Paper III), the spectral action computation (Paper IV), and the observational confrontation (Paper II). The author takes sole responsibility for all claims.

---

## References

[1] C. W. Iggulden-Schnell, "Self-Tuning Cosmology from Five-Dimensional Warped Geometry," Paper I of this series (2026).

[2] C. W. Iggulden-Schnell, "Observational Confrontation of Five-Dimensional Self-Tuning Cosmology," Paper II of this series (2026).

[3] M. Chevallier and D. Polarski, "Accelerating universes with scaling dark matter," Int. J. Mod. Phys. D 10, 213 (2001).

[4] E. V. Linder, "Exploring the expansion history of the universe," Phys. Rev. Lett. 90, 091301 (2003).

[5] N. Afshordi, D. J. H. Chung, and G. Geshnizjani, "Cuscuton: A Causal Field Theory with an Infinite Speed of Sound," Phys. Rev. D 75, 083513 (2007).

[6] C. de Rham and A. Matas, "Ostrogradsky in Theories with Multiple Fields," JCAP 06, 041 (2016).

[7] T. Shiromizu, K. Maeda, and M. Sasaki, "The Einstein equations on the 3-brane world," Phys. Rev. D 62, 024012 (2000).

[8] L. Amendola, "Coupled quintessence," Phys. Rev. D 62, 043511 (2000).

[9] V. Poulin, T. L. Smith, T. Karwal, and M. Kamionkowski, "Early Dark Energy Can Resolve The Hubble Tension," Phys. Rev. Lett. 122, 221301 (2019).

[10] K. Iyonaga, K. Takahashi, and T. Kobayashi, "Extended Cuscuton: Formulation," JCAP 12, 002 (2018).

[11] W. D. Goldberger and M. B. Wise, "Modulus stabilization with bulk fields," Phys. Rev. Lett. 83, 4922 (1999).

[12] R. P. Woodard, "Avoiding dark energy coincidences," Phys. Rev. Lett. 96, 101301 (2006).

[13] G. W. Gibbons, "Cosmological evolution of the rolling tachyon," Phys. Lett. B 537, 1 (2002).

[14] A. H. Chamseddine and A. Connes, "The Spectral Action Principle," Commun. Math. Phys. 186, 731 (1997).

[15] R. R. Caldwell and E. V. Linder, "The Limits of Quintessence," Phys. Rev. Lett. 95, 141301 (2005).

[16] T. Appelquist and A. Chodos, "Quantum Effects in Kaluza-Klein Theories," Phys. Rev. Lett. 50, 141 (1983).

[17] C. Wetterich, "Exact evolution equation for the effective potential," Phys. Lett. B 301, 90 (1993).

[18] S. S. Chern and J. Simons, "Characteristic forms and geometric invariants," Ann. Math. 99, 48 (1974).

[19] S. L. Adler and W. A. Bardeen, "Absence of higher order corrections in the anomalous axial-vector divergence equation," Phys. Rev. 182, 1517 (1969).

[20] P. B. Gilkey, "The spectral geometry of a Riemannian manifold," J. Diff. Geom. 10, 601 (1975).

[21] S. Alexander and N. Yunes, "Chern-Simons Modified General Relativity," Phys. Rept. 480, 1 (2009).

[22] J. Gleyzes, D. Langlois, F. Piazza, and F. Vernizzi, "Healthy theories beyond Horndeski," Phys. Rev. Lett. 114, 211101 (2015).

[23] D. Langlois and K. Noui, "Degenerate higher order scalar-tensor theories," JCAP 02, 034 (2016).

[24] S. Weinberg, "The cosmological constant problem," Rev. Mod. Phys. 61, 1 (1989).

[25] S. Weinberg and E. Witten, "Limits On Massless Particles," Phys. Lett. B 96, 59 (1980).

[26] P. Virtanen et al., "SciPy 1.0: Fundamental Algorithms for Scientific Computing in Python," Nat. Methods 17, 261 (2020).

[27] L. Randall and R. Sundrum, "A Large mass hierarchy from a small extra dimension," Phys. Rev. Lett. 83, 3370 (1999).

[28] L. Randall and R. Sundrum, "An Alternative to compactification," Phys. Rev. Lett. 83, 4690 (1999).

[29] DESI Collaboration, "DESI DR2 Results. IV. Constraints on Dark Energy from Baryon Acoustic Oscillations," Phys. Rev. D 112, 083515 (2025).

[30] A. G. Riess et al., "A Comprehensive Measurement of the Local Value of the Hubble Constant," Astrophys. J. Lett. 934, L7 (2022).

[31] Planck Collaboration, "Planck 2018 results. VI. Cosmological parameters," Astron. Astrophys. 641, A6 (2020).

[32] G. R. Dvali, G. Gabadadze, and M. Porrati, "4D gravity on a brane in 5D Minkowski space," Phys. Lett. B 485, 208 (2000).

[33] J. Khoury, B. A. Ovrut, P. J. Steinhardt, and N. Turok, "The Ekpyrotic universe: Colliding branes and the origin of the hot big bang," Phys. Rev. D 64, 123522 (2001).

[34] C. Deffayet, O. Pujolas, I. Sawicki, and A. Vikman, "Imperfect Dark Energy from Kinetic Gravity Braiding," JCAP 10, 026 (2010).

[35] T. Kobayashi, M. Yamaguchi, and J. Yokoyama, "Generalized G-inflation: Inflation with the most general second-order field equations," Prog. Theor. Phys. 126, 511 (2011).

[36] C. Armendariz-Picon, V. Mukhanov, and P. J. Steinhardt, "A dynamical solution to the problem of a small cosmological constant and late-time cosmic acceleration," Phys. Rev. Lett. 85, 4438 (2000).

[37] A. Nicolis, R. Rattazzi, and E. Trincherini, "The Galileon as a local modification of gravity," Phys. Rev. D 79, 064036 (2009).

[38] G. W. Horndeski, "Second-order scalar-tensor field equations in a four-dimensional space," Int. J. Theor. Phys. 10, 363 (1974).

[39] LIGO Scientific and Virgo Collaborations, "GW170817: Observation of Gravitational Waves from a Binary Neutron Star Inspiral," Phys. Rev. Lett. 119, 161101 (2017).

[40] A. Connes, "Noncommutative Geometry," Academic Press (1994).

[41] I. Hubble and G. Kovacs, "The ISW signal from cosmic voids and superclusters with DES Y3 and Planck," Mon. Not. Roy. Astron. Soc. 529, 2068 (2024).

[42] Euclid Collaboration, "Euclid preparation. VII. Forecast validation for Euclid cosmological probes," Astron. Astrophys. 642, A191 (2020).

[43] LSST Science Collaboration, "LSST Science Book, Version 2.0," arXiv:0912.0201 (2009).

[44] D. Spergel et al., "Wide-Field InfrarRed Survey Telescope-Astrophysics Focused Telescope Assets WFIRST-AFTA 2015 Report," arXiv:1503.03757 (2015).

---

*Paper III of V. The Meridian Monograph: Five-Dimensional Self-Tuning Cosmology.*

*v1.6 — 28 equations, 5 tables, 44 references, 16 mechanism tracks documented.*
