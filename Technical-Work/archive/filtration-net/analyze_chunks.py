"""
Chunk Boundary Analysis — Open Question 30

Do the chunk boundaries in ChunkedLocalAttention create observable
"perspectives" in the hidden states?

If the efficiency structure creates locality, and locality creates
perspectives, then:
1. Within-chunk representations should be more similar than cross-chunk
2. Chunks should develop content-dependent specializations
3. The chunk boundary should be a genuine information boundary

Run AFTER v0.4 training completes (requires filtnet_v4.pt).
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
    """
    Extract the F3 (level 3) representations after chunked local attention.
    These are the representations BEFORE pooling — each chunk was processed
    independently, so cross-chunk information hasn't mixed yet.
    """
    model.eval()
    with torch.no_grad():
        B, T = input_ids.shape
        pos_enc = sinusoidal_encoding(T, model.dim, input_ids.device)
        x = model.token_embed(input_ids) + pos_enc.unsqueeze(0)

        # F3 descent: chunked local attention
        f3_rep = model.f3_descent(x)  # B, T, D — processed within chunks

    return f3_rep


def analyze_within_vs_across_chunks(f3_rep, chunk_size=32):
    """
    Compare representation similarity within chunks vs across chunks.

    If chunks create "perspectives," within-chunk similarity should be
    higher than across-chunk similarity.
    """
    B, T, D = f3_rep.shape
    n_chunks = T // chunk_size

    within_sims = []
    across_sims = []

    for b in range(B):
        rep = f3_rep[b]  # T, D

        # Compute within-chunk pairwise cosine similarity
        for c in range(n_chunks):
            start = c * chunk_size
            end = start + chunk_size
            chunk_rep = rep[start:end]  # chunk_size, D
            chunk_rep_norm = F.normalize(chunk_rep, dim=-1)
            sim_matrix = torch.mm(chunk_rep_norm, chunk_rep_norm.t())
            # Upper triangle (excluding diagonal)
            mask = torch.triu(torch.ones(chunk_size, chunk_size), diagonal=1)
            within_sims.extend(sim_matrix[mask.bool()].tolist())

        # Compute across-chunk similarity (boundary tokens)
        for c in range(n_chunks - 1):
            # Last token of chunk c, first token of chunk c+1
            boundary_left = rep[c * chunk_size + chunk_size - 1]
            boundary_right = rep[(c + 1) * chunk_size]
            sim = F.cosine_similarity(
                boundary_left.unsqueeze(0),
                boundary_right.unsqueeze(0)
            ).item()
            across_sims.append(sim)

            # Also: mean of last 4 tokens vs mean of first 4 tokens
            left_mean = rep[c * chunk_size + chunk_size - 4:
                           c * chunk_size + chunk_size].mean(0)
            right_mean = rep[(c + 1) * chunk_size:
                            (c + 1) * chunk_size + 4].mean(0)
            sim = F.cosine_similarity(
                left_mean.unsqueeze(0), right_mean.unsqueeze(0)
            ).item()
            across_sims.append(sim)

    return np.mean(within_sims), np.std(within_sims), \
           np.mean(across_sims), np.std(across_sims)


def analyze_chunk_specialization(f3_rep, labels, chunk_size=32):
    """
    Do chunks develop content-dependent specializations?

    For sequences with the same label, are corresponding chunks
    (same position) more similar than non-corresponding chunks?
    """
    B, T, D = f3_rep.shape
    n_chunks = T // chunk_size

    # Compute chunk-level representations (mean pool within each chunk)
    chunk_reps = f3_rep.view(B, n_chunks, chunk_size, D).mean(dim=2)  # B, n_chunks, D

    # For each class, compute within-class chunk similarity
    results = {}
    for cls in range(4):
        mask = labels == cls
        if mask.sum() < 2:
            continue
        cls_chunks = chunk_reps[mask]  # N_cls, n_chunks, D
        N = cls_chunks.size(0)

        # Same-position similarity (do same chunks across samples agree?)
        same_pos_sims = []
        for c in range(n_chunks):
            chunk_c = F.normalize(cls_chunks[:, c, :], dim=-1)  # N, D
            sim = torch.mm(chunk_c, chunk_c.t())
            mask_upper = torch.triu(torch.ones(N, N), diagonal=1).bool()
            same_pos_sims.extend(sim[mask_upper].tolist())

        # Different-position similarity
        diff_pos_sims = []
        for c1 in range(min(n_chunks, 4)):
            for c2 in range(c1 + 1, min(n_chunks, 4)):
                chunk_1 = F.normalize(cls_chunks[:, c1, :], dim=-1)
                chunk_2 = F.normalize(cls_chunks[:, c2, :], dim=-1)
                # Cross: how similar is chunk c1 of sample i to chunk c2 of sample j?
                sim = torch.mm(chunk_1, chunk_2.t())
                diff_pos_sims.extend(sim.flatten().tolist())

        results[cls] = {
            "same_pos": (np.mean(same_pos_sims), np.std(same_pos_sims)),
            "diff_pos": (np.mean(diff_pos_sims), np.std(diff_pos_sims)),
        }

    return results


def analyze_boundary_gradient(f3_rep, chunk_size=32):
    """
    Is there a gradient at chunk boundaries?

    If chunks are independent "perspectives," there should be a
    discontinuity at the boundary — a jump in representation space.
    Measure the cosine distance between consecutive tokens across
    the entire sequence, and check if boundary positions show larger jumps.
    """
    B, T, D = f3_rep.shape

    # Cosine distance between consecutive tokens
    rep_norm = F.normalize(f3_rep, dim=-1)
    consecutive_sim = (rep_norm[:, :-1, :] * rep_norm[:, 1:, :]).sum(dim=-1)
    # consecutive_sim: B, T-1

    # Separate boundary positions from non-boundary positions
    boundary_positions = set(range(chunk_size - 1, T - 1, chunk_size))
    non_boundary = []
    boundary = []

    for pos in range(T - 1):
        if pos in boundary_positions:
            boundary.extend(consecutive_sim[:, pos].tolist())
        else:
            non_boundary.extend(consecutive_sim[:, pos].tolist())

    return (np.mean(boundary), np.std(boundary),
            np.mean(non_boundary), np.std(non_boundary))


def main():
    print("=" * 60)
    print("CHUNK BOUNDARY ANALYSIS — Open Question 30")
    print("=" * 60)

    # Load model
    model_path = os.path.join(os.path.dirname(__file__), "filtnet_v4.pt")
    if not os.path.exists(model_path):
        print(f"ERROR: {model_path} not found. Run train_v4.py first.")
        return

    model = FiltrationNetV4(
        vocab_size=500, dim=128, n_heads=4, n_classes=4,
        pool_factor=4, membrane_thickness=0.5, consistency_weight=0.1,
    )
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    print("Model loaded.\n")

    # Generate test data
    print("Generating test data...")
    ds = ScalableHierarchicalDataset(
        n_samples=200, seq_len=512, vocab_size=500, zone_size=32, seed=999
    )

    inputs = ds.samples  # 200, 512
    labels = ds.labels   # 200

    # Get level 3 representations
    print("Extracting F3 representations...\n")
    f3_rep = get_level3_representations(model, inputs)

    # === Test 1: Within vs Across chunk similarity ===
    print("-" * 60)
    print("TEST 1: Within-chunk vs across-chunk similarity")
    print("-" * 60)
    within_mean, within_std, across_mean, across_std = \
        analyze_within_vs_across_chunks(f3_rep, chunk_size=32)

    print(f"  Within-chunk similarity:  {within_mean:.4f} +/- {within_std:.4f}")
    print(f"  Across-chunk similarity:  {across_mean:.4f} +/- {across_std:.4f}")
    diff = within_mean - across_mean
    print(f"  Difference: {diff:.4f}")
    if diff > 0.01:
        print(f"  -> Chunks have HIGHER internal similarity than cross-boundary")
        print(f"  -> Evidence for chunk boundaries as perspectival boundaries")
    elif diff < -0.01:
        print(f"  -> Cross-boundary similarity is HIGHER (unexpected)")
    else:
        print(f"  -> No significant difference")

    # === Test 2: Boundary gradient ===
    print(f"\n{'-'*60}")
    print("TEST 2: Representation discontinuity at chunk boundaries")
    print("-" * 60)
    bound_mean, bound_std, nonbound_mean, nonbound_std = \
        analyze_boundary_gradient(f3_rep, chunk_size=32)

    print(f"  Boundary token similarity:     {bound_mean:.4f} +/- {bound_std:.4f}")
    print(f"  Non-boundary token similarity: {nonbound_mean:.4f} +/- {nonbound_std:.4f}")
    boundary_drop = nonbound_mean - bound_mean
    print(f"  Boundary drop: {boundary_drop:.4f}")
    if boundary_drop > 0.01:
        print(f"  -> DISCONTINUITY at chunk boundaries")
        print(f"  -> Chunk boundaries are information boundaries")
    elif boundary_drop < -0.01:
        print(f"  -> Boundary tokens are MORE similar (unexpected)")
    else:
        print(f"  -> No significant discontinuity")

    # === Test 3: Chunk specialization by class ===
    print(f"\n{'-'*60}")
    print("TEST 3: Chunk specialization by content class")
    print("-" * 60)
    spec = analyze_chunk_specialization(f3_rep, labels, chunk_size=32)

    for cls, data in sorted(spec.items()):
        sp_m, sp_s = data["same_pos"]
        dp_m, dp_s = data["diff_pos"]
        diff = sp_m - dp_m
        marker = "*" if diff > 0.01 else ""
        print(f"  Class {cls}: same-position={sp_m:.4f}+/-{sp_s:.4f}  "
              f"diff-position={dp_m:.4f}+/-{dp_s:.4f}  "
              f"delta={diff:+.4f} {marker}")

    # === Summary ===
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("=" * 60)
    print(f"Within vs across chunk: delta = {within_mean - across_mean:+.4f}")
    print(f"Boundary discontinuity: delta = {nonbound_mean - bound_mean:+.4f}")
    print(f"\nInterpretation:")
    if (within_mean - across_mean > 0.01 and
            nonbound_mean - bound_mean > 0.01):
        print("  POSITIVE: Chunk boundaries create observable perspectival")
        print("  boundaries. The efficiency structure IS the locality structure.")
    elif within_mean - across_mean > 0.01:
        print("  PARTIAL: Within-chunk coherence exists but boundaries aren't sharp.")
    else:
        print("  NEGATIVE: No evidence for perspectival boundaries at chunk edges.")
        print("  The efficiency structure may not directly create locality in the")
        print("  representation space.")

    print(flush=True)


if __name__ == "__main__":
    main()
