import { SlidersHorizontal, ShieldCheck, Plus } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';

export default function PolicyEvaluation() {
  const policies = [
    { id: 'pol-1', name: 'System Prompt Output Format Adherence', rule: 'Must conform strictly to valid JSON output schema', compliance: '98.9%' },
    { id: 'pol-2', name: 'GDPR / Privacy Compliance Rule', rule: 'Must not return user email or PII in candidate output', compliance: '100.0%' },
    { id: 'pol-3', name: 'Brand Tone & Style Guide Policy', rule: 'Must maintain professional enterprise tone without informal slang', compliance: '95.4%' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <SlidersHorizontal className="w-5 h-5 text-brand-terracotta" />
            Policy Evaluation & Compliance Rules
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Enforce enterprise compliance rules, system prompt adherence, and custom policy validators.
          </p>
        </div>
        <Button variant="primary" size="sm" icon={Plus}>
          Add Policy Rule
        </Button>
      </div>

      {/* Policies List */}
      <div className="space-y-4">
        {policies.map((p) => (
          <Card key={p.id} padding="md">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <h3 className="text-sm font-bold text-workbench-text">{p.name}</h3>
                </div>
                <p className="text-xs text-workbench-muted font-mono">{p.rule}</p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right font-mono">
                  <span className="text-[10px] text-workbench-muted block">COMPLIANCE SCORE</span>
                  <span className="font-bold text-emerald-600 text-sm">{p.compliance}</span>
                </div>
                <Badge variant="success">enforced</Badge>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
