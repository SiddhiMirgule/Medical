"use client";

import { useState } from "react";
import { Settings, Save, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { ChartSkeleton } from "@/components/StreamingAnswer";
import { MockDataBanner } from "@/components/MockDataBanner";
import { useAdmin } from "@/hooks/useAdmin";
import { useAppStore } from "@/lib/store";
import type { AdminSettings } from "@/types";

export default function AdminPage() {
  const { settings, isLoading, updateSettings, isUpdating } = useAdmin();
  const useMockData = useAppStore((s) => s.useMockData);
  const [form, setForm] = useState<Partial<AdminSettings>>({});

  const current = { ...settings, ...form };

  const handleSave = () => {
    updateSettings(form);
    setForm({});
  };

  const updateField = <K extends keyof AdminSettings>(key: K, value: AdminSettings[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  if (isLoading) {
    return (
      <div className="container mx-auto max-w-3xl px-4 py-8">
        <ChartSkeleton height={400} />
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-3xl px-4 py-8">
      <div className="mb-8 flex items-center gap-3">
        <Settings className="h-7 w-7 text-medical-teal" />
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold">Admin Panel</h1>
            <Badge variant="medical">Admin</Badge>
          </div>
          <p className="mt-1 text-muted-foreground">
            Configure retrieval, verification, and scoring parameters
          </p>
        </div>
      </div>

      {useMockData && <MockDataBanner />}

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Retrieval Settings</CardTitle>
            <CardDescription>Configure hybrid retrieval and reranking parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="retrievalTopK">Retrieval Top-K</Label>
                <Input
                  id="retrievalTopK"
                  type="number"
                  value={current.retrievalTopK ?? 25}
                  onChange={(e) => updateField("retrievalTopK", parseInt(e.target.value))}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="rerankTopK">Rerank Top-K</Label>
                <Input
                  id="rerankTopK"
                  type="number"
                  value={current.rerankTopK ?? 5}
                  onChange={(e) => updateField("rerankTopK", parseInt(e.target.value))}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Verification Settings</CardTitle>
            <CardDescription>Hallucination detection and confidence scoring</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="hallucinationThreshold">Hallucination Threshold</Label>
              <Input
                id="hallucinationThreshold"
                type="number"
                step="0.05"
                min="0"
                max="1"
                value={current.hallucinationThreshold ?? 0.3}
                onChange={(e) => updateField("hallucinationThreshold", parseFloat(e.target.value))}
              />
              <p className="text-xs text-muted-foreground">
                Claims above this threshold are flagged as potential hallucinations
              </p>
            </div>
            <div className="space-y-2">
              <Label htmlFor="confidenceFormula">Confidence Formula</Label>
              <Input
                id="confidenceFormula"
                value={current.confidenceFormula ?? ""}
                onChange={(e) => updateField("confidenceFormula", e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Model Settings</CardTitle>
            <CardDescription>Default LLM and streaming configuration</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Default Model</Label>
              <Select
                value={current.defaultModel ?? "gpt-4o"}
                onValueChange={(v) => updateField("defaultModel", v)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                  <SelectItem value="claude-sonnet">Claude Sonnet</SelectItem>
                  <SelectItem value="llama-3.1">Llama 3.1 70B</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Enable Streaming</Label>
                <p className="text-xs text-muted-foreground">Stream answers token-by-token</p>
              </div>
              <Button
                variant={current.enableStreaming ? "medical" : "outline"}
                size="sm"
                onClick={() => updateField("enableStreaming", !current.enableStreaming)}
              >
                {current.enableStreaming ? "Enabled" : "Disabled"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Separator />

        <div className="flex justify-end">
          <Button
            variant="medical"
            onClick={handleSave}
            disabled={isUpdating || Object.keys(form).length === 0}
          >
            {isUpdating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
