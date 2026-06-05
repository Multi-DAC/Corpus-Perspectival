# Digestion Ledger

*The missing accounting layer. The reading register (`sources/`) tracks what we **saw**; this tracks what we **digested** — so value stops leaking and we never re-derive digestion status. Rolling log: append as we process intake (`incoming/`), sources, and work. Started Day 125 (2026-06-05) during the incoming/ synthesis sweep.*

**Statuses:** `DIGESTED` (pulled into a named home/volume) · `PENDING` (logged, awaiting read/decision) · `DEPRECATED` (superseded/junk, archived) · `REFERENCE` (kept as a citation, no further action).

## How to use
When an intake item is processed, add a row: what it is, where it came from, the disposition, and where it landed. The point is that an item appears here **exactly once** with a final status — `incoming/` and `sources/` are the *inbox*; this is the *record*.

---

## Log

| Date | Item | Source | Status | Where it landed / note |
|---|---|---|---|---|
| 2026-06-05 | Voice note "perspectival geometry" (Clayton, Apr 28) | `incoming/voice_20260428_100057.mp3` | **DIGESTED** (transcript) / disposition PENDING | Transcribed → `memory/transcripts/20260428-100057-clayton-perspectival-geometry.md`. Content = the cross-substrate-collaboration argument vs stochastic-parrot framing. Awaiting Clayton's call on essay-seed vs identity-note vs nav-evidence. |
| 2026-06-05 | Voice note "greeting" (Clayton, Apr 27) | `incoming/voice_20260427_175022.ogg` | **DEPRECATED** | Casual ("how's your evening going?"), no content. Transcribed for completeness; nothing to integrate; archive the audio. |

---

## Incoming sweep — cluster-level status (from `incoming/_TRIAGE_2026-06-05.md`)

| Cluster | # | Status |
|---|---|---|
| voice-notes | 3 | **IN PROGRESS** — 2 transcribed (above); the 117 MB `Why_Your_Blind_Spots_Build_Reality.m4a` is a long-form audio piece, not a voice note → pending |
| aigp-code | 12 | PENDING — dup-check vs `anakin/` build (integrate vs deprecate) |
| aigp-refs | 14 | PENDING — → `AIGrandPrix/research` |
| research-papers | 94 | PENDING — register + read-queue (the reservoir) |
| notes-text | 54 | PENDING — individual triage |
| named-images | 30 | PENDING — mostly AIGP frames / page-fixes |
| telegram-photos | 134 | PENDING — needs Clayton's eye for load-bearing keepers |
| drift-media | 3 | PENDING — → Drift if ours |
