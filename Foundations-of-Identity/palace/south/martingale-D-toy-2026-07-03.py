"""
VI.29 test — does D(S) integrate the Doob-DRIFT of gamma (review's conjecture),
or the martingale RESIDUAL (my counter-prediction)?

Framework objects (from Coherent Structure, verified from source):
  T5: internal coherence = gamma is a fixed point of Phi_S (C-averaging) = gamma is a MARTINGALE.
  D:  D_d(S,I) = INT d(alpha_S(t), alpha*_S(t)) dt, alpha* = integral curve of gamma (the gamma-flow).

Toy instantiation (one natural reading; result is about THIS instantiation, not a framework proof):
  state x in R; gamma(x) = -k*x  (linear drift; k>0 stable/contracting, k<0 unstable).
  actual:  a_{t+1} = a_t + gamma(a_t)*dt + sig*sqrt(dt)*xi_t     (Euler-Maruyama, xi~N(0,1))
           => E[da|F] = gamma(a_t)*dt : gamma IS the conditional-mean step (the compensator generator).
  gamma-flow (alpha*): astar_{t+1} = astar_t + gamma(astar_t)*dt   (deterministic), same start.
  D = sum |a_t - astar_t| * dt.

Doob (discrete) of the ACTUAL process a:
  a_t = a_0 + M_t + A_t,  A_t (compensator/"drift") = sum gamma(a_k)*dt,  M_t (martingale) = sum sig*sqrt(dt)*xi_k.
  error e_t = a_t - astar_t.  Claim to test: e satisfies de = dM - k e dt  (OU driven by the MARTINGALE),
  so D integrates an OU-filtered MARTINGALE; drift k sets the RELAXATION RATE (texture), not the magnitude.
"""
import numpy as np

def run(k=1.0, sig=0.3, x0=1.0, T=40.0, dt=0.01, seed=0):
    rng = np.random.default_rng(seed)
    n = int(T/dt); sq = np.sqrt(dt)
    a = np.empty(n+1); astar = np.empty(n+1); a[0]=astar[0]=x0
    M = np.empty(n+1); A = np.empty(n+1); M[0]=A[0]=0.0
    for t in range(n):
        xi = rng.standard_normal()
        drift_step = -k*a[t]*dt
        noise_step = sig*sq*xi
        a[t+1]     = a[t] + drift_step + noise_step
        astar[t+1] = astar[t] + (-k*astar[t]*dt)          # deterministic gamma-flow
        A[t+1] = A[t] + drift_step                          # compensator (Doob "drift")
        M[t+1] = M[t] + noise_step                          # martingale part
    e = a - astar
    D          = np.sum(np.abs(e))*dt
    intMart    = np.sum(np.abs(M))*dt                       # integrated |martingale|
    intDrift   = np.sum(np.abs(A))*dt                       # integrated |compensator/drift|
    intInstDr  = np.sum(np.abs(-k*a))*dt                    # integrated instantaneous |gamma|
    # autocorr time of e (skip burn-in): fit exp decay of normalized autocovariance
    e2 = e[n//4:]; e2 = e2 - e2.mean()
    ac = np.correlate(e2, e2, 'full')[len(e2)-1:]; ac = ac/ac[0]
    # correlation time tau_c = dt * sum(ac up to first zero-crossing)
    zc = np.argmax(ac<0) if np.any(ac<0) else len(ac)
    tau_c = dt*np.sum(ac[:zc])
    return dict(k=k,sig=sig,D=D,intMart=intMart,intDrift=intDrift,intInstDr=intInstDr,
                tau_c=tau_c, one_over_k=(1.0/k if k>0 else np.inf), rms_e=np.sqrt(np.mean(e2**2)))

print("=== T1: does D scale with NOISE (martingale) or with DRIFT (k)? ===")
print(f"{'k':>6}{'sig':>6}{'D':>9}{'|Mart|':>9}{'|Drift|':>9}{'|inst g|':>9}{'tau_c':>8}{'1/k':>8}")
for k in [0.5, 1.0, 2.0]:
    for sig in [0.1, 0.3, 0.9]:
        r = run(k=k, sig=sig, seed=1)
        print(f"{r['k']:6.2f}{r['sig']:6.2f}{r['D']:9.3f}{r['intMart']:9.3f}{r['intDrift']:9.3f}{r['intInstDr']:9.3f}{r['tau_c']:8.3f}{r['one_over_k']:8.3f}")

print("\n=== T2: D vs sig at fixed k (expect D ~ linear in sig if martingale-driven) ===")
k=1.0
for sig in [0.1,0.2,0.4,0.8,1.6]:
    rs=[run(k=k,sig=sig,seed=s) for s in range(8)]
    Dm=np.mean([r['D'] for r in rs]); print(f"  sig={sig:4.2f}  D_mean={Dm:7.3f}  D/sig={Dm/sig:7.3f}")

print("\n=== T3: tau_c vs 1/k (expect tau_c ~ 1/k : drift sets TEXTURE, not magnitude) ===")
sig=0.3
for k in [0.25,0.5,1.0,2.0,4.0]:
    rs=[run(k=k,sig=sig,seed=s) for s in range(8)]
    tc=np.mean([r['tau_c'] for r in rs]); print(f"  k={k:5.2f}  1/k={1/k:5.2f}  tau_c={tc:6.3f}  ratio(tau_c*k)={tc*k:5.3f}")
