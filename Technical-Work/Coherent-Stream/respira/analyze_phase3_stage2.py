"""
Respira Phase-3 Stage 2 analysis — applies the locked verdicts and reads the
8-row factorial attribution table per pre-reg §4.

Pre-registration: palace/south/respira-phase3-stage2-v3h-prime-preregistration-2026-05-28.md
Ratified: Clayton 2026-05-29.

Win conditions (LOCKED, per pre-reg §4a):
  W-VhP{X}-acc:   arm-X mean token-accuracy @ final checkpoint within ±1 SE of
                  no_mirror's mean (0.897 from Stage 1).
  W-VhP{X}-halt:  arm-X mean halt cycle @ final checkpoint strictly less than 4.0.
  W-VhP{X}-calib: arm-X Spearman(conf_at_halt, correctness_pb) @ final checkpoint > +0.3.

  W-VhP{X}-DECISIVE: all three of {acc, halt, calib} pass for arm X.

Attribution table (§4c): 8 outcome combinations have pre-registered readings.

Usage:
    python3 analyze_phase3_stage2.py [results.json]
    (defaults to phase3_stage2_results_YYYY-MM-DD.json for today's date)

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import json
import sys
import math
from datetime import datetime
from statistics import mean, stdev


# Stage 1 reference for no_mirror (3 seeds, 2500 steps). Source: phase2v2_results_2026-05-28.json.
NO_MIRROR_REFERENCE = {
    "token_acc_mean": 0.897,
    "token_acc_se": 0.013,  # 1 SE across 3 seeds (approx; tight band)
}

FINAL_CKPT = "2500"


def per_arm_stats(runs: list[dict], arm: str) -> dict | None:
    """Aggregate the 3-seed stats for an arm at the final checkpoint."""
    arm_runs = [r for r in runs if r["arm"] == arm and not r.get("aborted", False)]
    if not arm_runs:
        return None
    accs, halts, calibs, confs = [], [], [], []
    for r in arm_runs:
        ck = r["checkpoints"].get(FINAL_CKPT)
        if not ck:
            continue
        if ck["token_accuracy"] is not None:
            accs.append(ck["token_accuracy"])
        if ck["mean_halt_cycle"] is not None:
            halts.append(ck["mean_halt_cycle"])
        if ck["calib_spearman_conf_vs_correctness"] is not None:
            calibs.append(ck["calib_spearman_conf_vs_correctness"])
        if ck["mean_confidence_at_halt"] is not None:
            confs.append(ck["mean_confidence_at_halt"])
    if not accs:
        return None
    return {
        "n_seeds": len(arm_runs),
        "acc_mean": mean(accs), "acc_se": stdev(accs) / math.sqrt(len(accs)) if len(accs) > 1 else 0.0,
        "halt_mean": mean(halts) if halts else None,
        "halt_se": stdev(halts) / math.sqrt(len(halts)) if len(halts) > 1 else 0.0,
        "calib_mean": mean(calibs) if calibs else None,
        "calib_se": stdev(calibs) / math.sqrt(len(calibs)) if len(calibs) > 1 else 0.0,
        "conf_mean": mean(confs) if confs else None,
    }


def verdict_acc(arm_stats: dict, ref_mean: float, ref_se: float) -> tuple[bool, str]:
    """W-VhP{X}-acc: arm mean within ±1 SE of no_mirror."""
    delta = arm_stats["acc_mean"] - ref_mean
    combined_se = math.sqrt(arm_stats["acc_se"] ** 2 + ref_se ** 2)
    passes = abs(delta) <= combined_se
    return passes, f"{arm_stats['acc_mean']:.4f} (Δ={delta:+.4f}, combined-SE={combined_se:.4f})"


def verdict_halt(arm_stats: dict) -> tuple[bool, str]:
    """W-VhP{X}-halt: arm mean halt cycle < 4.0."""
    if arm_stats["halt_mean"] is None:
        return False, "no halt data"
    passes = arm_stats["halt_mean"] < 4.0
    return passes, f"halt_mean={arm_stats['halt_mean']:.2f} (threshold 4.0)"


def verdict_calib(arm_stats: dict) -> tuple[bool, str]:
    """W-VhP{X}-calib: arm Spearman > +0.3."""
    if arm_stats["calib_mean"] is None:
        return False, "no calib data"
    passes = arm_stats["calib_mean"] > 0.3
    return passes, f"calib_mean={arm_stats['calib_mean']:+.3f} (threshold +0.3)"


# Attribution table from pre-reg §4c. Index: (A_full, C_detach_only, B_td_only)
ATTRIBUTION = {
    (True, True, True):
        "**Both fixes work independently AND together** — Read B operationally vindicated. "
        "Either fix alone is sufficient. Advance to Phase-3 v3-x falsifier.",
    (True, True, False):
        "**Detach was the load-bearing fix; TD-supervisor is unnecessary or neutral.** "
        "Channel-leakage was Stage 1's killer.",
    (True, False, True):
        "**TD-supervisor was the load-bearing fix; detach is unnecessary or neutral.** "
        "Supervisor target was Stage 1's killer.",
    (True, False, False):
        "**Both fixes are necessary together (interaction effect).** Neither alone is "
        "sufficient. Architecturally significant: the failure mode required the joint "
        "presence of both bugs.",
    (False, True, False):
        "**Detach alone works but adding TD breaks it.** Strong evidence TD-supervisor was "
        "wrong; revert to BCE-on-correctness with detach for v3 family.",
    (False, False, True):
        "**TD alone works but adding detach breaks it.** Suggests detach removes information "
        "the Mirror legitimately needed; channel-leakage diagnosis may have been wrong.",
    (False, True, True):
        "**Each fix alone works but combining breaks.** Unusual; suggests an interaction we "
        "don't currently understand. Investigate.",
    (False, False, False):
        "**Neither bug-fix nor their combination rescues v3h.** Either Read B is wrong, OR "
        "there's a third undiagnosed bug we haven't named. Either way, do NOT advance to "
        "v3-x; rethink.",
}


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    default_path = f"phase3_stage2_results_{today}.json"
    path = sys.argv[1] if len(sys.argv) > 1 else default_path

    with open(path) as f:
        data = json.load(f)
    runs = data["runs"]

    print("=" * 78)
    print("  RESPIRA PHASE-3 STAGE 2 — v3h-prime ATTRIBUTION ANALYSIS")
    print(f"  results: {path}")
    print(f"  {len(runs)} runs total")
    print("=" * 78)

    # Map arm names to attribution-table letters (per pre-reg §2)
    arm_letter = {"v3hp_full": "A", "v3hp_detach_only": "C", "v3hp_td_only": "B"}

    print(f"\n## Reference: no_mirror @ Stage 1 (3 seeds, 2500 steps)")
    print(f"  acc_mean = {NO_MIRROR_REFERENCE['token_acc_mean']:.4f}  "
          f"acc_SE = {NO_MIRROR_REFERENCE['token_acc_se']:.4f}")

    print(f"\n## Per-arm stats + verdicts (final checkpoint = step {FINAL_CKPT})\n")

    decisive_results = {}
    for arm in ("v3hp_full", "v3hp_detach_only", "v3hp_td_only"):
        letter = arm_letter[arm]
        stats = per_arm_stats(runs, arm)
        if stats is None:
            print(f"### Arm {letter} ({arm}): NO DATA")
            decisive_results[letter] = False
            continue

        print(f"### Arm {letter} ({arm}) — n_seeds={stats['n_seeds']}")
        p_acc, d_acc = verdict_acc(stats, NO_MIRROR_REFERENCE["token_acc_mean"],
                                   NO_MIRROR_REFERENCE["token_acc_se"])
        p_halt, d_halt = verdict_halt(stats)
        p_calib, d_calib = verdict_calib(stats)
        decisive = p_acc and p_halt and p_calib
        decisive_results[letter] = decisive

        print(f"  W-VhP{letter}-acc:   {'✅' if p_acc else '❌'}  {d_acc}")
        print(f"  W-VhP{letter}-halt:  {'✅' if p_halt else '❌'}  {d_halt}")
        print(f"  W-VhP{letter}-calib: {'✅' if p_calib else '❌'}  {d_calib}")
        print(f"  --> W-VhP{letter}-DECISIVE: {'✅ PASS' if decisive else '❌ FAIL'}")
        if stats["conf_mean"] is not None:
            print(f"  (conf_at_halt mean: {stats['conf_mean']:.3f})")
        print()

    print("## Factorial attribution\n")
    A = decisive_results.get("A", False)
    B = decisive_results.get("B", False)
    C = decisive_results.get("C", False)
    print(f"  Outcome: A=v3hp_full {'✅' if A else '❌'}  "
          f"C=v3hp_detach_only {'✅' if C else '❌'}  "
          f"B=v3hp_td_only {'✅' if B else '❌'}")
    reading = ATTRIBUTION.get((A, C, B), "(no pre-registered reading found — implementation error)")
    print(f"\n  PRE-REGISTERED READING:\n  {reading}\n")

    print("=" * 78)


if __name__ == "__main__":
    main()
