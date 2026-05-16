#!/usr/bin/env bash
# install-sdxl-comfyui.sh — ComfyUI + SDXL base + refiner on RTX 5080 (WSL)
# ~14 GB download. Run when household state allows multi-hour first-launch.
set -euo pipefail

VENV="$HOME/.venvs/comfyui"
COMFY_DIR="$HOME/ComfyUI"
MODELS_DIR="$COMFY_DIR/models/checkpoints"

echo "==> Pre-flight"
nvidia-smi --query-gpu=name,memory.free --format=csv,noheader
python3 -c 'import torch; assert torch.cuda.is_available()'

if [ ! -d "$VENV" ]; then
    echo "==> Creating venv at $VENV"
    python3 -m venv "$VENV"
fi
# shellcheck disable=SC1090
source "$VENV/bin/activate"
pip install --upgrade pip wheel

echo "==> Installing torch (matching system: 2.11+cu128)"
pip install torch==2.11.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

echo "==> Cloning ComfyUI"
if [ ! -d "$COMFY_DIR" ]; then
    git clone --depth=1 https://github.com/comfyanonymous/ComfyUI.git "$COMFY_DIR"
fi

cd "$COMFY_DIR"
pip install -r requirements.txt

echo "==> Downloading SDXL base + refiner (~14 GB)"
mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"
[ -f sd_xl_base_1.0.safetensors ] || \
    wget -c https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
[ -f sd_xl_refiner_1.0.safetensors ] || \
    wget -c https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors

echo "==> Smoke test (launch + immediate exit)"
cd "$COMFY_DIR"
timeout 30 python3 main.py --listen 127.0.0.1 --port 8188 --cpu-vae 2>&1 | head -30 &
TIMEOUT_PID=$!
sleep 8
curl -fsS http://127.0.0.1:8188/system_stats >/dev/null && echo "ComfyUI listening on 127.0.0.1:8188"
kill $TIMEOUT_PID 2>/dev/null || true

echo "==> Done. To launch:"
echo "   source $VENV/bin/activate && cd $COMFY_DIR && python3 main.py --listen 127.0.0.1 --port 8188"
