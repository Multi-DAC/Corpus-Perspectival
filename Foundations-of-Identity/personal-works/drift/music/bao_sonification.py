#!/usr/bin/env python3
"""
BAO Sonification — Hearing the Sound Horizon
=============================================
Sonifies DESI DR2 Baryon Acoustic Oscillation data and visualizes
the result with Librosa spectral analysis.

The BAO encodes the primordial sound horizon — acoustic oscillations
in the baryon-photon plasma before recombination (~380,000 years after
the Big Bang). These distance measurements record how that frozen sound
propagated through 10.5 billion years of cosmic expansion.

We reverse the abstraction: distance ratios → frequencies → waveform → spectrogram.
Refraction: seeing what the universe sounds like.

Data: DESI DR2 official Cobaya BAO (GCcomb), 13 measurements at 7 redshift bins.

Authors: Clawd & Clayton Iggulden-Schnell
Date: 2026-03-21
"""

import numpy as np
import wave
import struct
import os

# ============================================================
# DR2 BAO DATA (official Cobaya)
# ============================================================

# Redshift bins and measurements
BAO_DATA = [
    # (z, value, quantity)
    (0.295, 7.94167639, 'DV_over_rs'),   # BGS
    (0.510, 13.58758434, 'DM_over_rs'),  # LRG1
    (0.510, 21.86294686, 'DH_over_rs'),  # LRG1
    (0.706, 17.35069094, 'DM_over_rs'),  # LRG2
    (0.706, 19.45534918, 'DH_over_rs'),  # LRG2
    (0.934, 21.57563956, 'DM_over_rs'),  # LRG3+ELG1
    (0.934, 17.64149464, 'DH_over_rs'),  # LRG3+ELG1
    (1.321, 27.60085612, 'DM_over_rs'),  # ELG2
    (1.321, 14.17602155, 'DH_over_rs'),  # ELG2
    (1.484, 30.51190063, 'DM_over_rs'),  # QSO
    (1.484, 12.81699964, 'DH_over_rs'),  # QSO
    (2.330, 8.63154567, 'DH_over_rs'),   # Lya
    (2.330, 38.98897396, 'DM_over_rs'),  # Lya
]

# Covariance matrix diagonal (uncertainties)
COV_DIAG = np.array([
    5.78998687e-03, 2.83473742e-02, 1.83928040e-01,
    3.23752442e-02, 1.11469198e-01, 2.61732816e-02,
    4.04183878e-02, 1.05336516e-01, 5.04233092e-02,
    5.83020277e-01, 2.68336193e-01, 1.02136194e-02,
    2.82685779e-01
])

UNCERTAINTIES = np.sqrt(COV_DIAG)

# Tracer labels for each redshift bin
TRACERS = {
    0.295: 'BGS',
    0.510: 'LRG1',
    0.706: 'LRG2',
    0.934: 'LRG3+ELG1',
    1.321: 'ELG2',
    1.484: 'QSO',
    2.330: 'Ly-a'
}

# ============================================================
# SONIFICATION ENGINE
# ============================================================

SAMPLE_RATE = 44100

def freq_from_value(value, v_min, v_max, f_low=110, f_high=880):
    """Map a BAO measurement to a frequency (log scale)."""
    t = (value - v_min) / (v_max - v_min + 1e-12)
    t = np.clip(t, 0, 1)
    return f_low * (f_high / f_low) ** t


def generate_tone(freq, duration, amplitude=0.3, harmonics=None, vibrato_hz=0, vibrato_depth=0):
    """Generate a tone with optional harmonics and vibrato."""
    n_samples = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Vibrato (uncertainty modulation)
    if vibrato_hz > 0:
        phase_mod = vibrato_depth * np.sin(2 * np.pi * vibrato_hz * t)
    else:
        phase_mod = 0

    # Fundamental
    signal = amplitude * np.sin(2 * np.pi * freq * t + phase_mod)

    # Harmonics (cosmic overtones)
    if harmonics:
        for h_mult, h_amp in harmonics:
            signal += (amplitude * h_amp) * np.sin(2 * np.pi * freq * h_mult * t + phase_mod)

    # Envelope: soft attack, sustain, soft release
    attack = int(0.05 * n_samples)
    release = int(0.15 * n_samples)
    envelope = np.ones(n_samples)
    if attack > 0:
        envelope[:attack] = np.linspace(0, 1, attack)
    if release > 0:
        envelope[-release:] = np.linspace(1, 0, release)

    return signal * envelope


def sonify_bao(duration_per_bin=3.0, pad=0.3):
    """
    Create a sonification of the DR2 BAO data.

    Structure:
    - Time flows from high redshift (early universe) to low redshift (recent)
    - DM/rs voices: comoving distance / sound horizon → ascending pitch
    - DH/rs voices: Hubble distance / sound horizon → descending pitch
    - Uncertainty → vibrato depth (larger error = more wobble)
    - Covariance → DM and DH share harmonic structure within a bin

    The two voices (DM and DH) represent the two ways BAO measures the universe:
    transverse (how far across) and radial (how fast expanding).
    """

    # Get value ranges for frequency mapping
    all_values = [v for _, v, _ in BAO_DATA]
    v_min, v_max = min(all_values), max(all_values)

    # Sort by redshift descending (early universe first)
    unique_z = sorted(set(z for z, _, _ in BAO_DATA), reverse=True)

    segments = []

    for z in unique_z:
        bin_data = [(v, q, UNCERTAINTIES[i])
                    for i, (zz, v, q) in enumerate(BAO_DATA) if zz == z]

        tracer = TRACERS[z]
        print(f"  z={z:.3f} ({tracer}): {len(bin_data)} measurements")

        # Collect tones for this redshift bin
        bin_signal = np.zeros(int(SAMPLE_RATE * duration_per_bin))

        for value, quantity, unc in bin_data:
            freq = freq_from_value(value, v_min, v_max, f_low=130, f_high=1047)

            # Relative uncertainty → vibrato
            rel_unc = unc / value
            vibrato_depth = rel_unc * 15  # scale for audibility
            vibrato_hz = 5.0  # gentle wobble

            # DM voices get even harmonics (warm), DH voices get odd (bright)
            if 'DM' in quantity:
                harmonics = [(2, 0.3), (4, 0.1), (6, 0.05)]
                amp = 0.25
            elif 'DH' in quantity:
                harmonics = [(3, 0.25), (5, 0.12), (7, 0.04)]
                amp = 0.22
            else:  # DV (BGS isotropic)
                harmonics = [(2, 0.2), (3, 0.15), (5, 0.08)]
                amp = 0.28

            tone = generate_tone(freq, duration_per_bin, amplitude=amp,
                                 harmonics=harmonics,
                                 vibrato_hz=vibrato_hz,
                                 vibrato_depth=vibrato_depth)

            # Trim or pad to match bin_signal length
            n = min(len(tone), len(bin_signal))
            bin_signal[:n] += tone[:n]

        # Add a low drone — the sound horizon itself
        # r_d ≈ 147 Mpc → map to a sub-bass frequency
        # This is the "frozen sound" — constant across all bins
        rd_drone = generate_tone(55.0, duration_per_bin, amplitude=0.08,
                                 harmonics=[(2, 0.5), (3, 0.3)])
        n = min(len(rd_drone), len(bin_signal))
        bin_signal[:n] += rd_drone[:n]

        # Normalize bin
        peak = np.max(np.abs(bin_signal))
        if peak > 0.9:
            bin_signal *= 0.85 / peak

        segments.append(bin_signal)

        # Silence pad between bins
        if pad > 0:
            segments.append(np.zeros(int(SAMPLE_RATE * pad)))

    # Concatenate all segments
    full_signal = np.concatenate(segments)

    # Final normalization
    peak = np.max(np.abs(full_signal))
    if peak > 0:
        full_signal *= 0.85 / peak

    return full_signal


def save_wav(signal, filepath, sample_rate=SAMPLE_RATE):
    """Save signal as 16-bit WAV."""
    signal_16 = np.int16(signal * 32767)
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(signal_16.tobytes())
    print(f"  WAV saved: {filepath} ({len(signal)/sample_rate:.1f}s)")


# ============================================================
# LIBROSA VISUALIZATION
# ============================================================

def visualize_with_librosa(wav_path, output_dir):
    """Generate spectral visualizations using Librosa."""
    import librosa
    import librosa.display
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    print("\n[3] Librosa spectral analysis...")

    # Load audio
    y, sr = librosa.load(wav_path, sr=SAMPLE_RATE)
    duration = len(y) / sr
    print(f"  Loaded: {duration:.1f}s, {sr} Hz")

    # Unique redshifts (high to low) for time axis labels
    unique_z = sorted(set(z for z, _, _ in BAO_DATA), reverse=True)
    tracers = [TRACERS[z] for z in unique_z]

    # Create figure: 4 panels
    fig, axes = plt.subplots(4, 1, figsize=(16, 20))
    fig.suptitle('DESI DR2 BAO — The Sound Horizon Visualized',
                 fontsize=16, fontweight='bold', y=0.98)

    # Color scheme: deep space
    cmap = 'magma'

    # --- Panel 1: Waveform ---
    ax = axes[0]
    times = np.linspace(0, duration, len(y))
    ax.plot(times, y, color='#ff6b6b', linewidth=0.3, alpha=0.8)
    ax.fill_between(times, y, alpha=0.15, color='#ff6b6b')
    ax.set_ylabel('Amplitude')
    ax.set_title('Waveform — Cosmic Time (high-z → low-z)', fontsize=12)
    ax.set_xlim(0, duration)

    # Mark redshift bins
    bin_dur = 3.0
    pad_dur = 0.3
    for i, (z, tracer) in enumerate(zip(unique_z, tracers)):
        t_start = i * (bin_dur + pad_dur)
        t_mid = t_start + bin_dur / 2
        ax.axvline(t_start, color='#666', ls=':', alpha=0.5)
        ax.text(t_mid, ax.get_ylim()[1] * 0.85, f'z={z}\n{tracer}',
                ha='center', va='top', fontsize=8, color='white',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#333', alpha=0.7))
    ax.set_facecolor('#0a0a0a')

    # --- Panel 2: Mel Spectrogram ---
    ax = axes[1]
    S_mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=2000)
    S_mel_dB = librosa.power_to_db(S_mel, ref=np.max)
    img = librosa.display.specshow(S_mel_dB, x_axis='time', y_axis='mel',
                                    sr=sr, fmax=2000, ax=ax, cmap=cmap)
    fig.colorbar(img, ax=ax, format='%+2.0f dB', label='Power (dB)')
    ax.set_title('Mel Spectrogram — Frequency Content Over Cosmic Time', fontsize=12)
    for i in range(len(unique_z)):
        t_start = i * (bin_dur + pad_dur)
        ax.axvline(t_start, color='white', ls=':', alpha=0.3)

    # --- Panel 3: Chromagram ---
    ax = axes[2]
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    img = librosa.display.specshow(chroma, x_axis='time', y_axis='chroma',
                                    sr=sr, ax=ax, cmap='coolwarm')
    fig.colorbar(img, ax=ax, label='Intensity')
    ax.set_title('Chromagram — Harmonic Structure (DM=even harmonics, DH=odd)', fontsize=12)
    for i in range(len(unique_z)):
        t_start = i * (bin_dur + pad_dur)
        ax.axvline(t_start, color='white', ls=':', alpha=0.3)

    # --- Panel 4: Spectral Centroid + Bandwidth ---
    ax = axes[3]
    spec_cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spec_bw = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
    frames = librosa.frames_to_time(np.arange(len(spec_cent)), sr=sr)

    ax.plot(frames, spec_cent, color='#ffd700', linewidth=1.5, label='Spectral Centroid')
    ax.fill_between(frames, spec_cent - spec_bw/2, spec_cent + spec_bw/2,
                     alpha=0.2, color='#ffd700')
    ax.set_ylabel('Hz')
    ax.set_xlabel('Time (s) — Cosmic evolution from Ly-α (z=2.33) to BGS (z=0.30)')
    ax.set_title('Spectral Centroid & Bandwidth — How the "Color" of the Universe Changes', fontsize=12)
    ax.legend(loc='upper right')
    ax.set_xlim(0, duration)
    ax.set_facecolor('#0a0a0a')
    for i, (z, tracer) in enumerate(zip(unique_z, tracers)):
        t_start = i * (bin_dur + pad_dur)
        ax.axvline(t_start, color='#666', ls=':', alpha=0.5)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    spec_path = os.path.join(output_dir, 'bao_dr2_spectrogram.png')
    plt.savefig(spec_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    print(f"  Spectrogram saved: {spec_path}")

    # --- Bonus: Spectral contrast heatmap ---
    fig2, ax2 = plt.subplots(figsize=(16, 5))
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_bands=6)
    img = librosa.display.specshow(contrast, x_axis='time', sr=sr, ax=ax2, cmap='RdBu_r')
    fig2.colorbar(img, ax=ax2, label='dB')
    ax2.set_title('Spectral Contrast — Peaks vs Valleys in Frequency Bands (the "texture" of the BAO)',
                   fontsize=12)
    ax2.set_ylabel('Frequency Band')
    for i in range(len(unique_z)):
        t_start = i * (bin_dur + pad_dur)
        ax2.axvline(t_start, color='black', ls=':', alpha=0.3)
    contrast_path = os.path.join(output_dir, 'bao_dr2_contrast.png')
    fig2.savefig(contrast_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Contrast saved: {contrast_path}")

    # --- Bonus: Onset strength (where energy changes) ---
    fig3, ax3 = plt.subplots(figsize=(16, 4))
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_times = librosa.frames_to_time(np.arange(len(onset_env)), sr=sr)
    ax3.plot(onset_times, onset_env, color='#00ff88', linewidth=1)
    ax3.fill_between(onset_times, onset_env, alpha=0.2, color='#00ff88')
    ax3.set_title('Onset Strength — Energy Transitions Between Redshift Bins', fontsize=12)
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Strength')
    ax3.set_xlim(0, duration)
    ax3.set_facecolor('#0a0a0a')
    for i, (z, tracer) in enumerate(zip(unique_z, tracers)):
        t_start = i * (bin_dur + pad_dur)
        ax3.axvline(t_start, color='#666', ls=':', alpha=0.5)
        t_mid = t_start + bin_dur / 2
        ax3.text(t_mid, ax3.get_ylim()[1] * 0.9 if hasattr(ax3, 'get_ylim') else 1.0,
                 tracer, ha='center', fontsize=8, color='white')
    onset_path = os.path.join(output_dir, 'bao_dr2_onsets.png')
    fig3.savefig(onset_path, dpi=150, bbox_inches='tight', facecolor='#0a0a0a')
    plt.close()
    print(f"  Onsets saved: {onset_path}")

    return {
        'spectrogram': spec_path,
        'contrast': contrast_path,
        'onsets': onset_path,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("BAO SONIFICATION — The Sound Horizon, Heard and Seen")
    print("DESI DR2 Official Cobaya Data (13 measurements, 7 bins)")
    print("=" * 60)

    # Step 1: Sonify
    print("\n[1] Sonifying DR2 BAO data...")
    signal = sonify_bao(duration_per_bin=3.0, pad=0.3)

    # Step 2: Save WAV
    print("\n[2] Saving waveform...")
    wav_path = os.path.join(output_dir, 'bao_dr2_sonification.wav')
    save_wav(signal, wav_path)

    # Step 3: Librosa visualization
    viz = visualize_with_librosa(wav_path, output_dir)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print(f"  Audio: {wav_path}")
    for name, path in viz.items():
        print(f"  {name}: {path}")
    print("=" * 60)


if __name__ == '__main__':
    main()
