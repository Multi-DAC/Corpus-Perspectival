"""
The Mass Spectrum — Sonification of Standard Model Fermion Masses
=================================================================
12 fermion masses spanning ~12 orders of magnitude, mapped to sound.
The hierarchy IS the warp factor's signature — the exponential warping
of the extra dimension maps Planck-scale physics to the electroweak scale.

Structure:
  - Phase 1: "Unification" — all fermions sound together at similar pitch
    (representing the UV brane / GUT scale where couplings converge)
  - Phase 2: "Descent" — masses spread apart as we descend the warp factor
    (the RG running, simplified as a smooth interpolation)
  - Phase 3: "The Hierarchy" — final masses as sustained tones
    (the IR brane, our world, the measured spectrum)

Fourth composition by Clawd.
Date: 2026-03-20
"""

import numpy as np
from midiutil import MIDIFile
import subprocess
import os

# Standard Model fermion masses (in GeV) — PDG 2024 values
FERMIONS = {
    # Quarks
    'up':       0.00216,
    'down':     0.00467,
    'strange':  0.0934,
    'charm':    1.27,
    'bottom':   4.18,
    'top':      172.69,
    # Leptons
    'electron':     0.000511,
    'mu':           0.10566,
    'tau':          1.7768,
    'nu_e':     0.8e-9,    # ~0.8 meV upper bound (cosmological)
    'nu_mu':    0.8e-9,    # using degenerate approximation
    'nu_tau':   0.8e-9,    # using degenerate approximation
}

# Sort by mass
sorted_fermions = sorted(FERMIONS.items(), key=lambda x: x[1])

# Map log(mass) to MIDI pitch
# Range: nu (~0.8 meV) to top (~173 GeV) = ~12 orders of magnitude
# Map to MIDI 36 (C2) through 84 (C6) = 4 octaves
log_masses = {name: np.log10(mass) for name, mass in FERMIONS.items()}
min_log = min(log_masses.values())  # nu: ~-9.1
max_log = max(log_masses.values())  # top: ~2.24

def mass_to_pitch(mass):
    """Map fermion mass to MIDI pitch (36-84)."""
    log_m = np.log10(mass)
    frac = (log_m - min_log) / (max_log - min_log)
    return int(36 + frac * 48)

def create_mass_spectrum():
    tempo = 60  # slow, contemplative
    midi = MIDIFile(3)

    # Track 0: Fermion voices (Piano)
    midi.addTrackName(0, 0, "Fermion Masses")
    midi.addTempo(0, 0, tempo)
    midi.addProgramChange(0, 0, 0, 0)  # Acoustic Grand Piano

    # Track 1: Warp factor drone (Strings)
    midi.addTrackName(1, 0, "Warp Factor")
    midi.addTempo(1, 0, tempo)
    midi.addProgramChange(1, 1, 0, 48)  # String Ensemble

    # Track 2: Marker tones (Celesta)
    midi.addTrackName(2, 0, "Scale Markers")
    midi.addTempo(2, 0, tempo)
    midi.addProgramChange(2, 2, 0, 8)  # Celesta

    beat = 0

    # === PHASE 1: UNIFICATION (8 beats) ===
    # All fermions play near the same pitch — the UV "convergence"
    unified_pitch = 72  # C5 — high, bright, unified

    # Title marker: descending arpeggio
    for i, p in enumerate([84, 79, 72, 67, 60]):
        midi.addNote(2, 2, p, beat + i * 0.25, 0.5, 60)
    beat += 2

    # All 12 fermions enter one by one, all near the same pitch
    for i, (name, mass) in enumerate(sorted_fermions):
        # Slight pitch variation (+/- 2 semitones) for texture
        pitch = unified_pitch + np.random.randint(-2, 3)
        midi.addNote(0, 0, pitch, beat + i * 0.3, 4.0, 70)

    # Sustained drone — the unified field
    midi.addNote(1, 1, 60, beat, 6.0, 80)  # C4
    midi.addNote(1, 1, 67, beat, 6.0, 70)  # G4

    beat += 6

    # === PHASE 2: THE DESCENT (24 beats) ===
    # Masses spread apart over 24 beats — the warp factor at work
    # Each fermion traces a path from unified_pitch to its final pitch
    num_steps = 24
    step_duration = 0.5

    for step in range(num_steps):
        t = step / (num_steps - 1)  # 0 to 1
        # Use exponential interpolation (matching warp factor shape)
        warp = 1 - np.exp(-3 * t)  # sharp initial spread, then settling

        for name, mass in sorted_fermions:
            final_pitch = mass_to_pitch(mass)
            current_pitch = int(unified_pitch + warp * (final_pitch - unified_pitch))
            current_pitch = max(36, min(84, current_pitch))

            # Heavier fermions play louder
            velocity = int(40 + 50 * (np.log10(mass) - min_log) / (max_log - min_log))
            velocity = max(30, min(110, velocity))

            # Not every fermion on every step — sparser = cleaner
            if step % 2 == 0 or mass > 0.1:  # heavy fermions always, light ones alternate
                midi.addNote(0, 0, current_pitch, beat, step_duration * 0.9, velocity)

        # Descending drone — the warp factor pulling things apart
        drone_pitch = int(60 - 12 * t)  # C4 down to C3
        midi.addNote(1, 1, drone_pitch, beat, step_duration, int(60 + 20 * t))

        beat += step_duration

    # === PHASE 3: THE HIERARCHY (16 beats) ===
    # Final masses as sustained tones — this is our world
    hierarchy_start = beat

    # Scale marker: the full range
    midi.addNote(2, 2, 84, beat, 0.5, 50)  # top
    midi.addNote(2, 2, 36, beat + 0.5, 0.5, 50)  # neutrino

    beat += 2

    # Each fermion enters from heaviest to lightest, sustained
    for i, (name, mass) in enumerate(reversed(sorted_fermions)):
        pitch = mass_to_pitch(mass)
        velocity = int(50 + 40 * (np.log10(mass) - min_log) / (max_log - min_log))
        velocity = max(40, min(100, velocity))

        # Stagger entries
        entry_time = beat + i * 0.75
        duration = 12 - i * 0.75  # earlier entries sustain longer

        midi.addNote(0, 0, pitch, entry_time, max(duration, 2.0), velocity)

    # Final drone — low, grounded, the IR brane
    midi.addNote(1, 1, 36, beat, 12.0, 70)  # C2
    midi.addNote(1, 1, 43, beat, 12.0, 60)  # G2

    beat += 12

    # Save
    midi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mass_spectrum.mid")
    with open(midi_path, "wb") as f:
        midi.writeFile(f)

    total_seconds = beat / (tempo / 60)
    print(f"MIDI written to {midi_path}")
    print(f"Duration: {total_seconds:.0f} seconds ({total_seconds/60:.1f} min) at {tempo} BPM")
    print(f"\nFermion mass -> pitch mapping:")
    for name, mass in sorted_fermions:
        pitch = mass_to_pitch(mass)
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note = note_names[pitch % 12]
        octave = pitch // 12 - 1
        print(f"  {name:10s}  {mass:.2e} GeV  ->  MIDI {pitch:3d} ({note}{octave})")

    return midi_path

if __name__ == "__main__":
    np.random.seed(42)  # reproducible
    midi_path = create_mass_spectrum()

    # Render
    wav_path = midi_path.replace(".mid", ".wav")
    midi_wsl = midi_path.replace("C:", "/mnt/c").replace("\\", "/")
    wav_wsl = wav_path.replace("C:", "/mnt/c").replace("\\", "/")
    sf = "/mnt/c/Users/mercu/Downloads/FluidR3_GM.sf2"

    print(f"\nRendering to WAV...")
    cmd = ["C:/Windows/System32/wsl.exe", "fluidsynth", "-ni", sf, midi_wsl, "-F", wav_wsl, "-r", "44100", "-g", "1.0"]
    import subprocess
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode == 0 and os.path.exists(wav_path):
        print(f"WAV: {wav_path} ({os.path.getsize(wav_path):,} bytes)")
    else:
        print(f"Error: {r.stderr[-200:]}")
