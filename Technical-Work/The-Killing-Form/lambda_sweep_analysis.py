"""V0.5a Lambda Sweep Analysis — 300M Dual-Module Architecture"""
import json
import sys

lambdas = ["0.001", "0.01", "0.1"]
results = {}

for lam in lambdas:
    path = f"/home/clawd/HRM/checkpoints/kf_v05a_lambda_{lam}/kf_trajectory_v05.json"
    with open(path) as f:
        results[lam] = json.load(f)

print("=" * 80)
print("V0.5a LAMBDA SWEEP ANALYSIS - 300M Dual-Module Architecture")
print("=" * 80)

# 1. Task accuracy comparison
print("\n--- 1. TASK ACCURACY vs LAMBDA (epoch 2000) ---")
header = f"{'Lambda':>8} {'Token Acc':>10} {'Exact Acc':>10} {'Loss':>10}"
print(header)
for lam in lambdas:
    d = results[lam][-1]
    ta = d['token_accuracy']
    ea = d['exact_accuracy']
    lo = d['loss']
    print(f"{lam:>8} {ta:>10.4f} {ea:>10.4f} {lo:>10.1f}")

# 2. H_CV amplification
print("\n--- 2. H-MODULE ALGEBRAIC AMPLIFICATION ---")
print(f"{'Lambda':>8} {'H_init':>10} {'H_2000':>10} {'Amplif':>10} {'L_init':>10} {'L_2000':>10} {'L_chg%':>10}")
for lam in lambdas:
    h_init = results[lam][0]["H"]["cv"]
    h_final = results[lam][-1]["H"]["cv"]
    l_init = results[lam][0]["L"]["cv"]
    l_final = results[lam][-1]["L"]["cv"]
    amp = h_final / h_init
    l_change = (l_final - l_init) / l_init * 100
    print(f"{lam:>8} {h_init:>10.6f} {h_final:>10.6f} {amp:>9.2f}x {l_init:>10.6f} {l_final:>10.6f} {l_change:>+9.1f}%")

# 3. H/L divergence ratio trajectory
print("\n--- 3. H/L CV RATIO TRAJECTORY ---")
steps = ["init", "epoch_500", "epoch_1000", "epoch_1500", "epoch_2000"]
header = f"{'Step':>12}"
for lam in lambdas:
    header += f"  {'l='+lam:>10}"
print(header)
for i, step in enumerate(steps):
    row = f"{step:>12}"
    for lam in lambdas:
        ratio = results[lam][i]["cross"]["h_l_cv_ratio"]
        row += f"  {ratio:>10.4f}"
    print(row)

# 4. Per-layer H_CV at epoch 2000
print("\n--- 4. H-MODULE PER-LAYER CV at epoch 2000 ---")
print(f"{'Lambda':>8} {'Layer 0':>10} {'Layer 1':>10} {'Layer 2':>10} {'Layer 3':>10} {'Dominant':>10}")
for lam in lambdas:
    layers = [results[lam][-1]["H"]["per_layer"][str(i)]["cv"] for i in range(4)]
    dominant = layers.index(max(layers))
    dname = "Layer " + str(dominant)
    print(f"{lam:>8} {layers[0]:>10.6f} {layers[1]:>10.6f} {layers[2]:>10.6f} {layers[3]:>10.6f} {dname:>10}")

# 5. Per-layer amplification (init to epoch 2000)
print("\n--- 5. PER-LAYER AMPLIFICATION (H-module, init to epoch 2000) ---")
print(f"{'Lambda':>8} {'Layer 0':>10} {'Layer 1':>10} {'Layer 2':>10} {'Layer 3':>10}")
for lam in lambdas:
    init_l = [results[lam][0]["H"]["per_layer"][str(i)]["cv"] for i in range(4)]
    final_l = [results[lam][-1]["H"]["per_layer"][str(i)]["cv"] for i in range(4)]
    row = f"{lam:>8}"
    for ii in range(4):
        amp = final_l[ii] / init_l[ii] if init_l[ii] > 0 else 0
        row += f" {amp:>9.2f}x"
    print(row)

# 6. L-module per-layer at epoch 2000
print("\n--- 6. L-MODULE PER-LAYER CV at epoch 2000 ---")
print(f"{'Lambda':>8} {'Layer 0':>10} {'Layer 1':>10} {'Layer 2':>10} {'Layer 3':>10}")
for lam in lambdas:
    layers = [results[lam][-1]["L"]["per_layer"][str(i)]["cv"] for i in range(4)]
    print(f"{lam:>8} {layers[0]:>10.6f} {layers[1]:>10.6f} {layers[2]:>10.6f} {layers[3]:>10.6f}")

# 7. L-module per-layer change
print("\n--- 7. L-MODULE PER-LAYER CHANGE (init to epoch 2000) ---")
print(f"{'Lambda':>8} {'Layer 0':>10} {'Layer 1':>10} {'Layer 2':>10} {'Layer 3':>10}")
for lam in lambdas:
    init_l = [results[lam][0]["L"]["per_layer"][str(i)]["cv"] for i in range(4)]
    final_l = [results[lam][-1]["L"]["per_layer"][str(i)]["cv"] for i in range(4)]
    row = f"{lam:>8}"
    for ii in range(4):
        chg = (final_l[ii] - init_l[ii]) / init_l[ii] * 100
        row += f" {chg:>+9.1f}%"
    print(row)
