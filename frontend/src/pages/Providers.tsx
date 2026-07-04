import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  RefreshCw,
  Settings2,
  Key,
  ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';
import type { Provider } from '../services/api';

export default function Providers() {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null);
  const [apiKey, setApiKey] = useState('');
  const [modelType, setModelType] = useState('gpt-4o');

  const fetchProviders = async () => {
    setLoading(true);
    try {
      const data = await api.providers.list();
      setProviders(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProviders();
  }, []);

  const handleSaveConfig = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProvider) return;

    // Simulate saving API Key config
    setProviders((prev) =>
      prev.map((p) => {
        if (p.id === editingProvider.id) {
          return {
            ...p,
            status: 'healthy',
            latency: Math.max(100, p.latency - 80), // simulate optimization
          };
        }
        return p;
      })
    );

    setEditingProvider(null);
    setApiKey('');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {/* Title */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-heading font-bold text-3xl text-white">Judge Providers</h1>
          <p className="text-gray-400 text-sm mt-1">Configure external API keys, check model health parameters, examine rates.</p>
        </div>
        <button
          onClick={fetchProviders}
          className="flex items-center gap-2 bg-[#111827] border border-[#2A3352] text-white hover:text-primary hover:border-primary font-medium px-4 py-2.5 rounded-lg transition-all text-sm"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Sync status
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Providers List */}
        <div className="space-y-4">
          {loading ? (
            <div className="p-8 text-center text-gray-500 text-sm bg-[#111827] border border-[#2A3352] rounded-xl">Loading Judge Providers...</div>
          ) : (
            providers.map((prov) => (
              <div
                key={prov.id}
                className="bg-[#111827] border border-[#2A3352] rounded-xl p-5 hover:border-gray-500 transition-colors flex flex-col justify-between"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-heading font-bold text-lg text-white flex items-center gap-2">
                      {prov.name}
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded border font-mono ${
                        prov.status === 'healthy' ? 'text-emerald-400 bg-emerald-950/20 border-emerald-900/30' :
                        prov.status === 'degraded' ? 'text-yellow-400 bg-yellow-950/20 border-yellow-900/30' :
                        'text-red-400 bg-red-950/20 border-red-900/30'
                      }`}>
                        {prov.status.toUpperCase()}
                      </span>
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">Version: {prov.version}</p>
                  </div>
                  <button
                    onClick={() => {
                      setEditingProvider(prov);
                      setApiKey('••••••••••••••••••••');
                    }}
                    className="p-2 text-gray-400 hover:text-white hover:bg-[#1f2937] rounded-lg border border-[#2A3352] transition"
                  >
                    <Settings2 size={16} />
                  </button>
                </div>

                {/* Status metrics grid */}
                <div className="grid grid-cols-3 gap-3 mt-5 pt-4 border-t border-[#2A3352]/40 text-center font-mono">
                  <div className="bg-[#050816]/30 border border-[#2A3352] p-2 rounded">
                    <span className="text-[9px] uppercase text-gray-500 block">Avg Latency</span>
                    <span className="text-xs font-bold text-white block mt-0.5">{prov.latency}ms</span>
                  </div>
                  <div className="bg-[#050816]/30 border border-[#2A3352] p-2 rounded">
                    <span className="text-[9px] uppercase text-gray-500 block">Error Rate</span>
                    <span className="text-xs font-bold text-red-400 block mt-0.5">{(prov.error_rate * 100).toFixed(0)}%</span>
                  </div>
                  <div className="bg-[#050816]/30 border border-[#2A3352] p-2 rounded">
                    <span className="text-[9px] uppercase text-gray-500 block">Models Loaded</span>
                    <span className="text-xs font-bold text-cyan-400 block mt-0.5">{prov.active_models.length}</span>
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-1.5">
                  {prov.active_models.map((mod: string) => (
                    <span key={mod} className="text-[9px] font-mono text-gray-400 bg-[#050816] px-2 py-0.5 rounded border border-[#2A3352]">
                      {mod}
                    </span>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Configurations Form */}
        <div className="bg-[#111827] border border-[#2A3352] rounded-xl p-6 h-fit">
          <div className="flex items-center gap-2 mb-4 border-b border-[#2A3352] pb-3">
            <Key className="text-primary" size={18} />
            <h3 className="font-heading font-bold text-lg text-white">Credentials & Keys</h3>
          </div>
          {editingProvider ? (
            <form onSubmit={handleSaveConfig} className="space-y-4">
              <h4 className="text-sm font-semibold text-white">Configure: {editingProvider.name}</h4>
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">API Access Secret Key</label>
                <input
                  type="password"
                  required
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter sk-..."
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary font-mono"
                />
              </div>
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Default Judicial Model</label>
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary cursor-pointer"
                >
                  {editingProvider.active_models.map((mod: string) => (
                    <option key={mod} value={mod}>{mod}</option>
                  ))}
                </select>
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  className="flex-1 bg-primary hover:bg-primary/90 text-white font-medium py-2 rounded-lg text-sm transition"
                >
                  Save Configuration
                </button>
                <button
                  type="button"
                  onClick={() => setEditingProvider(null)}
                  className="px-4 py-2 border border-[#2A3352] text-gray-400 hover:text-white rounded-lg text-sm transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="text-center py-12 text-gray-500 text-sm space-y-3">
              <ShieldCheck className="mx-auto w-12 h-12 text-gray-600" />
              <p>Select a provider edit button to configure API access credentials.</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
