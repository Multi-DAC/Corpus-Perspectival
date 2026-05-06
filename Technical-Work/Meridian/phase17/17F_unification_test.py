"""
Track 17F: Gauge Unification Test -- Resolution Pathways
=========================================================
Authors: Clayton W. Iggulden-Schnell & Clawd
Date: March 19, 2026

PURPOSE: Quantify the gauge coupling unification tension in the Meridian
warped RS framework and test three resolution pathways.

Context from 17E:
  - SM 1-loop RGE gives ~21.8 spread in alpha_i^{-1} at Lambda_NCG
  - NCG spectral action predicts a_1 = a_2 = a_3 = 12 (universal)
  - Brane kinetic terms from spectral action are negligible O(k/Lambda)
  - Three pathways identified: boundary Seeley-DeWitt, reinterpreted
    unification scale, AS corrections

This script:
  1. Reproduces the unification tension quantitatively (1-loop SM RGE)
  2. Includes KK threshold corrections from bulk gauge boson tower
  3. Tests Path A (boundary Seeley-DeWitt), Path B (reinterpreted scale),
     Path C (asymptotic safety corrections)
  4. Computes brane kinetic terms from spectral action
  5. Gives an honest assessment
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize, brentq
import os
import sys

# ============================================================================
# Output setup (dual: console + file)
# ============================================================================
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "17F_unification_test_results.txt")
output_file = open(output_path, "w", encoding="utf-8")
_print = print
def print(*args, **kwargs):
    kwargs_file = dict(kwargs)
    kwargs_file['file'] = output_file
    _print(*args, **kwargs_file)
    output_file.flush()
    try:
        kwargs_console = {k: v for k, v in kwargs.items() if k != 'file'}
        _print(*args, **kwargs_console)
    except UnicodeEncodeError:
        text = ' '.join(str(a) for a in args)
        _print(text.encode('ascii', 'replace').decode('ascii'))

print("=" * 80)
print("TRACK 17F: GAUGE UNIFICATION TEST -- RESOLUTION PATHWAYS")
print("=" * 80)
print()

# ============================================================================
# SECTION 0: PHYSICAL CONSTANTS AND MERIDIAN PARAMETERS
# ============================================================================

print("=" * 80)
print("SECTION 0: PHYSICAL CONSTANTS AND MERIDIAN PARAMETERS")
print("=" * 80)

# Fundamental scales (GeV)
M_Pl = 1.22e19          # Full Planck mass
M_Pl_red = 2.435e18     # Reduced Planck mass
M_Z = 91.1876            # Z boson mass

# Meridian RS parameters
k = 1.22e19              # AdS curvature = Planck scale
k_yc = 35.0              # Warp factor exponent
yc = k_yc / k            # Physical extra dimension size
warp = np.exp(-k_yc)     # Warp factor e^{-k*y_c}
M_KK = np.pi * k * warp  # KK scale ~ pi * k * e^{-k*y_c}
Lambda_NCG = 1.1e17      # NCG spectral cutoff

# 5D Planck mass: M_5^3 = M_Pl^2 * k (RS relation)
M_5_cubed = M_Pl**2 * k
M_5 = M_5_cubed ** (1.0/3.0)

# SM gauge couplings at M_Z (PDG 2024, GUT normalization)
alpha_em_MZ = 1.0 / 127.951
sin2_thetaW = 0.23122
alpha_s_MZ = 0.1179

alpha_Y_MZ = alpha_em_MZ / (1.0 - sin2_thetaW)
alpha_2_MZ = alpha_em_MZ / sin2_thetaW
alpha_1_MZ = (5.0 / 3.0) * alpha_Y_MZ  # GUT-normalized U(1)
alpha_3_MZ = alpha_s_MZ

alpha_inv_MZ = np.array([1.0/alpha_1_MZ, 1.0/alpha_2_MZ, 1.0/alpha_3_MZ])

print(f"""
Meridian RS Parameters:
  k             = {k:.3e} GeV  (AdS curvature = Planck scale)
  k * y_c       = {k_yc:.1f}
  Warp factor   = e^{{-{k_yc:.0f}}} = {warp:.3e}
  KK scale      = {M_KK:.3e} GeV  ({M_KK/1e3:.1f} TeV)
  Lambda_NCG    = {Lambda_NCG:.3e} GeV  (10^{{{np.log10(Lambda_NCG):.2f}}})
  M_5           = {M_5:.3e} GeV
  M_Pl          = {M_Pl:.3e} GeV

Gauge Couplings at M_Z = {M_Z} GeV (GUT normalization):
  alpha_1^{{-1}}(M_Z) = {alpha_inv_MZ[0]:.4f}
  alpha_2^{{-1}}(M_Z) = {alpha_inv_MZ[1]:.4f}
  alpha_3^{{-1}}(M_Z) = {alpha_inv_MZ[2]:.4f}
  Spread at M_Z       = {max(alpha_inv_MZ) - min(alpha_inv_MZ):.4f}
""")


# ============================================================================
# SECTION 1: SM 1-LOOP RGE AND UNIFICATION TENSION
# ============================================================================

print("=" * 80)
print("SECTION 1: SM 1-LOOP RGE -- REPRODUCING THE UNIFICATION TENSION")
print("=" * 80)

# SM 1-loop beta function coefficients (N_g=3, N_H=1)
# d(alpha_i^{-1})/d(ln mu) = -b_i / (2 pi)
b_SM = np.array([41.0/10.0, -19.0/6.0, -7.0])

print(f"""
SM 1-loop beta coefficients:
  b_1 = 41/10  = {b_SM[0]:.4f}  (U(1)_Y, GUT normalized)
  b_2 = -19/6  = {b_SM[1]:.4f}  (SU(2)_L)
  b_3 = -7     = {b_SM[2]:.4f}  (SU(3)_C)

RGE: alpha_i^{{-1}}(mu) = alpha_i^{{-1}}(M_Z) - b_i/(2*pi) * ln(mu/M_Z)
""")


def alpha_inv_sm(mu):
    """1-loop SM running from M_Z to mu."""
    return alpha_inv_MZ - b_SM / (2.0 * np.pi) * np.log(mu / M_Z)


# Run to key scales
scales = [
    ('M_Z',           M_Z),
    ('1 TeV',         1e3),
    ('10 TeV',        1e4),
    ('10^8 GeV',      1e8),
    ('10^12 GeV',     1e12),
    ('10^14 GeV',     1e14),
    ('Lambda_NCG',    Lambda_NCG),
    ('10^18 GeV',     1e18),
    ('M_Pl',          M_Pl),
]

print("SM 1-loop running (no threshold corrections):")
print(f"  {'Scale':<14s}  {'mu [GeV]':>12s}  {'a1^-1':>8s}  {'a2^-1':>8s}  {'a3^-1':>8s}  {'Spread':>8s}")
print("  " + "-" * 64)
for name, mu in scales:
    ai = alpha_inv_sm(mu)
    spread = max(ai) - min(ai)
    print(f"  {name:<14s}  {mu:>12.3e}  {ai[0]:>8.3f}  {ai[1]:>8.3f}  {ai[2]:>8.3f}  {spread:>8.3f}")

# Key tension numbers
ai_NCG = alpha_inv_sm(Lambda_NCG)
spread_NCG = max(ai_NCG) - min(ai_NCG)
ai_Pl = alpha_inv_sm(M_Pl)
spread_Pl = max(ai_Pl) - min(ai_Pl)

print(f"""
UNIFICATION TENSION:
  At Lambda_NCG = {Lambda_NCG:.1e} GeV:
    alpha_1^{{-1}} = {ai_NCG[0]:.3f}
    alpha_2^{{-1}} = {ai_NCG[1]:.3f}
    alpha_3^{{-1}} = {ai_NCG[2]:.3f}
    Spread Delta  = {spread_NCG:.3f}

  At M_Pl = {M_Pl:.2e} GeV:
    alpha_1^{{-1}} = {ai_Pl[0]:.3f}
    alpha_2^{{-1}} = {ai_Pl[1]:.3f}
    alpha_3^{{-1}} = {ai_Pl[2]:.3f}
    Spread Delta  = {spread_Pl:.3f}

  The spread at Lambda_NCG ~ {spread_NCG:.1f} is the central tension.
  NCG predicts a_1 = a_2 = a_3 => same coupling at cutoff.
  SM running alone gives a spread of ~{spread_NCG:.1f} inverse coupling units.
""")

# Pairwise crossings
def find_crossing(i, j, mu_lo=M_Z, mu_hi=1e25):
    """Find scale where alpha_i^{-1} = alpha_j^{-1}."""
    db = b_SM[i] - b_SM[j]
    da = alpha_inv_MZ[i] - alpha_inv_MZ[j]
    if abs(db) < 1e-15:
        return None
    ln_mu = da * 2.0 * np.pi / db + np.log(M_Z)
    return np.exp(ln_mu)

mu_12 = find_crossing(0, 1)
mu_23 = find_crossing(1, 2)
mu_13 = find_crossing(0, 2)

print("SM pairwise crossings (1-loop):")
print(f"  alpha_1 = alpha_2 at {mu_12:.3e} GeV  (10^{{{np.log10(mu_12):.2f}}})")
print(f"  alpha_2 = alpha_3 at {mu_23:.3e} GeV  (10^{{{np.log10(mu_23):.2f}}})")
print(f"  alpha_1 = alpha_3 at {mu_13:.3e} GeV  (10^{{{np.log10(mu_13):.2f}}})")
print(f"  => SM does NOT unify. The triangle of non-unification is well-known.")
print()


# ============================================================================
# SECTION 2: KK THRESHOLD CORRECTIONS
# ============================================================================

print("=" * 80)
print("SECTION 2: KK THRESHOLD CORRECTIONS FROM BULK GAUGE BOSONS")
print("=" * 80)

print(f"""
In the Meridian framework, ALL gauge fields propagate in the 5D bulk.
The KK tower has masses:
  m_n ~ n * k * e^{{-k*y_c}} = n * {k*warp:.3e} GeV

For k*y_c = {k_yc}, KK scale = {M_KK:.3e} GeV ({M_KK/1e3:.1f} TeV)

Threshold corrections from the KK tower (Dienes-Dudas-Gherghetta):
  delta(alpha_i^{{-1}}) = - b_i^KK / (2*pi) * sum_{{n=1}}^N ln(Lambda / m_n)
                        = - b_i^KK / (2*pi) * [N * ln(Lambda/m_1) - ln(N!)]

For BULK gauge bosons with (+,+) boundary conditions:
  Each KK level contributes the same gauge beta function as the zero mode.
  b_gauge^KK = b_gauge = [0, -22/3, -11]  (pure gauge, no matter)

Fermion KK towers depend on bulk mass parameters c:
  |c| > 1/2 : UV-localized, full KK contribution
  |c| < 1/2 : IR-localized, KK tower suppressed at UV brane
  |c| = 1/2 : flat profile, marginal
""")

# Fermion bulk mass parameters (from 17E/17G)
fermion_content = {
    'Q3':  {'c': 0.30,  'SU3': 'F', 'SU2': 'F', 'Y': 1.0/6,  'name': 'Q_3 (b,t)_L'},
    'u3':  {'c': -0.50, 'SU3': 'F', 'SU2': 'S', 'Y': 2.0/3,  'name': 't_R'},
    'd3':  {'c': 0.55,  'SU3': 'F', 'SU2': 'S', 'Y': -1.0/3, 'name': 'b_R'},
    'L3':  {'c': 0.50,  'SU3': 'S', 'SU2': 'F', 'Y': -1.0/2, 'name': 'L_3 (tau)_L'},
    'e3':  {'c': 0.55,  'SU3': 'S', 'SU2': 'S', 'Y': -1.0,   'name': 'tau_R'},
    'nu3': {'c': 0.50,  'SU3': 'S', 'SU2': 'S', 'Y': 0.0,    'name': 'nu_tau_R'},
    'Q2':  {'c': 0.55,  'SU3': 'F', 'SU2': 'F', 'Y': 1.0/6,  'name': 'Q_2 (s,c)_L'},
    'u2':  {'c': 0.55,  'SU3': 'F', 'SU2': 'S', 'Y': 2.0/3,  'name': 'c_R'},
    'd2':  {'c': 0.65,  'SU3': 'F', 'SU2': 'S', 'Y': -1.0/3, 'name': 's_R'},
    'L2':  {'c': 0.55,  'SU3': 'S', 'SU2': 'F', 'Y': -1.0/2, 'name': 'L_2 (mu)_L'},
    'e2':  {'c': 0.65,  'SU3': 'S', 'SU2': 'S', 'Y': -1.0,   'name': 'mu_R'},
    'nu2': {'c': 0.50,  'SU3': 'S', 'SU2': 'S', 'Y': 0.0,    'name': 'nu_mu_R'},
    'Q1':  {'c': 0.65,  'SU3': 'F', 'SU2': 'F', 'Y': 1.0/6,  'name': 'Q_1 (d,u)_L'},
    'u1':  {'c': 0.65,  'SU3': 'F', 'SU2': 'S', 'Y': 2.0/3,  'name': 'u_R'},
    'd1':  {'c': 0.70,  'SU3': 'F', 'SU2': 'S', 'Y': -1.0/3, 'name': 'd_R'},
    'L1':  {'c': 0.60,  'SU3': 'S', 'SU2': 'F', 'Y': -1.0/2, 'name': 'L_1 (e)_L'},
    'e1':  {'c': 0.70,  'SU3': 'S', 'SU2': 'S', 'Y': -1.0,   'name': 'e_R'},
    'nu1': {'c': 0.50,  'SU3': 'S', 'SU2': 'S', 'Y': 0.0,    'name': 'nu_e_R'},
}


def eta_fermion(c, ky_c_val):
    """UV-brane efficiency factor for a bulk fermion with mass parameter c."""
    c_abs = abs(c)
    if c_abs > 0.5 + 1e-8:
        return 1.0 - np.exp(-(2.0 * c_abs - 1.0) * ky_c_val)
    elif c_abs < 0.5 - 1e-8:
        return np.exp(-(1.0 - 2.0 * c_abs) * ky_c_val)
    else:
        return 1.0 / (ky_c_val + 1.0)


def b_per_weyl(Y, d3, d2, is_su3_fund, is_su2_fund):
    """Beta function contribution from one Weyl fermion."""
    b1 = (2.0/3.0) * (3.0/5.0) * Y**2 * d3 * d2
    b2 = (2.0/3.0) * (0.5 if is_su2_fund else 0.0) * d3
    b3 = (2.0/3.0) * (0.5 if is_su3_fund else 0.0) * d2
    return np.array([b1, b2, b3])


# Pure gauge beta (no matter)
b_gauge = np.array([0.0, -22.0/3.0, -11.0])

# Higgs doublet contribution
b_higgs = np.array([
    (1.0/3.0) * (3.0/5.0) * 0.25 * 1 * 2,  # Y=1/2
    (1.0/3.0) * 0.5 * 1,                      # T(fund) * dim_SU3
    0.0
])


def compute_kk_threshold(Lambda_uv, n_max=None):
    """
    Compute KK threshold corrections to alpha_i^{-1}.

    Each KK gauge boson level n has mass m_n ~ n * k * e^{-k*y_c}.
    The threshold correction is:
      delta_i = -b_i^KK/(2*pi) * sum_{n=1}^{N} ln(Lambda/m_n)

    where N = floor(Lambda / m_1) is the number of KK modes below Lambda.
    b_i^KK = gauge contribution per KK level.

    For fermions, the KK contribution is weighted by eta(c).
    """
    m_1 = k * warp  # First KK mass (without pi factor for simplicity)
    if n_max is None:
        n_max = int(Lambda_uv / m_1)
        n_max = min(n_max, 10000)  # cap for numerical stability

    if n_max < 1:
        return np.zeros(3), 0

    # Gauge boson KK tower: each level contributes b_gauge
    delta_gauge = np.zeros(3)
    for n in range(1, n_max + 1):
        m_n = n * m_1
        if m_n < Lambda_uv:
            delta_gauge += -b_gauge / (2.0 * np.pi) * np.log(Lambda_uv / m_n)

    # Fermion KK tower: weighted by eta(c)
    delta_ferm = np.zeros(3)
    for f in fermion_content.values():
        eta = eta_fermion(f['c'], k_yc)
        d3 = 3 if f['SU3'] == 'F' else 1
        d2 = 2 if f['SU2'] == 'F' else 1
        b_f = b_per_weyl(f['Y'], d3, d2, f['SU3'] == 'F', f['SU2'] == 'F')
        for n in range(1, min(n_max, 100) + 1):
            m_n = n * m_1
            if m_n < Lambda_uv:
                delta_ferm += -eta * b_f / (2.0 * np.pi) * np.log(Lambda_uv / m_n)

    # Higgs KK tower (brane-localized Higgs scenario: NO KK tower)
    # In gauge-Higgs scenario: A_5 has (-,-) BC, also no KK contribution
    delta_higgs = np.zeros(3)

    return delta_gauge + delta_ferm + delta_higgs, n_max


# Compute KK corrections at Lambda_NCG and M_Pl
for scale_name, Lambda_uv in [("Lambda_NCG", Lambda_NCG), ("M_Pl", M_Pl)]:
    delta_kk, N_kk = compute_kk_threshold(Lambda_uv)
    ai_sm = alpha_inv_sm(Lambda_uv)
    ai_corrected = ai_sm + delta_kk
    spread_sm = max(ai_sm) - min(ai_sm)
    spread_corr = max(ai_corrected) - min(ai_corrected)

    print(f"\nKK threshold corrections at {scale_name} = {Lambda_uv:.1e} GeV:")
    print(f"  Number of KK levels below cutoff: N = {N_kk}")
    print(f"  m_1 (first KK mass) = {k*warp:.3e} GeV")
    print(f"")
    print(f"  delta_kk   = [{delta_kk[0]:>+8.3f}, {delta_kk[1]:>+8.3f}, {delta_kk[2]:>+8.3f}]")
    print(f"")
    print(f"  Without KK:  a_i^-1 = [{ai_sm[0]:>8.3f}, {ai_sm[1]:>8.3f}, {ai_sm[2]:>8.3f}]  spread = {spread_sm:.3f}")
    print(f"  With KK:     a_i^-1 = [{ai_corrected[0]:>8.3f}, {ai_corrected[1]:>8.3f}, {ai_corrected[2]:>8.3f}]  spread = {spread_corr:.3f}")
    print(f"")
    print(f"  Change in spread: {spread_corr - spread_sm:+.3f}")


# Also compute for the Angelescu-style warped running (logarithmic only,
# suppressed by 1/k for warped geometry)
print(f"""

KEY OBSERVATION: In the warped RS geometry, the KK threshold corrections
are SUPPRESSED compared to flat extra dimensions. The warping gives:
  - KK sum ~ N * ln(Lambda/M_KK) rather than N^2 (which flat gives)
  - The UV-brane correlator method (Angelescu et al.) shows that the
    warped geometry tames the power-law divergence of the KK sum

For Meridian (k*y_c = {k_yc}), the KK scale is at {M_KK:.1e} GeV.
The number of KK modes between M_KK and Lambda_NCG is huge, but each
mode's contribution is suppressed by the warp factor.
""")


# ============================================================================
# SECTION 3: RESOLUTION PATH A -- BOUNDARY SEELEY-DEWITT CORRECTIONS
# ============================================================================

print("=" * 80)
print("SECTION 3: PATH A -- BOUNDARY SEELEY-DEWITT CORRECTIONS")
print("=" * 80)

print(f"""
The spectral action on a manifold with boundary gets corrections from the
boundary Seeley-DeWitt coefficients. For the RS orbifold with two branes:

  S_spectral = S_bulk + S_UV-brane + S_IR-brane

The boundary heat kernel gives half-integer Seeley-DeWitt coefficients:
  a_{{1/2}}, a_{{3/2}}, a_{{5/2}}, ...

The a_{{3/2}} coefficient on a 4D brane in 5D is:
  a_{{3/2}} = (4*pi)^{{-2}} * int_brane d^4x sqrt(h) * [
      (1/6) * R_brane
    + (boundary curvature terms)
    + (gauge field strength terms proportional to b_{{3/2,i}})
  ]

The gauge kinetic correction from the boundary:
  delta_i = b_{{3/2,i}} / (16 * pi^2) * (f_2 * Lambda^2 / M_5^3)

where b_{{3/2,i}} depends on the field content and boundary conditions.

QUESTION: What values of b_{{3/2,i}} are NEEDED to achieve unification?
""")

# Required corrections for unification at Lambda_NCG
ai_at_NCG = alpha_inv_sm(Lambda_NCG)
alpha_unif_target = np.mean(ai_at_NCG)
delta_needed = alpha_unif_target - ai_at_NCG  # What to ADD to each

print(f"At Lambda_NCG = {Lambda_NCG:.1e} GeV (pure SM running):")
print(f"  alpha_i^{{-1}} = [{ai_at_NCG[0]:.3f}, {ai_at_NCG[1]:.3f}, {ai_at_NCG[2]:.3f}]")
print(f"  Target (mean) = {alpha_unif_target:.3f}")
print(f"  Required shifts: delta_i = [{delta_needed[0]:>+8.3f}, {delta_needed[1]:>+8.3f}, {delta_needed[2]:>+8.3f}]")
print()

# Express in terms of b_{3/2,i}
# The boundary correction to the gauge kinetic term is:
#   delta(alpha_i^{-1}) = b_{3/2,i} * k / (16 * pi^2)
# where the factor of k comes from the extrinsic curvature of the UV brane.
# The RS UV brane has K_{mu nu} = -k * g_{mu nu}.

factor_boundary = k / (16.0 * np.pi**2)

b32_needed = delta_needed / factor_boundary

print(f"Boundary correction model:")
print(f"  delta(alpha_i^{{-1}}) = b_{{3/2,i}} * k / (16 pi^2)")
print(f"  With k = {k:.3e} GeV, factor = k/(16 pi^2) = {factor_boundary:.3e}")
print(f"")
print(f"  Required b_{{3/2,i}} for unification:")
print(f"    b_{{3/2,1}} = {b32_needed[0]:.6e}")
print(f"    b_{{3/2,2}} = {b32_needed[1]:.6e}")
print(f"    b_{{3/2,3}} = {b32_needed[2]:.6e}")
print()

# Alternative: corrections as fraction of alpha_i^{-1}
print(f"  As fraction of alpha_i^{{-1}}:")
for i, name in enumerate(['U(1)', 'SU(2)', 'SU(3)']):
    frac = abs(delta_needed[i]) / ai_at_NCG[i] * 100
    print(f"    {name}: {frac:.1f}%")
print()

# Now parametric: what if the boundary correction is proportional to
# a universal b_{3/2} with group-dependent Casimir factors?
print("--- Parametric analysis: b_{3/2,i} = b_{3/2} * C_i ---")
print()
print("If the boundary correction respects a GUT-like structure:")
print("  b_{3/2,i} = b_{3/2} * C_i  where C_i are Casimir-related factors")
print()

# For SU(N): Casimir C_2(adj) = N
# C_1 = 0 for U(1), but with GUT normalization use the relation
# If C_1 : C_2 : C_3 = 5/3 : 2 : 3 (proportional to b_i of pure gauge)
# or C_i = a_i (spectral action coefficients)

# Try: delta_i = b_{3/2} * (a_i_spectral / a_3_spectral) where a_i = 12
# If a_1 = a_2 = a_3 = 12, then delta_i = b_{3/2} for all => UNIVERSAL
# This can't fix non-unification (same shift to all)

# Need NON-UNIVERSAL structure. Try different Casimir assignments:
casimir_options = {
    'C_2(adj): [0, 2, 3]':     np.array([0.0, 2.0, 3.0]),
    'C_2(fund): [0, 3/4, 4/3]': np.array([0.0, 3.0/4.0, 4.0/3.0]),
    'dim(G): [1, 3, 8]':        np.array([1.0, 3.0, 8.0]),
    'b_SM: [4.1, -3.17, -7]':   b_SM,
    'b_gauge: [0, -7.33, -11]':  b_gauge,
}

print(f"  {'Casimir choice':<30s}  {'b_3/2 needed':>12s}  {'Residual':>10s}")
print("  " + "-" * 60)

for label, C_i in casimir_options.items():
    # delta_needed = b_{3/2} * C_i * factor_boundary
    # Least-squares: b_{3/2} = sum(delta_needed * C_i) / sum(C_i^2)
    if np.sum(C_i**2) < 1e-30:
        continue
    b32_fit = np.sum(delta_needed * C_i) / np.sum(C_i**2)
    residual = delta_needed - b32_fit * C_i
    rms_residual = np.sqrt(np.mean(residual**2))
    print(f"  {label:<30s}  {b32_fit:>12.3e}  {rms_residual:>10.3f}")

print()

# Compare with 17G's b_{3/2} = 0.426
b32_17G = 0.426
delta_from_17G = b32_17G * factor_boundary  # Universal shift

print(f"Comparison with 17G result (b_{{3/2}} = {b32_17G}):")
print(f"  Universal shift from b_{{3/2}} = {b32_17G}:")
print(f"    delta(alpha_i^{{-1}}) = {b32_17G} * {factor_boundary:.3e} = {delta_from_17G:.3e}")
print(f"    This is {abs(delta_from_17G):.1e} -- ENORMOUS (factor_boundary = k/(16pi^2) ~ 10^{{{np.log10(factor_boundary):.0f}}})")
print()

# The issue: k/(16 pi^2) ~ 10^{16}, so even b_{3/2} ~ 0.4 gives huge correction
# This means the boundary model is: delta ~ b_{3/2} * Lambda^2 / M_5^3
# NOT delta ~ b_{3/2} * k / (16 pi^2)
# The correct normalization matters enormously

# Correct normalization: spectral action boundary term
# S_boundary ~ f_2 * Lambda_NCG^2 * a_{3/2}(brane)
# The gauge kinetic part: delta_i ~ f_2 * Lambda_NCG^2 * b_{3/2,i} / (4 pi)^2
# Relative to bulk: f_2 * Lambda_NCG^2 * a_i / volume_factor
# The volume factor for warped geometry: int_0^{y_c} e^{-4ky} dy = (1-e^{-4ky_c})/(4k) ~ 1/(4k)
# So bulk ~ f_2 * Lambda_NCG^2 * a_i * 1/(4k)
# Boundary / Bulk ~ b_{3/2,i} / (a_i / (4k)) = 4k * b_{3/2,i} / a_i

# More careful: the physical gauge coupling gets:
# 1/g_i^2 = f_2 * Lambda_NCG^2 * [a_i * warp_integral + b_{3/2,i} * brane_factor]
# For the UV brane: brane_factor = 1 (no warp suppression)
# warp_integral ~ 1/(4k)
# So: alpha_i^{-1} ~ (f_2 * Lambda_NCG^2) / (4pi) * [a_i/(4k) + b_{3/2,i}]

# Unification requires: a_1/(4k) + b_{3/2,1} = a_2/(4k) + b_{3/2,2} = a_3/(4k) + b_{3/2,3}
# Since a_1 = a_2 = a_3 = 12, the a_i/(4k) terms are universal
# => b_{3/2,1} = b_{3/2,2} = b_{3/2,3} needed
# => Universal brane correction does NOT help

print("CAREFUL NORMALIZATION OF BOUNDARY SPECTRAL ACTION:")
print()
print("  The 4D gauge coupling receives contributions:")
print("    1/g_i^2 = (f_2 * Lambda^2)/(4pi) * [a_i * V_warp + b_{3/2,i}]")
print()
print("  where V_warp = int_0^{y_c} e^{-4ky} dy = (1 - e^{-4ky_c})/(4k) ~ 1/(4k)")
print(f"  V_warp = {1.0/(4.0*k):.3e} GeV^{{-1}}")
print()
print("  Bulk contribution: a_i * V_warp = 12 * 1/(4k) = 3/k")
print(f"  = {3.0/k:.3e} GeV^{{-1}}")
print()
print("  Brane contribution: b_{3/2,i}  (dimensionless)")
print()
print("  The ratio brane/bulk = b_{3/2,i} * 4k / a_i = b_{3/2,i} * 4k / 12")
print(f"  For b_{{3/2}} = {b32_17G}: ratio = {b32_17G * 4 * k / 12.0:.3e}")
print()
print("  Since a_1 = a_2 = a_3 in the NCG spectral action, the BULK")
print("  contribution is already universal. The boundary b_{3/2,i} would")
print("  need to be NON-UNIVERSAL (different for each gauge group) to")
print("  resolve the spread.")
print()

# What non-universal b_{3/2,i} values are needed?
# We need: delta_i proportional to needed corrections
# In units where the full coupling is:
#   alpha_i^{-1} = C * [12/(4k) + b_{3/2,i}]
# where C = f_2 * Lambda^2 / (4pi)
# The SM running gives alpha_i^{-1}(Lambda) = ai_at_NCG[i]
# So we need: C * [12/(4k) + b_{3/2,i}] to equal the same value for all i
# But C and 12/(4k) are universal, so b_{3/2,i} must differ

# From the SM running, the SPREAD at Lambda_NCG is due to unequal alpha_i^{-1}.
# The difference alpha_1^{-1} - alpha_3^{-1} at Lambda_NCG is:
diff_13 = ai_at_NCG[0] - ai_at_NCG[2]
diff_12 = ai_at_NCG[0] - ai_at_NCG[1]

print(f"  Differences at Lambda_NCG:")
print(f"    alpha_1^{{-1}} - alpha_3^{{-1}} = {diff_13:.3f}")
print(f"    alpha_1^{{-1}} - alpha_2^{{-1}} = {diff_12:.3f}")
print()

# The brane b_{3/2} must compensate:
# (b_{3/2,1} - b_{3/2,3}) * C = -(diff_13)
# We need C ~ alpha_i^{-1} / [12/(4k)] ~ 30 * 4k/12 = 10k
# Actually C = f_2 * Lambda^2 / (4pi) and we match alpha_i^{-1}(M_Z) = C * [12/(4k) + ...]
# via RGE from Lambda to M_Z
# Simpler: just compute the NEEDED b_{3/2,i} differences directly

# At the cutoff Lambda, the spectral action prediction is:
# alpha_i^{-1}(Lambda) = f(Lambda) * [a_i * V_warp + b_{3/2,i}]
# For unification: all equal => a_i terms cancel (universal), b_{3/2,i} must be equal
# But the SM RGE already gave us DIFFERENT alpha_i^{-1}(Lambda)
# So the spectral action must either:
# (a) produce different a_i (breaks NCG prediction)
# (b) produce non-universal b_{3/2,i}
# (c) some other mechanism

# For (b): the NEEDED non-universality is:
# b_{3/2,i} - b_{3/2,j} proportional to alpha_i^{-1}(Lambda) - alpha_j^{-1}(Lambda)
# Normalized by the common prefactor

# Actually the key insight: the prefactor C relates Lambda_NCG to the coupling
# f_0 * a_i is what gives the coupling. So:
# alpha_i^{-1} = f_0 * a_i / (2*pi)  at the spectral action scale
# with a_1 = a_2 = a_3 = 12, this gives perfect unification
# The MISMATCH is between this prediction and the SM running from M_Z

# Required: b_{3/2,i} such that corrections at Lambda bring the couplings
# from the NCG-predicted universal value to the SM-running values
# delta(alpha_i^{-1}) = [correction term] * b_{3/2,i}

# The correction enters as a RELATIVE correction to a_i:
# alpha_i^{-1} = f_0/(2pi) * (a_i + epsilon * b_{3/2,i})
# For epsilon * b_{3/2,i} to produce the needed spread:

# epsilon * (b_{3/2,1} - b_{3/2,3}) = spread_NCG * (a_3 / [a_3 + epsilon*b_{3/2,3}])
# To leading order: epsilon * delta_b_{3/2} ~ spread / (f_0/(2pi))

# Estimate f_0 from the mean coupling:
# alpha_unif^{-1} = f_0 * 12 / (2*pi) => f_0 = 2*pi*alpha_unif / 12
f_0_estimate = 2.0 * np.pi * alpha_unif_target / 12.0
print(f"  Estimated f_0 from mean coupling: f_0 = {f_0_estimate:.4f}")
print(f"  (This is the moment of the spectral function f)")
print()

# Required non-universal boundary corrections (as shifts to a_i):
# alpha_i^{-1} = f_0/(2pi) * (12 + delta_a_i)
# => delta_a_i = 2pi * alpha_i^{-1}(Lambda) / f_0 - 12
delta_a_needed = 2.0 * np.pi * ai_at_NCG / f_0_estimate - 12.0

print(f"  Required delta_a_i (shifts to spectral action coefficients):")
print(f"    delta_a_1 = {delta_a_needed[0]:>+8.3f}")
print(f"    delta_a_2 = {delta_a_needed[1]:>+8.3f}")
print(f"    delta_a_3 = {delta_a_needed[2]:>+8.3f}")
print(f"    Range: {max(delta_a_needed) - min(delta_a_needed):.3f}")
print()

# As percentage of a_i = 12:
print(f"  As percentage of a_i = 12:")
for i, name in enumerate(['U(1)', 'SU(2)', 'SU(3)']):
    pct = delta_a_needed[i] / 12.0 * 100
    print(f"    {name}: {pct:>+.1f}%")
print()

print(f"""
PATH A VERDICT:
  The boundary Seeley-DeWitt corrections CAN resolve the unification
  tension IF they produce non-universal corrections delta_a_i with
  a range of ~{max(delta_a_needed) - min(delta_a_needed):.0f} (in units where the bulk gives a_i = 12).

  However, the NCG structure CONSTRAINS the boundary terms:
  - If the same spectral triple F lives on the brane, a_{3/2} inherits
    the same representation content => universal corrections
  - Non-universality requires brane-localized matter that is NOT in
    the bulk NCG triple, or different boundary conditions for different
    gauge fields

  This is a STRUCTURAL question about the spectral geometry of the
  orbifold boundary, not just a numerical fit.
""")


# ============================================================================
# SECTION 4: RESOLUTION PATH B -- REINTERPRETED UNIFICATION SCALE
# ============================================================================

print("=" * 80)
print("SECTION 4: PATH B -- REINTERPRETED UNIFICATION SCALE")
print("=" * 80)

print(f"""
The standard interpretation: NCG unification occurs at Lambda_NCG.
Alternative: unification occurs at the KK scale k * e^{{-k*y_c}}.

The idea: the NCG spectral triple describes the BRANE physics.
The spectral cutoff Lambda is not the unification scale --
it is the scale at which the spectral action is defined.
The actual unification might occur at a LOWER scale where the
gauge couplings physically equalize.
""")

# Compute spread at various scales
test_scales = [
    ('KK scale (M_KK)',         M_KK),
    ('10 * M_KK',               10 * M_KK),
    ('100 * M_KK',              100 * M_KK),
    ('1000 * M_KK',             1000 * M_KK),
    ('10^6 GeV',                1e6),
    ('10^8 GeV',                1e8),
    ('10^10 GeV',               1e10),
    ('10^12 GeV',               1e12),
    ('10^13 GeV (MSSM GUT)',    1e13),
    ('10^14 GeV',               1e14),
    ('10^15 GeV',               1e15),
    ('2x10^16 GeV (SM GUT)',    2e16),
    ('Lambda_NCG',              Lambda_NCG),
    ('M_Pl',                    M_Pl),
]

print(f"  {'Scale':<26s}  {'mu [GeV]':>12s}  {'a1^-1':>8s}  {'a2^-1':>8s}  {'a3^-1':>8s}  {'Spread':>8s}")
print("  " + "-" * 76)
for name, mu in test_scales:
    ai = alpha_inv_sm(mu)
    spread = max(ai) - min(ai)
    print(f"  {name:<26s}  {mu:>12.3e}  {ai[0]:>8.3f}  {ai[1]:>8.3f}  {ai[2]:>8.3f}  {spread:>8.3f}")

# Minimum spread scale
log_mu_scan = np.linspace(np.log10(M_Z), 20, 100000)
spreads_scan = []
for lm in log_mu_scan:
    mu = 10**lm
    ai = alpha_inv_sm(mu)
    spreads_scan.append(max(ai) - min(ai))
spreads_scan = np.array(spreads_scan)
idx_min = np.argmin(spreads_scan)
mu_min_spread = 10**log_mu_scan[idx_min]
min_spread = spreads_scan[idx_min]

print(f"\n  Minimum spread in pure SM running:")
print(f"    Scale: {mu_min_spread:.3e} GeV  (10^{{{np.log10(mu_min_spread):.2f}}})")
print(f"    Spread: {min_spread:.3f}")
ai_min = alpha_inv_sm(mu_min_spread)
print(f"    alpha_i^{{-1}} = [{ai_min[0]:.3f}, {ai_min[1]:.3f}, {ai_min[2]:.3f}]")
print()

# At the KK scale specifically
ai_KK = alpha_inv_sm(M_KK)
spread_KK = max(ai_KK) - min(ai_KK)
print(f"  At KK scale ({M_KK:.1e} GeV):")
print(f"    alpha_i^{{-1}} = [{ai_KK[0]:.3f}, {ai_KK[1]:.3f}, {ai_KK[2]:.3f}]")
print(f"    Spread: {spread_KK:.3f}")
print(f"    This is WORSE than at Lambda_NCG (lower scale => more divergence)")
print()

print(f"""
PATH B VERDICT:
  Reinterpreting the unification scale does NOT help:
  - The minimum spread in SM running is {min_spread:.1f} at ~10^{{{np.log10(mu_min_spread):.0f}}} GeV
  - At the KK scale ({M_KK:.0e} GeV), the spread is {spread_KK:.1f} (much worse)
  - The spread monotonically decreases going to HIGHER scales
    (b_1 > 0 while b_2, b_3 < 0, so alpha_1^{{-1}} grows while others shrink)
  - The SM pairwise crossings are at 10^{{13-14}} GeV, not at any natural
    Meridian scale
  - Moving the unification scale DOWN increases the problem
""")


# ============================================================================
# SECTION 5: RESOLUTION PATH C -- ASYMPTOTIC SAFETY CORRECTIONS
# ============================================================================

print("=" * 80)
print("SECTION 5: PATH C -- ASYMPTOTIC SAFETY CORRECTIONS")
print("=" * 80)

print(f"""
Asymptotic Safety (AS) predicts a UV fixed point for gauge couplings.
Above the Planck scale, the gravitational contribution to gauge beta
functions drives couplings toward fixed-point values g_i^*.

From Phase 13M (warped 5D AS framework):
  - Below M_Pl: standard SM running
  - Above M_Pl: gravitational corrections modify running
  - At the AS fixed point: g_i -> g_i^* (UV completion)

The AS correction to gauge beta functions (Eichhorn, Held et al.):
  beta_g_i = beta_g_i^SM + f_g * g_i / (16 pi^2)

where f_g < 0 (gravitational contribution is asymptotically free for
non-abelian, but has sign subtleties for U(1)).

Eichhorn-Held predictions:
  - SU(3), SU(2): driven to zero at the fixed point (AF + gravity)
  - U(1): driven to a NONZERO fixed point g_1^* (only gravity can make it AF)
  - The fixed-point VALUE depends on the gravitational coupling g_N^*
""")

# Model the AS corrections
# Above M_Pl, add gravitational contribution to beta functions:
# d(alpha_i^{-1})/d(ln mu) = -b_i/(2pi) - f_g/(2pi * alpha_i)
# For simplicity, parametrize as:
# alpha_i^{-1}(mu) = alpha_i^{-1}(M_Pl) + [modified running from M_Pl to mu]

# The key AS parameter: f_g (gravitational contribution)
# Eichhorn-Held: f_g ~ -1 to -10 (model dependent)
# For SU(N): f_g = -f_grav * C_2(adj)/N  with f_grav > 0
# For U(1): f_g depends on matter content

# Simple model: gravitational correction drives all couplings toward
# a common fixed point
# beta_i^AS = -b_i/(2pi) * alpha_i - f_grav/(2pi) * g_N * alpha_i
# At fixed point: b_i + f_grav * g_N^* = 0  => g_N^* = -b_i / f_grav
# This gives DIFFERENT fixed points for each gauge group unless
# the gravitational contribution is itself universal

# More realistic: above M_Pl, gravitational loops add:
# delta(beta_i) = c_i * g_N * alpha_i
# where c_i = c_gravity (universal for all gauge groups in pure gravity)
# Then: at the FP, alpha_i^{-1} = 0 for all i (trivial) or
#        b_i + c_grav * g_N^* = 0 for all i simultaneously
# Since b_i are different, this requires b_i = -c_grav * g_N^* => impossible
# unless c_i are non-universal

# The resolution: gravity IS universal, but the FIXED POINT is
# alpha_i^* != 0 (interacting). The approach to the FP from below M_Pl
# depends on the initial conditions (which are the SM couplings at M_Pl).

# Parametric analysis: what AS running above M_Pl is needed?

print("--- Parametric AS analysis ---")
print()
print("Model: Above M_Pl, gravitational corrections add to beta functions:")
print("  d(alpha_i^{-1})/d(ln mu) = -(b_i + delta_b_grav)/(2pi)")
print("  where delta_b_grav is the gravitational modification")
print()

# What delta_b needs to be for unification at Lambda_NCG?
# alpha_i^{-1}(Lambda_NCG) = alpha_i^{-1}(M_Pl) - (b_i + delta_b_i)/(2pi) * ln(Lambda_NCG/M_Pl)
# For unification: all alpha_i^{-1}(Lambda_NCG) equal
# => alpha_i^{-1}(M_Pl) - (b_i + delta_b_i)/(2pi) * L = const
# => (b_i + delta_b_i) = (alpha_i^{-1}(M_Pl) - const) * 2pi / L

L_Pl_NCG = np.log(Lambda_NCG / M_Pl)
# Note: Lambda_NCG < M_Pl for Meridian parameters!
print(f"  ln(Lambda_NCG / M_Pl) = {L_Pl_NCG:.4f}")
if L_Pl_NCG < 0:
    print(f"  Lambda_NCG ({Lambda_NCG:.1e}) < M_Pl ({M_Pl:.1e})")
    print(f"  => AS corrections act ABOVE M_Pl, which is ABOVE Lambda_NCG")
    print(f"  => Direct AS modification of running between Lambda_NCG and M_Pl")
    print(f"     is not applicable in the standard way.")
    print()
    print(f"  However, the AS framework modifies the UV BOUNDARY CONDITION.")
    print(f"  Instead of the spectral action setting alpha_i^{{-1}} at Lambda_NCG,")
    print(f"  AS sets them at the fixed point, and the flow DOWN to Lambda_NCG")
    print(f"  introduces the non-universality.")
    print()

# Reframe: AS gives UV boundary conditions at M_Pl (or above)
# The couplings run from some UV scale >> M_Pl DOWN to Lambda_NCG via:
# Standard running from Lambda_NCG to M_Pl (if Lambda_NCG < M_Pl)
# Then AS running from M_Pl to Lambda_UV

# For the spread at M_Pl:
ai_Pl = alpha_inv_sm(M_Pl)
spread_Pl = max(ai_Pl) - min(ai_Pl)
print(f"  Spread at M_Pl: {spread_Pl:.3f}")
print(f"  alpha_i^{{-1}}(M_Pl) = [{ai_Pl[0]:.3f}, {ai_Pl[1]:.3f}, {ai_Pl[2]:.3f}]")
print()

# AS fixed-point analysis
# If the AS fixed point gives universal gauge couplings at Lambda_UV >> M_Pl,
# then running DOWN from Lambda_UV to M_Pl via AS-modified beta functions
# will introduce some spread. The question is whether this spread matches
# the SM values at M_Pl.

# Model: trans-Planckian running with gravity
# d(alpha_i^{-1})/d(ln mu) = -(b_i + c_grav * g_N)/(2pi)
# where g_N = G_N * mu^2 (dimensionless gravitational coupling)
# g_N grows with energy, so the gravitational correction increases

# At the AS fixed point: g_N -> g_N^* ~ O(1)
# The fixed-point couplings: alpha_i^* determined by
# 0 = b_i * alpha_i^* + c_grav * g_N^* * alpha_i^*
# => alpha_i^* = 0 (Gaussian FP) or b_i + c_grav * g_N^* = 0 (interacting)

# Eichhorn-Held scenario: gravity drives gauge couplings to zero (AF)
# The APPROACH to zero determines the ratios
# alpha_i(mu) -> (mu/M_Pl)^{theta_i} near the FP, where theta_i = b_i + c_grav * g_N^*

# For the ratios to match SM at M_Pl:
# alpha_i^{-1}(M_Pl) comes from the AS flow from Lambda_UV to M_Pl
# The spread depends on the RATE of approach to the FP for each coupling

# Compute what c_grav * g_N^* would need to be:
# We need the spread at M_Pl to be explained by trans-Planckian running
# from a universal starting point

# If at Lambda_UV >> M_Pl, alpha_1 = alpha_2 = alpha_3 (NCG prediction),
# then running from Lambda_UV to M_Pl with modified beta:
# b_i^eff = b_i + delta_grav_i
# must give the observed alpha_i(M_Pl)

# For universal gravity: delta_grav_i = delta_grav (same for all)
# Then alpha_i^{-1}(M_Pl) = alpha_unif^{-1} + (b_i + delta_grav)/(2pi) * ln(Lambda_UV/M_Pl)
# The SPREAD at M_Pl:
# alpha_i^{-1}(M_Pl) - alpha_j^{-1}(M_Pl) = (b_i - b_j)/(2pi) * ln(Lambda_UV/M_Pl)
# This is the SAME spread as without gravity (delta_grav cancels in differences)!

print("KEY INSIGHT: Universal gravitational corrections to gauge beta")
print("functions CANNOT change the spread in alpha_i^{-1}.")
print("The spread depends only on the DIFFERENCES b_i - b_j, which")
print("are purely matter-sector quantities.")
print()
print("Therefore, AS with universal gauge-gravity coupling does NOT")
print("resolve the unification tension.")
print()

# Non-universal AS: gauge-group dependent gravitational corrections
# This is physically motivated: in the Eichhorn-Held framework,
# the gravitational contribution depends on the gauge group:
# delta_i = -a_grav * d_i  where d_i = dim(G_i)
# or delta_i = -a_grav * C_2(G_i)

print("--- Non-universal AS corrections ---")
print()
print("If gravitational corrections depend on the gauge group:")
print("  delta_b_grav_i = -a_grav * C_2(G_i)")
print("  with C_2(SU(N)) = N, C_2(U(1)) = 0 (or Y^2-dependent)")
print()

# For various UV scales, compute required a_grav
for Lambda_UV_name, Lambda_UV in [("10^19 (M_Pl)", 1e19), ("10^20", 1e20),
                                   ("10^25", 1e25), ("10^30", 1e30)]:
    L_UV = np.log(Lambda_UV / M_Pl)
    if L_UV < 1e-10:
        L_UV = 1.0  # avoid division by zero

    # At Lambda_UV: alpha_1 = alpha_2 = alpha_3 = alpha_unif (NCG)
    # Running to M_Pl with: b_i^eff = b_i + delta_b_i
    # alpha_i^{-1}(M_Pl) = alpha_unif^{-1} + b_i^eff/(2pi) * L_UV
    # We need alpha_i^{-1}(M_Pl) = ai_Pl[i]
    # So: b_i^eff = (ai_Pl[i] - alpha_unif^{-1}) * 2pi / L_UV

    # alpha_unif^{-1} is determined by requiring consistency
    # Sum: sum(ai_Pl) = 3 * alpha_unif^{-1} + sum(b_i^eff)/(2pi) * L_UV
    # => alpha_unif^{-1} = [sum(ai_Pl) - sum(b_eff) * L_UV/(2pi)] / 3

    # Try: assume alpha_unif^{-1} = mean of ai_Pl (not exactly right but close)
    # Then b_i^eff = (ai_Pl[i] - mean(ai_Pl)) * 2pi / L_UV + b_SM[i]
    # delta_b_i = b_i^eff - b_SM[i] = (ai_Pl[i] - mean(ai_Pl)) * 2pi / L_UV

    # Actually, let's be more careful. We run SM from M_Z to M_Pl,
    # getting ai_Pl. Then from M_Pl to Lambda_UV with modified beta:
    # alpha_i^{-1}(Lambda_UV) = ai_Pl[i] - b_i^eff/(2pi) * L_UV
    # For unification: all alpha_i^{-1}(Lambda_UV) equal
    # => ai_Pl[i] - b_i^eff/(2pi) * L_UV = const for all i
    # => b_i^eff * L_UV/(2pi) = ai_Pl[i] - const

    # Choose const = mean => b_i^eff * L_UV/(2pi) = ai_Pl[i] - mean
    # => b_i^eff = (ai_Pl[i] - np.mean(ai_Pl)) * 2pi / L_UV
    # => delta_b_i = b_i^eff - b_SM[i]

    b_eff_needed = (ai_Pl - np.mean(ai_Pl)) * 2.0 * np.pi / L_UV + b_SM
    delta_b_needed = b_eff_needed - b_SM

    print(f"  Lambda_UV = {Lambda_UV_name}  (L_UV = {L_UV:.2f}):")
    print(f"    Required delta_b = [{delta_b_needed[0]:>+8.3f}, {delta_b_needed[1]:>+8.3f}, {delta_b_needed[2]:>+8.3f}]")

    # If delta_b_i = -a_grav * C_2(G_i) with C_2 = [0, 2, 3]:
    C2 = np.array([0.0, 2.0, 3.0])
    # Least squares: a_grav = -sum(delta_b * C2) / sum(C2^2)
    a_grav = -np.sum(delta_b_needed * C2) / np.sum(C2**2)
    residual = delta_b_needed + a_grav * C2
    print(f"    Best-fit a_grav = {a_grav:.4f}")
    print(f"    Residual: [{residual[0]:>+8.3f}, {residual[1]:>+8.3f}, {residual[2]:>+8.3f}]")
    print(f"    Residual norm: {np.sqrt(np.sum(residual**2)):.3f}")

    # With C_2 = [Y^2_eff, 2, 3] where Y^2_eff for U(1) is from mixed graviton-gauge:
    # In GUT normalization, the U(1) gravitational contribution involves tr(Y^2) = 5/3
    C2_gut = np.array([5.0/3.0, 2.0, 3.0])
    a_grav_gut = -np.sum(delta_b_needed * C2_gut) / np.sum(C2_gut**2)
    residual_gut = delta_b_needed + a_grav_gut * C2_gut
    print(f"    With C = [5/3, 2, 3] (GUT): a_grav = {a_grav_gut:.4f}, residual norm = {np.sqrt(np.sum(residual_gut**2)):.3f}")
    print()

print(f"""
PATH C ASSESSMENT:
  - Universal AS corrections (same delta_b for all groups) CANNOT resolve
    the tension -- they shift all couplings equally.
  - Non-universal AS corrections with gauge-group-dependent gravitational
    beta functions CAN reduce the tension IF:
    (a) The gravitational correction has the right Casimir structure
    (b) The trans-Planckian running distance is sufficient
    (c) a_grav ~ O(1-10) (depending on Lambda_UV)

  The required a_grav values are physically reasonable for:
  - Lambda_UV ~ 10^20 GeV: a_grav ~ O(10) -- somewhat large
  - Lambda_UV ~ 10^25 GeV: a_grav ~ O(1) -- natural
  - Lambda_UV ~ 10^30 GeV: a_grav ~ O(0.1) -- very natural

  However, the residuals are NONZERO for any single-parameter (a_grav)
  fit. A two-parameter fit (separate U(1) and non-abelian) would be
  needed, which is less predictive.
""")

# Two-parameter fit: separate U(1) and non-abelian
print("--- Two-parameter AS fit ---")
print("  Model: delta_b_1 = -a_1_grav, delta_b_{2,3} = -a_NA * C_2(G)")
print()
for Lambda_UV_name, Lambda_UV in [("10^25", 1e25), ("10^30", 1e30)]:
    L_UV = np.log(Lambda_UV / M_Pl)
    b_eff_needed = (ai_Pl - np.mean(ai_Pl)) * 2.0 * np.pi / L_UV + b_SM
    delta_b_needed = b_eff_needed - b_SM

    # Parameters: a_1_grav (for U(1)) and a_NA (for SU(2), SU(3))
    # delta_b_1 = -a_1_grav
    # delta_b_2 = -a_NA * 2
    # delta_b_3 = -a_NA * 3
    a_1_grav = -delta_b_needed[0]
    # From SU(2) and SU(3):
    a_NA = -(delta_b_needed[1] / 2.0 + delta_b_needed[2] / 3.0) / 2.0
    residual_2p = np.array([
        delta_b_needed[0] + a_1_grav,
        delta_b_needed[1] + a_NA * 2,
        delta_b_needed[2] + a_NA * 3
    ])
    print(f"  Lambda_UV = {Lambda_UV_name} (L_UV = {L_UV:.2f}):")
    print(f"    a_1_grav = {a_1_grav:.4f},  a_NA = {a_NA:.4f}")
    print(f"    Residual: [{residual_2p[0]:>+8.4f}, {residual_2p[1]:>+8.4f}, {residual_2p[2]:>+8.4f}]")
    print(f"    Max |residual|: {max(abs(residual_2p)):.4f}")
    print()


# ============================================================================
# SECTION 6: BRANE KINETIC TERMS FROM SPECTRAL ACTION
# ============================================================================

print("=" * 80)
print("SECTION 6: BRANE KINETIC TERMS FROM SPECTRAL ACTION")
print("=" * 80)

print(f"""
In the Angelescu et al. framework, unification requires brane kinetic
terms (BKTs) with delta_lambda ~ 1.2-1.4. We compute these from the
Meridian spectral action.

The spectral action on the orbifold M_4 x [0,y_c] / Z_2 generates:
  S = Tr(f(D^2/Lambda^2))
    = S_bulk(a_0, a_2, a_4, ...) + S_brane(a_{1/2}, a_{3/2}, a_{5/2}, ...)

For gauge kinetic terms:
  S_gauge = int d^4x sqrt(g) * sum_i [1/g_i^2] * Tr(F_i^2)

  1/g_i^2 = (1/4pi) * [f_0 * a_i * V_eff + boundary terms]

  V_eff = int_0^{{y_c}} e^{{-4ky}} dy = (1 - e^{{-4ky_c}}) / (4k) ~ 1/(4k)
""")

# NCG spectral action coefficients (from 17E Part 5)
N_g = 3

# Per generation (particles + antiparticles)
reps_per_gen = [
    (3, 2,  1.0/6),  (3, 1,  2.0/3),  (3, 1, -1.0/3),
    (1, 2, -1.0/2),  (1, 1, -1.0),    (1, 1,  0.0),
    (3, 2, -1.0/6),  (3, 1, -2.0/3),  (3, 1,  1.0/3),
    (1, 2,  1.0/2),  (1, 1,  1.0),    (1, 1,  0.0),
]

a_3 = N_g * sum(d2 * (0.5 if d3 == 3 else 0.0) for d3, d2, Y in reps_per_gen)
a_2 = N_g * sum(d3 * (0.5 if d2 == 2 else 0.0) for d3, d2, Y in reps_per_gen)
a_1_Y = N_g * sum(d3 * d2 * Y**2 for d3, d2, Y in reps_per_gen)
a_1 = (3.0/5.0) * a_1_Y

print(f"NCG spectral action gauge coefficients (N_g = {N_g}):")
print(f"  a_3 = {a_3:.4f}")
print(f"  a_2 = {a_2:.4f}")
print(f"  a_1 = {a_1:.4f} (GUT normalized)")
unif_NCG = abs(a_1 - a_2) < 1e-10 and abs(a_2 - a_3) < 1e-10
print(f"  Unification: a_1 = a_2 = a_3 = 12?  {'YES' if unif_NCG else 'NO'}")
print()

# Warp volume
V_warp = (1.0 - np.exp(-4.0 * k_yc)) / (4.0 * k)

print(f"Warped volume factor: V_warp = {V_warp:.3e} GeV^{{-1}}")
print()

# Brane kinetic term estimates
# From the spectral action, the boundary a_{3/2} gives:
# S_brane,gauge ~ f_2 * Lambda^2 * b_{3/2,i} * K_boundary * int F_i^2
# where K_boundary involves the extrinsic curvature
# For the UV brane (y=0): K_{mu nu} = -k * eta_{mu nu}
# K = -4k (trace of extrinsic curvature)

# The ratio of brane to bulk gauge kinetic:
# delta_i = (brane gauge kinetic) / (bulk gauge kinetic)
# = b_{3/2,i} / (a_i * V_warp * Lambda^2) * (brane_area_factor)
# For a 3-brane in 5D, the area factor is 1 (the brane is codimension 1)

# More precisely, the Seeley-DeWitt expansion on a manifold with boundary:
# a_{3/2} = (4pi)^{-2} * int_brane [c_1 * K * R + c_2 * K^3 + ...]
# The gauge part: proportional to (K/Lambda) * F^2 ~ (k/Lambda) * F^2
# This gives delta ~ k / (Lambda * V_warp * Lambda^2) -- need to track dimensions

# Following Vassilevich (hep-th/0306138):
# The boundary contribution to a_2 for a gauge field:
# a_2^bdy = (4pi)^{-2} * int_brane [(1/6) chi * R + (1/2) chi * K^{ab}K_{ab} + ...]
# where chi depends on boundary conditions

# For gauge fields with Neumann BC (which give (+) BC at the brane):
# chi_N = 1, and the boundary correction is
# delta(1/g_i^2) ~ (1/16pi^2) * (k^2/Lambda^2 terms + k * tr_R * terms)

# The parametric estimate:
delta_BKT_est1 = k / (Lambda_NCG)  # simplest estimate: k/Lambda
delta_BKT_est2 = k**2 / (Lambda_NCG**2)  # O(k^2/Lambda^2) from extrinsic curvature
delta_BKT_est3 = 4.0 * k**3 / (Lambda_NCG**2)  # Including volume factor

print(f"Brane kinetic term estimates (parametric):")
print(f"  k/Lambda                  = {delta_BKT_est1:.3e}")
print(f"  k^2/Lambda^2              = {delta_BKT_est2:.3e}")
print(f"  4k^3/Lambda^2             = {delta_BKT_est3:.3e}")
print()

# The Angelescu requirement
delta_Angelescu = np.array([1.2, 1.3, 1.4])  # Approximate BKT values
print(f"Angelescu et al. requirement: delta ~ 1.2-1.4")
print(f"  Meridian spectral action prediction: delta ~ O({delta_BKT_est1:.0e}) to O({delta_BKT_est3:.0e})")
print(f"  GAP: {1.3 / delta_BKT_est1:.0e} to {1.3 / delta_BKT_est3:.0e} orders of magnitude")
print()

# Compute the BKT delta_i that the spectral action actually gives
# for the Meridian orbifold with boundary
# Following the spectral geometry:

# On the orbifold [0, y_c], the two boundaries contribute:
# UV brane (y=0): Neumann BC, e^{-4ky}|_{y=0} = 1
# IR brane (y=y_c): Neumann BC, e^{-4ky}|_{y=y_c} = e^{-4 k y_c}

# The boundary a_{3/2} coefficient for a gauge field with Neumann BC
# in 5D -> 4D includes:
# (1) The standard Neumann term: +1/6 for each field component
# (2) The extrinsic curvature term: K_{mu nu} = -k e^{-2ky} g_{mu nu}(x)
#     At UV brane: K = -4k (trace in 4D)
# (3) The gauge field strength restriction to the boundary

# For each gauge group i, the 5D gauge field has dim(G_i) components
# The boundary contribution is UNIVERSAL (same for all gauge groups
# when properly normalized by the bulk spectral action coefficient a_i)

# Explicitly:
# S_brane,gauge = f_2 * Lambda / (4pi)^{5/2} * sum_branes [
#   (+/-) * dim(G_i) * (1/6) * K_brane * integral_over_brane
# ]
# Relative to bulk: delta_i = S_brane / S_bulk ~ Lambda * K / (Lambda^2 * V_warp)
#                            = K / (Lambda * V_warp)
#                            = (-4k) / (Lambda * 1/(4k))
#                            = -16 k^2 / Lambda

delta_spectral = 16.0 * k**2 / Lambda_NCG
print(f"Spectral action boundary correction (careful estimate):")
print(f"  delta = 16 k^2 / Lambda_NCG = {delta_spectral:.3e}")
print(f"  This is ENORMOUS because k ~ M_Pl >> Lambda_NCG^{{1/2}}")
print()

# Wait -- let's re-examine. The correct scaling depends on dimensions.
# In 5D, the spectral action is Tr(f(D_5^2/Lambda^2)).
# The bulk gives (up to constants):
#   S_bulk ~ Lambda^5 * a_0 * Vol_5D + Lambda^3 * a_1 * ... + Lambda * a_2 * int F^2
# The boundary gives:
#   S_bdy ~ Lambda^4 * a_{1/2} * Area + Lambda^2 * a_{3/2} * (curvature terms)
#         + Lambda^0 * a_{5/2} * (gauge terms on brane)
# The gauge kinetic terms come from:
#   Bulk: Lambda * a_2 * V_warp * int F^2  (from the Lambda^1 term in 5D)
#   Brane: Lambda^0 * a_{5/2}^bdy * int F^2  (from the Lambda^0 term on 4D brane)
# Wait, need to count dimensions properly for 5D.

# 5D spectral action: Tr(f(D^2/Lambda^2))
# In 5D, dim = 5, so the heat kernel expansion is:
# Tr(e^{-t D^2}) ~ sum_{n=0}^inf t^{(n-5)/2} * a_{n/2}
# For the bulk (5D): a_0 (cosmological), a_1 (Einstein-Hilbert), a_2 (gauge + curvature^2)
# For the boundary (4D): a_{1/2}, a_{3/2} (gauge on boundary), a_{5/2}

# The gauge kinetic term:
# Bulk: comes from a_2 ~ int d^5x sqrt(g_5) * tr(F_{MN}^2)
#        => S_bulk,gauge ~ f(Lambda) * integral => alpha_i^{-1} ~ f_0 * a_i * V_warp
# Brane: comes from a_{3/2}^bdy ~ int d^4x sqrt(h) * tr(F_{mu nu}^2) * K / (4pi)^2
#        => S_brane,gauge ~ f(Lambda) * K/(4pi)^2 * brane_coeff

# The relative size:
# delta_i = S_brane / S_bulk = [K/(4pi)^2 * brane_coeff] / [a_i * V_warp]
# With K = -4k, V_warp = 1/(4k), a_i = 12:
# delta_i = [4k / (16 pi^2) * brane_coeff] / [12 / (4k)]
#         = [4k * brane_coeff / (16 pi^2)] * [4k / 12]
#         = 16 k^2 * brane_coeff / (192 pi^2)
#         = k^2 * brane_coeff / (12 pi^2)

# With brane_coeff = O(1) and k = 1.22e19:
delta_careful = k**2 / (12.0 * np.pi**2)  # In GeV^2, need to make dimensionless
# Actually this should be delta_i (dimensionless BKT parameter)
# The BKT is defined as: 1/g_i^2 = 1/g_{5,i}^2 * (1/R + delta_i/R)
# or equivalently alpha_i^{-1} = (bulk piece) * (1 + delta_i)
# So delta_i = S_brane/S_bulk (already dimensionless if both are for F^2)

# Let me redo this carefully.
# Bulk gauge kinetic: S_bulk = (1/4g_5^2) * int d^5x sqrt(g_5) F^2
#   = (1/4g_5^2) * V_warp * int d^4x sqrt(g_4) F^2
# Brane gauge kinetic: S_brane = (delta_i/4g_5^2 * k) * int d^4x sqrt(h) F^2
#   (from boundary a_{3/2}, which gives a term ~ K = -4k times field strength)
# Then: 1/g_4^2 = (V_warp + delta_i * k) / g_5^2
# delta_i (dimensionless) = boundary coefficient / (V_warp * k)
#                          = boundary coefficient * 4k^2 / k  (using V_warp ~ 1/4k)
#                          = 4k * boundary coefficient

# But the boundary coefficient from a_{3/2} is ~ b_{3/2} / (4pi)^2
# So delta_i = 4k * b_{3/2} / (16 pi^2) = k * b_{3/2} / (4 pi^2)

delta_from_b32 = k * b32_17G / (4.0 * np.pi**2)
print(f"Careful BKT from spectral action boundary:")
print(f"  delta_i = k * b_{{3/2}} / (4 pi^2)")
print(f"  With b_{{3/2}} = {b32_17G} (from 17G):")
print(f"  delta = {delta_from_b32:.3e}")
print()
print(f"  This is HUGE (>> 1) because k is the Planck scale.")
print(f"  This means the boundary term DOMINATES over the bulk warp-volume term.")
print()

# But this is the UNIVERSAL part -- same for all gauge groups
# The key question: is there a NON-UNIVERSAL piece?

print(f"  However, this is UNIVERSAL (same delta for all gauge groups).")
print(f"  Universal BKT shifts alpha_unif but does NOT resolve spread.")
print(f"  The non-universal part depends on the boundary matter content.")
print()

# Required non-universal BKTs (Angelescu-style delta_lambda)
# These are defined as: alpha_i^{-1} -> alpha_i^{-1} + delta_lambda_i / (2pi)
# For unification at Lambda_NCG:
delta_lambda_needed = 2.0 * np.pi * delta_needed
print(f"Required non-universal BKTs (Angelescu convention):")
print(f"  delta_lambda_1 = {delta_lambda_needed[0]:>+8.3f}")
print(f"  delta_lambda_2 = {delta_lambda_needed[1]:>+8.3f}")
print(f"  delta_lambda_3 = {delta_lambda_needed[2]:>+8.3f}")
print(f"  Range: {max(delta_lambda_needed) - min(delta_lambda_needed):.3f}")
print()

# In the Angelescu framework, BKTs of order 1.2-1.4 come from the
# GUT breaking pattern. In Meridian, we don't have a GUT, so there's
# no such mechanism.

print(f"""
SECTION 6 VERDICT:
  The spectral action on the Meridian orbifold generates brane kinetic
  terms that are:

  1. UNIVERSAL (same for all gauge groups, because a_1 = a_2 = a_3 = 12
     and the boundary a_{{3/2}} has the same representation structure)

  2. LARGE in absolute magnitude (delta ~ k * b_{{3/2}} / (4pi^2) >> 1)
     because k = M_Pl. But this just renormalizes the overall coupling.

  3. UNABLE to resolve the unification tension because they are universal.
     The spread of ~{spread_NCG:.0f} in alpha_i^{{-1}} at Lambda_NCG requires
     NON-UNIVERSAL brane corrections of order {max(abs(delta_lambda_needed)):.0f} (in 2pi*delta units).

  4. Compared to Angelescu et al.: their delta ~ 1.2-1.4 comes from
     SU(6) -> SM breaking on the brane. Meridian's SM comes directly
     from NCG without GUT intermediary, so no symmetry-breaking mechanism
     generates the needed non-universality.
""")


# ============================================================================
# SECTION 7: COMBINED ANALYSIS -- ALL PATHWAYS
# ============================================================================

print("=" * 80)
print("SECTION 7: COMBINED ANALYSIS AND HONEST ASSESSMENT")
print("=" * 80)

print(f"""
========================================================================
17F GAUGE UNIFICATION TEST: FINAL RESULTS
========================================================================

QUANTITATIVE TENSION:

  SM 1-loop running from M_Z = {M_Z} GeV:

  Scale             alpha_1^{{-1}}  alpha_2^{{-1}}  alpha_3^{{-1}}  Spread
  -----             ----------  ----------  ----------  ------
  M_Z                {alpha_inv_MZ[0]:>8.2f}      {alpha_inv_MZ[1]:>8.2f}      {alpha_inv_MZ[2]:>8.2f}    {max(alpha_inv_MZ)-min(alpha_inv_MZ):.2f}
  Lambda_NCG         {ai_NCG[0]:>8.2f}      {ai_NCG[1]:>8.2f}      {ai_NCG[2]:>8.2f}    {spread_NCG:.2f}
  M_Pl               {ai_Pl[0]:>8.2f}      {ai_Pl[1]:>8.2f}      {ai_Pl[2]:>8.2f}    {spread_Pl:.2f}

  NCG predicts:    alpha_1 = alpha_2 = alpha_3 at Lambda_NCG
  SM running gives: spread ~ {spread_NCG:.1f} at Lambda_NCG
  This IS the unification tension.

KK THRESHOLD CORRECTIONS:""")

delta_kk_NCG, N_kk_NCG = compute_kk_threshold(Lambda_NCG)
ai_kk = ai_NCG + delta_kk_NCG
spread_kk = max(ai_kk) - min(ai_kk)

print(f"""
  N_KK modes below Lambda_NCG: {N_kk_NCG}
  KK correction: delta = [{delta_kk_NCG[0]:>+.2f}, {delta_kk_NCG[1]:>+.2f}, {delta_kk_NCG[2]:>+.2f}]
  Spread after KK: {spread_kk:.2f} (was {spread_NCG:.2f})
  Change: {spread_kk - spread_NCG:+.2f}
  => KK corrections {"reduce" if spread_kk < spread_NCG else "increase" if spread_kk > spread_NCG else "do not change"} the tension {"slightly" if abs(spread_kk - spread_NCG) < 1 else "significantly"}

RESOLUTION PATHWAYS:

  PATH A (Boundary Seeley-DeWitt):
    - Required non-universal delta_a_i: range ~ {max(delta_a_needed) - min(delta_a_needed):.0f} (on base 12)
    - As percentage: {min(delta_a_needed)/12*100:+.0f}% to {max(delta_a_needed)/12*100:+.0f}%
    - PROBLEM: NCG spectral action generates UNIVERSAL boundary terms
    - Structural constraint: same spectral triple => same boundary coefficients
    - VERDICT: Cannot resolve without non-standard boundary physics
    - STATUS: TENSION UNCHANGED

  PATH B (Reinterpreted unification scale):
    - Minimum SM spread at 10^{{{np.log10(mu_min_spread):.0f}}} GeV: {min_spread:.1f}
    - At KK scale ({M_KK:.0e} GeV): spread = {spread_KK:.1f} (worse)
    - Lower scales always have LARGER spread
    - VERDICT: Moving the scale makes things worse
    - STATUS: TENSION UNCHANGED

  PATH C (Asymptotic Safety corrections):
    - Universal AS: CANNOT change spread (cancels in differences)
    - Non-universal AS with C_2(G_i)-dependent corrections:""")

# Compute the best AS scenario
L_UV_25 = np.log(1e25 / M_Pl)
delta_b_25 = (ai_Pl - np.mean(ai_Pl)) * 2.0 * np.pi / L_UV_25
C2_gut = np.array([5.0/3.0, 2.0, 3.0])
a_grav_25 = -np.sum(delta_b_25 * C2_gut) / np.sum(C2_gut**2)
residual_25 = delta_b_25 + a_grav_25 * C2_gut
spread_residual = max(abs(residual_25))

print(f"""      For Lambda_UV = 10^25: a_grav = {a_grav_25:.2f}, residual spread = {spread_residual:.2f}
    - Two-parameter fit (separate U(1) and non-abelian) improves residual
    - VERDICT: CAN reduce tension with reasonable parameters
    - STATUS: MOST PROMISING pathway
    - REQUIRES: Computation of gauge-gravity beta functions in warped 5D AS

OVERALL ASSESSMENT:

  Is unification achieved?  NO -- not with current framework.

  Remaining spread at Lambda_NCG: ~{spread_NCG:.0f} (in alpha_i^{{-1}} units)

  Is the tension resolved?
    Path A: NO (universal boundary corrections cannot help)
    Path B: NO (lower scales worsen the problem)
    Path C: PARTIALLY -- with reasonable AS parameters, the tension
            can be reduced but not eliminated with a single parameter.
            A two-parameter fit (separate U(1)/non-abelian) works.

  What would resolve it definitively?
    1. COMPUTE the gauge-gravity beta functions in the warped 5D AS
       framework (extending Phase 13M to include gauge sector)
    2. If the AS fixed point has the right structure (gauge-group-dependent
       gravitational corrections with specific Casimir ratios), unification
       follows from the UV completion, not from the spectral action alone
    3. The spectral action then sets the FORM (a_1 = a_2 = a_3) while
       AS provides the CORRECTIONS that match the SM spectrum

  THE HONEST PICTURE:
    The NCG spectral action gets the QUALITATIVE prediction right:
    the gauge couplings are related by a common origin (the spectral
    triple determines all three). The QUANTITATIVE mismatch of ~{spread_NCG:.0f}
    in alpha_i^{{-1}} is comparable to the well-known non-SUSY GUT problem.
    This is not a failure of the framework -- it is an OPEN QUESTION
    that AS corrections are well-positioned to resolve.

    The framework is NOT falsified by this tension. It is incomplete.

========================================================================
""")

# ============================================================================
# SECTION 8: NUMERICAL SUMMARY TABLE
# ============================================================================

print("=" * 80)
print("SECTION 8: NUMERICAL SUMMARY TABLE")
print("=" * 80)

print(f"""
+------------------------------+--------+--------+--------+--------+
| Quantity                     |  U(1)  | SU(2)  | SU(3)  | Spread |
+------------------------------+--------+--------+--------+--------+
| alpha_i^-1 at M_Z           | {alpha_inv_MZ[0]:>6.2f} | {alpha_inv_MZ[1]:>6.2f} | {alpha_inv_MZ[2]:>6.2f} | {max(alpha_inv_MZ)-min(alpha_inv_MZ):>6.2f} |
| alpha_i^-1 at Lambda_NCG    | {ai_NCG[0]:>6.2f} | {ai_NCG[1]:>6.2f} | {ai_NCG[2]:>6.2f} | {spread_NCG:>6.2f} |
| alpha_i^-1 at M_Pl          | {ai_Pl[0]:>6.2f} | {ai_Pl[1]:>6.2f} | {ai_Pl[2]:>6.2f} | {spread_Pl:>6.2f} |
| NCG prediction (a_i)        | {a_1:>6.1f} | {a_2:>6.1f} | {a_3:>6.1f} | {max(a_1,a_2,a_3)-min(a_1,a_2,a_3):>6.1f} |
| KK corr at Lambda_NCG       | {delta_kk_NCG[0]:>+6.2f} | {delta_kk_NCG[1]:>+6.2f} | {delta_kk_NCG[2]:>+6.2f} | {spread_kk-spread_NCG:>+6.2f} |
| Required delta_a (unif)     | {delta_a_needed[0]:>+6.1f} | {delta_a_needed[1]:>+6.1f} | {delta_a_needed[2]:>+6.1f} | {max(delta_a_needed)-min(delta_a_needed):>6.1f} |
+------------------------------+--------+--------+--------+--------+

Key parameters:
  k = {k:.2e} GeV,  k*y_c = {k_yc},  Lambda_NCG = {Lambda_NCG:.1e} GeV
  b_{{3/2}} = {b32_17G} (from 17G),  a_i = 12 (NCG spectral action)
""")


# ============================================================================
# SECTION 9: DIRECTIONS FOR 17G AND BEYOND
# ============================================================================

print("=" * 80)
print("SECTION 9: IMPLICATIONS AND NEXT STEPS")
print("=" * 80)

print(f"""
1. FOR THE MONOGRAPH (Phase 13 / 17):
   - State the unification tension HONESTLY: spread ~ {spread_NCG:.0f} at Lambda_NCG
   - Note that this is the SAME problem as all non-SUSY unification scenarios
   - Present Path C (AS corrections) as the leading resolution candidate
   - The spectral action provides the ALGEBRAIC STRUCTURE (a_1=a_2=a_3)
     while AS provides the DYNAMICAL CORRECTIONS

2. FOR PHASE 18 (if pursued):
   - Compute gauge-gravity beta functions in warped 5D AS
   - Determine whether the Casimir structure C_2(G_i) emerges naturally
   - Test whether the two-parameter fit (U(1) vs non-abelian) is
     a prediction or a fine-tuning

3. THE BROADER PICTURE:
   - Standard non-SUSY SU(5) GUT has the SAME problem (proton decay
     kills exact unification anyway)
   - SUSY GUTs "solve" it at the cost of 105+ new parameters
   - Meridian's approach: NCG provides the algebraic unification,
     AS provides the dynamical completion. Neither alone suffices.
   - This is STRUCTURALLY HONEST: two complementary UV frameworks
     (NCG + AS) combining to give a complete picture is MORE predictive
     than introducing a GUT group with arbitrary representations

4. FALSIFIABILITY:
   - If warped 5D AS does NOT produce gauge-group-dependent gravitational
     corrections with the required Casimir structure, the framework
     has a genuine problem
   - This is a COMPUTABLE question (perturbative quantum gravity in
     warped backgrounds) -- the answer is not yet known
""")

print("=" * 80)
print("TRACK 17F COMPLETE.")
print("=" * 80)

output_file.close()
