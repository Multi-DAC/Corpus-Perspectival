#!/usr/bin/env python3
"""
Compute all values needed for monograph update at the OP#8 definitive prediction.
zeta_0 = 8.8e-4, w_0 = -0.830

Outputs: w(z) table, w_{a,eff}, model discrimination metrics, figure data.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
from scipy.optimize import minimize_scalar, brentq
from scipy.integrate import quad

def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)

# =============================================================================
# PARAMETERS
# =============================================================================
Omega_m = 0.315
Omega_DE = 0.685
eps_1 = 0.010
q0 = -0.5275
C_KK = (1 + q0)**2 * Omega_DE * eps_1 / (4 * (1 - q0)**2)
zeta_0 = 8.8e-4

fprint(f"C_KK = {C_KK:.6e}")
fprint(f"zeta_0 = {zeta_0:.4e}")
fprint(f"C_KK / zeta_0 = {C_KK / zeta_0:.6f}")

# Non-perturbative w_0 formula
kappa0 = C_KK * Omega_DE / (2.0 * zeta_0)
w0 = -1.0 + 2.0 * kappa0 / (kappa0 + Omega_DE)
fprint(f"kappa_0 = {kappa0:.6e}")
fprint(f"w_0 (non-perturbative) = {w0:.6f}")
fprint(f"1 + w_0 = {1 + w0:.6f}")

# Perturbative approximation
w0_pert = -1.0 + C_KK / zeta_0
fprint(f"w_0 (perturbative) = {w0_pert:.6f}")
fprint(f"Non-pert correction: {(w0 - w0_pert)/abs(1+w0)*100:.2f}%")


# =============================================================================
# w(z) COMPUTATION
# =============================================================================
fprint("\n" + "=" * 78)
fprint("w(z) AT THE OP#8 PREDICTION (zeta_0 = 8.8e-4)")
fprint("=" * 78)

def E_squared(z, w0_val):
    """Friedmann function for constant w (Meridian: w_a = 0 exactly)."""
    return Omega_m * (1 + z)**3 + Omega_DE * (1 + z)**(3 * (1 + w0_val))


def w_of_z(z, w0_val):
    """Meridian w(z) = -1 + (C_KK/zeta_0) / E^2(z).
    Since C_KK/zeta_0 = 1 + w_0 (perturbatively), this gives:
    w(z) = -1 + (1+w_0) * E^2(0) / E^2(z)
    Non-perturbatively: w(z) = -1 + 2*kappa_0 / (kappa_0 + Omega_DE * E^2(z)/E^2(0))
    """
    E2_z = E_squared(z, w0_val)
    E2_0 = E_squared(0, w0_val)
    # Non-perturbative
    return -1.0 + 2 * kappa0 / (kappa0 + Omega_DE * E2_z / E2_0)


# Table of w(z) values
redshifts = [0.0, 0.5, 1.0, 1.5, 2.0]
fprint(f"\n{'z':>6} {'w_Meridian':>12} {'w_CPL':>10} {'Gap':>10} {'Phantom?':>10}")
fprint("-" * 52)

# CPL best-fit (DESI DR2): w_0 = -0.75, w_a = -0.86
w0_cpl = -0.75
wa_cpl = -0.86

for z in redshifts:
    w_mer = w_of_z(z, w0)
    w_cpl = w0_cpl + wa_cpl * z / (1 + z)
    gap = w_mer - w_cpl
    phantom = "Yes" if w_cpl < -1 else "No"
    fprint(f"{z:6.1f} {w_mer:12.3f} {w_cpl:10.3f} {gap:+10.3f} {phantom:>10}")

# Also compute at DESI DR2 updated CPL: w_0 = -0.75, w_a = -0.83
fprint(f"\n--- With updated CPL (w_0 = -0.75, w_a = -0.83): ---")
wa_cpl2 = -0.83
for z in redshifts:
    w_mer = w_of_z(z, w0)
    w_cpl2 = w0_cpl + wa_cpl2 * z / (1 + z)
    gap = w_mer - w_cpl2
    phantom = "Yes" if w_cpl2 < -1 else "No"
    fprint(f"{z:6.1f} {w_mer:12.3f} {w_cpl2:10.3f} {gap:+10.3f} {phantom:>10}")


# =============================================================================
# w_{a,eff} COMPUTATION
# =============================================================================
fprint("\n" + "=" * 78)
fprint("w_{a,eff}: CPL fit to Meridian's w(z)")
fprint("=" * 78)

# Fit CPL template w(a) = w_0 + w_a*(1-a) to Meridian w(z) at DESI bins
# DESI effective redshifts (approximate)
z_desi = np.array([0.30, 0.51, 0.71, 0.93, 1.32, 2.33])

# Compute Meridian w(z) at these points
w_mer_desi = np.array([w_of_z(z, w0) for z in z_desi])

# Fit CPL: w(z) = w0_fit + wa_fit * z/(1+z)
# Linear regression: y = A + B*x where x = z/(1+z), y = w(z)
x_desi = z_desi / (1 + z_desi)
A = np.vstack([np.ones_like(x_desi), x_desi]).T
result = np.linalg.lstsq(A, w_mer_desi, rcond=None)
w0_fit, wa_fit = result[0]
fprint(f"\n  CPL fit to Meridian at DESI bins:")
fprint(f"    w_0 (fit) = {w0_fit:.4f}")
fprint(f"    w_a (fit) = {wa_fit:.4f}")
fprint(f"    This is w_{{a,eff}} = {wa_fit:.3f}")

# Also compute the flatness ratio
fprint(f"    Flatness ratio: CPL w_a / w_{{a,eff}} = {wa_cpl / wa_fit:.1f}x")

# For the old benchmark (w_0 = -0.755) for comparison
w0_old = -0.755
kappa0_old = C_KK * Omega_DE / (2.0 * 9.64e-4)
w_mer_old = []
for z in z_desi:
    E2_z = E_squared(z, w0_old)
    E2_0 = E_squared(0, w0_old)
    w_mer_old.append(-1.0 + 2 * kappa0_old / (kappa0_old + Omega_DE * E2_z / E2_0))
w_mer_old = np.array(w_mer_old)
result_old = np.linalg.lstsq(A, w_mer_old, rcond=None)
fprint(f"\n  Old benchmark (w_0 = -0.755):")
fprint(f"    w_a (fit) = {result_old[0][1]:.4f}")


# =============================================================================
# DR3 PREDICTIONS TABLE
# =============================================================================
fprint("\n" + "=" * 78)
fprint("DR3 PREDICTIONS AT OP#8 VALUES")
fprint("=" * 78)

# Prediction 1: w_0
# Need error bars on w_0. From w_0(zeta_0) with eps_GW uncertainty:
# eps_GW = 0.275 +0.072/-0.106 -> zeta_0 varies
# From the scan: at eps = 0.169 (lower 1sigma), w_0 = -0.89
#                at eps = 0.347 (upper 1sigma), w_0 = -0.77
w0_central = -0.830
w0_upper = -0.77  # +1sigma
w0_lower = -0.89  # -1sigma

fprint(f"\n  Prediction 1: w_0 = {w0_central:.3f} +{w0_central - w0_lower:.3f} / {w0_central - w0_upper:.3f}")
fprint(f"  Prediction 2: No phantom (w(z) > -1 for all z)")

# Prediction 3: Growth decoupling
gamma_GR = 0.55
gamma_mer = 0.5495
fprint(f"  Prediction 3: gamma = {gamma_mer} (growth decoupling)")

# Prediction 4: w_{a,eff}
fprint(f"  Prediction 4: w_{{a,eff}} = {wa_fit:.3f} ({abs(wa_cpl / wa_fit):.1f}x flatter than CPL)")

# Prediction 5: w(z=1)
w_z1 = w_of_z(1.0, w0)
w_cpl_z1 = w0_cpl + wa_cpl * 1.0 / 2.0
gap_z1 = w_z1 - w_cpl_z1
fprint(f"  Prediction 5: w(z=1) = {w_z1:.3f} (vs CPL: {w_cpl_z1:.3f}), gap = {gap_z1:.3f}")

# Prediction 6: sum m_nu
delta_mnu = 0.12 * abs(1 + w0)
fprint(f"  Prediction 6: sum m_nu < {0.064 + delta_mnu:.3f} eV (relaxed)")


# =============================================================================
# MODEL DISCRIMINATION TABLE
# =============================================================================
fprint("\n" + "=" * 78)
fprint("MODEL DISCRIMINATION TABLE (updated Meridian column)")
fprint("=" * 78)

fprint(f"\n  w_0:           {w0:.3f}")
fprint(f"  w_{{a,eff}}:      {wa_fit:.3f}")
fprint(f"  w(z=1):        {w_z1:.3f}")
fprint(f"  Phantom:       Never")
fprint(f"  gamma:         {gamma_mer}")
fprint(f"  Delta(fsig8):  <0.1%")


# =============================================================================
# PHANTOM CROSSING REDSHIFT FOR CPL
# =============================================================================
# CPL: w(z) = w_0 + w_a * z/(1+z) = -1 at z_phantom
# w_0 + w_a * z/(1+z) = -1
# -0.75 + (-0.86) * z/(1+z) = -1
# -0.86 * z/(1+z) = -0.25
# z/(1+z) = 0.25/0.86 = 0.291
# z = 0.291 / (1 - 0.291) = 0.410
z_phantom = 0.25 / 0.86 / (1 - 0.25/0.86)
fprint(f"\n  CPL phantom crossing: z = {z_phantom:.2f}")

# For w_a = -0.83:
z_phantom2 = 0.25 / 0.83 / (1 - 0.25/0.83)
fprint(f"  CPL phantom crossing (w_a = -0.83): z = {z_phantom2:.2f}")


# =============================================================================
# FALSIFICATION THRESHOLDS
# =============================================================================
fprint("\n" + "=" * 78)
fprint("FALSIFICATION THRESHOLDS")
fprint("=" * 78)

# 3-sigma bounds
w0_3sig_lo = w0_central - 3 * (w0_central - w0_lower)
w0_3sig_hi = w0_central + 3 * (w0_upper - w0_central)
fprint(f"\n  3-sigma range: [{w0_3sig_lo:.3f}, {w0_3sig_hi:.3f}]")
fprint(f"  Falsification: w_0 outside [{w0_3sig_hi:.2f}, {w0_3sig_lo:.2f}] at >3sigma")

# z=1 separation significance
desi_dr3_wz_precision = 0.04  # per bin
sigma_z1 = abs(gap_z1) / desi_dr3_wz_precision
fprint(f"  z=1 gap = {gap_z1:.3f}, significance = {sigma_z1:.1f}sigma at DR3 precision")

# z=0 separation
gap_z0 = w0 - w0_cpl
desi_w0_precision = 0.04
sigma_z0 = abs(gap_z0) / desi_w0_precision
fprint(f"  z=0 gap = {gap_z0:.3f}, significance = {sigma_z0:.1f}sigma at current precision")


# =============================================================================
# FIGURE DATA: w(z) comparison
# =============================================================================
fprint("\n" + "=" * 78)
fprint("FIGURE DATA")
fprint("=" * 78)

z_fine = np.linspace(0, 2.5, 500)
w_mer_fine = np.array([w_of_z(z, w0) for z in z_fine])
w_cpl_fine = w0_cpl + wa_cpl * z_fine / (1 + z_fine)

# Find z where gap is largest
gaps = np.abs(w_mer_fine - w_cpl_fine)
idx_max = np.argmax(gaps)
fprint(f"\n  Max gap at z = {z_fine[idx_max]:.2f}: |Delta w| = {gaps[idx_max]:.3f}")
fprint(f"  At z = 1.0: Meridian = {w_of_z(1.0, w0):.3f}, CPL = {w0_cpl + wa_cpl * 0.5:.3f}")

# Save arrays for figure generation
np.savez('wz_figure_data.npz',
         z=z_fine, w_mer=w_mer_fine, w_cpl=w_cpl_fine,
         w0_mer=w0, w0_cpl=w0_cpl, wa_cpl=wa_cpl)
fprint("  Saved to wz_figure_data.npz")


# =============================================================================
# CHAPTER 3 BENCHMARK RECONCILIATION
# =============================================================================
fprint("\n" + "=" * 78)
fprint("CHAPTER 3 BENCHMARK CHECK")
fprint("=" * 78)

# Old benchmark: zeta_0 = 0.001
kap_001 = C_KK * Omega_DE / (2 * 0.001)
w0_001 = -1.0 + 2 * kap_001 / (kap_001 + Omega_DE)
fprint(f"\n  zeta_0 = 0.001: w_0 = {w0_001:.3f}")
fprint(f"  zeta_0 = 8.8e-4: w_0 = {w0:.3f}")
fprint(f"  Difference: {w0 - w0_001:+.3f}")

# CMB benchmark
kap_037 = C_KK * Omega_DE / (2 * 0.037)
w0_037 = -1.0 + 2 * kap_037 / (kap_037 + Omega_DE)
fprint(f"  zeta_0 = 0.037: w_0 = {w0_037:.4f}")


fprint("\nDone.")
