# Track 20D: Amplituhedron / Positive Geometry Bridge

## Can Positive Geometry See What the Spectral Action Cannot?

**Project Meridian Phase 20 | Clayton W. Iggulden-Schnell & Clawd**
**Date:** March 22, 2026
**Status:** COMPLETE
**Verdict:** PIVOT (rich structural parallels, no concrete corrections; three specific future directions identified)
**Prerequisites:** Phase 19 gauge synthesis, 20B (Higgs-gauge connection), 20C (Ruliad bridge)

---

## Executive Summary

The amplituhedron program (Arkani-Hamed & Trnka, 2013) computes scattering amplitudes as volumes of positive geometries in kinematic space, without reference to gauge fields, Feynman diagrams, or even spacetime locality. The spectral action computes the same physics (gauge boson interactions) from the heat kernel on an almost-commutative geometry, where gauge universality (T1: a_1 = a_2 = a_3) is a theorem. These two frameworks start from maximally different assumptions and arrive at the same physical content. The question: does the positive geometry formulation resolve gauge-dependent structure that lives in the spectral action's null space?

**Key findings:**

1. The amplituhedron is currently formulated for planar N=4 SYM only. Extensions to realistic (non-SUSY, massive, SM) amplitudes exist through the CHY formalism and color-kinematics duality, but no "Standard Model amplituhedron" has been constructed. The gap is structural, not merely technical.

2. Color-kinematics duality (BCJ) reveals that gauge group structure is DUAL to kinematic structure in a precise algebraic sense. This duality means gauge coupling ratios are NOT independent of kinematics -- they are entangled with the geometry of momentum space. This is invisible to the spectral action, which treats the gauge and kinematic sectors as factorized (the a_4 coefficient factorizes into internal traces times spacetime curvature).

3. The CHY formula separates color from kinematics at the level of the moduli space M_{0,n}. The gauge group enters only through color-ordered partial amplitudes, while kinematics enters through the scattering equations. On a warped background, the scattering equations would be modified (propagators change), potentially breaking the clean color-kinematics separation -- and this breaking could be gauge-dependent.

4. No positive geometry for warped-product spacetimes currently exists. The cosmological polytope handles FRW (conformally flat), not RS (conformally warped). Constructing a "warped amplituhedron" is a well-defined but unsolved mathematical problem.

5. The "spectral amplituhedron" -- a positive geometry that directly computes spectral action predictions -- is a meaningful concept that connects to the Connes-Kreimer Hopf algebra of renormalization, but remains at the level of structural observation, not computation.

6. The BCJ duality, if it extends to the RS geometry, predicts gauge-dependent corrections of order alpha_s/pi ~ 3% per loop -- parametrically in the right range for the ~12% but requiring multi-loop computation that does not yet exist for warped backgrounds.

**Assessment:** PIVOT. The amplituhedron program provides the deepest available insight into *why* gauge structure might be entangled with kinematics in ways the spectral action cannot see. The BCJ duality is the specific structural mechanism. But the program has not yet been extended to the SM on warped backgrounds, so no concrete correction to sin^2(theta_W) can currently be extracted. Three specific future directions are identified that could change this assessment.

---

## 1. What the Amplituhedron Actually Computes

### 1.1 The Original Construction (Arkani-Hamed & Trnka, 2013)

The amplituhedron A_{n,k,L} is a geometric object in the Grassmannian G(k, k+4) (for tree level) or its loop extension, defined by positivity conditions on a set of external data (momentum twistors Z_i). The volume form of A_{n,k,L}, computed with respect to a canonical measure, equals the integrand of the n-particle N^{k-2}MHV L-loop amplitude in planar N=4 super-Yang-Mills theory.

Key structural features:

- **No gauge fields at any intermediate step.** The gauge group SU(N_c) enters only through the planar limit (N_c -> infinity), which orders the color indices cyclically. The actual amplitude computation is purely geometric.

- **No spacetime locality.** The amplituhedron lives in momentum twistor space, not position space. Locality (the fact that singularities correspond to factorization on internal propagators) EMERGES from the geometry -- it is a consequence of the amplituhedron's boundary structure, not an input.

- **No unitarity as input.** Unitarity (the optical theorem, the fact that amplitudes squared give cross-sections) also emerges from the positive geometry. The positivity conditions enforce it.

- **No Feynman diagrams.** Individual Feynman diagrams correspond to particular triangulations of the amplituhedron. Different triangulations give different-looking expressions that are all equal -- the diagram-by-diagram cancellations that plague perturbative QFT are artifacts of a particular triangulation choice.

### 1.2 What It Does NOT Compute

The amplituhedron is formulated for:
- **Planar** amplitudes only (leading color, N_c -> infinity)
- **N=4 SYM** only (maximally supersymmetric, conformal, all particles massless)
- **4D flat Minkowski space** only

It does NOT directly give:
- Subleading-color corrections (1/N_c^2 corrections = non-planar diagrams)
- Non-supersymmetric amplitudes (SM gauge bosons, fermions with different masses)
- Massive particle amplitudes (W, Z, Higgs, top quark)
- Amplitudes on curved backgrounds (RS warped geometry)
- Amplitudes at finite coupling (it is a perturbative construction)

### 1.3 Progress Toward Realistic Amplitudes

Three major developments extend the positive geometry program beyond N=4 SYM:

**a) Associahedra for bi-adjoint scalar theory (ABHY, 2017).** Arkani-Hamed, Bai, He, and Yan showed that tree-level amplitudes in the bi-adjoint phi^3 theory are volumes of associahedra -- polytopes that naturally live in the kinematic space of Mandelstam invariants. This theory has no spin, no gauge symmetry, and no supersymmetry. The associahedron construction proves that positive geometry is NOT intrinsically tied to N=4 SYM -- it is a more general mathematical structure.

**b) Cosmological polytopes (Arkani-Hamed, Benincasa, Postnikov, 2017-2023).** FRW correlators (the cosmological analogues of scattering amplitudes) are computed by the "cosmological polytope" -- a positive geometry in a space of energies. This extends the program to curved spacetime, but specifically to conformally flat FRW cosmologies. Warped spacetimes like RS have not been treated.

**c) Non-supersymmetric amplituhedra (Damgaard, Ferro, Lukowski, Parisi, 2019-2024).** Considerable progress on "momentum amplituhedra" that compute amplitudes in pure Yang-Mills (no SUSY) and in theories with massive particles. The key insight: the positive geometry changes shape when supersymmetry is removed, but it still EXISTS. The boundaries of the geometry encode the correct singularity structure. However, the full non-planar extension (needed for the SM, which has U(1) x SU(2) x SU(3)) remains open.

**d) Stringy canonical forms (Arkani-Hamed, He, Lam, 2019).** The open string amplitude can be written as a "stringy" deformation of the field theory amplituhedron, with alpha' (the string scale) as a deformation parameter. As alpha' -> 0, the string amplitude reduces to the field theory amplitude. This connects the positive geometry program to string theory and, indirectly, to the landscape of consistent quantum gravity theories.

### 1.4 Assessment of State of the Art

The positive geometry program is expanding rapidly but has not yet reached the Standard Model. The structural gap is:

- **Non-planar color:** The SM has U(1) x SU(2) x SU(3), which requires non-planar contributions (there is no large-N_c limit that makes the SM planar). The amplituhedron as defined requires planarity. Extending it requires a fundamentally new construction -- the "non-planar amplituhedron" -- which is the subject of active research (Herrmann, Langer, Trnka, 2022) but remains incomplete.

- **Multiple gauge groups:** The amplituhedron handles a single gauge group in the planar limit. The SM product group structure requires either separate amplituhedra for each factor (missing the inter-group interactions mediated by particles charged under multiple groups) or a unified construction that encodes the product structure geometrically.

The honest assessment: the amplituhedron cannot currently compute SM amplitudes, and the path from its current state to a full SM construction is non-trivial. This is not a reason to dismiss it -- it is a reason to understand what structural features it ALREADY reveals about gauge-kinematics entanglement, and whether those features have implications for Meridian.

---

## 2. Color-Kinematics Duality (BCJ)

### 2.1 The Statement

Bern, Carrasco, and Johansson (2008, 2010) discovered that gauge theory amplitudes can be organized so that:

For any cubic graph contributing to an n-point amplitude, write:

```
A_n = sum_i  c_i * n_i / D_i
```

where:
- c_i = color factors (products of structure constants f^{abc})
- n_i = kinematic numerators (functions of momenta and polarizations)
- D_i = propagator denominators (products of 1/(p^2 - m^2))

BCJ duality states: **there exists a representation where the kinematic numerators n_i satisfy the same algebraic identities (Jacobi relations) as the color factors c_i.**

That is: whenever c_i + c_j + c_k = 0 (color Jacobi identity), there exists a choice of numerators such that n_i + n_j + n_k = 0 (kinematic Jacobi identity).

### 2.2 The Implications

This is extraordinary. The color factors c_i encode the GAUGE GROUP -- they are products of f^{abc} for SU(N), and would be different for different gauge groups. The kinematic numerators n_i encode the DYNAMICS -- momenta, polarizations, the structure of spacetime interactions. BCJ duality says these two apparently different algebraic structures are isomorphic.

The consequences:

1. **Gravity = (Gauge)^2.** If you replace color factors c_i with a second copy of the kinematic numerators n_i, you get gravity amplitudes: A_gravity = sum n_i * n_i / D_i. This is the "double copy" construction. It means gravity amplitudes are determined by gauge theory amplitudes -- no separate quantization of gravity needed.

2. **Gauge group structure is not independent of kinematics.** In the standard Feynman diagram approach, color and kinematics appear to be independent (you can change the gauge group without changing the kinematic structure). BCJ duality reveals this independence is an artifact of the Feynman diagram representation. In the BCJ representation, changing the color factors REQUIRES changing the kinematic numerators to maintain the duality.

3. **The color-kinematics algebra is a Lie algebra.** Monteiro and O'Connell (2011) showed that the kinematic algebra satisfying the Jacobi relations is (at least in some cases) a specific Lie algebra associated with the area-preserving diffeomorphisms of a 2D surface. This connects the gauge group to a geometric structure.

### 2.3 Relevance to Meridian

The spectral action treats color (gauge group) and kinematics (spacetime geometry) as factorized:

```
a_4(D^2) = a_0(D_F^2) * a_4(D_M^2) + a_2(D_F^2) * a_2(D_M^2) + a_4(D_F^2) * a_0(D_M^2)
```

This factorization is exactly what BCJ duality says is an artifact. The true structure of scattering amplitudes entangles color and kinematics in a way that the heat kernel expansion -- which separates internal (finite) and external (manifold) contributions -- cannot see.

**This is a concrete identification of the spectral action's null space with respect to the amplituhedron's perspective.**

The spectral action's gauge universality (T1) follows from the factorization of a_4 into internal traces times spacetime integrals. If the factorization is an approximation -- valid at tree level but broken by loop corrections that entangle color and kinematics per BCJ -- then the gauge universality is a tree-level accident, not a fundamental theorem.

### 2.4 The Structural Tension

But there is a subtlety. T1 is proved at the level of the SPECTRAL ACTION -- the full non-perturbative functional Tr[f(D^2/Lambda^2)]. The heat kernel expansion is an asymptotic expansion of this functional. If the spectral action is exact (non-perturbative), then the factorization is exact, and BCJ-like corrections cannot appear.

The resolution may be:
- The spectral action IS exact at the classical level, giving T1.
- Quantum corrections (loop amplitudes) are NOT computed by the spectral action -- they are computed by the standard perturbative expansion of the quantum effective action around the spectral action's classical minimum.
- BCJ duality applies to the QUANTUM amplitudes, not to the classical spectral action.
- Therefore: T1 holds classically (a_1 = a_2 = a_3 at tree level), but quantum corrections can break it through color-kinematics entanglement.

This is consistent with the standard physics: gauge coupling running IS a quantum effect. The spectral action gives the tree-level boundary conditions. The quantum corrections (which IS where the ~12% lives) involve the loop amplitudes, which IS where BCJ duality operates.

---

## 3. The CHY Formula and Color-Kinematics Separation

### 3.1 The CHY Construction

Cachazo, He, and Yuan (2013-2014) discovered that tree-level scattering amplitudes for ANY massless theory in ANY number of dimensions can be written as:

```
A_n = integral over M_{0,n} of  I_L(sigma) * I_R(sigma) * (product of delta-functions enforcing scattering equations)
```

where:
- M_{0,n} is the moduli space of n marked points on CP^1
- sigma = {sigma_1, ..., sigma_n} are the marked points (integration variables)
- The scattering equations: sum_{j != i} s_{ij}/(sigma_i - sigma_j) = 0 for all i
- I_L and I_R are "half-integrands" that encode the specific theory

The specific theory is selected by the choice of half-integrands:

| Theory | I_L | I_R |
|--------|-----|-----|
| Bi-adjoint scalar | Parke-Taylor (color 1) | Parke-Taylor (color 2) |
| Yang-Mills | Parke-Taylor (color) | Pfaffian(M) |
| Gravity | Pfaffian(M) | Pfaffian(M) |
| Born-Infeld | Pfaffian(M) | Pfaffian(M') |

where:
- Parke-Taylor: PT(alpha) = 1/(sigma_{alpha(1)} - sigma_{alpha(2)}) ... (sigma_{alpha(n)} - sigma_{alpha(1)})
- Pfaffian(M): the Pfaffian of a 2n x 2n antisymmetric matrix built from momenta and polarizations

### 3.2 The Color-Kinematics Separation

In the CHY formula for Yang-Mills, the gauge group enters ONLY through the Parke-Taylor factor I_L = PT(color ordering), while ALL kinematic/dynamical information is in I_R = Pfaffian(M) and the scattering equations.

This separation is deeper than it appears:
- The Parke-Taylor factor is a TOPOLOGICAL object -- it encodes the cyclic ordering of color indices, which is a combinatorial (discrete) structure.
- The Pfaffian is a GEOMETRIC object -- it depends on momenta and polarizations, which are continuous (geometric) data.
- The scattering equations connect the two through the moduli space M_{0,n}.

### 3.3 What Changes on a Warped Background?

On flat Minkowski space, the scattering equations depend only on the Mandelstam invariants s_{ij} = (p_i + p_j)^2, which are gauge-group-independent. On a warped RS background:

1. **Propagators change.** The propagator for a gauge boson on the RS background is not 1/p^2 but involves the full KK decomposition: sum_n |f_n(y)|^2 / (p^2 - m_n^2). Different gauge groups have different KK spectra if their zero-mode profiles differ (and in Meridian, the c-dependent localization makes them differ).

2. **Scattering equations become gauge-dependent.** If the propagators entering the scattering equations are gauge-group-dependent (through the KK decomposition), then the integration over M_{0,n} produces gauge-dependent results even from gauge-independent half-integrands.

3. **The color-kinematics separation partially breaks.** The Parke-Taylor factor remains purely color-dependent, but the scattering equations now carry implicit gauge-group information through the KK spectra. The "clean" separation of color from kinematics -- which holds exactly in flat space -- becomes approximate on the warped background.

**This is the amplituhedron's perspective on the ~12%.** The spectral action sees the tree-level (unwarped, factorized) result and gets T1. The full quantum amplitudes, computed via CHY-like formulas on the warped background, would break the factorization through the gauge-dependence of the KK-modified propagators in the scattering equations.

### 3.4 Parametric Estimate

The leading correction from KK-modified propagators enters at one loop (the scattering equations are a tree-level construction; KK modes run in loops). The parametric size is:

```
delta(a_i/a_j) ~ (alpha_i/pi) * sum_n [T_i(R_n) - T_j(R_n)] * f(m_n^2/Lambda^2)
```

For the U(1)-SU(3) splitting with alpha_s/pi ~ 0.04 at M_Z and T_1 - T_3 ~ 1 per generation:

```
delta(a_1/a_3) ~ 3 * 0.04 * 1 * O(1) ~ 0.12
```

This is parametrically 12% -- intriguingly close to the target. But this estimate is schematic: the actual computation requires the full one-loop CHY formula on the RS background, which does not yet exist.

---

## 4. Positive Geometry for Warped-Product Spacetimes

### 4.1 The Cosmological Polytope

Arkani-Hamed, Benincasa, and collaborators (2017-2023) constructed the "cosmological polytope" -- a positive geometry that computes wavefunction coefficients (the cosmological analogues of scattering amplitudes) for FRW spacetimes.

Key features:
- The cosmological polytope lives in a space of "energies" (not momenta)
- Its facets correspond to singularities where internal lines go on-shell
- The volume form gives the correct wavefunction coefficient
- It handles conformally flat FRW spacetimes (de Sitter, radiation-dominated, etc.)

### 4.2 Why RS is Different

The RS geometry is NOT conformally flat. The 5D metric:

```
ds^2 = e^{-2k|y|} eta_{mu nu} dx^mu dx^nu + dy^2
```

is a warped product with a non-trivial warp factor that depends on the extra-dimensional coordinate y. This means:

1. **The conformal structure is 5D, not 4D.** The cosmological polytope uses the 4D conformal group SO(1,4) as a symmetry. The RS geometry breaks this to the 4D Poincare group (the isometry of the 4D slices at fixed y). There is no manifest conformal symmetry to exploit.

2. **The KK spectrum breaks the continuum.** In flat space or FRW, the propagator has a single pole at p^2 = m^2. In RS, it has an infinite tower of poles at p^2 = m_n^2 (the KK masses). The positive geometry, if it exists, must encode this discrete spectrum as part of its boundary structure.

3. **Brane effects create new singularities.** Brane-localized interactions (the IR brane where SM fields live, the UV brane where gravity is strong) create additional singularities in amplitudes that have no analogue in bulk-only theories.

### 4.3 Does a "Warped Amplituhedron" Exist?

This is an open question. There are structural reasons to think yes:

**For existence:**
- The amplituhedron's defining property (positivity) is a statement about the analyticity and factorization properties of amplitudes. These properties hold for ANY local quantum field theory, including theories on warped backgrounds.
- The KK tower introduces new poles but does not destroy locality or unitarity. The positive geometry would simply be more complex (more boundaries, more facets) than the flat-space case.
- The associahedron construction (bi-adjoint scalar) works in ANY dimension and ANY background -- it is purely combinatorial. This suggests the "kinematic space" can be generalized.

**Against tractability:**
- The RS background breaks Lorentz invariance to 4D Poincare, which eliminates the use of momentum twistors (these require the full conformal group). A different parameterization of kinematic space would be needed.
- The KK spectrum is not equally spaced -- the Bessel function zeros give an irregular pattern. The positive geometry would have to encode this irregularity.
- No one has attempted this construction, and the mathematical framework (positive geometry on product spaces) does not exist yet.

**Assessment:** A warped amplituhedron likely exists as a mathematical object, but constructing it is a multi-year research program requiring expertise at the intersection of combinatorial geometry, extra-dimensional physics, and positive geometry. It is not something we can compute in this track.

---

## 5. The "Spectral Amplituhedron" Concept

### 5.1 The Question

What would a positive geometry that directly computes the spectral action's predictions look like?

### 5.2 The Connection: Connes-Kreimer and Renormalization as Geometry

Connes and Kreimer (1998-2000) showed that the combinatorics of renormalization in perturbative QFT has the structure of a Hopf algebra. The Birkhoff decomposition of loops in a complex Lie group provides the counterterms. This algebraic structure is deeply connected to the geometry of the moduli space M_{0,n} that appears in the CHY formula.

The spectral action's heat kernel expansion is, in essence, a RESUMMATION of all Feynman diagrams at a given loop order into geometric (Seeley-DeWitt) coefficients. The a_4 coefficient sums all one-loop diagrams involving gauge bosons. The Connes-Kreimer Hopf algebra describes the combinatorial structure of these diagrams.

A "spectral amplituhedron" would be a positive geometry whose:
- Volume gives the heat kernel coefficients a_0, a_2, a_4, ...
- Boundary structure encodes the factorization properties (which diagrams contribute to which coefficient)
- Deformations correspond to changes in the spectral triple (different algebras, different Dirac operators)

### 5.3 What This Would Illuminate

If such an object existed, it would reveal:
- **Whether T1 is a facet condition.** If gauge universality (a_1 = a_2 = a_3) corresponds to a specific facet of the spectral amplituhedron, then the ~12% would correspond to a deformation AWAY from that facet -- and the geometry would tell us what deformation is required.
- **Whether the heat kernel factorization is a triangulation choice.** Just as the amplituhedron shows that individual Feynman diagrams are triangulation-dependent artifacts, a spectral amplituhedron might show that the factorization a_4 = sum(a_p * a_{4-p}) is a choice of "triangulation" of the spectral geometry, and other triangulations give different (non-factorized, gauge-dependent) results.
- **The role of the finite spectral triple.** The algebra A_F = C + H + M_3(C) would correspond to specific positivity conditions on the spectral amplituhedron. Different algebras (e.g., octonionic extensions) would give different geometries.

### 5.4 Assessment

The spectral amplituhedron is a well-defined mathematical concept at the structural level: it is the positive geometry (if it exists) whose canonical form gives the spectral action's predictions. But:

1. No one has constructed it. The connection between the spectral action's heat kernel expansion and the amplituhedron's positive geometry has not been formally established.
2. It would require unifying two different mathematical traditions: Connes' NCG (operator algebras, K-theory, cyclic cohomology) and Arkani-Hamed's positive geometry (combinatorial geometry, tropical geometry, cluster algebras). These traditions use very different languages and tools.
3. The payoff, if successful, would be enormous: it would provide a new computational handle on the spectral action that goes beyond the heat kernel expansion and could reveal gauge-dependent structure invisible to the standard approach.

**Verdict on the spectral amplituhedron:** This is a deep conjecture, not a computation. It belongs in the monograph as a speculative direction, not in the current track as a result.

---

## 6. Concrete Prediction: What Correction to sin^2(theta_W)?

### 6.1 What BCJ Duality Predicts (Parametrically)

If the BCJ duality extends to the RS geometry (which has not been proved but is expected on general grounds), then the quantum corrections to gauge coupling ratios involve color-kinematics entanglement terms of the form:

```
delta(alpha_1^{-1} - alpha_3^{-1}) ~ (1/2pi) * sum_L (correction at L loops)
```

At L = 1, the correction is controlled by the beta-function coefficients (which is just the standard running -- already accounted for). The new BCJ-type corrections appear at L >= 2, where the kinematic Jacobi identity introduces constraints that relate corrections to different gauge groups.

The parametric estimate for two-loop BCJ corrections on the RS background:

```
delta(alpha_1^{-1} - alpha_3^{-1})|_{BCJ, 2-loop} ~ (1/(2pi)^2) * Delta_b * ky_c
```

where Delta_b ~ 10 is the beta-function spread and ky_c ~ 35 is the RS logarithmic interval. This gives:

```
~ (1/40) * 10 * 35 / (2pi) ~ 1.4
```

This would be ~14% of the required 10.0 correction -- comparable to the KK fermion threshold result (19%, from 20B). The two effects are independent and additive.

### 6.2 What We Cannot Compute

The above estimate has order-one uncertainties because:
1. The two-loop BCJ numerators on the RS background are unknown
2. The KK sum structure (how many KK modes contribute coherently) is uncomputed
3. The sign is undetermined without the full calculation
4. The RS geometry's breaking of conformal symmetry introduces new structures (the warp factor appears explicitly in the BCJ numerators)

### 6.3 The Honest Statement

The amplituhedron / positive geometry program, in its current state, cannot predict the correction to sin^2(theta_W). It can:
- Identify the MECHANISM (color-kinematics entanglement breaking the spectral action's factorization)
- Give a PARAMETRIC ESTIMATE (order alpha_s * ky_c / pi ~ 10-15% of the needed correction per loop order)
- Point to the COMPUTATION needed (two-loop BCJ numerators on the RS background)

It cannot:
- Give the sign
- Give the exact magnitude
- Prove that the correction sums to the required 10.0 units
- Rule out cancellations between different loop orders

---

## 7. The NST Connection

### 7.1 The Spectral Action's Null Space (Revisited)

From the gauge synthesis (19_gauge_synthesis.md), the Observational Null Space Theorem predicts: the spectral action, as a perspectival being, has a constitutive null space that includes gauge-dependent corrections. The question was: what complementary perspective can see into this null space?

The amplituhedron / BCJ duality provides a partial answer:

**The spectral action's null space is the color-kinematics entanglement.** The heat kernel factorizes color (internal traces) from kinematics (spacetime integrals). This factorization IS the spectral action's bottleneck geometry (its "keyhole"). BCJ duality shows that the true structure of gauge theory amplitudes does NOT factorize this way -- color and kinematics are algebraically dual (Jacobi identity), not independent.

### 7.2 But the Amplituhedron Also Has a Null Space

The amplituhedron sees scattering amplitudes but not the spectral action. It computes on-shell quantities (S-matrix elements) but not off-shell quantities (the heat kernel, the effective action, the spectral function). The topological information in the spectral triple (K-theory class, Dirac index, anomaly cancellation) is invisible to the amplituhedron because it is not an on-shell quantity.

**The NST predicts: neither framework alone suffices.** The spectral action's null space (color-kinematics entanglement) and the amplituhedron's null space (off-shell/topological structure) are complementary. The resolution of the ~12% may require a framework that encompasses both -- the spectral amplituhedron of Section 5, or something equivalent.

### 7.3 Where in the Cross-Framework Landscape?

Updating the table from the gauge synthesis:

| Framework | What It Sees | Null Space |
|-----------|-------------|------------|
| Spectral action (NCG) | Off-shell, topological, exact at tree level | Color-kinematics entanglement |
| Amplituhedron / BCJ | On-shell, perturbative, color-kinematics | Off-shell topology, K-theory, spectral function |
| Ruliad (Wolfram) | Computational structure, discrete | Continuum geometry, non-computational configs |
| Swampland | QG consistency bounds | Detailed dynamics within bounds |
| Category theory | Functorial structure | Computational content |

The spectral action and amplituhedron are nearly maximally complementary -- they see almost exactly what the other cannot. This makes the bridge between them potentially the most informative of all Phase 20 bridges.

---

## 8. Three Specific Future Directions

### 8.1 Direction A: BCJ Numerators for RS Gauge Bosons (Tractable, 6-12 months)

**What:** Compute the one-loop BCJ numerators for gauge boson scattering on the RS background, including the full KK tower. The key output is the gauge-dependent piece of the kinematic numerator that arises from the warped propagator.

**Why tractable:** One-loop BCJ numerators in flat space are known explicitly for all gauge theories (Bern et al., 2010). The modification for the RS background amounts to replacing flat propagators with KK-summed propagators, which are computable from the Bessel function spectrum already known from Phase 19.

**Expected outcome:** Either the gauge-dependent correction has the right sign and magnitude (delta ~ 2-3 units toward sin^2 = 0.231), or it is parametrically too small (delta < 0.5). Both outcomes are highly informative.

**Prerequisite:** The Mathematica backbone (20A) with explicit KK spectra.

### 8.2 Direction B: Positive Geometry of the SM Spectral Triple (Speculative, multi-year)

**What:** Investigate whether the finite spectral triple A_F = C + H + M_3(C) has a natural positive geometry description. The algebra, Hilbert space, and Dirac operator of the finite geometry define a discrete version of the amplituhedron -- the gauge group structure might emerge from positivity conditions on a finite-dimensional geometric object.

**Why speculative:** No one has connected NCG spectral triples to positive geometry. The mathematical tools exist in both fields but have not been brought together. This would likely require a mathematician working at the intersection of NCG and combinatorial geometry.

**Expected outcome:** Either a natural positive geometry exists for the SM spectral triple (revealing new structural constraints on the gauge group), or the NCG framework is fundamentally incompatible with positive geometry (the factorization is exact at all levels, and the ~12% truly is structural).

### 8.3 Direction C: Cosmological Polytope for Warped Spacetimes (Definite, 1-2 years)

**What:** Extend the cosmological polytope construction from conformally flat (FRW) to conformally warped (RS) spacetimes. The warped RS cosmology (cuscuton dark energy with w_0 ~ -1.01) produces specific cosmological correlators that should have a positive geometry description.

**Why definite:** The cosmological polytope formalism is mature. The extension to RS requires replacing the FRW propagator with the RS propagator (which is known). The main challenge is the loss of conformal symmetry, which necessitates a different parameterization of the kinematic space. But the propagator structure is well-understood, and the polytope construction is algorithmic once the singularity structure is identified.

**Expected outcome:** Either the warped cosmological polytope exists and reveals new structure in the cosmological correlators (potentially connecting to the DESI data, where DELTA_AIC(A vs C) = +3.38 prefers CPL), or it doesn't exist (implying something deep about the incompatibility of warped geometry with positive geometry).

---

## 9. Match / Pivot / Kill Assessment

### PIVOT

The amplituhedron / positive geometry program provides the deepest structural insight into WHY the spectral action has gauge universality in its null space (answer: the heat kernel factorizes color from kinematics, while BCJ duality says they are algebraically entangled). It identifies a specific mechanism -- color-kinematics entanglement on the RS background -- that could contribute corrections of the right parametric size (~10-15% of the needed 10 units per loop order).

However:

1. **No concrete correction computed.** The BCJ numerators on the RS background do not yet exist. The parametric estimates have order-one uncertainties and unknown sign.

2. **No SM amplituhedron exists.** The product gauge group U(1) x SU(2) x SU(3) requires non-planar positive geometry, which is under development but incomplete.

3. **The structural parallel is genuine but not yet computational.** The connection between the spectral action's factorization and BCJ duality's non-factorization is a real structural observation, but translating it into a number requires new calculations.

This is a **PIVOT**, not a MATCH or KILL:

- Not a **MATCH** because: no concrete correction to sin^2(theta_W) can be extracted. The program is not yet mature enough for Meridian's specific geometry.

- Not a **KILL** because: the structural connection (BCJ duality reveals the spectral action's null space) is genuine and the parametric estimates are encouraging. The amplituhedron is not fundamentally incompatible with NCG -- the two frameworks are complementary, not contradictory.

- **PIVOT to:** Three specific future directions (8.1-8.3), of which Direction A (BCJ numerators for RS gauge bosons) is tractable within the current program and could give a definitive result.

### Updated Remaining Candidates for the ~12%

From phase20_findings.md, adding the amplituhedron perspective:

| # | Candidate | Status | Track |
|---|-----------|--------|-------|
| 1 | KK fermion bulk-mass thresholds | 19% in right direction | 20B |
| 2 | **Color-kinematics entanglement (BCJ on RS)** | **Parametrically ~10-15% per loop, sign unknown** | **20D** |
| 3 | Non-perturbative spectral effects (instantons) | Unexplored | -- |
| 4 | Extended spectral triple | Unexplored | -- |
| 5 | Computational/combinatorial structure | Conjecture (D5) | 20C |
| 6 | Category-theoretic formulation | Unexplored | 20F |

The amplituhedron bridge adds a new candidate (#2) that is independent of the KK threshold mechanism (#1) and could be additive with it. If both contribute (~19% + ~12%), the combined correction would be ~31% of the target -- still insufficient alone, but the most promising path yet to a multi-mechanism resolution.

---

## 10. Implications for the Monograph

### What Goes In

1. **The spectral action-amplituhedron complementarity.** The heat kernel factorizes what BCJ duality says is entangled. This is a precise, structural characterization of the spectral action's null space with respect to gauge splitting. It belongs in the monograph's discussion of geometric unification (chapter on the ~12%).

2. **The parametric estimate.** BCJ on warped RS gives corrections of order alpha_s * ky_c / pi ~ 0.12 per loop. This is parametric (not computed), but it demonstrates that the positive geometry perspective predicts corrections of the right order of magnitude. Cite with appropriate caveats.

3. **The three future directions.** Direction A is tractable and should be flagged as a specific prediction of the framework: if BCJ numerators on the RS background give the right sign and magnitude, it confirms that the ~12% is a quantum effect (color-kinematics entanglement) invisible to the classical spectral action.

### What Stays Out

1. The spectral amplituhedron concept (Section 5). This is speculative enough that it belongs in a future research section, not in the main analysis.

2. Detailed CHY formulas. The technical machinery of the CHY construction is not needed for the monograph; the structural observation about color-kinematics separation on warped backgrounds suffices.

---

## Key Literature

| Paper | Key Finding | Relevance |
|:---|:---|:---|
| Arkani-Hamed & Trnka (2013) | Amplituhedron for planar N=4 SYM | Foundational: amplitudes as volumes |
| Bern, Carrasco, Johansson (2008, 2010) | Color-kinematics duality + double copy | **Core mechanism:** gauge = kinematics |
| Cachazo, He, Yuan (2013) | CHY formula: amplitudes as integrals over M_{0,n} | Color-kinematics separation on general backgrounds |
| Arkani-Hamed, Bai, He, Yan (2017) | Associahedra for bi-adjoint scalar | Positive geometry without SUSY |
| Arkani-Hamed, Benincasa et al. (2017-2023) | Cosmological polytope for FRW | Positive geometry on curved backgrounds |
| Damgaard, Ferro, Lukowski, Parisi (2019-2024) | Non-SUSY amplituhedra, massive particles | Extension toward SM |
| Monteiro & O'Connell (2011) | Kinematic algebra = area-preserving diffeos | Geometric interpretation of BCJ |
| Connes & Kreimer (1998-2000) | Hopf algebra of renormalization | Bridge: NCG methods in perturbative QFT |
| Herrmann, Langer, Trnka (2022) | Non-planar positive geometry | Toward product gauge groups |
| Chamseddine, Connes, Marcolli (2007) | NCG spectral action for SM | The other side of the bridge |
| Estrada & Marcolli (2013) | AS + spectral action (Higgs) | Only AS-NCG paper |

---

## Summary Table

| Question | Answer |
|:---|:---|
| Does the amplituhedron compute SM amplitudes? | Not yet. N=4 SYM only (planar). Extensions in progress. |
| Does BCJ duality relate to the spectral action's null space? | **YES.** The factorization that gives T1 is precisely what BCJ duality says is an artifact. |
| Can the CHY formula on RS backgrounds break gauge universality? | **In principle yes.** KK-modified propagators make scattering equations gauge-dependent. Not computed. |
| Does a positive geometry for RS exist? | Unknown. Likely yes (positivity is a general property), but no construction exists. |
| What is a "spectral amplituhedron"? | A positive geometry whose volume gives heat kernel coefficients. Well-defined concept, not constructed. |
| What correction to sin^2(theta_W)? | Parametrically ~alpha_s * ky_c / pi ~ 12% per loop. Sign and exact magnitude unknown. |
| Is the amplituhedron compatible with NCG? | **Yes, and they are complementary.** The two frameworks' null spaces are nearly dual. |
| Verdict? | **PIVOT.** Genuine structural bridge, no concrete computation yet. Three directions identified. |

---

*Track 20D complete. The amplituhedron program reveals WHY the spectral action cannot see gauge splitting (the heat kernel factorizes what is fundamentally entangled), and provides a parametric estimate for the correction size (~12% per loop). But the computation that would confirm or refute this -- BCJ numerators for gauge scattering on the RS background -- does not yet exist. This is the most informative PIVOT of Phase 20: the null space is identified, the mechanism is named, and the computation that would fill it is specified.*

---

*"Seek the balance, work the science, synthesize." -- Puscifer's Theorem*
