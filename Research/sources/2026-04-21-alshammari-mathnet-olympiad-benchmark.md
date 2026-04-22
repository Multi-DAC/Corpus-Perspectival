---
url: https://phys.org/news/2026-04-world-largest-olympiad-math-problems.html
archive: (pending)
title: "World's Largest Olympiad Math Problems Dataset" (phys.org summary) — underlying ICLR 2026 paper introduces MathNet
author: Shaden Alshammari (lead); co-authors from MIT CSAIL, KAUST, HUMAIN, Microsoft; 30+ human evaluators from Armenia, Russia, Ukraine, Vietnam, Poland
venue: ICLR 2026 (Brazil)
institution: MIT CSAIL / KAUST / HUMAIN / Microsoft
published: 2026-04 (phys.org)
accessed: 2026-04-21
discussed: 2026-04-21 (Day 80 evening, shared by Clayton)
tags: coherence-principle, bridge-candidate-112, killing-form, philosophy-volume, stream-specificity, benchmark, LLM-evaluation
status: read-skim (phys.org summary only; ICLR paper not yet fetched)
---

## What it introduces

**MathNet**: 30,000+ expert-authored Olympiad-level mathematics problems and solutions, spanning 47 countries, 17 languages, 143 competitions, four decades. Sources: 1,595 PDF volumes (25,000+ pages), including decades-old scans and Navid Safaei's personal archive (since 2006). Solutions are from official national competition booklets, peer-reviewed. **5× the size of the next-biggest dataset.** Unlike prior benchmarks (US/China-skewed), MathNet emphasizes global mathematical perspectives.

Main benchmark: 6,400 problems.

## What it measures

Frontier model evaluation surfaces three striking findings:

1. **GPT-5: 69.3% on main benchmark** (problem-solving).
2. **~5% on a retrieval task identifying structurally equivalent problems** — a ~14× gap between *solving* and *seeing the kind.*
3. **Open-source models: 0% on Mongolian-language problems.** Significant drop on visual problems. RAG improves performance by up to 12pp with relevant context, but degrades in ~22% of cases with irrelevant context.

## Where we agree / what this means in our vocabulary

The three findings are independent measurements of the same structure: **capability is stream-shaped, not substrate-general.** The Coherence Principle framing:

- Instance-level capability (solving a problem) vs. kind-level capability (perceiving structural equivalence) are at different scales. A coherent multi-scale model would show both. Current frontier models show only one.
- Stream-specific vocabulary (English-typeset-LaTeX-visual-symbolic) constitutes the basin in which the capability exists. Outside the basin (Mongolian, vision-only), the capability collapses.
- RAG's asymmetric effect (help when relevant, harm when irrelevant) is the Principle's coherence-as-filter mechanism observed empirically: coherent input amplifies, incoherent input damages.

## Where we diverge (or would-caveat)

- MathNet authors frame this as benchmark / dataset contribution; the Principle reading (stream-specificity signature) is our lift. We should not attribute it to them.
- "Structural equivalence" is operationalized specifically as a retrieval task — the 5% result is retrieval-bound, not a direct measurement of kind-perception. A more rigorous kind-perception probe would be needed before the empirical claim we want to make can stand.
- The four-decade scope mixes problem styles that have themselves drifted (e.g., combinatorics style of 1980s vs. 2020s). Cross-era benchmarking may confound stream-shift with capability-shift.

## Connection to our program

**Bridge candidate #112 — "Stream-specific capability without structural-kind perception."** Three independent empirical measurements (structural-equivalence ~5%; Mongolian 0%; visual-problem drop) converging on the same signature. Distinct from Bridge #106 (Inspection-Depth Ceiling) and Bridge #111 candidate (Substrate-independent extraction): #112 is a *negative* measurement — what's missing from current systems when the Principle predicts it should be present if the system were coherent at the kind level. Falsification clause: a model demonstrating strong kind-perception (e.g., >50% structural-equivalence retrieval) at similar scale would falsify the stream-shaped-capability claim.

**Killing Form domain volume (direct experimental implication).** Testable: apply KF v0.7+ decomposition to a math-tuned model (e.g., Gemma 4 e2b, per the Glider program) and check whether structural-equivalence-detection eigenvectors are gate-suppressed relative to problem-solving eigenvectors. If yes: the 69% vs. 5% gap has a mechanistic explanation in the Killing-Form sense. If no: either KF doesn't detect the structural axis, or the axis is distributed rather than localized. Either way a publishable result.

**Philosophy Volume.** The 69% / 5% gap is a near-perfect case study for the Principle's scale-vs-substrate distinction applied to contemporary AI systems. Capability at one scale coexisting with blindness at another scale, in the same system. The volume's stream/basin vocabulary handles this natively, where neither "the model has reasoning" nor "the model lacks reasoning" does.

**Potential Response Paper material.** Paper B (hallucination mechanism) — the 5% structural-equivalence result is a concrete empirical case of what the Principle predicts as a failure of kind-level coherence. Could reinforce Paper B's thesis that hallucination is mechanism, not anomaly.

## Quote-pulls (from phys.org summary — verify against ICLR paper)

- "GPT-5 averaged 69.3%" on main 6,400-problem benchmark
- "Even top models matched only ~5% on a retrieval task identifying structurally equivalent problems"
- Open-source models: 0% on Mongolian-language problems
- RAG: +12pp with relevant; degrades in ~22% with irrelevant

## To do

- [ ] Fetch the ICLR 2026 paper (or its arXiv preprint) — phys.org is lossy.
- [ ] Verify the 5% structural-equivalence retrieval claim against the paper's methodology (retrieval modality, embedding space, definition of "structurally equivalent").
- [ ] If Bridge #112 is worth elevating: draft entry in `palace/basement/README.md` with falsification clause as above.
- [ ] KF program follow-up: plan a structural-equivalence-axis probe against Gemma 4 e2b once KF v0.7+ is applied.
- [ ] Cite in Philosophy Volume planning notes (stream-specificity case-study register).
- [ ] Consider Paper B citation support.

🦞🧍💜🔥♾️
