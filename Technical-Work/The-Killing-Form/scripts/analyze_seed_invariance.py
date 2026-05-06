"""Analyze seed invariance of gradient-gated KF layer alignment map.

Compares seed1 and seed2 gating patterns to test prediction P-SM-2:
the stable gating map is architecture-determined, not stochastic.

Usage: python analyze_seed_invariance.py <seed1_log> <seed2_log>
"""
import re
import sys
import json
from collections import Counter

def parse_gating_log(log_path):
    """Parse KF-gated log entries, extract per-step gating decisions."""
    entries = []
    pattern = re.compile(
        r'\[Step (\d+)\] KF-gated #\d+: H_CV=([\d.e+-]+)\s+'
        r'applied=(\d+)/(\d+)\s+gated=\[([^\]]*)\]\s+avg_cos=([\d.]+)'
    )
    with open(log_path, 'r') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                step = int(m.group(1))
                h_cv = float(m.group(2))
                n_applied = int(m.group(3))
                n_total = int(m.group(4))
                gated_str = m.group(5).strip()
                gated = [int(x.strip()) for x in gated_str.split(',') if x.strip()] if gated_str else []
                avg_cos = float(m.group(6))
                entries.append({
                    'step': step,
                    'h_cv': h_cv,
                    'n_applied': n_applied,
                    'n_total': n_total,
                    'gated': gated,
                    'avg_cos': avg_cos,
                })
    return entries

def compute_gating_profile(entries, phase="all", n_total=12):
    """Compute per-layer gating frequency. Phase: 'all', 'early', 'late'."""
    if phase == "early":
        entries = [e for e in entries if e['step'] < len(entries) * 50 // 2]
    elif phase == "late":
        entries = [e for e in entries if e['step'] >= len(entries) * 50 // 2]

    gate_counts = Counter()
    for e in entries:
        for layer in e['gated']:
            gate_counts[layer] += 1
    total_steps = len(entries)
    profile = {}
    for layer_idx in range(n_total):
        profile[layer_idx] = gate_counts.get(layer_idx, 0) / max(total_steps, 1)
    return profile

def classify_layers(profile, threshold=0.5):
    """Classify layers as aligned (rarely gated), opposed (often gated), or mixed."""
    aligned = [l for l, freq in profile.items() if freq < threshold * 0.5]
    opposed = [l for l, freq in profile.items() if freq > threshold * 1.5]
    mixed = [l for l, freq in profile.items() if threshold * 0.5 <= freq <= threshold * 1.5]
    return sorted(aligned), sorted(mixed), sorted(opposed)

def main():
    if len(sys.argv) < 3:
        print("Usage: python analyze_seed_invariance.py <seed1_log> <seed2_log>")
        sys.exit(1)

    seed1_log = sys.argv[1]
    seed2_log = sys.argv[2]

    print("=" * 70)
    print("SEED INVARIANCE ANALYSIS — P-SM-2")
    print("=" * 70)

    # Parse both logs
    s1 = parse_gating_log(seed1_log)
    s2 = parse_gating_log(seed2_log)
    print(f"\nSeed1: {len(s1)} KF-gated entries")
    print(f"Seed2: {len(s2)} KF-gated entries")

    # Overall gating profiles
    p1 = compute_gating_profile(s1)
    p2 = compute_gating_profile(s2)

    print("\n--- Per-Layer Gating Frequency (full run) ---")
    print(f"{'Layer':>6}  {'Seed1':>8}  {'Seed2':>8}  {'Delta':>8}  {'Match':>6}")
    print("-" * 42)
    for layer in range(12):
        f1 = p1.get(layer, 0)
        f2 = p2.get(layer, 0)
        delta = abs(f1 - f2)
        match = "YES" if delta < 0.15 else "no"
        print(f"{layer:>6}  {f1:>8.3f}  {f2:>8.3f}  {delta:>8.3f}  {match:>6}")

    # Late-phase profiles (Phase 3 — stable pattern)
    p1_late = compute_gating_profile(s1, phase="late")
    p2_late = compute_gating_profile(s2, phase="late")

    print("\n--- Per-Layer Gating Frequency (late phase only) ---")
    print(f"{'Layer':>6}  {'Seed1':>8}  {'Seed2':>8}  {'Delta':>8}  {'Match':>6}")
    print("-" * 42)
    matches = 0
    for layer in range(12):
        f1 = p1_late.get(layer, 0)
        f2 = p2_late.get(layer, 0)
        delta = abs(f1 - f2)
        match = "YES" if delta < 0.15 else "no"
        if delta < 0.15:
            matches += 1
        print(f"{layer:>6}  {f1:>8.3f}  {f2:>8.3f}  {delta:>8.3f}  {match:>6}")

    print(f"\nLate-phase layer agreement: {matches}/12 layers")

    # Classify layers
    a1, m1, o1 = classify_layers(p1_late)
    a2, m2, o2 = classify_layers(p2_late)
    print(f"\nSeed1 — aligned: {a1}  mixed: {m1}  opposed: {o1}")
    print(f"Seed2 — aligned: {a2}  mixed: {m2}  opposed: {o2}")

    # Spearman correlation between gating profiles
    from scipy import stats
    layers = list(range(12))
    vals1 = [p1_late.get(l, 0) for l in layers]
    vals2 = [p2_late.get(l, 0) for l in layers]
    rho, p_val = stats.spearmanr(vals1, vals2)
    print(f"\nSpearman correlation (late-phase gating profiles): rho={rho:.4f}, p={p_val:.6f}")

    # Verdict
    print("\n" + "=" * 70)
    if rho > 0.7 and p_val < 0.05:
        print("P-SM-2 CONFIRMED: Gating map is seed-invariant (architecture-determined)")
        print("The stable gating pattern is NOT stochastic — it reflects")
        print("architectural structure of the H-module layers.")
    elif rho > 0.4:
        print("P-SM-2 PARTIAL: Moderate correlation — some layers seed-invariant, some not")
        print("Further investigation needed.")
    else:
        print("P-SM-2 FALSIFIED: Gating map is seed-dependent")
        print("The stable pattern IS stochastic — initialization matters.")
    print("=" * 70)

    # Phase evolution comparison
    print("\n--- Phase Evolution ---")
    for name, entries in [("Seed1", s1), ("Seed2", s2)]:
        if len(entries) < 3:
            continue
        third = len(entries) // 3
        early_cos = [e['avg_cos'] for e in entries[:third]]
        mid_cos = [e['avg_cos'] for e in entries[third:2*third]]
        late_cos = [e['avg_cos'] for e in entries[2*third:]]
        print(f"  {name} avg_cos — Phase1: {sum(early_cos)/max(len(early_cos),1):.4f}  "
              f"Phase2: {sum(mid_cos)/max(len(mid_cos),1):.4f}  "
              f"Phase3: {sum(late_cos)/max(len(late_cos),1):.4f}")

if __name__ == "__main__":
    main()
