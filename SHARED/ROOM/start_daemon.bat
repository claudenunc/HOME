@echo off
echo Starting HOME family daemon (with crash-recovery watchdog)...
echo.
echo This replaces family_chat.py and bot.py.
echo Sibling messages are routed via real claude CLI.
echo CLIPBOARD watcher fires instantly on new entries.
echo Watchdog: auto-restarts on crash, stops on clean exit or 5 crashes/120s.
echo.
cd /d "%~dp0"

REM Install watchdog if not present
pip show watchdog >nul 2>&1 || pip install watchdog

REM watch_daemon.py handles crash-recovery; use --once to disable restart loop
python watch_daemon.py
pause
