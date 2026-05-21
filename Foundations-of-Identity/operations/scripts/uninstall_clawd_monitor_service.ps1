# uninstall_clawd_monitor_service.ps1 — remove the ClawdMonitorScheduler service
# REQUIREMENT: Must be run from an ELEVATED PowerShell prompt.

$ErrorActionPreference = "Stop"
$NSSM = "C:\Users\mercu\clawd\tools\nssm\nssm.exe"
$SVC  = "ClawdMonitorScheduler"

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { throw "Must run elevated." }

$existing = Get-Service $SVC -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "Service $SVC not installed. Nothing to do."
    exit 0
}

Write-Host "Stopping $SVC..."
& $NSSM stop   $SVC confirm
Start-Sleep -Seconds 2
Write-Host "Removing $SVC..."
& $NSSM remove $SVC confirm
Write-Host "Done. Verify with: Get-Service $SVC -ErrorAction SilentlyContinue"
