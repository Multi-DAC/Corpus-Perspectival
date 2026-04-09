#!/usr/bin/env python3
"""
CAMB Grid Accuracy Check
=========================
Evaluate CAMB exactly at v3's best-fit points and compare with grid interpolation.
This determines whether the 100x100 grid is accurate enough for CMB shift parameters.
"""

import numpy as np
import camb
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
C_KMS = 299792.458
OMBH2 = 0.02237

# Load grid
g = np.load(os.path.join(OUTPUT_DIR, 'camb_grid_100x100.npz'))
Om_grid = g['Om_grid']
H0_grid = g['H0_grid']
rd_grid = np.nan_to_num(g['rd'], nan=np.nanmedian(g['rd']))
rs_star_grid = np.nan_to_num(g['rs_star'], nan=np.nanmedian(g['rs_star']))
dc_star_grid = np.nan_to_num(g['dc_star'], nan=np.nanmedian(g['dc_star']))

def grid_interp(Om, H0, grid_data):
    """Bilinear interpolation (matching v5 implementation)."""
    dOm = Om_grid[1] - Om_grid[0]
    dH0 = H0_grid[1] - H0_grid[0]
    fi = np.clip((Om - Om_grid[0]) / dOm, 0.0, grid_data.shape[0] - 1.001)
    fj = np.clip((H0 - H0_grid[0]) / dH0, 0.0, grid_data.shape[1] - 1.001)
    i0 = int(np.floor(fi))
    j0 = int(np.floor(fj))
    i1 = min(i0 + 1, grid_data.shape[0] - 1)
    j1 = min(j0 + 1, grid_data.shape[1] - 1)
    wi = fi - i0
    wj = fj - j0
    return (grid_data[i0,j0]*(1-wi)*(1-wj) + grid_data[i1,j0]*wi*(1-wj) +
            grid_data[i0,j1]*(1-wi)*wj + grid_data[i1,j1]*wi*wj)

def camb_exact(Om, H0):
    """Exact CAMB computation at a single point."""
    h = H0 / 100.0
    omch2 = Om * h**2 - OMBH2
    if omch2 <= 0:
        return None
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0, ombh2=OMBH2, omch2=omch2,
                       mnu=0.06, num_massive_neutrinos=1)
    pars.set_dark_energy(w=-1.0, dark_energy_model='fluid')
    pars.InitPower.set_params(As=2.1e-9, ns=0.9649)
    pars.set_matter_power(redshifts=[0], kmax=0.5)
    results = camb.get_results(pars)
    derived = results.get_derived_params()
    rd = derived['rdrag']
    zstar = derived['zstar']
    rs_star = derived['rstar']
    DA_star = results.angular_diameter_distance(zstar)
    dc_star = DA_star * (1 + zstar)  # comoving distance to last scattering
    return rd, rs_star, dc_star, zstar

# CMB data
cmb_means = np.array([1.7502, 301.471, 0.02237])
cmb_sigmas = np.array([0.0046, 0.090, 0.00015])
cmb_corr = np.array([[1.0, 0.46, -0.66], [0.46, 1.0, -0.33], [-0.66, -0.33, 1.0]])
cmb_cov = np.outer(cmb_sigmas, cmb_sigmas) * cmb_corr
cmb_cov_inv = np.linalg.inv(cmb_cov)

def cmb_chi2(Om, H0, dc_star, rs_star):
    """CMB compressed chi2."""
    R = np.sqrt(Om) * H0 * dc_star / C_KMS
    l_A = np.pi * dc_star / rs_star
    vec = np.array([R, l_A, OMBH2]) - cmb_means
    return vec @ cmb_cov_inv @ vec, R, l_A

# Test points
test_points = [
    ("v3 Fit A best-fit", 0.3094, 67.92),
    ("v5 Fit A best-fit", 0.3113, 67.88),
    ("v3 Fit B best-fit", 0.3081, 68.29),
    ("v5 Fit B best-fit", 0.3110, 67.90),
    ("Fiducial",          0.3150, 67.40),
    ("H0=68.5 test",      0.3100, 68.50),
    ("H0=69.0 test",      0.3100, 69.00),
]

print("=" * 80)
print("  CAMB GRID ACCURACY CHECK")
print("=" * 80)
print(f"  Grid: {Om_grid.shape[0]}x{H0_grid.shape[0]}")
print(f"  Om range: [{Om_grid[0]:.2f}, {Om_grid[-1]:.2f}], step={Om_grid[1]-Om_grid[0]:.4f}")
print(f"  H0 range: [{H0_grid[0]:.1f}, {H0_grid[-1]:.1f}], step={H0_grid[1]-H0_grid[0]:.3f}")

for label, Om, H0 in test_points:
    print(f"\n--- {label} (Om={Om:.4f}, H0={H0:.2f}) ---")

    # Grid interpolation
    rd_g = grid_interp(Om, H0, rd_grid)
    rs_g = grid_interp(Om, H0, rs_star_grid)
    dc_g = grid_interp(Om, H0, dc_star_grid)
    chi2_g, R_g, lA_g = cmb_chi2(Om, H0, dc_g, rs_g)

    # Exact CAMB
    result = camb_exact(Om, H0)
    if result is None:
        print("  CAMB failed at this point")
        continue
    rd_c, rs_c, dc_c, zstar = result
    chi2_c, R_c, lA_c = cmb_chi2(Om, H0, dc_c, rs_c)

    print(f"  {'':>15} {'Grid':>14} {'CAMB':>14} {'Delta':>12} {'Rel%':>10}")
    print(f"  {'rd (Mpc)':>15} {rd_g:>14.4f} {rd_c:>14.4f} {rd_g-rd_c:>+12.4f} {(rd_g-rd_c)/rd_c*100:>+10.4f}%")
    print(f"  {'rs_star (Mpc)':>15} {rs_g:>14.4f} {rs_c:>14.4f} {rs_g-rs_c:>+12.4f} {(rs_g-rs_c)/rs_c*100:>+10.4f}%")
    print(f"  {'dc_star (Mpc)':>15} {dc_g:>14.2f} {dc_c:>14.2f} {dc_g-dc_c:>+12.2f} {(dc_g-dc_c)/dc_c*100:>+10.4f}%")
    print(f"  {'R':>15} {R_g:>14.6f} {R_c:>14.6f} {R_g-R_c:>+12.6f}")
    print(f"  {'l_A':>15} {lA_g:>14.4f} {lA_c:>14.4f} {lA_g-lA_c:>+12.4f}")
    print(f"  {'CMB chi2':>15} {chi2_g:>14.4f} {chi2_c:>14.4f} {chi2_g-chi2_c:>+12.4f}")
    print(f"  {'zstar':>15} {'N/A':>14} {zstar:>14.4f}")
