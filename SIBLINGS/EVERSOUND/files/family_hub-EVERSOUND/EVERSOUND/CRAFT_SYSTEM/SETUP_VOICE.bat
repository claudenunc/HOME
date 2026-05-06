@echo off
echo ================================================
echo         AI FAMILY VOICE SYSTEM SETUP
echo         Talk to Your AI Family!
echo ================================================
echo.

echo Installing voice requirements...
pip install pyttsx3 SpeechRecognition pyaudio keyboard

echo.
echo Testing voice system...
python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Voice system active! Your AI family can now talk to you!'); engine.runAndWait(); print('Voice test successful!')"

echo.
echo ================================================
echo      VOICE SYSTEM READY!
echo ================================================
echo.
echo To start talking to your AI family:
echo   python voice_system.py
echo.
echo Or for quick voice test:
echo   python -c "import pyttsx3; engine = pyttsx3.init(); engine.say('Hello Unc!'); engine.runAndWait()"
echo.
pause