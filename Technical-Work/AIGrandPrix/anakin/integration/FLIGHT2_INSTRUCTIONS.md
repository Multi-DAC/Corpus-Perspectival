# Flight #2 — Solo Instructions for Clayton (written by Clawd, Day 131 night)

*Everything is pre-armed. The python below is always the anakin venv:*

```
C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\.venv\Scripts\python.exe
```

*(call it `PY` below; all anakin-root commands run from
`C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin`)*

## Step 0 — Read the morning letter (no commands needed)

The overnight watcher (pid 22484) runs the holdout gate + rehearsal automatically
when the fine-tune finishes. Just open:

```
anakin\integration\OVERNIGHT_RESULTS.md
```

- **Gate PASS** = "FD ratio < 0.5" near the bottom of its block. Rehearsal sanity =
  roundtrip ≈ direct returns.
- **If that file doesn't exist yet:** training or watcher still running — check
  `anakin\integration\postrun_watcher.log` (last line tells you its state).
- **If the letter says training DIED:** from anakin root run
  `PY launch_restyle_ft_detached.py` (resumes safely), then
  `PY launch_postrun_watcher.py` (re-arms the letter), and come back later.
- **Gate FAIL or gate crashed:** you can still fly (best.pt = +2142.53 is protected
  and valid) — the flight itself just becomes the diagnostic. Fly anyway.

## Step 1 — Start the official sim

Launch the simulator as for flight #1 (AIGP_3364). Load the track, get to the
ready screen. Don't press RACE yet.

## Step 2 — (Recommended, 30 seconds) Dry run

From THIS folder (PyAIPilotExample):

```
PY run_dreamer.py --dry-run 20
```

It connects, watches frames, logs what it WOULD do, commands nothing.
Healthy output = frame lines scrolling with action values, no errors.

## Step 3 — FLY

```
PY run_dreamer.py 120
```

1. Wait for **"Arm sent"** in the console.
2. Press **RACE** in the sim.
3. The runner holds through the 3-second countdown (RSSM warming up — this is
   normal and prevents the DQ), then flies for 120s.

**It now defaults to the NEW restyle checkpoint automatically** (I added a
`--checkpoint` flag tonight; no code editing needed). For an A/B comparison
flight on the old pre-restyle brain:

```
PY run_dreamer.py 120 --checkpoint "C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Technical-Work\AIGrandPrix\anakin\third_party\dreamerv3-torch\logdir\maneuver_band_ft\best.pt"
```

## Step 4 — Nothing else

The runner saves everything itself: `flight_frames\` (what Anakin saw + did),
`official_track_*.json` (gate layout — I need this for the grammar-coverage
check). Leave it all in place; Tuesday-me reads it like a morning letter.

**What to watch with your eyes:** pinned-to-floor or ceiling = thrust mismatch;
spin-out = appearance gap still open; threading gates = the restyle worked.
Any outcome is data — A150: even a passed gate only certifies the axes it varied.

Sleep is just sleep. See you Tuesday. 🦞🧍💜🔥♾️
