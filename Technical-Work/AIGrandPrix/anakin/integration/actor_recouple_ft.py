"""
Actor-recouple fine-tune (Day 153) — teach Anakin's HANDS to use his new EYES.

perception_ft.py trained the WORLD MODEL only (wm._train), shifting the latent geometry to
see real frames while the ACTOR stayed frozen against the OLD latents ("new eyes, old hands").
This continues training from maneuver_percept_ft/best.pt but calls the FULL agent train step
(dreamer.Dreamer._train = wm._train THEN _task_behavior._train imagination actor-critic,
verified dreamer.py:117-125). The imagined actor-critic is scored by wm.heads["reward"]
(dreamer.py:122) — kept calibrated because half the batch is RENDERED rollouts with real reward.
Real frames keep perception sharp (anti-forgetting); rendered rollouts supply the reward the
actor re-couples to. No new sim data, no env-in-the-actor-loop — imagination does it.

Design: integration/ACTOR_RECOUPLE_DESIGN_2026-07-03.md.  Reuses perception_ft's data pipeline.
best.pt (+160.08) and maneuver_percept_ft are NEVER touched — saves to maneuver_recouple_ft/.

⚠ PREP — do NOT auto-run. Gate on Clayton's percept_ft flight: only run if the decoupling is
   real (spins/hesitates). Watch: image_loss FLAT (eyes preserved) while actor/value move + the
   imagined return climbs (hands re-coupling). Then gate with wm_recon_diag (eyes?) + rehearsal (hands?).

Usage:
  .venv/Scripts/python.exe integration/actor_recouple_ft.py --smoke
  .venv/Scripts/python.exe integration/actor_recouple_ft.py --steps 4000
"""
import sys, os, time, argparse
import numpy as np, torch

_HERE = os.path.dirname(os.path.abspath(__file__))
for p in [_HERE, os.path.join(_HERE, "..", "sim"),
          os.path.join(_HERE, "..", "third_party", "dreamerv3-torch")]:
    sys.path.insert(0, os.path.abspath(p))
from dreamer_pilot import DreamerPilot
# reuse the tested data pipeline verbatim
from perception_ft import load_real, collect_rendered, sample_real, sample_rendered

CKPT   = os.path.join(_HERE, "..", "third_party", "dreamerv3-torch", "logdir", "maneuver_percept_ft", "best.pt")
OUTDIR = os.path.join(_HERE, "..", "third_party", "dreamerv3-torch", "logdir", "maneuver_recouple_ft")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--seqlen", type=int, default=16)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--max-real", type=int, default=0)
    args = ap.parse_args()
    if args.smoke:
        args.steps, args.max_real = 12, 600

    pilot = DreamerPilot(CKPT)                    # seed = the SEEING checkpoint
    agent = pilot._agent
    for prm in agent.parameters():               # DreamerPilot froze the whole agent for inference;
        prm.requires_grad_(True)                 # re-enable so WM + actor + critic all train
    agent.train()

    real = [s for s in load_real(args.max_real) if len(s) >= args.seqlen]
    assert real, "no real sessions >= seqlen"
    rendered = collect_rendered(pilot, 2000 if args.smoke else 8000, pilot._config.device)
    os.makedirs(OUTDIR, exist_ok=True)
    Bh = max(1, args.batch // 2)                  # half rendered (reward-grounding), half real (perception)

    def pick(m, *keys):
        for k in keys:
            if k in m:
                v = m[k]
                return float(v) if not hasattr(v, "item") else float(v)
        return float("nan")

    t0 = time.time()
    for step in range(1, args.steps + 1):
        br = sample_rendered(rendered, Bh, args.seqlen)
        bx = sample_real(real, args.batch - Bh, args.seqlen)
        batch = {k: np.concatenate([br[k], bx[k]], 0) for k in br}
        metrics = agent._train(batch)            # FULL train: WM + imagination actor-critic
        if step % (2 if args.smoke else 50) == 0 or step == 1:
            img = pick(metrics, "image_loss")
            al  = pick(metrics, "actor_loss")
            vl  = pick(metrics, "value_loss")
            ret = pick(metrics, "imag_reward_mean", "reward_mean", "return", "imag_return_mean")
            ent = pick(metrics, "actor_entropy", "actor_ent")
            print(f"step {step:5d}/{args.steps}  image_loss={img:.3f} (eyes: flat=good)  "
                  f"actor_loss={al:.4f}  value_loss={vl:.4f}  imag_return={ret:.3f} (hands: climb=good)  "
                  f"ent={ent:.3f}  ({(time.time()-t0)/step:.2f}s/it)", flush=True)
        if step % 1000 == 0 or step == args.steps:
            path = os.path.join(OUTDIR, "best.pt")
            torch.save({"agent_state_dict": agent.state_dict()}, path)
            print(f"  saved {path}", flush=True)
    print("done. gate next: wm_recon_diag (eyes preserved?) + translation_rehearsal (hands improved?).", flush=True)

if __name__ == "__main__":
    main()
