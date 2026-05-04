interface ConfidenceBadgeProps {
  value: number; // 0-100
  label?: string;
  size?: "sm" | "md";
}

export function ConfidenceBadge({ value, label, size = "sm" }: ConfidenceBadgeProps) {
  const tier = value >= 80 ? "high" : value >= 60 ? "med" : "low";
  const colors = {
    high: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 ring-emerald-500/30",
    med: "bg-amber-500/15 text-amber-700 dark:text-amber-300 ring-amber-500/30",
    low: "bg-rose-500/15 text-rose-700 dark:text-rose-300 ring-rose-500/30",
  } as const;
  const padding = size === "md" ? "px-2.5 py-1 text-xs" : "px-2 py-0.5 text-[10px]";
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-mono font-medium ring-1 ring-inset ${colors[tier]} ${padding}`}
      title={label ? `${label}: ${value}%` : `${value}% confident`}
    >
      {label ? <span className="opacity-70">{label}</span> : null}
      <span>{value}%</span>
    </span>
  );
}
