@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM =============================================================
REM VocaFlow Windows EXE builder (robust)
REM - Auto-detect launcher (py/python)
REM - Auto-create venv
REM - Auto-install required packages
REM - Build deterministic output: dist\VocaFlow.exe
REM =============================================================

cd /d "%~dp0"

set "PY_LAUNCH="
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY_LAUNCH=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY_LAUNCH=python"
  )
)

if "%PY_LAUNCH%"=="" (
  echo [ERROR] Python launcher not found. Install Python 3.10+ and re-run.
  exit /b 1
)

echo [INFO] Using launcher: %PY_LAUNCH%

if not exist ".venv" (
  echo [INFO] Creating virtual environment...
  %PY_LAUNCH% -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
  )
)

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv is broken. Delete .venv and run again.
  exit /b 1
)

set "VENV_PY=.venv\Scripts\python.exe"

echo [INFO] Upgrading pip/setuptools/wheel...
"%VENV_PY%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
  echo [ERROR] Failed to upgrade pip toolchain.
  exit /b 1
)

echo [INFO] Installing dependencies...
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] Failed to install requirements.
  echo [HINT] Check internet/proxy settings and try again.
  exit /b 1
)

if not exist "data" mkdir data
if not exist "data\words.json" (
  echo {"words":[],"meta":{"version":1},"stats":{"today_studied":0,"recent_wrong_words":[],"last_study_date":null}} > data\words.json
)

echo [INFO] Cleaning old build artifacts...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "VocaFlow.spec" del /q "VocaFlow.spec"

echo [INFO] Building EXE with PyInstaller...
"%VENV_PY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name VocaFlow ^
  --add-data "data;data" ^
  main.py

if errorlevel 1 (
  echo [ERROR] Build failed.
  exit /b 1
)

if exist "dist\VocaFlow.exe" (
  echo [OK] Build complete: dist\VocaFlow.exe
) else (
  echo [WARN] Build finished but dist\VocaFlow.exe not found.
  echo [INFO] Check dist folder manually.
)

endlocal
exit /b 0
