import { createContext, useContext, useEffect, useRef, useState } from 'react';
import { Link, NavLink, Outlet, useLocation, useNavigate, useMatch } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  ChevronRight,
  Database,
  FileText,
  FlaskConical,
  Folder,
  KeyRound,
  Layers,
  LogOut,
  Menu,
  Monitor,
  Moon,
  Settings,
  ShieldCheck,
  Sparkles,
  Sun,
  X,
  ChevronDown,
  Compass,
} from 'lucide-react';
import { DEMO_MODE, getPage, type RecordData } from '../services/client';
import { useConnection } from '../context/ConnectionContext';
import { useTheme, type Theme } from '../context/ThemeContext';
import { Button, Empty, ErrorNotice, Loading } from '../components/ui';

const Context = createContext<{ projectId: string; project?: RecordData; projects: RecordData[] }>({
  projectId: '',
  projects: [],
});
export const useProject = () => useContext(Context);
export function Brand() {
  return (
    <Link className="brand" to="/overview" aria-label="EvalForge workspace">
      <span className="brand-mark">
        <img src="/logo.png" alt="EvalForge Emblem" className="w-full h-full object-contain" />
      </span>
      <span>EvalForge</span>
    </Link>
  );
}
export function ThemeControl() {
  const { theme, setTheme } = useTheme();

  const getThemeIcon = () => {
    switch (theme) {
      case 'light':
        return <Sun size={14} className="text-[#0284C7] dark:text-[#38BDF8]" />;
      case 'dark':
        return <Moon size={14} className="text-[#38BDF8]" />;
      case 'aura':
        return <Sparkles size={14} className="text-[#A6633D]" />;
      case 'nordic':
        return <Compass size={14} className="text-[#0284C7]" />;
      case 'onyx':
        return <Sparkles size={14} className="text-[#E5B869]" />;
      default:
        return <Monitor size={14} className="text-[#7E939C]" />;
    }
  };

  return (
    <div className="theme-selector-container relative inline-flex items-center">
      <span className="sr-only">Color theme</span>
      <div className="theme-selector-icon-slot absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none flex items-center justify-center">
        {getThemeIcon()}
      </div>
      <select
        className="theme-select-input"
        aria-label="Color theme"
        value={theme}
        onChange={(e) => setTheme(e.target.value as Theme)}
      >
        <option value="system">System</option>
        <option value="light">Alpaca Silk</option>
        <option value="dark">Midnight Slate</option>
        <option value="aura">Aura Linen</option>
        <option value="nordic">Nordic Frost</option>
        <option value="onyx">Obsidian Onyx</option>
      </select>
      <div className="theme-selector-arrow-slot absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none flex items-center justify-center text-[#7E939C]">
        <ChevronDown size={13} strokeWidth={2.4} />
      </div>
    </div>
  );
}
export default function WorkspaceShell() {
  const routeId = useMatch('/projects/:projectId/*')?.params.projectId;
  const navigate = useNavigate();
  const location = useLocation();
  const { disconnect } = useConnection();
  const [selected, setSelected] = useState(() => sessionStorage.getItem('evalforge_project') || '');
  const [open, setOpen] = useState(false);
  const sidebarRef = useRef<HTMLElement>(null);
  const menuRef = useRef<HTMLButtonElement>(null);
  const query = useQuery({
    queryKey: ['projects'],
    queryFn: async ({ signal }) => {
      const first = await getPage('/projects?page_size=100', signal);
      const items = [...first.items];
      for (let page = 2; items.length < first.total; page++) {
        const next = await getPage(`/projects?page_size=100&page=${page}`, signal);
        if (!next.items.length) break;
        items.push(...next.items);
      }
      return items;
    },
  });
  const projects = query.data ?? [];
  const projectId =
    routeId || (projects.some((p) => p.id === selected) ? selected : String(projects[0]?.id ?? ''));
  const project = projects.find((p) => p.id === projectId);
  useEffect(() => {
    if (project?.id) {
      sessionStorage.setItem('evalforge_project', project.id);
      setSelected(project.id);
    }
  }, [project?.id]);
  useEffect(() => {
    setOpen(false);
    document.title = `${routeId ? 'Workspace' : 'Overview'} · EvalForge`;
  }, [location.pathname, routeId]);
  useEffect(() => {
    if (!open) return;
    const menuButton = menuRef.current;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    sidebarRef.current?.querySelector<HTMLElement>('a,button')?.focus();
    const keydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false);
      if (event.key === 'Tab') {
        const nodes = sidebarRef.current?.querySelectorAll<HTMLElement>('a[href],button,select');
        if (!nodes?.length) return;
        const first = nodes[0],
          last = nodes[nodes.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener('keydown', keydown);
    return () => {
      document.body.style.overflow = previous;
      window.removeEventListener('keydown', keydown);
      menuButton?.focus();
    };
  }, [open]);
  const path = (suffix: string) => `/projects/${projectId}/${suffix}`;
  const groups = [
    {
      name: 'Workspace',
      links: [
        { name: 'Overview', to: '/', icon: Layers },
        { name: 'Projects', to: '/projects', icon: Folder },
        ...(projectId
          ? [
              { name: 'Datasets', to: path('datasets'), icon: Database },
              { name: 'Evaluations', to: path('evaluations'), icon: FlaskConical },
              { name: 'Benchmarks', to: path('benchmarks'), icon: Activity },
            ]
          : []),
      ],
    },
    {
      name: 'Evaluation tools',
      links: projectId
        ? [
            { name: 'RAG assessments', to: path('rag'), icon: Layers },
            { name: 'Safety assessments', to: path('safety'), icon: ShieldCheck },
            { name: 'Policies', to: path('policy'), icon: FileText },
            { name: 'Reports', to: path('reports'), icon: FileText },
          ]
        : [],
    },
    {
      name: 'Operations',
      links: [
        ...(projectId ? [{ name: 'Background jobs', to: path('jobs'), icon: Activity }] : []),

        { name: 'Providers', to: '/providers', icon: Layers },
        { name: 'Developer guide', to: '/developer', icon: BookOpen },
      ],
    },
  ];
  const title =
    groups.flatMap((g) => g.links).find((item) => item.to === location.pathname)?.name || 'Details';
  return (
    <Context.Provider value={{ projectId, project, projects }}>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      {open && (
        <button
          className="sidebar-shade"
          aria-label="Close navigation"
          tabIndex={-1}
          onClick={() => setOpen(false)}
        />
      )}
      <aside
        ref={sidebarRef}
        className={`sidebar ${open ? 'open' : ''}`}
        aria-label="Workspace navigation"
        role={open ? 'dialog' : undefined}
        aria-modal={open || undefined}
      >
        <div className="actions" style={{ justifyContent: 'space-between' }}>
          <Brand />
          <Button
            className="mobile-only icon-button"
            aria-label="Close navigation"
            onClick={() => setOpen(false)}
          >
            <X size={18} />
          </Button>
        </div>
        <div className="relative w-full">
          <label className="sr-only" htmlFor="project-switcher">
            Active project
          </label>
          <select
            id="project-switcher"
            className="workspace-select"
            value={project?.id ?? ''}
            onChange={(e) => {
              const id = e.target.value;
              setSelected(id);
              const suffix = location.pathname.match(
                /^\/projects\/[^/]+\/(datasets|evaluations|benchmarks|rag|safety|policy|reports|jobs|logs)/
              )?.[1];
              navigate(suffix ? `/projects/${id}/${suffix}` : '/');
            }}
          >
            <option value="" disabled>
              {query.isPending ? 'Loading projects…' : 'Select a project'}
            </option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name || p.id}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[#7E939C] flex items-center">
            <ChevronDown size={13} strokeWidth={2.2} />
          </div>
        </div>
        <nav className="nav-scroll">
          {groups.map(
            (g) =>
              g.links.length > 0 && (
                <div key={g.name}>
                  <p className="nav-group">{g.name}</p>
                  {g.links.map((item) => (
                    <NavLink
                      key={item.to}
                      end={item.to === '/' || item.to === '/projects'}
                      to={item.to}
                      className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                      <item.icon size={17} strokeWidth={1.7} />
                      {item.name}
                    </NavLink>
                  ))}
                </div>
              )
          )}
        </nav>
        <div className="sidebar-bottom">
          <NavLink to="/settings/workspace" className="nav-link">
            <Settings size={17} />
            Workspace settings
          </NavLink>
          <button
            className="nav-link"
            style={{ width: '100%', border: 0, background: 'transparent' }}
            onClick={disconnect}
          >
            <LogOut size={17} />
            Disconnect
          </button>
        </div>
      </aside>
      <div className="app-main">
        {DEMO_MODE && (
          <div className="demo-banner">Demo workspace · Sample data · Read-only preview</div>
        )}
        <header className="topbar">
          <div className="breadcrumb">
            <button
              ref={menuRef}
              className="button mobile-only icon-button"
              aria-label="Open navigation"
              aria-expanded={open}
              onClick={() => setOpen(true)}
            >
              <Menu size={19} />
            </button>
            <span>{project?.name ?? 'Workspace'}</span>
            <ChevronRight size={14} />
            <span style={{ color: 'var(--text)' }}>{title}</span>
          </div>
          <div className="topbar-tools">
            <span className="connection-label muted" style={{ fontSize: 12 }}>
              <KeyRound size={12} style={{ display: 'inline', marginRight: 6 }} />
              API connection
            </span>
            <ThemeControl />
          </div>
        </header>
        <main id="main" className="content" tabIndex={-1}>
          {query.isPending ? (
            <Loading />
          ) : query.error ? (
            <ErrorNotice error={query.error} retry={() => void query.refetch()} />
          ) : routeId && !project ? (
            <Empty
              title="Project unavailable"
              description="This project is unavailable or outside your workspace."
              action={
                <Link className="button" to="/projects">
                  View projects
                </Link>
              }
            />
          ) : (
            <Outlet key={`${projectId}:${location.pathname}`} />
          )}
        </main>
        <footer
          className="muted"
          style={{
            padding: '0 36px 24px',
            fontSize: 12,
            display: 'flex',
            justifyContent: 'space-between',
          }}
        >
          <span>EvalForge · Evaluation workspace</span>
          <a href="https://github.com/hardikkaurani/Eval-Forge" target="_blank" rel="noreferrer">
            Documentation <ArrowUpRight size={12} style={{ display: 'inline' }} />
          </a>
        </footer>
      </div>
    </Context.Provider>
  );
}
