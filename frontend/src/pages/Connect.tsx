import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation } from 'react-router-dom';
import { Database, FlaskConical, KeyRound, ArrowRight } from 'lucide-react';
import { useConnection } from '../context/ConnectionContext';
import { ThemeControl } from '../layouts/WorkspaceShell';
import { Button, ErrorNotice, Field } from '../components/ui';
export default function Connect() {
  const { connected, connect } = useConnection();
  const { pathname } = useLocation();
  const [key, setKey] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  if (connected) return <Navigate to="/overview" replace />;
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      await connect(key);
      setKey('');
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="login-page bg-[#F6F4EE] dark:bg-[#182026]">
      <section className="login-story bg-white dark:bg-[#202A32] border-r border-[#DDE4E1] dark:border-[#2E3A44]">
        <div className="flex items-center justify-between">
          <Link to="/" className="inline-flex items-center gap-2 text-xs font-mono text-[#7E939C] hover:text-[#0284C7] transition-colors">
            <span>← Back to Overview</span>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg overflow-hidden bg-[#2E3A44] p-1 border border-[#DDE4E1] dark:border-[#2E3A44]">
              <img src="/logo.png" alt="EvalForge" className="w-full h-full object-contain" />
            </div>
            <span className="font-serif text-lg font-bold text-[#2E3A44] dark:text-[#F6F4EE]">EvalForge</span>
          </div>
        </div>
        <div className="login-story-content">
          <h1>
            Better evaluations.
            <br />
            Clearer decisions.
          </h1>
          <p>
            A focused workspace for testing model responses, inspecting results, and tracking what
            changed.
          </p>
          <div style={{ marginTop: 44 }}>
            <div className="login-feature">
              <Database size={20} />
              <div>
                <h3>Start with your data</h3>
                <p>Organize prompts and reference answers in versioned datasets.</p>
              </div>
            </div>
            <div className="login-feature">
              <FlaskConical size={20} />
              <div>
                <h3>Inspect every result</h3>
                <p>Compare scores, review reasoning, and investigate failures.</p>
              </div>
            </div>
          </div>
        </div>
        <div className="login-story-footer muted" style={{ fontSize: 12 }}>
          Open source. Self-hosted. Connected to your infrastructure.
        </div>
      </section>
      <section className="login-form-area">
        <div className="login-form">
          <div style={{ marginBottom: 30 }}>
            <ThemeControl />
          </div>
          <h1>Connect your workspace</h1>
          <p>Enter an EvalForge API key to access your projects.</p>
          {pathname !== '/login' && (
            <div className="notice info" style={{ marginBottom: 20 }}>
              This installation uses API keys. Account registration and password recovery are not
              available. Ask your administrator for a key.
            </div>
          )}
          <form className="form-stack" onSubmit={submit}>
            {error !== null && <ErrorNotice error={error} />}
            <Field
              label="API key"
              hint="Stored for this browser session only. Disconnect to remove it."
            >
              {(id) => (
                <input
                  id={id}
                  className="control mono"
                  type="password"
                  autoComplete="off"
                  spellCheck={false}
                  required
                  placeholder="Enter your workspace API key"
                  value={key}
                  onChange={(e) => setKey(e.target.value)}
                />
              )}
            </Field>
            <Button type="submit" variant="primary" busy={busy} disabled={!key.trim()}>
              <KeyRound size={16} />
              Connect workspace
              <ArrowRight size={16} />
            </Button>
          </form>
          <details className="setup-help">
            <summary>Need an API key?</summary>
            <p>
              Ask your EvalForge administrator for a workspace-scoped API key. Server administrators
              can use the bootstrap command in the setup guide.
            </p>
            <p>
              Provider keys from OpenAI or other model services are configured on the backend and
              cannot be used here.
            </p>
            <a
              href="https://github.com/hardikkaurani/Eval-Forge/blob/main/docs/ui-setup.md"
              target="_blank"
              rel="noreferrer"
            >
              Read the setup guide
            </a>
          </details>
          <p className="muted" style={{ fontSize: 12, marginTop: 24 }}>
            Trouble connecting? Confirm that the backend is running and accessible from this
            browser.
          </p>
          <Link to="/login" className="sr-only">
            Connection page
          </Link>
        </div>
      </section>
    </div>
  );
}
