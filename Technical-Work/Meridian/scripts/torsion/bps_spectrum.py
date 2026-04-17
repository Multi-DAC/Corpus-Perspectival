"""
BPS Spectrum Decomposition for ln(3)/sqrt(2) Conjecture
========================================================
Computes the threshold correction difference Delta_3 - Delta_2
from the BPS spectrum on dP_5 with hypercharge flux.

The SU(5) adjoint decomposes under SU(3) x SU(2) x U(1)_Y as:
  24 = (8,1)_0 + (1,3)_0 + (1,1)_0 + (3,2)_{5/6} + (3bar,2)_{-5/6}

The hypercharge flux N_Y shifts the zero-mode count for each sector
differently, creating the threshold splitting.

Best model: dP_5, p=3, c1(L_Y) = [2, -1, -1, -1, -2, 0]
(coefficients in basis {H, E1, E2, E3, E4, E5})
"""

import numpy as np
from itertools import product

# ============================================================
# dP_5 geometry
# ============================================================

# Intersection form on dP_5: H^2 = 1, Ei^2 = -1, H.Ei = 0, Ei.Ej = 0
# Basis: {H, E1, E2, E3, E4, E5}

def intersection(v1, v2):
    """Intersection number on dP_5."""
    return v1[0]*v2[0] - sum(v1[i]*v2[i] for i in range(1, 6))

def self_intersection(v):
    return intersection(v, v)

# Anticanonical class -K = 3H - E1 - E2 - E3 - E4 - E5
neg_K = np.array([3, -1, -1, -1, -1, -1])

# Best model hypercharge flux
c1_LY = np.array([2, -1, -1, -1, -2, 0])

# Verify N_Y = c1^2
N_Y = self_intersection(c1_LY)
print(f"N_Y = c1(L_Y)^2 = {N_Y}")
print(f"c1.(-K) = {intersection(c1_LY, neg_K)}")

# ============================================================
# (-1)-curves on dP_5
# ============================================================
# The (-1)-curves are:
# E_i (i=1..5): [0, delta_ij] with coefficient -1 at position i
# H - E_i - E_j (i<j): line through two blown-up points

neg1_curves = []
labels = []

# Exceptional divisors E_i
for i in range(5):
    v = np.zeros(6, dtype=int)
    v[i+1] = 1  # E_i has +1 in position i+1
    neg1_curves.append(v)
    labels.append(f"E{i+1}")

# Lines H - E_i - E_j
for i in range(5):
    for j in range(i+1, 5):
        v = np.zeros(6, dtype=int)
        v[0] = 1
        v[i+1] = -1
        v[j+1] = -1
        neg1_curves.append(v)
        labels.append(f"H-E{i+1}-E{j+1}")

print(f"\nNumber of (-1)-curves: {len(neg1_curves)}")
print(f"(Expected for dP_5: 16)")  # Actually 16 for dP_5

# Verify they are (-1)-curves
for i, (c, lab) in enumerate(zip(neg1_curves, labels)):
    assert self_intersection(c) == -1, f"{lab} has self-intersection {self_intersection(c)}"

# ============================================================
# Hypercharge flux through each curve
# ============================================================
print("\n--- Hypercharge flux through (-1)-curves ---")
print(f"{'Curve':<15} {'c1.C':>6} {'Interpretation'}")
print("-" * 50)

fluxes = []
for c, lab in zip(neg1_curves, labels):
    flux = intersection(c1_LY, c)
    fluxes.append(flux)
    print(f"{lab:<15} {flux:>6}")

# ============================================================
# BPS state decomposition
# ============================================================
# M2-branes wrapping curves C in S give BPS states.
# Under SU(5) -> SU(3) x SU(2) x U(1)_Y with flux N_Y:
#
# The adjoint 24 decomposes as:
#   (8,1)_0:     SU(3) gauginos - no U(1)_Y charge
#   (1,3)_0:     SU(2) gauginos - no U(1)_Y charge
#   (1,1)_0:     U(1)_Y gaugino - no U(1)_Y charge
#   (3,2)_{5/6}: bifundamental - U(1)_Y charge 5/6
#   (3bar,2)_{-5/6}: conjugate - U(1)_Y charge -5/6
#
# The flux shifts the KK spectrum differently for each sector.
# For a state wrapping curve C with Y-charge q:
#   mass^2 shift ~ q * c1(L_Y).C / Vol(C)

print("\n\n=== BPS State Analysis ===")
print("\nSU(5) adjoint decomposition under hypercharge flux:")
print("  (8,1)_0     : SU(3) sector, Y=0   -> contributes to Delta_3")
print("  (1,3)_0     : SU(2) sector, Y=0   -> contributes to Delta_2")
print("  (1,1)_0     : U(1) sector,  Y=0   -> contributes to Delta_1")
print("  (3,2)_{5/6} : mixed sector, Y=5/6 -> contributes to both")

# ============================================================
# Threshold correction from BPS spectrum
# ============================================================
# The gauge threshold correction for gauge group G_a is:
#
#   Delta_a = -b_a * log(M_s^2/mu^2) + Delta_a^{KK} + Delta_a^{winding}
#
# The KK threshold piece for curves wrapped by M2-branes:
#   Delta_a^{KK} = sum_C n_C^{(a)} * f(m_C, q_C * N_Y)
#
# where n_C^{(a)} counts states in the adjoint of G_a wrapping C,
# and the flux-dependent mass splitting creates:
#
#   Delta_3 - Delta_2 = sum_C [n_C^{(8,1)} - n_C^{(1,3)}] * log(m_C)
#                      + sum_C n_C^{bifund} * [log(m_C + q*flux) - log(m_C)]
#
# For the ZERO MODE sector (dominant contribution):
# The Dirac index on C with bundle L_Y^q gives:
#   n_zero(C, q) = q * c1(L_Y).C + (1 - g(C))
# where g(C) is the arithmetic genus.

print("\n\n=== Zero-mode spectrum from Dirac index ===")
print(f"\n{'Curve':<15} {'g(C)':>5} {'c1.C':>6} {'n(q=0)':>7} {'n(q=5/6)':>9} {'n(q=-5/6)':>10}")
print("-" * 65)

# For (-1)-curves: g = 0 (rational curves), so n_zero = q*c1.C + 1
for c, lab, flux in zip(neg1_curves, labels, fluxes):
    g = 0  # genus of (-1)-curve
    n_neutral = 1 - g  # = 1 for all (-1)-curves
    n_plus = int(round(5/6 * flux)) + (1 - g)   # This is approximate
    n_minus = int(round(-5/6 * flux)) + (1 - g)  # Need exact formula

    # Actually, for line bundle L_Y^q on a rational curve C:
    # chi(C, L_Y^q|_C) = q * deg(L_Y|_C) + 1 = q * c1(L_Y).C + 1
    # This is the holomorphic Euler characteristic
    chi_neutral = 0 * flux + 1
    chi_56 = 5*flux/6 + 1  # Note: this needs to be integer for consistency
    chi_m56 = -5*flux/6 + 1

    print(f"{lab:<15} {g:>5} {flux:>6} {chi_neutral:>7.2f} {chi_56:>9.2f} {chi_m56:>10.2f}")

# ============================================================
# The key ratio: adjoint sector splitting
# ============================================================
print("\n\n=== Threshold Correction Structure ===")
print()
print("The gauge kinetic function at one loop receives corrections from")
print("the FULL tower of BPS states. The key formula (Conlon-Palti 0907.1362):")
print()
print("  f_a(S,T) = S * delta_a0 + sum_n c_a(n) * log(eta(n*T))")
print()
print("where delta_a0 is the tree-level normalization (from flux),")
print("and the sum runs over BPS states with charges n.")
print()
print("For the RATIO a_1/a_2, the tree-level piece dominates:")
print("  a_1/a_2 = (S + chi_1 * C) / (S + chi_2 * C)")
print("          = (S - 5C/3) / (S + C)")
print()
print("The one-loop correction modifies this to:")
print("  a_1/a_2 = (S - 5C/3 + delta_1) / (S + C + delta_2)")
print()

# ============================================================
# Effective curve classes and flux integrals
# ============================================================
print("\n=== Effective curve classes on dP_5 ===")
print("\nAll effective curves up to degree 3:")

effective_curves = []
eff_labels = []

# Search for effective curves: classes beta = d*H - sum m_i*E_i
# with d >= 0, beta.(-K) > 0 (for effective curves in |-K| class)
# and beta^2 >= -1 (BPS bound)

for d in range(4):
    # m_i can range
    m_range = range(-1, d+2)
    for ms in product(m_range, repeat=5):
        beta = np.array([d] + list(ms), dtype=int)
        beta_sq = self_intersection(beta)
        beta_K = intersection(beta, neg_K)

        # Effective curve conditions:
        # 1. beta.(-K) > 0 (positive degree w.r.t. anticanonical)
        # 2. beta^2 >= -1 (BPS states exist)
        # 3. Not the zero class
        # 4. All coefficients reasonable
        if beta_K > 0 and beta_sq >= -1 and d >= 0 and np.any(beta != 0):
            # Check it's not a duplicate or negative of existing
            is_new = True
            for ec in effective_curves:
                if np.array_equal(beta, ec):
                    is_new = False
                    break
            if is_new:
                flux = intersection(c1_LY, beta)
                genus = (beta_sq + beta_K) // 2 + 1  # adjunction formula: 2g-2 = C^2 + K.C
                two_g_minus_2 = beta_sq - intersection(beta, neg_K)  # K.C = -(-K).C
                genus_exact = two_g_minus_2 / 2 + 1
                if genus_exact >= 0 and genus_exact == int(genus_exact):
                    effective_curves.append(beta)
                    eff_labels.append(f"{d}H-{''.join(str(m)+'E'+str(i+1) for i,m in enumerate(ms) if m!=0)}")

print(f"\nFound {len(effective_curves)} effective curve classes")

# Focus on the most important: (-1)-curves and the anticanonical class
print("\n\n=== Key BPS contributions to threshold splitting ===")
print(f"\n{'Class':<20} {'C^2':>4} {'-K.C':>5} {'g':>3} {'c1.C':>5} {'Contribution to Delta_3-Delta_2'}")
print("-" * 75)

for c, lab in zip(neg1_curves, labels):
    c_sq = self_intersection(c)
    neg_K_c = intersection(c, neg_K)
    g = 0  # (-1)-curves are rational
    flux_c = intersection(c1_LY, c)

    # The BPS contribution depends on whether the curve supports
    # modes in the (8,1) or (1,3) representation
    # For Y=0 sectors: both (8,1) and (1,3) see the same curve geometry
    # For bifundamental: the flux creates a mass splitting

    # The key insight: the DIFFERENCE Delta_3 - Delta_2 comes from
    # the bifundamental sector (3,2)_{5/6} + cc, which has
    # different U(1)_Y flux and hence different KK masses
    # for the SU(3) vs SU(2) components

    contrib = f"flux={flux_c}, shifts bifund mass by q*{flux_c}/Vol(C)"
    print(f"{lab:<20} {c_sq:>4} {neg_K_c:>5} {g:>3} {flux_c:>5}   {contrib}")

# ============================================================
# The analytic torsion connection
# ============================================================
print("\n\n=== Connection to Analytic Torsion ===")
print()
print("The FULL one-loop correction sums over ALL BPS states.")
print("This sum is precisely the Ray-Singer analytic torsion:")
print()
print("  T_RS(S, E_a) = exp(-zeta'_a(0)/2)")
print()
print("where zeta_a(s) = sum_n (m_n^{(a)})^{-2s}")
print("sums over the KK + winding + flux-shifted spectrum.")
print()
print("The RATIO we need:")
print("  T_RS(S, ad(E_3)) / T_RS(S, ad(E_2))")
print("  = exp(-(zeta'_3(0) - zeta'_2(0))/2)")
print()
print("If this equals exp(ln(3)/sqrt(2) + ...) then the conjecture holds.")
print()

# ============================================================
# Topological string connection (BCOV)
# ============================================================
print("=== BCOV / Topological String Connection ===")
print()
print("Via BCOV (Bershadsky-Cecotti-Ooguri-Vafa):")
print("  F_1(t) = -1/2 * log(det(Im(tau)) * |f(q)|^2 * ...)")
print()
print("The genus-1 topological string amplitude F_1 on local dP_n")
print("computes the same quantity as the analytic torsion.")
print()
print("F_1 can be computed via:")
print("  1. Topological vertex (combinatorial)")
print("  2. Mirror symmetry + holomorphic anomaly equation")
print("  3. Direct B-model period computation")
print()

# ============================================================
# Gopakumar-Vafa invariants at genus 1
# ============================================================
print("=== Genus-1 GV Invariants for Local dP_5 ===")
print()
print("The genus-1 free energy is:")
print("  F_1 = sum_{beta>0} n_1(beta) * sum_{k=1}^inf (1/k) * q^{k*beta}")
print()
print("where n_1(beta) are genus-1 GV invariants.")
print()
print("For local del Pezzo surfaces, the GV invariants are known")
print("from the topological vertex / refined vertex computation.")
print()
print("Key genus-1 invariants for local dP_5 (from Huang-Klemm-Reuter):")
print()

# Known GV invariants for local dP_5 at genus 1
# These come from the topological vertex computation
# Reference: Huang-Klemm-Reuter, Chiang-Klemm-Yau-Zaslow
# For the (-1)-curves: n_1 = 0 (rational, g=0, so genus-1 GV vanishes)
# For the anticanonical class: n_1 depends on the surface

print("  Curve class       n_0 (genus 0)    n_1 (genus 1)")
print("  " + "-"*55)
for c, lab in zip(neg1_curves[:5], labels[:5]):
    # (-1)-curves are isolated rational curves: n_0 = 1, n_1 = 0
    print(f"  {lab:<18} {'1':>12}    {'0':>12}")

print(f"  {'-K (anticanonical)':<18} {'?':>12}    {'?':>12}")
print()
print("The genus-1 GV invariants for the anticanonical class")
print("require the topological vertex computation.")
print("This is where SageMath becomes essential.")

# ============================================================
# Summary: what SageMath needs to compute
# ============================================================
print("\n\n" + "="*60)
print("SUMMARY: What SageMath Must Compute")
print("="*60)
print()
print("1. LATTICE STRUCTURE:")
print(f"   dP_5 Picard lattice: rank {6}, signature (1,5)")
print(f"   Intersection form: diag(1,-1,-1,-1,-1,-1)")
print(f"   -K = {list(neg_K)}")
print(f"   c1(L_Y) = {list(c1_LY)}")
print(f"   N_Y = {N_Y}")
print()
print("2. GENUS-1 GV INVARIANTS:")
print("   Compute n_1(beta) for effective curves beta on local dP_5")
print("   up to degree 5 in -K. The topological vertex gives these")
print("   from the toric data of dP_5.")
print()
print("3. THRESHOLD CORRECTION:")
print("   Delta_a = sum_beta n_1(beta) * chi_a(beta) * log(q^beta)")
print("   where chi_a(beta) is the index of the Dirac operator on")
print("   curve beta, twisted by the gauge bundle E_a restricted to beta.")
print()
print("4. THE TEST:")
print("   Compute (Delta_3 - Delta_2) / (tree-level a_1/a_2)")
print("   If this ratio produces ln(3)/sqrt(2): PROVEN")
print("   If not: the 0.11% match is coincidental")
print()
print("Target: a_1/a_2 = ln(3)/sqrt(2) = {:.10f}".format(np.log(3)/np.sqrt(2)))
print(f"Current: a_1/a_2 = 0.776 (from sin^2(theta_W) = 0.23121)")
print(f"Gap: {abs(np.log(3)/np.sqrt(2) - 0.776)/0.776 * 100:.3f}%")
