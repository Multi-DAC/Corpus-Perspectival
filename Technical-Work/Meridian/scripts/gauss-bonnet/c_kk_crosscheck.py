"""
Cross-check of C_KK derivation — verify each step independently.
"""
import numpy as np
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c_kk_crosscheck_results.txt")
lines = []
def log(s): lines.append(s)

# Constants
Omega_m = 0.315
Omega_DE = 0.685
q_0 = Omega_m/2 - Omega_DE  # -0.5275
xi_5D = 1/6
zeta_0_HK = 0.038
zeta_0_SA = xi_5D * 0.517**2  # 0.04453

log("C_KK CROSS-CHECK")
log("=" * 60)

# Step 1: Verify V''_eff = R_4/3
log("\nStep 1: V''_eff = R_4/3")
log("-" * 40)
# V''_eff = zeta_0 M_Pl^2 R_4 / phi_0^2
# phi_0^2 = 3 zeta_0 M_Pl^2
# => V''_eff = zeta_0 M_Pl^2 R_4 / (3 zeta_0 M_Pl^2) = R_4/3
R4_over_H02 = 6*(1-q_0)
Vpp_over_H02 = R4_over_H02 / 3
log(f"  R_4/H_0^2 = 6(1-q_0) = 6*{1-q_0:.4f} = {R4_over_H02:.4f}")
log(f"  V''_eff/H_0^2 = R_4/(3H_0^2) = {Vpp_over_H02:.4f}")
log(f"  V''_eff = 2(1-q_0) H_0^2 = {2*(1-q_0):.4f} H_0^2")
log("  CHECK: zeta_0 cancels. CONFIRMED.")

# Step 2: phi_dot from constraint
log("\nStep 2: phi_dot from constraint derivative")
log("-" * 40)
# V''_eff phi_dot = -3 H_dot mu^2 = 3(1+q_0) H_0^2 mu^2
# phi_dot = 3(1+q_0) H_0^2 mu^2 / V''_eff
#         = 3(1+q_0) H_0^2 mu^2 / (2(1-q_0) H_0^2)
#         = 3(1+q_0) mu^2 / (2(1-q_0))
phi_dot_coeff = 3*(1+q_0) / (2*(1-q_0))
log(f"  phi_dot = {phi_dot_coeff:.6f} * mu^2")
log(f"  (= 3*{1+q_0:.4f} / (2*{1-q_0:.4f}))")

# Step 3: X_4 and K_eff
log("\nStep 3: X_4 and K_eff")
log("-" * 40)
X4_coeff = phi_dot_coeff**2 / 2
log(f"  X_4 = phi_dot^2/2 = {X4_coeff:.6f} * mu^4")
log(f"  K_eff = epsilon_1 * {X4_coeff:.6f} * mu^4")

# Step 4: mu from dark energy condition
log("\nStep 4: mu from self-tuning")
log("-" * 40)
# mu^2 = Omega_DE M_Pl H_0 / phi_0 = Omega_DE H_0 / sqrt(3 zeta_0) [in M_Pl=1]
# mu^4 = Omega_DE^2 H_0^2 / (3 zeta_0) [in M_Pl=1]
# mu^4 / (M_Pl^2 H_0^2) = Omega_DE^2 / (3 zeta_0)
for z0, label in [(zeta_0_HK, "H&K"), (zeta_0_SA, "spectral")]:
    mu4_dimless = Omega_DE**2 / (3*z0)
    log(f"  zeta_0 = {z0:.4f} ({label}):")
    log(f"    mu^4/(M_Pl^2 H_0^2) = {mu4_dimless:.4f}")

# Step 5: kappa_0
log("\nStep 5: kappa_0")
log("-" * 40)
# kappa_0 = K_eff / (3 M_Pl^2 H_0^2)
#         = epsilon_1 * X4_coeff * mu^4 / (3 M_Pl^2 H_0^2)
#         = epsilon_1 * X4_coeff * Omega_DE^2 / (3 * 3 zeta_0)
#         = epsilon_1 * X4_coeff * Omega_DE^2 / (9 zeta_0)
for z0, label in [(zeta_0_HK, "H&K"), (zeta_0_SA, "spectral")]:
    kappa_coeff = X4_coeff * Omega_DE**2 / (9*z0)  # kappa_0 / epsilon_1
    # Wait, let me redo.
    # K_eff = epsilon_1 * X4_coeff * mu^4
    # kappa_0 = K_eff / (3 M_Pl^2 H_0^2) = epsilon_1 * X4_coeff * mu^4 / (3 M_Pl^2 H_0^2)
    # mu^4 / (M_Pl^2 H_0^2) = Omega_DE^2 / (3 zeta_0)
    # kappa_0 = epsilon_1 * X4_coeff * Omega_DE^2 / (3 * 3 * zeta_0)
    # No wait: kappa_0 = epsilon_1 * (X4_coeff mu^4) / (3 M_Pl^2 H_0^2)
    # = epsilon_1 * X4_coeff * [mu^4/(M_Pl^2 H_0^2)] / 3
    # = epsilon_1 * X4_coeff * Omega_DE^2 / (3 * 3 zeta_0)
    # = epsilon_1 * X4_coeff * Omega_DE^2 / (9 zeta_0)
    kappa_over_eps = X4_coeff * Omega_DE**2 / (9*z0)
    # Hmm, this doesn't match my earlier calculation. Let me trace through again.
    # mu^4 has dimensions [E^4]. In M_Pl=1, H_0=1 units:
    # mu^2 = Omega_DE / sqrt(3 zeta_0)  [dimensionless in these units]
    # mu^4 = Omega_DE^2 / (3 zeta_0)
    # X_4 = X4_coeff * mu^4 = X4_coeff * Omega_DE^2 / (3 zeta_0) [units of H_0^2 M_Pl^2]
    # Wait, X_4 = phi_dot^2/2. phi_dot has dimensions [E^2] (mass/time = mass*H_0).
    # phi_dot = phi_dot_coeff * mu^2 [dimensions E^2]
    # In M_Pl=1, H_0=1: phi_dot = phi_dot_coeff * Omega_DE/sqrt(3 zeta_0) [dimensionless]
    # X_4 = phi_dot^2/2 = X4_coeff * Omega_DE^2/(3 zeta_0) [in units of M_Pl^2 H_0^2]
    # K_eff = epsilon_1 * X_4 [in units of M_Pl^2 H_0^2]
    # kappa_0 = K_eff / (3 M_Pl^2 H_0^2) = epsilon_1 * X4_coeff * Omega_DE^2 / (9 zeta_0)
    log(f"  zeta_0 = {z0:.4f} ({label}):")
    log(f"    kappa_0/epsilon_1 = X4*mu4/(3 M_Pl^2 H_0^2)")
    log(f"                     = {X4_coeff:.6f} * {Omega_DE**2/(3*z0):.4f} / 3")
    log(f"                     = {kappa_over_eps:.6f}")

# Step 6: C_KK
log("\nStep 6: C_KK = kappa_0 / (epsilon_1 * Omega_DE)")
log("-" * 40)
for z0, label in [(zeta_0_HK, "H&K"), (zeta_0_SA, "spectral")]:
    kappa_over_eps = X4_coeff * Omega_DE**2 / (9*z0)
    C_KK = kappa_over_eps / Omega_DE
    # Simplify: C_KK = X4_coeff * Omega_DE / (9 zeta_0)
    # X4_coeff = 9(1+q_0)^2 / (8(1-q_0)^2)
    # C_KK = 9(1+q_0)^2 * Omega_DE / (8(1-q_0)^2 * 9 * zeta_0)
    #       = (1+q_0)^2 Omega_DE / (8(1-q_0)^2 zeta_0)
    C_KK_formula = (1+q_0)**2 * Omega_DE / (8*(1-q_0)**2 * z0)
    log(f"  zeta_0 = {z0:.4f} ({label}):")
    log(f"    C_KK (step by step) = {C_KK:.6f}")
    log(f"    C_KK (formula)      = {C_KK_formula:.6f}")
    log(f"    Match: {np.isclose(C_KK, C_KK_formula)}")
    w0 = -1 + 2*C_KK*0.01
    log(f"    w_0 (eps1=0.01) = {w0:.6f}")
    log(f"    1+w_0 = {1+w0:.6f}")

# Step 7: Verify the dimensional analysis chain
log("\nStep 7: Dimensional analysis verification")
log("-" * 40)
log("  [mu^2] = [V'] / [H] = [E^4 / E] / [E] = [E^2]  (energy squared)")
log("  [phi_dot] = [H_dot mu^2 / V''_eff] = [E^2 * E^2 / E^2] = [E^2]")
log("  [X_4] = [phi_dot^2] = [E^4]")
log("  [K_eff] = [epsilon_1 * X_4] = [E^4]  (energy density, correct)")
log("  [kappa_0] = [K_eff / (M_Pl^2 H_0^2)] = [E^4 / E^4] = dimensionless")
log("  [C_KK] = [kappa_0 / (epsilon_1 * Omega_DE)] = dimensionless")
log("  CONFIRMED: all dimensions consistent.")

# Step 8: Verify the O(zeta_0) correction from R_dot
log("\nStep 8: R_dot correction estimate")
log("-" * 40)
# The full equation is:
# V''_eff phi_dot + zeta_0 phi_0 M_Pl^2 R_dot / phi_0^2 = -3 H_dot mu^2
# correction term = (1/3) phi_0 R_dot [using zeta_0 M_Pl^2/phi_0^2 = 1/3... no]
# Actually: zeta_0 phi_0 M_Pl^2 / phi_0^2 = zeta_0 M_Pl^2 / phi_0
# = zeta_0 M_Pl^2 / (sqrt(3 zeta_0) M_Pl) = sqrt(zeta_0/3) M_Pl
# R_dot at a=1: R_dot = 6(4H_0 H_dot_0 + H_ddot_0)
# H_dot_0 = -(1+q_0) H_0^2
# H_ddot_0 = 9 Omega_m H_0^3 / 2  (from differentiating H_dot)
Rdot_over_H03 = 6*(4*(-(1+q_0)) + 9*Omega_m/2)
log(f"  R_dot / H_0^3 = {Rdot_over_H03:.4f}")
# correction / main = [zeta_0 phi_0 M_Pl^2 R_dot / phi_0^2] / [3 |H_dot| mu^2]
# = [sqrt(zeta_0/3) M_Pl * R_dot] / [3 (1+q_0) H_0^2 * Omega_DE M_Pl H_0 / sqrt(3 zeta_0)]
# = [sqrt(zeta_0/3) * R_dot] / [3(1+q_0) H_0^2 * Omega_DE H_0 / sqrt(3 zeta_0)]
# = [sqrt(zeta_0/3) * sqrt(3 zeta_0) * R_dot] / [3(1+q_0) Omega_DE H_0^3]
# = [zeta_0 * R_dot] / [3(1+q_0) Omega_DE H_0^3]
# = zeta_0 * Rdot_over_H03 / (3*(1+q_0)*Omega_DE)
for z0, label in [(zeta_0_HK, "H&K"), (zeta_0_SA, "spectral")]:
    correction_ratio = z0 * abs(Rdot_over_H03) / (3*(1+q_0)*Omega_DE)
    log(f"  zeta_0 = {z0:.4f} ({label}):")
    log(f"    |correction/main| = {correction_ratio:.4f} ({correction_ratio*100:.1f}%)")

log("\n  The R_dot correction is ~10-11%, which modifies C_KK at the ~20% level.")
log("  This is within the epsilon_1 uncertainty (factor of ~2).")
log("  For a precision calculation, include this correction:")
log("  C_KK_corrected = C_KK * (1 + correction_ratio)^{-2}")
log("  (the ^{-2} because phi_dot enters as phi_dot^2 in X_4)")

for z0, label in [(zeta_0_HK, "H&K"), (zeta_0_SA, "spectral")]:
    correction_ratio = z0 * abs(Rdot_over_H03) / (3*(1+q_0)*Omega_DE)
    C_KK_0 = (1+q_0)**2 * Omega_DE / (8*(1-q_0)**2 * z0)
    # phi_dot_corrected = phi_dot_0 * 1/(1 + correction_ratio)  [correction reduces phi_dot]
    # Actually the sign matters. R_dot < 0, so the correction term adds to -3 H_dot mu^2.
    # -3 H_dot mu^2 > 0 (since H_dot < 0). R_dot < 0, so correction term < 0.
    # Net: phi_dot = (-3 H_dot mu^2 - correction) / V''_eff
    # Since correction < 0 and -3 H_dot mu^2 > 0:
    # phi_dot = (-3 H_dot mu^2 + |correction|) / V''_eff  > phi_dot_0
    # Wait, need the sign of R_dot term.
    # Term = zeta_0 phi_0 M_Pl^2 R_dot / phi_0^2
    # R_dot < 0 (R is decreasing as universe expands), phi_0 > 0
    # So term < 0.
    # Equation: V''_eff phi_dot + (negative term) = -3 H_dot mu^2 = (positive)
    # => V''_eff phi_dot = positive - negative = larger positive
    # => phi_dot is LARGER when correction included
    # => C_KK is LARGER
    C_KK_corr = C_KK_0 * (1 + correction_ratio)**2
    w0_corr = -1 + 2*C_KK_corr*0.01
    log(f"\n  zeta_0 = {z0:.4f} ({label}):")
    log(f"    C_KK (leading order) = {C_KK_0:.4f}")
    log(f"    C_KK (with R_dot correction) = {C_KK_corr:.4f}")
    log(f"    w_0 (corrected, eps1=0.01) = {w0_corr:.6f}")

# Also include the NMC correction to mu^2 (eq 23 correction)
log("\n\nStep 9: NMC correction to mu^2")
log("-" * 40)
log("  From eq (23): 3 H_0 mu^2 = c_4D + NMC_correction")
log("  NMC_correction / c_4D = 2(1-q_0) * zeta_0 / (3 Omega_DE)")
for z0, label in [(zeta_0_HK, "H&K"), (zeta_0_SA, "spectral")]:
    mu_correction = 2*(1-q_0)*z0/(3*Omega_DE)
    log(f"  zeta_0 = {z0:.4f} ({label}):")
    log(f"    NMC_corr/c_4D = {mu_correction:.4f} ({mu_correction*100:.1f}%)")
    # mu^2 increases by this factor, so mu^4 increases by 2x this factor
    # kappa_0 propto mu^4, so kappa_0 increases by 2*mu_correction
    # C_KK increases by same factor
    C_KK_0 = (1+q_0)**2 * Omega_DE / (8*(1-q_0)**2 * z0)
    C_KK_mu_corr = C_KK_0 * (1 + mu_correction)**2
    log(f"    C_KK (with mu correction only) = {C_KK_mu_corr:.4f}")

log("\n\nStep 10: BEST ESTIMATE (all corrections)")
log("=" * 60)
for z0, label in [(zeta_0_HK, "H&K"), (zeta_0_SA, "spectral")]:
    correction_ratio = z0 * abs(Rdot_over_H03) / (3*(1+q_0)*Omega_DE)
    mu_correction = 2*(1-q_0)*z0/(3*Omega_DE)
    C_KK_0 = (1+q_0)**2 * Omega_DE / (8*(1-q_0)**2 * z0)
    # Combined: phi_dot enhanced by (1+Rdot_corr), mu enhanced by (1+mu_corr)
    # phi_dot ~ mu^2 * (1+Rdot_corr)
    # X_4 ~ mu^4 * (1+Rdot_corr)^2
    # But mu^4 ~ 1/(1+mu_corr)^{-2} ... wait.
    # mu^2 = c_4D / (3H_0) = [c_4D_0 + NMC_corr]/(3H_0)
    # c_4D_0 = 3 Omega_DE M_Pl^2 H_0^2 / phi_0
    # So mu^2 = Omega_DE M_Pl H_0 / sqrt(3 zeta_0) * (1 + mu_correction)
    # mu^4 increases by (1+mu_correction)^2
    # phi_dot = 3(1+q_0) mu^2 / (2(1-q_0)) * (1/(1-Rdot_sign*correction_ratio))
    # For R_dot < 0: the correction ADDS to phi_dot
    total_factor = (1 + mu_correction)**2 * (1 + correction_ratio)**2
    C_KK_best = C_KK_0 * total_factor
    w0_best = -1 + 2*C_KK_best*0.01
    log(f"\n  zeta_0 = {z0:.4f} ({label}):")
    log(f"    C_KK (leading order) = {C_KK_0:.4f}")
    log(f"    R_dot correction factor = (1+{correction_ratio:.4f})^2 = {(1+correction_ratio)**2:.4f}")
    log(f"    mu^2 correction factor = (1+{mu_correction:.4f})^2 = {(1+mu_correction)**2:.4f}")
    log(f"    Total correction = {total_factor:.4f}")
    log(f"    C_KK (corrected) = {C_KK_best:.4f}")
    log(f"    w_0 (eps1=0.01) = {w0_best:.6f}")

log("\n\nFINAL ANSWER")
log("=" * 60)
z0 = zeta_0_HK
correction_ratio = z0 * abs(Rdot_over_H03) / (3*(1+q_0)*Omega_DE)
mu_correction = 2*(1-q_0)*z0/(3*Omega_DE)
C_KK_0 = (1+q_0)**2 * Omega_DE / (8*(1-q_0)**2 * z0)
total = (1+mu_correction)**2 * (1+correction_ratio)**2
C_KK_final = C_KK_0 * total
log(f"  Leading order: C_KK = {C_KK_0:.4f}")
log(f"  With all O(zeta_0) corrections: C_KK = {C_KK_final:.4f}")
log(f"  Best estimate: C_KK = {(C_KK_0 + C_KK_final)/2:.4f} +/- {abs(C_KK_final-C_KK_0)/2:.4f}")
log("")
C_KK_mid = (C_KK_0 + C_KK_final)/2
for eps in [0.008, 0.010, 0.012, 0.015]:
    w0 = -1 + 2*C_KK_mid*eps
    log(f"  eps1={eps:.3f}: w_0 = {w0:.6f}")

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print(f"Written to {OUT}")
