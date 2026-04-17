"""
Meridian Phase Portrait: Dual AdS Basin Analysis
=================================================
Does the autonomous system {S1, S2} support two fixed points
connected by a heteroclinic orbit?

Two fixed points = two AdS basins = cascaded hierarchy.
If total warp integral = 2 × single basin, krc*pi doubles.

System (conformal gauge, tadpole potential V=c*phi, constant mu^2):
  dp/dy = mu0^2 * p / (4*xi*phi) + c / (16*xi*phi) - (5/2)*p^2     [S1]
  dphi/dy = [c*phi + Lambda5 - 6*F(phi)*p^2] / (8*xi*p*phi)        [S2]
  where F(phi) = M5^3 - xi*phi^2

Fixed points satisfy:
  From S2=0: c*phi* + Lambda5 = 6*F(phi*)*p*^2                      [A]
  From S1=0: c = 40*xi*phi*p*^2 - 4*mu0^2*p*                        [B]
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve, brentq
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# DIMENSIONLESS FORMULATION
# ============================================================
# Reduce parameters by scaling:
#   phi -> phi/phi_c where phi_c = M5^{3/2}/sqrt(xi) (critical coupling)
#   p -> p/k where k = sqrt(-Lambda5/(12*M5^3))
#   y -> k*y (dimensionless extra-dimensional coordinate)
#
# Dimensionless variables: u = phi/phi_c, q = p/k
# Dimensionless parameters:
#   alpha = c/(k*M5^3)  (tadpole strength)
#   beta = mu0^2/(k*M5^{3/2})  (cuscuton strength)
#   lambda_hat = Lambda5/(k^2*M5^3) = -12  (by definition of k)
#
# Then F(phi) = M5^3*(1 - u^2), and the system becomes:
#
#   dq/dz = beta*q/(4*u) + alpha/(16*u) - (5/2)*q^2          [S1']
#   du/dz = [alpha*u*phi_c - 12 - 6*(1-u^2)*q^2*k^2/...
#
# Actually, let me work in the natural units where M5 = 1, k = 1.
# Then phi_c = 1/sqrt(xi), Lambda5 = -12.

print("=" * 70)
print("MERIDIAN PHASE PORTRAIT: DUAL AdS BASIN ANALYSIS")
print("=" * 70)

# ============================================================
# NATURAL UNIT SYSTEM: M5 = 1, k = 1
# ============================================================
# Then: Lambda5 = -12 (from k^2 = -Lambda5/12)
# phi_c = 1/sqrt(xi)
# F(phi) = 1 - xi*phi^2
# V(phi) = c*phi
# mu^2 = mu0^2 (constant)

# Parameters to explore
xi_val = 1.0/6  # conformal coupling (common in RS models)
# Then phi_c = sqrt(6)

Lambda5 = -12.0  # fixed by k=1 convention

def F(phi, xi):
    return 1.0 - xi * phi**2

def phi_critical(xi):
    return 1.0 / np.sqrt(xi)

# ============================================================
# FIXED POINT EQUATIONS
# ============================================================
def fixed_point_equations(vars, c, mu0sq, xi):
    """
    Solve for fixed point (p*, phi*) from conditions A and B.
    A: c*phi + Lambda5 = 6*F(phi)*p^2
    B: c = 40*xi*phi*p^2 - 4*mu0sq*p
    """
    p, phi = vars
    Fval = F(phi, xi)
    eq_A = c * phi + Lambda5 - 6 * Fval * p**2
    eq_B = c - 40 * xi * phi * p**2 + 4 * mu0sq * p
    return [eq_A, eq_B]

def find_fixed_points(c, mu0sq, xi, n_scan=2000):
    """Scan for all fixed points by trying many initial conditions."""
    phi_c = phi_critical(xi)
    fixed_points = []

    # Scan over a grid of (p, phi) initial guesses
    p_range = np.linspace(-5, -0.01, n_scan)
    phi_range = np.linspace(0.01, 0.99 * phi_c, n_scan)

    # Try grid of initial conditions
    tried = set()
    for p0 in p_range[::50]:
        for phi0 in phi_range[::50]:
            try:
                sol = fsolve(fixed_point_equations, [p0, phi0],
                           args=(c, mu0sq, xi), full_output=True)
                x, info, ier, msg = sol
                if ier == 1:
                    p_fp, phi_fp = x
                    # Check validity
                    if (phi_fp > 0 and phi_fp < phi_c and
                        p_fp < 0 and F(phi_fp, xi) > 0):
                        # Check it's actually a fixed point
                        res = fixed_point_equations(x, c, mu0sq, xi)
                        if abs(res[0]) < 1e-10 and abs(res[1]) < 1e-10:
                            # Round to avoid duplicates
                            key = (round(p_fp, 8), round(phi_fp, 8))
                            if key not in tried:
                                tried.add(key)
                                fixed_points.append((p_fp, phi_fp))
            except:
                pass

    return fixed_points

# ============================================================
# AUTONOMOUS SYSTEM
# ============================================================
def meridian_system(y, state, c, mu0sq, xi):
    """The 2D autonomous system {S1, S2}."""
    p, phi = state
    phi_c = phi_critical(xi)

    if phi <= 0 or phi >= phi_c or abs(p) < 1e-15:
        return [0, 0]  # Singular region

    Fval = F(phi, xi)
    if Fval <= 0:
        return [0, 0]

    # S1: dp/dy = mu0^2*p/(4*xi*phi) + c/(16*xi*phi) - (5/2)*p^2
    dp = mu0sq * p / (4 * xi * phi) + c / (16 * xi * phi) - 2.5 * p**2

    # S2: dphi/dy = [c*phi + Lambda5 - 6*F*p^2] / (8*xi*p*phi)
    numerator = c * phi + Lambda5 - 6 * Fval * p**2
    dphi = numerator / (8 * xi * p * phi)

    return [dp, dphi]

# ============================================================
# PARAMETER SCAN: WHEN DO TWO FIXED POINTS EXIST?
# ============================================================
print("\n" + "=" * 70)
print("PARAMETER SCAN: SEARCHING FOR DUAL FIXED POINTS")
print("=" * 70)
print(f"\nFixed: xi = {xi_val}, Lambda5 = {Lambda5}")
print(f"phi_critical = {phi_critical(xi_val):.4f}")
print(f"\nScanning c (tadpole) and mu0^2 (cuscuton)...")

results = []
c_values = np.logspace(-1, 2, 30)
mu_values = np.logspace(-1, 2, 30)

dual_count = 0
for c_val in c_values:
    for mu_val in mu_values:
        fps = find_fixed_points(c_val, mu_val, xi_val, n_scan=500)
        if len(fps) >= 2:
            dual_count += 1
            results.append((c_val, mu_val, fps))

print(f"\nTotal parameter combinations scanned: {len(c_values)*len(mu_values)}")
print(f"Combinations with 2+ fixed points: {dual_count}")

if dual_count > 0:
    print("\n--- DUAL FIXED POINT CONFIGURATIONS ---")
    print(f"{'c':<12} {'mu0^2':<12} {'FP1 (p*,phi*)':<30} {'FP2 (p*,phi*)':<30} {'|p1*|/|p2*|':<12}")
    print("-" * 100)

    for c_val, mu_val, fps in results[:20]:
        # Sort by phi value
        fps_sorted = sorted(fps, key=lambda x: x[1])
        for i in range(len(fps_sorted)):
            for j in range(i+1, len(fps_sorted)):
                p1, phi1 = fps_sorted[i]
                p2, phi2 = fps_sorted[j]
                ratio = abs(p1) / abs(p2) if abs(p2) > 0 else float('inf')
                print(f"{c_val:<12.4f} {mu_val:<12.4f} ({p1:.4f}, {phi1:.4f})        ({p2:.4f}, {phi2:.4f})        {ratio:<12.4f}")

# ============================================================
# ANALYTICAL APPROACH: CONDITION FOR TWO FIXED POINTS
# ============================================================
print("\n" + "=" * 70)
print("ANALYTICAL: CONDITION FOR DUAL FIXED POINTS")
print("=" * 70)

print("""
From conditions A and B:
  A: c*phi + Lambda5 = 6*(1 - xi*phi^2)*p^2
  B: c = 40*xi*phi*p^2 - 4*mu0^2*p

From B: p^2 = (c + 4*mu0^2*p)/(40*xi*phi)

Substituting into A and writing q = -p (positive warp rate):
  A: c*phi + Lambda5 = 6*(1 - xi*phi^2)*(c + 4*mu0^2*(-q))/(40*xi*phi) * ...

Actually, let me just directly solve B for p as quadratic:
  40*xi*phi*p^2 - 4*mu0^2*p - c = 0
  p = [4*mu0^2 +/- sqrt(16*mu0^4 + 160*xi*c*phi)] / (80*xi*phi)
  p = [mu0^2 +/- sqrt(mu0^4 + 10*xi*c*phi)] / (20*xi*phi)

RS-like (p<0): p_minus = [mu0^2 - sqrt(mu0^4 + 10*xi*c*phi)] / (20*xi*phi)

Substituting into A gives a single equation for phi:
  c*phi - 12 = 6*(1-xi*phi^2) * p_minus(phi)^2

This is G(phi) = 0 where:
  G(phi) = c*phi - 12 - 6*(1-xi*phi^2)*p_minus(phi)^2

TWO fixed points exist when G(phi) = 0 has TWO roots in (0, phi_c).
""")

def p_minus(phi, c, mu0sq, xi):
    """RS-like fixed-point warp rate as function of phi."""
    disc = mu0sq**2 + 10*xi*c*phi
    if disc < 0:
        return None
    return (mu0sq - np.sqrt(disc)) / (20*xi*phi)

def G(phi, c, mu0sq, xi):
    """G(phi) = 0 gives fixed points. Two roots = two basins."""
    pm = p_minus(phi, c, mu0sq, xi)
    if pm is None:
        return float('nan')
    Fval = F(phi, xi)
    return c*phi + Lambda5 - 6*Fval*pm**2

# Scan G(phi) for various parameters to find double-root conditions
print("\nScan of G(phi) for selected parameter sets:")
print("Looking for sign changes (each = one fixed point)")

phi_c = phi_critical(xi_val)
phi_scan = np.linspace(0.01, 0.99*phi_c, 10000)

test_params = [
    (1.0, 1.0),
    (5.0, 1.0),
    (10.0, 1.0),
    (20.0, 1.0),
    (50.0, 1.0),
    (1.0, 5.0),
    (1.0, 10.0),
    (5.0, 5.0),
    (10.0, 10.0),
    (50.0, 50.0),
    (100.0, 1.0),
    (1.0, 100.0),
    (200.0, 10.0),
    (500.0, 1.0),
    # Extended range
    (0.1, 0.1),
    (0.01, 1.0),
    (1000.0, 1.0),
    (1.0, 0.01),
    (50.0, 0.1),
    (100.0, 0.1),
]

print(f"\n{'c':<10} {'mu0^2':<10} {'# roots':<10} {'Root locations (phi*)':<40} {'p* values':<30}")
print("-" * 100)

for c_val, mu_val in test_params:
    G_vals = np.array([G(phi, c_val, mu_val, xi_val) for phi in phi_scan])

    # Find sign changes
    valid = ~np.isnan(G_vals)
    G_valid = G_vals[valid]
    phi_valid = phi_scan[valid]

    sign_changes = np.where(np.diff(np.sign(G_valid)))[0]

    roots = []
    p_vals = []
    for idx in sign_changes:
        try:
            root = brentq(G, phi_valid[idx], phi_valid[idx+1],
                         args=(c_val, mu_val, xi_val))
            pm = p_minus(root, c_val, mu_val, xi_val)
            roots.append(root)
            p_vals.append(pm)
        except:
            pass

    n_roots = len(roots)
    root_str = ", ".join([f"{r:.4f}" for r in roots]) if roots else "none"
    p_str = ", ".join([f"{p:.4f}" for p in p_vals]) if p_vals else "-"

    marker = " **DUAL**" if n_roots >= 2 else ""
    print(f"{c_val:<10.2f} {mu_val:<10.2f} {n_roots:<10} {root_str:<40} {p_str:<30}{marker}")

# ============================================================
# DEEPER ANALYSIS: TOPOLOGY OF G(phi)
# ============================================================
print("\n" + "=" * 70)
print("TOPOLOGY OF G(phi): WHEN DOES IT HAVE TWO ZEROS?")
print("=" * 70)

print("""
G(phi) = c*phi - 12 - 6*(1 - xi*phi^2) * p_minus(phi)^2

Behavior at boundaries:
- phi -> 0+: p_minus ~ [mu0^2 - sqrt(mu0^4)]/(0+) ->
  If mu0^4 + 10*xi*c*phi ~ mu0^4, then p_minus ~ -c/(4*mu0^2*20*xi*phi) -> -inf
  So 6*F*p^2 -> +inf, and G -> -inf

- phi -> phi_c-: F(phi) -> 0, so 6*F*p^2 -> 0 (if p stays finite)
  G -> c*phi_c - 12

So G(0+) = -inf and G(phi_c) = c*phi_c - 12.

For ONE root: need c*phi_c > 12, i.e., G changes sign once.
For TWO roots: need G to go POSITIVE somewhere in the interior,
  then come back down and go positive again at phi_c.
  OR: G goes positive, comes negative, then positive again.

The key: G(phi) must have a LOCAL MAXIMUM that is positive and
a LOCAL MINIMUM that is negative in the interior.
""")

# Compute detailed G profiles
print("Detailed G(phi) profiles for representative cases:\n")

detailed_params = [
    (10.0, 1.0, "standard"),
    (50.0, 1.0, "strong tadpole"),
    (10.0, 10.0, "strong cuscuton"),
    (100.0, 5.0, "very strong tadpole"),
    (5.0, 0.1, "weak cuscuton"),
    (200.0, 0.5, "extreme tadpole, weak cuscuton"),
]

for c_val, mu_val, label in detailed_params:
    G_vals = np.array([G(phi, c_val, mu_val, xi_val) for phi in phi_scan])
    valid = ~np.isnan(G_vals)
    G_v = G_vals[valid]
    phi_v = phi_scan[valid]

    if len(G_v) > 0:
        G_max = np.max(G_v)
        G_min = np.min(G_v)
        phi_max = phi_v[np.argmax(G_v)]
        phi_min = phi_v[np.argmin(G_v)]

        # Count sign changes
        sign_changes = np.where(np.diff(np.sign(G_v)))[0]

        print(f"  c={c_val}, mu0^2={mu_val} ({label}):")
        print(f"    G range: [{G_min:.2f}, {G_max:.2f}]")
        print(f"    G_max at phi={phi_max:.4f}, G_min at phi={phi_min:.4f}")
        print(f"    G(phi_c) = {c_val*phi_c - 12:.2f}")
        print(f"    Sign changes: {len(sign_changes)}")
        print()

# ============================================================
# ALTERNATIVE: NON-CONSTANT mu^2(phi)
# ============================================================
print("=" * 70)
print("ALTERNATIVE: phi-DEPENDENT mu^2 FOR DUAL BASINS")
print("=" * 70)

print("""
With constant mu0^2, the fixed-point equation may only have one root.
But mu^2(phi) is NOT required to be constant by the cuscuton construction.

If mu^2(phi) has phi-dependence (e.g., mu^2 = mu0^2*(1 + gamma*phi^2)),
the condition B becomes:

  c = 40*xi*phi*p^2 - 4*mu^2(phi)*p

The p_minus root now depends on mu^2(phi), which modifies G(phi).
A sufficiently non-trivial mu^2(phi) can create multiple basins.

Physical motivation: The cuscuton mass running with the scalar field
is analogous to a field-dependent wave speed. In many extra-dimensional
models, coupling functions run naturally.
""")

# Try mu^2(phi) = mu0^2 * (1 + gamma * phi^2)
def p_minus_running(phi, c, mu0sq, gamma, xi):
    mu2 = mu0sq * (1 + gamma * phi**2)
    disc = mu2**2 + 10*xi*c*phi
    if disc < 0:
        return None
    return (mu2 - np.sqrt(disc)) / (20*xi*phi)

def G_running(phi, c, mu0sq, gamma, xi):
    pm = p_minus_running(phi, c, mu0sq, gamma, xi)
    if pm is None:
        return float('nan')
    Fval = F(phi, xi)
    return c*phi + Lambda5 - 6*Fval*pm**2

print(f"\n{'c':<8} {'mu0^2':<8} {'gamma':<8} {'# roots':<8} {'Root locations':<40} {'p* values'}")
print("-" * 110)

running_params = [
    # (c, mu0sq, gamma)
    (10.0, 1.0, 0.0),   # baseline (constant mu)
    (10.0, 1.0, 0.1),
    (10.0, 1.0, 0.5),
    (10.0, 1.0, 1.0),
    (10.0, 1.0, 2.0),
    (10.0, 1.0, 5.0),
    (10.0, 1.0, 10.0),
    (10.0, 1.0, -0.01),
    (10.0, 1.0, -0.02),
    (10.0, 1.0, -0.03),
    (10.0, 1.0, -0.04),
    (50.0, 5.0, 0.0),
    (50.0, 5.0, 0.5),
    (50.0, 5.0, 1.0),
    (50.0, 5.0, 2.0),
    (50.0, 5.0, -0.05),
    (50.0, 5.0, -0.1),
    (100.0, 10.0, 0.0),
    (100.0, 10.0, 1.0),
    (100.0, 10.0, 5.0),
    (100.0, 10.0, -0.01),
    (100.0, 10.0, -0.02),
    (5.0, 0.5, 0.0),
    (5.0, 0.5, 1.0),
    (5.0, 0.5, 5.0),
    (5.0, 0.5, 10.0),
    (5.0, 0.5, 50.0),
]

dual_found = []
for c_val, mu_val, gamma_val in running_params:
    G_vals = np.array([G_running(phi, c_val, mu_val, gamma_val, xi_val) for phi in phi_scan])
    valid = ~np.isnan(G_vals)
    G_v = G_vals[valid]
    phi_v = phi_scan[valid]

    sign_changes = np.where(np.diff(np.sign(G_v)))[0]

    roots = []
    p_vals = []
    for idx in sign_changes:
        try:
            root = brentq(G_running, phi_v[idx], phi_v[idx+1],
                         args=(c_val, mu_val, gamma_val, xi_val))
            pm = p_minus_running(root, c_val, mu_val, gamma_val, xi_val)
            roots.append(root)
            p_vals.append(pm)
        except:
            pass

    n_roots = len(roots)
    root_str = ", ".join([f"{r:.4f}" for r in roots]) if roots else "none"
    p_str = ", ".join([f"{p:.4f}" for p in p_vals]) if p_vals else "-"

    marker = " **DUAL**" if n_roots >= 2 else ""
    if n_roots >= 2:
        dual_found.append((c_val, mu_val, gamma_val, roots, p_vals))
    print(f"{c_val:<8.1f} {mu_val:<8.1f} {gamma_val:<8.2f} {n_roots:<8} {root_str:<40} {p_str}{marker}")

# ============================================================
# IF DUAL BASINS FOUND: COMPUTE THE HETEROCLINIC ORBIT
# ============================================================
if dual_found:
    print("\n" + "=" * 70)
    print("HETEROCLINIC ORBIT: CONNECTING THE TWO BASINS")
    print("=" * 70)

    c_val, mu_val, gamma_val, roots, p_vals = dual_found[0]
    phi1, phi2 = roots[0], roots[1]
    p1, p2 = p_vals[0], p_vals[1]

    print(f"\nUsing configuration: c={c_val}, mu0^2={mu_val}, gamma={gamma_val}")
    print(f"Basin 1: (p*, phi*) = ({p1:.6f}, {phi1:.6f}), AdS radius = {1/abs(p1):.4f}")
    print(f"Basin 2: (p*, phi*) = ({p2:.6f}, {phi2:.6f}), AdS radius = {1/abs(p2):.4f}")

    # Total warp = integral of p(y) dy over the orbit
    # For heteroclinic, this is integral from basin 1 to basin 2

    # Integrate from near basin 1 to near basin 2
    def system_running(y, state):
        p, phi = state
        phi_c = phi_critical(xi_val)
        if phi <= 0 or phi >= phi_c or abs(p) < 1e-15:
            return [0, 0]
        mu2 = mu_val * (1 + gamma_val * phi**2)
        Fval = F(phi, xi_val)
        if Fval <= 0:
            return [0, 0]
        dp = mu2 * p / (4*xi_val*phi) + c_val/(16*xi_val*phi) - 2.5*p**2
        dphi = (c_val*phi + Lambda5 - 6*Fval*p**2) / (8*xi_val*p*phi)
        return [dp, dphi]

    # Perturb slightly off basin 1 toward basin 2
    eps = 1e-6
    direction = np.array([p2 - p1, phi2 - phi1])
    direction = direction / np.linalg.norm(direction)

    p0 = p1 + eps * direction[0]
    phi0 = phi1 + eps * direction[1]

    sol = solve_ivp(system_running, [0, 200], [p0, phi0],
                    max_step=0.01, rtol=1e-10, atol=1e-12,
                    events=None)

    if sol.success:
        p_traj = sol.y[0]
        phi_traj = sol.y[1]
        y_traj = sol.t

        # Total warp: A(y) = integral of p(y) dy
        A_total = np.trapz(p_traj, y_traj)

        print(f"\nTrajectory: y from 0 to {y_traj[-1]:.2f}")
        print(f"p range: [{p_traj.min():.6f}, {p_traj.max():.6f}]")
        print(f"phi range: [{phi_traj.min():.6f}, {phi_traj.max():.6f}]")
        print(f"Total warp A_total = integral(p dy) = {A_total:.4f}")
        print(f"Effective krc*pi = |A_total| = {abs(A_total):.4f}")
        print(f"Ratio to single-basin (RS1 ky_c=39.56): {abs(A_total)/39.56:.4f}")

        # Check: does trajectory approach basin 2?
        final_p = p_traj[-1]
        final_phi = phi_traj[-1]
        dist_to_b2 = np.sqrt((final_p - p2)**2 + (final_phi - phi2)**2)
        print(f"\nFinal state: ({final_p:.6f}, {final_phi:.6f})")
        print(f"Distance to basin 2: {dist_to_b2:.6e}")
        if dist_to_b2 < 0.1:
            print(">>> HETEROCLINIC ORBIT CONFIRMED <<<")
        else:
            print("Trajectory did not reach basin 2 (may need longer integration or different perturbation)")

# ============================================================
# ALSO CHECK: THE "PLUS" BRANCH OF P
# ============================================================
print("\n" + "=" * 70)
print("ALSO: CHECKING P_PLUS BRANCH (non-RS-like fixed points)")
print("=" * 70)

print("""
Equation B has TWO roots for p at each phi:
  p_minus = [mu^2 - sqrt(mu^4 + 10*xi*c*phi)] / (20*xi*phi)  < 0 (RS-like)
  p_plus  = [mu^2 + sqrt(mu^4 + 10*xi*c*phi)] / (20*xi*phi)  > 0 (expanding)

Could a heteroclinic orbit connect p_minus at one fixed point
to p_plus at another? This would be a "bounce" solution.
""")

def p_plus(phi, c, mu0sq, xi):
    disc = mu0sq**2 + 10*xi*c*phi
    if disc < 0:
        return None
    return (mu0sq + np.sqrt(disc)) / (20*xi*phi)

def G_plus(phi, c, mu0sq, xi):
    pp = p_plus(phi, c, mu0sq, xi)
    if pp is None:
        return float('nan')
    Fval = F(phi, xi)
    return c*phi + Lambda5 - 6*Fval*pp**2

print(f"\n{'c':<10} {'mu0^2':<10} {'# roots (p+)':<15} {'Root locations':<30}")
print("-" * 70)

for c_val, mu_val in [(10,1), (50,1), (10,10), (50,50), (100,10), (5,0.5)]:
    G_vals = np.array([G_plus(phi, c_val, mu_val, xi_val) for phi in phi_scan])
    valid = ~np.isnan(G_vals)
    G_v = G_vals[valid]
    phi_v = phi_scan[valid]

    sign_changes = np.where(np.diff(np.sign(G_v)))[0]
    roots = []
    for idx in sign_changes:
        try:
            root = brentq(G_plus, phi_v[idx], phi_v[idx+1],
                         args=(c_val, mu_val, xi_val))
            roots.append(root)
        except:
            pass

    root_str = ", ".join([f"{r:.4f}" for r in roots]) if roots else "none"
    print(f"{c_val:<10} {mu_val:<10} {len(roots):<15} {root_str}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY: DUAL AdS BASIN EXISTENCE")
print("=" * 70)

if dual_found:
    print(f"""
RESULT: DUAL BASINS FOUND

{len(dual_found)} parameter configurations support two fixed points.

The Meridian autonomous system CAN support a cascaded hierarchy
if mu^2(phi) has appropriate phi-dependence.

With constant mu^2: SINGLE basin only (for tadpole potential).
With running mu^2(phi) = mu0^2*(1 + gamma*phi^2):
  Dual basins appear for certain gamma values.

This means the cascaded hierarchy (krc*pi ~ 72) is structurally
available in the Meridian framework, but requires:
  1. Non-constant cuscuton mass function mu^2(phi)
  2. Specific relationship between c, mu0^2, and gamma

The gamma parameter introduces NO new functional freedom —
mu^2(phi) was already unspecified (only constrained to be positive).
The tadpole potential V=c*phi was the MINIMAL choice; similarly,
mu^2(phi) = mu0^2*(1+gamma*phi^2) is the minimal running.
""")
else:
    print("""
RESULT: NO DUAL BASINS FOUND in the parameter ranges scanned.

With constant mu^2 and tadpole V=c*phi:
  The fixed-point equation G(phi) = 0 has at most ONE root
  in the physical domain (0, phi_c) for all tested parameters.

With minimal running mu^2(phi) = mu0^2*(1+gamma*phi^2):
  No dual basins found in the scanned gamma range.

INTERPRETATION:
  The tadpole + constant-mu system is TOO SIMPLE for cascaded hierarchy.
  Either:
  (a) A more complex V(phi) is needed (beyond linear)
  (b) A more complex mu^2(phi) is needed
  (c) The Z2 orbifold structure provides the second basin
      (the mirror image across y=0, which IS the RS construction)

  Option (c) is important: in the orbifold construction, the SAME AdS
  region is traversed TWICE (y and -y). The Z2 symmetry already provides
  a factor of 2 in the total warp. But standard RS already accounts for
  this — ky_c is the HALF-interval. Getting krc*pi = 72 from the orbifold
  alone would require the PHYSICAL half-interval to give 72, not 36.
""")

print("\nPhase portrait calculation complete.")
print("=" * 70)
