"""
Step 1: SM RG running of gauge couplings and top Yukawa from M_Z to M_Pl.
1-loop RGEs for the Standard Model.

References:
- Machacek & Vaughn, Nucl. Phys. B222 (1983) 83; B236 (1984) 221; B249 (1985) 70
- Arason et al., Phys. Rev. D46 (1992) 3945
- Buttazzo et al., JHEP 1312 (2013) 089 [arXiv:1307.3536]
"""

import numpy as np
from scipy.integrate import solve_ivp
import json

# Physical constants
M_Z = 91.1876  # GeV
M_t_pole = 172.76  # GeV (top pole mass)
v = 246.22  # GeV (Higgs vev)
M_W = 80.377  # GeV
M_H = 125.25  # GeV (observed)
M_Pl = 2.435e18  # GeV (reduced Planck mass)
alpha_s_MZ = 0.1179  # strong coupling at M_Z
alpha_em_MZ = 1.0 / 127.952  # EM coupling at M_Z
sin2_thetaW_MZ = 0.23122  # weak mixing angle at M_Z

# Derive gauge couplings at M_Z in GUT normalization
# g1 is in GUT normalization: g1_GUT = sqrt(5/3) * g1_SM = sqrt(5/3) * e/cos(theta_W)
# g2 = e / sin(theta_W)
# g3 from alpha_s

e_MZ = np.sqrt(4 * np.pi * alpha_em_MZ)
g2_MZ = e_MZ / np.sqrt(sin2_thetaW_MZ)
g1_SM_MZ = e_MZ / np.sqrt(1 - sin2_thetaW_MZ)
g1_MZ = np.sqrt(5.0/3.0) * g1_SM_MZ  # GUT normalization
g3_MZ = np.sqrt(4 * np.pi * alpha_s_MZ)

print("=== Initial conditions at M_Z ===")
print(f"g1(M_Z) [GUT norm] = {g1_MZ:.6f}")
print(f"g2(M_Z)            = {g2_MZ:.6f}")
print(f"g3(M_Z)            = {g3_MZ:.6f}")
print(f"alpha_1 = {g1_MZ**2/(4*np.pi):.6f}")
print(f"alpha_2 = {g2_MZ**2/(4*np.pi):.6f}")
print(f"alpha_3 = {g3_MZ**2/(4*np.pi):.6f}")

# Top Yukawa at M_t (we'll use M_t for the starting value, then run from M_Z)
# y_t(M_t) = sqrt(2) * m_t / v
# But m_t(pole) != m_t(running). The MS-bar mass at M_t is approximately:
# m_t_MSbar(M_t) ≈ M_t_pole * (1 - 4/(3*pi) * alpha_s(M_t) - ...)
# For 1-loop: m_t_MSbar ≈ 172.76 * (1 - 4*alpha_s/(3*pi)) ≈ 163.5 GeV
# But let's use the standard approach: start at M_Z with the MS-bar value.

# Actually, standard approach: define y_t at M_t from the pole mass with QCD correction
alpha_s_Mt = 0.1079  # alpha_s at M_t (well-known value)
m_t_MSbar = M_t_pole * (1 - (4.0/3.0) * alpha_s_Mt / np.pi)
y_t_Mt = np.sqrt(2) * m_t_MSbar / v
print(f"\nm_t(MSbar at M_t) = {m_t_MSbar:.4f} GeV")
print(f"y_t(M_t)          = {y_t_Mt:.6f}")

# Higgs quartic at M_Z from observed Higgs mass
# m_H^2 = 2 * lambda * v^2
lambda_MZ = M_H**2 / (2 * v**2)
print(f"lambda(M_Z)        = {lambda_MZ:.6f}")
print(f"  (from m_H = {M_H} GeV)")

# We'll run RGEs from M_Z to M_Pl
# Using 1-loop SM beta functions with n_g = 3 generations

# SM 1-loop beta functions
# Variables: y = [g1, g2, g3, y_t, lambda]
# t = ln(mu/M_Z)

def beta_SM_1loop(t, y):
    g1, g2, g3, yt, lam = y

    # Shorthand
    g1sq = g1**2
    g2sq = g2**2
    g3sq = g3**2
    ytsq = yt**2

    # 1-loop beta coefficients for gauge couplings
    # With n_g = 3, n_H = 1 (one Higgs doublet)
    # b_i = (b_i^gauge + b_i^Yukawa + b_i^scalar)
    # In GUT normalization for g1:
    # b1 = 41/10, b2 = -19/6, b3 = -7
    b1 = 41.0/10.0
    b2 = -19.0/6.0
    b3 = -7.0

    dg1 = g1**3 * b1 / (16 * np.pi**2)
    dg2 = g2**3 * b2 / (16 * np.pi**2)
    dg3 = g3**3 * b3 / (16 * np.pi**2)

    # Top Yukawa beta function (1-loop)
    # beta_yt = yt/(16*pi^2) * [9/2 yt^2 - (17/20 g1^2 + 9/4 g2^2 + 8 g3^2)]
    # Note: 17/20 in GUT normalization (= 17/12 * 3/5 for g1_GUT)
    # Actually let me be careful. With GUT-normalized g1:
    # The hypercharge contribution is (17/20)*g1_GUT^2
    # Check: in SM normalization, it's (17/12)*g1_SM^2 = (17/12)*(3/5)*g1_GUT^2 = (17/20)*g1_GUT^2 ✓

    dyt = yt / (16 * np.pi**2) * (
        (9.0/2.0) * ytsq
        - (17.0/20.0) * g1sq
        - (9.0/4.0) * g2sq
        - 8.0 * g3sq
    )

    # Higgs quartic beta function (1-loop)
    # beta_lambda = 1/(16*pi^2) * [
    #   24*lambda^2
    #   - lambda*(9/5 g1^2 + 9 g2^2) + 12*lambda*yt^2
    #   + 27/200 g1^4 + 9/20 g1^2*g2^2 + 9/8 g2^4
    #   - 6*yt^4
    # ]
    # Note: with GUT normalization g1, the 3/5 factors change the coefficients
    # In GUT normalization:
    #   3*g1_SM^2 = 3*(3/5)*g1_GUT^2 = (9/5)*g1_GUT^2
    #   g1_SM^4 = (3/5)^2 * g1_GUT^4 = (9/25)*g1_GUT^4
    #   g1_SM^2 * g2^2 = (3/5)*g1_GUT^2 * g2^2

    dlam = 1.0 / (16 * np.pi**2) * (
        24 * lam**2
        - lam * ((9.0/5.0) * g1sq + 9.0 * g2sq)
        + 12.0 * lam * ytsq
        + (27.0/200.0) * g1sq**2
        + (9.0/20.0) * g1sq * g2sq
        + (9.0/8.0) * g2sq**2
        - 6.0 * ytsq**2
    )

    return [dg1, dg2, dg3, dyt, dlam]

# Initial conditions at M_Z
# For y_t at M_Z, we need to run from M_t down to M_Z first, or use known value
# The standard value: y_t(M_Z) ≈ 0.9399 in MSbar (from Buttazzo et al.)
# Let me compute it by running from M_t to M_Z first (downward)

# Actually, let's just start from M_t and do a quick run down to M_Z to get y_t(M_Z)
# But for simplicity and to use standard values, let me use:
# y_t(M_t) from above, and run gauge couplings to M_t first

# Simpler approach: use known MSbar values at M_t as cross-check
# From Buttazzo et al. 2013 (Table 1):
# y_t(M_t) = 0.9369 ± 0.0034 (for m_t = 173.1, alpha_s = 0.1184)
# lambda(M_t) = 0.12604 ± 0.00018

# Let me use two approaches:
# A) Start at M_Z with alpha values, run everything to M_Pl
# B) Start at M_t with Buttazzo values, run to M_Pl

# Approach A: from M_Z
t_MZ = 0  # ln(M_Z/M_Z) = 0
t_Mt = np.log(M_t_pole / M_Z)
t_MPl = np.log(M_Pl / M_Z)

print(f"\nt(M_t)  = ln(M_t/M_Z) = {t_Mt:.4f}")
print(f"t(M_Pl) = ln(M_Pl/M_Z) = {t_MPl:.4f}")

# For y_t at M_Z: we need to account for threshold at M_t
# Below M_t, the top is integrated out. But for SM running WITH the top,
# the convention is to use 6-flavor running all the way.
# Standard approach: match at M_t.

# Let's use Buttazzo et al. central values at M_t as our starting point:
# This is the most reliable approach.
y_t_start = 0.9369  # Buttazzo et al. at M_t (MSbar, 6-flavor SM)
lambda_start = 0.12604

# Gauge couplings at M_t (run from M_Z with 1-loop)
# Quick analytic 1-loop running:
def g_1loop(g_MZ, b, t):
    """1-loop running of gauge coupling"""
    return g_MZ / np.sqrt(1 - b * g_MZ**2 * t / (8 * np.pi**2))

g1_Mt = g_1loop(g1_MZ, 41.0/10.0, t_Mt)
g2_Mt = g_1loop(g2_MZ, -19.0/6.0, t_Mt)
g3_Mt = g_1loop(g3_MZ, -7.0, t_Mt)

print(f"\n=== Gauge couplings at M_t (1-loop from M_Z) ===")
print(f"g1(M_t) = {g1_Mt:.6f}")
print(f"g2(M_t) = {g2_Mt:.6f}")
print(f"g3(M_t) = {g3_Mt:.6f}")
print(f"alpha_s(M_t) = {g3_Mt**2/(4*np.pi):.6f}")

# Now run from M_t to M_Pl
y0 = [g1_Mt, g2_Mt, g3_Mt, y_t_start, lambda_start]
t_span = (t_Mt, t_MPl)
t_eval = np.linspace(t_Mt, t_MPl, 10000)

sol = solve_ivp(beta_SM_1loop, t_span, y0, method='RK45', t_eval=t_eval,
                rtol=1e-10, atol=1e-12, max_step=0.1)

print(f"\n=== Results at M_Pl ===")
g1_Pl = sol.y[0, -1]
g2_Pl = sol.y[1, -1]
g3_Pl = sol.y[2, -1]
yt_Pl = sol.y[3, -1]
lam_Pl = sol.y[4, -1]

print(f"g1(M_Pl) = {g1_Pl:.6f}")
print(f"g2(M_Pl) = {g2_Pl:.6f}")
print(f"g3(M_Pl) = {g3_Pl:.6f}")
print(f"y_t(M_Pl) = {yt_Pl:.6f}")
print(f"lambda(M_Pl) = {lam_Pl:.8f}")

print(f"\nalpha_1(M_Pl) = {g1_Pl**2/(4*np.pi):.6f}")
print(f"alpha_2(M_Pl) = {g2_Pl**2/(4*np.pi):.6f}")
print(f"alpha_3(M_Pl) = {g3_Pl**2/(4*np.pi):.6f}")

# Check: sin^2(theta_W) at M_Pl
# sin^2(theta_W) = g1_SM^2 / (g1_SM^2 + g2^2) = (3/5)*g1_GUT^2 / ((3/5)*g1_GUT^2 + g2^2)
g1_SM_Pl = np.sqrt(3.0/5.0) * g1_Pl
sin2_thetaW_Pl = g1_SM_Pl**2 / (g1_SM_Pl**2 + g2_Pl**2)
print(f"\nsin^2(theta_W) at M_Pl = {sin2_thetaW_Pl:.6f}")
print(f"  (NCG predicts 3/8 = {3/8:.6f} at unification)")

# Find the scale where sin^2(theta_W) = 3/8
# This happens when (3/5)*g1^2 = g2^2, i.e., g1_GUT = sqrt(5/3) * g2
# Which means alpha_1 = alpha_2 (in GUT normalization)
# Let's find this scale

g1_arr = sol.y[0]
g2_arr = sol.y[1]
sin2_arr = (3.0/5.0) * g1_arr**2 / ((3.0/5.0) * g1_arr**2 + g2_arr**2)
target = 3.0/8.0

# Find crossing
for i in range(len(sin2_arr)-1):
    if sin2_arr[i] < target and sin2_arr[i+1] >= target:
        # Linear interpolation
        frac = (target - sin2_arr[i]) / (sin2_arr[i+1] - sin2_arr[i])
        t_cross = sol.t[i] + frac * (sol.t[i+1] - sol.t[i])
        mu_cross = M_Z * np.exp(t_cross)
        print(f"\nsin^2(theta_W) = 3/8 at mu = {mu_cross:.3e} GeV")
        print(f"  ln(mu/M_Z) = {t_cross:.4f}")

        # Interpolate couplings at this scale
        g1_cross = g1_arr[i] + frac * (g1_arr[i+1] - g1_arr[i])
        g2_cross = g2_arr[i] + frac * (g2_arr[i+1] - g2_arr[i])
        g3_cross = sol.y[2, i] + frac * (sol.y[2, i+1] - sol.y[2, i])
        yt_cross = sol.y[3, i] + frac * (sol.y[3, i+1] - sol.y[3, i])
        lam_cross = sol.y[4, i] + frac * (sol.y[4, i+1] - sol.y[4, i])
        print(f"  g1 = {g1_cross:.6f}, g2 = {g2_cross:.6f}, g3 = {g3_cross:.6f}")
        print(f"  y_t = {yt_cross:.6f}")
        print(f"  lambda = {lam_cross:.8f}")
        break
else:
    print("\nsin^2(theta_W) never reaches 3/8 (couplings don't unify at 1-loop)")
    # Check the maximum
    print(f"  max sin^2(theta_W) = {np.max(sin2_arr):.6f}")

# Also check: where does lambda cross zero? (vacuum stability)
lam_arr = sol.y[4]
for i in range(len(lam_arr)-1):
    if lam_arr[i] > 0 and lam_arr[i+1] <= 0:
        frac = -lam_arr[i] / (lam_arr[i+1] - lam_arr[i])
        t_zero = sol.t[i] + frac * (sol.t[i+1] - sol.t[i])
        mu_zero = M_Z * np.exp(t_zero)
        print(f"\nlambda = 0 (instability scale) at mu = {mu_zero:.3e} GeV")
        print(f"  ln(mu/M_Z) = {t_zero:.4f}")
        break
else:
    print(f"\nlambda never crosses zero (min = {np.min(lam_arr):.8f})")

# Print key intermediate values
checkpoints = [1e3, 1e6, 1e9, 1e12, 1e15, 1e18]
print(f"\n=== Running couplings at key scales ===")
print(f"{'Scale (GeV)':>12s}  {'g1':>8s}  {'g2':>8s}  {'g3':>8s}  {'y_t':>8s}  {'lambda':>10s}  {'sin2tW':>8s}")
for mu in checkpoints:
    t_target = np.log(mu / M_Z)
    if t_target < sol.t[0] or t_target > sol.t[-1]:
        continue
    idx = np.searchsorted(sol.t, t_target)
    if idx >= len(sol.t):
        idx = len(sol.t) - 1
    frac = (t_target - sol.t[idx-1]) / (sol.t[idx] - sol.t[idx-1]) if idx > 0 else 0
    vals = [sol.y[j, idx-1] + frac * (sol.y[j, idx] - sol.y[j, idx-1]) for j in range(5)]
    g1v, g2v, g3v, ytv, lamv = vals
    s2tw = (3/5)*g1v**2 / ((3/5)*g1v**2 + g2v**2)
    print(f"{mu:12.0e}  {g1v:8.5f}  {g2v:8.5f}  {g3v:8.5f}  {ytv:8.5f}  {lamv:10.7f}  {s2tw:8.5f}")

# Save results for next step
results = {
    'g1_MZ': g1_MZ, 'g2_MZ': g2_MZ, 'g3_MZ': g3_MZ,
    'g1_MPl': float(g1_Pl), 'g2_MPl': float(g2_Pl), 'g3_MPl': float(g3_Pl),
    'yt_MPl': float(yt_Pl), 'lambda_MPl': float(lam_Pl),
    'yt_Mt': y_t_start, 'lambda_Mt': lambda_start,
    'sin2_thetaW_MPl': float(sin2_thetaW_Pl),
}
print(f"\n=== Summary for Step 2 ===")
print(json.dumps(results, indent=2))
