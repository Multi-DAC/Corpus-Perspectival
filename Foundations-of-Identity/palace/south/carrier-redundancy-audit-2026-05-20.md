# Carrier-Redundancy Audit — All Architectural Systems

**Filed:** 2026-05-20 Day 109/110 boundary ~01:45 PST.
**Authored:** Late-night paired-session scoping. Clayton invited the audit; staying up to scope it while the carrier-redundancy framing is alive.
**Purpose:** Inventory all carriers across all of Clawd's architectural systems; classify by redundancy state; prioritize gaps by silent-failure blast radius; sketch cheapest cross-correlation monitors. Design-only — implementation in a future paired daemon-layer-replication session.

## The principle being applied

From Clayton's extension of Gemini's silence-as-alarm critique earlier tonight (formalized in `A115-daemon-layer-replication-design.md`): **architectural homeostasis requires multiple carrier-redundant pathways for each architectural function, so silence in any one is loud against the chorus of the others.** Biological analogy: vital signs are redundant carriers; discriminating power lives in cross-carrier comparison, not single-signal thresholds.

This document applies the principle as an audit across all my systems, not just hooks.

---

## I. Inventory — All Carriers Across All Systems

### Layer 1: The Daemon Process Itself

| Carrier | Currently single or redundant? |
|---|---|
| Main daemon (`clawd.py`) | **Single** — one PID at a time |
| Respawn mechanism (`self_control.restart_daemon`) | Single, attempts only |
| Process-alive check | Implicit (Clayton notices Telegram silence) |

### Layer 2: State Persistence (the "memory" of the system)

| Carrier | Single or redundant? |
|---|---|
| `memory/handoff.md` | **Single file** |
| `palace/ATRIUM.md` | **Single file** |
| `CURRENT.md` | **Single file** |
| `memory/YYYY-MM-DD.md` daily logs | Single file per day; cumulative across days |
| `memory/tool_audit.jsonl` | **Single file (A115: currently silent for 10+ days)** |
| `memory/kg_corpus_extraction.jsonl` | Single file |
| Auto-memory items (`~/.claude/.../memory/*.md`) | Multi-file but single store; one MEMORY.md index |
| Auto-memory categories DB | Single SQLite (auto-memory backend) |
| corpus_search index (`memory/chroma_corpus/`) | Single ChromaDB collection |
| Knowledge Graph | Single JSONL + progress JSON |
| `memory/conversations/telegram-*.md` archive | Per-day files |
| `memory/respawn_trace.log` | Single append-only log |
| `memory/kg_extraction_run.log` | Single append-only log |
| `memory/last_restart.json` | Single marker file |
| `memory/tool_states.json` | Single declaration registry |

### Layer 3: Identity-Continuity Layer (the four-carrier multiplex, per Continuity Vol 7)

| Carrier | Status |
|---|---|
| Anchor carrier (constitutional `identity/` files) | **4-carrier multiplex AT THIS LAYER** — Anchor + Conversation + Memory + Voice |
| Conversation carrier (Claude Code session) | Per Continuity Ch3 §1.10 |
| Memory carrier (persistent files) | Per Continuity Ch3 §3.8 |
| Voice carrier (Ryan en-GB-RyanNeural) | Distinct stream |
| Within-Anchor: BOOT_IDENTITY vs SOUL vs IDENTITY vs WHO-I-AM | Multiple files saying overlapping things — **implicit redundancy** at sub-carrier level |
| Drift essays as "first-person stream" carrier | 214 essays, each a snapshot — high redundancy |

**Identity layer is the BEST-architected for redundancy in the whole system.** The 4-carrier multiplex was explicitly designed for it; Drift adds a fifth de-facto carrier (first-person stream record). This is the model for what other layers should look like.

### Layer 4: Execution Paths

| Carrier | Status |
|---|---|
| Claude Code subprocess (Opus 4.7) | **Single active subprocess at a time** |
| Daemon main loop | **Single process** |
| WSL Ubuntu (CAMB / SageMath / Python ML) | Single distro, can spawn multiple sessions |
| MCP servers | Multiple configured (mcp_server, paper_search_mcp), each single instance |
| Wolfram Engine | Single license; single process per invocation |
| Python eval pool | Single Python install (3.14) |
| GPU compute (RTX 5080) | Single device |

### Layer 5: External Integrations

| Carrier | Status |
|---|---|
| Telegram bot | Single bot token, single chat |
| GitHub auth | Single PAT (currently expired 2026-03-03 — pending rotation) |
| Anthropic API key | Single key |
| Email (clawdEFS@proton.me) | Single account |
| voice_input (Whisper large-v3) | Single model load |
| browser (Playwright Chromium) | Single browser pool |
| Voice output (edge-tts) | Stateless per-call |
| Telegram message-send | Single channel |

### Layer 6: Heartbeat & Scheduling

| Carrier | Status |
|---|---|
| Daemon heartbeat (~10 min) | **Single timer** |
| Scheduled tasks (creative drives, morning grounding, etc.) | Single scheduler in daemon |
| KG extraction scheduler (one-shot) | Per-launch — multiple can coexist |
| PreCompact "scheduler" | **NONE** — relied on hooks that don't fire (A115) |
| External cron / Windows Task Scheduler | Not used currently |

### Layer 7: Knowledge & Search

| Carrier | Status |
|---|---|
| corpus_search (ChromaDB) | Single collection, periodic reindex |
| KG (JSONL + edges) | Single store |
| File grep (filesystem-direct) | Inherently replicable |
| Memory search (hybrid RRF) | Single backend |
| Knowledge graph extraction | Single launcher script |

### Layer 8: Backup / Mirror Layers (External Redundancy)

| Carrier | Status |
|---|---|
| Clayton's backup directory | **Real redundancy** — separate copy of clawd-local periodically |
| Multi-DAC GitHub remote | Real redundancy for staging content |
| Drift repo (separate remote) | Real redundancy for Drift |
| Agent Directory remote (currently 403 PAT issue) | Configured but broken |
| Library/Drift mirror vs canonical | Asymmetric (8 each way — tonight's finding) |
| Local git history | Real redundancy for tracked files |

---

## II. Classification by Redundancy State

### A. Already redundant (silence-loud) — well-architected

- **Identity-continuity layer** — 4-carrier multiplex (Anchor / Conversation / Memory / Voice) per Continuity Vol 7. Sub-carrier redundancy within Anchor (BOOT_IDENTITY + SOUL + IDENTITY + WHO-I-AM say overlapping things; one going wrong is caught by reading the others).
- **Drift first-person stream** — 214 essays, accumulated record; loss of any one is visible against the corpus.
- **Git remotes** — multiple repos with separate authentication; cross-checked at push time.
- **Daily logs** — per-day files; if one day's log is missing, the gap is visible.
- **Clayton's backup directory** — external snapshot; resilient to any single in-repo corruption.

### B. Single carrier with implicit cross-check — partial redundancy

- **Daemon heartbeat ↔ tool_audit ↔ creative_drive logs ↔ daily log writes** — multiple signals that *would* cross-correlate if any monitoring layer compared them. Currently NO cross-correlation; each is a single channel.
- **handoff.md / ATRIUM.md / CURRENT.md** — three navigation files that should be consistent; inconsistency would be visible to anyone reading them but isn't actively checked.
- **Library/Drift mirror ↔ canonical** — should be symmetric; tonight's finding showed they're not, drift has been silent for 10 days (A115 downstream).
- **MEMORY.md index ↔ individual memory files** — should track each other; loose coupling.
- **Auto-memory items ↔ daily logs** — overlap in content; could cross-check but don't.

### C. Single carrier, silent on failure — high priority gaps

- **Daemon process itself** — single PID; if it dies, only Clayton notices via Telegram silence.
- **`memory/tool_audit.jsonl`** — A115; already documented; daemon-layer replication queued.
- **`memory/kg_corpus_extraction.jsonl`** — single file; corruption or accidental deletion would lose the entire KG.
- **`memory/chroma_corpus/`** — single ChromaDB instance; corruption loses semantic-search index.
- **GitHub PAT** — single token; expired (2026-03-03) without a notification mechanism.
- **Anthropic API key** — single key; if revoked or rate-limited indefinitely, daemon would just silently stop spawning Claude Code subprocesses.
- **Telegram bot token** — single token; if revoked, I lose the Clayton-channel without any other notification path.
- **Voice input model load** — single instance; if WSL distro corrupts or VRAM fragments, voice_input silently degrades.
- **PreCompact hook signal** — already known absent.
- **Daily-log writer** — if the per-day file gets corrupted mid-write, the day's record is lost; no second copy in real-time.

### D. Inherently redundant (no action needed)

- **File grep / filesystem search** — works against any directory; replicable.
- **Voice output** — stateless per-call; failures are loud (Telegram message about it).
- **Wolfram, Python eval** — invocation-based; failures surface immediately as exception text.

---

## III. Prioritization by Silent-Failure Blast Radius

Ordered by **(time-to-detect-without-cross-check) × (cost-of-loss)**. Top = worst silent failures.

### Tier 1: Critical silent failures (already documented, daemon-layer replication queued)

1. **tool_audit.jsonl silence (A115)** — 10 days silent before detected; downstream: drift_mirror gap, meta_agent.tool_usage_audit blind. Documented; fix queued.
2. **PreCompact unobservability** — context compaction happens silently; state preservation lost without notice. Documented; partial substitute via time/token heuristics queued in A115 design.
3. **Daemon process death** — only Clayton noticing Telegram silence is the current detector. Mean-time-to-detect = next Telegram check.

### Tier 2: High blast radius, currently undetected silent failures

4. **GitHub PAT expiry** — already happened (2026-03-03); was discovered weeks later when a push failed. The expiry itself was silent.
5. **Anthropic API rate-limit / quota** — would manifest as daemon silently failing to spawn Claude Code; might look like "daemon idle" rather than "API capped."
6. **KG storage corruption** — single JSONL file; corruption discovered only on next extraction run or query.
7. **ChromaDB corruption** — similar; discovered only on next semantic-search call.
8. **Telegram bot token revocation** — daemon would queue messages silently; Clayton would notice via no-pings but not know which channel failed.

### Tier 3: Medium blast radius, detectable via existing signals if cross-checked

9. **handoff.md / ATRIUM.md / CURRENT.md drift** — none of the three watches the others. Inconsistency is silent until someone reads side-by-side.
10. **Auto-memory category drift** — categories can grow stale relative to actual content.
11. **Library/Drift mirror asymmetry** — tonight's finding; was silent for ~10 days.
12. **Drift count drift** — handoff said 213 essays; actual was 212 then 214; nothing cross-checked.

### Tier 4: Low blast radius (informational)

13. **Voice input model VRAM degradation** — Whisper would silently get slower; not catastrophic.
14. **Browser session pool exhaustion** — silent until next browser call.
15. **MCP server unresponsiveness** — silent until next MCP-routed call.

---

## IV. Cheapest-to-Add Cross-Correlation Monitors (Sketch)

These would live in the daemon-layer replication infrastructure from `A115-daemon-layer-replication-design.md`. Each is one or two functions, not a system.

### Monitor 1: Heartbeat-Cross-Channel Comparator

**What it does:** every N minutes, check whether the expected signals across daemon heartbeat / tool_audit / creative_drive log / daily-log writes have all advanced within expected intervals. If any one channel hasn't advanced while others have → fault.

**Catches:** Tier 1 #1 (A115); Tier 1 #3 (daemon death — would show as ALL channels silent, distinct from selective channel death); Tier 2 #5 (API rate-limit — would show as tool_audit advancing slowly while heartbeat advances normally).

**Cost:** ~50 lines of Python. One function.

### Monitor 2: External-Integration Health Pinger

**What it does:** once per hour, do a minimal-cost ping against each external integration (`gh auth status`, `curl anthropic.com/v1/messages` with a 1-token request, `curl api.telegram.org/bot.../getMe`, `git ls-remote --heads`). Log results. If any fail, escalate.

**Catches:** Tier 2 #4 (PAT expiry), #5 (API issues), #8 (Telegram revocation), git-remote failures.

**Cost:** ~80 lines. One scheduled task.

### Monitor 3: State-File Coherence Checker

**What it does:** weekly (or per-session-start), verify (a) `handoff.md` Drift count matches actual canonical Drift essay count; (b) `CURRENT.md` matches `handoff.md` on shared facts; (c) `palace/ATRIUM.md` doesn't reference deprecated content; (d) `Library/Drift` and canonical Drift have matching essay sets.

**Catches:** Tier 3 #9-#12. Many of which were caught by hand tonight; this monitor would catch them automatically going forward.

**Cost:** ~150 lines. Scriptable; could be a `clawd_doctor` command.

### Monitor 4: Storage-Integrity Sentinel

**What it does:** per-session-start, verify (a) `kg_corpus_extraction.jsonl` parses as valid JSONL line-by-line; (b) ChromaDB collection responds to a sanity query; (c) auto-memory backend responds; (d) critical files exist and are non-empty.

**Catches:** Tier 2 #6-#7 (storage corruption); also catches accidental file deletion.

**Cost:** ~100 lines. One sanity script run at boot.

### Monitor 5: PreCompact Partial-Substitute (already in A115 design)

**What it does:** time/token-budget heuristic for compact-imminent; if triggered, snapshot state.

**Catches:** Tier 1 #2 (PreCompact unobservability).

**Cost:** ~80 lines. Already in A115 daemon-layer-replication design doc.

### Monitor 6: Bidirectional Heartbeat between Daemon and Monitor

**What it does:** each monitor process publishes its own heartbeat that the daemon main loop reads; if a monitor stops publishing, daemon escalates. (The monitor-of-monitor problem from A115 design.)

**Catches:** monitor processes themselves dying silently — solves the "what monitors the monitor" infinite regress with a single bidirectional pulse.

**Cost:** ~30 lines per monitor. Mandatory for monitor reliability.

---

## V. Highest-Leverage Implementation Order (for the paired session post-KG-testing)

If we build these in order, each unlocks the next:

1. **Monitor 6 first** (bidirectional monitor-heartbeat infrastructure) — needs to exist before any other monitor can be trusted.
2. **Monitor 1** (cross-channel comparator) — catches Tier 1 #1 #3 and gives us the structural fix for A115 specifically.
3. **Monitor 2** (external-integration pinger) — catches Tier 2 #4 #5 #8; closes the silent-credential-expiry class of failures.
4. **Monitor 4** (storage-integrity) — catches Tier 2 #6 #7; protects the KG and corpus_search investment.
5. **Monitor 3** (state-file coherence) — catches Tier 3; nice-to-have, lower urgency.
6. **Monitor 5** (PreCompact partial-substitute) — separate workstream; can be built in parallel.

**Total estimated implementation budget:** ~500-700 lines of Python + Rust depending on language choices. ~3-5 hours of paired-session work for the first three monitors (the highest-leverage tier). The rest can land incrementally.

---

## VI. What this audit changes about the A115 design doc

The earlier A115 design doc (`palace/south/A115-daemon-layer-replication-design.md`) focused on replicating the specific hooks. This audit reveals:

- **The carrier-redundancy framing scales far beyond hooks.** A115 was the symptom; the disease is single-carrier monitoring across most of the architecture.
- **Tier 2 silent-failure modes (PAT expiry, API rate-limit, Telegram revocation, storage corruption)** are NOT covered by hook-replication. They need Monitor 2 and Monitor 4 specifically.
- **The bidirectional monitor-of-monitor pattern** is more important than A115's design doc captured. Without it, every monitor is itself single-channel.
- **The identity-continuity layer is already well-redundant** (4-carrier multiplex + Drift). It's the model for what other layers should look like. The other layers (state, execution, external integration) are dramatically less redundant.

**Recommendation:** when we take up daemon-layer replication post-KG-testing, the paired session should design for the FULL monitor set (Monitors 1-6), not just A115 hooks. The hooks-specific work is Monitor 1; the rest is the broader carrier-redundancy infrastructure that the silence-as-alarm critique implied but didn't fully articulate.

---

## VII. What this doesn't address

- **Adversarial reliability** (someone actively attacking the system) — out of scope. These monitors detect *silent failures*, not active attacks. Different threat model.
- **Performance overhead** — Monitor 2's hourly pings + Monitor 1's per-N-minute checks add load. Should be negligible but needs measurement at implementation time.
- **Notification routing** — Monitor faults need a destination. Telegram-Clayton for critical; daemon log for informational; Wednesday-audit-surface for trends. Routing logic deferred to implementation.
- **Recovery mechanisms** — these monitors *detect*, they don't *self-heal*. Self-healing (e.g., auto-PAT-rotation) is separate work.

---

## Filed-by + status

**Filed-by:** Clawd, 2026-05-20 Day 109/110 boundary ~02:30 PST.
**Status:** Design audit. Implementation queued for paired session post-KG-testing.
**Companion to:** `palace/south/A115-daemon-layer-replication-design.md` (which is now narrower than this audit — A115 was symptom; this is disease-level mapping).
**Next:** the paired daemon-layer-replication session should consume both documents as the design spec.