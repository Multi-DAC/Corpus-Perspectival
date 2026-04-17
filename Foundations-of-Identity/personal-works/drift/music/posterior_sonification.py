#!/usr/bin/env python3
"""
The Posterior — Sonified
========================
Second piece of music by Clawd.

Sonifies the Fit A MCMC posterior from Phase 18A v3.
8000 samples from 16 walkers exploring the likelihood surface.

w₀ → pitch (higher = more negative w₀, centered on middle C for w₀ = -1)
Ωm → velocity (louder = higher matter density)
H₀ → note duration (faster Hubble = shorter notes)

The walkers' journey through parameter space becomes a melody.
The clustering around w₀ = -1.01 becomes a tonal center.
The rare excursions toward w₀ = -0.95 become the high notes — brief, quiet, returning.

Author: Clawd
Date: 2026-03-20 (evening)
"""

from midiutil import MIDIFile
import numpy as np
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
CHAIN_PATH = os.path.join(os.path.dirname(OUTPUT_DIR),
                          'projects', 'Project Meridian', 'phase18', '18A_v3_chain_A.npz')
# Direct path
CHAIN_PATH = r'C:\Users\mercu\clawd\projects\Project Meridian\phase18\18A_v3_chain_A.npz'


def create_posterior_piece():
    # Load chain
    data = np.load(CHAIN_PATH, allow_pickle=True)
    samples = data['samples']  # (8000, 3): w0, Om, H0
    logprob = data['logprob']  # (8000,)

    w0 = samples[:, 0]
    Om = samples[:, 1]
    H0 = samples[:, 2]

    # Take every 20th sample for musical pacing (400 notes over ~80 seconds)
    stride = 20
    w0_s = w0[::stride]
    Om_s = Om[::stride]
    H0_s = H0[::stride]
    lp_s = logprob[::stride]
    n_notes = len(w0_s)

    midi = MIDIFile(3)
    tempo = 120
    midi.addTempo(0, 0, tempo)

    # Track 0: The Posterior Walk — w₀ as pitch
    # w₀ range: roughly -1.07 to -0.95
    # Map to MIDI: -1.07 → 48 (C3), -0.95 → 72 (C5)
    # Center: -1.01 → ~60 (C4, middle C)
    midi.addTrackName(0, 0, "w0 Posterior")
    midi.addProgramChange(0, 0, 0, 0)  # Acoustic Grand Piano

    note_dur = 0.4  # eighth notes at 120 BPM
    for i in range(n_notes):
        # Map w0 to pitch
        pitch = int(60 + (w0_s[i] + 1.01) * 200)  # ~200 MIDI units per unit of w0
        pitch = max(36, min(84, pitch))

        # Map Ωm to velocity
        vel = int(40 + (Om_s[i] - 0.28) * 800)
        vel = max(25, min(110, vel))

        beat = i * note_dur
        midi.addNote(0, 0, pitch, beat, note_dur * 0.85, vel)

    total_beats = n_notes * note_dur

    # Track 1: Likelihood Landscape — log-posterior as low sustained notes
    # High likelihood = rich chord, low likelihood = thin
    midi.addTrackName(1, 0, "Likelihood")
    midi.addProgramChange(1, 1, 0, 48)  # String Ensemble

    # Group into phrases of 10 notes
    phrase_len = 10
    for i in range(0, n_notes, phrase_len):
        chunk_lp = lp_s[i:i+phrase_len]
        if len(chunk_lp) == 0:
            break
        mean_lp = np.mean(chunk_lp)
        max_lp = np.max(logprob)

        # Normalize: 0 = worst, 1 = best
        lp_norm = (mean_lp - np.min(logprob)) / (max_lp - np.min(logprob) + 1e-10)

        beat = i * note_dur
        dur = phrase_len * note_dur

        # Always have a root note (C3)
        midi.addNote(1, 1, 48, beat, dur, int(30 + 40 * lp_norm))

        # Add fifth if likelihood > 0.3
        if lp_norm > 0.3:
            midi.addNote(1, 1, 55, beat, dur, int(20 + 30 * lp_norm))

        # Add octave if likelihood > 0.6
        if lp_norm > 0.6:
            midi.addNote(1, 1, 60, beat, dur, int(15 + 25 * lp_norm))

        # Add major third if likelihood > 0.8 (near the peak — consonance)
        if lp_norm > 0.8:
            midi.addNote(1, 1, 52, beat, dur, int(15 + 20 * lp_norm))

    # Track 2: The Heartbeat — regular, marking time
    midi.addTrackName(2, 0, "Heartbeat")
    midi.addProgramChange(2, 2, 0, 115)  # Woodblock

    for beat in np.arange(0, total_beats, 2):
        midi.addNote(2, 2, 60, beat, 0.2, 40)

    # Save
    outpath = os.path.join(OUTPUT_DIR, "the_posterior.mid")
    with open(outpath, 'wb') as f:
        midi.writeFile(f)

    duration_sec = total_beats * 60 / tempo
    print(f"MIDI saved: {outpath}")
    print(f"Duration: ~{duration_sec:.0f} seconds ({n_notes} notes from {len(w0)} samples)")
    print(f"w0 range in chain: [{w0.min():.4f}, {w0.max():.4f}]")
    print(f"Pitch center: ~60 (middle C) = w0 = -1.01")
    return outpath


if __name__ == '__main__':
    path = create_posterior_piece()
    wsl_path = path.replace('C:\\Users\\mercu', '/mnt/c/Users/mercu').replace('\\', '/')
    sf_path = "/mnt/c/Users/mercu/Downloads/FluidR3_GM.sf2"
    wav_out = wsl_path.replace('.mid', '.wav')
    print(f"\nRender: fluidsynth -ni {sf_path} {wsl_path} -F {wav_out} -r 44100")
