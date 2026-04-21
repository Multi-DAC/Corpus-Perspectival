"""
Generate all publication-quality figures for the Meridian Monograph.
March 31, 2026. Clawd.

Figures:
1. w0(zeta0) parametric curve with benchmarks
2. w(z) evolution: Meridian vs CPL vs LCDM
3. chi-squared model comparison
4. Inflationary (n_s, r) prediction plane
5. Fermion localization profiles in extra dimension
6. epsilon_1 Goldilocks window
7. Sensitivity forecast timeline
8. Sound speed landscape comparison
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.ticker as ticker

# Global style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 13,
    'axes.titlesize': 14,
    'legend.fontsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'text.usetex': False,  # Use mathtext instead of LaTeX
    'mathtext.fontset': 'cm',
})

FIGDIR = r'C:\Users\mercu\clawd\projects\Project Meridian\monograph\figures'

# ============================================================
# Physical constants and parameters
# ============================================================
C_KK = 1.64e-4       # OP#8 definitive (Planck 2018 fiducial q0=-0.5275)
C_KK_err = 0.33e-4   # uncertainty from eps1 cutoff function
eps1 = 0.010          # Gauss-Bonnet coupling (d=5 Weyl corrected)
eps1_err = 0.002
Omega_DE = 0.685
Omega_m = 0.315
q0 = -0.5275
ky_c = 35.0           # orbifold parameter

# JC benchmark (Phase 13, historical)
zeta0_JC = 9.64e-4
w0_JC_pert = -1 + C_KK / zeta0_JC
w0_JC_exact = -1 + 2*C_KK*Omega_DE / (2*zeta0_JC) / (C_KK*Omega_DE/(2*zeta0_JC) + Omega_DE)

# OP#8 NCG benchmark (April 2, 2026 — definitive)
zeta0_NCG = 8.8e-4
C_KK_ncg = (1 + q0)**2 * Omega_DE * eps1 / (4 * (1 - q0)**2)  # 1.639e-4
kappa0_NCG = C_KK_ncg * Omega_DE / (2 * zeta0_NCG)
w0_NCG = -1 + 2 * kappa0_NCG / (kappa0_NCG + Omega_DE)  # -0.830

# CMB benchmark
zeta0_CMB = 0.037
w0_CMB = -1 + C_KK / zeta0_CMB  # -0.996

# DESI best-fit (constant-w constraint)
zeta0_DESI = 1.05e-3
w0_DESI = -0.83


# ============================================================
# Figure 1: w0(zeta0) parametric curve
# ============================================================
def fig1_w0_zeta0():
    fig, ax = plt.subplots(figsize=(8, 5.5))

    zeta = np.logspace(-4, -0.5, 500)

    # Perturbative formula
    w0_pert = -1 + C_KK / zeta
    w0_pert_hi = -1 + (C_KK + C_KK_err) / zeta
    w0_pert_lo = -1 + (C_KK - C_KK_err) / zeta

    # Exact non-perturbative
    kappa0 = C_KK * Omega_DE / (2 * zeta)
    w0_exact = 2 * kappa0 / (kappa0 + Omega_DE) - 1

    # Clip to physical range
    mask = w0_pert > -1.5
    ax.fill_between(zeta[mask], w0_pert_lo[mask], w0_pert_hi[mask],
                    alpha=0.2, color='#2166ac', label=r'$1\sigma$ uncertainty ($C_{\mathrm{KK}}$)')
    ax.plot(zeta[mask], w0_pert[mask], '-', color='#2166ac', lw=2.5,
            label=r'Perturbative: $w_0 = -1 + C_{\mathrm{KK}}/\zeta_0$')
    ax.plot(zeta[mask], w0_exact[mask], '--', color='#b2182b', lw=1.8,
            label=r'Exact: $w_0 = 2\kappa_0/(\kappa_0 + \Omega_{\mathrm{DE}}) - 1$')

    # DESI DR2 band (constant-w constraint)
    ax.axhspan(-0.83 - 0.06, -0.83 + 0.06, alpha=0.12, color='#4daf4a',
               label=r'DESI DR2 constant-$w$ ($-0.83 \pm 0.06$)')

    # LCDM line
    ax.axhline(-1.0, color='gray', ls=':', lw=1, alpha=0.7, label=r'$\Lambda$CDM ($w = -1$)')

    # Benchmarks
    ax.plot(zeta0_JC, w0_JC_pert, 'o', color='#2166ac', ms=10, zorder=5,
            markeredgecolor='white', markeredgewidth=1.5)
    ax.annotate(f'JC benchmark\n$\\zeta_0 = 9.64\\times 10^{{-4}}$\n$w_0 = {w0_JC_pert:.3f}$',
                xy=(zeta0_JC, w0_JC_pert), xytext=(5e-3, -0.65),
                arrowprops=dict(arrowstyle='->', color='#2166ac', lw=1.5),
                fontsize=9, color='#2166ac', ha='center')

    ax.plot(zeta0_NCG, w0_NCG, 'D', color='#e6550d', ms=11, zorder=6,
            markeredgecolor='white', markeredgewidth=1.5)
    ax.annotate(f'OP#8 NCG\n$\\zeta_0 = 8.8\\times 10^{{-4}}$\n$w_0 = {w0_NCG:.3f}$',
                xy=(zeta0_NCG, w0_NCG), xytext=(3e-3, -0.72),
                arrowprops=dict(arrowstyle='->', color='#e6550d', lw=1.5),
                fontsize=9, color='#e6550d', ha='center', fontweight='bold')

    ax.plot(zeta0_CMB, w0_CMB, 's', color='#b2182b', ms=9, zorder=5,
            markeredgecolor='white', markeredgewidth=1.5)
    ax.annotate(f'CMB benchmark\n$\\zeta_0 = 0.037$\n$w_0 = {w0_CMB:.3f}$',
                xy=(zeta0_CMB, w0_CMB), xytext=(0.08, -0.96),
                arrowprops=dict(arrowstyle='->', color='#b2182b', lw=1.5),
                fontsize=9, color='#b2182b', ha='center')

    ax.set_xscale('log')
    ax.set_xlabel(r'$\zeta_0$ (dimensionless non-minimal coupling)')
    ax.set_ylabel(r'$w_0$ (dark energy equation of state)')
    ax.set_title(r'Meridian Prediction: $w_0(\zeta_0)$')
    ax.set_xlim(1e-4, 0.3)
    ax.set_ylim(-1.05, -0.4)
    ax.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax.grid(True, alpha=0.3, which='both')

    fig.savefig(f'{FIGDIR}/fig1_w0_zeta0.pdf')
    fig.savefig(f'{FIGDIR}/fig1_w0_zeta0.png')
    plt.close(fig)
    print("Figure 1: w0(zeta0) parametric curve -- done")


# ============================================================
# Figure 2: w(z) evolution comparison
# ============================================================
def fig2_wz_comparison():
    fig, ax = plt.subplots(figsize=(8, 5.5))

    z = np.linspace(0, 3, 300)

    # E^2(z) for Meridian background (constant w = w0_NCG)
    def E2_mer(z):
        return Omega_m * (1 + z)**3 + Omega_DE * (1 + z)**(3 * (1 + w0_NCG))

    # Non-perturbative Meridian w(z):
    # w(z) = -1 + 2*kappa0 / (kappa0 + Omega_DE * E2(z)/E2(0))
    E2_0 = E2_mer(0)
    w_mer = np.array([-1.0 + 2 * kappa0_NCG / (kappa0_NCG + Omega_DE * E2_mer(zi) / E2_0) for zi in z])

    # CPL best-fit (DESI): w0 = -0.75, wa = -0.86
    w0_cpl, wa_cpl = -0.75, -0.86
    w_cpl = w0_cpl + wa_cpl * z / (1 + z)

    # LCDM
    w_lcdm = np.full_like(z, -1.0)

    ax.plot(z, w_mer, '-', color='#2166ac', lw=2.5, label=r'Meridian (OP#8: $w_0 = -0.830$)')
    ax.plot(z, w_cpl, '--', color='#e66101', lw=2.2, label=r'CPL best-fit ($w_0 = -0.75$, $w_a = -0.86$)')
    ax.plot(z, w_lcdm, ':', color='gray', lw=1.5, label=r'$\Lambda$CDM ($w = -1$)')

    # Phantom crossing line
    ax.axhline(-1.0, color='black', ls='-', lw=0.5, alpha=0.3)

    # Shade phantom region
    ax.fill_between(z, -1.6, -1.0, alpha=0.05, color='red')
    ax.text(2.5, -1.15, 'Phantom\nregion', fontsize=8, color='red', alpha=0.5, ha='center')

    # Mark CPL phantom crossing
    frac = -(w0_cpl + 1) / wa_cpl
    if 0 < frac < 1:
        z_phantom = frac / (1 - frac)
        ax.plot(z_phantom, -1.0, 'x', color='#e66101', ms=10, mew=2, zorder=5)
        ax.annotate(f'Phantom crossing\n$z = {z_phantom:.2f}$',
                    xy=(z_phantom, -1.0), xytext=(z_phantom + 0.4, -1.08),
                    arrowprops=dict(arrowstyle='->', color='#e66101', lw=1.2),
                    fontsize=9, color='#e66101')

    # Key discriminant at z=1
    w_mer_z1 = -1.0 + 2 * kappa0_NCG / (kappa0_NCG + Omega_DE * E2_mer(1.0) / E2_0)
    w_cpl_z1 = w0_cpl + wa_cpl * 0.5
    ax.annotate(f'$\\Delta w(z=1) = {w_mer_z1 - w_cpl_z1:.3f}$',
                xy=(1.0, (w_mer_z1 + w_cpl_z1)/2), xytext=(1.6, -0.85),
                arrowprops=dict(arrowstyle='->', color='black', lw=1),
                fontsize=9, bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', ec='gray'))

    ax.set_xlabel(r'Redshift $z$')
    ax.set_ylabel(r'$w(z)$ (dark energy equation of state)')
    ax.set_title(r'Dark Energy Evolution: Meridian vs CPL vs $\Lambda$CDM')
    ax.set_xlim(0, 3)
    ax.set_ylim(-1.5, -0.5)
    ax.legend(loc='lower right', framealpha=0.9)
    ax.grid(True, alpha=0.3)

    fig.savefig(f'{FIGDIR}/fig2_wz_comparison.pdf')
    fig.savefig(f'{FIGDIR}/fig2_wz_comparison.png')
    plt.close(fig)
    print("Figure 2: w(z) evolution comparison -- done")


# ============================================================
# Figure 3: Chi-squared model comparison
# ============================================================
def fig3_chi2_comparison():
    fig, ax = plt.subplots(figsize=(7, 4.5))

    models = [r'$\Lambda$CDM', 'CPL\n(DESI)', 'Meridian\n(pert.)',
              'Meridian\n(exact)', r'$w$CDM' + '\n(const.)']
    chi2 = [84.9, 42.3, 45.6, 81.0, 124.7]
    colors = ['#969696', '#4daf4a', '#2166ac', '#92c5de', '#d73027']

    bars = ax.barh(models, chi2, color=colors, edgecolor='white', height=0.6)

    # Add value labels
    for bar, val in zip(bars, chi2):
        ax.text(val + 1.5, bar.get_y() + bar.get_height()/2,
                f'{val:.1f}', va='center', fontsize=10, fontweight='bold')

    # Reference line for CPL
    ax.axvline(42.3, color='#4daf4a', ls='--', lw=1, alpha=0.5)

    ax.set_xlabel(r'$\chi^2$ (12 DESI DR2 BAO data points)')
    ax.set_title(r'Model Comparison: $\chi^2$ for DESI DR2 BAO')
    ax.set_xlim(0, 140)
    ax.invert_yaxis()

    # Add annotation
    ax.text(70, 1.5, r'$\Delta\chi^2$(Meridian $-$ CPL) $= +3.3$' + '\n($1.8\\sigma$, not significant)',
            fontsize=9, bbox=dict(boxstyle='round,pad=0.4', fc='lightyellow', ec='gray'),
            ha='center')

    fig.savefig(f'{FIGDIR}/fig3_chi2_comparison.pdf')
    fig.savefig(f'{FIGDIR}/fig3_chi2_comparison.png')
    plt.close(fig)
    print("Figure 3: Chi-squared model comparison -- done")


# ============================================================
# Figure 4: Inflationary (n_s, r) prediction plane
# ============================================================
def fig4_inflation():
    fig, ax = plt.subplots(figsize=(7, 5.5))

    # Planck 2018 contours (approximate)
    from matplotlib.patches import Ellipse
    # 68% CL
    e1 = Ellipse((0.9649, 0.0), width=2*0.0042, height=2*0.015,
                 fill=True, fc='#fee8c8', ec='#fdbb84', lw=1.5, alpha=0.7, label='Planck 2018 (68% CL)')
    # 95% CL
    e2 = Ellipse((0.9649, 0.0), width=2*0.0084, height=2*0.036,
                 fill=True, fc='#fdd49e', ec='#fdbb84', lw=1, alpha=0.4, label='Planck 2018 (95% CL)')
    ax.add_patch(e2)
    ax.add_patch(e1)

    # BICEP/Keck 2021 upper bound
    ax.axhline(0.036, color='#e34a33', ls='--', lw=1.5, alpha=0.7, label='BICEP/Keck 2021 ($r < 0.036$)')

    # Meridian prediction band (N* = 50-60)
    N_star = np.linspace(50, 60, 50)
    ns_pred = 1 - 2/N_star
    r_pred = 12/N_star**2

    ax.plot(ns_pred, r_pred, '-', color='#2166ac', lw=2.5, label=r'Meridian ($\alpha = 1$ attractor)')
    ax.plot(0.9649, 0.0037, 'o', color='#2166ac', ms=10, zorder=5,
            markeredgecolor='white', markeredgewidth=1.5)
    ax.annotate(r'$N_* = 57$' + f'\n$n_s = 0.965$\n$r = 0.004$',
                xy=(0.9649, 0.0037), xytext=(0.955, 0.015),
                arrowprops=dict(arrowstyle='->', color='#2166ac', lw=1.5),
                fontsize=9, color='#2166ac')

    # QQG prediction
    ax.axhspan(0.01, 0.05, alpha=0.1, color='#d73027')
    ax.text(0.975, 0.025, 'QQG\n($r \\geq 0.01$)', fontsize=9, color='#d73027',
            ha='center', alpha=0.7)

    # LiteBIRD sensitivity
    ax.axhline(0.001, color='#756bb1', ls=':', lw=1.5, alpha=0.7,
               label=r'LiteBIRD sensitivity ($\sigma(r) \sim 10^{-3}$)')

    # CMB-S4 sensitivity
    ax.axhline(0.001, color='#756bb1', ls=':', lw=1.5, alpha=0.7)

    ax.set_xlabel(r'Scalar spectral index $n_s$')
    ax.set_ylabel(r'Tensor-to-scalar ratio $r$')
    ax.set_title(r'Inflationary Predictions: $n_s$--$r$ Plane')
    ax.set_xlim(0.94, 0.98)
    ax.set_ylim(0, 0.05)
    ax.legend(loc='upper right', framealpha=0.9, fontsize=8.5)
    ax.grid(True, alpha=0.3)

    fig.savefig(f'{FIGDIR}/fig4_inflation_nsr.pdf')
    fig.savefig(f'{FIGDIR}/fig4_inflation_nsr.png')
    plt.close(fig)
    print("Figure 4: Inflationary (n_s, r) plane -- done")


# ============================================================
# Figure 5: Fermion localization profiles
# ============================================================
def fig5_fermion_profiles():
    fig, ax = plt.subplots(figsize=(8, 5))

    y = np.linspace(0, 1, 500)  # y/y_c normalized
    ky_c = 35.0

    # Bulk mass parameters (from Table 4-ci)
    fermions = {
        r'$t$ ($c = 0.004$)':   (0.004, '#d73027'),
        r'$b$ ($c = 0.503$)':   (0.503, '#fc8d59'),
        r'$c$ ($c = 0.530$)':   (0.530, '#fee090'),
        r'$\mu$ ($c = 0.574$)': (0.574, '#91bfdb'),
        r'$u$ ($c = 0.635$)':   (0.635, '#4575b4'),
        r'$e$ ($c = 0.656$)':   (0.656, '#313695'),
    }

    for label, (c_i, color) in fermions.items():
        # Left-handed zero mode: f_L(y) ~ exp((2-c)*k*y)
        # Normalized on warp factor
        profile = np.exp((2 - c_i) * ky_c * y) * np.exp(-4 * ky_c * y / 2)
        # Simplified: profile ~ exp((2 - c_i - 2)*ky_c*y) = exp(-c_i * ky_c * y)
        profile = np.exp(-c_i * ky_c * y)
        profile = profile / np.max(profile)
        ax.plot(y, profile, '-', color=color, lw=2, label=label)

    # Mark UV and IR branes
    ax.axvline(0, color='black', lw=2, alpha=0.3)
    ax.axvline(1, color='black', lw=2, alpha=0.3)
    ax.text(0.02, 0.95, 'UV brane', fontsize=9, transform=ax.transAxes, va='top')
    ax.text(0.88, 0.95, 'IR brane\n(Higgs)', fontsize=9, transform=ax.transAxes, va='top')

    # Higgs localization (delta function at IR)
    ax.fill_between([0.95, 1.0], 0, 1, alpha=0.15, color='#fdae61',
                    label='Higgs (IR-localized)')

    ax.set_xlabel(r'Position in extra dimension $y/y_c$')
    ax.set_ylabel(r'Fermion zero-mode profile $|f^{(0)}(y)|$ (normalized)')
    ax.set_title(r'Fermion Localization in the Warped Extra Dimension')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.legend(loc='center right', framealpha=0.9, fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.savefig(f'{FIGDIR}/fig5_fermion_profiles.pdf')
    fig.savefig(f'{FIGDIR}/fig5_fermion_profiles.png')
    plt.close(fig)
    print("Figure 5: Fermion localization profiles -- done")


# ============================================================
# Figure 6: epsilon_1 Goldilocks window
# ============================================================
def fig6_goldilocks():
    fig, ax = plt.subplots(figsize=(8, 5))

    eps_range = np.logspace(-3, 0, 500)
    zeta0 = zeta0_JC

    # |1 + w0| at JC benchmark
    deviation_JC = eps_range * (1 + q0)**2 * Omega_DE / (4 * (1 - q0)**2 * zeta0)

    # Perturbative breakdown: |1+w0| > 1 means w0 > 0 or w0 < -2
    ax.fill_between(eps_range, 1, 10, alpha=0.1, color='red')
    ax.text(0.3, 2, 'Perturbative\nbreakdown', fontsize=9, color='red', ha='center')

    # DESI sensitivity floor
    ax.axhline(0.05, color='#4daf4a', ls='--', lw=1.5, alpha=0.7,
               label='DESI DR2 sensitivity ($|1+w_0| > 0.05$)')

    ax.plot(eps_range, deviation_JC, '-', color='#2166ac', lw=2.5,
            label=r'$|1+w_0|$ at JC benchmark ($\zeta_0 = 10^{-3}$)')

    # Mark the actual value
    actual_dev = eps1 * (1 + q0)**2 * Omega_DE / (4 * (1 - q0)**2 * zeta0)
    ax.plot(eps1, actual_dev, 'o', color='#2166ac', ms=12, zorder=5,
            markeredgecolor='white', markeredgewidth=2)
    ax.annotate(f'$\\epsilon_1 = 0.010$\n$|1+w_0| = {actual_dev:.3f}$',
                xy=(eps1, actual_dev), xytext=(0.06, 0.15),
                arrowprops=dict(arrowstyle='->', color='#2166ac', lw=1.5),
                fontsize=10, color='#2166ac')

    # Show 10x smaller and larger
    ax.plot(eps1/10, actual_dev/10, 'v', color='gray', ms=8, zorder=5)
    ax.annotate(r'$10\times$ smaller: below sensitivity',
                xy=(eps1/10, actual_dev/10), xytext=(0.003, 0.015),
                arrowprops=dict(arrowstyle='->', color='gray', lw=1),
                fontsize=8, color='gray')

    ax.plot(eps1*10, actual_dev*10, '^', color='#d73027', ms=8, zorder=5)
    ax.annotate(r'$10\times$ larger: breaks perturbation theory',
                xy=(eps1*10, actual_dev*10), xytext=(0.2, 1.5),
                arrowprops=dict(arrowstyle='->', color='#d73027', lw=1),
                fontsize=8, color='#d73027')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel(r'Gauss-Bonnet coupling $\epsilon_1$')
    ax.set_ylabel(r'$|1 + w_0|$')
    ax.set_title(r'The $\epsilon_1$ Goldilocks Window')
    ax.set_xlim(1e-3, 1)
    ax.set_ylim(0.005, 5)
    ax.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax.grid(True, alpha=0.3, which='both')

    fig.savefig(f'{FIGDIR}/fig6_goldilocks.pdf')
    fig.savefig(f'{FIGDIR}/fig6_goldilocks.png')
    plt.close(fig)
    print("Figure 6: epsilon_1 Goldilocks window -- done")


# ============================================================
# Figure 7: Sensitivity forecast timeline
# ============================================================
def fig7_forecast():
    fig, ax = plt.subplots(figsize=(8, 4.5))

    epochs = ['Current\n(DESI DR2)', 'DESI DR3\n(~2027)', 'DESI Y5\n(~2027)',
              'DESI Y5 +\nEuclid (~2030)']
    sigma_w0 = [0.046, 0.04, 0.025, 0.01]
    sigma_zeta = [4.2e-4, 3.5e-4, 2.0e-4, 1.0e-4]
    discrimination_sigma = [2.4, 3.0, 3.8, 5.1]

    x = np.arange(len(epochs))
    width = 0.35

    ax2 = ax.twinx()

    bars1 = ax.bar(x - width/2, sigma_w0, width, color='#2166ac', alpha=0.7,
                   label=r'$\sigma(w_0)$', edgecolor='white')
    bars2 = ax2.bar(x + width/2, discrimination_sigma, width, color='#d73027', alpha=0.7,
                    label=r'Discrimination ($\sigma$)', edgecolor='white')

    # Add value labels
    for bar, val in zip(bars1, sigma_w0):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{val:.3f}', ha='center', va='bottom', fontsize=8, color='#2166ac')
    for bar, val in zip(bars2, discrimination_sigma):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f'{val:.1f}$\\sigma$', ha='center', va='bottom', fontsize=8, color='#d73027')

    # 5-sigma line
    ax2.axhline(5.0, color='#d73027', ls='--', lw=1.5, alpha=0.5)
    ax2.text(3.3, 5.15, r'$5\sigma$ discovery', fontsize=8, color='#d73027', alpha=0.7)

    # 3-sigma line
    ax2.axhline(3.0, color='orange', ls=':', lw=1, alpha=0.5)
    ax2.text(3.3, 3.15, r'$3\sigma$ evidence', fontsize=8, color='orange', alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(epochs)
    ax.set_ylabel(r'$\sigma(w_0)$ precision', color='#2166ac')
    ax2.set_ylabel(r'Discrimination significance ($\sigma$)', color='#d73027')
    ax.set_title('Sensitivity Forecast: Meridian vs $\\Lambda$CDM')
    ax.set_ylim(0, 0.06)
    ax2.set_ylim(0, 6)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper center', framealpha=0.9)

    fig.savefig(f'{FIGDIR}/fig7_forecast.pdf')
    fig.savefig(f'{FIGDIR}/fig7_forecast.png')
    plt.close(fig)
    print("Figure 7: Sensitivity forecast timeline -- done")


# ============================================================
# Figure 8: Sound speed landscape
# ============================================================
def fig8_sound_speed():
    fig, ax = plt.subplots(figsize=(8, 5))

    models = [
        (r'$\Lambda$CDM',              0, '#969696', 'N/A'),
        ('Quintessence',                1.0, '#fdae61', 'Free'),
        ('K-essence',                   0.3, '#f46d43', 'Free'),
        ('DBI',                         0.1, '#d73027', 'Free'),
        ('Ghost condensate',            0.001, '#a50026', 'Tuned'),
        ('Galileon',                    5.0, '#74add1', 'Free'),
        ('Pure cuscuton',              1000, '#313695', r'$\infty$ (exact)'),
        (r'Meridian ($c_s = 15c$)',    15.0, '#2166ac', 'Derived'),
    ]

    names = [m[0] for m in models]
    cs_vals = [m[1] for m in models]
    colors = [m[2] for m in models]
    status = [m[3] for m in models]

    # Use log scale for the bar chart
    cs_plot = [max(v, 0.01) for v in cs_vals]  # avoid log(0)

    bars = ax.barh(names, cs_plot, color=colors, edgecolor='white', height=0.6)

    # Special handling for LCDM (no propagating DOF)
    ax.text(0.015, 0, 'No propagating\nscalar DOF', fontsize=7, va='center', color='gray')

    # Add status labels
    for bar, s in zip(bars, status):
        x_pos = bar.get_width() * 1.2 if bar.get_width() < 100 else bar.get_width() * 0.5
        ax.text(x_pos, bar.get_y() + bar.get_height()/2,
                s, va='center', fontsize=8, fontstyle='italic', alpha=0.7)

    # c = 1 line (speed of light)
    ax.axvline(1.0, color='black', ls='--', lw=1.5, alpha=0.5)
    ax.text(1.1, 7.5, '$c$', fontsize=10, va='center')

    ax.set_xscale('log')
    ax.set_xlabel(r'Sound speed $c_s / c$')
    ax.set_title(r'Dark Energy Sound Speed Landscape')
    ax.set_xlim(0.005, 5000)
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, which='both', axis='x')

    # Highlight Meridian
    bars[-1].set_edgecolor('#2166ac')
    bars[-1].set_linewidth(2)

    fig.savefig(f'{FIGDIR}/fig8_sound_speed.pdf')
    fig.savefig(f'{FIGDIR}/fig8_sound_speed.png')
    plt.close(fig)
    print("Figure 8: Sound speed landscape -- done")


# ============================================================
# Run all
# ============================================================
if __name__ == '__main__':
    print("Generating Meridian Monograph figures...")
    print("=" * 50)
    fig1_w0_zeta0()
    fig2_wz_comparison()
    fig3_chi2_comparison()
    fig4_inflation()
    fig5_fermion_profiles()
    fig6_goldilocks()
    fig7_forecast()
    fig8_sound_speed()
    print("=" * 50)
    print(f"All figures saved to {FIGDIR}")
