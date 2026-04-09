#!/usr/bin/env python3
"""
18A v3: Decoupled Perturbation Test with FULL Pantheon+ Covariance
===================================================================
Upgrade from v2: replaces diagonal-only 19-bin SNe with full 1590-SN
Pantheon+ stat+sys covariance and analytic M marginalization.

Fit A (Meridian): constant w0, GR perturbations (mu=Sigma=1). 3 params.
Fit B (CPL):      w0 + wa, perturbations coupled to w(z).    4 params.

Data:
  - DESI DR1 BAO (6 z-bins, D_M/r_d + D_H/r_d)
  - Pantheon+ FULL covariance (1590 SNe after z>0.01 cut, 1590x1590 C_inv)
  - Planck 2018 compressed CMB (R, l_A, omega_b with correlations)
  - f*sigma_8 compilation (7 measurements)

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-20 (upgrade from 2026-03-19 v2)
"""

import numpy as np
import camb
import emcee
import time
import os
import sys
import warnings
from scipy.optimize import minimize

warnings.filterwarnings('ignore')
import logging
logging.getLogger('camb').setLevel(logging.ERROR)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# DATA
# ============================================================

def get_desi_dr1_bao():
    """DESI DR1 consensus BAO (arXiv:2404.03002, Table 1)."""
    return {
        'z':    np.array([0.30,  0.51,  0.71,  0.93,  1.32,  2.33]),
        'DM_rd': np.array([7.93, 13.62, 17.86, 21.71, 27.79, 39.71]),
        'DM_rd_err': np.array([0.15, 0.25, 0.33, 0.28, 0.69, 0.94]),
        'DH_rd': np.array([20.0, 22.3, 20.1, 17.88, 13.82, 8.52]),
        'DH_rd_err': np.array([1.0, 0.6, 0.5, 0.35, 0.42, 0.17]),
    }

def load_pantheonplus_full():
    """Load full Pantheon+ with stat+sys covariance.

    Returns dict with m_obs, z_cmb, z_hel, C_inv_marg, N.
    M is analytically marginalized via Woodbury identity.
    """
    data_dir = os.path.join(OUTPUT_DIR, 'data', 'pantheonplus')
    dat_file = os.path.join(data_dir, 'Pantheon+SH0ES.dat')
    cov_file = os.path.join(data_dir, 'Pantheon+SH0ES_STAT+SYS.cov')

    print("  Loading Pantheon+ data...", flush=True)
    data = np.genfromtxt(dat_file, names=True, dtype=None, encoding='utf-8')

    z_cmb_all = np.array([float(row['zHD']) for row in data])
    z_hel_all = np.array([float(row['zHEL']) for row in data])
    m_obs_all = np.array([float(row['m_b_corr']) for row in data])

    print(f"    {len(z_cmb_all)} SNe loaded", flush=True)

    print("  Loading covariance matrix...", flush=True)
    cov_raw = np.loadtxt(cov_file)
    N_cov = int(cov_raw[0])
    C_full = cov_raw[1:].reshape(N_cov, N_cov)
    print(f"    {N_cov}x{N_cov} covariance ({C_full.nbytes/1e6:.1f} MB)", flush=True)

    # z > 0.01 cut (Pantheon+ only, no SH0ES calibrators)
    mask = z_cmb_all > 0.01
    m_obs = m_obs_all[mask]
    z_cmb = z_cmb_all[mask]
    z_hel = z_hel_all[mask]
    C = C_full[np.ix_(mask, mask)]
    N_cut = mask.sum()
    print(f"    After z > 0.01 cut: {N_cut} SNe", flush=True)

    # Invert and marginalize over M
    print("  Inverting covariance and marginalizing M...", flush=True)
    C_inv = np.linalg.inv(C)
    ones = np.ones(N_cut)
    C_inv_ones = C_inv @ ones
    C_inv_marg = C_inv - np.outer(C_inv_ones, C_inv_ones) / (ones @ C_inv_ones)
    print(f"    Done. C_inv_marg shape: {C_inv_marg.shape}", flush=True)

    return {
        'm_obs': m_obs,
        'z_cmb': z_cmb,
        'z_hel': z_hel,
        'C_inv_marg': C_inv_marg,
        'N': N_cut
    }

def get_planck_compressed():
    """Planck 2018 compressed CMB distance priors (arXiv:1807.06209)."""
    means = np.array([1.7502, 301.471, 0.02237])
    sigmas = np.array([0.0046, 0.090, 0.00015])
    corr = np.array([
        [1.0,    0.46,  -0.66],
        [0.46,   1.0,   -0.33],
        [-0.66, -0.33,   1.0]
    ])
    cov = np.outer(sigmas, sigmas) * corr
    cov_inv = np.linalg.inv(cov)
    return {'means': means, 'cov_inv': cov_inv, 'sigmas': sigmas}

def get_fsigma8_compilation():
    """Growth rate compilation: f*sigma_8(z)."""
    return {
        'z':     np.array([0.067, 0.38,  0.51,  0.61,  0.70,  0.85,  1.48]),
        'fs8':   np.array([0.423, 0.497, 0.459, 0.436, 0.473, 0.315, 0.342]),
        'fs8_err': np.array([0.055, 0.045, 0.038, 0.034, 0.041, 0.095, 0.070]),
    }

# ============================================================
# THEORY: Full CAMB predictions
# ============================================================

def get_camb_predictions(w0, wa, Om, H0, sne_z_cmb, sne_z_hel,
                          ob=0.02237, ns=0.9649, As=2.1e-9):
    """Run CAMB and return all observables.

    Now computes distances at ALL 1590 Pantheon+ redshifts.
    """
    try:
        ombh2 = ob
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
        pars.NonLinear = camb.model.NonLinear_none

        results = camb.get_results(pars)

        pred = {}

        # BAO: D_M/r_d and D_H/r_d
        rd = results.get_derived_params()['rdrag']
        bao_z = np.array([0.30, 0.51, 0.71, 0.93, 1.32, 2.33])
        pred['DM_rd'] = np.array([results.comoving_radial_distance(z) / rd for z in bao_z])
        pred['DH_rd'] = np.array([299792.458 / results.hubble_parameter(z) / rd for z in bao_z])

        # SNe: distance modulus with proper heliocentric correction
        # d_L = (1 + z_hel) * d_C(z_cmb) for flat universe
        # mu = 5 * log10(d_L / Mpc) + 25
        d_C = np.array([results.comoving_radial_distance(z) for z in sne_z_cmb])
        d_L = (1 + sne_z_hel) * d_C
        pred['mu_sne'] = 5.0 * np.log10(d_L) + 25.0

        # CMB compressed: R, l_A, omega_b
        derived = results.get_derived_params()
        zstar = derived['zstar']
        rs_star = derived['rstar']
        DA_star = results.angular_diameter_distance(zstar)
        DM_star = DA_star * (1 + zstar)
        R = np.sqrt(Om) * H0 * DM_star / 299792.458
        l_A = np.pi * DM_star / rs_star
        pred['R'] = R
        pred['l_A'] = l_A
        pred['omega_b'] = ombh2

        # fsigma8
        fs8_z = np.array([0.067, 0.38, 0.51, 0.61, 0.70, 0.85, 1.48])
        all_fs8 = results.get_fsigma8()
        all_z = sorted(set(zs_for_power))
        from scipy.interpolate import interp1d
        fs8_interp = interp1d(all_z, all_fs8, kind='cubic', fill_value='extrapolate')
        pred['fsigma8'] = fs8_interp(fs8_z)
        pred['sigma8'] = results.get_sigma8_0()

        return pred

    except Exception:
        return None

# ============================================================
# LIKELIHOODS
# ============================================================

def log_like_bao(pred, data):
    """BAO chi-squared: D_M/r_d and D_H/r_d (diagonal)."""
    chi2_DM = np.sum(((pred['DM_rd'] - data['DM_rd']) / data['DM_rd_err'])**2)
    chi2_DH = np.sum(((pred['DH_rd'] - data['DH_rd']) / data['DH_rd_err'])**2)
    return -0.5 * (chi2_DM + chi2_DH)

def log_like_sne(pred, sne_data):
    """Pantheon+ with full covariance and M marginalized."""
    delta = sne_data['m_obs'] - pred['mu_sne']
    chi2 = delta @ sne_data['C_inv_marg'] @ delta
    return -0.5 * chi2

def log_like_cmb(pred, data):
    """CMB compressed likelihood with full covariance."""
    vec = np.array([pred['R'], pred['l_A'], pred['omega_b']]) - data['means']
    chi2 = vec @ data['cov_inv'] @ vec
    return -0.5 * chi2

def log_like_fs8(pred, data):
    """f*sigma_8 chi-squared (diagonal errors)."""
    chi2 = np.sum(((pred['fsigma8'] - data['fs8']) / data['fs8_err'])**2)
    return -0.5 * chi2

# ============================================================
# PRIORS AND POSTERIORS
# ============================================================

def log_prior_fitA(theta):
    w0, Om, H0 = theta
    if -2.0 < w0 < -0.3 and 0.1 < Om < 0.6 and 55.0 < H0 < 80.0:
        return 0.0
    return -np.inf

def log_prior_fitB(theta):
    w0, wa, Om, H0 = theta
    if -2.0 < w0 < 0.5 and -4.0 < wa < 3.0 and 0.1 < Om < 0.6 and 55.0 < H0 < 80.0:
        return 0.0
    return -np.inf

def log_posterior_fitA(theta, bao_data, sne_data, cmb_data, fs8_data):
    lp = log_prior_fitA(theta)
    if not np.isfinite(lp):
        return -np.inf

    w0, Om, H0 = theta
    pred = get_camb_predictions(w0, 0.0, Om, H0,
                                 sne_data['z_cmb'], sne_data['z_hel'])
    if pred is None:
        return -np.inf

    ll = (log_like_bao(pred, bao_data) +
          log_like_sne(pred, sne_data) +
          log_like_cmb(pred, cmb_data) +
          log_like_fs8(pred, fs8_data))
    return lp + ll

def log_posterior_fitB(theta, bao_data, sne_data, cmb_data, fs8_data):
    lp = log_prior_fitB(theta)
    if not np.isfinite(lp):
        return -np.inf

    w0, wa, Om, H0 = theta
    if w0 + wa > 0:
        return -np.inf

    pred = get_camb_predictions(w0, wa, Om, H0,
                                 sne_data['z_cmb'], sne_data['z_hel'])
    if pred is None:
        return -np.inf

    ll = (log_like_bao(pred, bao_data) +
          log_like_sne(pred, sne_data) +
          log_like_cmb(pred, cmb_data) +
          log_like_fs8(pred, fs8_data))
    return lp + ll

# ============================================================
# OPTIMIZER
# ============================================================

def find_bestfit(fit_type, bao_data, sne_data, cmb_data, fs8_data):
    print(f"\n  Finding best-fit for {fit_type}...", flush=True)

    if fit_type == 'A':
        neg_lp = lambda t: -(v if np.isfinite(v := log_posterior_fitA(t, bao_data, sne_data, cmb_data, fs8_data)) else -1e30)
        starts = [[-0.75, 0.315, 67.36], [-0.95, 0.310, 67.5],
                  [-1.0, 0.320, 68.0], [-0.85, 0.305, 67.0]]
    else:
        neg_lp = lambda t: -(v if np.isfinite(v := log_posterior_fitB(t, bao_data, sne_data, cmb_data, fs8_data)) else -1e30)
        starts = [[-0.75, -0.5, 0.315, 67.36], [-0.90, -0.3, 0.310, 67.5],
                  [-0.80, -1.0, 0.320, 68.0], [-1.0, 0.0, 0.305, 67.0]]

    best_val, best_x = 1e30, None
    for x0 in starts:
        try:
            res = minimize(neg_lp, x0, method='Nelder-Mead',
                          options={'maxiter': 3000, 'xatol': 1e-5, 'fatol': 1e-3})
            if res.fun < best_val:
                best_val, best_x = res.fun, res.x
                print(f"    Start {x0[:2]}: chi2={2*res.fun:.2f}", flush=True)
        except Exception:
            pass

    if best_x is None:
        best_x = np.array(starts[0])

    print(f"  Best fit: {best_x}, chi2={2*best_val:.2f}", flush=True)
    return best_x, 2 * best_val

# ============================================================
# MCMC
# ============================================================

def run_mcmc(fit_type, bao_data, sne_data, cmb_data, fs8_data,
             nwalkers=16, nsteps=500, nburn=200):

    print(f"\n{'='*60}")
    print(f"MCMC: Fit {fit_type}")
    print(f"{'='*60}", flush=True)

    best_x, best_chi2 = find_bestfit(fit_type, bao_data, sne_data, cmb_data, fs8_data)

    if fit_type == 'A':
        ndim, labels = 3, ['w0', 'Om', 'H0']
        log_post = log_posterior_fitA
        spread = np.array([0.02, 0.005, 0.5])
    else:
        ndim, labels = 4, ['w0', 'wa', 'Om', 'H0']
        log_post = log_posterior_fitB
        spread = np.array([0.02, 0.1, 0.005, 0.5])

    pos = best_x + spread * np.random.randn(nwalkers, ndim)

    print(f"  {nwalkers} walkers, {nburn} burn-in + {nsteps} production steps", flush=True)

    sampler = emcee.EnsembleSampler(
        nwalkers, ndim, log_post,
        args=(bao_data, sne_data, cmb_data, fs8_data)
    )

    # Burn-in
    t0 = time.time()
    print(f"\n  Burn-in ({nburn} steps)...", flush=True)
    state = pos
    for i in range(0, nburn, 50):
        batch = min(50, nburn - i)
        state = sampler.run_mcmc(state, batch, progress=False)
        elapsed = time.time() - t0
        print(f"    Burn-in step {i+batch}/{nburn} | elapsed={elapsed:.0f}s", flush=True)
    t_burn = time.time() - t0
    print(f"  Burn-in done in {t_burn:.0f}s ({t_burn/nburn:.2f}s/step)", flush=True)

    # Production
    sampler.reset()
    t0 = time.time()
    print(f"\n  Production ({nsteps} steps)...", flush=True)
    for i in range(0, nsteps, 100):
        batch = min(100, nsteps - i)
        state = sampler.run_mcmc(state, batch, progress=False)
        elapsed = time.time() - t0
        done_frac = (i + batch) / nsteps
        eta = elapsed / done_frac * (1 - done_frac) if done_frac > 0 else 0
        accept = np.mean(sampler.acceptance_fraction)
        print(f"    Step {i+batch}/{nsteps} | accept={accept:.3f} | "
              f"elapsed={elapsed:.0f}s | ETA={eta:.0f}s", flush=True)
    t_prod = time.time() - t0
    print(f"\n  Production done in {t_prod:.0f}s ({t_prod/60:.1f} min)", flush=True)

    # Extract chains
    flat_samples = sampler.get_chain(flat=True)
    flat_logprob = sampler.get_log_prob(flat=True)

    # SAVE CHAINS TO DISK (learned from v2 crash)
    chain_path = os.path.join(OUTPUT_DIR, f'18A_v3_chain_{fit_type}.npz')
    np.savez(chain_path, samples=flat_samples, logprob=flat_logprob,
             labels=labels, best_x=best_x, best_chi2=best_chi2)
    print(f"  Chain saved to {chain_path}", flush=True)

    # Convergence
    try:
        tau = sampler.get_autocorr_time(quiet=True)
        print(f"  Autocorrelation times: {tau}")
        print(f"  Effective samples: {nwalkers * nsteps / np.max(tau):.0f}")
    except Exception:
        print("  (Autocorrelation time estimation failed)")

    # Best fit from chain
    best_idx = np.argmax(flat_logprob)
    best_params = flat_samples[best_idx]
    best_logprob = flat_logprob[best_idx]

    print(f"\n  Best-fit from chain:")
    for l, v in zip(labels, best_params):
        print(f"    {l} = {v:.4f}")
    print(f"    chi2 = {-2*best_logprob:.2f}", flush=True)

    # Posterior stats
    print(f"\n  Posterior summary:")
    for i, l in enumerate(labels):
        mean = np.mean(flat_samples[:, i])
        std = np.std(flat_samples[:, i])
        q16, q50, q84 = np.percentile(flat_samples[:, i], [16, 50, 84])
        print(f"    {l} = {q50:.4f} +{q84-q50:.4f} -{q50-q16:.4f} (mean={mean:.4f} +/- {std:.4f})",
              flush=True)

    return {
        'fit_type': fit_type, 'labels': labels,
        'samples': flat_samples, 'logprob': flat_logprob,
        'best_params': best_params, 'best_chi2': -2 * best_logprob,
        'ndim': ndim, 'nwalkers': nwalkers, 'nsteps': nsteps,
        'acceptance': np.mean(sampler.acceptance_fraction),
    }

# ============================================================
# ANALYSIS
# ============================================================

def analyze_results(resultA, resultB, bao_data, sne_data, cmb_data, fs8_data):

    print(f"\n{'='*70}")
    print("18A v3 MCMC -- FINAL RESULTS (Full Pantheon+ Covariance)")
    print(f"{'='*70}", flush=True)

    chi2_A = resultA['best_chi2']
    chi2_B = resultB['best_chi2']
    npar_A, npar_B = resultA['ndim'], resultB['ndim']

    # Data points: 12 BAO + (1590-1) SNe + 3 CMB + 7 fs8
    # The -1 is for M marginalization (one degree of freedom removed)
    n_bao = 12
    n_sne = sne_data['N'] - 1  # 1589 effective
    n_cmb = 3
    n_fs8 = 7
    n_total = n_bao + n_sne + n_cmb + n_fs8

    dof_A = n_total - npar_A
    dof_B = n_total - npar_B

    AIC_A = chi2_A + 2 * npar_A
    AIC_B = chi2_B + 2 * npar_B
    DAIC = AIC_A - AIC_B

    BIC_A = chi2_A + npar_A * np.log(n_total)
    BIC_B = chi2_B + npar_B * np.log(n_total)
    DBIC = BIC_A - BIC_B

    print(f"\n--- Best-Fit Parameters ---")
    print(f"\nFit A (Meridian: constant w, GR perturbations):")
    for l, v in zip(resultA['labels'], resultA['best_params']):
        print(f"  {l} = {v:.4f}")
    print(f"  chi2 = {chi2_A:.2f}, chi2/dof = {chi2_A/dof_A:.4f}")

    print(f"\nFit B (CPL: w0+wa, coupled perturbations):")
    for l, v in zip(resultB['labels'], resultB['best_params']):
        print(f"  {l} = {v:.4f}")
    print(f"  chi2 = {chi2_B:.2f}, chi2/dof = {chi2_B/dof_B:.4f}")

    print(f"\n--- Model Comparison ---")
    print(f"  Delta chi2 (A-B) = {chi2_A - chi2_B:+.2f}")
    print(f"  Delta AIC  (A-B) = {DAIC:+.2f}")
    print(f"  Delta BIC  (A-B) = {DBIC:+.2f}")

    if abs(DAIC) < 2:
        print(f"  => STATISTICALLY INDISTINGUISHABLE (|DAIC| < 2)")
    elif abs(DAIC) < 4:
        print(f"  => WEAK preference ({'B' if DAIC > 0 else 'A'}) (|DAIC| < 4)")
    elif abs(DAIC) < 10:
        print(f"  => MODERATE preference ({'B' if DAIC > 0 else 'A'}) (|DAIC| < 10)")
    else:
        print(f"  => STRONG preference ({'B' if DAIC > 0 else 'A'}) (|DAIC| > 10)")

    # Probe-by-probe chi2
    print(f"\n--- Probe-by-Probe chi2 at Best Fit ---", flush=True)
    predA = get_camb_predictions(resultA['best_params'][0], 0.0,
                                  resultA['best_params'][1], resultA['best_params'][2],
                                  sne_data['z_cmb'], sne_data['z_hel'])
    predB = get_camb_predictions(resultB['best_params'][0], resultB['best_params'][1],
                                  resultB['best_params'][2], resultB['best_params'][3],
                                  sne_data['z_cmb'], sne_data['z_hel'])

    if predA is not None and predB is not None:
        probes = {
            'BAO': (log_like_bao, bao_data),
            'SNe': (log_like_sne, sne_data),
            'CMB': (log_like_cmb, cmb_data),
            'fs8': (log_like_fs8, fs8_data),
        }
        print(f"     {'Probe':>8s}  {'Fit A':>8s}  {'Fit B':>8s}  {'Delta':>8s}   Prefers")
        exp_A, exp_B, grw_A, grw_B = 0, 0, 0, 0
        for name, (lik_fn, dat) in probes.items():
            c2_A = -2 * lik_fn(predA, dat)
            c2_B = -2 * lik_fn(predB, dat)
            d = c2_A - c2_B
            pref = 'B' if d > 0 else 'A' if d < 0 else '='
            print(f"     {name:>8s}  {c2_A:8.2f}  {c2_B:8.2f}  {d:+8.2f}         {pref}")
            if name != 'fs8':
                exp_A += c2_A; exp_B += c2_B
            else:
                grw_A += c2_A; grw_B += c2_B

        print(f"\n--- Growth vs Expansion ---")
        print(f"  Expansion (BAO+SNe+CMB): A={exp_A:.2f}, B={exp_B:.2f}, Delta={exp_A-exp_B:+.2f}")
        print(f"  Growth (fsigma8):        A={grw_A:.2f}, B={grw_B:.2f}, Delta={grw_A-grw_B:+.2f}")

    # wa posterior
    wa_samples = resultB['samples'][:, 1]
    wa_mean, wa_std = np.mean(wa_samples), np.std(wa_samples)
    wa_q16, wa_q50, wa_q84 = np.percentile(wa_samples, [16, 50, 84])
    frac_negative = np.mean(wa_samples < 0)

    print(f"\n--- wa Posterior (Fit B) ---")
    print(f"  wa = {wa_q50:.3f} +{wa_q84-wa_q50:.3f} -{wa_q50-wa_q16:.3f}")
    print(f"  Mean = {wa_mean:.3f} +/- {wa_std:.3f}")
    print(f"  Fraction wa < 0: {frac_negative:.3f} ({frac_negative*100:.1f}%)")
    print(f"  Tension with wa=0: {abs(wa_mean)/wa_std:.1f} sigma")
    print(f"  DESI (Lu & Simon 2026): wa = -0.62 +/- 0.26")
    tension_desi = abs(wa_mean - (-0.62)) / np.sqrt(wa_std**2 + 0.26**2)
    print(f"  Tension with DESI: {tension_desi:.1f} sigma")

    # Verdict
    print(f"\n{'='*70}")
    print("VERDICT")
    print(f"{'='*70}")
    if abs(DAIC) < 4:
        print("PASS: Constant-w fits as well as CPL (|DAIC| < 4).")
        print("      PRL letter viable.")
    elif abs(DAIC) < 10:
        print("PARTIAL: CPL moderately preferred. Need to decompose signal.")
    else:
        print("PRESSURE: CPL strongly preferred. Escape hatches needed.")

    if predA is not None and predB is not None:
        if grw_A - grw_B < 1.0:
            print("NOTE: Growth data barely discriminate -- perturbation coupling is NOT driving signal.")

    return {
        'chi2_A': chi2_A, 'chi2_B': chi2_B,
        'DAIC': DAIC, 'DBIC': DBIC,
        'wa_mean': wa_mean, 'wa_std': wa_std, 'wa_q50': wa_q50,
    }

# ============================================================
# PLOTS
# ============================================================

def make_plots(resultA, resultB, comparison, sne_data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('18A v3: Decoupled Perturbation Test (Full Pantheon+ Covariance)',
                 fontsize=13, fontweight='bold')

    # 1. wa posterior
    ax = axes[0, 0]
    wa_samples = resultB['samples'][:, 1]
    ax.hist(wa_samples, bins=50, density=True, alpha=0.7, color='steelblue', label='Posterior')
    ax.axvline(0, color='red', ls='--', lw=2, label='Meridian ($w_a=0$)')
    ax.axvline(-0.62, color='orange', ls='--', lw=2, label='DESI ($w_a=-0.62$)')
    ax.set_xlabel('$w_a$')
    ax.set_ylabel('Density')
    ax.set_title('$w_a$ Posterior (Fit B: CPL)')
    ax.legend(fontsize=8)

    # 2. w0 comparison
    ax = axes[0, 1]
    ax.hist(resultA['samples'][:, 0], bins=50, density=True, alpha=0.5,
            color='blue', label='Fit A (const w)')
    ax.hist(resultB['samples'][:, 0], bins=50, density=True, alpha=0.5,
            color='red', label='Fit B (CPL)')
    ax.axvline(-0.746, color='green', ls='--', lw=2, label='JC benchmark')
    ax.set_xlabel('$w_0$')
    ax.set_ylabel('Density')
    ax.set_title('$w_0$ Posterior Comparison')
    ax.legend(fontsize=8)

    # 3. Om-H0 contour
    ax = axes[1, 0]
    Om_A = resultA['samples'][:, 1]
    H0_A = resultA['samples'][:, 2]
    Om_B = resultB['samples'][:, 2]
    H0_B = resultB['samples'][:, 3]
    ax.scatter(Om_A[::10], H0_A[::10], alpha=0.1, s=1, c='blue', label='Fit A')
    ax.scatter(Om_B[::10], H0_B[::10], alpha=0.1, s=1, c='red', label='Fit B')
    ax.set_xlabel('$\\Omega_m$')
    ax.set_ylabel('$H_0$')
    ax.set_title('$\\Omega_m$-$H_0$ Posterior')
    ax.legend(fontsize=8, markerscale=10)

    # 4. Summary
    ax = axes[1, 1]
    ax.axis('off')
    DAIC = comparison['DAIC']
    txt = (f"DAIC (A-B) = {DAIC:+.2f}\n\n"
           f"Fit A: chi2 = {comparison['chi2_A']:.2f}\n"
           f"Fit B: chi2 = {comparison['chi2_B']:.2f}\n\n"
           f"wa = {comparison['wa_q50']:.3f} +/- {comparison['wa_std']:.3f}\n\n"
           f"SNe: Full Pantheon+ (1590 SNe)\n"
           f"     with stat+sys covariance\n"
           f"     M analytically marginalized")
    ax.text(0.1, 0.95, txt, transform=ax.transAxes, fontsize=12,
            va='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, '18A_v3_results.png')
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    print(f"\nFigure saved: {outpath}", flush=True)
    plt.close()

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("18A v3: DECOUPLED PERTURBATION TEST")
    print("Full Pantheon+ covariance (1590 SNe, stat+sys)")
    print("=" * 70, flush=True)

    t_start = time.time()

    # Load data
    print("\n[1] Loading data...", flush=True)
    bao_data = get_desi_dr1_bao()
    sne_data = load_pantheonplus_full()
    cmb_data = get_planck_compressed()
    fs8_data = get_fsigma8_compilation()

    n_bao = 2 * len(bao_data['z'])
    n_sne_eff = sne_data['N'] - 1  # M marginalized
    n_cmb = 3
    n_fs8 = len(fs8_data['z'])
    print(f"\n  BAO: {n_bao} points")
    print(f"  SNe: {sne_data['N']} Pantheon+ (1590-1={n_sne_eff} effective, M marginalized)")
    print(f"  CMB: {n_cmb} compressed parameters")
    print(f"  fs8: {n_fs8} measurements")
    print(f"  Total: {n_bao + n_sne_eff + n_cmb + n_fs8} effective data points", flush=True)

    # CAMB timing
    print("\n[2] Timing CAMB evaluation (with 1590 SNe distances)...", flush=True)
    t0 = time.time()
    for _ in range(3):
        get_camb_predictions(-0.95, 0.0, 0.315, 67.36,
                              sne_data['z_cmb'], sne_data['z_hel'])
    t_camb = (time.time() - t0) / 3
    print(f"  CAMB eval: {t_camb:.2f}s per call", flush=True)

    # MCMC settings
    nwalkers = 16
    nburn = 200
    nsteps = 500
    total_evals = nwalkers * (nburn + nsteps) * 2
    est_hours = total_evals * t_camb / 3600
    print(f"\n  MCMC: {nwalkers} walkers, {nburn} burn-in, {nsteps} production")
    print(f"  Serial (CAMB/Fortran deadlocks multiprocessing on Windows)")
    print(f"  Estimated total evals: {total_evals}")
    print(f"  Estimated runtime: {est_hours:.1f} hours", flush=True)

    # Fit A
    print("\n" + "=" * 70)
    print("[3] Running Fit A (Meridian: constant w, GR perturbations)")
    print("=" * 70, flush=True)
    resultA = run_mcmc('A', bao_data, sne_data, cmb_data, fs8_data,
                       nwalkers=nwalkers, nsteps=nsteps, nburn=nburn)

    # Fit B
    print("\n" + "=" * 70)
    print("[4] Running Fit B (CPL: w0+wa, coupled perturbations)")
    print("=" * 70, flush=True)
    resultB = run_mcmc('B', bao_data, sne_data, cmb_data, fs8_data,
                       nwalkers=nwalkers, nsteps=nsteps, nburn=nburn)

    # Analysis
    print("\n" + "=" * 70)
    print("[5] Analysis")
    print("=" * 70, flush=True)
    comparison = analyze_results(resultA, resultB, bao_data, sne_data, cmb_data, fs8_data)

    # Plots
    print("\n[6] Plots...", flush=True)
    make_plots(resultA, resultB, comparison, sne_data)

    # Save results
    rpath = os.path.join(OUTPUT_DIR, '18A_v3_results.md')
    with open(rpath, 'w', encoding='utf-8') as f:
        f.write("# 18A v3 Results: Full Pantheon+ Covariance\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Runtime:** {(time.time()-t_start)/3600:.1f} hours\n")
        f.write(f"**SNe:** Full Pantheon+ (1590 SNe, stat+sys covariance, M marginalized)\n\n")
        f.write(f"## Model Comparison\n\n")
        f.write(f"| Metric | Value |\n|--------|-------|\n")
        f.write(f"| Delta chi2 (A-B) | {comparison['chi2_A']-comparison['chi2_B']:+.2f} |\n")
        f.write(f"| Delta AIC (A-B) | {comparison['DAIC']:+.2f} |\n")
        f.write(f"| Delta BIC (A-B) | {comparison['DBIC']:+.2f} |\n")
        f.write(f"| wa posterior | {comparison['wa_q50']:.3f} +/- {comparison['wa_std']:.3f} |\n\n")
        f.write(f"## Best-Fit\n\n")
        f.write(f"**Fit A:** w0={resultA['best_params'][0]:.4f}, "
                f"Om={resultA['best_params'][1]:.4f}, H0={resultA['best_params'][2]:.2f}, "
                f"chi2={resultA['best_chi2']:.2f}\n\n")
        f.write(f"**Fit B:** w0={resultB['best_params'][0]:.4f}, "
                f"wa={resultB['best_params'][1]:.4f}, "
                f"Om={resultB['best_params'][2]:.4f}, H0={resultB['best_params'][3]:.2f}, "
                f"chi2={resultB['best_chi2']:.2f}\n")
    print(f"\nResults saved: {rpath}", flush=True)

    t_total = time.time() - t_start
    print(f"\n{'='*70}")
    print(f"18A v3 COMPLETE. Runtime: {t_total/3600:.1f} hours ({t_total:.0f}s)")
    print(f"{'='*70}", flush=True)

if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()
    main()
