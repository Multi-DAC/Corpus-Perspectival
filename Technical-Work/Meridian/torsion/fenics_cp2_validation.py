"""
fenics_cp2_validation.py
========================
Spectral eigenvalue validation on CP^2 (complex projective plane).

CP^2 = SU(3)/U(2), real dimension 4, complex dimension 2.
Fubini-Study metric with Ric = 6g, Vol(CP^2) = pi^2/2.

4D FEM LIMITATION:
  DOLFINx/basix only supports cell types up to topological dimension 3
  (point, interval, triangle, tetrahedron, quad, hex, prism, pyramid).
  There is NO 4-simplex (pentatope) cell type. Native 4D FEM is impossible.

RESOLUTION — TORIC SYMPLECTIC REDUCTION:
  CP^2 has a T^2 = U(1)^2 toric action: [z0 : e^{it1} z1 : e^{it2} z2].
  The moment map sends CP^2 to the simplex Delta = {s1>=0, s2>=0, s1+s2<=1}.
  Setting s0 = 1-s1-s2, the Laplacian separates in action-angle coords.

  For f(s,theta) = g(s) * exp(i(m1*t1 + m2*t2)), the eigenvalue problem
  on CP^2 reduces to a 2D problem on Delta:

    -div(G grad g) + V_m * g = lambda * g    (on Delta)

  where:
    G^{ij} = 2(s_i delta_{ij} - s_i s_j)    (degenerate diffusion tensor)
    V_m    = sum_{ij} H_{ij} m_i m_j         (angular momentum potential)
    H      = Hess(phi), phi = symplectic potential of FS metric

  Natural boundary conditions (from regularity of eigenfunctions on CP^2).

EXACT SPECTRUM:
  lambda_{a,b} = 2(a^2 + ab + b^2 + 3a + 3b)/3,  a,b >= 0
  mult = (a+1)(b+1)(a+b+2)/2  (= dim V_{(a,b)} of SU(3))
  Eigenvalue lambda_{a,b} = lambda_{b,a} with combined mult if a != b.

Author: Clawd
Date: 2026-03-23
"""

import numpy as np
import sys
import time
from mpi4py import MPI
from petsc4py import PETSc
from slepc4py import SLEPc

import dolfinx
from dolfinx import fem, mesh
from dolfinx.fem.petsc import assemble_matrix
import ufl
import basix
import basix.ufl
import gmsh
from dolfinx.io.gmsh import model_to_mesh


# ============================================================
# Exact CP^2 spectrum
# ============================================================

def cp2_eigenvalue(a, b):
    """Exact Laplacian eigenvalue for SU(3) irrep V_{(a,b)} on unit CP^2."""
    return 2.0 * (a**2 + b**2 + a*b + 3*a + 3*b) / 3.0

def cp2_multiplicity(a, b):
    """Dimension of SU(3) irrep V_{(a,b)}."""
    return (a + 1) * (b + 1) * (a + b + 2) // 2

def exact_spectrum(max_ab=8):
    """Sorted list of (eigenvalue, total_multiplicity, a, b)."""
    vals = []
    for a in range(max_ab):
        for b in range(a + 1):
            lam = cp2_eigenvalue(a, b)
            m = cp2_multiplicity(a, b)
            total_m = 2 * m if a != b else m
            vals.append((lam, total_m, a, b))
    vals.sort()
    return vals


# ============================================================
# Mesh the moment polytope
# ============================================================

def create_simplex_mesh_gmsh(N, eps=5e-3, comm=MPI.COMM_WORLD):
    """
    Mesh the 2-simplex Delta = {s1>=0, s2>=0, s1+s2<=1},
    inset by eps to avoid the singular boundary where s_i = 0
    (torus fiber degenerates -> metric singularity).

    N: approximate number of elements per edge.
    """
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.model.add("simplex")

    # Inset triangle
    p1 = gmsh.model.geo.addPoint(eps, eps, 0)
    p2 = gmsh.model.geo.addPoint(1.0 - 2*eps, eps, 0)
    p3 = gmsh.model.geo.addPoint(eps, 1.0 - 2*eps, 0)

    l1 = gmsh.model.geo.addLine(p1, p2)
    l2 = gmsh.model.geo.addLine(p2, p3)
    l3 = gmsh.model.geo.addLine(p3, p1)

    cl = gmsh.model.geo.addCurveLoop([l1, l2, l3])
    surf = gmsh.model.geo.addPlaneSurface([cl])
    gmsh.model.geo.synchronize()

    lc = 1.0 / N
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", lc)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", lc / 2)

    gmsh.model.mesh.generate(2)

    domain, _, _ = model_to_mesh(gmsh.model, comm, 0, gdim=2)
    gmsh.finalize()
    return domain


def create_simplex_mesh_builtin(N, eps=5e-3, comm=MPI.COMM_WORLD):
    """
    Alternative: use DOLFINx built-in rectangle mesh, then map to triangle.
    This avoids gmsh dependency issues.

    Maps the unit square [0,1]^2 to the simplex via:
      s1 = u * (1-v), s2 = v
    restricted to the triangle where s1+s2 <= 1.

    Actually, simpler: mesh the unit square and discard elements
    above the diagonal. But DOLFINx doesn't support that easily.

    Instead: mesh the simplex directly using create_mesh with custom cells.
    """
    # Create a structured triangulation of the simplex
    # Grid points: (i/N, j/N) with i>=0, j>=0, i+j<=N
    # Map to inset simplex: s1 = eps + (1-3*eps)*i/N, s2 = eps + (1-3*eps)*j/N

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

    # Triangulate: each grid square (i,j)-(i+1,j)-(i+1,j+1)-(i,j+1)
    # splits into two triangles. Only squares with i+j < N exist.
    cells = []
    for j in range(N):
        for i in range(N - j):
            # Lower triangle: (i,j), (i+1,j), (i,j+1)
            v0 = idx_map[(i, j)]
            v1 = idx_map[(i+1, j)]
            v2 = idx_map[(i, j+1)]
            cells.append([v0, v1, v2])
            # Upper triangle (if it exists): (i+1,j), (i+1,j+1), (i,j+1)
            if i + j + 1 < N:
                v3 = idx_map[(i+1, j+1)]
                cells.append([v1, v3, v2])

    cells_arr = np.array(cells, dtype=np.int64)

    # Create DOLFINx mesh
    e = basix.ufl.element("Lagrange", basix.CellType.triangle, 1, shape=())
    domain_ufl = ufl.Mesh(basix.ufl.element("Lagrange", basix.CellType.triangle, 1, shape=(2,)))
    domain = mesh.create_mesh(comm, cells_arr, domain_ufl, coords)

    return domain


# ============================================================
# Solve the reduced eigenvalue problem for one charge sector
# ============================================================

def solve_charge_sector(domain, m1, m2, num_eigs=12, poly_order=2):
    """
    Solve the toric-reduced Laplacian eigenvalue problem on the simplex
    for T^2 charge (m1, m2).

    Returns sorted list of eigenvalues.
    """
    V = fem.functionspace(domain, ("Lagrange", poly_order))

    u = ufl.TrialFunction(V)
    v = ufl.TestFunction(V)

    x = ufl.SpatialCoordinate(domain)
    s1 = x[0]
    s2 = x[1]
    s0 = 1.0 - s1 - s2

    # Diffusion tensor G^{ij} = 2(s_i delta_{ij} - s_i s_j)
    # This is the inverse Hessian of the symplectic potential phi(s).
    G11 = 2.0 * s1 * (1.0 - s1)
    G22 = 2.0 * s2 * (1.0 - s2)
    G12 = -2.0 * s1 * s2

    # Stiffness form: int G^{ij} (du/ds_i)(dv/ds_j) ds
    a_stiff = (G11 * ufl.Dx(u, 0) * ufl.Dx(v, 0)
             + G12 * (ufl.Dx(u, 0) * ufl.Dx(v, 1) + ufl.Dx(u, 1) * ufl.Dx(v, 0))
             + G22 * ufl.Dx(u, 1) * ufl.Dx(v, 1)) * ufl.dx

    # Angular momentum potential
    # V_m = H_{11}*m1^2 + 2*H_{12}*m1*m2 + H_{22}*m2^2
    # H_{11} = 1/(2*s1) + 1/(2*s0)
    # H_{12} = 1/(2*s0)
    # H_{22} = 1/(2*s2) + 1/(2*s0)
    if m1 != 0 or m2 != 0:
        # Regularization: the mesh is already inset from boundary,
        # but add a small floor for safety
        eps_reg = 1e-12

        V_m = ((0.5 / (s1 + eps_reg) + 0.5 / (s0 + eps_reg)) * float(m1**2)
             + 2.0 * 0.5 / (s0 + eps_reg) * float(m1 * m2)
             + (0.5 / (s2 + eps_reg) + 0.5 / (s0 + eps_reg)) * float(m2**2))

        a_pot = V_m * u * v * ufl.dx
    else:
        a_pot = fem.Constant(domain, PETSc.ScalarType(0.0)) * u * v * ufl.dx

    # Assemble LHS and mass matrix
    a_form = fem.form(a_stiff + a_pot)
    m_form = fem.form(u * v * ufl.dx)

    A = assemble_matrix(a_form)
    A.assemble()
    M = assemble_matrix(m_form)
    M.assemble()

    # SLEPc eigensolver
    eigensolver = SLEPc.EPS().create(domain.comm)
    eigensolver.setOperators(A, M)
    eigensolver.setProblemType(SLEPc.EPS.ProblemType.GHEP)
    eigensolver.setType(SLEPc.EPS.Type.KRYLOVSCHUR)
    eigensolver.setWhichEigenpairs(SLEPc.EPS.Which.SMALLEST_REAL)
    eigensolver.setDimensions(nev=num_eigs, ncv=max(3*num_eigs, 30))
    eigensolver.setTolerances(tol=1e-10, max_it=2000)

    # Shift-invert for better convergence on smallest eigenvalues
    st = eigensolver.getST()
    st.setType(SLEPc.ST.Type.SINVERT)
    st.setShift(-0.5)

    eigensolver.solve()

    nconv = eigensolver.getConverged()
    eigenvalues = []
    for i in range(min(nconv, num_eigs)):
        val = eigensolver.getEigenvalue(i)
        if hasattr(val, 'real'):
            eigval = val.real
        else:
            eigval = val
        if eigval > -0.1:
            eigenvalues.append(float(eigval))

    eigensolver.destroy()
    A.destroy()
    M.destroy()

    return sorted(eigenvalues)


# ============================================================
# Eigenvalue matching logic
# ============================================================

def match_eigenvalues(numerical_eigs_by_sector, exact_levels, max_exact=12):
    """
    Match numerical eigenvalues from all charge sectors against exact levels.

    For each exact eigenvalue lambda_{a,b}, we count how many numerical
    eigenvalues (across all sectors) fall within tolerance.

    Returns list of (exact_lam, exact_mult, num_lam_mean, num_count, rel_err).
    """
    # Flatten all numerical eigenvalues with their sector labels
    all_eigs = []
    for (m1, m2), eigs in numerical_eigs_by_sector.items():
        for e in eigs:
            all_eigs.append((e, m1, m2))
    all_eigs.sort()

    results = []
    for lam_exact, mult_exact, a, b in exact_levels[:max_exact]:
        # Find all numerical eigenvalues within 10% of this exact value
        if lam_exact < 0.01:
            # Zero eigenvalue
            nearby = [e for e, _, _ in all_eigs if abs(e) < 0.5]
        else:
            nearby = [e for e, _, _ in all_eigs
                     if abs(e - lam_exact) / lam_exact < 0.15]

        if nearby:
            num_mean = np.mean(nearby)
            num_count = len(nearby)
            if lam_exact > 0.01:
                rel_err = abs(num_mean - lam_exact) / lam_exact
            else:
                rel_err = abs(num_mean)
        else:
            num_mean = float('nan')
            num_count = 0
            rel_err = float('inf')

        results.append((lam_exact, mult_exact, a, b, num_mean, num_count, rel_err))

    return results


# ============================================================
# Main
# ============================================================

def main():
    comm = MPI.COMM_WORLD
    rank = comm.rank

    print("=" * 70)
    print("CP^2 SPECTRAL EIGENVALUE VALIDATION")
    print("Toric symplectic reduction to 2D FEM on moment polytope")
    print("=" * 70)
    print()

    # --- 4D limitation ---
    print("4D FEM STATUS:")
    cell_types = [ct.name for ct in basix.CellType]
    print(f"  basix cell types: {cell_types}")
    print(f"  Max topological dimension: 3 (tetrahedron)")
    print(f"  4-simplex (pentatope): NOT AVAILABLE")
    print(f"  => Native 4D FEM in DOLFINx is IMPOSSIBLE")
    print(f"  => Using toric reduction (CP^2 is toric)")
    print()

    # --- Exact spectrum ---
    exact = exact_spectrum(max_ab=6)
    print("EXACT CP^2 EIGENVALUES:")
    print(f"  Formula: lambda(a,b) = 2(a^2+ab+b^2+3a+3b)/3")
    print(f"  Mult:    dim V_(a,b) = (a+1)(b+1)(a+b+2)/2")
    print()
    print(f"  {'#':>3} {'lambda':>10} {'mult':>5}  SU(3) irrep(s)")
    print(f"  " + "-" * 45)
    for i, (lam, m, a, b) in enumerate(exact[:12]):
        label = f"({a},{b})+({b},{a})" if a != b else f"({a},{a})"
        frac_num = int(2*(a**2 + b**2 + a*b + 3*a + 3*b))
        print(f"  {i:3d} {lam:10.4f} {m:5d}  {label:20s}  = {frac_num}/3")
    print()

    # --- Mesh ---
    N = 30  # mesh density
    eps_inset = 0.01  # boundary inset
    print(f"Meshing moment polytope Delta (N={N}, eps={eps_inset})...")
    t0 = time.time()

    try:
        domain = create_simplex_mesh_gmsh(N, eps=eps_inset, comm=comm)
        mesh_method = "gmsh"
    except Exception as ex:
        print(f"  gmsh meshing failed ({ex}), using built-in...")
        domain = create_simplex_mesh_builtin(N, eps=eps_inset, comm=comm)
        mesh_method = "built-in structured"

    tdim = domain.topology.dim
    num_cells = domain.topology.index_map(tdim).size_global
    num_verts = domain.topology.index_map(0).size_global
    print(f"  Method: {mesh_method}")
    print(f"  Cells: {num_cells}, Vertices: {num_verts}")
    print(f"  Mesh time: {time.time()-t0:.2f}s")
    print()

    # --- Solve charge sectors ---
    # For low-lying eigenvalues, we need charges |m1|,|m2| <= max(a,b).
    # To capture eigenvalues up to (a,b) ~ (3,0), need max_charge >= 3.
    max_charge = 3
    num_eigs_per_sector = 8
    poly_order = 2

    total_sectors = (2*max_charge + 1)**2
    print(f"Solving {total_sectors} charge sectors (|m1|,|m2| <= {max_charge})...")
    print(f"  Polynomial order: {poly_order}")
    print(f"  Eigenvalues per sector: {num_eigs_per_sector}")
    print()

    all_eigs = {}
    t0 = time.time()
    failures = 0

    for m1 in range(-max_charge, max_charge + 1):
        for m2 in range(-max_charge, max_charge + 1):
            try:
                eigs = solve_charge_sector(domain, m1, m2,
                                          num_eigs=num_eigs_per_sector,
                                          poly_order=poly_order)
                all_eigs[(m1, m2)] = eigs
            except Exception as ex:
                failures += 1
                if failures <= 5:
                    print(f"  FAILED sector ({m1:+d},{m2:+d}): {ex}")

    elapsed = time.time() - t0
    print(f"  Solved {len(all_eigs)}/{total_sectors} sectors in {elapsed:.1f}s")
    if failures:
        print(f"  Failures: {failures}")
    print()

    # --- Print selected sectors ---
    print("SELECTED SECTOR RESULTS:")
    for (m1, m2) in [(0,0), (1,0), (0,1), (1,1), (2,0), (0,2), (1,-1)]:
        if (m1, m2) in all_eigs:
            eigs = all_eigs[(m1, m2)]
            eig_str = ", ".join(f"{e:.4f}" for e in eigs[:6])
            print(f"  ({m1:+d},{m2:+d}): [{eig_str}]")
    print()

    # --- Match against exact spectrum ---
    results = match_eigenvalues(all_eigs, exact, max_exact=12)

    print("EIGENVALUE COMPARISON:")
    print("=" * 70)
    print(f"  {'exact':>10} {'numerical':>10} {'rel_err':>10} "
          f"{'ex_mult':>7} {'num_cnt':>7} {'status':>8}")
    print(f"  " + "-" * 58)

    matched_5pct = 0
    matched_10pct = 0
    total = len(results)

    for lam_ex, mult_ex, a, b, num_mean, num_count, rel_err in results:
        label_ab = f"({a},{b})" if a == b else f"({a},{b})/({b},{a})"
        if np.isnan(num_mean):
            status = "MISS"
        elif rel_err < 0.02:
            status = "EXACT"
            matched_5pct += 1
            matched_10pct += 1
        elif rel_err < 0.05:
            status = "GOOD"
            matched_5pct += 1
            matched_10pct += 1
        elif rel_err < 0.10:
            status = "OK"
            matched_10pct += 1
        else:
            status = "POOR"

        if np.isnan(num_mean):
            print(f"  {lam_ex:10.4f} {'---':>10} {'---':>10} "
                  f"{mult_ex:7d} {num_count:7d} {status:>8}  {label_ab}")
        else:
            print(f"  {lam_ex:10.4f} {num_mean:10.4f} {rel_err:10.6f} "
                  f"{mult_ex:7d} {num_count:7d} {status:>8}  {label_ab}")

    print()

    # --- Detailed (0,0) sector ---
    print("DETAILED: T^2-invariant sector (m1=m2=0)")
    print("  This captures eigenvalues from irreps V_{(k,k)} (a=b diagonal).")
    if (0, 0) in all_eigs:
        eigs_00 = all_eigs[(0, 0)]
        diag_exact = [(cp2_eigenvalue(k, k), k) for k in range(6)]
        print(f"  {'exact':>10} {'numerical':>10} {'rel_err':>10} {'irrep':>8}")
        print(f"  " + "-" * 42)
        for idx, (lam_ex, k) in enumerate(diag_exact):
            if idx < len(eigs_00):
                err = abs(eigs_00[idx] - lam_ex) / max(lam_ex, 1e-10) if lam_ex > 0 else abs(eigs_00[idx])
                print(f"  {lam_ex:10.4f} {eigs_00[idx]:10.4f} {err:10.6f} ({k},{k})")
            else:
                print(f"  {lam_ex:10.4f} {'---':>10} {'---':>10} ({k},{k})")
    print()

    # --- Summary ---
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Manifold: CP^2 = SU(3)/U(2), real dim 4, complex dim 2")
    print(f"  Method:   Toric symplectic reduction -> 2D FEM on moment polytope Delta")
    print(f"  Mesh:     {num_cells} cells, {num_verts} vertices (N={N}, eps={eps_inset})")
    print(f"  FE order: P{poly_order}")
    print(f"  Sectors:  {len(all_eigs)} charge sectors, {num_eigs_per_sector} eigs each")
    print(f"  Matched:  {matched_5pct}/{total} within 5%, {matched_10pct}/{total} within 10%")
    print()

    if matched_5pct >= 6:
        print("  VERDICT: VALIDATED")
        print("  The toric reduction pipeline correctly reproduces CP^2 eigenvalues.")
    elif matched_5pct >= 3:
        print("  VERDICT: PARTIALLY VALIDATED")
        print("  Some eigenvalues match. Boundary effects or normalization may need tuning.")
    else:
        print("  VERDICT: NEEDS INVESTIGATION")
        print("  Check: metric normalization, Laplacian derivation, boundary treatment.")
    print()

    print("4D FEM ALTERNATIVES (for future reference):")
    print("  1. deal.II (C++ templates, supports arbitrary dimension)")
    print("  2. DUNE/PDELab (supports arbitrary dimension)")
    print("  3. Custom pentatope FEM (manual implementation)")
    print("  4. Toric reduction (this script) -- works for any toric manifold")
    print("  5. For dP5: also toric, same approach applies")
    print("  6. Spectral methods (Jacobi polynomials on simplex) -- avoids meshing")
    print()

    return matched_5pct, total


if __name__ == "__main__":
    main()
