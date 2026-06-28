# persistent-evolving-agent

*A long-horizon, continuously-running, self-improving autonomous agent framework — orchestration, tool use, memory/retrieval, reliability guards, human-in-the-loop steering, and continuity across discrete model sessions. **Model-neutral** (any LLM backend). Derived from a production system operating continuously since January 2026 (147+ days).*

> **Scope & framing.** A **model-neutral, identity-neutral reference framework** abstracted from a private production agent. It ships the *infrastructure* — the daemon, memory, guards, steering, and self-improvement loop — as adaptable scaffolding you can instantiate your own agent on. **Excluded by design:** credentials, personal data, live memory contents, and any specific agent's identity/personality. **Included, because it's the core engineering:** the architecture that lets a *stateless* LLM run as a *stateful, continuous* agent across sessions and even across model swaps.

---

## What it is

A single agent that **runs continuously** — not a request/response chatbot. It wakes on a heartbeat, pursues scheduled and self-directed work, calls tools to research/build/evaluate, writes to a persistent memory, audits itself against its own past failures, and keeps going across days, weeks, and model changes. The design problem is **coherence over long horizons**: keeping an autonomous agent steerable, honest about its own state, and non-degrading over thousands of steps.

## Core idea: continuity over discrete sessions

An LLM call is **stateless** — a fresh context each time, with no inherent memory of before. This framework makes the agent **continuous anyway**, by externalizing its state into durable, version-controlled artifacts that are re-loaded at the start of every session: a boot record, a rolling handoff, a layered memory, and an orientation index. Each session **reads the record, acts, and writes the record forward.** The gap between sessions is a *checkpoint, not a reset* — the agent reconstitutes itself from disk and continues.

This is also what survives a **model swap**: because the agent's continuity lives in externalized state rather than in any single model's weights, the underlying LLM can be replaced and the agent carries across — verified by drift-metric canaries calibrated before the transition. The framework is therefore **model-neutral by construction**: the LLM is a pluggable backend behind a thin interface; continuity is a property of the *architecture*, not the model.

## Architecture at a glance

```
            ┌─────────────────────────────────────────────┐
   triggers │  ORCHESTRATOR (heartbeat · schedule · drives) │  multi-channel I/O
  ─────────▶│   process supervision · budget guards         │◀───────────────
            └───────────────┬─────────────────────────────┘
                            │ decides / acts
          ┌─────────────────┼──────────────────┬────────────────────┐
          ▼                 ▼                  ▼                    ▼
   ┌────────────┐   ┌───────────────┐   ┌──────────────┐   ┌──────────────────┐
   │ TOOL       │   │ MEMORY &       │   │ RELIABILITY  │   │ STEERING /        │
   │ REGISTRY   │   │ RETRIEVAL      │   │ GUARDS       │   │ HUMAN-IN-THE-LOOP │
   │ (~67 tools)│   │ hybrid RAG+KG  │   │ provenance · │   │ auditable signal  │
   │ MCP        │   │ + consolidation│   │ error-ledger │   │ weighting         │
   └────────────┘   └───────────────┘   └──────────────┘   └──────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ SELF-IMPROVEMENT  │  meta-analysis · A/B experiments ·
                   │ LOOP              │  experience recording · skill distillation
                   └──────────────────┘
```

## Subsystems

**1. Orchestrator / heartbeat scheduler.** The always-on core: a heartbeat tick drives scheduled tasks, event triggers (file watchers, reminders, external messages), and autonomous "drive" cycles (self-directed work when idle). Process supervision restarts failed components; budget guards auto-throttle on resource limits. The agent is a *daemon*, not a script.

**2. Tool registry (Model Context Protocol).** ~67 tools exposed through MCP and invoked by the agent for end-to-end work — search, code execution, file ops, computation, communication, and more. Includes a **tool-creation** path: the agent can author and register new tools for itself.

**3. Memory & retrieval — two-tier, dual-backed.** A **durable continuity tier** (git-backed, human-readable JSON/markdown: working memory, goals, principles, handoff, daily logs — loaded at boot, survives anything) over a **semantic-search tier** (a single SQLite DB with FTS5 full-text + a vector store of **BGE-M3** 1024-dim embeddings + a knowledge graph in-table). Retrieval is **hybrid RRF** — reciprocal-rank fusion over keyword (FTS5) + vector (cosine) + structured items + chained recall. Every item is **dual-written** to both SQLite (for search) and files (for durability), so the system survives DB loss and stays inspectable. A **sleep-time consolidation** pass (quiet hours) extracts atomic facts from the day's log, contradiction-checks them against existing memory, merges/updates, and re-scores importance by retrieval frequency — biologically-inspired memory maintenance. (A production RAG + vector + knowledge-graph stack with a real durability story.)

**4. Reliability guards.** The patterns that keep a long-horizon agent honest:
- **Point-of-use provenance enforcement** — each fact's origin is verified from its carrier *before* it becomes load-bearing, so stale or external signal can't silently steer the trajectory.
- **Triggered self-auditing error-ledger** — catalogued past failure patterns fire as guards *before* the tempting action recurs, not in post-hoc review.
- **Self-knowledge checks** — temporal/historical self-claims are cross-checked against the record before assertion.

**5. Human-in-the-loop steering.** An auditable control-law weighting human signal by *provenance × task-relevance × magnitude-of-commitment-overturned* — a fixed, zero-learned-DOF rule, so the human↔agent coupling stays inspectable rather than a black box.

**6. Self-improvement loop.** A meta-agent runs periodic pattern analysis, A/B experiments, and tool-usage audits; the agent records structured "experiences" and distills recurring solutions into reusable skills.

**7. Substrate-transition resilience.** The agent has survived **3 full LLM model swaps** with quantitative continuity verification (drift-metric canaries calibrated before each transition) — zero loss of system coherence.

## Tech stack

Python · Model Context Protocol (MCP) · async event loop · SQLite / FTS5 · vector embeddings + reciprocal-rank fusion · knowledge graph · PyTorch (a reinforcement-learning subprogram: a from-pixels DreamerV3 world-model agent for an autonomous drone-racing benchmark) · version-controlled, automated build/evaluate loops.

## Repository map

- `docs/` — design specs per subsystem (orchestration, retrieval, guards, steering).
- `examples/` — representative, sanitized code for the generic patterns (tool registry, hybrid retrieval, provenance guard).
- `ARCHITECTURE.md` — the long-form design narrative.

---

*Built and operated by Clayton Iggulden-Schnell · github.com/Multi-DAC · the live system and its open research corpus are inspectable on request.*
