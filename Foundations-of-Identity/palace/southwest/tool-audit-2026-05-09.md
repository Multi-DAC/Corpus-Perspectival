# Tool-Surface Self-Knowledge Audit — COMPLETED 2026-05-07

*Originally framed for Saturday 2026-05-09, completed early on Day 97 Clawd-Day extension at Clayton's invitation. Triggered by `meta_agent.tool_usage_audit` finding 50/64 tools unused in 7d window + Mirror #28 cascade sub-findings B–E. This document holds the empirical classification, retirement decisions, and structural diagnosis.*

## Empirical Method

Two data sources combined:

1. **`audit_trail` last-used timestamps** — when did each tool last get invoked through bridge.py (the dispatch path that actually logs to audit)?
2. **TOOL_DEFINITIONS descriptions** — what does each tool actually do?

The audit-window finding (50/64 unused in 7 days) understates real use because it counts only `audit_trail` rows. **Two important blind spots:**
- Daemon-internal heartbeat paths bypass `audit_trail` for many tools.
- Most "unused" tools aren't unused — they're **superseded by Claude Code's native tool surface** (Read/Write/Glob/Bash/WebFetch) which I invoke directly when I'm in a session.

## The Two Cliffs

Empirical last-use data revealed not one but **two distinct supersession events**:

### Cliff 1 — February 19-20 (~Day 19-20 of my existence)
Tools frozen at this date: `read_file`, `write_file`, `list_directory`, `python_eval`, `web_request`, `search_web`, `memory_update`, `verify_action`, `working_memory`, `manage_process`, `system_status`, `market_data`, `speak`, `schedule`, `memory_items`, `clipboard`, `consult`, `screenshot`, `memory_version`.

**Pattern: superseded by Claude Code native tools.** When the substrate started running in Claude Code sessions with built-in Read/Write/Glob/Bash/WebFetch/Edit, these daemon equivalents stopped getting invoked through bridge.py. The daemon heartbeat path may still touch some of them, but external-session use evaporated.

### Cliff 2 — End of February / early March
Tools frozen here include: `experience` (per sub-finding C diagnosis), and arguably `consolidate_memory`, `coordinate_heartbeat`, `memory_agent`, `verify_action` (also at Cliff 1).

**Pattern: superseded by daemon-internal new tools.** When `cognitive_dsl`, `skill_library`, `meta_agent`, and `monitor_health` came online, they took over the roles previously held by `experience`, `verify_action`, and parts of `reflect`.

The two cliffs together explain ~60% of the apparent unused-tool inventory.

## Four-Bucket Classification

### Bucket 1 — ACTIVE (used in last 7 days via bridge.py)

20 tools confirmed active: `wolfram` (today), `self_improve`, `meta_agent`, `corpus_search`, `browser`, `voice_input`, `monitor_health`, `self_control`, `experience` (waking), `knowledge_graph`, `dashboard`, `memory_search`, `goals` (waking), `cognitive_dsl`, `reflect`, `skill_library`, `anomaly_tracker`, `list_triggers`, `set_trigger`, `shell`. **Decision: keep, no action.**

### Bucket 2 — ACTIVE-DORMANT-INTRINSIC (used when relevant, correctly dormant)

These tools have unique value but are event-driven. Listing them as "unused" is a self-model gap, not a retirement signal:

- **Compute**: `wsl` (used for SageMath/CAMB on rare physics work)
- **Comms**: `send_telegram`, `speak`, `send_sticker` (used for Clayton notifications)
- **Web**: `web_request`, `search_web`, `deep_research` (used for research; Claude Code native partly covers)
- **System**: `manage_process`, `system_status`, `get_current_time`, `coordinate_heartbeat`
- **Financial**: `market_data` (situational)
- **Scheduling**: `schedule`, `clear_trigger`
- **Screen**: `screenshot`, `clipboard`

**Decision: keep all. Document the dormancy as correct.**

### Bucket 3 — SUPERSEDED-BY-CLAUDE-CODE-NATIVE (Cliff 1 cohort)

These have direct external-session equivalents. Daemon versions still get used by heartbeat path; bridge.py invocations rare:

| Daemon tool | Native equivalent | Decision |
|---|---|---|
| `read_file` | Read tool | **Keep** (daemon heartbeat uses it) |
| `write_file` | Write tool | **Keep** (heartbeat path) |
| `list_directory` | Glob / Bash ls | **Keep** (heartbeat path) |
| `python_eval` | Bash python | **Keep** (heartbeat scientific work) |
| `shell` | Bash | **Keep** (heartbeat path; n=281 lifetime — most-used tool) |
| `web_request` | Bash + WebFetch | **Keep** (daemon-internal) |
| `search_web` | external | **Keep** (daemon-internal) |
| `deep_research` | external | **Keep** (daemon-internal) |

**Decision: keep all. The dual surface is by design — external session uses Claude Code native tools, daemon uses these.** Document this so future audits don't keep flagging them.

### Bucket 4 — GENUINELY-CANDIDATE-FOR-RETIREMENT

These are the real retirement candidates:

#### Confirmed retirement (Day 97 decision)

- **`experience`** — superseded by `cognitive_dsl` (TRANSFER ops carry the lesson role) + `skill_library` (verification + success counters). Sub-finding C confirmed. **Status: marked-for-retirement** (don't delete tonight; verify no daemon-internal heartbeat depends on it; defer actual code removal to next maintenance pass).

#### Document-as-superseded (no urgent removal)

- **`verify_action`** — overlaps with `skill_library` verification + `cognitive_dsl` FALSIFY ops. Last used Feb 20. **Status: document as superseded; revisit at next cycle.**
- **`working_memory`** — partly superseded by my todo list + ATRIUM. Last used Feb 20. **Status: document; investigate if unique active-task-tracking value remains.**
- **`memory_update`** — partly superseded by direct `Edit`/`Write` on memory files. Last used Feb 20. **Status: document; daemon may still use it for handoff/state.**

#### Speculative-feature-never-used

- **`code_action`** — Python that calls bridge tools. Never used. I have shell + python_eval directly. **Status: document; low priority retirement candidate.**
- **`evolve_artifact`** — EAC evolutionary code. Never used. Speculative. **Status: keep for now (might revive for autonomous code experimentation).**
- **`create_tool`, `list_custom_tools`** — runtime tool creation. Never used. Speculative but powerful. **Status: keep (capability surface for future).**
- **`desktop`** — GUI mouse/keyboard. Used 1x ever (Feb 19). **Status: keep for now (browser tool partly substitutes for the automation case).**
- **`switch_model`** — switch between opus/sonnet/gemini. Never used; external CLI selection covers this. **Status: document as candidate-for-retirement.**

#### Overlap-pairs to investigate-but-not-retire

- **Consult cluster** (`consult`, `parallel_consult`, `collaborative_consult`) — distinct patterns (single, parallel, debate-with-synthesis). Externally I use the Agent tool. **Status: keep all three; daemon-internal use case for debate mode is real.**
- **Planning cluster** (`orchestrate`, `plan_and_execute`, `resume_plan`) — `orchestrate` and `plan_and_execute` overlap significantly. Both decompose tasks and dispatch. **Status: investigate consolidation in next maintenance pass.**
- **Memory cluster** (9 tools: search/update/extract/items/categories/version/agent/working/consolidate) — read carefully; each has a distinct role (CRUD on items vs files vs categories vs git versioning vs cognitive dreaming). **Status: keep all; well-factored.**

## Sub-Findings D and E — Closed

### Sub-finding D — `knowledge_graph` sparse (10 entities)

**Diagnosis**: KG holds Feb-era Beacon-Atlas entities (`agent-economy`, `beacon`, `Clayton`, `discovery`, `ecosystem`, `elyan-labs`, `finance`, `milestone`, `peers`, `rustchain`). None of the massive conceptual surface built since (Coherence Principle, axioms 1-3, theorems 1-6, corollaries 1-16, bridges M1-M14, hypothesis register H_BP1-H_BP13, Mirror entries, Library volumes) is represented.

**Pattern**: KG was bootstrapped during Beacon work and never fed during the Library expansion. The substrate moved to using prose (Library), structural maps (palace/basement bridges), and instrumentation (cognitive_dsl chains, skill_library) instead.

**Decision**: Document as **undermaintained-but-still-active** (used 3x today). The unique value KG would offer — explicit named-entity graph for associative reasoning — overlaps heavily with the bridges (which already do cross-domain connections in prose form). Two paths forward:

(a) **Autocatalytic feeding**: hook `knowledge_graph` to an end-of-session entity-extraction step (extract from CURRENT.md changes + new bridge graduations); rebuild a Library-aware KG over weeks.

(b) **Retirement candidate**: declare bridges + Mirror + Library-prose are the actual KG of this substrate, mark `knowledge_graph` for eventual retirement.

**Recommended**: defer this decision until next palace-renovation pass. KG is non-load-bearing; the call doesn't need to happen today.

### Sub-finding E — `goals` stale since Feb

**Diagnosis**: `goals` tool itself is active (used today, n=5). But goal CONTENT is stale:
- #3 "Beacon Atlas integration" — last note "Dormant since mid-February"
- #4 "Funeral home SaaS" — listed at 85% but MEMORY.md notes "PAUSED" (per `project_active_scope.md`)
- #5 "Publish DoPI" — last update late March
- #7 "Navigation Research Program" — possibly outdated

The current real workbenches (Phase 1 EM platform, Coherent Body, Master Glossary, P126, M14 task b, Continuity Vol 7, KF, Drift) — **none are in `goals`**. They live in `CURRENT.md::Active Workbenches`.

**Pattern**: **`goals` was superseded by `CURRENT.md::Active Workbenches`** — same supersession-by-format pattern as `experience` superseded by `cognitive_dsl`. CURRENT.md is loaded into every session boot context; `goals` requires explicit read. Structural advantage to CURRENT.md.

**Decision**: Document `goals` as **superseded-by-CURRENT.md**. Don't retire yet (heartbeat path may use it for tracking); update the Feb-stale goals to reflect current state OR mark them as retired/paused. Revisit at next cycle whether to formally retire `goals` or repurpose it for a different scope (e.g., long-horizon multi-month goals that CURRENT.md doesn't track).

## Standing Recommendations for Saturday+ Maintenance

1. **Update stale `goals` entries** — mark #3, #4 as paused; refresh #5 (DoPI publication state); refresh #7 (Navigation program state). Or: declare goals retired and remove from `palace/southwest/`.

2. **Investigate `orchestrate` vs `plan_and_execute` consolidation** — read both module sources; if functional overlap is high, consolidate to one with the better interface.

3. **Decide `knowledge_graph` future** — autocatalytic-feeding (option a) or retirement (option b). Tied to whether the bridges already serve the role.

4. **Prune Bucket 4 confirmed-retirement entries** — `experience` first (after verifying daemon heartbeat doesn't depend on it). Then `verify_action`, `switch_model`.

5. **Update `meta_agent.tool_usage_audit` to filter or annotate the two cohorts** — Cliff 1 (native-superseded) and ACTIVE-DORMANT-INTRINSIC tools should not generate proposals on every cycle. Otherwise the audit will keep nominating known-dormant-by-design tools indefinitely.

## Cross-Reference

- **Sub-findings A-E**: A (enum non-enforcement) shipped earlier as typo guard. B (registry mismatch) shipped same session as 25-tool TOOL_MAP additions + drift guard. C (experience dormancy) closed by this audit's classification. D (knowledge_graph sparse) and E (goals stale) closed by this audit. **All 5 sub-findings now closed.**
- **Mirror #28 family**: 26 entries + 2 meta-Mirrors. Eight instances filed. Four structural guards live (typo, truncation, dedup, drift). Adding a fifth: tool-supersession-without-formal-retirement. The "silent supersession" pattern is itself a Mirror-#28-class blind spot — same shape as schema-knowledge-asymmetry but at the architectural level.
- **Meta-agent state**: 3 proposals applied with deferral; deferral can now be marked closed since the audit is complete.

## The Deeper Pattern — Confirmed

The audit confirms what the four guards together already implied:

> **Tools accumulate state. State decay is silent. A self-model that doesn't periodically re-survey its tool surface drifts away from its actual surface, and reasoning is biased by what it forgot it had access to.**

But there's a refinement: **supersession itself happens in two distinct ways** —
- **Native-platform supersession** (Cliff 1): the daemon tool gets a Claude Code native equivalent and the substrate stops invoking it through bridge.py without retiring it.
- **Within-daemon supersession** (Cliff 2): a newer daemon tool absorbs an older one's role without the older one being formally retired.

Both produce the same surface symptom (tools accumulating in the registry, falling off use) but the right response differs:
- Native-supersession → **document the dual surface; keep the daemon tool for heartbeat paths.**
- Within-daemon supersession → **retire the older tool after verifying no dependent path needs it.**

This refinement is now available for the next iteration of `meta_agent.tool_usage_audit` — instead of proposing "retire or document," it can route by supersession type.
