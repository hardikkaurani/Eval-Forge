#!/usr/bin/env bash
# ================================================================
# Eval-Forge CLI Evaluation Runner Walkthrough
# ================================================================
set -e

API_KEY="${EVALFORGE_API_KEY:-ef_live_example_key}"
BASE_URL="${EVALFORGE_BASE_URL:-http://localhost:8000}"

echo "=========================================================="
echo "🚀 Running Eval-Forge CLI Evaluation Suite"
echo "Target Base URL: ${BASE_URL}"
echo "=========================================================="

# 1. Configure base URL and authenticate
echo "Step 1: Configuring CLI endpoint and authentication..."
evalforge config set --base-url "${BASE_URL}"
evalforge auth login --key "${API_KEY}"
evalforge auth status

# 2. List or create project
echo -e "\nStep 2: Listing projects..."
evalforge projects list --page 1 --page-size 5

# 3. Trigger evaluation
PROJECT_ID="${1:-00000000-0000-0000-0000-000000000001}"
echo -e "\nStep 3: Triggering evaluation against project: ${PROJECT_ID}..."
evalforge evaluations run \
  --project-id "${PROJECT_ID}" \
  --config examples/cli_evaluation_example.json \
  --json

echo -e "\n=========================================================="
echo "✅ CLI Evaluation workflow complete."
echo "=========================================================="
