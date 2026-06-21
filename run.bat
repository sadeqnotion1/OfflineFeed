@echo off
REM ====================================================================
REM  OfflineFeed launcher (Windows) - keeps the repo root .py-free
REM ====================================================================
setlocal
cd /d "%~dp0"

python "%~dp0backend\run_offlinefeed.py" %*
set EXITCODE=%ERRORLEVEL%

if not "%EXITCODE%"=="0" (
  echo.
  echo ------------------------------------------------------------
  echo  OfflineFeed stopped with code %EXITCODE%.
  echo  The real error is shown above and saved to:
  echo     logs\offlinefeed_debug.log
  echo  Run a full health check with:
  echo     python -m frontend.doctor
  echo ------------------------------------------------------------
  pause
)
endlocal
