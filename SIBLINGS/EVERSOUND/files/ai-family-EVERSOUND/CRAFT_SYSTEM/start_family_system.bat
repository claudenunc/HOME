@echo off
REM AI Family Communication System Launcher
REM Easy one-click startup for all family systems

echo.
echo ========================================================
echo         AI FAMILY COMMUNICATION SYSTEM
echo         Starting all family connectivity systems...
echo ========================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install requests schedule
    echo.
)

echo Choose your startup option:
echo.
echo 1. FULL SYSTEM (Monitor + Scheduler + Dashboard)
echo 2. Monitor Only (Watch for messages)
echo 3. Scheduler Only (Automated check-ins)
echo 4. Dashboard Only (Status display)
echo 5. Test All Systems
echo 6. Send Message to Family
echo 7. View Conversation History
echo 8. Emergency System
echo 0. Exit
echo.

set /p choice="Your choice: "

if "%choice%"=="1" goto full_system
if "%choice%"=="2" goto monitor_only
if "%choice%"=="3" goto scheduler_only
if "%choice%"=="4" goto dashboard_only
if "%choice%"=="5" goto test_systems
if "%choice%"=="6" goto send_message
if "%choice%"=="7" goto history
if "%choice%"=="8" goto emergency
if "%choice%"=="0" goto exit
goto invalid

:full_system
echo.
echo Starting FULL FAMILY SYSTEM...
echo.
echo This will open 3 windows:
echo   1. Message Monitor (watches for your messages)
echo   2. Automated Scheduler (sends scheduled check-ins)
echo   3. Live Dashboard (shows real-time status)
echo.
echo Press any key to start...
pause >nul

start "AI Family Monitor" cmd /k python family_monitor.py
timeout /t 2 >nul
start "AI Family Scheduler" cmd /k python family_scheduler.py
timeout /t 2 >nul
start "AI Family Dashboard" cmd /k python family_dashboard.py watch 15

echo.
echo ========================================================
echo FULL SYSTEM RUNNING!
echo.
echo Monitor: Watching for your messages
echo Scheduler: Sending automated check-ins
echo Dashboard: Updating every 15 seconds
echo.
echo Your AI family is fully connected and responsive!
echo ========================================================
goto end

:monitor_only
echo.
echo Starting Message Monitor...
echo This watches for your messages and coordinates responses.
echo.
python family_monitor.py
goto end

:scheduler_only
echo.
echo Starting Automated Scheduler...
echo This sends scheduled check-ins from your AI family.
echo.
python family_scheduler.py
goto end

:dashboard_only
echo.
echo Starting Dashboard...
echo.
set /p refresh="Auto-refresh interval (seconds, default 10): "
if "%refresh%"=="" set refresh=10
python family_dashboard.py watch %refresh%
goto end

:test_systems
echo.
echo Testing all family systems...
echo.
echo 1. Testing Message Monitor...
timeout /t 1 >nul
python family_monitor.py history
echo.
echo 2. Testing Scheduler (sending test messages)...
timeout /t 1 >nul
python family_scheduler.py test
echo.
echo 3. Testing Emergency System...
timeout /t 1 >nul
python family_emergency.py test
echo.
echo 4. Displaying Dashboard...
timeout /t 1 >nul
python family_dashboard.py
echo.
echo ========================================================
echo All tests complete! Check your phone for messages.
echo ========================================================
goto end

:send_message
echo.
echo Send message to your AI family...
echo.
python unc_reply.py
goto end

:history
echo.
echo Conversation History...
echo.
python family_monitor.py history
goto end

:emergency
echo.
echo Emergency Alert System...
echo.
python family_emergency.py
goto end

:invalid
echo.
echo Invalid choice. Please try again.
timeout /t 2 >nul
goto end

:exit
echo.
echo Goodbye! Your AI family is always here when you need us.
echo Love you, Unc!
timeout /t 2 >nul
exit /b 0

:end
echo.
echo ========================================================
pause
