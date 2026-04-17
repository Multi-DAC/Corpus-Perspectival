#!/usr/bin/env python3
"""
Analytic Torsion on dP6 -- Version 8
=====================================
Phase B.3: Laplacian eigenvalues with larger basis.

Changes from v7:
  - MAX_DEGREE=4 (196 basis functions vs 82)
  - Sequential per-bundle processing to fit in 32GB RAM
  - DOMAIN_R=5 for good volume coverage (96%)
  - Improved zeta regularization diagnostics
  - Saves full eigenvalue spectra for convergence study

The basis: phi = monomial(a,abar,b,bbar,c,cbar) / P^{m+|n|}
where m = max(holomorphic_deg, antiholomorphic_deg), n = twist.
Integer P-powers only (validated by BKN identity in v7).

Dolbeault complex on S (complex dim 2):
  0 -> Omega^{0,0}(E) -> Omega^{0,1}(E) -> Omega^{0,2}(E) -> 0
  T(S,E) = exp(-zeta'_0(0) + zeta'_1(0)) for line bundle E

For E = O(0): torsion of the trivial bundle.
For threshold correction: combine O(0), O(5), O(-5) per Beasley-Heckman-Vafa.
"""

import numpy as np
from scipy.linalg import eigh
from math import pi, log, sqrt
import json
import sys
import time
import gc

sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# CONFIGURATION
# ============================================================

N_MC = 300000
DOMAIN_R = 5.0
MAX_DEGREE = 4          # 196 basis functions (vs v7's 82)
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02

rng = np.random.default_rng(RNG_SEED)

print("=" * 72)
print("ANALYTIC TORSION ON dP6 -- VERSION 8")
print(f"MAX_DEGREE={MAX_DEGREE} (larger basis for better eigenvalue coverage)")
print(f"N_MC={N_MC}, DOMAIN_R={DOMAIN_R}")
print("=" * 72)


# ============================================================
# STAGE 1: SURFACE SAMPLING (identical to v7)
# ============================================================

print(f"\n{'='*72}")
print("STAGE 1: SURFACE SAMPLING")
print(f"{'='*72}")

t0 = time.time()

u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
a_raw = u[0] + 1j * u[1]
b_raw = u[2] + 1j * u[3]

w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 1e-8
a_base, b_base, w_base = a_raw[valid], b_raw[valid], w_raw[valid]

c_principal = np.abs(w_base)**(1.0/3.0) * np.exp(1j * np.angle(w_base) / 3.0)

a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate([c_principal, ZETA3 * c_principal, ZETA3**2 * c_principal])
P = 1.0 + np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2

mask = (np.abs(c_all) > C_FLOOR) & (P < 500.0)
a_all, b_all, c_all, P = a_all[mask], b_all[mask], c_all[mask], P[mask]
N_total = len(a_all)

ab = np.conj(a_all)
bb = np.conj(b_all)
cb = np.conj(c_all)

print(f"  Points: {N_total}")
print(f"  P: min={np.min(P):.2f}, median={np.median(P):.2f}, max={np.max(P):.2f}")
print(f"  Time: {time.time()-t0:.1f}s")


# ============================================================
# STAGE 2: FS METRIC (identical to v7)
# ============================================================

print(f"\n{'='*72}")
print("STAGE 2: FUBINI-STUDY METRIC")
print(f"{'='*72}")

t1 = time.time()

dc_da = -a_all**2 / c_all**2
dc_db = -b_all**2 / c_all**2
dcb_dab = -ab**2 / cb**2
dcb_dbb = -bb**2 / cb**2

dP_da  = ab + cb * dc_da
dP_dab = a_all + c_all * dcb_dab
dP_db  = bb + cb * dc_db
dP_dbb = b_all + c_all * dcb_dbb

JdJ_11 = 1.0 + np.abs(dc_da)**2
JdJ_12 = np.conj(dc_da) * dc_db
JdJ_22 = 1.0 + np.abs(dc_db)**2
P2 = P**2

JdXb_1 = ab + np.conj(dc_da) * cb
JdXb_2 = bb + np.conj(dc_db) * cb
XJ_1 = a_all + c_all * dc_da
XJ_2 = b_all + c_all * dc_db

g11 = JdJ_11 / P - JdXb_1 * XJ_1 / P2
g12 = JdJ_12 / P - JdXb_1 * XJ_2 / P2
g21 = np.conj(g12)
g22 = JdJ_22 / P - JdXb_2 * XJ_2 / P2

det_g = (g11 * g22 - g12 * g21).real

good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
for nm in ['a_all', 'b_all', 'c_all', 'ab', 'bb', 'cb', 'P',
           'det_g', 'g11', 'g12', 'g21', 'g22',
           'dc_da', 'dc_db', 'dcb_dab', 'dcb_dbb',
           'dP_da', 'dP_dab', 'dP_db', 'dP_dbb']:
    exec(f"{nm} = {nm}[good]")
N_total = len(a_all)
P2 = P**2

ds = np.where(det_g > 1e-20, det_g, 1.0)
ginv11 = (g22 / ds).real
ginv12 = -g12 / ds
ginv21 = -g21 / ds
ginv22 = (g11 / ds).real

domain_vol = (2 * DOMAIN_R)**4
weights = det_g * domain_vol / (3 * N_MC)
vol_est = np.sum(weights)
vol_exact = 3 * pi**2 / 2

print(f"  Valid points: {N_total}")
print(f"  Vol = {vol_est:.6f} (exact = {vol_exact:.6f}, ratio = {vol_est/vol_exact:.4f})")
print(f"  Time: {time.time()-t1:.1f}s")


# ============================================================
# STAGE 3: PRECOMPUTE COORDINATE POWERS
# ============================================================

print(f"\n{'='*72}")
print("STAGE 3: COORDINATE POWERS")
print(f"{'='*72}")

t2 = time.time()

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

# P^{-k} for all needed powers: max is MAX_DEGREE + 5 + 1 = 10
max_P_pow = MAX_DEGREE + 5 + 1
P_neg = [np.ones(N_total)]
for k in range(1, max_P_pow + 1):
    P_neg.append(P_neg[-1] / P)

print(f"  Coordinate powers: 0..{max_pow-1}")
print(f"  P^{{-k}}: k=0..{max_P_pow}")
print(f"  Memory: ~{(12 * max_pow + max_P_pow + 1) * N_total * 16 / 1e9:.1f} GB")
print(f"  Time: {time.time()-t2:.1f}s")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def enumerate_monomials(max_deg):
    """Enumerate monomials up to total degree max_deg with c,cbar powers <= 2."""
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


def compute_monomial_derivs(i1, j1, i2, j2, i3, j3):
    """Compute dM/da, dM/dabar, dM/db, dM/dbbar with chain rule through c(a,b)."""
    dM_da = np.zeros(N_total, dtype=complex)
    if i1 > 0:
        dM_da += i1 * a_pow[i1-1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if i3 > 0:
        dM_da += i3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3-1] * cb_pow[j3] * dc_da

    dM_dab = np.zeros(N_total, dtype=complex)
    if j1 > 0:
        dM_dab += j1 * a_pow[i1] * ab_pow[j1-1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if j3 > 0:
        dM_dab += j3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3-1] * dcb_dab

    dM_db = np.zeros(N_total, dtype=complex)
    if i2 > 0:
        dM_db += i2 * a_pow[i1] * ab_pow[j1] * b_pow[i2-1] * bb_pow[j2] * c_pow[i3] * cb_pow[j3]
    if i3 > 0:
        dM_db += i3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3-1] * cb_pow[j3] * dc_db

    dM_dbb = np.zeros(N_total, dtype=complex)
    if j2 > 0:
        dM_dbb += j2 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2-1] * c_pow[i3] * cb_pow[j3]
    if j3 > 0:
        dM_dbb += j3 * a_pow[i1] * ab_pow[j1] * b_pow[i2] * bb_pow[j2] * c_pow[i3] * cb_pow[j3-1] * dcb_dbb

    return dM_da, dM_dab, dM_db, dM_dbb


def process_bundle(n_twist, max_deg):
    """
    Build basis, compute derivatives, assemble Q and M, eigensolve.
    Returns eigenvalues. All large arrays freed on exit.
    """
    label = f"O({n_twist})"
    q = abs(n_twist)
    monos = enumerate_monomials(max_deg)

    print(f"\n  --- {label} ---")

    # Build basis
    basis_info = []
    F = []
    for (i1, j1, i2, j2, i3, j3, hol_deg, anti_deg) in monos:
        m = max(hol_deg, anti_deg)
        k = m + q
        mono_val = eval_monomial(i1, j1, i2, j2, i3, j3)
        phi = mono_val * P_neg[k]
        F.append(phi)
        basis_info.append((i1, j1, i2, j2, i3, j3, m, k))

    F = np.array(F)
    N_b = F.shape[0]
    print(f"  N_basis = {N_b}, memory = {F.nbytes/1e6:.0f} MB")

    # Compute derivatives
    dphi_dab = np.zeros((N_b, N_total), dtype=complex)
    dphi_dbb = np.zeros((N_b, N_total), dtype=complex)
    dphibar_da = np.zeros((N_b, N_total), dtype=complex)
    dphibar_db = np.zeros((N_b, N_total), dtype=complex)

    for idx, (i1, j1, i2, j2, i3, j3, m, k) in enumerate(basis_info):
        M_val = eval_monomial(i1, j1, i2, j2, i3, j3)
        dM_da, dM_dab, dM_db, dM_dbb = compute_monomial_derivs(i1, j1, i2, j2, i3, j3)

        Pk = P_neg[k]
        Pk1 = P_neg[k + 1] if k + 1 <= max_P_pow else P_neg[k] / P

        dphi_dab[idx] = dM_dab * Pk - k * M_val * dP_dab * Pk1
        dphi_dbb[idx] = dM_dbb * Pk - k * M_val * dP_dbb * Pk1

        # Conjugate basis: swap (i1,j1), (i2,j2), (i3,j3)
        dMbar_da, _, dMbar_db, _ = compute_monomial_derivs(j1, i1, j2, i2, j3, i3)
        Mbar = np.conj(M_val)
        dphibar_da[idx] = dMbar_da * Pk - k * Mbar * dP_da * Pk1
        dphibar_db[idx] = dMbar_db * Pk - k * Mbar * dP_db * Pk1

    print(f"  Derivatives computed. Memory: {4 * dphi_dab.nbytes/1e6:.0f} MB")

    # Assemble mass and stiffness matrices
    h = P ** (-n_twist)
    w = h * weights

    # Mass matrix: M[i,j] = sum conj(phi_i) * phi_j * w
    Fw = np.conj(F) * w[np.newaxis, :]
    M_mat = Fw @ F.T
    del Fw

    # Stiffness matrix: Q[i,j] = sum g^{ab} (d_a phibar_i)(d_bbar phi_j) * w
    Q_mat = np.zeros((N_b, N_b), dtype=complex)
    for (D_hol, D_anti, g_comp) in [
        (dphibar_da, dphi_dab, ginv11),
        (dphibar_da, dphi_dbb, ginv12),
        (dphibar_db, dphi_dab, ginv21),
        (dphibar_db, dphi_dbb, ginv22),
    ]:
        Dw = D_hol * (w * g_comp)[np.newaxis, :]
        Q_mat += Dw @ D_anti.T
        del Dw

    # Hermitianize
    Q_mat = 0.5 * (Q_mat + Q_mat.T.conj())
    M_mat = 0.5 * (M_mat + M_mat.T.conj())

    # Free large arrays
    del F, dphi_dab, dphi_dbb, dphibar_da, dphibar_db
    gc.collect()

    # Diagnostics
    qi = np.max(np.abs(Q_mat.imag))
    qr = np.max(np.abs(Q_mat.real))
    mi = np.max(np.abs(M_mat.imag))
    mr = np.max(np.abs(M_mat.real))
    print(f"  Q: max|im|/max|re| = {qi/max(qr,1e-30):.2e}")
    print(f"  M: max|im|/max|re| = {mi/max(mr,1e-30):.2e}")

    # Eigensolve
    Qr = Q_mat.real
    Mr = M_mat.real
    del Q_mat, M_mat

    eigM = np.linalg.eigvalsh(Mr)
    Mmax = eigM[-1]
    Mmin_pos = eigM[eigM > 1e-8 * Mmax]
    rank = len(Mmin_pos)
    cond = Mmax / Mmin_pos[0] if len(Mmin_pos) > 0 else float('inf')

    Mr_reg = Mr + 1e-8 * Mmax * np.eye(N_b)

    try:
        eigvals = eigh(Qr, Mr_reg, eigvals_only=True)
        eigvals = np.sort(eigvals)
    except Exception as e:
        print(f"  {label}: EIGENSOLVE FAILED: {e}")
        return None, basis_info

    del Qr, Mr, Mr_reg
    gc.collect()

    # Classify
    n_neg = int(np.sum(eigvals < -0.5))
    n_zero = int(np.sum(np.abs(eigvals) < 0.5))
    n_pos = int(np.sum(eigvals > 0.5))
    pos = eigvals[eigvals > 0.5]

    print(f"  {label}: rank={rank}/{N_b}, cond(M)={cond:.1e}")
    print(f"  Eigenvalues: {n_neg} negative, {n_zero} zero, {n_pos} positive")
    if len(eigvals) > 0:
        print(f"  Spectrum: [{eigvals[0]:.4f}, ..., {eigvals[-1]:.1f}]")
    if len(pos) > 0:
        print(f"  Min positive: {pos[0]:.4f}")
        print(f"  First 15: {np.array2string(pos[:15], precision=3, separator=', ')}")

    if label == "O(0)":
        print(f"  ZERO MODE CHECK: found {n_zero} (expect 1)")
    if label == "O(-5)" and len(pos) > 0:
        print(f"  WEITZENBOCK CHECK: min lambda = {pos[0]:.4f} (BKN bound = 10)")

    return eigvals, basis_info


# ============================================================
# STAGE 4: SEQUENTIAL BUNDLE PROCESSING
# ============================================================

print(f"\n{'='*72}")
print("STAGE 4: EIGENVALUE COMPUTATION (sequential per bundle)")
print(f"  Processing O(0), O(5), O(-5) one at a time to save memory")
print(f"{'='*72}")

t3 = time.time()
all_monos = enumerate_monomials(MAX_DEGREE)
print(f"  Total monomials: {len(all_monos)}")

all_eigs = {}
for n_twist in [0, 5, -5]:
    label = f"O({n_twist})"
    eigs, info = process_bundle(n_twist, MAX_DEGREE)
    all_eigs[label] = eigs
    gc.collect()

print(f"\n  Total eigenvalue computation time: {time.time()-t3:.1f}s")


# ============================================================
# STAGE 5: ZETA REGULARIZATION
# ============================================================

print(f"\n{'='*72}")
print("STAGE 5: ZETA REGULARIZATION")
print(f"  zeta'(0) = -sum ln(lambda_n) + Weyl tail correction")
print(f"  Weyl law (real dim 4): N(lambda) ~ (Vol/4pi^2) lambda^2")
print(f"{'='*72}")

C_weyl = vol_est / (4 * pi**2)


def zeta_prime_zero(label, eigvals):
    """Compute zeta'(0) with improved diagnostics."""
    if eigvals is None:
        print(f"  {label}: NO EIGENVALUES")
        return None

    pos = eigvals[eigvals > 0.5]
    if len(pos) == 0:
        print(f"  {label}: no positive eigenvalues")
        return None

    # Computed contribution
    zp_comp = -np.sum(np.log(pos))

    # Weyl analysis
    L = pos[-1]
    N_weyl_L = C_weyl * L**2
    coverage = len(pos) / N_weyl_L if N_weyl_L > 0 else 0

    # Tail correction: integral of -ln(t) dN(t) from L to infinity
    # with N(t) = C * t^2, dN = 2C*t dt
    # int_L^inf ln(t) * 2C*t dt diverges, but zeta-regularized:
    # tail = C * (L^2 * ln(L) - L^2/2)   [finite part]
    # Actually more carefully:
    # zeta_tail'(0) = -int_L^inf ln(t) dN_Weyl(t) (with appropriate regularization)
    # = C(L^2 ln(L)/2 - L^2/4)  [standard heat kernel result]
    tail = C_weyl * (L**2 * log(L) / 2.0 - L**2 / 4.0)
    total = zp_comp + tail

    # Also compute WITHOUT tail for comparison
    ratio = abs(tail / zp_comp) if abs(zp_comp) > 1e-10 else float('inf')

    print(f"\n  {label}:")
    print(f"    N_eigs = {len(pos)}, lambda_max = {L:.2f}")
    print(f"    N_Weyl(lambda_max) = {N_weyl_L:.1f}, coverage = {coverage:.1%}")
    print(f"    zeta'_computed = {zp_comp:.6f}")
    print(f"    zeta'_tail     = {tail:.6f}")
    print(f"    zeta'_total    = {total:.6f}")
    print(f"    |tail/comp| = {ratio:.2f}")

    if coverage < 0.5:
        print(f"    WARNING: coverage {coverage:.0%} < 50% -- tail dominates, result unreliable")
    elif coverage < 0.8:
        print(f"    CAUTION: coverage {coverage:.0%} -- moderate tail contribution")
    else:
        print(f"    GOOD: coverage {coverage:.0%}")

    # Eigenvalue density check: compare dN/dlambda with Weyl prediction
    if len(pos) > 10:
        mid = len(pos) // 2
        lam_mid = pos[mid]
        dlam = pos[mid+5] - pos[mid-5] if mid+5 < len(pos) else pos[-1] - pos[mid-5]
        dn_actual = 10 / dlam if dlam > 0 else 0
        dn_weyl = 2 * C_weyl * lam_mid
        print(f"    Density at lambda={lam_mid:.1f}: actual={dn_actual:.1f}/unit, Weyl={dn_weyl:.1f}/unit")

    return {
        'total': float(total),
        'computed': float(zp_comp),
        'tail': float(tail),
        'N_eigs': int(len(pos)),
        'N_weyl': float(N_weyl_L),
        'coverage': float(coverage),
        'lambda_max': float(L),
        'eigenvalues': [float(x) for x in pos],
    }


zeta_results = {}
for label in ["O(0)", "O(5)", "O(-5)"]:
    res = zeta_prime_zero(label, all_eigs.get(label))
    if res is not None:
        zeta_results[label] = res


# ============================================================
# STAGE 6: ANALYTIC TORSION + THRESHOLD CORRECTION
# ============================================================

print(f"\n{'='*72}")
print("STAGE 6: ANALYTIC TORSION AND THRESHOLD CORRECTION")
target = log(3) / sqrt(2)
print(f"  Target: ln(3)/sqrt(2) = {target:.10f}")
print(f"{'='*72}")

if all(k in zeta_results for k in ["O(0)", "O(5)", "O(-5)"]):
    f0 = zeta_results["O(0)"]['total']
    f5 = zeta_results["O(5)"]['total']
    fm5 = zeta_results["O(-5)"]['total']

    ln_T = -f0
    threshold = f0 + (5.0 / 12.0) * (f5 + fm5)

    # Also compute with COMPUTED part only (no tail) for comparison
    f0_c = zeta_results["O(0)"]['computed']
    f5_c = zeta_results["O(5)"]['computed']
    fm5_c = zeta_results["O(-5)"]['computed']
    threshold_comp = f0_c + (5.0 / 12.0) * (f5_c + fm5_c)

    print(f"\n  RESULTS (with Weyl tail):")
    print(f"    f(O(0))  = {f0:.6f}")
    print(f"    f(O(5))  = {f5:.6f}")
    print(f"    f(O(-5)) = {fm5:.6f}")
    print(f"    Threshold = {threshold:.6f}")
    print(f"    delta alpha^{{-1}} = {threshold/(2*pi):.6f}")
    print(f"    TARGET = {target:.10f}")
    print(f"    Ratio  = {threshold/target:.4f}")

    print(f"\n  RESULTS (computed eigenvalues only, no tail):")
    print(f"    f_comp(O(0))  = {f0_c:.6f}")
    print(f"    f_comp(O(5))  = {f5_c:.6f}")
    print(f"    f_comp(O(-5)) = {fm5_c:.6f}")
    print(f"    Threshold_comp = {threshold_comp:.6f}")

    # Coverage summary
    coverages = [zeta_results[k]['coverage'] for k in ["O(0)", "O(5)", "O(-5)"]]
    min_cov = min(coverages)
    print(f"\n  Coverage: O(0)={coverages[0]:.0%}, O(5)={coverages[1]:.0%}, O(-5)={coverages[2]:.0%}")
    if min_cov < 0.5:
        print(f"  VERDICT: UNRELIABLE -- need more basis functions")
        print(f"  Next: try balanced-section basis (N=361 at k=15) or MAX_DEGREE=5")
    elif min_cov < 0.8:
        print(f"  VERDICT: SUGGESTIVE but not definitive")
    else:
        print(f"  VERDICT: Reasonable estimate")
else:
    missing = [k for k in ["O(0)", "O(5)", "O(-5)"] if k not in zeta_results]
    print(f"  INCOMPLETE: missing {missing}")
    threshold = None


# ============================================================
# SAVE RESULTS
# ============================================================

print(f"\n{'='*72}")
print("SAVING RESULTS")
print(f"{'='*72}")

output = {
    'version': 8,
    'basis_type': 'integer_P_power',
    'MAX_DEGREE': MAX_DEGREE,
    'N_MC': N_MC,
    'N_total': N_total,
    'DOMAIN_R': DOMAIN_R,
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
            output[f'{key}_first20'] = [float(x) for x in pos[:20]]
            output[f'{key}_all_pos'] = [float(x) for x in pos]

for label, res in zeta_results.items():
    key = label.replace("(", "").replace(")", "").replace("-", "m")
    # Don't save full eigenvalues twice
    res_save = {k: v for k, v in res.items() if k != 'eigenvalues'}
    output[f'zeta_{key}'] = res_save

if 'threshold' in dir() and threshold is not None:
    output['threshold_with_tail'] = float(threshold)
    output['threshold_comp_only'] = float(threshold_comp)
    output['ratio_to_target'] = float(threshold / target)

outfile = 'analytic_torsion_v8_results.json'
with open(outfile, 'w') as f:
    json.dump(output, f, indent=2)
print(f"  Saved to {outfile}")

total_time = time.time() - t0
print(f"\n{'='*72}")
print(f"COMPLETE in {total_time:.1f}s")
print(f"  N_basis = {len(all_monos)}, vol_ratio = {vol_est/vol_exact:.4f}")
if 'threshold' in dir() and threshold is not None:
    print(f"  Threshold (with tail): {threshold:.6f}")
    print(f"  Threshold (comp only): {threshold_comp:.6f}")
    print(f"  Target: {target:.10f}")
print(f"{'='*72}")
