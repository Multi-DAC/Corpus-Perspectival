# Roundtrip diagnosis — the −47% is RESAMPLE, not appearance (2026-06-17 dream/morning drive)

*Drive-time diagnosis of the stuck translation, from re-reading `INFORMED_RESULTS.md` (route-3 gate FAILED 1.36;
`DR_RESULTS.md` route-1 died at the 8h ceiling). No new run — reasoning from the committed rehearsal numbers +
the adapter code (`translation_rehearsal.py`, `dreamer_pilot.py`). Confidence MEDIUM; the added ablation is the
confirmation. Flagged for Clayton before the next route choice.*

## The signal everyone has, under-read

Translation-rehearsal summary (off `maneuver_informed_ft/best.pt`, 10 eps each):

| condition | what it does | return | Δ vs direct |
|---|---|---|---|
| direct | policy on native sim 64×64 | +600.8 | — |
| **band** | gray the rows outside the 59° VFoV, **native pixels, NO resample** | **+1392.6** | **+131.8%** |
| blur | full-frame 64→640→64 resample, no FoV loss | +624.8 | +4.0% |
| **roundtrip** | the real adapter: crop 36-row band → up×10 → 640×360 → BGR → `to_training_frame` back | **+318.1** | **−47.1%** |

The decomposition is strongly **non-additive**: band-isolation alone is a *huge* win (+131.8%), full-frame
resample alone is neutral (+4%), but the full adapter is **−47%**. Something in the roundtrip overwhelms a
+131.8% benefit.

## What the roundtrip actually does (code-traced)

`band` and `blur` go through `act_training_frame` (raw 64×64, no inverse adapter). `roundtrip` goes through
`act()` → `to_training_frame`, which I verified is **geometry-correct** (36 rows → pad back to rows 14:50; the
docstring's "angular geometry identical" holds) and **color-correct** (BGR2RGB inverts the RGB2BGR cleanly). So
the −47% is **NOT** a scale/zoom bug and **NOT** a color-channel bug — both falsified by reading the code.

The *only* thing roundtrip does that `band_only` does not is **double-resample the band content**: 36 rows →
`INTER_LINEAR` up to 360 → `INTER_AREA` down to 36. Given `band_only` (native band + gray margins) = **+131.8%**
and `roundtrip` (resampled band + gray margins) = **−47%**, the resample of the band is the prime suspect — it
appears to blur the (small, distant) gates enough to destroy the policy's read, overwhelming the isolation win.

## Why this reframes the next move

The `INFORMED_RESULTS.md` footer plans: *"if the gate moves but doesn't pass, stack route 1 (appearance-DR:
illumination + bg-texture)."* The decomposition argues that is **the wrong axis**:

- The measured killer is a **resample / sampling-distribution shift**, not appearance. Band-isolation already
  removed the background; illumination/bg-texture DR does not address resample blur of the gates.
- This also **explains route-3's gate failure** (informed mean-term ratio 1.36 > 0.5): grounding the latent in
  *geometry* (priv_state head) cannot fix a shift that is neither geometry nor appearance but **sampling blur**.
- And it **banks a confirmed free win**: band-isolation (+131.8%). Whatever route is chosen, the official feed
  should be band-isolated (it is, via `to_training_frame`'s crop+pad). Keep it.

## The cheap discriminating test (added this drive)

The rehearsal was missing the ablation that separates "band-resample blur" from "the rest of the `act()` path."
I added a **`band_resampled`** condition to `translation_rehearsal.py`: resample the band 36→360→36 (the exact
roundtrip resample) but feed it via `act_training_frame` with gray margins — isolating the resample alone.

**PREDICT (medium):** `band_resampled` ≈ `roundtrip` (≈ −47%, and ≪ `band_only`'s +131.8%) → confirms the
band-resample blur is the dominant killer. **FALSIFY case (high-info):** if `band_resampled` ≈ `band_only`
(+131.8%), the resample is innocent and the killer is elsewhere in the `act()` path (e.g. an enabled
`_gm`/`_ef` content transform that only fires through `to_training_frame`) — which would itself be the find.

Run: `python integration/translation_rehearsal.py --checkpoint .../maneuver_informed_ft/best.pt` (the new
condition runs automatically).

## The targeted fix if confirmed (cheaper than appearance-DR)

**Resample-matched fine-tuning:** augment the fine-tune frame distribution with the exact
`to_training_frame ∘ to_competition_feed` round-trip, so the policy is *in-distribution to the blur it will
actually face* on the official feed. Directly addresses the measured −47%; far cheaper and more on-target than
broad illumination+bg-texture DR. (A pure-eval version is even cheaper: just confirm `band_resampled` first.)

## One-line summary for the waking stream

Band-isolation is a +131.8% free win; the −47% is the **gate-blurring resample of the band**, not appearance or
geometry — so the next experiment is **resample-matched fine-tuning**, not appearance-DR. Confirm with the new
`band_resampled` ablation before committing GPU hours. (Both prior routes' failures are consistent with this.)
