# Actor-Recouple: teaching Anakin's hands to use his new eyes

*Day 153, 2026-07-03. The "next unlock" after the perception fine-tune. Design-first (survives interruption); build the script after. HOLD execution until Clayton's percept_ft flight measures how bad the decoupling actually is.*

## The problem (verified from source)
`perception_ft.py` fine-tuned the **world model only** (`wm._train(batch)`, line 124; actor/critic frozen, line 5–6). It taught the encoder/dynamics to *see* real frames — but it **shifted the WM's latent geometry** to accommodate them. The actor (`_task_behavior`) was trained against the *blind* WM's latents and was never updated. Result: **new eyes, old hands** — the actor may act poorly even on rendered frames now, because the latents it reads no longer mean what they meant when it learned to fly.

## The fix, and why it needs no new sim data
DreamerV3 trains its actor-critic **in imagination** — latent rollouts inside the WM, scored by the WM's reward head. So re-coupling the actor to the seeing WM is a **continued-training run, not a data-collection run**: no env in the loop for the actor, no new hand-flown frames needed.

**The reward crux (the real design constraint):** the real frames have **no reward** (the new sim stripped reward/position telemetry → dummy-0 in `sample_real`, line 82). Reward exists *only* in the **rendered** rollouts (`maneuver_env`, line 65). Therefore the recouple must keep reward grounded in the rendered env: the WM's reward head stays calibrated *because* half the batch is rendered-with-real-reward, and the imagined actor-critic training reads that calibrated reward head. **Real frames supply perception; rendered rollouts supply reward; imagination re-couples the hands to the eyes.**

## Recipe (minimal change to perception_ft.py)
Continue the *same* mixed real+rendered pipeline, but train the **full agent** (WM + actor-critic) instead of WM-only:
- Replace `wm._train(batch)` → the Dreamer agent's full train step (`agent._train(batch)` in dreamerv3-torch = `wm._train(data)` → posterior states → `_task_behavior._train(wm, post)` imagination actor-critic). **VERIFY the exact signature in `dreamerv3-torch/dreamer.py` before running** (candidate: `Dreamer._train(self, data)`).
- Keep the 50/50 real/rendered mix: real keeps the eyes sharp (anti-forgetting on perception); rendered keeps reward+dynamics grounded and gives the actor a live reward signal.
- Seed from `maneuver_percept_ft/best.pt` (the seeing checkpoint). Save to a NEW dir `maneuver_recouple_ft/` — never touch percept_ft or the +160 best.pt.
- ~3000–6000 steps (shorter than a fresh train — the WM is already good; only the actor needs to move). Watch: `image_loss` should stay flat (eyes preserved) while `actor_loss`/`value_loss`/imagined `return` climb (hands re-coupling).

## Two variants (recommend B)
- **A — surgical (freeze WM, train actor-critic only):** fastest, isolates the recouple; risk = reward head slightly off on shifted latents. Would need a few reward-head recalibration steps first.
- **B — full co-adapt (recommended):** train WM + actor together on the mix. Minimal code change, standard Dreamer, robust; the WM keeps improving perception while the actor re-couples. The actor chases a (slowly) moving WM — normal Dreamer dynamics.

## Gates (how we know it worked)
1. **Eyes preserved:** re-run `wm_recon_diag.py` on real VQ2 frames against `maneuver_recouple_ft` → must still reconstruct gates (not regress to mush).
2. **Hands improved:** `translation_rehearsal.py` / `holdout_gate_v2.py` roundtrip return climbs vs percept_ft; then a live flight.
3. Success = flight improves *without* losing the recon. Failure modes: recon regresses (perception forgotten → up the real/rendered ratio) or return stays flat (latent shift too large → may need more steps or the surgical variant).

## Sequencing (do NOT run yet)
**Gate on Clayton's percept_ft flight.** If percept_ft flies acceptably, the decoupling was mild and the governor alone may suffice — recouple deferred. If it spins/hesitates (likely), the recouple is the fix and this is ready to launch. Measure first, then run. (Also: the color-shift finding — percept_ft looks VQ2-appearance-tuned — means the *green-gate* track may additionally want its own frames folded into the real set; orthogonal to the recouple, same pipeline.)
