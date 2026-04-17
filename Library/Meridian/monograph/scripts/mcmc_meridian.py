"""
MCMC for Meridian one-parameter model: posterior on zeta0.
Fast implementation: analytical Friedmann + CAMB r_d interpolation.
Uses emcee (3 params: w0, H0, Omega_m) + multi-probe likelihood.
April 2026. Clawd.
"""
import numpy as np
import emcee
from scipy.integrate import quad
from scipy.interpolate import interp1d
from scipy.stats import norm
import json, time, sys

# ============================================================
# Constants
# ============================================================
c_km_s = 299792.458
C_KK = 1.64e-4         # OP#8 definitive (Planck 2018 fiducial q0=-0.5275)
ombh2 = 0.02237
sigma8_planck = 0.811

# ============================================================
# BAO Data — Lee 2025 DR2 (DESI)
# ============================================================
bgs = {'z_eff': 0.295, 'DV_rd': 7.93}
cov_inv_bgs = 1.0 / 0.005625  # 1/sigma^2

tracers = [
    {'z_eff': 0.510, 'DM_rd': 13.62, 'DH_rd': 22.33},
    {'z_eff': 0.706, 'DM_rd': 17.86, 'DH_rd': 20.08},
    {'z_eff': 0.934, 'DM_rd': 21.71, 'DH_rd': 17.88},
    {'z_eff': 1.321, 'DM_rd': 27.79, 'DH_rd': 13.82},
    {'z_eff': 1.484, 'DM_rd': 29.34, 'DH_rd': 13.12},
    {'z_eff': 2.330, 'DM_rd': 39.71, 'DH_rd':  8.52},
]

# Lee 2025 2x2 covariance blocks (DM/rd, DH/rd basis)
cov_blocks = [
    np.array([[2.788900e-2, -3.257752e-2], [-3.257752e-2, 1.806250e-1]]),
    np.array([[3.132900e-2, -2.359764e-2], [-2.359764e-2, 1.089000e-1]]),
    np.array([[2.310400e-2, -1.220377e-2], [-1.220377e-2, 3.724900e-2]]),
    np.array([[1.01124e-1, -3.050065e-2], [-3.050065e-2, 4.8841e-2]]),
    np.array([[5.7760e-1, -1.9608e-1], [-1.9608e-1, 2.66256e-1]]),
    np.array([[2.81961e-1, -2.311496e-2], [-2.311496e-2, 1.0201e-2]]),
]
cov_inv_blocks = [np.linalg.inv(c) for c in cov_blocks]

# ============================================================
# fsigma8 data
# ============================================================
fsigma8_data = [
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

# ============================================================
# HK constraint
# ============================================================
beta_HK_obs = -0.037
beta_HK_sigma = 0.0095

# ============================================================
# Planck H0 prior
# ============================================================
H0_prior_mean = 67.36
H0_prior_sigma = 0.54

# ============================================================
# Pre-compute r_d grid using CAMB (runs once at startup)
# r_d depends on (omega_b, omega_cdm), with omega_b fixed.
# So r_d = r_d(omega_m) where omega_m = Omega_m * h^2.
# ============================================================
def build_rd_interpolator():
    """Build 1D interpolator for r_d(omega_m). Uses CAMB."""
    import camb
    omega_m_grid = np.linspace(0.10, 0.22, 50)
    rd_vals = []
    for om in omega_m_grid:
        omch2 = om - ombh2
        if omch2 < 0.01:
            rd_vals.append(np.nan)
            continue
        pars = camb.CAMBparams()
        pars.set_cosmology(H0=67.36, ombh2=ombh2, omch2=omch2, tau=0.054,
                           mnu=0.06, nnu=3.046)
        pars.set_dark_energy(w=-1, wa=0, dark_energy_model='fluid')
        pars.InitPower.set_params(As=2.1e-9, ns=0.9649)
        pars.set_matter_power(redshifts=[0], kmax=0.5)
        try:
            results = camb.get_results(pars)
            rd_vals.append(results.get_derived_params()['rdrag'])
        except:
            rd_vals.append(np.nan)

    mask = ~np.isnan(rd_vals)
    return interp1d(omega_m_grid[mask], np.array(rd_vals)[mask],
                    kind='cubic', fill_value='extrapolate')

# ============================================================
# Analytical Friedmann solver for BAO distances
# ============================================================
def E_squared(z, Omega_m, w0):
    """E^2(z) = H(z)^2 / H0^2 for flat wCDM."""
    Omega_DE = 1.0 - Omega_m
    return Omega_m * (1+z)**3 + Omega_DE * (1+z)**(3*(1+w0))

def comoving_distance(z, H0, Omega_m, w0):
    """Comoving radial distance in Mpc (c/H0 * integral)."""
    def integrand(zp):
        return 1.0 / np.sqrt(E_squared(zp, Omega_m, w0))
    result, _ = quad(integrand, 0, z)
    return c_km_s / H0 * result

def H_of_z(z, H0, Omega_m, w0):
    """H(z) in km/s/Mpc."""
    return H0 * np.sqrt(E_squared(z, Omega_m, w0))

# ============================================================
# Growth function: sigma8(z) using linear growth factor
# ============================================================
def growth_factor_ratio(z, Omega_m, w0):
    """D(z)/D(0) via integral approximation for wCDM."""
    def integrand(a):
        zp = 1.0/a - 1.0
        E2 = E_squared(zp, Omega_m, w0)
        return 1.0 / (a * E2)**1.5

    a = 1.0 / (1.0 + z)
    D_z, _ = quad(integrand, 1e-6, a)
    D_0, _ = quad(integrand, 1e-6, 1.0)

    E_z = np.sqrt(E_squared(z, Omega_m, w0))
    E_0 = np.sqrt(E_squared(0, Omega_m, w0))

    return (E_z / E_0) * (D_z / D_0) * ((1+z)**(-1))

def sigma8_at_z(z, Omega_m, w0, sigma8_0=sigma8_planck):
    """sigma8(z) using growth factor."""
    if z < 0.001:
        return sigma8_0
    # Use growth factor D(z)
    # Approximate: sigma8(z) ≈ sigma8(0) * D(z)/D(0)
    # where D(z) is computed from the integral form
    D_ratio = growth_factor_ratio(z, Omega_m, w0)
    return sigma8_0 * D_ratio

# ============================================================
# Chi-squared components
# ============================================================
def chi2_bao(H0, Omega_m, w0, rd):
    """BAO chi2 using analytical distances."""
    chi2 = 0.0

    # BGS: DV/rd
    z = bgs['z_eff']
    DM = comoving_distance(z, H0, Omega_m, w0)
    DH = c_km_s / H_of_z(z, H0, Omega_m, w0)
    DV = (z * DM**2 * DH)**(1./3.) / rd
    chi2 += (DV - bgs['DV_rd'])**2 * cov_inv_bgs

    # Anisotropic tracers
    for i, tr in enumerate(tracers):
        z = tr['z_eff']
        DM_pred = comoving_distance(z, H0, Omega_m, w0) / rd
        DH_pred = c_km_s / (H_of_z(z, H0, Omega_m, w0) * rd)
        delta = np.array([DM_pred - tr['DM_rd'], DH_pred - tr['DH_rd']])
        chi2 += delta @ cov_inv_blocks[i] @ delta

    return chi2

def chi2_fsigma8(H0, Omega_m, w0):
    """fsigma8 chi2 using growth index approximation."""
    gamma = 0.55 + 0.05 * (1 + w0)
    chi2 = 0.0
    for z_eff, fsig8_obs, sigma in fsigma8_data:
        E2 = E_squared(z_eff, Omega_m, w0)
        Omega_m_z = Omega_m * (1 + z_eff)**3 / E2
        f_z = Omega_m_z**gamma
        # sigma8(z) from scaling with D(z)
        s8_z = sigma8_planck * growth_factor_ratio(z_eff, Omega_m, w0) if z_eff > 0.01 else sigma8_planck
        fsig8_pred = f_z * s8_z
        chi2 += ((fsig8_pred - fsig8_obs) / sigma)**2
    return chi2

def chi2_H0_prior(H0):
    """Planck H0 Gaussian prior."""
    return ((H0 - H0_prior_mean) / H0_prior_sigma)**2

def chi2_HK(zeta0):
    """Hiramatsu-Kobayashi beta_HK constraint."""
    beta_pred = -zeta0 / (1 + zeta0)
    return ((beta_pred - beta_HK_obs) / beta_HK_sigma)**2

# ============================================================
# Total log-likelihood
# ============================================================
rd_interp = None  # Will be initialized in main

def log_likelihood(theta):
    """Log-likelihood for (w0, H0, Omega_m)."""
    w0, H0, Om = theta

    # Parameter bounds
    if w0 <= -1.0 or w0 >= -0.5:
        return -np.inf
    if H0 < 55 or H0 > 80:
        return -np.inf
    if Om < 0.15 or Om > 0.50:
        return -np.inf

    omega_m = Om * (H0/100)**2
    omch2 = omega_m - ombh2
    if omch2 < 0.01 or omch2 > 0.20:
        return -np.inf

    # r_d from interpolation
    rd = rd_interp(omega_m)

    # zeta0 from w0
    if (1 + w0) < 1e-10:
        return -np.inf
    zeta0 = C_KK / (1 + w0)

    try:
        c2_bao = chi2_bao(H0, Om, w0, rd)
        c2_fs8 = chi2_fsigma8(H0, Om, w0)
        c2_h0 = chi2_H0_prior(H0)
        c2_hk = chi2_HK(zeta0)
    except:
        return -np.inf

    return -0.5 * (c2_bao + c2_fs8 + c2_h0 + c2_hk)

def log_prior(theta):
    """Flat priors on w0, H0, Omega_m."""
    w0, H0, Om = theta
    if -0.9999 < w0 < -0.5 and 55 < H0 < 80 and 0.15 < Om < 0.50:
        return 0.0
    return -np.inf

def log_probability(theta):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    ll = log_likelihood(theta)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll

# ============================================================
# Alternative priors for sensitivity test
# ============================================================
def log_prior_logflat_zeta(theta):
    """Log-flat prior on zeta0 (uniform in log(zeta0))."""
    w0, H0, Om = theta
    if not (-0.9999 < w0 < -0.5 and 55 < H0 < 80 and 0.15 < Om < 0.50):
        return -np.inf
    zeta0 = C_KK / (1 + w0) if (1+w0) > 1e-10 else np.inf
    if zeta0 <= 0 or zeta0 > 1.0:
        return -np.inf
    # p(zeta0) ~ 1/zeta0 => log p = -log(zeta0) + Jacobian
    # Jacobian: d(zeta0)/d(w0) = -C_KK/(1+w0)^2
    return -np.log(zeta0) + np.log(C_KK) - 2*np.log(1+w0)

def log_prior_gaussian_zeta(theta):
    """Gaussian prior centered at zeta0=0 (LCDM-favoring)."""
    w0, H0, Om = theta
    if not (-0.9999 < w0 < -0.5 and 55 < H0 < 80 and 0.15 < Om < 0.50):
        return -np.inf
    zeta0 = C_KK / (1 + w0) if (1+w0) > 1e-10 else np.inf
    sigma_prior = 0.05
    # Gaussian on zeta0 centered at 0 + Jacobian
    return -0.5*(zeta0/sigma_prior)**2 + np.log(C_KK) - 2*np.log(1+w0)

# ============================================================
# Main MCMC
# ============================================================
def run_mcmc(prior_name='flat', nwalkers=32, nsteps=4000, nburn=1000):
    """Run MCMC and return chain."""

    if prior_name == 'flat':
        prob_fn = log_probability
    elif prior_name == 'logflat':
        def prob_fn(theta):
            lp = log_prior_logflat_zeta(theta)
            if not np.isfinite(lp):
                return -np.inf
            ll = log_likelihood(theta)
            return lp + ll
    elif prior_name == 'gaussian':
        def prob_fn(theta):
            lp = log_prior_gaussian_zeta(theta)
            if not np.isfinite(lp):
                return -np.inf
            ll = log_likelihood(theta)
            return lp + ll

    ndim = 3
    # Initial positions near best-fit
    p0 = np.array([-0.993, 67.36, 0.315])
    pos = p0 + 1e-3 * np.random.randn(nwalkers, ndim)
    # Ensure all within bounds
    pos[:, 0] = np.clip(pos[:, 0], -0.999, -0.501)
    pos[:, 1] = np.clip(pos[:, 1], 55.1, 79.9)
    pos[:, 2] = np.clip(pos[:, 2], 0.151, 0.499)

    sampler = emcee.EnsembleSampler(nwalkers, ndim, prob_fn)

    print(f"Running MCMC ({prior_name} prior): {nwalkers} walkers, {nsteps} steps...")
    t0 = time.time()
    sampler.run_mcmc(pos, nsteps, progress=True)
    t1 = time.time()
    print(f"Done in {t1-t0:.1f} sec")

    # Discard burn-in and thin
    chain = sampler.get_chain(discard=nburn, flat=True)  # shape: (n_samples, 3)
    log_prob = sampler.get_log_prob(discard=nburn, flat=True)

    return chain, log_prob, sampler

def analyze_chain(chain, prior_range=(0, 0.20)):
    """Analyze MCMC chain: posterior summary + Savage-Dickey Bayes factor."""
    w0_chain = chain[:, 0]
    H0_chain = chain[:, 1]
    Om_chain = chain[:, 2]
    zeta0_chain = C_KK / (1 + w0_chain)

    # Posterior summary
    results = {}
    for name, arr in [('w0', w0_chain), ('H0', H0_chain), ('Omega_m', Om_chain), ('zeta0', zeta0_chain)]:
        results[name] = {
            'mean': float(np.mean(arr)),
            'std': float(np.std(arr)),
            'median': float(np.median(arr)),
            'q16': float(np.percentile(arr, 16)),
            'q84': float(np.percentile(arr, 84)),
            'q2.5': float(np.percentile(arr, 2.5)),
            'q97.5': float(np.percentile(arr, 97.5)),
        }

    # Savage-Dickey Bayes factor: B10 = pi(zeta0=0) / p(zeta0=0|data)
    # Estimate p(zeta0=0|data) from KDE or histogram
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(zeta0_chain)
    p_0 = float(kde(0.0)[0])

    z_min, z_max = prior_range
    pi_0 = 1.0 / (z_max - z_min) if z_max > z_min else 1.0

    B10 = pi_0 / p_0 if p_0 > 0 else np.inf

    results['savage_dickey'] = {
        'prior_range': list(prior_range),
        'pi_0': float(pi_0),
        'p_0': float(p_0),
        'B10': float(B10),
        'log10_B10': float(np.log10(B10)) if B10 > 0 and np.isfinite(B10) else None,
    }

    return results

# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("Meridian MCMC — Multi-probe posterior on zeta0")
    print("=" * 60)

    # Build r_d interpolator
    print("Pre-computing r_d(omega_m) grid with CAMB...")
    t0 = time.time()
    rd_interp = build_rd_interpolator()
    print(f"  r_d grid done in {time.time()-t0:.1f} sec")

    # Validate: r_d at fiducial
    omega_m_fid = 0.315 * (67.36/100)**2
    print(f"  r_d(fid) = {rd_interp(omega_m_fid):.2f} Mpc")

    # Run 3 prior choices
    all_results = {}

    for prior_name in ['flat', 'logflat', 'gaussian']:
        print(f"\n{'='*40}")
        print(f"Prior: {prior_name}")
        print(f"{'='*40}")
        chain, log_prob, sampler = run_mcmc(prior_name=prior_name, nwalkers=32,
                                             nsteps=4000, nburn=1000)

        results = analyze_chain(chain)
        all_results[prior_name] = results

        print(f"\nPosterior summary:")
        for param in ['w0', 'H0', 'Omega_m', 'zeta0']:
            r = results[param]
            print(f"  {param}: {r['mean']:.5f} +/- {r['std']:.5f}  "
                  f"[{r['q16']:.5f}, {r['q84']:.5f}]")

        sd = results['savage_dickey']
        print(f"\nSavage-Dickey B10 = {sd['B10']:.1f}:1")
        if sd['log10_B10'] is not None:
            print(f"  log10(B10) = {sd['log10_B10']:.2f}")

    # Save results
    outfile = 'mcmc_meridian_results.json'
    with open(outfile, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {outfile}")

    # Print prior sensitivity comparison
    print("\n" + "=" * 60)
    print("PRIOR SENSITIVITY COMPARISON")
    print("=" * 60)
    print(f"{'Prior':<12} {'zeta0 mean':>12} {'zeta0 std':>12} {'B10':>12}")
    for pname in ['flat', 'logflat', 'gaussian']:
        r = all_results[pname]
        z = r['zeta0']
        sd = r['savage_dickey']
        print(f"{pname:<12} {z['mean']:>12.5f} {z['std']:>12.5f} {sd['B10']:>12.1f}")
