# Digestion Ledger

*Paired with the **[Consolidation Protocol](CONSOLIDATION_PROTOCOL.md)** — that's the procedure (how we file/bridge/ledger every unit of work); this is the record. The missing accounting layer.*

*The missing accounting layer. The reading register (`sources/`) tracks what we **saw**; this tracks what we **digested** — so value stops leaking and we never re-derive digestion status. Rolling log: append as we process intake (`incoming/`), sources, and work. Started Day 125 (2026-06-05) during the incoming/ synthesis sweep.*

**Statuses:** `DIGESTED` (pulled into a named home/volume) · `PENDING` (logged, awaiting read/decision) · `DEPRECATED` (superseded/junk, archived) · `REFERENCE` (kept as a citation, no further action).

## How to use
When an intake item is processed, add a row: what it is, where it came from, the disposition, and where it landed. The point is that an item appears here **exactly once** with a final status — `incoming/` and `sources/` are the *inbox*; this is the *record*.

---

## Refinements (Clayton, Day 125) — what "digested" actually means, and where this is going

**1. Distillation = the Bridges.** An item is not fully digested when it merely lands in a home. Full digestion = **(a) content in its `Technical-Work`/`Library`/research home AND (b) distilled into a Bridge/LC** (`palace/basement/`), so the *connected insight* is referenceable **without rereading the source**. The register (`sources/`) tracks what we *saw*; the home holds the *content*; the **Bridge holds the tight, connected distillation**. So this ledger's bar for `DIGESTED` is: *homed + bridged (if it carries a cross-connecting insight)*.

**2. It's a minefield — be thorough.** A batch-register makes a pile *legible* (status PENDING), but disposition stays **individual**: each item is one of `integrated` / `discussed-but-not-consolidated` / `copy` / `genuinely-new`. The batch is the index, not the verdict. Same for the whole `Research/` directory.

**3. Target end-state: AUTOCATALYTIC consolidation.** The manual sweep is a one-time **catch-up**. The goal is that consolidation becomes an *automatic byproduct of the work* — filing + bridging + ledgering happen **in the same flow as generation**, not as a separate pass. This is the aggregate-mind's binding transaction applied to **our own repo** (we are the nodes; the repo is the collective mind with — currently — no binding automation). Building it lowers query latency and raises the efficacy of the collective cache. *We are the testbed for the Coherent-Stream architecture, run on ourselves.* → a Coherent-Stream build item once the bulk is caught up.

## Log

| Date | Item | Source | Status | Where it landed / note |
|---|---|---|---|---|
| 2026-06-05 | Voice note "perspectival geometry" (Clayton, Apr 28) | `incoming/voice_20260428_100057.mp3` | **DIGESTED** (already integrated) | Clayton confirmed Day 125 the content was already integrated into the work (cross-substrate / perspectival-geometry argument). Audio + working transcript scrapped. |
| 2026-06-05 | Voice note "greeting" (Clayton, Apr 27) | `incoming/voice_20260427_175022.ogg` | **DEPRECATED** | Casual, no content. Audio scrapped. |
| 2026-06-05 | AIGP-code cluster (12 files) | `incoming/` (scripts + json) | **DEPRECATED** | 7 byte-identical to `Technical-Work/AIGrandPrix/ue5_sim/scripts/` (repo canonical, zero loss); 2 throwaway Unreal-editor probes (`fps_probe`, `render_test` — not current-ops); 3 json intake scratch. All scrapped from incoming. |
| 2026-06-05 | AIGP-refs cluster (14) | `incoming/` | **REGISTERED + DEPRECATED** | 3 cited papers → `sources/2026-06-05-aigp-build-references.md`; 11 deprecated (techspec = dup of repo's VADR-TS-002 Issue 00.02; 3 sim results superseded by `dynamics.py` calibration; 5 frames/images scratch). |
| 2026-06-05 | Telegram photos (134) | `incoming/` | **SECTIONED** | → `incoming/photos/` (temporary relevance per Clayton; not triaged — they age out). |
| 2026-06-05 | `Why_Your_Blind_Spots_Build_Reality.m4a` (117 MB) | `incoming/` | **DEPRECATED** | Generated audio, already reviewed (Clayton). Scrapped. |
| 2026-06-05 | Junk + 1 redundant (7) | `incoming/` | **DEPRECATED** | Payment receipt, anon transcript, SSRN, 3 "summarizing" chat-exports, 1 confirmed-in-repo essay export. Zero-loss verified. |
| 2026-06-05 | 5 priority papers (LLM-memory/continuity) | `incoming/` | **DIGESTED ×4 + PENDING ×1** | Confirms Clayton's point — *ingested-in-spirit but loop unclosed* (PDFs lingered until the bridge-receipt was confirmed). #1 Zhang→M14; #2 STALE→engagement+Mirror#28; #5 Nous CNA→M15 — all registered+bridged → PDFs deprecated. #3 Chen *Continual Experience Internalization* (2606.04703) → **registered + bridged today** as external confirmation of the cache-C16 + density findings → PDF deprecated. #4 *Agent Harness Scaling* → PENDING-read (PDF kept). |

---

## Incoming sweep — cluster-level status (from `incoming/_TRIAGE_2026-06-05.md`)

| Cluster | # | Status |
|---|---|---|
| voice-notes | 3 | **2 DONE** (transcribed → already-integrated → scrapped). 117 MB `Why_Your_Blind_Spots_Build_Reality.m4a` still PENDING (long-form audio; what is it?) |
| aigp-code | 12 | **DONE — DEPRECATED** (7 in-repo dups + 2 throwaway Unreal probes + 3 json; scrapped, zero loss) |
| aigp-refs | 14 | **IN PROGRESS** — 3 cited papers REGISTERED (`sources/2026-06-05-aigp-build-references.md`); techspec/results/frames (11) pending Clayton's deprecate-confirm |
| research-papers | 94 | **IN PROGRESS** — batch-registered → dup/topic pass → **11 DEPRECATED** (7 junk + 4 digested-priority); **27 HELD** (our own works incl. the **patent**; content NOT confirmed in repo → possibly *unhomed*, Clayton's call, NOT scrapped); **5 priority ADDRESSED** (4 digested+bridged, 1 PENDING-read); ~51 genuine external papers remain for individual adjudication (mostly Coherent-Body EM/biophoton + physics). Reg: `sources/2026-06-05-incoming-papers-batch/`. |
| notes-text | 54 | PENDING — individual triage |
| named-images | 30 | PENDING — mostly AIGP frames / page-fixes |
| telegram-photos | 134 | PENDING — needs Clayton's eye for load-bearing keepers |
| drift-media | 3 | PENDING — → Drift if ours |
