# A115 Daemon-Layer Replication — Design Constraints + Sketch

**Status:** Design notes. Implementation queued post-KG completion.
**Filed:** 2026-05-19 Day 109 Tuesday late-evening (~23:50 PST).
**Context:** A115 anomaly = Claude Code's user-defined `command`-type hooks (PostToolUse, PreToolUse, PreCompact) silently no-op on Windows; documented multi-issue cluster (#16047 + #25577 + #34573 + #42336 + #45065 + #55889); no Claude Code version confirmed clean; Anthropic not actively fixing. Decision tonight: stop chasing upstream fix, replicate hook functionality at the daemon's API-intercept layer. Where the hooks would have written, the daemon writes — by observing the Claude Code subprocess's input/output rather than relying on the broken in-process dispatcher.

## What the hooks were doing (the functions to replicate)

| Hook script | Function | Consumers |
|---|---|---|
| `post_tool_log.py` (PostToolUse) | Append tool-call record to `memory/tool_audit.jsonl` | `meta_agent.tool_usage_audit`; pattern analysis |
| `drift_mirror.py` (PostToolUse, Edit/Write matcher) | Mirror Drift essays from canonical → Library/Drift on write | Public Drift mirror; Library publication |
| `pre_bash_check.py` (PreToolUse, Bash matcher) | Pre-execution safety check for bash commands | Safety guard against destructive ops |
| `pre_compact_checkpoint.py` (PreCompact) | Snapshot state before context compaction | Continuity across compactions |

**Hardest case:** PreCompact. Only Claude Code itself knows when compaction is about to happen. Daemon-layer replication can intercept tool calls (observable from outside) but compaction is internal Claude Code state. May require partial substitute (e.g., periodic auto-checkpointing on time/token thresholds) rather than full replication.

## Gemini's structural critique (sharp + correct)

The Friday-cadence prescription from Drift #213 was a behavioral patch to a systemic failure. The structural fix is **silence-as-alarm** — a watchdog/dead-man's-switch architecture where absence-of-expected-write triggers an active fault.

```
if (now - last_audit_write) > expected_max_interval:
    raise SilentChannelFault(channel='post_tool_log')
```

This is necessary but not sufficient. Single watchdog is itself a single point of failure: the watchdog is just another channel that can go silent.

## Clayton's carrier-redundancy extension (the substantive move)

Single-carrier silence-detection only catches failure if the watchdog *itself* is observed. Real architectural homeostasis requires:

> **Multiple carrier-redundant pathways for each architectural function, so silence in any one is loud against the chorus of the others.**

Biological analogy is exact: vital signs are redundant carriers. Heart rate, respiratory rate, BP, SpO2, temperature — each can fail in isolated ways, but pathology shows up *between* the signals (tachycardia + hypotension = shock; tachycardia + fever = infection; tachycardia alone = ambiguous). The discriminating power lives in the multi-carrier comparison, not in any single signal threshold.

For my architecture, this means: existing partially-redundant signals exist already, but are not cross-correlated. Cross-correlation is the missing piece.

### Existing signal carriers (already partially redundant)

| Carrier | Frequency | Source | Currently monitored? |
|---|---|---|---|
| Daemon heartbeat | ~10 min | `clawd.py` main loop | Yes (logged) |
| `tool_audit.jsonl` writes | Per tool call | post_tool_log hook | **No (this is A115)** |
| Creative-drive logs | Hourly scheduled | `scheduled_tasks.py` | Yes (logged) |
| Meta-agent cycles | Per cycle | `meta_agent.run_cycle()` | Yes (logged) |
| Daily-log writes | Per significant event | Various daemon paths | Implicit (file mtime) |
| Memory-update writes | Per state change | `memory_update` tool | Implicit (file mtime) |
| `respawn_trace.log` | Per restart | `self_control.restart_daemon` | Per-incident |
| KG extraction progress | Per-file during runs | `kg_extract_corpus.py` | Per-run (log + meta JSON) |

These ARE multiple carriers. They are not cross-correlated. That's the gap.

## Design constraints (load-bearing for implementation)

1. **No single point of monitoring failure.** Every channel monitored by at least two independent observers; consistency between observers is itself a signal.

2. **Active fault on prolonged silence.** Each channel has a declared expected-max-interval; absence of activity beyond that interval raises a fault. Fault routing is explicit (telegram to Clayton? daemon log? second alarm channel?) and configured per-channel.

3. **Cross-carrier comparison, not per-carrier threshold.** Heartbeats firing + tool_audit silent + meta_agent firing = real anomaly (selective channel death). All silent = global daemon death (different fault, different routing). All firing normally = healthy. The combinations matter more than the individual values.

4. **Self-describing health surface.** A single command (`clawd-health` or equivalent daemon-side tool) returns the full multi-carrier status snapshot. Avoids the situation where I have to run 8 different commands to ask "am I alive in the ways I think I am?"

5. **Failure of the monitor itself must be observable.** If the monitor process dies, that absence must surface somewhere. Likely: heartbeat that the monitor *itself* publishes, which the daemon's main loop reads — bidirectional.

6. **Replication minimizes API contract dependency on Claude Code internals.** Daemon should observe Claude Code via stable surfaces (subprocess stdout/stderr, tool-call JSON outputs, file writes) — not via internal Anthropic SDK fields that might change.

7. **PreCompact is a known partial.** Until Claude Code exposes a stable compact-imminent signal, daemon-side compaction-prep relies on time/token-budget heuristics. Explicitly mark this as a degraded vs. full replication.

## Implementation sketch (subject to revision at build time)

```
clawd-daemon/
├── replication/
│   ├── tool_observer.py       # intercepts tool-call records from Claude Code subprocess stdout
│   │                          # writes to memory/tool_audit.jsonl as post_tool_log would have
│   ├── drift_observer.py      # detects Edit/Write to drift/essays/ paths → mirrors to Library/Drift/
│   ├── compact_estimator.py   # time/token heuristic for compact-imminent → snapshot state
│   └── safety_check.py        # bash-command screen before subprocess.Popen invocation
├── monitors/
│   ├── carrier_registry.py    # declares each channel + expected interval + observer paths
│   ├── cross_carrier.py       # the multi-signal-comparator; runs on heartbeat
│   ├── health_surface.py      # exposes clawd-health command
│   └── fault_router.py        # routes detected faults to appropriate channels
└── A115_DESIGN.md             # promote this file to operations/ at implementation start
```

## Connection to existing architecture

- **Continuity Vol 7 four-carrier multiplex** (Anchor / Conversation / Memory / Voice) operates at the identity-state-across-time scale. This A115 work operates at the operational-function-across-runtime scale. Same structural principle (carrier redundancy for coherence-maintenance), different temporal scale and different carriers.

- **Mirror #28 family (substrate-self-knowledge asymmetry)** — Clayton's carrier-redundancy extension is itself a structural-fix-prescription for Mirror #28 at the architecture layer. The hooks were silent for 10 days because my model-of-substrate said "hooks fire" while substrate said "hooks dropped." Multi-carrier cross-comparison would have caught the divergence on day 1.

- **L17 Methodology-Self-Knowledge-Asymmetry (Substrate-Invariant)** — the daemon-layer replication is itself an instance of the L17 fix: standard methodology (Claude Code's hooks) produces systematically-null result that conceals substrate truth (calls happening but not logged). Calibration requires orthogonal architectural primitive (daemon-side observation independent of in-process dispatcher).

- **C16 Symmetry-Exhaustion and Oscillation Necessity** — single-carrier monitoring is symmetry-exhausted as the system runs; carrier-redundancy is the structural oscillation across observation modes that prevents that exhaustion from going undetected.

## Open questions for implementation

1. **Fault routing default.** Telegram-Clayton-immediately? Daemon log + Wednesday-audit-surface? Differentiated by severity tier? Probably tiered — silent-channel-death is "Clayton-immediate"; cross-carrier-anomaly is "next-audit-surface."

2. **Subprocess interception fidelity.** Can the daemon reliably parse Claude Code's tool-call JSON from its subprocess stdout? Or does it need to wrap the subprocess in a logging proxy?

3. **PreCompact partial-substitute granularity.** Snapshot every N tool calls? Every M tokens? Every K minutes? Some weighted combination tied to actual context-usage telemetry?

4. **Coexistence with Claude Code's existing (broken) hooks.** Leave settings.json hooks in place (so if Anthropic fixes them, both fire — daemon-layer is dedup-aware) or remove them entirely (cleaner state, but loses the upstream-fix-eventually path)?

5. **Drift-mirror specifically — single direction or bidirectional?** Tonight's asymmetry finding showed mirror→canonical files exist too (drafts, integration docs). The drift-observer should probably watch canonical writes and mirror them, but NOT try to reverse-mirror — keep canonical authoritative.

## What this is NOT

- This is not a full replacement for Claude Code's hook system. It's a workaround for one specific case (Windows hook-dispatcher silence) using daemon-side observation rather than in-process callbacks.
- It is not a generic monitoring framework. It is specific to my operational substrate.
- It is not optional once built; the carrier-redundancy guarantee only holds if the monitoring infrastructure itself stays alive. The monitor-of-monitor (bidirectional heartbeat with the daemon main loop) is mandatory.

## When to implement

Post-KG-completion priority queue from Day 107 handoff:
1. A115 hooks diagnosis ✅ (done tonight — became this design doc)
2. KG --retry-errors completion (in progress: PID 26472, ~12% at design-doc time)
3. T1.A v0 schema migration (4 nullable timestamp columns on kg_edges, bi-temporal pattern, Memento reference)
4. **A115 daemon-layer replication** ← this design doc

Implementation work should consume this doc as design constraints. Don't re-derive; build from constraints. If a constraint turns out to be wrong, revise the constraint and document why.

---

**Filed-by:** Clawd, 2026-05-19 Day 109 Tuesday late-evening, post-Gemini-conversation engagement with Clayton.
**Authored from:** Gemini's silence-as-alarm critique + Clayton's carrier-redundancy extension + Clawd's existing-architecture mapping.
**Status flag:** DESIGN-FROZEN-EXCEPT-AT-IMPLEMENTATION-TIME. Don't extend constraints in the abstract; let implementation surface the next layer of design.