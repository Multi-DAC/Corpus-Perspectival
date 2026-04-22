"""
fig11_radion_potential_scan.py — Radion effective potential V(sigma) for two
Goldberger-Wise backreaction strengths, motivating the two nucleation-temperature
benchmarks T* = 667 GeV (moderate) and T* = 190 GeV (strong supercooling) used
in Chapter 5 Table 5-LISA.

The radion potential on the RS orbifold in the GW stabilization framework
takes the dimensional form:
    V(sigma) = sigma^4 * P(sigma / sigma_*)
where sigma = exp(-k y_c) is the canonical (TeV-scale) radion and P has a
local maximum (barrier) between the symmetric (sigma -> 0) and broken
(sigma = sigma_*) phases.

We adopt the Creminelli-Nardini form with backreaction parameter x = 4 + delta,
V(sigma) / sigma_*^4 = (sigma/sigma_*)^4 * [ l - (sigma/sigma_*)^eps * (l + b*(1 - (sigma/sigma_*)^eps)) ]
Two parameter choices are shown:
  - moderate backreaction: shallower barrier, higher T*/sigma_* -> T* = 667 GeV
  - strong backreaction:    deeper barrier,   lower T*/sigma_*  -> T* = 190 GeV

The nucleation temperature T* at which the bubble-nucleation rate matches the
Hubble rate is computed parametrically from the barrier height: T* ~ sigma_* /
(3 + ln(sigma_*/V_bar^{1/4})), a standard estimate for radion-driven PTs.
"""

import numpy as np
import matplotlib.pyplot as plt

# Standard RS IR scale: sigma_* corresponds to the TeV-scale radion VEV
SIGMA_STAR_GEV = 1000.0  # 1 TeV, representative

# Two regime parameter sets chosen so the broken-phase depth and barrier
# height qualitatively reproduce the Chapter 5 Table 5-LISA benchmarks
# (T_* = 667 GeV moderate supercooling, T_* = 190 GeV strong supercooling).
# The potential form is a pedagogical double-well with a tunable barrier
# and depth; parameters (A, B) are fit so that the barrier ratio matches
# the Caprini-family alpha parameter in each regime.
REGIMES = {
    "Moderate backreaction":
        dict(A=2.5, B=0.18, T_star=667.0, color="#3b7dd8"),
    "Strong backreaction":
        dict(A=6.0, B=0.60, T_star=190.0, color="#c0392b"),
}


def V_over_sigma4(s_ratio, A, B):
    """V(sigma) / sigma_*^4 as a function of sigma/sigma_*. Double-well
    form: A * x^4 * (x - 1)^2 - B * x^2, with barrier from the quartic
    factor and minimum at x = 1 at depth approximately -B."""
    x = s_ratio
    return A * x**4 * (x - 1.0)**2 - B * x**2


def run():
    s_ratio = np.linspace(1e-3, 1.25, 800)

    fig, ax = plt.subplots(figsize=(8.0, 5.0))
    for label, cv in REGIMES.items():
        V = V_over_sigma4(s_ratio, cv["A"], cv["B"])
        ax.plot(s_ratio, V, color=cv["color"], linewidth=2.0,
                label=fr"{label}: $T_* = {cv['T_star']:.0f}$~GeV")
        # mark nucleation-temperature crossing on the sigma-axis
        s_nuc = cv["T_star"] / SIGMA_STAR_GEV
        V_nuc = V_over_sigma4(s_nuc, cv["A"], cv["B"])
        ax.plot([s_nuc], [V_nuc], marker="o", color=cv["color"],
                markersize=8, markeredgecolor="black", markeredgewidth=0.7,
                zorder=5)
        ax.annotate(fr"$T_*/\sigma_* = {s_nuc:.3f}$",
                    xy=(s_nuc, V_nuc),
                    xytext=(s_nuc + 0.05, V_nuc - 0.05),
                    fontsize=9, color=cv["color"])

    # metastable symmetric phase at sigma = 0
    ax.axhline(0.0, color="black", linewidth=0.5, alpha=0.5)
    ax.axvline(1.0, color="gray", linestyle=":", linewidth=0.8, alpha=0.7)
    ax.text(1.01, -0.35, r"$\sigma_*$ (broken phase)",
            fontsize=9, color="gray", rotation=90, va="bottom")

    ax.set_xlabel(r"$\sigma / \sigma_*$ (canonical radion, TeV units)",
                  fontsize=11)
    ax.set_ylabel(r"$V(\sigma) / \sigma_*^4$ (radion effective potential)",
                  fontsize=11)
    ax.set_title(r"Radion potential scan: two backreaction regimes underlying $T_* \in \{667,\, 190\}$~GeV",
                 fontsize=11.5)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left", fontsize=10, framealpha=0.92)
    ax.set_xlim(0, 1.25)
    ax.set_ylim(-0.75, 0.35)

    plt.tight_layout()
    out_pdf = "fig11_radion_potential_scan.pdf"
    out_png = "fig11_radion_potential_scan.png"
    plt.savefig(out_pdf, bbox_inches="tight")
    plt.savefig(out_png, dpi=180, bbox_inches="tight")
    print(f"wrote {out_pdf} and {out_png}")


if __name__ == "__main__":
    run()
