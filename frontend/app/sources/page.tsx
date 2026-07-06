"use client";

import { useState } from "react";
import { Search, Filter } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SourceCard } from "@/components/SourceCard";
import { SourceCardSkeleton } from "@/components/StreamingAnswer";
import { MockDataBanner } from "@/components/MockDataBanner";
import { useSources } from "@/hooks/useSources";
import { useAppStore } from "@/lib/store";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";

export default function SourcesPage() {
  const [search, setSearch] = useState("");
  const [sourceType, setSourceType] = useState("all");
  const debouncedSearch = useDebouncedValue(search, 300);
  const useMockData = useAppStore((s) => s.useMockData);

  const { data: sources, isLoading } = useSources({
    search: debouncedSearch || undefined,
    sourceType: sourceType !== "all" ? sourceType : undefined,
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Source Explorer</h1>
        <p className="mt-2 text-muted-foreground">
          Browse and search trusted medical literature from PubMed, NIH, WHO, and clinical guidelines
        </p>
      </div>

      {useMockData && <MockDataBanner />}

      <div className="mb-6 flex flex-col gap-4 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by title, abstract, or PMID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={sourceType} onValueChange={setSourceType}>
          <SelectTrigger className="w-full sm:w-[200px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Source type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sources</SelectItem>
            <SelectItem value="pubmed">PubMed</SelectItem>
            <SelectItem value="nih">NIH</SelectItem>
            <SelectItem value="who">WHO</SelectItem>
            <SelectItem value="guideline">Guidelines</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <SourceCardSkeleton key={i} />
          ))}
        </div>
      ) : sources && sources.length > 0 ? (
        <>
          <p className="mb-4 text-sm text-muted-foreground">
            {sources.length} source{sources.length !== 1 ? "s" : ""} found
          </p>
          <div className="grid gap-4 lg:grid-cols-2">
            {sources.map((source) => (
              <SourceCard key={source.id} source={source} />
            ))}
          </div>
        </>
      ) : (
        <div className="py-12 text-center text-muted-foreground">
          No sources found matching your criteria.
        </div>
      )}
    </div>
  );
}
