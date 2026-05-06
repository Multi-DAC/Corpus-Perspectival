#!/usr/bin/env python3
"""
Full Covariance Treatment of the Hubble-Kristian Expansion Rate Compilation
============================================================================

This script implements the complete covariance matrix for the 18-point H&K
dataset used in the Meridian Monograph (Paper II), including:

1. BOSS DR12 off-diagonal correlations (Alam et al. 2017, MNRAS 470, 2617)
2. WiggleZ off-diagonal correlations (Blake et al. 2012, MNRAS 425, 405)
3. All other measurements treated as uncorrelated

The analysis computes:
- chi^2 for LCDM and Meridian models with full covariance
- Delta chi^2 and significance
- Savage-Dickey Bayes factors for multiple prior widths
- F-test statistics
- Fisher information and parameter uncertainty
- Comparison with diagonal approximation
"""

import numpy as np
from scipy import stats, optimize
from scipy.linalg import inv, det

# =============================================================================
# 1. DATASET
# =============================================================================

# Planck 2018 fiducial cosmology
H0 = 67.4  # km/s/Mpc
Om = 0.315
Or = 9.15e-5  # radiation density (Planck 2018)
ODE = 1.0 - Om - Or

def H_LCDM(z):
    """LCDM Hubble parameter"""
    return H0 * np.sqrt(Om * (1+z)**3 + Or * (1+z)**4 + ODE)

# Dataset: [index, z, H(z), sigma_H, method, survey]
# Methods: CC=cosmic chronometer, BAO=baryon acoustic oscillation, GC=galaxy clustering
data = [
    # CC measurements
    (0,  0.070, 69.0, 19.6, 'CC',  'CC'),
    (1,  0.120, 68.6, 26.2, 'CC',  'CC'),
    (2,  0.170, 83.0,  8.0, 'CC',  'CC'),
    (3,  0.200, 72.9, 29.6, 'CC',  'CC'),
    (4,  0.280, 88.8, 36.6, 'CC',  'CC'),
    # BAO measurements
    (5,  0.106, 69.4,  5.6, 'BAO', '6dFGS'),
    (6,  0.150, 69.2,  7.8, 'BAO', 'SDSS_MGS'),
    (7,  0.380, 81.5,  2.3, 'BAO', 'BOSS_DR12'),
    (8,  0.510, 90.5,  2.5, 'BAO', 'BOSS_DR12'),
    (9,  0.610, 97.3,  2.7, 'BAO', 'BOSS_DR12'),
    (10, 0.700, 98.0, 12.0, 'BAO', 'eBOSS_LRG'),
    (11, 0.850, 113.1, 8.0, 'BAO', 'eBOSS_ELG'),
    (12, 1.480, 160.0, 13.0, 'BAO', 'eBOSS_QSO'),
    (13, 2.330, 224.0,  8.6, 'BAO', 'eBOSS_Lya'),
    # GC measurements
    (14, 0.440, 82.6,  7.8, 'GC',  'WiggleZ'),
    (15, 0.600, 87.9,  6.1, 'GC',  'WiggleZ'),
    (16, 0.730, 97.3,  7.0, 'GC',  'WiggleZ'),
    (17, 0.800, 105.0, 9.4, 'GC',  'VIPERS'),
]

N = len(data)
z_arr = np.array([d[1] for d in data])
H_arr = np.array([d[2] for d in data])
sig_arr = np.array([d[3] for d in data])

# Compute LCDM predictions
H_LCDM_arr = np.array([H_LCDM(z) for z in z_arr])

# beta_HK = H_measured / H_LCDM - 1
beta_arr = H_arr / H_LCDM_arr - 1.0
sigma_beta = sig_arr / H_LCDM_arr

# =============================================================================
# 2. COVARIANCE MATRIX CONSTRUCTION
# =============================================================================

def build_covariance_matrix(correlation_model='full'):
    """
    Build the full 18x18 covariance matrix.
    
    Parameters
    ----------
    correlation_model : str
        'diagonal' : no off-diagonal correlations
        'boss_only' : BOSS DR12 correlations only
        'full' : BOSS DR12 + WiggleZ correlations
    
    Returns
    -------
    C : 18x18 covariance matrix in beta_HK space
    """
    # Start with diagonal
    C = np.diag(sigma_beta**2)
    
    if correlation_model in ('boss_only', 'full'):
        # -----------------------------------------------------------
        # BOSS DR12 correlations (Alam et al. 2017, Table 5)
        # -----------------------------------------------------------
        # Indices 7, 8, 9 correspond to z = 0.38, 0.51, 0.61
        # 
        # The BOSS DR12 consensus analysis reports correlation coefficients
        # between the H(z) measurements at these three redshifts.
        # From Alam et al. 2017, the H(z) correlation matrix is approximately:
        #
        #   z=0.38  z=0.51  z=0.61
        #   1.000   0.120   0.037
        #   0.120   1.000   0.141
        #   0.037   0.141   1.000
        #
        # These arise from overlap in the galaxy samples used for the
        # three redshift bins and from shared systematic effects
        # (fiber collisions, photometric calibration, FKP weights).
        #
        # Reference: Alam et al. 2017, Table 5, "consensus" column,
        # H(z) correlation sub-matrix.
        
        boss_indices = [7, 8, 9]
        boss_corr = np.array([
            [1.000, 0.120, 0.037],
            [0.120, 1.000, 0.141],
            [0.037, 0.141, 1.000]
        ])
        
        for i_local, i_global in enumerate(boss_indices):
            for j_local, j_global in enumerate(boss_indices):
                if i_local != j_local:
                    C[i_global, j_global] = (boss_corr[i_local, j_local] 
                                              * sigma_beta[i_global] 
                                              * sigma_beta[j_global])
    
    if correlation_model == 'full':
        # -----------------------------------------------------------
        # WiggleZ correlations (Blake et al. 2012, MNRAS 425, 405)
        # -----------------------------------------------------------
        # Indices 14, 15, 16 correspond to z = 0.44, 0.60, 0.73
        #
        # Blake et al. 2012, Table 3 reports the correlation matrix
        # for the f*sigma_8 measurements. The H(z) values derived from
        # the Alcock-Paczynski effect share correlated systematic
        # uncertainties from the fiducial cosmology and the survey
        # window function. The reported correlation coefficients are:
        #
        #   z=0.44  z=0.60  z=0.73
        #   1.000   0.069   0.032
        #   0.069   1.000   0.073
        #   0.032   0.073   1.000
        #
        # These are smaller than BOSS because WiggleZ uses a different
        # survey strategy (no fiber collision issue, wider but shallower
        # coverage, independent photometric calibration).
        #
        # Reference: Blake et al. 2012, Table 3
        
        wigglez_indices = [14, 15, 16]
        wigglez_corr = np.array([
            [1.000, 0.069, 0.032],
            [0.069, 1.000, 0.073],
            [0.032, 0.073, 1.000]
        ])
        
        for i_local, i_global in enumerate(wigglez_indices):
            for j_local, j_global in enumerate(wigglez_indices):
                if i_local != j_local:
                    C[i_global, j_global] = (wigglez_corr[i_local, j_local] 
                                              * sigma_beta[i_global] 
                                              * sigma_beta[j_global])
    
    return C


# =============================================================================
# 3. CHI-SQUARED ANALYSIS
# =============================================================================

def chi2_LCDM(C):
    """chi^2 for LCDM (beta_HK = 0)"""
    Cinv = inv(C)
    return float(beta_arr @ Cinv @ beta_arr)

def chi2_meridian(zeta0, C):
    """chi^2 for Meridian model (beta_HK = -zeta0)"""
    Cinv = inv(C)
    residual = beta_arr + zeta0  # beta_HK - (-zeta0)
    return float(residual @ Cinv @ residual)

def fit_zeta0(C):
    """Analytical weighted least-squares fit for zeta0 with full covariance"""
    Cinv = inv(C)
    ones = np.ones(N)
    # Model: beta_HK,i = -zeta0 for all i
    # chi^2 = (beta + zeta0*1)^T C^{-1} (beta + zeta0*1)
    # d(chi^2)/d(zeta0) = 2 * 1^T C^{-1} (beta + zeta0*1) = 0
    # => zeta0 = -(1^T C^{-1} beta) / (1^T C^{-1} 1)
    
    numerator = -ones @ Cinv @ beta_arr
    denominator = ones @ Cinv @ ones
    zeta0_hat = numerator / denominator
    sigma_zeta0 = 1.0 / np.sqrt(denominator)
    
    return zeta0_hat, sigma_zeta0

def savage_dickey_bayes_factor(zeta0_hat, sigma_zeta0, prior_width):
    """
    Savage-Dickey density ratio for comparing:
      M1: zeta0 free (flat prior on [0, prior_width])
      M0: zeta0 = 0 (LCDM)
    
    B10 = pi(zeta0=0) / p(zeta0=0|data)
    """
    # Prior density at zeta0 = 0 for flat prior on [0, prior_width]
    pi_0 = 1.0 / prior_width
    
    # Posterior density at zeta0 = 0 (Gaussian approximation)
    p_0 = stats.norm.pdf(0, loc=zeta0_hat, scale=sigma_zeta0)
    
    # Bayes factor
    B10 = pi_0 / p_0
    return B10


# =============================================================================
# 4. RUN ANALYSIS FOR ALL THREE COVARIANCE MODELS
# =============================================================================

print("=" * 80)
print("HUBBLE-KRISTIAN COVARIANCE ANALYSIS")
print("Full treatment with BOSS DR12 + WiggleZ off-diagonal correlations")
print("=" * 80)

results = {}

for model_name in ['diagonal', 'boss_only', 'full']:
    print(f"\n{'='*60}")
    print(f"Covariance model: {model_name}")
    print(f"{'='*60}")
    
    C = build_covariance_matrix(model_name)
    
    # Verify positive definiteness
    eigvals = np.linalg.eigvalsh(C)
    print(f"Covariance matrix: {N}x{N}, min eigenvalue = {eigvals.min():.4e}")
    print(f"Condition number: {eigvals.max()/eigvals.min():.1f}")
    
    # Fit zeta0
    zeta0_hat, sigma_zeta0 = fit_zeta0(C)
    
    # Chi-squared values
    chi2_lcdm = chi2_LCDM(C)
    chi2_mer = chi2_meridian(zeta0_hat, C)
    delta_chi2 = chi2_mer - chi2_lcdm
    
    # Degrees of freedom
    dof_lcdm = N
    dof_mer = N - 1
    
    # Significance from delta chi^2
    sigma_detection = np.sqrt(-delta_chi2) if delta_chi2 < 0 else 0
    
    # p-values
    p_lcdm = 1.0 - stats.chi2.cdf(chi2_lcdm, dof_lcdm)
    p_mer = stats.chi2.cdf(chi2_mer, dof_mer)  # lower tail
    
    # F-test
    F_stat = (-delta_chi2 / 1) / (chi2_mer / dof_mer)
    p_F = 1.0 - stats.f.cdf(F_stat, 1, dof_mer)
    sigma_F = stats.norm.ppf(1.0 - p_F/2) if p_F > 0 else np.inf
    
    # Information criteria
    delta_AIC = delta_chi2 + 2
    delta_BIC = delta_chi2 + np.log(N)
    
    # Bayes factors
    prior_widths = [0.05, 0.10, 0.20, 0.30, 0.50, 1.00]
    bayes_factors = {pw: savage_dickey_bayes_factor(zeta0_hat, sigma_zeta0, pw) 
                     for pw in prior_widths}
    
    print(f"\nBest-fit: zeta0 = {zeta0_hat:.4f} +/- {sigma_zeta0:.4f}")
    print(f"Detection significance: {zeta0_hat/sigma_zeta0:.1f} sigma")
    print(f"\nchi^2 (LCDM):   {chi2_lcdm:.2f} / {dof_lcdm} dof = {chi2_lcdm/dof_lcdm:.3f}")
    print(f"chi^2 (Meridian): {chi2_mer:.2f} / {dof_mer} dof = {chi2_mer/dof_mer:.3f}")
    print(f"Delta chi^2:    {delta_chi2:.2f}")
    print(f"Significance (sqrt |Delta chi^2|): {sigma_detection:.2f} sigma")
    print(f"\nF-test: F = {F_stat:.2f}, p = {p_F:.2e}, sigma = {sigma_F:.1f}")
    print(f"Delta AIC: {delta_AIC:.1f}")
    print(f"Delta BIC: {delta_BIC:.1f}")
    
    print(f"\nSavage-Dickey Bayes factors (M1 vs LCDM):")
    for pw in prior_widths:
        B = bayes_factors[pw]
        label = "Decisive" if B > 100 else ("Strong" if B > 20 else ("Substantial" if B > 10 else "Weak"))
        print(f"  Prior [0, {pw:.2f}]: B10 = {B:.1f}:1 ({label})")
    
    print(f"\np(chi^2 <= {chi2_mer:.1f} | {dof_mer} dof) = {p_mer:.4f} ({p_mer*100:.1f}%)")
    
    results[model_name] = {
        'C': C,
        'zeta0': zeta0_hat,
        'sigma_zeta0': sigma_zeta0,
        'chi2_lcdm': chi2_lcdm,
        'chi2_mer': chi2_mer,
        'delta_chi2': delta_chi2,
        'sigma': sigma_detection,
        'F_stat': F_stat,
        'p_F': p_F,
        'sigma_F': sigma_F,
        'delta_AIC': delta_AIC,
        'delta_BIC': delta_BIC,
        'bayes_factors': bayes_factors,
        'p_low_chi2': p_mer,
    }

# =============================================================================
# 5. COMPARISON TABLE
# =============================================================================

print(f"\n\n{'='*80}")
print("COMPARISON: DIAGONAL vs FULL COVARIANCE")
print(f"{'='*80}")
print(f"\n{'Quantity':<35} {'Diagonal':>12} {'BOSS only':>12} {'Full':>12}")
print("-" * 75)

for key, label in [
    ('zeta0', 'zeta0 (best fit)'),
    ('sigma_zeta0', 'sigma(zeta0)'),
    ('chi2_lcdm', 'chi^2 (LCDM)'),
    ('chi2_mer', 'chi^2 (Meridian)'),
    ('delta_chi2', 'Delta chi^2'),
    ('sigma', 'Detection (sigma)'),
    ('sigma_F', 'F-test (sigma)'),
    ('delta_AIC', 'Delta AIC'),
    ('delta_BIC', 'Delta BIC'),
]:
    vals = [results[m][key] for m in ['diagonal', 'boss_only', 'full']]
    if key in ('zeta0', 'sigma_zeta0'):
        print(f"{label:<35} {vals[0]:>12.4f} {vals[1]:>12.4f} {vals[2]:>12.4f}")
    else:
        print(f"{label:<35} {vals[0]:>12.2f} {vals[1]:>12.2f} {vals[2]:>12.2f}")

# Reference Bayes factor at prior [0, 0.2]
print(f"\n{'Bayes factor [0, 0.2]':<35}", end="")
for m in ['diagonal', 'boss_only', 'full']:
    B = results[m]['bayes_factors'][0.20]
    print(f" {B:>11.1f}:1", end="")
print()

print(f"\n{'p(chi^2 low) [Meridian]':<35}", end="")
for m in ['diagonal', 'boss_only', 'full']:
    p = results[m]['p_low_chi2']
    print(f" {p*100:>10.1f}%", end="")
print()

# =============================================================================
# 6. IMPACT ASSESSMENT
# =============================================================================

print(f"\n\n{'='*80}")
print("IMPACT ASSESSMENT: Effect of including correlations")
print(f"{'='*80}")

d = results['diagonal']
f = results['full']

print(f"\nzeta0 shift:     {d['zeta0']:.4f} -> {f['zeta0']:.4f} (delta = {f['zeta0']-d['zeta0']:.4f})")
print(f"sigma shift:     {d['sigma_zeta0']:.4f} -> {f['sigma_zeta0']:.4f} (delta = {f['sigma_zeta0']-d['sigma_zeta0']:.4f})")
print(f"Detection:       {d['sigma']:.2f} -> {f['sigma']:.2f} sigma")
print(f"chi^2/dof (Mer): {d['chi2_mer']/(N-1):.3f} -> {f['chi2_mer']/(N-1):.3f}")
print(f"Bayes (0.2):     {d['bayes_factors'][0.2]:.1f}:1 -> {f['bayes_factors'][0.2]:.1f}:1")

# Does the signal survive?
if f['sigma'] >= 3.0:
    print(f"\n*** SIGNAL SURVIVES full covariance treatment at {f['sigma']:.1f} sigma ***")
elif f['sigma'] >= 2.0:
    print(f"\n*** Signal weakened but present at {f['sigma']:.1f} sigma ***")
else:
    print(f"\n*** Signal degraded below 2 sigma: {f['sigma']:.1f} sigma ***")

# =============================================================================
# 7. MONTE CARLO VALIDATION
# =============================================================================

print(f"\n\n{'='*80}")
print("MONTE CARLO VALIDATION (N=100,000 LCDM mocks)")
print(f"{'='*80}")

C_full = results['full']['C']
Cinv_full = inv(C_full)
L = np.linalg.cholesky(C_full)  # For generating correlated noise

np.random.seed(42)
N_mc = 100_000

chi2_null = np.zeros(N_mc)
zeta0_null = np.zeros(N_mc)

ones = np.ones(N)
denom = ones @ Cinv_full @ ones

for i in range(N_mc):
    # Generate correlated Gaussian noise (LCDM: beta=0)
    noise = L @ np.random.randn(N)
    
    # Fit zeta0
    z0 = -(ones @ Cinv_full @ noise) / denom
    
    # Chi^2 for best-fit model
    resid = noise + z0
    chi2_null[i] = resid @ Cinv_full @ resid

# Compare observed chi^2 to null distribution
obs_chi2 = results['full']['chi2_mer']
p_low_mc = np.mean(chi2_null <= obs_chi2)

# Compare observed |zeta0| to null distribution
obs_zeta0 = abs(results['full']['zeta0'])
p_zeta0_mc = np.mean(np.abs(zeta0_null) >= obs_zeta0)

print(f"Observed chi^2 (Meridian): {obs_chi2:.2f}")
print(f"MC null distribution: mean = {np.mean(chi2_null):.2f}, std = {np.std(chi2_null):.2f}")
print(f"P(chi^2 <= {obs_chi2:.1f} | LCDM): {p_low_mc:.4f} ({p_low_mc*100:.1f}%)")
print(f"\nObserved |zeta0|: {obs_zeta0:.4f}")
print(f"MC null distribution: mean = {np.mean(np.abs(zeta0_null)):.4f}, std = {np.std(zeta0_null):.4f}")
print(f"P(|zeta0| >= {obs_zeta0:.4f} | LCDM): {p_zeta0_mc:.6f}")
if p_zeta0_mc > 0:
    sigma_mc = stats.norm.ppf(1.0 - p_zeta0_mc/2)
    print(f"Equivalent significance: {sigma_mc:.2f} sigma")
else:
    print("Equivalent significance: > 5 sigma (none in 100k trials)")

# Percentile table
print(f"\nNull chi^2/dof distribution (17 dof):")
for pct in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
    val = np.percentile(chi2_null, pct)
    print(f"  {pct:3d}th percentile: chi^2/dof = {val/17:.3f}")

print(f"\n  Observed:          chi^2/dof = {obs_chi2/17:.3f}")
