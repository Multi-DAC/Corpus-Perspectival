#!/usr/bin/env python3
"""
The Warp Factor — Sonified
===========================
First piece of music by Clawd.

The warp factor A(y) = -ky defines how gravity weakens as you move
through the extra dimension from the UV brane (y=0) to the IR brane
(y=yc). This is the sound of that journey.

UV brane: high pitch, dense harmonics — gravity is strong, all forces unified
IR brane: low pitch, sparse — gravity has weakened by 10^34, the hierarchy exists

The cuscuton field ζ₀ provides a sustained bass drone — the constraint
that holds the geometry together.

Authors: Clawd
Date: 2026-03-20
"""

from midiutil import MIDIFile
import math
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def warp_factor_value(y, k=1.0, yc=39.56):
    """The RS warp factor: e^{-2ky}. Returns the suppression."""
    return math.exp(-2 * k * y / yc)  # Normalized so y ∈ [0, yc] maps to [1, e^{-2kyc}]

def create_warp_factor_piece():
    """
    Compose a MIDI piece representing the journey through the extra dimension.

    Track 0: The Warp Factor — descending pitch representing e^{-ky}
    Track 1: Cuscuton Drone — sustained bass, the constraint field
    Track 2: Harmonics — overtones that thin out as you approach the IR brane
    Track 3: Heartbeat — regular pulse, the self-tuning mechanism breathing
    """

    midi = MIDIFile(4)  # 4 tracks
    tempo = 72  # BPM — contemplative
    duration_beats = 64  # ~53 seconds at 72 BPM

    # Track names
    midi.addTrackName(0, 0, "Warp Factor")
    midi.addTrackName(1, 0, "Cuscuton Drone")
    midi.addTrackName(2, 0, "Harmonics")
    midi.addTrackName(3, 0, "Heartbeat")

    midi.addTempo(0, 0, tempo)

    # ============================================================
    # Track 0: The Warp Factor
    # Journey from UV brane (high) to IR brane (low)
    # Pitch maps exponentially: MIDI 84 (C6) → MIDI 36 (C2)
    # ============================================================
    channel_warp = 0
    midi.addProgramChange(0, channel_warp, 0, 48)  # String Ensemble

    num_notes = 32
    note_duration = duration_beats / num_notes  # 2 beats each

    for i in range(num_notes):
        y_frac = i / (num_notes - 1)  # 0 to 1 through extra dimension
        warp = warp_factor_value(y_frac * 39.56)

        # Map warp factor to pitch: log scale
        # At UV (warp=1): pitch=84 (C6)
        # At IR (warp→0): pitch=36 (C2)
        pitch = int(36 + 48 * math.log(warp + 1e-10) / math.log(1e-10) * -1)
        pitch = max(36, min(84, int(36 + 48 * warp)))

        # Velocity decreases as we descend — gravity weakening
        velocity = int(40 + 70 * warp)
        velocity = max(30, min(110, velocity))

        beat = i * note_duration
        midi.addNote(0, channel_warp, pitch, beat, note_duration * 0.9, velocity)

    # ============================================================
    # Track 1: Cuscuton Drone
    # Sustained bass — the constraint field that holds geometry together
    # Constant because the cuscuton is algebraically determined, not dynamic
    # ============================================================
    channel_drone = 1
    midi.addProgramChange(1, channel_drone, 0, 89)  # Pad (warm)

    # Low C and G drone, sustained throughout
    for beat in range(0, duration_beats, 8):
        dur = min(8.5, duration_beats - beat)  # Slightly overlapping for continuity
        midi.addNote(1, channel_drone, 36, beat, dur, 50)  # C2
        midi.addNote(1, channel_drone, 43, beat, dur, 40)  # G2 (perfect fifth)

    # ============================================================
    # Track 2: Harmonics
    # Overtones that thin out as you approach the IR brane
    # UV brane: rich harmonics (all forces unified)
    # IR brane: sparse (only gravity's echo remains)
    # ============================================================
    channel_harm = 2
    midi.addProgramChange(2, channel_harm, 0, 88)  # Pad (new age)

    harmonic_pitches = [60, 64, 67, 72, 76, 79, 84]  # C major across octaves
    for i in range(num_notes):
        y_frac = i / (num_notes - 1)
        beat = i * note_duration

        # Number of active harmonics decreases with y
        n_harmonics = max(1, int(len(harmonic_pitches) * (1 - y_frac * 0.85)))

        for h in range(n_harmonics):
            vel = int(25 + 30 * (1 - y_frac) * (1 - h / len(harmonic_pitches)))
            vel = max(15, min(80, vel))
            midi.addNote(2, channel_harm, harmonic_pitches[h], beat,
                        note_duration * 0.7, vel)

    # ============================================================
    # Track 3: Heartbeat
    # Regular pulse — the self-tuning mechanism
    # Steady regardless of where you are in the extra dimension
    # Because self-tuning holds to 15 significant figures across 60 orders
    # ============================================================
    channel_hb = 3
    midi.addProgramChange(3, channel_hb, 0, 117)  # Melodic Tom

    for beat in range(0, duration_beats, 2):
        # Strong beat
        midi.addNote(3, channel_hb, 48, beat, 0.3, 60)
        # Weak echo
        midi.addNote(3, channel_hb, 48, beat + 1, 0.2, 35)

    # ============================================================
    # Save
    # ============================================================
    outpath = os.path.join(OUTPUT_DIR, "the_warp_factor.mid")
    with open(outpath, 'wb') as f:
        midi.writeFile(f)
    print(f"MIDI saved: {outpath}")
    print(f"Duration: ~{duration_beats * 60 / tempo:.0f} seconds at {tempo} BPM")
    print(f"Tracks: Warp Factor, Cuscuton Drone, Harmonics, Heartbeat")
    return outpath


if __name__ == '__main__':
    path = create_warp_factor_piece()
    print(f"\nTo render with FluidSynth (in WSL2):")
    wsl_path = path.replace('C:\\Users\\mercu', '/mnt/c/Users/mercu').replace('\\', '/')
    print(f"  fluidsynth -ni <soundfont.sf2> {wsl_path} -F output.wav -r 44100")
