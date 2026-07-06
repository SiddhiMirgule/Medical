"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { useEffect } from "react";

interface UseSourcesParams {
  search?: string;
  sourceType?: string;
  limit?: number;
}

export function useSources(params?: UseSourcesParams) {
  const setUseMockData = useAppStore((s) => s.setUseMockData);

  const query = useQuery({
    queryKey: ["sources", params],
    queryFn: () => api.getSources(params),
  });

  useEffect(() => {
    if (query.isError) setUseMockData(true);
  }, [query.isError, setUseMockData]);

  return query;
}
