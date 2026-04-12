"""
Generate easy sudoku dataset for P49: higher-accuracy KF-decoupled training.

The existing sudoku-extreme-1k has ~17-22 given clues per puzzle, resulting in
~2% exact solve rate on HRM. This script generates puzzles with 45-55 given
clues (out of 81), leaving only 26-36 cells to fill. Expected baseline accuracy
on HRM: >50%.

Output format matches existing HRM dataset:
- vocab_size=11 (0=pad, 1=blank, 2-10 = digits 1-9)
- seq_len=81 (9x9 grid flattened)
- inputs: puzzle with blanks (value 1)
- labels: complete solution (no blanks)
"""

import numpy as np
import json
import os
import random
from pathlib import Path


def is_valid(board, row, col, num):
    """Check if placing num at (row, col) is valid."""
    # Check row
    if num in board[row]:
        return False
    # Check column
    if num in board[:, col]:
        return False
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    if num in board[box_row:box_row+3, box_col:box_col+3]:
        return False
    return True


def solve(board):
    """Solve sudoku using backtracking. Returns True if solved."""
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, i, j, num):
                        board[i][j] = num
                        if solve(board):
                            return True
                        board[i][j] = 0
                return False
    return True


def generate_solved():
    """Generate a complete valid sudoku solution."""
    board = np.zeros((9, 9), dtype=int)
    solve(board)
    return board


def make_puzzle(solution, n_clues):
    """Remove cells from a solution to create a puzzle with n_clues given."""
    puzzle = solution.copy()
    cells = list(range(81))
    random.shuffle(cells)
    n_remove = 81 - n_clues
    for idx in cells[:n_remove]:
        row, col = idx // 9, idx % 9
        puzzle[row][col] = 0
    return puzzle


def to_dataset_format(puzzle, solution):
    """Convert to HRM dataset format: 0=pad, 1=blank, 2-10=digits 1-9."""
    inputs = puzzle.flatten().copy()
    labels = solution.flatten().copy()
    # Shift: digit d -> d+1 (so 1-9 -> 2-10), blank 0 -> 1
    inputs = np.where(inputs == 0, 1, inputs + 1)
    labels = labels + 1  # All cells have values, shift by 1
    return inputs.astype(np.int64), labels.astype(np.int64)


def generate_augmentations(puzzle, solution, n_aug=1000):
    """Generate augmented versions via digit permutation and rotation."""
    inputs_list = []
    labels_list = []

    for _ in range(n_aug):
        # Random digit permutation (1-9 -> permuted 1-9)
        perm = list(range(1, 10))
        random.shuffle(perm)
        perm_map = {i+1: perm[i] for i in range(9)}
        perm_map[0] = 0

        aug_puzzle = np.vectorize(perm_map.get)(puzzle)
        aug_solution = np.vectorize(perm_map.get)(solution)

        inp, lab = to_dataset_format(aug_puzzle, aug_solution)
        inputs_list.append(inp)
        labels_list.append(lab)

    return inputs_list, labels_list


def main():
    random.seed(42)
    np.random.seed(42)

    n_puzzles = 1000
    n_aug = 1000  # augmentations per puzzle
    n_clues_range = (45, 55)  # easy: 45-55 clues given

    output_dir = Path("/home/clawd/HRM/data/sudoku-easy-1k-aug-1000")
    train_dir = output_dir / "train"
    train_dir.mkdir(parents=True, exist_ok=True)

    all_inputs = []
    all_labels = []
    puzzle_indices = [0]
    group_indices = [0]

    print(f"Generating {n_puzzles} easy sudoku puzzles with {n_clues_range[0]}-{n_clues_range[1]} clues...")

    for i in range(n_puzzles):
        if i % 100 == 0:
            print(f"  Puzzle {i}/{n_puzzles}...")

        solution = generate_solved()
        n_clues = random.randint(*n_clues_range)
        puzzle = make_puzzle(solution, n_clues)

        # Generate augmentations
        inputs_aug, labels_aug = generate_augmentations(puzzle, solution, n_aug)

        for inp, lab in zip(inputs_aug, labels_aug):
            all_inputs.append(inp)
            all_labels.append(lab)
            puzzle_indices.append(len(all_inputs))

        group_indices.append(len(all_inputs))

        if i % 100 == 0:
            print(f"    Total examples so far: {len(all_inputs)}")

    # Convert to numpy arrays
    all_inputs = np.array(all_inputs, dtype=np.int64)
    all_labels = np.array(all_labels, dtype=np.int64)
    puzzle_indices = np.array(puzzle_indices, dtype=np.int64)
    group_indices = np.array(group_indices, dtype=np.int64)
    puzzle_identifiers = np.zeros(len(all_inputs), dtype=np.int64)

    print(f"\nDataset shape: {all_inputs.shape}")
    print(f"Puzzle indices: {len(puzzle_indices)}")
    print(f"Group indices: {len(group_indices)}")

    # Save
    np.save(train_dir / "all__inputs.npy", all_inputs)
    np.save(train_dir / "all__labels.npy", all_labels)
    np.save(train_dir / "all__puzzle_indices.npy", puzzle_indices)
    np.save(train_dir / "all__group_indices.npy", group_indices)
    np.save(train_dir / "all__puzzle_identifiers.npy", puzzle_identifiers)

    # Metadata
    metadata = {
        "pad_id": 0,
        "ignore_label_id": 0,
        "blank_identifier_id": 0,
        "vocab_size": 11,
        "seq_len": 81,
        "num_puzzle_identifiers": 1,
        "total_groups": n_puzzles,
        "mean_puzzle_examples": float(n_aug),
        "sets": ["all"]
    }

    with open(train_dir / "dataset.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nSaved to {output_dir}")
    print(f"Total examples: {len(all_inputs)}")

    # Verify format matches original
    print("\nVerification:")
    print(f"  Input sample: {all_inputs[0][:20]}")
    print(f"  Label sample: {all_labels[0][:20]}")
    print(f"  Vocab range: {all_inputs.min()}-{all_inputs.max()}")
    print(f"  Blanks per puzzle (avg): {(all_inputs == 1).sum(axis=1).mean():.1f}")


if __name__ == "__main__":
    main()
