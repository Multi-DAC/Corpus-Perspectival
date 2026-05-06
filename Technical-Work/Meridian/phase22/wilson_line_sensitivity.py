"""
Wilson Line Sensitivity Analysis — Phase 22 Track alpha prep

Computes the sensitivity of |theta_1(pi*z, q_omega)| to z near z = 5/18.
This determines:
1. How precisely z must be known to close the 0.18% gap
2. Whether a perturbative (small delta_z) approach is viable
3. The exact z_0 where |theta_1| = ln(3)/sqrt(2)

Uses mpmath's jtheta for high-precision theta function evaluation.
"""

from mpmath import mp, mpf, mpc, pi, sqrt, log, exp, jtheta, diff, findroot, fabs

mp.dps = 50

# Z3 orbifold modular parameter
omega = mpc(-1, sqrt(3)) / 2  # e^{2*pi*i/3} = -1/2 + sqrt(3)/2 * i
tau = omega

# Nome q = e^{i*pi*tau}
q = exp(mpc(0, 1) * pi * tau)

print("Wilson Line Sensitivity Analysis")
print("=" * 60)
print(f"  tau = omega = {mp.nstr(tau, 10)}")
print(f"  q = e^(i*pi*tau) = {mp.nstr(q, 10)}")
print(f"  |q| = {mp.nstr(fabs(q), 10)}")
print()

# Target values
z_tree = mpf(5) / 18
target = log(3) / sqrt(2)

print(f"  Tree-level Wilson line: z = 5/18 = {mp.nstr(z_tree, 10)}")
print(f"  Target: ln(3)/sqrt(2) = {mp.nstr(target, 12)}")
print()


# === STEP 1: theta_1 at tree-level z ===

def theta1_abs(z):
    """Compute |theta_1(pi*z, q_omega)|"""
    u = pi * z
    return fabs(jtheta(1, u, q))


val_tree = theta1_abs(z_tree)
gap = val_tree - target
gap_rel = gap / target

print("STEP 1: Tree-level theta_1")
print(f"  |theta_1(pi*5/18, q_omega)| = {mp.nstr(val_tree, 14)}")
print(f"  ln(3)/sqrt(2)               = {mp.nstr(target, 14)}")
print(f"  Gap (absolute):  {mp.nstr(gap, 10)}")
print(f"  Gap (relative):  {mp.nstr(gap_rel * 100, 6)}%")
print()


# === STEP 2: Derivative at tree-level z ===

def dtheta1_abs_dz(z):
    """Numerical derivative of |theta_1(pi*z, q)| with respect to z"""
    return diff(theta1_abs, z)


deriv_tree = dtheta1_abs_dz(z_tree)
deriv2_tree = diff(theta1_abs, z_tree, 2)

print("STEP 2: Sensitivity at z = 5/18")
print(f"  d/dz |theta_1| at z=5/18:   {mp.nstr(deriv_tree, 12)}")
print(f"  d^2/dz^2 |theta_1| at z=5/18: {mp.nstr(deriv2_tree, 10)}")
print()

# Linear estimate of required delta_z
delta_z_linear = -gap / deriv_tree
print(f"  Linear estimate: delta_z = -gap / deriv = {mp.nstr(delta_z_linear, 10)}")
print(f"  z_0 (linear est.) = 5/18 + delta_z = {mp.nstr(z_tree + delta_z_linear, 12)}")
print()


# === STEP 3: Exact z_0 by root-finding ===

print("STEP 3: Exact z_0 (numerical root-finding)")
z0 = findroot(lambda z: theta1_abs(z) - target, z_tree + delta_z_linear)
delta_z_exact = z0 - z_tree

print(f"  z_0 (exact) = {mp.nstr(z0, 14)}")
print(f"  delta_z = z_0 - 5/18 = {mp.nstr(delta_z_exact, 12)}")
print(f"  delta_z / z_tree = {mp.nstr(delta_z_exact / z_tree * 100, 8)}%")
print()

# Verify
val_z0 = theta1_abs(z0)
print(f"  Verification: |theta_1(pi*z_0, q)| = {mp.nstr(val_z0, 14)}")
print(f"  Target:                               {mp.nstr(target, 14)}")
print(f"  Match: {mp.nstr(fabs(val_z0 - target), 6)}")
print()


# === STEP 4: Sensitivity landscape ===

print("STEP 4: Sensitivity landscape near z = 5/18")
print(f"  {'z':>14s}  {'|theta_1|':>16s}  {'|theta_1| - target':>20s}  {'rel gap %':>10s}")
for dz_pct in [-2.0, -1.5, -1.0, -0.5, -0.25, 0.0, 0.25, 0.5, 1.0]:
    z = z_tree * (1 + dz_pct / 100)
    val = theta1_abs(z)
    rel = (val - target) / target * 100
    print(f"  {mp.nstr(z, 10):>14s}  {mp.nstr(val, 12):>16s}  {mp.nstr(val - target, 10):>20s}  {mp.nstr(rel, 6):>10s}%")
print()


# === STEP 5: Required precision ===

print("STEP 5: Required precision to close the gap")
print(f"  |delta_z| = {mp.nstr(fabs(delta_z_exact), 8)}")
print(f"  |delta_z/z| = {mp.nstr(fabs(delta_z_exact/z_tree), 8)}")
print(f"  This is a {mp.nstr(fabs(delta_z_exact/z_tree)*100, 4)}% correction to z")
print()

# How many digits of z do we need?
import math
digits_needed = -math.log10(float(fabs(delta_z_exact)))
print(f"  Digits of z needed: ~{digits_needed:.1f}")
print(f"  (z must be known to {digits_needed:.0f} significant figures to distinguish z_0 from 5/18)")
print()


# === STEP 6: Perturbative viability assessment ===

print("STEP 6: Perturbative viability")
print("=" * 60)
print(f"  Tree-level z = 5/18 = {mp.nstr(z_tree, 10)}")
print(f"  Required z_0 = {mp.nstr(z0, 10)}")
print(f"  Shift delta_z = {mp.nstr(delta_z_exact, 10)}")
print(f"  Relative shift = {mp.nstr(fabs(delta_z_exact/z_tree)*100, 6)}%")
print()
print("  ASSESSMENT:")
print(f"  delta_z ~ {mp.nstr(fabs(delta_z_exact), 4)} is a {'SMALL' if fabs(delta_z_exact) < 0.01 else 'LARGE'} correction.")
if fabs(delta_z_exact) < 0.01:
    print("  -> Perturbative approach IS viable.")
    print("  -> One-loop Kahler potential correction could produce this shift.")
    print("  -> Full Donaldson balanced metric may not be needed!")
else:
    print("  -> Perturbative approach may NOT be viable.")
    print("  -> Full non-perturbative computation (Donaldson) likely needed.")
print()
print("  For Track alpha: the derivative d|theta_1|/dz tells us how sensitive")
print("  the observable is to the Wilson line. A large derivative means small")
print("  delta_z is needed (good for perturbation theory). A small derivative")
print("  means large delta_z (bad — need full non-perturbative computation).")
print(f"  Derivative = {mp.nstr(deriv_tree, 8)}")
print(f"  This is {'large' if fabs(deriv_tree) > 1 else 'small'} — the theta function is {'sensitive' if fabs(deriv_tree) > 1 else 'insensitive'} to z near 5/18.")
