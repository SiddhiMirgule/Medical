import type {
  AskResponse,
  AskStreamChunk,
  BenchmarkResult,
  EvaluationMetrics,
  MetricsHistory,
  ResearchData,
  Source,
  AdminSettings,
} from "@/types";
import {
  MOCK_SOURCES,
  MOCK_ASK_RESPONSE,
  MOCK_EVALUATION,
  MOCK_METRICS_HISTORY,
  MOCK_BENCHMARK,
  MOCK_RESEARCH,
  MOCK_ADMIN_SETTINGS,
  getMockAskResponse,
  getMockResearch,
} from "./mock-data";
import {
  transformAdminSettings,
  transformAskResponse,
  transformBenchmark,
  transformMetrics,
  transformMetricsHistory,
  transformResearch,
  transformSources,
  toBackendAdminSettings,
  type BackendAskResponse,
} from "./transformers";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private baseUrl: string;
  private useMock: boolean = false;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    this.useMock = false;
    return response.json();
  }

  isUsingMock(): boolean {
    return this.useMock;
  }

  async ask(question: string, researchMode = false): Promise<AskResponse> {
    try {
      const data = await this.request<BackendAskResponse>("/ask", {
        method: "POST",
        body: JSON.stringify({ question, research_mode: researchMode }),
      });
      return transformAskResponse(data);
    } catch {
      this.useMock = true;
      await this.delay(800);
      return {
        ...MOCK_ASK_RESPONSE,
        id: `q-${Date.now()}`,
        question,
      };
    }
  }

  async *askStream(question: string): AsyncGenerator<AskStreamChunk> {
    try {
      const response = await fetch(`${this.baseUrl}/ask/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, stream: true }),
      });

      if (!response.ok || !response.body) {
        throw new Error("Stream unavailable");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = JSON.parse(line.slice(6)) as {
            type: string;
            content?: string;
            result?: BackendAskResponse;
          };

          if (payload.type === "token" && payload.content) {
            yield { type: "token", content: payload.content };
          } else if (
            (payload.type === "complete" || payload.type === "done") &&
            payload.result
          ) {
            const transformed = transformAskResponse(payload.result);
            yield { type: "done", data: transformed };
          }
        }
      }
    } catch {
      this.useMock = true;
      yield* this.mockStream(question);
    }
  }

  private async *mockStream(question: string): AsyncGenerator<AskStreamChunk> {
    const answer = MOCK_ASK_RESPONSE.answer;
    const words = answer.split(" ");

    for (let i = 0; i < words.length; i++) {
      await this.delay(40);
      yield {
        type: "token",
        content: (i === 0 ? "" : " ") + words[i],
      };
    }

    await this.delay(200);
    yield {
      type: "done",
      data: {
        ...MOCK_ASK_RESPONSE,
        id: `q-${Date.now()}`,
        question,
        status: "completed",
      },
    };
  }

  async getResult(id: string): Promise<AskResponse> {
    try {
      const data = await this.request<BackendAskResponse>(`/results/${id}`);
      return transformAskResponse(data);
    } catch {
      this.useMock = true;
      await this.delay(300);
      return getMockAskResponse(id);
    }
  }

  async getSources(params?: {
    search?: string;
    sourceType?: string;
    limit?: number;
  }): Promise<Source[]> {
    try {
      const query = new URLSearchParams();
      if (params?.search) query.set("search", params.search);
      if (params?.sourceType && params.sourceType !== "all") {
        query.set("source", params.sourceType);
      }
      if (params?.limit) query.set("page_size", String(params.limit));
      const qs = query.toString();
      const data = await this.request<{
        items: Array<{
          id: string;
          title: string;
          authors: string[];
          source: string;
          publication_date?: string;
          pmid?: string;
          url?: string;
          abstract?: string;
          document_type?: string;
        }>;
        total: number;
        page: number;
        page_size: number;
      }>(`/sources${qs ? `?${qs}` : ""}`);
      return transformSources(data);
    } catch {
      this.useMock = true;
      await this.delay(400);
      let sources = [...MOCK_SOURCES];
      if (params?.search) {
        const q = params.search.toLowerCase();
        sources = sources.filter(
          (s) =>
            s.title.toLowerCase().includes(q) ||
            s.abstract.toLowerCase().includes(q) ||
            s.pmid.includes(q)
        );
      }
      if (params?.sourceType && params.sourceType !== "all") {
        sources = sources.filter((s) => s.sourceType === params.sourceType);
      }
      return sources;
    }
  }

  async getEvaluation(): Promise<EvaluationMetrics> {
    try {
      const data = await this.request<Parameters<typeof transformMetrics>[0]>("/metrics");
      return transformMetrics(data);
    } catch {
      this.useMock = true;
      await this.delay(400);
      return MOCK_EVALUATION;
    }
  }

  async getMetricsHistory(): Promise<MetricsHistory[]> {
    try {
      const data = await this.request<Array<Record<string, number | string>>>("/metrics/history");
      return transformMetricsHistory(data);
    } catch {
      this.useMock = true;
      await this.delay(300);
      return MOCK_METRICS_HISTORY;
    }
  }

  async getBenchmark(): Promise<BenchmarkResult> {
    try {
      const data = await this.request<Parameters<typeof transformBenchmark>[0]>("/benchmark");
      return transformBenchmark(data);
    } catch {
      this.useMock = true;
      await this.delay(400);
      return MOCK_BENCHMARK;
    }
  }

  async getResearch(id: string): Promise<ResearchData> {
    try {
      const data = await this.request<Parameters<typeof transformResearch>[0]>(`/research/${id}`);
      return transformResearch(data);
    } catch {
      this.useMock = true;
      await this.delay(400);
      return getMockResearch(id);
    }
  }

  async getAdminSettings(): Promise<AdminSettings> {
    try {
      const data = await this.request<Parameters<typeof transformAdminSettings>[0]>("/admin/settings");
      return transformAdminSettings(data);
    } catch {
      this.useMock = true;
      await this.delay(300);
      return MOCK_ADMIN_SETTINGS;
    }
  }

  async updateAdminSettings(settings: Partial<AdminSettings>): Promise<AdminSettings> {
    try {
      const data = await this.request<Parameters<typeof transformAdminSettings>[0]>("/admin/settings", {
        method: "PUT",
        body: JSON.stringify(toBackendAdminSettings(settings)),
      });
      return transformAdminSettings(data);
    } catch {
      this.useMock = true;
      await this.delay(300);
      return { ...MOCK_ADMIN_SETTINGS, ...settings };
    }
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export const api = new ApiClient(API_BASE);
