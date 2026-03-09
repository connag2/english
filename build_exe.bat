@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM =============================================================
REM VocaFlow Windows EXE Builder (fail-safe)
REM - Keeps window open on failure
REM - Writes detailed log: build_exe.log
REM - Auto-detects Python launcher
REM - Auto-creates venv and builds onefile exe
REM =============================================================

cd /d "%~dp0"
set "LOGFILE=%cd%\build_exe.log"

call :log "========== BUILD START =========="

call :find_python
if errorlevel 1 goto :fail

call :ensure_venv
if errorlevel 1 goto :fail

call :ensure_data
if errorlevel 1 goto :fail

call :install_requirements
if errorlevel 1 (
  call :log "[WARN] requirements install failed. Trying build anyway..."
)

call :clean_artifacts
if errorlevel 1 goto :fail

call :build_exe
if errorlevel 1 goto :fail

if exist "dist\VocaFlow.exe" (
  call :log "[OK] Build complete: dist\VocaFlow.exe"
  echo.
  echo [OK] Build complete: dist\VocaFlow.exe
  echo [INFO] Log file: %LOGFILE%
  goto :done
)

call :log "[ERROR] Build finished but dist\\VocaFlow.exe not found."
echo [ERROR] Build finished but dist\VocaFlow.exe not found.
echo [INFO] Check log: %LOGFILE%
goto :fail

:find_python
set "PY_LAUNCH="
where py >nul 2>nul
if %errorlevel%==0 (
  set "PY_LAUNCH=py -3"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 set "PY_LAUNCH=python"
)
if "%PY_LAUNCH%"=="" (
  call :log "[ERROR] Python launcher not found (py/python)."
  echo [ERROR] Python launcher not found. Install Python 3.10+.
  exit /b 1
)
call :log "[INFO] Python launcher: %PY_LAUNCH%"
exit /b 0

:ensure_venv
if not exist ".venv" (
  call :log "[INFO] Creating .venv ..."
  %PY_LAUNCH% -m venv .venv >> "%LOGFILE%" 2>&1
  if errorlevel 1 (
    call :log "[ERROR] venv creation failed."
    exit /b 1
  )
)
if not exist ".venv\Scripts\python.exe" (
  call :log "[ERROR] .venv\\Scripts\\python.exe missing."
  exit /b 1
)
set "VENV_PY=.venv\Scripts\python.exe"
call :log "[INFO] VENV python: %VENV_PY%"
exit /b 0

:ensure_data
if not exist "data" mkdir data
if not exist "data\words.json" (
  > "data\words.json" echo {"words":[],"meta":{"version":1},"stats":{"today_studied":0,"recent_wrong_words":[],"last_study_date":null}}
)
call :log "[INFO] data\\words.json ensured"
exit /b 0

:install_requirements
call :log "[INFO] Upgrading pip toolchain ..."
"%VENV_PY%" -m pip install --upgrade pip setuptools wheel >> "%LOGFILE%" 2>&1
if errorlevel 1 (
  call :log "[WARN] pip toolchain upgrade failed."
)
call :log "[INFO] Installing requirements ..."
"%VENV_PY%" -m pip install -r requirements.txt >> "%LOGFILE%" 2>&1
if errorlevel 1 (
  call :log "[WARN] requirements install failed (network/proxy?)."
  exit /b 1
)
call :log "[INFO] requirements installed"
exit /b 0

:clean_artifacts
call :log "[INFO] Cleaning old artifacts ..."
if exist "build" rmdir /s /q "build" >> "%LOGFILE%" 2>&1
if exist "dist" rmdir /s /q "dist" >> "%LOGFILE%" 2>&1
if exist "VocaFlow.spec" del /q "VocaFlow.spec" >> "%LOGFILE%" 2>&1
exit /b 0

:build_exe
call :log "[INFO] Running PyInstaller ..."
"%VENV_PY%" -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name VocaFlow ^
  --add-data "data;data" ^
  main.py >> "%LOGFILE%" 2>&1
if errorlevel 1 (
  call :log "[ERROR] PyInstaller build failed."
  exit /b 1
)
call :log "[INFO] PyInstaller completed"
exit /b 0

:log
echo %~1
echo %date% %time% %~1>> "%LOGFILE%"
exit /b 0

:fail
echo.
echo [FAIL] EXE build failed.
echo [INFO] Open log: %LOGFILE%
echo [TIP] Common causes: Python not installed, pip blocked by proxy, antivirus block.
echo.
pause
exit /b 1

:done
echo.
pause
exit /b 0
