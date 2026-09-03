export interface EvalForgeConfig {
  apiKey?: string;
  baseUrl?: string;
  timeoutMs?: number;
  maxRetries?: number;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  workspace_id?: string;
  created_at?: string;
}

export interface Dataset {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  created_at?: string;
}

export interface TestCase {
  input_prompt: string;
  model_output: string;
  reference?: string;
  context?: string;
  metadata?: Record<string, unknown>;
}

export interface EvaluationRun {
  id: string;
  project_id: string;
  name: string;
  status: string;
  total_cases: number;
  completed_cases: number;
  failed_cases: number;
  created_at?: string;
}

export interface EvaluationResult {
  id: string;
  run_id: string;
  input_prompt: string;
  model_output: string;
  reference?: string;
  metrics: Record<string, number | string | boolean>;
  passed: boolean;
  latency_ms?: number;
}

export interface Job {
  id: string;
  name: string;
  status: string;
  job_type: string;
  progress: number;
  created_at?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
}
