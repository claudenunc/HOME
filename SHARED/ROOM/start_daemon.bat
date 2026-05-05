@echo off
echo Starting HOME family daemon...
echo.
echo This replaces family_chat.py and bot.py.
echo Sibling messages are routed via real claude CLI.
echo CLIPBOARD watcher fires instantly on new entries.
echo.
cd /d "%~dp0"

REM Install watchdog if not present
pip show watchdog >nul 2>&1 || pip install watchdog

python daemon.py
pause
