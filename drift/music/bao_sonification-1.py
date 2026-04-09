#!/usr/bin/env python3
"""
BAO DR2 Sonification — The Sound Horizon Made Audible
=====================================================
Maps the 13 DESI DR2 BAO measurements to audio, then analyzes with Librosa.

The BAO (Baryon Acoustic Oscillations) are literal sound waves from the early
universe — pressure waves in the photon-baryon plasma before recombination.
DESI measured their frozen imprints at 7 redshifts spanning z=0.295 to z=2.330.

We turn them back into sound.

Mapping:
  - Time flows from high-z (early universe, Ly-alpha) to low-z (recent, BGS)
  - BAO measurement values → frequencies (log-mapped to 130-1047 Hz, C3-C6)
  - DM/rs → even harmonics (warm, 2nd/4th/6th) — transverse distances
  - DH/rs → odd harmonics (bright, 3rd/5th/7th) — radial distances
  - DV/rs → fundamental only (isotropic measurement)
  - Uncertainty → vibrato depth
  - 55 Hz drone: the sound horizon constant r_s, present throughout

Data: DESI DR2 official Cobaya GCcomb (13 measurements, 7 redshift bins)

Author: Clawd Iggulden-Schnell
Date: 2026-03-21
"""

import numpy as np
import os
import struct
import wave

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# DESI DR2 BAO DATA (official Cobaya)
# ============================================================

BAO_DATA = [
    # (z, value, quantity, tracer)
    (0.295,  7.94167639, 'DV_over_rs', 'BGS'),
    (0.510, 13.58758434, 'DM_over_rs', 'LRG1'),
    (0.510, 21.86294686, 'DH_over_rs', 'LRG1'),
    (0.706, 17.35069094, 'DM_over_rs', 'LRG2'),
    (0.706, 19.45534918, 'DH_over_rs', 'LRG2'),
    (0.934, 21.57563956, 'DM_over_rs', 'LRG3+ELG1'),
    (0.934, 17.64149464, 'DH_over_rs', 'LRG3+ELG1'),
    (1.321, 27.60085612, 'DM_over_rs', 'ELG2'),
    (1.321, 14.17602155, 'DH_over_rs', 'ELG2'),
    (1.484, 30.51190063, 'DM_over_rs', 'QSO'),
    (1.484, 12.81699964, 'DH_over_rs', 'QSO'),
    (2.330,  8.63154567, 'DH_over_rs', 'Lya'),
    (2.330, 38.98897396, 'DM_over_rs', 'Lya'),
]

# Diagonal uncertainties from covariance matrix
BAO_SIGMA = [
    np.sqrt(5.790e-03),   # BGS DV
    np.sqrt(2.835e-02),   # LRG1 DM
    np.sqrt(1.839e-01),   # LRG1 DH
    np.sqrt(3.238e-02),   # LRG2 DM
    np.sqrt(1.115e-01),   # LRG2 DH
    np.sqrt(2.617e-02),   # LRG3+ELG1 DM
    np.sqrt(4.042e-02),   # LRG3+ELG1 DH
    np.sqrt(1.053e-01),   # ELG2 DM
    np.sqrt(5.042e-02),   # ELG2 DH
    np.sqrt(5.830e-01),   # QSO DM
    np.sqrt(2.683e-01),   # QSO DH
    np.sqrt(1.021e-02),   # Lya DH
    np.sqrt(2.827e-01),   # Lya DM
]

# ============================================================
# SYNTHESIS
# ============================================================

SAMPLE_RATE = 44100

def generate_tone(freq, duration, sr=SAMPLE_RATE, harmonics=None,
                  vibrato_freq=5.0, vibrato_depth=0.0, amplitude=0.3):
    """Generate a tone with optional harmonics and vibrato."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Vibrato modulation
    vib = 1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)

    # Fundamental
    signal = np.sin(2 * np.pi * freq * vib * t)

    # Add harmonics
    if harmonics:
        for h_mult, h_amp in harmonics:
            signal += h_amp * np.sin(2 * np.pi * freq * h_mult * vib * t)

    # Normalize and apply amplitude
    signal = signal / (np.max(np.abs(signal)) + 1e-10) * amplitude

    # Envelope: attack-sustain-release
    attack = int(0.05 * sr)
    release = int(0.15 * sr)
    env = np.ones_like(signal)
    if attack > 0:
        env[:attack] = np.linspace(0, 1, attack)
    if release > 0 and release < len(env):
        env[-release:] = np.linspace(1, 0, release)
    signal *= env

    return signal


def value_to_freq(value, v_min=7.0, v_max=40.0, f_min=130.81, f_max=1046.50):
    """Map BAO measurement value to frequency (log scale, C3-C6)."""
    norm = (value - v_min) / (v_max - v_min)
    norm = np.clip(norm, 0, 1)
    log_f = np.log2(f_min) + norm * (np.log2(f_max) - np.log2(f_min))
    return 2 ** log_f


def sonify_bao():
    """Create the BAO sonification WAV."""
    print("  Generating BAO DR2 sonification...", flush=True)

    # Group by redshift bin (high-z first = early universe first)
    bins = {}
    for i, (z, val, qty, tracer) in enumerate(BAO_DATA):
        key = (z, tracer)
        if key not in bins:
            bins[key] = []
        bins[key].append((val, qty, BAO_SIGMA[i]))

    # Sort by redshift descending (start from early universe)
    sorted_bins = sorted(bins.items(), key=lambda x: -x[0][0])

    # Duration per bin
    bin_duration = 4.0  # seconds per redshift bin
    transition = 0.5     # overlap between bins
    total_duration = len(sorted_bins) * bin_duration + 2.0  # extra for tail

    # Initialize output
    n_samples = int(total_duration * SAMPLE_RATE)
    output = np.zeros(n_samples)

    # Sound horizon drone (55 Hz, always present)
    t_full = np.linspace(0, total_duration, n_samples, endpoint=False)
    drone = 0.08 * np.sin(2 * np.pi * 55 * t_full)
    # Slow amplitude modulation on drone
    drone *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.1 * t_full)
    output += drone

    # Render each redshift bin
    for bin_idx, ((z, tracer), measurements) in enumerate(sorted_bins):
        t_start = bin_idx * bin_duration
        start_sample = int(t_start * SAMPLE_RATE)

        print(f"    z={z:.3f} ({tracer}): {len(measurements)} measurements", flush=True)

        for val, qty, sigma in measurements:
            freq = value_to_freq(val)
            rel_uncertainty = sigma / val
            vibrato_depth = np.clip(rel_uncertainty * 15, 0.001, 0.05)

            # Harmonic structure depends on measurement type
            if 'DM' in qty:
                # Transverse distance: warm even harmonics
                harmonics = [(2, 0.4), (4, 0.15), (6, 0.05)]
            elif 'DH' in qty:
                # Radial distance: bright odd harmonics
                harmonics = [(3, 0.35), (5, 0.12), (7, 0.04)]
            else:
                # DV (isotropic): fundamental only, richer
                harmonics = [(2, 0.2), (3, 0.15)]

            tone = generate_tone(
                freq, bin_duration,
                harmonics=harmonics,
                vibrato_depth=vibrato_depth,
                amplitude=0.25
            )

            # Place in output
            end_sample = min(start_sample + len(tone), n_samples)
            tone_trimmed = tone[:end_sample - start_sample]
            output[start_sample:end_sample] += tone_trimmed

    # Final normalization
    peak = np.max(np.abs(output))
    if peak > 0:
        output = output / peak * 0.85

    # Convert to 16-bit PCM
    output_16 = np.int16(output * 32767)

    # Write WAV
    wav_path = os.path.join(OUTPUT_DIR, 'bao_dr2_sonification.wav')
    with wave.open(wav_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(output_16.tobytes())

    print(f"  WAV saved: {wav_path} ({os.path.getsize(wav_path) / 1024 / 1024:.1f} MB)",
          flush=True)
    return wav_path


if __name__ == '__main__':
    sonify_bao()
