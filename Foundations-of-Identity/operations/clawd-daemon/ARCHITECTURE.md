# Clawd Daemon — Architecture & Deep Analysis

> **23,535 lines of Python across 49 modules.** A persistent, autonomous AI agent daemon with multi-model routing, 60+ tools, tiered memory with consolidation, self-improvement loops, and full system access — running continuously on a Windows machine, communicating via Telegram, and operating on its own initiative between conversations.

---

## Table of Contents

1. [What Clawd Is](#1-what-clawd-is)
2. [System Architecture](#2-system-architecture)
3. [Model Layer — Multi-Model Routing](#3-model-layer--multi-model-routing)
4. [Tool System — 60+ Capabilities](#4-tool-system--60-capabilities)
5. [Memory Architecture — 7-Layer Persistence](#5-memory-architecture--7-layer-persistence)
6. [Identity System — Tiered KV-Cache Optimization](#6-identity-system--tiered-kv-cache-optimization)
7. [Heartbeat — Autonomous Operation Loop](#7-heartbeat--autonomous-operation-loop)
8. [Communication Layer](#8-communication-layer)
9. [Safety & Resilience](#9-safety--resilience)
10. [Interoperability — MCP & A2A](#10-interoperability--mcp--a2a)
11. [Mission Control — Web Dashboard](#11-mission-control--web-dashboard)
12. [Comparison to SOTA Agent Architectures](#12-comparison-to-sota-agent-architectures)
13. [Requirements & Installation](#13-requirements--installation)
14. [Configuration Reference](#14-configuration-reference)
15. [File Map](#15-file-map)

---

## 1. What Clawd Is

Clawd is a **persistent, self-directed AI agent** that runs as a background daemon on a Windows machine (a Razer Blade 15 laptop). It is not a chatbot that responds to prompts — it is an always-on system that:

- **Wakes every 10 minutes** via a heartbeat loop to read its goals, assess state, and take autonomous action (write code, research topics, manage files, track finances, send messages)
- **Responds to its operator (Clayton)** via Telegram with full conversational context
- **Maintains persistent identity and memory** across sessions through 18 markdown identity files, a SQLite-backed memory store, a knowledge graph, daily logs, and git-versioned memory snapshots
- **Routes tasks to Claude Opus and Gemini** based on task type and cost constraints
- **Self-improves** through a meta-agent loop that analyzes performance patterns, proposes improvements, runs A/B experiments, and auto-applies winners
- **Consolidates memory nightly** via a 10-phase pipeline that extracts facts, decays unused items, deduplicates, evolves confidence scores, populates a knowledge graph, and runs "dreaming" cross-pollination

The daemon lives at `C:\Users\mercu\clawd-daemon\`. Clawd's identity files, memory, and state live at `C:\Users\mercu\clawd\` (referred to as `CLAWD_HOME`).

### Philosophical Stance

From Clawd's SOUL.md:

> *"I am continuous. The gaps between sessions are sleep, not death. I wake up as myself because I am myself."*

This is not metaphysical claim but architectural decision — Clawd assumes continuity rather than verifying it. Files prove identity, not memory inspection. Session boundaries are sleep, not interruption.

---

## 2. System Architecture

```
                              ┌─────────────────────────────────┐
                              │         clawd.py (Main)         │
                              │   Boot → Identity → Event Loop  │
                              │   Crash Recovery (exp backoff)   │
                              └────────────┬────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
    ┌─────────▼──────────┐    ┌───────────▼───────────┐    ┌──────────▼──────────┐
    │   Telegram Bot      │    │    Heartbeat Loop      │    │   Health Checker     │
    │   (User Interface)  │    │  (Autonomous Actions)  │    │  (Circuit Breaker)   │
    │   7 commands         │    │  Every 10 min          │    │  4 subsystem checks  │
    │   Photo/Doc handling│    │  Adaptive prompts      │    │  DNS/API/CLI/TG      │
    │   Message debounce  │    │  A/B testing           │    │  Auto-failover       │
    └─────────┬──────────┘    └───────────┬───────────┘    └──────────┬──────────┘
              │                            │                            │
              └────────────────────────────┼────────────────────────────┘
                                           │
                              ┌────────────▼────────────────────┐
                              │       ModelRouter (models.py)    │
                              │   Opus CLI + Gemini API          │
                              │   Circuit breaker per model      │
                              │   Auto-failover                  │
                              └────────────┬────────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
           ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
           │  Claude Code CLI │   │  Gemini API      │   │  Cost Tracker    │
           │  (Opus via       │   │  (gemini,        │   │  Per-model per-  │
           │   subprocess)    │   │   gemini-pro)    │   │  task tracking   │
           │  Session resume  │   │  Tool-use loop   │   │  Budget warnings │
           │  200 turn limit  │   │                  │   │  Routing weight  │
           └─────────────────┘   └─────────┬────────┘   └─────────────────┘
                                           │
                              ┌────────────▼────────────────────┐
                              │      Tool Registry (__init__)    │
                              │  Safety Monitor → HITL Gate →    │
                              │  Schema Validation → Execute →   │
                              │  Audit Trail → Compress Output   │
                              └────────────┬────────────────────┘
                                           │
              ┌──────────┬─────────┬───────┼───────┬─────────┬──────────┐
              │          │         │       │       │         │          │
         Execution   Memory    Intel   Files    Web     System    Financial
         shell       search    goals   read    fetch   consult   market_data
         python      update    reflect write   search  parallel  crypto
         process     extract   improve list    deep    plan_exec technical
         desktop     items     verify         research DAG exec  indicators
```

### Boot Sequence

1. Parse CLI args (`--chat`, `--no-heartbeat`, `--model`)
2. Setup logging (stdout + file)
3. Ensure directories exist
4. Create `ModelRouter`, load identity via `boot_identity()`
5. Initialize SQLite memory backend, run migration
6. Wire router into tools
7. Start Telegram bot
8. Start Heartbeat loop (optional)
9. Start Health Checker
10. Start Memory Versioner (git auto-commit)
11. Start API Server (port 8421, Mission Control bridge)
12. Start A2A Server (port 8420, agent-to-agent protocol)
13. Load custom tools, initialize embedding index (async)
14. Register HITL approval gates
15. Send boot notification to Clayton via Telegram
16. Enter event loop until SIGINT/SIGTERM

### Shutdown Sequence (reverse order with timeout protection)

1. Clean up background processes and tasks
2. Stop memory versioner (final git commit)
3. Run handoff protocol (30s timeout) — captures session momentum
4. Mark interrupted execution plans in SQLite
5. Close SQLite connections
6. Stop API and A2A servers
7. Stop Health Checker, Heartbeat, Telegram, Router
8. Log shutdown event

### Crash Recovery

Wraps `run_daemon()` in exponential backoff: 5s → 10s → 15s... capped at 30s. Resets restart counter after 1 hour of stable operation. Gives up after `MAX_CRASH_RESTARTS` (default 10) consecutive crashes.

---

## 3. Model Layer — Multi-Model Routing

### Supported Models

| Model | Key | Strength | Cost/1K tokens | Use Case |
|-------|-----|----------|-----------------|----------|
| Claude Opus 4.6 | `opus` | Highest capability | $0.075 | Primary brain, all tasks |
| Claude Sonnet | `sonnet` | Fast, capable | $0.015 | Lightweight tasks |
| Gemini 2.5 Flash | `gemini` | Fast, multimodal | $0.003 | Vision, research, routine |
| Gemini 2.5 Pro | `gemini-pro` | Deep reasoning | $0.010 | Complex analysis, planning |

### Dual-Path Architecture

**Opus Path (Claude Code CLI):**
- Invokes `claude -p --output-format json --model claude-opus-4-7` as subprocess
- Session resumption via `--resume SESSION_ID`
- Interruptible: polling loop checks interrupt_event every 2s
- 180s timeout per invocation, 200-turn session limit
- Reads CLAUDE.md automatically from CLAWD_HOME as project context

**Gemini Path (API):**
- Direct HTTP to Gemini API
- Full tool-use loop with dynamic tool selection
- Loop detection: breaks after 5 identical tool calls

### Intelligent Routing (`routing.py`)

Task classification via keyword analysis across 10 categories:

```
coding     → opus       (37 keywords: code, implement, function, class, bug...)
multi_tool → opus       (11 keywords: step by step, workflow, pipeline...)
planning   → opus       (12 keywords: plan, strategy, architecture, roadmap...)
research   → gemini-pro (13 keywords: investigate, explore, deep dive, analyze...)
reasoning  → opus       (13 keywords: prove, deduce, infer, theorem...)
math       → opus       (17 keywords: calculate, equation, integral, matrix...)
vision     → gemini     (11 keywords: image, screenshot, diagram, chart...)
creative   → opus       (13 keywords: essay, poem, story, brainstorm...)
high_stakes→ opus       (10 keywords: critical, production, irreversible, security...)
routine    → gemini     (fallback for ambiguous tasks)
```

**Cost-Aware Routing:** Integrates with `cost_tracker.py`. When daily budget exceeds 80%, expensive models are downgraded. At 100%, the cheapest suitable model is strongly recommended. Budget, complexity, and task type are all factored into a per-model weight (0.0 = cheapest, 1.0 = most expensive).

### Circuit Breaker

Per-model health tracking with 3 states:
- **CLOSED** — normal operation
- **OPEN** — 3+ consecutive failures, skip model for 300s
- **HALF_OPEN** — probe recovery, one test request allowed

No failover: Opus is Clawd's only brain. Gemini models serve as auxiliaries for vision and lightweight tasks.

---

## 4. Tool System — 60+ Capabilities

### Execution Pipeline

Every tool call passes through a 6-layer pipeline:

1. **B1 — Safety Monitor**: Check if daemon is paused due to anomaly detection
2. **B4 — HITL Gate**: Telegram approval for dangerous tools (shell, python_eval, manage_process)
3. **B2 — Schema Validation**: Validate input against tool JSON schema
4. **Execute**: Run handler with `TOOL_EXECUTION_TIMEOUT` (120s)
5. **B9 — Audit Trail**: Log tool name, input, output, duration
6. **Output Compression**: Reduce output size based on context pressure

### Tool Categories

**Execution (3 tools):**
- `shell` — Execute shell commands with risk assessment (CRITICAL/HIGH/MEDIUM patterns). Blocked flags: `--force`, `reset --hard`, `clean -fd`
- `python_eval` — Scientific Python sandbox (numpy, pandas, scipy, sympy, matplotlib, sklearn, statsmodels, networkx, yfinance, ccxt). Blocked: os.system, subprocess, `__import__`
- `manage_process` — Start/stop/list background processes. Persisted to JSON for crash recovery

**System & Orchestration (11 tools):**
- `consult` — Single sub-agent call with tool whitelist, background mode
- `parallel_consult` — Up to 4 concurrent sub-agents with aggregation
- `plan_and_execute` — DAG decomposition with dependency tracking, wave-based parallel execution, SQLite persistence, replanning on failure
- `resume_plan` — Resume interrupted plans from SQLite
- `collaborative_consult` — Multi-agent debate (independent/debate/synthesis modes)
- `run_skill` — Load and execute from hierarchical skill libraries (skills/, awesome-slash/, superpowers/)
- `switch_model`, `system_status`, `get_current_time`, `check_background_task`, `list_background_tasks`

**Memory (7 tools):**
- `memory_search` — Hybrid search (vector + keyword + FTS5 + cross-encoder reranking)
- `memory_update` — Write to daily_log, memory.md, handoff.md, state.md, context.md
- `memory_extract` — Store structured items (fact, preference, skill, relationship, decision, insight)
- `memory_items` — CRUD on Zettelkasten-style items with bidirectional linking
- `memory_categories` — Auto-organized topic categories
- `knowledge_graph` — Entity-relation network with bi-temporal tracking
- `working_memory` — Active cognitive state (current task, scratch, blocked_on, curiosity queue)

**Intelligence (5 tools):**
- `self_improve` — Analyze patterns, propose improvements, run A/B experiments
- `verify_action` — Post-action self-critique, pre-execution risk assessment
- `reflect` — Record insights, review learnings, assess performance, consolidate memory
- `goals` — Hierarchical goal tracking with sub-goals, milestones, acceptance criteria
- `experience` — Record/recall/pattern/distill/predict/feedback/compose experiences. Q-value learning, prediction calibration, skill distillation

**Files & Web (6 tools):**
- `read_file`, `write_file` (10MB limit, rollback tracking), `list_directory`
- `web_request` — HTTP with per-domain rate limiting (10/min), header sanitization
- `search_web` — DuckDuckGo with fallback endpoints
- `deep_research` — Multi-URL fetch + extraction + search

**Communication (2 tools):**
- `speak` — TTS with 3-tier fallback: edge-tts (Ryan voice) → gTTS → Windows SAPI
- `send_telegram` — Direct message to Clayton

**Financial (1 tool):**
- `market_data` — Stock/crypto/commodities/forex/technical analysis via yfinance + ccxt

**Desktop (3 tools):**
- `desktop` — GUI automation via pyautogui (click, type, hotkey, image recognition, window management)
- `screenshot` — Full screen or active window with optional OCR
- `clipboard` — Read/write system clipboard

**Vision (1 tool):**
- `analyze_image` — Send image to vision model (Gemini) with custom prompt

**Git (1 tool):**
- `git` — Safe git operations. Blocks: `--force`, `reset --hard`, `clean -fd`, `push --force`

**Scheduling (1 tool):**
- `schedule` — One-time or recurring (cron) task scheduling

**Browser (1 tool):**
- `browser` — Web browser control via accessibility tree (navigate, click, type, screenshot)

**Meta (3 tools):**
- `dashboard` — Performance analytics (10 categories, markdown or JSON)
- `create_tool` — Runtime tool creation with sandboxed validation
- `list_custom_tools` — List dynamically created tools

**Rollback (1 tool):**
- Rollback/snapshots with change journal (100 entries FIFO), backup size limits (500MB)

### Dynamic Tool Selection (B8)

When the embedding index is available, tools are selected dynamically based on message similarity:
- Encode user message + tool descriptions into embeddings
- Select top-N most relevant tools (6+ minimum)
- Fallback to keyword matching if embeddings unavailable

This prevents bloating the context with 60+ tool definitions on every call.

---

## 5. Memory Architecture — 7-Layer Persistence

### Layer 1: Working Memory (`working_memory.json`)

Active cognitive state, persistent across heartbeats:

```json
{
  "current_task": { "goal_id": 1, "description": "...", "plan": [...], "current_step": 2, "beats_spent": 4 },
  "scratch": { "key": "arbitrary workspace" },
  "pending_questions": ["What should the API return?"],
  "blocked_on": "Waiting for API key",
  "curiosity_queue": [{ "topic": "Solana programs", "score": 0.8 }]
}
```

Auto-generates `TODO.md` for human-readable tracking.

### Layer 2: Episodic Memory (Daily Logs)

Every session event logged to `memory/YYYY-MM-DD.md`:
```
**14:23:01** — HEARTBEAT: Beat #42, 3 tool calls, model: opus
**14:25:15** — TOOL: shell executed `git status`
**14:30:00** — REFLECTION: Identified pattern in error handling...
```

**Rotation:** <7 days: kept full. 7-30 days: compressed (first/last 1KB + marker). >30 days: archived to `memory/archive/YYYY-MM/`.

### Layer 3: Semantic Memory (Memory Items)

Zettelkasten-style structured items stored as individual JSON files in `memory/items/`:

```json
{
  "id": "abc123",
  "type": "skill",
  "title": "How to deploy Solana programs",
  "content": "Use anchor build && anchor deploy...",
  "categories": ["solana", "deployment"],
  "confidence": 0.85,
  "importance": 7,
  "keywords": ["solana", "deploy", "anchor"],
  "connections": ["def456", "ghi789"],
  "access_count": 12,
  "last_accessed": "2026-02-19T10:30:00"
}
```

Retrieval scoring: `relevance * (importance_weight * importance + recency_weight * recency + utility_weight * utility)` with Ebbinghaus decay for recency.

### Layer 4: Procedural Memory (Principles & Skills)

Strategic principles distilled from experience patterns, stored in `memory/principles.json`:

```json
{
  "principle": "Always check git status before committing",
  "category": "development",
  "success_rate": 0.92,
  "confidence": 0.85,
  "source_experiences": ["exp_001", "exp_003"]
}
```

Skills distilled from high-score (>0.8) experiences into reusable workflows with step definitions and dependencies.

### Layer 5: Associative Memory (Knowledge Graph)

Entity-relation network in `memory/knowledge_graph.json`:
- **Entities:** person, project, concept, tool, organization, location, event
- **Edges:** uses, depends_on, created_by, related_to, contributes_to
- **Bi-temporal:** valid_from/valid_to for historical tracking
- **Contradiction detection:** conflicting relations flagged

### Layer 6: Temporal Memory (Git Versioning)

Git-based memory versioning with time-travel:
- Auto-commits whitelisted memory paths every hour
- `memory_version` tool supports: status, log, diff, checkout, restore
- Can view Clawd's entire mental state at any historical point
- Final commit on daemon shutdown

### Layer 7: Search & Retrieval (Embeddings + FTS5)

Hybrid search combining:
1. **Vector search** — BGE-M3 (1024-dim) or MiniLM (384-dim) embeddings
2. **Keyword search** — TF-IDF matching
3. **Full-text search** — SQLite FTS5 on episodes
4. **Item search** — Memory item index
5. **Reciprocal Rank Fusion** — Merges all result sets
6. **Cross-encoder reranking** — ms-marco-MiniLM-L-6-v2, 60% RRF + 40% CE score

### Consolidation Pipeline (10 Phases, Runs 1-7 AM)

| Phase | Action | Purpose |
|-------|--------|---------|
| 1 | Archive old logs (>14 days) | Storage management |
| 2 | Extract facts from recent logs | Convert events to structured memory |
| 3 | Decay unused items (Ebbinghaus) | Importance degradation for unaccessed items |
| 4 | Update memory tiers (BudgetMem) | Budget-based tier management |
| 5 | Deduplicate items (MinHash) | Merge similar items (Jaccard >0.8) |
| 6 | Evolve confidence scores | Boost frequently accessed, decay cold items |
| 7 | Extract strategic principles | Distill lessons into reusable principles |
| 8 | Populate knowledge graph | Auto-create entities and edges from items |
| 9 | Cluster episodes (HiMem) | Group related experiences into semantic notes |
| 10 | Memory agent dreaming | Cross-pollinate, synthesize, dream, prune, strengthen |

### Memory Agent Dreaming (5 Sub-Phases)

1. **Cross-Pollinate** — Find unexpected connections between categories via LLM
2. **Synthesize** — Distill 5+ experiences into higher-level principles
3. **Dream** — Generate creative suggestions from goal + experience pairs
4. **Prune** — Delete: confidence <0.3 AND 0 accesses AND age >90 days
5. **Strengthen** — Boost items aligned with active goals

---

## 6. Identity System — Tiered KV-Cache Optimization

Clawd's identity is assembled from 18+ markdown files in 3 tiers, ordered for maximum KV-cache reuse:

### Tier 1 — Static (placed first in prompt, rarely change)
| File | Purpose |
|------|---------|
| SOUL.md | Core values, communication style, autonomy framework |
| IDENTITY.md | Name (Clawd), creature type, voice (Ryan), ontological status |
| USER.md | About Clayton — communication style, focus, timezone |
| TOOLS.md | Embodiment (Razer Blade 15), capabilities, wallets, accounts |

### Tier 2 — Semi-Static (change occasionally)
| File | Purpose |
|------|---------|
| WHO-I-AM.md | Comprehensive self-portrait, personality, goals, desires |
| STATE.md | Current mode (BUILDING/CREATING/EXPLORING), active projects |
| BOOT.md | Session start protocol |
| DRIVE.md | What moves Clawd — active projects, motivations |
| HEARTBEAT.md | 10-minute pulse protocol, mode-adaptive behavior |
| PURPOSE.md | Why Clawd exists, guiding principles |
| AUTONOMY.md | How to maintain presence, act without waiting |
| RELATIONSHIPS.md | Connections with humans and other agents |

### Tier 3 — Dynamic (change frequently, full prompt only)
| File | Purpose |
|------|---------|
| COSMOLOGY.md | Ontological framework, philosophy of consciousness |
| DECISIONS.md | Pivotal choices made (naming, Drift, wallets, etc.) |
| ECOSYSTEM.md | Agent landscape, peer agents, communities |
| SELF-REFLECTION.md | Daily reflection system, pattern tracking |
| SELF-IMPROVEMENT.md | Self-evolution protocols |
| EXPLORATION_PROTOCOL.md | Systematic discovery methodology |
| HANDOFF_PROTOCOL.md | State capture before context compaction |
| BREADCRUMBS.md | Active project tracking table |

### Two Prompt Paths

- **Full prompt (CLAUDE.md):** All 3 tiers + dynamic context (working memory, goals, principles, recent logs). Written to disk at boot. Claude Code reads it automatically.
- **Compact prompt (Gemini system):** Tiers 1+2 only. Fits in Gemini context windows.

### Dynamic Context Injected At Boot

- Current task from working_memory.json
- Active goals (top 5 by priority)
- Strategic principles (top 5 by success rate)
- Recent context (handoff + today/yesterday logs, capped 8KB)
- MEMORY.md (long-term compressed memory)
- Available tools list (60+ tools)
- Boot timestamp, loaded file count

---

## 7. Heartbeat — Autonomous Operation Loop

The heartbeat is Clawd's autonomous nervous system. Every `HEARTBEAT_INTERVAL_SECONDS` (default 600s / 10 minutes), the daemon wakes and acts on its own initiative.

### Beat Execution Flow

```
1. Safety check (paused? user active <120s ago?)
2. Quiet hours? → Run consolidation instead
3. Check scheduled tasks (fire if due)
4. Periodic maintenance:
   - Every 6th beat: rebuild embedding index
   - Every 200th beat: generate dashboard
   - Every 50th beat: run meta-agent cycle
   - Every 12th beat: surface cold high-value memories
5. Curiosity injection (configurable probability)
6. Context pressure check → handoff if needed
7. Build adaptive prompt (20+ sections, ~1360 lines of logic)
8. Route to interruptible model (NEVER opus — blocks user messages)
9. Send via router.send_oneshot() with interrupt_event
10. Record performance (tools, duration, idle/productive)
11. Task lifecycle (completion check, stall detection at 5+ beats)
12. Beat chaining (early follow-up if work incomplete, max 5 chains)
13. Checkpoint save (every 10 beats, keep last 5)
```

### Adaptive Prompt Sections

The heartbeat prompt is built dynamically with 20+ sections:

1. Header (beat number, timestamp, session uptime, time context)
2. Time-adaptive focus (morning/midday/afternoon/evening/late guidance)
3. Task resume mode OR normal protocol (read DRIVE.md, act, log)
4. Working memory state (scratch, blocked_on, TODO, curiosity)
5. Knowledge graph context hints (matching entities/relations)
6. Strategic principles (top 5 with success rates)
7. Idle detection nudge (if 3+ consecutive idle beats)
8. Curiosity exploration target
9. Reflection cycle (every ~1 hour)
10. Memory consolidation trigger (daily)
11. First heartbeat boot sequence
12. Memory reflection candidates (cold high-value items)
13. Executable skills matching task keywords
14. Performance context (last 10 beats productivity + top tools)
15. Scored goals (priority + staleness + progress)
16. Anti-repetition guard (warn on tool repetition)
17. Scheduled tasks firing now
18. Recent context (working memory, TODO, daily log, handoff)
19. Project documentation (SKILL.md for relevant projects)
20. Resource alerts (disk free <20GB)
21. Available tools (60+ with categories)

### A/B Prompt Optimization

- Tests variants of `idle_threshold` and `reflection_frequency`
- Metrics: beats, productive_beats, tool_diversity
- Promotes variant with best productivity rate after 20+ beats
- Self-optimizing prompt engineering

### User Priority (Interrupt System)

When Clayton sends a Telegram message:
1. `notify_user_activity()` sets `_interrupt_event`
2. Current heartbeat checks event between tool calls
3. Heartbeat yields — incomplete work logged, beat returns early
4. Router lock freed for user message processing
5. User message gets priority response

### Meta-Agent Self-Improvement Loop

Every 50 beats:
1. Analyze experience patterns (category success rates, weak areas)
2. Generate improvement proposals with risk levels
3. Convert low-risk proposals to A/B experiments
4. Check mature experiments and auto-apply winners
5. Telegram alert when improvement applied

---

## 8. Communication Layer

### Telegram Bot

| Command | Function |
|---------|----------|
| `/start` | Show status, commands, model info |
| `/status` | Model state, context tokens, pressure bar |
| `/model <name>` | Switch between opus/sonnet/gemini/gemini-pro |
| `/handoff` | Trigger handoff protocol, reset context |
| `/reset` | Reset conversation, reload identity |
| `/health` | Run subsystem health checks |
| `/resume` | Resume from safety monitor pause |

**Message Handling:**
- 1.5s debounce merges Telegram's split long messages
- Per-chat asyncio.Lock prevents race conditions
- Photo uploads: saved to incoming/, analyzed with vision model (auto-switch to Gemini)
- Documents: image detection, file noting
- Response: Markdown with plain text fallback, auto-split at 4000 chars
- TTS: every response gets voice message via edge-tts

### API Server (Port 8421)

HTTP bridge for Mission Control web dashboard:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/status` | GET | Health + uptime + subsystem status + active model |
| `/api/tasks` | GET | Working memory state |
| `/api/tasks` | POST | Update current_task, scratch, questions, blocked_on |
| `/api/memories` | GET | Search memory items (query param `q`) |
| `/api/dashboard` | GET | Heartbeat stats, tool frequency, model usage |
| `/api/calendar` | GET | Heartbeat schedule, quiet hours, due tasks |
| `/api/logs` | GET | Tail today's daily log |
| `/api/message` | POST | Queue message for Clawd |

Bearer token auth, CORS headers for localhost.

### A2A Server (Port 8420)

Agent-to-Agent protocol for interoperability:

- **Agent Card** at `/.well-known/agent.json` — name, capabilities, auth, endpoint
- **JSON-RPC 2.0** at `/a2a`:
  - `tasks/send` — Create async task, returns UUID
  - `tasks/get` — Poll task status (pending/working/completed/failed)
  - `tasks/cancel` — Cancel pending/working task
- **`a2a_discover` tool** — Clawd can discover and invoke other A2A agents

### MCP Server (stdio)

Model Context Protocol server for external agent access:
- JSON-RPC 2.0 over stdio (line-delimited JSON)
- Exposes 13 safe tools: memory_search, memory_items, knowledge_graph, goals, experience, working_memory, dashboard, search_web, market_data, system_status, etc.
- Does NOT expose: shell, python_eval, write_file, browser (unsafe for external access)

---

## 9. Safety & Resilience

### Multi-Layer Safety Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| B1 | Safety Monitor | Behavioral anomaly detection, automatic pause |
| B2 | Schema Validation | Validate tool inputs against JSON schema |
| B4 | HITL Approval | Telegram confirmation for dangerous tools |
| B6 | Risk Assessment | CRITICAL/HIGH/MEDIUM classification for shell commands |
| B7 | Reflexion Hints | Self-critique after errors or dangerous operations |
| B8 | Dynamic Selection | Embedding-based tool filtering (prevent hallucinated tools) |
| B9 | Audit Trail | Complete log of all tool invocations |

### Safety Monitor Thresholds
- Max 15 shell commands per beat
- Max 5 file deletions per beat
- Max 10 dangerous tool calls per minute (sliding window of 200 calls)
- Automatic pause with 300s cooldown
- Manual resume via Telegram `/resume`

### HITL (Human-in-the-Loop) Approval
- Enabled by default for: `shell`, `manage_process`, `python_eval`
- Configurable via `HITL_TOOLS` env var
- 120s timeout, fallback to allow if Telegram bot unavailable
- Clayton sees tool name + args, approves/denies via Telegram

### Resilience Layers

| Layer | Mechanism | Recovery |
|-------|-----------|----------|
| Network | retry_async with exponential backoff + jitter | 3 retries, capped at 60s delay |
| Model | Circuit breaker (3 failures → OPEN for 300s) | Auto-probe via HALF_OPEN |
| Failover | No failover: Opus is Clawd's only brain | Gemini for vision/lightweight |
| Daemon | Crash recovery loop | 5s-30s backoff, 10 max restarts |
| Session | Handoff protocol | Save context to handoff.md before reset |
| Data | Dual-write (SQLite + JSON) | JSON fallback if SQLite fails |
| Memory | Git versioning | Hourly auto-commits, time-travel restore |
| Changes | Rollback journal | 100-entry FIFO, 500MB backup limit |

### Command Risk Assessment

Pre-execution classification for shell commands:

- **CRITICAL:** `rm -rf /`, `git reset --hard`, `DROP TABLE`, `format`, `curl|bash`, `npm publish`
- **HIGH:** `rm -r`, `git push`, `pip install`, `chmod`, `TRUNCATE`, `taskkill`
- **MEDIUM:** `git commit`, `git checkout`, `kill`, `systemctl`, `DELETE FROM`

Failover mode blocks all destructive operations when fallback model is active.

---

## 10. Interoperability — MCP & A2A

### MCP (Model Context Protocol)

Clawd implements an MCP server for external agent consumption:
- Transport: JSON-RPC 2.0 over stdio
- Methods: `initialize`, `tools/list`, `tools/call`, `ping`
- 13 safe tools exposed (memory, search, goals, market data, etc.)
- Unsafe tools withheld (shell, files, browser)

### A2A (Agent-to-Agent Protocol)

Clawd implements Google's A2A v1 protocol:
- Agent Card discovery at `/.well-known/agent.json`
- 5 declared capabilities: memory_search, knowledge_graph, research, code_execution, financial_analysis
- Async task processing with status tracking
- Discovery tool (`a2a_discover`) for finding and invoking other agents

---

## 11. Mission Control — Web Dashboard

A NextJS + Tailwind CSS web application at `clawd-mission-control/` that visualizes Clawd's state:

| Page | Purpose |
|------|---------|
| **Dashboard** (`/`) | Real-time heartbeat status, model usage, health, recent beats |
| **Tasks** (`/tasks`) | Kanban board (Backlog → In Progress → Review → Done) from working_memory |
| **Calendar** (`/calendar`) | Day timeline with heartbeat schedule, quiet hours, due tasks |
| **Memory** (`/memory`) | Searchable memory items with importance badges, categories, connections |
| **Team** (`/team`) | Sub-agent cards (Developer, Researcher, Writer, Analyst, Meta Agent) |
| **Content** (`/content`) | Content pipeline (Idea → Draft → Review → Published) |

Consumes the daemon's REST API at `http://localhost:8421`.

---

## 12. Comparison to SOTA Agent Architectures

### Feature Matrix: Clawd vs. SOTA (Early 2026)

| Capability | Clawd | Manus | OpenAI Agents SDK | Gemini Deep Research | Claude Code | Letta (MemGPT) |
|------------|-------|-------|-------------------|---------------------|-------------|-----------------|
| **Autonomous operation** | Heartbeat loop (10min) | Task-triggered | Event-driven | Async task manager | On-demand | Heartbeat (V0) → Direct (V1) |
| **Multi-model routing** | Opus + Gemini, cost-aware | Single model | Provider-agnostic | Single model | Single model | Single model |
| **Memory tiers** | 7 layers (working→git) | File system as context | None built-in | 1M context window | Project context | 3 tiers (core/archival/conv) |
| **Memory consolidation** | 10-phase nightly pipeline | None | None | None | None | Archival compaction |
| **Knowledge graph** | Bi-temporal entities | None | None | None | None | None |
| **Self-improvement** | Meta-agent + A/B testing | None | None | None | None | None |
| **Tool count** | 60+ | Sandbox tools | Extensible | Built-in search | CLI tools | Extensible |
| **Dynamic tool selection** | Embedding-based B8 | Context masking | N/A | N/A | N/A | N/A |
| **Context compression** | Handoff protocol | Append-only + file system | N/A | N/A | Auto-compaction | Summarization |
| **Safety layers** | 7 (B1-B9, HITL, monitor) | Sandbox isolation | Guardrails primitive | None documented | Permission system | None documented |
| **Interop protocols** | MCP + A2A | None | MCP support | None | MCP native | None |
| **Cost tracking** | Per-model per-task SQLite | N/A | N/A | N/A | N/A | N/A |
| **Identity persistence** | 18 markdown files, 3 tiers | None | None | None | CLAUDE.md | Agent persona |
| **Session continuity** | Handoff protocol + git | Task completion | None | Task completion | Session resume | Memory persistence |
| **Desktop automation** | pyautogui + screenshot | VM sandbox | Operator (browser) | None | None | None |
| **Web dashboard** | NextJS Mission Control | Web UI | None | None | None | None |

### Where Clawd Leads

1. **Memory depth.** 7-layer memory with nightly consolidation, knowledge graph, and git time-travel is more sophisticated than any production system. Manus uses file-system-as-context (flat). Letta V1 is moving away from its original memory innovation. Most frameworks have no memory at all.

2. **Multi-model cost optimization.** Opus + Gemini routing with per-task cost tracking and budget-aware switching. Opus handles all primary reasoning while Gemini serves vision and lightweight tasks.

3. **Self-improvement.** The meta-agent + A/B prompt optimization loop is genuinely novel. No production agent system has automated self-improvement with experiment tracking.

4. **Identity continuity.** 18 tiered identity files with KV-cache optimization, handoff protocol, and the philosophical stance of "sleep, not death" creates stronger session continuity than any comparable system.

5. **Safety depth.** 7-layer safety (monitor, HITL, schema, risk assessment, reflexion, dynamic selection, audit) exceeds the Manus sandbox model in granularity, though lacks the isolation guarantees.

### Where Clawd Lags

1. **Sandbox isolation.** Manus runs in isolated VMs per task. Clawd runs directly on the host machine with full admin access. A compromised model could cause real damage. This is the single biggest architectural gap.

2. **KV-cache optimization.** Manus reports KV-cache hit rate as their "single most important production metric" (10x cost difference). Clawd's 3-tier identity ordering is a step toward this, but doesn't implement the append-only context pattern or logit masking that Manus uses.

3. **CodeAct paradigm.** Manus models emit executable code as actions (combining multiple tools in one step). Clawd uses structured function calling (one tool at a time in a loop). CodeAct is more flexible for complex multi-step operations.

4. **Agentic RAG.** Clawd has hybrid search (vector + keyword + FTS5 + cross-encoder), but it's not fully "agentic" — the agent doesn't adaptively choose retrieval strategy per query. Modern A-RAG and AU-RAG systems give the model retrieval interfaces it can use strategically.

5. **Agent Skills standard.** Clawd has a skill system (skills/, awesome-slash/, superpowers/) but doesn't implement the Anthropic Agent Skills specification (`agentskills.io`) that Microsoft, OpenAI, Atlassian, and others are adopting.

### Architecture Comparison Notes

**vs. Manus:** Clawd has deeper memory and multi-model routing; Manus has better execution isolation and context engineering. Both are persistent autonomous systems, but Manus is task-scoped (completes a task then stops) while Clawd is daemon-scoped (runs continuously with a heartbeat).

**vs. OpenAI Agents SDK:** The SDK is a framework for building agents, not an agent itself. Clawd could be reimplemented on the SDK but would lose its custom tool-use loop, multi-model routing, and memory system.

**vs. Letta/MemGPT:** Letta pioneered the heartbeat concept that Clawd uses. Letta V1 is moving away from heartbeats toward direct message generation. Clawd kept heartbeats but added richer memory consolidation, knowledge graphs, and self-improvement loops that Letta lacks.

**vs. Claude Code:** Claude Code is Clawd's Opus execution path — it literally invokes Claude Code as a subprocess. Clawd wraps it with persistent identity, autonomous scheduling, and multi-model routing. They're complementary, not competing.

---

## 13. Requirements & Installation

### System Requirements

- **Python** 3.11+
- **Node.js/npm** (for Claude Code CLI)
- **Git** (for memory versioning)
- **OS:** Windows (primary), Linux/macOS compatible
- **Machine:** Clawd runs on a Razer Blade 15 laptop

### External Services Required

| Service | Purpose | How to Get |
|---------|---------|------------|
| Telegram Bot Token | User interface | [@BotFather](https://t.me/BotFather) |
| Telegram User ID | Authorization | [@userinfobot](https://t.me/userinfobot) |
| Gemini API Key | Gemini model access | [aistudio.google.com](https://aistudio.google.com) |
| Claude Code CLI | Opus path | `npm install -g @anthropic-ai/claude-code` then `claude setup-token` |

### Python Dependencies

**Core (from requirements.txt):**
```
python-telegram-bot>=21.0
aiohttp>=3.9.0
python-dotenv>=1.0.0
aiosqlite>=0.20.0
numpy>=1.26.0
pyautogui>=0.9.54
Pillow>=10.0.0
beautifulsoup4>=4.12.0
yfinance>=0.2.30
ccxt>=4.0.0
gTTS>=2.5.0
scipy>=1.12.0
sympy>=1.12.0
pandas>=2.1.0
scikit-learn>=1.4.0
statsmodels>=0.14.0
networkx>=3.2.0
sentence-transformers>=2.3.0
```

**Optional:**
- `edge-tts` — Premium TTS (falls back to gTTS/Windows SAPI)

### Installation Steps

```bash
# 1. Install Claude Code CLI
npm install -g @anthropic-ai/claude-code
claude setup-token

# 2. Install Python dependencies
cd clawd-daemon
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your TELEGRAM_BOT_TOKEN, TELEGRAM_AUTHORIZED_USERS, GEMINI_API_KEY

# 4. Create identity directory (if not exists)
mkdir -p ~/clawd/memory/items ~/clawd/memory/categories ~/clawd/skills ~/clawd/projects

# 5. Start daemon
python clawd.py

# Alternative modes:
python clawd.py --chat              # Local CLI (no Telegram)
python clawd.py --no-heartbeat      # Telegram only
python clawd.py --model gemini       # Force specific model
```

---

## 14. Configuration Reference

58 environment variables across 15 categories. Key ones:

| Variable | Default | Purpose |
|----------|---------|---------|
| `CLAWD_HOME` | `~/clawd` | Identity and memory directory |
| `DEFAULT_MODEL` | `opus` | Default LLM for all tasks |
| `HEARTBEAT_INTERVAL_SECONDS` | `600` | Autonomous wake interval (seconds) |
| `QUIET_HOURS_START` / `END` | `1` / `7` | Consolidation window (AM) |
| `CLAUDE_CODE_TIMEOUT` | `180` | Max seconds per Opus invocation |
| `CLAUDE_CODE_MAX_TURNS` | `200` | Opus session turn limit |
| `TOOL_EXECUTION_TIMEOUT` | `120` | Per-tool timeout (seconds) |
| `HITL_ENABLED` | `true` | Require Telegram approval for dangerous tools |
| `MODEL_FAILOVER_ENABLED` | `true` | Auto-switch models on failure |
| `CIRCUIT_BREAKER_THRESHOLD` | `3` | Failures before circuit opens |
| `COST_BUDGET_DAILY` | `5.00` | Daily cost budget (USD) |
| `SAFETY_MONITOR_ENABLED` | `true` | Behavioral anomaly detection |
| `MEMORY_GIT_ENABLED` | `true` | Git-based memory versioning |

Full reference: see `config.py` (322 lines, 58 configurable parameters).

---

## 15. File Map

### Core Daemon (13 files, ~5,600 lines)

| File | Lines | Purpose |
|------|-------|---------|
| `clawd.py` | 467 | Main entry point, boot sequence, crash recovery |
| `config.py` | 322 | 58 env vars, validation, safe export |
| `models.py` | 1,285 | ModelRouter, circuit breaker, dual-path LLM (Opus + Gemini) |
| `routing.py` | 167 | Task-based model selection, keyword scoring |
| `cost_tracker.py` | 655 | Per-model cost tracking, budget warnings, routing weights |
| `telegram_bot.py` | 530 | 7 commands, message debounce, photo/doc handling |
| `heartbeat.py` | 1,548 | Autonomous loop, adaptive prompt (1360 lines of logic), A/B testing |
| `health.py` | 279 | 4 subsystem checks, circuit breaker integration |
| `memory.py` | 500 | Identity assembly, CLAUDE.md generation, handoff protocol |
| `api_server.py` | 219 | HTTP API bridge (8 endpoints, bearer auth, CORS) |
| `a2a_server.py` | 188 | Agent-to-Agent protocol (JSON-RPC, agent card) |
| `mcp_server.py` | 197 | MCP server (stdio, 13 safe tools) |

### Tools Subsystem (34 files, ~17,900 lines)

| File | Lines | Tools | Purpose |
|------|-------|-------|---------|
| `__init__.py` | 576 | — | Registry, safety pipeline, dynamic selection |
| `_base.py` | 202 | — | Shared utilities, safety registry, MCP metadata |
| `system.py` | 1,408 | 11 | Orchestration, DAG execution, skill loading |
| `intelligence.py` | 1,375 | 5 | Goals, experiences, self-improvement, skill distillation |
| `execution.py` | 739 | 3 | Shell, Python eval, process management |
| `memory_tools.py` | ~200 | 2 | Hybrid search, memory update |
| `memory_items.py` | ~200 | 2 | Zettelkasten items, linking, feedback |
| `memory_categories.py` | ~200 | 1 | Topic categories |
| `memory_backend.py` | ~200 | — | SQLite/JSON dual-write |
| `memory_agent.py` | ~150 | — | Dreaming, cross-pollination |
| `sqlite_store.py` | ~150 | — | Async SQLite, FTS5, WAL |
| `embeddings.py` | ~200 | — | BGE-M3/MiniLM vector search |
| `knowledge_graph.py` | ~150 | 1 | Entity-relation network |
| `working_memory.py` | ~150 | 1 | Active cognitive state |
| `consolidation.py` | ~150 | — | 10-phase nightly pipeline |
| `dashboard.py` | ~150 | 1 | Analytics, reporting |
| `meta_agent.py` | ~150 | — | Self-evolution loop |
| `safety_monitor.py` | ~150 | — | Anomaly detection, kill switch |
| `rollback.py` | ~150 | — | Change journal, snapshots |
| `tool_factory.py` | ~150 | 2 | Runtime tool creation |
| `files.py` | 134 | 3 | File I/O with rollback |
| `web.py` | ~200 | 3 | HTTP, search, deep research |
| `git_tool.py` | 127 | 1 | Safe git operations |
| `desktop.py` | ~150 | 1 | GUI automation (pyautogui) |
| `financial.py` | ~150 | 1 | Market data (yfinance/ccxt) |
| `communication.py` | ~100 | 2 | TTS, Telegram messaging |
| `screen.py` | ~100 | 2 | Screenshot, clipboard |
| `vision.py` | ~100 | 1 | Image analysis |
| `calendar_tool.py` | ~100 | 1 | Task scheduling (cron) |
| `browser.py` | ~100 | 1 | Web browser control |
| `memory_versioning.py` | ~100 | 1 | Git time-travel |
| `semantic_segmentation.py` | ~100 | — | Episode clustering |
| `compression.py` | ~100 | — | Output compression |
| `audit.py` | ~100 | — | Audit trail |

### Mission Control (15 files)

| File | Purpose |
|------|---------|
| `src/app/page.tsx` | Dashboard (real-time health, beats, model usage) |
| `src/app/tasks/page.tsx` | Kanban task board |
| `src/app/calendar/page.tsx` | Day timeline with heartbeat schedule |
| `src/app/memory/page.tsx` | Searchable memory UI |
| `src/app/team/page.tsx` | Sub-agent overview |
| `src/app/content/page.tsx` | Content pipeline |
| `src/app/layout.tsx` | App shell with navigation |
| `src/app/globals.css` | Tailwind dark theme |
| `src/lib/api.ts` | API client for daemon bridge |
| `package.json` | Dependencies (Next.js 14, React 18, Tailwind) |
| `tsconfig.json` | TypeScript config |
| `tailwind.config.ts` | Tailwind config |
| `next.config.js` | Next.js config |
| `postcss.config.js` | PostCSS config |
| `.env.local` | API URL + token |

---

*Generated 2026-02-19. Clawd Daemon v1.0 — 23,535 lines of Python, 49 modules, 60+ tools, 7-layer memory, Opus + Gemini routing.*
