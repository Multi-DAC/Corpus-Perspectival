"""
P-Gauge-1: Natal Constraint Topology as Gauge Structure
Bridge #86 Test — Does perturbing constrained layers affect accuracy less than perturbing free layers?

Hypothesis: Constrained layers (high baseline CV, same across seeds) are gauge-like:
  perturbing them should NOT affect accuracy significantly.
Free layers (low baseline CV, seed-dependent) are physical-like:
  perturbing them SHOULD degrade accuracy.

Usage:
  python gauge_perturbation_test.py \
    --checkpoint /path/to/gated_checkpoint.pt \
    --baseline_cv_json /path/to/baseline_cv.json \
    --sigma 0.1 \
    --n_constrained 4 \
    --n_free 4

Reads the baseline per-layer CV from the JSON log, identifies the most constrained
(highest CV) and most free (lowest CV) layers, perturbs each group independently,
and measures accuracy change.
"""

import argparse
import json
import copy
import torch
import numpy as np
from pathlib import Path


def load_baseline_cv(json_path):
    """Load baseline per-layer CV from trajectory JSON."""
    with open(json_path) as f:
        data = json.load(f)

    # Look for the first entry's per-layer CV (before training)
    if isinstance(data, list):
        first = data[0]
    elif isinstance(data, dict) and "entries" in data:
        first = data["entries"][0]
    else:
        first = data

    # Try to find per-layer CV keys
    per_layer = {}
    for key, val in first.items():
        if key.startswith("h_cv_L") or key.startswith("H_CV_L"):
            layer_idx = int(key.split("L")[1])
            per_layer[layer_idx] = float(val)

    if not per_layer:
        raise ValueError(f"No per-layer CV found in {json_path}. Keys: {list(first.keys())}")

    return per_layer


def identify_layers(per_layer_cv, n_constrained, n_free):
    """Identify constrained (high CV) and free (low CV) layers."""
    sorted_layers = sorted(per_layer_cv.items(), key=lambda x: x[1])

    free_layers = [idx for idx, _ in sorted_layers[:n_free]]
    constrained_layers = [idx for idx, _ in sorted_layers[-n_constrained:]]

    print(f"\nLayer CV ranking (low to high):")
    for idx, cv in sorted_layers:
        label = ""
        if idx in free_layers:
            label = " <-- FREE (low CV, physical-like)"
        elif idx in constrained_layers:
            label = " <-- CONSTRAINED (high CV, gauge-like)"
        print(f"  Layer {idx:2d}: CV = {cv:.6f}{label}")

    return constrained_layers, free_layers


def perturb_layers(model, layer_indices, sigma, module_name="H_level"):
    """Add Gaussian noise to qkv_proj weights of specified layers."""
    perturbed = copy.deepcopy(model)

    # Navigate to H-module layers
    if hasattr(perturbed, 'inner'):
        layers = perturbed.inner.H_level.layers
    elif hasattr(perturbed, 'H_level'):
        layers = perturbed.H_level.layers
    else:
        raise AttributeError("Cannot find H_level layers in model")

    for idx in layer_indices:
        layer = layers[idx]
        w = layer.self_attn.qkv_proj.weight
        noise_std = sigma * w.std().item()
        noise = torch.randn_like(w) * noise_std
        w.data.add_(noise)
        print(f"  Perturbed layer {idx}: noise std = {noise_std:.6f} "
              f"(σ={sigma} × weight_std={w.std().item():.6f})")

    return perturbed


def evaluate_accuracy(model, dataloader, device, max_batches=50):
    """Evaluate token-level accuracy on sudoku data."""
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for i, batch in enumerate(dataloader):
            if i >= max_batches:
                break

            input_ids = batch["input_ids"].to(device)
            labels = batch.get("labels", input_ids[:, 1:]).to(device)

            outputs = model(input_ids)
            logits = outputs.logits if hasattr(outputs, 'logits') else outputs

            # Token accuracy
            preds = logits[:, :-1].argmax(dim=-1)
            target = labels if labels.shape[1] == preds.shape[1] else input_ids[:, 1:]

            mask = target != -100  # ignore padding
            correct += (preds[mask] == target[mask]).sum().item()
            total += mask.sum().item()

    return correct / total if total > 0 else 0.0


def main():
    parser = argparse.ArgumentParser(description="P-Gauge-1: Gauge perturbation test")
    parser.add_argument("--checkpoint", required=True, help="Path to model checkpoint")
    parser.add_argument("--baseline_cv_json", required=True, help="Path to baseline CV JSON")
    parser.add_argument("--sigma", type=float, default=0.1, help="Noise scale (fraction of weight std)")
    parser.add_argument("--n_constrained", type=int, default=4, help="Number of constrained layers to perturb")
    parser.add_argument("--n_free", type=int, default=4, help="Number of free layers to perturb")
    parser.add_argument("--max_batches", type=int, default=50, help="Max eval batches")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for noise")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    print("=" * 60)
    print("P-Gauge-1: Natal Constraint Topology as Gauge Structure")
    print("=" * 60)
    print(f"\nHypothesis: Constrained layers (high baseline CV) are gauge-like.")
    print(f"            Free layers (low baseline CV) are physical-like.")
    print(f"Test: Perturb each group with σ={args.sigma}, measure accuracy change.")
    print(f"Expected: Constrained perturbation → small Δacc, Free perturbation → large Δacc")

    # 1. Load baseline CV
    print(f"\n--- Loading baseline CV from {args.baseline_cv_json} ---")
    per_layer_cv = load_baseline_cv(args.baseline_cv_json)
    constrained, free = identify_layers(per_layer_cv, args.n_constrained, args.n_free)

    # 2. Load model
    print(f"\n--- Loading model from {args.checkpoint} ---")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    checkpoint = torch.load(args.checkpoint, map_location=device)

    # TODO: Instantiate model architecture and load state dict
    # This depends on the specific HRM model class
    # model = HRMModel(config)
    # model.load_state_dict(checkpoint["model_state_dict"])
    # model.to(device)
    # dataloader = get_eval_dataloader(...)

    print("\n[NOTE] Model loading requires HRM architecture class.")
    print("       This script provides the framework — adapt model instantiation")
    print("       to match the specific checkpoint format.\n")

    # 3. Evaluate baseline (placeholder)
    # baseline_acc = evaluate_accuracy(model, dataloader, device, args.max_batches)
    # print(f"\nBaseline accuracy: {baseline_acc:.4f}")

    # 4. Perturb constrained layers
    # print(f"\n--- Perturbing {args.n_constrained} CONSTRAINED layers (gauge-like) ---")
    # model_constrained = perturb_layers(model, constrained, args.sigma)
    # acc_constrained = evaluate_accuracy(model_constrained, dataloader, device, args.max_batches)
    # delta_constrained = acc_constrained - baseline_acc
    # print(f"Accuracy after constrained perturbation: {acc_constrained:.4f} (Δ = {delta_constrained:+.4f})")

    # 5. Perturb free layers
    # print(f"\n--- Perturbing {args.n_free} FREE layers (physical-like) ---")
    # model_free = perturb_layers(model, free, args.sigma)
    # acc_free = evaluate_accuracy(model_free, dataloader, device, args.max_batches)
    # delta_free = acc_free - baseline_acc
    # print(f"Accuracy after free perturbation: {acc_free:.4f} (Δ = {delta_free:+.4f})")

    # 6. Results
    # print("\n" + "=" * 60)
    # print("RESULTS")
    # print("=" * 60)
    # print(f"Baseline accuracy:            {baseline_acc:.4f}")
    # print(f"Constrained perturbation Δ:   {delta_constrained:+.4f}")
    # print(f"Free perturbation Δ:          {delta_free:+.4f}")
    # print(f"Ratio |Δ_free/Δ_constrained|: {abs(delta_free/delta_constrained) if delta_constrained != 0 else 'inf':.2f}")
    # print()
    # if abs(delta_free) > abs(delta_constrained) * 2:
    #     print("RESULT: CONSISTENT with gauge hypothesis (Bridge #86)")
    #     print("  Free layers carry more physical information than constrained layers.")
    # elif abs(delta_constrained) > abs(delta_free) * 2:
    #     print("RESULT: FALSIFIED — constrained layers MORE sensitive than free layers")
    #     print("  The gauge analogy does not hold at the perturbation level.")
    # else:
    #     print("RESULT: INCONCLUSIVE — similar sensitivity in both groups")
    #     print("  The distinction may be real but σ={args.sigma} doesn't resolve it.")


if __name__ == "__main__":
    main()
