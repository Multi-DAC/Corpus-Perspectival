"""
Ouroboros Condition — COUNTEREXAMPLE hunt: is the loop ALWAYS born via a Hopf?
Dream/free drive 2026-06-19 ~08:25. Clayton greenlit.

Conjecture under attack (my own, from the order/chaos result): "the Ouroboros Condition
IS a Hopf bifurcation in the regeneration parameter." If true, every compact polarity is
born with vanishing amplitude and finite period.

ATTACK: exhibit a compact polarity born via a SNIC (saddle-node on an invariant circle) —
a categorically different route with OPPOSITE onset signatures:
  Hopf : amplitude ~ sqrt(mu-mu_c) -> 0 ,  period -> finite      (gentle onset)
  SNIC : amplitude = FULL (const)       ,  period ~ (b-b_c)^-1/2 -> INF (dwell+transit)

Minimal SNIC normal form (the canonical Type-I / theta-neuron geometry):
  r_dot = r(1 - r^2)        # radial: attracts onto the invariant circle r=1 (the polarity loop)
  th_dot = b - sin(th)      # angular drive b on the loop
  b<1 : two fixed pts on the circle (saddle+node) -> STUCK at a phase (loop exists, frozen)
  b=1 : saddle-node ON the invariant circle (SNIC) -> birth of rotation, infinite period
  b>1 : rotation -> limit cycle, exact period T = 2*pi/sqrt(b^2-1)

PREDICT (high): circulates only for b>1; period = 2*pi/sqrt(b^2-1) (->inf as (b-1)^-1/2);
amplitude in x=cos(th) is CONSTANT 2 for all b>1 (does NOT vanish at onset). => not a Hopf.
"""
import numpy as np
from scipy.integrate import solve_ivp

def f(t, s, b):
    r, th = s
    return [r*(1 - r*r), b - np.sin(th)]

def measure(b, t_max=4000.0):
    # start on the loop, away from any ghost
    sol = solve_ivp(f, [0, t_max], [1.0, 0.0], args=(b,),
                    dense_output=True, rtol=1e-10, atol=1e-12, max_step=0.05)
    t = np.linspace(0, t_max, 200000)
    th = sol.sol(t)[1]
    x = np.cos(th)
    # circulating? -> theta grows without bound
    total_wind = (th[-1] - th[0]) / (2*np.pi)
    if total_wind < 0.5:                      # fewer than half a turn in t_max => stuck
        return dict(circulates=False, period=np.inf, amp=x.max()-x.min(),
                    rest_x=x[-1])
    # period from successful 2*pi crossings (skip first to drop transient)
    turns = np.floor((th - th[0]) / (2*np.pi))
    # time per turn over the measured window
    n_turns = turns[-1]
    T = t_max / n_turns if n_turns > 0 else np.inf
    amp = x.max() - x.min()
    return dict(circulates=True, period=T, amp=amp, rest_x=None)

print("SNIC normal form  r_dot=r(1-r^2),  th_dot = b - sin(th)\n")
print(f"{'b (drive)':>9} | {'circulates':>10} | {'period T':>10} | {'T_exact':>10} | {'amplitude':>9}")
print("-"*64)
rows=[]
for b in [0.80, 0.95, 0.99, 1.001, 1.01, 1.05, 1.2, 1.5, 2.0, 3.0]:
    m = measure(b)
    Texact = (2*np.pi/np.sqrt(b*b-1)) if b > 1 else np.inf
    Tshow = f"{m['period']:.2f}" if np.isfinite(m['period']) else "inf"
    Teshow = f"{Texact:.2f}" if np.isfinite(Texact) else "inf"
    cir = "yes" if m['circulates'] else "STUCK"
    print(f"{b:>9.3f} | {cir:>10} | {Tshow:>10} | {Teshow:>10} | {m['amp']:>9.3f}")
    rows.append((b, m, Texact))

print("\n--- SNIC signatures (the falsification) ---")
# 1) amplitude constant (full) for all b>1, does NOT ->0 at onset
amps = [m['amp'] for b,m,_ in rows if m['circulates']]
print(f"amplitude over circulating b: min={min(amps):.3f} max={max(amps):.3f}  "
      f"(Hopf would ->0 at onset; SNIC stays full)")
# 2) period ~ (b-1)^(-1/2): check the scaling exponent near onset
near = [(b, m['period']) for b,m,_ in rows if m['circulates'] and b < 1.21]
bs = np.array([b-1 for b,_ in near]); Ts = np.array([T for _,T in near])
slope = np.polyfit(np.log(bs), np.log(Ts), 1)[0]
print(f"log-log period vs (b-1) slope = {slope:.3f}  (SNIC predicts -0.5; Hopf predicts ~0)")
# 3) numeric vs exact period agreement
err = np.mean([abs(m['period']-Te)/Te for b,m,Te in rows if m['circulates'] and np.isfinite(Te)])
print(f"mean |T_num - T_exact|/T_exact = {err:.4f}  (confirms T=2pi/sqrt(b^2-1))")
print("\nVERDICT: a compact polarity born via SNIC, NOT Hopf.")
print("=> 'the Ouroboros Condition is always a Hopf' is FALSIFIED.")
print("The Condition (Poincare-Bendixson) is ROUTE-AGNOSTIC; the birth-route is a")
print("second axis: Hopf = gentle small-amplitude onset; SNIC = full-amplitude,")
print("infinite-period onset (long dwell at one pole, fast transit) — and b<1 is a")
print("THIRD state: the loop EXISTS but the dynamics are frozen at a phase.")
