import axios, { AxiosInstance } from "axios";

export interface EvaluationPayload {
  evaluation_name: string;
  evaluation_description?: string;
  judge: "geval" | "deepeval" | "rubric";
  provider: string;
  test_cases: Array<{
    input_prompt: string;
    model_output: string;
    reference?: string;
  }>;
  configuration?: Record<string, any>;
}

export class EvalForgeClient {
  private client: AxiosInstance;

  constructor(baseURL: string, apiKey: string) {
    this.client = axios.create({
      baseURL: baseURL.replace(/\/$/, ""),
      headers: {
        "X-API-Key": apiKey,
        "Content-Type": "application/json",
      },
    });
  }

  public async triggerRun(
    projectId: string,
    payload: EvaluationPayload,
  ): Promise<any> {
    const url = "/api/v1/evaluations/batch";
    const body = { ...payload, project_id: projectId };
    const response = await this.client.post(url, body);
    return response.data;
  }

  public async getRunStatus(runId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/evaluations/runs/${runId}`);
    return response.data;
  }

  public async registerWebhook(
    projectId: string,
    targetUrl: string,
    events: string[],
  ): Promise<any> {
    const response = await this.client.post("/api/v1/webhooks", {
      project_id: projectId,
      target_url: targetUrl,
      events,
    });
    return response.data;
  }
}
