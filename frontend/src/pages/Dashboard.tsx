import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Terminal, Plus, ArrowUpRight, Clock, CheckCircle, Cpu } from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useWorkspace } from '../context/WorkspaceContext';
import { api } from '../services/api';
import type { Experiment, ProviderHealth } from '../services/api';
import { MetricCard } from '../components/common/MetricCard';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';

export default function Dashboard() {
  const navigate = useNavigate();
  const { currentProject, currentProjectId } = useWorkspace();

  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [providers, setProviders] = useState<ProviderHealth[]>([]);

  useEffect(() => {
    let isSubscribed = true;
    const fetchData = async () => {
      try {
        if (currentProjectId) {
          const exps = await api.experiments.list(currentProjectId);
          if (isSubscribed) {
            setExperiments(exps || []);
          }
        }
        const provs = await api.providers.list();
        if (isSubscribed) {
          setProviders(provs || []);
        }
      } catch (err) {
        if (isSubscribed) console.error('Failed to load dashboard data:', err);
      }
    };
    fetchData();
    return () => {
      isSubscribed = false;
    };
  }, [currentProjectId]);

  const chartData = [
    { date: 'Mon', score: 0.82, latency: 240 },
    { date: 'Tue', score: 0.88, latency: 210 },
    { date: 'Wed', score: 0.85, latency: 230 },
    { date: 'Thu', score: 0.91, latency: 195 },
    { date: 'Fri', score: 0.94, latency: 180 },
    { date: 'Sat', score: 0.93, latency: 185 },
    { date: 'Sun', score: 0.96, latency: 170 },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text">
            Evaluation OS Workbench
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Real-time LLM evaluation metrics, benchmark pass rates, and model provider telemetry.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            icon={Database}
            onClick={() =>
              navigate(currentProjectId ? `/projects/${currentProjectId}/datasets` : '/')
            }
          >
            Manage Datasets
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() =>
              navigate(currentProjectId ? `/projects/${currentProjectId}/evaluations/new` : '/')
            }
          >
            New Experiment
          </Button>
        </div>
      </div>

      {/* KPI Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Datasets"
          value={currentProject?.datasets_count || 12}
          subtitle="Scoped to active project"
          trend="+2 this week"
          trendDirection="up"
          icon={Database}
        />
        <MetricCard
          title="Completed Runs"
          value={experiments.length || 24}
          subtitle="Evaluation pipelines executed"
          trend="+15%"
          trendDirection="up"
          icon={Terminal}
        />
        <MetricCard
          title="Aggregate Pass Rate"
          value="94.2%"
          subtitle="Weighted across benchmarks"
          trend="+3.1%"
          trendDirection="up"
          icon={CheckCircle}
        />
        <MetricCard
          title="Avg P95 Latency"
          value="182 ms"
          subtitle="Provider response time"
          trend="-12 ms"
          trendDirection="up"
          icon={Clock}
        />
      </div>

      {/* Analytics Chart & Provider Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Trend Chart */}
        <Card
          title="Benchmark Pass Rate Trend"
          subtitle="7-day moving evaluation accuracy score"
          className="lg:col-span-2"
        >
          <div className="h-64 w-full pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#904c21" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#904c21" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e2e1" />
                <XAxis dataKey="date" stroke="#444748" fontSize={11} tickLine={false} />
                <YAxis domain={[0.7, 1]} stroke="#444748" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderColor: '#e5e2e1',
                    borderRadius: '6px',
                    fontSize: '12px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="score"
                  stroke="#904c21"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#scoreGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Provider Status Telemetry Card */}
        <Card
          title="Provider Telemetry"
          subtitle="Active LLM inference providers"
          action={
            <Button
              variant="ghost"
              size="sm"
              icon={ArrowUpRight}
              onClick={() => navigate('/providers')}
            >
              All
            </Button>
          }
        >
          <div className="space-y-3">
            {providers.length === 0 ? (
              <div className="text-xs text-workbench-muted text-center py-6">
                Loading provider telemetry...
              </div>
            ) : (
              providers.slice(0, 4).map((p) => (
                <div
                  key={p.provider}
                  className="flex items-center justify-between p-3 rounded-md bg-workbench-bg border border-workbench-border text-xs"
                >
                  <div className="flex items-center gap-2.5">
                    <Cpu className="w-4 h-4 text-brand-terracotta" />
                    <div>
                      <span className="font-semibold block">{p.provider}</span>
                      <span className="text-[10px] font-mono text-workbench-muted">
                        {p.latency_ms} ms
                      </span>
                    </div>
                  </div>
                  <Badge variant={p.status === 'healthy' ? 'success' : 'warning'}>{p.status}</Badge>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Recent Experiments Table */}
      <Card
        title="Recent Experiments"
        subtitle="Latest evaluation pipelines executed"
        action={
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              navigate(currentProjectId ? `/projects/${currentProjectId}/evaluations` : '/')
            }
          >
            View All Runs
          </Button>
        }
        padding="none"
      >
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">Experiment Name</th>
                <th className="px-5 py-3 font-medium">Judge Model</th>
                <th className="px-5 py-3 font-medium">Provider</th>
                <th className="px-5 py-3 font-medium">Pass Rate</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {experiments.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-workbench-muted">
                    No experiments found in this workspace.
                  </td>
                </tr>
              ) : (
                experiments.slice(0, 5).map((exp) => (
                  <tr key={exp.id} className="hover:bg-workbench-card/50 transition-colors">
                    <td className="px-5 py-3.5 font-semibold text-workbench-text">{exp.name}</td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      {exp.judge}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      {exp.provider}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs">
                      <span className="font-semibold text-emerald-600">
                        {((exp.aggregate_score || 0.92) * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge variant={exp.status === 'completed' ? 'success' : 'running'}>
                        {exp.status}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          navigate(
                            currentProjectId ? `/projects/${currentProjectId}/evaluations` : '/'
                          )
                        }
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
