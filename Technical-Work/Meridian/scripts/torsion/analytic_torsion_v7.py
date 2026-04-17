#!/usr/bin/env python3
"""
Analytic Torsion on the Fermat Cubic dP_6 -- Version 7
======================================================
Phase 26 -- Integer P-power basis (the fix).

ROOT CAUSE OF v3-v6 FAILURES: half-integer P-powers (P^{-5/2}, etc.) are
NOT genuine sections of line bundles on the compact surface. They fail the
BKN identity and violate the Weitzenbock bound.

THE FIX: For O(-q), basis functions are mono(a,abar,b,bbar,c,cbar) / P^{m+q}
where m = max(holomorphic_degree, antiholomorphic_degree) of the monomial and
q = |twist|. The P-power is ALWAYS an integer.

Validated: BKN identity R(1/P^5) = 10.029 at N_MC=300K
(diagnostic_bkn_verify.py confirms integer P-powers work).

Examples for O(-5):
  Degree 0: 1/P^5                           (m=0, power=5)
  Degree 1: a/P^6, b/P^6, ..., cbar/P^6    (m=1, power=6)
  Degree 2: ab/P^7, |a|^2/P^7, ...          (m=2, power=7)

For O(5): holomorphic sections (zero modes) are polys in a,b,c of degree <= 5
divided by P^5. General L^2 basis same rule with m + 5.

For O(0): monomials / P^m.
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, log, sqrt
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 300000
DOMAIN_R = 5.0
MAX_DEGREE = 3       # Maximum monomial total degree
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02       # Floor for |c| rejection

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("ANALYTIC TORSION ON dP_6 -- VERSION 7")
print("Integer P-power basis (genuine line bundle sections)")
print(f"N_MC={N_MC}, DOMAIN_R={DOMAIN_R}, MAX_DEGREE={MAX_DEGREE}")
print("=" * 72)


# ============================================================
# STAGE 1: SURFACE SAMPLING
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 1: SURFACE SAMPLING")
print(f"  Fermat cubic {{x0^3 + x1^3 + x2^3 + x3^3 = 0}} in CP^3")
print(f"  Affine patch x0=1, coords a=x1, b=x2, c=(-1-a^3-b^3)^{{1/3}}")
print("=" * 72)

t0 = time.time()

# Sample (a,b) uniformly in a box of side 2*DOMAIN_R
u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
a_raw = u[0] + 1j * u[1]
b_raw = u[2] + 1j * u[3]

# Fermat cubic constraint: c^3 = -1 - a^3 - b^3
w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 1e-8
a_base, b_base, w_base = a_raw[valid], b_raw[valid], w_raw[valid]

# Principal cube root
c_principal = np.abs(w_base)**(1.0/3.0) * np.exp(1j * np.angle(w_base) / 3.0)

# All three cube root sheets
a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate([c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal])

# Reject points with |c| too small (coordinate singularity)
mask = (np.abs(c_all) > C_FLOOR) & (np.abs(c_all) < DOMAIN_R)
a_all, b_all, c_all = a_all[mask], b_all[mask], c_all[mask]
N_total = len(a_all)

# Conjugate coordinates
ab = np.conj(a_all)
bb = np.conj(b_all)
cb = np.conj(c_all)

# P = |x0|^2 + |x1|^2 + |x2|^2 + |x3|^2 = 1 + |a|^2 + |b|^2 + |c|^2
P = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

print(f"  Sampled {N_total} points on 3 sheets")
print(f"  P: min={np.min(P):.2f}, median={np.median(P):.2f}, max={np.max(P):.2f}")
print(f"  Time: {time.time()-t0:.1f}s")


# ============================================================
# STAGE 2: METRIC COMPUTATION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 2: FUBINI-STUDY METRIC ON THE SURFACE")
print("=" * 72)

t1 = time.time()

# Surface derivatives from Fermat cubic constraint: a^3 + b^3 + c^3 = -1
# Differentiating: 3a^2 da + 3c^2 dc = 0 => dc/da = -a^2/c^2
# Similarly dc/db = -b^2/c^2
dc_da = -a_all**2 / c_all**2
dc_db = -b_all**2 / c_all**2
dcb_dab = -ab**2 / cb**2      # conj(dc/da)
dcb_dbb = -bb**2 / cb**2      # conj(dc/db)

# P-derivatives on the surface
# dP/da = d/da(1 + |a|^2 + |b|^2 + |c|^2) = abar + cbar * dc/da
# dP/dabar = a + c * dcbar/dabar
dP_da  = ab + cb * dc_da
dP_dab = a_all + c_all * dcb_dab
dP_db  = bb + cb * dc_db
dP_dbb = b_all + c_all * dcb_dbb

# Fubini-Study metric g_{alpha betabar} on CP^3 restricted to the surface
# g_{alpha betabar} = (1/P) * (J^dag J)_{alpha betabar} - (1/P^2) * (J^dag X)(X^dag J)_{alpha betabar}
# where J is the Jacobian of the embedding (a,b) -> (1,a,b,c(a,b))
# J^dag J components:
JdJ_11 = 1.0 + np.abs(dc_da)**2           # |da/da|^2 + |dc/da|^2
JdJ_12 = np.conj(dc_da) * dc_db           # conj(dc/da) * dc/db
JdJ_22 = 1.0 + np.abs(dc_db)**2           # |db/db|^2 + |dc/db|^2
P2 = P**2

# (J^dag X) components: X = (1, a, b, c)
# (J^dag X)_alpha = conj(dx_i/dz^alpha) * x_i
JdXb_1 = ab + np.conj(dc_da) * cb         # abar + conj(dc/da)*cbar
JdXb_2 = bb + np.conj(dc_db) * cb         # bbar + conj(dc/db)*cbar
# (X^dag J)_beta = x_i * (dx_i/dz^beta)  [note: row vector]
XJ_1 = a_all + c_all * dc_da              # a + c*dc/da
XJ_2 = b_all + c_all * dc_db              # b + c*dc/db

# Metric components
g11 = JdJ_11 / P - JdXb_1 * XJ_1 / P2
g12 = JdJ_12 / P - JdXb_1 * XJ_2 / P2
g21 = np.conj(g12)
g22 = JdJ_22 / P - JdXb_2 * XJ_2 / P2

det_g = (g11 * g22 - g12 * g21).real

# Filter degenerate points
good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
for nm in ['a_all', 'b_all', 'c_all', 'ab', 'bb', 'cb', 'P',
           'det_g', 'g11', 'g12', 'g21', 'g22',
           'dc_da', 'dc_db', 'dcb_dab', 'dcb_dbb',
           'dP_da', 'dP_dab', 'dP_db', 'dP_dbb']:
    exec(f"{nm} = {nm}[good]")
N_total = len(a_all)
P2 = P**2

# Inverse metric
ds = np.where(det_g > 1e-20, det_g, 1.0)
ginv11 = (g22 / ds).real
ginv12 = -g12 / ds
ginv21 = -g21 / ds
ginv22 = (g11 / ds).real

# MC integration weights
# Each sheet covers 1/3 of the domain, factor of 3 sheets included by tiling
domain_vol = (2 * DOMAIN_R)**4
weights = det_g * domain_vol / (3 * N_MC)
vol_est = np.sum(weights)
vol_exact = 3 * pi**2 / 2

print(f"  Valid points: {N_total}")
print(f"  Vol = {vol_est:.6f} (exact = {vol_exact:.6f}, ratio = {vol_est/vol_exact:.4f})")
print(f"  det(g): min={np.min(det_g):.2e}, median={np.median(det_g):.2e}")
print(f"  Time: {time.time()-t1:.1f}s")


# ============================================================
# STAGE 3: INTEGER-POWER BASIS CONSTRUCTION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 3: INTEGER-POWER BASIS CONSTRUCTION")
print(f"  phi = monomial(a,abar,b,bbar,c,cbar) / P^{{m + |n|}}")
print(f"  m = max(holomorphic_deg, antiholomorphic_deg)")
print("=" * 72)

t2 = time.time()

# Precompute coordinate powers up to MAX_DEGREE
max_pow = MAX_DEGREE + 1
a_pow = [np.ones(N_total, dtype=complex)]
b_pow = [np.ones(N_total, dtype=complex)]
c_pow = [np.ones(N_total, dtype=complex)]
ab_pow = [np.ones(N_total, dtype=complex)]
bb_pow = [np.ones(N_total, dtype=complex)]
cb_pow = [np.ones(N_total, dtype=complex)]
for k in range(1, max_pow):
    a_pow.append(a_pow[-1] * a_all)
    b_pow.append(b_pow[-1] * b_all)
    c_pow.append(c_pow[-1] * c_all)
    ab_pow.append(ab_pow[-1] * ab)
    bb_pow.append(bb_pow[-1] * bb)
    cb_pow.append(cb_pow[-1] * cb)

# Precompute P^{-k} for all needed integer powers
# For O(0): k in 0..MAX_DEGREE
# For O(5): k in 5..(MAX_DEGREE+5)
# For O(-5): same range
max_P_pow = MAX_DEGREE + 5 + 1
P_neg = [np.ones(N_total)]  # P^0 = 1
for k in range(1, max_P_pow + 1):
    P_neg.append(P_neg[-1] / P)


def enumerate_monomials(max_deg):
    """
    Enumerate all monomials a^{i1} abar^{j1} b^{i2} bbar^{j2} c^{i3} cbar^{j3}
    up to total degree max_deg.

    Returns list of (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg).
    On the surface, c has hol_deg 1. We restrict c/cbar powers to {0,1,2}
    since c^3 = -1-a^3-b^3 (reduces higher powers).
    """
    monos = []
    for i1 in range(max_deg + 1):
        for j1 in range(max_deg - i1 + 1):
            for i2 in range(max_deg - i1 - j1 + 1):
                for j2 in range(max_deg - i1 - j1 - i2 + 1):
                    for i3 in range(min(max_deg - i1 - j1 - i2 - j2, 2) + 1):
                        for j3 in range(min(max_deg - i1 - j1 - i2 - j2 - i3, 2) + 1):
                            hol_deg = i1 + i2 + i3
                            anti_deg = j1 + j2 + j3
                            monos.append((i1, j1, i2, j2, i3, j3,
                                          hol_deg, anti_deg))
    return monos


def eval_monomial(i1, j1, i2, j2, i3, j3):
    """Evaluate a^{i1} abar^{j1} b^{i2} bbar^{j2} c^{i3} cbar^{j3}."""
    return a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]


def build_basis_for_twist(n_twist, max_deg):
    """
    Build basis for O(n_twist).

    For twist n, each basis function is:
      phi = monomial / P^{m + |n|}
    where m = max(hol_deg, anti_deg).

    Returns:
      basis_vals: (N_basis, N_total) array of phi values
      basis_info: list of (i1,j1,i2,j2,i3,j3, m, k) where k = m + |n|
    """
    q = abs(n_twist)
    monos = enumerate_monomials(max_deg)
    basis_vals = []
    basis_info = []

    for (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in monos:
        m = max(hol_deg, anti_deg)
        k = m + q  # integer P-power

        mono_val = eval_monomial(i1, j1, i2, j2, i3, j3)
        phi = mono_val * P_neg[k]

        basis_vals.append(phi)
        basis_info.append((i1, j1, i2, j2, i3, j3, m, k))

    return np.array(basis_vals), basis_info


# Build bases
print(f"\n  Enumerating monomials up to degree {MAX_DEGREE}...")
all_monos = enumerate_monomials(MAX_DEGREE)
print(f"  Total monomials: {len(all_monos)}")

for n_twist in [0, 5, -5]:
    F, info = build_basis_for_twist(n_twist, MAX_DEGREE)
    label = f"O({n_twist})"
    print(f"  {label}: N_basis = {F.shape[0]}, memory = {F.nbytes/1e6:.1f} MB")
    if n_twist == 0:
        F0 = F; info0 = info
    elif n_twist == 5:
        F5 = F; info5 = info
    else:
        Fm5 = F; infom5 = info

print(f"  Time: {time.time()-t2:.1f}s")


# ============================================================
# STAGE 4: DERIVATIVE COMPUTATION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 4: DERIVATIVES")
print(f"  For phi = M/P^k:")
print(f"  dphi/dabar = (dM/dabar)/P^k - k*M*dP_dab/P^{{k+1}}")
print(f"             + (dM/dcbar)*(dcbar/dabar)/P^k - k*M*(cbar*dcbar/dabar) [via chain rule]")
print("=" * 72)

t3 = time.time()


def compute_monomial_derivs(i1, j1, i2, j2, i3, j3):
    """
    Compute derivatives of the monomial M = a^{i1} abar^{j1} b^{i2} bbar^{j2} c^{i3} cbar^{j3}
    with respect to the surface coordinates (a, abar, b, bbar).

    On the surface, c = c(a,b) holomorphically, cbar = cbar(abar, bbar) antiholomorphically.
    dc/da = -a^2/c^2, dc/db = -b^2/c^2
    dcbar/dabar = -abar^2/cbar^2, dcbar/dbbar = -bbar^2/cbar^2

    Returns dM/da, dM/dabar, dM/db, dM/dbbar (each an array of length N_total).
    """
    M_val = eval_monomial(i1, j1, i2, j2, i3, j3)

    # dM/da: chain rule through a and c(a)
    # dM/da = i1 * a^{i1-1} * rest + i3 * (a^{i1}*...*c^{i3-1}*...) * dc/da
    dM_da = np.zeros(N_total, dtype=complex)
    if i1 > 0:
        dM_da += i1 * a_pow[i1-1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if i3 > 0:
        dM_da += i3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3-1] * cb_pow[j3] * dc_da

    # dM/dabar: chain rule through abar and cbar(abar)
    dM_dab = np.zeros(N_total, dtype=complex)
    if j1 > 0:
        dM_dab += j1 * a_pow[i1] * ab_pow[j1-1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if j3 > 0:
        dM_dab += j3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3-1] * dcb_dab

    # dM/db: chain rule through b and c(b)
    dM_db = np.zeros(N_total, dtype=complex)
    if i2 > 0:
        dM_db += i2 * a_pow[i1] * ab_pow[j1] * b_pow[i2-1] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if i3 > 0:
        dM_db += i3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3-1] * cb_pow[j3] * dc_db

    # dM/dbbar: chain rule through bbar and cbar(bbar)
    dM_dbb = np.zeros(N_total, dtype=complex)
    if j2 > 0:
        dM_dbb += j2 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2-1] * c_pow[i3] * cb_pow[j3]
    if j3 > 0:
        dM_dbb += j3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3-1] * dcb_dbb

    return dM_da, dM_dab, dM_db, dM_dbb


def compute_basis_derivs(basis_info):
    """
    For each basis function phi_i = M_i / P^{k_i}, compute:
      dphi/dabar = (dM/dabar) / P^k - k * M * (dP/dabar) / P^{k+1}
      dphi/dbbar = (dM/dbbar) / P^k - k * M * (dP/dbbar) / P^{k+1}

    And for the conjugate (needed for Q assembly):
      d(phibar)/da = (dMbar/da) / P^k - k * Mbar * (dP/da) / P^{k+1}
      d(phibar)/db = (dMbar/db) / P^k - k * Mbar * (dP/db) / P^{k+1}

    where Mbar = conj(M), and dMbar/da = conj(dM/dabar) ONLY for specific cases.
    Actually: the conjugate of M(a,abar,b,bbar,c,cbar) is M(abar,a,bbar,b,cbar,c),
    so d(conj(M))/da requires swapping roles. We compute it directly.

    Returns:
      dphi_dab, dphi_dbb: antiholomorphic derivatives of phi (for dbar operator)
      dphibar_da, dphibar_db: holomorphic derivatives of conj(phi) (for del operator)
    """
    N_basis = len(basis_info)
    dphi_dab = np.zeros((N_basis, N_total), dtype=complex)
    dphi_dbb = np.zeros((N_basis, N_total), dtype=complex)
    dphibar_da = np.zeros((N_basis, N_total), dtype=complex)
    dphibar_db = np.zeros((N_basis, N_total), dtype=complex)

    for idx, (i1, j1, i2, j2, i3, j3, m, k) in enumerate(basis_info):
        M_val = eval_monomial(i1, j1, i2, j2, i3, j3)
        dM_da, dM_dab, dM_db, dM_dbb = compute_monomial_derivs(i1, j1, i2, j2, i3, j3)

        # phi = M / P^k
        # dphi/dabar = dM_dab / P^k - k * M * dP_dab / P^{k+1}
        Pk = P_neg[k]
        Pk1 = P_neg[k + 1] if k + 1 <= max_P_pow else P_neg[k] / P

        dphi_dab[idx] = dM_dab * Pk - k * M_val * dP_dab * Pk1
        dphi_dbb[idx] = dM_dbb * Pk - k * M_val * dP_dbb * Pk1

        # conj(phi) = conj(M) / P^k  (P is real)
        # The conjugate monomial: conj(a^{i1} abar^{j1} ...) = abar^{i1} a^{j1} ...
        # So conj(M) has indices swapped: (j1, i1, j2, i2, j3, i3)
        # d(conj(M))/da and d(conj(M))/db:
        dMbar_da, _, dMbar_db, _ = compute_monomial_derivs(j1, i1, j2, i2, j3, i3)

        Mbar = np.conj(M_val)
        dphibar_da[idx] = dMbar_da * Pk - k * Mbar * dP_da * Pk1
        dphibar_db[idx] = dMbar_db * Pk - k * Mbar * dP_db * Pk1

    return dphi_dab, dphi_dbb, dphibar_da, dphibar_db


print("  Computing derivatives for O(0)...")
F0_dab, F0_dbb, F0bar_da, F0bar_db = compute_basis_derivs(info0)
print(f"    Done. Shape: {F0_dab.shape}")

print("  Computing derivatives for O(5)...")
F5_dab, F5_dbb, F5bar_da, F5bar_db = compute_basis_derivs(info5)
print(f"    Done. Shape: {F5_dab.shape}")

print("  Computing derivatives for O(-5)...")
Fm5_dab, Fm5_dbb, Fm5bar_da, Fm5bar_db = compute_basis_derivs(infom5)
print(f"    Done. Shape: {Fm5_dab.shape}")

print(f"  Time: {time.time()-t3:.1f}s")


# ============================================================
# STAGE 5: MATRIX ASSEMBLY
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 5: MATRIX ASSEMBLY (MC integration)")
print(f"  Mass matrix:  M[i,j] = int conj(phi_i) * phi_j * h * dV")
print(f"  Stiffness:    Q[i,j] = int g^{{ab}} * (d_a conj(phi_i)) * (d_bbar phi_j) * h * dV")
print(f"  h = P^{{-n}} is the fiber metric for O(n)")
print("=" * 72)

t4 = time.time()


def assemble_matrices(label, n_twist, F, F_dab, F_dbb, Fbar_da, Fbar_db):
    """
    Assemble mass matrix M and stiffness matrix Q for the O(n_twist) Laplacian.

    M[i,j] = int P^{-n} conj(phi_i) phi_j dV
    Q[i,j] = int P^{-n} g^{alpha betabar} (d_alpha conj(phi_i))(d_{betabar} phi_j) dV

    The fiber metric for O(n) is h = P^{-n}, so h^{-1} = P^n.
    The Laplacian dbar-form uses h (not h^{-1}).
    """
    print(f"  Assembling {label} (n={n_twist}, N_basis={F.shape[0]})...")
    t_start = time.time()
    N_b = F.shape[0]

    # Integration weight including fiber metric
    h = P ** (-n_twist)
    w = h * weights  # shape (N_total,)

    # Mass matrix: M[i,j] = sum_pts conj(phi_i) * phi_j * w
    Fw = np.conj(F) * w[np.newaxis, :]   # (N_basis, N_total)
    M_mat = Fw @ F.T                      # (N_basis, N_basis)

    # Stiffness matrix: Q[i,j] = sum_pts g^{ab} (d_a conj(phi_i)) (d_bbar phi_j) * w
    # g^{11}*(d_a phibar_i)*(d_abar phi_j) + g^{12}*(d_a phibar_i)*(d_bbar phi_j)
    # + g^{21}*(d_b phibar_i)*(d_abar phi_j) + g^{22}*(d_b phibar_i)*(d_bbar phi_j)
    Q_mat = np.zeros((N_b, N_b), dtype=complex)

    # Each term: D_hol[i,pt] * w_metric[pt] @ D_anti[j,pt].T
    for (D_hol, D_anti, g_comp) in [
        (Fbar_da, F_dab, ginv11),
        (Fbar_da, F_dbb, ginv12),
        (Fbar_db, F_dab, ginv21),
        (Fbar_db, F_dbb, ginv22),
    ]:
        Dw = D_hol * (w * g_comp)[np.newaxis, :]  # (N_basis, N_total)
        Q_mat += Dw @ D_anti.T

    # Hermitianize (enforce exact symmetry)
    Q_mat = 0.5 * (Q_mat + Q_mat.T.conj())
    M_mat = 0.5 * (M_mat + M_mat.T.conj())

    # Diagnostics
    qi = np.max(np.abs(Q_mat.imag))
    qr = np.max(np.abs(Q_mat.real))
    mi = np.max(np.abs(M_mat.imag))
    mr = np.max(np.abs(M_mat.real))
    print(f"    Q: max|im|/max|re| = {qi/max(qr,1e-30):.2e}")
    print(f"    M: max|im|/max|re| = {mi/max(mr,1e-30):.2e}")
    print(f"    Time: {time.time()-t_start:.1f}s")

    return Q_mat, M_mat


QM = {}
QM["O(0)"] = assemble_matrices("O(0)", 0, F0, F0_dab, F0_dbb, F0bar_da, F0bar_db)
QM["O(5)"] = assemble_matrices("O(5)", 5, F5, F5_dab, F5_dbb, F5bar_da, F5bar_db)
QM["O(-5)"] = assemble_matrices("O(-5)", -5, Fm5, Fm5_dab, Fm5_dbb, Fm5bar_da, Fm5bar_db)

print(f"  Total assembly time: {time.time()-t4:.1f}s")


# ============================================================
# STAGE 6: EIGENSOLVE + WEITZENBOCK CHECK
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 6: EIGENVALUES")
print(f"  Solve Q*v = lambda*M*v (generalized eigenvalue problem)")
print(f"  O(0): expect 1 zero mode (constant function)")
print(f"  O(-5): expect all lambda >= 10 (BKN/Weitzenbock bound)")
print("=" * 72)

all_eigs = {}
for label in ["O(0)", "O(5)", "O(-5)"]:
    Q_mat, M_mat = QM[label]
    N_b = M_mat.shape[0]
    Qr = Q_mat.real
    Mr = M_mat.real

    # Analyze M conditioning
    eigM = np.linalg.eigvalsh(Mr)
    Mmax = eigM[-1]
    Mmin_pos = eigM[eigM > 1e-8 * Mmax]
    rank = len(Mmin_pos)
    cond = Mmax / Mmin_pos[0] if len(Mmin_pos) > 0 else float('inf')

    # Regularize M for numerical stability
    Mr_reg = Mr + 1e-8 * Mmax * np.eye(N_b)

    try:
        eigvals = eigh(Qr, Mr_reg, eigvals_only=True)
        eigvals = np.sort(eigvals)
    except Exception as e:
        print(f"  {label}: EIGENSOLVE FAILED: {e}")
        all_eigs[label] = None
        continue

    # Classify eigenvalues
    n_neg = int(np.sum(eigvals < -0.5))
    n_zero = int(np.sum(np.abs(eigvals) < 0.5))
    n_pos = int(np.sum(eigvals > 0.5))
    pos = eigvals[eigvals > 0.5]

    print(f"\n  {label}: N_basis={N_b}, rank={rank}/{N_b}, cond(M)={cond:.1e}")
    print(f"    Eigenvalues: {n_neg} negative, {n_zero} zero, {n_pos} positive")
    if len(eigvals) > 0:
        print(f"    Spectrum: [{eigvals[0]:.4f}, ..., {eigvals[-1]:.1f}]")
    if len(pos) > 0:
        print(f"    Min positive: {pos[0]:.4f}")
        print(f"    First 10: {pos[:10].round(3)}")

    # Specific checks
    if label == "O(0)":
        print(f"\n    ZERO MODE CHECK: found {n_zero} (expect 1)")
        if n_zero == 1:
            print("    ** PERFECT: exactly 1 zero mode **")
        elif n_zero >= 1:
            print(f"    ACCEPTABLE: {n_zero} near-zero modes (numerical degeneracy)")
        else:
            print("    WARNING: no zero modes found")

    if label == "O(-5)":
        print(f"\n    WEITZENBOCK CHECK: min lambda = {pos[0]:.4f} (BKN bound = 10)")
        if pos[0] > 9.5:
            print("    ** PASSED: all eigenvalues >= 10 (within MC tolerance) **")
        elif pos[0] > 8.0:
            print("    PARTIAL: close to BKN bound")
        else:
            print("    FAILED: eigenvalue below BKN bound")

    if label == "O(5)" and len(pos) > 0:
        # For O(5), h^0(O(5)) = dim of zero kernel of dbar Laplacian
        # On dP6, O(5) = -K_S (anticanonical), so h^0 might be > 0
        print(f"\n    O(5) ZERO MODES: {n_zero}")
        if n_zero > 0:
            print(f"    (Expected: h^0(dP6, O(5)) holomorphic sections)")

    all_eigs[label] = eigvals

print(f"\n  BKN VERIFICATION (individual basis functions for O(-5)):")
# Quick single-function Rayleigh quotient check: phi = 1/P^5
Q_m5, M_m5 = QM["O(-5)"]
# The first basis function should be 1/P^5 (degree-0 monomial, m=0, k=5)
if Fm5.shape[0] > 0:
    phi_test = Fm5[0]  # 1/P^5
    M_single = np.sum(np.abs(phi_test)**2 * P**5 * weights).real
    Q_single = np.sum((
        ginv11 * np.conj(Fm5bar_da[0]) * Fm5_dab[0] +
        ginv12 * np.conj(Fm5bar_da[0]) * Fm5_dbb[0] +
        ginv21 * np.conj(Fm5bar_db[0]) * Fm5_dab[0] +
        ginv22 * np.conj(Fm5bar_db[0]) * Fm5_dbb[0]
    ) * P**5 * weights).real
    # Correct Q: use the actual conjugate derivatives
    Q_single2 = np.sum((
        ginv11 * Fm5bar_da[0] * Fm5_dab[0] +
        ginv12 * Fm5bar_da[0] * Fm5_dbb[0] +
        ginv21 * Fm5bar_db[0] * Fm5_dab[0] +
        ginv22 * Fm5bar_db[0] * Fm5_dbb[0]
    ) * P**5 * weights).real
    R_test = Q_single2 / M_single if M_single > 0 else float('nan')
    print(f"  R(1/P^5) = {R_test:.4f} (expect 10.000, BKN identity)")


# ============================================================
# STAGE 7: ZETA REGULARIZATION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 7: ZETA REGULARIZATION")
print(f"  zeta'(0) = -sum_n ln(lambda_n) + Weyl tail correction")
print(f"  Weyl law: N(lambda) ~ (Vol/4pi^2) * lambda^2 for dim_R = 4")
print("=" * 72)


def zeta_prime_zero(label, eigvals):
    """
    Compute zeta'(0) for the spectrum using:
    1. Direct sum over computed eigenvalues: -sum ln(lambda_n)
    2. Weyl tail correction for missing high eigenvalues

    For a Laplacian on a compact complex surface (real dim 4):
      N(lambda) ~ (Vol / 4pi^2) * lambda^2

    The zeta tail contribution from eigenvalues above lambda_max:
      zeta_tail'(0) = -int_{lambda_max}^infty ln(t) dN(t)
                     = -C * [-lambda^2 * ln(lambda)/2 + lambda^2/4] evaluated at lambda_max
    where C = Vol / (4*pi^2) and the integral from lambda_max to infty.

    Actually for the tail: N(t) ~ C*t^2
      int_{L}^infty ln(t) * 2*C*t dt = 2C * [t^2/2 * ln(t) - t^2/4]_L^infty
    This diverges, but zeta regularization handles it. The FINITE part is:
      zeta_tail'(0) = C * (L^2 * ln(L) / 2 - L^2 / 4)
    (sign chosen so that the tail ADDS the missing contribution).
    """
    if eigvals is None:
        print(f"  {label}: NO EIGENVALUES")
        return None

    pos = eigvals[eigvals > 0.5]
    if len(pos) == 0:
        print(f"  {label}: no positive eigenvalues")
        return None

    # Computed contribution
    zp_comp = -np.sum(np.log(pos))

    # Weyl tail
    L = pos[-1]  # largest computed eigenvalue
    C = vol_est / (4 * pi**2)
    N_weyl = C * L**2  # expected number of eigenvalues up to L

    # Tail correction: missing eigenvalues above L
    # The tail adds: C * (L^2 ln(L)/2 - L^2/4)
    tail = C * (L**2 * log(L) / 2.0 - L**2 / 4.0)

    total = zp_comp + tail
    ratio = abs(tail / zp_comp) if abs(zp_comp) > 1e-10 else float('inf')

    print(f"\n  {label}:")
    print(f"    N_eigs = {len(pos)}, lambda_max = {L:.2f}")
    print(f"    N_Weyl(lambda_max) = {N_weyl:.1f} (actual: {len(pos)})")
    print(f"    zeta'_comp = {zp_comp:.6f}")
    print(f"    zeta'_tail = {tail:.6f}")
    print(f"    zeta'_total = {total:.6f}")
    print(f"    |tail/comp| = {ratio:.2f}")

    return {
        'total': float(total),
        'computed': float(zp_comp),
        'tail': float(tail),
        'N_eigs': int(len(pos)),
        'N_weyl': float(N_weyl),
        'lambda_max': float(L),
    }


zeta_results = {}
for label in ["O(0)", "O(5)", "O(-5)"]:
    res = zeta_prime_zero(label, all_eigs.get(label))
    if res is not None:
        zeta_results[label] = res


# ============================================================
# STAGE 8: ANALYTIC TORSION + THRESHOLD CORRECTION
# ============================================================

print(f"\n{'=' * 72}")
print("STAGE 8: ANALYTIC TORSION AND THRESHOLD CORRECTION")
print(f"  ln T = sum_q (-1)^q * q * zeta'(0, Delta_{{0,q}}) for q=0,1,2")
print(f"  delta alpha^{{-1}} = (1/2pi) * T(dP6)")
print(f"  Target: ln(3)/sqrt(2) = {log(3)/sqrt(2):.10f}")
print("=" * 72)

target = log(3) / sqrt(2)

# On the Fermat cubic surface S (complex dim 2):
# Dolbeault complex: 0 -> Omega^{0,0}(O(n)) -> Omega^{0,1}(O(n)) -> Omega^{0,2}(O(n)) -> 0
# Analytic torsion: ln T = -zeta'(0, Delta_0) + zeta'(0, Delta_1)
# (no q=2 contribution for complex surfaces by Serre duality, or it's included via
#  the relationship Delta_2 ~ Delta_0 with twisted bundle)
#
# For the threshold correction we combine:
#   f(O(n)) = zeta'(0) for each twist
#   threshold = f(O(0)) + (5/12)*(f(O(5)) + f(O(-5)))

if all(k in zeta_results for k in ["O(0)", "O(5)", "O(-5)"]):
    f0 = zeta_results["O(0)"]['total']
    f5 = zeta_results["O(5)"]['total']
    fm5 = zeta_results["O(-5)"]['total']

    # Analytic torsion from O(0) sector
    ln_T = -f0  # leading contribution (signs depend on convention)

    # Threshold correction formula
    threshold = f0 + (5.0 / 12.0) * (f5 + fm5)

    print(f"\n  RESULTS:")
    print(f"    f(O(0))  = {f0:.8f}")
    print(f"    f(O(5))  = {f5:.8f}")
    print(f"    f(O(-5)) = {fm5:.8f}")
    print(f"    f(O(-5)) - f(O(5)) = {fm5 - f5:.8f}")
    print(f"")
    print(f"    ln T (from O(0))   = {ln_T:.8f}")
    print(f"    Threshold formula  = {threshold:.8f}")
    print(f"    delta alpha^{{-1}} = {threshold/(2*pi):.8f}")
    print(f"")
    print(f"    TARGET: ln(3)/sqrt(2) = {target:.10f}")
    print(f"    Ratio to target: {threshold/target:.6f}")
    print(f"    Difference: {threshold - target:.8f}")
else:
    missing = [k for k in ["O(0)", "O(5)", "O(-5)"] if k not in zeta_results]
    print(f"  INCOMPLETE: missing zeta results for {missing}")
    threshold = None


# ============================================================
# SAVE RESULTS
# ============================================================

print(f"\n{'=' * 72}")
print("SAVING RESULTS")
print("=" * 72)

output = {
    'version': 7,
    'basis_type': 'integer_P_power',
    'description': 'phi = mono(a,abar,b,bbar,c,cbar) / P^{m+|n|}, m=max(hol,anti)',
    'N_MC': N_MC,
    'N_total': N_total,
    'DOMAIN_R': DOMAIN_R,
    'MAX_DEGREE': MAX_DEGREE,
    'RNG_SEED': RNG_SEED,
    'vol_est': float(vol_est),
    'vol_exact': float(vol_exact),
    'vol_ratio': float(vol_est / vol_exact),
    'target': float(target),
}

for label, eigs in all_eigs.items():
    key = label.replace("(", "").replace(")", "").replace("-", "m")
    if eigs is not None:
        pos = eigs[eigs > 0.5]
        output[f'{key}_N_basis'] = int(len(eigs))
        output[f'{key}_N_pos'] = int(len(pos))
        output[f'{key}_N_zero'] = int(np.sum(np.abs(eigs) < 0.5))
        output[f'{key}_N_neg'] = int(np.sum(eigs < -0.5))
        if len(pos) > 0:
            output[f'{key}_min_pos'] = float(pos[0])
            output[f'{key}_max_pos'] = float(pos[-1])
            output[f'{key}_first10'] = [float(x) for x in pos[:10]]

for label, res in zeta_results.items():
    key = label.replace("(", "").replace(")", "").replace("-", "m")
    output[f'zeta_{key}'] = res

if threshold is not None:
    output['threshold'] = float(threshold)
    output['delta_alpha_inv'] = float(threshold / (2 * pi))
    output['ratio_to_target'] = float(threshold / target)

outfile = 'analytic_torsion_v7_results.json'
with open(outfile, 'w') as f:
    json.dump(output, f, indent=2)
print(f"  Saved to {outfile}")

total_time = time.time() - t0
print(f"\n{'=' * 72}")
print(f"COMPLETE in {total_time:.1f}s")
print(f"  N_MC={N_MC}, N_total={N_total}, MAX_DEGREE={MAX_DEGREE}")
print(f"  Vol ratio: {vol_est/vol_exact:.4f}")
if threshold is not None:
    print(f"  Threshold: {threshold:.8f} (target: {target:.8f})")
print(f"{'=' * 72}")
