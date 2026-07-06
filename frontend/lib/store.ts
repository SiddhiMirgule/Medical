import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AskResponse, AdminSettings } from "@/types";

interface AppState {
  currentQuery: string;
  setCurrentQuery: (query: string) => void;

  currentResult: AskResponse | null;
  setCurrentResult: (result: AskResponse | null) => void;

  isStreaming: boolean;
  setIsStreaming: (streaming: boolean) => void;

  streamedAnswer: string;
  setStreamedAnswer: (answer: string) => void;
  appendStreamedAnswer: (token: string) => void;
  resetStreamedAnswer: () => void;

  recentQueries: { id: string; question: string; createdAt: string }[];
  addRecentQuery: (query: { id: string; question: string; createdAt: string }) => void;

  adminSettings: AdminSettings | null;
  setAdminSettings: (settings: AdminSettings) => void;

  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;

  useMockData: boolean;
  setUseMockData: (useMock: boolean) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      currentQuery: "",
      setCurrentQuery: (query) => set({ currentQuery: query }),

      currentResult: null,
      setCurrentResult: (result) => set({ currentResult: result }),

      isStreaming: false,
      setIsStreaming: (streaming) => set({ isStreaming: streaming }),

      streamedAnswer: "",
      setStreamedAnswer: (answer) => set({ streamedAnswer: answer }),
      appendStreamedAnswer: (token) =>
        set((state) => ({ streamedAnswer: state.streamedAnswer + token })),
      resetStreamedAnswer: () => set({ streamedAnswer: "" }),

      recentQueries: [],
      addRecentQuery: (query) =>
        set((state) => ({
          recentQueries: [query, ...state.recentQueries.filter((q) => q.id !== query.id)].slice(0, 10),
        })),

      adminSettings: null,
      setAdminSettings: (settings) => set({ adminSettings: settings }),

      sidebarOpen: false,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

      useMockData: false,
      setUseMockData: (useMock) => set({ useMockData: useMock }),
    }),
    {
      name: "medverify-store",
      partialize: (state) => ({
        recentQueries: state.recentQueries,
        adminSettings: state.adminSettings,
      }),
    }
  )
);
