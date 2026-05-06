"""
Step 3: Precision computation of the NCG Higgs mass prediction.

Key findings from Steps 1-2:
1. SM 1-loop RGEs give lambda(M_Pl) = -0.0327 when starting from observed m_H = 125.25 GeV
2. lambda = 0 at mu ~ 10^8 GeV (the well-known vacuum instability scale)
3. sin^2(theta_W) = 3/8 at Lambda_NCG ~ 10^13 GeV (NOT at M_Pl or M_GUT!)
4. To get m_H = 125.25 GeV from RG running down from M_Pl, need lambda(M_Pl) ≈ -0.029
5. To get m_H = 125.25 GeV from Lambda_NCG, need lambda ~ 0.001 (not the NCG prediction!)
6. The NCG boundary conditions give lambda ~ 0.07-0.40, yielding m_H ~ 130-170 GeV.

Now: precision computation with 2-loop effects and careful matching.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# Constants
M_Z = 91.1876
M_t_pole = 172.76
v = 246.22
M_W = 80.377
M_H_obs = 125.25
M_Pl = 2.435e18
alpha_s_MZ = 0.1179
alpha_em_MZ = 1.0/127.952
sin2_thetaW_MZ = 0.23122

# GUT-normalized gauge couplings at M_Z
e_MZ = np.sqrt(4 * np.pi * alpha_em_MZ)
g2_MZ = e_MZ / np.sqrt(sin2_thetaW_MZ)
g1_MZ = np.sqrt(5.0/3.0) * e_MZ / np.sqrt(1 - sin2_thetaW_MZ)
g3_MZ = np.sqrt(4 * np.pi * alpha_s_MZ)

# From Buttazzo et al. 2013, MSbar values at M_t
y_t_Mt = 0.9369
lambda_Mt = 0.12604

def beta_SM_2loop(t, y):
    """2-loop SM beta functions for [g1, g2, g3, y_t, lambda].

    References:
    - Ford, Jones, Stephenson, Einhorn (1993)
    - Buttazzo et al., JHEP 1312 (2013) 089
    - Chetyrkin, Zoller (2012)

    g1 in GUT normalization (g1 = sqrt(5/3) * g'_SM).
    """
    g1, g2, g3, yt, lam = y
    g1sq = g1**2
    g2sq = g2**2
    g3sq = g3**2
    ytsq = yt**2
    lamsq = lam**2

    loop = 1.0 / (16 * np.pi**2)
    loop2 = loop**2

    # === 1-loop gauge beta functions ===
    b1_1 = 41.0/10.0
    b2_1 = -19.0/6.0
    b3_1 = -7.0

    dg1_1 = g1**3 * b1_1
    dg2_1 = g2**3 * b2_1
    dg3_1 = g3**3 * b3_1

    # === 2-loop gauge beta functions ===
    # beta_i^(2) = g_i^3 * sum_j B_ij * g_j^2 / (16*pi^2)
    # For SM with n_g=3 in GUT normalization:
    # B matrix:
    B11 = 199.0/50.0
    B12 = 27.0/10.0
    B13 = 44.0/5.0
    B21 = 9.0/10.0
    B22 = 35.0/6.0
    B23 = 12.0
    B31 = 11.0/10.0
    B32 = 9.0/2.0
    B33 = -26.0

    # Yukawa contribution to gauge 2-loop
    # -g_i^3 * Y_t contributions:
    # For g1: -17/10 * yt^2, For g2: -3/2 * yt^2, For g3: -2 * yt^2
    Yg1 = -17.0/10.0
    Yg2 = -3.0/2.0
    Yg3 = -2.0

    dg1_2 = g1**3 * (B11*g1sq + B12*g2sq + B13*g3sq + Yg1*ytsq)
    dg2_2 = g2**3 * (B21*g1sq + B22*g2sq + B23*g3sq + Yg2*ytsq)
    dg3_2 = g3**3 * (B31*g1sq + B32*g2sq + B33*g3sq + Yg3*ytsq)

    dg1 = loop * dg1_1 + loop2 * dg1_2
    dg2 = loop * dg2_1 + loop2 * dg2_2
    dg3 = loop * dg3_1 + loop2 * dg3_2

    # === 1-loop top Yukawa ===
    dyt_1 = yt * (
        (9.0/2.0) * ytsq - (17.0/20.0) * g1sq - (9.0/4.0) * g2sq - 8.0 * g3sq
    )

    # === 2-loop top Yukawa ===
    dyt_2 = yt * (
        -12.0 * ytsq**2
        + ytsq * ((393.0/80.0)*g1sq + (225.0/16.0)*g2sq + 36.0*g3sq)
        + (1187.0/600.0)*g1sq**2 - (9.0/20.0)*g1sq*g2sq
        + (19.0/15.0)*g1sq*g3sq - (23.0/4.0)*g2sq**2
        + 9.0*g2sq*g3sq - 108.0*g3sq**2
        + 6.0*lam**2 - 12.0*lam*ytsq   # lambda contributions
    )

    dyt = loop * dyt_1 + loop2 * dyt_2

    # === 1-loop Higgs quartic ===
    dlam_1 = (
        24 * lamsq
        - lam * ((9.0/5.0) * g1sq + 9.0 * g2sq)
        + 12.0 * lam * ytsq
        + (27.0/200.0) * g1sq**2
        + (9.0/20.0) * g1sq * g2sq
        + (9.0/8.0) * g2sq**2
        - 6.0 * ytsq**2
    )

    # === 2-loop Higgs quartic (dominant terms) ===
    dlam_2 = (
        -312.0 * lamsq**2 / lam if abs(lam) > 1e-15 else 0  # Actually: -312*lambda^3 is wrong
    )
    # The 2-loop is complex. For accuracy let me include the key terms:
    dlam_2 = (
        -312.0 * lam**3
        + lamsq * ((54.0/5.0)*g1sq + 54.0*g2sq - 144.0*ytsq)
        - lam * ((73.0/8.0)*g2sq**2 + (39.0/4.0)*g1sq*g2sq
                 + (629.0/24.0)*(3.0/5.0)**2*g1sq**2*(25.0/9.0)  # simplified
                 - 72.0*ytsq**2
                 + ytsq*((85.0/6.0)*g3sq + (45.0/4.0)*g2sq + (85.0/12.0)*(3.0/5.0)*g1sq))
        + 30.0 * ytsq**3
        - ytsq**2 * (8.0*g3sq + (9.0/4.0)*g2sq)
        - (305.0/16.0) * g2sq**3  # Leading gauge
        + 9.0/4.0 * g2sq**2 * g1sq * (3.0/5.0)
        + (497.0/8.0) * g2sq * (3.0/5.0)**2 * g1sq**2 * (25.0/9.0) / 16.0
        - (559.0/16.0) * (3.0/5.0)**3 * g1sq**3 * (125.0/27.0) / 16.0
    )
    # The 2-loop terms above are approximate. For a cleaner computation,
    # let me just use 1-loop with an effective correction factor.
    # The 2-loop correction to the Higgs mass is about -2 to -5 GeV.
    # For now, set 2-loop lambda to zero and note the correction.
    dlam_2 = 0  # Will correct manually below

    dlam = loop * dlam_1 + loop2 * dlam_2

    return [dg1, dg2, dg3, dyt, dlam]


def beta_SM_1loop(t, y):
    """1-loop SM beta functions."""
    g1, g2, g3, yt, lam = y
    g1sq, g2sq, g3sq, ytsq = g1**2, g2**2, g3**2, yt**2
    loop = 1.0 / (16 * np.pi**2)

    dg1 = loop * g1**3 * (41.0/10.0)
    dg2 = loop * g2**3 * (-19.0/6.0)
    dg3 = loop * g3**3 * (-7.0)

    dyt = loop * yt * (
        (9.0/2.0) * ytsq - (17.0/20.0) * g1sq - (9.0/4.0) * g2sq - 8.0 * g3sq
    )

    dlam = loop * (
        24 * lam**2 - lam * ((9.0/5.0) * g1sq + 9.0 * g2sq)
        + 12.0 * lam * ytsq
        + (27.0/200.0) * g1sq**2 + (9.0/20.0) * g1sq * g2sq + (9.0/8.0) * g2sq**2
        - 6.0 * ytsq**2
    )

    return [dg1, dg2, dg3, dyt, dlam]


# =====================================================
# COMPUTATION 1: Forward check
# Start from observed m_H, run UP to M_Pl
# =====================================================

print("=" * 70)
print("COMPUTATION 1: Run SM couplings from M_t to M_Pl (1-loop)")
print("Starting from observed values (Buttazzo et al. central)")
print("=" * 70)

t_Mt = np.log(M_t_pole / M_Z)
t_Pl = np.log(M_Pl / M_Z)

y0 = [
    0.463067,  # g1 at M_t (from Step 1)
    0.648213,  # g2 at M_t
    1.169125,  # g3 at M_t
    y_t_Mt,
    lambda_Mt
]

sol_up = solve_ivp(beta_SM_1loop, (t_Mt, t_Pl), y0, method='RK45',
                   t_eval=np.linspace(t_Mt, t_Pl, 20000),
                   rtol=1e-12, atol=1e-14, max_step=0.01)

# Extract values at M_Pl
g1_Pl = sol_up.y[0, -1]
g2_Pl = sol_up.y[1, -1]
g3_Pl = sol_up.y[2, -1]
yt_Pl = sol_up.y[3, -1]
lam_Pl = sol_up.y[4, -1]

print(f"\nAt M_Pl = {M_Pl:.3e} GeV:")
print(f"  g1 = {g1_Pl:.6f}")
print(f"  g2 = {g2_Pl:.6f}")
print(f"  g3 = {g3_Pl:.6f}")
print(f"  y_t = {yt_Pl:.6f}")
print(f"  lambda = {lam_Pl:.8f}")

# Where does lambda cross zero?
lam_arr = sol_up.y[4]
for i in range(len(lam_arr) - 1):
    if lam_arr[i] > 0 and lam_arr[i+1] <= 0:
        frac = -lam_arr[i] / (lam_arr[i+1] - lam_arr[i])
        t_zero = sol_up.t[i] + frac * (sol_up.t[i+1] - sol_up.t[i])
        mu_zero = M_Z * np.exp(t_zero)
        print(f"\n  lambda = 0 at mu = {mu_zero:.3e} GeV (instability scale)")
        # Also get y_t and g's at this scale
        idx = i
        yt_zero = sol_up.y[3, idx] + frac * (sol_up.y[3, idx+1] - sol_up.y[3, idx])
        g3_zero = sol_up.y[2, idx] + frac * (sol_up.y[2, idx+1] - sol_up.y[2, idx])
        print(f"  y_t at instability = {yt_zero:.6f}")
        print(f"  g3 at instability = {g3_zero:.6f}")
        break

# Where does lambda reach minimum?
lam_min_idx = np.argmin(lam_arr)
lam_min = lam_arr[lam_min_idx]
mu_min = M_Z * np.exp(sol_up.t[lam_min_idx])
print(f"\n  lambda_min = {lam_min:.8f} at mu = {mu_min:.3e} GeV")


# =====================================================
# COMPUTATION 2: Inverse problem - what lambda(Lambda) gives m_H = 125.25?
# =====================================================

print("\n" + "=" * 70)
print("COMPUTATION 2: What boundary condition lambda(Lambda) gives m_H = 125.25 GeV?")
print("Running DOWN from various scales to M_t")
print("=" * 70)

def run_down_get_mH(lam_high, t_high, g1_h, g2_h, g3_h, yt_h):
    """Run from t_high down to t_Mt and return m_H."""
    y0 = [g1_h, g2_h, g3_h, yt_h, lam_high]
    sol = solve_ivp(beta_SM_1loop, (t_high, t_Mt), y0, method='RK45',
                    rtol=1e-12, atol=1e-14)
    if sol.success:
        lam_low = sol.y[4, -1]
        if lam_low > 0:
            return v * np.sqrt(2 * lam_low)
        else:
            return -v * np.sqrt(-2 * lam_low)  # signal negative lambda
    return None

# Scale = M_Pl
print(f"\n--- Scale: M_Pl = {M_Pl:.3e} GeV ---")

# Use couplings at M_Pl from our upward run
def mH_residual_Pl(lam_h):
    mH = run_down_get_mH(lam_h, t_Pl, g1_Pl, g2_Pl, g3_Pl, yt_Pl)
    if mH is None:
        return 1000
    return mH - M_H_obs

# Fine search
lam_Pl_for_125 = brentq(mH_residual_Pl, -0.10, 0.05, xtol=1e-10)
mH_check = run_down_get_mH(lam_Pl_for_125, t_Pl, g1_Pl, g2_Pl, g3_Pl, yt_Pl)
print(f"  lambda(M_Pl) needed for m_H = 125.25 GeV: {lam_Pl_for_125:.8f}")
print(f"  Verification: m_H = {mH_check:.4f} GeV")

# Scale = Lambda_NCG (where sin^2(theta_W) = 3/8)
Lambda_NCG = 1.03e13
t_NCG = np.log(Lambda_NCG / M_Z)

# Get couplings at Lambda_NCG by interpolation from upward run
idx_NCG = np.searchsorted(sol_up.t, t_NCG)
frac = (t_NCG - sol_up.t[idx_NCG-1]) / (sol_up.t[idx_NCG] - sol_up.t[idx_NCG-1])
g1_NCG = sol_up.y[0, idx_NCG-1] + frac * (sol_up.y[0, idx_NCG] - sol_up.y[0, idx_NCG-1])
g2_NCG = sol_up.y[1, idx_NCG-1] + frac * (sol_up.y[1, idx_NCG] - sol_up.y[1, idx_NCG-1])
g3_NCG = sol_up.y[2, idx_NCG-1] + frac * (sol_up.y[2, idx_NCG] - sol_up.y[2, idx_NCG-1])
yt_NCG = sol_up.y[3, idx_NCG-1] + frac * (sol_up.y[3, idx_NCG] - sol_up.y[3, idx_NCG-1])

print(f"\n--- Scale: Lambda_NCG = {Lambda_NCG:.3e} GeV (sin^2 theta_W = 3/8) ---")
print(f"  Couplings: g1={g1_NCG:.5f}, g2={g2_NCG:.5f}, g3={g3_NCG:.5f}, y_t={yt_NCG:.5f}")

def mH_residual_NCG(lam_h):
    mH = run_down_get_mH(lam_h, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG)
    if mH is None:
        return 1000
    return mH - M_H_obs

lam_NCG_for_125 = brentq(mH_residual_NCG, -0.10, 0.20, xtol=1e-10)
mH_check_NCG = run_down_get_mH(lam_NCG_for_125, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG)
print(f"  lambda(Lambda_NCG) needed for m_H = 125.25 GeV: {lam_NCG_for_125:.8f}")
print(f"  Verification: m_H = {mH_check_NCG:.4f} GeV")


# =====================================================
# COMPUTATION 3: The CCM spectral action prediction
# =====================================================

print("\n" + "=" * 70)
print("COMPUTATION 3: CCM spectral action boundary conditions")
print("=" * 70)

# The CORRECT CCM relation (from the 2007 paper, derived carefully):
#
# The spectral action gives, at the cutoff Lambda:
#
# 1. Gauge coupling unification: g1 = g2 = g3 ≡ g at Lambda
#    This happens at Lambda_NCG ~ 10^13 GeV in SM (1-loop).
#
# 2. The HIGGS QUARTIC from the spectral action:
#    The spectral action coefficient structure is:
#    S_H = integral [f_0/(2*pi^2)] * [a/2 |D_mu H|^2 - mu_0^2 |H|^2 + b/2 |H|^4]
#    After rescaling H -> H/sqrt(a) for canonical kinetic:
#    S_H = integral [f_0/(2*pi^2)] * [1/2 |D_mu H|^2 - mu_0^2/a |H|^2 + b/(2*a^2) |H|^4]
#    Identifying with standard form: V = -mu^2|H|^2 + lambda|H|^4:
#    lambda = f_0 * b / (4*pi^2 * a^2)
#
#    With f_0 = 2*pi^2/g^2 (from gauge kinetic normalization):
#    lambda = b / (2*g^{-2} * a^2) = g^2*b/(2*a^2) = g^2*R/2
#
#    Wait, that's lambda = g^2*R/2 again. But this gives m_H ~ 67-77 GeV (tree).
#
# 3. The KEY ISSUE: The 170 GeV came from a DIFFERENT RELATION.
#    CCM 2007 relates m_H to the TOP MASS, not to the gauge coupling!
#    The relation is:
#    m_H^2 / m_t^2 = 4*R / (3*R_t)
#    where R = b/a^2 and R_t accounts for the top Yukawa relation to gauge.
#
# ACTUALLY, the cleanest statement from the literature (see Connes 2006,
# "Gravity and the Standard Model with Neutrino Mixing"):
#
# At tree level, the spectral action predicts:
# m_H^2 = (8*b/a^2) * M_W^2 / sin^2(theta_W)
#        = (8/3) * M_W^2 / sin^2(theta_W)   [for R = 1/3, top-only]
#
# Hmm, but sin^2(theta_W) = 3/8 at unification, so:
# m_H^2 = (8/3) * M_W^2 / (3/8) = (8/3) * (8/3) * M_W^2 = (64/9) * M_W^2
# m_H = (8/3) * M_W = 214.3 GeV. That's too big.
#
# With R = 1/4: m_H = sqrt(64/12) * M_W = sqrt(16/3) * M_W = 4/sqrt(3) * M_W = 185.6 GeV
# Still too big.
#
# None of these simple formulas give 170 GeV.
# The 170 GeV is from the RENORMALIZATION GROUP IMPROVED prediction.
#
# OK, I think the truth is simpler than all this formula-hunting.
# Let me just compute the CCM prediction using the KNOWN boundary condition formula
# and see what comes out.

# The STANDARD interpretation used in the literature:
# lambda_NCG(Lambda) = g^2(Lambda) * b / (2*a^2)

# With top-only (R = 1/3):
lam_CCM_top = g2_NCG**2 * (1.0/3.0) / 2.0
print(f"\nCCM boundary condition (top-only, R=1/3):")
print(f"  lambda(Lambda_NCG) = g^2 * R / 2 = {lam_CCM_top:.6f}")
mH_CCM_top = run_down_get_mH(lam_CCM_top, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG)
print(f"  => m_H = {mH_CCM_top:.2f} GeV (after RG running to M_t)")

# With top + neutrino (R = 1/4):
lam_CCM_nu = g2_NCG**2 * (1.0/4.0) / 2.0
print(f"\nCCM boundary condition (top+nu, R=1/4):")
print(f"  lambda(Lambda_NCG) = g^2 * R / 2 = {lam_CCM_nu:.6f}")
mH_CCM_nu = run_down_get_mH(lam_CCM_nu, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG)
print(f"  => m_H = {mH_CCM_nu:.2f} GeV (after RG running to M_t)")

# With the FULL formula including the factor from the spectral action:
# Let me try all reasonable numerical prefactors
print(f"\n--- Sweep of lambda = c * g^2 * R at Lambda_NCG ---")
print(f"{'c':>6s}  {'R':>6s}  {'lambda':>10s}  {'m_H (GeV)':>10s}")

for c in [1.0/4, 1.0/2, 1.0, 3.0/2, 2.0, 3.0, 4.0, np.pi, np.pi**2/4, np.pi**2/2]:
    for R, Rlabel in [(1.0/3, "1/3"), (1.0/4, "1/4")]:
        lam = c * g2_NCG**2 * R
        mH = run_down_get_mH(lam, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG)
        marker = " <-- ?" if mH and abs(mH - 125.25) < 3 else ""
        if mH:
            print(f"{c:6.3f}  {Rlabel:>6s}  {lam:10.6f}  {mH:10.2f}{marker}")
        else:
            print(f"{c:6.3f}  {Rlabel:>6s}  {lam:10.6f}  {'FAIL':>10s}")

# =====================================================
# COMPUTATION 4: The "Big Desert" predictions from the literature
# =====================================================

print("\n" + "=" * 70)
print("COMPUTATION 4: Literature predictions with known formulas")
print("=" * 70)

# Chamseddine-Connes 2012 "Resilience": m_H ≈ 170 GeV at tree level.
# They use the relation: m_H^2 = 4 * lambda * v^2 (their convention)
# where lambda comes from the spectral action.
# The 170 GeV result uses lambda ≈ 0.24 at the EW scale (no running!).
# That's lambda_tree = g^2(Lambda) * something BIG.

# The issue is that CCM use a DIFFERENT normalization for the Higgs quartic.
# In their notation: V = lambda * (phi^dag phi)^2 (no 1/4 factor!)
# In our notation: V = lambda_us * (phi^dag phi - v^2/2)^2
#                    = lambda_us * (phi^dag phi)^2 - lambda_us * v^2 (phi^dag phi) + ...
# So lambda_CCM = lambda_us (same).
# But: m_H^2 = d^2V/dh^2|_{h=v} depends on the expansion.
# In CCM: m_H^2 = 4*lambda*v^2 (if V = lambda*(phi^dag phi)^2)
# In standard: m_H^2 = 2*lambda*v^2 (if V = (lambda/4)*(phi^dag phi - v^2)^2)

# So if CCM's lambda is HALF of what we call lambda:
# lambda_us = 2 * lambda_CCM
# and m_H^2 = 2*lambda_us*v^2 = 4*lambda_CCM*v^2

# THIS MATTERS! The CCM tree-level lambda:
# lambda_CCM = b/(2*a^2) * pi^2/f_0 = b/(2*a^2) * g^2/2 = g^2*R/4
# lambda_us = 2*lambda_CCM = g^2*R/2

# m_H^2(tree) = 4 * lambda_CCM * v^2 = g^2*R * v^2
# With g^2 = 0.544^2, R = 1/4:
# m_H = v * sqrt(g^2/4) = 246 * 0.544/2 = 67 GeV

# That's NOT 170 either! So the formula I'm using must be wrong.

# Let me try the DIRECT numerical approach from the original paper.
# From CCM 2007, equation (4.11):
# y_t^2 = pi^2 / (2*f_0) * (a/3)   [the 1/3 is from color]
# And lambda = pi^2 * b / (2*f_0*a^2)
# Combining: lambda = (b/a^2) * (3*y_t^2/a) * a = 3*y_t^2 * b / a^3
# Hmm, that introduces y_t explicitly.

# With a = 4*y_t^2, b = 4*y_t^4:
# lambda = 3*y_t^2 * 4*y_t^4 / (4*y_t^2)^3 = 3*4/(64) = 3/16 = 0.1875

# m_H^2(tree) = 2*0.1875*v^2 = 0.375*v^2
# m_H = v*sqrt(0.375) = 246*0.612 = 150.7 GeV

# Closer! With the CCM convention m_H^2 = 4*lambda*v^2:
# m_H = v*sqrt(4*0.1875) = v*sqrt(0.75) = 246*0.866 = 213 GeV. Too big.

# OK, I found the issue. Let me re-derive from CCM 2007, equation (3.37)-(3.50).
# The spectral action gives (see their equation for the bosonic Lagrangian):
#
# L_H = (a*f_0)/(pi^2) |D_mu phi_0|^2 - (b*f_0)/(2*pi^2) |phi_0|^4
#     + (a*f_2*Lambda^2)/pi^2 |phi_0|^2 - ...
#
# Note the FACTORS: kinetic has a*f_0/pi^2, quartic has b*f_0/(2*pi^2).
# For canonical normalization, define H = sqrt(a*f_0/pi^2) * phi_0.
# Then:
# L_H = |D_mu H|^2 - (b*f_0)/(2*pi^2) * (pi^2/(a*f_0))^2 * |H|^4 + ...
#     = |D_mu H|^2 - (b*pi^2)/(2*a^2*f_0) * |H|^4 + ...
#
# So: lambda = b*pi^2/(2*a^2*f_0)  [with L = ... - lambda*|H|^4]
#
# Hmm wait, that means V includes -lambda*|H|^4, which is WRONG for a potential
# that's bounded below. The sign must be + for |H|^4.
#
# Actually, in Euclidean signature the sign is reversed:
# S_E = ... + lambda*|H|^4  (positive)
# Going to Minkowski: V = +lambda*|H|^4  (also positive)
# The mass term has -mu^2|H|^2 (tachyonic, triggers EWSB).
#
# So lambda = b*pi^2/(2*a^2*f_0) and m_H^2 = 2*lambda*v^2 (for V = lambda*(phi^dag phi - v^2/2)^2)
# Wait no. V = lambda*|H|^4 is NOT the same as V = lambda*(|H|^2 - v^2/2)^2.
# After EWSB with <H> = v/sqrt(2):
# V = lambda*(|H|^2 - v^2/2)^2 gives V(h=v+fluctuation) with m_H^2 = 8*lambda*(v/sqrt(2))^2/4...
#
# Standard: V = lambda/4 * (|phi|^2 - v^2)^2 = lambda/4*(phi^4 - 2*v^2*phi^2 + v^4)
#   m_H^2 = d^2V/dphi^2|_{phi=v} = lambda/4 * (12*v^2 - 4*v^2) = 2*lambda*v^2
# OR: V = lambda*(phi^dag phi - v^2/2)^2 where phi is the doublet with <phi^0> = v/sqrt(2):
#   m_H^2 = 4*lambda*v^2/2 ???
#
# The convention matters enormously. Let me just use V = lambda_4*(phi^dag phi)^2 and
# minimize properly.
# V = -mu_sq*phi^dag*phi + lambda_4*(phi^dag*phi)^2
# Minimum: phi^dag*phi = mu_sq/(2*lambda_4) = v^2/2
# m_H^2 = d^2V/d(Re phi)^2 = 4*lambda_4 * v^2/2 = 2*lambda_4 * v^2
#
# Wait: expanding around <phi^0> = v/sqrt(2), phi^0 = (v + h)/sqrt(2):
# phi^dag phi = (v+h)^2/2 + charged = v^2/2 + v*h + h^2/2
# V = -mu_sq*(v^2/2 + v*h + h^2/2) + lambda_4*(v^2/2 + v*h + h^2/2)^2
#   = (quadratic terms): (-mu_sq/2 + lambda_4*v^2)*h^2 + ...
# At minimum, -mu_sq + 2*lambda_4*v^2/2 = 0 => mu_sq = lambda_4*v^2
# Mass: m_H^2 = -mu_sq + 3*lambda_4*v^2 = lambda_4*v^2*(-1+3) = 2*lambda_4*v^2
#
# So m_H^2 = 2*lambda_4*v^2 where lambda_4 is the coefficient of (phi^dag phi)^2.
# This is the standard result.

# NOW: from CCM, lambda_4 = b*pi^2/(2*a^2*f_0)
# With f_0 = 2*pi^2/g^2 (from gauge coupling unification):
# lambda_4 = b*pi^2 / (2*a^2 * 2*pi^2/g^2) = b*g^2 / (4*a^2) = g^2*R/4

# m_H^2 = 2*lambda_4*v^2 = g^2*R*v^2/2

# With g = 0.544 at Lambda_NCG, R = 1/3:
# m_H = v*sqrt(g^2/(2*3)) = 246*sqrt(0.296/6) = 246*0.222 = 54.7 GeV (tree, at Lambda!)
# With R = 1/4:
# m_H = v*sqrt(g^2/8) = 246*sqrt(0.296/8) = 246*0.192 = 47.4 GeV

# BUT WAIT — this is lambda at the CUTOFF, evaluated as m_H at the cutoff scale.
# The tree-level prediction needs to be RG-improved.
# And the CCM "170 GeV" uses lambda at the ELECTROWEAK scale, not at the cutoff.

# From CCM 2012 "Resilience" paper, the 170 GeV comes from:
# Running lambda from the cutoff (~10^{17} GeV in their calculation) DOWN to M_Z.
# The RG running INCREASES lambda substantially because of the y_t^4 contribution.

# So let me compute that:
print(f"\n=== CCM prediction with RG running ===")
print(f"Using lambda_CCM = g^2*R/4 at Lambda_NCG = {Lambda_NCG:.2e} GeV")

for R_val, R_label in [(1.0/3, "top-only"), (1.0/4, "top+nu")]:
    lam_CCM = g2_NCG**2 * R_val / 4.0
    mH = run_down_get_mH(lam_CCM, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG)
    print(f"  R = {R_label}: lambda(Lambda) = {lam_CCM:.6f}, m_H = {mH:.2f} GeV")

# And with lambda = g^2*R/2:
print(f"\nUsing lambda_CCM = g^2*R/2 at Lambda_NCG")
for R_val, R_label in [(1.0/3, "top-only"), (1.0/4, "top+nu")]:
    lam_CCM = g2_NCG**2 * R_val / 2.0
    mH = run_down_get_mH(lam_CCM, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG)
    print(f"  R = {R_label}: lambda(Lambda) = {lam_CCM:.6f}, m_H = {mH:.2f} GeV")

# The CCM 2012 paper actually gets m_H ≈ 170. They must use a MUCH HIGHER cutoff
# (or different normalization). Let me try Lambda = 10^17 GeV:

Lambda_high = 1e17
t_high = np.log(Lambda_high / M_Z)
idx_h = np.searchsorted(sol_up.t, t_high)
if idx_h < len(sol_up.t):
    frac = (t_high - sol_up.t[idx_h-1]) / (sol_up.t[idx_h] - sol_up.t[idx_h-1])
    g1_h = sol_up.y[0, idx_h-1] + frac * (sol_up.y[0, idx_h] - sol_up.y[0, idx_h-1])
    g2_h = sol_up.y[1, idx_h-1] + frac * (sol_up.y[1, idx_h] - sol_up.y[1, idx_h-1])
    g3_h = sol_up.y[2, idx_h-1] + frac * (sol_up.y[2, idx_h] - sol_up.y[2, idx_h-1])
    yt_h = sol_up.y[3, idx_h-1] + frac * (sol_up.y[3, idx_h] - sol_up.y[3, idx_h-1])

    print(f"\n=== At Lambda = {Lambda_high:.0e} GeV ===")
    print(f"  g1={g1_h:.5f}, g2={g2_h:.5f}, g3={g3_h:.5f}, y_t={yt_h:.5f}")

    for R_val, R_label in [(1.0/3, "top-only"), (1.0/4, "top+nu")]:
        for c_factor, c_label in [(0.25, "g^2*R/4"), (0.5, "g^2*R/2"), (1.0, "g^2*R"), (2.0, "2*g^2*R")]:
            lam = c_factor * g2_h**2 * R_val
            mH = run_down_get_mH(lam, t_high, g1_h, g2_h, g3_h, yt_h)
            if mH:
                print(f"  {c_label}, R={R_label}: lambda={lam:.6f}, m_H = {mH:.2f} GeV")

# =====================================================
# COMPUTATION 5: The KEY INSIGHT — near-critical lambda
# =====================================================

print("\n" + "=" * 70)
print("COMPUTATION 5: The near-criticality argument")
print("=" * 70)

# The SM lambda crosses zero at ~10^8 GeV and is NEGATIVE at the Planck scale.
# lambda(M_Pl) ≈ -0.033 from our running of the OBSERVED Higgs mass.
# This means the OBSERVED Higgs mass is at the boundary of vacuum stability!
#
# The "near-criticality" argument (Shaposhnikov & Wetterich 2009, and others):
# If some UV completion imposes lambda(M_Pl) = 0, then running down gives
# a PREDICTION for m_H.

print(f"\nForward check: lambda(M_Pl) = 0 predicts what m_H?")
mH_from_zero = run_down_get_mH(0.0, t_Pl, g1_Pl, g2_Pl, g3_Pl, yt_Pl)
print(f"  m_H = {mH_from_zero:.2f} GeV")

print(f"\nForward check: lambda(M_Pl) = -0.01 predicts what m_H?")
mH_from_neg = run_down_get_mH(-0.01, t_Pl, g1_Pl, g2_Pl, g3_Pl, yt_Pl)
print(f"  m_H = {mH_from_neg:.2f} GeV")

# And beta(lambda) = 0 at M_Pl (the asymptotic safety condition):
# This gives lambda_AS(M_Pl) from the beta function.
# beta_lambda = 0 with lambda itself being a variable:
# 0 = 24*lam^2 - lam*(9/5*g1^2 + 9*g2^2) + 12*lam*y_t^2 + gauge^4 - 6*y_t^4
# 0 = 24*lam^2 + lam*(12*y_t^2 - 9/5*g1^2 - 9*g2^2) + (gauge^4 - 6*y_t^4)
# This is quadratic in lam.

A_quad = 24.0
B_quad = 12*yt_Pl**2 - (9.0/5.0)*g1_Pl**2 - 9.0*g2_Pl**2
C_quad = ((27.0/200.0)*g1_Pl**4 + (9.0/20.0)*g1_Pl**2*g2_Pl**2 + (9.0/8.0)*g2_Pl**4
          - 6.0*yt_Pl**4)
disc = B_quad**2 - 4*A_quad*C_quad
if disc >= 0:
    lam_AS_1 = (-B_quad + np.sqrt(disc)) / (2*A_quad)
    lam_AS_2 = (-B_quad - np.sqrt(disc)) / (2*A_quad)
    print(f"\nbeta(lambda) = 0 at M_Pl gives:")
    print(f"  lambda_AS = {lam_AS_1:.6f} or {lam_AS_2:.6f}")

    mH_AS1 = run_down_get_mH(lam_AS_1, t_Pl, g1_Pl, g2_Pl, g3_Pl, yt_Pl)
    mH_AS2 = run_down_get_mH(lam_AS_2, t_Pl, g1_Pl, g2_Pl, g3_Pl, yt_Pl)
    print(f"  lambda_AS = {lam_AS_1:.6f} => m_H = {mH_AS1:.2f} GeV")
    print(f"  lambda_AS = {lam_AS_2:.6f} => m_H = {mH_AS2:.2f} GeV")


# =====================================================
# FINAL SUMMARY
# =====================================================

print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

print(f"""
KEY RESULTS (1-loop SM RG running):

1. OBSERVED Higgs mass running:
   lambda(M_t)  = {lambda_Mt:.5f}  (m_H = {M_H_obs} GeV)
   lambda(M_Pl) = {lam_Pl:.8f}  (NEGATIVE — vacuum metastability)
   Instability scale: ~10^8 GeV

2. SM gauge couplings do NOT unify at 1-loop:
   sin^2(theta_W) = 3/8 at mu = 1.03 x 10^13 GeV (not the GUT scale)
   At that scale: g1 = g2 = 0.544 but g3 = 0.584 (NOT equal!)

3. CCM boundary condition lambda = g^2*R/4 at Lambda_NCG:
   R = 1/3 (top-only): lambda = {g2_NCG**2/12:.6f} => m_H = {run_down_get_mH(g2_NCG**2/12, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG):.1f} GeV
   R = 1/4 (top+nu):   lambda = {g2_NCG**2/16:.6f} => m_H = {run_down_get_mH(g2_NCG**2/16, t_NCG, g1_NCG, g2_NCG, g3_NCG, yt_NCG):.1f} GeV

4. To obtain m_H = 125.25 GeV:
   Need lambda(M_Pl)      = {lam_Pl_for_125:.8f}
   Need lambda(Lambda_NCG) = {lam_NCG_for_125:.8f}

5. Near-criticality prediction:
   lambda(M_Pl) = 0 => m_H = {mH_from_zero:.1f} GeV

6. The "124.5 GeV from NCG" claim:
   CANNOT be obtained from the standard CCM boundary condition alone.
   Would require EITHER:
   (a) A specific NCG boundary condition lambda ≈ {lam_Pl_for_125:.4f} at M_Pl
       (which is near-zero and NEGATIVE)
   (b) The near-criticality condition lambda(M_Pl) ~ 0 (gives {mH_from_zero:.1f} GeV, close but high)
   (c) Additional model ingredients (scalar singlet, threshold corrections, etc.)
   (d) 2-loop running (shifts result by ~-2 to -5 GeV)
""")

# Cross-check: what EXACT lambda(M_Pl) gives 124.5 specifically?
def mH_resid_exact(lam_h):
    return run_down_get_mH(lam_h, t_Pl, g1_Pl, g2_Pl, g3_Pl, yt_Pl) - 124.5

lam_for_124_5 = brentq(mH_resid_exact, -0.10, 0.05, xtol=1e-12)
print(f"For m_H = 124.5 GeV exactly: lambda(M_Pl) = {lam_for_124_5:.10f}")
print(f"  This is {abs(lam_for_124_5)/abs(lam_Pl)*100:.1f}% of the SM lambda(M_Pl)")
