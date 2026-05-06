# Track 13M: Warped 5D Asymptotic Safety — Framework Complete

**Date:** March 17, 2026
**Status:** Mathematical framework established. Computation strategy defined. No existing literature.
**Full document:** `phase13/13M_warped_5D_asymptotic_safety.md` (884 lines)

---

## Literature Gap Confirmed

No existing paper computes functional renormalization group (FRG) beta functions on a warped Randall-Sundrum background. Six closest results identified — none cover this case.

## Curvature Corrections (Important for Monograph)

Input values in the original prompt were incorrect. Corrected values for AdS₅:

| Quantity | Claimed | Correct | Note |
|----------|---------|---------|------|
| R₅ | −20k² | −20k² | ✓ Correct |
| R_MN R^MN | 20k⁴ | **80k⁴** | Was using R_MN = −2k²g_MN instead of −4k²g_MN |
| G_GB | 40k⁴ | **120k⁴** | Follows from corrected R_MN² |
| C_MNPQ² | ~8k⁴/3 | **0** | Weyl tensor vanishes on ANY maximally symmetric space |

**These corrections may propagate into the monograph.** Need to check Paper I.

## Key Physics: Dimensional Crossover

The central new result is the structure of the RG flow on the RS background:

- **Below** k_cross ~ πk·e^{−ky_c}: only the graviton zero mode contributes. Flow is **4D Reuter** — standard AS with G₄ and Λ₄.
- **Above** k_cross: KK tower activates. Each mode n contributes a threshold function shifted by m_n²/k². The sum transitions to **5D scaling** (k⁵ instead of k⁴).
- The KK tower enters the Wetterich equation as: β_G = β_G^(4D) + Σ_n [threshold corrections from mode n]

This crossover is the RS-specific signature in the AS flow. It doesn't exist in flat extra dimensions (where all KK modes have equal spacing).

## Heat Kernel on RS Orbifold

Full Seeley-DeWitt expansion computed for both:
- **Bulk:** a₀, a₂, a₄ evaluated on AdS₅ background for TT gravitons
- **Boundary:** a_{1/2}, a₁, a_{3/2} for Neumann BCs at both branes (Israel JCs reduce to Neumann for RS fine-tuned case)

## Feasibility Assessment

| Truncation | Difficulty | Tractable? |
|------------|-----------|------------|
| Einstein-Hilbert (G, Λ) | Medium | Yes — standard Wetterich + KK sum |
| Higher-derivative (R², Ric², Riem²) | Hard | Doable with care |
| Full (+ brane tensions) | Very hard | Research-grade computation |

### Five Technical Obstacles
1. KK sum convergence (infinite tower, needs regularization)
2. Boundary flow contributions (brane-localized terms)
3. Background self-consistency (RS is on-shell only for fine-tuned brane tensions)
4. Brane tension running (σ_UV, σ_IR flow with k)
5. Regulator definition on warped geometry (non-standard Laplacian)

### Recommended Four-Phase Strategy
1. EH truncation with finite KK sum (first N modes)
2. Extrapolate N → ∞, identify dimensional crossover
3. Add R² terms, compute GB coefficient at 5D fixed point
4. Include brane tension running

## Implications for Meridian

1. **Dimensional crossover** provides a physical mechanism for the 4D EFT: below the KK scale, the theory IS 4D with specific effective couplings determined by the KK tower
2. **Track 13N** (GB from AS) can proceed once the Phase 1-2 of the computation strategy is done
3. **The warp factor enters the beta functions** through the KK mass spectrum m_n = x_n k e^{−ky_c} — the hierarchy between k and the IR scale is physical and affects the flow

## Supporting Files
- `phase13/13M_warped_5D_asymptotic_safety.md` — Full 884-line framework
- `phase13/omega2_computation.py` — Connection curvature traces
- `phase13/verify_a4.py` — Curvature invariant verification

---

*This is the mathematical foundation for a computation nobody has done. The framework is complete. The computation awaits.*
