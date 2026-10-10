"use client";

/**
 * Annahmen-Schalter: Faktoren ausschalten (Standard: "Future relevance", unsere Wette auf 2030)
 * und sehen, welche Anforderungen ihren Rang halten. Rechnet im Browser mit derselben Formel wie das Backend
 * (src/studio/scoring.ts) und ändert nichts gespeichert, darum kein Audit-Eintrag.
 * Warum: Der Brief will sehen, "where conclusions rely on forward-looking assumptions".
 */
import { useState } from "react";
import { EvidenceBadge } from "@/src/components/badges";
import { FACTORS, scoreWithout, type FactorKey } from "@/src/studio/scoring";
import { useStudio } from "@/src/studio/StudioData";
import { ToolFrame } from "@/src/studio/ToolFrame";
import { AssumptionList } from "@/src/studio/ui";

export default function AssumptionsPage() {
  const { requirements } = useStudio();
  const [off, setOff] = useState<Set<FactorKey>>(new Set(["future_relevance"]));
  const [open, setOpen] = useState<string | null>(null);

  function toggle(key: FactorKey) {
    setOff((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }

  const rows = requirements
    .map((r) => ({ req: r, adjusted: scoreWithout(r, off) }))
    .sort((a, b) => b.adjusted - a.adjusted)
    .map((row, i) => ({ ...row, newRank: i + 1, move: row.req.rank - (i + 1) }));

  const switches = (
    <fieldset className="flex flex-wrap gap-2" aria-label="Factors to switch off">
      {FACTORS.map((f) => {
        const isOff = off.has(f.key);
        return (
          <button
            key={f.key}
            onClick={() => toggle(f.key)}
            aria-pressed={isOff}
            className={`rounded-full border px-3 py-1.5 text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
              isOff
                ? "border-dashed border-[var(--assumption)] bg-transparent text-[var(--assumption)] line-through"
                : "border-[var(--ink)]/25 bg-white"
            }`}
          >
            {f.label}
          </button>
        );
      })}
    </fieldset>
  );

  return (
    <ToolFrame tool="assumptions" actions={switches}>
      <p className="mb-4 text-sm text-[var(--ink)]/60">
        {off.size === 0
          ? "All factors on: this is the ranking from the cockpit."
          : `Switched off: ${FACTORS.filter((f) => off.has(f.key)).map((f) => f.label).join(", ")}. The other weights are scaled back up to 100%.`}
      </p>
      <ol className="divide-y divide-[var(--ink)]/10 rounded-lg border border-[var(--ink)]/15 bg-white">
        {rows.map(({ req, adjusted, newRank, move }) => (
          <li key={req.id}>
            <button
              onClick={() => setOpen(open === req.id ? null : req.id)}
              aria-expanded={open === req.id}
              className="grid w-full grid-cols-[3rem_1fr_auto] items-center gap-4 px-5 py-4 text-left hover:bg-[var(--paper)]/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-[var(--accent)] sm:grid-cols-[3rem_1fr_7rem_6rem_6rem]"
            >
              <span className="text-2xl font-semibold tabular-nums [font-stretch:125%]">{newRank}</span>
              <span>
                <span className="font-medium">{req.title}</span>
                <span className="ml-3 hidden sm:inline">
                  <EvidenceBadge level={req.evidence_level} reason={req.rationale} />
                </span>
              </span>
              <Move value={move} />
              <span className="hidden text-right text-sm tabular-nums text-[var(--ink)]/50 sm:block">was {req.score}</span>
              <span className="hidden text-right text-lg font-semibold tabular-nums sm:block">{adjusted}</span>
            </button>
            {open === req.id && (
              <div className="grid gap-6 border-t border-[var(--ink)]/10 px-5 py-5 sm:grid-cols-2">
                <div>
                  <p className="mb-2 text-sm font-medium">What this requirement assumes</p>
                  <AssumptionList items={req.assumptions} />
                </div>
                <div>
                  <p className="mb-2 text-sm font-medium">Open uncertainties</p>
                  <AssumptionList items={req.uncertainties} />
                </div>
              </div>
            )}
          </li>
        ))}
      </ol>
    </ToolFrame>
  );
}

/** Rangänderung gegenüber dem Cockpit: hoch grün, runter rot, gleich grau. */
function Move({ value }: { value: number }) {
  if (value === 0) return <span className="text-right text-sm text-[var(--ink)]/45">holds rank</span>;
  const up = value > 0;
  return (
    <span className={`text-right text-sm font-semibold ${up ? "text-[var(--praise)]" : "text-[var(--complaint)]"}`}>
      {up ? "▲" : "▼"} {Math.abs(value)} {Math.abs(value) === 1 ? "place" : "places"}
    </span>
  );
}
