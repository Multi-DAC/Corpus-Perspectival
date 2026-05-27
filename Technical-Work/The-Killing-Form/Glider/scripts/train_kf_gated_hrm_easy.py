"""
Path A — HRM easy-sudoku gated-vs-baseline accuracy replication (STEP-BASED)
============================================================================
Reproduces the P49 reasoning-accuracy benefit (KF gating accelerates learning
on LEARNABLE sudoku) on the 27M HRM, multi-seed, as the anchor/control for Path B.

Built 2026-05-27 Day 117 from train_and_measure.py (baseline: CE + accuracy/KF eval)
+ the v0.6a bidirectional gradient-gating from train_kf_300m.py (patch_bidir.py).

STEP-BASED: the easy-aug dataset is ~2600 steps/epoch, so epoch-granularity eval is
too coarse to see the acceleration curve. We train to --max_steps, eval every
--eval_steps, log throughput every --log_every. This gives the fine-grained
accuracy-vs-step curve the P49 signature lives in.

Key facts:
  - P49 benefit (+17.6%) was on EASY/learnable sudoku, 27M HRM (hrm_v1.yaml).
  - Gating is H-module only (the "speaker"); L-module evaluates.
  - HRM gating recomputes per-layer CV freshly from qkv_proj.weight — no graph
    sharing with the CE step, so CE and KF are clean separate optimizer steps.
  - threshold=0.0 breathed (Finding #82); default kept at 0.0.

Usage:
  python3 train_kf_gated_hrm_easy.py --save_dir DIR --seed 0 \
      --max_steps 3000 --eval_steps 300 --gating none
  ... --gating bidirectional --kf_lambda 1.0 --kf_every 50 --kf_threshold 0.0
"""
import sys
import os
import json
import time
import argparse
import torch
import numpy as np

sys.path.insert(0, '/home/clawd/HRM')
sys.stdout.reconfigure(line_buffering=True)

from omegaconf import OmegaConf
from torch.utils.data import DataLoader
from puzzle_dataset import PuzzleDataset, PuzzleDatasetConfig, PuzzleDatasetMetadata
from utils.functions import load_model_class
from adam_atan2_fallback import AdamATan2


# ============================================================
# MODEL + DATA
# ============================================================

def build_model(arch_cfg, num_puzzle_ids, device, vocab_size=11, seq_len=81, batch_size=384):
    arch_resolved = OmegaConf.to_container(arch_cfg, resolve=True)
    hidden_size = arch_resolved.get('hidden_size', 512)
    if isinstance(arch_resolved.get('puzzle_emb_ndim'), str):
        arch_resolved['puzzle_emb_ndim'] = hidden_size
    model_cfg = {
        **arch_resolved,
        'vocab_size': vocab_size, 'max_seq_len': seq_len, 'batch_size': batch_size,
        'seq_len': seq_len, 'num_puzzle_identifiers': num_puzzle_ids, 'causal': False,
    }
    loss_cfg = model_cfg.pop('loss', {})
    loss_type = loss_cfg.get('loss_type', 'stablemax_cross_entropy')
    model_name = model_cfg.pop('name', '')
    model_cls = load_model_class(model_name)
    loss_head_cls = load_model_class(loss_cfg.get('name', 'losses@ACTLossHead'))
    with torch.device(device):
        raw_model = model_cls(model_cfg)
        loss_extra = {k: v for k, v in loss_cfg.items() if k not in ('name', 'loss_type')}
        model = loss_head_cls(raw_model, loss_type=loss_type, **loss_extra)
    return model, raw_model


def create_dataloader(data_path, split, batch_size, epochs_per_iter=1, seed=42):
    ds_cfg = PuzzleDatasetConfig(
        seed=seed, dataset_path=data_path, test_set_mode=(split == "test"),
        epochs_per_iter=epochs_per_iter, global_batch_size=batch_size,
        rank=0, num_replicas=1,
    )
    dataset = PuzzleDataset(ds_cfg, split=split)
    metadata = dataset.metadata
    loader = DataLoader(dataset, batch_size=None, num_workers=0, pin_memory=True)
    return loader, metadata


# ============================================================
# KF MEASUREMENT (static)
# ============================================================

def extract_attention_weights(model):
    heads = {'H': [], 'L': []}
    for module_name, module in [('H', model.inner.H_level), ('L', model.inner.L_level)]:
        for layer_idx, layer in enumerate(module.layers):
            W = layer.self_attn.qkv_proj.weight.detach().float().cpu()
            num_heads = layer.self_attn.num_heads
            head_dim = layer.self_attn.head_dim
            W_Q = W[:num_heads * head_dim, :]
            W_K = W[num_heads * head_dim: 2 * num_heads * head_dim, :]
            for h in range(num_heads):
                q_h = W_Q[h * head_dim:(h + 1) * head_dim, :]
                k_h = W_K[h * head_dim:(h + 1) * head_dim, :]
                heads[module_name].append({'layer': layer_idx, 'head': h, 'W': q_h.T @ k_h})
    return heads


def _cv(heads_list):
    n = len(heads_list)
    if n < 2:
        return 0.0
    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = heads_list[i]['W'] @ heads_list[j]['W'] - heads_list[j]['W'] @ heads_list[i]['W']
            norms.append(torch.norm(comm, p='fro').item())
    return float(np.var(norms))


def measure_kf(model, step_label):
    heads = extract_attention_weights(model)
    h_cv = _cv(heads['H'])
    l_cv = _cv(heads['L'])
    return {'step': step_label, 'H_cv': h_cv, 'L_cv': l_cv, 'h_l_ratio': h_cv / (l_cv + 1e-20)}


# ============================================================
# DIFFERENTIABLE H-MODULE PER-LAYER CV + GATING
# ============================================================

def compute_h_module_cv_per_layer(raw_model):
    """Return list of (layer_idx, layer_cv_tensor, qkv_param_ref) — differentiable."""
    h_module = raw_model.inner.H_level
    layer_data = []
    for layer_idx, layer in enumerate(h_module.layers):
        W = layer.self_attn.qkv_proj.weight
        num_heads = layer.self_attn.num_heads
        head_dim = layer.self_attn.head_dim
        W_Q = W[:num_heads * head_dim, :]
        W_K = W[num_heads * head_dim: 2 * num_heads * head_dim, :]
        head_matrices = []
        for h in range(num_heads):
            q_h = W_Q[h * head_dim:(h + 1) * head_dim, :]
            k_h = W_K[h * head_dim:(h + 1) * head_dim, :]
            head_matrices.append(q_h.T @ k_h)
        norms = []
        for i in range(len(head_matrices)):
            for j in range(i + 1, len(head_matrices)):
                comm = head_matrices[i] @ head_matrices[j] - head_matrices[j] @ head_matrices[i]
                norms.append(torch.sqrt(torch.sum(comm ** 2) + 1e-12))
        if norms:
            layer_cv = torch.var(torch.stack(norms))
            layer_data.append((layer_idx, layer_cv, layer.self_attn.qkv_proj.weight))
    return layer_data


def apply_bidirectional_gating(raw_model, optimizer, current_lambda, threshold, stats):
    """v0.6a three-mode gated KF step on the H-module. CE backward+step just ran."""
    ce_grads = {}
    for layer_idx, layer in enumerate(raw_model.inner.H_level.layers):
        p = layer.self_attn.qkv_proj.weight
        if p.grad is not None:
            ce_grads[layer_idx] = p.grad.detach().clone()

    layer_data = compute_h_module_cv_per_layer(raw_model)
    h_cv_val = torch.stack([ld[1] for ld in layer_data]).mean().item()
    optimizer.zero_grad()

    build, neutral, dissolve = [], [], []
    for layer_idx, layer_cv, param_ref in layer_data:
        (-current_lambda * layer_cv).backward(retain_graph=True)
        if layer_idx in ce_grads and param_ref.grad is not None:
            kf_grad = param_ref.grad.detach().flatten()
            ce_grad = ce_grads[layer_idx].flatten()
            cos_val = (torch.dot(kf_grad, ce_grad) /
                       (torch.norm(kf_grad) * torch.norm(ce_grad) + 1e-20)).item()
            if cos_val > threshold:
                build.append((layer_idx, cos_val))
            elif cos_val < -threshold:
                param_ref.grad.mul_(-1.0)
                dissolve.append((layer_idx, cos_val))
            else:
                param_ref.grad.zero_()
                neutral.append(layer_idx)
    for p in raw_model.inner.L_level.parameters():
        if p.grad is not None:
            p.grad.zero_()
    optimizer.step()

    stats['applications'] += 1
    stats['build'] += len(build)
    stats['dissolve'] += len(dissolve)
    stats['neutral'] += len(neutral)
    return h_cv_val, len(build), len(neutral), len(dissolve)


# ============================================================
# TRAINING (step-based)
# ============================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_path", type=str, default='/home/clawd/HRM/data/sudoku-easy-1k-aug-1000')
    ap.add_argument("--save_dir", type=str, required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max_steps", type=int, default=3000)
    ap.add_argument("--eval_steps", type=int, default=300)
    ap.add_argument("--eval_batches", type=int, default=15,
                    help="cap eval at N batches (test set is 1M examples; full eval ~19min)")
    ap.add_argument("--log_every", type=int, default=50)
    ap.add_argument("--batch_size", type=int, default=384)
    ap.add_argument("--lr", type=float, default=7e-5)
    ap.add_argument("--gating", type=str, default="none", choices=["none", "bidirectional"])
    ap.add_argument("--kf_lambda", type=float, default=1.0)
    ap.add_argument("--kf_every", type=int, default=50)
    ap.add_argument("--kf_threshold", type=float, default=0.0)
    args = ap.parse_args()

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    os.makedirs(args.save_dir, exist_ok=True)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)

    print(f"{'='*64}")
    print(f"  Path A — gating={args.gating}  seed={args.seed}  data={os.path.basename(args.data_path)}")
    print(f"  max_steps={args.max_steps} eval_steps={args.eval_steps} bs={args.batch_size} lr={args.lr}")
    if args.gating != "none":
        print(f"  KF: lambda={args.kf_lambda} every={args.kf_every} threshold={args.kf_threshold} (H-module)")
    print(f"{'='*64}", flush=True)

    arch_cfg = OmegaConf.load('/home/clawd/HRM/config/arch/hrm_v1.yaml')
    print(f"Arch: H={arch_cfg.H_layers}L L={arch_cfg.L_layers}L hidden={arch_cfg.hidden_size} heads={arch_cfg.num_heads}")

    tmp, train_meta = create_dataloader(args.data_path, "train", batch_size=args.batch_size, seed=args.seed)
    del tmp
    num_puzzle_ids = train_meta.num_puzzle_identifiers
    vocab_size = train_meta.vocab_size
    seq_len = train_meta.seq_len
    # NB: the sampler draws ONE puzzle per group per epoch, so the real rate is
    # total_groups / batch_size (~2.5 here), NOT scaled by mean_puzzle_examples.
    steps_per_epoch = max(1, int(train_meta.total_groups / args.batch_size))
    print(f"Train: vocab={vocab_size} seq_len={seq_len} groups={train_meta.total_groups} "
          f"~steps/epoch={steps_per_epoch}", flush=True)

    model, raw_model = build_model(arch_cfg, num_puzzle_ids, device,
                                   vocab_size=vocab_size, seq_len=seq_len, batch_size=args.batch_size)
    print(f"Total params: {sum(p.numel() for p in model.parameters()):,}", flush=True)

    optimizer = AdamATan2([p for p in model.parameters() if p.requires_grad],
                          lr=args.lr, betas=(0.9, 0.95), weight_decay=1.0)

    traj = []
    traj.append(measure_kf(raw_model, 'init'))

    def run_eval():
        model.eval()
        eval_sum = {}
        carry_eval = None
        eval_loader, _ = create_dataloader(args.data_path, "test", batch_size=args.batch_size, seed=args.seed)
        nb = 0
        with torch.no_grad():
            for _set, batch, bs in eval_loader:
                bg = {k: v.cuda() for k, v in batch.items()}
                if carry_eval is None:
                    with torch.device(device):
                        carry_eval = model.initial_carry(bg)
                carry_eval, _, metrics, _, _ = model(carry=carry_eval, batch=bg, return_keys=[])
                for k, v in metrics.items():
                    if isinstance(v, torch.Tensor):
                        eval_sum[k] = eval_sum.get(k, 0) + v.item()
                nb += 1
                if nb >= args.eval_batches:
                    break
        model.train()
        c = eval_sum.get('count', 1)
        return eval_sum.get('exact_accuracy', 0) / max(c, 1), eval_sum.get('accuracy', 0) / max(c, 1), c

    # one long train loader (enough epochs to cover max_steps)
    epochs_needed = args.max_steps // steps_per_epoch + 2
    train_loader, _ = create_dataloader(args.data_path, "train", batch_size=args.batch_size,
                                        epochs_per_iter=epochs_needed, seed=args.seed)

    global_step = 0
    carry = None
    gate_stats = {'applications': 0, 'build': 0, 'dissolve': 0, 'neutral': 0}
    t_start = time.time()
    last_log_t = t_start
    last_log_step = 0
    model.train()

    done = False
    for _set, batch, bs in train_loader:
        bg = {k: v.cuda() for k, v in batch.items()}
        optimizer.zero_grad()
        if carry is None:
            with torch.device(device):
                carry = model.initial_carry(bg)
        carry, loss, metrics, _, _ = model(carry=carry, batch=bg, return_keys=[])
        ((1.0 / bs) * loss).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        global_step += 1

        if args.gating == "bidirectional" and args.kf_lambda > 0 and global_step % args.kf_every == 0:
            apply_bidirectional_gating(raw_model, optimizer, args.kf_lambda, args.kf_threshold, gate_stats)

        if global_step % args.log_every == 0:
            now = time.time()
            sps = (global_step - last_log_step) / max(now - last_log_t, 1e-6)
            last_log_t, last_log_step = now, global_step
            gx = (f" gate(b/n/d)={gate_stats['build']}/{gate_stats['neutral']}/{gate_stats['dissolve']}"
                  if args.gating != "none" else "")
            print(f"  step {global_step}/{args.max_steps}  loss={loss.item():.4f}  "
                  f"{sps:.2f} steps/s  elapsed={now-t_start:.0f}s{gx}", flush=True)

        if global_step % args.eval_steps == 0 or global_step >= args.max_steps:
            acc, tok, cnt = run_eval()
            kf_r = measure_kf(raw_model, f'step_{global_step}')
            kf_r.update({'loss': loss.item(), 'exact_accuracy': acc, 'token_accuracy': tok,
                         'global_step': global_step, 'gate_stats': dict(gate_stats)})
            traj.append(kf_r)
            print(f"  [EVAL @ step {global_step}]  exact_acc={acc:.4f}  token_acc={tok:.4f}  "
                  f"H_CV={kf_r['H_cv']:.4e}  ratio={kf_r['h_l_ratio']:.3f}", flush=True)
            with open(os.path.join(args.save_dir, 'trajectory.json'), 'w') as f:
                json.dump({'args': vars(args), 'trajectory': traj}, f, indent=2, default=float)

        if global_step >= args.max_steps:
            done = True
            break

    torch.save({'model_state_dict': raw_model.state_dict(), 'global_step': global_step,
                'args': vars(args)}, os.path.join(args.save_dir, 'final.pt'))

    print(f"\n{'='*64}\n  SUMMARY  gating={args.gating}  seed={args.seed}\n{'='*64}")
    for kf in traj:
        if 'exact_accuracy' in kf:
            print(f"    {kf['step']:>12s}: exact={kf['exact_accuracy']:.4f} "
                  f"token={kf['token_accuracy']:.4f} loss={kf.get('loss',0):.4f} H_CV={kf['H_cv']:.4e}")
    if args.gating != "none":
        print(f"  Gate totals: {gate_stats}")
    print(f"  Total time: {(time.time()-t_start)/60:.1f} min   reached_max={done}")
    print(f"  Saved: {args.save_dir}", flush=True)


if __name__ == '__main__':
    main()
