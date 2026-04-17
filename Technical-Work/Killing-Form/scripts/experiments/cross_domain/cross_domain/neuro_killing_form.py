"""
Neural Killing Form — Third Substrate Test

Tests P-Neuro-1: cortical CommVar should show a POSITIVE depth gradient
(parallel processing, like food webs and parallel transformers).

Uses the Markov et al. (2013) macaque cortical connectome — 29 directed,
quantitatively weighted cortical areas with FLN (fraction of labeled neurons).

The "depth" axis is cortical hierarchy, derived from the connectivity
asymmetry pattern (feedforward vs feedback laminar patterns).

Same mathematics as transformers and food webs. Third substrate.

Key question: Does r land near +0.4 again?
  Transformers (parallel): r = +0.38
  Food webs:               r = +0.41
  Cortex:                  r = ???
"""
import numpy as np
from scipy import stats
import json, os, sys

# ============================================================
# Load macaque cortical connectivity
# ============================================================

def load_markov_connectome():
    """Load the Markov et al. 2013 macaque directed cortical connectome."""
    from netneurotools.datasets import fetch_famous_gmat

    data = fetch_famous_gmat('macaque_markov')
    # Shape: (93, 29) — 93 target areas, 29 injection sites
    # For square matrix: use the 29x29 core
    conn_full = data['conn']
    labels_full = data['labels']

    # Extract labels
    labels = []
    for i in range(labels_full.shape[0]):
        lab = labels_full[i]
        if hasattr(lab, '__iter__') and not isinstance(lab, str):
            lab = lab[0] if len(lab) > 0 else f"area_{i}"
        labels.append(str(lab))

    # The 29x29 core: injection sites that are also targets
    n_inject = conn_full.shape[1]
    conn_29 = conn_full[:n_inject, :n_inject]

    return conn_29, labels[:n_inject]


def load_additional_connectomes():
    """Load additional connectomes from netneurotools."""
    from netneurotools.datasets import fetch_famous_gmat
    connectomes = {}

    # C. elegans — neuron-level, 279 neurons
    try:
        data = fetch_famous_gmat('celegans')
        connectomes['C. elegans'] = {
            'conn': data['conn'],
            'labels': [str(data['labels'][i][0]) if hasattr(data['labels'][i], '__iter__') else str(data['labels'][i]) for i in range(data['labels'].shape[0])],
            'description': 'C. elegans, 279 neurons, Varshney et al. 2011'
        }
    except Exception as e:
        print(f"  C. elegans: failed ({e})")

    # Mouse cortex — 112 areas
    try:
        data = fetch_famous_gmat('mouse')
        connectomes['Mouse cortex'] = {
            'conn': data['conn'],
            'labels': [str(data['labels'][i][0]) if hasattr(data['labels'][i], '__iter__') else str(data['labels'][i]) for i in range(data['labels'].shape[0])],
            'description': 'Mouse cortex, 112 areas, Rubinov et al. 2015'
        }
    except Exception as e:
        print(f"  Mouse cortex: failed ({e})")

    # Drosophila — 49 brain regions
    try:
        data = fetch_famous_gmat('drosophila')
        connectomes['Drosophila'] = {
            'conn': data['conn'],
            'labels': [str(data['labels'][i][0]) if hasattr(data['labels'][i], '__iter__') else str(data['labels'][i]) for i in range(data['labels'].shape[0])],
            'description': 'Drosophila brain, 49 regions, Chiang et al. 2011'
        }
    except Exception as e:
        print(f"  Drosophila: failed ({e})")

    return connectomes


# ============================================================
# Cortical hierarchy computation
# ============================================================

def compute_hierarchy(A):
    """
    Compute hierarchical depth from directed connectivity asymmetry.

    Method: For each pair (i,j), the ratio A[i,j]/A[j,i] indicates
    feedforward vs feedback dominance. Aggregate asymmetry defines
    hierarchical position.

    This is the Barone et al. (2000) / Markov & Kennedy method:
    hierarchy level ~ net feedforward tendency.
    """
    n = A.shape[0]

    # Compute asymmetry for each region:
    # How much does this region send feedforward (to "higher" areas)?
    # Feedforward connections: where A[i,j] >> A[j,i]

    # Simple method: total outgoing / total incoming
    # High ratio = low in hierarchy (sends up)
    # Low ratio = high in hierarchy (sends down)
    total_out = np.sum(A, axis=1)  # row sums = total projections FROM this area
    total_in = np.sum(A, axis=0)   # col sums = total projections TO this area

    # Hierarchy: areas that receive more than they send are "higher"
    # Use log ratio, handle zeros
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = np.log10((total_in + 1e-10) / (total_out + 1e-10))

    # Normalize to [0, 1]
    if np.ptp(ratio) > 0:
        hierarchy = (ratio - np.min(ratio)) / np.ptp(ratio)
    else:
        hierarchy = np.zeros(n)

    return hierarchy


def compute_hierarchy_svd(A):
    """
    Alternative hierarchy from SVD of asymmetry matrix.
    The first left singular vector of (A - A^T) gives hierarchical ordering.
    """
    asymmetry = A - A.T
    U, S, Vt = np.linalg.svd(asymmetry)
    hierarchy = U[:, 0]

    # Normalize to [0, 1]
    if np.ptp(hierarchy) > 0:
        hierarchy = (hierarchy - np.min(hierarchy)) / np.ptp(hierarchy)

    return hierarchy


# ============================================================
# Killing form computation
# ============================================================

def compute_killing_form(A, max_n=80):
    """Compute ecological/neural Killing form for a directed connectivity matrix."""
    n = A.shape[0]

    if n > max_n:
        print(f"    Subsampling from {n} to {max_n} for tractability...")
        # Keep the max_n regions with highest total connectivity
        total_conn = np.sum(A, axis=0) + np.sum(A, axis=1)
        top_idx = np.argsort(total_conn)[-max_n:]
        A = A[np.ix_(top_idx, top_idx)]
        n = max_n
    else:
        top_idx = np.arange(n)

    # Normalize
    An = A / (np.max(np.abs(A)) + 1e-10)

    # Interaction operators: W_i = outer(effects_OF_i, effects_ON_i)
    W = [np.outer(An[:, i], An[i, :]) for i in range(n)]

    # Check mediation: how many regions both send and receive?
    n_senders = np.sum(np.sum(A, axis=1) > 0)
    n_receivers = np.sum(np.sum(A, axis=0) > 0)
    n_mediators = np.sum((np.sum(A, axis=1) > 0) & (np.sum(A, axis=0) > 0))

    # Commutator norms
    cn = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            C = W[i] @ W[j] - W[j] @ W[i]
            cn[i,j] = cn[j,i] = np.linalg.norm(C, 'fro')

    # Killing form
    kf = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            val = 0.0
            for m in range(n):
                Cim = W[i] @ W[m] - W[m] @ W[i]
                Cjm = W[j] @ W[m] - W[m] @ W[j]
                val += np.trace(Cim @ Cjm)
            kf[i,j] = kf[j,i] = val

    # Eigenvalues
    eigs = np.sort(np.linalg.eigvalsh(kf))[::-1]
    me = np.max(np.abs(eigs))
    af = np.mean(np.abs(eigs) < 0.1 * me) if me > 0 else 1.0

    # CommVar
    upper = cn[np.triu_indices(n, k=1)]
    cv = np.var(upper / np.max(upper)) if np.max(upper) > 0 else 0.0

    return {
        'af': af, 'cv': cv, 'cn': cn, 'eigs': eigs,
        'n_regions': n, 'n_senders': int(n_senders),
        'n_receivers': int(n_receivers), 'n_mediators': int(n_mediators),
        'top_idx': top_idx
    }


def compute_depth_gradient(A, cn, hierarchy, n_bins=5):
    """Compute CommVar at each hierarchical level."""
    n = A.shape[0]

    # Bin regions by hierarchy level
    h_bins = np.digitize(hierarchy, np.linspace(0, 1.001, n_bins + 1)) - 1

    cvs, bin_centers = [], []
    for b in range(n_bins):
        regions = np.where(h_bins == b)[0]
        if len(regions) < 2:
            continue

        norms = [cn[i,j] for i in regions for j in range(n) if j != i]
        if norms and max(norms) > 0:
            cvs.append(np.var([x/max(norms) for x in norms]))
            bin_centers.append(np.mean(hierarchy[regions]))

    if len(cvs) >= 3:
        r, p = stats.spearmanr(bin_centers, cvs)
    else:
        r, p = 0.0, 1.0

    return r, p, cvs, bin_centers


# ============================================================
# Main
# ============================================================

def analyze_connectome(name, A, labels, description=""):
    """Full Killing form analysis on a connectome."""
    n = A.shape[0]
    print(f"\n{'='*60}")
    print(f"  {name}: {n} regions")
    if description:
        print(f"  {description}")

    # Connectivity stats
    density = np.sum(A > 0) / (n * n)
    asymmetry = np.sum(np.abs(A - A.T) > 0) / max(np.sum(A > 0) + np.sum(A.T > 0), 1)
    print(f"  Density: {density:.3f}")
    print(f"  Directed asymmetry: {asymmetry:.3f}")

    # Compute Killing form
    sys.stdout.write("  Computing Killing form... ")
    sys.stdout.flush()
    kf = compute_killing_form(A)
    print(f"done.")
    print(f"  Mediators: {kf['n_mediators']}/{kf['n_regions']} ({100*kf['n_mediators']/kf['n_regions']:.0f}%)")
    print(f"  Abelian fraction: {kf['af']:.3f}")
    print(f"  CommVar: {kf['cv']:.6f}")

    # Use the subset of A if it was subsampled
    A_sub = A
    if len(kf['top_idx']) < n:
        A_sub = A[np.ix_(kf['top_idx'], kf['top_idx'])]

    # Compute hierarchy (two methods)
    h1 = compute_hierarchy(A_sub)
    h2 = compute_hierarchy_svd(A_sub)

    # Depth gradient with both methods
    r1, p1, cvs1, bins1 = compute_depth_gradient(A_sub, kf['cn'], h1)
    r2, p2, cvs2, bins2 = compute_depth_gradient(A_sub, kf['cn'], h2)

    print(f"\n  Depth gradient (in/out ratio hierarchy):")
    print(f"    r = {r1:+.3f}, p = {p1:.4f}")
    if cvs1:
        for b, c in zip(bins1, cvs1):
            print(f"      depth {b:.2f}: CV = {c:.6f}")

    print(f"\n  Depth gradient (SVD hierarchy):")
    print(f"    r = {r2:+.3f}, p = {p2:.4f}")
    if cvs2:
        for b, c in zip(bins2, cvs2):
            print(f"      depth {b:.2f}: CV = {c:.6f}")

    return {
        'name': name,
        'n_regions': kf['n_regions'],
        'n_mediators': kf['n_mediators'],
        'density': float(density),
        'asymmetry': float(asymmetry),
        'af': kf['af'],
        'cv': kf['cv'],
        'depth_r_ratio': r1,
        'depth_p_ratio': p1,
        'depth_r_svd': r2,
        'depth_p_svd': p2,
    }


def main():
    print("=" * 70)
    print("NEURAL KILLING FORM -- Third Substrate Test")
    print("Same mathematics. Third substrate. Does r land near +0.4?")
    print("=" * 70)

    results = []

    # 1. Macaque cortex (Markov et al. 2013)
    print("\nLoading Markov macaque connectome...")
    try:
        conn, labels = load_markov_connectome()
        print(f"  Matrix shape: {conn.shape}")
        print(f"  Labels: {labels[:5]}...")
        print(f"  Nonzero entries: {np.sum(conn > 0)}")
        print(f"  Symmetric? {np.allclose(conn, conn.T)}")

        result = analyze_connectome("Macaque cortex (Markov)", conn, labels,
                                    "29 areas, FLN weights, retrograde tracing")
        results.append(result)
    except Exception as e:
        print(f"  Error: {e}")

    # 2. Additional connectomes
    print("\nLoading additional connectomes...")
    try:
        additional = load_additional_connectomes()
        for name, data in additional.items():
            n = data['conn'].shape[0]
            if n > 150:
                print(f"  {name} ({n} regions) -- using top 80 for tractability")
            result = analyze_connectome(name, data['conn'], data['labels'], data['description'])
            results.append(result)
    except Exception as e:
        print(f"  Error loading additional: {e}")

    # Summary
    print(f"\n\n{'='*70}")
    print(f"RESULTS SUMMARY: {len(results)} connectomes analyzed")
    print(f"{'='*70}")

    print(f"\n{'Name':<25} {'n':>5} {'Med%':>5} {'AF':>6} {'CV':>10} {'r(ratio)':>9} {'r(SVD)':>9}")
    print("-" * 75)
    for r in results:
        med_pct = 100 * r['n_mediators'] / r['n_regions']
        print(f"{r['name']:<25} {r['n_regions']:>5} {med_pct:>5.0f} {r['af']:>6.3f} "
              f"{r['cv']:>10.6f} {r['depth_r_ratio']:>+9.3f} {r['depth_r_svd']:>+9.3f}")

    # Cross-domain comparison
    print(f"\n{'='*70}")
    print("CROSS-DOMAIN COMPARISON")
    print(f"{'='*70}")
    print(f"\nTransformer (parallel):  r = +0.38 (n=3)")
    print(f"Transformer (sequential): r = -0.76 (n=7)")
    print(f"Food webs:               r = +0.41 (n=10)")
    for r in results:
        avg_r = np.mean([r['depth_r_ratio'], r['depth_r_svd']])
        print(f"{r['name']:<25} r = {avg_r:+.3f} (avg of two hierarchy methods)")

    print(f"\nDoes the cortex join the parallel family?")
    for r in results:
        avg_r = np.mean([r['depth_r_ratio'], r['depth_r_svd']])
        if avg_r > 0.2:
            print(f"  {r['name']}: YES (r = {avg_r:+.3f})")
        elif avg_r > -0.2:
            print(f"  {r['name']}: AMBIGUOUS (r = {avg_r:+.3f})")
        else:
            print(f"  {r['name']}: NO (r = {avg_r:+.3f})")

    # Save results
    outpath = os.path.join(os.path.dirname(__file__), 'neuro_kf_results.json')
    with open(outpath, 'w') as f:
        json.dump({'results': results}, f, indent=2)
    print(f"\nResults saved to {outpath}")


if __name__ == '__main__':
    main()
