import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { ArrowLeft } from 'lucide-react';
import {
  Button,
  DataTable,
  Empty,
  ErrorNotice,
  Loading,
  Modal,
  PageHeader,
  Panel,
  RecordDetails,
  Status,
} from '../components/ui';
import { client, getRecord, type RecordData } from '../services/client';
import { useProject } from '../layouts/WorkspaceShell';
import { useJobProgress } from '../hooks/useJobProgress';
export default function JobView() {
  const { jobId } = useParams();
  const { projectId } = useProject();
  const [action, setAction] = useState('');
  const query = useQuery({
    queryKey: ['job', jobId],
    queryFn: ({ signal }) => getRecord(`/jobs/${jobId}`, signal),
  });
  const terminal = ['COMPLETED', 'FAILED', 'CANCELLED', 'EXPIRED'].includes(
    String(query.data?.status)
  );
  const stream = useJobProgress(query.data ? jobId : undefined, terminal);
  const mutation = useMutation({
    mutationFn: () => client.post(`/jobs/${jobId}/${action}`),
    onSuccess: async () => {
      setAction('');
      await query.refetch();
    },
  });
  const payload = query.data?.payload as RecordData | undefined;
  return (
    <div className="page">
      <PageHeader
        title={query.data?.name ?? 'Background job'}
        description="Execution progress, logs, and worker results."
        actions={
          <Link className="button" to={`/projects/${projectId}/jobs`}>
            <ArrowLeft size={15} />
            Jobs
          </Link>
        }
      />
      {query.isPending ? (
        <Loading />
      ) : query.error ? (
        <ErrorNotice error={query.error} retry={() => void query.refetch()} />
      ) : payload?.project_id !== projectId ? (
        <ErrorNotice error={new Error('This job belongs to another project.')} />
      ) : (
        <>
          <div className="actions">
            <Status value={query.data.status} />
            <span className="muted">{stream}</span>
            <Button onClick={() => void query.refetch()}>Refresh</Button>
            {['FAILED', 'CANCELLED', 'EXPIRED', 'COMPLETED'].includes(String(query.data.status)) ? (
              <Button onClick={() => setAction('retry')}>Retry job</Button>
            ) : (
              <Button variant="danger" onClick={() => setAction('cancel')}>
                Cancel job
              </Button>
            )}
          </div>
          <Panel title="Progress">
            <div className="panel-body">
              <label htmlFor="job-progress">
                {Number(query.data.progress ?? 0).toFixed(0)}% ·{' '}
                {String(query.data.current_step ?? 'Waiting for an update')}
              </label>
              <progress
                id="job-progress"
                max={100}
                value={Number(query.data.progress ?? 0)}
                style={{ width: '100%', accentColor: 'var(--accent)' }}
              />
              {Boolean(query.data.error_message) && (
                <ErrorNotice error={new Error(String(query.data.error_message))} />
              )}
            </div>
          </Panel>
          <Panel title="Execution logs">
            {Array.isArray(query.data.logs) && query.data.logs.length ? (
              <DataTable
                rows={query.data.logs as RecordData[]}
                columns={[
                  { key: 'log_level', label: 'Level' },
                  { key: 'message', label: 'Message' },
                  { key: 'created_at', label: 'Time' },
                ]}
              />
            ) : (
              <Empty
                title="No log entries yet"
                description="Messages appear here as the worker reports progress."
              />
            )}
          </Panel>
          <Panel title="Job details">
            <div className="panel-body">
              <RecordDetails record={query.data} />
            </div>
          </Panel>
        </>
      )}
      <Modal
        title={action === 'cancel' ? 'Cancel this job?' : 'Retry this job?'}
        open={!!action}
        close={() => setAction('')}
        footer={
          <>
            <Button onClick={() => setAction('')}>Back</Button>
            <Button
              busy={mutation.isPending}
              variant={action === 'cancel' ? 'danger' : 'primary'}
              onClick={() => mutation.mutate()}
            >
              Confirm {action}
            </Button>
          </>
        }
      >
        <p>
          {action === 'cancel'
            ? 'The worker will be asked to stop processing this job.'
            : 'The job will be queued again. This may repeat provider calls and incur charges.'}
        </p>
        {mutation.error && <ErrorNotice error={mutation.error} />}
      </Modal>
    </div>
  );
}
