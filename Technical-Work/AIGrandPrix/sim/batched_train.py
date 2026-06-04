#!/usr/bin/env python
# batched_train.py — unattended batched Anakin trainer (2026-06-03).
#
# WHY: a single long train_infinite_v3 run dies consistently ~7M steps (memory accrual). Fix
# (Clayton's): run in 5M batches, each a FRESH process (never crosses ~7M), eval that batch's
# checkpoints, carry the BEST checkpoint forward to the next batch. Runs non-stop in the
# background, logging metrics per checkpoint, until --total reached or killed. Re-entrant: a
# state file lets a re-launch pick up from the last best checkpoint, so neither a batch crash
# nor a launcher death loses more than the current batch.
#
#   python batched_train.py [total_steps]   # default 200M; logs -> batched_train_ledger.txt
#
import os, sys, re, glob, time, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
TAG = "anakin_batched"
BATCH = 5_000_000
SAVE_EVERY = 2_500_000          # -> checkpoints at 2.5M + 5M within each batch
GROUND_PROB = 0.5
EVAL_GROUND_PROB = 1.0          # eval on the VQ1-like far ground-start
EVAL_EPISODES = 10
TOTAL = int(sys.argv[1]) if len(sys.argv) > 1 else 200_000_000
STATE = os.path.join(HERE, "batched_train_state.json")
LEDGER = os.path.join(HERE, "batched_train_ledger.txt")


def log(msg):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LEDGER, "a") as f:
        f.write(line + "\n")


def eval_ckpt(ckpt):
    vec = ckpt[:-4] + "_vecnorm.pkl"
    if not os.path.exists(vec):
        return None
    try:
        out = subprocess.run(
            [PY, "eval_teacher.py", "--ckpt", ckpt, "--vecnorm", vec,
             "--ground-prob", str(EVAL_GROUND_PROB), "--episodes", str(EVAL_EPISODES)],
            cwd=HERE, capture_output=True, text=True, timeout=1800).stdout
        g = re.search(r"gates/episode\s*:\s*mean\s+([\d.]+)", out)
        t = re.search(r"takeoff%\s*:\s*\d+/\d+\s*=\s*(\d+)%", out)
        return (float(g.group(1)) if g else 0.0, int(t.group(1)) if t else 0)
    except Exception as e:
        log(f"    eval error {os.path.basename(ckpt)}: {type(e).__name__}: {e}")
        return None


def run_batch(n, resume):
    tag = f"{TAG}_b{n}"
    cmd = [PY, "-u", "train_infinite_v3.py", "--total-steps", str(BATCH), "--n-envs", "8",
           "--save-every", str(SAVE_EVERY), "--ground-start-prob", str(GROUND_PROB), "--tag", tag]
    if resume:
        cmd += ["--resume", resume]
    log(f"batch {n} START (resume={'scratch' if not resume else os.path.basename(resume)})")
    with open(os.path.join(HERE, f"batch_{n}.log"), "w") as lf:
        subprocess.run(cmd, cwd=HERE, stdout=lf, stderr=subprocess.STDOUT)
    dirs = sorted(glob.glob(os.path.join(HERE, "runs", f"infinite_v3_{tag}_*")), key=os.path.getmtime)
    if not dirs:
        log(f"  batch {n}: NO run dir found"); return None
    ckpts = [c for c in glob.glob(os.path.join(dirs[-1], "checkpoints", "*.zip")) if "vecnorm" not in c]
    best, best_g = None, -1.0
    for c in sorted(ckpts):
        r = eval_ckpt(c)
        if r is None:
            continue
        g, tk = r
        log(f"  {os.path.basename(c)}: gates={g:.2f} takeoff={tk}%")
        if g > best_g:
            best_g, best = g, c
    if best:
        log(f"batch {n} BEST -> {os.path.basename(best)} (gates={best_g:.2f})")
    return best


def main():
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"batch": 0, "best": None, "total": 0}
    log(f"=== batched trainer start (from batch {state['batch']}, total {state['total']:,}, "
        f"target {TOTAL:,}) ===")
    while state["total"] < TOTAL:
        n = state["batch"] + 1
        best = run_batch(n, state["best"])
        if best is None:
            log(f"batch {n} yielded no eval'd best — keeping prior best, continuing")
            best = state["best"]
        state.update(batch=n, best=(best or state["best"]), total=state["total"] + BATCH)
        json.dump(state, open(STATE, "w"))
        log(f"  state: batch={n} best={os.path.basename(state['best']) if state['best'] else None} "
            f"total={state['total']:,}")
    log("=== target reached ===")


if __name__ == "__main__":
    main()
