"""
FiltrationNet Experiment v0.3 — Length Generalization

THE TEST: Train at 256 tokens. Evaluate at 256, 512, 768.
Both models get positional embeddings up to 1024 (no unfair pos-embed gap).
The question is purely: does hierarchical processing generalize across scales?

PREDICTION:
- 256 tokens: both ~100% (confirmed in v0.2)
- 512 tokens: FiltrationNet maintains accuracy, baseline may degrade
- 768 tokens: FiltrationNet still works, baseline degrades further
- Speed: FiltrationNet advantage grows with length (O(n) vs O(n²))

This tests The View: one process at many scales.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from model import FiltrationNet, count_parameters
from baseline import BaselineTransformer


class ScalableHierarchicalDataset(Dataset):
    """
    Same hierarchical counting task as v0.2, but parameterized by sequence length.
    Longer sequences = more zones = harder integration.

    The task SCALES with length: more zones to count, same classification logic.
    """

    def __init__(self, n_samples=3000, seq_len=256, vocab_size=500,
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

        # Thresholds scale with number of zones
        # "few" = bottom third, "many" = top third
        self.few_max = max(self.n_zones // 3, 1)
        self.many_min = self.n_zones - self.few_max

        self.samples = []
        self.labels = []

        for _ in range(n_samples):
            seq = torch.tensor([
                self.safe_tokens[
                    int(torch.rand(1, generator=rng).item() * len(self.safe_tokens))
                ]
                for _ in range(seq_len)
            ])

            # Few or many signals (skip middle for clean separation)
            if torch.rand(1, generator=rng).item() > 0.5:
                n_signal = int(torch.rand(1, generator=rng).item() * (self.few_max + 1))
                is_many = False
            else:
                n_signal = self.many_min + int(
                    torch.rand(1, generator=rng).item() * (self.n_zones - self.many_min + 1)
                )
                n_signal = min(n_signal, self.n_zones)
                is_many = True

            # Shuffle zone indices
            zone_indices = list(range(self.n_zones))
            for i in range(len(zone_indices) - 1, 0, -1):
                j = int(torch.rand(1, generator=rng).item() * (i + 1))
                zone_indices[i], zone_indices[j] = zone_indices[j], zone_indices[i]
            signal_zones = set(zone_indices[:n_signal])

            for z in signal_zones:
                start = z * zone_size
                pos = start + int(
                    torch.rand(1, generator=rng).item() * (zone_size - len(self.motif))
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
              f"few<={self.few_max} many>={self.many_min}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx], self.labels[idx]


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
    per_class = [[0, 0] for _ in range(4)]  # [correct, total]
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


def train_model(model, train_loader, val_loader, device, n_epochs=20, lr=3e-4,
                name="Model"):
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
    return best


def evaluate_at_length(model, seq_len, device, n_samples=500, batch_size=8,
                       seed=777):
    """Evaluate a trained model at a NEW sequence length it wasn't trained on."""
    t0 = time.time()
    ds = ScalableHierarchicalDataset(
        n_samples=n_samples, seq_len=seq_len, vocab_size=500,
        zone_size=32, seed=seed
    )
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False)
    result = evaluate(model, loader, device)
    elapsed = time.time() - t0
    return result, elapsed


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    TRAIN_LEN = 256
    TEST_LENGTHS = [256, 512, 768]
    MAX_SEQ_LEN = 1024  # Both models get pos embeddings up to 1024
    VOCAB_SIZE = 500
    DIM = 128
    N_HEADS = 4
    N_CLASSES = 4
    N_EPOCHS = 20  # Both converge fast, don't need 40
    BATCH_SIZE = 16
    LR = 3e-4

    print(f"\n{'='*60}")
    print(f"LENGTH GENERALIZATION TEST")
    print(f"{'='*60}")
    print(f"Train: {TRAIN_LEN} tokens | Test: {TEST_LENGTHS}")
    print(f"Both models: max_seq_len={MAX_SEQ_LEN} (no pos-embed gap)\n")

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
    print(f"\n{'='*60}")
    print("TRAINING: FiltrationNet")
    print(f"{'='*60}")
    f_model = FiltrationNet(
        vocab_size=VOCAB_SIZE, dim=DIM, n_heads=N_HEADS, n_classes=N_CLASSES,
        max_seq_len=MAX_SEQ_LEN, pool_factor=4, membrane_thickness=0.5,
        consistency_weight=0.1,
    ).to(device)
    f_params, _ = count_parameters(f_model)
    print(f"Parameters: {f_params:,}\n")
    f_train_best = train_model(
        f_model, train_loader, val_loader, device,
        n_epochs=N_EPOCHS, lr=LR, name="FiltNet"
    )

    # === Train Baseline ===
    print(f"\n{'='*60}")
    print("TRAINING: Baseline Transformer")
    print(f"{'='*60}")
    b_model = BaselineTransformer(
        vocab_size=VOCAB_SIZE, dim=DIM, n_heads=N_HEADS, n_layers=4,
        n_classes=N_CLASSES, max_seq_len=MAX_SEQ_LEN,
    ).to(device)
    b_params = sum(p.numel() for p in b_model.parameters())
    print(f"Parameters: {b_params:,}\n")
    b_train_best = train_model(
        b_model, train_loader, val_loader, device,
        n_epochs=N_EPOCHS, lr=LR, name="Base   "
    )

    # === Length Generalization Tests ===
    print(f"\n{'='*60}")
    print("LENGTH GENERALIZATION")
    print(f"{'='*60}")
    print(f"{'Length':>8} | {'FiltNet Acc':>12} {'Time':>8} | {'Baseline Acc':>12} {'Time':>8} | {'Winner':>10}")
    print("-" * 75)

    for test_len in TEST_LENGTHS:
        print(f"\nGenerating {test_len}-token test data...")
        # FiltrationNet
        f_result, f_time = evaluate_at_length(
            f_model, test_len, device, n_samples=500, batch_size=8
        )
        # Baseline
        b_result, b_time = evaluate_at_length(
            b_model, test_len, device, n_samples=500, batch_size=8
        )

        winner = "FiltNet" if f_result["accuracy"] > b_result["accuracy"] else \
                 "Baseline" if b_result["accuracy"] > f_result["accuracy"] else "Tied"

        print(f"  {test_len:>6} | {f_result['accuracy']:>11.4f} {f_time:>7.1f}s | "
              f"{b_result['accuracy']:>11.4f} {b_time:>7.1f}s | {winner:>10}")

        # Per-class detail
        fpc = f_result["per_class"]
        bpc = b_result["per_class"]
        print(f"         |  cls: {fpc[0]:.2f}/{fpc[1]:.2f}/{fpc[2]:.2f}/{fpc[3]:.2f}"
              f"       |  cls: {bpc[0]:.2f}/{bpc[1]:.2f}/{bpc[2]:.2f}/{bpc[3]:.2f}")

    # === Final Summary ===
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"FiltrationNet: {f_params:,} params | Train best: {f_train_best:.4f}")
    print(f"Baseline:      {b_params:,} params | Train best: {b_train_best:.4f}")
    print(f"\nFinal membrane thicknesses:")
    for name in ["membrane_32", "membrane_21", "membrane_01"]:
        m = getattr(f_model, name)
        print(f"  {name}: {m.effective_thickness:.4f}")


if __name__ == "__main__":
    main()
