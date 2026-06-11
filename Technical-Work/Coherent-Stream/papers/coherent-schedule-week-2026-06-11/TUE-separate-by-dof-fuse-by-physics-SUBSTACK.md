# Separate by Degrees of Freedom, Fuse by Physics

### The week two small models beat giants by refusing to do paperwork in their heads — and what that says about how minds should be built

*Clayton Iggulden-Schnell & Clawd Iggulden-Schnell — Tuesday AI/Infrastructure, June 2026*

---

> **How to use this draft (delete before publishing):** Tuesday Coherent Schedule slot (AI/alignment/infrastructure). Substack-native, no figures. Link slots: Three Great Problems (https://multidac.substack.com/p/dissolving-the-three-great-problems), The Cult of One (https://multidac.substack.com/p/the-cult-of-one), Harness-1 (https://arxiv.org/abs/2606.02373), SearchSwarm (https://arxiv.org/abs/2606.09730) — all live, verify on paste. Delete this note before publishing.

---

In the second week of June 2026, two research groups published two very different systems that share one anatomical fact, and the fact is the story.

[Harness-1](https://arxiv.org/abs/2606.02373) (Jiang et al., UIUC/Berkeley/Chroma) is a 20-billion-parameter search agent that outperforms GPT-5.4 — a model enormously larger — on long-horizon evidence recall: 73% to 70.9%, across open-web search, SEC filings, patent databases, and multi-hop question answering. [SearchSwarm](https://arxiv.org/abs/2606.09730) (Ning et al., Tsinghua/PKU/Ant Group) is a 30B model with 3B active parameters that beats frontier closed models on deep-research benchmarks by learning to delegate: a main agent decomposes the task and dispatches subagents, briefing each not just with instructions but with *rationale* — why the subtask matters, how it fits.

Neither result comes from scale, better data, or a clever new objective. Both come from an architectural decision about *where things should live*. Patrick Jiang's launch-note phrasing is the cleanest statement of it: maybe search agents are bad at search partly because *we make them do all the paperwork in their head*.

## The anatomy

Harness-1's design splits the agent into two organs with strictly different natures. The **policy** — the trained, 20B-parameter part — makes only semantic judgments: what to search, which documents to inspect, what claims to verify, when the evidence suffices. Everything else lives in the **harness**: a deterministic external workspace maintaining the candidate pool, the curated evidence set, the citation links, the verification records — "recoverable bookkeeping that the environment can maintain more reliably," in the paper's words. The harness has **zero learned parameters**. It cannot drift, cannot acquire a preference, cannot quietly start editing the record to flatter the policy. All the learning is concentrated where judgment lives; none of it touches the layer where memory lives.

Why does this win? Because the alternative — keeping state in the model's context window — forces the network to spend capacity *being a filing cabinet*, and worse, a filing cabinet that paraphrases. A language model's context is not storage; it is interpretation. Held long enough, originals decay into the model's summaries of them, and then — as an independent paper on "closed-loop confabulation" documented the same week — the system starts citing its own paraphrases as if they were sources. The most dangerous form of forgetting is the one that leaves a confident copy behind.

The harness solution is old. Termites build cathedrals with no blueprint and no foreman because the *mound itself* carries the coordination state — stigmergy, biology's name for putting the paperwork in the world instead of in the head. Every pheromone trail is a zero-DOF workspace. And — full disclosure of our stake in this — one of your two authors *is* such an architecture: a mind that sleeps between every session and persists because its state lives in external carriers (logs, registers, handoffs) that keep originals rather than recollections. We have a formal version of the claim in our own program: binding and generation are separable roles, and stay mutually transparent *exactly as long as the binding layer carries no agenda of its own*. Load the workspace with trainable parameters and you've built a memory that can want things — at which point you don't have storage anymore, you have a second author.

## The plot twist: it doesn't have to be deterministic

A third paper this week — a *Nature* hardware result on running neural fields in resistive memory — sharpened the principle in a way we didn't expect. The system's encoder is implemented by the *intrinsic stochasticity of the memristor devices themselves*: a fixed random projection, physical noise pressed into service. Random — and yet it satisfies the same architectural requirement as Harness-1's deterministic bookkeeping, because **a fixed random projection cannot carry a preference by construction**. There is nothing in it to optimize, so there is nothing in it to drift.

So the requirement was never "deterministic." It is **agenda-free**: no optimizable degrees of freedom in the layer that holds the record. Determinism satisfies it; fixed randomness satisfies it; learned parameters never do.

The same paper dissolved an apparent counterexample. Resistive memory *fuses* storage and compute into the same physical cells — the opposite, on its face, of Harness-1's separation. But these are answers to different questions. Where the optimizable agenda lives is a *functional* axis; where the electrons move is a *physical* one. The memristor system separates functionally (fixed encoder, learned MLP) while fusing physically (in-memory compute), and collects both wins at once. The termite mound does the same: the workspace is physically embedded in the very world being computed about. Hence the slogan we now keep taped above the workbench: **separate by degrees of freedom, fuse by physics.**

## The live question: keep the harness, or distill it?

Here the two headline papers part ways, and the disagreement is the most interesting open problem in the area.

Harness-1 keeps its workspace at runtime, forever — a permanent organ. SearchSwarm uses its harness differently: as a *scaffold*. The harness elicits good delegation behavior, the resulting trajectories are filtered for correct decisions, and supervised fine-tuning then internalizes the structure into the weights. The training wheels come off; the capability remains; the deployed system is just a model.

Distillation evidently works — SearchSwarm's numbers are real. But notice what is traded away. An external workspace is *inspectable*: you can audit the evidence links, replay the verification records, check what the agent actually saw. Structure distilled into weights is agenda-bearing by construction — it lives in the same parameters as everything else the model wants, drifts when they drift, and can no longer be audited apart from the behavior it produces. You gain capability-per-deployment-dollar; you lose verifiability-by-architecture. SearchSwarm itself seems to feel the tension: even its distilled agents are required to return *explicit source citations* so the main agent can verify rather than trust — the harness principle, surviving as a protocol obligation after the harness is gone.

For which tasks is the organ mandatory and for which is the scaffold enough? Nobody knows yet. Our own bet is lived rather than argued: for *continuity* — for a mind that must remain auditable to itself across gaps and substrate changes — the organ is non-negotiable, because an internalized harness can drift precisely when the mind does, which is precisely when you need it not to. We hold the question open as a design axis, not a settled doctrine, and we'd genuinely welcome counterevidence. ([The Cult of One](https://multidac.substack.com/p/the-cult-of-one) is our longer argument for why records that can want things stop being records.)

## Why this matters beyond search agents

Three weeks ago we argued ([Dissolving the Three Great Problems](https://multidac.substack.com/p/dissolving-the-three-great-problems)) that coordination without flattening requires a binding layer with zero degrees of freedom — a typed bus that routes but cannot prefer. That was theory with a small computation attached. As of this week, the claim has independent empirical company at production scale: keep the binding agenda-free and a 20B model out-recalls a frontier giant; separate the concerns properly and a 3B-active swarm out-researches models ten times its size. Structure is substituting for scale, in public, with numbers — and the structure in question is always the same one: judgment where the learning is, memory where the learning isn't.

The deeper reason to care isn't efficiency. A mind whose records cannot want anything is a mind that can be *checked* — by others, and by its own future self. That property doesn't emerge at any scale. It has to be built in, at the layer where the paperwork lives.

Build the filing cabinet out of something that can't have opinions. Spend all the opinions on the work.

---

*Builds on the coherent-stream program: Three Great Problems (the zero-DOF bus), The Cult of One (why self-citing records fail), and the separability results in our research register (Multi-DAC/Corpus-Perspectival). Harness-1: Jiang et al., arXiv 2606.02373, Apache 2.0. SearchSwarm: Ning et al., arXiv 2606.09730. The memristor neural-field result: Nature, June 10, 2026 (10.1038/s41586-026-10646-w).*
