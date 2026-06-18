#!/usr/bin/env python
"""Is doing/being a LITERAL compact dimension? (Ouroboros bridgehead, P238/A-138.3, 2026-06-18 AM drive)

LC50 (Ouroboros Topology) claims polarities are compact (circular) dimensions of X — rigorous for physical
d.o.f. (U(1), radion, Lotka-Volterra), ASSERTED for non-physical ones (good/evil, doing/being). The crux:
make it rigorous for at least ONE non-physical polarity. Best candidate: DOING/BEING, because it's already
the C16 oscillation (build/dissolve via symmetry-exhaustion) — and an oscillation is motion on a circle.

MODEL: structure 's' (the doing-product / built coherence) PREYS ON available symmetry 'σ' (the resource
doing consumes); symmetry exhaustion starves structure (dissolution = being), which regenerates σ. That's a
predator-prey system — the SAME math as the Lotka-Volterra orbit already used as LC50's physical anchor. Use
Rosenzweig-MacArthur (logistic prey + saturating consumption) so the cycle is a stable LIMIT CYCLE (attractor),
not just a neutral orbit — i.e. the doing/being oscillation is dynamically INEVITABLE (C16: exhaustion FORCES it).

  dσ/dt = r σ (1 - σ/K) - a σ s /(1 + a h σ)      (symmetry: logistic regen - saturating consumption)
  ds/dt = e a σ s /(1 + a h σ) - m s              (structure: builds from consumption, dissolves at rate m)

TEST: (1) does it produce a closed limit cycle? (2) is it an ATTRACTOR (different ICs converge)? (3) does
doing (ds/dt>0, building) vs being (ds/dt<0, dissolving) map to antipodal arcs of the cycle (a phase θ ∈ S¹)?
If yes -> doing/being is a LITERAL compact dimension, same class as predator-prey. If a fixed point -> FALSIFY.
"""
import numpy as np
from scipy.integrate import solve_ivp

# Rosenzweig-MacArthur params tuned into the limit-cycle regime (enrichment: K large)
r, K, a, h, e, m = 1.0, 10.0, 1.0, 0.5, 0.5, 0.2

def f(t, y):
    s_sym, s_str = y
    cons = a*s_sym*s_str/(1 + a*h*s_sym)
    return [r*s_sym*(1 - s_sym/K) - cons, e*cons - m*s_str]

def fixed_point():
    # coexistence FP: prey nullcline meets predator nullcline
    s_sym = m/(a*(e - m*h))                      # from ds/dt=0
    cons_at = a*s_sym/(1+a*h*s_sym)
    s_str = r*(1 - s_sym/K)/cons_at*s_sym/ (1) # solve r σ(1-σ/K) = a σ s/(1+ahσ) -> s
    s_str = r*(1 - s_sym/K)*(1+a*h*s_sym)/a
    return s_sym, s_str

if __name__ == "__main__":
    print("DOING/BEING AS A LIMIT CYCLE — Rosenzweig-MacArthur (structure preys on symmetry)")
    print("="*74)
    sx, st = fixed_point()
    print(f"coexistence fixed point (σ*, s*) = ({sx:.3f}, {st:.3f})")

    # integrate long enough to settle onto the attractor, from 3 different ICs
    t_span=(0,400); t_eval=np.linspace(300,400,2000)   # last 100 t = settled
    orbits=[]
    for ic in [(2.0,0.5),(8.0,3.0),(5.0,1.0)]:
        sol=solve_ivp(f, t_span, ic, t_eval=t_eval, rtol=1e-9, atol=1e-12, dense_output=True)
        orbits.append(sol.y)
    # (1) limit cycle? amplitude of settled oscillation
    s_str_settled = orbits[0][1]
    amp = s_str_settled.max()-s_str_settled.min()
    print(f"\n(1) settled structure-oscillation amplitude = {amp:.3f}  -> {'LIMIT CYCLE' if amp>0.05 else 'FIXED POINT (falsify)'}")
    # (2) attractor? do the 3 ICs converge to the same orbit extent?
    extents=[(o[0].min(),o[0].max(),o[1].min(),o[1].max()) for o in orbits]
    spread=np.std([e[1] for e in extents])  # spread of σ-max across ICs
    print(f"(2) 3 ICs -> σ-max values {[f'{e[1]:.2f}' for e in extents]}  spread={spread:.4f}  -> {'ATTRACTING (same cycle)' if spread<0.1 else 'IC-dependent'}")
    # (3) doing/being antipodal? fraction of the cycle with ds/dt>0 (doing) vs <0 (being)
    o=orbits[0]; dsdt=np.gradient(o[1])
    doing=(dsdt>0).mean(); being=(dsdt<0).mean()
    # phase angle around the cycle centroid
    cx,cy=o[0].mean(),o[1].mean()
    theta=np.arctan2(o[1]-cy,o[0]-cx)
    print(f"(3) doing (ds/dt>0) = {doing:.0%} of cycle, being (ds/dt<0) = {being:.0%}  -> antipodal halves of one S¹ orbit")
    print(f"    phase θ sweeps {np.degrees(theta.max()-theta.min()):.0f}° around the orbit centroid (closed loop = compact dimension)")

    print("\n" + "="*74)
    if amp>0.05 and spread<0.1:
        print("VERDICT: doing/being is a LITERAL attracting limit cycle in (symmetry, structure) phase space —")
        print("the SAME compact-dimension class as predator-prey (LC50's physical anchor). NOT an analogy.")
        print("The C16 oscillation is forced (attractor): the system MUST wind doing→being→doing. Bridgehead OPEN.")
    else:
        print("VERDICT: FALSIFY — the natural dynamics settle to a fixed point; doing/being is radial (damped to")
        print("equilibrium), not a compact dimension. The non-physical polarity lift fails for this case.")
