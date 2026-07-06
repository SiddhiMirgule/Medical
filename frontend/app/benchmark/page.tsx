"use client";

import { BarChart3, Clock, DollarSign, Trophy } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartSkeleton } from "@/components/StreamingAnswer";
import { MockDataBanner } from "@/components/MockDataBanner";
import { BenchmarkChart } from "@/components/charts/MetricsCharts";
import { useBenchmark } from "@/hooks/useBenchmark";
import { useAppStore } from "@/lib/store";
import { formatPercent } from "@/lib/utils";
import { cn } from "@/lib/utils";

export default function BenchmarkPage() {
  const { data, isLoading } = useBenchmark();
  const useMockData = useAppStore((s) => s.useMockData);

  const sortedModels = data?.models
    ? [...data.models].sort((a, b) => b.accuracy - a.accuracy)
    : [];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-center gap-3">
        <BarChart3 className="h-7 w-7 text-medical-teal" />
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold">Benchmark Dashboard</h1>
            <Badge variant="medical">Admin</Badge>
          </div>
          <p className="mt-1 text-muted-foreground">
            Compare LLM performance on medical QA tasks
          </p>
        </div>
      </div>

      {useMockData && <MockDataBanner />}

      {isLoading ? (
        <div className="space-y-6">
          <ChartSkeleton height={200} />
          <ChartSkeleton />
        </div>
      ) : data ? (
        <>
          <div className="mb-6 flex flex-wrap gap-4 text-sm text-muted-foreground">
            <span>{data.totalQueries.toLocaleString()} total queries evaluated</span>
            <span>·</span>
            <span>Last updated: {new Date(data.lastUpdated).toLocaleDateString()}</span>
          </div>

          {/* Leaderboard */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Trophy className="h-5 w-5 text-amber-400" />
                Leaderboard
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-muted-foreground">
                      <th className="pb-3 pr-4">Rank</th>
                      <th className="pb-3 pr-4">Model</th>
                      <th className="pb-3 pr-4">Accuracy</th>
                      <th className="pb-3 pr-4">Faithfulness</th>
                      <th className="pb-3 pr-4">Hallucination</th>
                      <th className="pb-3 pr-4">Latency</th>
                      <th className="pb-3">Cost/Query</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedModels.map((model, i) => (
                      <tr key={model.id} className="border-b border-border/50">
                        <td className="py-3 pr-4">
                          <span
                            className={cn(
                              "flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold",
                              i === 0
                                ? "bg-amber-500/20 text-amber-400"
                                : "bg-muted text-muted-foreground"
                            )}
                          >
                            {i + 1}
                          </span>
                        </td>
                        <td className="py-3 pr-4 font-medium">
                          {model.name}
                          {model.id === "medverify" && (
                            <Badge variant="medical" className="ml-2">Ours</Badge>
                          )}
                        </td>
                        <td className="py-3 pr-4 text-medical-teal">{formatPercent(model.accuracy)}</td>
                        <td className="py-3 pr-4">{formatPercent(model.faithfulness)}</td>
                        <td className="py-3 pr-4 text-red-400">{formatPercent(model.hallucinationRate)}</td>
                        <td className="py-3 pr-4">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {(model.latencyMs / 1000).toFixed(1)}s
                          </span>
                        </td>
                        <td className="py-3">
                          <span className="flex items-center gap-1">
                            <DollarSign className="h-3 w-3" />
                            ${model.costPerQuery.toFixed(3)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <BenchmarkChart models={data.models} />
        </>
      ) : null}
    </div>
  );
}
