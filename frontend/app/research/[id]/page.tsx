"use client";

import { use } from "react";
import Link from "next/link";
import { ArrowLeft, Database, Layers, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ResultsSkeleton } from "@/components/StreamingAnswer";
import { MockDataBanner } from "@/components/MockDataBanner";
import { ConfidenceIndicator } from "@/components/ConfidenceIndicator";
import { useResearch } from "@/hooks/useResearch";
import { useAppStore } from "@/lib/store";
import { formatPercent } from "@/lib/utils";

export default function ResearchPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data, isLoading } = useResearch(id);
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
          <Database className="h-6 w-6 text-medical-teal" />
          <div>
            <h1 className="text-2xl font-bold">Research Mode</h1>
            <p className="text-sm text-muted-foreground">{data.question}</p>
          </div>
        </div>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-medical-teal">{data.totalRetrieved}</p>
            <p className="text-xs text-muted-foreground">Retrieved</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-medical-teal">{data.totalAfterRerank}</p>
            <p className="text-xs text-muted-foreground">After Rerank</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-sm font-medium">{data.embeddingModel}</p>
            <p className="text-xs text-muted-foreground">Embedding Model</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-sm font-medium">{data.retrievalMethod}</p>
            <p className="text-xs text-muted-foreground">Retrieval Method</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="reranked" className="space-y-6">
        <TabsList>
          <TabsTrigger value="reranked">
            <Zap className="mr-1 h-4 w-4" />
            Reranked Chunks
          </TabsTrigger>
          <TabsTrigger value="retrieved">
            <Layers className="mr-1 h-4 w-4" />
            All Retrieved
          </TabsTrigger>
        </TabsList>

        <TabsContent value="reranked" className="space-y-4">
          {data.rerankedChunks.map((chunk, i) => (
            <ChunkCard key={chunk.id} chunk={chunk} rank={i + 1} />
          ))}
        </TabsContent>

        <TabsContent value="retrieved" className="space-y-4">
          {data.retrievedChunks.map((chunk, i) => (
            <ChunkCard key={chunk.id} chunk={chunk} rank={i + 1} showRerank={false} />
          ))}
        </TabsContent>
      </Tabs>
    </div>
  );
}

function ChunkCard({
  chunk,
  rank,
  showRerank = true,
}: {
  chunk: {
    id: string;
    text: string;
    similarityScore: number;
    rerankScore: number;
    sourceTitle: string;
  };
  rank: number;
  showRerank?: boolean;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-2">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-medical-teal/20 text-xs font-bold text-medical-teal">
              {rank}
            </span>
            <div>
              <CardTitle className="text-sm font-medium leading-snug">{chunk.sourceTitle}</CardTitle>
              <div className="mt-1 flex flex-wrap gap-2">
                <Badge variant="outline">Similarity: {formatPercent(chunk.similarityScore)}</Badge>
                {showRerank && (
                  <Badge variant="medical">Rerank: {formatPercent(chunk.rerankScore)}</Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">{chunk.text}</p>
        <ConfidenceIndicator
          confidence={showRerank ? chunk.rerankScore : chunk.similarityScore}
          size="sm"
        />
      </CardContent>
    </Card>
  );
}
