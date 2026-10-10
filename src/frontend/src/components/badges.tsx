/**
 * Kleine, wiederverwendbare Badges nach den Design-Regeln aus docs/pfade/PFAD-D.md:
 * Evidenzstufe mit Klartext + Tooltip, Status, Konflikt. Eine Datei, weil Liste
 * (D2) und Detailseite (D3) dieselben Badges brauchen.
 */
import type { EvidenceLevel, RequirementStatus } from "@/src/lib/api";

const EVIDENCE_STYLE: Record<EvidenceLevel, { label: string; className: string }> = {
  A: { label: "A · strong", className: "bg-emerald-100 text-emerald-800 border-emerald-300" },
  B: { label: "B · medium", className: "bg-blue-100 text-blue-800 border-blue-300" },
  C: { label: "C · weak", className: "bg-amber-100 text-amber-800 border-amber-300" },
  D: { label: "D · assumption", className: "bg-zinc-100 text-zinc-600 border-zinc-300" },
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
  proposed: { label: "Proposed", className: "bg-zinc-100 text-zinc-700 border-zinc-300" },
  challenged: { label: "Challenged", className: "bg-amber-100 text-amber-800 border-amber-300" },
  approved: { label: "Approved", className: "bg-emerald-100 text-emerald-800 border-emerald-300" },
  rejected: { label: "Rejected", className: "bg-rose-100 text-rose-800 border-rose-300" },
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
      className="inline-flex items-center gap-1 rounded-full border border-yellow-300 bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800"
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
