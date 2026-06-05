"""
Analyze Respira Phase-2 sweep results against the pre-registered win conditions.

Pre-registration: `palace/south/respira-phase2-preregistration-2026-05-28.md`.

Computes:
  W1 — Architecture beats matched baseline: Respira-full mean token-acc > transformer mean
       by ≥1 SE of difference, AND ≥2/3 per-seed Respira-full > per-seed transformer.
  W2 — Mirror earns its keep: Respira-full mean > Respira-no-mirror mean by ≥1 SE of diff,
       AND ≥2/3 per-seed Respira-full > Respira-no-mirror.

Plus secondary metrics (sample-efficiency curve, halt distribution, etc.) per §4 of the
pre-registration.

Reports the §5 outcome verdict honestly — does NOT extend or re-run on disappointing results.

Usage:  python3 analyze_phase2.py [results.json]

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path


CHECKPOINTS = [200, 500, 1000, 2000]
PRIMARY_STEP = "2000"


def load(path: str) -> dict:
    return json.loads(Path(path).read_text())


def by_arm_seed(results: dict, step: str = PRIMARY_STEP) -> dict:
    """Returns {arm: {seed: {metric: value}}} for the requested checkpoint step."""
    out: dict[str, dict[int, dict]] = {}
    for run in results["runs"]:
        if run.get("aborted"):
            continue
        arm = run["arm"]
        seed = run["seed"]
        ckpt = run["checkpoints"].get(step) or {}
        out.setdefault(arm, {})[seed] = ckpt
    return out


def mean_std(xs: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan")
    m = sum(xs) / n
    if n < 2:
        return m, 0.0
    v = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(v)


def paired_diff_test(a: list[float], b: list[float]) -> tuple[float, float, int]:
    """Per-seed paired differences. Returns (mean_diff, se_diff, n_positive_per_seed)."""
    diffs = [ai - bi for ai, bi in zip(a, b)]
    n = len(diffs)
    if n == 0:
        return float("nan"), float("nan"), 0
    md = sum(diffs) / n
    if n < 2:
        return md, 0.0, sum(1 for d in diffs if d > 0)
    v = sum((d - md) ** 2 for d in diffs) / (n - 1)
    se = math.sqrt(v / n)  # SE of the mean of paired differences
    n_pos = sum(1 for d in diffs if d > 0)
    return md, se, n_pos


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "phase2_results_2026-05-28.json"
    results = load(path)
    meta = results["metadata"]

    print("=" * 78)
    print(f"  RESPIRA PHASE-2 ANALYSIS — {path}")
    print(f"  seeds={meta['seeds']}  steps={meta['steps']}  arms={meta['arms']}")
    print("=" * 78)

    table = by_arm_seed(results, step=PRIMARY_STEP)

    # Per-arm summaries at the primary checkpoint
    print(f"\n--- token_accuracy @ step {PRIMARY_STEP} (primary metric) ---")
    print(f"  {'arm':<22} {'mean':>8} {'std':>8} {'per-seed values':>30}")
    arm_token_acc = {}
    for arm in meta["arms"]:
        seeds_dict = table.get(arm, {})
        vals = sorted([(s, seeds_dict[s].get("token_accuracy", float("nan"))) for s in seeds_dict])
        ys = [v for _, v in vals]
        arm_token_acc[arm] = {s: v for s, v in vals}
        m, s = mean_std(ys)
        per_seed = "  ".join(f"s{seed}:{v:.4f}" for seed, v in vals)
        print(f"  {arm:<22} {m:>8.4f} {s:>8.4f} {per_seed:>30}")

    # Pre-registered tests
    print(f"\n--- W1: Respira-full beats matched transformer? ---")
    if "respira_full" in arm_token_acc and "transformer" in arm_token_acc:
        seeds_common = sorted(set(arm_token_acc["respira_full"]) &
                              set(arm_token_acc["transformer"]))
        a = [arm_token_acc["respira_full"][s] for s in seeds_common]
        b = [arm_token_acc["transformer"][s] for s in seeds_common]
        md, se, n_pos = paired_diff_test(a, b)
        n = len(a)
        cond_se = (md > se) if not math.isnan(md) else False
        cond_seeds = n_pos >= max(1, math.ceil(2 / 3 * n))
        verdict = "W1 PASS" if (cond_se and cond_seeds) else "W1 FAIL"
        print(f"  mean diff (full − transformer): {md:+.4f}  SE: {se:.4f}  "
              f"mean > SE? {cond_se}")
        print(f"  per-seed diffs positive: {n_pos}/{n}  (need ≥{math.ceil(2/3*n)})  "
              f"satisfied? {cond_seeds}")
        print(f"  ⇒  {verdict}")

    print(f"\n--- W2: Mirror earns its keep within Respira? ---")
    if "respira_full" in arm_token_acc and "respira_no_mirror" in arm_token_acc:
        seeds_common = sorted(set(arm_token_acc["respira_full"]) &
                              set(arm_token_acc["respira_no_mirror"]))
        a = [arm_token_acc["respira_full"][s] for s in seeds_common]
        b = [arm_token_acc["respira_no_mirror"][s] for s in seeds_common]
        md, se, n_pos = paired_diff_test(a, b)
        n = len(a)
        cond_se = (md > se) if not math.isnan(md) else False
        cond_seeds = n_pos >= max(1, math.ceil(2 / 3 * n))
        verdict = "W2 PASS" if (cond_se and cond_seeds) else "W2 FAIL"
        print(f"  mean diff (full − no-mirror): {md:+.4f}  SE: {se:.4f}  "
              f"mean > SE? {cond_se}")
        print(f"  per-seed diffs positive: {n_pos}/{n}  (need ≥{math.ceil(2/3*n)})  "
              f"satisfied? {cond_seeds}")
        print(f"  ⇒  {verdict}")

    # Sample-efficiency curve
    print(f"\n--- token_accuracy sample-efficiency curve (mean across seeds) ---")
    header = "  " + f"{'arm':<22}" + "".join(f"  step {c:>4d}" for c in CHECKPOINTS)
    print(header)
    for arm in meta["arms"]:
        row_vals = []
        for c in CHECKPOINTS:
            tab = by_arm_seed(results, step=str(c)).get(arm, {})
            ys = [tab[s].get("token_accuracy", float("nan")) for s in tab if not math.isnan(tab[s].get("token_accuracy", float("nan")))]
            m, _ = mean_std(ys)
            row_vals.append(f"  {m:>9.4f}")
        print(f"  {arm:<22}" + "".join(row_vals))

    # Inside-analysis (Respira variants) at final
    print(f"\n--- Inside-analysis @ step {PRIMARY_STEP} (Respira variants) ---")
    for arm in ("respira_full", "respira_no_mirror"):
        tab = by_arm_seed(results, step=PRIMARY_STEP).get(arm, {})
        if not tab:
            continue
        hcs = [tab[s].get("mean_halt_cycle") for s in tab if tab[s].get("mean_halt_cycle") is not None]
        confs = [tab[s].get("mean_confidence_at_halt") for s in tab if tab[s].get("mean_confidence_at_halt") is not None]
        if hcs:
            m_hc, s_hc = mean_std(hcs)
            print(f"  {arm:<22} mean_halt_cycle = {m_hc:.2f} ± {s_hc:.2f}")
        if confs:
            m_c, s_c = mean_std(confs)
            print(f"  {arm:<22} mean_conf@halt  = {m_c:.4f} ± {s_c:.4f}")

    print(f"\n{'=' * 78}")
    print("  Per pre-registration §5 — interpretation:")
    print("    W1 ✓ W2 ✓  → Respira wins decisively; Phase-3 justified.")
    print("    W1 ✗ W2 ✓  → Mirror helps but architecture doesn't beat transformer (partial win).")
    print("    W1 ✓ W2 ✗  → Suspicious — investigate before claiming.")
    print("    W1 ✗ W2 ✗  → Honest null at this config/horizon. NO 'extend run' reflex.")
    print(f"{'=' * 78}")


if __name__ == "__main__":
    main()
