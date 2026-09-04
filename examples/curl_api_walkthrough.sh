#!/usr/bin/env bash
# ================================================================
# Eval-Forge REST API cURL Walkthrough
# Demonstrates authentication, health check, project creation,
# and evaluation run submission via standard HTTP requests.
# ================================================================
set -e

API_KEY="${EVALFORGE_API_KEY:-ef_live_example_key}"
BASE_URL="${EVALFORGE_BASE_URL:-http://localhost:8000}"

echo "=========================================================="
echo "🚀 Eval-Forge REST API cURL Walkthrough"
echo "Target Base URL: ${BASE_URL}"
echo "=========================================================="

# 1. Health check
echo -e "\n[1] Checking service health..."
curl -s -X GET "${BASE_URL}/health" | jq . || curl -s -X GET "${BASE_URL}/health"

# 2. List Projects
echo -e "\n\n[2] Listing evaluation projects..."
curl -s -X GET "${BASE_URL}/api/v1/projects?page=1&page_size=5" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" | jq . || true

# 3. Create Project
echo -e "\n\n[3] Creating new project..."
CREATE_RES=$(curl -s -X POST "${BASE_URL}/api/v1/projects" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cURL REST API Benchmark",
    "description": "Automated evaluation created via HTTP cURL"
  }')

echo "${CREATE_RES}" | jq . || echo "${CREATE_RES}"

# 4. Trigger Evaluation Run
PROJECT_ID=$(echo "${CREATE_RES}" | jq -r '.data.id // .id // "00000000-0000-0000-0000-000000000001"')

echo -e "\n\n[4] Launching evaluation run for project ${PROJECT_ID}..."
curl -s -X POST "${BASE_URL}/api/v1/evaluations" \
  -H "X-API-Key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": \"${PROJECT_ID}\",
    \"name\": \"cURL Evaluation Run\",
    \"metrics\": [\"accuracy\", \"semantic_similarity\"],
    \"test_cases\": [
      {
        \"input\": \"What is EvalForge?\",
        \"actual_output\": \"EvalForge is an enterprise-grade LLM evaluation platform.\",
        \"expected_output\": \"EvalForge is an open-source evaluation framework for AI models.\"
      }
    ]
  }" | jq . || true

echo -e "\n\n=========================================================="
echo "✅ REST API cURL Walkthrough Completed."
echo "=========================================================="
