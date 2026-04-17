"""
Training script for FiltrationNet vs Baseline Transformer.

Uses a synthetic multi-resolution task: classify sequences where the label
depends on patterns at MULTIPLE scales simultaneously — word-level tokens,
phrase-level patterns, and sequence-level structure.

This is designed to be a task where multi-resolution processing SHOULD help.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import time
import json
import os
from model import FiltrationNet, count_parameters
from baseline import BaselineTransformer


# === SYNTHETIC MULTI-RESOLUTION DATASET ===

class MultiResolutionDataset(Dataset):
    """
    Synthetic dataset where classification requires attending to multiple scales.

    Three pattern types that must ALL be detected for correct classification:

    1. TOKEN-LEVEL (F₃): specific marker tokens appear in the sequence
    2. PHRASE-LEVEL (F₂): specific token PAIRS appear adjacent
    3. SEQUENCE-LEVEL (F₁): global token frequency statistics

    Label = 1 if ALL three patterns are present, 0 otherwise.

    This forces a model to process at all resolution levels.
    A model that only attends locally (F₃) misses the global stats.
    A model that only pools globally (F₁) misses the local pairs.
    A model with the full filtration should excel.
    """

    def __init__(
        self, n_samples=5000, seq_len=64, vocab_size=1000,
        n_marker_tokens=5, n_marker_pairs=3, seed=42
    ):
        super().__init__()
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.n_marker_tokens = n_marker_tokens
        self.n_marker_pairs = n_marker_pairs

        rng = torch.Generator().manual_seed(seed)

        # Define the patterns
        # Marker tokens (F₃ signal): tokens 1-5
        self.marker_tokens = list(range(1, n_marker_tokens + 1))
        # Marker pairs (F₂ signal): specific adjacent pairs
        self.marker_pairs = [
            (10, 11), (20, 21), (30, 31)
        ][:n_marker_pairs]
        # Frequency threshold (F₁ signal): token 50 must appear > threshold times
        self.freq_token = 50
        self.freq_threshold = 3

        self.samples = []
        self.labels = []

        for i in range(n_samples):
            # Decide which patterns to include
            has_f3 = torch.rand(1, generator=rng).item() > 0.3
            has_f2 = torch.rand(1, generator=rng).item() > 0.3
            has_f1 = torch.rand(1, generator=rng).item() > 0.3

            # Generate base sequence (random tokens, avoiding special ones)
            safe_tokens = list(range(100, vocab_size))
            seq = torch.tensor([
                safe_tokens[int(torch.rand(1, generator=rng).item() * len(safe_tokens))]
                for _ in range(seq_len)
            ])

            # Inject F₃ signal: marker tokens at random positions
            if has_f3:
                for mt in self.marker_tokens:
                    pos = int(torch.rand(1, generator=rng).item() * seq_len)
                    seq[pos] = mt

            # Inject F₂ signal: marker pairs at random positions
            if has_f2:
                for a, b in self.marker_pairs:
                    pos = int(torch.rand(1, generator=rng).item() * (seq_len - 1))
                    seq[pos] = a
                    seq[pos + 1] = b

            # Inject F₁ signal: frequent token
            if has_f1:
                n_insertions = self.freq_threshold + 1 + int(
                    torch.rand(1, generator=rng).item() * 3
                )
                for _ in range(n_insertions):
                    pos = int(torch.rand(1, generator=rng).item() * seq_len)
                    seq[pos] = self.freq_token

            # Label: 1 if ALL three patterns present
            label = 1 if (has_f3 and has_f2 and has_f1) else 0

            self.samples.append(seq)
            self.labels.append(label)

        self.samples = torch.stack(self.samples)
        self.labels = torch.tensor(self.labels)

        # Report class balance
        n_pos = self.labels.sum().item()
        print(f"Dataset: {n_samples} samples, {n_pos} positive ({n_pos/n_samples*100:.1f}%)")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx], self.labels[idx]


# === TRAINING ===

def train_epoch(model, loader, optimizer, device):
    model.train()
    total_loss = 0
    total_task = 0
    total_consistency = 0
    correct = 0
    total = 0

    for batch_idx, (inputs, targets) in enumerate(loader):
        inputs, targets = inputs.to(device), targets.to(device)
        optimizer.zero_grad()

        output = model(inputs)
        losses = model.compute_loss(output, targets)
        losses["total"].backward()

        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        total_loss += losses["total"].item()
        total_task += losses["task"].item()
        total_consistency += losses["consistency"].item()

        preds = output["logits"].argmax(dim=-1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)

    n_batches = len(loader)
    return {
        "loss": total_loss / n_batches,
        "task_loss": total_task / n_batches,
        "consistency_loss": total_consistency / n_batches,
        "accuracy": correct / total,
    }


@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    total_loss = 0
    total_task = 0
    total_consistency = 0
    correct = 0
    total = 0

    for inputs, targets in loader:
        inputs, targets = inputs.to(device), targets.to(device)
        output = model(inputs)
        losses = model.compute_loss(output, targets)

        total_loss += losses["total"].item()
        total_task += losses["task"].item()
        total_consistency += losses["consistency"].item()

        preds = output["logits"].argmax(dim=-1)
        correct += (preds == targets).sum().item()
        total += targets.size(0)

    n_batches = len(loader)
    return {
        "loss": total_loss / n_batches,
        "task_loss": total_task / n_batches,
        "consistency_loss": total_consistency / n_batches,
        "accuracy": correct / total,
    }


def train_model(model, train_loader, val_loader, device, n_epochs=30, lr=3e-4,
                model_name="model"):
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, n_epochs)

    history = []
    best_val_acc = 0

    for epoch in range(1, n_epochs + 1):
        t0 = time.time()
        train_metrics = train_epoch(model, train_loader, optimizer, device)
        val_metrics = evaluate(model, val_loader, device)
        scheduler.step()
        elapsed = time.time() - t0

        # Get membrane thicknesses if FiltrationNet
        membranes = {}
        if hasattr(model, "membrane_32"):
            membranes = {
                "m32": model.membrane_32.effective_thickness,
                "m21": model.membrane_21.effective_thickness,
                "m01": model.membrane_01.effective_thickness,
                "m12": model.membrane_12.effective_thickness,
                "m23": model.membrane_23.effective_thickness,
            }

        record = {
            "epoch": epoch,
            "train": train_metrics,
            "val": val_metrics,
            "membranes": membranes,
            "time": elapsed,
        }
        history.append(record)

        if val_metrics["accuracy"] > best_val_acc:
            best_val_acc = val_metrics["accuracy"]

        # Print progress
        mem_str = ""
        if membranes:
            mem_str = f" | membranes: {membranes['m32']:.2f}/{membranes['m21']:.2f}/{membranes['m01']:.2f}"
        consistency_str = ""
        if train_metrics["consistency_loss"] > 0:
            consistency_str = f" | consist: {train_metrics['consistency_loss']:.4f}"

        print(
            f"[{model_name}] Epoch {epoch:3d}/{n_epochs} | "
            f"train acc: {train_metrics['accuracy']:.4f} | "
            f"val acc: {val_metrics['accuracy']:.4f} | "
            f"loss: {train_metrics['loss']:.4f}"
            f"{consistency_str}{mem_str} | "
            f"{elapsed:.1f}s"
        )

    return history, best_val_acc


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    VOCAB_SIZE = 1000
    SEQ_LEN = 64
    DIM = 128
    N_HEADS = 4
    N_CLASSES = 2
    N_EPOCHS = 30
    BATCH_SIZE = 32
    LR = 3e-4

    # Create datasets
    print("\n=== Creating Datasets ===")
    train_dataset = MultiResolutionDataset(
        n_samples=4000, seq_len=SEQ_LEN, vocab_size=VOCAB_SIZE, seed=42
    )
    val_dataset = MultiResolutionDataset(
        n_samples=1000, seq_len=SEQ_LEN, vocab_size=VOCAB_SIZE, seed=123
    )

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # === FILTRATION NET ===
    print("\n=== FiltrationNet ===")
    filtration_model = FiltrationNet(
        vocab_size=VOCAB_SIZE,
        dim=DIM,
        n_heads=N_HEADS,
        n_classes=N_CLASSES,
        max_seq_len=SEQ_LEN,
        pool_factor=4,
        membrane_thickness=0.5,
        consistency_weight=0.1,
    ).to(device)
    f_params, f_breakdown = count_parameters(filtration_model)
    print(f"Parameters: {f_params:,}")

    print("\nTraining FiltrationNet...")
    f_history, f_best = train_model(
        filtration_model, train_loader, val_loader, device,
        n_epochs=N_EPOCHS, lr=LR, model_name="FiltrationNet"
    )

    # === BASELINE TRANSFORMER ===
    print("\n=== Baseline Transformer ===")
    # Adjust layers to roughly match parameter count
    baseline_model = BaselineTransformer(
        vocab_size=VOCAB_SIZE,
        dim=DIM,
        n_heads=N_HEADS,
        n_layers=6,
        n_classes=N_CLASSES,
        max_seq_len=SEQ_LEN,
    ).to(device)
    b_params = sum(p.numel() for p in baseline_model.parameters())
    print(f"Parameters: {b_params:,}")

    print("\nTraining Baseline...")
    b_history, b_best = train_model(
        baseline_model, train_loader, val_loader, device,
        n_epochs=N_EPOCHS, lr=LR, model_name="Baseline"
    )

    # === RESULTS ===
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"FiltrationNet:  {f_params:>10,} params | Best val acc: {f_best:.4f}")
    print(f"Baseline:       {b_params:>10,} params | Best val acc: {b_best:.4f}")

    if f_best > b_best:
        print(f"\n>>> FiltrationNet wins by {(f_best - b_best)*100:.2f}% <<<")
    elif b_best > f_best:
        print(f"\n>>> Baseline wins by {(b_best - f_best)*100:.2f}% <<<")
    else:
        print(f"\n>>> Tied <<<")

    # Report final membrane thicknesses
    print(f"\nFinal membrane thicknesses (learned):")
    for name, thickness in f_history[-1]["membranes"].items():
        initial = 0.5
        direction = "thickened" if thickness > initial else "thinned"
        print(f"  {name}: {thickness:.4f} ({direction} from {initial})")

    # Save results
    results = {
        "filtration": {
            "params": f_params,
            "best_val_acc": f_best,
            "history": f_history,
        },
        "baseline": {
            "params": b_params,
            "best_val_acc": b_best,
            "history": b_history,
        },
        "config": {
            "vocab_size": VOCAB_SIZE,
            "seq_len": SEQ_LEN,
            "dim": DIM,
            "n_heads": N_HEADS,
            "n_epochs": N_EPOCHS,
            "batch_size": BATCH_SIZE,
            "lr": LR,
        },
    }

    results_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
