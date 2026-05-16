#!/usr/bin/env bash
# SDXL + ComfyUI via uv (no sudo)
set -euo pipefail

source $HOME/.local/bin/env 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"
VENV="$HOME/.venvs/comfyui"
COMFY_DIR="$HOME/ComfyUI"
MODELS_DIR="$COMFY_DIR/models/checkpoints"

echo "==> Pre-flight"
nvidia-smi --query-gpu=name,memory.free --format=csv,noheader

if [ ! -d "$VENV" ]; then
    uv venv "$VENV" --python python3.12
fi

echo "==> torch + ComfyUI requirements"
uv pip install --python "$VENV/bin/python" torch==2.11.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

if [ ! -d "$COMFY_DIR" ]; then
    git clone --depth=1 https://github.com/comfyanonymous/ComfyUI.git "$COMFY_DIR"
fi

uv pip install --python "$VENV/bin/python" -r "$COMFY_DIR/requirements.txt"

mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"

echo "==> Downloading SDXL base + refiner (~14 GB total)"
[ -f sd_xl_base_1.0.safetensors ] || \
    wget -c --progress=dot:giga https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
[ -f sd_xl_refiner_1.0.safetensors ] || \
    wget -c --progress=dot:giga https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors

echo "==> Smoke test (launch ComfyUI; query /system_stats)"
cd "$COMFY_DIR"
"$VENV/bin/python" main.py --listen 127.0.0.1 --port 8188 --cpu-vae > /home/clawd/comfyui.log 2>&1 &
COMFY_PID=$!
sleep 12
if curl -fsS http://127.0.0.1:8188/system_stats > /home/clawd/comfyui-stats.json; then
    echo "ComfyUI is up on 127.0.0.1:8188"
    cat /home/clawd/comfyui-stats.json
fi
echo "==> ComfyUI PID=$COMFY_PID; leave running or kill manually"
echo "==> Done."
