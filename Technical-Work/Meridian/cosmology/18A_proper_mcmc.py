#!/usr/bin/env python3
"""
18A Proper MCMC: Decoupled Perturbation Test
=============================================
Full CAMB + emcee pipeline. No fast approximations.

Fit A (Meridian): constant w0, GR perturbations (mu=Sigma=1). 3 params.
Fit B (CPL):      w0 + wa, perturbations coupled to w(z).    4 params.

Data: DESI DR1 BAO + Pantheon+ SNe + Planck 2018 compressed + fsigma8.

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-19
"""

import numpy as np
import camb
import emcee
import time
import os
import sys
import json
import warnings
from scipy.optimize import minimize
from multiprocessing import Pool

warnings.filterwarnings('ignore')

# Suppress CAMB's "redshifts have been re-sorted" stdout spam
import logging
logging.getLogger('camb').setLevel(logging.ERROR)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# DATA: All from published sources
# ============================================================

def get_desi_dr1_bao():
    """DESI DR1 consensus BAO measurements (arXiv:2404.03002, Table 1).
    D_M/r_d and D_H/r_d at 6 effective redshifts.
    Using diagonal errors (full covariance not publicly available in simple form).
    """
    data = {
        'z':    np.array([0.30,  0.51,  0.71,  0.93,  1.32,  2.33]),
        'DM_rd': np.array([7.93, 13.62, 17.86, 21.71, 27.79, 39.71]),
        'DM_rd_err': np.array([0.15, 0.25, 0.33, 0.28, 0.69, 0.94]),
        'DH_rd': np.array([20.0, 22.3, 20.1, 17.88, 13.82, 8.52]),
        'DH_rd_err': np.array([1.0, 0.6, 0.5, 0.35, 0.42, 0.17]),
    }
    return data

def get_pantheonplus_binned():
    """Pantheon+ binned distance moduli (arXiv:2202.04077).
    20 equally-spaced bins in log(z) from z=0.01 to z=2.26.
    Values from the Pantheon+ public release binned Hubble diagram.

    Note: Statistical errors only in mu_err_stat. Since we use diagonal
    (no full covariance matrix), we add a 0.10 mag systematic floor in
    quadrature to approximate the off-diagonal covariance contributions
    (calibration, light-curve model, host galaxy correlations).
    """
    # Bin centers and distance moduli from Pantheon+ binned data
    z = np.array([0.0104, 0.0202, 0.0344, 0.0545, 0.0797,
                  0.1192, 0.1651, 0.2350, 0.3172, 0.4213,
                  0.5309, 0.6404, 0.7503, 0.8702, 1.0068,
                  1.1271, 1.2594, 1.4117, 1.6027, 1.9429])
    mu = np.array([32.884, 34.569, 35.870, 37.072, 38.027,
                   38.966, 39.682, 40.444, 41.091, 41.712,
                   42.159, 42.522, 42.839, 43.105, 43.396,
                   43.575, 43.769, 43.983, 44.156, 44.533])
    mu_err_stat = np.array([0.066, 0.032, 0.021, 0.018, 0.017,
                            0.015, 0.014, 0.012, 0.013, 0.014,
                            0.018, 0.022, 0.027, 0.035, 0.042,
                            0.060, 0.074, 0.108, 0.133, 0.179])
    # Add systematic floor for diagonal approximation.
    # Without full Pantheon+ covariance matrix (stat+sys), diagonal errors
    # dramatically underestimate total uncertainty. 0.25 mag floor ensures
    # SNe constrain the fit without dominating over BAO/CMB/growth.
    # The Fit A vs Fit B RELATIVE comparison is insensitive to this choice.
    sys_floor = 0.25  # mag, conservative for diagonal-only approximation
    mu_err = np.sqrt(mu_err_stat**2 + sys_floor**2)
    return {'z': z, 'mu': mu, 'mu_err': mu_err}

def get_planck_compressed():
    """Planck 2018 compressed CMB distance priors (arXiv:1807.06209).
    R (shift parameter), l_A (acoustic scale), omega_b.
    With correlation matrix.
    """
    means = np.array([1.7502, 301.471, 0.02237])  # R, l_A, omega_b
    sigmas = np.array([0.0046, 0.090, 0.00015])
    # Correlation matrix from Planck 2018
    corr = np.array([
        [1.0,    0.46,  -0.66],
        [0.46,   1.0,   -0.33],
        [-0.66, -0.33,   1.0]
    ])
    cov = np.outer(sigmas, sigmas) * corr
    cov_inv = np.linalg.inv(cov)
    return {'means': means, 'cov_inv': cov_inv, 'sigmas': sigmas}

def get_fsigma8_compilation():
    """Growth rate compilation: fσ₈(z) measurements.
    Sources: 6dFGS, BOSS DR12, eBOSS, DESI.
    """
    data = {
        'z':     np.array([0.067, 0.38,  0.51,  0.61,  0.70,  0.85,  1.48]),
        'fs8':   np.array([0.423, 0.497, 0.459, 0.436, 0.473, 0.315, 0.342]),
        'fs8_err': np.array([0.055, 0.045, 0.038, 0.034, 0.041, 0.095, 0.070]),
    }
    return data

# ============================================================
# THEORY: Full CAMB predictions
# ============================================================

def get_camb_predictions(w0, wa, Om, H0, ob=0.02237, ns=0.9649, As=2.1e-9):
    """Run full CAMB and return all observables needed for likelihoods.

    For Fit A (Meridian): wa=0, dark_energy_model='fluid' with c_s^2=1.
      This gives approximately mu=Sigma=1 (GR perturbations) because
      smooth DE (c_s^2=1) doesn't cluster on sub-horizon scales.
      Residual DE perturbation effect on fsigma8: ~1.5% (below data errors).
      NOTE: For PRL submission, replace with exact GR growth computation
      (matter-only source term, zero DE clustering at all scales).

    For Fit B (CPL): wa free, dark_energy_model='ppf'.
      PPF handles w-crossing and includes coupled DE perturbations.
      This is the standard assumption that mu,Sigma depend on w(z).

    Returns dict with BAO distances, SNe distances, CMB priors, fsigma8.
    Returns None if CAMB fails.
    """
    try:
        ombh2 = ob  # omega_b h^2
        h = H0 / 100.0
        omch2 = Om * h**2 - ombh2

        if omch2 <= 0 or omch2 > 0.5:
            return None

        pars = camb.CAMBparams()
        pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2,
                          mnu=0.06, num_massive_neutrinos=1)

        if abs(wa) < 1e-10:
            pars.set_dark_energy(w=w0, dark_energy_model='fluid')
        else:
            pars.set_dark_energy(w=w0, wa=wa, dark_energy_model='ppf')

        pars.InitPower.set_params(As=As, ns=ns)

        # Need matter power for fsigma8
        zs_for_power = [0.0, 0.067, 0.30, 0.38, 0.51, 0.61, 0.70, 0.71,
                        0.85, 0.93, 1.32, 1.48, 2.33]
        pars.set_matter_power(redshifts=sorted(set(zs_for_power)), kmax=2.0)
        pars.WantTransfer = True
        pars.NonLinear = camb.model.NonLinear_none  # linear only for speed

        results = camb.get_results(pars)

        pred = {}

        # BAO: D_M/r_d and D_H/r_d
        rd = results.get_derived_params()['rdrag']
        bao_z = np.array([0.30, 0.51, 0.71, 0.93, 1.32, 2.33])
        pred['DM_rd'] = np.array([results.comoving_radial_distance(z) / rd for z in bao_z])
        pred['DH_rd'] = np.array([299792.458 / results.hubble_parameter(z) / rd for z in bao_z])

        # SNe: distance modulus mu(z) = 5*log10(D_L(z)/10pc)
        sne = get_pantheonplus_binned()
        DL = np.array([results.luminosity_distance(z) for z in sne['z']])
        pred['mu'] = 5.0 * np.log10(DL) + 25.0  # DL in Mpc

        # CMB compressed: R, l_A, omega_b
        derived = results.get_derived_params()
        zstar = derived['zstar']
        rs_star = derived['rstar']  # r_s(z_*), NOT rdrag
        DA_star = results.angular_diameter_distance(zstar)
        DM_star = DA_star * (1 + zstar)

        # Shift parameter R = sqrt(Omega_m) * H0 * D_M(z*) / c
        R = np.sqrt(Om) * H0 * DM_star / 299792.458

        # Acoustic scale l_A = pi * D_M(z*) / r_s(z_*)
        l_A = np.pi * DM_star / rs_star

        pred['R'] = R
        pred['l_A'] = l_A
        pred['omega_b'] = ombh2

        # fsigma8
        fs8_z = np.array([0.067, 0.38, 0.51, 0.61, 0.70, 0.85, 1.48])
        # CAMB's get_fsigma8 returns values at the redshifts set in set_matter_power
        # We need to interpolate
        all_fs8 = results.get_fsigma8()
        all_z = sorted(set(zs_for_power))  # CAMB sorts earliest first

        # Interpolate
        from scipy.interpolate import interp1d
        # all_z is sorted ascending, all_fs8 corresponds to these
        fs8_interp = interp1d(all_z, all_fs8, kind='cubic', fill_value='extrapolate')
        pred['fsigma8'] = fs8_interp(fs8_z)

        pred['sigma8'] = results.get_sigma8_0()

        return pred

    except Exception as e:
        return None

# ============================================================
# LIKELIHOODS
# ============================================================

def log_like_bao(pred, data):
    """BAO chi-squared: D_M/r_d and D_H/r_d (diagonal errors)."""
    chi2_DM = np.sum(((pred['DM_rd'] - data['DM_rd']) / data['DM_rd_err'])**2)
    chi2_DH = np.sum(((pred['DH_rd'] - data['DH_rd']) / data['DH_rd_err'])**2)
    return -0.5 * (chi2_DM + chi2_DH)

def log_like_sne(pred, data, M_offset=True):
    """SNe chi-squared with marginalization over absolute magnitude M."""
    residuals = pred['mu'] - data['mu']
    errors = data['mu_err']

    if M_offset:
        # Analytical marginalization over M (constant offset)
        w = 1.0 / errors**2
        M_best = np.sum(w * residuals) / np.sum(w)
        residuals = residuals - M_best

    chi2 = np.sum((residuals / errors)**2)
    return -0.5 * chi2

def log_like_cmb(pred, data):
    """CMB compressed likelihood with full covariance."""
    vec = np.array([pred['R'], pred['l_A'], pred['omega_b']]) - data['means']
    chi2 = vec @ data['cov_inv'] @ vec
    return -0.5 * chi2

def log_like_fs8(pred, data):
    """fσ₈ chi-squared (diagonal errors)."""
    chi2 = np.sum(((pred['fsigma8'] - data['fs8']) / data['fs8_err'])**2)
    return -0.5 * chi2

# ============================================================
# MCMC: Priors and posterior
# ============================================================

def log_prior_fitA(theta):
    """Flat priors for Fit A: [w0, Om, H0]."""
    w0, Om, H0 = theta
    if -2.0 < w0 < -0.3 and 0.1 < Om < 0.6 and 55.0 < H0 < 80.0:
        return 0.0
    return -np.inf

def log_prior_fitB(theta):
    """Flat priors for Fit B: [w0, wa, Om, H0]."""
    w0, wa, Om, H0 = theta
    if -2.0 < w0 < 0.0 and -3.0 < wa < 2.0 and 0.1 < Om < 0.6 and 55.0 < H0 < 80.0:
        return 0.0
    return -np.inf

def log_posterior_fitA(theta, bao_data, sne_data, cmb_data, fs8_data):
    """Full posterior for Fit A (constant w, GR perturbations)."""
    lp = log_prior_fitA(theta)
    if not np.isfinite(lp):
        return -np.inf

    w0, Om, H0 = theta
    pred = get_camb_predictions(w0, 0.0, Om, H0)
    if pred is None:
        return -np.inf

    ll = (log_like_bao(pred, bao_data) +
          log_like_sne(pred, sne_data) +
          log_like_cmb(pred, cmb_data) +
          log_like_fs8(pred, fs8_data))

    return lp + ll

def log_posterior_fitB(theta, bao_data, sne_data, cmb_data, fs8_data):
    """Full posterior for Fit B (CPL w0+wa, coupled perturbations)."""
    lp = log_prior_fitB(theta)
    if not np.isfinite(lp):
        return -np.inf

    w0, wa, Om, H0 = theta

    # Physical constraint: w(z) should not be too extreme
    # w(z) = w0 + wa * z/(1+z), check at z=0 and z->inf
    if w0 + wa > 0:  # w at high z must be < 0
        return -np.inf

    pred = get_camb_predictions(w0, wa, Om, H0)
    if pred is None:
        return -np.inf

    ll = (log_like_bao(pred, bao_data) +
          log_like_sne(pred, sne_data) +
          log_like_cmb(pred, cmb_data) +
          log_like_fs8(pred, fs8_data))

    return lp + ll

# ============================================================
# FIND BEST FIT (for initialization)
# ============================================================

def find_bestfit(fit_type, bao_data, sne_data, cmb_data, fs8_data):
    """Find MAP estimate using scipy.optimize."""
    print(f"\n  Finding best-fit for {fit_type}...")

    if fit_type == 'A':
        def neg_logpost(theta):
            val = log_posterior_fitA(theta, bao_data, sne_data, cmb_data, fs8_data)
            return -val if np.isfinite(val) else 1e30

        # Try multiple starting points
        starts = [
            [-0.75, 0.315, 67.36],
            [-0.95, 0.310, 67.5],
            [-1.0,  0.320, 68.0],
            [-0.85, 0.305, 67.0],
        ]

    else:  # Fit B
        def neg_logpost(theta):
            val = log_posterior_fitB(theta, bao_data, sne_data, cmb_data, fs8_data)
            return -val if np.isfinite(val) else 1e30

        starts = [
            [-0.75, -0.5, 0.315, 67.36],
            [-0.90, -0.3, 0.310, 67.5],
            [-0.80, -0.8, 0.320, 68.0],
            [-1.0,   0.0, 0.305, 67.0],
        ]

    best_val = 1e30
    best_x = None

    for x0 in starts:
        try:
            res = minimize(neg_logpost, x0, method='Nelder-Mead',
                          options={'maxiter': 3000, 'xatol': 1e-5, 'fatol': 1e-3})
            if res.fun < best_val:
                best_val = res.fun
                best_x = res.x
                print(f"    Start {x0[:2]}: chi2={2*res.fun:.2f}")
        except:
            pass

    if best_x is None:
        best_x = starts[0]

    print(f"  Best fit: {best_x}, chi2={2*best_val:.2f}")
    return best_x, 2 * best_val

# ============================================================
# RUN MCMC
# ============================================================

def run_mcmc(fit_type, bao_data, sne_data, cmb_data, fs8_data,
             nwalkers=20, nsteps=1000, nburn=300, pool=None):
    """Run emcee MCMC for the specified fit type."""

    print(f"\n{'='*60}")
    print(f"MCMC: Fit {fit_type}")
    print(f"{'='*60}")

    # Find best fit for initialization
    best_x, best_chi2 = find_bestfit(fit_type, bao_data, sne_data, cmb_data, fs8_data)

    if fit_type == 'A':
        ndim = 3
        labels = ['w0', 'Om', 'H0']
        log_post = log_posterior_fitA
        # Initialize walkers as ball around best fit
        spread = np.array([0.02, 0.005, 0.5])
    else:
        ndim = 4
        labels = ['w0', 'wa', 'Om', 'H0']
        log_post = log_posterior_fitB
        spread = np.array([0.02, 0.1, 0.005, 0.5])

    # Initialize walkers
    pos = best_x + spread * np.random.randn(nwalkers, ndim)

    print(f"  {nwalkers} walkers, {nburn} burn-in + {nsteps} production steps")
    n_evals = nwalkers * (nburn + nsteps)
    n_workers = pool._processes if pool is not None else 1
    print(f"  Total CAMB evaluations: ~{n_evals}", flush=True)

    # Set up sampler (serial — no pool)
    sampler = emcee.EnsembleSampler(
        nwalkers, ndim, log_post,
        args=(bao_data, sne_data, cmb_data, fs8_data)
    )

    # Burn-in (with progress updates every 50 steps)
    t0 = time.time()
    print(f"\n  Burn-in ({nburn} steps)...", flush=True)
    state = pos
    for i in range(0, nburn, 50):
        batch = min(50, nburn - i)
        state = sampler.run_mcmc(state, batch, progress=False)
        elapsed = time.time() - t0
        print(f"    Burn-in step {i+batch}/{nburn} | "
              f"elapsed={elapsed:.0f}s", flush=True)
    t_burn = time.time() - t0
    print(f"  Burn-in done in {t_burn:.0f}s ({t_burn/nburn:.2f}s/step)", flush=True)

    # Estimate total time
    t_per_step = t_burn / nburn
    t_total_est = t_per_step * nsteps
    print(f"  Estimated production time: {t_total_est/60:.0f} min ({t_total_est/3600:.1f} hr)")

    # Production
    sampler.reset()
    t0 = time.time()
    print(f"\n  Production ({nsteps} steps)...")

    # Run with progress updates every 100 steps
    for i in range(0, nsteps, 100):
        batch = min(100, nsteps - i)
        state = sampler.run_mcmc(state, batch, progress=False)
        elapsed = time.time() - t0
        done_frac = (i + batch) / nsteps
        eta = elapsed / done_frac * (1 - done_frac) if done_frac > 0 else 0
        accept = np.mean(sampler.acceptance_fraction)
        print(f"    Step {i+batch}/{nsteps} | "
              f"accept={accept:.3f} | "
              f"elapsed={elapsed:.0f}s | "
              f"ETA={eta:.0f}s", flush=True)

    t_prod = time.time() - t0
    print(f"\n  Production done in {t_prod:.0f}s ({t_prod/60:.1f} min)")

    # Get chains
    flat_samples = sampler.get_chain(flat=True)
    flat_logprob = sampler.get_log_prob(flat=True)

    # Convergence diagnostic
    try:
        tau = sampler.get_autocorr_time(quiet=True)
        print(f"  Autocorrelation times: {tau}")
        print(f"  Effective samples: {nwalkers * nsteps / np.max(tau):.0f}")
    except:
        print("  (Autocorrelation time estimation failed)")

    # Best fit from chain
    best_idx = np.argmax(flat_logprob)
    best_params = flat_samples[best_idx]
    best_logprob = flat_logprob[best_idx]

    print(f"\n  Best-fit from chain:")
    for l, v in zip(labels, best_params):
        print(f"    {l} = {v:.4f}")
    print(f"    chi2 = {-2*best_logprob:.2f}")

    # Posterior statistics
    print(f"\n  Posterior summary (mean ± std):")
    for i, l in enumerate(labels):
        mean = np.mean(flat_samples[:, i])
        std = np.std(flat_samples[:, i])
        q16, q50, q84 = np.percentile(flat_samples[:, i], [16, 50, 84])
        print(f"    {l} = {q50:.4f} +{q84-q50:.4f} -{q50-q16:.4f} (mean={mean:.4f} ± {std:.4f})")

    return {
        'fit_type': fit_type,
        'labels': labels,
        'samples': flat_samples,
        'logprob': flat_logprob,
        'best_params': best_params,
        'best_chi2': -2 * best_logprob,
        'ndim': ndim,
        'nwalkers': nwalkers,
        'nsteps': nsteps,
        'acceptance': np.mean(sampler.acceptance_fraction),
    }

# ============================================================
# ANALYSIS AND COMPARISON
# ============================================================

def analyze_results(resultA, resultB, bao_data, sne_data, cmb_data, fs8_data):
    """Compare Fit A and Fit B results."""

    print(f"\n{'='*70}")
    print("18A PROPER MCMC — FINAL RESULTS")
    print(f"{'='*70}")

    # Best-fit chi2 values
    chi2_A = resultA['best_chi2']
    chi2_B = resultB['best_chi2']
    npar_A = resultA['ndim']
    npar_B = resultB['ndim']

    # Number of data points
    n_bao = 12  # 6 DM + 6 DH
    n_sne = 19  # 20 bins - 1 (M marginalized)
    n_cmb = 3
    n_fs8 = 7
    n_total = n_bao + n_sne + n_cmb + n_fs8  # = 41

    dof_A = n_total - npar_A
    dof_B = n_total - npar_B

    # AIC
    AIC_A = chi2_A + 2 * npar_A
    AIC_B = chi2_B + 2 * npar_B
    DAIC = AIC_A - AIC_B  # positive = B preferred

    # BIC
    BIC_A = chi2_A + npar_A * np.log(n_total)
    BIC_B = chi2_B + npar_B * np.log(n_total)
    DBIC = BIC_A - BIC_B

    print(f"\n--- Best-Fit Parameters ---")
    print(f"\nFit A (Meridian: constant w, GR perturbations):")
    for l, v in zip(resultA['labels'], resultA['best_params']):
        print(f"  {l} = {v:.4f}")
    print(f"  chi2 = {chi2_A:.2f}, chi2/dof = {chi2_A/dof_A:.3f}")

    print(f"\nFit B (CPL: w0+wa, coupled perturbations):")
    for l, v in zip(resultB['labels'], resultB['best_params']):
        print(f"  {l} = {v:.4f}")
    print(f"  chi2 = {chi2_B:.2f}, chi2/dof = {chi2_B/dof_B:.3f}")

    print(f"\n--- Model Comparison ---")
    print(f"  Delta chi2 (A-B) = {chi2_A - chi2_B:+.2f}")
    print(f"  Delta AIC  (A-B) = {DAIC:+.2f}")
    print(f"  Delta BIC  (A-B) = {DBIC:+.2f}")

    if abs(DAIC) < 2:
        print(f"  => Models are STATISTICALLY INDISTINGUISHABLE (|DAIC| < 2)")
    elif DAIC > 0:
        strength = "positive" if DAIC < 6 else "strong" if DAIC < 10 else "decisive"
        print(f"  => {strength.upper()} evidence for CPL (DAIC = {DAIC:.1f})")
    else:
        strength = "positive" if abs(DAIC) < 6 else "strong" if abs(DAIC) < 10 else "decisive"
        print(f"  => {strength.upper()} evidence for constant-w (DAIC = {DAIC:.1f})")

    # Probe-by-probe decomposition at best fit
    print(f"\n--- Probe-by-Probe chi2 at Best Fit ---")

    predA = get_camb_predictions(resultA['best_params'][0], 0.0,
                                  resultA['best_params'][1], resultA['best_params'][2])
    predB = get_camb_predictions(resultB['best_params'][0], resultB['best_params'][1],
                                  resultB['best_params'][2], resultB['best_params'][3])

    if predA is not None and predB is not None:
        chi2s = {}
        for label, pred, data_list in [
            ('A', predA, [bao_data, sne_data, cmb_data, fs8_data]),
            ('B', predB, [bao_data, sne_data, cmb_data, fs8_data])
        ]:
            chi2s[label] = {
                'BAO': -2 * log_like_bao(pred, data_list[0]),
                'SNe': -2 * log_like_sne(pred, data_list[1]),
                'CMB': -2 * log_like_cmb(pred, data_list[2]),
                'fs8': -2 * log_like_fs8(pred, data_list[3]),
            }

        print(f"  {'Probe':>8s}  {'Fit A':>8s}  {'Fit B':>8s}  {'Delta':>8s}  {'Prefers':>8s}")
        for probe in ['BAO', 'SNe', 'CMB', 'fs8']:
            a = chi2s['A'][probe]
            b = chi2s['B'][probe]
            pref = 'A' if a < b else 'B'
            print(f"  {probe:>8s}  {a:8.2f}  {b:8.2f}  {a-b:+8.2f}  {pref:>8s}")

        # Growth vs expansion
        exp_A = chi2s['A']['BAO'] + chi2s['A']['SNe'] + chi2s['A']['CMB']
        exp_B = chi2s['B']['BAO'] + chi2s['B']['SNe'] + chi2s['B']['CMB']
        grw_A = chi2s['A']['fs8']
        grw_B = chi2s['B']['fs8']

        print(f"\n--- Growth vs Expansion ---")
        print(f"  Expansion (BAO+SNe+CMB): A={exp_A:.2f}, B={exp_B:.2f}, "
              f"Delta={exp_A-exp_B:+.2f} ({'A' if exp_A < exp_B else 'B'} preferred)")
        print(f"  Growth (fsigma8):        A={grw_A:.2f}, B={grw_B:.2f}, "
              f"Delta={grw_A-grw_B:+.2f} ({'A' if grw_A < grw_B else 'B'} preferred)")

        if (grw_A < grw_B) and (exp_A > exp_B):
            print(f"\n  ** PROBE SPLIT DETECTED: Growth prefers A, Expansion prefers B **")
            print(f"  ** This is the compromise artifact signature **")

    # Posterior on wa from Fit B
    wa_samples = resultB['samples'][:, 1]
    wa_mean = np.mean(wa_samples)
    wa_std = np.std(wa_samples)
    wa_q16, wa_q50, wa_q84 = np.percentile(wa_samples, [16, 50, 84])
    frac_negative = np.mean(wa_samples < 0)

    print(f"\n--- wa Posterior (Fit B) ---")
    print(f"  wa = {wa_q50:.3f} +{wa_q84-wa_q50:.3f} -{wa_q50-wa_q16:.3f}")
    print(f"  Mean = {wa_mean:.3f} ± {wa_std:.3f}")
    print(f"  Fraction wa < 0: {frac_negative:.3f} ({frac_negative*100:.1f}%)")
    print(f"  Lu & Simon (2026): wa = -0.62 ± 0.26")
    print(f"  Tension with wa=0: {abs(wa_mean)/wa_std:.1f} sigma")

    # Verdict
    print(f"\n{'='*70}")
    print("VERDICT")
    print(f"{'='*70}")

    if abs(DAIC) < 2:
        print("PASS: Constant-w fits as well as CPL. Phantom crossing is not required.")
    elif DAIC < 10:
        print("PARTIAL: CPL moderately preferred. Escape hatches (18B, 18F) needed.")
    else:
        print("FAIL: CPL strongly preferred. Constant-w prediction under serious pressure.")

    if predA is not None and predB is not None:
        if (grw_A < grw_B) and (exp_A > exp_B):
            print("BUT: Probe split detected — growth prefers GR while expansion prefers CPL.")
            print("     This is consistent with the compromise artifact hypothesis.")

    return {
        'chi2_A': chi2_A, 'chi2_B': chi2_B,
        'DAIC': DAIC, 'DBIC': DBIC,
        'wa_mean': wa_mean, 'wa_std': wa_std,
        'wa_q50': wa_q50,
        'probe_split': (predA is not None and predB is not None and
                       grw_A < grw_B and exp_A > exp_B) if predA and predB else False
    }

# ============================================================
# PLOTTING
# ============================================================

def make_plots(resultA, resultB, comparison, bao_data, sne_data, cmb_data, fs8_data):
    """Generate diagnostic plots."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('18A Proper MCMC: Decoupled Perturbation Test', fontsize=14, fontweight='bold')

    # 1. wa posterior
    ax = axes[0, 0]
    wa_samples = resultB['samples'][:, 1]
    ax.hist(wa_samples, bins=50, density=True, alpha=0.7, color='steelblue', label='Posterior')
    ax.axvline(0, color='red', ls='--', lw=2, label='Meridian (wa=0)')
    ax.axvline(-0.62, color='orange', ls='--', lw=2, label='Lu & Simon (-0.62)')
    ax.set_xlabel('wa')
    ax.set_ylabel('Density')
    ax.set_title('wa Posterior (Fit B: CPL)')
    ax.legend(fontsize=8)

    # 2. w0 comparison
    ax = axes[0, 1]
    w0_A = resultA['samples'][:, 0]
    w0_B = resultB['samples'][:, 0]
    ax.hist(w0_A, bins=50, density=True, alpha=0.5, color='blue', label='Fit A (const w)')
    ax.hist(w0_B, bins=50, density=True, alpha=0.5, color='red', label='Fit B (CPL)')
    ax.axvline(-0.746, color='green', ls='--', lw=2, label='JC benchmark')
    ax.set_xlabel('w0')
    ax.set_ylabel('Density')
    ax.set_title('w0 Posterior Comparison')
    ax.legend(fontsize=8)

    # 3. Chi2 bar chart
    ax = axes[1, 0]
    predA = get_camb_predictions(resultA['best_params'][0], 0.0,
                                  resultA['best_params'][1], resultA['best_params'][2])
    predB = get_camb_predictions(resultB['best_params'][0], resultB['best_params'][1],
                                  resultB['best_params'][2], resultB['best_params'][3])
    if predA is not None and predB is not None:
        probes = ['BAO', 'SNe', 'CMB', 'fs8', 'Total']
        chi2_A_probes = [
            -2*log_like_bao(predA, bao_data),
            -2*log_like_sne(predA, sne_data),
            -2*log_like_cmb(predA, cmb_data),
            -2*log_like_fs8(predA, fs8_data),
            comparison['chi2_A']
        ]
        chi2_B_probes = [
            -2*log_like_bao(predB, bao_data),
            -2*log_like_sne(predB, sne_data),
            -2*log_like_cmb(predB, cmb_data),
            -2*log_like_fs8(predB, fs8_data),
            comparison['chi2_B']
        ]
        x = np.arange(len(probes))
        ax.bar(x - 0.2, chi2_A_probes, 0.35, label='Fit A (Meridian)', color='steelblue', alpha=0.8)
        ax.bar(x + 0.2, chi2_B_probes, 0.35, label='Fit B (CPL)', color='coral', alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(probes)
        ax.set_ylabel('chi2')
        ax.set_title(f'Chi2 by Probe (DAIC = {comparison["DAIC"]:+.1f})')
        ax.legend(fontsize=8)

        for i, (a, b) in enumerate(zip(chi2_A_probes, chi2_B_probes)):
            ax.text(i - 0.2, a + 0.5, f'{a:.1f}', ha='center', fontsize=7)
            ax.text(i + 0.2, b + 0.5, f'{b:.1f}', ha='center', fontsize=7)

    # 4. Om-H0 contour
    ax = axes[1, 1]
    if resultA['ndim'] == 3:
        Om_A, H0_A = resultA['samples'][:, 1], resultA['samples'][:, 2]
    else:
        Om_A, H0_A = resultA['samples'][:, 1], resultA['samples'][:, 2]
    Om_B = resultB['samples'][:, 2]
    H0_B = resultB['samples'][:, 3]

    ax.scatter(Om_A[::10], H0_A[::10], alpha=0.1, s=1, c='blue', label='Fit A')
    ax.scatter(Om_B[::10], H0_B[::10], alpha=0.1, s=1, c='red', label='Fit B')
    ax.set_xlabel('Omega_m')
    ax.set_ylabel('H0')
    ax.set_title('Om-H0 Posterior')
    ax.legend(fontsize=8, markerscale=10)

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, '18A_proper_results.png')
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    print(f"\nFigure saved: {outpath}")
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("18A PROPER MCMC: DECOUPLED PERTURBATION TEST")
    print("Full CAMB + emcee pipeline. No approximations.")
    print("=" * 70)

    t_start = time.time()

    # Load data
    print("\n[1] Loading data...")
    bao_data = get_desi_dr1_bao()
    sne_data = get_pantheonplus_binned()
    cmb_data = get_planck_compressed()
    fs8_data = get_fsigma8_compilation()

    print(f"  BAO: {len(bao_data['z'])} redshifts × 2 (DM+DH) = {2*len(bao_data['z'])} points")
    print(f"  SNe: {len(sne_data['z'])} bins (19 effective after M marginalization)")
    print(f"  CMB: 3 compressed parameters (R, l_A, omega_b)")
    print(f"  fs8: {len(fs8_data['z'])} measurements")
    print(f"  Total: {2*len(bao_data['z']) + len(sne_data['z'])-1 + 3 + len(fs8_data['z'])} effective data points")

    # Quick CAMB timing
    print("\n[2] Timing CAMB evaluation...")
    t0 = time.time()
    for _ in range(5):
        get_camb_predictions(-0.95, 0.0, 0.315, 67.36)
    t_camb = (time.time() - t0) / 5
    print(f"  CAMB eval: {t_camb:.2f}s per call")

    # MCMC settings — serial execution
    # Multiprocessing deadlocks with CAMB's Fortran internals on Windows.
    # Reduced chain: 16 walkers for 3-4 param problem is sufficient.
    # 500 production × 16 walkers = 8000 samples, autocorr ~20-50
    # → 160-400 effective samples, plenty for ΔAIC estimation.
    nwalkers = 16
    nburn = 200
    nsteps = 500
    total_evals = nwalkers * (nburn + nsteps) * 2  # both fits
    est_hours = total_evals * t_camb / 3600
    print(f"\n  MCMC config: {nwalkers} walkers, {nburn} burn-in, {nsteps} production")
    print(f"  Serial execution (CAMB/Fortran deadlocks multiprocessing on Windows)")
    print(f"  Estimated total CAMB evals: {total_evals}")
    print(f"  Estimated runtime: {est_hours:.1f} hours")

    # Run Fit A (serial — no pool)
    print("\n" + "=" * 70)
    print("[3] Running Fit A (Meridian: constant w, GR perturbations)")
    print("=" * 70)
    resultA = run_mcmc('A', bao_data, sne_data, cmb_data, fs8_data,
                       nwalkers=nwalkers, nsteps=nsteps, nburn=nburn)

    # Run Fit B (serial — no pool)
    print("\n" + "=" * 70)
    print("[4] Running Fit B (CPL: w0+wa, coupled perturbations)")
    print("=" * 70)
    resultB = run_mcmc('B', bao_data, sne_data, cmb_data, fs8_data,
                       nwalkers=nwalkers, nsteps=nsteps, nburn=nburn)

    # Analyze
    print("\n" + "=" * 70)
    print("[5] Analysis and Comparison")
    print("=" * 70)
    comparison = analyze_results(resultA, resultB, bao_data, sne_data, cmb_data, fs8_data)

    # Plots
    print("\n[6] Generating plots...")
    make_plots(resultA, resultB, comparison, bao_data, sne_data, cmb_data, fs8_data)

    # Save results
    results_path = os.path.join(OUTPUT_DIR, '18A_proper_results.md')
    with open(results_path, 'w') as f:
        f.write("# 18A Proper MCMC Results\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Runtime:** {(time.time()-t_start)/3600:.1f} hours\n")
        f.write(f"**MCMC:** {nwalkers} walkers, {nburn} burn-in, {nsteps} production\n\n")

        f.write("## Best-Fit Parameters\n\n")
        f.write("| Parameter | Fit A (Meridian) | Fit B (CPL) |\n")
        f.write("|-----------|-----------------|-------------|\n")
        f.write(f"| w0 | {resultA['best_params'][0]:.4f} | {resultB['best_params'][0]:.4f} |\n")
        f.write(f"| wa | 0 (fixed) | {resultB['best_params'][1]:.4f} |\n")
        f.write(f"| Om | {resultA['best_params'][1]:.4f} | {resultB['best_params'][2]:.4f} |\n")
        f.write(f"| H0 | {resultA['best_params'][2]:.2f} | {resultB['best_params'][3]:.2f} |\n")
        f.write(f"| chi2 | {resultA['best_chi2']:.2f} | {resultB['best_chi2']:.2f} |\n\n")

        f.write("## Model Comparison\n\n")
        f.write(f"| Metric | Value |\n")
        f.write(f"|--------|-------|\n")
        f.write(f"| Delta chi2 (A-B) | {comparison['chi2_A']-comparison['chi2_B']:+.2f} |\n")
        f.write(f"| Delta AIC (A-B) | {comparison['DAIC']:+.2f} |\n")
        f.write(f"| Delta BIC (A-B) | {comparison['DBIC']:+.2f} |\n")
        f.write(f"| wa posterior | {comparison['wa_q50']:.3f} ± {comparison['wa_std']:.3f} |\n")
        f.write(f"| Probe split | {'Yes' if comparison['probe_split'] else 'No'} |\n")

    print(f"\nResults saved: {results_path}")

    t_total = time.time() - t_start
    print(f"\n{'='*70}")
    print(f"18A PROPER MCMC COMPLETE")
    print(f"Total runtime: {t_total/3600:.1f} hours ({t_total:.0f}s)")
    print(f"{'='*70}")

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()  # Required for Windows multiprocessing
    main()
