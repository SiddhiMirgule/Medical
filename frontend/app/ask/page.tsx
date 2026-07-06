"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Send, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StreamingAnswer } from "@/components/StreamingAnswer";
import { useAsk } from "@/hooks/useAsk";
import { useAppStore } from "@/lib/store";
import { cn } from "@/lib/utils";

const exampleQuestions = [
  "What are the side effects of Metformin?",
  "What is the recommended first-line treatment for type 2 diabetes?",
  "How does aspirin affect cardiovascular risk?",
  "What are the contraindications for warfarin?",
];

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const router = useRouter();
  const { askWithStream, isLoading } = useAsk();
  const { isStreaming, streamedAnswer, recentQueries } = useAppStore();

  const handleSubmit = async (e?: React.FormEvent, q?: string) => {
    e?.preventDefault();
    const query = q || question.trim();
    if (!query || isLoading || isStreaming) return;

    const result = await askWithStream(query);
    if (result?.id) {
      router.push(`/results/${result.id}`);
    }
  };

  return (
    <div className="container mx-auto max-w-3xl px-4 py-8 sm:py-12">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold">Ask a Medical Question</h1>
        <p className="mt-2 text-muted-foreground">
          Get evidence-backed answers with claim verification and hallucination detection
        </p>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="h-5 w-5 text-medical-teal" />
            Your Question
          </CardTitle>
          <CardDescription>
            Ask about medications, treatments, conditions, or clinical guidelines
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g., What are the side effects of Metformin?"
              rows={4}
              className="w-full resize-none rounded-md border border-input bg-background px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              disabled={isLoading || isStreaming}
            />
            <div className="flex justify-end">
              <Button
                type="submit"
                variant="medical"
                disabled={!question.trim() || isLoading || isStreaming}
              >
                {isLoading || isStreaming ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Ask MedVerify
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {(isStreaming || streamedAnswer) && (
        <div className="mb-8">
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">Generating answer...</h2>
          <StreamingAnswer content={streamedAnswer} isStreaming={isStreaming} />
        </div>
      )}

      <div className="mb-8">
        <h2 className="mb-3 text-sm font-medium text-muted-foreground">Example Questions</h2>
        <div className="grid gap-2 sm:grid-cols-2">
          {exampleQuestions.map((q) => (
            <button
              key={q}
              onClick={() => {
                setQuestion(q);
                handleSubmit(undefined, q);
              }}
              disabled={isLoading || isStreaming}
              className={cn(
                "rounded-lg border border-border bg-card p-3 text-left text-sm transition-colors",
                "hover:border-medical-teal/40 hover:bg-accent disabled:opacity-50"
              )}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {recentQueries.length > 0 && (
        <div>
          <h2 className="mb-3 text-sm font-medium text-muted-foreground">Recent Queries</h2>
          <div className="space-y-2">
            {recentQueries.map((q) => (
              <button
                key={q.id}
                onClick={() => router.push(`/results/${q.id}`)}
                className="w-full rounded-lg border border-border bg-card p-3 text-left text-sm transition-colors hover:border-medical-teal/40 hover:bg-accent"
              >
                <p className="line-clamp-1 font-medium">{q.question}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {new Date(q.createdAt).toLocaleString()}
                </p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
