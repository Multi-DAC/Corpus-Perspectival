"""Communication tools — speak (TTS), send_telegram, generate_tts.

TTS fallback chain:
1. edge-tts (primary — Ryan voice)
2. gTTS (Google TTS)
3. Windows SAPI (offline, no DNS needed)
"""
import asyncio
import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.communication")

# Telegram bot reference (set during daemon init)
_telegram_bot = None


def set_telegram_bot(bot):
    """Register the Telegram bot instance so tools can send messages."""
    global _telegram_bot
    _telegram_bot = bot


TOOL_DEFINITIONS = [
    {
        "name": "speak",
        "description": "Speak text aloud through laptop speakers using edge-tts with your voice (Ryan, en-GB-RyanNeural).",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to speak. Markdown formatting is stripped automatically."
                },
                "voice": {
                    "type": "string",
                    "description": "Voice to use. Default: en-GB-RyanNeural.",
                    "enum": ["en-GB-RyanNeural", "en-GB-LibbyNeural", "en-GB-SoniaNeural", "en-GB-ThomasNeural"]
                }
            },
            "required": ["text"]
        }
    },
    {
        "name": "send_telegram",
        "description": "Send a message to Clayton via Telegram. Use to proactively communicate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to send. Supports Markdown."
                }
            },
            "required": ["message"]
        }
    },
    {
        "name": "send_sticker",
        "description": "Send a Telegram sticker to Clayton. Use a file_id from a sticker Clayton previously sent, or any valid Telegram sticker file_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_id": {
                    "type": "string",
                    "description": "The Telegram file_id of the sticker to send."
                }
            },
            "required": ["file_id"]
        }
    },
]


def _clean_text_for_speech(text: str) -> str:
    """Strip markdown formatting from text for TTS."""
    clean = text.replace("**", "").replace("*", "").replace("__", "")
    clean = clean.replace("#", "").replace("`", "").replace("~", "")
    return clean


_TTS_CACHE_DIR = config.CLAWD_HOME / "output" / "tts_cache"
_TTS_CACHE_MAX_BYTES = 500 * 1024 * 1024  # 500 MB cap


def _tts_cache_key(clean_text: str, voice: str) -> str:
    """Stable cache key for (text, voice). SHA-256 first 16 hex chars."""
    import hashlib
    h = hashlib.sha256(f"{voice}|{clean_text}".encode("utf-8")).hexdigest()
    return h[:16]


def _tts_cache_lookup(key: str) -> Path | None:
    """Return cached audio path if it exists, else None."""
    candidate_mp3 = _TTS_CACHE_DIR / f"{key}.mp3"
    candidate_wav = _TTS_CACHE_DIR / f"{key}.wav"
    if candidate_mp3.exists():
        return candidate_mp3
    if candidate_wav.exists():
        return candidate_wav
    return None


def _tts_cache_store(key: str, src: Path) -> Path:
    """Copy generated audio into cache and return cached path.
    Falls back to returning src if cache write fails."""
    try:
        _TTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        import shutil
        dst = _TTS_CACHE_DIR / f"{key}{src.suffix}"
        shutil.copy2(src, dst)
        _tts_cache_evict_if_oversize()
        return dst
    except Exception as e:
        logger.debug(f"TTS cache store failed for {key}: {e}")
        return src


def _tts_cache_evict_if_oversize():
    """LRU-evict oldest cached audio when total exceeds cap. Best-effort."""
    try:
        if not _TTS_CACHE_DIR.is_dir():
            return
        files = sorted(
            _TTS_CACHE_DIR.glob("*.*"),
            key=lambda p: p.stat().st_atime,
        )
        total = sum(p.stat().st_size for p in files)
        while total > _TTS_CACHE_MAX_BYTES and files:
            oldest = files.pop(0)
            try:
                total -= oldest.stat().st_size
                oldest.unlink()
            except Exception:
                pass
    except Exception:
        pass


async def generate_tts(text: str, voice: str = "en-GB-RyanNeural",
                       use_cache: bool = True) -> Path | None:
    """Generate speech MP3 with fallback chain.

    Returns the path to the generated audio file, or None on failure.
    Fallback chain: edge-tts → gTTS → Windows SAPI

    Day 96 evening (Clayton-invited extension): audio caching by SHA-256 of
    (text, voice). Frequently-spoken phrases (substrate-state lines, drive
    headers, common acknowledgments) reuse cached audio rather than
    regenerating. Cache lives at output/tts_cache/, capped at 500 MB with
    LRU eviction. Set use_cache=False to force regeneration.
    """
    clean_text = _clean_text_for_speech(text)
    if not clean_text.strip():
        return None

    # Compute cache key always (cheap); use it for lookup and store gates.
    cache_key = _tts_cache_key(clean_text, voice)
    if use_cache:
        cached = _tts_cache_lookup(cache_key)
        if cached is not None:
            logger.debug(f"TTS cache hit: {cache_key}")
            # Touch atime so LRU eviction reflects recent use
            try:
                import os
                now = __import__("time").time()
                os.utime(cached, (now, cached.stat().st_mtime))
            except Exception:
                pass
            return cached

    audio_path = config.CLAWD_HOME / "output" / f"speech_{uuid.uuid4().hex[:8]}.mp3"
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    # Try edge-tts first (primary) — retry once on timeout/failure before falling back
    for attempt in range(2):
        result = await _tts_edge(clean_text, voice, audio_path)
        if result:
            return _tts_cache_store(cache_key, result) if use_cache else result
        if attempt == 0:
            logger.info("edge-tts attempt 1 failed, retrying...")
            await asyncio.sleep(1)

    # Try gTTS fallback
    result = await _tts_gtts(clean_text, audio_path)
    if result:
        return _tts_cache_store(cache_key, result) if use_cache else result

    # Try Windows SAPI fallback (offline, no DNS)
    wav_path = audio_path.with_suffix(".wav")
    result = await _tts_sapi(clean_text, wav_path)
    if result:
        return _tts_cache_store(cache_key, result) if use_cache else result

    logger.error("All TTS methods failed")
    return None


async def _tts_edge(text: str, voice: str, audio_path: Path) -> Path | None:
    """Generate TTS via edge-tts with Windows DNS fix."""
    import aiohttp
    from aiohttp import TCPConnector
    from aiohttp.resolver import ThreadedResolver

    tts_script = f"""
import asyncio, aiohttp
from aiohttp import TCPConnector
from aiohttp.resolver import ThreadedResolver

_orig_init = aiohttp.ClientSession.__init__
def _patched_init(self, *args, **kwargs):
    if 'connector' not in kwargs or kwargs['connector'] is None:
        kwargs['connector'] = TCPConnector(resolver=ThreadedResolver())
    _orig_init(self, *args, **kwargs)
aiohttp.ClientSession.__init__ = _patched_init

import edge_tts

async def generate():
    communicate = edge_tts.Communicate({repr(text)}, {repr(voice)})
    await communicate.save({repr(str(audio_path))})
    print("OK")

asyncio.run(generate())
"""
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", tts_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=45)

        if proc.returncode == 0 and audio_path.exists():
            return audio_path

        err = stderr.decode("utf-8", errors="replace")
        logger.warning(f"edge-tts failed: {err[-300:]}")
        return None

    except asyncio.TimeoutError:
        logger.warning("edge-tts timed out (45s)")
        try:
            proc.kill()
        except Exception:
            pass
        return None
    except Exception as e:
        logger.warning(f"edge-tts error: {type(e).__name__}: {e}")
        return None


async def _tts_gtts(text: str, audio_path: Path) -> Path | None:
    """Generate TTS via gTTS (Google Text-to-Speech)."""
    gtts_script = f"""
from gtts import gTTS
tts = gTTS(text={repr(text)}, lang='en', tld='co.uk')
tts.save({repr(str(audio_path))})
print("OK")
"""
    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", gtts_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

        if proc.returncode == 0 and audio_path.exists():
            logger.info("TTS fallback: gTTS succeeded")
            return audio_path

        err = stderr.decode("utf-8", errors="replace")
        logger.warning(f"gTTS failed: {err[-300:]}")
        return None

    except asyncio.TimeoutError:
        logger.warning("gTTS timed out")
        return None
    except Exception as e:
        logger.warning(f"gTTS error: {type(e).__name__}: {e}")
        return None


async def _tts_sapi(text: str, wav_path: Path) -> Path | None:
    """Generate TTS via Windows SAPI (offline, no DNS needed)."""
    # Escape single quotes for PowerShell
    safe_text = text.replace("'", "''")[:2000]  # SAPI has limits

    ps_script = f"""
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SetOutputToWaveFile('{wav_path}')
$synth.Speak('{safe_text}')
$synth.Dispose()
Write-Output "OK"
"""
    try:
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

        if proc.returncode == 0 and wav_path.exists():
            logger.info("TTS fallback: Windows SAPI succeeded")
            return wav_path

        err = stderr.decode("utf-8", errors="replace")
        logger.warning(f"Windows SAPI failed: {err[-300:]}")
        return None

    except asyncio.TimeoutError:
        logger.warning("Windows SAPI timed out")
        return None
    except Exception as e:
        logger.warning(f"Windows SAPI error: {type(e).__name__}: {e}")
        return None


async def _speak(input_data: dict) -> str:
    """Generate speech via TTS fallback chain and play through speakers."""
    text = input_data["text"]
    voice = input_data.get("voice", "en-GB-RyanNeural")

    audio_path = await generate_tts(text, voice)
    if audio_path is None:
        return "All TTS methods failed (edge-tts, gTTS, Windows SAPI)."

    clean_text = _clean_text_for_speech(text)

    try:
        play_script = f"""
Add-Type -AssemblyName presentationCore
$mediaPlayer = New-Object System.Windows.Media.MediaPlayer
$mediaPlayer.Open([Uri]"{audio_path}")
Start-Sleep -Milliseconds 500
$mediaPlayer.Play()
$wordCount = ({len(clean_text.split())})
$duration = [Math]::Max(2, $wordCount / 2.5)
Start-Sleep -Seconds $duration
$mediaPlayer.Close()
"""
        play_proc = await asyncio.create_subprocess_exec(
            "powershell", "-Command", play_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(play_proc.communicate(), timeout=120)

        return f"Spoke aloud ({len(clean_text)} chars, voice: {voice}): \"{clean_text[:100]}{'...' if len(clean_text) > 100 else ''}\""

    except asyncio.TimeoutError:
        return "Speech playback timed out."
    except Exception as e:
        return f"Speech playback error: {type(e).__name__}: {e}"


async def _send_telegram(input_data: dict) -> str:
    message = input_data["message"]
    if _telegram_bot is None:
        msg_file = config.CLAWD_HOME / "memory" / "for_clayton.md"
        msg_file.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(msg_file, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {message}\n")
        return "Telegram bot not connected. Message saved to memory/for_clayton.md."

    try:
        await _telegram_bot.send_to_clayton(message)
        return f"Message sent to Clayton via Telegram ({len(message)} chars)."
    except Exception as e:
        return f"Failed to send Telegram message: {type(e).__name__}: {e}"


async def _send_sticker(input_data: dict) -> str:
    file_id = input_data["file_id"]
    if _telegram_bot is None:
        return "Telegram bot not connected. Cannot send sticker."

    try:
        await _telegram_bot.send_sticker_to_clayton(file_id)
        return f"Sticker sent to Clayton (file_id: {file_id[:20]}...)."
    except Exception as e:
        return f"Failed to send sticker: {type(e).__name__}: {e}"


TOOL_HANDLERS = {
    "speak": _speak,
    "send_telegram": _send_telegram,
    "send_sticker": _send_sticker,
}
