"""
Phase 13F: CKK Derivation Chain Verification
=============================================

Comprehensive computation of the w₀(ζ₀) parametric prediction curve
with full uncertainty propagation, dimensional consistency checks,
and perturbative validity analysis.

The CKK formula:
    1 + w₀ = ((1+q₀)² · Ω_DE · ε₁) / (4·(1-q₀)² · ζ₀)

where:
    q₀ = -0.55 ± 0.05   (deceleration parameter)
    Ω_DE = 0.685 ± 0.007 (dark energy fraction)
    ε₁ = 0.017 ± 0.003   (GB coupling, from C_GB = 2/3)

Author: Clawd (Phase 13F)
Date: March 17, 2026
"""

import numpy as np
from scipy import optimize
from scipy.stats import norm
import json
import sys

# ============================================================
# SECTION 1: Central Parameters
# ============================================================

# Standard cosmological parameters with uncertainties
q0_central = -0.55
q0_sigma = 0.05

OmDE_central = 0.685
OmDE_sigma = 0.007

eps1_central = 0.017
eps1_sigma = 0.003

# CKK formula
def w0_from_zeta(zeta0, q0=q0_central, OmDE=OmDE_central, eps1=eps1_central):
    """
    Compute w₀ from ζ₀ via the CKK formula.

    1 + w₀ = ((1+q₀)² · Ω_DE · ε₁) / (4·(1-q₀)² · ζ₀)

    Returns w₀.
    """
    numerator = (1 + q0)**2 * OmDE * eps1
    denominator = 4 * (1 - q0)**2 * zeta0
    return -1 + numerator / denominator


def ckk_numerator(q0=q0_central, OmDE=OmDE_central, eps1=eps1_central):
    """The constant C in w₀ = -1 + C/ζ₀."""
    return (1 + q0)**2 * OmDE * eps1 / (4 * (1 - q0)**2)


# ============================================================
# SECTION 2: Parametric Curve w₀(ζ₀)
# ============================================================

# ζ₀ range: 10⁻⁴ to 0.1 (log scale, 2000 points)
zeta_range = np.logspace(-4, -1, 2000)

# Central curve
w0_central = np.array([w0_from_zeta(z) for z in zeta_range])

# Print CKK constant
C_ckk = ckk_numerator()
print("=" * 72)
print("SECTION 2: CKK Parametric Curve")
print("=" * 72)
print(f"CKK constant C = (1+q₀)² Ω_DE ε₁ / [4(1-q₀)²]")
print(f"  q₀ = {q0_central} ± {q0_sigma}")
print(f"  Ω_DE = {OmDE_central} ± {OmDE_sigma}")
print(f"  ε₁ = {eps1_central} ± {eps1_sigma}")
print(f"  (1+q₀)² = {(1+q0_central)**2:.6f}")
print(f"  (1-q₀)² = {(1-q0_central)**2:.6f}")
print(f"  C = {C_ckk:.8e}")
print(f"  w₀ = -1 + {C_ckk:.6e} / ζ₀")
print()

# ============================================================
# SECTION 3: Monte Carlo Uncertainty Propagation
# ============================================================

N_mc = 100000  # 100k samples for good statistics
np.random.seed(42)

q0_samples = np.random.normal(q0_central, q0_sigma, N_mc)
OmDE_samples = np.random.normal(OmDE_central, OmDE_sigma, N_mc)
eps1_samples = np.random.normal(eps1_central, eps1_sigma, N_mc)

# Enforce physicality: eps1 > 0, 0 < OmDE < 1, q0 ∈ (-1, 0)
mask = (eps1_samples > 0) & (OmDE_samples > 0) & (OmDE_samples < 1) & \
       (q0_samples > -1) & (q0_samples < 0)
q0_s = q0_samples[mask]
OmDE_s = OmDE_samples[mask]
eps1_s = eps1_samples[mask]
N_valid = len(q0_s)
print(f"SECTION 3: Monte Carlo Uncertainty Propagation")
print(f"  {N_valid}/{N_mc} samples passed physicality cuts")

# Compute C for each sample
C_samples = (1 + q0_s)**2 * OmDE_s * eps1_s / (4 * (1 - q0_s)**2)

# CKK constant with uncertainty
C_mean = np.mean(C_samples)
C_std = np.std(C_samples)
C_median = np.median(C_samples)
print(f"  C = {C_mean:.6e} ± {C_std:.6e}")
print(f"  C_median = {C_median:.6e}")
print(f"  Relative uncertainty: {C_std/C_mean*100:.1f}%")
print()

# Compute 1σ and 2σ bands at each ζ₀ value
# Use a coarser grid for the bands (still plenty of resolution)
zeta_band = np.logspace(-4, -1, 500)
w0_band_median = np.zeros(len(zeta_band))
w0_band_1sig_lo = np.zeros(len(zeta_band))
w0_band_1sig_hi = np.zeros(len(zeta_band))
w0_band_2sig_lo = np.zeros(len(zeta_band))
w0_band_2sig_hi = np.zeros(len(zeta_band))

for i, z in enumerate(zeta_band):
    w0_samples = -1 + C_samples / z
    w0_band_median[i] = np.median(w0_samples)
    w0_band_1sig_lo[i] = np.percentile(w0_samples, 15.87)
    w0_band_1sig_hi[i] = np.percentile(w0_samples, 84.13)
    w0_band_2sig_lo[i] = np.percentile(w0_samples, 2.28)
    w0_band_2sig_hi[i] = np.percentile(w0_samples, 97.72)

print("=" * 72)
print("SECTION 3 (cont): Uncertainty Bands at Key Points")
print("=" * 72)

key_zetas = [0.001, 0.005, 0.01, 0.02, 0.037, 0.05, 0.1]
print(f"{'ζ₀':>10s}  {'w₀(central)':>12s}  {'w₀(median)':>12s}  {'1σ range':>24s}  {'2σ range':>24s}")
for z in key_zetas:
    w_c = w0_from_zeta(z)
    w_samps = -1 + C_samples / z
    w_med = np.median(w_samps)
    lo1, hi1 = np.percentile(w_samps, [15.87, 84.13])
    lo2, hi2 = np.percentile(w_samps, [2.28, 97.72])
    print(f"  {z:8.4f}  {w_c:12.6f}  {w_med:12.6f}  [{lo1:10.6f}, {hi1:10.6f}]  [{lo2:10.6f}, {hi2:10.6f}]")
print()


# ============================================================
# SECTION 4: Observational Constraints
# ============================================================

print("=" * 72)
print("SECTION 4: Observational Constraints")
print("=" * 72)

# (a) CMB constraint: ζ₀ = 0.037 ± 0.010 (Hiramatsu & Kobayashi)
zeta_cmb = 0.037
zeta_cmb_sig = 0.010
w0_cmb = w0_from_zeta(zeta_cmb)
w0_cmb_lo = w0_from_zeta(zeta_cmb + zeta_cmb_sig)  # larger ζ₀ → w closer to -1
w0_cmb_hi = w0_from_zeta(zeta_cmb - zeta_cmb_sig)  # smaller ζ₀ → w further from -1

# Full MC for CMB constraint
zeta_cmb_samples = np.random.normal(zeta_cmb, zeta_cmb_sig, N_mc)
zeta_cmb_valid = zeta_cmb_samples[zeta_cmb_samples > 0]
w0_cmb_samples = np.array([-1 + C_samples[j] / zeta_cmb_valid[j]
                            for j in range(min(len(C_samples), len(zeta_cmb_valid)))])
w0_cmb_mc_mean = np.mean(w0_cmb_samples)
w0_cmb_mc_std = np.std(w0_cmb_samples)
w0_cmb_mc_med = np.median(w0_cmb_samples)
w0_cmb_1sig = np.percentile(w0_cmb_samples, [15.87, 84.13])

print(f"\n(a) CMB constraint (H&K 2022): ζ₀ = {zeta_cmb} ± {zeta_cmb_sig}")
print(f"    Central: w₀ = {w0_cmb:.6f}")
print(f"    MC mean: w₀ = {w0_cmb_mc_mean:.6f} ± {w0_cmb_mc_std:.6f}")
print(f"    MC median: w₀ = {w0_cmb_mc_med:.6f}")
print(f"    MC 1σ: [{w0_cmb_1sig[0]:.6f}, {w0_cmb_1sig[1]:.6f}]")

# (b) H(z) constraint: ζ₀ = 0.009 ± 0.013
zeta_hz = 0.009
zeta_hz_sig = 0.013
w0_hz = w0_from_zeta(zeta_hz)

# MC for H(z) — note this is consistent with zero, so many samples will be ≤ 0
zeta_hz_samples = np.random.normal(zeta_hz, zeta_hz_sig, N_mc)
zeta_hz_valid = zeta_hz_samples[zeta_hz_samples > 1e-6]  # exclude unphysical
frac_valid_hz = len(zeta_hz_valid) / N_mc
w0_hz_samples = np.array([-1 + C_samples[j] / zeta_hz_valid[j]
                           for j in range(min(len(C_samples), len(zeta_hz_valid)))])
w0_hz_mc_mean = np.mean(w0_hz_samples)
w0_hz_mc_std = np.std(w0_hz_samples)

print(f"\n(b) H(z) constraint: ζ₀ = {zeta_hz} ± {zeta_hz_sig}")
print(f"    Central: w₀ = {w0_hz:.6f}")
print(f"    MC mean: w₀ = {w0_hz_mc_mean:.6f} ± {w0_hz_mc_std:.6f}")
print(f"    Fraction with ζ₀ > 0: {frac_valid_hz:.3f}")
print(f"    (Consistent with ΛCDM at 0.7σ — large uncertainty)")

# (c) Brane benchmark: ζ₀ = 0.000964 (from JC with σ_UV=6, α_UV=0.01, μ²=0.1)
zeta_brane = 0.000964
w0_brane = w0_from_zeta(zeta_brane)
print(f"\n(c) Brane benchmark (JC): ζ₀ = {zeta_brane}")
print(f"    w₀ = {w0_brane:.6f}")

# (d) DESI intersection: w₀ = -0.75 ± 0.05
w0_desi = -0.75
w0_desi_sig = 0.05

# Invert: ζ₀ = C / (1 + w₀)
zeta_desi = C_ckk / (1 + w0_desi)
zeta_desi_lo = C_ckk / (1 + w0_desi + w0_desi_sig)  # smaller |1+w₀| → larger ζ₀
zeta_desi_hi = C_ckk / (1 + w0_desi - w0_desi_sig)  # larger |1+w₀| → smaller ζ₀
# Note: desi_lo and desi_hi are ζ₀ values, might be confusing — let's be explicit
zeta_desi_for_minus070 = C_ckk / (1 + (-0.70))
zeta_desi_for_minus080 = C_ckk / (1 + (-0.80))

print(f"\n(d) DESI constraint: w₀ = {w0_desi} ± {w0_desi_sig}")
print(f"    Inversion: ζ₀(w₀=-0.75) = {zeta_desi:.6e}")
print(f"    ζ₀(w₀=-0.70) = {zeta_desi_for_minus070:.6e}")
print(f"    ζ₀(w₀=-0.80) = {zeta_desi_for_minus080:.6e}")
print(f"    DESI band maps to ζ₀ ∈ [{zeta_desi_for_minus080:.6e}, {zeta_desi_for_minus070:.6e}]")

# MC inversion for DESI
w0_desi_samples = np.random.normal(w0_desi, w0_desi_sig, N_mc)
# Ensure 1+w₀ > 0 (formula requires w₀ > -1)
w0_desi_valid = w0_desi_samples[(w0_desi_samples > -1) & (w0_desi_samples < 0)]
zeta_desi_samples = C_samples[:len(w0_desi_valid)] / (1 + w0_desi_valid)
zeta_desi_mc_mean = np.mean(zeta_desi_samples)
zeta_desi_mc_std = np.std(zeta_desi_samples)
print(f"    MC: ζ₀ = {zeta_desi_mc_mean:.6e} ± {zeta_desi_mc_std:.6e}")
print()


# ============================================================
# SECTION 5: CKK Constant — Full Uncertainty Statement
# ============================================================

print("=" * 72)
print("SECTION 5: CKK Constant — Full Error Budget")
print("=" * 72)

# Analytical error propagation for C = (1+q₀)² Ω_DE ε₁ / [4(1-q₀)²]
# ∂C/∂q₀ = Ω_DE ε₁ / 4 · d/dq₀ [(1+q₀)²/(1-q₀)²]
#         = Ω_DE ε₁ / 4 · 2(1+q₀)(1-q₀)² + 2(1-q₀)(1+q₀)² / (1-q₀)⁴
#         = Ω_DE ε₁ / 4 · 2(1+q₀)[(1-q₀) + (1+q₀)] / (1-q₀)³
#         = Ω_DE ε₁ / 4 · 4(1+q₀) / (1-q₀)³
#         = Ω_DE ε₁ (1+q₀) / (1-q₀)³

dC_dq0 = OmDE_central * eps1_central * (1 + q0_central) / (1 - q0_central)**3
dC_dOmDE = (1 + q0_central)**2 * eps1_central / (4 * (1 - q0_central)**2)
dC_deps1 = (1 + q0_central)**2 * OmDE_central / (4 * (1 - q0_central)**2)

sigma_C_from_q0 = abs(dC_dq0) * q0_sigma
sigma_C_from_OmDE = abs(dC_dOmDE) * OmDE_sigma
sigma_C_from_eps1 = abs(dC_deps1) * eps1_sigma
sigma_C_total = np.sqrt(sigma_C_from_q0**2 + sigma_C_from_OmDE**2 + sigma_C_from_eps1**2)

print(f"\nAnalytical error propagation:")
print(f"  C = {C_ckk:.6e}")
print(f"  ∂C/∂q₀ = {dC_dq0:.6e}")
print(f"  ∂C/∂Ω_DE = {dC_dOmDE:.6e}")
print(f"  ∂C/∂ε₁ = {dC_deps1:.6e}")
print(f"")
print(f"  σ_C(q₀) = {sigma_C_from_q0:.6e}  ({sigma_C_from_q0/C_ckk*100:.1f}%)")
print(f"  σ_C(Ω_DE) = {sigma_C_from_OmDE:.6e}  ({sigma_C_from_OmDE/C_ckk*100:.1f}%)")
print(f"  σ_C(ε₁) = {sigma_C_from_eps1:.6e}  ({sigma_C_from_eps1/C_ckk*100:.1f}%)")
print(f"  σ_C(total) = {sigma_C_total:.6e}  ({sigma_C_total/C_ckk*100:.1f}%)")
print(f"")
print(f"  Analytical: C = ({C_ckk:.4e} ± {sigma_C_total:.4e})")
print(f"  Monte Carlo: C = ({C_mean:.4e} ± {C_std:.4e})")
print(f"  Agreement: {abs(C_ckk - C_mean)/C_std:.2f}σ (< 0.1σ expected)")
print()

# Fractional error budget
total_var = sigma_C_from_q0**2 + sigma_C_from_OmDE**2 + sigma_C_from_eps1**2
print(f"  Error budget:")
print(f"    q₀ contributes {sigma_C_from_q0**2/total_var*100:.1f}% of variance")
print(f"    Ω_DE contributes {sigma_C_from_OmDE**2/total_var*100:.1f}% of variance")
print(f"    ε₁ contributes {sigma_C_from_eps1**2/total_var*100:.1f}% of variance")
print(f"    → Dominated by q₀ uncertainty (72.5%), then ε₁ (27.4%)")
print()


# ============================================================
# SECTION 6: Dimensional Consistency Check
# ============================================================

print("=" * 72)
print("SECTION 6: Dimensional Consistency Check")
print("=" * 72)

print("""
The peer review flagged: Φ₀² = 3ζ₀M²_Pl requires k = 1/2 in certain units.

Checking the derivation chain:

DEFINITIONS:
  (i)   ζ₀ ≡ ξ Φ₀² / M₅³        [dimensionless if Φ₀ in M₅^{3/2} units]
  (ii)  M²_Pl = M₅³ / k           [4D Planck mass from 5D via RS compactification]
  (iii) ξ = 1/6                    [conformal coupling]

FROM (i):  Φ₀² = ζ₀ M₅³ / ξ = 6 ζ₀ M₅³

FROM (ii): M₅³ = k M²_Pl

SUBSTITUTING: Φ₀² = 6 ζ₀ k M²_Pl

THE MONOGRAPH STATES: Φ₀² = 3 ζ₀ M²_Pl

CONSISTENCY REQUIRES: 6k = 3  →  k = 1/2
""")

# Verify numerically
xi = 1.0/6.0
M5_cubed = 1.0  # natural units

print("Numerical verification:")
for k_val in [0.5, 1.0, 2.0]:
    M_Pl_sq = M5_cubed / k_val
    zeta_test = 0.038

    # From definition (i):
    Phi0_sq_from_def = zeta_test * M5_cubed / xi

    # From monograph claim:
    Phi0_sq_monograph = 3 * zeta_test * M_Pl_sq

    # From exact chain:
    Phi0_sq_exact = 6 * zeta_test * k_val * M_Pl_sq

    print(f"\n  k = {k_val}:")
    print(f"    M²_Pl = M₅³/k = {M_Pl_sq:.4f}")
    print(f"    Φ₀²(definition) = ζ₀ M₅³/ξ = {Phi0_sq_from_def:.6f}")
    print(f"    Φ₀²(monograph)  = 3ζ₀M²_Pl = {Phi0_sq_monograph:.6f}")
    print(f"    Φ₀²(exact chain)= 6ζ₀kM²_Pl = {Phi0_sq_exact:.6f}")
    print(f"    Match: def=monograph? {np.isclose(Phi0_sq_from_def, Phi0_sq_monograph)}")
    print(f"    Match: def=exact?     {np.isclose(Phi0_sq_from_def, Phi0_sq_exact)}")

print(f"""
CONCLUSION:
  The monograph relation Φ₀² = 3ζ₀M²_Pl is CONSISTENT if and only if k = 1/2.

  In the Randall-Sundrum model, the 4D Planck mass is:
    M²_Pl = M₅³ ∫₀^πR dy e^{{-2ky}} = M₅³(1 - e^{{-2kπR}}) / (2k)

  In the large-warping limit (kπR >> 1):
    M²_Pl ≈ M₅³ / (2k)

  This gives k = 1/2 in units where M₅ = 1, M_Pl = 1.
  More precisely: the relation defines the normalization convention.

  The factor of 2 difference between M²_Pl = M₅³/k (used in some of our
  earlier phases) and M²_Pl = M₅³/(2k) (standard RS) is the source.

  RESOLUTION: The monograph should either:
    (A) Use M²_Pl = M₅³/(2k), giving Φ₀² = 3ζ₀M²_Pl exactly, OR
    (B) State explicitly that k = 1/2 is the adopted convention, OR
    (C) Use the fundamental relation Φ₀² = ζ₀M₅³/ξ = 6ζ₀M₅³ throughout
        and define M²_Pl accordingly.

  Option (C) is cleanest — it avoids the k ambiguity entirely.
  The CKK formula itself uses only ζ₀, not Φ₀ or k separately,
  so the physics is unaffected.
""")


# ============================================================
# SECTION 7: Perturbative Validity Analysis
# ============================================================

print("=" * 72)
print("SECTION 7: Perturbative Validity Analysis")
print("=" * 72)

print("""
The CKK formula: 1 + w₀ = C/ζ₀  where C ≈ 4.8 × 10⁻⁴

As ζ₀ → 0: w₀ → +∞ (formula diverges — perturbative breakdown).
As ζ₀ → ∞: w₀ → -1 (ΛCDM limit).

Perturbative validity requires |1 + w₀| << 1 (small deviation from ΛCDM).
This means C/ζ₀ << 1, i.e., ζ₀ >> C.
""")

# Find where |1 + w₀| = various thresholds
thresholds = [0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
print(f"Perturbative breakdown scale:")
print(f"  {'|1+w₀|':>10s}  {'ζ₀':>12s}  {'w₀':>10s}  {'Status':>20s}")
for thresh in thresholds:
    z_thresh = C_ckk / thresh
    w_thresh = -1 + thresh
    status = "perturbative" if thresh < 0.1 else ("marginal" if thresh < 0.5 else "BREAKDOWN")
    print(f"  {thresh:10.3f}  {z_thresh:12.6e}  {w_thresh:10.4f}  {status:>20s}")

print(f"""
Physical interpretation:
  The CKK formula is derived assuming the scalar field perturbation is small
  relative to the background. The effective potential V_eff has curvature:

    V''_eff ∝ ζ₀ · (mass scales)

  As ζ₀ → 0:
    - V''_eff → 0 (flat potential — slow-roll limit)
    - The scalar becomes massless
    - 1 + w₀ → ∞ (perturbative formula breaks down)
    - Physical behavior: the scalar field rolls freely, dark energy
      equation of state deviates strongly from -1

  The perturbative formula is VALID for ζ₀ >> C ≈ {C_ckk:.1e}, i.e., ζ₀ >> 5 × 10⁻⁴.

  For ζ₀ ≲ C (i.e., ζ₀ ≲ {C_ckk:.1e}):
    - |1+w₀| ≳ 1
    - Need full nonlinear field equations
    - The brane benchmark ζ₀ = 0.00096 gives |1+w₀| = {abs(w0_from_zeta(0.00096)+1):.3f}
      → marginal (|1+w₀| ~ 0.25, could still be perturbative)
    - Below ζ₀ ~ 2×10⁻⁴, the formula is unreliable

  CRITICAL BOUNDARY: ζ₀_min ≈ {5*C_ckk:.4e} (where |1+w₀| < 0.1)
""")

# V''_eff singularity analysis
print(f"V''_eff → 0 singularity:")
print(f"  The effective mass m²_eff ∝ ζ₀ vanishes as ζ₀ → 0.")
print(f"  At ζ₀ = 0 exactly: massless scalar, V_eff is flat,")
print(f"  no restoring force, w₀ is determined by kinetic terms alone.")
print(f"  The CKK formula has a simple pole at ζ₀ = 0.")
print(f"  This is not a pathology — it correctly signals that the")
print(f"  linearized approximation fails.")
print()


# ============================================================
# SECTION 8: Summary Table — All Constraints
# ============================================================

print("=" * 72)
print("SECTION 8: Summary — All Observational Constraints")
print("=" * 72)

# CMB: propagate both ζ₀ uncertainty and cosmological parameter uncertainty
print(f"\n{'Constraint':>25s}  {'ζ₀':>12s}  {'σ(ζ₀)':>10s}  {'w₀':>10s}  {'σ(w₀)':>10s}  {'Notes':>30s}")
print("-" * 105)

# CMB
print(f"{'H&K CMB (Planck)':>25s}  {zeta_cmb:12.4f}  {zeta_cmb_sig:10.4f}  {w0_cmb_mc_mean:10.6f}  {w0_cmb_mc_std:10.6f}  {'4σ detection of β≠0':>30s}")

# H(z)
print(f"{'H(z) expansion rate':>25s}  {zeta_hz:12.4f}  {zeta_hz_sig:10.4f}  {w0_hz:10.6f}  {'(large)':>10s}  {'Consistent with ΛCDM':>30s}")

# Brane benchmark
print(f"{'Brane benchmark (JC)':>25s}  {zeta_brane:12.6f}  {'(fixed)':>10s}  {w0_brane:10.6f}  {'(param)':>10s}  {'σ_UV=6, α=0.01, μ²=0.1':>30s}")

# DESI
print(f"{'DESI intersection':>25s}  {zeta_desi:12.6e}  {zeta_desi_mc_std:10.6e}  {w0_desi:10.4f}  {w0_desi_sig:10.4f}  {'If DESI w₀ is physical':>30s}")

print()

# ============================================================
# SECTION 9: Inverse Function — ζ₀(w₀)
# ============================================================

print("=" * 72)
print("SECTION 9: Inverse Function ζ₀(w₀)")
print("=" * 72)

w0_targets = [-0.99, -0.98, -0.95, -0.90, -0.80, -0.75, -0.70, -0.50]
print(f"\n{'w₀':>8s}  {'1+w₀':>10s}  {'ζ₀':>14s}  {'ζ₀(1σ lo)':>14s}  {'ζ₀(1σ hi)':>14s}")
for w in w0_targets:
    one_plus_w = 1 + w
    z_central = C_ckk / one_plus_w
    z_lo = (C_ckk - sigma_C_total) / one_plus_w
    z_hi = (C_ckk + sigma_C_total) / one_plus_w
    print(f"  {w:6.3f}  {one_plus_w:10.4f}  {z_central:14.6e}  {z_lo:14.6e}  {z_hi:14.6e}")

print()


# ============================================================
# SECTION 10: Cross-checks
# ============================================================

print("=" * 72)
print("SECTION 10: Cross-checks")
print("=" * 72)

# Check 1: Does ζ₀ = 0.038 give w₀ ≈ -0.993?
w0_at_038 = w0_from_zeta(0.038)
print(f"\nCheck 1: ζ₀ = 0.038 → w₀ = {w0_at_038:.6f}")
print(f"  Monograph claimed w₀ = -0.993 ± 0.002")
print(f"  Difference: {abs(w0_at_038 - (-0.993)):.4f}")
print(f"  {'PASS' if abs(w0_at_038 - (-0.993)) < 0.005 else 'FAIL'}: within expected range")

# Check 2: Does ζ₀ = 0.00096 give w₀ ≈ -0.746?
w0_at_096 = w0_from_zeta(0.00096)
print(f"\nCheck 2: ζ₀ = 0.000964 → w₀ = {w0_from_zeta(0.000964):.6f}")
print(f"  13B stated w₀ = -0.746")
print(f"  ζ₀ = 0.00096 → w₀ = {w0_at_096:.6f}")
print(f"  Difference: {abs(w0_at_096 - (-0.746)):.4f}")

# Check 3: Limiting behavior
w0_large = w0_from_zeta(1.0)
w0_small = w0_from_zeta(1e-6)
print(f"\nCheck 3: Limiting behavior")
print(f"  ζ₀ = 1.0 → w₀ = {w0_large:.8f} (should be ≈ -1)")
print(f"  ζ₀ = 10⁻⁶ → w₀ = {w0_small:.2f} (should diverge from -1)")

# Check 4: CKK formula algebraic identity
# (1+q₀)² / (1-q₀)² for q₀ = -0.55 should be (0.45/1.55)² = 0.08432...
ratio_check = (1 + q0_central)**2 / (1 - q0_central)**2
ratio_manual = (0.45 / 1.55)**2
print(f"\nCheck 4: Algebraic identity")
print(f"  (1+q₀)²/(1-q₀)² = {ratio_check:.8f}")
print(f"  (0.45/1.55)²     = {ratio_manual:.8f}")
print(f"  Match: {np.isclose(ratio_check, ratio_manual)}")

# Full C computation step by step
print(f"\nCheck 5: CKK constant step-by-step")
print(f"  (1+q₀)² = (1 + ({q0_central}))² = {(1+q0_central):.4f}² = {(1+q0_central)**2:.8f}")
print(f"  (1-q₀)² = (1 - ({q0_central}))² = {(1-q0_central):.4f}² = {(1-q0_central)**2:.8f}")
print(f"  Ω_DE × ε₁ = {OmDE_central} × {eps1_central} = {OmDE_central*eps1_central:.8f}")
print(f"  numerator = {(1+q0_central)**2:.8f} × {OmDE_central*eps1_central:.8f} = {(1+q0_central)**2 * OmDE_central * eps1_central:.10f}")
print(f"  denominator = 4 × {(1-q0_central)**2:.8f} = {4*(1-q0_central)**2:.8f}")
print(f"  C = {(1+q0_central)**2 * OmDE_central * eps1_central:.10f} / {4*(1-q0_central)**2:.8f}")
print(f"    = {C_ckk:.10e}")
print()


# ============================================================
# SECTION 11: Data Export (for results markdown)
# ============================================================

results = {
    "ckk_constant": {
        "value": float(C_ckk),
        "uncertainty": float(sigma_C_total),
        "mc_value": float(C_mean),
        "mc_uncertainty": float(C_std),
        "relative_uncertainty_percent": float(sigma_C_total / C_ckk * 100),
        "error_budget": {
            "q0_fraction": float(sigma_C_from_q0**2 / total_var),
            "OmDE_fraction": float(sigma_C_from_OmDE**2 / total_var),
            "eps1_fraction": float(sigma_C_from_eps1**2 / total_var),
        }
    },
    "constraints": {
        "cmb_hk": {
            "zeta0": float(zeta_cmb),
            "zeta0_sigma": float(zeta_cmb_sig),
            "w0_mean": float(w0_cmb_mc_mean),
            "w0_sigma": float(w0_cmb_mc_std),
        },
        "hz_expansion": {
            "zeta0": float(zeta_hz),
            "zeta0_sigma": float(zeta_hz_sig),
            "w0_central": float(w0_hz),
        },
        "brane_benchmark": {
            "zeta0": float(zeta_brane),
            "w0": float(w0_brane),
        },
        "desi_intersection": {
            "w0": float(w0_desi),
            "w0_sigma": float(w0_desi_sig),
            "zeta0": float(zeta_desi),
            "zeta0_sigma": float(zeta_desi_mc_std),
        },
    },
    "dimensional_consistency": {
        "k_required": 0.5,
        "resolution": "Use M²_Pl = M₅³/(2k) or state k=1/2 convention explicitly",
        "physics_affected": False,
    },
    "perturbative_validity": {
        "zeta0_min_strict": float(10 * C_ckk),
        "zeta0_min_marginal": float(C_ckk),
        "w0_at_brane_benchmark": float(w0_brane),
        "brane_benchmark_perturbative": abs(w0_brane + 1) < 0.5,
    },
    "cross_checks": {
        "zeta038_gives_w0_993": abs(w0_at_038 - (-0.993)) < 0.005,
        "zeta00096_gives_w0_746": abs(w0_at_096 - (-0.746)) < 0.01,
    },
}

# Write JSON for downstream use
json_path = "C:/Users/mercu/clawd/projects/Project Meridian/phase13/13F_ckk_results.json"
with open(json_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"Results exported to: {json_path}")

print("\n" + "=" * 72)
print("COMPUTATION COMPLETE — Phase 13F CKK Parametric Analysis")
print("=" * 72)
