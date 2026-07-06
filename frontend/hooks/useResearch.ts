"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { useEffect } from "react";

export function useResearch(id: string) {
  const setUseMockData = useAppStore((s) => s.setUseMockData);

  const query = useQuery({
    queryKey: ["research", id],
    queryFn: () => api.getResearch(id),
    enabled: !!id,
  });

  useEffect(() => {
    if (query.isError) setUseMockData(true);
  }, [query.isError, setUseMockData]);

  return query;
}
