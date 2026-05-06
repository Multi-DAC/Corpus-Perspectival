# Track 15G: The Coincidence Problem Revisited

**Date:** March 18, 2026
**Authors:** Clayton W. Iggulden-Schnell & Clawd
**Status:** COMPLETE
**Computation:** `15G_computation.py` -> `15G_coincidence_results.json`
**Prerequisite:** 14D (coincidence computation), 15E (radion inflation), 15F (DESI DR2 confrontation)

---

## 0. Executive Summary

Phase 14D established that the coincidence problem is **ameliorated but not solved** by the Meridian framework. The KK correction kappa_0/E^2(z) grows monotonically toward the present, shifting matter-DE equality by +12.2% (JC benchmark), and the NCG-determined eps_1 = 0.017 places |1+w(0)| = 0.245 in a detectable window. But the fundamental question --- why Omega_DE ~ Omega_m at the present epoch --- was left open.

This track revisits the coincidence problem with the full arsenal of Phase 15 results: radion dynamics (15E), the KK spectrum (15A-15D), the spectral action structure (14A.2, 15A), and three external sources (PIRSA 14070030, Kim et al. 2023, Shimon 2024).

**The verdict is unchanged: the coincidence problem remains ameliorated but not solved.** None of the Phase 15 ingredients provide a dynamical mechanism that links the dark energy onset to the matter domination epoch. However, the analysis clarifies exactly what Meridian contributes and identifies a compatible three-layer resolution.

**What we found:**

| New ingredient | Helps? | Reason |
|---------------|--------|--------|
| Radion dynamics (15E) | No | Radion stabilized at T ~ 500 GeV, 12 orders of magnitude above coincidence epoch |
| KK tower effects (15A-15D) | No | Boltzmann-suppressed; virtual corrections negligible (delta_rho/rho_DE ~ 10^-51) |
| Spectral action cutoff | No | UV scale (10^18 GeV), no IR dynamical link to H_0 |
| Self-tuning attractor timescale | No | Algebraic (instantaneous junction conditions), not dynamical |
| Cuscuton tracker solution | No | Infinite sound speed prevents tracking; eps_1 correction gives stiff matter (w >> 1) |
| Hierarchy connection (rho_DE ~ m_KK^4) | No | rho_DE / m_KK^4 ~ 10^-18 for Meridian benchmark (still huge hierarchy) |
| PIRSA NMC trigger | No | Cuscuton responds instantly to R; no triggering delay |
| Kim holographic interaction | No | Requires DE-DM coupling absent in framework |
| Shimon observational selection | **Yes (partial)** | Compatible complement to dynamical amelioration |

---

## 1. Introduction: The Problem in Three Parts

The "cosmological constant problem" is actually three nested problems:

1. **The old CC problem (magnitude):** Why is Lambda_4 ~ 10^-122 M_Pl^4 instead of O(M_Pl^4) from quantum corrections?

2. **The new CC problem (coincidence):** Why is rho_DE ~ rho_m at the present epoch? In LCDM, Lambda is a constant while rho_m ~ a^-3 falls through it at one specific moment --- now. The probability of observing this coincidence in a random epoch is of order Omega_DE/Omega_m ~ 2, which selects a narrow window.

3. **The dynamical question:** Is dark energy actually dynamical (w != -1), and if so, does the dynamics itself provide a mechanism linking the DE onset to structure formation?

Meridian's position on each:
- Problem 1: **SOLVED.** Self-tuning through Israel junction conditions removes Lambda_5-dependence to 15 significant figures across 60 orders of magnitude (Phase 13G). The 4D cosmological constant is set by brane parameters (zeta_0, eps_1), not by bulk vacuum energy.
- Problem 2: **AMELIORATED** (Phase 14D, this track). The KK correction makes DE dynamical, but the ratio Omega_DE/Omega_m is still an input.
- Problem 3: **YES** --- w(z) = -1 + 2*kappa_0/(Omega_DE * E^2(z)) is a genuine prediction, confirmed by DESI at the 1.8-sigma level vs CPL (15F).

This track focuses exclusively on Problem 2.

---

## 2. Review of 14D Results

Track 14D (March 18, 2026) established the following quantitative picture.

### 2.1 The KK correction

The Meridian equation of state:

    w(z) = -1 + 2*kappa_0 / [Omega_DE * E^2(z)]

where kappa_0 = C_KK * Omega_DE / (2*zeta_0) and E^2(z) = Omega_m*(1+z)^3 + Omega_DE.

At the JC benchmark (zeta_0 = 0.001):
- kappa_0 = 0.084
- w(0) = -0.755, |1+w(0)| = 0.245
- The correction is 12.3% of Omega_DE at z = 0

### 2.2 Key 14D findings

1. **Monotonic growth.** kappa_0/E^2(z) grows as E(z) decreases (universe expands). The deviation from LCDM is largest at z = 0 and diminishes toward high z. At z = 5, |1+w| = 0.004.

2. **z_eq shift.** Matter-DE equality shifts from z = 0.296 (LCDM) to z = 0.332 (Meridian JC), a +12.2% change. The effective DE density grows at late times due to the KK correction.

3. **No independent timescale.** The inflection of the correction rate occurs at z_infl = 0.028, locked to z_eq by the universal ratio (1+z_infl)/(1+z_eq) = 2^{-1/3}. The KK correction does not introduce a new cosmological clock --- it amplifies the existing matter-DE transition.

4. **eps_1 Goldilocks zone.** The spectral action's eps_1 = 0.017 gives |1+w(0)| = 0.245 at JC benchmark. If eps_1 were 10x smaller, the deviation would be undetectable (|1+w| = 0.025). If 10x larger, the linearized treatment breaks down. The actual eps_1 is 4.1x below the O(1) threshold (eps_1^crit = 0.069 for JC).

5. **Verdict.** The coincidence is softened (DE is dynamical, not static; the transition is smooth over 89% of cosmic time since z = 10) but not explained (Omega_DE/Omega_m ~ 2 is still an input, not a prediction).

### 2.3 What 14D identified as paths forward

1. Tracker behavior from the full P(X) Lagrangian
2. Structural hierarchy constraint from the 5D stabilization
3. Multi-field dynamics (radion + cuscuton)

Phase 15 provides the tools to evaluate all three.

---

## 3. New Ingredients from Phase 15

### 3.1 Radion Dynamics (15E)

Track 15E established the complete radion cosmology:

- **Inflation:** The Kahler modulus drives alpha = 1 attractor inflation (n_s = 0.964, r = 0.004)
- **Stabilization:** Goldberger-Wise potential traps the radion at Lambda_r = 509 GeV (Meridian benchmark) or 3761 GeV (RS1 benchmark)
- **Reheating:** Efficient decay through trace anomaly, T_reh ~ 10^8 - 10^10 GeV

**Question:** Does the radion stabilization timescale connect to matter-radiation equality?

**Answer: No.** The Goldberger-Wise stabilization occurs at T ~ Lambda_r ~ 500 GeV (electroweak era). Matter-radiation equality occurs at T ~ 0.75 eV. These scales are separated by ~12 orders of magnitude in temperature. The radion is frozen at its minimum long before the coincidence epoch.

Quantitatively:
- Radion mass: m_r ~ 200 GeV
- Hubble rate at GW stabilization: H(T ~ 500 GeV) ~ T^2/M_Pl ~ 10^-13 GeV
- Ratio m_r/H ~ 2 x 10^15: radion oscillations damp in a tiny fraction of one Hubble time

The radion does not have residual dynamics at late times. It is exponentially frozen at the GW minimum. No radion-cuscuton coupling operates during the matter-dominated era.

### 3.2 KK Tower Effects (15A-15D)

The full KK spectrum from the RS orbifold:
- First KK graviton: m_KK1 = pi * k * exp(-ky_c) = 2 x 10^-7 GeV (Meridian benchmark with k = 10^8 GeV)
- KK modes at T_CMB: Boltzmann suppression exp(-m_KK/T) = exp(-10^6) ~ 0

Virtual (loop-level) KK corrections to the DE density:
- delta_rho_KK ~ m_KK^4 * (H/m_KK)^2 ~ 10^-98 GeV^4
- rho_DE ~ 2.5 x 10^-47 GeV^4
- delta_rho_KK / rho_DE ~ 10^-51

KK modes are negligible in both real and virtual contributions to the late-universe energy budget. They cannot link dark energy onset to structure formation.

### 3.3 Spectral Action Running

The Chamseddine-Connes spectral action has a cutoff Lambda_SA as its fundamental energy scale. The action is:

    S = Tr(f(D^2/Lambda_SA^2))

where f is a test function and D is the Dirac operator.

**Question:** Does Lambda_SA provide a dynamical mechanism linking Lambda_cc to H_0?

**Answer: No.** Lambda_SA is a UV scale (~M_Pl or Lambda_GUT), separated from H_0 by 60 orders of magnitude. The spectral action is expanded in powers of 1/Lambda_SA^2, and the low-energy effective action is independent of Lambda_SA at leading order (the coefficients are topological invariants of the spectral triple, not functions of Lambda_SA). There is no running of Lambda_SA with cosmological time. The connection between UV (spectral action) and IR (H_0) is entirely through the brane parameters, which are inputs, not predictions.

### 3.4 Self-Tuning Attractor Dynamics

Track 14N proved the self-tuning is the unique Omega_5-cancellation mechanism within the framework. Phase 13G confirmed it to 15 significant figures.

**Question:** Does the APPROACH to the self-tuned value have a timescale that naturally coincides with matter domination?

**Answer: No --- the question is misconceived.** The self-tuning is not dynamical in the usual sense. The Israel junction conditions (Eqs. 46a-b) are algebraic constraint equations that hold instantaneously at every cosmic epoch. Phi_0 is determined by the fixed brane parameters (sigma_UV, alpha_UV, mu^2). There is no "approach" --- the brane scalar is always at its self-tuned value.

What IS dynamical is the kappa_0/E^2(z) correction to the effective equation of state. But this dynamics is driven entirely by the Hubble expansion rate E(z), not by any internal relaxation of the self-tuning mechanism. The correction grows because E(z) decreases, not because the cuscuton is relaxing toward an attractor.

This distinction matters: the self-tuning does not introduce a new dynamical timescale. The only timescale is the Hubble rate, which is already the timescale of the coincidence problem.

---

## 4. Analysis of Proposed Mechanisms

### 4.1 Tracker Solution in the Cuscuton Sector

14D identified this as the most promising path: does the Lagrangian P(X) = mu^2*sqrt(2X) + eps_1*X admit scaling solutions where rho_DE tracks rho_m?

**Analysis:**

Standard tracking (Steinhardt, Wang, Zlatev 1999) requires:
1. The field's equation of state w_phi mimics w_background during the relevant epoch
2. Gamma = V*V_{phiphi}/V_phi^2 > 1 (sufficiently steep potential)
3. The field rolls slowly enough to track but fast enough to adjust

For the cuscuton:
- **Zero kinetic energy condition:** 2X*P_X - P = 0 for P = mu^2*sqrt(2X). The cuscuton carries no energy in the kinetic sector. It cannot track because it has no inertia.
- **Sound speed:** c_s^2 = P_X / (P_X + 2X*P_XX) = (mu^2/sqrt(2X) + eps_1) / eps_1 >> 1. The field responds instantaneously, which is the opposite of the slow response needed for tracking (trackers require underdamped oscillation; the cuscuton is infinitely overdamped).

With the eps_1 correction:
- The kinetic energy is rho_kinetic = 2*eps_1*X (from the canonical piece)
- The equation of state: w_phi = P/(2X*P_X - P) = (mu^2*sqrt(2X) + eps_1*X)/(2*eps_1*X) ~ mu^2/(2*eps_1*sqrt(2X)) >> 1
- This is **stiff matter** (w >> 1), which dilutes as a^{-3(1+w)} --- faster than radiation (w = 1/3). The kinetic contribution redshifts away catastrophically fast.

**Conclusion:** No tracker solution exists in the cuscuton sector. The cuscuton's infinite sound speed and zero kinetic energy are structurally incompatible with tracking. The eps_1 correction makes tracking worse, not better, by introducing a stiff-matter component that dilutes rapidly.

### 4.2 Structural Hierarchy Connection

**Question:** Does the same warping k*y_c ~ 35 that produces the Planck/TeV hierarchy also fix Omega_DE/Omega_m?

**Analysis:**

The RS hierarchy mechanism: M_Pl/M_TeV ~ exp(k*y_c). With k*y_c = 35: M_Pl/M_TeV ~ 10^15.

For this to explain the coincidence, we would need rho_DE ~ m_KK^4 ~ (k*exp(-ky_c))^4. This would mean the dark energy density is set by the KK scale.

Numerically (Meridian benchmark, k = 10^8 GeV):
- Lambda_DE = rho_DE^{1/4} = 2.24 meV
- m_KK ~ k*exp(-ky_c) = 6.3 x 10^-8 GeV = 0.063 eV
- rho_DE / m_KK^4 = 1.6 x 10^-18

Even with Meridian's lower curvature scale (k = 10^8 instead of M_Pl), the dark energy density is 18 orders of magnitude below m_KK^4. The hierarchy mechanism does not extend to the cosmological constant. The warping that explains M_Pl/M_TeV is entirely insufficient to explain M_Pl^4/rho_DE.

For RS1 (k ~ M_Pl, m_KK ~ TeV):
- m_KK^4 ~ 10^12 GeV^4
- rho_DE ~ 10^-47 GeV^4
- rho_DE / m_KK^4 ~ 10^-59

The ratio is even worse. The self-tuning handles the magnitude (absorbing the 10^{120} bulk contribution), but the residual value rho_DE = eps_1 * zeta_0 * ... is NOT explained by the hierarchy.

**Conclusion:** The RS hierarchy and the dark energy scale are set by different mechanisms. The warping explains the Planck-TeV hierarchy but NOT the Omega_DE/Omega_m ratio.

### 4.3 PIRSA NMC Scalar Trigger (PIRSA 14070030)

**The idea:** A non-minimally coupled scalar with xi*phi^2*R has its dynamics "triggered" by the onset of matter domination. During radiation domination, R = 0 (for conformally invariant radiation), so the scalar is frozen. When matter begins to dominate, R becomes nonzero and the scalar begins to evolve, naturally linking dark energy onset to the matter-radiation transition.

**Application to Meridian:**

The cuscuton has xi = 1/6 (conformal coupling). The NMC term phi^2*R/6 does couple the scalar to the curvature scalar R. During radiation domination, R = 0 (conformal flatness). During matter domination, R = 3*H_0^2*(Omega_m*(1+z)^3 - 2*Omega_DE) in units of H_0^2.

However, the cuscuton's infinite sound speed means it responds **instantaneously** to any change in R. There is no "triggering delay." A standard scalar with finite c_s would begin slow-rolling when R activates the effective potential --- the finite response time creates a natural link between matter emergence and dark energy onset. The cuscuton has no such delay mechanism.

Quantitatively, R transitions from zero to positive at the matter-radiation equality (z ~ 3400), but the cuscuton instantly adjusts to the new curvature. The kappa_0/E^2 correction begins growing at this point, but its magnitude is suppressed by E^2 ~ Omega_m*(1+z)^3 ~ 10^10 at z = 3400. The correction only becomes appreciable at z < 3 (when E^2 ~ 10). This growth pattern is identical to what 14D found --- it is the cosmological background evolution, not a triggered mechanism.

**Conclusion:** The NMC trigger mechanism is structurally inapplicable to the cuscuton. The infinite sound speed eliminates the delay that would connect matter emergence to dark energy onset.

### 4.4 Kim Interacting Holographic DE

Kim et al. (2023) propose interacting holographic dark energy with rho_DE ~ H^2*M_Pl^2 and a direct DE-DM interaction Q = 3*H*xi*rho_m*rho_DE/(rho_m + rho_DE).

**Application to Meridian:**

Meridian's DE is NOT holographic --- it arises from the brane self-tuning mechanism, not from a holographic bound. The holographic bound rho_DE < 3*H^2*M_Pl^2 IS satisfied (Omega_DE < 1), but this is a generic constraint, not a dynamical mechanism.

More critically, Kim's mechanism requires a direct DE-DM interaction term in the action. In Meridian, the cuscuton couples to matter only through gravity (the metric). There is no direct coupling between the cuscuton and dark matter. Adding such a coupling would modify the field equations and potentially spoil the self-tuning.

**Conclusion:** The Kim mechanism is incompatible with the Meridian framework. It requires field content and couplings not present in the theory.

### 4.5 Shimon Observational Selection Effect

Shimon (2024) observes that the conformal Hubble radius r_H = (1+z)/(H_0*E(z)) peaks at a specific redshift. Observers at this epoch have the maximum observable volume. This provides an **observational selection** for Omega_DE ~ Omega_m without requiring a dynamical explanation.

**Numerical result:**
- Conformal Hubble radius peaks at z = 0.632
- This coincides exactly with the deceleration-acceleration transition: z_accel = (2*Omega_DE/Omega_m)^{1/3} - 1 = 0.632
- It lies between z_eq = 0.296 (matter-DE equality) and z_accel

**Compatibility with Meridian:**

Shimon's argument is not a dynamical mechanism --- it is a selection effect. It does not explain WHY Omega_DE has its value; it explains why we observe the coincidence. This is structurally compatible with Meridian's dynamical amelioration:

| Layer | Question | Mechanism | Type |
|-------|----------|-----------|------|
| 1 | Why is Lambda_4 small? | Self-tuning (junction conditions) | Dynamical |
| 2 | Why is |1+w| ~ 0.25? | eps_1 from NCG spectral action | Structural |
| 3 | Why do we observe it now? | Maximum observable volume at z ~ 0.6 | Selection |

These three layers are independent and complementary. Layer 1 solves the old CC problem. Layer 2 makes the deviation detectable. Layer 3 addresses the timing question that Layer 2 leaves open.

**This is the most honest answer the framework can give.**

---

## 5. Quantitative Estimates

### 5.1 KK Correction Growth Timeline

The kappa_0/E^2 correction as a fraction of Omega_DE, with lookback time:

| Threshold | z_threshold | Lookback time (Gyr) |
|-----------|-------------|---------------------|
| 1% of Omega_DE | z = 2.33 | 11.0 |
| 2% | z = 1.59 | 9.7 |
| 5% | z = 0.78 | 6.9 |
| 10% | z = 0.20 | 2.5 |
| 12.3% (present) | z = 0 | 0 |

The correction has been above 1% of Omega_DE for the last 11 billion years (80% of cosmic history). It has been above 5% for the last 7 billion years. The dynamics are not a recent phenomenon.

### 5.2 Cuscuton Field Evolution from Inflation to Today

The cuscuton field Phi evolves according to the junction conditions, which are algebraic. At every epoch:

- **Inflation (T ~ 10^16 GeV):** The modulus is unstabilized. The cuscuton field value is determined by the instantaneous brane geometry, which is de Sitter with H_inf ~ 10^13 GeV. The KK correction is suppressed by E^2 ~ (H_inf/H_0)^2 ~ 10^{110}. Negligible.

- **Reheating (T ~ 10^8-10^10 GeV):** The modulus oscillates and decays. The cuscuton tracks the evolving geometry instantly (c_s -> infinity). KK correction negligible.

- **Radiation domination (T ~ 10^10 - 0.75 eV):** R = 0 for conformal radiation. The cuscuton's effective potential is R-independent (at xi = 1/6, the conformal coupling means Phi^2*R/6 vanishes when R = 0). The KK correction is suppressed by E^2 ~ Omega_r*(1+z)^4.

- **Matter domination (T ~ 0.75 eV - 0.33 eV):** R becomes nonzero. The cuscuton adjusts instantly. The KK correction begins growing as E^2 decreases.

- **Dark energy domination (T < 0.33 eV to present):** The correction reaches its maximum rate of change near z ~ 0.03 (inflection). Present value: 12.3% of Omega_DE.

- **Future (z -> -1):** E^2 -> Omega_DE. The correction asymptotes to kappa_0/Omega_DE = 12.3%.

**Key point:** The cuscuton does not undergo any phase transition, slow-roll, or triggered onset. Its entire late-time behavior is governed by the decreasing E^2(z), which is the Hubble expansion. The field value Phi_0 is constant (set by junction conditions). Only the effective equation of state w(z) changes, because w depends on E^2(z) through the kappa_0/E^2 correction.

### 5.3 Self-Tuning Relaxation --- A Non-Question

The self-tuning is exact at all times because it is algebraic. The junction conditions are constraint equations, not evolution equations. One might define a formal "relaxation timescale" as t_relax ~ 1/(sqrt(eps_1)*H_0) ~ 111 Gyr ~ 8 * t_age, but this is physically meaningless: the self-tuning does not relax toward its solution, it IS at its solution at every instant.

The 1/sqrt(eps_1) scale is the timescale over which the kappa_0/E^2 correction grows to O(1), i.e., the timescale for |1+w| to become O(1). Since eps_1 = 0.017 and 1/sqrt(eps_1) ~ 7.7, the deviation reaches O(1) only after ~7.7 Hubble times. We observe |1+w| = 0.245, consistent with being 1/8 of this timescale into the evolution.

But this is not a coincidence resolution --- it just restates the 14D finding that eps_1 places the deviation in a detectable window.

---

## 6. Honest Assessment

### 6.1 What Meridian Actually Contributes Beyond LCDM

**On the coincidence problem specifically:**

1. **The old CC problem is solved.** LCDM has no explanation for why Lambda is not O(M_Pl^4). Meridian's self-tuning absorbs 10^{120} in bulk vacuum energy. This is a genuine, quantitative advance.

2. **Dark energy is dynamical.** LCDM postulates a constant Lambda. Meridian derives w(z) = -1 + correction with a specific redshift dependence from the 5D geometry. The correction grows at late times, making the matter-DE transition smoother and less "coincidental."

3. **The deviation magnitude is structural.** The eps_1 = 0.017 from the NCG spectral action (Gauss-Bonnet coefficient C_GB = 2/3) places |1+w(0)| = 0.245, detectable by DESI. This is not fine-tuned --- eps_1 is computed from the spectral triple, not chosen.

4. **The z_eq shift is a testable prediction.** Meridian predicts z_eq = 0.332 vs LCDM z_eq = 0.296 (JC benchmark). This 12% shift is potentially measurable with future BAO surveys.

**What Meridian does NOT contribute:**

1. **Omega_DE/Omega_m ~ 2 is an input.** The ratio of dark energy to matter density is set by the brane parameters (sigma_UV, alpha_UV, mu^2) through the junction conditions. The self-tuning determines Lambda_4 given these parameters, but the parameters themselves are free (14C showed they are relevant perturbations at the Reuter fixed point).

2. **No tracking mechanism.** The cuscuton cannot track matter because of its infinite sound speed and zero kinetic energy. The eps_1 correction gives stiff matter, which dilutes faster than radiation. There is no scaling solution.

3. **No new timescale.** The KK correction peaks where the background cosmology already transitions. The framework amplifies the existing matter-DE transition but introduces no independent clock.

### 6.2 Classification of the Answer

| Problem component | Status | Mechanism | Honest qualifier |
|------------------|--------|-----------|-----------------|
| Why Lambda_4 is small (old CC) | **SOLVED** | Self-tuning (algebraic, exact) | To 15 sig figs, 60 orders of Lambda_5 |
| Why Lambda_4 != 0 (tiny residual) | **Predicted** | eps_1 * zeta_0 from brane geometry | Value set by brane params (input) |
| Why w != -1 (dynamical DE) | **Predicted** | kappa_0/E^2 from KK kinetic correction | Confirmed by DESI at 1.8sigma vs CPL |
| Why rho_DE ~ rho_m NOW | **AMELIORATED** | Dynamical onset + selection | Not solved: Omega_DE/Omega_m is input |
| Why we observe the coincidence | **COMPATIBLE** | Shimon selection (max obs. volume) | Selection, not dynamics |

### 6.3 Is the Answer Fundamentally Anthropic or Dynamical?

**Meridian's answer is primarily dynamical, secondarily structural, and the residual gap is addressable by selection.**

- **Dynamical:** Self-tuning is a dynamical mechanism (junction conditions responding to bulk geometry). The w(z) correction is a dynamical prediction.
- **Structural:** eps_1 from the spectral action is a structural feature of the NCG finite geometry, not a free parameter. The Goldilocks window is structural, not anthropic.
- **Selection (Shimon):** The timing question ("why NOW?") is addressed by observational selection. This is weaker than a dynamical explanation but stronger than a pure anthropic landscape argument, because Meridian has a unique vacuum (no landscape) --- the selection operates on observers, not on vacua.

This three-layer structure is more informative than LCDM (which offers no explanation at any layer) and more honest than models that claim full resolution through tracking or attractor mechanisms.

### 6.4 Comparison with Other Frameworks

| Framework | Old CC problem | Coincidence | Notes |
|-----------|---------------|-------------|-------|
| LCDM | Unsolved | Unsolved | No mechanism at all |
| String landscape | Anthropic selection | Anthropic + scanning | Requires 10^{500} vacua |
| Quintessence (general) | Unsolved | Tracking (some models) | Requires fine-tuned potential |
| Cuscuton gravity (Afshordi) | Partially addressed | No tracking | Similar to Meridian's limitation |
| **Meridian** | **Solved (self-tuning)** | **Ameliorated + selection** | **Unique vacuum, honest gap** |

---

## 7. What Meridian Actually Predicts

For the monograph and any publication, the following should be stated precisely:

### 7.1 Predictions (falsifiable)

1. **w(z) curve:** w(z) = -1 + C_KK/(zeta_0 * E^2(z)) with C_KK and eps_1 from the spectral action. The curve is fully specified given zeta_0.

2. **No phantom crossing:** w(z) > -1 at all redshifts. If DESI confirms w < -1 at any z, Meridian is falsified.

3. **z_eq shift:** +12.2% relative to LCDM at the JC benchmark. Testable with BAO surveys.

4. **eps_1 = 0.017:** The Gauss-Bonnet coupling is computed, not fitted. Determines the magnitude of the deviation.

### 7.2 Explanations (non-trivial but not predictions)

1. **Old CC problem:** Self-tuning explains why Lambda_4 is not O(M_Pl^4).

2. **Dynamical amelioration:** The KK correction softens the coincidence by making DE dynamical over 80% of cosmic history (since z = 2.3 at the 1% level).

### 7.3 Honest limitations

1. **Omega_DE/Omega_m ~ 2 is an input.** The ratio is set by brane parameters that are relevant perturbations at the Reuter fixed point (14C). No principle within the framework fixes this ratio.

2. **No tracker.** The cuscuton sector has no scaling solution. The coincidence timing is not dynamically explained.

3. **Shimon selection is compatible but external.** The observational selection argument works with Meridian but is not derived from it.

---

## 8. Implications for Monograph

### 8.1 What to include

The monograph should present the coincidence analysis at two levels:

**Level 1 (in the main text):** The self-tuning mechanism solves the old CC problem. The dynamical equation of state w(z) ameliorates the coincidence by making DE non-constant. The eps_1 from the spectral action places the deviation in the DESI-detectable window. The coincidence is softened but not fully resolved.

**Level 2 (in an appendix or subsection):** The full 14D computation (kappa_0/E^2 growth curve, z_eq shift, eps_1 sensitivity). The 15G analysis showing that Phase 15 ingredients (radion, KK tower, tracker, spectral action) do not provide additional coincidence resolution. The three-layer structure (dynamical + structural + selection).

### 8.2 What NOT to claim

- Do NOT claim the coincidence problem is "solved." It is ameliorated.
- Do NOT claim the self-tuning mechanism has a relaxation timescale that coincides with matter domination. It is algebraic, not dynamical.
- Do NOT claim the hierarchy connection (rho_DE ~ m_KK^4) works. The ratio is 10^{-18} at the Meridian benchmark.
- Do NOT claim tracker behavior exists. The cuscuton cannot track.

### 8.3 Monograph revision items

| Location | Change needed |
|----------|--------------|
| CC problem discussion | Clearly separate old (solved) from new (ameliorated) |
| DE equation of state | Include kappa_0/E^2 growth timeline table |
| Self-tuning section | Add note: algebraic, not dynamical (no approach timescale) |
| Open problems | List coincidence as "ameliorated, compatible with Shimon selection" |
| Phase 15 summary | Add 15G verdict: "Phase 15 ingredients do not provide additional coincidence resolution beyond 14D" |

### 8.4 Suggested monograph language

> "The Meridian framework solves the old cosmological constant problem through self-tuning: the 4D cosmological constant Lambda_4 is independent of the bulk vacuum energy Lambda_5, confirmed numerically to 15 significant figures across 60 orders of magnitude. The new cosmological constant problem --- why rho_DE ~ rho_m at the present epoch --- is ameliorated but not solved. The dynamical equation of state w(z) = -1 + 2*kappa_0/(Omega_DE * E^2(z)) softens the coincidence: the departure from LCDM grows smoothly from |1+w| < 10^{-5} at z = 10 to |1+w| = 0.245 at z = 0, with the KK correction exceeding 1% of Omega_DE over the last 11 billion years. The Gauss-Bonnet coupling eps_1 = 0.017, determined by the NCG spectral action, places this deviation in the DESI-detectable window without fine-tuning. However, the ratio Omega_DE/Omega_m ~ 2 is set by brane parameters (relevant perturbations at the Reuter fixed point) and is not predicted from first principles. No tracker solution exists in the cuscuton sector (the infinite sound speed and zero kinetic energy preclude tracking), and no Phase 15 ingredient (radion dynamics, KK tower, spectral action running) provides a dynamical link between the dark energy onset and the coincidence epoch. The residual timing question is compatible with observational selection (Shimon 2024): the conformal Hubble radius peaks at z = 0.63, maximizing the observable volume and selecting for Omega_DE ~ Omega_m. The framework thus provides a three-layer answer: dynamical self-tuning for the magnitude, structural NCG determination for the deviation size, and observational selection for the timing."

---

## 9. Open Directions

Two paths remain that could upgrade "ameliorated" to "partially solved":

### 9.1 Multi-field dynamics with octonionic structure (Phase 15B)

The octonionic spectral triple (15B-15B3) introduces a democratic inter-generation mixing matrix M_oct with eigenvalues {1/2, 1/2, 2}. The S_3 symmetry of M_oct is broken by bulk mass parameters. If the S_3-breaking pattern is correlated with the modulus stabilization (both involve the warp factor), there might be a structural connection between fermion mass generation and dark energy onset --- both set by the same warping.

This is speculative but represents the most natural path within the framework. It would require showing that the warp factor k*y_c ~ 35 simultaneously:
- Produces the Planck-TeV hierarchy
- Determines the fermion mass hierarchy (15C)
- Constrains Omega_DE/Omega_m

If all three ratios emerged from the single parameter k*y_c, the coincidence would be structural. This has not been demonstrated and requires the explicit computation of Lambda_4 from the full 5D stabilized potential.

### 9.2 Brane parameter determination from extended NCG (14C + 15A)

Track 14C showed that alpha_UV remains a free brane parameter. Track 15A constructed the explicit spectral triple on the RS orbifold. If the NCG axioms (particularly Poincare duality and orientability) constrain the brane-localized couplings alpha_UV, this would fix Omega_DE and potentially link it to Omega_m through the spectral geometry.

Track 15B4 (orientability of the octonionic triple) is the current frontier of this line of investigation. If the full 7/7 axiom verification constrains the boundary conditions on the Dirac operator (and hence the junction conditions), it could reduce the free parameter count and potentially predict Omega_DE/Omega_m.

---

## 10. Files

| File | Contents |
|------|----------|
| `15G_coincidence_revisited.md` | This document |
| `15G_computation.py` | Full numerical analysis (10 sections) |
| `15G_coincidence_results.json` | Machine-readable results |

---

## 11. References

1. Phase 14D: `14D_coincidence_computation.md` --- Full 14D computation (this project)
2. Phase 15E: `15E_radion_inflation.md` --- Radion inflation and stabilization (this project)
3. Phase 15F: `15F_desi_dr2_confrontation.md` --- DESI DR2 chi-squared analysis (this project)
4. Phase 14N: `14N_vacuum_energy_nogo.md` --- Uniqueness of self-tuning (this project)
5. Phase 14C: `14C_brane_parameters.md` --- Brane parameter determination (this project)
6. Phase 13G: Self-tuning to 15 significant figures (this project, monograph Ch.1)
7. Steinhardt, Wang, Zlatev, PRL 82 (1999) 896 --- "Cosmological tracking solutions"
8. Shimon (2024) --- Observational selection effect (conformal Hubble radius)
9. Kim et al. (2023) --- Interacting holographic dark energy, alpha-model
10. PIRSA 14070030 --- NMC scalar triggered by matter emergence
11. Afshordi et al., JCAP 0612 (2006) 007 --- "Cuscuton: a causal field theory with an infinite speed of sound"
12. Lacombe & Mukohyama, PRD 105 (2022) 104067 --- Self-tuning uniquely selects cuscuton
13. DESI DR2 (2025), arXiv:2503.14738 --- BAO measurements
14. Chamseddine, Connes, Marcolli, hep-th/0610241 --- Spectral action and the Standard Model
15. Goldberger & Wise, PRL 83 (1999) 4922 --- Modulus stabilization
