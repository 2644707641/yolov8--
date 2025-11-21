@echo off
REM YOLOv8 Parking Detection System - Startup Script (CMD Version)
cd /d "%~dp0"

echo ========================================
echo YOLOv8 Parking System - Starting...
echo ========================================
echo.

REM Check .env file
echo Checking environment files...
if not exist .env (
    echo ERROR: .env file not found
    echo Please copy .env.example to .env and configure Supabase settings
    echo.
    pause
    exit /b 1
)

REM Check backend .env (optional - don't fail if missing)
if not exist backend\.env (
    echo WARNING: backend\.env not found - using root .env only
    echo.
)

REM Check virtual environment
echo Checking virtual environment...
set "VENV_ACT="

REM Priority: .venv, venv, backend\venv
if exist ".venv\Scripts\activate.bat" (
    set "VENV_ACT=.venv\Scripts\activate.bat"
    echo Found venv: .venv
)
if not defined VENV_ACT if exist "venv\Scripts\activate.bat" (
    set "VENV_ACT=venv\Scripts\activate.bat"
    echo Found venv: venv
)
if not defined VENV_ACT if exist "backend\venv\Scripts\activate.bat" (
    set "VENV_ACT=backend\venv\Scripts\activate.bat"
    echo Found venv: backend\venv
)

if not defined VENV_ACT (
    echo ERROR: Virtual environment not found
    echo.
    echo Please create a virtual environment:
    echo   1^) Create:  python -m venv .venv
    echo   2^) Activate: .venv\Scripts\activate
    echo   3^) Install:  pip install -r backend\requirements.txt
    echo.
    pause
    exit /b 1
)

echo Environment ready!
echo.

REM Start backend service
echo Starting backend service...
start "YOLOv8 Backend" cmd /k "call "%VENV_ACT%" && cd backend && python main.py"

REM Wait for backend to start
echo Waiting for backend...
timeout /t 3 /nobreak >nul

REM Start frontend service
echo Starting frontend service...
start "YOLOv8 Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Startup script will close automatically in 2 seconds...
timeout /t 2 /nobreak >nul
