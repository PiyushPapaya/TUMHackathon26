/**
 * Ein Befund (Signal) als aufklappbare Karte mit seinen Belegen (Zitat, Quelle, Vertrauensstufe).
 * Durchgezogener Rand nach Design-Regel (Evidenz, kein Annahme-Look). Eigene Datei, weil die
 * Detailseite sonst über 200 Zeilen wächst (Jury-Review kappt danach).
 */
"use client";

import { useState } from "react";
import type { Evidence, Signal } from "@/src/lib/api";
import { SourceTrustBadge } from "@/src/components/badges";

const KIND_LABELS: Record<string, string> = {
  complaint: "Complaint",
  unmet_need: "Unmet need",
  delight: "Delight",
  competitor_advantage: "Competitor advantage",
  trend: "Trend",
};

function EvidenceItem({ evidence }: { evidence: Evidence }) {
  return (
    <li className="rounded-md border border-zinc-200 bg-zinc-50 p-3 text-sm dark:border-zinc-800 dark:bg-zinc-900">
      <p className="italic text-zinc-700 dark:text-zinc-300">&ldquo;{evidence.text}&rdquo;</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
        <span className="font-medium text-zinc-600 dark:text-zinc-300">{evidence.source_name}</span>
        {evidence.url && (
          <a
            href={evidence.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline dark:text-blue-400"
          >
            Link
          </a>
        )}
        <SourceTrustBadge sourceType={evidence.source_type} />
      </div>
    </li>
  );
}

export function FindingCard({ signal, evidence }: { signal: Signal; evidence: Evidence[] }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-lg border border-zinc-300 bg-surface dark:border-zinc-700">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left"
      >
        <div>
          <p className="font-medium text-[#0b1f3a] dark:text-zinc-100">{signal.title}</p>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            {KIND_LABELS[signal.kind] ?? signal.kind} · {signal.mention_count} mentions
          </p>
        </div>
        <span className="text-lg leading-none text-zinc-400 dark:text-zinc-500">{open ? "–" : "+"}</span>
      </button>

      {open && (
        <div className="border-t border-zinc-200 px-4 py-3 dark:border-zinc-800">
          <p className="mb-3 text-sm text-zinc-600 dark:text-zinc-400">{signal.summary}</p>

          {signal.conflicts_with.length > 0 && (
            <p
              title={`Conflicting signal IDs: ${signal.conflicts_with.join(", ")}`}
              className="mb-3 inline-flex items-center gap-1 rounded-full border border-yellow-300 bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800 dark:border-yellow-800 dark:bg-yellow-950 dark:text-yellow-300"
            >
              ⚠ Conflicting evidence
            </p>
          )}

          <ul className="space-y-2">
            {evidence.map((item) => (
              <EvidenceItem key={item.id} evidence={item} />
            ))}
            {evidence.length === 0 && (
              <li className="text-sm text-zinc-400 dark:text-zinc-500">No evidence linked.</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
