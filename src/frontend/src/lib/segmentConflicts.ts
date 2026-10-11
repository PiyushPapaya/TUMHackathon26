// Segment-Konflikt (A1) für die Detailseite übersetzen: Das Backend liefert BMW-Rohcodes ("BEVE", Quelle "A"),
// die PM soll "Electric (BEV) kritisiert, Plug-in hybrid lobt" lesen. Eigenständig ohne Imports, damit der
// node-Test die Datei direkt laden kann (deshalb Intl hier statt countryName aus countries.ts).
type RawConflict = {
  dimension: string;
  segment_a?: string;
  segment_b?: string;
  statement: string;
  a_count?: number;
  b_count?: number;
};

export type ConflictSide = { label: string; count: number | null };
// isSegmentComparison=false: "Befund gegen Befund" (Lob vs. Kritik) aus core/views.py, ohne zwei Kundengruppen.
export type ConflictView = {
  topic: string | null;
  dimensionLabel: string;
  isSegmentComparison: boolean;
  critical: ConflictSide;
  positive: ConflictSide;
};

const DIMENSION_LABELS: Record<string, string> = {
  engine: "Drive type",
  country: "Market",
  source: "Feedback channel",
  study_vs_feedback: "Study vs. comments",
  web: "Web source",
  signal: "Opposing findings",
};

const ENGINE_LABELS: Record<string, string> = {
  BEV: "Electric (BEV)",
  BEVE: "Electric (BEV)",
  PHEV: "Plug-in hybrid",
  ICE: "Combustion (ICE)",
};

function countryLabel(code: string): string {
  try {
    return new Intl.DisplayNames(["en"], { type: "region" }).of(code) ?? code;
  } catch {
    return code; // ungültiger Code: lieber roh anzeigen als abstürzen
  }
}

function segmentLabel(dimension: string, segment: string | undefined, fallback: string): string {
  if (!segment) return fallback;
  if (dimension === "engine") return ENGINE_LABELS[segment] ?? segment;
  if (dimension === "country") return countryLabel(segment);
  // Die BMW-Kanäle sind im Datensatz nur als A-D anonymisiert; wir erfinden keine Namen dafür.
  if (dimension === "source") return `Channel ${segment}`;
  if (dimension === "study_vs_feedback") return segment === "study" ? "Customer study" : "Customer feedback";
  return segment;
}

export function describeSegmentConflict(conflict: RawConflict): ConflictView {
  const { dimension } = conflict;
  const colon = conflict.statement.indexOf(": ");
  // Die Studie ist EIN Beleg, keine Kommentarzahl: b_count=1 wäre als "1 lobt" irreführend.
  const positiveCount = dimension === "study_vs_feedback" ? null : (conflict.b_count ?? null);
  return {
    topic: colon > 0 ? conflict.statement.slice(0, colon) : null,
    dimensionLabel: DIMENSION_LABELS[dimension] ?? dimension,
    isSegmentComparison: dimension !== "signal",
    critical: { label: segmentLabel(dimension, conflict.segment_a, "Group A"), count: conflict.a_count ?? null },
    positive: { label: segmentLabel(dimension, conflict.segment_b, "Group B"), count: positiveCount },
  };
}
