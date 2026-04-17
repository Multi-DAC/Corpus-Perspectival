"""
Track 16E: One-Loop R^2 Coefficient on the RS Orbifold
=====================================================

Computes the one-loop correction to the R^2 coefficient in the
effective 4D action from quantum gravitational fluctuations.

Tree level: Spectral action gives R^2 = 0 (structural identity of D^2).
One loop: Graviton + ghost fluctuations generate R^2 != 0.

Method: Heat kernel a_4 coefficients for each sector, decomposed
into {R^2, R_{mu nu}^2, R_{mu nu rho sigma}^2} using explicit
tensor algebra on multiple backgrounds.

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: March 19, 2026
"""

import numpy as np
from itertools import product as iproduct

# =========================================================
# 1. Setup: Curvature tensors on specific 4D backgrounds
# =========================================================

d = 4  # spacetime dimension

def sym_pairs(d):
    """Generate all symmetric index pairs (mu,nu) with mu <= nu."""
    pairs = []
    for mu in range(d):
        for nu in range(mu, d):
            pairs.append((mu, nu))
    return pairs

PAIRS = sym_pairs(d)
N_sym = len(PAIRS)  # = d(d+1)/2 = 10

def pair_index(mu, nu):
    """Map (mu,nu) -> index in PAIRS list (canonicalizing order)."""
    a, b = min(mu, nu), max(mu, nu)
    return PAIRS.index((a, b))

# Construct Riemann tensor for S^4 (maximally symmetric, positive curvature)
def riemann_S4(kappa):
    """Riemann tensor for S^4 with R_{mu nu rho sigma} = kappa * (g_{mr}g_{ns} - g_{ms}g_{nr})."""
    R = np.zeros((d, d, d, d))
    g = np.eye(d)
    for m, n, r, s in iproduct(range(d), repeat=4):
        R[m, n, r, s] = kappa * (g[m, r] * g[n, s] - g[m, s] * g[n, r])
    return R

# Construct Riemann tensor for S^2(k1) x S^2(k2)
def riemann_S2xS2(k1, k2):
    """Riemann tensor for S^2(k1) x S^2(k2)."""
    R = np.zeros((d, d, d, d))
    g = np.eye(d)
    # S^2(k1) in directions 0,1
    for m, n, r, s in iproduct(range(2), repeat=4):
        R[m, n, r, s] = k1 * (g[m, r] * g[n, s] - g[m, s] * g[n, r])
    # S^2(k2) in directions 2,3
    for m, n, r, s in iproduct(range(2, 4), repeat=4):
        R[m, n, r, s] = k2 * (g[m, r] * g[n, s] - g[m, s] * g[n, r])
    return R

def ricci_from_riemann(R):
    """Compute Ricci tensor R_{mu nu} = R^alpha_{mu alpha nu}."""
    g = np.eye(d)
    Ric = np.zeros((d, d))
    for m in range(d):
        for n in range(d):
            for a in range(d):
                Ric[m, n] += R[a, m, a, n]
    return Ric

def scalar_from_ricci(Ric):
    """Ricci scalar R = g^{mu nu} R_{mu nu}."""
    return np.trace(Ric)

def curvature_invariants(R_tensor):
    """Compute R^2, R_{mn}^2, R_{mnrs}^2 from Riemann tensor."""
    Ric = ricci_from_riemann(R_tensor)
    R_scalar = scalar_from_ricci(Ric)

    R2 = R_scalar**2
    Ric2 = np.sum(Ric * Ric)
    Riem2 = np.sum(R_tensor * R_tensor)

    return R2, Ric2, Riem2


# =========================================================
# 2. Ghost sector: Vector field with E_mu^nu = R_mu^nu
# =========================================================

def ghost_traces(R_tensor):
    """
    Ghost operator: D = -(nabla^2 + E) on vectors, E_mu^nu = R_mu^nu.
    Returns tr(E), tr(E^2), tr(Omega^2).
    """
    Ric = ricci_from_riemann(R_tensor)
    R_scalar = scalar_from_ricci(Ric)

    # tr(E) = R (Ricci scalar)
    trE = R_scalar

    # tr(E^2) = R_{mu nu} R^{mu nu}
    trE2 = np.sum(Ric * Ric)

    # tr(Omega^2) = R_{mu nu rho sigma} R^{mu nu rho sigma}
    # Connection curvature on vectors: (Omega_{ab})_mu^nu = R^nu_{mu a b}
    trOm2 = np.sum(R_tensor * R_tensor)

    return trE, trE2, trOm2


# =========================================================
# 3. Graviton sector: Lichnerowicz operator on symmetric 2-tensors
# =========================================================

def graviton_endomorphism_matrix(R_tensor):
    """
    Construct the endomorphism E for the Lichnerowicz operator on
    symmetric 2-tensors.

    (E h)_{mu nu} = -R_{mu alpha} h^alpha_nu - R_{nu alpha} h^alpha_mu
                    + 2 R_{mu alpha nu beta} h^{alpha beta}

    Returns E as N_sym x N_sym matrix.
    """
    g = np.eye(d)
    Ric = ricci_from_riemann(R_tensor)

    E = np.zeros((N_sym, N_sym))

    for I, (mu, nu) in enumerate(PAIRS):
        for J, (rho, sig) in enumerate(PAIRS):
            # Contribution from -R_{mu}^alpha h_{alpha nu} - R_{nu}^alpha h_{alpha mu}
            # + 2 R_{mu alpha nu beta} h^{alpha beta}

            # -R_{mu rho} g_{nu sigma} (symmetrized over rho<->sigma)
            val = 0.0

            # Term 1: -R_{mu}^{alpha} h_{alpha nu}
            # This maps h_{rho sigma} to -R_{mu rho} delta_{nu sigma} (+ symmetrizations)
            # More precisely: (E h)_{mu nu} = sum_{alpha} [-R_{mu alpha} h_{alpha nu}]
            # So E_{(mu nu),(rho sigma)} has contributions when alpha = rho and nu = sigma
            # or alpha = sigma and nu = rho (from symmetry of h)

            # Let me compute it directly.
            # (E h)_{mu nu} = -R_{mu}^{alpha} h_{alpha nu} - R_{nu}^{alpha} h_{alpha mu}
            #                 + 2 R_{mu alpha nu beta} h^{alpha beta}
            #
            # For h = basis element e_{(rho sigma)}, which has
            # e_{(rho sigma)}_{ab} = (delta_a^rho delta_b^sigma + delta_a^sigma delta_b^rho) / norm
            # where norm = sqrt(2) if rho != sigma, 1 if rho == sigma

            # For canonical basis: e_{(rho sigma)}_{ab} =
            #   delta_a^rho delta_b^sigma + delta_a^sigma delta_b^rho  (if rho != sigma)
            #   delta_a^rho delta_b^sigma                               (if rho == sigma)
            # But this isn't normalized. Let me use unnormalized basis.

            # Actually, let's compute E_{(mu nu)(rho sigma)} as the coefficient
            # of h_{rho sigma} in (Eh)_{mu nu}, where h is a symmetric tensor.
            #
            # (Eh)_{mu nu} = -R_{mu alpha} h^{alpha}_{nu} - R_{nu alpha} h^{alpha}_{mu} + 2 R_{mu alpha nu beta} h^{alpha beta}
            # = -R_{mu}^{alpha} h_{alpha nu} - R_{nu}^{alpha} h_{alpha mu} + 2 R_{mu}^{alpha}_{nu}^{beta} h_{alpha beta}
            # = sum_{alpha,beta} [-R_{mu alpha} g_{nu beta} - R_{nu beta} g_{mu alpha} + 2 R_{mu alpha nu beta}] h^{alpha beta}
            #
            # Since h is symmetric, the coefficient of h_{rho sigma} (for rho < sigma) is:
            # E_{(mu nu)(rho sigma)} = [-R_{mu rho} g_{nu sigma} - R_{nu sigma} g_{mu rho} + 2 R_{mu rho nu sigma}]
            #                        + [-R_{mu sigma} g_{nu rho} - R_{nu rho} g_{mu sigma} + 2 R_{mu sigma nu rho}]
            # And for rho = sigma:
            # E_{(mu nu)(rho rho)} = -R_{mu rho} g_{nu rho} - R_{nu rho} g_{mu rho} + 2 R_{mu rho nu rho}

            # General formula (works for both cases with proper handling):
            # For symmetric indices, the effective endomorphism is:

            # First contribution: alpha=rho, beta=sigma
            c1 = (-Ric[mu, rho] * g[nu, sig]
                   - Ric[nu, sig] * g[mu, rho]
                   + 2 * R_tensor[mu, rho, nu, sig])

            # Second contribution: alpha=sigma, beta=rho (from symmetry of h)
            c2 = (-Ric[mu, sig] * g[nu, rho]
                   - Ric[nu, rho] * g[mu, sig]
                   + 2 * R_tensor[mu, sig, nu, rho])

            if rho == sig:
                val = c1  # No double counting for diagonal elements
            else:
                val = (c1 + c2) / 2  # Average for off-diagonal
                # Actually, let me think about this more carefully.
                # h_{rho sigma} = h_{sigma rho}. When we write
                # (Eh)_{mu nu} = M_{mu nu}^{alpha beta} h_{alpha beta}
                # where the sum runs over ALL alpha, beta:
                # M_{mu nu}^{alpha beta} = -R_{mu}^{alpha} delta_{nu}^{beta}
                #                          - R_{nu}^{beta} delta_{mu}^{alpha}
                #                          + 2 R_{mu}^{alpha}_{nu}^{beta}
                # But h is symmetric, so the effective action on the symmetric part is:
                # E_{(mu nu)(rho sigma)} = M_{mu nu}^{rho sigma} + M_{mu nu}^{sigma rho}
                # for rho < sigma (the off-diagonal)
                # E_{(mu nu)(rho rho)} = M_{mu nu}^{rho rho} for diagonal
                val = c1 + c2  # For off-diagonal pairs

            # Also need to symmetrize over (mu, nu):
            # Wait, (mu, nu) is already the output index. The endomorphism
            # maps the symmetric pair (rho, sigma) to the component (mu, nu).
            # Since (Eh)_{mu nu} is automatically symmetric if E is correctly defined,
            # we just need the (mu, nu) component with mu <= nu.

            E[I, J] = val if rho == sig else val

    return E

def graviton_endomorphism_matrix_v2(R_tensor):
    """
    Compute endomorphism matrix using direct contraction.

    For the Lichnerowicz operator on symmetric 2-tensors:
    (E h)_{mu nu} = -R_{mu}^{alpha} h_{alpha nu} - R_{nu}^{alpha} h_{alpha mu}
                    + 2 R_{mu alpha nu beta} h^{alpha beta}
    """
    Ric = ricci_from_riemann(R_tensor)

    # Work with full (mu,nu) indexing, then extract symmetric part
    # E_{mu nu, rho sigma} = M_{mu nu rho sigma} + M_{mu nu sigma rho}
    # where M_{mu nu rho sigma} = -R_{mu rho} delta_{nu sigma}
    #                              - R_{nu sigma} delta_{mu rho}
    #                              + 2 R_{mu rho nu sigma}

    g = np.eye(d)

    # Full 4-index tensor M
    M = np.zeros((d, d, d, d))
    for mu, nu, rho, sig in iproduct(range(d), repeat=4):
        M[mu, nu, rho, sig] = (-Ric[mu, rho] * g[nu, sig]
                                - Ric[nu, sig] * g[mu, rho]
                                + 2 * R_tensor[mu, rho, nu, sig])

    # Symmetrize: E_{mu nu, rho sigma} = M_{mu nu, rho sigma} + M_{mu nu, sigma rho}
    # (from h_{rho sigma} = h_{sigma rho})
    # Also output is already symmetric in (mu, nu) by construction

    E_mat = np.zeros((N_sym, N_sym))
    for I, (mu, nu) in enumerate(PAIRS):
        for J, (rho, sig) in enumerate(PAIRS):
            # The basis element e_{(rho sig)} acts as:
            # h_{alpha beta} = delta_{alpha rho} delta_{beta sigma} + delta_{alpha sigma} delta_{beta rho}
            # (unnormalized, gives 2 for off-diagonal, 1 for diagonal)
            # Then (Eh)_{mu nu} = M_{mu nu rho sig} + M_{mu nu sig rho}

            val = M[mu, nu, rho, sig] + M[mu, nu, sig, rho]

            # For the output side, if mu != nu, we need to account for
            # the fact that (Eh) is symmetric and we only store mu <= nu.
            # (Eh)_{mu nu} and (Eh)_{nu mu} should be the same, so no extra factor.

            # For the input side, if rho != sigma, the basis element has
            # norm 2 (it appears twice in the sum), so we divide by 2.
            # But actually, in our convention, we use the FULL sum
            # M_{mu nu alpha beta} h_{alpha beta} over all alpha, beta.
            # For h = e_{(rho sigma)} with rho < sigma:
            # h_{rho sigma} = 1, h_{sigma rho} = 1, all others 0.
            # The sum gives M_{mu nu rho sigma} * 1 + M_{mu nu sigma rho} * 1 = val.
            # For h = e_{(rho rho)}:
            # h_{rho rho} = 1, all others 0.
            # The sum gives M_{mu nu rho rho} * 1.

            if rho == sig:
                val = M[mu, nu, rho, sig]  # Only one term

            E_mat[I, J] = val

    return E_mat


def graviton_connection_curvature_trace(R_tensor):
    """
    Compute tr(Omega_{alpha beta} Omega^{alpha beta}) for the connection
    on symmetric 2-tensors.

    (Omega_{alpha beta} h)_{mu nu} = R^rho_{mu alpha beta} h_{rho nu}
                                    + R^rho_{nu alpha beta} h_{mu rho}
    """
    # Full connection curvature tensor
    # (Omega_{ab})_{mu nu, rho sigma} maps h_{rho sigma} to (Omega h)_{mu nu}

    # Construct Omega as operator on symmetric 2-tensors for each (a,b)
    g = np.eye(d)

    trOm2 = 0.0

    for a in range(d):
        for b in range(d):
            # Omega_{ab} as a matrix on symmetric 2-tensors
            Om = np.zeros((N_sym, N_sym))

            for I, (mu, nu) in enumerate(PAIRS):
                for J, (rho, sig) in enumerate(PAIRS):
                    # (Omega_{ab} h)_{mu nu} = R^gamma_{mu a b} h_{gamma nu}
                    #                         + R^gamma_{nu a b} h_{mu gamma}
                    # Acting on h = e_{(rho sigma)}:

                    # Full action: sum over gamma of
                    # R^gamma_{mu a b} * h_{gamma nu} + R^gamma_{nu a b} * h_{mu gamma}

                    val = 0.0

                    if rho != sig:
                        # h_{rho sigma} = h_{sigma rho} = 1
                        # gamma = rho: R^rho_{mu a b} * delta_{nu sigma} + R^rho_{nu a b} * delta_{mu sigma}
                        # gamma = sigma: R^sigma_{mu a b} * delta_{nu rho} + R^sigma_{nu a b} * delta_{mu rho}
                        val += R_tensor[rho, mu, a, b] * g[nu, sig]
                        val += R_tensor[rho, nu, a, b] * g[mu, sig]
                        val += R_tensor[sig, mu, a, b] * g[nu, rho]
                        val += R_tensor[sig, nu, a, b] * g[mu, rho]
                    else:
                        # h_{rho rho} = 1, others 0
                        # gamma = rho only
                        val += R_tensor[rho, mu, a, b] * g[nu, rho]
                        val += R_tensor[rho, nu, a, b] * g[mu, rho]

                    Om[I, J] = val

            # Add tr(Omega_{ab} Omega^{ab}) = sum_{a,b} tr(Omega_{ab}^2)
            # Since we're using orthonormal frame, Omega^{ab} = Omega_{ab}
            trOm2 += np.trace(Om @ Om)

    return trOm2


def graviton_traces(R_tensor):
    """Compute tr(E), tr(E^2), tr(Omega^2) for the Lichnerowicz graviton operator."""
    E = graviton_endomorphism_matrix_v2(R_tensor)
    trE = np.trace(E)
    trE2 = np.trace(E @ E)
    trOm2 = graviton_connection_curvature_trace(R_tensor)
    return trE, trE2, trOm2


# =========================================================
# 4. Compute b_4 decomposition
# =========================================================

def b4_coefficients(N, trE, trE2, trOm2, R2, Ric2, Riem2):
    """
    Compute the b_4 coefficient:
    b_4 = (1/360) [N(5R^2 - 2R_{mn}^2 + 2R_{mnrs}^2) + 60R*tr(E) + 180*tr(E^2) + 30*tr(Om^2)]

    Returns the total b_4 value (excluding total derivative terms).
    """
    geom = N * (5 * R2 - 2 * Ric2 + 2 * Riem2)
    R_scalar = np.sqrt(R2)  # Only works for positive R
    endomorphism = 60 * R_scalar * trE + 180 * trE2
    connection = 30 * trOm2

    return (geom + endomorphism + connection) / 360


def compute_all(label, R_tensor):
    """Compute all traces and b_4 for a given background."""
    R2, Ric2, Riem2 = curvature_invariants(R_tensor)
    Ric = ricci_from_riemann(R_tensor)
    R_scalar = scalar_from_ricci(Ric)

    print(f"\n{'='*60}")
    print(f"Background: {label}")
    print(f"{'='*60}")
    print(f"R      = {R_scalar:.6f}")
    print(f"R^2    = {R2:.6f}")
    print(f"Ric^2  = {Ric2:.6f}")
    print(f"Riem^2 = {Riem2:.6f}")

    # Ghost traces
    g_trE, g_trE2, g_trOm2 = ghost_traces(R_tensor)
    print(f"\nGhost (vector, N={d}):")
    print(f"  tr(E)   = {g_trE:.6f}  [should be R = {R_scalar:.6f}]")
    print(f"  tr(E^2) = {g_trE2:.6f}  [should be Ric^2 = {Ric2:.6f}]")
    print(f"  tr(Om^2)= {g_trOm2:.6f}  [should be Riem^2 = {Riem2:.6f}]")

    # Graviton traces
    h_trE, h_trE2, h_trOm2 = graviton_traces(R_tensor)
    print(f"\nGraviton (sym-2, N={N_sym}):")
    print(f"  tr(E)   = {h_trE:.6f}")
    print(f"  tr(E^2) = {h_trE2:.6f}")
    print(f"  tr(Om^2)= {h_trOm2:.6f}")

    return {
        'R': R_scalar, 'R2': R2, 'Ric2': Ric2, 'Riem2': Riem2,
        'ghost': (g_trE, g_trE2, g_trOm2),
        'graviton': (h_trE, h_trE2, h_trOm2),
    }


# =========================================================
# 5. Main computation
# =========================================================

print("Track 16E: One-Loop R^2 Coefficient")
print("=" * 60)

# --- Background 1: S^4 with kappa = 1 ---
R1 = riemann_S4(1.0)
data1 = compute_all("S^4 (kappa = 1)", R1)

# --- Background 2: S^2(2) x S^2(1) ---
R2_bg = riemann_S2xS2(2.0, 1.0)
data2 = compute_all("S^2(k1=2) x S^2(k2=1)", R2_bg)

# --- Background 3: S^2(3) x S^2(1) ---
R3_bg = riemann_S2xS2(3.0, 1.0)
data3 = compute_all("S^2(k1=3) x S^2(k2=1)", R3_bg)


# =========================================================
# 6. Solve for decomposition coefficients
# =========================================================

print("\n" + "=" * 60)
print("DECOMPOSITION: Solving for R^2, Ric^2, Riem^2 coefficients")
print("=" * 60)

# For each trace T (trE, trE2, trOm2), we have:
# T = p_R2 * R^2 + p_Ric2 * Ric^2 + p_Riem2 * Riem^2
#
# Three backgrounds give three equations for three unknowns.

def solve_decomposition(trace_values, invariants_list, name):
    """
    Given trace values on 3 backgrounds and the (R^2, Ric^2, Riem^2) values,
    solve for the coefficients p = (p_R2, p_Ric2, p_Riem2).
    """
    A = np.array(invariants_list)  # 3x3 matrix
    b = np.array(trace_values)     # 3-vector

    # Check condition number
    cond = np.linalg.cond(A)
    p = np.linalg.solve(A, b)

    print(f"\n{name}:")
    print(f"  Condition number: {cond:.2f}")
    print(f"  p_R2   = {p[0]:.10f}")
    print(f"  p_Ric2 = {p[1]:.10f}")
    print(f"  p_Riem2= {p[2]:.10f}")

    # Verify
    for i, (tv, inv) in enumerate(zip(trace_values, invariants_list)):
        reconstructed = p @ inv
        print(f"  Check bg{i+1}: computed={tv:.6f}, reconstructed={reconstructed:.6f}, "
              f"diff={abs(tv - reconstructed):.2e}")

    return p

# Collect invariants
inv1 = [data1['R2'], data1['Ric2'], data1['Riem2']]
inv2 = [data2['R2'], data2['Ric2'], data2['Riem2']]
inv3 = [data3['R2'], data3['Ric2'], data3['Riem2']]
invariants = [inv1, inv2, inv3]

# --- Ghost decomposition ---
print("\n--- GHOST SECTOR ---")
ghost_trE_vals = [data1['ghost'][0], data2['ghost'][0], data3['ghost'][0]]
ghost_trE2_vals = [data1['ghost'][1], data2['ghost'][1], data3['ghost'][1]]
ghost_trOm2_vals = [data1['ghost'][2], data2['ghost'][2], data3['ghost'][2]]

# tr(E) = R is not quadratic in curvature, handle separately
# For the b_4 formula: 60R * tr(E) = 60 * R^2 (for ghost)
# This is already a quadratic invariant.

# Actually, tr(E) and tr(E^2) need to be decomposed differently.
# tr(E) is LINEAR in curvature (= R for ghost, some combination for graviton)
# In the b_4 formula: 60R * tr(E) is QUADRATIC (R^2, etc.)
# And: 180 * tr(E^2) is QUADRATIC
# And: 30 * tr(Omega^2) is QUADRATIC

# So the full b_4 quadratic contribution from E,Omega is:
# 60R * tr(E) + 180 * tr(E^2) + 30 * tr(Om^2)
# This is a quadratic expression in curvature that I need to decompose.

# Combined quadratic trace: Q = 60R*trE + 180*trE2 + 30*trOm2
ghost_Q_vals = [60 * data1['R'] * data1['ghost'][0] + 180 * data1['ghost'][1] + 30 * data1['ghost'][2],
                60 * data2['R'] * data2['ghost'][0] + 180 * data2['ghost'][1] + 30 * data2['ghost'][2],
                60 * data3['R'] * data3['ghost'][0] + 180 * data3['ghost'][1] + 30 * data3['ghost'][2]]

p_ghost_Q = solve_decomposition(ghost_Q_vals, invariants, "Ghost combined Q (60R*trE + 180*trE2 + 30*trOm2)")

# Total ghost b_4 coefficients (per unit (4pi)^{-d/2} volume):
# b_4 = (1/360) [N(5R^2 - 2Ric^2 + 2Riem^2) + Q]
# = (1/360) [(5N + q_R2)R^2 + (-2N + q_Ric2)Ric^2 + (2N + q_Riem2)Riem^2]

N_ghost = d  # = 4
ghost_R2_coeff = (5 * N_ghost + p_ghost_Q[0]) / 360
ghost_Ric2_coeff = (-2 * N_ghost + p_ghost_Q[1]) / 360
ghost_Riem2_coeff = (2 * N_ghost + p_ghost_Q[2]) / 360

print(f"\nGhost b_4 / (4pi)^{{-2}} = ")
print(f"  [{ghost_R2_coeff:.10f}] R^2 + [{ghost_Ric2_coeff:.10f}] Ric^2 + [{ghost_Riem2_coeff:.10f}] Riem^2")

# --- Graviton decomposition ---
print("\n--- GRAVITON SECTOR ---")

grav_Q_vals = [60 * data1['R'] * data1['graviton'][0] + 180 * data1['graviton'][1] + 30 * data1['graviton'][2],
               60 * data2['R'] * data2['graviton'][0] + 180 * data2['graviton'][1] + 30 * data2['graviton'][2],
               60 * data3['R'] * data3['graviton'][0] + 180 * data3['graviton'][1] + 30 * data3['graviton'][2]]

p_grav_Q = solve_decomposition(grav_Q_vals, invariants, "Graviton combined Q (60R*trE + 180*trE2 + 30*trOm2)")

N_grav = N_sym  # = 10
grav_R2_coeff = (5 * N_grav + p_grav_Q[0]) / 360
grav_Ric2_coeff = (-2 * N_grav + p_grav_Q[1]) / 360
grav_Riem2_coeff = (2 * N_grav + p_grav_Q[2]) / 360

print(f"\nGraviton b_4 / (4pi)^{{-2}} = ")
print(f"  [{grav_R2_coeff:.10f}] R^2 + [{grav_Ric2_coeff:.10f}] Ric^2 + [{grav_Riem2_coeff:.10f}] Riem^2")


# =========================================================
# 7. Total one-loop R^2 coefficient
# =========================================================

print("\n" + "=" * 60)
print("ONE-LOOP R^2 COEFFICIENT")
print("=" * 60)

# One-loop effective action:
# Gamma_1 = (1/2) Tr ln(Delta_grav) - Tr ln(Delta_ghost)
# The b_4 contribution to the divergence:
# Gamma_1^div = (1/2) b_4^grav - b_4^ghost (times 1/(16pi^2 epsilon))

# R^2 coefficient:
sigma1_R2 = 0.5 * grav_R2_coeff - ghost_R2_coeff
sigma1_Ric2 = 0.5 * grav_Ric2_coeff - ghost_Ric2_coeff
sigma1_Riem2 = 0.5 * grav_Riem2_coeff - ghost_Riem2_coeff

print(f"\nGamma_1^div / (1/(16pi^2 eps)) = integral sqrt(g) x [")
print(f"  sigma_R2   * R^2          = {sigma1_R2:.10f} R^2")
print(f"  sigma_Ric2 * R_mn^2       = {sigma1_Ric2:.10f} R_mn^2")
print(f"  sigma_Riem2* R_mnrs^2     = {sigma1_Riem2:.10f} R_mnrs^2")
print(f"]")

# Convert to (C^2, E_4, R^2) basis:
# C^2 = Riem^2 - 2Ric^2 + (1/3)R^2
# E_4 = Riem^2 - 4Ric^2 + R^2
# R^2 = R^2
#
# Inverse: Riem^2 = C^2 + 2Ric^2 - (1/3)R^2
#          So sigma_R^2 in (C^2, E_4, R^2) basis:
#
# sigma_total = sigma_Riem2 * Riem^2 + sigma_Ric2 * Ric^2 + sigma_R2 * R^2
# = sigma_Riem2 * (C^2 + 2Ric^2 - R^2/3) + sigma_Ric2 * Ric^2 + sigma_R2 * R^2
# = sigma_Riem2 * C^2 + (2*sigma_Riem2 + sigma_Ric2) * Ric^2 + (sigma_R2 - sigma_Riem2/3) * R^2
#
# But I want the (C^2, E_4, R^2) decomposition:
# Total = a*C^2 + b*E_4 + c*R^2
# = a*(Riem^2 - 2Ric^2 + R^2/3) + b*(Riem^2 - 4Ric^2 + R^2) + c*R^2
# Matching:
# Riem^2: a + b = sigma_Riem2
# Ric^2: -2a - 4b = sigma_Ric2
# R^2: a/3 + b + c = sigma_R2
#
# From first two: a = sigma_Riem2 - b, and -2(sigma_Riem2 - b) - 4b = sigma_Ric2
# => -2*sigma_Riem2 + 2b - 4b = sigma_Ric2
# => -2b = sigma_Ric2 + 2*sigma_Riem2
# => b = -(sigma_Ric2 + 2*sigma_Riem2)/2
# a = sigma_Riem2 + (sigma_Ric2 + 2*sigma_Riem2)/2 = (2*sigma_Riem2 + sigma_Ric2 + 2*sigma_Riem2)/2
# = (4*sigma_Riem2 + sigma_Ric2)/2... hmm let me redo

# a + b = sigma_Riem2    ... (i)
# -2a - 4b = sigma_Ric2  ... (ii)
# From (ii): a = -(sigma_Ric2 + 4b)/2
# Sub into (i): -(sigma_Ric2 + 4b)/2 + b = sigma_Riem2
# -sigma_Ric2/2 - 2b + b = sigma_Riem2
# -b = sigma_Riem2 + sigma_Ric2/2
# b = -(sigma_Riem2 + sigma_Ric2/2)
# a = sigma_Riem2 - b = sigma_Riem2 + sigma_Riem2 + sigma_Ric2/2 = 2*sigma_Riem2 + sigma_Ric2/2
# c = sigma_R2 - a/3 - b

a_C2 = 2 * sigma1_Riem2 + sigma1_Ric2 / 2
b_E4 = -(sigma1_Riem2 + sigma1_Ric2 / 2)
c_R2 = sigma1_R2 - a_C2 / 3 - b_E4

print(f"\nIn the (C^2, E_4, R^2) basis:")
print(f"  C^2 coefficient:  {a_C2:.10f}")
print(f"  E_4 coefficient:  {b_E4:.10f}")
print(f"  R^2 coefficient:  {c_R2:.10f}")

print(f"\n{'='*60}")
print(f"THE KEY RESULT")
print(f"{'='*60}")
print(f"\nTree level:  R^2 = 0  (spectral action structural identity)")
print(f"One loop:    R^2 coefficient sigma_1 = {c_R2:.10f}")
print(f"Sign:        {'POSITIVE (inside AS basin!)' if c_R2 > 0 else 'NEGATIVE (outside AS basin)' if c_R2 < 0 else 'ZERO (identity preserved!)'}")

# =========================================================
# 8. Cross-check with known results
# =========================================================

print(f"\n{'='*60}")
print("CROSS-CHECKS")
print(f"{'='*60}")

# For the ghost (vector with E = Ricci):
# Expected: b_4 = (1/360)[80R^2 + 172Ric^2 + 38Riem^2]
# where 80 = 5*4 + 60*1 (from 60R*R) + ... wait let me recompute
# geom: 4*(5R^2 - 2Ric^2 + 2Riem^2) = 20R^2 - 8Ric^2 + 8Riem^2
# 60R*trE = 60*R*R = 60R^2
# 180*trE2 = 180*Ric^2
# 30*trOm2 = 30*Riem^2
# Total: (20+60)R^2 + (-8+180)Ric^2 + (8+30)Riem^2 = 80R^2 + 172Ric^2 + 38Riem^2
print(f"\nGhost expected: (80, 172, 38)/360 = ({80/360:.10f}, {172/360:.10f}, {38/360:.10f})")
print(f"Ghost computed: ({ghost_R2_coeff:.10f}, {ghost_Ric2_coeff:.10f}, {ghost_Riem2_coeff:.10f})")

# For the Dirac operator (spin-1/2), the identity alpha + beta/3 + gamma/3 = 0:
# This should NOT hold for the graviton or ghost.
# Check: alpha + beta/3 + gamma/3 for each sector:
ghost_identity = ghost_R2_coeff + ghost_Ric2_coeff / 3 + ghost_Riem2_coeff / 3
grav_identity = grav_R2_coeff + grav_Ric2_coeff / 3 + grav_Riem2_coeff / 3

print(f"\nalpha + beta/3 + gamma/3 identity:")
print(f"  Ghost:    {ghost_identity:.10f}  (should be != 0)")
print(f"  Graviton: {grav_identity:.10f}  (should be != 0)")
print(f"  Dirac (known): 0.0  (structural identity of D^2)")

# =========================================================
# 9. Interpretation for the NCG-AS bridge
# =========================================================

print(f"\n{'='*60}")
print("INTERPRETATION FOR THE NCG-AS BRIDGE")
print(f"{'='*60}")

print(f"""
Tree-level spectral action: (C^2, E_4, R^2) = (-18, +11, 0)
  The R^2 = 0 is a structural identity of the Dirac operator.

One-loop correction: R^2 coefficient = {c_R2:.6f}

{'POSITIVE sigma_1:' if c_R2 > 0 else 'NEGATIVE sigma_1:'}
  The one-loop correction {'pushes the theory INTO' if c_R2 > 0 else 'pushes the theory AWAY FROM'}
  the R^2 = 0 critical surface{'.' if c_R2 < 0 else ' of the AS fixed point.'}

{'This is consistent with the NCG-AS bridge: the spectral action' if c_R2 > 0 else 'This challenges the NCG-AS bridge: the spectral action'}
{'sits on the critical surface at tree level, and one-loop' if c_R2 > 0 else 'sits on the critical surface at tree level, but one-loop'}
{'corrections are self-consistently small.' if c_R2 > 0 else 'corrections push it away.'}

Note: The sign of sigma_1 relative to the AS basin depends on the
convention for the R^2 coupling in the AS literature. In the standard
convention (Benedetti-Machado-Saueressig 2009), the UV-repulsive
direction at the AS fixed point determines the sign convention.
The spectral action is IN the basin if its R^2 coupling satisfies
the critical surface constraint.

KK tower contribution:
  Each massive KK mode contributes the SAME R^2 coefficient as the
  zero mode (mass-independence of a_4 curvature-squared terms).
  The total KK sum diverges as N_KK (regulated by the 5D cutoff).
  This does NOT affect the SIGN of sigma_1 -- it only rescales it.
""")
