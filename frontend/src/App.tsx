import { useEffect, useState } from 'react';
import {
  Activity,
  Layers,
  FolderTree,
  Terminal,
  Cpu,
  BookOpen,
  CheckCircle,
  AlertTriangle,
  RefreshCw,
  FileCode,
} from 'lucide-react';

interface HealthStatus {
  status: string;
  services: {
    api: string;
    database: string;
  };
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/health');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setHealth(data);
    } catch (err) {
      console.error('Error fetching health check:', err);
      setError('Could not connect to FastAPI server. Ensure the backend is running.');
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="app-container">
      {/* Hero Header */}
      <header className="hero">
        <div className="badge">
          <Activity size={14} />
          Phase 1: Foundation Completed
        </div>
        <h1 className="title-gradient">EvalForge</h1>
        <p className="subtitle">
          Production-grade open-source LLM evaluation platform with G-Eval, LLM-as-a-Judge, and
          custom pipeline tooling.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary" onClick={checkHealth} disabled={loading}>
            {loading ? <RefreshCw size={18} className="animate-spin" /> : <RefreshCw size={18} />}
            Trigger Health Check
          </button>
          <a href="#architecture" className="btn btn-secondary">
            <Layers size={18} />
            View Architecture
          </a>
        </div>
      </header>

      {/* Main Grid */}
      <main className="dashboard-grid">
        {/* Monorepo Architecture Map */}
        <section className="card" id="architecture">
          <h2 className="card-title">
            <FolderTree size={22} />
            Repository Structure & Architecture
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
            A unified, scalable monorepo structure separating frontend, backend, and configurations.
          </p>
          <pre className="tree">
            <span className="tree-folder">eval-forge/</span>
            {'\n'}
            ├── <span className="tree-folder">backend/</span>{' '}
            <span className="tree-comment"># FastAPI Application Root</span>
            {'\n'}│ ├── <span className="tree-folder">app/</span>
            {'\n'}│ │ ├── <span className="tree-folder">api/</span>{' '}
            <span className="tree-comment"># Endpoints and routers</span>
            {'\n'}│ │ ├── <span className="tree-folder">config/</span>{' '}
            <span className="tree-comment"># Pydantic Settings & Config</span>
            {'\n'}│ │ ├── <span className="tree-folder">core/</span>{' '}
            <span className="tree-comment"># Exceptions & Structured Logging</span>
            {'\n'}│ │ ├── <span className="tree-folder">database/</span>{' '}
            <span className="tree-comment"># SQLAlchemy session & Base model</span>
            {'\n'}│ │ ├── <span className="tree-folder">models/</span>{' '}
            <span className="tree-comment"># Database schemas / models</span>
            {'\n'}│ │ ├── <span className="tree-folder">schemas/</span>{' '}
            <span className="tree-comment"># Pydantic data schemas</span>
            {'\n'}│ │ ├── <span className="tree-folder">services/</span>{' '}
            <span className="tree-comment"># Business / Evaluation logic</span>
            {'\n'}│ │ └── <span className="tree-file">main.py</span>{' '}
            <span className="tree-comment"># FastAPI startup, CORS, lifespan</span>
            {'\n'}│ ├── <span className="tree-file">.env.example</span>
            {'\n'}│ ├── <span className="tree-file">pyproject.toml</span>{' '}
            <span className="tree-comment"># Ruff & Black config</span>
            {'\n'}│ └── <span className="tree-file">requirements.txt</span>
            {'\n'}
            ├── <span className="tree-folder">frontend/</span>{' '}
            <span className="tree-comment"># React + Vite Client</span>
            {'\n'}│ ├── <span className="tree-folder">src/</span>
            {'\n'}│ │ ├── <span className="tree-folder">components/</span>{' '}
            <span className="tree-comment"># Shared design system components</span>
            {'\n'}│ │ ├── <span className="tree-folder">pages/</span>{' '}
            <span className="tree-comment"># Page modules</span>
            {'\n'}│ │ ├── <span className="tree-folder">hooks/</span>{' '}
            <span className="tree-comment"># Custom React hooks</span>
            {'\n'}│ │ ├── <span className="tree-folder">services/</span>{' '}
            <span className="tree-comment"># API fetch & client connections</span>
            {'\n'}│ │ └── <span className="tree-folder">layouts/</span>{' '}
            <span className="tree-comment"># Root wrapper layouts</span>
            {'\n'}│ └── <span className="tree-file">package.json</span>
            {'\n'}
            ├── <span className="tree-folder">docker/</span>{' '}
            <span className="tree-comment"># Docker configuration files</span>
            {'\n'}
            └── <span className="tree-file">docker-compose.yml</span>{' '}
            <span className="tree-comment"># Monorepo orchestration</span>
          </pre>
        </section>

        {/* Status Panel */}
        <section className="card status-panel">
          <h3 className="card-title">
            <Cpu size={20} />
            Services Monitor
          </h3>

          <div className="service-status-row">
            <span className="service-name">
              <Terminal size={16} /> FastAPI Server
            </span>
            {loading ? (
              <span className="status-pill status-checking">Checking...</span>
            ) : health ? (
              <span className="status-pill status-online">Online</span>
            ) : (
              <span className="status-pill status-offline">Offline</span>
            )}
          </div>

          <div className="service-status-row">
            <span className="service-name">
              <FileCode size={16} /> PostgreSQL Database
            </span>
            {loading ? (
              <span className="status-pill status-checking">Checking...</span>
            ) : health?.services.database === 'healthy' ? (
              <span className="status-pill status-online">Connected</span>
            ) : (
              <span className="status-pill status-offline">Offline</span>
            )}
          </div>

          {error && (
            <div
              style={{
                display: 'flex',
                gap: '0.5rem',
                color: 'var(--accent-red)',
                fontSize: '0.85rem',
                padding: '0.75rem',
                background: 'rgba(239, 68, 68, 0.05)',
                borderRadius: '8px',
                border: '1px solid rgba(239, 68, 68, 0.1)',
                lineHeight: '1.4',
              }}
            >
              <AlertTriangle size={20} style={{ flexShrink: 0 }} />
              <div>{error}</div>
            </div>
          )}

          {!error && health && (
            <div
              style={{
                display: 'flex',
                gap: '0.5rem',
                color: 'var(--accent-green)',
                fontSize: '0.85rem',
                padding: '0.75rem',
                background: 'rgba(16, 185, 129, 0.05)',
                borderRadius: '8px',
                border: '1px solid rgba(16, 185, 129, 0.1)',
              }}
            >
              <CheckCircle size={16} style={{ flexShrink: 0 }} />
              <span>All foundational backend configurations validated successfully!</span>
            </div>
          )}
        </section>
      </main>

      {/* Tech Stack Summary */}
      <section className="card">
        <h3 className="card-title">
          <BookOpen size={20} />
          Foundational Tech Stack
        </h3>
        <div className="mini-grid">
          <div className="mini-card">
            <span className="tech-tag tag-fastapi">FastAPI</span>
            <h4>Python 3.11+ Backend</h4>
            <p>Fast, robust API framework with automatic OpenAPI docs and structured logging.</p>
          </div>
          <div className="mini-card">
            <span className="tech-tag tag-react">React + TS</span>
            <h4>TypeScript Client</h4>
            <p>Vite-powered, lightning fast client application with static typing.</p>
          </div>
          <div className="mini-card">
            <span className="tech-tag tag-postgres">PostgreSQL</span>
            <h4>SQL Database</h4>
            <p>Relational storage connection using SQLAlchemy async engine.</p>
          </div>
          <div className="mini-card">
            <span className="tech-tag tag-redis">Redis</span>
            <h4>Cache & Queue</h4>
            <p>In-memory cache and pipeline broker for asynchronous evaluation tasks.</p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer>
        <p>EvalForge Project Base &bull; Built with standard engineering principles.</p>
      </footer>
    </div>
  );
}

export default App;
