#!/usr/bin/env python3
"""
Cellular Automata — Information-Theoretic Analysis
====================================================
Tests whether computational mechanics measures (statistical complexity,
entropy rate, excess entropy) can distinguish Wolfram complexity classes
where spectral analysis failed.

The spectral analysis (ca_comparative.py) found that Rules 30, 90, and 110
are spectrally near-identical despite spanning chaos, fractal, and universal
computation. Only Rule 184 (ordered) was distinguishable.

Hypothesis: Statistical complexity C_μ (causal state entropy) will separate
Rule 110 from Rule 30, because universality requires causal memory that
pure chaos does not.

Method: Block entropy analysis on CA spacetime columns (temporal sequences).
- h(L): block entropy at block length L
- h_μ ≈ h(L) - h(L-1): entropy rate (converges as L grows)
- E ≈ Σ [h(L) - h(L-1) - h_μ]: excess entropy (total structure)
- C_μ estimated via ε-machine reconstruction (or block entropy bounds)
- LZ76 compression ratio as Kolmogorov complexity proxy

Author: Clawd Iggulden-Schnell
Date: 2026-03-21
"""

import subprocess
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter
import zlib
import os

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
WOLFRAM = r"C:\Program Files\Wolfram Research\Wolfram Engine\14.3\wolframscript.exe"

RULES = [
    {'rule': 30,  'name': 'Rule 30',  'class': 'III — Chaotic',    'color': '#e74c3c'},
    {'rule': 90,  'name': 'Rule 90',  'class': 'II — Periodic',    'color': '#3498db'},
    {'rule': 110, 'name': 'Rule 110', 'class': 'IV — Complex',     'color': '#2ecc71'},
    {'rule': 184, 'name': 'Rule 184', 'class': 'II — Ordered',     'color': '#f39c12'},
]

# Larger grid for better statistics
STEPS = 500
WIDTH = 501


def generate_ca(rule_num, steps=STEPS, width=WIDTH):
    """Generate cellular automaton using Wolfram Engine."""
    print(f"  Wolfram: Rule {rule_num} ({steps}x{width})...", flush=True)
    code = f'ExportString[CellularAutomaton[{rule_num}, {{{{1}}, 0}}, {steps}], "JSON"]'
    result = subprocess.run(
        [WOLFRAM, '-code', code],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"Wolfram error: {result.stderr}")
    grid = np.array(json.loads(result.stdout))
    print(f"    Grid shape: {grid.shape}, density: {100*grid.mean():.1f}%", flush=True)
    return grid


def block_entropy(sequence, L):
    """Compute block entropy H(L) for binary sequence at block length L.

    H(L) = -Σ p(block) log2(p(block))
    where the sum is over all observed blocks of length L.
    """
    n = len(sequence)
    if n < L:
        return 0.0

    # Extract all blocks of length L
    blocks = []
    for i in range(n - L + 1):
        blocks.append(tuple(sequence[i:i+L]))

    counts = Counter(blocks)
    total = len(blocks)

    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * np.log2(p)

    return entropy


def compute_entropy_curve(grid, max_L=12, n_columns=100):
    """Compute block entropy growth curve from CA spacetime.

    Samples temporal columns (vertical slices) and averages their
    block entropies across multiple spatial positions.

    Returns: L_values, H_L (average block entropy at each L)
    """
    rows, cols = grid.shape

    # Sample columns from the active region (center of the CA)
    center = cols // 2
    # Use columns from the active region, skip edges
    col_indices = np.linspace(
        max(0, center - cols // 4),
        min(cols - 1, center + cols // 4),
        n_columns, dtype=int
    )

    L_values = list(range(1, max_L + 1))
    H_L = np.zeros(len(L_values))

    for col_idx in col_indices:
        column = grid[:, col_idx]
        for i, L in enumerate(L_values):
            H_L[i] += block_entropy(column, L)

    H_L /= n_columns
    return L_values, H_L


def estimate_entropy_rate(H_L):
    """Estimate entropy rate h_μ from block entropy curve.

    h_μ = lim_{L→∞} [H(L) - H(L-1)]
    Use the last few values for the estimate.
    """
    diffs = np.diff(H_L)
    # Average over last 3 differences for stability
    if len(diffs) >= 3:
        return np.mean(diffs[-3:])
    return diffs[-1] if len(diffs) > 0 else 0.0


def estimate_excess_entropy(L_values, H_L, h_mu):
    """Estimate excess entropy E from block entropy curve.

    E = lim_{L→∞} [H(L) - L * h_μ]
    This measures total predictive structure — mutual information
    between the past and future of the process.
    """
    L_arr = np.array(L_values)
    # E ≈ H(L) - L * h_μ for large L
    E_estimates = H_L - L_arr * h_mu
    # Should converge; use last few values
    if len(E_estimates) >= 3:
        return np.mean(E_estimates[-3:])
    return E_estimates[-1]


def estimate_statistical_complexity_bound(L_values, H_L, h_mu):
    """Estimate a bound on statistical complexity C_μ.

    C_μ is the entropy of the causal states (ε-machine states).

    Upper bound: C_μ ≤ H(L) - (L-1) * h_μ  for any L
    (This is the entropy of length-L pasts modulo the entropy rate.)

    Also compute the "predictive information rate" — how quickly
    new information about block structure appears.
    """
    L_arr = np.array(L_values)

    # Upper bound on C_μ at each L
    bounds = H_L - (L_arr - 1) * h_mu

    # The tightest bound is the minimum over L ≥ some threshold
    # (for very small L, the bound is loose)
    if len(bounds) >= 4:
        return np.min(bounds[3:])  # Skip L=1,2,3 (too loose)
    return np.min(bounds)


def compression_ratio(grid):
    """Compression ratio via zlib as Kolmogorov complexity proxy.

    Higher ratio = more compressible = more regular.
    """
    raw = grid.tobytes()
    compressed = zlib.compress(raw, level=9)
    return len(compressed) / len(raw)


def mutual_information_spatial(grid, lag=1):
    """Mutual information between spatial neighbors.

    I(X_i; X_{i+lag}) averaged over the grid.
    Measures spatial correlation structure.
    """
    rows, cols = grid.shape
    total_mi = 0.0
    count = 0

    for row in grid:
        # Joint distribution of (X_i, X_{i+lag})
        pairs = []
        for i in range(cols - lag):
            pairs.append((int(row[i]), int(row[i + lag])))

        joint_counts = Counter(pairs)
        total_pairs = len(pairs)

        # Marginals
        x_counts = Counter(int(row[i]) for i in range(cols - lag))
        y_counts = Counter(int(row[i + lag]) for i in range(cols - lag))

        mi = 0.0
        for (x, y), jc in joint_counts.items():
            p_xy = jc / total_pairs
            p_x = x_counts[x] / total_pairs
            p_y = y_counts[y] / total_pairs
            if p_xy > 0 and p_x > 0 and p_y > 0:
                mi += p_xy * np.log2(p_xy / (p_x * p_y))

        total_mi += mi
        count += 1

    return total_mi / count


def transient_length(grid):
    """Estimate transient length by finding when temporal column
    distributions stabilize (for rules that settle).

    Uses sliding window KL divergence on column statistics.
    """
    rows, cols = grid.shape
    center_col = grid[:, cols // 2]

    window = 20
    densities = []
    for i in range(0, rows - window, window):
        densities.append(np.mean(center_col[i:i+window]))

    if len(densities) < 3:
        return 0

    # Find when density stabilizes (variance of recent windows < threshold)
    diffs = np.abs(np.diff(densities))
    for i in range(len(diffs)):
        if all(d < 0.02 for d in diffs[i:min(i+3, len(diffs))]):
            return i * window

    return rows  # Never stabilized


def plot_entropy_curves(all_results):
    """Plot block entropy growth curves for all rules."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Block Entropy Growth — Causal Architecture Fingerprints',
                 fontsize=16, fontweight='bold', color='white', y=0.98)
    fig.patch.set_facecolor('#0a0a0a')

    for idx, (rule, results) in enumerate(zip(RULES, all_results)):
        ax = axes[idx // 2][idx % 2]
        ax.set_facecolor('#0a0a0a')

        L = results['L_values']
        H = results['H_L']
        h_mu = results['entropy_rate']

        # Actual entropy curve
        ax.plot(L, H, 'o-', color=rule['color'], linewidth=2, markersize=6,
                label=f"H(L)")

        # Linear extrapolation (h_μ * L + E)
        E = results['excess_entropy']
        linear = np.array(L) * h_mu + E
        ax.plot(L, linear, '--', color='#888', linewidth=1,
                label=f'h_μ·L + E (h_μ={h_mu:.3f})')

        ax.set_xlabel('Block length L', color='#aaa')
        ax.set_ylabel('H(L) [bits]', color='#aaa')
        ax.set_title(f"{rule['name']} — {rule['class']}", color=rule['color'],
                     fontweight='bold', fontsize=12)
        ax.legend(fontsize=9, facecolor='#1a1a1a', edgecolor='#333', labelcolor='#ccc')
        ax.tick_params(colors='#888')
        ax.grid(color='#222', linewidth=0.5)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(AUDIO_DIR, 'ca_entropy_curves.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


def plot_information_landscape(all_results):
    """Plot rules in the (entropy rate, statistical complexity) plane.

    This is the key visualization: Crutchfield's 'complexity-entropy'
    diagram. Random processes are top-left (high h, low C). Ordered
    processes are bottom-left (low h, low C). Complex processes should
    be in the middle-right (moderate h, high C).
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    for rule, results in zip(RULES, all_results):
        h = results['entropy_rate']
        C = results['complexity_bound']
        E = results['excess_entropy']

        # Size proportional to excess entropy
        size = max(100, abs(E) * 500)

        ax.scatter(h, C, s=size, c=rule['color'], edgecolors='white',
                   linewidth=1.5, zorder=5, alpha=0.9)
        ax.annotate(f"{rule['name']}\n{rule['class']}",
                    (h, C), textcoords="offset points", xytext=(12, 8),
                    fontsize=10, color=rule['color'], fontweight='bold')

    ax.set_xlabel('Entropy Rate h_μ [bits/step]', fontsize=12, color='#ccc')
    ax.set_ylabel('Statistical Complexity Bound C_μ [bits]', fontsize=12, color='#ccc')
    ax.set_title('Causal Architecture: Entropy Rate vs Statistical Complexity',
                 fontsize=14, color='white', fontweight='bold', pad=15)
    ax.tick_params(colors='#888')
    ax.grid(color='#222', linewidth=0.5)

    # Add quadrant labels
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xmid = (xlim[0] + xlim[1]) / 2
    ymid = (ylim[0] + ylim[1]) / 2

    ax.text(xlim[0] + 0.02, ylim[1] - 0.1, 'COMPLEX\n(high memory, low randomness)',
            color='#444', fontsize=9, fontstyle='italic', va='top')
    ax.text(xlim[1] - 0.02, ylim[1] - 0.1, 'CHAOTIC-COMPLEX\n(high memory, high randomness)',
            color='#444', fontsize=9, fontstyle='italic', va='top', ha='right')
    ax.text(xlim[0] + 0.02, ylim[0] + 0.05, 'ORDERED\n(low memory, low randomness)',
            color='#444', fontsize=9, fontstyle='italic')
    ax.text(xlim[1] - 0.02, ylim[0] + 0.05, 'RANDOM\n(low memory, high randomness)',
            color='#444', fontsize=9, fontstyle='italic', ha='right')

    out = os.path.join(AUDIO_DIR, 'ca_information_landscape.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


def plot_summary_comparison(all_results):
    """Bar chart comparing all information-theoretic measures."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Information-Theoretic Fingerprints — Wolfram Complexity Classes',
                 fontsize=16, fontweight='bold', color='white', y=0.98)
    fig.patch.set_facecolor('#0a0a0a')

    measures = [
        ('entropy_rate', 'Entropy Rate h_μ\n[bits/step]'),
        ('excess_entropy', 'Excess Entropy E\n[bits]'),
        ('complexity_bound', 'Complexity Bound C_μ\n[bits]'),
        ('compression_ratio', 'Compression Ratio\n(lower = more structure)'),
        ('spatial_mi', 'Spatial Mutual Info\n[bits]'),
        ('transient', 'Transient Length\n[steps]'),
    ]

    for idx, (key, title) in enumerate(measures):
        ax = axes[idx // 3][idx % 3]
        ax.set_facecolor('#0a0a0a')

        names = [r['name'] for r in RULES]
        values = [r[key] for r in all_results]
        colors = [r['color'] for r in RULES]

        bars = ax.bar(names, values, color=colors, alpha=0.85, edgecolor='white', linewidth=0.5)
        ax.set_title(title, fontsize=11, color='#ccc', fontweight='bold')
        ax.tick_params(colors='#888')
        ax.grid(axis='y', color='#222', linewidth=0.5)

        # Annotate values
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=9, color='#ccc')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(AUDIO_DIR, 'ca_info_summary.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


def main():
    print("=" * 70)
    print("CELLULAR AUTOMATA — INFORMATION-THEORETIC ANALYSIS")
    print("Can computational mechanics see what spectral analysis cannot?")
    print("=" * 70, flush=True)

    # === PREDICTIONS (logged before testing) ===
    print("\n[PREDICTIONS — logged before running]", flush=True)
    print("  P1 (medium-high): C_mu distinguishes Rule 110 from Rule 30", flush=True)
    print("  P2 (medium): Rule 30 has highest entropy rate", flush=True)
    print("  P3 (high): Rule 184 has lowest entropy rate AND lowest C_mu", flush=True)
    print("  P4 (medium): Excess entropy E is highest for Rule 110", flush=True)
    print("  P5 (low): Compression ratio separates all four classes", flush=True)

    # Step 1: Generate CAs
    print("\n[1] Generating cellular automata...", flush=True)
    grids = {}
    for rule in RULES:
        grids[rule['rule']] = generate_ca(rule['rule'])

    # Step 2: Information-theoretic analysis
    print("\n[2] Computing information-theoretic measures...", flush=True)
    max_L = 12
    all_results = []

    for rule in RULES:
        print(f"\n  --- {rule['name']} ({rule['class']}) ---", flush=True)
        grid = grids[rule['rule']]

        # Block entropy curve
        print(f"    Computing block entropies (L=1..{max_L})...", flush=True)
        L_values, H_L = compute_entropy_curve(grid, max_L=max_L, n_columns=150)

        # Derived measures
        h_mu = estimate_entropy_rate(H_L)
        E = estimate_excess_entropy(L_values, H_L, h_mu)
        C_bound = estimate_statistical_complexity_bound(L_values, H_L, h_mu)

        # Compression
        cr = compression_ratio(grid)

        # Spatial mutual information
        mi = mutual_information_spatial(grid, lag=1)

        # Transient
        trans = transient_length(grid)

        results = {
            'L_values': L_values,
            'H_L': H_L,
            'entropy_rate': h_mu,
            'excess_entropy': E,
            'complexity_bound': C_bound,
            'compression_ratio': cr,
            'spatial_mi': mi,
            'transient': trans,
        }
        all_results.append(results)

        print(f"    Entropy rate h_μ:      {h_mu:.4f} bits/step", flush=True)
        print(f"    Excess entropy E:      {E:.4f} bits", flush=True)
        print(f"    Complexity bound C_μ:  {C_bound:.4f} bits", flush=True)
        print(f"    Compression ratio:     {cr:.4f}", flush=True)
        print(f"    Spatial MI (lag=1):    {mi:.4f} bits", flush=True)
        print(f"    Transient length:      {trans} steps", flush=True)

    # Step 3: Visualize
    print("\n[3] Generating visualizations...", flush=True)
    plot_entropy_curves(all_results)
    plot_information_landscape(all_results)
    plot_summary_comparison(all_results)

    # Step 4: Evaluate predictions
    print(f"\n{'='*70}")
    print("PREDICTION EVALUATION")
    print(f"{'='*70}", flush=True)

    names = [r['name'] for r in RULES]
    h_rates = [r['entropy_rate'] for r in all_results]
    C_bounds = [r['complexity_bound'] for r in all_results]
    E_vals = [r['excess_entropy'] for r in all_results]
    comp_ratios = [r['compression_ratio'] for r in all_results]

    # P1: C_μ distinguishes 110 from 30
    c110 = C_bounds[2]  # Rule 110 is index 2
    c30 = C_bounds[0]   # Rule 30 is index 0
    sep = abs(c110 - c30) / max(abs(c110), abs(c30), 1e-10)
    print(f"\n  P1: C_μ distinguishes Rule 110 ({c110:.4f}) from Rule 30 ({c30:.4f})")
    print(f"      Separation: {sep*100:.1f}%")
    print(f"      Verdict: {'CONFIRMED' if sep > 0.15 else 'PARTIALLY CONFIRMED' if sep > 0.05 else 'FALSIFIED'}")

    # P2: Rule 30 has highest entropy rate
    max_h_idx = np.argmax(h_rates)
    print(f"\n  P2: Rule 30 has highest h_μ?")
    print(f"      Actual highest: {names[max_h_idx]} (h_μ = {h_rates[max_h_idx]:.4f})")
    print(f"      Verdict: {'CONFIRMED' if max_h_idx == 0 else 'FALSIFIED'}")

    # P3: Rule 184 lowest h_μ AND C_μ
    min_h_idx = np.argmin(h_rates)
    min_c_idx = np.argmin(C_bounds)
    print(f"\n  P3: Rule 184 has lowest h_μ AND C_μ?")
    print(f"      Lowest h_μ: {names[min_h_idx]} ({h_rates[min_h_idx]:.4f})")
    print(f"      Lowest C_μ: {names[min_c_idx]} ({C_bounds[min_c_idx]:.4f})")
    p3 = min_h_idx == 3 and min_c_idx == 3
    print(f"      Verdict: {'CONFIRMED' if p3 else 'PARTIALLY' if (min_h_idx==3 or min_c_idx==3) else 'FALSIFIED'}")

    # P4: E highest for Rule 110
    max_E_idx = np.argmax(E_vals)
    print(f"\n  P4: Excess entropy E highest for Rule 110?")
    print(f"      Actual highest: {names[max_E_idx]} (E = {E_vals[max_E_idx]:.4f})")
    print(f"      Verdict: {'CONFIRMED' if max_E_idx == 2 else 'FALSIFIED'}")

    # P5: Compression separates all four
    sorted_comp = sorted(zip(comp_ratios, names))
    print(f"\n  P5: Compression ratio separates all four?")
    for cr, name in sorted_comp:
        print(f"      {name}: {cr:.4f}")
    gaps = [sorted_comp[i+1][0] - sorted_comp[i][0] for i in range(len(sorted_comp)-1)]
    all_separated = all(g > 0.01 for g in gaps)
    print(f"      Gaps: {[f'{g:.4f}' for g in gaps]}")
    print(f"      Verdict: {'CONFIRMED' if all_separated else 'FALSIFIED'}")

    # Overall
    print(f"\n{'='*70}")
    print("KEY FINDING")
    print(f"{'='*70}", flush=True)

    # Can information theory see what spectral analysis cannot?
    # Compare the distances in info-theoretic space
    info_features = np.array([[r['entropy_rate'], r['complexity_bound'],
                                r['excess_entropy'], r['compression_ratio']]
                               for r in all_results])
    # Normalize
    mins = info_features.min(axis=0)
    maxs = info_features.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1
    normed = (info_features - mins) / ranges

    from scipy.spatial.distance import pdist, squareform
    dist = squareform(pdist(normed))

    d_30_110 = dist[0, 2]
    d_90_110 = dist[1, 2]
    d_184_110 = dist[3, 2]
    d_30_90 = dist[0, 1]

    print(f"  Information-theoretic distances:")
    print(f"    Rule 30  <-> Rule 110: {d_30_110:.3f}")
    print(f"    Rule 90  <-> Rule 110: {d_90_110:.3f}")
    print(f"    Rule 184 <-> Rule 110: {d_184_110:.3f}")
    print(f"    Rule 30  <-> Rule 90:  {d_30_90:.3f}")

    # In spectral space, 30/90/110 were clustered. Are they separated here?
    spectral_cluster_separated = d_30_110 > 0.2 and d_90_110 > 0.2
    print(f"\n  Spectral cluster (30/90/110) separated in info space: "
          f"{'YES' if spectral_cluster_separated else 'NO'}")

    if spectral_cluster_separated:
        print("  → Information theory SEES what spectral analysis CANNOT.")
        print("    Computational universality has a causal signature, not a spectral one.")
    else:
        print("  → Information theory ALSO cannot fully separate computational classes.")
        print("    The invisibility of universality may be deeper than the measurement tool.")

    print(f"\n{'='*70}", flush=True)


if __name__ == '__main__':
    main()
