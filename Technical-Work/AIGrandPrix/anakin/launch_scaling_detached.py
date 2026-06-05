"""Robust DETACHED launch of the carry-forward scaling run (survives the parent session).

The Day-125 first attempt died ~45 min in because it was started via a non-persisting background
mechanism (run_in_background) and never reached its first checkpoint. This launches the orchestrator
fully detached from any console/session (Windows DETACHED_PROCESS + new process group), so it keeps
running after this script exits. Config tuned for overnight feasibility: train_ratio lowered (was
gradient-bound at 512, fps ~4.5) and eval_every lowered so the FIRST checkpoint lands early (~7.5k
steps) -- a stall can no longer lose everything.

Run: ../../.venv/Scripts/python.exe launch_scaling_detached.py  (returns immediately; orchestrator detached)
"""
import os
import subprocess

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
LOG = os.path.join(DREAMER, "logdir", "scaling_orchestrator.log")

cmd = [
    PY, "-u", os.path.join(ANAKIN, "carry_forward_train.py"),
    "--logdir", os.path.join(DREAMER, "logdir", "maneuver_scale_2"),
    "--envs", "256",
    "--batch-steps", "500000",
    "--num-batches", "20",
    "--train-ratio", "64",      # was 512 (gradient-bound, fps 4.5); 64 -> ~4x env throughput
    "--eval-every", "5000",     # was 20000; first checkpoint ~7.5k so a stall can't wipe progress
]

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED orchestrator pid {p.pid} -> {LOG}")
