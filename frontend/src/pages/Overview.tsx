import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowRight, Database, FlaskConical, Folder, Plus } from 'lucide-react';
import { DataTable, Empty, ErrorNotice, Loading, PageHeader, Panel } from '../components/ui';
import { getPage } from '../services/client';
import { useProject } from '../layouts/WorkspaceShell';
export default function Overview() {
  const { projectId, project, projects } = useProject();
  const navigate = useNavigate();
  const query = useQuery({
    queryKey: ['overview', projectId],
    enabled: !!projectId,
    queryFn: async ({ signal }) => {
      const scope = `project_id=${encodeURIComponent(projectId)}&limit=5`;
      const [datasets, runs, completed] = await Promise.all([
        getPage(`/datasets/?${scope}`, signal),
        getPage(`/experiments/?${scope}`, signal),
        getPage(`/experiments/?${scope}&status=COMPLETED`, signal),
      ]);
      return { datasets, runs, completed };
    },
  });
  if (!projectId)
    return (
      <div className="page">
        <PageHeader
          title="Welcome to EvalForge"
          description="Your evaluation workspace starts with a project."
        />
        <Panel>
          <Empty
            title="Create your first project"
            description="Organize a dataset, choose a judge, and run an evaluation. Your results will appear here."
            action={
              <Link className="button primary" to="/projects">
                <Plus size={16} />
                Create a project
              </Link>
            }
          />
        </Panel>
      </div>
    );
  return (
    <div className="page">
      <PageHeader
        title="Overview"
        description={`Your evaluation activity in ${project?.name ?? 'this project'}.`}
        actions={
          <Link className="button primary" to={`/projects/${projectId}/evaluations/new`}>
            <Plus size={16} />
            New evaluation
          </Link>
        }
      />
      {query.isPending ? (
        <Loading />
      ) : query.error ? (
        <ErrorNotice error={query.error} retry={() => void query.refetch()} />
      ) : (
        <>
          <div className="stats">
            {[
              {
                label: 'Datasets',
                value: query.data.datasets.total,
                icon: Database,
                note: 'Versioned evaluation inputs',
              },
              {
                label: 'Evaluation runs',
                value: query.data.runs.total,
                icon: FlaskConical,
                note: 'All runs in this project',
              },
              {
                label: 'Completed runs',
                value: query.data.completed.total,
                icon: Folder,
                note: 'Reported complete by the server',
              },
            ].map((s) => (
              <div className="stat" key={s.label}>
                <div className="stat-label">
                  <s.icon size={15} />
                  {s.label}
                </div>
                <div className="stat-value">{s.value.toLocaleString()}</div>
                <div className="stat-note">{s.note}</div>
              </div>
            ))}
          </div>
          <div className="split">
            <Panel
              title="Recent evaluations"
              description="Open a run to inspect scores and reasoning."
              actions={
                <Link className="button quiet" to={`/projects/${projectId}/evaluations`}>
                  View all
                  <ArrowRight size={14} />
                </Link>
              }
            >
              {query.data.runs.items.length ? (
                <DataTable
                  rows={query.data.runs.items}
                  columns={[
                    {
                      key: 'name',
                      label: 'Evaluation',
                      render: (r) => (
                        <>
                          <span className="record-name">{r.name}</span>
                          <span className="record-description">
                            {String(r.judge)} · {String(r.provider)}
                          </span>
                        </>
                      ),
                    },
                    { key: 'status', label: 'Status' },
                    { key: 'created_at', label: 'Created' },
                  ]}
                  inspect={(r) => navigate(`/projects/${projectId}/evaluations/${r.id}`)}
                />
              ) : (
                <Empty
                  title="No evaluations yet"
                  description="Choose a dataset and a configured provider to run your first evaluation."
                />
              )}
            </Panel>
            <Panel title="Project workspace">
              <div className="panel-body form-stack">
                <div>
                  <h3>{project?.name}</h3>
                  <p className="muted" style={{ marginTop: 8, fontSize: 13 }}>
                    {String(
                      project?.description ?? 'Keep your test data and evaluation runs together.'
                    )}
                  </p>
                </div>
                <div style={{ borderTop: '1px solid var(--border)', paddingTop: 18 }}>
                  <p className="muted" style={{ fontSize: 12 }}>
                    Available projects
                  </p>
                  <strong style={{ fontSize: 20, fontWeight: 550 }}>{projects.length}</strong>
                </div>
                <Link className="button" to={`/projects/${projectId}/datasets`}>
                  <Database size={15} />
                  Manage datasets
                </Link>
                <Link className="button quiet" to="/developer">
                  Read the evaluation guide
                  <ArrowRight size={14} />
                </Link>
              </div>
            </Panel>
          </div>
          <Panel
            title="Datasets"
            description="The latest test collections in this project."
            actions={
              <Link className="button quiet" to={`/projects/${projectId}/datasets/import`}>
                Import dataset
                <Plus size={14} />
              </Link>
            }
          >
            {query.data.datasets.items.length ? (
              <DataTable
                rows={query.data.datasets.items}
                columns={[
                  {
                    key: 'name',
                    label: 'Dataset',
                    render: (r) => (
                      <>
                        <span className="record-name">{r.name}</span>
                        <span className="record-description">{String(r.description ?? '')}</span>
                      </>
                    ),
                  },
                  { key: 'status', label: 'Status' },
                  { key: 'visibility', label: 'Visibility' },
                  { key: 'created_at', label: 'Created' },
                ]}
                inspect={(r) => navigate(`/projects/${projectId}/datasets/${r.id}`)}
              />
            ) : (
              <Empty
                title="Add your evaluation data"
                description="Import prompts, candidate responses, and reference answers from CSV, JSON, or JSONL."
                action={
                  <Link className="button" to={`/projects/${projectId}/datasets/import`}>
                    Import dataset
                  </Link>
                }
              />
            )}
          </Panel>
        </>
      )}
    </div>
  );
}
