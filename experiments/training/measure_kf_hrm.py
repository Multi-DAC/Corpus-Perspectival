"""
Killing Form Measurement for HRM
=================================
Measures algebraic structure (commutator variance, Killing form eigenspectra)
on HRM's H-module vs L-module attention heads.

Tests the universality hypothesis: does hierarchical reasoning architecture
develop the same algebraic focusing structure seen in LLM attention heads?
"""
import sys
import os
import json
import torch
import numpy as np
from pathlib import Path

# Add HRM root to path
sys.path.insert(0, '/home/clawd/HRM')

from omegaconf import OmegaConf


def extract_attention_weights(model):
    """Extract per-head Q, K weight matrices from H and L modules."""
    heads = {'H': [], 'L': []}

    for module_name, module in [('H', model.inner.H_level), ('L', model.inner.L_level)]:
        for layer_idx, layer in enumerate(module.layers):
            W = layer.self_attn.qkv_proj.weight.detach().float()  # [1536, 512]
            num_heads = layer.self_attn.num_heads
            head_dim = layer.self_attn.head_dim

            W_Q = W[:num_heads * head_dim, :]  # [512, 512]
            W_K = W[num_heads * head_dim: 2 * num_heads * head_dim, :]  # [512, 512]

            for h in range(num_heads):
                q_h = W_Q[h * head_dim:(h + 1) * head_dim, :]  # [64, 512]
                k_h = W_K[h * head_dim:(h + 1) * head_dim, :]  # [64, 512]
                W_h = q_h.T @ k_h  # [512, 512] effective attention matrix
                heads[module_name].append({
                    'layer': layer_idx,
                    'head': h,
                    'W': W_h,
                    'W_Q': q_h,
                    'W_K': k_h
                })
    return heads


def compute_commutator(A, B):
    """Compute [A, B] = AB - BA"""
    return A @ B - B @ A


def compute_killing_form_entry(Wi, Wj, Wk_list):
    """Compute kappa_{ij} = sum_k Tr([W_i, W_k][W_j, W_k])"""
    val = 0.0
    for Wk_info in Wk_list:
        Wk = Wk_info['W']
        comm_ik = compute_commutator(Wi, Wk)
        comm_jk = compute_commutator(Wj, Wk)
        val += torch.trace(comm_ik @ comm_jk).item()
    return val


def compute_commutator_variance(heads_list):
    """Compute commutator variance across all head pairs.
    CV = Var(||[W_i, W_j]||_F) over all pairs i!=j
    """
    n = len(heads_list)
    if n < 2:
        return 0.0

    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = compute_commutator(heads_list[i]['W'], heads_list[j]['W'])
            norms.append(torch.norm(comm, p='fro').item())

    norms = np.array(norms)
    return float(np.var(norms))


def compute_mean_commutator_norm(heads_list):
    """Mean ||[W_i, W_j]||_F over all pairs."""
    n = len(heads_list)
    if n < 2:
        return 0.0

    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = compute_commutator(heads_list[i]['W'], heads_list[j]['W'])
            norms.append(torch.norm(comm, p='fro').item())

    return float(np.mean(norms))


def compute_abelian_fraction(heads_list, threshold=1e-6):
    """Fraction of head pairs with near-zero commutators.
    AF ~ 0 means highly non-commutative (complex algebra).
    AF ~ 1 means nearly Abelian (independent heads).
    """
    n = len(heads_list)
    if n < 2:
        return 0.0

    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = compute_commutator(heads_list[i]['W'], heads_list[j]['W'])
            norms.append(torch.norm(comm, p='fro').item())

    norms = np.array(norms)
    max_norm = np.max(norms) if len(norms) > 0 else 1.0
    rel_threshold = threshold * max_norm
    abelian_count = np.sum(norms < rel_threshold)
    return float(abelian_count / len(norms))


def compute_killing_form_matrix(heads_list):
    """Full Killing form matrix kappa_{ab} for all heads."""
    n = len(heads_list)
    kappa = np.zeros((n, n))

    for a in range(n):
        for b in range(a, n):
            val = compute_killing_form_entry(
                heads_list[a]['W'], heads_list[b]['W'], heads_list
            )
            kappa[a, b] = val
            kappa[b, a] = val

    return kappa


def analyze_module(heads_list, module_name):
    """Full algebraic analysis of one module's attention heads."""
    layers = sorted(set(h['layer'] for h in heads_list))
    n_layers = len(layers)
    n_heads_per_layer = len(heads_list) // n_layers if n_layers > 0 else 0

    print(f"\n{'='*60}")
    print(f"  {module_name}-MODULE ALGEBRAIC ANALYSIS")
    print(f"  {len(heads_list)} heads ({n_layers} layers x {n_heads_per_layer} heads/layer)")
    print(f"{'='*60}")

    cv = compute_commutator_variance(heads_list)
    mean_norm = compute_mean_commutator_norm(heads_list)
    af = compute_abelian_fraction(heads_list)

    print(f"\n  Commutator Variance (CV):     {cv:.6e}")
    print(f"  Mean Commutator Norm:          {mean_norm:.6e}")
    print(f"  Abelian Fraction (AF):         {af:.4f}")

    # Per-layer analysis
    print(f"\n  Per-Layer Breakdown:")
    per_layer = {}
    for layer in layers:
        layer_heads = [h for h in heads_list if h['layer'] == layer]
        layer_cv = compute_commutator_variance(layer_heads)
        layer_mean = compute_mean_commutator_norm(layer_heads)
        layer_af = compute_abelian_fraction(layer_heads)
        per_layer[int(layer)] = {'cv': layer_cv, 'mean_norm': layer_mean, 'af': layer_af}
        print(f"    Layer {layer}: CV={layer_cv:.6e}  MeanNorm={layer_mean:.6e}  AF={layer_af:.4f}")

    # Killing form matrix
    print(f"\n  Computing Killing form matrix ({len(heads_list)}x{len(heads_list)})...")
    kappa = compute_killing_form_matrix(heads_list)
    eigvals = np.linalg.eigvalsh(kappa)
    eigvals_sorted = np.sort(eigvals)[::-1]

    print(f"  KF Eigenspectrum (top 8):  {np.array2string(eigvals_sorted[:8], precision=4)}")
    print(f"  KF Trace:                  {np.trace(kappa):.6e}")
    kf_rank = int(np.sum(np.abs(eigvals) > 1e-6 * np.max(np.abs(eigvals))))
    print(f"  KF Rank (>1e-6 of max):    {kf_rank}/{len(eigvals)}")

    # Spectral entropy
    abs_eig = np.abs(eigvals_sorted)
    abs_eig = abs_eig[abs_eig > 0]
    spectral_entropy = 0.0
    max_entropy = 0.0
    if len(abs_eig) > 0:
        probs = abs_eig / abs_eig.sum()
        spectral_entropy = float(-np.sum(probs * np.log(probs + 1e-12)))
        max_entropy = float(np.log(len(abs_eig)))
        norm_entropy = spectral_entropy / max_entropy if max_entropy > 0 else 0
        print(f"  Spectral Entropy:          {spectral_entropy:.4f} / {max_entropy:.4f} (normalized: {norm_entropy:.4f})")

    return {
        'cv': cv,
        'mean_commutator_norm': mean_norm,
        'abelian_fraction': af,
        'per_layer': per_layer,
        'kf_eigenvalues': eigvals_sorted.tolist(),
        'kf_trace': float(np.trace(kappa)),
        'kf_rank': kf_rank,
        'spectral_entropy': spectral_entropy,
        'max_entropy': max_entropy,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, default=None,
                       help='Path to trained checkpoint (.pt file)')
    parser.add_argument('--output', type=str, default='kf_hrm_results.json')
    args = parser.parse_args()

    # Load config
    arch_cfg = OmegaConf.load('/home/clawd/HRM/config/arch/hrm_v1.yaml')
    print(f"HRM Architecture Config:")
    print(f"  H_layers={arch_cfg.H_layers}, L_layers={arch_cfg.L_layers}")
    print(f"  hidden_size={arch_cfg.hidden_size}, num_heads={arch_cfg.num_heads}")
    print(f"  H_cycles={arch_cfg.H_cycles}, L_cycles={arch_cfg.L_cycles}")

    # Build model
    from models.hrm.hrm_act_v1 import HierarchicalReasoningModel_ACTV1

    vocab_size = arch_cfg.get('vocab_size', 1024)

    full_cfg = OmegaConf.create({
        **OmegaConf.to_container(arch_cfg),
        'vocab_size': vocab_size,
        'max_seq_len': 256,
        'batch_size': 1,
        'seq_len': 256,
        'num_puzzle_identifiers': 1000,
    })

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"\nInstantiating model on {device}...")
    model = HierarchicalReasoningModel_ACTV1(full_cfg).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")

    state = 'random_init'
    if args.checkpoint:
        print(f"Loading checkpoint: {args.checkpoint}")
        ckpt = torch.load(args.checkpoint, map_location=device, weights_only=False)
        if 'model_state_dict' in ckpt:
            model.load_state_dict(ckpt['model_state_dict'], strict=False)
        elif 'model' in ckpt:
            model.load_state_dict(ckpt['model'], strict=False)
        else:
            model.load_state_dict(ckpt, strict=False)
        state = 'trained'
        print("Checkpoint loaded.")

    model.eval()

    # Extract attention weights
    print("\nExtracting attention weights...")
    heads = extract_attention_weights(model)

    print(f"Extracted: H={len(heads['H'])} heads, L={len(heads['L'])} heads")

    # Analyze each module
    results = {'state': state, 'total_params': total_params}
    results['H_module'] = analyze_module(heads['H'], 'H (Strategic)')
    results['L_module'] = analyze_module(heads['L'], 'L (Execution)')

    # Cross-module analysis
    print(f"\n{'='*60}")
    print(f"  CROSS-MODULE COMPARISON")
    print(f"{'='*60}")

    all_heads = heads['H'] + heads['L']
    all_cv = compute_commutator_variance(all_heads)

    # Cross-module commutators
    cross_norms = []
    for h_head in heads['H']:
        for l_head in heads['L']:
            comm = compute_commutator(h_head['W'], l_head['W'])
            cross_norms.append(torch.norm(comm, p='fro').item())

    cross_mean = float(np.mean(cross_norms))
    cross_var = float(np.var(cross_norms))

    h_cv = results['H_module']['cv']
    l_cv = results['L_module']['cv']
    ratio = h_cv / (l_cv + 1e-20)

    print(f"\n  Full model CV:               {all_cv:.6e}")
    print(f"  H-module CV:                 {h_cv:.6e}")
    print(f"  L-module CV:                 {l_cv:.6e}")
    print(f"  H/L CV ratio:                {ratio:.4f}")
    print(f"\n  Cross-module mean comm norm: {cross_mean:.6e}")
    print(f"  Cross-module comm variance:  {cross_var:.6e}")
    print(f"  H mean norm:                 {results['H_module']['mean_commutator_norm']:.6e}")
    print(f"  L mean norm:                 {results['L_module']['mean_commutator_norm']:.6e}")

    results['cross_module'] = {
        'full_cv': all_cv,
        'cross_mean_norm': cross_mean,
        'cross_variance': cross_var,
        'h_l_cv_ratio': ratio,
    }

    # Summary
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  State: {state}")
    print(f"  H-module (strategic):  CV={h_cv:.6e}, AF={results['H_module']['abelian_fraction']:.4f}")
    print(f"  L-module (execution):  CV={l_cv:.6e}, AF={results['L_module']['abelian_fraction']:.4f}")

    if h_cv > l_cv:
        print(f"  => H-module has HIGHER algebraic complexity (as predicted)")
    else:
        print(f"  => L-module has higher algebraic complexity (unexpected if H=strategic)")

    # Save
    def convert(obj):
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert(v) for v in obj]
        return obj

    with open(args.output, 'w') as f:
        json.dump(convert(results), f, indent=2)
    print(f"\nResults saved to {args.output}")


if __name__ == '__main__':
    main()
