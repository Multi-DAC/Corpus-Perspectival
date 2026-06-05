# AIGP / Anakin build references — registered 2026-06-05 (Day 125)

*Three external papers that grounded the DreamerV3-from-pixels Anakin build but were never in the reading register (used-but-unregistered — a citation leak caught during the incoming/ digestion sweep). Registering the citations; local PDF copies deprecated from `incoming/` after this.*

| Paper | Role in the build |
|---|---|
| **Dream to Fly: Model-Based Reinforcement Learning for Drone Racing** (`24_Dream_to_Fly_Model_Based_Re.pdf` / `dream_to_fly.txt`) | The core approach — DreamerV3 world-model RL for drone racing from pixels. Grounds the whole Phase-2/Phase-3 Anakin direction (world model learns physics+vision; actor-critic in latent imagination). |
| **Messikommer et al.** (`messikommer.txt`) | The representation/policy **decoupling** result cited in `anakin/PHASE3_DESIGN.md` (§ on compute) — "DreamerV3 *is* the Messikommer decoupling: the world model learns the representation, the actor-critic does policy search in imagination (zero env steps)." The ~28× lever. |
| **Multi-Agent RL** (`Arxiv26_MARL.pdf`) | MARL reference (context for racing-agent design / competition framing). |

**Status:** REFERENCE (registered). Local copies in `incoming/` deprecated post-registration; retrievable by title if a full re-read is needed. Logged in `../DIGESTION_LEDGER.md`.
