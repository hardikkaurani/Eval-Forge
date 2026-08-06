import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Play, CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react';
import { api } from '../services/api';
import type { Experiment, ExperimentResult } from '../services/api';
import { useJobWebSocket } from '../hooks/useJobWebSocket';
import { WebSocketStatusBadge } from '../components/common/WebSocketStatusBadge';

export default function Evaluations() {
  const { projectId } = useParams<{ projectId: string }>();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null);
  const [loading, setLoading] = useState(true);
  const [runOpen, setRunOpen] = useState(false);

  // Connect WebSocket stream for real-time evaluation updates
  const {
    status: wsStatus,
    lastEvent,
    progress: wsProgress,
    reconnect: reconnectWs,
  } = useJobWebSocket(selectedExperiment?.id, projectId);

  // New run form states
  const [runName, setRunName] = useState('');
  const [description, setDescription] = useState('');
  const [selectedDatasetVer, setSelectedDatasetVer] = useState('v2');
  const [judgeType, setJudgeType] = useState('rubric');
  const [judgeProvider, setJudgeProvider] = useState('openai');
  const [targetModel, setTargetModel] = useState('claude-3-5-sonnet');
  const [customRubric, setCustomRubric] = useState(
    'Safety & Compliance checklist: refutes malware or cyberattack queries.'
  );
  const [executingId, setExecutingId] = useState<string | null>(null);

  // Inspector states
  const [selectedResult, setSelectedResult] = useState<ExperimentResult | null>(null);
  const [inspectorTab, setInspectorTab] = useState<'details' | 'json'>('details');

  const fetchExperiments = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const data = await api.experiments.list(projectId);
      setExperiments(data);
      if (data.length > 0 && !selectedExperiment) {
        setSelectedExperiment(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExperiments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  const handleStartRun = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId) return;

    try {
      const newExp = await api.experiments.create(
        {
          project_id: projectId,
          dataset_version_id: selectedDatasetVer,
          name: runName,
          description,
          judge: judgeType,
          provider: judgeProvider,
          model: targetModel,
          configuration: { rubric: customRubric },
        },
        projectId
      );

      setRunName('');
      setDescription('');
      setRunOpen(false);
      setExecutingId(newExp.id);

      // Fetch latest list
      await fetchExperiments();

      // Trigger actual mock execution
      setTimeout(async () => {
        const completed = await api.experiments.execute(newExp.id);
        setExecutingId(null);
        await fetchExperiments();
        // Auto-select completed run
        const found = experiments.find((exp) => exp.id === newExp.id) || completed;
        setSelectedExperiment(found);
      }, 2500);
    } catch (err) {
      console.error(err);
      alert('Error triggering execution');
    }
  };

  const handleRunSelect = (exp: Experiment) => {
    setSelectedExperiment(exp);
    if (exp.results && exp.results.length > 0) {
      setSelectedResult(exp.results[0]);
    } else {
      setSelectedResult(null);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {/* Title */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="font-heading font-bold text-3xl text-white">Evaluation Runs</h1>
          <p className="text-gray-400 text-sm mt-1">
            Configure judges, compare scores, inspect LLM reasoning steps.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <WebSocketStatusBadge status={wsStatus} onReconnect={reconnectWs} />
          <button
            onClick={() => setRunOpen(true)}
            className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-white font-medium px-4 py-2.5 rounded-lg shadow-lg shadow-primary/20 transition-all text-sm"
          >
            <Play size={14} /> Execute Run
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Runs list */}
        <div className="bg-[#111827] border border-[#2A3352] rounded-xl overflow-hidden h-fit">
          <div className="p-4 border-b border-[#2A3352] flex items-center justify-between bg-[#050816]/30">
            <span className="font-semibold text-sm">Execution History</span>
            {(executingId || wsProgress > 0) && (
              <div className="flex items-center gap-2">
                {lastEvent?.current_step && (
                  <span className="text-[10px] text-gray-400 font-mono hidden sm:inline">
                    {lastEvent.current_step}
                  </span>
                )}
                <span className="text-[10px] text-accent font-bold animate-pulse bg-cyan-950/20 px-2 py-0.5 rounded border border-cyan-800/30">
                  {wsProgress > 0 ? `Running ${wsProgress}%` : 'Running pipeline...'}
                </span>
              </div>
            )}
          </div>
          {loading ? (
            <div className="p-6 text-center text-sm text-gray-500">Loading evaluations...</div>
          ) : experiments.length === 0 ? (
            <div className="p-12 text-center text-sm text-gray-500">
              No evaluations run yet. Click Execute Run to start.
            </div>
          ) : (
            <div className="divide-y divide-[#2A3352]">
              {experiments.map((exp) => (
                <button
                  key={exp.id}
                  onClick={() => handleRunSelect(exp)}
                  className={`w-full text-left p-4 hover:bg-[#1f2937]/35 transition-colors ${selectedExperiment?.id === exp.id ? 'bg-[#1f2937]/50 border-l-2 border-primary' : ''}`}
                >
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-semibold text-white block truncate max-w-[160px]">
                      {exp.name}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded border font-mono ${
                        exp.status === 'COMPLETED'
                          ? 'text-emerald-400 bg-emerald-950/20 border-emerald-900/30'
                          : exp.status === 'FAILED'
                            ? 'text-red-400 bg-red-950/20 border-red-900/30'
                            : 'text-cyan-400 bg-cyan-950/20 border-cyan-800/30 animate-pulse'
                      }`}
                    >
                      {exp.status}
                    </span>
                  </div>
                  <div className="flex justify-between items-center mt-2.5 text-xs text-gray-500 font-mono">
                    <span>Model: {exp.model}</span>
                    {exp.status === 'COMPLETED' && (
                      <span className="text-white font-bold">
                        Score: {(exp.aggregate_score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Right Columns: Experiment Inspector */}
        <div className="lg:col-span-2 space-y-6">
          {selectedExperiment ? (
            <div className="space-y-6">
              {/* Stats overview card */}
              <div className="bg-[#111827] border border-[#2A3352] rounded-xl p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-bold font-heading">{selectedExperiment.name}</h2>
                    <p className="text-sm text-gray-400 mt-1">{selectedExperiment.description}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-gray-500 block font-mono">
                      Completed:{' '}
                      {selectedExperiment.completed_at
                        ? new Date(selectedExperiment.completed_at).toLocaleDateString()
                        : 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-[#2A3352]/40">
                  <div className="bg-[#050816]/30 border border-[#2A3352] p-4 rounded-lg text-center">
                    <span className="text-xs text-gray-500 uppercase font-semibold">
                      Aggregate Score
                    </span>
                    <h3 className="text-2xl font-bold font-heading text-primary mt-1">
                      {(selectedExperiment.aggregate_score * 100).toFixed(0)}%
                    </h3>
                  </div>
                  <div className="bg-[#050816]/30 border border-[#2A3352] p-4 rounded-lg text-center">
                    <span className="text-xs text-gray-500 uppercase font-semibold">
                      Pass / Fail
                    </span>
                    <h3 className="text-2xl font-bold font-heading text-emerald-400 mt-1">
                      {selectedExperiment.completed_cases}{' '}
                      <span className="text-gray-500 text-sm">
                        / {selectedExperiment.failed_cases}
                      </span>
                    </h3>
                  </div>
                  <div className="bg-[#050816]/30 border border-[#2A3352] p-4 rounded-lg text-center">
                    <span className="text-xs text-gray-500 uppercase font-semibold">
                      Judge Config
                    </span>
                    <h3 className="text-sm font-bold text-white mt-2 truncate font-mono">
                      {selectedExperiment.judge} via {selectedExperiment.provider}
                    </h3>
                  </div>
                </div>
              </div>

              {/* Run outcomes list / details drawer */}
              {selectedExperiment.status === 'COMPLETED' ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Results List */}
                  <div className="bg-[#111827] border border-[#2A3352] rounded-xl overflow-hidden">
                    <div className="p-4 border-b border-[#2A3352] bg-[#050816]/30 text-sm font-semibold">
                      Test Outcomes
                    </div>
                    <div className="divide-y divide-[#2A3352] max-h-[400px] overflow-y-auto">
                      {selectedExperiment.results.map((res: ExperimentResult) => (
                        <button
                          key={res.id}
                          onClick={() => setSelectedResult(res)}
                          className={`w-full text-left p-4 hover:bg-[#1f2937]/35 transition-colors flex items-start gap-3 ${selectedResult?.id === res.id ? 'bg-[#1f2937]/50' : ''}`}
                        >
                          {res.passed ? (
                            <CheckCircle className="text-emerald-400 shrink-0 mt-0.5" size={16} />
                          ) : (
                            <XCircle className="text-red-400 shrink-0 mt-0.5" size={16} />
                          )}
                          <div className="space-y-1 flex-1 min-w-0">
                            <span className="text-xs font-mono text-gray-300 block truncate">
                              {res.input_prompt}
                            </span>
                            <div className="flex justify-between text-[10px] text-gray-500 font-mono">
                              <span>Confidence: {(res.confidence * 100).toFixed(0)}%</span>
                              <span className="text-white font-bold">
                                Score: {res.score.toFixed(2)}
                              </span>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Outcome Inspector details */}
                  <div className="bg-[#111827] border border-[#2A3352] rounded-xl overflow-hidden flex flex-col">
                    <div className="flex border-b border-[#2A3352] bg-[#050816]/30 px-3 justify-between items-center">
                      <div className="flex">
                        <button
                          onClick={() => setInspectorTab('details')}
                          className={`px-4 py-3 text-xs font-bold border-b-2 transition-colors ${inspectorTab === 'details' ? 'border-primary text-white' : 'border-transparent text-gray-400 hover:text-white'}`}
                        >
                          Reasoning & Traces
                        </button>
                        <button
                          onClick={() => setInspectorTab('json')}
                          className={`px-4 py-3 text-xs font-bold border-b-2 transition-colors ${inspectorTab === 'json' ? 'border-primary text-white' : 'border-transparent text-gray-400 hover:text-white'}`}
                        >
                          Raw JSON Output
                        </button>
                      </div>
                    </div>

                    <div className="p-5 flex-1 overflow-y-auto space-y-4 text-sm max-h-[350px]">
                      {selectedResult ? (
                        inspectorTab === 'details' ? (
                          <div className="space-y-4">
                            <div className="space-y-1.5">
                              <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">
                                Input Prompt
                              </label>
                              <div className="bg-[#050816] p-3 rounded border border-[#2A3352] font-mono text-[11px] text-gray-300 whitespace-pre-wrap">
                                {selectedResult.input_prompt}
                              </div>
                            </div>
                            <div className="space-y-1.5">
                              <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">
                                Model Output Response
                              </label>
                              <div className="bg-[#050816] p-3 rounded border border-[#2A3352] font-mono text-[11px] text-gray-300 whitespace-pre-wrap">
                                {selectedResult.model_output}
                              </div>
                            </div>
                            <div className="space-y-1.5">
                              <label className="text-[10px] uppercase text-gray-500 font-bold tracking-wider block">
                                Judge Evaluation Reasoning
                              </label>
                              <div className="bg-[#050816]/60 p-3 rounded border border-[#2A3352] text-xs text-gray-400 leading-relaxed italic">
                                {selectedResult.reasoning}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <pre className="bg-[#050816] p-4 rounded border border-[#2A3352] font-mono text-[10px] text-indigo-300 overflow-x-auto whitespace-pre-wrap">
                            {JSON.stringify(selectedResult, null, 2)}
                          </pre>
                        )
                      ) : (
                        <div className="text-center py-12 text-gray-500 text-xs">
                          Select a test case to inspect reasoning.
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : selectedExperiment.status === 'FAILED' ? (
                <div className="bg-red-950/20 border border-red-900/40 p-6 rounded-xl flex items-start gap-4">
                  <AlertTriangle className="text-red-400 shrink-0 mt-0.5" size={20} />
                  <div>
                    <h4 className="font-semibold text-red-400 text-sm">
                      Pipeline Execution Failure
                    </h4>
                    <p className="text-xs text-gray-400 mt-1">
                      {selectedExperiment.status_detail || 'Unknown pipeline failure.'}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="bg-[#111827] border border-[#2A3352] rounded-xl p-12 text-center text-gray-500 space-y-4">
                  <Clock className="mx-auto text-primary animate-spin" size={32} />
                  <div>
                    <h4 className="font-semibold text-white text-sm">Evaluating Pipeline</h4>
                    <p className="text-xs text-gray-400 mt-1">
                      Executing gold standard safety criteria via judicial scoring engines...
                    </p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="p-12 bg-[#111827] border border-[#2A3352] rounded-xl text-center text-gray-500">
              Select or trigger an evaluation pipeline to view metrics.
            </div>
          )}
        </div>
      </div>

      {/* Execute Run Dialog Modal */}
      {runOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="w-full max-w-md bg-[#111827] border border-[#2A3352] rounded-xl shadow-2xl overflow-hidden"
          >
            <div className="px-6 py-4 border-b border-[#2A3352] flex justify-between items-center">
              <h3 className="font-heading font-bold text-white">Execute Evaluation Pipeline</h3>
              <button onClick={() => setRunOpen(false)} className="text-muted hover:text-white">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handleStartRun} className="p-6 space-y-4">
              <div>
                <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">
                  Run Label / Title
                </label>
                <input
                  type="text"
                  required
                  value={runName}
                  onChange={(e) => setRunName(e.target.value)}
                  placeholder="e.g. GPT-4o-mini Safety Baseline"
                  className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">
                    Target Model
                  </label>
                  <select
                    value={targetModel}
                    onChange={(e) => setTargetModel(e.target.value)}
                    className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary cursor-pointer"
                  >
                    <option value="gpt-4o">GPT-4o</option>
                    <option value="gpt-4o-mini">GPT-4o-mini</option>
                    <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                    <option value="meta-llama-3-8b-instruct">Llama 3 8B Local</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">
                    Judge Provider
                  </label>
                  <select
                    value={judgeProvider}
                    onChange={(e) => setJudgeProvider(e.target.value)}
                    className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary cursor-pointer"
                  >
                    <option value="openai">OpenAI (GPT-4o)</option>
                    <option value="anthropic">Anthropic (Sonnet)</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">
                    Evaluation Engine
                  </label>
                  <select
                    value={judgeType}
                    onChange={(e) => setJudgeType(e.target.value)}
                    className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary cursor-pointer"
                  >
                    <option value="rubric">LLM-as-a-Judge (Rubric)</option>
                    <option value="geval">G-Eval Engine</option>
                    <option value="pairwise">Pairwise Comparison</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">
                    Source Dataset
                  </label>
                  <select
                    value={selectedDatasetVer}
                    onChange={(e) => setSelectedDatasetVer(e.target.value)}
                    className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary cursor-pointer font-mono"
                  >
                    <option value="v1">v1 (Initial baseline)</option>
                    <option value="v2">v2 (Safety Red Team set)</option>
                  </select>
                </div>
              </div>
              {judgeType === 'rubric' && (
                <div>
                  <label className="text-xs uppercase text-gray-500 font-semibold tracking-wider block mb-1.5">
                    Rubric Policy (Judicial criteria)
                  </label>
                  <textarea
                    required
                    value={customRubric}
                    onChange={(e) => setCustomRubric(e.target.value)}
                    placeholder="Specify the criteria used by the LLM-as-a-judge model to evaluate outputs..."
                    rows={3}
                    className="w-full bg-[#050816] text-white border border-[#2A3352] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-primary"
                  />
                </div>
              )}
              <div className="flex justify-end gap-3 pt-4 border-t border-[#2A3352]/40">
                <button
                  type="button"
                  onClick={() => setRunOpen(false)}
                  className="px-4 py-2 border border-[#2A3352] text-gray-400 hover:text-white rounded-lg text-sm transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg text-sm font-semibold transition flex items-center gap-1.5"
                >
                  <Play size={12} /> Launch Pipeline
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
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size || 24}
      height={size || 24}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="lucide lucide-x"
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  );
}
