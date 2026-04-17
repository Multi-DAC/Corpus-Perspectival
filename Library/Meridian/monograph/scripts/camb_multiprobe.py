"""
CAMB Multi-Probe Refit for Meridian Monograph — v2 with Lee 2025 Covariance
April 1, 2026. Clawd.

Extends the Boltzmann scan with the full multi-probe dataset:
  1. DESI DR2 BAO with Lee 2025 covariance matrices (13 observables:
     1 DV/rd + 6x2 DM/rd,DH/rd pairs, arXiv:2507.01380)
  2. Growth rate fsigma8 (9 measurements from RSD compilations)
  3. Planck H0 prior
  4. Hiramatsu-Kobayashi beta_HK CMB constraint

Scans over w0 directly (since observables depend on w0, not zeta0).
Maps w0 -> zeta0 via zeta0 = C_KK / (1 + w0) at the end.
"""

import numpy as np
import camb
from camb import model
import json
import os
from lee2025_dr2_data import (
    bgs, tracers, cov_blocks, cov_inv_blocks, cov_inv_bgs,
    lee2025_reference
)

# ============================================================
# Physical constants — CORRECTED (d=5 Weyl)
# ============================================================
C_KK = 1.64e-4         # OP#8 definitive (Planck 2018 fiducial q0=-0.5275)
C_KK_err = 0.33e-4     # uncertainty from eps1 cutoff function
eps1 = 0.010
eps1_err = 0.002

# Planck 2018 fiducial
H0_fid = 67.36
ombh2 = 0.02237
omch2 = 0.1200
Omega_m = 0.315
Omega_DE = 0.685
tau = 0.054
ns = 0.9649
As = 2.1e-9
sigma8_planck = 0.811  # Planck 2018

# ============================================================
# DESI DR2 BAO data — now imported from lee2025_dr2_data.py
# Uses Lee 2025 covariance matrices (arXiv:2507.01380)
# 13 observables: 1 DV/rd (BGS) + 6x2 (DM/rd, DH/rd) pairs
# ============================================================

# ============================================================
# fσ₈ compilation (9 data points)
# Sources: 6dFGS, SDSS MGS, BOSS DR12, VIPERS, FastSound, eBOSS
# ============================================================
fsigma8_data = [
    # (z_eff, fsigma8, sigma)
    (0.067, 0.423, 0.055),   # 6dFGS (Beutler et al. 2012)
    (0.150, 0.490, 0.145),   # SDSS MGS (Howlett et al. 2015)
    (0.380, 0.497, 0.045),   # BOSS DR12 z1 (Alam et al. 2017)
    (0.510, 0.458, 0.038),   # BOSS DR12 z2 (Alam et al. 2017)
    (0.610, 0.436, 0.034),   # BOSS DR12 z3 (Alam et al. 2017)
    (0.760, 0.440, 0.040),   # VIPERS (Pezzotta et al. 2017)
    (1.360, 0.482, 0.116),   # FastSound (Okumura et al. 2016)
    (0.698, 0.473, 0.041),   # eBOSS LRG (Hou et al. 2021)
    (1.480, 0.462, 0.045),   # eBOSS QSO (du Mas des Bourboux et al. 2020)
]

# ============================================================
# Planck H₀ prior
# ============================================================
H0_planck = 67.36
H0_planck_sigma = 0.54

# ============================================================
# Hiramatsu-Kobayashi β_HK constraint
# ============================================================
beta_HK_obs = -0.037
beta_HK_sigma = 0.0095


def w0_from_zeta0(zeta0):
    """Perturbative w0 from zeta0."""
    return -1 + C_KK / zeta0


def zeta0_from_w0(w0):
    """Perturbative zeta0 from w0. Valid for w0 > -1."""
    if (1 + w0) <= 1e-10:
        return np.inf
    return C_KK / (1 + w0)


def get_camb_results(w0, H0=H0_fid, need_growth=False):
    """Run CAMB for constant-w dark energy.
    If need_growth=True, also compute matter power spectrum for sigma8(z)."""
    pars = camb.CAMBparams()
    pars.set_cosmology(
        H0=H0, ombh2=ombh2, omch2=omch2, tau=tau,
        mnu=0.06, nnu=3.046
    )
    pars.set_dark_energy(w=w0, wa=0, dark_energy_model='fluid')
    pars.InitPower.set_params(As=As, ns=ns)

    if need_growth:
        # Request power spectra at fsigma8 redshifts
        z_fsig = sorted(set([d[0] for d in fsigma8_data] + [0.0]), reverse=True)
        pars.set_matter_power(redshifts=z_fsig, kmax=2.0)
    else:
        pars.set_matter_power(redshifts=[0], kmax=2.0)

    pars.NonLinear = model.NonLinear_none
    results = camb.get_results(pars)
    return results


def chi2_desi_dr2(results):
    """Compute chi2 for DESI DR2 BAO using Lee 2025 covariance matrices.

    Uses the (DM/rd, DH/rd) basis with full 2x2 covariance blocks per
    tracer, plus a scalar DV/rd for BGS. Total: 13 observables.
    """
    derived = results.get_derived_params()
    rd = derived['rdrag']
    c_km_s = 299792.458

    chi2 = 0.0

    # BGS: scalar DV/rd
    z_bgs = bgs['z_eff']
    DM_bgs = results.comoving_radial_distance(z_bgs)
    Hz_bgs = results.hubble_parameter(z_bgs)
    DH_bgs = c_km_s / Hz_bgs
    DV_pred = (z_bgs * DM_bgs**2 * DH_bgs)**(1./3.) / rd
    delta_bgs = DV_pred - bgs['DV_rd']
    chi2 += delta_bgs**2 * cov_inv_bgs

    # Anisotropic tracers: (DM/rd, DH/rd) with 2x2 covariance
    for i, tr in enumerate(tracers):
        z = tr['z_eff']
        DM_pred = results.comoving_radial_distance(z) / rd
        Hz = results.hubble_parameter(z)
        DH_pred = c_km_s / (Hz * rd)

        delta = np.array([DM_pred - tr['DM_rd'], DH_pred - tr['DH_rd']])
        chi2 += delta @ cov_inv_blocks[i] @ delta

    return chi2


def chi2_fsigma8(results, w0):
    """Compute chi2 for fσ₈ data.
    Uses Linder growth index approximation: f ≈ Ω_m(z)^γ
    with γ = 0.55 + 0.05(1+w₀) (standard wCDM, Linder 2005).
    σ₈(z) from CAMB matter power spectrum."""

    gamma = 0.55 + 0.05 * (1 + w0)

    # Get sigma8 at each redshift from CAMB
    sigma8_z = results.get_sigma8()  # Returns at requested redshifts (in reverse z order)
    z_requested = sorted(set([d[0] for d in fsigma8_data] + [0.0]), reverse=True)

    # Build interpolation table: z -> sigma8
    s8_dict = {}
    for i, z in enumerate(z_requested):
        s8_dict[round(z, 4)] = sigma8_z[i]

    chi2 = 0
    for z_eff, fsig8_obs, sigma in fsigma8_data:
        # Omega_m(z) for the model
        Hz = results.hubble_parameter(z_eff)
        H0_val = results.hubble_parameter(0)
        E2 = (Hz / H0_val)**2
        Omega_m_z = Omega_m * (1 + z_eff)**3 / E2

        # Growth rate f(z)
        f_z = Omega_m_z**gamma

        # sigma8(z) from CAMB — find nearest
        z_key = round(z_eff, 4)
        if z_key in s8_dict:
            s8 = s8_dict[z_key]
        else:
            # Fallback: scale from z=0
            s8_0 = s8_dict.get(0.0, sigma8_planck)
            # Use growth factor approximation
            s8 = s8_0  # conservative fallback

        fsig8_pred = f_z * s8
        chi2 += ((fsig8_pred - fsig8_obs) / sigma)**2

    return chi2


def chi2_H0_prior(H0):
    """Planck H₀ Gaussian prior."""
    return ((H0 - H0_planck) / H0_planck_sigma)**2


def chi2_HK(zeta0):
    """Hiramatsu-Kobayashi β_HK constraint.
    β_HK = -ζ₀/(1+ζ₀) ≈ -ζ₀ for small ζ₀."""
    beta_pred = -zeta0 / (1 + zeta0)
    return ((beta_pred - beta_HK_obs) / beta_HK_sigma)**2


# ============================================================
# Multi-probe scan
# ============================================================
def _run_camb_bao(w0, H0, Om):
    """Run CAMB and return BAO chi2 for given (w0, H0, Om)."""
    omch2_local = Om * (H0/100)**2 - ombh2
    if omch2_local < 0.01 or H0 < 55 or H0 > 80 or Om < 0.15 or Om > 0.50:
        return 1e6
    try:
        pars = camb.CAMBparams()
        pars.set_cosmology(
            H0=H0, ombh2=ombh2, omch2=omch2_local, tau=tau,
            mnu=0.06, nnu=3.046
        )
        pars.set_dark_energy(w=w0, wa=0, dark_energy_model='fluid')
        pars.InitPower.set_params(As=As, ns=ns)
        pars.set_matter_power(redshifts=[0], kmax=2.0)
        pars.NonLinear = model.NonLinear_none
        results = camb.get_results(pars)
        return chi2_desi_dr2(results)
    except Exception:
        return 1e6


def profile_H0_Om(w0, start=None):
    """Profile over (H0, Omega_m) at fixed w0 to minimize BAO chi2.
    If start=(H0, Om) is given, skip grid and go directly to Nelder-Mead.
    Returns (best_H0, best_Om, best_chi2_bao)."""
    from scipy.optimize import minimize

    if start is None:
        # Coarse grid search
        best = (H0_fid, Omega_m, 1e6)
        for H0 in np.linspace(60.0, 75.0, 16):
            for Om in np.linspace(0.22, 0.40, 19):
                c2 = _run_camb_bao(w0, H0, Om)
                if c2 < best[2]:
                    best = (H0, Om, c2)
        x0 = [best[0], best[1]]
    else:
        x0 = list(start)

    def bao_chi2(params):
        return _run_camb_bao(w0, params[0], params[1])

    res = minimize(bao_chi2, x0, method='Nelder-Mead',
                   options={'xatol': 0.05, 'fatol': 0.005, 'maxiter': 200})
    return res.x[0], res.x[1], res.fun


def multi_probe_scan(n_points=200):
    """Scan over w0 from -0.999 to -0.5, profiling over H0 at each w0.
    Uses: DESI DR2 BAO (Lee 2025 cov) + fsigma8 + H0 prior + HK beta."""

    print("=" * 60)
    print("MULTI-PROBE SCAN: chi2(w0) with H0 profiling")
    print("=" * 60)

    w0_arr = np.linspace(-0.999, -0.50, n_points)
    chi2_total = np.zeros(n_points)
    chi2_bao = np.zeros(n_points)
    chi2_fs8 = np.zeros(n_points)
    chi2_h0 = np.zeros(n_points)
    chi2_hk = np.zeros(n_points)
    H0_profile = np.zeros(n_points)
    zeta0_arr = np.zeros(n_points)

    Om_profile = np.zeros(n_points)
    prev_start = None  # warm-start for profiler

    for i, w0 in enumerate(w0_arr):
        zeta0 = zeta0_from_w0(w0)
        zeta0_arr[i] = zeta0

        try:
            # Profile over (H0, Omega_m) — warm-start from previous
            best_H0, best_Om, c2_bao = profile_H0_Om(w0, start=prev_start)
            prev_start = (best_H0, best_Om)
            H0_profile[i] = best_H0
            Om_profile[i] = best_Om

            # Rerun with growth for fsigma8 at profiled cosmology
            omch2_local = best_Om * (best_H0/100)**2 - ombh2
            pars = camb.CAMBparams()
            pars.set_cosmology(
                H0=best_H0, ombh2=ombh2, omch2=omch2_local, tau=tau,
                mnu=0.06, nnu=3.046
            )
            pars.set_dark_energy(w=w0, wa=0, dark_energy_model='fluid')
            pars.InitPower.set_params(As=As, ns=ns)
            z_fsig = sorted(set([d[0] for d in fsigma8_data] + [0.0]), reverse=True)
            pars.set_matter_power(redshifts=z_fsig, kmax=2.0)
            pars.NonLinear = model.NonLinear_none
            results_growth = camb.get_results(pars)
            c2_fs8 = chi2_fsigma8(results_growth, w0)
            c2_h0 = chi2_H0_prior(best_H0)
            c2_hk = chi2_HK(zeta0)

            chi2_bao[i] = c2_bao
            chi2_fs8[i] = c2_fs8
            chi2_h0[i] = c2_h0
            chi2_hk[i] = c2_hk
            chi2_total[i] = c2_bao + c2_fs8 + c2_h0 + c2_hk
        except Exception as e:
            chi2_total[i] = 1e6
            chi2_bao[i] = 1e6
            chi2_fs8[i] = 1e6
            chi2_h0[i] = 1e6
            chi2_hk[i] = 1e6
            H0_profile[i] = H0_fid
            print(f"  CAMB error at w0={w0:.4f}: {e}")

        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{n_points} done (w0={w0:.4f}, H0={H0_profile[i]:.2f}, chi2={chi2_total[i]:.1f})")

    # Find best fit
    idx_best = np.argmin(chi2_total)
    w0_best = w0_arr[idx_best]
    z0_best = zeta0_arr[idx_best]
    chi2_min = chi2_total[idx_best]

    print(f"\nBest fit: w0 = {w0_best:.4f}, zeta0 = {z0_best:.4e}")
    print(f"  chi2_min = {chi2_min:.2f}")
    print(f"    BAO: {chi2_bao[idx_best]:.2f}")
    print(f"    fσ₈: {chi2_fs8[idx_best]:.2f}")
    print(f"    H₀:  {chi2_h0[idx_best]:.2f}")
    print(f"    HK:  {chi2_hk[idx_best]:.2f}")

    # 1-sigma bounds (Δχ² = 1)
    mask_1s = chi2_total < chi2_min + 1
    if np.any(mask_1s):
        w0_1s_lo = w0_arr[mask_1s].min()
        w0_1s_hi = w0_arr[mask_1s].max()
        z0_1s_lo = zeta0_from_w0(w0_1s_lo)
        z0_1s_hi = zeta0_from_w0(w0_1s_hi)
        print(f"\n  1-sigma: w0 in [{w0_1s_lo:.4f}, {w0_1s_hi:.4f}]")
        print(f"           zeta0 in [{z0_1s_hi:.4e}, {z0_1s_lo:.4e}]")

    # 2-sigma bounds (Δχ² = 4)
    mask_2s = chi2_total < chi2_min + 4
    if np.any(mask_2s):
        w0_2s_lo = w0_arr[mask_2s].min()
        w0_2s_hi = w0_arr[mask_2s].max()
        z0_2s_lo = zeta0_from_w0(w0_2s_lo)
        z0_2s_hi = zeta0_from_w0(w0_2s_hi)
        print(f"  2-sigma: w0 in [{w0_2s_lo:.4f}, {w0_2s_hi:.4f}]")
        print(f"           zeta0 in [{z0_2s_hi:.4e}, {z0_2s_lo:.4e}]")

    # JC benchmark evaluation
    w0_jc = w0_from_zeta0(9.64e-4)  # = -0.8455 (perturbative)
    idx_jc = np.argmin(np.abs(w0_arr - w0_jc))
    delta_chi2_jc = chi2_total[idx_jc] - chi2_min
    print(f"\nJC benchmark (zeta0 = 9.64e-4, w0 = {w0_jc:.4f}):")
    print(f"  chi2 = {chi2_total[idx_jc]:.2f}, Delta_chi2 = {delta_chi2_jc:+.2f}")
    print(f"    BAO: {chi2_bao[idx_jc]:.2f}, fσ₈: {chi2_fs8[idx_jc]:.2f}, HK: {chi2_hk[idx_jc]:.2f}")

    # JC with exact w0
    from camb_refit import w0_exact_from_zeta0
    w0_jc_exact = w0_exact_from_zeta0(9.64e-4)
    idx_jc_ex = np.argmin(np.abs(w0_arr - w0_jc_exact))
    delta_chi2_jc_ex = chi2_total[idx_jc_ex] - chi2_min
    print(f"  (exact w0 = {w0_jc_exact:.4f}): chi2 = {chi2_total[idx_jc_ex]:.2f}, Delta_chi2 = {delta_chi2_jc_ex:+.2f}")

    # CAMB benchmark evaluation
    w0_camb = w0_from_zeta0(0.013)
    idx_camb = np.argmin(np.abs(w0_arr - w0_camb))
    delta_chi2_camb = chi2_total[idx_camb] - chi2_min
    print(f"\nCAMB benchmark (zeta0 = 0.013, w0 = {w0_camb:.4f}):")
    print(f"  chi2 = {chi2_total[idx_camb]:.2f}, Delta_chi2 = {delta_chi2_camb:+.2f}")

    # LCDM comparison
    idx_lcdm = np.argmin(np.abs(w0_arr - (-0.999)))
    delta_chi2_lcdm = chi2_total[idx_lcdm] - chi2_min
    print(f"\nLCDM (w0 = -0.999):")
    print(f"  chi2 = {chi2_total[idx_lcdm]:.2f}, Delta_chi2 = {delta_chi2_lcdm:+.2f}")
    print(f"    BAO: {chi2_bao[idx_lcdm]:.2f}, fsig8: {chi2_fs8[idx_lcdm]:.2f}, HK: {chi2_hk[idx_lcdm]:.2f}")
    print(f"  (Lee 2025 reference: LCDM BAO chi2 = {lee2025_reference['LCDM']['chi2_min']:.3f} for {lee2025_reference['LCDM']['dof']} dof)")

    # Non-perturbative w0 = -0.865
    w0_nonpert = -0.865
    idx_np = np.argmin(np.abs(w0_arr - w0_nonpert))
    delta_chi2_np = chi2_total[idx_np] - chi2_min
    print(f"\nNon-perturbative (w0 = {w0_nonpert}):")
    print(f"  chi2 = {chi2_total[idx_np]:.2f}, Delta_chi2 = {delta_chi2_np:+.2f}")
    print(f"    BAO: {chi2_bao[idx_np]:.2f}, fsig8: {chi2_fs8[idx_np]:.2f}, HK: {chi2_hk[idx_np]:.2f}")

    # Perturbative w0 = -0.851
    w0_pert = -0.851
    idx_pt = np.argmin(np.abs(w0_arr - w0_pert))
    delta_chi2_pt = chi2_total[idx_pt] - chi2_min
    print(f"\nPerturbative (w0 = {w0_pert}):")
    print(f"  chi2 = {chi2_total[idx_pt]:.2f}, Delta_chi2 = {delta_chi2_pt:+.2f}")
    print(f"    BAO: {chi2_bao[idx_pt]:.2f}, fsig8: {chi2_fs8[idx_pt]:.2f}, HK: {chi2_hk[idx_pt]:.2f}")

    return {
        'w0': w0_arr.tolist(),
        'zeta0': zeta0_arr.tolist(),
        'H0_profile': H0_profile.tolist(),
        'Om_profile': Om_profile.tolist(),
        'chi2_total': chi2_total.tolist(),
        'chi2_bao': chi2_bao.tolist(),
        'chi2_fsigma8': chi2_fs8.tolist(),
        'chi2_H0': chi2_h0.tolist(),
        'chi2_HK': chi2_hk.tolist(),
        'best_fit': {
            'w0': float(w0_best),
            'zeta0': float(z0_best),
            'chi2': float(chi2_min),
        },
        'JC_benchmark': {
            'w0': float(w0_jc),
            'zeta0': 9.64e-4,
            'chi2': float(chi2_total[idx_jc]),
            'delta_chi2': float(delta_chi2_jc),
        },
        'CAMB_benchmark': {
            'w0': float(w0_camb),
            'zeta0': 0.013,
            'chi2': float(chi2_total[idx_camb]),
            'delta_chi2': float(delta_chi2_camb),
        },
        'LCDM': {
            'w0': -0.999,
            'chi2_total': float(chi2_total[idx_lcdm]),
            'chi2_bao': float(chi2_bao[idx_lcdm]),
            'delta_chi2': float(delta_chi2_lcdm),
        },
        'non_perturbative': {
            'w0': w0_nonpert,
            'chi2_total': float(chi2_total[idx_np]),
            'chi2_bao': float(chi2_bao[idx_np]),
            'delta_chi2': float(delta_chi2_np),
        },
        'perturbative': {
            'w0': w0_pert,
            'chi2_total': float(chi2_total[idx_pt]),
            'chi2_bao': float(chi2_bao[idx_pt]),
            'delta_chi2': float(delta_chi2_pt),
        },
        'lee2025_reference': lee2025_reference,
    }


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print("Meridian Monograph — Multi-Probe CAMB Refit")
    print(f"C_KK = {C_KK:.2e} ± {C_KK_err:.2e}")
    print(f"eps1 = {eps1} ± {eps1_err}")

    w0_jc = w0_from_zeta0(9.64e-4)
    print(f"JC benchmark: zeta0 = 9.64e-4, w0(pert) = {w0_jc:.4f}")
    print(f"CAMB benchmark: zeta0 = 0.013, w0(pert) = {w0_from_zeta0(0.013):.4f}")
    print()

    outdir = os.path.dirname(os.path.abspath(__file__))

    # Run multi-probe scan
    mp_results = multi_probe_scan(n_points=80)

    # Save results
    outfile = os.path.join(outdir, 'camb_multiprobe_results_lee2025.json')
    with open(outfile, 'w') as f:
        json.dump(mp_results, f, indent=2)
    print(f"\nResults saved to {outfile}")
