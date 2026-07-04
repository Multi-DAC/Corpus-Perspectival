"""
Nonlinear-gamma test of the martingale/D correction (Day 153 morning follow-up).
Morning linear result: D integrates the OU-filtered MARTINGALE (mag = noise), drift sets texture (tau_c = 1/k).
Question: survive nonlinear gamma, or was linear special?

gamma(x) = -k*sin(x): stable well near 0 (gamma'=-k cos x=-k, contracting),
                       zero-contraction near +-pi/2 (gamma'=0),
                       unstable ridge near pi (gamma'=+k, expanding).
One field, THREE regimes. Predict: mag=martingale robust; texture tau_c~1/<-gamma'> on avg,
breaking near low/negative -gamma' regions.
"""
import numpy as np

def run(sig=0.3, x0=0.5, T=40.0, dt=0.005, seed=0):
    rng=np.random.default_rng(seed); n=int(T/dt); sq=np.sqrt(dt)
    g  = lambda x: -np.sin(x)
    gp = lambda x: -np.cos(x)
    a=np.empty(n+1); astar=np.empty(n+1); a[0]=astar[0]=x0
    for t in range(n):
        a[t+1]=a[t]+g(a[t])*dt+sig*sq*rng.standard_normal()
        astar[t+1]=astar[t]+g(astar[t])*dt
    e=a-astar; D=np.sum(np.abs(e))*dt
    mean_contract=np.mean(-gp(astar))                 # <-gamma'(astar)> along the flow
    e2=e[n//4:]; e2=e2-e2.mean()
    ac=np.correlate(e2,e2,'full')[len(e2)-1:]; ac=ac/ac[0]
    zc=np.argmax(ac<0) if np.any(ac<0) else len(ac); tau_c=dt*np.sum(ac[:zc])
    return dict(D=D, tau_c=tau_c, mc=mean_contract, rms_e=np.sqrt(np.mean(e2**2)))

def sweep(x0, sigs, seeds=10):
    out=[]
    for sig in sigs:
        rs=[run(sig=sig,x0=x0,seed=s) for s in range(seeds)]
        out.append((sig, np.mean([r['D'] for r in rs]), np.mean([r['tau_c'] for r in rs]),
                    np.mean([r['mc'] for r in rs]), np.mean([r['rms_e'] for r in rs])))
    return out

print("=== NONLINEAR gamma=-sin(x). Header: sig | D | D/sig | tau_c | meanContract | tc*mc ===")
for lbl,x0 in [("(a) stable well x0=0.5",0.5), ("(b) zero-contraction x0=1.5 (~pi/2)",1.5),
               ("(c) unstable ridge x0=3.0 (~pi)",3.0)]:
    print("---",lbl,"---")
    for sig,D,tc,mc,rms in sweep(x0,[0.05,0.1,0.2,0.4]):
        print(f"  {sig:5.2f}  D={D:7.3f}  D/sig={D/sig:7.3f}  tau_c={tc:6.3f}  mc={mc:6.3f}  tc*mc={tc*mc:6.3f}")

print("\n=== VERDICT: constant D/sig => martingale-driven (mag=noise); tc*mc~1 => texture=1/contraction ===")
for lbl,x0 in [("stable",0.5),("zero-g'",1.5),("unstable",3.0)]:
    r=sweep(x0,[0.05,0.1,0.2,0.4],seeds=12)
    ratios=[D/sig for sig,D,tc,mc,rms in r]
    cv=np.std(ratios)/np.mean(ratios)
    tcmc=np.mean([tc*mc for sig,D,tc,mc,rms in r])
    verdict = "LINEAR (martingale)" if cv<0.12 else "NONLINEAR (OU-broken)"
    print(f"  {lbl:9s}: D/sig CV={cv:.3f} -> {verdict:22s} | mean tc*mc={tcmc:.3f}")
