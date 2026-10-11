"use client";

import { useState } from "react";
import type { OpportunitiesView } from "@/src/lib/insights";
import { categoryLabel } from "@/src/components/badges";
import { en, QUADRANT_EN } from "./labels";

const COLOR: Record<string, string> = {
  Chance: "#1c69d4",
  "Stärke halten": "#16588e",
  Beobachten: "#9a9a9a",
  Nebensache: "#cfcfcf",
};

// Streudiagramm Wichtigkeit (x) gegen Unzufriedenheit (y) aus den BMW-Kundenstudien.
// Rechts oben = wichtig und unzufrieden = Chance. Darunter dieselben Daten als Tabelle (barrierefrei).
export function OpportunityMap({ data }: { data: OpportunitiesView }) {
  const [showAll, setShowAll] = useState(false);
  const maxY = Math.max(0.1, ...data.points.map((p) => p.dissatisfaction)) * 1.1;
  const x = (v: number) => 50 + v * 1100;
  const y = (v: number) => 450 - (v / maxY) * 420;
  // Etwa 100 Attribute passen nicht alle mit Namen ins Bild: nur die 5 größten Chancen bekommen ein Label,
  // alle anderen zeigen den Namen beim Darüberfahren (title) und stehen unten in der Tabelle.
  const ranked = [...data.points].sort((a, b) => b.importance * b.dissatisfaction - a.importance * a.dissatisfaction);
  const labeled = new Set(ranked.slice(0, 5).map((p) => p.attribute));
  const rows = showAll ? ranked : ranked.slice(0, 12);
  // Ohne Studien-Attribute wäre das Diagramm nur ein leeres Achsenkreuz: lieber ehrlich sagen, was fehlt.
  if (data.points.length === 0) {
    return (
      <div className="border border-dashed border-[var(--hairline)] p-8">
        <p className="text-lg font-light text-[var(--ink)]">No study attributes for this scenario yet.</p>
        <p className="mt-2 max-w-2xl text-sm text-[var(--grey-500)]">
          The map needs importance and satisfaction scores per attribute from a BMW customer study. Until they arrive, the ranking in the cockpit relies on customer comments and web sources.
        </p>
      </div>
    );
  }
  return (
    <div>
      <svg viewBox="0 0 1200 490" className="w-full border border-[var(--hairline)]" role="img" aria-label="Importance versus dissatisfaction per attribute">
        <line x1="50" y1="450" x2="1150" y2="450" stroke="#cfcfcf" />
        <line x1="50" y1="20" x2="50" y2="450" stroke="#cfcfcf" />
        <text x="1150" y="478" fontSize="14" textAnchor="end" fill="#6b6b6b">Importance →</text>
        <text x="60" y="30" fontSize="14" fill="#6b6b6b">↑ Dissatisfaction</text>
        {data.points.map((p) => (
          <circle key={p.attribute + p.category + p.importance} cx={x(p.importance)} cy={y(p.dissatisfaction)} r={labeled.has(p.attribute) ? 6 : 4} fill={COLOR[p.quadrant] ?? "#9a9a9a"} opacity={labeled.has(p.attribute) ? 1 : 0.7}>
            <title>{p.attribute}</title>
          </circle>
        ))}
        {data.points.filter((p) => labeled.has(p.attribute)).map((p) => (
          <text key={p.attribute} x={Math.min(x(p.importance) + 10, 1000)} y={y(p.dissatisfaction) + 4} fontSize="13" fill="#262626">{p.attribute.slice(0, 40)}</text>
        ))}
      </svg>
      <p className="mt-2 text-xs text-[var(--grey-500)]">Blue = opportunity (important and dissatisfied). Hover a dot for its name.</p>
      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[600px] text-left text-sm">
          <thead className="text-xs uppercase tracking-[0.12em] text-[var(--grey-500)]">
            <tr>{["Attribute", "Category", "Importance", "Dissatisfaction", "Verdict"].map((h) => <th key={h} className="py-2 pr-4 font-semibold">{h}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.attribute + p.category + p.importance} className="border-t border-[var(--hairline)]">
                <td className="py-3 pr-4">{p.attribute}</td>
                <td className="py-3 pr-4 text-[var(--grey-500)]">{categoryLabel(p.category)}</td>
                <td className="py-3 pr-4 tabular-nums">{Math.round(p.importance * 100)}%</td>
                <td className="py-3 pr-4 tabular-nums">{Math.round(p.dissatisfaction * 100)}%</td>
                <td className="py-3 pr-4 font-semibold">{en(QUADRANT_EN, p.quadrant)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {ranked.length > 12 && (
        <button type="button" onClick={() => setShowAll(!showAll)} className="mt-4 text-sm font-semibold text-[var(--blue)]">
          {showAll ? "Show top 12 only" : `Show all ${ranked.length} attributes`}
        </button>
      )}
    </div>
  );
}
