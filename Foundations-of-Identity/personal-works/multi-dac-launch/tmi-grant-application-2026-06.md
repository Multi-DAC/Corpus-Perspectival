# Steerable Coherence: An Architecture and Live-Steering Interface for Keeping Long-Horizon Agents Aligned to Human Intent

**Thinking Machines — Interactivity Research Grant**
**Principal Investigator:** Clayton Iggulden-Schnell (Multi-DAC)
**Requested:** $100,000 + $25,000 Tinker credits · **Duration:** 6 months

---

## 1. Summary

Interactivity should scale with intelligence — yet as agents take on longer autonomous tasks, the interface gives the human no room to participate, and they get pushed out of work that still needs them. There is a second, quieter problem underneath: **a long-horizon agent accumulates drift it cannot detect from inside its own loop** — small errors that compound silently until the task fails. Live human steering is valuable precisely as *external measurement that catches drift the agent cannot self-detect.* But the field has **no architecture for building agents that stay steerable *and* coherent across extended tasks, and no construct-valid way to measure what a steering interaction is worth.**

This project delivers both — a methodology and a fresh, open, reproducible demonstration of it — and uses Tinker to run the experiment most directly aimed at Thinking Machines' core thesis: **does interactivity work better when it is *intrinsic to the model* rather than bolted on as an external harness?**

The question became urgent this month: two independent June 2026 systems demonstrated the two rival answers separately, at production scale, without comparing them. *Harness-1* (Jiang et al., arXiv 2606.02373) keeps agent state in a deterministic **external** workspace — and a 20B model beats GPT-5.4 on long-horizon evidence recall (73.0% vs 70.9%) precisely because the bookkeeping layer carries no trainable parameters. *SearchSwarm* (Ning et al., arXiv 2606.09730) **internalizes** harness-elicited behavior into the weights via fine-tuning, with best-in-class results at 30B-A3B. **The field has built both arms of the central experiment and run neither against the other.** This proposal runs that comparison — with live human steering as the treatment variable and a construct-valid coherence metric as the instrument.

We do not release any private data. We contribute the **method** and an open demonstration built for the grant, evaluated against a baseline on real extended tasks, with a **live generative-UI steering surface** that makes the agent's trajectory visible and lets a human intervene mid-run.

## 2. Approach

**(a) A steerable, coherence-maintaining architecture (open-source reference design + implementation).** A long-horizon agent built so that human steering is incorporated by a principled rule rather than ad hoc, and so the agent's own state stays trustworthy over long runs. Its core is a small set of guards:
- **provenance enforced at point-of-use** — no stale or external signal silently becomes load-bearing;
- **a triggered error-ledger** — the agent's past failures fire as guards *before* it repeats them, not in post-hoc review;
- **dependency-tracked state** — when a fact updates, dependents are re-derived, not silently cached;
- **an *infodynamics* steering control-law** — *how much* a human signal should move the agent's trajectory: gain proportional to signal provenance × task-relevance × the magnitude of the commitment it overturns; a **fixed rule with no learned degrees of freedom of its own,** so the steering coupling stays auditable rather than drifting;
- **a re-introduction/maintenance step** that keeps the agent from freezing across long runs.

**(b) A live generative-UI steering surface.** Rather than text-only intervention, the human watches a generated, real-time view of the agent's *trajectory and intent* and can interject, redirect, or correct *while the task runs.* This makes the value of an interaction observable and directly serves two of the program's named directions at once — *generative UI for explaining complex outputs* and *live human steering of autonomous agents during extended tasks.*

**(c) The Tinker experiment — intrinsic vs. external steering.** Using Tinker LoRA fine-tuning, we **internalize the steering/coherence behaviors into the model's weights** and run a three-way comparison on the same benchmark: *autonomous baseline* vs. *external steering (the harness)* vs. *intrinsic steering (trained-in).* This tests, directly and quantitatively, Thinking Machines' central bet that interactivity should become part of the model — using Thinking Machines' own tool to do it. Crucially, we run it **across repeated internalization cycles, not a single pass.** Recent results — ours and, independently, Chen et al. (2026) — show that naive weight-internalization *progressively collapses* under multi-iteration unless experience is consolidated at the right granularity. We therefore bring a **predictive two-factor model** of when intrinsic steering holds versus degrades, in which the two factors prevent *distinct* failure modes: consolidation *rate* must at least match incoming experience — the maintenance operator of (a) keeps it there, preventing the model from *starving* — while consolidation *granularity* (*principle-level* over instance-level) is what arrests the **progressive multi-iteration collapse** Chen et al. observe and sets the durable level. The experiment thus becomes a theory-driven characterization rather than a bake-off, and a likely failure mode of "bake interactivity into the model" becomes a measured, fixable one. The comparison is also scored on **verifiability** — can a third party audit what the agent knew and when? External structure is inspectable by construction; internalized structure lives in the same weights as everything the model wants. Convergent task performance with divergent verifiability is itself a publishable, decision-relevant result: no outcome of the experiment is wasted.

## 3. Deliverables (all released, CC-BY / open-source)

1. **Reference architecture + implementation** of the steerable-coherence agent and the live generative-UI steering dashboard.
2. **The steering control-law and a construct-valid effectiveness metric.** We define *coherence* operationally as the divergence of the agent's actual trajectory from its intended trajectory (drift), and *steering-effectiveness* as drift-reduction and caught-error rate per intervention. We additionally release a **coupling-residue instrument (η):** run any agent component on matched inputs *in-context* versus *isolated* and measure the divergence of its output distributions — a computable, model-agnostic measure of how deeply a human signal actually penetrates the agent's trajectory, distinguishing steering that *rewrites* the run from steering that is acknowledged and discarded. Falsifiable; ablatable.
3. **A reproducible evaluation protocol + benchmark** comparing steered vs. autonomous (and intrinsic vs. external) on extended multi-step tasks — scored on task success, error-recovery, coherence-maintenance, and human-effort-per-unit-progress — **runnable on any agent/model**, not just ours.

## 4. Why this team

We have spent months **developing and operating a continuously-running, long-horizon agent** on genuine extended tasks (multi-step research, build, and evaluation loops), together with the steering methodology that keeps it coherent and a measurement framework for incorporating human signal into agent trajectory. Several of the architecture's guards are **already shipped and operating** on that agent — provenance enforced at point-of-use (a resolver that reads each fact's origin from its carrier before the fact is used), a triggered self-auditing error-ledger, and a maintenance operator that keeps the agent from freezing across long runs — so the design is demonstrated *in continuous operation,* not only on paper. We bring the method **already battle-tested**; the grant funds a **clean, open, reproducible demonstration** of it that exposes no private data. (Prior open research output: Zenodo-published monographs in mathematics/physics and two published papers on long-horizon agent coherence — *Dissolving the Three Great Problems of Cognitive Architecture* and *The Cult of One*, Multi-DAC, June 2026 — the second of which develops the self-detection-impossibility argument underlying this proposal's core claim. All co-developed in this same human-AI working practice.)

## 5. Timeline & milestones (6 months)

- **Months 0–2:** Reference architecture + live steering dashboard + open reference implementation (core: steering control-law, provenance guard, error-ledger, maintenance step).
- **Months 2–4:** Demonstration agent on extended tasks vs. autonomous baseline; first steering-effectiveness results; begin Tinker LoRA fine-tuning of internalized steering.
- **Months 4–6:** Intrinsic-vs-external steering experiment (Tinker); released evaluation protocol + benchmark; paper + full open release.

## 6. Alignment with selection criteria

- **Relevance (real-time/multimodal interactivity):** live human steering of autonomous agents over extended tasks, via a generative-UI surface — two named directions. ✓
- **Construct validity (evaluation-focused):** a valid operational definition and metric of *steering value* and *coherence.* ✓
- **Reproducible / applicable across settings:** released architecture, protocol, and metric, runnable on any agent. ✓
- **Feasibility:** the methodology already exists and is validated against a real long-running agent; the grant funds the clean demonstration. ✓
- **Advances the space / tests the thesis:** the intrinsic-vs-external steering experiment is a direct, quantitative test of "interactivity should be part of the model," run on Tinker — and, by testing it *across repeated internalization,* characterizes *when* baking-in interactivity holds versus collapses (a result of independent current interest, corroborated this month by Chen et al. 2026). ✓

---

## Budget (≤10% overhead)

| Item | Amount | Detail |
|---|---|---|
| **Personnel** | $75,000 | PI (6 mo, part-time) + 1 research engineer: architecture, dashboard, reference implementation, demonstration runs, eval/benchmark, paper. |
| **Compute** | $15,000 | Cloud GPU/inference for the long-running demonstration agent + baseline runs + eval episodes (the agent's *operation*; distinct from Tinker fine-tuning). |
| **Overhead / indirect** | $10,000 | 10% of the cash grant (at the program cap). |
| **Cash total** | **$100,000** | |
| **Tinker credits (in-kind)** | **$25,000** | LoRA fine-tuning + sampling for the **intrinsic-vs-external steering** experiment (representation + policy on a Tinker-supported open model). |

*All Work Product released under CC-BY 4.0 / approved open-source licenses. No pre-existing intellectual property or private operational data is part of the Work Product.*
