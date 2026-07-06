"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft, Eye, FlaskConical, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ClaimCard, ClaimSummary } from "@/components/ClaimCard";
import { ConfidenceIndicator } from "@/components/ConfidenceIndicator";
import { HallucinationRiskBar } from "@/components/HallucinationBadge";
import { SourceCard } from "@/components/SourceCard";
import { ResultsSkeleton } from "@/components/StreamingAnswer";
import { MockDataBanner } from "@/components/MockDataBanner";
import { useResult } from "@/hooks/useResult";
import { useAppStore } from "@/lib/store";
import { formatDate } from "@/lib/utils";

export default function ResultsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data, isLoading, error } = useResult(id);
  const useMockData = useAppStore((s) => s.useMockData);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ResultsSkeleton />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <p className="text-muted-foreground">Failed to load results.</p>
        <Button variant="outline" className="mt-4" asChild>
          <Link href="/ask">Ask a new question</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {useMockData && <MockDataBanner />}

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
            <Link href="/ask">
              <ArrowLeft className="h-4 w-4" />
              Back to Ask
            </Link>
          </Button>
          <h1 className="text-2xl font-bold">Verified Answer</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Query ID: {data.id} · {formatDate(data.createdAt)}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link href={`/explain/${id}`}>
              <Eye className="h-4 w-4" />
              Explainability
            </Link>
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link href={`/research/${id}`}>
              <FlaskConical className="h-4 w-4" />
              Research Mode
            </Link>
          </Button>
        </div>
      </div>

      <Card className="mb-6 border-medical-teal/20">
        <CardHeader>
          <Badge variant="medical" className="w-fit">Question</Badge>
          <CardTitle className="text-lg font-medium">{data.question}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm leading-relaxed">{data.answer}</p>
        </CardContent>
      </Card>

      <div className="mb-8 grid gap-4 sm:grid-cols-2">
        <Card>
          <CardContent className="p-6">
            <ConfidenceIndicator confidence={data.overallConfidence} />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <HallucinationRiskBar risk={data.hallucinationRisk} />
          </CardContent>
        </Card>
      </div>

      <section className="mb-8">
        <h2 className="mb-4 text-xl font-semibold">Claim Verification</h2>
        <div className="mb-6">
          <ClaimSummary claims={data.claims} />
        </div>
        <div className="space-y-4">
          {data.claims.map((claim, i) => (
            <ClaimCard key={claim.id} claim={claim} index={i} />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold">Sources ({data.sources.length})</h2>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/sources">
              View all sources
              <ExternalLink className="h-3 w-3" />
            </Link>
          </Button>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          {data.sources.map((source) => (
            <SourceCard key={source.id} source={source} compact />
          ))}
        </div>
      </section>
    </div>
  );
}
