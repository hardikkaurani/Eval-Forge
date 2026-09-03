# Eval-Forge CLI (`evalforge-cli`)

Official Command-Line Interface for the [Eval-Forge](https://github.com/hardikkaurani/Eval-Forge) AI Evaluation Platform.

---

## Installation

```bash
pip install evalforge-cli
```

Or install in editable development mode:

```bash
pip install -e cli
```

---

## Authentication & Configuration

Log in with your Eval-Forge API key:

```bash
evalforge auth login --key "ef_live_your_api_key_here"
```

Check current authentication status:

```bash
evalforge auth status
```

Configure custom API base URL:

```bash
evalforge config set --base-url "https://api.evalforge.com"
evalforge config get
```

---

## Command Reference

### Projects

```bash
# List accessible projects in your workspace
evalforge projects list

# Create a new evaluation project
evalforge projects create --name "Production LLM Benchmark" --description "Nightly evaluation suite"
```

### Datasets

```bash
# List datasets for a project
evalforge datasets list --project-id "12345678-1234-5678-1234-567812345678"
```

### Evaluations

```bash
# Launch an evaluation from a JSON configuration file
evalforge evaluations run --project-id "12345678-1234-5678-1234-567812345678" --config eval_config.json
```

### Background Jobs & Results

```bash
# Inspect evaluation background job status
evalforge jobs get --id "job-uuid"

# Fetch evaluation results
evalforge results get --run-id "run-uuid" --limit 50
```

### Output Formatting

Append `--json` to any command to receive raw JSON responses suitable for shell pipelines:

```bash
evalforge projects list --json | jq .
```

---

## License

Apache 2.0 / MIT
