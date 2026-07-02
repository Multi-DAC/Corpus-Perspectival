"""
Collapse-timing generator — computational verification
======================================================
Claim (Day-152, palace/south/collapse-timing-generator-2026-07-02.md):
  For an OPTIMIZING inference system, the collapse-threshold height (= position
  on the LC28/32/38 collapse-timing axis) is a monotone function of the a-priori
  cost-asymmetry between premature vs delayed collapse (Wald/SPRT; Bogacz 2006).
  And the 'fail-safe direction' is NOT universal: it flips between the
  memory-regime (err-cost >> delay-cost -> late collapse) and the
  perception-regime (delay-cost >> err-cost -> early collapse).

This turns that cited claim into a MEASURED result (no hand-waving).

Model: drift-diffusion (symmetric absorbing bounds +/-a, drift v>0 toward the
correct bound, variance-rate sigma^2, start 0). Analytic DDM (Bogacz 2006):
    ER(a) = 1 / (1 + exp(2 a v / sigma^2))          # error probability
    DT(a) = (a/v) * tanh(a v / sigma^2)             # mean decision time
Cost per decision:
    C(a) = c_err * ER(a) + c_delay * DT(a)
Optimal threshold a* = argmin_a C(a).  Cost-asymmetry r = c_err / c_delay.

PREDICT (high conf): a*(r) increases monotonically in r; residual failure flips
from premature (high ER, low a*, perception) to over-cautious (high DT, high a*,
memory). If not -> implementation or understanding is wrong (high-info FALSIFY).

By Clawd. Day 152 - 2026-07-02.
"""
import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.random.seed(152)

# ---------- analytic DDM ----------
def error_rate(a, v, sigma):
    return 1.0 / (1.0 + np.exp(2.0 * a * v / sigma**2))

def decision_time(a, v, sigma):
    return (a / v) * np.tanh(a * v / sigma**2)

def expected_cost(a, v, sigma, c_err, c_delay):
    return c_err * error_rate(a, v, sigma) + c_delay * decision_time(a, v, sigma)

def optimal_threshold(v, sigma, c_err, c_delay, amax=80.0):
    r = minimize_scalar(lambda a: expected_cost(a, v, sigma, c_err, c_delay),
                        bounds=(1e-4, amax), method="bounded")
    return r.x

# ---------- Monte-Carlo verification of the analytic formulas ----------
def mc_ddm(a, v, sigma, dt=1e-3, n=6000, tmax=60.0):
    steps = int(tmax / dt)
    x = np.zeros(n); t = np.full(n, np.nan); done = np.zeros(n, bool); correct = np.zeros(n, bool)
    sq = sigma * np.sqrt(dt)
    for i in range(steps):
        act = ~done
        na = int(act.sum())
        if na == 0:
            break
        x[act] += v * dt + sq * np.random.randn(na)
        up = act & (x >= a); dn = act & (x <= -a)
        correct[up] = True
        for m in (up, dn):
            done[m] = True; t[m] = (i + 1) * dt
    return (1.0 - correct[done].mean()), np.nanmean(t[done])

# ---------- run ----------
v, sigma, c_delay = 0.3, 1.0, 1.0

# self-check: analytic vs MC at a mid threshold
a_chk = 2.0
er_mc, dt_mc = mc_ddm(a_chk, v, sigma)
er_an, dt_an = error_rate(a_chk, v, sigma), decision_time(a_chk, v, sigma)
print(f"[VERIFY a={a_chk}] ER analytic={er_an:.4f} MC={er_mc:.4f} | DT analytic={dt_an:.3f} MC={dt_mc:.3f}")

ratios = np.logspace(-1, 3, 80)                       # c_err/c_delay: 0.1 .. 1000
astar  = np.array([optimal_threshold(v, sigma, r * c_delay, c_delay) for r in ratios])
er_at  = error_rate(astar, v, sigma)
dt_at  = decision_time(astar, v, sigma)

monotone = bool(np.all(np.diff(astar) >= -1e-6))
print(f"[RESULT] a*(r) monotone increasing: {monotone}")
print(f"[RESULT] a* range: {astar.min():.3f} (r={ratios[0]:.1f}) -> {astar.max():.3f} (r={ratios[-1]:.0f})")
print(f"[RESULT] perception regime r=0.1: a*={astar[0]:.3f} ER={er_at[0]:.3f} DT={dt_at[0]:.2f}")
print(f"[RESULT] memory regime     r=1000: a*={astar[-1]:.3f} ER={er_at[-1]:.4f} DT={dt_at[-1]:.2f}")
# fail-safe flip: fraction of residual cost from error vs delay, at a*
err_share = (ratios * er_at) / (ratios * er_at + dt_at)
print(f"[RESULT] error-cost share of residual: perception={err_share[0]:.2f} -> memory={err_share[-1]:.2f}")

# ---------- figure ----------
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))

ax[0].semilogx(ratios, astar, lw=2.4, color="#2a6f97")
ax[0].set_xlabel("cost-asymmetry  r = c_err / c_delay")
ax[0].set_ylabel("optimal collapse threshold  a*")
ax[0].set_title("A. The generator: a* rises monotonically with cost-asymmetry")
ax[0].axvspan(0.1, 1, alpha=0.08, color="crimson")
ax[0].axvspan(100, 1000, alpha=0.08, color="navy")
ax[0].text(0.16, astar.max()*0.9, "perception\n(collapse early)", color="crimson", fontsize=9)
ax[0].text(180, astar.min()+0.4, "memory\n(collapse late)", color="navy", fontsize=9)
ax[0].grid(alpha=0.25)

# panel B: the speed-accuracy trade-off & the two miscalibrations, at r=100 (memory)
a_grid = np.linspace(0.05, 12, 300)
r_demo = 100.0
ec = r_demo * error_rate(a_grid, v, sigma)
dc = c_delay * decision_time(a_grid, v, sigma)
tot = ec + dc
astar_demo = optimal_threshold(v, sigma, r_demo, c_delay)
ax[1].plot(a_grid, ec, "--", color="crimson", label="error cost  c_err·ER")
ax[1].plot(a_grid, dc, "--", color="seagreen", label="delay cost  c_delay·DT")
ax[1].plot(a_grid, tot, lw=2.4, color="k", label="total cost")
ax[1].axvline(astar_demo, color="#2a6f97", lw=1.8)
ax[1].set_ylim(0, np.percentile(tot, 92))
ax[1].set_xlabel("threshold  a")
ax[1].set_ylabel("cost per decision  (r=100)")
ax[1].set_title("B. Two miscalibrations of one gate")
ax[1].text(astar_demo+0.2, ax[1].get_ylim()[1]*0.5, "a*", color="#2a6f97")
ax[1].text(0.3, ax[1].get_ylim()[1]*0.82, "too low →\nconfabulate\n/hallucinate", color="crimson", fontsize=8)
ax[1].text(8.2, ax[1].get_ylim()[1]*0.82, "too high →\nperseverate\n/paralyse", color="seagreen", fontsize=8)
ax[1].legend(fontsize=8, loc="upper center")
ax[1].grid(alpha=0.25)

# panel C: the fail-safe FLIP — which failure dominates at a*
ax[2].semilogx(ratios, er_at, lw=2.2, color="crimson", label="residual error ER(a*)")
ax2b = ax[2].twinx()
ax2b.semilogx(ratios, dt_at, lw=2.2, color="seagreen", label="residual delay DT(a*)")
ax[2].set_xlabel("cost-asymmetry  r = c_err / c_delay")
ax[2].set_ylabel("residual error at a*", color="crimson")
ax2b.set_ylabel("residual delay at a*", color="seagreen")
ax[2].set_title("C. No universal fail-safe: the residual failure flips")
ax[2].tick_params(axis="y", colors="crimson"); ax2b.tick_params(axis="y", colors="seagreen")
ax[2].grid(alpha=0.25)

plt.tight_layout()
plt.savefig("collapse_timing_sim.png", dpi=130)
print("wrote collapse_timing_sim.png")
