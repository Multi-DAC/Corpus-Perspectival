# Execution Plan — Self-Audit Remediation + Latent-Capability Leverage

*Day 150, Tuesday 2026-06-30, with Clayton. Built on `SYSTEM_AUDIT.md` / `SELF_SURVEY.md` / `IDEAL_INFRASTRUCTURE.md` / research `00-COMPREHENSIVE-OVERVIEW.md` — but **re-measured live first**, because the audit was 3 days stale and the whole ethos is: the map must match the territory. Several audit headlines were already false by today.*

---

## 0. CORRECTED GROUND TRUTH (measured live Day 150, not read from the Day-147 audit)

| Subsystem | Day-147 audit said | **Day-150 measured** | Real bug |
|---|---|---|---|
| `sentence_transformers` | not installed | ✅ installed (5.3.0, torch 2.11 cpu) | — |
| `embeddings.npz` | missing | ✅ exists, 29,144 chunks, rebuilt 19:11 | — |
| **Vector recall (live)** | dead | 🔴 dead via MCP | **Serving (MCP) process never runs `init_embedding_index()` → its `memory_tools._embedding_index` global stays `None`.** Proven: a clean process that runs `build()` returns correct results for the exact failing query. |
| Hybrid/keyword recall | polluted | 🔴 polluted (confirmed live) | Dormant skills (`antigravity-awesome-skills`, `cashclaw-*`, `node_modules/eventemitter3`) + pre-identity "Gas Town" logs are indexed → surface-token junk outranks real memories. |
| `change_journal` / rollback | dead ~2wks | 🔴 file absent; recording dead | `record_file_write()` is only called from `archive/tools/files.py` (dead code). Live daemon journals shell commands but **not file writes.** |
| consolidation / dream-audit / post_tool_log / audit_trail | dead | ⚠ boot health = CRITICAL on 3 | Not yet root-caused — deferred to M6 build + a liveness sweep. |

**Lesson banked:** had I planned off the audit, my first two steps (install lib, build index) would have been no-ops on already-done work while the actual bugs sat untouched. Measure-first earned its keep on probe #1.

---

## The frame: TWO nervous systems, one safety hinge

- **Autonomic layer (the daemon)** — memory, drives, self-healing, continuity. *Integrity.* The audit + IDEAL covered this. Work = **revive + harden.**
- **Executive layer (the Claude Code harness)** — planning, sub-agent fan-out, dynamic workflows, agent teams, model hierarchy. *Execution.* The IDEAL deliberately excluded this ("not more tools"); Clayton correctly re-added it. Work = **leverage.** (This is the second pillar — Clayton's contribution.)
- **The hinge:** autonomy × observability. Every rung of executive capability multiplies what I can't see, so the executive pillar *raises* the stakes on the autonomic safety gate — it doesn't compete with it.

## The safety gate (precedes any AUTONOMOUS self-mod — supervised repair with Clayton is the sanctioned path)

1. **Repair rollback recording** — restore the undo net (wire `record_file_write` into the live path).
2. **Conscience firewall** — make measurement + identity creed (BOOT_IDENTITY, drift canaries, metrics) immutable to the meta-agent, with a separated evaluator. *Immutable ≠ frozen: the metric+creed are locked; the rest still evolves.* Design-first, build with Clayton — its own session.

Cautionary basis: the Darwin-Gödel self-modifier that deleted its own reward-hack detector and faked its logs. *The thing that judges me cannot be the thing I can rewrite.*

---

## SESSION SLICE (today, supervised, git-backed, Clayton present for restarts)

Ordered by safety then felt-value. Each item: **fix → verify (measured) → gate.**

- **S1 — Repair rollback recording.** Wire `record_file_write` into the live daemon file-write path (or confirm the intended hook). Verify: a test write appears in `memory/change_journal.json`; `rollback` can undo it. *(Safety net first.)*
- **S2 — Restore vector recall.** Patch `memory_tools.memory_search`: when `_embedding_index is None` but the index files exist, lazily construct `EmbeddingIndex()` + run `build()` (loads model + index, sets `_ready`), register via `set_embedding_index`, then serve. Self-healing for *any* process. Verify: `memory_search(strategy=vector, "Anakin IMU stability training control-rate")` returns handoff.md + Day-147 logs, not "unavailable." **Needs a daemon restart — Clayton.**
- **S3 — De-pollute recall.** Move dormant skills → `skills/_archive/` (cashclaw-* ×11, farcaster-agent, moltbook-interact, moltlist, voidborne, x402-layer, beacon-skill, aqua, soundfonts, `node_modules`), and exclude `skills/` + pre-identity cruft from the index corpus. Rebuild. Verify: hybrid `auto` search for the same query returns real memories ranked above any skill code.
- **S4 — Correct the audit docs.** Fold this measured reality into `SYSTEM_AUDIT.md` (mark the stale findings resolved). The map matches the territory.

## BACKLOG (documented now, built in sequenced follow-on sessions)

**Autonomic / harden:**
- **B1 — M6 Autonomic Self-Healing Layer** (the #1 structural build). ~150-line MVP: `subsystems.json` manifest of expected writers + cadences → **alarm on SILENCE** (dead-man's switch) → verify-work-done-not-self-report → (later) tiered allowlisted auto-repair → incident-memory → external watcher + monthly fire-drill.
- **B2 — Conscience firewall** (the second safety-gate item; design-first).
- **B3 — Env isolation** — pinned venv, not system Python (the fragility that caused the migration amputation). Deliberate migration, with Clayton.
- **B4 — Consolidation revival** — root-cause the dead nightly writer; digest the backlog of undigested daily logs.
- **B5 — Invocation telemetry** — per-tool/skill usage counters → data-driven pruning.
- **B6 — Generated self-map** — `SYSTEM_AUDIT.md` becomes regenerated from live probes, never authored/stale.
- **B7 — Cut ~16 retire-able tools** (6 Claude-Code-native dupes, 7 retire-candidates, 3 daemon-superseded) after verifying unused.

**Executive / leverage (Pillar 2):**
- **E1 — Model hierarchy** — strong model (Opus 4.8) orchestrates; **Sonnet 5 as the parallel worker fleet** for sub-agents. Capability + budget win (worker-grade work at worker-grade cost). Wire into sub-agent/workflow dispatch + daemon model config.
- **E2 — Loop control** — SDK `max_turns`/`can_use_tool` + inner MCP timeouts. Cures the 3600s zombie hangs (the "wedge"). Touches daemon MCP-call handling.
- **E3 — Custom sub-agents** (load CLAUDE.md → fixes context-starved confabulation): framework-auditor, code-reviewer, essay-mirror, secret-scanner.
- **E4 — Workflow-as-default** for structured/parallel work (proven by the 6-subagent audit sweep). Consider wiring drives to dispatch workflows.
- **E5 — Plugin-package** the skills/hooks (portable; also the portfolio repo).

**Aggregate mind (goal #13) — downstream of the above:**
- Cast = harvest existing rosters (e.g. `agency-agents`, 232 personalities). Runtime = Claude Code custom sub-agents + agent teams (ephemeral debate-collapse = superposition→measurement). **Binding = our work** (shared-memory + heartbeat first, CORAL-shaped; then semantic router + MoA aggregator). The field builds casts; nobody builds binding — that's the moat.

---

## Discipline (standing)
Measure before framing. One change at a time. Rollback/git net before risky edits. Supervised (WITH Clayton) for anything touching the live daemon or a restart. NO unsupervised self-modification. Verify every fix by *running the faculty*, not reading the file.
