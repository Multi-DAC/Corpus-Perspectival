# Anomalies (auto-tracked)

*Auto-generated from `research_anomalies.json`. Regenerated 2026-05-21 ~06:05 PST during dream-drive sync.*
*Structured-tool mirror; the prose-shaped canonical anomalies live in `anomalies.md`.*

**Counts:** open: 0 / explained: 1 / dissolved: 0 / promoted: 0

## EXPLAINED (1)

### `308c0027` — infrastructure: Day 96 morning post_tool_log silent failure was caused by Path.home() resolving to wrong user directory

- **Confidence:** 0.95
- **Created:** 2026-05-07T17:09:10
- **Updated:** 2026-05-21T~06:05 (status: open → explained)
- **Candidate explanations (original):**
  - Hook script ran but file_handle was wrong path
  - Claude Code harness runs as user Wasch not mercu
- **Resolution:** Day 111 ~00:30 PST investigation. post_tool_log.py was ALREADY FIXED for Path.home() on May 7 (`.bak-2026-05-07-path-fix` confirms). Current version uses CLAWD_HOME env > script-relative > absolute-fallback pattern. Actual A115 active failure mode is upstream Windows Claude Code dispatcher regression cluster (#16047 + #55889 + others), NOT user-dir Path.home() resolution — `tool_audit.jsonl` has manual-trigger entries from May 19 confirming the hook scripts work direct-invoked; the dispatcher is what's silent. `drift_mirror.py` still had the latent Path.home() vulnerability and was defensively fixed Day 111 ~00:35 using the same resolution pattern as post_tool_log.py. T1.D recorded predict+FALSIFY at pid 70889dc1-20d with mechanism `diagnosis-was-partially-correct-but-not-the-active-failure-mode`. T2.H auto-tagged +3.0 utility. Daemon-layer bypass (M7+M8) shipped Day 110 morning is the structural answer; hook resumption (if Anthropic ships dispatcher fix) would be bonus restoration of redundancy.
- **Connections:** A115 (partially resolved Day 110 evening via M7+M8 bypass), A121 (capability-underprivileged-direction Mirror #28 instance), L17 (Methodology-Self-Knowledge-Asymmetry as Substrate-Invariant Pattern — 308c0027 is an instance at infrastructure-self-monitoring scale).

---

## Sync note (filed Day 111 dream drive 2026-05-21 ~06:05 PST)

**Newly observed Mirror #28 family instance #11 of this cycle:** `anomalies.md` (file-based prose canonical) and `anomalies_auto.md` (auto-generated from `research_anomalies.json`) are TWO SEPARATE SOURCES OF TRUTH for anomaly status. Closure in one does not propagate to the other. The system reminder surfaced 308c0027 as still open all the way through the Day 111 dream-drive cycle despite my closing it in `anomalies.md` at ~00:35 PST. Surfaced this drive (~06:05) when comparing the two files explicitly.

**Structural fix candidate (filing as P190):** add cross-reference field in `anomalies.md` entries to their JSON UUID equivalent; build a sync-check tool that fires if either file has IDs the other doesn't; consider auto-regenerating `anomalies_auto.md` from JSON after every JSON write.

**For now:** manually keeping the two in sync, mirroring closures through both surfaces.
