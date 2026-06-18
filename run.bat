@echo off
REM ====================================================================
REM  OfflineFeed launcher (Windows)
REM  Replaces the old wrapper that hid the real error behind
REM  "[WARNING] The Feed Server exited with an error - Code: 1".
REM ====================================================================
setlocal
cd /d "%~dp0"

REM Prefer the Python launcher, fall back to python on PATH.
where py >nul 2>nul && (set PY=py) || (set PY=python)

%PY% run_offlinefeed.py %*
set EXITCODE=%ERRORLEVEL%

if not "%EXITCODE%"=="0" (
  echo.
  echo ------------------------------------------------------------
  echo  OfflineFeed stopped with code %EXITCODE%.
  echo  The real error is shown above and saved to:
  echo     logs\offlinefeed_debug.log
  echo  Run a full health check with:
  echo     %PY% -m frontend.doctor
  echo ------------------------------------------------------------
  pause
)
endlocal
