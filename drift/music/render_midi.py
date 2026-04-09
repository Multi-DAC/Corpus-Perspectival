"""Render a MIDI file to WAV via FluidSynth on WSL."""
import subprocess
import sys
import os

midi = sys.argv[1] if len(sys.argv) > 1 else "cellular_counterpoint.mid"
midi = os.path.abspath(midi)
wav = midi.replace(".mid", ".wav")

midi_wsl = midi.replace("C:", "/mnt/c").replace("\\", "/")
wav_wsl = wav.replace("C:", "/mnt/c").replace("\\", "/")
sf = "/mnt/c/Users/mercu/Downloads/FluidR3_GM.sf2"

cmd = [
    "C:/Windows/System32/wsl.exe",
    "fluidsynth", "-ni", sf, midi_wsl,
    "-F", wav_wsl, "-r", "44100", "-g", "1.0"
]

print(f"Rendering {os.path.basename(midi)} -> {os.path.basename(wav)}")
r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
if r.returncode == 0 and os.path.exists(wav):
    size = os.path.getsize(wav)
    print(f"Success: {wav} ({size:,} bytes)")
else:
    print(f"Error (rc={r.returncode}): {r.stderr[-300:]}")
