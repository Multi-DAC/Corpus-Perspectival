# Tool Landscape for dP5 Computation — Phase 22 Track alpha

**Compiled:** 2026-03-25 (Dream Drive research agent)
**Purpose:** Inform Track alpha.1 implementation

---

## Key Finding: T-Operator Must Be Built From Scratch

No off-the-shelf Donaldson balanced metric implementation exists. The algorithm is conceptually simple but engineering-intensive. SageMath handles the algebraic setup; Python/JAX handles the numerical iteration.

---

## Available Tools

### SageMath (Algebraic Setup)

**Has:**
- Toric variety library: dP6, dP7, dP8 built-in. **dP5 NOT toric** (blowup at >3 points destroys toric structure).
- General scheme operations: intersection theory, Picard group, linear systems, divisor arithmetic.
- Macaulay2 interface: Groebner bases, ideal operations, resolution of singularities.
- Anticanonical embedding: can set up dP5 as V(Q1, Q2) in CP4 via scheme machinery.

**Does NOT have:**
- Built-in dP5 constructor (stops at dP6)
- Numerical differential geometry / Kahler metrics
- T-operator iteration

**WSL2:** Ubuntu 22.04 has SageMath 9.5 (old). Need AppImage 10.7+ or build from source.

### ML-Based Numerical Metric Packages

| Package | Approach | Usable for dP5? |
|---------|----------|-----------------|
| **cymyc** (Justin-Tan, JHEP 2025) | JAX tensor field PDE solving | Most promising. Needs Ricci-flat → KE adaptation. |
| **cymetric** (TensorFlow) | Neural network for CY metrics | CICYs only. Wrong curvature sign. |
| **CYJAX** (JAX) | Donaldson algebraic ansatz | Single hypersurfaces only. |
| **CYTools** (McAllister group) | Topological data | No metric computation. |

### Period Computation

- **Lairez (2016)** — SageMath/Julia implementation. State-of-the-art for hypersurfaces. **Needs adaptation for complete intersections** (dP5 is not a hypersurface).
- **Sertoz (2019)** — Picard-Lefschetz based. Also SageMath.
- SageMath's `dwork_relation()` (Feb 2026) — for hypergeometric functions.

### Already Available in Our Stack

- Python/mpmath: high-precision theta functions (from Track C)
- Wolfram: symbolic algebra, group theory
- numpy/scipy: numerical linear algebra, Monte Carlo

---

## Implementation Path for Track alpha.1

### What SageMath Does (alpha.1.1-1.2):
1. Set up dP5 = V(Q1, Q2) in CP4 algebraically
2. Compute basis of H^0(dP5, -kK) for k = 1,...,5
3. Intersection theory, divisor classes, line computation (16 lines on V(Q1,Q2))

### What We Build (alpha.1.3-1.4):
1. Monte Carlo sampling on V(Q1, Q2) ⊂ CP4
2. T-operator iteration: T_{ab} = integral (s_a s_b* / rho) dV
3. Convergence monitoring, basis updates

### What's Already Done (alpha.1.6):
1. High-precision theta function evaluation (mpmath, from Track C)
2. Comparison with ln(3)/sqrt(2) (from Track C)

### The Hard Gap (alpha.1.5):
Extracting the Wilson line parameter z from the balanced metric. This requires:
- Understanding the spectral cover construction (Friedman-Morgan-Witten)
- Mapping dP5 periods to heterotic Wilson line
- This is the mathematical crux, not the numerical computation

---

## Key References

- Doran, Headrick et al. (2008) — Numerical KE on dP3. **Toric reduction not applicable to dP5.**
- Donaldson (2005) — Foundational T-operator paper. CP1, CP2 demos. No public code.
- Douglas, Karp, Lukic, Reinbacher — Numerical CY metrics via balanced embeddings. No public code.
- cymyc [Justin-Tan/cymyc](https://github.com/Justin-Tan/cymyc) — Best existing codebase to adapt.
- CYTools [LiamMcAllisterGroup/cytools](https://github.com/LiamMcAllisterGroup/cytools) — Topological data.
- Vakil — Explicit equations for M_{0,5} moduli space.
- Lairez [arXiv:1404.5069] — Period computation for hypersurfaces.

---

## Revised Track alpha Assessment

The **numerical** challenge (T-operator iteration) is moderate — we build it ourselves, ~500 lines of Python.
The **mathematical** challenge (spectral cover → Wilson line map) is hard — requires Friedman-Morgan-Witten theory.
The **shortcut** (noted in daily log): the tree-level z = 5/18, and delta_z = -0.0007 is a small one-loop correction. We might be able to compute delta_z perturbatively rather than through the full balanced metric.

*Save this file. Read before Track alpha implementation sessions.*
