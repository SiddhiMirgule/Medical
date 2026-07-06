"use client";

import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import type { AskResponse } from "@/types";
import { useCallback } from "react";

export function useAsk() {
  const {
    setCurrentResult,
    setIsStreaming,
    resetStreamedAnswer,
    appendStreamedAnswer,
    addRecentQuery,
    setUseMockData,
  } = useAppStore();

  const mutation = useMutation({
    mutationFn: (question: string) => api.ask(question),
    onSuccess: (data) => {
      setCurrentResult(data);
      addRecentQuery({
        id: data.id,
        question: data.question,
        createdAt: data.createdAt,
      });
    },
  });

  const askWithStream = useCallback(
    async (question: string): Promise<AskResponse | null> => {
      setIsStreaming(true);
      resetStreamedAnswer();
      let result: AskResponse | null = null;

      try {
        for await (const chunk of api.askStream(question)) {
          if (chunk.type === "token" && chunk.content) {
            appendStreamedAnswer(chunk.content);
          } else if (chunk.type === "done" && chunk.data) {
            result = chunk.data as AskResponse;
            setCurrentResult(result);
            addRecentQuery({
              id: result.id,
              question: result.question,
              createdAt: result.createdAt,
            });
          } else if (chunk.type === "error") {
            throw new Error(chunk.content || "Stream error");
          }
        }
      } catch {
        setUseMockData(true);
        const data = await api.ask(question);
        setCurrentResult(data);
        addRecentQuery({
          id: data.id,
          question: data.question,
          createdAt: data.createdAt,
        });
        result = data;
      } finally {
        setIsStreaming(false);
      }

      return result;
    },
    [
      appendStreamedAnswer,
      addRecentQuery,
      resetStreamedAnswer,
      setCurrentResult,
      setIsStreaming,
      setUseMockData,
    ]
  );

  return {
    ask: mutation.mutate,
    askAsync: mutation.mutateAsync,
    askWithStream,
    isLoading: mutation.isPending,
    error: mutation.error,
    data: mutation.data,
  };
}
