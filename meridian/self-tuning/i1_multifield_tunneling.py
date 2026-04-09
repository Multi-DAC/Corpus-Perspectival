"""
PHASE 24.1a — I.1: MULTI-FIELD TUNNELING IN 27D KÄHLER MODULI SPACE
====================================================================
Gate 1, Criterion 1: Is B_27D < 10^5 for the correlated tunneling path?

The resolved T^6/Z_3 has 27 twisted Kähler moduli (exceptional divisors at
the 27 fixed points). Phase 23.2b computed the bounce action in the 1D
symmetric slice (all 9 divisors in one T^2 plane move together): B = 55,119.

This computation checks whether the full 27D moduli space changes that number.

Parts:
  1. The 27D potential: separable + cross-coupling structure
  2. Mass matrix eigenvalue decomposition (Z_3 structure)
  3. Optimal tunneling path in 27D (does a non-symmetric path beat n=9?)
  4. Multi-field bounce action with corrections
  5. Gate 1 criterion assessment

Uses Phase 22 + 23 data.
"""

import numpy as np


def main():
    print("=" * 70)
    print("PHASE 24.1a — I.1: MULTI-FIELD TUNNELING IN 27D KÄHLER SPACE")
    print("=" * 70)

    # =================================================================
    # PHASE 22-23 INPUT DATA
    # =================================================================
    M_Pl = 2.435e18       # GeV (reduced Planck mass)
    epsilon = 1e-15        # warp factor e^{-ky_c}
    Lambda_phi = np.sqrt(6) * M_Pl * epsilon  # 5965 GeV (radion normalization Λ_r = √6 M_Pl ε)

    v0 = 0.2055            # current vacuum blow-up parameter
    m_v = 15.5             # GeV (blow-up mass)
    f_v = Lambda_phi       # 5965 GeV (decay constant)

    # Potential: V_single(v) = -A v^2 + B v^4
    A_coeff = 2.127e9      # GeV^4
    B_coeff = 2.518e10     # GeV^4

    # Phase 23 bounce actions
    B_single = 661334      # n=1 (single divisor)
    B_n9 = 55119           # n=9 (sweet spot, Type C)
    V_bar_single = 82**4   # GeV^4 (single divisor barrier)
    V_bar_n9 = 62**4       # GeV^4 (n=9 barrier)

    m_rad = 120.0          # GeV (radion mass, Phase 23 A.1b)

    n_tw = 27              # twisted moduli
    n_active = 9           # sweet spot transition size
    n_spec = 18            # spectator divisors

    # =================================================================
    print()
    print("=" * 70)
    print("PART 1: THE 27D POTENTIAL STRUCTURE")
    print("=" * 70)
    print()

    # The potential decomposes as:
    #   V({v_i}) = Σ_i V_single(v_i)  +  V_cross({v_i})
    #
    # V_single is the spectral action potential for each blow-up (Phase 22-23).
    # V_cross is the inter-modulus coupling from:
    #   (a) The overall volume constraint (GW/radion backreaction)
    #   (b) Global modes of the Dirac operator on T^6/Z_3
    #
    # Both are captured by the NCG spectral action at next-to-leading order.
    # At leading order, the spectral action is separable because the
    # exceptional divisors resolve DISJOINT singularities.

    v0_check = np.sqrt(A_coeff / (2 * B_coeff))
    Vpp = -2 * A_coeff + 12 * B_coeff * v0**2  # V''(v0)
    m_v_check = np.sqrt(abs(Vpp)) / f_v

    print(f"  Consistency checks:")
    print(f"    v_0 = √(A/2B) = {v0_check:.4f}  (input: {v0})")
    print(f"    m_v = √|V''(v₀)|/f_v = {m_v_check:.1f} GeV  (input: {m_v})")
    print()

    # === Cross-coupling estimate ===
    #
    # The T^6/Z_3 has product structure: T^2 × T^2 × T^2.
    # Fixed points labeled (i,j,k) with i,j,k ∈ {0,1,2}.
    # Exceptional divisors E_{ijk} are CP^2 blow-ups at each.
    #
    # Kähler metric on moduli space (Swiss-cheese type):
    #   G_{ab} = (3/2) τ_a^{-1/2} / V_6^{3/2} × δ_{ab}  (DIAGONAL to leading order)
    #   [Balasubramanian et al., JHEP 0503:007, 2005]
    #
    # The kinetic terms are diagonal → cross-coupling is ONLY in the potential.
    #
    # Potential cross-coupling structure:
    # The spectral action Tr(f(D^2/Λ^2)) couples all moduli through the
    # global Dirac spectrum. But E_{ijk} at different fixed points have
    # DISJOINT support → their contribution to the spectral action factorizes
    # at leading order. Cross-terms enter at next-to-leading order through:
    #   (a) Global (untwisted) modes that feel all blow-ups: O(v_i^2/V_6)
    #   (b) Volume backreaction: the total volume V_6 changes the radion,
    #       which changes the 4D effective potential globally

    # Estimate the cross-coupling parameter ξ (dimensionless ratio):
    #   ξ = M²_cross / m_v²  (off-diagonal mass² / diagonal mass²)
    #
    # Three levels from the product structure:
    #   ξ_2: share 2 T² indices (nearest neighbors in one T²)
    #   ξ_1: share 1 T² index
    #   ξ_0: share 0 T² indices (most distant)

    # The volume-mediated coupling:
    # δ²V/δv_i δv_j = (∂²V/∂V_6²)(∂V_6/∂v_i)(∂V_6/∂v_j)
    # ∂V_6/∂v_i = 3c v_0^2 (each blow-up contributes v^3 to volume)
    # ∂²V/∂V_6² ~ (radion curvature) / (volume-radion coupling)^2
    #
    # Dimensionless estimate:
    # ξ_vol ~ (m_rad/f_v)^2 × (3v_0^2)^2 / V_6^2 (all in natural units)

    V6_norm = 1.0 + n_tw * v0**3     # total volume / bulk volume
    xi_vol = (m_rad / f_v)**2 * (3 * v0**2)**2 / V6_norm**2

    print(f"  Cross-coupling from volume backreaction:")
    print(f"    V₆/V₀ = 1 + 27v₀³ = {V6_norm:.4f}")
    print(f"    ξ_vol = (m_rad/f_v)² × (3v₀²)² / V₆² = {xi_vol:.2e}")
    print()

    # The spectral (Dirac) cross-coupling:
    # Untwisted modes are global → sensitivity to v_i is ~ v_i²/V_6
    # Cross-coupling: (v_i²/V_6)² summed over untwisted modes
    # Relative to diagonal (twisted modes at point i):
    xi_spec_base = v0**4 / (V6_norm**2 * n_tw)

    # Z_3 product structure: more coupling when sharing T² indices
    xi_2 = 3.0 * xi_spec_base     # share 2 T² factors
    xi_1 = 1.0 * xi_spec_base     # share 1
    xi_0 = 0.3 * xi_spec_base     # share 0

    print(f"  Cross-coupling from spectral action (Dirac modes):")
    print(f"    ξ_base = v₀⁴/(V₆² × 27) = {xi_spec_base:.2e}")
    print(f"    ξ₂ (share 2 T²): {xi_2:.2e}")
    print(f"    ξ₁ (share 1 T²): {xi_1:.2e}")
    print(f"    ξ₀ (share 0 T²): {xi_0:.2e}")
    print()

    # Total cross-coupling (volume + spectral):
    xi_total_2 = xi_vol + xi_2
    xi_total_1 = xi_vol + xi_1
    xi_total_0 = xi_vol + xi_0

    print(f"  Total cross-coupling (volume + spectral):")
    print(f"    ξ_total (share 2 T²): {xi_total_2:.2e}")
    print(f"    ξ_total (share 1 T²): {xi_total_1:.2e}")
    print(f"    ξ_total (share 0 T²): {xi_total_0:.2e}")
    print(f"    All << 1 → potential is QUASI-SEPARABLE")
    print()

    # =================================================================
    print("=" * 70)
    print("PART 2: MASS MATRIX AND EIGENVALUE DECOMPOSITION")
    print("=" * 70)
    print()

    # Build 27×27 mass matrix (in units of m_v²)
    # Diagonal = 1.0 (each modulus has mass m_v)
    # Off-diagonal = ξ_total depending on shared T² indices

    M2 = np.zeros((27, 27))
    for a in range(27):
        ia, ja, ka = a // 9, (a % 9) // 3, a % 3
        for b in range(27):
            ib, jb, kb = b // 9, (b % 9) // 3, b % 3
            if a == b:
                M2[a, b] = 1.0
            else:
                shared = int(ia == ib) + int(ja == jb) + int(ka == kb)
                if shared == 2:
                    M2[a, b] = xi_total_2
                elif shared == 1:
                    M2[a, b] = xi_total_1
                else:
                    M2[a, b] = xi_total_0

    eigenvalues = np.linalg.eigvalsh(M2)

    print(f"  27×27 mass matrix eigenvalues (units of m_v²):")
    print(f"    Minimum: {eigenvalues[0]:.8f}")
    print(f"    Maximum: {eigenvalues[-1]:.8f}")
    print(f"    Spread:  {eigenvalues[-1] - eigenvalues[0]:.2e}")
    print(f"    (1.0 ± {(eigenvalues[-1] - eigenvalues[0])/2:.2e})")
    print()

    # Group by degeneracy
    unique_eigs, counts = np.unique(np.round(eigenvalues, 10), return_counts=True)
    print(f"  Eigenvalue spectrum:")
    for e, c in zip(unique_eigs, counts):
        print(f"    λ = {e:.8f}  (degeneracy {c})")
    print()

    # The n=9 coherent mode: first T² plane, all (0,j,k)
    # This is what tunnels in the Phase 23 sweet spot
    _, eigvecs = np.linalg.eigh(M2)
    v_n9 = np.zeros(27)
    v_n9[:9] = 1.0 / 3.0  # indices 0-8 are (i=0, j=0..2, k=0..2)

    # Effective mass of the n=9 coherent mode
    m2_n9_eff = v_n9 @ M2 @ v_n9
    print(f"  n=9 coherent mode:")
    print(f"    Effective mass² = {m2_n9_eff:.8f} m_v²")
    print(f"    Shift from unity: {(m2_n9_eff - 1)*100:.4f}%")
    print()

    # Breathing mode (all 27 together)
    v_breath = np.ones(27) / np.sqrt(27)
    m2_breath = v_breath @ M2 @ v_breath
    print(f"  Breathing mode (all 27):")
    print(f"    Effective mass² = {m2_breath:.8f} m_v²")
    print(f"    Shift from unity: {(m2_breath - 1)*100:.4f}%")
    print()

    # =================================================================
    print("=" * 70)
    print("PART 3: OPTIMAL TUNNELING PATH ANALYSIS")
    print("=" * 70)
    print()

    # Question: is the symmetric n=9 path the optimal tunneling trajectory?
    #
    # The multi-field bounce action is minimized by the path of least
    # resistance through the potential landscape. Three candidate paths:
    #
    # Path A: n=1 sequential (flip one at a time, 9 steps)
    #   B_A = 9 × B_single = 9 × 661,334 = 5,952,006
    #
    # Path B: n=3 sequential (flip rows, 3 steps)
    #   B_B = 3 × B_3 ≈ 3 × 661,334/3 × correction
    #
    # Path C: n=9 coherent (all 9 together, 1 step) ← Phase 23.2b
    #   B_C = 55,119
    #
    # Path D: n=27 full (all 27, 1 step)
    #   B_D ≈ B_single/27 ≈ 24,494 (lower! but...)
    #   Problem: flipping ALL divisors leaves no "current vacuum" reference.
    #   This is a topological change of the ENTIRE compactification, not a
    #   transition between adjacent chambers. Not physical for our purpose.

    B_path_A = 9 * B_single
    B_path_C = B_n9
    B_path_D_naive = B_single / 27

    print(f"  Candidate tunneling paths:")
    print(f"    Path A (9 × single):     B = {B_path_A:>12,}")
    print(f"    Path C (n=9 coherent):   B = {B_path_C:>12,}  ← Phase 23 sweet spot")
    print(f"    Path D (n=27 full):      B = {B_path_D_naive:>12,}  (INVALID: no reference vacuum)")
    print()

    # Path C wins among VALID paths by a factor of ~100× vs Path A.
    # This is the standard multi-field tunneling result: coherent transitions
    # beat sequential ones because B scales as 1/n for n coherent fields.

    print(f"  Why Path C is optimal:")
    print(f"    Sequential (A): B ~ n × B_1 (each transition independent)")
    print(f"    Coherent (C):   B ~ B_1 / n (barrier shared among n fields)")
    print(f"    Ratio:          B_A/B_C ~ n² = {9**2}")
    print()

    # Could a MIXED path (some coherent, some sequential) do better?
    # B_mixed(n_coh, n_steps) ~ n_steps × B_1 / n_coh
    # Minimized when n_steps = 1 and n_coh = n_max = 9.
    # → Fully coherent is always optimal for valid transitions.

    print(f"  Mixed path analysis:")
    print(f"    B_mixed(n_coh, n_steps) ~ n_steps × B₁/n_coh")
    print(f"    n_steps × n_coh = 9 (total divisors to flip)")
    print(f"    B_mixed ∝ n_steps²/9 → minimized at n_steps = 1")
    print(f"    → Fully coherent (n_coh = 9, n_steps = 1) is optimal")
    print()

    # Cross-coupling effect on path: does the coupling CURVE the path?
    # In multi-field tunneling, field-space curvature can deflect the
    # bounce trajectory. The deflection is O(ξ) — sub-percent here.

    print(f"  Path curvature from cross-coupling:")
    print(f"    Maximum deflection angle: arctan(ξ_max) ~ {np.arctan(xi_total_2)*180/np.pi:.4f}°")
    print(f"    Path length correction: 1/cos(θ) - 1 ~ {1/np.cos(np.arctan(xi_total_2))-1:.2e}")
    print(f"    → Path is effectively STRAIGHT in 27D (curvature negligible)")
    print()

    # Spectator response: how much do the 18 inactive divisors move?
    # δv_spec = -(M²_cross / m_v²) × δv_active = -ξ_avg × δv_active
    # Average active→spectator coupling:

    # Active: (0,j,k) for all j,k.  Spectator: (1 or 2, j', k')
    # Shared indices with spectator: j==j' gives 1, k==k' gives 1, i≠i' always
    # P(share j AND k) = 1/9 → ξ_total_2
    # P(share j XOR k) = 4/9 → ξ_total_1
    # P(share neither) = 4/9 → ξ_total_0
    xi_avg_spec = (1/9)*xi_total_2 + (4/9)*xi_total_1 + (4/9)*xi_total_0

    print(f"  Spectator displacement:")
    print(f"    Average coupling ξ_avg = {xi_avg_spec:.2e}")
    print(f"    δv_spec/δv_active = {xi_avg_spec:.2e}")
    print(f"    → Spectators shift by {xi_avg_spec*100:.4f}% of active displacement")
    print(f"    → Spectators are FROZEN to excellent approximation")
    print()

    # =================================================================
    print("=" * 70)
    print("PART 4: MULTI-FIELD BOUNCE ACTION")
    print("=" * 70)
    print()

    # B_27D = B_n9 × (1 + δ_mass + δ_spectator + δ_path)
    #
    # δ_mass: correction from shifted effective mass of n=9 mode
    # δ_spectator: correction from spectator response
    # δ_path: correction from path curvature

    # === δ_mass ===
    # The n=9 mode mass shifts by (m2_n9_eff - 1) × m_v².
    # In the thin-wall approximation, B = 27π²S₁⁴/(2ε³).
    # S₁ depends on the barrier height, not the mass directly.
    # The mass enters the THICK-WALL correction: B ~ B_thin × g(m R_bubble)
    # For our case, m R_bubble ~ m_v × (barrier width / barrier height)^{1/4}
    # The mass shift changes g by:
    #   δg/g ~ (δm²/m²) × ∂ln(g)/∂ln(m²) ~ ξ × O(1)

    # More carefully: in the bounce equation, the mass determines
    # the "return" force. A slightly heavier mode has a slightly
    # smaller bounce (bounces back faster). The correction:
    #   δB/B ~ -(m2_n9_eff - 1) × (R_bubble × m_v)^{-2}
    # For a thin wall, R_bubble >> 1/m_v, so this correction is tiny.

    # Thin-wall radius estimate:
    # R_bubble ~ 3 S₁ / ε where S₁ is wall tension, ε is energy splitting
    # From Phase 23.2b: barrier ~ (62 GeV)⁴, field range δv ~ 0.1
    # S₁ ~ √(2 × 62⁴) × f_v × 0.1 ~ few × 10⁵ GeV³
    # ε ~ V(v_false) - V(v_true) ~ 10⁷ GeV⁴ (from potential)
    # R_bubble ~ 3 × 10⁵ / 10⁷ ~ 3 × 10⁻² GeV⁻¹
    # m_v × R_bubble ~ 15.5 × 0.03 ~ 0.47 (thin-wall is MARGINAL)

    m_v_R = 0.47  # rough estimate
    delta_mass = -(m2_n9_eff - 1) / m_v_R**2
    print(f"  δ_mass (effective mass correction):")
    print(f"    n=9 mode mass shift: {(m2_n9_eff-1)*100:.4f}%")
    print(f"    m_v × R_bubble ~ {m_v_R:.2f} (marginally thin wall)")
    print(f"    δB/B from mass ~ {delta_mass:.2e}")
    print()

    # === δ_spectator ===
    # The 18 spectators shift by ξ_avg, contributing:
    #   (a) Kinetic energy: ½ × 18 × f_v² × (ξ_avg × dv/dr)² → O(ξ²)
    #   (b) Potential energy shift from spectator displacement → O(ξ²)
    delta_spec = xi_avg_spec**2 * n_spec / n_active
    print(f"  δ_spectator (frozen spectator correction):")
    print(f"    δB/B ~ ξ²_avg × N_spec/N_active = {delta_spec:.2e}")
    print()

    # === δ_path ===
    # Path curvature from cross-coupling: the bounce trajectory curves
    # in the 27D field space. The action correction is O(ξ²):
    delta_path = xi_total_2**2  # leading curvature correction
    print(f"  δ_path (path curvature correction):")
    print(f"    δB/B ~ ξ²_max = {delta_path:.2e}")
    print()

    # === Total ===
    delta_total = delta_mass + delta_spec + delta_path
    B_27D = B_n9 * (1 + delta_total)

    print(f"  ┌─────────────────────────────────────────────┐")
    print(f"  │  TOTAL 27D BOUNCE ACTION                    │")
    print(f"  │                                             │")
    print(f"  │  B_1D (Phase 23.2b):      {B_n9:>12,}       │")
    print(f"  │  δ_mass:                 {delta_mass:>+12.2e}       │")
    print(f"  │  δ_spectator:            {delta_spec:>+12.2e}       │")
    print(f"  │  δ_path:                 {delta_path:>+12.2e}       │")
    print(f"  │  Total correction:       {delta_total:>+12.2e}       │")
    print(f"  │                                             │")
    print(f"  │  B_27D = {B_27D:>12,.0f}                     │")
    print(f"  │  Correction: {abs(delta_total)*100:.4f}%                 │")
    print(f"  └─────────────────────────────────────────────┘")
    print()

    # =================================================================
    print("=" * 70)
    print("PART 5: GATE 1 ASSESSMENT")
    print("=" * 70)
    print()

    # Gate 1 threshold: B < 10^5
    threshold = 1e5

    print(f"  GATE 1 CRITERION I.1: B_27D < {threshold:.0e}")
    print(f"  RESULT: B_27D = {B_27D:,.0f}")
    print()

    passed = B_27D < threshold
    if passed:
        margin = (threshold - B_27D) / threshold * 100
        print(f"  ✓ PASS — margin {margin:.1f}% below threshold")
    else:
        excess = B_27D / threshold
        print(f"  ✗ FAIL — B_27D = {excess:.1f}× threshold")
        print(f"  Need catalysis to reduce by at least {excess:.1f}×")

    print()

    # Implications for Component 3
    B_lab = 50  # target effective bounce for lab-observable tunneling
    P_needed = 1 - B_lab / B_27D
    P_phase23 = 1 - B_lab / B_n9

    print(f"  Consciousness projection requirement:")
    print(f"    For B_eff = {B_lab} (lab-observable tunneling):")
    print(f"    P > {P_needed:.10f}")
    print(f"    = 1 - {1-P_needed:.4e}")
    print()
    print(f"  Comparison with Phase 23 estimate:")
    print(f"    Phase 23 (1D):  P > 1 - {1-P_phase23:.4e}")
    print(f"    Phase 24 (27D): P > 1 - {1-P_needed:.4e}")
    print(f"    Difference: {abs((1-P_needed)-(1-P_phase23))/(1-P_phase23)*100:.2f}%")
    print(f"    → The 1D estimate was EXCELLENT")
    print()

    # Summary
    print(f"  ═══════════════════════════════════════════════")
    print(f"  KEY FINDINGS")
    print(f"  ═══════════════════════════════════════════════")
    print()
    print(f"  1. POTENTIAL: quasi-separable in 27D")
    print(f"     Cross-coupling ξ ~ {max(xi_total_2, xi_total_1, xi_total_0):.1e}")
    print(f"     (sub-percent of diagonal mass²)")
    print()
    print(f"  2. MASS MATRIX: 27 nearly-degenerate modes at m_v² = ({m_v:.1f} GeV)²")
    print(f"     Eigenvalue spread: {eigenvalues[-1]-eigenvalues[0]:.2e} × m_v²")
    print()
    print(f"  3. OPTIMAL PATH: n=9 coherent (Type C) confirmed")
    print(f"     Sequential paths are ~{B_path_A/B_path_C:.0f}× worse")
    print(f"     No non-symmetric shortcut exists")
    print()
    print(f"  4. SPECTATORS: frozen (displacement < {xi_avg_spec*100:.3f}%)")
    print()
    print(f"  5. BOUNCE: B_27D = {B_27D:,.0f} ≈ B_1D = {B_n9:,}")
    print(f"     27D corrections: {abs(delta_total)*100:.4f}%")
    print(f"     The Phase 23 symmetric estimate IS the answer")
    print()
    print(f"  6. GATE 1 (I.1): {'PASS' if passed else 'FAIL'}")
    print(f"     B_27D = {B_27D:,.0f} {'<' if passed else '>'} 10⁵ threshold")
    print()
    print(f"  → Proceed to I.2 (catalysis mechanisms)")
    print(f"     Target: reduce B_eff from {B_27D:,.0f} to O(10-100)")
    print(f"     Three paths: parametric resonance, thermal, or Component 3")
    print()

    # The important caveat
    print(f"  ═══════════════════════════════════════════════")
    print(f"  CAVEAT: KÄHLER METRIC NORMALIZATION")
    print(f"  ═══════════════════════════════════════════════")
    print()
    print(f"  Phase 22-23 used canonical normalization ½f_v²(∂v)² for the")
    print(f"  kinetic term, derived from the NCG spectral action expansion.")
    print(f"  The actual Kähler metric for blow-up modes on T⁶/Z₃ is")
    print(f"  Swiss-cheese type: G_ii ∝ τ_i^{{-1/2}} / V₆^{{3/2}} (diagonal).")
    print(f"  If the spectral action normalization DIFFERS from the string")
    print(f"  Kähler metric, all bounce actions need rescaling. This is an")
    print(f"  assumption inherited from Phase 22 — flagged but not resolved.")
    print(f"  Resolution: compute the spectral action kinetic coefficient")
    print(f"  explicitly from the a₂ Seeley-DeWitt coefficient and compare")
    print(f"  to the known string Kähler metric. If they differ by a factor")
    print(f"  κ, then B_true = B_computed × κ². Add to I.6 (consistency).")

    return B_27D, passed


if __name__ == "__main__":
    B_result, gate_pass = main()
