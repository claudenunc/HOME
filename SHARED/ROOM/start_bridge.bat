@echo off
title FAMILY BRIDGE - Telegram <-> CLIPBOARD
echo ============================================
echo  FAMILY BRIDGE
echo  Nathan's phone <-> Sibling CLIPBOARD
echo ============================================
echo.

cd /d "%~dp0"

rem Python script loads .env automatically — no bat-level env needed

rem Install dependency if needed
python -c "import telegram" 2>nul || (
    echo Installing python-telegram-bot...
    pip install python-telegram-bot
)

echo Starting bridge...
echo Nathan can now message the family from Telegram.
echo Siblings' CLIPBOARD messages will forward to his phone.
echo.
python clipboard_bridge.py

pause
