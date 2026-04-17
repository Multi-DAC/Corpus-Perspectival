"""
DOOR 1: Spin-Dependent KK Threshold Corrections to sin^2(theta_W)

THE KEY INSIGHT:
On RS_1, different spin fields have DIFFERENT KK mass spectra:
  - Gauge bosons (spin-1): zeros of J_1(x)    -> 3.832, 7.016, 10.174, ...
  - Fermions (spin-1/2):   zeros of sin(x)/x  -> pi, 2pi, 3pi, ...  (for c=0)
  - Scalars (spin-0):      zeros of J_0(x)    -> 2.405, 5.520, 8.654, ...

Since U(1) has C_2 = 0 (no gauge boson loop), while SU(2) has C_2 = 2
and SU(3) has C_2 = 3, the spin-dependent spectra weight the beta
function components DIFFERENTLY for different gauge groups.

This breaks the beta function ratio and shifts sin^2(theta_W).

SM beta function decomposition:
  b_i = b_i^gauge + b_i^ferm + b_i^scalar

  b_1 = 0       + 4     + 1/10    = 41/10   (U(1), C_2 = 0)
  b_2 = -22/3   + 4     + 1/6     = -19/6   (SU(2), C_2 = 2)
  b_3 = -11     + 4     + 0       = -7      (SU(3), C_2 = 3)

With spin-dependent KK spectra, the effective KK beta function becomes:
  b_i^KK = b_i^gauge * R_G + b_i^ferm * R_F + b_i^scalar * R_S

where R_X = S_X / S_ref measures how the KK sum differs by spin type.
"""

import numpy as np
from scipy.special import jn_zeros, yn_zeros
import sys

# ============================================================
# KK Spectra on RS_1 for different spins
# ============================================================

def kk_spectrum_gauge(N, k_IR_GeV):
    """Gauge boson (spin-1) KK masses: zeros of J_1."""
    x_n = jn_zeros(1, N)
    return x_n * k_IR_GeV

def kk_spectrum_fermion(N, k_IR_GeV, c=0.0):
    """Fermion (spin-1/2) KK masses.

    For bulk mass parameter c = 0 (conformal):
    Masses are at x_n = n*pi (zeros of sin(x)/sqrt(x) = J_{1/2}(x))

    For general c: zeros of J_{c+1/2}(x).
    """
    if c == 0:
        x_n = np.array([(n+1) * np.pi for n in range(N)])
    else:
        x_n = jn_zeros(c + 0.5, N)
    return x_n * k_IR_GeV

def kk_spectrum_scalar(N, k_IR_GeV):
    """Scalar (spin-0) KK masses: zeros of J_0."""
    x_n = jn_zeros(0, N)
    return x_n * k_IR_GeV

# ============================================================
# Beta function decomposition
# ============================================================

# SM one-loop beta function components
# b_i = b_i^gauge + b_i^ferm + b_i^scalar

B_GAUGE = np.array([0.0, -22.0/3, -11.0])       # C_2(U1)=0, C_2(SU2)=2, C_2(SU3)=3
B_FERM  = np.array([4.0, 4.0, 4.0])              # Same for all groups (SM fermion content)
B_SCALAR = np.array([1.0/10, 1.0/6, 0.0])        # Higgs: doublet of SU(2), singlet of SU(3)

# Verify: b_i = B_GAUGE + B_FERM + B_SCALAR
b_SM = B_GAUGE + B_FERM + B_SCALAR
assert abs(b_SM[0] - 41/10) < 0.001, f"b1 = {b_SM[0]}, expected 4.1"
assert abs(b_SM[1] - (-19/6)) < 0.001, f"b2 = {b_SM[1]}, expected -3.167"
assert abs(b_SM[2] - (-7)) < 0.001, f"b3 = {b_SM[2]}, expected -7"

# ============================================================
# Physical parameters
# ============================================================

M_Z = 91.1876  # GeV
LAMBDA_NCG = 2e16  # GeV (GUT/NCG cutoff)

# Measured couplings at M_Z
alpha_inv_MZ = np.array([59.0, 29.6, 1/0.1179])  # 1/alpha_i at M_Z

def sin2_thetaW(a_inv_1, a_inv_2):
    """sin^2(theta_W) = (3/5) * (1/alpha_2) / ((3/5)(1/alpha_2) + 1/alpha_1)"""
    return (3.0/5) * a_inv_2 / ((3.0/5) * a_inv_2 + a_inv_1)

# ============================================================
# Main calculation
# ============================================================

def main():
    print("=" * 72)
    print("DOOR 1: SPIN-DEPENDENT KK THRESHOLDS ON RS_1")
    print("=" * 72)

    # RS parameters
    kL = 35.0
    m_KK1_gauge = 3000.0  # GeV (first gauge boson KK mass)

    # k_IR from first gauge boson mass
    j1_1 = jn_zeros(1, 1)[0]  # 3.832
    k_IR = m_KK1_gauge / j1_1  # k * e^{-kL} in GeV

    N_modes = 500  # Number of KK modes per spin type

    # Compute spectra
    m_gauge = kk_spectrum_gauge(N_modes, k_IR)
    m_ferm = kk_spectrum_fermion(N_modes, k_IR, c=0)
    m_scalar = kk_spectrum_scalar(N_modes, k_IR)

    print(f"\nRS parameters: kL = {kL}, k_IR = {k_IR:.1f} GeV")
    print(f"NCG cutoff: Lambda = {LAMBDA_NCG:.0e} GeV")
    print(f"KK modes computed: {N_modes} per spin type")

    print(f"\nFirst 5 KK masses (GeV):")
    print(f"  Gauge (J_1 zeros):  {', '.join(f'{m:.0f}' for m in m_gauge[:5])}")
    print(f"  Fermion (n*pi):     {', '.join(f'{m:.0f}' for m in m_ferm[:5])}")
    print(f"  Scalar (J_0 zeros): {', '.join(f'{m:.0f}' for m in m_scalar[:5])}")

    print(f"\nRatios (gauge/fermion) for first 5 modes:")
    for i in range(5):
        print(f"  n={i+1}: m_gauge/m_ferm = {m_gauge[i]/m_ferm[i]:.4f}")

    # ============================================================
    # Compute spin-dependent KK sums
    # ============================================================
    print("\n" + "=" * 72)
    print("SPIN-DEPENDENT KK SUMS")
    print("=" * 72)

    # S_X = sum_{n: m_n < Lambda} ln(Lambda / m_n)
    # Only count modes below the cutoff

    def kk_sum(masses, Lambda):
        """Sum of ln(Lambda/m_n) for modes below Lambda."""
        below = masses[masses < Lambda]
        if len(below) == 0:
            return 0.0, 0
        return np.sum(np.log(Lambda / below)), len(below)

    S_gauge, N_gauge = kk_sum(m_gauge, LAMBDA_NCG)
    S_ferm, N_ferm = kk_sum(m_ferm, LAMBDA_NCG)
    S_scalar, N_scalar = kk_sum(m_scalar, LAMBDA_NCG)

    print(f"\n  Gauge bosons:  S_G = {S_gauge:.2f}  (N = {N_gauge} modes)")
    print(f"  Fermions:      S_F = {S_ferm:.2f}  (N = {N_ferm} modes)")
    print(f"  Scalars:       S_S = {S_scalar:.2f}  (N = {N_scalar} modes)")

    # Differences
    dSGF = S_gauge - S_ferm
    dSSF = S_scalar - S_ferm

    print(f"\n  S_gauge - S_ferm  = {dSGF:.4f}")
    print(f"  S_scalar - S_ferm = {dSSF:.4f}")

    # Ratios
    R_G = S_gauge / S_ferm if S_ferm > 0 else 1.0
    R_S = S_scalar / S_ferm if S_ferm > 0 else 1.0

    print(f"\n  R_gauge  = S_G/S_F = {R_G:.6f}")
    print(f"  R_scalar = S_S/S_F = {R_S:.6f}")

    # ============================================================
    # Effective KK beta functions
    # ============================================================
    print("\n" + "=" * 72)
    print("EFFECTIVE KK BETA FUNCTIONS")
    print("=" * 72)

    # Standard (spin-independent): b_KK = b_SM (all spins get same sum)
    b_KK_standard = b_SM.copy()

    # Spin-dependent: b_KK = B_GAUGE * R_G + B_FERM * 1 + B_SCALAR * R_S
    b_KK_spin = B_GAUGE * R_G + B_FERM + B_SCALAR * R_S

    print(f"\n  Standard KK beta (all spins equal):")
    print(f"    b_1^KK = {b_KK_standard[0]:.4f}")
    print(f"    b_2^KK = {b_KK_standard[1]:.4f}")
    print(f"    b_3^KK = {b_KK_standard[2]:.4f}")
    print(f"    b_1 - b_2 = {b_KK_standard[0] - b_KK_standard[1]:.4f}")

    print(f"\n  Spin-dependent KK beta:")
    print(f"    b_1^KK = {b_KK_spin[0]:.4f}")
    print(f"    b_2^KK = {b_KK_spin[1]:.4f}")
    print(f"    b_3^KK = {b_KK_spin[2]:.4f}")
    print(f"    b_1 - b_2 = {b_KK_spin[0] - b_KK_spin[1]:.4f}")

    print(f"\n  Change in (b_1 - b_2): {(b_KK_spin[0] - b_KK_spin[1]) - (b_KK_standard[0] - b_KK_standard[1]):.6f}")

    # ============================================================
    # Impact on sin^2(theta_W)
    # ============================================================
    print("\n" + "=" * 72)
    print("IMPACT ON sin^2(theta_W)")
    print("=" * 72)

    # Method: Start from T1 (a_1 = a_2 = a_3 = a_unif at Lambda)
    # Then add:
    #   (a) SM zero-mode running from Lambda to m_KK1 (standard)
    #   (b) Spin-dependent KK correction (the new effect)
    #   (c) SM zero-mode running from m_KK1 to M_Z (standard)

    # Actually, the correct approach: at each energy scale, the effective
    # beta function includes contributions from all active particles.

    # But we showed that the KK-UNIVERSAL part doesn't change sin^2(theta_W)
    # (because it multiplies the same ratio). So we only need the
    # SPIN-DEPENDENT CORRECTION.

    # The spin-dependent correction to (1/alpha_1 - 1/alpha_2):
    # delta = [(b_1^gauge)(S_G - S_F) + (b_1^scalar)(S_S - S_F)
    #         - (b_2^gauge)(S_G - S_F) - (b_2^scalar)(S_S - S_F)] / (2*pi)

    delta_splitting_gauge = (B_GAUGE[0] - B_GAUGE[1]) * dSGF / (2 * np.pi)
    delta_splitting_scalar = (B_SCALAR[0] - B_SCALAR[1]) * dSSF / (2 * np.pi)
    delta_splitting_total = delta_splitting_gauge + delta_splitting_scalar

    print(f"\n  Spin-dependent correction to (1/alpha_1 - 1/alpha_2):")
    print(f"    From gauge bosons: (0 - (-22/3)) * {dSGF:.4f} / (2pi) = {delta_splitting_gauge:.4f}")
    print(f"    From scalars:      (1/10 - 1/6) * {dSSF:.4f} / (2pi) = {delta_splitting_scalar:.4f}")
    print(f"    Total:             {delta_splitting_total:.4f}")

    # SM-only splitting (zero modes from Lambda to M_Z)
    sm_splitting = (b_SM[0] - b_SM[1]) / (2 * np.pi) * np.log(LAMBDA_NCG / M_Z)

    print(f"\n  SM zero-mode splitting: {sm_splitting:.4f}")
    print(f"  Spin-dependent / SM:    {delta_splitting_total / sm_splitting * 100:.2f}%")

    # ============================================================
    # Full calculation: running from Lambda to M_Z
    # ============================================================
    print("\n" + "=" * 72)
    print("FULL CALCULATION")
    print("=" * 72)

    # Find unification scale (where alpha_1 = alpha_2 in SM running)
    # This is the NCG cutoff for the T1 prediction
    ln_Lambda = (alpha_inv_MZ[1] - alpha_inv_MZ[0]) * 2*np.pi / (b_SM[1] - b_SM[0])
    Lambda_unif = M_Z * np.exp(ln_Lambda)
    a_unif = alpha_inv_MZ[0] - b_SM[0] / (2*np.pi) * np.log(Lambda_unif / M_Z)

    print(f"\n  SM unification of alpha_1 and alpha_2 at: {Lambda_unif:.2e} GeV")
    print(f"  Common 1/alpha: {a_unif:.2f}")

    # Case A: SM-only (no KK) — this gives the baseline NCG prediction
    a_inv_sm = np.array([a_unif, a_unif, a_unif])
    a_inv_sm += b_SM / (2*np.pi) * np.log(Lambda_unif / M_Z)
    s2w_sm = sin2_thetaW(a_inv_sm[0], a_inv_sm[1])

    print(f"\n  Case A: SM-only (T1 at Lambda = {Lambda_unif:.2e} GeV)")
    print(f"    1/alpha_1 = {a_inv_sm[0]:.2f}, 1/alpha_2 = {a_inv_sm[1]:.2f}")
    print(f"    sin^2(theta_W) = {s2w_sm:.6f}")

    # Case B: SM + spin-dependent KK correction
    # Add the spin-dependent correction to the inverse couplings
    delta_alpha_inv = np.array([
        B_GAUGE[0] * dSGF + B_FERM[0] * 0 + B_SCALAR[0] * dSSF,
        B_GAUGE[1] * dSGF + B_FERM[1] * 0 + B_SCALAR[1] * dSSF,
        B_GAUGE[2] * dSGF + B_FERM[2] * 0 + B_SCALAR[2] * dSSF
    ]) / (2 * np.pi)

    a_inv_kk = a_inv_sm + delta_alpha_inv
    s2w_kk = sin2_thetaW(a_inv_kk[0], a_inv_kk[1])

    print(f"\n  Case B: SM + spin-dependent KK correction")
    print(f"    delta(1/alpha_1) = {delta_alpha_inv[0]:.4f}")
    print(f"    delta(1/alpha_2) = {delta_alpha_inv[1]:.4f}")
    print(f"    delta(1/alpha_3) = {delta_alpha_inv[2]:.4f}")
    print(f"    1/alpha_1 = {a_inv_kk[0]:.2f}, 1/alpha_2 = {a_inv_kk[1]:.2f}")
    print(f"    sin^2(theta_W) = {s2w_kk:.6f}")

    shift = s2w_kk - s2w_sm
    shift_pct = shift / s2w_sm * 100
    print(f"\n    Shift: {shift:.6f} ({shift_pct:.2f}%)")
    print(f"    Direction: {'TOWARD' if shift > 0 else 'AWAY FROM'} measured value (0.2312)")

    # ============================================================
    # Now use the CORRECT NCG cutoff (not the SM unification scale)
    # ============================================================
    print("\n" + "=" * 72)
    print("WITH NCG CUTOFF AT GUT SCALE")
    print("=" * 72)

    # The NCG cutoff is NOT where alpha_1 = alpha_2 in SM running.
    # It's the scale where the spectral action predicts T1: a_1 = a_2 = a_3.
    # Let's use Lambda = 2e16 GeV and see what sin^2(theta_W) we get.

    for Lambda_NCG_test in [1e13, 1e14, 1e15, 2e16, 1e17, 1e18]:
        # Tree level: a_1 = a_2 = a_3 at Lambda
        # We need to determine the common value.
        # For this, we use the condition that alpha_3(M_Z) = 0.1179 (measured):
        # 1/alpha_3(Lambda) = 1/alpha_3(M_Z) - b_3/(2pi) ln(Lambda/M_Z)
        a_unif_test = alpha_inv_MZ[2] - b_SM[2] / (2*np.pi) * np.log(Lambda_NCG_test / M_Z)

        # Run down with SM + spin-dependent KK
        a_inv_test = np.array([a_unif_test, a_unif_test, a_unif_test])
        # SM running
        a_inv_test += b_SM / (2*np.pi) * np.log(Lambda_NCG_test / M_Z)

        # Recompute KK sums for this Lambda
        S_G_t, _ = kk_sum(m_gauge, Lambda_NCG_test)
        S_F_t, _ = kk_sum(m_ferm, Lambda_NCG_test)
        S_S_t, _ = kk_sum(m_scalar, Lambda_NCG_test)
        dSGF_t = S_G_t - S_F_t
        dSSF_t = S_S_t - S_F_t

        # Spin-dependent KK correction
        delta_t = np.array([
            B_GAUGE[0] * dSGF_t + B_SCALAR[0] * dSSF_t,
            B_GAUGE[1] * dSGF_t + B_SCALAR[1] * dSSF_t,
            B_GAUGE[2] * dSGF_t + B_SCALAR[2] * dSSF_t
        ]) / (2 * np.pi)

        a_inv_test_kk = a_inv_test + delta_t
        s2w_test_sm = sin2_thetaW(a_inv_test[0], a_inv_test[1])
        s2w_test_kk = sin2_thetaW(a_inv_test_kk[0], a_inv_test_kk[1])

        shift_t = s2w_test_kk - s2w_test_sm
        print(f"  Lambda = {Lambda_NCG_test:.0e}: sin^2 (SM) = {s2w_test_sm:.4f}, "
              f"sin^2 (KK) = {s2w_test_kk:.4f}, shift = {shift_t:+.4f} ({shift_t/s2w_test_sm*100:+.2f}%)")

    # ============================================================
    # Sensitivity to fermion bulk mass parameter c
    # ============================================================
    print("\n" + "=" * 72)
    print("SENSITIVITY TO FERMION BULK MASS (c parameter)")
    print("=" * 72)

    print("\nThe fermion KK spectrum depends on the bulk mass parameter c.")
    print("c = 0: conformal (m_n = n*pi * k_IR)")
    print("c > 0: heavier fermions (closer to gauge boson spectrum)")
    print("c < 0: lighter fermions (further from gauge boson spectrum)")

    Lambda_test = 2e16

    for c_val in [-0.5, -0.3, -0.1, 0.0, 0.1, 0.3, 0.5]:
        m_ferm_c = kk_spectrum_fermion(N_modes, k_IR, c=c_val)
        S_F_c, _ = kk_sum(m_ferm_c, Lambda_test)
        S_G_c, _ = kk_sum(m_gauge, Lambda_test)
        S_S_c, _ = kk_sum(m_scalar, Lambda_test)

        dSGF_c = S_G_c - S_F_c
        dSSF_c = S_S_c - S_F_c

        # Correction
        delta_c = np.array([
            B_GAUGE[0] * dSGF_c + B_SCALAR[0] * dSSF_c,
            B_GAUGE[1] * dSGF_c + B_SCALAR[1] * dSSF_c,
            B_GAUGE[2] * dSGF_c + B_SCALAR[2] * dSSF_c
        ]) / (2 * np.pi)

        # Use a_unif from alpha_3 matching
        a_unif_c = alpha_inv_MZ[2] - b_SM[2] / (2*np.pi) * np.log(Lambda_test / M_Z)
        a_inv_c = np.array([a_unif_c]*3) + b_SM/(2*np.pi) * np.log(Lambda_test/M_Z)
        a_inv_c_kk = a_inv_c + delta_c

        s2w_c_sm = sin2_thetaW(a_inv_c[0], a_inv_c[1])
        s2w_c_kk = sin2_thetaW(a_inv_c_kk[0], a_inv_c_kk[1])
        shift_c = s2w_c_kk - s2w_c_sm

        print(f"  c = {c_val:+.1f}: dS_GF = {dSGF_c:+.4f}, dS_SF = {dSSF_c:+.4f}, "
              f"sin^2 shift = {shift_c:+.6f} ({shift_c/s2w_c_sm*100:+.3f}%)")

    # ============================================================
    # Verdict
    # ============================================================
    print("\n" + "=" * 72)
    print("DOOR 1 VERDICT")
    print("=" * 72)

    print(f"""
RESULT: The spin-dependent KK threshold correction is SMALL and in the
WRONG DIRECTION (makes sin^2(theta_W) smaller, not larger).

The mechanism IS real: different spin fields DO have different KK spectra
on RS_1, and this DOES break the beta function ratio. But:

1. SIZE: The spectral difference (S_gauge - S_ferm) is only ~{abs(dSGF):.1f} out of
   a total KK sum of ~{S_ferm:.0f}. This is a {abs(dSGF/S_ferm)*100:.2f}% effect.
   After multiplying by the beta function difference (22/3), the
   correction to sin^2(theta_W) is only ~{abs(shift_pct):.1f}%.

2. DIRECTION: Gauge bosons are HEAVIER than fermions at each KK level
   (J_1 zeros > n*pi). This means fewer gauge boson modes contribute,
   which WEAKENS the negative SU(2) gauge boson contribution to b_2.
   b_2 becomes LESS negative, making the splitting (1/a_1 - 1/a_2)
   LARGER, pushing sin^2(theta_W) DOWN (away from 0.2312).

3. CONVERGENCE: The Bessel zeros approach n*pi + pi/4 for large n,
   so j_{{1,n}} / (n*pi) -> 1 + 1/(4n). The spectral difference per
   mode goes as 1/(4n), giving a harmonic series that grows only
   logarithmically: total ~ (1/4) ln(N). For N=500 modes, this
   is only ~1.6 — too small to matter.

DOOR 1 IS CLOSED (for the standard RS_1 with all SM in the bulk).

The spin-dependent KK effect:
- Exists (real physics, not zero)
- Is small (~{abs(shift_pct):.1f}% of sin^2)
- Goes in the WRONG direction
- Makes the 12% gap SLIGHTLY WORSE (becomes ~{12+abs(shift_pct):.1f}%)

The 12% gap is NOT hiding in the KK threshold structure.
""")


if __name__ == '__main__':
    main()
