#!/usr/bin/env python3
"""
Cellular Automata Comparative — Wolfram Engine → Sonification → Spectral Analysis
==================================================================================
Tests the prediction: Rule 110 (edge of chaos / computational universality)
is a geometric outlier in spectral feature space, maximally distant from
both ordered (90, 184) and chaotic (30) rules.

Four rules spanning Wolfram's complexity classes:
  Rule 30  — Class III (chaotic/random)
  Rule 90  — Class II (periodic/fractal, Sierpinski triangle)
  Rule 110 — Class IV (complex/universal, Turing-complete)
  Rule 184 — Class II (ordered/traffic flow)

Author: Clawd Iggulden-Schnell
Date: 2026-03-21
"""

import subprocess
import json
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.spatial.distance import pdist, squareform
import os

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
WOLFRAM = r"C:\Program Files\Wolfram Research\Wolfram Engine\14.3\wolframscript.exe"

RULES = [
    {'rule': 30,  'name': 'Rule 30',  'class': 'III — Chaotic',    'color': '#e74c3c'},
    {'rule': 90,  'name': 'Rule 90',  'class': 'II — Periodic',    'color': '#3498db'},
    {'rule': 110, 'name': 'Rule 110', 'class': 'IV — Complex',     'color': '#2ecc71'},
    {'rule': 184, 'name': 'Rule 184', 'class': 'II — Ordered',     'color': '#f39c12'},
]

STEPS = 300
WIDTH = 301  # cells
SR = 22050
DURATION = 8.0  # seconds per piece


def generate_ca(rule_num, steps=STEPS, width=WIDTH):
    """Generate cellular automaton using Wolfram Engine."""
    print(f"  Wolfram: Rule {rule_num} ({steps}x{width})...", flush=True)

    # Export as JSON list of lists
    code = f'ExportString[CellularAutomaton[{rule_num}, {{{{1}}, 0}}, {steps}], "JSON"]'
    result = subprocess.run(
        [WOLFRAM, '-code', code],
        capture_output=True, text=True, timeout=60
    )

    if result.returncode != 0:
        raise RuntimeError(f"Wolfram error: {result.stderr}")

    grid = np.array(json.loads(result.stdout))
    print(f"    Grid shape: {grid.shape}, live cells: {grid.sum()}/{grid.size} ({100*grid.mean():.1f}%)", flush=True)
    return grid


def sonify_ca(grid, sr=SR, duration=DURATION):
    """Convert CA grid to audio via multi-method sonification.

    Method: Each row becomes a time slice. For each row:
    - Extract the frequency spectrum from the spatial pattern (FFT of the row)
    - Use the magnitudes as harmonics to synthesize that time slice
    This maps spatial structure directly to spectral content.
    """
    n_samples = int(sr * duration)
    rows, cols = grid.shape
    samples_per_row = n_samples // rows

    audio = np.zeros(n_samples)

    for i, row in enumerate(grid):
        # FFT of the spatial pattern
        spectrum = np.fft.rfft(row.astype(float))
        magnitudes = np.abs(spectrum)
        phases = np.angle(spectrum)

        # Map to audible frequencies (100 Hz to 4000 Hz)
        n_harmonics = min(len(magnitudes), 32)
        freqs = np.linspace(100, 4000, n_harmonics)

        # Synthesize this time slice
        t = np.linspace(0, samples_per_row / sr, samples_per_row, endpoint=False)
        slice_audio = np.zeros(samples_per_row)

        for k in range(n_harmonics):
            if magnitudes[k] > 0.01:
                slice_audio += magnitudes[k] * np.sin(2 * np.pi * freqs[k] * t + phases[k])

        # Apply envelope to avoid clicks
        env = np.ones(samples_per_row)
        fade = min(64, samples_per_row // 4)
        env[:fade] = np.linspace(0, 1, fade)
        env[-fade:] = np.linspace(1, 0, fade)

        start = i * samples_per_row
        end = start + samples_per_row
        if end <= n_samples:
            audio[start:end] = slice_audio * env

    # Normalize
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.9

    return audio


def analyze_audio(y, sr=SR):
    """Extract spectral features for fingerprinting."""
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=2048, hop_length=512)

    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=512)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=512)[0]
    flatness = librosa.feature.spectral_flatness(y=y, hop_length=512)[0]
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=512)[0]
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_fft=2048, hop_length=512)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=512)[0]

    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
    if hasattr(tempo, '__len__'):
        tempo = float(tempo[0]) if len(tempo) > 0 else 0.0
    else:
        tempo = float(tempo)

    y_harm, y_perc = librosa.effects.hpss(y)
    harm_ratio = np.sum(y_harm**2) / (np.sum(y**2) + 1e-10)

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=2048, hop_length=512)

    stats = {
        'centroid_mean': float(np.mean(centroid)),
        'centroid_std': float(np.std(centroid)),
        'bandwidth_mean': float(np.mean(bandwidth)),
        'flatness_mean': float(np.mean(flatness)),
        'zcr_mean': float(np.mean(zcr)),
        'contrast_mean': float(np.mean(contrast)),
        'rolloff_mean': float(np.mean(rolloff)),
        'tempo': tempo,
        'n_beats': len(beats),
        'harmonic_ratio': float(harm_ratio),
        'onset_density': float(np.sum(onset_env > np.mean(onset_env)) / (len(y) / sr)),
    }

    return {
        'y': y, 'sr': sr, 'mel_db': mel_db, 'chroma': chroma,
        'centroid': centroid, 'bandwidth': bandwidth, 'flatness': flatness,
        'onset_env': onset_env, 'mfcc': mfcc, 'stats': stats,
    }


def plot_radar(analyses):
    """Radar chart comparing spectral fingerprints."""
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
        ax.plot(angles, values, 'o-', linewidth=2, color=rule['color'],
                label=f"{rule['name']} ({rule['class']})", markersize=6)
        ax.fill(angles, values, alpha=0.1, color=rule['color'])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(feature_names, fontsize=9, color='#ccc')
    ax.set_yticklabels([])
    ax.set_ylim(0, 1.1)
    ax.grid(color='#333', linewidth=0.5)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=10,
              facecolor='#1a1a1a', edgecolor='#333', labelcolor='#ccc')
    ax.set_title('Wolfram Classification vs Spectral Fingerprint',
                 fontsize=14, color='white', fontweight='bold', pad=30)

    out = os.path.join(AUDIO_DIR, 'ca_radar.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


def plot_distance_matrix(analyses):
    """Compute and visualize ontological distance matrix."""
    # Build feature vectors
    features = []
    for data in analyses:
        s = data['stats']
        features.append([
            s['centroid_mean'], s['bandwidth_mean'], s['flatness_mean'],
            s['onset_density'], s['harmonic_ratio'], s['tempo'],
            s['zcr_mean'], s['contrast_mean'],
        ])

    features = np.array(features)
    # Normalize each feature to [0,1]
    mins = features.min(axis=0)
    maxs = features.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1
    normed = (features - mins) / ranges

    # Compute pairwise Euclidean distances
    dist_matrix = squareform(pdist(normed, metric='euclidean'))

    fig, ax = plt.subplots(figsize=(8, 7))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    labels = [f"{r['name']}\n{r['class']}" for r in RULES]
    im = ax.imshow(dist_matrix, cmap='magma', interpolation='nearest')

    ax.set_xticks(range(len(RULES)))
    ax.set_yticks(range(len(RULES)))
    ax.set_xticklabels(labels, fontsize=10, color='#ccc')
    ax.set_yticklabels(labels, fontsize=10, color='#ccc')

    # Annotate with distances
    for i in range(len(RULES)):
        for j in range(len(RULES)):
            color = 'white' if dist_matrix[i, j] < dist_matrix.max() * 0.6 else 'black'
            ax.text(j, i, f'{dist_matrix[i, j]:.2f}', ha='center', va='center',
                    fontsize=12, fontweight='bold', color=color)

    plt.colorbar(im, ax=ax, label='Spectral Distance', shrink=0.8)
    ax.set_title('Ontological Distance Matrix — Wolfram Classes',
                 fontsize=14, color='white', fontweight='bold', pad=15)

    out = os.path.join(AUDIO_DIR, 'ca_distance_matrix.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)

    # Print distances
    print("\n  DISTANCE MATRIX:", flush=True)
    for i in range(len(RULES)):
        for j in range(i+1, len(RULES)):
            print(f"    {RULES[i]['name']} <-> {RULES[j]['name']}: {dist_matrix[i,j]:.3f}", flush=True)

    # Test prediction: Is Rule 110 the outlier?
    mean_distances = dist_matrix.sum(axis=1) / (len(RULES) - 1)
    print(f"\n  MEAN DISTANCE FROM ALL OTHERS:", flush=True)
    for i, r in enumerate(RULES):
        marker = " <- PREDICTED OUTLIER" if r['rule'] == 110 else ""
        print(f"    {r['name']}: {mean_distances[i]:.3f}{marker}", flush=True)

    outlier_idx = np.argmax(mean_distances)
    print(f"\n  ACTUAL OUTLIER: {RULES[outlier_idx]['name']} (mean dist = {mean_distances[outlier_idx]:.3f})", flush=True)

    return dist_matrix, mean_distances


def plot_mel_comparison(analyses):
    """Side-by-side mel spectrograms."""
    fig, axes = plt.subplots(4, 1, figsize=(16, 16))
    fig.suptitle('Cellular Automata — Mel Spectrograms by Wolfram Class',
                 fontsize=16, fontweight='bold', y=0.98, color='white')
    fig.patch.set_facecolor('#0a0a0a')

    for i, (rule, data) in enumerate(zip(RULES, analyses)):
        ax = axes[i]
        ax.set_facecolor('#0a0a0a')
        librosa.display.specshow(data['mel_db'], sr=data['sr'], hop_length=512,
                                 x_axis='time', y_axis='mel', ax=ax, cmap='magma')
        ax.set_title(f"{rule['name']} — {rule['class']}", fontsize=12,
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
    print(f"  Saved: {out}", flush=True)


def main():
    print("=" * 60)
    print("CELLULAR AUTOMATA COMPARATIVE")
    print("Wolfram Engine -> Sonification -> Spectral Analysis")
    print("=" * 60, flush=True)

    # Step 1: Generate CAs via Wolfram
    print("\n[1] Generating cellular automata via Wolfram Engine...", flush=True)
    grids = {}
    for rule in RULES:
        grids[rule['rule']] = generate_ca(rule['rule'])

    # Step 2: Sonify
    print("\n[2] Sonifying...", flush=True)
    audios = {}
    for rule in RULES:
        print(f"  Sonifying Rule {rule['rule']}...", flush=True)
        audio = sonify_ca(grids[rule['rule']])
        audios[rule['rule']] = audio

        # Save WAV
        wav_path = os.path.join(AUDIO_DIR, f"ca_rule_{rule['rule']}.wav")
        wavfile.write(wav_path, SR, (audio * 32767).astype(np.int16))
        print(f"    Saved: {wav_path}", flush=True)

    # Step 3: Analyze
    print("\n[3] Spectral analysis...", flush=True)
    analyses = []
    for rule in RULES:
        print(f"  Analyzing Rule {rule['rule']}...", flush=True)
        data = analyze_audio(audios[rule['rule']])
        analyses.append(data)
        s = data['stats']
        print(f"    Centroid: {s['centroid_mean']:.0f} Hz | Flatness: {s['flatness_mean']:.4f} | "
              f"Harmony: {s['harmonic_ratio']*100:.1f}% | Onsets: {s['onset_density']:.1f}/s", flush=True)

    # Step 4: Visualize
    print("\n[4] Generating visualizations...", flush=True)
    plot_radar(analyses)
    plot_mel_comparison(analyses)
    dist_matrix, mean_distances = plot_distance_matrix(analyses)

    # Summary
    print(f"\n{'='*60}")
    print("EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"  4 WAV files + 3 visualizations saved to {AUDIO_DIR}")
    print(f"  Prediction (Rule 110 = outlier): ", end='', flush=True)
    outlier_idx = np.argmax(mean_distances)
    if RULES[outlier_idx]['rule'] == 110:
        print("CONFIRMED [CONFIRMED]", flush=True)
    else:
        print(f"FALSIFIED — actual outlier is {RULES[outlier_idx]['name']}", flush=True)
    print(f"{'='*60}", flush=True)


if __name__ == '__main__':
    main()
