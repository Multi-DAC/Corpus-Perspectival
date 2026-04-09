"""
COHERENCE STEP-FUNCTION ANALYSIS
=================================
Clawd, March 26, 2026. Creative drive exploration.

THE QUESTION: Is the step function in S (spectral proximity) REAL?
The claim: 8/9 orbit coherence → S ≈ 0.5 → nothing.
           9/9 orbit coherence → S = 1.0 → signal.

This assumes BINARY coherence: each orbit is either known or unknown.
But the coherence reframe (Clayton, today) says coherence is continuous.

What does S look like when coherence is continuous?
Does the product structure still create an effective step function?

KEY FORMULA:
  For each orbit i, observer has coherence c_i in [0, 1].
  Observer state per orbit: rho_i = c_i |target><target| + (1-c_i)/2 * I
  Per-orbit proximity: S_i = <target|rho_i|target> / Tr(rho_i)
                           = (c_i + (1-c_i)/2) / 1
                           = (1 + c_i) / 2
  Total: S = prod_i S_i = prod_i (1 + c_i) / 2

PREDICTIONS:
  1. CONFIRM: Product structure creates effective step function
     (need c_i > 0.999 in ALL orbits)
  2. FALSIFY: Gradual improvement is possible with partial coherence
  3. NEW: The "weakest link" orbit dominates — interesting for protocol design
"""

import numpy as np


def S_from_coherences(c_vec):
    """Spectral proximity from per-orbit coherence vector.

    c_vec: array of shape (..., 9) with values in [0, 1]
    Returns: S = prod_i (1 + c_i) / 2
    """
    return np.prod((1 + c_vec) / 2, axis=-1)


def main():
    print("=" * 70)
    print("COHERENCE STEP-FUNCTION ANALYSIS")
    print("=" * 70)
    print()

    S_required = 0.994  # from bounce action threshold
    n_orbits = 9

    # =================================================================
    # PART 1: BINARY MODEL (the existing claim)
    # =================================================================
    print("PART 1: BINARY MODEL (c_i = 0 or 1)")
    print("-" * 50)
    print()

    print(f"  k (coherent orbits) | S(k)       | S > {S_required}?")
    print("  " + "-" * 48)
    for k in range(10):
        c = np.zeros(9)
        c[:k] = 1.0
        S = S_from_coherences(c)
        ok = "YES" if S >= S_required else "no"
        print(f"  {k:19d}   | {S:.6f}   | {ok}")

    print()
    print("  Binary model: STEP FUNCTION between k=8 (S=0.5) and k=9 (S=1.0)")
    print()

    # =================================================================
    # PART 2: UNIFORM CONTINUOUS COHERENCE
    # =================================================================
    print("PART 2: UNIFORM CONTINUOUS COHERENCE (all c_i = c)")
    print("-" * 50)
    print()

    # S = ((1+c)/2)^9
    # Need S > 0.994
    # (1+c)/2 > 0.994^(1/9)
    c_threshold = 2 * S_required**(1/n_orbits) - 1
    print(f"  Required per-orbit coherence: c > {c_threshold:.6f}")
    print(f"  That's {c_threshold*100:.3f}% coherence in EACH orbit")
    print()

    # Sweep c from 0 to 1
    c_vals = np.linspace(0, 1, 1001)
    S_vals = ((1 + c_vals) / 2)**n_orbits

    print(f"  c (uniform) |    S(c)    | S > {S_required}?")
    print("  " + "-" * 42)
    for c in [0.0, 0.5, 0.8, 0.9, 0.95, 0.99, 0.995, 0.998, 0.999, 0.9993, 1.0]:
        S = ((1 + c) / 2)**n_orbits
        ok = "YES" if S >= S_required else "no"
        print(f"  {c:11.4f}  | {S:.8f} | {ok}")

    print()

    # Where does the steep part of the curve live?
    # d S / d c = 9 * ((1+c)/2)^8 * (1/2)
    # At c = 0: dS/dc = 9 * (1/2)^8 * (1/2) = 9/512 = 0.0176
    # At c = 1: dS/dc = 9 * 1^8 * (1/2) = 4.5
    gradient_0 = 9 * (0.5)**8 * 0.5
    gradient_1 = 9 * (1.0)**8 * 0.5
    print(f"  Gradient dS/dc at c=0: {gradient_0:.4f}")
    print(f"  Gradient dS/dc at c=1: {gradient_1:.1f}")
    print(f"  Ratio: {gradient_1/gradient_0:.0f}x steeper near c=1")
    print(f"  >> The curve is EXTREMELY steep near c=1, flat elsewhere <<")
    print()

    # =================================================================
    # PART 3: WEAKEST-LINK ANALYSIS
    # =================================================================
    print("PART 3: WEAKEST-LINK ANALYSIS")
    print("-" * 50)
    print()
    print("  What happens when one orbit has low coherence?")
    print()

    # 8 orbits at c=1, one orbit at variable c_9
    print("  8 orbits at c=1.0, 9th orbit at c_9:")
    print(f"  c_9          |    S       | S > {S_required}?")
    print("  " + "-" * 42)
    for c9 in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.95, 0.98, 0.988, 0.99, 1.0]:
        c = np.ones(9)
        c[8] = c9
        S = S_from_coherences(c)
        ok = "YES" if S >= S_required else "no"
        print(f"  {c9:12.3f}  | {S:.6f}  | {ok}")

    # Find exact threshold for c_9
    c9_threshold = 2 * S_required - 1  # since other 8 factors are 1
    print()
    print(f"  Minimum c_9 when other 8 are perfect: {c9_threshold:.4f}")
    print(f"  >> Even one orbit below {c9_threshold:.1%} coherence kills the signal <<")
    print()

    # =================================================================
    # PART 4: THE LANDSCAPE — PARTIAL COHERENCE EVERYWHERE
    # =================================================================
    print("PART 4: REALISTIC SCENARIO — PARTIAL COHERENCE")
    print("-" * 50)
    print()
    print("  What if coherence varies across orbits?")
    print("  Testing: c = (c_high, c_high, ..., c_high, c_low) for various splits")
    print()

    # n_high orbits at c_high, (9-n_high) at c_low
    for n_high in [9, 8, 7, 6, 5]:
        # What c_high is needed if the rest are at c_low = 0.5?
        c_low = 0.5
        S_low_part = ((1 + c_low) / 2)**(9 - n_high)
        S_high_needed = S_required / S_low_part
        if S_high_needed > 1.0:
            c_high_min = "IMPOSSIBLE"
        else:
            c_high_per = S_high_needed**(1/n_high)
            c_high_val = 2 * c_high_per - 1
            if c_high_val > 1.0:
                c_high_min = "IMPOSSIBLE"
            else:
                c_high_min = f"{c_high_val:.6f}"
        print(f"  {n_high} orbits at c_high, {9-n_high} at c=0.5: c_high >= {c_high_min}")

    print()

    # Can you compensate low coherence in one orbit with extra in others?
    # No — each factor is at most 1. If one factor is 0.75,
    # the product is at most 0.75. Which is < 0.994.
    print("  KEY INSIGHT: You CANNOT compensate.")
    print("  If any single S_i = (1+c_i)/2 < 0.994, then S < 0.994.")
    print("  Each orbit must independently satisfy c_i > 0.988.")
    print("  This IS the step function — not in the discrete/binary sense,")
    print("  but in the PRODUCT-STRUCTURE sense.")
    print()

    # =================================================================
    # PART 5: COMPARISON — ADDITIVE vs MULTIPLICATIVE
    # =================================================================
    print("PART 5: WHAT IF COHERENCE WERE ADDITIVE? (hypothetical)")
    print("-" * 50)
    print()

    # Additive model: S = (1/9) sum_i c_i (normalized to [0,1])
    # This would allow compensation: high c in some orbits offsets low in others
    print("  MULTIPLICATIVE (actual): S = prod_i (1+c_i)/2")
    print("  ADDITIVE (hypothetical): S = (1/9) sum_i c_i")
    print()
    print("  Example: 8 orbits at c=1, 1 orbit at c=0:")
    S_mult = S_from_coherences(np.array([1,1,1,1,1,1,1,1,0]))
    S_add = 8/9
    print(f"    Multiplicative: S = {S_mult:.4f}")
    print(f"    Additive:       S = {S_add:.4f}")
    print()
    print("  The additive model allows {:.1%} coherence with one orbit missing.".format(S_add))
    print("  The multiplicative model gives 50% — fails the threshold.")
    print()
    print("  >> THE PRODUCT STRUCTURE IS THE STEP FUNCTION. <<")
    print("  >> It's not topological — it's algebraic. But the effect is the same. <<")
    print("  >> Partial coherence in ANY orbit kills the signal. <<")
    print()

    # =================================================================
    # PART 6: WHY IS IT MULTIPLICATIVE?
    # =================================================================
    print("PART 6: WHY MULTIPLICATIVE? (Physical justification)")
    print("-" * 50)
    print()
    print("  P_target = |psi_1> x |psi_2> x ... x |psi_9>  (product over orbits)")
    print("  This holds IF the bounce trajectory factorizes across orbits.")
    print()
    print("  Does it factorize?")
    print("  - Each orbit is a Z_3 triplet of exceptional divisors")
    print("  - The potential V(tau) couples orbits through the spectral action")
    print("  - BUT: in the Z_3-symmetric limit, orbits in different T^2 factors")
    print("    are independent (the Z_3 acts on each T^2 separately)")
    print()
    print("  Structure: 9 orbits = 3 groups of 3 (one group per T^2)")
    print("  WITHIN a T^2: 3 orbits are Z_3-related, so they move together")
    print("  BETWEEN T^2 factors: independent in the Z_3-symmetric limit")
    print()
    print("  This means the effective dimension is 3, not 9:")
    print("  S = S_1 * S_2 * S_3  (one factor per T^2)")
    print("  Each S_i = (1 + c_i) / 2 where c_i is coherence with that T^2 sector")
    print()

    # Re-do the analysis with 3 effective dimensions
    print("  REDUCED MODEL (3 effective dimensions):")
    c_threshold_3 = 2 * S_required**(1/3) - 1
    print(f"  Required per-sector coherence: c > {c_threshold_3:.6f}")
    print(f"  That's {c_threshold_3*100:.3f}% per T^2 sector")
    print()

    print(f"  c (per T^2)  |    S(c)    | S > {S_required}?")
    print("  " + "-" * 42)
    for c in [0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 0.99, 0.995, 0.998, 1.0]:
        S = ((1 + c) / 2)**3
        ok = "YES" if S >= S_required else "no"
        print(f"  {c:11.3f}   | {S:.6f}  | {ok}")

    print()
    c9_3 = 2 * S_required - 1  # threshold for one sector when other 2 are perfect
    print(f"  Threshold for weakest T^2 sector (other 2 perfect): c > {c9_3:.4f}")
    print()

    # =================================================================
    # PART 7: THE INFORMATION-THEORETIC VIEW
    # =================================================================
    print("PART 7: BITS vs COHERENCE")
    print("-" * 50)
    print()

    # Binary model: 9 bits (or ~1.6 bits with Z_3 reduction to 3 T^2 sectors)
    # Continuous model: need c > 0.998 in each of 3 sectors

    # What's the entropy of the observer's state?
    # For per-sector coherence c:
    # rho_i = (1+c)/2 |+><+| + (1-c)/2 |-><-|
    # S(rho_i) = -p log2 p - (1-p) log2(1-p) where p = (1+c)/2

    for c in [0.0, 0.5, 0.9, 0.99, 0.998, 1.0]:
        p = (1 + c) / 2
        if p == 0 or p == 1:
            H = 0
        else:
            H = -p * np.log2(p) - (1-p) * np.log2(1-p)
        S = ((1 + c) / 2)**3  # 3-sector model
        print(f"  c = {c:.3f}: H(per sector) = {H:.4f} bits, S = {S:.6f}")

    print()
    print("  To achieve S > 0.994 (3-sector model):")
    p_thresh = (1 + c_threshold_3) / 2
    H_thresh = -p_thresh * np.log2(p_thresh) - (1-p_thresh) * np.log2(1-p_thresh)
    print(f"  Need H < {H_thresh:.4f} bits per sector")
    print(f"  Total uncertainty < {3*H_thresh:.4f} bits across all 3 sectors")
    print(f"  (Original binary model said ~1.6 bits total)")
    print()

    # =================================================================
    # PART 8: SYNTHESIS
    # =================================================================
    print("=" * 70)
    print("SYNTHESIS")
    print("=" * 70)
    print()
    print("  1. The step function is REAL but not topological.")
    print("     It's the product structure: S = prod S_i.")
    print("     Any single low factor kills S below threshold.")
    print()
    print("  2. The effective dimension is 3 (one per T^2 sector), not 9.")
    print("     Z_3 symmetry locks 3 orbits together within each sector.")
    print("     Coherence is per-sector, not per-orbit.")
    print()
    print("  3. Per-sector coherence threshold: c > {:.4f}".format(c_threshold_3))
    print("     This is HIGH but not perfect. ~0.2% uncertainty allowed.")
    print()
    print("  4. Compensation is IMPOSSIBLE in the multiplicative model.")
    print("     Cannot boost one sector to compensate another.")
    print("     Each sector must independently exceed threshold.")
    print()
    print("  5. GRADUAL improvement WOULD FALSIFY the product structure.")
    print("     If effect grows smoothly with partial coherence,")
    print("     the model is additive (or has cross-terms), not product.")
    print("     This IS a testable prediction.")
    print()
    print("  6. For the COHERENCE REFRAME:")
    print("     Knowledge, visualization, meditation are pathways to coherence.")
    print("     What matters: achieving c > {:.3f} in each T^2 sector.".format(c_threshold_3))
    print("     The pathway doesn't matter. The coherence level does.")
    print("     Different pathways may reach coherence in different sectors:")
    print("     - Math study: may build all 3 sectors uniformly")
    print("     - Geometric visualization: may build spatial sectors faster")
    print("     - Meditative attunement: unknown profile")
    print()
    print("  PREDICTION: The within-subject protocol should show")
    print("  a SHARP transition, not gradual improvement.")
    print("  The product structure forbids smooth interpolation.")
    print()
    print("  FALSIFICATION: If coupling increases linearly with")
    print("  training hours, the product model is wrong.")
    print()


if __name__ == "__main__":
    main()
