"""
Figure: The Topological Correction — V_DKL Landscape with Three Zeros

Creates a publication-quality figure showing:
1. |theta_1(pi*z, q_omega)| as a function of z
2. The discrete orbifold point z = 5/18
3. The target z_0 where |theta_1| = ln(3)/sqrt(2)
4. The topological correction delta_z
5. Annotations explaining the three zeros (gamma, Bridge #37, delta_b12 = 0)

Phase 22 Track alpha — Midday Creation Drive
2026-03-25
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import json

# ============================================================
# Compute |theta_1(pi*z, q)| using numpy
# ============================================================

# Z3 orbifold: tau = omega = (-1 + i*sqrt(3))/2
tau = complex(-0.5, np.sqrt(3)/2)
q = np.exp(1j * np.pi * tau)

def theta1(z_arr, n_terms=200):
    """Compute theta_1(pi*z, q) for array of z values.
    theta_1(u, q) = 2 * sum_{n=0}^{inf} (-1)^n * q^{(n+1/2)^2} * sin((2n+1)*u)
    where u = pi*z
    """
    result = np.zeros_like(z_arr, dtype=complex)
    u = np.pi * z_arr
    for n in range(n_terms):
        qfactor = q ** ((n + 0.5) ** 2)
        result += ((-1) ** n) * qfactor * np.sin((2 * n + 1) * u)
    return 2 * result

# Key values
z_tree = 5.0 / 18.0  # = 0.27778
z0 = 0.27707944216419  # exact target
target = np.log(3) / np.sqrt(2)  # = 0.77684
delta_z = z0 - z_tree

# ============================================================
# Panel 1: Full landscape z in [0, 1]
# ============================================================

z_full = np.linspace(0.001, 0.999, 2000)
theta1_full = np.abs(theta1(z_full))

# ============================================================
# Panel 2: Zoom near z = 5/18
# ============================================================

z_zoom = np.linspace(0.25, 0.30, 1000)
theta1_zoom = np.abs(theta1(z_zoom))

# ============================================================
# Create figure
# ============================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [1, 1.2]})
fig.patch.set_facecolor('#fafaf8')

# Colors
c_landscape = '#2c3e50'
c_target = '#c0392b'
c_orbifold = '#2980b9'
c_resolution = '#27ae60'
c_arrow = '#8e44ad'
c_zero_bg = '#f0f0f0'

# --- Panel 1: Full landscape ---
ax1.set_facecolor('#fafaf8')
ax1.plot(z_full, theta1_full, color=c_landscape, linewidth=1.8, zorder=5)
ax1.axhline(y=target, color=c_target, linewidth=1.0, linestyle='--', alpha=0.7, label=r'$\ln 3 / \sqrt{2}$')
ax1.axvline(x=z_tree, color=c_orbifold, linewidth=0.8, linestyle=':', alpha=0.5)
ax1.axvline(x=1-z0, color=c_resolution, linewidth=0.8, linestyle=':', alpha=0.3)

# Mark the two zeros
ax1.plot(z0, target, 'o', color=c_resolution, markersize=8, zorder=10)
ax1.plot(1-z0, target, 'o', color=c_resolution, markersize=6, alpha=0.5, zorder=10)

# Mark orbifold point
theta1_at_tree = np.abs(theta1(np.array([z_tree])))[0]
ax1.plot(z_tree, theta1_at_tree, 's', color=c_orbifold, markersize=8, zorder=10)

ax1.set_xlabel(r'Wilson line parameter $z$', fontsize=12)
ax1.set_ylabel(r'$|\vartheta_1(\pi z, q_\omega)|$', fontsize=12)
ax1.set_title('Full Landscape', fontsize=13, fontweight='bold')
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1.1)

# Symmetry annotation
ax1.annotate(r'$z \leftrightarrow 1-z$', xy=(0.5, 0.02), fontsize=9, ha='center',
             color='gray', style='italic')

# Legend
ax1.plot([], [], 's', color=c_orbifold, markersize=8, label=r'Orbifold: $z = 5/18$')
ax1.plot([], [], 'o', color=c_resolution, markersize=8, label=r'Resolution: $z_0 = 0.27708$')
ax1.legend(loc='upper right', fontsize=9, framealpha=0.9)

ax1.grid(True, alpha=0.15)

# --- Panel 2: Zoom + topological correction ---
ax2.set_facecolor('#fafaf8')
ax2.plot(z_zoom, theta1_zoom, color=c_landscape, linewidth=2.0, zorder=5)
ax2.axhline(y=target, color=c_target, linewidth=1.2, linestyle='--', alpha=0.7)

# Orbifold point
ax2.plot(z_tree, theta1_at_tree, 's', color=c_orbifold, markersize=10, zorder=10)
ax2.annotate(r'$z = \frac{5}{18}$ (orbifold)',
             xy=(z_tree, theta1_at_tree), xytext=(z_tree + 0.008, theta1_at_tree + 0.008),
             fontsize=10, color=c_orbifold, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=c_orbifold, lw=1.5))

# Resolution point
ax2.plot(z0, target, 'o', color=c_resolution, markersize=10, zorder=10)
ax2.annotate(r'$z_0 = 0.27708$ (resolution)',
             xy=(z0, target), xytext=(z0 - 0.020, target - 0.012),
             fontsize=10, color=c_resolution, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=c_resolution, lw=1.5))

# The topological correction arrow
mid_y = (theta1_at_tree + target) / 2
ax2.annotate('', xy=(z0, mid_y), xytext=(z_tree, mid_y),
             arrowprops=dict(arrowstyle='<->', color=c_arrow, lw=2.0))
ax2.text((z_tree + z0)/2, mid_y + 0.002, r'$\delta z = -7 \times 10^{-4}$',
         fontsize=10, ha='center', va='bottom', color=c_arrow, fontweight='bold')
ax2.text((z_tree + z0)/2, mid_y - 0.003, r'$\delta z/z \approx \alpha_{\mathrm{GUT}}/4\pi$',
         fontsize=9, ha='center', va='top', color=c_arrow, style='italic')

# Target line label
ax2.text(0.298, target + 0.001, r'$\ln 3 / \sqrt{2}$',
         fontsize=10, color=c_target, va='bottom')

# Gap annotation
gap_y = theta1_at_tree
ax2.annotate('', xy=(0.2505, target), xytext=(0.2505, gap_y),
             arrowprops=dict(arrowstyle='<->', color='#e67e22', lw=1.5))
ax2.text(0.2495, (target + gap_y)/2, '0.18%\ngap',
         fontsize=9, ha='right', va='center', color='#e67e22', fontweight='bold')

# Three zeros box
box_text = (
    "Three Zeros of Protection\n"
    "───────────────────────\n"
    "Track γ:      NP ≈ 10⁻³²  ✓\n"
    "Bridge #37:  ΔH_mod = 0   ✓\n"
    "Theorem:     δb₁₂ = 0      ✓\n"
    "───────────────────────\n"
    "∴ Gap is TOPOLOGICAL"
)
props = dict(boxstyle='round,pad=0.5', facecolor='#f7f1e3', edgecolor='#2c3e50', alpha=0.9)
ax2.text(0.287, 0.768, box_text, fontsize=7.5, va='top',
         family='monospace', bbox=props)

ax2.set_xlabel(r'Wilson line parameter $z$', fontsize=12)
ax2.set_ylabel(r'$|\vartheta_1(\pi z, q_\omega)|$', fontsize=12)
ax2.set_title('Topological Correction: Orbifold → Resolution', fontsize=13, fontweight='bold')
ax2.set_xlim(0.25, 0.30)
ax2.set_ylim(0.765, 0.790)

ax2.grid(True, alpha=0.15)

# --- Suptitle ---
fig.suptitle('Phase 22 — The Gap as Topological Blow-Up Correction',
             fontsize=14, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.95])

# Save
outpath = r'C:\Users\mercu\clawd\projects\Project Meridian\phase22\fig_topological_correction.png'
fig.savefig(outpath, dpi=200, bbox_inches='tight', facecolor='#fafaf8')
print(f"Saved: {outpath}")

outpath_pdf = outpath.replace('.png', '.pdf')
fig.savefig(outpath_pdf, bbox_inches='tight', facecolor='#fafaf8')
print(f"Saved: {outpath_pdf}")
