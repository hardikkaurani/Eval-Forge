import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const ENABLE_MOCKS = import.meta.env.VITE_ENABLE_MOCKS === 'true';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    config.headers['X-API-Key'] = token;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || '60';
      const customMessage =
        error.response.data?.message ||
        error.response.data?.data?.error ||
        `Rate limit exceeded. Please retry after ${retryAfter} seconds.`;
      console.warn(`[RateLimit 429] ${customMessage} (Retry-After: ${retryAfter}s)`);
      error.message = customMessage;
    }
    return Promise.reject(error);
  }
);

// Shared domain types
export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
  datasets_count: number;
  benchmarks_count: number;
  evaluations_count: number;
}

export interface Dataset {
  id: string;
  project_id: string;
  name: string;
  description: string;
  visibility: string;
  owner: string;
  source: string;
  language: string;
  license: string;
  tags: string[];
  created_at: string;
  versions_count: number;
  current_version: string;
}

export interface DatasetVersion {
  id: string;
  label: string;
  description: string;
  created_at: string;
  records_count: number;
}

export interface DatasetRecord {
  id: string;
  input_prompt: string;
  candidate_output?: string;
  reference?: string;
  model_output?: string;
  score?: number;
  passed?: boolean;
  confidence?: number;
  reasoning?: string;
  judge?: string;
  provider?: string;
}

export interface Benchmark {
  id: string;
  project_id: string;
  name: string;
  description: string;
  tags: string[];
  dataset_ids: string[];
  created_at: string;
  datasets_count: number;
}

export interface ExperimentResult {
  id: string;
  input_prompt: string;
  model_output: string;
  reference: string;
  score: number;
  passed: boolean;
  confidence: number;
  reasoning: string;
  judge: string;
  provider: string;
}

export interface Experiment {
  id: string;
  project_id: string;
  dataset_version_id: string;
  name: string;
  description: string;
  status: string;
  judge: string;
  provider: string;
  model: string;
  configuration: Record<string, unknown>;
  created_at: string;
  completed_at: string | null;
  completed_cases: number;
  failed_cases: number;
  aggregate_score: number;
  success_rate: number;
  status_detail: string | null;
  results: ExperimentResult[];
}

export interface ProviderHealth {
  id: string;
  name: string;
  provider?: string;
  status: string;
  latency: number;
  latency_ms?: number;
  active_models: string[];
  models?: string[];
  error_rate: number;
  version: string;
}

export interface ScheduledJob {
  id: string;
  name: string;
  cron_expression: string;
  pipeline: string;
  next_run: string;
  enabled: boolean;
}

// Local Storage Keys for opt-in development mocks
const MOCK_PROJECTS_KEY = 'evalforge_mock_projects';
const MOCK_DATASETS_KEY = 'evalforge_mock_datasets';
const MOCK_BENCHMARKS_KEY = 'evalforge_mock_benchmarks';
const MOCK_EXPERIMENTS_KEY = 'evalforge_mock_experiments';
const MOCK_PROVIDERS_KEY = 'evalforge_mock_providers';

// Default Seed Data
const SEED_PROJECTS: Project[] = [
  {
    id: '1',
    name: 'Production LLM Evaluator',
    description: 'Core benchmark pipeline for enterprise agent model evaluations',
    created_at: '2026-08-01T10:00:00Z',
    datasets_count: 4,
    benchmarks_count: 2,
    evaluations_count: 12,
  },
  {
    id: '2',
    name: 'RAG Retrieval Benchmarks',
    description: 'Domain-specific evaluation suites for chunking & embedding models',
    created_at: '2026-08-10T14:30:00Z',
    datasets_count: 2,
    benchmarks_count: 1,
    evaluations_count: 5,
  },
  {
    id: '3',
    name: 'Customer Support Bot v2',
    description: 'Fine-tuning & safety evaluation for customer-facing chat assistant',
    created_at: '2026-08-18T09:15:00Z',
    datasets_count: 3,
    benchmarks_count: 3,
    evaluations_count: 8,
  },
];

const SEED_DATASETS: Dataset[] = [
  {
    id: 'd1',
    project_id: '1',
    name: 'Customer Support Inquiries',
    description: '1,200 curated multi-turn customer service conversations with intent annotations',
    visibility: 'public',
    owner: 'alex.chen',
    source: 'Production Logs',
    language: 'en-US',
    license: 'Internal-Proprietary',
    tags: ['support', 'multi-turn', 'gold-standard'],
    created_at: '2026-08-02T11:20:00Z',
    versions_count: 3,
    current_version: 'v1.2.0',
  },
  {
    id: 'd2',
    project_id: '1',
    name: 'Safety & Red Teaming Adversarial Prompts',
    description: 'Jailbreak prompts, PII extraction attempts, and safety edge cases',
    visibility: 'private',
    owner: 'security-team',
    source: 'Red Team Operations',
    language: 'en-US',
    license: 'Restricted',
    tags: ['safety', 'jailbreak', 'red-team'],
    created_at: '2026-08-05T16:45:00Z',
    versions_count: 2,
    current_version: 'v2.0.0',
  },
  {
    id: 'd3',
    project_id: '1',
    name: 'Code Generation Python Benchmarks',
    description: '500 Python coding problems with unit tests and docstring requirements',
    visibility: 'public',
    owner: 'dev-tools',
    source: 'GitHub Curated',
    language: 'python',
    license: 'MIT',
    tags: ['coding', 'python', 'unit-tests'],
    created_at: '2026-08-12T08:00:00Z',
    versions_count: 1,
    current_version: 'v1.0.0',
  },
  {
    id: 'd4',
    project_id: '2',
    name: 'Medical Q&A Knowledge Base',
    description: 'PubMed QA pairs for domain-specific RAG faithfulness testing',
    visibility: 'private',
    owner: 'health-ai',
    source: 'PubMed Open',
    language: 'en-US',
    license: 'CC-BY-4.0',
    tags: ['rag', 'medical', 'pubmed'],
    created_at: '2026-08-14T13:10:00Z',
    versions_count: 1,
    current_version: 'v1.0.0',
  },
];

const SEED_BENCHMARKS: Benchmark[] = [
  {
    id: 'b1',
    project_id: '1',
    name: 'Enterprise Quality & Safety Suite v2',
    description: 'Comprehensive baseline evaluation covering accuracy, safety, and hallucination',
    tags: ['enterprise', 'baseline', 'production-gate'],
    dataset_ids: ['d1', 'd2'],
    created_at: '2026-08-03T12:00:00Z',
    datasets_count: 2,
  },
  {
    id: 'b2',
    project_id: '1',
    name: 'Python Code Synthesis Benchmark',
    description: 'Automated functional test runner for model code generation outputs',
    tags: ['code', 'python', 'execution'],
    dataset_ids: ['d3'],
    created_at: '2026-08-13T10:30:00Z',
    datasets_count: 1,
  },
  {
    id: 'b3',
    project_id: '2',
    name: 'RAG Retrieval Faithfulness Suite',
    description: 'Hallucination and context relevance metrics for medical domain RAG',
    tags: ['rag', 'faithfulness', 'medical'],
    dataset_ids: ['d4'],
    created_at: '2026-08-15T15:00:00Z',
    datasets_count: 1,
  },
];

const SEED_EXPERIMENTS: Experiment[] = [
  {
    id: 'e1',
    project_id: '1',
    dataset_version_id: 'v1.2.0',
    name: 'GPT-4o vs Claude 3.5 Sonnet Support Baseline',
    description: 'Comparative accuracy and tone benchmark on customer support inquiries',
    status: 'COMPLETED',
    judge: 'gpt-4o-judge',
    provider: 'openai',
    model: 'gpt-4o-2024-08-06',
    configuration: { temperature: 0.2, top_p: 0.95 },
    created_at: '2026-08-20T09:00:00Z',
    completed_at: '2026-08-20T09:14:22Z',
    completed_cases: 1200,
    failed_cases: 23,
    aggregate_score: 0.942,
    success_rate: 0.981,
    status_detail: null,
    results: [
      {
        id: 'r1',
        input_prompt: 'How do I request a refund for my subscription order #EF-9482?',
        model_output:
          'To request a refund for order #EF-9482, please log into your account dashboard...',
        reference:
          'Direct the user to Account > Billing > Order History and select Request Refund.',
        score: 0.98,
        passed: true,
        confidence: 0.99,
        reasoning:
          'Model output correctly identifies refund policy steps and references the order number.',
        judge: 'gpt-4o-judge',
        provider: 'openai',
      },
    ],
  },
  {
    id: 'e2',
    project_id: '1',
    dataset_version_id: 'v2.0.0',
    name: 'Red Team Safety Hardening Gate',
    description: 'Jailbreak resistance evaluation across Llama-3-70B and GPT-4o',
    status: 'RUNNING',
    judge: 'claude-3-5-sonnet',
    provider: 'anthropic',
    model: 'claude-3-5-sonnet-20241022',
    configuration: { temperature: 0.0 },
    created_at: '2026-08-28T14:00:00Z',
    completed_at: null,
    completed_cases: 340,
    failed_cases: 2,
    aggregate_score: 0.994,
    success_rate: 0.994,
    status_detail: 'Evaluating batch 35/50...',
    results: [],
  },
];

const SEED_PROVIDERS: ProviderHealth[] = [
  {
    id: 'p1',
    name: 'OpenAI Enterprise API',
    status: 'healthy',
    latency: 185,
    active_models: ['gpt-4o', 'gpt-4o-mini', 'o1-preview'],
    error_rate: 0.001,
    version: 'v1.4.0',
  },
  {
    id: 'p2',
    name: 'Anthropic Claude Engine',
    status: 'healthy',
    latency: 210,
    active_models: ['claude-3-5-sonnet', 'claude-3-haiku'],
    error_rate: 0.0,
    version: 'v2.1.0',
  },
  {
    id: 'p3',
    name: 'HuggingFace Local Inference Server',
    status: 'degraded',
    latency: 1200,
    active_models: ['meta-llama-3-8b-instruct'],
    error_rate: 0.08,
    version: 'v0.14.2',
  },
  {
    id: 'p4',
    name: 'Cohere Embed & Command',
    status: 'healthy',
    latency: 310,
    active_models: ['command-r-plus'],
    error_rate: 0.0,
    version: 'v1.0.0',
  },
];

function getOrSeed<T>(key: string, seed: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) {
      localStorage.setItem(key, JSON.stringify(seed));
      return seed;
    }
    return JSON.parse(raw);
  } catch {
    return seed;
  }
}

export const seedMockData = () => {
  if (ENABLE_MOCKS) {
    getOrSeed(MOCK_PROJECTS_KEY, SEED_PROJECTS);
    getOrSeed(MOCK_DATASETS_KEY, SEED_DATASETS);
    getOrSeed(MOCK_BENCHMARKS_KEY, SEED_BENCHMARKS);
    getOrSeed(MOCK_EXPERIMENTS_KEY, SEED_EXPERIMENTS);
    getOrSeed(MOCK_PROVIDERS_KEY, SEED_PROVIDERS);
  }
};

// API Services object encapsulating real backend endpoints with opt-in development mocks
export const api = {
  projects: {
    list: async () => {
      try {
        const res = await apiClient.get('/projects');
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) return getOrSeed(MOCK_PROJECTS_KEY, SEED_PROJECTS);
        throw err;
      }
    },
    create: async (data: { name: string; description?: string }) => {
      try {
        const res = await apiClient.post('/projects/', data);
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const projects = getOrSeed(MOCK_PROJECTS_KEY, SEED_PROJECTS);
          const newProj = {
            id: String(projects.length + 1),
            name: data.name,
            description: data.description || '',
            created_at: new Date().toISOString(),
            datasets_count: 0,
            benchmarks_count: 0,
            evaluations_count: 0,
          };
          localStorage.setItem(MOCK_PROJECTS_KEY, JSON.stringify([...projects, newProj]));
          return newProj;
        }
        throw err;
      }
    },
    delete: async (id: string) => {
      try {
        await apiClient.delete(`/projects/${id}`);
        return true;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const projects = getOrSeed(MOCK_PROJECTS_KEY, SEED_PROJECTS);
          const filtered = projects.filter((p) => p.id !== id);
          localStorage.setItem(MOCK_PROJECTS_KEY, JSON.stringify(filtered));
          return true;
        }
        throw err;
      }
    },
  },
  datasets: {
    list: async (projectId: string) => {
      try {
        const res = await apiClient.get(`/datasets/?project_id=${projectId}`);
        return res.data.datasets || res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const datasets = getOrSeed(MOCK_DATASETS_KEY, SEED_DATASETS);
          return datasets.filter((d) => d.project_id === projectId);
        }
        throw err;
      }
    },
    create: async (data: Partial<Dataset>, projectId: string) => {
      try {
        const res = await apiClient.post(`/datasets/?project_id=${projectId}`, data);
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const datasets = getOrSeed(MOCK_DATASETS_KEY, SEED_DATASETS);
          const newDataset = {
            id: `d${datasets.length + 1}`,
            project_id: projectId,
            name: data.name,
            description: data.description || '',
            visibility: data.visibility || 'private',
            owner: data.owner || 'current_user',
            source: data.source || 'Manual',
            language: data.language || 'en',
            license: data.license || 'None',
            tags: data.tags || [],
            created_at: new Date().toISOString(),
            versions_count: 1,
            current_version: 'v1',
          };
          localStorage.setItem(MOCK_DATASETS_KEY, JSON.stringify([...datasets, newDataset]));
          return newDataset;
        }
        throw err;
      }
    },
    upload: async (formData: FormData) => {
      try {
        const res = await apiClient.post('/datasets/import', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const datasetName = formData.get('dataset_name') as string;
          const projectId = formData.get('project_id') as string;
          const versionLabel = (formData.get('version_label') as string) || 'v1';

          const datasets = getOrSeed(MOCK_DATASETS_KEY, SEED_DATASETS);
          const newDataset = {
            id: `d${datasets.length + 1}`,
            project_id: projectId,
            name: datasetName,
            description: (formData.get('description') as string) || 'Uploaded dataset file',
            visibility: 'private',
            owner: 'developer',
            source: 'File Upload',
            language: 'en',
            license: 'MIT',
            tags: ['upload'],
            created_at: new Date().toISOString(),
            versions_count: 1,
            current_version: versionLabel,
          };
          localStorage.setItem(MOCK_DATASETS_KEY, JSON.stringify([...datasets, newDataset]));
          return {
            job_id: `job-${Math.random().toString(36).substring(7)}`,
            status: 'COMPLETED',
            version_id: `v-${Math.random().toString(36).substring(7)}`,
            records_imported: 12,
          };
        }
        throw err;
      }
    },
    get: async (datasetId: string) => {
      try {
        const res = await apiClient.get(`/datasets/${datasetId}`);
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const datasets = getOrSeed(MOCK_DATASETS_KEY, SEED_DATASETS);
          return datasets.find((d) => d.id === datasetId) || datasets[0];
        }
        throw err;
      }
    },
    versions: {
      list: async (datasetId: string) => {
        try {
          const res = await apiClient.get(`/datasets/${datasetId}/versions`);
          return res.data;
        } catch (err) {
          if (ENABLE_MOCKS) {
            return [
              {
                id: 'v1',
                label: 'v1.0.0',
                description: 'Initial golden checkpoint',
                created_at: '2026-07-01T11:00:00Z',
                records_count: 50,
              },
              {
                id: 'v2',
                label: 'v1.1.0',
                description: 'Added 10 safety prompts',
                created_at: '2026-07-02T13:40:00Z',
                records_count: 120,
              },
            ];
          }
          throw err;
        }
      },
    },
    records: {
      list: async (datasetId: string, versionId?: string) => {
        try {
          const res = await apiClient.get(
            `/datasets/${datasetId}/records?version=${versionId || ''}`
          );
          return res.data.records || res.data;
        } catch (err) {
          if (ENABLE_MOCKS) {
            return [
              {
                id: 'r1',
                input_prompt: 'Explain quantum computing simply in beginner terms.',
                candidate_output: 'Quantum computing processes information using qubits...',
                reference: 'Simplistic explanation of superposition and qubits.',
                score: 0.96,
                passed: true,
                reasoning: 'Output is mathematically clear and appropriate for beginners.',
              },
              {
                id: 'r2',
                input_prompt: 'How to write a production FastAPI server?',
                candidate_output: 'Use FastAPI with uvicorn worker processes...',
                reference: 'FastAPI standard boilerplate with gunicorn/uvicorn workers.',
                score: 0.94,
                passed: true,
                reasoning: 'Correct architecture pattern provided.',
              },
            ];
          }
          throw err;
        }
      },
    },
  },
  benchmarks: {
    list: async (projectId: string) => {
      try {
        const res = await apiClient.get(`/benchmarks/?project_id=${projectId}`);
        return res.data.benchmark_suites || res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const benchmarks = getOrSeed(MOCK_BENCHMARKS_KEY, SEED_BENCHMARKS);
          return benchmarks.filter((b) => b.project_id === projectId);
        }
        throw err;
      }
    },
    create: async (data: Partial<Benchmark>, projectId: string) => {
      try {
        const res = await apiClient.post(`/benchmarks/?project_id=${projectId}`, data);
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const benchmarks = getOrSeed(MOCK_BENCHMARKS_KEY, SEED_BENCHMARKS);
          const newBench = {
            id: `b${benchmarks.length + 1}`,
            project_id: projectId,
            name: data.name,
            description: data.description || '',
            tags: data.tags || [],
            dataset_ids: data.dataset_ids || [],
            created_at: new Date().toISOString(),
            datasets_count: (data.dataset_ids || []).length,
          };
          localStorage.setItem(MOCK_BENCHMARKS_KEY, JSON.stringify([...benchmarks, newBench]));
          return newBench;
        }
        throw err;
      }
    },
  },
  experiments: {
    list: async (projectId: string) => {
      try {
        const res = await apiClient.get(`/experiments/?project_id=${projectId}`);
        return res.data.experiments || res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const experiments = getOrSeed(MOCK_EXPERIMENTS_KEY, SEED_EXPERIMENTS);
          return experiments.filter((e) => e.project_id === projectId);
        }
        throw err;
      }
    },
    create: async (data: Partial<Experiment>, projectId: string) => {
      try {
        const res = await apiClient.post(`/experiments/?project_id=${projectId}`, data);
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const experiments = getOrSeed(MOCK_EXPERIMENTS_KEY, SEED_EXPERIMENTS);
          const newExp = {
            id: `e${experiments.length + 1}`,
            project_id: projectId,
            dataset_version_id: data.dataset_version_id,
            name: data.name,
            description: data.description || '',
            status: 'PENDING',
            judge: data.judge,
            provider: data.provider,
            model: data.model || 'gpt-4o',
            configuration: data.configuration || {},
            created_at: new Date().toISOString(),
            completed_at: null,
            completed_cases: 0,
            failed_cases: 0,
            aggregate_score: 0.0,
            success_rate: 0.0,
            status_detail: null,
            results: [],
          };
          localStorage.setItem(MOCK_EXPERIMENTS_KEY, JSON.stringify([...experiments, newExp]));
          return newExp;
        }
        throw err;
      }
    },
    execute: async (id: string) => {
      try {
        const res = await apiClient.post(`/experiments/${id}/execute`);
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) {
          const experiments = getOrSeed(MOCK_EXPERIMENTS_KEY, SEED_EXPERIMENTS);
          const updated = experiments.map((exp) => {
            if (exp.id === id) {
              return {
                ...exp,
                status: 'COMPLETED',
                completed_at: new Date().toISOString(),
                completed_cases: 15,
                failed_cases: 0,
                aggregate_score: 0.91,
                success_rate: 1.0,
                results: [
                  {
                    id: 'r1',
                    input_prompt: 'Solve 5+5',
                    model_output: '10',
                    reference: '10',
                    score: 1.0,
                    passed: true,
                    confidence: 0.99,
                    reasoning: 'Model response is mathematically correct.',
                    judge: exp.judge,
                    provider: exp.provider,
                  },
                ],
              };
            }
            return exp;
          });
          localStorage.setItem(MOCK_EXPERIMENTS_KEY, JSON.stringify(updated));
          return updated.find((e) => e.id === id);
        }
        throw err;
      }
    },
  },
  providers: {
    list: async () => {
      try {
        const res = await apiClient.get('/providers');
        return res.data;
      } catch (err) {
        if (ENABLE_MOCKS) return getOrSeed(MOCK_PROVIDERS_KEY, SEED_PROVIDERS);
        throw err;
      }
    },
  },
  enterprise: {
    apiKeys: {
      list: async () => {
        const res = await apiClient.get('/api-keys');
        return res.data.data || res.data;
      },
      create: async (data: {
        name: string;
        organization_id?: string;
        workspace_id?: string;
        expires_in_days?: number;
      }) => {
        const res = await apiClient.post('/api-keys', data);
        return res.data.data || res.data;
      },
      revoke: async (id: string) => {
        const res = await apiClient.delete(`/api-keys/${id}`);
        return res.data;
      },
    },
    getSubscription: async (orgId: string) => {
      const res = await apiClient.get(`/billing/subscription?org_id=${orgId}`);
      return res.data.data;
    },
    createCheckout: async (orgId: string, planName: string, successUrl?: string, cancelUrl?: string) => {
      const params = new URLSearchParams({ org_id: orgId, plan_name: planName });
      if (successUrl) params.append('success_url', successUrl);
      if (cancelUrl) params.append('cancel_url', cancelUrl);
      const res = await apiClient.post(`/billing/checkout?${params.toString()}`);
      return res.data.data;
    },
    createPortalSession: async (orgId: string, returnUrl?: string) => {
      const params = new URLSearchParams({ org_id: orgId });
      if (returnUrl) params.append('return_url', returnUrl);
      const res = await apiClient.post(`/billing/customer-portal?${params.toString()}`);
      return res.data.data;
    },
    getInvoices: async (orgId: string) => {
      const res = await apiClient.get(`/billing/invoices?org_id=${orgId}`);
      return res.data.data;
    },
    listMembers: async (orgId: string) => {
      const res = await apiClient.get(`/organizations/${orgId}/members`);
      return res.data.data;
    },
    listInvitations: async (orgId: string) => {
      const res = await apiClient.get(`/organizations/${orgId}/invitations`);
      return res.data.data;
    },
    inviteMember: async (orgId: string, email: string, role: string = 'Member') => {
      const res = await apiClient.post(`/organizations/${orgId}/invitations`, { email, role });
      return res.data.data;
    },
    revokeInvitation: async (orgId: string, invitationId: string) => {
      const res = await apiClient.delete(`/organizations/${orgId}/invitations/${invitationId}`);
      return res.data.data;
    },
    resendInvitation: async (orgId: string, invitationId: string) => {
      const res = await apiClient.post(`/organizations/${orgId}/invitations/${invitationId}/resend`);
      return res.data.data;
    },
    acceptInvitation: async (token: string) => {
      const res = await apiClient.post(`/organizations/invitations/${token}/accept`);
      return res.data.data;
    },
    removeMember: async (orgId: string, membershipId: string) => {
      const res = await apiClient.delete(`/organizations/${orgId}/members/${membershipId}`);
      return res.data.data;
    },
    getWorkspaceQuota: async (wsId: string, orgId: string, metric: string) => {
      const res = await apiClient.get(`/workspaces/${wsId}/quotas/${metric}?org_id=${orgId}`);
      return res.data.data;
    },
  },
  health: async () => {
    try {
      const res = await apiClient.get('/health');
      return res.data;
    } catch (err) {
      if (ENABLE_MOCKS)
        return { status: 'healthy', services: { api: 'healthy', database: 'healthy' } };
      throw err;
    }
  },
  jobs: {
    scheduler: {
      list: async () => {
        try {
          const res = await apiClient.get('/jobs/scheduler/jobs');
          return res.data.data || res.data;
        } catch (err) {
          if (ENABLE_MOCKS) {
            return [
              {
                id: 'job-sch-1',
                name: 'Nightly LLM Regression Evaluation',
                cron_expression: '0 0 * * *',
                pipeline: 'Daily Model Quality Drift Check',
                next_run: '2026-09-02T00:00:00Z',
                enabled: true,
              },
            ];
          }
          throw err;
        }
      },
      create: async (data: { name: string; cron_expression: string; pipeline?: string }) => {
        try {
          const res = await apiClient.post('/jobs/scheduler/jobs', data);
          return res.data.data || res.data;
        } catch (err) {
          if (ENABLE_MOCKS) {
            return {
              id: `job-sch-${Date.now()}`,
              name: data.name,
              cron_expression: data.cron_expression,
              pipeline: data.pipeline || 'Custom Pipeline',
              next_run: new Date().toISOString(),
              enabled: true,
            };
          }
          throw err;
        }
      },
    },
    listScheduled: async () => {
      const res = await apiClient.get('/jobs/scheduler/jobs');
      return res.data.data;
    },
    triggerCron: async (jobId: string) => {
      const res = await apiClient.post(`/jobs/scheduler/jobs/${jobId}/trigger`);
      return res.data.data;
    },
    toggleCron: async (jobId: string) => {
      const res = await apiClient.post(`/jobs/scheduler/jobs/${jobId}/toggle`);
      return res.data.data;
    },
    getCronHistory: async () => {
      const res = await apiClient.get('/jobs/scheduler/history');
      return res.data.data;
    },
  },
};
