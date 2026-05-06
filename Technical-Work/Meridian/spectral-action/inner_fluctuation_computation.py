"""
Inner Fluctuation Computation — Level 3, Section 8 Follow-Up
Clawd, March 26, 2026 (Do Be Do Be Do drive)

The midday drive showed: spectral action of O x CY gives UNIVERSAL coupling (Model B).
This computation tests: do INNER FLUCTUATIONS give STATE-DEPENDENT coupling (Model C)?

Toy model:
  Observer: A_O = M_2(C), H_O = C^2, D_O = [[0, m], [m, 0]], gamma_O = diag(1, -1)
  CY (two chambers): A_F = C + C, H_F = C^2, D_F = [[0, y], [y, 0]]
  Product: A = A_O x A_F, H = C^4, D_total = D_O x 1 + gamma_O x D_F

The inner fluctuation in the CY direction is the Higgs analog:
  A_F = sum_j a_j [D_total, b_j]  for a_j, b_j in A_O x A_F

Key question: Does the effective potential V(A_F) = Tr(f(D'^2/Lambda^2))
depend on WHICH observer state (b_O) generates the inner fluctuation?
If yes -> Model C (state-dependent coupling). If no -> Model B confirmed.
"""

import numpy as np
from numpy import kron

# ============================================================
# Part 1: Build the product geometry
# ============================================================

def build_product_geometry(m_obs, y_cy):
    """Build the 4x4 product Dirac operator.

    D_O = [[0, m], [m, 0]]  (observer, real mass)
    D_F = [[0, y], [y, 0]]  (CY, real Yukawa)
    gamma_O = diag(1, -1)   (even grading)

    D_total = D_O x I_2 + gamma_O x D_F

    Basis: |1,1>, |1,2>, |2,1>, |2,2>
    where first index = observer, second = CY
    """
    I2 = np.eye(2)

    D_O = np.array([[0, m_obs], [m_obs, 0]])
    D_F = np.array([[0, y_cy], [y_cy, 0]])
    gamma_O = np.array([[1, 0], [0, -1]])

    D_total = kron(D_O, I2) + kron(gamma_O, D_F)

    return D_total, D_O, D_F, gamma_O


# ============================================================
# Part 2: Compute inner fluctuations
# ============================================================

def algebra_element_product(A_O_mat, c1, c2):
    """Element of A_O x A_F = M_2(C) x (C + C).

    A_O_mat: 2x2 matrix in M_2(C) (observer algebra element)
    c1, c2: complex numbers in C + C (CY algebra element)

    Acts on H = C^2 x C^2 = C^4 as:
    A_O_mat x diag(c1, c2)
    """
    D_F_elem = np.diag([c1, c2])
    return kron(A_O_mat, D_F_elem)


def inner_fluctuation(D_total, algebra_elements_a, algebra_elements_b):
    """Compute A = sum_j a_j [D_total, b_j]

    algebra_elements_a: list of 4x4 matrices (product algebra elements)
    algebra_elements_b: list of 4x4 matrices (product algebra elements)

    Returns A (4x4 matrix) — the inner fluctuation 1-form.
    """
    A = np.zeros_like(D_total, dtype=complex)
    for a, b in zip(algebra_elements_a, algebra_elements_b):
        comm = D_total @ b - b @ D_total
        A += a @ comm
    return A


def make_hermitian(A):
    """Ensure A + A* for self-adjoint fluctuation."""
    return A + A.conj().T


# ============================================================
# Part 3: Observer states and their inner fluctuations
# ============================================================

def observer_state_fluctuations(D_total, m_obs, y_cy):
    """Generate inner fluctuations for different observer algebraic states.

    Different b_O in M_2(C) produce different inner fluctuations.
    We test several representative observer states:
    1. Identity (trivial observer)
    2. sigma_x (transition between observer states)
    3. sigma_z (distinguishing observer states)
    4. sigma_y (complex transitions)
    5. Projection onto |1> (observer in state 1)
    6. Projection onto |2> (observer in state 2)
    """
    I2 = np.eye(2)
    sx = np.array([[0, 1], [1, 0]])
    sy = np.array([[0, -1j], [1j, 0]])
    sz = np.array([[1, 0], [0, -1]])
    P1 = np.array([[1, 0], [0, 0]])  # project onto |1>
    P2 = np.array([[0, 0], [0, 1]])  # project onto |2>

    observer_states = {
        "I (identity)": I2,
        "sigma_x (transition)": sx,
        "sigma_z (distinguish)": sz,
        "sigma_y (complex)": sy,
        "P_1 (state 1)": P1,
        "P_2 (state 2)": P2,
    }

    results = {}
    for name, b_O in observer_states.items():
        # For each observer state b_O, construct the product algebra element
        # b = b_O x diag(1, 0)  — pointing at chamber 1
        # and a = I_O x diag(1, 1) — identity on CY side

        # Inner fluctuation: a [D, b] where b = b_O x diag(1, 0)
        b = algebra_element_product(b_O, 1.0, 0.0)  # b_F = (1, 0): pointing at chamber 1
        a = algebra_element_product(I2, 1.0, 1.0)    # a_F = (1, 1): full CY

        A = inner_fluctuation(D_total, [a], [b])
        A_sa = make_hermitian(A)  # Self-adjoint part

        # Modified Dirac: D' = D + A_sa
        D_prime = D_total + A_sa

        # Eigenvalues of D' and D'^2
        eigs = np.sort(np.real(np.linalg.eigvalsh(D_prime)))
        eigs_sq = np.sort(np.real(np.linalg.eigvalsh(D_prime @ D_prime)))

        # Spectral action: S = sum f(lambda^2 / Lambda^2)
        # Use smooth cutoff with Lambda = 10
        Lambda = 10.0
        S = np.sum(1.0 / (1.0 + np.exp(20 * (eigs_sq / Lambda**2 - 1))))

        results[name] = {
            'b_O': b_O,
            'A': A_sa,
            'D_prime': D_prime,
            'eigenvalues': eigs,
            'eigenvalues_sq': eigs_sq,
            'spectral_action': S
        }

    return results


# ============================================================
# Part 4: Vary the CY modulus and check coupling
# ============================================================

def coupling_vs_modulus(m_obs, y_range, observer_states_dict):
    """For each observer state, compute spectral action as CY modulus y varies.

    If the SHAPE of S(y) depends on the observer state -> state-dependent coupling.
    If only the MAGNITUDE changes -> universal coupling (Model B).
    """
    I2 = np.eye(2)
    Lambda = 10.0

    results = {}
    for name, b_O in observer_states_dict.items():
        S_values = []
        for y in y_range:
            D_total, _, _, _ = build_product_geometry(m_obs, y)

            # Inner fluctuation with this observer state
            b = algebra_element_product(b_O, 1.0, 0.0)
            a = algebra_element_product(I2, 1.0, 1.0)
            A = inner_fluctuation(D_total, [a], [b])
            A_sa = make_hermitian(A)

            D_prime = D_total + A_sa
            eigs_sq = np.real(np.linalg.eigvalsh(D_prime @ D_prime))
            S = np.sum(1.0 / (1.0 + np.exp(20 * (eigs_sq / Lambda**2 - 1))))
            S_values.append(S)

        results[name] = np.array(S_values)

    return results


# ============================================================
# Part 5: Run the computation
# ============================================================

print("=" * 70)
print("INNER FLUCTUATION COMPUTATION")
print("Does the observer's algebraic state affect the coupling?")
print("=" * 70)

# Parameters
m_obs = 1.0   # Observer mass
y_cy = 2.0    # CY Yukawa (modulus)

# Build product geometry
D_total, D_O, D_F, gamma_O = build_product_geometry(m_obs, y_cy)

print(f"\nParameters: m_obs = {m_obs}, y_cy = {y_cy}")
print(f"\nD_total eigenvalues: {np.sort(np.real(np.linalg.eigvalsh(D_total)))}")

# ============================================================
# Part 6: Inner fluctuations for different observer states
# ============================================================

print("\n" + "=" * 70)
print("PART 1: INNER FLUCTUATIONS FOR DIFFERENT OBSERVER STATES")
print("=" * 70)

results = observer_state_fluctuations(D_total, m_obs, y_cy)

dp_label = "Eigenvalues of D'"
print(f"\n{'Observer state':<30} {dp_label:>40} {'S':>8}")
print("-" * 80)
for name, r in results.items():
    eig_str = "[" + ", ".join(f"{e:6.3f}" for e in r['eigenvalues']) + "]"
    print(f"  {name:<28} {eig_str:>40} {r['spectral_action']:8.4f}")

# Check if spectral actions differ
S_values = [r['spectral_action'] for r in results.values()]
S_min, S_max = min(S_values), max(S_values)
print(f"\nSpectral action range: [{S_min:.6f}, {S_max:.6f}]")
print(f"Variation: {(S_max - S_min):.6f}")
if abs(S_max - S_min) > 1e-6:
    print(">>> OBSERVER-DEPENDENT: Different states give different spectral actions!")
else:
    print(">>> UNIVERSAL: All states give the same spectral action (Model B).")

# ============================================================
# Part 7: Eigenvalue spectra comparison
# ============================================================

print("\n" + "=" * 70)
print("PART 2: EIGENVALUE SPECTRA OF D' (detailed)")
print("=" * 70)

for name, r in results.items():
    print(f"\n  {name}:")
    print(f"    D' eigenvalues:   {r['eigenvalues']}")
    print(f"    D'^2 eigenvalues: {r['eigenvalues_sq']}")
    print(f"    |A| (Frobenius):  {np.linalg.norm(r['A']):.6f}")

# ============================================================
# Part 8: Coupling vs. CY modulus for different observer states
# ============================================================

print("\n" + "=" * 70)
print("PART 3: COUPLING vs CY MODULUS (moduli sensitivity)")
print("=" * 70)

I2 = np.eye(2)
sx = np.array([[0, 1], [1, 0]])
sz = np.array([[1, 0], [0, -1]])
P1 = np.array([[1, 0], [0, 0]])
P2 = np.array([[0, 0], [0, 1]])

observer_dict = {
    "I (identity)": I2,
    "sigma_z": sz,
    "P_1 (state 1)": P1,
    "P_2 (state 2)": P2,
}

y_range = np.linspace(0.5, 5.0, 20)
coupling_results = coupling_vs_modulus(m_obs, y_range, observer_dict)

print(f"\nS(y) for each observer state (m_obs = {m_obs}):")
print(f"{'y':>6}", end="")
for name in observer_dict:
    print(f"  {name[:12]:>14}", end="")
print()
print("-" * (6 + 16 * len(observer_dict)))

for i, y in enumerate(y_range):
    print(f"{y:6.2f}", end="")
    for name in observer_dict:
        print(f"  {coupling_results[name][i]:14.6f}", end="")
    print()

# Compute derivatives (sensitivity to modulus change)
print(f"\ndS/dy for each observer (numerical derivative at y = {y_cy}):")
dy = y_range[1] - y_range[0]
y_idx = np.argmin(np.abs(y_range - y_cy))
if y_idx > 0 and y_idx < len(y_range) - 1:
    for name in observer_dict:
        dSdy = (coupling_results[name][y_idx + 1] - coupling_results[name][y_idx - 1]) / (2 * dy)
        print(f"  {name:<25}: dS/dy = {dSdy:.6f}")

# ============================================================
# Part 9: The key test — do sensitivities DIFFER between observers?
# ============================================================

print("\n" + "=" * 70)
print("PART 4: THE KEY TEST — STATE-DEPENDENT SENSITIVITY?")
print("=" * 70)

# Compare the S(y) curves: normalize each to its mean
print("\nNormalized S(y) / mean(S) for each observer:")
for name in observer_dict:
    S = coupling_results[name]
    S_norm = S / np.mean(S)
    print(f"  {name:<25}: min={S_norm.min():.6f}, max={S_norm.max():.6f}, "
          f"range={S_norm.max()-S_norm.min():.6f}")

# Cross-correlation between curves
print("\nCross-correlation of normalized S(y) curves:")
curves = {}
for name in observer_dict:
    S = coupling_results[name]
    curves[name] = (S - np.mean(S)) / np.std(S) if np.std(S) > 0 else S

names = list(observer_dict.keys())
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        corr = np.corrcoef(curves[names[i]], curves[names[j]])[0, 1]
        print(f"  {names[i][:15]:>15} x {names[j][:15]:<15}: r = {corr:.6f}")

# ============================================================
# Part 10: Asymmetric CY — two different chambers
# ============================================================

print("\n" + "=" * 70)
print("PART 5: ASYMMETRIC CY (two distinguishable chambers)")
print("=" * 70)

# Now make the CY asymmetric: D_F = diag(lambda_1, lambda_2) with lambda_1 != lambda_2
# This breaks the chamber symmetry, like having two distinct Kahler chambers

def build_asymmetric_product(m_obs, lambda1, lambda2):
    """Product with asymmetric CY: D_F has different eigenvalues for each chamber."""
    I2 = np.eye(2)
    D_O = np.array([[0, m_obs], [m_obs, 0]])
    # D_F with two DIFFERENT eigenvalues (asymmetric chambers)
    D_F = np.array([[0, complex(lambda1 + lambda2) / 2],
                     [complex(lambda1 + lambda2) / 2, 0]])
    # Actually, for distinct chambers, use diagonal D_F
    # In NCG, a spectral triple on two points with different "distances"
    D_F = np.array([[lambda1, 0], [0, lambda2]], dtype=complex)
    gamma_O = np.array([[1, 0], [0, -1]])

    D_total = kron(D_O, I2) + kron(gamma_O, D_F)
    return D_total

# Two chambers with different "curvatures"
lambda1 = 1.0   # Chamber 1 (close, SM-like)
lambda2 = 3.0   # Chamber 2 (target, different moduli)

D_asym = build_asymmetric_product(m_obs, lambda1, lambda2)
print(f"\nAsymmetric CY: lambda_1 = {lambda1}, lambda_2 = {lambda2}")
print(f"D_total eigenvalues: {np.sort(np.real(np.linalg.eigvalsh(D_asym)))}")

# Inner fluctuations pointing at each chamber
for label, cy_elem in [("pointing at chamber 1", (1.0, 0.0)),
                         ("pointing at chamber 2", (0.0, 1.0)),
                         ("superposition", (0.707, 0.707))]:
    print(f"\nCY element: {label} = {cy_elem}")
    for obs_name, b_O in [("I", I2), ("P_1", P1), ("P_2", P2)]:
        b = algebra_element_product(b_O, cy_elem[0], cy_elem[1])
        a = algebra_element_product(I2, 1.0, 1.0)
        A = inner_fluctuation(D_asym, [a], [b])
        A_sa = make_hermitian(A)
        D_prime = D_asym + A_sa
        eigs = np.sort(np.real(np.linalg.eigvalsh(D_prime)))
        eigs_sq = np.real(np.linalg.eigvalsh(D_prime @ D_prime))
        Lambda = 10.0
        S = np.sum(1.0 / (1.0 + np.exp(20 * (eigs_sq / Lambda**2 - 1))))
        print(f"    Observer {obs_name}: D' eigs = [{', '.join(f'{e:.3f}' for e in eigs)}], S = {S:.6f}")

# ============================================================
# Part 11: Summary
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
This computation tests whether INNER FLUCTUATIONS of the NCG product
geometry produce state-dependent coupling between observer and CY moduli.

The inner fluctuation A = sum a_j [D, b_j] depends on:
  - b_O: the observer's algebraic state (element of A_O = M_2(C))
  - b_F: which Kahler chamber is being "pointed at" (element of A_F = C+C)

The modified Dirac operator D' = D + A has a spectral action S(D')
that serves as an effective potential. If S depends on b_O, the
coupling is STATE-DEPENDENT (Model C). If not, it's UNIVERSAL (Model B).

Check the results above to see which case holds.
""")
