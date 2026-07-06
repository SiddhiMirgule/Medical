"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { useEffect } from "react";

export function useEvaluation() {
  const setUseMockData = useAppStore((s) => s.setUseMockData);

  const metrics = useQuery({
    queryKey: ["evaluation"],
    queryFn: () => api.getEvaluation(),
  });

  const history = useQuery({
    queryKey: ["metrics-history"],
    queryFn: () => api.getMetricsHistory(),
  });

  useEffect(() => {
    if (metrics.isError || history.isError) setUseMockData(true);
  }, [metrics.isError, history.isError, setUseMockData]);

  return { metrics, history };
}
