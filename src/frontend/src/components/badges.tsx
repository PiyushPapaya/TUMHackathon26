import type { EvidenceLevel, RequirementStatus, SourceType } from "@/src/lib/api";

// Ampel statt vier Farben: Ein PM soll in einer Sekunde sehen, ob etwas belegt ist.
// A und B sind durch Kundenstimmen getragen (grün), C ist dünn (gelb), D ist nur Annahme (rot).
// Der Buchstabe bleibt klein daneben, damit die feinere Stufe nicht verloren geht.
export const EVIDENCE_LIGHT: Record<EvidenceLevel, { word: string; dot: string; text: string }> = {
  A: { word: "Strong", dot: "bg-emerald-500", text: "text-emerald-800" },
  B: { word: "Moderate", dot: "bg-emerald-500", text: "text-emerald-800" },
  C: { word: "Weak", dot: "bg-amber-400", text: "text-amber-800" },
  D: { word: "Assumption", dot: "bg-[var(--m-red)]", text: "text-[var(--m-red)]" },
};

export function EvidenceDot({ level, size = 10 }: { level: EvidenceLevel; size?: number }) {
  const style = EVIDENCE_LIGHT[level];
  if (!style) return null;
  return <span aria-hidden="true" className={`inline-block shrink-0 rounded-full ${style.dot}`} style={{ width: size, height: size }} />;
}

export function EvidenceBadge({ level, reason }: { level: EvidenceLevel; reason?: string }) {
  const style = EVIDENCE_LIGHT[level];
  // Trend-Einträge ohne Anforderung haben keine Evidenzstufe: dann gar kein Badge statt Absturz.
  if (!style) return null;
  return (
    <span title={reason} className={`inline-flex min-h-7 items-center gap-2 whitespace-nowrap text-xs font-semibold ${style.text}`}>
      <EvidenceDot level={level} />
      {style.word}
      <span className="font-normal text-[var(--grey-500)]">{level}</span>
    </span>
  );
}

// Gelbes Badge mit Klartext statt eigener Spalte: Konflikte sind selten, sollen aber ohne Hover verständlich sein.
export function ConflictMark({ conflictingTitles }: { conflictingTitles: string[] }) {
  if (conflictingTitles.length === 0) return null;
  return (
    <span
      title={`Conflicting evidence: ${conflictingTitles.join(", ")}`}
      className="inline-flex h-7 items-center gap-1.5 border border-amber-300 bg-amber-50 px-2 text-xs font-semibold text-amber-800"
    >
      <span aria-hidden="true">!</span> Conflicting evidence
    </span>
  );
}

const STATUS_STYLE: Record<RequirementStatus, { label: string; className: string }> = {
  proposed: { label: "Proposed", className: "border-slate-300 bg-slate-50 text-slate-700" },
  challenged: { label: "Challenged", className: "border-amber-300 bg-amber-50 text-amber-800" },
  approved: { label: "Approved", className: "border-emerald-300 bg-emerald-50 text-emerald-800" },
  rejected: { label: "Rejected", className: "border-rose-300 bg-rose-50 text-rose-800" },
};

export function StatusBadge({ status }: { status: RequirementStatus }) {
  const style = STATUS_STYLE[status];
  return (
    <span
      className={`inline-flex min-h-7 items-center rounded-none border px-3 text-xs font-semibold ${style.className}`}
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
    "inline-flex min-h-7 items-center rounded-none border border-yellow-300 bg-yellow-50 px-3 text-xs font-semibold text-yellow-800";
  if (href) {
    return (
      <a className={`${className} hover:bg-yellow-100`} href={href} title={conflictingTitles.join(", ")}>
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
    className: "border-emerald-300 bg-emerald-50 text-emerald-800",
  },
  feedback_external: {
    label: "External feedback",
    hint: "External customer voice; useful as confirmation.",
    className: "border-blue-300 bg-blue-50 text-blue-800",
  },
  study: {
    label: "Study",
    hint: "BMW customer study; counts toward the evidence level.",
    className: "border-emerald-300 bg-emerald-50 text-emerald-800",
  },
  web: {
    label: "Web source",
    hint: "External web source with visible URL and trust metadata.",
    className: "border-amber-300 bg-amber-50 text-amber-800",
  },
  external_stat: {
    label: "External statistic",
    hint: "External statistic; confirms context.",
    className: "border-amber-300 bg-amber-50 text-amber-800",
  },
  sales: {
    label: "Sales context",
    hint: "Volume context, not direct customer evidence.",
    className: "border-slate-300 bg-slate-50 text-slate-700",
  },
  option_list: {
    label: "Offer context",
    hint: "Current offer or option list, not direct customer evidence.",
    className: "border-slate-300 bg-slate-50 text-slate-700",
  },
};

export function SourceTrustBadge({ sourceType }: { sourceType: SourceType }) {
  const style = SOURCE_TRUST[sourceType] ?? SOURCE_TRUST.web;
  return (
    <span
      title={style.hint}
      className={`inline-flex min-h-6 items-center rounded-none border px-2 text-[11px] font-semibold ${style.className}`}
    >
      {style.label}
    </span>
  );
}
