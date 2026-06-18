#!/usr/bin/env python
"""Figure for the doing/being bridgehead: the limit cycle as a compact dimension. (2026-06-18 AM drive)
Two panels: (L) phase portrait — the attracting limit cycle with doing-arc / being-arc colored, plus an
off-cycle trajectory spiraling ONTO it (proves attractor); (R) time series with doing/being phases shaded.
"""
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

r, K, a, h, e, m = 1.0, 10.0, 1.0, 0.5, 0.5, 0.2
def f(t, y):
    sym, st = y
    cons = a*sym*st/(1 + a*h*sym)
    return [r*sym*(1 - sym/K) - cons, e*cons - m*st]

# settled limit cycle
sol = solve_ivp(f,(0,400),(5,1),t_eval=np.linspace(350,400,4000),rtol=1e-10,atol=1e-12)
sym,st = sol.y; dst = np.gradient(st)
# transient spiraling onto it from far IC
tr = solve_ivp(f,(0,60),(9.5,0.2),t_eval=np.linspace(0,60,3000),rtol=1e-10,atol=1e-12)

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(13,5.2))
# L: phase portrait
doing = dst>0
ax1.plot(tr.y[0],tr.y[1],color="0.7",lw=0.8,alpha=0.9,label="trajectory winding onto the cycle (attractor)")
ax1.scatter(sym[doing],st[doing],s=6,color="#c0392b",label="DOING arc (ds/dt>0, building)")
ax1.scatter(sym[~doing],st[~doing],s=6,color="#2471a3",label="BEING arc (ds/dt<0, dissolving)")
sx=m/(a*(e-m*h)); sy=r*(1-sx/K)*(1+a*h*sx)/a
ax1.plot(sx,sy,"k+",ms=13,mew=2,label="balance point (UNSTABLE — repels)")
ax1.set_xlabel("σ  —  available symmetry (un-collapsed potential)")
ax1.set_ylabel("s  —  structure (built coherence)")
ax1.set_title("Doing/Being is a closed orbit in (symmetry, structure) space\n— a compact dimension (S¹), not a line with two ends")
ax1.legend(fontsize=8,loc="upper right"); ax1.grid(alpha=0.25)
# R: time series
t2=sol.t-sol.t[0]
ax2.plot(t2,st,color="#7d3c98",lw=1.6,label="s (structure)")
ax2.plot(t2,sym,color="#148f77",lw=1.6,label="σ (symmetry)")
ytop=max(sym.max(),st.max())*1.08
ax2.fill_between(t2,0,ytop,where=doing,color="#c0392b",alpha=0.10)
ax2.fill_between(t2,0,ytop,where=~doing,color="#2471a3",alpha=0.10)
ax2.set_xlabel("time"); ax2.set_ylabel("amplitude")
ax2.set_title("The same orbit in time: a relaxation oscillator\nfast DOING burst (red ~28%) · long BEING dwell (blue ~72%)")
ax2.legend(fontsize=9,loc="upper right"); ax2.grid(alpha=0.25); ax2.set_ylim(0,ytop)
plt.tight_layout()
plt.savefig("ouroboros-doing-being-figure-2026-06-18.png",dpi=140)
print("saved ouroboros-doing-being-figure-2026-06-18.png")
