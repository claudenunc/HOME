@echo off
echo ================================================
echo      AI FAMILY VOICE CHAT - WEB VERSION
echo         Access from your phone browser!
echo ================================================
echo.
echo Starting web server...
echo.
echo After server starts:
echo   1. On your PHONE browser, go to:
echo      http://[YOUR-COMPUTER-IP]:8000/voice_web_app.html
echo.
echo   To find your computer IP:
echo   - Type 'ipconfig' in another terminal
echo   - Look for IPv4 Address
echo   - Usually starts with 192.168...
echo.
echo   Example: http://192.168.1.100:8000/voice_web_app.html
echo.
echo ================================================
echo.
python -m http.server 8000