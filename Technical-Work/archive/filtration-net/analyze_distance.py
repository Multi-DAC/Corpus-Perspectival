"""
Distance Analysis — OQ30 Extension

Does within-chunk similarity decay differently than cross-chunk similarity?

If chunks create genuine spatial coherence: same-chunk pairs should have
higher similarity AND slower decay with distance than cross-chunk pairs.

If it's just a boundary discontinuity: both should decay at the same rate,
with only a discrete jump at chunk boundaries.

PREDICTION (Clawd, 2026-03-27):
  Within-chunk similarity decays at the same rate as cross-chunk.
  Boundary effect only. Confidence: MEDIUM (55%).

ALTERNATIVE:
  Within-chunk decays slower (genuine spatial coherence). Would be
  a stronger positive for the perspectives hypothesis.
"""

import torch
import torch.nn.functional as F
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from train_v4 import (FiltrationNetV4, ScalableHierarchicalDataset,
                        sinusoidal_encoding)


def get_level3_representations(model, input_ids):
    """Extract F3 representations after chunked local attention."""
    model.eval()
    with torch.no_grad():
        B, T = input_ids.shape
        pos_enc = sinusoidal_encoding(T, model.dim, input_ids.device)
        x = model.token_embed(input_ids) + pos_enc.unsqueeze(0)
        f3_rep = model.f3_descent(x)
    return f3_rep


def distance_analysis(f3_rep, chunk_size=32, max_samples=50):
    """
    Compute similarity as a function of distance, separated by
    same-chunk vs cross-chunk.

    Returns dict: {distance: {"same": [sims], "cross": [sims]}}
    """
    B, T, D = f3_rep.shape
    B = min(B, max_samples)  # limit for memory

    distances = [1, 2, 4, 8, 16, 24, 31]
    results = {d: {"same": [], "cross": []} for d in distances}

    rep_norm = F.normalize(f3_rep[:B], dim=-1)

    for d in distances:
        # All pairs at distance d
        left = rep_norm[:, :T-d, :]   # B, T-d, D
        right = rep_norm[:, d:, :]    # B, T-d, D
        sims = (left * right).sum(dim=-1)  # B, T-d

        for pos in range(T - d):
            chunk_left = pos // chunk_size
            chunk_right = (pos + d) // chunk_size

            vals = sims[:, pos].tolist()

            if chunk_left == chunk_right:
                results[d]["same"].extend(vals)
            else:
                results[d]["cross"].extend(vals)

    return results


def print_distance_table(results):
    """Pretty-print the distance analysis results."""
    print(f"\n{'='*70}")
    print("DISTANCE ANALYSIS — Similarity vs Token Distance")
    print(f"{'='*70}")
    print(f"{'Dist':>5}  {'Same-chunk':>15}  {'Cross-chunk':>15}  {'Delta':>10}  {'N_same':>8}  {'N_cross':>8}")
    print("-" * 70)

    same_means = []
    cross_means = []
    dists = []

    for d in sorted(results.keys()):
        s = results[d]["same"]
        c = results[d]["cross"]

        s_mean = np.mean(s) if s else float('nan')
        c_mean = np.mean(c) if c else float('nan')
        delta = s_mean - c_mean if s and c else float('nan')

        print(f"{d:>5}  {s_mean:>12.4f}+/-{np.std(s) if s else 0:.2f}"
              f"  {c_mean:>12.4f}+/-{np.std(c) if c else 0:.2f}"
              f"  {delta:>+10.4f}"
              f"  {len(s):>8}  {len(c):>8}")

        if s and c:
            same_means.append(s_mean)
            cross_means.append(c_mean)
            dists.append(d)

    # Compute decay rates (linear regression on log-distance vs similarity)
    if len(dists) >= 3:
        log_d = np.log(dists)
        same_arr = np.array(same_means)
        cross_arr = np.array(cross_means)

        # Linear fit: sim = a * log(d) + b
        same_slope = np.polyfit(log_d, same_arr, 1)[0]
        cross_slope = np.polyfit(log_d, cross_arr, 1)[0]

        print(f"\nDecay rates (similarity per log-distance):")
        print(f"  Same-chunk:  {same_slope:+.4f}")
        print(f"  Cross-chunk: {cross_slope:+.4f}")

        if abs(same_slope - cross_slope) < 0.01:
            print(f"  -> SAME RATE: boundary effect only (prediction confirmed)")
        elif abs(same_slope) < abs(cross_slope):
            print(f"  -> SLOWER within-chunk decay: genuine spatial coherence")
            print(f"  -> STRONGER POSITIVE for perspectives hypothesis")
        else:
            print(f"  -> FASTER within-chunk decay (unexpected)")

    return dists, same_means, cross_means


def boundary_profile(f3_rep, chunk_size=32, window=8, max_samples=50):
    """
    Show the similarity profile AROUND chunk boundaries.

    For each boundary, compute consecutive-token similarity
    for positions -window to +window relative to the boundary.
    """
    B, T, D = f3_rep.shape
    B = min(B, max_samples)

    rep_norm = F.normalize(f3_rep[:B], dim=-1)
    consecutive_sim = (rep_norm[:, :-1, :] * rep_norm[:, 1:, :]).sum(dim=-1)
    # B, T-1

    n_chunks = T // chunk_size
    profile = {offset: [] for offset in range(-window, window + 1)}

    for c in range(1, n_chunks):  # skip first boundary (no left context)
        boundary_pos = c * chunk_size - 1  # last position before boundary
        for offset in range(-window, window + 1):
            pos = boundary_pos + offset
            if 0 <= pos < T - 1:
                profile[offset].extend(consecutive_sim[:, pos].tolist())

    print(f"\n{'='*70}")
    print("BOUNDARY PROFILE — Consecutive similarity near chunk boundaries")
    print(f"{'='*70}")
    print(f"  Offset 0 = the boundary itself (last token of chunk to first of next)")
    print(f"  Negative offsets = inside the ending chunk")
    print(f"  Positive offsets = inside the starting chunk")
    print()

    for offset in range(-window, window + 1):
        vals = profile[offset]
        if vals:
            mean = np.mean(vals)
            bar_len = int((mean + 1) * 20)  # scale to ~40 chars
            bar = "#" * bar_len
            marker = " <-- BOUNDARY" if offset == 0 else ""
            print(f"  {offset:>+3}: {mean:.4f} {bar}{marker}")

    return profile


def main():
    print("=" * 70)
    print("OQ30 EXTENSION: Distance & Boundary Profile Analysis")
    print("=" * 70)

    model_path = os.path.join(os.path.dirname(__file__), "filtnet_v4.pt")
    if not os.path.exists(model_path):
        print(f"ERROR: {model_path} not found.")
        return

    model = FiltrationNetV4(
        vocab_size=500, dim=128, n_heads=4, n_classes=4,
        pool_factor=4, membrane_thickness=0.5, consistency_weight=0.1,
    )
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    print("Model loaded.")

    ds = ScalableHierarchicalDataset(
        n_samples=200, seq_len=512, vocab_size=500, zone_size=32, seed=999
    )
    inputs = ds.samples
    labels = ds.labels

    print("Extracting F3 representations...")
    f3_rep = get_level3_representations(model, inputs)
    print(f"Shape: {f3_rep.shape}")

    # Distance analysis
    results = distance_analysis(f3_rep, chunk_size=32)
    dists, same_means, cross_means = print_distance_table(results)

    # Boundary profile
    profile = boundary_profile(f3_rep, chunk_size=32, window=8)

    # Overall verdict
    print(f"\n{'='*70}")
    print("VERDICT")
    print("=" * 70)
    print("If decay rates are the same: boundary discontinuity without")
    print("internal coherence. Chunks are processing units, not perspectives.")
    print()
    print("If same-chunk decays slower: genuine spatial coherence.")
    print("Chunks create neighborhoods, not just containers.")
    print("The efficiency structure creates REAL locality in representation space.")


if __name__ == "__main__":
    main()
