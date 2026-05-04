"use client";

import { useRef, useState } from "react";

interface UploadCardProps {
  onAnalyze: (input: { file: File }) => void;
  busy: boolean;
  preview: string | null;
  setPreview: (url: string | null) => void;
}

const SAMPLE_IMAGES = [
  { label: "Rear bumper", url: "/samples/rear-bumper.jpg" },
  { label: "Front collision", url: "/samples/front-collision.png" },
  { label: "Side panel scrape", url: "/samples/side-panel.jpg" },
];

export function UploadCard({ onAnalyze, busy, preview, setPreview }: UploadCardProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    if (file) {
      setPreview(URL.createObjectURL(file));
    } else {
      setPreview(null);
    }
  };

  const handleFileSubmit = () => {
    if (!selectedFile) return;
    onAnalyze({ file: selectedFile });
  };

  const handleSampleClick = async (url: string) => {
    setPreview(url);
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Failed to load sample (${res.status})`);
      const blob = await res.blob();
      const filename = url.split("/").pop() || "sample.jpg";
      const file = new File([blob], filename, { type: blob.type || "image/jpeg" });
      onAnalyze({ file });
    } catch (err) {
      console.error("Failed to load sample:", err);
    }
  };

  return (
    <div className="rounded-xl border border-black/10 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-neutral-950">
      <div className="space-y-3">
        <label
          htmlFor="file-upload"
          className="block cursor-pointer rounded-lg border-2 border-dashed border-neutral-300 p-8 text-center transition hover:border-neutral-400 dark:border-neutral-700 dark:hover:border-neutral-600"
        >
          <input
            ref={fileInputRef}
            id="file-upload"
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
            disabled={busy}
          />
          {selectedFile ? (
            <div className="space-y-1">
              <div className="text-sm font-medium text-neutral-900 dark:text-neutral-100">{selectedFile.name}</div>
              <div className="text-xs text-neutral-500">
                {(selectedFile.size / 1024).toFixed(0)} KB · click to change
              </div>
            </div>
          ) : (
            <div className="space-y-1">
              <div className="text-3xl">📷</div>
              <div className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Click to choose a photo</div>
              <div className="text-xs text-neutral-500">JPEG, PNG, WebP, or GIF</div>
            </div>
          )}
        </label>
        <button
          type="button"
          onClick={handleFileSubmit}
          disabled={busy || !selectedFile}
          className="w-full rounded-lg bg-neutral-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-neutral-50 dark:text-neutral-900 dark:hover:bg-neutral-200"
        >
          {busy ? "Analyzing…" : "Analyze damage"}
        </button>
      </div>

      {/* Preview */}
      {preview && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={preview}
          alt="preview"
          className="mt-4 max-h-72 w-full rounded-lg border border-black/10 object-contain dark:border-white/10"
        />
      )}

      {/* Samples */}
      <div className="mt-5 border-t border-black/5 pt-4 dark:border-white/5">
        <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-neutral-500">Try a sample</h4>
        <div className="grid grid-cols-3 gap-2">
          {SAMPLE_IMAGES.map((sample) => (
            <button
              key={sample.url}
              type="button"
              onClick={() => handleSampleClick(sample.url)}
              disabled={busy}
              className="group relative overflow-hidden rounded-md border border-black/10 transition hover:border-neutral-400 disabled:opacity-50 dark:border-white/10 dark:hover:border-neutral-500"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={sample.url}
                alt={sample.label}
                className="aspect-square w-full object-cover transition group-hover:scale-105"
              />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent px-2 py-1.5 text-[10px] font-medium text-white">
                {sample.label}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
