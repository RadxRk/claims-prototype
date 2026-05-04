"use client";

import { useState } from "react";
import { UploadCard } from "@/components/UploadCard";
import { ResultsPanel } from "@/components/ResultsPanel";
import { CriteriaPanel } from "@/components/CriteriaPanel";
import { streamSSE } from "@/lib/sse-client";
import type { Analysis, Trigger } from "@/lib/schema";

interface AnalyzeResponse {
  analysis: Analysis;
  triggers: Trigger[];
  meta: {
    file_id: string;
    model: string;
    original_bytes: number;
    processed_bytes: number;
    dimensions: { width: number; height: number };
    usage: unknown;
  };
}

type Status = "idle" | "analyzing" | "done" | "error";

export default function Home() {
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [phases, setPhases] = useState<string[]>([]);
  const [elapsedMs, setElapsedMs] = useState<number | null>(null);

  async function handleAnalyze(input: { file: File }) {
    setStatus("analyzing");
    setError(null);
    setResult(null);
    setPhases([]);
    setElapsedMs(null);
    const start = Date.now();

    try {
      const fd = new FormData();
      fd.append("file", input.file);
      const response = await fetch("/api/analyze", { method: "POST", body: fd });

      // 4xx responses still come back as JSON (validation errors).
      const responseContentType = response.headers.get("content-type") ?? "";
      if (!response.ok && !responseContentType.startsWith("text/event-stream")) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody?.error || `Request failed with status ${response.status}`);
      }

      let finalResult: AnalyzeResponse | null = null;
      let streamError: string | null = null;

      await streamSSE(response, (event, data) => {
        const payload = data as { message?: string; error?: string } & Partial<AnalyzeResponse>;
        if (event === "status" && payload.message) {
          setPhases((prev) => [...prev, payload.message!]);
        } else if (event === "complete" && payload.analysis && payload.meta) {
          finalResult = payload as AnalyzeResponse;
        } else if (event === "error" && payload.error) {
          streamError = payload.error;
        }
      });

      if (streamError) throw new Error(streamError);
      if (!finalResult) throw new Error("Stream ended without a complete event");

      setResult(finalResult);
      setElapsedMs(Date.now() - start);
      setStatus("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
      setStatus("error");
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-black">
      <header className="border-b border-black/5 bg-white/60 backdrop-blur dark:border-white/5 dark:bg-neutral-950/60">
        <div className="mx-auto max-w-6xl px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
                Insurance Claims Analyzer
              </h1>
              <p className="text-xs text-neutral-500">
                AI-powered damage assessment · Claude Sonnet 4.6 · Structured outputs with confidence indicators
              </p>
            </div>
            <span className="hidden rounded-full bg-neutral-100 px-3 py-1 font-mono text-[10px] uppercase tracking-wider text-neutral-600 sm:inline-block dark:bg-neutral-900 dark:text-neutral-400">
              Prototype
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
          {/* Left: upload */}
          <div className="space-y-4">
            <UploadCard
              onAnalyze={handleAnalyze}
              busy={status === "analyzing"}
              preview={preview}
              setPreview={setPreview}
            />
            {result?.meta && (
              <div className="rounded-xl border border-black/5 bg-white px-4 py-3 text-xs text-neutral-600 shadow-sm dark:border-white/5 dark:bg-neutral-950 dark:text-neutral-400">
                <div className="flex flex-wrap gap-x-4 gap-y-1">
                  <span>
                    Model: <code className="font-mono text-neutral-800 dark:text-neutral-200">{result.meta.model}</code>
                  </span>
                  <span>
                    {result.meta.dimensions.width} × {result.meta.dimensions.height}
                  </span>
                  {elapsedMs && <span>{(elapsedMs / 1000).toFixed(1)}s</span>}
                </div>
              </div>
            )}
            <CriteriaPanel />
          </div>

          {/* Right: results */}
          <div>
            {status === "idle" && <EmptyState />}
            {status === "analyzing" && <AnalyzingState phases={phases} />}
            {status === "error" && error && <ErrorState message={error} />}
            {status === "done" && result && <ResultsPanel analysis={result.analysis} triggers={result.triggers} />}
          </div>
        </div>
      </main>

      <footer className="mx-auto max-w-6xl px-6 pb-12 pt-8 text-center text-xs text-neutral-500">
        Powered by Anthropic Claude · Cost estimates are AI-generated and should be reviewed by a licensed adjuster.
      </footer>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex h-full min-h-96 flex-col items-center justify-center rounded-xl border border-dashed border-black/10 bg-white/40 p-8 text-center dark:border-white/10 dark:bg-neutral-950/40">
      <div className="text-5xl">🚗</div>
      <h2 className="mt-4 text-lg font-semibold text-neutral-700 dark:text-neutral-300">
        Upload a damaged vehicle photo to begin
      </h2>
      <p className="mt-2 max-w-sm text-sm text-neutral-500">
        We&apos;ll identify the vehicle, describe the damage, and estimate a repair cost range with confidence indicators.
      </p>
    </div>
  );
}

function AnalyzingState({ phases }: { phases: string[] }) {
  // Show all received phases. The latest is "in progress" (animated dot);
  // earlier ones are checkmarks.
  return (
    <div className="rounded-xl border border-black/10 bg-white p-6 shadow-sm dark:border-white/10 dark:bg-neutral-950">
      <div className="mb-5 flex items-center gap-3">
        <div className="h-3 w-3 animate-pulse rounded-full bg-blue-500" />
        <h2 className="text-base font-semibold text-neutral-800 dark:text-neutral-200">Analyzing…</h2>
        <span className="ml-auto text-xs text-neutral-500">
          {phases.length === 0 ? "Connecting…" : `${phases.length} step${phases.length === 1 ? "" : "s"}`}
        </span>
      </div>
      <ul className="space-y-2.5 text-sm">
        {phases.length === 0 && (
          <li className="text-neutral-500">Opening stream…</li>
        )}
        {phases.map((phase, i) => {
          const isLast = i === phases.length - 1;
          return (
            <li key={i} className="flex items-start gap-3">
              {isLast ? (
                <span className="mt-1 inline-flex h-3 w-3 flex-none items-center justify-center">
                  <span className="absolute h-3 w-3 animate-ping rounded-full bg-blue-400 opacity-60" />
                  <span className="relative h-2 w-2 rounded-full bg-blue-500" />
                </span>
              ) : (
                <span className="mt-0.5 inline-flex h-4 w-4 flex-none items-center justify-center rounded-full bg-emerald-500/20 text-[10px] font-bold text-emerald-700 dark:text-emerald-300">
                  ✓
                </span>
              )}
              <span className={isLast ? "text-neutral-800 dark:text-neutral-200" : "text-neutral-500 line-through decoration-neutral-300 dark:decoration-neutral-700"}>
                {phase}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-rose-500/30 bg-rose-50 p-6 dark:bg-rose-950/20">
      <div className="flex items-start gap-3">
        <div className="text-2xl">❌</div>
        <div>
          <h2 className="text-base font-semibold text-rose-900 dark:text-rose-200">Analysis failed</h2>
          <p className="mt-2 text-sm text-rose-800 dark:text-rose-300">{message}</p>
          <p className="mt-3 text-xs text-rose-700/70 dark:text-rose-400/70">
            Common causes: missing/invalid <code className="font-mono">ANTHROPIC_API_KEY</code>, unreachable image URL,
            or unsupported file format.
          </p>
        </div>
      </div>
    </div>
  );
}
