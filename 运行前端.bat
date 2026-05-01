@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "ROOT_DIR=%~dp0"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "ENV_FILE=%ROOT_DIR%.env"
set "CLOUD_API_URL="

rem -- Read VITE_CLOUD_API_URL from .env ---------------------------
if exist "%ENV_FILE%" (
  for /f "usebackq tokens=1,* delims==" %%a in ("%ENV_FILE%") do (
    set "_KEY=%%a"
    if "!_KEY!"=="VITE_CLOUD_API_URL" set "CLOUD_API_URL=%%b"
  )
)

if not defined CLOUD_API_URL (
  echo [WARN] VITE_CLOUD_API_URL not found in .env
  echo.
  set /p "CLOUD_API_URL=Enter cloud backend URL (or press Enter to cancel): "
  if "!CLOUD_API_URL!"=="" (
    echo [CANCEL] Cancelled.
    pause
    exit /b 1
  )
)

echo.
echo [MODE] Cloud Backend (quick start)
echo [INFO] Cloud backend: !CLOUD_API_URL!
echo.

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

echo [START] Frontend: http://127.0.0.1:5173  (API -^> !CLOUD_API_URL!)
echo.

cd /d "%FRONTEND_DIR%"
set "VITE_API_URL=!CLOUD_API_URL!"
call pnpm dev --host 0.0.0.0 --port 5173
pause
