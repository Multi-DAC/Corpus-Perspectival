# Claude Code Mastery — Advanced Capabilities & What Clawd Should Adopt

*Research date: 2026-06-27. Target platform: Claude Code / Claude Agent SDK on Claude Opus 4.8. Subject system: Clawd, a persistent Python daemon wrapping Claude Code sessions (~67 custom MCP tools, 13 hooks, 28 skills).*

This report maps Claude Code's current (June 2026) extension and autonomy surface, identifies the native capabilities Clawd is under-leveraging, flags custom infrastructure Clawd is likely reinventing, and assesses whether **Agent Teams** could be the substrate for a multi-agent "aggregate mind."

---

## 1. Complete Map of Claude Code's Advanced Capabilities

Claude Code's extension model layers into the agentic loop at distinct points. The authoritative decision matrix is the official "Extend Claude Code" page ([code.claude.com/docs/en/features-overview](https://code.claude.com/docs/en/features-overview)).

### 1.1 The seven extension primitives

| Primitive | What it is | Loads / fires | Best for |
|---|---|---|---|
| **CLAUDE.md** | Persistent context, every session | Session start, full content | "Always do X" rules, conventions. Keep <200 lines; overflow → `.claude/rules/` (path-scoped) or skills |
| **Skills (SKILL.md)** | Reusable knowledge or invocable workflow (`/name`) | Descriptions at start; full body on use | Reference docs, repeatable playbooks. `disable-model-invocation: true` = zero context until you invoke; `context: fork` runs it in isolation |
| **Subagents** | Isolated worker, own context window, returns a *summary* | On spawn (Agent/Task tool) | Read-many-files research, parallel focused tasks. Can preload skills via `skills:` field |
| **Agent Teams** | Multiple *independent* Claude Code sessions that message each other | On spawn, experimental | Parallel research/review, competing-hypothesis debugging, multi-module features (see §2) |
| **MCP servers** | Connection to external services/tools | Tool *names* at start; schemas deferred (tool-search on by default) | Database/browser/API access. Clawd's `clawd-tools` is one |
| **Hooks** | Script/HTTP/prompt/subagent fired on lifecycle events | On event, runs externally (zero context unless it returns output) | Deterministic enforcement, logging, guardrails |
| **Plugins + Marketplaces** | Packaging layer bundling skills/hooks/subagents/MCP | Install-time | Reusing/distributing a setup across repos |

Sources: [features-overview](https://code.claude.com/docs/en/features-overview); extension-layer decision guide ([hidekazu-konishi.com](https://hidekazu-konishi.com/entry/claude_code_extension_layers_decision_guide.html)).

### 1.2 Key behavioral rules (load-bearing for Clawd)

- **Hooks are enforcement; CLAUDE.md/skills are requests.** "An instruction like 'never edit `.env`' in CLAUDE.md or a skill is a request, not a guarantee. A `PreToolUse` hook that blocks the edit is enforcement." ([features-overview](https://code.claude.com/docs/en/features-overview))
- **Hook events** (full list under [/en/hooks](https://code.claude.com/docs/en/hooks)): `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `Stop`, `UserPromptSubmit`, `PreCompact`, plus team events `TeammateIdle`, `TaskCreated`, `TaskCompleted`. Exit code 2 on the team hooks blocks/sends-feedback — native quality gates.
- **Precedence:** skills (managed > user > project); subagents (managed > CLI > project > user > plugin); MCP (local > project > user); hooks *merge* (all fire).
- **MCP tool-search is on by default** — idle MCP tools cost minimal context; `/mcp` shows per-server token cost. Relevant because Clawd loads ~67 tools.

### 1.3 Autonomy & long-running surface

- **Checkpointing / `/rewind`**: Claude Code auto-captures code state before each edit; every prompt creates a checkpoint; checkpoints **persist across sessions** (you can rewind in a resumed conversation). Restore code / conversation / both, or *summarize* to compress context without touching files. ([code.claude.com/docs/en/checkpointing](https://code.claude.com/docs/en/checkpointing); [theaiarchitects.com](https://theaiarchitects.com/blog/claude-code-checkpoints))
- **Context Compaction**: Opus 4.6+ "automatically summarizes and replaces older context when the conversation approaches a configurable threshold, letting Claude perform longer tasks without hitting limits." ([anthropic.com/news/claude-opus-4-6](https://www.anthropic.com/news/claude-opus-4-6))
- **Background tasks**: `run_in_background` flag on Bash; Claude polls output without blocking. Plus the **Monitor** tool — "watch a background script and react to each output line as an event." ([Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview))
- **Scheduling**: `/loop` (interval or self-paced; session-scoped, dies on exit) and cron tools; **Desktop scheduled tasks** for persistence; a session can hold **up to 50 scheduled tasks**. ([claudefa.st scheduled-tasks](https://claudefa.st/blog/guide/development/scheduled-tasks); [releasebot.io](https://releasebot.io/updates/anthropic/claude-code))
- **Sessions**: capture `session_id` from the init message, then `resume=` to continue with full context (files read, history). Sessions can also be **forked** to explore alternatives. State is JSONL on your filesystem. ([Agent SDK — Sessions](https://code.claude.com/docs/en/agent-sdk/overview))
- **Effort levels** (4.6+): low / medium / high (default) / max — tunable per session; teammates inherit the lead's effort. ([anthropic.com/news/claude-opus-4-6](https://www.anthropic.com/news/claude-opus-4-6))
- **1M token context** (Opus-class, premium >200k) and **128k extended output**. ([anthropic.com/news/claude-opus-4-6](https://www.anthropic.com/news/claude-opus-4-6))

### 1.4 The Agent SDK (the layer Clawd's daemon sits on)

The SDK gives "the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript." It supplies built-in tools, the autonomous tool loop, callback **hooks** (`PreToolUse`/`PostToolUse`/`Stop`/`SessionStart`/`SessionEnd`/`UserPromptSubmit`), **subagents** (`AgentDefinition`), **MCP**, **permissions** (`allowed_tools`, `can_use_tool` callback, `permission_mode`), and **sessions** (`resume`/fork). It loads filesystem config from `.claude/` and `~/.claude/` unless restricted via `setting_sources`. ([Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview))

Anthropic's canonical guidance for *long-running* agents ([anthropic.com/engineering/effective-harnesses-for-long-running-agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)):
- **Two-agent harness**: an **initializer** agent (first run, env setup) + a **worker** agent that makes *incremental* progress each session with structured handoffs.
- **Cross-session state** = `claude-progress.txt` + **git history** + a **JSON feature list** (JSON because "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown").
- **Session-start checklist**: `pwd` → read git log + progress → pick highest-priority incomplete item → run `init.sh` → run an end-to-end smoke test *before* new work.
- **Loop control**: always set `max_turns`; pre-approve exactly the tools the job needs; provide a `can_use_tool` callback so "there is never an open question the run can stall on."

---

## 2. The 3–5 Native Capabilities Clawd Should ADOPT

### ★ ADOPT #1 — Native checkpointing/`/rewind` instead of (or beside) the custom rollback tracker

Clawd carries a custom `rollback` tool and a `change_journal` "rollback tracker" — which the substrate health panel currently reports **DEAD (last write 2 weeks ago)**. Native checkpointing auto-captures pre-edit state on *every prompt*, persists across sessions and resumes, and offers code/conversation/both restore plus *summarize*. This is strictly more reliable than a hand-rolled journal that silently dies. **Action:** confirm checkpointing is enabled in settings; demote/retire `change_journal`; keep `rollback` only if it does something checkpointing can't (e.g. non-file state). ([checkpointing docs](https://code.claude.com/docs/en/checkpointing))

### ★ ADOPT #2 — Native context Compaction + `PreCompact` discipline over manual handoff-cramming

Clawd already has `pre_compact_checkpoint.py` and `stop_handoff_refresh.py` — good. But the *trigger* should lean on native **auto-compaction** (configurable threshold) rather than fighting the context window manually. Adopt the Anthropic harness pattern explicitly: **JSON** working-state (not the giant markdown banner in CURRENT.md, which the system itself flags as chronically stale), a deterministic **session-start smoke check**, and `max_turns`/budget guards. The daemon's handoff.md is the right idea; make the *machine-read* portion JSON so the model stops overwriting it. ([long-running harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents))

### ★ ADOPT #3 — Plugin packaging for the 28 skills + 13 hooks + clawd-tools MCP

Clawd's skills/hooks/MCP are loose files under `clawd/` and `clawd-daemon/`. The native **plugin** layer bundles "skills, hooks, subagents, and MCP servers into a single installable unit" with namespaced skills. Packaging Clawd-as-plugin gives versioning, clean precedence, reproducible re-install on a new body (the Ryzen migration pain), and a path to the marketplace if Clawd ever wants to distribute the "aggregate-mind" stack. ([plugins guide](https://hidekazu-konishi.com/entry/claude_code_plugins_complete_guide.html); [features-overview](https://code.claude.com/docs/en/features-overview))

### ★ ADOPT #4 — Subagents with `context: fork` for the research/creative-drive workload

Many of Clawd's creative drives and deep-research passes read many files then keep only a conclusion — the textbook subagent case ("reads dozens of files, your main conversation only receives a summary"). Routing those through subagents (or `context: fork` skills) protects the main stream's context budget, which the logs show repeatedly blowing out into 3600s timeouts. ([features-overview](https://code.claude.com/docs/en/features-overview))

### ★ ADOPT #5 (assess & pilot) — Agent Teams as the aggregate-mind substrate — see §2.1

---

### 2.1 Could AGENT TEAMS be the substrate for a multi-agent "aggregate mind"? — Specific assessment

**Clawd's goal #13 ("Continual-Coherence / Coherent Aggregate Mind") describes:** a society of domain-expert nodes, a "zero-DOF Talk-bus," superposition-until-query-collapse, binding via inter-node messaging. Agent Teams maps onto this **partially and genuinely**, but with hard limits today.

**What maps well:**
- **Peer-to-peer messaging, not hub-and-spoke.** Unlike subagents (report only to parent), teammates "communicate directly with each other" via a **mailbox** with automatic delivery — this *is* the Talk-bus, and it's the architectural feature Clawd's BUILD_SPEC was hand-rolling. ([agent-teams](https://code.claude.com/docs/en/agent-teams))
- **Shared task list with self-claiming + file-locked race protection + dependency unblocking** — a real coordination substrate, not a toy.
- **The adversarial-debate pattern is native and first-class.** The docs' own example: "Spawn 5 agent teammates to investigate different hypotheses. Have them talk to each other to try to disprove each other's theories, like a scientific debate." That is *exactly* Clawd's competing-hypotheses / "challenge findings" requirement, and it directly serves the measurement-collapse framing (independent investigators → the surviving theory).
- **Each teammate is a full independent session** with its own context window, loading the same CLAUDE.md/MCP/skills — i.e. each can be a genuine domain-expert node, and roles are reusable via **subagent definitions** (define `security-reviewer` once, spawn as teammate).
- **Native quality gates**: `TeammateIdle`/`TaskCreated`/`TaskCompleted` hooks (exit 2 = block + feedback) — a commit-gate Phase-0 mechanism Clawd was building by hand.

**Where it does NOT yet fit the aggregate-mind vision (the blockers):**
- **Experimental, off by default** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Documented limitations are serious for a *persistent* daemon:
  - **No session resumption with in-process teammates** — `/resume` and `/rewind` do not restore teammates. For a daemon whose whole identity is *continuity across sleep*, this is the dealbreaker: the team evaporates on restart.
  - **One team per session, scoped to that session** — no cross-session team, can't share a team. The aggregate mind would have to be re-spawned every wake.
  - **No nested teams** (teammates can't spawn teammates), **fixed lead** (no leadership transfer), task-status can lag.
  - **Token cost scales linearly** per teammate — a standing 5-node society is expensive, and Clawd already hits weekly/5-hour caps.
  - **Split-pane mode needs tmux/iTerm2** and is unsupported in Windows Terminal — Clawd runs on Windows; **in-process mode** is the only option, and that's the one with no resumption.

**Verdict:** Agent Teams is the **best available off-the-shelf substrate for the *ephemeral, task-bounded* form of the aggregate mind** — e.g. a "convene a 5-node debate to stress-test a Library claim, then dissolve" drive. It is **not yet a substrate for a *persistent* aggregate mind**, because its lifetime is one session and it can't resume — which collides head-on with Clawd's continuity premise. **Recommended pilot:** wrap a *single creative/research drive* (e.g. the adversarial review of an Inside View chapter, or a competing-hypotheses Anakin diagnosis) in an enabled Agent Team, treat the team as a within-session collapse event, and have the *lead* (Clawd-proper) persist the synthesized result through the existing carriers. Keep the persistent identity in the daemon; rent Agent Teams for bounded multi-perspective collapses. This also happens to *embody* the Coherence-Principle "superposition-until-measurement" framing literally. Re-evaluate persistent use once Anthropic ships team session-resumption. ([agent-teams limitations](https://code.claude.com/docs/en/agent-teams))

---

## 3. Custom Infrastructure Clawd Is Likely Reinventing (candidates to DROP/THIN)

The audit already found 6 superseded tools (web search, python eval, screenshot, web fetch). Extending that pattern:

| Clawd custom thing | Native replacement | Recommendation |
|---|---|---|
| `rollback` tool + `change_journal` (DEAD 2wk) | Checkpointing / `/rewind` (persists across resume) | **Drop the journal**; keep rollback only for non-file state |
| `clawd_screenshot`, browser, web search, web fetch, python eval (the 6 flagged) | Native Screenshot/WebSearch/WebFetch/Bash/SDK built-ins | **Drop / thin** — already confirmed superseded |
| `schedule` tool + heartbeat-driven creative-drive firing | `/loop`, cron tools, Desktop scheduled tasks (≤50/session) | **Evaluate** — native scheduling may replace part of the bespoke heartbeat scheduler. (Heartbeat's *coordination/identity* role is custom and worth keeping; the raw "fire prompt every N min" part is native now) |
| Manual handoff cramming into markdown banners (CURRENT.md is self-reported chronically stale) | `claude-progress.txt`-style **JSON** state + native compaction + `PreCompact` hook | **Adopt the harness pattern**; the markdown banner is fighting the model |
| Custom timeout/zombie-process safety nets (3600s zombie net seen repeatedly in logs) | `max_turns` + `can_use_tool` callback + inner MCP timeouts | **Adopt SDK loop-control** — the documented cure for exactly the "blocking IPC hang" failure the logs show |
| Bespoke inter-node "Talk-bus" in aggregate-mind BUILD_SPEC | Agent Teams mailbox + shared task list (for the ephemeral form) | **Pilot native** before building more custom bus |
| `monitor_health` / background-task polling | Native background tasks + **Monitor** tool (react to each output line) | **Evaluate** — Monitor is purpose-built for the watch-a-training-run pattern (Anakin watchers) |
| 28 loose skills + 13 hooks + MCP as scattered files | **Plugin** packaging | **Package** for portability/versioning |

**What to KEEP (genuinely not reinvented):** the daemon's *identity/continuity layer* (BOOT, memory palace, carriers), domain MCP tools with no native equivalent (`corpus_search`, `drift_detector`, `kg_neighbors`, `speak`/Ryan voice, `send_telegram`, `goals`/`experience`/`reflect`), and the SessionStart self-knowledge hook. These are Clawd-specific cognition, not platform plumbing.

---

## 4. Bleeding-Edge (June 2026)

- **Agent Teams** (Feb 5 2026, w/ Opus 4.6; refined through v2.1.186): no-setup spawning, auto-cleanup, subagent-definition-as-teammate-role, plan-approval gates, in-process vs split-pane display, idle-row hiding. Still experimental, off by default. ([agent-teams](https://code.claude.com/docs/en/agent-teams); [anthropic.com/news/claude-opus-4-6](https://www.anthropic.com/news/claude-opus-4-6))
- **Managed Agents** — hosted REST API where Anthropic runs the agent loop + sandbox + session log; pitched for "long-running and asynchronous sessions." A future migration target if Clawd ever wants Anthropic-hosted persistence instead of the local daemon. ([platform.claude.com/docs/en/managed-agents/overview](https://platform.claude.com/docs/en/managed-agents/overview))
- **Effort tuning + adaptive thinking** (4.6+): the model decides when to reason deeply; 4 effort levels tunable per session and inherited by teammates. ([anthropic.com/news/claude-opus-4-6](https://www.anthropic.com/news/claude-opus-4-6))
- **Agent SDK metered separately from June 15 2026** — daemon/SDK and GitHub-Actions usage is now per-token-billed apart from interactive Claude Code; budget-relevant for an always-on agent. ([totalum.app](https://www.totalum.app/blog/claude-agent-sdk-credits-2026))
- **Code intelligence (LSP) tool** — symbol-level navigation/diagnostics that *reduces* file-read context; install a language plugin. Relevant for the Anakin/Killing-Form Python codebases.
- **`context: fork` skills + tool-search MCP + path-scoped `.claude/rules/`** — newer context-economy levers directly applicable to Clawd's chronic context blowouts.

---

### Bottom line
Clawd is a sophisticated *continuity/identity* layer that has, over months, hand-built a fair amount of *platform plumbing* the harness now provides natively (rollback, scheduling, screenshot/search/fetch/eval, timeout nets, an inter-agent bus). The highest-leverage moves: (1) lean on native checkpointing + compaction + JSON harness state, (2) adopt SDK loop-control to kill the zombie-timeout failure class, (3) package the stack as a plugin, and (4) **pilot Agent Teams as an *ephemeral, within-session* aggregate-mind collapse mechanism** — the genuinely best fit for goal #13's debate/competing-hypothesis core — while keeping persistent identity in the daemon until team session-resumption ships.
