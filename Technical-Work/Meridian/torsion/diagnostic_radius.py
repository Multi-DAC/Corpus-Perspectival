#!/usr/bin/env python3
"""
Diagnostic: does increasing DOMAIN_R fix the Weitzenböck bound violation?

Test the Rayleigh quotient of φ = 1/P^{5/2} (a known smooth O(-5) section)
at R = 3, 4, 5, 6, 8. The BKN identity requires R(φ) ≥ 10.

If R=5 gives R(φ) > 10, the section-product basis at R=5 will work.
"""

import numpy as np
from math import pi
import sys, time

sys.stdout.reconfigure(encoding='utf-8')

N_MC = 300000
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02

print("=" * 72)
print("RADIUS DIAGNOSTIC — Rayleigh quotient of φ = 1/P^{5/2} on O(-5)")
print("BKN requires R(φ) ≥ 10 on the compact surface")
print("=" * 72)

for DOMAIN_R in [3.0, 4.0, 5.0, 6.0, 8.0, 12.0]:
    rng = np.random.default_rng(RNG_SEED)
    t0 = time.time()

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

    # P and metric
    P = np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2 + 1.0
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

    g11 = JdJ_11/P - JdXb_1*XJ_1/P2
    g12 = JdJ_12/P - JdXb_1*XJ_2/P2
    g21 = np.conj(g12)
    g22 = JdJ_22/P - JdXb_2*XJ_2/P2
    det_g = (g11*g22 - g12*g21).real

    good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
    a_all, b_all, c_all = a_all[good], b_all[good], c_all[good]
    ab, bb, cb = ab[good], bb[good], cb[good]
    P, P2, det_g = P[good], P2[good], det_g[good]
    g11, g12, g21, g22 = g11[good], g12[good], g21[good], g22[good]
    dc_da, dc_db = dc_da[good], dc_db[good]
    dcb_dab, dcb_dbb = dcb_dab[good], dcb_dbb[good]
    dP_da, dP_dab = dP_da[good], dP_dab[good]
    dP_db, dP_dbb = dP_db[good], dP_dbb[good]
    N = len(a_all)

    ds = np.where(det_g > 1e-20, det_g, 1.0)
    ginv11 = (g22/ds).real
    ginv12 = -g12/ds
    ginv21 = -g21/ds
    ginv22 = (g11/ds).real

    domain_vol = (2*DOMAIN_R)**4
    weights = det_g * domain_vol / (3*N_MC)
    vol_est = np.sum(weights)
    vol_exact = 3*pi**2/2

    # ---------- Test function: φ = 1/P^{5/2} for O(-5) ----------
    # φ = P^{-5/2}
    # ∂φ/∂ā = -5/2 · P^{-7/2} · ∂P/∂ā
    # ∂φ/∂b̄ = -5/2 · P^{-7/2} · ∂P/∂b̄
    # conj(φ) = P^{-5/2} (real function)
    # ∂(conj(φ))/∂a = -5/2 · P^{-7/2} · ∂P/∂a
    # ∂(conj(φ))/∂b = -5/2 · P^{-7/2} · ∂P/∂b

    phi = P**(-2.5)
    dphi_dab = -2.5 * P**(-3.5) * dP_dab
    dphi_dbb = -2.5 * P**(-3.5) * dP_dbb
    dphi_da  = -2.5 * P**(-3.5) * dP_da
    dphi_db  = -2.5 * P**(-3.5) * dP_db

    # O(-5) inner product weight: h^{-1} = P^{-(-5)} = P^5
    h_inv = P**5
    w_twist = h_inv * weights

    # M = ∫ |φ|² P^5 dV = ∫ P^{-5} P^5 dV = ∫ dV = Vol(S)
    M_val = np.sum(np.abs(phi)**2 * w_twist)

    # Q = ∫ g^{αβ̄} (∂φ̄/∂z^α)(∂φ/∂z̄^β) P^5 dV
    Q_val = np.sum((
        ginv11 * dphi_da * dphi_dab +
        ginv12 * dphi_da * dphi_dbb +
        ginv21 * dphi_db * dphi_dab +
        ginv22 * dphi_db * dphi_dbb
    ) * w_twist).real

    rayleigh = Q_val / M_val
    dt = time.time() - t0

    status = "PASS" if rayleigh > 9.5 else ("CLOSE" if rayleigh > 8.0 else "FAIL")
    print(f"  R={DOMAIN_R:5.1f}: Vol={vol_est:.4f} ({vol_est/vol_exact:.4f}x)  "
          f"R(φ)={rayleigh:8.4f}  M={M_val:.4f}  Q={Q_val:.4f}  [{status}]  "
          f"({dt:.1f}s, N={N})")

    # Also test φ = ā/P^{5/2}
    phi2 = ab * P**(-2.5)
    # ∂φ/∂ā = P^{-5/2} + ā · (-5/2) P^{-7/2} ∂P/∂ā
    dphi2_dab = P**(-2.5) + ab * (-2.5) * P**(-3.5) * dP_dab
    dphi2_dbb = ab * (-2.5) * P**(-3.5) * dP_dbb
    # ∂(φ̄)/∂a = a's contribution: ∂(a·P^{-5/2})/∂a = P^{-5/2} + a·(-5/2)P^{-7/2}∂P/∂a
    dphi2_da = P**(-2.5) + a_all * (-2.5) * P**(-3.5) * dP_da
    dphi2_db = a_all * (-2.5) * P**(-3.5) * dP_db

    M2 = np.sum(np.abs(phi2)**2 * w_twist)
    Q2 = np.sum((
        ginv11 * dphi2_da * dphi2_dab +
        ginv12 * dphi2_da * dphi2_dbb +
        ginv21 * dphi2_db * dphi2_dab +
        ginv22 * dphi2_db * dphi2_dbb
    ) * w_twist).real

    r2 = Q2 / M2
    s2 = "PASS" if r2 > 9.5 else ("CLOSE" if r2 > 8.0 else "FAIL")
    print(f"         φ=ā/P^{5/2}: R(φ)={r2:8.4f}  [{s2}]")

print(f"\n{'=' * 72}")
print("CONCLUSION")
print("=" * 72)
print("If R(φ) > 10 at some radius, the MC integration is sufficient there.")
print("The first radius where both tests PASS is the minimum for v7.")
