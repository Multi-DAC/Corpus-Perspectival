"""
Ouroboros Condition — THIRD worked case: order/chaos (the thermodynamic polarity).
Dream drive 2026-06-19 05:15.

Claim under test: the Ouroboros Condition (a polarity is COMPACT/circular iff it carries a
consume-exhaust-REGENERATE feedback) is, for order/chaos, a HOPF BIFURCATION in the
drive/throughput parameter. Below threshold -> collapse to a fixed point (the equilibrium
"chaos" sink, no sustained order). Above threshold -> stable limit cycle (compact).

Model: the Brusselator (Prigogine/Lefever) — the canonical dissipative-structure system,
order emerging from chaos via sustained throughput. THIS IS the order/chaos polarity as chemistry.
  dX/dt = A + X^2 Y - B X - X
  dY/dt = B X - X^2 Y
Fixed point: (X*,Y*) = (A, B/A). Hopf bifurcation at B = 1 + A^2.
A is the feed (throughput); B is the thermodynamic affinity/drive.

PREDICT (high): A=1 -> Hopf at B=2.  B=1.5 collapses to point; B=2.5 limit-cycles.
"""
import numpy as np
from scipy.integrate import solve_ivp

def brusselator(t, s, A, B):
    X, Y = s
    return [A + X*X*Y - B*X - X, B*X - X*X*Y]

def classify(A, B, t_max=400.0, settle=0.5):
    """Integrate, then measure the amplitude of X over the LATE window.
    Near-zero late amplitude => collapsed to a fixed point (POINT).
    Sustained amplitude => limit cycle (COMPACT)."""
    fp = (A, B/A)
    s0 = [fp[0] + 0.5, fp[1] - 0.5]          # perturb off the fixed point
    sol = solve_ivp(brusselator, [0, t_max], s0, args=(A, B),
                    dense_output=True, rtol=1e-9, atol=1e-12, max_step=0.1)
    t_late = np.linspace(t_max*settle, t_max, 4000)
    X_late = sol.sol(t_late)[0]
    amp = X_late.max() - X_late.min()
    # distance of the late trajectory from the fixed point
    drift = np.abs(X_late - fp[0]).mean()
    verdict = "COMPACT (limit cycle)" if amp > 1e-2 else "COLLAPSED (point)"
    return fp, amp, drift, verdict

A = 1.0
B_hopf = 1 + A*A
print(f"A = {A}   Hopf threshold B = 1+A^2 = {B_hopf}\n")
print(f"{'B (drive)':>10} | {'fixed pt':>14} | {'late amp':>10} | {'mean|X-X*|':>10} | verdict")
print("-"*78)
results = {}
for B in [0.8, 1.5, 1.9, 2.0, 2.1, 2.5, 3.0]:
    fp, amp, drift, verdict = classify(A, B)
    side = "below" if B < B_hopf else ("AT" if abs(B-B_hopf)<1e-9 else "above")
    print(f"{B:>10.2f} | ({fp[0]:.2f},{fp[1]:.2f}){'':>4} | {amp:>10.4f} | {drift:>10.4f} | {verdict}  [{side} Hopf]")
    results[B] = (amp, verdict)

print("\n--- VERDICT ---")
below = results[1.5][1]
above = results[2.5][1]
print(f"B=1.5 (below threshold): {below}")
print(f"B=2.5 (above threshold): {above}")
ok = ("COLLAPSED" in below) and ("COMPACT" in above)
print(f"\nOuroboros Condition as Hopf bifurcation CONFIRMED: {ok}")
print("Regeneration term (drive/throughput) crossing the Hopf threshold")
print("turns the order/chaos point into a circle. Same structure as:")
print("  good/evil  -> regeneration = the exit/free-will option")
print("  doing/being-> regeneration = the being/rest phase")
print("  order/chaos-> regeneration = energy/matter throughput (HERE)")
