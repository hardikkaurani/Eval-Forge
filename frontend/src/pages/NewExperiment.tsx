import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Terminal,
  ArrowLeft,
  Play,
  Database,
  Cpu,
  Sparkles,
} from 'lucide-react';
import { useWorkspace } from '../context/WorkspaceContext';
import { api } from '../services/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';

export default function NewExperiment() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const { currentProjectId } = useWorkspace();

  const activeProjectId = projectId || currentProjectId || '1';

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [datasetVersionId, setDatasetVersionId] = useState('v1.0.0');
  const [judge, setJudge] = useState('gpt-4-turbo');
  const [provider, setProvider] = useState('OpenAI');
  const [temperature, setTemperature] = useState('0.2');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSubmitting(true);

    try {
      await api.experiments.create(
        {
          name,
          description,
          dataset_version_id: datasetVersionId,
          judge,
          provider,
          model: 'gpt-3.5-turbo',
          configuration: { temperature: parseFloat(temperature) },
        },
        activeProjectId
      );
      navigate(`/projects/${activeProjectId}/evaluations`);
    } catch (err) {
      console.error('Failed to create experiment:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-workbench-border pb-4">
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            icon={ArrowLeft}
            onClick={() => navigate(`/projects/${activeProjectId}/evaluations`)}
          >
            Back
          </Button>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-workbench-text flex items-center gap-2">
              <Terminal className="w-5 h-5 text-brand-terracotta" />
              Configure New Evaluation Experiment
            </h1>
            <p className="text-xs text-workbench-muted">
              Configure judge model parameters, provider routes, and target test datasets.
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Step 1: Basic Info */}
        <Card title="1. Experiment Metadata" subtitle="Identify the evaluation run">
          <div className="space-y-4">
            <Input
              label="Experiment Name"
              placeholder="e.g. GPT-4 vs Claude-3 Hallucination Benchmark"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-workbench-text">Description</label>
              <textarea
                rows={2}
                placeholder="Optional notes regarding hypothesis, model checkpoint, or prompt changes..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full text-xs rounded-md border border-workbench-border bg-white p-3 text-workbench-text focus:outline-none focus:border-brand-sky"
              />
            </div>
          </div>
        </Card>

        {/* Step 2: Dataset & Provider */}
        <Card title="2. Evaluation Scope & Models" subtitle="Select test dataset and candidate provider">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-workbench-text flex items-center gap-1.5">
                <Database className="w-3.5 h-3.5 text-brand-terracotta" /> Test Dataset Version
              </label>
              <select
                value={datasetVersionId}
                onChange={(e) => setDatasetVersionId(e.target.value)}
                className="w-full text-xs rounded-md border border-workbench-border bg-white p-2.5 text-workbench-text focus:outline-none focus:border-brand-sky"
              >
                <option value="v1.0.0">v1.0.0 — Chatbot Golden Alignment (50 cases)</option>
                <option value="v1.1.0">v1.1.0 — Safety & Toxicity Edge Cases (120 cases)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-workbench-text flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-brand-terracotta" /> Inference Provider
              </label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full text-xs rounded-md border border-workbench-border bg-white p-2.5 text-workbench-text focus:outline-none focus:border-brand-sky"
              >
                <option value="OpenAI">OpenAI (API Key Route)</option>
                <option value="Anthropic">Anthropic (Claude 3.5 Sonnet)</option>
                <option value="Ollama">Ollama (Local Llama-3 8B)</option>
                <option value="vLLM">vLLM (Self-hosted Cluster)</option>
              </select>
            </div>
          </div>
        </Card>

        {/* Step 3: Judge & Hyperparameters */}
        <Card title="3. LLM Judge Configuration" subtitle="Configure automated evaluator logic">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-xs font-medium text-workbench-text flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-brand-terracotta" /> Judge Evaluator Model
              </label>
              <select
                value={judge}
                onChange={(e) => setJudge(e.target.value)}
                className="w-full text-xs rounded-md border border-workbench-border bg-white p-2.5 text-workbench-text focus:outline-none focus:border-brand-sky"
              >
                <option value="gpt-4-turbo">GPT-4 Turbo (High Precision Judge)</option>
                <option value="claude-3-5-sonnet">Claude 3.5 Sonnet (Reasoning Judge)</option>
                <option value="llama-3-70b">Llama 3 70B (Open Weights Judge)</option>
              </select>
            </div>

            <Input
              label="Temperature (0.0 to 1.0)"
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
            />
          </div>
        </Card>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t border-workbench-border">
          <Button
            variant="outline"
            size="md"
            onClick={() => navigate(`/projects/${activeProjectId}/evaluations`)}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            size="md"
            icon={Play}
            isLoading={isSubmitting}
          >
            Execute Evaluation Pipeline
          </Button>
        </div>
      </form>
    </div>
  );
}
