import { useState, useEffect } from 'react';
import { Clock, Plus, Play } from 'lucide-react';
import { api } from '../services/api';
import type { ScheduledJob } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Dialog } from '../components/common/Dialog';
import { Input } from '../components/common/Input';
import { EmptyState } from '../components/common/EmptyState';

export default function ScheduledJobs() {
  const [jobs, setJobs] = useState<ScheduledJob[]>([]);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const [jobName, setJobName] = useState('');
  const [cronExpr, setCronExpr] = useState('0 0 * * *');

  const fetchJobs = async () => {
    try {
      const list = await api.jobs.scheduler.list();
      setJobs(list || []);
    } catch (err) {
      console.error('Failed to load scheduled jobs:', err);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleCreate = async () => {
    if (!jobName.trim()) return;
    try {
      await api.jobs.scheduler.create({
        name: jobName,
        cron_expression: cronExpr,
        pipeline: 'Daily Model Quality Drift Check',
      });
      setJobName('');
      setIsCreateOpen(false);
      fetchJobs();
    } catch (err) {
      console.error('Failed to create scheduled job:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-workbench-border pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-workbench-text">
            Scheduled Evaluation Jobs
          </h1>
          <p className="text-xs text-workbench-muted mt-1">
            Automated cron schedules for continuous regression testing and model drift detection.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="primary" size="sm" icon={Plus} onClick={() => setIsCreateOpen(true)}>
            New Schedule
          </Button>
        </div>
      </div>

      {/* Jobs Data Table Card */}
      <Card padding="none">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-workbench-card border-b border-workbench-border text-[10px] font-mono uppercase text-workbench-muted">
              <tr>
                <th className="px-5 py-3 font-medium">Job Schedule Name</th>
                <th className="px-5 py-3 font-medium">Cron Expression</th>
                <th className="px-5 py-3 font-medium">Target Pipeline</th>
                <th className="px-5 py-3 font-medium">Next Execution</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-workbench-border">
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center">
                    <EmptyState
                      title="No scheduled jobs configured"
                      description="Create automated cron triggers to monitor model quality continuously."
                      icon={Clock}
                      action={
                        <Button
                          variant="primary"
                          size="sm"
                          icon={Plus}
                          onClick={() => setIsCreateOpen(true)}
                        >
                          Create Schedule
                        </Button>
                      }
                    />
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-workbench-card/50 transition-colors">
                    <td className="px-5 py-3.5 font-semibold text-workbench-text">{job.name}</td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      <span className="px-2 py-0.5 rounded bg-workbench-bg border border-workbench-border">
                        {job.cron_expression}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-workbench-muted">
                      {job.pipeline || 'Regression Evaluation'}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-[11px] text-workbench-muted">
                      {job.next_run
                        ? new Date(job.next_run).toLocaleString()
                        : 'Tomorrow 00:00 UTC'}
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge variant={job.enabled !== false ? 'success' : 'neutral'}>
                        {job.enabled !== false ? 'active' : 'paused'}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5 text-right space-x-2">
                      <Button variant="outline" size="sm" icon={Play}>
                        Run Now
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Create Dialog */}
      <Dialog
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Schedule Evaluation Cron Job"
        subtitle="Automate continuous model testing at fixed cron intervals"
        footer={
          <>
            <Button variant="ghost" size="sm" onClick={() => setIsCreateOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleCreate}>
              Save Schedule
            </Button>
          </>
        }
      >
        <div className="space-y-4 text-chrome-text">
          <Input
            label="Schedule Name"
            placeholder="e.g. Nightly Regression Evaluation"
            value={jobName}
            onChange={(e) => setJobName(e.target.value)}
            variant="chrome"
          />
          <Input
            label="Cron Syntax Expression"
            placeholder="0 0 * * *"
            value={cronExpr}
            onChange={(e) => setCronExpr(e.target.value)}
            variant="chrome"
            hint="Standard 5-part cron format (Minute Hour Day-of-month Month Day-of-week)"
          />
        </div>
      </Dialog>
    </div>
  );
}
