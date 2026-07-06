"use client";

import { Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ChartSkeleton } from "@/components/StreamingAnswer";
import { MockDataBanner } from "@/components/MockDataBanner";
import { MetricCard, MetricsRadar, MetricsHistoryChart } from "@/components/charts/MetricsCharts";
import { useEvaluation } from "@/hooks/useEvaluation";
import { useAppStore } from "@/lib/store";

export default function EvaluationPage() {
  const { metrics, history } = useEvaluation();
  const useMockData = useAppStore((s) => s.useMockData);

  const isLoading = metrics.isLoading || history.isLoading;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-center gap-3">
        <Activity className="h-7 w-7 text-medical-teal" />
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold">Evaluation Dashboard</h1>
            <Badge variant="medical">Admin</Badge>
          </div>
          <p className="mt-1 text-muted-foreground">
            RAG evaluation metrics powered by RAGAS and DeepEval
          </p>
        </div>
      </div>

      {useMockData && <MockDataBanner />}

      {isLoading ? (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <ChartSkeleton key={i} height={120} />
            ))}
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <ChartSkeleton />
            <ChartSkeleton />
          </div>
        </div>
      ) : metrics.data ? (
        <>
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="Faithfulness" value={metrics.data.faithfulness} description="Answer grounded in context" />
            <MetricCard label="Context Precision" value={metrics.data.contextPrecision} description="Relevant retrieved chunks" />
            <MetricCard label="Context Recall" value={metrics.data.contextRecall} description="Coverage of needed info" />
            <MetricCard label="Answer Relevancy" value={metrics.data.answerRelevancy} description="Relevance to question" />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <MetricsRadar data={metrics.data} />
            {history.data && <MetricsHistoryChart data={history.data} />}
          </div>
        </>
      ) : null}
    </div>
  );
}
