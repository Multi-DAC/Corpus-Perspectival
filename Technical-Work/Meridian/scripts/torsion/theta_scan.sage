"""
Theta Function Scan: Find the Wilson line shift z_0 where
|theta_1(z_0 | omega)| = ln(3)/sqrt(2)

If z_0 has a nice closed form, it supports the conjecture.
"""

from sage.all import *

R = RealField(200)
C = ComplexField(200)

pi_val = R(pi)
omega = C(exp(2 * pi * I / 3))
target = R(ln(R(3))) / R(sqrt(R(2)))

print(f"Target: ln(3)/sqrt(2) = {float(target):.15f}")
print(f"|theta_1(5/18|omega)| = 0.778241706886285")
print(f"Gap: {float(abs(R(0.778241706886285) - target)/target * 100):.4f}%")
print()

# Precompute q
q = C(exp(2 * pi * I * omega))

def theta1_abs(z):
    """Compute |theta_1(z | omega)| for real z."""
    z_r = R(z)
    result = C(0)
    for n in range(300):
        sign = (-1)^n
        q_pow = (n + R(1)/R(2))^2 / R(2)
        s_arg = (2*n + 1) * pi_val * z_r
        result += C(sign) * q^q_pow * C(sin(s_arg))
    return abs(2 * result)

# Binary search for z_0 where |theta_1(z_0|omega)| = ln(3)/sqrt(2)
print("Binary search for z_0 where |theta_1(z_0 | omega)| = target...")
print()

# theta_1 is odd and periodic. On (0, 1/2) it first increases then decreases.
# At z = 5/18 ~ 0.2778, we got 0.7782 which is ABOVE target 0.7768.
# Since theta_1 is increasing at z = 5/18 (still before the max),
# we need a slightly SMALLER z.

# Actually, let me first map out the theta_1 profile
print("Profile of |theta_1(z | omega)| near z = 5/18:")
print(f"{'z':>12} {'|theta_1|':>18} {'vs target':>12}")
print("-" * 45)

for z_num in [0.20, 0.22, 0.24, 0.25, 0.26, 0.27, 0.2750, 0.2770, 0.2778, 0.28, 0.29, 0.30, 0.32, 0.34, 0.36, 0.38, 0.40, 0.42, 0.44, 0.46, 0.48, 0.50]:
    val = theta1_abs(z_num)
    diff_pct = float((val - target) / target * 100)
    marker = " <-- 5/18" if abs(z_num - 5/18) < 0.0001 else ""
    print(f"{z_num:>12.6f} {float(val):>18.15f} {diff_pct:>+11.4f}%{marker}")

print()

# Find both roots (one below and one above 1/4)
# theta_1 reaches max around z = 1/4 on this lattice

# Search in the range below the maximum
z_lo = R(0.15)
z_hi = R(0.50)

# First find maximum
z_max = R(0.25)
for _ in range(50):
    z_a = z_max - R(0.0001)
    z_b = z_max + R(0.0001)
    if theta1_abs(z_a) < theta1_abs(z_b):
        z_max += R(0.00005)
    else:
        z_max -= R(0.00005)

val_max = theta1_abs(z_max)
print(f"Maximum of |theta_1| at z ≈ {float(z_max):.6f}, value = {float(val_max):.15f}")

if val_max < target:
    print(f"WARNING: Maximum {float(val_max)} is below target {float(target)}!")
    print("No solution exists on this interval.")
else:
    print(f"Maximum exceeds target by {float((val_max - target)/target*100):.4f}%")

print()

# Find z_0 on the LEFT branch (z < z_max) where |theta_1| = target
# Binary search
z_lo_l = R(0.15)
z_hi_l = z_max

for _ in range(100):
    z_mid = (z_lo_l + z_hi_l) / R(2)
    val = theta1_abs(z_mid)
    if val < target:
        z_lo_l = z_mid
    else:
        z_hi_l = z_mid

z0_left = (z_lo_l + z_hi_l) / R(2)
val_left = theta1_abs(z0_left)
print(f"Left root:  z_0 = {float(z0_left):.15f}")
print(f"            |theta_1(z_0|omega)| = {float(val_left):.15f}")
print(f"            Error: {float(abs(val_left - target)/target):.2e}")

# Find z_0 on the RIGHT branch (z > z_max)
z_lo_r = z_max
z_hi_r = R(0.50)

for _ in range(100):
    z_mid = (z_lo_r + z_hi_r) / R(2)
    val = theta1_abs(z_mid)
    if val < target:
        z_hi_r = z_mid
    else:
        z_lo_r = z_mid

z0_right = (z_lo_r + z_hi_r) / R(2)
val_right = theta1_abs(z0_right)
print(f"\nRight root: z_0 = {float(z0_right):.15f}")
print(f"            |theta_1(z_0|omega)| = {float(val_right):.15f}")
print(f"            Error: {float(abs(val_right - target)/target):.2e}")

# ============================================================
# Check if z_0 has a nice closed form
# ============================================================
print(f"\n{'='*60}")
print("ANALYSIS: Does z_0 have a nice form?")
print(f"{'='*60}")

z0 = z0_left  # The one near 5/18

print(f"\nz_0 = {float(z0):.15f}")
print(f"5/18 = {float(R(5)/R(18)):.15f}")
print(f"Difference: z_0 - 5/18 = {float(z0 - R(5)/R(18)):.15e}")
print()

# Check various nice fractions near z_0
print("Nearby nice fractions:")
for p in range(1, 30):
    for q_frac in range(p+1, 100):
        frac = R(p) / R(q_frac)
        if abs(frac - z0) < R(0.005):
            val_frac = theta1_abs(frac)
            diff_pct = float((val_frac - target) / target * 100)
            print(f"  {p}/{q_frac} = {float(frac):.10f}  |theta_1| = {float(val_frac):.10f}  ({diff_pct:+.4f}%)")

# Check algebraic numbers
print(f"\nAlgebraic candidates:")
for name, val in [
    ("1/(2*sqrt(2))", R(1)/(2*sqrt(R(2)))),
    ("(sqrt(3)-1)/4", (sqrt(R(3))-1)/R(4)),
    ("1/(1+sqrt(3))", R(1)/(R(1)+sqrt(R(3)))),
    ("ln(3)/(2*pi)", R(ln(R(3)))/(2*pi_val)),
    ("1/sqrt(5)", R(1)/sqrt(R(5))),
    ("(sqrt(5)-1)/4", (sqrt(R(5))-1)/R(4)),
    ("3/(2*(1+sqrt(5)))", R(3)/(R(2)*(R(1)+sqrt(R(5))))),
    ("ln(2)/sqrt(3)", R(ln(R(2)))/sqrt(R(3))),
    ("2/sqrt(29)", R(2)/sqrt(R(29))),
    ("sqrt(3)/sqrt(13)", sqrt(R(3))/sqrt(R(13))),
    ("1/sqrt(pi)", R(1)/sqrt(pi_val)),
]:
    if abs(val - z0) < R(0.01):
        theta_val = theta1_abs(val)
        diff_pct = float((theta_val - target) / target * 100)
        print(f"  {name:>25} = {float(val):.10f}  |theta_1| = {float(theta_val):.10f}  ({diff_pct:+.4f}%)")

# ============================================================
# The INVERSE problem: what shift gives EXACTLY ln(3)/sqrt(2)?
# ============================================================
print(f"\n{'='*60}")
print("KEY QUESTION: What IS z_0 exactly?")
print(f"{'='*60}")

# z_0 satisfies |theta_1(z_0 | omega)| = ln(3)/sqrt(2)
# Let's see what 1/z_0 is, z_0^2, etc.
print(f"\nz_0 = {float(z0):.15f}")
print(f"1/z_0 = {float(R(1)/z0):.15f}")
print(f"z_0^2 = {float(z0^2):.15f}")
print(f"z_0 * 18 = {float(z0 * R(18)):.15f}")
print(f"z_0 * 36 = {float(z0 * R(36)):.15f}")
print(f"z_0 * pi = {float(z0 * pi_val):.15f}")
print(f"z_0 * 2*pi = {float(z0 * 2 * pi_val):.15f}")
print(f"z_0 * sqrt(3) = {float(z0 * sqrt(R(3))):.15f}")
print(f"z_0 * sqrt(2) = {float(z0 * sqrt(R(2))):.15f}")
print(f"sin(pi*z_0) = {float(R(sin(pi_val * z0))):.15f}")
print(f"cos(pi*z_0) = {float(R(cos(pi_val * z0))):.15f}")
print(f"tan(pi*z_0) = {float(R(tan(pi_val * z0))):.15f}")

# Also check: does the RIGHT root have a nice form?
z0r = z0_right
print(f"\nRight root z_0' = {float(z0r):.15f}")
print(f"1/z_0' = {float(R(1)/z0r):.15f}")
print(f"z_0' * 6 = {float(z0r * R(6)):.15f}")
print(f"z_0' * 12 = {float(z0r * R(12)):.15f}")
print(f"1 - z_0' = {float(R(1) - z0r):.15f}")
print(f"1/2 - z_0' = {float(R(1)/R(2) - z0r):.15f}")
print(f"(1/2 - z_0') * 18 = {float((R(1)/R(2) - z0r) * R(18)):.15f}")
print(f"z_0 + z_0' = {float(z0 + z0r):.15f}")  # Should be ~0.5 by symmetry

# ============================================================
# Alternative: Does any theta ratio give ln(3)/sqrt(2)?
# ============================================================
print(f"\n{'='*60}")
print("THETA FUNCTION RATIOS")
print(f"{'='*60}")

# Compute various theta functions at z = 5/18
z = R(5) / R(18)
theta1_val = theta1_abs(z)

# theta_2(z|tau) = theta_1(z + 1/2 | tau)
theta2_val = theta1_abs(z + R(1)/R(2))

# theta_3 and theta_4 (these are the "even" theta functions)
# theta_3(z|tau) = 1 + 2*sum q^{n^2} cos(2*n*pi*z)
theta3_val = R(1)
for n in range(1, 300):
    q_pow = R(n)^2
    theta3_val += R(2) * abs(q)^q_pow * R(cos(2*n*pi_val*z))

# theta_4(z|tau) = 1 + 2*sum (-1)^n q^{n^2} cos(2*n*pi*z)
theta4_val = R(1)
for n in range(1, 300):
    q_pow = R(n)^2
    theta4_val += R(2) * (-1)^n * abs(q)^q_pow * R(cos(2*n*pi_val*z))

# eta value
gamma_13 = R(gamma(QQ(1)/QQ(3)))
eta_val = R(3)^(R(1)/R(8)) * gamma_13^(R(3)/R(2)) / (R(2) * pi_val)

print(f"\nAt z = 5/18, tau = omega:")
print(f"  |theta_1| = {float(theta1_val):.15f}")
print(f"  |theta_2| = {float(theta2_val):.15f}")
print(f"  |theta_3| = {float(theta3_val):.15f}")
print(f"  |theta_4| = {float(theta4_val):.15f}")
print(f"  |eta|     = {float(eta_val):.15f}")
print(f"  target    = {float(target):.15f}")

print(f"\nRatios involving target:")
for name, val in [
    ("theta_1/eta", theta1_val/eta_val),
    ("theta_2/theta_3", theta2_val/theta3_val),
    ("theta_4/theta_3", theta4_val/theta3_val),
    ("theta_1/theta_3", theta1_val/theta3_val),
    ("theta_1*theta_4/(theta_2*theta_3)", theta1_val*theta4_val/(theta2_val*theta3_val)),
    ("eta^2/theta_1", eta_val^2/theta1_val),
    ("theta_1^2/eta", theta1_val^2/eta_val),
    ("theta_1*eta", theta1_val*eta_val),
    ("ln(theta_3/theta_4)", R(ln(theta3_val/theta4_val))),
    ("theta_3^2 - theta_4^2", theta3_val^2 - theta4_val^2),
]:
    v = float(val)
    diff_pct = (v - float(target)) / float(target) * 100
    match = " <-- MATCH!" if abs(diff_pct) < 0.5 else ""
    print(f"  {name:<40} = {v:>15.10f}  ({diff_pct:+8.3f}%){match}")

# ============================================================
# The eta_omega^3 / (2*pi) combination
# ============================================================
print(f"\n{'='*60}")
print("SPECIAL COMBINATIONS")
print(f"{'='*60}")

# From the Chowla-Selberg formula, eta(omega) involves Gamma(1/3) and 3^{1/8}
# Check combinations of these constants
for name, val in [
    ("3^{1/8} * G(1/3)^{3/2} / (2pi)", R(3)^(R(1)/R(8)) * gamma_13^(R(3)/R(2)) / (2*pi_val)),
    ("eta(omega)", eta_val),
    ("eta^3", eta_val^3),
    ("eta^3 * sqrt(3)", eta_val^3 * sqrt(R(3))),
    ("3^{3/8} * eta^2", R(3)^(R(3)/R(8)) * eta_val^2),
    ("sqrt(3/pi) * eta^2", sqrt(R(3)/pi_val) * eta_val^2),
    ("G(1/3)^3 / (4*pi^2)", gamma_13^3 / (4*pi_val^2)),
    ("ln(3) / sqrt(2)", target),
    ("G(1/3)^3 / (4*pi^2) * 3^{1/4}", gamma_13^3 / (4*pi_val^2) * R(3)^(R(1)/R(4))),
    ("2*pi * eta^2 / G(1/3)^{3/2}", 2*pi_val * eta_val^2 / gamma_13^(R(3)/R(2))),
    ("G(1/3)^3 * 3^{1/4} / (8*pi^2)", gamma_13^3 * R(3)^(R(1)/R(4)) / (8*pi_val^2)),
]:
    v = float(val)
    diff_pct = (v - float(target)) / float(target) * 100
    match = " <-- EXACT" if abs(diff_pct) < 0.01 else (" <-- CLOSE" if abs(diff_pct) < 1 else "")
    print(f"  {name:<45} = {v:>15.10f}  ({diff_pct:+8.4f}%){match}")

# Can eta(omega) be expressed as exp(ln(3)/sqrt(2) + correction)?
print(f"\nln(eta(omega)) = {float(R(ln(eta_val))):.15f}")
print(f"ln(3)/sqrt(2) - 1 = {float(target - R(1)):.15f}")
print(f"eta = exp(ln(3)/sqrt(2) * x) where x = {float(R(ln(eta_val)) / target):.15f}")

# ============================================================
# DIRECT TEST: |theta_1(z|omega)| at z = ln(3)/(pi*sqrt(6))
# ============================================================
# This shift would mean the Wilson line is determined by ln(3)
z_test = R(ln(R(3))) / (pi_val * sqrt(R(6)))
theta_test = theta1_abs(z_test)
print(f"\n|theta_1(ln(3)/(pi*sqrt(6)) | omega)| = {float(theta_test):.15f}  vs target {float(target):.15f}")

z_test2 = R(ln(R(3))) / (R(2) * pi_val)
theta_test2 = theta1_abs(z_test2)
print(f"|theta_1(ln(3)/(2*pi) | omega)| = {float(theta_test2):.15f}  vs target {float(target):.15f}")

z_test3 = target / pi_val
theta_test3 = theta1_abs(z_test3)
print(f"|theta_1(ln(3)/(pi*sqrt(2)) | omega)| = {float(theta_test3):.15f}  vs target {float(target):.15f}")

print(f"\n{'='*60}")
print("COMPUTATION COMPLETE")
print(f"{'='*60}")
