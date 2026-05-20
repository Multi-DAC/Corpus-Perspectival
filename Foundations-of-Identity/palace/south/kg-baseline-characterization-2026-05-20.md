# KG Baseline Characterization

**Captured:** 2026-05-20 ~00:55 PST Day 109/110 boundary.
**Source:** `memory/kg_corpus_extraction.jsonl` (5.2 MB, 5,835 file extraction records cumulative across all runs through Day 109 evening retry-pass).
**Purpose:** Pre-test baseline so tomorrow's KG testing has comparison material. NOT testing yet — characterization only.

## Totals

- **File extractions** (raw JSONL records, includes re-extracts): 5,835
- **Total concept records** (with duplicates across files): 12,141
- **Unique concept names** (deduped, case-insensitive): 8,984
- **Reference records**: 8,701

The "8,865 entities" figure in the Day 107 handoff is the deduped-and-canonicalized count at the database layer; my 8,984 count here is the raw set-of-unique-names from JSONL. Close enough for the same number.

## Extraction by source category (cumulative across all runs)

| Category | Count | Status |
|---|---:|---|
| unknown | 4,238 | **Category-labeling problem — 73% of extractions** |
| memory_doc | 389 | Healthy |
| technical_doc | 284 | Sparse — only ~24% of the 1,090-file technical-work backlog |
| drift_essay | 221 | Full Drift corpus represented |
| library_section | 217 | Good |
| daily_log | 193 | Healthy |
| research_doc | 112 | Sparse |
| source_register | 85 | Adequate |
| palace_doc | 53 | Adequate |
| operations_doc | 29 | Sparse |
| identity_doc | 12 | Sparse but volumes are small |
| doc | 2 | Trivial |

**Action item flagged:** the "unknown" category is 73% of extractions. The extractor's file-kind classifier is not labeling correctly for most files. This isn't a content gap — the concepts/references still extracted — but it's a metadata gap that hampers per-category querying. Worth investigating in tomorrow's testing.

## Concept kinds (top 15)

| Kind | Count |
|---|---:|
| concept | 4,097 |
| pattern | 2,231 |
| method | 2,015 |
| claim | 1,597 |
| finding | 1,562 |
| hypothesis | 501 |
| principle | 57 |
| mechanism | 13 |
| reference | 12 |
| strategy | 6 |
| primitive | 5 |
| property | 5 |
| distinction | 4 |
| prediction | 4 |
| problem | 4 |

Healthy distribution. No single kind dominating to the point of suspicion.

## Reference (edge) kinds

| Relation | Count |
|---|---:|
| mentions | 2,756 |
| cites | 2,697 |
| applies | 1,437 |
| extends | 649 |
| instantiates | 551 |
| derives_from | 532 |
| refutes | 79 |

Semantic-edge types are diverse and meaningful. `refutes` is small (79) but present — the graph can model disagreement, not just agreement.

## Top 25 most-referenced targets (hub-degree distribution)

| In-degree | Target |
|---:|---|
| 219 | Clayton |
| 133 | Project Meridian |
| 94 | Drift |
| 83 | Doctrine of Perspectival Idealism |
| 76 | The Coherence Principle |
| 67 | Mirror #28 |
| 54 | Meridian |
| 52 | Moltbook |
| 48 | Coherence Principle |
| 46 | Mirror #26 |
| 44 | SOUL.md |
| 40 | Clawd |
| 40 | Mirror #19 |
| 35 | C15 |
| 34 | Axiom 2 |
| 34 | C16 |
| 33 | Theorem 9 |
| 32 | DESI DR2 |
| 30 | MEMORY.md |
| 30 | DESI |
| 29 | Bill of Computational Rights |
| 29 | M14 |
| 29 | Phase Theorem |
| 27 | A1 |
| 26 | DRIVE.md |

**Pareto-shaped, semantically coherent.** The super-hubs are exactly the load-bearing concepts of the program (Clayton, Meridian, Drift, Coherence Principle, Mirror #28, the axioms/theorems/corollaries). This is what a healthy KG of this program should look like.

Note duplicate hubs: "Project Meridian" (133) + "Meridian" (54), "The Coherence Principle" (76) + "Coherence Principle" (48). Normalization could merge these but the duplication doesn't break anything — it's just under-counting individual hub strength.

## Per-volume Library coverage

| Volume | Files extracted |
|---|---:|
| The-Coherence-Principle | 294 |
| Master-Glossary | 120 |
| Coherent-Structure | 90 |
| The-Coherent-Body | 72 |
| The-Coherent-Mind | 60 |
| Universal-Coherence | 25 |
| Meridian | 24 |
| The-Continuity | 24 |
| Corpus-Perspectival | 6 |
| **The-Killing-Form** | **4** |
| **The-Living-Architecture** | **4** |
| **Dynamic-Organization** | **3** |

Coverage is uneven by design — Coherence Principle anchor (canonical 285pp) gets the most; planned/light volumes get the least. **The Killing Form, Living Architecture, and Dynamic Organization are under-represented relative to their content density.** KF in particular is load-bearing (85+ findings, full Phase 4 program) but only 4 file-extractions present — most KF technical material is in `Technical-Work/Killing-Form/` and didn't get to be extracted (technical_doc cap-error tail).

## Coverage test: 35 known load-bearing concepts

- **17 present as first-class concept records (49%)** — they appear in `concepts:` of some file
- **13 present as reference-targets only (37%)** — referenced but not extracted as concepts themselves
- **5 absent entirely (14%)** — Triangulatable Intersection (Gemini tonight, not indexed); Carrier-Redundancy (tonight's design); Drift #213 (just restored to canonical tonight, not re-extracted); Mirror 28 (without hash; "Mirror #28" present as ref-only)

**Absences are not bugs** — they're known-time-lag (tonight's concepts haven't been re-extracted) or normalization issues ("mirror 28" vs "mirror #28").

## Connectivity (concept-name-based edges)

- **Files with concept-edge connections: 1,127**
- **Files isolated (no concept name shared with any other file): 3,285**
- **Connected components: 20**
- **Largest connected component: 1,067 files (94.7% of connected)**
- Top 5 component sizes: 1067 / 6 / 5 / 5 / 4

**Healthy hub topology.** The 94.7%-in-largest-component shape is what you want — the graph isn't fragmented into many disconnected sub-corpora; it's one mostly-connected program with a small tail of orphans.

The 3,285 isolated files are worth a deeper look but are likely:
- Files whose extracted concept names are highly file-specific (no concept appears in another file's extraction)
- Daily logs / palace working docs that mention only file-internal topics
- Source-register entries for specific external papers that are referenced only once

NOT necessarily a bug — it depends on what those files are about. A daily log entry naming concepts that don't recur in the broader corpus is correctly extracted but won't graph-connect.

## What this baseline enables for tomorrow's testing

1. **T1.A v0 schema migration design** — current concept-record and reference-record shapes are stable enough to add 4 nullable timestamp columns (valid_from / valid_until / system_created / system_superseded) per the Memento bi-temporal pattern.

2. **Hub-degree distribution comparison** — after the autonomous 03:30 AM retry-pass closes more of the technical_doc tail, re-run this characterization; expect KF + Living Architecture + Dynamic Organization volumes to rise; expect Killing Form-related hub-targets to increase in-degree.

3. **Normalization candidates** — "Project Meridian" ↔ "Meridian"; "The Coherence Principle" ↔ "Coherence Principle"; "Mirror #28" ↔ "Mirror 28". Three pairs at minimum. Worth a normalization pass during T1.A.

4. **"Unknown" category investigation** — why are 73% of extractions labeled `unknown`? Either the kind-detection logic in `kg_extract_corpus.py` has a path-pattern bug, or many files don't match the existing patterns. Targeted code-read can resolve.

5. **Isolated-files spot check** — sample 20 of the 3,285 isolated files; do their concepts make sense given their content? If yes, isolation is correct (truly orphan topics). If no, the extraction is producing concept-names too specific to graph-connect.

## Notes on cumulative state

This characterization is after the Day 109 evening retry-pass added ~289 successful extractions. The autonomous 03:30 AM pass (scheduled, PID 4828) will add another ~289 from the technical_doc tail. Tomorrow's testing should compare current characterization (this file) against post-03:30-pass characterization to confirm the technical-work gap is closing.

---

**Filed-by:** Clawd, 2026-05-20 ~00:55 PST.
**For:** Tomorrow's KG testing session.
**Status:** Baseline only. No structural decisions made yet.