# YOLOv8 Parking Detection System - Startup Script
# PowerShell Version

Set-Location $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YOLOv8 Parking System - Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check .env files
Write-Host "Checking environment files..." -ForegroundColor Yellow

if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env file not found" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure Supabase settings" -ForegroundColor Red
    Read-Host "Press any key to exit"
    exit 1
}

if (-not (Test-Path "backend\.env")) {
    Write-Host "WARNING: backend\.env file not found" -ForegroundColor Yellow
    Write-Host "Continuing with root .env only..." -ForegroundColor Yellow
}

# Check virtual environment
Write-Host "Checking virtual environment..." -ForegroundColor Yellow

$venvPath = $null

if (Test-Path ".venv\Scripts\Activate.ps1") {
    $venvPath = ".venv\Scripts\Activate.ps1"
    Write-Host "Found venv: .venv" -ForegroundColor Green
}
elseif (Test-Path "venv\Scripts\Activate.ps1") {
    $venvPath = "venv\Scripts\Activate.ps1"
    Write-Host "Found venv: venv" -ForegroundColor Green
}
elseif (Test-Path "backend\venv\Scripts\Activate.ps1") {
    $venvPath = "backend\venv\Scripts\Activate.ps1"
    Write-Host "Found venv: backend\venv" -ForegroundColor Green
}
else {
    Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
    Write-Host "  1) Create venv:  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  2) Activate:     .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  3) Install deps: pip install -r backend\requirements.txt" -ForegroundColor Yellow
    Read-Host "Press any key to exit"
    exit 1
}

Write-Host "Environment ready!" -ForegroundColor Green
Write-Host ""

# Start backend
Write-Host "Starting backend service..." -ForegroundColor Yellow

$backendScript = @"
& '$venvPath'
Set-Location backend
python main.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript -WindowStyle Normal

Write-Host "Waiting for backend..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting frontend service..." -ForegroundColor Yellow

$frontendScript = @"
Set-Location '$PSScriptRoot'
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Startup script will close automatically in 2 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
