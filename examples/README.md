# Eval-Forge Examples & Quickstarts

Welcome to the **Eval-Forge** examples directory. This folder provides complete, verified, end-to-end examples demonstrating how to evaluate LLM applications using our Python SDK, TypeScript SDK, CLI, and REST API.

---

## Directory Contents

| File | Description | Language / Tool |
|---|---|---|
| [`python_quickstart.py`](./python_quickstart.py) | End-to-end evaluation lifecycle with the official Python SDK | Python 3.9+ |
| [`typescript_quickstart.ts`](./typescript_quickstart.ts) | Programmatic evaluation setup with the `@evalforge/sdk` package | TypeScript / Node.js |
| [`cli_evaluation_example.json`](./cli_evaluation_example.json) | Sample dataset and configuration for the CLI evaluation runner | JSON |
| [`run_cli_eval.sh`](./run_cli_eval.sh) | Automated evaluation pipeline executed via the `evalforge` CLI | Bash / Shell |
| [`curl_api_walkthrough.sh`](./curl_api_walkthrough.sh) | Direct HTTP API requests demonstrating core endpoints | cURL / REST |

---

## 1. Python SDK Quickstart

### Prerequisites
```bash
pip install evalforge
# or from source repository:
pip install -e sdk/python
```

### Run
```bash
export EVALFORGE_API_KEY="ef_live_your_api_key_here"
export EVALFORGE_BASE_URL="http://localhost:8000"

python examples/python_quickstart.py
```

---

## 2. TypeScript SDK Quickstart

### Prerequisites
```bash
npm install @evalforge/sdk
```

### Run
```bash
export EVALFORGE_API_KEY="ef_live_your_api_key_here"
export EVALFORGE_BASE_URL="http://localhost:8000"

npx tsx examples/typescript_quickstart.ts
```

---

## 3. CLI Evaluation

### Prerequisites
```bash
pip install evalforge-cli
# or from source repository:
pip install -e cli
```

### Run
```bash
# 1. Authenticate
evalforge auth login --key "ef_live_your_api_key_here"

# 2. Run Evaluation
evalforge evaluations run \
  --project-id "00000000-0000-0000-0000-000000000001" \
  --config examples/cli_evaluation_example.json
```

---

## 4. Direct REST API Walkthrough

```bash
chmod +x examples/curl_api_walkthrough.sh
./examples/curl_api_walkthrough.sh
```
