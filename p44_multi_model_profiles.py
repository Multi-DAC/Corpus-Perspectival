"""
P44: Multi-model Killing form profiles for Meridian Bridge Test
Runs per-layer CommVar and AF on multiple architectures to expand
the parallel/sequential dataset from n=7 to n=12+.

Uses identical computation to P43: PROJ_DIM=64, SEED=71, AF_THRESHOLD=0.10

New models:
  Parallel:  Pythia-70m, Pythia-160m, Gemma-2-2b, Phi-2
  Sequential: Qwen2.5-0.5B
"""
import numpy as np
from scipy import stats
import torch
import json
import time
import sys
import os

# ============================================================
# Constants (must match P43 exactly)
# ============================================================
PROJ_DIM = 64
SEED = 71
AF_THRESHOLD = 0.10

# ============================================================
# Model definitions
# ============================================================
MODELS = [
    # d_head=64 family (parallel) — most comparable
    {
        'id': 'EleutherAI/pythia-70m-deduped',
        'name': 'Pythia-70m',
        'arch': 'parallel',
        'q_pattern': 'gpt_neox.layers.{L}.attention.query_key_value.weight',
        'qkv_split': 'first_third',
        'n_heads': 8, 'n_layers': 6, 'd_model': 512, 'd_head': 64,
    },
    {
        'id': 'EleutherAI/pythia-160m-deduped',
        'name': 'Pythia-160m',
        'arch': 'parallel',
        'q_pattern': 'gpt_neox.layers.{L}.attention.query_key_value.weight',
        'qkv_split': 'first_third',
        'n_heads': 12, 'n_layers': 12, 'd_model': 768, 'd_head': 64,
    },
    # d_head=64 family (sequential) — new
    {
        'id': 'Qwen/Qwen2.5-0.5B',
        'name': 'Qwen2.5-0.5B',
        'arch': 'sequential',
        'q_pattern': 'model.layers.{L}.self_attn.q_proj.weight',
        'qkv_split': 'none',
        'n_heads': 14, 'n_layers': 24, 'd_model': 896, 'd_head': 64,
    },
    # Parallel, different d_head — broadens the test
    {
        'id': 'google/gemma-2-2b',
        'name': 'Gemma-2-2b',
        'arch': 'parallel',
        'q_pattern': 'model.layers.{L}.self_attn.q_proj.weight',
        'qkv_split': 'none',
        'n_heads': 8, 'n_layers': 26, 'd_model': 2304, 'd_head': 256,
    },
    {
        'id': 'microsoft/phi-2',
        'name': 'Phi-2',
        'arch': 'parallel',
        'q_pattern': 'model.layers.{L}.self_attn.q_proj.weight',
        'qkv_split': 'none',
        'n_heads': 32, 'n_layers': 32, 'd_model': 2560, 'd_head': 80,
    },
]


def extract_q_heads(state_dict, cfg):
    """Extract per-head Q-projection weights for all layers."""
    layers = []
    for L in range(cfg['n_layers']):
        key = cfg['q_pattern'].format(L=L)
        if key not in state_dict:
            print(f"  WARNING: key {key} not found, trying alternatives...")
            # Try common alternatives
            for alt in [
                f"transformer.h.{L}.attn.c_attn.weight",
                f"model.layers.{L}.self_attn.q_proj.weight",
                f"gpt_neox.layers.{L}.attention.query_key_value.weight",
            ]:
                if alt in state_dict:
                    key = alt
                    print(f"  Found: {alt}")
                    break
            else:
                print(f"  ERROR: No Q-projection found for layer {L}")
                return None

        W = state_dict[key].float().cpu().numpy()

        # Handle fused QKV vs separate Q
        if cfg['qkv_split'] == 'first_third':
            d = cfg['d_model']
            W_Q = W[:d, :]  # First third of fused QKV (shape: d_model x d_model)
        elif cfg['qkv_split'] == 'none':
            W_Q = W  # Already just Q (shape: n_heads*d_head x d_model)
        else:
            W_Q = W

        # Split into per-head matrices
        d_head = cfg['d_head']
        n_heads = cfg['n_heads']
        heads = []
        for h in range(n_heads):
            Wh = W_Q[h * d_head:(h + 1) * d_head, :]  # (d_head x d_model)
            heads.append(Wh)
        layers.append(heads)

    return layers


def compute_layer_metrics(heads, d_head, d_model):
    """Compute CommVar and AF for one layer, matching P43 exactly."""
    np.random.seed(SEED)
    n_h = len(heads)

    # Random projection to PROJ_DIM x PROJ_DIM
    p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)
    proj = [p_out @ A @ p_in for A in heads]

    # --- Killing form ---
    killing = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(n_h):
            val = 0.0
            for k in range(n_h):
                c1 = proj[h] @ proj[k] - proj[k] @ proj[h]
                c2 = proj[hp] @ proj[k] - proj[k] @ proj[hp]
                val += np.trace(c1.T @ c2)
            killing[h, hp] = val

    mx = np.max(np.abs(killing))
    kn = killing / mx if mx > 0 else killing
    evs = np.sort(np.abs(np.linalg.eigvalsh(kn)))
    af = int(np.sum(evs < AF_THRESHOLD)) / n_h

    # --- Commutator variance ---
    norms = np.zeros((n_h, n_h))
    for h in range(n_h):
        for hp in range(h + 1, n_h):
            c = proj[h] @ proj[hp] - proj[hp] @ proj[h]
            norms[h, hp] = np.linalg.norm(c, 'fro')
            norms[hp, h] = norms[h, hp]

    typ = np.mean([np.linalg.norm(A, 'fro') for A in proj])
    if typ > 0:
        norms /= typ ** 2

    mask = np.ones_like(norms, dtype=bool)
    np.fill_diagonal(mask, False)
    cv = float(np.var(norms[mask]))

    return af, cv


def profile_model(cfg):
    """Full pipeline: load model, extract Q, compute per-layer metrics."""
    print(f"\n{'='*60}")
    print(f"  {cfg['name']} ({cfg['id']})")
    print(f"  {cfg['arch']}, {cfg['n_layers']}L, {cfg['n_heads']}h, d_head={cfg['d_head']}")
    print(f"{'='*60}")

    t0 = time.time()

    # Load state dict only (no need for full model)
    from transformers import AutoModelForCausalLM
    print(f"  Loading weights...", end=" ", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        cfg['id'], torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )
    state_dict = model.state_dict()
    del model
    torch.cuda.empty_cache()
    print(f"done ({time.time()-t0:.1f}s)")

    # Extract Q heads
    print(f"  Extracting Q-projections...", end=" ", flush=True)
    layers = extract_q_heads(state_dict, cfg)
    del state_dict
    if layers is None:
        return None
    print(f"done ({len(layers)} layers)")

    # Compute per-layer metrics
    layer_cvs = []
    layer_afs = []
    for L_idx, heads in enumerate(layers):
        af, cv = compute_layer_metrics(heads, cfg['d_head'], cfg['d_model'])
        layer_afs.append(af)
        layer_cvs.append(cv)
        print(f"  Layer {L_idx:2d}: AF={af:.3f}, CV={cv:.6f}")

    # Depth statistics
    d = np.arange(len(layer_cvs))
    rho, p_rho = stats.spearmanr(d, layer_cvs)
    rho_af, p_af = stats.spearmanr(d, layer_afs)

    result = {
        'model': cfg['id'],
        'name': cfg['name'],
        'arch': cfg['arch'],
        'n_heads': cfg['n_heads'],
        'n_layers': cfg['n_layers'],
        'd_model': cfg['d_model'],
        'd_head': cfg['d_head'],
        'layer_cvs': layer_cvs,
        'layer_afs': layer_afs,
        'mean_cv': float(np.mean(layer_cvs)),
        'mean_af': float(np.mean(layer_afs)),
        'r_cv_depth': float(rho),
        'p_cv_depth': float(p_rho),
        'r_af_depth': float(rho_af),
        'p_af_depth': float(p_af),
    }

    elapsed = time.time() - t0
    print(f"\n  RESULT: r(CV,depth) = {rho:+.3f} (p={p_rho:.4f})")
    print(f"  Mean AF = {np.mean(layer_afs):.4f}, Mean CV = {np.mean(layer_cvs):.6f}")
    print(f"  Elapsed: {elapsed:.1f}s")

    return result


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    # Allow running specific models via command line
    if len(sys.argv) > 1:
        names = [a.lower() for a in sys.argv[1:]]
        models_to_run = [m for m in MODELS if any(n in m['name'].lower() for n in names)]
    else:
        models_to_run = MODELS

    print(f"Running {len(models_to_run)} models:")
    for m in models_to_run:
        print(f"  {m['name']} ({m['arch']}, {m['n_layers']}L, d_head={m['d_head']})")

    results = {}
    for cfg in models_to_run:
        try:
            r = profile_model(cfg)
            if r:
                results[cfg['name']] = r
                # Save incrementally
                outpath = os.path.join(os.path.dirname(__file__),
                                       'p44_multi_results.json')
                with open(outpath, 'w') as f:
                    json.dump(results, f, indent=2)
                print(f"  Saved to p44_multi_results.json ({len(results)} models)")
        except Exception as e:
            print(f"  ERROR on {cfg['name']}: {e}")
            import traceback
            traceback.print_exc()

    # Final summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(results)} models profiled")
    print(f"{'='*60}")
    print(f"{'Model':20s} {'Arch':10s} {'dh':>3s} {'r(CV)':>7s} {'p':>8s} {'AF':>6s}")
    print("-" * 60)
    for name, r in results.items():
        print(f"{name:20s} {r['arch']:10s} {r['d_head']:3d} "
              f"{r['r_cv_depth']:+7.3f} {r['p_cv_depth']:8.4f} {r['mean_af']:6.3f}")
