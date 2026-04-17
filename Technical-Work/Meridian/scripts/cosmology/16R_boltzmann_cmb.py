#!/usr/bin/env python3
"""
Track 16R: mu(a) Boltzmann Code for CMB Constraint on zeta0
Project Meridian -- Phase 16

Uses CAMB to compute CMB + BAO observables for the Meridian dark energy model
  w0(zeta0) = -1 + C_KK / zeta0
and constrains zeta0 using Planck 2018 compressed likelihood + DESI BAO.

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: March 19, 2026
"""

import numpy as np
import camb
from scipy.optimize import minimize_scalar, minimize
from scipy.stats import chi2 as chi2_dist
import json
import os

# ============================================================
# CONSTANTS
# ============================================================

# CKK from 13F Monte Carlo
C_KK_CENTRAL = 2.528e-4
C_KK_SIGMA = 8.61e-5

# Planck 2018 baseline cosmology (TT,TE,EE+lowE+lensing)
H0_PLANCK = 67.36
OMB_H2 = 0.02237
OMC_H2 = 0.1200
TAU = 0.0544
AS = 2.1e-9
NS = 0.9649

# Derived
OM_TOTAL = (OMB_H2 + OMC_H2) / (H0_PLANCK / 100.0)**2  # Ω_m
OM_DE = 1.0 - OM_TOTAL  # Ω_DE (flat universe)

print(f"Planck 2018 baseline: H0={H0_PLANCK}, Om={OM_TOTAL:.4f}, ODE={OM_DE:.4f}")

# ============================================================
# PLANCK 2018 COMPRESSED CMB LIKELIHOOD
# ============================================================
# From Chen, Kumar, Ratra (2024, arXiv:2311.13062) Table I
# Based on Planck 2018 TT,TE,EE+lowE

# CMB distance priors (observed values)
LA_OBS = 301.471     # acoustic scale l_A = π d_A(z*)/r_s(z*)
R_OBS = 1.7502       # shift parameter R = √(Ω_m) d_L(z*) H₀/c  [at z*]
WB_OBS = 0.02237     # ω_b = Ω_b h²

# Inverse covariance matrix for (l_A, R, ω_b)
# From Planck 2018 compressed likelihood (Chen et al. 2024)
# sig_lA = 0.090, sig_R = 0.0046, sig_wb = 0.00015
# Correlation coefficients from Planck chains:
#   rho(lA, R) = 0.46, rho(lA, wb) = -0.66, rho(R, wb) = -0.33
_sig = np.array([0.090, 0.0046, 0.00015])
_rho = np.array([
    [ 1.00,  0.46, -0.66],
    [ 0.46,  1.00, -0.33],
    [-0.66, -0.33,  1.00],
])
COV_CMB = np.outer(_sig, _sig) * _rho
# Invert for chi² calculation
COV_CMB_INV = np.linalg.inv(COV_CMB)


# ============================================================
# DESI BAO DATA (Year 1, 2024)
# ============================================================
# From DESI Collaboration (arXiv:2404.03002)
# D_V/r_d, D_M/r_d, D_H/r_d measurements

DESI_BAO = [
    # (z_eff, quantity, value, sigma, type)
    # BGS
    (0.295, 'DV_rd', 7.93, 0.15),
    # LRG1
    (0.510, 'DM_rd', 13.62, 0.25),
    (0.510, 'DH_rd', 20.98, 0.61),
    # LRG2
    (0.706, 'DM_rd', 16.85, 0.32),
    (0.706, 'DH_rd', 20.08, 0.60),
    # LRG3 + ELG1
    (0.930, 'DM_rd', 21.71, 0.28),
    (0.930, 'DH_rd', 17.88, 0.35),
    # ELG2
    (1.317, 'DM_rd', 27.79, 0.69),
    (1.317, 'DH_rd', 13.82, 0.42),
    # Lya QSO
    (2.330, 'DM_rd', 39.71, 0.94),
    (2.330, 'DH_rd', 8.52, 0.17),
]


# ============================================================
# CAMB INTERFACE
# ============================================================

def get_camb_results(w0, wa=0.0):
    """Compute CMB and BAO observables for given dark energy parameters."""
    pars = camb.CAMBparams()
    pars.set_cosmology(
        H0=H0_PLANCK,
        ombh2=OMB_H2,
        omch2=OMC_H2,
        tau=TAU,
    )
    pars.InitPower.set_params(As=AS, ns=NS)

    # Set dark energy equation of state
    pars.set_dark_energy(w=w0, wa=wa, dark_energy_model='fluid')

    # We need background quantities, not full CMB spectra
    pars.WantCls = False
    pars.WantTransfer = False
    pars.set_accuracy(AccuracyBoost=1.0)

    try:
        results = camb.get_background(pars)
    except camb.CAMBError as e:
        return None

    return pars, results


def compute_cmb_distances(w0, wa=0.0):
    """Compute the CMB distance priors (l_A, R, ω_b) for given w0, wa."""
    out = get_camb_results(w0, wa)
    if out is None:
        return None

    pars, results = out

    # Recombination redshift
    zstar = results.get_derived_params()['zstar']

    # Comoving angular diameter distance to z*
    # CAMB gives comoving distances
    DA_star = results.comoving_radial_distance(zstar)  # Mpc

    # Sound horizon at z*
    rs_star = results.get_derived_params()['rstar']  # Mpc

    # Acoustic scale
    la = np.pi * DA_star / rs_star

    # Shift parameter R = √(Ω_m H₀²/c²) * d_A(z*)
    # With H₀ in km/s/Mpc and d_A in Mpc:
    # R = √(Ω_m) * H₀/c * d_A(z*)
    h = H0_PLANCK / 100.0
    c_km_s = 299792.458  # km/s
    R = np.sqrt(OM_TOTAL) * (H0_PLANCK / c_km_s) * DA_star

    return la, R, OMB_H2, zstar, rs_star


def compute_bao_distances(w0, wa=0.0):
    """Compute BAO distance ratios D_V/r_d, D_M/r_d, D_H/r_d at DESI redshifts."""
    out = get_camb_results(w0, wa)
    if out is None:
        return None

    pars, results = out

    # Sound horizon at drag epoch
    rd = results.get_derived_params()['rdrag']  # Mpc

    c_km_s = 299792.458  # km/s
    bao_pred = []

    for z_eff, qtype, val, sig in DESI_BAO:
        DM = results.comoving_radial_distance(z_eff)  # Mpc
        Hz = results.hubble_parameter(z_eff)  # km/s/Mpc
        DH = c_km_s / Hz  # Mpc

        if qtype == 'DV_rd':
            DV = (z_eff * DM**2 * DH)**(1./3.)
            pred = DV / rd
        elif qtype == 'DM_rd':
            pred = DM / rd
        elif qtype == 'DH_rd':
            pred = DH / rd

        bao_pred.append(pred)

    return bao_pred, rd


# ============================================================
# CHI-SQUARED
# ============================================================

def chi2_cmb(w0, wa=0.0):
    """CMB compressed likelihood chi²."""
    result = compute_cmb_distances(w0, wa)
    if result is None:
        return 1e10

    la, R, wb, zstar, rs = result
    delta = np.array([la - LA_OBS, R - R_OBS, wb - WB_OBS])
    return float(delta @ COV_CMB_INV @ delta)


def chi2_bao(w0, wa=0.0):
    """DESI BAO chi² (assuming uncorrelated measurements)."""
    result = compute_bao_distances(w0, wa)
    if result is None:
        return 1e10

    bao_pred, rd = result
    chi2 = 0.0
    for i, (z_eff, qtype, val, sig) in enumerate(DESI_BAO):
        chi2 += ((bao_pred[i] - val) / sig)**2

    return chi2


def chi2_total(w0, wa=0.0):
    """Combined CMB + BAO chi²."""
    return chi2_cmb(w0, wa) + chi2_bao(w0, wa)


def w0_from_zeta0(zeta0, c_kk=C_KK_CENTRAL):
    """Convert zeta0 to w0 using the Meridian prediction."""
    if zeta0 <= 0:
        return -100.0  # unphysical
    return -1.0 + c_kk / zeta0


def chi2_from_zeta0(zeta0, c_kk=C_KK_CENTRAL):
    """Combined chi² as a function of zeta0."""
    w0 = w0_from_zeta0(zeta0, c_kk)
    if w0 > 0 or w0 < -3:
        return 1e10  # outside physical range
    return chi2_total(w0)


# ============================================================
# MAIN COMPUTATION
# ============================================================

def main():
    print("=" * 70)
    print("Track 16R: Boltzmann CMB Constraint on zeta0")
    print("=" * 70)

    # Step 1: Validate LCDM baseline
    print("\n--- Step 1: LCDM Baseline ---")
    chi2_lcdm_cmb = chi2_cmb(-1.0)
    chi2_lcdm_bao = chi2_bao(-1.0)
    print(f"  LCDM chi2(CMB)  = {chi2_lcdm_cmb:.3f}")
    print(f"  LCDM chi2(BAO)  = {chi2_lcdm_bao:.3f}")
    print(f"  LCDM chi2(total)= {chi2_lcdm_cmb + chi2_lcdm_bao:.3f}")

    # CMB distances for LCDM
    la, R, wb, zstar, rs = compute_cmb_distances(-1.0)
    print(f"  l_A = {la:.3f}  (obs: {LA_OBS})")
    print(f"  R   = {R:.4f}  (obs: {R_OBS})")
    print(f"  z*  = {zstar:.2f}")
    print(f"  r_s = {rs:.2f} Mpc")

    # BAO distances for LCDM
    bao_pred, rd = compute_bao_distances(-1.0)
    print(f"  r_drag = {rd:.2f} Mpc")
    print(f"\n  BAO comparison (LCDM):")
    for i, (z, qt, val, sig) in enumerate(DESI_BAO):
        pull = (bao_pred[i] - val) / sig
        print(f"    z={z:.3f} {qt}: pred={bao_pred[i]:.2f}, obs={val:.2f}±{sig:.2f}, pull={pull:+.2f}sig")

    # Step 2: Scan w0 for chi² profile
    print("\n--- Step 2: w0 Profile Scan ---")
    w0_grid = np.linspace(-1.3, -0.5, 81)
    chi2_profile = []

    for w0 in w0_grid:
        c2_cmb = chi2_cmb(w0)
        c2_bao = chi2_bao(w0)
        chi2_profile.append((w0, c2_cmb, c2_bao, c2_cmb + c2_bao))

    chi2_profile = np.array(chi2_profile)

    # Find minimum
    idx_min = np.argmin(chi2_profile[:, 3])
    w0_best = chi2_profile[idx_min, 0]
    chi2_min = chi2_profile[idx_min, 3]

    print(f"  Best-fit w0 = {w0_best:.3f}")
    print(f"  chi2_min(total) = {chi2_min:.3f}")
    print(f"  dchi2(LCDM) = {chi2_lcdm_cmb + chi2_lcdm_bao - chi2_min:.3f}")

    # 1sig and 2sig bounds (dchi2 = 1.0 and 4.0 for 1 dof)
    delta_chi2 = chi2_profile[:, 3] - chi2_min
    w0_1sig = w0_grid[delta_chi2 <= 1.0]
    w0_2sig = w0_grid[delta_chi2 <= 4.0]

    if len(w0_1sig) > 0:
        print(f"  1sig range: [{w0_1sig[0]:.3f}, {w0_1sig[-1]:.3f}]")
    if len(w0_2sig) > 0:
        print(f"  2sig range: [{w0_2sig[0]:.3f}, {w0_2sig[-1]:.3f}]")

    # Step 3: zeta0 constraint
    print("\n--- Step 3: zeta0 Constraint (Meridian model) ---")

    # Scan zeta0
    zeta0_grid = np.logspace(-4, -1, 200)
    chi2_zeta = []

    for z0 in zeta0_grid:
        w0 = w0_from_zeta0(z0)
        if w0 > 0 or w0 < -3:
            chi2_zeta.append(1e10)
            continue
        chi2_zeta.append(chi2_total(w0))

    chi2_zeta = np.array(chi2_zeta)

    # Find minimum in zeta0
    idx_min_z = np.argmin(chi2_zeta)
    zeta0_best = zeta0_grid[idx_min_z]
    chi2_min_z = chi2_zeta[idx_min_z]
    w0_at_best = w0_from_zeta0(zeta0_best)

    print(f"  Best-fit zeta0 = {zeta0_best:.6f}")
    print(f"  Best-fit w0 = {w0_at_best:.4f}")
    print(f"  chi2_min = {chi2_min_z:.3f}")

    # dchi2 relative to LCDM (zeta0 → ∞ limit)
    chi2_lcdm_total = chi2_lcdm_cmb + chi2_lcdm_bao
    delta_vs_lcdm = chi2_lcdm_total - chi2_min_z
    print(f"  dchi2(LCDM - Meridian) = {delta_vs_lcdm:.3f}")
    if delta_vs_lcdm > 0:
        print(f"  Meridian preferred over LCDM by dchi2 = {delta_vs_lcdm:.1f}")
    else:
        print(f"  LCDM preferred over Meridian by dchi2 = {-delta_vs_lcdm:.1f}")

    # Upper bound on zeta0 (where chi² starts rising — i.e., lower bound on |1+w0|)
    # 95% CL upper bound: find where dchi2 = 3.84 (1 dof, one-sided)
    delta_chi2_z = chi2_zeta - chi2_min_z

    # Find 1sig and 2sig bounds
    zeta0_1sig_mask = delta_chi2_z <= 1.0
    zeta0_2sig_mask = delta_chi2_z <= 3.84

    zeta0_1sig = zeta0_grid[zeta0_1sig_mask]
    zeta0_2sig = zeta0_grid[zeta0_2sig_mask]

    if len(zeta0_1sig) > 0:
        print(f"  1sig range: [{zeta0_1sig[0]:.6f}, {zeta0_1sig[-1]:.6f}]")
        print(f"    → w0 range: [{w0_from_zeta0(zeta0_1sig[0]):.4f}, {w0_from_zeta0(zeta0_1sig[-1]):.4f}]")
    if len(zeta0_2sig) > 0:
        print(f"  95% CL range: [{zeta0_2sig[0]:.6f}, {zeta0_2sig[-1]:.6f}]")
        print(f"    → w0 range: [{w0_from_zeta0(zeta0_2sig[0]):.4f}, {w0_from_zeta0(zeta0_2sig[-1]):.4f}]")

    # Step 4: Key benchmark evaluation
    print("\n--- Step 4: Benchmark Evaluation ---")

    benchmarks = [
        ("Brane benchmark", 9.64e-4),
        ("DESI center",     1.0e-3),
        ("CMB (HK approx)", 0.037),
        ("Conservative",    0.005),
    ]

    for name, z0 in benchmarks:
        w0 = w0_from_zeta0(z0)
        c2 = chi2_total(w0)
        delta = c2 - chi2_min_z
        delta_vs_lcdm_bm = c2 - chi2_lcdm_total
        sigma = np.sqrt(max(0, delta)) if delta > 0 else 0
        print(f"  {name:20s}: zeta0={z0:.6f}, w0={w0:.4f}, "
              f"dchi2(vs best)={delta:.2f} ({sigma:.1f}sig), "
              f"dchi2(vs LCDM)={delta_vs_lcdm_bm:+.2f}")

    # Step 5: Comparison — HK approximate vs CAMB proper
    print("\n--- Step 5: HK Approximate vs CAMB Proper ---")
    print("  The HK constraint used β_HK = -0.037 ± 0.0095")
    print(f"  → zeta0(HK) = 0.037 ± 0.010, w0(HK) = -0.993 ± 0.005")

    if len(zeta0_2sig) > 0:
        print(f"  → zeta0(CAMB 95%) = [{zeta0_2sig[0]:.4f}, {zeta0_2sig[-1]:.4f}]")
        w_lo = w0_from_zeta0(zeta0_2sig[0])
        w_hi = w0_from_zeta0(zeta0_2sig[-1])
        print(f"  → w0(CAMB 95%) = [{w_lo:.4f}, {w_hi:.4f}]")

    # Step 6: Save results
    print("\n--- Step 6: Saving Results ---")

    results_dict = {
        "C_KK": C_KK_CENTRAL,
        "C_KK_sigma": C_KK_SIGMA,
        "LCDM_chi2_cmb": float(chi2_lcdm_cmb),
        "LCDM_chi2_bao": float(chi2_lcdm_bao),
        "LCDM_chi2_total": float(chi2_lcdm_total),
        "w0_best_fit": float(w0_best),
        "w0_chi2_min": float(chi2_min),
        "zeta0_best_fit": float(zeta0_best),
        "zeta0_w0_best": float(w0_at_best),
        "zeta0_chi2_min": float(chi2_min_z),
        "delta_chi2_vs_LCDM": float(delta_vs_lcdm),
    }

    if len(zeta0_1sig) > 0:
        results_dict["zeta0_1sig_lo"] = float(zeta0_1sig[0])
        results_dict["zeta0_1sig_hi"] = float(zeta0_1sig[-1])
    if len(zeta0_2sig) > 0:
        results_dict["zeta0_95CL_lo"] = float(zeta0_2sig[0])
        results_dict["zeta0_95CL_hi"] = float(zeta0_2sig[-1])

    # Save w0 profile
    results_dict["w0_profile"] = [
        {"w0": float(r[0]), "chi2_cmb": float(r[1]),
         "chi2_bao": float(r[2]), "chi2_total": float(r[3])}
        for r in chi2_profile
    ]

    # Save zeta0 profile
    results_dict["zeta0_profile"] = [
        {"zeta0": float(z), "chi2": float(c)}
        for z, c in zip(zeta0_grid, chi2_zeta) if c < 1e9
    ]

    outpath = os.path.join(os.path.dirname(__file__), "16R_results.json")
    with open(outpath, 'w') as f:
        json.dump(results_dict, f, indent=2)
    print(f"  Results saved to {outpath}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  LCDM:     chi2 = {chi2_lcdm_total:.2f}")
    print(f"  Best w0:  w0 = {w0_best:.3f}, chi2 = {chi2_min:.2f}")
    print(f"  Best zeta0:  zeta0 = {zeta0_best:.6f}, w0 = {w0_at_best:.4f}, chi2 = {chi2_min_z:.2f}")
    print(f"  dchi2(LCDM - best) = {delta_vs_lcdm:.2f}")
    if len(zeta0_2sig) > 0:
        print(f"  95% CL: zeta0 ∈ [{zeta0_2sig[0]:.5f}, {zeta0_2sig[-1]:.5f}]")
    brane_chi2 = chi2_from_zeta0(9.64e-4)
    brane_delta = brane_chi2 - chi2_lcdm_total
    print(f"  Brane benchmark (zeta0=9.64×10⁻⁴, w0=-0.746): dchi2(vs LCDM) = {brane_delta:+.2f}")

    if brane_delta < 4.0:
        print("  → Brane benchmark is WITHIN 2sig of LCDM")
    elif brane_delta < 9.0:
        print("  → Brane benchmark is at 2-3sig tension with CMB+BAO")
    else:
        print("  → Brane benchmark is EXCLUDED at >3sig by CMB+BAO")

    print("\n" + "=" * 70)
    return results_dict


if __name__ == "__main__":
    results = main()
