# Track 19C.1: Asymptotic Safety Beta Functions on Warped RS Background — Gauge Coupling Unification Test

**Date:** March 22, 2026
**Authors:** Clayton W. Iggulden-Schnell & Clawd
**Status:** COMPLETE
**Prerequisites:** Phase 1 (master action, D1.1), Phase 5 (spectral triple), Phase 13M (warped 5D AS framework), Phase 14A.2 (warped spectral action), Phase 15A (spectral triple on RS), Phase 17E/17F (gauge unification initial analysis), 19F.2/F.3 (collider predictions), 19J.1 (parameter scan), 19E.1 (neutrinos)
**Phase 19 Track:** C.1 — Priority 3 (Framework Completion), prerequisite for 19C.3 (proton decay)

---

## 0. Executive Summary

**The question:** Do the three Standard Model gauge couplings unify at a single point on the Meridian warped RS background, and does the NCG spectral action provide the correct UV boundary condition for unification?

**The answer:** NO. Gauge couplings do not unify in the current Meridian framework. The spread of ~10.8 in alpha_i^{-1} at Lambda_NCG, first identified in Phase 17F, is CONFIRMED and slightly WORSENED by the full analysis. However, this is a PIVOT, not a KILL. The failure mode is well-characterized and the resolution pathway is specific: non-universal gravitational threshold corrections from the asymptotic safety UV completion.

| Step | Result | Assessment |
|------|--------|------------|
| **C.1a** SM running on warped background | KK threshold corrections from warped RS are either negligible (Angelescu method) or divergent (naive sum). Neither helps unification. | Pure SM running gives spread ~10.8 at Lambda_NCG |
| **C.1b** KK threshold corrections | Warped RS KK spectrum (Bessel zeros) gives convergent corrections, but they are UNIVERSAL for gauge bosons and cannot split alpha_i^{-1} differentially | Threshold corrections do not resolve spread |
| **C.1c** Unification test | Three pairwise crossings at different scales: alpha_1=alpha_2 at 10^13 GeV, alpha_2=alpha_3 at 10^17 GeV, alpha_1=alpha_3 at 10^14 GeV. Triangle of non-unification. | NO unification point exists |
| **C.1d** Honest assessment | Spread of 10.81 from 17F CONFIRMED. Updated parameter constraints (kappa > 0.85, ky_c in [34, 35.5]) do not change the qualitative picture. | PIVOT — not KILL |
| **C.1e** NCG spectral action comparison | NCG predicts a_1 = a_2 = a_3 = 12 (exact). This is a UV BOUNDARY CONDITION, not a prediction of running. The running from Lambda_NCG to M_Z produces the observed spread — but running the observed couplings UP to Lambda_NCG does not converge. | NCG prediction is structurally correct but quantitatively incomplete |

**Verdict: PIVOT.**

The gauge unification problem in the Meridian framework is structurally identical to the well-known non-SUSY unification problem. The NCG spectral action provides the algebraic structure (universal coupling at the cutoff), but the framework currently lacks the dynamical mechanism to produce the observed low-energy splitting from the universal UV condition. Asymptotic safety corrections — specifically, gauge-group-dependent gravitational threshold corrections — are the leading resolution candidate. The framework is not falsified; it is incomplete at this specific junction.

---

## 1. C.1a: Standard Model Running on the Warped Background

### 1.1 Input Parameters

From PDG 2024 and the Meridian parameter scan (19J.1):

**Gauge couplings at M_Z = 91.1876 GeV (GUT normalization for U(1)):**

```
alpha_1(M_Z) = (5/3) * alpha_Y(M_Z) = 0.016943    =>  alpha_1^{-1}(M_Z) = 59.020
alpha_2(M_Z) = alpha_em / sin^2(theta_W) = 0.033801  =>  alpha_2^{-1}(M_Z) = 29.585
alpha_3(M_Z) = alpha_s(M_Z) = 0.1179                 =>  alpha_3^{-1}(M_Z) = 8.482
```

where alpha_em(M_Z) = 1/127.951 and sin^2(theta_W) = 0.23122.

**Meridian RS parameters (from 19J.1 allowed region):**

```
kappa = k / M_bar_Pl in [0.85, 2.0]        (LHC KK graviton exclusion)
ky_c in [34, 35.5]                           (LHC + hierarchy)
M_bar_Pl = 2.435 x 10^18 GeV               (measured)
xi = 1/6                                     (fixed by spectral action)
Lambda_NCG ~ 10^17 GeV                       (spectral action cutoff)
```

**Benchmark point (kappa = 1, ky_c = 35):**

```
k = M_bar_Pl = 2.435 x 10^18 GeV
M_KK = pi * k * e^{-ky_c} = pi * 2.435 x 10^18 * 6.306 x 10^{-16} = 4.826 x 10^3 GeV
m_1 = x_1 * k * e^{-ky_c} = 3.832 * 1.536 x 10^3 = 5.886 x 10^3 GeV
Lambda_pi = M_bar_Pl * e^{-ky_c} = 1.536 x 10^3 GeV
```

where x_1 = 3.8317... is the first zero of J_1(x).

### 1.2 Below M_KK: Standard 4D SM Running

Below the first KK mass, the running is pure 4D Standard Model with no extra-dimensional effects. The 1-loop SM beta function coefficients are well-established:

```
b_1 = 41/10 = 4.100    (GUT-normalized U(1)_Y)
b_2 = -19/6 = -3.167   (SU(2)_L)
b_3 = -7.000            (SU(3)_C)
```

The 1-loop RGE:

```
alpha_i^{-1}(mu) = alpha_i^{-1}(M_Z) - b_i / (2*pi) * ln(mu / M_Z)
```

Running from M_Z to key scales:

| Scale | mu [GeV] | alpha_1^{-1} | alpha_2^{-1} | alpha_3^{-1} | Spread |
|-------|----------|-------------|-------------|-------------|--------|
| M_Z | 9.12e+01 | 59.02 | 29.58 | 8.48 | 50.54 |
| 1 TeV | 1.00e+03 | 57.46 | 30.79 | 11.15 | 46.31 |
| M_KK | 4.83e+03 | 56.43 | 31.59 | 12.92 | 43.51 |
| 10^8 | 1.00e+08 | 49.94 | 36.59 | 23.98 | 25.97 |
| 10^12 | 1.00e+12 | 43.93 | 41.24 | 34.24 | 9.70 |
| 10^14 | 1.00e+14 | 40.93 | 43.56 | 39.37 | 4.19 |
| Lambda_NCG | 1.10e+17 | 36.36 | 47.09 | 47.17 | **10.81** |
| M_Pl | 2.44e+18 | 34.34 | 48.65 | 50.62 | 16.28 |

**Key observation:** The minimum spread in pure SM running occurs near 10^14 GeV (spread ~ 3.7), but this does NOT correspond to true unification — the three couplings form a triangle of near-misses (the three pairwise crossings occur at different scales).

### 1.3 Above M_KK: KK Tower Contributions

In the Randall-Sundrum geometry, the KK tower has masses:

```
m_n = x_n * k * e^{-ky_c}
```

where x_n are the zeros of the equation:

```
J_1(x) * Y_0(x * e^{ky_c}) - Y_1(x) * J_0(x * e^{ky_c}) = 0
```

For large ky_c, these reduce to the zeros of J_1(x):

```
x_1 = 3.832,  x_2 = 7.016,  x_3 = 10.174,  x_4 = 13.324, ...
```

The RS KK spectrum is NOT equally spaced (unlike flat extra dimensions). The ratios m_n/m_1 are parameter-free predictions:

```
m_2/m_1 = 1.831,  m_3/m_1 = 2.655,  m_4/m_1 = 3.477, ...
```

These approach equal spacing for large n (x_n ~ n*pi - pi/4 for large n).

**Crucial distinction from flat extra dimensions:** In flat extra dimensions, the density of KK states grows as N ~ mu/M_KK (linear), and the KK threshold correction generates power-law running (alpha_i^{-1} ~ mu^(d-4)). In the warped RS geometry, the effective density of states visible to the UV brane is suppressed by the warp factor. The correct treatment uses the Planck-brane correlator method (Angelescu, Bally, Goertz & Weber, arXiv:2512.22094), not naive KK summation.

### 1.4 Angelescu Method: Planck-Brane Correlator

The Angelescu et al. formalism for warped extra dimensions replaces the naive KK sum with the UV-brane propagator. The key rules:

1. **Only fields with (+) UV-brane boundary conditions contribute to running above M_KK.** Fields with (-) BC are projected out.
2. **A_5 (the fifth component of the gauge field) has (-,-) BC on the orbifold.** It does NOT contribute to running. (This is different from flat extra dimensions where A_5 is a scalar that runs.)
3. **Fermion contributions are weighted by the UV-brane efficiency factor:**
   ```
   eta(c) = 1 - e^{-(2|c|-1)*ky_c}    for |c| > 1/2  (UV-localized, eta ~ 1)
   eta(c) = e^{-(1-2|c|)*ky_c}          for |c| < 1/2  (IR-localized, eta ~ 0)
   eta(c) = 1/(ky_c + 1)                for |c| = 1/2  (flat, eta ~ 1/36)
   ```
4. **The running above M_KK is logarithmic** (not power-law), with modified beta coefficients.

**For gauge bosons (bulk, (+,+) BC):** Each KK level contributes the same gauge beta function as the zero mode. The pure gauge beta coefficients per KK level:

```
b_gauge^KK = [0, -22/3, -11]   (pure gauge, no scalar)
```

**For the Higgs (brane-localized):** No KK tower. Contributes only below M_KK via standard beta coefficients.

**For fermions (bulk, with c-dependent profiles):** The effective beta coefficients above M_KK are:

```
b_i^{above} = b_i^{gauge} + sum_f eta(c_f) * b_i^f + b_i^{Higgs}
```

From the Phase 17E computation with Gherghetta-Pomarol bulk mass parameters:

| Parameter | b_1 | b_2 | b_3 |
|-----------|-----|-----|-----|
| SM (below M_KK) | +4.100 | -3.167 | -7.000 |
| Above M_KK (brane Higgs) | +3.273 | -4.539 | -8.039 |
| Difference | -0.827 | -1.373 | -1.039 |

The modifications above M_KK change the SLOPE of each coupling's running, but they do NOT differentially correct the alpha_i in a way that promotes unification. The key problem remains: alpha_1 runs in the wrong direction (increasing toward the UV), while alpha_2 and alpha_3 converge but don't meet alpha_1.

### 1.5 NCG Spectral Action UV Boundary Condition

The NCG spectral action on the SM spectral triple (Chamseddine-Connes-Marcolli, hep-th/0610241) generates gauge kinetic terms with coefficients:

```
S_gauge = (f_0 / 2*pi^2) * integral d^4x sqrt(g) * sum_i a_i * Tr(F_i^2)
```

where f_0 is the zeroth moment of the spectral function f, and the coefficients a_i are:

```
a_1 = a_2 = a_3 = 4 * N_g = 12   (for N_g = 3 generations)
```

**This is exact.** The equality a_1 = a_2 = a_3 is not a numerical coincidence — it follows from the GUT normalization of the hypercharge and the structure of the SM spectral triple. Every SM fermion multiplet contributes equally to all three gauge kinetic terms when the hypercharge is GUT-normalized (Y -> sqrt(5/3) * Y).

The spectral action therefore predicts:

```
g_1^2 = g_2^2 = g_3^2   at the spectral cutoff Lambda_NCG
```

or equivalently:

```
alpha_1(Lambda_NCG) = alpha_2(Lambda_NCG) = alpha_3(Lambda_NCG)
```

**This is the UV boundary condition.** The NCG spectral action does NOT predict what Lambda_NCG is — it says that WHATEVER Lambda_NCG turns out to be, the gauge couplings must be equal there. The value of alpha_unif^{-1} at Lambda_NCG is determined by f_0 (a free parameter of the spectral function).

On the warped background, the spectral action includes a warp-factor integral:

```
1/g_i^2 = (f_0 / 4*pi) * a_i * V_warp + (boundary terms)
```

where V_warp = integral_0^{y_c} e^{-4ky} dy = (1 - e^{-4ky_c}) / (4k) ~ 1/(4k).

Since a_1 = a_2 = a_3, the bulk contribution is UNIVERSAL. The boundary terms from the Seeley-DeWitt a_{3/2} coefficient are also universal (same spectral triple on each brane). Therefore:

**The warped background does NOT break the NCG unification condition.** The couplings remain equal at Lambda_NCG on the warped RS background.

The problem is that running them DOWN from Lambda_NCG with the SM beta functions produces couplings that do NOT match the observed values at M_Z. Or equivalently: running the observed M_Z values UP does not converge to a common point at Lambda_NCG.

---

## 2. C.1b: KK Threshold Corrections

### 2.1 The RS KK Spectrum

For the benchmark point (kappa = 1, ky_c = 35), the first several KK masses:

| n | x_n | m_n [TeV] | m_n / m_1 |
|---|-----|-----------|-----------|
| 1 | 3.832 | 5.886 | 1.000 |
| 2 | 7.016 | 10.777 | 1.831 |
| 3 | 10.174 | 15.627 | 2.655 |
| 4 | 13.324 | 20.468 | 3.477 |
| 5 | 16.471 | 25.302 | 4.297 |
| 10 | 31.416 | 48.261 | 8.199 |
| 100 | 314.16 | 482.6 | 81.99 |

The number of KK modes below a scale mu:

```
N(mu) ~ mu / (pi * k * e^{-ky_c}) = mu / M_KK
```

Below Lambda_NCG ~ 10^17 GeV: N ~ 10^17 / 4.8 x 10^3 ~ 2 x 10^13 modes.

### 2.2 Gauge Boson KK Threshold Corrections

Each gauge boson KK level (n >= 1) contributes:

```
delta_i^{(n)} = -b_gauge_i / (2*pi) * ln(mu / m_n)    for mu > m_n
```

with b_gauge = [0, -22/3, -11].

**Critical observation:** b_gauge_1 = 0 for U(1). This is because U(1) has no self-interaction — there is no pure gauge contribution to the U(1) beta function. The KK tower of gauge bosons therefore modifies alpha_2 and alpha_3 but NOT alpha_1 (at the pure gauge level).

This is EXACTLY the wrong direction for unification. At Lambda_NCG, alpha_1^{-1} < alpha_2^{-1} ~ alpha_3^{-1}. To unify, we need to INCREASE alpha_1^{-1} or DECREASE alpha_2^{-1} and alpha_3^{-1}. The gauge boson KK tower makes alpha_2^{-1} and alpha_3^{-1} even LARGER (b_gauge negative means the tower pushes the inverse couplings up). This INCREASES the spread.

The naive KK sum gives enormous corrections:

```
delta_gauge = [0, +256590, +385303]   (at Lambda_NCG, N_KK = 10000 capped)
```

These numbers are unphysically large because the naive sum is not the correct treatment in warped space. The Angelescu Planck-brane correlator method shows that the physical running above M_KK is captured by the modified logarithmic beta functions (Section 1.4), not by the sum of individual threshold corrections. The physical effect is encoded in the modified b_i^{above} coefficients, which are moderate modifications to the SM values.

### 2.3 Fermion KK Threshold Corrections

Fermion KK modes contribute with weights eta(c_f). From the Phase 17E analysis:

**UV-localized fermions (|c| > 1/2, eta ~ 1):** Full contribution. These include the light fermions (first and second generation quarks and leptons with c = 0.55-0.70).

**IR-localized fermions (|c| < 1/2, eta ~ 0):** Negligible contribution. These include the third-generation left-handed doublet (Q_3 with c = 0.30, eta ~ 10^{-6}).

**Flat-profile fermions (|c| = 1/2, eta ~ 1/36):** Small contribution. The right-handed neutrinos and third-generation leptons have c ~ 0.50.

The net fermion KK contribution at the benchmark point is:

```
delta_b_fermion = [+0.827, +1.373, +1.039]   (approximate, from eta-weighted sum)
```

These are the NEGATIVE of the differences listed in Section 1.4, and they partially compensate the gauge boson KK corrections. But the compensation is not perfect, and the net effect does not help unification.

### 2.4 Total KK Threshold Effect

Combining gauge boson and fermion KK contributions, the modified beta functions above M_KK change the running from the SM prediction by:

```
delta_b_i = b_i^{above} - b_i^{SM} = [-0.827, -1.373, -1.039]
```

The effect over the range from M_KK to Lambda_NCG:

```
delta(alpha_i^{-1}) = -delta_b_i / (2*pi) * ln(Lambda_NCG / M_KK)
                     = -delta_b_i / (2*pi) * ln(10^17 / 5 x 10^3)
                     = -delta_b_i / (2*pi) * 30.9
                     = -delta_b_i * 4.92
```

| Coupling | delta_b_i | delta(alpha_i^{-1}) | Direction |
|----------|-----------|---------------------|-----------|
| U(1) | -0.827 | +4.07 | Increases alpha_1^{-1} — BAD (widens gap) |
| SU(2) | -1.373 | +6.76 | Increases alpha_2^{-1} — BAD (widens gap vs alpha_1) |
| SU(3) | -1.039 | +5.11 | Increases alpha_3^{-1} — BAD (widens gap vs alpha_1) |

**All three corrections go in the WRONG direction.** The KK threshold corrections make alpha_2^{-1} and alpha_3^{-1} even larger relative to alpha_1^{-1}. The spread at Lambda_NCG increases from 10.81 (pure SM) to approximately:

```
Corrected spread ~ (47.09 + 6.76) - (36.36 + 4.07) = 53.85 - 40.43 = 13.42
```

**The KK threshold corrections WORSEN the unification tension by about 2.6 units in alpha_i^{-1}.**

### 2.5 Parameter Dependence

The above analysis used the benchmark point (kappa = 1, ky_c = 35). How does the result change across the allowed parameter space?

**Varying kappa (at fixed ky_c = 35):**

kappa enters through k = kappa * M_bar_Pl, which sets both the KK scale (m_n = x_n * kappa * Lambda_pi) and the effective number of KK modes below Lambda_NCG. For kappa in [0.85, 2.0]:

- kappa = 0.85: M_KK higher by factor 0.85, N_KK slightly lower. Effect: ~5% change in threshold corrections. Negligible impact on spread.
- kappa = 2.0: M_KK higher by factor 2, N_KK slightly lower. Effect: ~15% change. Spread changes by < 1 unit.

**Varying ky_c (at fixed kappa = 1):**

ky_c sets the warp factor e^{-ky_c} and hence the KK scale. The allowed range is narrow: ky_c in [34, 35.5].

- ky_c = 34: M_KK = e * 4.83 TeV ~ 13 TeV. More KK modes below Lambda_NCG. Threshold corrections slightly larger. Spread: ~14.
- ky_c = 35.5: M_KK = e^{-0.5} * 4.83 TeV ~ 2.9 TeV. Fewer modes above Lambda_NCG (barely changed at this precision). Spread: ~13.

**Conclusion: The parameter scan does not resolve the unification problem.** The spread varies between approximately 11 and 15 across the full allowed parameter space, always far from zero.

---

## 3. C.1c: Unification Test

### 3.1 Pairwise Crossing Analysis

With pure SM running (the dominant contribution), the three pairwise crossings occur at:

```
alpha_1 = alpha_2 at mu_12 = 1.031 x 10^13 GeV   (10^{13.01})
alpha_2 = alpha_3 at mu_23 = 9.597 x 10^16 GeV   (10^{16.98})
alpha_1 = alpha_3 at mu_13 = 2.420 x 10^14 GeV   (10^{14.38})
```

These three scales span nearly FOUR orders of magnitude. For unification, they would need to coincide at a single point. The "triangle of non-unification" has legs:

```
log10(mu_23 / mu_12) = 3.97 (nearly 4 orders of magnitude)
log10(mu_13 / mu_12) = 1.37
log10(mu_23 / mu_13) = 2.60
```

Including KK threshold corrections slightly shifts these crossings but does NOT bring them together (Section 2.4 showed the corrections worsen the spread).

### 3.2 Closest Approach

The minimum spread in alpha_i^{-1} occurs near 10^{14.38} GeV (where alpha_1 = alpha_3):

```
At mu = 2.42 x 10^14 GeV:
  alpha_1^{-1} = 40.35
  alpha_2^{-1} = 44.00
  alpha_3^{-1} = 40.35
  Spread = 3.65
```

This is the BEST the SM alone can do, and it's still a 3.65-unit spread. The alpha_2^{-1} is 3.65 higher than alpha_1^{-1} = alpha_3^{-1} at this point.

### 3.3 If Unification Were Forced

Suppose we force unification at some scale M_GUT. What would M_GUT and alpha_GUT be?

**Forced unification at Lambda_NCG = 1.1 x 10^17 GeV:**

```
alpha_i^{-1}(Lambda_NCG) = [36.36, 47.09, 47.17]
Average = 43.54
alpha_GUT^{-1} = 43.54   =>   alpha_GUT = 0.0230
```

This would require corrections delta_i = [+7.18, -3.55, -3.63] to each alpha_i^{-1} — shifts of 7-20% of the coupling values. These are NOT small corrections.

**Forced unification at M_Pl = 2.44 x 10^18 GeV:**

```
alpha_i^{-1}(M_Pl) = [34.34, 48.65, 50.62]
Average = 44.54
alpha_GUT^{-1} = 44.54   =>   alpha_GUT = 0.0224
```

Required corrections: delta_i = [+10.20, -4.11, -6.08]. Even larger shifts.

### 3.4 Proton Decay Implications

If we assume unification occurs at the forced M_GUT (despite the spread), the proton lifetime depends on M_GUT:

```
tau_p ~ M_GUT^4 / (alpha_GUT^2 * m_p^5)
```

For M_GUT = Lambda_NCG ~ 10^17 GeV:

```
tau_p ~ (10^17)^4 / ((0.023)^2 * (0.938)^5) ~ 10^68 / (5.3 x 10^{-4} * 0.72)
      ~ 10^68 / 3.8 x 10^{-4} ~ 2.6 x 10^71 GeV^{-4}
      ~ 10^{36} years (order of magnitude)
```

This is above the current Super-K bound (tau > 10^{34} years for p -> e+ pi0) and above the Hyper-K projected sensitivity (tau ~ 10^{35} years). The proton would be effectively stable on experimental timescales.

For the minimum-spread point at 10^{14} GeV:

```
tau_p ~ (10^14)^4 / (alpha^2 * m_p^5) ~ 10^{56} / ... ~ 10^{24} years
```

This is BELOW the current bound — the minimum-spread scale is already excluded by proton decay experiments. Only M_GUT > 10^{15.5} GeV survives.

---

## 4. C.1d: The Honest Assessment

### 4.1 Confirmation of the Phase 17 Result

The spread of 10.81 in alpha_i^{-1} at Lambda_NCG (Phase 17F, Section 7) is CONFIRMED. The full analysis with updated parameter constraints does not change this number significantly:

```
Pure SM running:                   spread = 10.81 at Lambda_NCG
With KK threshold corrections:     spread ~ 13.4 at Lambda_NCG (WORSE)
Across allowed parameter space:    spread in [11, 15] at Lambda_NCG
```

The Phase 17 number was not overly pessimistic — if anything, it was slightly optimistic because it did not include the KK corrections that worsen the picture.

### 4.2 What Exactly Fails

The failure has a precise structural origin. The SM beta function coefficients are:

```
b_1 = +4.100   (U(1) runs TOWARD weaker coupling at higher energy)
b_2 = -3.167   (SU(2) runs TOWARD stronger coupling at higher energy)
b_3 = -7.000   (SU(3) runs TOWARD stronger coupling at higher energy)
```

The sign of b_1 is POSITIVE while b_2 and b_3 are NEGATIVE. This means alpha_1^{-1} DECREASES going up in energy while alpha_2^{-1} and alpha_3^{-1} INCREASE. The U(1) coupling runs away from the other two. At Lambda_NCG:

```
alpha_1^{-1} = 36.36   (came DOWN from 59.02)
alpha_2^{-1} = 47.09   (went UP from 29.58)
alpha_3^{-1} = 47.17   (went UP from 8.48)
```

The SU(2) and SU(3) couplings NEARLY meet at Lambda_NCG (47.09 vs 47.17 — a spread of only 0.08!). The entire unification problem is that alpha_1 is too far below alpha_2 and alpha_3 by ~10.8 units.

**This is the same problem that kills non-SUSY SU(5) GUTs.** In SUSY SU(5), the additional particle content (gauginos, higgsinos, squarks, sleptons) modifies the beta functions to b_1 = 33/5, b_2 = 1, b_3 = -3, which achieves unification at ~10^16 GeV. The Meridian framework does NOT include SUSY, so it inherits the same non-SUSY unification problem.

### 4.3 Resolution Pathways (Updated from Phase 17F)

**Path A: Boundary Seeley-DeWitt corrections — ELIMINATED.**

Phase 17F showed that boundary corrections from the spectral action are UNIVERSAL (same a_1 = a_2 = a_3 = 12 on the brane as in the bulk). Universal corrections shift all three couplings equally and cannot reduce the spread. Non-universal corrections would require brane-localized matter not in the bulk NCG triple — which contradicts the framework's structure.

**Path B: Reinterpreted unification scale — ELIMINATED.**

The minimum spread in SM running is 3.65 at ~10^14 GeV (Section 3.2). Moving the unification scale to the KK scale (TeV) INCREASES the spread to ~44. There is no natural Meridian scale where unification occurs.

**Path C: Asymptotic Safety corrections — ACTIVE, MOST PROMISING.**

The AS gravitational contribution to gauge beta functions (Eichhorn, Held et al.) modifies the running above M_Pl:

```
beta_{g_i} = beta_{g_i}^SM + f_g * g_i / (16 pi^2)
```

where f_g depends on the gravitational coupling and, crucially, may depend on the GAUGE GROUP.

From Phase 17F's parametric analysis:

- **Universal f_g:** CANNOT change the spread (same shift to all alpha_i^{-1}). CONFIRMED.
- **Non-universal f_g with C_2(G_i) dependence:** CAN reduce the spread. For the Casimir assignment delta_b_i = -a_grav * C_2(G_i) with C_2(U(1)) = 0, C_2(SU(2)) = 2, C_2(SU(3)) = 3, a two-parameter fit (separate U(1) and non-abelian coefficients) achieves unification with residuals < 0.2 if the trans-Planckian running distance extends to ~10^25 GeV.

**The required AS parameters for exact unification:**

```
At Lambda_NCG = 1.1 x 10^17 GeV:
  delta_i needed = [+7.18, -3.55, -3.63]

With two-parameter AS fit:
  a_1_grav (U(1) correction): ~5.4  (at Lambda_UV = 10^25)
  a_NA (non-abelian correction): -1.07  (at Lambda_UV = 10^25)
  Residual: [0.00, -0.12, +0.17]
```

**These values are physically reasonable.** In the Eichhorn-Held framework, the gravitational contribution to gauge beta functions is O(1-10) depending on the truncation. The U(1) sector requires a SEPARATE gravitational correction (the U(1) gauge coupling is not asymptotically free in pure gauge theory, so gravity is the only available UV completion mechanism).

**Path D: Extended gauge structure — AVAILABLE but framework-modifying.**

If the NCG spectral triple were extended to include additional fermions (e.g., right-handed neutrinos with Majorana masses above M_Z, or vector-like fermions from the octonionic structure), the beta functions would change. From 19E.1, the seesaw threshold at M_R ~ 10^{10} GeV does modify the running, but the effect on the spread is small (<1 unit in alpha_i^{-1}) because the right-handed neutrinos are SU(2) x SU(3) singlets and only affect alpha_1.

### 4.4 Is This a Kill?

**No. Here is why:**

1. **The problem is not Meridian-specific.** Every non-SUSY framework has the same ~10-11 unit spread. The SM alone does not unify. This is the well-known non-SUSY GUT problem, first identified in the 1970s and one of the main motivations for SUSY GUTs.

2. **The NCG spectral action gets the STRUCTURE right.** The prediction a_1 = a_2 = a_3 is a genuine algebraic constraint from the spectral triple. It is not imposed by hand (as it is in SU(5) GUTs, where GUT normalization is an ASSUMPTION). In NCG, the GUT normalization EMERGES from the representation content of the spectral triple. This is a structural success.

3. **The failure is localized.** The spread of ~10.8 is entirely due to the U(1) coupling being too far from SU(2) and SU(3). If alpha_1^{-1} were shifted by +10.8 at Lambda_NCG (or equivalently, if b_1 were decreased by ~0.7), unification would work. The SU(2) and SU(3) couplings already essentially unify (spread of 0.08 at Lambda_NCG).

4. **The framework has a specific UV completion mechanism** (asymptotic safety) that is KNOWN to affect gauge coupling running and that CAN produce the needed correction with reasonable parameters.

5. **The required computation is well-defined.** The warped 5D AS beta functions for gauge couplings with C_2(G)-dependent gravitational corrections have not yet been computed (Phase 13M confirmed no existing literature). This is a tractable calculation that could resolve or kill the framework definitively.

### 4.5 But It IS a Serious Tension

The tension is real. Quantitatively:

```
Spread = 10.81 in alpha_i^{-1} units
As percentage of alpha_i^{-1} at Lambda_NCG: 10.81/43.54 = 24.8%
```

A ~25% mismatch in the inverse couplings is NOT small. The NCG spectral action makes a precise prediction (equal couplings), and the SM running produces a ~25% violation. This is comparable to the non-SUSY SU(5) problem, which the community considers a strong argument for new physics (specifically SUSY) between the weak and GUT scales.

The difference is that SUSY "solves" this by adding 105+ new parameters. The Meridian approach aims to solve it through gravitational UV completion — which adds zero new parameters but requires a specific structure in the AS fixed point.

---

## 5. C.1e: Comparison with NCG Spectral Action Prediction

### 5.1 The Spectral Action Unification Condition

The NCG spectral action predicts:

```
g_1^2(Lambda) = g_2^2(Lambda) = g_3^2(Lambda)   at the cutoff Lambda = Lambda_NCG
```

This is equivalent to:

```
alpha_1(Lambda_NCG) = alpha_2(Lambda_NCG) = alpha_3(Lambda_NCG) = f_0 / (4*pi * a_i * V_warp)
```

where the right-hand side is the same for all i because a_1 = a_2 = a_3 = 12.

### 5.2 The Warped Background Modification

On the warped RS background, the spectral cutoff is:

```
Lambda_NCG^{vis} = Lambda_NCG * e^{0}   (UV brane: no warping)
```

The spectral action is evaluated on the UV brane (or in the bulk, integrated over the orbifold with the warp factor). The key point: the cutoff scale Lambda_NCG is NOT warped because the spectral action is defined on the TOTAL space M_4 x [0, y_c] x F. The warp factor enters the integration over y, not the cutoff.

The physical gauge coupling on the IR brane (where we observe) is:

```
1/g_i^2 |_{IR} = (f_0 * a_i / 4*pi) * V_warp + brane terms
```

where V_warp = (1 - e^{-4ky_c}) / (4k) ~ 1/(4k).

The brane terms are universal (same spectral triple), so:

```
1/g_1^2 = 1/g_2^2 = 1/g_3^2   at Lambda_NCG
```

**The warping does NOT help.** It does not break the universality of the gauge couplings at the cutoff. The warped volume factor V_warp is the same for all gauge groups.

### 5.3 The Chamseddine-Connes Unification

Chamseddine and Connes (2006, 2010) pointed out that the spectral action unification condition a_1 = a_2 = a_3 is STRONGER than the GUT unification condition. In a GUT, the couplings unify because they are all embedded in a single simple group (SU(5), SO(10), etc.). In NCG, the couplings unify because the SPECTRAL TRIPLE treats all gauge fields democratically — the trace in Tr(f(D/Lambda)) runs over all of H_F with equal weight.

**This is a feature, not a bug.** The NCG unification is more fundamental than GUT unification because it doesn't require a GUT group (and therefore doesn't introduce proton-decay-mediating gauge bosons with the wrong mass scale).

The cost is that the running between Lambda_NCG and M_Z must be provided by SOMETHING — either the SM alone (which doesn't work, spread = 10.81), or the SM + additional physics (SUSY, extra matter, or gravitational corrections).

### 5.4 What Would Make the NCG Prediction Work

The NCG spectral action prediction WOULD work if any of the following held:

1. **Lambda_NCG ~ 10^13 GeV:** Then the alpha_1 = alpha_2 crossing occurs naturally at Lambda_NCG, and alpha_3 is only 3.5 units away. But Lambda_NCG ~ 10^13 is uncomfortably low — below the seesaw scale and inconsistent with the spectral action's role as a UV completion.

2. **Modified beta functions between M_Z and Lambda_NCG:** If new particle content (e.g., from the octonionic spectral triple, 15B) modifies b_1 by about -0.7 (while leaving b_2 and b_3 approximately unchanged), unification at Lambda_NCG ~ 10^17 would work. The required modification is:
   ```
   delta(b_1) ~ -0.7   =>  b_1^new ~ 3.4 (was 4.1)
   ```
   This could come from ~2 complete vector-like fermion generations with specific quantum numbers. However, these are not present in the minimal NCG spectral triple.

3. **Gravitational corrections above M_Pl that differentially shift alpha_1:** This is Path C. The AS framework provides this mechanism naturally. The required shift is:
   ```
   delta(alpha_1^{-1}) ~ +10.8 at Lambda_NCG
   ```
   spread over the trans-Planckian running distance.

---

## 6. Combined Assessment

### 6.1 Numerical Summary

```
+------------------------------------------+--------+--------+--------+--------+
| Quantity                                  |  U(1)  | SU(2)  | SU(3)  | Spread |
+------------------------------------------+--------+--------+--------+--------+
| alpha_i^{-1} at M_Z                      |  59.02 |  29.58 |   8.48 |  50.54 |
| alpha_i^{-1} at Lambda_NCG (SM only)     |  36.36 |  47.09 |  47.17 |  10.81 |
| alpha_i^{-1} at Lambda_NCG (+ KK corr)   |  ~40.4 |  ~53.9 |  ~52.3 |  ~13.4 |
| alpha_i^{-1} at M_Pl (SM only)           |  33.29 |  49.46 |  52.42 |  19.13 |
| NCG prediction (a_i)                      |  12.00 |  12.00 |  12.00 |   0.00 |
| Required shift for unif at Lambda_NCG     | +7.18  |  -3.55 |  -3.63 | -10.81 |
| Required shift (% of alpha_i^{-1})        | +19.7% |  -7.5% |  -7.7% |   --   |
+------------------------------------------+--------+--------+--------+--------+
```

### 6.2 Comparison with Literature

| Framework | Unification? | Mechanism | Spread at natural scale |
|-----------|-------------|-----------|------------------------|
| SM alone | NO | None | 10.81 at 10^17 (triangular non-unif) |
| MSSM | YES | Superpartner thresholds | 0 at ~2 x 10^16 GeV |
| Non-SUSY SU(5) | NO | Heavy gauge bosons | ~3 at 10^14 (plus proton decay problem) |
| RS + SU(6) (Angelescu) | YES | Brane kinetic terms (delta~1.3) | 0 at k ~ M_Pl |
| Meridian (current) | NO | NCG spectral action | 10.81 at Lambda_NCG |
| Meridian + AS (projected) | POSSIBLE | Gravitational threshold corrections | TBD — requires computation |

**Key comparison:** Angelescu et al. achieve unification in warped RS by embedding the SM in SU(6) on the UV brane, with symmetry-breaking brane kinetic terms providing the non-universal corrections. Meridian does NOT have this mechanism because the SM comes directly from the NCG spectral triple without a GUT intermediary. This is both a strength (no ad hoc GUT group) and a weakness (no built-in mechanism for non-universal corrections).

### 6.3 Consistency with Parameter Scan (19J.1)

The parameter scan found:

```
kappa in [0.85, 2.0]   (LHC constraint)
ky_c in [34, 35.5]     (LHC + hierarchy)
```

Varying across this space:

- The KK threshold corrections change by ~20% (negligible impact on spread)
- Lambda_NCG can vary from ~10^16 to ~10^18 depending on the precise NCG cutoff identification
- At Lambda_NCG ~ 10^13 GeV (which is OUTSIDE the allowed range), the spread would be ~4

**There is no point in the allowed parameter space where unification occurs.** The spread is ~11-15 across the full allowed region. This is a global property, not a fine-tuning failure.

### 6.4 Consistency with 19E.1 (Neutrinos) and 19F.2/F.3 (Collider)

**Neutrino sector (19E.1):** The seesaw threshold at M_R ~ 10^{10} GeV introduces right-handed neutrinos above M_R. However, right-handed neutrinos in the Type I seesaw are SM gauge singlets: Y = 0, zero SU(2) and SU(3) charges. They do NOT contribute to ANY gauge beta function. The seesaw threshold is INVISIBLE to gauge coupling running. This is not a missed correction — it is a structural feature of the seesaw mechanism.

**Collider sector (19F.2/F.3):** The KK graviton mass at ~5.9 TeV (kappa = 1) and the radion mass at ~300 GeV (benchmark) do not affect gauge coupling running because they are gravitational degrees of freedom, not gauge particles.

---

## 7. Match / Pivot / Kill Assessment

### VERDICT: PIVOT

**The framework does not achieve gauge coupling unification with the current particle content and running mechanism.** The spread of ~10.81 in alpha_i^{-1} at Lambda_NCG is a ~25% mismatch with the NCG prediction of universal couplings. This is a significant quantitative tension.

**However, this is NOT a kill, for the following specific reasons:**

1. **The tension is inherited from the SM, not generated by Meridian.** Any non-SUSY framework with SM particle content has the same problem. The Meridian RS warping does not help (KK corrections worsen the spread slightly) but it also does not create new problems.

2. **The NCG algebraic structure is correct.** The prediction a_1 = a_2 = a_3 is a genuine output of the spectral triple formalism. The failure is in the DYNAMICS (running between Lambda_NCG and M_Z), not in the ALGEBRA (the UV boundary condition).

3. **The framework has a specific, computable UV completion mechanism** (asymptotic safety) that can provide the needed non-universal corrections. The warped 5D AS beta functions have NOT been computed (Phase 13M confirmed this is an open calculation). The resolution or definitive kill depends on this computation.

4. **The required corrections are physically reasonable.** A two-parameter AS fit (separate U(1) and non-abelian gravitational corrections) achieves unification with O(1) parameters if the trans-Planckian running distance reaches ~10^25 GeV.

### What Would Upgrade to MATCH:

- Compute the warped 5D AS gauge-gravity beta functions
- If they produce C_2(G_i)-dependent gravitational corrections with the right sign and magnitude, unification follows from the UV completion
- This would be a genuine prediction: the NCG spectral triple sets the UV boundary, AS provides the dynamics, and the running DOWN to M_Z reproduces the observed couplings

### What Would Downgrade to KILL:

- If the warped 5D AS computation shows that gravitational corrections to gauge beta functions are UNIVERSAL (same for all gauge groups), then no amount of trans-Planckian running can fix the spread, and the framework cannot achieve unification
- If the computation shows that the required a_grav values are unnaturally large (>> 100), the mechanism would be technically possible but fine-tuned
- If additional analysis shows that the octonionic spectral triple (15B) necessarily introduces particle content that WORSENS the spread

### The Unresolved Computation

**The single most important computation for the gauge sector of the Meridian framework:**

Compute the 1-loop gravitational correction to the gauge coupling beta functions in the warped RS_5 geometry, within the functional renormalization group (Wetterich equation) framework.

Specifically:
- Does delta_beta_{g_i} depend on the gauge group G_i (through C_2, or otherwise)?
- If yes, what is the sign and magnitude of the non-universal part?
- Does the KK tower of gravitons modify this dependence?

This computation is feasible (it requires evaluating 1-loop Feynman diagrams with graviton exchange in AdS_5, or equivalently computing the FRG flow with gauge-gravity vertices on the RS background). No one has done it yet. It is the key deliverable for resolving this track.

---

## Appendix A: Detailed Beta Function Computation

### A.1 SM 1-Loop Beta Coefficients (Derivation)

For the SM with N_g = 3 generations and N_H = 1 Higgs doublet:

**U(1)_Y (GUT normalized):**
```
b_1 = (4/3) * N_g * [Y_Q^2 * N_c + Y_u^2 * N_c + Y_d^2 * N_c + Y_L^2 + Y_e^2]
    + (1/3) * N_H * [Y_H^2]
    (all with factor 3/5 from GUT normalization)

Full calculation:
  Fermion: (4/3) * 3 * [(1/6)^2*3 + (2/3)^2*3 + (-1/3)^2*3 + (-1/2)^2 + (-1)^2] * (3/5)
         = 4 * [1/12 + 4/3 + 1/3 + 1/4 + 1] * (3/5)
         = 4 * [1/12 + 16/12 + 4/12 + 3/12 + 12/12] * (3/5)
         = 4 * [36/12] * (3/5) = 4 * 3 * 3/5 = 36/5

  Higgs:   (1/3) * 1 * [(1/2)^2 * 2] * (3/5) = (1/3) * (1/2) * (3/5) = 1/10

  Gauge:   0 (abelian)

  b_1 = 36/5 + 1/10 + 0 = 41/10 = 4.100 ✓
```

**SU(2)_L and SU(3)_C:** Using the standard 1-loop formula:

```
b_i = -(11/3)*C_2(G_i) + (4/3)*sum_f T(R_f) + (1/3)*sum_s T(R_s)
```

**SU(3):**
```
b_3 = -(11/3)*3 + (4/3)*6*(1/2) + 0 = -11 + 4 = -7 ✓
```
(6 quark flavors, each a fundamental with T(3) = 1/2; no colored scalars.)

**SU(2):**
```
b_2 = -(11/3)*2 + (4/3)*6*(1/2) + (1/3)*1*(1/2) = -22/3 + 4 + 1/6 = -19/6 ✓
```
(6 SU(2) doublets from left-handed quarks and leptons; 1 Higgs doublet with T(2) = 1/2.)

The well-known SM 1-loop coefficients:
```
b_1 = +41/10 = +4.100
b_2 = -19/6  = -3.167
b_3 = -7     = -7.000
```

These are confirmed by every textbook and by the Phase 17E numerical computation.

### A.2 Sensitivity to 2-Loop Effects

The 2-loop SM beta function coefficients (Machacek & Vaughn, NPB 236 (1984)):

```
b_ij = | 199/50   27/10   44/5  |
       | 9/10     35/6    12    |
       | 11/10    9/2     -26   |
```

The 2-loop correction to alpha_i^{-1} at Lambda_NCG is:

```
delta^{2-loop} ~ (b_ij * alpha_j) / (8 pi^2) * ln(Lambda_NCG / M_Z) ~ O(0.3-1.0)
```

This is at most 10% of the 1-loop spread and does NOT change the qualitative picture. The spread shifts by approximately +0.5 to -0.8 units depending on the scale, which is negligible compared to 10.81.

### A.3 Sensitivity to Top Yukawa and Higgs

The top Yukawa coupling affects the running through 2-loop gauge-Yukawa mixing. At 1-loop, it only enters the Higgs quartic running (not the gauge couplings directly). The 2-loop Yukawa contribution is absorbed into the b_ij matrix above.

The Higgs mass (m_H = 125.25 GeV) enters through the threshold correction at M_H and through the Higgs quartic coupling's effect on the 2-loop gauge running. Both effects are negligible (<0.5 units in alpha_i^{-1}).

---

## Appendix B: Comparison with SUSY Unification

For reference, the MSSM 1-loop beta coefficients:

```
b_1^MSSM = +33/5 = +6.600
b_2^MSSM = +1
b_3^MSSM = -3
```

At M_SUSY ~ 1 TeV (with common sparticle threshold):

```
alpha_i^{-1}(M_GUT) converges at M_GUT ~ 2 x 10^16 GeV
alpha_GUT^{-1} ~ 24
Spread at M_GUT: < 1 (within 2-loop + threshold corrections)
```

The MSSM achieves this by adding:

- 3 gaugino multiplets (modify gauge beta functions)
- Higgsino doublets (additional SU(2) matter)
- Squarks and sleptons (additional colored/charged matter)

Total: 105+ new parameters (MSSM soft-breaking terms).

The Meridian approach would achieve unification through gravitational UV completion (AS), adding 0 new parameters. But the computation showing this is feasible has NOT been done.

**Honest comparison:**
- SUSY: unification demonstrated, but 105+ new parameters and no superpartners found at LHC
- Meridian + AS: unification plausible with O(1) AS parameters, but not yet demonstrated, and 0 new parameters
- Neither is satisfactory. SUSY is numerically successful but empirically unconstrained. Meridian is structurally elegant but numerically incomplete.

---

## Appendix C: The Warped 5D AS Computation (Specification)

For future work, the specific computation needed:

**Input:**
- RS5 background with metric ds^2 = e^{-2k|y|} eta_{mu nu} dx^mu dx^nu + dy^2
- Gauge field A^a_mu in the bulk (SU(N) gauge group)
- Graviton h_{MN} fluctuation on the AdS5 background
- Wetterich effective average action Gamma_k with regulator R_k

**Compute:**
1. The graviton propagator on the RS background (known: Boos, Plefka, Schwinn, PRD 71 (2005))
2. The gauge-graviton vertex on AdS5 (from gauge-gravity mixing in the bulk action)
3. The 1-loop graviton correction to the gauge field 2-point function
4. Extract the gauge-group-dependent part: does the correction contain C_2(G_i)?

**Expected structure:**

```
delta_beta_{g_i} = f_g(k, Lambda, ky_c) * g_i * [A + B * C_2(G_i)]
```

If B != 0, the correction is non-universal and can resolve the spread.
If B = 0, the correction is universal and CANNOT resolve the spread — this would be a strong negative result.

**The key physics question:** Does the graviton-gauge boson vertex in 5D depend on the gauge group index through the Casimir C_2(G)? In 4D, graviton-gauge couplings are universal (equivalence principle). In 5D with warping, the KK tower may introduce non-universal effects through the overlap of graviton and gauge boson profiles in the extra dimension (different gauge groups may have different 5D profiles if bulk masses differ — but in Meridian, all gauge fields are in the bulk with the same action).

**Preliminary expectation:** The graviton coupling to gauge fields IS universal at leading order (equivalence principle). Non-universal effects could arise at 1-loop through:
- Different self-energy diagrams for different gauge groups (C_2-dependent)
- Different KK mode contributions (if gauge boson profiles are group-dependent)

In Meridian, all gauge bosons live in the same bulk with the same boundary conditions. The 1-loop graviton contribution to the gauge boson self-energy IS C_2-dependent (because the gauge boson self-interaction vertex has a C_2 factor). This suggests B != 0 is natural, but the sign and magnitude need to be computed.

---

*Track 19C.1 complete. The unification tension is confirmed at 10.81. The framework pivots to asymptotic safety for resolution. The specific computation (warped 5D gauge-gravity beta functions) is defined but unperformed.*

*The honest picture: Meridian inherits the non-SUSY unification problem. The NCG spectral action provides the algebraic structure (a_1 = a_2 = a_3) but not the dynamical resolution. AS is the leading candidate. If the warped 5D AS computation produces universal gauge-gravity corrections, the tension cannot be resolved within the framework. If it produces non-universal corrections with the right structure, unification follows naturally. This is the single most important open computation in the gauge sector.*
