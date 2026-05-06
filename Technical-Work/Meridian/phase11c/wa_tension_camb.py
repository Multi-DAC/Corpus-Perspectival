#!/usr/bin/env python3
"""
Item 4: w_a Tension Resolution — CAMB Boltzmann Analysis
=========================================================

Uses CAMB for Boltzmann-accurate distances, validated against analytical.
Strategy: CAMB for the 3 key model fits + profile likelihood.
Analytical (CAMB-validated) for Monte Carlo template artifact test.

Corrected Meridian parameters (from product heat kernel + V_bulk scan):
  epsilon_GW = 0.232, mu^2 = 0.097 k^2, zeta_0 = 8.82e-4
  w_0 = -0.830, w_a = 0 (exactly)

Clayton Iggulden-Schnell & Clawd, April 2026
"""

import sys
import numpy as np
import camb
from scipy.optimize import minimize, differential_evolution
from scipy.stats import chi2 as chi2_dist

# Force unbuffered output
def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)

fprint("=" * 78)
fprint("  ITEM 4: w_a TENSION RESOLUTION — CAMB BOLTZMANN ANALYSIS")
fprint("  CAMB version:", camb.__version__)
fprint("=" * 78)

# ============================================================================
# MERIDIAN PARAMETERS (corrected — product heat kernel, April 2026)
# ============================================================================
EPS1 = 0.010
W0_MERIDIAN = -0.830
WA_MERIDIAN = 0.0
ZETA0_MERIDIAN = 8.82e-4

H0_FID = 67.36
OM_FID = 0.315
OMBH2 = 0.02237
SIGMA8_FID = 0.811
MNU = 0.06
C_LIGHT = 299792.458
OMEGA_R = 9.14e-5

# ============================================================================
# DESI DR2 BAO DATA — Lee 2025 covariance
# ============================================================================
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
    (0.067, 0.423, 0.055),
    (0.150, 0.490, 0.145),
    (0.380, 0.497, 0.045),
    (0.510, 0.458, 0.038),
    (0.610, 0.436, 0.034),
    (0.760, 0.440, 0.040),
    (1.360, 0.482, 0.116),
    (0.698, 0.473, 0.041),
    (1.480, 0.462, 0.045),
]

# CMB compressed likelihood (Planck 2018)
R_OBS, R_SIG = 1.7502, 0.0046
LA_OBS, LA_SIG = 301.471, 0.090
OBH2_OBS, OBH2_SIG = 0.02236, 0.00015
CMB_CORR_INV = np.linalg.inv(
    np.array([[1.0, 0.46, -0.66], [0.46, 1.0, -0.33], [-0.66, -0.33, 1.0]]))

# ============================================================================
# CAMB DISTANCE COMPUTATION (with cache)
# ============================================================================
_camb_cache = {}

def get_camb_distances(H0, Om, w0=-1.0, wa=0.0):
    """Get BAO distances and CMB shift parameters from CAMB."""
    key = (round(H0, 2), round(Om, 5), round(w0, 5), round(wa, 5))
    if key in _camb_cache:
        return _camb_cache[key]

    omch2 = Om * (H0/100)**2 - OMBH2
    if omch2 < 0.001:
        return None

    try:
        pars = camb.CAMBparams()
        pars.set_cosmology(H0=H0, ombh2=OMBH2, omch2=omch2, mnu=MNU, omk=0, tau=0.054)
        if abs(w0 + 1) < 1e-5 and abs(wa) < 1e-5:
            pars.set_dark_energy(w=-1.0, wa=0.0)
        else:
            pars.set_dark_energy(w=w0, wa=wa, dark_energy_model='ppf')

        results = camb.get_background(pars)
        derived = results.get_derived_params()
        rd = derived['rdrag']

        d = {'rd': rd}
        zvals = [BGS_Z] + [tr['z'] for tr in TRACERS]
        for z in zvals:
            DM = results.comoving_radial_distance(z)
            Hz = results.hubble_parameter(z)
            DH = C_LIGHT / Hz
            d[z] = {'DM_rd': DM/rd, 'DH_rd': DH/rd,
                     'DV_rd': (z * (DM/rd)**2 * (DH/rd))**(1./3.)}

        DM_star = results.comoving_radial_distance(derived['zstar'])
        d['R'] = np.sqrt(Om) * H0 / C_LIGHT * DM_star
        d['lA'] = np.pi * DM_star / derived['rstar']

        _camb_cache[key] = d
        return d
    except Exception:
        return None


def chi2_bao_camb(H0, Om, w0=-1.0, wa=0.0):
    d = get_camb_distances(H0, Om, w0, wa)
    if d is None: return 1e8
    chi2 = (d[BGS_Z]['DV_rd'] - BGS_DV_RD)**2 * COV_INV_BGS
    for i, tr in enumerate(TRACERS):
        delta = np.array([d[tr['z']]['DM_rd'] - tr['DM_rd'],
                          d[tr['z']]['DH_rd'] - tr['DH_rd']])
        chi2 += float(delta @ COV_INV_BLOCKS[i] @ delta)
    return chi2


def chi2_cmb_camb(H0, Om, w0=-1.0, wa=0.0):
    d = get_camb_distances(H0, Om, w0, wa)
    if d is None: return 1e8
    delta = np.array([(d['R'] - R_OBS)/R_SIG, (d['lA'] - LA_OBS)/LA_SIG,
                       (OMBH2 - OBH2_OBS)/OBH2_SIG])
    return float(delta @ CMB_CORR_INV @ delta)


def chi2_growth(Om, w0=-1.0, wa=0.0, sigma8=0.811, gamma=0.55):
    GL_x, GL_w = np.polynomial.legendre.leggauss(64)
    def E2(z):
        zp1 = 1 + z
        ODE = 1 - Om - OMEGA_R
        if abs(wa) < 1e-8:
            return Om * zp1**3 + OMEGA_R * zp1**4 + ODE * zp1**(3*(1+w0))
        return Om * zp1**3 + OMEGA_R * zp1**4 + ODE * zp1**(3*(1+w0+wa)) * np.exp(-3*wa*z/zp1)

    chi2 = 0.0
    for z, fsig_obs, sig in FSIGMA8_DATA:
        Om_z = Om * (1+z)**3 / max(E2(z), 1e-30)
        f_z = Om_z**gamma
        nodes = 0.5 * z * (GL_x + 1.0)
        w = 0.5 * z * GL_w
        Om_arr = Om * (1 + nodes)**3 / np.array([max(E2(zi), 1e-30) for zi in nodes])
        D_ratio = np.exp(-np.sum(w * Om_arr**gamma / (1 + nodes)))
        chi2 += ((f_z * sigma8 * D_ratio - fsig_obs) / sig)**2
    return chi2


# ============================================================================
# ANALYTICAL DISTANCES (for Monte Carlo — validated against CAMB below)
# ============================================================================
_GL64_x, _GL64_w = np.polynomial.legendre.leggauss(64)

def E2_constw(z, Om, w0):
    zp1 = 1 + z
    return Om * zp1**3 + OMEGA_R * zp1**4 + (1 - Om - OMEGA_R) * zp1**(3*(1+w0))

def E2_CPL(z, Om, w0, wa):
    zp1 = 1 + z
    ODE = 1 - Om - OMEGA_R
    return Om * zp1**3 + OMEGA_R * zp1**4 + ODE * zp1**(3*(1+w0+wa)) * np.exp(-3*wa*z/zp1)

def comoving_int(z, E2_func, params):
    zp = 0.5 * z * (_GL64_x + 1.0)
    w = 0.5 * z * _GL64_w
    return float(np.sum(w / np.sqrt(np.maximum([E2_func(zi, *params) for zi in zp], 1e-30))))

def bao_obs(z, E2_func, params, hrd):
    integral = comoving_int(z, E2_func, params)
    DM_rd = integral / hrd
    DH_rd = 1.0 / (hrd * np.sqrt(max(E2_func(z, *params), 1e-30)))
    return DM_rd, DH_rd

def DV_rd_calc(z, E2_func, params, hrd):
    DM, DH = bao_obs(z, E2_func, params, hrd)
    return (z * DM**2 * DH)**(1./3.)

def chi2_bao_analytical(E2_func, params, hrd):
    chi2 = (DV_rd_calc(BGS_Z, E2_func, params, hrd) - BGS_DV_RD)**2 * COV_INV_BGS
    for i, tr in enumerate(TRACERS):
        DM, DH = bao_obs(tr['z'], E2_func, params, hrd)
        delta = np.array([DM - tr['DM_rd'], DH - tr['DH_rd']])
        chi2 += float(delta @ COV_INV_BLOCKS[i] @ delta)
    return chi2


# ============================================================================
# FITTING
# ============================================================================

def fit_camb(model, use_cmb=True, use_growth=True):
    """Fit using CAMB distances. Nelder-Mead from multiple starts."""
    N_DATA = 13 + (9 if use_growth else 0) + (3 if use_cmb else 0)

    def objective(theta):
        if model == 'LCDM':
            Om, H0, sigma8 = theta[0], theta[1], theta[2] if use_growth else 0.811
            w0, wa = -1.0, 0.0
        elif model == 'constw':
            w0, Om, H0 = theta[0], theta[1], theta[2]
            sigma8 = theta[3] if use_growth else 0.811
            wa = 0.0
        elif model == 'CPL':
            w0, wa, Om, H0 = theta[:4]
            sigma8 = theta[4] if use_growth else 0.811

        if Om < 0.15 or Om > 0.50 or H0 < 55 or H0 > 80: return 1e8
        if model != 'LCDM' and (w0 < -2 or w0 > 0.5): return 1e8
        if model == 'CPL' and (wa < -3 or wa > 2): return 1e8
        if use_growth and (sigma8 < 0.5 or sigma8 > 1.1): return 1e8

        c2 = chi2_bao_camb(H0, Om, w0, wa)
        if c2 > 1e7: return 1e8
        if use_cmb: c2 += chi2_cmb_camb(H0, Om, w0, wa)
        if use_growth:
            gamma = 0.55 if model != 'CPL' else 0.55 + 0.05*(1 + w0 + 0.5*wa)
            c2 += chi2_growth(Om, w0, wa, sigma8, gamma)
        return c2

    # Multiple Nelder-Mead starts
    if model == 'LCDM':
        starts = [[0.31, 67.4, 0.81], [0.30, 68.0, 0.80], [0.32, 66.5, 0.82]]
        npar = 3 if use_growth else 2
    elif model == 'constw':
        starts = [[-0.83, 0.31, 67.4, 0.81], [-0.90, 0.30, 68.0, 0.80],
                  [-0.75, 0.32, 66.5, 0.82], [-1.0, 0.31, 67.4, 0.81]]
        npar = 4 if use_growth else 3
    elif model == 'CPL':
        starts = [[-0.85, -0.5, 0.31, 67.4, 0.81], [-0.90, 0.0, 0.30, 68.0, 0.80],
                  [-0.75, -1.0, 0.32, 66.5, 0.82], [-1.0, -0.62, 0.31, 67.4, 0.81]]
        npar = 5 if use_growth else 4

    if not use_growth:
        starts = [s[:-1] for s in starts]

    best_fun = 1e8
    best_x = None
    for x0 in starts:
        res = minimize(objective, x0, method='Nelder-Mead',
                       options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 5000})
        if res.fun < best_fun:
            best_fun = res.fun
            best_x = res.x

    return best_x, best_fun, npar, N_DATA


# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':

    # ------------------------------------------------------------------
    # Step 0: Validate analytical vs CAMB distances
    # ------------------------------------------------------------------
    fprint("\n--- Validation: Analytical vs CAMB distances ---")

    d_camb = get_camb_distances(H0_FID, OM_FID, W0_MERIDIAN, 0.0)
    rd_camb = d_camb['rd']
    hrd = H0_FID * rd_camb / C_LIGHT

    for tr in TRACERS:
        z = tr['z']
        DM_camb = d_camb[z]['DM_rd']
        DH_camb = d_camb[z]['DH_rd']
        DM_anal, DH_anal = bao_obs(z, E2_constw, (OM_FID, W0_MERIDIAN), hrd)
        fprint(f"  z={z:.3f}: DM/rd CAMB={DM_camb:.4f} anal={DM_anal:.4f} "
               f"({abs(DM_camb-DM_anal)/DM_camb*100:.3f}%), "
               f"DH/rd CAMB={DH_camb:.4f} anal={DH_anal:.4f} "
               f"({abs(DH_camb-DH_anal)/DH_camb*100:.3f}%)")

    fprint(f"  rd = {rd_camb:.3f} Mpc, hrd = {hrd:.6f}")

    # ------------------------------------------------------------------
    # Analysis 1: Model comparison
    # ------------------------------------------------------------------
    fprint("\n" + "=" * 78)
    fprint("ANALYSIS 1: MODEL COMPARISON (CAMB Boltzmann)")
    fprint("Data: DESI DR2 BAO (Lee 2025) + CMB compressed + fsigma8")
    fprint("=" * 78)

    fprint("\nFitting LCDM...")
    lcdm_par, lcdm_chi2, lcdm_npar, ndata = fit_camb('LCDM')
    fprint(f"  LCDM: chi2 = {lcdm_chi2:.3f}, npar = {lcdm_npar}, "
           f"chi2/dof = {lcdm_chi2/(ndata-lcdm_npar):.3f}")
    fprint(f"  Om = {lcdm_par[0]:.4f}, H0 = {lcdm_par[1]:.2f}, sig8 = {lcdm_par[2]:.4f}")

    fprint("\nFitting constant-w...")
    cw_par, cw_chi2, cw_npar, _ = fit_camb('constw')
    fprint(f"  const-w: chi2 = {cw_chi2:.3f}, npar = {cw_npar}, "
           f"chi2/dof = {cw_chi2/(ndata-cw_npar):.3f}")
    fprint(f"  w0 = {cw_par[0]:.4f}, Om = {cw_par[1]:.4f}, H0 = {cw_par[2]:.2f}, sig8 = {cw_par[3]:.4f}")

    fprint("\nFitting CPL...")
    cpl_par, cpl_chi2, cpl_npar, _ = fit_camb('CPL')
    fprint(f"  CPL: chi2 = {cpl_chi2:.3f}, npar = {cpl_npar}, "
           f"chi2/dof = {cpl_chi2/(ndata-cpl_npar):.3f}")
    fprint(f"  w0 = {cpl_par[0]:.4f}, wa = {cpl_par[1]:.4f}, Om = {cpl_par[2]:.4f}, "
           f"H0 = {cpl_par[3]:.2f}, sig8 = {cpl_par[4]:.4f}")

    # Meridian: profile over (Om, H0, sigma8) at fixed w0=-0.830, wa=0
    fprint("\nMeridian (w0=-0.830, wa=0): profiling over Om, H0, sigma8...")
    def obj_meridian(theta):
        Om, H0, s8 = theta
        if Om < 0.15 or Om > 0.50 or H0 < 55 or H0 > 80 or s8 < 0.5 or s8 > 1.1: return 1e8
        c2 = chi2_bao_camb(H0, Om, W0_MERIDIAN, 0.0)
        if c2 > 1e7: return 1e8
        c2 += chi2_cmb_camb(H0, Om, W0_MERIDIAN, 0.0)
        c2 += chi2_growth(Om, W0_MERIDIAN, 0.0, s8, 0.55)
        return c2

    best_mer = 1e8
    best_mer_p = None
    for x0 in [[0.31, 67.4, 0.81], [0.28, 70.0, 0.80], [0.34, 65.0, 0.82], [0.30, 69.0, 0.81]]:
        r = minimize(obj_meridian, x0, method='Nelder-Mead',
                     options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 5000})
        if r.fun < best_mer:
            best_mer = r.fun
            best_mer_p = r.x
    chi2_mer_tot = best_mer
    fprint(f"  chi2 = {chi2_mer_tot:.3f}, Om = {best_mer_p[0]:.4f}, "
           f"H0 = {best_mer_p[1]:.2f}, sig8 = {best_mer_p[2]:.4f}")
    D_mer_lcdm = lcdm_chi2 - chi2_mer_tot
    sig_mer = np.sqrt(abs(D_mer_lcdm)) * np.sign(D_mer_lcdm)
    fprint(f"  Delta chi2 vs LCDM: {D_mer_lcdm:+.3f} ({abs(sig_mer):.2f} sigma)")
    D_mer_cw = cw_chi2 - chi2_mer_tot
    fprint(f"  Delta chi2 vs best-fit const-w: {D_mer_cw:+.3f}")

    D_cw_lcdm = lcdm_chi2 - cw_chi2
    D_cpl_cw = cw_chi2 - cpl_chi2
    sig_cw = np.sqrt(abs(D_cw_lcdm)) * np.sign(D_cw_lcdm)
    sig_wa = np.sqrt(abs(D_cpl_cw)) * np.sign(D_cpl_cw)

    fprint(f"\n  Delta chi2:")
    fprint(f"  const-w vs LCDM: {D_cw_lcdm:+.3f} ({abs(sig_cw):.2f} sigma)")
    fprint(f"  CPL vs const-w:  {D_cpl_cw:+.3f} ({abs(sig_wa):.2f} sigma preference for wa!=0)")

    # ------------------------------------------------------------------
    # Analysis 2: Profile likelihood for w_a
    # ------------------------------------------------------------------
    fprint("\n" + "=" * 78)
    fprint("ANALYSIS 2: PROFILE LIKELIHOOD FOR w_a (CAMB)")
    fprint("=" * 78)

    wa_vals = np.array([-2.0, -1.5, -1.2, -1.0, -0.8, -0.62, -0.5, -0.4, -0.3,
                         -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0])
    chi2_prof = []

    fprint(f"\n{'w_a':>8} {'chi2':>10} {'w0_bf':>8} {'Om_bf':>8}")
    fprint("-" * 40)

    for wa_val in wa_vals:
        def obj_profile(theta):
            w0, Om, H0, s8 = theta
            if w0 < -2 or w0 > 0.5 or Om < 0.15 or Om > 0.50: return 1e8
            if H0 < 55 or H0 > 80 or s8 < 0.5 or s8 > 1.1: return 1e8
            c2 = chi2_bao_camb(H0, Om, w0, wa_val)
            if c2 > 1e7: return 1e8
            c2 += chi2_cmb_camb(H0, Om, w0, wa_val)
            c2 += chi2_growth(Om, w0, wa_val, s8, 0.55 + 0.05*(1 + w0 + 0.5*wa_val))
            return c2

        best_f = 1e8
        best_p = None
        for x0 in [[-0.85, 0.31, 67.4, 0.81], [-0.95, 0.30, 68.0, 0.80], [-0.75, 0.32, 66.5, 0.82]]:
            r = minimize(obj_profile, x0, method='Nelder-Mead',
                         options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 5000})
            if r.fun < best_f:
                best_f = r.fun
                best_p = r.x
        chi2_prof.append(best_f)
        if best_p is not None:
            fprint(f"{wa_val:8.2f} {best_f:10.3f} {best_p[0]:8.4f} {best_p[1]:8.4f}")
        else:
            fprint(f"{wa_val:8.2f} {best_f:10.3f}  (no convergence)")

    chi2_prof = np.array(chi2_prof)
    chi2_min = chi2_prof.min()
    wa_best = wa_vals[np.argmin(chi2_prof)]
    idx0 = np.argmin(np.abs(wa_vals))
    dchi2_wa0 = chi2_prof[idx0] - chi2_min
    sig_wa0 = np.sqrt(max(dchi2_wa0, 0))

    fprint(f"\n  Profile minimum: w_a = {wa_best:.2f}, chi2 = {chi2_min:.3f}")
    fprint(f"  At w_a = 0 (Meridian): Delta chi2 = {dchi2_wa0:.3f} ({sig_wa0:.2f} sigma)")

    # ------------------------------------------------------------------
    # Analysis 3: Monte Carlo template artifact (analytical, CAMB-validated)
    # ------------------------------------------------------------------
    fprint("\n" + "=" * 78)
    fprint("ANALYSIS 3: TEMPLATE ARTIFACT TEST (MC, analytical distances)")
    fprint("Truth: constant-w (Meridian) -> fit CPL -> recover w_a")
    fprint("=" * 78)

    N_MC = 500
    rng = np.random.default_rng(42)
    wa_recovered = []

    # Truth: best-fit const-w
    w0_t, Om_t = cw_par[0], cw_par[1]
    hrd_t = cw_par[2] * rd_camb / C_LIGHT  # Use CAMB rd for truth

    fprint(f"\nTruth: w0={w0_t:.4f}, Om={Om_t:.4f}, hrd={hrd_t:.6f}")
    fprint(f"Running {N_MC} Monte Carlo realizations...")

    for i in range(N_MC):
        # Generate mock from const-w truth
        mock_BGS = DV_rd_calc(BGS_Z, E2_constw, (Om_t, w0_t), hrd_t) + \
                   rng.normal() * np.sqrt(BGS_DV_RD_VAR)
        mock_tr = []
        for j, tr in enumerate(TRACERS):
            DM_t, DH_t = bao_obs(tr['z'], E2_constw, (Om_t, w0_t), hrd_t)
            noise = rng.multivariate_normal([0, 0], COV_BLOCKS[j])
            mock_tr.append((DM_t + noise[0], DH_t + noise[1]))

        # Fit CPL to mock
        def obj_mock(theta):
            w0, wa, Om, hrd = theta
            if w0 < -2 or w0 > 0.5 or wa < -3 or wa > 2: return 1e8
            if Om < 0.15 or Om > 0.50 or hrd < 0.025 or hrd > 0.045: return 1e8
            c2 = (DV_rd_calc(BGS_Z, E2_CPL, (Om, w0, wa), hrd) - mock_BGS)**2 * COV_INV_BGS
            for j, tr in enumerate(TRACERS):
                DM, DH = bao_obs(tr['z'], E2_CPL, (Om, w0, wa), hrd)
                delta = np.array([DM - mock_tr[j][0], DH - mock_tr[j][1]])
                c2 += float(delta @ COV_INV_BLOCKS[j] @ delta)
            return c2

        best_f = 1e8
        best_wa = 0.0
        for x0 in [[-0.85, -0.3, Om_t, hrd_t], [-0.90, 0.0, Om_t, hrd_t],
                    [-0.75, -0.8, Om_t, hrd_t]]:
            r = minimize(obj_mock, x0, method='Nelder-Mead',
                         options={'xatol': 1e-5, 'fatol': 1e-5, 'maxiter': 3000})
            if r.fun < best_f:
                best_f = r.fun
                best_wa = r.x[1]
        wa_recovered.append(best_wa)

        if (i+1) % 100 == 0:
            fprint(f"  {i+1}/{N_MC}: mean w_a = {np.mean(wa_recovered):.3f} +/- {np.std(wa_recovered):.3f}")

    wa_recovered = np.array(wa_recovered)
    fprint(f"\n  Results ({len(wa_recovered)} realizations):")
    fprint(f"    w_a mean   = {np.mean(wa_recovered):.4f}")
    fprint(f"    w_a median = {np.median(wa_recovered):.4f}")
    fprint(f"    w_a std    = {np.std(wa_recovered):.4f}")
    fprint(f"    P(w_a < -0.5):  {np.mean(wa_recovered < -0.5):.3f}")
    fprint(f"    P(w_a < -0.62): {np.mean(wa_recovered < -0.62):.3f}")
    fprint(f"    Lu & Simon: w_a = -0.62 +/- 0.26")

    # ------------------------------------------------------------------
    # Analysis 4: Decoupled perturbation test
    # ------------------------------------------------------------------
    fprint("\n" + "=" * 78)
    fprint("ANALYSIS 4: DECOUPLED PERTURBATION TEST")
    fprint("Fit A: const-w + GR growth (gamma=0.55)")
    fprint("Fit B: CPL + coupled growth (gamma=0.55+0.05*(1+w_eff))")
    fprint("=" * 78)

    # Already computed: cw = Fit A, cpl = Fit B
    D_AB = cw_chi2 - cpl_chi2
    sig_AB = np.sqrt(abs(D_AB)) * np.sign(D_AB)
    fprint(f"\n  Fit A (const-w + GR): chi2 = {cw_chi2:.3f}")
    fprint(f"  Fit B (CPL + coupled): chi2 = {cpl_chi2:.3f}")
    fprint(f"  Delta chi2 = {D_AB:.3f} ({abs(sig_AB):.2f} sigma)")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    fprint("\n" + "=" * 78)
    fprint("SUMMARY FOR MONOGRAPH")
    fprint("=" * 78)
    fprint(f"""
  ===================================================================
  w_a TENSION RESOLUTION (CAMB Boltzmann, April 2026)
  Meridian: w_0 = -0.830, w_a = 0 (exact), zeta_0 = 8.82e-4
  Data: DESI DR2 + Planck CMB + fsigma8 ({ndata} points)
  ===================================================================

  Model       chi2     npar  chi2/dof  D(chi2)  sigma
  LCDM     {lcdm_chi2:8.3f}  {lcdm_npar:4d}   {lcdm_chi2/(ndata-lcdm_npar):7.3f}     ---     ---
  const-w  {cw_chi2:8.3f}  {cw_npar:4d}   {cw_chi2/(ndata-cw_npar):7.3f}  {D_cw_lcdm:+7.3f}   {abs(sig_cw):.2f}
  CPL      {cpl_chi2:8.3f}  {cpl_npar:4d}   {cpl_chi2/(ndata-cpl_npar):7.3f}  {D_cpl_cw:+7.3f}   {abs(sig_wa):.2f}
  Meridian {chi2_mer_tot:8.3f}  {3:4d}   {chi2_mer_tot/(ndata-3):7.3f}  {D_mer_lcdm:+7.3f}   {abs(sig_mer):.2f}

  Profile likelihood: w_a = 0 at {sig_wa0:.2f} sigma from minimum
  Template artifact: w_a bias = {np.mean(wa_recovered):.3f} +/- {np.std(wa_recovered):.3f}
  Decoupled test: Delta chi2 = {D_AB:.3f} ({abs(sig_AB):.2f} sigma)

  CONCLUSION:
    w_a = 0 (Meridian) is at {sig_wa0:.1f} sigma from the profile minimum.
    CPL fits {'show' if abs(sig_wa) > 2 else 'do not show'} significant preference for w_a != 0.
    Template artifact test: constant-w truth produces w_a bias of
    {np.mean(wa_recovered):.2f} when fit with CPL.
  ===================================================================
""")

    fprint("Done.")
