"""Does 'distinct roles' imply separability? Counterexample via a shared resource.

Two factors x,y with STRICTLY distinct roles: x improves output A only, y improves output B only.
J(x,y) = A(x) * B(y),  A(x)=1-exp(-ax),  B(y)=1-exp(-by)   (increasing, concave, independent forms).
Distinct roles by construction: dA/dy = 0, dB/dx = 0. If 'distinct roles => separable' is TRUE, the
optimal allocation x* should never couple to b. Add a shared budget x+y<=Bud and watch.

PREDICT (0.85): x* independent of b when budget SLACK (separable); x* depends on b when budget BINDS
(interaction). => interaction localizes to where the shared resource binds, NOT to role-overlap.
"""
import numpy as np
from scipy.optimize import minimize_scalar

a, b = 1.0, 3.0  # distinct role-efficiencies (b's role is 3x more resource-efficient)


def A(x): return 1 - np.exp(-a * x)
def B(y): return 1 - np.exp(-b * y)


def best_xy(lam, bparam):
    """maximize J = A(x)*B_b(y) - lam*(x+y) over x,y>=0  (resource PRICED at lam, not hard-capped).
    lam large = scarce/binding; lam small = abundant/slack. Returns x*, y*."""
    from scipy.optimize import minimize
    def neg(v):
        x, y = v
        if x < 0 or y < 0:
            return 1e9
        return -(A(x) * (1 - np.exp(-bparam * y)) - lam * (x + y))
    r = minimize(neg, x0=[1.0, 1.0], method="Nelder-Mead",
                 options=dict(xatol=1e-6, fatol=1e-9, maxiter=5000))
    return r.x


print("distinct roles by construction: dA/dy=0, dB/dx=0  (x->A only, y->B only)\n")
print("shared resource PRICED at lam (lam small=slack/abundant, lam large=scarce/binding).")
print("does the optimal x* couple to the PARTNER param b?  (b=3 vs b=9)\n")
print(f"{'lam':>8} {'x*(b=3)':>9} {'x*(b=9)':>9} {'|Δx*|':>9} {'A(x*) b=3':>10}  reading")
for lam in (1e-3, 0.01, 0.05, 0.15, 0.4, 0.8):
    x3, y3 = best_xy(lam, 3.0)
    x9, y9 = best_xy(lam, 9.0)
    d = abs(x3 - x9)
    sep = "separable" if d < 0.02 else "INTERACTION"
    print(f"{lam:>8.3f} {x3:>9.3f} {x9:>9.3f} {d:>9.3f} {A(x3):>10.3f}  {sep}")

print("\n-> roles are orthogonal at EVERY lam (dA/dy=dB/dx=0). If x* is independent of b at small lam")
print("   (slack) and couples to b at large lam (scarce), the interaction is created by the SHARED")
print("   RESOURCE binding, not by role-overlap. (Slack: B(y*)~1 so A'(x*)=lam decouples from b.)")
