import { useState } from 'react';
import { KeyRound, Plus, Trash2, Globe, Loader2 } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Dialog } from '../components/common/Dialog';
import { Input } from '../components/common/Input';
import { CodeBlock } from '../components/common/CodeBlock';
import { api } from '../services/api';

export default function ApiWebhooks() {
  const [isKeyModalOpen, setIsKeyModalOpen] = useState(false);
  const [keyName, setKeyName] = useState('');
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [isCreatingKey, setIsCreatingKey] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [apiKeys, setApiKeys] = useState([
    { id: '1', name: 'CI/CD Pipeline Key', prefix: 'ef_live_9a8f...', created: '2026-08-15', lastUsed: '2 mins ago' },
    { id: '2', name: 'Local Dev Key', prefix: 'ef_live_3b1d...', created: '2026-08-20', lastUsed: '1 hour ago' },
  ]);

  const webhooks = [
    { id: 'wh-1', url: 'https://api.evalforge.ai/webhooks/eval-completed', events: ['experiment.completed'], status: 'active' },
  ];

  const handleOpenModal = () => {
    setGeneratedKey(null);
    setKeyName('');
    setErrorMsg(null);
    setIsKeyModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsKeyModalOpen(false);
    setKeyName('');
    setGeneratedKey(null);
    setErrorMsg(null);
  };

  const handleCreateKey = async () => {
    if (!keyName.trim()) return;
    setIsCreatingKey(true);
    setErrorMsg(null);

    try {
      const response = await api.enterprise.apiKeys.create({ name: keyName });
      const secret = response.api_key || response.raw_key || (response.data && response.data.api_key);
      if (secret) {
        setGeneratedKey(secret);
        setApiKeys((prev) => [
          ...prev,
          {
            id: response.details?.id || String(Date.now()),
            name: keyName,
            prefix: `${secret.substring(0, 12)}...`,
            created: new Date().toISOString().split('T')[0],
            lastUsed: 'Just now',
          },
        ]);
      } else {
        setErrorMsg('Server created key but did not return secret payload.');
      }
    } catch (err: unknown) {
      console.error('Failed to generate server API Key:', err);
      setErrorMsg('Failed to generate API Key from server endpoint. Please verify backend connectivity.');
    } finally {
      setIsCreatingKey(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <KeyRound className="w-5 h-5 text-brand-terracotta" />
            API Keys & Webhooks Subscriptions
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Generate programmatic access credentials and configure real-time HTTP webhook callbacks.
          </p>
        </div>
        <Button variant="primary" size="sm" icon={Plus} onClick={handleOpenModal}>
          Generate API Key
        </Button>
      </div>

      {/* API Keys Table */}
      <Card title="Workspace API Keys" subtitle="Secret keys used to authenticate REST API requests" padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">Key Identifier</th>
                <th className="px-5 py-3 font-medium">Key Prefix</th>
                <th className="px-5 py-3 font-medium">Created Date</th>
                <th className="px-5 py-3 font-medium">Last Activity</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {apiKeys.map((k) => (
                <tr key={k.id} className="hover:bg-workbench-card/50 transition-colors">
                  <td className="px-5 py-3.5 font-semibold text-workbench-text">{k.name}</td>
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">{k.prefix}</td>
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">{k.created}</td>
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">{k.lastUsed}</td>
                  <td className="px-5 py-3.5 text-right">
                    <Button variant="ghost" size="sm" icon={Trash2}>Revoke</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Webhooks Section */}
      <Card title="Webhook Endpoints" subtitle="Receive HTTP POST payloads when evaluation pipeline events trigger">
        <div className="space-y-3">
          {webhooks.map((w) => (
            <div key={w.id} className="flex items-center justify-between p-3 rounded bg-workbench-bg border border-workbench-border text-xs">
              <div className="flex items-center gap-2 font-mono text-[11px]">
                <Globe className="w-4 h-4 text-brand-terracotta" />
                <span className="text-workbench-text font-semibold">{w.url}</span>
              </div>
              <Badge variant="success">{w.status}</Badge>
            </div>
          ))}
        </div>
      </Card>

      {/* Key Modal */}
      <Dialog
        isOpen={isKeyModalOpen}
        onClose={handleCloseModal}
        title="Generate New Secret API Key"
        subtitle="Make sure to copy your API key now; you won't be able to see it again."
      >
        {generatedKey ? (
          <div className="space-y-4">
            <span className="text-xs font-mono text-emerald-400 block font-semibold">API Key Generated Successfully (One-Time Reveal):</span>
            <CodeBlock code={generatedKey} language="text" />
            <Button variant="primary" size="sm" onClick={handleCloseModal}>Done & Erase Secret from Memory</Button>
          </div>
        ) : (
          <div className="space-y-4 text-chrome-text">
            {errorMsg && (
              <div className="p-3 bg-red-900/30 border border-red-500/50 rounded text-xs text-red-300 font-mono">
                {errorMsg}
              </div>
            )}
            <Input
              label="Key Description"
              placeholder="e.g. Staging Evaluation Runner"
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              variant="chrome"
            />
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="ghost" size="sm" onClick={handleCloseModal}>Cancel</Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleCreateKey}
                disabled={isCreatingKey || !keyName.trim()}
              >
                {isCreatingKey ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" /> Generating...
                  </span>
                ) : (
                  'Generate Key'
                )}
              </Button>
            </div>
          </div>
        )}
      </Dialog>
    </div>
  );
}
