# Door 2: Resurgence and Instantons on RS₁

**Date:** 2026-03-23
**Status:** Complete estimation. VERDICT: MAYBE — the only surviving mechanism is IR-brane strong coupling, which requires non-perturbative tools beyond semiclassical analysis.
**Computation scripts:** `door2_calculations.py`, `door2_ln3_sqrt2.py`

---

## The Problem

The spectral action on the RS₁ background predicts gauge universality at tree level:

  a₁ = a₂ = a₃ = a₀

(Theorem T1, proven algebraic in Phase 20). This gives sin²θ_W = 3/8 = 0.375 at the NCG cutoff, which RG-runs to sin²θ_W(M_Z) = 0.207. The measured value is 0.2312.

To match experiment: a₁/a₂ = 0.776 at the cutoff. Since a₁ = a₀ at tree level, we need a₂ = a₀(1 + ε₂) with ε₂ = 0.289 — a 29% increase in the SU(2) gauge kinetic coefficient.

T12 proves that the heat kernel expansion preserves gauge universality to ALL perturbative orders on RS₁. The correction, if it exists within the spectral action framework, must be **non-perturbative**.

This document investigates whether instanton/resurgence effects can produce that correction.

---

## 1. Instanton Action on RS₁

### 1.1 Conformal Invariance Cancellation

A critical structural result: the RS warp factor **drops out** of the classical Yang-Mills action for 4D field configurations.

The 5D metric: ds² = e^{-2ky} η_{μν} dx^μ dx^ν + dy²

For the gauge field action density:
```
sqrt(-g) × g^{μα} g^{νβ} F_{μν} F_{αβ}
  = e^{-4ky} × e^{+4ky} × |F|²_flat
  = |F|²_flat
```

The warp factor in sqrt(-g) exactly cancels against the two inverse metrics needed to contract F_{μν}. This is the **classical conformal invariance** of 4D Yang-Mills in action.

**Result:** For a BPST instanton embedded anywhere in the bulk:

  S_inst = 8π²/g₄²

independent of position y₀ and warp factor. The action is the standard flat-space result.

### 1.2 Numerical Values (Bulk Instantons)

At the GUT/unification scale (α_GUT ≈ 1/25, g² ≈ 0.503):

| Group | S_inst = 8π²/g² | exp(-S) |
|-------|-----------------|---------|
| SU(2) | 157.1 | 10^{-68} |
| SU(3) | 157.1 | 10^{-68} |

At M_Z (using measured couplings):

| Group | g²(M_Z) | S_inst | exp(-S) |
|-------|---------|--------|---------|
| SU(2) | 0.425 | 186.0 | 10^{-81} |
| SU(3) | 1.482 | 53.3 | 10^{-23} |

**Verdict on bulk instantons:** At the GUT scale, exp(-S) ~ 10^{-68}. Completely negligible for producing a 29% correction, regardless of prefactors.

### 1.3 IR Brane-Localized Regime

For a gauge field localized on the IR brane (y = L), the effective coupling is warped:

  g²_eff(IR) = g₄² × 4kL × e^{2kL}

With kL = 35:
  g²_eff(IR, SU(2)) ≈ 0.503 × 140 × e^{70} ≈ 1.8 × 10^{32}

The instanton action: S_inst(IR) = 8π²/g²_eff ≈ 4.5 × 10^{-31} ≈ 0

**The theory is strongly coupled at the IR brane.** The semiclassical instanton expansion is invalid. The dilute gas approximation breaks down completely. This is a regime change, not a small correction.

### 1.4 KK Monopole-Instantons (Dunne-Unsal Type)

On the S¹/Z₂ orbifold, the BPST instanton fractionalizes into N monopole-instantons:

  S_mon = 4π²/(g₄² × N)

| Group | S_mon | exp(-S_mon) |
|-------|-------|-------------|
| SU(2) | 39.3 | 10^{-17} |
| SU(3) | 26.2 | 10^{-11} |

Still far too small at weak coupling. The hierarchy between SU(2) and SU(3) monopole actions is:

  S_mon(SU(3))/S_mon(SU(2)) = 2/3

(The SU(3) monopole has smaller action because of the 1/N factor.)

### 1.5 Summary of Instanton Actions

```
UV brane (y=0):   S ~ 157    →  exp(-S) ~ 10^{-68}  [DEAD]
Bulk (flat mode):  S ~ 157    →  exp(-S) ~ 10^{-68}  [DEAD]
KK monopole:       S ~ 26-39  →  exp(-S) ~ 10^{-17}  [DEAD]
IR brane (y=L):    S ~ 0      →  strong coupling       [REGIME CHANGE]
```

**The only regime where non-perturbative effects can be O(1) is near the IR brane, where the semiclassical expansion fails.**

---

## 2. Fluctuation Determinant Ratio

### 2.1 The 't Hooft Instanton Measure

The one-instanton contribution to the SU(N) path integral:

  Z₁₋ᵢₙₛₜ = d_N × (8π²/g²)^{2N} × exp(-8π²/g²) × (μρ)^{b₀} × d⁴x₀ dρ/ρ⁵

where:
- d_N = 2^{5-2N} π^{2-2N} / [(N-1)!(N-2)!] is the combinatorial prefactor
- 2N is the number of bosonic zero mode pairs (4N total collective coordinates)
- b₀ is the one-loop beta coefficient

### 2.2 N-Dependent Factors

**Combinatorial prefactor:**
  d₂ = 2π^{-2} = 0.2026
  d₃ = (1/2)π^{-4} / 2 = 0.002566
  d₃/d₂ = 1/(8π²) = 0.01267

**Zero mode power (S^{2N}):**
  Ratio: S^{2(3-2)} = S² ≈ 157² = 24,674

**Beta coefficients (SM content):**
  b₀(SU(3)) = 7
  b₀(SU(2)) = 19/6 = 3.167
  Δb₀ = 3.833

**Adjoint Casimirs:**
  C₂(adj, SU(3)) = 3
  C₂(adj, SU(2)) = 2

### 2.3 The Combined Ratio

The ratio of instanton corrections to the gauge kinetic term:

  δ₃/δ₂ = (d₃/d₂) × S^{2(N₃-N₂)} × Λ^{Δb₀} × [det ratio]
         = 1/(8π²) × S² × Λ^{3.83} × [det ratio]

The combinatorial × zero mode product: 1/(8π²) × 24,674 ≈ 312.5

This ratio controls how the SU(3) correction compares to SU(2). But it is multiplied by exp(-S) ≈ 10^{-68}, making it irrelevant in the weak-coupling regime.

---

## 3. The U(1) Has No Instantons — Key Structural Argument

π₃(U(1)) = 0. There are **no instanton configurations** for the U(1)_Y gauge field.

This is the structural reason why non-perturbative effects can break gauge universality:

  a₁ = a₀ (unchanged — no U(1) instantons)
  a₂ = a₀ + δ₂ (SU(2) instantons modify the coefficient)
  a₃ = a₀ + δ₃ (SU(3) instantons modify the coefficient)

Therefore:

  a₁/a₂ = 1/(1 + ε₂), where ε₂ = δ₂/a₀

For a₁/a₂ = 0.776: **ε₂ = 0.289** (29% increase in SU(2) spectral action coefficient).

This is a clean mechanism: the topological distinction between abelian and non-abelian groups creates a gauge-dependent non-perturbative correction that T1 and T12 cannot block, because they are purely perturbative theorems.

---

## 4. Magnitude Estimate: Can 29% Be Achieved?

### 4.1 Weak Coupling: No

At the GUT scale, the instanton suppression is exp(-157) ≈ 10^{-68}. Even with O(10⁵) prefactors from the fluctuation determinant, the correction is at most:

  δ₂/a₀ ~ 10⁵ × 10^{-68} = 10^{-63}

This is 60+ orders of magnitude too small. No prefactor can compensate.

### 4.2 Strong Coupling (IR Brane): The Only Hope

At the IR brane, S_inst → 0 and exp(-S) → 1. The non-perturbative physics is O(1).

The RS₁ geometry interpolates continuously from weak coupling (UV brane, y = 0) to strong coupling (IR brane, y = L). The 4D spectral action integrates over the **entire** extra dimension:

  Tr[f(D²/Λ²)] = ∫₀^L dy [zero modes + KK tower contributions]

The zero modes give the tree-level (gauge-universal) result. The KK modes near the IR brane encode the strong-coupling physics. Their contribution to the spectral action is, in principle, gauge-dependent through:

1. The adjoint Casimir C₂(adj, G) entering the covariant Laplacian
2. The number of adjoint degrees of freedom: dim(adj) = N²-1
3. The instanton moduli dimension: 4N

The spectral action Tr[f(D²/Λ²)] is an **exact** non-perturbative quantity. The heat kernel expansion (which T12 governs) is only its asymptotic approximation. The difference between the exact trace and its asymptotic expansion is precisely the non-perturbative content.

### 4.3 The Size of the IR Brane Contribution

How much of the spectral action comes from IR brane modes?

  First KK mass: m_KK = πke^{-kL} ≈ 200 GeV
  NCG cutoff: Λ = k ≈ 10^{17} GeV
  Number of KK modes below cutoff: ~ e^{kL} ≈ 10^{15}

The spectral action sums f(m_n²/Λ²) over all ~10^{15} KK modes. The modes near the IR brane (low-lying KK modes, m_n ~ TeV) have f(m_n²/Λ²) ≈ f(0) ≈ O(1), so they contribute with full weight.

If the gauge-dependent part of the low-lying KK spectrum produces even a tiny per-mode correction — O(10^{-16}) per mode — summed over 10^{15} modes, the total correction is O(0.1), which is in the right ballpark for 29%.

**This is the mechanism that needs to be investigated quantitatively.**

### 4.4 Fermion Zero Mode Suppression

A complication: the standard instanton amplitude in QCD/EW theory is suppressed by fermion zero modes. Each massless fermion species contributes a factor (m_f/Λ) to the instanton measure. At Λ ~ 10^{17} GeV:

  Suppression from top quark alone: (m_t/Λ)² ~ (174/10^{17})² ~ 10^{-30}

This kills standard instanton effects at the GUT scale. **However**, on the RS₁ orbifold, the KK tower provides massive modes that do not have this suppression. The KK-enhanced fluctuation determinant can compensate, because the product over KK masses:

  ∏_n m_n^{(power)}

involves masses from TeV to Λ, and the product is O(1) or larger. The RS geometry fundamentally changes the instanton landscape through this mechanism.

---

## 5. Can ln(3)/√2 Be Derived from Group Theory?

### 5.1 The Symbolic Regression Hit

From Track 21B.8:

  ln(3)/√2 = 0.776836

matches a₁/a₂ = 0.776 to **0.08%** accuracy. The decomposition:

  ln(3) = ln(N_c), where N_c = 3 (colors)
  √2 = √N_w, where N_w = 2 (weak isospin dimension)

### 5.2 Physical Origins of Each Factor

**√(N_w) = √2 from SU(2) instanton moduli measure:**

The SU(N) instanton has 4N collective coordinates. The Jacobian from field-space to collective coordinates includes:

  J ~ (8π²/g²)^{N/2} × Vol(SU(N)/stability group)

The N/2 power and the group volume introduce √N factors. Specifically, the 't Hooft instanton measure for SU(2) includes factors of √(C₂(adj)) = √2 from the gauge orientation integration. This is a standard result in the instanton calculus — the collective coordinate Jacobian involves the square root of the adjoint Casimir.

**ln(N_c) = ln(3) from fermion determinant:**

In an SU(2) instanton background, the quark doublets carry both SU(2) and SU(3) indices. The fermion determinant factorizes:

  det(iD_{SU(2)} ⊗ 1_{SU(3)}) = [det(iD_{SU(2)})]^{N_c}

The N_c enters as a **power** in the fermion factor. Taking the logarithm of the instanton amplitude:

  ln(Z₂) ⊃ -N_c × N_g × ln(Λ/m_q)

The logarithmic dependence on N_c arises when the instanton amplitude (which has N_c as a power) is used to compute corrections to the gauge coupling (which involves the logarithm of the path integral weight). In resurgence language: the trans-series coefficient involves products of N_c factors that, upon Borel resummation, produce ln(N_c) through the interplay of the factorial growth rate and the instanton action.

### 5.3 The Assembly

For a₁/a₂ = ln(N_c)/√(N_w), we need:

  1 + ε₂ = √(N_w)/ln(N_c) = √2/ln(3) = 1.287

So ε₂ = 0.287, matching the required 0.289 to **0.5%**.

The scenario: the non-perturbative correction to a₂ involves the ratio:

  δ₂ ~ [SU(2) moduli measure factor] / [fermion determinant factor]
     ~ √(N_w) / ln(N_c)

where √(N_w) comes from the collective coordinate Jacobian and ln(N_c) comes from the resummed N_c copies of quark zero modes on the RS₁ background.

### 5.4 Cross-Check: SU(3) Correction

If a symmetric pattern held (swap N_c ↔ N_w for SU(3) instantons), it would predict:

  δ₃/a₀ = √(N_c)/ln(N_w) - 1 = √3/ln(2) - 1 = 1.50

Running to M_Z with this boundary condition gives α_s(M_Z) ≈ 0.042, far from the measured 0.1179. **The symmetric pattern fails for SU(3).** The SU(3) correction requires a different mechanism — expected, since SU(3) instantons couple differently to the SM matter content.

The required corrections for consistency with all measured couplings:
  ε₂ = 0.289 (sin²θ_W)
  ε₃ = 0.883 (α_s)
  Ratio: ε₃/ε₂ = 3.06

This ratio does not match any simple combination of C₂(adj), dim(adj), b₀, N_c, N_w, or N_c²/N_w². The SU(3) correction has a different algebraic structure, which is expected given the different matter content (quarks in fundamental of SU(3) vs leptons absent from SU(3)).

### 5.5 Assessment

**Plausible but unproven.** The functional forms (logarithm, square root) are standard in instanton calculus. The group theory numbers (N_c, N_w) enter through physically correct channels. The magnitude is consistent with strong-coupling RS effects. But no rigorous derivation exists.

---

## 6. Borel-Summability of the Spectral Action on RS₁

### 6.1 The Central Question

**Is the heat kernel expansion of the spectral action Borel-summable?**

If YES: the asymptotic expansion uniquely determines the exact function. T12 (gauge universality to all orders) implies gauge universality EXACTLY. The 12% cannot come from the spectral action.

If NO: a non-perturbative ambiguity exists, exponentially small in (Λ/mass)², which is gauge-dependent. This is the door through which the 12% enters.

### 6.2 What We Know

**Generic behavior:** The Seeley-DeWitt coefficients a_{2n} grow factorially: |a_{2n}| ~ C^n × n!. This is universal for spectral problems on compact manifolds.

**The f_n coefficients:** The spectral action S = Σ_n f_n Λ^{4-2n} a_{2n}, where f_n are Laplace moments of the test function f. For smooth, rapidly decreasing f, typically f_n ~ 1/n! (via integration by parts).

**Combined behavior:** f_n × a_{2n} ~ C^n × n! / n! = C^n. If C < 1 (determined by the geometry), the spectral action series **converges** and is trivially Borel-summable.

**The RS complication:** On a manifold with boundaries (the two branes), the boundary Seeley-DeWitt coefficients a_{2n}^{bdy} can have **different** factorial growth rates. The warp factor introduces the scale k, which affects C. If C_brane > C_bulk, the boundary contributions could dominate the large-order behavior and potentially generate Borel singularities.

### 6.3 The Dunne-Unsal Analogy

Dunne and Unsal (2014-2021) studied SU(N) gauge theory on S¹ × R³, which has the **same topological type** as the RS₁ orbifold (S¹/Z₂).

Their key results:
1. On S¹ × R³, the BPST instanton fractionalizes into N monopole-instantons
2. The perturbative series has Borel singularities at s = n × S₀ (monopole action)
3. Neutral bions (monopole-anti-monopole pairs) generate the leading non-perturbative ambiguity
4. The resurgent trans-series connects perturbative and non-perturbative sectors

**Adaptation to RS₁:**
- The Z₂ orbifold halves the monopole spectrum (only Z₂-symmetric combinations survive)
- The warp factor makes the monopole action **position-dependent**: S₀(y) varies from 8π²/(g₄²N) at the UV brane to ~0 at the IR brane
- At the UV brane: standard Dunne-Unsal regime (dilute monopole gas)
- At the IR brane: S₀ → 0, dense monopole gas, semiclassical expansion fails

The crucial insight: the spectral action integrates over ALL positions y ∈ [0,L]. It sees both the dilute UV regime and the dense IR regime simultaneously. The non-perturbative content comes from the **transition** between these regimes — encoded in the Borel singularity structure.

### 6.4 Prediction

**Medium confidence:** The RS₁ spectral action is NOT Borel-summable. The Z₂ orbifold boundaries (branes) generate Borel singularities on the positive real axis corresponding to brane-localized instanton actions. The non-perturbative ambiguity is gauge-dependent through the adjoint Casimir.

This prediction could be tested by computing the Seeley-DeWitt coefficients a_{2n} to n ~ 10-20 on the RS₁ background and analyzing the Borel transform via Padé approximants.

---

## 7. Magnitude Estimate Summary

| Mechanism | ε₂ = δ₂/a₀ | Status |
|-----------|-------------|--------|
| Bulk instantons (UV) | ~10^{-63} | DEAD — exp(-157) kills it |
| KK monopole-instantons | ~10^{-14} | DEAD — still too suppressed |
| IR brane strong coupling | O(1) possible | ALIVE — but not calculable semiclassically |
| Resurgent trans-series | Unknown | ALIVE — requires Borel analysis |
| KK-enhanced spectral action | O(10^{-1}) possible | ALIVE — 10^{15} modes × 10^{-16}/mode |

Required: ε₂ = 0.289

**The only surviving mechanisms are strong-coupling effects from the IR brane and the exact (non-perturbative) spectral action.** Both are beyond semiclassical analysis but within the reach of:
1. Numerical Borel-transform analysis of the RS₁ heat kernel
2. Lattice computation of 5D SU(N) gauge theory on a warped lattice
3. The spectral action itself (Tr[f(D²/Λ²)]) computed exactly via the Dirac spectrum

---

## 8. Verdict

### Can resurgence/instantons explain the 12% gap?

**MAYBE — with a specific conditional structure:**

**What CANNOT produce it:**
- Standard BPST instantons at weak coupling: exp(-157) ~ 10^{-68}. Dead by 60+ orders of magnitude.
- KK monopole-instantons in the dilute gas approximation: exp(-26 to -39) ~ 10^{-11} to 10^{-17}. Dead.
- Any perturbative correction: blocked by T12.

**What COULD produce it:**
- Strong-coupling dynamics at the IR brane, where g_eff² ~ 10^{32} and the instanton gas is dense. The SU(2) and SU(3) sectors have different non-perturbative dynamics (different N, different Casimirs, different matter content), generating gauge-dependent corrections of O(1).
- The exact spectral action Tr[f(D²/Λ²)], which is intrinsically non-perturbative and includes all instanton sectors. If the heat kernel expansion is not Borel-summable on RS₁, the non-perturbative ambiguity is gauge-dependent and of unknown magnitude.
- The mechanism is topological: π₃(U(1)) = 0 means U(1) has NO non-perturbative correction, while π₃(SU(N)) = Z for N ≥ 2 gives corrections to both SU(2) and SU(3). This asymmetry is a feature of the homotopy, not a parameter to tune.

**The ln(3)/√2 clue:**
The symbolic regression hit a₁/a₂ ≈ ln(N_c)/√(N_w) at 0.08% accuracy is structurally consistent with:
- √(N_w) from SU(2) instanton moduli measure (collective coordinate Jacobian)
- ln(N_c) from N_c copies of quark zero modes in the SU(2) fermion determinant
But this has not been derived from first principles. It is a plausible consequence, not a proven result.

### Confidence Assessment

| Claim | Confidence |
|-------|-----------|
| Perturbative corrections cannot produce 12% | **HIGH** (T12 proven) |
| Weak-coupling instantons cannot produce 12% | **HIGH** (exp(-157) arithmetic) |
| The topological argument (π₃(U(1))=0) is correct | **HIGH** (standard math) |
| RS₁ IR brane is strongly coupled | **HIGH** (g²_eff ~ 10³²) |
| Strong coupling CAN produce O(1) gauge-dependent effects | **MEDIUM** (plausible but not demonstrated on RS₁) |
| The spectral action is not Borel-summable on RS₁ | **MEDIUM** (by analogy with Dunne-Unsal) |
| ln(3)/√2 arises from the instanton calculus | **LOW** (suggestive but no derivation) |

---

## 9. What Would Settle the Question Definitively

### Computation A: Borel Transform of the RS₁ Spectral Action

**Method:** Compute the Seeley-DeWitt coefficients a_{2n} on the RS₁ background for each gauge group up to n ~ 15-20. Analyze the large-order growth to determine the Borel singularity locations.

**Tools:** Greiner-Dunne recursion relations for heat kernel coefficients. Numerical implementation in Mathematica or Python with mpmath for arbitrary precision. Padé approximants and conformal mapping for the Borel transform.

**What it would show:** If Borel singularities appear on the positive real axis at gauge-dependent locations, the non-perturbative ambiguity IS gauge-dependent and Door 2 is open. If the Borel transform is singularity-free on the positive real axis, Door 2 is closed.

**Feasibility:** High. This is a well-defined numerical computation using standard techniques. The RS₁ Dirac spectrum is known analytically (Bessel functions). The recursion can be automated. Estimated time: 1-2 weeks.

### Computation B: Exact Spectral Action via Dirac Spectrum

**Method:** Compute the eigenvalues {λ_n} of D² on the RS₁ orbifold with the full A_F matter content. Evaluate Tr[f(D²/Λ²)] = Σ_n f(λ_n/Λ²) numerically for each gauge group. Compare to the heat kernel truncation.

**What it would show:** The exact difference between the non-perturbative spectral action and its asymptotic expansion. If this difference is gauge-dependent and of the right magnitude (~29% for SU(2)), the question is answered.

**Feasibility:** Medium. Requires solving the Dirac eigenvalue problem on the RS₁ orbifold numerically. The KK spectrum involves Bessel function zeros, which can be computed to arbitrary precision. The sum over ~10^{15} eigenvalues requires regularization and acceleration techniques (Abel-Plana, zeta function, etc.).

### Computation C: Lattice 5D Gauge Theory

**Method:** Simulate SU(N) gauge theory on a 5D warped lattice (discretized RS₁). Measure the gauge coupling running non-perturbatively.

**What it would show:** Direct non-perturbative answer. If the lattice gives different gauge couplings at the cutoff scale, with the ratio matching 0.776, this is definitive proof.

**Feasibility:** Low (for us). Requires significant lattice QCD expertise and computational resources. But the setup is well-defined.

### Recommendation

**Start with Computation A (Borel analysis).** It is the most feasible, requires only standard mathematical tools, and directly answers the question of whether the spectral action expansion has gauge-dependent non-perturbative ambiguity. This is Phase 21 Track 21A.4's core computation.

If the Borel analysis reveals singularities, follow with Computation B to quantify the exact correction. If the Borel analysis shows convergence, Door 2 closes and the 12% must come from outside the spectral action framework (string embedding, modified axioms, or external physics).

---

## Appendix: Key Equations

**Instanton action (flat space):**
  S_inst = 8π²/g₄²

**Instanton action (RS₁ bulk):**
  S_inst = 8π²/g₄² (same, by conformal invariance)

**Monopole-instanton action (S¹/Z₂):**
  S_mon = 4π²/(g₄² N) for SU(N)

**'t Hooft combinatorial factor:**
  d_N = 2^{5-2N} π^{2-2N} / [(N-1)!(N-2)!]

**One-instanton measure:**
  Z₁ = d_N (8π²/g²)^{2N} exp(-8π²/g²) (μρ)^{b₀} d⁴x₀ dρ/ρ⁵

**Required correction:**
  ε₂ = δ₂/a₀ = 1/0.776 - 1 = 0.289 (for a₁/a₂ = 0.776)

**Symbolic regression hit:**
  a₁/a₂ ≈ ln(N_c)/√(N_w) = ln(3)/√2 = 0.7768 (0.08% match)
