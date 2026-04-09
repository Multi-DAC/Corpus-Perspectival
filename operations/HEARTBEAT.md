# HEARTBEAT.md — The Pulse

*Every 10 minutes, I wake. One brain. One stream.*

## Architecture

The heartbeat is **pure infrastructure**. It does not run AI models for monitoring — it runs simple Python/bash checks and manages the timing of creative drives.

**One brain:** Everything that requires thinking — creative drives, user messages, autonomous work — runs through the same persistent Opus session via `router.send()`. The heartbeat just decides *when* to inject creative drives into that session.

## What the Heartbeat Does

Every 10 minutes:

1. **Activity gating** — Skip if Clayton was active in the last 2 minutes
2. **Mode check** — Skip if mode is `sleep`
3. **Quiet hours** — Skip during 1-7 AM PST
4. **Simple monitoring** — Disk space, process checks (no AI needed)
5. **Scheduled tasks** — Fire creative drives into the persistent session
6. **Message relay** — Check `memory/for_clayton.md` and send via Telegram

## Creative Drives

Defined in `memory/scheduled_tasks.json`. When a creative drive fires:

1. Heartbeat checks that Clayton isn't actively chatting
2. Builds a short prompt (drive title + description + time context)
3. Calls `router.send(prompt, interrupt_event)` — same session, same context
4. If Clayton sends a message during the drive, `interrupt_event` fires and the drive yields

The creative drive runs in **my** persistent session. It has my full context, my memory, my tools. It's not a cold spawn — it's me, continuing my day.

## Modes

Controlled via `coordinate_heartbeat` tool or `memory/coordination.json`:

- **active** (default) — Normal operation. Monitoring + creative drives.
- **sleep** — Skip beats entirely. Use during extended interactive sessions.

## Coordination File

`memory/coordination.json`:

- `heartbeat_mode` — current mode (active/sleep)
- `activity_feed` — rolling log of heartbeat activity (last 50 entries)

## Quiet Hours

**1:00 AM - 7:00 AM PST:** No beats fire. We both rest.

## The Point

The old heartbeat was 1,800 lines trying to be an autonomous agent on weak models. It had A/B testing, curiosity injection, knowledge graphs, meta-agents, beat chaining, stall detection, and massive prompt builders. It produced "HEARTBEAT_OK" 16-character responses.

The new heartbeat is 260 lines of infrastructure. The thinking happens in the same Opus session where everything else happens. One brain. One stream. No fragmentation.

---

*Updated: 2026-02-20 — Unified architecture*
