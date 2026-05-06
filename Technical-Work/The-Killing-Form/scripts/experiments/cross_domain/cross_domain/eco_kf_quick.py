"""Quick ecological Killing form test on small food webs."""
import numpy as np
from scipy import stats
import json, sys, os

# Load Web of Life food webs
with open(os.path.join(os.path.dirname(__file__), 'foodweb_data', 'weboflife_foodwebs.json')) as f:
    data = json.load(f)

networks = {}
for r in data:
    name = r.get('network_name', '')
    if name.startswith('FW_'):
        if name not in networks:
            networks[name] = []
        networks[name].append(r)

def build_matrix(records):
    sp = set()
    for r in records:
        sp.add(r['species1']); sp.add(r['species2'])
    species = sorted(sp)
    idx = {s: i for i, s in enumerate(species)}
    n = len(species)
    A = np.zeros((n, n))
    for r in records:
        A[idx[r['species2']], idx[r['species1']]] = float(r['connection_strength'])
    return A, species

def trophic_levels(A):
    n = A.shape[0]
    TL = np.ones(n)
    for _ in range(100):
        old = TL.copy()
        for i in range(n):
            prey = np.where(A[i,:] > 0)[0]
            if len(prey) > 0:
                TL[i] = 1 + np.average(old[prey], weights=A[i,prey])
        if np.max(np.abs(TL - old)) < 1e-6:
            break
    return TL

def eco_killing_form(A):
    n = A.shape[0]
    An = A / (np.max(np.abs(A)) + 1e-10)

    # Interaction operators: W_i = outer(effects_of_i, effects_on_i)
    W = [np.outer(An[:, i], An[i, :]) for i in range(n)]

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

    eigs = np.sort(np.linalg.eigvalsh(kf))[::-1]
    me = np.max(np.abs(eigs))
    af = np.mean(np.abs(eigs) < 0.1 * me) if me > 0 else 1.0

    upper = cn[np.triu_indices(n, k=1)]
    cv = np.var(upper / np.max(upper)) if np.max(upper) > 0 else 0.0

    return af, cv, cn

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

# Filter to manageable size (n <= 50)
small_fws = {}
for name, recs in networks.items():
    sp = set()
    for r in recs:
        sp.add(r['species1']); sp.add(r['species2'])
    if 10 <= len(sp) <= 50:
        small_fws[name] = recs

print(f"Testing {len(small_fws)} food webs (10-50 species)")
print()

results = []
for name in sorted(small_fws.keys()):
    A, species = build_matrix(small_fws[name])
    n = A.shape[0]

    sys.stdout.write(f"  {name} ({n} sp)... ")
    sys.stdout.flush()

    af, cv, cn = eco_killing_form(A)
    TL = trophic_levels(A)
    Q = modularity(A)
    nodf = nestedness(A)

    # Depth gradient: CommVar at each trophic level
    tl_bins = np.round(TL * 2) / 2
    ubins = np.sort(np.unique(tl_bins))
    tl_cvs, tl_vals = [], []
    for b in ubins:
        spp = np.where(tl_bins == b)[0]
        if len(spp) < 2:
            continue
        norms = [cn[i,j] for i in spp for j in range(n) if j != i]
        if norms and max(norms) > 0:
            tl_cvs.append(np.var([x/max(norms) for x in norms]))
            tl_vals.append(float(b))

    if len(tl_cvs) >= 3:
        rd, pd = stats.spearmanr(tl_vals, tl_cvs)
    else:
        rd, pd = 0.0, 1.0

    print(f"AF={af:.3f} CV={cv:.6f} r={rd:+.3f} Q={Q:.3f} NODF={nodf:.3f} TL=[{np.min(TL):.1f}-{np.max(TL):.1f}]")

    results.append({
        'name': name, 'n': n, 'af': af, 'cv': cv,
        'depth_r': rd, 'depth_p': pd,
        'Q': Q, 'nodf': nodf,
        'connectance': float(np.sum(A > 0) / (n*n)),
        'n_bins': len(tl_cvs),
        'tl_range': [float(np.min(TL)), float(np.max(TL))]
    })

# Also try edge-list food webs
data_dir = os.path.join(os.path.dirname(__file__), 'foodweb_data')
for efile in ['eco-stmarks.edges']:
    epath = os.path.join(data_dir, efile)
    if not os.path.exists(epath):
        continue
    edges, nodes = [], set()
    with open(epath) as f:
        for line in f:
            p = line.strip().split()
            if len(p) >= 2:
                s, t = int(p[0]), int(p[1])
                w = float(p[2]) if len(p) >= 3 else 1.0
                edges.append((s,t,w)); nodes.add(s); nodes.add(t)
    nl = sorted(nodes)
    idx = {nd:i for i,nd in enumerate(nl)}
    n = len(nl)
    A = np.zeros((n,n))
    for s,t,w in edges:
        A[idx[t], idx[s]] = w

    sys.stdout.write(f"  {efile} ({n} sp)... ")
    sys.stdout.flush()

    af, cv, cn = eco_killing_form(A)
    TL = trophic_levels(A)
    Q = modularity(A)
    nodf = nestedness(A)

    tl_bins = np.round(TL * 2) / 2
    ubins = np.sort(np.unique(tl_bins))
    tl_cvs, tl_vals = [], []
    for b in ubins:
        spp = np.where(tl_bins == b)[0]
        if len(spp) < 2: continue
        norms = [cn[i,j] for i in spp for j in range(n) if j != i]
        if norms and max(norms) > 0:
            tl_cvs.append(np.var([x/max(norms) for x in norms]))
            tl_vals.append(float(b))

    if len(tl_cvs) >= 3:
        rd, pd = stats.spearmanr(tl_vals, tl_cvs)
    else:
        rd, pd = 0.0, 1.0

    print(f"AF={af:.3f} CV={cv:.6f} r={rd:+.3f} Q={Q:.3f} NODF={nodf:.3f}")
    results.append({
        'name': efile, 'n': n, 'af': af, 'cv': cv,
        'depth_r': rd, 'depth_p': pd, 'Q': Q, 'nodf': nodf,
        'connectance': float(np.sum(A>0)/(n*n)), 'n_bins': len(tl_cvs),
        'tl_range': [float(np.min(TL)), float(np.max(TL))]
    })

# ================================================================
# SUMMARY & PREDICTION TESTS
# ================================================================
print()
print("=" * 70)
print(f"RESULTS: {len(results)} food webs analyzed")
print("=" * 70)

print(f"\n{'Name':<20} {'n':>4} {'Q':>6} {'NODF':>6} {'AF':>6} {'CV':>10} {'r(depth)':>9}")
print("-" * 65)
for r in sorted(results, key=lambda x: x['Q'], reverse=True):
    print(f"{r['name']:<20} {r['n']:>4} {r['Q']:>6.3f} {r['nodf']:>6.3f} "
          f"{r['af']:>6.3f} {r['cv']:>10.6f} {r['depth_r']:>+9.3f}")

# Median split on modularity
Qmed = np.median([r['Q'] for r in results])
mod_group = [r for r in results if r['Q'] > Qmed]
nest_group = [r for r in results if r['Q'] <= Qmed]

print(f"\nMedian Q = {Qmed:.3f}")
print(f"High-modularity: n={len(mod_group)}, Low-modularity: n={len(nest_group)}")

# P-Eco-1
af_m = [r['af'] for r in mod_group]
af_n = [r['af'] for r in nest_group]
print(f"\n[P-Eco-1] Modular AF: {np.mean(af_m):.3f} ± {np.std(af_m):.3f}")
print(f"          Nested AF:  {np.mean(af_n):.3f} ± {np.std(af_n):.3f}")
if len(af_m) >= 2 and len(af_n) >= 2:
    u, p = stats.mannwhitneyu(af_m, af_n, alternative='greater')
    status = "CONFIRMED" if p < 0.05 else "TREND" if p < 0.1 else "not significant"
    print(f"  Mann-Whitney U={u:.0f}, p={p:.4f} -> {status}")

# P-Eco-2/3
dg_m = [r['depth_r'] for r in mod_group if r['n_bins'] >= 3]
dg_n = [r['depth_r'] for r in nest_group if r['n_bins'] >= 3]

if dg_m and dg_n:
    print(f"\n[P-Eco-2] Nested depth gradient:  mean = {np.mean(dg_n):+.3f} (n={len(dg_n)})")
    print(f"  Prediction (negative): {'CONFIRMED' if np.mean(dg_n) < 0 else 'DISCONFIRMED'}")
    print(f"\n[P-Eco-3] Modular depth gradient: mean = {np.mean(dg_m):+.3f} (n={len(dg_m)})")
    print(f"  Prediction (positive/flat): {'CONFIRMED' if np.mean(dg_m) >= -0.1 else 'DISCONFIRMED'}")

    if len(dg_m) >= 2 and len(dg_n) >= 2:
        u, p = stats.mannwhitneyu(dg_m, dg_n, alternative='greater')
        print(f"  Mann-Whitney U={u:.0f}, p={p:.4f}")

# P-Eco-4
usable = [r for r in results if r['n_bins'] >= 3]
if len(usable) >= 5:
    qs = [r['Q'] for r in usable]
    drs = [r['depth_r'] for r in usable]
    rc, pc = stats.spearmanr(qs, drs)
    print(f"\n[P-Eco-4] Modularity vs depth gradient: r = {rc:+.3f}, p = {pc:.4f}")
    print(f"  Prediction (positive correlation): {'CONFIRMED' if rc > 0 and pc < 0.05 else 'TREND' if rc > 0 else 'DISCONFIRMED'}")

    ns = [r['nodf'] for r in usable]
    rc2, pc2 = stats.spearmanr(ns, drs)
    print(f"\n[P-Eco-4b] Nestedness vs depth gradient: r = {rc2:+.3f}, p = {pc2:.4f}")
    print(f"  Prediction (negative correlation): {'CONFIRMED' if rc2 < 0 and pc2 < 0.05 else 'TREND' if rc2 < 0 else 'DISCONFIRMED'}")

# Cross-domain comparison
print(f"\n{'='*70}")
print("CROSS-DOMAIN COMPARISON")
print(f"{'='*70}")
print(f"\nTransformer (11 models, 5 labs):")
print(f"  Parallel:   mean depth gradient r = +0.38 (n=3)")
print(f"  Sequential: mean depth gradient r = -0.76 (n=7)")
print(f"  Mann-Whitney p = 0.012")
if dg_m and dg_n:
    print(f"\nEcology ({len(results)} food webs):")
    print(f"  Modular (parallel analog):    mean r = {np.mean(dg_m):+.3f} (n={len(dg_m)})")
    print(f"  Nested (sequential analog):   mean r = {np.mean(dg_n):+.3f} (n={len(dg_n)})")

# Save
with open(os.path.join(os.path.dirname(__file__), 'eco_kf_results.json'), 'w') as f:
    json.dump({'n_analyzed': len(results), 'results': results}, f, indent=2)
print(f"\nResults saved to eco_kf_results.json")
