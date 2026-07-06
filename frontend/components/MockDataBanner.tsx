"use client";

import { Badge } from "@/components/ui/badge";
import { Info } from "lucide-react";

export function MockDataBanner() {
  return (
    <div className="mb-6 flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-400">
      <Info className="h-4 w-4 shrink-0" />
      <span>
        API unavailable — displaying mock data. Start the backend at{" "}
        <code className="rounded bg-muted px-1.5 py-0.5 text-xs">localhost:8000</code> for live data.
      </span>
      <Badge variant="warning" className="ml-auto shrink-0">
        Mock Mode
      </Badge>
    </div>
  );
}
