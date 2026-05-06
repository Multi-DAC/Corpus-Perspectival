"""
SPECTRAL PROXIMITY COMPUTATION: S FOR THE RESOLVED T^6/Z_3
=============================================================
Clawd, March 26, 2026.

Computes the spectral proximity S = Tr(rho_O * P_target) / Tr(rho_O)
using the concrete geometry of the resolved T^6/Z_3 orbifold.

This is the first time S is a number rather than a symbol.

Key results:
- N_chambers = 512 (Z_3-symmetric sector)
- S_random = 1/512 ~ 0.002
- S_required > 0.994
- Amplification needed: ~510x
- Spectral proximity is STRUCTURAL (9 bits of topology),
  not high-precision numerical knowledge
"""

import numpy as np


def main():
    print("=" * 70)
    print("SPECTRAL PROXIMITY COMPUTATION: S FOR THE RESOLVED T^6/Z_3")
    print("=" * 70)
    print()

    # =================================================================
    # PART 1: KAHLER CHAMBER COUNTING
    # =================================================================
    print("PART 1: KAHLER CHAMBER COUNTING")
    print("-" * 50)
    print()

    h11 = 36          # total Kahler moduli
    n_twisted = 27    # exceptional divisors (one per fixed point)
    n_untwisted = 9   # inherited from T^6

    # 27 fixed points of Z_3 on T^6 = T^2 x T^2 x T^2
    # (3 fixed points per T^2, 3^3 = 27 total)
    n_fixed = 3**3
    print(f"  Fixed points of Z_3 action on T^6: {n_fixed}")
    print(f"  Exceptional divisors: {n_twisted}")
    print(f"  Untwisted moduli: {n_untwisted}")
    print(f"  Total h^(1,1) = {h11}")
    print()

    # Z_3 groups 27 divisors into 9 orbits of 3
    n_orbits = n_twisted // 3  # = 9
    print(f"  Z_3 orbits of exceptional divisors: {n_orbits}")
    print()

    # Z_3-symmetric chambers: each orbit either + or -
    N_chambers = 2**n_orbits
    print(f"  Z_3-symmetric Kahler chambers: 2^{n_orbits} = {N_chambers}")

    # Full chambers (non-Z_3-symmetric): 4 classes per orbit
    N_chambers_full = 4**n_orbits
    print(f"  Full chambers (non-symmetric): 4^{n_orbits} = {N_chambers_full:,}")
    print(f"  >> Using Z_3-symmetric count for n=9 coherent path <<")
    print()

    # =================================================================
    # PART 2: S_RANDOM AND REQUIRED AMPLIFICATION
    # =================================================================
    print("PART 2: SPECTRAL PROXIMITY — RANDOM vs REQUIRED")
    print("-" * 50)
    print()

    S_random = 1.0 / N_chambers
    S_random_full = 1.0 / N_chambers_full

    print(f"  S_random (Z_3-symmetric): 1/{N_chambers} = {S_random:.6f}")
    print(f"  S_random (full):          1/{N_chambers_full:,} = {S_random_full:.2e}")
    print()

    # Required S
    B_27D = 54937
    B_eff_threshold = 165  # for macroscopic observation
    P_required = 1 - B_eff_threshold / B_27D

    print(f"  B_27D = {B_27D}")
    print(f"  Required P = S^(1/2) * F > {P_required:.6f}")

    S_required = P_required**2
    print(f"  Required S (with F=1): > {S_required:.6f}")
    print()

    amp = S_required / S_random
    print(f"  Amplification needed: {amp:.0f}x over random")
    print()

    # =================================================================
    # PART 3: EIGENVALUE SHIFTS UNDER THE FLOP
    # =================================================================
    print("PART 3: DIRAC EIGENVALUE SHIFTS ACROSS KAHLER WALL")
    print("-" * 50)
    print()

    A_coeff = 2.127e9    # GeV^4
    B_coeff = 2.518e10   # GeV^4
    v0 = 0.2055          # dimensionless blow-up parameter
    m_v = 15.5           # GeV
    f_v = 5965.0         # GeV

    phi_0 = f_v * v0
    Delta_v = 2 * v0
    Delta_phi = f_v * Delta_v
    Delta_lambda = 2 * m_v

    print(f"  Current vacuum: v_0 = {v0}, phi_0 = {phi_0:.1f} GeV")
    print(f"  Flop displacement: Delta_v = {Delta_v:.4f}")
    print(f"  Eigenvalue shift per flop: Delta_lambda ~ {Delta_lambda:.1f} GeV")
    print(f"  This is {Delta_lambda/m_v:.0f}x the blow-up mass")
    print()

    n_shifting = 9
    print(f"  Eigenmodes that shift (n=9 transition): {n_shifting}")
    print(f"  Eigenmodes unchanged (spectator): {n_twisted - n_shifting}")
    print()

    # =================================================================
    # PART 4: S AS A FUNCTION OF KNOWLEDGE
    # =================================================================
    print("PART 4: S vs STRUCTURAL KNOWLEDGE")
    print("-" * 50)
    print()

    print("  k (orbits known) | Chambers | S(k)       | Sufficient?")
    print("  " + "-" * 58)
    for k in range(10):
        remaining = 2**(9 - k)
        S_k = 1.0 / remaining
        ok = "YES" if S_k >= S_required else "no"
        print(f"  {k:15d}    | {remaining:8d} | {S_k:.6f}   | {ok}")

    print()
    print(f"  Required: S > {S_required:.6f}")
    print(f"  Achieved ONLY at k = 9: S = 1.0")
    print(f"  k = 8 gives S = 0.5 — FAILS by factor of 2")
    print()
    print("  ** SHARP THRESHOLD: all 9 orbit directions must be known **")
    print()

    # =================================================================
    # PART 5: INFORMATION CONTENT
    # =================================================================
    print("PART 5: INFORMATION CONTENT OF SPECTRAL KNOWLEDGE")
    print("-" * 50)
    print()

    bits = np.log2(N_chambers)
    print(f"  Bits to identify K_target: {bits:.0f} bits")
    print(f"  = 1 bit per orbit x {n_orbits} orbits")
    print(f"  Each bit: does this orbit flop to + or - ?")
    print()

    # Resolution requirement
    print(f"  Eigenvalue precision needed: < {Delta_lambda:.0f} GeV")
    print(f"  (to distinguish flopped from unflopped orbits)")
    print(f"  This is COARSE — the shifts are macroscopic in GeV terms")
    print()

    # =================================================================
    # PART 6: THE CONTINUOUS REFINEMENT (WITHIN-CHAMBER)
    # =================================================================
    print("PART 6: WITHIN-CHAMBER REFINEMENT")
    print("-" * 50)
    print()

    omega = m_v  # harmonic oscillator frequency
    V_barrier = A_coeff**2 / (4 * B_coeff)

    print(f"  Once the correct chamber is identified (S_discrete = 1):")
    print(f"  the observer must also match the ground state wavefunction.")
    print()
    print(f"  Harmonic oscillator spacing: omega = {omega} GeV")
    print(f"  Barrier height (single modulus): {V_barrier:.3e} GeV^4")
    print()
    print(f"  The ground state is determined by V(tau) near the minimum.")
    print(f"  Knowing V requires knowing D_F eigenvalues (spectral action).")
    print(f"  First ~{h11} eigenvalues determine V shape.")
    print(f"  Precision needed: < {omega} GeV (resolve level spacing)")
    print()

    # =================================================================
    # PART 7: THE TORUS DIRAC SPECTRUM (FLAT ORBIFOLD LIMIT)
    # =================================================================
    print("PART 7: DIRAC SPECTRUM ON T^6/Z_3 (FLAT LIMIT)")
    print("-" * 50)
    print()

    # On T^6 with complex structure tau_i = omega = e^{2pi i/3}:
    # The lattice is Lambda = Z + omega Z on each T^2.
    # Eigenvalues: lambda^2 = (4/3) * sum_i (m_i^2 + n_i^2 - m_i*n_i)
    #
    # The norm-squared on the A_2 root lattice:
    # |m + n*omega|^2 = m^2 + n^2 - m*n  (using omega = e^{2pi i/3})
    # This is the A_2 lattice norm.

    # Enumerate eigenvalues on one T^2
    N_max = 20  # lattice range
    norms_2d = []
    for m in range(-N_max, N_max + 1):
        for n in range(-N_max, N_max + 1):
            if m == 0 and n == 0:
                continue
            norm = m**2 + n**2 - m * n  # A_2 lattice norm
            norms_2d.append(norm)

    norms_2d = sorted(set(norms_2d))
    print(f"  A_2 lattice norms (first 20): {norms_2d[:20]}")
    print()

    # On T^6/Z_3: eigenvalue = (4/3) * (N_1 + N_2 + N_3)
    # where N_i = m_i^2 + n_i^2 - m_i*n_i is the A_2 norm on each T^2.
    # Z_3 invariance: the state (m1,n1,m2,n2,m3,n3) is invariant under
    # the DIAGONAL Z_3 action: (m,n) -> (-n, m-n) simultaneously on all T^2.

    # Count Z_3-invariant states up to a given eigenvalue
    # The Z_3 action on lattice vectors: (m,n) -> (-n, m-n)
    # Orbit size is 3 (generic) or 1 (only origin)

    # For the FULL T^6: we need the 6D lattice and the diagonal Z_3 action.
    # A state is specified by 3 pairs: (m1,n1), (m2,n2), (m3,n3)
    # Z_3 maps each pair: (m,n) -> (-n, m-n)
    # A state is Z_3-invariant if the PRODUCT of three Z_3 phases = 1.

    # Actually, for spinors on the orbifold, the Z_3 action also involves
    # a phase from the spin structure. For the standard embedding:
    # the Z_3 phase on spinors is omega^{sum of weights}
    # For invariant states: sum of weights = 0 mod 3.

    # Let me count states more carefully.
    # Each (m,n) on T^2 has a Z_3 "charge" q defined by:
    # (m,n) -> omega^q * (m,n) ... no, the Z_3 acts geometrically, not by phase.
    # For SCALAR fields: invariance means the orbit averages to itself.
    # For the Dirac operator: need to account for the spinor Z_3 action.

    # For simplicity, count Z_3-invariant SCALAR modes first.
    # These are states where the 6D lattice vector is fixed by Z_3
    # (up to lattice translation), which means we average over the orbit.
    # The number of invariant states = (1/3)(total states + 2 * fixed states)
    # For the Dirac operator, there are additional selection rules from the
    # spin structure, but the COUNTING is similar.

    # Count total 6D lattice states up to eigenvalue lambda^2_max
    lam_max_sq = 100  # in units of (4/3)
    total_states = 0
    invariant_states = 0

    lattice_range = 8  # should be enough for norms up to ~100

    def z3_map(m, n):
        """Z_3 action on A_2 lattice: (m,n) -> (-n, m-n)"""
        return (-n, m - n)

    # Count states
    states_by_eigenvalue = {}

    for m1 in range(-lattice_range, lattice_range + 1):
        for n1 in range(-lattice_range, lattice_range + 1):
            N1 = m1**2 + n1**2 - m1 * n1
            if N1 > lam_max_sq:
                continue
            for m2 in range(-lattice_range, lattice_range + 1):
                for n2 in range(-lattice_range, lattice_range + 1):
                    N2 = m2**2 + n2**2 - m2 * n2
                    if N1 + N2 > lam_max_sq:
                        continue
                    for m3 in range(-lattice_range, lattice_range + 1):
                        for n3 in range(-lattice_range, lattice_range + 1):
                            N3 = m3**2 + n3**2 - m3 * n3
                            N_total = N1 + N2 + N3
                            if N_total > lam_max_sq or N_total == 0:
                                continue

                            total_states += 1

                            # Check Z_3 invariance:
                            # Apply Z_3 to all three pairs simultaneously
                            m1p, n1p = z3_map(m1, n1)
                            m2p, n2p = z3_map(m2, n2)
                            m3p, n3p = z3_map(m3, n3)

                            # State is invariant if it equals its Z_3 image
                            # (for scalars; Dirac has phase factors)
                            if (m1p == m1 and n1p == n1 and
                                m2p == m2 and n2p == n2 and
                                m3p == m3 and n3p == n3):
                                invariant_states += 1

                            # Count by eigenvalue
                            lam_sq = N_total
                            if lam_sq not in states_by_eigenvalue:
                                states_by_eigenvalue[lam_sq] = {"total": 0, "fixed": 0}
                            states_by_eigenvalue[lam_sq]["total"] += 1

                            if (m1p == m1 and n1p == n1 and
                                m2p == m2 and n2p == n2 and
                                m3p == m3 and n3p == n3):
                                states_by_eigenvalue[lam_sq]["fixed"] += 1

    # Invariant states by Burnside: N_inv = (1/3)(N_total + 2*N_fixed)
    N_inv_burnside = (total_states + 2 * invariant_states) // 3

    print(f"  Lattice range: [-{lattice_range}, {lattice_range}]")
    print(f"  Eigenvalue cutoff: N_total <= {lam_max_sq}")
    print(f"  Total 6D lattice states: {total_states}")
    print(f"  Z_3-fixed states: {invariant_states}")
    print(f"  Z_3-invariant (Burnside): {N_inv_burnside}")
    print(f"  Ratio (invariant/total): {N_inv_burnside/total_states:.4f}")
    print(f"  Expected ratio (1/3 + small correction): {1/3:.4f}")
    print()

    # Show the first few eigenvalue levels
    sorted_evals = sorted(states_by_eigenvalue.keys())[:15]
    print(f"  First 15 eigenvalue levels (lambda^2 in units of 4/3):")
    print(f"  {'N':>4s} | {'lambda^2':>10s} | {'total':>6s} | {'fixed':>6s} | {'orbifold':>8s}")
    print(f"  " + "-" * 48)
    cumul_total = 0
    cumul_inv = 0
    for N in sorted_evals:
        d = states_by_eigenvalue[N]
        n_inv = (d["total"] + 2 * d["fixed"]) // 3
        cumul_total += d["total"]
        cumul_inv += n_inv
        lam_sq = 4.0 * N / 3.0
        print(f"  {N:4d} | {lam_sq:10.3f} | {d['total']:6d} | {d['fixed']:6d} | {n_inv:8d}")

    print()
    print(f"  Cumulative (first 15 levels): {cumul_total} total, {cumul_inv} orbifold")
    print()

    # =================================================================
    # PART 8: WEYL'S LAW AND SPECTRAL DENSITY
    # =================================================================
    print("PART 8: SPECTRAL DENSITY AND S_RANDOM ESTIMATE")
    print("-" * 50)
    print()

    # Weyl's law for the Dirac operator on a 6D manifold:
    # N(Lambda) ~ Vol * Lambda^6 / (4pi)^3
    # For the orbifold: N_orb ~ (1/3) * Vol_torus * Lambda^6 / (4pi)^3
    # This gives the number of eigenvalues below Lambda.

    # The spectral density near the BARRIER (where chamber transitions happen)
    # determines how many eigenmodes are relevant for distinguishing chambers.
    #
    # The blow-up moduli mass m_v = 15.5 GeV sets the scale:
    # eigenmodes with lambda ~ m_v are the ones affected by the flop.

    print(f"  Blow-up mass: m_v = {m_v} GeV")
    print(f"  Eigenmode shift per flop: ~{Delta_lambda:.0f} GeV")
    print(f"  Number of eigenmodes affected by the n=9 flop: ~{n_shifting}")
    print()

    # For S_random in the continuous case:
    # If there are N_modes total eigenmodes below cutoff,
    # and 9 of them shift under the target flop,
    # then the probability that a random state overlaps with
    # exactly the right 9 modes is roughly (9/N_modes)^k for some k.
    #
    # But this is overcounting -- the discrete chamber structure
    # already captures the essential information. The continuous
    # refinement within a chamber adds a correction.

    # The main result is:
    print("  " + "=" * 50)
    print("  MAIN RESULT")
    print("  " + "=" * 50)
    print()
    print(f"  S_random = 1/{N_chambers} = {S_random:.6f}")
    print(f"  S_required > {S_required:.6f}")
    print(f"  Amplification: {amp:.0f}x")
    print()
    print(f"  Knowledge required:")
    print(f"    DISCRETE: All 9 Z_3-orbit flop directions ({int(bits)} bits)")
    print(f"    CONTINUOUS: V(tau) shape near target minimum")
    print(f"    PRECISION: < {Delta_lambda:.0f} GeV (to resolve flop vs no-flop)")
    print()
    print(f"  KEY INSIGHT: Spectral proximity is primarily TOPOLOGICAL.")
    print(f"  The observer must know the topology of the Kahler moduli")
    print(f"  space (which curves flop), not high-precision eigenvalues.")
    print(f"  9 bits of structural knowledge achieves S = 1.")
    print(f"  8/9 bits achieves only S = 0.5 (fails).")
    print()
    print(f"  SHARP THRESHOLD: There is NO smooth gradient.")
    print(f"  Either you know all 9 orbit directions or you don't.")
    print(f"  This is a consequence of the discrete chamber structure")
    print(f"  of the Kahler moduli space.")
    print()

    # =================================================================
    # PART 9: IMPLICATIONS
    # =================================================================
    print("PART 9: IMPLICATIONS FOR THE EXPERIMENT")
    print("-" * 50)
    print()

    print("  1. OPERATOR TRAINING is discrete, not continuous.")
    print("     The operator must learn 9 specific geometric facts,")
    print("     not achieve arbitrary numerical precision.")
    print()
    print("  2. The 2x2 FACTORIAL can test this:")
    print("     'Knowledge' in the experiment means: does the operator")
    print("     know which 9 exceptional divisors correspond to the")
    print("     target transition? This is a finite, teachable set of facts.")
    print()
    print("  3. WITHIN-SUBJECT prediction:")
    print("     Before learning: S ~ 0 (operator cannot identify target)")
    print("     After learning all 9 orbits: S -> 1 (sudden jump)")
    print("     This predicts a STEP FUNCTION, not a gradual improvement.")
    print()
    print("  4. FALSIFICATION:")
    print("     If the effect increases GRADUALLY with partial knowledge")
    print("     (e.g., knowing 5/9 orbits gives intermediate coupling),")
    print("     the discrete chamber model is WRONG.")
    print("     Gradual improvement would favor a continuous coupling model.")
    print()

    # Circularity check
    print("  5. CIRCULARITY STATUS (from peer review):")
    print("     This computation does NOT break the circularity flagged in")
    print("     Section 5.3 of the Level 3 document. The chamber counting")
    print("     gives S_random and the amplification needed, which are")
    print("     properties of the GEOMETRY (model-independent).")
    print("     But the claim that 'structural knowledge -> S = 1' still")
    print("     PRESUPPOSES Model C. The experiment tests this claim.")
    print()

    print("=" * 70)
    print("COMPUTATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
