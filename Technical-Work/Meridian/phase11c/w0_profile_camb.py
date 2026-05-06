#!/usr/bin/env python3
"""
w0 Profile + BAO-only Isolation — CAMB Boltzmann
=================================================

Two analyses to diagnose the Meridian w0 tension:

1. BAO-only fit (no CMB, no growth) — isolate what BAO alone says
2. w0 profile at fixed wa=0 — exact sigma(w0) from each data combination

This tells us:
  - How much of the tension is CMB-driven vs BAO-driven
  - The exact sigma at w0 = -0.830 (Meridian) and w0 = -0.933 (model extreme)
  - Whether the cuscuton's mu=Sigma=1 matters for the CMB constraint

Clayton Iggulden-Schnell & Clawd, April 2026
"""

import sys
import numpy as np
import camb
from scipy.optimize import minimize
from scipy.stats import chi2 as chi2_dist

def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)

fprint("=" * 78)
fprint("  w0 PROFILE + BAO-ONLY ISOLATION (CAMB)")
fprint("=" * 78)

# ============================================================================
# Parameters and data (same as wa_tension_camb.py)
# ============================================================================
OMBH2 = 0.02237
MNU = 0.06
C_LIGHT = 299792.458
OMEGA_R = 9.14e-5

BGS_Z = 0.295
BGS_DV_RD = 7.93
BGS_DV_RD_VAR = 0.005625

TRACERS = [
    {'name': 'LRG1',      'z': 0.510, 'DM_rd': 13.62, 'DH_rd': 22.33},
    {'name': 'LRG2',      'z': 0.706, 'DM_rd': 17.86, 'DH_rd': 20.08},
    {'name': 'LRG3+ELG1', 'z': 0.934, 'DM_rd': 21.71, 'DH_rd': 17.88},
    {'name': 'ELG2',       'z': 1.321, 'DM_rd': 27.79, 'DH_rd': 13.82},
    {'name': 'QSO',        'z': 1.484, 'DM_rd': 29.34, 'DH_rd': 13.12},
    {'name': 'Lya',        'z': 2.330, 'DM_rd': 39.71, 'DH_rd':  8.52},
]

COV_BLOCKS = [
    np.array([[2.788900e-2, -3.257752e-2], [-3.257752e-2, 1.806250e-1]]),
    np.array([[3.132900e-2, -2.359764e-2], [-2.359764e-2, 1.089000e-1]]),
    np.array([[2.310400e-2, -1.220377e-2], [-1.220377e-2, 3.724900e-2]]),
    np.array([[1.01124e-1, -3.050065e-2], [-3.050065e-2, 4.8841e-2]]),
    np.array([[5.7760e-1, -1.9608e-1], [-1.9608e-1, 2.66256e-1]]),
    np.array([[2.81961e-1, -2.311496e-2], [-2.311496e-2, 1.0201e-2]]),
]
COV_INV_BLOCKS = [np.linalg.inv(c) for c in COV_BLOCKS]
COV_INV_BGS = 1.0 / BGS_DV_RD_VAR

FSIGMA8_DATA = [
    (0.067, 0.423, 0.055), (0.150, 0.490, 0.145),
    (0.380, 0.497, 0.045), (0.510, 0.458, 0.038),
    (0.610, 0.436, 0.034), (0.760, 0.440, 0.040),
    (1.360, 0.482, 0.116), (0.698, 0.473, 0.041),
    (1.480, 0.462, 0.045),
]

R_OBS, R_SIG = 1.7502, 0.0046
LA_OBS, LA_SIG = 301.471, 0.090
OBH2_OBS, OBH2_SIG = 0.02236, 0.00015
CMB_CORR_INV = np.linalg.inv(
    np.array([[1.0, 0.46, -0.66], [0.46, 1.0, -0.33], [-0.66, -0.33, 1.0]]))

# ============================================================================
# CAMB
# ============================================================================
_cache = {}

def get_camb(H0, Om, w0):
    key = (round(H0, 2), round(Om, 5), round(w0, 5))
    if key in _cache:
        return _cache[key]
    omch2 = Om * (H0/100)**2 - OMBH2
    if omch2 < 0.001:
        return None
    try:
        pars = camb.CAMBparams()
        pars.set_cosmology(H0=H0, ombh2=OMBH2, omch2=omch2, mnu=MNU, omk=0, tau=0.054)
        if abs(w0 + 1) < 1e-5:
            pars.set_dark_energy(w=-1.0, wa=0.0)
        else:
            pars.set_dark_energy(w=w0, wa=0.0, dark_energy_model='ppf')
        results = camb.get_background(pars)
        derived = results.get_derived_params()
        rd = derived['rdrag']
        d = {'rd': rd}
        for z in [BGS_Z] + [tr['z'] for tr in TRACERS]:
            DM = results.comoving_radial_distance(z)
            Hz = results.hubble_parameter(z)
            DH = C_LIGHT / Hz
            d[z] = {'DM_rd': DM/rd, 'DH_rd': DH/rd,
                     'DV_rd': (z * (DM/rd)**2 * (DH/rd))**(1./3.)}
        DM_star = results.comoving_radial_distance(derived['zstar'])
        d['R'] = np.sqrt(Om) * H0 / C_LIGHT * DM_star
        d['lA'] = np.pi * DM_star / derived['rstar']
        _cache[key] = d
        return d
    except Exception:
        return None


def chi2_bao(H0, Om, w0):
    d = get_camb(H0, Om, w0)
    if d is None: return 1e8
    c2 = (d[BGS_Z]['DV_rd'] - BGS_DV_RD)**2 * COV_INV_BGS
    for i, tr in enumerate(TRACERS):
        delta = np.array([d[tr['z']]['DM_rd'] - tr['DM_rd'],
                          d[tr['z']]['DH_rd'] - tr['DH_rd']])
        c2 += float(delta @ COV_INV_BLOCKS[i] @ delta)
    return c2


def chi2_cmb(H0, Om, w0):
    d = get_camb(H0, Om, w0)
    if d is None: return 1e8
    delta = np.array([(d['R'] - R_OBS)/R_SIG, (d['lA'] - LA_OBS)/LA_SIG,
                       (OMBH2 - OBH2_OBS)/OBH2_SIG])
    return float(delta @ CMB_CORR_INV @ delta)


def chi2_growth(Om, w0, sigma8, gamma=0.55):
    GL_x, GL_w = np.polynomial.legendre.leggauss(64)
    def E2(z):
        zp1 = 1 + z
        return Om * zp1**3 + OMEGA_R * zp1**4 + (1 - Om - OMEGA_R) * zp1**(3*(1+w0))
    c2 = 0.0
    for z, fsig_obs, sig in FSIGMA8_DATA:
        Om_z = Om * (1+z)**3 / max(E2(z), 1e-30)
        f_z = Om_z**gamma
        nodes = 0.5 * z * (GL_x + 1.0)
        w = 0.5 * z * GL_w
        Om_arr = Om * (1 + nodes)**3 / np.array([max(E2(zi), 1e-30) for zi in nodes])
        D_ratio = np.exp(-np.sum(w * Om_arr**gamma / (1 + nodes)))
        c2 += ((f_z * sigma8 * D_ratio - fsig_obs) / sig)**2
    return c2


# ============================================================================
# Profile w0 at fixed wa=0 for different data combinations
# ============================================================================

def profile_w0(w0_val, data='all'):
    """Profile (Om, H0, [sigma8]) at fixed w0, wa=0."""
    def objective(theta):
        if data == 'bao':
            Om, H0 = theta
            if Om < 0.15 or Om > 0.50 or H0 < 55 or H0 > 85: return 1e8
            return chi2_bao(H0, Om, w0_val)
        elif data == 'bao+cmb':
            Om, H0 = theta
            if Om < 0.15 or Om > 0.50 or H0 < 55 or H0 > 85: return 1e8
            c2 = chi2_bao(H0, Om, w0_val)
            if c2 > 1e7: return 1e8
            return c2 + chi2_cmb(H0, Om, w0_val)
        else:  # all
            Om, H0, s8 = theta
            if Om < 0.15 or Om > 0.50 or H0 < 55 or H0 > 85 or s8 < 0.5 or s8 > 1.1: return 1e8
            c2 = chi2_bao(H0, Om, w0_val)
            if c2 > 1e7: return 1e8
            c2 += chi2_cmb(H0, Om, w0_val)
            return c2 + chi2_growth(Om, w0_val, s8)

    best_f = 1e8
    best_p = None
    if data == 'bao':
        starts = [[0.31, 67.4], [0.28, 70.0], [0.34, 65.0], [0.25, 72.0], [0.35, 63.0]]
    elif data == 'bao+cmb':
        starts = [[0.31, 67.4], [0.28, 70.0], [0.34, 65.0], [0.30, 69.0]]
    else:
        starts = [[0.31, 67.4, 0.81], [0.28, 70.0, 0.80], [0.34, 65.0, 0.82], [0.30, 69.0, 0.81]]

    for x0 in starts:
        r = minimize(objective, x0, method='Nelder-Mead',
                     options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 5000})
        if r.fun < best_f:
            best_f = r.fun
            best_p = r.x
    return best_f, best_p


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':

    w0_scan = np.array([-1.15, -1.10, -1.05, -1.03, -1.02, -1.01, -1.005,
                         -1.0, -0.995, -0.99, -0.98, -0.97, -0.96, -0.95,
                         -0.93, -0.90, -0.87, -0.85, -0.83, -0.80, -0.75,
                         -0.70, -0.65, -0.60])

    for dataset_label, dataset_key in [('BAO only (13 pts)', 'bao'),
                                        ('BAO + CMB (16 pts)', 'bao+cmb'),
                                        ('BAO + CMB + growth (25 pts)', 'all')]:

        fprint(f"\n{'='*78}")
        fprint(f"  w0 PROFILE AT FIXED wa=0 — {dataset_label}")
        fprint(f"{'='*78}")

        chi2_arr = []
        params_arr = []

        fprint(f"\n{'w0':>8} {'chi2':>10} {'Om':>8} {'H0':>8} {'sig8':>8}")
        fprint("-" * 48)

        for w0 in w0_scan:
            chi2_val, pars = profile_w0(w0, dataset_key)
            chi2_arr.append(chi2_val)
            params_arr.append(pars)
            if dataset_key == 'bao' or dataset_key == 'bao+cmb':
                fprint(f"{w0:8.3f} {chi2_val:10.3f} {pars[0]:8.4f} {pars[1]:8.2f}     ---")
            else:
                fprint(f"{w0:8.3f} {chi2_val:10.3f} {pars[0]:8.4f} {pars[1]:8.2f} {pars[2]:8.4f}")

        chi2_arr = np.array(chi2_arr)
        chi2_min = chi2_arr.min()
        w0_best = w0_scan[np.argmin(chi2_arr)]

        fprint(f"\n  Best fit: w0 = {w0_best:.3f}, chi2 = {chi2_min:.3f}")

        # Key model points
        for w0_test, label in [(-1.0, 'LCDM'), (-0.933, 'Model extreme (eps=0)'),
                                (-0.830, 'Meridian (eps=0.232)')]:
            idx = np.argmin(np.abs(w0_scan - w0_test))
            dchi2 = chi2_arr[idx] - chi2_min
            sigma = np.sqrt(max(dchi2, 0))
            fprint(f"  {label:30s}: w0 = {w0_scan[idx]:.3f}, "
                   f"Delta chi2 = {dchi2:7.3f}, {sigma:.2f} sigma")

        # Interpolate 1-sigma and 2-sigma bounds
        dchi2_arr = chi2_arr - chi2_min
        for nsig, dchi2_target in [(1, 1.0), (2, 4.0)]:
            # Find bounds where dchi2 crosses target
            lo_bound = w0_scan[0]
            hi_bound = w0_scan[-1]
            for i in range(len(w0_scan)-1):
                if dchi2_arr[i] > dchi2_target >= dchi2_arr[i+1]:
                    f = (dchi2_target - dchi2_arr[i+1]) / (dchi2_arr[i] - dchi2_arr[i+1])
                    lo_bound = w0_scan[i+1] + f * (w0_scan[i] - w0_scan[i+1])
                if dchi2_arr[i] <= dchi2_target < dchi2_arr[i+1]:
                    f = (dchi2_target - dchi2_arr[i]) / (dchi2_arr[i+1] - dchi2_arr[i])
                    hi_bound = w0_scan[i] + f * (w0_scan[i+1] - w0_scan[i])
            fprint(f"  {nsig}-sigma range: [{lo_bound:.3f}, {hi_bound:.3f}]")


    # ================================================================
    # SUMMARY
    # ================================================================
    fprint(f"\n{'='*78}")
    fprint("DIAGNOSTIC SUMMARY")
    fprint(f"{'='*78}")
    fprint("""
  The w0 profile at fixed wa=0 reveals where the tension lives:

  BAO ONLY: tells us what distances alone say about w0
  BAO + CMB: shows how much the CMB shift parameters constrain w0
  BAO + CMB + GROWTH: the full combined constraint

  Key question: Is the Meridian model extreme (w0 = -0.933) within the
  2-sigma region of any dataset? If yes, the tension is driven by
  the specific eps_GW value, not the framework itself.

  Key question: How much does the CMB shift the best-fit w0 toward -1?
  If BAO alone prefers w0 significantly away from -1, the CMB is
  pulling the combined fit toward LCDM.
""")

    fprint("Done.")
