#!/usr/bin/env python3
"""
Diagnostic: Are the basis functions genuine sections of O(-5)?

The BKN bound λ ≥ 10 applies ONLY to functions in H¹(S, O(-5)).
A function f(a,b) represents a section of O(-5) iff the transition
    g = a^5 · f (in x₀=1 chart, d'=1/a)
is smooth at d'=0.

Test:
  - 1/P^{5/2} → transition g = a^5/P^{5/2}. In homogeneous coords:
    1/P^{5/2} = |x₃|^5/Σ^{5/2}. Weight: λ^0 λ̄^0 / |λ|^5 = |λ|^{-5}.
    This has HALF-INTEGER P power → NOT smooth on CP³.

  - 1/P^5 → transition g = a^5/P^5. In homogeneous coords:
    1/P^5 = x̄₃^5 x₃^5 / Σ^5. Weight: (λλ̄)^5/(λλ̄)^5 ... wait.

    Actually: 1/P^5 in chart x₃=1 = |x₃|^{10}/Σ^5 = x₃^5 x̄₃^5/Σ^5.
    Under x→λx: (λx₃)^5(λ̄x̄₃)^5/(|λ|^2 Σ)^5 = |λ|^{10} · x₃^5 x̄₃^5 / (|λ|^{10} Σ^5) = 1/P^5.
    So 1/P^5 has weight 0 → section of O(0), NOT O(-5)!

    But wait: as a REPRESENTATIVE in the x₃=1 chart, what does it represent?
    A section s of O(-5) satisfies s_{x₃=1}(a,b) = a^{-5} · s_{x₀=1}(b',c',d').
    So s_{x₀=1} = a^5 · s_{x₃=1}.
    For s = 1/P^5: s_{x₀=1} = a^5/P^5.

    Homogeneously: x₀^5 x̄₃^5 x₃^5 / (x₃^5 · Σ^5) = x₀^5 x̄₃^5/Σ^5.
    Under x→λx: λ^5 x₀^5 · λ̄^5 x̄₃^5 / (|λ|^{10} Σ^5) = x₀^5 x̄₃^5/Σ^5.
    Weight 0 in the x₀=1 chart too. So the transition is self-consistent
    ONLY if 1/P^5 is O(0), not O(-5).

    KEY REALIZATION: 1/P^5 is a section of O(0) (a smooth function on S),
    not a section of O(-5). The P^5 weight in the Dirichlet form is the
    FIBER METRIC of O(-5). Using 1/P^5 as a section of O(-5) is a TYPE ERROR.

So what IS a section of O(-5)?

In homogeneous coords: F(x) with F(λx) = λ^{-5} F(x).
Example: x̄₃^5/Σ^5 has weight λ̄^5/|λ|^{10} = λ^{-5}. YES! Weight -5.
In x₃=1 chart: x̄₃^5/Σ^5 = 1/P^5 ... wait, that's the same thing!

Hmm. x̄₃^5 = |x₃|^{10}/x₃^5. In x₃=1: x̄₃^5 = 1.
Σ^5 = (|x₃|² P)^5 = P^5 in x₃=1.
So x̄₃^5/Σ^5 = 1/P^5 in x₃=1. ✓

Under x→λx: x̄₃^5/Σ^5 → λ̄^5 x̄₃^5/(|λ|^{10} Σ^5) = (λ̄/|λ|²)^5 · x̄₃^5/Σ^5 = λ^{-5} · x̄₃^5/Σ^5.
Weight -5! So this IS a section of O(-5).

But in x₃=1 chart, the representative is 1/P^5.
Contradiction? No — the representative DEPENDS ON THE TRIVIALIZATION.

The point: O(-5) is trivialized in each chart. In x₃=1: e_{-5} = x₃^{-(-5)} = x₃^5 (trivializing section).
A section s = F(x) · e_{-5}^{-1}... no wait.

In chart x₃=1: O(n) is trivialized by (x₃)^{-n}. So a section s is represented by:
f(a,b) = s / x₃^{-n} = s · x₃^n.

For O(-5): f = s · x₃^{-5}. In x₃=1: f = s. So f IS the section value directly.

In x₀=1: O(-5) is trivialized by x₀^5. Representative: f' = s · x₀^5.
Transition: f = (x₃/x₀)^5 · f' = d'^5/a^{-5} ... I'm confusing myself.

Let me just DO the computation two ways and compare.

For f = 1/P^5 as the O(-5) representative in x₃=1:
BKN says R(f) = Q/M ≥ 10 where
Q = ∫ g^{αβ̄} P^5 (∂_α f̄)(∂_{β̄} f) dV
M = ∫ P^5 |f|² dV = ∫ P^{-5} dV

For f = conj(s)/P^d where s ∈ H⁰(O(d)) is a degree-d monomial:
In homogeneous coords: f represents the section x̄^J/(|x₃|^{2d} P^d) · x₃^{-(-5)} ...

You know what, I'll just COMPUTE both R(1/P^5) and R(1/P^{5/2}) and compare.
Both should give ≥ 10 IF they're genuine O(-5) sections.
If only one does, we learn which normalization is correct.
"""

import numpy as np
from math import pi
import sys, time

sys.stdout.reconfigure(encoding='utf-8')

N_MC = 200000
DOMAIN_R = 5.0
RNG_SEED = 2026
ZETA3 = np.exp(2j * pi / 3)
C_FLOOR = 0.02

print("=" * 72)
print("SECTION DIAGNOSTIC — Integer vs half-integer P-power")
print("=" * 72)

rng = np.random.default_rng(RNG_SEED)
u = rng.uniform(-DOMAIN_R, DOMAIN_R, (4, N_MC))
a_raw = u[0] + 1j * u[1]
b_raw = u[2] + 1j * u[3]
w_raw = -1.0 - a_raw**3 - b_raw**3
valid = np.abs(w_raw) > 1e-8
a_base, b_base, w_base = a_raw[valid], b_raw[valid], w_raw[valid]
c_principal = np.abs(w_base)**(1/3) * np.exp(1j * np.angle(w_base) / 3)
a_all = np.tile(a_base, 3)
b_all = np.tile(b_base, 3)
c_all = np.concatenate([c_principal, ZETA3*c_principal, ZETA3**2*c_principal])
mask = np.abs(c_all) > C_FLOOR
a_all, b_all, c_all = a_all[mask], b_all[mask], c_all[mask]
ab, bb, cb = np.conj(a_all), np.conj(b_all), np.conj(c_all)
N = len(a_all)

P = np.abs(a_all)**2 + np.abs(b_all)**2 + np.abs(c_all)**2 + 1.0
dc_da = -a_all**2 / c_all**2; dc_db = -b_all**2 / c_all**2
dcb_dab = -ab**2 / cb**2; dcb_dbb = -bb**2 / cb**2
dP_da  = ab + cb * dc_da; dP_dab = a_all + c_all * dcb_dab
dP_db  = bb + cb * dc_db; dP_dbb = b_all + c_all * dcb_dbb

JdJ_11 = 1.0 + np.abs(dc_da)**2; JdJ_12 = np.conj(dc_da) * dc_db
JdJ_22 = 1.0 + np.abs(dc_db)**2; P2 = P**2
JdXb_1 = ab + np.conj(dc_da) * cb; JdXb_2 = bb + np.conj(dc_db) * cb
XJ_1 = a_all + c_all * dc_da; XJ_2 = b_all + c_all * dc_db
g11 = JdJ_11/P - JdXb_1*XJ_1/P2; g12 = JdJ_12/P - JdXb_1*XJ_2/P2
g21 = np.conj(g12); g22 = JdJ_22/P - JdXb_2*XJ_2/P2
det_g = (g11*g22 - g12*g21).real

good = (det_g > 1e-15) & (g11.real > 0) & np.isfinite(det_g)
for nm in ['a_all','b_all','c_all','ab','bb','cb','P','P2','det_g',
           'g11','g12','g21','g22','dc_da','dc_db','dcb_dab','dcb_dbb',
           'dP_da','dP_dab','dP_db','dP_dbb']:
    exec(f"{nm}={nm}[good]")
N = len(a_all)

ds = np.where(det_g > 1e-20, det_g, 1.0)
ginv11 = (g22/ds).real; ginv12 = -g12/ds
ginv21 = -g21/ds; ginv22 = (g11/ds).real
domain_vol = (2*DOMAIN_R)**4
weights = det_g * domain_vol / (3*N_MC)
vol_est = np.sum(weights)
vol_exact = 3*pi**2/2
print(f"  R={DOMAIN_R}, N={N}, Vol={vol_est:.4f} ({vol_est/vol_exact:.4f}x)")


def rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, label=""):
    """Compute Rayleigh quotient for O(-5) twisted Laplacian."""
    h_inv = P**5
    w_twist = h_inv * weights
    M = np.sum(np.abs(phi)**2 * w_twist).real
    Q = np.sum((
        ginv11 * dphi_da * dphi_dab +
        ginv12 * dphi_da * dphi_dbb +
        ginv21 * dphi_db * dphi_dab +
        ginv22 * dphi_db * dphi_dbb
    ) * w_twist).real
    R = Q / M
    status = "PASS ✓" if R > 9.5 else ("CLOSE" if R > 8.0 else "FAIL ✗")
    print(f"  {label:30s}: R={R:10.4f}  M={M:.4e}  Q={Q:.4e}  [{status}]")
    return R


print(f"\n--- Test functions for O(-5) ---")
print(f"  BKN bound: λ ≥ 10")

# 1. φ = 1/P^{5/2} (HALF-integer: NOT a genuine O(-5) section)
phi = P**(-2.5)
dphi_da  = -2.5 * P**(-3.5) * dP_da
dphi_db  = -2.5 * P**(-3.5) * dP_db
dphi_dab = -2.5 * P**(-3.5) * dP_dab
dphi_dbb = -2.5 * P**(-3.5) * dP_dbb
rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, "1/P^{5/2} (half-int)")

# 2. φ = 1/P^5 (INTEGER: genuine O(-5) section via x̄₃^5/Σ^5)
phi = P**(-5.0)
dphi_da  = -5.0 * P**(-6.0) * dP_da
dphi_db  = -5.0 * P**(-6.0) * dP_db
dphi_dab = -5.0 * P**(-6.0) * dP_dab
dphi_dbb = -5.0 * P**(-6.0) * dP_dbb
rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, "1/P^5 (integer)")

# 3. φ = ā/P^{5/2} (HALF-integer)
phi = ab * P**(-2.5)
dphi_dab = P**(-2.5) + ab * (-2.5) * P**(-3.5) * dP_dab
dphi_dbb = ab * (-2.5) * P**(-3.5) * dP_dbb
dphi_da = a_all * (-2.5) * P**(-3.5) * dP_da  # d(a·P^{-5/2})/da ... wait, conj(φ) = a/P^{5/2}
# ∂(φ̄)/∂a = ∂(a/P^{5/2})/∂a = P^{-5/2} + a·(-5/2)P^{-7/2}·∂P/∂a
dphi_da = P**(-2.5) + a_all * (-2.5) * P**(-3.5) * dP_da
dphi_db = a_all * (-2.5) * P**(-3.5) * dP_db
rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, "ā/P^{5/2} (half-int)")

# 4. φ = ā/P^6 (INTEGER: genuine section; a^p ā^q / P^{max(p,q)+5} with p=0,q=1 → P^6)
phi = ab * P**(-6.0)
dphi_dab = P**(-6.0) + ab * (-6.0) * P**(-7.0) * dP_dab
dphi_dbb = ab * (-6.0) * P**(-7.0) * dP_dbb
dphi_da = a_all * (-6.0) * P**(-7.0) * dP_da
dphi_db = a_all * (-6.0) * P**(-7.0) * dP_db
rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, "ā/P^6 (integer)")

# 5. φ = a/P^6 (INTEGER: p=1,q=0 → max(1,0)+5 = 6)
phi = a_all * P**(-6.0)
dphi_dab = a_all * (-6.0) * P**(-7.0) * dP_dab
dphi_dbb = a_all * (-6.0) * P**(-7.0) * dP_dbb
# ∂(φ̄)/∂a = ∂(ā/P^6)/∂a = ā·(-6)P^{-7}·∂P/∂a
dphi_da = ab * (-6.0) * P**(-7.0) * dP_da
dphi_db = ab * (-6.0) * P**(-7.0) * dP_db
rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, "a/P^6 (integer)")

# 6. φ = |a|²/P^6 (INTEGER: p=q=1 → max(1,1)+5=6)
phi = np.abs(a_all)**2 * P**(-6.0)
# ∂φ/∂ā = a·P^{-6} + |a|²·(-6)P^{-7}·∂P/∂ā
dphi_dab = a_all * P**(-6.0) + np.abs(a_all)**2 * (-6.0) * P**(-7.0) * dP_dab
dphi_dbb = np.abs(a_all)**2 * (-6.0) * P**(-7.0) * dP_dbb
# ∂(φ̄)/∂a = ā·P^{-6} + |a|²·(-6)P^{-7}·∂P/∂a
dphi_da = ab * P**(-6.0) + np.abs(a_all)**2 * (-6.0) * P**(-7.0) * dP_da
dphi_db = np.abs(a_all)**2 * (-6.0) * P**(-7.0) * dP_db
rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, "|a|²/P^6 (integer)")

# 7. φ = c/P^6 (INTEGER: c is coord with chain rule on surface)
phi = c_all * P**(-6.0)
# ∂φ/∂ā = c·(-6)P^{-7}·∂P/∂ā  (c doesn't depend on ā? Wait, on surface c = c(a,b) holomorphically)
# c is holomorphic in a,b: ∂c/∂ā = 0. ∂c̄/∂ā = ∂c̄/∂ā via chain rule on surface.
# Actually c̄ depends on ā, b̄: dc̄/dā = -ā²/c̄²
# ∂φ/∂ā = c·(-6)P^{-7}·∂P/∂ā
dphi_dab = c_all * (-6.0) * P**(-7.0) * dP_dab
dphi_dbb = c_all * (-6.0) * P**(-7.0) * dP_dbb
# ∂(φ̄)/∂a = ∂(c̄/P^6)/∂a = (dc̄/da)·P^{-6} + c̄·(-6)P^{-7}·∂P/∂a
# dc̄/da = dc̄/dā · dā/da = 0 (c̄ doesn't depend on a since dc̄/da = 0 for holo c)
# Wait: c̄ = conj(c(a,b)). So ∂c̄/∂a = conj(∂c/∂ā) = 0 (c is holomorphic in a).
dphi_da = cb * (-6.0) * P**(-7.0) * dP_da
dphi_db = cb * (-6.0) * P**(-7.0) * dP_db
rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, "c/P^6 (integer)")

# 8. φ = c̄/P^6 (antiholo coord: p=0, q=0 for a,b but c̄ has anti_deg 1 → P^6)
phi = cb * P**(-6.0)
# ∂φ/∂ā = (∂c̄/∂ā)·P^{-6} + c̄·(-6)P^{-7}·∂P/∂ā
# ∂c̄/∂ā = dcb_dab
dphi_dab = dcb_dab * P**(-6.0) + cb * (-6.0) * P**(-7.0) * dP_dab
dphi_dbb = dcb_dbb * P**(-6.0) + cb * (-6.0) * P**(-7.0) * dP_dbb
# ∂(φ̄)/∂a = ∂(c/P^6)/∂a = (dc/da)·P^{-6} + c·(-6)P^{-7}·∂P/∂a
dphi_da = dc_da * P**(-6.0) + c_all * (-6.0) * P**(-7.0) * dP_da
dphi_db = dc_db * P**(-6.0) + c_all * (-6.0) * P**(-7.0) * dP_db
rayleigh_Om5(phi, dphi_da, dphi_db, dphi_dab, dphi_dbb, "c̄/P^6 (integer)")

print(f"\n{'=' * 72}")
print("INTERPRETATION")
print("=" * 72)
print("  Half-integer P-powers are NOT genuine sections of O(-5).")
print("  Integer P-powers should satisfy the BKN bound R ≥ 10.")
print("  If integer powers PASS and half-integer FAIL: diagnosis confirmed.")
print("  All v3-v6 used half-integer P-powers for O(±5) → invalid results.")
