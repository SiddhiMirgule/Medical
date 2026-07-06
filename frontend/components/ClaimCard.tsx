import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ConfidenceIndicator } from "@/components/ConfidenceIndicator";
import { HallucinationBadge } from "@/components/HallucinationBadge";
import type { Claim } from "@/types";
import { cn, getStatusColor, formatPercent } from "@/lib/utils";
import { Quote } from "lucide-react";

interface ClaimCardProps {
  claim: Claim;
  index?: number;
  showEvidence?: boolean;
  className?: string;
}

const statusLabels: Record<Claim["status"], string> = {
  supported: "Supported",
  partially_supported: "Partially Supported",
  unsupported: "Unsupported",
  contradicted: "Contradicted",
};

export function ClaimCard({ claim, index, showEvidence = true, className }: ClaimCardProps) {
  return (
    <Card className={cn("border-l-4", className)} style={{ borderLeftColor: getBorderColor(claim.status) }}>
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="flex items-start gap-2">
            {index !== undefined && (
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium">
                {index + 1}
              </span>
            )}
            <p className="text-sm font-medium leading-relaxed">{claim.claim}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Badge className={cn("border", getStatusColor(claim.status))}>
              {statusLabels[claim.status]}
            </Badge>
            <HallucinationBadge risk={claim.hallucinationRisk} />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <ConfidenceIndicator confidence={claim.confidence} size="sm" />
        {showEvidence && claim.evidence.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Supporting Evidence</p>
            {claim.evidence.map((ev, i) => (
              <div key={i} className="rounded-lg bg-muted/50 p-3 text-sm">
                <div className="mb-1 flex items-center gap-1 text-xs text-medical-teal">
                  <Quote className="h-3 w-3" />
                  {ev.source}
                </div>
                <p className="text-muted-foreground italic">&ldquo;{ev.excerpt}&rdquo;</p>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function getBorderColor(status: Claim["status"]): string {
  switch (status) {
    case "supported":
      return "#34d399";
    case "partially_supported":
      return "#fbbf24";
    case "unsupported":
      return "#f87171";
    case "contradicted":
      return "#ef4444";
    default:
      return "#6b7280";
  }
}

export function ClaimSummary({ claims }: { claims: Claim[] }) {
  const supported = claims.filter((c) => c.status === "supported").length;
  const partial = claims.filter((c) => c.status === "partially_supported").length;
  const issues = claims.filter((c) => c.status === "unsupported" || c.status === "contradicted").length;
  const avgConfidence = claims.reduce((sum, c) => sum + c.confidence, 0) / claims.length;

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <SummaryStat label="Total Claims" value={claims.length.toString()} />
      <SummaryStat label="Supported" value={supported.toString()} color="text-emerald-400" />
      <SummaryStat label="Partial" value={partial.toString()} color="text-amber-400" />
      <SummaryStat label="Avg Confidence" value={formatPercent(avgConfidence)} color="text-medical-teal" />
      {issues > 0 && <SummaryStat label="Issues" value={issues.toString()} color="text-red-400" />}
    </div>
  );
}

function SummaryStat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="rounded-lg bg-muted/50 p-3 text-center">
      <p className={cn("text-2xl font-bold", color)}>{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  );
}
