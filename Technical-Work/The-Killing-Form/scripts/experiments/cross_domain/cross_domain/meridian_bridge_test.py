"""
Meridian Bridge Test -- Does C_GB = 2/3 predict the depth gradient ratio?

HYPOTHESIS: The ratio of parallel growth rate to sequential decay rate
equals the Gauss-Bonnet coupling constant C_GB = 2/3.

From Meridian Phase 1:
  C_GB = 2/3 is the P-tensor fraction in the 5D Gauss-Bonnet term.
  It governs the intrinsic-extrinsic coupling in the warped brane geometry.

Physical interpretation:
  Parallel systems preserve ONLY voluntary constraints -> warp rate = C_GB * k
  Sequential systems use ALL constraint types -> warp rate = full k
  Hence |kappa_par| / |kappa_seq| = C_GB = 2/3

Method:
  1. Load per-layer CommVar profiles from all transformer experiments
  2. Fit exponential CommVar(d) = C0 * exp(kappa * d) to each model
  3. Extract kappa for parallel and sequential families
  4. Test whether |mean_kappa_par| / |mean_kappa_seq| = 2/3
  5. Bootstrap confidence interval
  6. Cross-substrate check with ecological and neural data
"""
import numpy as np
from scipy import stats, optimize
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
# 1. Collect all models with per-layer CommVar data
# ============================================================

models = {}

# p43_profiles_results.json -- matched pairs with arch labels
p43 = load_results('p43_profiles_results.json')
if p43:
    for name, data in p43.items():
        if isinstance(data, dict) and 'layer_cvs' in data and 'arch' in data:
            models[name] = {
                'layer_cvs': np.array(data['layer_cvs']),
                'arch': data['arch'],
                'n_layers': data['n_layers'],
                'source': 'p43'
            }

# Individual experiment files (skip if already in p43)
for fname, model_name, arch in [
    ('p42g_falcon_results.json', 'Falcon-rw-1b', 'sequential'),
    ('p43b_bloom_results.json', 'BLOOM-560m', 'sequential'),
]:
    data = load_results(fname)
    if data and 'layer_cvs' in data:
        if model_name not in models:
            models[model_name] = {
                'layer_cvs': np.array(data['layer_cvs']),
                'arch': arch,
                'n_layers': data['n_layers'],
                'source': fname
            }

print(f"Loaded {len(models)} models with per-layer CommVar data\n")
for name, m in sorted(models.items()):
    cvs = m['layer_cvs']
    print(f"  {name}: {m['n_layers']}L, arch={m['arch']}, "
          f"CV range [{cvs.min():.2e}, {cvs.max():.2e}]")

# ============================================================
# 2. Fit exponential profiles: CommVar(d) = C0 * exp(kappa * d)
# ============================================================

def fit_exponential_loglin(layer_cvs, trim_last=False):
    """Log-linear regression: ln(CV) = ln(C0) + kappa * d.
    d normalized to [0, 1].
    """
    cvs = layer_cvs[:-1] if trim_last else layer_cvs
    n = len(cvs)
    d = np.linspace(0, 1, n)

    mask = cvs > 0
    if mask.sum() < 3:
        return None

    log_cv = np.log(cvs[mask])
    d_filt = d[mask]

    slope, intercept, r_value, p_value, std_err = stats.linregress(d_filt, log_cv)
    rho, p_spear = stats.spearmanr(d_filt, log_cv)

    return {
        'kappa': slope,
        'C0': np.exp(intercept),
        'r_squared': r_value ** 2,
        'pearson_r': r_value,
        'spearman_r': rho,
        'p_value': p_value,
        'std_err': std_err,
        'cv_ratio': float(cvs[-1] / cvs[0]) if cvs[0] > 0 else float('nan'),
        'n_points': int(mask.sum())
    }


def fit_exponential_robust(layer_cvs, trim_last=False):
    """Nonlinear least squares fit of C0 * exp(kappa * d)."""
    cvs = layer_cvs[:-1] if trim_last else layer_cvs
    n = len(cvs)
    d = np.linspace(0, 1, n)

    mask = cvs > 0
    if mask.sum() < 3:
        return None

    try:
        def exp_model(x, C0, kappa):
            return C0 * np.exp(kappa * x)

        log_fit = stats.linregress(d[mask], np.log(cvs[mask]))
        p0 = [np.exp(log_fit.intercept), log_fit.slope]

        popt, pcov = optimize.curve_fit(exp_model, d[mask], cvs[mask],
                                        p0=p0, maxfev=10000)
        C0_r, kappa_r = popt

        predicted = exp_model(d[mask], *popt)
        ss_res = np.sum((cvs[mask] - predicted) ** 2)
        ss_tot = np.sum((cvs[mask] - np.mean(cvs[mask])) ** 2)
        r_sq = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        return {
            'kappa': kappa_r,
            'C0': C0_r,
            'r_squared': r_sq,
            'std_err': float(np.sqrt(pcov[1, 1])) if pcov[1, 1] > 0 else float('nan')
        }
    except Exception:
        return None


print("\n" + "=" * 70)
print("EXPONENTIAL PROFILE FITTING")
print("CommVar(d) = C0 * exp(kappa * d),  d in [0,1]")
print("=" * 70)

results = {}
for name, m in sorted(models.items()):
    # Fit with and without last layer (last layer often anomalous)
    fit_full = fit_exponential_loglin(m['layer_cvs'], trim_last=False)
    fit_trim = fit_exponential_loglin(m['layer_cvs'], trim_last=True)
    fit_rob = fit_exponential_robust(m['layer_cvs'], trim_last=False)

    if fit_full:
        # Use trimmed fit if last-layer effect is large
        last_cv = m['layer_cvs'][-1]
        penult_cv = m['layer_cvs'][-2]
        last_layer_jump = abs(last_cv - penult_cv) / (penult_cv + 1e-20)

        results[name] = {
            'arch': m['arch'],
            'kappa_full': fit_full['kappa'],
            'kappa_trim': fit_trim['kappa'] if fit_trim else np.nan,
            'kappa_robust': fit_rob['kappa'] if fit_rob else np.nan,
            'R2_full': fit_full['r_squared'],
            'R2_robust': fit_rob['r_squared'] if fit_rob else np.nan,
            'spearman_r': fit_full['spearman_r'],
            'p_value': fit_full['p_value'],
            'cv_ratio': fit_full['cv_ratio'],
            'last_layer_jump': last_layer_jump,
            'n_layers': m['n_layers'],
        }

        print(f"\n{name} ({m['arch']}, {m['n_layers']}L):")
        print(f"  kappa (log-lin): {fit_full['kappa']:+.3f}  "
              f"(trimmed: {fit_trim['kappa']:+.3f})" if fit_trim else "")
        if fit_rob:
            print(f"  kappa (robust):  {fit_rob['kappa']:+.3f}  "
                  f"R2={fit_rob['r_squared']:.3f}")
        print(f"  R2={fit_full['r_squared']:.3f}, "
              f"Spearman r={fit_full['spearman_r']:+.3f}, "
              f"p={fit_full['p_value']:.4g}")
        print(f"  CV ratio (last/first) = {fit_full['cv_ratio']:.3f}")
        if last_layer_jump > 1.0:
            print(f"  ** Last-layer jump: {last_layer_jump:.1f}x **")

# ============================================================
# 3. THE TEST: |kappa_par| / |kappa_seq| = C_GB = 2/3 ?
# ============================================================

print("\n" + "=" * 70)
print("THE MERIDIAN BRIDGE TEST")
print("H0: |kappa_par| / |kappa_seq| = C_GB = 2/3 = 0.6667")
print("=" * 70)

C_GB = 2 / 3

# Separate by architecture
par_kappas, seq_kappas = [], []
par_names, seq_names = [], []

for name, r in results.items():
    k = r['kappa_full']
    if r['arch'] == 'parallel':
        par_kappas.append(k)
        par_names.append(name)
    else:
        seq_kappas.append(k)
        seq_names.append(name)

par_kappas = np.array(par_kappas)
seq_kappas = np.array(seq_kappas)

print(f"\nParallel models (n={len(par_kappas)}):")
for n, k in zip(par_names, par_kappas):
    print(f"  {n}: kappa = {k:+.4f}")
if len(par_kappas) > 0:
    print(f"  Mean: {np.mean(par_kappas):+.4f} +/- {np.std(par_kappas):.4f}")
    print(f"  |Mean|: {np.mean(np.abs(par_kappas)):.4f}")

print(f"\nSequential models (n={len(seq_kappas)}):")
for n, k in zip(seq_names, seq_kappas):
    print(f"  {n}: kappa = {k:+.4f}")
if len(seq_kappas) > 0:
    print(f"  Mean: {np.mean(seq_kappas):+.4f} +/- {np.std(seq_kappas):.4f}")
    print(f"  |Mean|: {np.mean(np.abs(seq_kappas)):.4f}")

mean_par = np.mean(np.abs(par_kappas))
mean_seq = np.mean(np.abs(seq_kappas))
ratio = mean_par / mean_seq if mean_seq > 0 else float('nan')

print(f"\n--- PRIMARY RESULT ---")
print(f"|mean kappa_par| = {mean_par:.4f}")
print(f"|mean kappa_seq| = {mean_seq:.4f}")
print(f"Ratio            = {ratio:.4f}")
print(f"C_GB             = {C_GB:.4f}")
print(f"Deviation        = {abs(ratio - C_GB) / C_GB * 100:.1f}%")

# Also with trimmed kappas (removing last-layer anomalies)
par_trim = np.array([results[n]['kappa_trim'] for n in par_names
                     if not np.isnan(results[n]['kappa_trim'])])
seq_trim = np.array([results[n]['kappa_trim'] for n in seq_names
                     if not np.isnan(results[n]['kappa_trim'])])
if len(par_trim) > 0 and len(seq_trim) > 0:
    ratio_trim = np.mean(np.abs(par_trim)) / np.mean(np.abs(seq_trim))
    print(f"\nTrimmed (no last layer):")
    print(f"  Ratio = {ratio_trim:.4f}, Dev = {abs(ratio_trim - C_GB) / C_GB * 100:.1f}%")

# With robust kappas
par_rob = np.array([results[n]['kappa_robust'] for n in par_names
                    if not np.isnan(results[n]['kappa_robust'])])
seq_rob = np.array([results[n]['kappa_robust'] for n in seq_names
                    if not np.isnan(results[n]['kappa_robust'])])
if len(par_rob) > 0 and len(seq_rob) > 0:
    ratio_rob = np.mean(np.abs(par_rob)) / np.mean(np.abs(seq_rob))
    print(f"\nRobust (nonlinear LS):")
    print(f"  Ratio = {ratio_rob:.4f}, Dev = {abs(ratio_rob - C_GB) / C_GB * 100:.1f}%")

# ============================================================
# 4. Bootstrap confidence interval
# ============================================================

print("\n" + "=" * 70)
print("BOOTSTRAP CONFIDENCE INTERVAL (10,000 resamples)")
print("=" * 70)

n_boot = 10000
boot_ratios = []
rng = np.random.default_rng(42)

for _ in range(n_boot):
    ps = rng.choice(par_kappas, size=len(par_kappas), replace=True)
    ss = rng.choice(seq_kappas, size=len(seq_kappas), replace=True)
    mp = np.mean(np.abs(ps))
    ms = np.mean(np.abs(ss))
    if ms > 0:
        boot_ratios.append(mp / ms)

boot_ratios = np.array(boot_ratios)
ci_lo, ci_hi = np.percentile(boot_ratios, [2.5, 97.5])
ci_68_lo, ci_68_hi = np.percentile(boot_ratios, [16, 84])

print(f"Bootstrap mean:  {np.mean(boot_ratios):.4f}")
print(f"Bootstrap median:{np.median(boot_ratios):.4f}")
print(f"68% CI: [{ci_68_lo:.4f}, {ci_68_hi:.4f}]")
print(f"95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"C_GB = {C_GB:.4f}")
print(f"C_GB within 68% CI: {ci_68_lo <= C_GB <= ci_68_hi}")
print(f"C_GB within 95% CI: {ci_lo <= C_GB <= ci_hi}")

# ============================================================
# 5. Matched pair analysis (same n_heads, same n_layers)
# ============================================================

print("\n" + "=" * 70)
print("MATCHED PAIR: Pythia-410m vs GPT2-medium")
print("(Same n_heads=16, same n_layers=24)")
print("=" * 70)

if 'Pythia-410m' in results and 'GPT2-medium' in results:
    kp = results['Pythia-410m']['kappa_full']
    ks = results['GPT2-medium']['kappa_full']
    ratio_m = abs(kp) / abs(ks)

    print(f"Pythia-410m (parallel):   kappa = {kp:+.4f}")
    print(f"GPT2-medium (sequential): kappa = {ks:+.4f}")
    print(f"|kappa_par| / |kappa_seq| = {ratio_m:.4f}")
    print(f"C_GB = {C_GB:.4f}")
    print(f"Deviation = {abs(ratio_m - C_GB) / C_GB * 100:.1f}%")
else:
    ratio_m = float('nan')

# ============================================================
# 6. Cross-substrate: ecological + neural depth gradients
# ============================================================

print("\n" + "=" * 70)
print("CROSS-SUBSTRATE: Depth gradient ratios")
print("Using Spearman r as proxy for exponential rate sign/magnitude")
print("=" * 70)

# Transformer Spearman r values from the data
transformer_par_r = []
transformer_seq_r = []
for name, r in results.items():
    sr = r['spearman_r']
    if r['arch'] == 'parallel':
        transformer_par_r.append(sr)
    else:
        transformer_seq_r.append(sr)

# Ecological: food webs are parallel (from eco_kf_results.json)
eco_data = load_results('eco_kf_results.json')
eco_r = []
if eco_data and 'results' in eco_data:
    for fw in eco_data['results']:
        if fw['n_bins'] >= 3:  # need at least 3 depth bins
            eco_r.append(fw['depth_r'])

# Neural: from neuro_kf_expanded_results.json
neuro_data = load_results('neuro_kf_expanded_results.json')
neuro_par_r, neuro_seq_r = [], []
if neuro_data and 'results' in neuro_data:
    # Classify by sign of avg_r
    for cn in neuro_data['results']:
        r_val = cn['avg_r']
        if r_val > 0.1:
            neuro_par_r.append(r_val)
        elif r_val < -0.1:
            neuro_seq_r.append(r_val)

print(f"Transformer parallel r:  {[f'{r:+.3f}' for r in transformer_par_r]}")
print(f"Transformer sequential r:{[f'{r:+.3f}' for r in transformer_seq_r]}")
print(f"Ecological r (parallel): {[f'{r:+.3f}' for r in eco_r]}")
print(f"Neural parallel r:       {[f'{r:+.3f}' for r in neuro_par_r]}")
print(f"Neural sequential r:     {[f'{r:+.3f}' for r in neuro_seq_r]}")

# All parallel vs all sequential
all_par = transformer_par_r + eco_r + neuro_par_r
all_seq = transformer_seq_r + neuro_seq_r

if all_par and all_seq:
    mp = np.mean(np.abs(all_par))
    ms = np.mean(np.abs(all_seq))
    cross_ratio = mp / ms
    print(f"\nAll parallel (n={len(all_par)}):  mean |r| = {mp:.4f}")
    print(f"All sequential (n={len(all_seq)}): mean |r| = {ms:.4f}")
    print(f"Ratio = {cross_ratio:.4f}")
    print(f"C_GB  = {C_GB:.4f}")
    print(f"Deviation = {abs(cross_ratio - C_GB) / C_GB * 100:.1f}%")
else:
    cross_ratio = float('nan')

# ============================================================
# 7. Is C_GB = 2/3 the ONLY special value near the ratio?
# ============================================================

print("\n" + "=" * 70)
print("ALTERNATIVE HYPOTHESES")
print("=" * 70)

alternatives = {
    'C_GB = 2/3': 2 / 3,
    '1/phi (golden)': 1 / ((1 + np.sqrt(5)) / 2),
    'ln(2)': np.log(2),
    '1/sqrt(2)': 1 / np.sqrt(2),
    'pi/4': np.pi / 4,
    '1/e': 1 / np.e,
    'sqrt(2)-1': np.sqrt(2) - 1,
    '1/2': 0.5,
    '3/4': 0.75,
}

print(f"Empirical ratio = {ratio:.4f}\n")
for label, val in sorted(alternatives.items(), key=lambda x: abs(x[1] - ratio)):
    dev = abs(val - ratio) / ratio * 100
    marker = " <--" if label == 'C_GB = 2/3' else ""
    print(f"  {label:20s} = {val:.4f}  (dev {dev:5.1f}%){marker}")

# ============================================================
# 8. Summary
# ============================================================

print("\n" + "=" * 70)
print("MERIDIAN BRIDGE TEST -- SUMMARY")
print("=" * 70)

print(f"""
Does C_GB = 2/3 from the 5D brane geometry predict the ratio of
parallel growth rate to sequential decay rate?

                                Ratio    C_GB     Dev
Transformers (log-linear):      {ratio:.4f}   {C_GB:.4f}   {abs(ratio - C_GB) / C_GB * 100:5.1f}%
Matched pair (Pythia/GPT2):     {ratio_m:.4f}   {C_GB:.4f}   {abs(ratio_m - C_GB) / C_GB * 100:5.1f}%
Cross-substrate (all r):        {cross_ratio:.4f}   {C_GB:.4f}   {abs(cross_ratio - C_GB) / C_GB * 100:5.1f}%

Bootstrap 95% CI (transformers): [{ci_lo:.4f}, {ci_hi:.4f}]
C_GB within 95% CI: {ci_lo <= C_GB <= ci_hi}

If confirmed:
  The Gauss-Bonnet coupling C_GB = 2/3 -- which determines the warping
  of the 5D brane geometry in Project Meridian -- ALSO determines the
  ratio of algebraic accumulation to sedimentation across substrates.

  Parallel: warp rate = C_GB * k_full = (2/3) * k_full (voluntary only)
  Sequential: warp rate = k_full (all constraints)
  Ratio = C_GB = 2/3
""")

# ============================================================
# Save results
# ============================================================

output = {
    'C_GB': C_GB,
    'transformer_ratio': float(ratio),
    'matched_pair_ratio': float(ratio_m),
    'cross_substrate_ratio': float(cross_ratio) if not np.isnan(cross_ratio) else None,
    'bootstrap_mean': float(np.mean(boot_ratios)),
    'bootstrap_95_CI': [float(ci_lo), float(ci_hi)],
    'bootstrap_68_CI': [float(ci_68_lo), float(ci_68_hi)],
    'C_GB_within_95_CI': bool(ci_lo <= C_GB <= ci_hi),
    'parallel_models': {
        n: {'kappa': float(k), 'r': float(results[n]['spearman_r'])}
        for n, k in zip(par_names, par_kappas)
    },
    'sequential_models': {
        n: {'kappa': float(k), 'r': float(results[n]['spearman_r'])}
        for n, k in zip(seq_names, seq_kappas)
    },
}

outpath = os.path.join(BASE, 'meridian_bridge_results.json')
with open(outpath, 'w') as f:
    json.dump(output, f, indent=2)
print(f"Results saved to meridian_bridge_results.json")
