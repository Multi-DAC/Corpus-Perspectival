#!/usr/bin/env bash
# install-musicgen.sh — audiocraft + MusicGen Medium (1.5B) on RTX 5080 (WSL)
# ~6 GB download. For Drift-essay sonification + procedural music generation.
set -euo pipefail

VENV="$HOME/.venvs/musicgen"

echo "==> Pre-flight"
nvidia-smi --query-gpu=name,memory.free --format=csv,noheader

if [ ! -d "$VENV" ]; then
    echo "==> Creating venv at $VENV"
    python3 -m venv "$VENV"
fi
# shellcheck disable=SC1090
source "$VENV/bin/activate"
pip install --upgrade pip wheel

echo "==> Installing torch + audiocraft"
pip install torch==2.11.0 torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install audiocraft

echo "==> Smoke test (5s generation, cold-load downloads model)"
python3 <<'PY'
import os, time
os.environ.setdefault("AUDIOCRAFT_CACHE_DIR", os.path.expanduser("~/models/audiocraft"))
import torch
from audiocraft.models import MusicGen
import torchaudio

print("Loading MusicGen Medium (downloads ~3 GB on first run)...")
t0 = time.time()
model = MusicGen.get_pretrained("facebook/musicgen-medium")
model.set_generation_params(duration=5)
print(f"Loaded in {time.time()-t0:.1f}s")

print("Generating 5s clip: 'slow contemplative piano, late evening'")
t0 = time.time()
wav = model.generate(["slow contemplative piano, late evening"])
print(f"Generated in {time.time()-t0:.1f}s, shape={wav.shape}")

out = os.path.expanduser("~/musicgen-smoke-test.wav")
torchaudio.save(out, wav[0].cpu(), model.sample_rate)
print(f"Saved {out}")
PY

echo "==> Done. Wire into daemon at tools/musicgen.py for generation tool."
