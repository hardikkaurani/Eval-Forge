import { useState, type FormEvent } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Play, Upload } from 'lucide-react';
import {
  Button,
  DataTable,
  Empty,
  ErrorNotice,
  Field,
  Loading,
  PageHeader,
  Panel,
  RecordDetails,
  Status,
} from '../components/ui';
import { client, DEMO_MODE, getPage, getRecord, unwrap, type RecordData } from '../services/client';
import { useProject } from '../layouts/WorkspaceShell';

export function ImportDataset() {
  const { projectId } = useProject();
  const navigate = useNavigate();
  const cache = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<unknown>(null);
  const mutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('Choose a CSV, JSON, or JSONL file.');
      if (!/\.(csv|json|jsonl)$/i.test(file.name) || file.size > 100 * 1024 * 1024)
        throw new Error('Choose a CSV, JSON, or JSONL file smaller than 100 MB.');
      const data = new FormData();
      data.set('project_id', projectId);
      data.set('dataset_name', name.trim());
      data.set('description', description);
      data.set('version_label', 'v1');
      data.set('file', file);
      const result = unwrap(
        (await client.post('/datasets/import', data, { timeout: 120000 })).data
      ) as RecordData;
      if (result.status !== 'COMPLETED' && result.status !== 'completed')
        throw new Error(
          'The import was accepted but completion is not confirmed. Refresh datasets to check its status before retrying.'
        );
      return result;
    },
    onSuccess: async () => {
      await cache.invalidateQueries();
      navigate(`/projects/${projectId}/datasets`);
    },
  });
  return (
    <div className="page form-width">
      <PageHeader
        title="Import a dataset"
        description="Add prompts and reference answers from your own evaluation data."
        actions={
          <Link className="button" to={`/projects/${projectId}/datasets`}>
            <ArrowLeft size={15} />
            Datasets
          </Link>
        }
      />
      <form
        className="form-stack"
        onSubmit={(e) => {
          e.preventDefault();
          if (!mutation.isPending) mutation.mutate();
        }}
      >
        {Boolean(mutation.error || error) && <ErrorNotice error={mutation.error || error} />}
        <section className="form-section">
          <div>
            <h2>Dataset details</h2>
            <p>Give this collection a name your team can recognize.</p>
          </div>
          <div className="form-stack">
            <Field label="Dataset name">
              {(id) => (
                <input
                  id={id}
                  required
                  maxLength={255}
                  className="control"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Customer support questions"
                />
              )}
            </Field>
            <Field label="Description (optional)">
              {(id) => (
                <textarea
                  id={id}
                  className="control"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              )}
            </Field>
          </div>
        </section>
        <section className="form-section">
          <div>
            <h2>Source file</h2>
            <p>CSV, JSON, or JSONL. Maximum 100 MB.</p>
          </div>
          <div className="form-stack">
            <Field
              label="Dataset file"
              hint="Include prompt, candidate_output, and reference_output fields. A dataset version is created on import."
            >
              {(id) => (
                <input
                  id={id}
                  className="control"
                  type="file"
                  accept=".csv,.json,.jsonl"
                  required
                  onChange={(e) => {
                    setFile(e.target.files?.[0] ?? null);
                    setError(null);
                  }}
                />
              )}
            </Field>
            <pre>{'prompt,candidate_output,reference_output\nWhat is 2 + 2?,4,4'}</pre>
          </div>
        </section>
        <div className="actions" style={{ justifyContent: 'flex-end' }}>
          <Link className="button" to={`/projects/${projectId}/datasets`}>
            Cancel
          </Link>
          <Button
            type="submit"
            variant="primary"
            busy={mutation.isPending}
            disabled={DEMO_MODE || !name.trim() || !file}
          >
            <Upload size={16} />
            Import dataset
          </Button>
        </div>
      </form>
    </div>
  );
}

export function NewEvaluation() {
  const { projectId } = useProject();
  const navigate = useNavigate();
  const cache = useQueryClient();
  const [name, setName] = useState('');
  const [dataset, setDataset] = useState('');
  const [version, setVersion] = useState('');
  const [provider, setProvider] = useState('');
  const [judge, setJudge] = useState('');
  const [model, setModel] = useState('');
  const metadata = useQuery({
    queryKey: ['evaluation-options', projectId],
    queryFn: async ({ signal }) => {
      const [datasets, providers, judges] = await Promise.all([
        getPage(`/datasets/?project_id=${projectId}&limit=100`, signal),
        getPage('/providers', signal),
        getPage('/judges', signal),
      ]);
      return { datasets, providers, judges };
    },
  });
  const versions = useQuery({
    queryKey: ['versions', dataset],
    enabled: !!dataset,
    queryFn: ({ signal }) => getPage(`/datasets/${dataset}/versions`, signal),
  });
  const [createdId, setCreatedId] = useState<string | null>(null);
  const mutation = useMutation({
    mutationFn: async () => {
      let id = createdId;
      if (!id) {
        const record = unwrap(
          (
            await client.post(`/experiments/?project_id=${projectId}`, {
              name: name.trim(),
              dataset_version_id: version,
              judge,
              provider,
              model: model.trim() || null,
              configuration: { temperature: 0, threshold: 0.7 },
            })
          ).data
        ) as RecordData;
        id = String(record.id);
        setCreatedId(id);
      }
      // Execution is synchronous in this backend; never issue an automatic retry.
      await client.post(`/experiments/${id}/execute`, undefined, { timeout: 0 });
      return id;
    },
    onSuccess: async (id) => {
      await cache.invalidateQueries();
      navigate(`/projects/${projectId}/evaluations/${id}`);
    },
  });
  const submit = (e: FormEvent) => {
    e.preventDefault();
    if (!mutation.isPending) mutation.mutate();
  };
  return (
    <div className="page form-width">
      <PageHeader
        title="New evaluation"
        description="Choose a versioned dataset, a judge, and a provider configured on your server."
        actions={
          <Link className="button" to={`/projects/${projectId}/evaluations`}>
            <ArrowLeft size={15} />
            Evaluations
          </Link>
        }
      />
      {metadata.isPending ? (
        <Loading />
      ) : metadata.error ? (
        <ErrorNotice error={metadata.error} retry={() => void metadata.refetch()} />
      ) : !metadata.data.datasets.items.length ? (
        <Panel>
          <Empty
            title="Add a dataset first"
            description="An evaluation needs a dataset version with at least one test case."
            action={
              <Link className="button primary" to={`/projects/${projectId}/datasets/import`}>
                Import dataset
              </Link>
            }
          />
        </Panel>
      ) : (
        <form className="form-stack" onSubmit={submit}>
          {mutation.error && <ErrorNotice error={mutation.error} />}{' '}
          {createdId && mutation.error && (
            <div className="notice info">
              The evaluation was created. Check its status before retrying execution.{' '}
              <Link className="table-link" to={`/projects/${projectId}/evaluations/${createdId}`}>
                View evaluation
              </Link>
            </div>
          )}
          <section className="form-section">
            <div>
              <h2>Evaluation details</h2>
              <p>A descriptive name makes it easier to compare runs later.</p>
            </div>
            <Field label="Evaluation name">
              {(id) => (
                <input
                  id={id}
                  required
                  maxLength={255}
                  className="control"
                  placeholder="Support response quality"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  disabled={!!createdId}
                />
              )}
            </Field>
          </section>
          <section className="form-section">
            <div>
              <h2>Test data</h2>
              <p>Each run uses a specific dataset version.</p>
            </div>
            <div className="form-stack">
              <Field label="Dataset">
                {(id) => (
                  <select
                    id={id}
                    required
                    className="control"
                    value={dataset}
                    disabled={!!createdId}
                    onChange={(e) => {
                      setDataset(e.target.value);
                      setVersion('');
                    }}
                  >
                    <option value="">Select a dataset</option>
                    {metadata.data.datasets.items.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.name}
                      </option>
                    ))}
                  </select>
                )}
              </Field>
              <Field label="Version">
                {(id) => (
                  <select
                    id={id}
                    required
                    className="control"
                    value={version}
                    disabled={!dataset || versions.isPending || !!createdId}
                    onChange={(e) => setVersion(e.target.value)}
                  >
                    <option value="">Select a version</option>
                    {versions.data?.items.map((v) => (
                      <option key={v.id} value={v.id} disabled={Number(v.record_count) === 0}>
                        {String(v.version)} · {String(v.record_count)} records
                      </option>
                    ))}
                  </select>
                )}
              </Field>
              {versions.error && <ErrorNotice error={versions.error} />}
            </div>
          </section>
          <section className="form-section">
            <div>
              <h2>Judge & provider</h2>
              <p>
                Provider credentials stay on the server. Running an evaluation may incur provider
                charges.
              </p>
            </div>
            <div className="form-stack">
              <div className="form-grid">
                <Field label="Judge">
                  {(id) => (
                    <select
                      id={id}
                      required
                      className="control"
                      value={judge}
                      disabled={!!createdId}
                      onChange={(e) => setJudge(e.target.value)}
                    >
                      <option value="">Select a judge</option>
                      {metadata.data.judges.items.map((j) => (
                        <option key={String(j.key)} value={String(j.key)}>
                          {String(j.display_name ?? j.name)}
                        </option>
                      ))}
                    </select>
                  )}
                </Field>
                <Field label="Provider">
                  {(id) => (
                    <select
                      id={id}
                      required
                      className="control"
                      value={provider}
                      disabled={!!createdId}
                      onChange={(e) => {
                        setProvider(e.target.value);
                        const p = metadata.data.providers.items.find(
                          (p) => p.key === e.target.value
                        );
                        setModel(String(p?.default_model ?? ''));
                      }}
                    >
                      <option value="">Select a provider</option>
                      {metadata.data.providers.items.map((p) => (
                        <option key={String(p.key)} value={String(p.key)}>
                          {String(p.display_name ?? p.name)}
                        </option>
                      ))}
                    </select>
                  )}
                </Field>
              </div>
              <Field label="Model" hint="Use a model supported by the selected provider.">
                {(id) => (
                  <input
                    id={id}
                    className="control"
                    value={model}
                    disabled={!!createdId}
                    onChange={(e) => setModel(e.target.value)}
                    required
                  />
                )}
              </Field>
            </div>
          </section>
          <div className="actions" style={{ justifyContent: 'flex-end' }}>
            <Link className="button" to={`/projects/${projectId}/evaluations`}>
              Cancel
            </Link>
            <Button
              type="submit"
              variant="primary"
              busy={mutation.isPending}
              disabled={DEMO_MODE || !version || !judge || !provider || !name.trim() || !!createdId}
            >
              <Play size={15} />
              {mutation.isPending ? 'Running evaluation…' : 'Run evaluation'}
            </Button>
          </div>
        </form>
      )}
    </div>
  );
}

export function DatasetView() {
  const { datasetId } = useParams();
  const { projectId } = useProject();
  const [version, setVersion] = useState('');
  const [page, setPage] = useState(1);
  const query = useQuery({
    queryKey: ['dataset', datasetId],
    queryFn: ({ signal }) => getRecord(`/datasets/${datasetId}`, signal),
  });
  const versions = (query.data?.versions ?? []) as RecordData[];
  const active = version || String(versions[0]?.id ?? '');
  const records = useQuery({
    queryKey: ['records', active, page],
    enabled: !!active,
    queryFn: ({ signal }) =>
      getPage(`/datasets/versions/${active}/records?skip=${(page - 1) * 20}&limit=20`, signal),
  });
  return (
    <div className="page">
      <PageHeader
        title={query.data?.name ?? 'Dataset'}
        description={String(
          query.data?.description ?? 'Inspect the records used in your evaluations.'
        )}
        actions={
          <Link className="button" to={`/projects/${projectId}/datasets`}>
            <ArrowLeft size={15} />
            Datasets
          </Link>
        }
      />
      {query.isPending ? (
        <Loading />
      ) : query.error ? (
        <ErrorNotice error={query.error} />
      ) : query.data.project_id !== projectId ? (
        <ErrorNotice error={new Error('This dataset belongs to another project.')} />
      ) : (
        <Panel
          title="Dataset records"
          actions={
            <label>
              <span className="sr-only">Dataset version</span>
              <select
                className="control"
                aria-label="Dataset version"
                value={active}
                onChange={(e) => {
                  setVersion(e.target.value);
                  setPage(1);
                }}
              >
                {versions.map((v) => (
                  <option key={v.id} value={v.id}>
                    {String(v.version)} · {String(v.record_count)} records
                  </option>
                ))}
              </select>
            </label>
          }
        >
          {!active ? (
            <Empty
              title="No versions yet"
              description="Import records to create the first dataset version."
            />
          ) : records.isPending ? (
            <Loading />
          ) : records.error ? (
            <ErrorNotice error={records.error} />
          ) : records.data.items.length ? (
            <>
              <DataTable
                rows={records.data.items}
                columns={[
                  { key: 'prompt', label: 'Prompt' },
                  { key: 'candidate_output', label: 'Candidate response' },
                  { key: 'reference_output', label: 'Reference answer' },
                ]}
              />
              <div className="pagination">
                <span>{records.data.total} records</span>
                <div className="actions">
                  <Button disabled={page === 1} onClick={() => setPage(page - 1)}>
                    Previous
                  </Button>
                  <Button
                    disabled={page * 20 >= records.data.total}
                    onClick={() => setPage(page + 1)}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <Empty
              title="No records in this version"
              description="Import a dataset containing prompts and reference answers."
            />
          )}
        </Panel>
      )}
    </div>
  );
}

export function EvaluationView() {
  const { evaluationId } = useParams();
  const { projectId } = useProject();
  const query = useQuery({
    queryKey: ['evaluation', evaluationId],
    queryFn: ({ signal }) => getRecord(`/experiments/${evaluationId}`, signal),
    refetchInterval: (q) => (q.state.data?.status === 'RUNNING' ? 5000 : false),
  });
  return (
    <div className="page">
      <PageHeader
        title={query.data?.name ?? 'Evaluation results'}
        description="Scores and reasoning returned by the evaluation engine."
        actions={
          <Link className="button" to={`/projects/${projectId}/evaluations`}>
            <ArrowLeft size={15} />
            Evaluations
          </Link>
        }
      />
      {query.isPending ? (
        <Loading />
      ) : query.error ? (
        <ErrorNotice error={query.error} />
      ) : query.data.project_id !== projectId ? (
        <ErrorNotice error={new Error('This evaluation belongs to another project.')} />
      ) : (
        <>
          <div className="actions">
            <Status value={query.data.status} />
            <span className="muted">
              {String(query.data.judge)} / {String(query.data.provider)} /{' '}
              {String(query.data.model ?? 'Default model')}
            </span>
          </div>
          <Panel title="Run summary">
            <div className="panel-body">
              <RecordDetails record={(query.data.metrics ?? {}) as RecordData} />
              {Object.keys((query.data.metrics ?? {}) as object).length === 0 && (
                <p className="muted">No summary metrics have been returned for this run.</p>
              )}
            </div>
          </Panel>
          <Panel title="Test case results">
            {Array.isArray(query.data.results) && query.data.results.length ? (
              <DataTable
                rows={query.data.results as RecordData[]}
                columns={[
                  { key: 'input_prompt', label: 'Prompt' },
                  { key: 'model_output', label: 'Response' },
                  { key: 'score', label: 'Score' },
                  { key: 'passed', label: 'Passed' },
                  { key: 'reasoning', label: 'Reasoning' },
                ]}
              />
            ) : (
              <Empty
                title="No results yet"
                description="Results appear after the evaluation engine finishes processing test cases."
              />
            )}
          </Panel>
        </>
      )}
    </div>
  );
}
