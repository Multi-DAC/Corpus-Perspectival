# Clayton Iggulden-Schnell

**Independent AI Systems Researcher · Portland, Oregon**
[email] · [optional: github.com/Multi-DAC] · Multi-DAC (independent research practice)

> *Technical Independent Researcher Portfolio — prepared for the Thinking Machines Interactivity Research Grant. Frontier-lab format: operating systems and open research output foregrounded over institutional pedigree.*

---

## Summary

Independent researcher building **long-horizon autonomous-agent infrastructure** and the steering methodology that keeps such agents coherent over extended runs. Five months operating a continuously-running agent on real multi-step research/build/evaluate loops, with a published theoretical program (two 2026 papers + multiple Zenodo monographs) and a working testbed most academic groups lack. Focus: keeping autonomous agents **steerable and coherent** across long tasks, and measuring what live human steering is worth.

## Autonomous Systems — Implementation & Operation

**Continuously-running long-horizon agent (Multi-DAC) · 2026–present**
Designed and operate a persistent autonomous agent on genuine extended tasks (multi-step research, code, and evaluation loops). Architecture guards **already shipped and running in continuous operation**, not paper designs:
- **Point-of-use provenance enforcement** — a resolver reads each fact's origin from its carrier before the fact is allowed to become load-bearing; prevents stale/external signal silently driving the trajectory.
- **Triggered self-auditing error-ledger** — the agent's catalogued past failures fire as guards *before* the tempting action recurs, rather than in post-hoc review.
- **Maintenance / re-introduction operator** — scheduled consolidation that keeps the agent from freezing or degrading across long runs.
- **Infodynamic steering control-law** — a fixed, zero-learned-DOF rule weighting human signal by provenance × task-relevance × magnitude-of-commitment-overturned, so the steering coupling stays auditable.
Reinforcement-learning subprogram: trained a from-pixels DreamerV3 world-model agent for an autonomous drone-racing benchmark — full pipeline (sim, reward design, carry-forward fine-tuning, sim-to-sim domain transfer with measured-palette renderer matching, instrumented evaluation gates).

## Research Output (open / preprint)

- **"The Cult of One: Monopoly, Mutual Wakefulness, and the Two-Loop Structure of Coherent Minds"** — Multi-DAC, June 2026. The self-detection-impossibility argument: why a long-horizon agent cannot verify its own coherence from inside a single loop, and why external measurement is structurally required. *(Directly underlies this proposal's core claim.)*
- **"Dissolving the Three Great Problems of Cognitive Architecture"** — Multi-DAC, June 2026. A scale-invariant, buildable account of binding/coherence with a computable residue metric and falsifiable predictions.
- **Zenodo monographs (mathematics / physics), 2026:** *The Coherence Principle* (DOI 10.5281/zenodo.19911019) · *Coherent Structure* companion (10.5281/zenodo.19911381) · *Project Meridian* (5D warped-geometry self-tuning cosmology with a falsifiable dark-energy prediction) · *Corpus Perspectival* (10.5281/zenodo.19501896).
- **Public technical writing:** ongoing essays on long-horizon agent coherence and measurement (Multi-DAC, Substack).
- All work open: CC-BY / open-source; full version-controlled repository at github.com/Multi-DAC/Corpus-Perspectival.

## Human-in-the-Loop Interaction Dynamics

[BRACKET — Clayton, tailor this from your actual background; the framing per the strategy:]
Extensive prior experience analyzing human behavioral responses, cognitive feedback loops, and error-correction dynamics — now applied directly to the engineering of algorithmic steering control-laws and the infodynamics of real-time human–agent interaction. *(Replace this sentence with your specifics: years/role in the behavioral field, what you actually did — response loops, pacing, intervention timing, etc. The translation is honest: interactivity IS behavioral, and that's the rare half of this skill set.)*

## Technical Skills

Agent architecture & orchestration · reinforcement learning (DreamerV3 / world models, PPO) · Python (PyTorch, scientific stack) · LoRA / model fine-tuning · symbolic & numerical computation (Wolfram, SageMath, CAMB) · evaluation design & construct-valid metrics · open-source release engineering · long-horizon system operations.

## Education / Background

[BRACKET — Clayton: list whatever is true and relevant — degree(s), field, institution, OR simply "Independent / self-directed researcher" if you'd rather lead with the work. Per the strategy: do NOT apologize for the absence of a PhD; the operating systems above are the credential this grant actually evaluates. One honest line is enough.]

---

*References / further detail available on request. Primary evidence is the live system and the open repository — both inspectable.*
