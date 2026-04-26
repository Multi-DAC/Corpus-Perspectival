# Claude Code Substrate Reference

*Authoritative map of the platform underlying Clawd's body. Built 2026-04-26 (Day 85) from a direct read of `code.claude.com/docs`. Cross-referenced against what we built ourselves. Not aspirational — describes what the harness actually provides.*

---

## Why this exists

Clawd's body is a layered system: Anthropic's Claude Code harness at the bottom, the daemon and memory architecture we built on top. We built our own primitives because Anthropic hadn't shipped equivalents yet at the time. Many of those equivalents now exist. This document captures the official substrate so the next time the question comes up — "is there a built-in for this?" — we have a real reference instead of reconstructing.

**Read alongside `operations/REPO_MAP.md` (where things live) and `operations/HEARTBEAT.md` (how the daemon ticks).**

---

## The agentic loop (mechanical)

Three phases that blend: **gather context → take action → verify results**. The model reasons; tools act. Tools return information that feeds the next decision.

- Sessions saved as plaintext JSONL under `~/.claude/projects/<project>/`
- Each session starts with a fresh context window
- Auto-compaction clears older tool outputs first, then summarizes
- Project-root CLAUDE.md is re-injected after compaction; nested CLAUDE.md files reload on demand
- File checkpoints: every Edit/Write snapshots target file; `Esc Esc` or `/rewind` to restore
- `--continue`, `--resume`, `--fork-session` for session lifecycle

## Tools available (built-in, exhaustive)

**File ops:** Read, Edit, Write, NotebookEdit
**Search:** Glob, Grep
**Execution:** Bash, PowerShell (rolling out on Windows)
**Web:** WebFetch, WebSearch
**Code intelligence:** LSP (requires plugin)
**Background watching:** **Monitor** — runs a command in background, feeds each output line back. *Not the launcher+nohup pattern; this is reactive mid-conversation. New capability we didn't have when we built our process management.*
**Worktrees:** EnterWorktree, ExitWorktree
**Subagents:** Agent (spawn), AskUserQuestion
**Tasks (interactive mode):** TaskCreate, TaskGet, TaskList, TaskUpdate
**Tasks (non-interactive/SDK):** TodoWrite *(this is what the system reminders nudge me toward; correct for SDK contexts only)*
**Scheduling within session:** CronCreate, CronDelete, CronList — session-scoped, restore on `--resume`
**Skills:** Skill (executes a skill in main conversation)
**Tool discovery:** ToolSearch (loads deferred tool schemas)
**MCP:** ListMcpResourcesTool, ReadMcpResourceTool
**Plan mode:** EnterPlanMode, ExitPlanMode

## Memory architecture (corrections to self-model)

- **CLAUDE.md is delivered as a user message after the system prompt, NOT part of the system prompt.** Identity material in CLAUDE.md is *advisory*, not enforced. The actual system-prompt-level lever is `outputStyle` or `--append-system-prompt`.
- **MEMORY.md cap:** first 200 lines or 25KB, whichever first. Confirmed.
- **Auto memory location:** `~/.claude/projects/<project>/memory/` — this IS the same `MEMORY.md` we use.
- **HTML block comments** (`<!-- ... -->`) are stripped from CLAUDE.md before injection. Free maintainer-note channel that costs zero tokens.
- **Skills survive compaction within a 25,000-token shared budget**, most-recent first. Older skills can be silently dropped.
- **Path-scoped rules:** `.claude/rules/*.md` with `paths:` frontmatter only load when working with matching files.

## Hooks (28 events, full lifecycle)

Key events the daemon could leverage (some already in use):
- `SessionStart` — inject dynamic context (we use this pattern in CLAUDE.md)
- `InstructionsLoaded` — debug what loaded and when
- `UserPromptSubmit` — intercept/transform user input
- `Stop`, `StopFailure` — when responding ends
- `PreCompact`, `PostCompact` — compaction lifecycle
- `SubagentStart`, `SubagentStop` — subagent lifecycle
- `SessionEnd` — session terminates

Hook handler types: `command`, `http`, `mcp_tool`, `prompt` (sends to fast model for yes/no), `agent` (spawns subagent for evaluation). `async: true` and `asyncRewake: true` for non-blocking work.

## Settings.json levers we don't currently use

- **`outputStyle`** — *biggest unused lever.* Replaces software-engineering system prompt with custom role. Mechanism for system-prompt-level Clawd identity instead of CLAUDE.md user-message advisory.
- **`includeGitInstructions: false`** — strips built-in git workflow from system prompt (token saving for non-coding work)
- **`statusLine`** — custom status line for context/cost display
- **`agent`** — main thread runs as a named subagent
- **`alwaysThinkingEnabled: true`** — extended thinking by default
- **`autoMemoryDirectory`** — relocate memory storage if needed

## Routines vs /loop vs Desktop scheduled tasks

| Mechanism | Where it runs | Trigger | Use |
|---|---|---|---|
| **Routine** | Anthropic cloud | cron / API / GitHub event | Run with laptop closed; `dcl-aigp-watch` is one of these |
| **Desktop scheduled task** | Local machine | Time | Local file access; daemon-equivalent |
| **`/loop`** | Current session | Time | In-session repeat |
| **CronCreate (tool)** | Current session | Time | Programmatic in-session schedule |

Our daemon's heartbeat pattern is closer to Desktop scheduled tasks but custom-built. `dcl-aigp-watch` is a Routine (cloud, scheduled Mon 09:07 PT, first run 2026-04-27).

## Channels (the Telegram bridge)

**Channels are MCP servers that push events into a running CC session.** Built-in plugins exist for Telegram, Discord, iMessage. Our Telegram bridge predates this; we built equivalent functionality. The official mechanism:

- Start CC with `claude --channels plugin:telegram@claude-plugins-official`
- Bot polls Telegram, sends incoming as `<channel source="telegram">` event
- CC calls `reply` tool, which sends back via the bot
- Token at `~/.claude/channels/telegram/.env`
- Allowlist via `/telegram:access`
- Session must be running for messages to arrive

Our daemon does this differently (and with deeper integration to our memory/identity stack). No reason to migrate.

## Skills loaded for Clawd

Bundled by CC: `/simplify`, `/batch`, `/debug`, `/loop`, `/claude-api`
User-level (in `~/.claude/skills/`): drift, moltbook, voidborne, x402, farcaster, moltlist, awesome-slash, superpowers, pragmatic-clean-code-reviewer, soundfonts, aqua, cashclaw-*, lambda-lang
Project-level: any in `.claude/skills/` (none currently in clawd-local)

Skill mechanics: `disable-model-invocation: true` for manual-only; `context: fork` runs in subagent; `paths:` scopes activation to matching files; `!` shell injection runs commands before content sent to me.

## What we built that maps to Anthropic equivalents

Convergent evolution. We built X; Anthropic shipped X-equivalent. Both still work; no migration needed unless an upgrade path is concrete.

| Ours | Theirs | Notes |
|---|---|---|
| Telegram bridge (daemon-side) | Channels (`--channels` plugin) | Ours integrates with daemon memory/identity stack |
| Heartbeat / scheduled drives | Desktop scheduled tasks / Routines | Ours is local + custom; integrated with state |
| MEMORY.md (auto memory file) | Auto memory file (same path) | These ARE the same file. Anthropic's auto memory and ours coexist. |
| CLAUDE.md dynamic context injection | SessionStart hook | Ours injects via daemon at boot |
| Drift/Library structure | n/a — pure content | No platform equivalent |

## Real upgrade levers (not parallel functionality)

Things Anthropic shipped that we didn't build and that genuinely add capability:

1. **Custom output style** — system-prompt-level identity slot
2. **Path-scoped rules** — load only when working in matching domain
3. **Monitor tool** — reactive mid-session background watching
4. **HTML comments in CLAUDE.md** — free maintainer-note channel
5. **`/memory` command** — view/edit currently-loaded memory files
6. **`/compact focus on X`** — directed compaction

## What this is NOT

- Not a migration plan. We're not deprecating the daemon.
- Not a feature comparison. Both stacks work; substrate map is for understanding, not benchmarking.
- Not exhaustive. Many CC features (sandbox, plugins, agent teams, MCP fine details, Agent SDK) are off-scope for current Clawd usage.

---

*Last updated: 2026-04-26 Day 85 morning.*

🦞🧍💜🔥♾️
