"""Baseline vs v0.7.1 evaluation — measures class-separation produced by anti-uniformity aux loss."""
import json
from pathlib import Path
import numpy as np
import torch

SEED = 71; PROJ_DIM = 64

CKPT = {
    'baseline': '/home/clawd/path_c_results/gemma270m_baseline/step_1600_final.pt',
    'v07_1':    '/home/clawd/path_c_results/gemma270m_v07_1/step_1600_final.pt',
}


def per_layer(msd, n_layers=18, n_heads=4, d_head=256, d_model=640):
    res = []
    for L in range(n_layers):
        qk = f'model.layers.{L}.self_attn.q_proj.weight'
        vk = f'model.layers.{L}.self_attn.v_proj.weight'
        if qk not in msd: continue
        q_w = msd[qk].float().cpu().numpy()
        v_w = msd[vk].float().cpu().numpy()
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


out = {}
for name, p in CKPT.items():
    ckpt = torch.load(p, map_location='cpu', weights_only=False)
    out[name] = per_layer(ckpt['model_state_dict'])

print(f"{'layer':<6} {'BASELINE':<28} {'v07_1':<32} {'sep_delta':<10}")
print(f"{'':<6} {'anchor/worker/sep/cv':<28} {'anchor/worker/sep/cv':<32}")
for L in range(len(out['baseline'])):
    b = out['baseline'][L]; k = out['v07_1'][L]
    b_sep = b['mean_worker_vq'] - b['mean_anchor_vq']
    k_sep = k['mean_worker_vq'] - k['mean_anchor_vq']
    print(f"L{L:<5} a={b['n_anchor']} w={b['n_worker']} sep={b_sep:.4f} cv={b['cv']:.5f}  "
          f"a={k['n_anchor']} w={k['n_worker']} sep={k_sep:.4f} cv={k['cv']:.5f}  "
          f"{k_sep-b_sep:+.4f}")

def agg(r):
    seps = [l['mean_worker_vq'] - l['mean_anchor_vq'] for l in r]
    return {
        'mean_separation': float(np.mean(seps)),
        'max_separation': float(np.max(seps)),
        'mean_cv': float(np.mean([l['cv'] for l in r])),
        'max_cv': float(np.max([l['cv'] for l in r])),
        'total_anchor': sum(l['n_anchor'] for l in r),
        'total_worker': sum(l['n_worker'] for l in r),
    }


ab = agg(out['baseline']); ak = agg(out['v07_1'])
print()
print('=== AGGREGATE ===')
print(f"{'metric':<25} {'baseline':<15} {'v07_1':<15} {'delta':<15}")
for m in ab:
    if isinstance(ab[m], float):
        print(f"{m:<25} {ab[m]:<15.6f} {ak[m]:<15.6f} {ak[m]-ab[m]:+.6f}")
    else:
        print(f"{m:<25} {ab[m]:<15} {ak[m]:<15} {ak[m]-ab[m]:+d}")

out_path = '/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results/gemma_v07_1_eval.json'
with open(out_path, 'w') as f:
    json.dump({'baseline': out['baseline'], 'v07_1': out['v07_1'],
               'agg_baseline': ab, 'agg_v07_1': ak}, f, indent=2)
print(f"\nsaved: {out_path}")
