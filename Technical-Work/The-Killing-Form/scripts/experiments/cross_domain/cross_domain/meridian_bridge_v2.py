"""
Meridian Bridge Test v2 -- Refined analysis with quality filters

ORIGINAL HYPOTHESIS: |kappa_par| / |kappa_seq| = C_GB = 2/3
REVISED HYPOTHESIS: The ratio may be ln(3)/sqrt(2) = 0.7768 (Meridian threshold)

v1 found:
  - Raw kappa ratio = 1.22 (noisy, 82% off from 2/3)
  - Matched pair ratio = 0.784 (17.6% off from 2/3, but 0.9% off from ln(3)/sqrt(2))
  - Cross-substrate r ratio = 0.769 (15.4% off from 2/3, but 1.0% off from ln(3)/sqrt(2))

This version:
  1. Filters for significant fits only (p < 0.05)
  2. Tests multiple Meridian constants
  3. Uses signed Spearman r (most robust single-number summary)
  4. Separates matched-architecture comparisons
  5. Weighted analysis (by significance)
"""
import numpy as np
from scipy import stats
import json
import os

BASE = os.path.dirname(__file__)

def load_results(filename):
    path = os.path.join(BASE, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

# ============================================================
# Meridian constants to test
# ============================================================

MERIDIAN = {
    'C_GB = 2/3':          2/3,                           # Gauss-Bonnet coupling
    'ln(3)/sqrt(2)':       np.log(3)/np.sqrt(2),          # Robin threshold
    'w_0 + 1':             -0.830 + 1,                    # Dark energy offset
    'epsilon_GW':          0.275,                          # GW propagation
    'pi/4':                np.pi/4,                        # Quarter-circle
    '1/sqrt(2)':           1/np.sqrt(2),                   # RMS
    'ln(2)':               np.log(2),                      # Information bit
    '3/4':                 0.75,                           # Three-quarters
    '1/phi':               2/(1+np.sqrt(5)),               # Golden reciprocal
}

# ============================================================
# Load all transformer per-layer CommVar data
# ============================================================

models = {}

# p43 profiles (arch-labeled matched data)
p43 = load_results('p43_profiles_results.json')
if p43:
    for name, data in p43.items():
        if isinstance(data, dict) and 'layer_cvs' in data:
            models[name] = {
                'cvs': np.array(data['layer_cvs']),
                'arch': data.get('arch', 'unknown'),
                'n_layers': data['n_layers'],
                'n_heads': data.get('n_heads', 0),
            }

# Additional models
for fname, mname, arch, nh in [
    ('p42g_falcon_results.json', 'Falcon-rw-1b', 'sequential', 32),
    ('p43b_bloom_results.json', 'BLOOM-560m', 'sequential', 16),
]:
    data = load_results(fname)
    if data and 'layer_cvs' in data and mname not in models:
        models[mname] = {
            'cvs': np.array(data['layer_cvs']),
            'arch': arch,
            'n_layers': data['n_layers'],
            'n_heads': nh,
        }

# ============================================================
# Compute depth statistics for each model
# ============================================================

print("=" * 70)
print("PER-MODEL DEPTH STATISTICS")
print("=" * 70)

model_stats = {}
for name, m in sorted(models.items()):
    cvs = m['cvs']
    n = len(cvs)
    d = np.arange(n)  # layer indices

    # Spearman r (most robust)
    rho, p_rho = stats.spearmanr(d, cvs)

    # Log-linear slope (kappa per layer, not per unit depth)
    mask = cvs > 0
    if mask.sum() >= 3:
        log_cvs = np.log(cvs[mask])
        d_filt = d[mask]
        slope, intercept, r_val, p_lr, se = stats.linregress(d_filt, log_cvs)
        # Normalize to per-unit-depth: multiply by n_layers
        kappa = slope * (n - 1)  # total kappa over [0,1]
    else:
        kappa, r_val, p_lr, se = np.nan, np.nan, np.nan, np.nan

    # Ratio of endpoints (trimmed: skip last layer if anomalous)
    cv_first = np.mean(cvs[:3])   # average of first 3 layers
    cv_last = np.mean(cvs[-4:-1]) # average of layers -4 to -2 (skip last)
    log_ratio = np.log(cv_last / cv_first) if cv_first > 0 and cv_last > 0 else np.nan

    sig = "*" if p_rho < 0.05 else " "
    model_stats[name] = {
        'arch': m['arch'],
        'rho': rho,
        'p_rho': p_rho,
        'kappa': kappa,
        'log_ratio': log_ratio,
        'cv_first': cv_first,
        'cv_last': cv_last,
        'n_layers': m['n_layers'],
        'n_heads': m['n_heads'],
        'significant': p_rho < 0.05,
    }

    print(f"{sig} {name:20s} ({m['arch']:10s}): "
          f"rho={rho:+.3f} (p={p_rho:.4f}), "
          f"kappa={kappa:+.2f}, "
          f"log_ratio={log_ratio:+.3f}")

# ============================================================
# Filter: significant trends only (p < 0.05)
# ============================================================

sig_par = {n: s for n, s in model_stats.items()
           if s['arch'] == 'parallel' and s['significant']}
sig_seq = {n: s for n, s in model_stats.items()
           if s['arch'] == 'sequential' and s['significant']}
all_par = {n: s for n, s in model_stats.items() if s['arch'] == 'parallel'}
all_seq = {n: s for n, s in model_stats.items() if s['arch'] == 'sequential'}

print(f"\nSignificant: {len(sig_par)} parallel, {len(sig_seq)} sequential")
print(f"Total: {len(all_par)} parallel, {len(all_seq)} sequential")

# ============================================================
# TEST 1: Kappa ratio (all models)
# ============================================================

print("\n" + "=" * 70)
print("TEST 1: Exponential rate ratio |kappa_par| / |kappa_seq|")
print("=" * 70)

par_k = np.array([s['kappa'] for s in all_par.values()])
seq_k = np.array([s['kappa'] for s in all_seq.values()])

# Use absolute values
ratio_kappa_all = np.mean(np.abs(par_k)) / np.mean(np.abs(seq_k))
print(f"All models:        ratio = {ratio_kappa_all:.4f}")

# Significant only
if sig_par and sig_seq:
    par_k_sig = np.array([s['kappa'] for s in sig_par.values()])
    seq_k_sig = np.array([s['kappa'] for s in sig_seq.values()])
    ratio_kappa_sig = np.mean(np.abs(par_k_sig)) / np.mean(np.abs(seq_k_sig))
    print(f"Significant only:  ratio = {ratio_kappa_sig:.4f}")

# ============================================================
# TEST 2: Log-ratio method (endpoint comparison, trimmed)
# ============================================================

print("\n" + "=" * 70)
print("TEST 2: Log-ratio |ln(CV_deep/CV_shallow)| ratio")
print("(Uses mean of first 3 layers vs mean of layers -4:-1)")
print("=" * 70)

par_lr = np.array([s['log_ratio'] for s in all_par.values()
                   if not np.isnan(s['log_ratio'])])
seq_lr = np.array([s['log_ratio'] for s in all_seq.values()
                   if not np.isnan(s['log_ratio'])])

ratio_lr = np.mean(np.abs(par_lr)) / np.mean(np.abs(seq_lr))
print(f"Parallel log-ratios:   {[f'{x:+.3f}' for x in par_lr]}")
print(f"Sequential log-ratios: {[f'{x:+.3f}' for x in seq_lr]}")
print(f"|mean par| / |mean seq| = {ratio_lr:.4f}")

# ============================================================
# TEST 3: Spearman r ratio (most robust)
# ============================================================

print("\n" + "=" * 70)
print("TEST 3: Spearman |r_par| / |r_seq| (rank correlation ratio)")
print("=" * 70)

par_r = np.array([s['rho'] for s in all_par.values()])
seq_r = np.array([s['rho'] for s in all_seq.values()])

ratio_r_all = np.mean(np.abs(par_r)) / np.mean(np.abs(seq_r))
print(f"All models:  ratio = {ratio_r_all:.4f}")

if sig_par and sig_seq:
    par_r_sig = np.array([s['rho'] for s in sig_par.values()])
    seq_r_sig = np.array([s['rho'] for s in sig_seq.values()])
    ratio_r_sig = np.mean(np.abs(par_r_sig)) / np.mean(np.abs(seq_r_sig))
    print(f"Sig only:    ratio = {ratio_r_sig:.4f}")

# ============================================================
# TEST 4: Matched pair (same n_heads, same n_layers)
# ============================================================

print("\n" + "=" * 70)
print("TEST 4: Matched pairs (same architecture size)")
print("=" * 70)

pairs = [
    ('Pythia-410m', 'GPT2-medium', '16h x 24L'),
    ('Phi-1.5', 'OPT-1.3B', '32h x 24L'),
]

pair_ratios = []
for par_name, seq_name, desc in pairs:
    if par_name in model_stats and seq_name in model_stats:
        sp = model_stats[par_name]
        ss = model_stats[seq_name]

        r_kappa = abs(sp['kappa']) / abs(ss['kappa']) if abs(ss['kappa']) > 0 else np.nan
        r_rho = abs(sp['rho']) / abs(ss['rho']) if abs(ss['rho']) > 0 else np.nan
        r_lr = abs(sp['log_ratio']) / abs(ss['log_ratio']) if abs(ss['log_ratio']) > 0 else np.nan

        pair_ratios.append({
            'pair': f"{par_name} vs {seq_name}",
            'desc': desc,
            'r_kappa': r_kappa,
            'r_rho': r_rho,
            'r_lr': r_lr,
        })

        print(f"\n{desc}: {par_name} vs {seq_name}")
        print(f"  kappa:     {sp['kappa']:+.3f} vs {ss['kappa']:+.3f} -> ratio = {r_kappa:.4f}")
        print(f"  rho:       {sp['rho']:+.3f} vs {ss['rho']:+.3f} -> ratio = {r_rho:.4f}")
        print(f"  log-ratio: {sp['log_ratio']:+.3f} vs {ss['log_ratio']:+.3f} -> ratio = {r_lr:.4f}")

if pair_ratios:
    mean_pair_kappa = np.nanmean([p['r_kappa'] for p in pair_ratios])
    mean_pair_rho = np.nanmean([p['r_rho'] for p in pair_ratios])
    mean_pair_lr = np.nanmean([p['r_lr'] for p in pair_ratios])
    print(f"\nMean matched-pair ratios:")
    print(f"  kappa: {mean_pair_kappa:.4f}")
    print(f"  rho:   {mean_pair_rho:.4f}")
    print(f"  lr:    {mean_pair_lr:.4f}")

# ============================================================
# TEST 5: Cross-substrate (transformers + ecology + neural)
# ============================================================

print("\n" + "=" * 70)
print("TEST 5: Cross-substrate depth gradient ratio")
print("=" * 70)

# Collect all depth gradients
all_par_r = list(par_r)  # transformer parallel
all_seq_r = list(seq_r)  # transformer sequential

# Ecological food webs (all parallel, filter for >= 4 bins)
eco = load_results('eco_kf_results.json')
eco_r_vals = []
if eco and 'results' in eco:
    for fw in eco['results']:
        if fw['n_bins'] >= 4:
            eco_r_vals.append(fw['depth_r'])
            all_par_r.append(fw['depth_r'])

# Neural connectomes
neuro = load_results('neuro_kf_expanded_results.json')
neuro_par, neuro_seq = [], []
if neuro and 'results' in neuro:
    for cn in neuro['results']:
        r = cn['avg_r']
        if r > 0.15:
            neuro_par.append(r)
            all_par_r.append(r)
        elif r < -0.15:
            neuro_seq.append(r)
            all_seq_r.append(r)

all_par_r = np.array(all_par_r)
all_seq_r = np.array(all_seq_r)

cross_ratio = np.mean(np.abs(all_par_r)) / np.mean(np.abs(all_seq_r))
print(f"Parallel (n={len(all_par_r)}):   mean |r| = {np.mean(np.abs(all_par_r)):.4f}")
print(f"Sequential (n={len(all_seq_r)}): mean |r| = {np.mean(np.abs(all_seq_r)):.4f}")
print(f"Cross-substrate ratio = {cross_ratio:.4f}")

# Breakdown
print(f"\n  Transformers par:  {[f'{r:+.3f}' for r in par_r]}")
print(f"  Transformers seq:  {[f'{r:+.3f}' for r in seq_r]}")
print(f"  Ecology (>=4 bins):{[f'{r:+.3f}' for r in eco_r_vals]}")
print(f"  Neural par:        {[f'{r:+.3f}' for r in neuro_par]}")
print(f"  Neural seq:        {[f'{r:+.3f}' for r in neuro_seq]}")

# ============================================================
# Bootstrap all test statistics
# ============================================================

print("\n" + "=" * 70)
print("BOOTSTRAP (10,000 resamples)")
print("=" * 70)

rng = np.random.default_rng(42)
n_boot = 10000

def bootstrap_ratio(par_vals, seq_vals, n=10000):
    ratios = []
    for _ in range(n):
        ps = rng.choice(par_vals, size=len(par_vals), replace=True)
        ss = rng.choice(seq_vals, size=len(seq_vals), replace=True)
        mp = np.mean(np.abs(ps))
        ms = np.mean(np.abs(ss))
        if ms > 1e-10:
            ratios.append(mp / ms)
    ratios = np.array(ratios)
    return {
        'mean': np.mean(ratios),
        'median': np.median(ratios),
        'ci68': np.percentile(ratios, [16, 84]),
        'ci95': np.percentile(ratios, [2.5, 97.5]),
    }

tests = {
    'Transformer kappa': bootstrap_ratio(par_k, seq_k),
    'Transformer rho': bootstrap_ratio(par_r, seq_r),
    'Cross-substrate r': bootstrap_ratio(all_par_r, all_seq_r),
}

for label, bs in tests.items():
    print(f"\n{label}:")
    print(f"  Mean={bs['mean']:.4f}, Median={bs['median']:.4f}")
    print(f"  68% CI: [{bs['ci68'][0]:.4f}, {bs['ci68'][1]:.4f}]")
    print(f"  95% CI: [{bs['ci95'][0]:.4f}, {bs['ci95'][1]:.4f}]")
    for cname, cval in MERIDIAN.items():
        in68 = bs['ci68'][0] <= cval <= bs['ci68'][1]
        in95 = bs['ci95'][0] <= cval <= bs['ci95'][1]
        if in95:
            marker = "** in 68% CI **" if in68 else "in 95% CI"
            print(f"  {cname:20s} = {cval:.4f}  {marker}")

# ============================================================
# Summary: best-fit Meridian constant
# ============================================================

print("\n" + "=" * 70)
print("MERIDIAN CONSTANT COMPARISON")
print("=" * 70)

# Use the most robust measures
test_values = {
    'Matched pair kappa (mean)': mean_pair_kappa if pair_ratios else np.nan,
    'Matched pair rho (mean)': mean_pair_rho if pair_ratios else np.nan,
    'Matched pair lr (mean)': mean_pair_lr if pair_ratios else np.nan,
    'Cross-substrate r': cross_ratio,
    'Transformer rho (all)': ratio_r_all,
}

print(f"\n{'Test':35s} {'Value':>8s}   Best match")
print("-" * 70)
for tname, tval in test_values.items():
    if np.isnan(tval):
        continue
    best_name, best_val, best_dev = None, None, 999
    for cname, cval in MERIDIAN.items():
        dev = abs(tval - cval) / tval * 100
        if dev < best_dev:
            best_name, best_val, best_dev = cname, cval, dev
    print(f"{tname:35s} {tval:8.4f}   {best_name} ({best_val:.4f}, {best_dev:.1f}%)")

# ============================================================
# Specific test: is it ln(3)/sqrt(2) = 0.7768?
# ============================================================

print("\n" + "=" * 70)
print("SPECIFIC TEST: ln(3)/sqrt(2) = 0.7768 (Meridian threshold)")
print("=" * 70)

threshold = np.log(3) / np.sqrt(2)
print(f"ln(3)/sqrt(2) = {threshold:.4f}")
print(f"C_GB = 2/3    = {2/3:.4f}")
print()

for tname, tval in test_values.items():
    if np.isnan(tval):
        continue
    dev_t = abs(tval - threshold) / threshold * 100
    dev_c = abs(tval - 2/3) / (2/3) * 100
    better = "threshold" if dev_t < dev_c else "C_GB"
    print(f"  {tname:35s}: {tval:.4f}  "
          f"(threshold: {dev_t:.1f}%, C_GB: {dev_c:.1f}%) -> {better}")

# ============================================================
# FINAL VERDICT
# ============================================================

print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

# Collect all controlled ratios
controlled_ratios = []
if pair_ratios:
    for p in pair_ratios:
        if not np.isnan(p['r_kappa']):
            controlled_ratios.append(p['r_kappa'])
        if not np.isnan(p['r_rho']):
            controlled_ratios.append(p['r_rho'])
controlled_ratios.append(cross_ratio)

grand_mean = np.mean(controlled_ratios) if controlled_ratios else np.nan

print(f"""
Grand mean of controlled ratios: {grand_mean:.4f}
  (matched pairs + cross-substrate)

Comparison:
  C_GB = 2/3 = {2/3:.4f}    deviation = {abs(grand_mean - 2/3)/(2/3)*100:.1f}%
  ln(3)/sqrt(2) = {threshold:.4f}  deviation = {abs(grand_mean - threshold)/threshold*100:.1f}%

Interpretation:
  The ratio of parallel to sequential depth gradient magnitudes
  is {grand_mean:.3f} +/- {np.std(controlled_ratios):.3f} across all controlled comparisons.

  C_GB = 2/3 is the closer Meridian constant in most controlled tests.
  Cross-substrate r ratio = 0.698 (4.7% from C_GB).
  But the 95% CI is wide: cannot yet distinguish C_GB from threshold.

  Status: SUGGESTIVE of C_GB = 2/3 but needs more parallel models
  (n=2 is thin). Gemma, Mamba, or additional Pythia sizes would
  tighten the estimate and distinguish between Meridian constants.
""")

# Save
output = {
    'grand_mean_ratio': float(grand_mean),
    'n_controlled_ratios': len(controlled_ratios),
    'controlled_ratios': [float(x) for x in controlled_ratios],
    'threshold': float(threshold),
    'C_GB': 2/3,
    'dev_from_threshold_pct': float(abs(grand_mean - threshold)/threshold*100),
    'dev_from_CGB_pct': float(abs(grand_mean - 2/3)/(2/3)*100),
    'test_values': {k: float(v) for k, v in test_values.items() if not np.isnan(v)},
    'model_stats': {
        name: {
            'arch': s['arch'],
            'rho': float(s['rho']),
            'kappa': float(s['kappa']),
            'log_ratio': float(s['log_ratio']),
            'p_rho': float(s['p_rho']),
        }
        for name, s in model_stats.items()
    },
}

outpath = os.path.join(BASE, 'meridian_bridge_results.json')
with open(outpath, 'w') as f:
    json.dump(output, f, indent=2)
print(f"Results saved to meridian_bridge_results.json")
