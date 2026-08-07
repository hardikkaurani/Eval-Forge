#!/usr/bin/env bash
# EvalForge Developer Onboarding & Local Environment Setup Script
# Target: Get a new contributor from git clone to running tests in < 5 minutes!

set -e

echo "🚀 Welcome to EvalForge Developer Setup!"
echo "==========================================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.12+."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python version detected: $PYTHON_VERSION"

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 20+."
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Node.js version detected: $NODE_VERSION"

# 1. Setup Backend Environment
echo ""
echo "📦 Setting up Backend Python virtual environment..."
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "  Created virtualenv in backend/.venv"
fi

source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  Installed backend Python dependencies."

# Copy backend environment sample if missing
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  Copied backend/.env.example to backend/.env"
fi

echo "🧪 Running backend pytest verification..."
pytest --quiet
echo "  Backend pytest suite PASSED! 100% Green."
cd ..

# 2. Setup Frontend Environment
echo ""
echo "🎨 Setting up Frontend Node.js dependencies..."
cd frontend
npm install --legacy-peer-deps --quiet
echo "  Installed frontend npm packages."

# Copy frontend environment sample if missing
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  Copied frontend/.env.example to frontend/.env"
fi

echo "🔍 Running frontend typecheck & lint verification..."
npm run typecheck
npm run lint
echo "  Frontend typecheck & lint PASSED! 100% Green."
cd ..

echo ""
echo "==========================================="
echo "🎉 EvalForge Local Developer Setup Complete!"
echo ""
echo "To start developing:"
echo "  Backend API:  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "  Frontend UI:  cd frontend && npm run dev"
echo "  Docker Full:  docker compose up --build"
echo "==========================================="
