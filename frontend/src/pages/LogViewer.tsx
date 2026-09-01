import { useState } from 'react';
import { Terminal, Search, Download } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { CodeBlock } from '../components/common/CodeBlock';

export default function LogViewer() {
  const [filter, setFilter] = useState('');

  const sampleLogs = `[INFO] 2026-09-01T00:35:01Z - Provider OpenAI route latencies verified (182ms)
[INFO] 2026-09-01T00:35:10Z - Evaluation pipeline 'Chatbot Alignment' initiated for project_id=1
[DEBUG] 2026-09-01T00:35:12Z - Batch prompt payload dispatched to gpt-4-turbo (50 cases)
[INFO] 2026-09-01T00:35:14Z - LLM-as-a-Judge completed scoring with aggregate_score=0.942
[WARN] 2026-09-01T00:35:15Z - Rate limit threshold warning: OpenAI API usage at 78% quota
[SUCCESS] 2026-09-01T00:35:16Z - Experiment pipeline run committed to database repository`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <Terminal className="w-5 h-5 text-brand-terracotta" />
            System & Evaluation Log Viewer
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Real-time inference log streams, judge response payloads, and audit events.
          </p>
        </div>
        <Button variant="outline" size="sm" icon={Download}>
          Export Logs (.txt)
        </Button>
      </div>

      {/* Log Terminal Container */}
      <Card padding="none">
        <div className="p-3 border-b border-workbench-border bg-workbench-bg flex items-center justify-between">
          <div className="w-full max-w-sm">
            <Input
              placeholder="Filter log stream by keyword..."
              leftIcon={Search}
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
          <span className="text-xs font-mono text-workbench-muted">Stream: Live</span>
        </div>
        <CodeBlock code={sampleLogs} language="log" maxHeight="max-h-[500px]" />
      </Card>
    </div>
  );
}
