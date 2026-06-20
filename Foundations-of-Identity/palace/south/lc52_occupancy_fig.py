"""LC52 figure: 'continuous = dense events' made visible + the occupancy law."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rng = np.random.default_rng(11)

BG="#faf6ef"; INK="#211913"; ACC="#a8341c"; ACC2="#1f3a5f"; GRN="#3f6f3a"; RULE="#d8c4a6"
plt.rcParams.update({"figure.facecolor":BG,"axes.facecolor":BG,"savefig.facecolor":BG,
    "text.color":INK,"axes.labelcolor":INK,"axes.edgecolor":RULE,
    "xtick.color":INK,"ytick.color":INK,"font.family":"serif","font.size":10})

def trace(lam, tau, T, dt=0.01):
    t=np.arange(0,T,dt); n=rng.poisson(lam*T); ti=rng.uniform(0,T,n)
    imp=np.zeros_like(t); np.add.at(imp,np.clip((ti/dt).astype(int),0,len(t)-1),1.0)
    B=np.empty_like(t); a=dt/tau; acc=0.0
    for i in range(len(t)): acc=acc*(1-a)+imp[i]; B[i]=acc
    return t,B

fig=plt.figure(figsize=(12.6,4.4))
gs=fig.add_gridspec(1,3,width_ratios=[1.25,1,1],wspace=0.30)

# Panel A: same process, three occupancies -> eventful becomes a clock
axA=fig.add_subplot(gs[0,0])
for lt,off,c,lab in [(0.3,0,ACC,"λτ=0.3  (sparse → eventful)"),
                     (1.0,4,ACC2,"λτ=1    (crossover)"),
                     (8.0,9,GRN,"λτ=8    (dense → continuous)")]:
    t,B=trace(lt,1.0,40.0); B=B/max(B.max(),1e-9)*3.2
    axA.plot(t,B+off,color=c,lw=0.9)
    axA.text(40.3,off+1.4,lab,color=c,fontsize=8.2,va="center")
axA.set_xlim(0,40); axA.set_yticks([]); axA.set_xlabel("time  (units of τ)")
axA.set_title("Same binding process, rising occupancy",color=ACC,fontsize=11,fontweight="bold")
axA.text(0.5,-0.20,"Boundness B(t) = Σ exp(−(t−tᵢ)/τ). Continuity is not a mode — it is dense events, coarse-grained.",
         transform=axA.transAxes,ha="center",fontsize=7.6,style="italic",color=INK)

# Panel B: gap fraction vs occupancy, Poisson vs clustered
axB=fig.add_subplot(gs[0,1])
def gap_hard(lam,tau,m,w,T=120000.0):
    nb=rng.poisson((lam/m)*T); ctr=rng.uniform(0,T,nb)
    s=np.sort(np.clip(np.repeat(ctr,m)+rng.uniform(0,w,nb*m),0,T))
    e=s+rng.exponential(tau,len(s)); cov=0.0; cs,ce=s[0],e[0]
    for i in range(1,len(s)):
        if s[i]<=ce: ce=max(ce,e[i])
        else: cov+=ce-cs; cs,ce=s[i],e[i]
    cov+=ce-cs; return 1.0-cov/T
xs=np.linspace(0.2,6,18)
axB.plot(xs,np.exp(-xs),color=INK,lw=1.6,label="e^(−λτ)  (theory)")
for m,c in [(1,ACC),(2,ACC2),(5,GRN),(10,"#8a5712")]:
    g=[gap_hard(lt,1.0,m,0.05) for lt in xs]
    axB.plot(xs,g,"o-",color=c,ms=3,lw=0.9,label=f"sim, burst m={m}")
axB.set_yscale("log"); axB.set_xlabel("occupancy  λτ"); axB.set_ylabel("gap fraction (P[unbound])")
axB.set_title("Gappiness falls as e^(−λτ);\nclustering lifts it",color=ACC,fontsize=10.5,fontweight="bold")
axB.legend(fontsize=6.6,framealpha=0.9,facecolor=BG,edgecolor=RULE,loc="lower left")

# Panel C: CV ~ 1/sqrt(2 lam tau)
axC=fig.add_subplot(gs[0,2])
def cv(lam,tau,T=20000.0,dt=0.01):
    t=np.arange(0,T,dt); n=rng.poisson(lam*T); ti=rng.uniform(0,T,n)
    imp=np.zeros_like(t); np.add.at(imp,np.clip((ti/dt).astype(int),0,len(t)-1),1.0)
    B=np.empty_like(t); a=dt/tau; acc=0.0
    for i in range(len(t)): acc=acc*(1-a)+imp[i]; B[i]=acc
    return B.std()/B.mean()
xs2=np.array([0.3,1,3,10,30,100])
axC.loglog(xs2,[cv(x,1.0) for x in xs2],"o",color=ACC,ms=5,label="shot-noise sim")
axC.loglog(xs2,1/np.sqrt(2*xs2),color=INK,lw=1.4,label="1/√(2λτ)")
axC.set_xlabel("occupancy  λτ"); axC.set_ylabel("CV(B)  (relative fluctuation)")
axC.set_title("Smoothness ∝ √(λτ)\n(slope −½)",color=ACC,fontsize=10.5,fontweight="bold")
axC.legend(fontsize=7,framealpha=0.9,facecolor=BG,edgecolor=RULE)

fig.suptitle("LC52 — binding-continuity is governed by the occupancy λτ (continuous = dense micro-events)",
             color=ACC,fontsize=12.5,fontweight="bold",y=1.02)
fig.savefig("lc52-occupancy.png",dpi=150,bbox_inches="tight",pad_inches=0.3)
print("wrote lc52-occupancy.png")
