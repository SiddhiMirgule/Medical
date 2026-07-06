import Link from "next/link";
import { ExternalLink, BookOpen, Users, Calendar } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ConfidenceIndicator } from "@/components/ConfidenceIndicator";
import type { Source } from "@/types";
import { formatDate, cn } from "@/lib/utils";

interface SourceCardProps {
  source: Source;
  compact?: boolean;
  className?: string;
}

const sourceTypeLabels: Record<Source["sourceType"], string> = {
  pubmed: "PubMed",
  nih: "NIH",
  who: "WHO",
  guideline: "Guideline",
  other: "Other",
};

export function SourceCard({ source, compact = false, className }: SourceCardProps) {
  return (
    <Card className={cn("transition-colors hover:border-medical-teal/40", className)}>
      <CardHeader className={compact ? "p-4 pb-2" : undefined}>
        <div className="flex items-start justify-between gap-3">
          <CardTitle className={cn("text-base leading-snug", compact && "text-sm")}>
            {source.title}
          </CardTitle>
          <Badge variant="medical" className="shrink-0">
            {sourceTypeLabels[source.sourceType]}
          </Badge>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Users className="h-3 w-3" />
            {source.authors.slice(0, 2).join(", ")}
            {source.authors.length > 2 && " et al."}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {formatDate(source.publicationDate)}
          </span>
          <span className="flex items-center gap-1">
            <BookOpen className="h-3 w-3" />
            PMID: {source.pmid}
          </span>
        </div>
      </CardHeader>
      <CardContent className={compact ? "p-4 pt-0" : undefined}>
        {!compact && (
          <p className="mb-4 line-clamp-3 text-sm text-muted-foreground">{source.abstract}</p>
        )}
        <div className="flex items-center justify-between gap-4">
          {source.relevanceScore !== undefined && (
            <ConfidenceIndicator
              confidence={source.relevanceScore}
              size="sm"
              className="flex-1 max-w-[200px]"
            />
          )}
          <Link
            href={source.sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-medical-teal hover:underline"
          >
            View Source
            <ExternalLink className="h-3 w-3" />
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
