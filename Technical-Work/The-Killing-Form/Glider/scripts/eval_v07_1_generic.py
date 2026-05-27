"""Topology eval for any v0.7.1 trained checkpoint vs pristine model — generalized.

Generalizes eval_v07_1_1b.py to accept --model_id + --ckpt + --output parameters
for cross-architecture replication (Qwen, Llama, etc.) without copy-paste.

Pristine model topology serves as the baseline reference per Phase 1 finding
(baseline-trained 270m topology = pristine topology).

Architecture assumptions: standard `model.model.layers[L].self_attn.{q_proj, v_proj}`
access path — works for Gemma, Llama (TinyLlama, SmolLM), Qwen2, Qwen3, Mistral.
For GPT-NeoX (Pythia) with fused QKV: not supported by this script (separate path).
"""
import argparse
import json
from pathlib import Path
import numpy as np
import torch

SEED = 71
PROJ_DIM = 64


def get_pristine_state(model_id):
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=torch.float32)
    return {k: v.cpu().numpy() for k, v in model.state_dict().items()}


def per_layer(msd, n_layers, n_heads, d_head, d_model):
    res = []
    for L in range(n_layers):
        qk = f'model.layers.{L}.self_attn.q_proj.weight'
        vk = f'model.layers.{L}.self_attn.v_proj.weight'
        if qk not in msd: continue
        q_w = msd[qk]
        if hasattr(q_w, 'cpu'): q_w = q_w.float().cpu().numpy()
        v_w = msd[vk]
        if hasattr(v_w, 'cpu'): v_w = v_w.float().cpu().numpy()
        n_kv = v_w.shape[0] // d_head
        q_heads = q_w.reshape(n_heads, d_head, d_model)
        v_heads = v_w.reshape(n_kv, d_head, d_model)
        heads_per_kv = n_heads // n_kv
        q_norms = [float(np.linalg.norm(q_heads[h],'fro')) for h in range(n_heads)]
        v_norms = [float(np.linalg.norm(v_heads[k],'fro')) for k in range(n_kv)]
        vq = [v_norms[h//heads_per_kv]/q_norms[h] if q_norms[h]>0 else 0 for h in range(n_heads)]
        arr = np.array(vq); mean, std = float(arr.mean()), float(arr.std())
        cls = ['anchor' if r<mean-0.5*std else 'worker' if r>mean+0.5*std else 'neutral' for r in vq]
        np.random.seed(SEED)
        p_out = np.random.randn(PROJ_DIM, d_head)/np.sqrt(d_head)
        p_in = np.random.randn(d_model, PROJ_DIM)/np.sqrt(d_model)
        proj = [p_out @ q_heads[h] @ p_in for h in range(n_heads)]
        norms = np.zeros((n_heads, n_heads))
        for h in range(n_heads):
            for hp in range(h+1, n_heads):
                c = proj[h] @ proj[hp] - proj[hp] @ proj[h]
                norms[h, hp] = np.linalg.norm(c, 'fro'); norms[hp, h] = norms[h, hp]
        typ = np.mean([np.linalg.norm(A,'fro') for A in proj])
        if typ > 0: norms /= typ**2
        mask = np.ones_like(norms, dtype=bool); np.fill_diagonal(mask, False)
        cv = float(np.var(norms[mask]))
        anchor_vqs = [vq[h] for h in range(n_heads) if cls[h]=='anchor']
        worker_vqs = [vq[h] for h in range(n_heads) if cls[h]=='worker']
        res.append({
            'layer': L, 'mean_vq': mean, 'std_vq': std,
            'mean_anchor_vq': float(np.mean(anchor_vqs)) if anchor_vqs else 0,
            'mean_worker_vq': float(np.mean(worker_vqs)) if worker_vqs else 0,
            'n_anchor': cls.count('anchor'), 'n_worker': cls.count('worker'),
            'n_neutral': cls.count('neutral'), 'cv': cv,
        })
    return res


def agg(r):
    seps = [l['mean_worker_vq'] - l['mean_anchor_vq'] for l in r]
    return {
        'mean_separation': float(np.mean(seps)),
        'max_separation': float(np.max(seps)),
        'mean_cv': float(np.mean([l['cv'] for l in r])),
        'max_cv': float(np.max([l['cv'] for l in r])),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model_id', required=True, help='HF model ID for pristine baseline reference')
    ap.add_argument('--ckpt', required=True, help='Path to v0.7.1 trained checkpoint .pt file')
    ap.add_argument('--output', required=True, help='Output JSON path for results')
    args = ap.parse_args()

    from transformers import AutoConfig
    cfg = AutoConfig.from_pretrained(args.model_id)
    n_heads = cfg.num_attention_heads
    n_layers = cfg.num_hidden_layers
    d_head = getattr(cfg, "head_dim", cfg.hidden_size // n_heads)
    d_model = cfg.hidden_size

    print(f"Loading pristine {args.model_id}...")
    pristine = get_pristine_state(args.model_id)
    print(f"Loading trained checkpoint {args.ckpt}...")
    ckpt = torch.load(args.ckpt, map_location='cpu', weights_only=False)
    trained = ckpt['model_state_dict']

    print(f"Analyzing topology (n_layers={n_layers}, n_heads={n_heads}, d_head={d_head})...")
    pristine_results = per_layer(pristine, n_layers, n_heads, d_head, d_model)
    trained_results = per_layer(trained, n_layers, n_heads, d_head, d_model)

    print(f"\n{'layer':<6} {'PRISTINE':<28} {'TRAINED':<32} {'sep_delta':<10}")
    for L in range(len(pristine_results)):
        p = pristine_results[L]; t = trained_results[L]
        p_sep = p['mean_worker_vq'] - p['mean_anchor_vq']
        t_sep = t['mean_worker_vq'] - t['mean_anchor_vq']
        print(f"L{L:<5} a={p['n_anchor']} w={p['n_worker']} sep={p_sep:.4f} cv={p['cv']:.5f}  "
              f"a={t['n_anchor']} w={t['n_worker']} sep={t_sep:.4f} cv={t['cv']:.5f}  "
              f"{t_sep-p_sep:+.4f}")

    ap_agg = agg(pristine_results); at_agg = agg(trained_results)
    print(f"\n=== AGGREGATE ({args.model_id}) ===")
    print(f"{'metric':<25} {'pristine':<15} {'trained':<15} {'delta':<15} {'ratio':<10}")
    for m in ap_agg:
        ratio = at_agg[m] / ap_agg[m] if ap_agg[m] != 0 else float('inf')
        print(f"{m:<25} {ap_agg[m]:<15.6f} {at_agg[m]:<15.6f} {at_agg[m]-ap_agg[m]:+.6f} {ratio:.2f}x")

    print(f"\nReference Gemma 1B v0.7.1 result: mean_sep ratio 5.40x; mean_cv ratio 9.21x")

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump({
            'model_id': args.model_id,
            'ckpt': args.ckpt,
            'pristine': pristine_results,
            'trained': trained_results,
            'agg_pristine': ap_agg,
            'agg_trained': at_agg
        }, f, indent=2)
    print(f"\nSaved: {out_path}")


if __name__ == "__main__":
    main()
