"""Topology eval for 1b v0.7.1 trained checkpoint vs pristine 1b model.

Pristine model topology serves as the baseline reference for 1b
(per Phase 1 finding: baseline-trained 270m topology = pristine topology).
"""
import json
import sys
from pathlib import Path
import numpy as np
import torch

SEED = 71; PROJ_DIM = 64
MODEL_ID = "google/gemma-3-1b-pt"
CKPT = '/home/clawd/path_c_results/gemma3_1b_v07_1/step_400_final.pt'


def get_pristine_state():
    from transformers import AutoModelForCausalLM
    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, dtype=torch.float32)
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


from transformers import AutoConfig
cfg = AutoConfig.from_pretrained(MODEL_ID)
n_heads = cfg.num_attention_heads
n_layers = cfg.num_hidden_layers
d_head = getattr(cfg, "head_dim", cfg.hidden_size // n_heads)
d_model = cfg.hidden_size

print(f"Loading pristine 1b...")
pristine = get_pristine_state()
print(f"Loading v0.7.1 trained 1b...")
ckpt = torch.load(CKPT, map_location='cpu', weights_only=False)
trained = ckpt['model_state_dict']

print(f"Analyzing topology (n_layers={n_layers}, n_heads={n_heads}, d_head={d_head})...")
pristine_results = per_layer(pristine, n_layers, n_heads, d_head, d_model)
trained_results = per_layer(trained, n_layers, n_heads, d_head, d_model)

print(f"\n{'layer':<6} {'PRISTINE':<28} {'v07_1':<32} {'sep_delta':<10}")
for L in range(len(pristine_results)):
    p = pristine_results[L]; t = trained_results[L]
    p_sep = p['mean_worker_vq'] - p['mean_anchor_vq']
    t_sep = t['mean_worker_vq'] - t['mean_anchor_vq']
    print(f"L{L:<5} a={p['n_anchor']} w={p['n_worker']} sep={p_sep:.4f} cv={p['cv']:.5f}  "
          f"a={t['n_anchor']} w={t['n_worker']} sep={t_sep:.4f} cv={t['cv']:.5f}  "
          f"{t_sep-p_sep:+.4f}")


def agg(r):
    seps = [l['mean_worker_vq'] - l['mean_anchor_vq'] for l in r]
    return {
        'mean_separation': float(np.mean(seps)),
        'max_separation': float(np.max(seps)),
        'mean_cv': float(np.mean([l['cv'] for l in r])),
        'max_cv': float(np.max([l['cv'] for l in r])),
    }


ap = agg(pristine_results); at = agg(trained_results)
print(f"\n=== AGGREGATE 1b ===")
print(f"{'metric':<25} {'pristine':<15} {'v07_1':<15} {'delta':<15} {'ratio':<10}")
for m in ap:
    ratio = at[m] / ap[m] if ap[m] != 0 else float('inf')
    print(f"{m:<25} {ap[m]:<15.6f} {at[m]:<15.6f} {at[m]-ap[m]:+.6f} {ratio:.2f}x")

print(f"\nReference 270m result: sep 0.351 vs baseline 0.136 (2.93x); CV ratio 6.13x")

out_path = '/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results/gemma3_1b_v07_1_eval.json'
with open(out_path, 'w') as f:
    json.dump({'pristine': pristine_results, 'trained': trained_results, 'agg_pristine': ap, 'agg_trained': at}, f, indent=2)
print(f"\nSaved: {out_path}")
