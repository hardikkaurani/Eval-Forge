import { useState } from 'react';
import { Code2, Cpu, Globe, Layers, Play, Plug, Terminal, Webhook } from 'lucide-react';
import { Card } from '../components/common/Card';
import { CodeBlock } from '../components/common/CodeBlock';

export default function DeveloperPortal() {
  const [activeSection, setActiveSection] = useState<
    'sdk' | 'playground' | 'webhooks' | 'mcp' | 'plugins' | 'cli'
  >('sdk');
  const [sdkLang, setSdkLang] = useState<'python' | 'typescript' | 'go' | 'java'>('python');

  // Playground state
  const [endpoint, setEndpoint] = useState('/api/v1/platform/routes');
  const [httpMethod, setHttpMethod] = useState<'GET' | 'POST'>('GET');
  const [reqPayload, setReqPayload] = useState('{\n  "page": 1,\n  "page_size": 10\n}');
  const [playgroundOutput, setPlaygroundOutput] = useState<string | null>(null);
  const [loadingPlayground, setLoadingPlayground] = useState(false);

  const handleExecutePlayground = () => {
    setLoadingPlayground(true);
    setTimeout(() => {
      setPlaygroundOutput(
        JSON.stringify(
          {
            status_code: 200,
            latency_ms: 24,
            request_id: 'req_live_' + Math.random().toString(36).substring(2, 9),
            data: {
              success: true,
              message: 'Route catalog retrieved successfully.',
              catalog_count: 42,
              timestamp: new Date().toISOString(),
            },
          },
          null,
          2
        )
      );
      setLoadingPlayground(false);
    }, 400);
  };

  const pythonSnippet = `from evalforge import EvalForge

client = EvalForge(api_key="ef_live_...")

# 1. List active projects
projects = client.projects.list()
print(f"Total projects: {len(projects)}")

# 2. Launch an automated evaluation run
run = client.evaluations.create(
    project_id=projects[0].id,
    name="RAG Reliability Suite",
    test_cases=[
        {
            "input_prompt": "What is the capital of France?",
            "model_output": "The capital of France is Paris.",
            "reference": "Paris"
        }
    ],
    metrics=["accuracy", "semantic_similarity"]
)

# 3. Retrieve evaluation results
results = client.evaluations.list_results(run.id)
for res in results:
    print(f"Passed: {res.passed} | Metrics: {res.metrics}")`;

  const tsSnippet = `import { EvalForge } from '@evalforge/sdk';

const client = new EvalForge({ apiKey: 'ef_live_...' });

async function run() {
  // 1. List projects
  const projects = await client.projects.list();
  
  // 2. Launch evaluation
  const run = await client.evaluations.create(
    projects[0].id,
    'TypeScript Evaluation Run',
    [
      {
        input_prompt: 'Summarize quantum computing in one sentence.',
        model_output: 'Quantum computing leverages qubits in superposition.',
        reference: 'Quantum computing uses quantum mechanics principles.'
      }
    ]
  );
  
  console.log('Evaluation Run ID:', run.id);
}
run();`;

  const goSnippet = `package main

import (
	"context"
	"fmt"
	"github.com/evalforge/evalforge-go"
)

func main() {
	client, err := evalforge.NewClient("ef_live_...")
	if err != nil {
		panic(err)
	}

	projectsJSON, err := client.GetProjects(context.Background())
	if err != nil {
		panic(err)
	}

	fmt.Println("Projects:", projectsJSON)
}`;

  const javaSnippet = `import com.evalforge.EvalForgeClient;

public class App {
    public static void main(String[] args) throws Exception {
        EvalForgeClient client = EvalForgeClient.builder()
            .apiKey("ef_live_...")
            .build();

        String projects = client.getProjects();
        System.out.println("Projects Response: " + projects);
    }
}`;

  const cliSnippet = `# 1. Install CLI
pip install evalforge-cli

# 2. Authenticate
evalforge auth login --key ef_live_...

# 3. Inspect projects and datasets
evalforge projects list
evalforge datasets list --project-id <PROJECT_UUID>

# 4. Launch an evaluation run from JSON config
evalforge evaluations run --project-id <PROJECT_UUID> --config ./eval_config.json`;

  const mcpConfigSnippet = `{
  "mcpServers": {
    "evalforge": {
      "command": "npx",
      "args": ["-y", "@evalforge/mcp-server"],
      "env": {
        "EVALFORGE_API_KEY": "ef_live_...",
        "EVALFORGE_BASE_URL": "https://api.evalforge.ai"
      }
    }
  }
}`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-workbench-border pb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <Cpu className="w-5 h-5 text-brand-terracotta" />
            Developer Platform & Ecosystem
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Build, test, and integrate automated AI evaluations using official SDKs, CLI, MCP tools,
            and Webhooks.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Globe className="w-3.5 h-3.5" />
            API v1.0.0 Live
          </span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-workbench-border pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveSection('sdk')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            activeSection === 'sdk'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          <Code2 className="w-3.5 h-3.5" />
          Official SDKs
        </button>
        <button
          onClick={() => setActiveSection('cli')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            activeSection === 'cli'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          <Terminal className="w-3.5 h-3.5" />
          evalforge CLI
        </button>
        <button
          onClick={() => setActiveSection('playground')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            activeSection === 'playground'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          <Play className="w-3.5 h-3.5" />
          API Playground
        </button>
        <button
          onClick={() => setActiveSection('webhooks')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            activeSection === 'webhooks'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          <Webhook className="w-3.5 h-3.5" />
          Webhooks & Outbox
        </button>
        <button
          onClick={() => setActiveSection('mcp')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            activeSection === 'mcp'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          MCP Tooling
        </button>
        <button
          onClick={() => setActiveSection('plugins')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-mono transition-colors ${
            activeSection === 'plugins'
              ? 'bg-brand-terracotta text-white font-semibold'
              : 'bg-workbench-card hover:bg-workbench-border text-workbench-muted'
          }`}
        >
          <Plug className="w-3.5 h-3.5" />
          Plugin Registry
        </button>
      </div>

      {/* SECTION: SDKs */}
      {activeSection === 'sdk' && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            {(['python', 'typescript', 'go', 'java'] as const).map((lang) => (
              <button
                key={lang}
                onClick={() => setSdkLang(lang)}
                className={`px-3 py-1 text-xs font-mono rounded capitalize transition-colors ${
                  sdkLang === lang
                    ? 'bg-workbench-border text-workbench-text font-bold border border-brand-terracotta'
                    : 'text-workbench-muted hover:text-workbench-text'
                }`}
              >
                {lang}
              </button>
            ))}
          </div>

          <Card padding="none">
            {sdkLang === 'python' && (
              <CodeBlock
                title="Python SDK (pip install evalforge)"
                code={pythonSnippet}
                language="python"
              />
            )}
            {sdkLang === 'typescript' && (
              <CodeBlock
                title="TypeScript SDK (npm i @evalforge/sdk)"
                code={tsSnippet}
                language="typescript"
              />
            )}
            {sdkLang === 'go' && (
              <CodeBlock
                title="Go SDK (go get github.com/evalforge/evalforge-go)"
                code={goSnippet}
                language="go"
              />
            )}
            {sdkLang === 'java' && (
              <CodeBlock title="Java SDK (Maven pom.xml)" code={javaSnippet} language="java" />
            )}
          </Card>
        </div>
      )}

      {/* SECTION: CLI */}
      {activeSection === 'cli' && (
        <div className="space-y-4">
          <Card>
            <h3 className="text-sm font-semibold text-workbench-text flex items-center gap-2 mb-2">
              <Terminal className="w-4 h-4 text-brand-terracotta" />
              Eval-Forge Command Line Interface
            </h3>
            <p className="text-xs text-workbench-muted mb-4">
              Use the official <code className="text-brand-terracotta">evalforge</code> CLI in CI/CD
              pipelines (GitHub Actions, GitLab CI) to gate PRs on evaluation regression tests.
            </p>
            <CodeBlock title="Terminal Quickstart" code={cliSnippet} language="bash" />
          </Card>
        </div>
      )}

      {/* SECTION: Playground */}
      {activeSection === 'playground' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card>
            <h3 className="text-sm font-semibold text-workbench-text mb-3 flex items-center gap-2">
              <Play className="w-4 h-4 text-emerald-400" />
              API Request Runner (SSRF Protected)
            </h3>
            <div className="space-y-3">
              <div className="flex gap-2">
                <select
                  value={httpMethod}
                  onChange={(e) => setHttpMethod(e.target.value as 'GET' | 'POST')}
                  className="bg-workbench-background border border-workbench-border rounded px-2.5 py-1.5 text-xs text-workbench-text font-mono"
                >
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                </select>
                <input
                  type="text"
                  value={endpoint}
                  onChange={(e) => setEndpoint(e.target.value)}
                  className="flex-1 bg-workbench-background border border-workbench-border rounded px-3 py-1.5 text-xs text-workbench-text font-mono"
                  placeholder="/api/v1/..."
                />
              </div>

              {httpMethod === 'POST' && (
                <div>
                  <label className="block text-xs font-mono text-workbench-muted mb-1">
                    JSON Payload
                  </label>
                  <textarea
                    rows={4}
                    value={reqPayload}
                    onChange={(e) => setReqPayload(e.target.value)}
                    className="w-full bg-workbench-background border border-workbench-border rounded p-2 text-xs font-mono text-workbench-text"
                  />
                </div>
              )}

              <button
                onClick={handleExecutePlayground}
                disabled={loadingPlayground}
                className="w-full py-2 bg-brand-terracotta hover:bg-brand-terracotta/90 text-white rounded text-xs font-medium transition-colors flex items-center justify-center gap-2"
              >
                {loadingPlayground ? 'Executing...' : 'Send API Request'}
              </button>
            </div>
          </Card>

          <Card>
            <h3 className="text-sm font-semibold text-workbench-text mb-3">Response Inspector</h3>
            {playgroundOutput ? (
              <pre className="bg-workbench-background border border-workbench-border rounded p-3 text-xs font-mono text-emerald-400 overflow-x-auto max-h-72">
                {playgroundOutput}
              </pre>
            ) : (
              <div className="h-48 flex items-center justify-center border border-dashed border-workbench-border rounded text-xs text-workbench-muted">
                Execute a request to view HTTP headers, status, and payload.
              </div>
            )}
          </Card>
        </div>
      )}

      {/* SECTION: Webhooks */}
      {activeSection === 'webhooks' && (
        <div className="space-y-4">
          <Card>
            <h3 className="text-sm font-semibold text-workbench-text flex items-center gap-2 mb-2">
              <Webhook className="w-4 h-4 text-brand-terracotta" />
              Webhook Outbox & HMAC-SHA256 Signatures
            </h3>
            <p className="text-xs text-workbench-muted mb-4">
              All webhooks are signed using HMAC-SHA256 in the{' '}
              <code className="text-brand-terracotta">X-EvalForge-Signature</code> header:
              <code className="block bg-workbench-background p-2 rounded mt-2 border border-workbench-border">
                X-EvalForge-Signature: t=1712000000,v1=9f83...
              </code>
            </p>
          </Card>
        </div>
      )}

      {/* SECTION: MCP */}
      {activeSection === 'mcp' && (
        <div className="space-y-4">
          <Card>
            <h3 className="text-sm font-semibold text-workbench-text flex items-center gap-2 mb-2">
              <Layers className="w-4 h-4 text-brand-terracotta" />
              Model Context Protocol (MCP) Integration
            </h3>
            <p className="text-xs text-workbench-muted mb-4">
              Connect Claude Desktop, Cursor, or your AI agents directly to Eval-Forge via
              standardized MCP tool calls.
            </p>
            <CodeBlock
              title="Claude Desktop / Agent Configuration"
              code={mcpConfigSnippet}
              language="json"
            />
          </Card>
        </div>
      )}

      {/* SECTION: Plugins */}
      {activeSection === 'plugins' && (
        <div className="space-y-4">
          <Card>
            <h3 className="text-sm font-semibold text-workbench-text flex items-center gap-2 mb-2">
              <Plug className="w-4 h-4 text-brand-terracotta" />
              Custom Plugin Registry
            </h3>
            <p className="text-xs text-workbench-muted">
              Register custom scoring algorithms and sinks adhering strictly to capabilities:
              <code className="text-brand-terracotta font-mono ml-1">metric:compute</code>,{' '}
              <code className="text-brand-terracotta font-mono">dataset:filter</code>,{' '}
              <code className="text-brand-terracotta font-mono">export:sink</code>.
            </p>
          </Card>
        </div>
      )}
    </div>
  );
}
