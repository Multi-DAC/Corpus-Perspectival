"""Per-layer CV analysis across all 5 training approaches."""
import json
import numpy as np
from scipy.stats import spearmanr

trajs = {}
for name, path in [
    ("baseline", "/home/clawd/HRM/checkpoints/300m_baseline/kf_trajectory_300m.json"),
    ("fixed", "/home/clawd/HRM/checkpoints/300m_kf_decoupled/kf_trajectory_300m.json"),
    ("log", "/home/clawd/HRM/checkpoints/300m_kf_log/kf_trajectory_300m.json"),
    ("cosine", "/home/clawd/HRM/checkpoints/300m_kf_cosine/kf_trajectory_300m.json"),
    ("gated", "/home/clawd/HRM/checkpoints/300m_kf_gated/kf_trajectory_300m.json"),
]:
    with open(path) as f:
        trajs[name] = json.load(f)

final_data = {}
for name in ["baseline", "fixed", "log", "cosine", "gated"]:
    last = trajs[name][-1]
    final_data[name] = [last["H"]["per_layer"][str(i)]["cv"] for i in range(12)]

print("=== Final Per-Layer H_CV (epoch 500) ===")
header = "  Lyr    baseline       fixed         log      cosine       gated"
print(header)
for i in range(12):
    row = f"  L{i:<2d}"
    for name in ["baseline", "fixed", "log", "cosine", "gated"]:
        v = final_data[name][i]
        if v < 1:
            row += f"  {v:11.6f}"
        else:
            row += f"  {v:11.1f}"
    print(row)

# Enrichment: gated / baseline
print("\n=== Gated Enrichment (Gated_CV / Baseline_CV) ===")
enrichment = []
for i in range(12):
    ratio = final_data["gated"][i] / max(final_data["baseline"][i], 1e-10)
    enrichment.append(ratio)
    marker = " ALIGNED" if i in {1,5,6,8} else (" OPPOSED" if i in {7,9,10,11} else "")
    print(f"  L{i:2d}: {ratio:>14,.0f}x  {marker}")

bl = final_data["baseline"]
rho, p = spearmanr(bl, enrichment)
print(f"\nBaseline CV vs Enrichment: rho={rho:.4f}, p={p:.4f}")

# Gated vs Fixed suppression
print("\n=== Gated / Fixed Ratio (>1 = gated grew MORE, <1 = gated SUPPRESSED) ===")
aligned_r = []
opposed_r = []
for i in range(12):
    ratio = final_data["gated"][i] / max(final_data["fixed"][i], 1e-10)
    marker = " ALIGNED" if i in {1,5,6,8} else (" OPPOSED" if i in {7,9,10,11} else "")
    print(f"  L{i:2d}: {ratio:.6f}  {marker}")
    if i in {1,5,6,8}:
        aligned_r.append(ratio)
    elif i in {7,9,10,11}:
        opposed_r.append(ratio)

print(f"\nAligned mean gated/fixed: {np.mean(aligned_r):.6f}")
print(f"Opposed mean gated/fixed: {np.mean(opposed_r):.6f}")
print(f"Separation ratio: {np.mean(aligned_r)/np.mean(opposed_r):.2f}x")

# Layer rank by gated final CV
print("\n=== Layers ranked by gated final CV ===")
ranked = sorted(range(12), key=lambda i: final_data["gated"][i], reverse=True)
for rank, i in enumerate(ranked):
    marker = " ALIGNED" if i in {1,5,6,8} else (" OPPOSED" if i in {7,9,10,11} else "")
    print(f"  #{rank+1:2d} L{i:2d}: {final_data['gated'][i]:>10.1f}  {marker}")

# Key test: do aligned layers cluster at top and opposed at bottom?
aligned_ranks = [ranked.index(i) for i in {1,5,6,8}]
opposed_ranks = [ranked.index(i) for i in {7,9,10,11}]
print(f"\nAligned mean rank: {np.mean(aligned_ranks)+1:.1f} (lower=more CV)")
print(f"Opposed mean rank: {np.mean(opposed_ranks)+1:.1f}")

# Compare growth trajectories for aligned vs opposed
print("\n=== Growth Trajectory: Aligned vs Opposed H_CV ===")
for entry in trajs["gated"]:
    step = entry["step"]
    aligned_cv = np.mean([entry["H"]["per_layer"][str(i)]["cv"] for i in [1,5,6,8]])
    opposed_cv = np.mean([entry["H"]["per_layer"][str(i)]["cv"] for i in [7,9,10,11]])
    ratio = aligned_cv / max(opposed_cv, 1e-10)
    print(f"  {step:>10}: aligned={aligned_cv:>10.2f}  opposed={opposed_cv:>10.2f}  ratio={ratio:.2f}")

# When does the divergence appear?
print("\n=== Divergence Timeline ===")
for idx, entry in enumerate(trajs["gated"]):
    if idx == 0:
        continue
    step = entry["step"]
    prev = trajs["gated"][idx-1]
    a_now = np.mean([entry["H"]["per_layer"][str(i)]["cv"] for i in [1,5,6,8]])
    a_prev = np.mean([prev["H"]["per_layer"][str(i)]["cv"] for i in [1,5,6,8]])
    o_now = np.mean([entry["H"]["per_layer"][str(i)]["cv"] for i in [7,9,10,11]])
    o_prev = np.mean([prev["H"]["per_layer"][str(i)]["cv"] for i in [7,9,10,11]])
    a_growth = a_now / max(a_prev, 1e-10)
    o_growth = o_now / max(o_prev, 1e-10)
    print(f"  {prev['step']} -> {step}: aligned grew {a_growth:.2f}x, opposed grew {o_growth:.2f}x, differential={a_growth/o_growth:.2f}x")
