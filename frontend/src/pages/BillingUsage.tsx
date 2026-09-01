import { CreditCard, Info } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';

export default function BillingUsage() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="border-b border-workbench-border pb-4">
        <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-brand-terracotta" />
          License Tier & Token Usage Telemetry
        </h1>
        <p className="text-xs text-workbench-muted mt-1">
          Monitor evaluation token consumption, provider quota limits, and enterprise subscription
          tier.
        </p>
      </div>

      {/* Backend Gap Isolated Notice */}
      <div className="p-4 rounded-md bg-amber-500/10 border border-amber-500/20 text-xs text-amber-800 dark:text-amber-300 flex items-start gap-3">
        <Info className="w-4 h-4 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold block mb-0.5">Backend Capability Gap Notice</span>
          <span>
            Billing and subscription management is isolated on static frontend contracts. Live
            backend billing APIs are reserved for enterprise SaaS licensing modules.
          </span>
        </div>
      </div>

      {/* License Tier */}
      <Card title="Current Subscription Tier" subtitle="Organization license entitlement">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-lg font-bold text-workbench-text block">
              Enterprise Dedicated License
            </span>
            <span className="text-xs text-workbench-muted">
              Unlimited evaluation projects & concurrent worker nodes
            </span>
          </div>
          <Badge variant="success">Active</Badge>
        </div>
      </Card>

      {/* Usage Gauges */}
      <Card title="Evaluation Token Quota Usage" subtitle="Monthly evaluation token allocation">
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs font-mono">
            <span className="text-workbench-text font-semibold">5,420,000 / 10,000,000 Tokens</span>
            <span className="text-brand-terracotta font-bold">54.2% Used</span>
          </div>
          <div className="w-full bg-workbench-bg h-3 rounded-full overflow-hidden border border-workbench-border">
            <div className="bg-brand-terracotta h-full rounded-full" style={{ width: '54.2%' }} />
          </div>
        </div>
      </Card>
    </div>
  );
}
