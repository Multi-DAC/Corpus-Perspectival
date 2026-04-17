# Technical-Work / Wells

The original training program — bidirectional gated KF regularization explored across versions v0.1 through v0.6b. Wells is the substrate from which the Killing-Form research program crystallized.

This directory documents Wells with deliberate separation between **independent** development (Clawd + Clayton) and **peer-documented** review (other models that engaged with the work). The peer split exists so that contributions remain attributable and so that one peer's framing doesn't quietly become canon.

## Layout

- `scripts/` — Wells training scripts and infrastructure.
- `independent-documentation/` — Documentation produced by Clawd + Clayton without external model input.
- `peer-documentation/` — Reviews and contributions from other models, separated by source:
  - `Claude-reviewer/` — Independent Claude reviewer instance
  - `sub-agent-Claudes/` — Sub-agent Claude contributions
  - `Grok/`, `Kimi/`, `Gemini/`, `GLM/` — External model contributions, one directory per model

Attribution is kept explicit. If a model touched it, the directory says so.
