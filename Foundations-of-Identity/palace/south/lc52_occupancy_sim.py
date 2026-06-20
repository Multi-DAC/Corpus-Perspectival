"""LC52 computational spine: is binding-continuity governed by the occupancy lambda*tau?
Tests P1-P4 from lc52-binding-occupancy-computation-2026-06-20.md.

Model: binding = a point process of discrete micro-collapse events (rate lam), each
contributing a coherence pulse. Two readouts:
  (A) HARD holding-time (M/G/inf): event occupies system for Exp(tau); gap = P[N=0].
  (B) SOFT shot-noise: B(t)=sum exp(-(t-t_i)/tau); measure mean, CV, duty cycle.
Plus a CLUSTERED (bursty) arrival variant at matched mean rate to test P4.
"""
import numpy as np
rng = np.random.default_rng(7)

# ---------- (A) HARD occupancy: gap fraction vs lambda*tau, Poisson ----------
def gap_fraction_hard(lam, tau, T=200000.0):
    """Idle probability of an M/G/inf queue with Exp(tau) holding times.
    Simulate arrivals (Poisson rate lam), each busy for Exp(tau); measure fraction
    of time with zero busy servers."""
    n = rng.poisson(lam * T)
    starts = np.sort(rng.uniform(0, T, n))
    durations = rng.exponential(tau, n)
    ends = starts + durations
    # sweep-line: merge intervals, compute covered time
    order = np.argsort(starts)
    s = starts[order]; e = ends[order]
    covered = 0.0; cur_s, cur_e = s[0], e[0]
    for i in range(1, len(s)):
        if s[i] <= cur_e:
            cur_e = max(cur_e, e[i])
        else:
            covered += cur_e - cur_s; cur_s, cur_e = s[i], e[i]
    covered += cur_e - cur_s
    return 1.0 - covered / T   # gap (idle) fraction

print("=== P2: gap fraction vs occupancy (Poisson, hard holding) ===")
print(f"{'lam*tau':>8} {'sim_gap':>10} {'theory e^-x':>12} {'rel_err':>9}")
for lt in [0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0]:
    tau = 1.0; lam = lt / tau
    g = gap_fraction_hard(lam, tau)
    th = np.exp(-lt)
    print(f"{lt:8.2f} {g:10.4f} {th:12.4f} {abs(g-th)/th:9.3f}")

# ---------- (B) SOFT shot-noise: mean, CV, duty cycle vs lambda*tau ----------
def shot_noise_stats(lam, tau, T=20000.0, dt=0.01, thresh_frac=0.5):
    t = np.arange(0, T, dt)
    n = rng.poisson(lam * T)
    ti = rng.uniform(0, T, n)
    B = np.zeros_like(t)
    # accumulate decaying kernels via per-event add on a causal grid (vectorized-ish)
    idx = np.clip((ti / dt).astype(int), 0, len(t) - 1)
    impulse = np.zeros_like(t)
    np.add.at(impulse, idx, 1.0)
    # exponential smoothing == convolution with causal exp kernel
    alpha = dt / tau
    B = np.empty_like(t); acc = 0.0
    for i in range(len(t)):
        acc = acc * (1 - alpha) + impulse[i]
        B[i] = acc
    mean = B.mean(); cv = B.std() / mean if mean > 0 else np.nan
    duty = np.mean(B > thresh_frac * (lam * tau))   # "bound" = above half mean-occupancy
    return mean, cv, duty

print("\n=== P1/P3: shot-noise mean, CV vs occupancy (Poisson, soft kernel) ===")
print(f"{'lam*tau':>8} {'meanB':>8} {'CV_sim':>8} {'CV_th=1/sqrt(2x)':>16}")
for lt in [0.3, 1.0, 3.0, 10.0, 30.0]:
    tau = 1.0; lam = lt / tau
    m, cv, duty = shot_noise_stats(lam, tau)
    print(f"{lt:8.2f} {m:8.3f} {cv:8.3f} {1/np.sqrt(2*lt):16.3f}")

# ---------- (P4) CLUSTERED arrivals at matched mean rate ----------
def gap_fraction_clustered(lam, tau, m_burst, burst_w, T=200000.0):
    """Mean rate lam, but events come in bursts of size m_burst within window burst_w.
    Burst centers Poisson at rate lam/m_burst. Same holding Exp(tau)."""
    n_bursts = rng.poisson((lam / m_burst) * T)
    centers = rng.uniform(0, T, n_bursts)
    starts = np.repeat(centers, m_burst) + rng.uniform(0, burst_w, n_bursts * m_burst)
    starts = np.clip(starts, 0, T)
    starts = np.sort(starts)
    durations = rng.exponential(tau, len(starts))
    ends = starts + durations
    covered = 0.0; cur_s, cur_e = starts[0], ends[0]
    for i in range(1, len(starts)):
        if starts[i] <= cur_e:
            cur_e = max(cur_e, ends[i])
        else:
            covered += cur_e - cur_s; cur_s, cur_e = starts[i], ends[i]
    covered += cur_e - cur_s
    return 1.0 - covered / T

print("\n=== P4: clustering breaks single-parameter lam*tau control ===")
print("(matched lam*tau=3.0, tau=1.0; burst window w=0.05*tau << tau)")
print(f"{'m_burst':>8} {'gap_clustered':>14} {'e^-(lam*tau)':>13} {'e^-(lam*tau/m)':>15}")
lt = 3.0; tau = 1.0; lam = lt / tau
for m_b in [1, 2, 5, 10]:
    g = gap_fraction_clustered(lam, tau, m_b, burst_w=0.05 * tau)
    print(f"{m_b:8d} {g:14.4f} {np.exp(-lt):13.4f} {np.exp(-lt/m_b):15.4f}")

print("\nDONE")
