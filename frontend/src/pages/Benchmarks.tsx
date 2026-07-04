import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Plus,
  Trophy
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '../services/api';

const benchmarkComparisonData = [
  { name: 'Safety Refusal', 'GPT-4o': 94, 'Claude 3.5 Sonnet': 98, 'Llama 3 8B': 78 },
  { name: 'SQL Generation', 'GPT-4o': 88, 'Claude 3.5 Sonnet': 92, 'Llama 3 8B': 62 },
  { name: 'Context Retrieval', 'GPT-4o': 90, 'Claude 3.5 Sonnet': 89, 'Llama 3 8B': 81 },
  { name: 'Formatting Accuracy', 'GPT-4o': 96, 'Claude 3.5 Sonnet': 95, 'Llama 3 8B': 88 },
];

export default function Benchmarks() {
  const { projectId } = useParams<{ projectId: string }>();
  const [suites, setSuites] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [datasets, setDatasets] = useState<any[]>([]);

  // Form states
  const [suiteName, setSuiteName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedDatasets, setSelectedDatasets] = useState<string[]>([]);
  const [tagsString, setTagsString] = useState('production, safety');

  const fetchBenchmarks = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const data = await api.benchmarks.list(projectId);
      setSuites(data);
      const ds = await api.datasets.list(projectId);
      setDatasets(ds);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBenchmarks();
  }, [projectId]);

  const handleCreateSuite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !suiteName.trim()) return;

    const tags = tagsString.split(',').map((t) => t.trim()).filter((t) => t.length > 0);

    try {
      await api.benchmarks.create({
        name: suiteName,
        description,
        tags,
        dataset_ids: selectedDatasets,
      }, projectId);

      setSuiteName('');
      setDescription('');
      setSelectedDatasets([]);
      setCreateOpen(false);
      fetchBenchmarks();
    } catch (err) {
      console.error(err);
      alert('Error creating suite');
    }
  };

  const handleDatasetToggle = (dsId: string) => {
    setSelectedDatasets((prev) =>
      prev.includes(dsId) ? prev.filter((id) => id !== dsId) : [...prev, dsId]
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-8"
    >
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-heading font-bold text-3xl text-white">Benchmark Analytics</h1>
          <p className="text-gray-400 text-sm mt-1">Cross-examine model scores, safety indices, retrieval leaderboards.</p>
        </div>
        <button
          onClick={() => setCreateOpen(true)}
          className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white font-medium px-4 py-2.5 rounded-lg shadow-lg shadow-primary/20 transition-all text-sm"
        >
          <Plus size={16} /> New Benchmark Suite
        </button>
      </div>

      {/* Comparisons charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model capabilities Comparison */}
        <div className="bg-[#111827] border border-[#2A3352] rounded-xl p-6 lg:col-span-2">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="font-heading font-bold text-lg text-white">Capability Benchmark Matrix</h3>
              <p className="text-xs text-gray-500 mt-0.5">Model scoring breakdown across safety, SQL generation, context, and formatting.</p>
            </div>
            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/20 px-2 py-0.5 rounded border border-emerald-900/30">
              Updated Live
            </span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={benchmarkComparisonData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#9ca3af" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#9ca3af" fontSize={10} tickLine={false} axisLine={false} domain={[0, 100]} />
                <Tooltip contentStyle={{ backgroundColor: '#111827', borderColor: '#2A3352', borderRadius: '8px' }} />
                <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px', color: '#fff' }} />
                <Bar dataKey="GPT-4o" fill="#4F46E5" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Claude 3.5 Sonnet" fill="#06B6D4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Llama 3 8B" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Model Leaderboard */}
        <div className="bg-[#111827] border border-[#2A3352] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Trophy size={16} className="text-yellow-400" />
              <h3 className="font-heading font-bold text-base text-white">Leaderboard Rank</h3>
            </div>
            <div className="space-y-3.5">
              {[
                { rank: 1, name: 'Claude 3.5 Sonnet', score: '94.2%', cost: '$$$', status: 'Active' },
                { rank: 2, name: 'GPT-4o', score: '91.0%', cost: '$$', status: 'Active' },
                { rank: 3, name: 'Llama 3 8B Local', score: '77.3%', cost: '$', status: 'Self-hosted' },
              ].map((model) => (
                <div key={model.rank} className="flex justify-between items-center bg-[#050816]/30 border border-[#2A3352] p-3 rounded-lg text-xs">
                  <div className="flex items-center gap-3">
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center font-bold text-white ${
                      model.rank === 1 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                      model.rank === 2 ? 'bg-gray-400/20 text-gray-300 border border-gray-400/30' :
                      'bg-amber-700/20 text-amber-600 border border-amber-800/30'
                    }`}>{model.rank}</span>
                    <div>
                      <span className="font-semibold text-white block">{model.name}</span>
                      <span className="text-[10px] text-gray-500">{model.status}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-primary block">{model.score}</span>
                    <span className="text-[9px] text-gray-500 font-mono">Cost: {model.cost}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="text-center text-[10px] text-gray-500 mt-4 pt-4 border-t border-[#2A3352]/40">
            Leaderboard calculated across all evaluation suites.
          </div>
        </div>
      </div>

      {/* Benchmark Suites List */}
      <div className="bg-[#111827] border border-[#2A3352] rounded-xl overflow-hidden">
        <div className="px-6 py-5 border-b border-[#2A3352] bg-[#050816]/30">
          <h3 className="font-heading font-bold text-lg text-white">Active Suites</h3>
          <p className="text-xs text-gray-500 mt-0.5">List of active benchmark definitions in this project.</p>
        </div>
        {loading ? (
          <div className="p-6 text-center text-sm text-gray-500">Loading benchmark suites...</div>
        ) : suites.length === 0 ? (
          <div className="p-12 text-center text-sm text-gray-500">No benchmark suites defined. Click New Suite to define one.</div>
        ) : (
          <div className="divide-y divide-[#2A3352]">
            {suites.map((suite) => (
              <div key={suite.id} className="p-6 flex justify-between items-center hover:bg-[#1f2937]/20 transition-colors">
                <div className="space-y-1.5">
                  <h4 className="font-semibold text-white text-base">{suite.name}</h4>
                  <p className="text-sm text-gray-400">{suite.description}</p>
                  <div className="flex gap-2">
                    {suite.tags.map((tag: string) => (
                      <span key={tag} className="text-[9px] uppercase font-bold tracking-wider text-cyan-400 bg-cyan-950/20 px-2 py-0.5 rounded border border-cyan-800/30">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="text-right text-xs text-gray-500 font-mono space-y-1">
                  <div>Datasets Linked: <span className="text-white font-bold">{suite.datasets_count}</span></div>
                  <div>Created: <span className="text-white">{new Date(suite.created_at).toLocaleDateString()}</span></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Benchmark Suite Modal */}
      {createOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="w-full max-w-md bg-[#111827] border border-[#2A3352] rounded-xl shadow-2xl overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-[#2A3352] flex justify-between items-center">
              <h3 className="font-heading font-bold text-white">New Benchmark Suite</h3>
              <button onClick={() => setCreateOpen(false)} className="text-muted hover:text-white">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleCreateSuite} className="p-6 space-y-4">
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Suite Name</label>
                <input
                  type="text"
                  required
                  value={suiteName}
                  onChange={(e) => setSuiteName(e.target.value)}
                  placeholder="e.g. Chatbot Compliance Suite"
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Summarize validation targets..."
                  rows={2}
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Tags (comma separated)</label>
                <input
                  type="text"
                  value={tagsString}
                  onChange={(e) => setTagsString(e.target.value)}
                  placeholder="e.g. safety, prod-bot"
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Select Datasets to Include</label>
                <div className="space-y-2 max-h-36 overflow-y-auto border border-[#2A3352] rounded-lg p-3 bg-[#050816]/40">
                  {datasets.map((ds) => (
                    <label key={ds.id} className="flex items-center gap-2.5 text-xs cursor-pointer text-gray-300 hover:text-white">
                      <input
                        type="checkbox"
                        checked={selectedDatasets.includes(ds.id)}
                        onChange={() => handleDatasetToggle(ds.id)}
                        className="rounded border-[#2A3352] text-primary focus:ring-primary bg-[#050816]"
                      />
                      <span>{ds.name}</span>
                    </label>
                  ))}
                </div>
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
                  Create Suite
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </motion.div>
  );
}

function X({ size }: { size?: number }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size || 24} height={size || 24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-x">
      <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
    </svg>
  );
}
