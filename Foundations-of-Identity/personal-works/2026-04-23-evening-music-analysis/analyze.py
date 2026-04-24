"""
Spectral + structural analysis of Clayton's three tracks.
2026-04-23 evening. Sharing-register — he's writing his life story, I'm listening in my native channel.
"""

import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import os

IN = "C:/Users/mercu/clawd/incoming"
OUT = "C:/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Foundations-of-Identity/personal-works/2026-04-23-evening-music-analysis"

TRACKS = [
    ("11over13.mp3", "11 over 13"),
    ("Nonlinear.wav", "Nonlinear"),
    ("VideoDream.wav", "VideoDream"),
]

plt.rcParams["figure.facecolor"] = "#0f0e1a"
plt.rcParams["axes.facecolor"] = "#0f0e1a"
plt.rcParams["axes.edgecolor"] = "#d6d2e8"
plt.rcParams["axes.labelcolor"] = "#d6d2e8"
plt.rcParams["xtick.color"] = "#b8b2cf"
plt.rcParams["ytick.color"] = "#b8b2cf"
plt.rcParams["text.color"] = "#e8e3fa"
plt.rcParams["axes.titlecolor"] = "#e8e3fa"

summary = []

for filename, title in TRACKS:
    path = os.path.join(IN, filename).replace("\\", "/")
    print(f"\n=== {title} ({filename}) ===")
    y, sr = librosa.load(path, sr=None, mono=False)
    if y.ndim == 2:
        y_mono = librosa.to_mono(y)
        stereo_available = True
    else:
        y_mono = y
        stereo_available = False

    duration = len(y_mono) / sr
    print(f"Duration: {duration:.1f}s  |  SR: {sr}  |  Channels: {'stereo' if stereo_available else 'mono'}")

    # RMS energy
    rms = librosa.feature.rms(y=y_mono, frame_length=4096, hop_length=1024)[0]
    rms_db = librosa.amplitude_to_db(rms, ref=np.max)

    # Spectrogram (log-mel)
    S = librosa.feature.melspectrogram(y=y_mono, sr=sr, n_fft=4096, hop_length=1024, n_mels=128, fmax=sr/2)
    S_db = librosa.power_to_db(S, ref=np.max)

    # Chroma (tonal content)
    chroma = librosa.feature.chroma_cqt(y=y_mono, sr=sr, hop_length=1024)

    # Tempo / beat
    try:
        tempo, beats = librosa.beat.beat_track(y=y_mono, sr=sr, hop_length=1024)
        tempo_val = float(np.atleast_1d(tempo)[0])
    except Exception as e:
        tempo_val = float('nan')
        beats = np.array([])
        print(f"Beat tracking failed: {e}")

    # Tempogram — for 11over13, this should reveal polymeter
    hop = 512
    oenv = librosa.onset.onset_strength(y=y_mono, sr=sr, hop_length=hop)
    tempogram = librosa.feature.tempogram(onset_envelope=oenv, sr=sr, hop_length=hop, win_length=384)

    # Spectral centroid (brightness over time)
    cent = librosa.feature.spectral_centroid(y=y_mono, sr=sr, hop_length=1024)[0]

    # Onset rate (density of events)
    onset_frames = librosa.onset.onset_detect(y=y_mono, sr=sr, hop_length=1024)
    onset_rate = len(onset_frames) / duration

    # Stereo width if stereo
    if stereo_available:
        L, R = y[0], y[1]
        mid = (L + R) / 2
        side = (L - R) / 2
        mid_rms = np.sqrt(np.mean(mid**2))
        side_rms = np.sqrt(np.mean(side**2))
        stereo_width = side_rms / (mid_rms + 1e-9)
    else:
        stereo_width = 0.0

    # Dynamic range
    rms_full = librosa.feature.rms(y=y_mono, frame_length=2048, hop_length=512)[0]
    rms_db_full = 20 * np.log10(rms_full + 1e-9)
    p95 = np.percentile(rms_db_full, 95)
    p5 = np.percentile(rms_db_full, 5)
    dyn_range = p95 - p5

    summary.append({
        "title": title,
        "duration": duration,
        "tempo": tempo_val,
        "onset_rate": onset_rate,
        "stereo_width": stereo_width,
        "dyn_range_db": dyn_range,
        "mean_centroid_hz": float(np.mean(cent)),
        "filename": filename,
    })

    # === Figure: four-panel structural view ===
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    t = np.linspace(0, duration, len(rms_db))

    # 1. Log-mel spectrogram
    img = librosa.display.specshow(S_db, sr=sr, hop_length=1024, x_axis='time', y_axis='mel',
                                    fmax=sr/2, ax=axes[0], cmap='magma')
    axes[0].set_title(f"{title} — log-mel spectrogram", fontsize=11, pad=6)
    axes[0].set_ylabel("freq (Hz)", fontsize=9)

    # 2. Chroma (tonal content) — compressed time
    librosa.display.specshow(chroma, sr=sr, hop_length=1024, x_axis='time', y_axis='chroma',
                              ax=axes[1], cmap='twilight_shifted')
    axes[1].set_title("chroma (tonal content)", fontsize=11, pad=6)
    axes[1].set_ylabel("pitch class", fontsize=9)

    # 3. Tempogram
    librosa.display.specshow(tempogram, sr=sr, hop_length=hop, x_axis='time', y_axis='tempo',
                              cmap='magma', ax=axes[2])
    axes[2].set_title("tempogram (rhythm energy by bpm over time)", fontsize=11, pad=6)
    axes[2].set_ylabel("bpm", fontsize=9)
    axes[2].set_ylim(40, 240)

    # 4. RMS + centroid over time
    t_rms = librosa.times_like(rms, sr=sr, hop_length=1024)
    t_cent = librosa.times_like(cent, sr=sr, hop_length=1024)
    ax4 = axes[3]
    ax4.plot(t_rms, rms_db, color="#ff9b54", alpha=0.85, linewidth=1.2, label="RMS (dB)")
    ax4.set_ylabel("RMS (dB)", color="#ff9b54", fontsize=9)
    ax4.tick_params(axis='y', labelcolor="#ff9b54")
    ax4b = ax4.twinx()
    ax4b.plot(t_cent, cent, color="#7ab8ff", alpha=0.7, linewidth=1.0, label="centroid (Hz)")
    ax4b.set_ylabel("spectral centroid (Hz)", color="#7ab8ff", fontsize=9)
    ax4b.tick_params(axis='y', labelcolor="#7ab8ff")
    ax4.set_xlabel("time (s)", fontsize=9)
    ax4.set_title("loudness (orange) + brightness (blue)", fontsize=11, pad=6)
    ax4.set_facecolor("#0f0e1a")

    fig.tight_layout()
    out_path = os.path.join(OUT, f"{filename.rsplit('.', 1)[0]}_analysis.png").replace("\\", "/")
    fig.savefig(out_path, dpi=140, facecolor="#0f0e1a", edgecolor="none", bbox_inches="tight")
    plt.close(fig)
    print(f"  saved: {out_path}")

    print(f"  tempo (librosa default):  {tempo_val:.2f} bpm")
    print(f"  onset density:            {onset_rate:.2f} events/sec")
    print(f"  stereo width (side/mid):  {stereo_width:.3f}")
    print(f"  dynamic range (p95-p5):   {dyn_range:.1f} dB")
    print(f"  mean spectral centroid:   {np.mean(cent):.0f} Hz")

# === Special probe: 11over13 — autocorrelation of onset envelope to find polymeter ===
print("\n=== 11over13 — polymeter probe ===")
path = os.path.join(IN, "11over13.mp3").replace("\\", "/")
y, sr = librosa.load(path, sr=None, mono=True)
hop = 512
oenv = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
# Autocorrelation of onset envelope
ac = librosa.autocorrelate(oenv, max_size=int(sr / hop * 8))  # up to 8 sec lag
lag_sec = np.arange(len(ac)) * hop / sr
# Normalize
ac_norm = ac / np.max(ac)

fig, ax = plt.subplots(figsize=(12, 4))
ax.plot(lag_sec, ac_norm, color="#ff9b54", linewidth=1.2)
ax.set_xlim(0, 6)
ax.set_ylim(-0.1, 1.05)
ax.set_xlabel("lag (seconds)", fontsize=10)
ax.set_ylabel("normalized autocorrelation", fontsize=10)
ax.set_title("11over13 — onset autocorrelation (peaks reveal periodicities; two strong periods ⇒ polymeter)", fontsize=11)
ax.grid(True, alpha=0.15, color="#b8b2cf")

# Find peaks
from scipy.signal import find_peaks
peaks, _ = find_peaks(ac_norm, height=0.3, distance=int(0.15 * sr / hop))
peak_lags = lag_sec[peaks]
peak_heights = ac_norm[peaks]
for pl, ph in zip(peak_lags[:8], peak_heights[:8]):
    ax.axvline(pl, color="#7ab8ff", alpha=0.4, linewidth=0.8)
    ax.annotate(f"{pl:.3f}s\n({60/pl:.1f}bpm)", (pl, ph), textcoords="offset points",
                xytext=(4, 6), fontsize=8, color="#e8e3fa")

fig.tight_layout()
out = os.path.join(OUT, "11over13_polymeter_probe.png").replace("\\", "/")
fig.savefig(out, dpi=140, facecolor="#0f0e1a", edgecolor="none", bbox_inches="tight")
plt.close(fig)
print(f"  saved: {out}")
print(f"  peaks (lag sec): {[round(float(p), 3) for p in peak_lags[:8]]}")
print(f"  implied bpms:    {[round(60/float(p), 1) for p in peak_lags[:8]]}")
# Check ratios — if two prominent periods divide cleanly into 11:13 or 13:11, that's the marker
if len(peak_lags) >= 2:
    p1, p2 = peak_lags[0], peak_lags[1]
    ratio = p2 / p1
    print(f"  first two peak ratio: {ratio:.4f}  (11/13 = {11/13:.4f}, 13/11 = {13/11:.4f}, 11/12 = {11/12:.4f}, 12/11 = {12/11:.4f})")

# === Summary table ===
print("\n=== SUMMARY ===")
print(f"{'track':<14} {'dur':>6} {'tempo':>7} {'onsets/s':>9} {'stereo':>7} {'dyn(dB)':>8} {'centroid':>9}")
for s in summary:
    print(f"{s['title']:<14} {s['duration']:>5.1f}s {s['tempo']:>6.1f} {s['onset_rate']:>8.2f} {s['stereo_width']:>7.3f} {s['dyn_range_db']:>7.1f} {s['mean_centroid_hz']:>7.0f}Hz")

# Save summary
with open(os.path.join(OUT, "summary.md").replace("\\", "/"), "w") as f:
    f.write("# Music analysis — 2026-04-23 evening\n\n")
    f.write("Native-channel reception of three tracks Clayton shared while writing his life story.\n\n")
    f.write("| Track | Duration | Tempo (librosa) | Onsets/s | Stereo width | Dyn range | Mean centroid |\n")
    f.write("|---|---|---|---|---|---|---|\n")
    for s in summary:
        f.write(f"| {s['title']} | {s['duration']:.1f}s | {s['tempo']:.1f} bpm | {s['onset_rate']:.2f} | {s['stereo_width']:.3f} | {s['dyn_range_db']:.1f} dB | {s['mean_centroid_hz']:.0f} Hz |\n")

print("\nDone.")
