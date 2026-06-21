@echo off
REM ===== OfflineFeed Path B - launch the twscrape control panel (GUI) =====
setlocal
cd /d "%~dp0"

set PYTHON_CMD=python

py -3.12 -V >nul 2>&1
if not errorlevel 1 (
  set PYTHON_CMD=py -3.12
  goto :python_found
)

py -3.11 -V >nul 2>&1
if not errorlevel 1 (
  set PYTHON_CMD=py -3.11
  goto :python_found
)

py -3.10 -V >nul 2>&1
if not errorlevel 1 (
  set PYTHON_CMD=py -3.10
  goto :python_found
)

python -V >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python is required, but was not found.
  echo Install Python 3.10+ from https://www.python.org/downloads/
  pause
  exit /b 1
)

for /f "tokens=2" %%v in ('python -V 2^>^&1') do (
  for /f "delims=. tokens=1,2" %%a in ("%%v") do (
    if %%a geq 3 (
      if %%b geq 10 (
        goto :python_found
      )
    )
    echo [ERROR] Current Python is %%a.%%b. twscrape requires Python 3.10+.
    echo Please install Python 3.10+ or run with py launcher.
    pause
    exit /b 1
  )
)

:python_found
echo Using Python command: %PYTHON_CMD%

echo Installing/updating twscrape (first run only may take a minute)...
%PYTHON_CMD% -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Could not install requirements. See messages above.
  pause
  exit /b 1
)

echo Launching the control panel...
%PYTHON_CMD% twscrape_gui.py
if errorlevel 1 pause
endlocal
