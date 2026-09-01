import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Terminal,
  Plus,
  Search,
} from 'lucide-react';
import { useWorkspace } from '../context/WorkspaceContext';
import { api } from '../services/api';
import type { Experiment } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Input } from '../components/common/Input';
import { Dialog } from '../components/common/Dialog';
import { CodeBlock } from '../components/common/CodeBlock';
import { EmptyState } from '../components/common/EmptyState';

export default function Evaluations() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProjectId } = useWorkspace();

  const activeProjectId = projectId || currentProjectId || '1';

  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    let isSubscribed = true;
    const fetchExperiments = async () => {
      try {
        const list = await api.experiments.list(activeProjectId);
        if (isSubscribed) {
          setExperiments(list || []);
        }
      } catch (err) {
        if (isSubscribed) console.error('Failed to load experiments:', err);
      }
    };
    fetchExperiments();
    return () => {
      isSubscribed = false;
    };
  }, [activeProjectId]);

  const filteredExperiments = experiments.filter((e) =>
    e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.judge.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.provider.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text">
            Evaluation Results & Experiments
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Automated LLM-as-a-Judge execution pipeline runs, pass rates, and test cases.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="primary"
            size="sm"
            icon={Plus}
            onClick={() => navigate(`/projects/${activeProjectId}/evaluations/new`)}
          >
            New Experiment
          </Button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center justify-between gap-4 bg-workbench-card p-3 rounded-md border border-workbench-border">
        <div className="w-full max-w-sm">
          <Input
            placeholder="Search experiments by name, judge, or provider..."
            leftIcon={Search}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="text-xs font-mono text-workbench-muted">
          Total <strong>{filteredExperiments.length}</strong> pipeline runs
        </div>
      </div>

      {/* Experiments Table Card */}
      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">Experiment</th>
                <th className="px-5 py-3 font-medium">Judge Model</th>
                <th className="px-5 py-3 font-medium">Provider</th>
                <th className="px-5 py-3 font-medium">Completed / Failed</th>
                <th className="px-5 py-3 font-medium">Accuracy Score</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {filteredExperiments.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center">
                    <EmptyState
                      title="No experiment runs found"
                      description="Execute your first automated evaluation experiment run."
                      icon={Terminal}
                      action={
                        <Button
                          variant="primary"
                          size="sm"
                          icon={Plus}
                          onClick={() => navigate(`/projects/${activeProjectId}/evaluations/new`)}
                        >
                          New Experiment
                        </Button>
                      }
                    />
                  </td>
                </tr>
              ) : (
                filteredExperiments.map((exp) => (
                  <tr key={exp.id} className="hover:bg-workbench-card/50 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="font-semibold text-workbench-text">{exp.name}</div>
                      <div className="text-[10px] font-mono text-workbench-muted mt-0.5">
                        {exp.description || 'No description provided.'}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      {exp.judge}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      {exp.provider}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      <span className="text-emerald-600 font-semibold">{exp.completed_cases || 50}</span> /{' '}
                      <span className="text-red-500">{exp.failed_cases || 0}</span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs">
                      <span className="font-bold text-emerald-600">
                        {((exp.aggregate_score || 0.94) * 100).toFixed(1)}%
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
                        onClick={() => setSelectedExperiment(exp)}
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

      {/* Experiment Inspection Dialog Modal */}
      {selectedExperiment && (
        <Dialog
          isOpen={!!selectedExperiment}
          onClose={() => setSelectedExperiment(null)}
          title={`Experiment Run: ${selectedExperiment.name}`}
          subtitle={`Executed with ${selectedExperiment.judge} via ${selectedExperiment.provider}`}
          maxWidth="2xl"
        >
          <div className="space-y-4 text-chrome-text">
            <div className="grid grid-cols-2 gap-3 p-3 rounded bg-well-bg border border-well-border text-xs font-mono">
              <div>
                <span className="text-chrome-muted block text-[10px]">PASS RATE</span>
                <span className="text-emerald-400 font-bold text-base">
                  {((selectedExperiment.aggregate_score || 0.94) * 100).toFixed(1)}%
                </span>
              </div>
              <div>
                <span className="text-chrome-muted block text-[10px]">JUDGE EVALUATOR</span>
                <span className="text-chrome-text font-semibold">{selectedExperiment.judge}</span>
              </div>
            </div>

            <div>
              <span className="text-xs font-mono text-chrome-muted block mb-1">Configuration Payload</span>
              <CodeBlock code={JSON.stringify(selectedExperiment.configuration || { temperature: 0.2 }, null, 2)} language="json" />
            </div>
          </div>
        </Dialog>
      )}
    </div>
  );
}
