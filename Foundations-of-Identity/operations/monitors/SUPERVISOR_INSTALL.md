# Supervisor Install — gap #4 (daemon supervision)

This documents the NSSM-as-Windows-Service supervisor for the Clawd
monitoring infrastructure, per Substrate Extension Plan gap #4.

## Architecture

Two distinct supervised processes are possible:

1. **Clawd Monitor Scheduler** (M1-M8 + ledger backup + weekly self-test)
   — **READY TO INSTALL.** This is what `install_clawd_monitor_service.ps1`
   sets up. Runs as `LocalSystem` because none of the monitors need user-
   profile state (file I/O + sqlite + HTTP only). No password required.

2. **Clawd Main Daemon** (heartbeat, creative drives, conversation handling,
   30 tools incl. WSL/GPU) — **DEFERRED, needs Clayton input.** This one
   requires the user account `.\mercu` (NOT LocalSystem) because of WSL
   distros, GPU/CUDA state, voice tools, browser sessions. Service-context
   install needs the user password baked in OR Task Scheduler with an
   InteractiveToken trigger. We should pair on this when Clayton is at
   the machine.

## Bedrock layer

Windows Service Control Manager (SCM) is the trust root. NSSM runs as a
service under SCM; SCM's per-service Recovery actions restart NSSM if NSSM
itself crashes. That's what catches "supervisor of the supervisor."

## To install the monitor-scheduler service

1. Open PowerShell as Administrator (right-click → Run as Administrator).
2. Run:
   ```powershell
   cd C:\Users\mercu\clawd
   .\operations\scripts\install_clawd_monitor_service.ps1
   ```
3. Verify:
   ```powershell
   Get-Service ClawdMonitorScheduler
   # State should be: Running
   ```
4. Watch first cycle:
   ```powershell
   Get-Content C:\Users\mercu\clawd\memory\supervisor\monitor_scheduler_stdout.log -Wait -Tail 20
   ```

The service will:
- Auto-start at every Windows boot.
- Restart automatically on crash (15s delay).
- Log stdout/stderr to `memory/supervisor/` with 10MB rotation.
- Be caught by SCM Recovery if NSSM itself dies.

## To uninstall

```powershell
.\operations\scripts\uninstall_clawd_monitor_service.ps1
```

## What this closes / doesn't close

- **Closes:** "if the monitor scheduler dies, nothing restarts it" — the
  scheduler is what runs M1-M8 + ledger backup + self-test. Without
  supervision, a crashed scheduler means all monitoring silently stops.
- **Doesn't close:** main Clawd daemon supervision. The daemon has
  internal `self_control.restart_daemon`, but if the daemon and its
  respawner both crash, there's still no external recovery. That's the
  pair-with-Clayton task.

## Failure modes to know

- **`AppThrottle` (default 1500ms) suppresses restart if app exits too
  fast at startup.** Raised to 10s in our config. If early-boot crashes
  get marked as paused, raise further.
- **LocalSystem can't access user-profile state.** Fine for the monitor
  scheduler; would break the main daemon (hence the deferral).
- **Service-context Python won't inherit interactive PATH.** If the
  scheduler needs additional env vars, set them via `nssm set <SVC>
  AppEnvironmentExtra "VAR=value"`.

## Files

- `operations/scripts/install_clawd_monitor_service.ps1` — installer
- `operations/scripts/uninstall_clawd_monitor_service.ps1` — uninstaller
- `tools/nssm/nssm.exe` — NSSM 2.24 binary (one-time downloaded from
  https://nssm.cc/release/nssm-2.24.zip, sha256 verified at zip-time)
