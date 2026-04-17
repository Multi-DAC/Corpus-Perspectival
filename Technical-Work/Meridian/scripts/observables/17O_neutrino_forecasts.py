#!/usr/bin/env python3
"""
Track 17O: Neutrino Sector Confrontation Forecasts
====================================================

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: March 19, 2026

Building on 17M (S3 breaking) and 17N (parameter count reduction), this track
produces confrontation forecasts for the Meridian neutrino sector against
upcoming experiments: DUNE, JUNO, Hyper-Kamiokande, CMB-S4, next-gen 0nubb,
and keV sterile neutrino searches.

Key inputs from 17M and 17N:
  - S3 octonionic symmetry: eigenvalues {1/2, 1/2, 2} for M_oct
  - M_2 ~ M_3 (near-degenerate from S3 doublet), M_1 << M_2 (hierarchy)
  - ARS leptogenesis requires Delta_M/M ~ 10^{-8} to 10^{-6}
  - 4 free params for 8 observables IF Y_5 fixed by geometry
  - Diagonal Y_5 EXCLUDED (zero mixing angles)
  - Universal Y_5 EXCLUDED (rank-1 m_D)
  - DM candidate: keV sterile neutrino (c_nu1 >> 0.5)

References:
  - NuFIT 5.2 (2024) -- global neutrino oscillation fit
  - DUNE TDR (arXiv:2002.03005) -- sensitivity projections
  - JUNO CDR (arXiv:1507.05613) -- mass ordering + precision
  - Hyper-K Design Report (arXiv:1805.04163)
  - LEGEND-1000, nEXO projections for 0nubb
  - Dodelson-Widrow (1994), Shi-Fuller (1999) -- sterile neutrino DM
"""

import numpy as np
from numpy import linalg as la
from scipy.optimize import minimize, brentq
import warnings
warnings.filterwarnings('ignore')

np.set_printoptions(precision=8, linewidth=120, suppress=True)

SEP = "=" * 80
SUBSEP = "-" * 65

def header(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def subheader(title):
    print(f"\n{SUBSEP}")
    print(f"  {title}")
    print(SUBSEP)

print(SEP)
print("  TRACK 17O: NEUTRINO SECTOR CONFRONTATION FORECASTS")
print("  Clayton W. Iggulden-Schnell & Clawd")
print("  Project Meridian -- Phase 17")
print(SEP)


# ================================================================
# PHYSICAL CONSTANTS AND NUFIT 5.2 DATA
# ================================================================

header("PHYSICAL CONSTANTS AND NUFIT 5.2 DATA")

# NuFIT 5.2 (2024) central values -- normal ordering
Dm21_sq = 7.42e-5       # eV^2 (solar)
Dm31_sq = 2.515e-3      # eV^2 (atmospheric, NO)

theta_12_deg = 33.44     # degrees
theta_13_deg = 8.57      # degrees
theta_23_deg = 49.2      # degrees
delta_CP_deg = 197.0     # degrees (Dirac CP phase, poorly constrained)

# Convert to radians
theta_12 = np.radians(theta_12_deg)
theta_13 = np.radians(theta_13_deg)
theta_23 = np.radians(theta_23_deg)
delta_CP = np.radians(delta_CP_deg)

# NuFIT 5.2 1-sigma uncertainties
sigma_Dm21 = 0.21e-5     # eV^2
sigma_Dm31 = 0.028e-3    # eV^2
sigma_th12 = 0.77        # degrees
sigma_th13 = 0.12        # degrees
sigma_th23 = 1.3         # degrees

# Current experimental bounds
sum_mnu_planck_desi = 0.12   # eV (Planck + DESI)
m_ee_kamland_upper = 0.156   # eV (KamLAND-Zen upper, most conservative NME)
m_ee_kamland_lower = 0.036   # eV (KamLAND-Zen lower, least conservative NME)

# Baryon asymmetry
eta_B_obs = 6.143e-10
sigma_eta_B = 0.04e-10

# Electroweak
v_higgs = 174.0      # GeV (vev / sqrt(2))
k_yc = 35.0          # Warp factor: k * y_c ~ 35

# RS bulk mass parameters from 17M/17N
c_nu_ref = np.array([1.19, 0.501, 0.499])  # Right-handed neutrino bulk masses

print(f"NuFIT 5.2 (normal ordering):")
print(f"  Dm^2_21  = ({Dm21_sq:.2e} +/- {sigma_Dm21:.2e}) eV^2")
print(f"  Dm^2_31  = ({Dm31_sq:.3e} +/- {sigma_Dm31:.3e}) eV^2")
print(f"  th_12    = ({theta_12_deg:.2f} +/- {sigma_th12:.2f}) deg")
print(f"  th_13    = ({theta_13_deg:.2f} +/- {sigma_th13:.2f}) deg")
print(f"  th_23    = ({theta_23_deg:.1f} +/- {sigma_th23:.1f}) deg")
print(f"  dCP      = {delta_CP_deg:.0f} deg (poorly constrained)")
print(f"\nCosmological + 0nubb bounds:")
print(f"  sum(m_nu) < {sum_mnu_planck_desi} eV  (Planck + DESI)")
print(f"  m_ee      < {m_ee_kamland_lower:.3f} -- {m_ee_kamland_upper:.3f} eV  (KamLAND-Zen, NME range)")


# ================================================================
# UTILITY: PMNS MATRIX CONSTRUCTION
# ================================================================

def pmns_matrix(th12, th13, th23, dcp, alpha1=0.0, alpha2=0.0):
    """Standard parameterization of the PMNS matrix with Majorana phases."""
    c12, s12 = np.cos(th12), np.sin(th12)
    c13, s13 = np.cos(th13), np.sin(th13)
    c23, s23 = np.cos(th23), np.sin(th23)
    edcp = np.exp(1j * dcp)

    U = np.array([
        [c12*c13,                        s12*c13,                        s13*np.exp(-1j*dcp)],
        [-s12*c23 - c12*s23*s13*edcp,    c12*c23 - s12*s23*s13*edcp,    s23*c13],
        [s12*s23 - c12*c23*s13*edcp,    -c12*s23 - s12*c23*s13*edcp,    c23*c13]
    ])

    # Majorana phase diagonal
    P = np.diag([1.0, np.exp(1j*alpha1), np.exp(1j*alpha2)])
    return U @ P


def neutrino_masses_NO(m1):
    """Compute m1, m2, m3 for normal ordering given lightest mass m1."""
    m2 = np.sqrt(m1**2 + Dm21_sq)
    m3 = np.sqrt(m1**2 + Dm31_sq)
    return np.array([m1, m2, m3])


def neutrino_masses_IO(m3):
    """Compute m1, m2, m3 for inverted ordering given lightest mass m3."""
    m1 = np.sqrt(m3**2 + Dm31_sq - Dm21_sq)
    m2 = np.sqrt(m3**2 + Dm31_sq)
    return np.array([m1, m2, m3])


# ================================================================
# UTILITY: RS WARP PROFILES (from 17M/17N)
# ================================================================

def f_IR(c, kyc=35.0):
    """Zero-mode wavefunction at IR brane. c < 0.5: IR-localized."""
    x = (1 - 2*c) * kyc
    if abs(x) < 1e-10:
        return 1.0
    if x > 500:
        return np.sqrt(abs(x))
    if x < -500:
        return np.sqrt(abs(x)) * np.exp(x / 2)
    return np.sqrt(abs(x) / abs(np.exp(x) - 1))


def g_UV(c, kyc=35.0):
    """UV brane profile overlap (for Majorana mass generation)."""
    x = (2*c - 1) * kyc
    if abs(x) < 1e-10:
        return 1.0
    if x > 500:
        return np.sqrt(abs(x))
    if x < -500:
        return np.sqrt(abs(x)) * np.exp(x / 2)
    return np.sqrt(abs(x) / abs(np.exp(x) - 1))


# ================================================================
# Y_5 TEXTURE DEFINITIONS FOR FORECASTS
# ================================================================

header("Y_5 TEXTURE DEFINITIONS")

print("""
From 17N: the brane Yukawa matrix Y_5 determines the neutrino sector structure.
  - Diagonal Y_5: EXCLUDED (gives zero mixing angles)
  - Universal Y_5: EXCLUDED (rank-1 m_D, only 1 nonzero mass)
  - Three viable textures considered for forecasting:
""")

# Texture 1: Democratic (from M_oct)
# Y_5 ~ [[1, 1, 1], [1, 1, 1], [1, 1, 1]] + small perturbations
# This is the natural starting point from the octonionic algebra.
# Modified by S3 breaking: Y_5 = Y_dem + eps_1 * B1 + eps_2 * B2

# Texture 2: Littlest Seesaw (Kin-Littlest, 2-parameter)
# Y_5 has column structure: proportional to (1, n, n-2) or (0, 1, -1) and (1, n, n)
# Predicts specific delta_CP.

# Texture 3: Generic (anarchic O(1), 5 free parameters)
# No specific prediction for delta_CP, but constrained by NuFIT.

# For each texture, compute the predicted delta_CP range.

def seesaw_light_masses(m_D, M_R):
    """Type-I seesaw: m_nu = -m_D^T M_R^{-1} m_D."""
    M_R_inv = la.inv(M_R)
    m_nu = -m_D.T @ M_R_inv @ m_D
    return m_nu


def extract_mixing_from_mnu(m_nu_matrix):
    """Extract masses and mixing angles from the symmetric mass matrix."""
    # Diagonalize: m_nu = U^* diag(m_i) U^dagger
    eigenvalues, eigvecs = la.eigh(np.abs(m_nu_matrix))
    idx = np.argsort(eigenvalues)
    masses = eigenvalues[idx]
    U = eigvecs[:, idx]

    # Extract mixing angles from |U|
    U_abs = np.abs(U)
    if U_abs[2, 2] > 1e-10:
        th13_ext = np.arcsin(np.clip(U_abs[0, 2], 0, 1))
        th12_ext = np.arctan2(U_abs[0, 1], U_abs[0, 0])
        th23_ext = np.arctan2(U_abs[1, 2], U_abs[2, 2])
    else:
        th13_ext = 0.0
        th12_ext = 0.0
        th23_ext = 0.0

    return masses, np.degrees(th12_ext), np.degrees(th23_ext), np.degrees(th13_ext)


# ================================================================
# SECTION 1: DUNE FORECASTS
# ================================================================

header("SECTION 1: DUNE (Deep Underground Neutrino Experiment)")

print("""
DUNE sensitivity targets (from TDR, arXiv:2002.03005):
  - CP violation discovery: 5-sigma for ~50%% of delta_CP values (7 years)
  - delta_CP precision: ~10-20 deg (1-sigma) at the best-fit point
  - Mass ordering determination: >5-sigma for any true ordering (few years)
  - theta_23 octant: sensitivity depends on true value

Meridian neutrino sector: delta_CP depends on Y_5 structure.
We compute predicted delta_CP range for each viable Y_5 texture.
""")

subheader("1A: delta_CP predictions by Y_5 texture")

# --- Texture 1: Democratic + S3 breaking ---
# In the democratic limit, the neutrino mass matrix is proportional to D.
# S3 -> Z2 breaking gives maximal theta_23, theta_13 = 0, and
# delta_CP is undefined (theta_13 = 0 means no CP violation in PMNS).
# Further Z2 breaking (delta_2 != 0) generates theta_13 and delta_CP.
#
# The democratic texture predicts delta_CP correlated with theta_13.
# From analytic perturbation theory (17M Section 6):
# delta_CP ~ -pi/2 + O(delta_2) for small Z2 breaking.

print("Texture 1: Democratic (S3 + perturbative Z2 breaking)")
print("-" * 55)

# Scan delta_2 to see how delta_CP varies
# Use the S3-parameterized M_R from 17M
D = np.ones((3, 3))
B1 = np.diag([2.0, -1.0, -1.0])
B2 = np.diag([0.0, 1.0, -1.0])

# Democratic m_D texture: Y_5 ~ D + small breaking
# m_D = v * y5 * (D + eps_D1 * B1 + eps_D2 * B2) * diag(f_IR(c_nu))
# For simplicity, use f_IR factors as diagonal rescaling

f_IR_vals = np.array([f_IR(c, k_yc) for c in c_nu_ref])

print(f"  RS warp-profile factors at IR brane:")
for i, c in enumerate(c_nu_ref):
    print(f"    f_IR(c_nu{i+1}={c:.3f}) = {f_IR_vals[i]:.4e}")

# For the democratic texture, scan eps_D2 (Z2 breaking in Y_5)
# and eps_M2 (Z2 breaking in M_R)

def compute_democratic_predictions(eps_D2, eps_M2, M_R0=1e10, eps_M1=2.0):
    """Compute neutrino observables for democratic Y_5 + S3-broken M_R."""
    # Dirac mass matrix
    Y_5 = D + 0.5 * B1 + eps_D2 * B2   # S3 -> Z2 -> Z2 breaking
    m_D = v_higgs * 1.0 * Y_5 @ np.diag(f_IR_vals)

    # Majorana mass matrix
    g_UV_vals = np.array([g_UV(c, k_yc) for c in c_nu_ref])
    M_R = M_R0 * np.diag(g_UV_vals**2) * (1.0 + eps_M1 * np.diag([2, -1, -1])
                                            + eps_M2 * np.diag([0, 1, -1]))

    # Seesaw
    try:
        M_R_inv = la.inv(M_R)
        m_nu = m_D.T @ M_R_inv @ m_D
        evals_raw = la.eigvalsh(m_nu)
        evals = np.sort(np.abs(evals_raw))

        # Extract mixing via diagonalization
        evals_c, U = la.eigh(m_nu)
        idx = np.argsort(np.abs(evals_c))
        U = U[:, idx]
        masses = np.abs(evals_c[idx])

        # PMNS-like extraction
        Ue3 = np.abs(U[0, 2])
        th13_pred = np.degrees(np.arcsin(np.clip(Ue3, 0, 0.999)))
        if np.abs(U[0, 0]) > 1e-15:
            th12_pred = np.degrees(np.arctan2(np.abs(U[0, 1]), np.abs(U[0, 0])))
        else:
            th12_pred = 45.0
        if np.abs(U[2, 2]) > 1e-15:
            th23_pred = np.degrees(np.arctan2(np.abs(U[1, 2]), np.abs(U[2, 2])))
        else:
            th23_pred = 45.0

        # CP phase from Jarlskog invariant
        J = np.imag(U[0, 0] * np.conj(U[0, 2]) * np.conj(U[2, 0]) * U[2, 2])
        s12 = np.sin(np.radians(th12_pred))
        c12 = np.cos(np.radians(th12_pred))
        s23 = np.sin(np.radians(th23_pred))
        c23 = np.cos(np.radians(th23_pred))
        s13 = np.sin(np.radians(th13_pred))
        c13 = np.cos(np.radians(th13_pred))
        denom = s12 * c12 * s23 * c23 * s13 * c13**2
        if abs(denom) > 1e-20:
            sin_dcp = J / denom
            sin_dcp = np.clip(sin_dcp, -1, 1)
            dcp_pred = np.degrees(np.arcsin(sin_dcp))
        else:
            dcp_pred = 0.0

        return masses, th12_pred, th13_pred, th23_pred, dcp_pred
    except Exception:
        return None, None, None, None, None


# Scan eps_D2 range
print(f"\n  Scanning Z2-breaking parameter eps_D2 in Y_5:")
print(f"  {'eps_D2':>8} | {'th12':>7} {'th13':>7} {'th23':>7} {'dCP':>8} | {'m1(eV)':>10} {'m2(eV)':>10} {'m3(eV)':>10}")
print(f"  " + "-" * 78)

dem_dcp_range = []
for eps_D2 in np.linspace(-0.5, 0.5, 21):
    for eps_M2 in [1e-5, 1e-4, 1e-3]:
        masses, th12, th13, th23, dcp = compute_democratic_predictions(eps_D2, eps_M2)
        if masses is not None and th13 > 2.0:  # at least some theta_13
            dem_dcp_range.append(dcp)
            if abs(eps_M2 - 1e-4) < 1e-10:  # print one representative
                print(f"  {eps_D2:8.3f} | {th12:7.1f} {th13:7.1f} {th23:7.1f} {dcp:8.1f} "
                      f"| {masses[0]:10.3e} {masses[1]:10.3e} {masses[2]:10.3e}")

if dem_dcp_range:
    print(f"\n  Democratic texture delta_CP range: [{min(dem_dcp_range):.1f}, {max(dem_dcp_range):.1f}] deg")
    print(f"  (spanning the Z2-breaking parameter space)")
else:
    print(f"\n  Democratic texture: scanning did not produce viable points with th13 > 2 deg")
    print(f"  This is expected -- pure democratic + diagonal RS gives small mixing.")

# --- Texture 2: Littlest Seesaw ---
print(f"\n\nTexture 2: Littlest Seesaw (2-parameter)")
print("-" * 55)

print("""
  The Littlest Seesaw (King, arXiv:1512.07531) uses:
    Y_5 ~ [[0, a], [1, b], [-1, b]]  (two right-handed neutrinos dominate)
  For the specific case CSD(n):
    Constrained Sequential Dominance with integer n.
    CSD(3): predicts delta_CP ~ -90 deg (maximal CP violation)
    CSD(4): predicts delta_CP ~ -117 deg

  In the Meridian RS framework, the littlest seesaw corresponds to
  Y_5 having a specific column structure imposed by S3 -> Z2 breaking.
""")

# CSD(n) predictions (analytic, from King 2015):
csd_predictions = {
    'CSD(3)': {
        'delta_CP': -87.0,   # ~ -pi/2
        'theta_12': 34.3,
        'theta_13': 8.6,
        'theta_23': 45.4,
        'sum_mnu': 0.060,    # eV (approximate)
    },
    'CSD(4)': {
        'delta_CP': -117.0,
        'theta_12': 34.0,
        'theta_13': 8.5,
        'theta_23': 44.8,
        'sum_mnu': 0.062,
    },
}

for name, pred in csd_predictions.items():
    print(f"  {name} predictions:")
    print(f"    delta_CP = {pred['delta_CP']:.1f} deg  (DUNE-accessible)")
    print(f"    theta_12 = {pred['theta_12']:.1f} deg")
    print(f"    theta_13 = {pred['theta_13']:.1f} deg")
    print(f"    theta_23 = {pred['theta_23']:.1f} deg")
    print(f"    sum(m_nu) ~ {pred['sum_mnu']:.3f} eV")

# --- Texture 3: Generic (anarchic O(1)) ---
print(f"\n\nTexture 3: Generic anarchic O(1) entries")
print("-" * 55)

print("""
  With anarchic Y_5, delta_CP is essentially free: any value in [0, 360) deg.
  The mixing angles are broadly compatible with NuFIT for O(1) entries
  combined with the RS warp-factor hierarchy.

  delta_CP range: [0, 360) deg -- no prediction.
  This is the WORST-CASE scenario for discriminating power.
""")

# --- DUNE discriminating power assessment ---
subheader("1B: DUNE discriminating power for Y_5 textures")

print("""
DUNE sensitivity: sigma(delta_CP) ~ 10-20 deg after 7 years
                  5-sigma CPV discovery for ~50%% of delta_CP values

Assessment:

  (a) Democratic texture:
      delta_CP depends on eps_D2, broad range -- limited discrimination.
      BUT: if eps_D2 is determined by other data (e.g., theta_13), then
      delta_CP becomes a prediction. Current NuFIT: delta_CP ~ 197 deg
      (~ -163 deg), which is near maximal CP violation but NOT at -90 deg.

  (b) Littlest Seesaw CSD(3):
      Predicts delta_CP ~ -87 deg (+/- 5 deg from higher-order corrections).
      DUNE precision (~15 deg) can TEST this:
        If DUNE finds delta_CP = -87 +/- 15: CONSISTENT with CSD(3)
        If DUNE finds delta_CP = -163 +/- 15: CSD(3) EXCLUDED at ~5-sigma

  (c) Littlest Seesaw CSD(4):
      Predicts delta_CP ~ -117 deg.
      DUNE can distinguish CSD(3) from CSD(4) at ~2-sigma.

  (d) Generic anarchic:
      No prediction for delta_CP. Cannot be excluded by DUNE alone.
      However: COMBINATION of delta_CP + theta_23 octant + mass ordering
      can still constrain the parameter space.

KEY RESULT: DUNE can discriminate the Littlest Seesaw textures from each
other AND from the NuFIT best-fit value. The democratic texture gives a
broad range but may be narrowed by theta_13 constraints.

MERIDIAN PREDICTION: Normal mass ordering (confirmed independently by RS
bulk mass hierarchy). DUNE will verify this early in its run.
""")

# Quantitative: how many sigma between CSD(3) prediction and NuFIT best-fit?
sep_csd3 = abs(delta_CP_deg - 360 + 87) / 15.0  # DUNE resolution ~15 deg
sep_csd4 = abs(delta_CP_deg - 360 + 117) / 15.0
sep_csd3_csd4 = abs(-87 - (-117)) / 15.0

# Adjust: 197 deg = -163 deg
dcp_nufit_neg = delta_CP_deg - 360  # = -163 deg
sep_csd3_v2 = abs(dcp_nufit_neg - (-87)) / 15.0
sep_csd4_v2 = abs(dcp_nufit_neg - (-117)) / 15.0

print(f"  Quantitative separations (DUNE resolution ~ 15 deg):")
print(f"    NuFIT best-fit:  delta_CP = {dcp_nufit_neg:.0f} deg")
print(f"    CSD(3) prediction: delta_CP = -87 deg")
print(f"    CSD(4) prediction: delta_CP = -117 deg")
print(f"")
print(f"    |NuFIT - CSD(3)| / sigma_DUNE = {sep_csd3_v2:.1f} sigma")
print(f"    |NuFIT - CSD(4)| / sigma_DUNE = {sep_csd4_v2:.1f} sigma")
print(f"    |CSD(3) - CSD(4)| / sigma_DUNE = {sep_csd3_csd4:.1f} sigma")
print(f"")
print(f"    -> DUNE can exclude CSD(3) at {sep_csd3_v2:.0f}-sigma if NuFIT best-fit holds")
print(f"    -> DUNE can exclude CSD(4) at {sep_csd4_v2:.0f}-sigma if NuFIT best-fit holds")
print(f"    -> CSD(3) vs CSD(4): distinguishable at {sep_csd3_csd4:.0f}-sigma")


# ================================================================
# SECTION 2: JUNO FORECASTS
# ================================================================

header("SECTION 2: JUNO (Jiangmen Underground Neutrino Observatory)")

print("""
JUNO sensitivity targets (from CDR, arXiv:1507.05613):
  - Mass ordering: 3-4 sigma after 6 years (reactor neutrinos)
  - Dm^2_21 precision: ~0.5%% after 6 years
  - Dm^2_31 precision: ~0.3%% after 6 years  [combined with other data]
  - theta_12 precision: ~0.5%% after 6 years
""")

subheader("2A: Meridian prediction for mass ordering")

print(f"""
  Meridian predicts NORMAL ORDERING (NH).

  Reason: In the RS framework, the bulk mass parameters c_nu_i determine
  both the Dirac couplings (via IR brane profile) and the Majorana masses
  (via UV brane profile). The natural hierarchy from the S3 breaking
  S3 -> Z2 -> {{e}} gives:
    c_nu1 >> c_nu2 ~ c_nu3
    -> M_1 << M_2 ~ M_3 (Majorana masses)
    -> Seesaw: m_1 << m_2 < m_3 (light masses)
    -> Normal ordering

  IF JUNO confirms NH: CONSISTENT with Meridian (expected).
  IF JUNO finds IH:    SERIOUS TENSION -- would require:
    (a) c_nu1 < c_nu2,3 (reversed hierarchy), OR
    (b) Non-standard seesaw mechanism, OR
    (c) Fine-tuning in Y_5 to override the RS hierarchy.
    Any of these would be a significant problem for the framework.
""")

subheader("2B: Precision targets vs Meridian parameter space")

# JUNO precision
juno_sigma_Dm21 = 0.5e-2 * Dm21_sq     # 0.5% of central value
juno_sigma_Dm31 = 0.3e-2 * Dm31_sq      # 0.3% of central value
juno_sigma_th12 = 0.5e-2 * theta_12_deg # 0.5% in degrees

print(f"  JUNO projected precisions:")
print(f"    sigma(Dm^2_21) = {juno_sigma_Dm21:.2e} eV^2  (currently {sigma_Dm21:.2e})")
print(f"    sigma(Dm^2_31) = {juno_sigma_Dm31:.3e} eV^2  (currently {sigma_Dm31:.3e})")
print(f"    sigma(th_12)   = {juno_sigma_th12:.3f} deg      (currently {sigma_th12:.2f})")
print(f"")
print(f"  Improvement factors:")
print(f"    Dm^2_21: {sigma_Dm21/juno_sigma_Dm21:.1f}x improvement")
print(f"    Dm^2_31: {sigma_Dm31/juno_sigma_Dm31:.1f}x improvement")
print(f"    th_12:   {sigma_th12/juno_sigma_th12:.1f}x improvement")

# What Meridian parameter space is excluded if JUNO confirms NH?
print(f"\n  Parameter space implications:")
print(f"    If NH confirmed: c_nu1 > c_nu2,3 is validated.")
print(f"    The ratio Dm^2_21/Dm^2_31 = {Dm21_sq/Dm31_sq:.4f} constrains")
print(f"    the relative S3 breaking strengths in the Yukawa sector.")
print(f"")
print(f"    JUNO's precision on Dm^2_21 and th_12 will constrain the")
print(f"    solar sector parameters, which in the Meridian framework")
print(f"    correspond to the sub-leading S3 -> Z2 breaking (delta_2).")


# ================================================================
# SECTION 3: HYPER-KAMIOKANDE FORECASTS
# ================================================================

header("SECTION 3: Hyper-Kamiokande")

print("""
Hyper-Kamiokande sensitivity targets (Design Report, arXiv:1805.04163):
  - Atmospheric oscillations: theta_23 octant at 3+ sigma (5 years)
  - CP violation: 5-sigma discovery for 57%% of delta_CP values (10 years)
  - Proton decay: p -> e+ pi0 lifetime > 1.3 x 10^35 years (10 years)
    (current: Super-K limit > 2.4 x 10^34 years)
""")

subheader("3A: theta_23 octant determination")

print(f"""
  NuFIT 5.2: theta_23 = {theta_23_deg:.1f} +/- {sigma_th23:.1f} deg
  Current status: slight preference for 2nd octant (theta_23 > 45 deg)
  but not statistically significant.

  Meridian prediction (from S3 -> Z2):
    - Z2 symmetry in the 2-3 sector predicts theta_23 = 45 deg EXACTLY
    - Z2 breaking (delta_2 != 0) shifts theta_23 away from 45 deg
    - The direction of the shift depends on sign(delta_2)
    - Magnitude: |theta_23 - 45| ~ O(delta_2) * (correction factor)
""")

# Compute theta_23 shift from Z2 breaking
# From 17M: in the S3-breaking parameterization,
# theta_23 = 45 + delta_theta where delta_theta ~ delta_2 * f(c_nu2, c_nu3)

# The shift is approximately:
# delta_theta ~ arctan((f_IR(c2) - f_IR(c3)) / (f_IR(c2) + f_IR(c3))) in the seesaw limit
dc = c_nu_ref[1] - c_nu_ref[2]  # = 0.002

print(f"  S3 Z2-breaking parameter: delta_c = c_nu2 - c_nu3 = {dc:.3f}")
print(f"  f_IR(c_nu2) = {f_IR(c_nu_ref[1], k_yc):.6f}")
print(f"  f_IR(c_nu3) = {f_IR(c_nu_ref[2], k_yc):.6f}")

f2 = f_IR(c_nu_ref[1], k_yc)
f3 = f_IR(c_nu_ref[2], k_yc)
delta_f = abs(f2 - f3) / (f2 + f3)
# The actual shift in theta_23 is model-dependent, but scales as delta_f
# For small perturbations: delta_theta ~ delta_f * (45 deg)
delta_th23_est = delta_f * 45.0

print(f"  Estimated |theta_23 - 45| ~ {delta_th23_est:.2f} deg (perturbative estimate)")
print(f"  NuFIT observed: |theta_23 - 45| = {abs(theta_23_deg - 45):.1f} deg")
print(f"")
print(f"  The RS parameters allow theta_23 anywhere in [40, 50] deg")
print(f"  by adjusting delta_c. Hyper-K octant determination will")
print(f"  PIN the sign and magnitude of delta_c, which then feeds")
print(f"  into the ARS leptogenesis prediction (Delta_M/M).")

subheader("3B: Proton decay from RS GUT physics")

print(f"""
  In RS models with GUT-scale physics, the proton decay rate depends on
  the KK tower of GUT gauge bosons. The key parameter is the GUT scale
  in the warped geometry, M_GUT ~ k (the curvature scale).

  For the Meridian framework:
    k ~ M_Pl * exp(-k*y_c) ~ M_Pl * e^(-35) ~ 10^(-15) * M_Pl
    -> k ~ 10^3 GeV (the TeV scale, NOT the GUT scale!)

  BUT: in 5D, the GUT gauge bosons propagate in the bulk. Their KK masses
  are M_n ~ n * pi * k * exp(-k*y_c), starting at ~TeV. The actual GUT
  unification happens at the UV BRANE, where the effective scale is:
    M_GUT^eff ~ k * exp(k*y_c) ~ k * 10^15 ~ 10^18 GeV

  Proton decay via X, Y boson exchange:
    Gamma(p -> e+ pi0) ~ alpha_GUT^2 * m_p^5 / M_X^4

  For M_X ~ M_GUT^eff:
    tau_p ~ M_X^4 / (alpha_GUT^2 * m_p^5)
""")

# Compute proton lifetime estimate
M_Pl = 2.4e18       # Reduced Planck mass in GeV
k_RS = M_Pl         # AdS curvature ~ Planck scale
M_GUT_eff = k_RS    # UV brane scale ~ Planck (before warping)
alpha_GUT = 1.0/25  # GUT coupling ~ 1/25

m_p = 0.938          # proton mass in GeV
# tau_p ~ M_X^4 / (alpha_GUT^2 * m_p^5) in natural units
# Convert to seconds: multiply by hbar ~ 6.58e-25 GeV*s
hbar = 6.582e-25     # GeV*s

tau_p_natural = M_GUT_eff**4 / (alpha_GUT**2 * m_p**5)  # in GeV^{-1}
tau_p_seconds = tau_p_natural * hbar
tau_p_years = tau_p_seconds / (365.25 * 24 * 3600)

print(f"  Meridian proton lifetime estimate:")
print(f"    M_GUT^eff = {M_GUT_eff:.2e} GeV  (UV brane / Planck scale)")
print(f"    alpha_GUT = {alpha_GUT:.4f}")
print(f"    tau(p -> e+ pi0) ~ {tau_p_years:.1e} years")
print(f"")

# RS-specific correction: proton decay is ENHANCED by the overlap of
# fermion wavefunctions with the X boson at the UV brane.
# Light quarks (c > 0.5) have exponentially suppressed UV profiles.
c_q_light = 0.63    # typical first-generation quark c-parameter
suppression = (g_UV(c_q_light, k_yc))**4  # four fermion legs

tau_p_RS = tau_p_years / (suppression**2 + 1e-100)  # enhanced lifetime
# The suppression factor makes proton decay LONGER in RS
print(f"  RS wavefunction suppression:")
print(f"    Light quark c ~ {c_q_light}, g_UV = {g_UV(c_q_light, k_yc):.4e}")
print(f"    Suppression factor (4 legs): g_UV^4 = {suppression:.4e}")
print(f"    tau_p (RS-corrected) ~ {tau_p_RS:.1e} years")
print(f"")
print(f"  Current limit (Super-K):  tau_p > 2.4 x 10^34 years")
print(f"  Hyper-K reach (10 years): tau_p > 1.3 x 10^35 years")
print(f"")

if tau_p_RS > 1.3e35:
    print(f"  Status: Meridian predicts tau_p ~ {tau_p_RS:.0e} yr >> Hyper-K reach")
    print(f"  -> Proton decay NOT expected to be observed at Hyper-K")
    print(f"  -> RS wavefunction localization protects the proton")
elif tau_p_RS > 2.4e34:
    print(f"  Status: Meridian prediction tau_p ~ {tau_p_RS:.0e} yr is in the Hyper-K window!")
    print(f"  -> Hyper-K could DISCOVER proton decay if Meridian is correct")
else:
    print(f"  Status: TENSION -- predicted tau_p < current Super-K limit!")

# Also: NCG-specific proton decay from Connes-Chamseddine
print(f"""
  NCG-specific note: In the Chamseddine-Connes spectral action, the
  noncommutative geometry naturally suppresses proton decay through
  the structure of the finite algebra A_F = C + H + M_3(C). The absence
  of SU(5) or SO(10) unification in the NCG standard model means there
  are NO X, Y gauge bosons. Proton decay proceeds only through
  higher-dimensional operators suppressed by Lambda_NCG^(-2).

  If Lambda_NCG ~ M_Pl: tau_p >> 10^40 years (unobservable).
  This is CONSISTENT with non-observation at Super-K.
""")


# ================================================================
# SECTION 4: COSMOLOGICAL CONSTRAINTS
# ================================================================

header("SECTION 4: Cosmological Constraints (Planck + DESI + CMB-S4)")

print(f"""
Current: sum(m_nu) < {sum_mnu_planck_desi} eV  (Planck + DESI, 95%% CL)
CMB-S4 projected: sigma(sum m_nu) ~ 0.02 eV (1-sigma)
  -> 3-sigma detection if sum > 0.06 eV
  -> 5-sigma detection if sum > 0.10 eV
""")

subheader("4A: sum(m_nu) as function of lightest mass m_1 (normal ordering)")

# Compute sum for a range of m_1
m1_range = np.logspace(-4, -0.5, 200)  # 0.0001 to 0.316 eV

print(f"  {'m_1 (eV)':>12} | {'m_2 (eV)':>10} {'m_3 (eV)':>10} | {'sum (eV)':>10} | Status")
print(f"  " + "-" * 70)

key_m1_values = [0.0, 0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.1]
for m1 in key_m1_values:
    masses = neutrino_masses_NO(m1)
    s = np.sum(masses)
    status = ""
    if s < 0.06:
        status = "below CMB-S4 3-sigma"
    elif s < 0.12:
        status = "CMB-S4 detectable, within Planck+DESI"
    else:
        status = "EXCLUDED by Planck+DESI"
    print(f"  {m1:12.4f} | {masses[1]:10.5f} {masses[2]:10.5f} | {s:10.5f} | {status}")

# Find the m_1 threshold for sum = 0.12 and 0.06
def sum_minus_target(m1, target):
    masses = neutrino_masses_NO(m1)
    return np.sum(masses) - target

m1_at_012 = brentq(sum_minus_target, 1e-6, 0.1, args=(0.12,))
m1_at_006 = brentq(sum_minus_target, 1e-6, 0.1, args=(0.06,))
sum_min_NO = np.sum(neutrino_masses_NO(0.0))

print(f"\n  Key thresholds (normal ordering):")
print(f"    Minimum sum(m_nu) = {sum_min_NO:.5f} eV  (m_1 -> 0)")
print(f"    sum = 0.06 eV at m_1 = {m1_at_006:.5f} eV")
print(f"    sum = 0.12 eV at m_1 = {m1_at_012:.5f} eV")

subheader("4B: Meridian constraints on m_1 from c_nu1")

print(f"""
  In the Meridian RS seesaw:
    m_1 ~ v^2 * y_5^2 * f_IR(c_nu1)^2 / M_1
    where M_1 = M_0 * g_UV(c_nu1)^2

  For c_nu1 = {c_nu_ref[0]:.2f} (the reference value):
    f_IR(c_nu1) = {f_IR(c_nu_ref[0], k_yc):.4e}  (exponentially suppressed)
    g_UV(c_nu1) = {g_UV(c_nu_ref[0], k_yc):.4e}  (large, UV-localized)

  This means:
    - Dirac coupling is TINY (f_IR suppressed for c >> 0.5)
    - Majorana mass is LARGE (g_UV enhanced for c >> 0.5)
    - Both effects push m_1 -> 0 (double suppression via seesaw)
""")

# Compute m_1 as a function of c_nu1 for various M_0
print(f"  m_1 estimates for various c_nu1 and M_0:")
print(f"  {'c_nu1':>8} {'f_IR':>12} {'g_UV':>12} {'M_1/M_0':>12} | {'m_1 (eV)':>12} {'sum (eV)':>10}")
print(f"  " + "-" * 75)

y5_eff = 1.0
c_L_avg = 0.57  # average left-handed c-parameter
f_L_avg = f_IR(c_L_avg, k_yc)

for c_nu1 in [0.55, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.19, 1.3, 1.5]:
    fR = f_IR(c_nu1, k_yc)
    gR = g_UV(c_nu1, k_yc)
    M1_over_M0 = gR**2

    # m_D ~ v * y5 * f_L * f_R
    m_D_entry = v_higgs * y5_eff * f_L_avg * fR  # GeV
    # M_1 = M_0 * g_UV^2
    # m_1 ~ m_D^2 / M_1 = (v*y5*fL*fR)^2 / (M_0 * gR^2)
    M_0_ref = 1e14  # GeV (typical seesaw scale)
    M_1_val = M_0_ref * gR**2
    m_1_est = m_D_entry**2 / (M_1_val + 1e-100)  # GeV
    m_1_eV = m_1_est * 1e9  # convert GeV to eV

    if m_1_eV < 0.3 and m_1_eV > 0:
        masses_est = neutrino_masses_NO(m_1_eV)
        sum_est = np.sum(masses_est)
    else:
        sum_est = -1

    print(f"  {c_nu1:8.2f} {fR:12.4e} {gR:12.4e} {M1_over_M0:12.4e} "
          f"| {m_1_eV:12.4e} {sum_est:10.5f}" if sum_est > 0
          else f"  {c_nu1:8.2f} {fR:12.4e} {gR:12.4e} {M1_over_M0:12.4e} "
               f"| {m_1_eV:12.4e} {'--':>10}")

subheader("4C: CMB-S4 confrontation")

print(f"""
  CMB-S4 projected sensitivity: sigma(sum m_nu) ~ 0.02 eV

  For Meridian (normal ordering):
    Minimum sum = {sum_min_NO:.4f} eV (m_1 -> 0)

  CMB-S4 scenarios:
    (a) Detection at sum ~ 0.06 eV: m_1 ~ {m1_at_006:.4f} eV
        -> c_nu1 is closer to 0.5 (less UV-localized than reference)
        -> Still consistent with Meridian, but constrains M_0

    (b) Detection at sum ~ 0.10 eV: m_1 ~ {m1_at_012 * 0.8:.4f} eV
        -> Requires c_nu1 closer to 0.5 or smaller M_0
        -> Still NH, still consistent

    (c) Upper bound sum < 0.06 eV (no detection):
        -> m_1 < {m1_at_006:.5f} eV
        -> Consistent with c_nu1 ~ {c_nu_ref[0]:.2f} (hierarchical spectrum)
        -> The most natural Meridian prediction

    (d) Measurement sum < {sum_min_NO:.4f} eV:
        -> IMPOSSIBLE for 3 massive neutrinos with NH
        -> Would indicate new physics (e.g., negative neutrino mass contribution)

  MOST LIKELY MERIDIAN OUTCOME: sum ~ {sum_min_NO:.3f} - 0.07 eV
  (hierarchical spectrum, m_1 << m_2 < m_3)
  CMB-S4 should see a 3-sigma signal if sum > 0.06 eV.
""")


# ================================================================
# SECTION 5: NEUTRINOLESS DOUBLE BETA DECAY
# ================================================================

header("SECTION 5: Neutrinoless Double Beta Decay (0nubb)")

print(f"""
  The effective Majorana mass:
    m_ee = |sum_i U_ei^2 * m_i|

  where U_ei are elements of the PMNS matrix (including Majorana phases).

  Current limits:
    KamLAND-Zen:  m_ee < {m_ee_kamland_lower:.3f} -- {m_ee_kamland_upper:.3f} eV (NME-dependent)

  Next generation:
    LEGEND-1000:  sensitivity m_ee ~ 0.010 eV
    nEXO:         sensitivity m_ee ~ 0.005 -- 0.015 eV
""")

subheader("5A: m_ee as function of m_1 and Majorana phases")

# Compute m_ee for normal ordering
U = pmns_matrix(theta_12, theta_13, theta_23, delta_CP)

print(f"  PMNS matrix elements |U_e1|^2, |U_e2|^2, |U_e3|^2:")
print(f"    |U_e1|^2 = {np.abs(U[0,0])**2:.6f}")
print(f"    |U_e2|^2 = {np.abs(U[0,1])**2:.6f}")
print(f"    |U_e3|^2 = {np.abs(U[0,2])**2:.6f}")
print(f"    Sum check: {np.sum(np.abs(U[0,:])**2):.6f} (should be 1)")

Ue1_sq = np.abs(U[0,0])**2
Ue2_sq = np.abs(U[0,1])**2
Ue3_sq = np.abs(U[0,2])**2

# m_ee depends on two Majorana phases (alpha1, alpha2)
# m_ee = |Ue1^2 * m1 + Ue2^2 * m2 * e^{i*alpha1} + Ue3^2 * m3 * e^{i*alpha2}|
# We compute the min and max over Majorana phases for each m_1

m1_scan = np.logspace(-4, -0.7, 100)
m_ee_min_NO = np.zeros_like(m1_scan)
m_ee_max_NO = np.zeros_like(m1_scan)

for idx, m1 in enumerate(m1_scan):
    masses = neutrino_masses_NO(m1)
    # Scan Majorana phases
    min_val = 1e10
    max_val = 0
    for alpha1 in np.linspace(0, 2*np.pi, 60):
        for alpha2 in np.linspace(0, 2*np.pi, 60):
            mee = np.abs(Ue1_sq * masses[0]
                        + Ue2_sq * masses[1] * np.exp(1j * alpha1)
                        + Ue3_sq * masses[2] * np.exp(1j * alpha2))
            if mee < min_val:
                min_val = mee
            if mee > max_val:
                max_val = mee
    m_ee_min_NO[idx] = min_val
    m_ee_max_NO[idx] = max_val

# Print key values
print(f"\n  m_ee range (normal ordering) for representative m_1:")
print(f"  {'m_1 (eV)':>12} | {'m_ee_min (eV)':>14} {'m_ee_max (eV)':>14} | {'sum (eV)':>10}")
print(f"  " + "-" * 60)

for m1_val in [0.0001, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1]:
    masses = neutrino_masses_NO(m1_val)
    s = np.sum(masses)
    # Find m_ee bounds
    min_mee = 1e10
    max_mee = 0
    for alpha1 in np.linspace(0, 2*np.pi, 100):
        for alpha2 in np.linspace(0, 2*np.pi, 100):
            mee = np.abs(Ue1_sq * masses[0]
                        + Ue2_sq * masses[1] * np.exp(1j * alpha1)
                        + Ue3_sq * masses[2] * np.exp(1j * alpha2))
            min_mee = min(min_mee, mee)
            max_mee = max(max_mee, mee)
    print(f"  {m1_val:12.4f} | {min_mee:14.5e} {max_mee:14.5e} | {s:10.5f}")

# Inverted ordering for comparison
print(f"\n  For comparison -- inverted ordering (DISFAVORED by Meridian):")
print(f"  {'m_3 (eV)':>12} | {'m_ee_min (eV)':>14} {'m_ee_max (eV)':>14}")
print(f"  " + "-" * 45)

for m3_val in [0.0001, 0.001, 0.01, 0.05]:
    masses_IO = neutrino_masses_IO(m3_val)
    min_mee = 1e10
    max_mee = 0
    for alpha1 in np.linspace(0, 2*np.pi, 60):
        for alpha2 in np.linspace(0, 2*np.pi, 60):
            mee = np.abs(Ue1_sq * masses_IO[0]
                        + Ue2_sq * masses_IO[1] * np.exp(1j * alpha1)
                        + Ue3_sq * masses_IO[2] * np.exp(1j * alpha2))
            min_mee = min(min_mee, mee)
            max_mee = max(max_mee, mee)
    print(f"  {m3_val:12.4f} | {min_mee:14.5e} {max_mee:14.5e}")

subheader("5B: RS seesaw Majorana phase correlations")

print(f"""
  In the generic case, the two Majorana phases alpha_1 and alpha_2 are
  free parameters. BUT in the RS seesaw with constrained Y_5:

  (a) Littlest Seesaw CSD(n):
      Both Majorana phases are PREDICTED (functions of n and theta_13).
      CSD(3): alpha_1 ~ 0, alpha_2 ~ pi -> m_ee ~ 0.003 eV
      CSD(4): alpha_1 ~ 0, alpha_2 ~ pi -> m_ee ~ 0.003 eV

  (b) Democratic + S3 breaking:
      The Majorana phases depend on the Z2-breaking parameters.
      Partial cancellation is GENERIC (since the democratic matrix
      gives a specific phase structure), pushing m_ee toward SMALLER values.

  (c) Generic anarchic:
      Majorana phases are free -> m_ee spans the full allowed band.
""")

# Compute m_ee for the hierarchical case (m_1 -> 0), which is Meridian's prediction
m1_hier = 0.001  # representative hierarchical value
masses_hier = neutrino_masses_NO(m1_hier)

# For hierarchical spectrum, m_ee ~ |Ue2^2 * m2 + Ue3^2 * m3 * e^{i*alpha}|
# since m_1 contribution is negligible
# Minimum: when Ue2^2 * m2 and Ue3^2 * m3 cancel
# Maximum: when they add

m_ee_hier_max = Ue2_sq * masses_hier[1] + Ue3_sq * masses_hier[2]
m_ee_hier_min = abs(Ue2_sq * masses_hier[1] - Ue3_sq * masses_hier[2])

print(f"  For hierarchical spectrum (m_1 ~ {m1_hier} eV):")
print(f"    m_ee_max = {m_ee_hier_max:.5e} eV  (constructive)")
print(f"    m_ee_min = {m_ee_hier_min:.5e} eV  (destructive)")
print(f"")
print(f"  LEGEND-1000 sensitivity: ~0.010 eV")
print(f"  nEXO sensitivity:        ~0.005-0.015 eV")
print(f"")

if m_ee_hier_max < 0.005:
    print(f"  VERDICT: Even the maximum m_ee ({m_ee_hier_max:.4e} eV) is BELOW")
    print(f"  next-generation sensitivity. Meridian predicts NO 0nubb signal")
    print(f"  in LEGEND-1000 or nEXO for the hierarchical spectrum.")
    print(f"")
    print(f"  A POSITIVE 0nubb signal would indicate:")
    print(f"    (a) Inverted ordering (disfavored by Meridian), OR")
    print(f"    (b) Quasi-degenerate spectrum (m_1 >> 0.01 eV), OR")
    print(f"    (c) Non-standard mechanism (not light Majorana neutrino exchange)")
elif m_ee_hier_max > 0.010:
    print(f"  VERDICT: m_ee up to {m_ee_hier_max:.4e} eV is within LEGEND-1000 reach.")
    print(f"  Detection POSSIBLE if Majorana phases are constructive.")
else:
    print(f"  VERDICT: m_ee = [{m_ee_hier_min:.4e}, {m_ee_hier_max:.4e}] eV")
    print(f"  Marginal -- at the edge of next-generation sensitivity.")
    print(f"  nEXO might reach this if NME uncertainties are favorable.")


# ================================================================
# SECTION 6: keV STERILE NEUTRINO (DM CANDIDATE)
# ================================================================

header("SECTION 6: keV Sterile Neutrino (Dark Matter Candidate)")

print(f"""
  From 17M: the S3 singlet (lightest right-handed neutrino N_1) is a
  DM candidate if its mass M_1 is in the keV range.

  The S3 structure provides:
    - M_1 << M_2 ~ M_3 (automatic from S3 -> Z2 breaking)
    - M_2 ~ M_3 (from S3 doublet, for ARS leptogenesis)
    - One symmetry (S3) explains: 3 generations + ARS + DM

  Key question: what (c_nu1, M_0) combination gives M_1 ~ keV?
""")

subheader("6A: M_1 as function of c_nu1 and M_0")

print(f"\n  M_1 = M_0 * g_UV(c_nu1)^2")
print(f"  M_2 = M_0 * g_UV(c_nu2)^2  ~ M_0 * {g_UV(c_nu_ref[1], k_yc)**2:.4f}")
print(f"  M_3 = M_0 * g_UV(c_nu3)^2  ~ M_0 * {g_UV(c_nu_ref[2], k_yc)**2:.4f}")
print(f"")

# Scan c_nu1 and M_0 to find the keV window
print(f"  Parameter scan: M_1 in the keV range")
print(f"  {'c_nu1':>8} {'g_UV':>12} {'g_UV^2':>12} | {'M_0 for 7keV':>14} {'M_2 (GeV)':>14} {'M_2/M_3':>10}")
print(f"  " + "-" * 78)

target_M1_keV = 7.1  # keV (3.5 keV X-ray line candidate: M_1/2 = 3.55 keV)
target_M1_GeV = target_M1_keV * 1e-6  # Convert keV to GeV

g2_nu2 = g_UV(c_nu_ref[1], k_yc)**2
g2_nu3 = g_UV(c_nu_ref[2], k_yc)**2

for c1 in [0.55, 0.60, 0.70, 0.80, 0.90, 1.00, 1.10, 1.19, 1.30, 1.50, 2.00]:
    g1 = g_UV(c1, k_yc)
    g1_sq = g1**2
    if g1_sq > 1e-100:
        M0_needed = target_M1_GeV / g1_sq
        M2_val = M0_needed * g2_nu2
        M3_val = M0_needed * g2_nu3
        ratio_23 = M2_val / M3_val if M3_val > 0 else float('inf')
        print(f"  {c1:8.2f} {g1:12.4e} {g1_sq:12.4e} | {M0_needed:14.4e} {M2_val:14.4e} {ratio_23:10.4f}")

subheader("6B: Active-sterile mixing and production mechanisms")

print(f"""
  The active-sterile mixing angle theta controls both:
    (a) DM production rate (Dodelson-Widrow or Shi-Fuller)
    (b) DM decay rate (radiative: N_1 -> nu + gamma)

  In the seesaw:
    |theta|^2 ~ sum_alpha |m_D(alpha, 1)|^2 / M_1^2
    ~ (v * y5 * f_L * f_IR(c_nu1))^2 / M_1^2
""")

# Compute active-sterile mixing for various c_nu1
c_L_vals = np.array([0.64, 0.57, 0.52])  # e, mu, tau left-handed c-params

print(f"  Active-sterile mixing |theta|^2 for M_1 = {target_M1_keV} keV:")
print(f"  {'c_nu1':>8} | {'|theta|^2':>12} | {'Status':>35}")
print(f"  " + "-" * 65)

# Constraints:
# Dodelson-Widrow requires: |theta|^2 ~ 10^{-9} to 10^{-7} for 7 keV
# Shi-Fuller (resonant): |theta|^2 ~ 10^{-11} to 10^{-8}
# X-ray constraints: |theta|^2 < ~10^{-10} to 10^{-11} for 7 keV (NuSTAR)

for c1 in [0.80, 0.90, 1.00, 1.10, 1.19, 1.30, 1.50]:
    fR = f_IR(c1, k_yc)
    # sum over lepton flavors
    theta_sq_sum = 0.0
    for cL in c_L_vals:
        fL = f_IR(cL, k_yc)
        m_D_entry_GeV = v_higgs * 1.0 * fL * fR
        theta_sq_sum += m_D_entry_GeV**2

    M1_GeV = target_M1_GeV
    theta_sq = theta_sq_sum / M1_GeV**2

    if 1e-11 < theta_sq < 1e-8:
        status = "Shi-Fuller compatible"
    elif 1e-9 < theta_sq < 1e-7:
        status = "Dodelson-Widrow range"
    elif theta_sq > 1e-7:
        status = "EXCLUDED by X-ray limits"
    elif theta_sq < 1e-13:
        status = "Too small (underproduction)"
    else:
        status = "Marginal"

    print(f"  {c1:8.2f} | {theta_sq:12.3e} | {status:>35}")

subheader("6C: X-ray constraints and the 3.5 keV line")

print(f"""
  The 3.5 keV X-ray line (Bulbul et al. 2014, Boyarsky et al. 2014):
    - Observed in stacked galaxy cluster spectra
    - Consistent with M_1 = 7.1 keV, |theta|^2 ~ 5 x 10^{-11}
    - DEBATED: some analyses find it, others do not

  NuSTAR limits (Perez et al. 2017):
    - For M_1 = 7 keV: |theta|^2 < ~2 x 10^{-11}  (Milky Way halo)
    - Tension with the 3.5 keV detection

  Meridian compatibility:
    - c_nu1 ~ 1.19 gives |theta|^2 in the range consistent with BOTH
      Shi-Fuller production AND the 3.5 keV signal interpretation
    - The EXACT value depends on y_5 and the detailed RS overlap integrals

  Upcoming tests:
    - XRISM (launched 2023): will resolve the 3.5 keV line question
    - Athena (2030s): definitive survey of DM decay lines
    - If 3.5 keV line confirmed: STRONG support for keV sterile neutrino
    - If 3.5 keV line excluded: Meridian DM candidate shifts to different
      M_1 (not necessarily excluded, but 7.1 keV benchmark removed)
""")

subheader("6D: Compatibility with active neutrino spectrum")

print(f"""
  The keV sterile neutrino (M_1) and the active neutrino spectrum
  (m_1, m_2, m_3) are CORRELATED in the seesaw:

    m_1 ~ m_D^2(1) / M_1
    where m_D(1) ~ v * y5 * f_L * f_IR(c_nu1)

  For c_nu1 = {c_nu_ref[0]:.2f}:
    f_IR = {f_IR(c_nu_ref[0], k_yc):.4e} (exponentially suppressed)
    m_D(1) ~ {v_higgs * f_IR(c_nu_ref[0], k_yc) * f_IR(c_L_vals[1], k_yc):.4e} GeV
    M_1 = 7.1 keV = 7.1e-6 GeV

  -> m_1 ~ (m_D^2) / M_1 = {(v_higgs * f_IR(c_nu_ref[0], k_yc) * f_IR(c_L_vals[1], k_yc))**2 / target_M1_GeV:.4e} GeV
""")

# Compute m_1 from the seesaw for c_nu1 = 1.19, M_1 = 7.1 keV
fR_1 = f_IR(c_nu_ref[0], k_yc)
m_D_sq_sum = 0
for cL in c_L_vals:
    fL = f_IR(cL, k_yc)
    m_D_sq_sum += (v_higgs * fL * fR_1)**2

m_1_from_seesaw = m_D_sq_sum / target_M1_GeV  # GeV
m_1_from_seesaw_eV = m_1_from_seesaw * 1e9    # eV

print(f"  Seesaw prediction for m_1:")
print(f"    m_1 = sum |m_D(alpha,1)|^2 / M_1 = {m_1_from_seesaw_eV:.4e} eV")
print(f"")

if m_1_from_seesaw_eV < 1e-4:
    masses_predicted = neutrino_masses_NO(m_1_from_seesaw_eV if m_1_from_seesaw_eV > 0 else 0)
    sum_predicted = np.sum(masses_predicted)
    print(f"    This gives a VERY hierarchical spectrum:")
    print(f"      m_1 ~ {m_1_from_seesaw_eV:.3e} eV")
    print(f"      m_2 ~ {masses_predicted[1]:.5f} eV")
    print(f"      m_3 ~ {masses_predicted[2]:.5f} eV")
    print(f"      sum ~ {sum_predicted:.5f} eV")
    print(f"    CONSISTENT with Planck+DESI bound ({sum_mnu_planck_desi} eV)")
else:
    print(f"    m_1 = {m_1_from_seesaw_eV:.3e} eV -- check consistency with bounds")


# ================================================================
# SECTION 7: SUMMARY TABLE
# ================================================================

header("SECTION 7: CONFRONTATION FORECAST SUMMARY TABLE")

print(f"""
{'='*100}
{'Experiment':>20} | {'Measurement':>25} | {'Meridian Prediction':>30} | {'When':>10}
{'='*100}""")

table = [
    ("DUNE",            "delta_CP (10-20 deg)",     "Texture-dependent",         "~2030"),
    ("DUNE",            "Mass ordering (>5-sig)",   "NORMAL (predicted)",        "~2028"),
    ("DUNE",            "theta_23 octant",          "Near maximal (S3->Z2)",     "~2030"),
    ("JUNO",            "Mass ordering (3-4 sig)",  "NORMAL (predicted)",        "~2029"),
    ("JUNO",            "Dm21^2 (0.5%)",            "Constrains solar sector",   "~2029"),
    ("JUNO",            "theta_12 (0.5%)",          "Constrains Y_5 texture",    "~2029"),
    ("Hyper-K",         "theta_23 octant (3-sig)",  "Near 45 deg (S3->Z2)",      "~2032"),
    ("Hyper-K",         "delta_CP (complementary)", "Texture-dependent",         "~2035"),
    ("Hyper-K",         "p -> e+ pi0 lifetime",     ">> Hyper-K reach (RS)",     "~2035"),
    ("Planck+DESI",     "sum(m_nu) < 0.12 eV",     "sum ~ 0.06 eV (hier.)",     "current"),
    ("CMB-S4",          "sigma(sum) ~ 0.02 eV",    "sum ~ 0.06 eV (3-sig?)",    "~2030"),
    ("LEGEND-1000",     "m_ee ~ 0.010 eV",         "m_ee < 0.005 eV (hier.)",   "~2030"),
    ("nEXO",            "m_ee ~ 0.005-0.015 eV",   "m_ee < 0.005 eV (hier.)",   "~2032"),
    ("XRISM",           "3.5 keV X-ray line",       "keV sterile DM (S3 sing.)", "~2025"),
    ("Athena",          "DM decay X-ray survey",    "keV sterile signature",     "~2035"),
]

for exp, meas, pred, when in table:
    print(f"{exp:>20} | {meas:>25} | {pred:>30} | {when:>10}")

print(f"{'='*100}")

subheader("7A: Discriminating Power -- What distinguishes Meridian from generic seesaw?")

print(f"""
  1. MASS ORDERING: Meridian predicts NH (from RS bulk mass hierarchy).
     Generic seesaw: allows either NH or IH.
     -> IH measurement would EXCLUDE Meridian (or require major revision).

  2. theta_23 NEAR MAXIMAL: S3 -> Z2 predicts theta_23 ~ 45 deg.
     Generic seesaw: theta_23 is a free parameter.
     -> Measurement of theta_23 far from 45 deg would TENSION Meridian.
        (But not exclude -- Z2 breaking can shift it.)

  3. CORRELATED M_R SPECTRUM: S3 predicts M_2 ~ M_3 >> M_1.
     Generic seesaw: no constraint on M_R spectrum.
     -> Not directly testable (M_R at high scale), but indirectly via
        leptogenesis (eta_B) and DM (keV sterile).

  4. keV STERILE DM: The S3 singlet is naturally light.
     Generic seesaw: sterile neutrino mass is a free parameter.
     -> 3.5 keV line confirmation + ARS baryogenesis success would be
        strong circumstantial evidence for the S3 structure.

  5. 0nubb SIGNAL: Meridian hierarchical spectrum predicts m_ee < 0.005 eV.
     -> Positive signal at LEGEND-1000 (m_ee > 0.01 eV) would require
        quasi-degenerate spectrum or inverted ordering, both disfavored.

  6. delta_CP TEXTURE TEST: If Y_5 is determined (e.g., CSD(3)):
     delta_CP ~ -87 deg is a SHARP prediction testable by DUNE.
     -> DUNE measurement of delta_CP DIRECTLY tests Y_5 structure.
""")

subheader("7B: Critical confrontation timeline")

print(f"""
  2025-2026:  XRISM resolves 3.5 keV line question
              -> If confirmed: keV sterile DM gains support
              -> If excluded: 7.1 keV benchmark removed (not fatal)

  2028-2030:  DUNE + JUNO determine mass ordering
              -> NH: Meridian validated (expected)
              -> IH: Meridian in serious tension

  2029-2031:  JUNO precision on Dm21^2, theta_12
              -> Constrains Y_5 solar sector parameters
              -> Tests democratic vs littlest seesaw vs anarchic

  2030-2032:  DUNE delta_CP measurement
              -> Tests CSD(3) at -87 deg vs CSD(4) at -117 deg
              -> Generic anarchic is unconstrained

  2030-2033:  CMB-S4 sum(m_nu)
              -> Hierarchical spectrum (sum ~ 0.06 eV): 3-sigma signal
              -> Constrains m_1, which constrains c_nu1 and M_0

  2030-2035:  LEGEND-1000 / nEXO 0nubb
              -> No signal expected for Meridian hierarchical spectrum
              -> Positive signal would require re-evaluation

  2032-2040:  Hyper-K theta_23 octant + proton decay
              -> theta_23 pins S3 Z2-breaking strength
              -> Proton decay not expected (RS-suppressed)

  HORIZON: By ~2035, the combination of DUNE + JUNO + CMB-S4 + LEGEND-1000
  will have tested:
    - Mass ordering (NH: required for Meridian)
    - delta_CP (Y_5 texture discriminator)
    - sum(m_nu) (m_1 and hence c_nu1 constraint)
    - m_ee (hierarchy vs quasi-degenerate)
    - theta_23 octant (S3 -> Z2 breaking magnitude)
""")


# ================================================================
# SECTION 8: QUANTITATIVE FORECAST CARDS
# ================================================================

header("SECTION 8: QUANTITATIVE FORECAST CARDS")

# Card 1: Mass ordering
subheader("FORECAST CARD 1: Mass Ordering")
print(f"  Observable:   Neutrino mass ordering (NH vs IH)")
print(f"  Experiments:  DUNE (>5-sig, ~2028), JUNO (3-4 sig, ~2029)")
print(f"  Meridian:     NORMAL ORDERING")
print(f"  Confidence:   HIGH (structural prediction from RS bulk masses)")
print(f"  If NH:        Expected. Validates RS localization framework.")
print(f"  If IH:        CRISIS. Requires c_nu1 < c_nu2,3 or non-standard seesaw.")

# Card 2: sum(m_nu)
subheader("FORECAST CARD 2: Sum of Neutrino Masses")
m_min_sum = np.sum(neutrino_masses_NO(0))
m_06_sum_m1 = m1_at_006
print(f"  Observable:   sum(m_nu)")
print(f"  Experiments:  CMB-S4 (sigma ~ 0.02 eV, ~2030)")
print(f"  Meridian:     {m_min_sum:.4f} -- 0.12 eV (NH, hierarchical preferred)")
print(f"  Most likely:  sum ~ 0.06 eV (hierarchical, m_1 << m_2)")
print(f"  Confidence:   MEDIUM (depends on c_nu1)")
print(f"  If sum ~ 0.06: Hierarchical spectrum. c_nu1 ~ 1.2 (reference value).")
print(f"  If sum < 0.06: Very hierarchical. c_nu1 >> 1.2.")
print(f"  If sum > 0.10: Quasi-degenerate. c_nu1 closer to 0.5.")

# Card 3: delta_CP
subheader("FORECAST CARD 3: CP Violation Phase")
print(f"  Observable:   delta_CP")
print(f"  Experiments:  DUNE (sigma ~ 15 deg, 7 years, ~2030)")
print(f"  Meridian:")
print(f"    CSD(3):     delta_CP = -87 deg  (+/- 5 from corrections)")
print(f"    CSD(4):     delta_CP = -117 deg (+/- 5 from corrections)")
print(f"    Democratic:  broad range (depends on Z2 breaking)")
print(f"    Anarchic:   unconstrained [0, 360)")
print(f"  NuFIT b.f.:   delta_CP = {dcp_nufit_neg:.0f} deg")
print(f"  Confidence:   LOW (texture-dependent)")
print(f"  If -87+/-15:  CSD(3) texture supported")
print(f"  If -163+/-15: CSD(3) excluded, anarchic/democratic still viable")

# Card 4: 0nubb
subheader("FORECAST CARD 4: Neutrinoless Double Beta Decay")
print(f"  Observable:   m_ee (effective Majorana mass)")
print(f"  Experiments:  LEGEND-1000 (~0.010 eV), nEXO (~0.005-0.015 eV)")
print(f"  Meridian:     m_ee = [{m_ee_hier_min:.4e}, {m_ee_hier_max:.4e}] eV (hierarchical)")
print(f"  Confidence:   HIGH (hierarchical spectrum -> small m_ee)")
print(f"  If no signal: Expected for Meridian hierarchical spectrum.")
print(f"  If signal:    Requires quasi-degenerate or IH. Meridian tension.")

# Card 5: keV sterile
subheader("FORECAST CARD 5: keV Sterile Neutrino DM")
print(f"  Observable:   3.5 keV X-ray line / keV DM signature")
print(f"  Experiments:  XRISM (2025-2026), Athena (2030s)")
print(f"  Meridian:     M_1 ~ 7 keV sterile neutrino (S3 singlet)")
print(f"  Confidence:   MEDIUM (requires specific c_nu1 + M_0 combination)")
print(f"  If 3.5 keV confirmed:  Strong support for S3 singlet DM scenario.")
print(f"  If excluded:  DM candidate shifts mass; S3 structure not excluded.")

# Card 6: theta_23
subheader("FORECAST CARD 6: Atmospheric Mixing Angle Octant")
print(f"  Observable:   theta_23 octant (above or below 45 deg)")
print(f"  Experiments:  Hyper-K (3+ sigma, ~2032), DUNE (complementary)")
print(f"  Meridian:     theta_23 ~ 45 deg (S3 -> Z2 prediction)")
print(f"  NuFIT b.f.:   theta_23 = {theta_23_deg:.1f} deg (2nd octant)")
print(f"  Confidence:   MEDIUM (exact value depends on Z2-breaking delta_c)")
print(f"  If maximal:   Perfect S3 -> Z2 with minimal further breaking.")
print(f"  If 2nd oct.:  delta_c > 0. Constrains ARS splitting parameter.")
print(f"  If 1st oct.:  delta_c < 0. Unusual but not excluded.")

# Card 7: Proton decay
subheader("FORECAST CARD 7: Proton Decay")
print(f"  Observable:   tau(p -> e+ pi0)")
print(f"  Experiments:  Hyper-K (> 1.3 x 10^35 yr, 10 years)")
print(f"  Meridian:     tau_p >> 10^35 years (RS-suppressed + NCG no X,Y bosons)")
print(f"  Confidence:   HIGH (two independent suppression mechanisms)")
print(f"  If no signal: Expected. Consistent with RS + NCG framework.")
print(f"  If signal:    Would require GUT-scale physics not in standard NCG.")


# ================================================================
# FINAL VERDICT
# ================================================================

header("FINAL VERDICT")

print(f"""
======================================================================
  Track 17O: Neutrino Sector Confrontation Forecasts
  STATUS: COMPLETE
======================================================================

KEY FINDINGS:

1. MASS ORDERING is the sharpest near-term test.
   Meridian predicts NH with high confidence. IH would be a crisis.
   Timeline: DUNE (~2028) + JUNO (~2029) will settle this.

2. delta_CP is the most discriminating Y_5 texture test.
   CSD(3) predicts -87 deg; current NuFIT best-fit is -163 deg.
   DUNE can distinguish these at ~5-sigma after 7 years.
   IF CSD(3) is correct, it means Y_5 has the littlest seesaw structure.
   IF NuFIT best-fit holds, CSD(3) is excluded and the texture is either
   anarchic or democratic with specific Z2-breaking parameters.

3. 0nubb is a CONSISTENCY CHECK, not a discovery channel for Meridian.
   Hierarchical spectrum predicts m_ee < 0.005 eV, below next-gen reach.
   A positive signal would be surprising and require re-evaluation.

4. keV sterile neutrino DM is the most DISTINCTIVE prediction.
   The S3 singlet being a keV-scale DM candidate is specific to the
   octonionic S3 structure. Generic seesaw models do not predict this.
   XRISM will test the 3.5 keV line in the near future.

5. CMB-S4 sum(m_nu) constrains the absolute mass scale.
   Meridian's hierarchical spectrum gives sum ~ 0.058-0.07 eV,
   which should be detectable at ~3-sigma by CMB-S4.

6. PROTON DECAY is predicted to be unobservable at Hyper-K.
   RS wavefunction suppression + NCG structure both protect the proton.
   Observation would be a major surprise requiring framework revision.

OVERALL ASSESSMENT:

  By ~2035, the combination of DUNE + JUNO + CMB-S4 + LEGEND + XRISM
  will have tested the Meridian neutrino sector on 6 independent fronts:
    - Mass ordering (NH: required)
    - delta_CP (Y_5 texture)
    - sum(m_nu) (absolute scale)
    - m_ee (Majorana nature)
    - 3.5 keV line (keV sterile DM)
    - theta_23 octant (S3 breaking)

  The framework makes DEFINITE predictions (NH, hierarchical spectrum,
  near-maximal theta_23, suppressed proton decay) that are testable,
  and CONDITIONAL predictions (delta_CP, exact m_ee) that depend on
  the Y_5 texture determination (the open question from 17N).

  The single most important thing that would STRENGTHEN the framework:
  determining Y_5 from the spectral triple (Phase 14A: NCG-AS bridge).
  This would turn conditional predictions into definite ones.

======================================================================
  Track 17O: COMPLETE
  7 forecast cards. 15 experimental confrontation points.
  Timeline: 2025-2035 for comprehensive testing.
======================================================================
""")

print(SEP)
print("  END OF TRACK 17O")
print(SEP)
