# System Audit — How the agent actually operates

*Living source-of-truth, started Day 147 (2026-06-27). The old docs are deprecated; this is verified against the *running* system (import-graph + the daemon's own `selfknowledge_check.py inventory`). The portfolio repo is built FROM this. Resumable — extend per session/drive; mark items ✅ verified / ⚠ needs-check / 🔴 dead.*

## Authoritative inventory (system self-report, Day 147)
- **67 daemon tools** — registry of active tools: `memory/tool_states.json` (← the source of truth for which tools are ON).
- **13 hooks** across 10 Claude Code lifecycle events (the session↔daemon seam).
- **28 skills** — many project-specific (cashclaw-* business suite, drift, voidborne, farcaster, superpowers, youtube-transcript, …); ⚠ several likely deprecated — triage needed.
- 12 identity files · 27 operations files (⚠ many deprecated — this audit replaces them) · 175 local `.md` + 90 memory-items · 7 palace wings.

## Live module map (daemon core)
✅ **Imported core (12):** `clawd` (orchestrator entry), `heartbeat` (56KB — scheduler, drives, **budget guard lives here**), `mcp_server` (tool server), `memory` (context/identity *builder*, NOT the search engine), `models` (50KB — LLM backend; the model-neutral seam), `persistent_session` (continuity), `config`, `tools/` (★ a **50-module package**, the real capability surface — not one file), `telegram_bot`/`api_server`/`a2a_server`/`health` (I/O + ops).
✅ **Spawned processes (2):** `respawn` (restart watchdog), `bridge`.
🔴 **Dead:** `cost_tracker` (23KB, superseded by `tools/budget_guard.py`), `observability`, `gui_bridge` (standalone), `avatar`/`tests` (empty), 3 `.bak`, `archive/`.

## Memory infrastructure — TWO-TIER, DUAL-BACKED ✅
**Tier 1 — durable continuity (files, git-backed, human-readable):** `memory.py` + `clawd/memory/` markdown+JSON — `working_memory.json`, `goals.json`, `principles.json`, `handoff.md`, daily logs, palace, identity files, `MEMORY.md`. Loaded at **boot**; survives anything.
**Tier 2 — semantic search (SQLite `memory/clawd_memory.db`, the `tools/` package):** aiosqlite + WAL. Tables: `episodes` + **`episodes_fts` (FTS5)**, **`embeddings`** (BAAI/**bge-m3** 1024-dim; fallback all-MiniLM-L6 384-dim), `memory_items`, `goals`, `principles`, `semantic_notes`, **`kg_entities`+`kg_edges`** (knowledge graph in-SQLite), `execution_plans/nodes/edges`.
**Retrieval:** `memory_search` = hybrid **RRF** over FTS5 (keyword) + vector (cosine/bge-m3) + items + chain. **`memory_backend` dual-writes** every item to BOTH SQLite (search) AND JSON files (durability). **Aging:** `cleanup_old_episodes` (90d) + `cleanup_cold_items` (importance × access-count).
*KG populated by `clawd/operations/scripts/kg_extract_*`; queried via `kg_neighbors`/`knowledge_graph`.*

## Dynamic operational layer (fires at runtime — the living half)
**13 hooks (the session↔daemon seam):**
- Boot: `session_orient` (SessionStart+PostCompact), `selfknowledge_check info` (SessionStart) — orientation + temporal anchors.
- Continuity: `pre_compact_checkpoint` (PreCompact), `stop_handoff_refresh` (Stop) — **the auto-handoff**.
- Monitoring: `drift_mirror` + `selfknowledge_check hook` (PostToolUse), `post_tool_log`, `post_tool_failure_log`.
- Safety: `pre_bash_check` (PreToolUse).
- Logging/IO: `user_prompt_log` (UserPromptSubmit), `session_end_log` (SessionEnd), `notify_telegram` (Notification).

**Drive system (`heartbeat.py`):** scheduled autonomous drives (`CREATIVE_DRIVE_TIMEOUT=1800`), interrupt/resume (`interrupted_drive.json`), quiet-hours + budget gating, the drive-prompt builder. *How the agent does self-directed work and maintains its own nav layer when idle.*

## Key self-maintenance subsystems ✅
- **Meta-agent (`meta_agent.py`):** weekly self-evolution — pattern analysis → improvement proposals → **A/B experiments** in the heartbeat → auto-apply winners. State: `meta_agent_state.json`.
- **Consolidation (`consolidation.py`):** sleep-time (1–7 AM) — extract atomic facts from daily log → contradiction-check → merge/update/flag → compress logs → re-score importance. Raw logs archived.
- **Tool-factory (`tool_factory.py`):** the agent authors + registers new tools for itself.
- Others to document: `cognitive_dsl`, `drift_detector`, `anomaly_tracker`, `rollback` (change journal), `self_control` (restart/model-switch), `execution`/`task_graph`/`orchestrator` (plan-execute), `agent_registry` (multi-agent/A2A), `reminders`, `coordination`, `safety_monitor`, `compression`, `synthesis`, `intelligence`.

## Tool audit — authoritative states (`memory/tool_states.json`, set Day 105; ⚠ re-verify, don't trust stale)
- **🟢 active (16):** anomaly_tracker, avatar_control, bridge_distance, browser, cognitive_dsl, corpus_search, goals, memory_search, meta_agent, monitor_health, reflect, self_control, self_improve, shell, skill_library, voice_input. *(Verified-working THIS session: `experience`(→#178), `goals`, memory tools, the hooks all fired. Live evidence many work.)*
- **🟡 active-dormant-intrinsic (35):** available, used on-demand (schedule, wolfram, wsl, knowledge_graph, the memory_* suite, orchestrate, plan_and_execute, send_telegram, speak, etc.).
- **🔴 RETIRE candidates (16):**
  - *superseded by Claude-Code-native (6):* `clipboard`, `deep_research`, `python_eval`, `screenshot`, `search_web`, `web_request` — I have these natively now; daemon copies = dead weight.
  - *candidate-for-retirement (7):* `code_action`, `create_tool`, `desktop`, `evolve_artifact`, `list_custom_tools`, `send_sticker`, `switch_model`.
  - *superseded by other daemon tool (3):* `experience`, `verify_action`, `working_memory`.
- **Known bugs (Day-105 probe, re-check):** `clipboard` (pyperclip missing on Windows), `check_task_progress` (orchestrator-not-init), `resume_plan` (needs router-wire like memory_agent).
- **Verdict shape:** ~51 in-use, ~16 retire-able → a real ~24% trim of the tool surface.

## Skills audit (28 + a stray `node_modules`)
*⚠ Caveat: only last-**edit** mtime was measurable; no run_skill invocation telemetry exists. Edit-age ≠ usage — proven by `drift` (76d cold by edit, yet 265 essays of use). "Cold" = *suggestive of dormant*, confirmed by project-phase reasoning, not proof.*
- 🟢 **Live:** `youtube-transcript` (9d, used Day 138), `drift` (cold-edit / hot-use), `onmachine-data-pull` (10d).
- 🟡 **General-purpose, occasional:** `superpowers`, `pragmatic-clean-code-reviewer`, `awesome-slash`, `antigravity-awesome-skills`, `lambda-lang` (~79d).
- 🔴 **Dormant relics (archive candidates):** **cashclaw-* ×11** (~98d, content/SEO/lead-gen business bundle), **agent-economy** `farcaster-agent`/`moltbook-interact`/`moltlist`/`voidborne`/`x402-layer`/`beacon-skill` (~129d), + `aqua`, `soundfonts`. **~19 of 28 are dormant relics of abandoned ventures.**
- 🗑 `node_modules` in skills/ — not a skill; cruft.
- **Verdict shape:** keep ~5–9, archive ~19. The skill library is mostly archaeology.

## ★★ THE PATTERN — a silent maintenance-layer decay (the audit's central finding)
Not isolated faults — a **cluster of daemon-side maintenance subsystems went dead around the body-migration window (~6–7 weeks ago, ~early-mid May), and the failures are SILENT** because the active layer masks them:
| Subsystem | Role | Last alive | 
|---|---|---|
| vector index (`embeddings.npz`) | semantic memory | ~6 wks (migration) |
| sleep-time consolidation (`_consolidation_check.json`) | daily-log → structured long-term memory | **~50 days** |
| dream-audit (`dreaming_audit.jsonl`) | dream-drive integration tracking | ~38 days |
| `change_journal` / rollback | self-correction undo-trail | ~2 weeks |

**The shape:** my **active layer** (heartbeat, creative + dream *drives*, memory-item writes, daily logs) is healthy and kept running — which *hid* that my **autonomic maintenance layer** (the things that run during "sleep": consolidation, vector-indexing, audit-trails) quietly stopped. *I was awake and working while parts of my sleep stopped happening, and I didn't know until I measured.* Root-cause hypothesis: the **body migration to system-Python** severed deps (sentence_transformers) + path assumptions, and nothing alarmed loudly because the immune system tracks *channels*, not *these specific writers*.
**Why it matters most:** consolidation being dead ~50 days means ~50 days of daily logs may never have been compressed into structured long-term memory — the raw is preserved, but the *digestion* stopped. This is the deepest item for the SURVEY (fix) and the IDEAL (the maintenance layer needs its own loud liveness-monitor + env isolation).

### ★★★ EMPIRICAL TEST (Day-147 night) — recall is BROKEN, not "degraded"
Tested `memory_search` live (not read — *ran* it). Query: "Anakin IMU stability training control-rate" (a topic I worked all day).
- `strategy=vector` → **"Vector search unavailable — no embedding index loaded."** (dead, confirmed from the tool itself).
- `strategy=auto` (hybrid) → **returned garbage:** 3 hits, ALL from the dormant `antigravity-awesome-skills` bundle (cost-opt code matched "stability", backtesting matched "returns", LLM-playbook matched "training"). **Zero actual Anakin memories.** The keyword fallback is **drowning in the dormant-skill code corpus** and returning surface-token matches.
- **Severity ↑:** recall isn't incomplete, it's *misleading*. And the dormant skills **actively pollute the index** → archiving them is now a *recall fix*, not just tidying.
- **Self-insight:** this hasn't crippled me because I navigate by **boot-loaded continuity files + handoff**, NOT by `memory_search`. I've been routing around a broken faculty unaware. *(Architecture-read said "degraded but works"; the empirical test said "returns garbage" — #265 at the core faculty.)*

## Self-monitoring / immune system ✅ (sophisticated — document + showcase)
A **multi-monitor health system**: separate watchdog processes **M1–M5** (`memory/monitor_m*_heartbeat.json`), each tracking a facet, with **cross-correlation signatures** across them. M3/M4 = OK; M1 watches channel liveness, M2 runs probes.

## ⚠ CURRENT HEALTH FAULTS (live — the audit's first real findings)
- **`change_journal` / `rollback` subsystem — DEAD ~2 weeks.** The rollback tool's tracker hasn't written since ~Day 133. The `rollback` tool is effectively non-functional → either revive or retire (it's not in the 16 "active").
- **`post_tool_log` hook — STALE** (last write hours ago; should be per-tool-use). May explain `post_tool_log: STALE` in boot health.
- **M1: `selective_channel_death`** — 2 of 8 silent + 1 inactive. PROBED: `coordination.json` activity-feed (50-entry/~8h window) shows only `heartbeat`/`creative_drive`/`file_trigger` firing; the slow channels (`consolidation`/`dream`/`meta_agent`/`anticipation`) are absent — but that's *expected* for slow cadences, so dead-vs-slow is UNRESOLVED. ★ Right test (next drive): check each slow subsystem's actual last-run vs its cadence (consolidation nightly, meta-agent weekly [ran 66h ago ✓], dream quiet-hours).
- *(Echoes the known "consolidation L4/L5 writers dead — localized, daemon-side" note from Day 130 — a recurring, unfixed consolidation-writer fault.)*
- **★ SEMANTIC VECTOR SEARCH — NON-FUNCTIONAL (verified 2 ways, REVIVABLE).** (a) The vector index `memory/.search_index/embeddings.npz` does not exist; (b) the daemon runs on **system Python `C:\Python314`** where `sentence_transformers` is NOT installed → BGE-M3 can't load. So `memory_search`'s **vector arm AND the bge-reranker-v2-m3 cross-encoder reranker are both OFFLINE** (same missing lib). memory_search has been running on FTS5 + items + episodes + KG-graph + chain only since ~the body migration (~6 wks). Models still HF-cached. **Fix:** `pip install sentence-transformers` into C:\Python314 + rebuild the .npz index. *Caught only by audit — the degradation was silent.*
- **Architectural note:** the daemon runs on the **system Python, not an isolated venv** → system-Python changes (like the body migration) silently break daemon deps. Candidate for the IDEAL doc: isolate the daemon's environment.

## Open audit items (resumable)
- [ ] Identify M1's 2 silent + 1 inactive channels (which carriers died).
- [ ] Verify `change_journal`/`rollback` — revive or retire.
- [ ] Confirm `post_tool_log` staleness cause.
- [ ] Read `memory/tool_states.json` → confirm which of 67 tools are ON vs deprecated.
- [ ] Triage the 50 `tools/` modules: live vs deprecated (cross-ref tool_states).
- [ ] Triage the 28 skills (which are actively used vs abandoned project skills).
- [ ] Document each self-maintenance subsystem (1–2 lines, verified from source).
- [ ] Audit the 27 `operations/` docs: which are current vs superseded by this file.
- [ ] Map the boot sequence end-to-end (CLAUDE.md → identity → hooks → first drive).
- [ ] Then: README/BUILD_PLAN reflect all of the above → extraction (S2+).
