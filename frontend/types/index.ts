export type VerificationStatus =
  | "supported"
  | "partially_supported"
  | "unsupported"
  | "contradicted";

export type HallucinationRisk = "verified" | "low_confidence" | "potential_hallucination";

export interface Evidence {
  source: string;
  excerpt: string;
  pmid?: string;
  url?: string;
}

export interface Claim {
  id: string;
  claim: string;
  status: VerificationStatus;
  confidence: number;
  hallucinationRisk: HallucinationRisk;
  evidence: Evidence[];
}

export interface Source {
  id: string;
  title: string;
  authors: string[];
  publicationDate: string;
  pmid: string;
  abstract: string;
  sourceUrl: string;
  sourceType: "pubmed" | "nih" | "who" | "guideline" | "other";
  citationCount?: number;
  relevanceScore?: number;
}

export interface AskResponse {
  id: string;
  question: string;
  answer: string;
  claims: Claim[];
  sources: Source[];
  overallConfidence: number;
  hallucinationRisk: number;
  createdAt: string;
  status: "completed" | "processing" | "failed";
}

export interface AskStreamChunk {
  type: "token" | "claim" | "source" | "metadata" | "done" | "error";
  content?: string;
  data?: Partial<AskResponse>;
}

export interface EvaluationMetrics {
  faithfulness: number;
  contextPrecision: number;
  contextRecall: number;
  answerRelevancy: number;
  timestamp: string;
}

export interface BenchmarkModel {
  id: string;
  name: string;
  accuracy: number;
  hallucinationRate: number;
  faithfulness: number;
  latencyMs: number;
  costPerQuery: number;
}

export interface BenchmarkResult {
  models: BenchmarkModel[];
  lastUpdated: string;
  totalQueries: number;
}

export interface ResearchChunk {
  id: string;
  text: string;
  similarityScore: number;
  rerankScore: number;
  sourceId: string;
  sourceTitle: string;
}

export interface ResearchData {
  queryId: string;
  question: string;
  retrievedChunks: ResearchChunk[];
  rerankedChunks: ResearchChunk[];
  embeddingModel: string;
  retrievalMethod: string;
  totalRetrieved: number;
  totalAfterRerank: number;
}

export interface AdminSettings {
  confidenceFormula: string;
  retrievalTopK: number;
  rerankTopK: number;
  hallucinationThreshold: number;
  enableStreaming: boolean;
  defaultModel: string;
}

export interface MetricsHistory {
  date: string;
  faithfulness: number;
  contextPrecision: number;
  contextRecall: number;
  answerRelevancy: number;
}

export interface ApiError {
  message: string;
  status: number;
}
