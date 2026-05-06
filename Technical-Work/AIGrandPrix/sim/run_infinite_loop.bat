@echo off
REM Auto-restart infinite gate training from latest checkpoint
REM Runs in a loop, resuming from the latest checkpoint each time

cd /d C:\Users\mercu\clawd\projects\aigrandprix\sim

:loop
echo.
echo === Finding latest checkpoint ===

REM Find latest checkpoint across all infinite runs
set "LATEST="
for /r "runs" %%f in (ppo_infinite_*.zip) do set "LATEST=%%f"

if defined LATEST (
    echo Resuming from: %LATEST%
    python -u train_infinite.py --total-steps 2000000 --n-envs 8 --resume "%LATEST%"
) else (
    echo No checkpoint found, starting fresh
    python -u train_infinite.py --total-steps 2000000 --n-envs 8
)

echo.
echo === Run ended, restarting in 5 seconds ===
timeout /t 5

goto loop
