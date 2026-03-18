@echo off
setlocal
chcp 65001 >nul

cd /d "%~dp0"

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"

if not exist "%BACKEND_PYTHON%" (
  echo [ERROR] Backend Python not found: %BACKEND_PYTHON%
  echo Create backend\.venv first and install dependencies.
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
  echo [ERROR] frontend\node_modules not found.
  echo Run pnpm install in the frontend directory first.
  pause
  exit /b 1
)

where pnpm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] pnpm is not available in PATH.
  echo Install pnpm or add it to PATH first.
  pause
  exit /b 1
)

call :is_port_listening 8000
if errorlevel 1 (
  echo [START] Backend: http://127.0.0.1:8000
  start "backend-dev" powershell.exe -NoExit -Command "Set-Location '%BACKEND_DIR%'; & '%BACKEND_PYTHON%' -m uvicorn main:app --host 127.0.0.1 --port 8000"
) else (
  echo [SKIP] Port 8000 is already in use.
)

call :is_port_listening 5173
if errorlevel 1 (
  echo [START] Frontend: http://127.0.0.1:5173
  start "frontend-dev" powershell.exe -NoExit -Command "Set-Location '%FRONTEND_DIR%'; pnpm dev --host 127.0.0.1 --port 5173"
) else (
  echo [SKIP] Port 5173 is already in use.
)

echo.
echo Launch request processed.
echo Frontend: http://127.0.0.1:5173
echo Backend:  http://127.0.0.1:8000
exit /b 0

:is_port_listening
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
  "if (Test-NetConnection -ComputerName 127.0.0.1 -Port %~1 -InformationLevel Quiet) { exit 0 } else { exit 1 }"
exit /b %errorlevel%
