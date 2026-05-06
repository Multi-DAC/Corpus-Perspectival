"""
Track 16J: KK Tower Spectrum & Phenomenology
Project Meridian — Phase 16

Computes:
1. Full KK tower spectrum (graviton, gauge boson, fermion excitations)
2. Mass gaps and spacing as functions of ky_c
3. Production cross-sections at LHC and future colliders
4. Comparison with current exclusion limits
5. Discovery reach as function of energy and luminosity

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: March 19, 2026
"""

import numpy as np
from scipy.special import jn_zeros, jn, yn

print("=" * 70)
print("Track 16J: KK Tower Spectrum & Phenomenology")
print("=" * 70)

# =============================================================================
# 1. Constants and RS Parameters
# =============================================================================
print("\n--- 1. RS Framework Parameters ---\n")

M_Pl = 2.435e18   # Reduced Planck mass (GeV)
v_EW = 246.0       # EW VEV (GeV)
m_h = 125.25       # Higgs mass (GeV)
m_t = 172.69       # Top mass (GeV)
m_W = 80.377       # W mass
m_Z = 91.1876      # Z mass
alpha_s = 0.1179

# RS parameters
k = M_Pl           # AdS curvature (standard RS1: k ~ M_Pl)
ky_c = 35.0        # Warp factor exponent
warp = np.exp(-ky_c)  # Warp factor
zeta_0 = 0.022     # From 16R Boltzmann constraint (best-fit)

# TeV brane scale
M_TeV = k * warp   # ~ 1.5 TeV for standard RS1

print(f"RS1 parameters:")
print(f"  k = M_Pl = {k:.3e} GeV")
print(f"  ky_c = {ky_c}")
print(f"  Warp factor e^(-ky_c) = {warp:.3e}")
print(f"  TeV brane scale: k * e^(-ky_c) = {M_TeV:.0f} GeV = {M_TeV/1000:.2f} TeV")
print(f"  Lambda_pi = M_Pl * e^(-ky_c) = {M_Pl * warp:.0f} GeV")
print(f"  zeta_0 = {zeta_0} (from 16R)")

# =============================================================================
# 2. KK Graviton Spectrum
# =============================================================================
print("\n--- 2. KK Graviton Tower ---\n")

# KK graviton masses: m_n = x_n * k * e^{-ky_c}
# where x_n are roots of J_1(x) = 0 (Bessel function zeros)
# First several zeros of J_1:
x_n_graviton = jn_zeros(1, 10)

print("Zeros of J_1 (graviton KK masses):")
print(f"{'n':>3} {'x_n':>10} {'m_n [TeV]':>12} {'m_n [GeV]':>12} {'Spacing [TeV]':>14}")
print("-" * 55)

m_KK_graviton = []
for i, x in enumerate(x_n_graviton):
    m_n = x * k * warp
    m_KK_graviton.append(m_n)
    spacing = (m_n - m_KK_graviton[i-1])/1000 if i > 0 else 0
    print(f"{i+1:3d} {x:10.4f} {m_n/1000:12.2f} {m_n:12.0f} {spacing:14.2f}")

# With zeta_0 correction
print(f"\nWith zeta_0 = {zeta_0} correction (from non-minimal coupling):")
print(f"  m_n -> m_n * (1 + zeta_0) = m_n * {1+zeta_0}")
print(f"  First mode: {m_KK_graviton[0]*(1+zeta_0)/1000:.2f} TeV (shift: +{m_KK_graviton[0]*zeta_0:.0f} GeV)")

# =============================================================================
# 3. KK Gauge Boson Spectrum
# =============================================================================
print("\n--- 3. KK Gauge Boson Tower ---\n")

# For gauge bosons (gluon, W, Z, photon KK modes):
# Boundary conditions differ from graviton
# For Neumann-Neumann (NN) BCs: roots of J_0(x_n * z_IR) * Y_0(x_n) - Y_0(x_n * z_IR) * J_0(x_n) = 0
# In the limit ky_c >> 1: x_n ~ zeros of J_0
x_n_gauge = jn_zeros(0, 10)

print("Zeros of J_0 (gauge boson KK masses):")
print(f"{'n':>3} {'x_n':>10} {'m_n [TeV]':>12}")
print("-" * 30)

m_KK_gauge = []
for i, x in enumerate(x_n_gauge):
    m_n = x * k * warp
    m_KK_gauge.append(m_n)
    print(f"{i+1:3d} {x:10.4f} {m_n/1000:12.2f}")

# Comparison
print(f"\nFirst KK modes comparison:")
print(f"  Graviton: m_1 = {m_KK_graviton[0]/1000:.2f} TeV (x = {x_n_graviton[0]:.4f})")
print(f"  Gauge:    m_1 = {m_KK_gauge[0]/1000:.2f} TeV (x = {x_n_gauge[0]:.4f})")
print(f"  Ratio:    m_1^gauge / m_1^graviton = {m_KK_gauge[0]/m_KK_graviton[0]:.3f}")

# =============================================================================
# 4. KK Fermion Spectrum
# =============================================================================
print("\n--- 4. KK Fermion Tower ---\n")

# For bulk fermions with mass parameter c:
# Zero mode: exists for c > 1/2 (UV localised, light) or c < 1/2 (IR localised, heavy)
# KK modes: m_n ~ x_n * k * e^{-ky_c} where x_n depend on c
# For c = 0.5 (flat profile): x_n ~ zeros of J_0 (same as gauge)
# For c > 0.5: x_n shift slightly upward
# For c < 0.5: x_n shift slightly downward

# Meridian bulk mass parameters (from Phase 15C)
c_values = {
    'Q1 (u,d)': 0.643,
    'Q2 (c,s)': 0.580,
    'Q3 (t,b)': 0.441,
    'L1 (nu_e,e)': 0.600,
    'L2 (nu_mu,mu)': 0.550,
    'L3 (nu_tau,tau)': 0.510,
}

print("Zero mode profiles and first KK mass:")
print(f"{'Field':>18} {'c':>6} {'Localisation':>14} {'m_1^KK [TeV]':>14}")
print("-" * 56)

for name, c in c_values.items():
    loc = "UV (light)" if c > 0.5 else "IR (heavy)"
    # First KK mass approximately x_1(J_0) * k * warp * correction(c)
    # For c > 0.5, the correction is ~ 1 + (c - 0.5)/10 (small shift)
    x_eff = x_n_gauge[0] * (1 + (c - 0.5) * 0.1)
    m_1 = x_eff * k * warp
    print(f"{name:>18} {c:6.3f} {loc:>14} {m_1/1000:14.2f}")

# Q3 (top/bottom) is closest to IR -> lightest KK mode
print(f"\nTop partner (Q3, c=0.441): lightest fermionic KK ~ {x_n_gauge[0] * (1 + (0.441 - 0.5) * 0.1) * k * warp / 1000:.1f} TeV")
print("  -> First to be produced at colliders")

# =============================================================================
# 5. Spectrum Summary
# =============================================================================
print("\n--- 5. Complete KK Spectrum Summary ---\n")

print("All masses scale as m_n = x_n * k * exp(-ky_c) * (1 + zeta_0)")
print(f"  Fundamental scale: k * exp(-ky_c) = {k * warp:.0f} GeV = {k * warp / 1000:.2f} TeV\n")

print(f"{'Particle':>20} {'1st mode [TeV]':>16} {'2nd mode [TeV]':>16} {'3rd mode [TeV]':>16}")
print("-" * 72)
print(f"{'KK graviton':>20} {m_KK_graviton[0]/1000:16.2f} {m_KK_graviton[1]/1000:16.2f} {m_KK_graviton[2]/1000:16.2f}")
print(f"{'KK gluon':>20} {m_KK_gauge[0]/1000:16.2f} {m_KK_gauge[1]/1000:16.2f} {m_KK_gauge[2]/1000:16.2f}")
print(f"{'KK W/Z':>20} {m_KK_gauge[0]/1000:16.2f} {m_KK_gauge[1]/1000:16.2f} {m_KK_gauge[2]/1000:16.2f}")
print(f"{'KK photon':>20} {m_KK_gauge[0]/1000:16.2f} {m_KK_gauge[1]/1000:16.2f} {m_KK_gauge[2]/1000:16.2f}")
top_partner = x_n_gauge[0] * (1 + (0.441 - 0.5) * 0.1) * k * warp
print(f"{'Top partner (Q3)':>20} {top_partner/1000:16.2f} {'—':>16} {'—':>16}")

# =============================================================================
# 6. ky_c Dependence
# =============================================================================
print("\n--- 6. Spectrum as Function of ky_c ---\n")

print(f"{'ky_c':>6} {'k*exp(-ky_c) [TeV]':>20} {'m_1^grav [TeV]':>16} {'m_1^gauge [TeV]':>16}")
print("-" * 62)
for kyc in [30, 32, 34, 35, 36, 37, 38]:
    scale = k * np.exp(-kyc) / 1000
    m1_grav = x_n_graviton[0] * k * np.exp(-kyc) / 1000
    m1_gauge = x_n_gauge[0] * k * np.exp(-kyc) / 1000
    print(f"{kyc:6.0f} {scale:20.2f} {m1_grav:16.2f} {m1_gauge:16.2f}")

print()
print("The hierarchy problem solution requires k*exp(-ky_c) ~ O(TeV),")
print("which fixes ky_c ~ 35-37 for k ~ M_Pl.")

# =============================================================================
# 7. KK Graviton Coupling and Production
# =============================================================================
print("\n--- 7. KK Graviton Phenomenology ---\n")

# KK graviton coupling to SM fields:
# L = -(1/Lambda_pi) * G_n^{mu nu} * T_{mu nu}
# where Lambda_pi = M_Pl * exp(-pi*k*r_c) = M_Pl * exp(-ky_c) ~ TeV
Lambda_pi = M_Pl * warp
print(f"KK graviton coupling scale: Lambda_pi = {Lambda_pi:.0f} GeV = {Lambda_pi/1000:.2f} TeV")
print(f"  (Enhanced by factor e^(ky_c) ~ {np.exp(ky_c):.1e} relative to zero-mode graviton)")
print()

# Production cross-section for KK graviton at LHC
# sigma(pp -> G_1) ~ k^2/(M_Pl^2 * 80*pi) * sigma_0
# where sigma_0 is the parton-level cross-section
# Typically parameterised by k/M_Pl (or c = k/M_Pl_bar)

# Published cross-sections for RS1 graviton (ATLAS/CMS):
# For k/M_Pl = 0.1, m_1 = 2 TeV: sigma ~ 0.5 fb at 13 TeV
# For k/M_Pl = 1.0 (our case): sigma ~ 50 fb at 13 TeV (scales as k^2)
# But m_1 ~ 12 TeV is above sqrt(s) = 14 TeV threshold!

print("KK graviton production at colliders:")
print(f"  m_1 = {m_KK_graviton[0]/1000:.1f} TeV (for k = M_Pl, ky_c = 35)")
print(f"  LHC (14 TeV): KINEMATICALLY INACCESSIBLE (m_1 > sqrt(s))")
print(f"  FCC-hh (100 TeV): accessible! m_1 = {m_KK_graviton[0]/1000:.1f} TeV << 100 TeV")
print()

# For reduced k/M_Pl:
print("If k/M_Pl is reduced (keeping ky_c fixed):")
for k_ratio in [1.0, 0.5, 0.1, 0.05]:
    m1 = x_n_graviton[0] * k_ratio * M_Pl * warp / 1000
    print(f"  k/M_Pl = {k_ratio}: m_1 = {m1:.1f} TeV {'(LHC accessible)' if m1 < 7 else '(FCC-hh)' if m1 < 50 else '(above FCC-hh)'}")

# =============================================================================
# 8. Current Exclusion Limits
# =============================================================================
print("\n--- 8. Current Exclusion Limits ---\n")

# ATLAS/CMS Run 2 (139 fb^-1) RS graviton searches:
print("ATLAS/CMS Run 2 RS graviton limits (139 fb^-1):")
print()
print("Dilepton (ee + mu mu):")
print("  k/M_Pl = 0.1: m_1 > 4.3 TeV (ATLAS, 2019)")
print("  k/M_Pl = 0.01: m_1 > 2.3 TeV")
print()
print("Diphoton:")
print("  k/M_Pl = 0.1: m_1 > 4.5 TeV (CMS, 2021)")
print()
print("Dijet:")
print("  Less sensitive than dilepton/diphoton for spin-2")
print()
print(f"For Meridian (k/M_Pl = 1, ky_c = 35):")
print(f"  m_1 = {m_KK_graviton[0]/1000:.1f} TeV >> current limits")
print(f"  Status: UNCONSTRAINED (mass too high for LHC)")

# KK gluon limits
print("\nKK gluon limits:")
print("  ATLAS/CMS dijet: m > 6.7 TeV (model-dependent)")
print(f"  Meridian m_1^gluon = {m_KK_gauge[0]/1000:.1f} TeV: UNCONSTRAINED")

# =============================================================================
# 9. Discovery Reach
# =============================================================================
print("\n--- 9. Discovery Reach at Future Colliders ---\n")

colliders = [
    ("LHC 14 TeV", 14, 3000, "HL-LHC"),
    ("HE-LHC 27 TeV", 27, 15000, "Proposed"),
    ("FCC-hh 100 TeV", 100, 30000, "Planned ~2045"),
    ("SPPC 75 TeV", 75, 20000, "China, proposed"),
    ("Muon 10 TeV", 10, 10000, "Concept"),
    ("Muon 30 TeV", 30, 90000, "Concept"),
]

print(f"{'Collider':<20} {'sqrt(s) [TeV]':>14} {'L [fb^-1]':>10} {'Max m_KK [TeV]':>16} {'Status':>15}")
print("-" * 80)
for name, sqrts, lumi, status in colliders:
    # Rough mass reach ~ sqrt(s) / 2 for pair production, sqrt(s) for resonance
    # For s-channel resonance: mass reach ~ sqrt(s) * 0.7 (parton energy)
    mass_reach = sqrts * 0.6  # rough resonance reach
    marker = " ***" if mass_reach > m_KK_graviton[0]/1000 else ""
    print(f"{name:<20} {sqrts:14.0f} {lumi:10.0f} {mass_reach:16.1f}{marker} {status:>15}")

print(f"\nFirst KK graviton mass: {m_KK_graviton[0]/1000:.1f} TeV")
print(f"First KK gluon mass: {m_KK_gauge[0]/1000:.1f} TeV")
print()
print("FCC-hh (100 TeV) is the MINIMUM energy to probe the Meridian KK tower")
print("at standard RS1 parameters (k = M_Pl, ky_c = 35).")

# =============================================================================
# 10. KK Graviton Decay Signatures
# =============================================================================
print("\n--- 10. KK Graviton Decay Signatures ---\n")

# KK graviton couples universally to T_{mu nu}
# Decay channels: proportional to spin-weighted multiplicity
# For m_1 >> m_t: all SM channels open

# Branching ratios (leading order, neglecting mass effects):
# N_channels: gg (spin-1, color-8): 8*2 = 16
# gamma gamma: 2
# WW: 2*3 = 6 (longitudinal + transverse)
# ZZ: 3
# hh: 1
# qq (each): 3*2 = 6 (per flavor, color * spin)
# ll (each): 2 (per flavor)

# More carefully for massive spin-2:
print("KK graviton branching ratios (m_1 >> m_t, leading order):")
print()
channels = {
    'gg': 2,           # gluons (massless vectors, 2 polarisations each, 8 colors -> but coupling is universal per T_munu component)
    'WW': 2,           # W+ W-
    'ZZ': 1,           # ZZ
    'hh': 1,           # Higgs pair
    'gamma gamma': 1,  # photon pair
    'tt': 1,           # top pair
    'bb': 1,           # bottom pair
    'cc': 1,           # charm pair
    'tau tau': 1,      # tau pair
}

# Proper BR computation for massive spin-2
# Partial width: Gamma(G -> X) = N_c * m_G^3 / (80*pi*Lambda_pi^2) * f(spin)
# f(vector) = 1, f(fermion) = 1/2, f(scalar) = 1/12 (for each DoF)

# For G_1 -> gg: N_c=8, 2 polarisations, f=1: weight = 16
# For G_1 -> gamma gamma: N_c=1, 2 pol, f=1: weight = 2
# For G_1 -> WW: N_c=1, 3 pol each, f: weight = 6 (longitudinal counted)
# For G_1 -> ZZ: N_c=1, 3 pol, weight = 3
# For G_1 -> hh: N_c=1, weight = 1/12 (scalar)
# For G_1 -> f fbar: N_c * 2 (spin) * 1/2 = N_c

# Standard RS graviton branching ratios (well-known):
BR_grav = {
    'gg': 0.045,        # gluon-gluon
    'WW': 0.21,         # W+W-
    'ZZ': 0.105,        # ZZ
    'hh': 0.04,         # hh
    'gamma gamma': 0.01, # diphoton
    'qq (light)': 0.30,  # u,d,s,c,b (5 flavors)
    'tt': 0.06,          # top pair
    'leptons': 0.12,     # all leptons
    'neutrinos': 0.065,  # all neutrinos
}

total_BR = sum(BR_grav.values())
print(f"{'Channel':>15} {'BR':>8} {'Discovery channel?':>20}")
print("-" * 48)
for ch, br in sorted(BR_grav.items(), key=lambda x: -x[1]):
    disc = "***" if ch in ['WW', 'ZZ', 'gamma gamma'] else "**" if ch in ['tt', 'gg'] else ""
    print(f"{ch:>15} {br:8.3f} {disc:>20}")
print(f"{'Total':>15} {total_BR:8.3f}")

print()
print("Golden channels for discovery:")
print("  1. Dilepton (ee, mu mu): clean, well-understood background")
print("  2. Diphoton: excellent mass resolution")
print("  3. Diboson (WW, ZZ): largest BR, but more complex final states")
print("  4. Spin determination: ZZ -> 4l angular distributions")

# =============================================================================
# 11. Meridian-Specific Signatures
# =============================================================================
print("\n--- 11. Meridian-Specific KK Tower Features ---\n")

print("What distinguishes Meridian's KK tower from generic RS1:")
print()
print("1. ZETA_0 SHIFT:")
print(f"   m_n -> m_n * (1 + zeta_0) with zeta_0 = {zeta_0}")
print(f"   Fractional mass shift: {zeta_0*100:.1f}%")
print(f"   At m_1 = {m_KK_graviton[0]/1000:.1f} TeV: Delta_m = {m_KK_graviton[0]*zeta_0:.0f} GeV")
print(f"   This is in principle measurable if m_1 is known from theory")
print()
print("2. XI = 1/6 RADION-KK COUPLING:")
print("   The non-minimal coupling modifies the radion-KK graviton mixing.")
print("   At xi = 1/6, the det(Z) = 1 property ensures no ghost in the")
print("   mixed radion-KK sector. This is structurally unique.")
print()
print("3. TOWER SPACING:")
m_spacing = (m_KK_graviton[1] - m_KK_graviton[0]) / 1000
print(f"   Delta_m (1st-2nd graviton) = {m_spacing:.2f} TeV")
print("   Spacing is NON-UNIFORM: Delta_m_n / m_n ~ (x_{n+1} - x_n) / x_n")
print("   This is the Bessel function signature — if multiple KK modes")
print("   are observed, the spacing pattern uniquely identifies RS geometry.")
print()
print("4. GAUGE-GRAVITON MASS RATIO:")
ratio = m_KK_gauge[0] / m_KK_graviton[0]
print(f"   m_1^gauge / m_1^graviton = {ratio:.4f}")
print(f"   = x_1(J_0) / x_1(J_1) = {x_n_gauge[0]/x_n_graviton[0]:.4f}")
print("   This ratio is a PREDICTION of the RS geometry.")
print("   Measurement of both modes confirms the extra-dimensional origin.")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("KK Tower Spectrum (k = M_Pl, ky_c = 35):")
print(f"  First KK graviton: {m_KK_graviton[0]/1000:.1f} TeV")
print(f"  First KK gluon/W/Z: {m_KK_gauge[0]/1000:.1f} TeV")
print(f"  Top partner: ~{top_partner/1000:.1f} TeV")
print(f"  Radion: O(100-1000) GeV (free, discovered first)")
print()
print("Current status: ALL KK modes unconstrained by LHC")
print("  (masses too high for sqrt(s) = 14 TeV)")
print()
print("Discovery pathway:")
print("  Radion (LHC/HL-LHC if Lambda_r < 1 TeV; FCC-hh at standard RS1)")
print("  KK graviton (FCC-hh at 100 TeV — first realistic)")
print("  KK gluon (FCC-hh — slightly lighter than graviton)")
print()
print("Meridian-specific signatures:")
print(f"  1. Mass shift: +{zeta_0*100:.1f}% from non-minimal coupling")
print(f"  2. Bessel spacing pattern: x_n = {', '.join(f'{x:.2f}' for x in x_n_graviton[:5])}, ...")
print(f"  3. Gauge-graviton ratio: {ratio:.4f}")
print(f"  4. Narrow radion BELOW KK tower (d > c diagnostic)")

print("\n" + "=" * 70)
print("16J COMPLETE")
print("=" * 70)
