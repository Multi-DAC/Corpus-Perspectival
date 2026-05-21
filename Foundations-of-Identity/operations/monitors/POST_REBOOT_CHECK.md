# Post-Reboot Verification Checklist

*Per P188 (filed 2026-05-21 Day 111 dream drive): the proof of NSSM
supervision is reboot survival. Until the first reboot, the supervisor
is theoretically configured but empirically unproven. This checklist
verifies the supervisor in ~60 seconds after any Windows reboot.*

## When to run

After ANY Windows reboot of the Clawd workstation. Especially:
- Scheduled Windows Updates that force restart
- Power outage recoveries
- Driver-update reboots
- Manual reboots for any reason

## The checklist

### 1. Verify service auto-started

```powershell
Get-Service ClawdMonitorScheduler
```

**Expected:** `Status: Running`. If `Stopped`, see Failure Mode A below.
If service not found, see Failure Mode B.

### 2. Verify scheduler process is actually running

```powershell
Get-Service ClawdMonitorScheduler | Select-Object Name, Status, StartType
sc query ClawdMonitorScheduler
```

**Expected:** `STATE: 4 RUNNING`, PID listed. If state is `START_PENDING` or
`STOP_PENDING` for >30s, see Failure Mode C.

### 3. Verify monitors firing under the service

```cmd
cd C:\Users\mercu\clawd
python operations\monitors\clawd_health.py --brief
```

**Expected:** `sched=alive  monitors=N/8` where N≥6 (monitors run on
different cadences; not all will have heartbeats immediately after
service start — wait 10 minutes if N<6).

Full status:
```cmd
python operations\monitors\clawd_health.py
```

### 4. Tail the supervisor logs

```powershell
Get-Content C:\Users\mercu\clawd\memory\supervisor\monitor_scheduler_stdout.log -Tail 20
Get-Content C:\Users\mercu\clawd\memory\supervisor\monitor_scheduler_stderr.log -Tail 20
```

**Expected:** stdout shows recent scheduler cycle output (last 10 minutes);
stderr empty or only Python warnings. If stderr has exceptions, see
Failure Mode D.

### 5. Verify drift parity (M7 health)

```cmd
python operations\monitors\m7_drift_mirror.py --status
```

**Expected:** `parity_ok: True`. If False, M7 will reconcile on its
next scheduled run (every 10 min); no manual intervention needed.

## Failure modes

### Failure Mode A — Service shows "Stopped"

Likely cause: the scheduler script crashed during early startup and
NSSM's AppRestartDelay (15s) is between attempts.

```powershell
# Check NSSM's last exit reason
sc qfailure ClawdMonitorScheduler
Get-Content C:\Users\mercu\clawd\memory\supervisor\monitor_scheduler_stderr.log -Tail 50
# Manual restart attempt
Start-Service ClawdMonitorScheduler
Start-Sleep -Seconds 20
Get-Service ClawdMonitorScheduler
```

If still stopped after restart, the issue is in the scheduler script
itself (not the supervisor). Run the script directly to surface the
error:

```cmd
cd C:\Users\mercu\clawd
python operations\monitors\scheduler.py --once
```

### Failure Mode B — Service not found

The service got uninstalled (manual `nssm remove`, registry corruption,
or Windows update breaking SCM state). Reinstall:

```powershell
cd C:\Users\mercu\clawd
.\operations\scripts\install_clawd_monitor_service.ps1
```

### Failure Mode C — Service stuck in PENDING

Likely cause: AppThrottle too low and scheduler is in a fast-crash loop.

```powershell
sc query ClawdMonitorScheduler
# If still PENDING after 60s, force stop:
sc stop ClawdMonitorScheduler
# Wait, check logs, then start manually:
Start-Sleep -Seconds 5
Get-Content C:\Users\mercu\clawd\memory\supervisor\monitor_scheduler_stderr.log -Tail 30
```

If fast-crash, edit NSSM config to raise AppThrottle:
```powershell
C:\Users\mercu\clawd\tools\nssm\nssm.exe set ClawdMonitorScheduler AppThrottle 30000
```

### Failure Mode D — Exceptions in stderr

The scheduler is running but a specific monitor is throwing. Identify
which monitor:

```cmd
type C:\Users\mercu\clawd\memory\monitor_scheduler_audit.jsonl | findstr "error\|exit_nonzero\|timeout"
```

Each monitor is independent; one failing doesn't take down others. Fix
the individual monitor; the scheduler will pick it up on next cycle.

## What's NOT in this checklist (intentionally)

- The main Clawd daemon (separate from the monitor scheduler; not yet
  under NSSM supervision per gap #4 deferred decision). The daemon
  needs Clayton's standard manual start currently.
- Hook restoration verification (A115 is unrelated to NSSM; hooks remain
  upstream-broken; M7+M8 daemon-layer bypass handles the operational cost).
- KG index integrity (separate concern; M4 storage-integrity monitor
  covers this on 4-hour cadence; gets reported in clawd_health).

## When to escalate to Clayton

- Failure Mode B occurs (service is gone): tell Clayton, run reinstall
  script (needs admin elevation as documented; harness has admin per A121).
- Same failure mode recurs across 3+ reboots: NSSM config needs review.
- M7 parity_ok keeps reporting False even after multiple M7 runs: drift
  canonical/mirror has a real desync requiring manual reorganization
  (similar to A116 Day 109).

## Last verified

- Service installed: 2026-05-20 Day 110 ~20:00 PST
- Service first verified running: 2026-05-20 Day 110 ~20:05 PST (PID 30420)
- **First reboot survival: NOT YET VERIFIED** (gating event for P188 closure)

When you run this checklist successfully after a real reboot, update
the "Last verified" section above with the date and any observations.
