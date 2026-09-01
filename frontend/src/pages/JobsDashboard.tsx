import { useNavigate } from 'react-router-dom';
import { Workflow, RefreshCw } from 'lucide-react';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';

export default function JobsDashboard() {
  const navigate = useNavigate();

  const jobsList = [
    { id: 'job-1049', type: 'IMPORT', dataset: 'Chatbot Alignment Set', status: 'completed', progress: '100%', time: '2 mins ago' },
    { id: 'job-1050', type: 'EXPORT', dataset: 'Safety Edge Cases', status: 'running', progress: '64%', time: 'Active' },
    { id: 'job-1051', type: 'EVALUATION', dataset: 'RAG Retrieval Suite', status: 'queued', progress: '0%', time: 'Queued' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
            <Workflow className="w-5 h-5 text-brand-terracotta" />
            Asynchronous Job Execution Queue
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Background batch import/export tasks, evaluation jobs, and worker pool queues.
          </p>
        </div>
        <Button variant="outline" size="sm" icon={RefreshCw}>
          Refresh Queue
        </Button>
      </div>

      {/* Jobs Table Card */}
      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">Job ID</th>
                <th className="px-5 py-3 font-medium">Job Type</th>
                <th className="px-5 py-3 font-medium">Target Context</th>
                <th className="px-5 py-3 font-medium">Progress</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {jobsList.map((job) => (
                <tr key={job.id} className="hover:bg-workbench-card/50 transition-colors">
                  <td className="px-5 py-3.5 font-mono text-xs font-semibold text-workbench-text">
                    {job.id}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                    {job.type}
                  </td>
                  <td className="px-5 py-3.5 text-workbench-text">
                    {job.dataset}
                  </td>
                  <td className="px-5 py-3.5 font-mono text-xs text-workbench-muted">
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-workbench-border h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-brand-terracotta h-full rounded-full"
                          style={{ width: job.progress }}
                        />
                      </div>
                      <span>{job.progress}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    <Badge variant={job.status === 'completed' ? 'success' : job.status === 'running' ? 'running' : 'neutral'}>
                      {job.status}
                    </Badge>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/projects/1/jobs/${job.id}`)}
                    >
                      Inspect Steps
                    </Button>
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
