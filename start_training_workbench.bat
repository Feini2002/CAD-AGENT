@echo off
setlocal

cd /d "%~dp0"

set "PY=%USERPROFILE%\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

echo [CAD Agent] Syncing training workbench data...
"%PY%" scripts\sync_training_workbench.py
if errorlevel 1 (
  echo.
  echo [CAD Agent] Sync failed. See output\validation_runs\training-workbench-sync.
  pause
  exit /b 1
)

echo [CAD Agent] Building runtime trace snapshot...
"%PY%" scripts\build_runtime_trace_snapshot.py
if errorlevel 1 (
  echo [CAD Agent] Runtime trace snapshot failed; the workbench will still open.
)

echo [CAD Agent] Starting local workbench server on http://127.0.0.1:8765/capability-map.html
start "CAD Agent Workbench Server" /min "%PY%" -m http.server 8765 --bind 127.0.0.1
timeout /t 1 /nobreak > nul
start "" "http://127.0.0.1:8765/capability-map.html"

echo.
echo Keep this repository folder available while the page is open.
echo Re-run this launcher after training, registry, or coverage changes.
endlocal
