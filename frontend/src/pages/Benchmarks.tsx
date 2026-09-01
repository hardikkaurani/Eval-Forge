import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Activity, Plus, Search, Tag, ExternalLink } from 'lucide-react';
import { useWorkspace } from '../context/WorkspaceContext';
import { api } from '../services/api';
import type { Benchmark } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Input } from '../components/common/Input';
import { Dialog } from '../components/common/Dialog';
import { EmptyState } from '../components/common/EmptyState';

export default function Benchmarks() {
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProjectId } = useWorkspace();

  const activeProjectId = projectId || currentProjectId || '1';

  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  // New Benchmark Modal
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newBenchmarkName, setNewBenchmarkName] = useState('');
  const [newBenchmarkDesc, setNewBenchmarkDesc] = useState('');

  const loadBenchmarks = async () => {
    try {
      const list = await api.benchmarks.list(activeProjectId);
      setBenchmarks(list || []);
    } catch (err) {
      console.error('Failed to load benchmarks:', err);
    }
  };

  useEffect(() => {
    let isSubscribed = true;
    const load = async () => {
      try {
        const list = await api.benchmarks.list(activeProjectId);
        if (isSubscribed) {
          setBenchmarks(list || []);
        }
      } catch (err) {
        if (isSubscribed) console.error('Failed to load benchmarks:', err);
      }
    };
    load();
    return () => {
      isSubscribed = false;
    };
  }, [activeProjectId]);

  const handleCreateBenchmark = async () => {
    if (!newBenchmarkName.trim()) return;
    try {
      await api.benchmarks.create(
        {
          name: newBenchmarkName,
          description: newBenchmarkDesc,
          tags: ['benchmark', 'suite'],
        },
        activeProjectId
      );
      setNewBenchmarkName('');
      setNewBenchmarkDesc('');
      setIsCreateOpen(false);
      await loadBenchmarks();
    } catch (err) {
      console.error('Failed to create benchmark suite:', err);
    }
  };

  const filteredBenchmarks = benchmarks.filter(
    (b) =>
      b.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      b.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text">Benchmark Suites</h1>
          <p className="text-xs text-workbench-muted mt-1">
            Composite benchmark suites combining multiple datasets for standardized model
            evaluation.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsCreateOpen(true)}>
            New Suite
          </Button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center justify-between gap-4 bg-workbench-card p-3 rounded-md border border-workbench-border">
        <div className="w-full max-w-sm">
          <Input
            placeholder="Search benchmark suites..."
            leftIcon={Search}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="text-xs font-mono text-workbench-muted">
          Showing <strong>{filteredBenchmarks.length}</strong> suites
        </div>
      </div>

      {/* Benchmark Suites Grid */}
      {filteredBenchmarks.length === 0 ? (
        <EmptyState
          title="No benchmark suites found"
          description="Create your first composite benchmark suite to evaluate models across datasets."
          icon={Activity}
          action={
            <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsCreateOpen(true)}>
              Create Benchmark Suite
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredBenchmarks.map((b) => (
            <Card
              key={b.id}
              className="hover:border-brand-terracotta/40 transition-colors flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-brand-terracotta" />
                    <h3 className="text-sm font-bold text-workbench-text truncate">{b.name}</h3>
                  </div>
                  <Badge variant="running">{b.datasets_count || 2} Datasets</Badge>
                </div>
                <p className="text-xs text-workbench-muted line-clamp-2 leading-relaxed">
                  {b.description || 'No description provided.'}
                </p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(b.tags || ['standard', 'suite']).map((t) => (
                    <span
                      key={t}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-workbench-bg border border-workbench-border text-workbench-muted"
                    >
                      <Tag className="w-2.5 h-2.5" />
                      {t}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 mt-4 border-t border-workbench-border text-xs">
                <span className="text-workbench-muted font-mono text-[11px]">
                  Created {new Date(b.created_at || Date.now()).toLocaleDateString()}
                </span>
                <Button variant="ghost" size="sm" icon={ExternalLink}>
                  View Details
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Dialog
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Create Benchmark Suite"
        subtitle="Combine evaluation datasets into a composite testing suite"
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleCreateBenchmark}>
              Create Suite
            </Button>
          </>
        }
      >
        <div className="space-y-4 text-chrome-text">
          <Input
            label="Suite Name"
            placeholder="e.g. Enterprise RAG Compliance Suite"
            value={newBenchmarkName}
            onChange={(e) => setNewBenchmarkName(e.target.value)}
            variant="chrome"
          />
          <div className="space-y-1.5">
            <label className="block text-xs font-medium text-chrome-text">Description</label>
            <textarea
              rows={3}
              placeholder="Describe the composite evaluation goals..."
              value={newBenchmarkDesc}
              onChange={(e) => setNewBenchmarkDesc(e.target.value)}
              className="w-full text-xs rounded-md border border-chrome-border bg-well-bg p-3 text-chrome-text focus:outline-none focus:border-brand-sky"
            />
          </div>
        </div>
      </Dialog>
    </div>
  );
}
