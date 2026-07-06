import Link from "next/link";
import {
  Shield,
  Search,
  CheckCircle,
  Eye,
  BarChart3,
  ArrowRight,
  Sparkles,
  FileSearch,
  AlertTriangle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: Search,
    title: "Hybrid Retrieval",
    description: "BM25 + dense search over trusted medical literature from PubMed, NIH, and WHO.",
  },
  {
    icon: CheckCircle,
    title: "Claim Verification",
    description: "Every answer is decomposed into atomic claims and verified against retrieved evidence.",
  },
  {
    icon: AlertTriangle,
    title: "Hallucination Detection",
    description: "Real-time classification of verified, low-confidence, and potential hallucination claims.",
  },
  {
    icon: Eye,
    title: "Explainability",
    description: "Full transparency into reasoning, evidence chains, and confidence scoring.",
  },
  {
    icon: FileSearch,
    title: "Source Explorer",
    description: "Browse and search retrieved medical literature with rich metadata.",
  },
  {
    icon: BarChart3,
    title: "Evaluation & Benchmarks",
    description: "RAGAS metrics and multi-model comparison for research-grade evaluation.",
  },
];

const stats = [
  { value: "94%", label: "Verification Accuracy" },
  { value: "5%", label: "Hallucination Rate" },
  { value: "1.2M+", label: "Medical Sources" },
  { value: "<4s", label: "Avg Response Time" },
];

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border/40">
        <div className="absolute inset-0 bg-gradient-to-br from-medical-blue/5 via-transparent to-medical-teal/5" />
        <div className="absolute -top-40 right-0 h-80 w-80 rounded-full bg-medical-teal/10 blur-3xl" />
        <div className="absolute -bottom-40 left-0 h-80 w-80 rounded-full bg-medical-blue/10 blur-3xl" />

        <div className="container relative mx-auto px-4 py-20 sm:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-medical-teal/30 bg-medical-teal/10 px-4 py-1.5 text-sm text-medical-teal">
              <Sparkles className="h-4 w-4" />
              Evidence-Grounded Medical AI
            </div>
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
              Trustworthy Medical Answers,{" "}
              <span className="text-gradient">Verified by Evidence</span>
            </h1>
            <p className="mt-6 text-lg text-muted-foreground sm:text-xl">
              MedVerify AI answers healthcare questions using trusted medical literature,
              with claim-level verification, hallucination detection, and full explainability.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button variant="medical" size="lg" asChild>
                <Link href="/ask">
                  Ask a Medical Question
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </Button>
              <Button variant="outline" size="lg" asChild>
                <Link href="/sources">Explore Sources</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-b border-border/40 bg-muted/20">
        <div className="container mx-auto px-4 py-12">
          <div className="grid grid-cols-2 gap-6 sm:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-3xl font-bold text-medical-teal">{stat.value}</p>
                <p className="mt-1 text-sm text-muted-foreground">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold">Built for Medical AI Safety</h2>
          <p className="mt-3 text-muted-foreground">
            Research-grade pipeline for evidence-grounded generation and verification
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} className="group transition-colors hover:border-medical-teal/30">
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-medical-teal/10 text-medical-teal transition-colors group-hover:bg-medical-teal/20">
                  <feature.icon className="h-5 w-5" />
                </div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      {/* Workflow */}
      <section className="border-t border-border/40 bg-muted/10">
        <div className="container mx-auto px-4 py-20">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold">How It Works</h2>
            <p className="mt-3 text-muted-foreground">From question to verified answer in seconds</p>
          </div>
          <div className="mx-auto flex max-w-4xl flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            {["Question", "Retrieve", "Generate", "Verify", "Explain"].map((step, i) => (
              <div key={step} className="flex items-center gap-4 sm:flex-col sm:gap-2">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-medical-blue to-medical-teal text-sm font-bold text-white">
                  {i + 1}
                </div>
                <span className="text-sm font-medium">{step}</span>
                {i < 4 && (
                  <ArrowRight className="hidden h-4 w-4 text-muted-foreground sm:block sm:rotate-0" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-20">
        <Card className="glow-teal border-medical-teal/20 bg-gradient-to-br from-medical-blue/5 to-medical-teal/5">
          <CardContent className="flex flex-col items-center p-12 text-center">
            <Shield className="mb-4 h-12 w-12 text-medical-teal" />
            <h2 className="text-2xl font-bold sm:text-3xl">Ready to verify medical knowledge?</h2>
            <p className="mt-3 max-w-lg text-muted-foreground">
              Ask a question and get evidence-backed answers with full claim verification and explainability.
            </p>
            <Button variant="medical" size="lg" className="mt-8" asChild>
              <Link href="/ask">
                Get Started
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
