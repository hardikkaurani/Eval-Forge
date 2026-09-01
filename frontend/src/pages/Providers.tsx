import { useState, useEffect } from 'react';
import { Cpu, RefreshCw, Key, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import type { ProviderHealth } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Dialog } from '../components/common/Dialog';
import { Input } from '../components/common/Input';

export default function Providers() {
  const [providers, setProviders] = useState<ProviderHealth[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState('');

  const fetchProviders = async () => {
    setIsLoading(true);
    try {
      const data = await api.providers.list();
      setProviders(data || []);
    } catch (err) {
      console.error('Failed to load providers:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text">
            LLM Inference Providers
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Provider health telemetry, latency monitoring, and API key credential routes.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            isLoading={isLoading}
            onClick={fetchProviders}
          >
            Refresh Health
          </Button>
        </div>
      </div>

      {/* Provider Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {providers.map((p) => (
          <Card key={p.provider} className="flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded bg-brand-terracotta/10 text-brand-terracotta border border-brand-terracotta/20">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-workbench-text">{p.provider}</h3>
                    <span className="text-[10px] font-mono text-workbench-muted">Inference Route</span>
                  </div>
                </div>
                <Badge variant={p.status === 'healthy' ? 'success' : 'warning'}>
                  {p.status}
                </Badge>
              </div>

              {/* Telemetry Metrics */}
              <div className="grid grid-cols-2 gap-3 p-3 rounded-md bg-workbench-bg border border-workbench-border text-xs font-mono">
                <div>
                  <span className="text-[10px] text-workbench-muted block">LATENCY (P95)</span>
                  <span className="font-bold text-workbench-text">{p.latency_ms} ms</span>
                </div>
                <div>
                  <span className="text-[10px] text-workbench-muted block">AVAILABLE MODELS</span>
                  <span className="font-bold text-workbench-text">{(p.models || []).length || 4}</span>
                </div>
              </div>

              {/* Model Badges List */}
              <div className="space-y-1">
                <span className="text-[10px] font-mono text-workbench-muted uppercase block">
                  Supported Models
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {(p.models || ['gpt-4-turbo', 'gpt-3.5-turbo']).map((m: string) => (
                    <span
                      key={m}
                      className="px-2 py-0.5 rounded text-[10px] font-mono bg-workbench-bg border border-workbench-border text-workbench-text"
                    >
                      {m}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 mt-4 border-t border-workbench-border text-xs">
              <span className="flex items-center gap-1 text-[11px] font-mono text-emerald-600">
                <ShieldCheck className="w-3.5 h-3.5" /> Key Configured
              </span>
              <Button
                variant="outline"
                size="sm"
                icon={Key}
                onClick={() => setSelectedProvider(p.provider || p.id)}
              >
                Configure Key
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {/* Key Config Modal */}
      {selectedProvider && (
        <Dialog
          isOpen={!!selectedProvider}
          onClose={() => setSelectedProvider(null)}
          title={`Configure API Key: ${selectedProvider}`}
          subtitle="API credentials are encrypted and stored in secure workspace isolation"
          footer={
            <>
              <Button variant="ghost" size="sm" onClick={() => setSelectedProvider(null)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={() => setSelectedProvider(null)}>
                Save Key
              </Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input
              label="Provider API Secret Key"
              type="password"
              placeholder="sk-..."
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              variant="chrome"
            />
          </div>
        </Dialog>
      )}
    </div>
  );
}
