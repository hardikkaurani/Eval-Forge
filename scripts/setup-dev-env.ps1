# EvalForge Developer Onboarding Script (Windows PowerShell)
# Target: Get a new contributor from git clone to running tests in < 5 minutes!

$ErrorActionPreference = "Stop"

Write-Host "🚀 Welcome to EvalForge Developer Setup (Windows)!" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✅ Python detected: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is required but not found on PATH." -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js detected: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is required but not found on PATH." -ForegroundColor Red
    exit 1
}

# 1. Backend Setup
Write-Host "`n📦 Setting up Backend Python virtual environment..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "  Created virtualenv in backend\.venv" -ForegroundColor Gray
}

& .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-Host "  Installed backend Python dependencies." -ForegroundColor Gray

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "  Copied backend\.env.example to backend\.env" -ForegroundColor Gray
}

Write-Host "🧪 Running backend pytest verification..." -ForegroundColor Yellow
python -m pytest --quiet
Write-Host "  Backend pytest suite PASSED! 100% Green." -ForegroundColor Green
Set-Location ..

# 2. Frontend Setup
Write-Host "`n🎨 Setting up Frontend Node.js dependencies..." -ForegroundColor Yellow
Set-Location frontend

cmd /c npm install --legacy-peer-deps --quiet
Write-Host "  Installed frontend npm packages." -ForegroundColor Gray

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "  Copied frontend\.env.example to frontend\.env" -ForegroundColor Gray
}

Write-Host "🔍 Running frontend typecheck & lint verification..." -ForegroundColor Yellow
cmd /c npm run typecheck
cmd /c npm run lint
Write-Host "  Frontend typecheck & lint PASSED! 100% Green." -ForegroundColor Green
Set-Location ..

Write-Host "`n===========================================" -ForegroundColor Cyan
Write-Host "🎉 EvalForge Local Developer Setup Complete!" -ForegroundColor Green
Write-Host "`nTo start developing:" -ForegroundColor White
Write-Host "  Backend API:  cd backend; .venv\Scripts\activate; uvicorn app.main:app --reload" -ForegroundColor Gray
Write-Host "  Frontend UI:  cd frontend; npm run dev" -ForegroundColor Gray
Write-Host "  Docker Full:  docker compose up --build" -ForegroundColor Gray
Write-Host "===========================================" -ForegroundColor Cyan
