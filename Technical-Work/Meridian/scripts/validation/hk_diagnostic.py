#!/usr/bin/env python3
"""
Diagnostic: Why does my calculation disagree with the monograph?

Monograph claims: chi^2(LCDM) = 24.6, chi^2(Meridian) = 9.6, zeta0 = 0.038
My calculation:   chi^2(LCDM) = 7.24, chi^2(Meridian) = 6.78, zeta0 = 0.009

This 3.4x discrepancy in chi^2(LCDM) cannot be a covariance effect.
Let me check the data point by point.
"""

import numpy as np

H0 = 67.4  # km/s/Mpc  (Planck 2018)
Om = 0.315
Or = 9.15e-5
ODE = 1.0 - Om - Or

def H_LCDM(z):
    return H0 * np.sqrt(Om * (1+z)**3 + Or * (1+z)**4 + ODE)

# Same dataset as before
data = [
    (0,  0.070, 69.0, 19.6),
    (1,  0.120, 68.6, 26.2),
    (2,  0.170, 83.0,  8.0),
    (3,  0.200, 72.9, 29.6),
    (4,  0.280, 88.8, 36.6),
    (5,  0.106, 69.4,  5.6),
    (6,  0.150, 69.2,  7.8),
    (7,  0.380, 81.5,  2.3),
    (8,  0.510, 90.5,  2.5),
    (9,  0.610, 97.3,  2.7),
    (10, 0.700, 98.0, 12.0),
    (11, 0.850, 113.1, 8.0),
    (12, 1.480, 160.0, 13.0),
    (13, 2.330, 224.0,  8.6),
    (14, 0.440, 82.6,  7.8),
    (15, 0.600, 87.9,  6.1),
    (16, 0.730, 97.3,  7.0),
    (17, 0.800, 105.0, 9.4),
]

print(f"{'#':>3} {'z':>6} {'H_obs':>8} {'sig':>6} {'H_LCDM':>8} {'beta':>8} {'sig_b':>8} {'chi2_i':>8} {'Survey'}")
print("-" * 80)

surveys = ['CC', 'CC', 'CC', 'CC', 'CC', '6dFGS', 'SDSS_MGS', 
           'BOSS', 'BOSS', 'BOSS', 'eBOSS_LRG', 'eBOSS_ELG',
           'eBOSS_QSO', 'eBOSS_Lya', 'WiggleZ', 'WiggleZ', 'WiggleZ', 'VIPERS']

total_chi2 = 0
weighted_beta_sum = 0
weight_sum = 0

for i, (idx, z, H_obs, sig) in enumerate(data):
    H_th = H_LCDM(z)
    beta = H_obs / H_th - 1
    sig_beta = sig / H_th
    chi2_i = (beta / sig_beta)**2
    total_chi2 += chi2_i
    
    weighted_beta_sum += beta / sig_beta**2
    weight_sum += 1.0 / sig_beta**2
    
    print(f"{i:3d} {z:6.3f} {H_obs:8.1f} {sig:6.1f} {H_th:8.2f} {beta:8.4f} {sig_beta:8.4f} {chi2_i:8.3f} {surveys[i]}")

print("-" * 80)
print(f"Total chi^2 (LCDM, beta=0): {total_chi2:.2f}")
print(f"chi^2/dof: {total_chi2/18:.3f}")

# Weighted mean beta
beta_mean = weighted_beta_sum / weight_sum
print(f"\nWeighted mean beta: {beta_mean:.5f}")
print(f"If zeta0 = -beta_mean: zeta0 = {-beta_mean:.5f}")

# Now let's also check: what if the monograph uses a different H0?
# The H0 tension: local measurements give H0 ~ 73.
# Maybe the monograph's "LCDM prediction" uses a different H0?

print("\n\n=== SENSITIVITY TO H0 ===")
for h0_test in [67.4, 70.0, 73.0, 75.0]:
    chi2 = 0
    for i, (idx, z, H_obs, sig) in enumerate(data):
        # Scale: H_test(z) = (h0_test/67.4) * H_LCDM(z) 
        # Actually need to recompute properly
        H_th = h0_test * np.sqrt(Om * (1+z)**3 + Or * (1+z)**4 + ODE)
        beta = H_obs / H_th - 1
        sig_beta = sig / H_th
        chi2 += (beta / sig_beta)**2
    print(f"H0 = {h0_test:.1f}: chi^2(LCDM) = {chi2:.2f}, chi^2/dof = {chi2/18:.3f}")

# Check: what zeta0 would you need to get chi^2 = 9.6?
# And what chi^2(LCDM) = 24.6 implies about the data
print("\n\n=== REVERSE ENGINEERING THE MONOGRAPH'S NUMBERS ===")
print("If chi^2(LCDM) = 24.6 and chi^2(Meridian) = 9.6 with zeta0=0.038:")
print("This requires sum((beta_i/sigma_i)^2) = 24.6")
print(f"My calculation gives: {total_chi2:.2f}")
print(f"Ratio: {24.6/total_chi2:.2f}")
print()
print("Possible explanations:")
print("1. Different H0 in the LCDM fiducial")
print("2. Different Omega_m")
print("3. Different dataset")
print("4. beta_HK defined differently (e.g., including growth rate modification)")
print("5. Error in the monograph's computation")
print()

# Let's check what combination of H0 and Om gives chi^2 ~ 24.6
print("\n=== SCAN: (H0, Om) combinations giving chi^2 ~ 24 ===")
from scipy.optimize import minimize_scalar

def chi2_lcdm_scan(h0, om):
    ode = 1.0 - om - Or
    chi2 = 0
    for i, (idx, z, H_obs, sig) in enumerate(data):
        H_th = h0 * np.sqrt(om * (1+z)**3 + Or * (1+z)**4 + ode)
        beta = H_obs / H_th - 1
        sig_beta = sig / H_th
        chi2 += (beta / sig_beta)**2
    return chi2

for h0 in [65.0, 67.4, 70.0, 73.0]:
    for om in [0.27, 0.30, 0.315, 0.33]:
        c2 = chi2_lcdm_scan(h0, om)
        if abs(c2 - 24.6) < 3:
            print(f"  H0={h0:.1f}, Om={om:.2f}: chi^2 = {c2:.2f}")

# Maybe the monograph uses H(z)/(1+z) or some other convention?
print("\n=== CHECKING ALTERNATIVE CONVENTIONS ===")

# Convention 1: Using E(z) = H(z)/H0 instead of H(z)
print("\nIf observable = H/H0 - E_LCDM(z):")
chi2_alt = 0
for i, (idx, z, H_obs, sig) in enumerate(data):
    E_obs = H_obs / H0
    E_th = np.sqrt(Om * (1+z)**3 + Or * (1+z)**4 + ODE)
    residual = E_obs - E_th
    sig_E = sig / H0
    chi2_alt += (residual / sig_E)**2
print(f"chi^2 = {chi2_alt:.2f}")

# Convention 2: Using H(z) directly
print("\nIf observable = H_obs - H_LCDM(z):")
chi2_alt2 = 0
for i, (idx, z, H_obs, sig) in enumerate(data):
    H_th = H_LCDM(z)
    residual = H_obs - H_th
    chi2_alt2 += (residual / sig)**2
print(f"chi^2 = {chi2_alt2:.2f}")

# These should be the same as beta formulation since chi^2 is scale-invariant
# Let me check if there's a factor of (1+z) issue

# The monograph model: H_meridian = H_LCDM * (1 + beta_HK) = H_LCDM * (1 - zeta0)
# But maybe the actual modification is more complex?
# The monograph says: "E^4 - R(a)E^2 - kappa0 = 0"
# with kappa0 = C_KK * epsilon1 * ODE
# This modifies H(z) at the ~0.1% level, not the ~4% level from zeta0

# Maybe zeta0 enters through: H^2 = (8piG/(3(1+2*zeta0))) * rho
# which gives H_meridian = H_LCDM / sqrt(1+2*zeta0)
# For zeta0 = 0.038: 1/sqrt(1.076) = 0.964, so 3.6% reduction
# beta = -0.036

print("\n=== TESTING MONOGRAPH'S GRAVITATIONAL MODIFICATION ===")
print("If H_meridian = H_LCDM / sqrt(1 + 2*zeta0):")
for zeta0_test in [0.01, 0.02, 0.038, 0.05]:
    factor = 1.0 / np.sqrt(1 + 2*zeta0_test)
    chi2_mod = 0
    for i, (idx, z, H_obs, sig) in enumerate(data):
        H_th = H_LCDM(z) * factor
        residual = H_obs - H_th
        chi2_mod += (residual / sig)**2
    print(f"  zeta0={zeta0_test:.3f}: H_factor={factor:.4f}, chi^2={chi2_mod:.2f}")
