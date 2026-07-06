import type {
  AskResponse,
  BenchmarkResult,
  EvaluationMetrics,
  MetricsHistory,
  ResearchData,
  Source,
  AdminSettings,
} from "@/types";

export const MOCK_SOURCES: Source[] = [
  {
    id: "src-1",
    title: "Metformin in the Treatment of Type 2 Diabetes: A Systematic Review",
    authors: ["Smith, J.", "Johnson, A.", "Williams, R."],
    publicationDate: "2024-03-15",
    pmid: "38123456",
    abstract:
      "Metformin remains the first-line pharmacological treatment for type 2 diabetes mellitus. This systematic review examines its efficacy, safety profile, and common adverse effects including gastrointestinal symptoms such as nausea, diarrhea, and abdominal discomfort.",
    sourceUrl: "https://pubmed.ncbi.nlm.nih.gov/38123456",
    sourceType: "pubmed",
    citationCount: 342,
    relevanceScore: 0.94,
  },
  {
    id: "src-2",
    title: "NIH Clinical Guidelines: Pharmacologic Approaches to Glycemic Treatment",
    authors: ["National Institutes of Health"],
    publicationDate: "2023-11-20",
    pmid: "37890123",
    abstract:
      "Clinical practice guidelines recommend metformin as initial therapy for type 2 diabetes when lifestyle modifications are insufficient. Monitoring for vitamin B12 deficiency with long-term use is advised.",
    sourceUrl: "https://www.nih.gov/guidelines/diabetes",
    sourceType: "nih",
    citationCount: 128,
    relevanceScore: 0.89,
  },
  {
    id: "src-3",
    title: "WHO Model List of Essential Medicines: Antidiabetic Agents",
    authors: ["World Health Organization"],
    publicationDate: "2024-01-10",
    pmid: "37234567",
    abstract:
      "Metformin is included in the WHO Model List of Essential Medicines for the management of type 2 diabetes, recognized for its efficacy, safety, and cost-effectiveness in diverse healthcare settings.",
    sourceUrl: "https://www.who.int/medicines",
    sourceType: "who",
    citationCount: 89,
    relevanceScore: 0.82,
  },
  {
    id: "src-4",
    title: "Lactic Acidosis Risk with Metformin: A Meta-Analysis",
    authors: ["Chen, L.", "Patel, S."],
    publicationDate: "2023-08-05",
    pmid: "36567890",
    abstract:
      "While metformin-associated lactic acidosis is rare in patients without contraindications, caution is warranted in renal impairment. Gastrointestinal side effects remain the most commonly reported adverse events.",
    sourceUrl: "https://pubmed.ncbi.nlm.nih.gov/36567890",
    sourceType: "pubmed",
    citationCount: 56,
    relevanceScore: 0.76,
  },
  {
    id: "src-5",
    title: "ADA Standards of Care in Diabetes—2024",
    authors: ["American Diabetes Association"],
    publicationDate: "2024-01-01",
    pmid: "38012345",
    abstract:
      "The American Diabetes Association recommends individualized glycemic targets and metformin as foundational therapy, with regular assessment of cardiovascular and renal outcomes.",
    sourceUrl: "https://diabetesjournals.org/care",
    sourceType: "guideline",
    citationCount: 210,
    relevanceScore: 0.91,
  },
];

export const MOCK_ASK_RESPONSE: AskResponse = {
  id: "q-mock-001",
  question: "What are the side effects of Metformin?",
  answer:
    "Metformin is commonly associated with gastrointestinal side effects, including nausea, diarrhea, abdominal discomfort, and loss of appetite. These effects are typically mild and often diminish over time. Rare but serious adverse effects include lactic acidosis, particularly in patients with renal impairment. Long-term use may be associated with vitamin B12 deficiency.",
  claims: [
    {
      id: "c-1",
      claim: "Metformin is commonly associated with gastrointestinal side effects",
      status: "supported",
      confidence: 0.96,
      hallucinationRisk: "verified",
      evidence: [
        {
          source: "PubMed PMID: 38123456",
          excerpt: "The most common adverse effects are gastrointestinal, including nausea and diarrhea.",
          pmid: "38123456",
        },
      ],
    },
    {
      id: "c-2",
      claim: "Metformin may cause nausea, diarrhea, and abdominal discomfort",
      status: "supported",
      confidence: 0.94,
      hallucinationRisk: "verified",
      evidence: [
        {
          source: "PubMed PMID: 38123456",
          excerpt: "GI symptoms including nausea, diarrhea, and abdominal discomfort were reported in 25-30% of patients.",
          pmid: "38123456",
        },
      ],
    },
    {
      id: "c-3",
      claim: "Long-term metformin use may cause vitamin B12 deficiency",
      status: "partially_supported",
      confidence: 0.78,
      hallucinationRisk: "low_confidence",
      evidence: [
        {
          source: "NIH Clinical Guidelines",
          excerpt: "Monitoring for vitamin B12 deficiency with long-term use is advised.",
        },
      ],
    },
    {
      id: "c-4",
      claim: "Metformin causes lactic acidosis in all patients",
      status: "contradicted",
      confidence: 0.12,
      hallucinationRisk: "potential_hallucination",
      evidence: [
        {
          source: "PubMed PMID: 36567890",
          excerpt: "Metformin-associated lactic acidosis is rare in patients without contraindications.",
          pmid: "36567890",
        },
      ],
    },
  ],
  sources: MOCK_SOURCES.slice(0, 4),
  overallConfidence: 0.87,
  hallucinationRisk: 0.12,
  createdAt: new Date().toISOString(),
  status: "completed",
};

export const MOCK_EVALUATION: EvaluationMetrics = {
  faithfulness: 0.89,
  contextPrecision: 0.85,
  contextRecall: 0.78,
  answerRelevancy: 0.92,
  timestamp: new Date().toISOString(),
};

export const MOCK_METRICS_HISTORY: MetricsHistory[] = [
  { date: "2024-01", faithfulness: 0.82, contextPrecision: 0.78, contextRecall: 0.71, answerRelevancy: 0.85 },
  { date: "2024-02", faithfulness: 0.84, contextPrecision: 0.80, contextRecall: 0.74, answerRelevancy: 0.87 },
  { date: "2024-03", faithfulness: 0.86, contextPrecision: 0.82, contextRecall: 0.76, answerRelevancy: 0.89 },
  { date: "2024-04", faithfulness: 0.87, contextPrecision: 0.84, contextRecall: 0.77, answerRelevancy: 0.90 },
  { date: "2024-05", faithfulness: 0.88, contextPrecision: 0.85, contextRecall: 0.78, answerRelevancy: 0.91 },
  { date: "2024-06", faithfulness: 0.89, contextPrecision: 0.85, contextRecall: 0.78, answerRelevancy: 0.92 },
];

export const MOCK_BENCHMARK: BenchmarkResult = {
  models: [
    { id: "gpt-4o", name: "GPT-4o", accuracy: 0.91, hallucinationRate: 0.08, faithfulness: 0.89, latencyMs: 2340, costPerQuery: 0.024 },
    { id: "claude-sonnet", name: "Claude Sonnet", accuracy: 0.89, hallucinationRate: 0.10, faithfulness: 0.87, latencyMs: 1890, costPerQuery: 0.018 },
    { id: "llama-3.1", name: "Llama 3.1 70B", accuracy: 0.82, hallucinationRate: 0.15, faithfulness: 0.80, latencyMs: 3200, costPerQuery: 0.008 },
    { id: "medverify", name: "MedVerify AI", accuracy: 0.94, hallucinationRate: 0.05, faithfulness: 0.93, latencyMs: 4100, costPerQuery: 0.032 },
  ],
  lastUpdated: new Date().toISOString(),
  totalQueries: 1250,
};

export const MOCK_RESEARCH: ResearchData = {
  queryId: "q-mock-001",
  question: "What are the side effects of Metformin?",
  retrievedChunks: [
    { id: "ch-1", text: "Metformin gastrointestinal adverse effects include nausea (25%), diarrhea (20%), and abdominal pain (15%).", similarityScore: 0.92, rerankScore: 0.95, sourceId: "src-1", sourceTitle: MOCK_SOURCES[0].title },
    { id: "ch-2", text: "First-line therapy for T2DM with well-established safety profile.", similarityScore: 0.85, rerankScore: 0.78, sourceId: "src-2", sourceTitle: MOCK_SOURCES[1].title },
    { id: "ch-3", text: "Vitamin B12 deficiency observed in 10-30% of long-term metformin users.", similarityScore: 0.81, rerankScore: 0.88, sourceId: "src-2", sourceTitle: MOCK_SOURCES[1].title },
    { id: "ch-4", text: "Lactic acidosis incidence <1 per 100,000 patient-years.", similarityScore: 0.76, rerankScore: 0.72, sourceId: "src-4", sourceTitle: MOCK_SOURCES[3].title },
    { id: "ch-5", text: "WHO essential medicine for diabetes management globally.", similarityScore: 0.68, rerankScore: 0.55, sourceId: "src-3", sourceTitle: MOCK_SOURCES[2].title },
  ],
  rerankedChunks: [
    { id: "ch-1", text: "Metformin gastrointestinal adverse effects include nausea (25%), diarrhea (20%), and abdominal pain (15%).", similarityScore: 0.92, rerankScore: 0.95, sourceId: "src-1", sourceTitle: MOCK_SOURCES[0].title },
    { id: "ch-3", text: "Vitamin B12 deficiency observed in 10-30% of long-term metformin users.", similarityScore: 0.81, rerankScore: 0.88, sourceId: "src-2", sourceTitle: MOCK_SOURCES[1].title },
    { id: "ch-2", text: "First-line therapy for T2DM with well-established safety profile.", similarityScore: 0.85, rerankScore: 0.78, sourceId: "src-2", sourceTitle: MOCK_SOURCES[1].title },
    { id: "ch-4", text: "Lactic acidosis incidence <1 per 100,000 patient-years.", similarityScore: 0.76, rerankScore: 0.72, sourceId: "src-4", sourceTitle: MOCK_SOURCES[3].title },
  ],
  embeddingModel: "BGE-Large-en-v1.5",
  retrievalMethod: "Hybrid (BM25 + Dense)",
  totalRetrieved: 25,
  totalAfterRerank: 4,
};

export const MOCK_ADMIN_SETTINGS: AdminSettings = {
  confidenceFormula: "weighted(retriever_score, source_count, cross_agreement, verifier_confidence)",
  retrievalTopK: 25,
  rerankTopK: 5,
  hallucinationThreshold: 0.3,
  enableStreaming: true,
  defaultModel: "gpt-4o",
};

export function getMockAskResponse(id: string): AskResponse {
  return { ...MOCK_ASK_RESPONSE, id };
}

export function getMockResearch(id: string): ResearchData {
  return { ...MOCK_RESEARCH, queryId: id };
}
