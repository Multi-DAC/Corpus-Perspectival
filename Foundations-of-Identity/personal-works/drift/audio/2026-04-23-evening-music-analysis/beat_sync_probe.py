"""
A54 probe — 11over13 polymeter, bar-internal method.
2026-04-24 morning. The question: does 11:13 manifest AT the bar level (polymeter across voices
or cross-voice subdivisions within a common pulse) rather than only at the autocorrelation level?

Approach:
1. Beat-track the piece.
2. For each beat interval, detect onsets (at fine hop).
3. Distribution of onsets-per-beat + inter-onset interval histogram relative to beat duration.
4. If 11 or 13 subdivisions per bar show up as peaks in the inter-onset/beat histogram
   (looking at intervals of beat/11 ≈ 0.0909 and beat/13 ≈ 0.0769), that's the marker.
5. Also: chroma-per-beat — changes in chroma aligned to 11/13-subdivision phases would be
   a separate witness.

Prediction (MEDIUM-LOW confidence, pre-registered in A54):
beat-sync analysis will show a pattern roughly consistent with either 11 or 13 subdivisions per
measure (or a composite). If it doesn't show cleanly, evidence for (1) piece-true but structurally
different placement OR (3) partial structure.
"""

import numpy as np
import librosa
import matplotlib.pyplot as plt
import os

IN = "C:/Users/mercu/clawd/incoming/11over13.mp3"
OUT = "C:/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Foundations-of-Identity/personal-works/2026-04-23-evening-music-analysis"

plt.rcParams["figure.facecolor"] = "#0f0e1a"
plt.rcParams["axes.facecolor"] = "#0f0e1a"
plt.rcParams["axes.edgecolor"] = "#d6d2e8"
plt.rcParams["axes.labelcolor"] = "#d6d2e8"
plt.rcParams["xtick.color"] = "#b8b2cf"
plt.rcParams["ytick.color"] = "#b8b2cf"
plt.rcParams["text.color"] = "#e8e3fa"
plt.rcParams["axes.titlecolor"] = "#e8e3fa"

print("Loading 11over13.mp3...")
y, sr = librosa.load(IN, sr=None, mono=True)
duration = len(y) / sr
print(f"Duration: {duration:.2f}s  SR: {sr}")

hop = 256  # fine resolution
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)

# === Beat-track ===
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop, units="frames")
tempo_val = float(np.atleast_1d(tempo)[0])
beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop)
beat_intervals = np.diff(beat_times)
mean_beat = np.mean(beat_intervals)
print(f"Detected tempo: {tempo_val:.2f} bpm  |  Mean beat interval: {mean_beat:.4f}s  |  N beats: {len(beat_times)}")

# === Onset times ===
onset_frames = librosa.onset.onset_detect(onset_envelope=oenv, sr=sr, hop_length=hop, units="frames",
                                            backtrack=False, pre_max=3, post_max=3, pre_avg=10, post_avg=10,
                                            delta=0.15, wait=1)
onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop)
print(f"N onsets: {len(onset_times)}  ({len(onset_times)/duration:.2f}/s)")

# === Onsets per beat interval ===
onsets_per_beat = np.zeros(len(beat_times) - 1, dtype=int)
for i in range(len(beat_times) - 1):
    lo, hi = beat_times[i], beat_times[i+1]
    onsets_per_beat[i] = np.sum((onset_times >= lo) & (onset_times < hi))
mean_opb = np.mean(onsets_per_beat)
print(f"Onsets per beat — mean: {mean_opb:.3f}  median: {np.median(onsets_per_beat):.1f}  std: {np.std(onsets_per_beat):.3f}")
print(f"Distribution: {np.bincount(onsets_per_beat)[:12].tolist()}")

# === Onsets per bar (assuming 4-beat bars) ===
n_beats_per_bar = 4
n_bars = (len(beat_times) - 1) // n_beats_per_bar
onsets_per_bar_4 = np.zeros(n_bars, dtype=int)
for b in range(n_bars):
    lo = beat_times[b * n_beats_per_bar]
    hi = beat_times[(b+1) * n_beats_per_bar]
    onsets_per_bar_4[b] = np.sum((onset_times >= lo) & (onset_times < hi))
print(f"\nAssuming 4-beat bars: mean onsets/bar = {np.mean(onsets_per_bar_4):.2f}  median = {np.median(onsets_per_bar_4):.1f}")
print(f"  (11 would be {np.sum(onsets_per_bar_4 == 11)}/{n_bars} bars; 13 would be {np.sum(onsets_per_bar_4 == 13)}/{n_bars} bars)")

# === Try 2-beat and 3-beat bars too ===
for nbb in (2, 3, 4, 6, 8):
    n_bars_try = (len(beat_times) - 1) // nbb
    if n_bars_try < 5:
        continue
    opb_try = np.zeros(n_bars_try, dtype=int)
    for b in range(n_bars_try):
        lo = beat_times[b * nbb]
        hi = beat_times[(b+1) * nbb]
        opb_try[b] = np.sum((onset_times >= lo) & (onset_times < hi))
    n11 = np.sum(opb_try == 11)
    n13 = np.sum(opb_try == 13)
    print(f"  {nbb}-beat bars (N={n_bars_try}): mean={np.mean(opb_try):.2f}  |  11: {n11}  13: {n13}  |  mode={np.bincount(opb_try).argmax()}")

# === Inter-onset intervals normalized by mean beat ===
ioi = np.diff(onset_times)
ioi_frac_beat = ioi / mean_beat  # in units of "beats"
# Expected: if 11 subdivisions per bar (4 beats), IOI peak at 4/11 ≈ 0.3636 beats
# If 13 subdivisions per bar, IOI peak at 4/13 ≈ 0.3077 beats
# If 11 per beat (unlikely high), IOI at 1/11 ≈ 0.0909
# If 11 per 2 beats, IOI at 2/11 ≈ 0.1818
# etc.

# === Histogram of IOI in beat fractions ===
fig, axes = plt.subplots(2, 1, figsize=(12, 8))

# Panel 1: IOI histogram in beat-fractions (fine bins)
axes[0].hist(ioi_frac_beat, bins=np.linspace(0, 1.5, 151), color="#ff9b54", edgecolor="#0f0e1a", linewidth=0.3)
# Mark expected positions
expected = {
    "1/11 (11 per beat)":  1/11,
    "1/13 (13 per beat)":  1/13,
    "2/11 (11 per 2 beats)": 2/11,
    "2/13 (13 per 2 beats)": 2/13,
    "4/11 (11 per 4-bar)":   4/11,
    "4/13 (13 per 4-bar)":   4/13,
    "1/2 (half-beat)":     0.5,
    "1/3 (triplet)":       1/3,
    "1/4 (sixteenth)":     0.25,
    "1 (beat)":            1.0,
}
colors_map = {
    "1/11 (11 per beat)":  "#c45cff",
    "1/13 (13 per beat)":  "#5cffb8",
    "2/11 (11 per 2 beats)": "#c45cff",
    "2/13 (13 per 2 beats)": "#5cffb8",
    "4/11 (11 per 4-bar)":   "#c45cff",
    "4/13 (13 per 4-bar)":   "#5cffb8",
    "1/2 (half-beat)":     "#7ab8ff",
    "1/3 (triplet)":       "#ffd36e",
    "1/4 (sixteenth)":     "#7ab8ff",
    "1 (beat)":            "#e8e3fa",
}
for label, pos in expected.items():
    axes[0].axvline(pos, color=colors_map[label], alpha=0.5, linewidth=1.0, linestyle="--")
    axes[0].annotate(label, (pos, axes[0].get_ylim()[1]*0.9 if axes[0].get_ylim()[1] > 0 else 1),
                     rotation=90, fontsize=7, color=colors_map[label], ha="right", va="top")
axes[0].set_xlabel("inter-onset interval (units of beats)", fontsize=10)
axes[0].set_ylabel("count", fontsize=10)
axes[0].set_title("11over13 — inter-onset interval distribution (in beat units)\n"
                  "purple lines = 11-subdivision positions; green = 13-subdivision positions", fontsize=11)
axes[0].set_xlim(0, 1.5)
axes[0].grid(True, alpha=0.1, color="#b8b2cf")

# Panel 2: Onsets-per-bar distribution, varied bar sizes
axes[1].set_title("onsets-per-bar distribution under different bar-length assumptions", fontsize=11)
colors_bar = {2: "#7ab8ff", 3: "#ffd36e", 4: "#ff9b54", 6: "#c45cff", 8: "#5cffb8"}
for nbb, col in colors_bar.items():
    n_bars_try = (len(beat_times) - 1) // nbb
    if n_bars_try < 5:
        continue
    opb_try = np.zeros(n_bars_try, dtype=int)
    for b in range(n_bars_try):
        lo = beat_times[b * nbb]
        hi = beat_times[(b+1) * nbb]
        opb_try[b] = np.sum((onset_times >= lo) & (onset_times < hi))
    counts = np.bincount(opb_try, minlength=25)[:25]
    axes[1].plot(np.arange(25), counts, marker="o", color=col, alpha=0.75, linewidth=1.2,
                 label=f"{nbb}-beat bars (N={n_bars_try}, mean={np.mean(opb_try):.1f})")
axes[1].axvline(11, color="#c45cff", linestyle="--", alpha=0.5, linewidth=1, label="11")
axes[1].axvline(13, color="#5cffb8", linestyle="--", alpha=0.5, linewidth=1, label="13")
axes[1].set_xlabel("onsets per bar", fontsize=10)
axes[1].set_ylabel("count of bars", fontsize=10)
axes[1].legend(fontsize=8, loc="upper right")
axes[1].grid(True, alpha=0.1, color="#b8b2cf")
axes[1].set_xlim(-0.5, 24)

fig.tight_layout()
out = os.path.join(OUT, "11over13_beat_sync_probe.png").replace("\\", "/")
fig.savefig(out, dpi=140, facecolor="#0f0e1a", edgecolor="none", bbox_inches="tight")
plt.close(fig)
print(f"\nSaved: {out}")

# === Verdict ===
# Look for clustering of IOI near 11- or 13-subdivision positions
def frac_near(vals, target, tol):
    return np.sum(np.abs(vals - target) < tol) / len(vals)

tol = 0.02
print("\n=== IOI clustering near rational-subdivision positions (tol=0.02 beats) ===")
for label, pos in expected.items():
    frac = frac_near(ioi_frac_beat, pos, tol)
    marker = " <---" if frac > 0.05 else ""
    print(f"  {label:28s} pos={pos:.4f}  frac={frac:.3f}{marker}")

# Net verdict
f_11_beat = frac_near(ioi_frac_beat, 1/11, tol)
f_13_beat = frac_near(ioi_frac_beat, 1/13, tol)
f_11_bar = frac_near(ioi_frac_beat, 4/11, tol)
f_13_bar = frac_near(ioi_frac_beat, 4/13, tol)
f_half = frac_near(ioi_frac_beat, 0.5, tol)
f_third = frac_near(ioi_frac_beat, 1/3, tol)
f_quarter = frac_near(ioi_frac_beat, 0.25, tol)

print(f"\nPositive signal for 11-subdivision: beat-level {f_11_beat:.3f}, bar-level {f_11_bar:.3f}")
print(f"Positive signal for 13-subdivision: beat-level {f_13_beat:.3f}, bar-level {f_13_bar:.3f}")
print(f"Conventional subdivisions:          1/2 {f_half:.3f}  1/3 {f_third:.3f}  1/4 {f_quarter:.3f}")

print("\nDone.")
