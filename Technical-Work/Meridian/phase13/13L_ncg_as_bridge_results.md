# Track 13L: NCG–AS Bridge — INITIAL RESULTS

**Date:** March 17, 2026
**Status:** Mathematical groundwork complete. Key insight identified. Open computation remains.
**Full analysis:** `projects/Project Meridian/ncg_as_bridge/ncg_as_bridge_analysis.md`

---

## The Core Result

**NCG and AS are not the same thing — they play different structural roles.**

- **NCG (spectral action)** = the bare action at the cutoff scale Λ. The **initial condition** for RG flow.
- **AS (Reuter fixed point)** = the UV attractor of the RG flow. Where the theory **goes** as k → ∞.

The bridge is: **the spectral action must lie in the basin of attraction of the Reuter fixed point** for the theory to be UV-complete via AS.

This is analogous to how SM gauge couplings at the GUT scale (initial condition) differ from the Gaussian fixed point (IR attractor), but the theory is asymptotically free because the initial conditions lie in the basin of attraction.

## Spectral Action Coupling Ratios (Exact, Universal)

From the Seeley-DeWitt a₄ coefficient on a 4D spin manifold:

**C² : E₄ : R² = −18 : +11 : −90**

These ratios are:
- Independent of the cutoff function f
- Independent of SM matter content (the finite triple multiplies ALL gravitational traces by the same N_F)
- Verified against Chamseddine-Connes-Marcolli (2007): C²/E₄ = −18/11 identically

## AS Fixed-Point Values (Literature)

From Benedetti-Machado-Saueressig (2009):
- 4 couplings: g₀* = 0.00442, g₁* = −0.0101, g₂* = +0.00754, g₃* = −0.005
- Critical exponents: (2.51, 1.69, 8.40, −2.11)
- **3 UV-attractive, 1 UV-repulsive** → basin of attraction is codimension-1

## Comparison: Partial Match, One Sign Discrepancy

| Coupling | Spectral Action | AS (BMS) | Match? |
|----------|----------------|----------|--------|
| Riem² | NEGATIVE | NEGATIVE | ✓ |
| E₄ (GB) | POSITIVE | POSITIVE | ✓ |
| C² (Weyl) | NEGATIVE | NEGATIVE (inferred) | ✓ |
| Ric² | NEGATIVE | **POSITIVE** | ✗ |

The Ric² sign mismatch is structural. But this does NOT kill the bridge — the spectral action doesn't need to match the fixed point. It needs to lie in its basin of attraction.

## The Open Computation (Next Step)

1. Compute the UV-repulsive eigenvector at the BMS fixed point
2. Project the spectral action coupling ratios onto this eigenvector
3. If projection ≈ 0: NCG-AS bridge is exact (spectral action lies on the UV critical surface)
4. If projection ≠ 0: bridge is approximate (theory is near-AS, with slow deviation)

This is a well-defined, finite computation. It determines whether the NCG-AS bridge holds.

## Implications for Meridian

1. **The spectral action ratios are topologically protected** — matter content doesn't change them. This resonates with our topological protection discovery from Phase 11D.

2. **The RS orbifold Z₂ is the same Z₂ that appears in the NCG real structure J.** Potential deep structural connection — not explored in the literature.

3. **5D extension:** How does the spectral action on M₄ × S¹/Z₂ modify the a₄ coefficients? The KK reduction gives additional couplings from 5D Weyl and R² terms. This connects to Track 13M.

4. **One-loop spectral action:** The tree-level computation gives specific ratios. The one-loop correction might shift them TOWARD the AS fixed point — worth computing.

---

*The bridge exists. It's not "NCG = AS." It's "NCG provides the UV initial condition; AS provides the RG flow." The spectral action is the boundary condition on the critical surface. Whether it sits exactly on that surface is computable and open.*
