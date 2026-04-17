"""
Generate updated figures using Lee 2025 CAMB refit results.
April 1, 2026. Clawd.

Produces:
  fig3_chi2_comparison.pdf/png — Updated chi2 landscape vs w0
  fig9_bao_residuals.pdf/png  — BAO chi2 decomposition by probe
"""

import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
    'text.usetex': False,
    'mathtext.fontset': 'cm',
})

import os, sys
if sys.platform != 'win32':
    FIGDIR = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/monograph/figures'
    DATAFILE = '/mnt/c/Users/mercu/clawd/projects/Project Meridian/monograph/scripts/camb_multiprobe_results_lee2025.json'
else:
    FIGDIR = r'C:\Users\mercu\clawd\projects\Project Meridian\monograph\figures'
    DATAFILE = r'C:\Users\mercu\clawd\projects\Project Meridian\monograph\scripts\camb_multiprobe_results_lee2025.json'

with open(DATAFILE) as f:
    d = json.load(f)

w0 = np.array(d['w0'])
chi2_bao = np.array(d['chi2_bao'])
chi2_total = np.array(d['chi2_total'])
chi2_fs8 = np.array(d['chi2_fsigma8'])
chi2_h0 = np.array(d['chi2_H0'])
chi2_hk = np.array(d['chi2_HK'])
H0_prof = np.array(d['H0_profile'])

# ============================================================
# Figure 3 (updated): BAO-only chi2 landscape vs w0
# ============================================================
def fig3_chi2_landscape():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 8), sharex=True,
                                    gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.08})

    # --- Top panel: BAO chi2 ---
    bao_lcdm = chi2_bao[np.argmin(np.abs(w0 - (-0.999)))]

    ax1.plot(w0, chi2_bao, 'b-', lw=2, label=r'$\chi^2_{\rm BAO}$ (13 DESI DR2 observables)')

    # Delta chi2 reference lines
    ax1.axhline(bao_lcdm, color='gray', ls=':', lw=1, alpha=0.5)
    ax1.axhline(bao_lcdm + 1, color='gray', ls='--', lw=0.8, alpha=0.4)
    ax1.axhline(bao_lcdm + 4, color='gray', ls='--', lw=0.8, alpha=0.4)
    ax1.axhline(bao_lcdm + 9, color='gray', ls='--', lw=0.8, alpha=0.4)
    ax1.text(-0.505, bao_lcdm + 1.2, r'$\Delta\chi^2 = 1$', fontsize=8, color='gray')
    ax1.text(-0.505, bao_lcdm + 4.2, r'$\Delta\chi^2 = 4$', fontsize=8, color='gray')
    ax1.text(-0.505, bao_lcdm + 9.2, r'$\Delta\chi^2 = 9$', fontsize=8, color='gray')

    # Mark key points
    # LCDM
    idx_lcdm = np.argmin(np.abs(w0 - (-0.999)))
    ax1.plot(w0[idx_lcdm], chi2_bao[idx_lcdm], 'ks', ms=8, zorder=5,
             label=r'$\Lambda$CDM ($\chi^2 = %.1f$)' % chi2_bao[idx_lcdm])

    # Non-perturbative
    idx_np = np.argmin(np.abs(w0 - (-0.865)))
    ax1.plot(w0[idx_np], chi2_bao[idx_np], 'ro', ms=8, zorder=5,
             label=r'Non-pert. $w_0 = -0.865$ ($\Delta\chi^2 = %.1f$)' % (chi2_bao[idx_np] - bao_lcdm))

    # Perturbative
    idx_pt = np.argmin(np.abs(w0 - (-0.851)))
    ax1.plot(w0[idx_pt], chi2_bao[idx_pt], 'r^', ms=8, zorder=5,
             label=r'Pert. $w_0 = -0.851$ ($\Delta\chi^2 = %.1f$)' % (chi2_bao[idx_pt] - bao_lcdm))

    # Lee 2025 wCDM best fit
    ax1.axvline(-0.918, color='green', ls='--', lw=1, alpha=0.7)
    ax1.text(-0.915, chi2_bao.max() * 0.95, 'Lee\nwCDM', fontsize=8, color='green', ha='left')

    # Lee 2025 reference chi2 (shifted by our systematic)
    lee_lcdm_ref = 10.15
    offset = bao_lcdm - lee_lcdm_ref
    ax1.text(-0.68, bao_lcdm + 0.5,
             r'Lee ref: $\chi^2_{\Lambda\rm CDM} = 10.15$' + '\n' +
             r'(our offset: $+%.1f$)' % offset,
             fontsize=8, bbox=dict(boxstyle='round,pad=0.3', fc='lightyellow', ec='gray'))

    ax1.set_ylabel(r'$\chi^2_{\rm BAO}$ (Lee 2025 covariance)')
    ax1.set_ylim(10, 35)
    ax1.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax1.set_title('DESI DR2 BAO with Lee 2025 Covariance: Profile Likelihood')

    # --- Bottom panel: Profiled H0 ---
    ax2.plot(w0, H0_prof, 'k-', lw=1.5)
    ax2.axhspan(67.36 - 0.54, 67.36 + 0.54, color='orange', alpha=0.2, label=r'Planck $H_0$ ($1\sigma$)')
    ax2.axhline(67.36, color='orange', ls='-', lw=1)

    ax2.plot(w0[idx_np], H0_prof[idx_np], 'ro', ms=6, zorder=5)
    ax2.plot(w0[idx_pt], H0_prof[idx_pt], 'r^', ms=6, zorder=5)
    ax2.plot(w0[idx_lcdm], H0_prof[idx_lcdm], 'ks', ms=6, zorder=5)

    ax2.set_xlabel(r'$w_0$')
    ax2.set_ylabel(r'Profiled $H_0$ [km/s/Mpc]')
    ax2.set_xlim(-1.0, -0.50)
    ax2.set_ylim(54, 70)
    ax2.legend(loc='lower left', fontsize=9)

    fig.savefig(f'{FIGDIR}/fig3_chi2_comparison.pdf')
    fig.savefig(f'{FIGDIR}/fig3_chi2_comparison.png')
    plt.close(fig)
    print("Figure 3 (updated): BAO chi2 landscape -- done")


# ============================================================
# Figure 9: Multi-probe chi2 decomposition
# ============================================================
def fig9_multiprobe_decomposition():
    fig, ax = plt.subplots(figsize=(7, 5))

    # Restrict to w0 > -0.998 to avoid the HK spike at LCDM
    mask = w0 > -0.998

    ax.fill_between(w0[mask], 0, chi2_bao[mask], alpha=0.3, color='#2166ac', label=r'BAO ($\chi^2_{\rm BAO}$)')
    ax.fill_between(w0[mask], chi2_bao[mask], chi2_bao[mask] + chi2_fs8[mask],
                    alpha=0.3, color='#4daf4a', label=r'$f\sigma_8$ ($\chi^2_{f\sigma_8}$)')
    ax.fill_between(w0[mask], chi2_bao[mask] + chi2_fs8[mask],
                    chi2_bao[mask] + chi2_fs8[mask] + chi2_h0[mask],
                    alpha=0.3, color='#ff7f00', label=r'$H_0$ prior ($\chi^2_{H_0}$)')
    ax.fill_between(w0[mask], chi2_bao[mask] + chi2_fs8[mask] + chi2_h0[mask],
                    chi2_total[mask],
                    alpha=0.3, color='#984ea3', label=r'$\beta_{\rm HK}$ ($\chi^2_{\rm HK}$)')

    ax.plot(w0[mask], chi2_total[mask], 'k-', lw=2, label='Total')

    # Best fit
    idx_best = np.argmin(chi2_total)
    ax.plot(w0[idx_best], chi2_total[idx_best], 'k*', ms=12, zorder=5,
            label=r'Best fit $w_0 = %.3f$' % w0[idx_best])

    # Mark non-perturbative
    idx_np = np.argmin(np.abs(w0 - (-0.865)))
    ax.axvline(-0.865, color='red', ls='--', lw=1, alpha=0.7)
    ax.text(-0.862, 60, r'$w_0 = -0.865$' + '\n(non-pert.)', fontsize=8, color='red')

    ax.set_xlabel(r'$w_0$')
    ax.set_ylabel(r'$\chi^2$')
    ax.set_title('Multi-Probe Profile Likelihood Decomposition')
    ax.set_xlim(-0.998, -0.80)
    ax.set_ylim(0, 100)
    ax.legend(loc='upper left', fontsize=9, ncol=2)

    fig.savefig(f'{FIGDIR}/fig9_bao_residuals.pdf')
    fig.savefig(f'{FIGDIR}/fig9_bao_residuals.png')
    plt.close(fig)
    print("Figure 9: Multi-probe decomposition -- done")


if __name__ == '__main__':
    fig3_chi2_landscape()
    fig9_multiprobe_decomposition()
    print("\nAll Lee 2025 figures generated.")
