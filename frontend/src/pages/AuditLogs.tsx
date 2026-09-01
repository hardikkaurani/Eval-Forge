import { HardDrive, Download } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

export default function AuditLogs() {
  const auditEvents = [
    {
      id: 'aud-101',
      action: 'DATASET_VERSION_CREATED',
      actor: 'engineer@evalforge.ai',
      ip: '192.168.1.45',
      time: '2026-09-01 00:24:10',
    },
    {
      id: 'aud-102',
      action: 'EXPERIMENT_PIPELINE_EXECUTED',
      actor: 'architect@evalforge.ai',
      ip: '192.168.1.12',
      time: '2026-09-01 00:15:30',
    },
    {
      id: 'aud-103',
      action: 'API_KEY_GENERATED',
      actor: 'engineer@evalforge.ai',
      ip: '192.168.1.45',
      time: '2026-08-31 23:50:00',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-brand-terracotta" />
            Security & Compliance Audit Trail
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Immutable workspace audit events, administrative actions, and authorization logs.
          </p>
        </div>
        <Button variant="outline" size="sm" icon={Download}>
          Export Audit Trail (.csv)
        </Button>
      </div>

      {/* Audit Table */}
      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">Audit Event ID</th>
                <th className="px-5 py-3 font-medium">Action Event</th>
                <th className="px-5 py-3 font-medium">Actor User</th>
                <th className="px-5 py-3 font-medium">Client IP</th>
                <th className="px-5 py-3 font-medium text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {auditEvents.map((a) => (
                <tr key={a.id} className="hover:bg-workbench-card/50 transition-colors">
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">{a.id}</td>
                  <td className="px-5 py-3.5 font-mono text-[11px] font-semibold text-workbench-text">
                    {a.action}
                  </td>
                  <td className="px-5 py-3.5 text-workbench-text">{a.actor}</td>
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">{a.ip}</td>
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted text-right">
                    {a.time}
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
