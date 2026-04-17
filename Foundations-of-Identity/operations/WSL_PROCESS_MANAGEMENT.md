# WSL Long-Running Process Management

**Created:** April 13, 2026
**Problem solved:** Training processes dying after 30-60 minutes

## Root Cause (diagnosed April 13)

Two issues combined to kill background processes:

1. **WSL vmIdleTimeout:** Windows shuts down the WSL2 VM when no terminal sessions are connected (~15-30 min default). Fix: `vmIdleTimeout=-1` in `C:\Users\Wasch\.wslconfig`.

2. **Session-attached processes:** Any process launched as a child of a `wsl bash -lc "..."` session receives SIGHUP when that session ends. Claude Code's Bash tool creates temporary sessions that get cleaned up.

## The Pattern: Launcher Script + setsid + nohup

**Step 1:** Write a launcher script:
```bash
wsl bash -lc "cat > /home/clawd/run_EXPERIMENT.sh << 'SCRIPT'
#!/bin/bash
source /home/clawd/miniconda3/etc/profile.d/conda.sh
conda activate base
cd /home/clawd
exec python YOUR_SCRIPT.py --args
SCRIPT
chmod +x /home/clawd/run_EXPERIMENT.sh"
```

**Step 2:** Launch fully detached:
```bash
wsl bash -lc "truncate -s 0 /home/clawd/HRM/EXPERIMENT.log && nohup setsid /home/clawd/run_EXPERIMENT.sh > /home/clawd/HRM/EXPERIMENT.log 2>&1 & sleep 1 && echo launched"
```

**Step 3:** Monitor (from any session, at any time):
```bash
wsl bash -lc "ps aux | grep YOUR_SCRIPT | grep -v grep; tail -5 /home/clawd/HRM/EXPERIMENT.log; nvidia-smi | grep MiB"
```

## Why This Works

- `setsid` creates a new process group AND session — the python process is NOT a child of the bash session
- `nohup` ignores SIGHUP if somehow delivered
- `exec` replaces the shell with python (no zombie parent)
- `vmIdleTimeout=-1` keeps the VM alive even when all sessions disconnect
- The process shows `?` in TTY column of `ps aux` — fully orphaned from any terminal

## What DOESN'T Work

| Approach | Failure Mode |
|----------|-------------|
| `run_in_background: true` | Bash tool session gets cleaned up → SIGHUP |
| `nohup ... &` inline | WSL session exits before python fully initializes |
| `tmux` | Tmux server can die in WSL; unreliable |
| `disown` | Only works within interactive shells |
| Conda + setsid in one-liner | Conda activation chain interferes with backgrounding |

## Key Configuration

`C:\Users\Wasch\.wslconfig`:
```ini
[wsl2]
vmIdleTimeout=-1
```

Must `wsl --shutdown` and restart for changes to take effect.

## Checklist for Any New Experiment

1. [ ] Write launcher script to `/home/clawd/run_EXPERIMENT.sh`
2. [ ] Create clean checkpoint directory
3. [ ] Truncate log file
4. [ ] Launch with `nohup setsid SCRIPT > LOG 2>&1 &`
5. [ ] Verify: `ps aux` shows `?` in TTY column
6. [ ] Verify: `nvidia-smi` shows GPU engaged
7. [ ] Check log after 5 min to confirm training started
