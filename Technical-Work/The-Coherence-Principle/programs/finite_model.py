"""
FINITE MODEL of A2.4 (posetal fragment) — Program 7.1, first discharge.
Carrier Y with dynamics f; invariant carrier X ⊆ Y (f(X)⊆X).
'Views at X'  P = all subsets of X            (streams-as-vantage-content)
'Wholes'      Q = f-invariant subsets of Y     (streams-as-closed-systems)
lift  ι(A) = forward closure of A in Y  (the role A plays in the whole)
restrict κ(B) = B ∩ X                   (the whole, seen at X's carrier)
Claims to verify exhaustively: Galois connection (Hom-bijection, thin case),
triangle identities, κι a closure operator (unit = context-gap, Anchor §1.0.3),
ικ a kernel operator (counit = projection-loss), γ-equivariance of ι.
"""
from itertools import chain, combinations
Y = list(range(8))
f = {0:1, 1:2, 2:2, 3:4, 4:2, 5:6, 6:5, 7:7}   # chain->fixpoint, feeder, 2-cycle, isolate
X = {0,1,2}
assert all(f[x] in X for x in X), "X must be f-invariant"

def closure(A):                       # smallest f-invariant superset
    A = set(A); frontier = set(A)
    while frontier:
        nxt = {f[a] for a in frontier} - A
        A |= nxt; frontier = nxt
    return frozenset(A)

def powerset(S): 
    S=list(S); return [frozenset(c) for r in range(len(S)+1) for c in combinations(S,r)]

P = powerset(X)
Q = [B for B in powerset(Y) if all(f[b] in B for b in B)]
i = lambda A: closure(A)              # ι : P -> Q
k = lambda B: frozenset(B & X)        # κ : Q -> P

# 1. Well-typedness
assert all(i(A) in Q for A in P) and all(k(B) in P for B in Q)
# 2. Monotonicity
mono = all(not A1<=A2 or i(A1)<=i(A2) for A1 in P for A2 in P) and \
       all(not B1<=B2 or k(B1)<=k(B2) for B1 in Q for B2 in Q)
# 3. Galois / Hom-bijection (thin): ι(A) ⊆ B  ⟺  A ⊆ κ(B), ALL pairs
galois = all((i(A)<=B) == (A<=k(B)) for A in P for B in Q)
# 4. Triangle identities: ικι = ι ; κικ = κ
tri = all(i(k(i(A)))==i(A) for A in P) and all(k(i(k(B)))==k(B) for B in Q)
# 5. κι closure operator on P: extensive, monotone, idempotent
c = lambda A: k(i(A))
clos = all(A<=c(A) for A in P) and all(c(c(A))==c(A) for A in P)
# 6. ικ kernel operator on Q: deflationary, idempotent
ker = lambda B: i(k(B))
kern = all(ker(B)<=B for B in Q) and all(ker(ker(B))==ker(B) for B in Q)
# 7. γ-equivariance: ι commutes with dynamics (f[ι(A)] ⊆ ι(A) ⊇ closure of f[A])
gamma = all(closure({f[a] for a in A}) <= i(A) for A in P)
# 8. Nontrivial unit & counit witnesses (the Anchor §1.0.3 'measurable gap')
unit_wit  = [(set(A), set(c(A))) for A in P if c(A)!=A][:2]
coun_wit  = [(set(B), set(ker(B))) for B in Q if ker(B)!=B][:2]

print(f"|P|={len(P)} views, |Q|={len(Q)} wholes; pairs checked={len(P)*len(Q)}")
print(f"monotone={mono}  GALOIS(Hom-bijection)={galois}  triangles={tri}")
print(f"κι closure-op={clos}  ικ kernel-op={kern}  γ-equivariant={gamma}")
print(f"η≠id witnesses (stream-in-context ⊋ stream-alone): {unit_wit}")
print(f"ε≠id witnesses (whole ⊋ its X-visible closure):    {coun_wit}")
print("VERDICT:", "A2.4 posetal fragment INSTANTIATED — model exists" if all([mono,galois,tri,clos,kern,gamma]) else "FAILURE")
