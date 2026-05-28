"""
Analyze Path A — gated vs baseline accuracy curves on HRM easy-sudoku.
Reads /home/clawd/path_a_results/easy_{baseline,gated}_s{SEED}/trajectory.json,
prints per-seed step-by-step comparison + the P49 acceleration check
(gated leads baseline early, narrows, widens at frontier).

Usage: python3 analyze_path_a.py [results_dir]
"""
import sys
import os
import json
import glob

RESULTS = sys.argv[1] if len(sys.argv) > 1 else '/home/clawd/path_a_results'


def load(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        d = json.load(f)
    pts = [t for t in d['trajectory'] if 'exact_accuracy' in t]
    return {t['global_step']: t for t in pts}


def seeds_present():
    s = set()
    for p in glob.glob(os.path.join(RESULTS, 'easy_baseline_s*')):
        if os.path.isdir(p):
            s.add(p.split('_s')[-1])
    return sorted(s, key=lambda x: int(x) if x.isdigit() else 999)


def main():
    seeds = seeds_present()
    if not seeds:
        print(f"No baseline runs found in {RESULTS}")
        return
    print(f"Path A analysis — results in {RESULTS}\n")

    agg = {}  # step -> list of (base_exact, gated_exact)
    for seed in seeds:
        base = load(os.path.join(RESULTS, f'easy_baseline_s{seed}', 'trajectory.json'))
        gated = load(os.path.join(RESULTS, f'easy_gated_s{seed}', 'trajectory.json'))
        print(f"{'='*78}\n  SEED {seed}\n{'='*78}")
        if not base or not gated:
            print(f"  incomplete: baseline={'ok' if base else 'MISSING'} gated={'ok' if gated else 'MISSING'}")
            if not base or not gated:
                # still show whichever exists
                pass
        steps = sorted(set((base or {}).keys()) | set((gated or {}).keys()))
        print(f"  {'step':>6} | {'base_exact':>10} {'gate_exact':>10} {'Δexact':>8} | "
              f"{'base_tok':>9} {'gate_tok':>9} {'Δtok':>7} | {'base_r':>7} {'gate_r':>7}")
        for st in steps:
            b = (base or {}).get(st)
            g = (gated or {}).get(st)
            be = b['exact_accuracy'] if b else float('nan')
            ge = g['exact_accuracy'] if g else float('nan')
            bt = b['token_accuracy'] if b else float('nan')
            gt = g['token_accuracy'] if g else float('nan')
            br = b['h_l_ratio'] if b else float('nan')
            gr = g['h_l_ratio'] if g else float('nan')
            de = ge - be if (b and g) else float('nan')
            dt = gt - bt if (b and g) else float('nan')
            mark = ''
            if b and g:
                mark = '  <== gated leads' if de > 0.005 else ('  (baseline leads)' if de < -0.005 else '')
            print(f"  {st:>6} | {be:>10.4f} {ge:>10.4f} {de:>+8.4f} | "
                  f"{bt:>9.4f} {gt:>9.4f} {dt:>+7.4f} | {br:>7.3f} {gr:>7.3f}{mark}")
            if b and g:
                agg.setdefault(st, []).append((be, ge, bt, gt))
        print()

    if agg:
        print(f"{'='*78}\n  AGGREGATE across {len(seeds)} seed(s) — mean accuracy\n{'='*78}")
        print(f"  {'step':>6} | {'base_exact':>10} {'gate_exact':>10} {'Δexact':>8} | "
              f"{'base_tok':>9} {'gate_tok':>9} {'Δtok':>7}")
        for st in sorted(agg):
            rows = agg[st]
            n = len(rows)
            mbe = sum(r[0] for r in rows) / n
            mge = sum(r[1] for r in rows) / n
            mbt = sum(r[2] for r in rows) / n
            mgt = sum(r[3] for r in rows) / n
            print(f"  {st:>6} | {mbe:>10.4f} {mge:>10.4f} {mge-mbe:>+8.4f} | "
                  f"{mbt:>9.4f} {mgt:>9.4f} {mgt-mbt:>+7.4f}")
        # P49 signature summary
        last = max(agg)
        first_nonzero = next((st for st in sorted(agg)
                              if any(r[1] > 0 or r[0] > 0 for r in agg[st])), None)
        print(f"\n  P49 signature check:")
        print(f"    first eval with any nonzero accuracy: step {first_nonzero}")
        rows = agg[last]
        n = len(rows)
        fe = (sum(r[1] for r in rows) - sum(r[0] for r in rows)) / n
        ft = (sum(r[3] for r in rows) - sum(r[2] for r in rows)) / n
        print(f"    final (step {last}): Δexact={fe:+.4f}  Δtoken={ft:+.4f}  "
              f"({'GATED WINS' if fe > 0.005 else 'no exact benefit' })")


if __name__ == '__main__':
    main()
