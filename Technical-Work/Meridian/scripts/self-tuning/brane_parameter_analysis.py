"""
Brane Parameter Analysis — Project Meridian
=============================================
Investigates the discrepancy between claimed Phi_0 = 0.477493
and the actual junction condition solution Phi_0 = 0.0761
with stated parameters (sigma_UV=6, alpha_UV=0.01, xi=1/6, mu2=0.1, M5_3=1).

Junction conditions:
  JC1: p(0) = -(sigma_UV + alpha_UV * Phi0^2) / (12 * F(Phi0))
       where F(Phi) = M5_3 - xi * Phi^2
  JC2: 2*mu2 + 32*xi*Phi0*p(0) = -4*alpha_UV*Phi0

Combining: substitute JC1 into JC2 to get a single equation in Phi0.
"""

import numpy as np
from scipy.optimize import fsolve, brentq
import sys
import io

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

output_lines = []

def log(s=""):
    print(s)
    output_lines.append(s)

def banner(title):
    log("")
    log("=" * 70)
    log(f"  {title}")
    log("=" * 70)

# ============================================================
# Core functions
# ============================================================

def F(Phi, xi, M5_3):
    """Effective Planck mass function"""
    return M5_3 - xi * Phi**2

def p0_from_JC1(Phi0, sigma_UV, alpha_UV, xi, M5_3):
    """JC1: p(0) = -(sigma_UV + alpha_UV * Phi0^2) / (12 * F(Phi0))"""
    Fval = F(Phi0, xi, M5_3)
    if abs(Fval) < 1e-15:
        return np.inf
    return -(sigma_UV + alpha_UV * Phi0**2) / (12.0 * Fval)

def JC2_residual(Phi0, sigma_UV, alpha_UV, xi, mu2, M5_3):
    """
    JC2: 2*mu2 + 32*xi*Phi0*p(0) = -4*alpha_UV*Phi0
    Residual = LHS - RHS = 2*mu2 + 32*xi*Phi0*p(0) + 4*alpha_UV*Phi0
    """
    p0 = p0_from_JC1(Phi0, sigma_UV, alpha_UV, xi, M5_3)
    return 2.0*mu2 + 32.0*xi*Phi0*p0 + 4.0*alpha_UV*Phi0

def find_Phi0(sigma_UV, alpha_UV, xi, mu2, M5_3, x0_guesses=None):
    """Find all roots of the combined junction condition."""
    if x0_guesses is None:
        x0_guesses = np.linspace(0.001, 3.0, 500)

    roots = []
    # Evaluate residual on a grid and find sign changes
    vals = []
    for x in x0_guesses:
        Fval = F(x, xi, M5_3)
        if abs(Fval) < 1e-10:
            vals.append(np.nan)
            continue
        vals.append(JC2_residual(x, sigma_UV, alpha_UV, xi, mu2, M5_3))

    for i in range(len(vals)-1):
        if np.isnan(vals[i]) or np.isnan(vals[i+1]):
            continue
        if vals[i] * vals[i+1] < 0:
            try:
                root = brentq(lambda x: JC2_residual(x, sigma_UV, alpha_UV, xi, mu2, M5_3),
                              x0_guesses[i], x0_guesses[i+1])
                # Check it's not near the singularity
                if abs(F(root, xi, M5_3)) > 1e-8:
                    # Check it's not a duplicate
                    is_dup = False
                    for r in roots:
                        if abs(r - root) < 1e-8:
                            is_dup = True
                            break
                    if not is_dup:
                        roots.append(root)
            except:
                pass

    return sorted(roots)

# ============================================================
# Cosmological formulas
# ============================================================

def compute_zeta0(Phi0, xi, M5_3):
    return xi * Phi0**2 / M5_3

def compute_w0(zeta0, q0=-0.55, Omega_DE=0.685, eps1=0.017):
    """CKK formula: 1 + w0 = ((1+q0)^2 * Omega_DE * eps1) / (4*(1-q0)^2 * zeta0)"""
    if abs(zeta0) < 1e-15:
        return -np.inf
    numerator = (1.0 + q0)**2 * Omega_DE * eps1
    denominator = 4.0 * (1.0 - q0)**2 * zeta0
    return -1.0 + numerator / denominator

# ============================================================
# PART 1: Confirm stated parameters give Phi0 ~ 0.076
# ============================================================

banner("PART 1: Junction Conditions with Stated Parameters")

sigma_UV = 6.0
alpha_UV = 0.01
xi = 1.0/6.0
mu2 = 0.1
M5_3 = 1.0

log(f"Parameters: sigma_UV={sigma_UV}, alpha_UV={alpha_UV}, xi={xi:.6f}, mu2={mu2}, M5_3={M5_3}")
log(f"Singularity at Phi = sqrt(M5_3/xi) = sqrt({M5_3/xi:.4f}) = {np.sqrt(M5_3/xi):.6f}")
log("")

# Find roots
roots = find_Phi0(sigma_UV, alpha_UV, xi, mu2, M5_3)

log(f"Found {len(roots)} root(s) of combined junction condition:")
for i, r in enumerate(roots):
    p0 = p0_from_JC1(r, sigma_UV, alpha_UV, xi, M5_3)
    resid = JC2_residual(r, sigma_UV, alpha_UV, xi, mu2, M5_3)
    Fval = F(r, xi, M5_3)
    zeta = compute_zeta0(r, xi, M5_3)
    log(f"  Root {i+1}: Phi_0 = {r:.10f}")
    log(f"    p(0)     = {p0:.10f}")
    log(f"    F(Phi_0) = {Fval:.10f}")
    log(f"    Residual = {resid:.2e}")
    log(f"    zeta_0   = {zeta:.10f}")

log("")
log("VERDICT: The stated parameters produce Phi_0 ~ 0.076, NOT 0.477.")

# Check what residual the claimed value gives
Phi_claimed = 0.477493
resid_claimed = JC2_residual(Phi_claimed, sigma_UV, alpha_UV, xi, mu2, M5_3)
p0_claimed = p0_from_JC1(Phi_claimed, sigma_UV, alpha_UV, xi, M5_3)
F_claimed = F(Phi_claimed, xi, M5_3)
log(f"\nAt claimed Phi_0 = {Phi_claimed}:")
log(f"  F(Phi_0)  = {F_claimed:.10f}")
log(f"  p(0)      = {p0_claimed:.10f}")
log(f"  JC2 residual = {resid_claimed:.6f}  (should be 0 if it were a solution)")

# ============================================================
# PART 2: Reverse-engineer parameters for Phi0 = 0.477493
# ============================================================

banner("PART 2: Reverse Engineering — What Parameters Give Phi_0 = 0.477493?")

log("Fixing xi = 1/6, M5_3 = 1. Solving for (sigma_UV, alpha_UV, mu2).")
log("We have TWO equations (JC1 substituted into JC2 gives one; but we need")
log("specific p(0) too). The system is underdetermined with 3 unknowns and")
log("effectively 1 combined equation. So we parameterize.")
log("")

Phi0_target = 0.477493
F_target = F(Phi0_target, xi, M5_3)
log(f"At Phi_0 = {Phi0_target}: F(Phi_0) = {F_target:.10f}")
log("")

# Combined equation (JC1 into JC2):
# 2*mu2 - (32*xi*Phi0/(12*F)) * (sigma_UV + alpha_UV*Phi0^2) + 4*alpha_UV*Phi0 = 0
# 2*mu2 - (8*xi*Phi0/(3*F)) * (sigma_UV + alpha_UV*Phi0^2) + 4*alpha_UV*Phi0 = 0
#
# Let A = 8*xi*Phi0/(3*F), B = Phi0^2
# 2*mu2 - A*(sigma_UV + alpha_UV*B) + 4*alpha_UV*Phi0 = 0
# 2*mu2 - A*sigma_UV - A*alpha_UV*B + 4*alpha_UV*Phi0 = 0
# 2*mu2 = A*sigma_UV + alpha_UV*(A*B - 4*Phi0)

A = 8.0 * xi * Phi0_target / (3.0 * F_target)
B = Phi0_target**2

log(f"Combined equation: 2*mu2 = A*sigma_UV + alpha_UV*(A*B - 4*Phi0)")
log(f"  where A = 8*xi*Phi0/(3*F) = {A:.10f}")
log(f"  and   B = Phi0^2 = {B:.10f}")
log(f"  and   A*B - 4*Phi0 = {A*B - 4*Phi0_target:.10f}")
log("")

# Strategy: scan sigma_UV and alpha_UV, compute required mu2
log("--- Scan: Fix alpha_UV, vary sigma_UV, compute required mu2 ---")
log(f"{'alpha_UV':>10} {'sigma_UV':>10} {'mu2':>12} {'p(0)':>12} {'Physical?':>12}")
log("-" * 60)

results = []
for alpha_test in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.5, 1.0]:
    for sigma_test in [0.1, 0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 20.0]:
        mu2_required = 0.5 * (A * sigma_test + alpha_test * (A * B - 4.0 * Phi0_target))
        p0_val = p0_from_JC1(Phi0_target, sigma_test, alpha_test, xi, M5_3)

        # Physical reasonableness checks
        physical = "Yes" if mu2_required > 0 and sigma_test > 0 and alpha_test > 0 else "No (mu2<0)"
        if mu2_required > 0:
            results.append((alpha_test, sigma_test, mu2_required, p0_val))

        # Only print a selection
        if sigma_test in [0.1, 1.0, 6.0, 20.0]:
            log(f"{alpha_test:10.3f} {sigma_test:10.1f} {mu2_required:12.6f} {p0_val:12.6f} {physical:>12}")

log("")
log("--- Specific case: closest to original alpha_UV=0.01 ---")
for alpha_test in [0.01]:
    for sigma_test in [0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]:
        mu2_required = 0.5 * (A * sigma_test + alpha_test * (A * B - 4.0 * Phi0_target))
        p0_val = p0_from_JC1(Phi0_target, sigma_test, alpha_test, xi, M5_3)
        resid_check = JC2_residual(Phi0_target, sigma_test, alpha_test, xi, mu2_required, M5_3)
        log(f"  sigma_UV={sigma_test:6.1f}, mu2={mu2_required:10.6f}, p(0)={p0_val:10.6f}, verify_resid={resid_check:.2e}")

log("")
log("--- What if we also fix sigma_UV=6? Solve for alpha_UV and mu2 ---")
log("With sigma_UV=6 fixed, we still have 2 unknowns (alpha_UV, mu2) and 1 equation.")
log("Parameterize by alpha_UV:")
log(f"{'alpha_UV':>10} {'mu2_required':>14} {'p(0)':>12}")
log("-" * 40)
for alpha_test in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]:
    mu2_req = 0.5 * (A * 6.0 + alpha_test * (A * B - 4.0 * Phi0_target))
    p0_val = p0_from_JC1(Phi0_target, 6.0, alpha_test, xi, M5_3)
    log(f"{alpha_test:10.4f} {mu2_req:14.6f} {p0_val:12.6f}")

# ============================================================
# PART 3: Physical reasonableness assessment
# ============================================================

banner("PART 3: Physical Reasonableness Assessment")

log("For Phi_0 = 0.477493 with xi=1/6, M5_3=1:")
log(f"  F(Phi_0) = {F_target:.6f}")
log(f"  Phi_0/sqrt(M5_3/xi) = {Phi0_target/np.sqrt(M5_3/xi):.4f} (fraction of singularity)")
log(f"  Singularity at Phi = {np.sqrt(M5_3/xi):.4f}")
log("")
log("The scalar field is at ~19.5% of the ghost threshold (F=0).")
log("This is not immediately pathological, but it's a significant displacement.")
log("")

# With original parameters, what zeta0 would Phi0=0.477 give?
zeta_claimed = compute_zeta0(Phi0_target, xi, M5_3)
log(f"If Phi_0 = {Phi0_target} WERE correct:")
log(f"  zeta_0 = xi * Phi_0^2 / M5_3 = {zeta_claimed:.6f}")
log(f"  This is the famous zeta_0 = 0.038 value!")
log("")

# With actual root
Phi0_actual = roots[0] if roots else 0.0761
zeta_actual = compute_zeta0(Phi0_actual, xi, M5_3)
log(f"With actual Phi_0 = {Phi0_actual:.6f}:")
log(f"  zeta_0 = {zeta_actual:.6f}")
log("")

log("KEY INSIGHT: The claimed Phi_0 = 0.477493 was likely CHOSEN to produce")
log(f"zeta_0 = 0.038 (since 1/6 * 0.477493^2 = {zeta_claimed:.6f}), and the brane")
log("parameters were not self-consistently derived from the junction conditions.")

# ============================================================
# PART 4: w0 from CKK formula for Phi0 = 0.076
# ============================================================

banner("PART 4: CKK Dark Energy Equation of State")

q0 = -0.55
Omega_DE = 0.685
eps1 = 0.017

log(f"CKK formula: 1 + w0 = ((1+q0)^2 * Omega_DE * eps1) / (4*(1-q0)^2 * zeta0)")
log(f"Standard parameters: q0={q0}, Omega_DE={Omega_DE}, eps1={eps1}")
log("")

# Numerator is constant
numerator = (1.0 + q0)**2 * Omega_DE * eps1
log(f"Numerator = (1+q0)^2 * Omega_DE * eps1 = {numerator:.10f}")
log(f"Denominator prefactor = 4*(1-q0)^2 = {4.0*(1.0-q0)**2:.10f}")
log("")

# For actual Phi0
log(f"--- For Phi_0 = {Phi0_actual:.6f} (actual JC solution) ---")
log(f"  zeta_0 = {zeta_actual:.8f}")
w0_actual = compute_w0(zeta_actual, q0, Omega_DE, eps1)
log(f"  w_0 = {w0_actual:.6f}")
log(f"  1 + w_0 = {1+w0_actual:.6f}")
log("")

# ============================================================
# PART 5: w0 for zeta0 = 0.038
# ============================================================

banner("PART 5: w0 for the Claimed zeta_0 = 0.038")

zeta_paper = 0.038
w0_paper = compute_w0(zeta_paper, q0, Omega_DE, eps1)
log(f"  zeta_0 = {zeta_paper}")
log(f"  w_0 = {w0_paper:.6f}")
log(f"  1 + w_0 = {1+w0_paper:.6f}")
log("")
log(f"  Paper claims w_0 = -0.993 +/- 0.002")
log(f"  CKK gives    w_0 = {w0_paper:.6f}")
log(f"  Discrepancy:       {abs(w0_paper - (-0.993)):.6f}")
log("")

# Also check what zeta0 gives exactly w0 = -0.993
# 1 + w0 = 0.007 = num / (4*(1-q0)^2 * zeta0)
# zeta0 = num / (4*(1-q0)^2 * 0.007)
zeta_exact = numerator / (4.0 * (1.0 - q0)**2 * 0.007)
log(f"  zeta_0 that gives EXACTLY w_0 = -0.993: {zeta_exact:.6f}")
Phi0_for_exact = np.sqrt(zeta_exact * M5_3 / xi)
log(f"  Corresponding Phi_0 = sqrt(zeta_0 * M5_3 / xi) = {Phi0_for_exact:.6f}")

# ============================================================
# PART 6: Scan — what zeta0 gives w0 in [-0.80, -0.70]?
# ============================================================

banner("PART 6: zeta_0 Values Giving w_0 in [-0.80, -0.70] (DESI-like)")

log("Scanning zeta_0 to find w_0 in [-0.80, -0.70]:")
log("")

# 1 + w0 = num / (denom_prefactor * zeta0)
# w0 = -0.80 => 1+w0 = 0.20 => zeta0 = num / (denom_pf * 0.20)
# w0 = -0.70 => 1+w0 = 0.30 => zeta0 = num / (denom_pf * 0.30)

denom_pf = 4.0 * (1.0 - q0)**2

zeta_for_w070 = numerator / (denom_pf * 0.30)
zeta_for_w080 = numerator / (denom_pf * 0.20)

log(f"  w_0 = -0.70 => zeta_0 = {zeta_for_w070:.6f}")
log(f"  w_0 = -0.80 => zeta_0 = {zeta_for_w080:.6f}")
log(f"  DESI-like range: zeta_0 in [{zeta_for_w080:.6f}, {zeta_for_w070:.6f}]")
log("")

Phi0_for_w070 = np.sqrt(zeta_for_w070 * M5_3 / xi)
Phi0_for_w080 = np.sqrt(zeta_for_w080 * M5_3 / xi)
log(f"  Corresponding Phi_0 range: [{Phi0_for_w080:.6f}, {Phi0_for_w070:.6f}]")
log("")

# Detailed scan
log(f"{'w_0':>8} {'1+w_0':>8} {'zeta_0':>12} {'Phi_0':>12}")
log("-" * 44)
for w0_target in np.arange(-0.80, -0.695, 0.01):
    one_plus_w = 1.0 + w0_target
    z = numerator / (denom_pf * one_plus_w)
    phi = np.sqrt(z * M5_3 / xi)
    log(f"{w0_target:8.2f} {one_plus_w:8.3f} {z:12.6f} {phi:12.6f}")

log("")

# Compare with actual JC solution
log("--- Comparison ---")
log(f"  Actual JC solution (sigma=6, alpha=0.01, mu2=0.1):")
log(f"    Phi_0 = {Phi0_actual:.6f}, zeta_0 = {zeta_actual:.6f}, w_0 = {w0_actual:.4f}")
log("")
log(f"  Paper's claimed values:")
log(f"    Phi_0 = 0.477493, zeta_0 = 0.038, w_0 = -0.993")
log("")

# Is the actual solution's w0 in DESI range?
log(f"  The actual JC solution gives w_0 = {w0_actual:.4f}")
if -0.80 <= w0_actual <= -0.70:
    log("  >>> THIS IS IN THE DESI RANGE! <<<")
elif w0_actual > -0.70:
    log("  >>> This is ABOVE the DESI range (less negative) <<<")
else:
    log("  >>> This is BELOW the DESI range (more negative) <<<")

# ============================================================
# SUMMARY
# ============================================================

banner("SUMMARY")

log("1. CONFIRMED: The stated brane parameters (sigma_UV=6, alpha_UV=0.01,")
log(f"   xi=1/6, mu2=0.1, M5_3=1) yield Phi_0 = {Phi0_actual:.6f}, NOT 0.477493.")
log("")
log("2. REVERSE ENGINEERING: Phi_0 = 0.477493 CAN be obtained with different")
log("   brane parameters. The system is underdetermined (1 equation, 3 unknowns")
log("   after fixing xi and M5_3). For example, with sigma_UV=6 and alpha_UV=0.01,")
mu2_needed_s6 = 0.5 * (A * 6.0 + 0.01 * (A * B - 4.0 * Phi0_target))
log(f"   you need mu2 = {mu2_needed_s6:.6f} (vs stated mu2 = 0.1).")
log("")
log("3. PHYSICAL REASONABLENESS: The required mu2 values are O(1), not")
log("   unreasonable in Planck units, but the key issue is self-consistency:")
log("   the monograph's parameters and its claimed Phi_0 are INCONSISTENT.")
log("")
log(f"4. ACTUAL SOLUTION: Phi_0 = {Phi0_actual:.6f}")
log(f"   => zeta_0 = {zeta_actual:.8f}")
log(f"   => w_0 = {w0_actual:.6f} (CKK formula)")
log(f"   This is far from the claimed w_0 = -0.993.")
log("")
log(f"5. CLAIMED zeta_0 = 0.038 => w_0 = {w0_paper:.6f} (CKK formula)")
log(f"   Close to but not exactly -0.993.")
log(f"   Exact w_0 = -0.993 requires zeta_0 = {zeta_exact:.6f}")
log("")
log(f"6. DESI-LIKE w_0 in [-0.80, -0.70] requires:")
log(f"   zeta_0 in [{zeta_for_w080:.6f}, {zeta_for_w070:.6f}]")
log(f"   Phi_0 in [{Phi0_for_w080:.6f}, {Phi0_for_w070:.6f}]")
log("")
log("BOTTOM LINE: The monograph's central prediction (w_0 = -0.993) depends on")
log("zeta_0 = 0.038, which requires Phi_0 = 0.477. But the stated brane parameters")
log("give Phi_0 = 0.076, yielding a dramatically different zeta_0 and w_0.")
log("The brane parameters and the VEV are not self-consistent as published.")

# Write to file
output_path = r"C:\Users\mercu\clawd\projects\Project Meridian\Ongoing Peer Reviews\brane_parameter_analysis.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(output_lines))
    f.write("\n")

log("")
log(f"Output saved to: {output_path}")
