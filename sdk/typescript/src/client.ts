import {
  APIError,
  AuthenticationError,
  EvalForgeError,
  NotFoundError,
  RateLimitError,
} from './errors';
import {
  ApiResponse,
  Dataset,
  EvalForgeConfig,
  EvaluationResult,
  EvaluationRun,
  Job,
  Project,
  TestCase,
} from './types';

const DEFAULT_BASE_URL = 'http://localhost:8000';

declare const process: { env?: Record<string, string | undefined> } | undefined;

export class EvalForge {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly timeoutMs: number;
  private readonly maxRetries: number;

  constructor(config: EvalForgeConfig = {}) {
    const envKey = typeof process !== 'undefined' ? process?.env?.EVALFORGE_API_KEY : undefined;
    const key = config.apiKey ?? envKey;
    if (!key) {
      throw new AuthenticationError('API key must be provided or configured via EVALFORGE_API_KEY.');
    }
    this.apiKey = key;
    const envBaseUrl = typeof process !== 'undefined' ? process?.env?.EVALFORGE_BASE_URL : undefined;
    this.baseUrl = (config.baseUrl ?? envBaseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, '');
    this.timeoutMs = config.timeoutMs ?? 30000;
    this.maxRetries = config.maxRetries ?? 3;
  }

  private async request<T>(method: string, path: string, body?: unknown, params?: Record<string, string | number>): Promise<T> {
    let url = `${this.baseUrl}${path}`;
    if (params) {
      const searchParams = new URLSearchParams();
      for (const [k, v] of Object.entries(params)) {
        searchParams.append(k, String(v));
      }
      url += `?${searchParams.toString()}`;
    }

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), this.timeoutMs);

        const response = await fetch(url, {
          method,
          headers: {
            'X-API-Key': this.apiKey,
            'Content-Type': 'application/json',
            'User-Agent': '@evalforge/sdk/1.0.0',
          },
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        });
        clearTimeout(timer);

        const requestId = response.headers.get('X-Request-ID') ?? undefined;

        if (response.status === 401) {
          throw new AuthenticationError('Invalid API Key provided', requestId);
        } else if (response.status === 404) {
          throw new NotFoundError(`Resource not found at ${path}`, requestId);
        } else if (response.status === 429) {
          if (attempt < this.maxRetries - 1) {
            await new Promise((r) => setTimeout(r, 1000 * Math.pow(2, attempt)));
            continue;
          }
          throw new RateLimitError('Rate limit exceeded', requestId);
        } else if (!response.ok) {
          const errText = await response.text();
          throw new APIError(`API Request failed with status ${response.status}: ${errText}`, response.status, requestId);
        }

        const json = (await response.json()) as ApiResponse<T> | T;
        return (typeof json === 'object' && json !== null && 'data' in json ? (json as ApiResponse<T>).data : json) as T;
      } catch (err: unknown) {
        if (err instanceof EvalForgeError) throw err;
        if (attempt === this.maxRetries - 1) {
          throw new APIError(`Network transport failure: ${err instanceof Error ? err.message : String(err)}`, 500);
        }
        await new Promise((r) => setTimeout(r, 1000 * Math.pow(2, attempt)));
      }
    }
    throw new APIError('Request failed after maximum retries', 500);
  }

  public readonly projects = {
    create: (name: string, description?: string): Promise<Project> =>
      this.request<Project>('POST', '/api/v1/projects', { name, description }),
    list: (page = 1, pageSize = 20): Promise<Project[]> =>
      this.request<Project[]>('GET', '/api/v1/projects', undefined, { page, page_size: pageSize }),
    get: (id: string): Promise<Project> =>
      this.request<Project>('GET', `/api/v1/projects/${id}`),
  };

  public readonly datasets = {
    create: (projectId: string, name: string, description?: string): Promise<Dataset> =>
      this.request<Dataset>('POST', '/api/v1/datasets', { project_id: projectId, name, description }),
    list: (projectId: string): Promise<Dataset[]> =>
      this.request<Dataset[]>('GET', '/api/v1/datasets', undefined, { project_id: projectId }),
  };

  public readonly evaluations = {
    create: (projectId: string, name: string, testCases: TestCase[], metrics?: string[]): Promise<EvaluationRun> =>
      this.request<EvaluationRun>('POST', '/api/v1/evaluations', {
        project_id: projectId,
        name,
        test_cases: testCases,
        metrics: metrics ?? ['accuracy', 'semantic_similarity'],
      }),
    get: (runId: string): Promise<EvaluationRun> =>
      this.request<EvaluationRun>('GET', `/api/v1/evaluations/${runId}`),
    listResults: (runId: string, limit = 50): Promise<EvaluationResult[]> =>
      this.request<EvaluationResult[]>('GET', `/api/v1/evaluations/${runId}/results`, undefined, { limit }),
  };

  public readonly jobs = {
    get: (jobId: string): Promise<Job> =>
      this.request<Job>('GET', `/api/v1/jobs/${jobId}`),
  };
}
