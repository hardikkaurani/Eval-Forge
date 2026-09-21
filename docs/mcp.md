# Model Context Protocol (MCP) Guide

Eval-Forge natively exposes its evaluation engine and dataset assets through the **Model Context Protocol (MCP)**, allowing AI coding assistants (Claude Desktop, Cursor, Continue, LangChain) to autonomously trigger evaluations, monitor runs, and inspect quality metrics.

---

## 1. Available Tools

All tools strictly enforce workspace and tenant-level isolation:

| Tool Name | Purpose | Parameters |
|---|---|---|
| `list_projects` | Lists evaluation projects accessible within the authenticated workspace. | `page` (int, default: 1), `page_size` (int, default: 20) |
| `list_datasets` | Lists datasets and version IDs available for a specific project. | `project_id` (UUID, required) |
| `get_evaluation_status` | Returns execution status (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`), completed case counts, and progression percentage. | `run_id` (UUID, required) |
| `get_evaluation_results` | Retrieves scored metrics, judge rationale, and latency distribution for an evaluation run. | `run_id` (UUID, required), `limit` (int, default: 50) |

---

## 2. API Endpoints

### List Available Tools
```bash
curl -X GET "http://localhost:8000/api/v1/mcp/tools" \
  -H "X-API-Key: ef_live_your_api_key_here"
```

### Call an MCP Tool
```bash
curl -X POST "http://localhost:8000/api/v1/mcp/tools/call" \
  -H "X-API-Key: ef_live_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "list_projects",
    "arguments": {
      "page": 1,
      "page_size": 10
    }
  }'
```

### Tool Response Format
```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 2 projects in workspace:\n- Customer Support AI (ID: 3fa85f64-5717-4562-b3fc-2c963f66afa6)\n- Code Generation Benchmarks (ID: e4d3c2b1-5a6f-7e8d-9c0b-1a2b3c4d5e6f)"
    }
  ],
  "is_error": false
}
```

---

## 3. Configuring AI Clients

### Claude Desktop Configuration
Add Eval-Forge to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "evalforge": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8000/api/v1/mcp/tools"
      ],
      "env": {
        "EVALFORGE_API_KEY": "ef_live_your_api_key_here"
      }
    }
  }
}
```

### Cursor / Agent Frameworks
When integrating with agent runners, pass your workspace API key in request headers:
```http
X-API-Key: ef_live_your_api_key_here
```

---

## 4. Security & Permissions

1. **Workspace Boundary:** Tools only return data belonging to the workspace associated with the provided `X-API-Key`. Cross-workspace access attempts return `is_error: true`.
2. **Read-Only Inspection:** MCP tools are designed for safe agent observability and reporting; they do not perform destructive actions (e.g. project or dataset deletion).
3. **Bounded Output Payloads:** Output responses enforce strict pagination and result limits to prevent context window overflow in LLMs.
