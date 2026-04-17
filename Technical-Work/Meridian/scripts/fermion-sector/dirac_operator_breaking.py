"""
DIRAC OPERATOR S_3 BREAKING CALCULATION
=========================================
Phase 26B: Does the internal Dirac operator D_F on the octonionic spectral
triple, constrained by NCG axioms on a warped RS_1 orbifold, break S_3
and determine the fermion bulk mass parameters?

The basin_determination.py found 5 null directions. All trace to S_3
degeneracy -- generations 1,2 are stuck in a doublet. Kinematic
eigenspace projections are S_3-invariant at leading order.

THIS calculation asks: does the DYNAMICS (Dirac operator D_F) break
S_3 through the octonionic first-order condition, where non-associativity
enters generation-dependently through the associator?

The key equation:
    [[D_F, L_{e_i}], R_{e_j}] = 0   (first-order condition)

For non-associative O, L_{e_i} L_{e_j} != L_{e_i e_j}, and the
deviation IS the associator. Different complex structures J_a see
different associator contributions -> generation-dependent constraints
on D_F -> S_3 breaking.

Clayton + Clawd, April 2, 2026
"""

import numpy as np
from scipy.optimize import minimize, differential_evolution
from scipy.linalg import svd, expm
from itertools import permutations, combinations
import warnings
warnings.filterwarnings('ignore')

print("=" * 72)
print("D_F ON THE OCTONIONIC SPECTRAL TRIPLE: S_3 BREAKING CALCULATION")
print("=" * 72)

# ============================================================
# STAGE 1: OCTONIONIC ALGEBRA (from basin_determination.py)
# ============================================================

print("\n--- STAGE 1: Octonionic Algebra Infrastructure ---\n")

# Fano plane triples (defines octonion multiplication)
FANO_TRIPLES = [
    (1, 2, 3), (1, 4, 5), (1, 7, 6),
    (2, 4, 6), (2, 5, 7), (3, 4, 7), (3, 6, 5)
]

def build_mult_table():
    """Build 8x8 octonion multiplication table from Fano plane."""
    table = np.zeros((8, 8), dtype=int)
    sign = np.zeros((8, 8), dtype=int)
    for i in range(8):
        table[0, i] = i; table[i, 0] = i
        sign[0, i] = 1;  sign[i, 0] = 1
    for i in range(1, 8):
        table[i, i] = 0; sign[i, i] = -1
    for a, b, c in FANO_TRIPLES:
        table[a, b] = c; sign[a, b] = 1
        table[b, c] = a; sign[b, c] = 1
        table[c, a] = b; sign[c, a] = 1
        table[b, a] = c; sign[b, a] = -1
        table[c, b] = a; sign[c, b] = -1
        table[a, c] = b; sign[a, c] = -1
    return table, sign

MULT_TABLE, MULT_SIGN = build_mult_table()

def oct_mult(a, b):
    """Multiply two octonions (8-component real vectors)."""
    result = np.zeros(8)
    for i in range(8):
        for j in range(8):
            k = MULT_TABLE[i, j]
            s = MULT_SIGN[i, j]
            result[k] += s * a[i] * b[j]
    return result

def left_mult_matrix(idx):
    """8x8 matrix for LEFT multiplication by e_idx: L_{e_idx}(x) = e_idx * x."""
    L = np.zeros((8, 8))
    for i in range(8):
        ei = np.zeros(8); ei[i] = 1.0
        eidx = np.zeros(8); eidx[idx] = 1.0
        prod = oct_mult(eidx, ei)  # e_idx * e_i
        L[:, i] = prod
    return L

def right_mult_matrix(idx):
    """8x8 matrix for RIGHT multiplication by e_idx: R_{e_idx}(x) = x * e_idx."""
    R = np.zeros((8, 8))
    for i in range(8):
        ei = np.zeros(8); ei[i] = 1.0
        eidx = np.zeros(8); eidx[idx] = 1.0
        prod = oct_mult(ei, eidx)  # e_i * e_idx
        R[:, i] = prod
    return R

# Build all left and right multiplication matrices
L = [left_mult_matrix(i) for i in range(8)]
R = [right_mult_matrix(i) for i in range(8)]

# Complex structures J_1, J_2, J_4 (right multiplication by e_1, e_2, e_4)
J1 = right_mult_matrix(1)
J2 = right_mult_matrix(2)
J4 = right_mult_matrix(4)
Js = [J1, J2, J4]
gen_labels = ['J1 (gen 1)', 'J2 (gen 2)', 'J4 (gen 3)']

# Verify J_a^2 = -Id
for name, J in zip(['J1', 'J2', 'J4'], Js):
    err = np.max(np.abs(J @ J + np.eye(8)))
    print(f"  {name}^2 + I = 0: error = {err:.2e}")

# M_oct from basin_determination
def compute_M_oct():
    M = np.zeros((3, 3))
    for a in range(3):
        for b in range(3):
            M[a, b] = (8.0 - np.trace(Js[a] @ Js[b])) / 16.0
    return M

M_oct = compute_M_oct()
evals_M = np.sort(np.linalg.eigvalsh(M_oct))
print(f"\n  M_oct eigenvalues: {evals_M}")
print(f"  Ratio: {evals_M[0]:.1f} : {evals_M[1]:.1f} : {evals_M[2]:.1f}")

# ============================================================
# STAGE 2: ASSOCIATOR TENSOR
# ============================================================

print("\n--- STAGE 2: Associator Tensor ---\n")

# The associator [a, b, c] = (ab)c - a(bc) for basis elements
# As matrices: [e_i, e_j, *] = L_{e_i} L_{e_j} - L_{e_i e_j}
# This is an 8x8 matrix for each (i,j) pair

def associator_map(i, j):
    """
    Compute the associator map [e_i, e_j, *]: O -> O
    as an 8x8 matrix. Acting on e_k gives [e_i, e_j, e_k].
    """
    # L_{e_i} L_{e_j} - L_{e_i * e_j}
    LiLj = L[i] @ L[j]
    # e_i * e_j
    ei = np.zeros(8); ei[i] = 1.0
    ej = np.zeros(8); ej[j] = 1.0
    eij = oct_mult(ei, ej)
    # L_{e_i * e_j} = sum_k eij[k] * L_k
    L_eij = sum(eij[k] * L[k] for k in range(8))
    return LiLj - L_eij

# Compute the full associator tensor A[i,j,k,l]:
# [e_i, e_j, e_k] = sum_l A[i,j,k,l] * e_l
A_tensor = np.zeros((8, 8, 8, 8))
for i in range(8):
    for j in range(8):
        A_map = associator_map(i, j)
        for k in range(8):
            ek = np.zeros(8); ek[k] = 1.0
            result = A_map @ ek
            A_tensor[i, j, k, :] = result

# Verify: associator is zero when any index is 0 (e_0 = 1 is associative)
assoc_with_1 = np.max(np.abs(A_tensor[0, :, :, :]))
print(f"  Associator involving e_0: max = {assoc_with_1:.2e} (should be 0)")

# Verify: [e_1, e_2, e_4] = 2*e_7 (the canonical non-associativity)
e1, e2, e4 = np.zeros(8), np.zeros(8), np.zeros(8)
e1[1] = 1; e2[2] = 1; e4[4] = 1
assoc_124 = oct_mult(oct_mult(e1, e2), e4) - oct_mult(e1, oct_mult(e2, e4))
print(f"  [e1, e2, e4] = {assoc_124}  (should be 2*e7)")

# Compute total associator magnitude for each complex structure
# This measures how much non-associativity each generation "sees"
print("\n  Associator profile per complex structure:")
gen_indices = [1, 2, 4]  # e_1, e_2, e_4 define the three complex structures

for a, (idx_a, label) in enumerate(zip(gen_indices, gen_labels)):
    # Total associator norm: sum over all pairs (i,j) involving idx_a
    total_norm = 0.0
    for i in range(1, 8):
        for j in range(1, 8):
            A_ij = associator_map(i, j)
            # Project onto the eigenspaces of J_a
            ea = np.zeros(8); ea[idx_a] = 1.0
            # [e_i, e_j, e_a]
            assoc_ija = A_tensor[i, j, idx_a, :]
            total_norm += np.dot(assoc_ija, assoc_ija)
    print(f"    {label}: ||[*, *, e_{idx_a}]||^2 = {total_norm:.4f}")

# ============================================================
# STAGE 3: FIRST-ORDER CONDITION ON NON-ASSOCIATIVE ALGEBRA
# ============================================================

print("\n--- STAGE 3: First-Order Condition Analysis ---\n")

# The NCG first-order condition: [[D, a], b^o] = 0 for all a, b in A
# where b^o acts from the opposite side.
#
# For A = O (octonions):
#   a acts by LEFT multiplication: pi(a) = L_a
#   b^o acts by RIGHT multiplication: pi^o(b) = R_b
#
# The condition becomes:
#   [D L_{e_i} - L_{e_i} D, R_{e_j}] = 0  for all i, j
# i.e.
#   (D L_i - L_i D) R_j = R_j (D L_i - L_i D)
#
# For associative algebras, [L_i, R_j] = 0 always, and this is
# relatively mild. For octonions, [L_i, R_j] != 0 in general,
# and the deviation is the associator.
#
# Key identity for octonions:
#   L_i R_j - R_j L_i = [e_i, *, e_j] (the associator map)
#
# This means the first-order condition has EXTRA terms from the
# associator that don't appear in associative NCG.

# The Hilbert space: We work in the "finite" part.
# For the Standard Model NCG, H_F has dimension 96 (per generation, after
# doubling). For our octonionic version, we consider the generation space
# explicitly.
#
# Minimal model: H_F = C^3_gen x C^2_{L,R} x C^N_internal
# where C^3_gen carries the S_3 representation from M_oct.
#
# D_F in the generation space is a 3x3 matrix (one block for each L-R sector).
# The first-order condition constrains this 3x3 matrix.

# Compute the commutator [L_i, R_j] for all imaginary units
print("  Commutator [L_i, R_j] analysis (= associator map):")
comm_norms = np.zeros((8, 8))
for i in range(1, 8):
    for j in range(1, 8):
        comm = L[i] @ R[j] - R[j] @ L[i]
        comm_norms[i, j] = np.linalg.norm(comm, 'fro')

n_nonzero_comm = np.count_nonzero(comm_norms > 1e-10)
print(f"  Non-zero [L_i, R_j] commutators: {n_nonzero_comm} (of 49 imaginary pairs)")

# The first-order condition on D_F in the generation space.
#
# D_F acts on H_F = O_L + O_R (left and right "particles").
# In the generation basis {J_1, J_2, J_4}, D_F is a 3x3 matrix D_ab
# mapping generation b (right) to generation a (left).
#
# The first-order condition projected onto generation space:
#   For each i, j in {1,...,7}:
#     sum_c D_ac [L_i, R_j]_{cb} = sum_c [L_i, R_j]_{ac} D_cb
#
# where [L_i, R_j]_{ab} is the commutator projected onto the generation
# subspace spanned by the complex structures.
#
# This becomes: D * C_ij = C_ij * D (D commutes with all projected commutators)
# where C_ij is the 3x3 matrix of [L_i, R_j] in the generation basis.

# Project [L_i, R_j] onto the generation subspace
# The generation basis vectors in O = R^8 are defined by the
# complex structure eigenvectors.

# For each J_a, the +i eigenspace of J_a (as a complex structure on R^8)
# gives a 4-dimensional real subspace (2-dimensional complex).
# The generation index labels WHICH complex structure is used.
#
# A cleaner approach: project onto the 3D space spanned by
# {e_1, e_2, e_4} (the complex structure generators themselves).

# Generation basis vectors in R^8
gen_basis = np.zeros((3, 8))
gen_basis[0, 1] = 1.0  # e_1 -> generation 1
gen_basis[1, 2] = 1.0  # e_2 -> generation 2
gen_basis[2, 4] = 1.0  # e_4 -> generation 3

# Project 8x8 matrices onto 3x3 generation space
def project_to_gen(M8):
    """Project an 8x8 matrix onto the 3x3 generation subspace."""
    return gen_basis @ M8 @ gen_basis.T

# Compute all projected commutators C_ij
print("\n  Projected commutators [L_i, R_j] in generation space:")
C_matrices = {}
n_nontrivial = 0
for i in range(1, 8):
    for j in range(1, 8):
        comm = L[i] @ R[j] - R[j] @ L[i]
        C_ij = project_to_gen(comm)
        C_matrices[(i, j)] = C_ij
        if np.linalg.norm(C_ij) > 1e-10:
            n_nontrivial += 1

print(f"  Non-trivial projected commutators: {n_nontrivial} (of 49)")

# Show the first few non-trivial ones
count = 0
for (i, j), C in C_matrices.items():
    if np.linalg.norm(C) > 1e-10 and count < 5:
        print(f"\n    C[{i},{j}] =")
        for row in C:
            print(f"      [{row[0]:+.4f}  {row[1]:+.4f}  {row[2]:+.4f}]")
        count += 1

# ============================================================
# STAGE 4: CONSTRAINT EXTRACTION
# ============================================================

print("\n\n--- STAGE 4: First-Order Condition Constraints on D_F ---\n")

# The first-order condition says: D * C_ij = C_ij * D for all (i,j)
# where D is the 3x3 generation-space Dirac operator.
#
# This is a set of linear constraints on the 9 entries of D.
# We vectorize: d = vec(D) (9-component vector)
# Each C_ij gives the constraint: (C_ij^T kron I - I kron C_ij) d = 0
# i.e., [C_ij, D] = 0 in matrix form.
#
# Stack all constraints and find the null space.

# Build the constraint matrix
constraint_rows = []
for (i, j), C in C_matrices.items():
    if np.linalg.norm(C) > 1e-10:
        # [C, D] = 0 means CD - DC = 0
        # vec(CD) = (I kron C) vec(D)
        # vec(DC) = (C^T kron I) vec(D)
        # So: (I kron C - C^T kron I) vec(D) = 0
        constraint = np.kron(np.eye(3), C) - np.kron(C.T, np.eye(3))
        # Each constraint is 9x9; we add all rows
        for row in constraint:
            if np.linalg.norm(row) > 1e-12:
                constraint_rows.append(row)

if len(constraint_rows) == 0:
    print("  WARNING: No non-trivial constraints! First-order condition is vacuous.")
    print("  This means D_F is UNCONSTRAINED in the generation space.")
    A_constraint = np.zeros((1, 9))
else:
    A_constraint = np.array(constraint_rows)
    print(f"  Constraint matrix: {A_constraint.shape[0]} rows x 9 columns")

    # SVD to find the null space
    U_c, S_c, Vh_c = svd(A_constraint)
    print(f"  Singular values of constraint matrix:")
    for k, s in enumerate(S_c):
        print(f"    sigma_{k+1} = {s:.6f}  {'[ACTIVE]' if s > 1e-6 else '[NULL]'}")

    n_active = np.sum(S_c > 1e-6)
    n_null_D = 9 - n_active
    print(f"\n  Active constraints: {n_active}")
    print(f"  Null space dimension: {n_null_D}")
    print(f"  D_F has {n_null_D} free parameter(s) in generation space")

    # Extract null space basis
    D_null_basis = []
    for k in range(n_null_D):
        v = Vh_c[8 - k, :]  # Last rows of Vh are null space
        D_mat = v.reshape(3, 3)
        D_null_basis.append(D_mat)
        print(f"\n  Null space basis element {k+1} (as 3x3 matrix):")
        for row in D_mat:
            print(f"    [{row[0]:+.6f}  {row[1]:+.6f}  {row[2]:+.6f}]")
        # Check S_3 properties
        # S_3 invariant means P D P^T = D for all permutation matrices P
        is_s3_inv = True
        for p in permutations([0, 1, 2]):
            P = np.eye(3)[list(p), :]
            D_perm = P @ D_mat @ P.T
            if not np.allclose(D_perm, D_mat, atol=1e-6):
                is_s3_inv = False
                break
        print(f"    S_3-invariant: {is_s3_inv}")

        # Check if diagonal
        off_diag = np.max(np.abs(D_mat - np.diag(np.diag(D_mat))))
        print(f"    Off-diagonal norm: {off_diag:.6f}")

        # Eigenvalues
        evals_D = np.linalg.eigvalsh((D_mat + D_mat.T) / 2)
        print(f"    Eigenvalues (symmetric part): {evals_D}")

# ============================================================
# STAGE 5: EXTENDED FIRST-ORDER CONDITION WITH EIGENSPACE PROJECTIONS
# ============================================================

print("\n\n--- STAGE 5: Extended Analysis with Full Eigenspace Projections ---\n")

# The generation basis {e_1, e_2, e_4} is too restrictive.
# Each complex structure J_a defines a full 4D eigenspace in R^8.
# The generation should be identified with the ENTIRE eigenspace,
# not just the generator.
#
# +i eigenspace of J_a: the 4D subspace where J_a acts as +i
# (i.e., vectors v with J_a v = v in the complex sense, or
# the -1 eigenspace of J_a^2 = -I restricted to appropriate subspace)
#
# Since J_a^2 = -I on all of R^8, the eigenvalues of J_a are +/-i,
# each with multiplicity 4 (as a complex structure on R^8).

# Compute projection onto +i eigenspace of J_a
# J_a has eigenvalues +i (mult 4) and -i (mult 4) over C
# The projector onto +i eigenspace is P_a = (I - i*J_a)/2 (complex)
# Over R, the +i eigenspace is a 4D real subspace.

for a, (J, label) in enumerate(zip(Js, gen_labels)):
    evals_J = np.linalg.eigvals(J)
    print(f"  {label}: eigenvalues of J = {np.sort_complex(evals_J)}")

# Complex projectors
P_plus = [(np.eye(8) - 1j * J) / 2.0 for J in Js]
P_minus = [(np.eye(8) + 1j * J) / 2.0 for J in Js]

# Check orthogonality: are the +i eigenspaces of different J_a orthogonal?
print("\n  Overlap of +i eigenspaces (Tr(P_a^+ * P_b^+)):")
for a in range(3):
    for b in range(3):
        overlap = np.trace(P_plus[a].conj().T @ P_plus[b]).real
        print(f"    <{a+1}|{b+1}> = {overlap:.4f}", end="")
    print()

# The generation subspace for generation a is the +i eigenspace of J_a.
# But these are 4D complex subspaces of C^8, and they OVERLAP.
# The overlap structure IS the M_oct matrix (up to normalization).

# For the extended first-order condition, we need to project onto
# each generation's eigenspace and check how the associator acts
# WITHIN that eigenspace versus ACROSS eigenspaces.

# Compute the associator's action WITHIN each generation's eigenspace
print("\n  Associator action within each generation's eigenspace:")

for a, (Pa, label) in enumerate(zip(P_plus, gen_labels)):
    # Total associator norm projected INTO generation a's eigenspace
    total_within = 0.0
    total_cross = 0.0
    for i in range(1, 8):
        for j in range(1, 8):
            A_ij = associator_map(i, j)
            A_ij_c = A_ij.astype(complex)
            # Project: Pa * A_ij * Pa
            within = Pa @ A_ij_c @ Pa.conj().T
            total_within += np.linalg.norm(within, 'fro')**2
            # Cross: Pa * A_ij * (I - Pa)
            cross = Pa @ A_ij_c @ (np.eye(8) - Pa.conj().T)
            total_cross += np.linalg.norm(cross, 'fro')**2
    print(f"    {label}: within = {total_within:.4f}, cross = {total_cross:.4f}, ratio = {total_within/(total_cross+1e-20):.4f}")

# ============================================================
# STAGE 6: THE FANO-INDUCED D_F
# ============================================================

print("\n\n--- STAGE 6: Fano-Plane-Induced Dirac Operator ---\n")

# The Fano plane defines which triple products are non-zero.
# For each Fano line (a, b, c), the product e_a * e_b = e_c (up to sign).
# This defines a TRILINEAR coupling between generations.
#
# If we identify generations with e_1, e_2, e_4, then the Fano lines
# involving these generators are:
#   (1, 2, 3): e_1 * e_2 = e_3
#   (1, 4, 5): e_1 * e_4 = e_5
#   (2, 4, 6): e_2 * e_4 = e_6
#
# The REMAINING Fano lines connect the "other" imaginary units:
#   (1, 7, 6): e_1 * e_7 = -e_6 (sign from Fano orientation)
#   (2, 5, 7): e_2 * e_5 = e_7
#   (3, 4, 7): e_3 * e_4 = e_7
#   (3, 6, 5): e_3 * e_6 = e_5
#
# The generation-generation couplings through the algebra are:
#   gen1-gen2: through e_3 (their product)
#   gen1-gen3: through e_5 (their product)
#   gen2-gen3: through e_6 (their product)
#
# These intermediary units {e_3, e_5, e_6} are the "mediators".
# The KEY insight: the mediators are NOT equivalent under S_3.
# e_3, e_5, e_6 connect to different Fano lines involving e_7.
#
# e_7 is the ASSOCIATOR direction: [e_1, e_2, e_4] = 2*e_7
# This is the preferred direction that the non-associativity picks out.

# Build the Fano-induced coupling matrix
# D_F^{Fano}_{ab} = strength of Fano-mediated coupling between gen a and gen b
# through the associator direction e_7.

# For each generation pair (a, b), the mediator is m = e_a * e_b.
# The coupling to e_7 is: e_m * e_7 or e_7 * e_m
# The strength is |[e_a, e_b, e_7]| -- how much non-associativity
# the pair (a, b) exhibits when probed by the associator direction.

print("  Generation mediators and associator couplings:")

gen_idx = [1, 2, 4]
mediator_map = {}
D_Fano = np.zeros((3, 3))

for a in range(3):
    for b in range(3):
        if a == b:
            # Self-coupling: e_a * e_a = -1 (no imaginary mediator)
            # But the associator [e_a, e_a, *] = 0 (alternating)
            D_Fano[a, a] = 0.0
        else:
            # Product e_a * e_b
            ea = np.zeros(8); ea[gen_idx[a]] = 1.0
            eb = np.zeros(8); eb[gen_idx[b]] = 1.0
            prod = oct_mult(ea, eb)
            mediator = np.argmax(np.abs(prod))
            med_sign = np.sign(prod[mediator])

            # Associator coupling: [e_a, e_b, e_7]
            e7 = np.zeros(8); e7[7] = 1.0
            assoc = oct_mult(oct_mult(ea, eb), e7) - oct_mult(ea, oct_mult(eb, e7))
            assoc_norm = np.linalg.norm(assoc)

            # Also: what direction does the associator point?
            if assoc_norm > 1e-10:
                assoc_dir = assoc / assoc_norm
                assoc_component = np.argmax(np.abs(assoc_dir))
            else:
                assoc_component = -1

            D_Fano[a, b] = assoc_norm * med_sign
            mediator_map[(a, b)] = (mediator, med_sign, assoc_norm, assoc_component)

            print(f"    gen{a+1} x gen{b+1}: mediator = e_{mediator} "
                  f"(sign={med_sign:+.0f}), "
                  f"||[e_{gen_idx[a]}, e_{gen_idx[b]}, e_7]|| = {assoc_norm:.4f}, "
                  f"direction = e_{assoc_component}")

print(f"\n  Fano-induced D_F (off-diagonal from associator):")
for row in D_Fano:
    print(f"    [{row[0]:+.4f}  {row[1]:+.4f}  {row[2]:+.4f}]")

evals_Fano = np.linalg.eigvalsh((D_Fano + D_Fano.T) / 2)
print(f"  Eigenvalues: {evals_Fano}")

# Check S_3 invariance of D_Fano
is_s3 = True
for p in permutations([0, 1, 2]):
    P = np.eye(3)[list(p), :]
    if not np.allclose(P @ D_Fano @ P.T, D_Fano, atol=1e-6):
        is_s3 = False
        break
print(f"  S_3-invariant: {is_s3}")

# ============================================================
# STAGE 7: FULL ASSOCIATOR-DEPENDENT D_F
# ============================================================

print("\n\n--- STAGE 7: Full Associator-Dependent D_F Construction ---\n")

# The internal Dirac operator D_F on the octonionic spectral triple
# is constrained by:
#   1. Self-adjointness: D_F = D_F^dagger
#   2. First-order condition: [[D_F, L_a], R_b] = 0 for all a, b in O
#   3. Orientability: D_F anticommutes with the grading gamma
#   4. Poincare duality: intersection form is non-degenerate
#
# For the generation sector, D_F is a 3x3 Hermitian matrix.
# The first-order condition (Stage 4) tells us which D_F are allowed.
#
# But we need more: the WARP FACTOR makes D_F position-dependent.
# On the RS_1 orbifold y in [0, pi*r_c]:
#   D_F(y) = e^{k*y} * D_F^0 + delta(y) * D_brane + delta(y - pi*r_c) * D_IR
#
# The key: D_F^0 (bulk contribution) is constrained by the first-order
# condition, but D_brane and D_IR (brane-localized terms) are NOT
# (branes break the NCG axioms).
#
# The S_3 breaking must come from the BRANE terms.
# Specifically: on the IR brane (y = pi*r_c), the Higgs field lives.
# The Higgs coupling to fermions IS the brane Dirac operator.
# Different generations couple differently because their bulk profiles
# have different overlaps with the IR brane.

# The effective 4D Dirac operator:
#   D_F^{4D}_{ab} = D_F^{bulk}_{ab} * I_{ab}^{bulk} + D_F^{IR}_{ab} * f_a(pi*r_c) * f_b(pi*r_c)
#
# where I_{ab}^{bulk} = integral of bulk profiles,
# and f_a(pi*r_c) is generation a's wavefunction at the IR brane.

# The RS zero-mode profiles
ky_c = 37.0

def f_profile(c, y_over_yc, ky_c=37.0):
    """Normalized zero-mode profile at position y/y_c."""
    x = (1.0 - 2.0 * c) * ky_c
    if abs(x) < 1e-10:
        N = np.sqrt(1.0 / ky_c)
    elif x > 500:
        N = np.sqrt(1.0 - 2.0 * c)
    elif x < -500:
        N = np.sqrt(2.0 * c - 1.0)
    else:
        N = np.sqrt(abs((1.0 - 2.0 * c) / (np.exp(x) - 1.0)))
    return N * np.exp((0.5 - c) * ky_c * y_over_yc)

def g_profile(c, ky_c=37.0):
    """Zero-mode overlap with IR-localized Higgs (y = pi*r_c, i.e. y/y_c = 1)."""
    return f_profile(c, 1.0, ky_c)

# Now: if the bulk D_F is S_3-invariant (as the first-order condition demands),
# and the brane D_F is a free matrix, then the S_3 BREAKING comes from the
# different bulk profiles at the IR brane.
#
# The effective mass matrix becomes:
#   M_ij = M_oct_ij * g(c_Li) * g(c_Rj) * Y5 * v/sqrt(2)
#        + D_F^{bulk}_ij * I_{ij}^{bulk}
#
# The bulk term is NEW. It's constrained by the first-order condition.
# If D_F^{bulk} is NOT proportional to identity (i.e., if the null space
# from Stage 4 contains non-trivial S_3-BREAKING elements), then the
# bulk term provides additional structure.

# Let's check: does the null space from Stage 4 contain S_3-BREAKING matrices?
# (Already checked above, but let's be explicit about the physical implications)

print("  Physical interpretation of D_F null space:\n")

if len(constraint_rows) > 0 and n_null_D > 0:
    print(f"  The first-order condition allows {n_null_D} independent D_F matrices.")
    print(f"  Checking which ones break S_3...\n")

    n_s3_breaking = 0
    breaking_matrices = []
    invariant_matrices = []

    for k, D_mat in enumerate(D_null_basis):
        is_s3_inv = True
        for p in permutations([0, 1, 2]):
            P = np.eye(3)[list(p), :]
            if not np.allclose(P @ D_mat @ P.T, D_mat, atol=1e-6):
                is_s3_inv = False
                break
        if is_s3_inv:
            invariant_matrices.append(D_mat)
            print(f"    Basis {k+1}: S_3-INVARIANT")
        else:
            n_s3_breaking += 1
            breaking_matrices.append(D_mat)
            print(f"    Basis {k+1}: S_3-BREAKING  <-- THIS IS WHAT WE NEED")

            # Decompose into S_3 irreps
            # S_3 has irreps: trivial (1D), sign (1D), standard (2D)
            # The symmetric part of D decomposes as:
            #   3x3 symmetric = trivial + standard + ...
            D_sym = (D_mat + D_mat.T) / 2
            # Trivial component: proportional to (1,1,1;1,1,1;1,1,1)/3
            trivial_proj = np.ones((3, 3)) / 3
            trivial_comp = np.trace(trivial_proj @ D_sym) / np.trace(trivial_proj @ trivial_proj)
            D_trivial = trivial_comp * trivial_proj
            D_standard = D_sym - D_trivial
            print(f"      Trivial component norm: {np.linalg.norm(D_trivial):.6f}")
            print(f"      Standard rep norm: {np.linalg.norm(D_standard):.6f}")
            print(f"      Standard rep eigenvalues: {np.sort(np.linalg.eigvalsh(D_standard))}")

    print(f"\n  S_3-breaking D_F matrices: {n_s3_breaking} out of {n_null_D}")

elif len(constraint_rows) == 0:
    print("  First-order condition is VACUOUS on the generation subspace.")
    print("  D_F is completely unconstrained -> all 9 entries are free.")
    print("  This means the first-order condition does NOT operate at the")
    print("  level of the simple {e_1, e_2, e_4} generation basis.")
    print("\n  Proceeding to full eigenspace analysis...")
    n_s3_breaking = 9  # all free
    breaking_matrices = []

# ============================================================
# STAGE 8: FULL EIGENSPACE FIRST-ORDER CONDITION
# ============================================================

print("\n\n--- STAGE 8: Full Eigenspace First-Order Condition ---\n")

# Instead of projecting onto the 3D subspace {e_1, e_2, e_4},
# work in the FULL 8D octonion space.
#
# D_F is an operator on the full Hilbert space H_F.
# For the octonionic SM, H_F = O_L + O_R = R^8 + R^8 = R^16
# (or C^16 after complexification).
#
# D_F has the block structure:
#   D_F = | 0    M  |
#         | M^T  0  |
# where M is an 8x8 real matrix (the mass matrix in octonion space).
#
# The first-order condition in the full space:
#   [[D_F, pi(a)], pi^o(b)] = 0 for all a, b in O
#
# where pi(a) = L_a acts on the LEFT block,
# and pi^o(b) = R_b acts on the RIGHT block.
#
# In block form, the condition becomes:
#   (M * R_b - L_a * M) * something = 0
# More precisely:
#   For the off-diagonal block:
#   M * R_j - L_i * M must commute with L_i, R_j appropriately.
#
# Expanding: the condition for the mass matrix M (8x8) is:
#   L_i * M * R_j - M * R_j * L_i - L_i * R_j * M + R_j * M * L_i = 0
# Hmm, this needs more careful derivation.

# Actually, for the real spectral triple (A, H, D) with A = O:
# H = O + O (left + right chirality)
# pi(a)(x_L, x_R) = (ax_L, ax_R) -- left multiplication on both
# pi^o(b)(x_L, x_R) = (x_L b, x_R b) -- right multiplication on both
# D(x_L, x_R) = (Mx_R, M^T x_L) -- swaps chirality through mass matrix M
#
# The first-order condition [[D, pi(a)], pi^o(b)] = 0 becomes:
# [D, pi(a)] (x_L, x_R) = D(ax_L, ax_R) - pi(a)D(x_L, x_R)
#   = (M(ax_R), M^T(ax_L)) - (a(Mx_R), a(M^T x_L))
#   = ((Ma - aM)x_R, (M^T a - aM^T)x_L)    [using L_a notation]
#   = (([M, L_a])x_R, ([M^T, L_a])x_L)
#
# [D, pi(a)] has blocks:
#   off-diag: [M, L_a] (maps R->L) and [M^T, L_a] (maps L->R)
#
# Then [[D, pi(a)], pi^o(b)] = [[M, L_a], R_b] on the R->L block
# and [[M^T, L_a], R_b] on the L->R block.
#
# So the FULL first-order condition is:
#   [[M, L_a], R_b] = 0  for all a, b in Im(O)
#
# where M is the 8x8 mass matrix.

# Compute constraints on 8x8 mass matrix M
print("  Computing first-order condition on 8x8 mass matrix M...\n")

# For each pair (i, j) of imaginary units:
# [[M, L_i], R_j] = [ML_i - L_i M, R_j]
#   = (ML_i - L_i M)R_j - R_j(ML_i - L_i M)
#   = ML_i R_j - L_i M R_j - R_j M L_i + R_j L_i M
#
# This must be zero for all i,j in {1,...,7}.
# Vectorizing M as a 64-component vector m = vec(M),
# each (i,j) gives a 64x64 constraint matrix.

# Build constraint matrix for vec(M)
constraint_rows_8x8 = []

for i in range(1, 8):
    for j in range(1, 8):
        # [[M, L_i], R_j] = 0
        # = M L_i R_j - L_i M R_j - R_j M L_i + R_j L_i M = 0
        #
        # In vec form: each term is a 64x64 matrix acting on vec(M)
        # vec(AMB) = (B^T kron A) vec(M)
        #
        # Term 1: M L_i R_j -> M (L_i R_j) = M * (L_i R_j)
        #   but M is on the left... vec(M * (L_i R_j)) = ((L_i R_j)^T kron I) vec(M)
        # Wait, we need: for the expression M L_i R_j, this is M * (L_i R_j).
        # No: the expression is [[M, L_i], R_j] which involves commutators.
        # Let me be more careful.
        #
        # Let K_i = L_i, S_j = R_j
        # [M, K_i] = M K_i - K_i M
        # [[M, K_i], S_j] = [M, K_i] S_j - S_j [M, K_i]
        #   = (MK_i - K_iM)S_j - S_j(MK_i - K_iM)
        #   = MK_iS_j - K_iMS_j - S_jMK_i + S_jK_iM
        #
        # vec(MK_iS_j) = (S_j^T K_i^T kron I) vec(M)  -- NO
        # Actually vec(AMB) = (B^T kron A) vec(M)
        # So vec(M * K_i * S_j) -- this is not of form AMB.
        # We need to think of M as the middle:
        #
        # Term 1: M K_i S_j -- M multiplied on right by K_i S_j
        #   = I * M * (K_i S_j) -> vec = ((K_i S_j)^T kron I) vec(M)
        #
        # Term 2: -K_i M S_j -- M multiplied on left by K_i, right by S_j
        #   = K_i * M * S_j -> vec = (S_j^T kron K_i) vec(M)
        #
        # Term 3: -S_j M K_i -- M multiplied on left by S_j, right by K_i
        #   = S_j * M * K_i -> vec = (K_i^T kron S_j) vec(M)
        #
        # Term 4: S_j K_i M -- M multiplied on left by S_j K_i
        #   = (S_j K_i) * M * I -> vec = (I kron S_j K_i) vec(M)

        KiSj = L[i] @ R[j]
        SjKi = R[j] @ L[i]

        T1 = np.kron(KiSj.T, np.eye(8))         # M K_i S_j
        T2 = -np.kron(R[j].T, L[i])              # -K_i M S_j
        T3 = -np.kron(L[i].T, R[j])              # -S_j M K_i
        T4 = np.kron(np.eye(8), SjKi)            # S_j K_i M

        constraint_64 = T1 + T2 + T3 + T4

        # Add non-trivial rows
        for row in constraint_64:
            if np.linalg.norm(row) > 1e-12:
                constraint_rows_8x8.append(row)

A_8x8 = np.array(constraint_rows_8x8)
print(f"  Raw constraint matrix: {A_8x8.shape[0]} rows x 64 columns")

# Remove near-duplicate rows
# Use QR decomposition to find independent constraints
Q, R_qr = np.linalg.qr(A_8x8.T, mode='reduced')
independent_mask = np.abs(np.diag(R_qr)) > 1e-10
n_independent = np.sum(independent_mask)
print(f"  Independent constraints: {n_independent}")

# SVD for null space
U_8, S_8, Vh_8 = svd(A_8x8, full_matrices=True)
# Only look at first 64 singular values
S_64 = S_8[:64] if len(S_8) >= 64 else S_8
print(f"\n  Singular values (first 20 of {len(S_64)}):")
for k in range(min(20, len(S_64))):
    status = "ACTIVE" if S_64[k] > 1e-6 else "NULL"
    print(f"    sigma_{k+1:2d} = {S_64[k]:12.6f}  [{status}]")
if len(S_64) > 20:
    n_more_active = np.sum(S_64[20:] > 1e-6)
    n_more_null = np.sum(S_64[20:] <= 1e-6)
    print(f"    ... {n_more_active} more active, {n_more_null} more null")

n_active_8 = np.sum(S_64 > 1e-6)
n_null_8 = 64 - n_active_8
print(f"\n  RESULT: 8x8 mass matrix M has {n_null_8} free parameters (of 64)")
print(f"  First-order condition eliminates {n_active_8} of 64 entries")

# Extract null space basis matrices
print(f"\n  Analyzing the {n_null_8}-dimensional null space of M...")

null_basis_8 = []
for k in range(n_null_8):
    v = Vh_8[63 - k, :]
    M_mat = v.reshape(8, 8)
    null_basis_8.append(M_mat)

# Check S_3 properties of the null space
# S_3 acts by permuting (J_1, J_2, J_4), which corresponds to
# permuting the imaginary units (e_1 <-> e_2 <-> e_4) and
# correspondingly (e_3 <-> e_6 <-> e_5) [their products] and
# e_7 stays fixed (it's the associator direction).
#
# The S_3 generators in the e-basis:
# sigma = (12): swaps e_1 <-> e_2, e_5 <-> e_6, fixes e_3(?), e_4, e_7
# Actually: need to be more careful about which permutation of
# {e_1, e_2, e_4} -> {e_2, e_1, e_4} maps to which permutation of
# ALL imaginary units.

# Under S_3 = Aut(Fano) acting on complex structures:
# The permutation (J_1, J_2, J_4) -> (J_2, J_1, J_4) corresponds to
# swapping e_1 <-> e_2. The other imaginary units transform to keep
# the Fano triples consistent.
#
# From the Fano triples:
# (1,2,3), (1,4,5), (1,7,6), (2,4,6), (2,5,7), (3,4,7), (3,6,5)
#
# Swap 1<->2:
# (2,1,3) = -(1,2,3) -- e_3 -> -e_3? No, let's think as algebra automorphism.
# phi(e_1) = e_2, phi(e_2) = e_1, phi(e_4) = e_4
# Then: phi(e_1)phi(e_2) = e_2*e_1 = -e_3, so phi(e_3) = -e_3
# phi(e_1)phi(e_4) = e_2*e_4 = e_6, so phi(e_5) = e_6
# phi(e_2)phi(e_4) = e_1*e_4 = e_5, so phi(e_6) = e_5
# phi(e_1)phi(e_7) = e_2*phi(e_7) must equal phi(e_1*e_7) = phi(-e_6) = -e_5
# so e_2*phi(e_7) = -e_5, phi(e_7) = -e_2\(-e_5) ... let me just compute.
# e_1*e_7 = -e_6 (from triple (1,7,6) with sign)
# phi(e_1*e_7) = phi(-e_6) = -e_5
# phi(e_1)*phi(e_7) = e_2*phi(e_7) = -e_5
# e_2*e_7 = e_5 (from triple (2,5,7): e_2*e_5=e_7, so e_2*e_7 = -e_5... wait)
# Let me just compute from the multiplication table.

def s3_matrix_swap12():
    """Build the 8x8 permutation matrix for the S_3 element swapping gen1<->gen2."""
    # phi: e_0 -> e_0, e_1 -> e_2, e_2 -> e_1, e_4 -> e_4
    # Determine the rest by requiring phi is an algebra automorphism
    # phi(ab) = phi(a)phi(b)
    phi = np.zeros(8)
    result = np.zeros((8, 8))
    result[0, 0] = 1  # e_0 -> e_0

    # Start with generators
    # phi(e_1) = e_2, phi(e_2) = e_1, phi(e_4) = e_4
    result[2, 1] = 1  # e_1 -> e_2
    result[1, 2] = 1  # e_2 -> e_1
    result[4, 4] = 1  # e_4 -> e_4

    # e_3 = e_1 * e_2, so phi(e_3) = phi(e_1)*phi(e_2) = e_2*e_1 = -e_3
    e2 = np.zeros(8); e2[2] = 1
    e1 = np.zeros(8); e1[1] = 1
    e2e1 = oct_mult(e2, e1)  # should be -e_3
    result[:, 3] = e2e1

    # e_5 = e_1 * e_4, so phi(e_5) = e_2*e_4
    e4 = np.zeros(8); e4[4] = 1
    e2e4 = oct_mult(e2, e4)  # should be e_6
    result[:, 5] = e2e4

    # e_6 = e_2 * e_4, so phi(e_6) = e_1*e_4 = e_5
    e1e4 = oct_mult(e1, e4)
    result[:, 6] = e1e4

    # e_7: need a triple involving e_7 and known elements
    # e_3 * e_4 = e_7 (from Fano triple (3,4,7))
    # phi(e_7) = phi(e_3)*phi(e_4) = (-e_3)*(e_4)
    e3 = np.zeros(8); e3[3] = 1
    neg_e3_times_e4 = oct_mult(-e3, e4)
    result[:, 7] = neg_e3_times_e4

    return result

P12 = s3_matrix_swap12()
print("\n  S_3 swap (gen1 <-> gen2) matrix P12:")
# Verify it's an algebra automorphism: P12(a*b) = P12(a)*P12(b)
is_auto = True
for i in range(8):
    for j in range(8):
        ei = np.zeros(8); ei[i] = 1
        ej = np.zeros(8); ej[j] = 1
        lhs = P12 @ oct_mult(ei, ej)
        rhs = oct_mult(P12 @ ei, P12 @ ej)
        if not np.allclose(lhs, rhs, atol=1e-10):
            is_auto = False
print(f"  P12 is algebra automorphism: {is_auto}")
print(f"  P12^2 = I: {np.allclose(P12 @ P12, np.eye(8), atol=1e-10)}")

# Check how many null space matrices are S_3-invariant vs breaking
n_inv_8 = 0
n_break_8 = 0
breaking_indices = []

for k in range(min(n_null_8, 30)):  # check first 30
    M_k = null_basis_8[k]
    # S_3 invariance: P12 M P12^T = M (and similarly for other generators)
    M_transformed = P12 @ M_k @ P12.T
    if np.allclose(M_transformed, M_k, atol=1e-6):
        n_inv_8 += 1
    else:
        n_break_8 += 1
        breaking_indices.append(k)

print(f"\n  Of the null space basis (checked {min(n_null_8, 30)}):")
print(f"    S_3-invariant: {n_inv_8}")
print(f"    S_3-BREAKING:  {n_break_8}")

if n_break_8 > 0:
    print(f"\n  *** S_3-BREAKING ELEMENTS FOUND IN THE NULL SPACE ***")
    print(f"  The first-order condition on the non-associative algebra")
    print(f"  ALLOWS mass matrices that break S_3!")
    print(f"\n  Examining the first few breaking matrices:")

    for idx in breaking_indices[:3]:
        M_k = null_basis_8[idx]
        print(f"\n    Null basis element {idx+1}:")
        # Project to generation subspace
        M_gen = gen_basis @ M_k @ gen_basis.T
        print(f"    Generation-space projection:")
        for row in M_gen:
            print(f"      [{row[0]:+.6f}  {row[1]:+.6f}  {row[2]:+.6f}]")

        evals_gen = np.linalg.eigvalsh((M_gen + M_gen.T) / 2)
        print(f"    Eigenvalues: {evals_gen}")

        # How much S_3 breaking?
        M_s3avg = np.zeros((3, 3))
        for p in permutations([0, 1, 2]):
            P = np.eye(3)[list(p), :]
            M_s3avg += P @ M_gen @ P.T
        M_s3avg /= 6
        M_break = M_gen - M_s3avg
        breaking_fraction = np.linalg.norm(M_break) / (np.linalg.norm(M_gen) + 1e-20)
        print(f"    S_3-breaking fraction: {breaking_fraction:.4f}")

# ============================================================
# STAGE 9: RS INTEGRATION WITH S_3-BREAKING D_F
# ============================================================

print("\n\n--- STAGE 9: RS Integration with Breaking D_F ---\n")

# Physical constants
v_EW = 246.0  # GeV

# Observed fermion masses at M_Z (GeV)
m_obs_u = np.array([2.16e-3, 1.27, 172.69])
m_obs_d = np.array([4.67e-3, 93.4e-3, 4.18])
m_obs_e = np.array([0.511e-3, 105.66e-3, 1.777])

# CKM elements
V_obs = {
    'us': 0.2243, 'ub': 0.00382, 'cb': 0.0408,
    'ud': 0.97373, 'cs': 0.975, 'tb': 0.99914
}

# The key question: does the S_3-breaking D_F from the first-order
# condition, combined with the RS warp factor, reproduce the
# fermion mass hierarchy?
#
# If the null space contains S_3-breaking matrices, then we can
# parameterize:
#   M = sum_k alpha_k * M_k^{null}
# where the alpha_k are the free parameters.
#
# The effective 4D mass matrix for sector s (up, down, lepton) is:
#   M^s_{ij} = Y5_s * sum_k alpha_k * (M_k^{null})_{ij} * g(c_i^L) * g(c_j^R) * v/sqrt(2)
#
# With S_3 breaking in M_k^{null}, the generations 1 and 2 are NO LONGER
# degenerate -- even if c_1 = c_2 (S_3 doublet in bulk mass).

# Count parameters in the new framework
print("  Parameter counting with D_F breaking:\n")

if n_break_8 > 0:
    # D_F null space parameters
    n_Df_params = n_null_8  # free coefficients in null space expansion
    # But many of these are redundant with the Yukawa/bulk mass params.
    # The INDEPENDENT new parameters are the S_3-breaking ones.
    n_new_params = n_break_8

    print(f"    D_F null space dimension: {n_null_8}")
    print(f"    S_3-invariant components: {n_inv_8} (absorbed into existing M_oct structure)")
    print(f"    S_3-BREAKING components:  {n_break_8} (NEW physics)")
    print(f"    These provide {n_break_8} new parameters that split gen 1 vs gen 2.")
    print()

    # The original basin_determination found 5 null directions.
    # Those 5 null directions correspond to:
    #   - gen1/gen2 splitting in each of the 5 sectors (Q, u, d, L, e)
    # The S_3-breaking D_F components provide a MECHANISM for this splitting.
    # But do they provide ENOUGH constraints to fill all 5 null directions?

    # Build the combined mass matrix with D_F breaking
    # For a concrete test: use the breaking matrices to fit the data

    # Select the breaking matrices in generation space
    gen_breaking_mats = []
    for idx in breaking_indices[:min(len(breaking_indices), 10)]:
        M_k = null_basis_8[idx]
        M_gen = gen_basis @ M_k @ gen_basis.T
        if np.linalg.norm(M_gen) > 1e-10:
            gen_breaking_mats.append(M_gen / np.linalg.norm(M_gen))

    n_break_gen = len(gen_breaking_mats)
    print(f"    Non-trivial generation-space breaking matrices: {n_break_gen}")

    if n_break_gen > 0:
        print("\n  Running combined fit: M_oct + D_F breaking + RS profiles...\n")

        # Combined mass matrix:
        # M_sector = Y5 * (M_oct + sum_k beta_k * B_k) * g_L x g_R * v/sqrt(2)
        # where B_k are the S_3-breaking matrices in generation space.
        #
        # Parameters: bulk masses (with S_3: c_12, c_3 per sector) + Yukawa + beta_k
        # With S_3 bulk masses: 2*5 = 10 (Q, u, d, L, e each have c_12, c_3)
        # Yukawa scales: 3 (Y5_u, Y5_d, Y5_e)
        # Breaking coefficients: n_break_gen per sector = 3 * n_break_gen
        # Total: 13 + 3*n_break_gen

        # But wait -- the breaking matrices are SHARED across sectors
        # (they come from the algebra, not from the specific fermion).
        # So the beta_k are universal, not per-sector.
        # Total: 13 + n_break_gen

        n_total_params = 13 + min(n_break_gen, 5)  # cap at 5 breaking matrices
        print(f"    Total parameters: 13 (original) + {min(n_break_gen, 5)} (breaking) = {n_total_params}")
        print(f"    Measurements: 15 (9 masses + 6 CKM)")
        print(f"    Degrees of freedom: {15 - n_total_params}")

        def mass_matrix_with_breaking(c_L, c_R, Y5, M_base, betas, break_mats):
            """Mass matrix with S_3-breaking from D_F."""
            g_L = np.array([g_profile(c, ky_c) for c in c_L])
            g_R = np.array([g_profile(c, ky_c) for c in c_R])
            M_eff = M_base.copy()
            for k, (beta, Bk) in enumerate(zip(betas, break_mats)):
                M_eff = M_eff + beta * Bk
            M = Y5 * M_eff * np.outer(g_L, g_R) * v_EW / np.sqrt(2)
            return M

        def diagonalize(M):
            U, s, Vh = svd(M)
            idx = np.argsort(s)
            return s[idx], U[:, idx], Vh[idx, :]

        n_bk = min(n_break_gen, 5)
        break_mats_use = gen_breaking_mats[:n_bk]

        def chi2_combined(params):
            c_Q12, c_Q3, c_u12, c_u3, c_d12, c_d3 = params[:6]
            c_L12, c_L3, c_e12, c_e3 = params[6:10]
            Y5_u, Y5_d, Y5_e = params[10:13]
            betas = params[13:13+n_bk]

            c_Q = [c_Q12, c_Q12, c_Q3]
            c_u = [c_u12, c_u12, c_u3]
            c_d = [c_d12, c_d12, c_d3]
            c_L = [c_L12, c_L12, c_L3]
            c_e = [c_e12, c_e12, c_e3]

            M_u = mass_matrix_with_breaking(c_Q, c_u, Y5_u, M_oct, betas, break_mats_use)
            M_d = mass_matrix_with_breaking(c_Q, c_d, Y5_d, M_oct, betas, break_mats_use)
            M_e = mass_matrix_with_breaking(c_L, c_e, Y5_e, M_oct, betas, break_mats_use)

            m_u_p, U_uL, _ = diagonalize(M_u)
            m_d_p, U_dL, _ = diagonalize(M_d)
            m_e_p, _, _ = diagonalize(M_e)

            V = U_uL.T @ U_dL

            chi2 = 0.0
            for pred, obs in zip(m_u_p, m_obs_u):
                if pred > 0:
                    chi2 += (np.log(pred) - np.log(obs))**2 / 0.1**2
                else:
                    chi2 += 1e6
            for pred, obs in zip(m_d_p, m_obs_d):
                if pred > 0:
                    chi2 += (np.log(pred) - np.log(obs))**2 / 0.1**2
                else:
                    chi2 += 1e6
            for pred, obs in zip(m_e_p, m_obs_e):
                if pred > 0:
                    chi2 += (np.log(pred) - np.log(obs))**2 / 0.1**2
                else:
                    chi2 += 1e6

            for key, val in V_obs.items():
                i, j = {'us': (0,1), 'ub': (0,2), 'cb': (1,2),
                        'ud': (0,0), 'cs': (1,1), 'tb': (2,2)}[key]
                v_pred = abs(V[i, j])
                chi2 += ((v_pred - val) / (0.05 * val))**2

            return chi2

        bounds_combined = [
            (0.3, 0.7), (0.0, 0.5),    # c_Q
            (0.3, 0.75), (0.0, 0.5),   # c_u
            (0.3, 0.7), (0.3, 0.7),    # c_d
            (0.3, 0.75), (0.3, 0.65),  # c_L
            (0.3, 0.75), (0.3, 0.65),  # c_e
            (0.1, 5.0), (0.01, 2.0), (0.01, 2.0),  # Y5
        ] + [(-2.0, 2.0)] * n_bk       # beta_k

        print(f"  Running differential evolution ({13+n_bk} params, pop=30, iter=2000)...")
        result_combined = differential_evolution(
            chi2_combined, bounds_combined,
            seed=42, maxiter=2000, tol=1e-12,
            popsize=30, mutation=(0.5, 1.5), recombination=0.9
        )

        bf_c = result_combined.x
        chi2_c = result_combined.fun
        n_dof_c = 15 - (13 + n_bk)

        print(f"  Optimization: {'SUCCESS' if result_combined.success else 'FAILED'}")
        print(f"  chi^2 = {chi2_c:.4f}, dof = {n_dof_c}, chi^2/dof = {chi2_c/max(n_dof_c,1):.2f}")

        # Extract predictions
        c_Q = [bf_c[0], bf_c[0], bf_c[1]]
        c_u = [bf_c[2], bf_c[2], bf_c[3]]
        c_d = [bf_c[4], bf_c[4], bf_c[5]]
        c_L = [bf_c[6], bf_c[6], bf_c[7]]
        c_e = [bf_c[8], bf_c[8], bf_c[9]]
        betas_bf = bf_c[13:13+n_bk]

        M_u_bf = mass_matrix_with_breaking(c_Q, c_u, bf_c[10], M_oct, betas_bf, break_mats_use)
        M_d_bf = mass_matrix_with_breaking(c_Q, c_d, bf_c[11], M_oct, betas_bf, break_mats_use)
        M_e_bf = mass_matrix_with_breaking(c_L, c_e, bf_c[12], M_oct, betas_bf, break_mats_use)

        m_u_p, U_uL, _ = diagonalize(M_u_bf)
        m_d_p, U_dL, _ = diagonalize(M_d_bf)
        m_e_p, _, _ = diagonalize(M_e_bf)
        V_CKM = U_uL.T @ U_dL

        print(f"\n  MASS PREDICTIONS (with D_F breaking):")
        print(f"  {'Fermion':>8s}  {'Predicted':>12s}  {'Observed':>12s}  {'Ratio':>8s}")
        print(f"  {'-'*46}")
        for name, pred, obs in [
            ('u', m_u_p[0], m_obs_u[0]), ('c', m_u_p[1], m_obs_u[1]), ('t', m_u_p[2], m_obs_u[2]),
            ('d', m_d_p[0], m_obs_d[0]), ('s', m_d_p[1], m_obs_d[1]), ('b', m_d_p[2], m_obs_d[2]),
            ('e', m_e_p[0], m_obs_e[0]), ('mu', m_e_p[1], m_obs_e[1]), ('tau', m_e_p[2], m_obs_e[2])]:
            ratio = pred / obs if obs > 0 else 0
            print(f"  {name:>8s}  {pred:12.4e}  {obs:12.4e}  {ratio:8.4f}")

        print(f"\n  CKM PREDICTIONS:")
        for key, val in V_obs.items():
            i, j = {'us': (0,1), 'ub': (0,2), 'cb': (1,2),
                    'ud': (0,0), 'cs': (1,1), 'tb': (2,2)}[key]
            v_pred = abs(V_CKM[i, j])
            print(f"    V_{key:>5s} = {v_pred:.5f}  (obs: {val:.5f})")

        print(f"\n  Breaking coefficients: {betas_bf}")

        # NULL SPACE ANALYSIS of the combined model
        print(f"\n  Null space analysis of combined model...")

        def compute_obs_combined(params):
            (c_Q12, c_Q3, c_u12, c_u3, c_d12, c_d3,
             c_L12, c_L3, c_e12, c_e3,
             Y5_u, Y5_d, Y5_e) = params[:13]
            betas = params[13:13+n_bk]

            c_Q = [c_Q12, c_Q12, c_Q3]
            c_u = [c_u12, c_u12, c_u3]
            c_d = [c_d12, c_d12, c_d3]
            c_L = [c_L12, c_L12, c_L3]
            c_e = [c_e12, c_e12, c_e3]

            M_u = mass_matrix_with_breaking(c_Q, c_u, Y5_u, M_oct, betas, break_mats_use)
            M_d = mass_matrix_with_breaking(c_Q, c_d, Y5_d, M_oct, betas, break_mats_use)
            M_e = mass_matrix_with_breaking(c_L, c_e, Y5_e, M_oct, betas, break_mats_use)

            m_u_p, U_uL, _ = diagonalize(M_u)
            m_d_p, U_dL, _ = diagonalize(M_d)
            m_e_p, _, _ = diagonalize(M_e)
            V = U_uL.T @ U_dL

            obs = np.concatenate([
                np.log(np.maximum(m_u_p, 1e-20)),
                np.log(np.maximum(m_d_p, 1e-20)),
                np.log(np.maximum(m_e_p, 1e-20)),
                [abs(V[0,1]), abs(V[0,2]), abs(V[1,2]),
                 abs(V[0,0]), abs(V[1,1]), abs(V[2,2])]
            ])
            return obs

        eps = 1e-6
        obs_0c = compute_obs_combined(bf_c)
        n_obs_c = len(obs_0c)
        n_par_c = 13 + n_bk
        J_c = np.zeros((n_obs_c, n_par_c))

        for j in range(n_par_c):
            p_plus = bf_c.copy(); p_plus[j] += eps
            p_minus = bf_c.copy(); p_minus[j] -= eps
            J_c[:, j] = (compute_obs_combined(p_plus) - compute_obs_combined(p_minus)) / (2*eps)

        _, S_Jc, Vh_Jc = svd(J_c)
        print(f"\n  Jacobian: {n_obs_c} observables x {n_par_c} parameters")
        print(f"  Singular values:")
        for k, s in enumerate(S_Jc):
            status = "CONSTRAINED" if s > 1e-3 else "NULL"
            print(f"    sigma_{k+1:2d} = {s:12.6f}  [{status}]")

        n_constrained_c = np.sum(S_Jc > 1e-3)
        n_null_c = n_par_c - n_constrained_c
        print(f"\n  Constrained directions: {n_constrained_c}")
        print(f"  NULL directions: {n_null_c}")

        if n_null_c > 0:
            print(f"\n  Null directions (unconstrained combinations):")
            labels_c = ['c_Q12', 'c_Q3', 'c_u12', 'c_u3', 'c_d12', 'c_d3',
                        'c_L12', 'c_L3', 'c_e12', 'c_e3', 'Y5_u', 'Y5_d', 'Y5_e']
            labels_c += [f'beta_{k+1}' for k in range(n_bk)]
            for i in range(n_null_c):
                idx = n_par_c - 1 - i
                direction = Vh_Jc[idx, :]
                print(f"    Null {i+1}: sigma = {S_Jc[idx]:.2e}")
                components = [(labels_c[j], direction[j]) for j in range(n_par_c) if abs(direction[j]) > 0.1]
                for lab, val in sorted(components, key=lambda x: -abs(x[1])):
                    print(f"      {lab:>10s}: {val:+.4f}")
else:
    n_break_gen = 0

# ============================================================
# STAGE 10: VERDICT
# ============================================================

print("\n\n" + "=" * 72)
print("VERDICT: DOES D_F BREAK S_3 AND DETERMINE THE BASIN?")
print("=" * 72)

print(f"""
SUMMARY OF FINDINGS
====================

1. ASSOCIATOR TENSOR:
   - Fully computed from Fano plane, 7^4 = 2401 components
   - Non-zero when all indices are imaginary (e_1 through e_7)
   - [e_1, e_2, e_4] = 2*e_7 (canonical non-associativity)

2. FIRST-ORDER CONDITION ON GENERATION SUBSPACE (3x3):
   - Projected commutators [L_i, R_j] onto {{e_1, e_2, e_4}}: {n_nontrivial} non-trivial
   - Null space dimension of D_F: {n_null_D if len(constraint_rows) > 0 else 'UNCONSTRAINED'}

3. FIRST-ORDER CONDITION ON FULL OCTONION SPACE (8x8):
   - 64 entries in mass matrix M
   - Active constraints: {n_active_8}, Null space: {n_null_8}
   - S_3-invariant null vectors: {n_inv_8}
   - S_3-BREAKING null vectors: {n_break_8}
""")

if n_break_8 > 0:
    print(f"""4. THE KEY RESULT:
   The first-order condition [[M, L_a], R_b] = 0 on the octonions
   DOES allow S_3-breaking mass matrices. The non-associativity of O
   creates {n_break_8} independent S_3-breaking directions in the
   allowed mass matrix space.

   These breaking directions are NOT put in by hand -- they emerge
   from the algebraic structure of the octonions and the NCG axioms.

5. COMBINED FIT (M_oct + D_F breaking + RS):
   chi^2 = {chi2_c:.2f}, dof = {n_dof_c}
   chi^2/dof = {chi2_c/max(n_dof_c,1):.2f}
   Null directions remaining: {n_null_c}
""")
    if n_null_c == 0 and chi2_c / max(n_dof_c, 1) < 10.0:
        print("   *** THE BASIN IS DETERMINED. ***")
        print("   The octonionic Dirac operator + RS warp factor fully")
        print("   constrains the fermion sector. No higher-dimensional")
        print("   metric data needed. The 5 null directions from the")
        print("   original basin_determination are FILLED by D_F breaking.")
    elif n_null_c < 5:
        print(f"   PARTIAL DETERMINATION: {5 - n_null_c} of 5 null directions filled.")
        print(f"   {n_null_c} directions remain unconstrained.")
        print(f"   D_F breaking helps but doesn't fully determine the basin.")
    else:
        print("   D_F breaking does NOT reduce the null space.")
        print("   The breaking matrices are degenerate with existing parameters.")
else:
    print("""4. THE KEY RESULT:
   The first-order condition on the octonions produces ONLY S_3-invariant
   allowed mass matrices. The non-associativity does not generate
   S_3-breaking at the level of the NCG first-order condition.

   This means: the S_3 breaking must come from OUTSIDE the algebraic
   constraints -- either from:
   (a) The brane-localized terms (IR boundary conditions)
   (b) Higher-dimensional geometry (compact manifold shape)
   (c) A different algebraic structure (J_3(O), Cayley plane)

5. IMPLICATION FOR MERIDIAN:
   The octonionic NCG provides the TOPOLOGY (gauge group, generations,
   anomaly cancellation) but not the full METRIC structure. The 5 null
   directions from basin_determination remain unfilled. The basin
   requires additional input beyond the spectral triple.
""")

print("\n" + "=" * 72)
print("CALCULATION COMPLETE")
print("=" * 72)
