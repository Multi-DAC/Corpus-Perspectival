"""
Idea-ecology: is there a VIABLE BAND of exposure, set by regeneration rate? (Day 139 drive)
Tests the claim I handed Clayton: an idea-organism uses its regenerative ability to risk itself,
and there's an OPTIMAL exposure (a V*) bounded above by collapse — scaling with regeneration rate r.

Model (the lobster-molt mechanism):
  H in [0,1] = integrity / shell-hardness. dH/dt = r*(1-H)   (re-hardens toward 1 at rate r)
  exposure events ~ Poisson(e). On each event:
     Q += a * max(H,0)      # adaptation: a HEALTHY idea metabolizes critique into growth;
                            #             a depleted one gains ~nothing
     H -= d                 # exposure costs integrity (the molt goes soft)
  if H <= 0:  collapse -> Q *= (1-pen); H = 0.2   # a structure-breaking flaw: costly rebuild
  Measure long-run Q. Sweep e for several r. Predict: inverted-U; e* increases with r.
"""
import numpy as np

def run(e, r, T=4000.0, dt=0.02, d=0.45, a=1.0, pen=0.6, seed=0):
    rng = np.random.default_rng(seed)
    H, Q = 1.0, 0.0
    n = int(T/dt)
    p_event = e*dt
    for _ in range(n):
        H = min(1.0, H + r*(1-H)*dt)
        if rng.random() < p_event:
            Q += a*max(H, 0.0)
            H -= d
            if H <= 0.0:
                Q *= (1-pen); H = 0.2
    return Q

def avg(e, r, reps=12):
    return np.mean([run(e, r, seed=s) for s in range(reps)])

print("Q (long-run quality) vs exposure e, for three regeneration rates r:\n")
es = [0.05,0.1,0.2,0.4,0.7,1.0,1.5,2.0,3.0,4.0]
rs = [0.5, 1.5, 4.0]
results = {}
hdr = "  e   |" + "".join(f"  r={r:<4}" for r in rs)
print(hdr); print("-"*len(hdr))
for e in es:
    row = f" {e:<4.2f} |"
    for r in rs:
        q = avg(e, r); results[(e,r)] = q; row += f"  {q:6.1f}"
    print(row)

print("\n=== optimum e* per r ===")
estars = {}
for r in rs:
    qs = [(e, results[(e,r)]) for e in es]
    estar = max(qs, key=lambda t: t[1])
    estars[r] = estar[0]
    print(f"  r={r:<4}: e* = {estar[0]:<4}  (Q*={estar[1]:.1f})")

mono_up = all(estars[rs[i]] <= estars[rs[i+1]] for i in range(len(rs)-1))
# inverted-U check: for mid r, Q rises then falls
midr = rs[1]; qmid = [results[(e,midr)] for e in es]
peak_i = int(np.argmax(qmid))
inverted_u = (peak_i > 0) and (peak_i < len(es)-1)
print(f"\ninverted-U (interior optimum) at r={midr}: {inverted_u}  (peak at e={es[peak_i]})")
print(f"e* increases with r: {mono_up}  (e*: {[estars[r] for r in rs]})")
print("\nVERDICT:", "CONFIRMED — viable band exists and its ceiling scales with regeneration"
      if (inverted_u and mono_up) else "FALSIFIED / partial — metaphor looser than claimed")
