#!/usr/bin/env python3
"""
BKN Verification Diagnostic.

For f = 1/P^5 as a section of O(-5), the BKN identity gives:
  Q_{dbar}(f) = Q_{del_A}(f) + 10*M(f)
where Q_{del_A} = ||del_A f||^2 = 0 (since del_A(1/P^5) = 0 exactly).

Therefore R(f) = Q/M = 10 EXACTLY.

Any deviation from 10 is a computational error. This script traces the error.
"""

import numpy as np
from math import pi
import sys, time

sys.stdout.reconfigure(encoding='utf-8')

RNG_SEED = 2026
DOMAIN_R = 5.0
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02

print("=" * 72)
print("BKN VERIFICATION — R(1/P^5) must be exactly 10")
print("=" * 72)

for N_MC in [100000, 300000, 1000000]:
    rng = np.random.default_rng(RNG_SEED)
    u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
    a_raw = u[0] + 1j * u[1]
    b_raw = u[2] + 1j * u[3]
    w_raw = -1.0 - a_raw**3 - b_raw**3
    valid = np.abs(w_raw) > 1e-8
    a_base, b_base, w_base = a_raw[valid], b_raw[valid], w_raw[valid]
    c_principal = np.abs(w_base)**(1/3) * np.exp(1j * np.angle(w_base) / 3)
    a_all = np.tile(a_base, 3)
    b_all = np.tile(b_base, 3)
    c_all = np.concatenate([c_principal, ZETA3*c_principal, ZETA3**2*c_principal])
    mask = np.abs(c_all) > C_FLOOR
    a_all, b_all, c_all = a_all[mask], b_all[mask], c_all[mask]
    ab, bb, cb = np.conj(a_all), np.conj(b_all), np.conj(c_all)
    N = len(a_all)
    P = np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2 + 1.0

    # Surface derivatives
    dc_da = -a_all**2 / c_all**2
    dc_db = -b_all**2 / c_all**2
    dcb_dab = -ab**2 / cb**2
    dcb_dbb = -bb**2 / cb**2

    # dP/dz^alpha (holomorphic surface derivatives)
    dP_da  = ab + cb * dc_da      # dP/da = abar + cbar * dc/da
    dP_db  = bb + cb * dc_db      # dP/db = bbar + cbar * dc/db
    # dP/dz^{bar beta} (antiholomorphic surface derivatives)
    dP_dab = a_all + c_all * dcb_dab  # dP/dabar = a + c * dcbar/dabar
    dP_dbb = b_all + c_all * dcb_dbb  # dP/dbbar = b + c * dcbar/dbbar

    # Verify: conj(dP/da) should equal dP/dabar (since P is real)
    err_conj = np.max(np.abs(np.conj(dP_da) - dP_dab))
    print(f"\n  N_MC={N_MC:>7d}: conj consistency |conj(dP/da) - dP/dabar| = {err_conj:.2e}")

    # Metric components
    JdJ_11 = 1.0 + np.abs(dc_da)**2
    JdJ_12 = np.conj(dc_da) * dc_db
    JdJ_22 = 1.0 + np.abs(dc_db)**2
    P2 = P**2

    JdXb_1 = ab + np.conj(dc_da) * cb
    JdXb_2 = bb + np.conj(dc_db) * cb
    XJ_1 = a_all + c_all * dc_da
    XJ_2 = b_all + c_all * dc_db

    g11 = JdJ_11/P - JdXb_1*XJ_1/P2
    g12 = JdJ_12/P - JdXb_1*XJ_2/P2
    g21 = np.conj(g12)
    g22 = JdJ_22/P - JdXb_2*XJ_2/P2
    det_g = (g11*g22 - g12*g21).real

    good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
    for nm in ['a_all','b_all','c_all','ab','bb','cb','P','P2','det_g',
               'g11','g12','g21','g22','dc_da','dc_db','dcb_dab','dcb_dbb',
               'dP_da','dP_dab','dP_db','dP_dbb','JdJ_11','JdJ_12','JdJ_22',
               'JdXb_1','JdXb_2','XJ_1','XJ_2']:
        exec(f"{nm}={nm}[good]")
    N = len(a_all)

    ds = np.where(det_g > 1e-20, det_g, 1.0)
    ginv11 = (g22/ds).real
    ginv12 = -g12/ds
    ginv21 = -g21/ds
    ginv22 = (g11/ds).real

    domain_vol = (2*DOMAIN_R)**4
    weights = det_g * domain_vol / (3*N_MC)

    # ---- Test: f = 1/P^5, BKN says R = 10 ----
    f = P**(-5.0)
    # df/da = -5*P^{-6}*dP_da, df/dabar = -5*P^{-6}*dP_dab
    df_da  = -5.0 * P**(-6.0) * dP_da
    df_db  = -5.0 * P**(-6.0) * dP_db
    df_dab = -5.0 * P**(-6.0) * dP_dab
    df_dbb = -5.0 * P**(-6.0) * dP_dbb

    # O(-5) fiber metric weight
    h_inv = P**5  # h = P^{-(-5)} = P^5
    w_twist = h_inv * weights

    # M = int P^5 |f|^2 dV
    M = np.sum(np.abs(f)**2 * w_twist).real

    # Q_{dbar} = int g^{alpha bar{beta}} P^5 (d_alpha fbar)(d_{bar beta} f) dV
    # For f real: d_alpha fbar = df_da (holomorphic deriv of f)
    #              d_{bar beta} f = df_dab, df_dbb
    integrand_Q = (
        ginv11 * df_da * df_dab +
        ginv12 * df_da * df_dbb +
        ginv21 * df_db * df_dab +
        ginv22 * df_db * df_dbb
    )
    Q = np.sum(integrand_Q * w_twist).real

    R = Q / M
    print(f"    Q = {Q:.10e}, M = {M:.10e}, R = {R:.6f} (expect 10.000)")

    # ---- Decompose: verify del_A f = 0 ----
    # del_A f = df/dz^alpha + 5*(dP/dz^alpha / P) * f
    dAf_1 = df_da + 5.0 * (dP_da / P) * f   # should be 0
    dAf_2 = df_db + 5.0 * (dP_db / P) * f   # should be 0
    print(f"    |del_A f|: max = {max(np.max(np.abs(dAf_1)), np.max(np.abs(dAf_2))):.2e}")

    # Q_{del_A} = int g^{ab} P^5 |del_A f|^2 ... compute it
    dAf_1_conj = np.conj(dAf_1)
    dAf_2_conj = np.conj(dAf_2)
    Q_delA = np.sum((
        ginv11 * dAf_1_conj * np.conj(dAf_1) +
        ginv12 * dAf_1_conj * np.conj(dAf_2) +
        ginv21 * dAf_2_conj * np.conj(dAf_1) +
        ginv22 * dAf_2_conj * np.conj(dAf_2)
    ) * w_twist).real
    print(f"    Q_delA = {Q_delA:.2e} (should be ~0)")

    # BKN check: Q = Q_delA + 10*M
    bkn_rhs = Q_delA + 10.0 * M
    print(f"    BKN: Q = {Q:.6e}, Q_delA + 10M = {bkn_rhs:.6e}, diff = {abs(Q - bkn_rhs):.2e}")

    # ---- Trace the discrepancy ----
    # The identity g^{ab} (dP_da)(dP_dab) = P * sum_i |dz_i/da|^2 * (partial^2 P / ...)
    # Let's compute the KEY quantity: g^{ab} (dP_da)(dP_db) and compare to known values

    # g^{ab} dP_a dP_ab^bar = ||grad_S P||^2 (squared gradient of P in the surface metric)
    grad_P_sq = (ginv11 * dP_da * dP_dab +
                 ginv12 * dP_da * dP_dbb +
                 ginv21 * dP_db * dP_dab +
                 ginv22 * dP_db * dP_dbb)

    # Q = 25 int P^{-7} grad_P_sq dV, M = int P^{-5} dV
    # BKN: Q = 10M means 25 * <grad_P_sq / P^7> = 10 * <1/P^5>
    # i.e., <grad_P_sq / P^2> = (2/5) <1>   (where <> is w.r.t. P^{-5} dV)

    # Check the identity: g^{ab} dP_a dP_ab = ||dP||^2_g
    # On the FS metric restricted to S: g^{ab} dP_a dP_bbar
    # There's a known identity: for P = 1 + |z|^2 in CP^m (unrestricted):
    #   g^{ij} (dP/dz^i)(dP/dzbar^j) = P * (dim + 1) - |z|^2 - ... hmm

    # Just print stats
    gPsq_mean = np.sum(grad_P_sq.real * weights) / np.sum(weights)
    P_mean = np.sum(P * weights) / np.sum(weights)
    print(f"    <||grad P||^2_g> = {gPsq_mean:.4f}, <P> = {P_mean:.4f}")
    print(f"    Ratio <grad_P^2/P^2> = {np.sum((grad_P_sq/P**2).real * w_twist) / M:.6f} (expect 2/5 = 0.4)")

    # ---- Alternative: compute Q using integration by parts ----
    # Q = int g^{ab} P^5 (da fbar)(dab f) dV
    # For f = P^{-5}: da fbar = -5 P^{-6} dP_da, dab f = -5 P^{-6} dP_dab
    # So Q = 25 int g^{ab} P^{5-12} dP_a dP_ab dV = 25 int g^{ab} P^{-7} dP_a dP_ab dV
    # Alternative via Laplacian: Q = -int fbar * Delta f * P^5 dV
    # where Delta f = -g^{ab} [da dab f + (da log h)(dab f)]
    # = -g^{ab} [da dab(1/P^5) + 5(dP_a/P)(dab(1/P^5))]
    # da(dab(1/P^5)) = da(-5 P^{-6} dP_ab) = -5 [-6 P^{-7} dP_a dP_ab + P^{-6} da(dP_ab)]
    # This is getting complicated. Let me just check the VOLUME normalization.

    vol_est = np.sum(weights)
    vol_exact = 3 * pi**2 / 2
    print(f"    Vol = {vol_est:.6f} (exact {vol_exact:.6f}, ratio {vol_est/vol_exact:.6f})")

    # ---- KEY TEST: does the integrand of Q match 10 * integrand of M pointwise? ----
    # If BKN holds pointwise (it doesn't — it's a global identity), we'd have
    # g^{ab} P^5 (da f)(dab f) = 10 * P^5 |f|^2 at each point.
    # This would mean g^{ab} |df/dz^a|^2 = 10 |f|^2.
    # For f = 1/P^5: 25 g^{ab} dP_a dP_ab / P^12 = 10/P^10
    # i.e., g^{ab} dP_a dP_ab = (2/5) P^2.
    #
    # This is an IDENTITY that should hold at every point of S if BKN is pointwise.
    # But BKN is typically NOT pointwise — it's an operator identity, so it holds
    # after integration by parts. Let's check.

    ratio_pointwise = (grad_P_sq.real) / (0.4 * P**2)
    print(f"    Pointwise ratio (should be 1 if identity holds): "
          f"mean={np.mean(ratio_pointwise):.4f}, "
          f"std={np.std(ratio_pointwise):.4f}, "
          f"min={np.min(ratio_pointwise):.4f}, "
          f"max={np.max(ratio_pointwise):.4f}")

print(f"\n{'=' * 72}")
print("ANALYSIS")
print("=" * 72)
print("If R converges to 10 with increasing N_MC: MC sampling issue.")
print("If R stays at ~8.7: systematic error in the computation.")
print("If pointwise ratio != 1: BKN is NOT pointwise, only global.")
print("  (In that case, integration by parts terms might be missed.)")
print("")
print("KEY INSIGHT: The BKN identity is an OPERATOR identity: □_dbar = □_del + 10.")
print("  Taking inner products: <f, □_dbar f> = <f, □_del f> + 10<f,f>")
print("  i.e., Q_dbar(f) = Q_del(f) + 10*M(f)")
print("  This holds AFTER integration by parts. The Dirichlet form Q_dbar")
print("  involves the WEAK form: Q = int g^ab h (d_a fbar)(d_bbar f) dV.")
print("  On a COMPACT manifold, this equals <f, □_dbar f> with no boundary terms.")
print("  If we're integrating over a NON-COMPACT domain (affine chart), we MISS")
print("  the boundary terms at infinity!")
