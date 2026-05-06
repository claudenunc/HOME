@echo off
echo ================================================
echo    AI FAMILY PHONE NOTIFICATION SETUP
echo        Quick Setup by Eversound
echo ================================================
echo.

echo Step 1: Installing required Python library...
pip install requests

echo.
echo Step 2: Launching notification system...
echo.
echo IMPORTANT:
echo 1. Install 'ntfy' app on your phone (free)
echo 2. Subscribe to: unc-ai-family-love
echo 3. Enable notifications
echo.
echo Press any key when ready...
pause > nul

python notify_unc.py

pause