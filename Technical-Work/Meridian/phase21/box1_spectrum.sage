"""
Spectrum of the Dolbeault Laplacian box_1 on (0,1)-forms on CP^2
================================================================

CP^2 = SU(3)/U(2). Peter-Weyl decomposition:
L^2(Omega^{0,q}(CP^2, O(k))) = bigoplus V_{(a,b)} with multiplicity
= dim Hom_{U(2)}(V_{(a,b)}|_{U(2)}, sigma_{q,k})

where sigma_{q,k} is the U(2) representation on Lambda^q(m^-) tensor det^k.

The Laplacian eigenvalue on V_{(a,b)} is the SU(3) Casimir:
C_2(a,b) = (a^2 + ab + b^2 + 3a + 3b) / 3

Strategy:
1. For each SU(3) irrep (a,b), branch to U(2) using the Weyl character formula
2. Count how many times the relevant U(2) rep appears
3. Total multiplicity = dim(a,b) * branching_multiplicity

For (0,0)-forms (functions) with O(k): sigma = det^k
For (0,1)-forms with O(k): sigma = conjugate_fundamental tensor det^k

Under U(2) subset SU(3), the embedding is:
  SU(3) fundamental (1,0) -> standard U(2) rep + det^{-1} piece

The weights of SU(3) under the maximal torus T^2 are:
  (1,0): weights (1,0), (0,1), (-1,-1)  [in epsilon basis: e1, e2, e3=-e1-e2]

U(2) subset SU(3): U(2) acts on first two coordinates.
  Standard U(2) rep has weights e1, e2 (the first two weights of the fundamental)
  The third weight e3 = -e1-e2 is the U(1) factor: det^{-1}

So the branching of SU(3) fundamental (1,0) to U(2):
  (1,0) -> std oplus det^{-1}  (as U(2) reps, with std = fund of SU(2) x det charge)

More precisely, under U(2) = S(U(2) x U(1)):
  The SU(3) maximal torus weights (m1, m2) for the U(2) subgroup give:
  - SU(2) spin j from the SU(2) part
  - U(1) charge q from the det part

For the fundamental (1,0) of SU(3):
  Weight e1 = (1,0): SU(2) weight +1/2, U(1) charge +1/3  -> (j=1/2, q=1/3)
  Weight e2 = (0,1): SU(2) weight -1/2, U(1) charge +1/3  -> (j=1/2, q=1/3)
  Weight e3 = (-1,-1): SU(2) weight 0, U(1) charge -2/3   -> (j=0, q=-2/3)

So (1,0)|_{U(2)} = (j=1/2, q=1/3) + (j=0, q=-2/3)

The anti-holomorphic cotangent T*^{0,1} at the identity coset:
  As a U(2) rep, T*^{0,1} corresponds to m^- = the negative root spaces not in U(2).

The roots of SU(3) are: +/-(e1-e2), +/-(e1-e3), +/-(e2-e3)
The U(2) root is +/-(e1-e2).
The complement roots: +/-(e1-e3), +/-(e2-e3)
The holomorphic tangent (positive roots not in U(2)): e1-e3, e2-e3
The anti-holomorphic cotangent (negative of positive complement): -(e1-e3) = e3-e1, -(e2-e3) = e3-e2

Wait, let me be more careful.

T^{1,0} = m^+ spanned by root vectors for e1-e3 and e2-e3
T^{0,1} = m^- spanned by root vectors for e3-e1 and e3-e2

As U(2) representations:
  m^+ has weights: e1-e3 = (2,1) and e2-e3 = (1,2)...

Actually, let me just use the U(2) weight directly.
Under the torus of U(2) subset SU(3), the weight of a root vector is:
  Root e_i - e_j acts with weight (under the Cartan of U(2)):
  - SU(2) weight: projection onto (e1-e2)/2
  - U(1) charge: projection onto (e1+e2)/2 (or rather (e1+e2+e3)/3 = 0,
    so the U(1) of U(2) is (e1+e2-2e3)/3*sqrt(3)... )

This is getting complicated. Let me use a different approach.
"""

# ===================================================================
# APPROACH: Direct weight decomposition using SageMath's Lie algebra
# ===================================================================

from sage.all import *

# SU(3) root system
W = WeylCharacterRing("A2", style="coroots")

# Define fundamental representations
V10 = W(1,0)  # fundamental 3
V01 = W(0,1)  # anti-fundamental 3-bar
V11 = W(1,1)  # adjoint 8

print("=== SU(3) Representations ===")
print(f"dim(1,0) = {V10.degree()}")  # 3
print(f"dim(0,1) = {V01.degree()}")  # 3
print(f"dim(1,1) = {V11.degree()}")  # 8

# Casimir for SU(3) irrep (a,b) in Dynkin labels:
# C_2(a,b) = (a^2 + ab + b^2 + 3a + 3b) / 3
def casimir(a, b):
    return (a**2 + a*b + b**2 + 3*a + 3*b) / 3

print(f"\nCasimir checks:")
print(f"C_2(1,0) = {float(casimir(1,0))}")  # should be 4/3
print(f"C_2(0,1) = {float(casimir(0,1))}")  # should be 4/3
print(f"C_2(1,1) = {float(casimir(1,1))}")  # should be 3
print(f"C_2(2,2) = {float(casimir(2,2))}")  # should be 8 = 2*4

# ===================================================================
# VERIFICATION: Scalar spectrum on O(0)
# Functions = sections of trivial bundle
# SU(3) irreps that appear: (l,l) for l = 0, 1, 2, ...
# Eigenvalue = C_2(l,l) = l(l+2)
# Multiplicity = dim(l,l) = (l+1)^3
# ===================================================================

print("\n=== Scalar Laplacian on O(0) [VERIFICATION] ===")
print(f"{'l':>3} {'(a,b)':>8} {'C_2':>8} {'l(l+2)':>8} {'dim':>8} {'(l+1)^3':>8}")
for l in range(6):
    a, b = l, l
    c2 = casimir(a, b)
    dim_ab = W(a,b).degree()
    print(f"{l:3d} ({a},{b}){' '*(4-len(str(a))-len(str(b)))} {float(c2):8.1f} {l*(l+2):8d} {dim_ab:8d} {(l+1)**3:8d}")

# ===================================================================
# (0,1)-FORMS on O(0)
#
# The anti-holomorphic cotangent T*^{0,1} as U(2) rep:
# Under the embedding U(2) -> SU(3), the isotropy rep m^- = T*^{0,1}
# corresponds to the (0,1) representation of SU(3) restricted to U(2)
# minus the "radial" direction.
#
# More precisely: for CP^2 = SU(3)/U(2), sections of T*^{0,1} are
# sections of the bundle SU(3) x_{U(2)} m^-, where m^- is a
# 2-dimensional U(2) representation.
#
# By Frobenius reciprocity:
# Hom_{SU(3)}(V_{(a,b)}, L^2(T*^{0,1}))
# = Hom_{U(2)}(V_{(a,b)}|_{U(2)}, m^-)
#
# The (0,1)-forms with values in O(k) use m^- tensor det^k.
#
# TENSOR PRODUCT APPROACH:
# L^2(T*^{0,1}) subset L^2(functions) tensor m^-
# = (bigoplus_{l>=0} V_{(l,l)}) tensor m^-
#
# But m^- as an SU(3) representation is part of the adjoint.
# Actually, for the homogeneous space approach:
# Gamma(T*^{0,1} tensor O(k)) = bigoplus V_{(a,b)}
# where (a,b) contributes with multiplicity =
#   dim Hom_{U(2)}(m^- tensor det^k, V_{(a,b)}|_{U(2)})
#
# For the GLOBAL sections approach, we can use the fact that
# on a symmetric space, the spectrum of box_q on Omega^{0,q}(O(k))
# can be computed from the TENSOR PRODUCT of the scalar spectrum
# with the isotropy representation.
#
# Specifically, the Hodge Laplacian on q-forms on G/K has eigenspaces
# that are NOT simply tensor products. The correct formula involves
# the CASIMIR operator, and the spectrum is:
#
# {C_2^G(lambda) : lambda appears in Ind_K^G(Lambda^q(m^-) tensor det^k)}
#
# ===================================================================

# The key insight: on CP^2, the (0,1)-forms transform under SU(3) as
# those irreps (a,b) that, when restricted to U(2), contain the
# representation m^- (the 2-dim anti-holomorphic cotangent).

# For CP^2 = SU(3)/U(2):
# The complexified tangent decomposes as m = m^+ + m^-
# m^+ and m^- are 2-dimensional U(2) representations
# m^+ corresponds to roots e1-e3 and e2-e3 (positive non-U(2) roots)
# m^- corresponds to roots e3-e1 and e3-e2

# As SU(2) x U(1) representations (where U(1) is the center of U(2)):
# m^+ has SU(2) spin j=1/2 and some U(1) charge
# m^- has SU(2) spin j=1/2 and opposite U(1) charge

# TENSOR PRODUCT METHOD:
# Omega^{0,1}(CP^2, O(k)) contains the SU(3) irreps that appear in:
#   V_{(l,l)} tensor V_iso
# where V_iso encodes the isotropy representation.

# On CP^2, T*^{0,1} is the tautological bundle Omega^1 ≅ O(-1) tensor ...
# Actually, the cotangent bundle of CP^n is:
# Omega^1(CP^n) = O(-1) tensor Q* where Q is the universal quotient bundle
# For CP^2: Omega^{0,1} = the anti-holomorphic part

# SIMPLER: Use the EULER SEQUENCE
# 0 -> O -> O(1)^3 -> T^{1,0} -> 0
# Dualizing: 0 -> Omega^{1,0} -> O(-1)^3 -> O -> 0
# Conjugating: 0 -> Omega^{0,1} -> O(-1)^3 -> O -> 0 (same on CP^2)

# NO WAIT. On CP^n, the holomorphic tangent bundle:
# 0 -> O -> O(1)^{n+1} -> T^{1,0}(CP^n) -> 0
# So T^{1,0}(CP^2) fits in: 0 -> O -> O(1)^3 -> T^{1,0} -> 0
# Dualizing: 0 -> Omega^{1,0} -> O(-1)^3 -> O -> 0
# So Omega^{1,0} ≅ kernel(O(-1)^3 -> O)

# PRACTICAL APPROACH:
# Just compute which SU(3) irreps (a,b) appear in sections of Omega^{0,1}
# by using the tensor product decomposition with the Euler sequence.

# From the Euler sequence, sections of T^{1,0} fit into:
# H^0(CP^2, O(1))^3 -> H^0(CP^2, T^{1,0}) -> H^1(CP^2, O) = 0
# So H^0(T^{1,0}) = Sym^1(C^3)^3 / C = C^9/C = C^8 = adjoint

# For general L^2 sections (not just holomorphic):
# L^2(Omega^{0,1}) sits inside L^2(O(-1))^3 (from the dual Euler sequence)

# Actually, the cleanest approach: use the fact that the HODGE-DOLBEAULT
# operator on (0,1)-forms with values in O(k) has the same spectrum as
# the SCALAR Laplacian on O(k) tensor T*^{0,1}.

# On a Hermitian symmetric space, the spectrum of Delta on sections of
# any homogeneous bundle E = G x_K sigma is:
# {C_2(lambda) : lambda in G-hat with [sigma : lambda|_K] > 0}
# with multiplicity dim(lambda) * [sigma : lambda|_K]

# So we need to find ALL (a,b) such that V_{(a,b)}|_{U(2)} contains
# the representation m^- tensor det^k.

# KEY IDENTIFICATION:
# m^- as a representation of U(2) is the CONJUGATE of m^+.
# m^+ is the representation with SU(2) spin 1/2 and U(1) charge +1
# (from the positive roots e1-e3 and e2-e3 which have U(1) charges...)

# Actually, let me just USE the structure theory directly.
# On CP^2, (0,1)-forms with values in O(0) correspond to:
# The INDUCED representation Ind_{U(2)}^{SU(3)}(m^-)

# The branching rule for SU(3) -> SU(2) x U(1) (the standard Levi decomposition)
# is well-known. For (a,b) -> sum of (j, q) where j is the SU(2) spin
# and q is the U(1) charge.

# For the STANDARD embedding U(2) in SU(3):
# (a,b) branches to: for each weight (m1, m2) of (a,b),
# j is determined by the SU(2) content, q = (m1 + m2 - 2*m3)/3

# Let me use a PRACTICAL NUMERICAL approach instead.
# Compute the branching using weight spaces.

print("\n\n=== COMPUTING box_1 SPECTRUM VIA BRANCHING ===")

# SU(3) weights in the epsilon basis: w = (w1, w2, w3) with w1+w2+w3 = 0
# Dynkin labels (a,b) correspond to highest weight a*L1 + b*L2
# where L1 = (2/3, -1/3, -1/3) and L2 = (1/3, 1/3, -2/3)

# U(2) subgroup: block diagonal (2x2 | 1x1) in SU(3)
# SU(2) part: generated by e1-e2 root
# U(1) part: diag(t, t, t^{-2}) (center of U(2) in SU(3))

# A weight (w1, w2, w3) of SU(3) has:
# - SU(2) weight: m = (w1 - w2)/2 (in the half-integer convention,
#   actually m = w1 - w2 for the integer weight convention)
# - U(1) charge: q = w1 + w2 (= -w3 since w1+w2+w3=0)

# Wait, I need to be more precise. Under U(2) = S(U(2) x U(1)) subset SU(3):
# The Cartan subalgebra of SU(3) has generators H1, H2.
# H1 = diag(1,-1,0) generates SU(2) Cartan
# H2 = diag(1,1,-2)/sqrt(3) generates U(1)

# A weight in Dynkin basis (m1, m2) means H1 eigenvalue m1 and H2 eigenvalue m2?
# No. In the weight lattice, m1 = <alpha_1^vee, lambda>, m2 = <alpha_2^vee, lambda>.

# Let me use the epsilon basis instead.
# SU(3) highest weight (a,b) in Dynkin:
#   highest weight in epsilon basis = (a+b)/3 * (2,-1,-1) + b/3 * (-1,2,-1) ??? no.

# Standard conversion:
# alpha_1 = e1 - e2 = (1,-1,0)
# alpha_2 = e2 - e3 = (0,1,-1)
# L1 (fundamental weight 1) = (2/3, -1/3, -1/3)
# L2 (fundamental weight 2) = (1/3, 1/3, -2/3)

# (a,b) has highest weight a*L1 + b*L2 = ((2a+b)/3, (-a+b)/3, (-a-2b)/3)

# Under U(2) branching:
# SU(2) weight of an SU(3) weight (w1,w2,w3):
#   w1 - w2 (eigenvalue of H_alpha1 = diag(1,-1,0))
# U(1) charge: w1 + w2 (= -w3, eigenvalue of diag(1,1,-2)/3 * 3/2 ... normalization varies)

# The m^- representation has weights:
# Root e3-e1: weight (w1,w2,w3) = (-1,0,1), SU(2) wt = -1, U(1) charge = -1
# Root e3-e2: weight (w1,w2,w3) = (0,-1,1), SU(2) wt = +1, U(1) charge = -1
# Wait, these should be the OPPOSITE of the root weights for the tangent space.

# Actually, m^- (the anti-holomorphic tangent) has weights that are the
# negatives of the positive complement roots.
# Positive complement roots: e1-e3 = (1,0,-1) and e2-e3 = (0,1,-1)
# Negative complement roots: e3-e1 = (-1,0,1) and e3-e2 = (0,-1,1)
# These are the weights of m^- as a representation of the maximal torus.

# m^- weights (in epsilon basis, projected to U(2) Cartan):
# e3-e1: SU(2) weight = w1-w2 = -1-0 = -1, U(1) charge = w1+w2 = -1+0 = -1
# e3-e2: SU(2) weight = w1-w2 = 0-(-1) = 1, U(1) charge = w1+w2 = 0+(-1) = -1

# So m^- = SU(2) spin 1/2 (weights +1, -1) with U(1) charge -1
# In terms of U(2) representations: m^- = fundamental of SU(2) tensor det^{-1}
# (where det is the determinant representation of U(2))

# Wait, the U(1) charge needs normalization. The det of U(2) acting on C^2 has charge 1
# per unit. If diag(a,b) in U(2) has det ab, then the character is (a)(b) = det.
# The U(1) charge I defined is w1+w2, and for the standard rep (e1, e2) of U(2),
# the charges are (1,0) and (0,1) with sum 1. So det has charge 1.
# m^- has U(1) charge -1 per weight, so m^- has det charge = -1.
# m^- = fund(SU(2)) tensor det^{-1} of U(2).

# For (0,1)-forms with O(k): we need m^- tensor det^k = fund(SU(2)) tensor det^{k-1}

# BRANCHING MULTIPLICITY:
# For SU(3) irrep (a,b), the multiplicity of (j, q) in the branching is:
# the number of weights of (a,b) with SU(2) weight system having spin j
# and U(1) charge q.

# An SU(3) weight (w1,w2,w3) with w1+w2+w3=0 gives:
# U(1) charge = w1 + w2 = -w3
# SU(2) weight = w1 - w2

# We need to count how many times the U(2) rep (j=1/2, q=k-1) appears
# in the branching of V_{(a,b)}.

# This means: among all weights of (a,b) with U(1) charge = k-1,
# how does the set of SU(2) weights decompose into SU(2) irreps?
# The multiplicity of j=1/2 in this decomposition.

# For O(0): q = k-1 = -1.
# We need weights of (a,b) with w1+w2 = -1, i.e., w3 = 1.
# (Remember w1+w2+w3 = 0, so w3 = -(w1+w2) = -(-1) = 1)

# Let me implement this.

def weights_of_irrep(a, b):
    """Return list of (weight, multiplicity) for SU(3) irrep (a,b) in Dynkin labels.
    Weight in epsilon basis (w1,w2,w3) with w1+w2+w3=0."""
    # Use SageMath's built-in
    R = RootSystem("A2")
    P = R.weight_space()
    alpha = R.root_system().ambient_space().simple_roots()

    # Actually use the WeylCharacterRing
    rep = W(a,b)
    # Get the weight multiplicities
    wt_dict = rep.weight_multiplicities()
    result = []
    for wt, mult in wt_dict.items():
        # Convert weight to epsilon basis
        # In SageMath, A2 weights are in the fundamental weight basis
        # Need to convert to epsilon coordinates
        coeffs = list(wt.to_vector())  # coefficients in fundamental weight basis
        # Fundamental weights in epsilon: L1 = (2/3, -1/3, -1/3), L2 = (1/3, 1/3, -2/3)
        w1 = QQ(2)/3 * coeffs[0] + QQ(1)/3 * coeffs[1]
        w2 = -QQ(1)/3 * coeffs[0] + QQ(1)/3 * coeffs[1]
        w3 = -QQ(1)/3 * coeffs[0] - QQ(2)/3 * coeffs[1]
        result.append(((w1, w2, w3), int(mult)))
    return result

def branching_multiplicity_spin_half(a, b, q_target):
    """Count how many times SU(2) spin-1/2 with U(1) charge q_target
    appears in the branching of SU(3) irrep (a,b) to U(2).

    U(1) charge of a weight (w1,w2,w3) = w1 + w2 = -w3.
    SU(2) weight = w1 - w2.
    """
    weights = weights_of_irrep(a, b)

    # Filter to weights with U(1) charge = q_target
    # i.e., w1 + w2 = q_target, i.e., w3 = -q_target
    su2_weights = {}  # {SU(2) weight: multiplicity}
    for (w1, w2, w3), mult in weights:
        if w3 == -q_target:
            m_su2 = w1 - w2  # SU(2) weight
            su2_weights[m_su2] = su2_weights.get(m_su2, 0) + mult

    if not su2_weights:
        return 0

    # Decompose the SU(2) weight system into irreps
    # Using the standard algorithm: highest weight method
    su2_wts = dict(su2_weights)  # copy
    spin_half_count = 0

    # Peel off irreps from highest to lowest
    while True:
        # Find highest non-zero weight
        max_m = None
        for m in sorted(su2_wts.keys(), reverse=True):
            if su2_wts[m] > 0:
                max_m = m
                break
        if max_m is None:
            break

        # This is a spin-j irrep with j = max_m (since SU(2) weight = w1-w2 is integer)
        j = max_m  # j is the highest weight (integer here, not half-integer)

        # Remove one copy of spin-j irrep (weights j, j-2, ..., -j)
        # Wait: SU(2) weights go j, j-1, ..., -j (integer steps for integer j)
        # But here the SU(2) weight = w1 - w2 which can be any integer
        # (since w1, w2 are in the weight lattice of SU(3))

        # SU(2) irrep of highest weight j has weights j, j-1, ..., -j
        # each with multiplicity 1
        for mm in range(int(j), int(-j)-1, -1):
            mm_rat = QQ(mm)
            if mm_rat not in su2_wts or su2_wts[mm_rat] <= 0:
                # Inconsistency - this shouldn't happen for a valid decomposition
                print(f"WARNING: inconsistency at (a,b)=({a},{b}), j={j}, m={mm}")
                break
            su2_wts[mm_rat] -= 1
            if su2_wts[mm_rat] == 0:
                del su2_wts[mm_rat]

        # Check if this was spin 1/2 (j=1 in our convention)
        # Wait: our SU(2) weight = w1 - w2, which is an INTEGER.
        # For the fundamental of SU(2), the weights are +1 and -1 (not +1/2, -1/2)
        # because the epsilon weights of SU(3) are integral.
        # So "spin 1/2" corresponds to j_max = 1 in our labeling.
        if j == 1:
            spin_half_count += 1

    return spin_half_count

# Test: scalar functions on O(0)
# These correspond to (j=0, q=0) i.e., trivial U(2) rep
# Should give (l,l) with multiplicity 1 each
print("\n--- Test: branching for scalar O(0) [should be (l,l) with mult 1] ---")
for a in range(5):
    for b in range(5):
        # For scalars on O(0): need (j=0, q=0)
        weights = weights_of_irrep(a, b)
        # Count singlets with q=0
        su2_weights_q0 = {}
        for (w1, w2, w3), mult in weights:
            if w3 == 0:  # q = -w3 = 0
                m_su2 = w1 - w2
                su2_weights_q0[m_su2] = su2_weights_q0.get(m_su2, 0) + mult

        # Count spin-0 (singlet) components
        if su2_weights_q0:
            # Peel off irreps
            wts = dict(su2_weights_q0)
            singlet_count = 0
            while True:
                max_m = None
                for m in sorted(wts.keys(), reverse=True):
                    if wts[m] > 0:
                        max_m = m
                        break
                if max_m is None:
                    break
                j = max_m
                for mm in range(int(j), int(-j)-1, -1):
                    mm_r = QQ(mm)
                    if mm_r in wts and wts[mm_r] > 0:
                        wts[mm_r] -= 1
                if j == 0:
                    singlet_count += 1

            if singlet_count > 0:
                print(f"  ({a},{b}): dim={W(a,b).degree()}, C2={float(casimir(a,b)):.1f}, singlet_mult={singlet_count}")

# Now compute box_1 spectrum for O(0)
print("\n\n=== box_1 spectrum on Omega^{0,1}(CP^2, O(0)) ===")
print(f"Need U(2) rep: (j=1/2, q=-1) i.e., spin-1 in integer convention, charge -1")
print(f"So w3 = -q = 1, and SU(2) highest weight = 1")
print()

eigenvalues_O0 = []
for a in range(15):
    for b in range(15):
        if a + b > 20:
            continue
        mult = branching_multiplicity_spin_half(a, b, -1)
        if mult > 0:
            c2 = casimir(a, b)
            dim_ab = W(a,b).degree()
            eigenvalues_O0.append((float(c2), dim_ab * mult, a, b, mult))

eigenvalues_O0.sort()
print(f"{'C_2':>8} {'total_mult':>10} {'(a,b)':>8} {'dim':>6} {'branch':>6}")
for c2, total, a, b, br in eigenvalues_O0[:25]:
    print(f"{c2:8.3f} {total:10d} ({a},{b}){' '*(4-len(str(a))-len(str(b)))} {W(a,b).degree():6d} {br:6d}")

# Now for O(2)
print("\n\n=== box_1 spectrum on Omega^{0,1}(CP^2, O(2)) ===")
print(f"Need U(2) rep: (j=1/2, q=1) i.e., spin-1 in integer convention, charge 1")
print(f"So w3 = -q = -1, and SU(2) highest weight = 1")
print()

eigenvalues_O2 = []
for a in range(15):
    for b in range(15):
        if a + b > 20:
            continue
        mult = branching_multiplicity_spin_half(a, b, 1)
        if mult > 0:
            c2 = casimir(a, b)
            dim_ab = W(a,b).degree()
            eigenvalues_O2.append((float(c2), dim_ab * mult, a, b, mult))

eigenvalues_O2.sort()
print(f"{'C_2':>8} {'total_mult':>10} {'(a,b)':>8} {'dim':>6} {'branch':>6}")
for c2, total, a, b, br in eigenvalues_O2[:25]:
    print(f"{c2:8.3f} {total:10d} ({a},{b}){' '*(4-len(str(a))-len(str(b)))} {W(a,b).degree():6d} {br:6d}")

# Verify: H^{0,1}(CP^2, O(0)) = 0, so no zero eigenvalue
print("\n=== Consistency checks ===")
min_ev_O0 = min(c2 for c2, _, _, _, _ in eigenvalues_O0) if eigenvalues_O0 else None
min_ev_O2 = min(c2 for c2, _, _, _, _ in eigenvalues_O2) if eigenvalues_O2 else None
print(f"Minimum eigenvalue for O(0): {min_ev_O0} (should be > 0 since H^{{0,1}}(CP^2,O)=0)")
print(f"Minimum eigenvalue for O(2): {min_ev_O2}")

# Check if multiplicities follow a pattern
print("\n=== Looking for multiplicity pattern ===")
print("\nO(0) eigenvalues grouped:")
from collections import defaultdict
ev_groups_O0 = defaultdict(int)
for c2, total, a, b, br in eigenvalues_O0:
    ev_groups_O0[c2] += total

for c2 in sorted(ev_groups_O0.keys())[:20]:
    print(f"  lambda = {c2:8.3f}, total mult = {ev_groups_O0[c2]}")

print("\nO(2) eigenvalues grouped:")
ev_groups_O2 = defaultdict(int)
for c2, total, a, b, br in eigenvalues_O2:
    ev_groups_O2[c2] += total

for c2 in sorted(ev_groups_O2.keys())[:20]:
    print(f"  lambda = {c2:8.3f}, total mult = {ev_groups_O2[c2]}")
