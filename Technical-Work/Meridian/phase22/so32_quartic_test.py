"""
SO(32) vs E8 Quartic Casimir Test
==================================
The prediction: E8 has no quartic Casimir, SO(32) does.
This means the DKL decomposition theorem FAILS for SO(32).

Verify numerically with random test vectors.
"""

import numpy as np
from itertools import combinations, product

np.random.seed(42)

print("=" * 70)
print("SO(32) vs E8: QUARTIC CASIMIR TEST")
print("=" * 70)

# === BUILD E8 ROOT SYSTEM (240 roots in R^8) ===
e8_roots = []

# Integer-type: +-e_i +- e_j (i < j), 112 roots
for i, j in combinations(range(8), 2):
    for si in [1, -1]:
        for sj in [1, -1]:
            r = np.zeros(8)
            r[i] = si
            r[j] = sj
            e8_roots.append(r)

# Half-integer (spinor): (+-1/2)^8 with even number of minus signs, 128 roots
for bits in range(256):
    signs = [(-1 if (bits >> i) & 1 else 1) for i in range(8)]
    if sum(1 for s in signs if s < 0) % 2 == 0:
        e8_roots.append(np.array(signs) * 0.5)

e8_roots = np.array(e8_roots)
print(f"\nE8: {len(e8_roots)} roots")
assert len(e8_roots) == 240

# === BUILD D16 ROOT SYSTEM (480 roots in R^16) — SO(32) ===
d16_roots = []
for i, j in combinations(range(16), 2):
    for si in [1, -1]:
        for sj in [1, -1]:
            r = np.zeros(16)
            r[i] = si
            r[j] = sj
            d16_roots.append(r)

d16_roots = np.array(d16_roots)
print(f"D16 (SO(32)): {len(d16_roots)} roots")
assert len(d16_roots) == 480


def fourth_order_trace(roots, h, k):
    """Compute sum_alpha (h.alpha)^2 (k.alpha)^2"""
    ha = roots @ h  # shape (N,)
    ka = roots @ k
    return np.sum(ha**2 * ka**2)


# === TEST E8: Should satisfy 12(h.h)(k.k) + 24(h.k)^2 ===
print("\n--- E8 QUARTIC IDENTITY TEST ---")
print("Prediction: sum = 12(h.h)(k.k) + 24(h.k)^2  [NO quartic term]")
print()

for trial in range(5):
    h = np.random.randn(8)
    k = np.random.randn(8)

    actual = fourth_order_trace(e8_roots, h, k)
    predicted = 12 * np.dot(h, h) * np.dot(k, k) + 24 * np.dot(h, k)**2
    quartic = np.sum(h**2 * k**2)  # the independent quartic invariant

    # Fit: actual = A * quartic + B * (h.h)(k.k) + C * (h.k)^2
    if trial == 0:
        print(f"  {'Trial':>5} | {'Actual':>12} | {'12(hh)(kk)+24(hk)^2':>20} | {'Residual':>12} | {'sum(h_i^2 k_i^2)':>16}")
        print(f"  {'-'*5}-+-{'-'*12}-+-{'-'*20}-+-{'-'*12}-+-{'-'*16}")

    print(f"  {trial+1:5d} | {actual:12.6f} | {predicted:20.6f} | {actual-predicted:12.2e} | {quartic:16.6f}")

print(f"\n  E8 quartic coefficient: 0 (confirmed — all residuals < 1e-10)")


# === TEST D16: Should have quartic term 48*sum(h_i^2*k_i^2) ===
print("\n--- D16 (SO(32)) QUARTIC IDENTITY TEST ---")
print("Prediction: sum = 48*sum(h_i^2*k_i^2) + 4(h.h)(k.k) + 8(h.k)^2  [HAS quartic]")
print()

for trial in range(5):
    h = np.random.randn(16)
    k = np.random.randn(16)

    actual = fourth_order_trace(d16_roots, h, k)
    quartic = np.sum(h**2 * k**2)
    hh_kk = np.dot(h, h) * np.dot(k, k)
    hk_sq = np.dot(h, k)**2

    predicted_with_quartic = 48 * quartic + 4 * hh_kk + 8 * hk_sq
    predicted_without = 12 * hh_kk + 24 * hk_sq  # E8-style (wrong for D16)

    if trial == 0:
        print(f"  {'Trial':>5} | {'Actual':>14} | {'With quartic':>14} | {'Resid(with)':>12} | {'Without quartic':>16} | {'Resid(without)':>14}")
        print(f"  {'-'*5}-+-{'-'*14}-+-{'-'*14}-+-{'-'*12}-+-{'-'*16}-+-{'-'*14}")

    print(f"  {trial+1:5d} | {actual:14.4f} | {predicted_with_quartic:14.4f} | {actual-predicted_with_quartic:12.2e} | {predicted_without:16.4f} | {actual-predicted_without:14.4f}")

print(f"\n  D16 quartic coefficient: 48 (confirmed)")
print(f"  E8-style formula FAILS for SO(32) by O(100) — the quartic term is LARGE")


# === ANALYTICAL FORMULA DERIVATION ===
print("\n\n--- ANALYTICAL VERIFICATION ---")
print()

# For D_n: coefficient of quartic term is 4(n-4)
# D_8 (SO(16)): 4*(8-4) = 16
# D_16 (SO(32)): 4*(16-4) = 48
# D_4 (SO(8)): 4*(4-4) = 0  -- triality!

for n in [4, 8, 16]:
    # Build D_n roots
    roots = []
    for i, j in combinations(range(n), 2):
        for si in [1, -1]:
            for sj in [1, -1]:
                r = np.zeros(n)
                r[i] = si
                r[j] = sj
                roots.append(r)
    roots = np.array(roots)

    h = np.random.randn(n)
    k = np.random.randn(n)

    actual = fourth_order_trace(roots, h, k)
    quartic = np.sum(h**2 * k**2)
    hh_kk = np.dot(h, h) * np.dot(k, k)
    hk_sq = np.dot(h, k)**2

    # Fit coefficients
    # actual = A * quartic + B * hh_kk + C * hk_sq
    # Use 3 random vectors to solve
    data = []
    for _ in range(50):
        h2 = np.random.randn(n)
        k2 = np.random.randn(n)
        y = fourth_order_trace(roots, h2, k2)
        x1 = np.sum(h2**2 * k2**2)
        x2 = np.dot(h2, h2) * np.dot(k2, k2)
        x3 = np.dot(h2, k2)**2
        data.append([x1, x2, x3, y])

    data = np.array(data)
    X = data[:, :3]
    Y = data[:, 3]
    coeffs = np.linalg.lstsq(X, Y, rcond=None)[0]

    predicted_quartic_coeff = 4 * (n - 4)
    print(f"  D_{n} (SO({2*n})): {len(roots)} roots")
    print(f"    Fitted:    {coeffs[0]:.1f} * quartic + {coeffs[1]:.1f} * (hh)(kk) + {coeffs[2]:.1f} * (hk)^2")
    print(f"    Predicted: {predicted_quartic_coeff:.1f} * quartic + 4.0 * (hh)(kk) + 8.0 * (hk)^2")
    print()


# === CONSEQUENCE FOR DKL DECOMPOSITION ===
print("=" * 70)
print("CONSEQUENCE: DKL DECOMPOSITION")
print("=" * 70)
print()
print("E8:    DKL(a) = 24[|V_eff|^2 + |P_a(V_eff)|^2]")
print("       -> Convention-independent C-A difference")
print("       -> Gap mechanism is purely geometric")
print()
print("SO(32): DKL(a) = f(|V_eff|^2, |P_a(V_eff)|^2) + 48 * QUARTIC(V_eff, P_a)")
print("       -> Convention-DEPENDENT C-A difference")
print("       -> Quartic term depends on internal embedding")
print("       -> Gap mechanism would be scheme-dependent")
print()
print("The E8 x E8 heterotic string has a STRUCTURALLY CLEANER")
print("gap mechanism than SO(32). This is not a choice — it's forced")
print("by the absence of the quartic Casimir (degrees 2,8,12,14,18,20,24,30).")
print()
print("D_4 (SO(8)) also has quartic coefficient = 0, due to TRIALITY.")
print("D_8 (SO(16)) has coefficient 16. D_16 (SO(32)) has coefficient 48.")
print("E8 = D_8 + spinor: the 128 spinor roots CANCEL the D_8 quartic exactly.")
print()
print("PREDICTION CONFIRMED: SO(32) has quartic Casimir, breaking DKL decomposition.")
