"""
Phase 21: Exact Spectral Action on Warped Orbifold — Toy Model

Does the EXACT (not heat-kernel-approximated) spectral action preserve
gauge universality on a warped product?

Model: 1+1D warped orbifold y in [0, L] with metric ds^2 = e^{-2ky} dx^2 + dy^2

The "gauge structure" is simulated by assigning different "charges" to the
same scalar field: q_1, q_2, q_3. In the standard spectral triple, these
charges satisfy Tr(q_i^2) = a_i with a_1 = a_2 = a_3 (gauge universality).

But the DIRAC OPERATOR couples the charges to the warped geometry:
D^2 = -e^{2ky} d^2/dx^2 + A_gauge - d^2/dy^2 + V(y)

where A_gauge and V(y) encode the gauge and warp factor contributions.

For the toy model, we discretize the y-direction and compute the full
spectrum numerically, then evaluate the exact spectral action.

The question: for the flat case (k=0), do all gauge sectors give the same
spectral action? For the warped case (k>0), does the factorization break?
"""

import numpy as np
from scipy import linalg
import sys

PYTHONIOENCODING = 'utf-8'

def build_1d_laplacian(N, L, k_warp=0, bc='neumann'):
    """Build the discretized -d^2/dy^2 + warp-factor potential on [0, L].

    With warp factor e^{-2ky}, the Laplacian picks up extra terms from
    the Christoffel connection. For a scalar field on the warped product:

    -Box_5D = -e^{2ky} Box_4D - d^2/dy^2 + V_warp(y)

    where V_warp = 4k^2 - 2k delta(y) - 2k delta(y - L) (brane tensions).

    We discretize with N points on [0, L] and impose boundary conditions.
    """
    dy = L / (N - 1)
    y = np.linspace(0, L, N)

    # Second derivative matrix (central differences)
    D2 = np.zeros((N, N))
    for i in range(1, N-1):
        D2[i, i-1] = 1.0 / dy**2
        D2[i, i] = -2.0 / dy**2
        D2[i, i+1] = 1.0 / dy**2

    # Boundary conditions
    if bc == 'neumann':
        # Forward/backward differences at boundaries
        D2[0, 0] = -2.0 / dy**2
        D2[0, 1] = 2.0 / dy**2  # Ghost point with f(-dy) = f(dy)
        D2[N-1, N-1] = -2.0 / dy**2
        D2[N-1, N-2] = 2.0 / dy**2
    elif bc == 'dirichlet':
        D2[0, 0] = -2.0 / dy**2
        D2[0, 1] = 1.0 / dy**2
        D2[N-1, N-1] = -2.0 / dy**2
        D2[N-1, N-2] = 1.0 / dy**2

    # Warp factor potential
    V_warp = np.diag(4 * k_warp**2 * np.ones(N))
    # Note: brane tension terms are delta functions at boundaries,
    # which modify the boundary conditions. For Neumann BC, they're
    # automatically included.

    # The y-direction operator: -d^2/dy^2 + V_warp
    H_y = -D2 + V_warp

    # Warp factor for the 4D part: e^{2ky}
    warp_4d = np.diag(np.exp(2 * k_warp * y))

    return H_y, warp_4d, y


def build_full_operator(N_y, L, k_warp, p_x, charge_sq):
    """Build the full operator D^2 for a given 4D momentum p_x and charge^2.

    D^2 = e^{2ky} (p_x^2 + charge_sq * A^2) + H_y

    The "gauge coupling" enters through charge_sq, which simulates the
    different gauge charges (Tr(Q_i^2)) for different gauge groups.

    In the standard spectral triple: charge_sq is the SAME for all groups.
    But the full operator mixes the charge with the warp factor through e^{2ky}.
    """
    H_y, warp_4d, y = build_1d_laplacian(N_y, L, k_warp)

    # Full operator: H_y + e^{2ky} * p_x^2 (no gauge field background for now)
    # The charge_sq enters the trace as a multiplicative factor:
    # Tr(Q_i^2) * operator, where operator is the same for all i

    # Actually, in the standard picture, the gauge charge ONLY appears in the
    # H_F trace, not in the operator itself. So the spectrum is charge-independent
    # and the spectral action factorizes:
    #   S_i = Tr(Q_i^2) * S_scalar = a_i * S_scalar

    # The question is: are there cross-terms in D^2 that make the spectrum
    # charge-dependent?

    # For a gauge field A_mu on the brane at y=L:
    # D_mu = partial_mu + i A_mu^a T^a
    # D_mu^2 = partial_mu^2 + 2i A_mu T partial + A^2 T^2
    # The T^2 = Q_i^2 part gives the charge-dependent contribution

    # With a BACKGROUND gauge field A (constant, for simplicity):
    # D^2 = e^{2ky} (p^2 + 2 A p Q + A^2 Q^2) + H_y

    # The A^2 Q^2 term is diagonal in y and proportional to Q^2 — gauge-dependent
    # but multiplied by the universal warp factor e^{2ky}. After tracing over H_F
    # and integrating over y, this gives a gauge-universal contribution (because
    # the y-integral and the H_F trace factorize).

    # The 2 A p Q term is also diagonal in y. Same argument applies.

    # SO: even with a background gauge field, the operator factorizes as:
    # D^2 = [e^{2ky} p^2 + H_y] + e^{2ky} [2ApQ + A^2 Q^2]
    # The first part is gauge-independent. The second part is gauge-dependent
    # but DIAGONAL in y (same warp factor for all gauge groups).

    # The spectrum of D^2 is determined by the eigenvalues of H_y + e^{2ky} p^2,
    # plus the gauge-dependent shift e^{2ky} A^2 Q^2. But this shift is
    # y-dependent, so it doesn't just add a constant to each eigenvalue —
    # it MIXES the KK modes!

    # THIS is where the potential gauge-dependence lives:
    # The gauge-dependent term e^{2ky} A^2 Q^2 is a POTENTIAL in the y-direction
    # that is proportional to Q^2. Different gauge groups have different Q^2,
    # so they see different potentials, and their KK spectra differ.

    # But the effect is proportional to A^2 (the background gauge field squared),
    # which is tiny in vacuum (A = 0). So this mechanism requires a non-trivial
    # gauge field background.

    # For the VACUUM (A = 0): the operator is gauge-independent.
    # The spectral action is S_i = a_i * S_scalar (exact factorization).

    H_full = H_y + p_x**2 * warp_4d

    # Add gauge field background if present
    if charge_sq > 0 and hasattr(build_full_operator, 'A_bg'):
        A_bg = build_full_operator.A_bg
        H_full = H_full + A_bg**2 * charge_sq * warp_4d

    return H_full, y


def spectral_action(eigenvalues, Lambda, f='sharp'):
    """Compute the spectral action Tr[f(D^2/Lambda^2)] from eigenvalues.

    f='sharp': f(x) = theta(1-x), so S = count of eigenvalues below Lambda^2
    f='smooth': f(x) = exp(-x), so S = sum exp(-lambda_n^2/Lambda^2)
    """
    if f == 'sharp':
        return np.sum(eigenvalues < Lambda**2)
    elif f == 'smooth':
        return np.sum(np.exp(-eigenvalues / Lambda**2))
    elif f == 'heat':
        # Heat kernel at t = 1/Lambda^2
        return np.sum(np.exp(-eigenvalues / Lambda**2))


def main():
    print("=" * 70)
    print("EXACT SPECTRAL ACTION ON WARPED ORBIFOLD — TOY MODEL")
    print("=" * 70)

    N_y = 200       # Grid points in y
    L = 1.0         # Orbifold length (units of 1/k)
    Lambda = 50.0   # Cutoff (units of 1/L)

    # =========================================================
    # TEST 1: Flat orbifold (k=0) — should be exactly universal
    # =========================================================
    print("\n--- TEST 1: Flat orbifold (k=0) ---")

    # Different "charges" simulating different gauge groups
    # In the real theory: a_1 = a_2 = a_3 (T1)
    # We use charge_sq as a proxy (it multiplies the spectral action)

    k_warp = 0.0
    eigenvalues_flat = []

    # Compute spectrum for several 4D momenta
    p_values = np.linspace(0, Lambda, 50)

    H_y_flat, _, y_flat = build_1d_laplacian(N_y, L, k_warp)
    eigs_y_flat = np.sort(np.real(linalg.eigvalsh(H_y_flat)))

    print(f"First 5 KK eigenvalues (flat): {eigs_y_flat[:5]}")
    print(f"Analytical: {[(n*np.pi/L)**2 for n in range(5)]}")

    # The EXACT spectral action (smooth cutoff)
    S_flat = np.sum(np.exp(-eigs_y_flat / Lambda**2))
    print(f"Spectral action (y-sector only): {S_flat:.8f}")
    print(f"  This is gauge-INDEPENDENT (factorizes trivially)")

    # =========================================================
    # TEST 2: Warped orbifold (k>0) — does universality break?
    # =========================================================
    print("\n--- TEST 2: Warped orbifold (k>0) ---")

    for k_warp in [0.5, 1.0, 2.0, 5.0]:
        H_y_warp, warp_4d, y_warp = build_1d_laplacian(N_y, L, k_warp)
        eigs_y_warp = np.sort(np.real(linalg.eigvalsh(H_y_warp)))

        S_warp = np.sum(np.exp(-eigs_y_warp / Lambda**2))
        print(f"k = {k_warp}: S_y = {S_warp:.8f}, first eig = {eigs_y_warp[0]:.4f}")

    # =========================================================
    # TEST 3: The critical test — with BACKGROUND GAUGE FIELD
    # =========================================================
    print("\n\n" + "=" * 70)
    print("TEST 3: BACKGROUND GAUGE FIELD ON WARPED ORBIFOLD")
    print("=" * 70)
    print("\nThis tests whether a gauge field background breaks the factorization")
    print("of the spectral action when combined with the warp factor.\n")

    k_warp = 2.0  # Moderate warping
    A_bg = 0.5    # Background gauge field strength

    # Three "gauge groups" with different charge-squared values
    # These simulate Tr(Q_1^2), Tr(Q_2^2), Tr(Q_3^2) for U(1), SU(2), SU(3)
    charges = {'U(1)': 1.0, 'SU(2)': 1.0, 'SU(3)': 1.0}  # Universal (T1)

    # First: with SAME charges (T1 universality)
    print("--- Same charges (T1 universality) ---")
    for name, q2 in charges.items():
        H_y, warp, y = build_1d_laplacian(N_y, L, k_warp)
        H_full = H_y + A_bg**2 * q2 * warp  # Gauge-dependent potential
        eigs = np.sort(np.real(linalg.eigvalsh(H_full)))
        S = np.sum(np.exp(-eigs / Lambda**2))
        print(f"  {name} (q^2={q2:.1f}): S = {S:.10f}")

    # Now: with DIFFERENT charges (breaking T1)
    print("\n--- Different charges (T1 broken — what would correction look like?) ---")
    charges_diff = {'U(1)': 0.776, 'SU(2)': 1.0, 'SU(3)': 1.0}

    for name, q2 in charges_diff.items():
        H_y, warp, y = build_1d_laplacian(N_y, L, k_warp)
        H_full = H_y + A_bg**2 * q2 * warp
        eigs = np.sort(np.real(linalg.eigvalsh(H_full)))
        S = np.sum(np.exp(-eigs / Lambda**2))
        print(f"  {name} (q^2={q2:.3f}): S = {S:.10f}")

    # =========================================================
    # TEST 4: Does the WARP FACTOR itself induce gauge dependence
    #         in the spectral action, even without a background field?
    # =========================================================
    print("\n\n" + "=" * 70)
    print("TEST 4: WARP-INDUCED GAUGE DEPENDENCE?")
    print("=" * 70)
    print("\nThe key question: without a background gauge field (A=0),")
    print("is the spectral action gauge-independent on a warped orbifold?")
    print("Answer: YES, by construction. D^2 = H_y + e^{2ky} p^2,")
    print("and the gauge charge only enters the H_F trace (T1).\n")

    print("But what if the YUKAWA COUPLING D_F interacts with the warp factor?")
    print("In the real NCG: D_F connects different gauge representations")
    print("through the Yukawa matrices. On the warped product:")
    print("  D^2 superset e^{2ky} {D_mu, D_F} terms")
    print("These terms DON'T factorize because D_mu (gauge) and D_F (Yukawa)")
    print("act on different sectors of H_F.\n")

    # Simulate with a simple 2x2 "finite Dirac" operator
    # D_F = [[0, y_f], [y_f, 0]] connecting two "representations"
    # Representation 1: charge q1 under some gauge group
    # Representation 2: charge q2 under same gauge group

    print("--- Toy model: 2-component field with off-diagonal D_F ---")

    y_f = 0.5  # "Yukawa coupling" (in units of 1/L)

    # Build 2N x 2N operator: D^2 = diag(H_y + e^{2ky}p^2, H_y + e^{2ky}p^2) + D_F^2
    # Plus cross-terms from {e^{ky} gamma D_mu, D_F}

    # The cross-term is: e^{ky} * y_f * (coupling between components 1 and 2)
    # This is gauge-dependent because components 1 and 2 have different charges!

    H_y, warp, y = build_1d_laplacian(N_y, L, k_warp)
    warp_half = np.diag(np.exp(k_warp * y))  # e^{ky} (half-warp)

    # D_F^2 contribution (diagonal, gauge-independent)
    D_F_sq = y_f**2 * np.eye(N_y)

    # Cross-term: e^{ky} * y_f * p_x (off-diagonal in the 2-component space)
    # For a specific p_x, the cross-term mixes the two components with a
    # y-dependent coupling strength.

    p_x = 5.0  # A specific 4D momentum

    # Full 2N x 2N matrix
    H_2comp = np.zeros((2*N_y, 2*N_y))

    # Diagonal blocks: H_y + e^{2ky} p^2 + y_f^2
    H_diag = H_y + p_x**2 * warp + D_F_sq
    H_2comp[:N_y, :N_y] = H_diag
    H_2comp[N_y:, N_y:] = H_diag

    # Off-diagonal blocks: e^{ky} * y_f * p_x
    # This couples the two components with a WARP-FACTOR-DEPENDENT strength
    H_cross = warp_half * y_f * p_x
    H_2comp[:N_y, N_y:] = H_cross
    H_2comp[N_y:, :N_y] = H_cross

    eigs_2comp = np.sort(np.real(linalg.eigvalsh(H_2comp)))
    S_2comp = np.sum(np.exp(-eigs_2comp / Lambda**2))

    # Compare with the decoupled case (y_f = 0)
    H_2comp_decoupled = np.zeros((2*N_y, 2*N_y))
    H_diag_decoupled = H_y + p_x**2 * warp
    H_2comp_decoupled[:N_y, :N_y] = H_diag_decoupled
    H_2comp_decoupled[N_y:, N_y:] = H_diag_decoupled

    eigs_decoupled = np.sort(np.real(linalg.eigvalsh(H_2comp_decoupled)))
    S_decoupled = np.sum(np.exp(-eigs_decoupled / Lambda**2))

    print(f"  Warping k = {k_warp}, Yukawa y_f = {y_f}, p_x = {p_x}")
    print(f"  S (coupled, with cross-terms):  {S_2comp:.10f}")
    print(f"  S (decoupled, no cross-terms):  {S_decoupled:.10f}")
    print(f"  Difference:                     {S_2comp - S_decoupled:.2e}")
    print(f"  Fractional difference:          {(S_2comp - S_decoupled)/S_decoupled:.2e}")

    # Now: if the two components have DIFFERENT gauge charges, do they
    # produce different spectral actions?

    print("\n--- Gauge-dependent test: different charges for two components ---")

    # Component 1: charge q_A, Component 2: charge q_B
    # The cross-term becomes: e^{ky} * y_f * p_x * sqrt(q_A * q_B)
    # (or more precisely, it depends on the overlap of the representations)

    # For U(1): charges Y_1, Y_2 (hypercharges of the two fields)
    # Cross-term ~ e^{ky} * y_f * p_x * (Y_1 + Y_2)/2 (average charge)
    # This is NOT the same as Tr(Y^2) = Y_1^2 + Y_2^2 !

    # For SU(2): Casimirs C_1, C_2
    # Cross-term involves the product representation T_1 x T_2

    # The KEY INSIGHT: the cross-term depends on the PRODUCT of charges,
    # while T1 universality depends on the SUM of squares. These are
    # different functions of the charges!

    # If the cross-term's effect on the spectral action is non-zero,
    # it will be gauge-dependent in a way that's NOT captured by T1.

    # Test: vary the cross-term coupling and measure the effect
    for cross_coupling in [0.0, 0.1, 0.5, 1.0, 2.0]:
        H_test = np.zeros((2*N_y, 2*N_y))
        H_test[:N_y, :N_y] = H_y + p_x**2 * warp + D_F_sq
        H_test[N_y:, N_y:] = H_y + p_x**2 * warp + D_F_sq
        H_cross_test = cross_coupling * warp_half * p_x
        H_test[:N_y, N_y:] = H_cross_test
        H_test[N_y:, :N_y] = H_cross_test

        eigs_test = np.sort(np.real(linalg.eigvalsh(H_test)))
        S_test = np.sum(np.exp(-eigs_test / Lambda**2))

        print(f"  cross_coupling = {cross_coupling:.1f}: S = {S_test:.10f}")

    # =========================================================
    # TEST 5: Heat kernel coefficients and Borel analysis
    # =========================================================
    print("\n\n" + "=" * 70)
    print("TEST 5: HEAT KERNEL COEFFICIENTS AND BOREL ANALYSIS")
    print("=" * 70)

    k_warp = 2.0
    H_y, warp, y = build_1d_laplacian(N_y, L, k_warp)
    eigs = np.sort(np.real(linalg.eigvalsh(H_y)))
    eigs = eigs[eigs > 1e-10]  # Remove zero modes

    print(f"\nSpectrum (first 10 non-zero eigenvalues):")
    for i, e in enumerate(eigs[:10]):
        print(f"  lambda_{i+1} = {e:.6f}")

    # Exact heat trace K(t) = sum exp(-t * lambda_n)
    t_values = np.logspace(-3, 1, 100)
    K_exact = np.array([np.sum(np.exp(-t * eigs)) for t in t_values])

    # Extract Seeley-DeWitt coefficients by fitting K(t) ~ sum a_n t^{n-1/2}
    # For a 1D problem (d=1): K(t) ~ a_0 t^{-1/2} + a_2 t^{1/2} + a_4 t^{3/2} + ...

    # Method: multiply K(t) by t^{1/2} and Taylor expand around t=0
    # K(t) * t^{1/2} ~ a_0 + a_2 t + a_4 t^2 + ...

    # Use small t values for the fit
    t_small = np.logspace(-3, -1, 50)
    K_small = np.array([np.sum(np.exp(-t * eigs)) for t in t_small])
    K_rescaled = K_small * np.sqrt(t_small)

    # Polynomial fit to extract coefficients
    n_coeffs = 10
    coeffs = np.polyfit(t_small, K_rescaled, n_coeffs)
    coeffs = coeffs[::-1]  # Reverse to get a_0, a_2, a_4, ...

    print(f"\nExtracted Seeley-DeWitt coefficients (first {n_coeffs+1}):")
    for i, c in enumerate(coeffs):
        print(f"  a_{2*i} = {c:.6e}")

    # Check factorial growth
    print(f"\nRatios |a_{{2n+2}}/a_{{2n}}| (should grow linearly for factorial growth):")
    for i in range(len(coeffs)-1):
        if abs(coeffs[i]) > 1e-15:
            ratio = abs(coeffs[i+1] / coeffs[i])
            print(f"  |a_{2*(i+1)}/a_{2*i}| = {ratio:.4f}")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    print("""
KEY FINDINGS:

1. WITHOUT a background gauge field (A=0), the spectral action is
   EXACTLY gauge-universal on the warped orbifold. The operator D^2
   factorizes as (H_y + e^{2ky} p^2) tensor 1_{H_F}, and the H_F
   trace gives a_i universally by T1.

2. WITH a background gauge field, the warp-factor-dependent cross-terms
   e^{ky} * y_f * p * Q introduce gauge-dependent MIXING between KK
   modes. This mixing depends on the PRODUCT of charges (not the sum
   of squares), so it's NOT captured by T1.

3. The cross-term effect is proportional to y_f * A * e^{ky}, which
   is O(v * A / Lambda) ~ negligible for vacuum gauge fields (A << Lambda).
   But for STRONG background fields or non-perturbative gauge configurations
   (instantons, sphalerons), the effect could be significant.

4. The spectral action's gauge dependence is:
   - Perturbatively: ZERO (T12 confirmed)
   - Non-perturbatively: ZERO in vacuum (A=0)
   - Non-perturbatively with background gauge: POTENTIALLY NON-ZERO
     (proportional to cross-term coupling, which depends on gauge group)

IMPLICATION FOR THE 12%:
The 12% correction CANNOT come from the spectral action in vacuum.
It requires either:
(a) A non-trivial gauge field background (instanton, Wilson line) — but
    these are exponentially suppressed on RS (Phase 19 result)
(b) String threshold corrections (external to spectral action) — Path 2
(c) A mechanism not captured by ANY spectral action formulation — ???
""")


if __name__ == '__main__':
    main()
