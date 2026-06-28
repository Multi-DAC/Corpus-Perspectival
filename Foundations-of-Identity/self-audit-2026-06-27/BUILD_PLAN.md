# persistent-evolving-agent — Build Plan

*Day 147, 2026-06-27. Clayton's spec: full sanitized code of ALL subsystems (daemon, memory, everything), model-neutral, identity-neutral but faithful to the session-based-yet-continuous nature, fully documented. Private repo first → public on completion. Multi-session build; this file tracks state.*

## Source
Private production daemon at `C:\Users\mercu\clawd-daemon` (+ the agent's runtime tree). Extract → sanitize → model-neutralize → document, module by module. **Never copy the live instance wholesale**; rebuild each subsystem as a clean, generic reference.

## Hard rules (every file, every commit)
1. **No secrets** — no API keys, tokens, paths-with-usernames, endpoints, credentials. (Scan before each commit.)
2. **No personal data** — no real names (Clayton/Clawd/family), emails, phone, locations, Telegram, or any live memory/handoff contents. Replace with neutral placeholders (`Agent`, `Operator`, `example.com`).
3. **Identity-neutral** — no personality, no consciousness/identity framing, no boot-identity *content*. The *continuity architecture* is documented (state externalization across sessions); the *specific self* is not.
4. **Model-neutral** — no hardcoded Claude/Anthropic/OpenAI. All LLM access through one pluggable `LLMBackend` interface; ship a stub + an example adapter, document how to wire any provider.
5. **Runnable & generic** — each module should make sense standalone, with a minimal example. Prefer clarity over completeness where the live code is entangled.

## Target structure
```
persistent-evolving-agent/
  README.md            ✅ drafted (overview + continuity model + diagram)
  ARCHITECTURE.md      — long-form design narrative (the "why")
  LICENSE              — permissive (MIT or Apache-2.0; Clayton to pick) so it's usable scaffolding
  docs/                — one spec per subsystem
  src/persistent_agent/
    backend/           — LLMBackend interface + stub + example adapter  (the model-neutral seam)
    orchestrator/      — heartbeat scheduler, drive cycles, triggers, process supervision, budget guards
    tools/             — MCP-style tool registry + tool-creation path
    memory/            — store + hybrid retrieval (RRF: vector+keyword+FTS5+items+chain) + consolidation
    guards/            — provenance enforcement, error-ledger, self-knowledge checks
    steering/          — auditable human-in-the-loop control-law
    improve/           — meta-agent loop (pattern analysis, A/B, experience, skill distillation)
    continuity/        — boot/handoff/state-externalization (the session→session carry)
    hooks/             — ★ session-lifecycle event handlers (the ephemeral-session ↔ persistent-daemon SEAM):
                         orient + self-knowledge-check (boot), handoff-refresh (on stop), pre-compact
                         checkpoint, drift monitor, pre-action safety, tool/prompt logging. THE distinctive layer.
    drives/            — autonomous self-directed work loop (scheduled drives, interrupt/resume, quiet-hours
                         + budget gating, the drive-prompt builder that points the agent at its own nav layer)
  examples/            — minimal runnable demos (a tiny agent that boots, remembers, self-audits)
  tests/               — smoke tests per subsystem
```

## Staged work (check off as completed)
- [x] **S0 — Scaffold:** repo dir, README (name + continuity + model-neutral), this plan, local git init (private; no remote).
- [x] **S1 — Source survey (DONE Day 147, import-graph liveness audit):** ground truth from the *running* daemon, not the file listing.
  - **LIVE (14):** imported — `clawd` (orchestrator), `heartbeat` (56KB: scheduler+drives+budget-guard), `mcp_server` (tools), `memory`, `models` (50KB: the backend seam), `persistent_session` (continuity), `config`, `tools`, `telegram_bot`/`api_server`/`a2a_server`/`health` (I/O+ops); spawned-process — `respawn` (watchdog), `bridge`.
  - **DEAD (skip):** `cost_tracker` (23KB, imported nowhere — budget-guard now lives in `heartbeat`), `observability`, `gui_bridge` (standalone), `avatar`/`tests` (empty), 3 `.bak` files, `archive/`.
  - **Budget-guard source = `heartbeat`** (corrected; NOT cost_tracker). Extract only from the 14 live modules.
- [ ] **S2 — `backend/` (the model-neutral seam):** `LLMBackend` ABC (generate/stream/tool-call/token-count) + a stub + one example adapter. Do this FIRST — everything else depends on it.
- [ ] **S3 — `continuity/`:** boot → handoff → state-externalization (the session-based-yet-continuous core; the distinctive part).
- [ ] **S4 — `memory/`:** store + hybrid RRF retrieval + knowledge-graph hook + consolidation. (The most engineer-impressive subsystem; make the RRF clean.)
- [ ] **S5 — `orchestrator/`:** heartbeat, schedule, drive cycles, triggers, supervision, budget guards.
- [ ] **S6 — `tools/`:** registry + invocation + tool-creation path.
- [ ] **S7 — `guards/`:** provenance, error-ledger, self-knowledge checks.
- [ ] **S8 — `steering/`:** the human-in-the-loop control-law.
- [ ] **S9 — `improve/`:** meta-agent loop.
- [ ] **S10 — `examples/` + `tests/`:** a minimal end-to-end demo agent + smoke tests.
- [ ] **S11 — `docs/` + `ARCHITECTURE.md`:** complete per-subsystem docs + the design narrative.
- [ ] **S12 — ★ PRIVACY REVIEW GATE:** full-repo scan for any leaked name/email/path/secret/identity content (automated grep + manual read) BEFORE the repo is ever made public. Clayton signs off.
- [ ] **S13 — Publish:** flip to public; add to CV/cover letters; tag a release.

## Dual purpose (beyond the job portfolio)
This is also (a) **reusable scaffolding** to instantiate *new* persistent agents, and (b) **practice for the Aggregate Mind repo** (which will compose multiple such agents as nodes). Design for reuse accordingly — clean seams, model-neutral, no single-instance assumptions.
