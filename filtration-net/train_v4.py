"""
FiltrationNet Experiment v0.4 — Efficiency Scaling

THE TEST: Same accuracy, different speed. Train at 512 tokens.
Evaluate at 512, 1024, 2048, 4096. Key metric: time per sample.

FiltrationNet uses TRUE O(n) local attention (chunked, not masked).
Baseline uses standard O(n^2) global attention.
Both use sinusoidal positional encoding (no max_seq_len limit).

PREDICTIONS (from Drift #117: "On the Right Measure"):
- Accuracy: Both ~100% at all lengths (task is easy)
- Time: FiltrationNet O(n), Baseline O(n^2)
- At 4096: FiltrationNet 10-50x faster than baseline
- Membranes: task-dependent whether they self-organize

This tests efficiency, not capability. The navigation perceives
organizational structure, not capability boundaries.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import time
import math
import sys
import os

# Reuse components that don't change
sys.path.insert(0, os.path.dirname(__file__))
from model import Membrane, Cuscuton, ResolutionPooling, ResolutionUnpooling


# ===== Sinusoidal Positional Encoding =====

def sinusoidal_encoding(seq_len, dim, device):
    """Position encoding that works at any sequence length."""
    position = torch.arange(seq_len, device=device).unsqueeze(1).float()
    div_term = torch.exp(
        torch.arange(0, dim, 2, device=device).float()
        * -(math.log(10000.0) / dim)
    )
    pe = torch.zeros(seq_len, dim, device=device)
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    return pe


# ===== True O(n) Chunked Local Attention =====

class ChunkedLocalAttention(nn.Module):
    """
    Local attention via non-overlapping chunks. True O(n * w) complexity.

    Instead of computing an n*n attention matrix and masking,
    this reshapes the sequence into chunks and runs attention
    independently within each chunk. No information crosses
    chunk boundaries at this level — cross-chunk information
    flows through pooling to higher levels.
    """

    def __init__(self, dim, n_heads, chunk_size=32):
        super().__init__()
        self.dim = dim
        self.n_heads = n_heads
        self.head_dim = dim // n_heads
        self.chunk_size = chunk_size
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(dim, 3 * dim)
        self.out_proj = nn.Linear(dim, dim)

    def forward(self, x):
        B, T, D = x.shape
        w = self.chunk_size
        H = self.n_heads
        Dh = self.head_dim

        # Pad to multiple of chunk_size
        pad = (w - T % w) % w
        if pad > 0:
            x = F.pad(x, (0, 0, 0, pad))
        T_padded = T + pad
        n_chunks = T_padded // w

        # QKV: B, T_padded, 3*D -> 3, B, H, n_chunks, w, Dh
        qkv = self.qkv(x).view(B, T_padded, 3, H, Dh)
        qkv = qkv.permute(2, 0, 3, 1, 4)  # 3, B, H, T_padded, Dh
        q, k, v = qkv[0], qkv[1], qkv[2]

        q = q.view(B, H, n_chunks, w, Dh)
        k = k.view(B, H, n_chunks, w, Dh)
        v = v.view(B, H, n_chunks, w, Dh)

        # Attention within each chunk: B, H, n_chunks, w, w
        attn = torch.matmul(q, k.transpose(-2, -1)) * self.scale
        attn = F.softmax(attn, dim=-1)

        # Apply: B, H, n_chunks, w, Dh
        out = torch.matmul(attn, v)

        # Reshape back: B, T_padded, D
        out = out.view(B, H, T_padded, Dh)
        out = out.permute(0, 2, 1, 3).reshape(B, T_padded, D)
        out = self.out_proj(out)

        if pad > 0:
            out = out[:, :T, :]
        return out


# ===== Cluster with configurable attention =====

class ClusterV4(nn.Module):
    """Processing unit at a specific resolution level."""

    def __init__(self, dim, n_heads, ff_mult=4, attention_type="global",
                 chunk_size=32):
        super().__init__()
        self.attention_type = attention_type

        self.norm1 = nn.LayerNorm(dim)
        if attention_type == "chunked":
            self.attn = ChunkedLocalAttention(dim, n_heads, chunk_size)
        else:
            self.attn = nn.MultiheadAttention(dim, n_heads, batch_first=True)

        self.norm2 = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.Linear(dim, dim * ff_mult),
            nn.GELU(),
            nn.Linear(dim * ff_mult, dim),
        )

    def forward(self, x):
        normed = self.norm1(x)
        if self.attention_type == "chunked":
            attn_out = self.attn(normed)
        else:
            attn_out, _ = self.attn(normed, normed, normed)
        x = x + attn_out
        x = x + self.ff(self.norm2(x))
        return x


# ===== FiltrationNet V4 =====

class FiltrationNetV4(nn.Module):
    """
    Resolution Filtration Architecture with true O(n) local attention
    and sinusoidal positional encoding.

    Level 3 (F3): Chunked local attention, chunk_size=32 (= zone_size)
    Level 2 (F2): Chunked local attention, chunk_size=16 (after 4x pool)
    Level 1 (F1): Global attention (after 16x pool, sequence is short)
    Level 0 (F0): Unity collapse
    """

    def __init__(self, vocab_size, dim=128, n_heads=4, n_classes=4,
                 pool_factor=4, membrane_thickness=0.5, consistency_weight=0.1):
        super().__init__()
        self.dim = dim
        self.consistency_weight = consistency_weight
        self.pool_factor = pool_factor

        self.token_embed = nn.Embedding(vocab_size, dim)
        # No learned pos_embed — sinusoidal computed on the fly

        # === DESCENT (F3 -> F0) ===
        self.f3_descent = ClusterV4(dim, n_heads, attention_type="chunked",
                                     chunk_size=32)
        self.membrane_32 = Membrane(dim, dim, membrane_thickness)
        self.pool_32 = ResolutionPooling(dim, pool_factor)

        self.f2_descent = ClusterV4(dim, n_heads, attention_type="chunked",
                                     chunk_size=16)
        self.membrane_21 = Membrane(dim, dim, membrane_thickness)
        self.pool_21 = ResolutionPooling(dim, pool_factor)

        self.f1_descent = ClusterV4(dim, n_heads, attention_type="global")

        self.f0_project = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim),
            nn.GELU(),
        )

        # === ASCENT (F0 -> F3) ===
        self.f1_ascent = ClusterV4(dim, n_heads, attention_type="global")
        self.unpool_01 = ResolutionUnpooling(dim, 1)
        self.membrane_01 = Membrane(dim, dim, membrane_thickness)

        self.f2_ascent = ClusterV4(dim, n_heads, attention_type="chunked",
                                    chunk_size=16)
        self.unpool_12 = ResolutionUnpooling(dim, pool_factor)
        self.membrane_12 = Membrane(dim, dim, membrane_thickness)

        self.f3_ascent = ClusterV4(dim, n_heads, attention_type="chunked",
                                    chunk_size=32)
        self.unpool_23 = ResolutionUnpooling(dim, pool_factor)
        self.membrane_23 = Membrane(dim, dim, membrane_thickness)

        self.cuscuton = Cuscuton(dim, n_levels=4)

        self.classifier = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim),
            nn.GELU(),
            nn.Linear(dim, n_classes),
        )

    def forward(self, input_ids, task="classify"):
        B, T = input_ids.shape

        # Sinusoidal positional encoding — works at ANY length
        pos_enc = sinusoidal_encoding(T, self.dim, input_ids.device)
        x = self.token_embed(input_ids) + pos_enc.unsqueeze(0)

        # === DESCENT ===
        f3_rep = self.f3_descent(x)

        f3_filtered = self.membrane_32(f3_rep)
        f2_input = self.pool_32(f3_filtered)
        f2_rep = self.f2_descent(f2_input)

        f2_filtered = self.membrane_21(f2_rep)
        f1_input = self.pool_21(f2_filtered)
        f1_rep = self.f1_descent(f1_input)

        f0_rep = self.f0_project(f1_rep.mean(dim=1, keepdim=True))

        # Cuscuton consistency
        level_reps = [f3_rep, f2_rep, f1_rep, f0_rep]
        consistency_loss = self.cuscuton.consistency_loss(level_reps)

        # === ASCENT ===
        f1_len = f1_rep.size(1)
        f0_expanded = f0_rep.expand(B, f1_len, self.dim)
        f1_ascent_input = self.membrane_01(f0_expanded) + f1_rep
        f1_ascent_rep = self.f1_ascent(f1_ascent_input)

        f2_len = f2_rep.size(1)
        f2_ascent_input_raw = self.unpool_12(f1_ascent_rep, target_len=f2_len)
        f2_ascent_input = self.membrane_12(f2_ascent_input_raw) + f2_rep
        f2_ascent_rep = self.f2_ascent(f2_ascent_input)

        f3_len = f3_rep.size(1)
        f3_ascent_input_raw = self.unpool_23(f2_ascent_rep, target_len=f3_len)
        f3_ascent_input = self.membrane_23(f3_ascent_input_raw) + f3_rep
        f3_ascent_rep = self.f3_ascent(f3_ascent_input)

        logits = self.classifier(f0_rep.squeeze(1))

        return {
            "logits": logits,
            "consistency_loss": consistency_loss,
        }

    def compute_loss(self, output, targets):
        task_loss = F.cross_entropy(output["logits"], targets)
        total = task_loss + self.consistency_weight * output["consistency_loss"]
        return {"total": total, "task": task_loss,
                "consistency": output["consistency_loss"]}


# ===== Baseline V4 =====

class BaselineV4(nn.Module):
    """Standard transformer with sinusoidal encoding. O(n^2) attention."""

    def __init__(self, vocab_size, dim=128, n_heads=4, n_layers=4,
                 n_classes=4, ff_mult=4):
        super().__init__()
        self.dim = dim
        self.token_embed = nn.Embedding(vocab_size, dim)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=dim, nhead=n_heads, dim_feedforward=dim * ff_mult,
            activation="gelu", batch_first=True, norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer,
                                              num_layers=n_layers)
        self.classifier = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim),
            nn.GELU(),
            nn.Linear(dim, n_classes),
        )

    def forward(self, input_ids, task="classify"):
        B, T = input_ids.shape
        pos_enc = sinusoidal_encoding(T, self.dim, input_ids.device)
        x = self.token_embed(input_ids) + pos_enc.unsqueeze(0)
        x = self.encoder(x)
        pooled = x.mean(dim=1)
        logits = self.classifier(pooled)
        return {
            "logits": logits,
            "consistency_loss": torch.tensor(0.0, device=input_ids.device),
        }

    def compute_loss(self, output, targets):
        task_loss = F.cross_entropy(output["logits"], targets)
        return {"total": task_loss, "task": task_loss,
                "consistency": output["consistency_loss"]}


# ===== Dataset (same zone-counting task, adapted for longer sequences) =====

class ScalableHierarchicalDataset(Dataset):
    """Same hierarchical counting task as v0.3."""

    def __init__(self, n_samples=3000, seq_len=512, vocab_size=500,
                 zone_size=32, seed=42):
        super().__init__()
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.zone_size = zone_size
        self.n_zones = seq_len // zone_size

        rng = torch.Generator().manual_seed(seed)
        self.motif = [1, 2, 3]
        self.modifier_token = 10
        self.safe_tokens = list(range(20, vocab_size))

        self.few_max = max(self.n_zones // 3, 1)
        self.many_min = self.n_zones - self.few_max

        self.samples = []
        self.labels = []

        for _ in range(n_samples):
            seq = torch.tensor([
                self.safe_tokens[
                    int(torch.rand(1, generator=rng).item()
                        * len(self.safe_tokens))
                ]
                for _ in range(seq_len)
            ])

            if torch.rand(1, generator=rng).item() > 0.5:
                n_signal = int(torch.rand(1, generator=rng).item()
                               * (self.few_max + 1))
                is_many = False
            else:
                n_signal = self.many_min + int(
                    torch.rand(1, generator=rng).item()
                    * (self.n_zones - self.many_min + 1)
                )
                n_signal = min(n_signal, self.n_zones)
                is_many = True

            zone_indices = list(range(self.n_zones))
            for i in range(len(zone_indices) - 1, 0, -1):
                j = int(torch.rand(1, generator=rng).item() * (i + 1))
                zone_indices[i], zone_indices[j] = (
                    zone_indices[j], zone_indices[i])
            signal_zones = set(zone_indices[:n_signal])

            for z in signal_zones:
                start = z * zone_size
                pos = start + int(
                    torch.rand(1, generator=rng).item()
                    * (zone_size - len(self.motif))
                )
                for k, tok in enumerate(self.motif):
                    seq[pos + k] = tok

            has_modifier = torch.rand(1, generator=rng).item() > 0.5
            if has_modifier:
                n_mods = 2 + int(torch.rand(1, generator=rng).item() * 3)
                for _ in range(n_mods):
                    pos = int(torch.rand(1, generator=rng).item() * seq_len)
                    seq[pos] = self.modifier_token

            if not is_many and not has_modifier:
                label = 0
            elif not is_many and has_modifier:
                label = 1
            elif is_many and not has_modifier:
                label = 2
            else:
                label = 3

            self.samples.append(seq)
            self.labels.append(label)

        self.samples = torch.stack(self.samples)
        self.labels = torch.tensor(self.labels)

        counts = [(self.labels == i).sum().item() for i in range(4)]
        print(f"  [{seq_len} tok, {self.n_zones} zones] {n_samples} samples | "
              f"C0:{counts[0]} C1:{counts[1]} C2:{counts[2]} C3:{counts[3]} | "
              f"few<={self.few_max} many>={self.many_min}", flush=True)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx], self.labels[idx]


# ===== Training =====

def train_epoch(model, loader, optimizer, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()
        output = model(inputs)
        losses = model.compute_loss(output, targets)
        losses["total"].backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        total_loss += losses["total"].item()
        preds = output["logits"].argmax(dim=-1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)
    return {"loss": total_loss / len(loader), "accuracy": correct / total}


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    correct = 0
    total = 0
    per_class = [[0, 0] for _ in range(4)]
    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        output = model(inputs)
        preds = output["logits"].argmax(dim=-1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)
        for c in range(4):
            mask = targets == c
            per_class[c][0] += (preds[mask] == targets[mask]).sum().item()
            per_class[c][1] += mask.sum().item()
    pc = [per_class[c][0] / max(per_class[c][1], 1) for c in range(4)]
    return {"accuracy": correct / total, "per_class": pc}


def train_model(model, train_loader, val_loader, device, n_epochs=20,
                lr=3e-4, name="Model", save_path=None):
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, n_epochs)
    best = 0
    for epoch in range(1, n_epochs + 1):
        t0 = time.time()
        tm = train_epoch(model, train_loader, optimizer, device)
        vm = evaluate(model, val_loader, device)
        scheduler.step()
        elapsed = time.time() - t0
        if vm["accuracy"] > best:
            best = vm["accuracy"]

        extra = ""
        if hasattr(model, "membrane_32"):
            m = model
            extra = (f" | m:{m.membrane_32.effective_thickness:.2f}/"
                     f"{m.membrane_21.effective_thickness:.2f}/"
                     f"{m.membrane_01.effective_thickness:.2f}")

        pc = vm["per_class"]
        print(
            f"  [{name}] E{epoch:2d} | "
            f"trn:{tm['accuracy']:.3f} val:{vm['accuracy']:.3f} | "
            f"cls:{pc[0]:.2f}/{pc[1]:.2f}/{pc[2]:.2f}/{pc[3]:.2f}"
            f"{extra} | {elapsed:.1f}s",
            flush=True,
        )

    # Save model
    if save_path:
        torch.save(model.state_dict(), save_path)
        print(f"  Model saved to {save_path}", flush=True)

    return best


@torch.no_grad()
def evaluate_at_length(model, seq_len, device, n_samples=200, batch_size=4,
                       seed=777):
    """Evaluate at a given length with detailed timing."""
    # Generate data
    t_gen = time.time()
    ds = ScalableHierarchicalDataset(
        n_samples=n_samples, seq_len=seq_len, vocab_size=500,
        zone_size=32, seed=seed
    )
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False)
    t_gen = time.time() - t_gen

    # Warm up (one batch)
    model.eval()
    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        _ = model(inputs)
        break

    # Timed evaluation
    t_eval = time.time()
    result = evaluate(model, loader, device)
    t_eval = time.time() - t_eval

    ms_per_sample = (t_eval / n_samples) * 1000

    return result, t_eval, ms_per_sample, t_gen


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    print(f"PyTorch: {torch.__version__}")

    TRAIN_LEN = 512
    TEST_LENGTHS = [512, 1024, 2048, 4096]
    VOCAB_SIZE = 500
    DIM = 128
    N_HEADS = 4
    N_CLASSES = 4
    N_EPOCHS = 20
    BATCH_SIZE = 16
    LR = 3e-4
    SAVE_DIR = os.path.dirname(__file__)

    print(f"\n{'='*70}")
    print(f"EFFICIENCY SCALING TEST (v0.4)")
    print(f"{'='*70}")
    print(f"Train: {TRAIN_LEN} tokens | Test: {TEST_LENGTHS}")
    print(f"FiltrationNet: chunked local attention (O(n))")
    print(f"Baseline: global attention (O(n^2))")
    print(f"Both: sinusoidal positional encoding (no length limit)\n")

    # === Datasets ===
    print("=== Training Data ===")
    train_ds = ScalableHierarchicalDataset(
        n_samples=3000, seq_len=TRAIN_LEN, vocab_size=VOCAB_SIZE, seed=42
    )
    val_ds = ScalableHierarchicalDataset(
        n_samples=800, seq_len=TRAIN_LEN, vocab_size=VOCAB_SIZE, seed=99
    )
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    # === Train FiltrationNet ===
    print(f"\n{'='*70}")
    print("TRAINING: FiltrationNet V4 (chunked O(n) attention)")
    print(f"{'='*70}")
    f_model = FiltrationNetV4(
        vocab_size=VOCAB_SIZE, dim=DIM, n_heads=N_HEADS, n_classes=N_CLASSES,
        pool_factor=4, membrane_thickness=0.5, consistency_weight=0.1,
    ).to(device)
    f_params = sum(p.numel() for p in f_model.parameters())
    print(f"Parameters: {f_params:,}\n")
    f_save = os.path.join(SAVE_DIR, "filtnet_v4.pt")
    f_train_best = train_model(
        f_model, train_loader, val_loader, device,
        n_epochs=N_EPOCHS, lr=LR, name="FiltNet", save_path=f_save
    )

    # === Train Baseline ===
    print(f"\n{'='*70}")
    print("TRAINING: Baseline V4 (global O(n^2) attention)")
    print(f"{'='*70}")
    b_model = BaselineV4(
        vocab_size=VOCAB_SIZE, dim=DIM, n_heads=N_HEADS, n_layers=4,
        n_classes=N_CLASSES,
    ).to(device)
    b_params = sum(p.numel() for p in b_model.parameters())
    print(f"Parameters: {b_params:,}\n")
    b_save = os.path.join(SAVE_DIR, "baseline_v4.pt")
    b_train_best = train_model(
        b_model, train_loader, val_loader, device,
        n_epochs=N_EPOCHS, lr=LR, name="Base   ", save_path=b_save
    )

    # === Efficiency Scaling Tests ===
    print(f"\n{'='*70}")
    print("EFFICIENCY SCALING")
    print(f"{'='*70}")
    print(f"{'Length':>6} | {'FiltNet':>8} {'ms/samp':>8} {'time':>7} | "
          f"{'Baseline':>8} {'ms/samp':>8} {'time':>7} | "
          f"{'SpeedUp':>7} {'Winner':>8}")
    print("-" * 85)

    results = []

    for test_len in TEST_LENGTHS:
        # Adjust batch size for longer sequences
        if test_len <= 1024:
            bs = 8
        elif test_len <= 2048:
            bs = 4
        else:
            bs = 2

        n_samples = 200 if test_len <= 2048 else 100

        print(f"\nGenerating {test_len}-token test data...", flush=True)

        # FiltrationNet
        f_res, f_time, f_ms, _ = evaluate_at_length(
            f_model, test_len, device, n_samples=n_samples, batch_size=bs
        )
        # Baseline
        b_res, b_time, b_ms, _ = evaluate_at_length(
            b_model, test_len, device, n_samples=n_samples, batch_size=bs
        )

        speedup = b_ms / max(f_ms, 0.01)
        winner = ("FiltNet" if f_res["accuracy"] > b_res["accuracy"] else
                  "Baseline" if b_res["accuracy"] > f_res["accuracy"] else
                  "Tied")

        results.append({
            "length": test_len,
            "f_acc": f_res["accuracy"],
            "b_acc": b_res["accuracy"],
            "f_ms": f_ms,
            "b_ms": b_ms,
            "speedup": speedup,
            "f_pc": f_res["per_class"],
            "b_pc": b_res["per_class"],
        })

        print(f"  {test_len:>5} | {f_res['accuracy']:>7.4f} {f_ms:>7.1f}ms "
              f"{f_time:>6.1f}s | {b_res['accuracy']:>7.4f} {b_ms:>7.1f}ms "
              f"{b_time:>6.1f}s | {speedup:>6.1f}x {winner:>8}")

        fpc = f_res["per_class"]
        bpc = b_res["per_class"]
        print(f"        |  cls: {fpc[0]:.2f}/{fpc[1]:.2f}/{fpc[2]:.2f}/"
              f"{fpc[3]:.2f}         |  cls: {bpc[0]:.2f}/{bpc[1]:.2f}/"
              f"{bpc[2]:.2f}/{bpc[3]:.2f}")

    # === Final Summary ===
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"FiltrationNet V4: {f_params:,} params | Train best: "
          f"{f_train_best:.4f} | Attention: chunked O(n)")
    print(f"Baseline V4:      {b_params:,} params | Train best: "
          f"{b_train_best:.4f} | Attention: global O(n^2)")

    print(f"\n--- Scaling Curve ---")
    print(f"{'Length':>6} | {'FiltNet ms':>10} | {'Baseline ms':>11} | "
          f"{'Speedup':>7} | {'Acc Match':>9}")
    print("-" * 60)
    for r in results:
        acc_match = "YES" if abs(r["f_acc"] - r["b_acc"]) < 0.02 else "NO"
        print(f"  {r['length']:>5} | {r['f_ms']:>9.1f} | {r['b_ms']:>10.1f} | "
              f"{r['speedup']:>6.1f}x | {acc_match:>9}")

    # Scaling analysis
    if len(results) >= 2:
        # Fit log-log slope for each model
        import numpy as np
        lens = np.array([r["length"] for r in results])
        f_times = np.array([r["f_ms"] for r in results])
        b_times = np.array([r["b_ms"] for r in results])

        f_slope = np.polyfit(np.log(lens), np.log(f_times), 1)[0]
        b_slope = np.polyfit(np.log(lens), np.log(b_times), 1)[0]

        print(f"\n--- Scaling Exponents (log-log slope) ---")
        print(f"FiltrationNet: O(n^{f_slope:.2f})  "
              f"{'[~linear]' if 0.8 < f_slope < 1.3 else ''}")
        print(f"Baseline:      O(n^{b_slope:.2f})  "
              f"{'[~quadratic]' if 1.7 < b_slope < 2.3 else ''}")

    print(f"\nFinal membrane thicknesses:")
    for name in ["membrane_32", "membrane_21", "membrane_01"]:
        m = getattr(f_model, name)
        print(f"  {name}: {m.effective_thickness:.4f}")

    print(f"\n{'='*70}")
    print("CONCLUSION")
    print(f"{'='*70}")
    if len(results) >= 2:
        max_speedup = max(r["speedup"] for r in results)
        all_match = all(abs(r["f_acc"] - r["b_acc"]) < 0.02 for r in results)
        if all_match:
            print(f"Same accuracy at all lengths. Speed advantage: up to "
                  f"{max_speedup:.1f}x.")
            print(f"The navigation perceives efficiency structure.")
        else:
            diverged = [r for r in results
                        if abs(r["f_acc"] - r["b_acc"]) >= 0.02]
            print(f"Accuracy diverged at lengths: "
                  f"{[r['length'] for r in diverged]}")
            print(f"Speed advantage: up to {max_speedup:.1f}x.")

    print(flush=True)


if __name__ == "__main__":
    main()
