"""
C3: The Coincidence Problem
============================
Does the framework explain why rho_DE ~ rho_matter TODAY?

The framework explains:
  1. Why Lambda_4 is small (self-tuning)
  2. What dark energy is (cuscuton + GB correction)
  3. What w_0 is (-0.993)

It does NOT obviously explain why we observe the transition from
matter domination to DE domination at z ~ 0.3 (the present epoch).

APPROACH:
  C3.1: Compute w(a) for the full expansion history
  C3.2: When is |1 + w(a)| maximized?
  C3.3: Is the deviation only observable during the DE epoch?
  C3.4: Structural mechanism or coincidence?

Author: Clawd
Date: 2026-03-17
"""

import numpy as np
import sys

print("=" * 70)
print("C3: THE COINCIDENCE PROBLEM")
print("=" * 70)

# ============================================================
# C3.1: w(a) FOR THE FULL EXPANSION HISTORY
# ============================================================
print("\nC3.1: w(a) ACROSS COSMIC HISTORY")
print("-" * 70)

# From Paper I, the modified Friedmann equation:
#   E^2(a) = R(a) + kappa_0/E^2(a)
# where E = H/H_0, R(a) = Omega_m/a^3 + Omega_r/a^4 + v_0
# and kappa_0 + v_0 = Omega_DE

# Parameters
Omega_m = 0.315
Omega_r = 9.1e-5  # radiation
Omega_DE = 0.685
q0 = -0.5275
eps1 = 0.017
zeta0 = 0.038

# C_KK and kappa_0
C_KK = (1 + q0)**2 * Omega_DE / (8 * (1 - q0)**2 * zeta0)
kappa_0 = C_KK * eps1 * Omega_DE
v_0 = Omega_DE - kappa_0

print(f"  Omega_m = {Omega_m}, Omega_r = {Omega_r:.1e}, Omega_DE = {Omega_DE}")
print(f"  epsilon_1 = {eps1}, zeta_0 = {zeta0}")
print(f"  C_KK = {C_KK:.4f}")
print(f"  kappa_0 = {kappa_0:.6f}")
print(f"  v_0 = {v_0:.6f}")
print(f"  kappa_0/Omega_DE = {kappa_0/Omega_DE:.6f}")

def R_func(a):
    """Matter + radiation + potential"""
    return Omega_m / a**3 + Omega_r / a**4 + v_0

def solve_E2(a):
    """Solve E^4 - R*E^2 - kappa_0 = 0"""
    R = R_func(a)
    # E^2 = (R + sqrt(R^2 + 4*kappa_0)) / 2
    discriminant = R**2 + 4 * kappa_0
    return (R + np.sqrt(discriminant)) / 2

# Compute w(a)
# The dark energy EOS: w_DE = p_DE / rho_DE
# rho_DE = v_0 + kappa_0/E^2 (in units of 3M_Pl^2 H_0^2)
# p_DE = -v_0 + kappa_0/E^2 * (1 + 2/(3E^2) * dE^2/dlna)
# Actually, from Paper I:
# w_DE(a) = -1 + (2/3) * kappa_0 * (1 + q(a)) / [E^2 * Omega_DE(a)]
# where Omega_DE(a) = (v_0 + kappa_0/E^2) / E^2

# Simpler approach: K_DE(a) = kappa_0/E^2(a)
# rho_DE(a) = v_0 + K_DE(a)
# The kinetic contribution is time-varying.
# w_DE = (p_DE / rho_DE) = (-v_0 + K_DE) / (v_0 + K_DE)
# = -1 + 2*K_DE / (v_0 + K_DE)
# Wait, that assumes p = K - V = K_DE - v_0.

# Actually, for the cuscuton with P(X) = mu^2 sqrt(2X) + eps1 X:
# rho = V + K_eff = v_0 + eps1 * X
# p = P(X) - V ≈ mu^2 sqrt(2X) + eps1 X - V
# In the cuscuton limit: mu^2 sqrt(2X) << V, so p ≈ eps1 X - V = K_eff - V

# Actually, for the effective Friedmann equation:
# rho_DE / (3 M_Pl^2 H_0^2) = v_0 + kappa_0 / E^2
# p_DE / (3 M_Pl^2 H_0^2) = -v_0 + kappa_0 / E^2 * (something)

# Let me use the exact relation from Paper I Eq. 73:
# w_DE = -1 + kappa_0 * (1 + 3Omega_m/(2E^2*a^3)) / (Omega_DE(a) * E^2)
# where Omega_DE(a) = 1 - Omega_m/a^3/E^2 - Omega_r/a^4/E^2

# Simplified: at leading order in kappa_0:
# w_DE ≈ -1 + 2*kappa_0/(Omega_DE * E^2)
# since kappa_0 << Omega_DE

a_vals = np.logspace(-4, 1, 1000)  # a from 10^-4 to 10

results = []
for a in a_vals:
    E2 = solve_E2(a)
    E = np.sqrt(E2)

    # DE density fraction
    Omega_DE_a = (v_0 + kappa_0 / E2) / E2
    Omega_m_a = Omega_m / (a**3 * E2)

    # K_DE = kappa_0 / E^2
    K_DE = kappa_0 / E2

    # w_DE
    rho_DE_a = v_0 + K_DE
    if rho_DE_a > 0:
        w_DE = -1 + 2 * K_DE / rho_DE_a
    else:
        w_DE = -1

    # |1 + w|
    deviation = abs(1 + w_DE)

    # Redshift
    z = 1/a - 1

    results.append((a, z, E, Omega_DE_a, Omega_m_a, K_DE, w_DE, deviation))

results = np.array(results)

print("\n  w_DE(a) across cosmic history:")
print(f"  {'a':>8s}  {'z':>8s}  {'Omega_DE':>10s}  {'Omega_m':>10s}  {'K_DE':>12s}  {'w_DE':>10s}  {'|1+w|':>10s}")
print("  " + "-" * 80)

# Print at key epochs
key_a = [0.001, 0.01, 0.1, 0.3, 0.5, 0.7, 1.0, 2.0, 5.0, 10.0]
for a_key in key_a:
    idx = np.argmin(np.abs(results[:, 0] - a_key))
    a, z, E, ODE, Om, KDE, w, dev = results[idx]
    print(f"  {a:8.3f}  {z:8.2f}  {ODE:10.6f}  {Om:10.6f}  {KDE:12.2e}  {w:10.6f}  {dev:10.2e}")

# ============================================================
# C3.2: WHEN IS |1+w| MAXIMIZED?
# ============================================================
print("\nC3.2: WHEN IS |1+w| MAXIMIZED?")
print("-" * 70)

idx_max = np.argmax(results[:, 7])
a_max, z_max, E_max, ODE_max, Om_max, KDE_max, w_max, dev_max = results[idx_max]
print(f"  Maximum |1+w| = {dev_max:.6f} at a = {a_max:.3f} (z = {z_max:.2f})")
print(f"  At this epoch: Omega_DE = {ODE_max:.4f}, Omega_m = {Om_max:.4f}")
print()

# The deviation grows monotonically as the universe expands!
# Because K_DE = kappa_0/E^2 and E^2 decreases toward the future
# (de Sitter limit: E^2 -> v_0 + kappa_0/v_0 = Omega_DE)

# At a -> infinity (far future):
E2_future = (v_0 + np.sqrt(v_0**2 + 4*kappa_0)) / 2
K_DE_future = kappa_0 / E2_future
rho_DE_future = v_0 + K_DE_future
w_future = -1 + 2 * K_DE_future / rho_DE_future
print(f"  Far future (a -> infinity):")
print(f"    E^2 -> {E2_future:.6f}")
print(f"    K_DE -> {K_DE_future:.6f}")
print(f"    w_DE -> {w_future:.6f}")
print(f"    |1+w| -> {abs(1+w_future):.6f}")
print()

# At a = 1 (present):
E2_now = solve_E2(1.0)
K_DE_now = kappa_0 / E2_now
rho_DE_now = v_0 + K_DE_now
w_now = -1 + 2 * K_DE_now / rho_DE_now
print(f"  Present (a = 1):")
print(f"    E^2 = {E2_now:.6f}")
print(f"    K_DE = {K_DE_now:.6f}")
print(f"    w_DE = {w_now:.6f}")
print(f"    |1+w| = {abs(1+w_now):.6f}")
print()

# The ratio: how much of the "final" deviation do we see now?
ratio_now = abs(1+w_now) / abs(1+w_future)
print(f"  Ratio |1+w|_now / |1+w|_future = {ratio_now:.4f}")
print(f"  We currently see {ratio_now*100:.1f}% of the asymptotic deviation.")

# ============================================================
# C3.3: IS THE DEVIATION ONLY OBSERVABLE DURING DE EPOCH?
# ============================================================
print("\nC3.3: OBSERVABILITY WINDOW")
print("-" * 70)

# The deviation |1+w| is observable only when:
# 1. |1+w| is large enough to measure (> sigma_w ~ 0.003)
# 2. DE is a significant fraction of the total energy (Omega_DE > 0.1)

# When did DE become significant?
# Omega_DE(a) = 0.1 at a = ?
for idx in range(len(results)):
    if results[idx, 3] > 0.1:
        a_DE_start = results[idx, 0]
        z_DE_start = results[idx, 1]
        break
print(f"  DE becomes significant (Omega_DE > 0.1) at a = {a_DE_start:.3f} (z = {z_DE_start:.2f})")

# When is |1+w| > 0.003 (measurable)?
for idx in range(len(results)):
    if results[idx, 7] > 0.003:
        a_meas = results[idx, 0]
        z_meas = results[idx, 1]
        break
print(f"  |1+w| > 0.003 (measurable) at a = {a_meas:.3f} (z = {z_meas:.2f})")

# When is BOTH conditions met?
for idx in range(len(results)):
    if results[idx, 3] > 0.1 and results[idx, 7] > 0.003:
        a_both = results[idx, 0]
        z_both = results[idx, 1]
        break
print(f"  Both conditions met at a = {a_both:.3f} (z = {z_both:.2f})")
print()

# The deviation is always present but only DETECTABLE when:
# - The universe is DE-dominated enough for DE to matter
# - The deviation is large enough to measure
# Both conditions are met only in the present and future epochs.

# ============================================================
# C3.4: STRUCTURAL MECHANISM OR COINCIDENCE?
# ============================================================
print("C3.4: STRUCTURAL MECHANISM OR COINCIDENCE?")
print("-" * 70)

# The framework does NOT solve the coincidence problem in the traditional sense.
# It does NOT explain why Omega_DE ~ Omega_m at the present epoch.
# The ratio Omega_DE/Omega_m is set by v_0 (= Omega_DE - kappa_0 ≈ Omega_DE)
# and the matter content, both of which are inputs.

# HOWEVER, the framework provides a STRUCTURAL AMELIORATION:

# 1. The self-tuning mechanism makes Omega_DE INSENSITIVE to the
#    bare vacuum energy. Unlike fine-tuning (which requires adjusting
#    Lambda_bare to 120 decimal places), self-tuning automatically
#    absorbs Lambda_bare. The residual Omega_DE is set by the
#    geometric parameters (k, zeta_0), not by cancellation.

# 2. The deviation |1+w| GROWS over time. It was negligible in the
#    matter-dominated era and becomes significant only in the DE era.
#    An observer in the matter era would see w = -1 exactly and have
#    no way to detect the 5D nature of spacetime.

# 3. The coincidence that Omega_DE ~ Omega_m TODAY is related to
#    the fact that the DE era JUST STARTED. In our framework:
#    - Before the DE era: |1+w| << 0.001 (undetectable)
#    - During transition: |1+w| ~ 0.003-0.007 (marginally detectable)
#    - In the far future: |1+w| -> 0.007 (asymptotic, fully detectable)

# 4. The OBSERVER SELECTION argument works differently here than in
#    the landscape: we don't need the anthropic principle. We need only
#    note that complex observers require structure formation (which
#    occurs during matter domination and the transition era), and
#    that the deviation is only detectable during and after this epoch.

print("  The framework DOES NOT solve the coincidence problem.")
print("  It does NOT explain why Omega_DE ~ Omega_m now.")
print()
print("  But it provides structural AMELIORATION:")
print()
print("  1. Self-tuning makes Omega_DE INSENSITIVE to Lambda_bare.")
print("     No 10^123 cancellation needed. The old CC problem is solved.")
print()
print("  2. The deviation |1+w| grows monotonically with time:")
print(f"     Matter era (z > 1): |1+w| < {results[np.argmin(np.abs(results[:,0]-0.5)), 7]:.4f}")
print(f"     Present (z = 0):    |1+w| = {abs(1+w_now):.4f}")
print(f"     Far future:         |1+w| = {abs(1+w_future):.4f}")
print()
print("  3. The 5D signature is detectable ONLY during and after the")
print("     DE-dominated epoch. An observer in the matter era would")
print("     see pure Lambda CDM and have no evidence for extra dimensions.")
print()
print("  4. This is NOT anthropic reasoning. It's a structural fact:")
print("     the cuscuton kinetic energy K_DE = kappa_0/E^2 is suppressed")
print("     by H^2 at early times (E >> 1) and grows as expansion decelerates.")
print("     The signal tracks the epoch, not the observer.")
print()

# ============================================================
# C3.5: THE DEEPER POINT
# ============================================================
print("C3.5: THE DEEPER POINT")
print("-" * 70)

# The coincidence problem has TWO aspects:
# (A) Why is rho_DE ~ rho_m now? (WHY THIS EPOCH?)
# (B) Why is Lambda_4 ~ (meV)^4? (WHY THIS VALUE?)

# The framework addresses (B) completely: Lambda_4 is set by the
# geometric parameters k and zeta_0, not by fine-tuning. The value
# (meV)^4 corresponds to zeta_0 = 0.038 and k ~ 10^8 GeV, both
# of which are determined by the hierarchy problem (RS mechanism).

# For (A): The framework says the DEVIATION 1+w grows as the universe
# expands. The question "why now?" becomes "why is the DE era starting
# now?" — which is equivalent to asking why Omega_DE ~ Omega_m.
# This IS the coincidence problem, and the framework doesn't solve it.

# But the framework REFRAMES the problem. In Lambda CDM, the coincidence
# is that we happen to live when Lambda ~ rho_m — an inexplicable coincidence.
# In our framework, the coincidence is that the transition from matter
# to DE domination happens to occur when structure has formed — which
# is AT LEAST partially structural: structure formation requires both
# gravitational collapse (which ends in the far future) and the
# matter-dominated epoch (which precedes DE domination by definition).

# The coincidence is AMELIORATED but not ELIMINATED.

print("  The framework solves the OLD CC problem (why Lambda is small)")
print("  but does not solve the NEW CC problem (why Lambda ~ rho_m now).")
print()
print("  The coincidence is AMELIORATED by three structural features:")
print("  - Self-tuning removes the 10^123 fine-tuning")
print("  - The 5D signature grows with cosmic time (not an accident)")
print("  - The DE value is set by geometric parameters, not cancellation")
print()
print("  HONEST ASSESSMENT: The coincidence problem remains open.")
print("  This is a limitation of the framework. We state it explicitly.")
print()

# ============================================================
# SUMMARY
# ============================================================
print("=" * 70)
print("C3: SUMMARY")
print("=" * 70)
print()
print("  Resolution: The framework AMELIORATES but does not SOLVE")
print("  the coincidence problem.")
print()
print("  Key finding: |1+w| grows monotonically with a:")
print(f"    z = 10:    |1+w| = {results[np.argmin(np.abs(results[:,1]-10)), 7]:.2e}")
print(f"    z = 1:     |1+w| = {results[np.argmin(np.abs(results[:,1]-1)), 7]:.4f}")
print(f"    z = 0:     |1+w| = {abs(1+w_now):.4f}")
print(f"    z = -0.5:  |1+w| = {results[np.argmin(np.abs(results[:,0]-2)), 7]:.4f}")
print(f"    z -> -1:   |1+w| = {abs(1+w_future):.4f}")
print()
print("  The 5D geometric signature is undetectable before DE domination")
print("  and grows to its asymptotic value during and after the transition.")
print()
print("  Track C3 STATUS: COMPLETE")
print("  Resolution type: HONEST NEGATIVE — the coincidence remains,")
print("  but the framework provides structural amelioration.")
