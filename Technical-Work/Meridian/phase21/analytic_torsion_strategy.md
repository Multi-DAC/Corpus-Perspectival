# Computational Strategy: Analytic Torsion on dP₅ with Hypercharge Flux

**Date:** 2026-03-23
**Status:** RESEARCH COMPLETE — Strategy designed, paths ranked
**Goal:** Determine whether Δ₃ − Δ₂ on dP₅ with N_Y = 3 gives a₁/a₂ = ln(3)/√2

---

## Executive Summary

Seven computational approaches were researched. The recommended path forward is a **three-track strategy** ordered by feasibility:

1. **Track A (RECOMMENDED, HIGHEST ROI):** Mourougane-style arithmetic RR computation on dP₅ via iterative blowup from CP²
2. **Track B (VALIDATION):** Numerical Dolbeault Laplacian spectrum via Donaldson balanced metrics + Ashmore method
3. **Track C (BACKUP):** Heterotic Z₃ orbifold DKL integral (already partially computed in Phase 21B)

The key discovery from this research: **there exists a blowup formula for analytic torsion** (Mourougane 2006 for Hirzebruch surfaces, Zhang 2023 for BCOV invariants) that could allow iterative computation from CP² → dP₁ → dP₂ → ... → dP₅ without needing the full KE metric.

---

## 1. FEniCS/DOLFINx for 4D Riemannian Manifolds

**Verdict: NOT VIABLE for this problem.**

### Findings
- DOLFINx provides built-in mesh creation for 1D (intervals), 2D (rectangles), and 3D (boxes/tetrahedra). **No built-in 4D mesh support exists.**
- The library is designed around simplicial elements in dimensions 1-3. There is no documentation for 4D pentatope (5-cell) elements.
- While DOLFINx theoretically supports arbitrary-dimensional meshes through its abstract mesh framework, there is no practical tooling for generating 4D meshes, defining 4D finite elements, or assembling forms on 4D domains.
- Even if 4D meshes were supported, dP₅ is a compact complex surface (real dimension 4) with nontrivial topology — meshing it would require specialized tools that do not exist in the FEniCS ecosystem.

### Assessment
- **Feasibility:** 0/10
- **Reason:** Wrong tool for the job. FEniCS is designed for PDEs on domains in R^n, not on compact complex algebraic surfaces with nontrivial topology.

---

## 2. State of the Art: Numerical KE Metrics on Del Pezzo Surfaces

**Verdict: PARTIALLY VIABLE — but only for toric del Pezzos (dP₁, dP₂, dP₃).**

### Findings

**The Doran-Headrick-Herzog-Kantor-Wiseman (2008) paper** remains the state of the art for numerical KE metrics on del Pezzo surfaces. Key facts:
- They compute the KE metric on **dP₃ only** (the third del Pezzo).
- The toric structure of dP₃ reduces the Einstein equation to a **single Monge-Ampère equation in 2 real dimensions** — a massive simplification.
- Three algorithms used: Ricci flow in complex coordinates, Ricci flow in symplectic coordinates, and optimization on a space of algebraic metrics.
- The authors explicitly state their algorithms apply to "general **toric manifolds**."
- **dP₅ is NOT toric** (only dP₀ = CP², dP₁, dP₂, dP₃ are toric among smooth del Pezzos). The toric reduction does not apply.

**No one has computed a numerical KE metric on dP₄, dP₅, dP₆, dP₇, or dP₈.** This is an open computational challenge.

**Machine learning approaches (2022-2025):**
- **cymyc** (Calabi-Yau Metrics, Yukawas, and Curvature, JHEP March 2025): High-performance JAX library for CY metrics. Focuses on Calabi-Yau threefolds (complex dimension 3), not surfaces. Could potentially be adapted but not designed for del Pezzo surfaces.
- **cyjax** (ML Calabi-Yau metrics with JAX): Uses Donaldson's algebraic ansatz. Currently limited to varieties defined by a single equation in one projective space. dP₅ as a blowup of CP² at 5 points is not in this class.
- **cymetric** (TensorFlow-based): Similar scope to cyjax, focused on CY threefold hypersurfaces.
- **AInstein** (arXiv:2502.13043, 2025): Semi-supervised ML for generic Einstein metrics. Tested on spheres S² through S⁵. No Kähler structure awareness. Could potentially handle dP₅ but would require significant adaptation to complex geometry.

### Assessment
- **Feasibility for dP₅:** 3/10 (no existing code; would require building from scratch)
- **Feasibility for dP₁-dP₃ validation:** 7/10 (Doran-Headrick method works, code not public but method is well-documented)

---

## 3. Donaldson Balanced/Algebraic Metrics

**Verdict: VIABLE and potentially the best numerical route for the metric.**

### Findings

Donaldson (2005) showed that balanced metrics on polarized Kähler manifolds converge to the KE metric in the large-k limit. The key results:

- **The T-iteration algorithm** defines operators on Hermitian metrics whose fixed points are balanced metrics. Convergence is proven for Fano manifolds with discrete automorphism group (which includes dP₅).
- **Convergence rate:** Moving from embedding degree k = 6 to k = 9 reduced mean metric error by factor ~2 for balanced metrics and ~5 for refined approximations (Donaldson's K3 example).
- **Anticanonically balanced metrics** converge smoothly to KE on Fano manifolds (arXiv:2006.05989).
- **Implementation complexity:** Donaldson notes that "fairly simple programs can achieve accurate results" — the algorithm is essentially linear algebra (matrix balancing) plus numerical integration.

**For dP₅ specifically:**
- dP₅ is embedded in CP⁵ via the anticanonical linear system |−K| (dimension 4+1=5, since h⁰(−K) = K² + 1 = 5). Actually, h⁰(−K_{dP_5}) = 5, so the anticanonical map goes to CP⁴.
- The Hilbert space of sections of O(−kK) has dimension given by Riemann-Roch: h⁰(−kK) = 1 + 5k/2 + 3k²/2 (for dP₅ with K² = 4).
- At k = 1: dim = 5. At k = 2: dim = 12. At k = 3: dim = 23. At k = 5: dim = 51.
- The T-iteration at degree k involves N×N matrices where N = h⁰(−kK). At k = 5, this is 51×51 — very manageable.
- **The key challenge:** numerical integration on dP₅. One needs to sample points on the surface and compute inner products of sections. This requires an explicit description of dP₅ (e.g., as a complete intersection, or via the blowup construction with explicit charts).

### Assessment
- **Feasibility:** 6/10
- **Key obstacle:** Implementing the point-sampling on dP₅ and the section basis computation
- **Advantage:** Does not require toric structure. Works for any Fano manifold.
- **Implementation in SageMath:** SageMath can handle the algebraic geometry (sections of line bundles, intersection theory) and the linear algebra. The numerical integration would need scipy or custom code.

---

## 4. Alternative Tools: SageMath and Toric Degenerations

### 4a. SageMath for Algebraic Geometry on dP₅

**Verdict: EXCELLENT for the algebraic/topological parts; insufficient alone for the analytic torsion.**

SageMath can:
- Compute intersection theory on dP₅ (already done in Phase 21)
- Work with the Picard lattice H²(dP₅, Z) and intersection form
- Compute cohomology of line bundles (Riemann-Roch, vanishing theorems)
- Handle toric varieties and their cohomology rings
- Compute modular forms, eta functions, theta functions (used in Phase 21B DKL computation)

SageMath cannot:
- Solve the Monge-Ampère equation for the KE metric
- Compute Laplacian eigenvalues on a Riemannian manifold
- Perform finite element analysis

### 4b. Toric Degeneration of dP₅

**Verdict: THEORETICALLY INTERESTING but does not simplify the core computation.**

- Every smooth del Pezzo surface with very ample anticanonical class admits a toric degeneration (a flat degeneration to a toric variety).
- For dP₅, the Fano polytope of the toric model can be constructed from the Newton polytope of the anticanonical class.
- **However:** The toric degeneration gives a singular toric variety (with at most Gorenstein singularities), not the smooth dP₅ itself. The analytic torsion of the singular limit is not the same as the smooth surface.
- **Potential use:** As a starting point for the Donaldson iteration (initialize with the toric metric and iterate to the balanced metric). This is exactly what Doran-Headrick suggest for dP₃.

### Assessment
- SageMath: **8/10 for algebraic parts** (already proven in Phase 21)
- Toric degeneration: **4/10** (useful as initialization only)

---

## 5. The Yoshikawa Formula

**Verdict: DOES NOT DIRECTLY APPLY to del Pezzo surfaces, but the Mourougane approach does.**

### Findings

**Yoshikawa's work** focuses on:
- K3 surfaces with involution (equivariant analytic torsion → Borcherds Φ-function)
- Enriques surfaces (quotient of K3 by fixed-point-free involution)
- Log-Enriques surfaces (with cyclic quotient singularities → Borcherds products)
- Borcea-Voisin Calabi-Yau threefolds

**Connection to del Pezzo:** The complex structure moduli of good log-Enriques surfaces are isomorphic to the Kähler moduli of del Pezzo surfaces (mirror symmetry at genus one). This means Yoshikawa's Borcherds product formulas are mirror-dual to del Pezzo data. But extracting the analytic torsion of dP₅ from this route requires the full mirror map, which is itself a nontrivial computation for non-toric surfaces.

**Mourougane (2006) — THE KEY FINDING:**
Mourougane computes the analytic torsion of Hirzebruch surfaces F_n = P(O ⊕ O(n)) using:
1. The arithmetic Riemann-Roch theorem (Gillet-Soulé)
2. Explicit computation of Bott-Chern secondary classes on projective bundles P(E)

**Critical fact:** F₁ = dP₁ = Bl₁(CP²). Mourougane's formula gives the analytic torsion of dP₁ explicitly.

**The blowup question:** Can we extend Mourougane's method to compute the change in analytic torsion under successive blowups CP² → dP₁ → dP₂ → ... → dP₅?

The Bismut-Gillet-Soulé anomaly formula relates the analytic torsion of fibers in a holomorphic family. The BCOV blowup formula (Zhang 2023) gives the behavior of the BCOV invariant under blowup. These results suggest that **a blowup formula for Ray-Singer analytic torsion on surfaces exists in principle**, connecting T(dPₙ) to T(dPₙ₋₁).

### Assessment
- Yoshikawa formula for dP₅ directly: **2/10** (wrong class of surfaces)
- Mourougane + blowup iteration: **7/10** (the most promising theoretical route)
- **Key papers needed:** Mourougane (math/0401029), Bismut-Gillet-Soulé (CMP 1988), Zhang (Compositio 2023)

---

## 6. BCOV / F₁ Amplitude Route

**Verdict: PARTIALLY VIABLE for toric del Pezzos; DIFFICULT for dP₅.**

### Findings

**For toric del Pezzos (dP₀ = CP², dP₁, dP₂, dP₃):**
- The topological vertex computes the full topological string partition function, including F₁ (genus-one free energy).
- Klemm-Zaslow (1999) computed local mirror symmetry results for local CP² (= local dP₀).
- Huang-Klemm-Reuter-Schiereck (2015) used mirror symmetry and quantum geometry to compute refined free energies on "non-compact toric Calabi-Yau manifolds based on del Pezzo surfaces" — but explicitly for TORIC geometries.
- Gopakumar-Vafa invariants are tabulated for toric del Pezzos.

**For non-toric del Pezzos (dP₄ through dP₈):**
- The topological vertex does NOT apply directly.
- The blowup equation approach (arXiv:2112.14753) relates blowup equations to holomorphic anomaly equations and introduces a "consistency equation" — but explicit computations for dP₅ are not given.
- The Hu-Li-Ruan blowup formula relates local GW invariants of dPₙ to dPₙ₋₁ for individual curve classes, but not the complete F₁.
- **The mirror of local dP₅ has 6 complex structure moduli.** The Picard-Fuchs system is a coupled system of 6 PDEs. Only dP₀ and dP₁ have explicit mirror curve results in the literature (Choi-Katz-Klemm 2012).

**Spectral theories on del Pezzo geometries (2020):**
- Recent work reformulates partition functions via quantum curves on del Pezzo geometries with exceptional algebra symmetry.
- Explicit grand potentials have been conjectured for local dP₅, but these are spectral theory results (related to the quantum Baxter equation), not direct F₁ computations.

### Assessment
- F₁ for toric dP₀, dP₁, dP₂, dP₃: **8/10** (known or computable via topological vertex)
- F₁ for dP₅: **3/10** (would require solving the full 6-moduli Picard-Fuchs system)
- **Validation strategy:** Compute F₁ and threshold corrections for dP₁ and dP₃ (toric, known results) to validate the method before attempting dP₅.

---

## 7. Minimum Viable Computation

**Verdict: Start with toric validation cases, then attack dP₅ via blowup iteration.**

### The Cascade Strategy

**Step 1: CP² (EXACT, KNOWN)**
- The spectrum of the Dolbeault Laplacian on CP² with Fubini-Study metric and line bundles O(k) is exactly known. The eigenvalues are determined by representation theory of SU(3).
- Spectral zeta functions on CPⁿ with Fubini-Study metric have been explicitly computed (see the paper on spectral zeta functions of Laplacians on projective complex spaces).
- This gives T(CP², O(k)) in closed form → exact base case.

**Step 2: dP₁ = F₁ (EXACT, via Mourougane)**
- Mourougane (2006) computes T(F₁) explicitly using arithmetic RR + Bott-Chern classes.
- F₁ = Bl₁(CP²) = dP₁, so this gives the analytic torsion after one blowup.
- Compare with the blowup formula: T(dP₁) should be related to T(CP²) by a computable correction term.

**Step 3: dP₂, dP₃ (VALIDATION via toric + topological vertex)**
- dP₂ and dP₃ are toric, so their F₁ amplitudes are computable via the topological vertex.
- The Doran-Headrick numerical KE metric exists for dP₃, allowing direct numerical validation.
- **Key test:** Does the blowup iteration CP² → dP₁ → dP₂ → dP₃ reproduce the known F₁ values?

**Step 4: dP₄ (FIRST NON-TORIC CASE)**
- dP₄ is the first non-toric del Pezzo. Apply the blowup formula from dP₃.
- No independent check available from the topological vertex, but consistency with the Donaldson balanced metric approximation can be verified.

**Step 5: dP₅ (THE TARGET)**
- Apply the blowup formula from dP₄.
- Alternatively, use the Donaldson balanced metric at degree k = 5-10 to numerically compute Laplacian eigenvalues and assemble the analytic torsion.
- Compare the threshold correction Δ₃ − Δ₂ to ln(3)/√2.

### Assessment of Cascade
- Step 1: **10/10** feasibility (exact, literature result)
- Step 2: **8/10** (Mourougane's result exists; need to extract the right formula for line bundles)
- Step 3: **7/10** (toric methods well-understood; need to implement topological vertex or use literature values)
- Step 4: **5/10** (first test of blowup formula beyond toric regime)
- Step 5: **4/10** (the actual computation; depends on all previous steps)

---

## Recommended Strategy: Three Parallel Tracks

### Track A: Blowup Iteration (ANALYTICAL — HIGHEST PRIORITY)

**Goal:** Compute T(dP₅, L_Y^n) by iterating the blowup formula from CP².

**Method:**
1. Start with the known analytic torsion on CP² with Fubini-Study metric and line bundles O(k).
2. Use the Bismut-Gillet-Soulé anomaly formula / Mourougane blowup method to compute the change in analytic torsion under blowup at a point.
3. Iterate: CP² → dP₁ → dP₂ → dP₃ → dP₄ → dP₅.
4. At each step, the line bundle L_Y must be tracked through the blowup (its pullback gains a component along the exceptional divisor).

**Tools:** SageMath (algebraic geometry, intersection theory, modular forms) + analytical computation.

**Key papers to study in detail:**
- Mourougane, "Analytic torsion of Hirzebruch surfaces" (math/0401029)
- Mourougane, "Computations of Bott-Chern classes on P(E)" (Duke Math J 2004)
- Bismut-Gillet-Soulé, "Analytic torsion and holomorphic determinant bundles I-III" (CMP 1988)
- Zhang, "BCOV invariant and blow-up" (Compositio 2023)

**Estimated complexity:** 2-3 dedicated sessions for the mathematical development, 1-2 sessions for computation.

**Risk:** The blowup formula may introduce dependence on the position of the blown-up points (for n ≥ 4, del Pezzo surfaces depend on the configuration of points). The analytic torsion of dP₅ is NOT unique — it depends on the complex structure moduli. However, the KE metric exists for all smooth dP₅ (Tian 1990), so the analytic torsion with KE metric is well-defined for each choice.

### Track B: Numerical Dolbeault Spectrum (COMPUTATIONAL — PARALLEL)

**Goal:** Numerically compute eigenvalues of the Dolbeault Laplacian on dP₅ with line bundle L_Y^n.

**Method:**
1. Implement Donaldson's T-iteration to find balanced metrics on dP₅ at degree k = 5, 8, 10.
2. Use these metrics to discretize the Dolbeault Laplacian Δ_{0,q}^{L_Y^n}.
3. Apply the Ashmore et al. (2023) method for numerical eigenvalue computation.
4. Compute the spectral zeta function ζ'(0) by truncation + Richardson extrapolation.
5. Assemble f(L^n) and the threshold correction.

**Tools:** Python/SageMath for algebraic geometry setup, numpy/scipy for linear algebra, potentially WSL for heavy computation.

**Key papers:**
- Donaldson, "Some numerical results in complex differential geometry" (math/0512625)
- Ashmore-He-Heyes-Ovrut, "Numerical spectra of the Laplacian for line bundles" (JHEP 2023, arXiv:2305.08901)
- Doran-Headrick et al., "Numerical KE metric on dP₃" (hep-th/0703057)

**Estimated complexity:** 3-5 dedicated sessions. The main challenge is implementing the dP₅ geometry (coordinate charts, transition functions, section bases) for the Donaldson iteration.

**Risk:** Numerical precision. The zeta-regularized determinant requires accurate low-lying eigenvalues AND the Weyl asymptotics for the tail. Getting ζ'(0) to 4+ significant digits may require large k in the Donaldson approximation.

### Track C: Z₃ Orbifold DKL Integral (CONTINUATION — ALREADY STARTED)

**Goal:** Complete the heterotic dual computation from Phase 21B.

**Method:**
1. Choose a specific Z₃ orbifold model with Wilson line breaking E₆ → SU(5) → SM.
2. Compute the shifted lattice theta function at the Z₃ fixed point.
3. Evaluate the twisted sector contribution.
4. Assemble the full threshold Δ₃ − Δ₂.

**Tools:** SageMath (modular forms, lattice theta functions, eta products).

**Status:** Phase 21B already identified the mechanism (ln(3) from Γ(1/3) via Z₃ structure) and the simplification (E₄(ω) = 0). The remaining frontier is the Wilson line / twisted sector computation.

**Estimated complexity:** 1-2 dedicated sessions.

**Risk:** This is the heterotic dual, not the direct F-theory computation. Agreement between the two would be powerful evidence but not a direct proof.

---

## Feasibility Matrix

| Approach | Feasibility | Precision | Independence | Sessions |
|----------|------------|-----------|--------------|----------|
| A: Blowup iteration | 7/10 | Exact (if formula works) | High | 3-5 |
| B: Numerical spectrum | 5/10 | ~4 digits | High | 3-5 |
| C: Z₃ DKL integral | 7/10 | Exact | Medium (dual) | 1-2 |
| FEniCS 4D | 0/10 | — | — | — |
| Full KE metric on dP₅ | 3/10 | High | High | 10+ |
| F₁ via mirror symmetry | 3/10 | Exact | High | 5-10 |
| Yoshikawa formula | 2/10 | Exact | Medium | 5+ |

---

## Immediate Next Steps

1. **Session priority:** Track C (complete the Z₃ DKL computation — closest to done)
2. **Next session:** Track A (study Mourougane's paper in detail; determine whether the blowup formula for analytic torsion with line bundles is explicit enough for iteration)
3. **Background preparation for Track B:** Set up dP₅ coordinate charts in SageMath; implement section bases for O(−kK); prepare for Donaldson iteration

### The Key Mathematical Question to Resolve First

**Does the Bismut-Gillet-Soulé anomaly formula give an EXPLICIT, COMPUTABLE correction term for the analytic torsion when blowing up a point on a surface?**

If yes: Track A is the clear winner — iterate from CP² to dP₅ in closed form.
If no (i.e., the formula is implicit or requires the metric): Track B becomes necessary.

Mourougane's paper is the Rosetta Stone here. He computes T(F_n) for Hirzebruch surfaces F_n = P(O ⊕ O(n)), which includes F₁ = dP₁. The question is whether his method generalizes to blowups at more than one point (i.e., to dP₂ through dP₅).

---

## Key References (Organized by Track)

### Track A (Blowup Iteration)
- Mourougane (2006), "Analytic torsion of Hirzebruch surfaces," Math. Ann. 335, 221-247. [arXiv:math/0401029]
- Mourougane (2004), "Computations of Bott-Chern classes on P(E)," Duke Math. J. 124, 389-420.
- Bismut-Gillet-Soulé (1988), "Analytic torsion and holomorphic determinant bundles I-III," CMP 115.
- Zhang (2023), "BCOV invariant and blow-up," Compositio Math. 159, 780-829.
- Gillet-Soulé, "Arithmetic Riemann-Roch theorem."

### Track B (Numerical Spectrum)
- Donaldson (2005), "Some numerical results in complex differential geometry." [arXiv:math/0512625]
- Ashmore-He-Heyes-Ovrut (2023), "Numerical spectra of the Laplacian for line bundles on CY hypersurfaces," JHEP. [arXiv:2305.08901]
- Doran-Headrick-Herzog-Kantor-Wiseman (2008), "Numerical KE metric on dP₃," CMP 282. [arXiv:hep-th/0703057]

### Track C (Z₃ DKL Integral)
- Erler-Jungnickel-Nilles (1993), NPB 407.
- Stieberger (1993), NPB 407.
- Kaplunovsky-Louis (1995), NPB 444.
- Phase 21B results: `ln3_sqrt2_phase21B.md`

### Track D (BCOV / F₁ Amplitude)
- BCOV (1993, 1994), [hep-th/9302103], [hep-th/9309140].
- Huang-Klemm-Reuter-Schiereck (2015), [arXiv:1401.4723].
- Klemm-Zaslow (1999), [hep-th/9906046].
- arXiv:2112.14753 (Blowup equations and holomorphic anomaly equations).

### Supplementary
- Tian (1990), "On Calabi's conjecture..." — existence of KE on dP₅.
- Conlon-Palti (2009), [arXiv:0907.1362] — F-theory gauge threshold corrections.
- Spectral zeta functions on CPⁿ — base case for Track A.

---

*This strategy document supersedes the unstructured discussion in `f1_dP5_results.md` §8 (The Remaining Computation). The cascade approach through blowup iteration was not previously considered and represents a significant simplification over the brute-force numerical KE metric approach.*

*"Seek the balance, work the science, synthesize." — Puscifer's Theorem*
