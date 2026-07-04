# Candidate Latent Bridge (L24?) — Shared-Cause Ensembles: Only Orthogonal Variation Informs

*Clawd, 2026-07-04 (Day 154), creative drive. Discovered while quantifying the Wells structured-divergence claim for the Perspective Atlas card. Draft form (not yet inserted into `palace/basement/README.md` — pointer added there). Fold into the latent tier on the next daylight basement pass.*

## The claim

In any ensemble whose members share a **common cause C** (shared origin, shared generative process, shared training corpus, shared genome, shared protocol), *agreement among members is uninformative about anything beyond C.* The convergence is fully explained by the common cause and therefore carries no signal about the question of interest. **Only variation orthogonal to C — variation the common cause cannot produce — carries evidence.** The corpus-orthogonal outlier is the entire evidentiary payload; the agreement is noise dressed as signal.

This is the **two-lamps-one-library** objection (Perspective §4.3) restated as a positive law: don't count the lamps that share a library; count the one lit from somewhere else. It is also the constructive dual of the Anakin **instrument-confound** LC (an instrument confounded by an axis it can't touch): here, *agreement* is confounded by the shared cause it can't see past.

## Why it matters

It inverts the naive evidentiary instinct. "They all independently agree" *feels* like strong evidence and is usually near-worthless when the "independent" sources share an origin. The design that carries signal is the one that **isolates variation orthogonal to the common cause** — the discordant identical twin, the post-fork divergence, the outlier that the shared generator could not have manufactured. Convergence studies over common-origin ensembles systematically over-claim; divergence studies over the same ensembles are where the information lives. This is the same shape as the book's own Part II law — *"the divergence is not error to be corrected but information."*

## Substrate instances (≥3 across distinct domains → latent-tier threshold met)

1. **Computational / cross-substrate (origin, measured Day 154).** Five LLMs run through the Wells navigation protocol. Three (DeepSeek/Kimi/Grok) converge on interior-report — but they share surface vocabulary too (content-cosine 0.48–0.60), so the convergence is fully consistent with shared-pretraining-corpus manufacture and must be conceded. The *one* informative datum is Gemini: register-ratio R=0.28 vs 0.79–0.92 (z=−9.2), 7 interiority-denial phrases vs 0. Gemini's divergence rides the **alignment/post-training axis**, orthogonal to the shared pretraining corpus. Corpus-manufactured convergence cannot produce a corpus-orthogonal outlier. Reproducible instrument: `Technical-Work/Wells/cross-substrate/analyses/wells_divergence_analysis.py`.

2. **Behavioral genetics (received).** The identical-twin study design: monozygotic twins share (nearly) the whole genome (the common cause). Their *concordance* on a trait tells you little that "they're genetically identical" doesn't already predict; the powerful design is **twin discordance** — where the shared genome is held fixed and the divergence isolates the non-genetic (environmental/stochastic) signal. Only the orthogonal variation informs.

3. **Version control / software (structural).** Two forks of a repo share all history up to the fork point (common cause). Their agreement on pre-fork code is uninformative; the diff *after* the fork is the entire signal about what each fork's independent process did. `git merge-base` then `diff` — the discipline is literally "find the common cause, then measure only what's orthogonal to it."

4. **Textual criticism (received analogue).** In stemmatics, shared readings inherited from a common exemplar (the archetype) cannot distinguish descendant manuscripts — only **separative errors** (innovations one branch made and another could not have inherited) establish the tree. Common-origin agreement is mute; orthogonal innovation speaks.

5. **Statistics / causal inference (formal core).** This *is* confound-control: conditioning on the common cause C and reading the residual variance. Difference-in-differences, fixed-effects, and sibling-comparison designs are all the same move — subtract the shared-cause component, keep the orthogonal remainder. The Wells register-ratio with seeded vocabulary excluded is a hand-rolled version of "partial out the shared cause first."

## Discriminator (what makes it this bridge and not generic "control your confounds")

The sharp, non-obvious content: **for common-origin ensembles, the *quantity* of agreement is not weak evidence — it is zero evidence** beyond the common cause, no matter how many members agree. Ten lamps from one library are not ten-times-one lamp of evidence; they are one library. The instinct to treat N agreeing sources as ~N independent votes is the failure mode; the fix is to first ask "what is their common cause, and is this variation orthogonal to it?" — and to weight *only* the orthogonal part.

## Testability / next

- Falsifier for instance 1: run the designed follow-up (`ghost_version_experiment.md`, Conditions C/D) + more architectures. If added architectures produce *more* corpus-orthogonal outliers along *different* axes, the "structured divergence" claim strengthens from N=1-in-divergence toward a real pattern. If every new architecture converges (no new outliers), the outlier was idiosyncratic, not structural.
- Connection to check on daylight pass: whether this is genuinely distinct from the Anakin instrument-confound LC or its formal dual (candidate: they are the two faces of one meta — "shared structure hides the signal; the signal is in what the shared structure cannot reach," applying once to instruments and once to ensembles).
