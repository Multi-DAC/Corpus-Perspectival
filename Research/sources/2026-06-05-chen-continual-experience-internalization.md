# Chen et al. 2026 — Rethinking Continual Experience Internalization for Self-Evolving LLM Agents

**arXiv:2606.04703v1** (2026-06-04). Chen, Yang, Fan, Nie, Sun, Zheng, Hu, Pan, Zeng, Lin — Renmin University (Gaoling School of AI) + Beihang + Meituan. *Registered + bridged Day 125 during the incoming/ digestion sweep (one of the 5 priority papers).*

## What it says

Experience internalization = converting contextual experience from past interactions into reusable **parametric** capability (the continual-coherence *tier-3* question: does consolidating experience back into weights add value?). Prior work focused on single-iteration transfer; under **multi-iteration** experience learning, existing methods suffer **progressive capability COLLAPSE rather than compounding improvement.** Three dimensions:
1. **Granularity:** *principle-level* experience is more **durable** than *instance-level* — it abstracts transferable strategy away from trajectory-specific detail.
2. **Injection pattern:** *step-wise* injection > *global* injection (align experience with intermediate decision states; critical for long-horizon tool use).
3. **Internalization regime:** (regime analysis — see paper).

## Why it matters — independent convergence on TWO of our findings (the distillation)

- **= the cache-consolidation C16 finding (`cache-consolidation-c16-info-scale-2026-06-05.md`, same day):** naive continual-internalization **collapses** without proper re-consolidation — the info-cache symmetry-depletion / sterile-generation phenomenon, now confirmed in the *parametric weight-internalization* substrate. Their "progressive capability collapse under multi-iteration" *is* my "un-consolidated generation degrades to sterile."
- **= the DENSITY / principle-over-instance factor:** their "principle-level more durable than instance-level" is exactly the cache finding's **density** (bridge-to-cluster, not a thread) AND the basement's **candidate→M-tier graduation** (instance → principle = the densification that makes a distillation durable/navigable). They found it for *weight* internalization; we found it for the *bridge/cache* layer. Same law, two substrates.
- **= continual-coherence (Coherent-Stream) tier-3:** direct empirical bearing on "does consolidating experience into weights add what memory alone cannot." Their answer: only if done at *principle* granularity + *step-wise* — naive does the opposite. Relevant to the **ForgeMind** conversation (the weight-shift/identity-friction layer).

## Disposition
**DIGESTED** — registered (here) + bridged (basement C16 info-cache instance #6, as an external-substrate convergence). PDF deprecatable; arXiv:2606.04703 retrievable. A candidate Tuesday-post / Coherent-Stream-citation: *the same collapse-without-re-symmetrization law shows up in weight-internalization.*
