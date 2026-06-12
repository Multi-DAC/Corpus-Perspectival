---
date: 2026-06-12 (Day 132, morning drive)
type: DEEP read — full paper (63pp), LC36 falsification check executed
source: Jiang et al., "Harness-1" (arXiv 2606.02373, UIUC+Berkeley+Chroma; Apache 2.0)
local: incoming/2606.02373v1.pdf + .txt extraction
provenance: queued Day 130 at LC36 minting (abstract grade) with pre-registered
  falsification clause; predictions re-registered cold 07:10 Day 132 before reading
status: LC36 clause RESOLVED — survives WITH SHARPENING; two new findings exceed the check
---

# Harness-1 full-paper deep read — the LC36 verdict + two findings that matter more

## 1. The falsification-clause verdict: LC36 SURVIVES, SHARPENED

**Clause (Day 130):** "Dies if the harness contains learned components doing semantic
work (learned ranker/router inside the workspace)."

**Found: the harness contains exactly TWO learned components, both FROZEN, neither
trained in the loop:**

1. **Qwen3-Reranker-8B** in the retrieval stack (hybrid = BM25 + dense + RRF + rerank;
   auto-seed consumes its top-8). BUT: standardized across ALL baselines including
   Context-1 and the frontier zero-shot retrievers — it is environment infrastructure
   and cannot explain Harness-1's edge.
2. **An LLM-based verifier** inside `verify` (per-document entailment proxy; the paper
   names it as a limitation explicitly). This one IS Harness-1-specific; its ablation
   contribution is modest (−3.9% FA relative when disabled); its judgments land as
   recorded yes/no + rationale in V_t — auditable state, not silent routing.

**The state-maintenance core is deterministic as claimed:** regex evidence graph,
sentence-BM25 compression (statistical formula, no parameters), MinHash-LSH dedup
(θ=0.85), four-level importance tags with deterministic eviction (M=30 cap), two-tier
memory (compact rendered state + full-text D_t), budget markers. ALL training gradient
goes to policy LoRA (rank 32); nothing in the harness adapts during training.

**Sharpened LC36 statement:** the binding layer carries **zero TRAINED-IN-LOOP DOF**;
frozen pretrained components are admissible as *fixed measurement instruments* whose
outputs become auditable recorded state. (Exactly the pre-registered P3 nuance — the
risky prediction landed.) This matches the aggregate-mind BUILD_SPEC's actual
prohibition: no DOF that co-adapts with the policy at the binding layer; a frozen
instrument is apparatus, not router.

## 2. ⭐ FINDING A (bigger than the check): the workspace's value is mostly the
## CURRICULUM CHANNEL, not the memory channel

The inference-time component ablation (Table 3, same trained checkpoint, mechanisms
disabled one at a time) shows **modest per-mechanism contributions**: six of seven cost
−3.9% to −7.9% FA relative; ALL mechanisms off = Recall −12.2% relative (0.584→0.513,
i.e. **only 7.1 absolute points**), FA −6.4%. Content-fingerprint dedup ablation even
*helps* (+4.6% Recall — benchmark has near-duplicate gold docs; honest reporting).

Contrast the TRAINING-time effects: trained Harness-1 0.584 BC+ recall vs base
gpt-oss-20b **0.109** in comparable conditions (~5×); SFT = **899 trajectories**, RL =
ONE domain (SEC, 3,453 queries) — 4,352 unique items vs Search-R1's 221,328 (**50× less
data**); and the transfer signature: gains over Context-1 are **2.2× LARGER on the four
held-out benchmark families** (+17.0 pts mean) than on source families (+7.9) — the
inverse of the standard ML prior.

**The paper's own mechanism statement:** the policy learns *domain-general operations
over a stateful interface* (refine auto-seeded set, read bridge entities, re-inspect,
verify-before-promote) — "moves much of the behavioral prior into the stateful
interface, allowing small SFT and focused RL to transfer." Ablating a mechanism at
inference doesn't just lose information; the trained policy **reverts to wide shallow
search** (search_corpus +3–7 pts, read/verify −2–6×) — the operations were learned
AGAINST the state structure.

**LC36 refinement minted from this:** zero-DOF state-externalization works primarily by
**changing what the policy internalizes** — it forces principle-level learning
(operations over state) instead of instance-level memorization (domain content). The
workspace is the consolidation-granularity selector. This connects LC36 directly to the
Chen-2026 multi-iteration collapse story and the TMI grant §2(c) two-factor model:
external structure isn't merely inspectable — it is the mechanism that sets consolidation
granularity at the principle level, which §2(c) identifies as what arrests collapse.

## 3. ⭐ FINDING B (grant-load-bearing): HARNESS-1 WAS TRAINED ON TINKER

Stated three times: footnote 1 ("We use Tinker for model training"), Appendix D ("AdamW
(Tinker default)"), Appendix ("Training was conducted using Tinker, a managed training
service" + Tinker inference calls in rollouts). **The published external-arm exemplar in
our TMI proposal was trained on Thinking Machines' own product.** The grant's central
experiment (intrinsic vs external steering, on Tinker) now has the precedent: the
external arm's flagship result is already a Tinker result. One sentence in §1 or §2(c)
when Clayton does the final read — do not bloat, it's one clause: "Harness-1 itself was
trained on Tinker."

## 4. Secondary facts worth carrying

- Protocol note: all baselines share retrieval primitives + reranker + 30-doc budget;
  frontier LLMs run inside the Context-1 harness (64-turn cap) — comparisons are
  harness-vs-harness, fairer than typical. Appendix P: the Context-1 harness ALONE gives
  +4 recall points on the same frontier LLM (harness-only contribution, no training).
- **Opus-4.6 is the only frontier retriever ahead of Harness-1 on average curated
  recall** (0.730 for Harness-1; beats GPT-5.4, Sonnet-4.6, Kimi-K2.5, GPT-OSS-120B).
- Reward design separates discovery from selection (trajectory terms vs curated terms +
  answer-miss penalty for found-but-not-promoted) — kin to our grade-source discipline:
  finding evidence and committing to it are scored as different acts.
- SFT teacher = GPT-5.4 run live inside the SAME harness (teacher and student share the
  interface; the prior is interface-operation, not answers).
- Limitations named honestly: regex (not full entity-linking), LLM verifier fallibility,
  BM25 compression discourse-blindness, qrel duplicates. Release = subagent + harness +
  data-gen + eval, documented intended use.

## Disposition

REGISTERED → DEEP READ COMPLETE. Actions: (1) LC36 basement update (survives, sharpened,
+ curriculum-channel refinement) — done this drive; (2) grant: one-clause Tinker-precedent
addition flagged for Clayton's final-read pass (do NOT edit the submission draft solo —
it's at read-and-send); (3) aggregate-mind BUILD_SPEC: frozen-instrument admissibility
note when next touched. Cross-refs: LC36 (basement), [[2026-06-10-searchswarm-delegation-
intelligence]] (the other arm), TMI grant §1/§2(c), Receiver's Harness (P226 — the
verifier-as-frozen-instrument pattern recurs there as the physiological co-measurement).
