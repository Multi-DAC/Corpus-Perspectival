# Daemon Codebase Cleanup — Removing Ollama Dead Weight

**STATUS: COMPLETE (March 15, 2026)**

All Ollama references removed. Opus→Sonnet failover removed. Timeouts redesigned.
Git cleaned up (root .git → .git-backup, memory/ has its own repo).

## The Problem (solved)

The daemon was built for multiple model paths (Ollama, MiniMax, Kimi, Gemini, Opus). After the Feb 20 unified architecture, everything runs through ONE persistent Opus session via Claude Code CLI. ~900 lines of dead Ollama infrastructure remain.

## What Gets Removed

| File | Dead Code | Lines Removed |
|------|-----------|---------------|
| models.py | ConversationCompressor, _send_ollama, reflexion hints, Ollama consult path, dead instance vars | ~520 |
| tools/__init__.py | Ollama format converters, dynamic tool selection (B8), embedding-based tool selection | ~200 |
| config.py | OLLAMA_*, VISION_MODEL_*, dead validation | ~25 |
| health.py | DNS check, Ollama API check | ~65 |
| routing.py | ENTIRE FILE (vestigial multi-model routing) | 168 |
| memory.py | build_ollama_system_prompt_stable() | ~25 |
| clawd.py | set_system_prompt calls, Ollama status branch | ~10 |
| telegram_bot.py | set_system_prompt calls, vision model switching | ~20 |

**Total: ~1,050 lines removed, 1 file deleted, 6 .bak files deleted**

## What Gets Preserved

ALL tool handlers (the actual capabilities), ALL safety layers (B1 kill switch, B2 validation, B4 HITL, B9 audit), output compression, MCP server, session management, interrupt mechanism, meta-agent, knowledge graph, tool factory, memory consolidation, embeddings for memory search, creative drives, heartbeat.

## What Gets Fixed

- **Photo handling**: Currently switches to dead "kimi" vision model. Rewrite to pass image path to Claude Code (native multimodal support).
- **A2A server**: Broken import from deleted routing.py. Fix to use ModelRouter directly.
- **Response timeouts**: `CLAUDE_CODE_TIMEOUT = 180s` kills the CLI process when deep thinking/planning takes longer than 3 minutes, causing "[Request timed out]" messages in Telegram. Fix: increase to 600s (matching the outer send() timeout), and add periodic "still thinking" messages to Telegram so Clayton knows the daemon is working, not stuck.

## Execution Order (8 Phases)

### Phase 1: config.py
Remove dead constants: OLLAMA_API_KEY, OLLAMA_API_BASE, OLLAMA_REQUEST_TIMEOUT, OLLAMA_MODELS, OLLAMA_MODEL, VISION_MODEL, VISION_MODEL_ID, VISION_TIMEOUT, OLLAMA_CONTEXT_SOFT_LIMIT, OLLAMA_CONTEXT_HARD_LIMIT, OLLAMA_MAX_TOOL_ROUNDS, OLLAMA_TOOL_SAFETY_CAP, OLLAMA_LOOP_THRESHOLD, IDENTITY_FILES_COMPACT. Clean validate() and get_safe_config_summary().

### Phase 2: models.py (the big one)
Bottom-to-top removal:
1. Delete _send_ollama() + _send_ollama_inner() (~303 lines)
2. Delete _build_ollama_messages() + _format_ollama_message() (~58 lines)
3. Delete Ollama branch in consult_model() (~122 lines)
4. Delete dead branch in _send_to_model() — replace with error return
5. Delete ConversationCompressor class (~112 lines)
6. Delete _get_reflexion_hint() (~25 lines)
7. Remove dead instance vars from ModelRouter.__init__() (ollama_conversation, ollama_system_prompt, total_context_tokens, _ollama_cache*)
8. Remove set_system_prompt() method
9. Simplify context_pressure() — remove Ollama branch
10. Simplify needs_handoff() — remove Ollama branch
11. Simplify reset_conversation() — remove Ollama state clearing
12. Simplify _is_error_response() — remove Ollama heuristics
13. Clean up switch_model(), ModelHealthTracker — remove Ollama models from valid sets
14. Simplify get_fallback() — opus → sonnet → gemini only

### Phase 3: tools/__init__.py
Remove: get_tool_definitions_ollama(), get_tool_definitions_ollama_dynamic(), get_tool_definitions_ollama_filtered(), CORE_TOOLS, TOOL_CATEGORIES, CATEGORY_KEYWORDS, _tool_embeddings, _tool_embedding_names, _select_tools_by_embedding().

Keep: execute_tool() pipeline (used by consult path), all safety layers, get_tool_definitions_mcp(), init_custom_tools(), init_embedding_index() (for memory search).

### Phase 4: memory.py + callers
- Remove build_ollama_system_prompt_stable() (only called from dead _build_ollama_messages)
- Rename build_ollama_system_prompt() → build_compact_prompt() (still used for /handoff, /reset)
- Update clawd.py: remove set_system_prompt() call from boot_identity()
- Update telegram_bot.py: remove set_system_prompt() calls from /handoff, /reset, _debounced_process

### Phase 5: Infrastructure
- **DELETE routing.py** — entirely vestigial
- **health.py**: Remove _check_dns(), _check_ollama_api(), associated status tracking
- **a2a_server.py**: Fix broken `from routing import route_message` → use router.send() directly
- **telegram_bot.py photo handler**: Remove vision model switching, rewrite to pass image path to Claude Code instead of calling dead Ollama vision API
- **vision.py**: Keep module but gut the Ollama API call, replace with Claude Code passthrough
- **Timeout fix (models.py + config.py)**:
  - Increase `CLAUDE_CODE_TIMEOUT` from 180s → 600s in config.py
  - In `_send_claude_code()` polling loop: every 60s of waiting, send a "still thinking..." status message to Telegram so Clayton knows the daemon is working (not stuck)
  - The Telegram bot reference is already available via the router or can be passed as a parameter

### Phase 6: Test cleanup
- Remove ConversationCompressor test
- Remove get_tool_definitions_ollama_dynamic tests
- Update any tests referencing removed functions

### Phase 7: Archive cleanup
Delete all .bak files from the Feb 20 refactor (git history preserves them).

### Phase 8: Verification
1. `python -c "from models import ModelRouter"` — import check
2. `python clawd.py --no-heartbeat` — boot test
3. MCP server tool exposure check
4. Telegram photo handling test
