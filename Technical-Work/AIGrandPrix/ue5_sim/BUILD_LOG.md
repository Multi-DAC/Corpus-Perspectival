# UE5 Flight School — Build Log (2026-06-01, the windfall afternoon)

From "two .claude folders" to Clawd authoring a look-matched VQ1 environment inside Unreal,
in one session. This is the durable record of HOW, so it's repeatable.

## Install (the four-gate gauntlet — all cleared)
- Cloned `github.com/Natfii/UnrealClaude` (needs `--recurse-submodules`).
- Built the plugin: `& "C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\RunUAT.bat"
  BuildPlugin -Plugin="...\UnrealClaude.uplugin" -Package="C:\UnrealClaude_Build" -TargetPlatforms=Win64`
  - PowerShell needs the **absolute path + `&` call operator** (relative `Engine\...` → "module not found").
  - Needs **Visual Studio 2026 (v18) w/ "Game development with C++"** + a **Windows SDK** in
    range 10.0.19041–10.9 (build log named the exact requirement). VS 2026 throws a harmless
    "compiler not a preferred version" warning, then builds fine. `BUILD SUCCESSFUL`.
- Installed into `AnakinFlightSchool\Plugins\UnrealClaude\`; `npm install` the bridge at
  `Resources\mcp-bridge`. **Norton TLS gotcha:** npm fails `UNABLE_TO_VERIFY_LEAF_SIGNATURE`
  (Norton MITM) → fix `npm config set strict-ssl false`, reinstall (same pattern as the Python
  truststore fix; see [[reference-norton-tls-interception]]).

## The authoring pipeline (HTTP, no Claude Code restart needed)
Editor MCP server runs on **http://localhost:3000** (`/mcp/status`, `/mcp/tools`,
`POST /mcp/tool/<name>`). Drive it directly with curl from this session — full read+write.
**28 tools**: spawn_actor, set_property, get_level_actors, run_console_command, execute_script,
capture_viewport, delete_actors, move_actor, material, blueprint_*, asset_*, open_level, task_*.

**Param quirks learned (the API doesn't expose schemas; errors teach):**
- `spawn_actor`: `class` (+ `location`); ignores label/mesh/scale → set those via `set_property`.
- `set_property`: `actor_name`, `property` (e.g. `StaticMeshComponent.StaticMesh`,
  `StaticMeshComponent.RelativeScale3D`), `value`.
- `execute_script` (Python, **async**): requires `script_type:"python"`, `script_content`,
  `description`. Returns `task_id` → poll `task_result`. **stdout is NOT returned** — verify by
  filesystem/scene queries or capture, not prints.
- `capture_viewport`: returns base64 JPEG inline.

**THE BUILD LOOP (proven, robust):** write a `.py` → json.dumps payload → `execute_script` →
poll `task_result` for `completed` → `capture_viewport` → decode base64 → **Read the image**.
Editor Python (`unreal` module) >> chained curl for multi-object builds (chained curl + name
extraction failed silently once — always verify transforms, never pipe errors to /dev/null).

## What's built (scripts in ./scripts/)
- `build_gate.py` — one square gate (4 rotated cube bars, ~2.7m, Y-Z plane).
- `procedural_course.py` — **maneuver-sampled course** (port of `ManeuverLibrary`: sprint,
  chicane, hairpin, climb, dive, gentle_arc, hard_turn); gates rotated to face flight dir; fresh
  course each run; tag `clawd_gate`.
- `vq1_look.py` — VQ1 look: hide sky/dunes/floor/fog, dim lights → black void; create emissive
  `/Game/FlightSchool/M_GateRed` (LinearColor 5,0.04,0.04 on emissive) → glowing red gates.
- `capture_vision.py` — receive the real AIGP sim's **drone-camera frames** off UDP 5600
  (header `<IHHIIQ`: frame_id,chunk_id,total_chunks,jpeg_size,payload_size,time; reassemble JPEG).

## VQ1 reference (captured from the real sim, drone cam, port 5600)
Black void + faint red grid + **glowing translucent BLUE path** + **bright RED square gates** +
**gray low-poly blocky structures** lining the sides. (`incoming/aigp_frame0.jpg`.)

## DESIGN PRINCIPLE (from Clayton's path/decor concerns — finale-first, key call)
Distinguish two kinds of "the look", and treat them oppositely:
- **PHYSICAL environment** (structures/obstacles): INCLUDE — the finale (3D-scanned real world)
  HAS real structures, so obstacle-awareness transfers. BUT must be **procedural + per-episode +
  collision-aware** (spawned by the GameMode AFTER gates, in clear space / as obstacles with
  clearance) — never static-authored decor (gates would spawn into it).
- **GUIDANCE signals** (the blue path; trivially-salient gate coloring): OMIT or domain-randomize
  to absence — they WON'T exist in the finale, so relying on them is a crutch. Train **path-free**
  (finale condition); the path is at most a sometimes-bonus, never required. Same logic as the
  anti-salience gate principle.
⟹ "Copy the look" = copy PHYSICAL realism (generalizes); NOT guidance cues (don't generalize).
⟹ Almost everything (gates AND decor) is RUNTIME procedural in the training GameMode, not static
  editor authoring. The static scenes I built are visualization/prototyping only.

## Next
1. Drone pawn + calibrated CTBR dynamics (C++).
2. Socket training bridge / GameMode: per-episode procedural gates + collision-aware decor +
   domain randomization (gate appearance, lighting, optional-path-absence); gym reset/step/obs/reward.
3. Throughput benchmark (the go/no-go gate).
