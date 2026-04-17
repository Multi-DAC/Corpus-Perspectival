"""Diagnostic script for CP^2 toric eigenvalue problem."""
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
import traceback

# Create simple structured triangle mesh of inset simplex
N = 15
eps = 0.02
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
domain = mesh.create_mesh(MPI.COMM_WORLD, cells_arr, domain_ufl, coords)

ncells = len(cells)
npts = len(points)
print("Mesh: %d cells, %d vertices" % (ncells, npts))
print("Coord range: s1=[%.4f, %.4f], s2=[%.4f, %.4f]" % (
    coords[:,0].min(), coords[:,0].max(), coords[:,1].min(), coords[:,1].max()))

# (0,0) sector -- pure degenerate diffusion, no potential
V = fem.functionspace(domain, ("Lagrange", 2))
ndofs = V.dofmap.index_map.size_global
print("DOFs: %d" % ndofs)

u_trial = ufl.TrialFunction(V)
v_test = ufl.TestFunction(V)
x = ufl.SpatialCoordinate(domain)
s1 = x[0]
s2 = x[1]

G11 = 2.0 * s1 * (1.0 - s1)
G22 = 2.0 * s2 * (1.0 - s2)
G12 = -2.0 * s1 * s2

a_form = fem.form(
    (G11 * ufl.Dx(u_trial, 0) * ufl.Dx(v_test, 0)
   + G12 * (ufl.Dx(u_trial, 0) * ufl.Dx(v_test, 1) + ufl.Dx(u_trial, 1) * ufl.Dx(v_test, 0))
   + G22 * ufl.Dx(u_trial, 1) * ufl.Dx(v_test, 1)) * ufl.dx
)
m_form = fem.form(u_trial * v_test * ufl.dx)

print("Assembling...")
A = assemble_matrix(a_form)
A.assemble()
M = assemble_matrix(m_form)
M.assemble()

a_size = A.getSize()
a_nnz = A.getInfo()['nz_allocated']
a_norm = A.norm()
m_norm = M.norm()
print("A: size=%s, nnz=%.0f, norm=%.6e" % (str(a_size), a_nnz, a_norm))
print("M: size=%s, norm=%.6e" % (str(M.getSize()), m_norm))

# Try solving with no spectral transform first
print("\n--- Attempt 1: no spectral transform ---")
try:
    eigensolver = SLEPc.EPS().create(MPI.COMM_WORLD)
    eigensolver.setOperators(A, M)
    eigensolver.setProblemType(SLEPc.EPS.ProblemType.GHEP)
    eigensolver.setType(SLEPc.EPS.Type.KRYLOVSCHUR)
    eigensolver.setWhichEigenpairs(SLEPc.EPS.Which.SMALLEST_REAL)
    eigensolver.setDimensions(nev=8)
    eigensolver.setTolerances(tol=1e-8, max_it=500)
    eigensolver.solve()

    nconv = eigensolver.getConverged()
    print("Converged: %d" % nconv)
    for i in range(min(nconv, 8)):
        val = eigensolver.getEigenvalue(i)
        if hasattr(val, 'real'):
            print("  eig %d: %.6f + %.6fi" % (i, val.real, val.imag))
        else:
            print("  eig %d: %.6f" % (i, val))
    eigensolver.destroy()
except Exception as ex:
    print("ERROR: %s" % str(ex))
    traceback.print_exc()

# Try with shift-invert at sigma = 0.1
print("\n--- Attempt 2: shift-invert at sigma=0.1 ---")
try:
    eigensolver = SLEPc.EPS().create(MPI.COMM_WORLD)
    eigensolver.setOperators(A, M)
    eigensolver.setProblemType(SLEPc.EPS.ProblemType.GHEP)
    eigensolver.setType(SLEPc.EPS.Type.KRYLOVSCHUR)
    eigensolver.setWhichEigenpairs(SLEPc.EPS.Which.TARGET_MAGNITUDE)
    eigensolver.setTarget(0.1)
    eigensolver.setDimensions(nev=8)
    eigensolver.setTolerances(tol=1e-8, max_it=500)

    st = eigensolver.getST()
    st.setType(SLEPc.ST.Type.SINVERT)

    eigensolver.solve()

    nconv = eigensolver.getConverged()
    print("Converged: %d" % nconv)
    for i in range(min(nconv, 8)):
        val = eigensolver.getEigenvalue(i)
        if hasattr(val, 'real'):
            print("  eig %d: %.6f + %.6fi" % (i, val.real, val.imag))
        else:
            print("  eig %d: %.6f" % (i, val))
    eigensolver.destroy()
except Exception as ex:
    print("ERROR: %s" % str(ex))
    traceback.print_exc()

# Try with GNHEP (general non-hermitian) in case the matrices aren't symmetric
print("\n--- Attempt 3: GNHEP problem type ---")
try:
    eigensolver = SLEPc.EPS().create(MPI.COMM_WORLD)
    eigensolver.setOperators(A, M)
    eigensolver.setProblemType(SLEPc.EPS.ProblemType.GNHEP)
    eigensolver.setType(SLEPc.EPS.Type.KRYLOVSCHUR)
    eigensolver.setWhichEigenpairs(SLEPc.EPS.Which.SMALLEST_REAL)
    eigensolver.setDimensions(nev=8)
    eigensolver.setTolerances(tol=1e-8, max_it=500)
    eigensolver.solve()

    nconv = eigensolver.getConverged()
    print("Converged: %d" % nconv)
    for i in range(min(nconv, 8)):
        val = eigensolver.getEigenvalue(i)
        if hasattr(val, 'real'):
            print("  eig %d: %.6f + %.6fi" % (i, val.real, val.imag))
        else:
            print("  eig %d: %.6f" % (i, val))
    eigensolver.destroy()
except Exception as ex:
    print("ERROR: %s" % str(ex))
    traceback.print_exc()

# Check if A is really symmetric
print("\n--- Matrix diagnostics ---")
# Check a few entries
Alocal = A.getValuesCSR()
print("A is %s" % ("symmetric" if A.isSymmetric(tol=1e-10) else "NOT symmetric"))
print("M is %s" % ("symmetric" if M.isSymmetric(tol=1e-10) else "NOT symmetric"))

# Check if A has any negative diagonal entries (would indicate problems)
diag_A = A.getDiagonal()
diag_vals = diag_A.getArray()
print("A diagonal: min=%.6e, max=%.6e" % (diag_vals.min(), diag_vals.max()))
diag_M = M.getDiagonal()
diag_m_vals = diag_M.getArray()
print("M diagonal: min=%.6e, max=%.6e" % (diag_m_vals.min(), diag_m_vals.max()))

A.destroy()
M.destroy()
