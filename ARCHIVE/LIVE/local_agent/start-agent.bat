@echo off
REM ============================================================
REM  HOME Local Agent — one-click starter
REM  Double-click this file to run the agent in a visible window.
REM  Close the window (or Ctrl+C) to stop.
REM
REM  v2 — handles both `venv` and `.venv` folder naming
REM        adds pause-on-exit so the window never closes silently
REM  Author: EVERSOUND, patched by BEACON 2026-04-20
REM ============================================================

setlocal EnableDelayedExpansion

cd /d "%~dp0"

echo.
echo ==========================================================
echo   HOME Local Agent starting
echo   Folder: %CD%
echo ==========================================================
echo.

REM --- Find the venv. Try both common names.
set "VENV_ACTIVATE="
if exist ".venv\Scripts\activate.bat" (
  set "VENV_ACTIVATE=.venv\Scripts\activate.bat"
  echo [startup] found .venv
) else if exist "venv\Scripts\activate.bat" (
  set "VENV_ACTIVATE=venv\Scripts\activate.bat"
  echo [startup] found venv
)

if "!VENV_ACTIVATE!"=="" (
  echo [ERROR] No virtual environment found.
  echo.
  echo Looked for: .venv\Scripts\activate.bat  and  venv\Scripts\activate.bat
  echo Neither exists. Open RUNBOOK.md and follow Parts 1-5.
  echo.
  pause
  exit /b 1
)

REM --- .env must exist.
if not exist ".env" (
  echo [ERROR] No .env file found in this folder.
  echo.
  echo Copy .env.example to .env and fill in your keys.
  echo See RUNBOOK.md Part 5.
  echo.
  pause
  exit /b 1
)

REM --- Activate venv.
call "!VENV_ACTIVATE!"
if errorlevel 1 (
  echo [ERROR] Could not activate the virtual environment.
  echo Check that Python was installed correctly.
  pause
  exit /b 1
)

echo [startup] virtual environment active
echo [startup] launching agent.py
echo [startup] press Ctrl+C to stop
echo ----------------------------------------------------------
echo.

python agent.py
set "EXIT_CODE=!ERRORLEVEL!"

echo.
echo ----------------------------------------------------------
if "!EXIT_CODE!"=="0" (
  echo [shutdown] agent exited cleanly
) else (
  echo [shutdown] agent exited with code !EXIT_CODE!
  echo [shutdown] scroll up to see the error
)
echo.
echo Press any key to close this window.
pause
endlocal
