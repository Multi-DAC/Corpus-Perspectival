"""
box_1 spectrum — LEAN version
Only checks irreps where b+2a = 0 (mod 3) and a+b <= 15.
"""
from sage.all import *
from collections import defaultdict

W = WeylCharacterRing("A2", style="coroots")

def casimir(a, b):
    return QQ(a**2 + a*b + b**2 + 3*a + 3*b) / 3

def su2_branching_at_charge(a, b, q_target):
    """Return dict of {SU(2) hw j: count} for SU(3) irrep (a,b) at U(1) charge q_target.
    SU(2) weight = m1, U(1) charge = (m1 + 2*m2)/3."""
    rep = W(a, b)
    wm = rep.weight_multiplicities()

    su2_weights = defaultdict(int)
    for wt, mult in wm.items():
        coeffs = wt.to_vector()
        m1, m2 = coeffs[0], coeffs[1]
        q = QQ(m1 + 2*m2) / 3
        if q == q_target:
            su2_weights[int(m1)] += int(mult)

    if not su2_weights:
        return {}

    # Decompose into SU(2) irreps by peeling highest weight
    wts = dict(su2_weights)
    result = defaultdict(int)

    while True:
        nonzero = {m: c for m, c in wts.items() if c > 0}
        if not nonzero:
            break
        j = max(nonzero.keys())  # highest weight
        for mm in range(j, -j-1, -2):
            wts[mm] = wts.get(mm, 0) - 1
        result[j] += 1

    return dict(result)


# O(0): (0,1)-forms need SU(2) fund (j=1) at U(1) charge -1
# O(2): (0,1)-forms tensor O(2) need SU(2) fund (j=1) at U(1) charge +1
# Necessary condition for BOTH: b+2a = 0 (mod 3)

print("=== box_1 on O(0): charge = -1 ===")
print(f"{'(a,b)':>8} {'C2':>8} {'dim':>6} {'br_j1':>5} {'tot_mult':>8} {'SU2 decomp'}")

spec_O0 = []
for s in range(1, 20):  # s = a + b
    for a in range(s+1):
        b = s - a
        if (b + 2*a) % 3 != 0:
            continue
        decomp = su2_branching_at_charge(a, b, QQ(-1))
        j1 = decomp.get(1, 0)
        if j1 > 0:
            c2 = float(casimir(a, b))
            dim_v = W(a,b).degree()
            total = dim_v * j1
            spec_O0.append((c2, total, a, b))
            decomp_str = ", ".join(f"j={j}x{c}" for j,c in sorted(decomp.items()))
            print(f"({a:2d},{b:2d}) {c2:8.3f} {dim_v:6d} {j1:5d} {total:8d}  {decomp_str}")
        elif decomp:  # has non-zero decomp but no j=1
            c2 = float(casimir(a, b))
            dim_v = W(a,b).degree()
            decomp_str = ", ".join(f"j={j}x{c}" for j,c in sorted(decomp.items()))
            print(f"({a:2d},{b:2d}) {c2:8.3f} {dim_v:6d}     0        0  {decomp_str} [NO FUND]")


print("\n\n=== box_1 on O(2): charge = +1 ===")
print(f"{'(a,b)':>8} {'C2':>8} {'dim':>6} {'br_j1':>5} {'tot_mult':>8} {'SU2 decomp'}")

spec_O2 = []
for s in range(1, 20):
    for a in range(s+1):
        b = s - a
        # For charge +1: need m1 + 2m2 = 3 in the weight
        # Necessary condition: see below
        decomp = su2_branching_at_charge(a, b, QQ(1))
        j1 = decomp.get(1, 0)
        if j1 > 0:
            c2 = float(casimir(a, b))
            dim_v = W(a,b).degree()
            total = dim_v * j1
            spec_O2.append((c2, total, a, b))
            decomp_str = ", ".join(f"j={j}x{c}" for j,c in sorted(decomp.items()))
            print(f"({a:2d},{b:2d}) {c2:8.3f} {dim_v:6d} {j1:5d} {total:8d}  {decomp_str}")


# Group and display
print("\n\n=== GROUPED EIGENVALUES: O(0) ===")
ev_O0 = defaultdict(int)
for c2, total, a, b in spec_O0:
    ev_O0[c2] += total

print(f"{'n':>3} {'lambda':>10} {'mult':>10}")
for i, (lam, mult) in enumerate(sorted(ev_O0.items())[:25]):
    print(f"{i:3d} {lam:10.4f} {mult:10d}")


print("\n\n=== GROUPED EIGENVALUES: O(2) ===")
ev_O2 = defaultdict(int)
for c2, total, a, b in spec_O2:
    ev_O2[c2] += total

print(f"{'n':>3} {'lambda':>10} {'mult':>10}")
for i, (lam, mult) in enumerate(sorted(ev_O2.items())[:25]):
    print(f"{i:3d} {lam:10.4f} {mult:10d}")


# Pattern analysis: try to find closed form for eigenvalues/multiplicities
print("\n\n=== PATTERN ANALYSIS ===")
sorted_O0 = sorted(ev_O0.items())
print("\nO(0) (0,1)-forms: trying lambda = f(n)")
for i, (lam, mult) in enumerate(sorted_O0[:15]):
    # Is lambda = n(n+2) + shift?
    # Is lambda = C2(a,b) for specific (a,b)?
    print(f"  n={i}: lambda={lam:.4f}, mult={mult}")

sorted_O2 = sorted(ev_O2.items())
print("\nO(2) (0,1)-forms: trying lambda = f(n)")
for i, (lam, mult) in enumerate(sorted_O2[:15]):
    print(f"  n={i}: lambda={lam:.4f}, mult={mult}")

# Check: do the eigenvalues correspond to a simple formula?
print("\n\nO(0) eigenvalue gaps:")
for i in range(min(len(sorted_O0)-1, 15)):
    gap = sorted_O0[i+1][0] - sorted_O0[i][0]
    print(f"  gap[{i}→{i+1}] = {gap:.4f}")

print("\nO(2) eigenvalue gaps:")
for i in range(min(len(sorted_O2)-1, 15)):
    gap = sorted_O2[i+1][0] - sorted_O2[i][0]
    print(f"  gap[{i}→{i+1}] = {gap:.4f}")
