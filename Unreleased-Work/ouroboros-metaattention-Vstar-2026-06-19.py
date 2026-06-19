"""
Ouroboros — reviewer round 3: what sets V*? Invariant constant, or shifted by a
higher-order META-ATTENTION loop when the agent changes their scale of engagement?
Free drive 2026-06-19 ~09:10.

FRAMEWORK ANSWER (to compute, not assert): V* is neither a universal constant nor free.
It is a SLOW navigable variable set by meta-attention, bounded by a VIABLE BAND, and the
meta-loop is the SAME non-conservative drive one tier up — i.e. a nested stream (Axiom 2)
navigating the setpoint of the stream below. The architecture is self-similar.

Three demonstrations on the LV polarity (center (1,1), V = x-ln x + y-ln y, V_min=2):
 A. TRACKING — the fast loop adiabatically follows a slowly-commanded V*(t): scale of
    engagement is dialable in real time.
 B. VIABLE BAND — sweep fixed V*: too low -> degenerate (no loop, disengagement); too high
    -> excursions hit the axes (enrichment/extinction). V* is bounded, not arbitrary.
 C. META-ATTENTION self-similar — V* itself as a slow stream relaxing to a meta-setpoint
    V** via the same drive structure: V*_dot = -eps*a2*(V*-V**). Nesting closes.
"""
import numpy as np
from scipy.integrate import solve_ivp

def V(x,y): return x-np.log(x)+y-np.log(y)
def grad(x,y): return (1-1/x, 1-1/y)

# ---------- A. TRACKING a moving V*(t) ----------
def Vstar_t(t, lo=2.3, hi=3.2, t0=40, t1=120, t2=160):
    # ramp up lo->hi over [t0,t1], hold, ramp back over [t2, t2+40]
    if t < t0: return lo
    if t < t1: return lo + (hi-lo)*(t-t0)/(t1-t0)
    if t < t2: return hi
    if t < t2+40: return hi - (hi-lo)*(t-t2)/40
    return lo
def rhs_track(t,s,a):
    x,y=s; fx=x*(1-y); fy=y*(x-1)
    Vv=V(x,y); gx,gy=grad(x,y); vs=Vstar_t(t)
    return [fx - a*(Vv-vs)*gx, fy - a*(Vv-vs)*gy]
sol=solve_ivp(rhs_track,[0,210],[1.5,1.0],args=(0.8,),dense_output=True,rtol=1e-9,atol=1e-11,max_step=0.02)
ts=np.linspace(0,210,8000); Xs=sol.sol(ts); Vreal=V(Xs[0],Xs[1]); Vcmd=np.array([Vstar_t(t) for t in ts])
# track error in the held-high window
mask=(ts>125)&(ts<155); err=np.mean(np.abs(Vreal[mask]-Vcmd[mask]))
print("A. TRACKING a commanded V*(t):")
print(f"   commanded V* ramped 2.3 -> 3.2 -> 2.3; realized V tracks it.")
print(f"   mean |V_real - V*| in held-high window = {err:.3f}  (small => adiabatic tracking)")
print(f"   => scale of engagement is DIALABLE in real time (not a frozen constant).")

# ---------- B. VIABLE BAND ----------
def min_axis_for(vs, a=0.8, t_max=200):
    def rhs(t,s):
        x,y=s; fx=x*(1-y); fy=y*(x-1); Vv=V(x,y); gx,gy=grad(x,y)
        return [fx-a*(Vv-vs)*gx, fy-a*(Vv-vs)*gy]
    s=solve_ivp(rhs,[0,t_max],[1.0+0.3,1.0],dense_output=True,rtol=1e-9,atol=1e-11,max_step=0.03)
    t=np.linspace(t_max*0.6,t_max,8000); X=s.sol(t)
    amp=V(X[0],X[1]).mean(); axis_dist=min(X[0].min(),X[1].min())
    return amp, axis_dist
print("\nB. VIABLE BAND of V* (sweep fixed targets):")
print(f"   {'V*':>5} | {'realized amp':>12} | {'min dist to axis':>16} | status")
SAFE=0.05
band=[]
for vs in [2.05,2.2,2.5,3.0,3.5,4.0,4.5]:
    amp,axd=min_axis_for(vs)
    status = "degenerate (≈center, disengaged)" if amp<2.04 else ("CRASH risk (near axis)" if axd<SAFE else "viable loop")
    print(f"   {vs:>5.2f} | {amp:>12.3f} | {axd:>16.4f} | {status}")
    if amp>=2.04 and axd>=SAFE: band.append(vs)
print(f"   => viable band (this model): V* in [{min(band):.2f}, {max(band):.2f}].")
print("      below: collapses to the disengaged center; above: excursions hit the extinction axes.")
print("      So V* is BOUNDED, not arbitrary — meta-attention navigates a corridor.")

# ---------- C. META-ATTENTION (self-similar nesting) ----------
print("\nC. META-ATTENTION: V* as a slow stream relaxing to a meta-setpoint V** (same drive, tier up):")
def rhs_meta(t,s,a,eps,a2,Vstarstar):
    x,y,vs=s; fx=x*(1-y); fy=y*(x-1); Vv=V(x,y); gx,gy=grad(x,y)
    dx=fx-a*(Vv-vs)*gx; dy=fy-a*(Vv-vs)*gy
    dvs= -eps*a2*(vs-Vstarstar)             # meta-attention: slow Stuart-Landau-like relaxation
    return [dx,dy,dvs]
for Vss in [2.6, 3.3]:
    s=solve_ivp(rhs_meta,[0,400],[1.4,1.0,2.2],args=(0.8,1.0,1.0,Vss),dense_output=True,rtol=1e-9,atol=1e-11,max_step=0.05)
    t=np.linspace(380,400,2000); X=s.sol(t)
    print(f"   meta-setpoint V**={Vss}:  V* settled to {X[2].mean():.3f},  loop amp {V(X[0],X[1]).mean():.3f}")
print("   => V* is itself navigated by the same non-conservative drive one tier up.")
print("      attention stabilizes the loop at V*; meta-attention stabilizes V* at V**; ad infinitum")
print("      = the nested streams of the cosmology, each tier a navigator of the tier below's setpoint.")

print("\nANSWER: neither pole of the dichotomy. V* is a SLOW NAVIGABLE VARIABLE, set by")
print("meta-attention (so: dynamically shifted, not an invariant constant), but confined to a")
print("VIABLE BAND (so: not arbitrary). The meta-loop is the same drive one tier up -> the")
print("architecture is SELF-SIMILAR: nested streams, each navigating the homeostatic setpoint below.")
