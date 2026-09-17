import { useState, type FormEvent } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, ArrowRight, Download, Plus, RefreshCw, Search } from 'lucide-react';
import {
  Button,
  DataTable,
  Empty,
  ErrorNotice,
  Field,
  Loading,
  Modal,
  PageHeader,
  Panel,
  RecordDetails,
  formatValue,
  type Column,
} from '../components/ui';
import {
  client,
  DEMO_MODE,
  download,
  getPage,
  getRecord,
  unwrap,
  type RecordData,
} from '../services/client';
import { useProject } from '../layouts/WorkspaceShell';

export type FormField = {
  key: string;
  label: string;
  type?: 'textarea' | 'number' | 'json' | 'select' | 'email' | 'datasets';
  required?: boolean;
  options?: string[];
  hint?: string;
  initial?: string;
};
export type ResourceConfig = {
  title: string;
  description: string;
  unavailable?: string;
  endpoint: string;
  columns: Column[];
  pagination?: 'offset' | 'page' | 'none';
  search?: boolean;
  create?: { label: string; endpoint?: string; fields: FormField[]; extra?: RecordData };
  detailPath?: string;
  deleteEndpoint?: string;
};
const nameColumn: Column = {
  key: 'name',
  label: 'Name',
  render: (r) => (
    <>
      <span className="record-name">{r.name ?? r.id}</span>
      {typeof r.description === 'string' && (
        <span className="record-description">{r.description}</span>
      )}
    </>
  ),
};
const columns = (...keys: string[]): Column[] =>
  keys.map((key) => ({ key, label: key.replace(/_/g, ' ').replace(/^./, (x) => x.toUpperCase()) }));
const nameFields: FormField[] = [
  { key: 'name', label: 'Name', required: true },
  { key: 'description', label: 'Description', type: 'textarea' },
];

export function resourceConfig(
  kind: string,
  projectId: string,
  orgId?: string
): ResourceConfig | null {
  const project = `project_id=${encodeURIComponent(projectId)}`;
  const scope = (path: string) => `${path}?${project}`;
  const config: Record<string, ResourceConfig> = {
    projects: {
      title: 'Projects',
      description: 'Keep datasets, evaluations, and results organized by project.',
      endpoint: '/projects',
      pagination: 'page',
      search: true,
      columns: [nameColumn, ...columns('status', 'created_at')],
      create: { label: 'New project', fields: nameFields },
      deleteEndpoint: '/projects',
    },
    datasets: {
      title: 'Datasets',
      description: 'Versioned prompts and reference answers for repeatable evaluations.',
      endpoint: scope('/datasets/'),
      pagination: 'offset',
      search: true,
      columns: [nameColumn, ...columns('visibility', 'status', 'created_at')],
      create: { label: 'New dataset', fields: nameFields },
      detailPath: `/projects/${projectId}/datasets`,
    },
    evaluations: {
      title: 'Evaluations',
      description: 'Run your datasets through a judge and inspect the results.',
      endpoint: scope('/experiments/'),
      pagination: 'offset',
      search: true,
      columns: [nameColumn, ...columns('status', 'judge', 'provider', 'created_at')],
      detailPath: `/projects/${projectId}/evaluations`,
    },
    benchmarks: {
      title: 'Benchmarks',
      description: 'Group datasets into reusable benchmark suites.',
      endpoint: scope('/benchmarks/'),
      pagination: 'offset',
      search: true,
      columns: [nameColumn, ...columns('tags', 'created_at')],
      create: {
        label: 'New benchmark',
        fields: [
          ...nameFields,
          {
            key: 'dataset_ids',
            label: 'Datasets',
            type: 'datasets',
            required: true,
            initial: '[]',
            hint: 'Select the collections to include. Hold Ctrl or Command to select more than one.',
          },
        ],
      },
    },
    rag: {
      title: 'RAG assessments',
      description:
        'Recorded retrieval and grounding measurements. These records are supplied by your evaluation pipeline.',
      endpoint: scope('/rag'),
      pagination: 'offset',
      columns: columns(
        'id',
        'faithfulness',
        'context_precision',
        'context_recall',
        'answer_relevancy',
        'created_at'
      ),
    },
    safety: {
      title: 'Safety assessments',
      description:
        'Recorded content-safety assessments for your project. Scores are reported by the source pipeline.',
      endpoint: scope('/safety'),
      pagination: 'offset',
      columns: columns(
        'result_id',
        'safety_score',
        'toxicity_score',
        'policy_violations',
        'created_at'
      ),
    },
    policy: {
      title: 'Policies',
      description: 'Define and review the policies applied to project evaluations.',
      endpoint: scope('/policies'),
      pagination: 'offset',
      columns: [nameColumn, ...columns('is_active', 'created_at')],
      create: {
        label: 'New policy',
        fields: [
          ...nameFields,
          {
            key: 'rules',
            label: 'Policy rules',
            type: 'json',
            initial: '{}',
            hint: 'Policy rule configuration as a JSON object.',
          },
        ],
      },
      deleteEndpoint: '/policies',
    },
    reports: {
      title: 'Reports',
      description: 'Generate and download evaluation reports from project results.',
      endpoint: scope('/reports'),
      pagination: 'page',
      columns: [nameColumn, ...columns('type', 'status', 'created_at')],
      create: {
        label: 'Generate report',
        endpoint: scope('/reports/generate'),
        fields: [
          { key: 'name', label: 'Report name', required: true },
          { key: 'type', label: 'Format', type: 'select', options: ['PDF', 'CSV'], initial: 'PDF' },
        ],
      },
    },
    jobs: {
      title: 'Background jobs',
      description: 'Track execution, inspect logs, and manage queued work for this project.',
      endpoint: scope('/jobs'),
      pagination: 'page',
      search: true,
      columns: [nameColumn, ...columns('status', 'progress', 'queue_name', 'created_at')],
      detailPath: `/projects/${projectId}/jobs`,
      create: {
        label: 'New job',
        fields: [
          { key: 'name', label: 'Job name', required: true },
          { key: 'queue_name', label: 'Queue', initial: 'default', required: true },
          {
            key: 'payload',
            label: 'Job parameters',
            type: 'json',
            initial: '{}',
            hint: 'Use the payload supported by your configured worker.',
          },
        ],
      },
    },
    logs: {
      title: 'Execution logs',
      description: 'Open a background job to inspect its execution logs and retry history.',
      endpoint: scope('/jobs'),
      pagination: 'page',
      columns: [nameColumn, ...columns('status', 'current_step', 'created_at')],
      detailPath: `/projects/${projectId}/jobs`,
    },
    schedules: {
      title: 'Scheduled jobs',
      unavailable:
        'User-managed scheduling is not available in this release. The server maintenance scheduler is administered outside the workspace interface.',
      description: 'Review recurring jobs configured by your server administrator.',
      endpoint: '/jobs/scheduler/jobs',
      pagination: 'none',
      columns: [nameColumn, ...columns('cron_expression', 'next_run', 'enabled')],
    },
    providers: {
      title: 'Providers',
      description:
        'Provider capabilities registered on this server. Availability here does not indicate a configured or healthy connection.',
      endpoint: '/providers',
      pagination: 'none',
      columns: columns('name', 'key', 'description'),
    },
    webhooks: {
      title: 'API keys & webhooks',
      description: 'Manage workspace credentials and project event subscriptions.',
      endpoint: scope('/webhooks'),
      pagination: 'none',
      columns: columns('target_url', 'events', 'is_active', 'created_at'),
    },
    audit: {
      title: 'Audit log',
      description: 'Recorded administrative actions for your organization.',
      endpoint: `/audit?org_id=${orgId}`,
      pagination: 'offset',
      columns: columns('action', 'resource_type', 'actor_id', 'created_at'),
    },
    members: {
      title: 'Members & access',
      description: 'Manage access to your organization.',
      endpoint: `/organizations/${orgId}/members`,
      pagination: 'none',
      columns: columns('user_id', 'role', 'workspace_id', 'created_at'),
      create: {
        label: 'Invite member',
        endpoint: `/organizations/${orgId}/invitations`,
        fields: [
          { key: 'email', label: 'Email address', type: 'email', required: true },
          {
            key: 'role',
            label: 'Role',
            type: 'select',
            options: ['Member', 'Admin'],
            initial: 'Member',
          },
        ],
      },
    },
    billing: {
      title: 'Billing & usage',
      description:
        'Invoices issued for this organization. Billing changes are managed by your administrator.',
      endpoint: `/billing/invoices?org_id=${orgId}`,
      pagination: 'none',
      columns: columns('id', 'status', 'amount_due', 'currency', 'created_at'),
    },
  };
  return config[kind] ?? null;
}

export function CreateForm({
  config,
  close,
  saved,
}: {
  config: NonNullable<ResourceConfig['create']> & { path: string };
  close: () => void;
  saved: () => void;
}) {
  const cache = useQueryClient();
  const { projectId } = useProject();
  const datasetOptions = useQuery({
    queryKey: ['form-datasets', projectId],
    queryFn: ({ signal }) => getPage(`/datasets/?project_id=${projectId}&limit=100`, signal),
    enabled: config.fields.some((f) => f.type === 'datasets'),
  });
  const [values, setValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(config.fields.map((f) => [f.key, f.initial ?? '']))
  );
  const [parseError, setParseError] = useState<unknown>(null);
  const mutation = useMutation({
    mutationFn: async (data: RecordData) => unwrap((await client.post(config.path, data)).data),
    onSuccess: async () => {
      await cache.invalidateQueries();
      saved();
      close();
    },
  });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (mutation.isPending) return;
    setParseError(null);
    try {
      const payload: RecordData = { ...config.extra };
      for (const f of config.fields) {
        const v = values[f.key]?.trim();
        if (!v && !f.required) continue;
        payload[f.key] =
          f.type === 'json' || f.type === 'datasets'
            ? JSON.parse(v)
            : f.type === 'number'
              ? Number(v)
              : v;
      }
      mutation.mutate(payload);
    } catch {
      setParseError(new Error('Enter valid JSON in the configuration field.'));
    }
  };
  return (
    <form onSubmit={submit} className="form-stack">
      {(parseError || mutation.error) && <ErrorNotice error={parseError || mutation.error} />}{' '}
      {config.fields.map((field) => (
        <Field key={field.key} label={field.label} hint={field.hint}>
          {(id) =>
            field.type === 'datasets' ? (
              <select
                multiple
                id={id}
                className="control"
                required
                value={JSON.parse(values[field.key] || '[]')}
                onChange={(e) =>
                  setValues({
                    ...values,
                    [field.key]: JSON.stringify(
                      Array.from(e.target.selectedOptions, (o) => o.value)
                    ),
                  })
                }
              >
                {datasetOptions.data?.items.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            ) : field.type === 'textarea' || field.type === 'json' ? (
              <textarea
                id={id}
                className={`control ${field.type === 'json' ? 'mono' : ''}`}
                required={field.required}
                value={values[field.key]}
                onChange={(e) => setValues({ ...values, [field.key]: e.target.value })}
              />
            ) : field.type === 'select' ? (
              <select
                id={id}
                className="control"
                value={values[field.key]}
                onChange={(e) => setValues({ ...values, [field.key]: e.target.value })}
              >
                {field.options?.map((o) => (
                  <option key={o}>{o}</option>
                ))}
              </select>
            ) : (
              <input
                id={id}
                className="control"
                type={field.type ?? 'text'}
                required={field.required}
                maxLength={field.type === 'number' ? undefined : 2000}
                value={values[field.key]}
                onChange={(e) => setValues({ ...values, [field.key]: e.target.value })}
              />
            )
          }
        </Field>
      ))}
      <div className="actions" style={{ justifyContent: 'flex-end' }}>
        <Button onClick={close} disabled={mutation.isPending}>
          Cancel
        </Button>
        <Button variant="primary" type="submit" busy={mutation.isPending}>
          {config.label}
        </Button>
      </div>
    </form>
  );
}

export default function ResourcePage({ kind }: { kind: string }) {
  const { projectId, projects } = useProject();
  const navigate = useNavigate();
  const cache = useQueryClient();
  const connection = useQuery({
    queryKey: ['connection'],
    queryFn: ({ signal }) => getRecord('/connection', signal),
    enabled: !DEMO_MODE,
  });
  const orgId = connection.data?.organization_id as string | undefined;
  const config = resourceConfig(kind, projectId, orgId);
  const needsOrg = ['members', 'audit', 'billing'].includes(kind);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<RecordData | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [notice, setNotice] = useState('');
  const [actionError, setActionError] = useState<unknown>(null);
  const endpoint = config?.endpoint ?? '';
  const pagination = config?.pagination;
  const queryString = new URLSearchParams(
    pagination === 'page'
      ? { page: String(page), page_size: '20' }
      : pagination === 'offset'
        ? { skip: String((page - 1) * 20), limit: '20' }
        : {}
  );
  if (search && config?.search) queryString.set('search', search);
  const url = `${endpoint}${endpoint.includes('?') ? '&' : '?'}${queryString}`;
  const query = useQuery({
    queryKey: ['resource', kind, projectId, orgId, page, search],
    queryFn: ({ signal }) => getPage(url, signal),
    enabled: !!config && !config.unavailable && (!needsOrg || !!orgId),
    refetchInterval: kind === 'jobs' ? 10000 : false,
  });
  const remove = useMutation({
    mutationFn: async () => {
      await client.delete(`${config?.deleteEndpoint}/${selected?.id}`);
    },
    onSuccess: async () => {
      setConfirmDelete(false);
      setSelected(null);
      setNotice('Deleted successfully.');
      await cache.invalidateQueries();
    },
  });
  if (!config)
    return (
      <Empty
        title="Page unavailable"
        description="Return to your workspace to continue."
        action={
          <Link className="button" to="/">
            Overview
          </Link>
        }
      />
    );
  if (config.unavailable)
    return (
      <div className="page">
        <PageHeader title={config.title} description="Availability" />
        <Panel>
          <Empty
            title="Scheduling is managed by your administrator"
            description={config.unavailable}
          />
        </Panel>
      </div>
    );
  if (needsOrg && !orgId)
    return (
      <div className="page">
        <PageHeader title={config.title} description={config.description} />
        {connection.isPending && !DEMO_MODE ? (
          <Loading />
        ) : connection.error ? (
          <ErrorNotice error={connection.error} retry={() => void connection.refetch()} />
        ) : (
          <Panel>
            <Empty
              title="Organization access required"
              description="Connect with an organization-scoped key to view this page."
              action={
                <Link className="button" to="/profile">
                  Connection settings
                </Link>
              }
            />
          </Panel>
        )}
      </div>
    );
  const items = query.data?.items ?? [];
  const total = query.data?.total ?? 0;
  const paged = pagination === 'page' || pagination === 'offset';
  const partialTotal =
    pagination === 'offset' && ['rag', 'safety', 'policy', 'audit'].includes(kind);
  const more = partialTotal ? items.length === 20 : page * 20 < total;
  const inspect = (record: RecordData) => {
    if (DEMO_MODE) {
      setSelected(record);
      return;
    }
    if (kind === 'projects') {
      navigate(`/projects/${record.id}/datasets`);
    } else if (config.detailPath) {
      navigate(`${config.detailPath}/${record.id}`);
    } else setSelected(record);
  };
  return (
    <div className="page">
      <PageHeader
        title={config.title}
        description={config.description}
        actions={
          <>
            {kind === 'datasets' && (
              <Link className="button" to={`/projects/${projectId}/datasets/import`}>
                Import dataset
              </Link>
            )}
            {kind === 'evaluations' ? (
              <Link className="button primary" to={`/projects/${projectId}/evaluations/new`}>
                <Plus size={16} />
                New evaluation
              </Link>
            ) : (
              config.create && (
                <Button variant="primary" disabled={DEMO_MODE} onClick={() => setOpen(true)}>
                  <Plus size={16} />
                  {config.create.label}
                </Button>
              )
            )}
          </>
        }
      />
      {notice && (
        <div className="notice" role="status">
          {notice}
        </div>
      )}
      {actionError !== null && <ErrorNotice error={actionError} />}
      {kind === 'webhooks' && (
        <div className="notice info">
          API keys are provisioned by your administrator. This page lists event subscriptions for
          the active project.
        </div>
      )}
      <Panel>
        <div className="toolbar">
          {config.search ? (
            <div className="search">
              <Search size={16} />
              <input
                className="control"
                aria-label={`Search ${config.title.toLowerCase()}`}
                placeholder={`Search ${config.title.toLowerCase()}…`}
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
              />
            </div>
          ) : (
            <span className="muted">
              {query.data ? `${total} ${total === 1 ? 'record' : 'records'}` : 'Records'}
            </span>
          )}
          <Button
            onClick={() => void query.refetch()}
            disabled={query.isFetching}
            aria-label="Refresh records"
          >
            <RefreshCw size={15} />
            Refresh
          </Button>
        </div>
        {query.isPending ? (
          <Loading />
        ) : query.error ? (
          <div className="panel-body">
            <ErrorNotice error={query.error} retry={() => void query.refetch()} />
          </div>
        ) : items.length ? (
          <DataTable rows={items} columns={config.columns} inspect={inspect} />
        ) : (
          <Empty
            title={search ? 'No matching records' : `No ${config.title.toLowerCase()} yet`}
            description={
              search
                ? 'Try a different search.'
                : kind === 'datasets'
                  ? 'Import a CSV, JSON, or JSONL file to start building your evaluation set.'
                  : kind === 'evaluations'
                    ? 'Create an evaluation using a versioned dataset and a configured provider.'
                    : 'Records will appear here when they are created in this workspace.'
            }
            action={
              kind === 'projects' ? (
                <Button variant="primary" disabled={DEMO_MODE} onClick={() => setOpen(true)}>
                  <Plus size={16} />
                  Create your first project
                </Button>
              ) : undefined
            }
          />
        )}
        {query.data && paged && (
          <div className="pagination">
            <span>
              {total === 0
                ? '0 records'
                : `Page ${page} · ${total} records${partialTotal ? ' loaded' : ''}`}
            </span>
            <div className="actions">
              <Button onClick={() => setPage(page - 1)} disabled={page === 1 || query.isFetching}>
                <ArrowLeft size={14} />
                Previous
              </Button>
              <Button onClick={() => setPage(page + 1)} disabled={!more || query.isFetching}>
                Next
                <ArrowRight size={14} />
              </Button>
            </div>
          </div>
        )}
      </Panel>
      <Modal title={config.create?.label ?? 'Create'} open={open} close={() => setOpen(false)}>
        {open && config.create && (
          <CreateForm
            config={{ ...config.create, path: config.create.endpoint ?? endpoint }}
            close={() => setOpen(false)}
            saved={() => setNotice('Saved successfully.')}
          />
        )}
      </Modal>
      <Modal
        title={String(selected?.name ?? 'Record details')}
        open={!!selected && !confirmDelete}
        close={() => setSelected(null)}
        footer={
          <>
            {kind === 'reports' && selected?.status === 'COMPLETED' && (
              <Button
                disabled={DEMO_MODE}
                onClick={() =>
                  void download(
                    `/reports/${selected.id}/download`,
                    `${selected.name}.${String(selected.type).toLowerCase()}`
                  ).catch(setActionError)
                }
              >
                <Download size={16} />
                Download report
              </Button>
            )}
            {kind === 'schedules' && selected?.id && (
              <Button
                disabled={DEMO_MODE}
                onClick={async () => {
                  try {
                    await client.post(`/jobs/scheduler/jobs/${selected.id}/toggle`);
                    setSelected(null);
                    await query.refetch();
                    setNotice('Schedule updated.');
                  } catch (e) {
                    setActionError(e);
                  }
                }}
              >
                {selected.enabled ? 'Pause schedule' : 'Resume schedule'}
              </Button>
            )}
            {config.deleteEndpoint && (
              <Button variant="danger" disabled={DEMO_MODE} onClick={() => setConfirmDelete(true)}>
                Delete
              </Button>
            )}
          </>
        }
      >
        {selected && <RecordDetails record={selected} />}
      </Modal>
      <Modal
        title="Delete this record?"
        open={confirmDelete}
        close={() => setConfirmDelete(false)}
        footer={
          <>
            <Button onClick={() => setConfirmDelete(false)}>Cancel</Button>
            <Button variant="danger" busy={remove.isPending} onClick={() => remove.mutate()}>
              Delete record
            </Button>
          </>
        }
      >
        <p>
          This removes {formatValue(selected?.name)} from this workspace. Confirm that it is no
          longer needed.
        </p>
        {remove.error && <ErrorNotice error={remove.error} />}
      </Modal>
      {kind === 'projects' && projects.length === 0 && (
        <p className="muted">Projects inherit the workspace assigned to your API key.</p>
      )}
    </div>
  );
}
