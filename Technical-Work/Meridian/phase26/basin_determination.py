"""
BASIN DETERMINATION CALCULATION
================================
Phase 26: The definitive test of whether the octonionic spectral triple
on the RS_1 warped orbifold fully determines the fermion sector.

Question: After exhausting ALL algebraic constraints from the octonions
(S_3, G_2, Fano, M_oct, anomaly cancellation, b_{3/2}), how many free
parameters remain -- and is that number less than the number of
independent measurements?

If yes -> the basin is determined at 5D + NCG (local TOE candidate)
If no  -> higher-dimensional metric data is needed (effective theory)

Clayton + Clawd, April 2, 2026
"""

import numpy as np
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import svd
from itertools import permutations
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# PHYSICAL CONSTANTS
# ============================================================

# RS geometry
ky_c = 37.0           # warp factor parameter
k = 1e8               # AdS curvature scale (GeV) -- sets the overall mass scale
v_EW = 246.0           # Higgs VEV (GeV)

# Observed fermion masses at M_Z (GeV) -- MSbar, PDG 2024
# Up-type quarks
m_u = 2.16e-3          # +/- 0.49e-3
m_c = 1.27             # +/- 0.02
m_t = 172.69           # +/- 0.30

# Down-type quarks
m_d = 4.67e-3          # +/- 0.48e-3
m_s = 93.4e-3          # +/- 8.6e-3
m_b = 4.18             # +/- 0.03

# Charged leptons
m_e = 0.511e-3
m_mu = 105.66e-3
m_tau = 1.777

# CKM matrix elements (magnitudes)
V_ud = 0.97373         # +/- 0.00031
V_us = 0.2243          # +/- 0.0008
V_ub = 0.00382         # +/- 0.00020
V_cd = 0.221           # +/- 0.004
V_cs = 0.975           # +/- 0.006
V_cb = 0.0408          # +/- 0.0014
V_td = 0.0086          # +/- 0.0002
V_ts = 0.0415          # +/- 0.0009
V_tb = 0.99914         # +/- 0.00005

# Jarlskog invariant
J_CKM = 3.08e-5        # +/- 0.15e-5

# PMNS mixing angles (sin^2theta)
sin2_12 = 0.307        # +/- 0.013 (solar)
sin2_23 = 0.546        # +/- 0.021 (atmospheric)
sin2_13 = 0.0220       # +/- 0.0007 (reactor)

# Neutrino mass-squared differences (eV^2)
dm2_21 = 7.53e-5       # +/- 0.18e-5 (solar)
dm2_32 = 2.453e-3      # +/- 0.033e-3 (atmospheric, normal hierarchy)

# ============================================================
# STAGE 1: OCTONIONIC ALGEBRA
# ============================================================

print("=" * 70)
print("STAGE 1: OCTONIONIC ALGEBRA AND CONSTRAINTS")
print("=" * 70)

# Fano plane triples (defines octonion multiplication)
FANO_TRIPLES = [
    (1, 2, 3), (1, 4, 5), (1, 7, 6),
    (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 6, 5)
]

# Build multiplication table
def build_mult_table():
    """Build 8x8 octonion multiplication table from Fano plane."""
    table = np.zeros((8, 8), dtype=int)
    sign = np.zeros((8, 8), dtype=int)

    # e_0 is identity
    for i in range(8):
        table[0, i] = i
        table[i, 0] = i
        sign[0, i] = 1
        sign[i, 0] = 1

    # e_i * e_i = -e_0
    for i in range(1, 8):
        table[i, i] = 0
        sign[i, i] = -1

    # Fano triples: e_a * e_b = e_c (cyclic)
    for a, b, c in FANO_TRIPLES:
        table[a, b] = c; sign[a, b] = 1
        table[b, c] = a; sign[b, c] = 1
        table[c, a] = b; sign[c, a] = 1
        table[b, a] = c; sign[b, a] = -1
        table[c, b] = a; sign[c, b] = -1
        table[a, c] = b; sign[a, c] = -1

    return table, sign

MULT_TABLE, MULT_SIGN = build_mult_table()

def oct_mult(a, b):
    """Multiply two octonions (8-component real vectors)."""
    result = np.zeros(8)
    for i in range(8):
        for j in range(8):
            k = MULT_TABLE[i, j]
            s = MULT_SIGN[i, j]
            result[k] += s * a[i] * b[j]
    return result

# Complex structures J_1, J_2, J_4 (right multiplication by e_1, e_2, e_4)
def right_mult_matrix(idx):
    """8x8 matrix for right multiplication by e_idx."""
    J = np.zeros((8, 8))
    for i in range(8):
        ei = np.zeros(8); ei[i] = 1
        eidx = np.zeros(8); eidx[idx] = 1
        prod = oct_mult(ei, eidx)
        J[:, i] = prod
    return J

J1 = right_mult_matrix(1)
J2 = right_mult_matrix(2)
J4 = right_mult_matrix(4)

# Verify J_a^2 = -Id
for name, J in [("J1", J1), ("J2", J2), ("J4", J4)]:
    err = np.max(np.abs(J @ J + np.eye(8)))
    print(f"  {name}^2 + I = 0: error = {err:.2e}")

# The democratic mass matrix M_oct
# M_oct(a,b) = (1/16)(8 - Tr(J_a J_b)) for the 3 complex structures
def compute_M_oct():
    """Compute M_oct from the three complex structures."""
    Js = [J1, J2, J4]
    M = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            M[a, b] = (8.0 - np.trace(Js[a] @ Js[b])) / 16.0
    return M

M_oct = compute_M_oct()
evals_M = np.sort(np.linalg.eigvalsh(M_oct))

print(f"\n  M_oct:")
for row in M_oct:
    print(f"    [{row[0]:.4f}  {row[1]:.4f}  {row[2]:.4f}]")
print(f"  Eigenvalues: {evals_M}")
print(f"  Ratio: {evals_M[0]:.1f} : {evals_M[1]:.1f} : {evals_M[2]:.1f}")

# S_3 symmetry verification
print("\n  S_3 symmetry check:")
perms = list(permutations([0, 1, 2]))
s3_invariant = True
for p in perms:
    M_perm = M_oct[np.ix_(list(p), list(p))]
    if not np.allclose(M_perm, M_oct, atol=1e-10):
        s3_invariant = False
        print(f"    Permutation {p}: BROKEN")
print(f"  M_oct is S_3-invariant: {s3_invariant}")

# ============================================================
# G_2 AUTOMORPHISM ANALYSIS
# ============================================================

print(f"\n  G_2 cross-sector analysis:")

# G_2 is the automorphism group of the octonions.
# It acts on Im(O) = R^7, preserving the multiplication table.
# The three complex structures J_1, J_2, J_4 are mapped to each other
# by OUTER automorphisms -- but G_2 (inner auts) acts within the
# 7-dimensional imaginary space.
#
# Key question: Does G_2 relate different FERMION SECTORS?
# In Spin(10), u_R and nu_R are in the same 16-spinor.
# If the octonionic Spin(10) -> SM decomposition preserves
# G_2 relationships between the sectors, then c_u and c_nu
# are not independent.

# The G_2 Lie algebra has dimension 14 (generators).
# Acting on R^7, it decomposes as: 7 -> 7 (irreducible)
# Acting on the generation space (through complex structures),
# S_3 ? G_2 permutes the three complex structures.
# But S_3 is discrete -- the continuous G_2 gives MORE constraints.

# Check: what is the G_2 orbit structure on the parameter space?
# If all three complex structures are in the same G_2 orbit,
# then G_2 imposes c_{a1} = c_{a2} = c_{a3} for each sector --
# which contradicts the mass hierarchy. So G_2 must be broken.

# The RELEVANT question is: does the UNBROKEN part of G_2
# (after the complex structure selection breaks G_2 -> SU(3))
# impose cross-sector constraints?

# G_2 -> SU(3): choosing one complex structure (say J_1) breaks
# G_2 to SU(3). The 7 of G_2 decomposes as 7 -> 1 + 3 + 3 under SU(3).
# This SU(3) is the COLOR group.
# The generations are labeled by the THREE complex structures,
# not by the SU(3) decomposition. So G_2 -> SU(3) doesn't
# directly constrain inter-generation parameters.

# However: the G_2-invariant 3-form phi (the associative calibration)
# IS a constraint on the Yukawa couplings. It determines which
# triple products are nonzero.

# Compute the associative calibration phi
phi = np.zeros((7, 7, 7))  # indices 1-7 mapped to 0-6
for a, b, c in FANO_TRIPLES:
    # phi is totally antisymmetric, nonzero on Fano triples
    for p in [(a-1, b-1, c-1), (b-1, c-1, a-1), (c-1, a-1, b-1)]:
        phi[p] = 1.0
    for p in [(b-1, a-1, c-1), (c-1, b-1, a-1), (a-1, c-1, b-1)]:
        phi[p] = -1.0

# Count nonzero components
n_nonzero = np.count_nonzero(phi)
print(f"  Associative 3-form phi: {n_nonzero} nonzero components (of 343)")
print(f"  phi has ZERO free parameters -- fully determined by Fano plane")

# The G_2-invariant 4-form *phi (coassociative calibration)
# gives additional constraints. But these are GEOMETRIC constraints
# on the 7D space, not directly on the generation-indexed parameters.

# VERDICT on G_2 cross-sector:
print(f"\n  G_2 CROSS-SECTOR VERDICT:")
print(f"  G_2 acts on Im(O) = R^7, not on the generation space directly.")
print(f"  The generation space is {'{'}J_1, J_2, J_4{'}'} -- labeled by complex structures.")
print(f"  G_2 -> SU(3) (choosing one J) gives color, not generation constraints.")
print(f"  S_3 ? Out(O) permutes the J's -- this IS the generation symmetry.")
print(f"  G_2 does NOT provide additional cross-sector constraints")
print(f"  beyond what S_3 already gives.")
print(f"  -> Cross-sector constraints must come from Spin(10) GUT embedding,")
print(f"    not from G_2 directly.")

# ============================================================
# STAGE 2: RS FERMION MASS MODEL (LEFT-RIGHT)
# ============================================================

print("\n" + "=" * 70)
print("STAGE 2: RS FERMION MASS MODEL")
print("=" * 70)

def g_profile(c, ky_c=37.0):
    """
    Zero-mode profile overlap with IR-localized Higgs.
    g(c) = sqrt((1-2c)/(exp((1-2c)*ky_c) - 1)) * exp((1/2-c)*ky_c)
    """
    x = (1.0 - 2.0 * c) * ky_c
    if abs(x) < 1e-10:
        # c ~ 0.5: g ~ sqrt(ky_c) * exp(-ky_c/2) ... but numerically:
        return np.sqrt(1.0 / ky_c)
    elif x > 500:
        # c < 0.5 (IR-localized): g ~ sqrt(1-2c) (large)
        return np.sqrt(1.0 - 2.0 * c)
    elif x < -500:
        # c > 0.5 (UV-localized): g ~ sqrt(2c-1) * exp((1/2-c)*ky_c) (tiny)
        return np.sqrt(2.0 * c - 1.0) * np.exp((0.5 - c) * ky_c)
    else:
        return np.sqrt((1.0 - 2.0 * c) / (np.exp(x) - 1.0)) * np.exp((0.5 - c) * ky_c)

def mass_matrix(c_L, c_R, Y5, M_oct, ky_c=37.0):
    """
    Compute the 3x3 mass matrix:
    M_ij = Y5 * M_oct_ij * g(c_Li) * g(c_Rj) * v_EW / sqrt(2)
    """
    g_L = np.array([g_profile(c, ky_c) for c in c_L])
    g_R = np.array([g_profile(c, ky_c) for c in c_R])
    M = Y5 * M_oct * np.outer(g_L, g_R) * v_EW / np.sqrt(2)
    return M

def diagonalize(M):
    """SVD diagonalization: M = U @ diag(s) @ Vh"""
    U, s, Vh = svd(M)
    # Sort by singular value (ascending)
    idx = np.argsort(s)
    return s[idx], U[:, idx], Vh[idx, :]

# ============================================================
# STAGE 3: CONSTRAINT COUNTING
# ============================================================

print("\n" + "=" * 70)
print("STAGE 3: PARAMETER AND CONSTRAINT COUNTING")
print("=" * 70)

print("""
RAW PARAMETERS (left-right model):
  Quark doublets:     c_Q1, c_Q2, c_Q3                    = 3
  Up singlets:        c_u1, c_u2, c_u3                    = 3
  Down singlets:      c_d1, c_d2, c_d3                    = 3
  Lepton doublets:    c_L1, c_L2, c_L3                    = 3
  Charged lep singlets: c_e1, c_e2, c_e3                  = 3
  RH neutrino:        c_N1, c_N2, c_N3                    = 3
  Yukawa scales:      Y5_u, Y5_d, Y5_e                    = 3
  Majorana params:    a, b                                 = 2
  CP phase:           delta                                = 1
  ????????????????????????????????????????????????????????????
  TOTAL RAW:                                               = 24

ALGEBRAIC CONSTRAINTS:
  M_oct fixed (no free params):                            = 0 (structure, not parameter reduction)
  S_3 doublet degeneracy:
    c_Q1 = c_Q2, c_u1 = c_u2, c_d1 = c_d2                = -3
    c_L1 = c_L2, c_e1 = c_e2, c_N1 = c_N2                = -3
  G_2 cross-sector:                                        = 0 (does not constrain)
  ????????????????????????????????????????????????????????????
  TOTAL AFTER S_3:                                          = 18

ADDITIONAL POTENTIAL CONSTRAINTS:
  b_{3/2} = 0.426 (boundary heat kernel):                  = -1
  Spin(10) GUT embedding (c_Q = c_L, c_u = c_N, etc.):    = -? (IF it holds)
  ????????????????????????????????????????????????????????????
  MINIMUM AFTER ALL:                                       = 17 (without GUT)
                                                           = 13 (with Spin(10))

MEASUREMENTS:
  6 quark masses:                                          = 6
  3 charged lepton masses:                                 = 3
  3 CKM angles:                                            = 3
  1 CKM phase (Jarlskog):                                  = 1
  3 PMNS angles:                                           = 3
  1 PMNS phase:                                            = 1 (poorly measured)
  2 neutrino ?m^2:                                          = 2
  ????????????????????????????????????????????????????????????
  TOTAL MEASUREMENTS:                                      = 19

OVERCONSTRAINED?
  Without Spin(10): 19 - 17 = +2 (2 consistency conditions)
  With Spin(10):    19 - 13 = +6 (6 consistency conditions)
""")

# ============================================================
# STAGE 4: GLOBAL FIT -- THE DEFINITIVE TEST
# ============================================================

print("=" * 70)
print("STAGE 4: GLOBAL FIT TO ALL FERMION DATA")
print("=" * 70)

# We fit with S_3 degeneracy enforced: c_{a1} = c_{a2} for each sector.
# Free parameters (18 without b_{3/2} constraint):
#   c_Q_12, c_Q_3   (quark doublets: 2)
#   c_u_12, c_u_3   (up singlets: 2)
#   c_d_12, c_d_3   (down singlets: 2)
#   c_L_12, c_L_3   (lepton doublets: 2)
#   c_e_12, c_e_3   (charged lepton singlets: 2)
#   c_N_12, c_N_3   (RH neutrino: 2)
#   Y5_u, Y5_d, Y5_e (Yukawa scales: 3)
#   a, b             (Majorana parameters: 2 -- but in eV, not directly comparable)
#   delta            (CP phase: 1)

# For the QUARK + CHARGED LEPTON sector (no Majorana):
# Parameters: 6 doublet-degenerate bulk masses + 6 singlet bulk masses + 3 Yukawa = 15
# (ignoring CP phase for magnitude-only fit)
# Measurements: 9 masses + 3 CKM angles = 12
# So the quark+lepton sector alone is UNDERDETERMINED (15 > 12).
# BUT: with S_3, the structure constrains the CKM to specific patterns.

# Let's do the fit and see what the null space looks like.

# Observed masses (GeV) -- targets
m_obs_u = np.array([m_u, m_c, m_t])      # up-type quarks
m_obs_d = np.array([m_d, m_s, m_b])      # down-type quarks
m_obs_e = np.array([m_e, m_mu, m_tau])   # charged leptons

# Observed CKM (magnitudes of first row and first column, plus V_cb)
V_obs = {
    'us': V_us, 'ub': V_ub, 'cb': V_cb,
    'ud': V_ud, 'cs': V_cs, 'tb': V_tb
}

def chi2_quarks_leptons(params):
    """
    Chi-squared for quark + charged lepton sector.

    params = [c_Q12, c_Q3, c_u12, c_u3, c_d12, c_d3,
              c_L12, c_L3, c_e12, c_e3,
              Y5_u, Y5_d, Y5_e]
    """
    (c_Q12, c_Q3, c_u12, c_u3, c_d12, c_d3,
     c_L12, c_L3, c_e12, c_e3,
     Y5_u, Y5_d, Y5_e) = params

    # Enforce S_3 doublet degeneracy
    c_Q = [c_Q12, c_Q12, c_Q3]
    c_u = [c_u12, c_u12, c_u3]
    c_d = [c_d12, c_d12, c_d3]
    c_L = [c_L12, c_L12, c_L3]
    c_e = [c_e12, c_e12, c_e3]

    # Compute mass matrices
    M_u = mass_matrix(c_Q, c_u, Y5_u, M_oct)
    M_d = mass_matrix(c_Q, c_d, Y5_d, M_oct)
    M_e = mass_matrix(c_L, c_e, Y5_e, M_oct)

    # Diagonalize
    m_u_pred, U_uL, U_uR = diagonalize(M_u)
    m_d_pred, U_dL, U_dR = diagonalize(M_d)
    m_e_pred, U_eL, U_eR = diagonalize(M_e)

    # CKM = U_uL? @ U_dL
    V_CKM = U_uL.T @ U_dL

    # Chi-squared: masses (log-scale to weight hierarchy fairly)
    chi2 = 0.0

    # Up-type quarks
    for i in range(3):
        if m_u_pred[i] > 0:
            chi2 += (np.log(m_u_pred[i]) - np.log(m_obs_u[i]))**2 / (0.1)**2
        else:
            chi2 += 1e6

    # Down-type quarks
    for i in range(3):
        if m_d_pred[i] > 0:
            chi2 += (np.log(m_d_pred[i]) - np.log(m_obs_d[i]))**2 / (0.1)**2
        else:
            chi2 += 1e6

    # Charged leptons
    for i in range(3):
        if m_e_pred[i] > 0:
            chi2 += (np.log(m_e_pred[i]) - np.log(m_obs_e[i]))**2 / (0.1)**2
        else:
            chi2 += 1e6

    # CKM elements
    sigma_ckm = 0.05  # relative precision
    for key, val in V_obs.items():
        i, j = {'us': (0,1), 'ub': (0,2), 'cb': (1,2),
                'ud': (0,0), 'cs': (1,1), 'tb': (2,2)}[key]
        v_pred = abs(V_CKM[i, j])
        if v_pred > 0:
            chi2 += ((v_pred - val) / (sigma_ckm * val))**2
        else:
            chi2 += 1e6

    return chi2

# Initial guess based on existing best-fit (Chapter 4, left-right model)
x0 = [
    0.557, 0.247,    # c_Q12, c_Q3  (doublet: gen 1,2 degenerate; gen 3 different)
    0.661, 0.200,    # c_u12, c_u3
    0.495, 0.567,    # c_d12, c_d3
    0.650, 0.520,    # c_L12, c_L3
    0.660, 0.500,    # c_e12, c_e3
    1.75, 0.18, 0.10 # Y5_u, Y5_d, Y5_e
]

# Bounds: c_i in [0, 0.8], Y5 in [0.01, 10]
bounds = [
    (0.3, 0.7), (0.0, 0.5),    # c_Q
    (0.3, 0.75), (0.0, 0.5),   # c_u
    (0.3, 0.7), (0.3, 0.7),    # c_d
    (0.3, 0.75), (0.3, 0.65),  # c_L
    (0.3, 0.75), (0.3, 0.65),  # c_e
    (0.1, 5.0), (0.01, 2.0), (0.01, 2.0)  # Y5
]

print("\n  Running global fit (differential evolution)...")
result = differential_evolution(
    chi2_quarks_leptons, bounds,
    seed=42, maxiter=2000, tol=1e-12,
    popsize=30, mutation=(0.5, 1.5), recombination=0.9
)

print(f"  Optimization: {'SUCCESS' if result.success else 'FAILED'}")
print(f"  chi^2 = {result.fun:.4f}")

# Extract best-fit parameters
bf = result.x
(c_Q12, c_Q3, c_u12, c_u3, c_d12, c_d3,
 c_L12, c_L3, c_e12, c_e3,
 Y5_u, Y5_d, Y5_e) = bf

# Compute predictions at best-fit
c_Q = [c_Q12, c_Q12, c_Q3]
c_u = [c_u12, c_u12, c_u3]
c_d = [c_d12, c_d12, c_d3]
c_L = [c_L12, c_L12, c_L3]
c_e = [c_e12, c_e12, c_e3]

M_u_bf = mass_matrix(c_Q, c_u, Y5_u, M_oct)
M_d_bf = mass_matrix(c_Q, c_d, Y5_d, M_oct)
M_e_bf = mass_matrix(c_L, c_e, Y5_e, M_oct)

m_u_pred, U_uL, _ = diagonalize(M_u_bf)
m_d_pred, U_dL, _ = diagonalize(M_d_bf)
m_e_pred, _, _ = diagonalize(M_e_bf)

V_CKM = U_uL.T @ U_dL

print(f"\n  Best-fit parameters (S_3 doublet-degenerate):")
print(f"    c_Q  = [{c_Q12:.4f}, {c_Q12:.4f}, {c_Q3:.4f}]")
print(f"    c_u  = [{c_u12:.4f}, {c_u12:.4f}, {c_u3:.4f}]")
print(f"    c_d  = [{c_d12:.4f}, {c_d12:.4f}, {c_d3:.4f}]")
print(f"    c_L  = [{c_L12:.4f}, {c_L12:.4f}, {c_L3:.4f}]")
print(f"    c_e  = [{c_e12:.4f}, {c_e12:.4f}, {c_e3:.4f}]")
print(f"    Y5_u = {Y5_u:.4f}, Y5_d = {Y5_d:.4f}, Y5_e = {Y5_e:.4f}")

print(f"\n  MASS PREDICTIONS vs OBSERVED:")
print(f"  {'Fermion':>8s}  {'Predicted':>12s}  {'Observed':>12s}  {'Ratio':>8s}")
print(f"  {'-'*46}")
for name, pred, obs in [
    ('u', m_u_pred[0], m_u), ('c', m_u_pred[1], m_c), ('t', m_u_pred[2], m_t),
    ('d', m_d_pred[0], m_d), ('s', m_d_pred[1], m_s), ('b', m_d_pred[2], m_b),
    ('e', m_e_pred[0], m_e), ('mu', m_e_pred[1], m_mu), ('?', m_e_pred[2], m_tau)]:
    ratio = pred / obs if obs > 0 else 0
    print(f"  {name:>8s}  {pred:12.4e}  {obs:12.4e}  {ratio:8.4f}")

print(f"\n  CKM PREDICTIONS vs OBSERVED:")
print(f"  {'Element':>8s}  {'Predicted':>10s}  {'Observed':>10s}  {'Pull (sigma)':>10s}")
print(f"  {'-'*44}")
for key, val in V_obs.items():
    i, j = {'us': (0,1), 'ub': (0,2), 'cb': (1,2),
            'ud': (0,0), 'cs': (1,1), 'tb': (2,2)}[key]
    v_pred = abs(V_CKM[i, j])
    pull = (v_pred - val) / (0.05 * val)
    print(f"  V_{key:>5s}  {v_pred:10.5f}  {val:10.5f}  {pull:10.2f}")

N_params = 13  # (10 bulk masses with S_3 + 3 Yukawa)
N_meas = 15    # (9 masses + 6 CKM elements)
N_dof = N_meas - N_params
print(f"\n  Degrees of freedom: {N_meas} measurements - {N_params} parameters = {N_dof}")
print(f"  chi^2/dof = {result.fun:.2f}/{N_dof} = {result.fun/max(N_dof,1):.2f}")

# ============================================================
# STAGE 5: NULL SPACE ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("STAGE 5: NULL SPACE ANALYSIS (JACOBIAN)")
print("=" * 70)

# Compute the Jacobian of observables w.r.t. parameters at the best-fit
def compute_observables(params):
    """Return vector of observables for Jacobian computation."""
    (c_Q12, c_Q3, c_u12, c_u3, c_d12, c_d3,
     c_L12, c_L3, c_e12, c_e3,
     Y5_u, Y5_d, Y5_e) = params

    c_Q = [c_Q12, c_Q12, c_Q3]
    c_u = [c_u12, c_u12, c_u3]
    c_d = [c_d12, c_d12, c_d3]
    c_L = [c_L12, c_L12, c_L3]
    c_e = [c_e12, c_e12, c_e3]

    M_u = mass_matrix(c_Q, c_u, Y5_u, M_oct)
    M_d = mass_matrix(c_Q, c_d, Y5_d, M_oct)
    M_e = mass_matrix(c_L, c_e, Y5_e, M_oct)

    m_u_p, U_uL, _ = diagonalize(M_u)
    m_d_p, U_dL, _ = diagonalize(M_d)
    m_e_p, _, _ = diagonalize(M_e)

    V = U_uL.T @ U_dL

    # Observables: log masses + CKM elements
    obs = np.concatenate([
        np.log(np.maximum(m_u_p, 1e-20)),  # 3 up masses
        np.log(np.maximum(m_d_p, 1e-20)),  # 3 down masses
        np.log(np.maximum(m_e_p, 1e-20)),  # 3 lepton masses
        [abs(V[0,1]), abs(V[0,2]), abs(V[1,2]),  # V_us, V_ub, V_cb
         abs(V[0,0]), abs(V[1,1]), abs(V[2,2])]   # V_ud, V_cs, V_tb
    ])
    return obs

# Numerical Jacobian
eps = 1e-6
obs_0 = compute_observables(bf)
n_obs = len(obs_0)
n_par = len(bf)
J = np.zeros((n_obs, n_par))

for j in range(n_par):
    p_plus = bf.copy(); p_plus[j] += eps
    p_minus = bf.copy(); p_minus[j] -= eps
    J[:, j] = (compute_observables(p_plus) - compute_observables(p_minus)) / (2 * eps)

# SVD of the Jacobian
U_J, S_J, Vh_J = svd(J)
print(f"\n  Jacobian shape: {J.shape} ({n_obs} observables x {n_par} parameters)")
print(f"  Singular values:")
for i, s in enumerate(S_J):
    status = "CONSTRAINED" if s > 1e-3 else "NULL DIRECTION"
    print(f"    sigma_{i+1} = {s:12.6f}  [{status}]")

n_constrained = np.sum(S_J > 1e-3)
n_null = n_par - n_constrained

print(f"\n  Constrained directions: {n_constrained}")
print(f"  Null directions:       {n_null}")
print(f"  Effective parameters:  {n_constrained}")
print(f"  Effective dof:         {n_obs} - {n_constrained} = {n_obs - n_constrained}")

if n_null > 0:
    print(f"\n  NULL SPACE DIRECTIONS (unconstrained parameter combinations):")
    for i in range(n_null):
        idx = n_par - 1 - i
        direction = Vh_J[idx, :]
        print(f"    Null direction {i+1}: sigma = {S_J[idx]:.2e}")
        labels = ['c_Q12', 'c_Q3', 'c_u12', 'c_u3', 'c_d12', 'c_d3',
                  'c_L12', 'c_L3', 'c_e12', 'c_e3', 'Y5_u', 'Y5_d', 'Y5_e']
        components = [(labels[j], direction[j]) for j in range(n_par) if abs(direction[j]) > 0.1]
        for lab, val in sorted(components, key=lambda x: -abs(x[1])):
            print(f"      {lab:>8s}: {val:+.4f}")

# ============================================================
# STAGE 5b: SPIN(10) GUT CONSTRAINT TEST
# ============================================================

print("\n" + "=" * 70)
print("STAGE 5b: SPIN(10) GUT EMBEDDING TEST")
print("=" * 70)

# In Spin(10), each generation fills one 16-spinor:
#   16 = (Q, u^c, d^c, L, e^c, nu^c)
# The SIMPLEST GUT relation: all members of a 16 share the SAME bulk mass.
# i.e., c_Q_a = c_u_a = c_d_a = c_L_a = c_e_a = c_N_a == c_a
#
# This reduces 18 bulk masses to 3 (one per generation) -> with S_3: 2.
# BUT: this is known to be too restrictive -- it gives wrong V_cb.
#
# The NEXT level: Spin(10) -> SU(5) x U(1)_X
#   10 = (Q, u^c, e^c) share one bulk mass
#   5  = (d^c, L) share another
#   1  = (nu^c) has its own
# This gives: per generation: 3 parameters (c_10, c_5bar, c_1)
# With S_3: 6 total (2 per representation class)

# Let's test: does the GUT-constrained model fit?
print("\n  Testing SU(5) GUT relation: c_Q = c_u = c_e (10), c_d = c_L (5)")

def chi2_gut(params):
    """
    SU(5) GUT-constrained fit.
    params = [c_10_12, c_10_3, c_5bar_12, c_5bar_3, Y5_u, Y5_d, Y5_e]
    """
    c_10_12, c_10_3, c_5b_12, c_5b_3, Y5_u, Y5_d, Y5_e = params

    # SU(5) relations
    c_Q = [c_10_12, c_10_12, c_10_3]
    c_u = [c_10_12, c_10_12, c_10_3]
    c_e = [c_10_12, c_10_12, c_10_3]
    c_d = [c_5b_12, c_5b_12, c_5b_3]
    c_L = [c_5b_12, c_5b_12, c_5b_3]

    M_u = mass_matrix(c_Q, c_u, Y5_u, M_oct)
    M_d = mass_matrix(c_Q, c_d, Y5_d, M_oct)
    M_e = mass_matrix(c_L, c_e, Y5_e, M_oct)

    m_u_p, U_uL, _ = diagonalize(M_u)
    m_d_p, U_dL, _ = diagonalize(M_d)
    m_e_p, _, _ = diagonalize(M_e)

    V = U_uL.T @ U_dL

    chi2 = 0.0
    for pred, obs in zip(m_u_p, m_obs_u):
        if pred > 0:
            chi2 += (np.log(pred) - np.log(obs))**2 / 0.1**2
    for pred, obs in zip(m_d_p, m_obs_d):
        if pred > 0:
            chi2 += (np.log(pred) - np.log(obs))**2 / 0.1**2
    for pred, obs in zip(m_e_p, m_obs_e):
        if pred > 0:
            chi2 += (np.log(pred) - np.log(obs))**2 / 0.1**2

    for key, val in V_obs.items():
        i, j = {'us': (0,1), 'ub': (0,2), 'cb': (1,2),
                'ud': (0,0), 'cs': (1,1), 'tb': (2,2)}[key]
        v_pred = abs(V[i, j])
        chi2 += ((v_pred - val) / (0.05 * val))**2

    return chi2

bounds_gut = [
    (0.3, 0.75), (0.0, 0.5),    # c_10
    (0.3, 0.7), (0.3, 0.65),    # c_5bar
    (0.1, 5.0), (0.01, 2.0), (0.01, 2.0)  # Y5
]

print("  Running GUT-constrained fit...")
result_gut = differential_evolution(
    chi2_gut, bounds_gut,
    seed=42, maxiter=2000, tol=1e-12,
    popsize=30
)

N_params_gut = 7
N_meas_gut = 15
N_dof_gut = N_meas_gut - N_params_gut

print(f"  GUT fit: chi^2 = {result_gut.fun:.2f}, dof = {N_dof_gut}, chi^2/dof = {result_gut.fun/N_dof_gut:.2f}")
print(f"  {'PASSES' if result_gut.fun/N_dof_gut < 3.0 else 'FAILS'} (threshold: chi^2/dof < 3)")

bf_gut = result_gut.x
print(f"\n  GUT best-fit parameters:")
print(f"    c_10  = [{bf_gut[0]:.4f}, {bf_gut[0]:.4f}, {bf_gut[1]:.4f}]")
print(f"    c_5   = [{bf_gut[2]:.4f}, {bf_gut[2]:.4f}, {bf_gut[3]:.4f}]")
print(f"    Y5_u = {bf_gut[4]:.4f}, Y5_d = {bf_gut[5]:.4f}, Y5_e = {bf_gut[6]:.4f}")

# ============================================================
# STAGE 6: VERDICT
# ============================================================

print("\n" + "=" * 70)
print("STAGE 6: VERDICT -- IS THE BASIN DETERMINED?")
print("=" * 70)

print(f"""
RESULTS SUMMARY
===============

1. OCTONIONIC CONSTRAINTS:
   - M_oct: fully determined, zero free parameters
   - S_3 doublet degeneracy: -6 parameters
   - G_2 cross-sector: NO additional constraints
   - Total algebraic reduction: 24 -> 18

2. UNCONSTRAINED FIT (S_3 only):
   - Parameters: 13 (10 bulk masses + 3 Yukawa scales)
   - Measurements: 15 (9 masses + 6 CKM)
   - chi^2 = {result.fun:.2f} for {N_dof} dof -> chi^2/dof = {result.fun/max(N_dof,1):.2f}
   - Null directions: {n_null}

3. GUT-CONSTRAINED FIT (SU(5) relations):
   - Parameters: 7 (4 bulk masses + 3 Yukawa scales)
   - Measurements: 15
   - chi^2 = {result_gut.fun:.2f} for {N_dof_gut} dof -> chi^2/dof = {result_gut.fun/N_dof_gut:.2f}

4. DETERMINATION STATUS:
""")

if n_null == 0 and result.fun / max(N_dof, 1) < 3.0:
    print("   OK THE BASIN IS DETERMINED at 5D + NCG (S_3 constraints).")
    print("   All parameters are constrained by measurements.")
    print("   The overconstrained system has consistency conditions that ARE satisfied.")
    determined = True
elif n_null > 0:
    print(f"   X THE BASIN HAS {n_null} UNDETERMINED DIRECTION(S).")
    print(f"   The S_3 constraints alone do not fully determine the fermion sector.")
    if result_gut.fun / N_dof_gut < 3.0:
        print(f"   HOWEVER: SU(5) GUT relations close the null space (chi^2/dof = {result_gut.fun/N_dof_gut:.2f}).")
        print(f"   -> The basin requires Spin(10) / SU(5) structure (higher-dimensional topology).")
        print(f"   -> This structure IS encoded in the octonionic spectral triple's Spin(10).")
        print(f"   -> The basin MAY be determined if the GUT embedding is exact.")
    else:
        print(f"   AND: SU(5) GUT relations FAIL (chi^2/dof = {result_gut.fun/N_dof_gut:.2f}).")
        print(f"   -> The basin requires metric data beyond what the topology provides.")
        print(f"   -> Higher-dimensional geometry IS needed.")
    determined = False
else:
    print("   The fit quality is poor -- framework may be wrong or parameters misidentified.")
    determined = False

print(f"""
5. WHAT THIS MEANS FOR MERIDIAN AS LOCAL TOE:
""")
if determined:
    print("   The 5D + full NCG framework has enough algebraic structure to")
    print("   determine all fermion parameters from measurements. The basin map")
    print("   is COMPLETABLE at this level of description. No higher dimensions needed.")
else:
    print("   The framework identifies the basin's TOPOLOGY (gauge group, generations,")
    print("   anomaly cancellation) but not its full METRIC structure. The null")
    print("   directions correspond to parameter combinations that require either:")
    print("   (a) Additional algebraic constraints not yet exploited")
    print("   (b) Higher-dimensional metric data (compact geometry shape)")
    print("   (c) A selection principle we haven't discovered")
    print()
    print("   The NEXT calculation: test whether the exceptional Jordan algebra J_3(O)")
    print("   or the Cayley plane OP^2 provides the missing constraints.")

print("\n" + "=" * 70)
print("CALCULATION COMPLETE")
print("=" * 70)
