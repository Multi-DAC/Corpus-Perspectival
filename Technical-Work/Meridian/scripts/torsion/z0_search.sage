"""
Precise binary search for z_0 where |theta_1(z_0 | omega)| = ln(3)/sqrt(2)
"""
from sage.all import *

R = RealField(200)
C = ComplexField(200)
pi_val = R(pi)
omega = C(exp(2 * pi * I / 3))
q = C(exp(2 * pi * I * omega))
target = R(ln(R(3))) / R(sqrt(R(2)))

def theta1_abs(z):
    z_r = R(z)
    result = C(0)
    for n in range(300):
        sign = (-1)^n
        q_pow = (n + R(1)/R(2))^2 / R(2)
        s_arg = (2*n + 1) * pi_val * z_r
        result += C(sign) * q^q_pow * C(sin(s_arg))
    return abs(2 * result)

print(f"Target: {float(target):.15f}")
print()

# Binary search in [0.275, 0.278]
z_lo = R(0.275)
z_hi = R(0.278)

for i in range(100):
    z_mid = (z_lo + z_hi) / R(2)
    val = theta1_abs(z_mid)
    if val < target:
        z_lo = z_mid
    else:
        z_hi = z_mid

z0 = (z_lo + z_hi) / R(2)
val0 = theta1_abs(z0)
print(f"z_0 = {z0}")
print(f"|theta_1(z_0|omega)| = {val0}")
print(f"target               = {target}")
print(f"relative error: {float(abs(val0 - target)/target):.2e}")
print()

# Now analyze z_0
print("=" * 60)
print("WHAT IS z_0?")
print("=" * 60)
print(f"\nz_0 = {float(z0):.18f}")

# Check various representations
print(f"\nz_0 * 6   = {float(z0*6):.18f}")
print(f"z_0 * 12  = {float(z0*12):.18f}")
print(f"z_0 * 18  = {float(z0*18):.18f}")
print(f"z_0 * 24  = {float(z0*24):.18f}")
print(f"z_0 * 36  = {float(z0*36):.18f}")
print(f"z_0 * pi  = {float(z0*pi_val):.18f}")
print(f"z_0 * 2pi = {float(z0*2*pi_val):.18f}")

print(f"\n5/18 = {float(R(5)/R(18)):.18f}")
print(f"z_0 - 5/18 = {float(z0 - R(5)/R(18)):.18e}")
print(f"z_0 / (5/18) = {float(z0 / (R(5)/R(18))):.18f}")

# Try simple fractions with small denominators
print(f"\nSimple fraction search:")
best_frac = None
best_err = 1.0
for denom in range(1, 500):
    numer = round(float(z0 * denom))
    if numer > 0 and numer < denom:
        frac = R(numer) / R(denom)
        err = abs(float(frac - z0))
        if err < 1e-6 and err < best_err:
            best_frac = (numer, denom)
            best_err = err
            print(f"  {numer}/{denom} = {float(frac):.18f}  error = {err:.2e}")

# Try irrational numbers
print(f"\nIrrational candidates:")
candidates = [
    ("ln(3)/(2*sqrt(2))", R(ln(R(3)))/(2*sqrt(R(2)))),
    ("ln(3)/4", R(ln(R(3)))/4),
    ("ln(2)/sqrt(5)", R(ln(R(2)))/sqrt(R(5))),
    ("(sqrt(5)-1)/(2*sqrt(5))", (sqrt(R(5))-1)/(2*sqrt(R(5)))),
    ("1/(2*sqrt(pi/ln(3)))", R(1)/(2*sqrt(pi_val/R(ln(R(3)))))),
    ("ln(3)/(pi*sqrt(2))", R(ln(R(3)))/(pi_val*sqrt(R(2)))),
    ("sqrt(ln(3)/ln(27))", sqrt(R(ln(R(3)))/R(ln(R(27))))),
    ("1/sqrt(13)", R(1)/sqrt(R(13))),
    ("sqrt(3)/(2*sqrt(13))", sqrt(R(3))/(2*sqrt(R(13)))),
    ("pi/sqrt(129)", pi_val/sqrt(R(129))),
    ("3/(sqrt(2)*pi*sqrt(3))", R(3)/(sqrt(R(2))*pi_val*sqrt(R(3)))),
    ("ln(3)^2/2", R(ln(R(3)))^2/2),
    ("sin(pi/6)/sqrt(e)", R(sin(pi_val/6))/sqrt(R(exp(R(1))))),
    ("3/(2*e*sqrt(2))", R(3)/(2*R(exp(R(1)))*sqrt(R(2)))),
]

for name, val in candidates:
    err = abs(float(val - z0))
    if err < 0.01:
        theta_val = theta1_abs(val)
        theta_err = float(abs(theta_val - target)/target*100)
        print(f"  {name:<35} = {float(val):.15f}  z-err={err:.6e}  |theta|={float(theta_val):.10f} ({theta_err:+.4f}%)")

# Most interesting: check if z_0 = ln(3)/(2*sqrt(2))
z_test = R(ln(R(3))) / (2*sqrt(R(2)))
print(f"\n*** ln(3)/(2*sqrt(2)) = {float(z_test):.18f}")
print(f"*** z_0               = {float(z0):.18f}")
print(f"*** difference         = {float(z0 - z_test):.6e}")
theta_test = theta1_abs(z_test)
print(f"*** |theta_1(ln(3)/(2sqrt2)|omega)| = {float(theta_test):.15f}")
print(f"*** target                          = {float(target):.15f}")
print(f"*** error                           = {float(abs(theta_test-target)/target*100):.6f}%")

# Check the SELF-REFERENTIAL possibility:
# z_0 = ln(3)/(2*sqrt(2)) means the shift = target/2
# i.e., |theta_1(target/2 | omega)| = target
# This would be: |theta_1(ln(3)/(2*sqrt(2)) | omega)| = ln(3)/sqrt(2)
z_self = target / R(2)
print(f"\n*** Self-referential: z = target/2 = {float(z_self):.18f}")
print(f"*** z_0                            = {float(z0):.18f}")
print(f"*** difference                     = {float(z0 - z_self):.6e}")

# Also check ln(3)^2/2
z_ln3sq = R(ln(R(3)))^2 / 2
print(f"\n*** ln(3)^2/2 = {float(z_ln3sq):.18f}")
theta_ln3sq = theta1_abs(z_ln3sq)
print(f"*** |theta_1| = {float(theta_ln3sq):.15f} vs target {float(target):.15f}")

# ============================================================
# The PHYSICAL question: what Wilson line value produces this?
# ============================================================
print(f"\n{'='*60}")
print("PHYSICAL INTERPRETATION")
print(f"{'='*60}")

print(f"\nz_0 = {float(z0):.15f}")
print(f"If this is the U(1)_Y charge * Wilson line shift:")
print(f"  For q_Y = 5/6: phi = z_0 * 6/5 = {float(z0*R(6)/R(5)):.15f}")
print(f"  For q_Y = 1:   phi = z_0       = {float(z0):.15f}")
print(f"  For q_Y = 1/2: phi = 2*z_0     = {float(2*z0):.15f}")

# On Z_3 orbifold, Wilson lines are quantized to 0, 1/3, 2/3 (mod 1)
# But continuous Wilson lines are allowed on smooth manifolds
print(f"\nQuantized check: z_0 * 3 = {float(z0*3):.15f}")
print(f"                 z_0 * 6 = {float(z0*6):.15f}")

# ============================================================
# THETA RATIO: more precise calculation
# ============================================================
print(f"\n{'='*60}")
print("THETA_1/THETA_3 RATIO (more precise)")
print(f"{'='*60}")

# Compute theta_3 at the exact z where theta_1/theta_3 = target
# theta_3(z|tau) = 1 + 2*sum q^{n^2} cos(2*n*pi*z)
def theta3_val_fn(z):
    z_r = R(z)
    result = R(1)
    for n in range(1, 300):
        q_pow = R(n)^2
        result += R(2) * abs(q)^q_pow * R(cos(2*n*pi_val*z_r))
    return result

# Binary search for z where theta_1/theta_3 = target
z_lo2 = R(0.27)
z_hi2 = R(0.29)

for i in range(100):
    z_mid = (z_lo2 + z_hi2) / R(2)
    ratio = theta1_abs(z_mid) / theta3_val_fn(z_mid)
    if ratio < target:
        z_lo2 = z_mid
    else:
        z_hi2 = z_mid

z0_ratio = (z_lo2 + z_hi2) / R(2)
t1 = theta1_abs(z0_ratio)
t3 = theta3_val_fn(z0_ratio)
print(f"\nz where theta_1/theta_3 = target:")
print(f"  z = {float(z0_ratio):.18f}")
print(f"  theta_1/theta_3 = {float(t1/t3):.15f}")
print(f"  target          = {float(target):.15f}")
print(f"  5/18            = {float(R(5)/R(18)):.18f}")
print(f"  z - 5/18        = {float(z0_ratio - R(5)/R(18)):.6e}")

# At z = 5/18, what is the exact ratio?
t1_518 = theta1_abs(R(5)/R(18))
t3_518 = theta3_val_fn(R(5)/R(18))
print(f"\nAt z = 5/18 exactly:")
print(f"  theta_1 = {float(t1_518):.15f}")
print(f"  theta_3 = {float(t3_518):.15f}")
print(f"  theta_1/theta_3 = {float(t1_518/t3_518):.15f}")
print(f"  target          = {float(target):.15f}")
print(f"  error = {float(abs(t1_518/t3_518 - target)/target*100):.4f}%")

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"\n1. |theta_1(z_0 | omega)| = ln(3)/sqrt(2)  at z_0 = {float(z0):.10f}")
print(f"   (5/18 = {float(R(5)/R(18)):.10f}, differs by {float(abs(z0 - R(5)/R(18))):.6e})")
print(f"\n2. theta_1/theta_3 = ln(3)/sqrt(2)  at z = {float(z0_ratio):.10f}")
print(f"   (5/18 = {float(R(5)/R(18)):.10f}, differs by {float(abs(z0_ratio - R(5)/R(18))):.6e})")
print(f"\n3. At z = 5/18 exactly:")
print(f"   |theta_1| = {float(t1_518):.10f}  ({float(abs(t1_518-target)/target*100):.4f}% from target)")
print(f"   theta_1/theta_3 = {float(t1_518/t3_518):.10f}  ({float(abs(t1_518/t3_518-target)/target*100):.4f}% from target)")
