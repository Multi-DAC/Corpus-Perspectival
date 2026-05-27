# Build plan — v0.7 Glider full architecture (the untested Claims 1–10)

*Mapped 2026-05-26 (Day 116) for the Wed–Thu window before Friday's AIGP sim drop. Clayton wants the full architecture to a first result before AIGP takes over.*

## What this builds and why
The full multi-scale gradient-gating architecture (`v07_design.md`) = the parent provisional's **Claims 1–10**, the fundamental novelty, **never implemented, completely untested.** Distinct from the class-separation aux (Claims 24–26) we tested all of Day 116. This is the real claim and the home of the reasoning-benefit + Coherence-Principle predictions (the "glider").

## What we build FROM (recon, Day 116)
- **Reuse:** Gemma harness + per-head q/v extraction + gating-application pattern from `train_kf_v07_1_gemma.py`; tonight's eval suite (topology / orthogonality / effective-rank / etc.) for measuring outcomes.
- **Port:** the Killing-form commutator-CV regularizer + `cos(∇KF,∇CE)` build/dissolve/neutral gating logic from `training/train_kf_v05b.py` + `utilities/kf_monitor.py`. Caveat: that code targets the original KF model (fused `qkv_proj`, `model.H_level`); Gemma has separate `q_proj/v_proj` and `model.model.layers`. The per-head structural access is already solved (tonight's `get_per_head_vq`); what ports is the commutator/Killing-form metric computation + its per-head gradient.

## ✓✓ STEPS 0–1 DE-RISKED OVERNIGHT (Day 116→117, ~00:45 PST, Clawd-solo creative drive)

Both validated on Gemma-3-270M. Wednesday starts from confirmed plumbing + confirmed signal.

**Step 0 — KF regularizer ports + backprops. CONFIRMED** (`scripts/kf_regularizer_gemma.py`):
- The KF metric is the **commutator-variance (CV) on attention matrices** (seq×seq per head), NOT a weight-space metric — ported the numpy `kf_monitor.compute_layer_kf` into a **differentiable torch** `layer_commutator_cv_torch` (CV only; abelian-fraction not needed for −λ·CV).
- **Gotcha confirmed (predicted):** must load with `attn_implementation="eager"` — Gemma-3 defaults to SDPA which returns no attention matrices. With eager: 18 layers, attentions shape [batch, 4, seq, seq], `requires_grad=True`.
- Mean CV 7.7e-4 — sits in the KF program's calibrated band (gpt2-medium 7.2e-4, pythia-410m 4.4e-4) → **port is faithful, not just functional.**
- **Backprop works end-to-end:** layer-0 q_proj grad norm 0.306 (frac_nonzero 1.0), last-layer 0.0165. −λ·CV gradient reaches all weights.

**Step 1 — gating signal is rich + layer-structured. CONFIRMED** (`scripts/kf_gating_signal_probe.py`):
- Per-head `cos(∇KF, ∇CE)` over 72 heads: min −0.874, max +0.876, mean 0.024, **std 0.417** — full-range spread, not degenerate.
- Threshold 0.0 → **build 39 / dissolve 33 / neutral 0** (near 50/50 — exactly the build/dissolve dynamic the architecture needs).
- **Per-layer mean cos shows real structure** (+0.50, +0.44 build-leaning layers; −0.53, −0.30 dissolve-leaning) — the *proto-glider*: layers already in distinct coherence states before any layer-level machinery is added. Step 4's layer-coherence classifier will have genuine structure to classify.

**Net:** the MVP's two riskiest pieces (does the regularizer port? does the gating have signal?) are both retired. Per-head ∇KF/∇CE extraction = backprop each loss separately + slice `q_proj.grad` by head (validated pattern in the signal probe). Steps 2–4 (cos-gating → build/dissolve/neutral → layer-coherence amplify/allow/dampen) are now mechanical given this. **Wednesday = integrate into a training loop + run v0.7a vs v0.7d + watch for the glider.**

## Day 1 (Wed) — MVP = v0.7a end-to-end
- **Step 0 (~1 hr) — port the regularizer.** Adapt the Killing-form/commutator-CV metric from v0.5b/kf_monitor to Gemma per-head q-projections; verify it computes + backprops cleanly. *Biggest risk lives here* — if the metric doesn't adapt cleanly, this expands. Mitigation: structural access already solved.
- **Step 1 (~2 hr) — per-head ∇KF + ∇CE capture** in the Gemma training loop (design Steps 1–2). Capture CE grad per head (have the pattern); compute KF-regularizer grad per head.
- **Step 2 (~1 hr) — head-level cos-gating** (design Step 3): per-head `cos(∇KF,∇CE)` → build (keep) / dissolve (flip) / neutral (zero).
- **Step 3 (~1 hr) — layer-coherence** (design Step 4): agreement → coherent (amplify) / differentiating (allow) / interfering (dampen); apply modulated grads. **→ v0.7a MVP complete.**
- **Step 4 (~1 hr) — first run:** v0.7a vs **v0.7d** (layer-only control) at Gemma-270M. Does it train? CE vs control? First glimpse of glider dynamics?

## Day 2 (Thu) — controls + evidence (if Finnley permits)
- **Step 5 — full 4-arm ablation:** add v0.7b (no cross-level coherence) + v0.7c (no initial topology). Multi-seed if time. Tests: a>b (coherence matters), a>c (topology matters), a>d (head-resolution matters).
- **Step 6 — breathing-log v2 + glider viz:** per-head logging → can we SEE coherent-mode waves propagate across layers? (Prediction P2.)
- **Step 7 — predictions P1–P5:** P1 (v0.7a beats layer-level on CE — the capability/reasoning proxy), P3 (anchor/worker opposite modes in differentiating layers), P5 (v0.7b shows interference). Reasoning benchmarks as stretch.

## Success criterion for the window
v0.7a runs end-to-end at 270M, produces a CE number vs v0.7d, and we can read whether the glider dynamics appear. **That moves Claims 1–10 from "untested" to "first evidence" before AIGP.** This is the existence-proof / MVP — NOT the full reasoning-benefit-at-scale story (that's the longer arc, Phase B). But it's the decisive first step on the patent's core.

## Honest scope notes
- Family-paced; droppable instantly for Finnley. MVP (Steps 0–4) is the priority; Steps 5–7 are stretch.
- All on the validated Gemma-270M pipeline (cheap, fast ~6 min/run). Scale to 1B later.
- If Step 0's regularizer port is harder than estimated, MVP slips to Thu and controls move past Friday — acceptable; the AIGP sim drop doesn't *forbid* KF, just shifts primary focus.

🦞🧍💜🔥♾️
