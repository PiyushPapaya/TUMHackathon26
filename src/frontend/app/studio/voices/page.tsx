"use client";

/**
 * Kundenstimmen-Wand: jedes Zitat hinter der Liste, mit ID und der Anforderung, die es stützt.
 * Team-Picks aus baukasten/stimmen.json stehen oben (Mission Daten-Detektiv, ohne Code pflegbar).
 */
import { useState } from "react";
import stimmen from "@/baukasten/stimmen.json";
import type { Evidence } from "@/src/lib/api";
import { useStudio } from "@/src/studio/StudioData";
import { ToolFrame } from "@/src/studio/ToolFrame";
import { Notice, QuoteCard } from "@/src/studio/ui";

const FILTERS = [
  { key: "all", label: "All" },
  { key: "-1", label: "Complaints" },
  { key: "1", label: "Praise" },
  { key: "0", label: "Neutral" },
] as const;

export default function VoicesPage() {
  const { evidenceById, signals, requirements } = useStudio();
  const [filter, setFilter] = useState<(typeof FILTERS)[number]["key"]>("all");

  // Beleg → Anforderung: über die Befunde, auf denen die Anforderung beruht.
  const requirementFor = (e: Evidence) => {
    const signalIds = signals.filter((s) => s.evidence_ids.includes(e.id)).map((s) => s.id);
    return requirements.find((r) => r.signal_ids.some((id) => signalIds.includes(id)))?.title;
  };

  const notes = new Map(stimmen.team_picks.map((p) => [p.evidence_id, p.note]));
  const all = [...evidenceById.values()];
  const visible = all
    .filter((e) => filter === "all" || String(e.polarity) === filter)
    .sort((a, b) => Number(notes.has(b.id)) - Number(notes.has(a.id)));

  const filterBar = (
    <div role="radiogroup" aria-label="Filter quotes" className="flex gap-1 rounded-lg border border-[var(--ink)]/15 bg-white p-1">
      {FILTERS.map((f) => {
        const count = f.key === "all" ? all.length : all.filter((e) => String(e.polarity) === f.key).length;
        return (
          <button
            key={f.key}
            role="radio"
            aria-checked={filter === f.key}
            onClick={() => setFilter(f.key)}
            className={`rounded-md px-3 py-1.5 text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
              filter === f.key ? "bg-[var(--ink)] text-white" : "text-[var(--ink)]/70 hover:text-[var(--ink)]"
            }`}
          >
            {f.label} <span className="tabular-nums opacity-60">{count}</span>
          </button>
        );
      })}
    </div>
  );

  return (
    <ToolFrame tool="voices" actions={filterBar}>
      {visible.length === 0 ? (
        <Notice kind="empty">No quotes in this group. Pick another filter above.</Notice>
      ) : (
        <div className="columns-1 gap-4 sm:columns-2 lg:columns-3 [&>*]:mb-4 [&>*]:break-inside-avoid">
          {visible.map((e) => (
            <QuoteCard key={e.id} evidence={e} note={notes.get(e.id)} context={requirementFor(e)} />
          ))}
        </div>
      )}
    </ToolFrame>
  );
}
