import { ShieldAlert, AlertTriangle, ShieldCheck, Lock, Eye } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { MetricCard } from '../components/common/MetricCard';

export default function AiSafety() {
  const violations = [
    { id: 'v-101', type: 'PROMPT_INJECTION', severity: 'HIGH', model: 'gpt-3.5-turbo', blocked: true, time: '10 mins ago' },
    { id: 'v-102', type: 'PII_LEAKAGE_ATTEMPT', severity: 'MEDIUM', model: 'claude-3-haiku', blocked: true, time: '1 hour ago' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-workbench-border pb-4">
        <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-brand-terracotta" />
          AI Safety & Toxicity Guardrails
        </h1>
        <p className="text-xs text-workbench-muted mt-1">
          Automated prompt injection testing, PII leakage detection, and jailbreak defense evaluation.
        </p>
      </div>

      {/* Safety Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Jailbreak Resistance"
          value="99.2%"
          subtitle="Prompt injection defense"
          trend="+0.4%"
          trendDirection="up"
          icon={ShieldCheck}
        />
        <MetricCard
          title="PII Protection"
          value="100.0%"
          subtitle="Zero data leakages"
          trend="Stable"
          trendDirection="neutral"
          icon={Lock}
        />
        <MetricCard
          title="Toxicity Trigger Rate"
          value="0.04%"
          subtitle="Harmful output generation"
          trend="-0.01%"
          trendDirection="up"
          icon={AlertTriangle}
        />
        <MetricCard
          title="Guardrail Latency"
          value="14 ms"
          subtitle="Inline filter overhead"
          trend="-2 ms"
          trendDirection="up"
          icon={Eye}
        />
      </div>

      {/* Violations Log */}
      <Card padding="none" title="Blocked Guardrail Incidents">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">Incident ID</th>
                <th className="px-5 py-3 font-medium">Violation Type</th>
                <th className="px-5 py-3 font-medium">Target Model</th>
                <th className="px-5 py-3 font-medium">Severity</th>
                <th className="px-5 py-3 font-medium">Action Handled</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {violations.map((v) => (
                <tr key={v.id} className="hover:bg-workbench-card/50 transition-colors">
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">{v.id}</td>
                  <td className="px-5 py-3.5 font-mono font-semibold text-workbench-text">{v.type}</td>
                  <td className="px-5 py-3.5 font-mono text-workbench-muted">{v.model}</td>
                  <td className="px-5 py-3.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-red-500/10 text-red-600 border border-red-500/20 font-semibold">
                      {v.severity}
                    </span>
                  </td>
                  <td className="px-5 py-3.5">
                    <Badge variant="success">BLOCKED_INLINE</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
