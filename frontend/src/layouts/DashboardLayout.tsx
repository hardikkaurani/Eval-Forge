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
  Sparkles,
  Command,
  Heart
} from 'lucide-react';
import { api } from '../services/api';
import type { Project } from '../services/api';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { projectId } = useParams();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProjectName, setCurrentProjectName] = useState('Select Project');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications, setNotifications] = useState<string[]>([
    'Evaluation pipeline Chatbot Alignment complete (Score: 0.94)',
    'Database connection established with healthy status',
    'Rate limit alert on OpenAI provider'
  ]);
  const [showNotifications, setShowNotifications] = useState(false);

  const commandPaletteRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);

  // Fetch projects list for sidebar and command palette
  useEffect(() => {
    const fetchProjects = async () => {
      const projs = await api.projects.list();
      setProjects(projs);
      if (projectId) {
        const current = projs.find((p: Project) => p.id === projectId);
        if (current) setCurrentProjectName(current.name);
      }
    };
    fetchProjects();
  }, [projectId]);

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
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Click outside handlers
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (commandPaletteRef.current && !commandPaletteRef.current.contains(e.target as Node)) {
        setCommandPaletteOpen(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setShowUserMenu(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(e.target as Node)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: Layers },
    { name: 'Datasets', path: projectId ? `/projects/${projectId}/datasets` : '#', icon: Database, disabled: !projectId },
    { name: 'Evaluations', path: projectId ? `/projects/${projectId}/evaluations` : '#', icon: Terminal, disabled: !projectId },
    { name: 'Benchmarks', path: projectId ? `/projects/${projectId}/benchmarks` : '#', icon: Activity, disabled: !projectId },
    { name: 'Providers', path: '/providers', icon: Cpu },
  ];

  // Command palette commands
  const commands = [
    { title: 'Go to Dashboard', action: () => navigate('/') },
    { title: 'Configure Providers', action: () => navigate('/providers') },
    { title: 'User Profile', action: () => navigate('/profile') },
    ...projects.map((p) => ({
      title: `Switch to Project: ${p.name}`,
      action: () => navigate(`/projects/${p.id}/datasets`),
    })),
  ];

  const filteredCommands = commands.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#050816] text-white flex">
      {/* Sidebar for Desktop */}
      <aside className={`fixed inset-y-0 left-0 z-40 w-64 bg-[#111827] border-r border-[#2A3352] transform transition-transform md:translate-x-0 md:static md:flex md:flex-col ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="h-16 flex items-center justify-between px-6 border-b border-[#2A3352]">
          <Link to="/" className="flex items-center gap-3">
            <Sparkles className="text-primary w-6 h-6 animate-pulse" />
            <span className="font-heading font-bold text-xl tracking-tight text-white">EvalForge</span>
          </Link>
          <button className="md:hidden text-muted hover:text-white" onClick={() => setSidebarOpen(false)}>
            <X size={20} />
          </button>
        </div>

        {/* Project Selector dropdown inside Sidebar */}
        <div className="px-4 py-4 border-b border-[#2A3352]">
          <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Active Project</label>
          <div className="relative">
            <select
              value={projectId || ''}
              onChange={(e) => {
                if (e.target.value) {
                  navigate(`/projects/${e.target.value}/datasets`);
                } else {
                  navigate('/');
                }
              }}
              className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary appearance-none cursor-pointer"
            >
              <option value="">-- Select Project --</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none text-muted">
              <ChevronRight size={14} className="rotate-90" />
            </div>
          </div>
        </div>

        {/* Sidebar Nav Links */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = location.pathname === link.path || (link.path !== '/' && location.pathname.startsWith(link.path.replace(/\/:projectId.*/, '')));
            
            if (link.disabled) {
              return (
                <div
                  key={link.name}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-600 cursor-not-allowed text-sm"
                  title="Select a project first"
                >
                  <Icon size={18} />
                  <span>{link.name}</span>
                </div>
              );
            }

            return (
              <Link
                key={link.name}
                to={link.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all text-sm font-medium ${isActive ? 'bg-primary text-white shadow-lg shadow-primary/20' : 'text-gray-400 hover:bg-[#1f2937] hover:text-white'}`}
              >
                <Icon size={18} />
                <span>{link.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Footer in Sidebar */}
        <div className="p-4 border-t border-[#2A3352] text-xs text-gray-500 flex items-center justify-between">
          <span>v0.1.0 (Beta)</span>
          <span className="flex items-center gap-1">Made with <Heart size={10} className="text-red-500 fill-red-500" /></span>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="h-16 bg-[#111827] border-b border-[#2A3352] flex items-center justify-between px-6 sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <button className="md:hidden text-muted hover:text-white" onClick={() => setSidebarOpen(true)}>
              <Menu size={20} />
            </button>

            {/* Breadcrumbs */}
            <div className="hidden sm:flex items-center gap-2 text-sm text-gray-400">
              <Link to="/" className="hover:text-white transition">Home</Link>
              <ChevronRight size={14} className="text-gray-600" />
              {projectId ? (
                <>
                  <span className="text-gray-300 font-semibold">{currentProjectName}</span>
                  {location.pathname.includes('/datasets') && (
                    <>
                      <ChevronRight size={14} className="text-gray-600" />
                      <span className="text-white">Datasets</span>
                    </>
                  )}
                  {location.pathname.includes('/evaluations') && (
                    <>
                      <ChevronRight size={14} className="text-gray-600" />
                      <span className="text-white">Evaluations</span>
                    </>
                  )}
                  {location.pathname.includes('/benchmarks') && (
                    <>
                      <ChevronRight size={14} className="text-gray-600" />
                      <span className="text-white">Benchmarks</span>
                    </>
                  )}
                </>
              ) : (
                <span className="text-white">Workspace Overview</span>
              )}
            </div>
          </div>

          {/* User Section, Notification & Global Search */}
          <div className="flex items-center gap-4">
            {/* Global Search Input */}
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-[#050816] border border-[#2A3352] rounded-lg text-sm text-gray-400 hover:border-gray-500 transition-colors w-40 sm:w-60 text-left"
            >
              <Search size={14} />
              <span className="flex-1 truncate">Search...</span>
              <kbd className="hidden sm:inline-flex items-center gap-1 bg-[#111827] border border-[#2A3352] px-1.5 py-0.5 rounded text-[10px] font-mono text-gray-500">
                <Command size={10} />K
              </kbd>
            </button>

            {/* Notification Center */}
            <div className="relative" ref={notificationRef}>
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-[#1f2937] relative"
              >
                <Bell size={18} />
                {notifications.length > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-accent rounded-full animate-ping" />
                )}
              </button>

              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-[#111827] border border-[#2A3352] rounded-lg shadow-xl py-2 z-50">
                  <div className="px-4 py-2 border-b border-[#2A3352] flex justify-between items-center">
                    <span className="font-semibold text-sm">Notifications</span>
                    <button className="text-xs text-primary hover:underline" onClick={() => setNotifications([])}>Clear all</button>
                  </div>
                  <div className="divide-y divide-[#2A3352] max-h-60 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-4 text-center text-sm text-gray-500">No new alerts</div>
                    ) : (
                      notifications.map((notif, index) => (
                        <div key={index} className="p-3 text-xs text-gray-300 hover:bg-[#1f2937] transition-colors">
                          {notif}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* User Profile dropdown */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-[#1f2937] transition"
              >
                <div className="w-8 h-8 bg-gradient-to-tr from-primary to-accent rounded-lg flex items-center justify-center font-bold text-white text-sm">
                  HK
                </div>
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-[#111827] border border-[#2A3352] rounded-lg shadow-xl py-1 z-50">
                  <div className="px-4 py-2 border-b border-[#2A3352]">
                    <p className="text-sm font-semibold text-white">Hardik Kaurani</p>
                    <p className="text-xs text-gray-500 truncate">hardikkaurani1@gmail.com</p>
                  </div>
                  <Link to="/profile" className="flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-[#1f2937] hover:text-white" onClick={() => setShowUserMenu(false)}>
                    <User size={14} /> Profile
                  </Link>
                  <Link to="/providers" className="flex items-center gap-2 px-4 py-2 text-sm text-gray-300 hover:bg-[#1f2937] hover:text-white" onClick={() => setShowUserMenu(false)}>
                    <Settings size={14} /> Providers Config
                  </Link>
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      navigate('/login');
                    }}
                    className="w-full text-left flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-red-950/20 hover:text-red-300"
                  >
                    <LogOut size={14} /> Log Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Wrapper */}
        <main className="flex-1 p-6 overflow-y-auto">
          {children}
        </main>
      </div>

      {/* Keyboard Command Palette Dialog Modal */}
      {commandPaletteOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-start justify-center pt-24 px-4">
          <div ref={commandPaletteRef} className="w-full max-w-xl bg-[#111827] border border-[#2A3352] rounded-xl shadow-2xl overflow-hidden">
            <div className="p-3 border-b border-[#2A3352] flex items-center gap-2">
              <Search className="text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search projects, shortcuts, commands..."
                className="w-full bg-transparent border-0 text-white placeholder-gray-500 focus:outline-none focus:ring-0 text-sm"
                autoFocus
              />
              <button
                className="text-xs bg-[#050816] border border-[#2A3352] px-1.5 py-0.5 rounded text-gray-400"
                onClick={() => setCommandPaletteOpen(false)}
              >
                ESC
              </button>
            </div>
            <div className="max-h-80 overflow-y-auto p-2">
              {filteredCommands.length === 0 ? (
                <div className="py-8 text-center text-sm text-gray-500">No results found for &ldquo;{searchQuery}&rdquo;</div>
              ) : (
                filteredCommands.map((cmd, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      cmd.action();
                      setCommandPaletteOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-300 hover:bg-primary hover:text-white transition flex items-center justify-between"
                  >
                    <span>{cmd.title}</span>
                    <span className="text-xs opacity-50 font-mono">Action</span>
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
