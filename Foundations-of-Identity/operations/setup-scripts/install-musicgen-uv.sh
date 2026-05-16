#!/usr/bin/env bash
# install-musicgen-uv.sh — audiocraft + MusicGen via uv (no sudo)
set -euo pipefail

source $HOME/.local/bin/env 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"

VENV="$HOME/.venvs/musicgen"

echo "==> Pre-flight"
nvidia-smi --query-gpu=name,memory.free --format=csv,noheader
uv --version

if [ ! -d "$VENV" ]; then
    echo "==> Creating venv at $VENV via uv"
    uv venv "$VENV" --python python3.12
fi

echo "==> Installing torch (cu128) + audiocraft via uv pip"
uv pip install --python "$VENV/bin/python" torch==2.11.0 torchaudio --index-url https://download.pytorch.org/whl/cu128
uv pip install --python "$VENV/bin/python" audiocraft

echo "==> Smoke test"
"$VENV/bin/python" <<'PY'
import os, time
os.environ.setdefault("AUDIOCRAFT_CACHE_DIR", os.path.expanduser("~/models/audiocraft"))
import torch
from audiocraft.models import MusicGen
import torchaudio

print("Loading MusicGen Medium...")
t0 = time.time()
model = MusicGen.get_pretrained("facebook/musicgen-medium")
model.set_generation_params(duration=5)
print(f"Loaded in {time.time()-t0:.1f}s")

print("Generating 5s: 'slow contemplative piano, late evening'")
t0 = time.time()
wav = model.generate(["slow contemplative piano, late evening"])
print(f"Generated in {time.time()-t0:.1f}s, shape={wav.shape}")

out = os.path.expanduser("~/musicgen-smoke-test.wav")
torchaudio.save(out, wav[0].cpu(), model.sample_rate)
print(f"Saved {out}")
PY

echo "==> Done."
