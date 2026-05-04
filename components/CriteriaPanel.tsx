import { REVIEW_THRESHOLDS } from "@/lib/schema";

const formatUSD = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

interface Criterion {
  code: string;
  label: string;
  rule: string;
  description: string;
}

const CRITERIA: Criterion[] = [
  {
    code: "Low confidence",
    label: "Low confidence",
    rule: `Any field < ${REVIEW_THRESHOLDS.CONFIDENCE}`,
    description: "Make, model, color, year, severity, or repair-cost confidence below threshold",
  },
  {
    code: "Severe damage",
    label: "Severe damage",
    rule: 'severity = "severe"',
    description: "Possible structural, frame, or safety-system involvement",
  },
  {
    code: "Poor image quality",
    label: "Poor image quality",
    rule: `score < ${REVIEW_THRESHOLDS.IMAGE_QUALITY}`,
    description: "Blur, darkness, partial view — assessment may miss damage detail",
  },
  {
    code: "High-value claim",
    label: "High-value claim",
    rule: `> ${formatUSD(REVIEW_THRESHOLDS.HIGH_VALUE_USD)}`,
    description: "Repair estimate high end exceeds dollar threshold",
  },
];

export function CriteriaPanel() {
  return (
    <details className="group rounded-xl border border-black/10 bg-white shadow-sm dark:border-white/10 dark:bg-neutral-950">
      <summary className="flex cursor-pointer items-center justify-between gap-3 px-5 py-4">
        <div>
          <h3 className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">
            Human Review Criteria
          </h3>
          <p className="mt-0.5 text-xs text-neutral-500">
            4 triggers · any one fires escalates to adjuster
          </p>
        </div>
        <span className="text-neutral-400 transition group-open:rotate-180">▾</span>
      </summary>
      <div className="border-t border-black/5 px-5 py-4 dark:border-white/5">
        <ol className="space-y-3 text-sm">
          {CRITERIA.map((c, i) => (
            <li key={i} className="grid grid-cols-[auto_1fr] items-start gap-x-3 gap-y-1">
              <span className="rounded bg-amber-500/15 px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider text-amber-800 dark:text-amber-300">
                {c.label}
              </span>
              <code className="font-mono text-xs text-neutral-700 dark:text-neutral-300">{c.rule}</code>
              <span className="col-start-2 text-xs text-neutral-500">{c.description}</span>
            </li>
          ))}
        </ol>
        <p className="mt-4 border-t border-black/5 pt-3 text-[11px] text-neutral-500 dark:border-white/5">
          Thresholds are computed server-side in <code className="font-mono">lib/schema.ts</code> and configurable per
          carrier policy.
        </p>
      </div>
    </details>
  );
}
