"""Anakin Phase 3 step 5 — carry-forward batch trainer (the outer loop; overnight scaling run).

Wraps the (proven, untouched) DreamerV3 inner loop. Runs training in fixed-size batches, EACH a
FRESH subprocess — that's the memory bound: the old PPO carry-forward run leaked and died ~7M steps;
a fresh process per batch resets any accrual and frees VRAM/RAM between chunks.

Carry-forward is via DreamerV3's native resume: one PERSISTENT logdir, so each batch's subprocess
loads the previous `latest.pt` (full agent: world model `_wm.*` + policy `_task_behavior.*` +
optimizers) and continues. The design intent — "carry the best WORLD MODEL forward (the expensive
physics+vision part) while the policy keeps adapting" — is served with NO dreamer.py surgery by
adding best-protection: after each batch we read the recent return; on a new best we snapshot
`best.pt`; on a real regression we restore `best.pt -> latest.pt` so a destabilized batch can't
poison the carry. (The world model is a clean `_wm.`-prefixed slice — see extract_world_model — if
we ever want strict world-model-only carry with a policy reset per curriculum stage.)

Re-entrant: a JSON state file records the batch index + best return, so a killed/rebooted run
resumes from the next batch. Stop it any time; rerun the same command to continue.

Run (overnight scaling):
  ../../.venv/Scripts/python.exe -u carry_forward_train.py \
      --logdir third_party/dreamerv3-torch/logdir/maneuver_scale \
      --envs 256 --batch-steps 1000000 --num-batches 12
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

_ANAKIN = Path(__file__).resolve().parent
_DEFAULT_DREAMER = _ANAKIN / "third_party" / "dreamerv3-torch"
_DEFAULT_PYTHON = _ANAKIN / ".venv" / "Scripts" / "python.exe"


def extract_world_model(ckpt_path):
    """Return (wm_state, wm_optim) — the `_wm.*` slice of a latest.pt. Available for strict
    world-model-only carry (the handoff gotcha: carry ONLY world-model sub-keys); v1 uses native
    full-resume + best-protection instead, so this is a utility, not on the default path."""
    import torch
    ck = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    wm_state = {k: v for k, v in ck["agent_state_dict"].items() if k.startswith("_wm.")}
    wm_optim = {k: v for k, v in ck["optims_state_dict"].items() if k.startswith("_wm.")}
    return wm_state, wm_optim


def load_state(path):
    if path.exists():
        return json.loads(path.read_text())
    return {"batch": 0, "best_return": None, "history": []}


def save_state(path, state):
    path.write_text(json.dumps(state, indent=2))


def recent_return(logdir, k):
    """Mean of the last k logged train_return values (metrics.jsonl tail = current performance)."""
    mfile = logdir / "metrics.jsonl"
    if not mfile.exists():
        return None
    returns = []
    for line in mfile.read_text().splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "train_return" in d:
            returns.append(float(d["train_return"]))
    if not returns:
        return None
    tail = returns[-k:]
    return sum(tail) / len(tail)


def run_batch(args, target_steps, logfile):
    """One fresh-process DreamerV3 batch: resume from latest.pt, train up to target_steps, exit."""
    cmd = [
        str(args.python), "-u", "dreamer.py",
        "--configs", args.config,
        "--logdir", str(Path(args.logdir).resolve()),
        "--envs", str(args.envs),
        "--steps", str(int(target_steps)),
        "--train_ratio", str(args.train_ratio),
        "--eval_every", str(int(args.eval_every)),
        "--prefill", str(int(args.prefill)),
    ]
    with open(logfile, "w") as f:
        proc = subprocess.run(cmd, cwd=str(args.dreamer_dir), stdout=f,
                              stderr=subprocess.STDOUT)
    return proc.returncode


def main():
    ap = argparse.ArgumentParser(description="Anakin Phase 3 carry-forward batch trainer")
    ap.add_argument("--logdir", required=True, help="PERSISTENT logdir (carry-forward via resume)")
    ap.add_argument("--envs", type=int, default=256, help="drone batch size (one batched GPU env)")
    ap.add_argument("--batch-steps", type=int, default=1_000_000, help="env-steps per batch")
    ap.add_argument("--num-batches", type=int, default=12)
    ap.add_argument("--train-ratio", type=int, default=512)
    ap.add_argument("--eval-every", type=int, default=20_000,
                    help="dreamer loop chunk / latest.pt save cadence (also a constant step offset)")
    ap.add_argument("--prefill", type=int, default=2500,
                    help="random-policy prefill (first batch only; must be < batch-steps)")
    ap.add_argument("--config", default="anakin_maneuver")
    ap.add_argument("--regression-thresh", type=float, default=5.0,
                    help="restore best.pt if a batch's return drops this far below best")
    ap.add_argument("--recent-k", type=int, default=20, help="metrics tail length for the return")
    ap.add_argument("--dreamer-dir", default=str(_DEFAULT_DREAMER))
    ap.add_argument("--python", default=str(_DEFAULT_PYTHON))
    ap.add_argument("--state", default=None, help="state JSON (default: <logdir>/carry_state.json)")
    args = ap.parse_args()

    logdir = Path(args.logdir).resolve()
    logdir.mkdir(parents=True, exist_ok=True)
    args.dreamer_dir = Path(args.dreamer_dir).resolve()
    state_path = Path(args.state) if args.state else logdir / "carry_state.json"
    best_pt, latest_pt = logdir / "best.pt", logdir / "latest.pt"

    state = load_state(state_path)
    print(f"[carry] logdir={logdir}  resume at batch {state['batch']}/{args.num_batches}  "
          f"best_return={state['best_return']}", flush=True)

    for b in range(state["batch"], args.num_batches):
        target = (b + 1) * args.batch_steps
        logfile = logdir / f"carry_batch_{b:03d}.log"
        print(f"[carry] batch {b}: train -> {target:,} env-steps  (log {logfile.name})", flush=True)

        rc = run_batch(args, target, logfile)
        if rc != 0:
            print(f"[carry] batch {b} FAILED (exit {rc}). See {logfile}. Stopping; rerun to resume.",
                  flush=True)
            return 1
        if not latest_pt.exists():
            print(f"[carry] batch {b}: no latest.pt written — the training loop never ran "
                  f"(is prefill {args.prefill} >= batch-steps {args.batch_steps}?). See {logfile}.",
                  flush=True)
            return 1

        ret = recent_return(logdir, args.recent_k)
        note = ""
        if ret is None:
            note = "no metrics yet"
        elif state["best_return"] is None or ret > state["best_return"]:
            shutil.copy2(latest_pt, best_pt)
            state["best_return"] = ret
            note = f"NEW BEST {ret:+.2f} -> best.pt"
        elif ret < state["best_return"] - args.regression_thresh and best_pt.exists():
            shutil.copy2(best_pt, latest_pt)
            note = f"regressed ({ret:+.2f} < best {state['best_return']:+.2f}) -> restored best.pt"
        else:
            note = f"return {ret:+.2f} (best {state['best_return']:+.2f}); kept"

        state["batch"] = b + 1
        state["history"].append({"batch": b, "target": target, "return": ret, "note": note})
        save_state(state_path, state)
        print(f"[carry] batch {b} done: {note}", flush=True)

    print(f"[carry] complete: {args.num_batches} batches, best_return={state['best_return']}",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
