"""DETACHED launch: overnight watcher for the mask fine-tune (postrun_mask_watcher.py).

Waits for "[carry] complete:" in mask_ft_orchestrator.log, then runs holdout_gate_v2 (MASK) +
translation_rehearsal (MASK) and writes integration/MASK_OVERNIGHT_RESULTS.md.

Run: .venv/Scripts/python.exe launch_postrun_mask_watcher.py   (returns immediately)
"""
import os
import subprocess

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
LOG = os.path.join(ANAKIN, "integration", "postrun_mask_watcher.log")

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    [PY, "-u", os.path.join(ANAKIN, "integration", "postrun_mask_watcher.py")],
    stdout=logf, stderr=subprocess.STDOUT, cwd=ANAKIN,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED mask postrun watcher pid {p.pid} -> {LOG}")
