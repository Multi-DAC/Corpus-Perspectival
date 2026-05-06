"""
Ecological Killing Form — Cross-Domain Test

Tests predictions P-Eco-1 through P-Eco-4 from cross_domain_killing_form.md:
  The same Killing form mathematics applied to transformers should apply
  to ecological networks. Species = "heads", trophic levels = "depth".

Uses real food web data from Web of Life database + Network Repository.

Method:
  For each species i in a food web with n species:
    1. Extract interaction vector a_i (column i of adjacency matrix)
    2. Construct interaction operator W_i = outer(a_out_i, a_in_i)
       where a_out_i = effects OF species i on others (column i)
       and a_in_i = effects ON species i from others (row i)
    3. W_i is an n×n matrix representing species i's mediation role
    4. Commutator [W_i, W_j] = W_i @ W_j - W_j @ W_i
    5. Killing form κ_{ij} = Σ_k Tr([W_i,W_k][W_j,W_k])

  This is IDENTICAL mathematics to the transformer Killing form,
  just with different substrates for "heads" and "interaction operators".

  Trophic level = ecological "depth" (analog of network layer depth).
  Computed as: TL(i) = 1 + mean(TL(prey of i))

Predictions:
  P-Eco-1: Modular food webs → higher Abelian fraction than nested
  P-Eco-2: Nested food webs → CommVar decreases with trophic level (sedimentation)
  P-Eco-3: Modular food webs → CommVar flat or increases with trophic level
  P-Eco-4: Modularity/nestedness ratio predicts depth gradient sign
"""

import numpy as np
from scipy import stats
import json
import os

###############################################################################
# Data loading
###############################################################################

def load_weboflife_foodwebs(json_path):
    """Load food webs from Web of Life JSON export."""
    with open(json_path) as f:
        data = json.load(f)

    networks = {}
    for record in data:
        name = record.get('network_name', '')
        if not name.startswith('FW_'):
            continue
        if name not in networks:
            networks[name] = []
        networks[name].append(record)

    foodwebs = {}
    for name, records in networks.items():
        # Build species list and adjacency matrix
        species_set = set()
        for r in records:
            species_set.add(r['species1'])
            species_set.add(r['species2'])
        species = sorted(species_set)
        sp_idx = {s: i for i, s in enumerate(species)}
        n = len(species)

        # A[i,j] = interaction strength from species j (prey/resource) to species i (consumer)
        # In Web of Life FW data: species1 = prey, species2 = predator
        A = np.zeros((n, n))
        for r in records:
            prey = sp_idx[r['species1']]
            pred = sp_idx[r['species2']]
            weight = float(r['connection_strength'])
            A[pred, prey] = weight  # predator row, prey column

        foodwebs[name] = {
            'matrix': A,
            'species': species,
            'n_species': n,
            'n_interactions': len(records),
            'source': 'WebOfLife'
        }

    return foodwebs


def load_edgelist_foodweb(filepath, name):
    """Load a food web from Network Repository edge list format."""
    edges = []
    nodes = set()
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('%') or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2:
                src = int(parts[0])
                tgt = int(parts[1])
                weight = float(parts[2]) if len(parts) >= 3 else 1.0
                edges.append((src, tgt, weight))
                nodes.add(src)
                nodes.add(tgt)

    # Map to contiguous indices
    node_list = sorted(nodes)
    idx_map = {n: i for i, n in enumerate(node_list)}
    n = len(node_list)

    A = np.zeros((n, n))
    for src, tgt, w in edges:
        A[idx_map[tgt], idx_map[src]] = w  # tgt consumes src

    return {
        'matrix': A,
        'species': [str(n) for n in node_list],
        'n_species': n,
        'n_interactions': len(edges),
        'source': 'NetworkRepository'
    }


###############################################################################
# Trophic level computation
###############################################################################

def compute_trophic_levels(A):
    """
    Compute trophic levels using the standard formula:
    TL(i) = 1 + mean(TL(prey of i))

    Solved iteratively. Basal species (no prey) have TL = 1.
    """
    n = A.shape[0]
    TL = np.ones(n)  # start all at 1

    # Iterate to convergence
    for iteration in range(100):
        TL_old = TL.copy()
        for i in range(n):
            prey_indices = np.where(A[i, :] > 0)[0]
            if len(prey_indices) > 0:
                # Weighted mean trophic level of prey
                weights = A[i, prey_indices]
                TL[i] = 1 + np.average(TL_old[prey_indices], weights=weights)

        if np.max(np.abs(TL - TL_old)) < 1e-6:
            break

    return TL


###############################################################################
# Ecological Killing form
###############################################################################

def compute_eco_killing_form(A, min_species=8):
    """
    Compute the Killing form for a food web interaction matrix.

    For each species i, construct interaction operator W_i:
      W_i = outer(a_out_i, a_in_i)
    where a_out_i = A[:, i] (effects OF species i)
    and   a_in_i = A[i, :] (effects ON species i)

    Then compute commutators and Killing form exactly as for transformers.
    """
    n = A.shape[0]
    if n < min_species:
        return None

    # Normalize A for numerical stability
    A_norm = A / (np.max(np.abs(A)) + 1e-10)

    # Construct interaction operators W_i for each species
    W = []
    for i in range(n):
        a_out = A_norm[:, i]  # column i: effects OF species i on others
        a_in = A_norm[i, :]   # row i: effects ON species i from others
        W_i = np.outer(a_out, a_in)
        W.append(W_i)

    # Compute commutators [W_i, W_j] for all pairs
    n_pairs = n * (n - 1) // 2
    comm_norms = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            C = W[i] @ W[j] - W[j] @ W[i]
            norm = np.sqrt(np.sum(C ** 2))  # Frobenius norm
            comm_norms[i, j] = norm
            comm_norms[j, i] = norm

    # Compute Killing form: κ_{ij} = Σ_k Tr([W_i,W_k] @ [W_j,W_k])
    killing_form = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            kappa = 0.0
            for k in range(n):
                if k == i or k == j:
                    C_ik = W[i] @ W[k] - W[k] @ W[i]
                    C_jk = W[j] @ W[k] - W[k] @ W[j]
                else:
                    C_ik = W[i] @ W[k] - W[k] @ W[i]
                    C_jk = W[j] @ W[k] - W[k] @ W[j]
                kappa += np.trace(C_ik @ C_jk)
            killing_form[i, j] = kappa
            killing_form[j, i] = kappa

    # Eigenvalues of the Killing form
    eigenvalues = np.linalg.eigvalsh(killing_form)
    eigenvalues = np.sort(eigenvalues)[::-1]

    # Abelian fraction: fraction of eigenvalues below 10% of max
    max_eig = np.max(np.abs(eigenvalues))
    if max_eig > 0:
        threshold = 0.1 * max_eig
        abelian_fraction = np.mean(np.abs(eigenvalues) < threshold)
    else:
        abelian_fraction = 1.0

    # CommVar: variance of normalized commutator norms
    upper_tri = comm_norms[np.triu_indices(n, k=1)]
    if np.max(upper_tri) > 0:
        normalized = upper_tri / np.max(upper_tri)
        comm_var = np.var(normalized)
    else:
        comm_var = 0.0

    return {
        'killing_form': killing_form,
        'eigenvalues': eigenvalues,
        'abelian_fraction': abelian_fraction,
        'comm_var': comm_var,
        'comm_norms': comm_norms,
        'interaction_operators': W,
        'n_species': n
    }


def compute_trophic_depth_gradient(A, kf_result):
    """
    Compute CommVar at each trophic level (the ecological "depth gradient").

    Groups species by trophic level band, computes CommVar within each band.
    Returns Spearman correlation between trophic level and CommVar.
    """
    n = A.shape[0]
    TL = compute_trophic_levels(A)
    comm_norms = kf_result['comm_norms']

    # Group species into trophic level bands
    # Round to nearest 0.5 for binning
    tl_bins = np.round(TL * 2) / 2  # round to 0.5
    unique_bins = np.sort(np.unique(tl_bins))

    trophic_commvar = []
    trophic_levels_mean = []

    for bin_val in unique_bins:
        species_in_bin = np.where(tl_bins == bin_val)[0]
        if len(species_in_bin) < 2:
            continue

        # CommVar for this trophic level: variance of commutator norms
        # among species at this level with ALL other species
        norms_at_level = []
        for i in species_in_bin:
            for j in range(n):
                if j != i:
                    norms_at_level.append(comm_norms[i, j])

        if len(norms_at_level) > 1:
            max_norm = max(norms_at_level) if max(norms_at_level) > 0 else 1
            normalized = [x / max_norm for x in norms_at_level]
            cv = np.var(normalized)
            trophic_commvar.append(cv)
            trophic_levels_mean.append(float(bin_val))

    if len(trophic_commvar) >= 3:
        r, p = stats.spearmanr(trophic_levels_mean, trophic_commvar)
    else:
        r, p = 0.0, 1.0

    return {
        'trophic_levels': TL,
        'trophic_bins': trophic_levels_mean,
        'trophic_commvar': trophic_commvar,
        'depth_gradient_r': r,
        'depth_gradient_p': p,
        'n_bins': len(trophic_commvar)
    }


###############################################################################
# Modularity and nestedness
###############################################################################

def compute_modularity(A):
    """
    Compute modularity Q of the food web using spectral method.
    Higher Q → more modular network.
    """
    # Convert to binary
    B = (A > 0).astype(float)
    # Symmetrize for modularity calculation
    B_sym = B + B.T
    B_sym = (B_sym > 0).astype(float)

    n = B_sym.shape[0]
    m = np.sum(B_sym) / 2  # number of edges
    if m == 0:
        return 0.0, np.zeros(n, dtype=int)

    k = np.sum(B_sym, axis=1)  # degree

    # Modularity matrix
    M = B_sym - np.outer(k, k) / (2 * m)

    # Spectral partitioning (first eigenvector)
    eigenvalues, eigenvectors = np.linalg.eigh(M)
    idx = np.argmax(eigenvalues)
    v = eigenvectors[:, idx]

    # Partition by sign
    partition = (v >= 0).astype(int)

    # Compute Q
    Q = 0
    for i in range(n):
        for j in range(n):
            if partition[i] == partition[j]:
                Q += M[i, j]
    Q /= (2 * m)

    return float(Q), partition


def compute_nestedness(A):
    """
    Compute nestedness (NODF) of the food web.
    Higher NODF → more nested network.

    Nestedness measures whether specialists interact with subsets
    of the species that generalists interact with.
    """
    B = (A > 0).astype(float)
    n = B.shape[0]

    # Row fill (number of interactions per species)
    row_fill = np.sum(B, axis=1)
    col_fill = np.sum(B, axis=0)

    # Compute paired overlap for rows
    n_row = 0
    nodf_rows = 0
    for i in range(n):
        for j in range(i + 1, n):
            if row_fill[i] != row_fill[j] and min(row_fill[i], row_fill[j]) > 0:
                # Species with fewer interactions
                min_idx = i if row_fill[i] < row_fill[j] else j
                max_idx = j if row_fill[i] < row_fill[j] else i
                # Overlap: fraction of min's interactions that overlap with max's
                overlap = np.sum(B[min_idx, :] * B[max_idx, :])
                nodf_rows += overlap / row_fill[min_idx]
                n_row += 1

    # Same for columns
    n_col = 0
    nodf_cols = 0
    for i in range(n):
        for j in range(i + 1, n):
            if col_fill[i] != col_fill[j] and min(col_fill[i], col_fill[j]) > 0:
                min_idx = i if col_fill[i] < col_fill[j] else j
                max_idx = j if col_fill[i] < col_fill[j] else i
                overlap = np.sum(B[:, min_idx] * B[:, max_idx])
                nodf_cols += overlap / col_fill[min_idx]
                n_col += 1

    total = n_row + n_col
    if total > 0:
        nodf = (nodf_rows + nodf_cols) / total
    else:
        nodf = 0.0

    return float(nodf)


###############################################################################
# Main analysis
###############################################################################

def analyze_foodweb(name, fw_data, verbose=True):
    """Run full Killing form analysis on a single food web."""
    A = fw_data['matrix']
    n = fw_data['n_species']

    if n < 8:
        if verbose:
            print(f"  {name}: SKIPPED (only {n} species, need ≥8)")
        return None

    if verbose:
        print(f"\n{'='*60}")
        print(f"  {name}: {n} species, {fw_data['n_interactions']} interactions")
        print(f"  Connectance: {np.sum(A > 0) / (n*n):.3f}")

    # Compute modularity and nestedness
    Q, partition = compute_modularity(A)
    nodf = compute_nestedness(A)

    if verbose:
        print(f"  Modularity Q: {Q:.3f}")
        print(f"  Nestedness NODF: {nodf:.3f}")
        n_modules = len(np.unique(partition))
        print(f"  Modules (spectral): {n_modules}")

    # Compute Killing form
    kf = compute_eco_killing_form(A)
    if kf is None:
        return None

    if verbose:
        print(f"  Abelian fraction: {kf['abelian_fraction']:.3f}")
        print(f"  CommVar: {kf['comm_var']:.6f}")

    # Compute trophic depth gradient
    depth = compute_trophic_depth_gradient(A, kf)

    if verbose:
        TL = depth['trophic_levels']
        print(f"  Trophic levels: {np.min(TL):.1f} to {np.max(TL):.1f}")
        print(f"  Depth bins: {depth['n_bins']}")
        print(f"  Depth gradient r: {depth['depth_gradient_r']:+.3f} (p={depth['depth_gradient_p']:.3f})")
        if depth['n_bins'] >= 3:
            print(f"  CommVar by trophic level:")
            for tl, cv in zip(depth['trophic_bins'], depth['trophic_commvar']):
                print(f"    TL {tl:.1f}: CV={cv:.6f}")

    return {
        'name': name,
        'n_species': n,
        'n_interactions': fw_data['n_interactions'],
        'connectance': float(np.sum(A > 0) / (n * n)),
        'modularity_Q': Q,
        'nestedness_NODF': nodf,
        'abelian_fraction': kf['abelian_fraction'],
        'comm_var': kf['comm_var'],
        'depth_gradient_r': depth['depth_gradient_r'],
        'depth_gradient_p': depth['depth_gradient_p'],
        'n_trophic_bins': depth['n_bins'],
        'trophic_bins': depth['trophic_bins'],
        'trophic_commvar': depth['trophic_commvar'],
    }


def main():
    print("=" * 70)
    print("ECOLOGICAL KILLING FORM — Cross-Domain Test")
    print("Same mathematics as transformer Killing form, different substrate")
    print("=" * 70)

    # Load all available food webs
    all_foodwebs = {}

    # Web of Life data
    wol_path = os.path.join(os.path.dirname(__file__), 'foodweb_data', 'weboflife_foodwebs.json')
    if not os.path.exists(wol_path):
        wol_path = os.path.join('.', 'foodweb_data', 'weboflife_foodwebs.json')
    if not os.path.exists(wol_path):
        wol_path = 'weboflife_foodwebs.json'

    if os.path.exists(wol_path):
        print(f"\nLoading Web of Life food webs from {wol_path}...")
        wol_fws = load_weboflife_foodwebs(wol_path)
        all_foodwebs.update(wol_fws)
        print(f"  Loaded {len(wol_fws)} food webs")

    # Network Repository edge lists
    data_dir = os.path.dirname(wol_path)
    for edgefile in ['eco-everglades.edges', 'eco-florida.edges', 'eco-stmarks.edges']:
        epath = os.path.join(data_dir, edgefile)
        if os.path.exists(epath):
            name = edgefile.replace('.edges', '').upper()
            all_foodwebs[name] = load_edgelist_foodweb(epath, name)
            print(f"  Loaded {name}: {all_foodwebs[name]['n_species']} species")

    print(f"\nTotal food webs: {len(all_foodwebs)}")

    # Analyze all food webs
    results = []
    for name in sorted(all_foodwebs.keys()):
        result = analyze_foodweb(name, all_foodwebs[name])
        if result is not None:
            results.append(result)

    print(f"\n\n{'='*70}")
    print(f"RESULTS SUMMARY: {len(results)} food webs analyzed")
    print(f"{'='*70}")

    # Sort by modularity for display
    results.sort(key=lambda x: x['modularity_Q'], reverse=True)

    print(f"\n{'Name':<20} {'n':>4} {'Q':>6} {'NODF':>6} {'AF':>6} {'CV':>10} {'r(depth)':>9} {'p':>7}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<20} {r['n_species']:>4} {r['modularity_Q']:>6.3f} {r['nestedness_NODF']:>6.3f} "
              f"{r['abelian_fraction']:>6.3f} {r['comm_var']:>10.6f} {r['depth_gradient_r']:>+9.3f} {r['depth_gradient_p']:>7.3f}")

    # Test P-Eco-1: Modular food webs → higher Abelian fraction
    print(f"\n\n{'='*70}")
    print("PREDICTION TESTS")
    print(f"{'='*70}")

    # Median split on modularity
    Q_values = [r['modularity_Q'] for r in results]
    Q_median = np.median(Q_values)

    modular = [r for r in results if r['modularity_Q'] > Q_median]
    nested = [r for r in results if r['modularity_Q'] <= Q_median]

    print(f"\nMedian modularity Q = {Q_median:.3f}")
    print(f"High-modularity group: n={len(modular)}")
    print(f"Low-modularity group: n={len(nested)}")

    # P-Eco-1: AF comparison
    af_mod = [r['abelian_fraction'] for r in modular]
    af_nest = [r['abelian_fraction'] for r in nested]
    if len(af_mod) >= 2 and len(af_nest) >= 2:
        u_stat, p_val = stats.mannwhitneyu(af_mod, af_nest, alternative='greater')
        print(f"\n[P-Eco-1] Modular AF ({np.mean(af_mod):.3f}) vs Nested AF ({np.mean(af_nest):.3f})")
        print(f"  Mann-Whitney U={u_stat:.1f}, p={p_val:.4f}")
        print(f"  Prediction: Modular > Nested → {'CONFIRMED' if p_val < 0.05 else 'NOT SIGNIFICANT' if p_val < 0.1 else 'DISCONFIRMED'}")

    # P-Eco-4: Modularity predicts depth gradient sign
    # Use nestedness as the predictor (high NODF → sequential/nested → negative r)
    nodf_values = [r['nestedness_NODF'] for r in results]
    depth_r_values = [r['depth_gradient_r'] for r in results]

    if len(results) >= 5:
        r_corr, p_corr = stats.spearmanr(nodf_values, depth_r_values)
        print(f"\n[P-Eco-4] Nestedness vs depth gradient direction")
        print(f"  Spearman r = {r_corr:+.3f}, p = {p_corr:.4f}")
        print(f"  Prediction: Higher nestedness → more negative depth gradient")
        print(f"  → {'CONFIRMED' if r_corr < 0 and p_corr < 0.05 else 'TREND' if r_corr < 0 else 'DISCONFIRMED'}")

    # Also test: modularity vs depth gradient
    Q_vals = [r['modularity_Q'] for r in results]
    if len(results) >= 5:
        r_corr, p_corr = stats.spearmanr(Q_vals, depth_r_values)
        print(f"\n[P-Eco-4b] Modularity vs depth gradient direction")
        print(f"  Spearman r = {r_corr:+.3f}, p = {p_corr:.4f}")
        print(f"  Prediction: Higher modularity → more positive depth gradient")
        print(f"  → {'CONFIRMED' if r_corr > 0 and p_corr < 0.05 else 'TREND' if r_corr > 0 else 'DISCONFIRMED'}")

    # P-Eco-2/3: Depth gradient sign in nested vs modular groups
    dg_mod = [r['depth_gradient_r'] for r in modular if r['n_trophic_bins'] >= 3]
    dg_nest = [r['depth_gradient_r'] for r in nested if r['n_trophic_bins'] >= 3]

    if len(dg_mod) >= 2 and len(dg_nest) >= 2:
        print(f"\n[P-Eco-2/3] Depth gradient by group:")
        print(f"  Modular mean depth gradient: {np.mean(dg_mod):+.3f} (n={len(dg_mod)})")
        print(f"  Nested mean depth gradient: {np.mean(dg_nest):+.3f} (n={len(dg_nest)})")
        print(f"  P-Eco-2 (nested → negative): {'CONFIRMED' if np.mean(dg_nest) < 0 else 'DISCONFIRMED'}")
        print(f"  P-Eco-3 (modular → positive/flat): {'CONFIRMED' if np.mean(dg_mod) >= 0 else 'DISCONFIRMED'}")
        u_stat, p_val = stats.mannwhitneyu(dg_mod, dg_nest, alternative='greater')
        print(f"  Mann-Whitney U={u_stat:.1f}, p={p_val:.4f}")

    # Overall depth gradient distribution
    all_dg = [r['depth_gradient_r'] for r in results if r['n_trophic_bins'] >= 3]
    if all_dg:
        print(f"\n[Overall] Depth gradient distribution:")
        print(f"  Mean: {np.mean(all_dg):+.3f}")
        print(f"  Positive (accumulation): {sum(1 for x in all_dg if x > 0)}")
        print(f"  Negative (sedimentation): {sum(1 for x in all_dg if x < 0)}")
        print(f"  Range: [{min(all_dg):+.3f}, {max(all_dg):+.3f}]")

    # Save results
    output = {
        'n_foodwebs_analyzed': len(results),
        'results': results,
        'summary': {
            'mean_AF': float(np.mean([r['abelian_fraction'] for r in results])),
            'mean_CV': float(np.mean([r['comm_var'] for r in results])),
            'mean_Q': float(np.mean([r['modularity_Q'] for r in results])),
            'mean_NODF': float(np.mean([r['nestedness_NODF'] for r in results])),
            'n_positive_gradient': sum(1 for r in results if r['depth_gradient_r'] > 0),
            'n_negative_gradient': sum(1 for r in results if r['depth_gradient_r'] < 0),
        }
    }

    outpath = os.path.join(os.path.dirname(__file__), 'eco_killing_form_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved to {outpath}")

    print(f"\n{'='*70}")
    print("CROSS-DOMAIN CORRESPONDENCE")
    print(f"{'='*70}")
    print(f"\nTransformer depth gradient (p=0.012):")
    print(f"  Parallel: mean r = +0.38 (n=3)")
    print(f"  Sequential: mean r = -0.76 (n=7)")
    print(f"\nEcological depth gradient:")
    if dg_mod and dg_nest:
        print(f"  Modular (parallel analog): mean r = {np.mean(dg_mod):+.3f} (n={len(dg_mod)})")
        print(f"  Nested (sequential analog): mean r = {np.mean(dg_nest):+.3f} (n={len(dg_nest)})")
        print(f"\nSame mathematics. Different substrate. Does the pattern hold?")


if __name__ == '__main__':
    main()
