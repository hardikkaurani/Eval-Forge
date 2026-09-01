import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Database, Plus, Search, Layers, Tag, ExternalLink } from 'lucide-react';
import { useWorkspace } from '../context/WorkspaceContext';
import { api } from '../services/api';
import type { Dataset } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Input } from '../components/common/Input';
import { Dialog } from '../components/common/Dialog';
import { EmptyState } from '../components/common/EmptyState';

export default function Datasets() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProjectId } = useWorkspace();

  const activeProjectId = projectId || currentProjectId || '1';

  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  // New Dataset Modal State
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newDatasetName, setNewDatasetName] = useState('');
  const [newDatasetDesc, setNewDatasetDesc] = useState('');

  const loadDatasets = async () => {
    try {
      const data = await api.datasets.list(activeProjectId);
      setDatasets(data || []);
    } catch (err) {
      console.error('Failed to load datasets:', err);
    }
  };

  useEffect(() => {
    let isSubscribed = true;
    const load = async () => {
      try {
        const data = await api.datasets.list(activeProjectId);
        if (isSubscribed) {
          setDatasets(data || []);
        }
      } catch (err) {
        if (isSubscribed) console.error('Failed to load datasets:', err);
      }
    };
    load();
    return () => {
      isSubscribed = false;
    };
  }, [activeProjectId]);

  const handleCreateDataset = async () => {
    if (!newDatasetName.trim()) return;
    try {
      await api.datasets.create(
        {
          name: newDatasetName,
          description: newDatasetDesc,
          tags: ['eval', 'custom'],
        },
        activeProjectId
      );
      setNewDatasetName('');
      setNewDatasetDesc('');
      setIsCreateOpen(false);
      await loadDatasets();
    } catch (err) {
      console.error('Failed to create dataset:', err);
    }
  };

  const filteredDatasets = datasets.filter(
    (d) =>
      d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text">
            Evaluation Datasets
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Golden evaluation datasets, record versions, and benchmark test cases.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsCreateOpen(true)}>
            New Dataset
          </Button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex items-center justify-between gap-4 bg-workbench-card p-3 rounded-md border border-workbench-border">
        <div className="w-full max-w-sm">
          <Input
            placeholder="Search datasets by name or tag..."
            leftIcon={Search}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="text-xs font-mono text-workbench-muted">
          Showing <strong>{filteredDatasets.length}</strong> datasets
        </div>
      </div>

      {/* Datasets Grid / List */}
      {filteredDatasets.length === 0 ? (
        <EmptyState
          title="No datasets found"
          description="Create your first dataset or import test cases via CSV/JSONL file."
          icon={Database}
          action={
            <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsCreateOpen(true)}>
              Create Dataset
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredDatasets.map((d) => (
            <Card
              key={d.id}
              className="hover:border-brand-terracotta/40 transition-colors flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    <Database className="w-4 h-4 text-brand-terracotta" />
                    <h3 className="text-sm font-bold text-workbench-text truncate">{d.name}</h3>
                  </div>
                  <Badge variant="sky">{d.visibility || 'private'}</Badge>
                </div>
                <p className="text-xs text-workbench-muted line-clamp-2 leading-relaxed">
                  {d.description || 'No description provided.'}
                </p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(d.tags || ['eval']).map((t) => (
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
                <div className="flex items-center gap-3 text-workbench-muted font-mono text-[11px]">
                  <span className="flex items-center gap-1">
                    <Layers className="w-3.5 h-3.5" /> {d.versions_count || 1} V
                  </span>
                  <span>•</span>
                  <span>{d.current_version || 'v1.0.0'}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  icon={ExternalLink}
                  onClick={() => navigate(`/projects/${activeProjectId}/datasets/${d.id}`)}
                >
                  Inspect
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Create Dataset Dialog Modal */}
      <Dialog
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Create New Dataset"
        subtitle="Initialize a new golden evaluation dataset container"
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleCreateDataset}>
              Create Dataset
            </Button>
          </>
        }
      >
        <div className="space-y-4 text-chrome-text">
          <Input
            label="Dataset Name"
            placeholder="e.g. Chatbot Alignment Golden Set"
            value={newDatasetName}
            onChange={(e) => setNewDatasetName(e.target.value)}
            variant="chrome"
          />
          <div className="space-y-1.5">
            <label className="block text-xs font-medium text-chrome-text">Description</label>
            <textarea
              rows={3}
              placeholder="Describe the target evaluation scenarios and record domain..."
              value={newDatasetDesc}
              onChange={(e) => setNewDatasetDesc(e.target.value)}
              className="w-full text-xs rounded-md border border-chrome-border bg-well-bg p-3 text-chrome-text focus:outline-none focus:border-brand-sky"
            />
          </div>
        </div>
      </Dialog>
    </div>
  );
}
