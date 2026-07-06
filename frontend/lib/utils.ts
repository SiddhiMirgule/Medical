import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatPercent(value: number, decimals = 0): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.8) return "text-emerald-400";
  if (confidence >= 0.6) return "text-amber-400";
  return "text-red-400";
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "supported":
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    case "partially_supported":
      return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    case "unsupported":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    case "contradicted":
      return "bg-red-600/20 text-red-500 border-red-600/30";
    default:
      return "bg-muted text-muted-foreground";
  }
}
