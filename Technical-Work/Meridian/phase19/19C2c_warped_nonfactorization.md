# Track 19C.2c — Warped Spectral Action Non-Factorization

**Project Meridian Phase 19 | Clayton W. Iggulden-Schnell & Clawd**
**Date:** March 22, 2026
**Status:** COMPLETE
**Verdict:** PIVOT (to threshold corrections, Track 19C.3)

---

## Context

The spectral action on a flat background (M^4 x F) gives universal gauge kinetic coefficients, predicting sin^2(theta_W) = 3/8 at the cutoff. Previous tracks established:

- **19C.1:** Standard one-loop SM running from sin^2 = 3/8 fails to match experiment at M_Z with the correct alpha_s. The "unification triangle" doesn't close.
- **19C.2:** Asymptotic safety corrections are universal (same for all gauge groups) and cannot break the degeneracy.
- **19C.2b:** Brane kinetic terms (BKTs) have the wrong sign to help.

**This track** asks: Does the warped geometry itself break the universality through mass-dependent non-factorization of the spectral action trace?

---

## 1. Mass-Weighted Traces S_i

On a warped background, the heat kernel trace does not factorize:

    Tr(e^{-tD^2}) =/= Tr_M(e^{-t D_M^2}) * Tr_F(e^{-t D_F^2})

The leading mass-dependent correction to the gauge kinetic coefficient for group G_i is proportional to:

    S_i = sum_f m_f^2 * c_i(f)

where c_i(f) is the contribution coefficient of Dirac fermion f to group i.

### Coefficient Table (per Dirac fermion)

| Fermion type | c_3 | c_2 | c_1 (raw) | c_1 (GUT) |
|:---|---:|---:|---:|---:|
| Up-type quark | 3/2 | 3/2 | 17/12 | 85/36 |
| Down-type quark | 3/2 | 3/2 | 5/12 | 25/36 |
| Charged lepton | 0 | 1/2 | 5/4 | 25/12 |

Key structural fact: **c_3 = c_2 = 3/2 for all quarks.** The SU(3) and SU(2) traces receive identical quark contributions. The asymmetry between S_2 and S_3 comes exclusively from charged leptons (which contribute to SU(2) but not SU(3)).

### Mass-Weighted Traces (fermions only)

| Trace | Value (GeV^2) | Dominant contribution |
|:---|---:|:---|
| S_3 | 44922.14 | top quark (99.94%) |
| S_2 | 44923.73 | top quark (99.93%) |
| S_1 (GUT) | 70688.24 | top quark (99.68%) |

The entire calculation is dominated by the top quark mass. All other fermions contribute at the sub-percent level.

---

## 2. Universal Traces a_i

Per generation of Weyl fermions:

| Multiplet | d_3 | d_2 | Y | T_3 * d_2 | d_3 * T_2 | d_3 * d_2 * Y^2 |
|:---|---:|---:|---:|---:|---:|---:|
| Q_L | 3 | 2 | 1/6 | 1 | 3/2 | 1/6 |
| u_R | 3 | 1 | 2/3 | 1/2 | 0 | 4/3 |
| d_R | 3 | 1 | 1/3 | 1/2 | 0 | 1/3 |
| L | 1 | 2 | 1/2 | 0 | 1/2 | 1/2 |
| e_R | 1 | 1 | 1 | 0 | 0 | 1 |
| **Total/gen** | | | | **2** | **2** | **10/3** |

With GUT normalization (5/3 factor on U(1)):

| Coefficient | Per generation | Total (N_g = 3) |
|:---|---:|---:|
| a_3 | 2 | 6 |
| a_2 | 2 | 6 |
| a_1 (GUT) | 50/9 = 5.556 | 50/3 = 16.667 |

**a_3 = a_2, but a_1(GUT) /= a_3.** The ratio a_1(GUT)/a_3 = 25/9 = 2.778.

This reflects the well-known fact that the raw Dynkin index traces do not equalize. The spectral action prediction sin^2(theta_W) = 3/8 comes from the *coupling* relation g_1 = g_2 at the cutoff (with g_1 = sqrt(5/3) g'), which is a property of the spectral triple's algebra structure, not a trace equalization.

---

## 3. The S_2/S_3 Ratio (Not the "Color Factor 3/2")

**Structural theorem:**

    S_2 = S_3 + (1/2) * sum_leptons m_l^2

**Proof:** Every quark contributes c_3 = c_2 = 3/2 to both SU(3) and SU(2). Leptons contribute c_3 = 0 (color singlet) but c_2 = 1/2 (weak doublet). Therefore:

    S_3 = (3/2) * sum_quarks m_q^2
    S_2 = (3/2) * sum_quarks m_q^2 + (1/2) * sum_leptons m_l^2

The ratio:

    S_2/S_3 = 1 + sum(m_l^2) / (3 * sum(m_q^2))
            = 1 + 3.17 / (3 * 29948)
            = 1 + 3.53 x 10^{-5}
            = 1.0000353

**The hypothesized "3/2 color factor" does NOT appear.** The S_2/S_3 ratio is essentially unity because the top quark mass overwhelms all lepton masses. The SU(2)-SU(3) splitting from mass-weighted traces is negligible (0.004%).

---

## 4. The S_1(GUT)/S_3 Ratio

In the top-dominated limit:

    S_1(GUT)/S_3 -> c_1(GUT, up-type) / c_3(up-type) = (85/36) / (3/2) = 85/54 = 1.5741

**Computed:** S_1(GUT)/S_3 = 1.5736 (matches the top-limit prediction to 0.03%)

This is the only significant non-trivial ratio. The U(1) mass-weighted trace is ~57% larger than the SU(3) trace, driven by the large hypercharge of u_R (Y = 2/3).

---

## 5. Boundary Non-Factorization Correction

The warped geometry introduces a mass-dependent correction to the gauge kinetic terms:

    1/g_i^2(Lambda) propto a_i * [1 + epsilon * S_i / (Lambda^2 * a_i)]

where epsilon depends on the warp factor geometry.

### The Sign Problem

For the correction to give a_1^eff/a_3^eff < 1 (as needed for unification), we need S_1(GUT) < S_3. But:

    S_1(GUT) = 70688 GeV^2 > S_3 = 44922 GeV^2

**Positive epsilon pushes the ratio the wrong way.** To achieve the target a_1/a_3 = 0.77, we would need epsilon < 0 (or equivalently, the warp factor geometry would need to give a negative mass correction to the heavier group), which is non-standard.

### Scan Results (at Lambda = 10^17 GeV)

| epsilon/Lambda^2 (GeV^-2) | a_1^eff/a_3^eff | a_2^eff/a_3^eff | sin^2(theta_W) at cutoff |
|---:|---:|---:|---:|
| +10^{-6} | 1.00426 | 1.0000 | 0.3740 |
| +10^{-5} | 1.0400 | 1.0000 | 0.3659 |
| -10^{-5} | 0.9536 | 1.0000 | 0.3862 |
| -10^{-4.5} | 0.822 | 1.000 | 0.422 |
| -10^{-3.5} | (diverges) | 1.000 | (unphysical) |

The correction to a_2/a_3 is always negligible (because S_2 ~ S_3 to 0.004%). The entire lever arm is between SU(3) and U(1).

### With Running Enhancement (ky_c = 35)

The RS warp factor amplifies the boundary correction by the factor ky_c ~ 35. This reduces the required bare epsilon by a factor of 35, but **does not change the sign problem.** The correction still pushes a_1/a_3 in the wrong direction for positive epsilon.

---

## 6. The sin^2(theta_W) Precision Test

### Spectral Action Prediction

The spectral action predicts sin^2(theta_W) = 3/8 = 0.375 at the cutoff Lambda. Running down to M_Z with one-loop SM beta coefficients:

    b_1 = 41/10,   b_2 = -19/6,   b_3 = -7

### Results: sin^2(theta_W) at M_Z

**Method 1:** Assume unified coupling, determine alpha_U from measured alpha_3:

| Lambda (GeV) | alpha_GUT^{-1} | sin^2(M_Z) predicted | Error |
|---:|---:|---:|---:|
| 10^{15} | 41.93 | 0.2072 | -10.4% |
| 10^{16} | 44.49 | 0.2051 | -11.3% |
| 10^{17} | 47.06 | 0.2032 | -12.1% |
| 10^{18} | 49.62 | 0.2015 | -12.9% |

**Method 2:** Determine alpha_U from measured alpha_2, enforce g_1 = g_2 at cutoff:

| Lambda (GeV) | sin^2(M_Z) predicted | Error | alpha_s predicted | alpha_s measured |
|---:|---:|---:|---:|---:|
| 10^{14} | 0.2195 | -5.1% | 0.088 | 0.118 |
| 10^{15} | 0.2077 | -10.2% | 0.116 | 0.118 |
| 10^{16} | 0.1961 | -15.2% | 0.170 | 0.118 |
| 10^{17} | 0.1846 | -20.2% | 0.318 | 0.118 |

### The Unification Triangle

The three gauge couplings, run with SM one-loop RGEs, do not meet at a single point:

| Pair | Crossing scale |
|:---|---:|
| alpha_1 = alpha_2 | 10^{13.0} GeV |
| alpha_2 = alpha_3 | 10^{17.0} GeV |

The famous 4-order-of-magnitude gap. At 10^{13} GeV, the sin^2 prediction matches experiment exactly (tautologically -- that's where the 1-2 lines cross by definition). At 10^{17} GeV (the Meridian RS scale), the prediction is 12-20% off.

### Boundary Correction to sin^2

At Lambda = 10^{17} GeV:

| epsilon/Lambda^2 | sin^2 at cutoff | sin^2 at M_Z | Error |
|---:|---:|---:|---:|
| 0 (baseline) | 0.3750 | 0.2031 | -12.2% |
| +10^{-5} | 0.3737 | 0.2025 | -12.4% |
| -10^{-5} | 0.3763 | 0.2037 | -11.9% |
| -10^{-4.5} | 0.3791 | 0.2050 | -11.3% |

The boundary correction shifts sin^2 by at most ~1% for reasonable epsilon values. It cannot close the ~12% gap.

---

## 7. Honest Assessment

### What Works

1. **The spectral action predicts sin^2(theta_W) = 3/8.** This is a genuine prediction from the NCG spectral triple, not an input. It's the same prediction as SU(5) GUT but derived from a completely different structure (the algebra axioms of the spectral triple, not an embedding group).

2. **The prediction is approximately right.** sin^2 = 0.375 at the cutoff runs to ~0.20-0.22 at M_Z depending on the cutoff scale, vs measured 0.231. Within 10-20%. For a UV-complete framework with ONE free parameter (Lambda), this is respectable.

3. **The structural analysis is clean.** The mass-weighted traces are completely dominated by the top quark. The S_2/S_3 = 1 + O(m_tau^2/m_t^2) result is a theorem, not a numerical accident. The S_1/S_3 = 85/54 ratio in the top limit is exact.

### What Doesn't Work

1. **The boundary non-factorization has the wrong sign.** S_1(GUT) > S_3, so the mass-dependent correction from warping pushes a_1/a_3 > 1, opposite to the 0.77 target. This is structural: the top quark's large hypercharge (Y = 2/3 for u_R) makes the U(1) mass trace ~57% larger than the SU(3) trace.

2. **The correction is too small.** Even with the ky_c ~ 35 enhancement, the boundary non-factorization gives O(1%) effects on sin^2(theta_W), while the gap is O(10%).

3. **SM running alone cannot close the triangle.** This is the standard result shared with minimal SU(5). The three coupling lines do not meet at a single point with SM particle content.

### The "3/2 Color Factor Theorem" — Falsified

The hypothesized S_2/S_3 = 3/2 does not hold. The actual ratio is S_2/S_3 = 1.000035. This is because:
- Quarks contribute identically to S_2 and S_3 (both get c = 3/2)
- The only difference comes from charged leptons (c_2 = 1/2, c_3 = 0)
- Lepton masses are negligible vs the top quark

The "color factor" is already baked into the quark coefficients symmetrically. There is no additional factor of 3/2 between SU(2) and SU(3) in the mass-weighted traces.

---

## 8. What This Means for Meridian

The spectral action's sin^2(theta_W) = 3/8 prediction is a **feature of the framework**, not a crisis. It's the same prediction that any GUT-like theory makes, and the ~10% discrepancy with experiment is the same one that motivates the MSSM in conventional GUT phenomenology.

For Meridian specifically, three mechanisms could close the gap:

### (a) KK Threshold Corrections (most promising)
The RS orbifold has a tower of Kaluza-Klein modes. These contribute to the running between the compactification scale (1/R ~ TeV) and the cutoff (k ~ M_Pl). The KK modes have different multiplicities under each gauge group (because they have bulk quantum numbers), giving **group-dependent threshold corrections** that can split the couplings.

This is the natural next computation: **Track 19C.3 — KK threshold corrections to gauge coupling running.**

### (b) NCG Spectral Triple Modifications
Chamseddine-Connes-Marcolli showed that including the right-handed neutrino and the Majorana mass scale introduces an intermediate scale that modifies the running. The "big desert" between M_Z and M_GUT is partially populated, changing the effective beta coefficients.

### (c) Two-Loop + Threshold Matching
Two-loop corrections and proper matching at the weak scale reduce the discrepancy by a few percent. Combined with (a) or (b), this may suffice.

---

## 9. Verdict: PIVOT

**Not MATCH:** The boundary non-factorization alone cannot explain gauge coupling unification. The correction is too small and has the wrong sign for the primary ratio.

**Not KILL:** The spectral action sin^2 = 3/8 prediction is approximately correct and represents the same situation as all GUT-like theories. The framework is not falsified — it needs the same kind of threshold corrections that every unification framework needs.

**PIVOT to Track 19C.3:** KK tower threshold corrections. The RS orbifold's KK modes provide a natural, calculable mechanism for group-dependent corrections to the running. This is where the warped geometry can actually help — not through the trace non-factorization, but through the tower of massive states it predicts.

---

## Key Files

- **Script:** `phase19/19C2c_warped_nonfactorization.py`
- **Previous tracks:** `19C1_gauge_unification.md`, `19C2_as_gauge_splitting.md`, `19C2b_bkt_computation.md`
- **Next:** Track 19C.3 — KK threshold corrections

---

*Track 19C.2c complete. The trace non-factorization is real but insufficient. The KK tower is the right lever.*
