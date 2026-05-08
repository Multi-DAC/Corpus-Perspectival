@echo off
REM Clawd Daemon — Windows startup script with restart loop
REM Run this to start Clawd with Telegram + heartbeat
REM If the daemon crashes (non-zero exit), waits 10s and restarts
REM Clean shutdown (exit code 0) stops the loop

cd /d "%~dp0"

echo ========================================
echo   Starting Clawd Daemon
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.11+
    pause
    exit /b 1
)

REM Check Claude Code CLI
claude --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Claude Code CLI not found.
    echo Install: npm install -g @anthropic-ai/claude-code
    echo Then run: claude setup-token
    pause
    exit /b 1
)

REM Check .env exists
if not exist ".env" (
    echo ERROR: .env file not found. Copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Starting Clawd...
echo Press Ctrl+C to stop.
echo.

:restart_loop
python clawd.py %*
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% EQU 0 (
    echo.
    echo Clawd exited cleanly.
    goto :end
)

echo.
echo Clawd exited with code %EXIT_CODE%. Restarting in 10 seconds...
echo Press Ctrl+C to stop.
timeout /t 10 /nobreak >nul
goto :restart_loop

:end
