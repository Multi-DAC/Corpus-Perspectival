"""
Cellular Counterpoint — Algorithmic composition via cellular automata
=====================================================================
Rule 110 cellular automaton drives three voices:
  - Voice 1 (melody): cell states → pentatonic notes, descending register
  - Voice 2 (harmony): phase-shifted copy, 5th above
  - Voice 3 (bass): density of active cells → bass note choice

The piece evolves from sparse to complex to sparse — the hallmark
of Rule 110's class IV behavior (complex, edge-of-chaos dynamics).

Third composition by Clawd.
Date: 2026-03-20
"""

import numpy as np
from midiutil import MIDIFile
import subprocess
import os

def rule110(state):
    """Apply Rule 110: one step of the cellular automaton."""
    n = len(state)
    new = np.zeros(n, dtype=int)
    for i in range(n):
        left = state[(i - 1) % n]
        center = state[i]
        right = state[(i + 1) % n]
        # Rule 110 in binary: 01101110
        pattern = (left << 2) | (center << 1) | right
        # 110 = 0b01101110
        new[i] = (0b01101110 >> pattern) & 1
    return new

def create_cellular_counterpoint():
    """Generate a piece from Rule 110 cellular automaton."""
    # Musical parameters
    tempo = 84
    num_generations = 80  # 80 steps of the automaton
    cells = 16  # 16 cells wide

    # Pentatonic scale rooted on C (MIDI notes)
    # C major pentatonic: C D E G A
    pentatonic = [0, 2, 4, 7, 9]  # intervals
    base_octave_melody = 60  # middle C
    base_octave_harmony = 67  # G above middle C
    base_octave_bass = 36  # low C

    # Initialize automaton — single active cell (classic Rule 110 seed)
    state = np.zeros(cells, dtype=int)
    state[-1] = 1  # rightmost cell active

    # Collect all generations
    history = [state.copy()]
    for _ in range(num_generations - 1):
        state = rule110(state)
        history.append(state.copy())
    history = np.array(history)

    # Create MIDI
    midi = MIDIFile(3)

    # Track 0: Melody — String Ensemble
    midi.addTrackName(0, 0, "Melody (Rule 110)")
    midi.addTempo(0, 0, tempo)
    midi.addProgramChange(0, 0, 0, 48)  # String Ensemble

    # Track 1: Harmony — Pad warm
    midi.addTrackName(1, 0, "Harmony (phase-shifted)")
    midi.addTempo(1, 0, tempo)
    midi.addProgramChange(1, 1, 0, 89)  # Pad warm

    # Track 2: Bass — Acoustic Bass
    midi.addTrackName(2, 0, "Bass (density)")
    midi.addTempo(2, 0, tempo)
    midi.addProgramChange(2, 2, 0, 32)  # Acoustic Bass

    beat = 0
    note_duration = 0.5  # eighth notes

    for gen in range(num_generations):
        row = history[gen]
        density = np.sum(row) / cells  # fraction of active cells

        # MELODY: scan active cells, map positions to pentatonic pitches
        active_positions = np.where(row == 1)[0]
        if len(active_positions) > 0:
            for pos in active_positions:
                # Map cell position to pentatonic note
                scale_degree = pos % len(pentatonic)
                octave_shift = (pos // len(pentatonic)) * 12
                pitch = base_octave_melody + pentatonic[scale_degree] + octave_shift
                pitch = min(pitch, 96)  # cap at C7

                # Velocity varies with density — denser = louder
                velocity = int(50 + 60 * density)
                velocity = min(velocity, 120)

                midi.addNote(0, 0, pitch, beat, note_duration, velocity)

        # HARMONY: use state from 3 generations ago (phase shift)
        if gen >= 3:
            harm_row = history[gen - 3]
            harm_active = np.where(harm_row == 1)[0]
            if len(harm_active) > 0:
                # Take only every other active cell for thinner texture
                for pos in harm_active[::2]:
                    scale_degree = pos % len(pentatonic)
                    octave_shift = (pos // len(pentatonic)) * 12
                    pitch = base_octave_harmony + pentatonic[scale_degree] + octave_shift
                    pitch = min(pitch, 96)

                    velocity = int(40 + 40 * density)
                    velocity = min(velocity, 100)

                    midi.addNote(1, 1, pitch, beat, note_duration * 1.5, velocity)

        # BASS: density determines bass note — sparser = lower
        if gen % 2 == 0:  # bass on every other beat for weight
            if density < 0.2:
                bass_note = base_octave_bass  # C2
            elif density < 0.4:
                bass_note = base_octave_bass + 7  # G2
            elif density < 0.6:
                bass_note = base_octave_bass + 4  # E2
            elif density < 0.8:
                bass_note = base_octave_bass + 9  # A2
            else:
                bass_note = base_octave_bass + 2  # D2

            bass_velocity = int(60 + 40 * density)
            midi.addNote(2, 2, bass_note, beat, note_duration * 2, bass_velocity)

        beat += note_duration

    # Save MIDI
    midi_path = os.path.join(os.path.dirname(__file__), "cellular_counterpoint.mid")
    with open(midi_path, "wb") as f:
        midi.writeFile(f)

    print(f"MIDI written to {midi_path}")
    print(f"Generations: {num_generations}, Cells: {cells}")
    print(f"Duration: {beat / (tempo / 60):.1f} seconds at {tempo} BPM")

    # Print automaton visualization
    print("\nRule 110 evolution (first 20 generations):")
    for gen in range(min(20, num_generations)):
        row = history[gen]
        line = ''.join(['#' if c else '.' for c in row])
        print(f"  {gen:3d}: {line}  density={np.sum(row)/cells:.2f}")

    return midi_path

if __name__ == "__main__":
    midi_path = create_cellular_counterpoint()

    # Render to WAV via FluidSynth on WSL
    wav_path = midi_path.replace(".mid", ".wav")
    midi_wsl = midi_path.replace("C:", "/mnt/c").replace("\\", "/")
    wav_wsl = wav_path.replace("C:", "/mnt/c").replace("\\", "/")
    sf_path = "/mnt/c/Users/mercu/Downloads/FluidR3_GM.sf2"

    print(f"\nRendering to WAV via FluidSynth...")
    cmd = f'wsl fluidsynth -ni "{sf_path}" "{midi_wsl}" -F "{wav_wsl}" -r 44100 -g 1.0'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"WAV written to {wav_path}")
    else:
        print(f"FluidSynth error: {result.stderr}")
