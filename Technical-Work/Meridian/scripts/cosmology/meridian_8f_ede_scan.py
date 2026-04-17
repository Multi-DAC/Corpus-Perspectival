"""
Project Meridian — Phase 8F: Early Dark Energy / Sound Horizon Scan
Clayton & Clawd, March 2026

Key insight: DESI measures D/r_d, not D alone. If the Meridian model
produces early dark energy (from extended K(H)), the sound horizon r_d
shifts. A smaller r_d increases all D/r_d values, potentially improving
the BAO fit and changing the w0-wa landscape.

This script scans delta_r_d from -10% to +5% and re-optimizes at each
value, to determine:
1. Whether a shifted r_d improves the total chi2
2. How much shift is needed to resolve the DESI tension
3. Whether the shift is physically plausible from extended K(H)
"""

import sys
import os
import builtins
import numpy as np
from scipy.optimize import minimize

# Import model functions from 8A solver
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from meridian_8a_methodology import (
    OMEGA_M0, OMEGA_R0, OMEGA_DE0, H0_FIDUCIAL,
    Z_STAR, SIGMA8_FID, C_OVER_H0,
    DESI_BAO_DATA, FSIGMA8_DATA,
    H0_OBS, H0_SIGMA, BETA_HK_CENTER, SIGMA_HK,
    W0_SN_CMB, W0_SN_CMB_SIGMA, WA_SN_CMB, WA_SN_CMB_SIGMA, RHO_W0_WA,
    E_extended, E_lcdm,
    _comoving_chi, compute_H0_CMB, compute_fsigma8,
    fit_CPL
)

R_D_FID = 147.09  # Mpc, Planck 2018 fiducial


def compute_DM_rd(z, gamma_r, alpha_b, lambda0, r_d, n_int=500):
    """D_M(z) / r_d with variable sound horizon."""
    chi = _comoving_chi(z, gamma_r, alpha_b, lambda0, n_int)
    return chi * C_OVER_H0 / r_d


def compute_DV_rd(z, gamma_r, alpha_b, lambda0, r_d, n_int=500):
    """D_V(z) / r_d with variable sound horizon."""
    chi = _comoving_chi(z, gamma_r, alpha_b, lambda0, n_int)
    a_z = 1.0 / (1.0 + z)
    E_z = E_extended(a_z, gamma_r, alpha_b, lambda0)
    D_V = (z * chi**2 / E_z) ** (1.0 / 3.0)
    return D_V * C_OVER_H0 / r_d


def chi2_with_rd(zeta0, gamma_r, alpha_b, lambda0, r_d,
                 include_w_prior=False):
    """chi2 with variable sound horizon r_d."""
    # 1. BAO distances (uses r_d)
    chi2_D = 0.0
    for z_eff, obs, sigma, dtype in DESI_BAO_DATA:
        if dtype == 'DV':
            model = compute_DV_rd(z_eff, gamma_r, alpha_b, lambda0, r_d)
        else:
            model = compute_DM_rd(z_eff, gamma_r, alpha_b, lambda0, r_d)
        chi2_D += ((model - obs) / sigma) ** 2

    # 2. Growth (independent of r_d)
    chi2_f = 0.0
    for z_eff, fs8_obs, sigma in FSIGMA8_DATA:
        fs8_model = compute_fsigma8(z_eff, zeta0, gamma_r, alpha_b, lambda0)
        chi2_f += ((fs8_model - fs8_obs) / sigma) ** 2

    # 3. H0 — note: r_d shift changes inferred H0 from CMB
    # If r_d is smaller, theta_* = r_d/D_A(z*) is preserved by
    # increasing H0. So H0_inferred = H0_fid * (R_D_FID / r_d)
    H0_model_fid = compute_H0_CMB(gamma_r, alpha_b, lambda0)
    H0_model = H0_model_fid * (R_D_FID / r_d)
    chi2_H = ((H0_model - H0_OBS) / H0_SIGMA) ** 2

    # 4. H&K (independent of r_d)
    eps_SW = zeta0 / (1.0 + zeta0) if zeta0 > 0 else 0.0
    beta_HK_model = -eps_SW
    chi2_HK = ((beta_HK_model - BETA_HK_CENTER) / SIGMA_HK) ** 2

    # 5. w0-wa prior (optional)
    w0_model, wa_model, cpl_rms = fit_CPL(gamma_r, alpha_b, lambda0)
    chi2_w = 0.0
    if include_w_prior:
        det = 1.0 - RHO_W0_WA**2
        dw0 = (w0_model - W0_SN_CMB) / W0_SN_CMB_SIGMA
        dwa = (wa_model - WA_SN_CMB) / WA_SN_CMB_SIGMA
        chi2_w = (dw0**2 - 2.0 * RHO_W0_WA * dw0 * dwa + dwa**2) / det

    # 6. r_d prior: Planck measures r_d = 147.09 +/- 0.26 Mpc
    # If we shift r_d, we incur a penalty from CMB
    chi2_rd = ((r_d - R_D_FID) / 0.26) ** 2

    total = chi2_D + chi2_f + chi2_H + chi2_HK + chi2_w + chi2_rd
    return {
        'chi2_D': chi2_D, 'chi2_f': chi2_f,
        'chi2_H': chi2_H, 'chi2_HK': chi2_HK,
        'chi2_w': chi2_w, 'chi2_rd': chi2_rd,
        'chi2_total': total,
        'H0': H0_model, 'w0': w0_model, 'wa': wa_model,
    }


def optimize_at_rd(r_d, n_starts=4, include_w_prior=False):
    """Optimize the 4 model params at fixed r_d."""
    bounds = [
        (0.001, 0.15),   # zeta0
        (0.01, 0.95),    # gamma_r
        (0.01, 5.0),     # alpha_b
        (0.0, 0.55),     # lambda0
    ]

    best_chi2 = 1e10
    best_x = None

    starts = [
        [0.0379, 0.0189, 4.5, 0.0],  # 8A no-prior best
        [0.04, 0.40, 0.5, 0.0],      # high gamma_r
        [0.05, 0.10, 2.0, 0.2],      # with lambda0
        [0.03, 0.05, 3.0, 0.0],      # moderate
    ]

    for x0 in starts:
        def obj(th):
            z0, gr, ab, l0 = th
            if z0 < 0 or gr < 0 or ab < 0 or l0 < 0 or l0 >= OMEGA_DE0:
                return 1e10
            res = chi2_with_rd(z0, gr, ab, l0, r_d,
                              include_w_prior=include_w_prior)
            return res['chi2_total']

        result = minimize(obj, x0, method='Nelder-Mead',
                         options={'maxiter': 3000, 'xatol': 1e-6,
                                  'fatol': 1e-4})

        if result.fun < best_chi2:
            best_chi2 = result.fun
            best_x = result.x.copy()

    return best_x, best_chi2


def main():
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '8f_results.txt')
    outf = open(outpath, 'w', encoding='utf-8')
    _print = builtins.print
    def print(*args, **kwargs):
        _print(*args, **kwargs, file=outf, flush=True)

    print("=" * 70)
    print("  PROJECT MERIDIAN — PHASE 8F: SOUND HORIZON SCAN")
    print("=" * 70)

    # Reference: LCDM at fiducial r_d
    ref = chi2_with_rd(0.0, 0.0, 0.0, 0.0, R_D_FID)
    print(f"\n  Reference LCDM (r_d = {R_D_FID:.2f} Mpc):")
    print(f"    chi2 = {ref['chi2_total']:.2f}  "
          f"(BAO={ref['chi2_D']:.2f}, fs8={ref['chi2_f']:.2f}, "
          f"H0={ref['chi2_H']:.2f}, HK={ref['chi2_HK']:.2f}, "
          f"r_d={ref['chi2_rd']:.2f})")

    # Phase 7 best-fit at fiducial r_d
    p7 = chi2_with_rd(0.0379, 0.0189, 4.5, 0.0, R_D_FID)
    print(f"\n  Phase 7/8A best (r_d = {R_D_FID:.2f} Mpc):")
    print(f"    chi2 = {p7['chi2_total']:.2f}  "
          f"(BAO={p7['chi2_D']:.2f}, fs8={p7['chi2_f']:.2f}, "
          f"H0={p7['chi2_H']:.2f}, HK={p7['chi2_HK']:.2f}, "
          f"r_d={p7['chi2_rd']:.2f})")

    # ============================================================
    # SCAN: vary r_d from -10% to +5% in steps of 1%
    # ============================================================
    print(f"\n{'=' * 70}")
    print(f"  SCAN: Optimize model at each r_d value")
    print(f"{'=' * 70}")
    print(f"\n  {'r_d':>7s}  {'delta%':>6s}  {'chi2':>7s}  "
          f"{'BAO':>6s}  {'fs8':>6s}  {'H0':>6s}  {'HK':>6s}  "
          f"{'r_d_p':>6s}  {'z0':>6s}  {'gr':>6s}  "
          f"{'w0':>7s}  {'wa':>7s}  {'H0_v':>6s}")
    print(f"  {'---':>7s}  {'---':>6s}  {'---':>7s}  "
          f"{'---':>6s}  {'---':>6s}  {'---':>6s}  {'---':>6s}  "
          f"{'---':>6s}  {'---':>6s}  {'---':>6s}  "
          f"{'---':>7s}  {'---':>7s}  {'---':>6s}")

    # Also track LCDM at each r_d for comparison
    scan_results = []
    for delta_pct in np.arange(-10.0, 5.5, 1.0):
        r_d = R_D_FID * (1.0 + delta_pct / 100.0)

        # Optimize model
        best_x, best_chi2 = optimize_at_rd(r_d, n_starts=4)
        z0, gr, ab, l0 = best_x
        res = chi2_with_rd(z0, gr, ab, l0, r_d)

        # LCDM at this r_d
        lcdm = chi2_with_rd(0.0, 0.0, 0.0, 0.0, r_d)

        delta_vs_lcdm = res['chi2_total'] - lcdm['chi2_total']

        print(f"  {r_d:7.2f}  {delta_pct:+5.1f}%  "
              f"{res['chi2_total']:7.2f}  "
              f"{res['chi2_D']:6.2f}  {res['chi2_f']:6.2f}  "
              f"{res['chi2_H']:6.2f}  {res['chi2_HK']:6.2f}  "
              f"{res['chi2_rd']:6.2f}  "
              f"{z0:6.4f}  {gr:6.4f}  "
              f"{res['w0']:7.4f}  {res['wa']:7.4f}  "
              f"{res['H0']:6.2f}")

        scan_results.append({
            'r_d': r_d, 'delta_pct': delta_pct,
            'chi2_model': res['chi2_total'],
            'chi2_lcdm': lcdm['chi2_total'],
            'delta_chi2': delta_vs_lcdm,
            'params': best_x.copy(),
            'res': res,
            'lcdm': lcdm,
        })

    # ============================================================
    # ANALYSIS
    # ============================================================
    print(f"\n{'=' * 70}")
    print(f"  ANALYSIS")
    print(f"{'=' * 70}")

    # Find best r_d for the model
    best = min(scan_results, key=lambda x: x['chi2_model'])
    print(f"\n  Best model chi2 at r_d = {best['r_d']:.2f} Mpc "
          f"({best['delta_pct']:+.1f}%)")
    print(f"    chi2 = {best['chi2_model']:.2f} "
          f"(vs {best['chi2_lcdm']:.2f} for LCDM)")
    print(f"    Delta chi2 vs LCDM = {best['delta_chi2']:.2f}")
    z0, gr, ab, l0 = best['params']
    print(f"    z0={z0:.4f}, gr={gr:.4f}, ab={ab:.4f}, l0={l0:.4f}")
    print(f"    w0={best['res']['w0']:.4f}, wa={best['res']['wa']:.4f}")
    print(f"    H0={best['res']['H0']:.2f} km/s/Mpc")

    # Find best r_d for LCDM
    best_lcdm = min(scan_results, key=lambda x: x['chi2_lcdm'])
    print(f"\n  Best LCDM chi2 at r_d = {best_lcdm['r_d']:.2f} Mpc "
          f"({best_lcdm['delta_pct']:+.1f}%)")
    print(f"    chi2 = {best_lcdm['chi2_lcdm']:.2f}")

    # The key question: does DELTA chi2 (model vs LCDM) improve?
    print(f"\n  Delta chi2 (model - LCDM) at each r_d:")
    for sr in scan_results:
        marker = " ***" if sr['delta_pct'] == best['delta_pct'] else ""
        print(f"    r_d={sr['r_d']:7.2f} ({sr['delta_pct']:+5.1f}%): "
              f"Delta chi2 = {sr['delta_chi2']:+7.2f}{marker}")

    # EDE physics: how much EDE needed for a given r_d shift?
    print(f"\n  EDE PHYSICS:")
    print(f"    r_d = integral_0^z_drag c_s(z)/H(z) dz")
    print(f"    Adding EDE (extra energy at z ~ 3000-5000) increases H,")
    print(f"    decreasing the integral -> smaller r_d.")
    print(f"    f_EDE ~ 2 * |delta_r_d/r_d| is a rough scaling.")
    print(f"    delta_r_d = -5% -> f_EDE ~ 10% (typical EDE models)")
    print(f"    delta_r_d = -3% -> f_EDE ~ 6%")
    print(f"    Planck constraint: f_EDE < 6% at 95% CL (Smith+ 2020)")

    # Verdict
    print(f"\n{'=' * 70}")
    print(f"  VERDICT")
    print(f"{'=' * 70}")
    if best['delta_pct'] < -0.5 and best['chi2_model'] < p7['chi2_total'] - 2.0:
        print(f"  A shifted r_d DOES improve the fit!")
        print(f"  Optimal r_d shift: {best['delta_pct']:+.1f}%")
        f_ede = 2.0 * abs(best['delta_pct']) / 100.0
        print(f"  Required EDE fraction: f_EDE ~ {f_ede:.1%}")
        if f_ede > 0.06:
            print(f"  WARNING: f_EDE > 6% is in tension with Planck CMB")
        else:
            print(f"  This is within Planck EDE bounds (< 6%)")
    elif abs(best['delta_pct']) < 1.0:
        print(f"  No significant improvement from shifting r_d.")
        print(f"  The problem is in w(z), not in the distance calibration.")
    else:
        print(f"  r_d shift helps but incurs large chi2_rd penalty from CMB.")

    print(f"\n{'=' * 70}")
    print(f"  TRACK 8F COMPLETE")
    print(f"{'=' * 70}")

    outf.close()
    _print(f"Results written to {outpath}")


if __name__ == '__main__':
    main()
