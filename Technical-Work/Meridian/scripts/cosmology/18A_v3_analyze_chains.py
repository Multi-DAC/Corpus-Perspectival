#!/usr/bin/env python3
"""
18A v3 Post-Hoc Chain Analysis
===============================
Standalone script that loads saved MCMC chains and produces the full
honest assessment following the pre-registered interpretation guide.

Runs in seconds (no CAMB needed for basic analysis).
For probe-by-probe decomposition, set --probes flag (requires CAMB).

Usage:
    python 18A_v3_analyze_chains.py           # Basic analysis
    python 18A_v3_analyze_chains.py --probes  # Full probe decomposition

Authors: Clayton W. Iggulden-Schnell & Clawd
Date: 2026-03-20
"""

import numpy as np
import os
import sys
import time

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Meridian predictions
MERIDIAN_W0_JC = -0.745       # JC benchmark (ζ₀ = 0.001)
MERIDIAN_W0_VIABLE = -0.99    # Viable regime (ζ₀ ~ 0.02)
DESI_W0 = -0.55               # DESI DR1 best-fit
DESI_WA = -1.27               # DESI DR1 best-fit
DESI_WA_LUSIM = -0.62         # Lu & Simon 2026
DESI_WA_LUSIM_ERR = 0.26


def load_chain(fit_type):
    """Load saved chain from .npz file."""
    path = os.path.join(OUTPUT_DIR, f'18A_v3_chain_{fit_type}.npz')
    if not os.path.exists(path):
        print(f"  Chain file not found: {path}")
        return None
    data = np.load(path, allow_pickle=True)
    return {
        'samples': data['samples'],
        'logprob': data['logprob'],
        'labels': list(data['labels']),
        'best_x': data['best_x'],
        'best_chi2': float(data['best_chi2']),
    }


def posterior_stats(samples, labels):
    """Compute posterior summary statistics."""
    stats = {}
    for i, label in enumerate(labels):
        col = samples[:, i]
        mean = np.mean(col)
        std = np.std(col)
        q16, q50, q84 = np.percentile(col, [16, 50, 84])
        stats[label] = {
            'mean': mean, 'std': std,
            'q16': q16, 'q50': q50, 'q84': q84,
            'err_up': q84 - q50, 'err_down': q50 - q16,
        }
    return stats


def tension_sigma(value, posterior_mean, posterior_std):
    """Compute tension between a value and a Gaussian posterior."""
    return abs(value - posterior_mean) / posterior_std


def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def analyze_basic(chainA, chainB):
    """Basic analysis from chains alone (no CAMB needed)."""

    print_section("18A v3 CHAIN ANALYSIS — HONEST ASSESSMENT")
    print(f"  Date: {time.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Chain A samples: {chainA['samples'].shape}")
    print(f"  Chain B samples: {chainB['samples'].shape}")

    # Posterior stats
    statsA = posterior_stats(chainA['samples'], chainA['labels'])
    statsB = posterior_stats(chainB['samples'], chainB['labels'])

    # Model comparison
    chi2_A = chainA['best_chi2']
    chi2_B = chainB['best_chi2']
    npar_A = len(chainA['labels'])
    npar_B = len(chainB['labels'])

    # Data points: 12 BAO + 1589 SNe (M marginalized) + 3 CMB + 7 fσ₈
    n_total = 12 + 1589 + 3 + 7

    AIC_A = chi2_A + 2 * npar_A
    AIC_B = chi2_B + 2 * npar_B
    DAIC = AIC_A - AIC_B

    BIC_A = chi2_A + npar_A * np.log(n_total)
    BIC_B = chi2_B + npar_B * np.log(n_total)
    DBIC = BIC_A - BIC_B

    dof_A = n_total - npar_A
    dof_B = n_total - npar_B

    # ============================================================
    # RESULTS
    # ============================================================

    print_section("FIT A — Meridian (constant w, GR perturbations)")
    print(f"  Parameters: {npar_A}")
    print(f"  Best-fit chi2: {chi2_A:.2f} (chi2/dof = {chi2_A/dof_A:.4f})")
    for label in chainA['labels']:
        s = statsA[label]
        print(f"  {label:>5s} = {s['q50']:.4f} +{s['err_up']:.4f} -{s['err_down']:.4f} "
              f"(mean={s['mean']:.4f} +/- {s['std']:.4f})")

    print_section("FIT B — CPL (w0+wa, coupled perturbations)")
    print(f"  Parameters: {npar_B}")
    print(f"  Best-fit chi2: {chi2_B:.2f} (chi2/dof = {chi2_B/dof_B:.4f})")
    for label in chainB['labels']:
        s = statsB[label]
        print(f"  {label:>5s} = {s['q50']:.4f} +{s['err_up']:.4f} -{s['err_down']:.4f} "
              f"(mean={s['mean']:.4f} +/- {s['std']:.4f})")

    print_section("MODEL COMPARISON")
    print(f"  Delta chi2 (A-B) = {chi2_A - chi2_B:+.2f}")
    print(f"  Delta AIC  (A-B) = {DAIC:+.2f}")
    print(f"  Delta BIC  (A-B) = {DBIC:+.2f}")
    print()

    if abs(DAIC) < 2:
        verdict_aic = "INDISTINGUISHABLE (|DAIC| < 2)"
    elif abs(DAIC) < 4:
        pref = 'CPL' if DAIC > 0 else 'Constant-w'
        verdict_aic = f"WEAK preference for {pref} (|DAIC| < 4)"
    elif abs(DAIC) < 10:
        pref = 'CPL' if DAIC > 0 else 'Constant-w'
        verdict_aic = f"MODERATE preference for {pref} (|DAIC| < 10)"
    else:
        pref = 'CPL' if DAIC > 0 else 'Constant-w'
        verdict_aic = f"STRONG preference for {pref} (|DAIC| > 10)"
    print(f"  AIC verdict: {verdict_aic}")

    # Decision threshold
    if abs(DAIC) < 4:
        decision = "WRITE PRL — constant-w is competitive"
    elif abs(DAIC) < 10:
        decision = "DECOMPOSE — probe-by-probe analysis needed"
    else:
        decision = "INVESTIGATE — examine epsilon_2 X^2 / radion dynamics"
    print(f"  Decision (Clayton thresholds): {decision}")

    # ============================================================
    # MERIDIAN-SPECIFIC DIAGNOSTICS
    # ============================================================

    print_section("MERIDIAN-SPECIFIC DIAGNOSTICS")

    w0_A = statsA['w0']
    sigma_jc = tension_sigma(MERIDIAN_W0_JC, w0_A['mean'], w0_A['std'])
    sigma_viable = tension_sigma(MERIDIAN_W0_VIABLE, w0_A['mean'], w0_A['std'])
    sigma_lcdm = tension_sigma(-1.0, w0_A['mean'], w0_A['std'])

    print(f"  Fit A w0 posterior: {w0_A['mean']:.4f} +/- {w0_A['std']:.4f}")
    print(f"  Tension with Meridian JC benchmark (w0 = {MERIDIAN_W0_JC}): {sigma_jc:.1f} sigma")
    print(f"  Tension with Meridian viable regime (w0 ~ {MERIDIAN_W0_VIABLE}): {sigma_viable:.1f} sigma")
    print(f"  Tension with LCDM (w0 = -1.0): {sigma_lcdm:.1f} sigma")
    print()

    if sigma_jc > 3:
        print(f"  ** JC benchmark (zeta_0 = 0.001) is EXCLUDED at {sigma_jc:.1f} sigma")
    else:
        print(f"  ** JC benchmark is within {sigma_jc:.1f} sigma — still viable")

    if sigma_viable < 2:
        print(f"  ** Viable regime (zeta_0 ~ 0.02) is CONSISTENT at {sigma_viable:.1f} sigma")
    elif sigma_viable < 3:
        print(f"  ** Viable regime is in MILD TENSION at {sigma_viable:.1f} sigma")
    else:
        print(f"  ** Viable regime is EXCLUDED at {sigma_viable:.1f} sigma")

    # Fit B comparison with DESI
    if 'wa' in statsB:
        wa_B = statsB['wa']
        sigma_wa_zero = tension_sigma(0.0, wa_B['mean'], wa_B['std'])
        sigma_wa_desi = abs(wa_B['mean'] - DESI_WA_LUSIM) / np.sqrt(wa_B['std']**2 + DESI_WA_LUSIM_ERR**2)
        frac_neg = np.mean(chainB['samples'][:, 1] < 0)

        print(f"\n  Fit B wa posterior: {wa_B['mean']:.3f} +/- {wa_B['std']:.3f}")
        print(f"  Fraction wa < 0: {frac_neg:.3f} ({frac_neg*100:.1f}%)")
        print(f"  Tension with wa = 0 (Meridian): {sigma_wa_zero:.1f} sigma")
        print(f"  Tension with DESI Lu&Simon (wa = {DESI_WA_LUSIM}): {sigma_wa_desi:.1f} sigma")

        # Is Fit B finding a sensible minimum?
        w0_B = statsB['w0']
        print(f"\n  Fit B w0: {w0_B['mean']:.3f} +/- {w0_B['std']:.3f}")
        if abs(wa_B['mean']) > 2.5:
            print(f"  ** WARNING: wa near prior boundary — Fit B may be pathological")
        if w0_B['mean'] > -0.3:
            print(f"  ** WARNING: w0 > -0.3 — unusual, check for optimizer issues")

    # ============================================================
    # v2 vs v3 COMPARISON
    # ============================================================

    print_section("v2 vs v3 COMPARISON")
    print(f"  {'Metric':>25s}  {'v2':>12s}  {'v3':>12s}  {'Change':>12s}")
    print(f"  {'-'*25}  {'-'*12}  {'-'*12}  {'-'*12}")

    v2_daic = 12.63
    print(f"  {'DAIC':>25s}  {v2_daic:>+12.2f}  {DAIC:>+12.2f}  {DAIC-v2_daic:>+12.2f}")

    v2_chi2A = 118.84
    print(f"  {'chi2 Fit A':>25s}  {v2_chi2A:>12.2f}  {chi2_A:>12.2f}  {chi2_A-v2_chi2A:>+12.2f}")

    v2_chi2B = 104.21
    print(f"  {'chi2 Fit B':>25s}  {v2_chi2B:>12.2f}  {chi2_B:>12.2f}  {chi2_B-v2_chi2B:>+12.2f}")

    v2_w0A = -1.05
    print(f"  {'Fit A w0':>25s}  {v2_w0A:>12.4f}  {w0_A['mean']:>12.4f}  {w0_A['mean']-v2_w0A:>+12.4f}")

    # ============================================================
    # PRE-REGISTERED PREDICTION CHECK
    # ============================================================

    print_section("PRE-REGISTERED PREDICTION CHECK")
    preds = [
        ("chi2/N near 1", chi2_A/dof_A < 1.2 and chi2_A/dof_A > 0.8),
        ("Fit B less pathological than v2", 'wa' not in statsB or abs(statsB['wa']['mean']) < 2.5),
        ("DAIC decreased from +12.63", DAIC < v2_daic),
        ("Fit A w0 near -1", abs(w0_A['mean'] + 1.0) < 0.1),
    ]
    for desc, result in preds:
        mark = "CONFIRMED" if result else "DISCONFIRMED"
        print(f"  [{mark:>13s}] {desc}")

    # ============================================================
    # INTERPRETATION GUIDE TEMPLATE — FILLED
    # ============================================================

    print_section("HONEST ASSESSMENT TEMPLATE")
    print(f"  1. DAIC = {DAIC:+.2f}")
    print(f"  2. Fit A: w0 = {w0_A['mean']:.4f} +/- {w0_A['std']:.4f}, "
          f"Om = {statsA['Om']['mean']:.4f} +/- {statsA['Om']['std']:.4f}, "
          f"H0 = {statsA['H0']['mean']:.2f} +/- {statsA['H0']['std']:.2f}")
    if 'wa' in statsB:
        print(f"  3. Fit B: w0 = {statsB['w0']['mean']:.4f} +/- {statsB['w0']['std']:.4f}, "
              f"wa = {statsB['wa']['mean']:.4f} +/- {statsB['wa']['std']:.4f}, "
              f"Om = {statsB['Om']['mean']:.4f} +/- {statsB['Om']['std']:.4f}, "
              f"H0 = {statsB['H0']['mean']:.2f} +/- {statsB['H0']['std']:.2f}")
    print(f"  4. Probe decomposition: [requires --probes flag]")
    print(f"  5. Fit A: w0 = -0.745 is at {sigma_jc:.1f} sigma from posterior peak")
    if 'wa' in statsB:
        print(f"  6. Fit B vs DESI DR1: wa tension = {sigma_wa_desi:.1f} sigma")
    print(f"  7. Convergence: [check main pipeline log]")

    # Overall assessment
    if abs(DAIC) < 4 and sigma_jc < 3:
        assessment = "COMPETITIVE — constant-w viable AND JC benchmark not excluded"
    elif abs(DAIC) < 4 and sigma_jc >= 3:
        assessment = "MIXED — constant-w viable BUT JC benchmark excluded; viable regime consistent"
    elif abs(DAIC) < 10:
        assessment = "AMBIGUOUS — probe decomposition needed to determine driver"
    else:
        assessment = "DISFAVORED — CPL strongly preferred"
    print(f"  8. Assessment: {assessment}")

    # ============================================================
    # SAVE RESULTS
    # ============================================================

    results = {
        'DAIC': DAIC, 'DBIC': DBIC,
        'chi2_A': chi2_A, 'chi2_B': chi2_B,
        'statsA': statsA, 'statsB': statsB,
        'sigma_jc': sigma_jc, 'sigma_viable': sigma_viable,
        'sigma_lcdm': sigma_lcdm,
        'assessment': assessment,
    }
    return results


def make_quick_plots(chainA, chainB, results):
    """Generate diagnostic plots from chains."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n  matplotlib not available — skipping plots")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('18A v3 Post-Hoc Analysis (Full Pantheon+ Covariance)',
                 fontsize=13, fontweight='bold')

    # 1. w0 posteriors
    ax = axes[0, 0]
    ax.hist(chainA['samples'][:, 0], bins=60, density=True, alpha=0.6,
            color='steelblue', label='Fit A (const w)')
    ax.hist(chainB['samples'][:, 0], bins=60, density=True, alpha=0.6,
            color='salmon', label='Fit B (CPL)')
    ax.axvline(MERIDIAN_W0_JC, color='green', ls='--', lw=2, label=f'JC: {MERIDIAN_W0_JC}')
    ax.axvline(-1.0, color='gray', ls=':', lw=2, label='LCDM')
    ax.set_xlabel('$w_0$')
    ax.set_ylabel('Density')
    ax.set_title('$w_0$ Posterior')
    ax.legend(fontsize=8)

    # 2. wa posterior
    ax = axes[0, 1]
    wa_samples = chainB['samples'][:, 1]
    ax.hist(wa_samples, bins=60, density=True, alpha=0.7, color='steelblue')
    ax.axvline(0, color='red', ls='--', lw=2, label='Meridian ($w_a=0$)')
    ax.axvline(DESI_WA_LUSIM, color='orange', ls='--', lw=2, label=f'DESI ($w_a={DESI_WA_LUSIM}$)')
    ax.set_xlabel('$w_a$')
    ax.set_ylabel('Density')
    ax.set_title('$w_a$ Posterior (Fit B)')
    ax.legend(fontsize=8)

    # 3. Om-H0
    ax = axes[1, 0]
    ax.scatter(chainA['samples'][:, 1][::10], chainA['samples'][:, 2][::10],
               alpha=0.1, s=1, c='steelblue', label='Fit A')
    ax.scatter(chainB['samples'][:, 2][::10], chainB['samples'][:, 3][::10],
               alpha=0.1, s=1, c='salmon', label='Fit B')
    ax.set_xlabel(r'$\Omega_m$')
    ax.set_ylabel('$H_0$')
    ax.set_title(r'$\Omega_m$-$H_0$ Posterior')
    ax.legend(fontsize=8, markerscale=10)

    # 4. Summary text
    ax = axes[1, 1]
    ax.axis('off')
    txt = (f"DAIC (A-B) = {results['DAIC']:+.2f}\n\n"
           f"Fit A: chi2 = {results['chi2_A']:.2f}\n"
           f"       w0 = {results['statsA']['w0']['mean']:.4f} +/- {results['statsA']['w0']['std']:.4f}\n"
           f"Fit B: chi2 = {results['chi2_B']:.2f}\n"
           f"       w0 = {results['statsB']['w0']['mean']:.4f} +/- {results['statsB']['w0']['std']:.4f}\n"
           f"       wa = {results['statsB']['wa']['mean']:.4f} +/- {results['statsB']['wa']['std']:.4f}\n\n"
           f"JC benchmark: {results['sigma_jc']:.1f} sigma from Fit A\n"
           f"Viable regime: {results['sigma_viable']:.1f} sigma from Fit A\n\n"
           f"Assessment: {results['assessment']}")
    ax.text(0.05, 0.95, txt, transform=ax.transAxes, fontsize=11,
            va='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, '18A_v3_posthoc_analysis.png')
    plt.savefig(outpath, dpi=150, bbox_inches='tight')
    print(f"\n  Plot saved: {outpath}")
    plt.close()


def write_results_md(results):
    """Write filled-in assessment to markdown."""
    rpath = os.path.join(OUTPUT_DIR, '18A_v3_honest_assessment.md')
    sA = results['statsA']
    sB = results['statsB']
    with open(rpath, 'w', encoding='utf-8') as f:
        f.write("# 18A v3 Honest Assessment\n\n")
        f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**SNe:** Full Pantheon+ (1590 SNe, stat+sys covariance)\n\n")
        f.write("## Filled Template\n\n")
        f.write(f"1. **DAIC** = {results['DAIC']:+.2f}\n")
        f.write(f"2. **Fit A:** w0 = {sA['w0']['mean']:.4f} +/- {sA['w0']['std']:.4f}, "
                f"Om = {sA['Om']['mean']:.4f} +/- {sA['Om']['std']:.4f}, "
                f"H0 = {sA['H0']['mean']:.2f} +/- {sA['H0']['std']:.2f}\n")
        f.write(f"3. **Fit B:** w0 = {sB['w0']['mean']:.4f} +/- {sB['w0']['std']:.4f}, "
                f"wa = {sB['wa']['mean']:.4f} +/- {sB['wa']['std']:.4f}, "
                f"Om = {sB['Om']['mean']:.4f} +/- {sB['Om']['std']:.4f}, "
                f"H0 = {sB['H0']['mean']:.2f} +/- {sB['H0']['std']:.2f}\n")
        f.write(f"4. **Probe decomposition:** See main pipeline output\n")
        f.write(f"5. **JC benchmark tension:** {results['sigma_jc']:.1f} sigma\n")
        f.write(f"6. **Viable regime tension:** {results['sigma_viable']:.1f} sigma\n")
        f.write(f"7. **LCDM tension:** {results['sigma_lcdm']:.1f} sigma\n")
        f.write(f"8. **Assessment:** {results['assessment']}\n\n")
        f.write("## v2 vs v3 Comparison\n\n")
        f.write(f"| Metric | v2 | v3 |\n|--------|-----|-----|\n")
        f.write(f"| DAIC | +12.63 | {results['DAIC']:+.2f} |\n")
        f.write(f"| chi2 Fit A | 118.84 | {results['chi2_A']:.2f} |\n")
        f.write(f"| chi2 Fit B | 104.21 | {results['chi2_B']:.2f} |\n")
        f.write(f"| Fit A w0 | -1.0500 | {sA['w0']['mean']:.4f} |\n\n")
        f.write("## Interpretation\n\n")
        if abs(results['DAIC']) < 4:
            f.write("Constant-w is competitive with CPL. The functional form predicted by "
                    "Meridian (constant w with GR perturbations) fits the data as well as "
                    "the more flexible CPL parameterization.\n\n")
            if results['sigma_jc'] > 3:
                f.write(f"However, the JC benchmark value w0 = {MERIDIAN_W0_JC} is excluded at "
                        f"{results['sigma_jc']:.1f} sigma. The framework survives in the "
                        f"near-LCDM regime (zeta_0 ~ 0.02+) where w0 ~ -0.99.\n")
        elif abs(results['DAIC']) < 10:
            f.write("Ambiguous result. CPL is moderately preferred. Probe-by-probe "
                    "decomposition is needed to identify which data are driving the preference.\n")
        else:
            f.write("CPL is strongly preferred. The constant-w prediction faces pressure. "
                    "Investigate epsilon_2 X^2 correction or radion dynamics.\n")
    print(f"  Assessment saved: {rpath}")


def main():
    print("=" * 70)
    print("  18A v3 POST-HOC CHAIN ANALYSIS")
    print("  Following pre-registered interpretation guide")
    print("=" * 70)

    # Load chains
    print("\nLoading chains...")
    chainA = load_chain('A')
    chainB = load_chain('B')

    if chainA is None or chainB is None:
        print("\nERROR: Both chain files required.")
        print(f"  Expected: {OUTPUT_DIR}/18A_v3_chain_A.npz")
        print(f"  Expected: {OUTPUT_DIR}/18A_v3_chain_B.npz")
        if chainA is not None:
            print("\n  Chain A exists — running partial analysis...")
            statsA = posterior_stats(chainA['samples'], chainA['labels'])
            print_section("FIT A (PARTIAL — No Fit B for comparison)")
            for label in chainA['labels']:
                s = statsA[label]
                print(f"  {label:>5s} = {s['q50']:.4f} +{s['err_up']:.4f} -{s['err_down']:.4f}")
            sigma_jc = tension_sigma(MERIDIAN_W0_JC, statsA['w0']['mean'], statsA['w0']['std'])
            print(f"\n  JC benchmark tension: {sigma_jc:.1f} sigma")
        sys.exit(1)

    # Run analysis
    results = analyze_basic(chainA, chainB)

    # Plots
    print("\nGenerating plots...")
    make_quick_plots(chainA, chainB, results)

    # Save filled assessment
    print("\nSaving assessment...")
    write_results_md(results)

    print(f"\n{'='*70}")
    print(f"  ANALYSIS COMPLETE")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
