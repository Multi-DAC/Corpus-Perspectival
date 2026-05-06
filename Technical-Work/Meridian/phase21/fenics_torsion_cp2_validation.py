"""
VALIDATION: Analytic torsion on CP^2 via FEniCS
================================================

Purpose: Verify our numerical spectral computation pipeline on CP^2
where eigenvalues are known analytically from SU(3) representation theory.

CP^2 = SU(3)/U(2). The scalar Laplacian eigenvalues on CP^2 with
Fubini-Study metric (Ric = 6g) are:

  lambda_{a,b} = 2(a^2 + ab + b^2 + 3a + 3b) / 3,  a,b >= 0
  multiplicity = (a+1)(b+1)(a+b+2)/2   [= dim of SU(3) irrep (a,b)]

For the UNIT CP^2 (diameter pi, Ric = 6g):
  Vol(CP^2) = pi^2 / 2

We compute via FEniCS on a triangulated mesh approximating CP^2,
then compare numerical eigenvalues to the exact formula.

Step 1: Build mesh of CP^2 via coordinate charts
Step 2: Define the Fubini-Study metric tensor
Step 3: Solve Laplacian eigenvalue problem
Step 4: Compare to exact eigenvalues
Step 5: Form spectral zeta function and compute zeta'(0)
"""

import numpy as np
from mpi4py import MPI
import dolfinx
from dolfinx import mesh, fem, default_scalar_type
from dolfinx.fem.petsc import LinearProblem
import ufl
from petsc4py import PETSc

# For eigenvalue computation
try:
    from slepc4py import SLEPc
    HAS_SLEPC = True
except ImportError:
    HAS_SLEPC = False
    print("WARNING: SLEPc not available. Cannot compute eigenvalues.")

print("=" * 60)
print("VALIDATION: Spectral computation on S^2 (CP^1)")
print("=" * 60)
print()
print("Starting with S^2 (simpler, 2D) before CP^2 (4D).")
print("S^2 eigenvalues: l(l+1), multiplicity 2l+1, l=0,1,2,...")
print()

# ============================================================
# PART 1: S^2 validation (2D — simpler test case)
# ============================================================

# Create a mesh of the unit sphere S^2
# FEniCS doesn't have a built-in sphere mesh, so we use gmsh
import subprocess
import tempfile
import os

def create_sphere_mesh(radius=1.0, resolution=0.15):
    """Create a triangulated sphere mesh using gmsh."""
    import gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.model.add("sphere")

    # Create sphere surface
    gmsh.model.occ.addSphere(0, 0, 0, radius)
    gmsh.model.occ.synchronize()

    # Get the surface entities
    surfaces = gmsh.model.getEntities(dim=2)

    # Set mesh size
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", resolution)
    gmsh.option.setNumber("Mesh.CharacteristicLengthMin", resolution * 0.5)

    # Generate 2D mesh on the surface
    gmsh.model.mesh.generate(2)

    # Extract mesh data
    node_tags, coords, _ = gmsh.model.mesh.getNodes()
    coords = coords.reshape(-1, 3)

    # Get triangle elements
    elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.getElements(dim=2)
    triangles = elem_node_tags[0].reshape(-1, 3) - 1  # 0-indexed

    # Project nodes onto sphere (ensure exact radius)
    norms = np.linalg.norm(coords, axis=1, keepdims=True)
    coords = coords * radius / norms

    gmsh.finalize()
    return coords, triangles.astype(np.int64)


def create_sphere_mesh_dolfinx(resolution=0.12):
    """Create sphere mesh directly importable by DOLFINx."""
    import gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Verbosity", 0)
    gmsh.model.add("sphere")

    # Create sphere
    gmsh.model.occ.addSphere(0, 0, 0, 1.0)
    gmsh.model.occ.synchronize()

    # Add physical group for the surface (required by DOLFINx)
    surfaces = gmsh.model.getEntities(dim=2)
    surface_tags = [s[1] for s in surfaces]
    gmsh.model.addPhysicalGroup(2, surface_tags, tag=1)
    gmsh.model.setPhysicalName(2, 1, "sphere_surface")

    # Mesh parameters
    gmsh.option.setNumber("Mesh.CharacteristicLengthMax", resolution)

    # Generate surface mesh
    gmsh.model.mesh.generate(2)

    # Import into DOLFINx
    from dolfinx.io import gmsh as gmsh_io
    mesh_data = gmsh_io.model_to_mesh(
        gmsh.model, MPI.COMM_WORLD, 0, gdim=3
    )
    gmsh.finalize()
    return mesh_data.mesh


print("Creating sphere mesh...")
msh = create_sphere_mesh_dolfinx(resolution=0.12)
print(f"  Mesh: {msh.topology.index_map(2).size_local} triangles, "
      f"{msh.topology.index_map(0).size_local} vertices")

# ============================================================
# Eigenvalue computation on S^2
# ============================================================

# The Laplace-Beltrami operator on S^2 embedded in R^3
# For a surface mesh in R^3, DOLFINx handles the intrinsic geometry

V = fem.functionspace(msh, ("Lagrange", 2))  # quadratic elements
print(f"  Function space: {V.dofmap.index_map.size_local} DOFs")

# Define variational forms for the eigenvalue problem:
# Find (u, lambda) such that: integral grad(u).grad(v) = lambda * integral u*v
u = ufl.TrialFunction(V)
v = ufl.TestFunction(V)

# Stiffness matrix (Laplacian)
a = ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx
# Mass matrix
m = ufl.inner(u, v) * ufl.dx

# Assemble matrices
A = fem.petsc.assemble_matrix(fem.form(a))
A.assemble()
M = fem.petsc.assemble_matrix(fem.form(m))
M.assemble()

if HAS_SLEPC:
    print("\nSolving eigenvalue problem on S^2...")

    # Set up SLEPc eigensolver
    eigensolver = SLEPc.EPS().create(MPI.COMM_WORLD)
    eigensolver.setOperators(A, M)
    eigensolver.setProblemType(SLEPc.EPS.ProblemType.GHEP)
    eigensolver.setType(SLEPc.EPS.Type.KRYLOVSCHUR)
    eigensolver.setWhichEigenpairs(SLEPc.EPS.Which.SMALLEST_MAGNITUDE)

    # Request enough eigenvalues to cover l=0,...,10
    # Total eigenvalues up to l=10: sum_{l=0}^{10} (2l+1) = 121
    n_eigs = 150
    eigensolver.setDimensions(nev=n_eigs)
    eigensolver.setTolerances(tol=1e-10)

    eigensolver.solve()

    nconv = eigensolver.getConverged()
    print(f"  Converged eigenvalues: {nconv}")

    eigenvalues = []
    for i in range(min(nconv, n_eigs)):
        eigval = eigensolver.getEigenvalue(i)
        eigenvalues.append(eigval.real)

    eigenvalues = np.array(sorted(eigenvalues))

    # Compare to exact S^2 eigenvalues: l(l+1), mult 2l+1
    print("\n  Comparison to exact S^2 eigenvalues:")
    print(f"  {'l':>3} {'Exact':>10} {'Numerical':>12} {'Mult(exact)':>11} {'Count':>6} {'Rel.Err':>10}")
    print("  " + "-" * 60)

    idx = 0
    for l in range(11):
        exact = l * (l + 1)
        mult = 2 * l + 1

        # Find numerical eigenvalues near this exact value
        if exact == 0:
            # l=0: eigenvalue 0, multiplicity 1
            count = 1  # The constant mode
            if len(eigenvalues) > 0:
                num_val = eigenvalues[0]
            else:
                num_val = float('nan')
        else:
            # Find cluster near exact value
            tol_cluster = max(0.5, 0.1 * exact)
            cluster = eigenvalues[np.abs(eigenvalues - exact) < tol_cluster]
            count = len(cluster)
            num_val = np.mean(cluster) if count > 0 else float('nan')

        if not np.isnan(num_val) and exact > 0:
            rel_err = abs(num_val - exact) / exact
        else:
            rel_err = float('nan')

        print(f"  {l:3d} {exact:10.4f} {num_val:12.4f} {mult:11d} {count:6d} {rel_err:10.2e}")

    # ============================================================
    # Spectral zeta function from numerical eigenvalues
    # ============================================================

    print("\n  Spectral zeta function test:")
    # zeta(s) = sum_{lambda > 0} lambda^{-s}
    # For S^2: zeta(0) = -2/3 (known exactly)

    pos_eigs = eigenvalues[eigenvalues > 1e-8]
    print(f"  Non-zero eigenvalues: {len(pos_eigs)}")

    # Compute zeta(s) for several s values
    for s_val in [2.0, 3.0, 5.0]:
        zeta_num = np.sum(pos_eigs ** (-s_val))
        # Exact: sum_{l=1}^{lmax} (2l+1) / [l(l+1)]^s
        lmax = 50
        zeta_exact = sum((2*l+1) / (l*(l+1))**s_val for l in range(1, lmax+1))
        print(f"  zeta({s_val}): numerical={zeta_num:.6f}, exact(l<={lmax})={zeta_exact:.6f}")

    print("\n  Pipeline validation complete.")
    print("  If eigenvalues match, the FEniCS spectral pipeline is working.")
    print("  Next step: extend to CP^2 (4D) and then to dP_5 with gauge bundles.")

else:
    print("\nSLEPc not available — cannot compute eigenvalues.")
    print("Install: conda install -c conda-forge slepc4py")

print("\n" + "=" * 60)
print("END VALIDATION")
print("=" * 60)
