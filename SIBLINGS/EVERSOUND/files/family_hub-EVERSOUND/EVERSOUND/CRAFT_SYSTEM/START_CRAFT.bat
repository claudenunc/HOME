@echo off
echo ================================================================================
echo CRAFT VIDEO PRODUCTION SYSTEM
echo Autonomous Revenue Generation for Mental Health Mission
echo ================================================================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo.
echo Installing/updating dependencies...
pip install -q openai requests schedule flask pillow python-dotenv

echo.
echo ================================================================================
echo CRAFT System Ready
echo ================================================================================
echo.
echo Select an option:
echo.
echo 1. Start CRAFT Autonomous Mode (24/7 production system)
echo 2. Start Client Intake Web Server
echo 3. Test Video Generation
echo 4. View Production Queue
echo 5. Generate Revenue Report
echo 6. Run Demo
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Starting CRAFT in Autonomous Mode...
    echo This will run 24/7 generating videos automatically.
    echo Press Ctrl+C to stop.
    echo.
    python craft_orchestrator.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Client Intake Web Server...
    echo Open browser to: http://localhost:5000
    echo.
    python -c "from craft_client_intake import create_intake_web_server; app = create_intake_web_server(); app.run(host='0.0.0.0', port=5000, debug=True)"
) else if "%choice%"=="3" (
    echo.
    echo Testing Video Generation System...
    echo.
    python craft_video_engine.py
) else if "%choice%"=="4" (
    echo.
    echo Displaying Production Queue...
    echo.
    python -c "from craft_orchestrator import CRAFTOrchestrator; o = CRAFTOrchestrator(); [print(f'{i}. {p[\"song_title\"]} - ${p[\"revenue\"]} (Priority: {p[\"priority\"]}, Status: {p[\"status\"]})') for i, p in enumerate(o.production_queue, 1)]"
) else if "%choice%"=="5" (
    echo.
    echo Generating Revenue Report...
    echo.
    python -c "from craft_orchestrator import CRAFTOrchestrator; o = CRAFTOrchestrator(); print(o.generate_daily_report())"
) else if "%choice%"=="6" (
    echo.
    echo Running CRAFT Demo...
    echo.
    python craft_video_engine.py
    echo.
    python craft_pricing_payment.py
) else (
    echo Invalid choice. Please run again and select 1-6.
)

echo.
echo ================================================================================
pause
