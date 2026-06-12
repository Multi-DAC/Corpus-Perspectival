"""DETACHED launch: overnight gate watcher (see integration/postrun_gate_watcher.py).

Waits for the restyle fine-tune to print "[carry] complete:", then runs
holdout_gate.py + translation_rehearsal.py and writes integration/OVERNIGHT_RESULTS.md.

Run: .venv/Scripts/python.exe launch_postrun_watcher.py   (returns immediately)
"""
import os
import subprocess

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
LOG = os.path.join(ANAKIN, "integration", "postrun_watcher.log")

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    [PY, "-u", os.path.join(ANAKIN, "integration", "postrun_gate_watcher.py")],
    stdout=logf, stderr=subprocess.STDOUT, cwd=ANAKIN,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED postrun watcher pid {p.pid} -> {LOG}")
