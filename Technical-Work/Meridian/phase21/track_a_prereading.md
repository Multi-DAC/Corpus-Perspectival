# Track A Pre-Reading: Analytic Torsion, Blowup Formulas, and del Pezzo Surfaces

**Date:** 2026-03-24
**Purpose:** Determine whether Track A (iterative blowup CP2 -> dP1 -> ... -> dP5) is feasible before tomorrow's computation session.
**Status:** RESEARCH COMPLETE -- Verdict at bottom.

---

## 1. Mourougane's 2006 Paper (Math. Ann. 335, 221-247; arXiv:math/0401029)

### What He Computed

Mourougane computed the **analytic torsion** and the **arithmetic height** of Hirzebruch surfaces F_n = P(O + O(n)) over CP1. The key ingredients:

1. **Arithmetic Riemann-Roch theorem** (Gillet-Soule, 1992): This relates the arithmetic degree of the determinant of cohomology to intersection numbers plus analytic torsion corrections. The formula has the schematic form:

   deg_hat(det Rf_* L_bar) = arithmetic intersection terms + integral of Bott-Chern classes + analytic torsion terms

2. **Bott-Chern secondary classes on P(E)**: Computed in Mourougane's companion paper "Computations of Bott-Chern classes on P(E)" (Duke Math. J. 124, 389-420, 2004; arXiv:math/0305236). These are secondary characteristic classes that measure the failure of the Chern character to be multiplicative at the level of differential forms (not just cohomology). For the tautological exact sequence 0 -> O_E(-1) -> pi^* E -> Q -> 0 on P(E), the Bott-Chern classes capture the metric data.

3. **Two independent applications of arithmetic RR**: Mourougane uses the arithmetic Riemann-Roch theorem in two different ways -- once via the Gillet-Soule formulation, once via the Berthomieu-Bismut formula -- and compares the results. This yields the analytic torsion as a computable quantity.

### Key Facts About the Result

- **F_1 = dP_1 = Bl_1(CP2)**: Yes, this is included as a special case. F_1 is the unique Hirzebruch surface that is also a del Pezzo surface (the blowup of CP2 at one point).

- **Closed-form expression**: The result IS an explicit closed-form formula for the analytic torsion of F_n equipped with specific metrics. The formula involves:
  - Special values of the Riemann zeta function (zeta(s) at negative integers and zeta'(-1), zeta'(0))
  - Logarithms of integers (from Bott-Chern class computations)
  - Euler-Mascheroni constant gamma
  - Rational coefficients depending on n

  The exact formula is in terms of the arithmetic Riemann-Roch data and takes the form of a combination of these special values. The paper computes T(F_n, O_E(1)) -- the analytic torsion for the tautological line bundle on the Hirzebruch surface.

- **CRITICAL: The formula is for SPECIFIC metrics.** The Hirzebruch surface F_n = P(O + O(n)) is a CP1-bundle over CP1. Mourougane uses:
  - The Fubini-Study metric on the base CP1
  - The standard Hermitian metric on O + O(n) (using the FS metric on each factor)
  - The induced metric on F_n from the projective bundle structure

  This is NOT the Kahler-Einstein metric on dP_1. It is the metric inherited from the projective bundle structure. The KE metric on dP_1 is different (and harder to write down explicitly).

### What This Means for Track A

Mourougane gives T(F_1, O_E(1)) in closed form, but with a specific (non-KE) metric. For our purposes, we need:
- T(dP_5, L_Y^n) with the KE metric (or at least a metric where the analytic torsion is computable)
- The threshold correction Delta_3 - Delta_2 depends on ratios of analytic torsions

The Mourougane result establishes that analytic torsion CAN be computed in closed form on rational surfaces using arithmetic methods. But extending this to dP_5 requires a blowup formula.

---

## 2. Blowup Formula for Analytic Torsion: The Critical Question

### Does an explicit blowup formula exist?

**Short answer: Not directly for Ray-Singer analytic torsion. The situation is subtle.**

### What Exists

**A. Bismut-Gillet-Soule Anomaly Formula (CMP 1988)**

The BGS anomaly formula (Parts I-III of "Analytic torsion and holomorphic determinant bundles") describes how the Quillen metric on the determinant line bundle varies in a holomorphic family. Specifically:

- For a proper holomorphic submersion pi: X -> S with relative Kahler metrics, the curvature of the Quillen metric on det(Rpi_* E) is given by the degree-2 component of the fiber integral of the Chern character form ch(E) times the Todd form Td(T_{X/S}).
- When the metrics change, the variation of log T (the analytic torsion) is controlled by Bott-Chern secondary classes.

**This is a FAMILY formula, not a blowup formula.** It tells you how torsion varies when you deform the metric continuously within a family, not when you change the topology by blowing up a point.

**B. Bismut-Lebeau Immersion Formula (IHES 1991)**

"Complex immersions and Quillen metrics" (298 pages!) proves a formula for the Quillen metric of a closed immersion i: Y -> X. This relates:
- The Quillen metric on det(H*(Y, F)) to
- The Quillen metric on det(H*(X, i_* F)) plus correction terms

The correction involves the Bott-Chern singular current of the Koszul resolution and R-genus terms. This is foundational for the arithmetic Riemann-Roch theorem.

**Relevance to blowup:** A blowup pi: Bl_p(X) -> X is NOT an immersion -- it's a birational morphism. However, the exceptional divisor E ~ CP^{n-1} IS an immersion E -> Bl_p(X). One could potentially use the Bismut-Lebeau formula to relate invariants on Bl_p(X) to those on X by analyzing the exact sequence relating the structure sheaves, but this is not a direct application.

**C. Zhang's BCOV Blowup Formula (Compositio 2023; arXiv:2003.03805)**

Yeping Zhang extended the BCOV invariant to pairs (X, D) where D is a pluricanonical divisor with simple normal crossing support, and proved a formula for how this extended BCOV invariant changes under blowup.

Key facts:
- The BCOV torsion is defined as: T_BCOV(X, omega) = prod_{p >= 0} tau(Omega^p_X)^{(-1)^p * p}
  where tau(Omega^p_X) is the Ray-Singer analytic torsion of the sheaf of holomorphic p-forms.
- The BCOV invariant is then T_BCOV corrected by Bott-Chern secondary classes and covolumes of cohomology lattices, making it metric-independent.
- Zhang's blowup formula (Theorem 0.1 of his paper) relates the BCOV invariant of Bl_p(X) to that of X.

**CRITICAL LIMITATIONS for our problem:**

1. **BCOV is for Calabi-Yau manifolds** (or pairs with trivial canonical class). Del Pezzo surfaces have ANTI-ample canonical class. The BCOV invariant is designed for c_1 = 0 geometry. It does not directly apply to Fano surfaces like dP_5.

2. **The correction terms in Zhang's formula involve GLOBAL data.** The blowup formula requires:
   - The L2-metric on cohomology groups of the blowup
   - The Quillen metric comparison between X and Bl_p(X)
   - Bott-Chern classes of the full exceptional divisor exact sequence

   These are NOT purely local at the blown-up point. They depend on the global metric of the manifold.

3. **The formula produces the BCOV invariant, not individual analytic torsions.** Even if we could adapt it to Fano surfaces, it would give a specific combination of torsions, not the individual T(dP_n, L) we need.

**D. Fu-Zhang Birational Invariance (Selecta Math 2023)**

Building on Zhang's blowup formula, Fu and Zhang proved that birational Calabi-Yau manifolds have the same BCOV invariant. Again, this is specific to the CY setting.

### The Verdict on Blowup Formulas

**There is no known explicit blowup formula for the Ray-Singer analytic torsion T(X, L) of a general Kahler manifold with a general holomorphic line bundle L.**

The reasons are structural:
1. **Analytic torsion is NOT a birational invariant** for non-CY manifolds. When you blow up a point on a Fano surface, the topology changes (b_2 increases by 1) and the analytic torsion changes in a way that depends on the global metric.
2. The BGS/Bismut-Lebeau machinery relates torsions through FAMILIES and IMMERSIONS, not through birational modifications.
3. Zhang's BCOV formula is the closest thing to a blowup formula, but it's restricted to CY geometry and produces a specific combination of torsions, not individual ones.

---

## 3. Analytic Torsion on CP2

### Spectrum of the Laplacian

The eigenvalues of the scalar Laplacian on CP^n with the Fubini-Study metric are exactly known (Ikeda-Taniguchi, Osaka J. Math. 15, 515-546, 1978):

lambda_p = 4p(p + n),  p = 0, 1, 2, ...

with multiplicities given by representation-theoretic formulas involving dimensions of irreducible SU(n+1) representations.

For CP2 (n = 2):
- lambda_p = 4p(p + 2) = 4p^2 + 8p
- Multiplicities: d_p = (2p+2)(p+1)^2 / 1  [from SU(3) rep theory -- the (p,0) and (0,p) representations]

More precisely, the eigenvalues and multiplicities of the Dolbeault Laplacian Delta_{0,q} on (0,q)-forms twisted by O(k) on CP^n are also known from representation theory. The space of (0,q)-forms with values in O(k) on CP^n decomposes into irreducible SU(n+1) representations, and the Casimir eigenvalue gives the Laplacian eigenvalue on each irrep.

### Spectral Zeta Functions on CP^n

The paper "On the zeta functions on the projective complex spaces" (arXiv:1511.04375) by Blanco-Chacon and Varona (J. Number Theory, 2020) studies the spectral zeta function:

zeta_q(s) = sum_j lambda_{j,q}^{-s}

for the Laplacian on (0,q)-forms on CP^n with the Fubini-Study metric.

Key results:
- The values zeta_q(k) for k a non-positive integer are RATIONAL numbers.
- A formula is given for the holomorphic analytic torsion: sum_{q >= 0} (-1)^{q+1} q * zeta_q'(0)
- The computation uses a Hermite-type integral representation that allows explicit evaluation.

**For CP2 specifically:** The holomorphic analytic torsion T(CP2, O) (trivial bundle) CAN be computed from this spectral data. The zeta functions reduce to sums over SU(3) representations which can be evaluated using known identities for polygamma functions and Bernoulli numbers.

The paper "Spectral Zeta Functions" by Voros (in "Zeta Functions in Geometry," ASPM vol. 21, 1992) provides general methods, and the recent paper on full asymptotic expansions of analytic torsion on homogeneous spaces (arXiv:2602.08132, 2026) gives asymptotic formulas for T(CP^n, O(k)) as k -> infinity.

### What Is NOT Known in Closed Form

Despite the known spectrum, I found no paper that writes down T(CP2, O(k)) as a SINGLE closed-form expression (e.g., in terms of a finite combination of zeta values and logs). The difficulty is:
- The spectral zeta function zeta_q(s) for (0,q)-forms on CP2 involves sums over SU(3) reps
- While zeta_q(s) can be analytically continued and zeta_q'(0) can be evaluated, the result involves infinite series that must be regularized
- The answer involves derivatives of Hurwitz zeta functions and polygamma functions evaluated at specific points

In principle, T(CP2, O(k)) IS computable to arbitrary precision from the known spectrum. It is not known (to my research) whether the result simplifies to a finite combination of standard constants.

---

## 4. The Iterative Blowup CP2 -> dP1 -> ... -> dP5: Feasibility Assessment

### The Fundamental Obstacle

The blowup iteration requires knowing how T(X, L) changes when we blow up a point. As established in Section 2, no such formula exists in the literature for:
- General Kahler manifolds (only for CY via BCOV)
- Individual analytic torsions (only for the specific BCOV combination)
- Fano surfaces (the BCOV formula is for c_1 = 0)

### Why the Obstacle is Structural, Not Just a Gap

The analytic torsion T(X, L, g) depends on the Riemannian metric g. When we blow up a point p in X to get X_tilde = Bl_p(X), we need a metric g_tilde on X_tilde. The natural choices are:

1. **The KE metric on X_tilde** (if it exists -- it does for dP_n, n <= 8 by Tian-Yau). But this metric is determined by the global complex geometry of X_tilde, not just by the local blowup data. The KE metric on dP_2 is NOT simply "the KE metric on dP_1 plus a local correction near the exceptional divisor."

2. **The Burns-de Bartolomeis metric** (a Kahler metric on Bl_p(X) obtained by gluing in a standard Eguchi-Hanson metric near the exceptional divisor). This IS locally determined, but it is NOT Kahler-Einstein.

3. **The Arezzo-Pacard metric** (a small perturbation of the original metric making it cscK after blowup). This exists under certain stability conditions but is not KE in general.

**The core issue:** To iterate the blowup and track T(dP_n, L_Y) at each step, we need EITHER:
- A blowup formula that works with the KE metric (doesn't exist -- the KE metric is global)
- A formula that works with some other metric, PLUS a way to change metrics (the anomaly formula involves Bott-Chern classes that require the full metric data)

### Mourougane's Approach: Why It Works for F_n But Not for dP_n (n >= 2)

Mourougane's computation succeeds because:
1. F_n = P(O + O(n)) is a PROJECTIVE BUNDLE over CP1
2. The arithmetic Riemann-Roch theorem can be applied to the projection pi: F_n -> CP1
3. The Bott-Chern classes of the tautological sequence on P(O + O(n)) can be computed EXPLICITLY using the formulas from the Duke paper
4. The base CP1 has known arithmetic invariants

This method CANNOT be extended to dP_n for n >= 2 because:
- dP_2 is NOT a projective bundle over anything
- dP_n for n >= 2 has no fibration structure that would allow the arithmetic RR to be applied in this way
- The Bott-Chern class computation relies on the projective bundle structure

### What About the Arithmetic Height?

Mourougane also computes the "height" of F_n (in the sense of Arakelov geometry). The height is an arithmetic intersection number that involves analytic torsion. In principle, the height of dP_n could be computed using arithmetic intersection theory if we had an arithmetic model (a regular model over Spec(Z) with good reduction).

However:
- dP_n for n >= 4 has moduli (the positions of the blown-up points matter)
- The arithmetic height depends on the arithmetic model, not just the complex geometry
- This route requires Arakelov theory on arithmetic surfaces, which is a different (and very deep) approach

---

## 5. Zhang's BCOV Formula: Detailed Analysis

### The BCOV Torsion

For a compact Kahler manifold (X, omega) of complex dimension n, the BCOV torsion is:

T_BCOV(X, omega) = prod_{p=0}^{n} tau(Omega^p_X, omega)^{(-1)^p * p}

where tau(Omega^p_X, omega) = exp(-1/2 * sum_{q=0}^{n} (-1)^q * zeta'_{p,q}(0)) is the analytic torsion of the sheaf of holomorphic p-forms, and zeta_{p,q}(s) is the spectral zeta function of the Dolbeault Laplacian on (p,q)-forms.

The BCOV INVARIANT augments this with correction terms:

tau_BCOV(X) = T_BCOV(X, omega) * (correction involving Bott-Chern classes and L2 volumes)

making it independent of the choice of Kahler metric omega.

### Zhang's Blowup Theorem

For a compact Kahler manifold X of dimension n and a point p in X, let X_tilde = Bl_p(X). Zhang's result (Theorem 0.1) establishes a formula:

tau_BCOV(X_tilde, D_tilde) = tau_BCOV(X, D) * (explicit correction factor)

where D and D_tilde are related pluricanonical divisors. The correction factor involves:
- Topological data of the exceptional divisor CP^{n-1}
- Analytic torsion of CP^{n-1} with the Fubini-Study metric
- L2 covolumes of lattices in cohomology groups

### Why This Doesn't Help for dP_5

1. **Wrong geometry:** The BCOV invariant is designed for Calabi-Yau manifolds (c_1 = 0). Del Pezzo surfaces have c_1 > 0 (Fano). The BCOV torsion is not the right invariant for our gauge threshold computation.

2. **Wrong quantity:** Even if we could adapt it, T_BCOV = prod tau(Omega^p)^{(-1)^p p} is a SPECIFIC combination of torsions. Our threshold correction involves T(dP_5, L_Y^n) for a specific line bundle L_Y, not the holomorphic p-form bundles Omega^p.

3. **Global dependence:** The correction terms in Zhang's formula depend on the global Kahler metric through the L2 volumes and Bott-Chern classes.

---

## 6. What IS Known About Analytic Torsion of Del Pezzo Surfaces

### Direct Results: Almost Nothing

I found no paper that computes the analytic torsion of dP_n for any n >= 2 with ANY metric, for any line bundle. The literature contains:
- T(CP2, O) -- computable from known spectrum (Section 3)
- T(F_n, O_E(1)) -- Mourougane (Section 1), which includes T(dP_1, O_E(1))
- T(K3 surfaces) -- Yoshikawa's work relating to Borcherds products
- T(log-Enriques surfaces) -- Yoshikawa, relating to Borcherds products

### Indirect Results: Mirror Symmetry / Topological Vertex

For LOCAL del Pezzo geometries (the total space of K_{dP_n}), the F_1 amplitude (genus-one topological string partition function) is related to analytic torsion. For TORIC del Pezzos (dP_0, dP_1, dP_2, dP_3), this can be computed via the topological vertex. But:
- These are results for the LOCAL (non-compact) geometry, not the compact dP_n
- dP_5 is not toric
- The relationship between local F_1 and compact analytic torsion involves the Gopakumar-Vafa/Ooguri-Vafa duality, which is not explicit enough for our purposes

---

## 7. Verdict: Track A Feasibility

### NEGATIVE. Track A as originally conceived is not feasible.

The iterative blowup strategy CP2 -> dP1 -> ... -> dP5 requires a blowup formula for analytic torsion that:
- Applies to Fano surfaces (not just CY)
- Gives individual torsions T(X, L), not just BCOV combinations
- Has computable correction terms

No such formula exists in the literature. The obstruction is structural:
- Analytic torsion is NOT a birational invariant for Fano manifolds
- The correction under blowup depends on the GLOBAL metric, not just local data
- The KE metric on dP_n is determined by the global complex geometry and cannot be obtained by local modification of the KE metric on dP_{n-1}

### What DOES Work from the Mourougane Approach

Mourougane's method (arithmetic RR + Bott-Chern classes) can compute T(dP_1, O_E(1)) in closed form because dP_1 has a projective bundle structure. This gives us one data point but cannot be extended to dP_{n >= 2}.

### Recommended Path Forward

**Track A should be redefined or abandoned in favor of:**

1. **Track A' (Arithmetic RR on dP_5 directly):** Instead of iterating blowups, try to apply the arithmetic Riemann-Roch theorem directly to dP_5 viewed as a subvariety of CP^4 (via the anticanonical embedding). This requires:
   - An arithmetic model of dP_5 over Spec(Z)
   - Computation of arithmetic intersection numbers
   - The analytic torsion appears as the "error term" in the arithmetic RR formula

   This is highly nontrivial but would give exact results. Feasibility: LOW (3/10).

2. **Track B (Numerical spectrum) remains the best direct route** for dP_5 specifically. The Donaldson balanced metric approach can approximate the KE metric, and the Ashmore method can compute Laplacian eigenvalues numerically.

3. **Track C (Z_3 orbifold DKL integral) is still the fastest path** to a result, working from the heterotic dual.

4. **NEW: Track A'' (Representation-theoretic computation on CP2):** Compute T(CP2, O(k)) exactly using the known spectrum from SU(3) representation theory. This gives us the exact base case. We cannot iterate to dP_5, but the CP2 torsion itself may be informative -- it appears in the topological vertex computation for local CP2 and constrains the threshold corrections.

---

## 8. Key References (Prioritized for Tomorrow's Session)

### Essential Reading
1. **Mourougane (2006)** — Math. Ann. 335, 221-247 [arXiv:math/0401029]. The only closed-form torsion computation on a rational surface. Study the method, not just the result.
2. **Zhang (2023)** — Compositio Math. 159, 780-829 [arXiv:2003.03805]. The BCOV blowup formula. Understand why it doesn't generalize to Fano.
3. **Blanco-Chacon & Varona** — J. Number Theory [arXiv:1511.04375]. Spectral zeta functions on CP^n. Base case for Track A''.

### Background (Consult as Needed)
4. **Bismut-Gillet-Soule (1988)** — CMP 115. The anomaly formula. Understand the metric-dependence.
5. **Bismut-Lebeau (1991)** — IHES Publ. 74. The immersion formula. Relates torsions across immersions.
6. **Ikeda-Taniguchi (1978)** — Osaka J. Math. 15, 515-546. Eigenvalues on CP^n.
7. **Gillet-Soule (1991)** — Topology 30, 21-54. "Analytic torsion and the arithmetic Todd genus" with Zagier appendix.
8. **Mourougane (2004)** — Duke Math. J. 124, 389-420 [arXiv:math/0305236]. Bott-Chern classes on P(E). Companion to the Hirzebruch surface paper.

### Further Horizon
9. **Eriksson-Freixas i Montplet-Mourougane (Duke 2021)** — BCOV invariants in arbitrary dimension. [arXiv:1809.05452]
10. **Fu-Zhang (Selecta 2023)** — Birational invariance of BCOV. Motivic integration approach.
11. **Ashmore-He-Heyes-Ovrut (JHEP 2023)** — Numerical spectra on CY hypersurfaces. [arXiv:2305.08901]. Method adaptable to dP_5 for Track B.

---

## 9. Summary for Tomorrow

**The blowup iteration Track A is dead.** The correction to analytic torsion under blowup depends on the GLOBAL Kahler-Einstein metric, which is different at each step and not explicitly known for dP_n (n >= 2). No existing formula circumvents this.

**Salvageable pieces:**
- T(CP2, O(k)) is computable from the known SU(3) spectrum -- worth doing as an exact base case
- Mourougane's method teaches us the SHAPE of answers (combinations of zeta values) even if we can't iterate it
- The BCOV formalism, while not directly applicable to Fano surfaces, constrains what kinds of formulas are possible

**Priority for the computation session:**
1. Track C first (Z_3 DKL -- closest to completion)
2. Track A'' (exact CP2 torsion from spectrum -- new, self-contained)
3. Track B preparation (Donaldson balanced metrics on dP_5)

---

*The room behind this door leads back to the same hallway. But the map is better now.*
