import { Cpu, Server, Activity } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { MetricCard } from '../components/common/MetricCard';

export default function SystemSettings() {
  const nodes = [
    {
      id: 'node-worker-01',
      cpu: '14%',
      memory: '2.4 GB / 8.0 GB',
      tasks: '12 active',
      status: 'healthy',
    },
    {
      id: 'node-worker-02',
      cpu: '28%',
      memory: '3.8 GB / 8.0 GB',
      tasks: '18 active',
      status: 'healthy',
    },
    {
      id: 'node-worker-03',
      cpu: '8%',
      memory: '1.2 GB / 8.0 GB',
      tasks: '4 active',
      status: 'healthy',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-workbench-border pb-4">
        <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
          <Server className="w-5 h-5 text-brand-terracotta" />
          System Settings & Node Telemetry
        </h1>
        <p className="text-xs text-workbench-muted mt-1">
          Cluster health, worker node pool memory telemetry, and queue depth monitoring.
        </p>
      </div>

      {/* Cluster Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard
          title="Active Worker Nodes"
          value="3 Nodes"
          subtitle="All nodes healthy"
          icon={Server}
        />
        <MetricCard
          title="Queue Depth"
          value="0 Tasks"
          subtitle="No queue backlog"
          icon={Activity}
        />
        <MetricCard title="Cluster CPU Load" value="16.6%" subtitle="P95 load metric" icon={Cpu} />
      </div>

      {/* Nodes Table */}
      <Card padding="none" title="Worker Pool Node Telemetry">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">Node ID</th>
                <th className="px-5 py-3 font-medium">CPU Load</th>
                <th className="px-5 py-3 font-medium">Memory Used</th>
                <th className="px-5 py-3 font-medium">Active Tasks</th>
                <th className="px-5 py-3 font-medium">Health Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {nodes.map((n) => (
                <tr key={n.id} className="hover:bg-workbench-card/50 transition-colors">
                  <td className="px-5 py-3.5 font-mono font-semibold text-workbench-text">
                    {n.id}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-workbench-muted">{n.cpu}</td>
                  <td className="px-5 py-3.5 font-mono text-workbench-muted">{n.memory}</td>
                  <td className="px-5 py-3.5 font-mono text-workbench-muted">{n.tasks}</td>
                  <td className="px-5 py-3.5">
                    <Badge variant="success">{n.status}</Badge>
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
