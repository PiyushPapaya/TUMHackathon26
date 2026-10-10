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

function evidenceOrigin(evidence: Evidence) {
  const letter = evidence.meta?.source_letter;
  const country = evidence.meta?.country;
  const engine = evidence.meta?.engine;
  return [evidence.source_name, letter ? `Feedback ${letter}` : null, country, engine]
    .filter(Boolean)
    .join(" · ");
}

function EvidenceItem({ evidence }: { evidence: Evidence }) {
  return (
    <li className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 p-3 text-sm">
      <p className="text-zinc-700 dark:text-zinc-300">&ldquo;{evidence.text}&rdquo;</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
        <span className="font-semibold text-zinc-700 dark:text-zinc-300">{evidence.id}</span>
        <span>{evidenceOrigin(evidence)}</span>
        {evidence.url && (
          <a
            href={evidence.url}
            target="_blank"
            rel="noopener noreferrer"
            className="font-semibold text-accent-hover dark:text-accent underline underline-offset-2"
          >
            Source link
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
    <article className="rounded-lg border border-zinc-300 dark:border-zinc-700 bg-surface">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        className="flex min-h-14 w-full items-center justify-between gap-3 px-4 py-3 text-left transition hover:bg-zinc-50 dark:hover:bg-zinc-900 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/50 focus-visible:ring-offset-2 focus-visible:ring-offset-background"
      >
        <div>
          <p className="font-semibold text-foreground">{signal.title}</p>
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            {KIND_LABELS[signal.kind] ?? signal.kind} · {signal.mention_count} mentions from linked findings
          </p>
        </div>
        <span className="grid h-8 w-8 place-items-center rounded-full border border-zinc-200 dark:border-zinc-800 text-lg leading-none text-zinc-500 dark:text-zinc-400">
          {open ? "-" : "+"}
        </span>
      </button>

      {open && (
        <div className="border-t border-zinc-200 dark:border-zinc-800 px-4 py-3">
          <p className="mb-3 text-sm text-zinc-700 dark:text-zinc-300">{signal.summary}</p>

          {signal.conflicts_with.length > 0 && (
            <a
              href={`#signal-${signal.conflicts_with[0]}`}
              title={`Conflicting signal IDs: ${signal.conflicts_with.join(", ")}`}
              className="mb-3 inline-flex min-h-7 items-center rounded-full border border-yellow-300 bg-yellow-50 px-3 text-xs font-semibold text-yellow-800 hover:bg-yellow-100 dark:border-yellow-800 dark:bg-yellow-950 dark:text-yellow-300 dark:hover:bg-yellow-900"
            >
              Conflicting evidence
            </a>
          )}

          <ul className="space-y-2">
            {evidence.map((item) => (
              <EvidenceItem key={item.id} evidence={item} />
            ))}
            {evidence.length === 0 && (
              <li className="rounded-sm border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 p-3 text-sm text-zinc-500 dark:text-zinc-400">
                No evidence linked to this finding.
              </li>
            )}
          </ul>
        </div>
      )}
    </article>
  );
}
