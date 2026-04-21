"""Fix Figure 5: Fermion localization profiles with correct physics."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({
    'font.family': 'serif', 'font.size': 11, 'axes.labelsize': 13,
    'axes.titlesize': 14, 'legend.fontsize': 9, 'figure.dpi': 300,
    'savefig.dpi': 300, 'savefig.bbox': 'tight', 'mathtext.fontset': 'cm',
})

FIGDIR = r'C:\Users\mercu\clawd\projects\Project Meridian\monograph\figures'

fig, ax = plt.subplots(figsize=(8, 5.5))

y = np.linspace(0, 1, 1000)  # y/y_c normalized
ky_c = 35.0

# Physical probability density in warped metric:
# P(y) ∝ |f_L(y)|^2 * e^{-4A} = exp(-2*c_i*k*y)
# For c_i ≈ 0 (top): nearly flat (extends across full dimension)
# For c_i > 0.5 (light fermions): sharply UV-peaked

fermions = [
    (r'$t$ quark ($c = 0.004$, IR)',   0.004, '#d73027', 2.5),
    (r'$b$ quark ($c = 0.503$)',        0.503, '#fc8d59', 2.0),
    (r'$c$ quark ($c = 0.530$)',        0.530, '#fee090', 1.8),
    (r'$\mu$ ($c = 0.574$)',            0.574, '#91bfdb', 1.8),
    (r'$u$ quark ($c = 0.635$, UV)',    0.635, '#4575b4', 2.0),
    (r'$e$ ($c = 0.656$, UV)',          0.656, '#313695', 2.5),
]

for label, c_i, color, lw in fermions:
    # Probability density in warped space: P(y) ∝ exp(-2*c_i*ky_c*y/y_c)
    P = np.exp(-2 * c_i * ky_c * y)
    # Normalize to max = 1
    P = P / P[0]
    ax.semilogy(y, P, '-', color=color, lw=lw, label=label)

# Mark UV and IR branes
ax.axvline(0, color='black', lw=2.5, alpha=0.4)
ax.axvline(1, color='black', lw=2.5, alpha=0.4)
ax.text(0.015, 0.92, 'UV brane', fontsize=10, transform=ax.transAxes, va='top', fontweight='bold')
ax.text(0.82, 0.92, 'IR brane\n(Higgs)', fontsize=10, transform=ax.transAxes, va='top', fontweight='bold')

# Higgs localization (shaded at IR)
ax.axvspan(0.95, 1.0, alpha=0.2, color='#fdae61', label='Higgs (IR-localized)')

# Yukawa overlap annotation
ax.annotate('Top quark: large Higgs\noverlap $\\Rightarrow$ heavy',
            xy=(0.8, np.exp(-2*0.004*ky_c*0.8)),
            xytext=(0.55, 3e-3),
            arrowprops=dict(arrowstyle='->', color='#d73027', lw=1.5),
            fontsize=9, color='#d73027')

ax.annotate('Electron: negligible Higgs\noverlap $\\Rightarrow$ light',
            xy=(0.3, np.exp(-2*0.656*ky_c*0.3)),
            xytext=(0.4, 1e-8),
            arrowprops=dict(arrowstyle='->', color='#313695', lw=1.5),
            fontsize=9, color='#313695')

ax.set_xlabel(r'Position in extra dimension $y/y_c$')
ax.set_ylabel(r'Probability density $|\psi(y)|^2$ (log scale, normalized)')
ax.set_title(r'Fermion Localization in the Warped Extra Dimension')
ax.set_xlim(0, 1)
ax.set_ylim(1e-20, 2)
ax.legend(loc='center left', framealpha=0.9, bbox_to_anchor=(0.01, 0.35))
ax.grid(True, alpha=0.3, which='both')

fig.savefig(f'{FIGDIR}/fig5_fermion_profiles.pdf')
fig.savefig(f'{FIGDIR}/fig5_fermion_profiles.png')
plt.close(fig)
print("Figure 5 (fixed): Fermion localization profiles -- done")
