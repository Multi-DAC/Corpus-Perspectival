#!/bin/bash
# Detached launcher for the full MVP run, per operations/WSL_PROCESS_MANAGEMENT.md.
# Invoked via `nohup setsid bash launch_run.sh & sleep 3` so the process is orphaned
# (new session/process group, TTY '?') and survives Claude/Bash-tool session cleanup.
# Source login env so torch resolves under the non-login setsid context.
[ -f /etc/profile ] && . /etc/profile
[ -f "$HOME/.profile" ] && . "$HOME/.profile"
[ -f "$HOME/.bashrc" ] && . "$HOME/.bashrc"
cd /mnt/c/Users/mercu/clawd || exit 1
exec python3 continual_coherence/run_mvp.py > continual_coherence/results/full_run.log 2>&1
