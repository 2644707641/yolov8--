@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"
set "ENV_FILE=%ROOT_DIR%.env"
set "LOCAL_API_URL=http://localhost:8000"
set "CLOUD_API_URL="
set "FRONTEND_RUN_DEV="

rem -- Read VITE_CLOUD_API_URL from .env ---------------------------
if exist "%ENV_FILE%" (
  for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
    set "_KEY=%%a"
    if "!_KEY!"=="VITE_CLOUD_API_URL" set "CLOUD_API_URL=%%b"
  )
)

rem -- Display mode selection menu ---------------------------------
echo.
echo  ============================================
echo    YOLOv8 Debug Launcher
echo  ============================================
echo.
echo    [1] Local Backend (debug)
echo        Backend: hot-reload + debug log
echo        http://localhost:8000
echo.
echo    [2] Cloud Backend (debug)
echo        Frontend only, connect to cloud
if defined CLOUD_API_URL (
  echo        Cloud: !CLOUD_API_URL!
) else (
  echo        Cloud: Not configured [set VITE_CLOUD_API_URL in .env]
)
echo.
echo  ============================================
echo.
set /p "MODE_CHOICE=Select mode [1/2]: "

if "%MODE_CHOICE%"=="1" goto :mode_local_debug
if "%MODE_CHOICE%"=="2" goto :mode_cloud_debug

echo [ERROR] Invalid choice. Please enter 1 or 2.
pause
exit /b 1

rem -- Mode 1: Local Backend Debug --------------------------------
:mode_local_debug
echo.
echo [MODE] Local Backend (debug)
echo.

call :check_backend_deps
if errorlevel 1 exit /b 1
call :check_frontend_deps
if errorlevel 1 exit /b 1

call :is_port_listening 8000
if errorlevel 1 (
  echo [START][DEBUG] Backend: http://127.0.0.1:8000
  start "backend-debug" powershell.exe -NoExit -Command ^
    "$env:PYTHONUNBUFFERED='1'; $env:PYTHONDEVMODE='1'; Set-Location '%BACKEND_DIR%'; & '%BACKEND_PYTHON%' -m uvicorn main:app --reload --reload-dir app --host 0.0.0.0 --port 8000 --log-level debug"
) else (
  echo [SKIP] Port 8000 is already in use.
  call :print_port_owner 8000
)

call :start_frontend "%LOCAL_API_URL%"

echo.
echo Debug mode started!
echo   Frontend : http://127.0.0.1:5173
echo   Backend  : http://127.0.0.1:8000 (debug, hot-reload)
echo   Tip      : Backend auto-reloads on code change, log-level=debug
exit /b 0

rem -- Mode 2: Cloud Backend Debug --------------------------------
:mode_cloud_debug
echo.
echo [MODE] Cloud Backend (debug)
echo.

if not defined CLOUD_API_URL (
  echo [WARN] Cloud backend URL not found.
  echo [WARN] Set VITE_CLOUD_API_URL in .env or enter it below.
  echo.
  set /p "CLOUD_API_URL=Enter cloud backend URL (or press Enter to cancel): "
  if "!CLOUD_API_URL!"=="" (
    echo [CANCEL] Cancelled.
    pause
    exit /b 1
  )
)

echo [INFO] Cloud backend: !CLOUD_API_URL!
echo.

call :check_frontend_deps
if errorlevel 1 exit /b 1

call :start_frontend "!CLOUD_API_URL!"

echo.
echo Debug mode started!
echo   Frontend : http://127.0.0.1:5173
echo   Backend  : !CLOUD_API_URL! (cloud)
echo   Tip      : Frontend runs with strictPort
exit /b 0

rem -- Utility functions -------------------------------------------

:check_backend_deps
if not exist "%BACKEND_PYTHON%" (
  echo [ERROR] Backend Python not found: %BACKEND_PYTHON%
  echo         Create backend\.venv and install dependencies first.
  pause
  exit /b 1
)
exit /b 0

:check_frontend_deps
if not exist "%FRONTEND_DIR%\node_modules" (
  echo [ERROR] frontend\node_modules not found.
  echo         Run "npm install" or "pnpm install" in the frontend directory first.
  pause
  exit /b 1
)
where pnpm >nul 2>nul
if not errorlevel 1 (
  set "FRONTEND_RUN_DEV=pnpm dev"
  exit /b 0
)
where npm >nul 2>nul
if not errorlevel 1 (
  set "FRONTEND_RUN_DEV=npm run dev --"
  exit /b 0
)
if not defined FRONTEND_RUN_DEV (
  echo [ERROR] Neither pnpm nor npm is in PATH. Install Node.js first.
  pause
  exit /b 1
)
exit /b 0

:start_frontend
set "FE_API_URL=%~1"
call :is_port_listening 5173
if errorlevel 1 (
  echo [START][DEBUG] Frontend: http://127.0.0.1:5173  (API -^> %FE_API_URL%)
  start "frontend-debug" powershell.exe -NoExit -Command ^
    "$env:VITE_API_URL='%FE_API_URL%'; Set-Location '%FRONTEND_DIR%'; !FRONTEND_RUN_DEV! --host 0.0.0.0 --port 5173 --strictPort"
) else (
  echo [SKIP] Port 5173 is already in use.
  call :print_port_owner 5173
)
exit /b 0

:is_port_listening
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "if (Test-NetConnection -ComputerName 127.0.0.1 -Port %~1 -InformationLevel Quiet) { exit 0 } else { exit 1 }"
exit /b %errorlevel%

:print_port_owner
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "$conn = Get-NetTCPConnection -LocalPort %~1 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; if ($null -eq $conn) { Write-Host '  Unable to resolve owner process.'; exit 0 }; $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue; if ($proc) { Write-Host ('  Port %~1 -> PID {0} ({1})' -f $proc.Id, $proc.ProcessName) } else { Write-Host ('  Port %~1 -> PID {0}' -f $conn.OwningProcess) }"
exit /b 0
