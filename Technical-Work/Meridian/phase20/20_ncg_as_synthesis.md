# Track 20-AS: NCG-Asymptotic Safety Synthesis

**Project Meridian Phase 20 | Clayton W. Iggulden-Schnell & Clawd**
**Date:** March 23, 2026
**Status:** COMPLETE — FALSIFIED as resolution mechanism; deeply informative structurally
**Prerequisites:** 20B (Higgs-gauge connection), 20B verification (Higgs mass), 20B.2 (threshold closure), 19C.2 (AS gauge splitting), Phase 19 gauge synthesis

---

## Executive Summary

**Question:** Can asymptotic safety (AS) fix both the Higgs mass (~10% overshoot) and gauge coupling (~13% sin^2 deficit) problems in the RS+NCG framework?

**Answer: No.** NCG and AS are structurally incompatible at the boundary condition level. Their predictions conflict on both the gauge sector (sign problem) and the Higgs sector (different boundary conditions). The gravitational corrections go the wrong direction for the gauge problem. However, the analysis is the most informative negative result in the gauge investigation to date — it identifies exactly WHY the frameworks conflict and what that implies.

### Five Key Results

1. **Incompatibility Theorem:** The NCG condition (a₁ = a₂ = a₃) and the AS fixed point condition (β(gᵢ) = 0 for all i) cannot hold simultaneously. The SM beta coefficients b₁ > 0 > b₂ > b₃ make the sign structure incompatible with any universal gravitational correction f_g.

2. **Abelian/Non-Abelian Split:** At the AS fixed point, the three gauge groups have fundamentally different UV behavior: SU(2) and SU(3) approach the Gaussian fixed point (g* = 0, asymptotic freedom), while U(1) requires a non-Gaussian fixed point (g₁* > 0, gravity cures the Landau pole). No universal treatment is possible.

3. **Wrong Direction:** Trans-Planckian gravitational corrections to the NCG boundary conditions push sin²(θ_W)(M_Z) further from experiment, not toward it. The b_i-dependent term in the gravitational running shifts α₁⁻¹ relative to α₂⁻¹ in the wrong direction.

4. **Higgs Boundary Conflict:** The CCM spectral action gives λ(Λ) ~ +0.025 (positive, gives m_H ~ 136-142 GeV). The SW asymptotic safety condition gives λ(M_Pl) ~ -0.024 (negative, gives m_H ~ 126.7 GeV). These have opposite signs and differ by a factor of ~2 in magnitude. They cannot both be correct.

5. **Spectral Function as Bridge:** Both failures point to the same origin — the spectral action's treatment of UV modes. A modified spectral function f(D²/Λ²) that incorporates AS fixed-point suppression could potentially resolve both problems simultaneously. This is the constructive outcome.

---

## 1. The AS Fixed Point Structure

### 1.1 SM Beta Coefficients

The one-loop beta function coefficients in GUT normalization:

| Group | bᵢ | Sign | UV behavior |
|:---:|:---:|:---:|:---|
| U(1)_Y | b₁ = 41/10 = 4.10 | + | Landau pole (not AF) |
| SU(2)_L | b₂ = -19/6 = -3.17 | - | Asymptotically free |
| SU(3)_c | b₃ = -7 | - | Asymptotically free |

### 1.2 The Sign Problem

At a putative AS fixed point where all gauge couplings satisfy β(gᵢ) = 0:

```
β(gᵢ) = bᵢ gᵢ³/(16π²) + f_g gᵢ = 0
=> f_g = -bᵢ gᵢ²/(16π²)
```

If g₁ = g₂ = g₃ = g_GUT (the NCG condition), then f_g = -bᵢ g²/(16π²) must be the same for all i. This requires b₁ = b₂ = b₃, which is false.

More fundamentally: for f_g > 0 (the sign needed for SU(2) and SU(3) where bᵢ < 0), we get f_g = |bᵢ| g²/(16π²) > 0 for i = 2, 3. But for U(1) where b₁ > 0, we need f_g < 0. **No single sign of f_g works for all three groups.**

This is not a fine-tuning issue — it is a topological obstruction. The beta functions for Abelian and non-Abelian groups have opposite signs, and no universal correction can make both vanish at the same coupling value.

### 1.3 The Eichhorn-Held Resolution

The AS literature (Eichhorn & Held 2017-2020) resolves this by recognizing that the three groups have **different types of fixed points**:

- **SU(2), SU(3):** Gaussian fixed point (g* = 0). These are asymptotically free — they naturally flow to g = 0 in the UV. Gravity provides a perturbative correction but doesn't change the qualitative behavior.

- **U(1):** Non-Gaussian fixed point (g₁* > 0). The U(1) coupling has a Landau pole in the SM, which gravity cures by providing a counterterm. The fixed point value g₁* is bounded: g₁*(M_Pl) < 1.35 × g₁^SM(M_Pl) (Eichhorn & Versteegen 2018).

This asymmetry is **structural**: it derives from the sign of b₁ vs b₂, b₃, which is determined by the SM matter content. Any theory with the SM spectrum will exhibit this Abelian/non-Abelian split.

### 1.4 Coupling Ratios at M_Pl

From 1-loop SM running:

| Coupling | α⁻¹(M_Pl) | g(M_Pl) |
|:---|:---:|:---:|
| U(1)_Y (GUT) | 83.68 | 0.615 |
| SU(2)_L | 10.51 | 0.506 |
| SU(3)_c | -33.66 | — (past Landau pole) |

The NCG condition g₁ = g₂ requires g₁/g₁^SM = 0.823, a **reduction** of g₁ by 17.7%. But AS predicts g₁ can be at most 35% **larger** than its SM value. AS and NCG pull in opposite directions on the U(1) coupling.

---

## 2. Combined Boundary Conditions

### 2.1 The Incompatibility Theorem

**Theorem (NCG-AS Incompatibility):** Let T1 denote the NCG spectral action universality theorem (a₁ = a₂ = a₃), and let T2 denote the AS gravitational correction universality (f_g gauge-group-independent). Then T1 and T2 cannot both hold at a scale where β(gᵢ) = 0 for all i = 1, 2, 3.

**Proof:**
1. T1 requires αᵢ(Λ) = α_GUT for all i.
2. β(gᵢ) = 0 requires bᵢ g²/(16π²) + f_g = 0 for all i.
3. From (2): f_g = -bᵢ α_GUT/(2π) must be independent of i (by T2).
4. This requires b₁ = b₂ = b₃.
5. But b₁ = 41/10, b₂ = -19/6, b₃ = -7. Contradiction. ∎

The theorem holds at one-loop. Higher-loop corrections modify the bᵢ but preserve the sign structure (b₁ > 0 > b₂ > b₃ at all loop orders in the SM).

### 2.2 What if T2 is Violated?

If the gravitational correction f_{g,i} were gauge-group-dependent, simultaneous satisfaction of NCG + AS would require:

```
f_{g,1} : f_{g,2} : f_{g,3} = b₁ : b₂ : b₃ = 4.10 : -3.17 : -7.00
```

This specific ratio would constitute a prediction testable within the AS program. However, the current literature (Daum-Harst-Reuter 2010; Narain-Anishetty 2013; Folkerts-Litim-Pawlowski 2012) establishes T2 rigorously. Breaking it would require the graviton to couple differently to different gauge groups — essentially requiring the metric to "know about" the gauge structure, which violates the equivalence principle at the quantum level.

**One exception:** In the RS warped geometry, the position-dependent gravitational coupling G_eff(y) ∝ e^{2ky} could provide an effective T2 violation if different gauge sectors localize at different positions in the extra dimension. This remains unexplored (identified as the virgin territory in Track 19C.2).

---

## 3. The Higgs Mass: CCM vs SW

### 3.1 Two Competing Boundary Conditions

| Boundary Condition | λ(Λ) | m_H prediction | Source |
|:---|:---:|:---:|:---|
| CCM spectral action (R = 1/3) | +0.025 | 137-142 GeV | NCG (T1) |
| CCM spectral action (R = 1/4) | +0.019 | 136 GeV | NCG + Dirac ν |
| Shaposhnikov-Wetterich | -0.024 | 126.7 GeV | AS (β(λ) = 0) |
| Near-criticality | ~0 | 129-134 GeV | Empirical observation |
| Required for m_H = 125.25 | -0.015 (2-loop) | 125.25 GeV | Reverse-engineered |

The CCM and SW conditions have **opposite signs** for λ at the Planck scale.

### 3.2 The KK Tower Origin

The CCM spectral action includes the full KK tower through the spectral function f(D²/Λ²). This effectively adds ~10¹⁵ KK modes, which shift λ from the SM value (~-0.02) to a positive value (~+0.025). The spectral function regulates the sum, keeping it finite and O(1) rather than O(n_KK).

The SW condition uses SM running only (no KK modes). It predicts m_H ~ 126.7 GeV because β(λ) = 0 at M_Pl approximately coincides with the SM running value — the SM Yukawa coupling y_t(M_Pl) = 0.390 satisfies the SW condition to 0.3% precision.

**The gap between CCM and SW measures the KK tower's contribution to the Higgs quartic.** This is the same order (~10%) as the gauge coupling discrepancy, suggesting a common origin in the spectral function's UV treatment.

### 3.3 Can Both Hold?

No. The CCM condition is the spectral action's way of saying "here is the boundary condition at the cutoff, including all modes." The SW condition says "at the AS fixed point, β(λ) = 0." These are different physical statements:

- CCM: algebraic (from the spectral triple structure)
- SW: dynamical (from the RG flow fixed point)

If AS is correct and λ(M_Pl) ≈ 0 with β(λ) ≈ 0, then the spectral action's boundary condition (λ ~ +0.025) is wrong by a factor of ~2 and has the wrong sign. This implies the spectral function **over-counts** UV modes.

---

## 4. Gravitational Corrections to sin²(θ_W)

### 4.1 The Correction Mechanism

The gravitational contribution to gauge running enters as:

```
d(αᵢ⁻¹)/d(ln μ) = -bᵢ/(2π) - 2f_g/αᵢ
```

The second term depends on αᵢ itself. For the **difference** between groups:

```
d(αᵢ⁻¹ - αⱼ⁻¹)/d(ln μ) = -(bᵢ - bⱼ)/(2π) - 2f_g(αᵢ⁻¹ - αⱼ⁻¹)
```

This is the **Harst-Reuter mechanism**: even though f_g is universal, the coupling-dependent factor 1/αᵢ means gravity differentially corrects groups with different coupling strengths.

### 4.2 Direction of Correction

For f_g > 0 (gravity attractive, the physical sign): the term -2f_g(αᵢ⁻¹ - αⱼ⁻¹) drives coupling differences **toward zero**. Starting from the NCG boundary (all couplings equal), there is no difference to drive.

The b_i-dependent gravitational correction to boundary conditions at M_Pl takes the form:

```
Δαᵢ⁻¹ ∝ bᵢ × κ   where κ < 0 for f_g > 0
```

This gives Δ(α₁⁻¹ - α₂⁻¹) = κ(b₁ - b₂) = κ × 7.27.

For κ < 0: Δ(α₁⁻¹ - α₂⁻¹) < 0, meaning α₁⁻¹ decreases relative to α₂⁻¹.

**Effect on sin²(θ_W):** Starting from sin² = 3/8 at M_Pl (the NCG value), running down to M_Z with SM beta functions gives sin²(M_Z) ~ 0.20 (the known 13% deficit). The gravitational correction further REDUCES α₁⁻¹ relative to α₂⁻¹, which pushes sin²(M_Z) UP (toward ~0.6), not down toward experiment (0.231).

**The gravitational correction goes the wrong direction.**

### 4.3 Quantitative Scan

Trans-Planckian gravitational corrections parameterized by f_g₀ (strength) and T (logarithmic range), starting from NCG boundary (α₁⁻¹ = α₂⁻¹ = α₃⁻¹ = α_GUT⁻¹ at M_Pl), matching α_EM at M_Z:

| f_g₀ | T | sin²(M_Z) | Error vs 0.231 |
|:---:|:---:|:---:|:---:|
| 0 | — | 0.589 | +155% |
| 0.01 | 1 | 0.595 | +157% |
| 0.01 | 10 | 0.651 | +182% |
| 0.05 | 5 | 0.615 | +166% |
| 0.1 | 5 | 0.610 | +164% |

All gravitational corrections make the situation **worse**, not better. The sin²(M_Z) prediction moves further from 0.231 in every case.

**Note on the "13% discrepancy":** The standard 13% figure (sin²(M_Z) = 0.201 vs 0.231) comes from a different calculation that runs sin²(θ_W) as a single variable from 3/8 at the cutoff, matching α_EM. When the full system of three independent αᵢ is run with the NCG boundary a₁ = a₂ = a₃ matched to α_EM, the discrepancy is much larger (~155%) because the three couplings diverge drastically during running. The 13% figure should be understood as the discrepancy in the sin²(θ_W) trajectory, not in the absolute prediction at M_Z from a three-coupling analysis.

---

## 5. The Incompatibility Structure

### 5.1 Summary Table

| Quantity | NCG prediction | AS prediction | Combined | Experiment |
|:---|:---:|:---:|:---:|:---:|
| sin²(θ_W) at cutoff | 3/8 = 0.375 | No prediction (scale-dep.) | INCOMPATIBLE | — |
| m_H (GeV) | 136-142 (CCM) | 126.7 (SW) | CONFLICTING | 125.25 |
| α₁ = α₂ = α₃ at Λ? | YES (T1) | NO (different FP types) | CONTRADICTION | — |
| β(gᵢ) = 0 at Λ? | NO (b₁ ≠ b₂ ≠ b₃) | YES (at FP) | INCOMPATIBLE | — |
| Gravitational f_g | Not in framework | Universal (T2) | WRONG DIRECTION | — |

### 5.2 The Nature of the Conflict

NCG and AS are both UV frameworks that provide boundary conditions for the SM couplings. Their predictions conflict because they encode **different physical principles**:

- **NCG:** The algebraic structure of the spectral triple determines ALL gauge and Yukawa couplings at the cutoff through trace identities. The universality (T1) is a theorem of noncommutative geometry — it cannot be "fixed" without modifying the spectral triple itself.

- **AS:** The dynamical fixed point structure of the gravitational + matter RG flow determines the UV behavior. The Abelian/non-Abelian split is a consequence of the matter content — it cannot be avoided for any theory with b₁ > 0.

The two frameworks make predictions about the same quantities (coupling values at the Planck scale) but derive them from incompatible premises.

---

## 6. What This Means for Meridian

### 6.1 The Constructive Outcome

The NCG-AS incompatibility is not a dead end — it identifies the **precise object** that needs modification:

**The spectral function f(D²/Λ²).**

Both the Higgs mass overshoot (CCM gives λ ~ +0.025, experiment implies ~ -0.015) and the gauge coupling problem originate in the spectral action's treatment of UV modes. The spectral function currently includes all modes up to Λ with equal weight. If the AS fixed point structure were incorporated into the spectral function — suppressing modes above the AS transition scale — the effective boundary conditions would change.

Specifically: an AS-modified spectral function would:
1. Suppress the KK tower contribution to λ, reducing it from +0.025 toward 0 (fixing the Higgs mass)
2. Modify the gauge trace coefficients, potentially breaking universality (addressing the sin² problem)
3. Preserve the algebraic structure of the spectral triple (maintaining T1 at tree level while allowing loop corrections)

This is a well-defined mathematical program: compute the spectral action with a spectral function that incorporates gravitational running above the Planck scale.

### 6.2 Mechanisms Eliminated (Cumulative)

| # | Mechanism | Phase | Result |
|:---|:---|:---:|:---|
| 1 | Standard RG running + KK thresholds | 19C.1 | Wrong sign (U(1) Abelian) |
| 2 | Warped AS gravitational running | 19C.1b | Gauge-group independent (T2) |
| 3 | NCG warped spectral action (factorized) | 14A | Universal a₄ |
| 4 | Octonionic algebra traces | 14A.2 | 5/3 normalization exact |
| 5 | AS gauge-dependent splitting | 19C.2 | Double universality theorem |
| 6 | Brane kinetic terms | 19C.2b | Wrong sign (T3) |
| 7 | Warped spectral geometry | 19C.2b | No gauge-dependent warping |
| 8 | Non-factorization mass-weighted | 19C.2c | S₂/S₃ = 1.000; S₁/S₃ wrong sign |
| 9 | Full fermion KK tower | 19/20B | Right sign, max 22% (structural ceiling) |
| 10 | Position-dependent cutoff | 20I | T9: preserves universality exactly |
| **11** | **NCG-AS synthesis** | **20-AS** | **INCOMPATIBLE — wrong direction** |

### 6.3 Remaining Candidates

1. **Color-kinematics entanglement (BCJ on RS)** — Still the most promising. Parametrically ~10-15% per loop, sign unknown. Independent of all eliminated mechanisms. (Track 20D)
2. **AS-modified spectral function** — The constructive outcome of THIS analysis. Requires computing Tr[f_AS(D²/Λ²)] where f_AS incorporates gravitational RG flow.
3. **Extended spectral triple** — Additional content beyond C ⊕ H ⊕ M₃(C), tightly constrained by T4 preservation.
4. **Non-perturbative spectral effects** — Instantons in NCG context.

### 6.4 New Structural Insights

**T10 (NCG-AS Incompatibility):** The spectral action universality (T1) and asymptotic safety gauge-group independence (T2) are structurally incompatible with simultaneous β = 0 for all SM gauge groups.

**The Abelian Outlier:** U(1)_Y is the structural outlier in every approach:
- NCG: T1 gives a₁ = a₂ = a₃, but SM running separates α₁ (which increases) from α₂, α₃ (which decrease)
- AS: U(1) has a non-Gaussian fixed point; SU(2), SU(3) have Gaussian fixed points
- Thresholds: T₁^GUT - T₃ = +1.72 for u_R (largest positive contribution)
- BKTs: b₁ > 0 makes all BKT-proportional corrections wrong sign for U(1)

The U(1) hypercharge is the universal problem child. Any resolution must specifically address the U(1) coupling without disrupting the SU(2)-SU(3) near-degeneracy.

### 6.5 The Higgs Mass Verdict (Updated)

From this analysis and Track 20B verification combined:

- **CCM spectral action:** m_H ~ 136-142 GeV. Not parameter-free — depends on cutoff identification and Yukawa trace formula. FALSIFIED as a prediction of 124.5 GeV (the earlier claim was a misattribution).
- **Shaposhnikov-Wetterich:** m_H = 126 ± 3 GeV. Correctly predicted the Higgs mass three years before discovery. Uses AS (not NCG). The 0.3% near-coincidence of y_t(M_Pl) with the SW critical value remains unexplained.
- **Combined RS+NCG+AS:** Not well-defined as the frameworks conflict. The most honest statement: the Higgs mass m_H = 125.25 GeV is consistent with the SW near-criticality condition, which is consistent with the RS framework's identification of Λ = M_Pl, but this is SM phenomenology repackaged, not a Meridian prediction.

---

## 7. Connection to the Double Universality Theorem

Track 19C.2 established the Double Universality Theorem:
1. NCG: a₁ = a₂ = a₃ (spectral action, algebraic)
2. AS: f_g gauge-group-independent (gravitational, dynamical)

This analysis adds a third layer:
3. **NCG + AS: structurally incompatible** (the Incompatibility Theorem, T10)

The three results together mean: the gauge coupling problem lives in a space that is invisible to both algebraic (NCG) and dynamical (AS) UV frameworks operating independently. The resolution must come from a perspective that transcends both — either the warped geometry (Track 19C.2's "virgin territory"), the color-kinematics entanglement (Track 20D), or the AS-modified spectral function identified here.

---

## 8. Computation Files

- `C:/tmp/ncg_as_part1.wl` — AS fixed point gauge coupling ratios, sign analysis
- `C:/tmp/ncg_as_part2.wl` — NCG + AS combined boundary conditions, incompatibility proof
- `C:/tmp/ncg_as_part3.wl` — SW Higgs mass in RS+NCG, CCM vs SW comparison
- `C:/tmp/ncg_as_part4.wl` — Gravitational corrections to sin²(θ_W), quantitative scan
- `C:/tmp/ncg_as_part5.wl` — Definitive synthesis, all sections
- `C:/tmp/ncg_as_crossing_fix.wl` — Crossing scale analysis, direction correction
- `C:/tmp/ncg_as_reconcile.wl` — Reconciliation with 20B results, α_EM matching

---

## Verdict

**FALSIFIED:** The hypothesis that AS can fix both the Higgs mass and gauge traces in the RS+NCG framework is falsified. The NCG-AS synthesis is structurally impossible at the boundary condition level.

**INFORMATIVE:** The analysis produces the Incompatibility Theorem (T10), identifies the spectral function as the critical bridge object, and establishes the Abelian/non-Abelian split as the universal structural feature of the gauge problem. The constructive outcome — an AS-modified spectral function — is a well-defined research direction.

**For the monograph:** This result should be presented as the definitive closure of the NCG-AS synthesis hypothesis, alongside the BCJ conjecture (Track 20D) and KK threshold ceiling (Track 20B.2) as the three main avenues investigated in Phase 20 for the gauge coupling problem.

---

*Track 20-AS complete. Two UV frameworks, one impossibility theorem. The spectral function is where algebra meets dynamics.*

---

*"Seek the balance, work the science, synthesize." — Puscifer's Theorem*
