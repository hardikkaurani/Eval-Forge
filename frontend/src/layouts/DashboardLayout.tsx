import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useLocation, useParams } from 'react-router-dom';
import {
  Layers,
  Search,
  Database,
  Terminal,
  Activity,
  Cpu,
  User,
  Settings,
  Bell,
  LogOut,
  Menu,
  X,
  ChevronRight,
  Command,
  Clock,
  ChevronDown,
  CheckCircle2,
  ShieldAlert,
  FileText,
  KeyRound,
  Users,
  HardDrive,
  BarChart3,
  BookOpen,
  CreditCard,
  SlidersHorizontal,
  Workflow,
  Sparkles,
} from 'lucide-react';
import { useWorkspace } from '../context/WorkspaceContext';
import { useAuth } from '../context/AuthContext';
import logo from '../assets/logo.jpg';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

interface NavLinkItem {
  name: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  exact?: boolean;
  disabled?: boolean;
}

interface NavGroup {
  label: string;
  links: NavLinkItem[];
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { projectId: routeProjectId } = useParams();

  const { projects, currentProjectId, currentProject, setCurrentProjectId } = useWorkspace();
  const { user, logout } = useAuth();

  const activeProjectId = routeProjectId || currentProjectId || (projects[0]?.id ?? '');

  // Keep WorkspaceContext in sync with URL parameter if present
  useEffect(() => {
    if (routeProjectId && routeProjectId !== currentProjectId) {
      setCurrentProjectId(routeProjectId);
    }
  }, [routeProjectId, currentProjectId, setCurrentProjectId]);

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [projectDropdownOpen, setProjectDropdownOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    'Evaluation pipeline Chatbot Alignment complete (Score: 0.94)',
    'Database connection established with healthy status',
    'Rate limit alert on OpenAI provider',
  ];

  const commandPaletteRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);
  const projectDropdownRef = useRef<HTMLDivElement>(null);

  // Keyboard shortcut Ctrl+K / Cmd+K for command palette
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setCommandPaletteOpen(false);
        setShowUserMenu(false);
        setShowNotifications(false);
        setProjectDropdownOpen(false);
        setSidebarOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Click outside handlers
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (commandPaletteRef.current && !commandPaletteRef.current.contains(target)) {
        setCommandPaletteOpen(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(target)) {
        setShowUserMenu(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(target)) {
        setShowNotifications(false);
      }
      if (projectDropdownRef.current && !projectDropdownRef.current.contains(target)) {
        setProjectDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navGroups: NavGroup[] = [
    {
      label: 'Workbench',
      links: [
        { name: 'Dashboard', path: '/', icon: Layers, exact: true },
        {
          name: 'Datasets',
          path: activeProjectId ? `/projects/${activeProjectId}/datasets` : '#',
          icon: Database,
          disabled: !activeProjectId,
        },
        {
          name: 'Evaluations',
          path: activeProjectId ? `/projects/${activeProjectId}/evaluations` : '#',
          icon: Terminal,
          disabled: !activeProjectId,
        },
        {
          name: 'Benchmarks',
          path: activeProjectId ? `/projects/${activeProjectId}/benchmarks` : '#',
          icon: Activity,
          disabled: !activeProjectId,
        },
      ],
    },
    {
      label: 'Advanced AI & Safety',
      links: [
        {
          name: 'RAG Evaluation',
          path: activeProjectId ? `/projects/${activeProjectId}/rag` : '#',
          icon: Sparkles,
          disabled: !activeProjectId,
        },
        {
          name: 'Policy Rules',
          path: activeProjectId ? `/projects/${activeProjectId}/policy` : '#',
          icon: SlidersHorizontal,
          disabled: !activeProjectId,
        },
        {
          name: 'AI Safety',
          path: activeProjectId ? `/projects/${activeProjectId}/safety` : '#',
          icon: ShieldAlert,
          disabled: !activeProjectId,
        },
        {
          name: 'Reports',
          path: activeProjectId ? `/projects/${activeProjectId}/reports` : '#',
          icon: FileText,
          disabled: !activeProjectId,
        },
      ],
    },
    {
      label: 'Jobs & Execution',
      links: [
        { name: 'Providers', path: '/providers', icon: Cpu },
        { name: 'Scheduled Jobs', path: '/scheduled-jobs', icon: Clock },
        {
          name: 'Jobs Queue',
          path: activeProjectId ? `/projects/${activeProjectId}/jobs` : '#',
          icon: Workflow,
          disabled: !activeProjectId,
        },
        {
          name: 'Audit Logs',
          path: activeProjectId ? `/projects/${activeProjectId}/logs` : '#',
          icon: BarChart3,
          disabled: !activeProjectId,
        },
      ],
    },
    {
      label: 'Settings & Administration',
      links: [
        { name: 'Workspace', path: '/settings/workspace', icon: Settings },
        { name: 'Members & Access', path: '/settings/members', icon: Users },
        { name: 'API & Webhooks', path: '/settings/keys', icon: KeyRound },
        { name: 'Audit Trail', path: '/settings/audit', icon: HardDrive },
        { name: 'Billing & Usage', path: '/settings/billing', icon: CreditCard },
      ],
    },
    {
      label: 'Platform & Docs',
      links: [
        { name: 'Developer Portal', path: '/developer', icon: BookOpen },
      ],
    },
  ];

  // Command palette options
  const commands = [
    { title: 'Go to Dashboard', action: () => navigate('/') },
    { title: 'Configure Providers', action: () => navigate('/providers') },
    { title: 'View Scheduled Jobs', action: () => navigate('/scheduled-jobs') },
    { title: 'User Profile & Settings', action: () => navigate('/profile') },
    { title: 'Developer Portal & MCP', action: () => navigate('/developer') },
    ...projects.map((p) => ({
      title: `Switch Project: ${p.name}`,
      action: () => {
        setCurrentProjectId(p.id);
        navigate(`/projects/${p.id}/datasets`);
      },
    })),
  ];

  const filteredCommands = commands.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getBreadcrumbTitle = () => {
    const path = location.pathname;
    if (path === '/') return 'Dashboard';
    if (path === '/providers') return 'Providers';
    if (path === '/scheduled-jobs') return 'Scheduled Jobs';
    if (path === '/profile') return 'Profile';
    if (path === '/developer') return 'Developer Portal';
    if (path.startsWith('/settings/workspace')) return 'Workspace Settings';
    if (path.startsWith('/settings/members')) return 'Members & Access';
    if (path.startsWith('/settings/keys')) return 'API & Webhooks';
    if (path.startsWith('/settings/audit')) return 'Audit Trail';
    if (path.startsWith('/settings/billing')) return 'Billing & Usage';
    if (path.includes('/datasets')) return 'Datasets';
    if (path.includes('/evaluations')) return 'Evaluations';
    if (path.includes('/benchmarks')) return 'Benchmarks';
    if (path.includes('/rag')) return 'RAG Evaluation';
    if (path.includes('/policy')) return 'Policy Rules';
    if (path.includes('/safety')) return 'AI Safety';
    if (path.includes('/jobs')) return 'Jobs Queue';
    if (path.includes('/logs')) return 'Log Viewer';
    if (path.includes('/reports')) return 'Reports';
    return 'Workbench';
  };

  return (
    <div className="min-h-screen bg-chrome-bg flex text-chrome-text">
      {/* Mobile Drawer Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Navigation */}
      <aside
        role="navigation"
        aria-label="Main Navigation"
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-chrome-panel border-r border-chrome-border transform transition-transform duration-200 ease-in-out md:translate-x-0 md:static md:flex md:flex-col ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-chrome-border">
          <Link to="/" className="flex items-center gap-3 group">
            <img
              src={logo}
              alt="Eval-Forge Logo"
              className="w-8 h-8 rounded-md object-cover border border-chrome-border group-hover:border-brand-sky transition-colors"
            />
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-tight text-chrome-text flex items-center gap-1.5">
                Eval-Forge
                <span className="text-[10px] font-mono uppercase bg-brand-terracotta/20 text-brand-terracotta px-1.5 py-0.5 rounded border border-brand-terracotta/30">
                  OS
                </span>
              </span>
              <span className="text-[11px] font-mono text-chrome-muted -mt-0.5">
                v1.4.0 • Enterprise
              </span>
            </div>
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="md:hidden text-chrome-muted hover:text-chrome-text p-1 rounded-md"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Workspace / Project Switcher */}
        <div className="p-3 border-b border-chrome-border relative" ref={projectDropdownRef}>
          <label className="text-[10px] font-mono uppercase text-chrome-muted px-2 block mb-1">
            Active Project
          </label>
          <button
            onClick={() => setProjectDropdownOpen(!projectDropdownOpen)}
            className="w-full flex items-center justify-between px-3 py-2 rounded-md bg-chrome-bg border border-chrome-border hover:border-chrome-text text-left transition-colors"
            aria-haspopup="listbox"
            aria-expanded={projectDropdownOpen}
          >
            <div className="truncate pr-2">
              <div className="text-xs font-semibold text-chrome-text truncate">
                {currentProject ? currentProject.name : 'Select Project'}
              </div>
              <div className="text-[10px] font-mono text-chrome-muted truncate">
                {currentProject ? `${currentProject.datasets_count || 0} Datasets` : 'No project'}
              </div>
            </div>
            <ChevronDown className={`w-4 h-4 text-chrome-muted shrink-0 transition-transform ${projectDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Dropdown Menu */}
          {projectDropdownOpen && (
            <div className="absolute left-3 right-3 top-full mt-1 bg-chrome-panel border border-chrome-border rounded-md shadow-chrome z-50 py-1 max-h-60 overflow-y-auto">
              {projects.length === 0 ? (
                <div className="px-3 py-2 text-xs text-chrome-muted">No projects found</div>
              ) : (
                projects.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => {
                      setCurrentProjectId(p.id);
                      setProjectDropdownOpen(false);
                      if (location.pathname.includes('/projects/')) {
                        const parts = location.pathname.split('/');
                        const section = parts[3] || 'datasets';
                        navigate(`/projects/${p.id}/${section}`);
                      }
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex items-center justify-between hover:bg-chrome-hover transition-colors ${
                      p.id === activeProjectId ? 'bg-chrome-hover text-brand-sky font-semibold' : 'text-chrome-text'
                    }`}
                  >
                    <span className="truncate">{p.name}</span>
                    {p.id === activeProjectId && <CheckCircle2 className="w-3.5 h-3.5 text-brand-sky shrink-0" />}
                  </button>
                ))
              )}
            </div>
          )}
        </div>

        {/* Navigation Links Group */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-4">
          {navGroups.map((group, idx) => (
            <div key={idx}>
              <div className="text-[10px] font-mono uppercase text-chrome-muted px-3 mb-1.5 tracking-wider">
                {group.label}
              </div>
              <div className="space-y-0.5">
                {group.links.map((link) => {
                  const Icon = link.icon;
                  const isActive = link.exact
                    ? location.pathname === link.path
                    : location.pathname.startsWith(link.path) && link.path !== '#';

                  if (link.disabled) {
                    return (
                      <span
                        key={link.name}
                        className="flex items-center gap-3 px-3 py-1.5 rounded-md text-xs font-medium text-chrome-muted/40 cursor-not-allowed select-none"
                      >
                        <Icon className="w-4 h-4 shrink-0" />
                        <span>{link.name}</span>
                      </span>
                    );
                  }

                  return (
                    <Link
                      key={link.name}
                      to={link.path}
                      onClick={() => setSidebarOpen(false)}
                      className={`flex items-center justify-between px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                        isActive
                          ? 'bg-chrome-hover text-brand-sky border-l-2 border-brand-sky'
                          : 'text-chrome-muted hover:text-chrome-text hover:bg-chrome-hover/50'
                      }`}
                    >
                      <div className="flex items-center gap-3 truncate">
                        <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-brand-sky' : 'text-chrome-muted'}`} />
                        <span className="truncate">{link.name}</span>
                      </div>
                      {isActive && <ChevronRight className="w-3.5 h-3.5 text-brand-sky shrink-0" />}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer Info */}
        <div className="p-3 border-t border-chrome-border bg-chrome-bg/50">
          <div className="flex items-center justify-between text-[11px] font-mono text-chrome-muted">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Engine Online
            </span>
            <span>REST / WS</span>
          </div>
        </div>
      </aside>

      {/* Main Content Layout */}
      <div className="flex-1 flex flex-col min-w-0 bg-workbench-bg text-workbench-text">
        {/* Sticky Header Bar */}
        <header className="h-16 bg-chrome-panel border-b border-chrome-border sticky top-0 z-30 flex items-center justify-between px-4 md:px-8 text-chrome-text">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="md:hidden p-2 text-chrome-muted hover:text-chrome-text rounded-md"
              aria-label="Open navigation menu"
            >
              <Menu className="w-5 h-5" />
            </button>

            {/* Breadcrumb Context */}
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-chrome-muted">Eval-Forge</span>
              <ChevronRight className="w-3.5 h-3.5 text-chrome-muted" />
              {currentProject && (
                <>
                  <span className="text-chrome-muted truncate max-w-[120px] md:max-w-[200px]">
                    {currentProject.name}
                  </span>
                  <ChevronRight className="w-3.5 h-3.5 text-chrome-muted" />
                </>
              )}
              <span className="text-brand-sky font-medium">{getBreadcrumbTitle()}</span>
            </div>
          </div>

          {/* Header Controls */}
          <div className="flex items-center gap-3">
            {/* Command Palette Trigger Button */}
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="flex items-center gap-3 px-3 py-1.5 rounded-md bg-chrome-bg border border-chrome-border text-xs text-chrome-muted hover:text-chrome-text hover:border-chrome-text transition-colors"
              aria-label="Search and command palette"
            >
              <Search className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Search commands...</span>
              <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-chrome-panel border border-chrome-border text-[10px] font-mono text-chrome-muted">
                <Command className="w-2.5 h-2.5" /> K
              </kbd>
            </button>

            {/* Notifications Trigger */}
            <div className="relative" ref={notificationRef}>
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 rounded-md hover:bg-chrome-hover text-chrome-muted hover:text-chrome-text relative"
                aria-label="Notifications"
              >
                <Bell className="w-4 h-4" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-brand-terracotta" />
              </button>

              {showNotifications && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-chrome-panel border border-chrome-border rounded-md shadow-chrome z-50 p-3 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold border-b border-chrome-border pb-2">
                    <span>Notifications</span>
                    <span className="text-[10px] font-mono text-brand-sky">{notifications.length} New</span>
                  </div>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {notifications.map((n, i) => (
                      <div key={i} className="text-[11px] p-2 rounded bg-chrome-bg border border-chrome-border text-chrome-muted">
                        {n}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* User Profile Menu */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 p-1.5 rounded-md hover:bg-chrome-hover border border-transparent hover:border-chrome-border transition-colors"
                aria-label="User menu"
              >
                <div className="w-7 h-7 rounded-full bg-brand-terracotta text-white flex items-center justify-center font-bold text-xs">
                  {user?.name?.[0] || 'E'}
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-chrome-muted hidden sm:block" />
              </button>

              {showUserMenu && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-chrome-panel border border-chrome-border rounded-md shadow-chrome z-50 py-1 text-xs">
                  <div className="px-3 py-2 border-b border-chrome-border">
                    <p className="font-semibold text-chrome-text truncate">{user?.name || 'Developer'}</p>
                    <p className="text-[10px] font-mono text-chrome-muted truncate">{user?.email || 'developer@evalforge.ai'}</p>
                  </div>
                  <Link
                    to="/profile"
                    onClick={() => setShowUserMenu(false)}
                    className="flex items-center gap-2 px-3 py-2 text-chrome-muted hover:text-chrome-text hover:bg-chrome-hover transition-colors"
                  >
                    <User className="w-3.5 h-3.5" />
                    <span>Profile Settings</span>
                  </Link>
                  <button
                    onClick={() => {
                      logout();
                      setShowUserMenu(false);
                      navigate('/login');
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-red-400 hover:bg-chrome-hover transition-colors text-left"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Workbench Area */}
        <main className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>

      {/* Command Palette Modal */}
      {commandPaletteOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-start justify-center pt-20 px-4">
          <div
            ref={commandPaletteRef}
            className="w-full max-w-xl bg-chrome-panel border border-chrome-border rounded-md shadow-chrome overflow-hidden text-chrome-text"
          >
            <div className="flex items-center px-4 border-b border-chrome-border">
              <Search className="w-4 h-4 text-chrome-muted mr-3" />
              <input
                type="text"
                autoFocus
                placeholder="Type a command or search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full py-3.5 bg-transparent text-xs text-chrome-text focus:outline-none placeholder:text-chrome-muted"
              />
              <button
                onClick={() => setCommandPaletteOpen(false)}
                className="text-chrome-muted hover:text-chrome-text text-xs font-mono"
              >
                ESC
              </button>
            </div>
            <div className="max-h-72 overflow-y-auto p-2 space-y-1">
              {filteredCommands.length === 0 ? (
                <div className="px-4 py-3 text-xs text-chrome-muted text-center">No commands found</div>
              ) : (
                filteredCommands.map((c, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      c.action();
                      setCommandPaletteOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-md text-xs hover:bg-chrome-hover flex items-center justify-between transition-colors"
                  >
                    <span>{c.title}</span>
                    <ChevronRight className="w-3.5 h-3.5 text-chrome-muted" />
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
