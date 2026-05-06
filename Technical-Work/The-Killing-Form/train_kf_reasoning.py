"""
KF-Gated Reasoning Training for Pythia-410M

Applies gradient-gated Killing Form regularization to the first 12 layers
(H-module) of Pythia-410M during fine-tuning on reasoning data.

Usage:
    python train_kf_reasoning.py \
        --kf_objective gated \
        --kf_lambda 1.0 \
        --data_path /home/clawd/reasoning/training_data/metamathqa \
        --save_dir /home/clawd/reasoning/checkpoints/pythia_kf_gated \
        --epochs 3 \
        --batch_size 8 \
        --lr 3e-5
"""

import argparse
import json
import os
import time
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_from_disk
import numpy as np


# ============================================================
# KF Computation (same as HRM experiments, adapted for Pythia)
# ============================================================

def compute_layer_cv(model, layer_idx):
    """Compute commutator variance for attention heads at a given layer.

    Uses Q^T @ K weight matrices (d_head x d_head per head).
    Returns scalar CV value for the layer.
    """
    layer = model.gpt_neox.layers[layer_idx].attention

    # Extract Q, K weight matrices and reshape to per-head
    # Pythia uses fused QKV projection: query_key_value weight is (3 * hidden, hidden)
    qkv_weight = layer.query_key_value.weight  # (3 * hidden_size, hidden_size)
    hidden_size = model.config.hidden_size
    num_heads = model.config.num_attention_heads
    head_dim = hidden_size // num_heads

    # Split into Q, K, V
    qkv = qkv_weight.view(num_heads, 3, head_dim, hidden_size)
    Q = qkv[:, 0, :, :]  # (num_heads, head_dim, hidden_size)
    K = qkv[:, 1, :, :]  # (num_heads, head_dim, hidden_size)

    # Compute W_h = Q_h^T @ K_h for each head -> (num_heads, hidden_size, hidden_size)
    # Actually we want (head_dim, head_dim) per head for tractability
    # Project to head subspace: Q[:, :, :head_dim] and K[:, :, :head_dim]
    # More correctly: W_h captures the head's interaction pattern
    # Use Q^T @ K in the head_dim space
    W = torch.bmm(Q.transpose(1, 2)[:, :head_dim, :head_dim],
                   K[:, :head_dim, :head_dim])  # (num_heads, head_dim, head_dim)

    n_h = W.shape[0]

    # Compute all pairwise commutators
    # [W_i, W_j] = W_i @ W_j - W_j @ W_i
    prod_ij = torch.einsum('iab,jbc->ijac', W, W)
    prod_ji = torch.einsum('jab,ibc->ijac', W, W)
    comm = prod_ij - prod_ji  # (n_h, n_h, head_dim, head_dim)

    # Normalized commutator norms
    norms = torch.norm(comm, dim=(-2, -1))  # (n_h, n_h)
    w_norms = torch.norm(W.flatten(1), dim=1)  # (n_h,)
    normalized = norms / (w_norms[:, None] * w_norms[None, :] + 1e-10)

    # CV = variance of upper-triangle normalized norms
    idx = torch.triu_indices(n_h, n_h, offset=1)
    cv = torch.var(normalized[idx[0], idx[1]])

    return cv


def compute_h_module_cv(model, h_layers):
    """Compute mean CV across all H-module layers."""
    cvs = []
    per_layer = {}
    for l in h_layers:
        cv = compute_layer_cv(model, l)
        cvs.append(cv)
        per_layer[l] = cv.item()
    mean_cv = torch.stack(cvs).mean()
    return mean_cv, per_layer


# ============================================================
# Gradient Gating
# ============================================================

def compute_gated_kf_loss(model, h_layers, ce_loss, kf_lambda, objective='gated'):
    """Compute KF loss with per-layer gradient gating.

    For each H-module layer:
    - Compute cos(grad_CE, grad_KF)
    - If cos > 0: apply KF (structure helps task)
    - If cos <= 0: zero KF gradient (structure hurts task)

    Returns total KF loss (only from aligned layers).
    """
    if objective == 'none':
        return torch.tensor(0.0, device=next(model.parameters()).device)

    # Compute per-layer CV
    layer_cvs = {}
    for l in h_layers:
        layer_cvs[l] = compute_layer_cv(model, l)

    if objective == 'fixed':
        # Simple: maximize total CV
        total_cv = torch.stack(list(layer_cvs.values())).mean()
        return -kf_lambda * total_cv, {l: True for l in h_layers}, {}

    if objective == 'log':
        total_cv = torch.stack(list(layer_cvs.values())).mean()
        return -kf_lambda * torch.log(1 + total_cv), {l: True for l in h_layers}, {}

    if objective in ('gated', 'bidirectional'):
        # Need per-layer gradient alignment
        # Strategy: compute CE gradient and KF gradient for each layer's QKV weight,
        # check cosine similarity

        applied = {}
        cos_sims = {}
        kf_loss = torch.tensor(0.0, device=next(model.parameters()).device)

        for l in h_layers:
            qkv_param = model.gpt_neox.layers[l].attention.query_key_value.weight

            # CE gradient for this layer
            if qkv_param.grad is not None:
                grad_ce = qkv_param.grad.clone().flatten()
            else:
                # CE backward hasn't been called yet — skip gating, apply all
                applied[l] = True
                kf_loss = kf_loss - kf_lambda * layer_cvs[l]
                cos_sims[l] = 0.0
                continue

            # KF gradient for this layer (compute independently)
            kf_layer_loss = -kf_lambda * layer_cvs[l]
            kf_grads = torch.autograd.grad(kf_layer_loss, qkv_param, retain_graph=True)[0]
            grad_kf = kf_grads.flatten()

            # Cosine similarity
            cos_sim = F.cosine_similarity(grad_ce.unsqueeze(0), grad_kf.unsqueeze(0)).item()
            cos_sims[l] = cos_sim

            if cos_sim > 0:
                # Aligned: apply KF (build structure)
                applied[l] = True
                kf_loss = kf_loss - kf_lambda * layer_cvs[l]
            elif objective == 'bidirectional' and cos_sim < -0.01:
                # Opposed: reverse KF (remove structure)
                applied[l] = False
                kf_loss = kf_loss + kf_lambda * 0.1 * layer_cvs[l]  # gentler decrystallization
            else:
                # Opposed or dead zone: don't apply
                applied[l] = False

        return kf_loss, applied, cos_sims

    raise ValueError(f'Unknown objective: {objective}')


# ============================================================
# Dataset
# ============================================================

class ReasoningDataset(Dataset):
    """Dataset for math reasoning traces (MetaMathQA format)."""

    def __init__(self, data_path, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Load from HuggingFace datasets format
        from datasets import load_from_disk
        ds = load_from_disk(data_path)
        self.data = ds['train'] if 'train' in ds else ds
        print(f'Loaded {len(self.data)} reasoning examples')

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Format as "Question: {query}\nAnswer: {response}"
        query = item.get('query', item.get('question', ''))
        response = item.get('response', item.get('answer', ''))

        text = f"Question: {query}\nAnswer: {response}"

        # Tokenize
        encoded = self.tokenizer(
            text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )

        input_ids = encoded['input_ids'].squeeze(0)
        attention_mask = encoded['attention_mask'].squeeze(0)

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': input_ids.clone()  # Causal LM: predict next token
        }


# ============================================================
# Training Loop
# ============================================================

def train(args):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}')

    # Load model and tokenizer
    print(f'\nLoading {args.model_name}...')
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(args.model_name).to(device)
    total_params = sum(p.numel() for p in model.parameters())
    print(f'  Total parameters: {total_params:,}')

    # Define H-module and L-module layers
    n_layers = model.config.num_hidden_layers
    h_layers = list(range(n_layers // 2))  # First half
    l_layers = list(range(n_layers // 2, n_layers))  # Second half
    print(f'  H-module: layers {h_layers[0]}-{h_layers[-1]} ({len(h_layers)} layers)')
    print(f'  L-module: layers {l_layers[0]}-{l_layers[-1]} ({len(l_layers)} layers)')

    # Dataset
    print(f'\nLoading dataset from {args.data_path}...')
    dataset = ReasoningDataset(args.data_path, tokenizer, max_length=args.max_length)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True,
                           num_workers=2, pin_memory=True)

    # Optimizer
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)

    # Baseline KF measurement
    print('\n--- BASELINE KF (before training) ---')
    with torch.no_grad():
        h_cv, h_per_layer = compute_h_module_cv(model, h_layers)
        l_cv, l_per_layer = compute_h_module_cv(model, l_layers)
    print(f'  H_CV: {h_cv:.6e}  L_CV: {l_cv:.6e}  ratio: {h_cv/l_cv:.4f}')
    print(f'  H per-layer: {", ".join(f"L{l}:{v:.4e}" for l,v in h_per_layer.items())}')
    print(f'  L per-layer: {", ".join(f"L{l}:{v:.4e}" for l,v in l_per_layer.items())}')

    # Save baseline
    trajectory = [{
        'step': 0, 'epoch': 0, 'h_cv': h_cv.item(), 'l_cv': l_cv.item(),
        'h_per_layer': h_per_layer, 'l_per_layer': l_per_layer
    }]

    # Training
    os.makedirs(args.save_dir, exist_ok=True)
    global_step = 0
    steps_per_epoch = len(dataloader)
    total_steps = steps_per_epoch * args.epochs

    print(f'\n{"="*60}')
    print(f'  KF Objective: {args.kf_objective}')
    print(f'  KF Lambda: {args.kf_lambda}')
    print(f'  KF Every: {args.kf_every} steps')
    print(f'  Steps/epoch: {steps_per_epoch}  Total steps: {total_steps}')
    print(f'  Save dir: {args.save_dir}')
    print(f'{"="*60}\n')

    start_time = time.time()

    for epoch in range(args.epochs):
        model.train()
        epoch_ce_loss = 0
        epoch_kf_loss = 0

        for batch_idx, batch in enumerate(dataloader):
            global_step += 1

            # Move to device
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            # Forward pass (CE loss)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            ce_loss = outputs.loss

            # Backward CE first (so gradients are available for gating)
            optimizer.zero_grad()
            ce_loss.backward(retain_graph=(global_step % args.kf_every == 0))

            # KF regularization (every kf_every steps)
            kf_loss_val = 0.0
            if global_step % args.kf_every == 0 and args.kf_objective != 'none':
                kf_loss, applied, cos_sims = compute_gated_kf_loss(
                    model, h_layers, ce_loss, args.kf_lambda, args.kf_objective
                )

                if kf_loss.requires_grad:
                    kf_loss.backward()

                kf_loss_val = kf_loss.item()

                # Zero L-module KF gradients (safety — KF shouldn't touch them anyway)
                for l in l_layers:
                    for param in model.gpt_neox.layers[l].parameters():
                        if param.grad is not None:
                            # Only zero the KF component — CE grad is already accumulated
                            pass  # KF grad only touches H-module QKV weights

                # Log gating
                n_applied = sum(1 for v in applied.values() if v)
                gated_layers = [l for l, v in applied.items() if not v]
                avg_cos = np.mean(list(cos_sims.values())) if cos_sims else 0.0

                # Compute current CV
                with torch.no_grad():
                    h_cv, h_per_layer = compute_h_module_cv(model, h_layers)

                diag_num = global_step // args.kf_every
                print(f'  [Step {global_step}] KF-{args.kf_objective} #{diag_num}: '
                      f'H_CV={h_cv.item():.6e}  applied={n_applied}/{len(h_layers)}  '
                      f'gated={gated_layers}  avg_cos={avg_cos:.4f}')

                trajectory.append({
                    'step': global_step, 'epoch': epoch,
                    'h_cv': h_cv.item(), 'h_per_layer': h_per_layer,
                    'applied': {str(k): v for k, v in applied.items()},
                    'cos_sims': {str(k): v for k, v in cos_sims.items()},
                    'ce_loss': ce_loss.item(), 'kf_loss': kf_loss_val
                })

            # Optimizer step
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            epoch_ce_loss += ce_loss.item()
            epoch_kf_loss += kf_loss_val

            # Progress logging
            if global_step % 100 == 0:
                elapsed = time.time() - start_time
                steps_per_sec = global_step / elapsed
                print(f'  step {global_step}  ce_loss={ce_loss.item():.4f}  '
                      f'steps/s={steps_per_sec:.2f}  elapsed={elapsed:.0f}s')

        # End of epoch
        avg_ce = epoch_ce_loss / steps_per_epoch
        print(f'\n--- Epoch {epoch+1}/{args.epochs} complete ---')
        print(f'  Avg CE loss: {avg_ce:.4f}')

        # Full KF measurement
        with torch.no_grad():
            h_cv, h_per_layer = compute_h_module_cv(model, h_layers)
            l_cv, l_per_layer = compute_h_module_cv(model, l_layers)
        print(f'  H_CV: {h_cv:.6e}  L_CV: {l_cv:.6e}  ratio: {h_cv/l_cv:.4f}')

        trajectory.append({
            'step': global_step, 'epoch': epoch + 1,
            'h_cv': h_cv.item(), 'l_cv': l_cv.item(),
            'h_per_layer': h_per_layer, 'l_per_layer': l_per_layer,
            'avg_ce_loss': avg_ce, 'checkpoint': True
        })

        # Save checkpoint
        ckpt_dir = os.path.join(args.save_dir, f'epoch_{epoch+1}')
        model.save_pretrained(ckpt_dir)
        tokenizer.save_pretrained(ckpt_dir)
        print(f'  Checkpoint saved: {ckpt_dir}')

        # Save trajectory
        traj_path = os.path.join(args.save_dir, 'kf_trajectory.json')
        with open(traj_path, 'w') as f:
            json.dump(trajectory, f, indent=2)

    print(f'\n{"="*60}')
    print(f'Training complete. {global_step} steps, {args.epochs} epochs.')
    print(f'Trajectory: {traj_path}')
    print(f'{"="*60}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', default='EleutherAI/pythia-410m')
    parser.add_argument('--data_path', default='/home/clawd/reasoning/training_data/metamathqa')
    parser.add_argument('--save_dir', default='/home/clawd/reasoning/checkpoints/pythia_kf_gated')
    parser.add_argument('--kf_objective', default='gated',
                       choices=['none', 'fixed', 'log', 'gated', 'bidirectional'])
    parser.add_argument('--kf_lambda', type=float, default=1.0)
    parser.add_argument('--kf_every', type=int, default=50)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--lr', type=float, default=3e-5)
    parser.add_argument('--max_length', type=int, default=512)
    args = parser.parse_args()

    train(args)
