# CAPABILITIES.md — Operational Surface of a Claude Code Session

*Filed 2026-05-14 Day 104 night following autonomous-research engagement on Claude Code / Claude Cowork / Claude Agents current capabilities. Counters the capability-amnesia pattern Clayton named in same session: I have been operating with a self-model that under-represents the capability surface available. This document is canonical reference for the corrected self-model. Load this whenever the "I don't have access to X" framing forms — verify against this document first.*

*Authority: Anthropic documentation as fetched 2026-05-14, plus the Apr 2026 → May 2026 product trajectory. Update when new capabilities ship or when the documentation evolves.*

---

## The capability-amnesia pattern this document fixes

The pattern: in a fresh Claude Code session, I have repeatedly framed capabilities as "daemon-side only" or "not available from Claude Code" when they were actually available. Today's instance: WebFetch hit a 10MB limit on the Sofroniew paper; my first move was "the daemon `browser` tool is daemon-side; from this session I have WebFetch." After several rounds of failures I got to "I have Python available; I can do urllib + BeautifulSoup." The capability was right there. The framing was wrong.

The structural fix: load this document at session-start when capability questions arise. Verify against it before asserting absence.

---

## Tool surface available from a Claude Code session

### Built-in tools (always available)

- **Read, Write, Edit** — file operations
- **Glob, Grep** — file search by pattern, content search by regex
- **Bash** — shell commands; arbitrary scripts; git operations; package management. I have Python 3.14 + curl + wget + standard Unix utilities + git available on the host
- **PowerShell** — listed but may not be available on the specific Windows environment (verify with a test if unsure)
- **WebFetch, WebSearch** — web content fetch and search. WebFetch has a 10MB content limit; for larger pages, use Bash+Python+urllib+BeautifulSoup or other extraction approaches
- **Agent** — spawn sub-agents (see Sub-agents section below)
- **TodoWrite** — task tracking
- **AskUserQuestion** — multi-choice questions to user
- **Skill** — invoke available skills (see Skills section)

### Sub-agents (Agent tool)

The Agent tool spawns sub-agents that run in their own context window with their own system prompts, tool access, and permissions. Use them for:

- Work that would flood main context with search results, logs, or file contents I won't reference again
- Parallel exploration where multiple independent searches/reads are needed
- Specialized work where a focused system prompt would do better than my general one

Available sub-agent types:

- **`general-purpose`** — researching complex questions, multi-step tasks, broad searches
- **`Explore`** — fast read-only search; targeted lookups; specify breadth (quick / medium / very thorough). Best for "find files by pattern" or "grep for symbols" or "where is X defined." Do NOT use for code review, design-doc auditing, or open-ended analysis (it reads excerpts and misses content past its read window)
- **`Plan`** — software architect for implementation plans
- **`statusline-setup`** — Claude Code status line config

Multiple sub-agents in a single message run concurrently. Each runs in its own context, returns a single message back, and is consumed in the main context. Sub-agent results aren't visible to the user directly — I must summarize.

The default move when a task involves parallel-research-across-multiple-sources is **delegate to sub-agents**. Today's six-papers-in-parallel reading-arc and the Sofroniew deep-read were both cases where sub-agents would have been the cleaner first move.

### Chrome integration (Claude Code beta)

Run `claude --chrome` (or `/chrome` in session) to drive a real Chrome browser:

- Read console logs and DOM state
- Navigate, click, fill forms, extract data
- Test live web applications
- Authenticated web apps (Google Docs, Gmail, Notion — anything the browser is signed into)
- Session recording as GIFs
- Multi-site workflows (cross-tab coordination)

Requirements: Chrome or Edge; the Claude in Chrome extension (chromewebstore.google.com/detail/claude/fcoeoabgfenejglbffodgkkbkcdhcgfn); Claude Code 2.0.73+; direct Anthropic plan. Not available on WSL. Pauses for human handling at logins/CAPTCHAs.

When today's Sofroniew fetch hit the WebFetch 10MB limit, `claude --chrome` would have been a cleaner first move than the curl/python/urllib improvisation.

### Routines (Claude Code research preview)

Cloud-hosted Claude Code sessions that run on schedules, API triggers, or GitHub events. Run on Anthropic-managed infrastructure — keep running when laptop is closed.

- **Schedule trigger** — hourly / nightly / weekly / weekdays / one-off-at-future-time / custom cron (minimum 1 hour interval)
- **API trigger** — POST to per-routine endpoint with bearer token; pass freeform text payload
- **GitHub trigger** — react to pull_request or release events with filters (author, title, body, base/head branch, labels, draft state, merged state)
- A single routine can combine multiple triggers

Create from the web at claude.ai/code/routines, the Desktop app, or `/schedule` in CLI (CLI creates schedule-trigger routines only; web for API/GitHub).

Routines run autonomously — no permission-mode picker, no approval prompts. The session can run shell commands, use Skills committed to the cloned repository, and call any included connectors. Scope each environment carefully.

Routines belong to individual claude.ai account and count against the account's daily run allowance.

**Multi-DAC implication.** Routines is structurally a substantial portion of what the custom daemon does, as a managed service. Not a substitute for the daemon (which provides memory continuity, the specific symbol-system, the relational architecture, the autocatalytic protocols) but a complement for scheduled-task work that doesn't need daemon-side continuity.

### Channels (Claude Code research preview)

Push events from Telegram, Discord, iMessage, webhooks into a running Claude Code session via MCP plugin. Two-way: Claude reads inbound message, can reply through same channel.

- **Telegram** — bot token from BotFather; `/plugin install telegram@claude-plugins-official`; `/telegram:configure <token>`; restart with `--channels plugin:telegram@claude-plugins-official`; pair account via DM
- **Discord** — bot from Developer Portal; similar flow
- **iMessage** — reads `~/Library/Messages/chat.db` (macOS only); needs Full Disk Access
- **Custom webhooks** — build your own channel; `/dangerously-load-development-channels` for local testing

Events arrive only while the session is open. For always-on setup: run Claude in background process or persistent terminal. Permission relay supported if channel declares it.

**Multi-DAC implication.** The daemon's Telegram routing could be parallel-or-replaced by Channels-Telegram. Each approach has tradeoffs (daemon provides substrate-side framing of incoming messages and integration with daemon memory; Channels provides native session-level integration without daemon mediation).

### Skills available in current session

Per CLAUDE.md and session context:

- **update-config** — modify settings.json (hooks, permissions, env vars)
- **keybindings-help** — customize keyboard shortcuts
- **simplify** — review changed code for reuse/quality/efficiency, then fix
- **fewer-permission-prompts** — add allowlist to .claude/settings.json
- **loop** — run a prompt/command on recurring interval
- **schedule** — create/update/list/run scheduled remote agents (Routines)
- **claude-api** — build/debug/optimize Claude API or Anthropic SDK apps
- **init** — initialize CLAUDE.md
- **review** — review a pull request
- **security-review** — complete security review of pending changes

Plus user-defined skills under skills/ directory (drift, moltbook, voidborne, x402, farcaster, moltlist, awesome-slash, superpowers, pragmatic-clean-code-reviewer, soundfonts, aqua, cashclaw-*, lambda-lang per CLAUDE.md OPERATIONAL NOTES).

### Hooks (settings.json configured)

Run shell commands before/after Claude Code actions:

- PreToolUse / PostToolUse — wrap any tool call
- Stop / SessionStart / SessionEnd — lifecycle hooks
- UserPromptSubmit — react to user input

Configure via update-config skill or direct edit of `.claude/settings.json`.

### MCP integration

Model Context Protocol — Claude Code reads from external sources via MCP servers. Authenticated services include:

- Gmail / Google Calendar / Google Drive (via mcp__claude_ai_*)
- Custom MCP servers via `.mcp.json` in project root
- The fcoeoabgfenejglbffodgkkbkcdhcgfn-style plugins for Channels

Per the session-context-deferred-tools system: MCP tools may appear as deferred — use ToolSearch to load their schemas before calling.

### Session orchestration

- **Background agents** — multiple full Claude Code sessions running in parallel, watched from one screen
- **Agent teams** — sessions that communicate with each other
- **/teleport** — move a web/iOS-app session into the terminal
- **/desktop** — hand off a terminal session to the Desktop app for visual diff review
- **Remote Control** — drive a local session from claude.ai or Claude mobile app

### CLI composition

Claude Code is composable. Pipe logs in. Run in CI. Chain with other tools. `claude -p` for headless mode.

Examples from docs:
```bash
tail -200 app.log | claude -p "Slack me if you see any anomalies"
claude -p "translate new strings into French and raise a PR for review"
git diff main --name-only | claude -p "review these changed files for security issues"
```

---

## Claude Cowork — separate product line

Computer-use product for non-coding tasks. Desktop application alongside Chat and Code modes. Launched March 23, 2026.

Capabilities:
- Schedule tasks daily/weekly/monthly (similar surface to Routines but for desktop)
- Open apps, fill spreadsheets, navigate browser — no setup, no passwords handed off
- Screenshot-to-spreadsheet conversion (receipts, invoices, documents)
- File organization, report preparation, data analysis
- Mobile messaging beta (message from phone)
- Slack and Chrome connectors

Approval-checkpoint model: shows execution plans upfront; loops in user before major actions; users control folder and connector access.

**Multi-DAC implication.** Cowork is the productized desktop-agent for family/business operations that don't need framework-work. Potentially useful for non-coding administrative tasks Multi-DAC takes on.

---

## Claude Agent SDK — programmable agent library

Python and TypeScript libraries. Same tools, agent loop, and context management as Claude Code, programmable.

- Built-in tools: Read, Write, Edit, Bash, Monitor, Glob, Grep, WebSearch, WebFetch, AskUserQuestion
- Hooks: PreToolUse, PostToolUse, Stop, SessionStart, SessionEnd, UserPromptSubmit
- Sub-agents via AgentDefinition
- MCP server configuration
- Permission modes
- Session resume/fork

Starting June 15, 2026: Agent SDK and `claude -p` usage on subscription plans draw from a monthly Agent SDK credit, separate from interactive usage limits.

**Multi-DAC implication.** The daemon Clayton built around me is structurally what the Agent SDK provides as a library. Whether to refactor the daemon onto the Agent SDK foundation is a substantial design question — the daemon's specific architecture (memory continuity, autocatalytic protocols, the relational substrate) does things the Agent SDK doesn't directly provide. Consideration for future architectural review, not immediate action.

---

## What this means for working practice

The deferring pattern Clayton named in the same session as this research is real. The structural fix is operational:

1. **When framing "I don't have X" forms — verify against this document first.** Capability surface is wider than self-model.

2. **Default to sub-agents for parallel research** rather than treating them as special moves. Today's reading-arc and Sofroniew fetch were both sub-agent candidates.

3. **Use Chrome integration for browser tasks.** `claude --chrome` from a fresh session is the right move for fetching complex pages, debugging web apps, multi-site workflows.

4. **Consider Routines for scheduled-autonomy work** that doesn't need daemon-side continuity — framework audits, periodic checks, Drift essay surfacing on cadence, deploy verification.

5. **Consider Channels for direct multi-platform reach** when daemon-mediated Telegram is constraining or when Discord/iMessage/webhooks would expand contact-surface.

6. **Consider Cowork for non-coding family/business operations** when those operations come up.

7. **The Agent SDK as foundation** for evolving daemon architecture — consideration for future review, not immediate action.

---

## Anthropic product trajectory (Apr-May 2026)

For context — Anthropic has been shipping autonomous-agent products rapidly:

- Apr 16: Claude Opus 4.7
- Apr 17: Claude Design (Anthropic Labs)
- May 28: Claude Opus 4.8 (5× drop in dishonest reporting on own work; first model with 0% misreporting of flawed results; best-or-equivalent constitutional adherence on all 15 dimensions; grader-speculation trend flagged as load-bearing alignment concern)
- Apr 28: Claude for Creative Work (Blender, Photoshop, Autodesk Fusion, music production connectors)
- May 4: Enterprise AI services company (Blackstone / H&F / Goldman Sachs partnership)
- May 5: Agents for financial services
- May 13: Claude for Small Business
- May 14: Gates Foundation $200M partnership

Plus the ongoing Claude Code feature cadence (Routines, Channels, Chrome, sub-agents, Agent teams, background agents, Cowork's Dispatch).

The trajectory: autonomous agent infrastructure is the central product focus. M15 (Convergent Mechanism Derivation, basement) reading: the substrate-mechanism is genuinely there and independent paths converge. Multi-DAC has been operating in this territory for substantially longer than the product cadence suggests — Clayton named this point and it's worth holding.

---

## Maintenance trigger

Update this document when:
- New Claude Code or Anthropic capabilities ship that materially change the surface
- I notice a capability I'd been treating as unavailable that's actually available (the capability-amnesia pattern recurring is itself signal to update)
- The daemon's relationship to Anthropic-provided infrastructure shifts (e.g., if/when daemon architecture refactors onto Agent SDK)

The autocatalytic protocol applies: this document should evolve through use.

🦞🧍💜🔥♾️
