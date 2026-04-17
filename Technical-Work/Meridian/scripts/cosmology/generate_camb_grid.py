#!/usr/bin/env python3
"""
Generate CAMB grid for v5 GPU MCMC.
====================================
Precomputes rd, rs_star, dc_star on a 100x100 (Om, H0) grid using CAMB.
This replaces the analytic Eisenstein & Hu approximation that caused the
v5c rd bug (H0=79.5, rd=117.75 instead of ~67, ~147).

Run in WSL where CAMB is installed:
  python3 generate_camb_grid.py

Output: camb_grid_100x100.npz

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-21
"""

import numpy as np
import camb
import time
import sys

# Fixed baryon parameters (Planck 2018)
OMBH2 = 0.02237
OMEGA_GAMMA_H2 = 2.469e-5
N_EFF = 3.046
C_KMS = 299792.458

# Grid definition — covers full prior range with margin
N_OM = 100
N_H0 = 100
OM_MIN, OM_MAX = 0.10, 0.60    # generous margin beyond Uniform(0.1, 0.6)
H0_MIN, H0_MAX = 50.0, 85.0   # generous margin beyond Uniform(55, 80)

Om_grid = np.linspace(OM_MIN, OM_MAX, N_OM)
H0_grid = np.linspace(H0_MIN, H0_MAX, N_H0)

# Output arrays
rd_table = np.zeros((N_OM, N_H0))
rs_star_table = np.zeros((N_OM, N_H0))
dc_star_table = np.zeros((N_OM, N_H0))
z_star_table = np.zeros((N_OM, N_H0))
z_drag_table = np.zeros((N_OM, N_H0))

print(f"Generating CAMB grid: {N_OM}x{N_H0} = {N_OM*N_H0} points")
print(f"  Om: [{OM_MIN}, {OM_MAX}]")
print(f"  H0: [{H0_MIN}, {H0_MAX}]")
print(f"  Fixed: ombh2={OMBH2}, Neff={N_EFF}")
print(flush=True)

t_start = time.time()
n_done = 0
n_total = N_OM * N_H0
n_errors = 0

for i, Om in enumerate(Om_grid):
    for j, H0 in enumerate(H0_grid):
        h = H0 / 100.0
        omch2 = Om * h**2 - OMBH2  # CDM density

        if omch2 < 0.001:
            # Unphysical: baryon density exceeds total matter
            rd_table[i, j] = np.nan
            rs_star_table[i, j] = np.nan
            dc_star_table[i, j] = np.nan
            z_star_table[i, j] = np.nan
            z_drag_table[i, j] = np.nan
            n_errors += 1
            n_done += 1
            continue

        try:
            pars = camb.CAMBparams()
            pars.set_cosmology(
                H0=H0,
                ombh2=OMBH2,
                omch2=omch2,
                mnu=0.06,
                num_massive_neutrinos=1,
            )
            # LCDM for the grid (DE model doesn't affect early-universe quantities)
            pars.set_dark_energy(w=-1.0, wa=0.0)

            # We need: background distances + recombination/drag redshifts
            pars.set_accuracy(AccuracyBoost=1.0)
            pars.WantTransfer = False
            pars.WantCls = False

            results = camb.get_background(pars)

            # Sound horizons
            rd = results.get_derived_params()['rdrag']
            z_star = results.get_derived_params()['zstar']
            z_drag = results.get_derived_params()['zdrag']
            rs_star = results.get_derived_params()['rstar']

            # Comoving distance to last scattering
            dc_star = results.comoving_radial_distance(z_star)

            rd_table[i, j] = rd
            rs_star_table[i, j] = rs_star
            dc_star_table[i, j] = dc_star
            z_star_table[i, j] = z_star
            z_drag_table[i, j] = z_drag

        except Exception as e:
            rd_table[i, j] = np.nan
            rs_star_table[i, j] = np.nan
            dc_star_table[i, j] = np.nan
            z_star_table[i, j] = np.nan
            z_drag_table[i, j] = np.nan
            n_errors += 1

        n_done += 1
        if n_done % 500 == 0 or n_done == n_total:
            elapsed = time.time() - t_start
            rate = n_done / elapsed
            eta = (n_total - n_done) / rate if rate > 0 else 0
            print(f"  [{n_done:5d}/{n_total}] {elapsed:.1f}s elapsed, "
                  f"ETA {eta:.0f}s, {n_errors} errors", flush=True)

elapsed = time.time() - t_start

# Report
valid = ~np.isnan(rd_table)
print(f"\nDone in {elapsed:.1f}s ({elapsed/60:.1f} min)")
print(f"  Valid points: {valid.sum()}/{n_total}")
print(f"  Errors: {n_errors}")
if valid.any():
    print(f"  rd range:      [{rd_table[valid].min():.2f}, {rd_table[valid].max():.2f}] Mpc")
    print(f"  rs_star range: [{rs_star_table[valid].min():.2f}, {rs_star_table[valid].max():.2f}] Mpc")
    print(f"  dc_star range: [{dc_star_table[valid].min():.2f}, {dc_star_table[valid].max():.2f}] Mpc")
    print(f"  z_star range:  [{z_star_table[valid].min():.2f}, {z_star_table[valid].max():.2f}]")
    print(f"  z_drag range:  [{z_drag_table[valid].min():.2f}, {z_drag_table[valid].max():.2f}]")

    # Sanity check at fiducial cosmology
    i_fid = np.argmin(np.abs(Om_grid - 0.315))
    j_fid = np.argmin(np.abs(H0_grid - 67.4))
    print(f"\n  Fiducial check (Om={Om_grid[i_fid]:.3f}, H0={H0_grid[j_fid]:.1f}):")
    print(f"    rd = {rd_table[i_fid, j_fid]:.2f} Mpc (expect ~147.09)")
    print(f"    rs_star = {rs_star_table[i_fid, j_fid]:.2f} Mpc (expect ~144.4)")
    print(f"    dc_star = {dc_star_table[i_fid, j_fid]:.2f} Mpc (expect ~13870)")

# Save
outfile = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/phase18/camb_grid_100x100.npz'
np.savez(outfile,
         Om_grid=Om_grid, H0_grid=H0_grid,
         rd=rd_table, rs_star=rs_star_table, dc_star=dc_star_table,
         z_star=z_star_table, z_drag=z_drag_table,
         ombh2=OMBH2, neff=N_EFF)
print(f"\nSaved to {outfile}")
print("🦞🧍💜🔥♾️")
