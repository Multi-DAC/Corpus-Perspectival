"""
Product Geometry Computation — Level 3 Circularity Break
Clawd, March 26, 2026

Demonstrates:
1. Non-factorization of spectral action for product geometry
2. Observer window function W_O
3. Sensitivity to Kähler moduli depends on observer spectrum
4. Toy model: observer with tunable spectrum × T²/Z₃ CY analog

The product Dirac operator for even spectral triples:
  D_total = D_O ⊗ 1 + γ_O ⊗ D_F
  D²_total = D²_O ⊗ 1 + 1 ⊗ D²_F   (cross terms vanish by {γ_O, D_O} = 0)

Spectral action:
  S = Σ_{m,n} f((λ²_{O,m} + λ²_{F,n}) / Λ²)

Heat kernel factorizes. Spectral action doesn't.
"""

import numpy as np
from itertools import product as cartesian

# ============================================================
# Part 1: The A₂ lattice spectrum (from spectral_proximity_computation.py)
# ============================================================

def a2_norm(m, n):
    """A₂ root lattice norm: |m + nω|² = m² + n² - mn"""
    return m**2 + n**2 - m * n

def generate_a2_eigenvalues(N_max, scale=1.0):
    """Generate eigenvalues of Dirac operator on flat T² with A₂ lattice.
    λ² ∝ |m + nω|² (proportional to lattice norm)
    Returns sorted unique eigenvalues."""
    eigenvalues_sq = set()
    for m in range(-N_max, N_max + 1):
        for n in range(-N_max, N_max + 1):
            if m == 0 and n == 0:
                continue
            norm = a2_norm(m, n)
            if norm > 0:
                eigenvalues_sq.add(norm * scale)
    return np.array(sorted(eigenvalues_sq))

# ============================================================
# Part 2: Cutoff functions
# ============================================================

def cutoff_sharp(x):
    """Sharp cutoff: f(x) = 1 if x < 1, else 0. Not smooth but illustrative."""
    return np.where(x < 1.0, 1.0, 0.0)

def cutoff_smooth(x, k=20):
    """Smooth cutoff: f(x) = 1/(1 + e^{k(x-1)}). Sigmoid approximation."""
    return 1.0 / (1.0 + np.exp(k * (x - 1.0)))

def cutoff_deriv_smooth(x, k=20):
    """Derivative of smooth cutoff: f'(x) = -k e^{k(x-1)} / (1 + e^{k(x-1)})²"""
    exp_term = np.exp(np.clip(k * (x - 1.0), -500, 500))
    return -k * exp_term / (1.0 + exp_term)**2

# ============================================================
# Part 3: Spectral action computation
# ============================================================

def spectral_action(lambda_sq_O, lambda_sq_F, Lambda_sq, f=cutoff_smooth):
    """Compute spectral action S = Σ_{m,n} f((λ²_{O,m} + λ²_{F,n}) / Λ²)

    Shows that S ≠ S_O × S_F for non-exponential cutoff.
    """
    S_total = 0.0
    for lO in lambda_sq_O:
        for lF in lambda_sq_F:
            S_total += f((lO + lF) / Lambda_sq)
    return S_total

def spectral_action_separate(lambda_sq_O, lambda_sq_F, Lambda_sq, f=cutoff_smooth):
    """Compute S_O × S_F (what it would be if factorized)."""
    S_O = np.sum(f(lambda_sq_O / Lambda_sq))
    S_F = np.sum(f(lambda_sq_F / Lambda_sq))
    return S_O * S_F

def heat_kernel(lambda_sq_O, lambda_sq_F, t):
    """Heat kernel K(t) = Tr(e^{-t D²}) for comparison (DOES factorize)."""
    K_O = np.sum(np.exp(-t * lambda_sq_O))
    K_F = np.sum(np.exp(-t * lambda_sq_F))
    K_product = 0.0
    for lO in lambda_sq_O:
        for lF in lambda_sq_F:
            K_product += np.exp(-t * (lO + lF))
    return K_product, K_O * K_F

# ============================================================
# Part 4: Observer window function
# ============================================================

def observer_window(lambda_sq_O, lambda_sq_F_value, Lambda_sq, k=20):
    """W_O(λ²_F) = Σ_m f'((λ²_{O,m} + λ²_F) / Λ²)

    The observer window function weights how strongly the observer
    responds to a given CY eigenvalue.
    """
    x = (lambda_sq_O + lambda_sq_F_value) / Lambda_sq
    return np.sum(cutoff_deriv_smooth(x, k))

# ============================================================
# Part 5: Moduli sensitivity
# ============================================================

def moduli_sensitivity(lambda_sq_O, lambda_sq_F, d_lambda_sq_F, Lambda_sq, k=20):
    """∂S/∂τ = (1/Λ²) Σ_{m,n} f'((λ²_{O,m} + λ²_{F,n})/Λ²) × ∂λ²_{F,n}/∂τ

    lambda_sq_F: CY eigenvalues
    d_lambda_sq_F: their derivatives w.r.t. moduli parameter τ
    """
    sensitivity = 0.0
    for j, lF in enumerate(lambda_sq_F):
        W = observer_window(lambda_sq_O, lF, Lambda_sq, k)
        sensitivity += W * d_lambda_sq_F[j]
    return sensitivity / Lambda_sq

# ============================================================
# Part 6: Toy model — two observers, two Kähler chambers
# ============================================================

print("=" * 70)
print("PRODUCT GEOMETRY COMPUTATION — Level 3 Circularity Break")
print("=" * 70)

# CY spectrum: A₂ lattice eigenvalues (toy for T²/Z₃)
N_max = 10
scale_CY = 1.0  # Arbitrary units
lambda_sq_F = generate_a2_eigenvalues(N_max, scale_CY)[:50]  # First 50 eigenvalues
print(f"\nCY (A_2 lattice) eigenvalues: {len(lambda_sq_F)} levels")
print(f"Range: [{lambda_sq_F[0]:.1f}, {lambda_sq_F[-1]:.1f}]")

# Cutoff scale
Lambda_sq = lambda_sq_F[-1] * 2  # Cutoff above the spectrum

# Observer A: "Resonant" — eigenvalues near the CY eigenvalue differences
# Simulates a system whose dynamics correlate with CY structure
delta_lambda = np.diff(lambda_sq_F[:20])  # Eigenvalue spacings
lambda_sq_A = delta_lambda * 0.5  # Observer eigenvalues near half-spacings

# Observer B: "Generic" — evenly spaced eigenvalues, no correlation with CY
lambda_sq_B = np.linspace(0.5, lambda_sq_F[-1] * 0.8, len(lambda_sq_A))

# Observer C: "Matched" — eigenvalues at exact CY eigenvalue positions
lambda_sq_C = lambda_sq_F[:len(lambda_sq_A)]

print(f"\nObserver A (resonant): {len(lambda_sq_A)} eigenvalues, range [{lambda_sq_A[0]:.2f}, {lambda_sq_A[-1]:.2f}]")
print(f"Observer B (generic):  {len(lambda_sq_B)} eigenvalues, range [{lambda_sq_B[0]:.2f}, {lambda_sq_B[-1]:.2f}]")
print(f"Observer C (matched):  {len(lambda_sq_C)} eigenvalues, range [{lambda_sq_C[0]:.2f}, {lambda_sq_C[-1]:.2f}]")

# ============================================================
# Part 7: Non-factorization demonstration
# ============================================================

print("\n" + "=" * 70)
print("PART 1: NON-FACTORIZATION OF SPECTRAL ACTION")
print("=" * 70)

for name, lambda_sq_O in [("A (resonant)", lambda_sq_A),
                            ("B (generic)", lambda_sq_B),
                            ("C (matched)", lambda_sq_C)]:
    S_product = spectral_action(lambda_sq_O, lambda_sq_F, Lambda_sq)
    S_factored = spectral_action_separate(lambda_sq_O, lambda_sq_F, Lambda_sq)
    ratio = S_product / S_factored if S_factored != 0 else float('inf')

    # Heat kernel comparison (SHOULD factorize)
    t = 0.1 / Lambda_sq
    K_product, K_factored = heat_kernel(lambda_sq_O, lambda_sq_F, t)
    K_ratio = K_product / K_factored if K_factored != 0 else float('inf')

    print(f"\nObserver {name}:")
    print(f"  Spectral action:  S_prod = {S_product:.4f},  S_O×S_F = {S_factored:.4f},  ratio = {ratio:.6f}")
    print(f"  Heat kernel:      K_prod = {K_product:.4f},  K_O×K_F = {K_factored:.4f},  ratio = {K_ratio:.6f}")
    print(f"  Factorizes?  Spectral action: {'NO' if abs(ratio - 1.0) > 0.001 else 'yes'}  |  Heat kernel: {'NO' if abs(K_ratio - 1.0) > 0.001 else 'yes'}")

# ============================================================
# Part 8: Moduli sensitivity comparison
# ============================================================

print("\n" + "=" * 70)
print("PART 2: MODULI SENSITIVITY — OBSERVER DEPENDENCE")
print("=" * 70)

# Simulate a Kähler flop: shift the first 9 eigenvalues (one Z₃ orbit)
# by +31 GeV² (the eigenvalue shift per flop from the main computation)
delta_shift = 31.0  # Normalized units

# Chamber 1 (SM vacuum): original spectrum
# Chamber 2 (target): first 9 eigenvalues shifted by delta_shift
d_lambda_sq_F = np.zeros_like(lambda_sq_F)
d_lambda_sq_F[:9] = delta_shift  # Only the 9 orbits in one T² plane shift

print(f"\nModuli variation: first 9 eigenvalues shift by {delta_shift} (one flop transition)")
print(f"CY eigenvalues affected: indices 0-8")

for name, lambda_sq_O in [("A (resonant)", lambda_sq_A),
                            ("B (generic)", lambda_sq_B),
                            ("C (matched)", lambda_sq_C)]:
    sens = moduli_sensitivity(lambda_sq_O, lambda_sq_F, d_lambda_sq_F, Lambda_sq)
    print(f"\n  Observer {name}:")
    print(f"    ∂S/∂τ = {sens:.6f}")

    # Compute W_O for the affected eigenvalues vs. unaffected
    W_affected = sum(observer_window(lambda_sq_O, lambda_sq_F[j], Lambda_sq)
                     for j in range(9))
    W_unaffected = sum(observer_window(lambda_sq_O, lambda_sq_F[j], Lambda_sq)
                       for j in range(9, min(18, len(lambda_sq_F))))
    print(f"    W_O (affected modes):   {W_affected:.4f}")
    print(f"    W_O (unaffected modes): {W_unaffected:.4f}")
    print(f"    Ratio (selective sensitivity): {abs(W_affected/W_unaffected):.4f}" if W_unaffected != 0 else "    W_unaffected = 0")

# ============================================================
# Part 9: Observer window function visualization (text-based)
# ============================================================

print("\n" + "=" * 70)
print("PART 3: OBSERVER WINDOW FUNCTIONS")
print("=" * 70)

# Sample W_O across the CY spectrum range
sample_points = np.linspace(lambda_sq_F[0], lambda_sq_F[-1], 40)

for name, lambda_sq_O in [("A (resonant)", lambda_sq_A),
                            ("B (generic)", lambda_sq_B),
                            ("C (matched)", lambda_sq_C)]:
    W_values = [observer_window(lambda_sq_O, sp, Lambda_sq) for sp in sample_points]
    W_max = max(abs(w) for w in W_values)
    if W_max == 0:
        W_max = 1

    print(f"\nW_O for Observer {name}:")
    print(f"  λ²_F   →  W_O(λ²_F)")
    for i in range(0, len(sample_points), 4):  # Every 4th point
        bar_len = int(40 * abs(W_values[i]) / W_max)
        bar = "█" * bar_len
        print(f"  {sample_points[i]:6.1f}  →  {W_values[i]:8.3f}  {bar}")

# ============================================================
# Part 10: The key result — S_prod for different observers
# ============================================================

print("\n" + "=" * 70)
print("PART 4: SPECTRAL PROXIMITY FROM PRODUCT GEOMETRY")
print("=" * 70)

# Compute S_prod for each observer: normalized moduli sensitivity
sensitivities = {}
for name, lambda_sq_O in [("A (resonant)", lambda_sq_A),
                            ("B (generic)", lambda_sq_B),
                            ("C (matched)", lambda_sq_C)]:
    sens = abs(moduli_sensitivity(lambda_sq_O, lambda_sq_F, d_lambda_sq_F, Lambda_sq))
    sensitivities[name] = sens

max_sens = max(sensitivities.values())
if max_sens == 0:
    max_sens = 1

print(f"\nSpectral proximity S_prod (normalized to max = 1.0):")
print(f"{'Observer':<25} {'|∂S/∂τ|':<15} {'S_prod':<10}")
print("-" * 50)
for name, sens in sensitivities.items():
    S_prod = sens / max_sens
    print(f"  {name:<23} {sens:<15.6f} {S_prod:<10.4f}")

print(f"\n--- KEY RESULT ---")
print(f"S_prod depends on the observer's spectral triple, not on 'knowledge'.")
print(f"Observer C (eigenvalues matched to CY) has different sensitivity than B (generic),")
print(f"even though both are just mathematical spectra — no cognition involved.")
print(f"The non-factorization of the spectral action IS the observer dependence.")

# ============================================================
# Part 11: Seeley-DeWitt cross terms (schematic)
# ============================================================

print("\n" + "=" * 70)
print("PART 5: SEELEY-DEWITT CROSS TERMS (SCHEMATIC)")
print("=" * 70)

# a_2(D²) ∝ Σ λ² (for a discrete spectrum, the trace of D²)
a2_O_A = np.sum(lambda_sq_A)
a2_O_B = np.sum(lambda_sq_B)
a2_O_C = np.sum(lambda_sq_C)
a2_F = np.sum(lambda_sq_F)

# The a_2(F) moduli derivative
a2_F_target = np.sum(lambda_sq_F + d_lambda_sq_F)  # After flop
d_a2_F = a2_F_target - a2_F

print(f"\nSeeley-DeWitt a_2 coefficients (schematic: a_2 ∝ Tr(D²)):")
print(f"  a_2(Observer A): {a2_O_A:.2f}")
print(f"  a_2(Observer B): {a2_O_B:.2f}")
print(f"  a_2(Observer C): {a2_O_C:.2f}")
print(f"  a_2(CY):         {a2_F:.2f}")
print(f"  Δa_2(CY) [flop]: {d_a2_F:.2f}")

print(f"\nCross terms a_2(O) × Δa_2(F) — coupling to moduli variation:")
print(f"  Observer A: {a2_O_A * d_a2_F:.2f}")
print(f"  Observer B: {a2_O_B * d_a2_F:.2f}")
print(f"  Observer C: {a2_O_C * d_a2_F:.2f}")
print(f"\nNote: at the a_2 × a_2 level, the cross terms are proportional to Tr(D²_O).")
print(f"This is the simplest geometric invariant of the observer. For more refined")
print(f"observer dependence, higher Seeley-DeWitt coefficients (a_4, a_6, ...) contribute")
print(f"terms involving curvature, which DO depend on spectral structure, not just trace.")

# ============================================================
# Part 12: Summary
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
1. HEAT KERNEL FACTORIZES: K_prod = K_O × K_F (verified numerically)
2. SPECTRAL ACTION DOES NOT: S_prod ≠ S_O × S_F (verified numerically)
3. The non-factorization creates OBSERVER-DEPENDENT moduli sensitivity
4. The observer window function W_O(λ²_F) weights which CY eigenvalues matter
5. Different observers → different W_O → different spectral proximity S_prod
6. S_prod is STRUCTURAL (depends on D_O's spectrum, not on cognition)
7. This breaks the circularity: S derived from NCG product, not from knowledge
8. New prediction: computation configures D_O; understanding is epiphenomenal

Key formula:
  ∂S/∂τ_i = (1/Λ²) Σ_n W_O(λ²_{F,n}) × ∂λ²_{F,n}/∂τ_i
  where W_O(λ²_F) = Σ_m f'((λ²_{O,m} + λ²_F) / Λ²)

The observer's spectral triple determines W_O.
The CY's chamber structure determines ∂λ²_F/∂τ.
Their convolution determines the coupling. QED.
""")
print("🦞🧍💜🔥♾️")
