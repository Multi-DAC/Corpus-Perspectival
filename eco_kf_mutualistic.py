"""
Ecological Killing Form — Mutualistic vs Antagonistic Networks

Compares:
  - Food webs (antagonistic, parallel energy flow)
  - Pollination networks (mutualistic, nested generalist-specialist hierarchy)

Hypothesis: Mutualistic networks are more nested/sequential than food webs,
so their depth gradient should be LOWER (more negative or less positive).

For bipartite mutualistic networks, "depth" = degree rank (generalist to specialist).
"""
import numpy as np
from scipy import stats
import json, sys, os

with open(os.path.join(os.path.dirname(__file__), 'foodweb_data', 'weboflife_foodwebs.json')) as f:
    data = json.load(f)

# Parse all networks
fw_networks = {}
mut_networks = {}
for r in data:
    name = r.get('network_name', '')
    if name.startswith('FW_'):
        fw_networks.setdefault(name, []).append(r)
    elif name.startswith('M_PL_'):
        mut_networks.setdefault(name, []).append(r)

def build_matrix(records):
    sp = set()
    for r in records:
        sp.add(r['species1']); sp.add(r['species2'])
    species = sorted(sp)
    idx = {s: i for i, s in enumerate(species)}
    n = len(species)
    A = np.zeros((n, n))
    for r in records:
        i1, i2 = idx[r['species1']], idx[r['species2']]
        w = float(r['connection_strength'])
        A[i2, i1] = w  # species2 interacts with species1
    return A, species

def eco_killing_form(A):
    n = A.shape[0]
    An = A / (np.max(np.abs(A)) + 1e-10)
    W = [np.outer(An[:, i], An[i, :]) for i in range(n)]

    cn = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            C = W[i] @ W[j] - W[j] @ W[i]
            cn[i,j] = cn[j,i] = np.linalg.norm(C, 'fro')

    kf = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            val = 0.0
            for m in range(n):
                Cim = W[i] @ W[m] - W[m] @ W[i]
                Cjm = W[j] @ W[m] - W[m] @ W[j]
                val += np.trace(Cim @ Cjm)
            kf[i,j] = kf[j,i] = val

    eigs = np.sort(np.linalg.eigvalsh(kf))[::-1]
    me = np.max(np.abs(eigs))
    af = np.mean(np.abs(eigs) < 0.1 * me) if me > 0 else 1.0

    upper = cn[np.triu_indices(n, k=1)]
    cv = np.var(upper / np.max(upper)) if np.max(upper) > 0 else 0.0

    return af, cv, cn

def depth_gradient(A, cn):
    """Compute depth gradient using degree-ranked species."""
    n = A.shape[0]
    # Use degree as proxy for "depth" (generalists = deep, specialists = shallow)
    degree = np.sum(A > 0, axis=0) + np.sum(A > 0, axis=1)

    # Rank species by degree and bin into quartiles
    ranks = np.argsort(degree)
    n_bins = min(5, n // 3)
    if n_bins < 3:
        return 0.0, 1.0, 0

    bin_size = n // n_bins
    cvs, bin_centers = [], []

    for b in range(n_bins):
        start = b * bin_size
        end = start + bin_size if b < n_bins - 1 else n
        spp = ranks[start:end]

        norms = [cn[i,j] for i in spp for j in range(n) if j != i]
        if norms and max(norms) > 0:
            cvs.append(np.var([x/max(norms) for x in norms]))
            bin_centers.append(np.mean(degree[spp]))

    if len(cvs) >= 3:
        r, p = stats.spearmanr(bin_centers, cvs)
        return r, p, len(cvs)
    return 0.0, 1.0, 0

def nestedness(A):
    B = (A > 0).astype(float)
    n = B.shape[0]
    rf = np.sum(B, axis=1)
    nodf_r, nr = 0, 0
    for i in range(n):
        for j in range(i+1, n):
            if rf[i] != rf[j] and min(rf[i],rf[j]) > 0:
                mi = i if rf[i] < rf[j] else j
                ma = j if rf[i] < rf[j] else i
                nodf_r += np.sum(B[mi,:] * B[ma,:]) / rf[mi]
                nr += 1
    return nodf_r / nr if nr > 0 else 0.0

def modularity(A):
    B = (A > 0).astype(float)
    Bs = ((B + B.T) > 0).astype(float)
    n = Bs.shape[0]
    m = np.sum(Bs) / 2
    if m == 0: return 0.0
    k = np.sum(Bs, axis=1)
    M = Bs - np.outer(k,k)/(2*m)
    ev, evec = np.linalg.eigh(M)
    v = evec[:, np.argmax(ev)]
    part = (v >= 0).astype(int)
    Q = sum(M[i,j] for i in range(n) for j in range(n) if part[i]==part[j]) / (2*m)
    return float(Q)

# ================================================================
# Run analysis on both types
# ================================================================
print("=" * 70)
print("MUTUALISTIC vs ANTAGONISTIC: Ecological Killing Form")
print("=" * 70)

# Analyze food webs (antagonistic)
print("\n--- FOOD WEBS (antagonistic) ---")
fw_results = []
for name in sorted(fw_networks.keys()):
    recs = fw_networks[name]
    sp = set()
    for r in recs:
        sp.add(r['species1']); sp.add(r['species2'])
    if not (10 <= len(sp) <= 40):
        continue

    A, species = build_matrix(recs)
    n = A.shape[0]
    sys.stdout.write(f"  {name} ({n})... ")
    sys.stdout.flush()

    af, cv, cn = eco_killing_form(A)
    rd, pd, nb = depth_gradient(A, cn)
    Q = modularity(A)
    nodf = nestedness(A)

    print(f"AF={af:.3f} r={rd:+.3f} Q={Q:.3f} NODF={nodf:.3f}")
    fw_results.append({'name': name, 'n': n, 'af': af, 'cv': cv,
                       'depth_r': rd, 'Q': Q, 'nodf': nodf, 'type': 'antagonistic'})

# Analyze mutualistic pollination networks
print("\n--- POLLINATION NETWORKS (mutualistic) ---")
mut_results = []
count = 0
for name in sorted(mut_networks.keys()):
    recs = mut_networks[name]
    sp = set()
    for r in recs:
        sp.add(r['species1']); sp.add(r['species2'])
    if not (10 <= len(sp) <= 35):
        continue
    if count >= 15:  # limit for speed
        break

    A, species = build_matrix(recs)
    n = A.shape[0]
    sys.stdout.write(f"  {name} ({n})... ")
    sys.stdout.flush()

    af, cv, cn = eco_killing_form(A)
    rd, pd, nb = depth_gradient(A, cn)
    Q = modularity(A)
    nodf = nestedness(A)

    print(f"AF={af:.3f} r={rd:+.3f} Q={Q:.3f} NODF={nodf:.3f}")
    mut_results.append({'name': name, 'n': n, 'af': af, 'cv': cv,
                        'depth_r': rd, 'Q': Q, 'nodf': nodf, 'type': 'mutualistic'})
    count += 1

# ================================================================
# Compare
# ================================================================
print("\n" + "=" * 70)
print("COMPARISON: Antagonistic (food webs) vs Mutualistic (pollination)")
print("=" * 70)

fw_dg = [r['depth_r'] for r in fw_results]
mut_dg = [r['depth_r'] for r in mut_results]
fw_af = [r['af'] for r in fw_results]
mut_af = [r['af'] for r in mut_results]
fw_nodf = [r['nodf'] for r in fw_results]
mut_nodf = [r['nodf'] for r in mut_results]

print(f"\nFood webs (n={len(fw_results)}):")
print(f"  Mean depth gradient: {np.mean(fw_dg):+.3f}")
print(f"  Mean AF: {np.mean(fw_af):.3f}")
print(f"  Mean NODF: {np.mean(fw_nodf):.3f}")

print(f"\nPollination (n={len(mut_results)}):")
print(f"  Mean depth gradient: {np.mean(mut_dg):+.3f}")
print(f"  Mean AF: {np.mean(mut_af):.3f}")
print(f"  Mean NODF: {np.mean(mut_nodf):.3f}")

# Statistical comparison
if len(fw_dg) >= 3 and len(mut_dg) >= 3:
    u, p = stats.mannwhitneyu(fw_dg, mut_dg)
    print(f"\nDepth gradient comparison:")
    print(f"  Mann-Whitney U={u:.0f}, p={p:.4f}")

    u2, p2 = stats.mannwhitneyu(fw_af, mut_af)
    print(f"\nAbelian fraction comparison:")
    print(f"  Mann-Whitney U={u2:.0f}, p={p2:.4f}")

    print(f"\n--- Cross-domain ---")
    print(f"Transformer parallel:   mean r = +0.38")
    print(f"Transformer sequential: mean r = -0.76")
    print(f"Food webs:              mean r = {np.mean(fw_dg):+.3f}")
    print(f"Pollination:            mean r = {np.mean(mut_dg):+.3f}")

# Save
all_results = fw_results + mut_results
with open(os.path.join(os.path.dirname(__file__), 'eco_kf_mutualistic_results.json'), 'w') as f:
    json.dump({'fw': fw_results, 'mutualistic': mut_results}, f, indent=2)
