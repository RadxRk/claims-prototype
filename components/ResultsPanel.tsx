import type { Analysis, Trigger } from "@/lib/schema";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { SeverityBadge } from "./SeverityBadge";

const formatUSD = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

const TRIGGER_LABELS: Record<Trigger["code"], string> = {
  low_confidence: "Low confidence",
  severe_damage: "Severe damage",
  poor_image_quality: "Poor image quality",
  high_value: "High-value claim",
};

interface ResultsPanelProps {
  analysis: Analysis;
  triggers: Trigger[];
}

export function ResultsPanel({ analysis, triggers }: ResultsPanelProps) {
  const { car, damage, repair_estimate, image_quality, analysis_notes } = analysis;
  const requiresReview = triggers.length > 0;

  return (
    <div className="space-y-4">
      {requiresReview && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-4">
          <div className="flex items-start gap-3">
            <div className="text-2xl">⚠️</div>
            <div className="flex-1">
              <h3 className="font-semibold text-amber-900 dark:text-amber-200">Human Review Recommended</h3>
              <ul className="mt-3 space-y-2">
                {triggers.map((trigger, i) => (
                  <li
                    key={i}
                    className="flex items-start gap-2 rounded-md bg-white/40 px-3 py-2 text-sm dark:bg-black/20"
                  >
                    <span className="rounded bg-amber-500/20 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-amber-900 dark:text-amber-200">
                      {TRIGGER_LABELS[trigger.code]}
                    </span>
                    <span className="flex-1 text-amber-900 dark:text-amber-100">{trigger.label}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Car Metadata */}
      <Card title="Vehicle">
        <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
          <Field label="Make" value={car.make} confidence={car.field_confidences.make} />
          <Field label="Model" value={car.model} confidence={car.field_confidences.model} />
          <Field label="Color" value={car.color} confidence={car.field_confidences.color} />
          <Field label="Year" value={car.year_estimate} confidence={car.field_confidences.year} />
        </div>
        {car.confidence_reasoning && (
          <p className="mt-4 border-t border-black/5 pt-3 text-xs italic text-neutral-600 dark:border-white/5 dark:text-neutral-400">
            {car.confidence_reasoning}
          </p>
        )}
      </Card>

      {/* Damage */}
      <Card title="Damage Assessment" headerExtra={<SeverityBadge severity={damage.severity} />}>
        <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">{damage.summary}</p>
        {damage.affected_areas.length > 0 && (
          <div className="mt-3 space-y-2">
            {damage.affected_areas.map((area, i) => (
              <div key={i} className="flex items-start justify-between gap-3 rounded-md bg-neutral-50 px-3 py-2 text-sm dark:bg-neutral-900/50">
                <div>
                  <div className="font-medium text-neutral-900 dark:text-neutral-100">{area.location}</div>
                  <div className="text-xs text-neutral-600 dark:text-neutral-400">{area.damage_type}</div>
                </div>
                <ConfidenceBadge value={area.area_confidence} />
              </div>
            ))}
          </div>
        )}
        <div className="mt-3 flex items-center gap-2 text-xs text-neutral-600 dark:text-neutral-400">
          <span>Severity confidence:</span>
          <ConfidenceBadge value={damage.severity_confidence} />
        </div>
        {damage.confidence_reasoning && (
          <p className="mt-3 border-t border-black/5 pt-3 text-xs italic text-neutral-600 dark:border-white/5 dark:text-neutral-400">
            {damage.confidence_reasoning}
          </p>
        )}
      </Card>

      {/* Repair Estimate */}
      <Card title="Repair Estimate" headerExtra={<ConfidenceBadge value={repair_estimate.confidence} size="md" />}>
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-neutral-900 dark:text-neutral-50">
            {formatUSD(repair_estimate.low_usd)}
          </span>
          <span className="text-neutral-500">–</span>
          <span className="text-3xl font-bold text-neutral-900 dark:text-neutral-50">
            {formatUSD(repair_estimate.high_usd)}
          </span>
        </div>
        <p className="mt-3 text-sm text-neutral-700 dark:text-neutral-300">{repair_estimate.reasoning}</p>
        {repair_estimate.sources.length > 0 && (
          <div className="mt-4">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-neutral-500">Sources</h4>
            <ul className="mt-2 space-y-1 text-xs">
              {repair_estimate.sources.map((src, i) => (
                <li key={i} className="truncate">
                  <a
                    href={src}
                    target="_blank"
                    rel="noreferrer noopener"
                    className="text-blue-600 hover:underline dark:text-blue-400"
                  >
                    {src}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>

      {/* Meta footer */}
      <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-neutral-600 dark:text-neutral-400">
        <span>
          Image quality:{" "}
          <span className="font-mono font-medium text-neutral-800 dark:text-neutral-200">
            {image_quality.score}/100
          </span>
          {image_quality.issues.length > 0 && (
            <span className="ml-1 text-neutral-500">({image_quality.issues.join(", ")})</span>
          )}
        </span>
      </div>

      {analysis_notes && (
        <details className="rounded-lg border border-black/10 bg-neutral-50 p-3 text-sm dark:border-white/10 dark:bg-neutral-900/50">
          <summary className="cursor-pointer font-medium text-neutral-700 dark:text-neutral-300">
            Full analysis notes
          </summary>
          <p className="mt-2 whitespace-pre-wrap text-neutral-600 dark:text-neutral-400">{analysis_notes}</p>
        </details>
      )}
    </div>
  );
}

function Card({
  title,
  headerExtra,
  children,
}: {
  title: string;
  headerExtra?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-black/10 bg-white p-5 shadow-sm dark:border-white/10 dark:bg-neutral-950">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-neutral-500 dark:text-neutral-400">
          {title}
        </h3>
        {headerExtra}
      </div>
      {children}
    </div>
  );
}

function Field({ label, value, confidence }: { label: string; value: string; confidence: number }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <span className="text-xs uppercase tracking-wider text-neutral-500 dark:text-neutral-400">{label}</span>
        <ConfidenceBadge value={confidence} />
      </div>
      <div className="text-base font-medium text-neutral-900 dark:text-neutral-100">{value}</div>
    </div>
  );
}
