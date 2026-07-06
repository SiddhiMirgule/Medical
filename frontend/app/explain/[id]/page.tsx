"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft, Network, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { ClaimCard, ClaimSummary } from "@/components/ClaimCard";
import { ConfidenceIndicator } from "@/components/ConfidenceIndicator";
import { HallucinationRiskBar } from "@/components/HallucinationBadge";
import { SourceCard } from "@/components/SourceCard";
import { ResultsSkeleton } from "@/components/StreamingAnswer";
import { MockDataBanner } from "@/components/MockDataBanner";
import { useResult } from "@/hooks/useResult";
import { useAppStore } from "@/lib/store";
import { formatPercent } from "@/lib/utils";

export default function ExplainPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data, isLoading } = useResult(id);
  const useMockData = useAppStore((s) => s.useMockData);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <ResultsSkeleton />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="container mx-auto px-4 py-8">
      {useMockData && <MockDataBanner />}

      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
          <Link href={`/results/${id}`}>
            <ArrowLeft className="h-4 w-4" />
            Back to Results
          </Link>
        </Button>
        <div className="flex items-center gap-3">
          <Network className="h-6 w-6 text-medical-teal" />
          <div>
            <h1 className="text-2xl font-bold">Explainability Dashboard</h1>
            <p className="text-sm text-muted-foreground">
              Transparent reasoning for: {data.question}
            </p>
          </div>
        </div>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="p-6 text-center">
            <p className="text-3xl font-bold text-medical-teal">{data.claims.length}</p>
            <p className="text-sm text-muted-foreground">Claims Extracted</p>
          </CardContent>
        </Card>
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

      <Tabs defaultValue="claims" className="space-y-6">
        <TabsList>
          <TabsTrigger value="claims">Claim Analysis</TabsTrigger>
          <TabsTrigger value="evidence">Evidence Chain</TabsTrigger>
          <TabsTrigger value="scoring">Confidence Scoring</TabsTrigger>
        </TabsList>

        <TabsContent value="claims" className="space-y-4">
          <ClaimSummary claims={data.claims} />
          {data.claims.map((claim, i) => (
            <ClaimCard key={claim.id} claim={claim} index={i} showEvidence />
          ))}
        </TabsContent>

        <TabsContent value="evidence" className="space-y-4">
          {data.claims.map((claim) => (
            <Card key={claim.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-sm font-medium">{claim.claim}</CardTitle>
                  <Badge variant="medical">{formatPercent(claim.confidence)}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                {claim.evidence.map((ev, i) => (
                  <div key={i} className="flex gap-3 rounded-lg border border-border p-3">
                    <FileText className="mt-0.5 h-4 w-4 shrink-0 text-medical-teal" />
                    <div>
                      <p className="text-xs font-medium text-medical-teal">{ev.source}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{ev.excerpt}</p>
                    </div>
                  </div>
                ))}
                {claim.evidence.length === 0 && (
                  <p className="text-sm text-muted-foreground">No evidence found for this claim.</p>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="scoring">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Confidence Scoring Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {data.claims.map((claim) => (
                <div key={claim.id} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="line-clamp-1 flex-1 pr-4">{claim.claim}</span>
                    <span className="font-medium text-medical-teal">
                      {formatPercent(claim.confidence)}
                    </span>
                  </div>
                  <ConfidenceIndicator confidence={claim.confidence} showLabel={false} size="sm" />
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <section className="mt-8">
        <h2 className="mb-4 text-xl font-semibold">Source Documents</h2>
        <div className="grid gap-4 lg:grid-cols-2">
          {data.sources.map((source) => (
            <SourceCard key={source.id} source={source} />
          ))}
        </div>
      </section>
    </div>
  );
}
