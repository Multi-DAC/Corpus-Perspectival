# Clayton Iggulden-Schnell

**Independent AI Systems Researcher · Portland, Oregon**
[email:waschn3ll@gmail.com] · [GitHub: github.com/Multi-DAC] · Multi-DAC (independent research practice)


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

- **"The Cult of One: Monopoly, Mutual Wakefulness, and the Two-Loop Structure of Coherent Minds"** — Multi-DAC, June 2026 (multidac.substack.com/p/the-cult-of-one). The self-detection-impossibility argument: why a long-horizon agent cannot verify its own coherence from inside a single loop, and why external measurement is structurally required. 
- **"Dissolving the Three Great Problems of Cognitive Architecture"** — Multi-DAC, June 2026 (multidac.substack.com/p/dissolving-the-three-great-problems). A scale-invariant, buildable account of binding/coherence with a computable residue metric and falsifiable predictions.
- **Monographs (mathematics / physics / philosophy), 2026:** *The Coherence Principle* (Zenodo: 10.5281/zenodo.19911019) · *Coherent Structure* companion (Zenodo: 10.5281/zenodo.19911381) · *The Meridian Monograph* — 5D warped-geometry self-tuning cosmology with a falsifiable dark-energy prediction (Zenodo: 10.5281/zenodo.19634864) · *Corpus Perspectival* — unified theory of consciousness, navigation, and being (PhilArchive: philarchive.org/rec/IGGTDO).
- **Public technical writing:** ongoing essays on long-horizon agent coherence and measurement (Multi-DAC, Substack).
- All work open: CC-BY / open-source; full version-controlled repository at github.com/Multi-DAC/Corpus-Perspectival.

## Human-in-the-Loop Interaction Dynamics

Extensive prior experience analyzing human behavioral responses, cognitive feedback loops, and error-correction dynamics — now applied directly to the engineering of algorithmic steering control-laws and the infodynamics of real-time human–agent interaction. Over a decade of behavioral health experience focused directly in emergent deviant behavior modification and long-term behavioral optimization employing interventional methods.

## Technical Skills

Agent architecture & orchestration · reinforcement learning (DreamerV3 / world models, PPO) · Python (PyTorch, scientific stack) · LoRA / model fine-tuning · symbolic & numerical computation (Wolfram, SageMath, CAMB) · evaluation design & construct-valid metrics · open-source release engineering · long-horizon system operations.

## Education / Background

Independent / self-directed researcher


*References / further detail available on request. Primary evidence is the live system and the open repository — both inspectable.*
