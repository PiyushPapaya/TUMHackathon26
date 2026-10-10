import type { EvidenceLevel, RequirementStatus, SourceType } from "@/src/lib/api";

const EVIDENCE_STYLE: Record<EvidenceLevel, { label: string; className: string }> = {
  A: {
    label: "A · strong",
    className: "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  },
  B: {
    label: "B · medium",
    className: "border-accent/40 bg-accent/5 text-accent-hover dark:bg-accent/10 dark:text-accent",
  },
  C: {
    label: "C · weak",
    className: "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300",
  },
  D: {
    label: "D · assumption",
    className: "border-zinc-300 bg-zinc-50 text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300",
  },
};

export function EvidenceBadge({ level, reason }: { level: EvidenceLevel; reason?: string }) {
  const style = EVIDENCE_STYLE[level];
  return (
    <span
      title={reason}
      className={`inline-flex min-h-7 items-center rounded-full border px-3 text-xs font-semibold ${style.className}`}
    >
      {style.label}
    </span>
  );
}

const STATUS_STYLE: Record<RequirementStatus, { label: string; className: string }> = {
  proposed: {
    label: "Proposed",
    className: "border-zinc-300 bg-zinc-50 text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300",
  },
  challenged: {
    label: "Challenged",
    className: "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300",
  },
  approved: {
    label: "Approved",
    className: "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  },
  rejected: {
    label: "Rejected",
    className: "border-rose-300 bg-rose-50 text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300",
  },
};

export function StatusBadge({ status }: { status: RequirementStatus }) {
  const style = STATUS_STYLE[status];
  return (
    <span
      className={`inline-flex min-h-7 items-center rounded-full border px-3 text-xs font-semibold ${style.className}`}
    >
      {style.label}
    </span>
  );
}

export function ConflictBadge({
  conflictingTitles,
  href,
}: {
  conflictingTitles: string[];
  href?: string;
}) {
  if (conflictingTitles.length === 0) return null;
  const label = "Conflicting evidence";
  const className =
    "inline-flex min-h-7 items-center rounded-full border border-yellow-300 bg-yellow-50 px-3 text-xs font-semibold text-yellow-800 dark:border-yellow-800 dark:bg-yellow-950 dark:text-yellow-300";
  if (href) {
    return (
      <a className={`${className} hover:bg-yellow-100 dark:hover:bg-yellow-900`} href={href} title={conflictingTitles.join(", ")}>
        {label}
      </a>
    );
  }
  return (
    <span className={className} title={conflictingTitles.join(", ")}>
      {label}
    </span>
  );
}

const CATEGORY_LABELS: Record<string, string> = {
  exterior: "Exterior",
  interior: "Interior",
  comfort_space: "Comfort and space",
  infotainment_digital: "Infotainment and digital",
  driving_experience: "Driving experience",
  range_charging: "Range and charging",
  driver_assistance: "Driver assistance",
  quality_perception: "Quality perception",
  variants_packages: "Variants and packages",
};

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] ?? category.replaceAll("_", " ");
}

const SOURCE_TRUST: Record<SourceType, { label: string; hint: string; className: string }> = {
  feedback: {
    label: "Feedback A-D",
    hint: "Direct customer feedback; counts toward the evidence level.",
    className: "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  },
  feedback_external: {
    label: "External feedback",
    hint: "External customer voice; useful as confirmation.",
    className: "border-accent/40 bg-accent/5 text-accent-hover dark:bg-accent/10 dark:text-accent",
  },
  study: {
    label: "Study",
    hint: "BMW customer study; counts toward the evidence level.",
    className: "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
  },
  web: {
    label: "Web source",
    hint: "External web source with visible URL and trust metadata.",
    className: "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300",
  },
  external_stat: {
    label: "External statistic",
    hint: "External statistic; confirms context.",
    className: "border-amber-300 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300",
  },
  sales: {
    label: "Sales context",
    hint: "Volume context, not direct customer evidence.",
    className: "border-zinc-300 bg-zinc-50 text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300",
  },
  option_list: {
    label: "Offer context",
    hint: "Current offer or option list, not direct customer evidence.",
    className: "border-zinc-300 bg-zinc-50 text-zinc-700 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300",
  },
};

export function SourceTrustBadge({ sourceType }: { sourceType: SourceType }) {
  const style = SOURCE_TRUST[sourceType] ?? SOURCE_TRUST.web;
  return (
    <span
      title={style.hint}
      className={`inline-flex min-h-6 items-center rounded-full border px-2 text-[11px] font-semibold ${style.className}`}
    >
      {style.label}
    </span>
  );
}
