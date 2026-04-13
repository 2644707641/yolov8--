@echo off
setlocal EnableExtensions
chcp 65001 >nul

cd /d "%~dp0"

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"

if not exist "%BACKEND_PYTHON%" (
  echo [ERROR] Backend Python not found: %BACKEND_PYTHON%
  echo Please create backend\.venv and install backend dependencies first.
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
  echo [ERROR] frontend\node_modules not found.
  echo Please run pnpm install in the frontend directory first.
  pause
  exit /b 1
)

where pnpm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] pnpm is not available in PATH.
  echo Please install pnpm or add it to PATH first.
  pause
  exit /b 1
)

echo [DEBUG MODE] Starting development services...
echo.

call :is_port_listening 8000
if errorlevel 1 (
  echo [START][DEBUG] Backend: http://127.0.0.1:8000
  start "backend-debug" powershell.exe -NoExit -Command ^
    "$env:PYTHONUNBUFFERED='1'; $env:PYTHONDEVMODE='1'; Set-Location '%BACKEND_DIR%'; & '%BACKEND_PYTHON%' -m uvicorn main:app --reload --reload-dir app --host 0.0.0.0 --port 8000 --log-level debug"
) else (
  echo [SKIP] Port 8000 is already in use.
  call :print_port_owner 8000
)

call :is_port_listening 5173
if errorlevel 1 (
  echo [START][DEBUG] Frontend: http://127.0.0.1:5173
  start "frontend-debug" powershell.exe -NoExit -Command ^
    "Set-Location '%FRONTEND_DIR%'; pnpm dev --host 0.0.0.0 --port 5173 --strictPort"
) else (
  echo [SKIP] Port 5173 is already in use.
  call :print_port_owner 5173
)

echo.
echo Debug launch request processed.
echo Frontend local: http://127.0.0.1:5173
echo Backend local:  http://127.0.0.1:8000
echo Tips:
echo - Backend runs with auto-reload and debug log level.
echo - Frontend runs with strict port 5173.
echo - If either port is occupied, owner process is printed above.
exit /b 0

:is_port_listening
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "if (Test-NetConnection -ComputerName 127.0.0.1 -Port %~1 -InformationLevel Quiet) { exit 0 } else { exit 1 }"
exit /b %errorlevel%

:print_port_owner
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$conn = Get-NetTCPConnection -LocalPort %~1 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; if ($null -eq $conn) { Write-Host '  Unable to resolve owner process.'; exit 0 }; $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue; if ($proc) { Write-Host ('  Port %~1 -> PID {0} ({1})' -f $proc.Id, $proc.ProcessName) } else { Write-Host ('  Port %~1 -> PID {0}' -f $conn.OwningProcess) }"
exit /b 0
