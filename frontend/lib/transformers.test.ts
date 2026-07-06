import { describe, it, expect } from "vitest";
import {
  transformAskResponse,
  transformSources,
  transformBenchmark,
} from "../lib/transformers";

describe("transformAskResponse", () => {
  it("maps backend snake_case to frontend camelCase", () => {
    const result = transformAskResponse({
      query_id: "550e8400-e29b-41d4-a716-446655440000",
      question: "What are the side effects of Metformin?",
      answer: "Metformin may cause nausea.",
      insufficient_evidence: false,
      confidence_score: 0.91,
      hallucination_risk_pct: 12,
      hallucination_classification: "Verified",
      claims: [
        {
          claim: "Metformin may cause nausea",
          status: "SUPPORTED",
          confidence: 0.94,
          hallucination_risk: "Verified",
          evidence: [{ source: "PubMed", excerpt: "GI symptoms." }],
        },
      ],
      citations: [
        {
          reference_num: 1,
          title: "Metformin Review",
          authors: ["Smith J"],
          source: "PubMed",
        },
      ],
      pipeline_latency_ms: 3200,
      model_used: "gpt-4o",
    });

    expect(result.id).toBe("550e8400-e29b-41d4-a716-446655440000");
    expect(result.overallConfidence).toBe(0.91);
    expect(result.claims[0].status).toBe("supported");
  });
});

describe("transformSources", () => {
  it("maps source list items", () => {
    const sources = transformSources({
      items: [
        {
          id: "doc-1",
          title: "Test",
          authors: ["A"],
          source: "PubMed",
          pmid: "123",
          abstract: "Abstract",
        },
      ],
      total: 1,
      page: 1,
      page_size: 20,
    });
    expect(sources).toHaveLength(1);
    expect(sources[0].sourceType).toBe("pubmed");
  });
});

describe("transformBenchmark", () => {
  it("maps benchmark results to leaderboard", () => {
    const result = transformBenchmark({
      benchmark_id: "b-1",
      name: "Test",
      status: "completed",
      results: [
        {
          model_name: "gpt-4o",
          accuracy: 0.9,
          hallucination_rate: 0.1,
          faithfulness: 0.85,
          avg_latency_ms: 1200,
          total_cost_usd: 0.05,
        },
      ],
    });
    expect(result.models[0].name).toBe("gpt-4o");
  });
});
