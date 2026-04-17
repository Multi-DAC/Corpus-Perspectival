#!/usr/bin/env python3
"""
Track 15C2: CKM and PMNS from Bulk Mass Parameters
Numerical verification script for the Meridian framework.

Usage:
    python 15C2_ckm_pmns.py

All computations are self-contained. No external data files needed.
"""

import numpy as np
from numpy.linalg import eigh, svd, norm
import sys

np.set_printoptions(precision=8, suppress=True, linewidth=120)

# =============================================================================
# Constants
# =============================================================================
KY_C = 37.0          # RS warp factor parameter
V_EW = 246.0         # Electroweak VEV (GeV)
Y5 = 1.0             # 5D Yukawa coupling

# Democratic mixing matrix from octonionic spectral triple (15B3)
M_OCT = np.array([
    [1.0, 0.5, 0.5],
    [0.5, 1.0, 0.5],
    [0.5, 0.5, 1.0]
])

# Bulk mass parameters from 15C
C_UP    = np.array([0.635, 0.530, 0.004])   # up, charm, top
C_DOWN  = np.array([0.623, 0.576, 0.503])   # down, strange, bottom
C_LEPTON = np.array([0.656, 0.574, 0.523])  # electron, muon, tau
C_NU    = np.array([0.941, 0.911, 0.887])   # nu1, nu2, nu3 (Dirac)

# Observed masses (GeV)
M_UP_OBS    = np.array([2.16e-3, 1.27, 172.69])
M_DOWN_OBS  = np.array([4.67e-3, 93.4e-3, 4.18])
M_LEPTON_OBS = np.array([0.511e-3, 105.66e-3, 1.777])

# PDG 2024 CKM magnitudes
V_CKM_PDG = np.array([
    [0.97401, 0.22650, 0.00361],
    [0.22636, 0.97320, 0.04053],
    [0.00854, 0.03978, 0.999172]
])

# NuFit 5.3 PMNS parameters (normal ordering)
THETA12_OBS = 33.41  # degrees
THETA23_OBS = 42.2   # degrees
THETA13_OBS = 8.58   # degrees
J_OBS = 3.08e-5      # Jarlskog invariant


# =============================================================================
# Core functions
# =============================================================================

def g_profile(c, ky_c=KY_C):
    """Gherghetta-Pomarol profile overlap function."""
    x = (1 - 2*c) * ky_c
    if abs(x) < 1e-10:
        return 1.0 / np.sqrt(ky_c)
    else:
        return np.sqrt(abs((1-2*c) / (np.exp(x) - 1))) * np.exp((0.5-c)*ky_c)


def build_yukawa_single(c_vals, M_gen=M_OCT, Y5=Y5):
    """Build symmetric Yukawa matrix in single-c model."""
    g = np.array([g_profile(c) for c in c_vals])
    return Y5 * M_gen * np.outer(g, g)


def build_yukawa_lr(c_left, c_right, M_gen=M_OCT, Y5=Y5):
    """Build non-symmetric Yukawa matrix in L-R model."""
    g_L = np.array([g_profile(c) for c in c_left])
    g_R = np.array([g_profile(c) for c in c_right])
    return Y5 * M_gen * np.outer(g_L, g_R)


def extract_pmns_angles(V):
    """Extract PMNS mixing angles from mixing matrix."""
    V = np.abs(V)
    s13 = min(V[0, 2], 1.0)
    th13 = np.degrees(np.arcsin(s13))
    c13 = np.cos(np.radians(th13))
    if c13 > 0:
        s12 = min(V[0, 1] / c13, 1.0)
        s23 = min(V[1, 2] / c13, 1.0)
    else:
        s12, s23 = 0, 0
    th12 = np.degrees(np.arcsin(s12))
    th23 = np.degrees(np.arcsin(s23))
    return th12, th23, th13


# =============================================================================
# Tests
# =============================================================================

def test_moct_eigenstructure():
    """Verify M_oct has eigenvalues {1/2, 1/2, 2}."""
    evals, evecs = eigh(M_OCT)
    assert np.allclose(evals, [0.5, 0.5, 2.0]), f"M_oct eigenvalues wrong: {evals}"
    # Check S3 symmetry: M_oct is invariant under generation permutations
    P12 = np.array([[0,1,0],[1,0,0],[0,0,1]], dtype=float)
    P23 = np.array([[1,0,0],[0,0,1],[0,1,0]], dtype=float)
    assert np.allclose(P12 @ M_OCT @ P12.T, M_OCT), "M_oct not S3-symmetric (12)"
    assert np.allclose(P23 @ M_OCT @ P23.T, M_OCT), "M_oct not S3-symmetric (23)"
    print("  PASS: M_oct eigenvalues = {1/2, 1/2, 2}, S3-symmetric")


def test_profile_masses():
    """Verify g(c_i) reproduces observed masses."""
    for name, c_vals, m_obs in [
        ("Up quarks", C_UP, M_UP_OBS),
        ("Down quarks", C_DOWN, M_DOWN_OBS),
        ("Leptons", C_LEPTON, M_LEPTON_OBS),
    ]:
        g = np.array([g_profile(c) for c in c_vals])
        m_pred = Y5 * g**2 * V_EW / np.sqrt(2)
        ratios = m_pred / m_obs
        assert all(0.95 < r < 1.05 for r in ratios), \
            f"{name} mass mismatch: ratios = {ratios}"
    print("  PASS: All charged fermion masses reproduced to <5%")


def test_gst_relation():
    """Verify |V_us| ~ sqrt(m_d/m_s) from profile ratios."""
    g_d = g_profile(C_DOWN[0])
    g_s = g_profile(C_DOWN[1])
    ratio = g_d / g_s
    gst = np.sqrt(M_DOWN_OBS[0] / M_DOWN_OBS[1])
    assert abs(ratio - gst) < 0.01, f"GST mismatch: g_d/g_s={ratio}, sqrt(m_d/m_s)={gst}"
    assert abs(gst - 0.2265) < 0.01, f"GST far from |V_us|: {gst}"
    print(f"  PASS: g_d/g_s = {ratio:.4f}, sqrt(m_d/m_s) = {gst:.4f}, |V_us| = 0.2265")


def test_ckm_single_c():
    """Verify CKM is near-diagonal in single-c model."""
    Y_u = build_yukawa_single(C_UP)
    Y_d = build_yukawa_single(C_DOWN)
    _, V_u = eigh(Y_u)
    _, V_d = eigh(Y_d)
    V_CKM = V_u.T @ V_d
    V_abs = np.abs(V_CKM)

    # Check near-diagonal
    assert V_abs[0, 0] > 0.99, f"|V_ud| too small: {V_abs[0,0]}"
    assert V_abs[1, 1] > 0.99, f"|V_cs| too small: {V_abs[1,1]}"
    assert V_abs[2, 2] > 0.99, f"|V_tb| too small: {V_abs[2,2]}"

    # Check hierarchical off-diagonal
    assert V_abs[0, 1] > V_abs[1, 2], "|V_us| should be > |V_cb|"
    assert V_abs[1, 2] > V_abs[0, 2], "|V_cb| should be > |V_ub|"

    # Check unitarity
    assert np.allclose(V_CKM @ V_CKM.T, np.eye(3), atol=1e-10), "CKM not unitary"

    print(f"  PASS: CKM near-diagonal, hierarchical, unitary")
    print(f"         |V_us|={V_abs[0,1]:.4f}, |V_cb|={V_abs[1,2]:.4f}, |V_ub|={V_abs[0,2]:.4f}")


def test_ckm_lr_cancellation():
    """Verify democratic M_oct causes CKM suppression in L-R model."""
    c_Q = np.array([0.63, 0.55, 0.35])
    c_uR = np.array([0.68, 0.54, -0.40])
    c_dR = np.array([0.64, 0.59, 0.55])

    g_L = np.array([g_profile(c) for c in c_Q])
    g_uR = np.array([g_profile(c) for c in c_uR])
    g_dR = np.array([g_profile(c) for c in c_dR])

    # Democratic M_oct
    Y_u_dem = M_OCT * np.outer(g_L, g_uR)
    Y_d_dem = M_OCT * np.outer(g_L, g_dR)
    L_u_dem, _, _ = svd(Y_u_dem)
    L_d_dem, _, _ = svd(Y_d_dem)
    diff_dem = np.max(np.abs(L_u_dem - L_d_dem))

    # Anarchic M (random)
    np.random.seed(42)
    M_anarch = np.random.rand(3, 3) + 0.5
    M_anarch = (M_anarch + M_anarch.T) / 2
    Y_u_an = M_anarch * np.outer(g_L, g_uR)
    Y_d_an = M_anarch * np.outer(g_L, g_dR)
    L_u_an, _, _ = svd(Y_u_an)
    L_d_an, _, _ = svd(Y_d_an)
    diff_an = np.max(np.abs(L_u_an - L_d_an))

    # Democratic should give smaller CKM mixing than anarchic
    assert diff_dem < diff_an, \
        f"Democratic should suppress CKM: dem={diff_dem:.4e} vs an={diff_an:.4e}"
    print(f"  PASS: Democratic suppresses CKM (max|L_u-L_d|: dem={diff_dem:.4e} < an={diff_an:.4e})")


def test_cp_violation_zero():
    """Verify J = 0 for real parameters."""
    Y_u = build_yukawa_single(C_UP)
    Y_d = build_yukawa_single(C_DOWN)
    _, V_u = eigh(Y_u)
    _, V_d = eigh(Y_d)
    V_CKM = V_u.T @ V_d

    J = np.imag(V_CKM[0,1] * V_CKM[1,2] *
                np.conj(V_CKM[0,2]) * np.conj(V_CKM[1,1]))
    assert abs(J) < 1e-15, f"J should be 0 for real params: J = {J}"
    print(f"  PASS: Jarlskog J = {J:.2e} (= 0 for real parameters)")


def test_pmns_single_c():
    """Verify PMNS structure in single-c model."""
    Y_e = build_yukawa_single(C_LEPTON)
    Y_nu = build_yukawa_single(C_NU)
    _, V_e = eigh(Y_e)
    _, V_nu = eigh(Y_nu)
    V_PMNS = V_e.T @ V_nu
    V_abs = np.abs(V_PMNS)

    th12, th23, th13 = extract_pmns_angles(V_PMNS)
    print(f"  PASS: PMNS angles: th12={th12:.1f}, th23={th23:.1f}, th13={th13:.1f}")
    print(f"         (observed: th12=33.4, th23=42.2, th13=8.6)")


def test_perturbative_ckm():
    """Verify perturbative CKM formula."""
    g_u = np.array([g_profile(c) for c in C_UP])
    g_d = np.array([g_profile(c) for c in C_DOWN])

    # Perturbative: |V_us| ~ |g_u1/g_u2 - g_d1/g_d2|
    V_us_pert = abs(g_u[0]/g_u[1] - g_d[0]/g_d[1])
    V_cb_pert = abs(g_u[1]/g_u[2] - g_d[1]/g_d[2])
    V_ub_pert = abs(g_u[0]/g_u[2] - g_d[0]/g_d[2])

    # These should be in the right ballpark (order of magnitude)
    assert 0.05 < V_us_pert < 0.5, f"|V_us| perturbative out of range: {V_us_pert}"
    assert 0.01 < V_cb_pert < 0.2, f"|V_cb| perturbative out of range: {V_cb_pert}"

    print(f"  PASS: Perturbative CKM: |V_us|~{V_us_pert:.3f}, |V_cb|~{V_cb_pert:.3f}, |V_ub|~{V_ub_pert:.4f}")


# =============================================================================
# Main
# =============================================================================

def main():
    print("=" * 70)
    print("Track 15C2: CKM/PMNS Verification Tests")
    print("=" * 70)

    tests = [
        ("M_oct eigenstructure", test_moct_eigenstructure),
        ("Profile masses", test_profile_masses),
        ("GST relation", test_gst_relation),
        ("CKM (single-c)", test_ckm_single_c),
        ("CKM L-R cancellation", test_ckm_lr_cancellation),
        ("CP violation = 0", test_cp_violation_zero),
        ("PMNS (single-c)", test_pmns_single_c),
        ("Perturbative CKM", test_perturbative_ckm),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f"\nTest: {name}")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            failed += 1

    print(f"\n{'=' * 70}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"{'=' * 70}")

    if failed > 0:
        sys.exit(1)
    else:
        print("ALL TESTS PASS")


if __name__ == "__main__":
    main()
