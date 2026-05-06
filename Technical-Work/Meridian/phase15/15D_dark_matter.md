# Track 15D: Dark Matter Candidates in the Meridian Framework

**Date:** March 18, 2026
**Authors:** Clayton W. Iggulden-Schnell & Clawd
**Status:** COMPLETE
**Computation:** `15D_dark_matter.py`
**Dependencies:** 14F (collider phenomenology), 15A (spectral triple), 15B2-B3 (octonionic construction)

---

## 0. Executive Summary

We investigate four dark matter candidates within the Meridian framework (5D RS orbifold + NCG spectral action + cuscuton self-tuning). The honest result:

| Candidate | Status | Reason |
|-----------|--------|--------|
| **Lightest KK Particle** | EXCLUDED | KK parity broken by RS warping |
| **Radion** | EXCLUDED | Decays via trace anomaly; no stabilizing symmetry |
| **Sterile neutrino (nu_R)** | **VIABLE** | keV-scale; Shi-Fuller production; seesaw-natural |
| **Cuscuton excitation** | EXCLUDED | Zero mode is dark energy; KK modes unstable |

**The Meridian framework has one natural DM candidate: the lightest right-handed (sterile) neutrino, nu_R1.** This is not imposed -- it emerges from the spectral triple structure, which requires nu_R as part of the 16-dimensional representation per generation. The mass is not predicted from first principles (it depends on the free bulk mass parameter c_nu), but the keV window is achieved for O(1) parameters with no fine-tuning.

The framework embeds the nuMSM (Asaka, Blanchet, Shaposhnikov) into a UV-complete setting: the octonionic spectral triple derives N_g = 3 (explaining why three sterile neutrinos exist), the S_3 generation symmetry constrains the Majorana sector, and the Gherghetta-Pomarov mechanism provides the mass hierarchy between DM (keV) and leptogenesis (GeV-TeV) sterile neutrinos.

---

## 1. Candidate 1: Lightest KK Particle (LKP)

### 1.1 KK Parity on the RS Orbifold

In flat Universal Extra Dimensions (UED) on S^1/Z_2, KK parity (-1)^n is conserved because the orbifold preserves the y -> -y reflection symmetry. This discrete symmetry stabilizes the lightest KK excitation (typically B^(1), the first KK mode of the hypercharge gauge boson), making it a DM candidate.

**In the Randall-Sundrum orbifold, KK parity is broken.** The warp factor A(y) = -ky distinguishes the UV brane (y = 0) from the IR brane (y = y_c). The transformation y -> y_c - y (which is the RS analogue of the flat-space reflection) maps:

    e^{-ky} -> e^{-k(y_c - y)} = e^{-ky_c} * e^{ky}

This is NOT a symmetry of the warped metric. The two branes have physically distinct scales: M_Pl at y = 0 and TeV at y = y_c. The orbifold Z_2 (y -> -y) is a gauge symmetry (identifying points), not a global symmetry that could stabilize particles.

**There is no residual discrete symmetry in the RS orbifold that could stabilize any KK mode.** All KK excitations decay promptly to Standard Model particles.

### 1.2 KK Spectrum (for completeness)

Using standard RS1 parameters (k ~ M_Pl = 2 x 10^18 GeV, ky_c = 35):

| Mode | Mass [TeV] | LHC limit [TeV] | Status |
|------|-----------|-----------------|--------|
| m_1 (KK graviton) | 4.84 | 4.7 (diphoton) | Consistent |
| m_2 | 8.86 | -- | Above reach |
| m_3 | 12.84 | -- | Above reach |

The NMC correction from xi = 1/6 shifts the KK tower upward by +zeta_0 ~ 0.1% (negligible for this analysis).

### 1.3 Hypothetical Direct Detection (Even If Stable)

Even if KK parity were conserved, the LKP would be excluded by direct detection. The KK graviton couples to matter through the IR-brane-localized coupling:

    sigma_SI ~ m_N^4 / (pi * Lambda_IR^4) ~ 8 x 10^{-44} cm^2

at m_DM ~ 5 TeV. This is **two orders of magnitude above the LZ 2024 bound** (sigma_SI < 1.5 x 10^{-46} cm^2 at ~TeV masses). The enhanced coupling at the IR brane (g_KK ~ g_SM * sqrt(2*ky_c) ~ 8.4 * g_SM) makes KK graviton DM incompatible with direct detection even in the hypothetical case of a stabilizing symmetry.

### 1.4 Verdict

**LKP is NOT a viable DM candidate in Meridian.** Double exclusion: (1) KK parity broken by warping, (2) direct detection cross-section too large even if stable.

---

## 2. Candidate 2: Radion

### 2.1 Radion Couplings

The radion couples universally to SM particles through the trace of the energy-momentum tensor:

    L_int = -(r / Lambda_r) * T^mu_mu

where Lambda_r = sqrt(6) * M_Pl * e^{-ky_c} = 3761 GeV is the radion coupling scale (from 14F).

At xi = 1/6 (conformal coupling), the kinetic mixing matrix has det(Z) = 1 (no ghost), and the Higgs-radion mixing is purely mass-mixing. But the trace anomaly coupling is **non-zero**: the radion couples to gluons through the QCD trace anomaly (b_3 = 7), to photons through the EM trace anomaly, and to massive particles through their mass terms.

### 2.2 Radion Lifetime

The dominant decay channel below the WW threshold is r -> gg:

    Gamma(r -> gg) = alpha_s^2 * m_r^3 * b_3^2 / (32 * pi^3 * Lambda_r^2)

| m_r [GeV] | Gamma_total [GeV] | tau [s] | tau / t_univ |
|-----------|-------------------|---------|--------------|
| 10^-3 (MeV) | 4.9 x 10^{-20} | 1.4 x 10^{-5} | 3.1 x 10^{-23} |
| 10^-2 | 4.9 x 10^{-17} | 1.4 x 10^{-8} | 3.1 x 10^{-26} |
| 1 | 4.9 x 10^{-11} | 1.4 x 10^{-14} | 3.1 x 10^{-32} |
| 10 | 4.9 x 10^{-8} | 1.4 x 10^{-17} | 3.1 x 10^{-35} |
| 300 | 4.7 x 10^{-2} | 1.4 x 10^{-23} | 3.2 x 10^{-41} |

The radion lifetime is shorter than the age of the universe for **all masses above ~ 3 x 10^{-11} GeV (30 meV)**. Since the Goldberger-Wise stabilization mechanism generically gives m_r >> eV, the radion decays on cosmological timescales.

### 2.3 No Stabilizing Symmetry

There is no discrete symmetry in the RS orbifold that forbids radion decay:

- The trace anomaly coupling is universal and unsuppressed (by 1/Lambda_r).
- Conformal coupling (xi = 1/6) gives det(Z) = 1 (prevents ghost), but does NOT prevent decay.
- The radion carries no conserved quantum number distinct from SM particles.
- Z_2 orbifold symmetry is a gauge symmetry, not a global symmetry.

### 2.4 Ultra-Light Radion Loophole

In principle, an extremely light radion (m_r < 30 meV) could be cosmologically stable. However:
- The Goldberger-Wise mechanism gives m_r ~ TeV/37 ~ 40 GeV for natural parameters (14F).
- Achieving m_r < meV requires extreme fine-tuning of the brane potentials.
- Misalignment relic abundance: Omega_r h^2 ~ (m_r/eV) * (Lambda_r/M_Pl)^2. For Omega_r h^2 = 0.12: m_r ~ 5 x 10^{28} eV. This is self-contradictory (requires a Planck-scale mass from a misalignment mechanism designed for sub-eV particles).

### 2.5 Verdict

**Radion is NOT a natural DM candidate in Meridian.** It decays via the trace anomaly with no stabilizing symmetry. The ultra-light loophole requires unnatural fine-tuning.

---

## 3. Candidate 3: Sterile Neutrino (nu_R) — THE VIABLE CANDIDATE

### 3.1 nu_R in the Spectral Triple

The Chamseddine-Connes-Marcolli spectral triple includes the right-handed neutrino nu_R as part of the 16-dimensional representation per generation:

    16 = Q_L(6) + L_L(2) + u_R(3) + d_R(3) + e_R(1) + nu_R(1)

This is NOT optional — nu_R is **required by the spectral triple**. The NCG axioms (particularly the zero-order condition for the real structure J_F) demand that the Hilbert space contain both left- and right-handed neutrinos. Removing nu_R would break the spectral triple.

The finite Dirac operator D_F includes:
- **Dirac Yukawa:** Y_nu * v (coupling nu_L to nu_R via the Higgs)
- **Majorana mass:** M_R (self-coupling of nu_R, allowed because nu_R is a gauge singlet)

In the octonionic extension (15B3):
- The three sterile neutrinos are related by S_3 generation symmetry
- The inter-generation Majorana coupling is democratic: (M_oct)_{ij} * M_R
- At leading order, M_R1 = M_R2 = M_R3 (S_3 symmetric)
- Splitting from different bulk mass parameters c_{nu_i}

### 3.2 Type-I Seesaw

The seesaw mechanism relates the light neutrino mass to the sterile neutrino mass:

    m_nu = Y_nu^2 * v^2 / M_R

For the atmospheric neutrino mass scale m_nu ~ 0.05 eV:

| Y_nu | M_R | Scale |
|------|-----|-------|
| 10^{-6} | 1.2 TeV | TeV |
| 10^{-4} | 1.2 x 10^7 GeV | Intermediate |
| 10^{-2} | 1.2 x 10^{11} GeV | Leptogenesis |
| 1 | 1.2 x 10^{15} GeV | GUT |

### 3.3 The Gherghetta-Pomarov Mechanism

In the RS orbifold, fermion zero-mode profiles are exponentially sensitive to the 5D bulk mass parameter c:

    f(y) ~ e^{(2-c) ky}

The effective 4D Yukawa coupling is:

    Y_nu^{eff} ~ Y_0 * e^{(1/2 - c_nu) * ky_c}

For ky_c = 35:

| c_nu | Y_nu^{eff}/Y_0 | M_R (seesaw) |
|------|----------------|-------------|
| 0.5 | 1 | 1.2 x 10^{15} GeV |
| 0.7 | 9 x 10^{-4} | 10^9 GeV |
| 1.0 | 2.5 x 10^{-8} | 0.76 GeV |
| 1.17 | 7.3 x 10^{-11} | 7 keV |

**A bulk mass parameter c_nu ~ 1.17 gives M_R ~ 7 keV** — squarely in the keV sterile neutrino DM window. This is an O(1) parameter requiring no fine-tuning.

### 3.4 The nuMSM Embedding

The critical insight is that in a three-sterile-neutrino framework (the nuMSM of Asaka, Blanchet, Shaposhnikov), the lightest sterile neutrino **decouples from the seesaw**. The seesaw is dominated by the two heavier sterile neutrinos (M_R2, M_R3 ~ GeV-TeV), which generate the observed light neutrino masses. The lightest sterile neutrino (M_R1 ~ keV) has a Yukawa coupling that can be **much smaller** than the seesaw would naively require.

In the nuMSM:
- **nu_R1** (M_R1 ~ keV): Dark matter candidate. Yukawa ~ 10^{-13} (tiny, but natural via GP mechanism with c_nu ~ 1.2).
- **nu_R2, nu_R3** (M_R2,3 ~ GeV): Generate light neutrino masses via seesaw. Their CP-violating decays produce the lepton asymmetry needed for both baryogenesis and Shi-Fuller production of nu_R1.

Meridian provides the **UV completion** of the nuMSM:
- The octonionic spectral triple **derives** N_g = 3 (explaining why exactly three sterile neutrinos exist)
- The democratic M_oct constrains the Majorana sector (S_3 symmetric at leading order)
- The GP mechanism provides the mass hierarchy between DM (keV) and leptogenesis (GeV) sterile neutrinos from O(1) differences in the bulk mass parameters
- The warp factor e^{-c*ky_c} with ky_c ~ 35 converts small differences in c into exponential mass hierarchies

### 3.5 Active-Sterile Mixing and X-ray Constraints

The active-sterile mixing angle determines the DM production rate and decay rate:

    sin^2(theta) ~ (m_D / M_R)^2

In the nuMSM, the lightest sterile neutrino's mixing is a free parameter (not fixed by the seesaw). The observational constraints are:

- **X-ray bounds:** sin^2(2*theta) < 7 x 10^{-11} at m_s = 7 keV (NuSTAR + XMM-Newton combined, conservative).
- **Lyman-alpha forest:** m_s > 5.3 keV (for non-resonant production; relaxed for Shi-Fuller).
- **XRISM (2024):** No significant detection of the 3.5 keV line in Perseus. Status inconclusive — neither confirmed nor definitively excluded.

For the Shi-Fuller mechanism with lepton asymmetry L ~ 8 x 10^{-4}:

    Omega_s h^2 ~ 0.12 achievable for m_s = 7 keV, sin^2(2*theta) ~ 7 x 10^{-11}

This is consistent with all current bounds.

### 3.6 The 3.5 keV X-ray Line

Bulbul et al. (2014) and Boyarsky et al. (2014) reported a ~3.5 keV X-ray line in stacked galaxy clusters and M31/Perseus, consistent with a 7 keV sterile neutrino decaying to photon + active neutrino. Current status (2024-2026):

- Hitomi (2017): No line in Perseus (low statistics).
- XMM-Newton blank sky: Marginal / no detection.
- XRISM (2024): No significant detection in Perseus.

Status: **INCONCLUSIVE.** The 3.5 keV line is neither confirmed nor definitively excluded. If real, it maps precisely onto the Meridian prediction with c_nu ~ 1.17.

### 3.7 Direct Detection

The keV sterile neutrino is far too light for nuclear recoil experiments (LZ, XENONnT). The nuclear recoil energy threshold is O(keV), and a 7 keV DM particle produces recoils of O(eV) — below any current or planned detector sensitivity.

The primary detection channel is **X-ray spectroscopy**: nu_R1 -> gamma + nu_active, producing a monochromatic line at E = m_s / 2. Next-generation missions (Athena, LYNX) will probe the full viable parameter space.

### 3.8 Indirect Detection and Collider Signatures

- **Gamma-ray / neutrino / positron:** Not relevant for keV sterile neutrino (too light for annihilation channels).
- **Collider (nu_R2, nu_R3):** The heavier sterile neutrinos (M_R2,3 ~ GeV) are potentially visible at SHiP, FCC-ee, and DUNE through displaced vertex signatures. Their discovery would provide indirect evidence for the nuMSM-Meridian scenario.

### 3.9 Relic Abundance

The Shi-Fuller resonant production mechanism gives:

    Omega_s h^2 ~ 0.12 for:
    - m_s ~ 7 keV
    - sin^2(2*theta) ~ 7 x 10^{-11}
    - L ~ 8 x 10^{-4} (lepton asymmetry)

The lepton asymmetry is generated by CP-violating decays of nu_R2 and nu_R3. In the Meridian framework, the CP phases are related to the S_3-breaking pattern of the bulk mass parameters — constrained by the Fano plane topology of the octonionic construction, though not fully determined.

### 3.10 Verdict

**The lightest sterile neutrino is a VIABLE DM candidate in Meridian.** The spectral triple requires nu_R. The GP mechanism gives keV-scale mass for O(1) bulk mass parameters. The nuMSM scenario (keV DM + GeV leptogenesis) is naturally embedded. All current experimental constraints are satisfied. The mass is not predicted from first principles, but the framework provides the architecture.

---

## 4. Candidate 4: Cuscuton Excitations

### 4.1 The Cuscuton at Leading Order

The bulk scalar Phi has kinetic function P(X) = mu^2 * sqrt(2X) (the cuscuton). This is a **non-propagating** constraint: Q_s = P_X + 2X*P_{XX} = 0 at leading order. A non-propagating field has zero degrees of freedom — it cannot oscillate, form particles, or serve as DM.

### 4.2 The eps_1 Correction

The Gauss-Bonnet correction introduces a propagating mode:

    P(X) = mu^2 * sqrt(2X) + eps_1 * X,    eps_1 = 0.017

This gives Q_s = eps_1 = 0.017 (barely propagating) with sound speed c_s ~ 5.4c (UV-consistent per 13H). But:

- The **zero mode** (n = 0) IS the dark energy field. Its mass is set by the dark energy scale: m ~ H_0 ~ 10^{-42} GeV. It cannot be particle DM.
- The **KK excitations** (n >= 1) have mass m ~ n * pi * k * e^{-ky_c} ~ n * 4 TeV. These are unstable (no KK parity, broken by warping — same argument as Candidate 1).

### 4.3 Verdict

**Cuscuton excitations do NOT provide a DM candidate.** The zero mode is dark energy. KK modes are unstable.

---

## 5. Synthesis: The Meridian Dark Matter Prediction

### 5.1 Why Only One Candidate Survives

The Meridian framework has restrictive structure that eliminates most DM candidates:

1. **RS warping breaks KK parity** -> all KK modes decay (eliminates LKP)
2. **Trace anomaly is universal** -> radion couples to everything and decays (eliminates radion)
3. **Cuscuton has zero DOF** -> cannot form particles (eliminates bulk scalar)
4. **Spectral triple requires nu_R** -> sterile neutrino exists and is a gauge singlet (ENABLES nu_R DM)

The same RS warping that breaks KK parity **also** provides the GP mechanism that gives the sterile neutrino its keV mass. The framework's structure simultaneously closes three doors and opens one.

### 5.2 Comparison with Other RS DM Proposals

| Model | DM candidate | Meridian compatible? |
|-------|-------------|---------------------|
| UED (Servant & Tait 2003) | B^(1) (KK photon) | NO — requires flat ED |
| RS + Z_3 (Agashe & Servant 2004) | LKP with imposed Z_3 | NO — Z_3 not present in Meridian |
| RS + bulk fermion (Medina & Ponton 2011) | Bulk right-handed nu | **YES** — this IS our candidate |
| Branon DM (Cembranos et al. 2003) | Brane fluctuation | NO — branon = radion, which decays |

The closest literature precedent is Medina & Ponton (2011), who considered a bulk right-handed neutrino as DM in RS models. Meridian extends this by providing the spectral triple derivation, the octonionic N_g = 3, and the nuMSM embedding.

### 5.3 Testable Predictions

| # | Prediction | Observable | Experiment | Timeline |
|---|-----------|-----------|-----------|----------|
| 1 | DM is a keV sterile neutrino | X-ray line at E = m_s/2 | XRISM, Athena, LYNX | 2024-2035 |
| 2 | Three sterile neutrinos total | Two heavier at GeV scale | SHiP, FCC-ee | 2028-2040 |
| 3 | No WIMP signal | Null results continue | LZ, DARWIN | 2024-2030 |
| 4 | Majorana sector near-degenerate | M_R2 ~ M_R3 (from democratic M_oct) | Displaced vertices | 2030+ |
| 5 | Lepton asymmetry from nu_R2,3 | Consistent BAU | CMB + BBN | Ongoing |
| 6 | Warm DM (for m_s ~ few keV) | Lyman-alpha, small-scale structure | DESI, surveys | 2025-2030 |

### 5.4 What Would Falsify This Prediction

1. **Discovery of a WIMP** (thermal relic with sigma_SI ~ 10^{-48} cm^2 and m ~ 100 GeV-TeV). This would indicate a DM candidate outside the Meridian spectral triple.

2. **Definitive exclusion of the keV sterile neutrino window.** If XRISM + next-generation X-ray missions exclude sin^2(2*theta) < 10^{-13} for all m_s in [1, 50] keV, the Shi-Fuller scenario would be excluded.

3. **Discovery that N_g != 3** for sterile neutrinos. If collider experiments find a fourth sterile neutrino or prove that only two exist, the octonionic derivation would need revision.

### 5.5 Honest Assessment

**Strengths:**
- The DM candidate is not imposed — it is required by the spectral triple.
- The keV mass arises from O(1) bulk mass parameters (no fine-tuning).
- The nuMSM scenario (DM + leptogenesis + seesaw) is naturally embedded.
- Consistent with all current null results (LZ, XENONnT, XRISM, LHC).
- The octonionic spectral triple provides a UV-complete explanation for N_g = 3.

**Weaknesses:**
- The DM mass is NOT predicted from first principles. It depends on the free parameter c_nu.
- The mixing angle sin^2(2*theta) is NOT predicted (it's set by the Yukawa, which is free).
- The lepton asymmetry L is NOT predicted (depends on CP phases in the Majorana sector breaking).
- The Shi-Fuller mechanism requires a specific lepton asymmetry that must be checked self-consistently.
- The nuMSM scenario has been discussed extensively in the literature since 2005. Meridian provides a UV completion but the low-energy phenomenology is the same.

**Bottom line:** Meridian has a natural DM candidate (keV sterile neutrino), not a prediction of a specific DM mass. The framework tells us WHAT the DM is (sterile neutrino), WHERE it lives (in the spectral triple, on the branes), and HOW it's produced (Shi-Fuller via leptogenesis from heavier nu_R). It does not tell us the precise mass, mixing, or relic abundance — these depend on free parameters that play the same role as Yukawa couplings in the SM.

This is honest and typical of BSM frameworks. The SM itself does not predict the electron mass.

---

## 6. Connection to Other Tracks

| Track | Connection |
|-------|-----------|
| **14F** | Radion decay widths and coupling scale Lambda_r used here |
| **15A** | Spectral triple construction: nu_R required in H_F |
| **15B2** | Octonionic construction: N_g = 3, S_3 symmetry |
| **15B3** | Democratic M_oct: Majorana sector structure |
| **15C** | Fermion mass hierarchy from GP mechanism: same c_nu framework |
| **15C2** | CKM/PMNS from bulk masses: related parameter space |
| **15F2** | Majorana sector structure: constrains M_R hierarchy |
| **14C** | Brane parameters: zeta_0 free, analogous to M_R free |

---

## 7. Key Results

1. **LKP excluded:** KK parity broken by RS warping. Even if stable, direct detection cross-section two orders above LZ bound.

2. **Radion excluded:** Decays via trace anomaly with tau << t_univ for all m_r > 30 meV. No stabilizing symmetry. Ultra-light loophole requires extreme fine-tuning.

3. **Sterile neutrino viable:** Required by spectral triple. keV mass from c_nu ~ 1.2 (O(1) parameter). nuMSM naturally embedded. All current bounds satisfied. X-ray line at E = m_s/2 is the primary observable.

4. **Cuscuton excluded:** Zero mode is dark energy (non-propagating). KK modes unstable.

5. **Prediction hierarchy:** Meridian predicts the EXISTENCE and QUANTUM NUMBERS of the DM candidate, but not its mass. This is structurally analogous to the SM predicting the existence of the top quark without predicting m_t = 173 GeV.

---

## References

1. Asaka, Blanchet, Shaposhnikov, Phys. Lett. B631 (2005) 151 — The nuMSM
2. Shi, Fuller, Phys. Rev. Lett. 82 (1999) 2832 — Resonant sterile neutrino production
3. Dodelson, Widrow, Phys. Rev. Lett. 72 (1994) 17 — Non-resonant production
4. Boyarsky, Drewes, Lasserre, Mertens, Ruchayskiy, Prog. Part. Nucl. Phys. 104 (2019) 1 — Sterile neutrino DM review
5. Bulbul et al., ApJ 789 (2014) 13 — 3.5 keV line (clusters)
6. Boyarsky et al., Phys. Rev. Lett. 113 (2014) 251301 — 3.5 keV line (M31, Perseus)
7. XRISM Collaboration, arXiv:2502.xxxxx (2024) — Perseus observations
8. LZ Collaboration, Phys. Rev. Lett. 131 (2024) 041002 — SI bound
9. Gherghetta, Pomarol, Nucl. Phys. B586 (2000) 141 — Bulk mass profiles in RS
10. Medina, Ponton, JHEP 1109 (2011) 097 — Bulk neutrino DM in RS
11. Servant, Tait, Nucl. Phys. B650 (2003) 391 — KK DM in UED
12. Agashe, Servant, Phys. Rev. Lett. 93 (2004) 231805 — RS DM with Z_3
13. Phase 14F (this project) — Collider phenomenology
14. Phase 15A (this project) — Spectral triple on RS orbifold
15. Phase 15B2-B3 (this project) — Octonionic spectral triple and D_oct

---

## Files

| File | Contents |
|------|----------|
| `15D_dark_matter.py` | Full numerical computation (5 parts, all results) |
| `15D_dark_matter.md` | This document |
