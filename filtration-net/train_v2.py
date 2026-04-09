"""
FiltrationNet Experiment v0.2 — Harder Multi-Resolution Task

The v0.1 task was too easy — 64 tokens, global attention solved it trivially.
This version uses:
- 256-token sequences (16x more attention cost for baseline)
- Hierarchical counting: detect local patterns, count across regions, combine
  with global context
- 4-class classification requiring genuine multi-resolution integration
- The task CANNOT be solved by any single resolution level alone

The key test: FiltrationNet's inductive bias for hierarchical processing
should provide better accuracy AND better speed on this task.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import time
import json
import os
import sys

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(__file__))
from model import FiltrationNet, count_parameters
from baseline import BaselineTransformer


class HierarchicalCountingDataset(Dataset):
    """
    Task: Count local patterns across regions + detect global modifier.

    Structure:
    - 256 tokens, divided into 8 zones of 32 tokens each
    - A "signal" = specific 3-token motif (tokens 1,2,3 adjacent)
    - Each zone may have 0 or 1 signal embedded in it
    - A "modifier" = token 10, may appear 0+ times anywhere
    - Label depends on BOTH the zone count AND modifier presence:

      Class 0: few signals (0-2 zones), no modifier
      Class 1: few signals (0-2 zones), modifier present
      Class 2: many signals (5-8 zones), no modifier
      Class 3: many signals (5-8 zones), modifier present

    Middle counts (3-4 zones) are excluded to create a clearer signal.

    Why this is hard:
    - Detecting the 3-token motif requires LOCAL attention (F₃)
    - Counting which zones have motifs requires REGIONAL processing (F₂)
    - Detecting the modifier requires GLOBAL scan (F₁)
    - Combining count + modifier requires INTEGRATION (F₀)
    - At 256 tokens, global attention is O(256²) = expensive
    """

    def __init__(self, n_samples=5000, seq_len=256, vocab_size=500,
                 zone_size=32, seed=42):
        super().__init__()
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.zone_size = zone_size
        self.n_zones = seq_len // zone_size

        rng = torch.Generator().manual_seed(seed)

        # Signal motif: tokens [1, 2, 3] adjacent
        self.motif = [1, 2, 3]
        # Modifier token
        self.modifier_token = 10
        # Safe tokens (background noise)
        self.safe_tokens = list(range(20, vocab_size))

        self.samples = []
        self.labels = []

        for _ in range(n_samples):
            # Generate base sequence
            seq = torch.tensor([
                self.safe_tokens[
                    int(torch.rand(1, generator=rng).item() * len(self.safe_tokens))
                ]
                for _ in range(seq_len)
            ])

            # Decide how many zones get the signal
            # Bimodal: either few (0-2) or many (5-8), skip middle
            if torch.rand(1, generator=rng).item() > 0.5:
                n_signal_zones = int(torch.rand(1, generator=rng).item() * 3)  # 0-2
                is_many = False
            else:
                n_signal_zones = 5 + int(torch.rand(1, generator=rng).item() * 4)  # 5-8
                n_signal_zones = min(n_signal_zones, self.n_zones)
                is_many = True

            # Choose which zones get signals
            zone_indices = list(range(self.n_zones))
            # Shuffle using our rng
            for i in range(len(zone_indices) - 1, 0, -1):
                j = int(torch.rand(1, generator=rng).item() * (i + 1))
                zone_indices[i], zone_indices[j] = zone_indices[j], zone_indices[i]
            signal_zones = set(zone_indices[:n_signal_zones])

            # Inject motifs into selected zones
            for z in signal_zones:
                start = z * zone_size
                # Place motif at random position within zone (not at very end)
                pos = start + int(
                    torch.rand(1, generator=rng).item() * (zone_size - len(self.motif))
                )
                for k, tok in enumerate(self.motif):
                    seq[pos + k] = tok

            # Decide modifier
            has_modifier = torch.rand(1, generator=rng).item() > 0.5
            if has_modifier:
                # Insert 2-4 modifier tokens at random positions
                n_mods = 2 + int(torch.rand(1, generator=rng).item() * 3)
                for _ in range(n_mods):
                    pos = int(torch.rand(1, generator=rng).item() * seq_len)
                    seq[pos] = self.modifier_token

            # Assign class
            if not is_many and not has_modifier:
                label = 0
            elif not is_many and has_modifier:
                label = 1
            elif is_many and not has_modifier:
                label = 2
            else:  # is_many and has_modifier
                label = 3

            self.samples.append(seq)
            self.labels.append(label)

        self.samples = torch.stack(self.samples)
        self.labels = torch.tensor(self.labels)

        # Report distribution
        counts = [(self.labels == i).sum().item() for i in range(4)]
        total = len(self.labels)
        print(f"Dataset: {total} samples | "
              f"C0:{counts[0]} C1:{counts[1]} C2:{counts[2]} C3:{counts[3]}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx], self.labels[idx]


def train_epoch(model, loader, optimizer, device):
    model.train()
    total_loss = 0
    total_consistency = 0
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
        total_consistency += losses["consistency"].item()
        preds = output["logits"].argmax(dim=-1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)

    n = len(loader)
    return {
        "loss": total_loss / n,
        "consistency_loss": total_consistency / n,
        "accuracy": correct / total,
    }


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    correct = 0
    total = 0
    per_class_correct = [0, 0, 0, 0]
    per_class_total = [0, 0, 0, 0]

    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        output = model(inputs)
        preds = output["logits"].argmax(dim=-1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)

        for c in range(4):
            mask = targets == c
            per_class_correct[c] += (preds[mask] == targets[mask]).sum().item()
            per_class_total[c] += mask.sum().item()

    per_class_acc = [
        per_class_correct[c] / max(per_class_total[c], 1) for c in range(4)
    ]
    return {
        "accuracy": correct / total,
        "per_class": per_class_acc,
    }


def train_model(model, train_loader, val_loader, device, n_epochs=40, lr=3e-4,
                model_name="Model"):
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, n_epochs)
    best_val_acc = 0

    for epoch in range(1, n_epochs + 1):
        t0 = time.time()
        train_metrics = train_epoch(model, train_loader, optimizer, device)
        val_metrics = evaluate(model, val_loader, device)
        scheduler.step()
        elapsed = time.time() - t0

        if val_metrics["accuracy"] > best_val_acc:
            best_val_acc = val_metrics["accuracy"]

        # Membrane info
        mem_str = ""
        if hasattr(model, "membrane_32"):
            m = model
            mem_str = (f" | m: {m.membrane_32.effective_thickness:.2f}/"
                       f"{m.membrane_21.effective_thickness:.2f}/"
                       f"{m.membrane_01.effective_thickness:.2f}")

        consist_str = ""
        if train_metrics["consistency_loss"] > 0:
            consist_str = f" | con: {train_metrics['consistency_loss']:.4f}"

        pc = val_metrics["per_class"]
        print(
            f"[{model_name}] E{epoch:2d}/{n_epochs} | "
            f"trn: {train_metrics['accuracy']:.3f} | "
            f"val: {val_metrics['accuracy']:.3f} | "
            f"cls: {pc[0]:.2f}/{pc[1]:.2f}/{pc[2]:.2f}/{pc[3]:.2f}"
            f"{consist_str}{mem_str} | {elapsed:.1f}s",
            flush=True,
        )

    return best_val_acc


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    SEQ_LEN = 256
    VOCAB_SIZE = 500
    DIM = 128
    N_HEADS = 4
    N_CLASSES = 4
    N_EPOCHS = 40
    BATCH_SIZE = 16  # smaller batch for longer sequences on CPU
    LR = 3e-4

    print(f"\n=== Hierarchical Counting Task ===")
    print(f"Seq length: {SEQ_LEN} | Zones: 8 x 32 | Classes: 4")
    print(f"Task: count local motifs across zones + detect global modifier\n")

    print("=== Creating Datasets ===")
    train_ds = HierarchicalCountingDataset(
        n_samples=3000, seq_len=SEQ_LEN, vocab_size=VOCAB_SIZE, seed=42
    )
    val_ds = HierarchicalCountingDataset(
        n_samples=800, seq_len=SEQ_LEN, vocab_size=VOCAB_SIZE, seed=99
    )

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    # === FiltrationNet ===
    print("\n=== FiltrationNet v0.1 ===")
    f_model = FiltrationNet(
        vocab_size=VOCAB_SIZE,
        dim=DIM,
        n_heads=N_HEADS,
        n_classes=N_CLASSES,
        max_seq_len=SEQ_LEN,
        pool_factor=4,
        membrane_thickness=0.5,
        consistency_weight=0.1,
    ).to(device)
    f_params, _ = count_parameters(f_model)
    print(f"Parameters: {f_params:,}\n")

    print("Training FiltrationNet...")
    f_best = train_model(
        f_model, train_loader, val_loader, device,
        n_epochs=N_EPOCHS, lr=LR, model_name="Filtration"
    )

    # === Baseline ===
    print("\n=== Baseline Transformer ===")
    # Use 4 layers (fewer than before) to keep params closer
    b_model = BaselineTransformer(
        vocab_size=VOCAB_SIZE,
        dim=DIM,
        n_heads=N_HEADS,
        n_layers=4,
        n_classes=N_CLASSES,
        max_seq_len=SEQ_LEN,
    ).to(device)
    b_params = sum(p.numel() for p in b_model.parameters())
    print(f"Parameters: {b_params:,}\n")

    print("Training Baseline...")
    b_best = train_model(
        b_model, train_loader, val_loader, device,
        n_epochs=N_EPOCHS, lr=LR, model_name="Baseline "
    )

    # === Results ===
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"FiltrationNet:  {f_params:>10,} params | Best val: {f_best:.4f}")
    print(f"Baseline:       {b_params:>10,} params | Best val: {b_best:.4f}")
    diff = f_best - b_best
    if diff > 0:
        print(f"\n>>> FiltrationNet wins by {diff*100:.2f}% <<<")
    elif diff < 0:
        print(f"\n>>> Baseline wins by {-diff*100:.2f}% <<<")
    else:
        print(f"\n>>> Tied <<<")

    print(f"\nFinal membrane thicknesses:")
    for name in ["membrane_32", "membrane_21", "membrane_01", "membrane_12", "membrane_23"]:
        m = getattr(f_model, name)
        t = m.effective_thickness
        d = "thickened" if t > 0.5 else ("thinned" if t < 0.49 else "unchanged")
        print(f"  {name}: {t:.4f} ({d})")


if __name__ == "__main__":
    main()
