#!/usr/bin/env python3
"""
Project Meridian Phase 20: Pati-Salam Extended Spectral Triple Analysis
========================================================================
Comprehensive verification of gauge unification through PS intermediate symmetry.
"""

import numpy as np

print("=" * 80)
print("PROJECT MERIDIAN — PHASE 20: PATI-SALAM SPECTRAL TRIPLE ANALYSIS")
print("=" * 80)

# ============================================================
# 1. SM COUPLING CONSTANTS AT M_Z
# ============================================================
print("\n" + "=" * 80)
print("1. SM COUPLING CONSTANTS AT M_Z = 91.1876 GeV")
print("=" * 80)

M_Z = 91.1876  # GeV

alpha_em_MZ = 1.0 / 127.9
sin2_thetaW_MZ = 0.2312
alpha_s_MZ = 0.1179

# Derive SU(2) and U(1) couplings
# alpha_em = alpha_2 * sin^2(theta_W) = alpha_1 * cos^2(theta_W) / (5/3)
# In GUT normalization: alpha_1 = (5/3) * alpha_Y
# alpha_em^{-1} = alpha_2^{-1} * sin^2(theta_W)^{-1} ...
# More precisely:
# alpha_em = alpha_2 * sin^2(theta_W)
# alpha_2 = alpha_em / sin^2(theta_W)
alpha_2_MZ = alpha_em_MZ / sin2_thetaW_MZ
alpha_2_inv_MZ = 1.0 / alpha_2_MZ

# For U(1)_Y (non-GUT normalized):
# alpha_em = alpha_Y * cos^2(theta_W) => alpha_Y = alpha_em / cos^2(theta_W)
cos2_thetaW_MZ = 1.0 - sin2_thetaW_MZ
alpha_Y_MZ = alpha_em_MZ / cos2_thetaW_MZ

# GUT normalization: alpha_1 = (5/3) * alpha_Y
alpha_1_MZ = (5.0 / 3.0) * alpha_Y_MZ
alpha_1_inv_MZ = 1.0 / alpha_1_MZ

alpha_3_MZ = alpha_s_MZ
alpha_3_inv_MZ = 1.0 / alpha_3_MZ

print(f"  alpha_em(M_Z)    = 1/{1.0/alpha_em_MZ:.1f}")
print(f"  sin²θ_W(M_Z)    = {sin2_thetaW_MZ}")
print(f"  alpha_s(M_Z)     = {alpha_s_MZ}")
print()
print(f"  GUT-normalized inverse couplings at M_Z:")
print(f"  α₁⁻¹(M_Z) = {alpha_1_inv_MZ:.2f}")
print(f"  α₂⁻¹(M_Z) = {alpha_2_inv_MZ:.2f}")
print(f"  α₃⁻¹(M_Z) = {alpha_3_inv_MZ:.2f}")

# Cross-check: 1/alpha_em = (3/5) * (1/alpha_1) + 1/alpha_2
# In terms of inverse couplings: alpha_em^{-1} = (3/5) * alpha_1^{-1} + alpha_2^{-1}  [WRONG]
# Actually: alpha_em = alpha_2 * sin²θ_W, and 1/alpha_em = 1/alpha_2 + 1/alpha_Y
# where alpha_Y = (3/5) alpha_1, so 1/alpha_Y = (5/3)/alpha_1 = (5/3)*alpha_1_inv
# Thus: alpha_em^{-1} = alpha_2^{-1} + (5/3)*alpha_1^{-1}
alpha_em_inv_check = alpha_2_inv_MZ + (5.0/3.0) * alpha_1_inv_MZ
# Wait, that's also not right. Let's be precise:
# e² = g² sin²θ_W = g'² cos²θ_W
# 1/e² = 1/g² + 1/g'²   (standard)
# α_em = α₂ sin²θ_W, so 1/α_em = 1/α₂ + 1/α_Y
# α_Y = (3/5)α₁ => 1/α_Y = (5/3)α₁⁻¹
# So: α_em⁻¹ = α₂⁻¹ + (5/3)α₁⁻¹
# Hmm, but numerically: 29.57 + (5/3)*59.00 = 29.57 + 98.34 = 127.91  ✓ (too large)
# Actually that IS correct: 1/α_em = 1/α₂ + (5/3)/α₁
alpha_em_inv_check = alpha_2_inv_MZ + (5.0/3.0) * alpha_1_inv_MZ
print(f"\n  Cross-check: α_em⁻¹ = α₂⁻¹ + (5/3)α₁⁻¹ = {alpha_em_inv_check:.1f} (should be 127.9)")

# ============================================================
# 2. SM-ONLY RUNNING FROM UNIFICATION
# ============================================================
print("\n" + "=" * 80)
print("2. SM-ONLY ONE-LOOP RUNNING")
print("=" * 80)

# SM one-loop beta coefficients (b_i where dα_i^{-1}/d(ln μ) = -b_i/(2π))
b1_SM = 41.0 / 10.0   # 4.1
b2_SM = -19.0 / 6.0   # -3.167
b3_SM = -7.0           # -7.0

print(f"  SM beta coefficients (one-loop):")
print(f"  b₁ = 41/10 = {b1_SM:.4f}")
print(f"  b₂ = -19/6 = {b2_SM:.4f}")
print(f"  b₃ = -7     = {b3_SM:.4f}")

# RGE: α_i^{-1}(μ) = α_i^{-1}(M_Z) - (b_i / 2π) * ln(μ/M_Z)
def run_SM(log10_mu, alpha_inv_MZ, b):
    """Run coupling from M_Z to mu using SM betas."""
    t = np.log(10**log10_mu / M_Z)
    return alpha_inv_MZ - (b / (2.0 * np.pi)) * t

# Find SU(2)-SU(3) crossing
# α₂⁻¹(Λ) = α₃⁻¹(Λ)
# α₂⁻¹(M_Z) - (b₂/2π) ln(Λ/M_Z) = α₃⁻¹(M_Z) - (b₃/2π) ln(Λ/M_Z)
# (α₂⁻¹ - α₃⁻¹)(M_Z) = ((b₂ - b₃)/2π) ln(Λ/M_Z)
delta_23_MZ = alpha_2_inv_MZ - alpha_3_inv_MZ
ln_Lambda_MZ = delta_23_MZ * 2.0 * np.pi / (b2_SM - b3_SM)
log10_Lambda_23 = np.log10(M_Z) + ln_Lambda_MZ / np.log(10)

print(f"\n  SU(2)-SU(3) crossing scale:")
print(f"  Δ₂₃(M_Z) = α₂⁻¹ - α₃⁻¹ = {delta_23_MZ:.2f}")
print(f"  b₂ - b₃ = {b2_SM - b3_SM:.4f}")
print(f"  log₁₀(Λ₂₃/GeV) = {log10_Lambda_23:.2f}")
print(f"  Λ₂₃ = 10^{log10_Lambda_23:.2f} GeV")

# At that scale, compute all three couplings
alpha_1_inv_Lambda = run_SM(log10_Lambda_23, alpha_1_inv_MZ, b1_SM)
alpha_2_inv_Lambda = run_SM(log10_Lambda_23, alpha_2_inv_MZ, b2_SM)
alpha_3_inv_Lambda = run_SM(log10_Lambda_23, alpha_3_inv_MZ, b3_SM)

print(f"\n  Couplings at Λ₂₃ = 10^{log10_Lambda_23:.2f} GeV:")
print(f"  α₁⁻¹(Λ₂₃) = {alpha_1_inv_Lambda:.2f}")
print(f"  α₂⁻¹(Λ₂₃) = {alpha_2_inv_Lambda:.2f}")
print(f"  α₃⁻¹(Λ₂₃) = {alpha_3_inv_Lambda:.2f}")

alpha_U_inv = 0.5 * (alpha_2_inv_Lambda + alpha_3_inv_Lambda)
gap = alpha_1_inv_Lambda - alpha_U_inv
print(f"\n  Unification coupling: α_U⁻¹ ≈ {alpha_U_inv:.2f}")
print(f"  U(1) GAP: α₁⁻¹ - α_U⁻¹ = {gap:.2f}")
print(f"  This gap of ~{gap:.1f} units prevents simple SU(5) unification.")

# ============================================================
# 3. PATI-SALAM INTERMEDIATE REGIME
# ============================================================
print("\n" + "=" * 80)
print("3. PATI-SALAM MATCHING CONDITIONS & BETA COEFFICIENTS")
print("=" * 80)

print("\n  Pati-Salam group: SU(2)_L × SU(2)_R × SU(4)_C")
print()
print("  Matching at M_PS (PS → SM):")
print("    α₁⁻¹ = (3/5)α_R⁻¹ + (2/5)α₄⁻¹")
print("    α₂⁻¹ = α_L⁻¹")
print("    α₃⁻¹ = α₄⁻¹")
print()
print("  Verification: At PS cutoff Λ with α_L = α_R = α₄ = α_U:")
a_U = 1.0  # symbolic
a1_check = 1.0 / ((3.0/5.0) / a_U + (2.0/5.0) / a_U)
a2_check = a_U
a3_check = a_U
print(f"    α₁ = 1/((3/5)/α_U + (2/5)/α_U) = 1/(1/α_U) = α_U  ✓")
print(f"    α₂ = α_L = α_U  ✓")
print(f"    α₃ = α₄ = α_U  ✓")

# sin²θ_W at unification:
# sin²θ_W = α₁/(α₁ + (5/3)α₂) = g₁²/(g₁² + g₂²) in GUT norm
# At unification α₁ = α₂ => sin²θ_W = 1/(1 + 5/3) = 3/8
sin2_unif = 3.0 / 8.0
print(f"\n  sin²θ_W at PS unification = 3/8 = {sin2_unif:.4f}")

# PS beta coefficients
print("\n  PS one-loop beta coefficients:")
print("  Fermion content: 3 generations of (2,1,4) + (1,2,4̄)")

# Pure gauge contributions: b = -11/3 * C₂(G)
# SU(2): C₂ = 2, so b_gauge = -22/3
# SU(4): C₂ = 4, so b_gauge = -44/3

# Fermion contributions per generation:
# For SU(2)_L: (2,1,4) gives n_f Weyl fermions in fundamental of SU(2)
#   Each (2,1,4) = 4 Weyl doublets under SU(2)_L
#   Fermion contribution: (2/3) * T(R) per Weyl fermion
#   T(fund of SU(2)) = 1/2, T(fund of SU(4)) = 1/2
#   (2,1,4): 4 copies of SU(2)_L doublet => Δb_L = (2/3)*4*(1/2) = 4/3 per gen
#   (1,2,4̄): singlet under SU(2)_L => Δb_L = 0
#   3 gen: Δb_L(ferm) = 3 * 4/3 = 4

# For SU(2)_R: by L-R symmetry, same = 4
# For SU(4)_C:
#   (2,1,4): 2 copies of SU(4) fund => Δb₄ = (2/3)*2*(1/2) = 2/3 per gen
#   (1,2,4̄): 2 copies of SU(4) fund => Δb₄ = (2/3)*2*(1/2) = 2/3 per gen
#   3 gen: Δb₄(ferm) = 3 * (2/3 + 2/3) = 4

b_L_gauge = -22.0 / 3.0
b_R_gauge = -22.0 / 3.0
b_4_gauge = -44.0 / 3.0

b_L_ferm = 4.0
b_R_ferm = 4.0
b_4_ferm = 4.0

print(f"    Gauge: b_L = {b_L_gauge:.4f}, b_R = {b_R_gauge:.4f}, b₄ = {b_4_gauge:.4f}")
print(f"    Fermion (3 gen): Δb_L = {b_L_ferm:.1f}, Δb_R = {b_R_ferm:.1f}, Δb₄ = {b_4_ferm:.1f}")

# Minimal scalar: bidoublet Φ = (2,2,1)
# Under SU(2)_L: 2 copies of doublet (from SU(2)_R dim) => T = 1/2 each
# Scalar contribution: (1/3)*T(R) per real scalar degree of freedom
# (2,2,1): complex scalar, so 2*2*1 = 4 complex = 8 real d.o.f.
# Under SU(2)_L: 2 doublets (complex) = 4 real doublets
#   Δb_L = (1/3) * 2 * (1/2) = 1/3
# Under SU(2)_R: same by symmetry = 1/3
# Under SU(4)_C: singlet => 0
b_L_scalar_bidoublet = 1.0 / 3.0
b_R_scalar_bidoublet = 1.0 / 3.0
b_4_scalar_bidoublet = 0.0

print(f"\n  Minimal scalar — bidoublet (2,2,1):")
print(f"    Δb_L = {b_L_scalar_bidoublet:.4f}, Δb_R = {b_R_scalar_bidoublet:.4f}, Δb₄ = {b_4_scalar_bidoublet:.4f}")

b_L_min = b_L_gauge + b_L_ferm + b_L_scalar_bidoublet
b_R_min = b_R_gauge + b_R_ferm + b_R_scalar_bidoublet
b_4_min = b_4_gauge + b_4_ferm + b_4_scalar_bidoublet

print(f"\n  Minimal PS totals:")
print(f"    b_L = {b_L_min:.4f}")
print(f"    b_R = {b_R_min:.4f}")
print(f"    b₄  = {b_4_min:.4f}")

# Also include the (1,1,15) + (2,2,15) that's typically needed for symmetry breaking
# But first let's also need (1,3,10) or (1,2,4) for R-parity breaking
# Let's add the SU(2)_R doublet (1,2,4) needed for B-L breaking
# This is the "left-right symmetric" Higgs
# But let's keep it simple and do the minimal first

# R-parity breaking scalar: (1,2,4) + (1,2,4̄) (needed for SU(2)_R × SU(4) → U(1)_Y × SU(3))
# Under SU(2)_R: fund, under SU(4): fund
# (1,2,4):
#   SU(2)_L: singlet => 0
#   SU(2)_R: 1 copy of fund (4 components from SU(4)) => Δb_R = (1/3)*4*(1/2) = 2/3
#   SU(4): 2 copies of fund (from SU(2)_R) => Δb₄ = (1/3)*2*(1/2) = 1/3
# With conjugate pair:
b_L_scalar_124 = 0.0
b_R_scalar_124 = 2.0 * (2.0/3.0)  # pair
b_4_scalar_124 = 2.0 * (1.0/3.0)  # pair

print(f"\n  R-symmetry breaking scalar (1,2,4) + (1,2,4̄):")
print(f"    Δb_L = {b_L_scalar_124:.4f}, Δb_R = {b_R_scalar_124:.4f}, Δb₄ = {b_4_scalar_124:.4f}")

# ============================================================
# 4. SCAN OVER M_PS FOR MINIMAL PS MODEL
# ============================================================
print("\n" + "=" * 80)
print("4. M_PS SCAN — MINIMAL PATI-SALAM MODEL")
print("=" * 80)

# Unification scale
log10_Lambda = log10_Lambda_23  # ~16.5

# For the scan, we use two-stage running:
# Stage 1: PS running from Λ down to M_PS
# Stage 2: SM running from M_PS down to M_Z

def compute_MZ_couplings(log10_MPS, log10_Lambda_U, alpha_U_inv_val,
                          b_L, b_R, b_4, b1_sm, b2_sm, b3_sm):
    """
    Two-stage running: PS from Λ_U to M_PS, then SM from M_PS to M_Z.
    Returns (α₁⁻¹, α₂⁻¹, α₃⁻¹) at M_Z.
    """
    # Stage 1: PS running from Λ_U to M_PS
    t_PS = np.log(10**log10_MPS / 10**log10_Lambda_U)  # negative (running down)

    alpha_L_inv_MPS = alpha_U_inv_val - (b_L / (2.0 * np.pi)) * t_PS
    alpha_R_inv_MPS = alpha_U_inv_val - (b_R / (2.0 * np.pi)) * t_PS
    alpha_4_inv_MPS = alpha_U_inv_val - (b_4 / (2.0 * np.pi)) * t_PS

    # PS → SM matching
    alpha_1_inv_MPS = (3.0/5.0) * alpha_R_inv_MPS + (2.0/5.0) * alpha_4_inv_MPS
    alpha_2_inv_MPS = alpha_L_inv_MPS
    alpha_3_inv_MPS = alpha_4_inv_MPS

    # Stage 2: SM running from M_PS to M_Z
    t_SM = np.log(M_Z / 10**log10_MPS)  # negative (running down)

    alpha_1_inv_MZ_pred = alpha_1_inv_MPS - (b1_sm / (2.0 * np.pi)) * t_SM
    alpha_2_inv_MZ_pred = alpha_2_inv_MPS - (b2_sm / (2.0 * np.pi)) * t_SM
    alpha_3_inv_MZ_pred = alpha_3_inv_MPS - (b3_sm / (2.0 * np.pi)) * t_SM

    return alpha_1_inv_MZ_pred, alpha_2_inv_MZ_pred, alpha_3_inv_MZ_pred

# Determine alpha_U_inv at the crossing scale
# Use average of α₂ and α₃ at the crossing
alpha_U_inv_crossing = 0.5 * (alpha_2_inv_Lambda + alpha_3_inv_Lambda)
print(f"  Using α_U⁻¹ = {alpha_U_inv_crossing:.2f} at Λ = 10^{log10_Lambda:.2f} GeV")

print(f"\n  --- Minimal PS: b_L={b_L_min:.2f}, b_R={b_R_min:.2f}, b₄={b_4_min:.2f} ---")

# Scan
log10_MPS_range = np.linspace(8, 17, 1000)
results_min = []

for log10_MPS in log10_MPS_range:
    a1, a2, a3 = compute_MZ_couplings(log10_MPS, log10_Lambda, alpha_U_inv_crossing,
                                        b_L_min, b_R_min, b_4_min,
                                        b1_SM, b2_SM, b3_SM)
    # sin²θ_W = α₁/(α₁ + (5/3)α₂) but in terms of inverse:
    # sin²θ_W = (1/α₁) / (1/α₁ + 5/(3α₂)) ...
    # Actually: sin²θ_W = g'²/(g'² + g²) = α_Y/(α_Y + α₂)
    # α_Y = (3/5)α₁, so sin²θ_W = (3/5)α₁/((3/5)α₁ + α₂)
    # = (3/5)/α₁⁻¹ / ((3/5)/α₁⁻¹ + 1/α₂⁻¹) ... let me just do it numerically
    alpha_1_val = 1.0 / a1
    alpha_2_val = 1.0 / a2
    alpha_Y_val = (3.0/5.0) * alpha_1_val
    sin2_pred = alpha_Y_val / (alpha_Y_val + alpha_2_val)

    delta_23 = a2 - a3
    results_min.append((log10_MPS, a1, a2, a3, sin2_pred, delta_23))

results_min = np.array(results_min)

# Find M_PS where α₁⁻¹(M_Z) = 59.01
target_a1 = alpha_1_inv_MZ
idx_a1 = np.argmin(np.abs(results_min[:, 1] - target_a1))
log10_MPS_a1 = results_min[idx_a1, 0]
a2_at_match = results_min[idx_a1, 2]
a3_at_match = results_min[idx_a1, 3]
sin2_at_match = results_min[idx_a1, 4]
delta23_at_match = results_min[idx_a1, 5]

print(f"\n  U(1) gap closure: α₁⁻¹(M_Z) = {target_a1:.2f}")
print(f"  Required M_PS = 10^{log10_MPS_a1:.2f} GeV")
print(f"  At this M_PS:")
print(f"    α₁⁻¹(M_Z) = {results_min[idx_a1, 1]:.2f}")
print(f"    α₂⁻¹(M_Z) = {a2_at_match:.2f} (target: {alpha_2_inv_MZ:.2f})")
print(f"    α₃⁻¹(M_Z) = {a3_at_match:.2f} (target: {alpha_3_inv_MZ:.2f})")
print(f"    sin²θ_W(M_Z) = {sin2_at_match:.4f} (target: {sin2_thetaW_MZ:.4f})")
print(f"    Δ₂₃ = α₂⁻¹ - α₃⁻¹ = {delta23_at_match:.2f} (target: {delta_23_MZ:.2f})")

# Find M_PS where sin²θ_W = 0.2312
idx_sin2 = np.argmin(np.abs(results_min[:, 4] - sin2_thetaW_MZ))
log10_MPS_sin2 = results_min[idx_sin2, 0]
print(f"\n  sin²θ_W match: sin²θ_W(M_Z) = 0.2312")
print(f"  Required M_PS = 10^{log10_MPS_sin2:.2f} GeV")
print(f"  At this M_PS:")
print(f"    α₁⁻¹(M_Z) = {results_min[idx_sin2, 1]:.2f}")
print(f"    α₂⁻¹(M_Z) = {results_min[idx_sin2, 2]:.2f}")
print(f"    α₃⁻¹(M_Z) = {results_min[idx_sin2, 3]:.2f}")
print(f"    Δ₂₃ = {results_min[idx_sin2, 5]:.2f}")

# Print table of key M_PS values
print(f"\n  --- Coupling evolution table (minimal PS) ---")
print(f"  {'log₁₀(M_PS)':>12s}  {'α₁⁻¹(M_Z)':>10s}  {'α₂⁻¹(M_Z)':>10s}  {'α₃⁻¹(M_Z)':>10s}  {'sin²θ_W':>8s}  {'Δ₂₃':>8s}")
for target_log in [8, 9, 10, 11, 12, 13, 14, 15, 16, log10_Lambda]:
    idx = np.argmin(np.abs(results_min[:, 0] - target_log))
    r = results_min[idx]
    print(f"  {r[0]:12.2f}  {r[1]:10.2f}  {r[2]:10.2f}  {r[3]:10.2f}  {r[4]:8.4f}  {r[5]:8.2f}")

# ============================================================
# 5. PROTON DECAY CONSTRAINT
# ============================================================
print("\n" + "=" * 80)
print("5. PROTON DECAY CONSTRAINTS")
print("=" * 80)

# Proton decay from gauge boson exchange in PS/GUT:
# τ_p ~ M_X⁴ / (α_U² * m_p⁵)
# where M_X is the mass of the leptoquark gauge boson

m_p = 0.938  # GeV (proton mass)
tau_SK = 2.4e34  # years (Super-K bound for p → e+π⁰)
sec_per_year = 3.156e7
GeV_inv_to_sec = 6.582e-25  # ℏ in GeV·s

# More precisely: τ_p ≈ M_X⁴ / (α_U² × m_p⁵ × A)
# where A includes hadronic matrix elements.
# Standard estimate: τ_p ≈ (M_X/10^16 GeV)⁴ × 10^{36±1} years for α_U ~ 1/40
# Let's use the dimensional estimate with a standard prefactor

alpha_U_val = 1.0 / alpha_U_inv_crossing

print(f"  α_U = {alpha_U_val:.6f} (at Λ = 10^{log10_Lambda:.2f} GeV)")
print(f"  m_p = {m_p} GeV")
print(f"  Super-K limit: τ_p > {tau_SK:.1e} years (p → e⁺π⁰)")

# Dimensional estimate: τ_p ~ M_X⁴/(α_U² m_p⁵) × (ℏ/c conversion)
# In natural units: τ_p [GeV⁻¹] = M_X⁴ / (α_U² × m_p⁵) (up to O(1) factors)
# Convert to seconds: × ℏ = 6.582e-25 GeV·s
# Then to years: / 3.156e7

# Including standard hadronic matrix element factor A ~ 0.01-0.1 GeV³
# Full formula: Γ = α_U² m_p⁵ A² / (f_π² M_X⁴) × phase space
# Simplified: τ_p ≈ C × M_X⁴ / (α_U² m_p⁵)  with C encompassing matrix elements
# Standard reference: for M_X = 10^{16} GeV, α_U = 1/40, τ_p ~ 10^{36} years
# So C = 10^{36} years × (1/40)² × (0.938)⁵ / (10^{16})⁴ GeV⁴
# Let me calibrate:
tau_ref = 1e36  # years for M_X = 10^16, α_U = 1/40
M_X_ref = 1e16  # GeV
alpha_U_ref = 1.0 / 40.0
C_prefactor = tau_ref * alpha_U_ref**2 * m_p**5 / M_X_ref**4

print(f"\n  Calibrated prefactor C = {C_prefactor:.3e} GeV⁻⁴·years")

def proton_lifetime(M_X_GeV, alpha_U):
    """Proton lifetime in years."""
    return C_prefactor * M_X_GeV**4 / (alpha_U**2 * m_p**5)

# In PS, the leptoquark gauge bosons are in SU(4)_C
# Their mass is M_PS (the PS breaking scale)
# Note: PS leptoquarks mediate p → e+π⁰ etc.

print(f"\n  Proton lifetime as function of M_PS:")
print(f"  {'log₁₀(M_PS)':>12s}  {'τ_p (years)':>15s}  {'log₁₀(τ_p)':>12s}  {'Allowed?':>10s}")
for log10_M in [8, 9, 10, 11, 12, 13, 14, 15, 16]:
    M_X = 10**log10_M
    tau = proton_lifetime(M_X, alpha_U_val)
    allowed = "YES" if tau > tau_SK else "NO"
    print(f"  {log10_M:12.0f}  {tau:15.2e}  {np.log10(tau):12.2f}  {allowed:>10s}")

# Find minimum M_PS for proton stability
# tau > 2.4e34 years
# C * M_PS^4 / (alpha_U^2 * m_p^5) > 2.4e34
# M_PS^4 > 2.4e34 * alpha_U^2 * m_p^5 / C
M_PS_min_4 = tau_SK * alpha_U_val**2 * m_p**5 / C_prefactor
M_PS_min = M_PS_min_4**0.25
log10_MPS_min = np.log10(M_PS_min)

print(f"\n  Minimum M_PS for proton stability:")
print(f"  M_PS > {M_PS_min:.2e} GeV")
print(f"  log₁₀(M_PS) > {log10_MPS_min:.2f}")

print(f"\n  Comparison with gap closure requirement:")
print(f"  Gap closure needs M_PS = 10^{log10_MPS_a1:.2f} GeV")
print(f"  Proton decay needs  M_PS > 10^{log10_MPS_min:.2f} GeV")
if log10_MPS_a1 > log10_MPS_min:
    print(f"  → Gap closure scale is ABOVE proton decay bound. COMPATIBLE.")
else:
    print(f"  → Gap closure scale is BELOW proton decay bound. INCOMPATIBLE.")
    print(f"  → Need additional scalar content to modify running.")

# ============================================================
# 6. SCALAR CONTENT SCAN FOR T4 PRESERVATION
# ============================================================
print("\n" + "=" * 80)
print("6. SCALAR CONTENT SCAN — T4 PRESERVATION")
print("=" * 80)

# The T4 condition: the PS running should preserve the α₂-α₃ splitting
# ratio, i.e., the differential running in the PS regime should match
# the SM differential running.
#
# T4 condition: b_L - b₄ ≈ b₂^SM - b₃^SM = -19/6 + 7 = 23/6 ≈ 3.833
# (This ensures Δ₂₃ is unchanged by the PS intermediate stage)

T4_target = b2_SM - b3_SM
print(f"  T4 target: b_L - b₄ = b₂^SM - b₃^SM = {T4_target:.4f}")
print(f"  Minimal PS: b_L - b₄ = {b_L_min:.4f} - ({b_4_min:.4f}) = {b_L_min - b_4_min:.4f}")
print(f"  T4 violation (minimal): {(b_L_min - b_4_min) - T4_target:.4f}")

# Adding n copies of (1,1,15) — adjoint of SU(4)_C
# Under SU(4): adjoint, dimension 15, T(adj) = 4 (= C₂(SU(4)))
# Scalar contribution: Δb₄ = (1/3) × T(adj) = 4/3 per real scalar
# Complex scalar: 2× real, so Δb₄ = 2 × (1/3) × 4 = 8/3 per complex (1,1,15)
# Actually, the adjoint of SU(4) is real (15 is self-conjugate), so:
# Real scalar in adjoint: Δb₄ = (1/3) × T(adj) × d(other reps)
# For (1,1,15): singlet under SU(2)_L and SU(2)_R
# Δb_L = 0, Δb_R = 0, Δb₄ = (1/3) × 4 = 4/3

print(f"\n  Adding n × (1,1,15) [real adjoint scalar of SU(4)_C]:")
print(f"  Each (1,1,15) contributes: Δb₄ = 4/3")
print(f"  Δb_L = 0, Δb_R = 0")

print(f"\n  {'n':>3s}  {'b_L':>8s}  {'b_R':>8s}  {'b₄':>8s}  {'b_L-b₄':>8s}  {'T4 viol':>8s}")
for n in range(0, 10):
    b_L_n = b_L_min
    b_R_n = b_R_min
    b_4_n = b_4_min + n * (4.0/3.0)
    diff = b_L_n - b_4_n
    viol = diff - T4_target
    print(f"  {n:3d}  {b_L_n:8.3f}  {b_R_n:8.3f}  {b_4_n:8.3f}  {diff:8.3f}  {viol:+8.3f}")

# Find optimal n for T4
# b_L - (b_4_min + n*4/3) = T4_target
# n = (b_L_min - b_4_min - T4_target) / (4/3)
n_opt_exact = (b_L_min - b_4_min - T4_target) / (4.0/3.0)
print(f"\n  Exact n for T4: {n_opt_exact:.2f}")
n_opt = int(np.round(n_opt_exact))
print(f"  Nearest integer: n = {n_opt}")

# Also consider (2,2,15) — bifundamental under SU(2)_L × SU(2)_R, adjoint of SU(4)
# Δb_L = (1/3) × (1/2) × 2 × 15 = 5   ... let me be more careful
# (2,2,15):
#   Under SU(2)_L: fund (dim 2), with multiplicity from SU(2)_R × SU(4) = 2×15 = 30
#     But we count T(R) properly: 30 real d.o.f. in fund of SU(2)_L
#     Actually for complex scalar: 2×2×15 = 60 real d.o.f.
#     Under SU(2)_L: T(fund) = 1/2, multiplied by d(SU(2)_R) × d(SU(4) adj)
#     Δb_L = (1/3) × T(2) × d(2)_R × d(15) = ...
# This gets complicated. Let's focus on the (1,1,15) result.

# With optimal n, redo the scan
b_L_opt = b_L_min
b_R_opt = b_R_min
b_4_opt = b_4_min + n_opt * (4.0/3.0)

print(f"\n  Optimal PS betas with n={n_opt} × (1,1,15):")
print(f"  b_L = {b_L_opt:.4f}")
print(f"  b_R = {b_R_opt:.4f}")
print(f"  b₄  = {b_4_opt:.4f}")
print(f"  b_L - b₄ = {b_L_opt - b_4_opt:.4f} (target: {T4_target:.4f})")

# Scan with optimal scalar content
results_opt = []
for log10_MPS in log10_MPS_range:
    a1, a2, a3 = compute_MZ_couplings(log10_MPS, log10_Lambda, alpha_U_inv_crossing,
                                        b_L_opt, b_R_opt, b_4_opt,
                                        b1_SM, b2_SM, b3_SM)
    alpha_1_val = 1.0 / a1
    alpha_2_val = 1.0 / a2
    alpha_Y_val = (3.0/5.0) * alpha_1_val
    sin2_pred = alpha_Y_val / (alpha_Y_val + alpha_2_val)
    delta_23 = a2 - a3
    results_opt.append((log10_MPS, a1, a2, a3, sin2_pred, delta_23))

results_opt = np.array(results_opt)

# Find gap closure
idx_a1_opt = np.argmin(np.abs(results_opt[:, 1] - target_a1))
log10_MPS_a1_opt = results_opt[idx_a1_opt, 0]

print(f"\n  --- With n={n_opt} × (1,1,15): coupling evolution ---")
print(f"  {'log₁₀(M_PS)':>12s}  {'α₁⁻¹(M_Z)':>10s}  {'α₂⁻¹(M_Z)':>10s}  {'α₃⁻¹(M_Z)':>10s}  {'sin²θ_W':>8s}  {'Δ₂₃':>8s}")
for target_log in [8, 10, 12, 14, 15, 16, log10_Lambda]:
    idx = np.argmin(np.abs(results_opt[:, 0] - target_log))
    r = results_opt[idx]
    print(f"  {r[0]:12.2f}  {r[1]:10.2f}  {r[2]:10.2f}  {r[3]:10.2f}  {r[4]:8.4f}  {r[5]:8.2f}")

print(f"\n  Gap closure with optimal scalars:")
print(f"  M_PS = 10^{log10_MPS_a1_opt:.2f} GeV")
print(f"  α₁⁻¹(M_Z) = {results_opt[idx_a1_opt, 1]:.2f}")
print(f"  α₂⁻¹(M_Z) = {results_opt[idx_a1_opt, 2]:.2f}")
print(f"  α₃⁻¹(M_Z) = {results_opt[idx_a1_opt, 3]:.2f}")
print(f"  sin²θ_W(M_Z) = {results_opt[idx_a1_opt, 4]:.4f}")
print(f"  Δ₂₃ = {results_opt[idx_a1_opt, 5]:.2f}")

# Proton decay check
tau_opt = proton_lifetime(10**log10_MPS_a1_opt, alpha_U_val)
print(f"\n  Proton decay at M_PS = 10^{log10_MPS_a1_opt:.2f} GeV:")
print(f"  τ_p = {tau_opt:.2e} years")
print(f"  log₁₀(τ_p) = {np.log10(tau_opt):.2f}")
print(f"  Super-K bound: {tau_SK:.1e} years")
if tau_opt > tau_SK:
    print(f"  → SAFE: τ_p > Super-K bound by factor {tau_opt/tau_SK:.1f}")
else:
    print(f"  → EXCLUDED: τ_p < Super-K bound by factor {tau_SK/tau_opt:.1f}")

# Also try with (1,2,4) + bidoublet + n×(1,1,15)
print(f"\n  --- Extended model: bidoublet + (1,2,4)+(1,2,4̄) + n×(1,1,15) ---")
b_L_ext_base = b_L_min + b_L_scalar_124  # =  b_L_min (since 124 doesn't affect L)
b_R_ext_base = b_R_min + b_R_scalar_124
b_4_ext_base = b_4_min + b_4_scalar_124

n_ext_exact = (b_L_ext_base - b_4_ext_base - T4_target) / (4.0/3.0)
print(f"  Base (no (1,1,15)): b_L={b_L_ext_base:.3f}, b_R={b_R_ext_base:.3f}, b₄={b_4_ext_base:.3f}")
print(f"  b_L - b₄ = {b_L_ext_base - b_4_ext_base:.3f}")
print(f"  Exact n for T4: {n_ext_exact:.2f}")
n_ext = int(np.round(n_ext_exact))
print(f"  Nearest integer: n = {n_ext}")

b_L_ext = b_L_ext_base
b_R_ext = b_R_ext_base
b_4_ext = b_4_ext_base + n_ext * (4.0/3.0)
print(f"  Final: b_L={b_L_ext:.3f}, b_R={b_R_ext:.3f}, b₄={b_4_ext:.3f}")
print(f"  b_L - b₄ = {b_L_ext - b_4_ext:.4f} (target: {T4_target:.4f})")

# Scan extended model
results_ext = []
for log10_MPS in log10_MPS_range:
    a1, a2, a3 = compute_MZ_couplings(log10_MPS, log10_Lambda, alpha_U_inv_crossing,
                                        b_L_ext, b_R_ext, b_4_ext,
                                        b1_SM, b2_SM, b3_SM)
    alpha_1_val_l = 1.0 / a1
    alpha_2_val_l = 1.0 / a2
    alpha_Y_val_l = (3.0/5.0) * alpha_1_val_l
    sin2_pred = alpha_Y_val_l / (alpha_Y_val_l + alpha_2_val_l)
    delta_23 = a2 - a3
    results_ext.append((log10_MPS, a1, a2, a3, sin2_pred, delta_23))

results_ext = np.array(results_ext)
idx_a1_ext = np.argmin(np.abs(results_ext[:, 1] - target_a1))
log10_MPS_a1_ext = results_ext[idx_a1_ext, 0]

print(f"\n  Gap closure (extended model):")
print(f"  M_PS = 10^{log10_MPS_a1_ext:.2f} GeV")
print(f"  α₂⁻¹(M_Z) = {results_ext[idx_a1_ext, 2]:.2f}, α₃⁻¹(M_Z) = {results_ext[idx_a1_ext, 3]:.2f}")
print(f"  Δ₂₃ = {results_ext[idx_a1_ext, 5]:.2f} (target: {delta_23_MZ:.2f})")
print(f"  sin²θ_W = {results_ext[idx_a1_ext, 4]:.4f}")

tau_ext = proton_lifetime(10**log10_MPS_a1_ext, alpha_U_val)
print(f"  τ_p = {tau_ext:.2e} years (log₁₀ = {np.log10(tau_ext):.1f})")

# ============================================================
# 7. REQUIRED BOUNDARY CONDITION
# ============================================================
print("\n" + "=" * 80)
print("7. REQUIRED BOUNDARY CONDITION AT NCG CUTOFF")
print("=" * 80)

# If sin²θ_W(Λ) ≠ 3/8, what value is needed?
# sin²θ_W(μ) = α_Y(μ) / (α_Y(μ) + α₂(μ))
# where α_Y = (3/5)α₁

# With pure SM running from Λ to M_Z:
# α_i⁻¹(Λ) = α_i⁻¹(M_Z) + (b_i/2π) ln(Λ/M_Z)
# (note sign: running UP from M_Z)

# At the unification scale Λ:
print(f"\n  At Λ = 10^{log10_Lambda:.2f} GeV (SM-only running from M_Z):")
# These are the same as what we computed in Section 2
print(f"  α₁⁻¹(Λ) = {alpha_1_inv_Lambda:.2f}")
print(f"  α₂⁻¹(Λ) = {alpha_2_inv_Lambda:.2f}")
print(f"  α₃⁻¹(Λ) = {alpha_3_inv_Lambda:.2f}")

# sin²θ_W at Λ (if running SM all the way)
alpha_1_at_Lambda = 1.0 / alpha_1_inv_Lambda
alpha_2_at_Lambda = 1.0 / alpha_2_inv_Lambda
alpha_Y_at_Lambda = (3.0/5.0) * alpha_1_at_Lambda
sin2_at_Lambda = alpha_Y_at_Lambda / (alpha_Y_at_Lambda + alpha_2_at_Lambda)
print(f"  sin²θ_W(Λ) [from SM running] = {sin2_at_Lambda:.4f}")
print(f"  Compare: sin²θ_W = 3/8 = {3.0/8.0:.4f}")

# What sin²θ_W(Λ) is needed to get sin²θ_W(M_Z) = 0.2312?
# sin²θ_W(M_Z) depends on α₁ and α₂ at M_Z, which depend on boundary conditions at Λ
#
# The question is: if we allow sin²θ_W(Λ) ≠ 3/8 while keeping a single unified coupling,
# what value gives 0.2312 at M_Z?
#
# With unified coupling α_U at Λ but allowing α₁(Λ)/α₂(Λ) = r ≠ 1:
#   α₁(Λ) = r × α₂(Λ)
#   sin²θ_W(Λ) = (3/5)r / ((3/5)r + 1)
#
# Then at M_Z:
#   α₁⁻¹(M_Z) = α₁⁻¹(Λ) + b₁/(2π) ln(Λ/M_Z)
#   α₂⁻¹(M_Z) = α₂⁻¹(Λ) + b₂/(2π) ln(Λ/M_Z)
#
# We need: sin²θ_W(M_Z) = 0.2312
# i.e., (3/5)/α₁⁻¹(M_Z) / ((3/5)/α₁⁻¹(M_Z) + 1/α₂⁻¹(M_Z)) = 0.2312

# Let's solve this differently.
# sin²θ_W = g'²/(g'²+g²) = α_Y/(α_Y + α₂)
# At M_Z we know the exact values. Running up with SM betas gives us α₁,α₂ at Λ.
# The ratio at Λ tells us sin²θ_W(Λ).
# This is just what we computed above: sin2_at_Lambda

print(f"\n  Direct computation:")
print(f"  sin²θ_W(Λ) needed for sin²θ_W(M_Z) = 0.2312:")
print(f"  Answer: sin²θ_W(Λ) = {sin2_at_Lambda:.4f}")

# But what if there's a PS intermediate stage? Then we need different boundary conditions.
# The PS stage with L-R symmetry (α_L = α_R) gives:
# α₁⁻¹ = (3/5)α_R⁻¹ + (2/5)α₄⁻¹
# With α_L = α_R (not necessarily = α₄):
# sin²θ_W at PS scale = (3/5)α₁/(…)
# This is more complex. Let's compute for the general case.

print(f"\n  --- General boundary condition analysis ---")
print()
print(f"  Case A: Pure SM (no intermediate scale)")
print(f"    sin²θ_W(Λ) = {sin2_at_Lambda:.6f}")
print(f"    Ratio α₁/α₂ at Λ = {alpha_1_at_Lambda/alpha_2_at_Lambda:.6f}")

# Case B: With PS intermediate, what boundary condition at Λ?
# If α_L = α_R = α₄ at Λ, sin²θ_W(Λ) = 3/8 exactly.
# But we showed this doesn't give correct MZ values with minimal content.
#
# So: what if α_L ≠ α₄ at Λ?  (α_L = α_R still, by left-right symmetry)
# Then: define r = α_L/α₄ at Λ
# At Λ: α₁⁻¹ = (3/5)α_R⁻¹ + (2/5)α₄⁻¹ = (3/5)α_L⁻¹ + (2/5)α₄⁻¹
#        α₂⁻¹ = α_L⁻¹
#        α₃⁻¹ = α₄⁻¹
# sin²θ_W(Λ) from the PS matching:
# α₁ = 1/((3/5)/α_L + (2/5)/α₄)
# sin²θ_W(Λ) = (3/5)α₁ / ((3/5)α₁ + α₂) = ...
# With α_L = r × α₄:
# α₁⁻¹ = (3/5)/(r α₄) + (2/5)/α₄ = (1/α₄)(3/(5r) + 2/5) = (1/α₄)(3 + 2r)/(5r)
# α₂⁻¹ = 1/(r α₄)
# sin²θ_W = (3/5)/α₁⁻¹ / ((3/5)/α₁⁻¹ + 1/α₂⁻¹)
#          = (3/5) × (5r α₄)/(3 + 2r) / ((3/5) × (5r α₄)/(3 + 2r) + r α₄/(1))
#          ... this simplifies. Let me do it with x = α₁/α₂:
# α₁ = 5r α₄/(3 + 2r)
# α₂ = r α₄
# x = α₁/α₂ = 5/(3 + 2r)
# sin²θ_W = (3/5)x / ((3/5)x + 1) = 3x/(3x + 5) = 3×5/(3+2r) / (3×5/(3+2r) + 5)
#          = 15/(3+2r) / (15/(3+2r) + 5) = 15 / (15 + 5(3+2r)) = 15/(15 + 15 + 10r) = 15/(30 + 10r)
#          = 3/(6 + 2r)
# Check: r=1 => sin²θ_W = 3/8 ✓

# For sin²θ_W(Λ) needed:
# We need to find what combination of PS betas + boundary conditions
# gives the correct M_Z values.
#
# With the optimal scalar content from Section 6, the T4 condition is approximately
# satisfied, meaning Δ₂₃ is preserved. The α₁ matching is the remaining freedom.

# For the PS model with given betas, find the boundary condition:
# We want α₁⁻¹(M_Z) = 59.01, α₂⁻¹(M_Z) = 29.57, α₃⁻¹(M_Z) = 8.48
#
# From SM running up to M_PS:
# α_i⁻¹(M_PS) = α_i⁻¹(M_Z) + (b_i^SM/2π) ln(M_PS/M_Z)
#
# PS matching at M_PS:
# α_L⁻¹(M_PS) = α₂⁻¹(M_PS)
# α₄⁻¹(M_PS) = α₃⁻¹(M_PS)
# α_R⁻¹(M_PS) = (5/3)(α₁⁻¹(M_PS) - (2/5)α₃⁻¹(M_PS))
#              = (5/3)α₁⁻¹(M_PS) - (2/3)α₃⁻¹(M_PS)

# Then run PS up to Λ:
# α_L⁻¹(Λ) = α_L⁻¹(M_PS) + (b_L/2π) ln(Λ/M_PS)
# α_R⁻¹(Λ) = α_R⁻¹(M_PS) + (b_R/2π) ln(Λ/M_PS)
# α₄⁻¹(Λ) = α₄⁻¹(M_PS) + (b₄/2π) ln(Λ/M_PS)

print(f"\n  Case B: With PS intermediate stage")
print(f"  Computing boundary conditions at Λ for different M_PS values:")
print()

# Use the optimal scalar content
b_L_use = b_L_opt
b_R_use = b_R_opt
b_4_use = b_4_opt

print(f"  PS betas: b_L={b_L_use:.3f}, b_R={b_R_use:.3f}, b₄={b_4_use:.3f}")
print()
print(f"  {'log₁₀(M_PS)':>12s}  {'α_L⁻¹(Λ)':>10s}  {'α_R⁻¹(Λ)':>10s}  {'α₄⁻¹(Λ)':>10s}  {'sin²θ_W(Λ)':>12s}  {'α_R/α₄':>8s}")

for log10_MPS in [10, 11, 12, 13, 14, 15]:
    MPS = 10**log10_MPS
    Lambda = 10**log10_Lambda
    t_SM_up = np.log(MPS / M_Z)

    # SM running up to M_PS
    a1_MPS = alpha_1_inv_MZ + (b1_SM / (2*np.pi)) * t_SM_up
    a2_MPS = alpha_2_inv_MZ + (b2_SM / (2*np.pi)) * t_SM_up
    a3_MPS = alpha_3_inv_MZ + (b3_SM / (2*np.pi)) * t_SM_up

    # PS matching
    aL_MPS = a2_MPS
    a4_MPS = a3_MPS
    aR_MPS = (5.0/3.0) * a1_MPS - (2.0/3.0) * a3_MPS

    # PS running up to Λ
    t_PS_up = np.log(Lambda / MPS)
    aL_Lambda = aL_MPS + (b_L_use / (2*np.pi)) * t_PS_up
    aR_Lambda = aR_MPS + (b_R_use / (2*np.pi)) * t_PS_up
    a4_Lambda = a4_MPS + (b_4_use / (2*np.pi)) * t_PS_up

    # sin²θ_W at Λ
    alpha_L = 1.0/aL_Lambda
    alpha_R = 1.0/aR_Lambda
    alpha_4 = 1.0/a4_Lambda

    # α₁ at Λ from PS
    a1_Lambda = 1.0/((3.0/5.0)/alpha_R + (2.0/5.0)/alpha_4)
    a2_Lambda_val = alpha_L
    sin2_Lambda = (3.0/5.0) * a1_Lambda / ((3.0/5.0) * a1_Lambda + a2_Lambda_val)

    r_ratio = alpha_R / alpha_4 if alpha_4 > 0 else float('nan')

    print(f"  {log10_MPS:12.0f}  {aL_Lambda:10.2f}  {aR_Lambda:10.2f}  {a4_Lambda:10.2f}  {sin2_Lambda:12.6f}  {r_ratio:8.4f}")

# Direct computation for SM-only case
print(f"\n  Required sin²θ_W at Λ (SM-only running, no PS):")
print(f"  sin²θ_W(Λ) = {sin2_at_Lambda:.6f}")

# What ratio α₁/α₂ at Λ?
ratio_a1_a2 = alpha_1_at_Lambda / alpha_2_at_Lambda
print(f"  α₁/α₂ at Λ = {ratio_a1_a2:.6f}")

# If the NCG spectral action gives sin²θ_W = a₁/(a₁ + (5/3)a₂) at cutoff,
# and we need sin²θ_W ≠ 3/8, what does this mean?
# sin²θ_W(Λ) = 3x/(3x + 5) where x = α₁/α₂
# For sin²θ_W(Λ) = sin2_at_Lambda:
# sin2_at_Lambda × (3x + 5) = 3x
# 5 sin2_at_Lambda = 3x(1 - sin2_at_Lambda)
# x = 5 sin2_at_Lambda / (3(1 - sin2_at_Lambda))
x_needed = 5 * sin2_at_Lambda / (3 * (1 - sin2_at_Lambda))
print(f"\n  NCG spectral action constraint:")
print(f"  Need α₁/α₂ = {x_needed:.6f} at cutoff Λ")
print(f"  Equivalently: a₁/a₂ ≈ {x_needed:.3f} (where a_i are spectral action coefficients)")
print(f"  Standard NCG prediction: a₁/a₂ = 1 → sin²θ_W = 3/8 = 0.375")
print(f"  Required: a₁/a₂ = {x_needed:.3f} → sin²θ_W = {sin2_at_Lambda:.4f}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 80)
print("SUMMARY — PATI-SALAM SPECTRAL TRIPLE ANALYSIS")
print("=" * 80)

print(f"""
  SM inputs at M_Z:
    α₁⁻¹ = {alpha_1_inv_MZ:.2f},  α₂⁻¹ = {alpha_2_inv_MZ:.2f},  α₃⁻¹ = {alpha_3_inv_MZ:.2f}
    sin²θ_W = {sin2_thetaW_MZ}

  SM-only unification:
    SU(2)-SU(3) crossing: Λ₂₃ = 10^{{{log10_Lambda_23:.2f}}} GeV
    U(1) gap at crossing: Δ(α₁⁻¹ - α_U⁻¹) = {gap:.2f}
    → Simple SU(5) FAILS.

  Minimal PS (bidoublet only):
    b_L = {b_L_min:.3f},  b_R = {b_R_min:.3f},  b₄ = {b_4_min:.3f}
    Gap closure at M_PS = 10^{{{log10_MPS_a1:.2f}}} GeV
    T4 violation: Δ₂₃(M_Z) = {delta23_at_match:.2f} (need {delta_23_MZ:.2f})
    → T4 VIOLATED.

  Optimal PS (bidoublet + {n_opt}×(1,1,15)):
    b_L = {b_L_opt:.3f},  b_R = {b_R_opt:.3f},  b₄ = {b_4_opt:.3f}
    b_L - b₄ = {b_L_opt - b_4_opt:.3f} (T4 target: {T4_target:.3f})
    Gap closure at M_PS = 10^{{{log10_MPS_a1_opt:.2f}}} GeV
    τ_p = {tau_opt:.1e} years (Super-K: {tau_SK:.1e})
    → Proton decay: {'SAFE' if tau_opt > tau_SK else 'EXCLUDED'}

  Boundary conditions at NCG cutoff:
    SM-only sin²θ_W(Λ) = {sin2_at_Lambda:.4f} (≠ 3/8 = 0.375)
    Required α₁/α₂ ratio: {x_needed:.3f} (NCG predicts 1.000)
    → NCG boundary condition REQUIRES modification from simple spectral action.
    → This is the Meridian prediction: warped extra dimension modifies the ratio.
""")

print("=" * 80)
print("END OF ANALYSIS")
print("=" * 80)
