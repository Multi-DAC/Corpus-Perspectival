# install_clawd_monitor_service.ps1 — install monitor-scheduler as Windows Service
#
# REQUIREMENT: Must be run from an ELEVATED PowerShell prompt.
# (Right-click PowerShell → Run as Administrator)
#
# What this does:
# - Installs the Clawd monitor scheduler (M1-M8 + ledger backup + weekly
#   self-test) as a Windows Service named "ClawdMonitorScheduler".
# - Uses NSSM (Non-Sucking Service Manager) at C:\Users\mercu\clawd\tools\nssm\nssm.exe
# - Runs as LocalSystem (no user password needed; the scheduler + monitors
#   only do file I/O + sqlite + HTTP, no WSL/GPU/profile state).
# - Auto-starts at boot.
# - Restarts automatically on crash (15s delay).
# - Logs stdout/stderr to C:\Users\mercu\clawd\memory\supervisor\ with
#   auto-rotation at 10MB.
# - SCM (Service Control Manager) Recovery actions catch NSSM itself.
#
# What this does NOT do:
# - Install the main Clawd daemon as a service. That decision is deferred
#   pending pairing on credentials (WSL/GPU/profile needs Clayton's user
#   account; needs explicit password). See SUPERVISOR_INSTALL.md.
#
# Verify after install:
#   sc query ClawdMonitorScheduler
#   Get-Service ClawdMonitorScheduler
#   Get-Content C:\Users\mercu\clawd\memory\supervisor\stdout.log -Tail 20
#
# Uninstall:
#   .\uninstall_clawd_monitor_service.ps1
#   (or manually: C:\Users\mercu\clawd\tools\nssm\nssm.exe remove ClawdMonitorScheduler confirm)

$ErrorActionPreference = "Stop"

$NSSM     = "C:\Users\mercu\clawd\tools\nssm\nssm.exe"
$SVC      = "ClawdMonitorScheduler"
$PYTHON   = "C:\Python314\python.exe"
$SCRIPT   = "C:\Users\mercu\clawd\operations\monitors\scheduler.py"
$CWD      = "C:\Users\mercu\clawd"
$LOG_DIR  = "C:\Users\mercu\clawd\memory\supervisor"
$STDOUT   = "$LOG_DIR\monitor_scheduler_stdout.log"
$STDERR   = "$LOG_DIR\monitor_scheduler_stderr.log"

# Sanity checks
if (-not (Test-Path $NSSM))   { throw "NSSM not found at $NSSM. Run download step first." }
if (-not (Test-Path $PYTHON)) { throw "Python not found at $PYTHON. Adjust script." }
if (-not (Test-Path $SCRIPT)) { throw "Monitor scheduler not found at $SCRIPT." }
if (-not (Test-Path $LOG_DIR)) { New-Item -ItemType Directory -Path $LOG_DIR -Force | Out-Null }

# Must be admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    throw "This script must be run from an elevated PowerShell. Right-click PowerShell -> Run as Administrator."
}

# If service already exists, remove first (idempotent reinstall)
$existing = Get-Service $SVC -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Service $SVC exists; stopping + removing for clean reinstall..."
    & $NSSM stop   $SVC confirm
    & $NSSM remove $SVC confirm
    Start-Sleep -Seconds 2
}

Write-Host "Installing $SVC via NSSM..."
& $NSSM install $SVC $PYTHON $SCRIPT
& $NSSM set $SVC AppDirectory      $CWD
& $NSSM set $SVC AppStdout         $STDOUT
& $NSSM set $SVC AppStderr         $STDERR
& $NSSM set $SVC AppRotateFiles    1
& $NSSM set $SVC AppRotateBytes    10485760    # 10 MB
& $NSSM set $SVC AppExit Default   Restart
& $NSSM set $SVC AppRestartDelay   15000       # 15s -- prevents crash-loop CPU burn
& $NSSM set $SVC AppThrottle       10000       # don't mark restart-failed if app survives >10s
& $NSSM set $SVC Start             SERVICE_AUTO_START
& $NSSM set $SVC Description       "Clawd monitor scheduler -- runs M1-M8, ledger backup, weekly self-test."

# SCM-level recovery: catches NSSM itself if NSSM dies
& sc.exe failure $SVC reset= 86400 actions= restart/60000/restart/60000/restart/60000

Write-Host "Starting $SVC..."
& $NSSM start $SVC

Start-Sleep -Seconds 3
$state = (Get-Service $SVC).Status
Write-Host ""
Write-Host "=== Install complete ==="
Write-Host "Service: $SVC"
Write-Host "State:   $state"
Write-Host "Logs:    $STDOUT"
Write-Host "         $STDERR"
Write-Host ""
Write-Host "Verify next boot survives by rebooting; service should be running."
