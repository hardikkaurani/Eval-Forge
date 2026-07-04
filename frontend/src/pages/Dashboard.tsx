import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Layers,
  Plus,
  ArrowRight,
  TrendingUp,
  Database,
  Terminal,
  Activity,
  Trash2,
  Layers2
} from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../services/api';
import type { Project } from '../services/api';

const chartData = [
  { name: 'Mon', executions: 4 },
  { name: 'Tue', executions: 8 },
  { name: 'Wed', executions: 15 },
  { name: 'Thu', executions: 12 },
  { name: 'Fri', executions: 22 },
  { name: 'Sat', executions: 14 },
  { name: 'Sun', executions: 25 },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [newProjName, setNewProjName] = useState('');
  const [newProjDesc, setNewProjDesc] = useState('');

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const projs = await api.projects.list();
      setProjects(projs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjName.trim()) return;
    await api.projects.create({ name: newProjName, description: newProjDesc });
    setNewProjName('');
    setNewProjDesc('');
    setCreateOpen(false);
    fetchDashboardData();
  };

  const handleDeleteProject = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this project?')) {
      await api.projects.delete(id);
      fetchDashboardData();
    }
  };

  // Compute stats
  const totalDatasets = projects.reduce((acc, p) => acc + (p.datasets_count || 0), 0);
  const totalBenchmarks = projects.reduce((acc, p) => acc + (p.benchmarks_count || 0), 0);
  const totalEvaluations = projects.reduce((acc, p) => acc + (p.evaluations_count || 0), 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-8"
    >
      {/* Header section */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-heading font-bold text-3xl text-white">Enterprise Workspace</h1>
          <p className="text-gray-400 text-sm mt-1">Manage evaluation pipelines, datasets and benchmarks.</p>
        </div>
        <button
          onClick={() => setCreateOpen(true)}
          className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white font-medium px-4 py-2.5 rounded-lg shadow-lg shadow-primary/20 transition-all"
        >
          <Plus size={16} /> New Project
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {[
          { title: 'Active Projects', value: projects.length, icon: Layers2, color: 'text-indigo-400' },
          { title: 'Total Datasets', value: totalDatasets, icon: Database, color: 'text-cyan-400' },
          { title: 'Benchmark Suites', value: totalBenchmarks, icon: Activity, color: 'text-purple-400' },
          { title: 'Evaluation Runs', value: totalEvaluations, icon: Terminal, color: 'text-emerald-400' },
        ].map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-[#111827] border border-[#2A3352] rounded-xl p-5 hover:border-gray-500 transition-colors flex items-center justify-between">
              <div>
                <span className="text-xs uppercase text-gray-500 font-semibold tracking-wider">{stat.title}</span>
                <h3 className="text-3xl font-bold font-heading text-white mt-1.5">{stat.value}</h3>
              </div>
              <div className={`p-3 bg-[#050816] rounded-lg border border-[#2A3352] ${stat.color}`}>
                <Icon size={20} />
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Charts & Health Monitor Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Performance Chart */}
        <div className="bg-[#111827] border border-[#2A3352] rounded-xl p-6 lg:col-span-2">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="font-heading font-bold text-lg text-white">Evaluation Activity</h3>
              <p className="text-xs text-gray-500 mt-0.5">Pipeline execution volume over the past 7 days.</p>
            </div>
            <span className="flex items-center gap-1.5 text-xs text-accent font-semibold bg-accent/10 px-2 py-1 rounded">
              <TrendingUp size={12} /> +18.4% this week
            </span>
          </div>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorExecutions" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4F46E5" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#4F46E5" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" stroke="#9ca3af" fontSize={11} tickLine={false} axisLine={false} />
                <YAxis stroke="#9ca3af" fontSize={11} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#2A3352', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="executions" stroke="#4F46E5" strokeWidth={2} fillOpacity={1} fill="url(#colorExecutions)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* System Monitor & API latency info */}
        <div className="bg-[#111827] border border-[#2A3352] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <h3 className="font-heading font-bold text-lg text-white">System Performance</h3>
            <p className="text-xs text-gray-500 mt-0.5">Real-time infrastructure health parameters.</p>
            <div className="space-y-4 mt-6">
              <div className="flex justify-between items-center text-sm border-b border-[#2A3352]/40 pb-2">
                <span className="text-gray-400">REST API Status</span>
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" /> Active
                </span>
              </div>
              <div className="flex justify-between items-center text-sm border-b border-[#2A3352]/40 pb-2">
                <span className="text-gray-400">Database Engine</span>
                <span className="text-emerald-400 font-semibold">PostgreSQL</span>
              </div>
              <div className="flex justify-between items-center text-sm border-b border-[#2A3352]/40 pb-2">
                <span className="text-gray-400">Average Judge Latency</span>
                <span className="text-cyan-400 font-mono">485ms</span>
              </div>
              <div className="flex justify-between items-center text-sm pb-2">
                <span className="text-gray-400">Uptime</span>
                <span className="text-white">99.98%</span>
              </div>
            </div>
          </div>
          <div className="pt-4 border-t border-[#2A3352] mt-6 flex justify-between items-center text-xs text-gray-500">
            <span>Server Response Time: <b className="text-white">12ms</b></span>
            <span>CLI Engine: <b className="text-white">1.0.4</b></span>
          </div>
        </div>
      </div>

      {/* Projects List */}
      <div className="bg-[#111827] border border-[#2A3352] rounded-xl overflow-hidden">
        <div className="px-6 py-5 border-b border-[#2A3352]">
          <h3 className="font-heading font-bold text-lg text-white">Projects</h3>
          <p className="text-xs text-gray-500 mt-0.5">Select a project to manage datasets, evaluations and benchmarks.</p>
        </div>
        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="p-12 text-center text-gray-500 space-y-3">
            <Layers className="mx-auto w-12 h-12 opacity-55" />
            <p>No projects found in this workspace.</p>
            <button
              onClick={() => setCreateOpen(true)}
              className="text-primary hover:underline font-semibold"
            >
              Create one now
            </button>
          </div>
        ) : (
          <div className="divide-y divide-[#2A3352]">
            {projects.map((proj) => (
              <div
                key={proj.id}
                onClick={() => navigate(`/projects/${proj.id}/datasets`)}
                className="px-6 py-5 flex flex-col sm:flex-row justify-between items-start sm:items-center hover:bg-[#1f2937]/40 transition-colors cursor-pointer group"
              >
                <div className="space-y-1 max-w-xl">
                  <h4 className="font-heading font-bold text-white text-base group-hover:text-primary transition-colors flex items-center gap-2">
                    {proj.name}
                    <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity text-primary" />
                  </h4>
                  <p className="text-sm text-gray-400 line-clamp-1">{proj.description}</p>
                </div>
                <div className="flex items-center gap-6 mt-4 sm:mt-0 text-sm text-gray-500 self-end sm:self-auto">
                  <div className="flex gap-4">
                    <span><b>{proj.datasets_count}</b> datasets</span>
                    <span><b>{proj.benchmarks_count}</b> benchmarks</span>
                    <span><b>{proj.evaluations_count}</b> runs</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteProject(proj.id, e)}
                    className="p-1.5 text-gray-500 hover:text-red-400 hover:bg-red-950/20 rounded transition"
                    title="Delete Project"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* New Project Dialog Modal */}
      {createOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="w-full max-w-md bg-[#111827] border border-[#2A3352] rounded-xl shadow-2xl overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-[#2A3352] flex justify-between items-center">
              <h3 className="font-heading font-bold text-white">Create New Project</h3>
              <button onClick={() => setCreateOpen(false)} className="text-muted hover:text-white">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleCreateProject} className="p-6 space-y-4">
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Project Name</label>
                <input
                  type="text"
                  required
                  value={newProjName}
                  onChange={(e) => setNewProjName(e.target.value)}
                  placeholder="e.g. Code Translation Evaluator"
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Description</label>
                <textarea
                  value={newProjDesc}
                  onChange={(e) => setNewProjDesc(e.target.value)}
                  placeholder="Summarize the validation pipeline or model category..."
                  rows={3}
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4 border-t border-[#2A3352]/40">
                <button
                  type="button"
                  onClick={() => setCreateOpen(false)}
                  className="px-4 py-2 border border-[#2A3352] text-gray-400 hover:text-white rounded-lg text-sm transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-sm font-semibold transition"
                >
                  Create Project
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </motion.div>
  );
}

// Simple Helper X close icon
function X({ size }: { size?: number }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size || 24} height={size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-x">
      <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
    </svg>
  );
}
