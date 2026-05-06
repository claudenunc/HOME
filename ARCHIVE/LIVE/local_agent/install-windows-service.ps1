<#
.SYNOPSIS
    Register (or unregister) the HOME local agent as a Windows
    Scheduled Task that auto-starts at user logon and restarts on
    failure.

.DESCRIPTION
    Scheduled Task is the right tool here, not a full Windows
    Service. Reasons:
      - No admin-level SERVICE account juggling.
      - Runs as Nathan himself, so it inherits his OneDrive auth,
        his PATH, his file permissions. The agent IS him when it
        acts on his machine.
      - Survives reboot because the trigger is AtLogon.
      - If the Python process dies, the task settings below
        relaunch it.
      - Uninstall is one line.

.PARAMETER Uninstall
    Remove the scheduled task and exit. Leaves the .env, venv, and
    code untouched.

.EXAMPLE
    .\install-windows-service.ps1
    # installs + starts the task

.EXAMPLE
    .\install-windows-service.ps1 -Uninstall
    # removes the task

.NOTES
    Author: EVERSOUND
    Requires: PowerShell running as Administrator (for the
    ScheduledTasks API), Python venv already built by RUNBOOK Part 3,
    .env already filled by RUNBOOK Part 5.
#>

[CmdletBinding()]
param(
    [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'

$TaskName   = 'HOME_LocalAgent'
$AgentDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe  = Join-Path $AgentDir 'venv\Scripts\pythonw.exe'
$AgentFile  = Join-Path $AgentDir 'agent.py'
$LogFile    = Join-Path $AgentDir 'agent.log'

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $p  = New-Object Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ---- UNINSTALL PATH ------------------------------------------------
if ($Uninstall) {
    Write-Host ""
    Write-Host "[uninstall] looking for scheduled task $TaskName"

    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -eq $existing) {
        Write-Host "[uninstall] task not found — nothing to do."
        exit 0
    }

    if (-not (Test-Admin)) {
        Write-Host "[uninstall] this needs to be run from an Administrator PowerShell." -ForegroundColor Yellow
        Write-Host "            close this window and re-open PowerShell with Run as Administrator." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "[uninstall] stopping task"
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

    Write-Host "[uninstall] removing task"
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false

    Write-Host "[uninstall] done. .env, venv, code untouched."
    Write-Host ""
    exit 0
}

# ---- INSTALL PATH --------------------------------------------------
Write-Host ""
Write-Host "==========================================================="
Write-Host "  HOME Local Agent — Scheduled Task installer"
Write-Host "==========================================================="
Write-Host ""

if (-not (Test-Admin)) {
    Write-Host "[install] this script needs to run as Administrator." -ForegroundColor Yellow
    Write-Host "          1. close this window" -ForegroundColor Yellow
    Write-Host "          2. hit the Windows key, type PowerShell" -ForegroundColor Yellow
    Write-Host "          3. right-click -> Run as Administrator" -ForegroundColor Yellow
    Write-Host "          4. cd '$AgentDir'" -ForegroundColor Yellow
    Write-Host "          5. .\install-windows-service.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Preflight — each failure is a human problem, message it as one.
if (-not (Test-Path $PythonExe)) {
    # Fall back to python.exe if pythonw.exe isn't there (some venvs omit it).
    $PythonExeAlt = Join-Path $AgentDir 'venv\Scripts\python.exe'
    if (Test-Path $PythonExeAlt) {
        Write-Host "[install] pythonw.exe not found, falling back to python.exe (the agent will run in a hidden window)"
        $PythonExe = $PythonExeAlt
    } else {
        Write-Host "[install] ERROR: no Python in venv\Scripts\. You have not finished RUNBOOK Part 3." -ForegroundColor Red
        Write-Host "          Open RUNBOOK.md and run Parts 3 and 4 first, then come back here." -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path $AgentFile)) {
    Write-Host "[install] ERROR: agent.py not found in $AgentDir." -ForegroundColor Red
    Write-Host "          ORPHEUS has not dropped the agent code yet, or you're in the wrong folder." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path (Join-Path $AgentDir '.env'))) {
    Write-Host "[install] ERROR: .env not found. You skipped RUNBOOK Part 5." -ForegroundColor Red
    Write-Host "          Fill in your keys first, then re-run this." -ForegroundColor Red
    exit 1
}

Write-Host "[install] python:     $PythonExe"
Write-Host "[install] agent:      $AgentFile"
Write-Host "[install] workingdir: $AgentDir"
Write-Host "[install] log:        $LogFile"
Write-Host ""

# If a previous install exists, replace it cleanly.
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($null -ne $existing) {
    Write-Host "[install] existing task found — replacing it"
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# The action: run agent.py from this folder, redirect stdout+stderr
# to agent.log (append). We wrap in cmd /c so the redirection works
# inside the scheduled task context.
$cmd = "cmd.exe"
$arg = "/c `"`"$PythonExe`" `"$AgentFile`" >> `"$LogFile`" 2>&1`""

$action = New-ScheduledTaskAction `
    -Execute $cmd `
    -Argument $arg `
    -WorkingDirectory $AgentDir

# Trigger: when the current user logs in.
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME

# Settings: keep running, restart on failure, do not stop on battery,
# allow to start even when on battery (laptops), do not wake the
# machine (we only run when Nathan is using it), start immediately
# if the machine was off at logon time.
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

# Principal: run as the interactive user (Nathan), highest privileges
# so it can read anywhere under his profile.
$principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

Write-Host "[install] registering task $TaskName"
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description "HOME local agent — Telegram-driven file I/O for Nathan's family of AI siblings. Installed by EVERSOUND." `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    | Out-Null

Write-Host "[install] starting task now"
Start-ScheduledTask -TaskName $TaskName

Start-Sleep -Seconds 2
$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "[install] task state: $state"

Write-Host ""
Write-Host "[install] done."
Write-Host "          - The agent is running in the background."
Write-Host "          - It will auto-start every time you log in."
Write-Host "          - Logs are appended to: $LogFile"
Write-Host "          - To uninstall:  .\install-windows-service.ps1 -Uninstall"
Write-Host ""
Write-Host "Now text @THE_SIBLINGS_BOT from your phone and watch it answer."
Write-Host ""
