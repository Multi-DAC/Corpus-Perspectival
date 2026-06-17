"""Figures for the place-threshold-mechanism essay (R1–R11). Day 136, 2026-06-16."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams.update({"font.size": 11, "axes.titlesize": 11.5, "axes.titleweight": "bold",
                 "figure.dpi": 140, "savefig.dpi": 140, "axes.grid": True,
                 "grid.alpha": 0.25, "axes.axisbelow": True})
INK = "#1a2b3c"; HOT = "#c0392b"; COOL = "#2471a3"; GOLD = "#b9770e"; GREEN = "#1e8449"
mu0 = 4*np.pi*1e-7; mp = 1.6726e-27
FS = (7.4, 4.5)   # wider panels: room for titles + annotations (fixes clipping/overlap)

# ---- Fig 1: Derrick rescaling, with and without the gauge (plasma) term ----
fig, ax = plt.subplots(figsize=FS)
lam = np.linspace(0.35, 2.8, 400)
Eg, Ep = 1.0, 0.5
bare = lam**-1*Eg + lam**-3*Ep
Eem = Eg + 3*Ep                       # virial -> minimum at lam=1
gauged = lam**-1*Eg + lam**-3*Ep + lam**+1*Eem
ax.plot(lam, bare, color=HOT, lw=2.4, label="bare radion lump (collapses — no minimum)")
ax.plot(lam, gauged, color=COOL, lw=2.4, label="plasma-stabilized (gauge term added)")
ax.plot(1.0, gauged[np.argmin(np.abs(lam-1))], "o", color=GREEN, ms=9, zorder=5)
# label placed in the clear wedge between the curves (was overlapped by the rising blue curve)
ax.annotate("virial minimum\n$E_{EM}=E_{grad}+3E_{pot}$", xy=(1.0, gauged[np.argmin(np.abs(lam-1))]),
            xytext=(1.5, 2.25), color=GREEN, fontsize=10, ha="center",
            arrowprops=dict(arrowstyle="->", color=GREEN))
ax.set_xlabel("scale factor  $\\lambda$  (shrink $\\rightarrow$)"); ax.set_ylabel("static energy  $\\epsilon(\\lambda)$")
ax.set_title("Fig. 1  Derrick's no-go, and the plasma evasion (R1, R4)")
ax.legend(frameon=False, fontsize=9.5, loc="upper center"); ax.set_ylim(0, 8)
fig.tight_layout(); fig.savefig("portal-fig1-derrick.png"); plt.close(fig)

# ---- Fig 2: wall thickness vs field mass (scale / field identification) ----
fig, ax = plt.subplots(figsize=FS)
hbar_c = 1.973e-7  # eV*m
m_eV = np.logspace(-3.3, 12, 500)        # meV .. TeV
wall = hbar_c / m_eV                      # Compton wall thickness (m)
ax.loglog(m_eV, wall, color=INK, lw=2.4)
ax.set_ylim(1e-19, 3e1)
# markers
m_rad, w_rad = 120e9, hbar_c/120e9
m_de, w_de = 2.3e-3, hbar_c/2.3e-3
# radion label: right-aligned at the dot's x so it extends LEFT (was clipping the right edge)
ax.plot(m_rad, w_rad, "o", color=HOT, ms=9); ax.annotate("radion ~120 GeV\nwall ~$10^{-18}$ m (excluded)",
        xy=(m_rad, w_rad), xytext=(m_rad, 6e-15), color=HOT, fontsize=9.5, ha="right",
        arrowprops=dict(arrowstyle="->", color=HOT))
# dark-energy label: out in the empty upper-middle, clear of the dotted vline and the curve
ax.plot(m_de, w_de, "o", color=GREEN, ms=9); ax.annotate("dark-energy modulus\n$(\\rho_\\Lambda)^{1/4}=2.3$ meV\nwall ~0.085 mm",
        xy=(m_de, w_de), xytext=(9e-2, 1.3e-2), color=GREEN, fontsize=9.5, va="center",
        arrowprops=dict(arrowstyle="->", color=GREEN))
ax.axvline(2.3e-3, color=GREEN, ls=":", lw=1.2)
ax.axhline(1e-3, color=GOLD, ls="--", lw=1.5)
# "sub-mm" label sits ABOVE the dashed line (was sitting on it)
ax.text(1e8, 1.5e-3, "sub-mm: macroscopic wall", color=GOLD, fontsize=9, ha="right", va="bottom")
ax.set_xlabel("wall-field mass  (eV)"); ax.set_ylabel("wall thickness  $\\hbar c/mc^2$  (m)")
ax.set_title("Fig. 2  The scale problem is field identification (R5, R7)")
fig.tight_layout(); fig.savefig("portal-fig2-scale.png"); plt.close(fig)

# ---- Fig 3: structure (sigma) vs signature (d sigma sources EM at the wall) ----
fig, ax = plt.subplots(figsize=FS)
r = np.linspace(0, 2, 500); R, w = 1.0, 0.08
sigma = 0.5*(1 + np.tanh((R - r)/w))            # high inside, drops across wall
dsigma = np.abs(np.gradient(sigma, r)); dsigma /= dsigma.max()
ax.plot(r, sigma, color=COOL, lw=2.4, label="$\\sigma$ — structure (sets wall, screens)")
ax.plot(r, dsigma, color=HOT, lw=2.4, label="$|\\partial\\sigma|$ — EM signature (only at wall)")
ax.axvspan(R-3*w, R+3*w, color=GOLD, alpha=0.13)
ax.text(R, 1.05, "the wall shell\n($\\partial\\sigma\\neq0$)", color=GOLD, ha="center", fontsize=9)
ax.text(0.10, 0.90, "interior\n(unscreened)", color=COOL, fontsize=9, va="top")
ax.text(1.72, 0.10, "exterior\n(screened)", color=INK, fontsize=9, ha="center")
ax.set_xlabel("radius  $r$  (carrier units)"); ax.set_ylabel("normalized amplitude")
ax.set_title("Fig. 3  Structure vs signature (R9)")
ax.legend(frameon=False, fontsize=9, loc="center right"); ax.set_ylim(-0.05, 1.20)
fig.tight_layout(); fig.savefig("portal-fig3-structure-signature.png"); plt.close(fig)

# ---- Fig 4: Lundquist maintenance margin S vs carrier scale ----
fig, ax = plt.subplots(figsize=FS)
L = np.logspace(-1, 3.3, 400)
def Scurve(B, n, T_eV, ionf):
    v_A = B/np.sqrt(mu0*n*mp); sigma = 1.5e2*T_eV**1.5*ionf; eta = 1/(mu0*sigma)
    return L*v_A/eta
ax.loglog(L, Scurve(1e-4,1e19,1.0,0.01), color=COOL, lw=2.2, label="cool weakly-ionized (decoheres)")
ax.loglog(L, Scurve(1e-3,1e20,5.0,0.2),  color=GOLD, lw=2.2, label="warm partially-ionized")
ax.loglog(L, Scurve(1e-2,1e20,20.0,0.8), color=HOT,  lw=2.2, label="hot well-ionized (deeply stable)")
ax.axhline(1.0, color=INK, ls="--", lw=1.6); ax.text(0.12, 1.5, "$S=1$  maintenance threshold", color=INK, fontsize=9.5)
# spheromak validation point
v_A=0.1/np.sqrt(mu0*1e20*mp); sig=1.5e2*20**1.5; eta=1/(mu0*sig); S_sph=0.3*v_A/eta
ax.plot(0.3, S_sph, "*", color=GREEN, ms=16); ax.annotate("lab spheromak\n$S\\approx10^3$ (validates)",
        xy=(0.3, S_sph), xytext=(0.5, 2e5), color=GREEN, fontsize=9.5,
        arrowprops=dict(arrowstyle="->", color=GREEN))
ax.set_xlabel("carrier size  $L$  (m)"); ax.set_ylabel("Lundquist number  $S=\\mu_0\\sigma L v_A$")
ax.set_title("Fig. 4  The maintenance threshold (R10)")
ax.legend(frameon=False, fontsize=9, loc="lower right"); ax.set_ylim(1e-3, 1e8)
fig.tight_layout(); fig.savefig("portal-fig4-maintenance.png"); plt.close(fig)

# ---- Fig 5: helicity source — classical vs anomalous double-layer potential ----
fig, ax = plt.subplots(figsize=FS)
fac = np.logspace(0, 3, 300)
B, sigma = 0.1, 1.5e2*20**1.5          # spheromak-class
V_classical = B/(2*mu0*sigma)          # ~3 V
V = V_classical*fac
ax.loglog(fac, V, color=COOL, lw=2.4)
ax.axhspan(700, 1500, color=GREEN, alpha=0.18); ax.text(1.2, 950, "observed spheromak CHI drive  ~1 kV", color=GREEN, fontsize=9.5)
ax.plot(1, V_classical, "o", color=HOT, ms=9); ax.annotate("classical Spitzer floor\n~3 V", xy=(1, V_classical),
        xytext=(1.4, 0.2), color=HOT, fontsize=9.5, arrowprops=dict(arrowstyle="->", color=HOT))
ax.axvspan(1e2, 1e3, color=GOLD, alpha=0.12); ax.text(1.3e2, 8, "anomalous (reconnection)\nresistivity ×$10^2$–$10^3$",
        color=GOLD, fontsize=9)
ax.set_xlabel("resistivity enhancement  $\\eta_{anom}/\\eta_{Spitzer}$"); ax.set_ylabel("double-layer drive  $V_{DL}$  (V)")
ax.set_title("Fig. 5  Anomalous resistivity brackets the kV drive (R11)")
ax.set_ylim(0.1, 1e4); fig.tight_layout(); fig.savefig("portal-fig5-source.png"); plt.close(fig)

print("wrote portal-fig1..5")
