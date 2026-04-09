"""
Proper Pantheon+ likelihood with full stat+sys covariance.

Replaces the diagonal-only approximation from 18A_proper_mcmc.py.
Uses the exact method from Cobaya (Brout et al. 2022):
  - Full 1701x1701 covariance matrix
  - Analytic marginalization over absolute magnitude M
  - Proper redshift handling (zHD for CMB frame, zHEL for heliocentric)
  - z > 0.01 cut (Pantheon+ only, no SH0ES calibrators)

References:
  - Scolnic et al. 2022, ApJ 938 113 (data release)
  - Brout et al. 2022, ApJ 938 110 (cosmological constraints, Eq. 8-15)
  - github.com/PantheonPlusSH0ES/DataRelease

Data: phase18/data/pantheonplus/
  - Pantheon+SH0ES.dat (1701 SNe)
  - Pantheon+SH0ES_STAT+SYS.cov (1701x1701 covariance)

WARNING from the Pantheon+ team:
  "DO NOT FIT COSMOLOGICAL PARAMETERS WITH [DIAGONAL] UNCERTAINTIES.
   YOU MUST USE THE FULL COVARIANCE."
"""

import os
import numpy as np

# ==============================================================
# DATA LOADING
# ==============================================================

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'data', 'pantheonplus')

def load_pantheonplus(z_min=0.01, verbose=True):
    """Load Pantheon+ data with full covariance.

    Args:
        z_min: minimum CMB-frame redshift cut (0.01 for Pantheon+ only)
        verbose: print diagnostics

    Returns:
        dict with keys:
            m_obs: corrected apparent magnitudes (N_cut,)
            z_cmb: CMB-frame redshifts (N_cut,)
            z_hel: heliocentric redshifts (N_cut,)
            C_inv_marg: M-marginalized inverse covariance (N_cut, N_cut)
            N: number of SNe after cut
    """
    dat_file = os.path.join(DATA_DIR, 'Pantheon+SH0ES.dat')
    cov_file = os.path.join(DATA_DIR, 'Pantheon+SH0ES_STAT+SYS.cov')

    if not os.path.exists(dat_file):
        raise FileNotFoundError(
            f"Pantheon+ data not found at {dat_file}. "
            f"Download from github.com/PantheonPlusSH0ES/DataRelease"
        )

    # Load SNe data
    # Header is space-separated, first line is column names
    with open(dat_file, 'r') as f:
        header = f.readline().strip().split()

    data = np.genfromtxt(dat_file, names=True, dtype=None, encoding='utf-8')

    z_cmb_all = np.array([float(row['zHD']) for row in data])
    z_hel_all = np.array([float(row['zHEL']) for row in data])
    m_obs_all = np.array([float(row['m_b_corr']) for row in data])

    N_total = len(z_cmb_all)
    if verbose:
        print(f"  Pantheon+: {N_total} SNe loaded")

    # Load covariance
    cov_raw = np.loadtxt(cov_file)
    N_cov = int(cov_raw[0])
    assert N_cov == N_total, f"Covariance dim {N_cov} != data rows {N_total}"
    C_full = cov_raw[1:].reshape(N_cov, N_cov)

    if verbose:
        print(f"  Covariance: {N_cov}x{N_cov}, loaded ({C_full.nbytes/1e6:.1f} MB)")

    # Apply redshift cut
    mask = z_cmb_all > z_min
    m_obs = m_obs_all[mask]
    z_cmb = z_cmb_all[mask]
    z_hel = z_hel_all[mask]
    C = C_full[np.ix_(mask, mask)]
    N_cut = mask.sum()

    if verbose:
        print(f"  After z > {z_min} cut: {N_cut} SNe")

    # Invert covariance
    try:
        C_inv = np.linalg.inv(C)
    except np.linalg.LinAlgError:
        # Add small regularization if singular
        C_reg = C + 1e-10 * np.eye(N_cut)
        C_inv = np.linalg.inv(C_reg)
        if verbose:
            print("  WARNING: covariance required regularization")

    # Analytic marginalization over absolute magnitude M
    # Using Woodbury identity / Schur complement:
    # C_inv_marg = C_inv - (C_inv @ 1)(1^T @ C_inv) / (1^T @ C_inv @ 1)
    ones = np.ones(N_cut)
    C_inv_ones = C_inv @ ones
    denom = ones @ C_inv_ones  # scalar: 1^T C^{-1} 1
    C_inv_marg = C_inv - np.outer(C_inv_ones, C_inv_ones) / denom

    if verbose:
        print(f"  M marginalized. C_inv_marg shape: {C_inv_marg.shape}")
        # Sanity check: marginalized matrix should have rank N-1
        # (one eigenvalue should be ~0)
        eig_min = np.min(np.abs(np.linalg.eigvalsh(C_inv_marg)))
        print(f"  Min eigenvalue of C_inv_marg: {eig_min:.2e} (should be ~0)")

    return {
        'm_obs': m_obs,
        'z_cmb': z_cmb,
        'z_hel': z_hel,
        'C_inv_marg': C_inv_marg,
        'N': N_cut
    }


# ==============================================================
# LIKELIHOOD
# ==============================================================

def log_like_pantheonplus(mu_theory, sne_data):
    """Compute Pantheon+ log-likelihood with full covariance.

    Args:
        mu_theory: distance moduli at the SNe redshifts (N,)
                   mu = 5*log10(d_L/Mpc) + 25
        sne_data: dict from load_pantheonplus()

    Returns:
        log-likelihood (float, negative)

    Note: M is analytically marginalized. You do NOT need to include
    M as a parameter in your MCMC.
    """
    # Delta = m_obs - mu_theory
    # With M marginalized, this is equivalent to profiling over M
    delta = sne_data['m_obs'] - mu_theory
    chi2 = delta @ sne_data['C_inv_marg'] @ delta
    return -0.5 * chi2


def distance_modulus(z_cmb, z_hel, Om, H0, w0, wa=0.0):
    """Compute distance modulus for flat wCDM/CPL.

    Uses numerical integration of E(z) = H(z)/H0.
    Proper treatment: d_L = (1+z_hel) * (1+z_cmb) * d_A(z_cmb)

    Args:
        z_cmb: CMB-frame redshifts
        z_hel: heliocentric redshifts
        Om: matter density
        H0: Hubble constant (km/s/Mpc)
        w0: DE equation of state at z=0
        wa: DE equation of state evolution (CPL)
    """
    from scipy.integrate import quad

    c_km_s = 299792.458  # km/s

    def E(z):
        a = 1.0 / (1.0 + z)
        Ode = 1.0 - Om
        # DE density: rho_DE/rho_DE0 = a^(-3(1+w0+wa)) * exp(-3*wa*(1-a))
        de_factor = a**(-3*(1+w0+wa)) * np.exp(-3*wa*(1-a))
        return np.sqrt(Om * (1+z)**3 + Ode * de_factor)

    mu = np.zeros_like(z_cmb)
    for i in range(len(z_cmb)):
        integral, _ = quad(lambda z: 1.0/E(z), 0, z_cmb[i])
        d_C = (c_km_s / H0) * integral  # comoving distance in Mpc
        # Luminosity distance with proper heliocentric correction
        d_L = (1 + z_hel[i]) * d_C  # flat universe: d_C = d_M
        mu[i] = 5 * np.log10(d_L) + 25

    return mu


# ==============================================================
# VALIDATION
# ==============================================================

def validate():
    """Run validation checks on the loaded data."""
    print("Loading Pantheon+ data...")
    sne = load_pantheonplus(verbose=True)

    print(f"\nData summary:")
    print(f"  N = {sne['N']}")
    print(f"  z range: [{sne['z_cmb'].min():.4f}, {sne['z_cmb'].max():.4f}]")
    print(f"  m_b range: [{sne['m_obs'].min():.2f}, {sne['m_obs'].max():.2f}]")

    # Compute chi2 at LCDM fiducial
    print("\nComputing chi2 at LCDM fiducial (Om=0.315, H0=67.4)...")
    mu_lcdm = distance_modulus(sne['z_cmb'], sne['z_hel'],
                                Om=0.315, H0=67.4, w0=-1.0)
    ll = log_like_pantheonplus(mu_lcdm, sne)
    chi2 = -2 * ll
    print(f"  chi2 = {chi2:.2f}")
    print(f"  chi2/N = {chi2/sne['N']:.3f}")
    print(f"  (expect chi2/N ~ 1.0 for good fit)")

    # Compare with diagonal
    diag_err = np.sqrt(np.diag(
        np.linalg.inv(sne['C_inv_marg'] +
                       np.outer(np.ones(sne['N']), np.ones(sne['N'])) * 1e-10)
    ))
    print(f"\n  Effective diagonal errors: [{diag_err.min():.4f}, {diag_err.max():.4f}]")

    return sne, chi2


if __name__ == '__main__':
    validate()
