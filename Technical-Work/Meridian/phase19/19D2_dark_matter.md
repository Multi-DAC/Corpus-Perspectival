# Track 19D.2: Dark Matter and the 3.5 keV X-ray Line

**Date:** March 22, 2026
**Authors:** Clayton W. Iggulden-Schnell & Clawd
**Status:** COMPLETE
**Dependencies:** 15A (spectral triple), 15B3 (octonionic N_g=3), 15C (fermion hierarchy), 15D/16M (sterile neutrino), 19E.1 (neutrino sector), 19F.2-3 (collider predictions)
**Phase 19 Track:** D.2 — Priority 2 (Core Physics)

---

## 0. Executive Summary

We assess every dark matter candidate that the Meridian framework (RS1 + NCG spectral action + cuscuton self-tuning) can offer, computing masses, lifetimes, mixing angles, relic abundances, and confronting the 3.5 keV X-ray anomaly. The framework is minimal: its particle content is exactly the Standard Model plus three right-handed neutrinos, and its extra-dimensional sector produces KK graviton excitations and the radion.

| Candidate | Mass | Lifetime | Stable? | DM Viable? |
|-----------|------|----------|---------|------------|
| **nu_R1 (sterile neutrino)** | keV (free parameter) | >> t_univ | Yes | **YES** (only candidate) |
| KK graviton (G_1) | ~5.9 TeV | ~5 x 10^{-28} s | No | No |
| Radion (phi) | 10--1500 GeV | ~3 x 10^{-22} s | No | No |
| Axion | Does not exist | -- | -- | No (no U(1)_PQ) |
| Gravitino | Does not exist | -- | -- | No (no SUSY) |

**The bottom line:** The lightest sterile neutrino is the *only* dark matter candidate in the minimal framework. It exists structurally (the spectral triple requires nu_R), but its mass and mixing angle are free parameters. The framework *points to* sterile neutrino warm dark matter but does not *determine* the DM mass. The 3.5 keV X-ray line, now disfavored by XRISM (2024), was never a prediction of the framework.

**Match/Pivot/Kill verdict:** PIVOT. The framework accommodates DM but does not sharply predict it. The sharpest prediction is *negative*: no WIMPs, no axion, no gravitino. A WIMP discovery at the LHC or in direct detection would be a serious challenge to NCG minimality.

---

## 1. The Dark Matter Candidates

### 1.1 Inventory

The Meridian framework has exactly the following BSM content:

**From the NCG spectral triple** (C + H + M_3(C)):
- 3 generations of right-handed (sterile) neutrinos nu_R, gauge singlets with Majorana masses (from the spectral action). Number fixed by octonionic rigidity (N_g = 3, from 15B3).

**From the RS1 geometry** (M_4 x S^1/Z_2):
- KK graviton tower: G_n with masses m_n = x_n * k * e^{-ky_c}, where x_n are zeros of J_1.
- Radion phi: scalar fluctuation of brane separation, mass set by Goldberger-Wise stabilization.

**Not present:**
- No axion (strong CP solved geometrically, Phase 16E; no U(1)_PQ in the spectral triple).
- No gravitino (no supersymmetry).
- No additional scalars beyond the Higgs and radion.
- No dark photon or hidden sector gauge bosons (gauge group fixed by NCG algebra).

This is the *minimal* content. Any DM candidate must come from this list.

---

## 2. Candidate 1: Sterile Neutrino (nu_R1)

### 2.1 Existence and Quantum Numbers

The sterile neutrino is **structural** in the Meridian framework. The finite spectral triple (A_F, H_F, D_F, J_F, gamma_F) with algebra A_F = C + H + M_3(C) requires the right-handed neutrino to complete the fermionic Hilbert space H_F. This is not optional — removing nu_R would violate the axioms of the spectral triple (specifically the Poincare duality / intersection form condition).

Properties:
- **Number:** Exactly 3 (octonionic N_g = 3, from 15B3)
- **Gauge quantum numbers:** Complete singlet under SU(3) x SU(2) x U(1)
- **Mass type:** Majorana (lepton-number violating, allowed by the spectral action)
- **Mixing:** With active neutrinos through the Dirac mass term in D_F

### 2.2 Mass Scale: The Natural Scale Problem

The sterile neutrino mass depends on where the Majorana operator lives in the bulk.

**Scenario A: UV-brane Majorana mass (M_* ~ M_Pl)**

For the UV-brane operator delta(y) * M_* * nu_R^T C nu_R, the effective 4D mass for UV-localized nu_R (c > 1/2) is:

    M_R^{4D} ~ M_Pl * (2c - 1)

This gives GUT-scale masses for any O(1) value of c:

| c | M_R [GeV] |
|---|-----------|
| 0.6 | 4.9 x 10^17 |
| 0.7 | 9.7 x 10^17 |
| 1.0 | 2.4 x 10^18 |
| 1.17 | 8.3 x 10^17 |

**Conclusion:** UV-brane Majorana mass naturally gives GUT-scale sterile neutrinos, suitable for the standard Type I seesaw. This does NOT produce keV DM.

**Scenario B: IR-brane Majorana mass (M_IR ~ TeV)**

For an IR-brane operator with M_IR = k * e^{-ky_c} ~ 1535 GeV:

    M_R^{4D} = M_IR * (2c-1) * exp(-(2c-1)*ky_c)

| c | M_R |
|---|-----|
| 0.51 | 15.2 GeV |
| 0.55 | 4.6 GeV |
| 0.60 | 0.28 GeV |
| 0.70 | 511 keV |
| 0.80 | 0.70 keV |
| 0.90 | 8.5 x 10^{-4} keV |
| 1.00 | 9.7 x 10^{-7} keV |

**Conclusion:** IR-brane Majorana gives keV masses at c ~ 0.70--0.80, but sub-eV for c > 0.9. The keV window exists but requires specific parameter values.

**Scenario C: Intermediate Majorana scale**

For any M_IR, a 7 keV mass can be achieved by choosing the appropriate c:

| M_IR [GeV] | c_nuR1 for M_R = 7 keV |
|------------|------------------------|
| 10^3 | 0.759 |
| 10^6 | 0.862 |
| 10^9 | 0.965 |
| 10^12 | 1.066 |
| 10^15 | 1.167 |
| M_Pl | 1.281 |

**Key conclusion:** A 7 keV sterile neutrino is *achievable* for any choice of the Majorana scale, but c_nuR1 must be tuned to match. The keV scale is an **input**, not an **output** of the framework.

### 2.3 Active-Sterile Mixing Angle

In the nuMSM (nu Minimal Standard Model) scenario, nu_R1 is the DM candidate, decoupled from the seesaw that generates active neutrino masses (handled by nu_R2 and nu_R3). The mixing angle between nu_R1 and the active neutrinos is:

    sin^2(2theta) = 4 * (m_D / M_R1)^2

where m_D = Y_5 * g(c_nuR1) * v/sqrt(2) is the Dirac mass from the Gherghetta-Pomarol overlap.

For M_R1 = 7 keV, Y_5 = 1, ky_c = 35:

| c_nuR1 | g(c) | sin^2(2theta) | XRISM Status |
|--------|------|---------------|-------------|
| 1.00 | 1.5 x 10^{-7} | 55 | EXCLUDED |
| 1.10 | 4.9 x 10^{-9} | 0.060 | EXCLUDED |
| 1.17 | 4.5 x 10^{-10} | 5.0 x 10^{-4} | EXCLUDED |
| 1.20 | 1.6 x 10^{-10} | 6.3 x 10^{-5} | EXCLUDED |
| 1.30 | 5.2 x 10^{-12} | 6.6 x 10^{-8} | EXCLUDED |
| 1.40 | 1.7 x 10^{-13} | 6.8 x 10^{-11} | EXCLUDED |
| 1.50 | 5.3 x 10^{-15} | 6.9 x 10^{-14} | XRISM OK |

**XRISM boundary (Y_5 = 1):** c_nuR1 > 1.415 is required.

**Important caveat:** The effective coupling is not simply Y_5 = 1. The left-handed lepton doublet overlap g_L(c_L) and the actual 5D Yukawa enter as Y_0 * g_L, which can be much smaller than 1. The Phase 16M analysis used calibrated values and found the XRISM boundary at c_nuR1 ~ 1.185 (with ky_c = 37). The precise boundary depends on the normalization convention, but in all cases, the mixing angle is a free parameter controlled by the bulk mass c_nuR1.

### 2.4 Radiative Decay: nu_s -> nu + gamma

The standard one-loop decay rate (Pal & Wolfenstein 1982):

    Gamma(nu_s -> nu + gamma) = (9 * alpha * G_F^2 * sin^2(2theta) * m_s^5) / (1024 * pi^4)

Numerical prefactor: 8.96 x 10^{-17} GeV^{-4}

For m_s = 7 keV (photon energy E_gamma = 3.5 keV):

| sin^2(2theta) | Gamma [GeV] | tau [s] | tau / t_univ |
|---------------|-------------|---------|-------------|
| 7 x 10^{-11} (Bulbul+2014) | 1.05 x 10^{-52} | 6.2 x 10^{27} | 1.4 x 10^{10} |
| 2.4 x 10^{-11} (XRISM limit) | 3.6 x 10^{-53} | 1.8 x 10^{28} | 4.2 x 10^{10} |
| 10^{-12} | 1.5 x 10^{-54} | 4.4 x 10^{29} | 10^{12} |
| 10^{-13} | 1.5 x 10^{-55} | 4.4 x 10^{30} | 10^{13} |

**All mixing angles in the viable window produce lifetimes >> t_univ.** The sterile neutrino is cosmologically stable (it decays, but far too slowly to deplete the relic abundance).

### 2.5 Relic Abundance

**Dodelson-Widrow (non-resonant production):**

    Omega_DW h^2 ~ 0.3 * (sin^2(2theta) / 10^{-8}) * (m_s / 3 keV)^{1.8}

For m_s = 7 keV, achieving Omega h^2 = 0.12 requires sin^2(2theta) ~ 4 x 10^{-9}. This is **excluded by XRISM** (limit: 2.4 x 10^{-11}), ruling out non-resonant production.

**Shi-Fuller (resonant production):**

A primordial lepton asymmetry L resonantly enhances production, allowing much smaller mixing angles. The required asymmetry:

    L_6 ~ 8 * (7 x 10^{-11} / sin^2(2theta))

| sin^2(2theta) | L_6 | L | BBN Status |
|---------------|-----|---|-----------|
| 2.4 x 10^{-11} | 23 | 2.3 x 10^{-5} | OK |
| 10^{-11} | 56 | 5.6 x 10^{-5} | OK |
| 10^{-12} | 560 | 5.6 x 10^{-4} | OK |
| 10^{-13} | 5600 | 5.6 x 10^{-3} | OK |

BBN constraint: |L| < 0.01 (conservative). All entries satisfy this.

**Viable production window:** sin^2(2theta) in [~5 x 10^{-14}, 2.4 x 10^{-11}], with Shi-Fuller production requiring a lepton asymmetry that can be generated by CP-violating decays of nu_R2 and nu_R3 (the heavier sterile neutrinos in the nuMSM).

### 2.6 Structure Formation Constraints

A keV-mass sterile neutrino is warm dark matter (WDM), with free-streaming length:

    lambda_fs ~ 0.3 * (m_s / keV)^{-1} Mpc    (Dodelson-Widrow)
    lambda_fs ~ 0.2 * (m_s / keV)^{-1} Mpc    (Shi-Fuller, colder spectrum)

For m_s = 7 keV: lambda_fs ~ 0.03--0.04 Mpc.

Lyman-alpha forest constraint: m_s > 5.3 keV (2-sigma, DW); m_s > 3--4 keV (Shi-Fuller). A 7 keV sterile neutrino is **safe** for both.

### 2.7 Sterile Neutrino DM: Assessment

| Aspect | Status |
|--------|--------|
| Existence | PREDICTED (structural, from spectral triple) |
| Number = 3 | PREDICTED (octonionic N_g = 3) |
| Gauge singlet + Majorana | PREDICTED (NCG algebra) |
| keV mass | ACCOMMODATED (c_nuR1 is free) |
| Mixing angle | ACCOMMODATED (free parameter) |
| Cosmological stability | YES (tau >> t_univ for all viable mixing) |
| Relic abundance | ACCOMMODATED (Shi-Fuller with lepton asymmetry) |
| Structure formation | CONSISTENT (WDM at 7 keV is allowed) |
| X-ray signal | FREE PARAMETER (no prediction for flux) |

---

## 3. Candidate 2: KK Graviton

### 3.1 Mass and Width

First KK graviton mass (from 19F.2):

    m_1 = x_1 * k * e^{-ky_c} = 3.832 * M_Pl_bar * e^{-35} = 5883 GeV ~ 5.9 TeV

Total width (for kappa = k/M_Pl_bar = 1):

    Gamma_tot ~ 1317 GeV
    Gamma/m ~ 0.22
    tau ~ 5 x 10^{-28} s

### 3.2 KK Parity

The critical question for DM stability is whether a discrete symmetry prevents the lightest KK mode from decaying.

In **Universal Extra Dimensions (UED):** All SM fields propagate in the bulk, and the orbifold preserves a Z_2 KK parity. The lightest KK particle (LKP) is stable and is a viable WIMP dark matter candidate.

In **RS1:** KK parity is **broken** by the orbifold boundary conditions. The key difference: in RS1, the two branes (UV and IR) have different properties and different fields localized on them. The Z_2 symmetry y -> -y of the orbifold acts as a gauge symmetry (it identifies the fundamental domain), not as a global symmetry of the spectrum. The effective 4D theory has no conserved KK number.

Concretely: the coupling G_n -> SM + SM is **allowed** for all n. The first KK graviton can decay to any pair of SM particles it kinematically accesses (dijets, dileptons, diphotons, dibosons). The branching ratios are computed in 19F.3.

### 3.3 KK Graviton DM Verdict

| Property | Value |
|----------|-------|
| Mass | ~5.9 TeV |
| Lifetime | ~5 x 10^{-28} s |
| tau / t_univ | ~10^{-45} |
| Stabilizing symmetry | **None** (KK parity broken in RS1) |
| DM viable? | **NO** |

**The KK graviton is not a DM candidate.** It decays essentially instantaneously to SM pairs.

---

## 4. Candidate 3: Radion

### 4.1 Mass and Couplings

The radion mass in the Meridian framework (from 19F.2):

    m_phi ~ (epsilon / sqrt(3)) * k * e^{-ky_c}

Range: ~10 GeV to ~1.5 TeV depending on brane couplings (free parameter).

The radion couples universally to the trace of the SM stress-energy tensor:

    L_int = -(1 / Lambda_phi) * phi * T^mu_mu

with Lambda_phi = sqrt(6) * M_Pl_bar * e^{-ky_c} = 3761 GeV.

### 4.2 Decay and Stability

For a benchmark m_phi = 300 GeV:

    Gamma(phi -> gg) ~ 1.3 x 10^{-3} GeV (trace anomaly dominates)
    Gamma_tot ~ 2.0 x 10^{-3} GeV
    tau ~ 3.3 x 10^{-22} s

| Property | Value |
|----------|-------|
| Mass | 10--1500 GeV |
| Lifetime | ~10^{-22} s (at 300 GeV) |
| tau / t_univ | ~10^{-40} |
| Stabilizing symmetry | **None** |
| DM viable? | **NO** |

The radion has no stabilizing symmetry. It couples to everything that has mass (through the stress-energy trace) and decays promptly. Not a DM candidate.

### 4.3 Could the Cuscuton Stabilize the Radion?

The cuscuton self-tuning mechanism (Phase 13G) locks the radion position via the cosmological constant matching condition. However, this constrains the radion *VEV*, not the radion *fluctuations*. The radion particle still decays through its couplings to SM fields. The cuscuton adds a negligible mass contribution at the dark energy scale (~meV) and does not provide a stabilizing symmetry.

---

## 5. Other Candidates

### 5.1 Axion-like Particles

The RS1+NCG framework does **not** produce an axion. The strong CP problem is solved geometrically in Phase 16E: the CP-violating theta parameter is set to zero by the RS orbifold boundary conditions and the NCG spectral action structure. No Peccei-Quinn U(1)_PQ symmetry is introduced, and the spectral triple C + H + M_3(C) does not contain one. Therefore there is no QCD axion and no axion DM.

### 5.2 Gravitino

The framework is not supersymmetric. No gravitino exists. Not a candidate.

### 5.3 NCG Moduli

The spectral action parameters (Yukawa couplings, Majorana masses, gauge couplings) are fixed at the classical level by the spectral triple data. There are no additional light moduli beyond the radion. The Higgs scalar is the only light scalar in the NCG particle content, and it is not stable.

---

## 6. The 3.5 keV X-ray Line

### 6.1 Observational Status (as of 2024--2025)

| Year | Observation | Result |
|------|------------|--------|
| 2014 | Bulbul+ (XMM, 73 clusters) | ~3.5-sigma detection, sin^2(2theta) ~ 7 x 10^{-11} |
| 2014 | Boyarsky+ (XMM, M31+Perseus) | ~3.5-sigma detection, consistent |
| 2017 | Hitomi (Perseus) | No detection (limited exposure) |
| 2020 | Dessert+ (NuSTAR, M31) | No detection; limit < 2.0 x 10^{-11} |
| 2021 | Foster+ (NuSTAR, MW halo) | No detection; limit < 1.0 x 10^{-11} |
| 2024 | **XRISM (Perseus, ~5 eV resolution)** | **No detection; 99.7% CL: sin^2(2theta) < 2.4 x 10^{-11}** |

**Status:** The original Bulbul+2014 signal (sin^2(2theta) ~ 7 x 10^{-11}) is **excluded** at >99.7% CL by XRISM. Multiple independent non-detections (Dessert+, Foster+, XRISM) with different instruments and targets consistently find no line. The 3.5 keV feature is most likely a systematic artifact — plasma lines, charge exchange, or instrumental effects in the original XMM-Newton data.

### 6.2 What Does the Framework Say?

The Meridian framework is **agnostic** about the 3.5 keV line:

1. A 7 keV sterile neutrino is *consistent* with the framework (c_nuR1 ~ 1.19 for appropriate M_IR and ky_c).
2. The mixing angle sin^2(2theta) is a *free parameter* — the framework does not predict it.
3. Shi-Fuller production at sin^2(2theta) < 2.4 x 10^{-11} is viable with appropriate lepton asymmetry.
4. But the 7 keV mass is an *input*, not a prediction. Any mass in the keV range works equally well for slightly different c values.

**The framework neither predicted nor required the 3.5 keV line. Its non-detection is not a problem for Meridian.**

However, a weaker X-ray line from sterile neutrino DM at *some* energy remains a generic prediction if DM is indeed the lightest nu_R. The energy and flux are not determined by the geometry.

---

## 7. Comprehensive Dark Matter Verdict

### 7.1 Genuine Predictions (Geometry/Algebra-Determined)

1. **Exactly 3 sterile neutrinos exist** (octonionic N_g = 3 rigidity).
2. **They are gauge singlets with Majorana mass** (NCG spectral triple structure).
3. **Exponential mass hierarchy between generations** (Gherghetta-Pomarol mechanism from O(1) bulk mass differences).
4. **Normal mass ordering for active neutrinos** (structural, S_3 singlet heavier).
5. **No WIMP dark matter** (KK parity broken in RS1; no stable heavy relic).
6. **No axion dark matter** (strong CP solved geometrically; no U(1)_PQ).
7. **No gravitino** (no supersymmetry).
8. **KK graviton and radion are unstable** (no stabilizing symmetry; tau ~ 10^{-22}--10^{-28} s).

### 7.2 The Dark Matter Scenario

The **only viable DM candidate** in the minimal RS1+NCG framework is the **lightest right-handed neutrino**, nu_R1, in the nuMSM (nu Minimal Standard Model) configuration:

- nu_R1: keV-scale mass, DM candidate (free-streaming ~0.03--0.04 Mpc at 7 keV)
- nu_R2, nu_R3: GeV-scale masses, generate active neutrino masses via seesaw, generate lepton asymmetry for Shi-Fuller production

This scenario:
- Is **consistent** with all current data (XRISM, Lyman-alpha, structure formation, BBN)
- Requires Shi-Fuller production (Dodelson-Widrow is excluded by X-ray bounds)
- Predicts warm dark matter with suppresseed small-scale structure

### 7.3 What Is Predicted vs. Accommodated

| Feature | Status | Comment |
|---------|--------|---------|
| DM is a sterile neutrino | **PREDICTED** | Structural (spectral triple requires nu_R) |
| Warm DM, not cold | **PREDICTED** | keV mass implies WDM |
| No WIMPs at LHC | **PREDICTED** | Structural (no stable heavy BSM particle) |
| No axion DM | **PREDICTED** | No U(1)_PQ in the framework |
| m_s = 7 keV | **ACCOMMODATED** | c_nuR1 is a free parameter |
| sin^2(2theta) | **ACCOMMODATED** | Depends on free parameters |
| Relic abundance | **ACCOMMODATED** | Requires lepton asymmetry (free) |
| 3.5 keV line flux | **NOT PREDICTED** | Free parameter; line now disfavored |

### 7.4 Honest Assessment

The framework **points to** sterile neutrino DM but does not **determine** the DM mass or mixing angle. This is weaker than, for example:

- **SUSY DM:** where the WIMP mass is tied to the SUSY-breaking scale (a single free parameter determines both the hierarchy and the DM mass).
- **Axion DM:** where the axion mass is tied to the PQ scale (one parameter determines both strong CP solution and the DM density).

In Meridian, the sterile neutrino mass is essentially **decoupled** from the hierarchy-solving mechanism (the warp factor e^{-ky_c} solves the hierarchy; the sterile neutrino mass requires additional input about the Majorana sector). The existence of nu_R is structural, but the keV scale is not.

The framework does, however, make **sharp negative predictions**: no WIMPs, no axion, no gravitino. If any of these were discovered, it would require extending the spectral triple beyond C + H + M_3(C), which would be a serious blow to the NCG minimality principle.

### 7.5 Match/Pivot/Kill

**MATCH:** Dark matter exists (trivially accommodated); sterile neutrinos exist (structural prediction matched by all oscillation data).

**PIVOT:** The mass scale and mixing angle of the DM candidate are free parameters. The framework cannot sharply predict the DM mass without additional input about the Majorana sector. Future work should investigate whether the NCG spectral action places any constraints on the relative scale of the three Majorana masses M_1, M_2, M_3.

**KILL CRITERION:** A confirmed WIMP discovery (at the LHC, in direct detection, or in indirect detection) with properties inconsistent with keV sterile neutrinos would require BSM content beyond the minimal spectral triple. This would not necessarily kill the entire framework (the gauge group and Higgs sector are still determined by NCG), but it would undermine the claim that the spectral triple fully determines the matter content.

### 7.6 Testable Predictions (Ordered by Sharpness)

1. **NO WIMP signals at LHC or direct detection** (SHARP, structural). No neutralino, no inert doublet scalar, no stable KK particle.
2. **NO gravitino or axion DM signals** (SHARP, no SUSY/PQ in the framework).
3. **WDM signatures in Lyman-alpha/21cm** (SOFT, depends on DM mass). Suppressed small-scale power at k > 10 h/Mpc if m_s < 20 keV.
4. **X-ray line from nu_s -> nu + gamma** (SOFT, depends on mixing angle). Detectable by next-generation missions (Athena, HUBS, LEM) if sin^2(2theta) > 10^{-13}.
5. **No detection at large direct-detection experiments** (XENONnT, LZ, DARWIN). Sterile neutrino DM has zero nuclear scattering cross-section at leading order (gauge singlet).

### 7.7 What Phase 19 Tier 3/4 Should Investigate

1. **Does the spectral action constrain M_R relative scales?** If the NCG self-consistency conditions (e.g., the spectral action coefficient relations) link the three Majorana eigenvalues, this could sharpen the prediction for the DM mass.
2. **Baryogenesis/leptogenesis from nu_R2,3:** The nuMSM requires CP-violating oscillations of the GeV-scale sterile neutrinos to generate the baryon asymmetry. Does the NCG CP violation mechanism (Phase 16A) provide the correct amount?
3. **Warm DM signatures in the 21cm signal:** The HERA/SKA 21cm experiments probe small-scale structure at high redshift. What WDM mass range would Meridian's nuMSM scenario predict, and is it distinguishable from CDM?

---

## Appendix A: Numerical Results

### A.1 GP Profile Overlap (ky_c = 35)

| c | g(c) |
|---|------|
| 0.3 | 3.74 |
| 0.5 | 0.169 |
| 0.7 | 3.41 x 10^{-3} |
| 0.9 | 4.40 x 10^{-6} |
| 1.0 | 1.49 x 10^{-7} |
| 1.1 | 4.91 x 10^{-9} |
| 1.17 | 4.48 x 10^{-10} |
| 1.2 | 1.60 x 10^{-10} |
| 1.3 | 5.17 x 10^{-12} |
| 1.5 | 5.28 x 10^{-15} |

### A.2 Free-Streaming Length

| m_s [keV] | lambda_fs (DW) [Mpc] | lambda_fs (SF) [Mpc] |
|-----------|---------------------|---------------------|
| 1 | 0.30 | 0.21 |
| 3 | 0.10 | 0.07 |
| 5 | 0.06 | 0.04 |
| 7 | 0.04 | 0.03 |
| 10 | 0.03 | 0.02 |
| 50 | 0.006 | 0.004 |

### A.3 Computation Scripts

- Full computation: `phase19/19D2_full_computation.wl`
- Prior exploration: `phase19/19D2_computation.wl`, `phase19/19D2_refined.wl`

---

*Analysis complete. The honest verdict: the framework has a natural DM candidate (sterile neutrino, structural), but cannot predict its mass or mixing. The sharpest predictions are negative — no WIMPs, no axion, no gravitino.*
