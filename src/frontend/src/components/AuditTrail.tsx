"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getAudit, getRequirements, type AuditEvent } from "@/src/lib/api";

const LABELS: Record<string, string> = {
  PIPELINE_LOADED: "Data loaded", REQUIREMENT_PROPOSED: "Requirement proposed",
  REQUIREMENT_DISCARDED: "Draft excluded", PM_APPROVE: "Requirement approved",
  PM_REJECT: "Requirement rejected", PM_EDIT: "Requirement edited",
  PM_CHALLENGE: "Evidence challenged", AI_RESPONDED: "AI answered challenge",
  WEIGHTS_CHANGED: "Priorities recalculated", AI_LENS_SUGGESTED: "Priority preview suggested",
};

const WHO: Record<string, string> = { human: "Product manager", ai: "AI", system: "System" };

// One plain sentence per event, so nobody has to decode event types or IDs.
function sentence(e: AuditEvent, title?: string): string {
  const what = LABELS[e.event_type] ?? e.event_type.replaceAll("_", " ").toLowerCase();
  return `${WHO[e.actor.type] ?? e.actor.name}: ${what}${title ? ` - "${title}"` : ""}`;
}

function display(value: unknown): string {
  if (value === null) return "Not recorded";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

type NumberMap = Record<string, number>;
const isNumberMap = (v: unknown): v is NumberMap => !!v && typeof v === "object" && Object.values(v).every(x => typeof x === "number");
const pct = (v?: number) => typeof v === "number" ? `${Math.round(v * 100)}%` : "-";

// Weight changes as "Customer pain 20% -> 25%" instead of raw JSON with float noise.
function NumberChanges({ before, after }: { before: NumberMap; after: NumberMap }) {
  const keys = [...new Set([...Object.keys(before), ...Object.keys(after)])];
  return <ul className="grid gap-1">{keys.map(k => {
    const changed = pct(before[k]) !== pct(after[k]);
    return <li key={k} className={`flex justify-between gap-3 ${changed ? "font-semibold text-[var(--ink)]" : "text-[var(--grey-500)]"}`}>
      <span>{k.replaceAll("_", " ")}</span><span className="tabular-nums">{pct(before[k])} &rarr; {pct(after[k])}</span>
    </li>;
  })}</ul>;
}

function Changes({ payload }: { payload: Record<string, unknown> }) {
  const changes = Object.entries(payload).filter(([, value]) => value && typeof value === "object" && "before" in value && "after" in value);
  return <>
    {changes.length > 0 && <div className="mt-4 overflow-x-auto"><table className="w-full table-fixed text-left text-xs">
      <thead><tr className="border-b border-[var(--hairline)]"><th className="w-1/4 py-2">Changed field</th><th className="px-2 py-2">Before</th><th className="px-2 py-2">After</th></tr></thead>
      <tbody>{changes.map(([field, value]) => { const change = value as { before: unknown; after: unknown }; if (isNumberMap(change.before) && isNumberMap(change.after)) return <tr key={field} className="border-b border-[var(--hairline)] align-top"><th className="break-words py-3 font-medium">{field.replaceAll("_", " ")}</th><td colSpan={2} className="px-2 py-3"><NumberChanges before={change.before} after={change.after} /></td></tr>;
        return <tr key={field} className="border-b border-[var(--hairline)] align-top"><th className="break-words py-3 font-medium">{field.replaceAll("_", " ")}</th><td className="px-2 py-3"><pre>{display(change.before)}</pre></td><td className="px-2 py-3"><pre>{display(change.after)}</pre></td></tr>; })}</tbody>
    </table></div>}
    {Object.keys(payload).length > 0 && <details className="mt-4 border-t border-[var(--hairline)] pt-3"><summary className="text-xs font-semibold">Full event data</summary><pre className="mt-3 max-h-72 overflow-auto text-xs text-[var(--grey-500)]">{JSON.stringify(payload, null, 2)}</pre></details>}
  </>;
}

export function AuditTrail({ scenarioId, requirementId, compact = false }: { scenarioId?: string; requirementId?: string; compact?: boolean }) {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loadedFor, setLoadedFor] = useState("");
  const [query, setQuery] = useState("");
  const [actor, setActor] = useState("");
  const [type, setType] = useState("");
  const [order, setOrder] = useState("newest");
  const [page, setPage] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  // Requirement titles instead of hash IDs like REQ-G60-US-67ffe2: readable without context.
  const [titles, setTitles] = useState<Record<string, string>>({});
  const key = `${scenarioId ?? ""}:${requirementId ?? ""}`;
  useEffect(() => {
    let cancelled = false;
    getAudit({ scenarioId, requirementId }).then(next => {
      if (!cancelled) { setEvents(next); setError(null); setPage(0); setSelected(null); }
      const ids = [...new Set(next.map(e => e.scenario_id).filter(Boolean))];
      Promise.all(ids.map(id => getRequirements(id).catch(() => [])))
        .then(lists => { if (!cancelled) setTitles(Object.fromEntries(lists.flat().map(r => [r.id, r.title]))); });
    }).catch((err: Error) => { if (!cancelled) setError(err.message); })
      .finally(() => { if (!cancelled) setLoadedFor(key); });
    return () => { cancelled = true; };
  }, [scenarioId, requirementId, key]);

  if (loadedFor !== key) return <p role="status" className="py-6 text-sm text-[var(--grey-500)]">Loading decision history...</p>;
  if (error) return <p role="alert" className="border border-rose-300 p-4 text-sm text-rose-800">{error}</p>;
  const filtered = events.filter(e => (!actor || e.actor.type === actor) && (!type || e.event_type === type)
    && `${LABELS[e.event_type] ?? e.event_type} ${e.rationale} ${e.requirement_id ?? ""} ${titles[e.requirement_id ?? ""] ?? ""} ${e.actor.name} ${e.seq} ${JSON.stringify(e.payload)}`.toLowerCase().includes(query.trim().toLowerCase()))
    .sort((a, b) => order === "newest" ? b.seq - a.seq : a.seq - b.seq);
  const size = compact ? 5 : 6;
  const pages = Math.max(1, Math.ceil(filtered.length / size));
  const currentPage = Math.min(page, pages - 1);
  const visible = filtered.slice(currentPage * size, (currentPage + 1) * size);
  const chosen = visible.find(e => e.seq === selected) ?? visible[0];
  const changeFilter = (set: (value: string) => void, value: string) => { set(value); setPage(0); setSelected(null); };
  return <section className="min-w-0">
    {!compact && <>
      <dl className="mb-6 grid grid-cols-3 gap-4 border-y border-[var(--hairline)] py-4">
        {[['human', 'PM actions'], ['ai', 'AI actions'], ['system', 'System actions']].map(([key, label]) => <div key={key}><dt className="text-xs text-[var(--grey-500)]">{label}</dt><dd className="mt-1 text-2xl tabular-nums">{events.filter(e => e.actor.type === key).length}</dd></div>)}
      </dl>
      {!events.some(e => e.actor.type === "human") && <p className="mb-6 border-l-2 border-[var(--blue)] bg-[var(--grey-100)] px-4 py-3 text-sm">No product manager decision yet. Open a requirement in the <Link href={scenarioId ? `/cockpit?scenario=${scenarioId}` : "/cockpit"} className="font-semibold text-[var(--blue)]">cockpit</Link> and approve, reject or challenge it; the decision and its reason appear here.</p>}
      <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <label className="field-label">Search history<input className="field-control" type="search" placeholder="Requirement, person or reason" value={query} onChange={e => changeFilter(setQuery, e.target.value)} /></label>
        <label className="field-label">Who acted<select className="field-control" value={actor} onChange={e => changeFilter(setActor, e.target.value)}><option value="">Everyone</option><option value="human">Product manager</option><option value="ai">AI</option><option value="system">System</option></select></label>
        <label className="field-label">Action<select className="field-control" value={type} onChange={e => changeFilter(setType, e.target.value)}><option value="">All actions</option>{[...new Set(events.map(e => e.event_type))].map(t => <option key={t} value={t}>{LABELS[t] ?? t.replaceAll("_", " ")}</option>)}</select></label>
        <label className="field-label">Order<select className="field-control" value={order} onChange={e => changeFilter(setOrder, e.target.value)}><option value="newest">Latest first</option><option value="oldest">Oldest first</option></select></label>
      </div>
    </>}
    <div className="mb-3 flex flex-wrap items-center justify-between gap-3 text-xs text-[var(--grey-500)]"><p role="status">{filtered.length} events{filtered.length !== events.length ? ` / ${events.length} total` : ""}</p>{(query || actor || type) && <button className="min-h-11 text-[var(--blue)]" onClick={() => { setQuery(""); setActor(""); setType(""); setPage(0); }}>Clear filters</button>}</div>
    {visible.length === 0 ? <p className="border-y border-[var(--hairline)] py-8 text-sm text-[var(--grey-500)]">No events match this selection.</p> : <div className={`grid min-w-0 gap-6 ${compact ? "" : "lg:grid-cols-[1fr_1.2fr]"}`}>
      <ol className="min-w-0 divide-y divide-[var(--hairline)] border-y border-[var(--hairline)]">
        {visible.map(e => <li key={e.seq}>
          <button aria-pressed={chosen?.seq === e.seq} onClick={() => setSelected(e.seq)} className={`w-full border-l-2 px-4 py-3 text-left ${chosen?.seq === e.seq ? "border-[var(--blue)] bg-blue-50" : "border-transparent hover:bg-[var(--grey-100)]"}`}>
            <span className="block text-sm font-semibold">{LABELS[e.event_type] ?? e.event_type.replaceAll("_", " ")}</span>
            {e.requirement_id && <span className="mt-1 line-clamp-2 block text-sm text-[var(--ink)]">{titles[e.requirement_id] ?? e.requirement_id}</span>}
            <span className="mt-1 block text-xs text-[var(--grey-500)]">{WHO[e.actor.type] ?? e.actor.type} / {new Date(e.ts).toLocaleString("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })} / {e.actor.name}</span>
          </button>
        </li>)}
      </ol>
      {chosen && <article className="min-w-0 self-start border-l-2 border-[var(--blue)] px-5 py-3" aria-label="Event details">
        <h3 className="text-lg font-medium">{sentence(chosen, titles[chosen.requirement_id ?? ""])}</h3>
        <p className="mt-2 text-xs text-[var(--grey-500)]">{WHO[chosen.actor.type]}: {chosen.actor.name} / {new Date(chosen.ts).toLocaleString("en")} / entry #{chosen.seq}</p>
        <p className="mt-4 text-xs font-semibold text-[var(--grey-500)]">Reason</p><p className="mt-1 break-words text-sm">{chosen.rationale}</p>
        {chosen.requirement_id && <Link href={`/requirements/${chosen.requirement_id}?scenario=${chosen.scenario_id}`} className="mt-4 inline-block text-sm font-semibold text-[var(--blue)]">Open requirement &rarr;</Link>}
        <Changes payload={chosen.payload} />
      </article>}
    </div>}
    {pages > 1 && <div className="mt-4 flex items-center justify-between gap-4 text-sm"><button className="min-h-11 px-3 disabled:opacity-40" disabled={currentPage === 0} onClick={() => { setPage(currentPage - 1); setSelected(null); }}>Previous</button><span className="tabular-nums">Page {currentPage + 1} of {pages}</span><button className="min-h-11 px-3 disabled:opacity-40" disabled={currentPage === pages - 1} onClick={() => { setPage(currentPage + 1); setSelected(null); }}>Next</button></div>}
  </section>;
}
