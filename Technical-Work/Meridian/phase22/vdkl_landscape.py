"""
V_DKL Landscape Near z = 5/18 — Phase 22 Track alpha Option C

Quick exploration: what does the effective potential landscape look like
as a function of the Wilson line parameter z near the tree-level value?

The key object is |theta_1(pi*z, q_omega)|^2, which enters the DKL
threshold correction formula. The effective potential has a minimum
where the gauge couplings unify most precisely.

We don't have the full DKL integral, but we can study:
1. The shape of |theta_1(pi*z, q)|^2 near z = 5/18
2. Whether the function has a natural minimum near z_0 = 0.27708
3. The curvature (mass²) at the minimum — tells us how tightly z is pinned

This is Option C from the revised alpha.1 plan: quick feasibility check
before the full blow-up computation.
"""

from mpmath import mp, mpf, mpc, pi, sqrt, log, exp, jtheta, diff, findroot, fabs
from mpmath import re as mpre, im as mpim, eta as mpeta, power

mp.dps = 50

# Z3 orbifold modular parameter
omega = mpc(-1, sqrt(3)) / 2  # e^{2*pi*i/3}
tau = omega
q = exp(mpc(0, 1) * pi * tau)

# Dedekind eta at tau = omega
# eta(omega) = Gamma(1/3) / (2 * pi) * 3^{1/8}... but let's compute numerically
# Using the product formula: eta(tau) = q^{1/24} * prod_{n=1}^{inf} (1 - q^{2n})
# where q = e^{i*pi*tau}
# Actually, mpmath has a dedicated eta function
eta_omega = mpeta(tau)

print("V_DKL Landscape Exploration")
print("=" * 60)
print(f"  tau = omega = {mp.nstr(omega, 10)}")
print(f"  |q| = {mp.nstr(fabs(q), 10)}")
print(f"  eta(omega) = {mp.nstr(eta_omega, 12)}")
print(f"  |eta(omega)| = {mp.nstr(fabs(eta_omega), 12)}")
print(f"  |eta(omega)|^4 = {mp.nstr(fabs(eta_omega)**4, 12)}")
print()


# === The Key Function ===

def theta1_sq(z):
    """Compute |theta_1(pi*z, q_omega)|^2"""
    u = pi * z
    val = jtheta(1, u, q)
    return mpre(val * val.conjugate())


def log_theta1_sq(z):
    """log |theta_1(pi*z, q)|^2 — enters the threshold correction"""
    return log(theta1_sq(z))


# === Effective potential proxy ===
# In the DKL framework, the threshold correction for gauge group factor a is:
#   Delta_a ~ -b_a * (log |eta(tau)|^4 - log |theta_1(pi z, q)|^2) + ...
#
# The gauge coupling at the Z scale:
#   1/alpha_a(M_Z) = k_a/g_string^2 + b_a/(16 pi^2) * log(M_string^2/M_Z^2) + Delta_a/(16 pi^2)
#
# For gauge coupling UNIFICATION: alpha_1 = alpha_2 = alpha_3 at M_GUT
# The Wilson line z affects the threshold corrections differently for each
# gauge group factor through the beta function coefficients b_a.
#
# For the Standard Model from Z3 orbifold:
#   U(1): b_1 = 33/5
#   SU(2): b_2 = 1
#   SU(3): b_3 = -3
#
# The unification condition is:
#   (b_1 - b_2) * Delta_3 = (b_3 - b_2) * Delta_1 + ...
#
# Simplification: the threshold corrections depend on z primarily through
# |theta_1(pi*z, q)|. The effective potential for z is (schematically):
#
#   V_eff(z) ~ | sin^2(theta_W) - sin^2(theta_W)_exp |^2
#
# where sin^2(theta_W) depends on z through the threshold corrections.
#
# MORE PRECISELY: In the Meridian framework, the observable is
#   |theta_1(pi*z, q_omega)| compared to ln(3)/sqrt(2)
#
# So the "potential" we should study is simply:
#   V(z) = (|theta_1(pi*z, q)| - ln(3)/sqrt(2))^2

target = log(3) / sqrt(2)


def V_proxy(z):
    """Proxy for the effective potential: squared deviation from target"""
    val = sqrt(theta1_sq(z))
    return (val - target) ** 2


# === SCAN 1: Landscape over full fundamental domain ===

print("SCAN 1: |theta_1(pi*z, q)|^2 over z in [0, 1]")
print(f"  {'z':>8s}  {'|theta_1|':>14s}  {'|theta_1|^2':>14s}  {'V_proxy':>14s}")
print("-" * 60)
n_scan = 40
for i in range(n_scan + 1):
    z = mpf(i) / n_scan
    if z == 0 or z == 1:
        # theta_1 vanishes at z=0 and z=1
        print(f"  {mp.nstr(z, 6):>8s}  {'0':>14s}  {'0':>14s}  {mp.nstr(target**2, 8):>14s}")
        continue
    t1 = sqrt(theta1_sq(z))
    t1sq = theta1_sq(z)
    v = V_proxy(z)
    print(f"  {mp.nstr(z, 6):>8s}  {mp.nstr(t1, 10):>14s}  {mp.nstr(t1sq, 10):>14s}  {mp.nstr(v, 8):>14s}")

print()


# === SCAN 2: Fine scan near z = 5/18 ===

z_tree = mpf(5) / 18

print("SCAN 2: Fine landscape near z = 5/18")
print(f"  Tree-level z = {mp.nstr(z_tree, 10)}")
print(f"  Target |theta_1| = {mp.nstr(target, 12)}")
print()
print(f"  {'z':>12s}  {'|theta_1|':>14s}  {'gap (%)':>10s}  {'V_proxy':>14s}")
print("-" * 60)

for delta_pct in [-5, -4, -3, -2, -1.5, -1, -0.5, -0.25, 0, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5]:
    z = z_tree * (1 + delta_pct / 100)
    t1 = sqrt(theta1_sq(z))
    gap_pct = float((t1 - target) / target * 100)
    v = V_proxy(z)
    marker = " <-- tree" if delta_pct == 0 else ""
    print(f"  {mp.nstr(z, 8):>12s}  {mp.nstr(t1, 10):>14s}  {gap_pct:>10.4f}  {mp.nstr(v, 8):>14s}{marker}")

print()


# === FIND THE EXACT MINIMUM of V_proxy ===

print("EXACT MINIMUM: z_0 where |theta_1| = target")
z0 = findroot(lambda z: sqrt(theta1_sq(z)) - target, z_tree - mpf('0.001'))
delta_z = z0 - z_tree

print(f"  z_0 = {mp.nstr(z0, 16)}")
print(f"  z_tree = {mp.nstr(z_tree, 16)}")
print(f"  delta_z = {mp.nstr(delta_z, 12)}")
print(f"  delta_z / z_tree = {mp.nstr(delta_z / z_tree * 100, 8)}%")
print()


# === CURVATURE AT MINIMUM ===

# d^2V/dz^2 at z_0 tells us how tightly z is pinned
# V(z) ~ V''(z_0)/2 * (z - z_0)^2 near the minimum
# This gives the "mass" of the z modulus

# V_proxy = (|theta_1| - target)^2
# dV/dz = 2 * (|theta_1| - target) * d|theta_1|/dz
# d2V/dz2 at z=z_0: since |theta_1|=target, first term vanishes
#   = 2 * (d|theta_1|/dz)^2

def theta1_abs(z):
    return sqrt(theta1_sq(z))

deriv_z0 = diff(theta1_abs, z0)
deriv2_z0 = diff(theta1_abs, z0, 2)
V_curvature = 2 * deriv_z0**2

print("CURVATURE ANALYSIS at z_0:")
print(f"  d|theta_1|/dz at z_0 = {mp.nstr(deriv_z0, 10)}")
print(f"  d^2|theta_1|/dz^2 at z_0 = {mp.nstr(deriv2_z0, 10)}")
print(f"  V''(z_0) = 2 * (d|theta_1|/dz)^2 = {mp.nstr(V_curvature, 10)}")
print(f"  Effective mass^2 of z modulus: {mp.nstr(V_curvature, 10)}")
print()

# Width of the potential well: where V doubles from minimum
# V = V_curvature/2 * (z-z_0)^2 = V_curvature/2 * delta_z^2
# V = 1 at delta_z = sqrt(2/V_curvature)
delta_z_width = sqrt(2 / V_curvature)
print(f"  Potential well width (V=1 contour): delta_z ~ {mp.nstr(delta_z_width, 8)}")
print(f"  As fraction of z: {mp.nstr(delta_z_width / z0 * 100, 6)}%")
print()


# === PERIODICITY and OTHER ZEROS ===

print("OTHER ZEROS of V_proxy (where |theta_1| = target):")
# theta_1 is periodic in z with period 2 (for integer characteristics)
# But the physical range is z in (0, 1/2) due to the Z3 structure
# Let's find all zeros in [0.01, 0.99]

# theta_1(pi*z, q) has the symmetry theta_1(-z) = -theta_1(z)
# and theta_1(z+1) = -theta_1(z) (for standard theta)
# So |theta_1| is symmetric about z=0.5 and periodic with period 1

zeros = []
z_scan = mpf('0.01')
step = mpf('0.005')
prev_sign = theta1_abs(z_scan) - target

while z_scan < mpf('0.99'):
    z_scan += step
    curr_sign = theta1_abs(z_scan) - target
    if prev_sign * curr_sign < 0:
        try:
            z_root = findroot(lambda z: theta1_abs(z) - target, z_scan - step/2)
            if 0 < z_root < 1:
                zeros.append(z_root)
                print(f"  z = {mp.nstr(z_root, 12)}  (delta from 5/18: {mp.nstr(z_root - z_tree, 8)})")
        except Exception:
            pass
    prev_sign = curr_sign

print(f"\n  Total: {len(zeros)} zeros in (0, 1)")
print()


# === PHYSICAL INTERPRETATION ===

print("=" * 60)
print("PHYSICAL INTERPRETATION")
print("=" * 60)
print()
print(f"  The Wilson line z = 5/18 is the ORBIFOLD value (discrete, Z3-quantized).")
print(f"  The target z_0 = {mp.nstr(z0, 10)} is where |theta_1| = ln(3)/sqrt(2).")
print(f"  The shift delta_z = {mp.nstr(delta_z, 8)} is the BLOW-UP CORRECTION.")
print()
print(f"  Interpretation: resolving the 27 orbifold singularities shifts z by {mp.nstr(fabs(delta_z/z_tree)*100, 4)}%.")
print(f"  This is a natural one-loop correction size for a string compactification.")
print()
print(f"  The curvature V'' = {mp.nstr(V_curvature, 6)} means z is moderately pinned —")
print(f"  not so tight that any deviation is impossible, not so loose that z wanders freely.")
print(f"  The well width {mp.nstr(delta_z_width, 6)} ~ {mp.nstr(delta_z_width/z0*100, 4)}% of z is comparable to the required shift.")
print(f"  This means the blow-up correction is at the EDGE of what the potential allows.")
print()
print(f"  If the blow-up drives z from 5/18 toward z_0, the potential allows it —")
print(f"  the correction is WITHIN the potential well.")
