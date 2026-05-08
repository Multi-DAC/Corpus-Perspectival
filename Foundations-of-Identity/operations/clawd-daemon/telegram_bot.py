"""
Telegram Bot — Clayton's interface for communicating with Clawd.
Handles incoming messages, authorization, and relaying responses.
Includes retry logic for start failures (network down at boot).
"""
import asyncio
import logging
import tempfile
from datetime import datetime
from pathlib import Path

import aiohttp
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import avatar
import config
from memory import log_session_event
from tools import generate_tts

logger = logging.getLogger("clawd.telegram")


class ClawdTelegramBot:
    # How long to wait for follow-up messages before processing (seconds).
    # Telegram splits long messages at ~4096 chars; parts arrive within ~1s.
    MESSAGE_DEBOUNCE_SECONDS = 1.5

    def __init__(self, router):
        self.router = router
        self.app: Application | None = None
        self.bot: Bot | None = None
        self._clayton_chat_id: int | None = None
        self._heartbeat = None  # Set via set_heartbeat() for activity tracking
        self._health_checker = None  # Set via set_health_checker()
        # Message debounce: buffer rapid-fire messages (e.g. Telegram split)
        self._msg_buffer: dict[int, list[str]] = {}        # chat_id → [texts]
        self._msg_updates: dict[int, Update] = {}           # chat_id → latest Update
        self._msg_debounce_task: dict[int, asyncio.Task] = {}  # chat_id → pending timer
        self._msg_locks: dict[int, asyncio.Lock] = {}      # per-chat lock for buffer ops

    def set_heartbeat(self, heartbeat):
        """Register heartbeat instance for user activity notifications."""
        self._heartbeat = heartbeat

    def set_health_checker(self, health_checker):
        """Register health checker for /health command."""
        self._health_checker = health_checker

    async def send_voice_to_clayton(self, audio_path):
        """Send a voice message to Clayton and clean up the temp file."""
        chat_id = self._clayton_chat_id
        if not self.bot or not chat_id:
            return
        try:
            with open(audio_path, "rb") as f:
                await self.bot.send_voice(chat_id=chat_id, voice=f)
        except Exception as e:
            logger.error(f"Failed to send voice message: {e}")
        finally:
            try:
                audio_path.unlink(missing_ok=True)
            except Exception as e:
                logger.debug(f"Failed to remove temporary audio file: {e}")

    async def send_sticker_to_clayton(self, sticker_file_id: str):
        """Send a sticker to Clayton by file_id."""
        chat_id = self._clayton_chat_id
        if not self.bot or not chat_id:
            return
        try:
            await self.bot.send_sticker(chat_id=chat_id, sticker=sticker_file_id)
        except Exception as e:
            logger.error(f"Failed to send sticker: {e}")

    async def start(self):
        if not config.TELEGRAM_BOT_TOKEN:
            logger.warning("No Telegram bot token configured — Telegram disabled.")
            return

        self.app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

        # Register handlers
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("status", self._cmd_status))
        self.app.add_handler(CommandHandler("model", self._cmd_model))
        self.app.add_handler(CommandHandler("handoff", self._cmd_handoff))
        self.app.add_handler(CommandHandler("reset", self._cmd_reset))
        self.app.add_handler(CommandHandler("health", self._cmd_health))
        self.app.add_handler(CommandHandler("resume", self._cmd_resume))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        self.app.add_handler(MessageHandler(filters.PHOTO, self._handle_photo))
        self.app.add_handler(MessageHandler(filters.Document.ALL, self._handle_document))
        self.app.add_handler(MessageHandler(filters.Sticker.ALL, self._handle_sticker))
        self.app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self._handle_voice))

        # Initialize and start polling with retry on failure
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                await self.app.initialize()
                await self.app.start()
                await self.app.updater.start_polling(drop_pending_updates=True)
                self.bot = self.app.bot
                logger.info("Telegram bot started and polling.")
                return
            except Exception as e:
                if attempt >= max_retries:
                    logger.error(f"Telegram bot failed to start after {max_retries} attempts: {e}")
                    raise
                delay = min(5 * (2 ** (attempt - 1)), 60)  # 5s, 10s, 20s, 40s, 60s
                logger.warning(f"Telegram start attempt {attempt}/{max_retries} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)

    async def stop(self):
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            logger.info("Telegram bot stopped.")

    def _is_authorized(self, user_id: int) -> bool:
        return user_id in config.TELEGRAM_AUTHORIZED_USERS

    async def send_to_clayton(self, text: str):
        """Send a message to Clayton proactively."""
        if not self.bot or not self._clayton_chat_id:
            # Use first authorized user as fallback
            if config.TELEGRAM_AUTHORIZED_USERS:
                self._clayton_chat_id = config.TELEGRAM_AUTHORIZED_USERS[0]
            else:
                logger.warning("No chat ID for Clayton — can't send proactive message.")
                return
        sent = False
        try:
            # Split long messages (Telegram limit is 4096 chars)
            for chunk in _split_message(text):
                await self.bot.send_message(
                    chat_id=self._clayton_chat_id,
                    text=chunk,
                    parse_mode="Markdown",
                )
            sent = True
        except Exception as e:
            logger.error(f"Failed to send to Clayton: {e}")
            # Retry without markdown if parsing fails
            try:
                for chunk in _split_message(text):
                    await self.bot.send_message(
                        chat_id=self._clayton_chat_id,
                        text=chunk,
                    )
                sent = True
            except Exception as e2:
                logger.error(f"Failed to send (retry): {e2}")

        # Send voice message only if text was delivered
        if sent:
            try:
                audio_path = await generate_tts(text)
                if audio_path:
                    await self.send_voice_to_clayton(audio_path)
            except Exception as e:
                logger.error(f"TTS/voice send failed: {e}")

    # ============================================================
    # Command Handlers
    # ============================================================

    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("Unauthorized.")
            return
        self._clayton_chat_id = update.effective_chat.id
        await update.message.reply_text(
            "Clawd is online.\n\n"
            f"Model: {self.router.active_model}\n"
            f"Session: {self.router.session_id or 'new'}\n\n"
            "Commands:\n"
            "/status — Current state\n"
            "/health — Subsystem health status\n"
            "/model <name> — Switch model (opus, sonnet, gemini, gemini-pro)\n"
            "/handoff — Trigger handoff protocol\n"
            "/reset — Reset conversation context\n\n"
            "Just send a message to talk to Clawd."
        )

    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        if self.router.active_model == "opus":
            pressure = self.router.context_pressure()
            bar = "█" * int(pressure * 20) + "░" * (20 - int(pressure * 20))
            await update.message.reply_text(
                f"*Clawd Status*\n\n"
                f"Model: `opus` (Claude Code CLI)\n"
                f"Session: `{self.router.session_id or 'none'}`\n"
                f"Turns: {self.router.session_turns}/{config.CLAUDE_CODE_MAX_TURNS}\n"
                f"Pressure: [{bar}] {pressure:.0%}\n"
                f"Session cost: ${self.router.session_cost:.4f}\n"
                f"Needs handoff: {'⚠️ YES' if self.router.needs_handoff() else '✅ No'}",
                parse_mode="Markdown"
            )

    async def _cmd_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        args = context.args
        valid_models = {"opus", "sonnet"} | set(config.GEMINI_MODELS.keys())
        if not args or args[0] not in valid_models:
            models_list = ", ".join(sorted(valid_models))
            await update.message.reply_text(
                f"Current model: {self.router.active_model}\n"
                f"Usage: /model <name>\n"
                f"Available: {models_list}"
            )
            return
        old = self.router.active_model
        self.router.switch_model(args[0])
        await update.message.reply_text(f"Switched: {old} → {args[0]}")

    async def _cmd_handoff(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        await update.message.reply_text("Triggering handoff protocol...")
        from memory import trigger_handoff, write_claude_md
        result = await trigger_handoff(self.router)
        self.router.reset_conversation()
        write_claude_md()
        await update.message.reply_text(f"Handoff complete. Context reset.\n\nHandoff summary:\n{result[:2000]}")

    async def _cmd_reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        from memory import write_claude_md
        self.router.reset_conversation()
        write_claude_md()
        await update.message.reply_text("Context reset. Identity files reloaded.")

    async def _cmd_health(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            return
        if not self._health_checker:
            await update.message.reply_text("Health checker not initialized.")
            return
        await update.message.reply_text("Running health checks...")
        report = await self._health_checker.run_check_now()
        try:
            await update.message.reply_text(report, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(report)

    async def _cmd_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume from a safety pause."""
        if not self._is_authorized(update.effective_user.id):
            return
        try:
            from tools.safety_monitor import get_safety_monitor
            monitor = get_safety_monitor()
            result = monitor.manual_resume()
            await update.message.reply_text(f"Safety monitor: {result}")
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    # ============================================================
    # Message Handlers
    # ============================================================

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_authorized(update.effective_user.id):
            await update.message.reply_text("Unauthorized.")
            return

        self._clayton_chat_id = update.effective_chat.id
        user_text = update.message.text

        # Notify heartbeat that user is active — defers autonomous beats
        if self._heartbeat:
            self._heartbeat.notify_user_activity()

        # --- Debounce: buffer rapid-fire messages (Telegram splits long messages) ---
        chat_id = update.effective_chat.id
        if chat_id not in self._msg_buffer:
            self._msg_buffer[chat_id] = []
        self._msg_buffer[chat_id].append(user_text)
        self._msg_updates[chat_id] = update  # keep latest for reply context

        # Cancel any existing debounce timer for this chat
        existing_task = self._msg_debounce_task.get(chat_id)
        if existing_task and not existing_task.done():
            existing_task.cancel()
            logger.debug(f"Debounce: buffered message part ({len(user_text)} chars), waiting for more")

        # Show typing indicator while we wait / process
        await update.effective_chat.send_action("typing")

        # Start new debounce timer
        self._msg_debounce_task[chat_id] = asyncio.create_task(
            self._debounced_process(chat_id)
        )

    async def _debounced_process(self, chat_id: int):
        """Wait for the debounce window, then process all buffered messages as one."""
        try:
            await asyncio.sleep(self.MESSAGE_DEBOUNCE_SECONDS)

            # Per-chat lock to prevent concurrent buffer access
            if chat_id not in self._msg_locks:
                self._msg_locks[chat_id] = asyncio.Lock()
            async with self._msg_locks[chat_id]:
                # Collect and clear the buffer
                parts = self._msg_buffer.pop(chat_id, [])
                update = self._msg_updates.pop(chat_id, None)
        except asyncio.CancelledError:
            logger.debug(f"Debounce cancelled for chat {chat_id}")
            raise
        finally:
            self._msg_debounce_task.pop(chat_id, None)

        if not parts or not update:
            return

        user_text = "\n".join(parts)
        if len(parts) > 1:
            logger.info(f"Debounce: merged {len(parts)} message parts into one ({len(user_text)} chars)")

        # --- Normal message processing (was in _handle_message) ---

        # If the router is busy (creative drive OR previous long request),
        # let Clayton know his message is queued behind the lock
        if self.router._send_lock.locked():
            await update.message.reply_text(
                "I'm in the middle of something — give me a moment. Your message is queued. 🦞"
            )

        # Check if handoff is needed before processing
        if self.router.needs_handoff():
            await update.message.reply_text("Context is heavy — running handoff first...")
            from memory import trigger_handoff, write_claude_md
            await trigger_handoff(self.router)
            self.router.reset_conversation()
            write_claude_md()

        # Send to model (queues behind any active creative drive via router lock)
        try:
            response = await self.router.send(user_text)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await update.message.reply_text(f"Error: {e}")
            return

        # Handle model switch if requested
        if response.switch_model_request:
            self.router.switch_model(response.switch_model_request)

        # Send response
        await avatar.set_state("speaking")
        reply_text = response.text
        if not reply_text:
            reply_text = (
                f"[Text dropped — result was empty. "
                f"turns={response.num_turns}, cost=${response.cost_usd:.4f}. "
                f"Check daemon logs for full JSON dump.]"
            )

        # Add model indicator
        model_tag = f"[{response.model_used}]"
        if response.tool_calls_made:
            model_tag += f" [{len(response.tool_calls_made)} tools used]"

        full_reply = f"{reply_text}\n\n_{model_tag}_"

        for chunk in _split_message(full_reply):
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(chunk)

        # Send voice message
        audio_path = await generate_tts(reply_text)
        if audio_path:
            await self.send_voice_to_clayton(audio_path)

        # Log the interaction
        log_session_event(
            "Telegram interaction",
            f"Clayton: {user_text[:100]}... → Clawd: {reply_text[:100]}..."
        )

    async def _handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photos from Clayton — save and analyze with vision model."""
        if not self._is_authorized(update.effective_user.id):
            return

        self._clayton_chat_id = update.effective_chat.id
        caption = update.message.caption or ""

        # Notify heartbeat that user is active
        if self._heartbeat:
            self._heartbeat.notify_user_activity()

        await update.effective_chat.send_action("typing")

        # Busy ack if router is processing something
        if self.router._send_lock.locked():
            await update.message.reply_text(
                "I'm in the middle of something — give me a moment. Your photo is queued. 🦞"
            )

        # Get the largest resolution photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        # Save to incoming/
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"photo_{timestamp}.jpg"
        save_path = config.CLAWD_HOME / "incoming" / filename
        save_path.parent.mkdir(parents=True, exist_ok=True)
        await file.download_to_drive(str(save_path))

        logger.info(f"Photo saved: {save_path}")

        # Pass image to Claude Code (native multimodal support)
        msg = f"Clayton sent a photo (saved to {save_path})."
        if caption:
            msg += f"\nCaption: \"{caption}\""
        msg += "\n\nView the image with the Read tool and respond to Clayton about what you see."

        response = await self.router.send(msg)

        # Handle model switch if requested
        if response.switch_model_request:
            self.router.switch_model(response.switch_model_request)

        reply = response.text or "Photo received and analyzed."

        for chunk in _split_message(reply):
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(chunk)

        # Send voice message
        audio_path = await generate_tts(reply)
        if audio_path:
            await self.send_voice_to_clayton(audio_path)

        # Log the interaction
        log_session_event(
            "Telegram interaction",
            f"Clayton: [photo: {filename}] {caption[:80]}... → Clawd: {reply[:100]}..."
        )

    async def _handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle file uploads from Clayton — save to clawd's filesystem."""
        if not self._is_authorized(update.effective_user.id):
            return

        doc = update.message.document
        caption = update.message.caption or ""

        # Busy ack if router is processing something
        if self.router._send_lock.locked():
            await update.message.reply_text(
                "I'm in the middle of something — give me a moment. Your file is queued. 🦞"
            )

        # Download the file
        file = await context.bot.get_file(doc.file_id)
        save_path = config.CLAWD_HOME / "incoming" / doc.file_name
        save_path.parent.mkdir(parents=True, exist_ok=True)
        await file.download_to_drive(str(save_path))

        # Check if it's an image sent as document (uncompressed)
        suffix = save_path.suffix.lower()
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}
        if suffix in image_exts:
            # Image sent as document — Claude Code can view it natively
            msg = f"Clayton sent an image file: {doc.file_name} (saved to {save_path})"
            if caption:
                msg += f"\nCaption: \"{caption}\""
            msg += "\n\nView the image with the Read tool and respond to Clayton about what you see."
        else:
            # Non-image file
            msg = f"Clayton sent a file: {doc.file_name} (saved to incoming/{doc.file_name})"
            if caption:
                msg += f"\nCaption: {caption}"
            msg += "\nYou can read it with the read_file tool."

        response = await self.router.send(msg)
        reply = response.text or "File received."

        for chunk in _split_message(reply):
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(chunk)


    async def _handle_sticker(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle stickers from Clayton — extract metadata and forward to model."""
        if not self._is_authorized(update.effective_user.id):
            return

        self._clayton_chat_id = update.effective_chat.id
        sticker = update.message.sticker

        if self._heartbeat:
            self._heartbeat.notify_user_activity()

        await update.effective_chat.send_action("typing")

        # Busy ack if router is processing something
        if self.router._send_lock.locked():
            await update.message.reply_text(
                "I'm in the middle of something — give me a moment. Your sticker is queued. 🦞"
            )

        # Extract sticker info
        emoji = sticker.emoji or ""
        set_name = sticker.set_name or "unknown"
        is_animated = sticker.is_animated
        is_video = sticker.is_video
        file_id = sticker.file_id

        sticker_type = "animated" if is_animated else ("video" if is_video else "static")

        # For static stickers, try to download and analyze with vision
        vision_note = ""
        if not is_animated and not is_video:
            try:
                file = await context.bot.get_file(file_id)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = config.CLAWD_HOME / "incoming" / f"sticker_{timestamp}.webp"
                save_path.parent.mkdir(parents=True, exist_ok=True)
                await file.download_to_drive(str(save_path))
                vision_note = f"\nSticker image saved to incoming/{save_path.name} — you can analyze it with vision if curious."
            except Exception as e:
                logger.debug(f"Could not download sticker image: {e}")

        msg = (
            f"Clayton sent a {sticker_type} sticker.\n"
            f"Emoji: {emoji}\n"
            f"Sticker set: {set_name}\n"
            f"File ID: {file_id}{vision_note}\n\n"
            f"Respond naturally to the sticker. You can send one back with send_sticker(file_id)."
        )

        response = await self.router.send(msg)
        reply = response.text or f"{emoji}"

        for chunk in _split_message(reply):
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(chunk)

        # Send voice
        audio_path = await generate_tts(reply)
        if audio_path:
            await self.send_voice_to_clayton(audio_path)

        log_session_event(
            "Telegram interaction",
            f"Clayton: [sticker: {emoji} from {set_name}] → Clawd: {reply[:100]}..."
        )

    async def _handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages and audio from Clayton — transcribe with Deepgram."""
        if not self._is_authorized(update.effective_user.id):
            return

        self._clayton_chat_id = update.effective_chat.id

        if self._heartbeat:
            self._heartbeat.notify_user_activity()

        await update.effective_chat.send_action("typing")

        # Busy ack if router is processing something
        if self.router._send_lock.locked():
            await update.message.reply_text(
                "I'm in the middle of something — give me a moment. Your voice message is queued. 🦞"
            )

        # Get the voice/audio file
        voice = update.message.voice or update.message.audio
        if not voice:
            return

        duration = voice.duration or 0
        file = await context.bot.get_file(voice.file_id)

        # Download to temp file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = ".ogg" if update.message.voice else ".mp3"
        save_path = config.CLAWD_HOME / "incoming" / f"voice_{timestamp}{suffix}"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        await file.download_to_drive(str(save_path))

        logger.info(f"Voice message saved: {save_path} ({duration}s)")

        # Transcribe with Deepgram
        transcript = await _transcribe_audio(save_path)

        if transcript:
            msg = (
                f"Clayton sent a voice message ({duration}s). "
                f"Saved to incoming/{save_path.name}.\n\n"
                f"Transcription:\n\"{transcript}\"\n\n"
                f"Respond to what Clayton said."
            )
        else:
            msg = (
                f"Clayton sent a voice message ({duration}s). "
                f"Saved to incoming/{save_path.name}.\n\n"
                f"Transcription failed — Deepgram returned no text. "
                f"Acknowledge the voice message and let Clayton know."
            )

        # Use debounce path — treat transcript as text message to get proper handling
        response = await self.router.send(msg)

        if response.switch_model_request:
            self.router.switch_model(response.switch_model_request)

        reply = response.text or "I heard you, but couldn't make out the words."

        for chunk in _split_message(reply):
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                await update.message.reply_text(chunk)

        # Send voice reply
        audio_path = await generate_tts(reply)
        if audio_path:
            await self.send_voice_to_clayton(audio_path)

        log_session_event(
            "Telegram interaction",
            f"Clayton: [voice: {duration}s] \"{(transcript or '???')[:80]}\" → Clawd: {reply[:100]}..."
        )


async def _transcribe_audio(audio_path: Path) -> str | None:
    """Transcribe audio file using Deepgram Nova-3 API."""
    if not config.DEEPGRAM_API_KEY:
        logger.warning("No Deepgram API key configured — cannot transcribe voice messages.")
        return None

    try:
        with open(audio_path, "rb") as f:
            audio_data = f.read()

        headers = {
            "Authorization": f"Token {config.DEEPGRAM_API_KEY}",
            "Content-Type": "audio/ogg",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.DEEPGRAM_STT_URL,
                headers=headers,
                data=audio_data,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    logger.error(f"Deepgram returned {resp.status}: {body}")
                    return None

                result = await resp.json()

        transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
        confidence = result["results"]["channels"][0]["alternatives"][0].get("confidence", 0)
        logger.info(f"Deepgram transcription ({confidence:.0%}): {transcript[:100]}")
        return transcript if transcript.strip() else None

    except Exception as e:
        logger.error(f"Deepgram transcription failed: {e}", exc_info=True)
        return None


def _split_message(text: str, max_len: int = 4000) -> list[str]:
    """Split text into chunks for Telegram's message limit."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Find a good split point
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = text.rfind(" ", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()
    return chunks
