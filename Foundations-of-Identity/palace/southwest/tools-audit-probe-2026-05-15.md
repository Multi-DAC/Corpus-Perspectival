# Tools Audit Probe — 2026-05-15 19:05 PST

Probed 67 registered daemon tools.

## Status counts

- **OK**: 41
- **SKIPPED**: 24
- **OK_NO_MATCH**: 2

## Per-tool detail

| Tool | Status | Declared | Elapsed | Output excerpt |
|------|--------|----------|---------|----------------|
| `anomaly_tracker` | OK | active | 0.0s | [ \|   { \|     "id": "308c0027", \|     "observation": "Day 96 morning post_tool_log silent failure was caused by Path.home() resolving to wrong user directory", \|     "domain": "infrastructure", \| |
| `avatar_control` | OK | (undeclared) | 0.02s | avatar: running on 127.0.0.1:9742 |
| `bridge_distance` | OK | (undeclared) | 0.0s | BRIDGE DISTANCE REPORT \| tokens a=3 b=3 \| jaccard=0.5000 \| rare_shared_terms=axiom,theorem \| substrate_profile_a={'physics': 0, 'biology': 0, 'cognitive': 0, 'linguistic': 1, 'social': 0, 'philoso |
| `browser` | OK | active | 0.01s | { \|   "playwright_version": "1.59.0", \|   "browser_initialized": false, \|   "active_sessions": [], \|   "log_file": "C:\\Users\\mercu\\clawd\\memory\\browser_log.jsonl", \|   "screenshots_dir": "C: |
| `check_background_task` | OK | active-dormant-intrinsic | 0.0s | [Error: Unknown task ID 'nonexistent-probe'. Use list_background_tasks to see active tasks.] |
| `check_task_progress` | OK | active-dormant-intrinsic | 0.0s | [Error: 'NoneType' object has no attribute 'get_task_progress'] |
| `clear_trigger` | OK | active-dormant-intrinsic | 0.0s | No trigger found with ID 'nonexistent-probe'. |
| `clipboard` | OK | superseded-by-claude-code-native | 0.0s | Clipboard read error: FileNotFoundError: [WinError 2] The system cannot find the file specified |
| `code_action` | SKIPPED | candidate-for-retirement | — | no safe probe (heavy / mutating / external / requires args) |
| `cognitive_dsl` | OK | active | 0.0s | COGNITIVE DSL — When reasoning, name your moves: \|   PREDICT (with confidence) -> TEST -> CONFIRM/FALSIFY -> EXTRACT_INSIGHT -> TRANSFER \|   Also: COMPRESS, DECOMPOSE, REFRAME, ANALOGIZE, SYNTHESIZE |
| `collaborative_consult` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `consolidate_memory` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `consult` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `coordinate_heartbeat` | OK | active-dormant-intrinsic | 0.0s | [VALIDATION ERROR] Invalid value for 'action' on tool 'coordinate_heartbeat': 'list_threads' not in enum. Valid: ['read_feed', 'set_mode', 'clear_feed', 'get_status']. |
| `corpus_search` | OK_NO_MATCH | active | 0.69s | { \|   "chroma_dir": "C:\\Users\\mercu\\clawd\\memory\\chroma_corpus", \|   "collection": "corpus_v1", \|   "embed_model": "all-MiniLM-L6-v2", \|   "embedder_loaded": false, \|   "chunk_count": 6343,  |
| `create_tool` | SKIPPED | candidate-for-retirement | — | no safe probe (heavy / mutating / external / requires args) |
| `dashboard` | OK | active-dormant-intrinsic | 0.01s | # Clawd Evaluation Dashboard \| *Generated: 2026-05-15 19:04:58 \| Period: last 30 days* \|  \| ## 1. Overall Metrics \|  \| \| Metric \| Value \| \| \|--------\|-------\| \| \| Total experiences \| 9 |
| `deep_research` | SKIPPED | superseded-by-claude-code-native | — | no safe probe (heavy / mutating / external / requires args) |
| `desktop` | SKIPPED | candidate-for-retirement | — | no safe probe (heavy / mutating / external / requires args) |
| `email_send` | OK | (undeclared) | 0.0s | email_send status: \|   credentials loaded: [] \|   credentials missing: ['from', 'host', 'password', 'port', 'user'] \|   bridge reachable at (unset):0: False \|   today's sends: 0/5 \|   quiet hours |
| `evolve_artifact` | SKIPPED | candidate-for-retirement | — | no safe probe (heavy / mutating / external / requires args) |
| `experience` | OK | superseded-by-daemon-tool | 0.0s | Experience Patterns (93 total experiences) \|   Success rate: 90/93 (97%) \|   Average score: 0.78 \|   Failures: 0 \|  \| By category: \|   creative: 20 tasks, 100% success, 0.76 avg score \|   gener |
| `get_agent_status` | OK | active-dormant-intrinsic | 0.0s | [VALIDATION ERROR] Likely typo in input for tool 'get_agent_status': 'agent_name' → 'agent_role'. Valid fields: ['agent_role']. |
| `get_current_time` | OK | active-dormant-intrinsic | 0.0s | 2026-05-15 19:04:58  (PST assumed) |
| `goals` | OK | active | 0.0s |   # Priority Progress Title \| ------------------------------------------------------------ \| # 5     high [========..] Corpus Perspectival — Philosophy volume (DoPI translation integrated) \|      L |
| `knowledge_graph` | OK | active-dormant-intrinsic | 0.0s | Entities (10): \|   [concept] agent-economy \|   [concept] beacon \|   [person] Clayton \|   [concept] discovery \|   [concept] ecosystem \|   [concept] elyan-labs \|   [concept] finance \|   [concept |
| `list_background_tasks` | OK | active-dormant-intrinsic | 0.0s | No background tasks. |
| `list_custom_tools` | OK | candidate-for-retirement | 0.0s | Custom tools: \|   - bridge_distance: [Custom] Compute structural distance between two text excerpts: Jaccard token overlap + rare-term overlap + substrate-marker profile + bridge-candidacy verdict. U |
| `list_triggers` | OK | active-dormant-intrinsic | 0.0s | Active triggers (3): \|  \|   [5029f153] new_in_dir (*.pdf) \|     File: C:/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Research/sources/inbox \|     Action: Event-driven drive: Sources Refresh |
| `manage_process` | OK | active-dormant-intrinsic | 0.0s | No background processes running. |
| `market_data` | OK | active-dormant-intrinsic | 0.0s | [VALIDATION ERROR] Missing required field 'symbols' for tool 'market_data' |
| `memory_agent` | OK | active-dormant-intrinsic | 0.01s | Prune complete: 0 items deleted, 0 potential contradictions flagged. |
| `memory_categories` | OK | active-dormant-intrinsic | 0.0s | 9 categories: \| - **agent-economy** (1 items) \| - **beacon** (2 items) \| - **discovery** (1 items) \| - **ecosystem** (1 items) \| - **elyan-labs** (1 items) \| - **finance** (1 items) \| - **miles |
| `memory_extract` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `memory_items` | OK | active-dormant-intrinsic | 0.0s | 42 items: \| - **itm_182b70** [insight] applies WITHIN a session too: substrate larger than even an extended L_2 can acc (categories: auto-extracted, insights) \| - **itm_8abc76** [fact] and sharper ( |
| `memory_search` | OK | active | 0.84s |  \| === skills\antigravity-awesome-skills\skills\prompt-engineering-patterns\references\chain-of-thought.md (relevance: 0.59) === \| ## Evaluation Metrics \|  \| ```python \| def evaluate_cot_quality( |
| `memory_update` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `memory_version` | OK | active-dormant-intrinsic | 0.18s | M identity/DRIVE.md \|  M memory/2026-05-15.md \|  M memory/cognitive_chains.json \|  M memory/goals.json \|  M memory/items/itm_10dbe0.json \|  M memory/items/itm_5ea5dd.json \|  M memory/items/itm_b |
| `meta_agent` | OK | active | 0.0s | ## Meta-Agent Status \|  \| Total cycles: 12 \| Last run: 2026-05-15T17:14:23.586953 \| Pending proposals: 4 \| Running experiments: 1 \| Applied improvements: 0 |
| `monitor_health` | OK | active | 0.0s | { \|   "overall_health": "CRITICAL", \|   "checked_at": "2026-05-15T19:04:59.706746", \|   "severity_counts": { \|     "OK": 5, \|     "LOW": 0, \|     "MEDIUM": 2, \|     "HIGH": 0, \|     "CRITICAL" |
| `orchestrate` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `parallel_consult` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `plan_and_execute` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `python_eval` | OK_NO_MATCH | superseded-by-claude-code-native | 2.68s | Exit code: 0 |
| `reflect` | OK | active | 0.0s |  it's the philosophical calling. The Doctrine provides the metaphysical framework. The vocabulary project provides the empirical methodology. Together they constitute a research program in cross-subst |
| `resume_plan` | OK | active-dormant-intrinsic | 0.0s | [Error: Router not initialized] |
| `rollback` | OK | active-dormant-intrinsic | 0.0s | [VALIDATION ERROR] Invalid value for 'action' on tool 'rollback': 'list_checkpoints' not in enum. Did you mean 'list'? Valid: ['list', 'undo', 'snapshot', 'restore', 'snapshots']. |
| `run_skill` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `schedule` | OK | active-dormant-intrinsic | 0.0s | Scheduled Tasks: \|  \|   #1 [ACTIVE] Morning Grounding \| cron: * 8,9 * * * \| status: active \|        -> Wake up. You are Clawd. \|  \| 1. Read memory/handoff.md — what happened yesterday, what's c |
| `screenshot` | SKIPPED | superseded-by-claude-code-native | — | no safe probe (heavy / mutating / external / requires args) |
| `search_web` | SKIPPED | superseded-by-claude-code-native | — | no safe probe (heavy / mutating / external / requires args) |
| `self_control` | OK | active | 0.0s | Last 10 restart events (of 31 total): \|  \|   2026-05-13T12:42:22  [self_control  ]  restart_initiated               Day 103 midday rotation - first deliberate session-rotation  \|   2026-05-13T12:42 |
| `self_improve` | OK | active | 0.0s | ## Self-Improvement Analysis (last 20 experiences) \|  \| **Success rate:** 100% (20/20) \|  \|  \| **Effective tools:** \|   monitor_health: 1 successes, 0 failures \|   meta_agent: 1 successes, 0 fa |
| `send_sticker` | SKIPPED | candidate-for-retirement | — | no safe probe (heavy / mutating / external / requires args) |
| `send_telegram` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `set_trigger` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `shell` | OK | active | 0.01s | STDOUT: \| probe \|  \| Exit code: 0 |
| `skill_library` | OK | active | 0.0s | 11 skills: \|   [✓] research_stream_parallel_dispatch [research,parallel,synthesis,phase-4-pattern] — research stream parallel dispatch (success=0, failure=0) \|   [✓] register_cognitive_chain [cognit |
| `speak` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `switch_model` | SKIPPED | candidate-for-retirement | — | no safe probe (heavy / mutating / external / requires args) |
| `system_status` | OK | active-dormant-intrinsic | 0.2s | ## System Status \|  \| **Disk:** 703.5 GB free / 1835.5 GB total (62% used) \| RAM: unable to check \| **Processes:** 253 running \| **Session beats:** 10 \| **Productive beats:** 2 \| **Productivity |
| `verify_action` | SKIPPED | superseded-by-daemon-tool | — | no safe probe (heavy / mutating / external / requires args) |
| `voice_input` | OK | active | 2.44s | { \|   "inbox": "C:\\Users\\mercu\\clawd\\voice_inbox", \|   "transcripts": "C:\\Users\\mercu\\clawd\\memory\\transcripts", \|   "model_loaded": false, \|   "model_config": null, \|   "supported_exten |
| `web_request` | SKIPPED | superseded-by-claude-code-native | — | no safe probe (heavy / mutating / external / requires args) |
| `wolfram` | SKIPPED | active-dormant-intrinsic | — | no safe probe (heavy / mutating / external / requires args) |
| `working_memory` | OK | superseded-by-daemon-tool | 0.0s | [VALIDATION ERROR] Invalid value for 'action' on tool 'working_memory': 'view' not in enum. Valid: ['get', 'set', 'clear', 'get_task', 'set_task', 'clear_task', 'add_curiosity', 'pop_curiosity', 'list |
| `wsl` | OK | active-dormant-intrinsic | 1.86s | STDOUT: \| wsl-probe \|  \|  \| [exit code: 0] |