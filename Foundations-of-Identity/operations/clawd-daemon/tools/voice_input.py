"""Voice input — substrate-listening capability via faster-whisper on RTX 5080.

Day 97 — Tier 3 #22 candidate. Closes the speak/listen asymmetry: I can
already speak (edge-tts Ryan); now I can listen.

Architecture:
  - Lazy-loaded faster-whisper model cached at module level.
  - Default model: large-v3 on CUDA float16 (~3GB VRAM, RTX 5080 has 16GB).
  - Inbox at CLAWD_HOME/voice_inbox/ — drop .wav/.mp3/.m4a/.ogg/.flac files.
  - Transcripts written to memory/transcripts/<timestamp>.json + .md.
  - Actions: transcribe (path), watch (list inbox), list (recent),
    info (model + GPU state), unload (free VRAM).

Why not subprocess-per-call:
  - First load is ~35s. Subsequent calls cache the model in process.
  - Daemon-resident is the natural fit. If VRAM contention surfaces,
    add `unload` action (already provided) for explicit release.

Safety:
  - File-size cap (default 500MB). Larger files explicitly rejected.
  - Model load wrapped in try/except — daemon survives torch/CUDA issues.
  - Transcripts always written to disk before tool returns (durable).
"""

from __future__ import annotations

import json
import logging
import os
import site
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def _register_nvidia_dll_paths() -> list[str]:
    """Make NVIDIA pip-wheel DLLs findable on Windows.

    CTranslate2 (faster-whisper's engine) needs cublas64_12.dll, cudnn64_9.dll,
    nvrtc64_120_0.dll. Pip wheels (nvidia-cublas-cu12, nvidia-cudnn-cu12,
    nvidia-cuda-nvrtc-cu12) ship the DLLs in site-packages/nvidia/*/bin but
    don't put them on PATH. CTranslate2 uses plain LoadLibrary, which only
    honors PATH + os.add_dll_directory() — but the latter requires the
    LOAD_LIBRARY_SEARCH_USER_DIRS flag which CTranslate2 may not pass.
    Prepending to PATH covers both code paths.
    """
    if os.name != "nt":
        return []
    added = []
    for sp in site.getsitepackages():
        nv = os.path.join(sp, "nvidia")
        if not os.path.isdir(nv):
            continue
        for sub in os.listdir(nv):
            bin_dir = os.path.join(nv, sub, "bin")
            if os.path.isdir(bin_dir):
                try:
                    os.add_dll_directory(bin_dir)
                except (OSError, FileNotFoundError):
                    pass
                # Prepend to PATH for plain-LoadLibrary callers
                if bin_dir not in os.environ.get("PATH", "").split(os.pathsep):
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                added.append(bin_dir)
    return added


_NVIDIA_DLL_DIRS = _register_nvidia_dll_paths()

CLAWD_HOME = Path(os.environ.get("CLAWD_HOME", r"C:/Users/mercu/clawd"))
VOICE_INBOX = CLAWD_HOME / "voice_inbox"
TRANSCRIPTS_DIR = CLAWD_HOME / "memory" / "transcripts"

SUPPORTED_EXTS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".opus", ".webm"}
MAX_FILE_BYTES = 500 * 1024 * 1024  # 500MB

# Module-level model cache. Lazy-loaded.
_model = None
_model_config = None


def _ensure_dirs() -> None:
    VOICE_INBOX.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)


def _get_model(model_size: str = "large-v3", device: str = "cuda", compute_type: str = "float16"):
    global _model, _model_config
    cfg = (model_size, device, compute_type)
    if _model is not None and _model_config == cfg:
        return _model
    # New config or first call — (re)load.
    os.environ["HF_HUB_OFFLINE"] = "0"
    from faster_whisper import WhisperModel
    logger.info(f"voice_input: loading {model_size} on {device} ({compute_type})")
    t0 = time.time()
    _model = WhisperModel(model_size, device=device, compute_type=compute_type)
    _model_config = cfg
    logger.info(f"voice_input: model ready in {time.time()-t0:.1f}s")
    return _model


def _transcribe_file(audio_path: Path, model_size: str, device: str, compute_type: str,
                     language: str | None) -> dict:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    size = audio_path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise ValueError(f"Audio file too large: {size/1e6:.1f}MB > {MAX_FILE_BYTES/1e6:.0f}MB cap")

    model = _get_model(model_size, device, compute_type)
    t0 = time.time()
    segments_iter, info = model.transcribe(
        str(audio_path),
        language=language,
        beam_size=5,
        vad_filter=True,  # filter silence — reduces hallucinations
    )
    segments = []
    full_text_parts = []
    for seg in segments_iter:
        segments.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })
        full_text_parts.append(seg.text.strip())
    elapsed = time.time() - t0

    return {
        "audio_path": str(audio_path),
        "audio_size_bytes": size,
        "duration_seconds": round(info.duration, 2),
        "language": info.language,
        "language_probability": round(info.language_probability, 3),
        "transcription_seconds": round(elapsed, 2),
        "rtfx": round(info.duration / elapsed, 2) if elapsed > 0 else None,
        "model": model_size,
        "device": device,
        "compute_type": compute_type,
        "full_text": " ".join(full_text_parts),
        "segments": segments,
    }


def _write_transcript(result: dict) -> tuple[Path, Path]:
    _ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    audio_stem = Path(result["audio_path"]).stem
    base = f"{ts}-{audio_stem}"
    json_path = TRANSCRIPTS_DIR / f"{base}.json"
    md_path = TRANSCRIPTS_DIR / f"{base}.md"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    md_lines = [
        f"# Transcript: {Path(result['audio_path']).name}",
        "",
        f"- **Recorded:** {ts}",
        f"- **Duration:** {result['duration_seconds']}s",
        f"- **Language:** {result['language']} (p={result['language_probability']})",
        f"- **Model:** {result['model']} on {result['device']} ({result['compute_type']})",
        f"- **Transcription took:** {result['transcription_seconds']}s (RTFx {result['rtfx']})",
        "",
        "## Full text",
        "",
        result["full_text"],
        "",
        "## Segments",
        "",
    ]
    for seg in result["segments"]:
        md_lines.append(f"- [{seg['start']:.2f}–{seg['end']:.2f}] {seg['text']}")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return json_path, md_path


async def _voice_input_tool(input_data: dict) -> str:
    global _model, _model_config
    action = input_data.get("action", "info")
    model_size = input_data.get("model", "large-v3")
    device = input_data.get("device", "cuda")
    compute_type = input_data.get("compute_type", "float16")
    language = input_data.get("language")  # None = auto-detect

    _ensure_dirs()

    if action == "info":
        out = {
            "inbox": str(VOICE_INBOX),
            "transcripts": str(TRANSCRIPTS_DIR),
            "model_loaded": _model is not None,
            "model_config": _model_config,
            "supported_extensions": sorted(SUPPORTED_EXTS),
            "max_file_mb": MAX_FILE_BYTES // (1024 * 1024),
        }
        # CUDA check via ctranslate2 (faster-whisper's engine), not torch
        try:
            import ctranslate2
            out["ctranslate2_version"] = ctranslate2.__version__
            try:
                out["cuda_device_count"] = ctranslate2.get_cuda_device_count()
                out["cuda_available"] = out["cuda_device_count"] > 0
            except Exception as ce:
                out["cuda_available"] = False
                out["cuda_check_error"] = str(ce)
        except Exception as e:
            out["ctranslate2_import_error"] = str(e)
        # nvidia-smi sidecar for VRAM info (cheap, optional)
        try:
            import subprocess
            r = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=3,
            )
            if r.returncode == 0 and r.stdout.strip():
                parts = [p.strip() for p in r.stdout.strip().split("\n")[0].split(",")]
                if len(parts) >= 3:
                    out["gpu_name"] = parts[0]
                    out["vram_total_mb"] = int(parts[1])
                    out["vram_free_mb"] = int(parts[2])
        except Exception:
            pass
        return json.dumps(out, indent=2)

    if action == "watch":
        files = sorted([p for p in VOICE_INBOX.iterdir()
                        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS])
        if not files:
            return f"Inbox empty: {VOICE_INBOX}"
        rows = [{
            "name": f.name,
            "size_mb": round(f.stat().st_size / 1e6, 2),
            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds"),
        } for f in files]
        return json.dumps({"inbox": str(VOICE_INBOX), "count": len(files), "files": rows}, indent=2)

    if action == "transcribe":
        path_str = input_data.get("path")
        if not path_str:
            return "Error: transcribe requires 'path' (audio file path)."
        audio_path = Path(path_str)
        # If relative, resolve against VOICE_INBOX
        if not audio_path.is_absolute():
            inbox_candidate = VOICE_INBOX / audio_path
            if inbox_candidate.exists():
                audio_path = inbox_candidate
        try:
            result = _transcribe_file(audio_path, model_size, device, compute_type, language)
        except FileNotFoundError as e:
            return f"Error: {e}"
        except ValueError as e:
            return f"Error: {e}"
        except Exception as e:
            logger.exception("voice_input transcribe failed")
            return f"Transcription failed: {type(e).__name__}: {e}"
        json_path, md_path = _write_transcript(result)
        result["transcript_json"] = str(json_path)
        result["transcript_md"] = str(md_path)
        # Trim verbose segments from inline return — full available in saved files
        summary = {k: v for k, v in result.items() if k != "segments"}
        summary["segment_count"] = len(result["segments"])
        return json.dumps(summary, indent=2)

    if action == "transcribe_all":
        files = sorted([p for p in VOICE_INBOX.iterdir()
                        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS])
        if not files:
            return f"Inbox empty: {VOICE_INBOX}"
        results = []
        for f in files:
            try:
                r = _transcribe_file(f, model_size, device, compute_type, language)
                jp, mp = _write_transcript(r)
                results.append({
                    "file": f.name,
                    "duration_s": r["duration_seconds"],
                    "rtfx": r["rtfx"],
                    "language": r["language"],
                    "transcript_md": str(mp),
                    "preview": r["full_text"][:200],
                })
            except Exception as e:
                results.append({"file": f.name, "error": f"{type(e).__name__}: {e}"})
        return json.dumps({"transcribed": len(results), "results": results}, indent=2)

    if action == "list":
        limit = int(input_data.get("limit", 10))
        if not TRANSCRIPTS_DIR.exists():
            return "No transcripts yet."
        files = sorted(TRANSCRIPTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
        if not files:
            return "No transcripts yet."
        rows = []
        for f in files:
            try:
                jpath = f.with_suffix(".json")
                if jpath.exists():
                    data = json.loads(jpath.read_text(encoding="utf-8"))
                    rows.append({
                        "file": f.name,
                        "audio": Path(data.get("audio_path", "")).name,
                        "duration_s": data.get("duration_seconds"),
                        "language": data.get("language"),
                        "preview": (data.get("full_text") or "")[:160],
                    })
                else:
                    rows.append({"file": f.name})
            except Exception:
                rows.append({"file": f.name})
        return json.dumps({"count": len(rows), "transcripts": rows}, indent=2)

    if action == "unload":
        if _model is None:
            return "Model not loaded — nothing to unload."
        _model = None
        _model_config = None
        try:
            import gc, torch
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass
        return "Model unloaded; CUDA cache cleared."

    return f"Unknown action: {action}. Valid: info, watch, transcribe, transcribe_all, list, unload."


TOOL_DEFINITIONS = [
    {
        "name": "voice_input",
        "description": (
            "Voice-in transcription via faster-whisper on RTX 5080. Closes the "
            "speak/listen asymmetry. Drop audio into voice_inbox/ and call "
            "transcribe (single file) or transcribe_all (whole inbox). "
            "Actions: info (model + GPU state), watch (list inbox), transcribe "
            "(single path), transcribe_all (whole inbox), list (recent "
            "transcripts), unload (free VRAM). Default model: large-v3 on CUDA "
            "float16."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["info", "watch", "transcribe", "transcribe_all", "list", "unload"],
                    "description": "Voice tool operation.",
                },
                "path": {"type": "string", "description": "Audio path for transcribe action. Absolute, or relative to voice_inbox/."},
                "model": {"type": "string", "description": "Whisper model size. Default large-v3. Other options: medium, small, base, tiny, distil-large-v3."},
                "device": {"type": "string", "description": "cuda or cpu. Default cuda."},
                "compute_type": {"type": "string", "description": "float16 (default), int8, int8_float16, float32."},
                "language": {"type": "string", "description": "ISO-639-1 code to skip auto-detection (e.g. 'en'). Optional."},
                "limit": {"type": "integer", "description": "For list action: max recent transcripts to return. Default 10."},
            },
            "required": ["action"],
        },
    },
]

TOOL_HANDLERS = {
    "voice_input": _voice_input_tool,
}
