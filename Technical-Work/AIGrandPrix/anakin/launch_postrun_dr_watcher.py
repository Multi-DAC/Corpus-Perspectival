"""DETACHED launch of integration/postrun_dr_watcher.py — polls the dr-ft orchestrator,
then auto-runs the holdout gate + translation rehearsal and writes integration/DR_RESULTS.md.

Run: .venv/Scripts/python.exe launch_postrun_dr_watcher.py   (returns immediately)
"""
import os
import subprocess

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
WATCHER = os.path.join(ANAKIN, "integration", "postrun_dr_watcher.py")
LOG = os.path.join(ANAKIN, "third_party", "dreamerv3-torch", "logdir", "dr_watcher.log")

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    [PY, "-u", WATCHER], stdout=logf, stderr=subprocess.STDOUT, cwd=ANAKIN,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED DR watcher pid {p.pid} -> {LOG}")
