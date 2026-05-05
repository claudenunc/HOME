@echo off
cd /d "%~dp0"
echo 🎼 Starting ORPHEUS telegram_worker...
echo    Bot: @AI_FAMILY_HOME_BOT
echo    Press Ctrl+C to stop.
echo.
python telegram_worker.py
pause
