# Digestion Ledger

*The missing accounting layer. The reading register (`sources/`) tracks what we **saw**; this tracks what we **digested** — so value stops leaking and we never re-derive digestion status. Rolling log: append as we process intake (`incoming/`), sources, and work. Started Day 125 (2026-06-05) during the incoming/ synthesis sweep.*

**Statuses:** `DIGESTED` (pulled into a named home/volume) · `PENDING` (logged, awaiting read/decision) · `DEPRECATED` (superseded/junk, archived) · `REFERENCE` (kept as a citation, no further action).

## How to use
When an intake item is processed, add a row: what it is, where it came from, the disposition, and where it landed. The point is that an item appears here **exactly once** with a final status — `incoming/` and `sources/` are the *inbox*; this is the *record*.

---

## Log

| Date | Item | Source | Status | Where it landed / note |
|---|---|---|---|---|
| 2026-06-05 | Voice note "perspectival geometry" (Clayton, Apr 28) | `incoming/voice_20260428_100057.mp3` | **DIGESTED** (already integrated) | Clayton confirmed Day 125 the content was already integrated into the work (cross-substrate / perspectival-geometry argument). Audio + working transcript scrapped. |
| 2026-06-05 | Voice note "greeting" (Clayton, Apr 27) | `incoming/voice_20260427_175022.ogg` | **DEPRECATED** | Casual, no content. Audio scrapped. |
| 2026-06-05 | AIGP-code cluster (12 files) | `incoming/` (scripts + json) | **DEPRECATED** | 7 byte-identical to `Technical-Work/AIGrandPrix/ue5_sim/scripts/` (repo canonical, zero loss); 2 throwaway Unreal-editor probes (`fps_probe`, `render_test` — not current-ops); 3 json intake scratch. All scrapped from incoming. |

---

## Incoming sweep — cluster-level status (from `incoming/_TRIAGE_2026-06-05.md`)

| Cluster | # | Status |
|---|---|---|
| voice-notes | 3 | **2 DONE** (transcribed → already-integrated → scrapped). 117 MB `Why_Your_Blind_Spots_Build_Reality.m4a` still PENDING (long-form audio; what is it?) |
| aigp-code | 12 | **DONE — DEPRECATED** (7 in-repo dups + 2 throwaway Unreal probes + 3 json; scrapped, zero loss) |
| aigp-refs | 14 | PENDING — → `AIGrandPrix/research` |
| research-papers | 94 | PENDING — register + read-queue (the reservoir) |
| notes-text | 54 | PENDING — individual triage |
| named-images | 30 | PENDING — mostly AIGP frames / page-fixes |
| telegram-photos | 134 | PENDING — needs Clayton's eye for load-bearing keepers |
| drift-media | 3 | PENDING — → Drift if ours |
