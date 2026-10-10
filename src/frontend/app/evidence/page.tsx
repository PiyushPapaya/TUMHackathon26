"use client";

import { Suspense, useState } from "react";
import { getEvidencePage } from "@/src/lib/insights";
import { useLoad } from "@/src/lib/useLoad";
import { useScenarioParam } from "@/src/components/shell/useScenarioParam";
import { ErrorNote, Loading, PageHeader } from "@/src/components/ui/PageHeader";
import { SourceTrustBadge } from "@/src/components/badges";
import { Button } from "@/src/components/ui/Button";

const SEGMENTS = [["", "All drivetrains"], ["engine:BEV", "BEV"], ["engine:PHEV", "PHEV"], ["engine:ICE", "Combustion"]];
const SIZE = 20;

// Beleg-Browser: jede Kundenstimme hinter einem Vorschlag, filterbar. Das macht "grounded in evidence" nachprüfbar.
function Browser() {
  const id = useScenarioParam();
  const [q, setQ] = useState("");
  const [applied, setApplied] = useState("");
  const [segment, setSegment] = useState("");
  const [page, setPage] = useState(1);
  const key = [id, applied, segment, page].join("|");
  const view = useLoad(key, () => getEvidencePage(id, { q: applied, segment, page, size: SIZE }));
  const total = view.data?.total ?? 0;

  return (
    <main className="mx-auto max-w-[1000px] px-6 py-12 lg:px-10">
      <PageHeader eyebrow={`Evidence · ${id}`} title="Evidence browser.">
        Every customer voice, study line and source behind the proposals. Search it, filter it, check it yourself.
      </PageHeader>
      <form
        className="flex flex-wrap gap-3 pb-6"
        onSubmit={(e) => {
          e.preventDefault();
          setPage(1);
          setApplied(q.trim());
        }}
      >
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search text, e.g. charging"
          aria-label="Search evidence"
          className="h-[52px] min-w-64 flex-1 border border-[var(--hairline)] px-4"
        />
        <select
          aria-label="Drivetrain"
          value={segment}
          onChange={(e) => {
            setPage(1);
            setSegment(e.target.value);
          }}
          className="h-[52px] border border-[var(--hairline)] bg-white px-3"
        >
          {SEGMENTS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
        <Button type="submit">Search</Button>
      </form>
      {view.error && <ErrorNote message={view.error} />}
      {view.loading && <Loading what="evidence" />}
      {view.data && (
        <>
          <p className="pb-3 text-sm text-[var(--grey-500)]">{total.toLocaleString("en-US")} results</p>
          <ul className="border-t border-[var(--hairline)]">
            {view.data.items.map((ev) => (
              <li key={ev.id} className="border-b border-[var(--hairline)] py-5">
                <div className="flex flex-wrap items-center gap-3 text-xs text-[var(--grey-500)]">
                  <span className="font-mono">{ev.id}</span>
                  <SourceTrustBadge sourceType={ev.source_type} />
                  <span>{ev.source_name}</span>
                  <span>{ev.polarity < 0 ? "▼ negative" : ev.polarity > 0 ? "▲ positive" : "neutral"}</span>
                </div>
                <p className="mt-2">{ev.text}</p>
                {ev.url && (
                  <a href={ev.url} target="_blank" rel="noopener noreferrer" className="mt-1 inline-block text-sm text-[var(--blue)]">Open source ›</a>
                )}
              </li>
            ))}
          </ul>
          <div className="flex items-center justify-between pt-6">
            <Button variant="outline" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</Button>
            <span className="text-sm text-[var(--grey-500)]">Page {page} of {Math.max(1, Math.ceil(total / SIZE))}</span>
            <Button variant="outline" disabled={page * SIZE >= total} onClick={() => setPage(page + 1)}>Next</Button>
          </div>
        </>
      )}
    </main>
  );
}

export default function EvidencePage() {
  return (
    <Suspense fallback={<main className="px-6 py-12 text-sm text-[var(--grey-500)]">Loading...</main>}>
      <Browser />
    </Suspense>
  );
}
