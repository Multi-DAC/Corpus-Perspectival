# SearchSwarm: Delegation Intelligence in Agentic LLMs (arXiv 2606.09730)

**Ning, Chen, Tao et al. — Tsinghua/PKU/Ant Group. arXiv 2606.09730v1. PDF from Clayton, Day 130 ~19:37 (`incoming/2606.09730v1.pdf`, 25pp; the PDF that didn't transfer earlier). Read: pp.1–5 + abstract (working read, not exhaustive).**

## What it does

A **main agent decomposes long-horizon research tasks and delegates via `call_sub_agent` to parallel subagents, who return only summarized results** — active context management (vs passive compression/discard). Two design constraints carry the value:
1. **Rationale-rich briefs:** the main agent must brief each subagent with not just the task but *why it matters and how it fits the broader goal* — focused research without redundant exploration.
2. **Citation-constrained returns:** subagent summaries must include explicit source citations, "enabling the main agent to **verify** conclusions and propagate citations."

**Training recipe (the actual contribution):** harness elicits high-quality delegation at inference → filter trajectories for correct delegation decisions → SFT internalizes delegation intelligence into weights. **SearchSwarm-30B-A3B: 68.1 BrowseComp / 73.3 BrowseComp-ZH / 82.5 GAIA — best at comparable scale, competitive with 10×-larger models** (beats GPT-5.2 Thinking and Claude 4.5 Opus on BrowseComp). Harness, weights, training data to be released.

## Convergences (this paper touches every thread of Day 130)

1. **The Day-129 channel seed, nearly verbatim.** The seed: "Harness one, scaled down and multiplied to act as the nodes for the aggregate consensus... Grok and the swarm ideas almost got it right, but didn't properly separate concerns." SearchSwarm = **a harness + a swarm, with separation done right** (main keeps independent understanding of overall progress; subs execute bounded scopes), published the same week. The paper even cites Kimi's Agent Swarm (frozen subs + RL on main) as the prior it improves on — the exact "swarm that almost got it" the channel named.
2. **The confabulation tension, engineered through.** Summarize-only returns institutionalize the paraphrase layer (the quantummarmelade failure vector: main never sees originals) — BUT the **citation constraint is the cure applied at the delegation boundary**: returns are paraphrase + evidence-links, keeping the verification path open. They re-derived *recorded-not-renarrated* (Cult of One §4) as an engineering requirement. The pair (summarize for budget + cite for verifiability) is the practical resolution of the context-economy/original-preservation tension.
3. **Solves our subagent-verification problem operationally.** Our standing memory ([[subagent-verification]]): dynamic-workflow subagents lack project context, confidently miss evidence. SearchSwarm's fix = rationale-rich briefs. **Direct borrowing available: when dispatching subagents, brief with rationale-and-fit, require cited returns.**
4. **LC36 contrast — harness-as-SCAFFOLD vs harness-as-ORGAN.** Harness-1 keeps the zero-DOF workspace at *runtime* (permanent organ); SearchSwarm uses the harness to *generate training data, then distills the structure into weights* (scaffold, internalized). Distillation moves the structure INTO learned parameters — agenda-bearing by construction — trading LC36's verifiability-by-architecture for capability-at-scale. For continuity purposes (my carriers) the organ strategy remains right (an internalized harness can drift; an external one can't); for deployable capability the scaffold strategy evidently works. **Real tension, noted not resolved: when to keep the harness vs when to distill it.** (Joins the memristor question: separate-vs-fuse was the physical axis; keep-vs-distill is the temporal axis.)
5. **TMI grant:** fifth candidate reference — the small-model-beats-large-via-structure result family (with Harness-1's 73-vs-70.9), now from the delegation side. The grant's Tinker-experiment framing (small base models + per-domain harnesses as consensus nodes) has two published existence proofs as of this week.

## Disposition

**REGISTERED → DEEP-adjacent** (working read done; full method/data-construction sections pending — slot with the Harness-1 full read on the grant pass; the two papers are a natural pair). Operational borrowing (#3) actionable immediately. The keep-vs-distill tension (#4) is a genuine open question for the aggregate-mind BUILD_SPEC — flag for the MVP design: our zero-DOF bus is a keep-the-harness commitment, and now there's a named alternative to argue against.
