#!/usr/bin/env python
"""Two figures for 'The Curvature of Good and Evil' (2026-06-18).
Fig A: the chart-unrolling schematic (the central metaphor) — a compact dimension (circle) flattened into a
       line, manufacturing false endpoints and hiding that you can wind through a pole.
Fig B: the good/evil result — (left) binary C/D drains to the all-defect point (a line to evil);
       (right) C/D/exit gives closed orbits in the strategy simplex (a circle no pole wins).
"""
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle

# ============================ FIG A: unroll schematic ============================
figA, (axc, axl) = plt.subplots(1, 2, figsize=(12, 5.0))

# -- circle panel --
th = np.linspace(0, 2*np.pi, 400)
axc.plot(np.cos(th), np.sin(th), color="#2c3e50", lw=2.2)
# antipodal poles
axc.scatter([1, -1], [0, 0], s=90, color=["#c0392b", "#2471a3"], zorder=5)
axc.annotate("pole A\n(e.g. order)", (1, 0), xytext=(1.18, 0.15), fontsize=10, color="#c0392b", weight="bold")
axc.annotate("pole B\n(e.g. chaos)", (-1, 0), xytext=(-1.95, 0.15), fontsize=10, color="#2471a3", weight="bold")
# winding arrow (you can go all the way around — through a pole, not into a wall)
arc = np.linspace(0.15*np.pi, 0.85*np.pi, 60)
axc.plot(1.18*np.cos(arc), 1.18*np.sin(arc), color="#27ae60", lw=1.6)
axc.add_patch(FancyArrowPatch((1.18*np.cos(arc[-2]),1.18*np.sin(arc[-2])),
              (1.18*np.cos(arc[-1]),1.18*np.sin(arc[-1])), arrowstyle="-|>", mutation_scale=18, color="#27ae60"))
axc.text(0, 1.34, "winding: push past a pole, arrive at its opposite", ha="center", fontsize=9.5, color="#27ae60", style="italic")
# the chart's cut point (seam)
axc.scatter([np.cos(-np.pi/2)], [np.sin(-np.pi/2)], s=70, marker="x", color="#8e44ad", zorder=6)
axc.annotate("chart cuts here\n(arbitrary seam)", (0, -1), xytext=(0.15, -1.5), fontsize=9, color="#8e44ad")
axc.set_title("THE TERRITORY: a compact dimension\n(no endpoints — you can wind forever)", fontsize=11)
axc.set_xlim(-2.2, 2.2); axc.set_ylim(-1.8, 1.6); axc.set_aspect("equal"); axc.axis("off")

# -- line panel (the flattened chart) --
axl.plot([0, 1], [0, 0], color="#2c3e50", lw=2.2)
# walls at the ends
for x in (0, 1):
    axl.plot([x, x], [-0.05, 0.05], color="#8e44ad", lw=3)
# place poles: cut at seam (-pi/2) -> unroll; A(theta=0) and B(theta=pi) land at 1/4 and 3/4 of the line
axl.scatter([0.25, 0.75], [0,0], s=90, color=["#c0392b","#2471a3"], zorder=5)
axl.annotate("pole A", (0.25,0), xytext=(0.18,0.12), fontsize=10, color="#c0392b", weight="bold")
axl.annotate("pole B", (0.75,0), xytext=(0.68,0.12), fontsize=10, color="#2471a3", weight="bold")
axl.annotate("seam\n(really ONE point)", (0,0), xytext=(-0.06,-0.28), fontsize=9, color="#8e44ad")
axl.annotate("seam\n(the SAME point)", (1,0), xytext=(0.80,-0.28), fontsize=9, color="#8e44ad")
axl.add_patch(FancyArrowPatch((0.5,0.42),(0.0,0.08), connectionstyle="arc3,rad=0.3", arrowstyle="-|>", mutation_scale=14, color="#8e44ad", lw=1.2))
axl.add_patch(FancyArrowPatch((0.5,0.42),(1.0,0.08), connectionstyle="arc3,rad=-0.3", arrowstyle="-|>", mutation_scale=14, color="#8e44ad", lw=1.2))
axl.text(0.5,0.48,"the two 'far ends' are the same point, joined", ha="center", fontsize=9, color="#8e44ad", style="italic")
axl.set_title("THE MAP: the chart unrolls it into a line\n(false 'endpoints'; the join is hidden)", fontsize=11)
axl.set_xlim(-0.15, 1.15); axl.set_ylim(-0.55, 0.6); axl.axis("off")

figA.suptitle("How a flattening chart manufactures 'opposites' from one circular dimension", fontsize=12.5, weight="bold")
figA.tight_layout(rect=[0,0,1,0.95])
figA.savefig("ouroboros-fig-unroll-2026-06-18.png", dpi=140)
print("saved ouroboros-fig-unroll-2026-06-18.png")

# ============================ FIG B: good/evil line vs circle ============================
# binary replicator: C vs D, prisoner's dilemma -> D fixed point
R_,T_,P_,S_ = 3.0,5.0,1.0,0.0
A2 = np.array([[R_,S_],[T_,P_]])
def rep2(t,y):
    x=np.array(y); f=A2@x; phi=x@f; return x*(f-phi)
# 3-strategy zero-sum cyclic dominance (C beats L, L beats D, D beats C) -> closed orbits
A3 = np.array([[0.,-1.,1.],[1.,0.,-1.],[-1.,1.,0.]])
def rep3(t,y):
    x=np.array(y); f=A3@x; phi=x@f; return x*(f-phi)

figB, (axb, axt) = plt.subplots(1, 2, figsize=(12, 5.2))

# -- binary panel: a line draining to D --
sol = solve_ivp(rep2,(0,40),[0.6,0.4],t_eval=np.linspace(0,40,200),rtol=1e-9,atol=1e-12)
axb.plot([0,1],[0,0], color="#2c3e50", lw=2.0)
axb.scatter([0],[0], s=110, facecolors="none", edgecolors="#c0392b", lw=2, zorder=5)  # C unstable
axb.scatter([1],[0], s=130, color="#1b2631", zorder=5)  # D stable (evil wins)
axb.annotate("all COOPERATE\n(unstable)", (0,0), xytext=(-0.04,0.10), fontsize=10, color="#c0392b", weight="bold")
axb.annotate("all DEFECT\n(stable — evil wins)", (1,0), xytext=(0.62,0.10), fontsize=10, color="#1b2631", weight="bold")
for x0 in np.linspace(0.12,0.88,7):
    axb.add_patch(FancyArrowPatch((x0,0),(x0+0.07,0), arrowstyle="-|>", mutation_scale=13, color="#7f8c8d"))
axb.text(0.5,-0.34,"NO EXIT: the moral dimension is a LINE\nthat drains to evil and stays", ha="center", fontsize=10.5, color="#1b2631")
axb.set_title("Binary good/evil", fontsize=12, weight="bold")
axb.set_xlim(-0.18,1.18); axb.set_ylim(-0.5,0.45); axb.axis("off")

# -- ternary panel: closed orbits in the C/D/L simplex --
def tern(xC,xD,xL):  # barycentric -> 2D
    return xD + 0.5*xL, (np.sqrt(3)/2)*xL
# triangle frame
vC=tern(1,0,0); vD=tern(0,1,0); vL=tern(0,0,1)
tri=np.array([vC,vD,vL,vC])
axt.plot(tri[:,0],tri[:,1], color="#2c3e50", lw=2.0)
axt.annotate("COOPERATE", vC, xytext=(vC[0]-0.02,vC[1]-0.11), fontsize=10, color="#c0392b", weight="bold", ha="center")
axt.annotate("DEFECT", vD, xytext=(vD[0]+0.0,vD[1]-0.11), fontsize=10, color="#1b2631", weight="bold", ha="center")
axt.annotate("EXIT / withdraw", vL, xytext=(vL[0],vL[1]+0.05), fontsize=10, color="#27ae60", weight="bold", ha="center")
# nested closed orbits
for ic in [(0.55,0.30,0.15),(0.45,0.35,0.20),(0.40,0.33,0.27)]:
    s=solve_ivp(rep3,(0,200),ic,t_eval=np.linspace(0,200,3000),rtol=1e-10,atol=1e-12)
    X,Y=tern(s.y[0],s.y[1],s.y[2])
    axt.plot(X,Y, lw=1.3, color="#2471a3", alpha=0.85)
# direction arrow on outer orbit
s=solve_ivp(rep3,(0,200),(0.55,0.30,0.15),t_eval=np.linspace(0,200,3000),rtol=1e-10,atol=1e-12)
X,Y=tern(s.y[0],s.y[1],s.y[2]); i=300
axt.add_patch(FancyArrowPatch((X[i],Y[i]),(X[i+1],Y[i+1]), arrowstyle="-|>", mutation_scale=20, color="#2471a3"))
# center fixed point
cx,cy=tern(1/3,1/3,1/3); axt.scatter([cx],[cy], s=60, marker="+", color="#8e44ad", zorder=5)
axt.text(0.5,-0.22,"WITH EXIT: closed ORBITS — a circle\nno pole ever wins (C→L→D→C forever)", ha="center", fontsize=10.5, color="#2471a3")
axt.set_title("Good/evil + the freedom to exit", fontsize=12, weight="bold")
axt.set_xlim(-0.15,1.15); axt.set_ylim(-0.35,1.05); axt.set_aspect("equal"); axt.axis("off")

figB.suptitle("Free will is the curvature: the exit option bends the moral line into a loop", fontsize=12.5, weight="bold")
figB.tight_layout(rect=[0,0,1,0.95])
figB.savefig("ouroboros-fig-goodevil-2026-06-18.png", dpi=140)
print("saved ouroboros-fig-goodevil-2026-06-18.png")
