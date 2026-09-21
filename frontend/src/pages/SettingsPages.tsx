import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Button,
  ErrorNotice,
  Field,
  Loading,
  PageHeader,
  Panel,
  RecordDetails,
} from '../components/ui';
import { useConnection } from '../context/ConnectionContext';
import { ThemeControl, useProject } from '../layouts/WorkspaceShell';
import { API_URL, client, DEMO_MODE, getRecord } from '../services/client';
export function WorkspaceSettingsPage() {
  const { project } = useProject();
  const cache = useQueryClient();
  const [name, setName] = useState(String(project?.name ?? ''));
  const [description, setDescription] = useState(String(project?.description ?? ''));
  const mutation = useMutation({
    mutationFn: () => client.patch(`/projects/${project?.id}`, { name: name.trim(), description }),
    onSuccess: () => cache.invalidateQueries({ queryKey: ['projects'] }),
  });
  return (
    <div className="page form-width">
      <PageHeader
        title="Workspace settings"
        description="Manage the active project and your workspace preferences."
      />
      <section className="form-section">
        <div>
          <h2>Appearance</h2>
          <p>Choose a theme or follow your system setting.</p>
        </div>
        <ThemeControl />
      </section>
      {project && (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!mutation.isPending) mutation.mutate();
          }}
          className="form-section"
        >
          <div>
            <h2>Project details</h2>
            <p>Changes apply to the active project.</p>
          </div>
          <div className="form-stack">
            {mutation.error && <ErrorNotice error={mutation.error} />}{' '}
            {mutation.isSuccess && (
              <div className="notice" role="status">
                Project settings saved.
              </div>
            )}
            <Field label="Project name">
              {(id) => (
                <input
                  id={id}
                  className="control"
                  required
                  maxLength={255}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              )}
            </Field>
            <Field label="Description">
              {(id) => (
                <textarea
                  id={id}
                  className="control"
                  maxLength={2000}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              )}
            </Field>
            <div>
              <Button
                type="submit"
                variant="primary"
                busy={mutation.isPending}
                disabled={DEMO_MODE || !name.trim()}
              >
                Save changes
              </Button>
            </div>
          </div>
        </form>
      )}
      <section className="form-section">
        <div>
          <h2>Administration</h2>
          <p>These pages require the appropriate organization permissions.</p>
        </div>
        <div className="actions">
          <Link className="button" to="/settings/members">
            Members & access
          </Link>
          <Link className="button" to="/settings/audit">
            Audit log
          </Link>
          <Link className="button" to="/settings/billing">
            Billing
          </Link>
          <Link className="button" to="/settings/keys">
            API keys & webhooks
          </Link>
          <Link className="button" to="/settings/system">
            System status
          </Link>
        </div>
      </section>
    </div>
  );
}
export function ConnectionPage() {
  const { disconnect } = useConnection();
  const query = useQuery({
    queryKey: ['connection'],
    queryFn: ({ signal }) => getRecord('/connection', signal),
    enabled: !DEMO_MODE,
  });
  return (
    <div className="page form-width">
      <PageHeader
        title="Connection settings"
        description="This workspace uses an API key rather than a personal account."
      />
      <Panel title="Current connection">
        <div className="panel-body form-stack">
          <div>
            <span className="muted">API endpoint</span>
            <pre>{API_URL}</pre>
          </div>
          {DEMO_MODE ? (
            <p>Read-only demo mode. No API key is in use.</p>
          ) : query.isPending ? (
            <Loading />
          ) : query.error ? (
            <ErrorNotice error={query.error} />
          ) : (
            <RecordDetails record={query.data} />
          )}
          <p className="muted">
            The API key is kept for this browser session. Disconnecting removes it and clears cached
            workspace data.
          </p>
          <div>
            <Button variant="danger" onClick={disconnect}>
              Disconnect workspace
            </Button>
          </div>
        </div>
      </Panel>
    </div>
  );
}
export function SystemPage() {
  const query = useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => getRecord('/health', signal),
    enabled: !DEMO_MODE,
  });
  return (
    <div className="page">
      <PageHeader
        title="System status"
        description="Status reported by the connected backend. Server configuration is managed by your administrator."
      />
      {DEMO_MODE ? (
        <div className="notice">System health is unavailable in demo mode.</div>
      ) : query.isPending ? (
        <Loading />
      ) : query.error ? (
        <ErrorNotice error={query.error} retry={() => void query.refetch()} />
      ) : (
        <Panel title="Service health">
          <div className="panel-body">
            <RecordDetails record={query.data} />
          </div>
        </Panel>
      )}
    </div>
  );
}
export function DeveloperGuide() {
  return (
    <div className="page form-width">
      <PageHeader
        title="Developer guide"
        description="Connect your existing evaluation pipeline to Evalium."
      />
      <Panel title="A repeatable evaluation workflow">
        <div className="panel-body form-stack">
          <div>
            <h3>1. Create a project and import a dataset</h3>
            <p className="muted">
              Include a prompt, candidate response, and reference answer for each test case. Select
              a specific dataset version when creating an evaluation.
            </p>
          </div>
          <div>
            <h3>2. Configure the provider on your server</h3>
            <p className="muted">
              Keep provider credentials in backend environment variables. The Providers page lists
              registered capabilities; it does not verify credentials.
            </p>
          </div>
          <div>
            <h3>3. Run an evaluation and inspect results</h3>
            <p className="muted">
              Choose a registered judge and provider. Review individual scores and reasoning
              alongside the original inputs. Failed or incomplete runs remain visible.
            </p>
          </div>
        </div>
      </Panel>
      <Panel title="API access">
        <div className="panel-body form-stack">
          <p>
            Send your workspace key in the X-API-Key header. Never embed credentials in source code
            or URLs.
          </p>
          <pre>{'curl "$EVALFORGE_API_URL/projects" \\\n  -H "X-API-Key: $EVALFORGE_API_KEY"'}</pre>
          <p className="muted">
            Registration and password reset are not supported by this API-key deployment.
            Administrators provision keys using the server bootstrap command.
          </p>
          <a
            className="table-link"
            href="https://github.com/hardikkaurani/Evalium"
            target="_blank"
            rel="noreferrer"
          >
            Repository and API documentation
          </a>
        </div>
      </Panel>
    </div>
  );
}
