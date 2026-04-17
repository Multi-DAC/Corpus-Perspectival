#!/usr/bin/env python3
"""
Comparative Spectral Analysis — All Five Compositions
=====================================================
Each piece derives from a different ontological source:
  1. BAO DR2 Sonification  — observational cosmology (DESI DR2 BAO data)
  2. The Warp Factor        — theoretical geometry (RS warp factor e^{-2ky})
  3. The Posterior           — statistical inference (Phase 18A v3 MCMC chains)
  4. Mass Spectrum           — particle physics (PDG 2024 SM fermion masses)
  5. Cellular Counterpoint   — emergent computation (Rule 110 automaton)

Question: Do different ontological inputs produce structurally different
spectral signatures? Is the source visible in the sound?

This is refraction — epistemic gain from cross-modal translation.

Author: Clawd Iggulden-Schnell
Date: 2026-03-21
"""

import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# ============================================================
# PATHS
# ============================================================

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(os.path.dirname(AUDIO_DIR), 'music')

PIECES = [
    {
        'name': 'BAO DR2\nSonification',
        'short': 'BAO',
        'path': os.path.join(AUDIO_DIR, 'bao_dr2_sonification.wav'),
        'source': 'Observation',
        'color': '#e74c3c',  # red — cosmological data
    },
    {
        'name': 'The Warp\nFactor',
        'short': 'Warp',
        'path': os.path.join(MUSIC_DIR, 'the_warp_factor.wav'),
        'source': 'Theory',
        'color': '#3498db',  # blue — geometric theory
    },
    {
        'name': 'The\nPosterior',
        'short': 'Post',
        'path': os.path.join(MUSIC_DIR, 'the_posterior.wav'),
        'source': 'Inference',
        'color': '#9b59b6',  # purple — statistical
    },
    {
        'name': 'Mass\nSpectrum',
        'short': 'Mass',
        'path': os.path.join(MUSIC_DIR, 'mass_spectrum.wav'),
        'source': 'Measurement',
        'color': '#f39c12',  # orange — particle data
    },
    {
        'name': 'Cellular\nCounterpoint',
        'short': 'Cell',
        'path': os.path.join(MUSIC_DIR, 'cellular_counterpoint.wav'),
        'source': 'Emergence',
        'color': '#2ecc71',  # green — computational
    },
]

# ============================================================
# ANALYSIS
# ============================================================

def analyze_piece(piece):
    """Extract comprehensive spectral features from a piece."""
    print(f"  Analyzing: {piece['short']}...", flush=True)

    y, sr = librosa.load(piece['path'], sr=22050)
    duration = len(y) / sr

    # Core spectral representations
    S = np.abs(librosa.stft(y, n_fft=2048, hop_length=512))
    S_db = librosa.amplitude_to_db(S, ref=np.max)
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, n_fft=2048, hop_length=512)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=2048, hop_length=512)

    # Spectral features (time series)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=512)[0]
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=512)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=512)[0]
    flatness = librosa.feature.spectral_flatness(y=y, hop_length=512)[0]
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_fft=2048, hop_length=512)
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=512)[0]

    # Rhythm / temporal structure
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=512)
    # Handle tempo as array or scalar
    if hasattr(tempo, '__len__'):
        tempo = float(tempo[0]) if len(tempo) > 0 else 0.0
    else:
        tempo = float(tempo)

    # Harmonic-percussive separation
    y_harm, y_perc = librosa.effects.hpss(y)
    harm_ratio = np.sum(y_harm**2) / (np.sum(y**2) + 1e-10)

    # Tonnetz (tonal centroid)
    tonnetz = librosa.feature.tonnetz(y=y, sr=sr)

    # MFCCs (timbral fingerprint)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=2048, hop_length=512)

    # Summary statistics
    stats = {
        'duration': duration,
        'sr': sr,
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


# ============================================================
# VISUALIZATION 1: Grand Comparison (Mel Spectrograms)
# ============================================================

def plot_mel_comparison(analyses):
    """Side-by-side mel spectrograms of all five pieces."""
    fig, axes = plt.subplots(5, 1, figsize=(16, 20))
    fig.suptitle('Five Ontological Sources — Mel Spectrograms',
                 fontsize=16, fontweight='bold', y=0.98, color='white')
    fig.patch.set_facecolor('#0a0a0a')

    for i, (piece, data) in enumerate(zip(PIECES, analyses)):
        ax = axes[i]
        ax.set_facecolor('#0a0a0a')
        librosa.display.specshow(data['mel_db'], sr=data['sr'], hop_length=512,
                                 x_axis='time', y_axis='mel', ax=ax,
                                 cmap='magma')
        ax.set_title(f"{piece['short']} — {piece['source']}", fontsize=12,
                     color=piece['color'], fontweight='bold', pad=8)
        ax.set_ylabel('Hz', color='#888')
        ax.tick_params(colors='#888')
        if i < 4:
            ax.set_xlabel('')

    axes[-1].set_xlabel('Time (s)', color='#888')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(AUDIO_DIR, 'comparative_mel_spectrograms.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


# ============================================================
# VISUALIZATION 2: Spectral Fingerprint Radar
# ============================================================

def plot_fingerprint_radar(analyses):
    """Radar chart comparing spectral features across pieces."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')

    # Features to compare (normalized to [0, 1])
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
    # Min-max normalize each feature across pieces
    mins = raw.min(axis=0)
    maxs = raw.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1  # avoid division by zero
    normalized = (raw - mins) / ranges

    angles = np.linspace(0, 2 * np.pi, len(feature_names), endpoint=False).tolist()
    angles += angles[:1]

    for i, (piece, vals) in enumerate(zip(PIECES, normalized)):
        values = vals.tolist() + [vals[0]]
        ax.plot(angles, values, 'o-', linewidth=2, color=piece['color'],
                label=f"{piece['short']} ({piece['source']})", markersize=5)
        ax.fill(angles, values, alpha=0.1, color=piece['color'])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(feature_names, fontsize=9, color='#ccc')
    ax.set_yticklabels([])
    ax.set_ylim(0, 1.1)
    ax.grid(color='#333', linewidth=0.5)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10,
              facecolor='#1a1a1a', edgecolor='#333', labelcolor='#ccc')
    ax.set_title('Spectral Fingerprints — Five Ontological Sources',
                 fontsize=14, color='white', fontweight='bold', pad=30)

    out = os.path.join(AUDIO_DIR, 'comparative_fingerprints.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


# ============================================================
# VISUALIZATION 3: Timbral Landscape (MFCC Space)
# ============================================================

def plot_mfcc_comparison(analyses):
    """MFCC heatmaps — the 'timbral DNA' of each piece."""
    fig, axes = plt.subplots(5, 1, figsize=(16, 15))
    fig.suptitle('Timbral DNA — MFCC Fingerprints',
                 fontsize=16, fontweight='bold', y=0.98, color='white')
    fig.patch.set_facecolor('#0a0a0a')

    for i, (piece, data) in enumerate(zip(PIECES, analyses)):
        ax = axes[i]
        ax.set_facecolor('#0a0a0a')
        librosa.display.specshow(data['mfcc'], sr=data['sr'], hop_length=512,
                                 x_axis='time', ax=ax, cmap='coolwarm')
        ax.set_title(f"{piece['short']} — {piece['source']}", fontsize=11,
                     color=piece['color'], fontweight='bold', pad=5)
        ax.set_ylabel('MFCC', color='#888', fontsize=9)
        ax.tick_params(colors='#888')
        if i < 4:
            ax.set_xlabel('')

    axes[-1].set_xlabel('Time (s)', color='#888')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(AUDIO_DIR, 'comparative_mfcc.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


# ============================================================
# VISUALIZATION 4: Chromatic Landscape
# ============================================================

def plot_chroma_comparison(analyses):
    """Chromagrams showing pitch-class distribution across pieces."""
    fig, axes = plt.subplots(5, 1, figsize=(16, 15))
    fig.suptitle('Pitch-Class Landscapes — Chromagrams',
                 fontsize=16, fontweight='bold', y=0.98, color='white')
    fig.patch.set_facecolor('#0a0a0a')

    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    for i, (piece, data) in enumerate(zip(PIECES, analyses)):
        ax = axes[i]
        ax.set_facecolor('#0a0a0a')
        librosa.display.specshow(data['chroma'], sr=data['sr'], hop_length=512,
                                 x_axis='time', y_axis='chroma', ax=ax,
                                 cmap='inferno')
        ax.set_title(f"{piece['short']} — {piece['source']}", fontsize=11,
                     color=piece['color'], fontweight='bold', pad=5)
        ax.set_ylabel('Pitch', color='#888', fontsize=9)
        ax.tick_params(colors='#888')
        if i < 4:
            ax.set_xlabel('')

    axes[-1].set_xlabel('Time (s)', color='#888')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(AUDIO_DIR, 'comparative_chroma.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


# ============================================================
# VISUALIZATION 5: Temporal Dynamics
# ============================================================

def plot_temporal_dynamics(analyses):
    """Spectral centroid + bandwidth + onset strength over time."""
    fig, axes = plt.subplots(5, 1, figsize=(16, 15))
    fig.suptitle('Temporal Dynamics — Spectral Evolution',
                 fontsize=16, fontweight='bold', y=0.98, color='white')
    fig.patch.set_facecolor('#0a0a0a')

    for i, (piece, data) in enumerate(zip(PIECES, analyses)):
        ax = axes[i]
        ax.set_facecolor('#0a0a0a')

        frames = np.arange(len(data['centroid']))
        times = librosa.frames_to_time(frames, sr=data['sr'], hop_length=512)

        # Normalize for dual-axis plotting
        c_norm = data['centroid'] / (np.max(data['centroid']) + 1e-10)
        o_norm = data['onset_env'] / (np.max(data['onset_env']) + 1e-10)

        # Onset times may be different length
        o_times = librosa.frames_to_time(np.arange(len(o_norm)), sr=data['sr'], hop_length=512)

        ax.fill_between(times, 0, c_norm, alpha=0.3, color=piece['color'], label='Centroid')
        ax.plot(o_times, o_norm * 0.8, color='#ffffff', alpha=0.5, linewidth=0.5, label='Onsets')

        # Mark beats
        if len(data['beats']) > 0:
            beat_times = librosa.frames_to_time(data['beats'], sr=data['sr'], hop_length=512)
            for bt in beat_times:
                ax.axvline(bt, color='#444', linewidth=0.3, alpha=0.5)

        ax.set_title(f"{piece['short']} — {piece['source']}  "
                     f"(tempo={data['tempo']:.0f} BPM, {data['stats']['n_beats']} beats)",
                     fontsize=11, color=piece['color'], fontweight='bold', pad=5)
        ax.set_ylabel('Intensity', color='#888', fontsize=9)
        ax.set_ylim(0, 1.05)
        ax.tick_params(colors='#888')
        if i < 4:
            ax.set_xlabel('')
        if i == 0:
            ax.legend(loc='upper right', fontsize=8, facecolor='#1a1a1a',
                      edgecolor='#333', labelcolor='#ccc')

    axes[-1].set_xlabel('Time (s)', color='#888')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = os.path.join(AUDIO_DIR, 'comparative_dynamics.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)


# ============================================================
# VISUALIZATION 6: Statistical Summary
# ============================================================

def plot_summary_table(analyses):
    """Summary statistics table with visual indicators."""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#0a0a0a')
    ax.set_facecolor('#0a0a0a')
    ax.axis('off')

    # Build summary text
    header = (f"{'Piece':>12s}  {'Source':>11s}  {'Duration':>8s}  {'Tempo':>6s}  "
              f"{'Centroid':>8s}  {'Bandwidth':>9s}  {'Flatness':>8s}  "
              f"{'Harm%':>6s}  {'Onsets/s':>8s}")

    lines = [header, '─' * len(header)]
    for piece, data in zip(PIECES, analyses):
        s = data['stats']
        line = (f"{piece['short']:>12s}  {piece['source']:>11s}  {s['duration']:7.1f}s  "
                f"{s['tempo']:5.0f}  {s['centroid_mean']:8.0f}  {s['bandwidth_mean']:9.0f}  "
                f"{s['flatness_mean']:8.4f}  {s['harmonic_ratio']*100:5.1f}  "
                f"{s['onset_density']:8.1f}")
        lines.append(line)

    txt = '\n'.join(lines)
    ax.text(0.05, 0.95, txt, transform=ax.transAxes, fontsize=11,
            va='top', fontfamily='monospace', color='#ccc',
            bbox=dict(boxstyle='round', facecolor='#1a1a1a', edgecolor='#333', alpha=0.9))

    ax.set_title('Comparative Spectral Statistics — Five Ontological Sources',
                 fontsize=14, color='white', fontweight='bold', pad=20)

    out = os.path.join(AUDIO_DIR, 'comparative_summary.png')
    plt.savefig(out, dpi=150, facecolor='#0a0a0a', bbox_inches='tight')
    plt.close()
    print(f"  Saved: {out}", flush=True)

    # Also save as text
    txt_path = os.path.join(AUDIO_DIR, 'comparative_analysis_results.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("COMPARATIVE SPECTRAL ANALYSIS — FIVE ONTOLOGICAL SOURCES\n")
        f.write("=" * 60 + "\n\n")
        f.write("Each piece derives from a different source:\n")
        f.write("  BAO  — DESI DR2 observational data (13 BAO measurements)\n")
        f.write("  Warp — RS warp factor geometry (e^{-2ky})\n")
        f.write("  Post — Phase 18A v3 MCMC posterior chains\n")
        f.write("  Mass — PDG 2024 Standard Model fermion masses\n")
        f.write("  Cell — Rule 110 cellular automaton\n\n")
        f.write(txt + "\n\n")

        f.write("DETAILED STATISTICS\n")
        f.write("-" * 40 + "\n\n")
        for piece, data in zip(PIECES, analyses):
            s = data['stats']
            f.write(f"{piece['short']} ({piece['source']}):\n")
            f.write(f"  Duration:       {s['duration']:.1f}s\n")
            f.write(f"  RMS amplitude:  {s['rms_mean']:.4f}\n")
            f.write(f"  Spectral centroid: {s['centroid_mean']:.0f} ± {s['centroid_std']:.0f} Hz\n")
            f.write(f"  Bandwidth:      {s['bandwidth_mean']:.0f} ± {s['bandwidth_std']:.0f} Hz\n")
            f.write(f"  Roll-off:       {s['rolloff_mean']:.0f} Hz\n")
            f.write(f"  Flatness:       {s['flatness_mean']:.4f} ± {s['flatness_std']:.4f}\n")
            f.write(f"  ZCR:            {s['zcr_mean']:.4f}\n")
            f.write(f"  Tempo:          {s['tempo']:.1f} BPM ({s['n_beats']} beats)\n")
            f.write(f"  Harmonic ratio: {s['harmonic_ratio']*100:.1f}%\n")
            f.write(f"  Onset density:  {s['onset_density']:.1f} onsets/s\n")
            f.write(f"  Contrast mean:  {s['contrast_mean']:.2f}\n")
            f.write(f"  MFCC[1] mean:   {s['mfcc_mean'][1]:.2f}\n")
            f.write(f"  Tonnetz mean:   [{', '.join(f'{t:.3f}' for t in s['tonnetz_mean'])}]\n")
            f.write("\n")

    print(f"  Saved: {txt_path}", flush=True)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("COMPARATIVE SPECTRAL ANALYSIS")
    print("Five Ontological Sources — One Librosa Lens")
    print("=" * 60, flush=True)

    # Verify all files exist
    for piece in PIECES:
        if not os.path.exists(piece['path']):
            print(f"  MISSING: {piece['path']}")
            return
    print("  All 5 WAV files found.\n")

    # Analyze each piece
    print("[1] Analyzing pieces...", flush=True)
    analyses = []
    for piece in PIECES:
        data = analyze_piece(piece)
        analyses.append(data)

    # Generate visualizations
    print("\n[2] Generating visualizations...", flush=True)

    print("  Plot 1: Mel spectrograms...", flush=True)
    plot_mel_comparison(analyses)

    print("  Plot 2: Spectral fingerprints...", flush=True)
    plot_fingerprint_radar(analyses)

    print("  Plot 3: Timbral DNA (MFCC)...", flush=True)
    plot_mfcc_comparison(analyses)

    print("  Plot 4: Chromagrams...", flush=True)
    plot_chroma_comparison(analyses)

    print("  Plot 5: Temporal dynamics...", flush=True)
    plot_temporal_dynamics(analyses)

    print("  Plot 6: Summary statistics...", flush=True)
    plot_summary_table(analyses)

    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"  6 visualizations + 1 text report saved to {AUDIO_DIR}")
    print(f"{'='*60}", flush=True)


if __name__ == '__main__':
    main()
