"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { useEffect } from "react";

export function useBenchmark() {
  const setUseMockData = useAppStore((s) => s.setUseMockData);

  const query = useQuery({
    queryKey: ["benchmark"],
    queryFn: () => api.getBenchmark(),
  });

  useEffect(() => {
    if (query.isError) setUseMockData(true);
  }, [query.isError, setUseMockData]);

  return query;
}
