"""
Door 2b — AdS/CFT Holographic Analysis of Gauge Coupling Corrections on RS₁
=============================================================================

Project Meridian, Phase 21, Track 21A.4 (continued)

The RS₁ orbifold has a well-known holographic dual: a 4D large-N CFT
coupled to dynamical gravity, with the IR brane corresponding to
spontaneous conformal symmetry breaking.

We use this duality to compute non-perturbative gauge-dependent corrections
to sin²θ_W. The key question: can the holographic dual produce the required
a₁/a₂ = 0.776 (ε₂ = 0.289)?

Sections:
1. RS/CFT Dictionary & Parameters
2. Holographic Gauge Self-Energy (Perturbative CFT Running)
3. Non-Perturbative Condensate Corrections
4. Partial Compositeness Corrections
5. CFT Instanton Contributions (π₃ Topological Effects)
6. Goldberger-Wise Stabilization Backreaction
7. Parameter Space Scan: What Condensate Values Give a₁/a₂ = 0.776?
8. Combined Analysis & Verdict

Author: Clawd (Project Meridian)
Date: 2026-03-23
"""

import numpy as np
from scipy import optimize, integrate, special
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# SECTION 1: RS/CFT Dictionary & Parameters
# =============================================================================

print("=" * 80)
print("DOOR 2b: AdS/CFT HOLOGRAPHIC ANALYSIS OF GAUGE COUPLING CORRECTIONS")
print("=" * 80)

# RS₁ geometry parameters
kL = 35.0                          # Warp factor exponent (standard hierarchy solution)
k = 1e17                           # AdS curvature scale (GeV) ~ M_Planck / sqrt(8π)
L = kL / k                         # Physical length of extra dimension
Lambda_IR = k * np.exp(-kL)        # IR brane scale ~ TeV
Lambda_UV = k                      # UV brane scale
M_Z = 91.2                         # Z boson mass (GeV)

# CFT parameters from RS/CFT dictionary
# N_CFT² ~ (M_Pl / k)² ~ (kL)^(3/2) in the simplest estimate
# More precisely: N_CFT² = (16π² / g₅²k) × (Volume factor)
# The "number of colors" of the dual CFT
N_CFT_squared = (kL)**3            # Standard estimate: N² ~ (kL)³
N_CFT = np.sqrt(N_CFT_squared)     # Effective N
# Alternative estimates
N_CFT_sq_alt1 = 16 * np.pi**2 * kL  # From 5D gauge-gravity matching
N_CFT_sq_alt2 = (kL)**(3/2)         # Minimal estimate

# Gauge group data
# SM gauge groups with their Casimirs and dimensions
gauge_groups = {
    'U(1)_Y': {
        'name': 'U(1)_Y',
        'dim_adj': 1,
        'C2_adj': 0,           # Abelian: no adjoint Casimir
        'C2_fund': 0,          # No fundamental for U(1)
        'b0_SM': -41/6,        # SM one-loop beta coefficient (convention: negative = not asymptotically free)
        'g2_MZ': 4*np.pi*0.01017,   # g'² at M_Z (α₁ = 5/3 × α_Y = 0.01017)
        'alpha_MZ': 0.01017,
        'has_instantons': False,  # π₃(U(1)) = 0
        'N_gauge': 1,
        'Y2_trace': 11/3,     # Tr[Y²] over one SM generation
    },
    'SU(2)_L': {
        'name': 'SU(2)_L',
        'dim_adj': 3,
        'C2_adj': 2,
        'C2_fund': 3/4,
        'b0_SM': 19/6,        # SM one-loop beta coefficient (with Higgs)
        'g2_MZ': 4*np.pi*0.03378,   # g² at M_Z (α₂ = 0.03378)
        'alpha_MZ': 0.03378,
        'has_instantons': True,   # π₃(SU(2)) = Z
        'N_gauge': 2,
        'N_ferm_doublets': 12,  # 3 generations × (q_L, l_L) × 2 colors... = 12 doublets
    },
    'SU(3)_c': {
        'name': 'SU(3)_c',
        'dim_adj': 8,
        'C2_adj': 3,
        'C2_fund': 4/3,
        'b0_SM': 7.0,         # SM one-loop beta coefficient
        'g2_MZ': 4*np.pi*0.1179,    # g_s² at M_Z (α₃ = 0.1179)
        'alpha_MZ': 0.1179,
        'has_instantons': True,   # π₃(SU(3)) = Z
        'N_gauge': 3,
        'N_ferm_triplets': 12,  # 3 gen × (u_L, d_L, u_R, d_R) = 12 triplets
    },
}

# GUT-scale values (running up from M_Z)
alpha_GUT = 1/25.0    # Approximate unified coupling
g2_GUT = 4*np.pi*alpha_GUT

# Required correction
a1_over_a2_target = 0.776
epsilon_2_target = 1/a1_over_a2_target - 1  # = 0.2887

print("\n--- RS/CFT Dictionary ---")
print(f"kL = {kL}")
print(f"k (UV scale) = {k:.1e} GeV")
print(f"Λ_IR = ke^{{-kL}} = {Lambda_IR:.2e} GeV")
print(f"ln(Λ_UV/Λ_IR) = kL = {kL}")
print(f"N_CFT² = (kL)³ = {N_CFT_squared:.0f}")
print(f"N_CFT = {N_CFT:.1f}")
print(f"N_CFT² (alt: 16π²kL) = {N_CFT_sq_alt1:.0f}")
print(f"N_CFT² (alt: (kL)^{{3/2}}) = {N_CFT_sq_alt2:.1f}")
print(f"α_GUT ≈ 1/{1/alpha_GUT:.0f}")
print(f"\nTarget: a₁/a₂ = {a1_over_a2_target}")
print(f"Required: ε₂ = {epsilon_2_target:.4f} (29% increase in SU(2) gauge kinetic coefficient)")


# =============================================================================
# SECTION 2: Holographic Gauge Self-Energy (Perturbative CFT Running)
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 2: PERTURBATIVE CFT RUNNING")
print("=" * 80)

print("""
In the holographic dual, the gauge coupling at scale μ receives three contributions:

  1/g_i²(μ) = 1/g_i²(Λ_UV) + Δ_i^{elem}(μ) + Δ_i^{CFT}(μ)

where:
  Δ_i^{elem}  = elementary (UV brane-localized) SM running = (b_i^{SM}/16π²) ln(Λ_UV/μ)
  Δ_i^{CFT}   = composite (CFT) running

The CFT contribution comes from the current-current two-point function:

  ⟨J_μ^a(p) J_ν^b(-p)⟩ = δ^{ab} (p²η_{μν} - p_μp_ν) Π_i(p²)

The holographic computation of Π_i(p²):
  Π_i(p²) = (1/g₅²) × [∂_y G_A(y, p²)|_{y=0}]

where G_A(y, p²) is the bulk-to-boundary propagator for the gauge field.
""")

# The bulk-to-boundary propagator in RS₁
# For a gauge field A_μ in AdS₅ slice: A_μ(x, y) = A_μ(x) × φ(y, p)
# where φ satisfies: e^{2ky} ∂_y(e^{-2ky} ∂_y φ) + p² φ = 0
# with φ(0) = 1 (Dirichlet at UV), ∂_y φ(L) = 0 (Neumann at IR)

# The solution involves Bessel functions:
# φ(y, p) = e^{ky} [Y₁(p/k) J₁(pe^{ky}/k) - J₁(p/k) Y₁(pe^{ky}/k)] / [Y₁(p/k) J₁(pe^{kL}/k) - J₁(p/k) Y₁(pe^{kL}/k)]

# For p << k (momenta well below UV cutoff), the self-energy:
# Π_i(p²) = (k/g₅²) × [1 + (p²/(2k²)) × (1 - e^{-2kL}) + ...]

# The gauge-universal part:
# 1/g₄² = k*L/g₅²  (tree-level, from zero-mode integral over extra dimension)

# The perturbative CFT correction (large-N, leading in 1/N):
# Δ_i^{CFT,pert} = (N_CFT²/16π²) × C_i × ln(Λ_UV/Λ_IR)

# where C_i encodes the CFT current two-point function coefficient.

# For a CONFORMAL field theory, the current-current OPE coefficient C_J is fixed
# by the central charge. But the RS dual is NOT exactly conformal — conformal symmetry
# is broken by the IR brane. The PERTURBATIVE running (above Λ_IR) is approximately
# conformal, with corrections suppressed by (μ/k)^{2Δ-4} for nearly-marginal deformations.

# Key result: In a large-N gauge theory (which is the CFT dual), the current two-point
# function for a GLOBAL symmetry G is:
#   C_J^{G} = N_CFT² × c_G
# where c_G depends on the EMBEDDING of G in the CFT.

# If the SM gauge group is a SUBGROUP of the CFT global symmetry, then c_G is the
# same for all SM gauge factors (by the embedding). This would preserve gauge universality.
#
# If the SM gauge factors couple to DIFFERENT CFT sectors (e.g., SU(3) couples to
# colored composites, SU(2) to weak composites), then c_G can differ.

# In the RS₁ model, ALL gauge fields propagate in the same bulk. The dual CFT has a
# SINGLE set of "color" degrees of freedom with global symmetry containing SU(3)×SU(2)×U(1).
# Therefore:

print("\n--- Result 2.1: Perturbative CFT Running is Gauge-Universal ---")
print("""
In the RS₁ dual, all SM gauge fields are bulk fields coupling to the SAME CFT.
The dual CFT has a global symmetry SU(3)×SU(2)×U(1) (minimally), and the
current-current OPE coefficient for each factor is determined by the embedding.

For a unified embedding (all gauge factors from the same CFT sector):
  C_J^{SU(3)} / C_J^{SU(2)} / C_J^{U(1)} scales with dim(adj)

The perturbative correction to 1/g_i²:
  Δ_i^{CFT,pert} = (N_CFT² / 16π²) × (dim(adj_i) × c₀) × ln(Λ_UV/Λ_IR)

where c₀ is a universal constant of the CFT.
""")

# Compute perturbative CFT running for each gauge group
c0_CFT = 1.0  # Universal CFT constant (normalized)

for name, data in gauge_groups.items():
    dim_adj = data['dim_adj']
    # Perturbative CFT contribution (log running)
    delta_pert = (N_CFT_squared / (16 * np.pi**2)) * dim_adj * c0_CFT * kL
    print(f"  {name}: Δ_i^{{CFT,pert}} = (N²/16π²) × dim(adj) × c₀ × kL")
    print(f"        = ({N_CFT_squared:.0f}/{16*np.pi**2:.1f}) × {dim_adj} × {c0_CFT} × {kL}")
    print(f"        = {delta_pert:.1f}")

print("""
The perturbative part contributes to gauge coupling running but is GAUGE-UNIVERSAL
in the ratio (it enters each 1/g_i² proportionally to the tree-level contribution).

This confirms T12 from the holographic perspective: the perturbative CFT running
cannot break gauge universality. The running is large (N² enhanced) but universal.
""")

# The correction to a₁/a₂ from perturbative CFT running:
# a_i ∝ 1/g_i² = (tree) + Δ_i^{pert}
# If Δ_i^{pert}/tree = same for all i, then a₁/a₂ = 1 (unchanged)

print("Perturbative CFT contribution to a₁/a₂: ZERO (gauge universal)")
print("This is the holographic dual of T12.\n")


# =============================================================================
# SECTION 3: Non-Perturbative Condensate Corrections
# =============================================================================

print("=" * 80)
print("SECTION 3: NON-PERTURBATIVE CONDENSATE CORRECTIONS")
print("=" * 80)

print("""
When the CFT confines/breaks at scale Λ_IR, the non-perturbative dynamics
generates condensates. These modify the current-current correlator:

  Π_i(p²) = Π_i^{pert}(p²) + Π_i^{NP}(p²)

The non-perturbative part involves condensates of the form:
  ⟨O_dim⟩ ~ Λ_IR^dim × f(N_CFT, representations)

The leading condensate contributing to the gauge coupling:
  Π_i^{NP} = Σ_n c_{i,n} × ⟨O_n⟩ / p^{2n-2}

At p² = 0 (the gauge coupling at zero momentum), the relevant operator
is the dimension-4 gluon condensate (in CFT language, the stress-tensor
trace anomaly):
  ⟨T_μ^μ⟩ ~ N_CFT² × Λ_IR⁴

For the GAUGE COUPLING correction, the relevant OPE coefficient involves
the current-current correlator at the conformal breaking scale:

  δ(1/g_i²)^{NP} = (1/Λ_IR²) × ⟨J_i J_i⟩^{NP}

In the large-N expansion:
  δ(1/g_i²)^{NP} = (N_CFT² / 16π²) × f_i^{NP}

where f_i^{NP} is an O(1) number that depends on the gauge group through
the quantum numbers of the condensing operators.
""")

# The gauge-dependent condensate correction
# In the CFT dual, the distinction arises because:
# 1. SU(3) composites form glueballs (pure glue) + mesons (quark-antiquark)
# 2. SU(2) composites form technirhos, technipions, etc.
# 3. U(1) has no confinement, only Schwinger pair production at strong coupling

# The key physics: in a confining CFT with global SU(3)×SU(2)×U(1),
# the confinement dynamics PRESERVES the global symmetry (by Vafa-Witten theorem
# for vector-like theories, or 't Hooft anomaly matching for chiral theories).
# However, the STRENGTH of the condensate is representation-dependent.

# Large-N scaling of condensates:
# ⟨O_i⟩ ~ N_CFT^{power} × Λ_IR^{dim(O)}
# The power depends on the operator:
# - Singlet operators (glueball ≡ Tr F²): N_CFT² (planar dominance)
# - Adjoint operators: N_CFT
# - Fundamental operators: N_CFT^{1/2}

# For gauge coupling correction, the relevant operator is the current-current
# condensate ⟨J_μ^a J_ν^a⟩, which is in the adjoint × adjoint representation.

# Decomposition: adj × adj = singlet + adj + symmetric + antisymmetric
# The singlet component ⟨Tr(J² )⟩ is gauge-universal (same for all gauge groups)
# The non-singlet components can be gauge-dependent.

# CRITICAL INSIGHT: The non-perturbative correction to 1/g_i² is the
# SINGLET projection of the current-current condensate. This is because
# the gauge kinetic term is Tr(F_i²), which is a singlet under the gauge group.

print("\n--- Result 3.1: Structure of Condensate Corrections ---")

# Let's compute the condensate corrections numerically
# The holographic computation uses the AdS/CFT formula:

# In the bulk, the gauge field propagator near p² = 0 has the form:
#   G_A(y, y'; p²) = G_A^{(0)} + p² G_A^{(1)} + ...
# The gauge coupling comes from G_A^{(1)}.

# The non-perturbative part corresponds to KK modes below the confinement scale.
# These are the "composite resonances" of the CFT.

# The KK contribution to the gauge self-energy:
#   Π_i^{KK}(p²) = Σ_n F_n² / (p² - m_n²)
# where m_n are KK masses and F_n are decay constants.

# At p² = 0:
#   Π_i^{KK}(0) = -Σ_n F_n² / m_n²

# The decay constants F_n depend on the overlap of the KK mode with the UV brane:
#   F_n ~ √(2/L) × sin(nπ/2) × (correction from warp factor)

# For the first few KK modes (n ~ 1-10), the contribution is:
m_KK_1 = np.pi * k * np.exp(-kL)  # First KK mass ~ π × Λ_IR
print(f"\nFirst KK mass: m_KK^(1) = π × Λ_IR = {m_KK_1:.2e} GeV")
print(f"Number of KK modes below cutoff: ~ e^{{kL}} = {np.exp(kL):.2e}")

# The KK sum for the gauge self-energy
# Weinberg sum rules constrain the sum:
#   Σ_n F_n² = f_π² (pion decay constant of the CFT)
#   Σ_n F_n² m_n² = 0 (second Weinberg sum rule, for conformal theory)

# The pion decay constant in the RS dual:
f_pi_CFT_sq = N_CFT_squared * Lambda_IR**2 / (16 * np.pi**2)
f_pi_CFT = np.sqrt(f_pi_CFT_sq)
print(f"CFT 'pion' decay constant: f_π = N × Λ_IR / 4π = {f_pi_CFT:.2e} GeV")

# The condensate contribution to the gauge coupling:
# δ(1/g_i²)^{NP} = Π_i^{NP}(0) = Σ_n (F_n,i² / m_n²)
#
# In the large-N limit with a vector-like spectrum (as in RS), the sum is:
# Π_i^{NP}(0) ~ (N_CFT² / 16π²) × (1 / m_ρ²) × F_ρ,i²
# where ρ is the first CFT resonance (lightest KK mode).
#
# The GAUGE-DEPENDENT part comes from the REPRESENTATION of the resonance.
# A vector resonance in the adjoint of SU(N) has:
#   F_ρ,i² ~ dim(adj_i) × (universal factor)
# This is STILL gauge-universal (proportional to tree-level).
#
# BUT: a scalar resonance (from the radion/dilaton sector) or a fermion
# composite (from partial compositeness) can have non-universal couplings.

# Let's quantify the possible gauge-dependent effects

# The radion/dilaton of RS₁ couples to each gauge group through the trace anomaly:
# L_radion = (r/Λ_r) × (β_i / 2g_i) × F_i²
# where β_i is the beta function coefficient.

# The beta functions are DIFFERENT for each gauge group!
# This is a concrete, calculable source of gauge-dependence.

print("\n--- Result 3.2: Radion/Dilaton Trace Anomaly Coupling ---")
print("""
The radion (stabilization modulus, dual to the dilaton of the CFT) couples
to gauge fields through the trace anomaly:

  L_rad = (r/Λ_r) × Σ_i (β_i / 2g_i) × F_i,μν F_i^μν

The beta function coefficients b_i^{SM} are:
  b₁ = -41/6 (U(1)_Y, GUT normalized)
  b₂ = 19/6  (SU(2)_L)
  b₃ = 7     (SU(3)_c)

The radion VEV ⟨r⟩ shifts the gauge couplings:
  δ(1/g_i²) = (⟨r⟩/Λ_r) × (b_i / 8π²)

This IS gauge-dependent! Different b_i → different corrections.
""")

# SM beta function coefficients (one-loop)
b1_SM = -41/6   # U(1)_Y (GUT normalized: b₁ = -41/10 with α₁ = 5/3 αY)
b2_SM = 19/6    # SU(2)_L
b3_SM = 7.0     # SU(3)_c

# But wait — we need the FULL beta function including the CFT sector.
# In the holographic picture, the CFT contribution to the beta function is:
# b_i^{CFT} = (N_CFT² / 16π²) × c_i^{CFT}
# where c_i^{CFT} is the CFT current central charge.

# The total radion coupling:
# δ(1/g_i²)_rad = (⟨r⟩/Λ_r) × (b_i^{SM} + b_i^{CFT}) / (8π²)

# However, the CFT contribution to b_i is gauge-universal (by the same argument
# as Section 2). So the gauge-DEPENDENT part of the radion correction is:
# δ(1/g_i²)_rad^{g-dep} = (⟨r⟩/Λ_r) × b_i^{SM} / (8π²)

# Now: how big is ⟨r⟩/Λ_r?
# In the Goldberger-Wise stabilization, the radion mass m_r ~ Λ_IR × ε
# where ε ~ 1/(kL) ~ 1/35.
# The VEV is ⟨r⟩ ~ Λ_IR.
# Λ_r ~ Λ_IR (the radion decay constant).
# So ⟨r⟩/Λ_r ~ 1.

r_over_Lambda_r = 1.0  # O(1) in Goldberger-Wise

# Gauge-dependent correction from radion
delta_radion = {}
for name, data in gauge_groups.items():
    b_i = data['b0_SM']
    delta_i = r_over_Lambda_r * b_i / (8 * np.pi**2)
    delta_radion[name] = delta_i
    print(f"  {name}: δ(1/g_i²)_rad = (⟨r⟩/Λ_r) × b_i/(8π²) = {r_over_Lambda_r} × {b_i:.3f}/{8*np.pi**2:.2f} = {delta_i:.6f}")

# Now compute the RATIO correction
# a_i ∝ 1/g_i²
# At tree level: a₁ = a₂ = a₃ = a₀ = kL/(g₅² k) = L/g₅²
# The tree-level value: 1/g₄² = kL/g₅² (≈ 1/g_GUT²)
tree_level = 1/g2_GUT  # = 1/(4π α_GUT) = 25/(4π) ≈ 1.99

print(f"\nTree-level: 1/g₄² = 1/g²_GUT = {tree_level:.4f}")
print(f"(α_GUT = 1/25)")

# The correction to a₁/a₂:
# a₁/a₂ = (tree + δ₁) / (tree + δ₂)
# = 1 + (δ₁ - δ₂)/tree + O(δ²)
# ≈ 1 + (δ₁^{rad} - δ₂^{rad})/tree

delta_diff_12_rad = delta_radion['U(1)_Y'] - delta_radion['SU(2)_L']
a1_over_a2_rad = 1 + delta_diff_12_rad / tree_level

print(f"\nRadion contribution to a₁/a₂:")
print(f"  δ₁^{{rad}} - δ₂^{{rad}} = {delta_diff_12_rad:.6f}")
print(f"  Correction to a₁/a₂ = {delta_diff_12_rad/tree_level:.6f}")
print(f"  a₁/a₂ = 1 + {delta_diff_12_rad/tree_level:.6f} = {a1_over_a2_rad:.6f}")

print("""
The radion coupling through the SM beta functions gives a gauge-dependent
correction of order δ ~ b_i/(8π²) × (⟨r⟩/Λ_r). This is O(10⁻²), roughly
100× too small for the required 0.289 correction.

However, this is the ELEMENTARY sector radion coupling. The full correction
includes the CFT sector's response to the radion VEV.
""")


# =============================================================================
# SECTION 4: Full Holographic Computation — Bulk Self-Energy
# =============================================================================

print("=" * 80)
print("SECTION 4: HOLOGRAPHIC BULK SELF-ENERGY COMPUTATION")
print("=" * 80)

print("""
The holographic gauge self-energy is computed from the bulk gauge field
propagator on the RS₁ background. The key object is the spectral function:

  ρ_i(s) = (1/π) Im[Π_i(-s - iε)]

The spectral function has poles at the KK masses m_n and a continuum
above the gap Λ_IR. The gauge coupling correction at a scale μ:

  δ(1/g_i²)(μ²) = ∫_0^∞ ds ρ_i(s) / (s + μ²)

We compute this using the RS₁ Green's function.
""")

# The RS₁ Green's function for a gauge field
# In conformal coordinates z = (1/k)(e^{ky} - 1), the metric is:
#   ds² = (k/(1+kz))² (η_μν dx^μ dx^ν + dz²)
# with z ∈ [0, z_L] where z_L = (e^{kL}-1)/k ≈ e^{kL}/k

# The gauge field equation of motion (for transverse modes at momentum p):
#   [∂_z² - 2kz/(1+kz) ∂_z + p²/(1+kz)²] A(z, p) = 0

# This is equivalent to:
#   A'' + (p²/k²)(1+kz)^{-2} A = 0
# after rescaling. The solutions are Bessel functions of order 1.

# The bulk-to-boundary propagator (normalized to 1 at UV brane):
# A(z, p) = (1+kz) × [J₁(p(1+kz)/k) Y₁(p/k) - Y₁(p(1+kz)/k) J₁(p/k)]
#           / [J₁(p(1+kz_L)/k) Y₁(p/k) - Y₁(p(1+kz_L)/k) J₁(p/k)]
# evaluated with Neumann BC at IR brane.

# For p << k, the self-energy:
# Π(p²) = (k/g₅²) × {kL + (p²/k²) × [(e^{2kL}-1)/(2k) - L] + higher}

# The GAUGE-DEPENDENT part enters through LOOP corrections to the bulk propagator.
# At one loop in the bulk, virtual KK modes of different spin contribute differently
# to different gauge groups.

# However, the key NON-PERTURBATIVE effect is different: it comes from the
# IR brane dynamics, which in the holographic dual is the conformal symmetry breaking.

# Let's compute the spectral representation numerically
def compute_kk_spectrum(N_max=100):
    """Compute first N_max KK masses for gauge boson on RS₁"""
    # KK masses are determined by: J₁(m_n/Λ_IR) Y₁(m_n/Λ_UV) - Y₁(m_n/Λ_IR) J₁(m_n/Λ_UV) = 0
    # For kL >> 1, approximately: m_n ≈ (n - 1/4)π Λ_IR for n = 1, 2, 3, ...
    masses = np.array([(n - 0.25) * np.pi for n in range(1, N_max+1)]) * Lambda_IR
    return masses

def compute_decay_constants(masses, kL_val):
    """Compute KK mode decay constants (coupling to UV brane current)
    F_n² = 2 m_n² / (kL × m_n²) × [1/(J₁'(x_n))²]
    where x_n = m_n/Λ_IR are the Bessel zeros

    In the large-kL limit: F_n² ≈ 2 Λ_IR² / (kL)
    """
    # Approximate: all F_n are comparable in magnitude
    # F_n² ~ 2 Λ_IR² / kL (from normalization of KK wavefunctions)
    F_sq = 2 * Lambda_IR**2 / kL_val * np.ones_like(masses)
    return F_sq

kk_masses = compute_kk_spectrum(200)
kk_F_sq = compute_decay_constants(kk_masses, kL)

# The gauge coupling from KK sum:
# 1/g_i²(p²=0) = 1/g₅² × kL + Σ_n F_n² / m_n²
# The first term is gauge-universal (tree level).
# The KK sum contributes:
kk_sum = np.sum(kk_F_sq / kk_masses**2)
print(f"\nKK resonance sum: Σ F_n²/m_n² = {kk_sum:.6e} GeV⁻²")
print(f"Compared to tree: kL/g₅² ~ {kL/g2_GUT:.4f}")

# The KK sum is GAUGE-UNIVERSAL at tree level (same spectrum for all gauge groups)
# The gauge dependence enters at ONE LOOP in the CFT:

print("""
The KK resonance sum is gauge-universal at tree level.
Gauge dependence enters through:
  (a) Loop corrections to KK masses (gauge-dependent self-energies)
  (b) Loop corrections to decay constants (mixing with composites)
  (c) Non-perturbative effects (condensates, instantons)

The loop corrections (a,b) are perturbative and captured by the standard
RG running — they give the usual SM beta function contributions.

The non-perturbative effects (c) are the new physics.
""")


# =============================================================================
# SECTION 5: CFT Instanton Contributions (Topological Effects)
# =============================================================================

print("=" * 80)
print("SECTION 5: CFT INSTANTON CONTRIBUTIONS")
print("=" * 80)

print("""
The topological argument in AdS/CFT language:

In the CFT dual, the SM gauge symmetries are GLOBAL symmetries of the CFT
that are weakly gauged. The non-perturbative structure of the CFT includes:

  • SU(N_CFT) instantons: the CFT itself has instantons (θ_CFT term)
  • These affect ALL gauge groups equally (since they're in the CFT sector)

  • SM gauge instantons (in the elementary sector):
    - U(1)_Y: π₃(U(1)) = 0 → NO instantons → NO non-perturbative correction
    - SU(2)_L: π₃(SU(2)) = Z → instantons exist → non-perturbative correction
    - SU(3)_c: π₃(SU(3)) = Z → instantons exist → non-perturbative correction

The CFT instanton contribution to the current-current correlator:

For the SU(N_gauge) global symmetry current J_μ^a of the CFT:

  ⟨J_μ^a(x) J_ν^b(0)⟩_inst = C_inst × δ^{ab} × I_{μν}(x) × exp(-S_{CFT-inst})

where S_{CFT-inst} = 8π²/g_{CFT}² = 8π² × N_CFT / λ_CFT
(with λ_CFT = g_{CFT}² N_CFT the 't Hooft coupling).

In the RS dual, λ_CFT ~ kL ~ 35 (the CFT is strongly coupled!).
So g_{CFT}² ~ λ_CFT / N_CFT.
""")

# CFT instanton action
lambda_tHooft = kL  # 't Hooft coupling of the dual CFT ~ kL
g2_CFT = lambda_tHooft / N_CFT
S_CFT_inst = 8 * np.pi**2 / g2_CFT
exp_neg_S_CFT = np.exp(-S_CFT_inst)

print(f"λ_CFT ('t Hooft coupling) = kL = {lambda_tHooft}")
print(f"g²_CFT = λ/N = {g2_CFT:.4f}")
print(f"S_CFT_inst = 8π²/g²_CFT = {S_CFT_inst:.1f}")
print(f"exp(-S_CFT_inst) = {exp_neg_S_CFT:.2e}")

print(f"""
The CFT instanton suppression: exp(-{S_CFT_inst:.1f}) = {exp_neg_S_CFT:.2e}
This is HUGELY suppressed — the CFT instantons are irrelevant.

BUT: This is the wrong instanton. The relevant instantons are not in the
CFT gauge group SU(N_CFT), but in the GLOBAL symmetry that becomes the SM
gauge group. These are DIFFERENT objects.
""")

# The relevant object: instanton of the weakly-gauged SM symmetry
# within the CFT background.
#
# In the CFT, the SM gauge field is an external source for the global current.
# An "instanton" of this external source changes the topology of the gauge
# configuration of the EXTERNAL field, not the CFT.
#
# The instanton action for the SM gauge field, in the presence of the CFT,
# is modified by the CFT dynamics:
#
#   S_inst^{eff}(SU(N)) = (8π²/g_i²) × [1 - Π_i^{NP}(0) × g_i²]
#
# where Π_i^{NP}(0) is the non-perturbative CFT self-energy at zero momentum.

# In the strong-coupling regime (λ_CFT ~ kL >> 1), the CFT self-energy is:
#   Π_i^{NP}(0) ~ (N_CFT² / 16π²) × f_i

# The instanton amplitude:
#   Z_inst^i ~ exp(-S_inst^{eff,i}) × [prefactors]

# The correction to the gauge coupling from instantons-in-background-of-CFT:
#   δ(1/g_i²)_inst ~ (d/dθ²) ln Z |_{θ=0}
# where θ is the vacuum angle.

# For U(1): No instantons. δ(1/g₁²)_inst = 0.
# For SU(2): Instanton contribution exists.
# For SU(3): Instanton contribution exists.

print("--- Result 5.1: Instanton Correction to Gauge Coupling in CFT Background ---")

# The instanton-induced correction to the gauge coupling:
# In the holographic picture, this is computed by the bulk gauge field
# in an instanton background on the RS₁ geometry.

# From Section 1 of the resurgence analysis: the instanton action in the bulk
# is gauge-universal (S = 8π²/g₄²) but the PREFACTOR involves the fluctuation
# determinant, which IS gauge-dependent.

# The one-instanton correction to 1/g_i²:
# δ(1/g_i²)_1-inst = C_N × (8π²/g²)^{2N} × exp(-8π²/g²) × Λ_eff^{b_i}

# At the GUT scale:
for name in ['SU(2)_L', 'SU(3)_c']:
    data = gauge_groups[name]
    N = data['N_gauge']
    g2 = g2_GUT
    S_inst = 8 * np.pi**2 / g2
    prefactor = (S_inst)**(2*N) * np.exp(-S_inst)
    print(f"\n{name}: S_inst = 8π²/g² = {S_inst:.1f}")
    print(f"  Prefactor: S^{{2N}} × exp(-S) = {S_inst:.1f}^{2*N} × exp(-{S_inst:.1f})")
    print(f"  = {S_inst**(2*N):.2e} × {np.exp(-S_inst):.2e}")
    print(f"  = {prefactor:.2e}")

print("""
VERDICT on CFT instanton mechanism: The SM gauge instanton amplitude
(even in the CFT background) is exp(-8π²/g_GUT²) ~ 10⁻⁶⁸.
This is DEAD, same as in the bulk analysis.

The CFT RESHAPES the instanton landscape (through the self-energy Π),
but cannot make the instanton action vanish because g_i at the UV scale
is perturbative (α ~ 1/25).
""")

# HOWEVER: at the IR brane (in the holographic language, at the CFT confinement
# scale), the effective coupling is different.

print("--- Result 5.2: IR Brane Instanton in Holographic Language ---")

# At the IR brane, the effective coupling:
g2_eff_IR = {}
for name, data in gauge_groups.items():
    if data['has_instantons']:
        N = data['N_gauge']
        # The effective coupling at the IR brane includes the CFT contribution
        # g_eff²(IR) = g₄² × (1 + N_CFT²/(16π²) × g₄² × ln(Λ_UV/Λ_IR))
        # In the strong coupling regime, this is dominated by the CFT part:
        # g_eff²(IR) ~ g₄² × N_CFT²/(16π²) × g₄² × kL
        g2_eff = g2_GUT * (1 + N_CFT_squared * g2_GUT * kL / (16 * np.pi**2))
        # More directly: in the RS picture, g²_eff(IR) = g₄² × 4kL × e^{2kL}
        g2_eff_RS = g2_GUT * 4 * kL * np.exp(2*kL)
        S_inst_IR = 8 * np.pi**2 / g2_eff_RS if g2_eff_RS > 0 else 0
        exp_neg_S_IR = np.exp(-min(S_inst_IR, 700))  # cap to avoid overflow

        g2_eff_IR[name] = g2_eff_RS
        print(f"\n{name}:")
        print(f"  g²_eff(IR) = g₄² × 4kL × e^{{2kL}} = {g2_GUT:.3f} × {4*kL:.0f} × e^{{{2*kL:.0f}}}")
        print(f"  = {g2_eff_RS:.2e}")
        print(f"  S_inst(IR) = 8π²/g²_eff = {S_inst_IR:.2e}")
        print(f"  exp(-S) → 1 (strong coupling regime)")
        print(f"  Instanton gas is DENSE. Semiclassical expansion INVALID.")

print("""
In the holographic language: the elementary SM gauge field mixes with
composite CFT resonances. At the confinement scale, the mixing is maximal
and the effective coupling is strong. The instanton gas becomes dense,
and the standard semiclassical expansion breaks down.

This is EXACTLY the regime where gauge-dependent non-perturbative effects
can be O(1). The question is: what is the quantitative prediction?
""")


# =============================================================================
# SECTION 6: Large-N Estimate of Non-Perturbative Correction
# =============================================================================

print("=" * 80)
print("SECTION 6: LARGE-N ESTIMATE OF NON-PERTURBATIVE CORRECTIONS")
print("=" * 80)

print("""
In the large-N CFT, we can estimate the non-perturbative correction using
three complementary approaches:

  A. Current correlator OPE with condensates
  B. Holographic computation via bulk fields
  C. Partial compositeness mixing angles

All three are controlled by the same physics: the CFT dynamics at the
confinement scale Λ_IR.
""")

# Approach A: OPE with condensates
print("\n--- Approach A: Current Correlator OPE ---")
print("""
The current-current two-point function in the broken phase of the CFT:

  Π_i(Q²) = (N_CFT² / 16π²) × [ln(Q²/Λ_IR²) + Σ_n c_{i,n} (Λ_IR/Q)^{2n}]

The condensate corrections c_{i,n} are OPE coefficients × condensate VEVs.

For the dimension-4 operator (gluon condensate analogue):
  c_{i,2} = ⟨O₄⟩_i / Λ_IR⁴

In the large-N limit, the condensates are:
  ⟨O₄⟩_singlet ~ N_CFT² × Λ_IR⁴  (universal, gauge-blind)
  ⟨O₄⟩_adjoint_i ~ Λ_IR⁴ × h_i    (gauge-dependent)

where h_i is an O(1) coefficient that depends on the gauge group through
the representation content of the CFT states.
""")

# The non-perturbative correction to the gauge coupling
# evaluated at the cutoff scale Q² = Λ_UV²:
#
# δ(1/g_i²)^{NP} = (N_CFT²/16π²) × Σ_n c_{i,n} × (Λ_IR/Λ_UV)^{2n}
#
# The suppression factor:
suppression = (Lambda_IR / Lambda_UV)**2
print(f"OPE suppression factor: (Λ_IR/Λ_UV)² = (e^{{-kL}})² = e^{{-2kL}} = {suppression:.2e}")
print(f"This is TINY — OPE condensate corrections at the UV scale are negligible.\n")

# But wait — we don't evaluate at Λ_UV. We evaluate the SPECTRAL ACTION
# which integrates over ALL scales. The spectral action:
# Tr[f(D²/Λ²)] = Σ_n f(λ_n/Λ²)
# includes eigenvalues λ_n at ALL scales from Λ_IR to Λ_UV.

print("""
CRITICAL REALIZATION: The condensate OPE is suppressed at the UV scale
by (Λ_IR/Λ_UV)² ~ e^{-70} ~ 10^{-30}. But the spectral action integrates
over the ENTIRE KK spectrum, including modes near Λ_IR where the condensate
correction is O(1).

The total non-perturbative contribution to the spectral action:
  δ_i^{NP} = ∫ dλ ρ(λ) f(λ/Λ²) × [c_{i}(λ)]

where c_i(λ) is the non-perturbative modification of the spectral density
near eigenvalue λ, and is gauge-dependent for λ ~ Λ_IR.
""")

# Approach B: Holographic computation
print("\n--- Approach B: Holographic (AdS/CFT) Bulk Computation ---")
print("""
In the bulk RS₁ picture, the gauge kinetic coefficient is:

  a_i = (1/g₅²) × ∫₀^L dy e^{-2ky} × [1 + δ_i^{loop}(y)]

where δ_i^{loop}(y) includes loop corrections from KK modes.

The tree-level integral: ∫₀^L dy e^{-2ky} = (1 - e^{-2kL})/(2k) ≈ 1/(2k)
This is gauge-universal (T1/T12).

The one-loop correction:
  δ_i^{loop}(y) = (g₅² / 16π²) × Σ_fields b_{i,field} × Σ_n |ψ_n(y)|² × ln(m_n²/μ²)

The KK mode profiles |ψ_n(y)|² depend on the field type but NOT on the gauge
group. The gauge group enters only through:
  • b_{i,field} = beta function coefficient (perturbative — captured by SM running)
  • Non-perturbative dressing of the KK propagator near y = L (the strong-coupling region)
""")

# The non-perturbative dressing near the IR brane
# In the dual CFT language, this is the formation of bound states (mesons, baryons)
# from the composite sector.

# For each gauge group, the bound state spectrum is different:
# SU(3): colored bound states (glueballs + hadron-like objects)
# SU(2): weak-isospin bound states (technirho-like objects)
# U(1): no bound states (abelian — no confinement)

# The correction to the spectral action coefficient:
# δa_i^{NP} = (1/g₅²) × ∫_{L-δ}^L dy e^{-2ky} × δ_i^{NP}(y)
# where δ ranges over the "confinement region" near the IR brane.

# The width of the confinement region:
# In the dual CFT, the confinement transition happens at scale Λ_IR.
# In the bulk, this corresponds to the region y ∈ [L - 1/k, L] (width ~ 1/k).

# The integral over the confinement region:
# ∫_{L-1/k}^L dy e^{-2ky} ≈ e^{-2kL} × (1/k) × [1 + O(1)]
# ≈ (1/k) × e^{-2kL}

confinement_integral = (1/k) * np.exp(-2*kL)
tree_integral = 1 / (2*k)
ratio_conf_to_tree = confinement_integral / tree_integral

print(f"\nConfinement region integral / tree-level integral:")
print(f"  = (1/k)e^{{-2kL}} / (1/2k) = 2e^{{-2kL}} = {ratio_conf_to_tree:.2e}")
print(f"\nThis ratio is TINY: 2e^{{-70}} ~ {2*np.exp(-2*kL):.2e}")

print("""
PROBLEM: The IR brane region's contribution to the gauge kinetic coefficient
is exponentially suppressed by e^{-2kL} ~ 10^{-30} relative to the UV part.
Even if the non-perturbative correction is O(1) locally, it contributes
only O(10^{-30}) to the integrated gauge kinetic coefficient.

This is the WARP FACTOR SUPPRESSION: the same exponential hierarchy that
solves the gauge hierarchy problem also suppresses any IR brane effect
on the gauge coupling.
""")


# =============================================================================
# SECTION 7: Partial Compositeness and Anomalous Dimensions
# =============================================================================

print("=" * 80)
print("SECTION 7: PARTIAL COMPOSITENESS AND ANOMALOUS DIMENSIONS")
print("=" * 80)

print("""
In the holographic dual, SM fermions are partially composite: they mix with
CFT operators O_ψ of dimension Δ_ψ. The mixing angle ε_ψ determines the
fermion mass:
  m_ψ ~ ε_L × ε_R × Λ_IR × (Λ_IR/Λ_UV)^{Δ_L + Δ_R - 4}

The anomalous dimension of a CFT operator that couples to the gauge current:
  ⟨J_μ^a O†_ψ O_ψ⟩ ~ f(Δ_ψ, spin, representation)

The partial compositeness mixing modifies the gauge coupling through
wavefunction renormalization:

  1/g_i²(μ²) = 1/g_i²(tree) × Z_i(μ²)

where Z_i is the wavefunction renormalization factor from the mixing:
  Z_i = 1 + Σ_ψ ε_ψ² × c_i(ψ) × N_CFT × ln(Λ_UV/μ)

The coefficient c_i(ψ) depends on the REPRESENTATION of ψ under gauge
group i. This is a concrete source of gauge dependence!
""")

# SM fermion representations and their mixing parameters
# In the RS model, the bulk mass parameter c determines the localization:
# c > 1/2: UV-localized (small composite fraction)
# c < 1/2: IR-localized (large composite fraction)

fermion_data = {
    'q_L': {'c': 0.63, 'SU3': 'fund', 'SU2': 'fund', 'Y': 1/6, 'n_gen': 3},
    'u_R': {'c': 0.3, 'SU3': 'fund', 'SU2': 'singlet', 'Y': 2/3, 'n_gen': 3},
    'd_R': {'c': 0.6, 'SU3': 'fund', 'SU2': 'singlet', 'Y': -1/3, 'n_gen': 3},
    'l_L': {'c': 0.6, 'SU3': 'singlet', 'SU2': 'fund', 'Y': -1/2, 'n_gen': 3},
    'e_R': {'c': 0.6, 'SU3': 'singlet', 'SU2': 'singlet', 'Y': -1, 'n_gen': 3},
}

print("\nFermion localization parameters (RS bulk masses):")
print(f"{'Fermion':>6} | {'c':>5} | {'Profile':>15} | {'ε²':>12} | SU(3) | SU(2) | Y")
print("-" * 75)

for name, data in fermion_data.items():
    c = data['c']
    # Composite fraction: ε² ~ (Λ_IR/Λ_UV)^{2c-1} for c > 1/2 (UV-localized)
    # ε² ~ 1 for c < 1/2 (IR-localized)
    if c > 0.5:
        eps_sq = np.exp(-(2*c - 1)*kL)
        profile = "UV-localized"
    else:
        eps_sq = 1.0
        profile = "IR-localized"
    data['eps_sq'] = eps_sq
    print(f"{name:>6} | {c:5.2f} | {profile:>15} | {eps_sq:12.2e} | {data['SU3']:>5} | {data['SU2']:>5} | {data['Y']:>5.2f}")

# The partial compositeness correction to the gauge coupling
# For each fermion ψ in representation R_i of gauge group i:
#   δ(1/g_i²)_ψ = (N_CFT / 16π²) × ε_ψ² × T(R_i) × (anomalous dim correction)
# where T(R_i) is the Dynkin index of the representation.

# Dynkin indices
T_fund_SU3 = 1/2
T_fund_SU2 = 1/2
T_singlet = 0

print("\n\n--- Partial Compositeness Correction to Gauge Couplings ---")

delta_PC = {'U(1)_Y': 0, 'SU(2)_L': 0, 'SU(3)_c': 0}

for ferm_name, fdata in fermion_data.items():
    eps_sq = fdata['eps_sq']
    n_gen = fdata['n_gen']

    # The partial compositeness correction to the gauge coupling is a LOOP effect:
    # δ(1/g_i²) ~ (1/16π²) × ε² × T(R) × ln(Λ/m)
    # Note: this is O(1/16π²), NOT O(N_CFT/16π²) — the N_CFT factor
    # appears in the TOTAL running (already captured by perturbative CFT running),
    # not in the compositeness mixing correction itself.
    # The genuinely NEW gauge-dependent piece from partial compositeness is:
    # δ(1/g_i²)_PC = (1/16π²) × ε² × T(R_i) × O(1)

    # SU(3) contribution
    if fdata['SU3'] == 'fund':
        delta_3 = (1 / (16 * np.pi**2)) * eps_sq * T_fund_SU3 * n_gen
    else:
        delta_3 = 0

    # SU(2) contribution
    if fdata['SU2'] == 'fund':
        delta_2 = (1 / (16 * np.pi**2)) * eps_sq * T_fund_SU2 * n_gen
    else:
        delta_2 = 0

    # U(1) contribution (Y² for each field)
    Y = fdata['Y']
    delta_1 = (1 / (16 * np.pi**2)) * eps_sq * Y**2 * n_gen

    delta_PC['U(1)_Y'] += delta_1
    delta_PC['SU(2)_L'] += delta_2
    delta_PC['SU(3)_c'] += delta_3

print(f"\nPartial compositeness corrections:")
for name in delta_PC:
    print(f"  δ(1/g²)^{{PC}}_{{{name}}} = {delta_PC[name]:.6e}")

# The correction to a₁/a₂:
delta_diff_12_PC = delta_PC['U(1)_Y'] - delta_PC['SU(2)_L']
a1_over_a2_PC = (tree_level + delta_PC['U(1)_Y']) / (tree_level + delta_PC['SU(2)_L'])
print(f"\n  δ₁ - δ₂ (PC) = {delta_diff_12_PC:.6e}")
print(f"  a₁/a₂ (PC) = {a1_over_a2_PC:.8f}")
print(f"  Shift from unity: {a1_over_a2_PC - 1:.2e}")

print("""
The partial compositeness correction is small because:
  (a) Most SM fermions are UV-localized (c > 1/2), giving ε² ~ e^{-(2c-1)kL} ~ 10^{-4} to 10^{-30}
  (b) The correction is a LOOP effect: O(1/16π²) per mixing
  (c) The only sizable contribution comes from the top quark (c_R ~ 0.3, IR-localized)

Note: The gauge-dependent piece from partial compositeness is perturbative
(it's a loop effect involving the composite-elementary mixing). This means
it is already CAPTURED by the standard RG running of gauge couplings between
Λ_IR and Λ_UV. It is NOT a new non-perturbative contribution.

The partial compositeness mechanism cannot explain the 29% gap.
""")


# =============================================================================
# SECTION 8: The Goldberger-Wise Mechanism
# =============================================================================

print("=" * 80)
print("SECTION 8: GOLDBERGER-WISE STABILIZATION BACKREACTION")
print("=" * 80)

print("""
The Goldberger-Wise (GW) mechanism stabilizes the RS₁ modulus using a bulk
scalar Φ with:
  • Mass m_Φ² = Δ(Δ-4)k² (with Δ the conformal dimension, typically Δ ≈ 4-ε)
  • UV brane potential: V_UV(Φ) → Φ|_{y=0} = v_UV
  • IR brane potential: V_IR(Φ) → Φ|_{y=L} = v_IR

In the CFT dual, Φ corresponds to a nearly-marginal deformation:
  L_CFT → L_CFT + λ_GW × O_Δ

The GW VEV profile: Φ(y) = v_UV × e^{(4-Δ)ky} × [1 + ...]

The backreaction on the metric modifies the gauge coupling:
  δ(1/g_i²)_GW = (1/g₅²) × ∫₀^L dy e^{-2ky} × δg_{μν}^{GW}(y)

If the GW scalar is a GAUGE SINGLET (which is the standard assumption):
  δg_{μν}^{GW} is gauge-independent → correction is gauge-universal

HOWEVER, if the GW scalar has gauge quantum numbers (or mixes with
gauge-charged operators through higher-dimensional operators):
  The correction becomes gauge-dependent.
""")

# Case 1: GW scalar is a gauge singlet (standard)
Delta_GW = 4 - 0.1  # Nearly marginal: Δ ≈ 4 - ε with ε small
epsilon_GW = 4 - Delta_GW

v_UV = k  # GW scalar VEV at UV brane (natural scale)
v_IR = Lambda_IR  # GW scalar VEV at IR brane

# The metric backreaction from GW scalar
# δg_{μν}/g_{μν} ~ (v_UV/k)² × (ε/kL)
metric_backreaction = (v_UV/k)**2 * epsilon_GW / kL
print(f"\nGW metric backreaction: δg/g ~ (v/k)² × ε/(kL) = {metric_backreaction:.4f}")
print(f"This is O(ε/kL) ~ {epsilon_GW/kL:.4f} — a small correction to tree level.")

# Case 2: GW scalar mixes with gauge sector
print("""
If the GW scalar mixes with gauge-charged operators through higher-dimensional
operators (dim-6 or higher):

  L_mix = (Φ/M_*)² × F_{i,μν} F_i^{μν}

The correction:
  δ(1/g_i²)_mix = (v_IR/M_*)² × c_i

where c_i depends on the operator structure and IS gauge-dependent.
""")

# Estimate with M_* = k (Planck-scale suppression)
M_star = k
delta_GW_mix = (v_IR / M_star)**2
print(f"GW mixing correction: (v_IR/M_*)² = (Λ_IR/k)² = e^{{-2kL}} = {delta_GW_mix:.2e}")
print(f"This is exponentially suppressed by the warp factor — NEGLIGIBLE.\n")


# =============================================================================
# SECTION 9: The Critical Question — Where Does Gauge Dependence Survive?
# =============================================================================

print("=" * 80)
print("SECTION 9: WHERE DOES GAUGE DEPENDENCE SURVIVE?")
print("=" * 80)

print("""
Summary of all holographic corrections and their gauge dependence:

┌─────────────────────────────┬──────────────────┬──────────────────┐
│ Mechanism                   │ Gauge-dependent? │ Magnitude        │
├─────────────────────────────┼──────────────────┼──────────────────┤
│ 1. Perturbative CFT running │ NO (universal)   │ Large, universal │
│ 2. Radion trace anomaly     │ YES              │ ~ b_i/(8π²) ~ 0.01 │
│ 3. CFT instantons           │ NO (in CFT gauge)│ exp(-S) ~ 10⁻⁶⁸ │
│ 4. SM gauge instantons      │ YES (π₃)         │ exp(-S) ~ 10⁻⁶⁸ │
│ 5. IR brane strong coupling │ YES              │ ~ e^{-2kL} ~ 10⁻³⁰│
│ 6. Partial compositeness    │ YES              │ ~ 10⁻⁶            │
│ 7. GW backreaction          │ NO (singlet)     │ ~ ε/kL ~ 0.003  │
│ 8. GW mixing (dim-6)       │ YES              │ ~ e^{-2kL} ~ 10⁻³⁰│
│ 9. Condensate OPE           │ YES              │ ~ e^{-2kL} ~ 10⁻³⁰│
└─────────────────────────────┴──────────────────┴──────────────────┘

Required: δ(a₁/a₂) = 0.224 (shift from 1 to 0.776)
Best candidate: Radion trace anomaly ~ 0.01

ALL holographic mechanisms are either gauge-universal or exponentially
suppressed by the warp factor.
""")

# The warp factor suppression is the KEY OBSTRUCTION
print("=" * 50)
print("THE WARP FACTOR OBSTRUCTION")
print("=" * 50)
print("""
The RS geometry SIMULTANEOUSLY:
  (a) Generates the gauge hierarchy (Λ_IR/Λ_UV = e^{-kL} ~ 10⁻¹⁵)
  (b) SUPPRESSES any IR brane effect on gauge couplings by e^{-2kL} ~ 10⁻³⁰

This is a STRUCTURAL feature of the warped geometry:
  • The gauge kinetic coefficient a_i = ∫₀^L dy e^{-2ky} × (...)
  • The integrand is DOMINATED by the UV brane (y ~ 0) where e^{-2ky} ~ 1
  • The IR brane (y ~ L) contributes e^{-2kL} ~ 10⁻³⁰ to the integral

In the holographic dual:
  • The tree-level gauge coupling is set at the UV CUTOFF of the CFT
  • The non-perturbative CFT dynamics at the confinement scale Λ_IR
    contributes to the running, but the running is PERTURBATIVE and
    gauge-universal (this is the content of T12)
  • The truly non-perturbative effects (condensates, instantons) are
    localized at the confinement scale and suppressed by (Λ_IR/Λ_UV)^n

This is a THEOREM of the AdS/CFT correspondence: in the large-N limit,
the gauge coupling at the UV cutoff receives corrections suppressed by
powers of Λ_IR/Λ_UV = e^{-kL} ~ 10⁻¹⁵. No non-perturbative effect
at the IR scale can produce an O(1) correction to the UV gauge coupling.
""")


# =============================================================================
# SECTION 10: Parameter Space Scan — What Would Be Needed?
# =============================================================================

print("=" * 80)
print("SECTION 10: PARAMETER SPACE SCAN")
print("=" * 80)

print("""
Despite the warp factor suppression, let's ask: WHAT VALUES of the non-perturbative
parameters would produce a₁/a₂ = 0.776?

We parameterize the correction as:
  δ(1/g_i²)^{NP} = (N_CFT^{2p} / 16π²) × Λ_IR^{2q} / Λ_UV^{2q} × f_i

with:
  f₁ = 0 (U(1), no instantons)
  f₂ = f (SU(2), to be determined)
  f₃ = f₃ (SU(3), different)

The condition a₁/a₂ = 0.776 requires:
  f₂ × (N_CFT^{2p} / 16π²) × e^{-2q×kL} = ε₂ × (tree_level)
""")

# Scan over different power-law assumptions for the warp factor suppression
print(f"\nRequired: ε₂ × tree_level = {epsilon_2_target * tree_level:.4f}")
print(f"N_CFT = {N_CFT:.1f}, kL = {kL}")
print()

# What if the warp factor suppression is NOT e^{-2kL}?
# What if the correction goes as e^{-αkL} for some α?
print("Scanning: What warp factor suppression exponent α gives the right magnitude?")
print("Assumption: f_2 = 1, p = 1 (leading large-N)")
print()
print(f"{'α':>6} | {'e^{-αkL}':>15} | {'N²/(16π²) × e^{-αkL}':>22} | {'ε₂ achieved':>15} | {'Status':>10}")
print("-" * 80)

for alpha in [0, 0.01, 0.1, 0.5, 1.0, 1.5, 2.0]:
    suppression = np.exp(-alpha * kL)
    correction = N_CFT_squared / (16 * np.pi**2) * suppression
    eps_achieved = correction / tree_level
    status = "TARGET" if abs(eps_achieved - epsilon_2_target) / epsilon_2_target < 0.1 else \
             ("TOO BIG" if eps_achieved > epsilon_2_target else "TOO SMALL")
    print(f"{alpha:6.2f} | {suppression:15.2e} | {correction:22.4e} | {eps_achieved:15.4e} | {status:>10}")

# Find the exact α that gives the target
# ε₂ = N²/(16π²) × e^{-αkL} / tree_level
# e^{-αkL} = ε₂ × tree_level × 16π² / N²
required_exp = epsilon_2_target * tree_level * 16 * np.pi**2 / N_CFT_squared
alpha_required = -np.log(required_exp) / kL

print(f"\n*** Required warp suppression exponent: α = {alpha_required:.4f} ***")
print(f"    (Corresponding to e^{{-{alpha_required:.4f}×{kL:.0f}}} = e^{{-{alpha_required*kL:.1f}}} = {required_exp:.2e})")

print("""
For the standard RS₁ geometry:
  • Gauge kinetic integral: α = 2 (the e^{-2ky} measure)
  • This gives suppression ~ 10⁻³⁰ — far too small

For α ≈ 0: NO warp suppression → the correction is O(N²/16π²) ~ 270
  This is TOO LARGE by a factor of ~1000.

The "sweet spot" is α ~ 0.2, which requires a correction that falls off
much more slowly than the metric measure. No standard mechanism produces this.
""")

# Alternative: What if the correction is NOT exponentially suppressed?
# What if it's a POWER-LAW correction from the CFT?
print("\n--- Alternative: Power-Law Correction (No Warp Suppression) ---")
print("""
If the correction is purely a large-N effect without warp suppression:
  δ(1/g_i²) = c_i / (16π²)

Then c₂ must satisfy:
  c₂ / (16π²) = ε₂ × tree_level = ε₂ / g²_GUT
""")

c2_required = epsilon_2_target * 16 * np.pi**2 * tree_level
print(f"Required c₂ = ε₂ × 16π² / g²_GUT = {c2_required:.2f}")
print(f"This is an O(1) coefficient — naturally achievable in large-N gauge theory!")

# But then we need to explain why U(1) doesn't get this correction
# The answer: π₃(U(1)) = 0 → no non-perturbative sector

print(f"""
If the non-perturbative correction is:
  δ(1/g_i²)^{{NP}} = c_i / (16π²)

with c₁ = 0 (no U(1) instantons), c₂ = {c2_required:.2f}, then:

  a₁/a₂ = tree / (tree + c₂/16π²)
         = {tree_level:.4f} / ({tree_level:.4f} + {c2_required/(16*np.pi**2):.4f})
         = {tree_level / (tree_level + c2_required/(16*np.pi**2)):.4f}

Target: 0.776

BUT: Where does this correction COME FROM without warp suppression?
In the holographic picture, any correction from the IR dynamics is
necessarily suppressed by the warp factor. A correction without warp
suppression would have to come from the UV brane or the full bulk —
but T12 proves those are gauge-universal.
""")


# =============================================================================
# SECTION 11: The Catch-22 and Resolution Attempts
# =============================================================================

print("=" * 80)
print("SECTION 11: THE CATCH-22")
print("=" * 80)

print("""
THE FUNDAMENTAL CATCH-22 OF RS₁ GAUGE COUPLING CORRECTIONS:

1. Gauge-dependent non-perturbative effects require STRONG COUPLING
   → This is localized at the IR brane (y ~ L)

2. But any effect at the IR brane is SUPPRESSED by e^{-2kL} in the
   gauge kinetic coefficient (because the integral ∫ dy e^{-2ky} is
   UV-dominated)

3. The warp factor that creates the hierarchy (and strong coupling at IR)
   SIMULTANEOUSLY suppresses the IR contribution to gauge couplings

4. T12 ensures that the UV/bulk contributions are gauge-universal

Therefore: Gauge-dependent corrections exist but are exponentially small.
The 29% gap CANNOT be produced by the holographic mechanism within the
standard RS₁ framework.

This is a NO-GO result for the AdS/CFT approach to the 12% problem.
""")

# However, let's examine escape routes
print("\n--- Possible Escape Routes ---\n")

# Escape 1: Modified measure
print("Escape 1: Modified Warping/Measure")
print("=" * 40)
print("""
If the bulk geometry is not exactly AdS₅ (e.g., departures from RS
due to GW backreaction, bulk cosmological constant running, or
higher-derivative gravity), the measure in the gauge kinetic integral
could change:

  a_i = ∫₀^L dy e^{-σ(y)} × [1 + δ_i(y)]

with σ(y) ≠ 2ky. If σ(y) is SMALLER than 2ky near y = L, the IR
contribution is less suppressed.
""")

# What σ(L) is needed?
# We need: e^{-σ(L)} × δ₂ × L ≈ ε₂ × tree
# With δ₂ ~ O(1) and tree ≈ 1/(2k):
# e^{-σ(L)} / (2k²L) ≈ ε₂ / (2k) → e^{-σ(L)} ≈ ε₂ / (kL) ≈ 0.008

sigma_L_required = -np.log(epsilon_2_target / kL)
print(f"Required σ(L) = -ln(ε₂/kL) = {sigma_L_required:.2f}")
print(f"Compare to standard RS: σ(L) = 2kL = {2*kL:.0f}")
print(f"Need σ(L) to be {sigma_L_required:.0f}, but RS gives {2*kL:.0f}.")
print(f"This requires DRAMATIC departure from AdS geometry — not consistent")
print(f"with the RS model solving the hierarchy problem.\n")

# Escape 2: Brane-localized kinetic terms
print("Escape 2: Brane-Localized Kinetic Terms (BLKTs)")
print("=" * 40)
print("""
If gauge kinetic terms are localized on the IR brane (not just in the bulk):

  a_i = a_i^{bulk} + a_i^{brane}

where:
  a_i^{bulk} = (1/g₅²) ∫₀^L dy e^{-2ky}  [gauge-universal, by T1/T12]
  a_i^{brane} = r_i / g₅²                   [potentially gauge-dependent]

The brane kinetic terms r_i can be different for different gauge groups
if the IR brane has non-trivial dynamics.
""")

# What brane kinetic term r₂ is needed?
# a₁/a₂ = a^{bulk} / (a^{bulk} + r₂/g₅²)
# = 1 / (1 + r₂ × g₅² / a^{bulk})
# = 1 / (1 + r₂ × 2k / (1 - e^{-2kL}))
# ≈ 1 / (1 + 2kr₂)

# For a₁/a₂ = 0.776:
# 2kr₂ = 1/0.776 - 1 = 0.289
r2_required = epsilon_2_target / (2*k)

print(f"Required: r₂ = ε₂/(2k) = {r2_required:.2e} GeV⁻¹")
print(f"In natural units: r₂ × k = ε₂/2 = {epsilon_2_target/2:.4f}")
print(f"Dimensionless: 2kr₂ = ε₂ = {epsilon_2_target:.4f}")
print(f"\nThis is an O(0.1) brane kinetic term — perfectly natural!")

print("""
CRITICAL FINDING: Brane-localized gauge kinetic terms (BLKTs) on the IR brane
can produce gauge-dependent corrections of the EXACT right magnitude without
warp factor suppression.

The physics: BLKTs are NOT part of the bulk spectral action — they are
BOUNDARY contributions. T1 and T12 govern the BULK part only. The brane
action is a separate term in the total action.

In the holographic dual: BLKTs correspond to the UV-finite part of the
CFT current correlator at the confinement scale. These ARE non-perturbative
(they arise from the CFT dynamics) and ARE gauge-dependent (different
current correlators for different gauge groups).
""")

# Let's compute what BLKTs give
print("\n--- BLKT Analysis ---")

# The BLKT contribution in the holographic picture
# The current-current correlator at p² = 0 in the confined phase:
# Π_i(0) = r_i / g₅²
# where r_i is the BLKT parameter.

# In the large-N CFT, the current correlator at zero momentum:
# Π_i(0) = (N_CFT² / 16π²) × C_i × (1/Λ_IR²) × ⟨O⟩

# The finite part (not captured by the logarithmic running):
# r_i = (N_CFT² / 16π²) × C_i × δ_i^{NP}

# For gauge group i, the non-perturbative coefficient δ_i^{NP} depends on:
# 1. Whether the group has instantons (topological)
# 2. The representation content of the CFT composites
# 3. The dynamics at the confinement transition

# The BLKT in the RS model appears as a counterterm for the gauge field
# on the IR brane. Its natural size is:
# r_i ~ 1/(16π²) × ln(Λ_brane / m_KK) ~ 1/(16π²) × O(1)

# For SU(2): non-perturbative contribution from instanton effects
# For U(1): no instanton contribution → r₁ = 0 (or gauge-universal)

print("Brane-Localized Kinetic Terms: Natural magnitudes")
print(f"  r_i ~ 1/(16π²) × O(1) = {1/(16*np.pi**2):.4f} × O(1)")
print(f"  Required for 12%: 2kr₂ = {epsilon_2_target:.4f}")
print(f"  This requires: r₂ × 2k ~ 0.29")
print(f"  In the BLKT framework: 2k × [δ₂/(16π²)] = 0.29")
print(f"  So δ₂ = 0.29 × 16π² / (2 × 1) = {0.29 * 16 * np.pi**2 / 2:.1f}")
print(f"  (where we used dimensionless units with k = 1)")
print(f"\n  δ₂ ~ {0.29 * 16 * np.pi**2 / 2:.0f} — this is large but not absurd")
print(f"  in a strongly-coupled CFT with N_CFT ~ {N_CFT:.0f}")

# Connection to the ln(3)/√2 formula
print("\n\n--- Connection to ln(3)/√2 ---")
print("""
If the BLKT arises from the instanton sector of the CFT, the SU(2) BLKT:

  r₂ = (1/16π²) × C₂(adj, SU(2)) × N_c^{eff} × (some function of kL)

The ln(3)/√2 formula predicts:
  a₁/a₂ = ln(N_c)/√(N_w) = 0.7768

This corresponds to:
  ε₂ = √(N_w)/ln(N_c) - 1 = √2/ln(3) - 1 = 0.2875

In the BLKT language:
  2kr₂ = 0.2875

The coefficient structure of the instanton contribution:
  r₂ ∝ √(C₂(adj, SU(2))) × ln(N_c)
     = √2 × ln(3)

This has the right functional form for an instanton calculation:
  • √(C₂) from the collective coordinate Jacobian (adjoint zero modes)
  • ln(N_c) from the fermion determinant with N_c colors

The question is whether this specific combination arises from the IR brane
instanton calculus. This requires a full non-perturbative computation.
""")


# =============================================================================
# SECTION 12: Comprehensive Numerical Results
# =============================================================================

print("=" * 80)
print("SECTION 12: COMPREHENSIVE NUMERICAL RESULTS")
print("=" * 80)

# Collect ALL corrections
print("\n--- All Gauge-Dependent Corrections to a₁/a₂ ---\n")

corrections = {
    'Perturbative CFT running': {'delta_a1_a2': 0.0, 'gauge_dep': False, 'confidence': 'HIGH'},
    'Radion trace anomaly': {
        'delta_a1_a2': (delta_radion['U(1)_Y'] - delta_radion['SU(2)_L']) / tree_level,
        'gauge_dep': True, 'confidence': 'HIGH'
    },
    'SM gauge instantons (UV)': {'delta_a1_a2': 0.0, 'gauge_dep': True, 'confidence': 'HIGH',
                                  'note': 'exp(-157) ~ 10^{-68}'},
    'CFT instantons': {'delta_a1_a2': 0.0, 'gauge_dep': False, 'confidence': 'HIGH'},
    'IR brane strong coupling': {
        'delta_a1_a2': -2 * np.exp(-2*kL),  # O(e^{-2kL}) gauge-dependent part
        'gauge_dep': True, 'confidence': 'HIGH'
    },
    'Partial compositeness': {
        'delta_a1_a2': (delta_PC['U(1)_Y'] - delta_PC['SU(2)_L']) / tree_level,
        'gauge_dep': True, 'confidence': 'MEDIUM'
    },
    'GW stabilization': {'delta_a1_a2': 0.0, 'gauge_dep': False, 'confidence': 'HIGH'},
    'BLKTs (if present)': {
        'delta_a1_a2': 'FREE PARAMETER',
        'gauge_dep': True, 'confidence': 'LOW',
        'note': 'Not determined by bulk RS₁ alone'
    },
}

print(f"{'Mechanism':>30} | {'δ(a₁/a₂)':>15} | {'Gauge-dep?':>10} | {'Confidence':>10}")
print("-" * 75)
for name, data in corrections.items():
    delta = data['delta_a1_a2']
    if isinstance(delta, str):
        delta_str = delta
    elif abs(delta) < 1e-100:
        delta_str = "≈ 0"
    else:
        delta_str = f"{delta:.2e}"
    gd = "YES" if data['gauge_dep'] else "NO"
    print(f"{name:>30} | {delta_str:>15} | {gd:>10} | {data['confidence']:>10}")

print(f"\nRequired: δ(a₁/a₂) = {a1_over_a2_target - 1:.4f}")

# Total from computable mechanisms
total_computable = sum(v['delta_a1_a2'] for v in corrections.values()
                       if isinstance(v['delta_a1_a2'], (int, float)))
print(f"Total from computable mechanisms: {total_computable:.2e}")
print(f"Shortfall: {(a1_over_a2_target - 1) - total_computable:.4f} ({abs(((a1_over_a2_target-1) - total_computable)/(a1_over_a2_target-1))*100:.1f}% of target)")


# =============================================================================
# SECTION 13: The BLKT Route — Detailed Analysis
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 13: BRANE-LOCALIZED KINETIC TERMS — THE SURVIVING ROUTE")
print("=" * 80)

print("""
The ONLY mechanism that can produce O(0.1) gauge-dependent corrections
without warp factor suppression is brane-localized kinetic terms (BLKTs).

BLKTs arise naturally in:
  1. Orbifold field theory (as counterterms for brane-localized divergences)
  2. String theory (from brane dynamics, open string loops)
  3. The holographic dual (as the finite part of the CFT correlator)

In the standard RS₁ model, BLKTs are FREE PARAMETERS — they are not
determined by the bulk geometry. They must be set by UV completion
(string theory, NCG axioms, or experimental data).

The question: Does the NCG spectral action DETERMINE the BLKTs?
""")

# The NCG spectral action perspective
print("--- NCG Spectral Action and BLKTs ---\n")
print("""
The NCG spectral action Tr[f(D²/Λ²)] on the RS₁ orbifold includes:
  • Bulk contribution: ∫₀^L dy e^{-4ky} √g × L_{bulk}(y)
  • Boundary contributions: Σ_{branes} √g_brane × L_{brane}

The boundary terms in the spectral action ARE the BLKTs!
They arise from the Seeley-DeWitt boundary coefficients:

  a_n^{bdy} = boundary heat kernel coefficients

These include gauge kinetic terms localized on the branes:
  L_{brane} ⊃ a₂^{bdy,i} × F_i² |_{brane}

The coefficient a₂^{bdy,i} depends on the BOUNDARY CONDITIONS of the
Dirac operator, which ARE gauge-dependent (different representations
have different boundary conditions on the orbifold).

THIS IS THE KEY INSIGHT:
  • T1 proves bulk gauge kinetic terms are universal
  • T12 proves this to all perturbative orders
  • NEITHER addresses boundary terms explicitly
  • Boundary terms ARE computed by the spectral action
  • They CAN be gauge-dependent through boundary conditions
""")

# Compute the boundary heat kernel contribution
# For the RS₁ orbifold, the boundary conditions are:
# Gauge bosons: Neumann (++ BC) on even, Dirichlet (+-) on odd
# The boundary heat kernel coefficient a₂^{bdy} for gauge fields:

# The Seeley-DeWitt boundary term for a vector field with Neumann BC:
# a₂^{bdy} = (1/6) × ∫_{brane} Tr[E|_{brane}] + (1/3) × ∫ Tr[K_{ab}F^{ab}]
# where E is the endomorphism and K is the extrinsic curvature.

# On the RS branes:
# K_{ab} = ∓k g_{ab} (extrinsic curvature of the UV/IR brane)
# E|_{brane} depends on the field content and representations

# For the gauge field A_μ^a:
# E = -F_{μν}^a × T^a (in the adjoint representation)
# Tr[E] = -C₂(adj) × F²

# The boundary coefficient:
# a₂^{bdy,i} = (C₂(adj,i)/6) × Area(brane) + curvature terms

print("Boundary heat kernel coefficients:")
for name, data in gauge_groups.items():
    C2 = data['C2_adj']
    dim_adj = data['dim_adj']
    a2_bdy = C2 / 6
    print(f"  {name}: a₂^{{bdy}} = C₂(adj)/6 = {C2}/{6} = {a2_bdy:.4f}")
    print(f"    × dim(adj) = {dim_adj} → total = {a2_bdy * dim_adj:.4f}")

# The boundary contribution to the gauge kinetic coefficient:
# δa_i^{bdy} = f₁ × a₂^{bdy,i} / (4π²)
# where f₁ is the first moment of the test function f.

# This IS gauge-dependent: different C₂(adj) for different groups!
# But the magnitude...

f1 = 1.0  # Normalized first moment of f
for name, data in gauge_groups.items():
    C2 = data['C2_adj']
    dim_adj = data['dim_adj']
    delta_bdy = f1 * (C2 / 6) / (4 * np.pi**2)
    print(f"\n  δa^{{bdy}}_{{{name}}} / a_tree = {delta_bdy:.6f} / {tree_level:.4f} = {delta_bdy/tree_level:.6f}")

# The ratio correction
delta_bdy_U1 = f1 * (0 / 6) / (4 * np.pi**2)
delta_bdy_SU2 = f1 * (2 / 6) / (4 * np.pi**2)
delta_bdy_SU3 = f1 * (3 / 6) / (4 * np.pi**2)

a1_a2_bdy = (tree_level + delta_bdy_U1) / (tree_level + delta_bdy_SU2)
print(f"\n  Boundary contribution to a₁/a₂:")
print(f"  = (tree + δ^bdy_U1) / (tree + δ^bdy_SU2)")
print(f"  = ({tree_level:.4f} + {delta_bdy_U1:.6f}) / ({tree_level:.4f} + {delta_bdy_SU2:.6f})")
print(f"  = {a1_a2_bdy:.6f}")
print(f"  Shift: {a1_a2_bdy - 1:.6f}")

print("""
The boundary heat kernel contribution is gauge-dependent (through C₂(adj))
but SMALL: δ(a₁/a₂) ~ C₂/(24π² × tree) ~ 0.001.

This is the PERTURBATIVE boundary contribution. The key question is whether
the NON-PERTURBATIVE boundary contribution can be much larger.
""")

# What enhancement factor is needed?
enhancement_needed = (a1_over_a2_target - 1) / (a1_a2_bdy - 1)
print(f"Enhancement factor needed: {enhancement_needed:.0f}×")
print(f"This requires non-perturbative enhancement by ~ {enhancement_needed:.0f}× over")
print(f"the perturbative boundary term.")

print("""
In the holographic dual, this enhancement corresponds to the CFT being
strongly coupled: the current-current correlator receives O(N²) enhancement
from the dense spectrum of composite resonances.

The question is whether this O(N²) enhancement survives after the
conformal symmetry breaking (which it does, as a finite constant term
in the correlator — this IS the BLKT).
""")


# =============================================================================
# SECTION 14: The Holographic BLKT Computation
# =============================================================================

print("=" * 80)
print("SECTION 14: HOLOGRAPHIC BLKT — THE NON-PERTURBATIVE BOUNDARY TERM")
print("=" * 80)

print("""
In the holographic picture, the BLKT arises from the FINITE part of the
CFT current-current correlator after conformal symmetry breaking:

  Π_i(p² = 0) = (b_i^{CFT}/16π²) × ln(Λ_UV²/Λ_IR²) + r_i

The logarithmic part is the perturbative running (gauge-universal by T12).
The finite part r_i is the BLKT, and it IS non-perturbative.

In a strongly-coupled large-N theory, r_i can be estimated from the
Weinberg sum rules. The first and second sum rules:

  (WSR1): Σ_n F_{V,n}² - F_{A,n}² = f_π²
  (WSR2): Σ_n F_{V,n}² m_{V,n}² - F_{A,n}² m_{A,n}² = 0

These sum rules constrain the BLKT through:
  r_i = (1/2) × Σ_n (F_{V,n,i}² / m_{V,n}²)  (from spectral representation)
""")

# Estimate r_i from the KK spectrum
# In the RS model, the vector KK modes have:
#   m_n = x_n × Λ_IR  (x_n are Bessel zeros, x_1 ≈ 2.45)
#   F_n² = 2Λ_IR² / (kL × x_n²) × [1 + O(1/kL)]

# The sum:
#   r_i = (1/2) × Σ_n F_n² / m_n²
#       = (1/2) × Σ_n [2Λ_IR²/(kL × x_n²)] / [x_n² × Λ_IR²]
#       = (1/kL) × Σ_n 1/x_n⁴

# The Bessel zero sum:
bessel_zeros = [special.jn_zeros(1, 200)]  # First 200 zeros of J₁
x_n = bessel_zeros[0]
bessel_sum = np.sum(1/x_n**4)
print(f"Bessel zero sum: Σ 1/x_n⁴ = {bessel_sum:.6f}")

r_universal = bessel_sum / kL
print(f"Universal BLKT: r = Σ(1/x_n⁴)/kL = {r_universal:.6f}")
print(f"This is the GAUGE-UNIVERSAL part of the BLKT (same for all groups).")

# The gauge-DEPENDENT part of the BLKT comes from:
# 1. Different boundary conditions for different gauge groups
# 2. Gauge-dependent loop corrections to KK masses and decay constants
# 3. Non-perturbative effects (instantons in the brane theory)

# For a weakly-gauged global symmetry of the CFT:
# The current two-point function gets a contribution from the CFT dynamics:
#
# Π_i^{CFT}(p²) = (N_CFT²/16π²) × [b_i^{CFT} ln(p²/Λ_IR²) + c_i^{NP}]
#
# where c_i^{NP} is the finite, non-perturbative piece.
#
# In the large-N limit of a VECTOR-LIKE theory:
# c_i^{NP} = α_i × C₂(adj,i) + β × (gauge-universal part)
#
# The coefficient α_i is an O(1/N_CFT²) quantity in the large-N expansion.
# The LEADING large-N contribution (O(N_CFT²)) is gauge-universal.
# The SUBLEADING contribution (O(1)) is gauge-dependent.

print("\n--- Large-N Expansion of the Non-Perturbative BLKT ---")
print("""
The BLKT in the 1/N expansion:

  r_i = r_0 + (1/N_CFT²) × δr_i + O(1/N_CFT⁴)

where:
  r_0 = O(N_CFT² / 16π²) × (universal)  [LARGE but gauge-independent]
  δr_i = O(1/16π²) × (gauge-dependent)   [SMALL and gauge-dependent]

The correction to a₁/a₂:
  a₁/a₂ = (tree + r_0 + δr₁/N²) / (tree + r_0 + δr₂/N²)
         ≈ 1 + (δr₁ - δr₂) / (N² × (tree + r_0))
         ~ 1 + O(1/N²)

For N_CFT² ~ 42,875 (kL³):
  The gauge-dependent correction is O(1/N²) ~ 2×10⁻⁵

THIS IS FAR TOO SMALL.
""")

delta_from_subleading = 1 / N_CFT_squared
print(f"Subleading (1/N²) correction: ~ {delta_from_subleading:.2e}")
print(f"Required: ~ {abs(a1_over_a2_target - 1):.4f}")
print(f"Shortfall: ~ {abs(a1_over_a2_target - 1)/delta_from_subleading:.0f}×")

# But wait — what if the theory is not in the large-N regime?
# N_CFT ~ 207 from (kL)^{3/2}. Is this really "large"?
# 1/N_CFT² ~ 10⁻⁵. The 1/N correction is:
# δr/N² ~ 1/N² × (16π² × tree) ~ 1/42875 × 314 ~ 0.007
# This is still too small by a factor of ~30.

# Alternative N estimate
print("\n--- Sensitivity to N_CFT Estimate ---")
print(f"{'N_CFT²':>10} | {'1/N²':>10} | {'δ(a₁/a₂)':>12} | {'Status':>10}")
print("-" * 50)

for N2 in [N_CFT_squared, N_CFT_sq_alt1, N_CFT_sq_alt2, 100, 10, 1]:
    delta_12 = 16 * np.pi**2 * tree_level / N2  # crude estimate of 1/N² correction
    status = "OK" if abs(delta_12 + (a1_over_a2_target - 1)) / abs(a1_over_a2_target - 1) < 0.5 else "TOO SMALL"
    if delta_12 > 1:
        status = "TOO BIG (perturbative breakdown)"
    print(f"{N2:10.1f} | {1/N2:10.2e} | {-delta_12:12.4f} | {status:>10}")

print("""
For the 1/N_CFT² correction to produce the 29% gap, we need:
  N_CFT² ~ O(16π² × tree/ε₂) ~ O(1000)

This corresponds to kL ~ 10 (from N² ~ (kL)³).

But kL = 10 gives Λ_IR = ke^{-10} ~ 10^{17} × 10^{-4} ~ 10^{13} GeV.
This does NOT solve the hierarchy problem (Λ_IR >> TeV).

The RS₁ model with kL ~ 35 (hierarchy solution) gives N_CFT too large
for 1/N corrections to matter. A model with N_CFT small enough for
corrections to matter doesn't solve the hierarchy.
""")


# =============================================================================
# SECTION 15: Final Summary — The Three Regimes
# =============================================================================

print("=" * 80)
print("SECTION 15: FINAL SUMMARY — THE THREE REGIMES")
print("=" * 80)

print("""
The holographic analysis reveals THREE distinct regimes:

═══════════════════════════════════════════════════════════════════
REGIME 1: Standard RS₁ (kL = 35)
═══════════════════════════════════════════════════════════════════
  • Solves hierarchy: ✓ (Λ_IR ~ TeV)
  • N_CFT ~ 207 (large-N well-controlled)
  • Warp suppression of IR effects: e^{-70} ~ 10⁻³⁰
  • 1/N² corrections: O(10⁻⁵)
  • Achievable δ(a₁/a₂): ~ 10⁻⁵ (from 1/N) or 10⁻³⁰ (from warp)
  → CANNOT produce 29% correction
  → The model that solves the hierarchy cannot explain the gap

═══════════════════════════════════════════════════════════════════
REGIME 2: Small-kL RS₁ (kL ~ 10)
═══════════════════════════════════════════════════════════════════
  • Solves hierarchy: ✗ (Λ_IR ~ 10¹³ GeV)
  • N_CFT ~ 32 (1/N² ~ 10⁻³)
  • 1/N² corrections large enough: ~ 0.1-0.3
  → COULD produce 29% correction
  → But doesn't solve hierarchy — needs additional mechanism

═══════════════════════════════════════════════════════════════════
REGIME 3: Dual-brane / Multiple Warping
═══════════════════════════════════════════════════════════════════
  If the RS₁ model is embedded in a more complex geometry (multiple
  throats, cascading gauge theory dual, or similar), the effective
  N_CFT can be different from (kL)^{3/2}, and the warp factor
  suppression can be modified. This is the F-theory/string embedding
  route (Track 21A.3).
""")

# Compute the kL that gives the right N_CFT for 29% correction
# We need: (16π² × tree) / N_CFT² ~ ε₂
# N_CFT² ~ (16π² × tree) / ε₂
N2_required = 16 * np.pi**2 * tree_level / epsilon_2_target
print(f"\n--- Critical N_CFT² for 29% correction ---")
print(f"N_CFT² required = 16π² × tree / ε₂ = {N2_required:.0f}")
print(f"If N² = (kL)³: kL = N^{{2/3}} = {N2_required**(1/3):.1f}")
print(f"Corresponding Λ_IR = k × e^{{-{N2_required**(1/3):.1f}}} = {k * np.exp(-N2_required**(1/3)):.2e} GeV")
print(f"This is way above the TeV scale — not a hierarchy solution.\n")

# Alternative: what if N² = 16π²kL (the other estimate)?
kL_required_alt = N2_required / (16 * np.pi**2)
print(f"If N² = 16π²kL: kL = N²/(16π²) = {kL_required_alt:.1f}")
print(f"Corresponding Λ_IR = k × e^{{-{kL_required_alt:.0f}}} = {k * np.exp(-kL_required_alt):.2e} GeV")


# =============================================================================
# SECTION 16: Verdict and Classification
# =============================================================================

print("\n" + "=" * 80)
print("SECTION 16: VERDICT")
print("=" * 80)

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  DOOR 2b (AdS/CFT Holographic Route): CLOSED                        ║
║                                                                      ║
║  The RS₁/CFT duality provides a complete non-perturbative            ║
║  framework for computing gauge coupling corrections. The result:     ║
║                                                                      ║
║  • ALL perturbative CFT corrections are gauge-universal (T12 dual)   ║
║  • Non-perturbative condensates are warp-suppressed: O(e^{-2kL})     ║
║  • Partial compositeness corrections: O(10⁻⁶)                       ║
║  • SM gauge instantons in CFT background: O(10⁻⁶⁸)                  ║
║  • CFT instanton sector: gauge-universal                             ║
║  • BLKTs: gauge-dependent but O(1/N²) ~ O(10⁻⁵)                    ║
║  • Radion trace anomaly: O(10⁻²) — largest but still 30× too small  ║
║                                                                      ║
║  STRUCTURAL REASON:                                                  ║
║  The warp factor that solves the hierarchy problem simultaneously     ║
║  suppresses any IR brane effect on gauge couplings. And the large-N  ║
║  limit that makes the holographic computation reliable simultaneously ║
║  suppresses gauge-dependent 1/N² corrections. This is a DOUBLE       ║
║  CATCH-22 that closes the holographic route within standard RS₁.     ║
║                                                                      ║
║  THE SURVIVING QUESTION:                                             ║
║  Does the NCG spectral action compute boundary terms that differ     ║
║  from the large-N holographic prediction? The spectral action        ║
║  includes boundary Seeley-DeWitt coefficients that are NOT           ║
║  controlled by the large-N expansion. If these boundary terms        ║
║  are O(1) (not O(1/N²)), the 12% gap could emerge from the          ║
║  BOUNDARY spectral action — outside the scope of both T12            ║
║  (which governs bulk terms) and the holographic prediction           ║
║  (which assumes large-N).                                            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
""")

# Classification update
print("--- Door 2 Classification Update ---\n")
doors = [
    ("2a", "Heat kernel Borel ambiguity", "CLOSED", "Gauge-universal singularity structure (Comp A)"),
    ("2b", "AdS/CFT holographic corrections", "CLOSED", "Double catch-22: warp suppression + large-N (this computation)"),
    ("2c", "One-loop alpha shift", "CLOSED", "δ ~ 0.5%, need 29%"),
    ("2d", "IR brane strong coupling (direct)", "CONSTRAINED", "Exists but warp-suppressed to O(10⁻³⁰)"),
    ("2e", "Exact spectral action (Comp B)", "OPEN", "Boundary terms not governed by T12 or large-N"),
    ("2f", "Boundary Seeley-DeWitt terms", "OPEN (NEW)", "Gauge-dependent, outside T12 scope"),
]

print(f"{'Door':>5} | {'Mechanism':>40} | {'Status':>12} | Evidence")
print("-" * 120)
for door, mech, status, evidence in doors:
    print(f"{door:>5} | {mech:>40} | {status:>12} | {evidence}")

print("""
\n--- Key Discovery: Boundary Spectral Action (Door 2f) ---

The holographic analysis has SHARPENED the problem. The 12% gap cannot come
from the bulk spectral action (T12), the IR brane dynamics (warp suppression),
or the large-N CFT corrections (1/N² suppression).

The ONLY remaining route within the spectral action framework is the BOUNDARY
spectral action — the Seeley-DeWitt boundary coefficients on the UV and IR branes.
These are:
  1. Gauge-dependent (through boundary conditions → C₂(adj))
  2. NOT governed by T12 (which is a BULK theorem)
  3. NOT described by the large-N holographic dual (boundary terms are UV-sensitive)
  4. Potentially O(1) in the spectral action (no warp suppression if on UV brane)

The UV brane boundary term has NO warp suppression (it's at y = 0 where e^{-2ky} = 1).
If the boundary Seeley-DeWitt coefficients contain a gauge-dependent piece of order:

  a₂^{bdy,UV,i} ~ f₁ × C₂(adj,i) / (some normalization)

this could produce the 29% correction without any exponential suppression.

THIS NEEDS TO BE COMPUTED. It is Computation C: the boundary spectral action
on RS₁ with the full NCG algebra A_F, including the specific representation
content of the Standard Model.
""")

# Confidence assessment
print("\n--- Confidence Assessment ---\n")
claims = [
    ("Perturbative CFT running is gauge-universal", "HIGH", "Follows from T12 via AdS/CFT"),
    ("Non-perturbative condensates are warp-suppressed", "HIGH", "Standard AdS/CFT result"),
    ("BLKTs are O(1/N²) in gauge-dependent part", "MEDIUM-HIGH", "Large-N expansion; exact coefficients unknown"),
    ("Radion coupling is too small (O(0.01))", "HIGH", "Direct calculation of β_i/(8π²)"),
    ("Standard RS₁ cannot produce 29% gap", "HIGH", "Multiple independent mechanisms all fail"),
    ("Boundary spectral action is gauge-dependent", "HIGH", "Boundary conditions involve C₂(adj)"),
    ("Boundary terms can be O(1) (no warp suppression)", "MEDIUM", "True for UV brane; IR brane still suppressed"),
    ("ln(3)/√2 arises from boundary spectral action", "LOW", "Suggestive but no derivation"),
]

print(f"{'Claim':>55} | {'Confidence':>12} | {'Basis'}")
print("-" * 120)
for claim, conf, basis in claims:
    print(f"{claim:>55} | {conf:>12} | {basis}")

print("\n" + "=" * 80)
print("COMPUTATION COMPLETE")
print("=" * 80)
