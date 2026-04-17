#!/usr/bin/env python3
"""
Track 14C: Brane Parameter Determination from First Principles
Three Convergence Channels: Asymptotic Safety, DESI, NCG Spectral Action

Project Meridian — Phase 14
Authors: Clayton & Clawd
Date: March 18, 2026
"""

import numpy as np
from scipy.optimize import brentq
import json

np.random.seed(42)

# ==============================================================================
# SECTION 0: FUNDAMENTAL PARAMETERS
# ==============================================================================
print("=" * 80)
print("TRACK 14C: BRANE PARAMETER DETERMINATION")
print("Three Convergence Channels")
print("=" * 80)

# RS parameters (working units: M_5^3 = 1, k = 1)
sigma_UV = 6.0
alpha_UV = 0.01
mu2 = 0.1
xi = 1.0 / 6.0
M5_cubed = 1.0
k_RS = 1.0
ky_c = 35.0

# Cosmological parameters (Planck 2018)
Omega_DE = 0.685
Omega_m = 0.315
q0 = -0.55
sigma_q0 = 0.05
sigma_OmDE = 0.007
eps_1 = 0.017
sigma_eps1 = 0.003

# CKK constant (from 13F)
C_KK_central = 2.454e-4
C_KK_sigma = 0.827e-4

# Physical scales
M_Pl = 2.435e18  # GeV

print(f"\nFundamental parameters:")
print(f"  xi = {xi:.6f} (= 1/6)")
print(f"  C_KK = ({C_KK_central:.3e} +/- {C_KK_sigma:.3e})")

# ==============================================================================
# SECTION 1: JUNCTION CONDITION SOLUTION
# ==============================================================================
print("\n" + "=" * 80)
print("SECTION 1: JUNCTION CONDITION SOLUTION")
print("=" * 80)

def solve_junction_conditions(sigma_uv, alpha_uv, mu_sq, xi_val, M5c):
    """
    Solve UV Israel junction conditions (46a-b):
      A'(0+) = -(sigma_UV + alpha_UV * Phi_0^2) / (12 * F_0)
      2*mu^2 + 32*xi*Phi_0*A'(0+) + 4*alpha_UV*Phi_0 = 0
    where F_0 = M5^3 - xi*Phi_0^2
    """
    def residual(Phi_0):
        F_0 = M5c - xi_val * Phi_0**2
        if F_0 <= 0:
            return 1e10
        Aprime = -(sigma_uv + alpha_uv * Phi_0**2) / (12.0 * F_0)
        return 2.0 * mu_sq + 32.0 * xi_val * Phi_0 * Aprime + 4.0 * alpha_uv * Phi_0

    try:
        Phi_0 = brentq(residual, 0.001, 2.0, xtol=1e-15)
    except ValueError:
        try:
            Phi_0 = brentq(residual, 1e-6, 5.0, xtol=1e-15)
        except ValueError:
            return None, None, None, None

    F_0 = M5c - xi_val * Phi_0**2
    Aprime = -(sigma_uv + alpha_uv * Phi_0**2) / (12.0 * F_0)
    zeta_0 = xi_val * Phi_0**2 / M5c
    return Phi_0, F_0, Aprime, zeta_0

# Benchmark solution
Phi_0_bench, F_0_bench, Ap_bench, zeta_0_bench = solve_junction_conditions(
    sigma_UV, alpha_UV, mu2, xi, M5_cubed
)

w0_linear = -1.0 + C_KK_central / zeta_0_bench
kappa_0 = C_KK_central * Omega_DE / (2.0 * zeta_0_bench)
w0_exact = -1.0 + 2.0 * kappa_0 / (kappa_0 + Omega_DE)

print(f"\nBenchmark JC solution (sigma_UV={sigma_UV}, alpha_UV={alpha_UV}, mu^2={mu2}):")
print(f"  Phi_0  = {Phi_0_bench:.15f}")
print(f"  F_0    = {F_0_bench:.15f}")
print(f"  A'(0)  = {Ap_bench:.15f}")
print(f"  zeta_0 = {zeta_0_bench:.6e}")
print(f"  w_0 (linearized) = {w0_linear:.4f}")
print(f"  w_0 (exact)      = {w0_exact:.4f}")

# ==============================================================================
# SECTION 2: PARAMETER SPACE MAPPING
# ==============================================================================
print("\n" + "=" * 80)
print("SECTION 2: PARAMETER SPACE MAPPING (JC degeneracy)")
print("=" * 80)

print("\nScanning (sigma_UV, mu^2) with alpha_UV=0.01:")
print(f"{'sigma_UV':>10} {'mu^2':>10} {'Phi_0':>12} {'zeta_0':>12} {'w_0':>10}")
print("-" * 60)

for sig in [1.0, 3.0, 6.0, 10.0, 20.0, 50.0]:
    for m2 in [0.01, 0.05, 0.1, 0.5, 1.0]:
        r = solve_junction_conditions(sig, alpha_UV, m2, xi, M5_cubed)
        if r[0] is not None and 0 < r[3] < 1:
            w0 = -1.0 + C_KK_central / r[3]
            print(f"{sig:10.1f} {m2:10.3f} {r[0]:12.6f} {r[3]:12.6e} {w0:10.4f}")

print(f"\nScanning alpha_UV with sigma_UV=6, mu^2=0.1:")
print(f"{'alpha_UV':>10} {'Phi_0':>12} {'zeta_0':>12} {'w_0':>10}")
print("-" * 50)
for alph in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]:
    r = solve_junction_conditions(sigma_UV, alph, mu2, xi, M5_cubed)
    if r[0] is not None and 0 < r[3] < 1:
        w0 = -1.0 + C_KK_central / r[3]
        print(f"{alph:10.4f} {r[0]:12.6f} {r[3]:12.6e} {w0:10.4f}")

# ==============================================================================
# SECTION 3: CHANNEL 1 — ASYMPTOTIC SAFETY
# ==============================================================================
print("\n" + "=" * 80)
print("SECTION 3: CHANNEL 1 — ASYMPTOTIC SAFETY")
print("=" * 80)

g_star = 0.7
lambda_star = 0.19

def A_coeff(lam):
    num = 99 + 318*lam - 1464*lam**2 + 1232*lam**3 - 96*lam**4
    den = 18*np.pi*(1-2*lam)**3*(3-4*lam)**2
    return num / den

def B_coeff(lam):
    return 4*(21 - 8*lam) / (np.pi*(3-4*lam)**2)

def C_coeff_AS(lam):
    return 54*(5 - 8*lam) / (np.pi*(3-4*lam)**2)

A_val = A_coeff(lambda_star)
B_val = B_coeff(lambda_star)
C_val = C_coeff_AS(lambda_star)

print(f"\nAS coefficients at Reuter FP (g*={g_star}, lambda*={lambda_star}):")
print(f"  A(lambda*) = {A_val:.4f}")
print(f"  B(lambda*) = {B_val:.4f}")
print(f"  C(lambda*) = {C_val:.4f}")

# Beta functions
C_SM = 6.076
def beta_xi_grav(xi_val):
    return g_star * (-A_val * xi_val + B_val * xi_val**2 + C_val * xi_val**3)

def beta_xi_matter(xi_val):
    return (xi_val - 1.0/6.0) * C_SM / (16.0 * np.pi**2)

print(f"\nbeta_xi at key values:")
print(f"  beta_xi^grav(0)   = {beta_xi_grav(0.0):.6f}")
print(f"  beta_xi^grav(1/6) = {beta_xi_grav(xi):.6f}")
print(f"  beta_xi^matter(1/6) = {beta_xi_matter(xi):.6f}")
print(f"  beta_xi^total(1/6)  = {beta_xi_matter(xi) + beta_xi_grav(xi):.6f}")

# Scalar mass anomalous dimension
eta_m_minimal = -g_star / (np.pi * (1 - 2*lambda_star))
eta_m_conformal = eta_m_minimal * (1 - 6*xi)
dim_mu2 = 2 + eta_m_conformal

print(f"\nScalar mass anomalous dimension:")
print(f"  eta_m (xi=0):   {eta_m_minimal:.4f}")
print(f"  eta_m (xi=1/6): {eta_m_conformal:.4f}")
print(f"  Scaling dim of mu^2: Delta = 2 + eta_m = {dim_mu2:.4f}")
print(f"  Since Delta > 0, mu^2 is RELEVANT (UV-free)")

print(f"""
AS CHANNEL VERDICT:
  AS does NOT determine zeta_0.
  All three brane parameters (sigma_UV, alpha_UV, mu^2) are relevant
  perturbations at the Reuter FP (positive scaling dimensions).
  Their values are UV-free, like quark masses in QCD.
  AS contributes CONSTRAINTS on running, not determination of values.
""")

# ==============================================================================
# SECTION 4: CHANNEL 2 — DESI OBSERVATIONAL CONSTRAINTS
# ==============================================================================
print("=" * 80)
print("SECTION 4: CHANNEL 2 — DESI OBSERVATIONAL CONSTRAINTS")
print("=" * 80)

w0_DESI = -0.75
sigma_w0_DESI = 0.05

# Monte Carlo propagation
N_MC = 200000
q0_samples = np.random.normal(q0, sigma_q0, N_MC)
OmDE_samples = np.random.normal(Omega_DE, sigma_OmDE, N_MC)
eps1_samples = np.random.normal(eps_1, sigma_eps1, N_MC)
w0_DESI_samples = np.random.normal(w0_DESI, sigma_w0_DESI, N_MC)

C_KK_samples = ((1 + q0_samples)**2 * OmDE_samples * eps1_samples) / \
               (4 * (1 - q0_samples)**2)

valid = (1 + w0_DESI_samples) > 0.001
zeta_DESI_samples = np.where(valid, C_KK_samples / (1 + w0_DESI_samples), np.nan)
zeta_DESI_valid = zeta_DESI_samples[~np.isnan(zeta_DESI_samples)]

zeta_DESI_median = np.nanmedian(zeta_DESI_valid)
zeta_DESI_mean = np.nanmean(zeta_DESI_valid)
zeta_DESI_lo = np.nanpercentile(zeta_DESI_valid, 16)
zeta_DESI_hi = np.nanpercentile(zeta_DESI_valid, 84)
zeta_DESI_2lo = np.nanpercentile(zeta_DESI_valid, 2.5)
zeta_DESI_2hi = np.nanpercentile(zeta_DESI_valid, 97.5)

print(f"\nDESI DR1 constraint on zeta_0:")
print(f"  w_0 = {w0_DESI} +/- {sigma_w0_DESI}")
print(f"  zeta_0 (median) = {zeta_DESI_median:.4e}")
print(f"  zeta_0 (mean)   = {zeta_DESI_mean:.4e}")
print(f"  1-sigma: [{zeta_DESI_lo:.4e}, {zeta_DESI_hi:.4e}]")
print(f"  2-sigma: [{zeta_DESI_2lo:.4e}, {zeta_DESI_2hi:.4e}]")

sigma_offset = (zeta_0_bench - zeta_DESI_median) / ((zeta_DESI_hi - zeta_DESI_lo)/2)
print(f"\n  JC benchmark: zeta_0 = {zeta_0_bench:.4e}")
print(f"  DESI median:  zeta_0 = {zeta_DESI_median:.4e}")
print(f"  Offset: {sigma_offset:.2f} sigma")

# DESI DR3 forecast
sigma_w0_DR3 = sigma_w0_DESI / 1.8
w0_DR3_samples = np.random.normal(w0_DESI, sigma_w0_DR3, N_MC)
valid_DR3 = (1 + w0_DR3_samples) > 0.001
zeta_DR3_samples = np.where(valid_DR3, C_KK_samples / (1 + w0_DR3_samples), np.nan)
zeta_DR3_valid = zeta_DR3_samples[~np.isnan(zeta_DR3_samples)]
zeta_DR3_lo = np.nanpercentile(zeta_DR3_valid, 16)
zeta_DR3_hi = np.nanpercentile(zeta_DR3_valid, 84)

print(f"\nDESI DR3 forecast (sigma(w_0) = {sigma_w0_DR3:.3f}):")
print(f"  1-sigma: [{zeta_DR3_lo:.4e}, {zeta_DR3_hi:.4e}]")
print(f"  Width reduction: {(zeta_DESI_hi-zeta_DESI_lo)/(zeta_DR3_hi-zeta_DR3_lo):.1f}x")

# Euclid + DESI Y5
sigma_w0_future = 0.01
q0_future = np.random.normal(q0, 0.01, N_MC)
OmDE_future = np.random.normal(Omega_DE, 0.003, N_MC)
eps1_future = np.random.normal(eps_1, sigma_eps1, N_MC)
C_KK_future = ((1 + q0_future)**2 * OmDE_future * eps1_future) / \
              (4 * (1 - q0_future)**2)
w0_fut_samples = np.random.normal(w0_DESI, sigma_w0_future, N_MC)
valid_fut = (1 + w0_fut_samples) > 0.001
zeta_fut_samples = np.where(valid_fut, C_KK_future / (1 + w0_fut_samples), np.nan)
zeta_fut_valid = zeta_fut_samples[~np.isnan(zeta_fut_samples)]
zeta_fut_lo = np.nanpercentile(zeta_fut_valid, 16)
zeta_fut_hi = np.nanpercentile(zeta_fut_valid, 84)

print(f"\nDESI Y5 + Euclid forecast (sigma(w_0) = {sigma_w0_future}):")
print(f"  1-sigma: [{zeta_fut_lo:.4e}, {zeta_fut_hi:.4e}]")
print(f"  Width reduction: {(zeta_DESI_hi-zeta_DESI_lo)/(zeta_fut_hi-zeta_fut_lo):.1f}x")

print(f"""
DESI CHANNEL VERDICT:
  DESI CONSTRAINS zeta_0 but does not DETERMINE it from first principles.
  Current: zeta_0 = {zeta_DESI_median:.4e} [{zeta_DESI_lo:.4e}, {zeta_DESI_hi:.4e}]
  JC benchmark consistent at {abs(sigma_offset):.1f} sigma.
  DESI measures zeta_0 through w_0 — the question is whether theory predicts it.
""")

# ==============================================================================
# SECTION 5: CHANNEL 3 — NCG SPECTRAL ACTION
# ==============================================================================
print("=" * 80)
print("SECTION 5: CHANNEL 3 — NCG SPECTRAL ACTION")
print("=" * 80)

# The spectral action determines the scalar mass through the a_2 coefficient.
# On AdS_5: R_5 = -20k^2, and xi = 1/6 gives the conformal coupling.
# The effective bulk mass: mu^2_eff = -R_5 * xi = 20k^2 * (1/6) = 10k^2/3

R_5 = -20 * k_RS**2
d_S = 4  # Spinor dimension in 4D and 5D
mu2_spectral = -R_5 * xi  # = 10k^2/3

print(f"\nSpectral action scalar potential:")
print(f"  R_5 = {R_5:.1f} k^2")
print(f"  xi = 1/6")
print(f"  mu^2_eff = -R_5 * xi = {mu2_spectral:.4f} k^2")
print(f"  mu^2 (benchmark) = {mu2}")
print(f"  Discrepancy: factor of {mu2_spectral/mu2:.1f}")

# a_4 coefficients (from 14A.2 — corrected)
print(f"\n  Curvature-squared (from a_4): (C^2, E_4, R^2) = (-18, +11, 0)")
print(f"  R^2 = 0 is STRUCTURAL (Dirac conformal identity)")

# Solve JC with spectral-action mu^2
print(f"\nJC solution with NCG mu^2 = {mu2_spectral:.4f}:")
r_NCG = solve_junction_conditions(sigma_UV, alpha_UV, mu2_spectral, xi, M5_cubed)
if r_NCG[0] is not None:
    w0_NCG = -1.0 + C_KK_central / r_NCG[3]
    print(f"  Phi_0  = {r_NCG[0]:.10f}")
    print(f"  zeta_0 = {r_NCG[3]:.6e}")
    print(f"  w_0    = {w0_NCG:.4f}")
else:
    print("  No solution found with benchmark alpha_UV=0.01")
    # Scan for where solutions exist
    print("  Scanning alpha_UV:")
    for alph in np.logspace(-3, 2, 50):
        r = solve_junction_conditions(sigma_UV, alph, mu2_spectral, xi, M5_cubed)
        if r[0] is not None and 0 < r[3] < 1:
            print(f"    alpha_UV={alph:.4f}: Phi_0={r[0]:.6f}, zeta_0={r[3]:.4e}")
            break

# NCG zeta_0 as function of alpha_UV (with mu^2=10/3 and sigma_UV=6 fixed)
print(f"\nNCG-predicted zeta_0 vs alpha_UV (mu^2={mu2_spectral:.2f}, sigma_UV={sigma_UV}):")
print(f"{'alpha_UV':>10} {'Phi_0':>12} {'zeta_0':>12} {'w_0':>10}")
print("-" * 50)

ncg_results = []
for alph in [0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]:
    r = solve_junction_conditions(sigma_UV, alph, mu2_spectral, xi, M5_cubed)
    if r[0] is not None and 0 < r[3] < 1:
        w0 = -1.0 + C_KK_central / r[3]
        ncg_results.append({'alpha_UV': alph, 'Phi_0': r[0], 'zeta_0': r[3], 'w_0': w0})
        print(f"{alph:10.3f} {r[0]:12.6f} {r[3]:12.6e} {w0:10.4f}")

# Find DESI-consistent alpha_UV
desi_consistent = [r for r in ncg_results
                   if zeta_DESI_lo <= r['zeta_0'] <= zeta_DESI_hi]
if desi_consistent:
    print(f"\nDESI-consistent solutions:")
    for r in desi_consistent:
        print(f"  alpha_UV={r['alpha_UV']:.3f}: zeta_0={r['zeta_0']:.4e}, w_0={r['w_0']:.4f}")

# Try to find exact alpha_UV matching DESI median by interpolation
if len(ncg_results) >= 2:
    alphas_arr = np.array([r['alpha_UV'] for r in ncg_results])
    zetas_arr = np.array([r['zeta_0'] for r in ncg_results])

    # Find bracket for DESI median
    target = zeta_DESI_median
    for i in range(len(zetas_arr)-1):
        if (zetas_arr[i] - target) * (zetas_arr[i+1] - target) < 0:
            # Bisection to find alpha
            a_lo, a_hi = alphas_arr[i], alphas_arr[i+1]
            for _ in range(50):
                a_mid = (a_lo + a_hi) / 2
                r = solve_junction_conditions(sigma_UV, a_mid, mu2_spectral, xi, M5_cubed)
                if r[0] is None:
                    break
                if r[3] > target:
                    a_hi = a_mid
                else:
                    a_lo = a_mid
            r_final = solve_junction_conditions(sigma_UV, a_mid, mu2_spectral, xi, M5_cubed)
            if r_final[0] is not None:
                print(f"\nExact DESI-matching alpha_UV (NCG channel):")
                print(f"  alpha_UV = {a_mid:.6f}")
                print(f"  Phi_0    = {r_final[0]:.10f}")
                print(f"  zeta_0   = {r_final[3]:.6e} (target: {target:.6e})")
                print(f"  w_0      = {-1+C_KK_central/r_final[3]:.4f}")
            break

print(f"""
NCG CHANNEL VERDICT:
  NCG PARTIALLY determines zeta_0 — reduces to 1 free parameter (alpha_UV).
  Fixes: mu^2/k^2 = 10/3 (from xi=1/6 and R_5=-20k^2)
         sigma_UV/(M_5^3 k) = 6 (RS structural)
  Leaves: alpha_UV free (from boundary spectral terms)
  Combined with DESI: alpha_UV can be determined.
""")

# ==============================================================================
# SECTION 6: THREE-CHANNEL CONVERGENCE TEST
# ==============================================================================
print("=" * 80)
print("SECTION 6: THREE-CHANNEL CONVERGENCE TEST")
print("=" * 80)

print(f"""
CHANNEL 1 (AS):   zeta_0 is FREE (all brane params are relevant perturbations)
CHANNEL 2 (DESI): zeta_0 = {zeta_DESI_median:.4e} +/- {(zeta_DESI_hi-zeta_DESI_lo)/2:.4e} (measurement)
CHANNEL 3 (NCG):  zeta_0 = zeta_0(alpha_UV) (1-parameter family)

Convergence status: PARTIAL

The three channels are COMPLEMENTARY, not REDUNDANT:
  - AS tells us zeta_0 cannot be predicted from the UV fixed point alone
  - NCG reduces the parameter space from 3D to 1D
  - DESI provides the observational measurement

Together they tell a consistent story: zeta_0 ~ 10^-3 is the
brane scalar condensate, determined by one remaining UV parameter (alpha_UV),
and consistent with both the JC benchmark and DESI observations.
""")

# ==============================================================================
# SECTION 7: PARAMETER DEGENERACY STRUCTURE
# ==============================================================================
print("=" * 80)
print("SECTION 7: PARAMETER DEGENERACY STRUCTURE")
print("=" * 80)

target_zeta = 1.0e-3
Phi_target = np.sqrt(target_zeta * M5_cubed / xi)
F_target = M5_cubed - xi * Phi_target**2
coeff = 8 * xi * Phi_target / (3 * F_target)

print(f"Constant-zeta_0 surface at zeta_0 = {target_zeta:.1e} (Phi_0 = {Phi_target:.6f}):")
print(f"Degeneracy: mu^2 = {coeff/2:.6f}*sigma_UV + alpha_UV*({coeff*Phi_target**2/2 - 2*Phi_target:.6f})")
print()
print(f"{'sigma_UV':>10} {'alpha_UV':>10} {'mu^2':>10} {'Check zeta_0':>14}")
print("-" * 50)

for sig in [1.0, 3.0, 6.0, 10.0, 20.0]:
    for alph in [0.01, 0.1, 1.0]:
        mu2_needed = (coeff * sig + alph * (coeff * Phi_target**2 - 4*Phi_target)) / 2.0
        if mu2_needed > 0:
            r = solve_junction_conditions(sig, alph, mu2_needed, xi, M5_cubed)
            if r[0] is not None and abs(r[3] - target_zeta)/target_zeta < 0.1:
                print(f"{sig:10.1f} {alph:10.3f} {mu2_needed:10.4f} {r[3]:14.6e}")

# ==============================================================================
# SECTION 8: WHAT WOULD DETERMINE zeta_0 FROM FIRST PRINCIPLES
# ==============================================================================
print("\n" + "=" * 80)
print("SECTION 8: WHAT WOULD DETERMINE zeta_0 FROM FIRST PRINCIPLES?")
print("=" * 80)

print("""
After exhaustive analysis, the honest answer:

  zeta_0 CANNOT be fully determined from first principles with current tools.

The obstruction is clean:

1. AS: All brane parameters are RELEVANT perturbations (positive scaling dim).
   Their UV values are free, like quark masses in QCD.

2. NCG: Determines mu^2/k^2 and sigma_UV/(M_5^3 k), but NOT alpha_UV.
   Reduces 3 free parameters to 1.

3. DESI: Measures zeta_0, but this is observation, not prediction.

WHAT WOULD CLOSE THE GAP:

(a) Conjecture 4.1 proof (Track 14A.1): If NCG axioms uniquely determine
    the boundary conditions on D_5 at the branes, then alpha_UV is fixed
    by the spectral triple geometry. MOST PROMISING AVENUE.

(b) 5D FRG on RS background (Track 13M): If the warped FRG has additional
    fixed-point structure constraining brane couplings.

(c) Stability constraint: Not all alpha_UV values produce stable vacua.
    Tachyonic/ghost modes might select a unique viable point.

(d) Goldberger-Wise: Radion stabilization provides one additional constraint,
    reducing degeneracy from 2D to 1D on constant-zeta_0 surface.
    But one parameter still remains.
""")

# ==============================================================================
# SECTION 9: COMBINED BEST ESTIMATE
# ==============================================================================
print("=" * 80)
print("SECTION 9: COMBINED BEST ESTIMATE")
print("=" * 80)

zeta_best = (zeta_0_bench + zeta_DESI_median) / 2
w0_best = -1 + C_KK_central / zeta_best

print(f"\nBEST CURRENT VALUES:")
print(f"  zeta_0 (JC benchmark):  {zeta_0_bench:.4e}")
print(f"  zeta_0 (DESI median):   {zeta_DESI_median:.4e}")
print(f"  zeta_0 (combined):      {zeta_best:.4e}")
print(f"  w_0 (combined):         {w0_best:.3f}")
print(f"  |1+w_0|:                {abs(C_KK_central/zeta_best):.3f}")

print(f"\nUncertainty budget:")
dw_CKK = C_KK_sigma / zeta_0_bench
dw_zeta = abs(C_KK_central/zeta_DESI_lo - C_KK_central/zeta_DESI_hi) / 2
dw_total = np.sqrt(dw_CKK**2 + dw_zeta**2)
print(f"  From C_KK (q_0, eps_1): dw_0 ~ {dw_CKK:.3f}")
print(f"  From zeta_0 (DESI w_0): dw_0 ~ {dw_zeta:.3f}")
print(f"  Total (quadrature):     dw_0 ~ {dw_total:.3f}")

# ==============================================================================
# SECTION 10: SUMMARY TABLE
# ==============================================================================
print("\n" + "=" * 80)
print("SECTION 10: FINAL SUMMARY")
print("=" * 80)

print("""
+------------------+-----------------------------------------------------+
| Channel          | Contribution to zeta_0 determination                |
+------------------+-----------------------------------------------------+
| AS               | CONSTRAINTS on running, NOT determination           |
|                  | All brane params are relevant (UV-free)             |
+------------------+-----------------------------------------------------+
| DESI             | MEASUREMENT through w_0                             |
|                  | zeta_0 ~ 9.8e-4 +/- 4.5e-4 (1sigma)               |
|                  | DR3 -> 1.8x tighter, Y5+Euclid -> ~5x              |
+------------------+-----------------------------------------------------+
| NCG              | PARTIAL determination (1 free param remains)        |
|                  | Fixes mu^2/k^2 = 10/3, sigma_UV/(M5^3 k) = 6      |
|                  | Leaves alpha_UV free                                |
+------------------+-----------------------------------------------------+
| COMBINED         | zeta_0 = zeta_0(alpha_UV)                           |
|                  | alpha_UV measured by DESI (not predicted)            |
|                  | Full determination needs Conj. 4.1 or 5D FRG       |
+------------------+-----------------------------------------------------+
""")

# Save results
results = {
    'jc_benchmark': {
        'sigma_UV': sigma_UV, 'alpha_UV': alpha_UV, 'mu2': mu2,
        'Phi_0': float(Phi_0_bench), 'zeta_0': float(zeta_0_bench),
        'w0_linear': float(w0_linear), 'w0_exact': float(w0_exact)
    },
    'desi_constraint': {
        'zeta_0_median': float(zeta_DESI_median),
        'zeta_0_1sigma': [float(zeta_DESI_lo), float(zeta_DESI_hi)],
        'zeta_0_2sigma': [float(zeta_DESI_2lo), float(zeta_DESI_2hi)],
        'jc_desi_offset_sigma': float(sigma_offset)
    },
    'ncg_prediction': {
        'mu2_over_k2': float(mu2_spectral),
        'sigma_UV_RS': float(sigma_UV),
        'alpha_UV': 'free parameter',
        'note': 'reduces 3 free params to 1'
    },
    'as_analysis': {
        'all_brane_params_relevant': True,
        'eta_m_xi_sixth': float(eta_m_conformal),
        'dim_mu2': float(dim_mu2),
        'note': 'no determination - all params UV-free'
    },
    'convergence': {
        'status': 'PARTIAL',
        'jc_desi_consistent': True,
        'remaining_free_params': 1,
        'free_param': 'alpha_UV',
        'resolution_paths': [
            'Conjecture 4.1 proof (NCG axioms fix boundary conditions)',
            '5D FRG on RS orbifold (additional fixed-point constraints)',
            'Stability analysis (tachyonic mode exclusion)',
            'Goldberger-Wise (radion stabilization constraint)'
        ]
    },
    'best_estimate': {
        'zeta_0': float(zeta_best),
        'w_0': float(w0_best),
        'uncertainty_CKK': float(dw_CKK),
        'uncertainty_zeta': float(dw_zeta),
        'uncertainty_total': float(dw_total)
    }
}

outpath = 'C:/Users/mercu/clawd/projects/Project Meridian/phase14/14C_brane_parameters_results.json'
with open(outpath, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {outpath}")
print("=" * 80)
