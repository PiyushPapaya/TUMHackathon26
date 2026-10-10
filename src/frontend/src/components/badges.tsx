/**
 * Kleine, wiederverwendbare Badges nach den Design-Regeln aus docs/pfade/PFAD-D.md:
 * Evidenzstufe mit Klartext + Tooltip, Status, Konflikt. Eine Datei, weil Liste
 * (D2) und Detailseite (D3) dieselben Badges brauchen.
 */
import type { EvidenceLevel, RequirementStatus, SourceType } from "@/src/lib/api";

const EVIDENCE_STYLE: Record<EvidenceLevel, { label: string; className: string }> = {
  A: {
    label: "A · strong",
    className:
      "bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800",
  },
  B: {
    label: "B · medium",
    className:
      "bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-950 dark:text-blue-300 dark:border-blue-800",
  },
  C: {
    label: "C · weak",
    className:
      "bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800",
  },
  D: {
    label: "D · assumption",
    className:
      "bg-zinc-100 text-zinc-600 border-zinc-300 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700",
  },
};

/** `reason` ist der Begründungssatz (Requirement.rationale), damit die Zahl eine Herkunft hat. */
export function EvidenceBadge({ level, reason }: { level: EvidenceLevel; reason?: string }) {
  const style = EVIDENCE_STYLE[level];
  return (
    <span
      title={reason}
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${style.className}`}
    >
      {style.label}
    </span>
  );
}

const STATUS_STYLE: Record<RequirementStatus, { label: string; className: string }> = {
  proposed: {
    label: "Proposed",
    className: "bg-zinc-100 text-zinc-700 border-zinc-300 dark:bg-zinc-800 dark:text-zinc-300 dark:border-zinc-700",
  },
  challenged: {
    label: "Challenged",
    className:
      "bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800",
  },
  approved: {
    label: "Approved",
    className:
      "bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800",
  },
  rejected: {
    label: "Rejected",
    className: "bg-rose-100 text-rose-800 border-rose-300 dark:bg-rose-950 dark:text-rose-300 dark:border-rose-800",
  },
};

export function StatusBadge({ status }: { status: RequirementStatus }) {
  const style = STATUS_STYLE[status];
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${style.className}`}
    >
      {style.label}
    </span>
  );
}

/** Gelbes Badge, falls ein verknüpfter Befund `conflicts_with` hat (Design-Regel PFAD-D). */
export function ConflictBadge({ conflictingTitles }: { conflictingTitles: string[] }) {
  if (conflictingTitles.length === 0) return null;
  return (
    <span
      title={`Conflicting evidence: ${conflictingTitles.join(", ")}`}
      className="inline-flex items-center gap-1 rounded-full border border-yellow-300 bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800 dark:border-yellow-800 dark:bg-yellow-950 dark:text-yellow-300"
    >
      ⚠ Conflicting evidence
    </span>
  );
}

const CATEGORY_LABELS: Record<string, string> = {
  exterior: "Exterior",
  interior: "Interior",
  comfort_space: "Comfort & space",
  infotainment_digital: "Infotainment & digital",
  driving_experience: "Driving experience",
  range_charging: "Range & charging",
  driver_assistance: "Driver assistance",
  quality_perception: "Quality perception",
  variants_packages: "Variants & packages",
};

export function categoryLabel(category: string): string {
  return CATEGORY_LABELS[category] ?? category;
}

/**
 * Vertrauensstufe pro Beleg, abgeleitet aus den Regeln in
 * requirements_engine/evidence_level.py (BMW_SOURCES zählen mehr als Web, Web bestätigt nur,
 * Absatz/Optionsliste sind Kontext, kein Kundenbeleg). Keine neue Regel, nur die bestehende
 * für den Detailbildschirm sichtbar gemacht.
 */
const SOURCE_TRUST: Record<SourceType, { label: string; hint: string; className: string }> = {
  feedback: {
    label: "BMW customer data",
    hint: "Direct customer feedback; counts toward the evidence level.",
    className: "bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800",
  },
  study: {
    label: "BMW customer data",
    hint: "BMW customer study; counts toward the evidence level.",
    className: "bg-emerald-50 text-emerald-700 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800",
  },
  web: {
    label: "External · confirms only",
    hint: "Web source. Can confirm a finding but never carries it alone.",
    className: "bg-amber-50 text-amber-700 border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800",
  },
  sales: {
    label: "Context data",
    hint: "Sales volume, not direct customer feedback.",
    className: "bg-zinc-50 text-zinc-600 border-zinc-300 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700",
  },
  option_list: {
    label: "Context data",
    hint: "Today's options list, not direct customer feedback.",
    className: "bg-zinc-50 text-zinc-600 border-zinc-300 dark:bg-zinc-800 dark:text-zinc-400 dark:border-zinc-700",
  },
};

export function SourceTrustBadge({ sourceType }: { sourceType: SourceType }) {
  const style = SOURCE_TRUST[sourceType];
  return (
    <span
      title={style.hint}
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${style.className}`}
    >
      {style.label}
    </span>
  );
}
