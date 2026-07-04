import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Database,
  Upload,
  Clock,
  History,
  Tag,
  CheckCircle,
  ChevronRight
} from 'lucide-react';
import { api } from '../services/api';
import type { Dataset, DatasetVersion, DatasetRecord, ImportReport } from '../services/api';

export default function Datasets() {
  const { projectId } = useParams<{ projectId: string }>();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [importReport, setImportReport] = useState<ImportReport | null>(null);

  // Form states
  const [datasetName, setDatasetName] = useState('');
  const [description, setDescription] = useState('');
  const [versionLabel, setVersionLabel] = useState('v1');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Detail views states
  const [activeTab, setActiveTab] = useState<'records' | 'versions' | 'details'>('records');
  const [versions, setVersions] = useState<DatasetVersion[]>([]);
  const [records, setRecords] = useState<DatasetRecord[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<string>('');

  const fetchDatasets = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const data = await api.datasets.list(projectId);
      setDatasets(data);
      if (data.length > 0 && !selectedDataset) {
        setSelectedDataset(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  useEffect(() => {
    const fetchDetails = async () => {
      if (!selectedDataset) return;
      try {
        const vers = await api.datasets.versions(selectedDataset.id);
        setVersions(vers);
        if (vers.length > 0) {
          const defaultVer = vers[vers.length - 1];
          setSelectedVersion(defaultVer.id);
          const recs = await api.datasets.records(defaultVer.id);
          setRecords(recs);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchDetails();
  }, [selectedDataset]);

  const handleVersionChange = async (verId: string) => {
    setSelectedVersion(verId);
    try {
      const recs = await api.datasets.records(verId);
      setRecords(recs);
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      setDatasetName(e.target.files[0].name.split('.')[0]);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !projectId) return;

    setUploadProgress(10);
    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev === null) return null;
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + 25;
      });
    }, 200);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('dataset_name', datasetName);
    formData.append('project_id', projectId);
    formData.append('description', description);
    formData.append('version_label', versionLabel);

    try {
      const result = await api.datasets.upload(formData);
      clearInterval(interval);
      setUploadProgress(100);
      setTimeout(() => {
        setUploadProgress(null);
        setImportReport(result);
        fetchDatasets();
      }, 500);
    } catch (err) {
      clearInterval(interval);
      setUploadProgress(null);
      alert('Upload failed');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {/* Title block */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="font-heading font-bold text-3xl text-white">Dataset Management</h1>
          <p className="text-gray-400 text-sm mt-1">Upload validation cases, import formats, check version controls.</p>
        </div>
        <button
          onClick={() => {
            setImportReport(null);
            setUploadOpen(true);
          }}
          className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white font-medium px-4 py-2.5 rounded-lg shadow-lg shadow-primary/20 transition-all text-sm"
        >
          <Upload size={16} /> Import Dataset
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Datasets List */}
        <div className="bg-[#111827] border border-[#2A3352] rounded-xl overflow-hidden h-fit">
          <div className="p-4 border-b border-[#2A3352] flex items-center gap-2 bg-[#050816]/30">
            <Database size={16} className="text-indigo-400" />
            <span className="font-semibold text-sm">Dataset Repositories</span>
          </div>
          {loading ? (
            <div className="p-6 text-center text-sm text-gray-500">Loading datasets...</div>
          ) : datasets.length === 0 ? (
            <div className="p-12 text-center text-sm text-gray-500">No datasets found. Import one to start.</div>
          ) : (
            <div className="divide-y divide-[#2A3352]">
              {datasets.map((dataset) => (
                <button
                  key={dataset.id}
                  onClick={() => setSelectedDataset(dataset)}
                  className={`w-full text-left p-4 hover:bg-[#1f2937]/35 transition-colors flex justify-between items-center ${selectedDataset?.id === dataset.id ? 'bg-[#1f2937]/50 border-l-2 border-primary' : ''}`}
                >
                  <div className="space-y-1">
                    <span className="text-sm font-semibold text-white block">{dataset.name}</span>
                    <span className="text-xs text-gray-400 block line-clamp-1">{dataset.description}</span>
                  </div>
                  <ChevronRight size={16} className="text-gray-600" />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right Columns: Selected Dataset details & records */}
        <div className="lg:col-span-2 space-y-6">
          {selectedDataset ? (
            <div className="bg-[#111827] border border-[#2A3352] rounded-xl overflow-hidden">
              {/* Header inside details */}
              <div className="p-6 border-b border-[#2A3352] flex justify-between items-start">
                <div>
                  <h2 className="text-xl font-bold font-heading">{selectedDataset.name}</h2>
                  <p className="text-sm text-gray-400 mt-1">{selectedDataset.description}</p>
                  <div className="flex gap-2.5 mt-3">
                    {selectedDataset.tags.map((tag: string) => (
                      <span key={tag} className="flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider text-cyan-400 bg-cyan-950/30 px-2 py-0.5 rounded border border-cyan-800/30">
                        <Tag size={8} /> {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="text-right text-xs text-gray-500 space-y-1 font-mono">
                  <div>Source: <span className="text-white">{selectedDataset.source}</span></div>
                  <div>Format: <span className="text-white">{selectedDataset.language}</span></div>
                  <div>Owner: <span className="text-white">{selectedDataset.owner}</span></div>
                </div>
              </div>

              {/* Tabs list */}
              <div className="flex border-b border-[#2A3352] bg-[#050816]/30 px-4">
                {[
                  { id: 'records', label: 'Test Cases & Records' },
                  { id: 'versions', label: 'Version History' },
                  { id: 'details', label: 'Metadata Schema' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as 'records' | 'versions' | 'details')}
                    className={`px-4 py-3 text-sm font-semibold border-b-2 transition-colors ${activeTab === tab.id ? 'border-primary text-white' : 'border-transparent text-gray-400 hover:text-white'}`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab Content body */}
              <div className="p-6">
                {activeTab === 'records' && (
                  <div className="space-y-4">
                    {/* Version Selector */}
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <Clock size={14} className="text-gray-500" />
                        <span className="text-gray-400">Viewing version:</span>
                        <select
                          value={selectedVersion}
                          onChange={(e) => handleVersionChange(e.target.value)}
                          className="bg-[#050816] text-white border border-[#2A3352] rounded px-2.5 py-1 text-xs focus:outline-none focus:border-primary cursor-pointer font-semibold"
                        >
                          {versions.map((v) => (
                            <option key={v.id} value={v.id}>{v.label} ({v.records_count} records)</option>
                          ))}
                        </select>
                      </div>
                      <span className="text-xs text-gray-500 font-mono">Total size: {records.length} records</span>
                    </div>

                    {/* Records Table */}
                    <div className="border border-[#2A3352] rounded-lg overflow-hidden">
                      <table className="w-full text-left text-sm">
                        <thead className="bg-[#050816]/50 text-gray-400 border-b border-[#2A3352]">
                          <tr>
                            <th className="p-3 font-semibold text-xs uppercase tracking-wider">Input Prompt</th>
                            <th className="p-3 font-semibold text-xs uppercase tracking-wider">Expected Response</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#2A3352]">
                          {records.length === 0 ? (
                            <tr>
                              <td colSpan={2} className="p-6 text-center text-gray-500">No records found in this version.</td>
                            </tr>
                          ) : (
                            records.map((rec) => (
                              <tr key={rec.id} className="hover:bg-[#1f2937]/20">
                                <td className="p-3 align-top font-mono text-xs max-w-xs truncate text-gray-300">{rec.input_prompt}</td>
                                <td className="p-3 align-top text-gray-400 max-w-xs truncate font-mono text-xs">{rec.reference}</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {activeTab === 'versions' && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-4">
                      <History size={16} className="text-primary" />
                      <h4 className="font-semibold text-sm">Version Commit Logs</h4>
                    </div>
                    <div className="relative border-l-2 border-[#2A3352] ml-3 pl-5 space-y-6">
                      {versions.map((ver) => (
                        <div key={ver.id} className="relative">
                          {/* Bullet point indicator */}
                          <div className={`absolute -left-7 top-1 w-3.5 h-3.5 rounded-full border-2 border-[#111827] ${ver.label === selectedDataset.current_version ? 'bg-accent' : 'bg-[#2A3352]'}`} />
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-bold text-white font-mono bg-[#050816] px-1.5 py-0.5 rounded border border-[#2A3352]">{ver.label}</span>
                              {ver.label === selectedDataset.current_version && (
                                <span className="text-[10px] font-bold text-emerald-400 bg-emerald-950/20 px-2 py-0.5 rounded border border-emerald-900/30">Active Production</span>
                              )}
                              <span className="text-xs text-gray-500">{new Date(ver.created_at).toLocaleDateString()}</span>
                            </div>
                            <p className="text-xs text-gray-400">{ver.description}</p>
                            <span className="text-[10px] text-gray-500 font-mono block">Count: {ver.records_count} records</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'details' && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <h4 className="font-semibold text-sm text-gray-300">File metadata specifications</h4>
                      <div className="bg-[#050816] p-4 rounded-lg border border-[#2A3352] font-mono text-xs text-gray-400 space-y-2">
                        <div>Visibility: <span className="text-white">{selectedDataset.visibility}</span></div>
                        <div>Language Code: <span className="text-white">{selectedDataset.language}</span></div>
                        <div>License Standard: <span className="text-white">{selectedDataset.license}</span></div>
                        <div>Dataset Repository ID: <span className="text-white">{selectedDataset.id}</span></div>
                      </div>
                    </div>
                    <div className="space-y-2 text-xs text-gray-400">
                      <h4 className="font-semibold text-sm text-gray-300">Schema Validation Policy</h4>
                      <p>Every imported record must contain the following minimum fields:</p>
                      <ul className="list-disc pl-4 space-y-1 font-mono">
                        <li><b className="text-white">input_prompt</b> (string, required)</li>
                        <li><b className="text-white">reference</b> (string, optional)</li>
                        <li><b className="text-white">expected_score</b> (float, optional)</li>
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="p-12 bg-[#111827] border border-[#2A3352] rounded-xl text-center text-gray-500">
              Select or import a dataset repository to view details.
            </div>
          )}
        </div>
      </div>

      {/* Import Dataset Dialog Modal */}
      {uploadOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="w-full max-w-md bg-[#111827] border border-[#2A3352] rounded-xl shadow-2xl overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-[#2A3352] flex justify-between items-center">
              <h3 className="font-heading font-bold text-white">Import Dataset</h3>
              <button onClick={() => setUploadOpen(false)} className="text-muted hover:text-white">
                <X size={18} />
              </button>
            </div>
            
            {uploadProgress !== null ? (
              <div className="p-8 space-y-4 text-center">
                <Upload size={32} className="mx-auto text-primary animate-bounce" />
                <h4 className="text-sm font-semibold">Uploading & parsing file content...</h4>
                <div className="w-full bg-[#050816] rounded-full h-2 overflow-hidden border border-[#2A3352]">
                  <div className="bg-primary h-full transition-all duration-300" style={{ width: `${uploadProgress}%` }} />
                </div>
                <span className="text-xs text-gray-500 font-mono">{uploadProgress}%</span>
              </div>
            ) : importReport ? (
              <div className="p-6 space-y-4">
                <div className="flex items-center gap-3 text-emerald-400 bg-emerald-950/20 border border-emerald-900/30 p-4 rounded-lg">
                  <CheckCircle size={20} className="shrink-0" />
                  <div>
                    <h4 className="font-semibold text-sm">Parse Successful</h4>
                    <p className="text-xs text-gray-400">File format validated, records imported successfully.</p>
                  </div>
                </div>
                <div className="bg-[#050816] p-4 rounded-lg border border-[#2A3352] font-mono text-xs text-gray-400 space-y-1.5">
                  <div>Job ID: <span className="text-white">{importReport.job_id}</span></div>
                  <div>Status: <span className="text-white">{importReport.status}</span></div>
                  <div>Records Loaded: <span className="text-white">{importReport.records_imported}</span></div>
                </div>
                <button
                  onClick={() => setUploadOpen(false)}
                  className="w-full bg-primary hover:bg-primary/90 text-white font-medium py-2 rounded-lg text-sm transition"
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleUploadSubmit} className="p-6 space-y-4">
                <div>
                  <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Select File (CSV, JSON, JSONL)</label>
                  <div className="border-2 border-dashed border-[#2A3352] hover:border-gray-500 rounded-lg p-6 text-center cursor-pointer transition relative">
                    <input
                      type="file"
                      required
                      accept=".csv,.json,.jsonl"
                      onChange={handleFileChange}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <Upload className="mx-auto text-gray-500 mb-2" size={24} />
                    <span className="text-xs text-gray-400 block">{selectedFile ? selectedFile.name : 'Drag & drop or click to choose file'}</span>
                  </div>
                </div>
                <div>
                  <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Dataset Name</label>
                  <input
                    type="text"
                    required
                    value={datasetName}
                    onChange={(e) => setDatasetName(e.target.value)}
                    placeholder="Customer Inquiries safety set"
                    className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Version Label</label>
                    <input
                      type="text"
                      required
                      value={versionLabel}
                      onChange={(e) => setVersionLabel(e.target.value)}
                      placeholder="e.g. v1"
                      className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary font-mono"
                    />
                  </div>
                  <div>
                    <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Format Type</label>
                    <select className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary cursor-pointer">
                      <option value="csv">CSV File</option>
                      <option value="json">JSON Records</option>
                      <option value="jsonl">JSON Lines</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">Description</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe content and source target fields..."
                    rows={2}
                    className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                </div>
                <div className="flex justify-end gap-3 pt-4 border-t border-[#2A3352]/40">
                  <button
                    type="button"
                    onClick={() => setUploadOpen(false)}
                    className="px-4 py-2 border border-[#2A3352] text-gray-400 hover:text-white rounded-lg text-sm transition"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-sm font-semibold transition"
                  >
                    Process Import
                  </button>
                </div>
              </form>
            )}
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
