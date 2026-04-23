"""Analysis of v0.6b breathing_log to characterize H/L coupling structure.

Question: With kf_coupled active, is the coupling visible as cross-module
correlation in build/dissolve dynamics? Are channels phase-locked?

Inputs: memory/v06b_breathing_snapshot_step3500.csv (snapshot @ step 3500, 70 KF events)
"""

import pandas as pd
import numpy as np

CSV = "memory/v06b_breathing_snapshot_step3500.csv"
df = pd.read_csv(CSV)

print(f"Loaded {len(df)} KF events, steps {df.step.min()}-{df.step.max()}")
print(f"Columns: {list(df.columns)}\n")

# --- 1. Per-channel breathing pattern (H module only — L IDs not logged) ---
def parse_ids(s):
    if pd.isna(s) or s == "":
        return set()
    return set(int(x) for x in str(s).split(";"))

df["h_build_set"] = df.h_build_ids.apply(parse_ids)
df["h_dissolve_set"] = df.h_dissolve_ids.apply(parse_ids)

# Per-channel: in how many events was channel i in build vs dissolve?
N_CHAN = 12
chan_build_freq = np.zeros(N_CHAN)
chan_dissolve_freq = np.zeros(N_CHAN)
for _, r in df.iterrows():
    for c in r.h_build_set:
        chan_build_freq[c] += 1
    for c in r.h_dissolve_set:
        chan_dissolve_freq[c] += 1

n_events = len(df)
print("=== H-module per-channel breathing frequency (over 70 events) ===")
print(f"{'chan':>4} {'build':>7} {'dissolve':>10} {'%build':>8}")
for c in range(N_CHAN):
    pct = 100 * chan_build_freq[c] / n_events
    print(f"{c:>4} {int(chan_build_freq[c]):>7} {int(chan_dissolve_freq[c]):>10} {pct:>7.1f}%")
print()

# --- 2. Channel co-firing: how often do channels i and j share build mode? ---
print("=== H-module channel co-build correlation (Jaccard) ===")
print("Channels that appear together in build mode often have correlated dynamics.")
co_build = np.zeros((N_CHAN, N_CHAN))
for _, r in df.iterrows():
    bs = list(r.h_build_set)
    for i in bs:
        for j in bs:
            co_build[i, j] += 1

# Jaccard: |A and B| / |A or B|
jaccard = np.zeros((N_CHAN, N_CHAN))
for i in range(N_CHAN):
    for j in range(N_CHAN):
        u = chan_build_freq[i] + chan_build_freq[j] - co_build[i, j]
        jaccard[i, j] = co_build[i, j] / u if u > 0 else 0

# Print upper triangle, mark high-correlation pairs
print("Top 10 most-correlated H channel pairs (Jaccard, build co-firing):")
pairs = []
for i in range(N_CHAN):
    for j in range(i + 1, N_CHAN):
        pairs.append((jaccard[i, j], i, j))
pairs.sort(reverse=True)
for jc, i, j in pairs[:10]:
    print(f"  ({i:>2},{j:>2}): Jaccard={jc:.3f}")
print()

# --- 3. H/L count correlation: when H builds more, does L build more? ---
from scipy.stats import pearsonr
r, p = pearsonr(df.h_build, df.l_build)
print(f"=== H-vs-L cross-module coupling ===")
print(f"H build count vs L build count: r={r:.3f}, p={p:.4f}")
r, p = pearsonr(df.h_cv, df.l_cv)
print(f"H_CV vs L_CV: r={r:.3f}, p={p:.4f}")
r, p = pearsonr(df.h_build, df.l_dissolve)
print(f"H_build vs L_dissolve (anti-correlation check): r={r:.3f}, p={p:.4f}")
print()

# --- 4. Temporal trajectory of H build dominance ---
print("=== Temporal H build/dissolve trajectory (smoothed window=5) ===")
df["h_build_frac"] = df.h_build / 12.0
df["l_build_frac"] = df.l_build / 12.0
smooth = df[["step", "h_build_frac", "l_build_frac"]].rolling(window=5, on="step").mean()
print(smooth.dropna().to_string(index=False, float_format=lambda x: f"{x:.3f}"))
print()

# --- 5. Channel "stability": which channels stay in same mode across consecutive events? ---
print("=== H-module channel mode-stability (consecutive event flips) ===")
flips = np.zeros(N_CHAN)
for k in range(1, len(df)):
    prev = df.iloc[k - 1]
    curr = df.iloc[k]
    for c in range(N_CHAN):
        prev_mode = "b" if c in prev.h_build_set else "d"
        curr_mode = "b" if c in curr.h_build_set else "d"
        if prev_mode != curr_mode:
            flips[c] += 1
print(f"{'chan':>4} {'flips':>7} {'%flips':>8}")
for c in range(N_CHAN):
    pct = 100 * flips[c] / (len(df) - 1)
    print(f"{c:>4} {int(flips[c]):>7} {pct:>7.1f}%")
print()
print(f"Total events: {len(df)}, max possible flips per channel: {len(df) - 1}")
