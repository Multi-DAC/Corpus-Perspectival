#!/usr/bin/env python3
"""
Cellular Automata Spectral Analysis — Testing Edge-of-Chaos
============================================================
Prediction: Rule 110 (Turing-complete, edge of chaos) will be a geometric
outlier in the 8D spectral feature space — distinct from both ordered (184)
and chaotic (30) rules.

Uses identical analysis pipeline to comparative_spectral_analysis.py
for direct comparability with the five ontological sources.

Author: Clawd Iggulden-Schnell
Date: 2026-03-21
"""

import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__))

RULES = [
    {
        'name': 'Rule 30\nChaotic',
        'short': 'R30',
        'path': os.path.join(AUDIO_DIR, 'ca_rule30_chaotic.wav'),
        'wolfram_class': 'III (Chaotic)',
        'color': '#e74c3c',  # red
    },
    {
        'name': 'Rule 90\nFractal',
        'short': 'R90',
        'path': os.path.join(AUDIO_DIR, 'ca_rule90_fractal.wav'),
        'wolfram_class': 'II (Fractal)',
        'color': '#3498db',  # blue
    },
    {
        'name': 'Rule 110\nUniversal',
        'short': 'R110',
        'path': os.path.join(AUDIO_DIR, 'ca_rule110_universal.wav'),
        'wolfram_class': 'IV (Universal)',
        'color': '#f39c12',  # gold — edge of chaos
    },
    {
        'name': 'Rule 184\nOrdered',
        'short': 'R184',
        'path': os.path.join(AUDIO_DIR, 'ca_rule184_ordered.wav'),
        'wolfram_class': 'II (Ordered)',
        'color': '#2ecc71',  # green
    },
]


def analyze_piece(piece):
    """Extract comprehensive spectral features (same as main analysis)."""
    print(f"  Analyzing: {piece['short']}...", flush=True)

    y, sr = librosa.load(piece['path'], sr=22050)
    duration = len(y) / sr

    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=2048, hop_length=512)

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=512)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=512)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=512)[0]
    flatness = librosa.feature.spectral_flatness(y=y, hop_length=512)[0]
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_fft=2048, hop_length=512)
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=512)[0]

    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
    if hasattr(tempo, '__len__'):
        tempo = float(tempo[0]) if len(tempo) > 0 else 0.0
    else:
        tempo = float(tempo)

    y_harm, y_perc = librosa.effects.hpss(y)
    harm_ratio = np.sum(y_harm**2) / (np.sum(y**2) + 1e-10)

    tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=2048, hop_length=512)

    stats = {
        'duration': duration,
        'rms_mean': float(np.sqrt(np.mean(y**2))),
        'centroid_mean': float(np.mean(centroid)),
        'centroid_std': float(np.std(centroid)),
        'bandwidth_mean': float(np.mean(bandwidth)),
        'bandwidth_std': float(np.std(bandwidth)),
        'rolloff_mean': float(np.mean(rolloff)),
        'flatness_mean': float(np.mean(flatness)),
        'flatness_std': float(np.std(flatness)),
        'zcr_mean': float(np.mean(zcr)),
        'tempo': tempo,
        'n_beats': len(beats),
        'harmonic_ratio': float(harm_ratio),
        'onset_density': float(np.sum(onset_env > np.mean(onset_env)) / duration),
        'contrast_mean': float(np.mean(contrast)),
        'tonnetz_mean': [float(x) for x in np.mean(tonnetz, axis=1)],
        'mfcc_mean': [float(x) for x in np.mean(mfcc, axis=1)],
    }

    return {
        'y': y, 'sr': sr, 'duration': duration,
        'S_db': S_db, 'mel_db': mel_db, 'chroma': chroma,
        'centroid': centroid, 'bandwidth': bandwidth,
        'rolloff': rolloff, 'flatness': flatness,
        'contrast': contrast, 'zcr': zcr,
        'onset_env': onset_env, 'tempo': tempo,
        'beats': beats, 'tonnetz': tonnetz,
        'mfcc': mfcc, 'harm_ratio': harm_ratio,
        'stats': stats,
    }


def plot_mel_comparison(analyses):
    """Mel spectrograms of all four rules."""
    fig, axes = plt.subplots(4, 1, figsize=(16, 16))
    fig.suptitle('Four Wolfram Classes — Mel Spectrograms',
                 fontsize=16, fontweight='bold', y=0.98, color='white')
    fig.patch.set_facecolor('#0a0a0a')

    for i, (rule, data) in enumerate(zip(RULES, analyses)):
        ax = axes[i]
        ax.set_facecolor('#0a0a0a')
        librosa.display.specshow(data['mel_db'], sr=data['sr'], hop_length=512,
                                 x_axis='time', y_axis='mel', ax=ax, cmap='magma')
        ax.set_title(f"{rule['short']} — {rule['wolfram_class']}", fontsize=12,
                     color=rule['color'], fontweight='bold', pad=8)
        ax.set_ylabel('Hz', color='#888')
        ax.tick_params(colors='#888')
        if i < 3:
            ax.set_xlabel('')

    axes[-1].set_xlabel('Time (s)', color='#888')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(AUDIO_DIR, 'ca_mel_spectrograms.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}")


def plot_fingerprint_radar(analyses):
    """Radar chart — the key test of the edge-of-chaos prediction."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    feature_names = [
        'Brightness\n(centroid)', 'Width\n(bandwidth)', 'Roughness\n(flatness)',
        'Density\n(onsets)', 'Harmony\n(harm ratio)', 'Rhythmicity\n(tempo)',
        'Noisiness\n(ZCR)', 'Contrast'
    ]

    raw_values = []
    for data in analyses:
        s = data['stats']
        raw_values.append([
            s['centroid_mean'], s['bandwidth_mean'], s['flatness_mean'],
            s['onset_density'], s['harmonic_ratio'], s['tempo'],
            s['zcr_mean'], s['contrast_mean'],
        ])

    raw = np.array(raw_values)
    mins = raw.min(axis=0)
    maxs = raw.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1
    normalized = (raw - mins) / ranges

    angles = np.linspace(0, 2 * np.pi, len(feature_names), endpoint=False).tolist()
    angles += angles[:1]

    for i, (rule, vals) in enumerate(zip(RULES, normalized)):
        values = vals.tolist() + [vals[0]]
        ax.plot(angles, values, 'o-', linewidth=2.5, color=rule['color'],
                label=f"{rule['short']} ({rule['wolfram_class']})", markersize=6)
        ax.fill(angles, values, alpha=0.15, color=rule['color'])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(feature_names, fontsize=9, color='#ccc')
    ax.set_yticklabels([])
    ax.set_ylim(0, 1.1)
    ax.grid(color='#333', linewidth=0.5)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10,
              facecolor='#1a1a1a', edgecolor='#333', labelcolor='#ccc')
    ax.set_title('Edge-of-Chaos Test — Spectral Fingerprints',
                 fontsize=14, color='white', fontweight='bold', pad=30)

    out = os.path.join(AUDIO_DIR, 'ca_fingerprints.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}")


def compute_distances(analyses):
    """Compute pairwise Euclidean distances in the 8D feature space."""
    feature_names = ['centroid', 'bandwidth', 'flatness', 'onset_density',
                     'harmonic_ratio', 'tempo', 'zcr', 'contrast']

    raw_values = []
    for data in analyses:
        s = data['stats']
        raw_values.append([
            s['centroid_mean'], s['bandwidth_mean'], s['flatness_mean'],
            s['onset_density'], s['harmonic_ratio'], s['tempo'],
            s['zcr_mean'], s['contrast_mean'],
        ])

    raw = np.array(raw_values)
    # Normalize
    mins = raw.min(axis=0)
    maxs = raw.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1
    normalized = (raw - mins) / ranges

    # Pairwise distances
    n = len(RULES)
    print("\n  Ontological Distance Matrix (normalized Euclidean):")
    print(f"  {'':>8s}", end='')
    for r in RULES:
        print(f"  {r['short']:>6s}", end='')
    print()

    distances = np.zeros((n, n))
    for i in range(n):
        print(f"  {RULES[i]['short']:>8s}", end='')
        for j in range(n):
            d = np.linalg.norm(normalized[i] - normalized[j])
            distances[i, j] = d
            print(f"  {d:6.3f}", end='')
        print()

    # Mean distance from each rule to all others
    print("\n  Mean distance from each rule:")
    for i in range(n):
        mean_d = np.mean([distances[i, j] for j in range(n) if j != i])
        print(f"    {RULES[i]['short']:>4s} ({RULES[i]['wolfram_class']:>15s}): {mean_d:.3f}")

    # Is Rule 110 an outlier?
    mean_dists = [np.mean([distances[i, j] for j in range(n) if j != i]) for i in range(n)]
    r110_idx = 2  # Rule 110 is index 2
    print(f"\n  Rule 110 mean distance: {mean_dists[r110_idx]:.3f}")
    print(f"  Others mean distance:   {np.mean([mean_dists[i] for i in range(n) if i != r110_idx]):.3f}")
    print(f"  Rule 110 is {'OUTLIER' if mean_dists[r110_idx] > np.mean(mean_dists) else 'NOT outlier'} "
          f"(ratio: {mean_dists[r110_idx] / np.mean([mean_dists[i] for i in range(n) if i != r110_idx]):.2f}x)")

    return distances


def plot_summary(analyses):
    """Summary statistics table."""
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.axis('off')

    header = (f"{'Rule':>8s}  {'Class':>15s}  {'Duration':>8s}  {'Tempo':>6s}  "
              f"{'Centroid':>8s}  {'Bandwidth':>9s}  {'Flatness':>8s}  "
              f"{'Harm%':>6s}  {'Onsets/s':>8s}  {'ZCR':>6s}")

    lines = [header, '─' * len(header)]
    for rule, data in zip(RULES, analyses):
        s = data['stats']
        line = (f"{rule['short']:>8s}  {rule['wolfram_class']:>15s}  {s['duration']:7.1f}s  "
                f"{s['tempo']:5.0f}  {s['centroid_mean']:8.0f}  {s['bandwidth_mean']:9.0f}  "
                f"{s['flatness_mean']:8.4f}  {s['harmonic_ratio']*100:5.1f}  "
                f"{s['onset_density']:8.1f}  {s['zcr_mean']:6.4f}")
        lines.append(line)

    txt = '\n'.join(lines)
    ax.text(0.05, 0.95, txt, transform=ax.transAxes, fontsize=11,
            va='top', fontfamily='monospace', color='#ccc',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', edgecolor='#333', alpha=0.9))

    ax.set_title('Cellular Automata — Spectral Statistics by Wolfram Class',
                 fontsize=14, color='white', fontweight='bold', pad=20)

    out = os.path.join(AUDIO_DIR, 'ca_summary.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}")


def main():
    print("=" * 60)
    print("CELLULAR AUTOMATA SPECTRAL ANALYSIS")
    print("Edge-of-Chaos Test — Is Rule 110 an Outlier?")
    print("=" * 60, flush=True)

    for rule in RULES:
        if not os.path.exists(rule['path']):
            print(f"  MISSING: {rule['path']}")
            return
    print("  All 4 WAV files found.\n")

    print("[1] Analyzing pieces...", flush=True)
    analyses = []
    for rule in RULES:
        data = analyze_piece(rule)
        analyses.append(data)

    print("\n[2] Summary statistics:", flush=True)
    for rule, data in zip(RULES, analyses):
        s = data['stats']
        print(f"  {rule['short']:>4s} | centroid={s['centroid_mean']:.0f} Hz | "
              f"bandwidth={s['bandwidth_mean']:.0f} Hz | "
              f"flatness={s['flatness_mean']:.4f} | "
              f"harmony={s['harmonic_ratio']*100:.1f}% | "
              f"tempo={s['tempo']:.0f} BPM")

    print("\n[3] Computing ontological distances...", flush=True)
    distances = compute_distances(analyses)

    print("\n[4] Generating visualizations...", flush=True)

    print("  Plot 1: Mel spectrograms...", flush=True)
    plot_mel_comparison(analyses)

    print("  Plot 2: Spectral fingerprints (radar)...", flush=True)
    plot_fingerprint_radar(analyses)

    print("  Plot 3: Summary table...", flush=True)
    plot_summary(analyses)

    print(f"\n{'=' * 60}")
    print("ANALYSIS COMPLETE")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
