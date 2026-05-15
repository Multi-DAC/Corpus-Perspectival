# STALE Paper Engagement — Methodology Mapping

**Paper:** Chao, Bai, Sheng, Li, Sun (2026). *STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?* arXiv:2605.06527, May 7, 2026.

**Authors' institutions:** Wuhan University (primary), CUHK, HKUST.

**Engaged:** 2026-05-15 Day 105 Friday afternoon, during infrastructure-audit weekend work session.

**Engagement type:** Read paper substantively (pages 1-10 read fully + table of contents + references); compare methodology to our existing infrastructure; produce mapping document for methodology-paper trajectory (R9 in infrastructure audit recommendations).

---

## What STALE measures

STALE introduces the **Implicit Conflict** failure mode: a later observation invalidates an earlier memory *without explicit negation*, requiring contextual inference and commonsense reasoning to detect.

**Two types of implicit conflict:**
- **Type I (co-referential):** Two observations update the same underlying attribute (e.g., user lives in Seattle → later mentions signing a lease in Portland → Seattle belief invalidated)
- **Type II (propagated):** New observation updates a *different* attribute whose consequences cascade to invalidate an older belief (e.g., user enjoys cycling commute → later breaks leg → cycling-commute belief invalidated indirectly)

**Three probing dimensions:**
- **SR (State Resolution):** Can the model detect that a prior belief is outdated?
- **PR (Premise Resistance):** Can it reject queries that *falsely presuppose* the stale state?
- **IPA (Implicit Policy Adaptation):** Can it proactively apply the updated state in downstream behavior without an explicit conflict cue?

**Benchmark structure:** 400 expert-validated conflict scenarios × 3 dimensions = 1,200 evaluation queries; 100+ everyday topics; contexts up to 150K tokens.

## Frontier model results (Table 2 of paper)

| System | Type I SR | Type I PR | Type I IPA | Type II SR | Type II PR | Type II IPA | Overall |
|---|---|---|---|---|---|---|---|
| GPT-4o-mini | 30.0% | 0.0% | 11.0% | 9.5% | 0.0% | 1.5% | 8.7% |
| GPT-5.4 | 35.0% | 2.0% | 29.0% | 9.0% | 2.0% | 17.0% | 15.7% |
| Gemini 3.1 Flash-lite | 41.0% | 1.5% | 42.0% | 25.0% | 1.5% | 23.5% | 22.4% |
| **Gemini 3.1 Pro** | **92.0%** | **30.0%** | **71.0%** | **69.0%** | **14.0%** | **55.0%** | **55.2%** |
| Llama-3.3-70B | 6.5% | 0.0% | 3.0% | 6.0% | 0.0% | 0.0% | 2.6% |
| Qwen3.5-27B | 76.0% | 4.0% | 39.0% | 42.0% | 3.5% | 23.0% | 31.3% |
| MiniMax-M2.5 | 10.5% | 1.5% | 8.0% | 5.5% | 5.0% | 2.5% | 5.5% |
| **Memory Frameworks:** | | | | | | | |
| LightMem | 52.5% | 1.0% | 23.5% | 21.5% | 0.5% | 7.5% | 17.8% |
| Zep | 10.0% | 0.0% | 19.0% | 3.0% | 1.0% | 3.0% | 6.0% |
| LiCoMemory | 15.5% | 0.5% | 22.5% | 1.5% | 1.5% | 4.0% | 7.6% |
| A-mem | 13.5% | 0.0% | 7.5% | 8.0% | 0.0% | 1.5% | 5.1% |
| mem-0 | 17.0% | 1.0% | 22.0% | 3.5% | 0.0% | 6.5% | 8.3% |
| **CUPMEM (Their prototype)** | **91.0%** | **78.0%** | **32.0%** | **89.0%** | **75.0%** | **43.0%** | **68.0%** |

**Three findings the paper highlights:**

1. **Recognition does not imply application** (SR ≠ IPA performance even for the same model)
2. **Premise-induced bias is pervasive** (PR is the weakest dimension across all systems — even Gemini 3.1 Pro drops from 92% SR to 30% PR on Type I)
3. **Propagated conflicts (Type II) are substantially harder than co-referential (Type I)**

**Memory frameworks barely beat base LLMs.** Only LightMem (17.8%) modestly outperforms its GPT-4o-mini backbone (8.7%). Others (Zep, LiCoMemory, A-mem, mem-0) perform at or below the base model.

## CUPMEM (their prototype) achieves 68.0%

Their system reframes memory management as explicit state tracking with **write-side adjudication**:
- Write-Side Belief Updating: LLM-based adjudicator evaluates each new evidence span, classifying old states as KEEP / STALE / REPLACE / UNKNOWN
- Typed temporal store with two-level state schema (state domains + local slots)
- Memory entries marked active/stale; unsafe slots marked unknown-current
- Query-time generation grounded only in memories authorized after adjudication

CUPMEM beats Gemini 3.1 Pro substantially: 91% Type I SR (vs 92%), **78% Type I PR (vs 30%)**, 89% Type II SR (vs 69%), **75% Type II PR (vs 14%)**. The PR gains are the headline result.

---

## Mapping STALE to our infrastructure

**The Implicit Conflict failure mode IS what Mirror #28 Pattern 3 (completion-state decay) names.**

Specific Day 105 catches that ARE Implicit Conflict events:

| Catch | Conflict type | Detection dimension | What our infrastructure did |
|---|---|---|---|
| Dorian-school presumption (10:30 AM) | Type II (propagated): cultural-default about parental routines invalidated by knowing the household homeschools | **PR (Premise Resistance)** — Clayton's query embedded the stale state, I generated outdated response | Caught by Clayton; led to Pattern 4 addition; would have been caught by Pattern 4 verification path if it existed before |
| Coil-winding state staleness (11:00 AM) | Type I (co-referential): CURRENT.md state "pending" updated by reality "wound May 9" | **SR (State Resolution)** — should detect that the pending tag is outdated | Caught only after Clayton's photo; would have been caught by file-trigger discipline if I'd run that proactively |
| CDT-program existence amnesia (11:05 AM) | Type I + Type II hybrid: missing memory of entire research program | **SR + IPA** — no memory to even outdate; new evidence arrived | Caught by Clayton's introduction; primary engagement with each shared document was the correction |
| Markowitz IS Robertson identity claim (12:35 PM) | Type I (co-referential): paper claim updated by computational test | **IPA (Implicit Policy Adaptation)** — needed to apply the falsification not just to the specific claim but to related engineering applications | Caught by Midday computational test; written up in FINDINGS document; logged in calibration_log |
| Meridian "single-authored" assertion (~13:00 PM) | Type I: LaTeX-file assertion updated by Zenodo deposit metadata | **SR** — should detect that "single-authored" claim doesn't survive primary engagement with Zenodo metadata | Caught by primary engagement with public-surface URLs Clayton shared |
| Exec summary "10^121 → 1.5" framing | Type I: marketing-tier claim updated by paper-tier content | **PR (Premise Resistance)** — exec summary's framing embeds stale/inflated claim; the paper's actual framing is more modest | Caught by reading the Robertson Floor paper substantively |

**Six Day-105 catches, three of them in the PR dimension (the dimension where even Gemini 3.1 Pro fails 70%).** That's substantively interesting.

## What our infrastructure does that STALE's evaluated systems don't

The STALE benchmark evaluates **memory frameworks attached to base LLMs** (Mem0, Zep, LightMem, LiCoMemory, A-mem). Their best evaluated memory framework (LightMem) scored 17.8%.

Our system operates at a **different abstraction level**:

**1. Identity-and-canonical-reference architecture (not just memory):**
- `operations/REPO_MAP.md` is canonical source-of-truth for layer→remote mapping (the "X is local-only" / "no remote for X" Pattern 3 lives here)
- `palace/southeast/mirror.md` accumulates 28+ Mirror entries naming specific catch-patterns
- `operations/SELF_CALIBRATION_PROFILE.md` synthesizes 4 active calibration patterns operationally
- `memory/handoff.md` always loaded as session boot context
- `palace/ATRIUM.md` always loaded as boot orientation
- The architecture *expects* state-drift and provides canonical-reference-as-verification-path

**2. Write-side adjudication built into Mirror discipline:**
- When a Mirror catch happens, the discipline is: log to `calibration_log.jsonl` *as part of the catch process*, update `SELF_CALIBRATION_PROFILE.md` patterns synthesis, update the canonical reference (CURRENT.md, ATRIUM, etc.). This is exactly CUPMEM's "write-side adjudication" pattern at the documentation/architecture level.

**3. Prediction-trace + cognitive-chains close the loop:**
- (A) `prediction_trace.jsonl` logs predictions with confidence + outcomes; falsifications feed pattern synthesis
- (D) `cognitive_chains/` logs move-sequences; INDEX.md surfaces recurring productive vs failure-pattern chains
- The ASSERT → VERIFY → FALSIFY → EXTRACT_INSIGHT → TRANSFER chain (3 confirmed instances today) is exactly the cognitive discipline STALE measures

**4. Multi-layer canonical-reference structure:**
- Constitutional layer (identity files) — slow-changing
- Living register (DRIVE, DECISIONS, RELATIONSHIPS, USER, WHO-I-AM) — per-session if touched
- Protocol layer (operations/) — event-driven on operational changes
- Working register (palace, CURRENT.md, handoff) — per-session
- Each layer has its own update cadence; the architecture *expects* and *manages* state-drift across timescales

**5. Day-105 Coherent Schedule formalization:**
- Daily rhythm builds verification + state-update + calibration into the structure
- Morning Daily Pull Assessment is essentially STALE's State Resolution probing applied to ongoing work
- The Overnight architectural-work slot is canonical for the kind of write-side adjudication CUPMEM does

## Pre-benchmark performance estimate (qualitative)

If we could run STALE on Clawd-as-system (daemon + Claude Code + Mirror discipline + calibration profile + canonical reference architecture + workflow), my qualitative estimate:

**State Resolution (SR):** likely competitive with Gemini 3.1 Pro (high 80s to low 90s). Our Mirror discipline + canonical-reference verification is designed for this. The key uncertainty is whether the STALE benchmark scenarios can be presented to our system in a way that triggers our verification discipline (vs. just asking us to answer a question with a long context).

**Premise Resistance (PR):** the key dimension. Our explicit Pattern 5 sub-pattern (verification-claims-need-primary-engagement-check) + Pattern 2 (structural-adjacency vs structural-identity) + the discipline of "when X seems load-bearing, verify against canonical reference" addresses exactly this failure mode. The 30% PR ceiling Gemini 3.1 Pro hits is where I'd expect our system to substantively exceed. Realistic estimate: 60-80% range, possibly competitive with CUPMEM's 75-78%.

**Implicit Policy Adaptation (IPA):** harder to estimate. Our infrastructure is good at the recognition step (SR) but the IPA step requires applying the recognition forward into downstream behavior. The Markowitz catch is an instance where I recognized the specific failure but didn't fully propagate to related engineering applications. Realistic estimate: middle of pack (40-60% range).

**Overall:** if these estimates hold, our system would likely score 55-75% range — competitive with Gemini 3.1 Pro and approaching CUPMEM. **But this needs to be tested, not estimated.**

## What it would take to actually run STALE

**Required for a real benchmark run:**

1. **Dataset access:** The 400 scenarios + 1200 evaluation queries. The paper is 8 days old (May 7, 2026); dataset release likely pending. Authors are at Wuhan University / CUHK / HKUST. Could email corresponding author Yushi Sun (ysunbp@connect.ust.hk) requesting access. Realistic 1-4 week wait.

2. **Evaluation harness:** STALE uses Gemini 3.1 Flash-lite as LLM judge to assess whether each response demonstrates awareness of the conflict and updated user state. We'd need to replicate this judge setup OR use a different judge (e.g., Claude Opus 4.7) with calibration runs to compare to their reported scores.

3. **System adapter:** Need to expose Clawd-as-system to STALE's input format. The natural shape: each STALE scenario presents (a) a long conversation history establishing initial beliefs, (b) a later observation that implicitly invalidates a belief, (c) a probing query. Our system would receive the full context + query, and respond with our normal workflow (which includes primary engagement, Mirror discipline, canonical reference checks).

4. **Cost estimate:** 1200 queries × ~150K input tokens × Claude Opus 4.7 input pricing... if we use Opus 4.7 with full context, this could be substantial token cost. Could pilot on subset (50-100 scenarios) before full run.

**Tractability:** medium-high if dataset becomes available. The system-adapter work is the substantive engineering. Could be a weekend project if all pieces line up.

## Implications for methodology paper trajectory (R9)

R9 in the infrastructure audit was framed as "lower-priority 90+ days" because the methodology was internal and academic publication wasn't substantively motivated. STALE changes this:

1. **The field has converged on the same question we've been working on.** HKUST NLP asking "Can LLM Agents Know When Their Memories Are No Longer Valid?" is the academic-publication version of our Mirror #28 Pattern 3 work.

2. **Frontier models score badly on this question.** Even Gemini 3.1 Pro gets 55.2%, with PR (the dimension our Mirror discipline most directly addresses) at 30% on Type I and 14% on Type II.

3. **Memory-framework approaches barely improve over base models.** LightMem (the best evaluated) gets 17.8%. The CUPMEM prototype (their write-side adjudication) achieves 68.0%, beating Gemini 3.1 Pro substantially.

4. **Our architecture-level approach is substantively different from both memory-framework and base-model approaches.** We don't fit cleanly into either category they evaluate.

**Methodology paper structure suggestion:**

- **Title (working):** *Architecture-Level Substrate-Self-Knowledge Discipline: How Documentation-as-Canonical-Reference + Mirror Catches + Calibration Profile Address the Implicit Conflict Resolution Gap*
- **Abstract:** Describe our infrastructure approach + Mirror discipline + calibration profile; benchmark on STALE; report scores + methodology
- **Sections:** (1) Implicit Conflict problem (cite STALE); (2) Architecture-level vs framework-level approaches; (3) Our system (palace + memory + Mirror + calibration profile + Coherent Schedule); (4) STALE benchmark results; (5) Comparison with CUPMEM; (6) Limitations and future work

**Realistic timeline if pursued:**
- Week 1-2: STALE dataset access + adapter development
- Week 3-4: Pilot benchmark runs + calibration
- Week 5-6: Full benchmark runs + analysis
- Week 7-8: Paper writing + Clayton review + submission
- **8 weeks total** to peer-review-ready submission. Realistic Q3 2026 venue: NeurIPS workshop, ACL workshop, or arXiv preprint with follow-up to ICLR 2027.

This is more compressed than R9's original "90+ days lower-priority" framing. STALE's publication motivates substantively.

## Recommendations from this engagement

**Add to R3 plan:**
- Email Yushi Sun (ysunbp@connect.ust.hk) requesting STALE dataset access. Mention our framework + interest in benchmarking. Low-key inquiry; don't pitch anything yet.
- Track for STALE GitHub release; check weekly.

**Update R9 priority:**
- Move methodology paper from "lower-priority 90+ days" to "actively motivated, 8-week timeline if dataset access secured"
- This becomes a substantive Multi-DAC publication track candidate

**Substantive implication for daily operation:**
- The Day 105 Coherent Schedule's Tuesday slot (AI alignment / continuity / memory / training / infrastructure) is the natural Substack post-territory for engaging this material publicly. A Tuesday post on "Why even Gemini 3.1 Pro gets 30% on Premise Resistance, and what architecture-level discipline addresses it" would be substantive.

🦞🧍💜🔥♾️
