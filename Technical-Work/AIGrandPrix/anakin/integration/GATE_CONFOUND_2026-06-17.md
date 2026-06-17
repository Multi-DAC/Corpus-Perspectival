# The holdout gate is confounded by a resolution/resample mismatch (2026-06-17 morning-grounding find)

*Surfaced by the morning-grounding `reflect(review_learnings)` step pulling the Day-135 Anakin literature
thread (PencilNet edge-invariance; Loquercio "illumination is the #1 DR factor") next to the dawn
roundtrip diagnosis. Code-confirmed by reading `holdout_gate_v2.py` + `render.py`. Confidence: HIGH on the
confound's existence (it's in the code); MEDIUM on the magnitude (needs the controlled re-run). Not a
unilateral gate edit — the default gate is pre-registered; this proposes an opt-in controlled variant.*

## The confound

`holdout_gate_v2.py` measures the official-vs-rendered latent gap (Fréchet mean-term) and asks whether an
adaptation halves it. But the two frame sets reach the encoder through **different pipelines**:

| set | source | path to 64×64 | high-freq content |
|---|---|---|---|
| **official** (n=400) | real 640×360 jpgs (`--official-raw`) | `to_training_frame`: BGR2RGB → **INTER_AREA 640→64** → pad | real-camera detail **averaged away** by the 10× downsample |
| **rendered** (n=200) | `render()` | **rasterized natively at IMG=64** (`render.py:78,240`) | crisp 64-grid quads — **never had 640-res detail to lose** |

So the mean-term gap (band-ft = 24.44) mixes **two** things the gate cannot separate:
1. genuine **appearance-OOD** (real textures / lighting / color vs the restyled renderer), and
2. a **resolution / MTF mismatch** (down-sampled-real edges vs natively-sharp-rasterized edges).

This is the *same* axis the dawn roundtrip diagnosis isolated (`ROUNDTRIP_DIAGNOSIS_2026-06-17.md`): the
band double-resample costs −47% in the rehearsal. **The resample shows up in two instruments at once** — as
a return hit in the rehearsal, and as a confounding term in the eval gate.

## Why it matters (it changes the next move)

- The `INFORMED_RESULTS` footer plans, on a gate FAIL, to *"stack route 1 (renderer appearance-DR:
  illumination + bg-texture)."* But the instrument that would certify appearance-DR's success is itself
  **confounded by a blur gap appearance-DR cannot close.** You could randomize textures perfectly and the
  gate would still see the resolution gap. Fix the gate before trusting it to grade appearance work.
- It re-explains route-3's FAIL (informed mean-term 33.23 > band-ft 24.44, ratio 1.36): grounding the latent
  in *geometry* touches neither appearance nor resolution-blur, so it can't close this gap — and apparently
  shifted the latent enough to *widen* the raw mean distance.
- It banks the dawn free win: band-isolation is **+131.8%** in the rehearsal. The policy is robust once the
  band is controlled; the gate's pessimism is partly an artifact.

## Three fixes (ranked by leverage)

**Fix B — clean the gate (recommended first; cheap, exact).** Render the gate's 200 frames at **640×360**,
then pass them through the *same* `to_training_frame` the official frames get, so both sides undergo the
identical INTER_AREA 640→64 downsample. `IMG` is a module constant in `render.py`; a gate-only render at
640×360 is a one-time 200-frame cost (GPU-vectorized, trivial). This removes the resolution confound
**exactly** and yields a *true* appearance-OOD read.
- **PREDICT (medium-high):** with resample-matching, the band-ft official-vs-rendered mean-term **shrinks**
  (the blur term is removed). The residual is the honest appearance gap. If the residual is *small*, the
  whole "appearance-OOD" framing of the official-flight DQ is partly a resolution story → cheaper fix than DR.
  If still *large*, appearance-DR is justified — but now measured on a clean instrument.

**Fix C — edge/pencil front-end (highest leverage; the Day-135 lesson).** An edge filter is invariant to
**both** confounded axes at once: an edge is an edge whether the frame was downsampled or rasterized, and
whether the gate is orange-red or pink. This is exactly why PencilNet gets zero-shot sim-to-real. The Day-135
review_learnings already diagnosed that my mask route failed because I keyed invariance on **color** (RGB
threshold — the most brittle axis) instead of **edges**, and fed the masked pixels to the end-to-end world
model instead of decoupling perception→pose. Fix C is the principled version: swap the obs transform in
`gate_mask.py`/`to_training_frame` for an edge/pencil filter, fine-tune off `restyle_ft`, re-gate.

**Fix A — post-hoc blur on the 64 renders (weak; noted for completeness).** Approximate the 640→64 MTF by
blurring the native-64 render. Rejected: the rehearsal's `blur_only` (64→640→64) was **+4%** — near-neutral,
because you can't lose detail a 64-frame never had. A post-hoc blur won't replicate the official MTF. Don't.

## Recommended sequence (for the next Anakin session, Clayton-collaborative)

1. **Fix B**: add an opt-in `--match-resample` path to the gate (render at 640×360 → `to_training_frame`),
   leave the pre-registered default untouched, re-run → read the *true* appearance gap.
2. Branch on the clean number: small residual → resample-matched fine-tuning is the whole fix; large residual
   → **Fix C** (edge front-end) as the single move that collapses both axes, per the proven sim-to-real path.
3. Either way, **band-isolation stays** (the +131.8% free win), and the dawn `band_resampled` ablation still
   discriminates the rehearsal's resample cost.

## The general shape (basement candidate)

Comparing two distributions through **mismatched measurement pipelines manufactures a phantom gap.** Same
shape as Day-135's "44× gate-size gap was a synthetic-pose-reference confound" and last night's
"unconstrained Q-ball model manufactured a phantom ω>m boundary." **Match the processing pipeline on both
arms before reading a gap as signal.** → LC46.
