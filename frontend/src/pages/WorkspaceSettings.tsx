import { useState } from 'react';
import { Settings, Save } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';

export default function WorkspaceSettings() {
  const [wsName, setWsName] = useState('Eval-Forge Core Workspace');
  const [orgDomain, setOrgDomain] = useState('evalforge.ai');
  const [defaultJudge, setDefaultJudge] = useState('gpt-4-turbo');

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <Settings className="w-5 h-5 text-brand-terracotta" />
            Workspace Settings & Configuration
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Configure organization domain policies, default evaluators, and project defaults.
          </p>
        </div>
        <Button variant="primary" size="sm" icon={Save}>
          Save Settings
        </Button>
      </div>

      <Card title="Organization Identity" subtitle="General workspace parameters">
        <div className="space-y-4">
          <Input
            label="Workspace Name"
            value={wsName}
            onChange={(e) => setWsName(e.target.value)}
          />
          <Input
            label="Verified Organization Domain"
            value={orgDomain}
            onChange={(e) => setOrgDomain(e.target.value)}
          />
        </div>
      </Card>

      <Card
        title="Default Evaluator Configuration"
        subtitle="Default LLM judge parameters for new experiments"
      >
        <div className="space-y-1.5">
          <label className="block text-xs font-medium text-workbench-text">
            Default Judge Evaluator
          </label>
          <select
            value={defaultJudge}
            onChange={(e) => setDefaultJudge(e.target.value)}
            className="w-full text-xs rounded-md border border-workbench-border bg-white p-2.5 text-workbench-text focus:outline-none"
          >
            <option value="gpt-4-turbo">GPT-4 Turbo (High Precision)</option>
            <option value="claude-3-5-sonnet">Claude 3.5 Sonnet (Reasoning)</option>
            <option value="llama-3-70b">Llama 3 70B (Open Weights)</option>
          </select>
        </div>
      </Card>
    </div>
  );
}
