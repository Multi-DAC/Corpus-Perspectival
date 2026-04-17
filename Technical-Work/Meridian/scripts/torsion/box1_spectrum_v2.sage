"""
box_1 spectrum on CP^2 via SU(3) branching — v2 (fixed API)
"""
from sage.all import *
from collections import defaultdict

W = WeylCharacterRing("A2", style="coroots")

def casimir(a, b):
    return QQ(a**2 + a*b + b**2 + 3*a + 3*b) / 3

def get_weights_epsilon(a, b):
    """Get weights of SU(3) irrep (a,b) in Dynkin labels.
    Returns list of ((w1,w2,w3), multiplicity) in epsilon basis."""
    rep = W(a, b)
    wt_dict = rep.weight_multiplicities()
    result = []
    for wt, mult in wt_dict.items():
        # wt is in the coroot (Dynkin) basis for A2
        # Get coefficients: wt = m1*omega_1 + m2*omega_2
        coeffs = wt.to_vector()
        m1, m2 = coeffs[0], coeffs[1]
        # Convert to epsilon basis:
        # omega_1 = (2/3, -1/3, -1/3), omega_2 = (1/3, 1/3, -2/3)
        w1 = QQ(2*m1 + m2) / 3
        w2 = QQ(-m1 + m2) / 3
        w3 = QQ(-m1 - 2*m2) / 3
        result.append(((w1, w2, w3), int(mult)))
    return result

def branching_mult_j1(a, b, q_target):
    """Count spin-1 (in integer convention = physical spin-1/2) with U(1) charge q_target.

    For (0,1)-forms on O(k): q_target = k-1.
    m^- has SU(2) weights +1,-1 and U(1) charge -1.
    So (0,1)-forms tensor O(k) need the U(2) rep with
    SU(2) spin 1 (weights +1,-1) and U(1) charge k-1.

    U(1) charge = w1 + w2 = -w3, SU(2) weight = w1 - w2.
    """
    weights = get_weights_epsilon(a, b)

    # Filter to weights with U(1) charge = q_target (i.e., w3 = -q_target)
    su2_mults = defaultdict(int)
    for (w1, w2, w3), mult in weights:
        if w3 == -q_target:
            m_su2 = w1 - w2  # integer-valued SU(2) weight
            su2_mults[m_su2] += mult

    if not su2_mults:
        return 0

    # Decompose into SU(2) irreps by peeling from highest weight
    wts = dict(su2_mults)
    j1_count = 0

    while True:
        # Find highest weight with nonzero multiplicity
        nonzero = [(m, c) for m, c in wts.items() if c > 0]
        if not nonzero:
            break
        max_m = max(m for m, c in nonzero)
        j = int(max_m)  # highest weight = 2j in half-integer convention, but here it's integer

        # Remove one copy of this irrep (weights j, j-1, ..., -j)
        for mm in range(j, -j-1, -1):
            wts[QQ(mm)] = wts.get(QQ(mm), 0) - 1

        # j=1 means weights +1, 0, -1 -> that's spin-1 (3-dimensional SU(2) irrep)
        # j=1 in our convention corresponds to the ADJOINT of SU(2), not the fundamental!
        # The fundamental of SU(2) has weights +1, -1 (NO zero weight) -> j=1 with dim 2
        # Wait, SU(2) irrep of spin j has dimension 2j+1 and weights j, j-1, ..., -j
        # In integer labeling: "spin 1" has weights 1, 0, -1 (dim 3)
        # "spin 1/2" = what? In integer labeling, there's no half-integer.
        #
        # The issue: SU(3) weights are in the weight lattice which uses integers.
        # The standard representation of SU(2) has weights 1 and -1 in the
        # ROOT convention (where roots have length 2), not +1/2 and -1/2.
        # So the standard rep (dim 2) has highest weight 1.
        # The adjoint (dim 3) has highest weight 2.
        # General: dim = j+1 where j is the highest weight.
        #
        # So "spin 1/2" = highest weight 1, dim 2, weights {+1, -1}.
        # "spin 1" = highest weight 2, dim 3, weights {+2, 0, -2}.
        #
        # For m^-: weights are +1 and -1 with no 0 weight -> highest weight 1 -> dim 2.
        # This is the spin-1/2 (fundamental) of SU(2) in physical convention,
        # which has highest weight 1 in root convention.

        if j == 1:
            j1_count += 1

    return j1_count


print("=== VERIFICATION: scalar O(0) spectrum ===")
print("Expect (l,l) with branching mult 1 for singlet (j=0)")
print()

# For scalars: need U(2) singlet (j=0, q=0)
# That means w3 = 0 and SU(2) highest weight = 0
for l in range(8):
    a, b = l, l
    weights = get_weights_epsilon(a, b)
    # Count singlets at q=0
    su2_mults_q0 = defaultdict(int)
    for (w1, w2, w3), mult in weights:
        if w3 == 0:
            su2_mults_q0[w1-w2] += mult

    # Count spin-0 = highest weight 0
    wts = dict(su2_mults_q0)
    singlets = 0
    while True:
        nonzero = [(m, c) for m, c in wts.items() if c > 0]
        if not nonzero:
            break
        max_m = max(m for m, c in nonzero)
        j = int(max_m)
        for mm in range(j, -j-1, -1):
            wts[QQ(mm)] = wts.get(QQ(mm), 0) - 1
        if j == 0:
            singlets += 1

    if singlets > 0:
        dim_v = W(a,b).degree()
        c2 = float(casimir(a,b))
        print(f"  ({a},{b}): C2 = {c2:.1f} = {l}*{l+2}, dim = {dim_v} = {(l+1)**3}, singlets = {singlets}")


print("\n\n=== box_1 SPECTRUM: Omega^{0,1}(CP^2, O(0)) ===")
print("Need U(2) rep: fundamental SU(2) (hw=1) with U(1) charge q = -1")
print()

results_O0 = []
for a in range(20):
    for b in range(20):
        if a + b > 25:
            continue
        mult = branching_mult_j1(a, b, -1)
        if mult > 0:
            c2 = float(casimir(a, b))
            dim_v = W(a,b).degree()
            # Total multiplicity: dim(a,b) * branching_mult
            # Wait: no. The multiplicity in L^2 is dim(V_{(a,b)})
            # because by Peter-Weyl, L^2(G x_K sigma) = oplus V_lambda ot Hom_K(V_lambda, sigma)
            # The eigenspace for C_2 = C_2(lambda) has dimension
            # dim(V_lambda) * dim(Hom_K(V_lambda, sigma))
            # = dim(V_lambda) * branching_mult
            total = dim_v * mult
            results_O0.append((c2, total, a, b, mult, dim_v))

results_O0.sort()

print(f"{'C_2':>10} {'total_mult':>10} {'(a,b)':>8} {'dim_V':>7} {'br_mult':>7}")
for c2, total, a, b, br, dim_v in results_O0[:30]:
    print(f"{c2:10.4f} {total:10d} ({a},{b}){' '*(4-len(str(a))-len(str(b)))} {dim_v:7d} {br:7d}")


print("\n\n=== box_1 SPECTRUM: Omega^{0,1}(CP^2, O(2)) ===")
print("Need U(2) rep: fundamental SU(2) (hw=1) with U(1) charge q = 1")
print()

results_O2 = []
for a in range(20):
    for b in range(20):
        if a + b > 25:
            continue
        mult = branching_mult_j1(a, b, 1)
        if mult > 0:
            c2 = float(casimir(a, b))
            dim_v = W(a,b).degree()
            total = dim_v * mult
            results_O2.append((c2, total, a, b, mult, dim_v))

results_O2.sort()

print(f"{'C_2':>10} {'total_mult':>10} {'(a,b)':>8} {'dim_V':>7} {'br_mult':>7}")
for c2, total, a, b, br, dim_v in results_O2[:30]:
    print(f"{c2:10.4f} {total:10d} ({a},{b}){' '*(4-len(str(a))-len(str(b)))} {dim_v:7d} {br:7d}")


# Group by eigenvalue and look for patterns
print("\n\n=== EIGENVALUE GROUPING (O(0)) ===")
ev_O0 = defaultdict(int)
for c2, total, a, b, br, dim_v in results_O0:
    ev_O0[c2] += total

print(f"{'lambda':>10} {'mult':>10} {'predicted':>10}")
for lam in sorted(ev_O0.keys())[:20]:
    # Try to find a formula
    # For scalar: lambda = l(l+2), mult = (l+1)^3
    # For (0,1)-forms: maybe lambda = l(l+2) + c, mult = f(l)?
    print(f"{lam:10.4f} {ev_O0[lam]:10d}")


print("\n\n=== EIGENVALUE GROUPING (O(2)) ===")
ev_O2 = defaultdict(int)
for c2, total, a, b, br, dim_v in results_O2:
    ev_O2[c2] += total

print(f"{'lambda':>10} {'mult':>10}")
for lam in sorted(ev_O2.keys())[:20]:
    print(f"{lam:10.4f} {ev_O2[lam]:10d}")


# Summary of what we need for the spectral zeta
print("\n\n=== SPECTRAL ZETA DATA ===")
print("\nFor O(0) (0,1)-forms:")
print("lambda_n, d_n (first 30 eigenvalue-multiplicity pairs):")
sorted_O0 = sorted(ev_O0.items())
for lam, mult in sorted_O0[:30]:
    print(f"  {lam:.6f}, {mult}")

print("\nFor O(2) (0,1)-forms:")
print("lambda_n, d_n (first 30 eigenvalue-multiplicity pairs):")
sorted_O2 = sorted(ev_O2.items())
for lam, mult in sorted_O2[:30]:
    print(f"  {lam:.6f}, {mult}")
