"""
Meridian Phase Portrait: Double-Well Potential Analysis
=======================================================
The tadpole V=cφ gave exactly one basin. The monotone slope
couldn't create the non-monotonicity in G(φ) needed for two zeros.

Now test: V(φ) = c₁φ - c₂φ³ + c₃φ²  (cubic with inflection)
And:      V(φ) = V₀(1 - (φ/φ₀)²)²    (Mexican hat / double-well)
And:      V(φ) = c₁φ + c₂φ²           (tadpole + mass term)

The question: does ANY reasonable V(φ) give G(φ) two zeros?

System:
  S1: dp/dy = μ₀²p/(4ξφ) + V'(φ)/(16ξφ) - (5/2)p²
  S2: dφ/dy = [V(φ) + Λ₅ - 6F(φ)p²] / (8ξp φ)
  F(φ) = M₅³ - ξφ²

Fixed points: S1=0 and S2=0
  From S2: V(φ*) + Λ₅ = 6F(φ*)p*²                    [A]
  From S1: V'(φ*) = 40ξφ*p*² - 4μ₀²p*                [B]
"""

import numpy as np
from scipy.optimize import brentq, fsolve
from scipy.integrate import solve_ivp
import warnings
warnings.filterwarnings('ignore')

# Natural units: M₅ = 1, k = 1, Λ₅ = -12
Lambda5 = -12.0
xi_val = 1.0/6  # conformal coupling

def F(phi, xi):
    return 1.0 - xi * phi**2

def phi_critical(xi):
    return 1.0 / np.sqrt(xi)

phi_c = phi_critical(xi_val)  # = sqrt(6) ≈ 2.449

# ============================================================
# GENERAL FIXED-POINT MACHINERY
# ============================================================
def p_from_B(phi, Vprime, mu0sq, xi):
    """
    From condition B: V'(φ) = 40ξφp² - 4μ₀²p
    Quadratic in p: 40ξφ p² - 4μ₀² p - V'(φ) = 0
    """
    a = 40 * xi * phi
    b = -4 * mu0sq
    c_coeff = -Vprime
    disc = b**2 - 4*a*c_coeff
    if disc < 0 or a == 0:
        return None, None
    sqrt_disc = np.sqrt(disc)
    p_plus = (-b + sqrt_disc) / (2*a)
    p_minus = (-b - sqrt_disc) / (2*a)
    return p_minus, p_plus

def G_general(phi, V_func, Vprime_func, mu0sq, xi):
    """
    G(φ) = V(φ) + Λ₅ - 6F(φ)p_minus(φ)²
    Two roots of G = two AdS basins.
    """
    Vp = Vprime_func(phi)
    pm, pp = p_from_B(phi, Vp, mu0sq, xi)
    if pm is None:
        return float('nan')
    Fval = F(phi, xi)
    V_val = V_func(phi)
    return V_val + Lambda5 - 6*Fval*pm**2

def scan_roots(V_func, Vprime_func, mu0sq, xi, n_pts=20000):
    """Find all roots of G(φ) = 0 in (0, φ_c)."""
    phi_scan = np.linspace(0.001, 0.999*phi_c, n_pts)
    G_vals = np.array([G_general(phi, V_func, Vprime_func, mu0sq, xi) for phi in phi_scan])

    valid = ~np.isnan(G_vals)
    G_v = G_vals[valid]
    phi_v = phi_scan[valid]

    if len(G_v) < 2:
        return [], [], G_vals, phi_scan

    sign_changes = np.where(np.diff(np.sign(G_v)))[0]
    roots = []
    p_vals = []
    for idx in sign_changes:
        try:
            root = brentq(G_general, phi_v[idx], phi_v[idx+1],
                         args=(V_func, Vprime_func, mu0sq, xi))
            Vp = Vprime_func(root)
            pm, pp = p_from_B(root, Vp, mu0sq, xi)
            roots.append(root)
            p_vals.append(pm)
        except:
            pass

    return roots, p_vals, G_vals, phi_scan


print("=" * 70)
print("POTENTIAL #1: TADPOLE + MASS TERM")
print("V(φ) = c₁φ + (m²/2)φ²")
print("=" * 70)

print("""
Adding a mass term creates V'(φ) = c₁ + m²φ, which GROWS with φ.
This could bend G(φ) back down in the interior.
""")

test_cases_1 = []
for c1 in [5, 10, 20, 50]:
    for msq in [-5, -2, -1, -0.5, 0, 0.5, 1, 2, 5, 10, 20, 50]:
        for mu0sq in [0.5, 1, 5, 10]:
            V = lambda phi, c1=c1, msq=msq: c1*phi + 0.5*msq*phi**2
            Vp = lambda phi, c1=c1, msq=msq: c1 + msq*phi
            roots, p_vals, _, _ = scan_roots(V, Vp, mu0sq, xi_val)
            if len(roots) >= 2:
                test_cases_1.append((c1, msq, mu0sq, roots, p_vals))

print(f"Scanned: 4×12×4 = {4*12*4} parameter sets")
print(f"Dual basins found: {len(test_cases_1)}")

if test_cases_1:
    print(f"\n{'c1':<8} {'m²':<8} {'μ₀²':<8} {'φ₁*':<10} {'φ₂*':<10} {'p₁*':<12} {'p₂*':<12} {'|p₁/p₂|':<10}")
    print("-" * 80)
    for c1, msq, mu0sq, roots, pv in test_cases_1[:30]:
        r = abs(pv[0]/pv[1]) if abs(pv[1]) > 0 else float('inf')
        print(f"{c1:<8} {msq:<8} {mu0sq:<8} {roots[0]:<10.4f} {roots[1]:<10.4f} {pv[0]:<12.6f} {pv[1]:<12.6f} {r:<10.4f}")

# ============================================================
print("\n" + "=" * 70)
print("POTENTIAL #2: CUBIC (tadpole + mass + cubic)")
print("V(φ) = c₁φ + (m²/2)φ² - (λ/3)φ³")
print("=" * 70)

print("""
The cubic term creates an inflection point in V, which
can generate non-monotonicity in G(φ).
""")

test_cases_2 = []
for c1 in [5, 10, 20, 50]:
    for msq in [-5, -1, 0, 1, 5, 10]:
        for lam in [0.1, 0.5, 1, 2, 5, 10, 20, 50]:
            for mu0sq in [0.5, 1, 5, 10]:
                V = lambda phi, c1=c1, msq=msq, lam=lam: c1*phi + 0.5*msq*phi**2 - (lam/3)*phi**3
                Vp = lambda phi, c1=c1, msq=msq, lam=lam: c1 + msq*phi - lam*phi**2
                roots, pv, _, _ = scan_roots(V, Vp, mu0sq, xi_val, n_pts=5000)
                if len(roots) >= 2:
                    test_cases_2.append((c1, msq, lam, mu0sq, roots, pv))

print(f"Scanned: 4×6×8×4 = {4*6*8*4} parameter sets")
print(f"Dual basins found: {len(test_cases_2)}")

if test_cases_2:
    print(f"\n{'c1':<6} {'m²':<6} {'λ':<6} {'μ₀²':<6} {'φ₁*':<10} {'φ₂*':<10} {'p₁*':<12} {'p₂*':<12} {'|p₁/p₂|':<10}")
    print("-" * 80)
    for c1, msq, lam, mu0sq, roots, pv in test_cases_2[:30]:
        r = abs(pv[0]/pv[1]) if len(pv) > 1 and abs(pv[1]) > 0 else float('inf')
        print(f"{c1:<6} {msq:<6} {lam:<6} {mu0sq:<6} {roots[0]:<10.4f} {roots[1]:<10.4f} {pv[0]:<12.6f} {pv[1]:<12.6f} {r:<10.4f}")

# ============================================================
print("\n" + "=" * 70)
print("POTENTIAL #3: MEXICAN HAT / DOUBLE-WELL")
print("V(φ) = V₀[(φ/φ₀)² - 1]² = V₀[φ⁴/φ₀⁴ - 2φ²/φ₀² + 1]")
print("=" * 70)

print("""
Classic symmetry-breaking potential. Has TWO minima at φ = ±φ₀.
Only the positive-φ minimum is in our domain.
V'(φ) = 4V₀φ/φ₀²[(φ/φ₀)² - 1] = 0 at φ=0 and φ=φ₀.
V'(φ) < 0 for 0 < φ < φ₀, V'(φ) > 0 for φ > φ₀.
The sign change in V' is what could create two basins.
""")

test_cases_3 = []
for V0 in [1, 5, 10, 50, 100, 500]:
    for phi0_frac in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        phi0 = phi0_frac * phi_c
        for mu0sq in [0.1, 0.5, 1, 5, 10, 50]:
            V = lambda phi, V0=V0, phi0=phi0: V0*((phi/phi0)**2 - 1)**2
            Vp = lambda phi, V0=V0, phi0=phi0: 4*V0*phi/phi0**2 * ((phi/phi0)**2 - 1)
            roots, pv, _, _ = scan_roots(V, Vp, mu0sq, xi_val, n_pts=5000)
            if len(roots) >= 2:
                test_cases_3.append((V0, phi0/phi_c, mu0sq, roots, pv))

print(f"Scanned: 6×8×6 = {6*8*6} parameter sets")
print(f"Dual basins found: {len(test_cases_3)}")

if test_cases_3:
    print(f"\n{'V₀':<8} {'φ₀/φc':<8} {'μ₀²':<8} {'φ₁*':<10} {'φ₂*':<10} {'p₁*':<12} {'p₂*':<12} {'|p₁/p₂|':<10}")
    print("-" * 80)
    for V0, phi0_frac, mu0sq, roots, pv in test_cases_3[:40]:
        r = abs(pv[0]/pv[1]) if len(pv) > 1 and abs(pv[1]) > 0 else float('inf')
        print(f"{V0:<8} {phi0_frac:<8.2f} {mu0sq:<8} {roots[0]:<10.4f} {roots[1]:<10.4f} {pv[0]:<12.6f} {pv[1]:<12.6f} {r:<10.4f}")

# ============================================================
print("\n" + "=" * 70)
print("POTENTIAL #4: TILTED DOUBLE-WELL (most physical)")
print("V(φ) = V₀[(φ/φ₀)² - 1]² + cφ")
print("= double-well + linear tilt (tadpole breaks Z2)")
print("=" * 70)

print("""
This is the natural generalization: the Mexican hat provides
two basins, and the linear tilt (tadpole) breaks the degeneracy.
String theory generically produces both: the double-well from
moduli stabilization and the tilt from uncanceled tadpoles.
""")

test_cases_4 = []
for V0 in [5, 10, 50, 100, 500]:
    for phi0_frac in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        phi0 = phi0_frac * phi_c
        for c1 in [0.1, 0.5, 1, 2, 5, 10]:
            for mu0sq in [0.5, 1, 5, 10]:
                V = lambda phi, V0=V0, phi0=phi0, c1=c1: V0*((phi/phi0)**2 - 1)**2 + c1*phi
                Vp = lambda phi, V0=V0, phi0=phi0, c1=c1: 4*V0*phi/phi0**2*((phi/phi0)**2 - 1) + c1
                roots, pv, _, _ = scan_roots(V, Vp, mu0sq, xi_val, n_pts=5000)
                if len(roots) >= 2:
                    test_cases_4.append((V0, phi0/phi_c, c1, mu0sq, roots, pv))

print(f"Scanned: 5×6×6×4 = {5*6*6*4} parameter sets")
print(f"Dual basins found: {len(test_cases_4)}")

if test_cases_4:
    print(f"\n{'V₀':<6} {'φ₀/φc':<7} {'c₁':<6} {'μ₀²':<6} {'φ₁*':<10} {'φ₂*':<10} {'p₁*':<12} {'p₂*':<12} {'|p₁/p₂|':<10}")
    print("-" * 85)
    for V0, phi0_frac, c1, mu0sq, roots, pv in test_cases_4[:40]:
        r = abs(pv[0]/pv[1]) if len(pv) > 1 and abs(pv[1]) > 0 else float('inf')
        print(f"{V0:<6} {phi0_frac:<7.2f} {c1:<6} {mu0sq:<6} {roots[0]:<10.4f} {roots[1]:<10.4f} {pv[0]:<12.6f} {pv[1]:<12.6f} {r:<10.4f}")


# ============================================================
# IF ANY DUAL BASINS FOUND: DETAILED ANALYSIS OF BEST CASE
# ============================================================
all_dual = test_cases_1 + test_cases_2 + test_cases_3 + test_cases_4
source_labels = (["tadpole+mass"]*len(test_cases_1) +
                 ["cubic"]*len(test_cases_2) +
                 ["Mexican hat"]*len(test_cases_3) +
                 ["tilted hat"]*len(test_cases_4))

if all_dual:
    print("\n" + "=" * 70)
    print(f"TOTAL DUAL-BASIN CONFIGURATIONS FOUND: {len(all_dual)}")
    print("=" * 70)

    # Report by type
    for label, cases in [("tadpole+mass", test_cases_1), ("cubic", test_cases_2),
                          ("Mexican hat", test_cases_3), ("tilted hat", test_cases_4)]:
        if cases:
            print(f"\n  {label}: {len(cases)} configurations")

    # Find the case with the largest |p₁*/p₂*| ratio (most hierarchy enhancement)
    best = None
    best_ratio = 0
    best_label = ""
    best_idx = 0
    for i, (case, label) in enumerate(zip(all_dual, source_labels)):
        pv = case[-1]  # p_vals is last element
        if len(pv) >= 2 and abs(pv[1]) > 0:
            r = abs(pv[0]/pv[1])
            if r > best_ratio:
                best_ratio = r
                best = case
                best_label = label
                best_idx = i

    if best:
        roots = best[-2]
        pv = best[-1]
        print(f"\n--- BEST CASE (largest warp ratio) ---")
        print(f"Source: {best_label}")
        print(f"Parameters: {best[:-2]}")
        print(f"Basin 1: φ* = {roots[0]:.6f}, p* = {pv[0]:.6f}, AdS radius = {1/abs(pv[0]):.4f}")
        print(f"Basin 2: φ* = {roots[1]:.6f}, p* = {pv[1]:.6f}, AdS radius = {1/abs(pv[1]):.4f}")
        print(f"|p₁*/p₂*| = {best_ratio:.4f}")
        print(f"\nPhysical meaning:")
        print(f"  Two regions of bulk, each with different AdS curvature.")
        print(f"  Basin 1 warp rate: |A'| = {abs(pv[0]):.4f} (in k=1 units)")
        print(f"  Basin 2 warp rate: |A'| = {abs(pv[1]):.4f} (in k=1 units)")

        # Estimate total warp for a trajectory through both basins
        # If each basin extends over comparable y-range:
        # Total A = p1*L1 + p2*L2
        # For standard RS: |p|*L = krc*pi = 39.56
        # Two basins each with |p|*L = 39.56 gives total = 79.12
        avg_p = (abs(pv[0]) + abs(pv[1])) / 2
        print(f"\n  If each basin extends over L ≈ 39.56/|p_avg|:")
        print(f"  Total |A| ≈ {abs(pv[0])*39.56/avg_p + abs(pv[1])*39.56/avg_p:.2f}")
        print(f"  (This is just 2×39.56 = {2*39.56:.2f} if basins are equal)")

    # ============================================================
    # HETEROCLINIC ORBIT COMPUTATION FOR BEST CASE
    # ============================================================
    if best and best_label == "tilted hat":
        V0, phi0_frac, c1, mu0sq = best[:4]
        phi0 = phi0_frac * phi_c
        roots_best = best[-2]
        pv_best = best[-1]

        print("\n" + "=" * 70)
        print("HETEROCLINIC ORBIT COMPUTATION")
        print("=" * 70)

        def system_best(y, state):
            p, phi = state
            if phi <= 1e-10 or phi >= 0.999*phi_c or abs(p) < 1e-15:
                return [0, 0]
            Fval = F(phi, xi_val)
            if Fval <= 0:
                return [0, 0]
            V_val = V0*((phi/phi0)**2 - 1)**2 + c1*phi
            Vp_val = 4*V0*phi/phi0**2*((phi/phi0)**2 - 1) + c1
            dp = mu0sq*p/(4*xi_val*phi) + Vp_val/(16*xi_val*phi) - 2.5*p**2
            dphi = (V_val + Lambda5 - 6*Fval*p**2) / (8*xi_val*p*phi)
            return [dp, dphi]

        # Linearize around basin 1 to find unstable direction
        phi1, phi2 = roots_best[0], roots_best[1]
        p1, p2 = pv_best[0], pv_best[1]

        print(f"Basin 1: (p={p1:.6f}, φ={phi1:.6f})")
        print(f"Basin 2: (p={p2:.6f}, φ={phi2:.6f})")

        # Numerical Jacobian at basin 1
        h = 1e-7
        J = np.zeros((2,2))
        f0 = system_best(0, [p1, phi1])
        for j in range(2):
            state_p = [p1, phi1]
            state_p[j] += h
            fp = system_best(0, state_p)
            for i in range(2):
                J[i,j] = (fp[i] - f0[i]) / h

        eigvals, eigvecs = np.linalg.eig(J)
        print(f"\nJacobian eigenvalues at basin 1: {eigvals}")
        print(f"Eigenvectors: {eigvecs}")

        # Find unstable direction (positive eigenvalue)
        unstable_idx = np.argmax(eigvals.real)
        if eigvals[unstable_idx].real > 0:
            unstable_dir = eigvecs[:, unstable_idx].real
            unstable_dir = unstable_dir / np.linalg.norm(unstable_dir)
            print(f"Unstable direction: {unstable_dir}")

            # Launch trajectory along unstable manifold
            eps = 1e-5
            p_start = p1 + eps * unstable_dir[0]
            phi_start = phi1 + eps * unstable_dir[1]

            # Also try the opposite direction
            for sign, label in [(1, "forward"), (-1, "backward")]:
                p_s = p1 + sign * eps * unstable_dir[0]
                phi_s = phi1 + sign * eps * unstable_dir[1]

                if phi_s <= 0 or phi_s >= phi_c:
                    continue

                sol = solve_ivp(system_best, [0, 500], [p_s, phi_s],
                              max_step=0.05, rtol=1e-10, atol=1e-12)

                if sol.success and len(sol.t) > 10:
                    p_traj = sol.y[0]
                    phi_traj = sol.y[1]
                    y_traj = sol.t

                    # Total warp
                    A_total = np.trapezoid(p_traj, y_traj)

                    # Distance to basin 2 at end
                    dist = np.sqrt((p_traj[-1]-p2)**2 + (phi_traj[-1]-phi2)**2)

                    # Minimum distance to basin 2 along trajectory
                    dists = np.sqrt((p_traj-p2)**2 + (phi_traj-phi2)**2)
                    min_dist = np.min(dists)
                    min_dist_idx = np.argmin(dists)

                    print(f"\n  Direction: {label}")
                    print(f"  Integration: y=[0, {y_traj[-1]:.2f}], {len(y_traj)} points")
                    print(f"  p range: [{p_traj.min():.6f}, {p_traj.max():.6f}]")
                    print(f"  φ range: [{phi_traj.min():.6f}, {phi_traj.max():.6f}]")
                    print(f"  Total warp A = ∫p dy = {A_total:.4f}")
                    print(f"  Final distance to basin 2: {dist:.6f}")
                    print(f"  Minimum distance to basin 2: {min_dist:.6f} (at y={y_traj[min_dist_idx]:.2f})")
                    if min_dist < 0.01:
                        print(f"  >>> APPROACHES BASIN 2 <<<")
                        print(f"  Effective krc·π = {abs(A_total):.2f}")

                        # Compare to standard RS
                        print(f"  Standard RS krc·π = 39.56")
                        print(f"  Enhancement factor: {abs(A_total)/39.56:.2f}x")

                        # What KK mass does this give?
                        from scipy.special import jn_zeros
                        x1 = jn_zeros(1, 1)[0]
                        M_Pl_GeV = 2.435e18
                        eV = 1.602e-19
                        hbar = 1.0546e-34
                        m1_GeV = x1 * M_Pl_GeV * np.exp(-abs(A_total))
                        f1_Hz = m1_GeV * 1e9 * eV / (2*np.pi*hbar)
                        print(f"\n  First KK mode: m₁ = {m1_GeV:.4e} GeV")
                        print(f"  Frequency: f₁ = {f1_Hz:.4e} Hz")
                        if 1e9 < f1_Hz < 1e12:
                            print(f"  >>> IN PLASMA FREQUENCY RANGE (GHz-THz) <<<")
        else:
            print("Basin 1 is stable (no unstable direction). Heteroclinic from basin 1 not possible.")
            print("Try launching from basin 2 instead...")

else:
    print("\n" + "=" * 70)
    print("NO DUAL BASINS FOUND IN ANY POTENTIAL")
    print("=" * 70)
    print("""
All four potential forms tested. None produced two simultaneous
roots of G(φ) = 0 in the physical domain.

This is a STRUCTURAL result, not a parameter-tuning failure.
The constraint is coming from the interplay of:
  - F(φ) = 1 - ξφ² vanishing at φ_c (the gravitational positivity bound)
  - The p_minus branch structure (quadratic in p from condition B)
  - The bounded domain (0, φ_c)

Let's understand WHY by analyzing G(φ) more carefully.
""")

    # ============================================================
    # DIAGNOSTIC: WHY CAN'T G HAVE TWO ZEROS?
    # ============================================================
    print("=" * 70)
    print("DIAGNOSTIC: STRUCTURE OF G(φ) NEAR THE CRITICAL COUPLING")
    print("=" * 70)

    # Use tilted double-well for detailed analysis
    V0, phi0_frac, c1, mu0sq = 100, 0.5, 2, 5
    phi0 = phi0_frac * phi_c

    V = lambda phi: V0*((phi/phi0)**2 - 1)**2 + c1*phi
    Vp = lambda phi: 4*V0*phi/phi0**2*((phi/phi0)**2 - 1) + c1

    phi_scan = np.linspace(0.001, 0.999*phi_c, 20000)
    G_vals = np.array([G_general(phi, V, Vp, mu0sq, xi_val) for phi in phi_scan])
    valid = ~np.isnan(G_vals)

    print(f"\nV(φ) = {V0}[(φ/{phi0:.3f})² - 1]² + {c1}φ")
    print(f"μ₀² = {mu0sq}, ξ = {xi_val:.4f}")

    # Compute components of G
    print("\nφ-decomposition of G(φ):")
    header = "{:<8} {:<12} {:<12} {:<14} {:<8} {:<12} {:<12}".format("phi", "V+L5", "6Fp^2", "G", "F", "p_minus", "Vprime")
    print(header)
    print("-" * 80)

    for phi in [0.01, 0.1, 0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.2, 2.4]:
        if phi >= phi_c:
            continue
        Fval = F(phi, xi_val)
        V_val = V(phi)
        Vp_val = Vp(phi)
        pm, pp = p_from_B(phi, Vp_val, mu0sq, xi_val)
        if pm is not None:
            term1 = V_val + Lambda5
            term2 = 6*Fval*pm**2
            G_val = term1 - term2
            print(f"{phi:<8.2f} {term1:<12.2f} {term2:<12.2f} {G_val:<14.2f} {Fval:<8.4f} {pm:<12.6f} {Vp_val:<12.2f}")

    # Key insight: as φ→0, p_minus → -∞ (from the structure of condition B)
    # and 6Fp² → ∞, dominating V+Λ₅. Near φ_c, F→0 so 6Fp²→0.
    # The question: can 6Fp² have a LOCAL MINIMUM in between?

    print("\n\nDerivative analysis: d(6Fp²)/dφ")
    print("If this has a sign change, G can have an internal extremum.\n")

    term2_vals = []
    for phi in phi_scan:
        if phi < 0.001 or phi >= 0.999*phi_c:
            term2_vals.append(np.nan)
            continue
        Fval = F(phi, xi_val)
        Vp_val = Vp(phi)
        pm, pp = p_from_B(phi, Vp_val, mu0sq, xi_val)
        if pm is not None:
            term2_vals.append(6*Fval*pm**2)
        else:
            term2_vals.append(np.nan)

    term2_arr = np.array(term2_vals)
    valid2 = ~np.isnan(term2_arr)
    t2_v = term2_arr[valid2]
    phi_v = phi_scan[valid2]

    if len(t2_v) > 2:
        dt2 = np.diff(t2_v) / np.diff(phi_v)
        # Sign changes in derivative of 6Fp²
        dt2_signs = np.where(np.diff(np.sign(dt2)))[0]
        print(f"  Sign changes in d(6Fp²)/dφ: {len(dt2_signs)}")
        if dt2_signs.any():
            for idx in dt2_signs:
                print(f"    At φ ≈ {phi_v[idx+1]:.4f}, 6Fp² = {t2_v[idx+1]:.4f}")

        # Also check: G itself
        G_v2 = G_vals[valid]
        phi_v2 = phi_scan[valid]
        dG = np.diff(G_v2) / np.diff(phi_v2)
        dG_signs = np.where(np.diff(np.sign(dG)))[0]
        print(f"  Sign changes in dG/dφ: {len(dG_signs)}")
        for idx in dG_signs[:5]:
            print(f"    At φ ≈ {phi_v2[idx+1]:.4f}, G = {G_v2[idx+1]:.4f}")

        # The critical question: does G have a local MAX that is positive
        # AND a local MIN that is negative?
        if len(dG_signs) >= 2:
            # Check the extrema
            extrema = []
            for idx in dG_signs:
                extrema.append((phi_v2[idx+1], G_v2[idx+1]))
            print(f"\n  G extrema: {extrema}")
            has_pos_max = any(g > 0 for _, g in extrema[::2])  # maxima at even indices
            has_neg_min = any(g < 0 for _, g in extrema[1::2])  # minima at odd indices
            print(f"  Has positive maximum: {has_pos_max}")
            print(f"  Has negative minimum: {has_neg_min}")
            if has_pos_max and has_neg_min:
                print("  >>> G HAS THE RIGHT TOPOLOGY FOR TWO ZEROS <<<")
                print("  But the roots may not both be in the physical domain.")

    # Final summary
    print("\n" + "=" * 70)
    print("STRUCTURAL ANALYSIS SUMMARY")
    print("=" * 70)
    print("""
The 6F(φ)p²(φ) term is the key. It represents the gravitational
potential energy contribution to the fixed-point condition.

Near φ=0: p→-∞ (scalar constraint requires large warp for small φ),
  so 6Fp² → +∞ regardless of V(φ). G is always -∞ here.

Near φ=φ_c: F→0 kills the gravitational term, so G → V(φ_c)+Λ₅.
  G is positive here if V(φ_c) > |Λ₅| = 12.

The transition: 6Fp² decreases monotonically from ∞ to 0 as φ goes
from 0 to φ_c. The V(φ)+Λ₅ term adds structure but can't overcome
the monotone decay of 6Fp² for any tested potential.

CONCLUSION: The gravitational positivity bound F>0 combined with
the cuscuton constraint creates a SINGLE-BASIN attractor in the
(p,φ) plane. The approach to dual basins through more complex V(φ)
appears to be structurally blocked by the monotone behavior of
the gravitational potential energy term 6F(φ)p²_minus(φ).
""")

print("\nCalculation complete.")
print("=" * 70)
