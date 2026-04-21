"""
CAMB Refit for Meridian Monograph — Corrected ε₁ = 0.010
April 1, 2026. Clawd.

Recomputes:
1. Boltzmann scan: χ²(ζ₀) over Planck compressed + DESI Y1 BAO
2. BAO distance tables at JC and CMB benchmarks (DESI DR2 redshifts)
3. Multi-probe best-fit (analytical + numerical cross-check)
4. CMB benchmark table (H₀, χ²_CMB at each benchmark)
"""

import numpy as np
import camb
from camb import model
from scipy.optimize import minimize_scalar
import json
import os

# ============================================================
# Physical constants — CORRECTED
# ============================================================
C_KK = 1.64e-4        # OP#8 definitive (Planck 2018 fiducial q0=-0.5275)
C_KK_err = 0.33e-4    # uncertainty from eps1 cutoff function
eps1 = 0.010
eps1_err = 0.002

# Planck 2018 fiducial
H0_fid = 67.36
ombh2 = 0.02237
omch2 = 0.1200
Omega_m = 0.315
Omega_DE = 0.685
tau = 0.054
ns = 0.9649
As = 2.1e-9

# ============================================================
# DESI Year 1 BAO data (from Ch2 Section 2.5)
# ============================================================
# z_eff, measurement_type, value, sigma
desi_y1_bao = [
    # DV/rd measurements
    (0.295, 'DV', 7.93, 0.15),
    # DM/rd and DH/rd measurements
    (0.510, 'DM', 13.62, 0.25),
    (0.510, 'DH', 22.33, 0.58),
    (0.706, 'DM', 17.86, 0.33),
    (0.706, 'DH', 20.08, 0.61),
    (0.930, 'DM', 21.71, 0.28),
    (0.930, 'DH', 17.88, 0.35),
    (1.317, 'DM', 27.79, 0.69),
    (1.317, 'DH', 13.82, 0.42),
    (2.330, 'DM', 39.71, 0.94),
    (2.330, 'DH',  8.52, 0.17),
]

# ============================================================
# Planck 2018 compressed distance priors
# ============================================================
# Central values
planck_la = 301.471   # acoustic scale
planck_R = 1.7502     # shift parameter
planck_wb = 0.02237   # baryon density

# Covariance matrix (from Planck 2018 compressed likelihood)
# Correlations: rho(lA, R) = 0.46, rho(lA, wb) = -0.66, rho(R, wb) = -0.33
sigma_la = 0.090
sigma_R = 0.0046
sigma_wb = 0.00015

cov_planck = np.array([
    [sigma_la**2,
     0.46 * sigma_la * sigma_R,
     -0.66 * sigma_la * sigma_wb],
    [0.46 * sigma_la * sigma_R,
     sigma_R**2,
     -0.33 * sigma_R * sigma_wb],
    [-0.66 * sigma_la * sigma_wb,
     -0.33 * sigma_R * sigma_wb,
     sigma_wb**2]
])
cov_planck_inv = np.linalg.inv(cov_planck)

# ============================================================
# DESI DR2 BAO data (7 tracers, for distance tables)
# Approximate uncertainties from published precision
# ============================================================
desi_dr2_tracers = [
    {'name': 'BGS',        'z': 0.295, 'sigma_DM_pct': 1.5, 'sigma_DH_pct': 2.0},
    {'name': 'LRG1',       'z': 0.510, 'sigma_DM_pct': 0.9, 'sigma_DH_pct': 1.7},
    {'name': 'LRG2',       'z': 0.706, 'sigma_DM_pct': 0.6, 'sigma_DH_pct': 1.3},
    {'name': 'LRG3+ELG1',  'z': 0.934, 'sigma_DM_pct': 0.5, 'sigma_DH_pct': 0.8},
    {'name': 'ELG2',       'z': 1.321, 'sigma_DM_pct': 0.7, 'sigma_DH_pct': 1.0},
    {'name': 'QSO',        'z': 1.484, 'sigma_DM_pct': 1.5, 'sigma_DH_pct': 1.2},
    {'name': 'Lya',        'z': 2.330, 'sigma_DM_pct': 1.2, 'sigma_DH_pct': 1.1},
]


def w0_from_zeta0(zeta0):
    """Perturbative w0 from zeta0."""
    return -1 + C_KK / zeta0


def w0_exact_from_zeta0(zeta0):
    """Non-perturbative w0 from the quartic Friedmann equation."""
    kappa0 = C_KK * Omega_DE / (2 * zeta0)
    return 2 * kappa0 / (kappa0 + Omega_DE) - 1


def get_camb_results(w0, H0=H0_fid):
    """Run CAMB for constant-w dark energy."""
    pars = camb.CAMBparams()
    pars.set_cosmology(
        H0=H0, ombh2=ombh2, omch2=omch2, tau=tau,
        mnu=0.06, nnu=3.046
    )
    pars.set_dark_energy(w=w0, wa=0, dark_energy_model='fluid')
    pars.InitPower.set_params(As=As, ns=ns)
    pars.set_matter_power(redshifts=[0], kmax=2.0)
    pars.NonLinear = model.NonLinear_none

    results = camb.get_results(pars)
    return results


def get_distances(results, z_arr):
    """Get DM/rd and DH/rd at given redshifts."""
    rd = results.get_derived_params()['rdrag']
    c_km_s = 299792.458  # km/s

    DM_over_rd = []
    DH_over_rd = []

    for z in z_arr:
        DM = results.comoving_radial_distance(z)  # Mpc
        Hz = results.hubble_parameter(z)           # km/s/Mpc
        DM_over_rd.append(DM / rd)
        DH_over_rd.append(c_km_s / (Hz * rd))

    return np.array(DM_over_rd), np.array(DH_over_rd), rd


def chi2_planck_compressed(results):
    """Compute chi2 for Planck compressed distance priors.
    Uses rstar (sound horizon at recombination), NOT rdrag."""
    derived = results.get_derived_params()
    rs = derived['rstar']  # sound horizon at recombination z*

    z_star = derived['zstar']
    DA_star = results.angular_diameter_distance(z_star)
    DM_star = DA_star * (1 + z_star)  # comoving distance
    l_A = np.pi * DM_star / rs

    # Shift parameter: R = sqrt(Omega_m) * H0 * DM(z*) / c
    H0_val = results.hubble_parameter(0)
    R = np.sqrt(Omega_m) * H0_val * DM_star / 299792.458

    wb = ombh2  # fixed

    delta = np.array([l_A - planck_la, R - planck_R, wb - planck_wb])
    chi2 = delta @ cov_planck_inv @ delta
    return chi2, l_A, R


def chi2_desi_y1(results):
    """Compute chi2 for DESI Year 1 BAO."""
    derived = results.get_derived_params()
    rd = derived['rdrag']
    c_km_s = 299792.458

    chi2 = 0
    for z_eff, mtype, val, sigma in desi_y1_bao:
        if mtype == 'DV':
            DM = results.comoving_radial_distance(z_eff)
            Hz = results.hubble_parameter(z_eff)
            DH = c_km_s / Hz
            DV = (z_eff * DM**2 * DH)**(1./3.) / rd
            chi2 += ((DV - val) / sigma)**2
        elif mtype == 'DM':
            DM = results.comoving_radial_distance(z_eff) / rd
            chi2 += ((DM - val) / sigma)**2
        elif mtype == 'DH':
            Hz = results.hubble_parameter(z_eff)
            DH = c_km_s / (Hz * rd)
            chi2 += ((DH - val) / sigma)**2
    return chi2


# ============================================================
# 1. Boltzmann scan: chi2(zeta0)
# ============================================================
def boltzmann_scan(n_points=200):
    print("=" * 60)
    print("1. BOLTZMANN SCAN: chi2(zeta0)")
    print("=" * 60)

    zeta0_arr = np.logspace(-4, -1, n_points)
    chi2_total = np.zeros(n_points)
    chi2_cmb = np.zeros(n_points)
    chi2_bao = np.zeros(n_points)
    w0_arr = np.zeros(n_points)
    rd_arr = np.zeros(n_points)

    for i, z0 in enumerate(zeta0_arr):
        w0 = w0_from_zeta0(z0)
        w0_arr[i] = w0

        if w0 < -0.999:
            w0 = -0.999  # CAMB can't handle exactly -1

        try:
            results = get_camb_results(w0)
            c2_cmb, _, _ = chi2_planck_compressed(results)
            c2_bao = chi2_desi_y1(results)
            chi2_cmb[i] = c2_cmb
            chi2_bao[i] = c2_bao
            chi2_total[i] = c2_cmb + c2_bao
            rd_arr[i] = results.get_derived_params()['rdrag']
        except Exception as e:
            chi2_total[i] = 1e6
            chi2_cmb[i] = 1e6
            chi2_bao[i] = 1e6
            print(f"  CAMB error at zeta0={z0:.2e}, w0={w0:.4f}: {e}")

        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{n_points} done (zeta0={z0:.2e}, w0={w0:.4f}, chi2={chi2_total[i]:.1f})")

    # Find best fit
    idx_best = np.argmin(chi2_total)
    z0_best = zeta0_arr[idx_best]
    w0_best = w0_arr[idx_best]
    chi2_min = chi2_total[idx_best]

    print(f"\nBest fit: zeta0 = {z0_best:.4e}, w0 = {w0_best:.4f}")
    print(f"  chi2_min = {chi2_min:.2f} (CMB: {chi2_cmb[idx_best]:.2f}, BAO: {chi2_bao[idx_best]:.2f})")
    print(f"  r_d = {rd_arr[idx_best]:.2f} Mpc")

    # 1-sigma bounds (Delta chi2 = 1)
    mask_1s = chi2_total < chi2_min + 1
    if np.any(mask_1s):
        z0_lo = zeta0_arr[mask_1s].min()
        z0_hi = zeta0_arr[mask_1s].max()
        print(f"  1-sigma: zeta0 in [{z0_lo:.4e}, {z0_hi:.4e}]")
        print(f"           w0 in [{w0_from_zeta0(z0_hi):.4f}, {w0_from_zeta0(z0_lo):.4f}]")

    # 2-sigma bounds (Delta chi2 = 4)
    mask_2s = chi2_total < chi2_min + 4
    if np.any(mask_2s):
        z0_lo2 = zeta0_arr[mask_2s].min()
        z0_hi2 = zeta0_arr[mask_2s].max()
        print(f"  2-sigma: zeta0 in [{z0_lo2:.4e}, {z0_hi2:.4e}]")

    # JC benchmark
    idx_jc = np.argmin(np.abs(zeta0_arr - 9.64e-4))
    print(f"\nJC benchmark (zeta0 = 9.64e-4):")
    print(f"  chi2 = {chi2_total[idx_jc]:.1f}, Delta_chi2 = {chi2_total[idx_jc] - chi2_min:+.1f}")
    print(f"  chi2_CMB = {chi2_cmb[idx_jc]:.1f}, chi2_BAO = {chi2_bao[idx_jc]:.1f}")

    # LCDM comparison
    try:
        results_lcdm = get_camb_results(-1.0 + 1e-6)
        c2_cmb_lcdm, _, _ = chi2_planck_compressed(results_lcdm)
        c2_bao_lcdm = chi2_desi_y1(results_lcdm)
        print(f"\nLCDM: chi2 = {c2_cmb_lcdm + c2_bao_lcdm:.1f} (CMB: {c2_cmb_lcdm:.1f}, BAO: {c2_bao_lcdm:.1f})")
        print(f"  Delta_chi2(best-fit vs LCDM) = {chi2_min - (c2_cmb_lcdm + c2_bao_lcdm):.1f}")
    except Exception as e:
        print(f"LCDM evaluation failed: {e}")

    return {
        'zeta0': zeta0_arr.tolist(),
        'w0': w0_arr.tolist(),
        'chi2_total': chi2_total.tolist(),
        'chi2_cmb': chi2_cmb.tolist(),
        'chi2_bao': chi2_bao.tolist(),
        'rd': rd_arr.tolist(),
        'best_fit': {
            'zeta0': float(z0_best), 'w0': float(w0_best),
            'chi2': float(chi2_min)
        }
    }


# ============================================================
# 2. BAO distance tables (DESI DR2 redshifts)
# ============================================================
def bao_distance_tables():
    print("\n" + "=" * 60)
    print("2. BAO DISTANCE TABLES (DESI DR2)")
    print("=" * 60)

    z_arr = [t['z'] for t in desi_dr2_tracers]
    names = [t['name'] for t in desi_dr2_tracers]

    benchmarks = {
        'LCDM': -1.0 + 1e-6,
        'Meridian_JC': w0_from_zeta0(9.64e-4),
        'Meridian_CMB': w0_from_zeta0(0.037),
        'CPL_w0': -0.75,  # for comparison (constant-w approximation)
    }

    results = {}
    for label, w0 in benchmarks.items():
        print(f"\n  Computing {label} (w0 = {w0:.4f})...")
        try:
            res = get_camb_results(w0)
            DM_rd, DH_rd, rd = get_distances(res, z_arr)
            results[label] = {
                'w0': w0, 'rd': rd,
                'DM_rd': DM_rd.tolist(),
                'DH_rd': DH_rd.tolist()
            }
            print(f"    r_d = {rd:.2f} Mpc")
        except Exception as e:
            print(f"    Error: {e}")

    # Print comparison table
    if 'LCDM' in results and 'Meridian_JC' in results:
        print("\n  DM/rd comparison (JC benchmark vs LCDM):")
        print(f"  {'Tracer':<12} {'z':>5} {'LCDM':>10} {'Meridian':>10} {'delta%':>8}")
        for i, (name, z) in enumerate(zip(names, z_arr)):
            dm_lcdm = results['LCDM']['DM_rd'][i]
            dm_mer = results['Meridian_JC']['DM_rd'][i]
            delta = 100 * (dm_mer - dm_lcdm) / dm_lcdm
            print(f"  {name:<12} {z:>5.3f} {dm_lcdm:>10.4f} {dm_mer:>10.4f} {delta:>+8.3f}%")

        print(f"\n  DH/rd comparison (JC benchmark vs LCDM):")
        print(f"  {'Tracer':<12} {'z':>5} {'LCDM':>10} {'Meridian':>10} {'delta%':>8}")
        for i, (name, z) in enumerate(zip(names, z_arr)):
            dh_lcdm = results['LCDM']['DH_rd'][i]
            dh_mer = results['Meridian_JC']['DH_rd'][i]
            delta = 100 * (dh_mer - dh_lcdm) / dh_lcdm
            print(f"  {name:<12} {z:>5.3f} {dh_lcdm:>10.4f} {dh_mer:>10.4f} {delta:>+8.3f}%")

    return results


# ============================================================
# 3. CMB benchmark table
# ============================================================
def cmb_benchmark_table():
    print("\n" + "=" * 60)
    print("3. CMB BENCHMARK TABLE")
    print("=" * 60)

    benchmarks = [
        ('LCDM',      0.1,    -1.0 + 1e-6),
        ('CAMB',      0.022,  w0_from_zeta0(0.022)),
        ('JC',        9.64e-4, w0_from_zeta0(9.64e-4)),
        ('JC_exact',  9.64e-4, w0_exact_from_zeta0(9.64e-4)),
    ]

    # For each benchmark, find H0 that preserves CMB angular diameter distance
    print(f"\n  {'Benchmark':<12} {'zeta0':>10} {'w0':>8} {'H0':>8} {'chi2_CMB':>10} {'chi2_BAO':>10}")
    print("  " + "-" * 62)

    for label, z0, w0 in benchmarks:
        if w0 < -0.999:
            w0 = -0.999

        # First compute with fiducial H0
        try:
            res = get_camb_results(w0, H0=H0_fid)
            c2_cmb, l_A, R = chi2_planck_compressed(res)
            c2_bao = chi2_desi_y1(res)
            rd = res.get_derived_params()['rdrag']
            print(f"  {label:<12} {z0:>10.2e} {w0:>8.4f} {H0_fid:>8.2f} {c2_cmb:>10.2f} {c2_bao:>10.2f}  rd={rd:.2f}")
        except Exception as e:
            print(f"  {label:<12} Error: {e}")

    # Now find optimal H0 for JC benchmark (minimize chi2_CMB)
    print("\n  Finding H0 that minimizes CMB chi2 at JC benchmark...")
    w0_jc = w0_from_zeta0(9.64e-4)

    def cmb_chi2_for_H0(H0_try):
        try:
            res = get_camb_results(w0_jc, H0=H0_try)
            c2, _, _ = chi2_planck_compressed(res)
            return c2
        except:
            return 1e6

    result = minimize_scalar(cmb_chi2_for_H0, bounds=(55, 75), method='bounded')
    H0_opt = result.x
    res_opt = get_camb_results(w0_jc, H0=H0_opt)
    c2_cmb_opt, l_A_opt, R_opt = chi2_planck_compressed(res_opt)
    c2_bao_opt = chi2_desi_y1(res_opt)

    print(f"  Optimal H0 = {H0_opt:.2f} km/s/Mpc")
    print(f"  chi2_CMB = {c2_cmb_opt:.2f}, chi2_BAO = {c2_bao_opt:.2f}")
    print(f"  l_A = {l_A_opt:.3f}, R = {R_opt:.4f}")

    return {
        'JC_optimal_H0': H0_opt,
        'JC_chi2_CMB': c2_cmb_opt,
        'JC_chi2_BAO': c2_bao_opt,
    }


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print("Meridian Monograph — CAMB Refit")
    print(f"C_KK = {C_KK:.2e} ± {C_KK_err:.2e}")
    print(f"eps1 = {eps1} ± {eps1_err}")
    print(f"JC benchmark: zeta0 = 9.64e-4, w0(pert) = {w0_from_zeta0(9.64e-4):.4f}, w0(exact) = {w0_exact_from_zeta0(9.64e-4):.4f}")
    print(f"CMB benchmark: zeta0 = 0.037, w0(pert) = {w0_from_zeta0(0.037):.4f}")
    print()

    outdir = os.path.dirname(os.path.abspath(__file__))

    # Run all analyses
    scan_results = boltzmann_scan(n_points=150)
    distance_results = bao_distance_tables()
    cmb_results = cmb_benchmark_table()

    # Save results
    all_results = {
        'parameters': {
            'C_KK': C_KK, 'C_KK_err': C_KK_err,
            'eps1': eps1, 'eps1_err': eps1_err,
            'H0': H0_fid, 'Omega_m': Omega_m,
        },
        'boltzmann_scan': scan_results,
        'distances': {k: v for k, v in distance_results.items()},
        'cmb_benchmarks': cmb_results,
    }

    outfile = os.path.join(outdir, 'camb_refit_results.json')
    with open(outfile, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {outfile}")
