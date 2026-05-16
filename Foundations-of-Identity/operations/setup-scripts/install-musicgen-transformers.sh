#!/usr/bin/env bash
# MusicGen via transformers (no audiocraft, no apt-system deps)
set -euo pipefail

source $HOME/.local/bin/env 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"
VENV="$HOME/.venvs/musicgen"

echo "==> Installing transformers + scipy + sentencepiece"
uv pip install --python "$VENV/bin/python" transformers scipy soundfile sentencepiece numpy

echo "==> Smoke test — MusicGen Small via transformers"
"$VENV/bin/python" <<'PY'
import os, time
os.environ.setdefault("HF_HOME", os.path.expanduser("~/models/hf_cache"))
import torch
import scipy.io.wavfile
from transformers import AutoProcessor, MusicgenForConditionalGeneration

print("Loading facebook/musicgen-small...")
t0 = time.time()
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").to("cuda")
print(f"Loaded in {time.time()-t0:.1f}s. cuda available: {torch.cuda.is_available()}")

inputs = processor(text=["slow contemplative piano, late evening"], padding=True, return_tensors="pt").to("cuda")
print("Generating 5s clip...")
t0 = time.time()
audio = model.generate(**inputs, max_new_tokens=256, do_sample=True)
print(f"Generated in {time.time()-t0:.1f}s, shape={tuple(audio.shape)}")

sr = model.config.audio_encoder.sampling_rate
out = os.path.expanduser("~/musicgen-smoke-test.wav")
scipy.io.wavfile.write(out, sr, audio[0, 0].cpu().numpy())
print(f"Saved {out} (sr={sr})")
PY

echo "==> Done."
