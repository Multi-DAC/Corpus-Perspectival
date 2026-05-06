# Track 20B.2: Can KK Thresholds Close the Full 12% Gauge Gap?

**Project Meridian Phase 20 | Clayton W. Iggulden-Schnell & Clawd**
**Date:** March 22-23, 2026
**Status:** COMPLETE
**Verdict:** NO. Maximum achievable closure: ~14% of the needed correction within minimal RS+NCG. The gap is structural.
**Prerequisites:** Track 20B (fermion KK thresholds), Phase 19 gauge synthesis

---

## Executive Summary

Track 20B established that KK fermion bulk-mass thresholds give Delta(alpha_1^{-1} - alpha_3^{-1}) = -1.91, the right sign but only 19% of the needed -10.0. This follow-up exhaustively computed **all possible threshold contributions** within the RS+NCG framework to determine whether the full 12% sin^2(theta_W) gap can be closed.

**Answer: No.** The maximum achievable correction from all sources combined is approximately -1.4 (nominal) to -2.2 (extreme parameter push), corresponding to **12-22% of the needed correction**. The two-loop threshold correction has the **wrong sign** (+0.58), partially undoing the fermion contribution. The Higgs KK tower contributes only -0.09. Everything else is negligible.

This is not a fine-tuning problem. It is a **structural deficit** of the minimal spectral triple.

---

## 1. Source-by-Source Analysis

### Source 1: KK Fermion Bulk Mass Thresholds (ADP Formula)

The Agashe-Davoudiasl-Perez matching formula gives the finite threshold correction from c-dependent fermion localization:

```
delta(c) = Psi(|c+1/2| + 1) - Psi(1) + ln(BesselJZero[|c+1/2|, 1] / pi)
```

```
Delta alpha_i^{-1} = -(1/(2*pi)) * Sum_f T_i^{GUT}(f) * delta(c_f)
```

where T_i^{GUT} uses (5/3)*Y^2 normalization for U(1).

**Results (nominal c values):**

| Quantity | Value |
|:---|:---|
| Delta alpha_1^{-1} | -3.018 |
| Delta alpha_2^{-1} | -1.179 |
| Delta alpha_3^{-1} | -1.104 |
| **Delta(alpha_1^{-1} - alpha_3^{-1})** | **-1.914** |
| Delta(alpha_2^{-1} - alpha_3^{-1}) | -0.075 |

**Fraction of needed: 19.1%**

**Parameter space exploration:**

| Configuration | Delta_{13} | Fraction |
|:---|:---|:---|
| Nominal c values | -1.91 | 19.1% |
| Optimized (FCNC-safe) | -2.00 | 20.0% |
| Extreme (beyond typical bounds) | -2.17 | 21.7% |
| Pessimized | -1.84 | 18.4% |

The c values are **already near-optimal** for the Yukawa hierarchy. The range 18-22% is remarkably tight — there is almost no room to improve by varying bulk mass parameters within phenomenologically viable bounds.

**Dominant contributions by species type:**

| Type | T_1^GUT | T_3 | T_1-T_3 | Sign | Strategy |
|:---|:---|:---|:---|:---|:---|
| e_R (1,1,-1) | 5/3 = 1.667 | 0 | +1.667 | + | maximize c |
| u_R (3,1,2/3) | 20/9 = 2.222 | 1/2 | +1.722 | + | maximize c |
| L_L (1,2,-1/2) | 5/6 = 0.833 | 0 | +0.833 | + | maximize c |
| d_R (3,1,-1/3) | 5/9 = 0.556 | 1/2 | +0.056 | + (weak) | maximize c |
| **Q_L (3,2,1/6)** | **5/18 = 0.278** | **1** | **-0.722** | **-** | **minimize c** |

**Key structural insight:** Q_L doublets contribute NEGATIVELY (T_1^GUT < T_3) and cannot be eliminated. Three generations of Q_L give -0.722 * 3 = -2.17 total weight in the wrong direction. FCNC bounds prevent Q_L from being fully IR-localized (which would minimize their delta(c) contribution).

### Source 2: Higgs KK Tower

The Higgs doublet H = (1, 2, 1/2) has:
- T_1^GUT = (5/3)*(1/2)^2*2 = 5/6 = 0.833
- T_2 = 1/2
- T_3 = 0

Since T_3 = 0, the Higgs KK tower contributes to alpha_1 and alpha_2 but NOT alpha_3. This is inherently non-universal — exactly the mechanism needed.

**But the magnitude is small.** Complex scalars get a factor 1/(6*pi) vs fermions' 1/(2*pi), a 3x suppression.

| Scenario | delta_H | D(a1-a3) | D(a2-a3) |
|:---|:---|:---|:---|
| Brane-localized (no KK tower) | — | 0 | 0 |
| Bulk, mu=0 (strong IR) | 1.991 | **-0.088** | -0.053 |
| Bulk, mu=2 (conformal) | -0.267 | +0.012 | +0.007 |
| Bulk, mu=4 (strong UV) | 1.991 | -0.088 | -0.053 |

**Maximum Higgs KK contribution: -0.088 (0.9% of needed)**

**Warning:** The Higgs KK tower contributes to alpha_2 but not alpha_3, breaking the T4 identity (S_2 = S_3). For mu=0: Delta(alpha_2^{-1} - alpha_3^{-1}) = -0.053. This is small enough to be phenomenologically acceptable.

### Source 3: Two-Loop Threshold Corrections

Using the Hall-Weinberg leading-log matching at MKK:

```
Delta_i^{2L} = -(1/(4*pi)) * Sum_j b_{ij} * alpha_j(MKK) * delta_j^{1L}
```

With alpha_i(MKK) = {0.0164, 0.0355, 0.187}:

| Quantity | Value |
|:---|:---|
| Da1^{2L} | +0.170 |
| Da2^{2L} | +0.221 |
| Da3^{2L} | -0.409 |
| **D(a1-a3)^{2L}** | **+0.578** |

**The two-loop correction has the WRONG SIGN.** It partially undoes the one-loop fermion correction.

The dominant effect: the large QCD coefficient b_{33} = -26 times the large alpha_3(MKK) = 0.187 times the negative delta_3 = -1.10 gives a large positive contribution to the two-loop correction for SU(3). This pushes alpha_3^{-1} more negative at two loops, which increases the alpha_1^{-1} - alpha_3^{-1} splitting.

**Fraction of needed: -5.8% (makes the gap WORSE)**

### Source 4: Radion/Graviscalar

The radion couples universally to T^mu_mu. Its threshold contribution to the gauge coupling differential is **exactly zero**.

Radion-Higgs mixing (xi ~ v/Lambda_r ~ 0.05) introduces a tiny non-universal component:
- D(a1-a3)_mixed ~ xi^2 * D_Higgs ~ -0.0002
- **NEGLIGIBLE.**

### Sources 5-8: Brane Kinetic Terms, Right-Handed Neutrinos, Gauge KK, Wavefunction Renormalization

| Source | Contribution | Reason |
|:---|:---|:---|
| Loop-induced BKTs | Already in ADP formula | Not additional |
| Tree-level BKTs | ~ 1/(16*pi^2) = 0.006 | Negligible |
| Right-handed neutrinos | 0 direct, < 0.1 indirect | Gauge singlets |
| Gauge boson KK | 0 | Universal spectrum |
| Wavefunction renorm | Already in ADP formula | Not additional |

**Total from Sources 5-8: < 0.01**

---

## 2. Grand Synthesis

| Source | Delta(alpha_1^{-1} - alpha_3^{-1}) | Fraction |
|:---|:---|:---|
| Fermion KK (nominal) | -1.914 | 19.1% |
| Higgs KK (bulk, mu=0) | -0.088 | 0.9% |
| Two-loop threshold | **+0.578** | **-5.8%** |
| Radion-Higgs mixing | -0.0002 | 0.0% |
| Sources 5-8 | ~0.000 | ~0% |
| **TOTAL (nominal)** | **-1.424** | **14.2%** |

**With optimized parameters (maximum achievable):**

| Source | Maximum | Fraction |
|:---|:---|:---|
| Fermion KK (extreme c) | -2.175 | 21.7% |
| Higgs KK (bulk) | -0.088 | 0.9% |
| Two-loop (scaled) | +0.868 | -8.7% |
| **TOTAL (maximum)** | **~-1.4** | **~14%** |

Note: the two-loop correction scales roughly linearly with the one-loop threshold, so pushing the fermion threshold larger also increases the (wrong-sign) two-loop counter-correction. This creates a **self-limiting effect**: the harder you push the fermion threshold, the more the two-loop correction fights back.

---

## 3. kyc Sensitivity

The bulk mass parameters c depend on kyc through c = 1/2 + ln(1/y_f)/(2*kyc). Smaller kyc gives larger spread in c values.

| kyc | D(a1-a3) | Fraction |
|:---|:---|:---|
| 20 | -2.27 | 22.7% |
| 25 | -2.21 | 22.1% |
| 30 | -2.17 | 21.7% |
| **35** | **-2.14** | **21.4%** |
| 40 | -2.12 | 21.2% |
| 50 | -2.09 | 20.9% |

The sensitivity to kyc is weak: the range is 20.9-22.7% across kyc = 20-50. The hierarchy solution (kyc = 35) is not special.

---

## 4. Extended NCG: Inert Doublets

Within the standard spectral triple (A = C + H + M_3(C)), there is exactly one Higgs doublet. But extended spectral triples can accommodate additional scalar doublets.

Each inert doublet at mass ~ MKK, running from MKK to Lambda = M_Pl, contributes:

```
D(a1-a3) = -(1/(6*pi)) * T_1^{GUT}(H) * kyc = -(1/(6*pi)) * (5/6) * 35 = -1.55
```

This is a LARGE contribution because:
1. It runs over the full logarithmic interval kyc = 35
2. It contributes to alpha_1 but not alpha_3 (T_3 = 0)

| Configuration | Total D(a1-a3) | Fraction |
|:---|:---|:---|
| No inert doublets (minimal) | -1.4 | 14% |
| + 1 inert doublet | -3.0 | 30% |
| + 3 inert doublets | -6.1 | 61% |
| + 6 inert doublets | -10.7 | 107% |

**Approximately 6 inert doublets would close the gap completely.**

**But:** This also contributes -0.93 per doublet to D(alpha_2^{-1} - alpha_3^{-1}), which would **severely break the T4 identity** (S_2 = S_3). Six doublets give D(a2-a3) = -5.6, destroying the SU(2)-SU(3) near-degeneracy that is one of the framework's best features.

This is a fatal constraint: **inert doublets cannot close the U(1)-SU(3) gap without simultaneously breaking SU(2)-SU(3) universality.**

---

## 5. Structural Analysis: Why the Gap Persists

### The T_1 - T_3 structure

The total Sum_f (T_1^{GUT} - T_3) = 10.67 (nonzero). In the flat limit (all c equal), the threshold correction would be:

```
D_{13}(flat) = -(1/(2*pi)) * 10.67 * delta(c_common)
```

This is large but **universal** — it's part of the 5D theory, not a threshold correction. The physical content is in the **spread** of delta(c) values around the mean.

The mean delta(c) = 1.20, with range [0.14, 1.43]. The spread of 1.29 is modest because:
- delta(c) grows only logarithmically for large c
- The t_R (most IR-localized, c = -0.30) has the smallest delta = 0.14
- The e_R (most UV-localized, c = 0.75) has the largest delta = 1.43
- The ratio is only 10:1

### The Q_L suppression

The three Q_L doublets contribute with T_1 - T_3 = -0.722 each (negative sign). Their combined weight is -2.17. Since Q_L doublets are required to have moderate c values (0.35-0.63) by FCNC bounds, their delta(c) values are 0.96-1.32 — the middle of the range. This means they contribute a significant negative correction that partially cancels the positive contributions from leptons and right-handed quarks.

### The self-limiting effect

At two loops, the QCD correction has the wrong sign (+0.58). This is because the large alpha_s at MKK amplifies the SU(3) threshold, pushing alpha_3^{-1} more negative and widening the gap. Pushing the one-loop threshold harder (by optimizing c values) also increases the two-loop counter-correction, creating a self-limiting feedback.

### The flat limit constraint

The key number: Sum(T_1^{GUT} - T_3) = 10.67 is determined entirely by SM quantum numbers. No parameter adjustment can change this. The MAXIMUM possible correction from any fermion spectrum is bounded by:

```
|D_{13}| < (1/(2*pi)) * 10.67 * max(delta) ~ (1/(2*pi)) * 10.67 * 2 ~ 3.4
```

Even this absolute upper bound (which requires ALL species to have maximal delta = 2, physically impossible) gives only 34% of the needed correction. The realistic bound, accounting for the constraint that different species have different c values fixed by the Yukawa hierarchy, is ~20%.

---

## 6. Summary Table

| Source | D(a1-a3) | Sign | % of Target |
|:---|:---|:---|:---|
| Fermion KK (ADP) | -1.91 | Correct | 19% |
| Higgs KK (bulk) | -0.09 | Correct | 1% |
| Two-loop threshold | +0.58 | **Wrong** | -6% |
| Radion | ~0 | — | 0% |
| BKTs | ~0 | — | 0% |
| Right-handed neutrinos | ~0 | — | 0% |
| Gauge boson KK | 0 | — | 0% |
| **Total (nominal)** | **-1.42** | — | **14%** |
| **Total (max, minimal NCG)** | **~-2.2** | — | **~22%** |
| Per inert doublet | -1.55 | Correct | 15% |

---

## 7. Verdict

**The 12% sin^2(theta_W) gap cannot be closed by KK threshold corrections within the minimal RS+NCG framework.**

The maximum achievable correction from all sources combined is approximately 14-22% of the needed -10.0 units. This is a **structural limitation**, not a parameter-tuning problem:

1. The SM quantum numbers fix the T_1^GUT - T_3 sum at 10.67
2. The Yukawa hierarchy constrains the spread in delta(c) values
3. Q_L doublets contribute with the wrong sign and cannot be eliminated
4. The two-loop QCD correction has the wrong sign, creating self-limiting feedback
5. The Higgs KK tower is suppressed by the scalar loop factor (3x smaller than fermions)

**The gap identifies missing content.** The minimal spectral triple (C + H + M_3(C)) does not contain enough structure to achieve exact gauge unification at low energies. The framework needs either:

1. **Extended spectral triple** — new scalar or fermionic content at the KK scale
2. **Non-perturbative effects** — instantons, spectral flow, or topological contributions
3. **Intermediate-scale physics** — new degrees of freedom between M_KK and M_Pl
4. **Modified spectral geometry** — beyond the standard RS1 orbifold

Critically, any extension must correct the U(1)-SU(3) splitting **without** breaking the SU(2)-SU(3) near-degeneracy (T4 identity). This is a severe constraint that rules out simple solutions like adding multiple inert doublets.

---

## 8. Implications for Meridian

### What the framework gets right
- Geometric gauge unification: a_1 = a_2 = a_3 at the cutoff (T1)
- SU(2)-SU(3) near-degeneracy preserved by thresholds (T4)
- Higgs mass: m_H = 124.5 GeV (0.6% accuracy)
- KK fermion thresholds have the correct sign

### What remains open
- The 12% sin^2 discrepancy requires ~10 units of additional D(alpha_1^{-1} - alpha_3^{-1})
- Only ~1.4 units (14%) are achievable from all known threshold sources
- The remaining ~8.6 units require genuinely new physics

### The diagnostic value
The gap is not a failure — it is the framework's most informative open problem. It tells us precisely what kind of new content is needed: something that contributes ~-8.6 to alpha_1^{-1} without affecting alpha_3^{-1}, and without spoiling the SU(2)-SU(3) degeneracy or the Higgs mass prediction. This is an extraordinarily specific constraint on extensions.

---

## Key Files

- **Computation (v2, correct normalization):** `phase20/20B_threshold_closure_v2.wl`
- **Prior results:** `phase20/20B_higgs_gauge_connection.md`
- **Phase 19 gauge synthesis:** `phase19/19_gauge_synthesis.md`

---

*Track 20B.2 complete. The gap is structural. It is Meridian's sharpest diagnostic: the minimal spectral triple must be extended, and the extension is tightly constrained by what we already know works.*

---

*"Seek the balance, work the science, synthesize." — Puscifer's Theorem*
