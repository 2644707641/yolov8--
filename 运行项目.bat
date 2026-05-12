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
echo    YOLOv8 Smart Parking Detection
echo  ============================================
echo.
echo    [1] Local Backend
echo        Start backend + frontend locally
echo        Backend:  http://localhost:8000
echo.
echo    [2] Cloud Backend
echo        Frontend only, connect to cloud API
if defined CLOUD_API_URL (
  echo        Cloud: !CLOUD_API_URL!
) else (
  echo        Cloud: Not configured [set VITE_CLOUD_API_URL in .env]
)
echo.
echo  ============================================
echo.
set /p "MODE_CHOICE=Select mode [1/2]: "

if "%MODE_CHOICE%"=="1" goto :mode_local
if "%MODE_CHOICE%"=="2" goto :mode_cloud

echo [ERROR] Invalid choice. Please enter 1 or 2.
pause
exit /b 1

rem -- Mode 1: Local Backend ---------------------------------------
:mode_local
echo.
echo [MODE] Local Backend
echo.

call :check_backend_deps
if errorlevel 1 exit /b 1
call :check_frontend_deps
if errorlevel 1 exit /b 1

call :is_port_listening 8000
if errorlevel 1 (
  echo [START] Backend: http://127.0.0.1:8000
  start "backend-dev" powershell.exe -NoExit -Command "Set-Location '%BACKEND_DIR%'; & '%BACKEND_PYTHON%' -m uvicorn main:app --host 0.0.0.0 --port 8000"
) else (
  echo [SKIP] Port 8000 is already in use.
  call :print_port_owner 8000
)

call :start_frontend "%LOCAL_API_URL%"

echo.
echo Project started!
echo   Frontend : http://127.0.0.1:5173
echo   Backend  : http://127.0.0.1:8000
echo   LAN      : use this computer's IP, e.g. http://192.168.x.x:5173
exit /b 0

rem -- Mode 2: Cloud Backend ---------------------------------------
:mode_cloud
echo.
echo [MODE] Cloud Backend
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
echo Project started!
echo   Frontend : http://127.0.0.1:5173
echo   Backend  : !CLOUD_API_URL! (cloud)
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
  echo         Run "pnpm install" in the frontend directory first.
  pause
  exit /b 1
)
where pnpm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] pnpm is not in PATH. Install pnpm first.
  pause
  exit /b 1
)
exit /b 0

:start_frontend
set "FE_API_URL=%~1"
call :is_port_listening 5173
if errorlevel 1 (
  echo [START] Frontend: http://127.0.0.1:5173  (API -^> %FE_API_URL%)
  start "frontend-dev" powershell.exe -NoExit -Command "$env:VITE_API_URL='%FE_API_URL%'; Set-Location '%FRONTEND_DIR%'; pnpm dev --host 0.0.0.0 --port 5173"
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
