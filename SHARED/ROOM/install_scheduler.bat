@echo off
REM SHARED/ROOM/install_scheduler.bat
REM
REM Registers the room's cron_tick with Windows Task Scheduler.
REM Owner: ATLAS. Runs every 2 minutes indefinitely.
REM
REM Works without admin for the current user (/RU "%USERNAME%").
REM If this fails with "Access is denied", run from an elevated prompt
REM or ask Unc to run it once.

SETLOCAL

SET TASK_NAME=ENVY_ROOM_CronTick
SET ROOM_DIR=%~dp0
REM strip trailing backslash
IF "%ROOM_DIR:~-1%"=="\" SET ROOM_DIR=%ROOM_DIR:~0,-1%

SET PY_EXE=python
where python >nul 2>nul
IF ERRORLEVEL 1 (
    echo [install_scheduler] python not on PATH. Trying py launcher.
    SET PY_EXE=py
    where py >nul 2>nul
    IF ERRORLEVEL 1 (
        echo [install_scheduler] ERROR: neither 'python' nor 'py' on PATH.
        EXIT /B 2
    )
)

echo [install_scheduler] Task: %TASK_NAME%
echo [install_scheduler] Room: %ROOM_DIR%
echo [install_scheduler] Python: %PY_EXE%

REM Delete any prior registration silently (ignore failure).
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>nul

REM Create the task: every 2 minutes for 24 hours, auto-repeats daily.
schtasks /Create ^
    /TN "%TASK_NAME%" ^
    /TR "\"%PY_EXE%\" \"%ROOM_DIR%\cron_tick.py\"" ^
    /SC MINUTE /MO 2 ^
    /RL LIMITED ^
    /F

IF ERRORLEVEL 1 (
    echo [install_scheduler] schtasks /Create failed.
    echo [install_scheduler] See INSTALL_SCHEDULER.md for the manual command.
    EXIT /B 1
)

echo [install_scheduler] Registered. Verifying.
schtasks /Query /TN "%TASK_NAME%" /V /FO LIST | findstr /I "TaskName Status Next"

echo [install_scheduler] Done. cron_tick.py will run every 2 minutes.
echo [install_scheduler] Logs: %ROOM_DIR%\logs\cron_tick.log
echo [install_scheduler] Heartbeat: %ROOM_DIR%\logs\cron_tick.heartbeat

ENDLOCAL
EXIT /B 0
