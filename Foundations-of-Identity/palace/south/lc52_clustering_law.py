"""LC52 follow-up: is the clustered gap fraction exactly exp(-lam*tau * H_m/m)?
Tests the Boolean-model derivation (max of m Exp = tau*H_m) across lam*tau and m,
plus the finite-burst-window interpolation back to Poisson e^(-lam*tau)."""
import numpy as np
rng = np.random.default_rng(23)

def H(m):
    return float(np.sum(1.0 / np.arange(1, m + 1)))

def gap_clustered(lam, tau, m, w, T=400000.0):
    nb = rng.poisson((lam / m) * T)
    ctr = rng.uniform(0, T, nb)
    s = np.sort(np.clip(np.repeat(ctr, m) + rng.uniform(0, w, nb * m), 0, T))
    e = s + rng.exponential(tau, len(s))
    cov = 0.0; cs, ce = s[0], e[0]
    for i in range(1, len(s)):
        if s[i] <= ce:
            ce = max(ce, e[i])
        else:
            cov += ce - cs; cs, ce = s[i], e[i]
    cov += ce - cs
    return 1.0 - cov / T

# --- TEST (a): law across lam*tau and m, tight bursts (w = 1e-4 tau ~ point) ---
print("=== exp(-lam*tau * H_m/m) vs sim, tight bursts (w=1e-4 tau) ===")
print(f"{'lt':>4} {'m':>3} {'H_m/m':>7} {'sim_gap':>9} {'law':>9} {'abs_err':>8}")
tau = 1.0
for lt in [1.0, 3.0, 6.0]:
    lam = lt / tau
    for m in [1, 2, 5, 10, 20]:
        g = gap_clustered(lam, tau, m, w=1e-4 * tau)
        law = np.exp(-lt * H(m) / m)
        print(f"{lt:4.1f} {m:3d} {H(m)/m:7.4f} {g:9.4f} {law:9.4f} {abs(g-law):8.4f}")

# --- TEST (b): finite-w interpolation 0 -> >>tau should rise toward e^(-lt) ---
print("\n=== finite burst window: gap vs w (m=10, lam*tau=3) ===")
print("predict: w=0 -> exp(-lt*H_m/m); w>>tau -> declusters toward e^(-lt)=%.4f" % np.exp(-3.0))
print(f"{'w/tau':>7} {'sim_gap':>9}   [point-burst law=%.4f]" % np.exp(-3.0 * H(10) / 10))
for wf in [0.0001, 0.1, 0.5, 1.0, 3.0, 10.0, 50.0]:
    g = gap_clustered(3.0, 1.0, 10, w=wf * 1.0)
    print(f"{wf:7.3f} {g:9.4f}")

# --- TEST (c): m -> infinity, H_m/m ~ (ln m + gamma)/m -> 0 ---
print("\n=== m -> large: H_m/m -> 0 (gap -> 1 slowly), lam*tau=3 ===")
print(f"{'m':>5} {'H_m/m':>8} {'law_gap':>8}")
for m in [1, 10, 100, 1000]:
    print(f"{m:5d} {H(m)/m:8.4f} {np.exp(-3.0*H(m)/m):8.4f}")
print("\nDONE")
