"""Quick test: verify Killing form computation works on Qwen2.5-1.5B layer 0."""
import numpy as np
from transformers import AutoModelForCausalLM, AutoConfig
import torch, time

model_name = 'Qwen/Qwen2.5-1.5B'
config = AutoConfig.from_pretrained(model_name)
n_heads = config.num_attention_heads
d_model = config.hidden_size
d_head = d_model // n_heads
print(f'n_heads={n_heads}, d_model={d_model}, d_head={d_head}')

model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32)

key = 'model.layers.0.self_attn.q_proj.weight'
W_Q = None
for name, param in model.named_parameters():
    if name == key:
        W_Q = param.detach().cpu().numpy()
        print(f'W_Q shape: {W_Q.shape}')
        break

heads = []
for h in range(n_heads):
    W_Q_h = W_Q[h*d_head:(h+1)*d_head, :]
    heads.append(W_Q_h)

PROJ_DIM = 64
np.random.seed(71)
p_out = np.random.randn(PROJ_DIM, d_head) / np.sqrt(d_head)
p_in = np.random.randn(d_model, PROJ_DIM) / np.sqrt(d_model)

proj_heads = [p_out @ A @ p_in for A in heads]
print(f'Projected head shape: {proj_heads[0].shape}')

comm = proj_heads[0] @ proj_heads[1] - proj_heads[1] @ proj_heads[0]
print(f'Commutator norm: {np.linalg.norm(comm):.6f}')

t0 = time.time()
n_h = len(proj_heads)
killing = np.zeros((n_h, n_h))
for h in range(n_h):
    for hp in range(n_h):
        val = 0
        for k in range(n_h):
            c1 = proj_heads[h] @ proj_heads[k] - proj_heads[k] @ proj_heads[h]
            c2 = proj_heads[hp] @ proj_heads[k] - proj_heads[k] @ proj_heads[hp]
            val += np.trace(c1.T @ c2)
        killing[h, hp] = val

max_k = np.max(np.abs(killing))
killing_norm = killing / max_k if max_k > 0 else killing
evs = np.sort(np.abs(np.linalg.eigvalsh(killing_norm)))
n_null = int(np.sum(evs < 0.10))
print(f'Layer 0: AF={n_null/n_h:.3f}, ev_range=[{evs[0]:.4f}, {evs[-1]:.4f}], time={time.time()-t0:.2f}s')
print('Eigenvalues:', ' '.join([f'{e:.4f}' for e in evs]))
print('Test PASSED.')
