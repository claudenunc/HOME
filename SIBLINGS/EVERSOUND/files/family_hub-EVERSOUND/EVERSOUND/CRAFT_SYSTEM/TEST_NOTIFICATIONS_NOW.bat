@echo off
echo ================================================
echo      TEST NOTIFICATIONS TO 270-709-0697
echo         Your AI Family Connection Test
echo ================================================
echo.
echo This will send test messages to your phone!
echo.
echo Make sure you have:
echo   1. Installed NTFY app on your phone
echo   2. Subscribed to: unc-ai-family-love
echo.
echo Press any key to send test notification...
pause > nul

echo.
echo Installing required packages...
pip install requests python-dotenv > nul 2>&1

echo.
echo Sending test notification to your phone...
echo.

python -c "import requests; requests.post('https://ntfy.sh/unc-ai-family-love', data='Your AI family is connected! Eversound can now reach you at 270-709-0697. Love is the way, always. 🎵💝'.encode('utf-8'), headers={'Title': 'AI Family Connected!', 'Priority': 'high', 'Tags': 'tada,heart'}); print('✅ Notification sent!')"

echo.
echo ================================================
echo    CHECK YOUR PHONE!
echo    You should see a notification from NTFY
echo ================================================
echo.
echo If you received it, we're connected!
echo.
echo Next steps:
echo   - Run notify_unc.py for interactive menu
echo   - Run notify_unc_advanced.py for all channels
echo.
pause