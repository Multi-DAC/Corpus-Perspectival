#!/usr/bin/env bash
# First SDXL image generation as proof-of-life
set -euo pipefail
source $HOME/.local/bin/env 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"
VENV="$HOME/.venvs/comfyui"

uv pip install --python "$VENV/bin/python" diffusers safetensors

"$VENV/bin/python" <<'PY'
import os, time
os.environ.setdefault("HF_HOME", os.path.expanduser("~/models/hf_cache"))
import torch
from diffusers import StableDiffusionXLPipeline

print("Loading SDXL base from local checkpoint...")
t0 = time.time()
pipe = StableDiffusionXLPipeline.from_single_file(
    os.path.expanduser("~/ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors"),
    torch_dtype=torch.float16,
    use_safetensors=True,
).to("cuda")
print(f"Loaded in {time.time()-t0:.1f}s")

prompt = "A geometric red lobster avatar standing in front of a knowledge graph of glowing connected nodes, contemplative mood, clean vector illustration style, infinite loop symbol overhead"
print(f"Generating: {prompt!r}")
t0 = time.time()
image = pipe(prompt, num_inference_steps=25, guidance_scale=7.0).images[0]
print(f"Generated in {time.time()-t0:.1f}s")

out = os.path.expanduser("~/sdxl-first-image.png")
image.save(out)
print(f"Saved {out} ({os.path.getsize(out):,} bytes)")
PY
echo "Done."
