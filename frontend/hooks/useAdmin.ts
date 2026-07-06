"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { useEffect } from "react";
import type { AdminSettings } from "@/types";

export function useAdmin() {
  const queryClient = useQueryClient();
  const { adminSettings, setAdminSettings, setUseMockData } = useAppStore();

  const settingsQuery = useQuery({
    queryKey: ["admin-settings"],
    queryFn: () => api.getAdminSettings(),
  });

  useEffect(() => {
    if (settingsQuery.data) setAdminSettings(settingsQuery.data);
    if (settingsQuery.isError) setUseMockData(true);
  }, [settingsQuery.data, settingsQuery.isError, setAdminSettings, setUseMockData]);

  const updateMutation = useMutation({
    mutationFn: (settings: Partial<AdminSettings>) => api.updateAdminSettings(settings),
    onSuccess: (data) => {
      setAdminSettings(data);
      queryClient.setQueryData(["admin-settings"], data);
    },
  });

  return {
    settings: adminSettings || settingsQuery.data,
    isLoading: settingsQuery.isLoading,
    updateSettings: updateMutation.mutate,
    isUpdating: updateMutation.isPending,
  };
}
