import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, HelpCircle } from "lucide-react";
import type { HallucinationRisk } from "@/types";
import { cn } from "@/lib/utils";

interface HallucinationBadgeProps {
  risk: HallucinationRisk;
  className?: string;
}

const config: Record<
  HallucinationRisk,
  { label: string; variant: "success" | "warning" | "danger"; icon: typeof CheckCircle }
> = {
  verified: { label: "Verified", variant: "success", icon: CheckCircle },
  low_confidence: { label: "Low Confidence", variant: "warning", icon: HelpCircle },
  potential_hallucination: { label: "Potential Hallucination", variant: "danger", icon: AlertTriangle },
};

export function HallucinationBadge({ risk, className }: HallucinationBadgeProps) {
  const { label, variant, icon: Icon } = config[risk];

  return (
    <Badge variant={variant} className={cn("gap-1", className)}>
      <Icon className="h-3 w-3" />
      {label}
    </Badge>
  );
}

interface HallucinationRiskBarProps {
  risk: number;
  className?: string;
}

export function HallucinationRiskBar({ risk, className }: HallucinationRiskBarProps) {
  const percent = risk * 100;
  const color = risk <= 0.1 ? "text-emerald-400" : risk <= 0.25 ? "text-amber-400" : "text-red-400";

  return (
    <div className={cn("space-y-1", className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Hallucination Risk</span>
        <span className={cn("font-medium", color)}>{percent.toFixed(0)}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className={cn(
            "h-full rounded-full transition-all",
            risk <= 0.1 ? "bg-emerald-500" : risk <= 0.25 ? "bg-amber-500" : "bg-red-500"
          )}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
