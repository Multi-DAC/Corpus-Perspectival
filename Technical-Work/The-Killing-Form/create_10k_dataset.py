"""Create ~10K subsampled dataset: keep all 1000 groups, reduce puzzles per group to 10."""
import numpy as np
import json
import os
import shutil

src = "/home/clawd/HRM/data/sudoku-extreme-1k-aug-1000"
dst = "/home/clawd/HRM/data/sudoku-extreme-10k"

for d in [dst + "/train", dst + "/test"]:
    os.makedirs(d, exist_ok=True)

np.random.seed(42)

# --- TRAINING ---
# Original: 1000 groups, 1001 puzzles per group, 1 sample per puzzle = 1,001,000
# Target: 1000 groups, 10 puzzles per group, 1 sample per puzzle = 10,000
# Strategy: for each group, keep first 10 puzzles

train_inputs = np.load(src + "/train/all__inputs.npy")
train_labels = np.load(src + "/train/all__labels.npy")
train_puzzle_ids = np.load(src + "/train/all__puzzle_identifiers.npy")
orig_gi = np.load(src + "/train/all__group_indices.npy")
orig_pi = np.load(src + "/train/all__puzzle_indices.npy")

n_groups = 1000
puzzles_per_group = 10  # down from 1001

# Build new indices and collect samples
new_inputs = []
new_labels = []
new_puzzle_ids = []
new_gi = [0]  # group_indices starts at 0
new_pi = [0]  # puzzle_indices starts at 0
sample_count = 0

for g in range(n_groups):
    g_start = orig_gi[g]  # first puzzle index in this group
    g_end = orig_gi[g + 1]  # last puzzle index + 1
    n_puzzles_orig = g_end - g_start

    # Take first puzzles_per_group puzzles from this group
    n_take = min(puzzles_per_group, n_puzzles_orig)
    for p_offset in range(n_take):
        p_idx = g_start + p_offset
        s_start = orig_pi[p_idx]
        s_end = orig_pi[p_idx + 1]
        n_samples = s_end - s_start

        new_inputs.append(train_inputs[s_start:s_end])
        new_labels.append(train_labels[s_start:s_end])
        new_puzzle_ids.append(train_puzzle_ids[s_start:s_end])
        sample_count += n_samples
        new_pi.append(sample_count)

    new_gi.append(new_gi[-1] + n_take)

new_inputs = np.concatenate(new_inputs)
new_labels = np.concatenate(new_labels)
new_puzzle_ids = np.concatenate(new_puzzle_ids)
new_gi = np.array(new_gi, dtype=np.int32)
new_pi = np.array(new_pi, dtype=np.int32)

np.save(dst + "/train/all__inputs.npy", new_inputs)
np.save(dst + "/train/all__labels.npy", new_labels)
np.save(dst + "/train/all__puzzle_identifiers.npy", new_puzzle_ids)
np.save(dst + "/train/all__puzzle_indices.npy", new_pi)
np.save(dst + "/train/all__group_indices.npy", new_gi)

print("Train: %d samples, %d groups, %d puzzles" % (sample_count, n_groups, len(new_pi) - 1))

# --- TEST ---
# Test set: keep first 4000 samples with 1-to-1 structure
test_inputs = np.load(src + "/test/all__inputs.npy")
test_labels = np.load(src + "/test/all__labels.npy")
test_puzzle_ids = np.load(src + "/test/all__puzzle_identifiers.npy")
test_pi = np.load(src + "/test/all__puzzle_indices.npy")
test_gi = np.load(src + "/test/all__group_indices.npy")

n_test = min(4000, len(test_inputs))
np.save(dst + "/test/all__inputs.npy", test_inputs[:n_test])
np.save(dst + "/test/all__labels.npy", test_labels[:n_test])
np.save(dst + "/test/all__puzzle_identifiers.npy", test_puzzle_ids[:n_test])
np.save(dst + "/test/all__puzzle_indices.npy", test_pi[:n_test + 1])
np.save(dst + "/test/all__group_indices.npy", test_gi[:n_test + 1])

print("Test: %d samples" % n_test)

# Dataset metadata
ds_meta = {
    "pad_id": 0,
    "ignore_label_id": 0,
    "blank_identifier_id": 0,
    "vocab_size": 11,
    "seq_len": 81,
    "num_puzzle_identifiers": 1,
    "total_groups": n_groups,
    "mean_puzzle_examples": 1.0,
    "sets": ["all"]
}
for d in ["train", "test"]:
    with open(dst + "/" + d + "/dataset.json", "w") as f:
        json.dump(ds_meta, f, indent=2)

shutil.copy(src + "/identifiers.json", dst + "/identifiers.json")

# Each epoch: 1000 group selections, each yielding 1 sample → 1000 samples consumed
# At batch_size=32, that's 1000/32 = 31 batches per epoch
# At 4.79 steps/s: ~6.5s per epoch, 500 epochs = 54 min
batches = sample_count // 32
est_sec = batches / 4.79
print("")
print("Dataset: %s" % dst)
print("  Train: %d  Test: %d" % (sample_count, n_test))
print("  Groups: %d  Puzzles per group: %d" % (n_groups, puzzles_per_group))
print("  Batches/epoch (bs=32): ~%d (1000 groups / 32)" % (n_groups // 32))
print("  Note: iterator consumes groups (1 sample each), not raw samples")
print("  Est. time/epoch: ~%ds" % (n_groups // 32 / 4.79))
print("  Est. 500 epochs: %.1f min" % (500 * (n_groups // 32 / 4.79) / 60))
