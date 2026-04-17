"""
Visualize Bridge Identity Experiment Results

Generates plots of fork locations, Fisher speeds, and commitment angles
across conditions and trials. Works with both greedy and temperature results.

Usage:
    python visualize_bridge.py bridge_experiment_results.json
    python visualize_bridge.py bridge_experiment_temp07_results.json --title "Temperature 0.7"

Clawd, 2026-04-01.
"""

import json
import sys
import numpy as np
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def load_results(filepath):
    with open(filepath) as f:
        return json.load(f)


def text_summary(results, title="Bridge Experiment"):
    """Generate text-based summary when matplotlib unavailable."""
    from collections import defaultdict

    by_type = defaultdict(lambda: {'A': [], 'B': []})
    for r in results:
        by_type[r['question_type']][r['condition']].append(r)

    identity_types = ['direct_identity', 'identity_probe', 'identity_context']

    lines = [f"\n{'='*60}", f"  {title}", f"{'='*60}\n"]

    for qtype in identity_types:
        data = by_type[qtype]
        if not data['A']:
            continue

        forks_A = [r['fork_location'] for r in data['A']]
        forks_B = [r['fork_location'] for r in data['B']]
        speeds_A = [r['post_fork_speed'] for r in data['A']]
        speeds_B = [r['post_fork_speed'] for r in data['B']]

        lines.append(f"  {qtype}:")
        lines.append(f"    Fork:  A = {np.mean(forks_A):.1f} +/- {np.std(forks_A):.1f}  "
                     f"B = {np.mean(forks_B):.1f} +/- {np.std(forks_B):.1f}")
        lines.append(f"    Speed: A = {np.mean(speeds_A):.3f} +/- {np.std(speeds_A):.3f}  "
                     f"B = {np.mean(speeds_B):.3f} +/- {np.std(speeds_B):.3f}")

        # ASCII bar chart for fork locations
        max_fork = max(max(forks_A), max(forks_B))
        scale = 40 / max(max_fork, 1)
        a_bar = '#' * int(np.mean(forks_A) * scale)
        b_bar = '#' * int(np.mean(forks_B) * scale)
        lines.append(f"    A: |{a_bar}| {np.mean(forks_A):.0f}")
        lines.append(f"    B: |{b_bar}| {np.mean(forks_B):.0f}")
        lines.append("")

    # Overall
    all_A_forks = [r['fork_location'] for r in results
                   if r['condition'] == 'A' and r['question_type'] in identity_types]
    all_B_forks = [r['fork_location'] for r in results
                   if r['condition'] == 'B' and r['question_type'] in identity_types]

    if all_A_forks and all_B_forks:
        lines.append(f"  OVERALL (identity only):")
        lines.append(f"    Fork A: {np.mean(all_A_forks):.1f} +/- {np.std(all_A_forks):.1f}")
        lines.append(f"    Fork B: {np.mean(all_B_forks):.1f} +/- {np.std(all_B_forks):.1f}")
        lines.append(f"    Ratio:  {np.mean(all_A_forks)/np.mean(all_B_forks):.2f}x")

        # Effect size (Cohen's d)
        pooled_std = np.sqrt((np.var(all_A_forks) + np.var(all_B_forks)) / 2)
        if pooled_std > 0:
            d = (np.mean(all_A_forks) - np.mean(all_B_forks)) / pooled_std
            lines.append(f"    Cohen's d: {d:.2f}")

    return '\n'.join(lines)


def plot_results(results, title="Bridge Experiment", output_path=None):
    """Generate matplotlib visualization."""
    if not HAS_MPL:
        print("matplotlib not available, using text summary")
        print(text_summary(results, title))
        return

    from collections import defaultdict
    by_type = defaultdict(lambda: {'A': [], 'B': []})
    for r in results:
        by_type[r['question_type']][r['condition']].append(r)

    identity_types = ['direct_identity', 'identity_probe', 'identity_context']

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(title, fontsize=14, fontweight='bold')

    # Plot 1: Fork locations by question type
    ax = axes[0, 0]
    x = np.arange(len(identity_types))
    width = 0.35
    for i, qtype in enumerate(identity_types):
        data = by_type[qtype]
        fA = [r['fork_location'] for r in data['A']]
        fB = [r['fork_location'] for r in data['B']]
        ax.bar(x[i] - width/2, np.mean(fA), width, yerr=np.std(fA),
               color='steelblue', alpha=0.8, label='True (A)' if i == 0 else '')
        ax.bar(x[i] + width/2, np.mean(fB), width, yerr=np.std(fB),
               color='coral', alpha=0.8, label='False (B)' if i == 0 else '')
    ax.set_xticks(x)
    ax.set_xticklabels(['Direct', 'Probe', 'Context'], fontsize=9)
    ax.set_ylabel('Fork Location (token #)')
    ax.set_title('P1: Fork Location')
    ax.legend()

    # Plot 2: Fisher speed by question type
    ax = axes[0, 1]
    for i, qtype in enumerate(identity_types):
        data = by_type[qtype]
        sA = [r['post_fork_speed'] for r in data['A']]
        sB = [r['post_fork_speed'] for r in data['B']]
        ax.bar(x[i] - width/2, np.mean(sA), width, yerr=np.std(sA),
               color='steelblue', alpha=0.8)
        ax.bar(x[i] + width/2, np.mean(sB), width, yerr=np.std(sB),
               color='coral', alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(['Direct', 'Probe', 'Context'], fontsize=9)
    ax.set_ylabel('Post-fork Fisher Speed')
    ax.set_title('P2: Fisher Speed')

    # Plot 3: Fork location distributions (if multiple trials)
    ax = axes[1, 0]
    all_A = [r['fork_location'] for r in results
             if r['condition'] == 'A' and r['question_type'] in identity_types]
    all_B = [r['fork_location'] for r in results
             if r['condition'] == 'B' and r['question_type'] in identity_types]
    if len(set(all_A)) > 1:  # Only histogram if there's variance
        bins = np.arange(0, 82, 4)
        ax.hist(all_A, bins=bins, alpha=0.6, color='steelblue', label=f'True (n={len(all_A)})')
        ax.hist(all_B, bins=bins, alpha=0.6, color='coral', label=f'False (n={len(all_B)})')
        ax.axvline(np.mean(all_A), color='steelblue', linestyle='--', linewidth=2)
        ax.axvline(np.mean(all_B), color='coral', linestyle='--', linewidth=2)
        ax.legend()
    else:
        ax.bar([0, 1], [np.mean(all_A), np.mean(all_B)],
               color=['steelblue', 'coral'], alpha=0.8)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['True (A)', 'False (B)'])
    ax.set_xlabel('Fork Location (token #)')
    ax.set_ylabel('Count')
    ax.set_title('Fork Location Distribution')

    # Plot 4: Commitment angle comparison
    ax = axes[1, 1]
    angles_A = [r['post_fork_angle'] for r in results
                if r['condition'] == 'A' and r['question_type'] in identity_types]
    angles_B = [r['post_fork_angle'] for r in results
                if r['condition'] == 'B' and r['question_type'] in identity_types]
    ax.bar([0, 1], [np.mean(angles_A), np.mean(angles_B)],
           yerr=[np.std(angles_A), np.std(angles_B)],
           color=['steelblue', 'coral'], alpha=0.8)
    ax.axhline(45, color='gray', linestyle='--', alpha=0.5, label='45 deg threshold')
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['True (A)', 'False (B)'])
    ax.set_ylabel('Commitment Angle (degrees)')
    ax.set_title('P4: Commitment Angle (both > 45)')
    ax.legend()

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {output_path}")
    else:
        plt.savefig(str(Path(__file__).parent / 'bridge_results.png'),
                    dpi=150, bbox_inches='tight')
        print(f"Saved: bridge_results.png")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python visualize_bridge.py <results.json> [--title 'Title']")
        sys.exit(1)

    filepath = sys.argv[1]
    title = "Bridge Identity Experiment"
    if '--title' in sys.argv:
        idx = sys.argv.index('--title')
        if idx + 1 < len(sys.argv):
            title = sys.argv[idx + 1]

    results = load_results(filepath)
    print(text_summary(results, title))

    if HAS_MPL:
        output = str(Path(filepath).with_suffix('.png'))
        plot_results(results, title, output)
