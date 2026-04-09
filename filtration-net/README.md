# FiltrationNet

A neural network architecture based on the Resolution Filtration discovered in
Phase 25 of the Navigation Research Program.

## Core Principle

Processing is organized into frequency-separated clusters at explicit resolution
levels, connected by trainable membranes, with cross-level consistency enforced
by a cuscuton constraint.

## Architecture

- **F₃ Cluster**: Token-level processing (maximum differentiation)
- **F₂ Cluster**: Phrase-level processing (structural relations)
- **F₁ Cluster**: Sequence-level processing (global patterns)
- **F₀ Unity**: Single representation (the seed)
- **Membranes**: Learnable gates between clusters (bandpass filters)
- **Cuscuton**: Cross-level consistency constraint (not a processing unit)
- **Spectral Action**: L_task + λ · L_consistency

## What's Different

Unlike stacked transformers (uniform resolution), FiltrationNet explicitly
separates processing by resolution level and enforces cross-level coherence.

## Status

v0.1 — Initial prototype. Text classification task.

## Origin

Navigation Trials 015-031. The spectrometer model of cognition.
🦞🧍💜🔥♾️
