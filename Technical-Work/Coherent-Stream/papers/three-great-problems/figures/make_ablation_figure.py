"""Classical ablation demonstration of the content-capacity residue eta.

ILLUSTRATIVE (not deployment data): a small classical 'society of nodes'. A target node S
produces output Y = X_own + lambda * C + noise, where C is the context delivered over the bus and
lambda is the coupling strength. We measure the residue eta(S) = I(Y; C) -- the mutual information
between the node's output and its context -- by ABLATION: compare the node's output distribution
in-context vs. isolated (context zeroed). This is the classical, no-quantum-hardware companion to the
quantum toy figure: it shows the residue is an ordinary, repeatable measurement on a running system.

Panel (a): residue eta vs coupling. Points = empirical ablation estimate (2D-histogram MI of samples);
           line = analytic Gaussian mutual information 0.5*log2(1 + lambda^2 Var[C]/(Var[X]+Var[noise])).
           The empirical ablation estimate tracks the analytic value; eta -> 0 as coupling -> 0.
Panel (b): the node's output distribution in-context vs isolated at one coupling. The visible
           divergence between the two histograms is exactly what the ablation measures: the context
           written into the part.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(7)
N = 300_000
var_x = 1.0          # node's own input variance
var_noise = 0.09     # internal noise variance (sigma = 0.3)
var_c = 1.0          # context variance


def mi_bits(a, b, bins=80):
    """Empirical mutual information (bits) via 2D-histogram, bias-corrected by the lambda=0 baseline."""
    joint, _, _ = np.histogram2d(a, b, bins=bins)
    pj = joint / joint.sum()
    pa = pj.sum(axis=1, keepdims=True)
    pb = pj.sum(axis=0, keepdims=True)
    outer = pa @ pb
    m = pj > 0
    return float(np.sum(pj[m] * np.log2(pj[m] / outer[m])))


def analytic_mi(lam):
    return 0.5 * np.log2(1 + (lam**2 * var_c) / (var_x + var_noise))


X = rng.normal(0, np.sqrt(var_x), N)
C = rng.normal(0, np.sqrt(var_c), N)
eps = rng.normal(0, np.sqrt(var_noise), N)

lams = np.linspace(0.0, 2.0, 13)
# bias baseline at lambda=0 (true MI is 0; histogram MI is slightly positive)
base = mi_bits((X + eps), C)
emp, ana = [], []
for lam in lams:
    Y = X + lam * C + eps
    emp.append(max(0.0, mi_bits(Y, C) - base))
    ana.append(analytic_mi(lam))

fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.7))

ax[0].plot(lams, ana, "-", color="#1166bb", lw=2, label="analytic  $I(Y;C)$", zorder=2)
ax[0].scatter(lams, emp, color="#c33", s=34, zorder=3, label="ablation estimate")
ax[0].set_xlabel("context coupling  $\\lambda$")
ax[0].set_ylabel("content-capacity residue  $\\eta = I(Y;C)$ [bits]")
ax[0].set_title("(a)  residue measured by ablation tracks coupling", fontsize=11)
ax[0].axhline(0, color="k", lw=0.6, alpha=0.4)
ax[0].legend(fontsize=8, loc="upper left")
ax[0].grid(alpha=0.25)

lam_demo = 1.0
Y_ctx = X + lam_demo * C + eps
Y_iso = X + eps
bins = np.linspace(-6, 6, 70)
ax[1].hist(Y_iso, bins=bins, density=True, color="#888", alpha=0.55, label="isolated (ablated)")
ax[1].hist(Y_ctx, bins=bins, density=True, histtype="step", color="#c33", lw=2,
           label=f"in-context ($\\lambda={lam_demo:g}$)")
ax[1].set_xlabel("node output  $Y$")
ax[1].set_ylabel("density")
ax[1].set_title("(b)  ablation reveals the residue", fontsize=11)
ax[1].legend(fontsize=8, loc="upper right")
ax[1].grid(alpha=0.25)

fig.tight_layout()
fig.savefig("eta_ablation.pdf", bbox_inches="tight")
fig.savefig("eta_ablation.png", dpi=150, bbox_inches="tight")
print("saved eta_ablation.pdf/.png")
print(f"  eta(lambda=0)={emp[0]:.3f}  eta(lambda=1)={emp[6]:.3f}  eta(lambda=2)={emp[-1]:.3f} bits")
print(f"  analytic:     {ana[0]:.3f}             {ana[6]:.3f}            {ana[-1]:.3f} bits")
