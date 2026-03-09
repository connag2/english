@echo off
setlocal

REM Build Windows executable (.exe)
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --name VocaFlow ^
  --add-data "data;data" ^
  main.py

if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo Build complete. Check dist\VocaFlow\VocaFlow.exe or dist\VocaFlow.exe
endlocal
