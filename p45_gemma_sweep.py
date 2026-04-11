"""
P45: Gemma Sweep — All accessible Gemma generations

ALL Gemma models have d_head=256. This tests:
1. Does the depth gradient change across Gemma 1/2/3?
2. Does model size matter within a generation?
3. Does PROJ_DIM=256 (matching d_head) change the result?

Also runs PROJ_DIM=256 on Gemma-2-2b as a control experiment
to test whether the negative gradient in P44 was a projection artifact.
"""
import numpy as np
from scipy import stats
import torch
import json
import time
import sys
import os
import gc

SEED = 71
AF_THRESHOLD = 0.10
BASE = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.'

GEMMA_MODELS = [
    {
        'id': 'google/gemma-3-270m',
        'name': 'Gemma3-270m',
        'gen': 3,
        'n_heads': 4, 'n_kv_heads': 1, 'n_layers': 18,
        'd_model': 640, 'd_head': 256,
        'q_pattern': 'model.layers.{L}.self_attn.q_proj.weight',
    },
    {
        'id': 'google/gemma-2b',
        'name': 'Gemma1-2b',
        'gen': 1,
        'n_heads': 8, 'n_kv_heads': 1, 'n_layers': 18,
        'd_model': 2048, 'd_head': 256,
        'q_pattern': 'model.layers.{L}.self_attn.q_proj.weight',
    },
    {
        'id': 'google/gemma-3-1b-pt',
        'name': 'Gemma3-1b',
        'gen': 3,
        'n_heads': 4, 'n_kv_heads': 1, 'n_layers': 26,
        'd_model': 1152, 'd_head': 256,
        'q_pattern': 'model.layers.{L}.self_attn.q_proj.weight',
    },
    {
        'id': 'google/gemma-2-2b',
        'name': 'Gemma2-2b',
        'gen': 2,
        'n_heads': 8, 'n_kv_heads': 4, 'n_layers': 26,
        'd_model': 2304, 'd_head': 256,
        'q_pattern': 'model.layers.{L}.self_attn.q_proj.weight',
    },
    {
        'id': 'google/gemma-2-9b',
        'name': 'Gemma2-9b',
        'gen': 2,
        'n_heads': 16, 'n_kv_heads': 8, 'n_layers': 42,
        'd_model': 3584, 'd_head': 256,
        'q_pattern': 'model.layers.{L}.self_attn.q_proj.weight',
    },
]


def extract_q_heads(state_dict, cfg):
    """Extract per-head Q-projection weights for all layers."""
    layers = []
    for L in range(cfg['n_layers']):
        key = cfg['q_pattern'].format(L=L)
        if key not in state_dict:
            print(f"  WARNING: {key} not found!")
            # Try scanning for q_proj
            for k in state_dict:
                if f'.{L}.' in k and 'q_proj' in k:
                    key = k
                    print(f"  Found: {k}")
                    break
            else:
                return None

        W = state_dict[key].float().cpu().numpy()
        d_head = cfg['d_head']
        n_heads = cfg['n_heads']
        heads = []
        for h in range(n_heads):
            Wh = W[h * d_head:(h + 1) * d_head, :]
            heads.append(Wh)
        layers.append(heads)
    return layers


def compute_layer_metrics(heads, d_head, d_model, proj_dim=64):
    """Compute CommVar and AF with configurable projection dimension."""
    np.random.seed(SEED)
    n_h = len(heads)

    p_out = np.random.randn(proj_dim, d_head) / np.sqrt(d_head)
    p_in = np.random.randn(d_model, proj_dim) / np.sqrt(d_model)
    proj = [p_out @ A @ p_in for A in heads]

    # Killing form
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

    # Commutator variance
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


def profile_model(cfg, proj_dims=[64, 256]):
    """Profile a Gemma model at multiple projection dimensions."""
    print(f"\n{'=' * 60}")
    print(f"  {cfg['name']} ({cfg['id']})")
    print(f"  Gen {cfg['gen']}, {cfg['n_layers']}L, {cfg['n_heads']}h, d_head={cfg['d_head']}")
    print(f"{'=' * 60}")

    t0 = time.time()

    # Load model — use float16 for 9B+ to save memory
    from transformers import AutoModelForCausalLM
    use_fp16 = 'n_heads' in cfg and cfg['n_heads'] >= 16
    dtype = torch.float16 if use_fp16 else torch.float32
    print(f"  Loading ({dtype})...", end=" ", flush=True)

    try:
        model = AutoModelForCausalLM.from_pretrained(
            cfg['id'], dtype=dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
    except Exception as e:
        print(f"FAILED: {e}")
        return None

    state_dict = model.state_dict()
    del model
    gc.collect()
    torch.cuda.empty_cache()
    print(f"done ({time.time() - t0:.1f}s)")

    # Extract Q heads
    print(f"  Extracting Q-projections...", end=" ", flush=True)
    layers = extract_q_heads(state_dict, cfg)
    del state_dict
    gc.collect()
    if layers is None:
        return None
    print(f"done ({len(layers)} layers)")

    results = {}
    for proj_dim in proj_dims:
        print(f"\n  --- PROJ_DIM = {proj_dim} ---")
        layer_cvs = []
        layer_afs = []
        for L_idx, heads in enumerate(layers):
            af, cv = compute_layer_metrics(heads, cfg['d_head'], cfg['d_model'],
                                           proj_dim=proj_dim)
            layer_afs.append(af)
            layer_cvs.append(cv)
            if L_idx % 5 == 0 or L_idx == len(layers) - 1:
                print(f"    Layer {L_idx:2d}: AF={af:.3f}, CV={cv:.6f}")

        d = np.arange(len(layer_cvs))
        rho, p_rho = stats.spearmanr(d, layer_cvs)

        key = f"proj{proj_dim}"
        results[key] = {
            'proj_dim': proj_dim,
            'layer_cvs': layer_cvs,
            'layer_afs': layer_afs,
            'mean_cv': float(np.mean(layer_cvs)),
            'mean_af': float(np.mean(layer_afs)),
            'r_cv_depth': float(rho),
            'p_cv_depth': float(p_rho),
        }

        print(f"  RESULT (PROJ={proj_dim}): r = {rho:+.3f} (p={p_rho:.4f}), "
              f"AF = {np.mean(layer_afs):.3f}")

    elapsed = time.time() - t0
    print(f"\n  Total elapsed: {elapsed:.1f}s")

    return {
        'model': cfg['id'],
        'name': cfg['name'],
        'gen': cfg['gen'],
        'n_heads': cfg['n_heads'],
        'n_layers': cfg['n_layers'],
        'd_model': cfg['d_model'],
        'd_head': cfg['d_head'],
        **results,
    }


if __name__ == '__main__':
    # Allow filtering by name
    if len(sys.argv) > 1:
        names = [a.lower() for a in sys.argv[1:]]
        to_run = [m for m in GEMMA_MODELS
                  if any(n in m['name'].lower() or n in m['id'].lower() for n in names)]
    else:
        to_run = GEMMA_MODELS

    print(f"Gemma Sweep: {len(to_run)} models")
    for m in to_run:
        print(f"  {m['name']} ({m['id']}) — {m['n_layers']}L, {m['n_heads']}h")

    all_results = {}
    for cfg in to_run:
        try:
            r = profile_model(cfg, proj_dims=[64, 256])
            if r:
                all_results[cfg['name']] = r
                # Save incrementally
                outpath = os.path.join(BASE, 'p45_gemma_results.json')
                with open(outpath, 'w') as f:
                    json.dump(all_results, f, indent=2, default=str)
                print(f"  Saved ({len(all_results)} models)")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n{'=' * 80}")
    print(f"GEMMA SWEEP SUMMARY")
    print(f"{'=' * 80}")
    print(f"{'Model':15s} {'Gen':>3s} {'H':>3s} {'L':>3s}  "
          f"{'r(P=64)':>8s} {'p':>8s}  {'r(P=256)':>9s} {'p':>8s}")
    print("-" * 80)
    for name, r in sorted(all_results.items(), key=lambda x: (x[1]['gen'], x[1]['n_heads'])):
        r64 = r.get('proj64', {})
        r256 = r.get('proj256', {})
        print(f"{name:15s} {r['gen']:3d} {r['n_heads']:3d} {r['n_layers']:3d}  "
              f"{r64.get('r_cv_depth', float('nan')):+8.3f} {r64.get('p_cv_depth', float('nan')):8.4f}  "
              f"{r256.get('r_cv_depth', float('nan')):+9.3f} {r256.get('p_cv_depth', float('nan')):8.4f}")

    # Key question: does PROJ_DIM=256 flip the gradient direction?
    print(f"\nKEY QUESTION: Does matching PROJ_DIM to d_head change the gradient?")
    for name, r in all_results.items():
        r64 = r.get('proj64', {}).get('r_cv_depth', float('nan'))
        r256 = r.get('proj256', {}).get('r_cv_depth', float('nan'))
        if not (np.isnan(r64) or np.isnan(r256)):
            flip = "FLIP!" if (r64 > 0) != (r256 > 0) else "same"
            print(f"  {name:15s}: P64={r64:+.3f} -> P256={r256:+.3f}  [{flip}]")
