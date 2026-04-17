"""
CP^2 toric eigenvalue validation — refined diagnostic.

Now understanding that the (0,0) charge sector contains MULTIPLE
eigenfunctions per irrep V_{(k,k)} (one per zero-weight vector).

The zero-weight multiplicity of V_{(k,k)} in SU(3) is:
  mult_0(k,k) = k+1  (the number of independent Cartan elements
  that can be raised/lowered k times)

So we expect eigenvalue clusters:
  lambda = 6.0  with numerical mult 2  (k=1: mult_0 = 2)   [ADJOINT]
  lambda = 16.0 with numerical mult 3  (k=2: mult_0 = 3)
  lambda = 30.0 with numerical mult 4  (k=3: mult_0 = 4)

Also: the NON-diagonal irreps V_{(a,b)} with a != b contribute to
non-zero charge sectors. E.g., V_{(1,0)} = fundamental rep, dim 3,
weights are (1,0), (0,1), (-1,-1) in the Dynkin basis... wait,
need to be more careful about the weight conventions.

For the T^2 action on CP^2 = SU(3)/U(2), the weights ARE the
moment map values. For V_{(1,0)} (fundamental, dim 3):
  Weights in the toric basis: (1,0), (-1,1), (0,-1)
  Or equivalently: the three vertices of the weight diagram.
  Each sector (m1,m2) = (1,0), (-1,1), (0,-1) gets ONE eigenfunction
  with eigenvalue lambda_{1,0} = 8/3.

Let me verify this by solving the (1,0) sector and checking for
an eigenvalue near 8/3 = 2.667.
"""

import numpy as np
from mpi4py import MPI
from petsc4py import PETSc
from slepc4py import SLEPc
import dolfinx
from dolfinx import fem, mesh
from dolfinx.fem.petsc import assemble_matrix
import ufl
import basix
import basix.ufl


def create_mesh_triangle(N, eps):
    """Create structured mesh of inset simplex."""
    scale = 1.0 - 3*eps
    points = []
    idx_map = {}
    k = 0
    for j in range(N + 1):
        for i in range(N + 1 - j):
            s1 = eps + scale * i / N
            s2 = eps + scale * j / N
            points.append([s1, s2])
            idx_map[(i, j)] = k
            k += 1

    coords = np.array(points, dtype=np.float64)
    cells = []
    for j in range(N):
        for i in range(N - j):
            v0 = idx_map[(i, j)]
            v1 = idx_map[(i+1, j)]
            v2 = idx_map[(i, j+1)]
            cells.append([v0, v1, v2])
            if i + j + 1 < N:
                v3 = idx_map[(i+1, j+1)]
                cells.append([v1, v3, v2])

    cells_arr = np.array(cells, dtype=np.int64)
    domain_ufl = ufl.Mesh(basix.ufl.element("Lagrange", basix.CellType.triangle, 1, shape=(2,)))
    return mesh.create_mesh(MPI.COMM_WORLD, cells_arr, domain_ufl, coords), len(cells)


def solve_sector(domain, m1, m2, num_eigs=12, poly_order=3):
    """Solve the toric eigenvalue problem for charge (m1,m2)."""
    V = fem.functionspace(domain, ("Lagrange", poly_order))
    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    x = ufl.SpatialCoordinate(domain)
    s1 = x[0]
    s2 = x[1]
    s0 = 1.0 - s1 - s2

    # Diffusion tensor
    G11 = 2.0 * s1 * (1.0 - s1)
    G22 = 2.0 * s2 * (1.0 - s2)
    G12 = -2.0 * s1 * s2

    a_diff = (G11 * ufl.Dx(u, 0) * ufl.Dx(v, 0)
            + G12 * (ufl.Dx(u, 0) * ufl.Dx(v, 1) + ufl.Dx(u, 1) * ufl.Dx(v, 0))
            + G22 * ufl.Dx(u, 1) * ufl.Dx(v, 1)) * ufl.dx

    # Angular momentum potential
    if m1 != 0 or m2 != 0:
        e = 1e-14
        H11 = 0.5 / (s1 + e) + 0.5 / (s0 + e)
        H12v = 0.5 / (s0 + e)
        H22 = 0.5 / (s2 + e) + 0.5 / (s0 + e)
        Vm = float(m1*m1) * H11 + 2.0 * float(m1*m2) * H12v + float(m2*m2) * H22
        a_pot = Vm * u * v * ufl.dx
    else:
        a_pot = fem.Constant(domain, PETSc.ScalarType(0.0)) * u * v * ufl.dx

    a_form = fem.form(a_diff + a_pot)
    m_form = fem.form(u * v * ufl.dx)

    A = assemble_matrix(a_form)
    A.assemble()
    M = assemble_matrix(m_form)
    M.assemble()

    eigensolver = SLEPc.EPS().create(MPI.COMM_WORLD)
    eigensolver.setOperators(A, M)
    eigensolver.setProblemType(SLEPc.EPS.ProblemType.GHEP)
    eigensolver.setType(SLEPc.EPS.Type.KRYLOVSCHUR)
    eigensolver.setWhichEigenpairs(SLEPc.EPS.Which.SMALLEST_REAL)
    eigensolver.setDimensions(nev=num_eigs, ncv=max(3*num_eigs, 30))
    eigensolver.setTolerances(tol=1e-10, max_it=2000)
    eigensolver.solve()

    nconv = eigensolver.getConverged()
    eigenvalues = []
    for i in range(min(nconv, num_eigs)):
        val = eigensolver.getEigenvalue(i)
        if hasattr(val, 'real'):
            eigenvalues.append(val.real)
        else:
            eigenvalues.append(float(val))

    eigensolver.destroy()
    A.destroy()
    M.destroy()

    return sorted(eigenvalues)


def cp2_eigenvalue(a, b):
    return 2.0 * (a**2 + b**2 + a*b + 3*a + 3*b) / 3.0


# ============================================
# Main
# ============================================

print("=" * 60)
print("CP^2 TORIC SPECTRAL VALIDATION — REFINED")
print("=" * 60)

# Higher mesh density
N = 50
eps = 0.003
domain, ncells = create_mesh_triangle(N, eps)
print("Mesh: N=%d, eps=%.4f, cells=%d" % (N, eps, ncells))
print()

# --- Sector (0,0): diagonal eigenvalues ---
print("SECTOR (0,0) — T^2-invariant")
print("-" * 50)
eigs_00 = solve_sector(domain, 0, 0, num_eigs=15, poly_order=3)
print("  Numerical eigenvalues (first 10):")
for i, e in enumerate(eigs_00[:10]):
    print("    [%d] %.6f" % (i, e))
print()

# Group nearby eigenvalues
clusters = []
current = [eigs_00[0]]
for e in eigs_00[1:]:
    if abs(e - current[-1]) < 0.3:
        current.append(e)
    else:
        clusters.append(current)
        current = [e]
clusters.append(current)

print("  Eigenvalue clusters:")
exact_diag = [cp2_eigenvalue(k, k) for k in range(6)]
for i, cl in enumerate(clusters[:6]):
    mean = np.mean(cl)
    mult = len(cl)
    if i < len(exact_diag):
        ex = exact_diag[i]
        if ex > 0:
            err = abs(mean - ex) / ex * 100
            print("    Cluster %d: mean=%.4f, mult=%d | exact(%.1f,%d)=%.4f | err=%.2f%%" %
                  (i, mean, mult, i, i, ex, err))
        else:
            print("    Cluster %d: mean=%.4f, mult=%d | exact=0" % (i, mean, mult))

print()

# --- Sector (1,0): should contain lambda_{1,0} = 8/3 and lambda_{2,1} = 32/3 etc ---
print("SECTOR (1,0)")
print("-" * 50)
eigs_10 = solve_sector(domain, 1, 0, num_eigs=10, poly_order=3)
print("  Numerical eigenvalues:")
for i, e in enumerate(eigs_10[:8]):
    print("    [%d] %.6f" % (i, e))
print("  Expected: lambda_{1,0} = %.6f" % cp2_eigenvalue(1, 0))
print("  Expected: lambda_{1,1} = %.6f (if (1,0) is a weight of V_{1,1})" % cp2_eigenvalue(1, 1))
print()

# --- Sector (0,1) ---
print("SECTOR (0,1)")
print("-" * 50)
eigs_01 = solve_sector(domain, 0, 1, num_eigs=10, poly_order=3)
print("  Numerical eigenvalues:")
for i, e in enumerate(eigs_01[:8]):
    print("    [%d] %.6f" % (i, e))
print("  Should match sector (1,0) by S_3 symmetry of CP^2")
print()

# --- Sector (1,1) ---
print("SECTOR (1,1)")
print("-" * 50)
eigs_11 = solve_sector(domain, 1, 1, num_eigs=10, poly_order=3)
print("  Numerical eigenvalues:")
for i, e in enumerate(eigs_11[:8]):
    print("    [%d] %.6f" % (i, e))
print()

# --- Sector (-1,0) ---
print("SECTOR (-1,0)")
print("-" * 50)
eigs_m10 = solve_sector(domain, -1, 0, num_eigs=10, poly_order=3)
print("  Numerical eigenvalues:")
for i, e in enumerate(eigs_m10[:8]):
    print("    [%d] %.6f" % (i, e))
print()

# --- Sector (1,-1) ---
print("SECTOR (1,-1)")
print("-" * 50)
eigs_1m1 = solve_sector(domain, 1, -1, num_eigs=10, poly_order=3)
print("  Numerical eigenvalues:")
for i, e in enumerate(eigs_1m1[:8]):
    print("    [%d] %.6f" % (i, e))
print()

# --- Collect and compare ---
print("=" * 60)
print("COMPREHENSIVE COMPARISON")
print("=" * 60)

# All sectors we computed
sectors = {
    (0, 0): eigs_00,
    (1, 0): eigs_10,
    (0, 1): eigs_01,
    (1, 1): eigs_11,
    (-1, 0): eigs_m10,
    (1, -1): eigs_1m1,
}

# Collect all numerical eigenvalues
all_num = []
for (m1, m2), eigs in sectors.items():
    for e in eigs:
        all_num.append(e)
all_num.sort()

# Exact spectrum
exact_all = []
for a in range(5):
    for b in range(5):
        exact_all.append(cp2_eigenvalue(a, b))
exact_unique = sorted(set(exact_all))

print("\nAll numerical eigenvalues (first 30):")
for i, e in enumerate(all_num[:30]):
    # Find closest exact
    diffs = [abs(e - ex) for ex in exact_unique]
    best_idx = np.argmin(diffs)
    best_ex = exact_unique[best_idx]
    if best_ex > 0.01:
        err = abs(e - best_ex) / best_ex * 100
    else:
        err = abs(e) * 100
    print("  [%2d] num=%.4f  closest_exact=%.4f  err=%.2f%%" % (i, e, best_ex, err))
