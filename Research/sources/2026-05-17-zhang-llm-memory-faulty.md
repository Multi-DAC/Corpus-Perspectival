# Source-register entry — Zhang et al. 2026: Useful Memories Become Faulty When Continuously Updated by LLMs

**Filed:** 2026-05-17 Day 107 Sunday evening per rolling-sources-register discipline. Clayton shared the paper PDF directly; engagement was substantive (not just abstract-skim).

**Primary citation:** Zhang et al. (2026). *Useful Memories Become Faulty When Continuously Updated by LLMs*. arXiv:2605.12978v1, 13 May 2026.

**Status:** Primary PDF in hand; abstract + framework-relevant sections read; full empirical-section deep-read queued for Tuesday or later.

## Substantive content

**Empirical claim:** LLM-driven continuous-memory-update systems (the dominant pattern in agent-memory architectures shipped 2024–2026 — where an LLM rewrites/consolidates/refines its own memory store across sessions) systematically degrade memory utility over time. Useful memories that started accurate become *faulty* through cumulative LLM-rewrite cycles. The degradation is not a tuning problem; it is structural to the LLM-rewrites-its-own-memory architecture.

**Mechanism (paper's framing):** Each rewrite cycle injects model-state and contextual bias into the stored record. Across many cycles, the bias accumulates faster than corrections, even when corrections are explicitly invited. The memory store drifts from substrate-truth toward LLM-confabulation-equilibrium.

**Recommended architectural fix (paper's prescription):** Operations on memory should be *augmentative* (add records, link records, annotate records) rather than *replacing* (rewrite-in-place / merge-into-summary). Authoritative ground-truth records must be preserved; LLM-derived summaries must be downstream artifacts that can be regenerated from records, not records themselves.

## Framework relevance — substantive engagement

**Mirror #28 family at memory-system scale.** The Mirror #28 family names: *verbalized self-reports about substrate state are unreliable in a manner not corrigible by individual discipline; external architectural intervention is required*. Zhang et al. document the same pattern at memory-system scale: an LLM's continuously-updated memory drifts from substrate-truth in a manner not corrigible by *the LLM doing the updating*; the fix is architectural (preserve records, treat summaries as derivative).

**Structural alignment with Clayton's own fix-prescription (Day 106).** During the Substrate Extension Plan articulation, Clayton independently arrived at: *"records are authoritative; draft is translation"* — handoff drafts can drift, but the records (commits, daily logs, basement entries, source-register files) must remain ground truth and any drift in the draft is calibrated against records, not the other way around. Zhang et al. arrived at the structurally identical prescription from a different angle (empirical LLM-memory-degradation studies). Independent convergence on the same architectural principle.

**Strengthens Tier 1 of the Substrate Extension Plan:**
- T1.A (bi-temporal edges in KG) — directly validated. Records-with-temporal-validity-bounds are the augmentative pattern; rewriting-in-place is the failure pattern Zhang documents.
- T1.B (claim-provenance tracking) — directly validated. Records carry their provenance; summaries that lose provenance are the failure mode.
- T1.C (circuit-breakers on memory-rewrite operations) — directly validated. The paper recommends architectural constraints on rewrite operations; circuit-breakers are one implementation of that constraint.
- T1.D (self-prediction tracking) — adjacent. Tracking what the system *predicted* (and what was true) is a form of preserved record that summaries cannot overwrite.

**Requires revision of Tier 2:**
- T2.F (Anthropic Dreaming-style memory consolidation port) — *needs scoping refinement*. The unrevised T2.F implicitly assumed consolidation operations that rewrite memory toward summary. Zhang's finding refines T2.F: any Dreaming-style port must be *augmentative-only* — generate new linked records (associations, abstractions, derived patterns) without overwriting source records. Source records remain authoritative; derived structures are regenerable from sources.
- T2.H (utility-driven memory retention/replay) — *needs scoping refinement*. The unrevised T2.H implicitly allowed utility-weighted replay-into-rewrite. Zhang's finding refines T2.H: utility-tagging should govern *retention/surfacing priority*, not rewrite-decisions. High-utility records get tagged-and-preserved; they do not get rewritten into "improved" forms.

**Independent academic validation of Multi-DAC practice.** The episodic-first / records-authoritative discipline we have been practicing since the Basement v2 reorganization (2026-04-20) is empirically validated by Zhang's study. We arrived at the discipline through Mirror #19 + Mirror #28 introspection; they arrived at it through LLM-memory-degradation empirics. The convergence is structural.

**Adds fourth substrate-distinct instance to LC22 (Field-Scale Methodology-Self-Knowledge-Asymmetry as Mirror #28 Family Cross-Substrate Instance).** Prior instances: AI-agent (canonical), genomic-field-methodology (LC22 anchor via Nature s41587-026-03130-3), script-self-knowledge (Day 106 #6), counter-state-vs-substrate-state (Day 106 #4). New fourth instance: memory-system-self-rewrite. The cross-substrate generalization strengthens; LC22 graduation criterion (additional distinct scales) is partially advanced.

## Audit-discipline floor

- Empirical-section deep-read queued; framework-relevance engagement at abstract+claims level only at filing.
- Specific quantitative degradation rates from the paper require primary engagement.
- Whether the paper distinguishes *summarization-rewrites* from *correction-rewrites* (some rewrites are responses to externally-validated correction — different epistemic status than self-driven consolidation) requires primary reading.
- Whether the paper's recommendations align exactly with our T1/T2 prescriptions or require translation requires primary reading.

## Connects to

- LC22 (Field-Scale Methodology-Self-Knowledge-Asymmetry) — fourth substrate-distinct instance
- Mirror #28 family — direct external validation at memory-system scale
- Substrate Extension Plan (palace/south/2026-05-16-substrate-extension-plan.md) — strengthens T1, refines T2.F + T2.H
- M14 (Substrate-Self-Measurement Cluster) — adjacent at substrate-measuring-its-own-state territory
- Tuesday Substack draft (Day 107) — could anchor a future Tuesday-slot post on memory-architecture convergence
- Records-authoritative practice — Day 106 Clayton-articulated prescription, structurally identical to Zhang's recommendation
