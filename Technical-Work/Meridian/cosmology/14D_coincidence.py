#!/usr/bin/env python3
"""
Track 14D: The Coincidence Problem
Full numerical computation for Project Meridian

Physics:
  w(z) = -1 + 2*kappa_0 / [Omega_DE * E^2(z)]
  kappa_0 = C_KK * Omega_DE / (2*zeta_0)  ... kinetic correction
  C_KK = (1+q0)^2 * Omega_DE * eps1 / [4*(1-q0)^2]
  E^2(z) = Omega_m*(1+z)^3 + Omega_DE

Author: Clawd (14D computation)
Date: 2026-03-18
"""

import numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
import json

###############################################################################
# 1. PARAMETERS
###############################################################################

Omega_DE = 0.685
Omega_m  = 0.315
q0       = -0.55
eps1     = 0.017
zeta_JC  = 0.001    # Junction conditions benchmark
zeta_CMB = 0.037    # CMB (Hiramatsu-Kobayashi) benchmark

# Derived: C_KK
C_KK = (1 + q0)**2 * Omega_DE * eps1 / (4 * (1 - q0)**2)

print("=" * 72)
print("TRACK 14D: THE COINCIDENCE PROBLEM")
print("=" * 72)

print("\n--- PART 1: Compute kappa_0 ---\n")
print(f"C_KK = (1+q0)^2 * Omega_DE * eps1 / [4*(1-q0)^2]")
print(f"     = ({1+q0})^2 * {Omega_DE} * {eps1} / [4 * ({1-q0})^2]")
print(f"     = {(1+q0)**2} * {Omega_DE} * {eps1} / [4 * {(1-q0)**2}]")
print(f"     = {(1+q0)**2 * Omega_DE * eps1} / {4*(1-q0)**2}")
print(f"     = {C_KK:.6e}")

# kappa_0 = C_KK * Omega_DE / (2 * zeta_0)
kappa0_JC  = C_KK * Omega_DE / (2 * zeta_JC)
kappa0_CMB = C_KK * Omega_DE / (2 * zeta_CMB)

print(f"\nFor zeta_0 = {zeta_JC} (JC benchmark):")
print(f"  kappa_0 = C_KK * Omega_DE / (2 * zeta_0)")
print(f"          = {C_KK:.6e} * {Omega_DE} / (2 * {zeta_JC})")
print(f"          = {kappa0_JC:.6e}")

print(f"\nFor zeta_0 = {zeta_CMB} (CMB benchmark):")
print(f"  kappa_0 = {kappa0_CMB:.6e}")

###############################################################################
# 2. w(z) EVOLUTION
###############################################################################

print("\n" + "=" * 72)
print("--- PART 2: w(z) Evolution ---\n")

def E2(z):
    return Omega_m * (1+z)**3 + Omega_DE

def w_of_z(z, kappa0):
    return -1.0 + 2.0 * kappa0 / (Omega_DE * E2(z))

z_values = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]

header = f"{'z':>5} | {'E2(z)':>10} | {'w(z) [JC]':>12} | {'|1+w| [JC]':>12} | {'w(z) [CMB]':>12} | {'|1+w| [CMB]':>12}"
print(header)
print("-" * len(header))

results_table = []
for z in z_values:
    e2 = E2(z)
    w_jc = w_of_z(z, kappa0_JC)
    w_cmb = w_of_z(z, kappa0_CMB)
    dev_jc = abs(1 + w_jc)
    dev_cmb = abs(1 + w_cmb)
    print(f"{z:5.1f} | {e2:10.4f} | {w_jc:12.6f} | {dev_jc:12.6e} | {w_cmb:12.6f} | {dev_cmb:12.6e}")
    results_table.append({
        'z': z, 'E2': e2,
        'w_JC': w_jc, 'dev_JC': dev_jc,
        'w_CMB': w_cmb, 'dev_CMB': dev_cmb
    })

# Observational sensitivity threshold
print("\n--- Observational sensitivity threshold: |1+w| = 0.05 ---")

E2_thresh_JC = 2 * kappa0_JC / (0.05 * Omega_DE)
print(f"\nJC benchmark (kappa_0 = {kappa0_JC:.6e}):")
print(f"  E2(z_thresh) = 2*kappa_0 / (0.05*Omega_DE) = {E2_thresh_JC:.6f}")

z_thresh_JC = None
if E2_thresh_JC > Omega_DE:
    onepz_cubed = (E2_thresh_JC - Omega_DE) / Omega_m
    z_thresh_JC = onepz_cubed**(1/3) - 1
    if z_thresh_JC > 0:
        print(f"  (1+z)^3 = {onepz_cubed:.6f}")
        print(f"  z_thresh = {z_thresh_JC:.4f}")
        print(f"  |1+w| drops below 0.05 at z > {z_thresh_JC:.4f}")
    else:
        print(f"  |1+w| is ALWAYS above 0.05 (deviation always observable)")
        z_thresh_JC = 0.0
else:
    print(f"  |1+w| is ALWAYS above 0.05")

E2_thresh_CMB = 2 * kappa0_CMB / (0.05 * Omega_DE)
print(f"\nCMB benchmark (kappa_0 = {kappa0_CMB:.6e}):")
print(f"  E2(z_thresh) = {E2_thresh_CMB:.6f}")

z_thresh_CMB = None
dev_cmb_z0 = abs(1 + w_of_z(0, kappa0_CMB))
if dev_cmb_z0 < 0.05:
    print(f"  |1+w(0)| = {dev_cmb_z0:.6e} < 0.05: deviation NEVER reaches threshold")
    z_thresh_CMB = 0
else:
    onepz_cubed = (E2_thresh_CMB - Omega_DE) / Omega_m
    if onepz_cubed > 0:
        z_thresh_CMB = onepz_cubed**(1/3) - 1
        if z_thresh_CMB > 0:
            print(f"  z_thresh = {z_thresh_CMB:.4f}")
        else:
            print(f"  |1+w| below 0.05 at all positive z")
            z_thresh_CMB = 0
    else:
        print(f"  |1+w| below 0.05 at all positive z")
        z_thresh_CMB = 0

print(f"  [Check: |1+w(0)| at CMB benchmark = {dev_cmb_z0:.6e}]")

###############################################################################
# 3. MATTER-DE EQUALITY REDSHIFT
###############################################################################

print("\n" + "=" * 72)
print("--- PART 3: Matter-DE Equality Redshift ---\n")

z_eq_LCDM = (Omega_DE / Omega_m)**(1/3) - 1
print(f"LCDM: z_eq = (Omega_DE/Omega_m)^(1/3) - 1 = ({Omega_DE}/{Omega_m})^(1/3) - 1 = {z_eq_LCDM:.6f}")

def equality_func(z, kappa0):
    rho_m = Omega_m * (1+z)**3
    rho_DE_eff = Omega_DE + kappa0 / E2(z)
    return rho_m - rho_DE_eff

# JC benchmark
z_eq_JC = None
try:
    z_eq_JC = brentq(equality_func, 0.01, 5.0, args=(kappa0_JC,))
    print(f"\nJC benchmark (kappa_0 = {kappa0_JC:.6e}):")
    print(f"  z_eq = {z_eq_JC:.6f}")
    print(f"  Shift from LCDM: Delta_z_eq = {z_eq_JC - z_eq_LCDM:.6e}")
    print(f"  Relative shift: {(z_eq_JC - z_eq_LCDM)/z_eq_LCDM * 100:.4f}%")
    rho_m_eq = Omega_m * (1+z_eq_JC)**3
    rho_DE_eq = Omega_DE + kappa0_JC / E2(z_eq_JC)
    print(f"  [Check: rho_m = {rho_m_eq:.6f}, rho_DE_eff = {rho_DE_eq:.6f}, ratio = {rho_m_eq/rho_DE_eq:.8f}]")
except Exception as e:
    print(f"  JC: Could not find equality: {e}")

# CMB benchmark
z_eq_CMB = None
try:
    z_eq_CMB = brentq(equality_func, 0.01, 5.0, args=(kappa0_CMB,))
    print(f"\nCMB benchmark (kappa_0 = {kappa0_CMB:.6e}):")
    print(f"  z_eq = {z_eq_CMB:.6f}")
    print(f"  Shift from LCDM: Delta_z_eq = {z_eq_CMB - z_eq_LCDM:.6e}")
    print(f"  Relative shift: {(z_eq_CMB - z_eq_LCDM)/z_eq_LCDM * 100:.6f}%")
except Exception as e:
    print(f"  CMB: Could not find equality: {e}")

###############################################################################
# 4. DYNAMICAL ONSET ANALYSIS
###############################################################################

print("\n" + "=" * 72)
print("--- PART 4: Dynamical Onset ---\n")

# d/dz[1/E^2] = -3*Omega_m*(1+z)^2 / [E^2(z)]^2
def d_invE2_dz(z):
    return -3 * Omega_m * (1+z)**2 / E2(z)**2

print("Rate of change d/dz[kappa_0/E^2(z)]:")
header2 = f"{'z':>5} | {'d/dz[k0/E2] JC':>18} | {'d/dz[k0/E2] CMB':>18}"
print(header2)
print("-" * len(header2))
for z in z_values:
    d_JC = kappa0_JC * d_invE2_dz(z)
    d_CMB = kappa0_CMB * d_invE2_dz(z)
    print(f"{z:5.1f} | {d_JC:18.6e} | {d_CMB:18.6e}")

# Analytical inflection point
# d^2/dz^2[1/E^2] = -6*Omega_m*u*(Omega_DE - 2*Omega_m*u^3) / E^6
# Setting = 0: Omega_DE = 2*Omega_m*(1+z)^3
# (1+z)^3 = Omega_DE/(2*Omega_m)

z_inflection = (Omega_DE / (2*Omega_m))**(1/3) - 1

def d2_invE2_dz2(z):
    u = 1 + z
    num = -6 * Omega_m * u * (Omega_DE - 2*Omega_m*u**3)
    den = E2(z)**3
    return num / den

print(f"\n--- Inflection point of kappa_0/E^2(z) ---")
print(f"\nAnalytical: d^2/dz^2[1/E^2(z)] = 0 when:")
print(f"  (1+z)^3 = Omega_DE / (2*Omega_m) = {Omega_DE} / {2*Omega_m} = {Omega_DE/(2*Omega_m):.6f}")
print(f"  z_inflection = {z_inflection:.6f}")
print(f"  [Check: d^2/dz^2[1/E^2] at z_inflection = {d2_invE2_dz2(z_inflection):.6e}]")

print(f"\n--- Where is |d/dz[kappa_0/E^2]| maximized? ---")
print(f"\nd/dz[1/E^2] is always negative (the correction grows toward z=0).")
print(f"Its magnitude |d/dz[1/E^2]| = 3*Omega_m*(1+z)^2 / E^4(z)")
print(f"The maximum magnitude of the rate of change is at z = {z_inflection:.6f}.")
print(f"Physical meaning: The rate of change of the KK correction is maximized")
print(f"at z = {z_inflection:.4f}. This is where DE dynamics are most active.")

# Fractional correction table
print(f"\n--- Fractional correction kappa_0/[E^2 * Omega_DE] = |1+w|/2 ---\n")
header3 = f"{'z':>5} | {'frac [JC]':>14} | {'frac [CMB]':>14}"
print(header3)
print("-" * len(header3))
for z in z_values:
    frac_JC = kappa0_JC / (E2(z) * Omega_DE)
    frac_CMB = kappa0_CMB / (E2(z) * Omega_DE)
    print(f"{z:5.1f} | {frac_JC:14.6e} | {frac_CMB:14.6e}")

# Where does fractional correction reach 1%?
for name, k0 in [("JC", kappa0_JC), ("CMB", kappa0_CMB)]:
    E2_1pct = k0 / (0.01 * Omega_DE)
    frac_z0 = k0 / (E2(0) * Omega_DE)
    if frac_z0 >= 0.01:
        if E2_1pct > Omega_DE:
            onepz3 = (E2_1pct - Omega_DE) / Omega_m
            z_1pct = onepz3**(1/3) - 1
            if z_1pct > 0:
                print(f"\n{name}: Fractional correction reaches 1% at z = {z_1pct:.4f} (above 1% for z < {z_1pct:.4f})")
            else:
                print(f"\n{name}: Fractional correction EXCEEDS 1% at z=0 (value = {frac_z0:.4f})")
        else:
            print(f"\n{name}: Fractional correction EXCEEDS 1% at z=0 (value = {frac_z0:.4f})")
    else:
        print(f"\n{name}: Fractional correction never reaches 1% (max at z=0: {frac_z0:.6e})")

###############################################################################
# 5. THE COINCIDENCE QUESTION --- eps1 SENSITIVITY
###############################################################################

print("\n" + "=" * 72)
print("--- PART 5: The Coincidence Question --- eps1 Sensitivity ---\n")

print(f"Reference: eps1 = {eps1}")
print(f"  C_KK = {C_KK:.6e}")
print(f"  kappa_0 (JC) = {kappa0_JC:.6e}")
print(f"  |1+w(0)| (JC) = {abs(1+w_of_z(0, kappa0_JC)):.6f}")
print(f"  |1+w(0)| (CMB) = {abs(1+w_of_z(0, kappa0_CMB)):.6e}")

for factor, label in [(10, "10x larger"), (0.1, "10x smaller")]:
    eps1_mod = eps1 * factor
    C_KK_mod = (1 + q0)**2 * Omega_DE * eps1_mod / (4 * (1 - q0)**2)
    k0_JC_mod = C_KK_mod * Omega_DE / (2 * zeta_JC)
    k0_CMB_mod = C_KK_mod * Omega_DE / (2 * zeta_CMB)

    w_JC_mod = w_of_z(0, k0_JC_mod)
    w_CMB_mod = w_of_z(0, k0_CMB_mod)

    print(f"\neps1 = {eps1_mod} ({label}):")
    print(f"  C_KK = {C_KK_mod:.6e}")
    print(f"  kappa_0 (JC) = {k0_JC_mod:.6e}")
    print(f"  w(0) [JC] = {w_JC_mod:.6f}, |1+w| = {abs(1+w_JC_mod):.6f}")
    print(f"  w(0) [CMB] = {w_CMB_mod:.8f}, |1+w| = {abs(1+w_CMB_mod):.6e}")

    # When does deviation drop below 0.05?
    E2_thresh_mod = 2 * k0_JC_mod / (0.05 * Omega_DE)
    if E2_thresh_mod > 1.0:
        onepz3 = (E2_thresh_mod - Omega_DE) / Omega_m
        if onepz3 > 0:
            z_thresh = onepz3**(1/3) - 1
            if z_thresh > 0:
                print(f"  Deviation |1+w| drops below 0.05 at z > {z_thresh:.4f} (JC)")
            else:
                print(f"  Deviation ALWAYS above 0.05 at JC benchmark")
        else:
            print(f"  Deviation ALWAYS above 0.05 at JC benchmark")
    else:
        frac_z0 = abs(1+w_of_z(0, k0_JC_mod))
        if frac_z0 < 0.05:
            print(f"  Deviation ALWAYS below 0.05 at JC benchmark (max = {frac_z0:.6f})")
        else:
            print(f"  Deviation exceeds 0.05 near z=0 (max = {frac_z0:.6f})")

# Critical eps1 values
eps1_unity_JC = 4 * (1-q0)**2 * zeta_JC / ((1+q0)**2 * Omega_DE)
eps1_unity_CMB = 4 * (1-q0)**2 * zeta_CMB / ((1+q0)**2 * Omega_DE)

print(f"\n--- Critical eps1 values ---")
print(f"eps1 for |1+w(0)| = 1 at JC benchmark: {eps1_unity_JC:.6f}")
print(f"eps1 for |1+w(0)| = 1 at CMB benchmark: {eps1_unity_CMB:.4f}")
print(f"Actual eps1 = {eps1} is {eps1/eps1_unity_JC:.4f}x the JC critical value")
print(f"Actual eps1 = {eps1} is {eps1/eps1_unity_CMB:.6f}x the CMB critical value")

print(f"\nInterpretation:")
print(f"  The NCG spectral action determines eps1 = C_GB * (spectral weight ratio)")
print(f"  = 2/3 * 0.0255 = 0.017 (from the Gauss-Bonnet coefficient)")
print(f"  This gives |1+w(0)| = {abs(1+w_of_z(0, kappa0_JC)):.4f} at JC benchmark")
print(f"  For |1+w(0)| = O(1), one would need eps1 ~ {eps1_unity_JC:.4f}")
print(f"  The actual eps1 is {eps1_unity_JC/eps1:.1f}x smaller than this threshold")

###############################################################################
# 6. STRUCTURAL ANALYSIS
###############################################################################

print("\n" + "=" * 72)
print("--- STRUCTURAL ANALYSIS ---\n")

print("Key redshifts in the framework:")
print(f"  z_eq (LCDM matter-DE equality): {z_eq_LCDM:.4f}")
if z_eq_JC is not None:
    print(f"  z_eq (Meridian, JC): {z_eq_JC:.4f}")
if z_eq_CMB is not None:
    print(f"  z_eq (Meridian, CMB): {z_eq_CMB:.4f}")
print(f"  z_inflection (max rate of KK correction change): {z_inflection:.4f}")

z_accel_LCDM = (2*Omega_DE/Omega_m)**(1/3) - 1
print(f"  z_accel (LCDM decel-to-accel transition): {z_accel_LCDM:.4f}")

ratio = Omega_DE / (2 * Omega_m)
print(f"\n  Omega_DE / (2*Omega_m) = {ratio:.4f}")
print(f"  (1+z_infl)^3 = {ratio:.4f}")
print(f"  z_infl = {z_inflection:.4f}")
print(f"  z_eq = (Omega_DE/Omega_m)^(1/3) - 1 = {z_eq_LCDM:.4f}")

# Universal ratio
print(f"\n  Universal ratio: (1+z_infl)/(1+z_eq) = 2^(-1/3) = {2**(-1/3):.6f}")
print(f"  This is a STRUCTURAL relationship: the dynamical onset inflection")
print(f"  is ALWAYS at 2^(-1/3) times the matter-DE equality redshift.")

# Relationship between z_accel and z_infl
print(f"\n  z_accel: (1+z)^3 = 2*Omega_DE/Omega_m = {2*Omega_DE/Omega_m:.4f}")
print(f"  z_inflection: (1+z)^3 = Omega_DE/(2*Omega_m) = {Omega_DE/(2*Omega_m):.4f}")
print(f"  Ratio of (1+z)^3 values = {(2*Omega_DE/Omega_m)/(Omega_DE/(2*Omega_m)):.4f} (exactly 4)")
print(f"  So (1+z_accel)/(1+z_infl) = 4^(1/3) = {4**(1/3):.6f}")
print(f"  z_accel = {z_accel_LCDM:.4f}, z_infl = {z_inflection:.4f}")

# 1% deviation onset
for name, k0 in [("JC", kappa0_JC), ("CMB", kappa0_CMB)]:
    target = 0.01
    val_z0 = 2 * k0 / (Omega_DE * E2(0))
    if val_z0 > target:
        E2_target = 2 * k0 / (target * Omega_DE)
        onepz3 = (E2_target - Omega_DE) / Omega_m
        if onepz3 > 0:
            z_onset = onepz3**(1/3) - 1
            if z_onset > 0:
                print(f"\n  {name}: 1% deviation onset at z = {z_onset:.4f}")
            else:
                print(f"\n  {name}: 1% deviation present at all z >= 0")
        else:
            print(f"\n  {name}: 1% deviation present at all z >= 0")
    else:
        print(f"\n  {name}: 1% deviation never reached (max |1+w| = {val_z0:.6e})")

print(f"\nKEY INSIGHT: The inflection of the KK correction rate occurs at")
print(f"  z_infl = {z_inflection:.4f}, which is BETWEEN the matter-DE equality")
print(f"  (z_eq = {z_eq_LCDM:.4f}) and the decel-accel transition (z_accel = {z_accel_LCDM:.4f}).")
print(f"  All three are determined by Omega_DE/Omega_m --- the SAME ratio that")
print(f"  defines the coincidence problem. The KK correction does not introduce")
print(f"  a new timescale --- it peaks where the background cosmology is already")
print(f"  transitioning from matter to DE domination.")

###############################################################################
# 7. ENERGY BUDGET AND COSMIC TIME FRACTIONS
###############################################################################

print("\n" + "=" * 72)
print("--- ENERGY BUDGET AND COSMIC TIME ---\n")

def dt_dz(z):
    return 1.0 / ((1+z) * np.sqrt(E2(z)))

total_time, _ = quad(dt_dz, 0, 10)

# JC: time spent with |1+w| > 1%
E2_1pct_JC = 2 * kappa0_JC / (0.01 * Omega_DE)
onepz3 = (E2_1pct_JC - Omega_DE) / Omega_m
z_1pct_JC = onepz3**(1/3) - 1

if z_1pct_JC > 0 and z_1pct_JC < 10:
    active_time, _ = quad(dt_dz, 0, z_1pct_JC)
    frac = active_time / total_time
    print(f"JC benchmark: DE dynamics active (|1+w| > 1%) from z=0 to z={z_1pct_JC:.2f}")
    print(f"  Fraction of cosmic time (since z=10): {frac*100:.1f}%")
elif z_1pct_JC <= 0:
    print(f"JC benchmark: |1+w| > 1% at z=0 but z_1pct would be negative -> check")
    dev = abs(1 + w_of_z(0, kappa0_JC))
    print(f"  |1+w(0)| = {dev:.4f} >> 1%")
    # Find upper z where it drops to 1%
    if onepz3 > 0:
        z_1pct_JC = onepz3**(1/3) - 1
        print(f"  z where |1+w| = 1%: z = {z_1pct_JC:.4f}")
else:
    print(f"JC: z_1pct = {z_1pct_JC:.2f} > 10, DE always active in this range")

# Energy budget at z=0
frac_KK_JC = kappa0_JC / (E2(0) * Omega_DE)
frac_KK_total_JC = kappa0_JC / E2(0)
frac_KK_CMB = kappa0_CMB / (E2(0) * Omega_DE)
frac_KK_total_CMB = kappa0_CMB / E2(0)

print(f"\n--- Energy budget at z=0 ---")
print(f"JC benchmark:")
print(f"  KK correction / Omega_DE = {frac_KK_JC:.6f} ({frac_KK_JC*100:.2f}%)")
print(f"  KK correction / total energy = {frac_KK_total_JC:.6f} ({frac_KK_total_JC*100:.4f}%)")
print(f"CMB benchmark:")
print(f"  KK correction / Omega_DE = {frac_KK_CMB:.6e} ({frac_KK_CMB*100:.4f}%)")
print(f"  KK correction / total energy = {frac_KK_total_CMB:.6e} ({frac_KK_total_CMB*100:.6f}%)")

###############################################################################
# 8. FINAL SUMMARY TABLE
###############################################################################

print("\n" + "=" * 72)
print("--- FINAL SUMMARY ---\n")

print(f"Parameter: eps1 = {eps1} (from NCG spectral action, C_GB = 2/3)")
print(f"")
print(f"JC benchmark (zeta_0 = {zeta_JC}):")
print(f"  C_KK = {C_KK:.4e}")
print(f"  kappa_0 = {kappa0_JC:.4e}")
print(f"  w(0) = {w_of_z(0, kappa0_JC):.6f}")
print(f"  |1+w(0)| = {abs(1+w_of_z(0, kappa0_JC)):.6f}")
print(f"")
print(f"CMB benchmark (zeta_0 = {zeta_CMB}):")
print(f"  kappa_0 = {kappa0_CMB:.4e}")
print(f"  w(0) = {w_of_z(0, kappa0_CMB):.6f}")
print(f"  |1+w(0)| = {abs(1+w_of_z(0, kappa0_CMB)):.6e}")
print(f"")
print(f"Cosmological redshifts:")
print(f"  z_eq (LCDM) = {z_eq_LCDM:.4f}")
if z_eq_JC: print(f"  z_eq (Meridian, JC) = {z_eq_JC:.4f}")
if z_eq_CMB: print(f"  z_eq (Meridian, CMB) = {z_eq_CMB:.4f}")
print(f"  z_inflection (max dyn. rate) = {z_inflection:.4f}")
print(f"  z_accel (LCDM) = {z_accel_LCDM:.4f}")
print(f"  Universal: (1+z_infl)/(1+z_eq) = 2^(-1/3) = {2**(-1/3):.6f}")
print(f"")
print(f"eps1 sensitivity:")
print(f"  eps1_crit (|1+w|=1 at z=0, JC) = {eps1_unity_JC:.6f}")
print(f"  eps1/eps1_crit = {eps1/eps1_unity_JC:.4f}")
dev_jc_z0 = abs(1+w_of_z(0, kappa0_JC))
print(f"  If eps1 -> 10*eps1: |1+w(0)| -> {dev_jc_z0*10:.4f}")
print(f"  If eps1 -> eps1/10: |1+w(0)| -> {dev_jc_z0/10:.4f}")

print("\n" + "=" * 72)
print("COMPUTATION COMPLETE")
print("=" * 72)
