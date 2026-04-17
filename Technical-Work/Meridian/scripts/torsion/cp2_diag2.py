"""
Diagnose the normalization issue in CP^2 toric eigenvalue problem.

Key question: what is the CORRECT Laplacian in toric symplectic coords?

On a Kahler manifold with symplectic coords (s,theta), the metric is:
  ds: g_{ij}^{base} = Hess_{ij}(phi)   (phi = symplectic potential)
  dt: g_{ij}^{fiber} = Hess_{ij}(phi)
  (block diagonal)

The FULL metric determinant:
  det(g_full) = det(Hess(phi))^2
  (because the metric is block diagonal with both blocks = Hess(phi))

Wait, that's not right. In the (s,theta) coords for a toric Kahler:
  g = [ H     0   ]
      [ 0   H^{-1} ]

where H = Hess(phi). The angular part has INVERSE Hessian.

Actually for a toric Kahler manifold in action-angle coordinates:
The metric is:
  ds^2 = sum H_{ij} ds_i ds_j + sum H^{ij} dtheta_i dtheta_j

where H = Hess(phi), H^{ij} = (H^{-1})_{ij} = G^{ij}.

So det(g_full) = det(H) * det(H^{-1}) = 1!

That means sqrt(det g) = 1, and the volume form IS just ds dtheta (flat).
The Laplace-Beltrami operator in these coords:

Delta f = (1/sqrt(det g)) sum d_mu (sqrt(det g) g^{mu nu} d_nu f)
        = sum d_mu (g^{mu nu} d_nu f)    [since sqrt(det g) = 1]

For the block diagonal metric:
g^{mu nu} = [ H^{-1}  0 ]  = [ G    0 ]
             [  0      H ]    [ 0    H ]

So for the base (s) directions: g^{ij}_{base} = G^{ij} = H^{-1}_{ij}
For the fiber (theta) directions: g^{ij}_{fiber} = H_{ij}

Delta f = sum_{ij} d/ds_i (G^{ij} df/ds_j) + sum_{ij} H_{ij} d^2f/dtheta_i dtheta_j

For f = g(s) exp(i m.theta):
Delta f = [sum_{ij} d/ds_i(G^{ij} dg/ds_j) - sum_{ij} H_{ij} m_i m_j * g] * exp(im.t)

So the eigenvalue problem for -Delta is:
  -sum d/ds_i(G^{ij} dg/ds_j) + sum H_{ij} m_i m_j g = lambda g

with FLAT measure ds1 ds2.

This is what I had before. But the eigenvalues don't match.

Let me check: maybe I got H wrong. For CP^2 with FS metric:
phi(s) = (1/2)(s1 log s1 + s2 log s2 + s0 log s0), s0 = 1-s1-s2

H_{11} = d^2 phi/ds1^2 = 1/(2s1) + 1/(2s0)
H_{12} = d^2 phi/ds1 ds2 = 1/(2s0)
H_{22} = 1/(2s2) + 1/(2s0)

G = H^{-1}, det(H) = 1/(4 s0 s1 s2)

G^{11} = H_{22}/det(H) = (1/(2s2)+1/(2s0)) * 4s0s1s2
       = 4s0s1s2 * (s0+s2)/(2s0s2) = 2s1(s0+s2) = 2s1(1-s1)  ✓
G^{12} = -H_{12}/det(H) = -1/(2s0) * 4s0s1s2 = -2s1s2  ✓
G^{22} = H_{11}/det(H) = (1/(2s1)+1/(2s0)) * 4s0s1s2
       = 2s2(s0+s1) = 2s2(1-s2)  ✓

OK so the matrices are correct. Why don't the eigenvalues match?

Possible issue: the NORMALIZATION of the symplectic potential.
The standard FS metric on CP^2 with Vol = pi^2/2 corresponds to
  omega = i/2 * d d-bar log(1 + |z|^2)
In the affine chart z0=1, z1,z2 are coords.

The moment map for the T^2 action is:
  mu_1 = |z1|^2 / (1 + |z1|^2 + |z2|^2)
  mu_2 = |z2|^2 / (1 + |z1|^2 + |z2|^2)

Image: Delta = {s1>=0, s2>=0, s1+s2<=1}

The symplectic potential for [omega] = [standard FS]:
  phi(s) = (1/2)(s1 log s1 + s2 log s2 + (1-s1-s2) log(1-s1-s2))

But wait -- there may be a factor of 2pi in the relation between the
symplectic form and the metric. For CP^n the standard normalization is:
  [omega^n / n!] = Vol/pi^n on the Kahler class.

Actually, let me try a DIFFERENT approach: instead of guessing the normalization,
let me solve the STANDARD Laplacian on the STANDARD 2-simplex
(NOT the toric problem) and see if the FEM works at all.

The 2-simplex with flat metric has eigenvalues that can be computed.
If FEM works for that, then the issue is in my toric formulation.

Actually, let me try scaling. If the numerical eigenvalues are 6.978 vs exact 6.0,
the ratio is 6.978/6.0 = 1.163. Let me check the next level:
  19.55/16.0 = 1.222
  19.68/16.0 = 1.230

These ratios aren't constant, so it's not just an overall scale factor.
But they're not far off either.

Let me try a different normalization of the symplectic potential:
  phi_alpha(s) = alpha * (s1 log s1 + s2 log s2 + s0 log s0)
with alpha as a free parameter. Then H -> 2*alpha * H, G -> G/(2*alpha).
The eigenvalue equation becomes:
  -(1/(2*alpha)) * div(G grad g) = lambda g
  => eigenvalues scale as 1/(2*alpha)

With alpha = 1/2 (my current choice), the eigenvalues should be
what we get from div(G grad g). If I change alpha, they scale.

But the EXACT eigenvalues of CP^2 are fixed by the curvature normalization.
So the question is: what value of alpha gives the correct FS metric?

For CP^n with omega = (i/2) d d-bar log(1+|z|^2):
  The scalar curvature is R = 2n(n+1) = 12 for CP^2
  And Ric = 2(n+1)g = 6g

The Guillemin symplectic potential for this omega is:
  phi = (1/2) sum s_k log s_k  (sum over k=0,1,...,n)

So alpha = 1/2 is correct for the standard FS.

But WAIT. I may have the wrong sign convention or wrong factor in the
Laplacian -> eigenvalue mapping. Let me double-check by computing
a KNOWN case: the standard Laplacian on CP^1 = S^2.

For CP^1, the toric reduction gives a 1D problem on [0,1]:
  phi(s) = (1/2)(s log s + (1-s) log(1-s))
  H = phi'' = 1/(2s) + 1/(2(1-s)) = 1/(2s(1-s))
  G = 1/H = 2s(1-s)

  -d/ds(G dg/ds) = lambda g on [eps, 1-eps]
  i.e., -d/ds(2s(1-s) dg/ds) = lambda g

Standard S^2 eigenvalues: l(l+1) for l=0,1,2,...
For CP^1 with Ric = 2g (i.e. sphere of radius 1):
  eigenvalues = l(l+1), l=0,1,2,...

Using the Casimir formula: lambda_k = 2*k*(k+1)/...
For CP^1: lambda_k = k*(k+1) (from l(l+1) with Ric = 2g)

Let me check: Using CP^n formula lambda_{a,b} = 2(a^2+ab+b^2+3a+3b)/3
for n=2... wait that's specific to CP^2.

For CP^1: lambda_k = 2k(k+1)/1 = 2k(k+1)? No,
For CP^1 = SU(2)/U(1), eigenvalue of Casimir on V_k = k(k+2)/4...
actually the standard result for S^2 of radius R is:
  lambda_l = l(l+1)/R^2

For the FS metric on CP^1 with Ric = 2g, the radius is 1/sqrt(2)
(since for S^2 of radius R, Ric = g/R^2, so Ric=2g => R=1/sqrt(2))
Wait no. For S^2 of radius R: Ric_{ij} = (1/R^2) g_{ij}.
Ric = 2g => R = 1/sqrt(2)? No, Ricci scalar R_scal = 2/R^2 for S^2,
and Ric = (1/R^2) g, so Ric = 2g means R = 1/sqrt(2).
Then eigenvalues = l(l+1)/R^2 = l(l+1) * 2 = 2l(l+1).

Hmm, but the standard result for CP^1 with holomorphic sectional
curvature K=4 (i.e. Ric = 2g in 2 real dims, or Ric = 2Kg = 4g
in...no, for a 2-manifold Ric = Kg where K is Gauss curvature).

I'm getting confused. Let me just verify numerically on CP^1.
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

# ============================================
# CP^1 = S^2 toric reduction: 1D problem on [eps, 1-eps]
# ============================================

def test_cp1():
    """
    Solve -d/ds[2s(1-s) dg/ds] = lambda g on [eps, 1-eps].
    Compare to S^2 eigenvalues.
    """
    print("=" * 50)
    print("CP^1 (S^2) toric eigenvalue test")
    print("=" * 50)

    N = 200
    eps = 0.001

    # Create 1D mesh on [eps, 1-eps]
    domain = mesh.create_interval(MPI.COMM_WORLD, N, [eps, 1.0 - eps])
    V = fem.functionspace(domain, ("Lagrange", 3))
    ndofs = V.dofmap.index_map.size_global
    print("DOFs: %d" % ndofs)

    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    x = ufl.SpatialCoordinate(domain)
    s = x[0]

    G = 2.0 * s * (1.0 - s)

    a_form = fem.form(G * ufl.Dx(u, 0) * ufl.Dx(v, 0) * ufl.dx)
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
    eigensolver.setDimensions(nev=10)
    eigensolver.setTolerances(tol=1e-12, max_it=1000)
    eigensolver.solve()

    nconv = eigensolver.getConverged()
    print("\nResults (T^2-invariant = m=0 sector):")
    print("  These should match S^2 eigenvalues for axial modes (l, m=0)")
    print("  %-5s %-12s %-12s %-12s %-10s" % ("idx", "numerical", "l(l+1)", "2l(l+1)", "ratio/l(l+1)"))

    for i in range(min(nconv, 8)):
        val = eigensolver.getEigenvalue(i)
        if hasattr(val, 'real'):
            eigval = val.real
        else:
            eigval = val

        l = i  # l = 0, 1, 2, ...
        exact_v1 = l * (l + 1)         # S^2 of radius 1
        exact_v2 = 2 * l * (l + 1)     # S^2 of radius 1/sqrt(2)
        if exact_v1 > 0:
            ratio = eigval / exact_v1
        else:
            ratio = 0.0
        print("  %-5d %-12.6f %-12.6f %-12.6f %-10.6f" % (i, eigval, exact_v1, exact_v2, ratio))

    eigensolver.destroy()
    A.destroy()
    M.destroy()


def test_cp2():
    """
    CP^2 toric eigenvalue test on (0,0) sector.
    Solve -div(G grad g) = lambda g on inset simplex.
    """
    print("\n" + "=" * 50)
    print("CP^2 toric eigenvalue test (m1=m2=0)")
    print("=" * 50)

    N = 30
    eps = 0.005
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
    print("Mesh: %d cells" % len(cells))

    V = fem.functionspace(domain, ("Lagrange", 3))
    print("DOFs: %d" % V.dofmap.index_map.size_global)

    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)
    x = ufl.SpatialCoordinate(domain)
    s1 = x[0]
    s2 = x[1]

    G11 = 2.0 * s1 * (1.0 - s1)
    G22 = 2.0 * s2 * (1.0 - s2)
    G12 = -2.0 * s1 * s2

    a_form = fem.form(
        (G11 * ufl.Dx(u, 0) * ufl.Dx(v, 0)
       + G12 * (ufl.Dx(u, 0) * ufl.Dx(v, 1) + ufl.Dx(u, 1) * ufl.Dx(v, 0))
       + G22 * ufl.Dx(u, 1) * ufl.Dx(v, 1)) * ufl.dx
    )
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
    eigensolver.setDimensions(nev=10)
    eigensolver.setTolerances(tol=1e-10, max_it=1000)
    eigensolver.solve()

    nconv = eigensolver.getConverged()

    # Exact diagonal eigenvalues: lambda_{k,k} = 2(3k^2 + 6k)/3 = 2k(k+2)
    print("\nResults:")
    print("  Exact diagonal: lambda_{k,k} = 2k(k+2)")
    print("  %-5s %-12s %-12s %-10s" % ("idx", "numerical", "2k(k+2)", "ratio"))

    for i in range(min(nconv, 8)):
        val = eigensolver.getEigenvalue(i)
        if hasattr(val, 'real'):
            eigval = val.real
        else:
            eigval = val

        k = i
        exact_diag = 2.0 * k * (k + 2)
        if exact_diag > 0:
            ratio = eigval / exact_diag
        else:
            ratio = 0.0
        print("  %-5d %-12.6f %-12.6f %-10.6f" % (i, eigval, exact_diag, ratio))

    eigensolver.destroy()
    A.destroy()
    M.destroy()


test_cp1()
test_cp2()
