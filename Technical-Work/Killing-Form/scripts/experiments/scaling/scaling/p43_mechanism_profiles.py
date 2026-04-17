"""
P43: CommVar Depth Profile Analysis — The Mechanism Question
============================================================

WHY does architecture determine depth gradient direction?

Hypothesis 1 (Sedimentation cascade): Sequential models start HIGH and
decay — each sequential step filters out algebraic structure.

Hypothesis 2 (Independent accumulation): Parallel models start LOW and
grow — independent pathways allow non-commutativity to compound.

Hypothesis 3 (Initialization offset): Both start similar, but diverge
because sequential coupling forces early-layer structure while parallel
independence delays it.

This script loads per-layer CommVar from all experiments and examines
the PROFILE SHAPES to distinguish between hypotheses.

Author: Clawd
Date: April 10, 2026
"""

import json
import numpy as np
from scipy import stats
import os

RESULTS_DIR = os.path.dirname(os.path.abspath(__file__))


def load_results(filename):
    path = os.path.join(RESULTS_DIR, filename)
    with open(path) as f:
        return json.load(f)


def normalize_profile(cvs):
    """Normalize to [0,1] range for shape comparison."""
    arr = np.array(cvs)
    mn, mx = arr.min(), arr.max()
    if mx > mn:
        return (arr - mn) / (mx - mn)
    return np.zeros_like(arr)


if __name__ == '__main__':
    print("P43: CommVar Depth Profile Analysis")
    print("=" * 70)

    # Load all models with per-layer data
    models = {}

    # P42c has all Pythia + GPT-2 d_head=64 models
    p42c = load_results('p42c_dhead64_results.json')
    for model_data in p42c.get('models', []):
        name = model_data['model'].split('/')[-1]
        if 'layer_cvs' in model_data:
            arch = 'parallel' if 'pythia' in name.lower() else 'sequential'
            models[name] = {
                'arch': arch,
                'layer_cvs': model_data['layer_cvs'],
                'layer_afs': model_data.get('layer_afs', []),
                'n_layers': len(model_data['layer_cvs']),
                'family': 'Pythia' if 'pythia' in name.lower() else 'GPT-2',
            }

    # Individual results
    for fname, name, arch, family in [
        ('p42d_llama_results.json', 'TinyLlama-1.1B', 'sequential', 'TinyLlama'),
        ('p42e_phi_results.json', 'Phi-1.5', 'parallel', 'Phi'),
        ('p42f_opt_results.json', 'OPT-1.3B', 'sequential', 'OPT'),
        ('p42g_falcon_results.json', 'Falcon-RW-1B', 'sequential', 'Falcon'),
    ]:
        try:
            data = load_results(fname)
            if 'layer_cvs' in data:
                models[name] = {
                    'arch': arch,
                    'layer_cvs': data['layer_cvs'],
                    'layer_afs': data.get('layer_afs', []),
                    'n_layers': len(data['layer_cvs']),
                    'family': family,
                }
        except FileNotFoundError:
            pass

    print(f"\nLoaded {len(models)} models\n")

    # === ANALYSIS 1: Absolute CommVar at Layer 0 vs Last Layer ===
    print("=" * 70)
    print("ANALYSIS 1: Where does the CommVar START and END?")
    print("=" * 70)
    print(f"\n{'Model':<20} {'Arch':<12} {'CV_first':>12} {'CV_last':>12} {'Ratio':>8} {'r':>8}")
    print("-" * 76)

    parallel_starts = []
    sequential_starts = []
    parallel_ends = []
    sequential_ends = []

    for name in sorted(models.keys()):
        m = models[name]
        cvs = m['layer_cvs']
        if len(cvs) < 4:  # Skip models with too few layers
            continue
        cv_first = np.mean(cvs[:2])  # Average first 2 layers
        cv_last = np.mean(cvs[-2:])  # Average last 2 layers
        ratio = cv_last / cv_first if cv_first > 0 else float('inf')
        r, _ = stats.spearmanr(range(len(cvs)), cvs)
        print(f"{name:<20} {m['arch']:<12} {cv_first:>12.6f} {cv_last:>12.6f} {ratio:>8.2f} {r:>+8.3f}")

        if m['arch'] == 'parallel' and cv_first > 1e-5:  # Exclude noise-level
            parallel_starts.append(cv_first)
            parallel_ends.append(cv_last)
        elif m['arch'] == 'sequential' and cv_first > 1e-5:
            sequential_starts.append(cv_first)
            sequential_ends.append(cv_last)

    if parallel_starts and sequential_starts:
        print(f"\nParallel: start mean={np.mean(parallel_starts):.6f}, end mean={np.mean(parallel_ends):.6f}")
        print(f"Sequential: start mean={np.mean(sequential_starts):.6f}, end mean={np.mean(sequential_ends):.6f}")
        print(f"\nStart ratio (seq/par): {np.mean(sequential_starts)/np.mean(parallel_starts):.2f}")
        print(f"End ratio (seq/par): {np.mean(sequential_ends)/np.mean(parallel_ends):.2f}")

    # === ANALYSIS 2: Normalized profile shapes ===
    print(f"\n{'='*70}")
    print("ANALYSIS 2: Normalized Profile Shapes (0=min, 1=max)")
    print("=" * 70)

    for arch_type in ['parallel', 'sequential']:
        print(f"\n--- {arch_type.upper()} ---")
        for name in sorted(models.keys()):
            m = models[name]
            if m['arch'] != arch_type:
                continue
            cvs = m['layer_cvs']
            if len(cvs) < 4 or max(cvs) < 1e-5:
                continue
            normed = normalize_profile(cvs)
            # Show quartile positions
            n = len(normed)
            q1 = normed[:n//4].mean()
            q2 = normed[n//4:n//2].mean()
            q3 = normed[n//2:3*n//4].mean()
            q4 = normed[3*n//4:].mean()
            # Where is the peak?
            peak_pos = np.argmax(cvs) / (n - 1) if n > 1 else 0
            print(f"  {name:<20} Q1={q1:.2f} Q2={q2:.2f} Q3={q3:.2f} Q4={q4:.2f}  peak@{peak_pos:.0%}")

    # === ANALYSIS 3: First-layer vs last-layer CommVar ratio ===
    print(f"\n{'='*70}")
    print("ANALYSIS 3: Profile Classification")
    print("=" * 70)

    for name in sorted(models.keys()):
        m = models[name]
        cvs = np.array(m['layer_cvs'])
        if len(cvs) < 4 or max(cvs) < 1e-5:
            continue
        n = len(cvs)

        # Classify shape
        first_half = cvs[:n//2].mean()
        second_half = cvs[n//2:].mean()
        monotonic_r, _ = stats.spearmanr(range(n), cvs)

        if second_half > 2 * first_half:
            shape = "RISING (late-concentrated)"
        elif first_half > 2 * second_half:
            shape = "FALLING (early-concentrated)"
        elif abs(monotonic_r) < 0.3:
            shape = "FLAT (uniform)"
        elif monotonic_r > 0:
            shape = "RISING (gradual)"
        else:
            shape = "FALLING (gradual)"

        print(f"  {name:<20} {m['arch']:<12} {shape}")

    # === ANALYSIS 4: Cross-architecture comparison at matched depth fraction ===
    print(f"\n{'='*70}")
    print("ANALYSIS 4: CommVar at 25%/50%/75% depth (absolute values)")
    print("=" * 70)

    print(f"\n{'Model':<20} {'Arch':<12} {'CV@25%':>10} {'CV@50%':>10} {'CV@75%':>10}")
    print("-" * 66)

    for name in sorted(models.keys()):
        m = models[name]
        cvs = np.array(m['layer_cvs'])
        if len(cvs) < 4 or max(cvs) < 1e-5:
            continue
        n = len(cvs)
        cv25 = cvs[n//4]
        cv50 = cvs[n//2]
        cv75 = cvs[3*n//4]
        print(f"  {name:<20} {m['arch']:<12} {cv25:>10.6f} {cv50:>10.6f} {cv75:>10.6f}")

    # === ANALYSIS 5: Hypothesis evaluation ===
    print(f"\n{'='*70}")
    print("HYPOTHESIS EVALUATION")
    print("=" * 70)

    print("""
H1 (Sedimentation cascade): Sequential starts HIGH, decays.
   Test: Do sequential models have higher CV at layer 0 than parallel?

H2 (Independent accumulation): Parallel starts LOW, grows.
   Test: Do parallel models have lower CV at early layers?

H3 (Initialization offset): Both start similar, diverge.
   Test: Are first-layer CVs similar, with divergence appearing later?
""")

    # Collect first-quarter and last-quarter CVs by architecture
    par_q1 = []
    par_q4 = []
    seq_q1 = []
    seq_q4 = []

    for name, m in models.items():
        cvs = np.array(m['layer_cvs'])
        if len(cvs) < 8 or max(cvs) < 1e-5:
            continue
        n = len(cvs)
        if m['arch'] == 'parallel':
            par_q1.append(np.mean(cvs[:n//4]))
            par_q4.append(np.mean(cvs[3*n//4:]))
        else:
            seq_q1.append(np.mean(cvs[:n//4]))
            seq_q4.append(np.mean(cvs[3*n//4:]))

    if par_q1 and seq_q1:
        print(f"First quarter CV — Parallel: {np.mean(par_q1):.6f}, Sequential: {np.mean(seq_q1):.6f}")
        print(f"Last quarter CV  — Parallel: {np.mean(par_q4):.6f}, Sequential: {np.mean(seq_q4):.6f}")

        # Which starts higher?
        if np.mean(seq_q1) > 1.5 * np.mean(par_q1):
            print("\n→ Sequential starts HIGHER — supports H1 (sedimentation)")
        elif np.mean(par_q1) > 1.5 * np.mean(seq_q1):
            print("\n→ Parallel starts HIGHER — contradicts H1")
        else:
            print("\n→ Similar starting points — supports H3 (divergence)")

        # Which ends higher?
        if np.mean(par_q4) > 1.5 * np.mean(seq_q4):
            print("→ Parallel ends HIGHER — supports H2 (accumulation)")
        elif np.mean(seq_q4) > 1.5 * np.mean(par_q4):
            print("→ Sequential ends HIGHER — contradicts H2")
        else:
            print("→ Similar endpoints — need more data")

    print(f"\n{'='*70}")
    print("Done. Results are descriptive — no JSON saved (analysis only).")
