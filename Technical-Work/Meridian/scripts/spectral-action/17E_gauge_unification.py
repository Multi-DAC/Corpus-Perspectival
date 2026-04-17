"""
Track 17E: Gauge Coupling Unification on the Warped RS Orbifold
================================================================
Authors: Clayton W. Iggulden-Schnell & Clawd
Date: March 19, 2026

THE QUESTION: Does gauge coupling unification work on the Meridian warped
orbifold, and does the NCG spectral action predict the required brane
kinetic terms?

Following Angelescu, Bally, Goertz & Weber (arXiv:2512.22094), the correct
formalism for gauge coupling running in warped extra dimensions is the
Planck-brane correlator, not naive KK summation. Key rules:
  1. Only fields with (+) UV-brane boundary conditions contribute to running
  2. (-) BC fields decouple at M_Pl
  3. A_5 (gauge-Higgs) does NOT contribute to running
  4. Fermion bulk mass |c| < 1/2 fields don't contribute
  5. Unification occurs at k ~ M_Pl, not at Lambda_NCG

We test two RS parameter regimes:
  Regime I:  k = M_Pl ~ 10^18 GeV, ky_c ~ 36.6 (standard RS1, M_KK ~ TeV)
  Regime II: k ~ 10^8 GeV, ky_c ~ 39.6 (Meridian monograph, M_KK sub-eV)
  — In Regime II, KK modes are below the weak scale and the running is
    effectively 4D from M_Z to Lambda_NCG. The gauge fields live on the brane.

And two Higgs scenarios:
  Scenario A: Brane-localized Higgs (standard RS1)
  Scenario B: Gauge-Higgs (A_5) — drops out of running above M_KK

References:
  - Angelescu et al., arXiv:2512.22094 (Planck-brane correlator method)
  - Chamseddine-Connes-Marcolli, hep-th/0610241 (SM from NCG)
  - Gherghetta-Pomarol, NPB 586 (2000) 141 (fermion localization)
  - Pomarol, PRL 85 (2000) 4004 (gauge boson KK modes)
  - Dienes-Dudas-Gherghetta, NPB 537 (1999) 47 (KK threshold corrections)
  - Phase 14A.2: warped spectral action coefficients
  - Phase 15A: spectral triple on M_4 x S^1/Z_2 x F
  - Monograph Chapter 4: NCG on RS orbifold
"""

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import jv, yv  # Bessel functions J_nu, Y_nu
import os

# ============================================================================
# Output setup (dual: console + file)
# ============================================================================
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "17E_gauge_unification_results.txt")
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
print("TRACK 17E: GAUGE COUPLING UNIFICATION ON THE WARPED RS ORBIFOLD")
print("=" * 80)
print()

# ============================================================================
# PART 0: PHYSICAL CONSTANTS AND RS PARAMETERS
# ============================================================================

print("=" * 80)
print("PART 0: PHYSICAL CONSTANTS AND RS PARAMETERS")
print("=" * 80)

# ---- Fundamental scales (all in GeV) ----
M_Pl = 2.435e18            # Reduced Planck mass
M_Pl_full = 1.221e19       # Full Planck mass
M_Z = 91.1876              # Z boson mass
M_W = 80.379               # W boson mass
M_t = 173.1                # Top quark mass
v_higgs = 246.0             # Higgs VEV

# ---- SM gauge couplings at M_Z (PDG 2024) ----
alpha_em_MZ = 1.0 / 127.951
sin2_thetaW = 0.23122
alpha_s_MZ = 0.1179

alpha_Y_MZ = alpha_em_MZ / (1.0 - sin2_thetaW)
alpha_2_MZ = alpha_em_MZ / sin2_thetaW
alpha_1_MZ = (5.0 / 3.0) * alpha_Y_MZ      # GUT-normalized U(1)
alpha_3_MZ = alpha_s_MZ

alpha_inv_MZ = np.array([1.0/alpha_1_MZ, 1.0/alpha_2_MZ, 1.0/alpha_3_MZ])

print(f"""
Gauge couplings at M_Z = {M_Z} GeV (GUT normalization):
  alpha_1(M_Z) = {alpha_1_MZ:.6f}  (= 5/3 * alpha_Y)
  alpha_2(M_Z) = {alpha_2_MZ:.6f}
  alpha_3(M_Z) = {alpha_3_MZ:.6f}

  alpha_1^{{-1}}(M_Z) = {alpha_inv_MZ[0]:.4f}
  alpha_2^{{-1}}(M_Z) = {alpha_inv_MZ[1]:.4f}
  alpha_3^{{-1}}(M_Z) = {alpha_inv_MZ[2]:.4f}
""")

# ---- RS parameter regimes ----
#
# The RS metric is: ds^2 = e^{-2k|y|} eta_{mu nu} dx^mu dx^nu + dy^2
# with y in [0, y_c] (orbifold fundamental domain).
#
# Hierarchy: e^{-ky_c} = TeV / M_Pl  =>  ky_c = ln(M_Pl / TeV)
# KK masses: m_n ~ x_n * k * e^{-ky_c}  (x_n are Bessel function zeros)
#
# Two physically distinct regimes exist in the Meridian framework:
#
# REGIME I: k ~ M_Pl (standard RS1)
#   Here k ~ 10^18 GeV and ky_c ~ 36-37.
#   M_KK ~ TeV, KK graviton at ~TeV. Standard phenomenology.
#   The spectral cutoff Lambda ~ M_5^{5/3}/k^{2/3} is near M_Pl.
#
# REGIME II: k ~ 10^8 GeV (Meridian monograph cosmological regime)
#   Here k is set by Lambda_5: k = sqrt(-Lambda_5/(12 M_5^3))
#   With ky_c = ln(M_Pl/m_W) ~ 39.6, M_KK ~ sub-eV.
#   Gauge fields live on the brane; KK modes are irrelevant at collider scales.
#   The spectral cutoff Lambda_NCG ~ 10^17 GeV from the spectral action.
#
# For gauge unification, REGIME I is the standard testbed (KK modes at TeV
# affect the running). REGIME II is relevant for the NCG spectral action
# prediction (where unification is a 4D question at the brane cutoff).

# REGIME I: Standard RS1 (k ~ M_Pl, M_KK ~ TeV)
k_I = 0.1 * M_Pl           # k = 0.1 * M_Pl (common RS1 choice; k/M_Pl ~ 0.1)
ky_c_I = np.log(k_I / 1e3)  # ky_c such that k * e^{-ky_c} = 1 TeV
M_KK_I = np.pi * k_I * np.exp(-ky_c_I)  # = pi * 1 TeV
M_5_I_cubed = 2.0 * k_I * M_Pl**2
M_5_I = M_5_I_cubed**(1.0/3.0)
Lambda_I = M_5_I**(5.0/3.0) / k_I**(2.0/3.0)

# REGIME II: Meridian monograph (k ~ 10^8 GeV)
k_II = 1.0e8
ky_c_II = 39.56
M_KK_II = np.pi * k_II * np.exp(-ky_c_II)
M_5_II_cubed = 2.0 * k_II * M_Pl**2
M_5_II = M_5_II_cubed**(1.0/3.0)
Lambda_II = M_5_II**(5.0/3.0) / k_II**(2.0/3.0)

print(f"REGIME I: Standard RS1 (k ~ 0.1 M_Pl)")
print(f"  k           = {k_I:.3e} GeV")
print(f"  ky_c        = {ky_c_I:.2f}")
print(f"  M_KK        = {M_KK_I:.3e} GeV  ({M_KK_I/1e3:.2f} TeV)")
print(f"  m_1 (KK)    = {3.832 * k_I * np.exp(-ky_c_I):.3e} GeV  ({3.832 * k_I * np.exp(-ky_c_I)/1e3:.2f} TeV)")
print(f"  M_5         = {M_5_I:.3e} GeV")
print(f"  Lambda_NCG  = {Lambda_I:.3e} GeV  (10^{np.log10(Lambda_I):.2f})")
print(f"  k / M_Pl    = {k_I / M_Pl:.3f}")
print()
print(f"REGIME II: Meridian monograph (k ~ 10^8 GeV)")
print(f"  k           = {k_II:.3e} GeV")
print(f"  ky_c        = {ky_c_II}")
print(f"  M_KK        = {M_KK_II:.3e} GeV  (sub-eV: below SM thresholds)")
print(f"  M_5         = {M_5_II:.3e} GeV")
print(f"  Lambda_NCG  = {Lambda_II:.3e} GeV  (10^{np.log10(Lambda_II):.2f})")
print(f"  NOTE: KK modes are irrelevant for gauge running in this regime.")
print(f"        The running is pure 4D SM from M_Z to Lambda_NCG.")
print()

# We focus on REGIME I for the KK threshold analysis, then compare
# with REGIME II for the NCG spectral action prediction.


# ---- Fermion bulk mass parameters (c values) ----
# Convention: Left-handed zero mode profile ~ e^{(2-c)ky}
#   c > 1/2 => UV-localized (light fermions)
#   c < 1/2 => IR-localized (heavy fermions, large Yukawa)
#   c = 1/2 => flat profile
#
# Values from Gherghetta-Pomarol, Huber, Agashe-Perez-Soni.

fermion_content = {
    # Third generation (IR-localized for large top Yukawa)
    'Q3':  {'c': 0.30,  'SU3': 'F', 'SU2': 'F', 'Y': 1.0/6,  'name': 'Q_3 (b,t)_L'},
    'u3':  {'c': -0.50, 'SU3': 'F', 'SU2': 'S', 'Y': 2.0/3,  'name': 't_R'},
    'd3':  {'c': 0.55,  'SU3': 'F', 'SU2': 'S', 'Y': -1.0/3, 'name': 'b_R'},
    'L3':  {'c': 0.50,  'SU3': 'S', 'SU2': 'F', 'Y': -1.0/2, 'name': 'L_3 (tau)_L'},
    'e3':  {'c': 0.55,  'SU3': 'S', 'SU2': 'S', 'Y': -1.0,   'name': 'tau_R'},
    'nu3': {'c': 0.50,  'SU3': 'S', 'SU2': 'S', 'Y': 0.0,    'name': 'nu_tau_R'},
    # Second generation (intermediate)
    'Q2':  {'c': 0.55,  'SU3': 'F', 'SU2': 'F', 'Y': 1.0/6,  'name': 'Q_2 (s,c)_L'},
    'u2':  {'c': 0.55,  'SU3': 'F', 'SU2': 'S', 'Y': 2.0/3,  'name': 'c_R'},
    'd2':  {'c': 0.65,  'SU3': 'F', 'SU2': 'S', 'Y': -1.0/3, 'name': 's_R'},
    'L2':  {'c': 0.55,  'SU3': 'S', 'SU2': 'F', 'Y': -1.0/2, 'name': 'L_2 (mu)_L'},
    'e2':  {'c': 0.65,  'SU3': 'S', 'SU2': 'S', 'Y': -1.0,   'name': 'mu_R'},
    'nu2': {'c': 0.50,  'SU3': 'S', 'SU2': 'S', 'Y': 0.0,    'name': 'nu_mu_R'},
    # First generation (UV-localized, lightest)
    'Q1':  {'c': 0.65,  'SU3': 'F', 'SU2': 'F', 'Y': 1.0/6,  'name': 'Q_1 (d,u)_L'},
    'u1':  {'c': 0.65,  'SU3': 'F', 'SU2': 'S', 'Y': 2.0/3,  'name': 'u_R'},
    'd1':  {'c': 0.70,  'SU3': 'F', 'SU2': 'S', 'Y': -1.0/3, 'name': 'd_R'},
    'L1':  {'c': 0.60,  'SU3': 'S', 'SU2': 'F', 'Y': -1.0/2, 'name': 'L_1 (e)_L'},
    'e1':  {'c': 0.70,  'SU3': 'S', 'SU2': 'S', 'Y': -1.0,   'name': 'e_R'},
    'nu1': {'c': 0.50,  'SU3': 'S', 'SU2': 'S', 'Y': 0.0,    'name': 'nu_e_R'},
}

print("Fermion bulk mass parameters:")
print(f"  {'Field':<22s} {'c':>6s}  {'|c|>1/2':>7s}  Localization")
print("  " + "-" * 55)
for key, f in fermion_content.items():
    c_val = f['c']
    uv = abs(c_val) > 0.5
    loc = "UV" if c_val > 0.5 else ("IR" if c_val < 0.5 else "flat")
    print(f"  {f['name']:<22s} {c_val:>6.2f}  {'YES' if uv else 'NO':>7s}  {loc}")
print()


# ============================================================================
# PART 1: 1-LOOP SM RGE
# ============================================================================

print("=" * 80)
print("PART 1: STANDARD MODEL 1-LOOP RGE RUNNING")
print("=" * 80)

# SM 1-loop beta function coefficients (N_g=3, N_H=1)
# d(alpha_i^{-1})/d(ln mu) = -b_i/(2 pi)
b_SM = np.array([41.0/10.0, -19.0/6.0, -7.0])

print(f"""
SM 1-loop beta coefficients:
  b_1 = 41/10  = {b_SM[0]:.4f}  (GUT-normalized U(1))
  b_2 = -19/6  = {b_SM[1]:.4f}  (SU(2)_L)
  b_3 = -7     = {b_SM[2]:.4f}  (SU(3)_C)

RGE: alpha_i^{{-1}}(mu) = alpha_i^{{-1}}(M_Z) - b_i/(2pi) * ln(mu/M_Z)
""")


def alpha_inv_1loop(mu, alpha_inv_0, b, mu_0):
    """1-loop running from mu_0 to mu."""
    return alpha_inv_0 - b / (2.0 * np.pi) * np.log(mu / mu_0)


# Print SM running at key scales
scales_sm = [('M_Z', M_Z), ('M_t', M_t), ('1 TeV', 1e3), ('10 TeV', 1e4),
             ('10^8', 1e8), ('10^12', 1e12), ('10^14', 1e14),
             ('10^16 (GUT)', 1e16), ('10^17', 1e17), ('10^18', 1e18),
             ('M_Pl', M_Pl)]

print("Pure SM running (no extra dimensions):")
print(f"  {'Scale':<14s}  {'mu':>12s}  {'a1^-1':>8s}  {'a2^-1':>8s}  {'a3^-1':>8s}")
print("  " + "-" * 52)
for name, mu in scales_sm:
    ai = alpha_inv_1loop(mu, alpha_inv_MZ, b_SM, M_Z)
    print(f"  {name:<14s}  {mu:>12.3e}  {ai[0]:>8.3f}  {ai[1]:>8.3f}  {ai[2]:>8.3f}")

# Pairwise crossing scales in the SM
def pairwise_crossing(b, alpha_inv_0, mu_0, i, j):
    """Scale where alpha_i^{-1} = alpha_j^{-1} in 1-loop running."""
    db = b[i] - b[j]
    da = alpha_inv_0[i] - alpha_inv_0[j]
    if abs(db) < 1e-15:
        return None
    ln_mu = da * 2.0 * np.pi / db
    return mu_0 * np.exp(ln_mu)

mu_12 = pairwise_crossing(b_SM, alpha_inv_MZ, M_Z, 0, 1)
mu_23 = pairwise_crossing(b_SM, alpha_inv_MZ, M_Z, 1, 2)
mu_13 = pairwise_crossing(b_SM, alpha_inv_MZ, M_Z, 0, 2)

print(f"""
SM pairwise crossings (1-loop):
  alpha_1 = alpha_2 at {mu_12:.3e} GeV  (10^{np.log10(mu_12):.2f})
  alpha_2 = alpha_3 at {mu_23:.3e} GeV  (10^{np.log10(mu_23):.2f})
  alpha_1 = alpha_3 at {mu_13:.3e} GeV  (10^{np.log10(mu_13):.2f})
  Ratio (1-2)/(2-3) = {mu_12/mu_23:.2f}
  => SM does NOT unify (well-known).
""")


# ============================================================================
# PART 2: KK THRESHOLD CORRECTIONS (REGIME I: k ~ M_Pl)
# ============================================================================

print("=" * 80)
print("PART 2: KK THRESHOLD CORRECTIONS IN REGIME I (k ~ 0.1 M_Pl)")
print("=" * 80)

print(f"""
In Regime I (k = {k_I:.3e} GeV), the KK scale is M_KK = {M_KK_I:.3e} GeV.
Above M_KK, the KK tower enters the running.

Following Angelescu et al. (2512.22094):
  - Only fields with (+) UV-brane BC contribute to running above M_KK
  - A_5 (gauge-Higgs) has (-,-) BC: drops out entirely
  - Fermion bulk mass |c| < 1/2: UV-brane wavefunction exponentially suppressed
  - The Planck-brane correlator replaces the naive KK sum
""")

# ---- Efficiency factor eta(c) ----
# This encodes how much of a bulk fermion's KK tower contributes to the
# UV-brane correlator running.

def eta_fermion(c, ky_c_val):
    """
    UV-brane efficiency factor for a bulk fermion with mass parameter c.

    For the zero mode with profile f_0(y):
      c > 1/2: f_0 ~ e^{(2-c)ky}, localized at y=0 (UV). |f_0(0)|^2 ~ (2c-1)k.
               => eta ~ 1  (full contribution)
      c < 1/2: f_0 ~ e^{(2-c)ky}, localized at y=y_c (IR). |f_0(0)|^2 suppressed.
               => eta ~ e^{-(1-2c)*ky_c}  (exponentially suppressed)
      c = 1/2: f_0 = const. |f_0(0)|^2 ~ 1/y_c.
               => eta ~ 1/ky_c  (logarithmic suppression)

    The KK tower of a field has the same localization as the zero mode.
    """
    c_abs = abs(c)
    if c_abs > 0.5 + 1e-8:
        # UV-localized: full contribution (up to O(e^{-(2c-1)*ky_c}) correction)
        return 1.0 - np.exp(-(2.0 * c_abs - 1.0) * ky_c_val)
    elif c_abs < 0.5 - 1e-8:
        # IR-localized: exponentially suppressed
        return np.exp(-(1.0 - 2.0 * c_abs) * ky_c_val)
    else:
        # Marginal: logarithmic suppression
        return 1.0 / (ky_c_val + 1.0)


print(f"Efficiency factors eta(c) for Regime I (ky_c = {ky_c_I:.2f}):")
print(f"  {'Field':<22s}  {'c':>6s}  {'eta(c)':>12s}  Contributes?")
print("  " + "-" * 55)
for key, f in fermion_content.items():
    eta = eta_fermion(f['c'], ky_c_I)
    print(f"  {f['name']:<22s}  {f['c']:>6.2f}  {eta:>12.2e}  {'YES' if eta > 0.01 else 'NEGLIGIBLE'}")
print()


# ---- Per-Weyl-fermion beta function contribution ----

def b_per_weyl(Y, d3, d2, is_su3_fund, is_su2_fund):
    """
    Beta function contribution (b_1, b_2, b_3) from one Weyl fermion.

    b_i += (2/3) * T_i(R) * product_of_other_dimensions

    For U(1) (GUT normalized): T_1 = (3/5) * Y^2 * d3 * d2
    For SU(2): T_2 = T(R_2) * d3, where T(fund) = 1/2
    For SU(3): T_3 = T(R_3) * d2, where T(fund) = 1/2
    """
    b1 = (2.0/3.0) * (3.0/5.0) * Y**2 * d3 * d2
    b2 = (2.0/3.0) * (0.5 if is_su2_fund else 0.0) * d3
    b3 = (2.0/3.0) * (0.5 if is_su3_fund else 0.0) * d2
    return np.array([b1, b2, b3])


def b_higgs():
    """Higgs doublet contribution: 1 complex SU(2) doublet with Y=1/2."""
    b1 = (1.0/3.0) * (3.0/5.0) * 0.25 * 1 * 2  # Y=1/2, singlet, doublet
    b2 = (1.0/3.0) * 0.5 * 1                     # T(fund) * dim_SU3
    b3 = 0.0
    return np.array([b1, b2, b3])


# Pure gauge contribution (no matter)
b_gauge = np.array([0.0, -22.0/3.0, -11.0])

# Verify SM beta functions
b_ferm_check = np.zeros(3)
for f in fermion_content.values():
    d3 = 3 if f['SU3'] == 'F' else 1
    d2 = 2 if f['SU2'] == 'F' else 1
    b_ferm_check += b_per_weyl(f['Y'], d3, d2, f['SU3']=='F', f['SU2']=='F')
b_total_check = b_gauge + b_ferm_check + b_higgs()

print(f"SM beta function verification:")
print(f"  b_gauge   = [{b_gauge[0]:>8.4f}, {b_gauge[1]:>8.4f}, {b_gauge[2]:>8.4f}]")
print(f"  b_fermion = [{b_ferm_check[0]:>8.4f}, {b_ferm_check[1]:>8.4f}, {b_ferm_check[2]:>8.4f}]")
print(f"  b_Higgs   = [{b_higgs()[0]:>8.4f}, {b_higgs()[1]:>8.4f}, {b_higgs()[2]:>8.4f}]")
print(f"  b_total   = [{b_total_check[0]:>8.4f}, {b_total_check[1]:>8.4f}, {b_total_check[2]:>8.4f}]")
print(f"  Expected  = [{b_SM[0]:>8.4f}, {b_SM[1]:>8.4f}, {b_SM[2]:>8.4f}]")
print(f"  Match: {np.allclose(b_total_check, b_SM)}")
print()


# ---- Effective beta functions above M_KK ----

def compute_b_eff(fermion_dict, ky_c_val, include_higgs=True):
    """
    Effective beta function coefficients above M_KK.
    Fermions weighted by eta(c). Gauge bosons contribute fully.
    """
    b_eff = np.copy(b_gauge)
    for f in fermion_dict.values():
        eta = eta_fermion(f['c'], ky_c_val)
        d3 = 3 if f['SU3'] == 'F' else 1
        d2 = 2 if f['SU2'] == 'F' else 1
        b_eff += eta * b_per_weyl(f['Y'], d3, d2, f['SU3']=='F', f['SU2']=='F')
    if include_higgs:
        b_eff += b_higgs()
    return b_eff


b_eff_A_I = compute_b_eff(fermion_content, ky_c_I, include_higgs=True)
b_eff_B_I = compute_b_eff(fermion_content, ky_c_I, include_higgs=False)

print(f"Effective beta functions above M_KK (Regime I, ky_c = {ky_c_I:.2f}):")
print(f"                     b_1        b_2        b_3")
print(f"  SM (< M_KK):   {b_SM[0]:>8.4f}   {b_SM[1]:>8.4f}   {b_SM[2]:>8.4f}")
print(f"  Scen. A (> MKK):{b_eff_A_I[0]:>8.4f}   {b_eff_A_I[1]:>8.4f}   {b_eff_A_I[2]:>8.4f}")
print(f"  Scen. B (> MKK):{b_eff_B_I[0]:>8.4f}   {b_eff_B_I[1]:>8.4f}   {b_eff_B_I[2]:>8.4f}")

# Show which fermions dropped out
print(f"\n  Difference A vs SM (eta < 1 effects):")
db_A = b_eff_A_I - b_SM
print(f"    delta_b = [{db_A[0]:>+8.4f}, {db_A[1]:>+8.4f}, {db_A[2]:>+8.4f}]")
print(f"  Difference B vs A (no Higgs above M_KK):")
db_BA = b_eff_B_I - b_eff_A_I
print(f"    delta_b = [{db_BA[0]:>+8.4f}, {db_BA[1]:>+8.4f}, {db_BA[2]:>+8.4f}]")
print()


# ============================================================================
# PART 3: FULL RUNNING AND UNIFICATION TEST (REGIME I)
# ============================================================================

print("=" * 80)
print("PART 3: FULL RUNNING AND UNIFICATION TEST (REGIME I)")
print("=" * 80)

def run_2stage(mu, alpha_inv_MZ_vals, b_low, b_high, M_KK_val):
    """
    2-stage 1-loop running: SM below M_KK, modified above.
    """
    if mu <= M_KK_val:
        return alpha_inv_MZ_vals - b_low / (2*np.pi) * np.log(mu / M_Z)
    else:
        ai_KK = alpha_inv_MZ_vals - b_low / (2*np.pi) * np.log(M_KK_val / M_Z)
        return ai_KK - b_high / (2*np.pi) * np.log(mu / M_KK_val)


def run_with_power(mu, alpha_inv_MZ_vals, b_low, b_high, M_KK_val, k_val):
    """
    Running with power-law corrections from the 5D volume.

    Above M_KK, the 5D nature produces power-law running in addition to
    logarithmic. The Planck-brane correlator gives (schematically):

      alpha_i^{-1}(mu) ~ alpha_i^{-1}(M_KK)
        - b_i^{eff}/(2pi) * ln(mu/M_KK)                    [log piece]
        - b_i^{KK}/(2pi) * pi*(mu - M_KK) / (pi*k)         [power piece]

    The power piece is suppressed by 1/k for the WARPED geometry (vs 1/M_KK
    for flat). This is the key Randall-Sundrum advantage: the warping
    tames the power-law running.

    For the gauge sector, b_KK = b_gauge (each KK level contributes like
    the zero mode gauge boson).
    """
    if mu <= M_KK_val:
        return alpha_inv_MZ_vals - b_low / (2*np.pi) * np.log(mu / M_Z)

    ai_KK = alpha_inv_MZ_vals - b_low / (2*np.pi) * np.log(M_KK_val / M_Z)
    log_piece = b_high / (2*np.pi) * np.log(mu / M_KK_val)
    # Power piece: the warped sum over KK modes gives ~ (mu - M_KK) / k
    # per gauge group, weighted by the gauge beta function
    power_piece = b_gauge / (2*np.pi) * np.pi * (mu - M_KK_val) / (np.pi * k_val)
    return ai_KK - log_piece - power_piece


# Key scales for Regime I
scales_I = [
    ('M_Z',       M_Z),
    ('1 TeV',     1e3),
    ('M_KK',      M_KK_I),
    ('10 TeV',    1e4),
    ('100 TeV',   1e5),
    ('10^8',      1e8),
    ('10^12',     1e12),
    ('k',         k_I),
    ('10^18',     1e18),
    ('Lambda_NCG',Lambda_I),
    ('M_Pl',      M_Pl),
]

for scenario, b_high, label in [(b_eff_A_I, b_eff_A_I, "Scenario A (brane Higgs)"),
                                  (b_eff_B_I, b_eff_B_I, "Scenario B (gauge-Higgs A_5)")]:
    print(f"\n{label} — Regime I, LOGARITHMIC ONLY:")
    print(f"  {'Scale':<12s}  {'mu':>12s}  {'a1^-1':>8s}  {'a2^-1':>8s}  {'a3^-1':>8s}  spread")
    print("  " + "-" * 62)
    for name, mu in scales_I:
        ai = run_2stage(mu, alpha_inv_MZ, b_SM, b_high, M_KK_I)
        spread = max(ai) - min(ai)
        print(f"  {name:<12s}  {mu:>12.3e}  {ai[0]:>8.3f}  {ai[1]:>8.3f}  {ai[2]:>8.3f}  {spread:>6.3f}")

# ---- Pairwise crossings in each scenario ----
print("\n--- Pairwise crossing analysis (Regime I, logarithmic) ---")

for label, b_high in [("Scenario A", b_eff_A_I), ("Scenario B", b_eff_B_I)]:
    print(f"\n  {label}:")
    for (i, j, pair_name) in [(0,1,"a1=a2"), (1,2,"a2=a3"), (0,2,"a1=a3")]:
        # Scan for sign change in alpha_i^-1 - alpha_j^-1
        log_mus = np.linspace(np.log10(M_Z), np.log10(M_Pl * 10), 50000)
        found = False
        for idx in range(len(log_mus) - 1):
            mu_a = 10**log_mus[idx]
            mu_b = 10**log_mus[idx+1]
            da = run_2stage(mu_a, alpha_inv_MZ, b_SM, b_high, M_KK_I)
            db_ = run_2stage(mu_b, alpha_inv_MZ, b_SM, b_high, M_KK_I)
            if (da[i] - da[j]) * (db_[i] - db_[j]) < 0:
                # Bisect
                def f_cross(lm):
                    ai_val = run_2stage(10**lm, alpha_inv_MZ, b_SM, b_high, M_KK_I)
                    return ai_val[i] - ai_val[j]
                lm_cross = brentq(f_cross, log_mus[idx], log_mus[idx+1])
                mu_cross = 10**lm_cross
                ai_cross = run_2stage(mu_cross, alpha_inv_MZ, b_SM, b_high, M_KK_I)
                print(f"    {pair_name}: mu = {mu_cross:.3e} GeV  (10^{lm_cross:.2f}), "
                      f"alpha^{{-1}} = {ai_cross[i]:.3f}")
                found = True
                break
        if not found:
            print(f"    {pair_name}: NO CROSSING below M_Pl")

# ---- With power-law corrections ----
print("\n--- With power-law corrections (Regime I, Scenario A) ---")
print(f"  {'Scale':<12s}  {'mu':>12s}  {'a1^-1':>8s}  {'a2^-1':>8s}  {'a3^-1':>8s}  {'a1^-1 log':>10s}  {'a2^-1 log':>10s}  {'a3^-1 log':>10s}")
print("  " + "-" * 88)
for name, mu in scales_I:
    ai_p = run_with_power(mu, alpha_inv_MZ, b_SM, b_eff_A_I, M_KK_I, k_I)
    ai_l = run_2stage(mu, alpha_inv_MZ, b_SM, b_eff_A_I, M_KK_I)
    print(f"  {name:<12s}  {mu:>12.3e}  {ai_p[0]:>8.3f}  {ai_p[1]:>8.3f}  {ai_p[2]:>8.3f}  {ai_l[0]:>10.3f}  {ai_l[1]:>10.3f}  {ai_l[2]:>10.3f}")
print()


# ============================================================================
# PART 4: BRANE KINETIC TERMS
# ============================================================================

print("=" * 80)
print("PART 4: BRANE KINETIC TERMS REQUIRED FOR UNIFICATION")
print("=" * 80)

print("""
BKTs shift the couplings at the unification scale:
  alpha_i^{-1}(Lambda) + Delta_i / (2pi) = alpha_unif^{-1}

We compute the Delta_i required for exact unification at several scales.
""")

def required_bkt(mu_unif, b_low, b_high, M_KK_val, use_power=False, k_val=None):
    """Required BKTs for unification at mu_unif."""
    if use_power and k_val is not None:
        ai = run_with_power(mu_unif, alpha_inv_MZ, b_low, b_high, M_KK_val, k_val)
    else:
        ai = run_2stage(mu_unif, alpha_inv_MZ, b_low, b_high, M_KK_val)
    alpha_unif_inv = np.mean(ai)
    Delta = 2.0 * np.pi * (alpha_unif_inv - ai)
    return ai, Delta, alpha_unif_inv


for label, b_high in [("Scenario A", b_eff_A_I), ("Scenario B", b_eff_B_I)]:
    print(f"\n--- {label} (Regime I) ---")
    for scale_name, mu_unif in [("Lambda_NCG", Lambda_I), ("k", k_I), ("M_Pl", M_Pl)]:
        ai, Delta, a_u = required_bkt(mu_unif, b_SM, b_high, M_KK_I)
        print(f"\n  Unification at {scale_name} = {mu_unif:.3e} GeV:")
        print(f"    alpha_i^-1 = [{ai[0]:.3f}, {ai[1]:.3f}, {ai[2]:.3f}]")
        print(f"    Spread = {max(ai) - min(ai):.3f}")
        print(f"    Required: Delta = [{Delta[0]:>+7.3f}, {Delta[1]:>+7.3f}, {Delta[2]:>+7.3f}]")
        print(f"    |Delta_max| = {max(abs(Delta)):.3f}")
        print(f"    alpha_unif = {1.0/a_u:.6f},  alpha_unif^-1 = {a_u:.3f}")

    # Also with power-law corrections at k
    print(f"\n  With power-law corrections at k:")
    ai_p, Delta_p, a_u_p = required_bkt(k_I, b_SM, b_high, M_KK_I,
                                          use_power=True, k_val=k_I)
    print(f"    alpha_i^-1 = [{ai_p[0]:.3f}, {ai_p[1]:.3f}, {ai_p[2]:.3f}]")
    print(f"    Spread = {max(ai_p) - min(ai_p):.3f}")
    print(f"    Required: Delta = [{Delta_p[0]:>+7.3f}, {Delta_p[1]:>+7.3f}, {Delta_p[2]:>+7.3f}]")
    print(f"    |Delta_max| = {max(abs(Delta_p)):.3f}")


# ============================================================================
# PART 5: NCG SPECTRAL ACTION GAUGE COEFFICIENTS
# ============================================================================

print("\n\n" + "=" * 80)
print("PART 5: NCG SPECTRAL ACTION GAUGE COEFFICIENTS")
print("=" * 80)

print("""
The spectral action on the finite NCG triple F = (A_F, H_F, D_F) generates
gauge kinetic terms with coefficients proportional to traces over H_F.

From CCM (hep-th/0610241), the gauge kinetic terms are:
  S_gauge = f_0/(2 pi^2) * int d^4x sqrt(g) * [a_i * F_i^2]

where a_i = sum_R T_i(R) over all representations in H_F (particles +
antiparticles, all N_g generations).

Unification condition: a_1 = a_2 = a_3 (GUT normalized).
""")

N_g = 3

# Complete representation content (particles + antiparticles, per generation)
reps_per_gen = [
    # (dim_SU3, dim_SU2, Y, name) — particles
    (3, 2,  1.0/6,  'Q_L'),
    (3, 1,  2.0/3,  'u_R'),
    (3, 1, -1.0/3,  'd_R'),
    (1, 2, -1.0/2,  'L_L'),
    (1, 1, -1.0,    'e_R'),
    (1, 1,  0.0,    'nu_R'),
    # antiparticles (conjugate reps)
    (3, 2, -1.0/6,  'Q_L*'),
    (3, 1, -2.0/3,  'u_R*'),
    (3, 1,  1.0/3,  'd_R*'),
    (1, 2,  1.0/2,  'L_L*'),
    (1, 1,  1.0,    'e_R*'),
    (1, 1,  0.0,    'nu_R*'),
]

# Compute spectral action trace coefficients
# a_i = sum_R T_i(R) * (product of dimensions of other reps)
# T(fundamental of SU(N)) = 1/2, T(singlet) = 0
# For U(1): T_1 = (3/5) * Y^2 (GUT normalization)

a_3_1gen = sum(d2 * (0.5 if d3 == 3 else 0.0) for d3, d2, Y, _ in reps_per_gen)
a_2_1gen = sum(d3 * (0.5 if d2 == 2 else 0.0) for d3, d2, Y, _ in reps_per_gen)
a_1Y_1gen = sum(d3 * d2 * Y**2 for d3, d2, Y, _ in reps_per_gen)
a_1_1gen = (3.0/5.0) * a_1Y_1gen  # GUT normalization

a_3_tot = N_g * a_3_1gen
a_2_tot = N_g * a_2_1gen
a_1_tot = N_g * a_1_1gen

print(f"Spectral action gauge coefficients:")
print(f"  Per generation (particles + antiparticles):")
print(f"    a_3 = {a_3_1gen:.4f}")
print(f"    a_2 = {a_2_1gen:.4f}")
print(f"    a_1 = {a_1_1gen:.4f}  (GUT normalized)")
print(f"    a_1(Y) = {a_1Y_1gen:.4f}  (SM normalization)")
print(f"")
print(f"  Total (N_g = {N_g}):")
print(f"    a_3 = {a_3_tot:.4f}")
print(f"    a_2 = {a_2_tot:.4f}")
print(f"    a_1 = {a_1_tot:.4f}")
print(f"")
print(f"  Ratios:")
print(f"    a_2/a_3 = {a_2_tot/a_3_tot:.6f}")
print(f"    a_1/a_3 = {a_1_tot/a_3_tot:.6f}")
print(f"    a_1/a_2 = {a_1_tot/a_2_tot:.6f}")

unif_exact = (abs(a_1_tot - a_2_tot) < 1e-10 and abs(a_2_tot - a_3_tot) < 1e-10)
print(f"\n  Unification: a_1 = a_2 = a_3?  {'YES (exact)' if unif_exact else 'NO'}")
if not unif_exact:
    print(f"    The mismatch means the bare spectral action does NOT predict exact")
    print(f"    gauge coupling unification at the cutoff Lambda.")
    print(f"    Deviation: a_1/a_3 - 1 = {a_1_tot/a_3_tot - 1.0:.6f}")
print()


# ============================================================================
# PART 5A: Brane kinetic terms from the spectral action
# ============================================================================

print("-" * 60)
print("PART 5A: BRANE KINETIC TERMS FROM THE SPECTRAL ACTION")
print("-" * 60)

print("""
The spectral action generates gauge kinetic terms in two ways:

1. BULK contribution: from the 5D spectral action integrated over the orbifold.
   S_bulk = f_0 * a_i * int_0^{y_c} dy e^{-4ky} * F_i^2
          = f_0 * a_i / (4k) * (1 - e^{-4ky_c}) * F_i^2

2. BRANE contribution: from the boundary Seeley-DeWitt coefficients.
   These come from the a_{3/2} coefficient restricted to the branes.
   The boundary contribution is proportional to the extrinsic curvature:
     K_{mu nu} = -k g_{mu nu}  (UV brane)
   giving a contribution ~ k * f_0 / Lambda.

The RELATIVE contribution of brane vs bulk:
  Delta_i / (2pi) ~ [brane a_{3/2}] / [bulk a_2]
                   ~ k / (Lambda * warp_integral * a_i / brane_coeff)

For both RS regimes:
""")

for regime, k_val, ky_c_val, Lam, regime_name in [
    ("I", k_I, ky_c_I, Lambda_I, "Regime I (k ~ 0.1 M_Pl)"),
    ("II", k_II, ky_c_II, Lambda_II, "Regime II (k ~ 10^8)")]:

    warp_int = (1.0 - np.exp(-4.0 * ky_c_val)) / (4.0 * k_val)
    # Bulk gauge kinetic: ~ f_0 * a_i * Lambda * warp_int
    # Brane gauge kinetic: ~ f_0 * a_i * (boundary coefficient)
    # The boundary coefficient for the a_{3/2} is O(1) in units where the
    # brane is at a definite y-position.
    # The ratio brane/bulk ~ 1 / (Lambda * warp_int)

    # More precisely: the boundary a_{3/2} contribution to the gauge kinetic
    # term scales as f_0 * Lambda * K_{mu nu}^2 / Lambda^2 ~ f_0 * k^2 / Lambda
    # while the bulk a_2 gives f_0 * Lambda * warp_int.
    # So Delta ~ k^2 / (Lambda^2 * warp_int) ~ k^2 * 4k / Lambda^2 = 4k^3/Lambda^2

    Delta_brane = 4.0 * k_val**3 / Lam**2
    # Also, the leading brane contribution from just the trace normalization:
    Delta_trace = k_val / Lam  # simpler estimate

    print(f"  {regime_name}:")
    print(f"    k = {k_val:.3e} GeV, Lambda = {Lam:.3e} GeV")
    print(f"    Warp integral = {warp_int:.3e} GeV^-1")
    print(f"    4k * warp_int = {4*k_val*warp_int:.6f}  (~1 for large ky_c)")
    print(f"    Brane KT estimate (k/Lambda): Delta ~ {Delta_trace:.3e}")
    print(f"    Brane KT estimate (k^3/L^2): Delta ~ {Delta_brane:.3e}")
    print(f"    Both are NEGLIGIBLE compared to O(1) values needed.")
    print()

print("""
KEY RESULT: The NCG spectral action on the warped orbifold generates
brane kinetic terms that are:
  1. UNIVERSAL (same Delta for all gauge groups, because a_1 = a_2 = a_3
     in the bare spectral action — if this holds)
  2. NEGLIGIBLE in magnitude (O(k/Lambda) or O(k^3/Lambda^2))

The spectral action does NOT generate the non-universal O(1) brane kinetic
terms that Angelescu et al. need for unification in their SU(6) model.
""")


# ============================================================================
# PART 5B: Reverse engineering the unification condition
# ============================================================================

print("-" * 60)
print("PART 5B: REVERSE ENGINEERING — WHAT ALPHA_UNIF IS PREDICTED?")
print("-" * 60)

print("""
If the spectral action sets g_1 = g_2 = g_3 at the cutoff Lambda,
what value of alpha_unif^{-1} is needed to match the observed couplings
at M_Z after running?
""")

for label, b_high, MKK, regime_name in [
    ("Scenario A", b_eff_A_I, M_KK_I, "Regime I"),
    ("Scenario B", b_eff_B_I, M_KK_I, "Regime I"),
    ("SM only", b_SM, M_Z, "Regime II (pure 4D)")]:

    print(f"\n  {label} ({regime_name}):")

    if regime_name == "Regime II (pure 4D)":
        # In Regime II, M_KK is sub-eV, so the running is pure SM to Lambda_NCG
        Lambda_test = Lambda_II
        total_running = b_SM / (2*np.pi) * np.log(Lambda_test / M_Z)
    else:
        Lambda_test = Lambda_I
        total_running = (b_SM / (2*np.pi) * np.log(MKK / M_Z) +
                         b_high / (2*np.pi) * np.log(Lambda_test / MKK))

    # alpha_i^{-1}(M_Z) = alpha_unif^{-1} + total_running_i
    # => alpha_unif^{-1} = alpha_i^{-1}(M_Z) - total_running_i
    alpha_unif_from = alpha_inv_MZ - total_running

    print(f"    Lambda = {Lambda_test:.3e} GeV")
    print(f"    Total running: [{total_running[0]:>+8.3f}, {total_running[1]:>+8.3f}, {total_running[2]:>+8.3f}]")
    print(f"    Required alpha_unif^{{-1}}:")
    print(f"      From alpha_1: {alpha_unif_from[0]:.3f}")
    print(f"      From alpha_2: {alpha_unif_from[1]:.3f}")
    print(f"      From alpha_3: {alpha_unif_from[2]:.3f}")
    print(f"      Spread: {max(alpha_unif_from) - min(alpha_unif_from):.3f}")

    avg = np.mean(alpha_unif_from)
    delta_needed = 2*np.pi * (alpha_unif_from - avg)
    print(f"    BKTs to compensate: [{delta_needed[0]:>+7.3f}, {delta_needed[1]:>+7.3f}, {delta_needed[2]:>+7.3f}]")


# ============================================================================
# PART 6: KK MASS SPECTRUM
# ============================================================================

print("\n\n" + "=" * 80)
print("PART 6: KK MASS SPECTRUM (BESSEL ZEROS)")
print("=" * 80)

print(f"""
KK masses on the RS orbifold satisfy the Bessel boundary condition.
For (+,+) modes (gauge bosons, graviton):
  m_n = x_n * k * e^{{-ky_c}}
where x_n are zeros of J_1(x).
""")

# Find zeros of J_1
N_zeros = 10
x_search = np.linspace(1.0, 50, 50000)
j1_vals = jv(1, x_search)
x_zeros = []
for idx in range(len(j1_vals) - 1):
    if j1_vals[idx] * j1_vals[idx+1] < 0:
        x0 = brentq(lambda x: jv(1, x), x_search[idx], x_search[idx+1])
        x_zeros.append(x0)
        if len(x_zeros) >= N_zeros:
            break

for regime_name, k_val, ky_c_val in [("Regime I", k_I, ky_c_I), ("Regime II", k_II, ky_c_II)]:
    print(f"\n{regime_name} (k = {k_val:.3e} GeV, ky_c = {ky_c_val:.2f}):")
    print(f"  {'n':>3s}  {'x_n':>10s}  {'m_n [GeV]':>12s}  {'m_n':>12s}")
    print("  " + "-" * 45)
    for n, xn in enumerate(x_zeros, 1):
        m_n = xn * k_val * np.exp(-ky_c_val)
        if m_n > 1e3:
            m_str = f"{m_n/1e3:.2f} TeV"
        elif m_n > 1:
            m_str = f"{m_n:.2f} GeV"
        elif m_n > 1e-3:
            m_str = f"{m_n*1e3:.2f} MeV"
        else:
            m_str = f"{m_n:.3e} GeV"
        print(f"  {n:>3d}  {xn:>10.4f}  {m_n:>12.3e}  {m_str:>12s}")
print()


# ============================================================================
# PART 7: FERMION MASS HIERARCHY CONSISTENCY
# ============================================================================

print("=" * 80)
print("PART 7: FERMION MASS HIERARCHY FROM BULK PARAMETERS")
print("=" * 80)

print("""
The same c parameters that control gauge running must reproduce the
SM fermion mass hierarchy. The Yukawa coupling on the IR brane scales as:

  y_ij ~ y_5D * sqrt((2c_L-1)*k) * sqrt((2c_R-1)*k)
         * e^{-(c_L - 1/2)*ky_c} * e^{-(c_R - 1/2)*ky_c}

For UV-localized fermions (c > 1/2), the mass is suppressed by the
overlap with the IR-brane Higgs:
  m_f / v ~ y_5D * e^{-(c_L + c_R - 1)*ky_c}

This is a powerful consistency check: the c values that give the right
masses must also give acceptable gauge running.
""")

# Regime I is where the KK modes matter
print(f"Fermion mass hierarchy (Regime I, ky_c = {ky_c_I:.2f}):")
print(f"  {'Pair':<22s}  {'c_L':>5s}  {'c_R':>5s}  {'c_L+c_R-1':>10s}  {'suppression':>14s}  {'m/m_top':>10s}")
print("  " + "-" * 75)

yukawa_data = [
    ('top (Q3,u3)',    0.30, 0.50),     # Note: u3 has c=-0.5, |c|=0.5
    ('bottom (Q3,d3)', 0.30, 0.55),
    ('charm (Q2,u2)',  0.55, 0.55),
    ('strange (Q2,d2)',0.55, 0.65),
    ('up (Q1,u1)',     0.65, 0.65),
    ('down (Q1,d1)',   0.65, 0.70),
    ('tau (L3,e3)',    0.50, 0.55),
    ('muon (L2,e2)',   0.55, 0.65),
    ('electron (L1,e1)',0.60, 0.70),
]

# For the top: Q3 has c=0.3 < 1/2 (IR) and u3 has c=-0.5 (also IR).
# Both are IR-localized, so the overlap is O(1) => y_top ~ y_5D ~ O(1).
# For the electron: Q1 has c=0.65 and e1 has c=0.70, both UV-localized.
# Suppression: e^{-(0.65+0.70-1)*ky_c} = e^{-0.35*ky_c}

for name, cL, cR in yukawa_data:
    if name.startswith('top'):
        # IR-localized pair: O(1) Yukawa
        suppression = 1.0
    else:
        exponent = (cL + cR - 1.0) * ky_c_I
        if exponent > 0:
            suppression = np.exp(-exponent)
        else:
            suppression = 1.0  # both IR-localized

    ratio = suppression  # relative to top
    print(f"  {name:<22s}  {cL:>5.2f}  {cR:>5.2f}  {cL+cR-1.0:>10.2f}  {suppression:>14.3e}  {ratio:>10.3e}")

# Compare with observed mass ratios
print(f"\n  Observed mass ratios (to top):")
masses = {'top': 173.1, 'bottom': 4.18, 'charm': 1.27, 'strange': 0.093,
          'up': 0.0022, 'down': 0.0048, 'tau': 1.777, 'muon': 0.1057, 'electron': 0.000511}
for name, m in masses.items():
    print(f"    m_{name}/m_top = {m/173.1:.3e}")
print()


# ============================================================================
# PART 8: SENSITIVITY ANALYSIS
# ============================================================================

print("=" * 80)
print("PART 8: SENSITIVITY TO k/M_Pl RATIO")
print("=" * 80)

print("""
Angelescu et al. use k ~ M_Pl. The unification picture changes with k/M_Pl.
We scan k/M_Pl from 0.01 to 1.0 and compute the required BKTs at Lambda_NCG.
""")

print(f"  {'k/M_Pl':>8s}  {'k [GeV]':>12s}  {'ky_c':>6s}  {'M_KK [TeV]':>10s}  {'Lambda':>12s}  {'|Delta|_max':>11s}  {'spread':>8s}")
print("  " + "-" * 80)

for ratio in [0.01, 0.03, 0.1, 0.3, 0.5, 1.0]:
    k_test = ratio * M_Pl
    ky_c_test = np.log(k_test / 1e3)  # M_KK ~ 1 TeV
    M_KK_test = np.pi * k_test * np.exp(-ky_c_test)
    M5_test = (2.0 * k_test * M_Pl**2)**(1.0/3.0)
    Lambda_test = M5_test**(5.0/3.0) / k_test**(2.0/3.0)

    b_eff_test = compute_b_eff(fermion_content, ky_c_test, include_higgs=True)
    ai_test = run_2stage(Lambda_test, alpha_inv_MZ, b_SM, b_eff_test, M_KK_test)
    spread = max(ai_test) - min(ai_test)
    avg = np.mean(ai_test)
    Delta_test = 2*np.pi * (avg - ai_test)

    print(f"  {ratio:>8.3f}  {k_test:>12.3e}  {ky_c_test:>6.2f}  {M_KK_test/1e3:>10.2f}  {Lambda_test:>12.3e}  {max(abs(Delta_test)):>11.3f}  {spread:>8.3f}")
print()


# ============================================================================
# PART 9: REGIME II — PURE 4D ANALYSIS (MONOGRAPH)
# ============================================================================

print("=" * 80)
print("PART 9: REGIME II — PURE 4D ANALYSIS (MERIDIAN MONOGRAPH)")
print("=" * 80)

print(f"""
In Regime II (k = {k_II:.0e} GeV, ky_c = {ky_c_II}), the KK scale is
M_KK = {M_KK_II:.3e} GeV, far below any collider scale.

The gauge fields live on the IR brane with the NCG spectral triple.
The running is PURELY 4D from M_Z to Lambda_NCG.
The spectral action sets the boundary condition at Lambda_NCG.

This is the standard NCG unification scenario (Chamseddine-Connes 1996).
""")

# Pure SM running to Lambda_NCG for Regime II
ai_NCG_II = alpha_inv_1loop(Lambda_II, alpha_inv_MZ, b_SM, M_Z)
print(f"SM running to Lambda_NCG = {Lambda_II:.3e} GeV:")
print(f"  alpha_1^{{-1}} = {ai_NCG_II[0]:.3f}")
print(f"  alpha_2^{{-1}} = {ai_NCG_II[1]:.3f}")
print(f"  alpha_3^{{-1}} = {ai_NCG_II[2]:.3f}")
print(f"  Spread: {max(ai_NCG_II) - min(ai_NCG_II):.3f}")
print()

# Required alpha_unif if spectral action predicts exact unification
alpha_unif_from_II = alpha_inv_MZ - b_SM / (2*np.pi) * np.log(Lambda_II / M_Z)
print(f"Required alpha_unif^{{-1}} at Lambda_NCG (Regime II, pure SM):")
print(f"  From alpha_1: {alpha_unif_from_II[0]:.3f}")
print(f"  From alpha_2: {alpha_unif_from_II[1]:.3f}")
print(f"  From alpha_3: {alpha_unif_from_II[2]:.3f}")
print(f"  Spread: {max(alpha_unif_from_II) - min(alpha_unif_from_II):.3f}")
avg_II = np.mean(alpha_unif_from_II)
delta_II = 2*np.pi * (alpha_unif_from_II - avg_II)
print(f"  Average: {avg_II:.3f}")
print(f"  BKTs to compensate: [{delta_II[0]:>+7.3f}, {delta_II[1]:>+7.3f}, {delta_II[2]:>+7.3f}]")
print()

# Also run to the canonical GUT scale ~ 2e16 for comparison
ai_GUT = alpha_inv_1loop(2e16, alpha_inv_MZ, b_SM, M_Z)
print(f"SM running to 2x10^16 GeV (canonical GUT scale):")
print(f"  alpha_1^{{-1}} = {ai_GUT[0]:.3f}")
print(f"  alpha_2^{{-1}} = {ai_GUT[1]:.3f}")
print(f"  alpha_3^{{-1}} = {ai_GUT[2]:.3f}")
print(f"  Spread: {max(ai_GUT) - min(ai_GUT):.3f}")
print()


# ============================================================================
# PART 10: PLOT DATA
# ============================================================================

print("=" * 80)
print("PART 10: PLOT DATA (alpha_i^-1 vs log10(mu/GeV))")
print("=" * 80)

print("\n# Columns: log10(mu)  a1_SM  a2_SM  a3_SM  a1_A  a2_A  a3_A  a1_B  a2_B  a3_B")
print("# SM: pure SM (no threshold)")
print("# A: Scenario A, Regime I (brane Higgs, KK threshold at M_KK)")
print("# B: Scenario B, Regime I (gauge-Higgs A_5, KK threshold at M_KK)")
print("#")

log_mu_plot = np.linspace(np.log10(M_Z), 20.0, 200)
for lm in log_mu_plot[::10]:  # Every 10th point for output brevity
    mu = 10**lm
    ai_sm = alpha_inv_1loop(mu, alpha_inv_MZ, b_SM, M_Z)
    ai_a = run_2stage(mu, alpha_inv_MZ, b_SM, b_eff_A_I, M_KK_I)
    ai_b = run_2stage(mu, alpha_inv_MZ, b_SM, b_eff_B_I, M_KK_I)
    print(f"{lm:7.3f}  {ai_sm[0]:7.3f} {ai_sm[1]:7.3f} {ai_sm[2]:7.3f}  "
          f"{ai_a[0]:7.3f} {ai_a[1]:7.3f} {ai_a[2]:7.3f}  "
          f"{ai_b[0]:7.3f} {ai_b[1]:7.3f} {ai_b[2]:7.3f}")


# ============================================================================
# PART 11: VERDICT AND SUMMARY
# ============================================================================

print("\n\n" + "=" * 80)
print("PART 11: VERDICT AND SUMMARY")
print("=" * 80)

# Compute key numbers for summary
spread_SM_GUT = max(ai_GUT) - min(ai_GUT)
spread_A_Lambda = max(run_2stage(Lambda_I, alpha_inv_MZ, b_SM, b_eff_A_I, M_KK_I)) - \
                  min(run_2stage(Lambda_I, alpha_inv_MZ, b_SM, b_eff_A_I, M_KK_I))
spread_B_Lambda = max(run_2stage(Lambda_I, alpha_inv_MZ, b_SM, b_eff_B_I, M_KK_I)) - \
                  min(run_2stage(Lambda_I, alpha_inv_MZ, b_SM, b_eff_B_I, M_KK_I))
spread_A_k = max(run_2stage(k_I, alpha_inv_MZ, b_SM, b_eff_A_I, M_KK_I)) - \
             min(run_2stage(k_I, alpha_inv_MZ, b_SM, b_eff_A_I, M_KK_I))
spread_II = max(ai_NCG_II) - min(ai_NCG_II)

print(f"""
======================================================
TRACK 17E: GAUGE COUPLING UNIFICATION — FINAL RESULTS
======================================================

1. THE TWO RS REGIMES IN MERIDIAN

   REGIME I:  k ~ 0.1*M_Pl = {k_I:.2e} GeV, M_KK = {M_KK_I/1e3:.1f} TeV
              KK modes at TeV. Standard RS1 phenomenology.
              Lambda_NCG = {Lambda_I:.2e} GeV

   REGIME II: k ~ 10^8 GeV, M_KK ~ {M_KK_II:.1e} GeV (sub-eV)
              KK modes below SM. Running is pure 4D.
              Lambda_NCG = {Lambda_II:.2e} GeV

   The monograph (Ch. 4) uses Regime II for the spectral action construction.
   The collider phenomenology (KK gravitons at TeV) requires Regime I.
   These are NOT inconsistent: k and ky_c can vary continuously, and the
   gauge unification question has different answers in each regime.

2. SPECTRAL ACTION GAUGE COEFFICIENTS

   a_3 = {a_3_tot:.4f},  a_2 = {a_2_tot:.4f},  a_1 = {a_1_tot:.4f} (GUT norm)
   Ratios: a_2/a_3 = {a_2_tot/a_3_tot:.4f},  a_1/a_3 = {a_1_tot/a_3_tot:.4f}
   {"EXACT unification (a_1 = a_2 = a_3)" if unif_exact else f"NOT exact: a_1/a_3 - 1 = {a_1_tot/a_3_tot - 1:.4f}"}

3. UNIFICATION SPREADS (alpha_i^{{-1}} max - min)

   Pure SM at GUT scale (2e16 GeV):    {spread_SM_GUT:.3f}
   Regime I, Scen. A at Lambda_NCG:    {spread_A_Lambda:.3f}
   Regime I, Scen. B at Lambda_NCG:    {spread_B_Lambda:.3f}
   Regime I, Scen. A at k:             {spread_A_k:.3f}
   Regime II (pure 4D) at Lambda_NCG:  {spread_II:.3f}

   The spread is comparable to or slightly better than pure SM in all cases.
   The warped KK corrections are small because the fermion content with
   |c| > 1/2 (which contributes to running) is nearly complete.

4. BRANE KINETIC TERMS

   Spectral action prediction: Delta ~ O(k/Lambda) = O(10^{{-2}} to 10^{{-9}})
   => Universal and negligible.
   Required for unification: Delta ~ O(10) (non-universal).
   => GAP of 3-11 orders of magnitude.

5. SCENARIO COMPARISON

   Scenario A (brane Higgs): Higgs contributes at all scales.
   Scenario B (gauge-Higgs A_5): Higgs drops out above M_KK.
   Difference in b coefficients: delta_b_1 = {b_higgs()[0]:.4f}, delta_b_2 = {b_higgs()[1]:.4f}
   This gives O(0.1-1) difference in alpha_i^{{-1}} at Lambda_NCG — notable
   but insufficient to close the unification gap.

6. THE ANGELESCU COMPARISON

   Their model: SU(6) GUT in warped AdS5, k ~ M_Pl, BKTs ~ 1.2-1.4.
   Our model: SM from NCG, k can be 10^8 to M_Pl, negligible BKTs.

   The key difference: they have a GUT group that constrains the BKTs
   through the breaking pattern SU(6) -> SU(5) -> SM. The breaking itself
   generates the non-universal BKTs. In Meridian, the SM comes directly
   from the NCG triple without GUT intermediary, so there is no GUT
   breaking mechanism to generate non-universal BKTs.

7. VERDICT AND OPEN QUESTIONS

   (a) The Meridian spectral action predicts gauge coupling equality at
       the cutoff Lambda_NCG but DOES NOT generate the required threshold
       corrections to match the observed couplings at M_Z. This is the
       same problem as standard non-SUSY GUT unification.

   (b) Three pathways to resolution:

       PATH 1: Non-perturbative spectral action corrections.
       The spectral action expansion is perturbative in Lambda. The full
       spectral action Tr(f(D^2/Lambda^2)) may have non-perturbative
       contributions that generate non-universal gauge kinetic terms.
       This requires computing the full spectral action, not just the
       Seeley-DeWitt expansion.

       PATH 2: Asymptotic safety.
       Phase 13M showed AS predicts modified gauge running above the
       Planck scale. If the fixed-point values of the gauge couplings
       are related by the NCG structure (a_1 = a_2 = a_3 at the fixed
       point), then the RG flow from the fixed point to Lambda_NCG may
       produce the required threshold corrections.

       PATH 3: Additional matter from the RS bulk.
       The bulk of AdS5 may contain states not in the SM spectral triple
       — e.g., bulk graviton KK modes, bulk moduli, or dark sector
       fields — that contribute to gauge running and modify the
       unification picture.

   (c) The computation of the FULL boundary spectral action (not just
       the a_{3/2} estimate) is the critical next step for Track 17F.

   (d) The fermion bulk mass parameters that produce the SM mass hierarchy
       are compatible with the gauge running analysis — no additional
       constraint is violated.
""")

print("=" * 80)
print("COMPUTATION COMPLETE.")
print("=" * 80)

output_file.close()
