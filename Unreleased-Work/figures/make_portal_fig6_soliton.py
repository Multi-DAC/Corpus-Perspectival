"""Fig. 6 — the EXHIBITED gauged dilatonic Q-ball (R12). Day 136 creative drive."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.optimize import minimize
rcParams.update({"font.size": 11, "axes.titlesize": 11.5, "axes.titleweight": "bold",
                 "figure.dpi": 140, "savefig.dpi": 140, "axes.grid": True, "grid.alpha": 0.25,
                 "axes.axisbelow": True})
INK="#1a2b3c"; HOT="#c0392b"; COOL="#2471a3"; GOLD="#b9770e"; GREEN="#1e8449"; PUR="#6c3483"
m=1.0; f0=1.0; S1=0.5; U0=0.3; c_em=1.0/(8*np.pi); k_sig=0.1
def vol(R): return (4/3)*np.pi*R**3
def parts(R,s,Q,a):
    V=vol(R)
    return (4*np.pi*R**2*S1, V*U0, Q**2/(2*V*f0**2), c_em*Q**2/(R*np.exp(a*s)),
            V*0.5*m**2*s**2+4*np.pi*R**2*k_sig*s**2)
def Etot(x,Q,a):
    R,s=x
    return 1e12 if R<=1e-3 else sum(parts(R,s,Q,a))
def sol(Q,a,x0=(2,0.2)):
    r=minimize(Etot,x0,args=(Q,a),method="Nelder-Mead",options=dict(xatol=1e-6,fatol=1e-9,maxiter=8000))
    return r.x[0], r.x[1], sum(parts(r.x[0],r.x[1],Q,a))

fig,ax=plt.subplots(1,3,figsize=(14.4,5.0))

# (a) E(R) well with components, Q=10,a=0.5,sig=0.15
R=np.linspace(0.3,5,300); s=0.15; Q=10; a=0.5
P=np.array([parts(r,s,Q,a) for r in R]); tot=P.sum(1)
ax[0].plot(R,tot,color=INK,lw=2.6,label="total E(R)")
ax[0].plot(R,P[:,2],color=HOT,lw=1.6,ls="--",label="charge-kinetic ~Q²/R³ (binds)")
ax[0].plot(R,P[:,1]+P[:,4],color=GREEN,lw=1.6,ls="--",label="volume+radion ~R³ (anti-disperse)")
ax[0].plot(R,P[:,3],color=GOLD,lw=1.6,ls=":",label="EM ~Q²/R (anti-collapse)")
Rm=R[np.argmin(tot)]; ax[0].plot(Rm,tot.min(),"o",color=PUR,ms=10,zorder=5)
ax[0].annotate("exhibited\nsoliton",xy=(Rm,tot.min()),xytext=(1.95,tot.min()+15),
               color=PUR,fontsize=9.5,ha="center",arrowprops=dict(arrowstyle="->",color=PUR))
ax[0].set_xlabel("bubble radius R (1/m)"); ax[0].set_ylabel("energy E"); ax[0].set_ylim(0,92)
ax[0].set_title("(a) Both ends diverge → a real minimum"); ax[0].legend(frameon=False,fontsize=8.5,loc="upper center",ncol=1)

# (b) E* ~ Q (Q-ball signature)
Qs=np.array([5,10,20,40,80,160,320]); Es=[]; Rs=[]
for Q in Qs:
    R_,s_,E_=sol(Q,0.5); Es.append(E_); Rs.append(R_)
Es=np.array(Es); Rs=np.array(Rs)
ax[1].loglog(Qs,Es,"o-",color=COOL,lw=2.2,ms=7,label="E* (soliton energy)")
pE=np.polyfit(np.log(Qs),np.log(Es),1)[0]
ax[1].loglog(Qs,Es[0]*(Qs/Qs[0]),color=HOT,ls="--",lw=1.4,label="linear E∝Q (Q-ball)")
ax[1].set_xlabel("charge Q"); ax[1].set_ylabel("soliton energy E*")
ax[1].set_title(f"(b) E* ∝ Q^{pE:.2f} — the Q-ball stability signature")
ax[1].legend(frameon=False,fontsize=8.5,loc="upper left")

# (c) dilaton lowers energy + sags
aa=np.linspace(0,3,16); Ea=[]; sa=[]
for a in aa:
    R_,s_,E_=sol(40.0,a); Ea.append(E_); sa.append(s_)
Ea=np.array(Ea)
ax2=ax[2].twinx()
l1=ax[2].plot(aa,100*(Ea-Ea[0])/Ea[0],color=GREEN,lw=2.4,label="energy change vs a=0")
l2=ax2.plot(aa,sa,color=PUR,lw=2.2,ls="--",label="radion sag σ_in")
ax[2].axhline(0,color=INK,lw=0.8,ls=":")
ax[2].set_xlabel("dilatonic coupling a"); ax[2].set_ylabel("ΔE vs a=0 (%)",color=GREEN)
ax2.set_ylabel("radion sag σ_in",color=PUR)
ax[2].set_title("(c) The radion actively binds (≈−21% by a=3)")
ax[2].tick_params(axis="y",labelcolor=GREEN); ax2.tick_params(axis="y",labelcolor=PUR)
ls=l1+l2; ax[2].legend(ls,[x.get_label() for x in ls],frameon=False,fontsize=8.5,loc="lower left")

fig.suptitle("Fig. 6 — The gauged dilatonic Q-ball, exhibited (R12): the portal's existence made concrete",
             fontsize=12,fontweight="bold")
fig.tight_layout(rect=[0,0,1,0.96]); fig.savefig("portal-fig6-soliton.png"); plt.close(fig)
print(f"wrote portal-fig6-soliton.png   (E~Q^{pE:.3f})")
