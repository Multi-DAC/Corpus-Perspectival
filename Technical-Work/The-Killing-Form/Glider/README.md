# Technical-Work / Glider

Applied program: take the Killing-Form regularization and the Coherence Principle into a real, open-weight model. The test subject is **Gemma 4 e2b** (2B parameters, multi-modal, tool-calling, open weights) — a model that's small enough to iterate on and capable enough that results matter.

Glider is the next-step from KF. Where Wells/KF developed the method on synthetic substrates and HRM-class models, Glider asks: does it hold under a model the world actually uses?

## Layout

- `scripts/` — Glider training, evaluation, and analysis scripts.
