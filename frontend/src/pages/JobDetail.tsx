import { useParams, useNavigate } from 'react-router-dom';
import { Workflow, ArrowLeft } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { CodeBlock } from '../components/common/CodeBlock';

export default function JobDetail() {
  const navigate = useNavigate();
  const { jobId, projectId } = useParams<{ jobId: string; projectId: string }>();

  const activeJobId = jobId || 'job-1049';

  const steps = [
    { name: '1. Validate File Format & Schema', status: 'completed', duration: '120ms' },
    { name: '2. Parse JSONL / CSV Payload Chunks', status: 'completed', duration: '450ms' },
    { name: '3. Sanitize Record Identifiers & Prompts', status: 'completed', duration: '280ms' },
    { name: '4. Commit Records to Database Repository', status: 'running', duration: 'Active' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 border-b border-workbench-border pb-4">
        <Button
          variant="outline"
          size="sm"
          icon={ArrowLeft}
          onClick={() => navigate(`/projects/${projectId || '1'}/jobs`)}
        >
          Back to Jobs
        </Button>
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <Workflow className="w-5 h-5 text-brand-terracotta" />
            Job Step Execution: {activeJobId}
          </h1>
          <p className="text-xs text-workbench-muted">
            Detailed worker pool execution trace and log console output.
          </p>
        </div>
      </div>

      {/* Steps Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Execution Steps" subtitle="Worker pipeline execution steps" className="lg:col-span-1">
          <div className="space-y-3">
            {steps.map((s, idx) => (
              <div
                key={idx}
                className="p-3 rounded bg-workbench-bg border border-workbench-border flex items-center justify-between text-xs font-mono"
              >
                <span className="truncate pr-2">{s.name}</span>
                <Badge variant={s.status === 'completed' ? 'success' : 'running'}>
                  {s.status}
                </Badge>
              </div>
            ))}
          </div>
        </Card>

        <div className="lg:col-span-2 space-y-4">
          <span className="text-xs font-mono text-workbench-muted uppercase block">
            Worker Task Console Logs
          </span>
          <CodeBlock
            title="STDOUT / STDERR STREAM"
            language="log"
            code={`[2026-09-01T00:30:12Z] INFO: Initializing worker task ${activeJobId}
[2026-09-01T00:30:12Z] INFO: Validating project boundary ownership against tenant workspace
[2026-09-01T00:30:13Z] INFO: Parsed 250 evaluation records successfully from file payload
[2026-09-01T00:30:13Z] INFO: Writing dataset version checkpoint v1.0.0
[2026-09-01T00:30:14Z] SUCCESS: Job ${activeJobId} step 3 completed in 280ms`}
          />
        </div>
      </div>
    </div>
  );
}
