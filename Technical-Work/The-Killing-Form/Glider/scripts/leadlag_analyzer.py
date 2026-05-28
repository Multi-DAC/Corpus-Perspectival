"""
Lead/lag analyzer — does structure-formation LEAD capability-emergence?
=======================================================================
Phase-1 observational tool from INSIDE_ANALYSIS_PROTOCOL.md. Consumes the
trajectory.json files emitted by train_kf_gated_hrm_easy.py.

For each arm: extract structure trajectory (Killing-CV, H/L ratio) and capability
trajectory (exact/token accuracy) over training steps. Compute the cross-correlation
between structure and capability at integer eval-step lags; the lag maximizing
correlation is the lead/lag. Positive lag = structure LEADS capability (fingerprint
that structure does causal work). Also: arm-vs-arm divergence step + final delta.

HONEST CAVEATS (printed in output):
- Eval points are sparse (~15 for a 15k-step run) -> lead/lag is SUGGESTIVE, coarse
  (resolution = one eval interval), not a rigorous causal claim.
- Correlation != causation. This is OBSERVATIONAL only. Causal direction needs the
  Phase-2 interventions (freeze/inject/ablate). This tool generates the hypothesis;
  interventions test it.

Usage: python3 leadlag_analyzer.py [results_dir]
"""
import sys, os, json, glob, math

RESULTS = sys.argv[1] if len(sys.argv) > 1 else '/home/clawd/path_a_results'


def load_series(path):
    if not os.path.exists(path):
        return None
    d = json.load(open(path))
    pts = [t for t in d.get('trajectory', []) if 'exact_accuracy' in t]
    if not pts:
        return None
    return {
        'step':  [t['global_step'] for t in pts],
        'exact': [t['exact_accuracy'] for t in pts],
        'token': [t['token_accuracy'] for t in pts],
        'h_cv':  [t.get('H_cv', float('nan')) for t in pts],
        'ratio': [t.get('h_l_ratio', float('nan')) for t in pts],
    }


def _z(x):
    x = [v for v in x]
    n = len(x)
    m = sum(x) / n
    var = sum((v - m) ** 2 for v in x) / n
    sd = math.sqrt(var) if var > 1e-12 else 0.0
    return [(v - m) / sd for v in x] if sd > 0 else [0.0] * n


def xcorr_best_lag(struct, cap, max_lag=None):
    """Normalized cross-correlation of struct vs cap over integer lags.
    lag k>0 means struct[t] correlates with cap[t+k] -> struct LEADS cap by k evals."""
    n = len(struct)
    if n < 4:
        return None
    if max_lag is None:
        max_lag = min(5, n // 2)
    zs, zc = _z(struct), _z(cap)
    best = None
    table = []
    for k in range(-max_lag, max_lag + 1):
        # overlap of zs[i] with zc[i+k]
        pairs = [(zs[i], zc[i + k]) for i in range(n) if 0 <= i + k < n]
        if len(pairs) < 3:
            continue
        c = sum(a * b for a, b in pairs) / len(pairs)
        table.append((k, c))
        if best is None or abs(c) > abs(best[1]):
            best = (k, c)
    return {'best_lag': best[0], 'best_corr': best[1], 'table': table}


def first_cross(steps, vals, thresh):
    for s, v in zip(steps, vals):
        if v >= thresh:
            return s
    return None


def analyze_arm(name, s):
    print(f"\n--- {name} ---")
    print(f"  evals: {len(s['step'])}  steps {s['step'][0]}..{s['step'][-1]}")
    print(f"  final: exact={s['exact'][-1]:.4f} token={s['token'][-1]:.4f} "
          f"H_CV={s['h_cv'][-1]:.3e} ratio={s['ratio'][-1]:.3f}")
    print(f"  first token>=0.5 @ step {first_cross(s['step'], s['token'], 0.5)}; "
          f"exact>0 @ {first_cross(s['step'], s['exact'], 1e-9)}; "
          f"exact>=0.1 @ {first_cross(s['step'], s['exact'], 0.1)}")
    # lead/lag: structure (ratio) vs capability (exact, then token)
    for cap_name in ('exact', 'token'):
        r = xcorr_best_lag(s['ratio'], s[cap_name])
        if r:
            evals = s['step'][1] - s['step'][0] if len(s['step']) > 1 else 1
            lead = r['best_lag'] * evals
            direction = ("STRUCTURE LEADS capability" if r['best_lag'] > 0 else
                         "capability leads structure" if r['best_lag'] < 0 else
                         "simultaneous")
            print(f"  lead/lag  ratio vs {cap_name}: best_lag={r['best_lag']} eval(s) "
                  f"(~{lead} steps), corr={r['best_corr']:+.3f}  => {direction}")


def compare_pair(base, gated):
    print(f"\n=== BASELINE vs GATED (arm comparison) ===")
    bsteps = {st: i for i, st in enumerate(base['step'])}
    common = [st for st in gated['step'] if st in bsteps]
    if not common:
        print("  no common steps")
        return
    print(f"  {'step':>6} | {'base_ex':>8} {'gate_ex':>8} {'Δex':>7} | {'base_tok':>8} {'gate_tok':>8} {'Δtok':>7} | {'base_r':>6} {'gate_r':>6}")
    first_div = None
    maxd = (None, 0.0)
    for st in common:
        bi = bsteps[st]
        gi = gated['step'].index(st)
        de = gated['exact'][gi] - base['exact'][bi]
        dt = gated['token'][gi] - base['token'][bi]
        if first_div is None and abs(de) > 0.01:
            first_div = st
        if abs(de) > abs(maxd[1]):
            maxd = (st, de)
        mk = '  <==gated' if de > 0.01 else ('  baseline' if de < -0.01 else '')
        print(f"  {st:>6} | {base['exact'][bi]:>8.4f} {gated['exact'][gi]:>8.4f} {de:>+7.4f} | "
              f"{base['token'][bi]:>8.4f} {gated['token'][gi]:>8.4f} {dt:>+7.4f} | "
              f"{base['ratio'][bi]:>6.2f} {gated['ratio'][gi]:>6.2f}{mk}")
    le = common[-1]
    bi, gi = bsteps[le], gated['step'].index(le)
    print(f"\n  first exact-divergence (|Δ|>0.01): step {first_div}")
    print(f"  max exact-Δ: {maxd[1]:+.4f} @ step {maxd[0]}")
    print(f"  final exact-Δ (gated-baseline): {gated['exact'][gi]-base['exact'][bi]:+.4f}  "
          f"=> {'GATED ACCELERATES' if gated['exact'][gi]-base['exact'][bi] > 0.01 else 'no exact benefit (yet)'}")


def main():
    print(f"Lead/lag analysis — {RESULTS}")
    seeds = sorted({p.split('_s')[-1] for p in glob.glob(os.path.join(RESULTS, 'easy_baseline_s*'))})
    if not seeds:
        print("no runs found")
        return
    for seed in seeds:
        print(f"\n{'='*72}\n  SEED {seed}\n{'='*72}")
        base = load_series(os.path.join(RESULTS, f'easy_baseline_s{seed}', 'trajectory.json'))
        gated = load_series(os.path.join(RESULTS, f'easy_gated_s{seed}', 'trajectory.json'))
        if base:
            analyze_arm('baseline', base)
        if gated:
            analyze_arm('gated', gated)
        if base and gated:
            compare_pair(base, gated)
    print(f"\nCAVEATS: sparse evals => lead/lag is suggestive (resolution = 1 eval interval), "
          f"not rigorous. Correlation != causation — observational only; Phase-2 interventions "
          f"(freeze/inject/ablate) test the causal direction this tool hypothesizes.")


if __name__ == '__main__':
    main()
