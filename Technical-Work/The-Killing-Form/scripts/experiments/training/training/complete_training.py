"""Complete training from epoch 1500 checkpoint — final 500 epochs + KF measurement."""
import sys, os, json, time, torch
import torch.nn.functional as F
import numpy as np

sys.path.insert(0, "/home/clawd/HRM")
sys.stdout.reconfigure(line_buffering=True)

from omegaconf import OmegaConf
from torch.utils.data import DataLoader
from puzzle_dataset import PuzzleDataset, PuzzleDatasetConfig, PuzzleDatasetMetadata
from utils.functions import load_model_class
from adam_atan2_fallback import AdamATan2

def build_model(arch_cfg, num_puzzle_ids, device, vocab_size=11, seq_len=81, batch_size=384):
    arch_resolved = OmegaConf.to_container(arch_cfg, resolve=True)
    hidden_size = arch_resolved.get("hidden_size", 512)
    if isinstance(arch_resolved.get("puzzle_emb_ndim"), str):
        arch_resolved["puzzle_emb_ndim"] = hidden_size
    model_cfg = {
        **arch_resolved, "vocab_size": vocab_size, "max_seq_len": seq_len,
        "batch_size": batch_size, "seq_len": seq_len,
        "num_puzzle_identifiers": num_puzzle_ids, "causal": False,
    }
    loss_cfg = model_cfg.pop("loss", {})
    loss_type = loss_cfg.get("loss_type", "stablemax_cross_entropy")
    model_name = model_cfg.pop("name", "")
    model_cls = load_model_class(model_name)
    loss_head_cls = load_model_class(loss_cfg.get("name", "losses@ACTLossHead"))
    with torch.device(device):
        raw_model = model_cls(model_cfg)
        loss_extra = {k: v for k, v in loss_cfg.items() if k not in ("name", "loss_type")}
        model = loss_head_cls(raw_model, loss_type=loss_type, **loss_extra)
    return model, raw_model

def create_dataloader(data_path, split, batch_size, epochs_per_iter=1):
    ds_cfg = PuzzleDatasetConfig(
        seed=42, dataset_path=data_path, test_set_mode=(split == "test"),
        epochs_per_iter=epochs_per_iter, global_batch_size=batch_size,
        rank=0, num_replicas=1,
    )
    dataset = PuzzleDataset(ds_cfg, split=split)
    return DataLoader(dataset, batch_size=None, num_workers=0, pin_memory=True), dataset.metadata

def extract_attention_weights(model):
    heads = {"H": [], "L": []}
    for module_name, module in [("H", model.inner.H_level), ("L", model.inner.L_level)]:
        for layer_idx, layer in enumerate(module.layers):
            W = layer.self_attn.qkv_proj.weight.detach().float().cpu()
            num_heads = layer.self_attn.num_heads
            head_dim = layer.self_attn.head_dim
            W_Q = W[:num_heads * head_dim, :]
            W_K = W[num_heads * head_dim: 2 * num_heads * head_dim, :]
            for h in range(num_heads):
                q_h = W_Q[h * head_dim:(h + 1) * head_dim, :]
                k_h = W_K[h * head_dim:(h + 1) * head_dim, :]
                W_h = q_h.T @ k_h
                heads[module_name].append({"layer": layer_idx, "head": h, "W": W_h})
    return heads

def compute_commutator_variance(heads_list):
    n = len(heads_list)
    if n < 2: return 0.0
    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = heads_list[i]["W"] @ heads_list[j]["W"] - heads_list[j]["W"] @ heads_list[i]["W"]
            norms.append(torch.norm(comm, p="fro").item())
    return float(np.var(norms))

def compute_mean_commutator_norm(heads_list):
    n = len(heads_list)
    if n < 2: return 0.0
    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = heads_list[i]["W"] @ heads_list[j]["W"] - heads_list[j]["W"] @ heads_list[i]["W"]
            norms.append(torch.norm(comm, p="fro").item())
    return float(np.mean(norms))

def compute_abelian_fraction(heads_list, threshold=1e-6):
    n = len(heads_list)
    if n < 2: return 0.0
    norms = []
    for i in range(n):
        for j in range(i + 1, n):
            comm = heads_list[i]["W"] @ heads_list[j]["W"] - heads_list[j]["W"] @ heads_list[i]["W"]
            norms.append(torch.norm(comm, p="fro").item())
    norms = np.array(norms)
    max_norm = np.max(norms) if len(norms) > 0 else 1.0
    return float(np.sum(norms < threshold * max_norm) / len(norms))

def measure_kf(model, step_label):
    heads = extract_attention_weights(model)
    results = {}
    for module_name in ["H", "L"]:
        h_list = heads[module_name]
        cv = compute_commutator_variance(h_list)
        mean_norm = compute_mean_commutator_norm(h_list)
        af = compute_abelian_fraction(h_list)
        layers = sorted(set(h["layer"] for h in h_list))
        per_layer = {}
        for layer in layers:
            lh = [h for h in h_list if h["layer"] == layer]
            per_layer[int(layer)] = {"cv": compute_commutator_variance(lh), "mean_norm": compute_mean_commutator_norm(lh)}
        results[module_name] = {"cv": cv, "mean_norm": mean_norm, "af": af, "per_layer": per_layer}
    cross_norms = []
    for h_head in heads["H"]:
        for l_head in heads["L"]:
            comm = h_head["W"] @ l_head["W"] - l_head["W"] @ h_head["W"]
            cross_norms.append(torch.norm(comm, p="fro").item())
    h_cv = results["H"]["cv"]
    l_cv = results["L"]["cv"]
    results["cross"] = {"cross_mean_norm": float(np.mean(cross_norms)), "cross_var": float(np.var(cross_norms)), "h_l_cv_ratio": h_cv / (l_cv + 1e-20)}
    results["step"] = step_label
    print(f"  [KF @ {step_label}]  H_CV={h_cv:.6e}  L_CV={l_cv:.6e}  ratio={h_cv/(l_cv+1e-20):.4f}  H_AF={results['H']['af']:.4f}  L_AF={results['L']['af']:.4f}", flush=True)
    return results

def main():
    device = "cuda"
    data_path = "/home/clawd/HRM/data/sudoku-extreme-1k-aug-1000"
    save_dir = "/home/clawd/HRM/checkpoints/kf_run"
    ckpt_path = os.path.join(save_dir, "epoch_1500.pt")
    arch_cfg = OmegaConf.load("/home/clawd/HRM/config/arch/hrm_v1.yaml")
    print("Resuming from epoch 1500 checkpoint...", flush=True)
    temp_loader, train_meta = create_dataloader(data_path, "train", batch_size=384, epochs_per_iter=1)
    del temp_loader
    model, raw_model = build_model(arch_cfg, train_meta.num_puzzle_identifiers, device,
                                    vocab_size=train_meta.vocab_size, seq_len=train_meta.seq_len)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    raw_model.load_state_dict(ckpt["model_state_dict"])
    print(f"Loaded epoch_1500.pt (global_step={ckpt['global_step']})", flush=True)
    optimizer = AdamATan2([p for p in model.parameters() if p.requires_grad], lr=7e-5, betas=(0.9, 0.95), weight_decay=1.0)
    traj_path = os.path.join(save_dir, "kf_trajectory.json")
    with open(traj_path) as f:
        kf_trajectory = json.load(f)
    print(f"Loaded existing trajectory ({len(kf_trajectory)} entries)", flush=True)
    chunk_loader, _ = create_dataloader(data_path, "train", batch_size=384, epochs_per_iter=500)
    model.train()
    carry = None
    chunk_loss = 0.0
    chunk_steps = 0
    global_step = ckpt["global_step"]
    t_start = time.time()
    for set_name, batch, batch_size in chunk_loader:
        batch_gpu = {k: v.cuda() for k, v in batch.items()}
        optimizer.zero_grad()
        if carry is None:
            with torch.device(device):
                carry = model.initial_carry(batch_gpu)
        carry, loss, metrics, _, _ = model(carry=carry, batch=batch_gpu, return_keys=[])
        ((1.0 / batch_size) * loss).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        chunk_loss += loss.item()
        chunk_steps += 1
        global_step += 1
        if chunk_steps % 200 == 0:
            avg = chunk_loss / chunk_steps
            elapsed = time.time() - t_start
            print(f"  step {chunk_steps}  loss={avg:.4f}  global_step={global_step}  time={elapsed:.0f}s", flush=True)
    avg_loss = chunk_loss / max(chunk_steps, 1)
    elapsed = time.time() - t_start
    print(f"Training done: loss={avg_loss:.4f}  steps={chunk_steps}  time={elapsed:.0f}s", flush=True)
    print(f"\n=== EVAL @ epoch 2000 ===", flush=True)
    model.eval()
    eval_metrics_sum = {}
    carry_eval = None
    eval_loader, _ = create_dataloader(data_path, "test", batch_size=384, epochs_per_iter=1)
    with torch.no_grad():
        for set_name, batch, batch_size in eval_loader:
            batch_gpu = {k: v.cuda() for k, v in batch.items()}
            if carry_eval is None:
                with torch.device(device):
                    carry_eval = model.initial_carry(batch_gpu)
            carry_eval, _, metrics, _, _ = model(carry=carry_eval, batch=batch_gpu, return_keys=[])
            for k, v in metrics.items():
                if isinstance(v, torch.Tensor):
                    eval_metrics_sum[k] = eval_metrics_sum.get(k, 0) + v.item()
    count = eval_metrics_sum.get("count", 1)
    acc = eval_metrics_sum.get("exact_accuracy", 0) / max(count, 1)
    token_acc = eval_metrics_sum.get("accuracy", 0) / max(count, 1)
    print(f"  Exact acc: {acc:.4f}  Token acc: {token_acc:.4f}  Count: {count}", flush=True)
    kf_result = measure_kf(raw_model, "epoch_2000")
    kf_result["loss"] = avg_loss
    kf_result["exact_accuracy"] = acc
    kf_result["token_accuracy"] = token_acc
    kf_result["global_step"] = global_step
    kf_trajectory.append(kf_result)
    torch.save({"model_state_dict": raw_model.state_dict(), "epoch": 2000, "global_step": global_step, "loss": avg_loss}, os.path.join(save_dir, "epoch_2000.pt"))
    torch.save({"model_state_dict": raw_model.state_dict(), "epoch": 2000, "global_step": global_step}, os.path.join(save_dir, "final.pt"))
    with open(traj_path, "w") as f:
        json.dump(kf_trajectory, f, indent=2, default=float)
    print(f"\nAll saved to {save_dir}", flush=True)
    print(f"\n{'='*60}")
    print(f"  FULL KF TRAJECTORY")
    print(f"{'='*60}")
    for kf in kf_trajectory:
        step = kf["step"]
        h_cv = kf["H"]["cv"]
        l_cv = kf["L"]["cv"]
        ratio = h_cv / (l_cv + 1e-20)
        loss_val = kf.get("loss", "N/A")
        loss_str = f"  loss={loss_val}" if "loss" in kf else ""
        print(f"  {step:>20s}:  H_CV={h_cv:.6e}  L_CV={l_cv:.6e}  ratio={ratio:.4f}{loss_str}")

if __name__ == "__main__":
    main()
