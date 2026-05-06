# Track 21A.4: Resurgence of the Spectral Action — Research Note

**Date:** 2026-03-23 (morning creative drive)
**Status:** Pre-research. Key questions formulated. Computation not yet attempted.

## Why This Track Is Now the Primary Candidate

The overnight eliminations + T12 (morning) have closed the entire perturbative landscape:

| Mechanism | Status | Reason |
|-----------|--------|--------|
| Twisted spectral triples (algebraic) | ELIMINATED | Aut(A_F) preserves all traces |
| KK Schwinger (engineering) | ELIMINATED | Mass^2 barrier: 10^14x too weak |
| Warp-factor cross-terms (geometric) | ELIMINATED by T12 | Volume suppression kills all orders |
| KK threshold corrections | Phase 20B | Representation-universal by spectral triple |
| GUT algebra extension | Phase 20 | ALL GUTs give 3/8 + proton decay |
| AS gravitational corrections | T10 | NCG-AS-beta=0 incompatibility |

**What remains:** The spectral action is defined non-perturbatively as Tr[f(D^2/Lambda^2)].
The heat kernel gives an ASYMPTOTIC expansion. T12 shows this expansion preserves gauge
universality to ALL orders. But asymptotic ≠ exact. The gap between the expansion and the
function is precisely what resurgence can quantify.

## The Central Mathematical Question

**Is the heat kernel expansion of the spectral action Borel-summable?**

If YES: the asymptotic expansion uniquely determines the function. Gauge universality
holds exactly. The 12% cannot come from the spectral action itself.

If NO: the asymptotic expansion has a non-perturbative ambiguity. The ambiguity is
exponentially small (~ e^{-c Lambda^2/m^2} for some mass scale m) and represents
genuine physical information not captured by any finite truncation. The question is
then: IS THIS AMBIGUITY GAUGE-DEPENDENT?

## What We Know About the Heat Kernel Asymptotics

### General theory:
- The heat kernel Tr(e^{-tD^2}) has an asymptotic expansion as t -> 0+
- The Seeley-DeWitt coefficients a_{2n} grow factorially: |a_{2n}| ~ C^n n!
  (This is generic for spectral problems on compact manifolds)
- Factorial growth implies the expansion is divergent (zero radius of convergence)
- By Watson's lemma, it IS an asymptotic expansion of the exact heat trace

### On the RS background specifically:
- The RS orbifold has boundaries (the two branes). Boundary effects modify the
  heat kernel through boundary contributions a_{2n}^{bdy}
- The boundary coefficients have DIFFERENT factorial growth rates than the bulk
  coefficients (Grubb-Seeley asymptotic analysis)
- The orbifold Z_2 identification introduces "image charges" in the heat kernel
  that produce oscillatory corrections

### Key reference: Dunne-Unsal program
- Dunne and Unsal (2014-2021) developed resurgence for quantum mechanics and
  low-dimensional QFT on S^1 x R^3 (similar topology to RS orbifold!)
- Key finding: on S^1 x R^3, the perturbative expansion has non-perturbative
  contributions from "neutral bions" (instanton-anti-instanton pairs)
- The Stokes phenomenon determines which non-perturbative sectors contribute
- The resurgent structure is TOPOLOGICAL: it depends on the topology of the
  compact space (S^1 in their case, S^1/Z_2 in ours)

## The Specific Computation Needed

### Step 1: Large-order behavior of a_{2n} on RS

Compute the Seeley-DeWitt coefficients a_{2n} for the Dirac operator on the RS
background up to n ~ 10-20. This can be done:
(a) Recursively using the Greiner-Dunne recursion relations for heat kernel coefficients
(b) Numerically using the exact spectrum of D on the RS orbifold

The large-order behavior determines the location and nature of the singularities
in the Borel transform.

### Step 2: Borel transform analysis

The Borel transform B(s) = sum_n a_{2n}/(n!) s^n should have finite radius of
convergence (the expansion is asymptotic but the Borel transform might converge).

Singularities of B(s):
- On the positive real axis: Borel-summability is BROKEN (non-perturbative ambiguity)
- Off the positive real axis: Borel-summable but with lateral Borel resummation

The positions of singularities correspond to non-perturbative actions:
s_k = S_k / Lambda^2 where S_k is the action of the k-th saddle point.

### Step 3: Gauge dependence of the non-perturbative ambiguity

If B(s) has singularities on the positive real axis, the ambiguity in the Borel
resummation is:

  Im[S_Borel] ~ e^{-S_k/Lambda^2} x (pre-exponential factors)

The pre-exponential factors involve the fluctuation determinant around the k-th
saddle point. In gauge theory, this determinant depends on the gauge group through
the second Casimir C_2(G_i).

**This is where gauge dependence enters.** Even if the perturbative expansion is
gauge-universal (T12), the non-perturbative ambiguity can be gauge-dependent through
the fluctuation determinant.

## Predictions

### PREDICT (medium confidence): Non-Borel-summability
The RS orbifold, like S^1 x R^3 in the Dunne-Unsal program, should have Borel
singularities on the positive real axis due to neutral bion contributions. The
Z_2 orbifold actually ENHANCES the non-perturbative effects compared to pure S^1
because the orbifold projection removes certain cancellations between bions.

### PREDICT (low confidence): Gauge-dependent ambiguity at the percent level
If the ambiguity is ~ e^{-S_bion} x C_2(G_i), then the gauge dependence is at
the level of (C_2(SU(3)) - C_2(SU(2))) / C_2(SU(3)) = (4/3 - 3/4) / (4/3) = 7/16 = 0.4375.

Interesting: 7/16 ≈ 0.44 is close to sin^2(theta_W)(Lambda) = 0.436! This is
probably a coincidence, but it suggests the gauge dependence enters through Casimir
ratios, which are of the right magnitude to produce a percent-level correction.

### PREDICT (high confidence): Factorially divergent coefficients
The heat kernel coefficients on the RS background should grow as |a_{2n}| ~ C^n n!.
This is generic and would be surprising if violated.

## Pre-work for Phase 21 Computation

What's needed before the full computation:

1. **Exact spectrum of D on RS:** The eigenvalues m_n of the Dirac operator on
   the RS orbifold with A_F matter content. This determines the exact heat trace
   Tr(e^{-tD^2}) = sum_n e^{-t m_n^2}. We have this from Phase 18 (the KK spectrum).

2. **High-order Seeley-DeWitt coefficients:** Recursive computation of a_{2n} for
   n up to 10-20. Can be done in Mathematica using the Greiner-Dunne recursion.

3. **Borel plane analysis:** Standard numerical technique: Pade approximants of the
   Borel transform, conformal mapping, Richardson extrapolation.

4. **Dunne-Unsal framework adaptation:** Their S^1 x R^3 analysis needs to be
   modified for S^1/Z_2 (orbifold) with a warped metric. The key difference:
   the orbifold removes half the bion spectrum.

## Connection to ln(N_c)/sqrt(N_w)

The symbolic regression found that a_1/a_2 ≈ ln(3)/sqrt(2) to 0.08%.

In the resurgence framework, logarithms of group dimensions arise naturally from
one-loop fluctuation determinants around non-perturbative saddles:

  det(D^2 + m^2)_{adj} ~ (Lambda/m)^{dim(G)} -> ln[det] ~ dim(G) ln(Lambda/m)

If the non-perturbative correction involves the ratio of fluctuation determinants
for different gauge groups, the result would be:

  delta(1/alpha_i) ~ ln(dim(G_i)) x (some function of bion action)

This gives:
  delta(1/alpha_3)/delta(1/alpha_2) = ln(8)/ln(3) = 1.893 (for adjoint)
  or ln(3)/ln(2) = 1.585 (for fundamental, using N_c, N_w)

The ratio a_1/a_2 from such a correction would involve ln(N_c)/ln(N_w) or similar.
The symbolic regression hit ln(N_c)/sqrt(N_w) = ln(3)/sqrt(2) could arise if the
SU(2) determinant enters through a half-power (square root) rather than logarithm.

This is speculative but concrete enough to test once the Borel analysis is done.

## Assessment

This is the most promising remaining track. T12 closed the perturbative landscape;
resurgence is the systematic tool for what lies beyond. The Dunne-Unsal program
provides a tested framework for similar topologies. The computation is tractable
(Mathematica + numerical Pade/conformal mapping).

The key question — Borel-summability of the RS spectral action — has never been
asked in the literature. We would be the first.
