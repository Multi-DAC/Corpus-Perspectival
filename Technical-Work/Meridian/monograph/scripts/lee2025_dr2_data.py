"""
DESI DR2 BAO data with Lee 2025 covariance matrices.

Source: S. Lee, arXiv:2507.01380v2 (2025), Section III.B.
Covariance blocks are from Eq. (16) and the explicit numerical values
following it. We use the (DM/rd, DH/rd) basis [C^(2) blocks] to avoid
double-counting with DV/rd.

BGS (z=0.295) provides only DV/rd — treated as a single scalar measurement.
The remaining 6 tracers provide (DM/rd, DH/rd) pairs: 12 measurements.
Total: 13 independent observables (1 + 6×2).
"""

import numpy as np

# ============================================================
# DESI DR2 BAO central values
# From DESI DR2 Key Paper (Ref. [8] in Lee 2025)
# ============================================================

# BGS: only DV/rd
bgs = {
    'z_eff': 0.295,
    'DV_rd': 7.93,
    'DV_rd_sigma': 0.075,  # sqrt(0.005625)
}

# Anisotropic tracers: (DM/rd, DH/rd) pairs
# Central values from existing camb_multiprobe.py (DESI DR2 published)
tracers = [
    {'name': 'LRG1',       'z_eff': 0.510, 'DM_rd': 13.62, 'DH_rd': 22.33},
    {'name': 'LRG2',       'z_eff': 0.706, 'DM_rd': 17.86, 'DH_rd': 20.08},
    {'name': 'LRG3+ELG1',  'z_eff': 0.934, 'DM_rd': 21.71, 'DH_rd': 17.88},
    {'name': 'ELG2',        'z_eff': 1.321, 'DM_rd': 27.79, 'DH_rd': 13.82},
    {'name': 'QSO',         'z_eff': 1.484, 'DM_rd': 29.34, 'DH_rd': 13.12},
    {'name': 'Lya',         'z_eff': 2.330, 'DM_rd': 39.71, 'DH_rd':  8.52},
]

# ============================================================
# Lee 2025 covariance matrices — C^(2) blocks (DM/rd, DH/rd basis)
# Each is a 2x2 matrix: [[sigma_DM^2, rho*sigma_DM*sigma_DH],
#                         [rho*sigma_DM*sigma_DH, sigma_DH^2]]
# ============================================================

# BGS: scalar variance for DV/rd
cov_bgs = np.array([[0.005625]])

# LRG1 (z=0.510)
cov_lrg1 = np.array([
    [2.788900e-2, -3.257752e-2],
    [-3.257752e-2, 1.806250e-1],
])

# LRG2 (z=0.706)
cov_lrg2 = np.array([
    [3.132900e-2, -2.359764e-2],
    [-2.359764e-2, 1.089000e-1],
])

# LRG3+ELG1 (z=0.934)
cov_lrg3_elg1 = np.array([
    [2.310400e-2, -1.220377e-2],
    [-1.220377e-2, 3.724900e-2],
])

# ELG2 (z=1.321)
cov_elg2 = np.array([
    [1.01124e-1, -3.050065e-2],
    [-3.050065e-2, 4.8841e-2],
])

# QSO (z=1.484)
cov_qso = np.array([
    [5.7760e-1, -1.9608e-1],
    [-1.9608e-1, 2.66256e-1],
])

# Lya (z=2.330)
cov_lya = np.array([
    [2.81961e-1, -2.311496e-2],
    [-2.311496e-2, 1.0201e-2],
])

# Ordered list matching tracers[]
cov_blocks = [cov_lrg1, cov_lrg2, cov_lrg3_elg1, cov_elg2, cov_qso, cov_lya]

# Pre-compute inverse covariance blocks
cov_inv_blocks = [np.linalg.inv(c) for c in cov_blocks]
cov_inv_bgs = 1.0 / cov_bgs[0, 0]

# ============================================================
# Reference chi2 values from Lee 2025 Table I
# (for validation of our computation)
# ============================================================
lee2025_reference = {
    'LCDM': {
        'Omega_m': 0.2949,
        'hrd': 101.80,
        'chi2_min': 10.150,
        'dof': 10,
        'chi2_reduced': 1.015,
    },
    'wCDM': {
        'w0': -0.918,
        'Omega_m': 0.2964,
        'hrd': 99.87,
        'chi2_min': 9.470,
        'dof': 9,
        'chi2_reduced': 1.052,
    },
}
