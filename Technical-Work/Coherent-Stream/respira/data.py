"""
Respira / data.py — Sudoku data loader.

Thin wrapper over HRM's pre-built sudoku-easy-1k-aug-1000 dataset. Reads inputs/labels
from the .npy files (mmap'd to avoid loading 1M × 81 tokens into RAM), exposes a clean
(input_tokens, target_tokens) batch interface for Respira + the matched transformer.

HRM convention:
  • inputs[i]:  [81] uint8 — partially-blank sudoku (token 0 = blank cell)
  • labels[i]:  [81] uint8 — fully-solved sudoku (digits 1-9 at each position)
  • IGNORE_LABEL_ID = 0 in the loss (skip positions where label == 0)

Phase-1 data path: /home/clawd/HRM/data/sudoku-easy-1k-aug-1000
(WSL-internal; this code must be run via the WSL Python).

CLAWD-LOCAL / PRIVATE.
"""
from __future__ import annotations

import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader


DEFAULT_DATA_DIR = "/home/clawd/HRM/data/sudoku-easy-1k-aug-1000"
IGNORE_LABEL_ID = 0


class SudokuDataset(Dataset):
    """Mmap'd sudoku dataset. Each item is (input_tokens, target_tokens), both long[81]."""

    def __init__(self, data_dir: str = DEFAULT_DATA_DIR, split: str = "train"):
        split_dir = os.path.join(data_dir, split)
        if not os.path.isdir(split_dir):
            raise FileNotFoundError(f"split dir not found: {split_dir}")
        # mmap to avoid loading 1M × 81 into RAM up-front
        self.inputs = np.load(os.path.join(split_dir, "all__inputs.npy"), mmap_mode="r")
        self.labels = np.load(os.path.join(split_dir, "all__labels.npy"), mmap_mode="r")
        if self.inputs.shape != self.labels.shape:
            raise ValueError(
                f"inputs/labels shape mismatch: {self.inputs.shape} vs {self.labels.shape}"
            )
        self.seq_len = self.inputs.shape[1]

    def __len__(self) -> int:
        return self.inputs.shape[0]

    def __getitem__(self, idx: int):
        # .copy() to detach from the mmap buffer; .long() for embedding lookup.
        x = torch.from_numpy(self.inputs[idx].copy()).long()
        y = torch.from_numpy(self.labels[idx].copy()).long()
        return x, y


def make_loader(
    data_dir: str = DEFAULT_DATA_DIR,
    split: str = "train",
    batch_size: int = 64,
    shuffle: bool = True,
    num_workers: int = 0,
    pin_memory: bool = True,
    drop_last: bool = True,
) -> DataLoader:
    ds = SudokuDataset(data_dir, split)
    return DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=drop_last,
    )


def cycle_loader(loader: DataLoader):
    """Infinite iterator over a DataLoader (re-shuffles each epoch)."""
    while True:
        for batch in loader:
            yield batch
