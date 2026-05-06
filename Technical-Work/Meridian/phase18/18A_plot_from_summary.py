"""
Generate approximate plots from 18A MCMC summary statistics.
Chain data was lost to a Unicode crash — this reconstructs
Gaussian approximations for visual communication.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Results from the log
# Fit A posterior
A_w0_mean, A_w0_std = -1.049, 0.041
A_Om_mean, A_Om_std = 0.302, 0.010
A_H0_mean, A_H0_std = 68.91, 1.12

# Fit B posterior
B_w0_mean, B_w0_std = -0.324, 0.170
B_wa_mean, B_wa_std = -2.300, 0.537
B_Om_mean, B_Om_std = 0.352, 0.016
B_H0_mean, B_H0_std = 64.08, 1.47

# Probe chi2 decomposition
probes = ['BAO', 'SNe', 'CMB', r'f$\sigma_8$', 'Total']
chi2_A = [41.56, 67.69, 1.51, 8.09, 118.84]
chi2_B = [41.09, 55.85, 0.17, 7.10, 104.21]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('18A Proper MCMC: Decoupled Perturbation Test\n(Gaussian approximations from summary statistics)',
             fontsize=13, fontweight='bold')

# 1. wa posterior (Fit B)
ax = axes[0, 0]
wa_x = np.linspace(-4, 0, 500)
wa_pdf = np.exp(-0.5 * ((wa_x - B_wa_mean) / B_wa_std)**2) / (B_wa_std * np.sqrt(2*np.pi))
ax.fill_between(wa_x, wa_pdf, alpha=0.4, color='steelblue', label='Fit B posterior')
ax.plot(wa_x, wa_pdf, color='steelblue', lw=2)
ax.axvline(0, color='red', ls='--', lw=2, label='Meridian ($w_a = 0$)')
ax.axvline(-0.62, color='orange', ls='--', lw=2, label='DESI ($w_a = -0.62$)')
ax.set_xlabel('$w_a$', fontsize=12)
ax.set_ylabel('Probability density', fontsize=12)
ax.set_title('$w_a$ Posterior (Fit B: CPL)', fontsize=11)
ax.legend(fontsize=9)
ax.text(0.05, 0.95, f'$w_a = {B_wa_mean:.2f} \\pm {B_wa_std:.2f}$\n'
        f'4.3$\\sigma$ from 0\n3.3$\\sigma$ from DESI',
        transform=ax.transAxes, va='top', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 2. w0 comparison
ax = axes[0, 1]
w0_x = np.linspace(-1.3, 0.2, 500)
w0_A_pdf = np.exp(-0.5 * ((w0_x - A_w0_mean) / A_w0_std)**2) / (A_w0_std * np.sqrt(2*np.pi))
w0_B_pdf = np.exp(-0.5 * ((w0_x - B_w0_mean) / B_w0_std)**2) / (B_w0_std * np.sqrt(2*np.pi))
ax.fill_between(w0_x, w0_A_pdf, alpha=0.4, color='blue', label='Fit A (const-w, GR)')
ax.fill_between(w0_x, w0_B_pdf, alpha=0.4, color='red', label='Fit B (CPL)')
ax.plot(w0_x, w0_A_pdf, color='blue', lw=2)
ax.plot(w0_x, w0_B_pdf, color='red', lw=2)
ax.axvline(-0.746, color='green', ls='--', lw=2, label='Meridian JC benchmark')
ax.axvline(-1.0, color='gray', ls=':', lw=1.5, label='$\\Lambda$CDM')
ax.set_xlabel('$w_0$', fontsize=12)
ax.set_ylabel('Probability density', fontsize=12)
ax.set_title('$w_0$ Posterior Comparison', fontsize=11)
ax.legend(fontsize=8, loc='upper left')

# 3. Probe chi2 bar chart
ax = axes[1, 0]
x = np.arange(len(probes))
width = 0.35
bars_A = ax.bar(x - width/2, chi2_A, width, label='Fit A (const-w)', color='steelblue', alpha=0.8)
bars_B = ax.bar(x + width/2, chi2_B, width, label='Fit B (CPL)', color='coral', alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(probes, fontsize=10)
ax.set_ylabel('$\\chi^2$', fontsize=12)
ax.set_title('Probe-by-Probe $\\chi^2$ at Best Fit', fontsize=11)
ax.legend(fontsize=9)
# Annotate the SNe difference
ax.annotate(f'$\\Delta = +11.84$\n(81% of signal)',
            xy=(1, 67.69), xytext=(1.8, 75),
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
            fontsize=9, color='red', fontweight='bold')

# 4. Summary text panel
ax = axes[1, 1]
ax.axis('off')
summary_text = (
    "18A MCMC Results Summary\n"
    "========================\n\n"
    f"$\\Delta$AIC (A$-$B) = +12.63\n"
    f"$\\Delta$BIC (A$-$B) = +10.91\n\n"
    "Formally: 'decisive' for CPL\n\n"
    "BUT:\n"
    "  - SNe drive 81% of signal\n"
    "    (diagonal-only, 0.25 mag floor)\n"
    "  - Fit B: $w_a = -2.94$ (prior boundary)\n"
    "  - Fit B: $H_0 = 62.7$ (unphysical)\n"
    "  - Growth $\\Delta\\chi^2 = 0.99$ (no split)\n"
    "  - $w_a$ 3.3$\\sigma$ from DESI\n\n"
    "Assessment: INCONCLUSIVE\n"
    "Bottleneck: Pantheon+ covariance"
)
ax.text(0.1, 0.95, summary_text, transform=ax.transAxes,
        fontsize=11, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.savefig('C:/Users/mercu/clawd/projects/Project Meridian/phase18/18A_proper_results.png',
            dpi=150, bbox_inches='tight')
print("Plot saved to 18A_proper_results.png")
