interface SeverityBadgeProps {
  severity: "minor" | "moderate" | "severe";
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
  const config = {
    minor: { label: "Minor", classes: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 ring-emerald-500/30" },
    moderate: { label: "Moderate", classes: "bg-amber-500/15 text-amber-700 dark:text-amber-300 ring-amber-500/30" },
    severe: { label: "Severe", classes: "bg-rose-500/15 text-rose-700 dark:text-rose-300 ring-rose-500/30" },
  } as const;
  const { label, classes } = config[severity];
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wider ring-1 ring-inset ${classes}`}
    >
      {label}
    </span>
  );
}
