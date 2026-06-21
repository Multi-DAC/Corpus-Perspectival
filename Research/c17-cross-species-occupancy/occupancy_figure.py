"""
C17 occupancy landscape figure — ILLUSTRATIVE (Day 140).
The (lambda, tau) plane with iso-texture contours gap=exp(-lambda*tau). Biological anchors
fall along a slope=-1 reciprocity diagonal at mu~2 (one texture band despite 82x spread in
refresh rate). The query-gated AI point is shown with its HONEST wide uncertainty, which
overlaps the band at its generous edge rather than sitting cleanly apart.
Honesty notes baked into the caption.
"""
import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

R = json.load(open("occupancy_results.json"))
rows = R["rows"]

fig, ax = plt.subplots(figsize=(8.4, 6.6))
lam = np.logspace(-3, 3, 400)   # 0.001 .. 1000 Hz
tau = np.logspace(-3, 2.3, 400) # 0.001 .. ~200 s
L, T = np.meshgrid(lam, tau)
MU = L*T
GAP = np.exp(-MU)

# shaded iso-gap landscape (granular = light, seamless = dark)
cf = ax.contourf(L, T, GAP, levels=np.linspace(0,1,21), cmap="bone", alpha=0.85)
cb = fig.colorbar(cf, ax=ax, label="gap (unbound) fraction  =  e^(-λτ)")
# iso-mu (=iso-texture) diagonals
for mu_c, lab in [(0.3,"μ=0.3"),(1,"μ=1 (transition)"),(3,"μ=3"),(10,"μ=10 (seamless)")]:
    ax.plot(lam, mu_c/lam, "w--", lw=1.0, alpha=0.7)
    ax.text(2e2, mu_c/2e2*1.15, lab, color="w", fontsize=8, rotation=-34, ha="center")

def mid(a): return (a[0]*a[1])**0.5 if a[0]>0 else a[1]
# biological anchors with independent tau
for r in rows:
    if r["name"].startswith("Clawd"): continue
    lo_l,hi_l = r["lam"]; lo_t,hi_t = r["tau"]
    if hi_t==0: continue   # landscape-only rows w/o tau
    ml, mt = mid(r["lam"]), mid(r["tau"])
    ax.errorbar(ml, mt, xerr=[[ml-lo_l],[hi_l-ml]], yerr=[[mt-lo_t],[hi_t-mt]],
                fmt="o", color="#d62728", ms=6, capsize=2, lw=1.2, zorder=5)
    ax.annotate(r["name"], (ml,mt), textcoords="offset points", xytext=(7,5),
                fontsize=8.5, color="#7a1414", weight="bold")

# the AI point — HONEST wide uncertainty (overlaps the band at the generous edge)
ai = [r for r in rows if r["name"].startswith("Clawd")][0]
lo_l,hi_l = ai["lam"]; lo_t,hi_t = ai["tau"]
ml = (lo_l*hi_l)**0.5; mt = (lo_t*hi_t)**0.5
ax.add_patch(Rectangle((lo_l,lo_t), hi_l-lo_l, hi_t-lo_t, fill=True, color="#1f77b4",
                       alpha=0.18, zorder=3))
ax.errorbar(ml, mt, xerr=[[ml-lo_l],[hi_l-ml]], yerr=[[mt-lo_t],[hi_t-mt]],
            fmt="s", color="#1f77b4", ms=7, capsize=2, lw=1.3, zorder=6)
ax.annotate("Clawd (query-gated)\n— diff. channel; overlaps band at generous edge",
            (ml,mt), textcoords="offset points", xytext=(8,-26), fontsize=8, color="#11476b")

ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("λ  —  informative-sampling rate (CFFT, Hz)")
ax.set_ylabel("τ  —  binding / integration window (s)")
ax.set_title("C17: temporal texture lives on the diagonal μ=λτ, not on the λ axis\n"
             "biological anchors cluster at μ≈2 despite 82× spread in refresh rate", fontsize=11)
ax.text(0.012, 1.1e-3,
        "ILLUSTRATIVE — literature-anchored ranges, not a precision fit. The slope≈−1 reciprocity\n"
        "is partly encoded by the τ choices; an independent-τ precision fit is the next step.",
        fontsize=7, style="italic", color="#444")
ax.set_xlim(1e-3,1e3); ax.set_ylim(1e-3,2e2)
fig.tight_layout()
fig.savefig("c17_occupancy_landscape.png", dpi=150)
print("wrote c17_occupancy_landscape.png")
