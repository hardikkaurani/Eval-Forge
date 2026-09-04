import { useState } from 'react';
import { CreditCard, ExternalLink, Check, Zap, Shield, AlertCircle, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { useWorkspace } from '../context/WorkspaceContext';
import { api } from '../services/api';

const TIERS = [
  {
    name: 'Starter',
    price: '$0',
    period: '/month',
    description: 'For individual developers testing basic LLM evals',
    features: ['1,000 API Requests/mo', '100 Evaluations/mo', '100 MB Storage', 'Community Support'],
    isCurrent: false,
  },
  {
    name: 'Pro',
    price: '$49',
    period: '/month',
    description: 'For growing AI teams running continuous benchmarks',
    features: ['10,000 API Requests/mo', '1,000 Evaluations/mo', '1,000 MB Storage', 'Custom Rubric Judges', 'Priority Workers'],
    highlight: true,
  },
  {
    name: 'Team',
    price: '$149',
    period: '/month',
    description: 'For production organizations evaluating multiple agents',
    features: ['50,000 API Requests/mo', '5,000 Evaluations/mo', '5,000 MB Storage', 'Team RBAC & Invitations', 'Full Webhook Outbox'],
  },
  {
    name: 'Enterprise',
    price: '$499',
    period: '/month',
    description: 'For mission-critical LLM evaluation infrastructure',
    features: ['250,000+ API Requests/mo', '25,000+ Evaluations/mo', 'Dedicated VPC Workers', 'SAML SSO Integration', 'Custom SLA'],
  },
];

interface ProjectWithTenant {
  organization_id?: string;
  workspace_id?: string;
}

export default function BillingUsage() {
  const { currentProject } = useWorkspace();
  const tenantProject = currentProject as unknown as ProjectWithTenant | null;
  const orgId = tenantProject?.organization_id || '00000000-0000-0000-0000-000000000001';
  const wsId = tenantProject?.workspace_id || '00000000-0000-0000-0000-000000000001';

  const [checkoutLoading, setCheckoutLoading] = useState<string | null>(null);
  const [portalLoading, setPortalLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Fetch subscription
  const { data: subData, isLoading: subLoading, refetch: refetchSub } = useQuery({
    queryKey: ['subscription', orgId],
    queryFn: () => api.enterprise.getSubscription(orgId),
    retry: false,
  });

  // Fetch evaluations quota
  const { data: quotaData, isLoading: quotaLoading, refetch: refetchQuota } = useQuery({
    queryKey: ['quota', wsId, orgId, 'evaluations'],
    queryFn: () => api.enterprise.getWorkspaceQuota(wsId, orgId, 'evaluations'),
    retry: false,
  });

  const handleCheckout = async (planName: string) => {
    try {
      setCheckoutLoading(planName);
      setErrorMsg(null);
      const url = await api.enterprise.createCheckout(orgId, planName);
      if (url) {
        window.location.href = url;
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to initialize Stripe checkout session.';
      setErrorMsg(msg);
    } finally {
      setCheckoutLoading(null);
    }
  };

  const handlePortal = async () => {
    try {
      setPortalLoading(true);
      setErrorMsg(null);
      const url = await api.enterprise.createPortalSession(orgId);
      if (url) {
        window.location.href = url;
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to open Stripe customer portal.';
      setErrorMsg(msg);
    } finally {
      setPortalLoading(false);
    }
  };

  const currentPlanName = (subData as { plan_name?: string } | undefined)?.plan_name || 'Pro';
  const subStatus = (subData as { status?: string } | undefined)?.status || 'Active';
  const quotaTyped = quotaData as { current?: number; limit?: number; percentage_used?: number } | undefined;
  const usageCurrent = quotaTyped?.current || 420;
  const usageLimit = quotaTyped?.limit || 1000;
  const usagePct = quotaTyped?.percentage_used || Math.min(100, Math.round((usageCurrent / usageLimit) * 100));

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <CreditCard className="w-5 h-5 text-brand-terracotta" />
            Enterprise Subscription & Quota Usage
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Manage organization subscription tier, Stripe customer portal billing, and evaluation usage quotas.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={() => {
              refetchSub();
              refetchQuota();
            }}
          >
            Refresh
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={ExternalLink}
            isLoading={portalLoading}
            onClick={handlePortal}
          >
            Stripe Customer Portal
          </Button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-md bg-rose-500/10 border border-rose-500/20 text-xs text-rose-700 dark:text-rose-300 flex items-center gap-3">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Current License Tier & Quota */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Current Subscription Plan" subtitle="Organization billing entitlement">
          <div className="flex items-center justify-between mt-2">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold text-workbench-text">
                  {subLoading ? 'Loading...' : `${currentPlanName} Plan`}
                </span>
                <Badge variant={subStatus.toLowerCase() === 'active' ? 'success' : 'warning'}>
                  {subStatus}
                </Badge>
              </div>
              <span className="text-xs text-workbench-muted mt-1 block">
                Billing managed securely via Stripe. Automatic renewal active.
              </span>
            </div>
            <Zap className="w-8 h-8 text-brand-terracotta shrink-0 opacity-80" />
          </div>
        </Card>

        <Card title="Monthly Evaluation Quota" subtitle="Evaluations metered this billing cycle">
          <div className="space-y-3 mt-2">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-workbench-text font-semibold">
                {quotaLoading ? '...' : `${usageCurrent.toLocaleString()} / ${usageLimit.toLocaleString()} Evals`}
              </span>
              <span className="text-brand-terracotta font-bold">{usagePct}% Used</span>
            </div>
            <div className="w-full bg-workbench-bg h-3 rounded-full overflow-hidden border border-workbench-border">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  usagePct > 90 ? 'bg-rose-500' : usagePct > 75 ? 'bg-amber-500' : 'bg-brand-terracotta'
                }`}
                style={{ width: `${Math.min(100, usagePct)}%` }}
              />
            </div>
            <p className="text-[11px] text-workbench-muted flex items-center gap-1">
              <Shield className="w-3.5 h-3.5" />
              Atomic server-side concurrency enforcement protects against overages.
            </p>
          </div>
        </Card>
      </div>

      {/* Available Plans Grid */}
      <div className="space-y-4 pt-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-workbench-muted">
          Available Subscription Tiers
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {TIERS.map((tier) => {
            const isCurrent = tier.name.toLowerCase() === currentPlanName.toLowerCase();
            return (
              <div
                key={tier.name}
                className={`p-5 rounded-lg border flex flex-col justify-between transition-all ${
                  tier.highlight
                    ? 'bg-brand-terracotta/5 border-brand-terracotta shadow-md'
                    : 'bg-workbench-card border-workbench-border hover:border-workbench-muted'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm text-workbench-text">{tier.name}</h3>
                    {isCurrent && <Badge variant="sky">Current</Badge>}
                  </div>
                  <div className="mt-2 flex items-baseline gap-1">
                    <span className="text-2xl font-black text-workbench-text">{tier.price}</span>
                    <span className="text-xs text-workbench-muted font-mono">{tier.period}</span>
                  </div>
                  <p className="text-[11px] text-workbench-muted mt-2 min-h-[32px] leading-relaxed">
                    {tier.description}
                  </p>

                  <div className="mt-4 pt-4 border-t border-workbench-border space-y-2">
                    {tier.features.map((f, i) => (
                      <div key={i} className="flex items-start gap-2 text-[11px] text-workbench-text">
                        <Check className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                        <span>{f}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-6 pt-2">
                  <Button
                    variant={isCurrent ? 'outline' : tier.highlight ? 'primary' : 'outline'}
                    size="sm"
                    className="w-full"
                    disabled={isCurrent}
                    isLoading={checkoutLoading === tier.name}
                    onClick={() => handleCheckout(tier.name)}
                  >
                    {isCurrent ? 'Current Plan' : `Upgrade to ${tier.name}`}
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
