"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { BenchmarkModel, MetricsHistory } from "@/types";
import { formatPercent } from "@/lib/utils";

interface MetricsRadarProps {
  data: {
    faithfulness: number;
    contextPrecision: number;
    contextRecall: number;
    answerRelevancy: number;
  };
}

export function MetricsRadar({ data }: MetricsRadarProps) {
  const chartData = [
    { metric: "Faithfulness", value: data.faithfulness * 100 },
    { metric: "Precision", value: data.contextPrecision * 100 },
    { metric: "Recall", value: data.contextRecall * 100 },
    { metric: "Relevancy", value: data.answerRelevancy * 100 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">RAG Evaluation Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={chartData}>
            <PolarGrid stroke="hsl(var(--border))" />
            <PolarAngleAxis dataKey="metric" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }} />
            <Radar
              name="Score"
              dataKey="value"
              stroke="#14b8a6"
              fill="#14b8a6"
              fillOpacity={0.3}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, "Score"]}
            />
          </RadarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

interface MetricsHistoryChartProps {
  data: MetricsHistory[];
}

export function MetricsHistoryChart({ data }: MetricsHistoryChartProps) {
  const chartData = data.map((d) => ({
    date: d.date,
    Faithfulness: +(d.faithfulness * 100).toFixed(1),
    Precision: +(d.contextPrecision * 100).toFixed(1),
    Recall: +(d.contextRecall * 100).toFixed(1),
    Relevancy: +(d.answerRelevancy * 100).toFixed(1),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Metrics Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="date" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
            <YAxis domain={[60, 100]} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
            />
            <Legend />
            <Line type="monotone" dataKey="Faithfulness" stroke="#0ea5e9" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="Precision" stroke="#14b8a6" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="Recall" stroke="#06b6d4" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="Relevancy" stroke="#8b5cf6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

interface BenchmarkChartProps {
  models: BenchmarkModel[];
}

export function BenchmarkChart({ models }: BenchmarkChartProps) {
  const chartData = models.map((m) => ({
    name: m.name,
    Accuracy: +(m.accuracy * 100).toFixed(1),
    Faithfulness: +(m.faithfulness * 100).toFixed(1),
    "Low Hallucination": +((1 - m.hallucinationRate) * 100).toFixed(1),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Model Comparison</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={chartData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis type="number" domain={[0, 100]} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
            <YAxis type="category" dataKey="name" width={100} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
            />
            <Legend />
            <Bar dataKey="Accuracy" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
            <Bar dataKey="Faithfulness" fill="#14b8a6" radius={[0, 4, 4, 0]} />
            <Bar dataKey="Low Hallucination" fill="#06b6d4" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

interface MetricCardProps {
  label: string;
  value: number;
  description?: string;
}

export function MetricCard({ label, value, description }: MetricCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <p className="text-sm text-muted-foreground">{label}</p>
        <p className="mt-1 text-3xl font-bold text-medical-teal">{formatPercent(value)}</p>
        {description && <p className="mt-1 text-xs text-muted-foreground">{description}</p>}
      </CardContent>
    </Card>
  );
}
