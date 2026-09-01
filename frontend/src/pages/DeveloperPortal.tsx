import { useState } from 'react';
import { BookOpen } from 'lucide-react';
import { Card } from '../components/common/Card';
import { CodeBlock } from '../components/common/CodeBlock';

export default function DeveloperPortal() {
  const [tab, setTab] = useState<'python' | 'curl' | 'mcp'>('python');

  const pythonCode = `import evalforge

client = evalforge.Client(api_key="ef_live_...")

# Run an automated evaluation pipeline
result = client.experiments.create(
    name="GPT-4 Hallucination Benchmark",
    dataset_version_id="v1.0.0",
    judge="gpt-4-turbo",
    provider="OpenAI"
)

print(f"Pass Rate: {result.aggregate_score * 100}%")`;

  const curlCode = `curl -X POST "https://api.evalforge.ai/api/v1/evaluation/experiments" \\
  -H "X-API-Key: ef_live_..." \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "cURL Automated Benchmark",
    "dataset_version_id": "v1.0.0",
    "judge": "gpt-4-turbo"
  }'`;

  const mcpCode = `{
  "mcpServers": {
    "evalforge": {
      "serverUrl": "https://api.evalforge.ai/mcp",
      "headers": {
        "X-API-Key": "ef_live_..."
      }
    }
  }
}`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-workbench-border pb-4">
        <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-brand-terracotta" />
          Developer Platform & SDK Documentation
        </h1>
        <p className="text-xs text-workbench-muted mt-1">
          Integrate evaluation pipelines into CI/CD workflows via Python SDK, REST API, or Model Context Protocol (MCP).
        </p>
      </div>

      {/* Tabs Bar */}
      <div className="flex items-center gap-2 border-b border-workbench-border pb-2">
        <button
          onClick={() => setTab('python')}
          className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            tab === 'python'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          Python SDK
        </button>
        <button
          onClick={() => setTab('curl')}
          className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            tab === 'curl'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          REST API (cURL)
        </button>
        <button
          onClick={() => setTab('mcp')}
          className={`px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            tab === 'mcp'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          Model Context Protocol (MCP)
        </button>
      </div>

      {/* Code Snippet Display */}
      <Card padding="none">
        {tab === 'python' && <CodeBlock title="evalforge-python v1.4.0" code={pythonCode} language="python" />}
        {tab === 'curl' && <CodeBlock title="REST API Endpoint Example" code={curlCode} language="bash" />}
        {tab === 'mcp' && <CodeBlock title="MCP Client Configuration (mcp_config.json)" code={mcpCode} language="json" />}
      </Card>
    </div>
  );
}
