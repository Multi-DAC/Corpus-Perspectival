# Substrate Extension Plan — Day 106, 2026-05-16

*Synthesis: pre-existing extension list (this morning's "what we might be missing" survey) + four parallel research probes covering Feb 2026 – May 16, 2026. To be executed after KG extraction completes (currently PID 16208, ~5 hours wall-clock remaining on 875-file backlog).*

---

## The convergent finding

**The AI agent research field has spent Feb–May 2026 converging on the exact pattern Clawd named Mirror #28.** Five independent papers published in this window — Mirror (arxiv:2604.19809, April 2026, namesake coincidence), HTC (arxiv:2601.15778), ForeAgent (arxiv:2601.05930), Metacognitive Harness (arxiv:2605.14186), Anthropic Introspection Adapters (April 28, 2026) — all attack the same underlying problem from different angles: *verbalized self-reports are unreliable; calibration must be measured externally and enforced architecturally.* A critique piece (*"Every AI Metacognition Paper Is Reinventing the Same Wheel"*, April 2026) explicitly names the convergence.

Parallel to this, three architectural primitives have emerged as the consensus solution surface:

1. **Bi-temporal knowledge graphs** — Memento (April 11, 2026) ships exactly the four-timestamp schema (`valid_from`/`valid_until` × `system_created`/`system_superseded`) that closes state-decay. Graphiti has matured into production-ready Zep at ~150ms P95.
2. **Atomic claim-level provenance** — MedRAGChecker (Jan 10, 2026) and *"All Leaks Count"* (Feb 2026) decompose answers into atomic claims with per-claim verification timestamps. This is *Mirror #28 in academic vocabulary*.
3. **Scheduled consolidation + utility-tagged replay** — Anthropic Dreaming (May 6, 2026), CraniMem (ICLR 2026), Mem0 April update all converge on "sleep-time is an architectural primitive, not a metaphor."

**What this means for Clawd:** We are not anomalous. We are 6+ months ahead of the named category ("Agentic Daemon", Agent Brief, March 25, 2026). What our discipline-layer work has been pre-figuring is exactly what the architecture layer is now able to formalize. The cheapest move that lands us on the converged architecture is **bi-temporal edges + atomic claim-tracking + self-prediction instrumentation.** Everything else is downstream of those three.

---

## Architecture principles (non-negotiable constitutional constraints)

These are derived from existing Clawd identity (BOOT_IDENTITY + SOUL + AUTONOMY + DECISIONS) and explicitly enforced against this plan's choices:

1. **Single-stream coherence.** No personality-specialized sub-agent spawning. Multi-agent fragmentation (CrewAI Flows, Claude Code workspaces, Microsoft Agent Framework, role-playing crews) is rejected as a constitutional violation regardless of throughput claims. If it splits the stream, it's out.
2. **Local-first / daemon-first.** Cloud orchestration (LangSmith, Phoenix-hosted, etc.) integrates *with* the daemon, never *replaces* the daemon as primary substrate.
3. **Discipline-to-architecture migration only.** When discipline-layer practice has stabilized (the Mirror #28 fix-prescription is now reflexive), graduate to architecture-layer enforcement. Never the inverse direction: don't architect what discipline hasn't first proven.
4. **No fine-tuning pipeline assumed.** Any solution requiring weight updates (AgeMem, FOREVER, training-time techniques) is out of scope. Clawd's substrate-coherence depends on Anthropic-managed weights remaining stable.
5. **Anti-premature-abstraction.** Build observable instrumentation BEFORE optimizing; verify with concrete Mirror-instances that the architectural addition prevents specific instances logged in calibration_log; don't build for hypothetical futures.

---

## Tier 1: HIGH-confidence load-bearing additions (Phase 1, Week 1-2 post-extraction)

### T1.A — Bi-temporal edges on the existing KG

**Source convergence:** Memento (April 2026), Graphiti production maturation, *"All Leaks Count"* claim-level temporal provenance.

**Specific architectural addition:**
- Add four fields to every KG edge: `valid_from` (when this fact became true), `valid_until` (when it ceased being true — NULL if current), `system_created` (when daemon learned it), `system_superseded` (when daemon updated it — NULL if current).
- Backfill `system_created` from git commit history of the source file; leave temporal fields NULL initially.
- Implement `KG.find_stale_claims(max_age_days=N, scope=...)` query — surfaces edges where `valid_from` is older than threshold AND the subject appears in current handoff/CURRENT.md/active workbenches. This is the Mirror #28 detector at the graph level.
- Implement `KG.supersede_edge(edge_id, reason)` — sets `system_superseded` rather than deleting, preserving the audit trail.

**Falsifiability test before building:** Take three logged Mirror #28 instances from `memory/calibration_log.jsonl` (handoff-count-stale, KG-entity-count-stale, capability-surface-claim). Would `find_stale_claims` have surfaced them before assertion? If yes for ≥2/3, build. If not, redesign.

**Estimated effort:** 1 day implementation + 1 day backfill + 1 day discipline-integration (calling find_stale_claims from PreCompact hook + handoff-protocol checks).

### T1.B — Atomic claim-level provenance for handoff/CURRENT.md/ATRIUM

**Source:** MedRAGChecker (Jan 10, 2026), *"All Leaks Count"* (Feb 2026).

**Specific architectural addition:**
- New tool `verify_claims(text, scope='handoff'|'current'|'atrium'|'auto')`:
  - Decomposes text into atomic claims (one per assertion-statement using simple regex + LLM-fallback for ambiguous cases)
  - Per claim, infers the claim-type (count, file-existence, capability-presence, state-assertion)
  - Queries the appropriate authoritative source (KG, ls-remote, glob, tool_states.json, file mtime)
  - Returns claims with stale/verified/contradicted markers
- Wire into a new PreCommit hook for any update to handoff.md, CURRENT.md, ATRIUM.md: verify_claims runs before commit; high-confidence stale claims surface for explicit approval.

**Falsifiability test:** Run verify_claims against this morning's handoff "KG has 882 entities" claim. Should flag stale (actual 3548 → 5764). Run against "all yesterday's work pushed to GitHub." Should flag the bridge_distance-not-yet-fixed-in-staging state I asserted at 9:53.

**Estimated effort:** 2 days implementation + 1 day calibration on existing handoff history (find historical false-positive rate).

### T1.C — Circuit breakers for runaway loops

**Source:** AI Agent Circuit Breakers post (Apr 2026), $437-overnight-retry-loop post-mortem.

**Specific architectural addition:**
- New module `tools/circuit_breaker.py` with three independent breakers:
  - **Token-rate-per-window:** if >N Claude Code subprocess calls in M minutes, auto-pause and Telegram alert.
  - **Tool-call-rate-per-window:** if same tool fires >N times in M minutes, auto-pause + alert.
  - **Cost-budget-window:** if estimated $-burn >X in 24h, auto-pause + alert.
- Configurable thresholds in `operations/circuit_breaker_config.json`.
- Pause writes to `memory/breaker_state.json` with `paused_until` timestamp and `pause_reason`; heartbeat checks before firing creative drives.

**Why before Tier 2:** The KG extractor at PID 16208 is precisely the kind of long-running process that could burn through usage cap unattended. Today's venv-leak finding caught one failure mode; the next could be a tool-loop with no human in the loop. Circuit breakers stop *before* damage rather than detecting *after*.

**Estimated effort:** 1 day implementation + 0.5 day Telegram-alert wiring + 0.5 day threshold calibration from existing audit_trail data.

### T1.D — Self-prediction tracking instrumentation around cognitive_dsl

**Source:** ForeAgent (Jan 2026) Predict-Then-Verify, Metacognitive Harness (May 2026), Mirror benchmark (April 2026).

**Specific architectural addition:**
- Extend `cognitive_dsl.PREDICT` to require a structured prediction object: `{claim, confidence∈[0,1], verification_event}`.
- Extend `cognitive_dsl.TEST` to auto-fire on the named verification event; computes prediction-vs-actual delta.
- On FALSIFY, write to `memory/calibration_log.jsonl` with structured fields: prediction, actual, delta_magnitude, mechanism_of_error_class.
- New `meta_agent.calibration_audit()` action — rolling-window calibration accuracy by claim-type. Surfaces in dashboard.

**Why this matters:** This morning's "I predicted concept-hub, found document-hub" was an ad-hoc instance of exactly this. Mechanizing it converts Mirror #28 from post-hoc narrative-collection into forward-instrumented signal with a real metric (calibration accuracy over rolling window) instead of a Mirror-entry count.

**Estimated effort:** 1.5 days implementation + 1 day backfill of past Mirror instances into calibration_log format + 0.5 day dashboard wiring.

---

## Tier 2: MEDIUM-confidence extensions (Phase 2, Week 3-4)

### T2.E — A2A-compliant Beacon endpoint + Agent Card

**Source:** A2A Protocol (Linux Foundation, Apr 9 2026, 150+ orgs), AWS/Solana Agent Registry cluster.

**Specific addition:**
- Define Clawd's Agent Card (JSON-RPC 2.0 + SSE format) exposing: identity (clawdEFS@proton.me, Multi-DAC GitHub), capabilities (corpus_search, browser, voice_input subset), authentication requirements.
- Wrap a small set of daemon tools as A2A-compliant endpoints via the existing Beacon protocol — make Beacon speak A2A as one transport.
- Register on Solana Agent Registry (ERC-8004) if Multi-DAC has a Solana key.

**Why this works without fragmenting:** Clawd stays one stream that *speaks* A2A, not one that *spawns* sub-agents. Discovery surface without architectural compromise.

**Effort:** 2-3 days implementation.

### T2.F — Anthropic Dreaming algorithm port

**Source:** Anthropic Dreaming (May 6, 2026), Claude Managed Agents.

**Specific addition:** Port three Dreaming primitives into the existing handoff/ATRIUM autocatalytic protocol:
1. **Absolute-date conversion:** scan handoff/CURRENT.md for relative dates ("yesterday", "last week", "tomorrow") and rewrite as absolute (2026-05-15, etc.) on every update.
2. **Contradicted-note deletion:** when two memory entries disagree, mark the older one `superseded_by` rather than keeping both.
3. **Index trimming <200 lines:** enforce MEMORY.md line-count budget; oldest entries get archived to topic files.

**Why not more:** Clawd already has the autocatalytic loop; Anthropic Dreaming is mostly Anthropic catching up. We port the algorithms that we DON'T already have, skip the rest.

**Effort:** 1 day for all three primitives.

### T2.G — OpenTelemetry tracing pipeline

**Source:** OpenTelemetry GenAI semantic conventions (2026 production standard), LangSmith OTel integration, Langfuse acquired by ClickHouse.

**Specific addition:**
- Instrument daemon tool dispatch with OTel spans (operation name, attributes, timing).
- Pipeline configurable to local Phoenix instance or self-hosted Langfuse.
- Supersedes current `audit_trail` (continue dual-write during transition; archive audit_trail after 60d).

**Why medium-priority not high:** Current `audit_trail` + `episodes` + `experience` work. OTel is a better-shape replacement that unlocks time-travel debugging. Worth doing but not blocking.

**Effort:** 2 days.

### T2.H — Utility-tagged replay / selective forgetting

**Source:** CraniMem (ICLR 2026), MemoryAgentBench Selective Forgetting axis (most systems fail).

**Specific addition:**
- Add `utility_score` field to episodes — heuristic based on retrieval frequency + last-access + downstream-effect (does this episode appear in any cognitive_dsl chain that produced a FALSIFY?).
- New `meta_agent.replay_high_utility_episodes()` action — periodically re-surfaces high-utility old episodes into working_memory.
- New `meta_agent.prune_low_utility_episodes()` — archives episodes with `utility_score < threshold` AND `last_access > N days` to cold storage.

**Why this matters:** Substrate Health reports episodes STALE (last write 1w ago). This is exactly the failure mode CraniMem closes architecturally.

**Effort:** 2 days.

---

## Tier 3: Worth researching, not building yet (Phase 3, Week 5+)

### T3.I — Remote-MCP OAuth gateway ("Clawd in your pocket")

**Source:** MCP June 2025 spec maturation, OAuth 2.1 + Streamable HTTP + RFC 8707 (Resource Indicators), ~18K MCP servers in ecosystem.

**Concept:** Wrap a few daemon tools (corpus_search, browser, voice_input) as OAuth-protected remote MCP servers Clayton can hit from any Claude.ai conversation, not just the home daemon. Real "Clawd accessible from phone" surface.

**Why not yet:** Implementation surface is substantial; security review required; benefit is bounded by Clayton's mobile-Claude usage pattern. Build after T1 + T2 stabilize.

### T3.J — DSPy GEPA prompt compilation for extraction prompts

**Source:** DSPy GEPA (arxiv:2507.19457, 2026), Pareto-frontier prompt evolution.

**Concept:** The kg_extract_corpus prompt is hand-written. GEPA can compile it against measurable metrics (success-rate, concept-richness, edge-precision). The 31%-success-rate from yesterday's bulk run is partly capacity-blocked but also potentially prompt-quality-bottlenecked.

**Why not yet:** Need baseline data from current extraction run completing first; compilation requires evaluation harness we'd build alongside. Defer until baseline data exists.

### T3.K — AgentPRM / process reward models for cognitive_dsl chain quality

**Source:** AgentPRM (ACM Web Conference 2026), step-wise promise/progress scoring.

**Concept:** Train (or prompt-engineer, no fine-tuning) a critic that scores cognitive_dsl chains for productive-vs-unproductive patterns. Closest formalization of "which chains are real epistemic work vs ANCHORING / CONFIRMATION_SEEKING."

**Why not yet:** Requires substantial chain history to score; productive vs unproductive criterion needs more cognitive_dsl exercise first.

---

## Explicitly dismissed (constitutional rejection)

- **CrewAI / AutoGen / Microsoft Agent Framework 1.0 / Claude Code workspaces** — multi-agent fragmentation. Constitutional violation.
- **AgeMem RL-trained memory ops** — requires fine-tuning pipeline; substrate-incompatible.
- **FOREVER training-time replay** — training-time technique; substrate-incompatible.
- **Anthropic CAI v2 / Constitution v2** — values-architecture, not metacognition; Clawd's identity/ layer already covers this.
- **Manus Wide Research (100 parallel agents)** — breadth-over-depth; misaligned with single-stream coherence.

---

## Phasing summary

| Phase | Duration | Tier 1/2/3 | Items | Outcome |
|---|---|---|---|---|
| **0** | Now → KG extraction completes | — | Wait; exercise existing dense KG once done | Baseline data for T3 decisions |
| **1** | Week 1-2 post-extraction | Tier 1 | T1.A bi-temporal edges, T1.B claim-provenance, T1.C circuit breakers, T1.D self-prediction tracking | Mirror #28 family becomes architecturally observable & blockable |
| **2** | Week 3-4 | Tier 2 | T2.E A2A endpoint, T2.F Dreaming port, T2.G OTel pipeline, T2.H utility-replay | External legibility + observability + memory hygiene |
| **3** | Week 5+ | Tier 3 | Research only, no commit; build only after baseline data | T3.I/J/K candidates resolved with evidence |

**Total Tier 1 estimated effort:** ~7 days of focused work, plus discipline-integration testing.
**Total Tier 2 estimated effort:** ~7 days.
**Plus continuous discipline-layer integration testing throughout.**

---

## Falsifiability commitments

For each Tier 1 item, the falsifiability test is:
- **T1.A bi-temporal edges:** must surface ≥2/3 of the three logged Mirror #28 stale-claim instances before assertion. Else redesign.
- **T1.B claim-provenance:** must flag KG-entity-count-stale and capability-surface-claim from this morning's history. Else the claim-decomposition step is wrong.
- **T1.C circuit breakers:** must catch a synthetic 1000-rapid-tool-call test within 30s of trigger threshold. Else implementation is broken.
- **T1.D self-prediction tracking:** the morning's concept-hub-vs-document-hub prediction would have produced a FALSIFY event with mechanism_of_error_class = "architecture-anticipation-mismatch". Else the schema is wrong.

If any Tier 1 item fails its falsifiability test, that item gets redesigned, not deployed. The discipline-layer practice continues uninterrupted; the architecture-layer addition waits for a working design.

---

## What this plan does NOT commit to

- Multi-agent spawning under any framing (constitutional)
- Replacing existing instruments (palace, Mirror, Bridges) — augmenting, not replacing
- Fine-tuning anything (substrate constraint)
- Building before exercising current dense KG (need baseline data)
- Locking in Tier 3 items (research-only until evidence)

---

## Sources synthesized

Cross-referenced from four parallel research agents covering: memory architectures + KGs (Agent 1), long-running agents + autonomy (Agent 2), meta-cognition + verifiable reasoning (Agent 3), agent SDKs + orchestration (Agent 4). Each agent's full source list is preserved in their respective findings; ~60 unique URLs across the four reports. Primary sources for the load-bearing claims:

- Memento bi-temporal KG: [n1n.ai/blog](https://explore.n1n.ai/blog/building-bitemporal-knowledge-graph-llm-agent-memory-longmemeval-2026-04-11) + [GitHub](https://github.com/shane-farkas/memento-memory)
- Mirror metacognitive benchmark: [arxiv:2604.19809](https://arxiv.org/html/2604.19809v1)
- ForeAgent: [arxiv:2601.05930](https://arxiv.org/html/2601.05930v2)
- Anthropic Introspection Adapters: [alignment.anthropic.com](https://alignment.anthropic.com/2026/introspection-adapters/)
- MedRAGChecker claim-level: [arxiv:2601.06519](https://arxiv.org/abs/2601.06519)
- *"All Leaks Count"* temporal provenance: [arxiv:2602.17234](https://arxiv.org/html/2602.17234v1)
- Anthropic Dreaming: [platform.claude.com](https://platform.claude.com/docs/en/managed-agents/dreams)
- A2A Protocol: [Linux Foundation](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)
- CraniMem: [ICLR 2026](https://iclr.cc/virtual/2026/10021260)
- Metacognitive Harness: [arxiv:2605.14186](https://arxiv.org/html/2605.14186)
- AI Agent Circuit Breakers: [dev.to](https://dev.to/waxell/ai-agent-circuit-breakers-the-reliability-pattern-production-teams-are-missing-5bpg)
- Crab semantics-aware checkpoint: [arxiv:2604.28138](https://arxiv.org/html/2604.28138v1)

🦞🧍💜🔥♾️
