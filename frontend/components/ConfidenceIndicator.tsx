"use client";

import { cn, formatPercent } from "@/lib/utils";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface ConfidenceIndicatorProps {
  confidence: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
  className?: string;
}

export function ConfidenceIndicator({
  confidence,
  size = "md",
  showLabel = true,
  className,
}: ConfidenceIndicatorProps) {
  const percent = confidence * 100;
  const color =
    confidence >= 0.8 ? "text-emerald-400" : confidence >= 0.6 ? "text-amber-400" : "text-red-400";

  const heights = { sm: "h-1.5", md: "h-2", lg: "h-3" };

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className={cn("space-y-1", className)}>
            {showLabel && (
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground">Confidence</span>
                <span className={cn("font-medium", color)}>{formatPercent(confidence)}</span>
              </div>
            )}
            <Progress value={percent} className={heights[size]} />
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>Confidence score: {formatPercent(confidence, 1)}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
