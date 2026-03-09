#!/usr/bin/env bash
set -euo pipefail

# Windows exe is generated when this is run on Windows (or with cross-build tooling).
# On Linux/macOS, PyInstaller will produce a native executable, not .exe.
python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name VocaFlow \
  --add-data "data:./data" \
  main.py

echo "Build complete. Check dist/ directory."
